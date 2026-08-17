#!/usr/bin/env python3
"""Validate MXMACA's native 16x16x4 FP32 MMA on a real C500."""

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
    launch = library.run_fp32_mma_k128_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None
    map_launch = library.run_fp32_mma_basis_map_probe
    map_launch.argtypes = [ctypes.c_void_p]
    map_launch.restype = None

    rng = np.random.default_rng(20260811)
    # Quantize through BF16 first: these are the exact FP32 values that an
    # attention producer would obtain after converting Q/K cache elements.
    a = torch.from_numpy(rng.standard_normal((16, 128), dtype=np.float32))
    b = torch.from_numpy(rng.standard_normal((128, 16), dtype=np.float32))
    a = a.to(torch.bfloat16).to(torch.float32).cuda()
    b = b.to(torch.bfloat16).to(torch.float32).cuda()
    out = torch.full((16, 16), float("nan"), dtype=torch.float32, device="cuda")

    launch(
        ctypes.c_void_p(a.data_ptr()),
        ctypes.c_void_p(b.data_ptr()),
        ctypes.c_void_p(out.data_ptr()),
    )
    torch.cuda.synchronize()

    got = out.cpu().numpy()
    reference = a.cpu().numpy() @ b.cpu().numpy()
    if not np.isfinite(got).all():
        raise RuntimeError("FP32 MMA produced NaN/Inf")
    max_error = float(np.max(np.abs(got - reference)))
    max_rel = float(
        np.max(np.abs(got - reference) / np.maximum(np.abs(reference), 1.0e-6))
    )
    if not np.allclose(got, reference, atol=2.0e-5, rtol=2.0e-5):
        basis = torch.zeros((64, 64, 256), dtype=torch.float32, device="cuda")
        map_launch(ctypes.c_void_p(basis.data_ptr()))
        torch.cuda.synchronize()
        basis_host = basis.cpu().numpy()
        records: list[tuple[int, int, int]] = []
        for a_slot in range(64):
            for b_slot in range(64):
                nz = np.flatnonzero(np.abs(basis_host[a_slot, b_slot]) > 0.5)
                if nz.size:
                    if nz.size != 1 or basis_host[a_slot, b_slot, nz[0]] != 1.0:
                        raise RuntimeError(
                            f"unexpected basis result a={a_slot} b={b_slot}: "
                            f"indices={nz.tolist()}"
                        )
                    records.append((a_slot, b_slot, int(nz[0])))
        print(f"basis_nonzero_records={len(records)}")
        print("basis_first_96=" + repr(records[:96]))
        mismatch = np.unravel_index(np.argmax(np.abs(got - reference)), got.shape)
        raise RuntimeError(
            "FP32 MMA mapping/accumulation mismatch: "
            f"index={mismatch} got={got[mismatch]} ref={reference[mismatch]} "
            f"max_error={max_error:.6e} max_rel={max_rel:.6e}"
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("[PASS] __builtin_mxc_mma_16x16x4f32 fragment mapping is 16x16")
    print(
        "[PASS] 32 chained K=4 MMA steps match K=128 FP32 matmul: "
        f"max_error={max_error:.6e} max_rel={max_rel:.6e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
