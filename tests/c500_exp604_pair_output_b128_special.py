#!/usr/bin/env python3
"""Exp652 case-11 pair-output/B128 correctness gate for a later C500 run.

This is an isolated safety harness for
``cuda_case11_pair_output_b128_tailmask_exp652.cpp`` (source SHA
``f993ccd69f320e5710b282f03e01d713b2cc47b2bd57e672a238970918732a08``)
against control #113889 (source SHA
``a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972``).
It exercises the exact case-11 ABI shape (B=16, KV=4, cap=12251), including
zero length, page/tail boundaries, a mixed batch, legal-but-invalid NaN
padding, raw BF16 output word/lane ordering, output guards, and repeated
workspace use.  Baseline/page-only/full-reuse checks gate both candidate and
control.  Tail-poison checks gate the candidate against a finite reference;
the known control tail behavior is diagnostic only.

No timing is performed and this script does not build, select, archive, or
submit a candidate.  Run it only after the two libraries have been built on a
real MetaX C500 host, for example::

    python3 tests/c500_exp604_pair_output_b128_special.py \
        --candidate build/exp652_normal.so \
        --control build/cuda_113889.so --seed 20260823
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

import numpy as np
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


CASE11 = next(case for case in CASES if case.case_id == 11)
EXACT_LENGTHS = (0, 1, 2, 15, 16, 17, 319, 320, 321, 12250, 12251)
MIXED_LENGTHS = tuple(EXACT_LENGTHS[index % len(EXACT_LENGTHS)] for index in range(16))
# Keep the reuse short phase genuinely short while covering zero, tail, and
# page-boundary forms.  The complete exact-length list is checked separately.
SHORT_LENGTHS = tuple(
    (0, 1, 2, 15, 16, 17, 319, 320, 321)[index % 9] for index in range(16)
)
FULL_LENGTHS = (CASE11.seqlen_k,) * CASE11.batch_size

GUARD_WORDS = 64
GUARD_VALUE = -777.0
# Signed int16 representations of quiet NaN BF16 words.  The poison is
# installed through raw words so it does not depend on a float conversion.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1


def _assert_requested_contract() -> None:
    if (CASE11.case_id, CASE11.batch_size, CASE11.seqlen_k, CASE11.num_heads_k) != (
        11,
        16,
        12251,
        4,
    ):
        raise AssertionError(f"unexpected case11 manifest: {CASE11}")
    if len(EXACT_LENGTHS) != 11 or len(set(EXACT_LENGTHS)) != 11:
        raise AssertionError("exact case11 lengths must contain 11 unique values")
    if set(EXACT_LENGTHS) - {0, 1, 2, 15, 16, 17, 319, 320, 321, 12250, 12251}:
        raise AssertionError("exact case11 length contract changed")
    if any(length < 0 or length > CASE11.seqlen_k for length in EXACT_LENGTHS):
        raise AssertionError("exact case11 length is outside the ABI capacity")
    if len(MIXED_LENGTHS) != CASE11.batch_size or set(EXACT_LENGTHS) - set(MIXED_LENGTHS):
        raise AssertionError("mixed B16 batch does not cover every exact length")
    if len(SHORT_LENGTHS) != CASE11.batch_size or max(SHORT_LENGTHS) >= 12250:
        raise AssertionError("short workspace phase is not short")


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (CASE11.batch_size, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (
        CASE11.batch_size * CASE11.max_pages,
        PAGE_SIZE,
        CASE11.num_heads_k,
        HEAD_DIM,
    )
    if inputs.case != CASE11:
        raise AssertionError(f"unexpected input case: {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case11 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case11 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (CASE11.batch_size,):
        raise AssertionError("case11 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (CASE11.batch_size, CASE11.max_pages):
        raise AssertionError("case11 block_table shape mismatch")
    if inputs.num_blocks != CASE11.batch_size * CASE11.max_pages:
        raise AssertionError("case11 physical page count mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(length) for length in lengths)
    if len(values) == 1:
        values = values * CASE11.batch_size
    if len(values) != CASE11.batch_size:
        raise ValueError(f"expected one or {CASE11.batch_size} lengths, got {values}")
    if any(length < 0 or length > CASE11.seqlen_k for length in values):
        raise ValueError(f"length outside case11 capacity: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    """Give every batch row a private, legal page range for poison checks."""

    table = torch.arange(
        inputs.num_blocks,
        dtype=torch.int32,
        device=inputs.block_table.device,
    ).reshape(CASE11.batch_size, CASE11.max_pages)
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
    if not inputs.output.is_contiguous():
        raise AssertionError("guarded output must be contiguous")
    # The even-lane B128 stores must begin at a 128-bit boundary.  BF16 has
    # two bytes, and the guard count is therefore deliberately a multiple of 8.
    if (inputs.output.data_ptr() % 16) != 0:
        raise AssertionError("guarded output is not B128 aligned")
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
    inputs = make_input(CASE11, seed=seed, length_mode="full")
    _assert_layout(inputs)
    _install_disjoint_page_table(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail


def _padding_page_ids_and_tail_tokens(
    inputs: PagedDecodeInput,
) -> tuple[list[int], list[tuple[int, int]]]:
    """Find logically invalid pages/tokens while keeping every ID legal."""

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
    """Poison selected logical padding pages/tails with BF16 NaNs."""

    page_ids, tail_tokens = _padding_page_ids_and_tail_tokens(inputs)
    device = inputs.k_cache.device
    if poison_pages and page_ids:
        ids = torch.tensor(page_ids, dtype=torch.int64, device=device)
        if bool(((ids < 0) | (ids >= inputs.num_blocks)).any().item()):
            raise AssertionError("NaN page poison selected an illegal page ID")
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    if poison_tails:
        for page, token in tail_tokens:
            inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
            inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    if (poison_pages and page_ids) or (poison_tails and tail_tokens):
        return len(page_ids) if poison_pages else 0, len(tail_tokens) if poison_tails else 0
    if not page_ids and not tail_tokens:
        raise AssertionError("poison case has no logical padding target")
    return 0, 0


def _write_nan_poison(inputs: PagedDecodeInput) -> tuple[int, int]:
    """Poison both logical padding pages and tail tokens."""

    return _write_nan_poison_mode(
        inputs,
        poison_pages=True,
        poison_tails=True,
    )


def _restore_cache(
    inputs: PagedDecodeInput,
    base_k: torch.Tensor,
    base_v: torch.Tensor,
) -> None:
    inputs.k_cache.copy_(base_k)
    inputs.v_cache.copy_(base_v)


def _evaluate(
    label: str,
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> tuple[bool, torch.Tensor, float, float, bool]:
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
    if within:
        max_error = float(difference.max().item())
        max_ratio = float((difference / tolerance).max().item())
    else:
        max_error = float("inf")
        max_ratio = float("inf")
    guards = _guards_ok(storage, before_head, before_tail)
    passed = within and guards
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} finite={finite} reference_finite={reference_finite} "
        f"within_tolerance={within} max_error={max_error:.6e} "
        f"max_tol_ratio={max_ratio:.3f} guards={guards}"
    )
    return passed, actual_bf16, max_error, max_ratio, finite


def _pair_check(
    label: str,
    candidate,
    control,
    inputs: PagedDecodeInput,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
    *,
    require_control: bool = True,
) -> tuple[bool, torch.Tensor | None, torch.Tensor | None, torch.Tensor | None]:
    reference = flash_reference(inputs).detach().clone()
    reference_finite = bool(torch.isfinite(reference.float()).all().item())
    if not reference_finite:
        print(f"[FAIL] {label} reference_finite=False")
        return False, None, None, None

    candidate_result = _evaluate(
        f"{label} candidate",
        candidate,
        inputs,
        reference,
        storage,
        before_head,
        before_tail,
    )
    control_result = _evaluate(
        f"{label} control",
        control,
        inputs,
        reference,
        storage,
        before_head,
        before_tail,
    )
    candidate_ok, candidate_out, candidate_error, candidate_ratio, candidate_finite = (
        candidate_result
    )
    control_ok, control_out, control_error, control_ratio, control_finite = control_result
    pair_diff = (candidate_out.float() - control_out.float()).abs()
    pair_tol = ATOL + RTOL * reference.float().abs()
    pair_match = bool(torch.isfinite(pair_diff).all().item()) and bool(
        (pair_diff <= pair_tol).all().item()
    )
    passed = candidate_ok and candidate_finite
    if require_control:
        passed = passed and control_ok and control_finite and pair_match
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} require_control={require_control} "
        f"candidate_error={candidate_error:.6e} "
        f"candidate_tol_ratio={candidate_ratio:.3f} control_error={control_error:.6e} "
        f"control_tol_ratio={control_ratio:.3f} "
        f"candidate_finite={candidate_finite} control_finite={control_finite} "
        f"candidate_control_within_tolerance={pair_match}"
    )
    if not require_control:
        print(
            f"[INFO] {label} control_diagnostic_tail_nonfinite="
            f"{not control_finite} control_pass={control_ok}"
        )
    return passed, reference, candidate_out, control_out


def _run_exact_lengths(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    try:
        print(
            f"[INFO] case11 exact lengths={','.join(map(str, EXACT_LENGTHS))} "
            f"B={CASE11.batch_size} KV={CASE11.num_heads_k}"
        )
        all_passed = True
        for index, length in enumerate(EXACT_LENGTHS, start=1):
            _set_lengths(inputs, (length,))
            passed, _, _, _ = _pair_check(
                f"case11 exact-{index:02d}/{len(EXACT_LENGTHS)} length={length}",
                candidate,
                control,
                inputs,
                storage,
                before_head,
                before_tail,
            )
            all_passed = all_passed and passed
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case11 exact-length coverage "
            f"checks={len(EXACT_LENGTHS)}"
        )
        return all_passed
    finally:
        del inputs
        torch.cuda.empty_cache()


def _raw_expected_words() -> np.ndarray:
    expected_words = np.empty(
        (CASE11.batch_size, CASE11.num_heads_k, HEAD_DIM), dtype=np.uint16
    )
    for batch in range(CASE11.batch_size):
        for kv_head in range(CASE11.num_heads_k):
            exponent = 124 + ((batch + kv_head) % 3)
            for dim in range(HEAD_DIM):
                # 37 is coprime to 128, so every dimension in one output row
                # has a distinct mantissa and lane swaps are observable.
                mantissa = (37 * dim + 13 * batch + 17 * kv_head) & 0x7F
                expected_words[batch, kv_head, dim] = np.uint16(
                    (exponent << 7) | mantissa
                )
    return expected_words


def _raw_expected_output(expected_words: np.ndarray) -> np.ndarray:
    expected_output = np.empty(
        (CASE11.batch_size, NUM_HEADS, HEAD_DIM), dtype=np.uint16
    )
    for batch in range(CASE11.batch_size):
        for head in range(NUM_HEADS):
            expected_output[batch, head] = expected_words[batch, head // 8]
    return expected_output


def _check_raw_words(
    label: str,
    output: torch.Tensor,
    expected_output: np.ndarray,
) -> bool:
    observed = (
        output.detach()
        .to(device="cpu")
        .view(torch.int16)
        .numpy()
        .view(np.uint16)
        .reshape(CASE11.batch_size, NUM_HEADS, HEAD_DIM)
    )
    full_match = np.array_equal(observed, expected_output)
    pair_match = True
    for lane in range(0, 32, 2):
        start = lane * 4
        stop = (lane + 2) * 4
        pair_match = pair_match and np.array_equal(
            observed[:, :, start:stop], expected_output[:, :, start:stop]
        )
    result = full_match and pair_match
    print(
        f"[{'PASS' if result else 'FAIL'}] case11 raw-BF16 {label} "
        f"word_order={full_match} even_lane_B128_slices={pair_match}"
    )
    return result


def _run_raw_word_order(candidate, control, seed: int) -> bool:
    """Check raw BF16 output under unpoisoned and separated poison modes."""

    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    expected_words = _raw_expected_words()
    expected_output = _raw_expected_output(expected_words)
    try:
        _set_lengths(inputs, (1,))
        baseline_reference = None
        baseline_candidate = None
        all_passed = True
        modes = (
            ("none", False, False, True),
            ("pages-only", True, False, True),
            ("tails-only", False, True, False),
            ("pages+tails", True, True, False),
        )
        for mode, poison_pages, poison_tails, require_control in modes:
            _restore_cache(inputs, base_k, base_v)
            poisoned_pages = poisoned_tails = 0
            if poison_pages or poison_tails:
                poisoned_pages, poisoned_tails = _write_nan_poison_mode(
                    inputs,
                    poison_pages=poison_pages,
                    poison_tails=poison_tails,
                )
            for batch in range(CASE11.batch_size):
                page = int(inputs.block_table[batch, 0].item())
                words = expected_words[batch]
                _copy_raw_bf16(inputs.v_cache[page, 0], words)
                observed = (
                    inputs.v_cache[page, 0]
                    .detach()
                    .to(device="cpu")
                    .view(torch.int16)
                    .numpy()
                    .view(np.uint16)
                )
                if not np.array_equal(observed, words):
                    raise AssertionError("raw BF16 V payload changed during installation")

            passed, reference, candidate_out, control_out = _pair_check(
                f"case11 raw-BF16 mode={mode} pages={poisoned_pages} "
                f"tails={poisoned_tails}",
                candidate,
                control,
                inputs,
                storage,
                before_head,
                before_tail,
                require_control=require_control,
            )
            if reference is None or candidate_out is None or control_out is None:
                all_passed = False
                continue
            candidate_words_ok = _check_raw_words(
                f"candidate mode={mode}", candidate_out, expected_output
            )
            control_words_ok = _check_raw_words(
                f"control mode={mode}", control_out, expected_output
            )
            if baseline_reference is None:
                baseline_reference = reference.detach().clone()
                baseline_candidate = candidate_out.detach().clone()
                reference_unchanged = candidate_unchanged = True
                candidate_reference_bits_equal = torch.equal(reference, candidate_out)
                invariant = candidate_reference_bits_equal
            else:
                reference_unchanged = torch.equal(baseline_reference, reference)
                candidate_unchanged = torch.equal(baseline_candidate, candidate_out)
                candidate_reference_bits_equal = torch.equal(reference, candidate_out)
                invariant = (
                    reference_unchanged
                    and candidate_unchanged
                    and candidate_reference_bits_equal
                )
            print(
                f"[{'PASS' if invariant else 'FAIL'}] case11 raw-BF16 mode={mode} "
                f"reference_unchanged={reference_unchanged} "
                f"candidate_unchanged={candidate_unchanged} "
                f"candidate_reference_bits_equal={candidate_reference_bits_equal} "
                f"control_word_order_diagnostic={control_words_ok}"
            )
            all_passed = all_passed and passed and candidate_words_ok and invariant
        return all_passed
    finally:
        del base_k, base_v, inputs
        torch.cuda.empty_cache()


def _copy_raw_bf16(tensor: torch.Tensor, words: np.ndarray) -> None:
    if words.dtype != np.uint16 or words.size != tensor.numel():
        raise AssertionError("raw BF16 payload shape/type mismatch")
    cpu_words = torch.from_numpy(words.reshape(-1).view(np.int16)).view(torch.bfloat16)
    tensor.copy_(cpu_words.reshape(tensor.shape).to(device=tensor.device))


def _run_mixed_poison(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    try:
        _set_lengths(inputs, MIXED_LENGTHS)
        if set(MIXED_LENGTHS) != set(EXACT_LENGTHS):
            raise AssertionError("mixed batch lost an exact-length value")
        baseline_reference = None
        baseline_candidate = None
        baseline_control = None
        all_passed = True
        modes = (
            ("baseline", False, False, True),
            ("pages-only", True, False, True),
            ("tails-only", False, True, False),
            ("pages+tails", True, True, False),
        )
        for mode, poison_pages, poison_tails, require_control in modes:
            _restore_cache(inputs, base_k, base_v)
            poisoned_pages = poisoned_tails = 0
            if poison_pages or poison_tails:
                poisoned_pages, poisoned_tails = _write_nan_poison_mode(
                    inputs,
                    poison_pages=poison_pages,
                    poison_tails=poison_tails,
                )
            passed, reference, candidate_out, control_out = _pair_check(
                f"case11 mixed-B16 mode={mode} pages={poisoned_pages} "
                f"tails={poisoned_tails}",
                candidate,
                control,
                inputs,
                storage,
                before_head,
                before_tail,
                require_control=require_control,
            )
            if reference is None or candidate_out is None or control_out is None:
                all_passed = False
                continue
            if baseline_reference is None:
                baseline_reference = reference.detach().clone()
                baseline_candidate = candidate_out.detach().clone()
                baseline_control = control_out.detach().clone()
                reference_unchanged = candidate_unchanged = True
                invariant = True
            else:
                reference_unchanged = torch.equal(baseline_reference, reference)
                candidate_unchanged = torch.equal(baseline_candidate, candidate_out)
                invariant = reference_unchanged and candidate_unchanged
            control_unchanged = torch.equal(baseline_control, control_out)
            print(
                f"[{'PASS' if invariant else 'FAIL'}] case11 mixed-B16 mode={mode} "
                f"reference_unchanged={reference_unchanged} "
                f"candidate_unchanged={candidate_unchanged} "
                f"control_unchanged_diagnostic={control_unchanged}"
            )
            all_passed = all_passed and passed and invariant
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case11 mixed-B16 "
            "baseline/pages-only/tails-only/pages+tails candidate gate"
        )
        return all_passed
    finally:
        del base_k, base_v, inputs
        torch.cuda.empty_cache()


def _run_reuse(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    full_snapshot: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
    try:
        sequences: tuple[tuple[str, tuple[tuple[int, ...], ...]], ...] = (
            (
                "full->short->full",
                (FULL_LENGTHS, SHORT_LENGTHS, FULL_LENGTHS),
            ),
            ("short->full", (SHORT_LENGTHS, FULL_LENGTHS)),
        )
        all_passed = True
        for sequence_label, sequence in sequences:
            sequence_passed = True
            for step, lengths in enumerate(sequence, start=1):
                _restore_cache(inputs, base_k, base_v)
                _set_lengths(inputs, lengths)
                poisoned_pages = poisoned_tails = 0
                if any(length < CASE11.seqlen_k for length in lengths):
                    poisoned_pages, poisoned_tails = _write_nan_poison_mode(
                        inputs,
                        poison_pages=True,
                        poison_tails=True,
                    )
                require_control = poisoned_tails == 0
                passed, reference, candidate_out, control_out = _pair_check(
                    f"case11 workspace {sequence_label} step={step}/{len(sequence)} "
                    f"poison_pages={poisoned_pages} poison_tails={poisoned_tails}",
                    candidate,
                    control,
                    inputs,
                    storage,
                    before_head,
                    before_tail,
                    require_control=require_control,
                )
                if reference is None or candidate_out is None or control_out is None:
                    sequence_passed = False
                    continue
                if lengths == FULL_LENGTHS:
                    if full_snapshot is None:
                        full_snapshot = (
                            reference.detach().clone(),
                            candidate_out.detach().clone(),
                            control_out.detach().clone(),
                        )
                    else:
                        same_full = all(
                            torch.equal(previous, current)
                            for previous, current in zip(
                                full_snapshot, (reference, candidate_out, control_out)
                            )
                        )
                        print(
                            f"[{'PASS' if same_full else 'FAIL'}] case11 workspace "
                            f"{sequence_label} full-state invariant={same_full}"
                        )
                        sequence_passed = sequence_passed and same_full
                sequence_passed = sequence_passed and passed
            print(
                f"[{'PASS' if sequence_passed else 'FAIL'}] case11 workspace sequence "
                f"{sequence_label}"
            )
            all_passed = all_passed and sequence_passed
        print(
            f"[{'PASS' if all_passed else 'FAIL'}] case11 workspace reuse "
            "full->short->full and short->full"
        )
        return all_passed
    finally:
        del base_k, base_v, inputs
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260823)
    args = parser.parse_args(argv)

    _assert_requested_contract()
    require_maca_gpu()
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    if not _run_exact_lengths(candidate, control, args.seed + 6040):
        return 1
    if not _run_raw_word_order(candidate, control, args.seed + 6041):
        return 1
    if not _run_mixed_poison(candidate, control, args.seed + 6042):
        return 1
    if not _run_reuse(candidate, control, args.seed + 6043):
        return 1
    print(
        "case11 exp652 special correctness: PASS finite=True no_nan=True "
        "no_inf=True tolerance=True raw_word_lane_order=True guards=True "
        "lengths=0,1,2,15,16,17,319,320,321,12250,12251 "
        "reuse=full->short->full,short->full"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
