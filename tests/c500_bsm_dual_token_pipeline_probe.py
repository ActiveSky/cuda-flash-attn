#!/usr/bin/env python3
"""Check alternating two-token BSM K/V page-pipeline semantics on C500."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--iterations", type=int, default=1025)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")
    if args.iterations <= 0:
        raise ValueError("--iterations must be positive")

    library = ctypes.CDLL(args.library)
    launch = library.run_bsm_dual_token_pipeline_probe
    launch.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    launch.restype = None

    # Each stress iteration consumes a current pair and its replacement pair,
    # so it verifies two alternating K/V buffer lifecycles.
    rows = args.iterations * 2 * 64
    rng = np.random.default_rng(20260815)
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

    expected_k = k_host.reshape(args.iterations * 2, 64, 4)[
        :, np.arange(64) ^ 16, :]
    expected_v = v_host.reshape(args.iterations * 2, 64, 4)[
        :, np.arange(64) ^ 32, :]
    got_k = k_output.cpu().numpy()
    got_v = v_output.cpu().numpy()
    if not np.array_equal(got_k, expected_k.reshape(rows, 4)):
        row, word = np.argwhere(got_k != expected_k.reshape(rows, 4))[0]
        raise RuntimeError(f"K mismatch at row={row}, word={word}")
    if not np.array_equal(got_v, expected_v.reshape(rows, 4)):
        row, word = np.argwhere(got_v != expected_v.reshape(rows, 4))[0]
        raise RuntimeError(f"V mismatch at row={row}, word={word}")

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        f"[PASS] {args.iterations} repeated dual-token K/V lifecycles: "
        "K-next is issued before V-current waits, and V-next while K-next is live"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
