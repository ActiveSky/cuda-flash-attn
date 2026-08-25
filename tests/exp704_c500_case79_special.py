#!/usr/bin/env python3
"""Correctness-only C500 safety gate for exp704 cases 7 and 9.

The regular harness covers full, boundary, and random batches.  This companion
adds legal page-table padding and incomplete-tail BF16-NaN poison, output
guards, byte/raw-word input immutability, candidate/control comparison, and
same-allocation full/short/full reuse.  It performs no timing or OJ action.
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


TARGETS = {case.case_id: case for case in CASES if case.case_id in (7, 9)}
GUARD_WORDS = 64
GUARD_VALUE = -777.0
# Signed int16 spellings of quiet BF16 NaNs.  Input comparisons below use raw
# int16 words so an intentional poison NaN is not reported as a mutation.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1

MIXED_LENGTHS = {
    7: (1, 15, 16, 17, 687, 688, 689, 703, 704, 705, 1375, 1376, 1377, 2047, 2048),
    9: (1, 15, 16, 17, 687, 688, 689, 703, 704, 705, 1375, 1376, 1377,
        2047, 2048, 2049, 2751, 2752, 2753, 3440, 4095, 4096),
}
RANDOM_LENGTHS = {
    7: (37, 271, 701, 1025, 1537, 1999),
    9: (37, 271, 701, 1025, 1537, 2049, 3073, 3999),
}


def _same(a: torch.Tensor, b: torch.Tensor) -> bool:
    """Compare tensors exactly, preserving BF16 NaN payload equality."""

    if a.dtype != b.dtype or a.shape != b.shape:
        return False
    if a.dtype == torch.bfloat16:
        return torch.equal(a.detach().contiguous().view(torch.int16),
                           b.detach().contiguous().view(torch.int16))
    return torch.equal(a, b)


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in lengths)
    if len(values) == 1:
        values = values * inputs.case.batch_size
    if len(values) != inputs.case.batch_size:
        raise ValueError(
            f"case {inputs.case.case_id} needs {inputs.case.batch_size} lengths, got {len(values)}"
        )
    if any(value < 1 or value > inputs.case.seqlen_k for value in values):
        raise ValueError(f"length outside case {inputs.case.case_id}: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_disjoint_table(inputs: PagedDecodeInput) -> None:
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(inputs.case.batch_size, inputs.case.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed page table contains an invalid ID")


def _guard_output(inputs: PagedDecodeInput):
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


def _guards_ok(storage, before_head, before_tail) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _snapshot(inputs: PagedDecodeInput):
    return tuple(
        tensor.detach().clone()
        for tensor in (
            inputs.q,
            inputs.k_cache,
            inputs.v_cache,
            inputs.cache_seqlens,
            inputs.block_table,
        )
    )


def _restore(inputs: PagedDecodeInput, state) -> None:
    for current, expected in zip(
        (inputs.q, inputs.k_cache, inputs.v_cache, inputs.cache_seqlens, inputs.block_table),
        state,
    ):
        current.copy_(expected)


def _poison_targets(inputs: PagedDecodeInput):
    page_ids: list[int] = []
    tails: list[tuple[int, int]] = []
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    table = inputs.block_table.detach().to(device="cpu")
    for batch, length_value in enumerate(lengths):
        length = int(length_value)
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        row = [int(page) for page in table[batch].tolist()]
        page_ids.extend(row[valid_pages:])
        remainder = length & (PAGE_SIZE - 1)
        if remainder:
            tails.extend((row[valid_pages - 1], token)
                         for token in range(remainder, PAGE_SIZE))
    if any(page < 0 or page >= inputs.num_blocks for page in page_ids):
        raise AssertionError("poison selected an invalid physical page")
    return page_ids, tails


def _write_poison(inputs: PagedDecodeInput, *, pages: bool, tails: bool) -> tuple[int, int]:
    page_ids, tail_tokens = _poison_targets(inputs)
    if pages:
        ids = torch.tensor(page_ids, dtype=torch.int64, device=inputs.k_cache.device)
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if tails:
        for page, token in tail_tokens:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    return (len(page_ids) if pages else 0, len(tail_tokens) if tails else 0)


def _invoke(label, kernel, inputs, reference, expected, storage, before_head, before_tail):
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    actual_bf16 = inputs.output.detach().clone()
    actual = actual_bf16.float()
    wanted = reference.float()
    difference = (actual - wanted).abs()
    tolerance = ATOL + RTOL * wanted.abs()
    finite = bool(torch.isfinite(actual).all().item())
    reference_finite = bool(torch.isfinite(wanted).all().item())
    within = reference_finite and finite and bool(
        torch.isfinite(difference).all().item()
    ) and bool((difference <= tolerance).all().item())
    untouched = all(
        _same(current, before)
        for current, before in zip(
            (inputs.q, inputs.k_cache, inputs.v_cache,
             inputs.cache_seqlens, inputs.block_table),
            expected,
        )
    )
    guards = _guards_ok(storage, before_head, before_tail)
    max_error = float(difference.max().item()) if torch.isfinite(difference).any() else float("inf")
    max_ratio = float((difference / tolerance).max().item()) if torch.isfinite(difference).any() else float("inf")
    passed = finite and reference_finite and within and untouched and guards
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} finite={finite} "
        f"within_tolerance={within} max_error={max_error:.6e} "
        f"max_tol_ratio={max_ratio:.3f} guards={guards} inputs_untouched={untouched}"
    )
    return passed, actual_bf16


def _pair(label, candidate, control, inputs, expected, storage, before_head, before_tail):
    reference = flash_reference(inputs).detach().clone()
    candidate_ok, candidate_out = _invoke(
        f"{label} candidate", candidate, inputs, reference, expected,
        storage, before_head, before_tail
    )
    _restore(inputs, expected)
    control_ok, control_out = _invoke(
        f"{label} control", control, inputs, reference, expected,
        storage, before_head, before_tail
    )
    _restore(inputs, expected)
    difference = (candidate_out.float() - control_out.float()).abs()
    tolerance = ATOL + RTOL * reference.float().abs()
    pair_match = bool(torch.isfinite(difference).all().item()) and bool(
        (difference <= tolerance).all().item()
    )
    passed = candidate_ok and control_ok and pair_match
    print(
        f"[{'PASS' if passed else 'FAIL'}] {label} "
        f"candidate_control_within_tolerance={pair_match}"
    )
    return passed, candidate_out, reference


def _prepare(inputs, base, lengths, poison_pages, poison_tails):
    _restore(inputs, base)
    values = _set_lengths(inputs, lengths)
    page_count, tail_count = _write_poison(
        inputs, pages=poison_pages, tails=poison_tails
    )
    expected = _snapshot(inputs)
    return values, page_count, tail_count, expected


def _run_case(case_id: int, candidate, control, seed: int) -> bool:
    case = TARGETS[case_id]
    inputs = make_input(case, seed=seed, length_mode="full")
    _install_disjoint_table(inputs)
    storage, before_head, before_tail = _guard_output(inputs)
    base = _snapshot(inputs)
    all_passed = True
    try:
        mixed = tuple(MIXED_LENGTHS[case_id][i % len(MIXED_LENGTHS[case_id])]
                      for i in range(case.batch_size))
        print(f"[INFO] case{case_id} mixed lengths={mixed}")
        for label, poison_pages, poison_tails in (
            ("mixed baseline", False, False),
            ("mixed padding-page NaN", True, False),
            ("mixed tail NaN", False, True),
            ("mixed padding-page+tail NaN", True, True),
        ):
            values, pages, tails, expected = _prepare(
                inputs, base, mixed, poison_pages, poison_tails
            )
            passed, _, reference = _pair(
                f"case{case_id} {label} lengths={values} pages={pages} tails={tails}",
                candidate, control, inputs, expected, storage, before_head, before_tail
            )
            all_passed = passed and all_passed
            if label == "mixed baseline":
                baseline_reference = reference
                baseline_candidate = _snapshot(inputs)  # state only; output captured below
            if not passed:
                return False

        # A deterministic mixed/random-equivalent batch is run against the
        # same reference contract after the poison checks.  This complements
        # the regular harness's random mode while retaining guards and state
        # immutability in this pairwise process.
        random_lengths = tuple(RANDOM_LENGTHS[case_id][i % len(RANDOM_LENGTHS[case_id])]
                               for i in range(case.batch_size))
        values, pages, tails, expected = _prepare(
            inputs, base, random_lengths, False, False
        )
        passed, _, _ = _pair(
            f"case{case_id} random-equivalent lengths={values}",
            candidate, control, inputs, expected, storage, before_head, before_tail
        )
        all_passed = passed and all_passed
        if not passed:
            return False

        full = (case.seqlen_k,) * case.batch_size
        short = (1,) * case.batch_size
        full_outputs: list[torch.Tensor] = []
        for sequence_label, sequence in (
            ("workspace full->short->full", (full, short, full)),
            ("workspace short->full", (short, full)),
        ):
            sequence_passed = True
            for step, lengths in enumerate(sequence, start=1):
                values, pages, tails, expected = _prepare(
                    inputs, base, lengths, lengths == short, lengths == short
                )
                passed, candidate_out, _ = _pair(
                    f"case{case_id} {sequence_label} step={step}/{len(sequence)} "
                    f"lengths={values} pages={pages} tails={tails}",
                    candidate, control, inputs, expected,
                    storage, before_head, before_tail
                )
                sequence_passed = passed and sequence_passed
                if lengths == full:
                    full_outputs.append(candidate_out.detach().clone())
                    if len(full_outputs) > 1:
                        deterministic = torch.equal(full_outputs[0], full_outputs[-1])
                        print(
                            f"[{'PASS' if deterministic else 'FAIL'}] case{case_id} "
                            f"{sequence_label} full-output-invariant={deterministic}"
                        )
                        sequence_passed = deterministic and sequence_passed
            print(f"[{'PASS' if sequence_passed else 'FAIL'}] case{case_id} {sequence_label}")
            all_passed = sequence_passed and all_passed
            if not sequence_passed:
                return False
        print(f"[{'PASS' if all_passed else 'FAIL'}] case{case_id} special safety gate")
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
    if set(TARGETS) != {7, 9}:
        raise AssertionError(f"unexpected target manifest: {TARGETS}")
    require_maca_gpu()
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    result7 = _run_case(7, candidate, control, args.seed + 7047)
    result9 = _run_case(9, candidate, control, args.seed + 7049)
    passed = result7 and result9
    print(f"SPECIAL_RESULT={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
