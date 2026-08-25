#!/usr/bin/env python3
"""Exp644 case-12 safety gate on a real MetaX C500.

This is a correctness-only companion for the raw-FP32 pair-state/three-peer
fan-in candidate.  It keeps one case-12 allocation alive and checks the
reference, finite output, candidate/control numerical agreement, input and
output guards, raw-BF16 query-head/GQA tags, every 832-token split boundary,
poisoned logical padding, mixed batches, and workspace reuse.  No timing is
performed here.
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
# These are finite BF16 poison values.  They are deliberately unlike the
# tagged payload and must never be observed for an invalid page or token.
SENTINEL_K_BITS = 0x7F7F
SENTINEL_V_BITS = 0xFF7F
SENTINEL_V_I16 = SENTINEL_V_BITS - 0x10000
TAG_DIMS = 8
MIXED_LENGTHS = (1, 15, 16, 17, 831, 832, 833, 32767)
RANDOM_BATCHES = (
    (32768, 16385, 4097, 1025, 833, 257, 17, 1),
    (32767, 24577, 12289, 8193, 4095, 2049, 513, 15),
    (16384, 12288, 8192, 4096, 832, 416, 32, 16),
)


def _exact_241() -> tuple[int, ...]:
    """All short lengths plus boundary +/- 1 and page-tail points.

    Case 12 has 40 logical splits and 832 tokens per split.  The three values
    around every internal split boundary are mandatory; the +15/+16/+17
    points additionally exercise the last page mask around that boundary.
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
        raise AssertionError("exact length outside case12 capacity")
    return result


EXACT_241 = _exact_241()


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected_q = (8, 1, NUM_HEADS, HEAD_DIM)
    expected_cache = (8 * CASE12.max_pages, PAGE_SIZE, 8, HEAD_DIM)
    if inputs.case.case_id != 12:
        raise AssertionError(f"unexpected case {inputs.case}")
    if tuple(inputs.q.shape) != expected_q or tuple(inputs.output.shape) != expected_q:
        raise AssertionError("case12 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case12 K/V shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (8,) or tuple(inputs.block_table.shape) != (8, CASE12.max_pages):
        raise AssertionError("case12 metadata shape mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in lengths)
    if len(values) == 1:
        values = values * CASE12.batch_size
    if len(values) != CASE12.batch_size:
        raise ValueError(f"expected one or eight lengths, got {values}")
    if any(value < 1 or value > CASE12.seqlen_k for value in values):
        raise ValueError(f"length outside case12 capacity: {values}")
    inputs.cache_seqlens.copy_(
        torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    return values


def _install_disjoint_page_table(inputs: PagedDecodeInput) -> None:
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(CASE12.batch_size, CASE12.max_pages)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("invalid page-table entry")


def _copy_raw_bf16(tensor: torch.Tensor, bits: np.ndarray) -> None:
    if bits.dtype != np.uint16 or bits.size != tensor.numel():
        raise AssertionError("raw BF16 payload shape/type mismatch")
    cpu_words = torch.from_numpy(bits.view(np.int16)).view(torch.bfloat16).reshape(tensor.shape)
    tensor.copy_(cpu_words.to(device=tensor.device))
    observed = tensor.detach().to(device="cpu").view(torch.int16).numpy().view(np.uint16)
    if not np.array_equal(observed, bits.reshape(observed.shape)):
        raise AssertionError("raw BF16 payload changed during installation")


def _install_tagged_payload(inputs: PagedDecodeInput) -> tuple[int, int, int]:
    """Install finite raw-BF16 Q plus KV/head/page tags.

    Q has a distinct signature for every query head.  The first eight K/V
    dimensions carry independent page/token/KV-head tags; the remaining
    dimensions retain make_input's finite random payload.  This keeps the
    allocation cheap to construct while making a wrong GQA owner or page
    address visible in the output.
    """

    q_bits = np.empty(inputs.q.numel(), dtype=np.uint16).reshape(8, 32, 128)
    for batch in range(8):
        for head in range(32):
            group = batch * 32 + head
            sign = ((group >> 1) & 1) << 15
            exponent = 124 + (group % 4)
            for dim in range(128):
                q_bits[batch, head, dim] = np.uint16(
                    sign | (exponent << 7) | ((dim + group * 17) & 0x7F)
                )
    _copy_raw_bf16(inputs.q, q_bits)

    device = inputs.k_cache.device
    page = torch.arange(inputs.num_blocks, dtype=torch.int32, device=device).view(-1, 1, 1, 1)
    token = torch.arange(PAGE_SIZE, dtype=torch.int32, device=device).view(1, -1, 1, 1)
    kv_head = torch.arange(8, dtype=torch.int32, device=device).view(1, 1, -1, 1)
    dim = torch.arange(TAG_DIMS, dtype=torch.int32, device=device).view(1, 1, 1, -1)
    group = page * 3 + token * 17 + kv_head * 29 + dim * 7
    k_bits = (((124 + ((page + kv_head) & 3)) << 7) | (group & 0x7F)).to(torch.int16)
    v_group = page * 11 + token * 23 + kv_head * 37 + dim * 13
    v_sign = ((page + token + kv_head) & 1) << 15
    v_bits = (((123 + ((page + kv_head * 2) & 3)) << 7) | v_sign | (v_group & 0x7F)).to(torch.int16)
    inputs.k_cache.view(torch.int16)[..., :TAG_DIMS].copy_(k_bits)
    inputs.v_cache.view(torch.int16)[..., :TAG_DIMS].copy_(v_bits)
    del page, token, kv_head, dim, group, k_bits, v_group, v_sign, v_bits
    for tensor in (inputs.q, inputs.k_cache, inputs.v_cache):
        if not bool(torch.isfinite(tensor).all().item()):
            raise AssertionError("tagged payload contains nonfinite BF16")

    q_head_tags = inputs.q.view(torch.int16)[..., 0].detach().to(device="cpu").numpy()
    k_head_tags = inputs.k_cache[:, 0, :, 0].view(torch.int16).detach().to(device="cpu").numpy()
    v_head_tags = inputs.v_cache[:, 0, :, 0].view(torch.int16).detach().to(device="cpu").numpy()
    q_unique = int(np.unique(q_head_tags).size)
    k_unique = int(np.unique(k_head_tags).size)
    v_unique = int(np.unique(v_head_tags).size)
    if q_unique < 32 or k_unique < 8 or v_unique < 8:
        raise AssertionError(f"collapsed query/GQA tags q={q_unique} k={k_unique} v={v_unique}")
    return q_unique, k_unique, v_unique


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
        raise AssertionError("guarded output is not contiguous")
    return storage, before_head, before_tail


def _guards_ok(storage: torch.Tensor, before_head: torch.Tensor, before_tail: torch.Tensor) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(
        storage[-GUARD_WORDS:], before_tail
    )


def _new_inputs(seed: int):
    inputs = make_input(CASE12, seed=seed, length_mode="full")
    _assert_layout(inputs)
    _install_disjoint_page_table(inputs)
    tags = _install_tagged_payload(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail, tags


def _padding_ids_and_tail_rows(inputs: PagedDecodeInput):
    lengths = [int(value) for value in inputs.cache_seqlens.detach().to(device="cpu").tolist()]
    pages: list[int] = []
    tails: list[tuple[int, int, int]] = []
    for batch, length in enumerate(lengths):
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        table = inputs.block_table[batch].detach().to(device="cpu").tolist()
        pages.extend(int(page) for page in table[valid_pages:])
        remainder = length % PAGE_SIZE
        if remainder:
            tails.extend((int(table[valid_pages - 1]), token, batch) for token in range(remainder, PAGE_SIZE))
    return pages, tails


def _write_padding_poison(inputs: PagedDecodeInput) -> tuple[int, int]:
    pages, tails = _padding_ids_and_tail_rows(inputs)
    if not pages and not tails:
        return 0, 0
    if pages:
        page_ids = torch.tensor(pages, dtype=torch.int64, device=inputs.k_cache.device)
        inputs.k_cache.index_fill_(0, page_ids, torch.tensor(SENTINEL_K_BITS, dtype=torch.int16, device=page_ids.device).view(torch.bfloat16))
        inputs.v_cache.index_fill_(0, page_ids, torch.tensor(SENTINEL_V_I16, dtype=torch.int16, device=page_ids.device).view(torch.bfloat16))
    for page, token, _batch in tails:
        inputs.k_cache[page, token].view(torch.int16).fill_(SENTINEL_K_BITS)
        inputs.v_cache[page, token].view(torch.int16).fill_(SENTINEL_V_I16)
    return len(pages), len(tails)


def _restore_payload(inputs: PagedDecodeInput, base_k: torch.Tensor, base_v: torch.Tensor) -> None:
    inputs.k_cache.copy_(base_k)
    inputs.v_cache.copy_(base_v)


def _evaluate(kernel, inputs, reference, storage, before_head, before_tail):
    q_before = inputs.q.detach().clone()
    k_before = inputs.k_cache.detach().clone()
    v_before = inputs.v_cache.detach().clone()
    lengths_before = inputs.cache_seqlens.detach().clone()
    table_before = inputs.block_table.detach().clone()
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    actual_bf16 = inputs.output.detach().clone()
    actual = actual_bf16.float()
    expected = reference.float()
    diff = (actual - expected).abs()
    tol = ATOL + RTOL * expected.abs()
    finite = bool(torch.isfinite(actual).all().item())
    matched = float((diff <= tol).float().mean().item())
    max_error = float(diff.max().item())
    max_ratio = float((diff / tol).max().item())
    untouched = (
        torch.equal(inputs.q, q_before)
        and torch.equal(inputs.k_cache, k_before)
        and torch.equal(inputs.v_cache, v_before)
        and torch.equal(inputs.cache_seqlens, lengths_before)
        and torch.equal(inputs.block_table, table_before)
    )
    passed = finite and matched >= 1.0 and max_ratio <= 8.0 and untouched and _guards_ok(
        storage, before_head, before_tail
    )
    return passed, actual_bf16, max_error, max_ratio, finite, untouched


def _pair_check(label, candidate, control, inputs, storage, before_head, before_tail):
    reference = flash_reference(inputs)
    candidate_result = _evaluate(candidate, inputs, reference, storage, before_head, before_tail)
    control_result = _evaluate(control, inputs, reference, storage, before_head, before_tail)
    candidate_ok, candidate_out, candidate_error, candidate_ratio, candidate_finite, candidate_untouched = candidate_result
    control_ok, control_out, control_error, control_ratio, control_finite, control_untouched = control_result
    pair_diff = (candidate_out.float() - control_out.float()).abs()
    pair_tol = ATOL + RTOL * reference.float().abs()
    pair_match = bool((pair_diff <= pair_tol).all().item())
    bit_equal = torch.equal(candidate_out, control_out)
    passed = candidate_ok and control_ok and candidate_finite and control_finite and pair_match
    status = "PASS" if passed else "FAIL"
    print(
        f"[{status}] {label} candidate_error={candidate_error:.6e} control_error={control_error:.6e} "
        f"candidate_tol_ratio={candidate_ratio:.3f} control_tol_ratio={control_ratio:.3f} "
        f"pair_match={pair_match} bit_equal={bit_equal} finite={candidate_finite and control_finite} "
        f"inputs_untouched={candidate_untouched and control_untouched} "
        f"guards={_guards_ok(storage, before_head, before_tail)}"
    )
    return passed, reference.detach().clone(), candidate_out, control_out


def _run_exact(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, tags = _new_inputs(seed)
    try:
        print(f"[INFO] exact-241 lengths={len(EXACT_241)} q_head_tags={tags[0]} k_head_tags={tags[1]} v_head_tags={tags[2]}")
        for index, length in enumerate(EXACT_241):
            _set_lengths(inputs, (length,))
            passed, _, _, _ = _pair_check(
                f"case12 exact-{index + 1:03d}/{len(EXACT_241)} length={length}",
                candidate, control, inputs, storage, before_head, before_tail
            )
            if not passed:
                return False
        print("[PASS] case12 exact 1/2/15/16/17 and all 832-token boundaries")
        return True
    finally:
        del inputs
        torch.cuda.empty_cache()


def _run_poison_and_random(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, tags = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    try:
        checks: list[bool] = []
        for label, lengths in (
            ("full batch", (32768,)),
            ("mixed fixed batch", MIXED_LENGTHS),
            *[(f"random mixed batch {index + 1}", values) for index, values in enumerate(RANDOM_BATCHES)],
        ):
            _restore_payload(inputs, base_k, base_v)
            _set_lengths(inputs, lengths)
            baseline_ok, baseline_ref, baseline_candidate, baseline_control = _pair_check(
                f"case12 {label} baseline", candidate, control, inputs, storage, before_head, before_tail
            )
            if label == "full batch":
                print(f"[{'PASS' if baseline_ok else 'FAIL'}] case12 {label} has no logical padding target; baseline only")
                checks.append(baseline_ok)
                continue
            pages, tails = _write_padding_poison(inputs)
            poisoned_ok, poisoned_ref, poisoned_candidate, poisoned_control = _pair_check(
                f"case12 {label} padding-page/token poison pages={pages} tail_rows={tails}",
                candidate, control, inputs, storage, before_head, before_tail
            )
            unchanged = (
                torch.equal(baseline_ref, poisoned_ref)
                and torch.equal(baseline_candidate, poisoned_candidate)
                and torch.equal(baseline_control, poisoned_control)
            )
            print(f"[{'PASS' if unchanged else 'FAIL'}] case12 {label} poison invariance reference/candidate/control={unchanged}")
            checks.append(baseline_ok and poisoned_ok and unchanged)
        print(f"[{'PASS' if all(checks) else 'FAIL'}] case12 full/random mixed-batch poison checks={len(checks)} q_head_tags={tags[0]}")
        return all(checks)
    finally:
        del base_k, base_v, inputs
        torch.cuda.empty_cache()


def _run_reuse(candidate, control, seed: int) -> bool:
    inputs, storage, before_head, before_tail, tags = _new_inputs(seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    try:
        sequences: tuple[tuple[str, tuple[tuple[int, ...], ...]], ...] = (
            ("32768->1->32768", ((32768,), (1,), (32768,))),
            ("1->32768", ((1,), (32768,))),
        )
        all_passed = True
        for sequence_label, sequence in sequences:
            history: dict[int, tuple[torch.Tensor, torch.Tensor]] = {}
            for iteration in range(1, 4):
                for step, lengths in enumerate(sequence, start=1):
                    _restore_payload(inputs, base_k, base_v)
                    _set_lengths(inputs, lengths)
                    _write_padding_poison(inputs)
                    passed, _, candidate_out, control_out = _pair_check(
                        f"case12 workspace {sequence_label} iter={iteration}/3 step={step}/{len(sequence)}",
                        candidate, control, inputs, storage, before_head, before_tail
                    )
                    key = step
                    deterministic = key not in history or (
                        torch.equal(history[key][0], candidate_out)
                        and torch.equal(history[key][1], control_out)
                    )
                    print(f"[{'PASS' if deterministic else 'FAIL'}] case12 workspace {sequence_label} step={step} deterministic={deterministic}")
                    history[key] = (candidate_out.detach().clone(), control_out.detach().clone())
                    all_passed = all_passed and passed and deterministic
            print(f"[{'PASS' if all_passed else 'FAIL'}] case12 workspace sequence {sequence_label}")
        print(f"[{'PASS' if all_passed else 'FAIL'}] case12 workspace reuse 32768->1->32768 and 1->32768 tags={tags[0]}")
        return all_passed
    finally:
        del base_k, base_v, inputs
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
    print(f"reference: flash_attn.flash_attn_with_kvcache | candidate: {args.candidate} | control: {args.control} | seed: {args.seed}")
    if not _run_exact(candidate, control, args.seed + 1200):
        return 1
    if not _run_poison_and_random(candidate, control, args.seed + 1201):
        return 1
    if not _run_reuse(candidate, control, args.seed + 1202):
        return 1
    print("case12 exp644 special correctness: PASS finite=True no_nan=True no_inf=True guards=True")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
