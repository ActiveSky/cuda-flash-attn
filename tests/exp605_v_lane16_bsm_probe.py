#!/usr/bin/env python3
"""Validate raw BSM lane^16 V payload exchange on the exact z8 geometry."""

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
    launch = library.run_exp605_v_lane16_bsm_probe
    launch.argtypes = [ctypes.c_void_p]
    launch.restype = None

    output = torch.full((256, 4), -1, dtype=torch.int32, device="cuda")
    launch(ctypes.c_void_p(output.data_ptr()))
    torch.cuda.synchronize()
    got = output.cpu().numpy().view(np.uint32).reshape(8, 2, 16, 4)

    expected = np.empty_like(got)
    for tz in range(8):
        for ty in range(2):
            for tx in range(16):
                base = (tz << 24) | ((1 - ty) << 16) | (tx << 8)
                expected[tz, ty, tx] = np.asarray(
                    [base | word for word in range(4)], dtype=np.uint32
                )
    if not np.array_equal(got, expected):
        mismatch = np.argwhere(got != expected)[0]
        raise RuntimeError(
            "lane^16 V payload mismatch at "
            f"tz={mismatch[0]}, ty={mismatch[1]}, tx={mismatch[2]}, "
            f"word={mismatch[3]}: got=0x{int(got[tuple(mismatch)]):08x}, "
            f"expected=0x{int(expected[tuple(mismatch)]):08x}"
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "[PASS] exp605 lane^16 exchanges all four uint32 words with the "
        "same tx/tz and opposite ty in every physical z-pair wave"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
