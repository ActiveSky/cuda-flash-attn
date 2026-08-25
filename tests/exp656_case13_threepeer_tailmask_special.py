#!/usr/bin/env python3
"""Exp656 case-13 correctness gate for a real MetaX C500.

This runner is deliberately limited to the case-13 ABI shape (B=1, 32 query
heads, 8 KV heads, head dimension 128, and a 58966-token capacity).  It checks
the short/page/split boundaries used by the candidate, legal-but-invalid page
and tail poison, output guards, input/metadata immutability, and reuse of one
workspace across full and short requests.  The control is required to pass
unpoisoned and page-only checks.  A control failure under tail poison is
reported diagnostically because the known control may read an invalid tail
row; the candidate is always required to remain finite and reference-correct.

The script does not build, benchmark, archive, select, or submit anything.
Run it only after the candidate and control shared libraries have been built
on a real C500, for example::

    python3 tests/exp656_case13_threepeer_tailmask_special.py \
        --candidate-library build/exp656_normal.so \
        --control-library build/cuda_113889.so --seed 20260823
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable, Sequence

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


CASE13 = next(case for case in CASES if case.case_id == 13)
EXACT_LENGTHS = (
    1,
    2,
    15,
    16,
    17,
    911,
    912,
    913,
    1823,
    1824,
    1825,
    3647,
    3648,
    3649,
    58351,
    58352,
    58367,
    58368,
    58369,
    58383,
    58384,
    58385,
    58965,
    58966,
)

GUARD_WORDS = 64
GUARD_VALUE = -777.0
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1, a negative quiet NaN BF16 word.


def _assert_contract() -> None:
    if (CASE13.batch_size, CASE13.seqlen_k, CASE13.num_heads_k) != (1, 58966, 8):
        raise AssertionError(f"unexpected case13 manifest: {CASE13}")
    if len(EXACT_LENGTHS) != 24 or len(set(EXACT_LENGTHS)) != 24:
        raise AssertionError("case13 exact-length contract must contain 24 unique values")
    if any(length < 1 or length > CASE13.seqlen_k for length in EXACT_LENGTHS):
        raise AssertionError("case13 exact length is outside the ABI capacity")


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (1, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (CASE13.max_pages, PAGE_SIZE, 8, HEAD_DIM)
    if inputs.case != CASE13:
        raise AssertionError(f"unexpected input case: {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case13 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case13 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (1,):
        raise AssertionError("case13 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (1, CASE13.max_pages):
        raise AssertionError("case13 block_table shape mismatch")
    if inputs.num_blocks != CASE13.max_pages:
        raise AssertionError("case13 physical page count mismatch")


def _set_length(inputs: PagedDecodeInput, length: int) -> torch.Tensor:
    if length < 1 or length > CASE13.seqlen_k:
        raise ValueError(f"length outside case13 capacity: {length}")
    values = torch.tensor((int(length),), dtype=torch.int32, device=inputs.cache_seqlens.device)
    inputs.cache_seqlens.copy_(values)
    return values.detach().clone()


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).view(1, CASE13.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed block table contains an illegal page ID")


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
    """Compare input buffers exactly, including NaN poison bit patterns."""
    if actual.dtype != expected.dtype or actual.shape != expected.shape:
        return False
    if actual.dtype.is_floating_point:
        # torch.equal treats NaN != NaN, although the poison snapshot is
        # intentionally expected to contain the same NaN words.
        return torch.equal(
            actual.detach().contiguous().view(torch.uint8),
            expected.detach().contiguous().view(torch.uint8),
        )
    return torch.equal(actual, expected)


def _new_inputs(seed: int) -> tuple[
    PagedDecodeInput,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
]:
    inputs = make_input(CASE13, seed=seed, length_mode="full")
    _assert_layout(inputs)
    _install_disjoint_page_table(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    # These immutable snapshots are also used as the expected input state for
    # every candidate/control invocation.  Keeping them outside _invoke avoids
    # cloning the 120 MB cache pair for every one of the 24 exact lengths.
    q_base = inputs.q.detach().clone()
    k_base = inputs.k_cache.detach().clone()
    v_base = inputs.v_cache.detach().clone()
    table_base = inputs.block_table.detach().clone()
    return (
        inputs,
        storage,
        before_head,
        before_tail,
        q_base,
        k_base,
        v_base,
        table_base,
    )


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
    # Always restore the exact mode before the control invocation, including
    # after a failed candidate immutability check.  This keeps the comparison
    # meaningful and makes a corrupt candidate an explicit failure.
    _restore_inputs(inputs, q_expected, k_expected, v_expected, lengths_expected, table_expected)
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
    _restore_inputs(inputs, q_expected, k_expected, v_expected, lengths_expected, table_expected)
    pair_diff = (candidate_out.float() - control_out.float()).abs()
    pair_tol = ATOL + RTOL * reference.float().abs()
    pair_match = bool(torch.isfinite(pair_diff).all().item()) and bool(
        (pair_diff <= pair_tol).all().item()
    )
    passed = candidate_ok and candidate_finite and (
        control_ok and control_finite and pair_match if require_control else True
    )
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} require_control={require_control} "
        f"candidate_finite={candidate_finite} control_finite={control_finite} "
        f"candidate_control_within_tolerance={pair_match}"
    )
    return passed, candidate_out, control_out, control_ok and control_finite


def _padding_targets(
    inputs: PagedDecodeInput,
    length: int,
) -> tuple[list[int], list[tuple[int, int]]]:
    table = inputs.block_table[0].detach().to(device="cpu").tolist()
    valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
    if valid_pages < 1 or valid_pages > len(table):
        raise AssertionError(f"invalid valid-page count for length={length}: {valid_pages}")
    page_ids = [int(page) for page in table[valid_pages:]]
    if any(page < 0 or page >= inputs.num_blocks for page in page_ids):
        raise AssertionError("padding poison selected an illegal page ID")
    remainder = length & (PAGE_SIZE - 1)
    tail_tokens = []
    if remainder:
        valid_page = int(table[valid_pages - 1])
        tail_tokens = [(valid_page, token) for token in range(remainder, PAGE_SIZE)]
    return page_ids, tail_tokens


def _write_nan_poison(
    inputs: PagedDecodeInput,
    length: int,
    *,
    poison_pages: bool,
    poison_tails: bool,
) -> tuple[int, int]:
    pages, tails = _padding_targets(inputs, length)
    if poison_pages and pages:
        ids = torch.tensor(pages, dtype=torch.int64, device=inputs.k_cache.device)
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if poison_tails:
        for page, token in tails:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    if (poison_pages and not pages) or (poison_tails and not tails):
        raise AssertionError(
            f"poison mode has no target: pages={len(pages)} tails={len(tails)} "
            f"select_pages={poison_pages} select_tails={poison_tails} length={length}"
        )
    return len(pages) if poison_pages else 0, len(tails) if poison_tails else 0


def _reference(inputs: PagedDecodeInput) -> torch.Tensor:
    result = flash_reference(inputs).detach().clone()
    if not bool(torch.isfinite(result.float()).all().item()):
        raise AssertionError("reference output is nonfinite")
    return result


def _run_exact(candidate, control, seed: int) -> bool:
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
    all_passed = True
    try:
        print(f"[INFO] case13 exact lengths ({len(EXACT_LENGTHS)}): {','.join(map(str, EXACT_LENGTHS))}")
        for index, length in enumerate(EXACT_LENGTHS, start=1):
            lengths = _set_length(inputs, length)
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            reference = _reference(inputs)
            passed, _, _, _ = _pair_check(
                f"case13 exact-{index:02d}/{len(EXACT_LENGTHS)} length={length}",
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
            if not passed:
                return False
        print(f"[{'PASS' if all_passed else 'FAIL'}] case13 exact-length coverage checks={len(EXACT_LENGTHS)}")
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
    all_passed = True
    try:
        # Length 17 has both many legal padding pages and a nonempty invalid
        # tail.  The exact suite already exercises the same mask at every
        # requested late split boundary, keeping this poison phase bounded.
        length = 17
        lengths = _set_length(inputs, length)
        _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
        base_reference = _reference(inputs)
        baseline_ok, baseline_candidate, baseline_control, _ = _pair_check(
            "case13 poison baseline length=17",
            candidate,
            control,
            inputs,
            base_reference,
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
        all_passed = all_passed and baseline_ok
        if not baseline_ok:
            return False

        modes = (
            ("pages-only", True, False, True),
            ("tails-only", False, True, False),
            ("pages+tails", True, True, False),
        )
        for mode, poison_pages, poison_tails, require_control in modes:
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            poisoned_pages, poisoned_tails = _write_nan_poison(
                inputs,
                length,
                poison_pages=poison_pages,
                poison_tails=poison_tails,
            )
            mode_k = inputs.k_cache.detach().clone()
            mode_v = inputs.v_cache.detach().clone()
            poisoned_reference = _reference(inputs)
            passed, poisoned_candidate, poisoned_control, control_passed = _pair_check(
                f"case13 NaN {mode} pages={poisoned_pages} tails={poisoned_tails}",
                candidate,
                control,
                inputs,
                poisoned_reference,
                storage,
                before_head,
                before_tail,
                q_base,
                mode_k,
                mode_v,
                lengths,
                table_base,
                require_control=require_control,
            )
            reference_unchanged = torch.equal(base_reference, poisoned_reference)
            candidate_unchanged = torch.equal(baseline_candidate, poisoned_candidate)
            control_unchanged = torch.equal(baseline_control, poisoned_control)
            invariant = reference_unchanged and candidate_unchanged
            if require_control:
                invariant = invariant and control_unchanged
            print(
                f"[{'PASS' if invariant else 'FAIL'}] case13 NaN {mode} "
                f"reference_unchanged={reference_unchanged} "
                f"candidate_unchanged={candidate_unchanged} "
                f"control_unchanged={control_unchanged} "
                f"control_required={require_control} control_pass={control_passed}"
            )
            all_passed = all_passed and passed and invariant
            del mode_k, mode_v
            if not all_passed:
                return False
        print(f"[{'PASS' if all_passed else 'FAIL'}] case13 page/tail poison checks")
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
    all_passed = True
    full_snapshot: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
    try:
        sequences: tuple[tuple[str, tuple[int, ...]], ...] = (
            ("58966->1->58966", (58966, 1, 58966)),
            ("1->58966", (1, 58966)),
        )
        for sequence_label, sequence in sequences:
            sequence_ok = True
            for step, length in enumerate(sequence, start=1):
                lengths = _set_length(inputs, length)
                _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
                reference = _reference(inputs)
                passed, candidate_out, control_out, _ = _pair_check(
                    f"case13 workspace {sequence_label} step={step}/{len(sequence)} length={length}",
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
                deterministic = True
                if length == CASE13.seqlen_k:
                    if full_snapshot is None:
                        full_snapshot = (
                            reference.detach().clone(),
                            candidate_out.detach().clone(),
                            control_out.detach().clone(),
                        )
                    else:
                        deterministic = all(
                            torch.equal(previous, current)
                            for previous, current in zip(
                                full_snapshot, (reference, candidate_out, control_out)
                            )
                        )
                print(
                    f"[{'PASS' if deterministic else 'FAIL'}] case13 workspace "
                    f"{sequence_label} step={step} full_deterministic={deterministic}"
                )
                sequence_ok = sequence_ok and passed and deterministic
                all_passed = all_passed and sequence_ok
                if not sequence_ok:
                    return False
            print(f"[{'PASS' if sequence_ok else 'FAIL'}] case13 workspace sequence {sequence_label}")
        print(f"[{'PASS' if all_passed else 'FAIL'}] case13 workspace reuse 58966->1->58966 and 1->58966")
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
        f"candidate={args.candidate_library} | control={args.control_library} | seed={args.seed}"
    )
    if not _run_exact(candidate, control, args.seed):
        return 1
    if not _run_poison(candidate, control, args.seed + 1):
        return 1
    if not _run_reuse(candidate, control, args.seed + 2):
        return 1
    print("case13 exp656 special correctness: PASS finite=True no_nan=True no_inf=True guards=True")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
