#!/usr/bin/env python3
"""Validate the lane-local BF16-MMA P*V mapping proposed for exp423."""

from __future__ import annotations

import argparse
import ctypes

import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_bf16_mma_pv_probe
    launch.argtypes = [ctypes.c_void_p] * 3
    launch.restype = None

    generator = torch.Generator(device="cuda")
    samples = 0
    worst_max_error = 0.0
    worst_mean_error = 0.0
    for scale in (0.125, 1.0, 4.0):
        for seed in (20260814, 11, 101, 1009):
            generator.manual_seed(seed)
            probability = torch.rand(
                (8, 4), generator=generator, device="cuda", dtype=torch.float32
            ).to(torch.bfloat16)
            value = (
                torch.randn((4, 128), generator=generator, device="cuda") * scale
            ).to(torch.bfloat16)
            actual = torch.full(
                (8, 128), float("nan"), dtype=torch.float32, device="cuda"
            )
            launch(
                ctypes.c_void_p(probability.data_ptr()),
                ctypes.c_void_p(value.data_ptr()),
                ctypes.c_void_p(actual.data_ptr()),
            )
            torch.cuda.synchronize()

            reference = probability.cpu().float() @ value.cpu().float()
            actual_cpu = actual.cpu()
            if not bool(torch.isfinite(actual_cpu).all()):
                raise RuntimeError("BF16 MMA P*V produced NaN/Inf")
            error = (actual_cpu - reference).abs()
            max_error = float(error.max())
            mean_error = float(error.mean())
            worst_max_error = max(worst_max_error, max_error)
            worst_mean_error = max(worst_mean_error, mean_error)
            samples += 1
            print(
                f"scale={scale:g} seed={seed} "
                f"max_error={max_error:.6e} mean_error={mean_error:.6e}"
            )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"samples={samples} worst_max_error={worst_max_error:.6e} "
        f"worst_mean_error={worst_mean_error:.6e}"
    )
    if worst_max_error > 2.0e-3:
        raise RuntimeError("lane mapping or BF16 MMA precision is outside probe bound")
    print("[PASS] lane-local head-pair/z4 BF16-MMA P*V mapping is correct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
