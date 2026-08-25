#!/usr/bin/env python3
"""Raw-word tail-poison probe for the exp710 z4 cases."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import torch

from c500_case_manifest import CASES, PAGE_SIZE
from c500_paged_decode_harness import (
    flash_reference,
    load_kernel,
    make_input,
    require_maca_gpu,
    run_kernel,
)


TARGETS = {case.case_id: case for case in CASES if case.case_id in (8, 10, 11, 14)}
NAN_K = 0x7FC1
NAN_V = -63
FINITE_K = 0x42A0  # BF16 +80.0
FINITE_V = -15776  # 0xC260, BF16 -56.0; finite and unlike random payload


def _raw_equal(a: torch.Tensor, b: torch.Tensor) -> bool:
    if a.dtype == torch.bfloat16:
        return torch.equal(a.detach().contiguous().view(torch.int16),
                           b.detach().contiguous().view(torch.int16))
    return torch.equal(a, b)


def _set_layout(inputs, lengths: tuple[int, ...]):
    case = inputs.case
    if len(lengths) != case.batch_size:
        raise AssertionError(f"case{case.case_id} length count mismatch")
    table = torch.arange(
        inputs.num_blocks, dtype=torch.int32, device=inputs.block_table.device
    ).reshape(case.batch_size, case.max_pages)
    inputs.block_table.copy_(table)
    inputs.cache_seqlens.copy_(
        torch.tensor(lengths, dtype=torch.int32, device=inputs.cache_seqlens.device)
    )
    if not bool(((table >= 0) & (table < inputs.num_blocks)).all().item()):
        raise AssertionError("disjoint table has an invalid page")


def _tail_targets(inputs):
    lengths = inputs.cache_seqlens.detach().to(device="cpu").tolist()
    table = inputs.block_table.detach().to(device="cpu")
    targets: list[tuple[int, int]] = []
    for batch, value in enumerate(lengths):
        length = int(value)
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        remainder = length & (PAGE_SIZE - 1)
        if remainder == 0:
            continue
        row = [int(page) for page in table[batch].tolist()]
        page = row[valid_pages - 1]
        # Every selected token is after cache_seqlens and within that valid
        # physical page; no block-table padding entry is touched.
        targets.extend((page, token) for token in range(remainder, PAGE_SIZE))
        if any(token < remainder or token >= PAGE_SIZE for _page, token in targets):
            raise AssertionError("tail target escaped the invalid suffix")
    return targets


def _poison(inputs, targets, k_word: int, v_word: int) -> None:
    for page, token in targets:
        inputs.k_cache[page, token].view(torch.int16).fill_(k_word)
        inputs.v_cache[page, token].view(torch.int16).fill_(v_word)
    for page, token in targets:
        observed_k = inputs.k_cache[page, token].view(torch.int16)
        observed_v = inputs.v_cache[page, token].view(torch.int16)
        if not bool((observed_k == k_word).all().item()) or not bool(
            (observed_v == v_word).all().item()
        ):
            raise AssertionError("raw tail poison word did not land at selected address")


def _run(kernel, inputs):
    inputs.output.fill_(float("nan"))
    torch.cuda.synchronize()
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    return inputs.output.detach().clone()


def _state(inputs):
    return tuple(
        tensor.detach().clone()
        for tensor in (
            inputs.q, inputs.k_cache, inputs.v_cache,
            inputs.cache_seqlens, inputs.block_table,
        )
    )


def _restore(inputs, state):
    for current, expected in zip(
        (inputs.q, inputs.k_cache, inputs.v_cache,
         inputs.cache_seqlens, inputs.block_table), state
    ):
        current.copy_(expected)


def _check_case(case_id: int, candidate, control, seed: int) -> bool:
    case = TARGETS[case_id]
    length = {8: 321, 10: 321, 11: 17, 14: 17}[case_id]
    lengths = (length,) * case.batch_size
    inputs = make_input(case, seed=seed, length_mode="full")
    try:
        _set_layout(inputs, lengths)
        base = _state(inputs)
        targets = _tail_targets(inputs)
        if not targets:
            raise AssertionError(f"case{case_id} selected no invalid tail tokens")
        valid_pages = (length + PAGE_SIZE - 1) // PAGE_SIZE
        remainder = length & (PAGE_SIZE - 1)
        print(
            f"[INFO] case{case_id} B={case.batch_size} length={length} "
            f"valid_pages={valid_pages} tail_tokens={remainder}..15 "
            f"selected_tail_words={len(targets)} block_table=disjoint"
        )

        # Reference must not observe either poison because all selected words
        # are outside cache_seqlens.  Raw-word comparison avoids NaN equality
        # ambiguity in any future reference path.
        reference_base = flash_reference(inputs).detach().clone()
        candidate_base = _run(candidate, inputs)
        candidate_base_state_ok = all(
            _raw_equal(current, expected)
            for current, expected in zip(
                (inputs.q, inputs.k_cache, inputs.v_cache,
                 inputs.cache_seqlens, inputs.block_table), base
            )
        )
        _restore(inputs, base)
        control_base = _run(control, inputs)
        control_base_state_ok = all(
            _raw_equal(current, expected)
            for current, expected in zip(
                (inputs.q, inputs.k_cache, inputs.v_cache,
                 inputs.cache_seqlens, inputs.block_table), base
            )
        )
        baseline_finite = bool(torch.isfinite(candidate_base).all().item()) and bool(
            torch.isfinite(control_base).all().item()
        )
        print(
            f"[{'PASS' if baseline_finite and candidate_base_state_ok and control_base_state_ok else 'FAIL'}] "
            f"case{case_id} baseline candidate/control finite={baseline_finite} "
            f"inputs_untouched={candidate_base_state_ok and control_base_state_ok}"
        )

        _restore(inputs, base)
        _poison(inputs, targets, NAN_K, NAN_V)
        poisoned = _state(inputs)
        reference_nan = flash_reference(inputs).detach().clone()
        reference_unchanged = _raw_equal(reference_base, reference_nan)
        candidate_nan = _run(candidate, inputs)
        candidate_nan_state_ok = all(
            _raw_equal(current, expected)
            for current, expected in zip(
                (inputs.q, inputs.k_cache, inputs.v_cache,
                 inputs.cache_seqlens, inputs.block_table), poisoned
            )
        )
        _restore(inputs, poisoned)
        control_nan = _run(control, inputs)
        control_nan_state_ok = all(
            _raw_equal(current, expected)
            for current, expected in zip(
                (inputs.q, inputs.k_cache, inputs.v_cache,
                 inputs.cache_seqlens, inputs.block_table), poisoned
            )
        )
        candidate_nan_finite = bool(torch.isfinite(candidate_nan).all().item())
        control_nan_finite = bool(torch.isfinite(control_nan).all().item())
        candidate_control_raw_equal = _raw_equal(candidate_nan, control_nan)
        candidate_nonfinite_words = int(
            (~torch.isfinite(candidate_nan.float())).sum().item()
        )
        control_nonfinite_words = int(
            (~torch.isfinite(control_nan.float())).sum().item()
        )
        print(
            f"[{'PASS' if reference_unchanged else 'FAIL'}] case{case_id} "
            f"NaN poison reference_unchanged_raw_words={reference_unchanged}"
        )
        print(
            f"[{'PASS' if candidate_nan_finite else 'FAIL'}] case{case_id} "
            f"candidate NaN-poison finite={candidate_nan_finite} "
            f"inputs_untouched={candidate_nan_state_ok}"
        )
        print(
            f"[{'PASS' if control_nan_finite else 'FAIL'}] case{case_id} "
            f"control NaN-poison finite={control_nan_finite} "
            f"inputs_untouched={control_nan_state_ok}"
        )
        print(
            f"[INFO] case{case_id} "
            f"NaN tail result candidate_finite={candidate_nan_finite} "
            f"control_finite={control_nan_finite} "
            f"candidate_control_raw_equal={candidate_control_raw_equal} "
            f"nonfinite_words={candidate_nonfinite_words}/{control_nonfinite_words}"
        )

        # A finite raw sentinel distinguishes an actual invalid-tail read from
        # a comparison artifact caused solely by NaN payload handling.
        _restore(inputs, base)
        _poison(inputs, targets, FINITE_K, FINITE_V)
        finite_poisoned = _state(inputs)
        reference_finite_poison = flash_reference(inputs).detach().clone()
        finite_reference_unchanged = _raw_equal(reference_base, reference_finite_poison)
        candidate_finite_poison = _run(candidate, inputs)
        _restore(inputs, finite_poisoned)
        control_finite_poison = _run(control, inputs)
        candidate_finite_unchanged = _raw_equal(candidate_base, candidate_finite_poison)
        control_finite_unchanged = _raw_equal(control_base, control_finite_poison)
        print(
            f"[{'PASS' if finite_reference_unchanged else 'FAIL'}] case{case_id} "
            f"finite-sentinel reference_unchanged_raw_words={finite_reference_unchanged}"
        )
        print(
            f"[INFO] case{case_id} finite-sentinel output_unchanged "
            f"candidate={candidate_finite_unchanged} control={control_finite_unchanged}"
        )
        return (
            baseline_finite
            and candidate_base_state_ok
            and control_base_state_ok
            and reference_unchanged
            and candidate_nan_state_ok
            and control_nan_state_ok
            and finite_reference_unchanged
            and candidate_nan_finite
            and _raw_equal(candidate_base, candidate_nan)
            and candidate_finite_unchanged
        )
    finally:
        del inputs
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260910)
    args = parser.parse_args(argv)
    require_maca_gpu()
    candidate = load_kernel(args.candidate)
    control = load_kernel(args.control)
    print(
        f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__} | "
        f"candidate={args.candidate} | control={args.control} | seed={args.seed}"
    )
    results = [
        _check_case(case_id, candidate, control, args.seed + case_id)
        for case_id in (8, 10, 11, 14)
    ]
    passed = all(results)
    print(f"TAIL_PROBE_RESULT={'PASS' if passed else 'SHARED_CONTROL_TAIL_READ'}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, AssertionError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
