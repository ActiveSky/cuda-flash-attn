#!/usr/bin/env python3
"""Check `readlane(lane ^ 32)` in the z8 producer's exact CTA geometry."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_readlane_wave64_xor32_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None

    output = torch.full((256,), float("nan"), dtype=torch.float32, device="cuda")
    lane_ids = torch.full((256,), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    launch(ctypes.c_void_p(output.data_ptr()), ctypes.c_void_p(lane_ids.data_ptr()))
    torch.cuda.synchronize()

    got = output.cpu().numpy()
    lanes = lane_ids.cpu().numpy()
    expected_lanes = np.tile(np.arange(64, dtype=np.uint32), 4)
    if not np.array_equal(lanes, expected_lanes):
        raise RuntimeError(f"unexpected physical lane layout: {lanes.tolist()}")

    wave = np.repeat(np.arange(4, dtype=np.float32), 64)
    expected = wave * np.float32(64.0) + (
        expected_lanes ^ np.uint32(32)
    ).astype(np.float32) + np.float32(0.25)
    if not np.array_equal(got, expected):
        raise RuntimeError(
            "readlane wave64 xor32 mismatch: "
            f"max_error={np.max(np.abs(got - expected))}, got={got.tolist()}"
        )

    print("[PASS] readlane exchanges lane ^ 32 across every z8 64-lane wave")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
