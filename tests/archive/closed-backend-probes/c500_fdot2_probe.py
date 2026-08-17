#!/usr/bin/env python3
"""Validate packed FP16/BF16 dot-to-FP32 support on a real C500."""

from __future__ import annotations

import argparse
import ctypes

import numpy as np
import torch


def packed_words(values: torch.Tensor) -> torch.Tensor:
    """Return contiguous pairs of 16-bit values viewed as uint32 words."""
    return values.contiguous().view(torch.int32)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_fdot2_capability_probe
    launch.argtypes = [ctypes.c_void_p] * 6
    launch.restype = None

    generator = torch.Generator(device="cpu").manual_seed(20260812)
    a = torch.randn((64, 2), generator=generator, dtype=torch.float32)
    b = torch.randn((64, 2), generator=generator, dtype=torch.float32)
    seeds = torch.randn((64,), generator=generator, dtype=torch.float32)

    f16_words = torch.stack(
        (packed_words(a.to(torch.float16)), packed_words(b.to(torch.float16))),
        dim=1,
    ).reshape(-1).cuda()
    bf16_words = torch.stack(
        (packed_words(a.to(torch.bfloat16)), packed_words(b.to(torch.bfloat16))),
        dim=1,
    ).reshape(-1).cuda()
    seeds_gpu = seeds.cuda()
    f16_out = torch.full_like(seeds_gpu, float("nan"))
    bf16_out = torch.full_like(seeds_gpu, float("nan"))
    capability = torch.full((2,), -1, dtype=torch.int32, device="cuda")

    launch(
        ctypes.c_void_p(f16_words.data_ptr()),
        ctypes.c_void_p(bf16_words.data_ptr()),
        ctypes.c_void_p(seeds_gpu.data_ptr()),
        ctypes.c_void_p(f16_out.data_ptr()),
        ctypes.c_void_p(bf16_out.data_ptr()),
        ctypes.c_void_p(capability.data_ptr()),
    )
    torch.cuda.synchronize()

    cap = capability.cpu().tolist()
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"compile capability: f16={cap[0]} bf16={cap[1]}")

    if cap[0]:
        ref = seeds + (
            a.to(torch.float16).float() * b.to(torch.float16).float()
        ).sum(dim=1)
        error = (f16_out.cpu() - ref).abs()
        print(f"f16 max_abs_error={float(error.max()):.9e}")
        if not np.allclose(f16_out.cpu().numpy(), ref.numpy(), atol=2e-6, rtol=2e-6):
            raise RuntimeError("FP16 fdot2 does not match FP32 accumulation")

    if cap[1]:
        ref = seeds + (
            a.to(torch.bfloat16).float() * b.to(torch.bfloat16).float()
        ).sum(dim=1)
        error = (bf16_out.cpu() - ref).abs()
        print(f"bf16 max_abs_error={float(error.max()):.9e}")
        if not np.allclose(bf16_out.cpu().numpy(), ref.numpy(), atol=2e-6, rtol=2e-6):
            raise RuntimeError("BF16 fdot2 does not match FP32 accumulation")

    if not any(cap):
        print("[UNAVAILABLE] no packed floating dot builtin is exposed")
    else:
        print("[PASS] exposed fdot2 variants preserve an FP32 accumulator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
