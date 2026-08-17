#!/usr/bin/env python3
"""Read the exp456 cooperative case13 producer resource gate without launching it."""

from __future__ import annotations

import argparse
import ctypes

import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--required-grid", type=int, default=520)
    args = parser.parse_args()
    if args.required_grid <= 0:
        raise ValueError("--required-grid must be positive")
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    query = library.query_case13_coop_phase_resource_exp456
    query.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    query.restype = ctypes.c_int

    device = ctypes.c_int(-1)
    num_regs = ctypes.c_int()
    shared_bytes = ctypes.c_int()
    active_blocks = ctypes.c_int()
    status = query(
        ctypes.byref(device),
        ctypes.byref(num_regs),
        ctypes.byref(shared_bytes),
        ctypes.byref(active_blocks),
    )
    if status:
        raise RuntimeError(f"exp456 resource query failed with CUDA bridge status={status}")

    properties = torch.cuda.get_device_properties(device.value)
    resident_grid = properties.multi_processor_count * active_blocks.value
    print(f"GPU: {torch.cuda.get_device_name(device.value)} (device {device.value})")
    print(
        "exp456 case13 cooperative resource-only instance: "
        f"regs={num_regs.value}, shared={shared_bytes.value} B, "
        f"active_blocks/SM={active_blocks.value}, "
        f"resident_grid={resident_grid}/{args.required_grid}"
    )
    if shared_bytes.value > 8448 or active_blocks.value < 5:
        print(
            "[CLOSED] P2-3: cooperative endpoint loses the required exact "
            "5-block/SM resource tier; no GPU launch attempted"
        )
        return 0
    print("[PASS] P2-3 runtime occupancy gate; inspect compiler stack/spill before any next stage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
