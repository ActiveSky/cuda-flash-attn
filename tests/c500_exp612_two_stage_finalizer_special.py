#!/usr/bin/env python3
"""Exp612 case-7 two-stage-finalizer correctness gate for a later C500 run.

The candidate is deliberately kept outside the normal work file.  This
companion exercises the finalizer's whole per-row contract in one B=64
allocation: live-split counts 0/1/2/3, every requested page/tail boundary,
legal-but-poisoned padding pages and tail tokens, output guards, and workspace
reuse.  The reference output must be finite, and every candidate output value
must be finite and within the existing local tolerance.  A control library is
run on the same tensors as a diagnostic and must also pass the reference gate.

This file does not build, benchmark, select, archive, or submit a candidate.
Run it only after a separate build on a real C500, for example::

    python3 tests/c500_exp612_two_stage_finalizer_special.py \
        --candidate build/exp612_two_stage_finalizer.so \
        --control build/cuda_113889.so --seed 20260823
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


CASE7 = next(case for case in CASES if case.case_id == 7)
EXACT_LENGTHS = (
    0,
    1,
    2,
    15,
    16,
    17,
    687,
    688,
    689,
    703,
    704,
    705,
    1375,
    1376,
    1377,
    1391,
    1392,
    1393,
    2047,
    2048,
)
GUARD_WORDS = 32
GUARD_VALUE = -777.0
# Quiet NaN BF16 payloads, installed through the signed int16 view so the
# poison is independent of the device's float conversion path.
NAN_K_I16 = 0x7FC1
NAN_V_I16 = -63  # 0xFFC1, a negative quiet NaN in BF16


def _repeat_to_batch(values: Sequence[int]) -> tuple[int, ...]:
    if not values:
        raise ValueError("at least one length is required")
    return tuple(values[index % len(values)] for index in range(CASE7.batch_size))


MIXED_LENGTHS = _repeat_to_batch(EXACT_LENGTHS)
NO_LEN0_MIXED_LENGTHS = _repeat_to_batch(tuple(length for length in EXACT_LENGTHS if length != 0))
FULL_LENGTHS = (CASE7.seqlen_k,) * CASE7.batch_size
EXPECTED_LIVE_LENGTHS = {
    0: (0,),
    1: (1, 2, 15, 16, 17, 687, 688, 689, 703),
    2: (704, 705, 1375, 1376, 1377, 1391),
    3: (1392, 1393, 2047, 2048),
}


def _live_splits(seqlen: int) -> int:
    """Mirror exp612's case7 finalizer read contract on the host."""

    full_pages = seqlen // PAGE_SIZE
    if full_pages == 0:
        return int((seqlen & (PAGE_SIZE - 1)) != 0)
    return 1 + int(full_pages > 43) + int(full_pages > 86)


def _assert_requested_contract() -> None:
    flattened = tuple(
        length for lengths in EXPECTED_LIVE_LENGTHS.values() for length in lengths
    )
    if set(flattened) != set(EXACT_LENGTHS) or len(flattened) != len(EXACT_LENGTHS):
        raise AssertionError("live-split boundary table does not cover exact lengths")
    for live, lengths in EXPECTED_LIVE_LENGTHS.items():
        if any(_live_splits(length) != live for length in lengths):
            raise AssertionError(f"wrong host live-split mapping for live={live}: {lengths}")


def _assert_case7_layout(inputs: PagedDecodeInput) -> None:
    if (CASE7.batch_size, CASE7.seqlen_k, CASE7.num_heads_k) != (64, 2048, 8):
        raise AssertionError(f"unexpected case7 manifest: {CASE7}")
    expected_q = (64, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (64 * CASE7.max_pages, PAGE_SIZE, 8, HEAD_DIM)
    if inputs.case.case_id != 7:
        raise AssertionError(f"unexpected case: {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case7 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case7 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (CASE7.batch_size,):
        raise AssertionError("case7 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (CASE7.batch_size, CASE7.max_pages):
        raise AssertionError("case7 block_table shape mismatch")
    if inputs.num_blocks != CASE7.batch_size * CASE7.max_pages:
        raise AssertionError("case7 physical page count mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in lengths)
    if len(values) == 1:
        values = values * CASE7.batch_size
    if len(values) != CASE7.batch_size:
        raise ValueError(f"expected one or {CASE7.batch_size} lengths, got {values}")
    if any(value < 0 or value > CASE7.seqlen_k for value in values):
        raise ValueError(f"length outside case7 capacity: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    """Use legal, nonaliased physical IDs so poison reads are observable."""

    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(CASE7.batch_size, CASE7.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("constructed page table contains an invalid page ID")


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
    return storage, before_head, before_tail


def _guards_ok(
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _new_inputs(seed: int) -> tuple[
    PagedDecodeInput, torch.Tensor, torch.Tensor, torch.Tensor
]:
    inputs = make_input(CASE7, seed=seed, length_mode="full")
    _assert_case7_layout(inputs)
    _install_disjoint_page_table(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail


def _padding_page_ids_and_tail_tokens(
    inputs: PagedDecodeInput,
) -> tuple[list[int], list[tuple[int, int]]]:
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    page_ids: list[int] = []
    tail_tokens: list[tuple[int, int]] = []
    table = inputs.block_table.detach().to(device="cpu")
    for batch, length_value in enumerate(lengths):
        length = int(length_value)
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        row = table[batch].tolist()
        page_ids.extend(int(page) for page in row[valid_pages:])
        remainder = length & (PAGE_SIZE - 1)
        if remainder:
            # The last valid page is legal, but tokens [remainder, 16) are
            # outside cache_seqlens and must never influence the result.
            tail_tokens.extend(
                (int(row[valid_pages - 1]), token)
                for token in range(remainder, PAGE_SIZE)
            )
    return page_ids, tail_tokens


def _format_ranges(values: Sequence[int]) -> str:
    """Render sorted integer IDs as compact inclusive ranges."""

    if not values:
        return "none"
    ordered = sorted(set(int(value) for value in values))
    ranges: list[str] = []
    start = previous = ordered[0]
    for value in ordered[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = value
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(ranges)


def _format_tail_tokens(tokens: Sequence[tuple[int, int]]) -> str:
    if not tokens:
        return "none"
    grouped: dict[int, list[int]] = {}
    for page, token in tokens:
        grouped.setdefault(int(page), []).append(int(token))
    return ";".join(
        f"page={page}:tokens={_format_ranges(page_tokens)}"
        for page, page_tokens in sorted(grouped.items())
    )


def _audit_page_table(
    inputs: PagedDecodeInput,
    lengths: Sequence[int],
    label: str,
) -> tuple[set[int], set[int]]:
    """Prove physical page uniqueness and print every row's valid/padding range."""

    table = inputs.block_table.detach().to(device="cpu").tolist()
    if len(table) != CASE7.batch_size:
        raise AssertionError(f"{label}: unexpected page-table rows: {len(table)}")
    flat = [int(page) for row in table for page in row]
    if len(flat) != inputs.num_blocks or len(set(flat)) != inputs.num_blocks:
        raise AssertionError(
            f"{label}: block_table physical IDs are not globally unique "
            f"(entries={len(flat)} unique={len(set(flat))} num_blocks={inputs.num_blocks})"
        )
    if any(page < 0 or page >= inputs.num_blocks for page in flat):
        raise AssertionError(f"{label}: block_table contains an out-of-range physical page")

    valid_pages_all: set[int] = set()
    padding_pages_all: set[int] = set()
    for batch, (row, length_value) in enumerate(zip(table, lengths)):
        length = int(length_value)
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        valid_pages_ids = [int(page) for page in row[:valid_pages]]
        padding_page_ids = [int(page) for page in row[valid_pages:]]
        valid_pages_all.update(valid_pages_ids)
        padding_pages_all.update(padding_page_ids)
        remainder = length & (PAGE_SIZE - 1)
        tail_tokens = (
            [(int(row[valid_pages - 1]), token) for token in range(remainder, PAGE_SIZE)]
            if remainder
            else []
        )
        print(
            f"[INFO] page-audit {label} row={batch} length={length} "
            f"valid_page_ids={_format_ranges(valid_pages_ids)} "
            f"padding_page_ids={_format_ranges(padding_page_ids)} "
            f"tail_tokens={_format_tail_tokens(tail_tokens)}"
        )

    overlap = valid_pages_all & padding_pages_all
    if overlap:
        raise AssertionError(
            f"{label}: a poisonable padding page is valid for another row: "
            f"{_format_ranges(sorted(overlap))}"
        )
    print(
        f"[PASS] page-audit {label} physical_page_global_unique=True "
        f"entries={len(flat)} valid_pages={len(valid_pages_all)} "
        f"padding_pages={len(padding_pages_all)} valid_padding_overlap=False"
    )
    return valid_pages_all, padding_pages_all


def _write_nan_poison(
    inputs: PagedDecodeInput,
    *,
    poison_pages: bool = True,
    poison_tails: bool = True,
) -> tuple[int, int]:
    """Poison only logical padding; all physical IDs remain in range."""

    page_ids, tail_tokens = _padding_page_ids_and_tail_tokens(inputs)
    if not poison_pages:
        page_ids = []
    if not poison_tails:
        tail_tokens = []
    device = inputs.k_cache.device
    if page_ids:
        ids = torch.tensor(page_ids, dtype=torch.int64, device=device)
        inputs.k_cache.view(torch.int16).index_fill_(0, ids, NAN_K_I16)
        inputs.v_cache.view(torch.int16).index_fill_(0, ids, NAN_V_I16)
    for page, token in tail_tokens:
        inputs.k_cache[page, token].view(torch.int16).fill_(NAN_K_I16)
        inputs.v_cache[page, token].view(torch.int16).fill_(NAN_V_I16)
    return len(page_ids), len(tail_tokens)


def _restore_cache(
    inputs: PagedDecodeInput, base_k: torch.Tensor, base_v: torch.Tensor
) -> None:
    inputs.k_cache.copy_(base_k)
    inputs.v_cache.copy_(base_v)


def _failure_signature(
    actual: torch.Tensor,
    inputs: PagedDecodeInput,
) -> tuple[tuple[bool, ...], tuple[tuple[int, int, int], ...]]:
    """Return per-batch finite bits and (batch, head, length) failures."""

    finite_tensor = torch.isfinite(actual)
    finite_by_batch = finite_tensor.reshape(CASE7.batch_size, -1).all(dim=1)
    finite_bits = tuple(bool(value) for value in finite_by_batch.detach().to(device="cpu").tolist())
    bad_by_head = (~finite_tensor).any(dim=3)[:, 0, :]
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    bad_cpu = bad_by_head.detach().to(device="cpu").tolist()
    failures = tuple(
        (batch, head, int(lengths[batch]))
        for batch, row in enumerate(bad_cpu)
        for head, bad in enumerate(row)
        if bool(bad)
    )
    return finite_bits, failures


def _report_nonfinite(
    label: str,
    actual: torch.Tensor,
    inputs: PagedDecodeInput,
) -> None:
    finite_bits, failures = _failure_signature(actual, inputs)
    grouped: dict[tuple[int, int], list[int]] = {}
    for batch, head, length in failures:
        grouped.setdefault((batch, length), []).append(head)
    grouped_text = ";".join(
        f"batch={batch} length={length} heads={_format_ranges(heads)}"
        for (batch, length), heads in sorted(grouped.items())
    )
    print(
        f"[INFO] {label} nonfinite_batches="
        f"{_format_ranges([index for index, finite in enumerate(finite_bits) if not finite])} "
        f"nonfinite_batch_head_length={grouped_text or 'none'}"
    )


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
    finite = bool(torch.isfinite(actual).all().item())
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    within = finite and bool(torch.isfinite(difference).all().item()) and bool(
        (difference <= tolerance).all().item()
    )
    if finite and bool(torch.isfinite(difference).all().item()):
        max_error = float(difference.max().item())
        max_ratio = float((difference / tolerance).max().item())
    else:
        max_error = float("inf")
        max_ratio = float("inf")
    if not finite:
        _report_nonfinite(label, actual, inputs)
    guards = _guards_ok(storage, before_head, before_tail)
    passed = within and guards
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} finite={finite} within_tolerance={within} "
        f"max_error={max_error:.6e} max_tol_ratio={max_ratio:.3f} guards={guards}"
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
    reference = flash_reference(inputs)
    torch.cuda.synchronize()
    reference_finite = bool(torch.isfinite(reference).all().item())
    if not reference_finite:
        print(f"[FAIL] {label} reference_finite=False")
        return False, None, None, None

    candidate_result = _evaluate(
        f"{label} candidate", candidate, inputs, reference,
        storage, before_head, before_tail,
    )
    control_result = _evaluate(
        f"{label} control", control, inputs, reference,
        storage, before_head, before_tail,
    )
    candidate_ok, candidate_out, candidate_error, candidate_ratio, candidate_finite = candidate_result
    control_ok, control_out, control_error, control_ratio, control_finite = control_result
    candidate_signature = _failure_signature(candidate_out, inputs)
    control_signature = _failure_signature(control_out, inputs)
    finite_bits_equal = candidate_signature[0] == control_signature[0]
    failure_set_equal = candidate_signature[1] == control_signature[1]
    pair_diff = (candidate_out.float() - control_out.float()).abs()
    pair_tol = ATOL + RTOL * reference.float().abs()
    pair_match = bool(torch.isfinite(pair_diff).all().item()) and bool(
        (pair_diff <= pair_tol).all().item()
    )
    passed = candidate_ok and candidate_finite and (
        (control_ok and control_finite) if require_control else True
    )
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} reference_finite={reference_finite} "
        f"candidate_error={candidate_error:.6e} candidate_tol_ratio={candidate_ratio:.3f} "
        f"control_error={control_error:.6e} control_tol_ratio={control_ratio:.3f} "
        f"candidate_control_within_tolerance={pair_match} "
        f"candidate_control_finite_bits_equal={finite_bits_equal} "
        f"candidate_control_failure_set_equal={failure_set_equal} "
        f"require_control={require_control} "
        f"control_gate={'PASS' if control_ok and control_finite else 'FAIL'}"
    )
    return passed, reference.detach().clone(), candidate_out, control_out


def _run_isolated_poison_probe(
    candidate,
    control,
    *,
    label: str,
    lengths: Sequence[int],
    seed: int,
    poison_pages: bool,
    poison_tails: bool,
) -> bool:
    """Run one baseline plus one independently selected poison mode."""

    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    try:
        values = _set_lengths(inputs, lengths)
        valid_pages, padding_pages = _audit_page_table(inputs, values, label)
        all_padding_ids, all_tail_tokens = _padding_page_ids_and_tail_tokens(inputs)
        if set(all_padding_ids) - padding_pages:
            raise AssertionError(f"{label}: poison page is not a row padding page")
        if set(all_padding_ids) & valid_pages:
            raise AssertionError(f"{label}: poison page is a row-valid page")
        print(
            f"[INFO] poison-audit {label} page_poison_selected={poison_pages} "
            f"tail_poison_selected={poison_tails} "
            f"padding_page_ids_not_valid=True tail_tokens={len(all_tail_tokens)}"
        )

        baseline_ok, baseline_ref, baseline_candidate, baseline_control = _pair_check(
            f"{label} baseline", candidate, control, inputs,
            storage, before_head, before_tail,
            require_control=True,
        )
        _restore_cache(inputs, base_k, base_v)
        poisoned_pages, poisoned_tails = _write_nan_poison(
            inputs, poison_pages=poison_pages, poison_tails=poison_tails,
        )
        poisoned_ok, poisoned_ref, poisoned_candidate, poisoned_control = _pair_check(
            f"{label} poison pages={poisoned_pages} tails={poisoned_tails}",
            candidate, control, inputs, storage, before_head, before_tail,
            require_control=not poison_tails,
        )
        if any(
            value is None
            for value in (
                baseline_ref,
                baseline_candidate,
                baseline_control,
                poisoned_ref,
                poisoned_candidate,
                poisoned_control,
            )
        ):
            return False
        reference_unchanged = torch.equal(baseline_ref, poisoned_ref)
        candidate_unchanged = torch.equal(baseline_candidate, poisoned_candidate)
        poison_invariant = reference_unchanged and candidate_unchanged
        print(
            f"[{'PASS' if poison_invariant else 'FAIL'}] {label} poison-invariant "
            f"reference_unchanged={reference_unchanged} "
            f"candidate_unpoisoned_equal={candidate_unchanged} "
            f"candidate_poison_matches_reference_gate={poisoned_ok}"
        )
        return baseline_ok and poisoned_ok and poison_invariant
    finally:
        del base_k, base_v, inputs
        torch.cuda.empty_cache()


def _run_isolated_diagnostics(candidate, control, seed: int) -> bool:
    """Separate page and tail poisoning before allowing workspace reuse."""

    all_passed = True
    # This is deliberately a no-len0 mixed batch so a zero-length row cannot
    # hide a page-table or output failure in the first isolation pass.
    all_passed = _run_isolated_poison_probe(
        candidate,
        control,
        label="case7 no-len0-mixed pages-only",
        lengths=NO_LEN0_MIXED_LENGTHS,
        seed=seed + 700,
        poison_pages=True,
        poison_tails=False,
    ) and all_passed
    # A single short boundary has both one valid page and many padding pages.
    all_passed = _run_isolated_poison_probe(
        candidate,
        control,
        label="case7 single-length-17 pages-only",
        lengths=(17,),
        seed=seed + 701,
        poison_pages=True,
        poison_tails=False,
    ) and all_passed

    tail_mixed_ok = _run_isolated_poison_probe(
        candidate,
        control,
        label="case7 no-len0-mixed tails-only",
        lengths=NO_LEN0_MIXED_LENGTHS,
        seed=seed + 800,
        poison_pages=False,
        poison_tails=True,
    )
    all_passed = tail_mixed_ok and all_passed

    # If the mixed tail probe fails, isolate the requested odd/even tail
    # boundaries one at a time and retain the candidate/control signatures.
    if not tail_mixed_ok:
        for index, length in enumerate((1, 15, 17, 687, 689, 703)):
            boundary_ok = _run_isolated_poison_probe(
                candidate,
                control,
                label=f"case7 single-length-{length} tails-only",
                lengths=(length,),
                seed=seed + 801 + index,
                poison_pages=False,
                poison_tails=True,
            )
            all_passed = boundary_ok and all_passed
    return all_passed


def _run_mixed_poison(
    candidate, control, seed: int
) -> bool:
    inputs, storage, before_head, before_tail = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    try:
        _set_lengths(inputs, MIXED_LENGTHS)
        observed_live = {_live_splits(length) for length in MIXED_LENGTHS}
        if observed_live != {0, 1, 2, 3}:
            raise AssertionError(f"mixed batch does not cover live_splits 0/1/2/3: {observed_live}")
        missing = sorted(set(EXACT_LENGTHS) - set(MIXED_LENGTHS))
        if missing:
            raise AssertionError(f"mixed batch omitted exact lengths: {missing}")
        counts = {live: sum(_live_splits(length) == live for length in MIXED_LENGTHS) for live in range(4)}
        print(
            f"[INFO] case=7 mixed B=64 lengths={','.join(map(str, EXACT_LENGTHS))} "
            f"live_splits_counts={counts}"
        )

        baseline_ok, baseline_ref, baseline_candidate, baseline_control = _pair_check(
            "case7 mixed-64 baseline", candidate, control, inputs,
            storage, before_head, before_tail,
        )
        _restore_cache(inputs, base_k, base_v)
        poisoned_pages, poisoned_tails = _write_nan_poison(inputs)
        poisoned_ok, poisoned_ref, poisoned_candidate, poisoned_control = _pair_check(
            f"case7 mixed-64 NaN poison pages={poisoned_pages} tails={poisoned_tails}",
            candidate, control, inputs, storage, before_head, before_tail,
        )
        if any(
            value is None
            for value in (
                baseline_ref,
                baseline_candidate,
                baseline_control,
                poisoned_ref,
                poisoned_candidate,
                poisoned_control,
            )
        ):
            return False
        reference_unchanged = torch.equal(baseline_ref, poisoned_ref)
        candidate_unchanged = torch.equal(baseline_candidate, poisoned_candidate)
        control_unchanged = torch.equal(baseline_control, poisoned_control)
        invariant = reference_unchanged and candidate_unchanged and control_unchanged
        print(
            f"[{'PASS' if invariant else 'FAIL'}] case7 invalid-padding/tail poison invariant "
            f"reference={reference_unchanged} candidate={candidate_unchanged} "
            f"control={control_unchanged}"
        )
        return baseline_ok and poisoned_ok and invariant
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
            ("full->short->full", (FULL_LENGTHS, MIXED_LENGTHS, FULL_LENGTHS)),
            ("short->full", (MIXED_LENGTHS, FULL_LENGTHS)),
        )
        all_passed = True
        for sequence_label, sequence in sequences:
            sequence_outputs: dict[int, tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = {}
            for step, lengths in enumerate(sequence, start=1):
                _restore_cache(inputs, base_k, base_v)
                _set_lengths(inputs, lengths)
                poisoned_pages = poisoned_tails = 0
                short_step = any(length < CASE7.seqlen_k for length in lengths)
                baseline_ref = baseline_candidate = baseline_control = None
                if short_step:
                    baseline_ok, baseline_ref, baseline_candidate, baseline_control = _pair_check(
                        f"case7 workspace {sequence_label} step={step}/{len(sequence)} "
                        "short-unpoisoned-baseline",
                        candidate, control, inputs, storage, before_head, before_tail,
                        require_control=True,
                    )
                    all_passed = all_passed and baseline_ok
                    _restore_cache(inputs, base_k, base_v)
                    _set_lengths(inputs, lengths)
                    poisoned_pages, poisoned_tails = _write_nan_poison(inputs)
                passed, reference, candidate_out, control_out = _pair_check(
                    f"case7 workspace {sequence_label} step={step}/{len(sequence)} "
                    f"poison_pages={poisoned_pages} poison_tails={poisoned_tails}",
                    candidate, control, inputs, storage, before_head, before_tail,
                    require_control=not short_step,
                )
                if reference is None or candidate_out is None or control_out is None:
                    all_passed = False
                    continue
                sequence_outputs[step] = (reference, candidate_out, control_out)
                if short_step:
                    short_reference_unchanged = torch.equal(baseline_ref, reference)
                    short_candidate_unchanged = torch.equal(baseline_candidate, candidate_out)
                    short_invariant = short_reference_unchanged and short_candidate_unchanged
                    print(
                        f"[{'PASS' if short_invariant else 'FAIL'}] case7 workspace "
                        f"{sequence_label} step={step}/{len(sequence)} short-poison-invariant "
                        f"reference_unchanged={short_reference_unchanged} "
                        f"candidate_unpoisoned_equal={short_candidate_unchanged} "
                        f"candidate_poison_matches_reference_gate={passed}"
                    )
                    all_passed = all_passed and short_invariant
                if lengths == FULL_LENGTHS:
                    if full_snapshot is None:
                        full_snapshot = (reference, candidate_out, control_out)
                    else:
                        same_full = all(
                            torch.equal(previous, current)
                            for previous, current in zip(full_snapshot, sequence_outputs[step])
                        )
                        print(
                            f"[{'PASS' if same_full else 'FAIL'}] case7 workspace {sequence_label} "
                            f"full-state invariant={same_full} "
                            f"full_normal_repeat_deterministic={same_full}"
                        )
                        all_passed = all_passed and same_full
                all_passed = all_passed and passed
            print(
                f"[{'PASS' if all_passed else 'FAIL'}] case7 workspace sequence {sequence_label}"
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
    if (CASE7.batch_size, CASE7.seqlen_k, CASE7.num_heads_k) != (64, 2048, 8):
        raise RuntimeError(f"unexpected case7 manifest: {CASE7}")
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    if not _run_isolated_diagnostics(candidate, control, args.seed + 6120):
        return 1
    if not _run_reuse(candidate, control, args.seed + 6121):
        return 1
    print(
        "case7 exp612 special correctness: PASS "
        "reference_finite=True candidate_finite=True guards=True "
        "live_splits=0/1/2/3 reuse=full->short->full,short->full"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
