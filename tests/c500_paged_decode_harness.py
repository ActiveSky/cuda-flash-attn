#!/usr/bin/env python3
"""Local GPU correctness harness for the XPUOJ paged-KV decode kernel.

This loads a MACA-built shared object with ctypes, invokes its ``run_kernel``
entry point with the exact OJ ABI, and compares against the installed
``flash_attn_with_kvcache`` reference.  Test shapes are obtained exclusively
from :mod:`c500_case_manifest`, which parses an accepted OJ SPJ response.

Examples:
    tools/build_local_maca.sh
    python tests/c500_paged_decode_harness.py
    python tests/c500_paged_decode_harness.py --cases 7,9 --benchmark
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Iterable

import torch

from c500_case_manifest import CASES, CaseConfig, HEAD_DIM, NUM_HEADS, PAGE_SIZE


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = ROOT / "build/cuda_maca_version.so"
ATOL = 1.6e-2
RTOL = 1.6e-2


@dataclass
class PagedDecodeInput:
    """CUDA tensors matching the submission ABI for one OJ case."""

    case: CaseConfig
    q: torch.Tensor
    k_cache: torch.Tensor
    v_cache: torch.Tensor
    output: torch.Tensor
    cache_seqlens: torch.Tensor
    block_table: torch.Tensor

    @property
    def num_blocks(self) -> int:
        return self.k_cache.shape[0]


@dataclass(frozen=True)
class CorrectnessResult:
    case_id: int
    passed: bool
    matched_ratio: float
    max_error: float
    max_outlier_ratio: float
    finite: bool


@dataclass(frozen=True)
class TimingResult:
    label: str
    samples_ms: tuple[float, ...]

    @property
    def p10_ms(self) -> float:
        return _percentile(self.samples_ms, 0.10)

    @property
    def p50_ms(self) -> float:
        return _percentile(self.samples_ms, 0.50)

    @property
    def p90_ms(self) -> float:
        return _percentile(self.samples_ms, 0.90)


def _percentile(values: Iterable[float], fraction: float) -> float:
    values = sorted(values)
    if not values:
        raise ValueError("cannot compute a percentile of no samples")
    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    weight = position - lower
    return values[lower] * (1.0 - weight) + values[upper] * weight


def parse_case_ids(value: str) -> tuple[int, ...]:
    if value == "all":
        return tuple(case.case_id for case in CASES)
    ids = tuple(int(part) for part in value.split(",") if part.strip())
    known = {case.case_id for case in CASES}
    unknown = sorted(set(ids) - known)
    if not ids or unknown:
        raise argparse.ArgumentTypeError(
            f"cases must be a comma-separated subset of 1-14; unknown: {unknown}"
        )
    return ids


def selected_cases(case_ids: Iterable[int]) -> tuple[CaseConfig, ...]:
    wanted = set(case_ids)
    return tuple(case for case in CASES if case.case_id in wanted)


def require_maca_gpu() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("a CUDA/MACA device is required")
    name = torch.cuda.get_device_name()
    if "MetaX" not in name:
        print(f"warning: expected MetaX C500, found {name}", file=sys.stderr)


def load_kernel(path: Path) -> ctypes._CFuncPtr:
    if not path.is_file():
        raise FileNotFoundError(
            f"kernel library is missing: {path}; run tools/build_local_maca.sh first"
        )
    library = ctypes.CDLL(str(path), mode=ctypes.RTLD_LOCAL)
    run_kernel = library.run_kernel
    run_kernel.restype = None
    run_kernel.argtypes = [ctypes.c_void_p] * 6 + [ctypes.c_int64] * 9
    # Retain the CDLL through the function reference. ctypes functions normally
    # do this, but an explicit attribute makes the ownership obvious.
    run_kernel._library = library
    return run_kernel


def _boundary_length(case: CaseConfig, index: int) -> int:
    candidates = (1, 15, 16, 17, case.seqlen_k - 1, case.seqlen_k)
    return max(1, min(case.seqlen_k, candidates[index % len(candidates)]))


def make_input(
    case: CaseConfig,
    *,
    seed: int,
    length_mode: str = "boundary",
) -> PagedDecodeInput:
    """Construct an OJ-layout input with legal page IDs in padding entries."""
    require_maca_gpu()
    if length_mode not in ("boundary", "random", "full"):
        raise ValueError(f"unsupported length mode: {length_mode}")

    # Reset both CPU and C500 RNGs per case so a failure can be reproduced from
    # the reported case ID and seed alone. The CPU generator is kept separate
    # for page-table construction.
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    generator = torch.Generator(device="cpu").manual_seed(seed)
    pages_per_batch = case.max_pages
    num_blocks = case.batch_size * pages_per_batch
    device = torch.device("cuda")

    q = torch.randn(
        (case.batch_size, 1, NUM_HEADS, HEAD_DIM),
        device=device,
        dtype=torch.bfloat16,
    )
    k_cache = torch.randn(
        (num_blocks, PAGE_SIZE, case.num_heads_k, HEAD_DIM),
        device=device,
        dtype=torch.bfloat16,
    )
    v_cache = torch.randn(
        (num_blocks, PAGE_SIZE, case.num_heads_k, HEAD_DIM),
        device=device,
        dtype=torch.bfloat16,
    )

    if length_mode == "full":
        lengths_cpu = torch.full((case.batch_size,), case.seqlen_k, dtype=torch.int32)
    elif length_mode == "boundary":
        lengths_cpu = torch.tensor(
            [_boundary_length(case, batch_index) for batch_index in range(case.batch_size)],
            dtype=torch.int32,
        )
    else:
        lengths_cpu = torch.randint(
            1,
            case.seqlen_k + 1,
            (case.batch_size,),
            generator=generator,
            dtype=torch.int32,
        )

    table_cpu = torch.empty((case.batch_size, pages_per_batch), dtype=torch.int32)
    for batch_index, seqlen in enumerate(lengths_cpu.tolist()):
        # Every row has a fresh full-pool permutation. The first valid entries
        # are used by this sequence; padding remains legal but must never load.
        permutation = torch.randperm(num_blocks, generator=generator, dtype=torch.int64)
        table_cpu[batch_index] = permutation[:pages_per_batch].to(torch.int32)
        valid_pages = (seqlen + PAGE_SIZE - 1) // PAGE_SIZE
        if valid_pages < pages_per_batch:
            padding = table_cpu[batch_index, valid_pages:]
            if torch.any(padding < 0) or torch.any(padding >= num_blocks):
                raise AssertionError("padding must contain valid physical page IDs")

    output = torch.full_like(q, float("nan"))
    return PagedDecodeInput(
        case=case,
        q=q.contiguous(),
        k_cache=k_cache.contiguous(),
        v_cache=v_cache.contiguous(),
        output=output.contiguous(),
        cache_seqlens=lengths_cpu.to(device=device).contiguous(),
        block_table=table_cpu.to(device=device).contiguous(),
    )


def run_kernel(kernel: ctypes._CFuncPtr, inputs: PagedDecodeInput) -> None:
    case = inputs.case
    kernel(
        ctypes.c_void_p(inputs.q.data_ptr()),
        ctypes.c_void_p(inputs.k_cache.data_ptr()),
        ctypes.c_void_p(inputs.v_cache.data_ptr()),
        ctypes.c_void_p(inputs.output.data_ptr()),
        ctypes.c_void_p(inputs.cache_seqlens.data_ptr()),
        ctypes.c_void_p(inputs.block_table.data_ptr()),
        ctypes.c_int64(case.batch_size),
        ctypes.c_int64(case.seqlen_k),
        ctypes.c_int64(1),
        ctypes.c_int64(NUM_HEADS),
        ctypes.c_int64(case.num_heads_k),
        ctypes.c_int64(HEAD_DIM),
        ctypes.c_int64(PAGE_SIZE),
        ctypes.c_int64(inputs.num_blocks),
        ctypes.c_int64(0),
    )


def flash_reference(inputs: PagedDecodeInput) -> torch.Tensor:
    from flash_attn import flash_attn_with_kvcache

    return flash_attn_with_kvcache(
        inputs.q,
        inputs.k_cache,
        inputs.v_cache,
        None,
        None,
        cache_seqlens=inputs.cache_seqlens,
        cache_batch_idx=None,
        block_table=inputs.block_table,
        causal=False,
        window_size=(-1, -1),
        rotary_interleaved=False,
        alibi_slopes=None,
        num_splits=0,
    )


def check_correctness(
    kernel: ctypes._CFuncPtr,
    inputs: PagedDecodeInput,
) -> CorrectnessResult:
    """Run the candidate and reproduce the OJ's numerical acceptance rule."""
    reference = flash_reference(inputs)
    torch.cuda.synchronize()
    inputs.output.fill_(float("nan"))
    run_kernel(kernel, inputs)
    torch.cuda.synchronize()

    actual = inputs.output.float()
    reference = reference.float()
    finite = bool(torch.isfinite(actual).all().item())
    difference = (actual - reference).abs()
    tolerance = ATOL + RTOL * reference.abs()
    matched_ratio = float((difference <= tolerance).float().mean().item())
    max_error = float(difference.max().item())
    max_outlier_ratio = float((difference / tolerance).max().item())
    required_ratio = 1.0 if inputs.case.kind == "edge" else 0.99
    passed = finite and matched_ratio >= required_ratio and max_outlier_ratio <= 8.0
    return CorrectnessResult(
        case_id=inputs.case.case_id,
        passed=passed,
        matched_ratio=matched_ratio,
        max_error=max_error,
        max_outlier_ratio=max_outlier_ratio,
        finite=finite,
    )


def time_callable(
    label: str,
    callback: Callable[[], None],
    *,
    warmup: int,
    iterations: int,
    samples: int,
) -> TimingResult:
    """Measure device time only; warm-up excludes static allocation/JIT work."""
    for _ in range(warmup):
        callback()
    torch.cuda.synchronize()

    timings: list[float] = []
    for _ in range(samples):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        for _ in range(iterations):
            callback()
        end.record()
        end.synchronize()
        timings.append(float(start.elapsed_time(end)) / iterations)
    return TimingResult(label=label, samples_ms=tuple(timings))


def benchmark_case(
    kernel: ctypes._CFuncPtr,
    inputs: PagedDecodeInput,
    *,
    warmup: int,
    iterations: int,
    samples: int,
) -> tuple[TimingResult, TimingResult]:
    """Time the submitted kernel and OJ-equivalent FlashAttention reference."""
    candidate = time_callable(
        "candidate",
        lambda: run_kernel(kernel, inputs),
        warmup=warmup,
        iterations=iterations,
        samples=samples,
    )
    reference_output = torch.empty_like(inputs.output)

    def reference_callback() -> None:
        reference_output.copy_(flash_reference(inputs))

    reference = time_callable(
        "flash_attn",
        reference_callback,
        warmup=warmup,
        iterations=iterations,
        samples=samples,
    )
    return candidate, reference


def print_correctness(result: CorrectnessResult, case: CaseConfig, length_mode: str) -> None:
    status = "PASS" if result.passed else "FAIL"
    print(
        f"[{status}] case {case.case_id:2d} B={case.batch_size:2d} L={case.seqlen_k:5d} "
        f"KV={case.num_heads_k} lengths={length_mode:8s} "
        f"match={result.matched_ratio:.6f} max_error={result.max_error:.6e} "
        f"max_tol_ratio={result.max_outlier_ratio:.3f} finite={result.finite}"
    )


def print_timing(case: CaseConfig, candidate: TimingResult, reference: TimingResult) -> None:
    ratio = candidate.p50_ms / reference.p50_ms
    print(
        f"[BENCH] case {case.case_id:2d} B={case.batch_size:2d} L={case.seqlen_k:5d} "
        f"KV={case.num_heads_k} | candidate p10/p50/p90="
        f"{candidate.p10_ms:.4f}/{candidate.p50_ms:.4f}/{candidate.p90_ms:.4f} ms | "
        f"flash_attn={reference.p10_ms:.4f}/{reference.p50_ms:.4f}/{reference.p90_ms:.4f} ms | "
        f"candidate/reference={ratio:.3f}x"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--cases", type=parse_case_ids, default=tuple(case.case_id for case in CASES))
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--lengths", choices=("boundary", "random", "full"), default="boundary")
    parser.add_argument(
        "--full-length",
        action="store_true",
        help="run every selected case at cache capacity (equivalent to --lengths full)",
    )
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--samples", type=int, default=15)
    args = parser.parse_args(argv)

    if min(args.warmup, args.iterations, args.samples) < 1:
        parser.error("warmup, iterations and samples must all be positive")

    require_maca_gpu()
    length_mode = "full" if args.full_length else args.lengths
    print(f"GPU: {torch.cuda.get_device_name()} | torch={torch.__version__}")
    kernel = load_kernel(args.library)
    all_passed = True
    for case in selected_cases(args.cases):
        inputs = make_input(case, seed=args.seed + case.case_id, length_mode=length_mode)
        try:
            result = check_correctness(kernel, inputs)
            print_correctness(result, case, length_mode)
            all_passed = all_passed and result.passed
            if args.benchmark and result.passed:
                candidate, reference = benchmark_case(
                    kernel,
                    inputs,
                    warmup=args.warmup,
                    iterations=args.iterations,
                    samples=args.samples,
                )
                print_timing(case, candidate, reference)
        finally:
            # Long cases allocate up to several GiB of K/V. Release each case
            # before constructing the next one so --cases all cannot OOM from
            # PyTorch's caching allocator retaining every prior capacity.
            del inputs
            torch.cuda.empty_cache()

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
