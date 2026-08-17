#!/usr/bin/env python3
"""Recover xcore1000 mma_16x16x4f32 register-fragment mapping."""

from __future__ import annotations

import argparse
import ctypes
from collections import Counter

import numpy as np
import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")
    library = ctypes.CDLL(args.library)
    launch = library.run_mma_f32_fragment_probe
    launch.argtypes = [ctypes.c_void_p]
    launch.restype = None

    output = torch.empty((64, 64, 64, 4), dtype=torch.float32, device="cuda")
    output.fill_(float("nan"))
    launch(ctypes.c_void_p(output.data_ptr()))
    torch.cuda.synchronize()
    host = output.cpu().numpy()
    if not np.isfinite(host).all():
        raise RuntimeError("probe left NaN/Inf output; kernel did not fully materialize")

    matches: dict[int, list[tuple[int, int, int, float]]] = {}
    count_hist: Counter[int] = Counter()
    for a_lane in range(64):
        rows: list[tuple[int, int, int, float]] = []
        for b_lane in range(64):
            nz = np.argwhere(np.abs(host[a_lane, b_lane]) > 0.5)
            count_hist[len(nz)] += 1
            for out_lane, slot in nz:
                rows.append(
                    (b_lane, int(out_lane), int(slot),
                     float(host[a_lane, b_lane, out_lane, slot]))
                )
        matches[a_lane] = rows

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("nonzero outputs per one-hot pair:", dict(sorted(count_hist.items())))
    # A valid 16x16x4 outer-product mapping has 64*16 compatible pairs and
    # exactly one accumulator element for every compatible pair.
    compatible = sum(len(rows) for rows in matches.values())
    if compatible != 64 * 16 or count_hist[1] != 64 * 16:
        raise RuntimeError(
            f"unexpected mapping: compatible={compatible}, one_nz={count_hist[1]}"
        )
    for a_lane in range(64):
        a_k = a_lane >> 4
        row = a_lane & 15
        expected = {
            (16 * a_k + col, 16 * (row >> 2) + col, row & 3, 1.0)
            for col in range(16)
        }
        if set(matches[a_lane]) != expected:
            raise RuntimeError(f"formula mismatch for A lane {a_lane}")
    print(
        "mapping: A_lane=16*k+row, B_lane=16*k+col, "
        "C_lane=16*(row//4)+col, C_slot=row%4"
    )
    print("[PASS] recovered complete 16x16x4 one-hot fragment mapping")

    k128 = library.run_mma_f32_k128_probe
    k128.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    k128.restype = None
    generator = torch.Generator(device="cuda")
    for seed in (20260809, 7, 97, 997):
        generator.manual_seed(seed)
        q = torch.randn((16, 128), generator=generator, device="cuda").to(
            torch.bfloat16
        )
        k = torch.randn((16, 128), generator=generator, device="cuda").to(
            torch.bfloat16
        )
        result = torch.empty((16, 16), dtype=torch.float32, device="cuda")
        result.fill_(float("nan"))
        k128(
            ctypes.c_void_p(q.data_ptr()),
            ctypes.c_void_p(k.data_ptr()),
            ctypes.c_void_p(result.data_ptr()),
        )
        torch.cuda.synchronize()
        reference = q.float() @ k.float().transpose(0, 1)
        error = (result - reference).abs()
        max_error = float(error.max().item())
        mean_error = float(error.mean().item())
        if not bool(torch.isfinite(result).all()) or max_error > 1.0e-4:
            raise RuntimeError(
                f"K128 seed={seed} failed: max_error={max_error:.6e}"
            )
        print(
            f"[PASS] K128 seed={seed} max_error={max_error:.6e} "
            f"mean_error={mean_error:.6e}"
        )
    print("[PASS] native FP32 MMA preserves FP32 K=128 dot-product accuracy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
