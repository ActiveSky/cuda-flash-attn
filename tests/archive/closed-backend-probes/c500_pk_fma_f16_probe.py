#!/usr/bin/env python3
"""Validate native packed FP16 FMA semantics on a real MetaX C500."""

from __future__ import annotations

import argparse
import ctypes

import torch


def f16_words(values: torch.Tensor) -> torch.Tensor:
    return values.to(torch.float16).contiguous().view(torch.int32)


def chained_reference(a: torch.Tensor, b: torch.Tensor, c: torch.Tensor, steps: int) -> torch.Tensor:
    accum = c.to(torch.float16)
    for _ in range(steps):
        accum = (a.float() * b.float() + accum.float()).to(torch.float16)
    return accum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_pk_fma_f16_probe
    launch.argtypes = [ctypes.c_void_p] * 5
    launch.restype = None

    generator = torch.Generator(device="cpu").manual_seed(20260812)
    a = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.float16)
    b = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.float16)
    c = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.float16)
    a_gpu = f16_words(a).cuda()
    b_gpu = f16_words(b).cuda()
    c_gpu = f16_words(c).cuda()
    once_gpu = torch.zeros_like(a_gpu)
    four_gpu = torch.zeros_like(a_gpu)
    launch(
        ctypes.c_void_p(a_gpu.data_ptr()),
        ctypes.c_void_p(b_gpu.data_ptr()),
        ctypes.c_void_p(c_gpu.data_ptr()),
        ctypes.c_void_p(once_gpu.data_ptr()),
        ctypes.c_void_p(four_gpu.data_ptr()),
    )
    torch.cuda.synchronize()

    once = once_gpu.cpu().view(torch.float16).reshape(64, 2)
    four = four_gpu.cpu().view(torch.float16).reshape(64, 2)
    once_ref = chained_reference(a, b, c, 1)
    four_ref = chained_reference(a, b, c, 4)
    once_equal = torch.equal(once.view(torch.int16), once_ref.view(torch.int16))
    four_equal = torch.equal(four.view(torch.int16), four_ref.view(torch.int16))
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"one-step bitwise_equal={once_equal}")
    print(f"four-step bitwise_equal={four_equal}")
    if not once_equal or not four_equal:
        raise RuntimeError("native packed FP16 FMA does not match chained FP16 semantics")
    print("[PASS] packed FP16 FMA is lane-wise and rounds each chained result to FP16")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
