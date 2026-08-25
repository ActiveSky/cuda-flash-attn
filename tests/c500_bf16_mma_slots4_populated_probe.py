#!/usr/bin/env python3
"""Validate all four accumulator components of the C500 BF16-MMA probe.

This driver is a finite capability test, not a production benchmark or
candidate admission.  It intentionally uses a deterministic, positive input
pattern so that a zero c[2]/c[3] cannot be explained by cancellation.
"""

from __future__ import annotations

import argparse
import ctypes

import torch


def _pattern(device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    """Build BF16 inputs with independent row, K, and token dimensions."""

    row = torch.arange(16, device=device, dtype=torch.float32).view(16, 1)
    kk = torch.arange(128, device=device, dtype=torch.float32).view(1, 128)
    token = torch.arange(16, device=device, dtype=torch.float32).view(16, 1)

    # All values are strictly positive.  Row and token terms are large enough
    # to survive BF16 conversion; the K terms make every reduction depend on
    # the full lane-local fragment rather than a repeated one-hot shortcut.
    q = (0.125 + 0.015625 * (row + 1.0) + 0.00390625 * (kk + 1.0)).to(
        torch.bfloat16
    )
    k = (0.25 + 0.0625 * (token + 1.0) + 0.00390625 * (kk + 1.0)).to(
        torch.bfloat16
    )
    return q.contiguous(), k.contiguous()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_bf16_mma_slots4_populated_probe
    launch.argtypes = [ctypes.c_void_p] * 3
    launch.restype = None

    device = torch.device("cuda")
    q, k = _pattern(device)
    q_cpu = q.cpu().float()
    k_cpu = k.cpu().float()

    # This specifically guards the historical row_in_group < 2 mistake.
    # Check all rows as well as rows 8..15 (the former zero-filled groups).
    _require(bool(torch.isfinite(q_cpu).all()), "Q pattern contains NaN/Inf")
    _require(bool(torch.isfinite(k_cpu).all()), "K pattern contains NaN/Inf")
    _require(bool((q_cpu.abs() > 0).all()), "Q pattern unexpectedly contains zero")
    _require(
        bool((q_cpu[1:] != q_cpu[:-1]).any(dim=1).all()),
        "Q rows are not independently distinguishable after BF16 conversion",
    )
    _require(
        bool((q_cpu[:, 1:] != q_cpu[:, :-1]).any(dim=1).all()),
        "Q K coordinates are not independently represented after BF16 conversion",
    )
    _require(
        bool((q_cpu[8:16].abs() > 0).all()),
        "Q rows 8..15 (former A rows 2/3) are not all nonzero",
    )
    _require(
        bool((q_cpu[8:16].amax(dim=1) > 0).all()),
        "Q rows 8..15 do not carry nonzero row signatures",
    )
    _require(
        bool((k_cpu.abs() > 0).all()), "K pattern unexpectedly contains zero"
    )
    _require(
        bool((k_cpu[1:] != k_cpu[:-1]).any(dim=1).all()),
        "K token/column rows are not independently distinguishable",
    )
    _require(
        bool((k_cpu[:, 1:] != k_cpu[:, :-1]).any(dim=1).all()),
        "K coordinates are not independently represented after BF16 conversion",
    )

    actual = torch.full(
        (4, 4, 16, 4), float("nan"), dtype=torch.float32, device=device
    )
    launch(
        ctypes.c_void_p(q.data_ptr()),
        ctypes.c_void_p(k.data_ptr()),
        ctypes.c_void_p(actual.data_ptr()),
    )
    # Synchronization is deliberately in the driver, so launch/runtime errors
    # are surfaced before any mapping claim is made.
    torch.cuda.synchronize()
    actual_cpu = actual.cpu()

    _require(bool(torch.isfinite(actual_cpu).all()), "BF16 MMA produced NaN/Inf")

    # The custom fragment is expected to expose all four row components in
    # c[0..3].  Compute the exact BF16-input/FP32-accumulator reference for
    # every z, ty, tx and component; no absmax-only or aggregate-only check is
    # accepted as evidence of a mapping.
    reference = torch.empty_like(actual_cpu)
    for z in range(4):
        for ty in range(4):
            for tx in range(16):
                token = z * 4 + (tx & 3)
                for component in range(4):
                    q_row = ty + 4 * component
                    reference[z, ty, tx, component] = torch.dot(
                        q_cpu[q_row], k_cpu[token]
                    )

    error = (actual_cpu - reference).abs()
    # Chained BF16 MMA accumulates in FP32.  Allow a small reduction-order
    # margin while retaining a bound far below the dimension/token signatures.
    bound = 1.0e-2 + 5.0e-4 * reference.abs()
    max_error = float(error.max())
    max_ratio = float((error / bound).max())

    # Check every component before the aggregate mapping assertion so a dead
    # c[2]/c[3] is reported explicitly rather than hidden behind one max error.
    component_stats = []
    for component in range(4):
        expected_absmax = float(reference[..., component].abs().max())
        actual_absmax = float(actual_cpu[..., component].abs().max())
        component_error = float(error[..., component].max())
        _require(
            expected_absmax > 0.0,
            f"c[{component}] has no expected nonzero reference value",
        )
        _require(
            actual_absmax > 0.0,
            f"c[{component}] has no observed nonzero value; slot may be inert",
        )
        component_stats.append((expected_absmax, actual_absmax, component_error))

    _require(
        bool((error <= bound).all()),
        "all-four-slot lane mapping disagrees with CPU BF16/FP32 reference: "
        f"max_error={max_error:.6e} max_ratio={max_ratio:.6e}",
    )

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "mapping: lane(z,ty,tx), token=4*z+(tx&3), "
        "c[s]=dot(q[ty+4*s], k[token]), s=0..3"
    )
    print(
        f"q_rows_8_15_absmin={float(q_cpu[8:16].abs().min()):.6e} "
        f"k_absmin={float(k_cpu.abs().min()):.6e}"
    )
    print(
        f"max_error={max_error:.6e} max_error_ratio={max_ratio:.6e}"
    )
    for component, (expected_absmax, actual_absmax, component_error) in enumerate(
        component_stats
    ):
        print(
            f"c[{component}]: expected_absmax={expected_absmax:.6e} "
            f"observed_absmax={actual_absmax:.6e} "
            f"max_error={component_error:.6e}"
        )

    print(
        "[PASS] all four populated BF16-MMA accumulator components match the "
        "lane/row/token reference; this is capability evidence only"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
