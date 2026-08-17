#!/usr/bin/env python3
"""Check C500 __ldcs/__ldlu uint4 payload semantics."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--vectors", type=int, default=65537)
    args = parser.parse_args()
    if args.vectors <= 0:
        raise ValueError("--vectors must be positive")
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_c500_ldcs_probe
    launch.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    launch.restype = None

    rng = np.random.default_rng(20260814)
    host = rng.integers(0, 2**32, size=(args.vectors, 4), dtype=np.uint32)
    source = torch.from_numpy(host.copy()).to(device="cuda")
    normal = torch.empty_like(source)
    ldcs = torch.empty_like(source)
    ldlu = torch.empty_like(source)
    launch(
        ctypes.c_void_p(source.data_ptr()),
        ctypes.c_void_p(normal.data_ptr()),
        ctypes.c_void_p(ldcs.data_ptr()),
        ctypes.c_void_p(ldlu.data_ptr()),
        args.vectors,
    )
    torch.cuda.synchronize()

    expected = host
    for name, result in (("normal", normal), ("ldcs", ldcs), ("ldlu", ldlu)):
        actual = result.cpu().numpy()
        if not np.array_equal(actual, expected):
            where = np.argwhere(actual != expected)[0]
            raise RuntimeError(
                f"{name} mismatch at vector={where[0]}, word={where[1]}: "
                f"got={int(actual[tuple(where)])}, expected={int(expected[tuple(where)])}"
            )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"[PASS] normal/__ldcs/__ldlu exact uint4 payload for {args.vectors} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
