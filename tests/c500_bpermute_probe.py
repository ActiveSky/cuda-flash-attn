#!/usr/bin/env python3
"""Validate row-local and cross-half exchanges with raw BSM bpermute."""

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
    launch = library.run_bpermute_runtime_probe
    launch.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    launch.restype = None

    raw = torch.full((4, 64), float("nan"), dtype=torch.float32, device="cuda")
    wrapped = torch.full_like(raw, float("nan"))
    row0_broadcast = torch.full(
        (64,), float("nan"), dtype=torch.float32, device="cuda"
    )
    row16_broadcast_raw = torch.full(
        (16, 64), float("nan"), dtype=torch.float32, device="cuda"
    )
    row16_broadcast_wrapped = torch.full_like(
        row16_broadcast_raw, float("nan")
    )
    row16_broadcast_native0 = torch.full_like(
        row0_broadcast, float("nan")
    )
    raw_allreduce = torch.full_like(row0_broadcast, float("nan"))
    native_allreduce = torch.full_like(row0_broadcast, float("nan"))
    wave64_xor32 = torch.full_like(row0_broadcast, float("nan"))
    lane_ids = torch.full((64,), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    launch(
        ctypes.c_void_p(raw.data_ptr()),
        ctypes.c_void_p(wrapped.data_ptr()),
        ctypes.c_void_p(row0_broadcast.data_ptr()),
        ctypes.c_void_p(row16_broadcast_raw.data_ptr()),
        ctypes.c_void_p(row16_broadcast_wrapped.data_ptr()),
        ctypes.c_void_p(row16_broadcast_native0.data_ptr()),
        ctypes.c_void_p(raw_allreduce.data_ptr()),
        ctypes.c_void_p(native_allreduce.data_ptr()),
        ctypes.c_void_p(wave64_xor32.data_ptr()),
        ctypes.c_void_p(lane_ids.data_ptr()),
    )
    torch.cuda.synchronize()

    raw_host = raw.cpu().numpy()
    wrapped_host = wrapped.cpu().numpy()
    row0_broadcast_host = row0_broadcast.cpu().numpy()
    row16_broadcast_raw_host = row16_broadcast_raw.cpu().numpy()
    row16_broadcast_wrapped_host = row16_broadcast_wrapped.cpu().numpy()
    row16_broadcast_native0_host = row16_broadcast_native0.cpu().numpy()
    raw_allreduce_host = raw_allreduce.cpu().numpy()
    native_allreduce_host = native_allreduce.cpu().numpy()
    wave64_xor32_host = wave64_xor32.cpu().numpy()
    lanes = lane_ids.cpu().numpy()
    expected_lanes = np.arange(64, dtype=np.uint32)
    if not np.array_equal(lanes, expected_lanes):
        raise RuntimeError(f"unexpected lane IDs: {lanes.tolist()}")

    source = np.arange(64, dtype=np.float32) + np.float32(0.25)
    offsets = (8, 4, 2, 1)
    for row, offset in enumerate(offsets):
        expected = source[np.arange(64) ^ offset]
        if not np.array_equal(raw_host[row], expected):
            raise RuntimeError(
                f"raw bpermute mismatch at offset={offset}: "
                f"max_error={np.max(np.abs(raw_host[row] - expected))}"
            )
        if not np.array_equal(wrapped_host[row], expected):
            raise RuntimeError(
                f"wrapper mismatch at offset={offset}: "
                f"max_error={np.max(np.abs(wrapped_host[row] - expected))}"
            )
        if not np.array_equal(raw_host[row], wrapped_host[row]):
            raise RuntimeError(f"raw/wrapper mismatch at offset={offset}")
        subgroup = np.arange(64) // 16
        source_subgroup = (np.arange(64) ^ offset) // 16
        if not np.array_equal(subgroup, source_subgroup):
            raise RuntimeError(f"offset={offset} crossed a 16-lane subgroup")
        print(f"[PASS] offset={offset}: raw == wrapper == lane^offset")

    expected_broadcast = source[np.arange(64) & 15]
    if not np.array_equal(row0_broadcast_host, expected_broadcast):
        raise RuntimeError(
            "raw cross-row broadcast mismatch: "
            f"max_error={np.max(np.abs(row0_broadcast_host - expected_broadcast))}"
        )
    for row in range(4):
        got = row0_broadcast_host[row * 16 : (row + 1) * 16]
        if not np.array_equal(got, source[:16]):
            raise RuntimeError(f"row {row} did not receive row-0 values")
    print("[PASS] raw BSM bpermute broadcasts row 0 to all four rows")

    lane_rows = (np.arange(64) // 16) * 16
    for source_tx in range(16):
        expected = source[lane_rows + source_tx]
        raw_got = row16_broadcast_raw_host[source_tx]
        wrapped_got = row16_broadcast_wrapped_host[source_tx]
        if not np.array_equal(raw_got, expected):
            raise RuntimeError(
                f"raw row-local broadcast mismatch at source_tx={source_tx}: "
                f"max_error={np.max(np.abs(raw_got - expected))}"
            )
        if not np.array_equal(wrapped_got, expected):
            raise RuntimeError(
                f"wrapper row-local broadcast mismatch at source_tx={source_tx}: "
                f"max_error={np.max(np.abs(wrapped_got - expected))}"
            )
        if not np.array_equal(raw_got, wrapped_got):
            raise RuntimeError(
                f"raw/wrapper row-local mismatch at source_tx={source_tx}"
            )
    print("[PASS] raw row-local broadcasts == wrapper for source tx 0..15")

    expected_native0 = source[lane_rows]
    if not np.array_equal(row16_broadcast_native0_host, expected_native0):
        raise RuntimeError(
            "native row lane-0 broadcast mismatch: "
            f"max_error={np.max(np.abs(row16_broadcast_native0_host - expected_native0))}"
        )
    print("[PASS] native mov.shfl mode 0x150 broadcasts lane 0 within each row")

    expected_sum = np.repeat(
        np.asarray(
            [source[row * 16 : (row + 1) * 16].sum() for row in range(4)],
            dtype=np.float32,
        ),
        16,
    )
    if not np.array_equal(raw_allreduce_host, expected_sum):
        raise RuntimeError(
            "raw XOR allreduce mismatch: "
            f"max_error={np.max(np.abs(raw_allreduce_host - expected_sum))}"
        )
    if not np.array_equal(native_allreduce_host, raw_allreduce_host):
        raise RuntimeError(
            "native row shuffle allreduce mismatch: "
            f"max_error={np.max(np.abs(native_allreduce_host - raw_allreduce_host))}, "
            f"native={native_allreduce_host.tolist()}"
        )
    print("[PASS] native row rotate/quad allreduce == raw XOR allreduce")

    expected_xor32 = source[np.arange(64) ^ 32]
    if not np.array_equal(wave64_xor32_host, expected_xor32):
        raise RuntimeError(
            "raw wave64 XOR-32 mismatch: "
            f"max_error={np.max(np.abs(wave64_xor32_host - expected_xor32))}, "
            f"got={wave64_xor32_host.tolist()}"
        )
    print("[PASS] raw BSM bpermute exchanges FP32 lane ^ 32 across a 64-lane wave")

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "[PASS] raw BSM bpermute preserves row-local XOR, cross-row broadcast, "
        "and wave-half XOR-32"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
