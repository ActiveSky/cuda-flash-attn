#!/usr/bin/env python3
"""Interleaved local C500 A/B benchmark for paged-KV decode candidates.

Each round measures a control and candidate back-to-back on identical tensors,
alternating their order to avoid a one-sided clock/power bias.  It reports the
per-round candidate/control ratio distribution; conclusions should use the
ratio rather than separately collected absolute timings.

Examples:
    python tests/c500_benchmark.py --control build/cuda_maca_version.so \\
        --candidate build/cuda_maca_optimized.so --cases 7,9,12,13
"""

from __future__ import annotations

import argparse
import ctypes
from pathlib import Path
import sys

import torch

from c500_case_manifest import CASES, CaseConfig
from c500_paged_decode_harness import (
    DEFAULT_LIBRARY,
    PagedDecodeInput,
    check_correctness,
    load_kernel,
    make_input,
    parse_case_ids,
    require_maca_gpu,
    run_kernel,
    selected_cases,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE = ROOT / "build/cuda_maca_optimized.so"


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("cannot compute percentile of empty values")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def measure_block(
    kernel: ctypes._CFuncPtr,
    inputs: PagedDecodeInput,
    *,
    iterations: int,
) -> float:
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    for _ in range(iterations):
        run_kernel(kernel, inputs)
    end.record()
    end.synchronize()
    return float(start.elapsed_time(end)) / iterations


def warmup(kernel: ctypes._CFuncPtr, inputs: PagedDecodeInput, count: int) -> None:
    for _ in range(count):
        run_kernel(kernel, inputs)
    torch.cuda.synchronize()


def benchmark_case(
    control: ctypes._CFuncPtr,
    candidate: ctypes._CFuncPtr,
    inputs: PagedDecodeInput,
    *,
    warmup_count: int,
    iterations: int,
    rounds: int,
) -> tuple[list[float], list[float], list[float]]:
    warmup(control, inputs, warmup_count)
    warmup(candidate, inputs, warmup_count)

    control_ms: list[float] = []
    candidate_ms: list[float] = []
    ratios: list[float] = []
    for round_index in range(rounds):
        # Alternating order prevents the second measurement of every round from
        # systematically receiving warmer clocks or a different power state.
        if round_index % 2 == 0:
            control_time = measure_block(control, inputs, iterations=iterations)
            candidate_time = measure_block(candidate, inputs, iterations=iterations)
        else:
            candidate_time = measure_block(candidate, inputs, iterations=iterations)
            control_time = measure_block(control, inputs, iterations=iterations)
        control_ms.append(control_time)
        candidate_ms.append(candidate_time)
        ratios.append(candidate_time / control_time)
    return control_ms, candidate_ms, ratios


def check_library(
    label: str,
    kernel: ctypes._CFuncPtr,
    inputs: PagedDecodeInput,
) -> None:
    result = check_correctness(kernel, inputs)
    if not result.passed:
        raise RuntimeError(
            f"{label} fails correctness on case {result.case_id}: "
            f"matched={result.matched_ratio:.6f}, max-tolerance-ratio={result.max_outlier_ratio:.3f}"
        )


def print_result(
    case: CaseConfig,
    control_ms: list[float],
    candidate_ms: list[float],
    ratios: list[float],
) -> None:
    ratio_p10 = percentile(ratios, 0.10)
    ratio_p50 = percentile(ratios, 0.50)
    ratio_p90 = percentile(ratios, 0.90)
    speedup = 1.0 / ratio_p50
    print(
        f"case {case.case_id:2d} B={case.batch_size:2d} L={case.seqlen_k:5d} KV={case.num_heads_k} | "
        f"control p50={percentile(control_ms, 0.50):.4f} ms | "
        f"candidate p50={percentile(candidate_ms, 0.50):.4f} ms | "
        f"candidate/control p10/p50/p90={ratio_p10:.4f}/{ratio_p50:.4f}/{ratio_p90:.4f} | "
        f"speedup={speedup:.3f}x"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--cases", type=parse_case_ids, default=(7, 9, 12, 13))
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument(
        "--lengths", choices=("full", "random", "boundary"), default="full",
        help="cache_seqlens distribution used for both control and candidate",
    )
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--rounds", type=int, default=15)
    args = parser.parse_args(argv)
    if min(args.warmup, args.iterations, args.rounds) < 1:
        parser.error("warmup, iterations and rounds must all be positive")

    require_maca_gpu()
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    print(f"control:   {args.control}")
    print(f"candidate: {args.candidate}")
    control = load_kernel(args.control)
    candidate = load_kernel(args.candidate)

    for case in selected_cases(args.cases):
        inputs = make_input(case, seed=args.seed + case.case_id, length_mode=args.lengths)
        try:
            check_library("control", control, inputs)
            check_library("candidate", candidate, inputs)
            control_ms, candidate_ms, ratios = benchmark_case(
                control,
                candidate,
                inputs,
                warmup_count=args.warmup,
                iterations=args.iterations,
                rounds=args.rounds,
            )
            print_result(case, control_ms, candidate_ms, ratios)
        finally:
            del inputs
            torch.cuda.empty_cache()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
