#!/usr/bin/env python3
"""Validate MACA packed signed dot-product primitives on a real C500."""

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
    launch = library.run_sdot4_runtime_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None

    builtin_out = torch.full((64,), 0x5A5A5A5A, dtype=torch.int32, device="cuda")
    scalar_out = torch.full_like(builtin_out, 0x6B6B6B6B)
    launch(
        ctypes.c_void_p(builtin_out.data_ptr()),
        ctypes.c_void_p(scalar_out.data_ptr()),
    )
    torch.cuda.synchronize()

    builtin_host = builtin_out.cpu().numpy()
    scalar_host = scalar_out.cpu().numpy()
    if not np.array_equal(builtin_host, scalar_host):
        mismatch = np.flatnonzero(builtin_host != scalar_host)
        first = int(mismatch[0])
        raise RuntimeError(
            "sdot4 mismatch: "
            f"lane={first} builtin={builtin_host[first]} "
            f"scalar={scalar_host[first]} mismatches={mismatch.size}"
        )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print("[PASS] __mckl_sdot4 == four signed INT8 products plus INT32 seed")
    print(f"range=[{int(builtin_host.min())}, {int(builtin_host.max())}]")

    launch8 = library.run_sdot8_runtime_probe
    launch8.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    launch8.restype = None
    builtin8 = torch.full_like(builtin_out, 0x12345678)
    nibble8 = torch.full_like(builtin_out, 0x23456789)
    byte8 = torch.full_like(builtin_out, 0x3456789A)
    launch8(
        ctypes.c_void_p(builtin8.data_ptr()),
        ctypes.c_void_p(nibble8.data_ptr()),
        ctypes.c_void_p(byte8.data_ptr()),
    )
    torch.cuda.synchronize()
    builtin8_host = builtin8.cpu().numpy()
    nibble8_host = nibble8.cpu().numpy()
    byte8_host = byte8.cpu().numpy()
    if np.array_equal(builtin8_host, nibble8_host):
        print("[PASS] __mckl_sdot8 == eight signed INT4 products plus INT32 seed")
    elif np.array_equal(builtin8_host, byte8_host):
        print("[PASS] __mckl_sdot8 aliases four signed INT8 products plus INT32 seed")
    else:
        mismatch_nibble = int(np.count_nonzero(builtin8_host != nibble8_host))
        mismatch_byte = int(np.count_nonzero(builtin8_host != byte8_host))
        raise RuntimeError(
            "sdot8 semantics unknown: "
            f"builtin[0]={builtin8_host[0]} nibble[0]={nibble8_host[0]} "
            f"byte[0]={byte8_host[0]} mismatches="
            f"{mismatch_nibble}/{mismatch_byte}"
        )

    launch_cvt = library.run_cvt_pk_f32tou8_runtime_probe
    launch_cvt.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    launch_cvt.restype = None
    cvt_outputs = [
        torch.full((64,), 0x456789AB, dtype=torch.uint32, device="cuda")
        for _ in range(4)
    ]
    launch_cvt(
        *(ctypes.c_void_p(output.data_ptr()) for output in cvt_outputs),
    )
    torch.cuda.synchronize()
    cvt_host = [output.cpu().numpy() for output in cvt_outputs]
    print("[INFO] __builtin_mxc_cvt_pk_f32tou8 samples:")
    for lane in (0, 1, 7, 31, 63):
        values = "/".join(f"0x{int(output[lane]):08x}" for output in cvt_host)
        x = (lane - 16.0) * 16.0 + 0.625
        print(f"  lane={lane:2d} x={x:8.3f} slots={values}")

    launch_sequence = library.run_cvt_pk_f32tou8_sequence_probe
    launch_sequence.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    launch_sequence.restype = None
    probes = np.array(
        [
            -300.0,
            -1.6,
            -1.5,
            -1.4,
            -0.6,
            -0.5,
            -0.4,
            0.0,
            0.4,
            0.5,
            0.6,
            1.4,
            1.5,
            1.6,
            2.4,
            2.5,
            2.6,
            126.5,
            127.4,
            127.5,
            127.6,
            128.5,
            253.5,
            254.4,
            254.5,
            254.6,
            255.0,
            255.4,
            255.5,
            255.6,
            256.0,
            300.0,
        ],
        dtype=np.float32,
    )
    tiled = np.resize(probes, 64 * 4).reshape(64, 4).copy()
    values_gpu = torch.from_numpy(tiled).cuda()
    packed_gpu = torch.zeros((64,), dtype=torch.uint32, device="cuda")
    unpacked_gpu = torch.full((64, 4), float("nan"), device="cuda")
    launch_sequence(
        ctypes.c_void_p(values_gpu.data_ptr()),
        ctypes.c_void_p(packed_gpu.data_ptr()),
        ctypes.c_void_p(unpacked_gpu.data_ptr()),
    )
    torch.cuda.synchronize()
    packed = packed_gpu.cpu().numpy()
    unpacked = unpacked_gpu.cpu().numpy()
    packed_bytes = np.stack(
        [((packed >> (8 * slot)) & 0xFF).astype(np.float32) for slot in range(4)],
        axis=1,
    )
    if not np.array_equal(unpacked, packed_bytes):
        raise RuntimeError("b0..b3 unpack does not match packed byte order")

    candidates = {
        "nearest-even+saturate": np.clip(np.rint(tiled), 0, 255),
        "truncate+saturate": np.clip(np.trunc(tiled), 0, 255),
        "floor+saturate": np.clip(np.floor(tiled), 0, 255),
    }
    semantics = next(
        (name for name, expected in candidates.items() if np.array_equal(unpacked, expected)),
        None,
    )
    if semantics is None:
        mismatches = np.argwhere(unpacked != candidates["nearest-even+saturate"])
        examples = [
            (float(tiled[i, j]), float(unpacked[i, j]))
            for i, j in mismatches[:12]
        ]
        raise RuntimeError(f"unknown packed-U8 conversion semantics: {examples}")
    print(f"[PASS] sequential slot insertion and byte unpack: {semantics}")
    print(
        "samples="
        + ", ".join(
            f"{float(tiled[i, j]):g}->{int(unpacked[i, j])}"
            for i, j in ((0, 0), (0, 1), (1, 0), (2, 0), (4, 1), (7, 1))
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
