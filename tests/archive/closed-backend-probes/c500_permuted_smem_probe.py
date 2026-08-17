#!/usr/bin/env python3
"""Check ordinary k128B shared swizzling on the C500 target.

The probe compares the current row-major 128-bit page layout with the
official mcflashinfer k128B XOR-permuted address formula.  It is intentionally
not a FlashAttention benchmark: it isolates the repeated shared consumer
pattern and reports clocks only as capability evidence.
"""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def percentiles(values: np.ndarray) -> tuple[float, float, float]:
    return tuple(float(x) for x in np.percentile(values.astype(np.float64), [10, 50, 90]))


def run_case(library: ctypes.CDLL, threads: int, rounds: int, repetitions: int) -> None:
    rows = threads // 16
    rng = np.random.default_rng(20260815 + threads)
    input_host = rng.integers(0, 2**32, size=(2, 4, 16, 4), dtype=np.uint32)

    # torch.int32/int64 are used only as raw storage; the host views restore
    # uint32/uint64 bit patterns after the device call.
    # The C500 bridge may retain a multidimensional logical layout for an
    # int32 tensor.  The probe passes a raw C pointer, so make its backing
    # storage explicitly one-dimensional before the device transfer.
    input_device = torch.from_numpy(
        input_host.reshape(-1).view(np.int32).copy()
    ).to("cuda")
    # A sentinel distinguishes a malformed/no-op ABI call from a real shared
    # payload permutation; torch.empty() can otherwise retain input-like data.
    row_output = torch.full(
        (threads, 2, rows, 4), -1, dtype=torch.int32, device="cuda"
    )
    swizzled_output = torch.full_like(row_output, -1)
    row_producer = torch.empty(repetitions, dtype=torch.int64, device="cuda")
    row_consumer = torch.empty_like(row_producer)
    swizzled_producer = torch.empty_like(row_producer)
    swizzled_consumer = torch.empty_like(row_producer)
    row_checksums = torch.empty(repetitions, dtype=torch.int32, device="cuda")
    swizzled_checksums = torch.empty_like(row_checksums)

    launch = library.run_permuted_smem_probe
    launch(
        ctypes.c_void_p(input_device.data_ptr()),
        ctypes.c_void_p(row_output.data_ptr()),
        ctypes.c_void_p(swizzled_output.data_ptr()),
        ctypes.c_void_p(row_producer.data_ptr()),
        ctypes.c_void_p(row_consumer.data_ptr()),
        ctypes.c_void_p(swizzled_producer.data_ptr()),
        ctypes.c_void_p(swizzled_consumer.data_ptr()),
        ctypes.c_void_p(row_checksums.data_ptr()),
        ctypes.c_void_p(swizzled_checksums.data_ptr()),
        ctypes.c_int(threads),
        ctypes.c_int(rounds),
        ctypes.c_int(repetitions),
    )
    torch.cuda.synchronize()

    expected = input_host[:, :rows, :, :]
    row_got = row_output.cpu().numpy().view(np.uint32)
    swizzled_got = swizzled_output.cpu().numpy().view(np.uint32)
    if threads == 32 and rounds <= 64:
        print("debug strides", row_output.stride(), row_got.strides,
              "input", input_host.ravel()[:16].tolist())
    for name, got in (("row-major", row_got), ("k128B-swizzled", swizzled_got)):
        for lane in range(threads):
            tx = lane & 15
            if not np.array_equal(got[lane], expected[:, :, tx, :]):
                mismatch = np.argwhere(got[lane] != expected[:, :, tx, :])[0]
                raise RuntimeError(
                    f"{name} mismatch at lane={lane}, row={mismatch[0]}, "
                    f"word={mismatch[1]}, got={got[lane].tolist()}, "
                    f"expected={expected[:, :, tx, :].tolist()}, "
                    f"first_lanes={got[:4].tolist()}"
                )

    row_prod = row_producer.cpu().numpy().view(np.uint64)
    row_cons = row_consumer.cpu().numpy().view(np.uint64)
    swiz_prod = swizzled_producer.cpu().numpy().view(np.uint64)
    swiz_cons = swizzled_consumer.cpu().numpy().view(np.uint64)
    row_sum = row_checksums.cpu().numpy().view(np.uint32)
    swiz_sum = swizzled_checksums.cpu().numpy().view(np.uint32)
    if not np.array_equal(row_sum, swiz_sum):
        raise RuntimeError("row-major and swizzled checksums differ")

    print(f"[PASS] threads={threads}: row-major and k128B-swizzled payloads match")
    print(
        f"  producer clocks row={percentiles(row_prod)} "
        f"swizzled={percentiles(swiz_prod)} "
        f"ratio_p50={np.median(swiz_prod) / np.median(row_prod):.4f}"
    )
    print(
        f"  consumer clocks row={percentiles(row_cons)} "
        f"swizzled={percentiles(swiz_cons)} "
        f"ratio_p50={np.median(swiz_cons) / np.median(row_cons):.4f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--rounds", type=int, default=2048)
    parser.add_argument("--repetitions", type=int, default=32)
    args = parser.parse_args()
    if args.rounds <= 0 or args.repetitions < 4:
        raise ValueError("--rounds must be positive and --repetitions >= 4")
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    library.run_permuted_smem_probe.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    library.run_permuted_smem_probe.restype = None

    # Warm up compilation, clocks and the first stream launch.  The measured
    # call still alternates row-major/swizzled order internally.
    run_case(library, 32, args.rounds // 4 + 1, 4)
    run_case(library, 64, args.rounds // 4 + 1, 4)
    run_case(library, 32, args.rounds, args.repetitions)
    run_case(library, 64, args.rounds, args.repetitions)
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
