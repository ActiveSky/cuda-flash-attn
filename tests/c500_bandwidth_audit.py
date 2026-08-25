#!/usr/bin/env python3
"""Per-case achieved-bandwidth audit for the paged-KV decode control.

The OJ display score is ``floor(100 * baseline_ms / (baseline_ms + user_ms))``
with a per-case constant ``baseline_ms``.  Deciding where the remaining display
points are therefore needs an absolute roofline view, not another ratio: this
script reports, per case, the exact KV bytes the kernel must stream, the
achieved GB/s, and the fraction of the best case's achieved GB/s.

It also measures a device streaming-read reference so "achieved" can be scored
against something the same GPU demonstrably reaches.

Usage:
    python3 tests/c500_bandwidth_audit.py --library build/ctl_113889.so \
        --lengths full --cases 4-14
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import torch

from c500_case_manifest import CASES, CaseConfig, HEAD_DIM, PAGE_SIZE
from c500_paged_decode_harness import (
    PagedDecodeInput,
    load_kernel,
    make_input,
    parse_case_ids,
    require_maca_gpu,
    run_kernel,
    selected_cases,
)

ROOT = Path(__file__).resolve().parents[1]
BF16_BYTES = 2


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def kv_bytes(inputs: PagedDecodeInput) -> int:
    """Bytes of K plus V that any correct kernel must read for these lengths.

    A page is the smallest loadable unit, so a partially valid tail page still
    costs a full page of traffic in every page-granular loader.
    """
    case = inputs.case
    lengths = inputs.cache_seqlens.to("cpu").tolist()
    pages = sum((length + PAGE_SIZE - 1) // PAGE_SIZE for length in lengths)
    return pages * PAGE_SIZE * case.num_heads_k * HEAD_DIM * BF16_BYTES * 2


def measure(kernel, inputs: PagedDecodeInput, *, warmup: int, iterations: int, rounds: int) -> float:
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


def stream_reference(size_mb: int = 512) -> tuple[float, float]:
    """Read+write and read-only streaming references in GB/s."""
    elements = size_mb * 1024 * 1024 // 2
    source = torch.randn(elements, device="cuda", dtype=torch.bfloat16)
    destination = torch.empty_like(source)
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    for _ in range(5):
        destination.copy_(source)
    torch.cuda.synchronize()
    start.record()
    for _ in range(20):
        destination.copy_(source)
    end.record()
    end.synchronize()
    copy_ms = float(start.elapsed_time(end)) / 20
    copy_gbps = 2 * source.numel() * 2 / (copy_ms * 1e-3) / 1e9

    for _ in range(5):
        source.sum(dtype=torch.float32)
    torch.cuda.synchronize()
    start.record()
    for _ in range(20):
        source.sum(dtype=torch.float32)
    end.record()
    end.synchronize()
    read_ms = float(start.elapsed_time(end)) / 20
    read_gbps = source.numel() * 2 / (read_ms * 1e-3) / 1e9

    del source, destination
    torch.cuda.empty_cache()
    return copy_gbps, read_gbps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "build/ctl_113889.so")
    parser.add_argument("--cases", type=parse_case_ids, default=tuple(range(1, 15)))
    parser.add_argument("--lengths", choices=("full", "random", "boundary"), default="full")
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--rounds", type=int, default=9)
    parser.add_argument("--skip-stream-reference", action="store_true")
    args = parser.parse_args(argv)

    require_maca_gpu()
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    if not args.skip_stream_reference:
        copy_gbps, read_gbps = stream_reference()
        print(f"stream reference: copy(r+w)={copy_gbps:.0f} GB/s  read-only={read_gbps:.0f} GB/s")
    print(f"library: {args.library} | lengths={args.lengths}")

    kernel = load_kernel(args.library)
    rows: list[tuple[CaseConfig, float, int, float]] = []
    for case in selected_cases(args.cases):
        inputs = make_input(case, seed=args.seed + case.case_id, length_mode=args.lengths)
        try:
            elapsed_ms = measure(
                kernel,
                inputs,
                warmup=args.warmup,
                iterations=args.iterations,
                rounds=args.rounds,
            )
            byte_count = kv_bytes(inputs)
            gbps = byte_count / (elapsed_ms * 1e-3) / 1e9
            rows.append((case, elapsed_ms, byte_count, gbps))
        finally:
            del inputs
            torch.cuda.empty_cache()

    best = max(row[3] for row in rows)
    print()
    print("case   B      L KV   local_us   OJ_us   KV_MB   GB/s  %best  OJ_GB/s(scaled)")
    for case, elapsed_ms, byte_count, gbps in rows:
        oj_us = case.user_ms * 1000.0
        # The OJ runs unknown per-sequence lengths; scaling the locally measured
        # GB/s by local/OJ time is only a first-order hint, not a measurement.
        scaled = gbps * (elapsed_ms * 1000.0) / oj_us if oj_us > 0 else float("nan")
        print(
            f"{case.case_id:4d} {case.batch_size:3d} {case.seqlen_k:6d} {case.num_heads_k:2d}"
            f" {elapsed_ms * 1000:10.1f} {oj_us:7.0f} {byte_count / 1e6:7.1f}"
            f" {gbps:6.0f} {gbps / best * 100:5.0f}% {scaled:12.0f}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
