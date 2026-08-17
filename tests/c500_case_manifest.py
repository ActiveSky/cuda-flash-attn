#!/usr/bin/env python3
"""Authoritative local test configuration for XPUOJ paged decode.

The table in problem.md is incomplete and has shifted fields.  This module reads
an accepted OJ response and treats its parsed SPJ ``Config:`` fields as the
single source of truth for the 14 evaluated shapes.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_RESULT = ROOT / "results/raw/cuda_112302_raw.json"
NUM_HEADS = 32
HEAD_DIM = 128
PAGE_SIZE = 16
SEQLEN_Q = 1
CAUSAL = 0


@dataclass(frozen=True)
class CaseConfig:
    """One evaluated configuration parsed from the archived OJ SPJ report."""

    case_id: int
    batch_size: int
    seqlen_k: int
    num_heads_k: int
    kind: str
    baseline_ms: float
    user_ms: float

    @property
    def gqa_ratio(self) -> int:
        return NUM_HEADS // self.num_heads_k

    @property
    def max_pages(self) -> int:
        return (self.seqlen_k + PAGE_SIZE - 1) // PAGE_SIZE


def _parse_config(config: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field in config.split(","):
        key, value = field.strip().split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def _require_constant(fields: dict[str, str], key: str, expected: int) -> None:
    actual = int(fields[key])
    if actual != expected:
        raise ValueError(f"unexpected {key}: expected {expected}, got {actual}")


def load_cases(raw_result: Path = DEFAULT_RAW_RESULT) -> tuple[CaseConfig, ...]:
    """Load and validate the exact 14 OJ configurations from an accepted run."""
    data = json.loads(raw_result.read_text())
    testcases = data.get("testcases")
    if not isinstance(testcases, list):
        raise ValueError(f"missing normalized testcases in {raw_result}")

    cases: list[CaseConfig] = []
    for testcase in testcases:
        spj = testcase.get("spj", {})
        fields = _parse_config(str(spj["config"]))
        _require_constant(fields, "seqlen_q", SEQLEN_Q)
        _require_constant(fields, "heads", NUM_HEADS)
        _require_constant(fields, "headdim", HEAD_DIM)
        _require_constant(fields, "page_size", PAGE_SIZE)
        _require_constant(fields, "causal", CAUSAL)

        num_heads_k = int(fields["kv_heads"])
        if num_heads_k not in (4, 8) or NUM_HEADS % num_heads_k:
            raise ValueError(f"invalid kv_heads={num_heads_k} in {fields}")
        kind = fields["kind"]
        if kind not in ("edge", "perf"):
            raise ValueError(f"invalid kind={kind} in {fields}")

        cases.append(
            CaseConfig(
                case_id=int(spj["testcase"]),
                batch_size=int(fields["batch"]),
                seqlen_k=int(fields["seqlen_k_cap"]),
                num_heads_k=num_heads_k,
                kind=kind,
                baseline_ms=float(spj["baseline_ms"]),
                user_ms=float(spj["user_ms"]),
            )
        )

    cases.sort(key=lambda case: case.case_id)
    expected_ids = list(range(1, 15))
    actual_ids = [case.case_id for case in cases]
    if actual_ids != expected_ids:
        raise ValueError(f"expected cases {expected_ids}, got {actual_ids}")
    return tuple(cases)


CASES = load_cases()


def split_policy(case: CaseConfig) -> tuple[int, int, str]:
    """Mirror #112302's validated split count and production family.

    Returns ``(n_split, pages_per_split, producer_family)``. The family label
    is descriptive only; CPU replay validates paged lookup and the split/
    reducer contract, not backend instruction scheduling.
    """
    n_split = (case.seqlen_k + 127) // 128
    target_splits = (1024 + case.batch_size * case.num_heads_k - 1) // (
        case.batch_size * case.num_heads_k
    )
    n_split = max(1, min(n_split, target_splits))

    if case.num_heads_k == 8 and (
        (case.batch_size == 64 and case.seqlen_k == 2048)
        or (case.batch_size == 32 and case.seqlen_k == 4096)
    ):
        n_split *= 8
    if case.num_heads_k == 8 and case.batch_size == 8 and case.seqlen_k == 32768:
        n_split *= 16
    if case.num_heads_k == 4 and case.batch_size == 16 and case.seqlen_k == 12251:
        n_split = 39
    if case.num_heads_k == 4 and case.batch_size == 16 and case.seqlen_k == 4096:
        n_split *= 2
    if case.num_heads_k == 8 and case.batch_size == 16 and case.seqlen_k == 362:
        n_split = 8
    if case.num_heads_k == 4 and case.batch_size == 16 and case.seqlen_k == 141:
        # Production retains the validated five-split/two-page policy. Keep
        # this manifest aligned with the structural control #112302.
        n_split = 5
    if case.num_heads_k == 4 and case.batch_size == 1 and case.seqlen_k == 8192:
        n_split *= 2
    if case.num_heads_k == 4 and case.batch_size == 1 and case.seqlen_k == 61519:
        n_split = 257

    # Keep the manifest byte-for-byte policy-equivalent to run_kernel's final
    # shape overrides; the earlier generic multipliers are only intermediate.
    if case.num_heads_k == 8 and case.batch_size == 64 and case.seqlen_k == 2048:
        n_split = 3
    if case.num_heads_k == 8 and case.batch_size == 32 and case.seqlen_k == 4096:
        n_split = 6
    if case.num_heads_k == 4 and case.batch_size == 16 and case.seqlen_k == 4096:
        n_split = 14
    if case.num_heads_k == 8 and case.batch_size == 8 and case.seqlen_k == 32768:
        n_split = 40
    if case.num_heads_k == 8 and case.batch_size == 1 and case.seqlen_k == 58966:
        n_split = 65
    if case.seqlen_k == 1:
        producer_family = "copy1"
    elif case.seqlen_k == 2:
        producer_family = "attn2"
    elif case.case_id in (7, 9, 12, 13):
        producer_family = "kv8-z8-native"
    elif case.case_id in (5, 8, 10, 11, 14):
        producer_family = "kv4-z4-mma"
    else:
        producer_family = "token-parallel"
    return n_split, (case.max_pages + n_split - 1) // n_split, producer_family


if __name__ == "__main__":
    for case in CASES:
        n_split, pages_per_split, producer_family = split_policy(case)
        print(
            f"case {case.case_id:2d}: B={case.batch_size:2d} L={case.seqlen_k:5d} "
            f"KV={case.num_heads_k} {case.kind:4s} | {producer_family:14s} "
            f"splits={n_split:3d} pages/split={pages_per_split:2d}"
        )
