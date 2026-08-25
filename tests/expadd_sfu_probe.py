#!/usr/bin/env python3
"""Run the narrow C500 expaddf semantic/SFU probe."""

from __future__ import annotations

import argparse
import ctypes
import math
import struct

import numpy as np
import torch


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    # Include normal finite softmax-scale magnitudes, subnormals/overflow
    # boundaries, and exceptional inputs.  Scale is intentionally wider than
    # the attention contract so the intrinsic's integer exponent behavior is
    # observable rather than inferred from one benign point.
    xs = np.asarray(
        [
            -150.0,
            np.float32(-1.40129846e-45),
            np.float32(1.40129846e-45),
            np.float32(-1.17549435e-38),
            np.float32(1.17549435e-38),
            -128.0,
            -127.0,
            -126.0,
            -64.0,
            -10.0,
            -1.5,
            -0.0,
            0.0,
            0.5,
            1.0,
            10.0,
            64.0,
            126.0,
            127.0,
            128.0,
            150.0,
            np.float32(np.nan),
            np.float32(np.inf),
            np.float32(-np.inf),
        ],
        dtype=np.float32,
    )
    scales = np.asarray(
        [-(2**31), -256, -255, -149, -128, -127, -126, -64, -32,
         -8, -1, 0, 1, 8, 32, 64, 126, 127, 128, 149, 255, 256,
         2**31 - 1],
        dtype=np.int32,
    )
    x = np.repeat(xs, scales.size)
    scale = np.tile(scales, xs.size)

    library = ctypes.CDLL(args.library)
    launch = library.run_expadd_sfu_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    launch.restype = None

    # Keep input/output on device for the driver call, matching the existing
    # C500 probe convention; the host arrays are only the test vectors.
    dx = torch.from_numpy(x).cuda()
    db = torch.from_numpy(scale).cuda()
    dout = torch.empty((x.size, 8), dtype=torch.float32, device="cuda")
    launch(
        ctypes.c_void_p(dx.data_ptr()),
        ctypes.c_void_p(db.data_ptr()),
        ctypes.c_void_p(dout.data_ptr()),
        ctypes.c_int(x.size),
    )
    torch.cuda.synchronize()
    actual = dout.cpu().numpy()

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"vectors={x.size} x_values={xs.size} scale_values={scales.size}")
    print("columns: expaddf, ldexpf, exp2(x), exp2(x+b), exp2(x)*exp2(b), x*exp2(b), exp2(x-b), exp2(x)+b")

    # Print compact bit patterns.  Exact equality is expected for the
    # ldexp-like candidate if that is the intrinsic's contract; approximate
    # comparisons alone are not sufficient around NaN/subnormal boundaries.
    mismatches = 0
    expected = np.ldexp(x, scale)
    expected_bits = expected.view(np.uint32)
    actual_bits = actual[:, 0].view(np.uint32)
    semantic_mismatches = np.flatnonzero(actual_bits != expected_bits)
    if semantic_mismatches.size:
        print("first expaddf-vs-host-ldexp mismatch:", int(semantic_mismatches[0]))
    print(f"expaddf_vs_host_float32_ldexp_bit_mismatches={semantic_mismatches.size}/{x.size}")
    for i, (xi, bi) in enumerate(zip(x, scale)):
        row = actual[i]
        if bits(float(row[0])) != bits(float(row[1])):
            mismatches += 1
        if i < 80 or not math.isfinite(float(xi)):
            words = " ".join(f"{bits(float(v)):08x}" for v in row)
            print(f"i={i:04d} x={float(xi)!r} b={int(bi):4d} bits={words}")
    print(f"expaddf_vs_ldexpf_bit_mismatches={mismatches}/{x.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
