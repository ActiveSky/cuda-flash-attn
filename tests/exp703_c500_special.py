#!/usr/bin/env python3
"""Exp703 case-12 C500 semantic safety gate.

This driver is deliberately correctness-only.  It checks the candidate and
the #124611 control against the installed FlashAttention reference while
keeping legal page-table padding and incomplete tail rows poisoned with BF16
NaNs.  It also checks output guards, input immutability, finite results, and
same-process workspace reuse.  No timing or OJ operation is performed.
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


CASE12 = next(case for case in CASES if case.case_id == 12)
MIXED_LENGTHS = (1, 16, 8191, 8192, 16385, 24576, 32767, 32768)
FULL_LENGTHS = (CASE12.seqlen_k,) * CASE12.batch_size
SHORT_LENGTHS = (1,) * CASE12.batch_size
GUARD_WORDS = 64
GUARD_VALUE = -777.0
# Raw signed int16 spellings of quiet BF16 NaNs.  Poison is installed through
# raw words so it cannot be changed by float conversion or dtype rounding.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1


def _assert_contract() -> None:
    expected = (12, 8, 32768, 8)
    actual = (CASE12.case_id, CASE12.batch_size, CASE12.seqlen_k, CASE12.num_heads_k)
    if actual != expected:
        raise AssertionError(f"unexpected case12 manifest: {actual}")
    if len(MIXED_LENGTHS) != CASE12.batch_size:
        raise AssertionError("mixed case12 batch length count changed")
    if any(length < 1 or length > CASE12.seqlen_k for length in MIXED_LENGTHS):
        raise AssertionError("mixed case12 length is outside the ABI capacity")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(length) for length in lengths)
    if len(values) == 1:
        values = values * CASE12.batch_size
    if len(values) != CASE12.batch_size:
        raise ValueError(f"expected one or {CASE12.batch_size} lengths, got {values}")
    if any(length < 1 or length > CASE12.seqlen_k for length in values):
        raise ValueError(f"length outside case12 capacity: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    table = torch.arange(
        inputs.num_blocks,
        dtype=torch.int32,
        device=inputs.block_table.device,
    ).reshape(CASE12.batch_size, CASE12.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed block table contains an invalid page ID")


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
    if not inputs.output.is_contiguous() or inputs.output.data_ptr() % 16:
        raise AssertionError("guarded output is not contiguous/B128 aligned")
    return storage, before_head, before_tail


def _guards_ok(
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _new_inputs(seed: int):
    inputs = make_input(CASE12, seed=seed, length_mode="full")
    _install_disjoint_page_table(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail


def _padding_pages_and_tail_tokens(
    inputs: PagedDecodeInput,
) -> tuple[list[int], list[tuple[int, int]]]:
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


def _write_poison(
    inputs: PagedDecodeInput,
    *,
    poison_pages: bool,
    poison_tails: bool,
) -> tuple[int, int]:
    page_ids, tail_tokens = _padding_pages_and_tail_tokens(inputs)
    if poison_pages and page_ids:
        ids = torch.tensor(page_ids, dtype=torch.int64, device=inputs.k_cache.device)
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if poison_tails:
        for page, token in tail_tokens:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    return (len(page_ids) if poison_pages else 0, len(tail_tokens) if poison_tails else 0)


def _snapshot_inputs(inputs: PagedDecodeInput):
    return (
        inputs.q.detach().clone(),
        inputs.k_cache.detach().clone(),
        inputs.v_cache.detach().clone(),
        inputs.cache_seqlens.detach().clone(),
        inputs.block_table.detach().clone(),
    )


def _inputs_ok(inputs: PagedDecodeInput, snapshot) -> bool:
    current_values = (
        inputs.q,
        inputs.k_cache,
        inputs.v_cache,
        inputs.cache_seqlens,
        inputs.block_table,
    )
    for current, expected in zip(current_values, snapshot):
        # NaN poison is intentional.  Compare BF16 payloads as raw int16 so
        # identical NaN words are treated as unchanged rather than unequal by
        # floating-point equality.
        if current.dtype == torch.bfloat16:
            if not torch.equal(current.view(torch.int16), expected.view(torch.int16)):
                return False
        elif not torch.equal(current, expected):
            return False
    return True


def _restore_base(inputs: PagedDecodeInput, base) -> None:
    inputs.q.copy_(base[0])
    inputs.k_cache.copy_(base[1])
    inputs.v_cache.copy_(base[2])
    inputs.cache_seqlens.copy_(base[3])
    inputs.block_table.copy_(base[4])


def _evaluate(
    label: str,
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    expected_inputs,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
):
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
    within = reference_finite and finite and bool(torch.isfinite(difference).all().item()) and bool(
        (difference <= tolerance).all().item()
    )
    max_error = float(difference.max().item()) if torch.isfinite(difference).any() else float("inf")
    max_ratio = float((difference / tolerance).max().item()) if torch.isfinite(difference).any() else float("inf")
    guards = _guards_ok(storage, before_head, before_tail)
    inputs_untouched = _inputs_ok(inputs, expected_inputs)
    passed = reference_finite and finite and within and guards and inputs_untouched
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} finite={finite} "
        f"reference_finite={reference_finite} within_tolerance={within} "
        f"max_error={max_error:.6e} max_tol_ratio={max_ratio:.3f} "
        f"guards={guards} inputs_untouched={inputs_untouched}"
    )
    return passed, actual_bf16, reference_finite, finite


def _prepare_mode(inputs: PagedDecodeInput, base, lengths, poison_pages, poison_tails):
    _restore_base(inputs, base)
    values = _set_lengths(inputs, lengths)
    poisoned_pages, poisoned_tails = _write_poison(
        inputs, poison_pages=poison_pages, poison_tails=poison_tails
    )
    expected_inputs = _snapshot_inputs(inputs)
    reference = flash_reference(inputs).detach().clone()
    torch.cuda.synchronize()
    return values, poisoned_pages, poisoned_tails, expected_inputs, reference


def _run_mode(
    label,
    candidate,
    control,
    inputs,
    base,
    storage,
    before_head,
    before_tail,
    lengths,
    poison_pages,
    poison_tails,
):
    values, pages, tails, expected, reference = _prepare_mode(
        inputs, base, lengths, poison_pages, poison_tails
    )
    candidate_ok, candidate_out, ref_finite, candidate_finite = _evaluate(
        f"{label} candidate lengths={values} pages={pages} tails={tails}",
        candidate,
        inputs,
        reference,
        expected,
        storage,
        before_head,
        before_tail,
    )

    # Recreate exactly the same poisoned state before running the control, so
    # an input mutation by the candidate cannot influence the diagnostic pair.
    _, _, _, control_expected, control_reference = _prepare_mode(
        inputs, base, lengths, poison_pages, poison_tails
    )
    control_ok, control_out, control_ref_finite, control_finite = _evaluate(
        f"{label} control lengths={values} pages={pages} tails={tails}",
        control,
        inputs,
        control_reference,
        control_expected,
        storage,
        before_head,
        before_tail,
    )
    pair_match = True
    if candidate_out is not None and control_out is not None and control_finite:
        pair_difference = (candidate_out.float() - control_out.float()).abs()
        pair_tolerance = ATOL + RTOL * control_reference.float().abs()
        pair_match = bool(torch.isfinite(pair_difference).all().item()) and bool(
            (pair_difference <= pair_tolerance).all().item()
        )
    print(
        f"[{'PASS' if pair_match else 'INFO'}] {label} candidate_control_within_tolerance={pair_match} "
        f"control_gate={'pass' if control_ok else 'diagnostic'}"
    )
    return candidate_ok, candidate_out, reference, control_ok, control_out


def _run_mixed_poison(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base = _snapshot_inputs(inputs)
    try:
        modes = (
            ("case12 mixed baseline", False, False),
            ("case12 mixed padding-page poison", True, False),
            ("case12 mixed tail poison", False, True),
            ("case12 mixed padding-page+tail poison", True, True),
        )
        baseline_candidate = None
        baseline_reference = None
        all_passed = True
        for label, poison_pages, poison_tails in modes:
            passed, candidate_out, reference, _, _ = _run_mode(
                label,
                candidate,
                control,
                inputs,
                base,
                storage,
                before_head,
                before_tail,
                MIXED_LENGTHS,
                poison_pages,
                poison_tails,
            )
            if candidate_out is None:
                all_passed = False
                continue
            if baseline_candidate is None:
                baseline_candidate = candidate_out.detach().clone()
                baseline_reference = reference.detach().clone()
                invariant = True
            else:
                candidate_invariant = torch.equal(baseline_candidate, candidate_out)
                reference_invariant = torch.equal(baseline_reference, reference)
                invariant = candidate_invariant and reference_invariant
                print(
                    f"[{'PASS' if invariant else 'FAIL'}] {label} poison invariance "
                    f"candidate_unchanged={candidate_invariant} reference_unchanged={reference_invariant}"
                )
            all_passed = all_passed and passed and invariant
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case12 mixed padding/tail poison gate "
            f"lengths={MIXED_LENGTHS}"
        )
        return all_passed
    finally:
        del base, inputs
        torch.cuda.empty_cache()


def _run_reuse(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base = _snapshot_inputs(inputs)
    full_outputs = []
    all_passed = True
    try:
        sequences = (
            ("32768->1->32768", (FULL_LENGTHS, SHORT_LENGTHS, FULL_LENGTHS)),
            ("1->32768", (SHORT_LENGTHS, FULL_LENGTHS)),
        )
        for sequence_label, sequence in sequences:
            sequence_passed = True
            for step, lengths in enumerate(sequence, start=1):
                poisoned = lengths != FULL_LENGTHS
                passed, candidate_out, reference, _, _ = _run_mode(
                    f"case12 workspace {sequence_label} step={step}/{len(sequence)}",
                    candidate,
                    control,
                    inputs,
                    base,
                    storage,
                    before_head,
                    before_tail,
                    lengths,
                    poisoned,
                    poisoned,
                )
                if candidate_out is None:
                    sequence_passed = False
                    continue
                if lengths == FULL_LENGTHS:
                    full_outputs.append((reference.detach().clone(), candidate_out.detach().clone()))
                    if len(full_outputs) > 1:
                        same_full = all(
                            torch.equal(previous, current)
                            for previous, current in zip(full_outputs[0], full_outputs[-1])
                        )
                        print(
                            f"[{'PASS' if same_full else 'FAIL'}] case12 workspace "
                            f"{sequence_label} full-state invariant={same_full}"
                        )
                        sequence_passed = sequence_passed and same_full
                sequence_passed = sequence_passed and passed
            print(f"[{'PASS' if sequence_passed else 'FAIL'}] case12 workspace sequence {sequence_label}")
            all_passed = all_passed and sequence_passed
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case12 workspace reuse "
            "32768->1->32768 and 1->32768"
        )
        return all_passed
    finally:
        del base, inputs
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260824)
    args = parser.parse_args(argv)

    _assert_contract()
    require_maca_gpu()
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    mixed_ok = _run_mixed_poison(candidate, control, args.seed + 7030)
    reuse_ok = _run_reuse(candidate, control, args.seed + 7031)
    print(f"SPECIAL_RESULT={'PASS' if mixed_ok and reuse_ok else 'FAIL'}")
    return 0 if mixed_ok and reuse_ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
