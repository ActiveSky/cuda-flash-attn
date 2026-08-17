#!/usr/bin/env python3
"""Validate row-local 64-lane vote semantics for lazy page-max guards."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def pattern(pattern_id: int, tx: int, ty: int, tz: int) -> bool:
    if pattern_id == 0:
        return ty == 1 and tx == 2
    if pattern_id == 1:
        return tz == 0 and ty == 3 and tx == 15
    if pattern_id == 2:
        return False
    return tx == ((ty * 3 + tz * 5) & 15)


def expected(pattern_id: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    expected_any = np.zeros((4, 128), dtype=np.int32)
    expected_full_wave_any = np.zeros((4, 128), dtype=np.int32)
    expected_ballot = np.zeros((4, 128), dtype=np.uint64)
    for tz in range(2):
        full_wave_hits = [
            any(pattern(p, tx, ty, tz) for ty in range(4) for tx in range(16))
            for p in range(4)
        ]
        for ty in range(4):
            bits_by_pattern: list[int] = []
            for pattern_id_inner in range(4):
                bits = 0
                for tx in range(16):
                    if pattern(pattern_id_inner, tx, ty, tz):
                        bits |= 1 << (ty * 16 + tx)
                bits_by_pattern.append(bits)
            for tx in range(16):
                linear_tid = (tz * 4 + ty) * 16 + tx
                bits = bits_by_pattern[pattern_id]
                expected_ballot[pattern_id, linear_tid] = bits
                expected_any[pattern_id, linear_tid] = int(bits != 0)
                expected_full_wave_any[pattern_id, linear_tid] = int(
                    full_wave_hits[pattern_id]
                )
    return expected_any, expected_full_wave_any, expected_ballot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_lazy_page_guard_probe
    launch.argtypes = [ctypes.c_void_p] * 7
    launch.restype = None

    any_out = torch.empty((4, 128), dtype=torch.int32, device="cuda")
    full_wave_any_out = torch.empty_like(any_out)
    ballot_out = torch.empty((4, 128), dtype=torch.int64, device="cuda")
    lane_ids = torch.empty((128,), dtype=torch.int32, device="cuda")
    scores = torch.arange(256, dtype=torch.float32, device="cuda")
    references = torch.zeros_like(scores)
    output = torch.empty_like(scores)
    launch(
        ctypes.c_void_p(any_out.data_ptr()),
        ctypes.c_void_p(full_wave_any_out.data_ptr()),
        ctypes.c_void_p(ballot_out.data_ptr()),
        ctypes.c_void_p(lane_ids.data_ptr()),
        ctypes.c_void_p(scores.data_ptr()),
        ctypes.c_void_p(references.data_ptr()),
        ctypes.c_void_p(output.data_ptr()),
    )
    torch.cuda.synchronize()

    got_lanes = lane_ids.cpu().numpy().astype(np.uint32, copy=False)
    expected_lanes = np.arange(128, dtype=np.uint32) & 63
    if not np.array_equal(got_lanes, expected_lanes):
        raise RuntimeError(
            f"unexpected physical lane map: got={got_lanes.tolist()}"
        )

    got_any = any_out.cpu().numpy()
    got_full_wave_any = full_wave_any_out.cpu().numpy()
    got_ballot = ballot_out.cpu().numpy().view(np.uint64)
    for pattern_id in range(4):
        expected_any, expected_full_wave_any, expected_ballot = expected(pattern_id)
        if not np.array_equal(got_any[pattern_id], expected_any[pattern_id]):
            raise RuntimeError(
                f"__any_sync row isolation mismatch for pattern={pattern_id}"
            )
        if not np.array_equal(
            got_full_wave_any[pattern_id], expected_full_wave_any[pattern_id]
        ):
            raise RuntimeError(
                f"__any_sync full-wave mismatch for pattern={pattern_id}"
            )
        if not np.array_equal(
            got_ballot[pattern_id], expected_ballot[pattern_id]
        ):
            mismatch = np.flatnonzero(
                got_ballot[pattern_id] != expected_ballot[pattern_id]
            )[0]
            raise RuntimeError(
                "__ballot_sync row-mask mismatch for pattern="
                f"{pattern_id}, lane={mismatch}, got="
                f"0x{got_ballot[pattern_id, mismatch]:016x}, expected="
                f"0x{expected_ballot[pattern_id, mismatch]:016x}"
            )
        print(
            f"[PASS] pattern {pattern_id}: row-local any/ballot and "
            "full-wave any semantics"
        )

    # The guard-shaped kernel has a positive score in every row, so it should
    # select score rather than reference.  This also catches a launch or ABI
    # mismatch independently of the semantic kernel.
    if not torch.equal(output, scores):
        raise RuntimeError("guard codegen probe did not take the expected path")
    print("[PASS] physical z waves reset lane IDs and guard-shaped branch runs")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
