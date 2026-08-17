#!/usr/bin/env python3
"""Compare mov_raw_shfl and mov_shfl on a MetaX C500."""

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
    launch = library.run_raw_shfl_runtime_probe
    launch.argtypes = [ctypes.c_void_p] * 5
    launch.restype = None

    mov = torch.full((4, 64), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    raw = torch.full_like(mov, 0xFFFFFFFF)
    mov_reduce = torch.full((64,), float("nan"), dtype=torch.float32, device="cuda")
    raw_reduce = torch.full_like(mov_reduce, float("nan"))
    lane_ids = torch.full((64,), 0xFFFFFFFF, dtype=torch.uint32, device="cuda")
    launch(
        ctypes.c_void_p(mov.data_ptr()),
        ctypes.c_void_p(raw.data_ptr()),
        ctypes.c_void_p(mov_reduce.data_ptr()),
        ctypes.c_void_p(raw_reduce.data_ptr()),
        ctypes.c_void_p(lane_ids.data_ptr()),
    )
    torch.cuda.synchronize()

    lanes = lane_ids.cpu().numpy()
    if not np.array_equal(lanes, np.arange(64, dtype=np.uint32)):
        raise RuntimeError(f"unexpected lane IDs: {lanes.tolist()}")

    mov_host = mov.cpu().numpy()
    raw_host = raw.cpu().numpy()
    modes = (0x128, 0x124, 0x04E, 0x0B1)
    for index, mode in enumerate(modes):
        if not np.array_equal(raw_host[index], mov_host[index]):
            mismatch = np.flatnonzero(raw_host[index] != mov_host[index])
            raise RuntimeError(
                f"raw != mov for mode=0x{mode:03x}; mismatches={mismatch.tolist()}"
            )
        print(f"[PASS] mode=0x{mode:03x}: raw == mov")

    mov_sum = mov_reduce.cpu().numpy()
    raw_sum = raw_reduce.cpu().numpy()
    if not np.array_equal(raw_sum, mov_sum):
        raise RuntimeError(
            "raw allreduce differs from mov allreduce: "
            f"max_error={np.max(np.abs(raw_sum - mov_sum))}"
        )
    print("[PASS] raw four-stage allreduce == mov allreduce")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
