#!/usr/bin/env python3
"""Fixed-vs-marginal cost audit over synthetic paged-decode shapes.

``c500_bandwidth_audit.py`` shows the KV4 long paths (cases 8/10/11/14) reach
only 27-72% of the streaming roofline while the KV8 paths (7/9/12) reach
92-97%.  This script separates the two candidate explanations by sweeping one
dimension at a time on synthetic shapes:

* fixed length, growing batch  -> is the shape parallelism-starved?
* fixed batch, growing length  -> what is the per-CTA fixed cost?

Synthetic shapes miss run_kernel's hardcoded per-case split overrides, so they
measure the generic policy.  Conclusions are about cost structure, never a
substitute for an OJ-shape A/B.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import torch

from c500_case_manifest import CaseConfig, HEAD_DIM, PAGE_SIZE
from c500_paged_decode_harness import (
    load_kernel,
    make_input,
    require_maca_gpu,
    run_kernel,
)

ROOT = Path(__file__).resolve().parents[1]
BF16_BYTES = 2


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def synthetic_case(batch: int, seqlen_k: int, num_heads_k: int) -> CaseConfig:
    return CaseConfig(
        case_id=0,
        batch_size=batch,
        seqlen_k=seqlen_k,
        num_heads_k=num_heads_k,
        kind="perf",
        baseline_ms=0.0,
        user_ms=0.0,
    )


def measure(kernel, inputs, *, warmup: int, iterations: int, rounds: int) -> float:
    for _ in range(warmup):
        run_kernel(kernel, inputs)
    torch.cuda.synchronize()
    samples: list[float] = []
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    for _ in range(rounds):
        start.record()
        for _ in range(iterations):
            run_kernel(kernel, inputs)
        end.record()
        end.synchronize()
        samples.append(float(start.elapsed_time(end)) / iterations)
    return percentile(samples, 0.50)


def sweep(kernel, shapes, *, seed: int, warmup: int, iterations: int, rounds: int) -> None:
    print("   B      L KV   pages  MB     us    GB/s")
    for batch, seqlen_k, num_heads_k in shapes:
        case = synthetic_case(batch, seqlen_k, num_heads_k)
        inputs = make_input(case, seed=seed, length_mode="full")
        try:
            elapsed = measure(
                kernel, inputs, warmup=warmup, iterations=iterations, rounds=rounds
            )
        finally:
            del inputs
            torch.cuda.empty_cache()
        pages = batch * ((seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE)
        byte_count = pages * PAGE_SIZE * num_heads_k * HEAD_DIM * BF16_BYTES * 2
        print(
            f"{batch:4d} {seqlen_k:6d} {num_heads_k:2d} {pages:7d}"
            f" {byte_count / 1e6:7.1f} {elapsed * 1000:7.1f}"
            f" {byte_count / (elapsed * 1e-3) / 1e9:7.0f}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "build/ctl_113889.so")
    parser.add_argument("--seed", type=int, default=20260817)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--rounds", type=int, default=7)
    args = parser.parse_args(argv)

    require_maca_gpu()
    kernel = load_kernel(args.library)
    print(f"library: {args.library}")

    print("\n== KV4, batch=1, growing length ==")
    sweep(
        kernel,
        [(1, length, 4) for length in (2048, 4096, 8192, 16384, 32768, 61519)],
        seed=args.seed,
        warmup=args.warmup,
        iterations=args.iterations,
        rounds=args.rounds,
    )

    print("\n== KV4, length=8192, growing batch ==")
    sweep(
        kernel,
        [(batch, 8192, 4) for batch in (1, 2, 4, 8, 16)],
        seed=args.seed,
        warmup=args.warmup,
        iterations=args.iterations,
        rounds=args.rounds,
    )

    print("\n== KV8, batch=1, growing length (reference family) ==")
    sweep(
        kernel,
        [(1, length, 8) for length in (2048, 8192, 32768, 58966)],
        seed=args.seed,
        warmup=args.warmup,
        iterations=args.iterations,
        rounds=args.rounds,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
