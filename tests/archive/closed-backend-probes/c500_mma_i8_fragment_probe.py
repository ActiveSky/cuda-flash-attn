#!/usr/bin/env python3
"""Validate xcore1000 signed-INT8 MMA fragment layout and arithmetic."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--seeds", type=int, default=8)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_mma_i8_fragment_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None

    for seed in range(args.seeds):
        rng = np.random.default_rng(seed)
        a_host = rng.integers(-31, 32, size=(16, 16), dtype=np.int8)
        b_host = rng.integers(-31, 32, size=(16, 16), dtype=np.int8)
        expected = a_host.astype(np.int32) @ b_host.astype(np.int32)
        a = torch.from_numpy(a_host).to(device="cuda")
        b = torch.from_numpy(b_host).to(device="cuda")
        output = torch.full(
            (16, 16), 0x5A5A5A5A, dtype=torch.int32, device="cuda"
        )
        launch(
            ctypes.c_void_p(a.data_ptr()),
            ctypes.c_void_p(b.data_ptr()),
            ctypes.c_void_p(output.data_ptr()),
        )
        torch.cuda.synchronize()
        got = output.cpu().numpy()
        if not np.array_equal(got, expected):
            mismatch = np.argwhere(got != expected)
            row, col = (int(v) for v in mismatch[0])
            raise RuntimeError(
                f"seed={seed} mismatch at ({row},{col}): "
                f"got={got[row, col]} expected={expected[row, col]} "
                f"mismatches={mismatch.shape[0]}"
            )
        print(
            f"[PASS] seed={seed} exact INT8 GEMM "
            f"range=[{int(got.min())}, {int(got.max())}]"
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("[PASS] MMA I8 mapping: packed K4 per lane, FP32-probe C mapping")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
