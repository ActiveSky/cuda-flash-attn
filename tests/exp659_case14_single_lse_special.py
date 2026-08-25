#!/usr/bin/env python3
"""Exp659 case-14 single-LSE reducer correctness gate for a real C500.

The candidate changes only the case-14 reducer: normalized BF16 partials carry
one FP32 LSE value instead of separate ``m`` and ``l`` metadata.  This runner
keeps the producer and the accepted control beside every check, while
requiring the candidate to remain finite and reference-correct under all
logical-padding poison modes.

The suite intentionally exercises the case-14 257-split/15-pages-per-split
contract, including live-split counts 0, 1, 2+, and the final reducer source
slot 256.  It checks exact page boundaries, random/boundary lengths, legal
physical page IDs with poisoned logical padding, output guards, byte-exact
input immutability, and reuse of one allocation across full and short calls.

No build, timing, archive, selection, or submission is performed here.  Run
it only after both shared libraries have been built on a real MetaX C500, for
example::

    python3 tests/exp659_case14_single_lse_special.py \
        --candidate-library build/exp659_candidate_normal.so \
        --control-library build/cuda_113889.so --seed 20260823
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

import torch

from c500_case_manifest import CASES, HEAD_DIM, NUM_HEADS, PAGE_SIZE
from c500_paged_decode_harness import (
    ATOL,
    RTOL,
    PagedDecodeInput,
    flash_reference,
    load_kernel,
    make_input,
    require_maca_gpu,
    run_kernel,
)


CASE14 = next(case for case in CASES if case.case_id == 14)

# The first group includes all requested zero/one/page/split boundaries.  The
# late group brackets the transition to live split 256 and then source slot
# 256 (257 live splits) at the end of the full-capacity request.
EXACT_LENGTHS = (
    0,
    1,
    15,
    16,
    17,
    239,
    240,
    241,
    254,
    255,
    256,
    479,
    480,
    481,
    719,
    720,
    721,
    959,
    960,
    961,
    3839,
    3840,
    3841,
    61423,
    61424,
    61425,
    61439,
    61440,
    61441,
    61455,
    61456,
    61457,
    61503,
    61504,
    61505,
    61518,
    61519,
)

# Separate deterministic sets make the log show that the page-boundary
# checks above are not the only non-full workloads examined.
BOUNDARY_LENGTHS = (
    2,
    14,
    18,
    255,
    257,
    511,
    512,
    513,
    1023,
    1024,
    1025,
    8191,
    8192,
    8193,
    12287,
    12288,
    12289,
    24575,
    24576,
    24577,
    49151,
    49152,
    49153,
)
RANDOM_LENGTHS = (73, 317, 1021, 7777, 16383, 32769, 50000)

GUARD_WORDS = 64
GUARD_VALUE = -777.0
# Signed int16 representations of quiet NaN BF16 words.  Raw words keep the
# poison check independent of float conversion or NaN canonicalization.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xffc1


def _live_splits(length: int) -> int:
    """Mirror the single-LSE reducer's fused-tail live-split contract."""

    full_pages = length // PAGE_SIZE
    if full_pages > 0:
        return min(
            257,
            (full_pages + 15 - 1) // 15,
        )
    return int((length & (PAGE_SIZE - 1)) != 0)


def _assert_contract() -> None:
    if (CASE14.case_id, CASE14.batch_size, CASE14.seqlen_k, CASE14.num_heads_k) != (
        14,
        1,
        61519,
        4,
    ):
        raise AssertionError(f"unexpected case14 manifest: {CASE14}")
    if len(EXACT_LENGTHS) != len(set(EXACT_LENGTHS)):
        raise AssertionError("case14 exact lengths must be unique")
    if any(length < 0 or length > CASE14.seqlen_k for length in EXACT_LENGTHS):
        raise AssertionError("case14 exact length is outside the ABI capacity")
    required = {0, 1, 15, 16, 17, 239, 240, 241, 61456, 61519}
    if not required.issubset(EXACT_LENGTHS):
        raise AssertionError("case14 exact suite lost a required boundary")
    live = {_live_splits(length) for length in EXACT_LENGTHS}
    if not {0, 1}.issubset(live) or not any(value > 1 for value in live):
        raise AssertionError(f"exact suite does not cover live_splits 0/1/>1: {live}")
    if _live_splits(61456) != 257 or 256 >= _live_splits(61456):
        raise AssertionError("exact suite does not reach reducer source slot 256")
    if len(BOUNDARY_LENGTHS) != len(set(BOUNDARY_LENGTHS)):
        raise AssertionError("case14 boundary lengths must be unique")
    if len(RANDOM_LENGTHS) != len(set(RANDOM_LENGTHS)):
        raise AssertionError("case14 random lengths must be unique")
    for length in BOUNDARY_LENGTHS + RANDOM_LENGTHS:
        if length < 1 or length > CASE14.seqlen_k:
            raise AssertionError(f"out-of-range auxiliary length: {length}")


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (1, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (CASE14.max_pages, PAGE_SIZE, 4, HEAD_DIM)
    if inputs.case != CASE14:
        raise AssertionError(f"unexpected input case: {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case14 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case14 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (1,):
        raise AssertionError("case14 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (1, CASE14.max_pages):
        raise AssertionError("case14 block_table shape mismatch")
    if inputs.num_blocks != CASE14.max_pages:
        raise AssertionError("case14 physical page count mismatch")


def _set_length(inputs: PagedDecodeInput, length: int) -> torch.Tensor:
    if length < 0 or length > CASE14.seqlen_k:
        raise ValueError(f"length outside case14 capacity: {length}")
    values = torch.tensor((int(length),), dtype=torch.int32, device=inputs.cache_seqlens.device)
    inputs.cache_seqlens.copy_(values)
    return values.detach().clone()


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    table = torch.arange(
        inputs.num_blocks,
        dtype=torch.int32,
        device=inputs.block_table.device,
    ).view(1, CASE14.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed block table contains an illegal page ID")
    if len(set(int(page) for page in table.detach().cpu().view(-1).tolist())) != inputs.num_blocks:
        raise AssertionError("case14 poison table is not physically disjoint")


def _install_output_guard(
    inputs: PagedDecodeInput,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    storage = torch.full(
        (inputs.output.numel() + 2 * GUARD_WORDS,),
        GUARD_VALUE,
        dtype=inputs.output.dtype,
        device=inputs.output.device,
    )
    before_head = storage[:GUARD_WORDS].clone()
    before_tail = storage[-GUARD_WORDS:].clone()
    inputs.output = storage[GUARD_WORDS:-GUARD_WORDS].view_as(inputs.q)
    if not inputs.output.is_contiguous() or inputs.output.data_ptr() % 16 != 0:
        raise AssertionError("guarded output is not contiguous and B128-aligned")
    return storage, before_head, before_tail


def _guards_ok(
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _tensor_bytes_equal(actual: torch.Tensor, expected: torch.Tensor) -> bool:
    """Compare input/output buffers exactly, including NaN BF16 bit patterns."""

    if actual.dtype != expected.dtype or actual.shape != expected.shape:
        return False
    if actual.dtype.is_floating_point:
        return torch.equal(
            actual.detach().contiguous().view(torch.uint8),
            expected.detach().contiguous().view(torch.uint8),
        )
    return torch.equal(actual, expected)


def _new_inputs(seed: int):
    inputs = make_input(CASE14, seed=seed, length_mode="full")
    _assert_layout(inputs)
    _install_disjoint_page_table(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    q_base = inputs.q.detach().clone()
    k_base = inputs.k_cache.detach().clone()
    v_base = inputs.v_cache.detach().clone()
    table_base = inputs.block_table.detach().clone()
    return inputs, storage, before_head, before_tail, q_base, k_base, v_base, table_base


def _restore_inputs(
    inputs: PagedDecodeInput,
    q_expected: torch.Tensor,
    k_expected: torch.Tensor,
    v_expected: torch.Tensor,
    lengths_expected: torch.Tensor,
    table_expected: torch.Tensor,
) -> None:
    inputs.q.copy_(q_expected)
    inputs.k_cache.copy_(k_expected)
    inputs.v_cache.copy_(v_expected)
    inputs.cache_seqlens.copy_(lengths_expected)
    inputs.block_table.copy_(table_expected)


def _reference(inputs: PagedDecodeInput) -> torch.Tensor:
    reference = flash_reference(inputs).detach().clone()
    if not bool(torch.isfinite(reference.float()).all().item()):
        raise AssertionError("case14 reference output is nonfinite")
    return reference


def _invoke(
    label: str,
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
    q_expected: torch.Tensor,
    k_expected: torch.Tensor,
    v_expected: torch.Tensor,
    lengths_expected: torch.Tensor,
    table_expected: torch.Tensor,
) -> tuple[bool, torch.Tensor, bool, bool, float, float]:
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()

    actual_bf16 = inputs.output.detach().clone()
    actual = actual_bf16.float()
    expected = reference.float()
    finite = bool(torch.isfinite(actual).all().item())
    reference_finite = bool(torch.isfinite(expected).all().item())
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    within = reference_finite and finite and bool(torch.isfinite(difference).all().item()) and bool(
        (difference <= tolerance).all().item()
    )
    if finite and bool(torch.isfinite(difference).all().item()):
        max_error = float(difference.max().item())
        max_ratio = float((difference / tolerance).max().item())
    else:
        max_error = float("inf")
        max_ratio = float("inf")
    untouched = (
        _tensor_bytes_equal(inputs.q, q_expected)
        and _tensor_bytes_equal(inputs.k_cache, k_expected)
        and _tensor_bytes_equal(inputs.v_cache, v_expected)
        and _tensor_bytes_equal(inputs.cache_seqlens, lengths_expected)
        and _tensor_bytes_equal(inputs.block_table, table_expected)
    )
    guards = _guards_ok(storage, before_head, before_tail)
    passed = within and untouched and guards
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} finite={finite} "
        f"reference_finite={reference_finite} within_tolerance={within} "
        f"max_error={max_error:.6e} max_tol_ratio={max_ratio:.3f} "
        f"inputs_untouched={untouched} guards={guards}"
    )
    return passed, actual_bf16, finite, untouched, max_error, max_ratio


def _pair_check(
    label: str,
    candidate,
    control,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
    q_expected: torch.Tensor,
    k_expected: torch.Tensor,
    v_expected: torch.Tensor,
    lengths_expected: torch.Tensor,
    table_expected: torch.Tensor,
    *,
    require_control: bool,
) -> tuple[bool, torch.Tensor, torch.Tensor, bool]:
    candidate_ok, candidate_out, candidate_finite, _, _, _ = _invoke(
        f"{label} candidate",
        candidate,
        inputs,
        reference,
        storage,
        before_head,
        before_tail,
        q_expected,
        k_expected,
        v_expected,
        lengths_expected,
        table_expected,
    )
    _restore_inputs(
        inputs,
        q_expected,
        k_expected,
        v_expected,
        lengths_expected,
        table_expected,
    )
    control_ok, control_out, control_finite, _, _, _ = _invoke(
        f"{label} control",
        control,
        inputs,
        reference,
        storage,
        before_head,
        before_tail,
        q_expected,
        k_expected,
        v_expected,
        lengths_expected,
        table_expected,
    )
    _restore_inputs(
        inputs,
        q_expected,
        k_expected,
        v_expected,
        lengths_expected,
        table_expected,
    )
    pair_difference = (candidate_out.float() - control_out.float()).abs()
    pair_tolerance = ATOL + RTOL * reference.float().abs()
    pair_match = bool(torch.isfinite(pair_difference).all().item()) and bool(
        (pair_difference <= pair_tolerance).all().item()
    )
    passed = candidate_ok and candidate_finite
    if require_control:
        passed = passed and control_ok and control_finite and pair_match
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} require_control={require_control} "
        f"candidate_finite={candidate_finite} control_finite={control_finite} "
        f"candidate_control_within_tolerance={pair_match}"
    )
    if not require_control:
        print(
            f"[INFO] {label} control_diagnostic_tail_nonfinite="
            f"{not control_finite} control_pass={control_ok}"
        )
    return passed, candidate_out, control_out, control_ok and control_finite


def _padding_targets(
    inputs: PagedDecodeInput,
    length: int,
) -> tuple[list[int], list[tuple[int, int]]]:
    table = inputs.block_table[0].detach().cpu().tolist()
    valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
    if valid_pages < 0 or valid_pages > len(table):
        raise AssertionError(f"invalid valid-page count for length={length}: {valid_pages}")
    page_ids = [int(page) for page in table[valid_pages:]]
    if any(page < 0 or page >= inputs.num_blocks for page in page_ids):
        raise AssertionError("padding poison selected an illegal physical page")
    tail_tokens: list[tuple[int, int]] = []
    remainder = length & (PAGE_SIZE - 1)
    if remainder:
        valid_page = int(table[valid_pages - 1])
        tail_tokens = [(valid_page, token) for token in range(remainder, PAGE_SIZE)]
    return page_ids, tail_tokens


def _write_nan_poison_mode(
    inputs: PagedDecodeInput,
    length: int,
    *,
    poison_pages: bool,
    poison_tails: bool,
) -> tuple[int, int]:
    pages, tails = _padding_targets(inputs, length)
    if poison_pages and pages:
        ids = torch.tensor(pages, dtype=torch.int64, device=inputs.k_cache.device)
        if bool(((ids < 0) | (ids >= inputs.num_blocks)).any().item()):
            raise AssertionError("NaN page poison selected an illegal page ID")
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if poison_tails:
        for page, token in tails:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    if poison_pages and not pages:
        raise AssertionError(f"pages-only poison has no target at length={length}")
    if poison_tails and not tails:
        raise AssertionError(f"tails-only poison has no target at length={length}")
    return len(pages) if poison_pages else 0, len(tails) if poison_tails else 0


def _run_lengths(
    label: str,
    lengths_to_run: Iterable[int],
    candidate,
    control,
    seed: int,
) -> bool:
    (
        inputs,
        storage,
        before_head,
        before_tail,
        q_base,
        k_base,
        v_base,
        table_base,
    ) = _new_inputs(seed)
    lengths_to_run = tuple(int(length) for length in lengths_to_run)
    all_passed = True
    try:
        print(
            f"[INFO] case14 {label} lengths ({len(lengths_to_run)}): "
            f"{','.join(map(str, lengths_to_run))}"
        )
        for index, length in enumerate(lengths_to_run, start=1):
            lengths = _set_length(inputs, length)
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            reference = _reference(inputs)
            live = _live_splits(length)
            passed, _, _, _ = _pair_check(
                f"case14 {label}-{index:02d}/{len(lengths_to_run)} "
                f"length={length} live_splits={live}",
                candidate,
                control,
                inputs,
                reference,
                storage,
                before_head,
                before_tail,
                q_base,
                k_base,
                v_base,
                lengths,
                table_base,
                require_control=True,
            )
            all_passed = all_passed and passed
            # A candidate correctness failure is a blocking safety result; do
            # not continue into unrelated long calls after the first failure.
            if not passed:
                return False
        print(f"[{'PASS' if all_passed else 'FAIL'}] case14 {label} checks={len(lengths_to_run)}")
        return all_passed
    finally:
        del inputs, q_base, k_base, v_base, table_base
        torch.cuda.empty_cache()


def _run_poison(candidate, control, seed: int) -> bool:
    (
        inputs,
        storage,
        before_head,
        before_tail,
        q_base,
        k_base,
        v_base,
        table_base,
    ) = _new_inputs(seed)
    length = 17
    all_passed = True
    try:
        lengths = _set_length(inputs, length)
        _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
        baseline_reference = _reference(inputs)
        baseline_ok, baseline_candidate, baseline_control, _ = _pair_check(
            "case14 poison baseline length=17",
            candidate,
            control,
            inputs,
            baseline_reference,
            storage,
            before_head,
            before_tail,
            q_base,
            k_base,
            v_base,
            lengths,
            table_base,
            require_control=True,
        )
        if not baseline_ok:
            return False

        # The control is diagnostic for tail poison because historical control
        # code may read the invalid tail row.  Candidate/reference invariance
        # remains mandatory in all three modes.
        modes = (
            ("pages-only", True, False, True),
            ("tails-only", False, True, False),
            ("pages+tails", True, True, False),
        )
        for mode, poison_pages, poison_tails, require_control in modes:
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            poisoned_pages, poisoned_tails = _write_nan_poison_mode(
                inputs,
                length,
                poison_pages=poison_pages,
                poison_tails=poison_tails,
            )
            poisoned_k = inputs.k_cache.detach().clone()
            poisoned_v = inputs.v_cache.detach().clone()
            poisoned_reference = _reference(inputs)
            passed, poisoned_candidate, poisoned_control, control_passed = _pair_check(
                f"case14 NaN {mode} pages={poisoned_pages} tails={poisoned_tails}",
                candidate,
                control,
                inputs,
                poisoned_reference,
                storage,
                before_head,
                before_tail,
                q_base,
                poisoned_k,
                poisoned_v,
                lengths,
                table_base,
                require_control=require_control,
            )
            reference_unchanged = _tensor_bytes_equal(baseline_reference, poisoned_reference)
            candidate_unchanged = _tensor_bytes_equal(baseline_candidate, poisoned_candidate)
            control_unchanged = _tensor_bytes_equal(baseline_control, poisoned_control)
            invariant = reference_unchanged and candidate_unchanged
            if require_control:
                invariant = invariant and control_unchanged
            print(
                f"[{'PASS' if invariant else 'FAIL'}] case14 NaN {mode} "
                f"reference_unchanged={reference_unchanged} "
                f"candidate_unchanged={candidate_unchanged} "
                f"control_unchanged={control_unchanged} "
                f"control_required={require_control} control_pass={control_passed}"
            )
            all_passed = all_passed and passed and invariant
            del poisoned_k, poisoned_v
            if not all_passed:
                return False
        print(f"[{'PASS' if all_passed else 'FAIL'}] case14 page/tail poison checks")
        return all_passed
    finally:
        del inputs, q_base, k_base, v_base, table_base
        torch.cuda.empty_cache()


def _run_reuse(candidate, control, seed: int) -> bool:
    (
        inputs,
        storage,
        before_head,
        before_tail,
        q_base,
        k_base,
        v_base,
        table_base,
    ) = _new_inputs(seed)
    full_snapshot: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
    short_snapshot: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
    all_passed = True
    sequences = (
        ("61519->17->61519", (61519, 17, 61519)),
        ("17->61519", (17, 61519)),
    )
    try:
        for sequence_label, sequence in sequences:
            sequence_passed = True
            for step, length in enumerate(sequence, start=1):
                lengths = _set_length(inputs, length)
                _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
                reference = _reference(inputs)
                passed, candidate_out, control_out, _ = _pair_check(
                    f"case14 workspace {sequence_label} step={step}/{len(sequence)} "
                    f"length={length} live_splits={_live_splits(length)}",
                    candidate,
                    control,
                    inputs,
                    reference,
                    storage,
                    before_head,
                    before_tail,
                    q_base,
                    k_base,
                    v_base,
                    lengths,
                    table_base,
                    require_control=True,
                )
                snapshot = (
                    reference.detach().clone(),
                    candidate_out.detach().clone(),
                    control_out.detach().clone(),
                )
                deterministic = True
                if length == CASE14.seqlen_k:
                    if full_snapshot is None:
                        full_snapshot = snapshot
                    else:
                        deterministic = all(
                            _tensor_bytes_equal(previous, current)
                            for previous, current in zip(full_snapshot, snapshot)
                        )
                elif length == 17:
                    if short_snapshot is None:
                        short_snapshot = snapshot
                    else:
                        deterministic = all(
                            _tensor_bytes_equal(previous, current)
                            for previous, current in zip(short_snapshot, snapshot)
                        )
                print(
                    f"[{'PASS' if deterministic else 'FAIL'}] case14 workspace "
                    f"{sequence_label} step={step} deterministic={deterministic}"
                )
                sequence_passed = sequence_passed and passed and deterministic
                all_passed = all_passed and sequence_passed
                if not sequence_passed:
                    return False
            print(
                f"[{'PASS' if sequence_passed else 'FAIL'}] "
                f"case14 workspace sequence {sequence_label}"
            )
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case14 workspace reuse "
            "61519->17->61519 and 17->61519"
        )
        return all_passed
    finally:
        del inputs, q_base, k_base, v_base, table_base
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-library", type=Path, required=True)
    parser.add_argument("--control-library", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260823)
    args = parser.parse_args(argv)

    _assert_contract()
    require_maca_gpu()
    candidate = load_kernel(args.candidate_library)
    control = load_kernel(args.control_library)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate_library} | control={args.control_library} | "
        f"seed={args.seed} | case14_capacity={CASE14.seqlen_k} | "
        f"n_split=257 | pages_per_split=15"
    )
    if not _run_lengths("exact", EXACT_LENGTHS, candidate, control, args.seed + 6590):
        return 1
    if not _run_lengths("boundary", BOUNDARY_LENGTHS, candidate, control, args.seed + 6591):
        return 1
    if not _run_lengths("random", RANDOM_LENGTHS, candidate, control, args.seed + 6592):
        return 1
    if not _run_poison(candidate, control, args.seed + 6593):
        return 1
    if not _run_reuse(candidate, control, args.seed + 6594):
        return 1
    print(
        "case14 exp659 special correctness: PASS finite=True no_nan=True "
        "no_inf=True guards=True input_immutability=True "
        "live_splits=0/1/>1 final_source_slot=256 "
        "poison=pages/tails/pages+tails "
        "reuse=61519->17->61519,17->61519"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
