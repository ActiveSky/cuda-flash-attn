#!/usr/bin/env python3
"""Exp635 case-12 correctness-only C500 boundary and ownership checks.

The regular paged-decode harness deliberately keeps its input construction
simple.  This companion keeps one case-12 allocation alive while checking the
additional contracts needed by exp635: every 40-split/page boundary, mixed
per-row lengths with legal padding sentinels, a deliberately nonuniform raw
BF16 Q payload, output guards, and workspace reuse.  Candidate and control
are run against the same tensors and their BF16 outputs are compared bitwise.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable, Sequence

import numpy as np
import torch

from c500_case_manifest import CASES, HEAD_DIM, NUM_HEADS, PAGE_SIZE
from c500_paged_decode_harness import (
    ATOL,
    RTOL,
    DEFAULT_LIBRARY,
    PagedDecodeInput,
    flash_reference,
    load_kernel,
    make_input,
    require_maca_gpu,
    run_kernel,
)


CASE12 = next(case for case in CASES if case.case_id == 12)
GUARD_WORDS = 32
GUARD_VALUE = -777.0
SENTINEL_K = 37.0
SENTINEL_V = -4096.0
MIXED_LENGTHS = (1, 15, 16, 17, 831, 832, 833, 32767)


def _exact_241() -> tuple[int, ...]:
    """Return exp624's 241 page/split/tail lengths for case12.

    Case12 has 40 logical splits and 52 pages per split.  Around each of the
    39 internal split boundaries we test the boundary token and the following
    page boundary; the leading short lengths and final capacity tail complete
    the exact contract.
    """

    values = [1, 2, 15, 16, 17]
    for boundary in range(832, 32768, 832):
        values.extend((boundary - 1, boundary, boundary + 1))
        values.extend((boundary + 15, boundary + 16, boundary + 17))
    values.extend((32767, 32768))
    result = tuple(values)
    if len(result) != 241 or len(set(result)) != 241:
        raise AssertionError(f"expected 241 unique lengths, got {len(result)}")
    if min(result) < 1 or max(result) > CASE12.seqlen_k:
        raise AssertionError("exact length is outside case12 capacity")
    return result


EXACT_241 = _exact_241()


def _assert_case12_layout(inputs: PagedDecodeInput) -> None:
    expected = (8, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (8 * CASE12.max_pages, PAGE_SIZE, 8, HEAD_DIM)
    if inputs.case.case_id != 12:
        raise AssertionError(f"unexpected case: {inputs.case}")
    if tuple(inputs.q.shape) != expected or tuple(inputs.output.shape) != expected:
        raise AssertionError("case12 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case12 K/V shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (8,):
        raise AssertionError("case12 cache_seqlens shape mismatch")
    if tuple(inputs.block_table.shape) != (8, CASE12.max_pages):
        raise AssertionError("case12 block_table shape mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(length) for length in lengths)
    if len(values) == 1:
        values = values * inputs.case.batch_size
    if len(values) != inputs.case.batch_size:
        raise ValueError(f"expected 1 or {inputs.case.batch_size} lengths, got {len(values)}")
    if any(length < 1 or length > inputs.case.seqlen_k for length in values):
        raise ValueError("length outside case12 capacity")
    tensor = torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    inputs.cache_seqlens.copy_(tensor)
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    _assert_case12_layout(inputs)
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(inputs.case.batch_size, inputs.case.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table < 0) | (table >= inputs.num_blocks)).logical_not().all().item()):
        raise AssertionError("constructed page table has an invalid page ID")


def _install_unique_raw_bf16_q(inputs: PagedDecodeInput) -> int:
    """Install deterministic, nonuniform raw BF16 words in every Q row."""

    count = inputs.q.numel()
    if count != 32768:
        raise AssertionError(f"expected 32768 case12 Q words, got {count}")
    indices = np.arange(count, dtype=np.uint32)
    # Enumerate every sign/exponent/mantissa combination in the finite,
    # moderate BF16 range.  The linear index is the (b,h,d) payload index, so
    # no two Q words can alias even when a kernel accidentally reuses a row.
    sign = (indices >> 14) & 1
    exponent = (indices >> 7) & 0x7F
    mantissa = indices & 0x7F
    bits = ((sign << 15) | (exponent << 7) | mantissa).astype(np.uint16)
    unique_words = int(np.unique(bits).size)
    if unique_words != count:
        raise AssertionError(f"constructed Q words are not unique: {unique_words}/{count}")
    cpu_words = torch.from_numpy(bits.view(np.int16)).view(torch.bfloat16)
    if not bool(torch.isfinite(cpu_words).all().item()):
        raise AssertionError("constructed Q words contain non-finite BF16 values")
    inputs.q.copy_(cpu_words.reshape(inputs.q.shape).to(device=inputs.q.device))
    observed = (
        inputs.q.detach()
        .to(device="cpu")
        .view(torch.int16)
        .numpy()
        .view(np.uint16)
    )
    if not np.array_equal(observed, bits.reshape(observed.shape)):
        raise AssertionError("raw BF16 Q words changed during installation")
    observed_unique_words = int(np.unique(observed).size)
    if observed_unique_words != 32768:
        raise AssertionError(
            f"installed Q words are not unique: {observed_unique_words}/32768"
        )
    return observed_unique_words


def _install_output_guard(inputs: PagedDecodeInput) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
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
        raise AssertionError("guarded output view must be contiguous")
    return storage, before_head, before_tail


def _guards_ok(storage: torch.Tensor, before_head: torch.Tensor, before_tail: torch.Tensor) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _new_inputs(seed: int) -> tuple[PagedDecodeInput, torch.Tensor, torch.Tensor, torch.Tensor, int]:
    inputs = make_input(CASE12, seed=seed, length_mode="full")
    _assert_case12_layout(inputs)
    _install_disjoint_page_table(inputs)
    unique_words = _install_unique_raw_bf16_q(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail, unique_words


def _padding_page_ids(inputs: PagedDecodeInput) -> torch.Tensor:
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    ids: list[torch.Tensor] = []
    for row, length in enumerate(lengths):
        valid_pages = (int(length) + PAGE_SIZE - 1) // PAGE_SIZE
        ids.append(inputs.block_table[row, valid_pages:])
    nonempty = [value.reshape(-1) for value in ids if value.numel()]
    if not nonempty:
        return torch.empty((0,), dtype=torch.int64, device=inputs.block_table.device)
    return torch.cat(nonempty).to(dtype=torch.int64)


def _write_padding_sentinel(inputs: PagedDecodeInput) -> int:
    page_ids = _padding_page_ids(inputs)
    if page_ids.numel() == 0:
        raise AssertionError("mixed case12 lengths have no padding pages")
    if bool(((page_ids < 0) | (page_ids >= inputs.num_blocks)).any().item()):
        raise AssertionError("padding page ID is outside allocated cache")
    inputs.k_cache.index_fill_(0, page_ids, SENTINEL_K)
    inputs.v_cache.index_fill_(0, page_ids, SENTINEL_V)
    return int(page_ids.numel())


def _evaluate(
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> tuple[bool, torch.Tensor, float, float]:
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    actual_bf16 = inputs.output.detach().clone()
    actual = actual_bf16.float()
    expected = reference.float()
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    matched = float((difference <= tolerance).float().mean().item())
    max_error = float(difference.max().item())
    max_ratio = float((difference / tolerance).max().item())
    finite = bool(torch.isfinite(actual).all().item())
    required = 1.0 if inputs.case.kind == "edge" else 0.99
    passed = (
        finite
        and matched >= required
        and max_ratio <= 8.0
        and _guards_ok(storage, before_head, before_tail)
    )
    return passed, actual_bf16, max_error, max_ratio


def _run_pair(
    label: str,
    candidate,
    control,
    inputs: PagedDecodeInput,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> tuple[bool, torch.Tensor, torch.Tensor, torch.Tensor]:
    reference = flash_reference(inputs)
    torch.cuda.synchronize()
    candidate_ok, candidate_out, candidate_error, candidate_ratio = _evaluate(
        candidate, inputs, reference, storage, before_head, before_tail
    )
    q_before = inputs.q.detach().clone()
    control_ok, control_out, control_error, control_ratio = _evaluate(
        control, inputs, reference, storage, before_head, before_tail
    )
    q_unchanged = torch.equal(inputs.q, q_before)
    bit_equal = torch.equal(candidate_out, control_out)
    passed = candidate_ok and control_ok and bit_equal and q_unchanged
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} candidate_error={candidate_error:.6e} "
        f"control_error={control_error:.6e} candidate_tol_ratio={candidate_ratio:.3f} "
        f"control_tol_ratio={control_ratio:.3f} bit_equal={bit_equal} "
        f"q_unchanged={q_unchanged} guards={_guards_ok(storage, before_head, before_tail)}"
    )
    return passed, reference.detach().clone(), candidate_out, control_out


def _run_exact_241(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, unique_words = _new_inputs(seed)
    try:
        print(f"[INFO] exact-241 lengths={len(EXACT_241)} unique_q_words={unique_words}")
        for index, length in enumerate(EXACT_241):
            _set_lengths(inputs, (length,))
            passed, _, _, _ = _run_pair(
                f"case12 exact-{index + 1:03d}/{len(EXACT_241)} length={length}",
                candidate,
                control,
                inputs,
                storage,
                before_head,
                before_tail,
            )
            if not passed:
                return False
        print("[PASS] case12 exact-241 split/page/tail boundaries")
        return True
    finally:
        del inputs
        torch.cuda.empty_cache()


def _run_padding_trap(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, unique_words = _new_inputs(seed)
    try:
        _set_lengths(inputs, MIXED_LENGTHS)
        baseline_ok, baseline_ref, baseline_candidate, baseline_control = _run_pair(
            "case12 mixed-batch baseline", candidate, control, inputs, storage, before_head, before_tail
        )
        sentinel_pages = _write_padding_sentinel(inputs)
        sentinel_ok, sentinel_ref, sentinel_candidate, sentinel_control = _run_pair(
            "case12 mixed-batch padding-sentinel", candidate, control, inputs, storage, before_head, before_tail
        )
        reference_unchanged = torch.equal(baseline_ref, sentinel_ref)
        candidate_unchanged = torch.equal(baseline_candidate, sentinel_candidate)
        control_unchanged = torch.equal(baseline_control, sentinel_control)
        passed = baseline_ok and sentinel_ok and reference_unchanged and candidate_unchanged and control_unchanged
        status = "PASS" if passed else "FAIL"
        print(
            f"[{status}] case12 padding-trap sentinel_pages={sentinel_pages} "
            f"unique_q_words={unique_words} reference_unchanged={reference_unchanged} "
            f"candidate_unchanged={candidate_unchanged} control_unchanged={control_unchanged}"
        )
        return passed
    finally:
        del inputs
        torch.cuda.empty_cache()


def _run_reuse(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, unique_words = _new_inputs(seed)
    try:
        sequences: tuple[tuple[str, Sequence[Sequence[int]]], ...] = (
            ("32768->1->32768", ((32768,), (1,), (32768,))),
            ("1->32768", ((1,), (32768,))),
            ("mixed-batch-reuse", (MIXED_LENGTHS,)),
        )
        for sequence_label, sequence in sequences:
            for step, lengths in enumerate(sequence, start=1):
                _set_lengths(inputs, lengths)
                passed, _, _, _ = _run_pair(
                    f"case12 reuse {sequence_label} step={step}/{len(sequence)}",
                    candidate,
                    control,
                    inputs,
                    storage,
                    before_head,
                    before_tail,
                )
                if not passed:
                    return False
        print(f"[PASS] case12 workspace reuse sequences unique_q_words={unique_words}")
        return True
    finally:
        del inputs
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args(argv)

    require_maca_gpu()
    if (CASE12.batch_size, CASE12.seqlen_k, CASE12.num_heads_k) != (8, 32768, 8):
        raise RuntimeError(f"unexpected case12 manifest: {CASE12}")
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    print(f"candidate: {args.candidate} | control: {args.control} | seed: {args.seed}")
    if not _run_exact_241(candidate, control, args.seed + 1200):
        return 1
    if not _run_padding_trap(candidate, control, args.seed + 1201):
        return 1
    if not _run_reuse(candidate, control, args.seed + 1202):
        return 1
    print("case12 exp635 special correctness: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
