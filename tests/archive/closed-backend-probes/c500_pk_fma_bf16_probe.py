#!/usr/bin/env python3
"""Validate native packed BF16 FMA semantics on a real MetaX C500."""

from __future__ import annotations

import argparse
import ctypes

import torch


def bf16_words(values: torch.Tensor) -> torch.Tensor:
    return values.to(torch.bfloat16).contiguous().view(torch.int32)


def chained_reference(a: torch.Tensor, b: torch.Tensor, c: torch.Tensor, steps: int) -> torch.Tensor:
    accum = c.to(torch.bfloat16)
    for _ in range(steps):
        accum = (a.to(torch.float32) * b.to(torch.float32) + accum.to(torch.float32)).to(
            torch.bfloat16
        )
    return accum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    launch = library.run_pk_fma_bf16_probe
    launch.argtypes = [ctypes.c_void_p] * 5
    launch.restype = None

    generator = torch.Generator(device="cpu").manual_seed(20260812)
    a = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.bfloat16)
    b = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.bfloat16)
    c = torch.randn((64, 2), generator=generator, dtype=torch.float32).to(torch.bfloat16)

    a_gpu = bf16_words(a).cuda()
    b_gpu = bf16_words(b).cuda()
    c_gpu = bf16_words(c).cuda()
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

    once = once_gpu.cpu().view(torch.bfloat16).reshape(64, 2)
    four = four_gpu.cpu().view(torch.bfloat16).reshape(64, 2)
    once_ref = chained_reference(a, b, c, 1)
    four_ref = chained_reference(a, b, c, 4)
    once_equal = torch.equal(once.view(torch.int16), once_ref.view(torch.int16))
    four_equal = torch.equal(four.view(torch.int16), four_ref.view(torch.int16))
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(
        "one-step bitwise_equal={} max_error={:.9e}".format(
            once_equal, float((once.float() - once_ref.float()).abs().max())
        )
    )
    print(
        "four-step bitwise_equal={} max_error={:.9e}".format(
            four_equal, float((four.float() - four_ref.float()).abs().max())
        )
    )
    if not once_equal or not four_equal:
        raise RuntimeError("native packed BF16 FMA does not match chained BF16 semantics")
    print("[PASS] packed BF16 FMA is lane-wise and rounds each chained result to BF16")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
