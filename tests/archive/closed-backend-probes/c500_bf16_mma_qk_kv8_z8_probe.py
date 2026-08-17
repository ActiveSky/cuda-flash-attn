#!/usr/bin/env python3
"""Validate the long-KV8 head-pair/z8 lane-local BF16-MMA mapping."""

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
    launch = library.run_bf16_mma_qk_kv8_z8_probe
    launch.argtypes = [ctypes.c_void_p] * 3
    launch.restype = None

    generator = torch.Generator(device="cuda")
    samples = 0
    worst_max_error = 0.0
    worst_mean_error = 0.0
    for scale in (0.125, 1.0, 4.0):
        for seed in (20260813, 7, 97, 997):
            generator.manual_seed(seed)
            q = (torch.randn((4, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            k = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            actual = torch.full(
                (8, 2, 16, 2), float("nan"), dtype=torch.float32, device="cuda"
            )
            launch(
                ctypes.c_void_p(q.data_ptr()),
                ctypes.c_void_p(k.data_ptr()),
                ctypes.c_void_p(actual.data_ptr()),
            )
            torch.cuda.synchronize()

            q_cpu = q.cpu().float()
            k_cpu = k.cpu().float()
            actual_cpu = actual.cpu()
            reference = torch.empty_like(actual_cpu)
            for z in range(8):
                for ty in range(2):
                    for tx in range(16):
                        token = (z // 2) * 4 + (tx & 3)
                        reference[z, ty, tx, 0] = torch.dot(q_cpu[ty], k_cpu[token])
                        reference[z, ty, tx, 1] = torch.dot(
                            q_cpu[ty + 2], k_cpu[token]
                        )

            if not bool(torch.isfinite(actual_cpu).all()):
                raise RuntimeError("BF16 MMA QK produced NaN/Inf")
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
        raise RuntimeError("KV8 z8 lane mapping or BF16 MMA precision is outside bound")
    print("[PASS] lane-local head-pair/z8 BF16-MMA QK mapping is correct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
