#!/usr/bin/env python3
"""Compare FP16-input and BF16-input native MMA precision on a real C500."""

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
    launch = library.run_mma_f16_bf16_k128_probe
    launch.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    launch.restype = None

    generator = torch.Generator(device="cuda")
    f16_wins = 0
    bf16_wins = 0
    ties = 0
    max_output_delta = 0.0
    for scale in (0.125, 1.0, 4.0):
        for seed in (20260811, 7, 97, 997):
            generator.manual_seed(seed)
            q = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            k = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            out_f16 = torch.full(
                (16, 16), float("nan"), dtype=torch.float32, device="cuda"
            )
            out_bf16 = torch.full_like(out_f16, float("nan"))
            launch(
                ctypes.c_void_p(q.data_ptr()),
                ctypes.c_void_p(k.data_ptr()),
                ctypes.c_void_p(out_f16.data_ptr()),
                ctypes.c_void_p(out_bf16.data_ptr()),
            )
            torch.cuda.synchronize()

            # Keep the reference off the C500: a device-side float matmul may
            # select the same backend MMA path and therefore hide its error.
            q_cpu = q.cpu().float()
            k_cpu = k.cpu().float()
            reference = q_cpu @ k_cpu.transpose(0, 1)
            out_f16_cpu = out_f16.cpu()
            out_bf16_cpu = out_bf16.cpu()
            f16_error = (out_f16_cpu - reference).abs()
            bf16_error = (out_bf16_cpu - reference).abs()
            if not bool(torch.isfinite(out_f16).all()):
                raise RuntimeError(f"FP16 MMA produced NaN/Inf at scale={scale} seed={seed}")
            if not bool(torch.isfinite(out_bf16).all()):
                raise RuntimeError(f"BF16 MMA produced NaN/Inf at scale={scale} seed={seed}")

            f16_max = float(f16_error.max().item())
            bf16_max = float(bf16_error.max().item())
            f16_mean = float(f16_error.mean().item())
            bf16_mean = float(bf16_error.mean().item())
            mean_delta = f16_mean - bf16_mean
            if abs(mean_delta) <= 1.0e-12:
                ties += 1
            elif mean_delta < 0.0:
                f16_wins += 1
            else:
                bf16_wins += 1
            max_output_delta = max(
                max_output_delta,
                float((out_f16_cpu - out_bf16_cpu).abs().max().item()),
            )
            print(
                f"scale={scale:g} seed={seed} "
                f"f16 max/mean={f16_max:.6e}/{f16_mean:.6e} "
                f"bf16 max/mean={bf16_max:.6e}/{bf16_mean:.6e}"
            )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "summary: "
        f"f16_wins={f16_wins} bf16_wins={bf16_wins} ties={ties} "
        f"max_output_delta={max_output_delta:.6e}"
    )
    if f16_wins == 12:
        print("[PASS] FP16-input MMA consistently improves K=128 dot precision")
    elif ties == 12 and max_output_delta == 0.0:
        print(
            "[PASS] FP16-input and BF16-input MMA are bitwise equivalent for "
            "all probe outputs; FP16 provides no precision advantage"
        )
    else:
        print(
            "[PASS] probe completed; FP16-input MMA does not provide a "
            "consistent K=128 precision advantage"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
