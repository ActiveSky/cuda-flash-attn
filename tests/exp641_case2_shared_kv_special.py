#!/usr/bin/env python3
"""Exp641 case-2 shared-KV ownership and reuse checks on a real C500.

Case 2 is the only ``B=4, KV=8, seqlen_k_cap=2`` dispatch.  The candidate
loads token zero into CTA shared memory and conditionally loads token one, so
this companion test makes the token-one tail visibly poisonous for short
rows.  It also gives every batch/KV/query head a distinct raw BF16 pattern,
which makes GQA and page ownership mistakes observable.
"""

from __future__ import annotations

import argparse
from pathlib import Path
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


CASE2 = next(case for case in CASES if case.case_id == 2)
GUARD_WORDS = 32
GUARD_VALUE = -777.0
SENTINEL_K_BITS = 0x7F7F
SENTINEL_V_BITS = 0xFF7F
SENTINEL_V_I16 = SENTINEL_V_BITS - 0x10000
REPETITIONS = 100


def _assert_layout(inputs: PagedDecodeInput) -> None:
    expected = (4, 1, NUM_HEADS, HEAD_DIM)
    # Deliberately provide two physical pages per batch row.  Case 2 only
    # needs the first page, so the second block-table entry is an explicit
    # unreadable-PID trap rather than an omitted allocation.
    expected_cache = (8, PAGE_SIZE, 8, HEAD_DIM)
    if inputs.case.case_id != 2:
        raise AssertionError(f"unexpected case: {inputs.case}")
    if tuple(inputs.q.shape) != expected or tuple(inputs.output.shape) != expected:
        raise AssertionError("case2 Q/output shape mismatch")
    if tuple(inputs.k_cache.shape) != expected_cache or tuple(inputs.v_cache.shape) != expected_cache:
        raise AssertionError("case2 K/V shape mismatch")
    if tuple(inputs.cache_seqlens.shape) != (4,) or tuple(inputs.block_table.shape) != (4, 2):
        raise AssertionError("case2 metadata shape mismatch")


def _set_lengths(inputs: PagedDecodeInput, lengths: Iterable[int]) -> tuple[int, ...]:
    values = tuple(int(value) for value in lengths)
    if len(values) == 1:
        values = values * CASE2.batch_size
    if len(values) != CASE2.batch_size or any(value not in (1, 2) for value in values):
        raise ValueError(f"case2 lengths must contain four values in {{1,2}}, got {values}")
    inputs.cache_seqlens.copy_(torch.tensor(values, dtype=torch.int32, device=inputs.cache_seqlens.device))
    return values


def _install_page_table(inputs: PagedDecodeInput) -> None:
    if inputs.num_blocks != CASE2.batch_size * 2:
        raise AssertionError(f"special case2 requires 2 pages per batch, got {inputs.num_blocks}")
    table = torch.arange(inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device).reshape(4, 2)
    inputs.block_table.copy_(table)
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("invalid physical page in case2 table")


def _copy_raw_bf16(tensor: torch.Tensor, bits: np.ndarray) -> None:
    if bits.dtype != np.uint16 or bits.size != tensor.numel():
        raise AssertionError("raw BF16 payload shape/type mismatch")
    cpu_words = torch.from_numpy(bits.view(np.int16)).view(torch.bfloat16).reshape(tensor.shape)
    tensor.copy_(cpu_words.to(device=tensor.device))
    observed = tensor.detach().to(device="cpu").view(torch.int16).numpy().view(np.uint16)
    if not np.array_equal(observed, bits.reshape(observed.shape)):
        raise AssertionError("raw BF16 payload changed during installation")


def _install_distinct_payload(inputs: PagedDecodeInput) -> tuple[int, int, int]:
    """Install finite, nonuniform raw words with independent B/KV/head fields."""

    q_bits = np.empty(inputs.q.numel(), dtype=np.uint16)
    q_view = q_bits.reshape(4, 32, 128)
    for batch in range(4):
        for head in range(32):
            group = batch * 32 + head
            exponent = 124 + ((group * 3) % 4)
            sign = (group & 1) << 15
            for dim in range(128):
                q_view[batch, head, dim] = np.uint16(sign | (exponent << 7) | ((group * 17 + dim) & 0x7F))

    k_bits = np.empty(inputs.k_cache.numel(), dtype=np.uint16)
    v_bits = np.empty(inputs.v_cache.numel(), dtype=np.uint16)
    k_view = k_bits.reshape(inputs.num_blocks, 16, 8, 128)
    v_view = v_bits.reshape(inputs.num_blocks, 16, 8, 128)
    for page in range(inputs.num_blocks):
        # Pages 2*b and 2*b+1 belong to batch b in _install_page_table.  The
        # first page carries the legal token rows; the second page is the PID
        # trap.  Keeping page in the tag also catches accidental cross-page
        # ownership even before the trap is installed.
        batch = page // 2
        for token in range(2):
            for kv_head in range(8):
                group = batch * 8 + kv_head
                k_exp = 124 + ((group + token) % 4)
                v_exp = 123 + ((group * 2 + token) % 5)
                k_sign = ((group + token) & 1) << 15
                v_sign = ((group * 3 + token) & 1) << 15
                for dim in range(128):
                    k_view[page, token, kv_head, dim] = np.uint16(
                        k_sign | (k_exp << 7) | ((group * 29 + token * 43 + page * 11 + dim) & 0x7F)
                    )
                    v_view[page, token, kv_head, dim] = np.uint16(
                        v_sign | (v_exp << 7) | ((group * 31 + token * 47 + page * 13 + dim) & 0x7F)
                    )

    _copy_raw_bf16(inputs.q, q_bits)
    _copy_raw_bf16(inputs.k_cache, k_bits)
    _copy_raw_bf16(inputs.v_cache, v_bits)
    for tensor in (inputs.q, inputs.k_cache, inputs.v_cache):
        if not bool(torch.isfinite(tensor).all().item()):
            raise AssertionError("distinct payload contains nonfinite BF16")

    q_groups = int(torch.unique(inputs.q.view(torch.int16)[..., 0]).numel())
    k_groups = int(torch.unique(inputs.k_cache[:, 0, :, 0].view(torch.int16)).numel())
    v_groups = int(torch.unique(inputs.v_cache[:, 0, :, 0].view(torch.int16)).numel())
    if q_groups < 32 or k_groups < 8 or v_groups < 8:
        raise AssertionError(f"payload group fields collapsed: q={q_groups} k={k_groups} v={v_groups}")
    return q_groups, k_groups, v_groups


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
        raise AssertionError("guarded output view is not contiguous")
    return storage, before_head, before_tail


def _guards_ok(storage: torch.Tensor, before_head: torch.Tensor, before_tail: torch.Tensor) -> bool:
    return torch.equal(storage[:GUARD_WORDS], before_head) and torch.equal(storage[-GUARD_WORDS:], before_tail)


def _new_inputs(seed: int) -> tuple[PagedDecodeInput, torch.Tensor, torch.Tensor, torch.Tensor, tuple[int, int, int]]:
    inputs = make_input(CASE2, seed=seed, length_mode="full")
    # make_input follows the manifest's one-page capacity.  Replace only the
    # K/V and table storage here so run_kernel receives pages_per_batch=2 while
    # retaining the exact case-2 ABI and query shape.
    device = inputs.q.device
    inputs.k_cache = torch.empty(
        (CASE2.batch_size * 2, PAGE_SIZE, CASE2.num_heads_k, HEAD_DIM),
        dtype=torch.bfloat16,
        device=device,
    ).contiguous()
    inputs.v_cache = torch.empty_like(inputs.k_cache).contiguous()
    inputs.block_table = torch.empty(
        (CASE2.batch_size, 2), dtype=torch.int32, device=device
    ).contiguous()
    _assert_layout(inputs)
    _install_page_table(inputs)
    payload_groups = _install_distinct_payload(inputs)
    storage, before_head, before_tail = _install_output_guard(inputs)
    return inputs, storage, before_head, before_tail, payload_groups


def _set_token1_sentinel(inputs: PagedDecodeInput) -> None:
    # Token 1 is a valid physical address but an invalid logical token only for
    # rows whose real cache_seqlens is one.  Token 2..15 are padding for every
    # case-2 length and are poisoned unconditionally.  The second physical PID
    # is also poisoned, exercising both logical and block-table read bounds.
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    for batch, length in enumerate(lengths):
        page = int(inputs.block_table[batch, 0].item())
        k_tail = inputs.k_cache[page, 1, :, :].view(torch.int16)
        v_tail = inputs.v_cache[page, 1, :, :].view(torch.int16)
        if int(length) == 1:
            k_tail.fill_(SENTINEL_K_BITS)
            v_tail.fill_(SENTINEL_V_I16)

        k_padding = inputs.k_cache[page, 2:PAGE_SIZE, :, :].view(torch.int16)
        v_padding = inputs.v_cache[page, 2:PAGE_SIZE, :, :].view(torch.int16)
        k_padding.fill_(SENTINEL_K_BITS)
        v_padding.fill_(SENTINEL_V_I16)

        second_page = int(inputs.block_table[batch, 1].item())
        k_second = inputs.k_cache[second_page].view(torch.int16)
        v_second = inputs.v_cache[second_page].view(torch.int16)
        k_second.fill_(SENTINEL_K_BITS)
        v_second.fill_(SENTINEL_V_I16)
        if int(length) == 1 and not bool((k_tail == SENTINEL_K_BITS).all().item()):
            raise AssertionError(f"token-one K poison installation failed for batch={batch}")
        if int(length) == 1 and not bool((v_tail == SENTINEL_V_I16).all().item()):
            raise AssertionError(f"token-one V poison installation failed for batch={batch}")
        if not bool((k_padding == SENTINEL_K_BITS).all().item()) or not bool(
            (v_padding == SENTINEL_V_I16).all().item()
        ):
            raise AssertionError(f"token-2..15 poison installation failed for batch={batch}")
        if not bool((k_second == SENTINEL_K_BITS).all().item()) or not bool(
            (v_second == SENTINEL_V_I16).all().item()
        ):
            raise AssertionError(f"second-PID poison installation failed for batch={batch}")


def _restore_payload(inputs: PagedDecodeInput, base_k: torch.Tensor, base_v: torch.Tensor) -> None:
    inputs.k_cache.copy_(base_k)
    inputs.v_cache.copy_(base_v)


def _evaluate(
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
) -> tuple[bool, torch.Tensor, float, float, bool]:
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
    difference = (actual - expected).abs()
    tolerance = ATOL + RTOL * expected.abs()
    finite = bool(torch.isfinite(actual).all().item())
    matched = float((difference <= tolerance).float().mean().item())
    max_error = float(difference.max().item())
    max_ratio = float((difference / tolerance).max().item())
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
    return passed, actual_bf16, max_error, max_ratio, untouched


def _run_pair(
    label: str,
    candidate,
    control,
    inputs: PagedDecodeInput,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
    reuse_key: str | None = None,
    previous_outputs: dict[str, tuple[torch.Tensor, torch.Tensor]] | None = None,
    verbose: bool = True,
) -> bool:
    reference = flash_reference(inputs)
    candidate_ok, candidate_out, candidate_error, candidate_ratio, candidate_untouched = _evaluate(
        candidate, inputs, reference, storage, before_head, before_tail
    )
    control_ok, control_out, control_error, control_ratio, control_untouched = _evaluate(
        control, inputs, reference, storage, before_head, before_tail
    )
    bit_equal = torch.equal(candidate_out, control_out)
    deterministic = True
    if reuse_key is not None and previous_outputs is not None:
        previous = previous_outputs.get(reuse_key)
        if previous is not None:
            deterministic = torch.equal(previous[0], candidate_out) and torch.equal(
                previous[1], control_out
            )
        previous_outputs[reuse_key] = (candidate_out.detach().clone(), control_out.detach().clone())
    passed = candidate_ok and control_ok and bit_equal and deterministic
    status = "PASS" if passed else "FAIL"
    if verbose:
        print(
            f"[{status}] {label} candidate_error={candidate_error:.6e} control_error={control_error:.6e} "
            f"candidate_tol_ratio={candidate_ratio:.3f} control_tol_ratio={control_ratio:.3f} "
            f"bit_equal={bit_equal} deterministic={deterministic} "
            f"candidate_untouched={candidate_untouched} control_untouched={control_untouched} "
            f"guards={_guards_ok(storage, before_head, before_tail)}"
        )
    return passed


def _repeat_determinism(
    label: str,
    kernel,
    inputs: PagedDecodeInput,
    reference: torch.Tensor,
    repetitions: int,
    ) -> bool:
    first: torch.Tensor | None = None
    mismatch = 0
    max_ratio = 0.0
    for _ in range(repetitions):
        inputs.output.fill_(float("nan"))
        torch.cuda.synchronize()
        run_kernel(kernel, inputs)
        torch.cuda.synchronize()
        current = inputs.output.detach().clone()
        if not bool(torch.isfinite(current).all().item()):
            print(f"[FAIL] {label} nonfinite output")
            return False
        difference = (current.float() - reference.float()).abs()
        tolerance = ATOL + RTOL * reference.float().abs()
        max_ratio = max(max_ratio, float((difference / tolerance).max().item()))
        if first is None:
            first = current
        elif not torch.equal(first, current):
            mismatch += 1
    passed = mismatch == 0 and max_ratio <= 8.0
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label} repetitions={repetitions} mismatches={mismatch} max_tol_ratio={max_ratio:.3f}")
    return passed


def _run_reuse_sequences(
    candidate,
    control,
    inputs: PagedDecodeInput,
    storage: torch.Tensor,
    before_head: torch.Tensor,
    before_tail: torch.Tensor,
    base_k: torch.Tensor,
    base_v: torch.Tensor,
) -> bool:
    sequences: tuple[tuple[str, tuple[tuple[int, ...], ...]], ...] = (
        ("full->short->full", ((2, 2, 2, 2), (1, 1, 1, 1), (2, 2, 2, 2))),
        ("short->full", ((1, 1, 1, 1), (2, 2, 2, 2))),
    )
    for sequence_label, sequence in sequences:
        previous_outputs: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}
        for iteration in range(1, REPETITIONS + 1):
            for step, lengths in enumerate(sequence, start=1):
                _restore_payload(inputs, base_k, base_v)
                _set_lengths(inputs, lengths)
                _set_token1_sentinel(inputs)
                key = f"{sequence_label}:step={step}"
                if not _run_pair(
                    f"workspace reuse {sequence_label} iter={iteration}/{REPETITIONS} "
                    f"step={step}/{len(sequence)} lengths={lengths}",
                    candidate,
                    control,
                    inputs,
                    storage,
                    before_head,
                    before_tail,
                    reuse_key=key,
                    previous_outputs=previous_outputs,
                    verbose=iteration in (1, REPETITIONS),
                ):
                    return False
        print(f"[PASS] workspace reuse {sequence_label} deterministic checks={REPETITIONS}")
    print("[PASS] workspace reuse full->short->full and short->full")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args(argv)

    require_maca_gpu()
    if (CASE2.batch_size, CASE2.seqlen_k, CASE2.num_heads_k) != (4, 2, 8):
        raise RuntimeError(f"unexpected case2 manifest: {CASE2}")
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    inputs, storage, before_head, before_tail, payload_groups = _new_inputs(args.seed)
    base_k = inputs.k_cache.detach().clone()
    base_v = inputs.v_cache.detach().clone()
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    print(f"candidate: {args.candidate} | control: {args.control} | seed: {args.seed}")
    print(f"[INFO] distinct raw BF16 groups q={payload_groups[0]} k={payload_groups[1]} v={payload_groups[2]} GQA=4")
    try:
        checks: list[bool] = []
        _restore_payload(inputs, base_k, base_v)
        _set_lengths(inputs, (1, 1, 1, 1))
        _set_token1_sentinel(inputs)
        checks.append(_run_pair("all-one token1 poison/tail padding trap", candidate, control, inputs, storage, before_head, before_tail))

        _restore_payload(inputs, base_k, base_v)
        _set_lengths(inputs, (2, 2, 2, 2))
        _set_token1_sentinel(inputs)
        checks.append(_run_pair("all-two full token range", candidate, control, inputs, storage, before_head, before_tail))

        _restore_payload(inputs, base_k, base_v)
        _set_lengths(inputs, (1, 2, 1, 2))
        _set_token1_sentinel(inputs)
        checks.append(_run_pair("mixed [1,2,1,2] GQA/page ownership", candidate, control, inputs, storage, before_head, before_tail))

        _restore_payload(inputs, base_k, base_v)
        _set_lengths(inputs, (2, 1, 2, 1))
        _set_token1_sentinel(inputs)
        checks.append(_run_pair("reverse [2,1,2,1] GQA/page ownership", candidate, control, inputs, storage, before_head, before_tail))

        if not _run_reuse_sequences(candidate, control, inputs, storage, before_head, before_tail, base_k, base_v):
            checks.append(False)
        else:
            checks.append(True)

        for label, lengths, poison in (
            ("determinism all-one", (1, 1, 1, 1), True),
            ("determinism all-two", (2, 2, 2, 2), False),
        ):
            _restore_payload(inputs, base_k, base_v)
            _set_lengths(inputs, lengths)
            if poison:
                _set_token1_sentinel(inputs)
            reference = flash_reference(inputs)
            checks.append(_repeat_determinism(label + " candidate", candidate, inputs, reference, REPETITIONS))
            checks.append(_repeat_determinism(label + " control", control, inputs, reference, REPETITIONS))

        passed = all(checks)
        print(f"case2 exp641 special correctness: {'PASS' if passed else 'FAIL'} checks={len(checks)}")
        return 0 if passed else 1
    finally:
        del inputs
        torch.cuda.empty_cache()


if __name__ == "__main__":
    raise SystemExit(main())
