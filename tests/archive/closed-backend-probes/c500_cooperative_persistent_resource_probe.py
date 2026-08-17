#!/usr/bin/env python3
"""Read exp457's cooperative case13 persistent-kernel resource gate only.

This driver intentionally never launches the candidate.  It queries the exact
cooperative specialization that would be dispatched for case13, so the P2-4
runtime-residency gate remains separate from correctness/performance testing.
"""

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
    query = library.query_case13_coop_persistent_resource_exp457
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
        raise RuntimeError(f"exp457 resource query failed with CUDA bridge status={status}")

    properties = torch.cuda.get_device_properties(device.value)
    resident_grid = properties.multi_processor_count * active_blocks.value
    print(f"GPU: {torch.cuda.get_device_name(device.value)} (device {device.value})")
    print(
        "exp457 case13 cooperative persistent instance: "
        f"regs={num_regs.value}, shared={shared_bytes.value} B, "
        f"active_blocks/SM={active_blocks.value}, "
        f"resident_grid={resident_grid}/{args.required_grid}"
    )
    if shared_bytes.value > 8448 or active_blocks.value < 5 or resident_grid < args.required_grid:
        print(
            "[CLOSED] P2-4: cooperative persistent endpoint loses the exact "
            "case13 residency tier; no candidate launch attempted"
        )
        return 0
    print("[PASS] P2-4 runtime occupancy gate; correctness may proceed serially")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
