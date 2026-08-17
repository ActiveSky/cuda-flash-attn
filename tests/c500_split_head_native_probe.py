#!/usr/bin/env python3
"""Validate the all-native split-head reduction on a MetaX C500."""

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
    launch = library.run_split_head_native_runtime_probe
    launch.argtypes = [ctypes.c_void_p] * 5
    launch.restype = None

    lanes = torch.full((64,), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    baseline = torch.full((64,), float("nan"), dtype=torch.float32, device="cuda")
    candidate = torch.full_like(baseline, float("nan"))
    bit1_candidate = torch.full_like(baseline, float("nan"))
    bit0_candidate = torch.full_like(baseline, float("nan"))
    launch(
        ctypes.c_void_p(lanes.data_ptr()),
        ctypes.c_void_p(baseline.data_ptr()),
        ctypes.c_void_p(candidate.data_ptr()),
        ctypes.c_void_p(bit1_candidate.data_ptr()),
        ctypes.c_void_p(bit0_candidate.data_ptr()),
    )
    torch.cuda.synchronize()

    lane_host = lanes.cpu().numpy()
    if not np.array_equal(lane_host, np.arange(64, dtype=np.uint32)):
        raise RuntimeError(f"unexpected lane IDs: {lane_host.tolist()}")

    source0 = np.arange(64, dtype=np.float32) + np.float32(0.25)
    source1 = np.arange(64, dtype=np.float32) + np.float32(100.5)
    expected0 = np.empty((64,), dtype=np.float32)
    expected1 = np.empty((64,), dtype=np.float32)
    for row_begin in range(0, 64, 16):
        expected0[row_begin : row_begin + 16] = source0[
            row_begin : row_begin + 16
        ].sum(dtype=np.float32)
        expected1[row_begin : row_begin + 16] = source1[
            row_begin : row_begin + 16
        ].sum(dtype=np.float32)

    baseline_host = baseline.cpu().numpy()
    baseline_expected = np.where((np.arange(64) & 8) != 0, expected1, expected0)
    if not np.array_equal(baseline_host, baseline_expected):
        raise RuntimeError(
            "baseline split-head reduction mismatch: "
            f"max_error={np.max(np.abs(baseline_host - baseline_expected))}"
        )
    print("[PASS] production rotate8/BSM-XOR4 network reduces both heads")

    candidate_host = candidate.cpu().numpy()
    candidate_expected = np.where((np.arange(64) & 4) != 0, expected1, expected0)
    if not np.array_equal(candidate_host, candidate_expected):
        raise RuntimeError(
            "all-native split-head reduction mismatch: "
            f"max_error={np.max(np.abs(candidate_host - candidate_expected))}, "
            f"got={candidate_host.tolist()}"
        )
    print("[PASS] rotate4/rotate8/quad network reduces both heads")

    bit1_host = bit1_candidate.cpu().numpy()
    bit1_expected = np.where((np.arange(64) & 2) != 0, expected1, expected0)
    if not np.array_equal(bit1_host, bit1_expected):
        raise RuntimeError(
            "bit1 split-head reduction mismatch: "
            f"max_error={np.max(np.abs(bit1_host - bit1_expected))}, "
            f"got={bit1_host.tolist()}"
        )
    print("[PASS] quad2/rotate4/rotate8/quad1 bit1 network reduces both heads")

    bit0_host = bit0_candidate.cpu().numpy()
    bit0_expected = np.where((np.arange(64) & 1) != 0, expected1, expected0)
    if not np.array_equal(bit0_host, bit0_expected):
        raise RuntimeError(
            "bit0 split-head reduction mismatch: "
            f"max_error={np.max(np.abs(bit0_host - bit0_expected))}, "
            f"got={bit0_host.tolist()}"
        )
    print("[PASS] quad1/quad2/rotate4/rotate8 bit0 network reduces both heads")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
