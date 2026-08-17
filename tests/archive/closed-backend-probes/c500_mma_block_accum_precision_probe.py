#!/usr/bin/env python3
"""Compare chained BF16 MMA against zero-started K=16 tile accumulation."""

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
    launch = library.run_mma_bf16_block_accum_precision_probe
    launch.argtypes = [ctypes.c_void_p] * 4
    launch.restype = None

    generator = torch.Generator(device="cuda")
    zero_started_wins = 0
    samples = 0
    for scale in (0.125, 1.0, 4.0):
        for seed in (20260813, 7, 97, 997):
            generator.manual_seed(seed)
            q = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            k = (torch.randn((16, 128), generator=generator, device="cuda") * scale).to(
                torch.bfloat16
            )
            chained = torch.full(
                (16, 16), float("nan"), dtype=torch.float32, device="cuda"
            )
            tiles = torch.full(
                (8, 16, 16), float("nan"), dtype=torch.float32, device="cuda"
            )
            launch(
                ctypes.c_void_p(q.data_ptr()),
                ctypes.c_void_p(k.data_ptr()),
                ctypes.c_void_p(chained.data_ptr()),
                ctypes.c_void_p(tiles.data_ptr()),
            )
            torch.cuda.synchronize()

            # Keep all references and the alternate tile merge on the CPU so
            # no C500 matmul path can hide the same backend behavior.
            q_cpu = q.cpu().float()
            k_cpu = k.cpu().float()
            reference = q_cpu @ k_cpu.transpose(0, 1)
            tile_reference = torch.stack(
                [
                    q_cpu[:, 16 * i : 16 * (i + 1)]
                    @ k_cpu[:, 16 * i : 16 * (i + 1)].transpose(0, 1)
                    for i in range(8)
                ]
            )
            chained_cpu = chained.cpu()
            tiles_cpu = tiles.cpu()
            merged = tiles_cpu.sum(dim=0)

            if not bool(torch.isfinite(chained_cpu).all()):
                raise RuntimeError("chained MMA produced NaN/Inf")
            if not bool(torch.isfinite(tiles_cpu).all()):
                raise RuntimeError("zero-started MMA tile produced NaN/Inf")

            chained_error = (chained_cpu - reference).abs()
            merged_error = (merged - reference).abs()
            tile_error = (tiles_cpu - tile_reference).abs()
            chained_mean = float(chained_error.mean())
            merged_mean = float(merged_error.mean())
            if merged_mean < chained_mean:
                zero_started_wins += 1
            samples += 1
            print(
                f"scale={scale:g} seed={seed} "
                f"chain max/mean={float(chained_error.max()):.6e}/"
                f"{chained_mean:.6e} "
                f"zero+fp32 max/mean={float(merged_error.max()):.6e}/"
                f"{merged_mean:.6e} "
                f"tile max/mean={float(tile_error.max()):.6e}/"
                f"{float(tile_error.mean()):.6e}"
            )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"zero_started_wins={zero_started_wins}/{samples}")
    if zero_started_wins == samples:
        print("[PASS] zero-started K=16 tiles consistently improve precision")
    else:
        print("[PASS] cross-tile accumulator chaining is not the sole precision wall")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
