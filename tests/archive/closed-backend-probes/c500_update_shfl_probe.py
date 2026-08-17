#!/usr/bin/env python3
"""Validate update_shfl semantics against mov_shfl on a MetaX C500."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def _hex_rows(values: np.ndarray) -> str:
    return " ".join(f"0x{int(value):08x}" for value in values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_update_shfl_runtime_probe
    launch.argtypes = [ctypes.c_void_p] * 8
    launch.restype = None

    def uint_tensor(*shape: int) -> torch.Tensor:
        return torch.full(shape, 0xFFFFFFFF, dtype=torch.uint32, device="cuda")

    mov_full = uint_tensor(4, 64)
    update_same_full = uint_tensor(4, 64)
    update_old_full = uint_tensor(4, 64)
    update_row_masks = uint_tensor(6, 64)
    update_bank_masks = uint_tensor(6, 64)
    mov_reduce = torch.full((64,), float("nan"), dtype=torch.float32, device="cuda")
    update_reduce = torch.full_like(mov_reduce, float("nan"))
    lane_ids = uint_tensor(64)

    launch(
        ctypes.c_void_p(mov_full.data_ptr()),
        ctypes.c_void_p(update_same_full.data_ptr()),
        ctypes.c_void_p(update_old_full.data_ptr()),
        ctypes.c_void_p(update_row_masks.data_ptr()),
        ctypes.c_void_p(update_bank_masks.data_ptr()),
        ctypes.c_void_p(mov_reduce.data_ptr()),
        ctypes.c_void_p(update_reduce.data_ptr()),
        ctypes.c_void_p(lane_ids.data_ptr()),
    )
    torch.cuda.synchronize()

    lanes = lane_ids.cpu().numpy()
    if not np.array_equal(lanes, np.arange(64, dtype=np.uint32)):
        raise RuntimeError(f"unexpected lane IDs: {lanes.tolist()}")

    mov = mov_full.cpu().numpy()
    same = update_same_full.cpu().numpy()
    old = update_old_full.cpu().numpy()
    modes = (0x128, 0x124, 0x04E, 0x0B1)
    for index, mode in enumerate(modes):
        if not np.array_equal(same[index], mov[index]):
            raise RuntimeError(f"update(value,value) != mov for mode=0x{mode:03x}")
        if not np.array_equal(old[index], mov[index]):
            raise RuntimeError(
                f"full-mask update(old,source) retained old bits for mode=0x{mode:03x}"
            )
        print(f"[PASS] mode=0x{mode:03x}: full-mask update == mov")

    mov_sum = mov_reduce.cpu().numpy()
    update_sum = update_reduce.cpu().numpy()
    if not np.array_equal(update_sum, mov_sum):
        raise RuntimeError(
            "update allreduce differs from mov allreduce: "
            f"max_error={np.max(np.abs(update_sum - mov_sum))}"
        )
    print("[PASS] four-stage update allreduce == mov allreduce")

    masks = (0x0, 0x1, 0x3, 0x5, 0x7, 0xF)
    row_results = update_row_masks.cpu().numpy()
    bank_results = update_bank_masks.cpu().numpy()
    source = np.arange(64, dtype=np.uint32) + np.uint32(0x10000000)
    old_source = np.arange(64, dtype=np.uint32) + np.uint32(0x70000000)
    rotated = source[(np.arange(64) // 16) * 16 + ((np.arange(64) + 8) & 15)]

    for label, results in (("row", row_results), ("bank", bank_results)):
        for index, mask in enumerate(masks):
            got = results[index]
            moved = int(np.count_nonzero(got == rotated))
            retained = int(np.count_nonzero(got == old_source))
            other = 64 - moved - retained
            print(
                f"[INFO] {label}_mask=0x{mask:x}: "
                f"shuffled={moved} retained_old={retained} other={other}"
            )
            if other:
                unexpected = got[(got != rotated) & (got != old_source)][:8]
                print(f"       unexpected: {_hex_rows(unexpected)}")

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("[PASS] update_shfl is a masked destination update, not an arithmetic reduction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
