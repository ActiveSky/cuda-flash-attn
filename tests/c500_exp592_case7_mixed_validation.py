#!/usr/bin/env python3
"""Validate exp592's case-7 dispatch boundaries in one loaded process.

This is a correctness-only wrapper for a later serial C500 run.  It keeps the
OJ case-7 shape (B=64, KV=8, L=2048) for every call, but writes a different
``cache_seqlens[b]`` for every batch row.  That is deliberately different from
the broadcast ``--length-values`` mode in ``c500_paged_decode_harness.py``.

The script has three deterministic sections:

* a mixed direct/normal batch containing every exp592 live-page boundary;
* a legal-page padding sentinel trap, checked before and after the sentinel
  pages are written; and
* repeated calls on the same B=64 allocation, including
  ``2048 -> 1 -> 2048`` and ``1 -> 2048`` reuse.

No candidate is selected or benchmarked here.  The loaded ``run_kernel``
function and all tensor/reference calls are supplied by the existing harness.

Usage (on a later C500 host)::

    python3 tests/c500_exp592_case7_mixed_validation.py \
        --library build/cuda_maca_optimized.so --seed 20260818
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
    CorrectnessResult,
    PagedDecodeInput,
    DEFAULT_LIBRARY,
    check_correctness,
    flash_reference,
    load_kernel,
    make_input,
    require_maca_gpu,
)


CASE7 = next(case for case in CASES if case.case_id == 7)
EXPECTED_LENGTHS = (
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
DIRECT_PAGE_LIMIT = 43
SENTINEL_K = 37.0
SENTINEL_V = -4096.0


def _repeat_to_batch(values: Sequence[int], batch_size: int) -> tuple[int, ...]:
    if not values:
        raise ValueError("at least one length is required")
    return tuple(values[index % len(values)] for index in range(batch_size))


def _assert_case7_layout(inputs: PagedDecodeInput) -> None:
    case = inputs.case
    if (case.case_id, case.batch_size, case.seqlen_k, case.num_heads_k) != (
        7,
        64,
        2048,
        8,
    ):
        raise AssertionError(f"unexpected case-7 config: {case}")
    expected_blocks = case.batch_size * case.max_pages
    expected_q = (64, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (expected_blocks, PAGE_SIZE, case.num_heads_k, HEAD_DIM)
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError(
            f"case-7 Q/output shape mismatch: {tuple(inputs.q.shape)} / "
            f"{tuple(inputs.output.shape)}"
        )
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case-7 K/V cache shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (case.batch_size,):
        raise AssertionError("case-7 cache_seqlens must have one value per row")
    if tuple(inputs.block_table.shape) != (case.batch_size, case.max_pages):
        raise AssertionError("case-7 block_table shape mismatch")
    if inputs.num_blocks != expected_blocks:
        raise AssertionError("case-7 num_blocks mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(length) for length in lengths)
    if len(values) != inputs.case.batch_size:
        raise ValueError(
            f"expected {inputs.case.batch_size} row lengths, got {len(values)}"
        )
    if any(length < 1 or length > inputs.case.seqlen_k for length in values):
        raise ValueError(f"lengths must be in [1, {inputs.case.seqlen_k}]")
    tensor = torch.tensor(
        values,
        dtype=torch.int32,
        device=inputs.cache_seqlens.device,
    )
    inputs.cache_seqlens.copy_(tensor)
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    """Give every row its own legal page range before writing sentinels."""

    _assert_case7_layout(inputs)
    table = torch.arange(
        inputs.num_blocks,
        dtype=torch.int32,
        device=inputs.block_table.device,
    ).reshape(inputs.case.batch_size, inputs.case.max_pages)
    inputs.block_table.copy_(table)
    valid = (table >= 0) & (table < inputs.num_blocks)
    if not bool(valid.all().item()):
        raise AssertionError("constructed block_table contains an invalid page ID")


def _padding_page_ids(inputs: PagedDecodeInput) -> torch.Tensor:
    """Return all legal physical IDs after each row's valid page prefix."""

    page_ids: list[torch.Tensor] = []
    lengths = inputs.cache_seqlens.detach().cpu().tolist()
    for batch_index, length in enumerate(lengths):
        valid_pages = (int(length) + PAGE_SIZE - 1) // PAGE_SIZE
        page_ids.append(inputs.block_table[batch_index, valid_pages:])
    nonempty = [ids.reshape(-1) for ids in page_ids if ids.numel()]
    if not nonempty:
        return torch.empty(
            (0,), dtype=torch.int64, device=inputs.block_table.device
        )
    return torch.cat(nonempty).to(dtype=torch.int64)


def _write_padding_sentinel(inputs: PagedDecodeInput) -> int:
    """Fill only padding pages; all IDs remain allocated and in range."""

    page_ids = _padding_page_ids(inputs)
    if page_ids.numel() == 0:
        raise AssertionError("sentinel section requires at least one padding page")
    if bool(((page_ids < 0) | (page_ids >= inputs.num_blocks)).any().item()):
        raise AssertionError("padding sentinel selected an invalid physical page")
    inputs.k_cache.index_fill_(0, page_ids, SENTINEL_K)
    inputs.v_cache.index_fill_(0, page_ids, SENTINEL_V)
    return int(page_ids.numel())


def _report(label: str, result: CorrectnessResult) -> bool:
    status = "PASS" if result.passed else "FAIL"
    print(
        f"[{status}] case=7 sequence={label} "
        f"finite={result.finite} match={result.matched_ratio:.6f} "
        f"max_error={result.max_error:.6e} "
        f"max_tol_ratio={result.max_outlier_ratio:.3f}"
    )
    return result.passed


def _snapshot_output(inputs: PagedDecodeInput) -> torch.Tensor:
    torch.cuda.synchronize()
    return inputs.output.detach().float().clone()


def _snapshot_reference(inputs: PagedDecodeInput) -> torch.Tensor:
    reference = flash_reference(inputs)
    torch.cuda.synchronize()
    return reference.detach().float().clone()


def _delta_within_tolerance(actual: torch.Tensor, expected: torch.Tensor) -> tuple[bool, float, float]:
    if actual.shape != expected.shape:
        return False, float("inf"), float("inf")
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    max_error = float(difference.max().item())
    max_ratio = float((difference / tolerance).max().item())
    return bool(torch.isfinite(actual).all().item()) and bool(
        (difference <= tolerance).all().item()
    ), max_error, max_ratio


def _report_sentinel(
    result: CorrectnessResult,
    baseline_actual: torch.Tensor,
    sentinel_actual: torch.Tensor,
    baseline_reference: torch.Tensor,
    sentinel_reference: torch.Tensor,
    sentinel_pages: int,
) -> bool:
    reference_ok, reference_error, reference_ratio = _delta_within_tolerance(
        sentinel_reference, baseline_reference
    )
    actual_ok, actual_error, actual_ratio = _delta_within_tolerance(
        sentinel_actual, baseline_actual
    )
    passed = result.passed and reference_ok and actual_ok
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] case=7 sequence=padding-sentinel "
        f"sentinel_pages={sentinel_pages} finite={result.finite} "
        f"tolerance={result.passed} reference_unchanged={reference_ok} "
        f"reference_max_error={reference_error:.6e} "
        f"reference_max_tol_ratio={reference_ratio:.3f} "
        f"candidate_unchanged={actual_ok} "
        f"candidate_max_error={actual_error:.6e} "
        f"candidate_max_tol_ratio={actual_ratio:.3f}"
    )
    return passed


def _new_case7_input(seed: int, lengths: Iterable[int]) -> PagedDecodeInput:
    inputs = make_input(CASE7, seed=seed, length_mode="full")
    _install_disjoint_page_table(inputs)
    _set_lengths(inputs, lengths)
    return inputs


def _run_mixed(kernel, seed: int) -> bool:
    lengths = _repeat_to_batch(EXPECTED_LENGTHS, CASE7.batch_size)
    direct_rows = sum(
        1 for length in lengths if (length + PAGE_SIZE - 1) // PAGE_SIZE <= DIRECT_PAGE_LIMIT
    )
    normal_rows = len(lengths) - direct_rows
    if not direct_rows or not normal_rows:
        raise AssertionError("mixed batch must contain both direct and normal rows")
    inputs = _new_case7_input(seed, lengths)
    try:
        print(
            f"[INFO] case=7 sequence=mixed-rows rows={len(lengths)} "
            f"direct_rows={direct_rows} normal_rows={normal_rows} "
            f"lengths={','.join(map(str, lengths))}"
        )
        result = check_correctness(kernel, inputs)
        return _report("mixed-rows", result)
    finally:
        del inputs
        torch.cuda.empty_cache()


def _run_padding_trap(kernel, seed: int) -> bool:
    lengths = _repeat_to_batch(EXPECTED_LENGTHS, CASE7.batch_size)
    inputs = _new_case7_input(seed, lengths)
    try:
        # First establish the result with ordinary random padding contents.
        baseline_result = check_correctness(kernel, inputs)
        baseline_ok = _report("padding-baseline", baseline_result)
        baseline_actual = _snapshot_output(inputs)
        baseline_reference = _snapshot_reference(inputs)

        sentinel_pages = _write_padding_sentinel(inputs)
        sentinel_result = check_correctness(kernel, inputs)
        sentinel_actual = _snapshot_output(inputs)
        sentinel_reference = _snapshot_reference(inputs)
        return _report_sentinel(
            sentinel_result,
            baseline_actual,
            sentinel_actual,
            baseline_reference,
            sentinel_reference,
            sentinel_pages,
        ) and baseline_ok
    finally:
        del inputs
        torch.cuda.empty_cache()


def _run_reuse_sequences(kernel, seed: int) -> bool:
    full = _repeat_to_batch((2048,), CASE7.batch_size)
    short = _repeat_to_batch((1,), CASE7.batch_size)
    all_short = _repeat_to_batch((1, 2, 15, 16, 17, 687, 688), CASE7.batch_size)
    inputs = _new_case7_input(seed, full)
    all_passed = True
    try:
        sequences = (
            ("reuse-2048-first", full),
            ("reuse-1", short),
            ("reuse-2048-second", full),
            ("reuse-1-to-2048-short", short),
            ("reuse-1-to-2048-full", full),
            ("all-short-rows", all_short),
        )
        for label, lengths in sequences:
            _set_lengths(inputs, lengths)
            result = check_correctness(kernel, inputs)
            all_passed = _report(label, result) and all_passed
    finally:
        del inputs
        torch.cuda.empty_cache()
    return all_passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--seed", type=int, default=20260818)
    args = parser.parse_args(argv)

    require_maca_gpu()
    if CASE7.batch_size != 64 or CASE7.num_heads_k != 8 or CASE7.seqlen_k != 2048:
        raise RuntimeError(f"case manifest no longer describes case 7 as expected: {CASE7}")
    kernel = load_kernel(args.library)
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    print(f"library: {args.library} | seed: {args.seed}")

    all_passed = True
    all_passed = _run_mixed(kernel, args.seed + 700) and all_passed
    all_passed = _run_padding_trap(kernel, args.seed + 701) and all_passed
    all_passed = _run_reuse_sequences(kernel, args.seed + 702) and all_passed
    print(f"case=7 exp592 mixed validation: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
