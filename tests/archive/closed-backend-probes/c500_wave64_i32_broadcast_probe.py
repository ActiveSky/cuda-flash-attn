#!/usr/bin/env python3
"""Validate a fixed-source raw int32 broadcast inside every z8 wave."""

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
    launch = library.run_wave64_i32_broadcast_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None

    output = torch.full((256,), -1, dtype=torch.int32, device="cuda")
    lanes = torch.full((256,), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    launch(ctypes.c_void_p(output.data_ptr()), ctypes.c_void_p(lanes.data_ptr()))
    torch.cuda.synchronize()

    got = output.cpu().numpy()
    got_lanes = lanes.cpu().numpy()
    expected_lanes = np.tile(np.arange(64, dtype=np.uint32), 4)
    expected = np.repeat(
        np.asarray([0x13570000 + wave for wave in range(4)], dtype=np.int32),
        64,
    )
    if not np.array_equal(got_lanes, expected_lanes):
        raise RuntimeError(f"unexpected physical lane layout: {got_lanes.tolist()}")
    if not np.array_equal(got, expected):
        raise RuntimeError(
            "wave64 raw int32 broadcast mismatch: "
            f"max_abs={np.max(np.abs(got.astype(np.int64) - expected.astype(np.int64)))}"
        )

    print("[PASS] fixed lane-0 raw int32 BSM broadcast is isolated per z8 wave")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
