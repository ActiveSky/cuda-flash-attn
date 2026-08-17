#!/usr/bin/env python3
"""Validate MCTLASS-style waits for register-returning async global loads."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def run_one(library: ctypes.CDLL, threads: int, iterations: int) -> None:
    rows = threads * iterations
    rng = np.random.default_rng(20260815 + threads)
    host = rng.integers(0, 2**32, size=(rows, 4), dtype=np.uint32)
    input_tensor = torch.from_numpy(host.copy()).to(device="cuda")
    output_tensor = torch.full_like(input_tensor, 0xA5A5A5A5)

    launch = library.run_async_register_gld_probe
    launch(
        ctypes.c_void_p(input_tensor.data_ptr()),
        ctypes.c_void_p(output_tensor.data_ptr()),
        iterations,
        threads,
    )
    torch.cuda.synchronize()

    got = output_tensor.cpu().numpy()
    if not np.array_equal(got, host):
        row, word = np.argwhere(got != host)[0]
        raise RuntimeError(
            f"threads={threads}: mismatch at row={row}, word={word}: "
            f"got={int(got[row, word])}, expected={int(host[row, word])}"
        )
    print(f"[PASS] threads={threads}, iterations={iterations}, async128 payloads match")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--iterations", type=int, default=257)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")
    if args.iterations <= 0:
        raise ValueError("--iterations must be positive")

    library = ctypes.CDLL(args.library)
    launch = library.run_async_register_gld_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    launch.restype = None

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    for threads in (64, 256):
        run_one(library, threads, args.iterations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
