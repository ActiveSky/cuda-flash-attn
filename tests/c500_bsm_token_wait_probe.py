#!/usr/bin/env python3
"""Runtime-check scope-0 waits on per-load MXMACA BSM tokens."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


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
    launch = library.run_bsm_token_wait_probe
    launch.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    launch.restype = None

    rows = args.iterations * 64
    rng = np.random.default_rng(20260812)
    k_host = rng.integers(0, 2**32, size=(rows, 4), dtype=np.uint32)
    v_host = rng.integers(0, 2**32, size=(rows, 4), dtype=np.uint32)
    k_input = torch.from_numpy(k_host.copy()).to(device="cuda")
    v_input = torch.from_numpy(v_host.copy()).to(device="cuda")
    k_output = torch.full_like(k_input, 0xA5A5A5A5)
    v_output = torch.full_like(v_input, 0x5A5A5A5A)

    launch(
        ctypes.c_void_p(k_input.data_ptr()),
        ctypes.c_void_p(v_input.data_ptr()),
        ctypes.c_void_p(k_output.data_ptr()),
        ctypes.c_void_p(v_output.data_ptr()),
        args.iterations,
    )
    torch.cuda.synchronize()

    got_k = k_output.cpu().numpy()
    got_v = v_output.cpu().numpy()
    expected_k = k_host.reshape(args.iterations, 64, 4)[:, np.arange(64) ^ 16, :]
    expected_v = v_host.reshape(args.iterations, 64, 4)[:, np.arange(64) ^ 32, :]
    expected_k = expected_k.reshape(rows, 4)
    expected_v = expected_v.reshape(rows, 4)

    if not np.array_equal(got_k, expected_k):
        mismatch = np.argwhere(got_k != expected_k)[0]
        raise RuntimeError(
            f"K scope-0 wait mismatch at row={mismatch[0]}, word={mismatch[1]}: "
            f"got={int(got_k[tuple(mismatch)])}, "
            f"expected={int(expected_k[tuple(mismatch)])}"
        )
    if not np.array_equal(got_v, expected_v):
        mismatch = np.argwhere(got_v != expected_v)[0]
        raise RuntimeError(
            f"V scope-0 wait mismatch at row={mismatch[0]}, word={mismatch[1]}: "
            f"got={int(got_v[tuple(mismatch)])}, "
            f"expected={int(expected_v[tuple(mismatch)])}"
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"[PASS] {args.iterations} K/V overwrite iterations with "
        "per-load scope-0 BSM token waits"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
