#!/usr/bin/env python3
"""Identify the xcore1000 b0..b3-to-FP32 conversion semantics."""

from __future__ import annotations

import argparse
import ctypes

import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    args = parser.parse_args()
    library = ctypes.CDLL(args.library)
    launch = library.run_bx_cast_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    launch.restype = None

    examples = torch.tensor(
        [0x00000000, 0x01020304, 0x7F80FF01, 0x3F803F00, 0xBF80C000],
        dtype=torch.uint32,
    )
    words = torch.zeros((64,), dtype=torch.uint32)
    words[: examples.numel()] = examples
    words_gpu = words.cuda()
    out_gpu = torch.full((64, 4), float("nan"), dtype=torch.float32, device="cuda")
    launch(ctypes.c_void_p(words_gpu.data_ptr()), ctypes.c_void_p(out_gpu.data_ptr()))
    torch.cuda.synchronize()
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    for word, values in zip(examples.tolist(), out_gpu.cpu()[: examples.numel()].tolist()):
        print(f"0x{word:08x} -> {values}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
