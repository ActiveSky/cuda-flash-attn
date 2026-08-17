#!/usr/bin/env python3
"""Validate the lane-local BF16-MMA mapping for head-pair/z4 QK."""

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
    launch = library.run_bf16_mma_qk_resource_probe
    launch.argtypes = [ctypes.c_void_p] * 3
    launch.restype = None

    generator = torch.Generator(device="cuda")
    samples = 0
    worst_max_error = 0.0
    worst_mean_error = 0.0
    worst_inert_slot_absmax = 0.0
    for scale in (0.125, 1.0, 4.0):
        for seed in (20260813, 7, 97, 997):
            generator.manual_seed(seed)
            q = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            k = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            actual = torch.full(
                (4, 4, 16, 4), float("nan"), dtype=torch.float32, device="cuda"
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
            reference = torch.zeros_like(actual_cpu)
            for z in range(4):
                for ty in range(4):
                    for tx in range(16):
                        token = z * 4 + (tx & 3)
                        reference[z, ty, tx, 0] = torch.dot(q_cpu[ty], k_cpu[token])
                        reference[z, ty, tx, 1] = torch.dot(
                            q_cpu[ty + 4], k_cpu[token]
                        )

            if not bool(torch.isfinite(actual_cpu).all()):
                raise RuntimeError("BF16 MMA QK produced NaN/Inf")
            error = (actual_cpu - reference).abs()
            max_error = float(error.max())
            mean_error = float(error.mean())
            worst_max_error = max(worst_max_error, max_error)
            worst_mean_error = max(worst_mean_error, mean_error)
            inert_slot_absmax = float(actual_cpu[..., 2:].abs().max())
            worst_inert_slot_absmax = max(worst_inert_slot_absmax, inert_slot_absmax)
            samples += 1
            print(
                f"scale={scale:g} seed={seed} "
                f"max_error={max_error:.6e} mean_error={mean_error:.6e} "
                f"c23_absmax={inert_slot_absmax:.6e}"
            )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"samples={samples} worst_max_error={worst_max_error:.6e} "
        f"worst_mean_error={worst_mean_error:.6e} "
        f"worst_c23_absmax={worst_inert_slot_absmax:.6e}"
    )
    if worst_max_error > 2.0e-3:
        raise RuntimeError("lane mapping or BF16 MMA precision is outside probe bound")
    if worst_inert_slot_absmax != 0.0:
        raise RuntimeError("C500 c[2]/c[3] stopped being inert; remap before use")
    print("[PASS] c[0]/c[1] map correctly; populated c[2]/c[3] remain inert on C500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
