#!/usr/bin/env python3
"""Validate and time a two-wave shared mbarrier against CTA barriers."""

from __future__ import annotations

import argparse
import ctypes
import math
import statistics
import time

import numpy as np
import torch


def expected_output(blocks: int, iterations: int) -> np.ndarray:
    tid = np.arange(256, dtype=np.uint64)
    lane = tid & 63
    wave = tid >> 6
    peer = ((wave ^ 1) << 6) | lane
    triangular = iterations * (iterations + 1) // 2
    values = (257 * triangular + iterations * peer) & 0xFFFFFFFF
    return np.tile(values.astype(np.uint32), blocks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--blocks", type=int, default=256)
    parser.add_argument("--iterations", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--rounds", type=int, default=15)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")
    if args.blocks <= 0 or args.iterations <= 0:
        raise ValueError("blocks and iterations must be positive")

    library = ctypes.CDLL(args.library)
    launch = library.run_zgroup_barrier_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    launch.restype = None
    output = torch.empty(
        args.blocks * 256, dtype=torch.uint32, device="cuda"
    )

    def run(use_zgroup: bool) -> None:
        launch(
            ctypes.c_void_p(output.data_ptr()),
            args.blocks,
            args.iterations,
            int(use_zgroup),
        )

    reference = expected_output(args.blocks, args.iterations)
    for label, use_zgroup in (("cta", False), ("zgroup", True)):
        output.fill_(0xFFFFFFFF)
        run(use_zgroup)
        torch.cuda.synchronize()
        got = output.cpu().numpy()
        if not np.array_equal(got, reference):
            bad = np.flatnonzero(got != reference)
            first = int(bad[0])
            raise RuntimeError(
                f"{label} mismatch: count={bad.size}, first={first}, "
                f"got={int(got[first])}, expected={int(reference[first])}"
            )
        print(f"[PASS] {label}: exact shared peer exchange")

    for _ in range(args.warmup):
        run(False)
        run(True)
    torch.cuda.synchronize()

    ratios: list[float] = []
    cta_ms: list[float] = []
    zgroup_ms: list[float] = []
    for round_idx in range(args.rounds):
        order = (False, True) if round_idx % 2 == 0 else (True, False)
        elapsed: dict[bool, float] = {}
        for use_zgroup in order:
            start = time.perf_counter_ns()
            run(use_zgroup)
            torch.cuda.synchronize()
            elapsed[use_zgroup] = (time.perf_counter_ns() - start) / 1.0e6
        cta_ms.append(elapsed[False])
        zgroup_ms.append(elapsed[True])
        ratios.append(elapsed[True] / elapsed[False])

    ratios.sort()
    q = lambda p: ratios[round((len(ratios) - 1) * p)]
    print(
        f"CTA median={statistics.median(cta_ms):.4f} ms, "
        f"zgroup median={statistics.median(zgroup_ms):.4f} ms"
    )
    print(
        "zgroup/cta ratio "
        f"p10/p50/p90={q(0.1):.4f}/{q(0.5):.4f}/{q(0.9):.4f}"
    )
    if not math.isfinite(q(0.5)):
        raise RuntimeError("non-finite timing ratio")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
