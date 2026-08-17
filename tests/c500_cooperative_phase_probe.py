#!/usr/bin/env python3
"""Gate cooperative grid phases against the exact #111918 case13 producer."""

from __future__ import annotations

import argparse
import ctypes
import math

import torch


class CooperativePhaseProbeInfo(ctypes.Structure):
    _fields_ = [
        ("device", ctypes.c_int),
        ("cooperative_launch", ctypes.c_int),
        ("multiprocessors", ctypes.c_int),
        ("max_threads_per_multiprocessor", ctypes.c_int),
        ("max_blocks_per_multiprocessor", ctypes.c_int),
        ("max_shared_bytes_per_multiprocessor", ctypes.c_int),
        ("case13_active_blocks_per_multiprocessor", ctypes.c_int),
        ("case13_num_regs", ctypes.c_int),
        ("case13_shared_bytes", ctypes.c_int),
        ("case13_max_threads_per_block", ctypes.c_int),
        ("phase_active_blocks_per_multiprocessor", ctypes.c_int),
        ("phase_num_regs", ctypes.c_int),
        ("phase_shared_bytes", ctypes.c_int),
        ("phase_max_threads_per_block", ctypes.c_int),
        ("cost_baseline_active_blocks_per_multiprocessor", ctypes.c_int),
        ("cost_baseline_num_regs", ctypes.c_int),
        ("cost_baseline_shared_bytes", ctypes.c_int),
        ("cost_sync_active_blocks_per_multiprocessor", ctypes.c_int),
        ("cost_sync_num_regs", ctypes.c_int),
        ("cost_sync_shared_bytes", ctypes.c_int),
    ]


def require_success(status: int, operation: str) -> None:
    if status:
        raise RuntimeError(f"{operation} failed with CUDA bridge status={status}")


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("cannot compute a percentile of no samples")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def format_p10_p50_p90(values: list[float]) -> str:
    return "/".join(f"{percentile(values, q):.3f}" for q in (0.10, 0.50, 0.90))


def measure_block(launch: ctypes._CFuncPtr, iterations: int) -> float:
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    for _ in range(iterations):
        launch()
    end.record()
    end.synchronize()
    return float(start.elapsed_time(end)) / iterations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--case13-grid", type=int, default=520)
    parser.add_argument("--case14-grid", type=int, default=1028)
    parser.add_argument("--barriers-per-launch", type=int, default=32)
    parser.add_argument("--timing-launches", type=int, default=4)
    parser.add_argument("--timing-rounds", type=int, default=9)
    parser.add_argument("--reducer-iterations", type=int, default=20)
    args = parser.parse_args()
    if min(
        args.case13_grid,
        args.case14_grid,
        args.barriers_per_launch,
        args.timing_launches,
        args.timing_rounds,
        args.reducer_iterations,
    ) <= 0:
        raise ValueError("all grid and timing counts must be positive")
    if not torch.cuda.is_available():
        raise RuntimeError("a MetaX CUDA-compatible GPU is required")

    library = ctypes.CDLL(args.library)
    query = library.query_cooperative_phase_probe_info
    query.argtypes = [ctypes.POINTER(CooperativePhaseProbeInfo)]
    query.restype = ctypes.c_int
    launch = library.run_cooperative_phase_probe
    launch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    launch.restype = ctypes.c_int
    launch_cost = library.run_cooperative_phase_cost_probe
    launch_cost.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    launch_cost.restype = ctypes.c_int
    launch_reducer = library.run_case13_reducer_cost_probe
    launch_reducer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    launch_reducer.restype = ctypes.c_int

    info = CooperativePhaseProbeInfo()
    require_success(query(ctypes.byref(info)), "cooperative capability query")

    case13_capacity = (
        info.multiprocessors * info.case13_active_blocks_per_multiprocessor
    )
    phase_capacity = (
        info.multiprocessors * info.phase_active_blocks_per_multiprocessor
    )
    cost_baseline_capacity = (
        info.multiprocessors
        * info.cost_baseline_active_blocks_per_multiprocessor
    )
    cost_sync_capacity = (
        info.multiprocessors * info.cost_sync_active_blocks_per_multiprocessor
    )
    # This is intentionally only a resource-independent upper bound for
    # case14.  It cannot prove case13 infeasible; the exact case13 query above
    # supplies that separate fact.
    case14_thread_only_capacity = info.multiprocessors * (
        info.max_threads_per_multiprocessor // 256
    )

    print(f"GPU: {torch.cuda.get_device_name(info.device)} (device {info.device})")
    print(
        "runtime: cooperative_launch="
        f"{info.cooperative_launch}, SMs={info.multiprocessors}, "
        f"threads/SM={info.max_threads_per_multiprocessor}, "
        f"blocks/SM limit={info.max_blocks_per_multiprocessor}, "
        f"shared/SM={info.max_shared_bytes_per_multiprocessor} B"
    )
    print(
        "case13 exact z8 producer: "
        f"regs={info.case13_num_regs}, shared={info.case13_shared_bytes} B, "
        f"max_threads={info.case13_max_threads_per_block}, "
        f"active_blocks/SM={info.case13_active_blocks_per_multiprocessor}, "
        f"resident_grid={case13_capacity}/{args.case13_grid}"
    )
    print(
        "minimal phase kernel: "
        f"regs={info.phase_num_regs}, shared={info.phase_shared_bytes} B, "
        f"max_threads={info.phase_max_threads_per_block}, "
        f"active_blocks/SM={info.phase_active_blocks_per_multiprocessor}, "
        f"resident_grid={phase_capacity}/{args.case13_grid}"
    )
    print(
        "barrier-cost kernels: baseline "
        f"regs={info.cost_baseline_num_regs}, shared={info.cost_baseline_shared_bytes} B, "
        f"resident_grid={cost_baseline_capacity}/{args.case13_grid}; sync "
        f"regs={info.cost_sync_num_regs}, shared={info.cost_sync_shared_bytes} B, "
        f"resident_grid={cost_sync_capacity}/{args.case13_grid}"
    )
    print(
        "case14 independent thread-only upper bound: "
        f"{case14_thread_only_capacity}/{args.case14_grid} blocks"
    )

    if info.cooperative_launch != 1:
        print("[CLOSED] P2-2: cudaDevAttrCooperativeLaunch is not enabled; no launch attempted")
        return 0
    if case13_capacity < args.case13_grid:
        print(
            "[CLOSED] P2-2: the exact current case13 producer cannot fully "
            "reside, so no grid.sync() launch or barrier-cost measurement is valid"
        )
        return 0
    if phase_capacity < args.case13_grid:
        raise RuntimeError(
            "the minimal phase kernel cannot resident-launch the already "
            "admissible case13 grid"
        )

    if min(cost_baseline_capacity, cost_sync_capacity) < args.case13_grid:
        raise RuntimeError(
            "the barrier-cost kernels cannot resident-launch the already "
            "admissible case13 grid"
        )

    phase_one = torch.full(
        (args.case13_grid,), -1, dtype=torch.int32, device="cuda"
    )
    phase_two = torch.full_like(phase_one, -1)
    require_success(
        launch(
            ctypes.c_void_p(phase_one.data_ptr()),
            ctypes.c_void_p(phase_two.data_ptr()),
            args.case13_grid,
        ),
        "cooperative phase launch",
    )
    torch.cuda.synchronize()

    expected_phase_one = torch.arange(
        1, args.case13_grid + 1, dtype=torch.int32, device="cuda"
    )
    if not torch.equal(phase_one, expected_phase_one):
        raise RuntimeError("phase-one writes did not survive cooperative launch")
    if not torch.equal(phase_two, torch.ones_like(phase_two)):
        bad = int(torch.nonzero(phase_two != 1, as_tuple=False)[0].item())
        raise RuntimeError(
            f"grid.sync() phase visibility mismatch at block={bad}: "
            f"got={int(phase_two[bad].item())}"
        )
    print(
        f"[PASS] cooperative grid.sync() phase semantics at {args.case13_grid} "
        "fully resident blocks"
    )

    # One barrier is timed as the alternating delta of two cooperative kernels
    # with identical launch geometry.  The current exact reducer is timed on
    # finite dummy partials only as the stop-condition reference scale.
    sink = torch.zeros(args.case13_grid, dtype=torch.uint32, device="cuda")
    partial_slots = 65 * 32
    partial_m = torch.zeros(partial_slots, dtype=torch.float32, device="cuda")
    partial_l = torch.zeros_like(partial_m)
    partial_acc = torch.zeros(
        partial_slots * 128, dtype=torch.float32, device="cuda"
    )
    reducer_out = torch.empty(32 * 128, dtype=torch.bfloat16, device="cuda")
    reducer_lengths = torch.full((1,), 58966, dtype=torch.int32, device="cuda")

    def run_cost(with_grid_sync: int) -> None:
        require_success(
            launch_cost(
                ctypes.c_void_p(sink.data_ptr()),
                args.case13_grid,
                args.barriers_per_launch,
                with_grid_sync,
            ),
            "cooperative barrier-cost launch",
        )

    def run_reducer() -> None:
        require_success(
            launch_reducer(
                ctypes.c_void_p(partial_m.data_ptr()),
                ctypes.c_void_p(partial_l.data_ptr()),
                ctypes.c_void_p(partial_acc.data_ptr()),
                ctypes.c_void_p(reducer_out.data_ptr()),
                ctypes.c_void_p(reducer_lengths.data_ptr()),
            ),
            "case13 reducer cost launch",
        )

    for _ in range(2):
        run_cost(0)
        run_cost(1)
        run_reducer()
    torch.cuda.synchronize()

    barrier_us: list[float] = []
    reducer_us: list[float] = []
    barrier_to_reducer: list[float] = []
    for round_index in range(args.timing_rounds):
        if round_index % 2 == 0:
            baseline_ms = measure_block(
                lambda: run_cost(0), args.timing_launches
            )
            sync_ms = measure_block(lambda: run_cost(1), args.timing_launches)
        else:
            sync_ms = measure_block(lambda: run_cost(1), args.timing_launches)
            baseline_ms = measure_block(
                lambda: run_cost(0), args.timing_launches
            )
        reducer_ms = measure_block(run_reducer, args.reducer_iterations)
        additional_us = (
            (sync_ms - baseline_ms) * 1000.0 / args.barriers_per_launch
        )
        reducer_launch_us = reducer_ms * 1000.0
        barrier_us.append(additional_us)
        reducer_us.append(reducer_launch_us)
        barrier_to_reducer.append(additional_us / reducer_launch_us)

    if not all(math.isfinite(value) for value in barrier_us + reducer_us):
        raise RuntimeError("non-finite cooperative barrier timing")
    print(
        "one grid.sync() additional cost (us, p10/p50/p90): "
        f"{format_p10_p50_p90(barrier_us)}"
    )
    print(
        "exact current case13 reducer launch (us, p10/p50/p90): "
        f"{format_p10_p50_p90(reducer_us)}"
    )
    print(
        "barrier/reducer ratio (p10/p50/p90): "
        f"{format_p10_p50_p90(barrier_to_reducer)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
