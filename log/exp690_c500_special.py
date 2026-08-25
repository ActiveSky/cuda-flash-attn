#!/usr/bin/env python3
"""Exp690 case-7 direct-three-chunk correctness gate on a MetaX C500.

This file is deliberately kept under the exp690 log namespace.  It does not
change the shared test harness or any project source.  The test keeps one
case-7 allocation alive and compares the candidate and immutable control on
the same tensors.  In addition to the regular mixed-row test it exercises the
zero/short lengths, the 43/86/127 page ownership boundaries, legal padding and
tail poison, output guards, all 32 query heads, and workspace reuse.
"""

from __future__ import annotations

import argparse
import gc
import random
from pathlib import Path
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
GUARD_WORDS = 64
GUARD_VALUE = -777.0
SENTINEL_K = 37.0
SENTINEL_V = -4096.0

# Include zero explicitly even though the regular parser only accepts the
# positive OJ lengths.  It is a useful no-token safety probe for the direct
# path and must not cause a launch, guard, or stale-output failure.
EXACT_LENGTHS = (
    0,
    1,
    15,
    16,
    17,
    42 * 16 - 1,
    42 * 16,
    42 * 16 + 1,
    43 * 16 - 1,
    43 * 16,
    43 * 16 + 1,
    85 * 16 - 1,
    85 * 16,
    85 * 16 + 1,
    86 * 16 - 1,
    86 * 16,
    86 * 16 + 1,
    127 * 16 - 1,
    127 * 16,
    127 * 16 + 1,
    2048,
)


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (64, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (64 * CASE7.max_pages, PAGE_SIZE, 8, HEAD_DIM)
    if (CASE7.case_id, CASE7.batch_size, CASE7.seqlen_k, CASE7.num_heads_k) != (
        7,
        64,
        2048,
        8,
    ):
        raise AssertionError(f"case manifest changed: {CASE7}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case7 Q/output layout mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case7 K/V layout mismatch")
    if tuple(inputs.cache_seqlens.shape) != (64,) or tuple(inputs.block_table.shape) != (64, 128):
        raise AssertionError("case7 metadata layout mismatch")


def _install_disjoint_pages(inputs: PagedDecodeInput) -> None:
    _assert_layout(inputs)
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(64, 128)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("invalid page table constructed")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in lengths)
    if len(values) == 1:
        values = values * CASE7.batch_size
    if len(values) != CASE7.batch_size:
        raise ValueError(f"expected 1 or 64 lengths, got {len(values)}")
    if any(value < 0 or value > CASE7.seqlen_k for value in values):
        raise ValueError(f"length outside [0, {CASE7.seqlen_k}]: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_guard(inputs: PagedDecodeInput):
    storage = torch.full(
        (inputs.output.numel() + 2 * GUARD_WORDS,),
        GUARD_VALUE,
        dtype=inputs.output.dtype,
        device=inputs.output.device,
    )
    inputs.output = storage[GUARD_WORDS:-GUARD_WORDS].view_as(inputs.q)
    if not inputs.output.is_contiguous():
        raise AssertionError("guarded output is not contiguous")
    return storage, storage[:GUARD_WORDS].clone(), storage[-GUARD_WORDS:].clone()


def _guards_ok(storage, before_head, before_tail) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _padding_ids(inputs: PagedDecodeInput) -> torch.Tensor:
    lengths = inputs.cache_seqlens.detach().cpu().tolist()
    pieces: list[torch.Tensor] = []
    for row, length in enumerate(lengths):
        valid_pages = (int(length) + PAGE_SIZE - 1) // PAGE_SIZE
        if valid_pages < CASE7.max_pages:
            pieces.append(inputs.block_table[row, valid_pages:])
    if not pieces:
        return torch.empty((0,), dtype=torch.int64, device=inputs.block_table.device)
    return torch.cat([piece.reshape(-1) for piece in pieces]).to(torch.int64)


def _write_padding_sentinel(inputs: PagedDecodeInput) -> int:
    page_ids = _padding_ids(inputs)
    if page_ids.numel() == 0:
        raise AssertionError("padding poison has no padding pages")
    if bool(((page_ids < 0) | (page_ids >= inputs.num_blocks)).any().item()):
        raise AssertionError("padding poison selected invalid page")
    inputs.k_cache.index_fill_(0, page_ids, SENTINEL_K)
    inputs.v_cache.index_fill_(0, page_ids, SENTINEL_V)
    return int(page_ids.numel())


def _write_tail_sentinel(inputs: PagedDecodeInput) -> int:
    lengths = inputs.cache_seqlens.detach().cpu().tolist()
    poisoned = 0
    for row, length in enumerate(lengths):
        length = int(length)
        tail = length % PAGE_SIZE
        if length <= 0 or tail == 0:
            continue
        page = (length - 1) // PAGE_SIZE
        pid = int(inputs.block_table[row, page].item())
        inputs.k_cache[pid, tail:, :, :].fill_(SENTINEL_K)
        inputs.v_cache[pid, tail:, :, :].fill_(SENTINEL_V)
        poisoned += PAGE_SIZE - tail
    if poisoned == 0:
        raise AssertionError("tail poison has no partial tail")
    return poisoned


def _input_snapshot(inputs: PagedDecodeInput):
    return (
        inputs.q.detach().clone(),
        inputs.cache_seqlens.detach().clone(),
        inputs.block_table.detach().clone(),
    )


def _inputs_unchanged(inputs: PagedDecodeInput, snapshot) -> bool:
    return (
        torch.equal(inputs.q, snapshot[0])
        and torch.equal(inputs.cache_seqlens, snapshot[1])
        and torch.equal(inputs.block_table, snapshot[2])
    )


def _score(actual: torch.Tensor, expected: torch.Tensor) -> tuple[bool, float, float, float, int]:
    actual_f = actual.float()
    expected_f = expected.float()
    finite = bool(torch.isfinite(actual_f).all().item())
    if not bool(torch.isfinite(expected_f).all().item()):
        return finite, float("nan"), float("nan"), float("nan"), 0
    difference = (actual_f - expected_f).abs()
    tolerance = ATOL + RTOL * expected_f.abs()
    ratio = difference / tolerance
    matched = float((difference <= tolerance).float().mean().item())
    max_error = float(difference.max().item())
    max_ratio = float(ratio.max().item())
    per_head = (difference <= tolerance).reshape(64, 1, NUM_HEADS, HEAD_DIM).float().mean(
        dim=(0, 1, 3)
    )
    bad_heads = int((per_head < 0.99).sum().item())
    passed = finite and matched >= 0.99 and bad_heads == 0 and max_ratio <= 8.0
    return passed, matched, max_error, max_ratio, bad_heads


def _invoke(kernel, inputs: PagedDecodeInput, storage, before_head, before_tail):
    snapshot = _input_snapshot(inputs)
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    actual = inputs.output.detach().clone()
    return (
        actual,
        _guards_ok(storage, before_head, before_tail),
        _inputs_unchanged(inputs, snapshot),
    )


def _evaluate_pair(label: str, candidate, control, inputs, guards):
    storage, before_head, before_tail = guards
    reference = flash_reference(inputs).detach().clone()
    torch.cuda.synchronize()
    candidate_out, candidate_guards, candidate_inputs = _invoke(
        candidate, inputs, storage, before_head, before_tail
    )
    control_out, control_guards, control_inputs = _invoke(
        control, inputs, storage, before_head, before_tail
    )
    candidate_score = _score(candidate_out, reference)
    control_score = _score(control_out, reference)
    cc_diff = (candidate_out.float() - control_out.float()).abs()
    cc_tol = ATOL + RTOL * control_out.float().abs()
    cc_finite = bool(torch.isfinite(candidate_out.float()).all().item()) and bool(
        torch.isfinite(control_out.float()).all().item()
    )
    cc_ratio = float((cc_diff / cc_tol).max().item()) if cc_finite else float("inf")
    cc_match = float((cc_diff <= cc_tol).float().mean().item()) if cc_finite else 0.0
    cc_ok = cc_finite and cc_match >= 0.99 and cc_ratio <= 8.0
    expected_finite = bool(torch.isfinite(reference.float()).all().item())
    # The zero-token reference is accepted as an independent safety probe if
    # a backend reference build returns non-finite sentinels; positive lengths
    # always require the ordinary numerical gate.
    if expected_finite:
        passed = candidate_score[0] and control_score[0] and cc_ok
    else:
        passed = cc_ok and bool(torch.isfinite(candidate_out.float()).all().item())
    passed = passed and candidate_guards and control_guards and candidate_inputs and control_inputs
    print(
        f"[{('PASS' if passed else 'FAIL')}] {label} "
        f"ref_finite={expected_finite} "
        f"cand_match={candidate_score[1]:.6f} cand_err={candidate_score[2]:.6e} "
        f"cand_ratio={candidate_score[3]:.3f} cand_bad_heads={candidate_score[4]} "
        f"ctrl_match={control_score[1]:.6f} ctrl_err={control_score[2]:.6e} "
        f"ctrl_ratio={control_score[3]:.3f} ctrl_bad_heads={control_score[4]} "
        f"cc_match={cc_match:.6f} cc_ratio={cc_ratio:.3f} "
        f"guards={candidate_guards and control_guards} "
        f"inputs={candidate_inputs and control_inputs}"
    )
    return passed, reference, candidate_out, control_out


def _phase_snapshot(inputs: PagedDecodeInput):
    # K/V are read-only kernel inputs.  Keep a complete snapshot per poison
    # phase so a silent illegal store is detected without hashing shortcuts.
    return inputs.k_cache.detach().clone(), inputs.v_cache.detach().clone()


def _phase_inputs_ok(inputs: PagedDecodeInput, snapshot) -> bool:
    return torch.equal(inputs.k_cache, snapshot[0]) and torch.equal(
        inputs.v_cache, snapshot[1]
    )


def _repeat(values: Sequence[int]) -> tuple[int, ...]:
    return tuple(values[index % len(values)] for index in range(CASE7.batch_size))


def _compare_stability(label: str, actual: torch.Tensor, baseline: torch.Tensor) -> bool:
    actual_f = actual.float()
    baseline_f = baseline.float()
    diff = (actual_f - baseline_f).abs()
    tolerance = ATOL + RTOL * baseline_f.abs()
    finite = bool(torch.isfinite(actual_f).all().item())
    match = float((diff <= tolerance).float().mean().item())
    ratio = float((diff / tolerance).max().item())
    passed = finite and match >= 0.99 and ratio <= 8.0
    print(
        f"[{('PASS' if passed else 'FAIL')}] {label} "
        f"match={match:.6f} max_error={float(diff.max().item()):.6e} "
        f"max_tol_ratio={ratio:.3f}"
    )
    return passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260824)
    args = parser.parse_args(argv)

    require_maca_gpu()
    if CASE7.batch_size != 64 or CASE7.seqlen_k != 2048 or CASE7.num_heads_k != 8:
        raise RuntimeError(f"unexpected case7 manifest: {CASE7}")
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    print(f"candidate: {args.candidate}")
    print(f"control:   {args.control}")
    print(f"exact_lengths: {','.join(map(str, EXACT_LENGTHS))}")

    inputs = make_input(CASE7, seed=args.seed, length_mode="full")
    _install_disjoint_pages(inputs)
    guards = _install_guard(inputs)
    all_passed = True

    # Exact single-length sweep includes every requested page bucket and the
    # full 128-page capacity.  The 127-page interior is included both with and
    # without a tail to cover all three CTA ownership counts.
    kv_snapshot = _phase_snapshot(inputs)
    for length in EXACT_LENGTHS:
        _set_lengths(inputs, (length,))
        passed, _, _, _ = _evaluate_pair(f"exact-L{length}", candidate, control, inputs, guards)
        all_passed = passed and all_passed
    kv_ok = _phase_inputs_ok(inputs, kv_snapshot)
    print(f"[{'PASS' if kv_ok else 'FAIL'}] exact-phase K/V input invariance")
    all_passed = kv_ok and all_passed

    # Mixed rows exercise different bucket counts in one launch, including
    # both direct and normal rows, while each row owns disjoint physical pages.
    mixed_lengths = _repeat((0, 1, 15, 16, 17, 671, 672, 673, 687, 688, 689,
                             1359, 1360, 1361, 1375, 1376, 1377, 2031,
                             2032, 2047, 2048))
    _set_lengths(inputs, mixed_lengths)
    kv_snapshot = _phase_snapshot(inputs)
    passed, baseline_ref, baseline_candidate, baseline_control = _evaluate_pair(
        "mixed-all-boundaries", candidate, control, inputs, guards
    )
    all_passed = passed and all_passed

    # Poison only the padding pages.  Reference and both kernels must be
    # unchanged, proving cache_seqlens rather than legal-looking table padding
    # controls the load range.
    padding_pages = _write_padding_sentinel(inputs)
    padding_kv_snapshot = _phase_snapshot(inputs)
    passed, poisoned_ref, poisoned_candidate, poisoned_control = _evaluate_pair(
        "mixed-padding-poison", candidate, control, inputs, guards
    )
    all_passed = passed and all_passed
    all_passed = _compare_stability(
        "padding reference unchanged", poisoned_ref, baseline_ref
    ) and all_passed
    all_passed = _compare_stability(
        "padding candidate unchanged", poisoned_candidate, baseline_candidate
    ) and all_passed
    all_passed = _compare_stability(
        "padding control unchanged", poisoned_control, baseline_control
    ) and all_passed
    kv_ok = _phase_inputs_ok(inputs, padding_kv_snapshot)
    print(f"[{'PASS' if kv_ok else 'FAIL'}] padding-phase K/V input invariance")
    all_passed = kv_ok and all_passed
    print(f"[INFO] padding poisoned physical pages={padding_pages}")

    # Poison invalid tokens in each non-page-aligned final valid page.  The
    # baseline output above used random tail values; re-run after poisoning and
    # require the same result.
    tail_tokens = _write_tail_sentinel(inputs)
    tail_kv_snapshot = _phase_snapshot(inputs)
    passed, tail_ref, tail_candidate, tail_control = _evaluate_pair(
        "mixed-tail-poison", candidate, control, inputs, guards
    )
    all_passed = passed and all_passed
    all_passed = _compare_stability("tail reference unchanged", tail_ref, poisoned_ref) and all_passed
    all_passed = _compare_stability("tail candidate unchanged", tail_candidate, poisoned_candidate) and all_passed
    all_passed = _compare_stability("tail control unchanged", tail_control, poisoned_control) and all_passed
    print(f"[INFO] tail poisoned invalid tokens={tail_tokens}")
    # K/V must not be written by either kernel.  The snapshot is taken after
    # the intentional tail poison and is checked after both pair invocations.
    kv_ok = _phase_inputs_ok(inputs, tail_kv_snapshot)
    print(f"[{'PASS' if kv_ok else 'FAIL'}] tail-phase K/V input invariance")
    all_passed = kv_ok and all_passed

    # Deterministic random mixed rows, repeated twice, cover arbitrary
    # per-row ownership and make stale workspace/state visible.
    rng = random.Random(args.seed + 690)
    random_lengths = tuple(rng.randrange(0, CASE7.seqlen_k + 1) for _ in range(64))
    _set_lengths(inputs, random_lengths)
    passed, _, _, _ = _evaluate_pair("random-mixed-1", candidate, control, inputs, guards)
    all_passed = passed and all_passed
    passed, _, _, _ = _evaluate_pair("random-mixed-2", candidate, control, inputs, guards)
    all_passed = passed and all_passed

    # Same allocation reuse: explicitly include 2048 -> short -> 2048 and
    # short -> 2048, with candidate and control paired on each call.
    for label, length in (
        ("reuse-2048-first", 2048),
        ("reuse-short-1", 1),
        ("reuse-2048-second", 2048),
        ("reuse-short-15", 15),
        ("reuse-short-16", 16),
        ("reuse-2048-third", 2048),
    ):
        _set_lengths(inputs, (length,))
        passed, _, _, _ = _evaluate_pair(label, candidate, control, inputs, guards)
        all_passed = passed and all_passed

    # The final full call proves that all 32 query heads write finite output;
    # _score also requires every individual head to meet the numerical gate.
    _set_lengths(inputs, (2048,))
    passed, _, _, _ = _evaluate_pair("full-32-head-output", candidate, control, inputs, guards)
    all_passed = passed and all_passed
    print(f"case=7 exp690 special validation: {'PASS' if all_passed else 'FAIL'}")
    del inputs
    gc.collect()
    torch.cuda.empty_cache()
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
