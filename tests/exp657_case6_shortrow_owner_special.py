#!/usr/bin/env python3
"""Exp657 case-6 mixed short-row ownership correctness gate for a C500.

Case 6 is the ``B=16, QH=32, KVH=8, headdim=128, seqlen_k_cap=362``
dispatch.  This runner focuses on the short-row/long-row ownership boundary:
every requested length is run with all sixteen rows set to that length, and
one mixed call contains zero-length rows, short rows, and long rows together.
It also poisons only legal physical pages and invalid tail rows, checks output
guards and byte-for-byte input immutability, and reuses one allocation through
full and mixed-short calls.

The control is run beside every candidate invocation.  Under tail poison the
control result is diagnostic because an older control may read an invalid tail
row; the candidate must remain finite, reference-correct, and invariant to
all logical-padding poison modes.

No build, timing, archive, selection, or submission is performed here.  Run
this after building both shared libraries on a real MetaX C500, for example::

    python3 tests/exp657_case6_shortrow_owner_special.py \
        --candidate-library build/exp657_normal.so \
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


CASE6 = next(case for case in CASES if case.case_id == 6)
EXACT_LENGTHS = (
    0,
    1,
    2,
    15,
    16,
    17,
    31,
    32,
    33,
    47,
    48,
    49,
    95,
    96,
    97,
    361,
    362,
)

# This deliberately contains all three ownership classes in one B16 launch:
# zero/short rows (0..48) and long rows (>48).  The exact suite covers 361
# separately; full-length reuse covers 362.
MIXED_LENGTHS = (
    0,
    1,
    2,
    15,
    16,
    17,
    31,
    32,
    33,
    47,
    48,
    49,
    95,
    96,
    97,
    362,
)

# Reuse uses only short rows so that a full -> short -> full transition tests
# both ownership selection and stale workspace state without changing the
# allocation or page table.
MIXED_SHORT_LENGTHS = (
    0,
    1,
    2,
    15,
    16,
    17,
    31,
    32,
    33,
    47,
    48,
    1,
    2,
    17,
    33,
    48,
)
FULL_LENGTHS = (CASE6.seqlen_k,) * CASE6.batch_size

GUARD_WORDS = 64
GUARD_VALUE = -777.0
# Signed int16 representations of quiet NaN BF16 words.  Installing raw
# words makes poison checks independent of float conversion and NaN canonical-
# ization.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1


def _assert_requested_contract() -> None:
    if (CASE6.case_id, CASE6.batch_size, CASE6.seqlen_k, CASE6.num_heads_k) != (
        6,
        16,
        362,
        8,
    ):
        raise AssertionError(f"unexpected case6 manifest: {CASE6}")
    if len(EXACT_LENGTHS) != 17 or len(set(EXACT_LENGTHS)) != 17:
        raise AssertionError("case6 exact lengths must contain 17 unique values")
    if set(EXACT_LENGTHS) != {
        0,
        1,
        2,
        15,
        16,
        17,
        31,
        32,
        33,
        47,
        48,
        49,
        95,
        96,
        97,
        361,
        362,
    }:
        raise AssertionError("case6 exact-length contract changed")
    if any(length < 0 or length > CASE6.seqlen_k for length in EXACT_LENGTHS):
        raise AssertionError("case6 exact length is outside the ABI capacity")
    if len(MIXED_LENGTHS) != CASE6.batch_size:
        raise AssertionError("case6 mixed batch must contain exactly B16 rows")
    if 0 not in MIXED_LENGTHS or not any(1 <= length <= 48 for length in MIXED_LENGTHS):
        raise AssertionError("case6 mixed batch lost zero/short ownership rows")
    if not any(length > 48 for length in MIXED_LENGTHS):
        raise AssertionError("case6 mixed batch lost long control rows")
    if len(MIXED_SHORT_LENGTHS) != CASE6.batch_size or any(
        length > 48 for length in MIXED_SHORT_LENGTHS
    ):
        raise AssertionError("case6 mixed-short reuse contract changed")


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (CASE6.batch_size, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (
        CASE6.batch_size * CASE6.max_pages,
        PAGE_SIZE,
        CASE6.num_heads_k,
        HEAD_DIM,
    )
    if inputs.case != CASE6:
        raise AssertionError(f"unexpected input case: {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case6 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case6 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (CASE6.batch_size,):
        raise AssertionError("case6 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (CASE6.batch_size, CASE6.max_pages):
        raise AssertionError("case6 block_table shape mismatch")
    if inputs.num_blocks != CASE6.batch_size * CASE6.max_pages:
        raise AssertionError("case6 physical page count mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> torch.Tensor:
    values = tuple(int(length) for length in lengths)
    if len(values) == 1:
        values = values * CASE6.batch_size
    if len(values) != CASE6.batch_size:
        raise ValueError(f"expected one or {CASE6.batch_size} lengths, got {values}")
    if any(length < 0 or length > CASE6.seqlen_k for length in values):
        raise ValueError(f"length outside case6 capacity: {values}")
    values_tensor = torch.tensor(
        values, dtype=torch.int32, device=inputs.cache_seqlens.device
    )
    inputs.cache_seqlens.copy_(values_tensor)
    return values_tensor.detach().clone()


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    """Give every row private, legal pages so poison ownership is unambiguous."""

    table = torch.arange(
        inputs.num_blocks,
        dtype=torch.int32,
        device=inputs.block_table.device,
    ).reshape(CASE6.batch_size, CASE6.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed block_table contains an invalid page ID")
    rows = table.detach().to(device="cpu").tolist()
    flat = [int(page) for row in rows for page in row]
    if len(set(flat)) != inputs.num_blocks:
        raise AssertionError("case6 poison table is not physically disjoint")


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
    if not inputs.output.is_contiguous():
        raise AssertionError("guarded output must be contiguous")
    if inputs.output.data_ptr() % 16 != 0:
        raise AssertionError("guarded output is not 128-bit aligned")
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
    """Compare input buffers exactly, including NaN BF16 bit patterns."""

    if actual.dtype != expected.dtype or actual.shape != expected.shape:
        return False
    if actual.dtype.is_floating_point:
        return torch.equal(
            actual.detach().contiguous().view(torch.uint8),
            expected.detach().contiguous().view(torch.uint8),
        )
    return torch.equal(actual, expected)


def _new_inputs(seed: int):
    inputs = make_input(CASE6, seed=seed, length_mode="full")
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
        raise AssertionError("case6 reference output is nonfinite")
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
    reference_finite = bool(torch.isfinite(expected).all().item())
    finite = bool(torch.isfinite(actual).all().item())
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    within = reference_finite and finite and bool(
        torch.isfinite(difference).all().item()
    ) and bool((difference <= tolerance).all().item())
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


def _padding_page_ids_and_tail_tokens(
    inputs: PagedDecodeInput,
) -> tuple[list[int], list[tuple[int, int]]]:
    """Return only logically invalid pages/tokens; every page ID is legal."""

    lengths = [int(value) for value in inputs.cache_seqlens.detach().cpu().tolist()]
    table = inputs.block_table.detach().cpu()
    page_ids: list[int] = []
    tail_tokens: list[tuple[int, int]] = []
    for batch, length in enumerate(lengths):
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        row = [int(page) for page in table[batch].tolist()]
        if any(page < 0 or page >= inputs.num_blocks for page in row):
            raise AssertionError("padding scan found an illegal physical page ID")
        page_ids.extend(row[valid_pages:])
        remainder = length & (PAGE_SIZE - 1)
        if remainder:
            valid_page = row[valid_pages - 1]
            tail_tokens.extend(
                (valid_page, token) for token in range(remainder, PAGE_SIZE)
            )
    return page_ids, tail_tokens


def _write_nan_poison_mode(
    inputs: PagedDecodeInput,
    *,
    poison_pages: bool,
    poison_tails: bool,
) -> tuple[int, int]:
    page_ids, tail_tokens = _padding_page_ids_and_tail_tokens(inputs)
    device = inputs.k_cache.device
    if poison_pages and page_ids:
        ids = torch.tensor(page_ids, dtype=torch.int64, device=device)
        if bool(((ids < 0) | (ids >= inputs.num_blocks)).any().item()):
            raise AssertionError("NaN page poison selected an illegal physical page")
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if poison_tails:
        for page, token in tail_tokens:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    if (poison_pages and not page_ids) or (poison_tails and not tail_tokens):
        raise AssertionError(
            f"poison mode has no target: pages={len(page_ids)} tails={len(tail_tokens)}"
        )
    return len(page_ids) if poison_pages else 0, len(tail_tokens) if poison_tails else 0


def _run_exact_lengths(candidate, control, seed: int) -> bool:
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
        print(
            f"[INFO] case6 exact all-row lengths ({len(EXACT_LENGTHS)}): "
            f"{','.join(map(str, EXACT_LENGTHS))}"
        )
        for index, length in enumerate(EXACT_LENGTHS, start=1):
            lengths = _set_lengths(inputs, (length,))
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            reference = _reference(inputs)
            passed, _, _, _ = _pair_check(
                f"case6 exact-{index:02d}/{len(EXACT_LENGTHS)} length={length}",
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
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case6 exact all-row coverage "
            f"checks={len(EXACT_LENGTHS)}"
        )
        return all_passed
    finally:
        del inputs, q_base, k_base, v_base, table_base
        torch.cuda.empty_cache()


def _run_mixed_poison(candidate, control, seed: int) -> bool:
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
        lengths = _set_lengths(inputs, MIXED_LENGTHS)
        if 0 not in lengths or not any(1 <= length <= 48 for length in lengths):
            raise AssertionError("mixed case6 input lacks zero/short rows")
        if not any(length > 48 for length in lengths):
            raise AssertionError("mixed case6 input lacks long rows")
        _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
        print(
            f"[INFO] case6 mixed-B16 rows={len(lengths)} "
            f"short_owner={sum(0 <= length <= 48 for length in lengths)} "
            f"long_control={sum(length > 48 for length in lengths)} "
            f"lengths={','.join(map(str, lengths.tolist()))}"
        )
        baseline_reference = _reference(inputs)
        baseline_ok, baseline_candidate, baseline_control, _ = _pair_check(
            "case6 mixed-B16 baseline",
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
        all_passed = all_passed and baseline_ok

        modes = (
            ("pages-only", True, False, True),
            ("tails-only", False, True, False),
            ("pages+tails", True, True, False),
        )
        for mode, poison_pages, poison_tails, require_control in modes:
            _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
            poisoned_pages, poisoned_tails = _write_nan_poison_mode(
                inputs,
                poison_pages=poison_pages,
                poison_tails=poison_tails,
            )
            poisoned_k = inputs.k_cache.detach().clone()
            poisoned_v = inputs.v_cache.detach().clone()
            poisoned_reference = _reference(inputs)
            passed, poisoned_candidate, poisoned_control, control_passed = _pair_check(
                f"case6 mixed-B16 NaN {mode} pages={poisoned_pages} "
                f"tails={poisoned_tails}",
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
            reference_unchanged = _tensor_bytes_equal(
                baseline_reference, poisoned_reference
            )
            candidate_unchanged = _tensor_bytes_equal(
                baseline_candidate, poisoned_candidate
            )
            control_unchanged = _tensor_bytes_equal(
                baseline_control, poisoned_control
            )
            invariant = reference_unchanged and candidate_unchanged
            if require_control:
                invariant = invariant and control_unchanged
            print(
                f"[{'PASS' if invariant else 'FAIL'}] case6 mixed-B16 NaN {mode} "
                f"reference_unchanged={reference_unchanged} "
                f"candidate_unchanged={candidate_unchanged} "
                f"control_unchanged={control_unchanged} "
                f"control_required={require_control} control_pass={control_passed}"
            )
            all_passed = all_passed and passed and invariant
            del poisoned_k, poisoned_v

        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case6 mixed-B16 "
            "reference/candidate padding-page, tail-row, and combined NaN invariance"
        )
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
    sequences: tuple[tuple[str, tuple[tuple[int, ...], ...]], ...] = (
        (
            "362->mixed-short->362",
            (FULL_LENGTHS, MIXED_SHORT_LENGTHS, FULL_LENGTHS),
        ),
        ("mixed-short->362", (MIXED_SHORT_LENGTHS, FULL_LENGTHS)),
    )
    try:
        for sequence_label, sequence in sequences:
            sequence_passed = True
            for step, lengths_values in enumerate(sequence, start=1):
                lengths = _set_lengths(inputs, lengths_values)
                _restore_inputs(inputs, q_base, k_base, v_base, lengths, table_base)
                reference = _reference(inputs)
                passed, candidate_out, control_out, _ = _pair_check(
                    f"case6 workspace {sequence_label} step={step}/{len(sequence)}",
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
                snapshot = (reference.detach().clone(), candidate_out.detach().clone(), control_out.detach().clone())
                deterministic = True
                if lengths_values == FULL_LENGTHS:
                    if full_snapshot is None:
                        full_snapshot = snapshot
                    else:
                        deterministic = all(
                            _tensor_bytes_equal(previous, current)
                            for previous, current in zip(full_snapshot, snapshot)
                        )
                elif lengths_values == MIXED_SHORT_LENGTHS:
                    if short_snapshot is None:
                        short_snapshot = snapshot
                    else:
                        deterministic = all(
                            _tensor_bytes_equal(previous, current)
                            for previous, current in zip(short_snapshot, snapshot)
                        )
                print(
                    f"[{'PASS' if deterministic else 'FAIL'}] case6 workspace "
                    f"{sequence_label} step={step} deterministic={deterministic}"
                )
                sequence_passed = sequence_passed and passed and deterministic
                all_passed = all_passed and sequence_passed
            print(
                f"[{'PASS' if sequence_passed else 'FAIL'}] case6 workspace sequence "
                f"{sequence_label}"
            )
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case6 workspace reuse "
            "362->mixed-short->362 and mixed-short->362"
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

    _assert_requested_contract()
    require_maca_gpu()
    candidate = load_kernel(args.candidate_library)
    control = load_kernel(args.control_library)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate_library} | control={args.control_library} | "
        f"seed={args.seed}"
    )
    if not _run_exact_lengths(candidate, control, args.seed + 6570):
        return 1
    if not _run_mixed_poison(candidate, control, args.seed + 6571):
        return 1
    if not _run_reuse(candidate, control, args.seed + 6572):
        return 1
    print(
        "case6 exp657 special correctness: PASS finite=True no_nan=True "
        "no_inf=True guards=True input_immutability=True "
        "lengths=0,1,2,15,16,17,31,32,33,47,48,49,95,96,97,361,362 "
        "reuse=362->mixed-short->362,mixed-short->362"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
