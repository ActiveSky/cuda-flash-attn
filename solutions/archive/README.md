# Solution experiment archive

This directory stores historical/rejected candidates and byte-exact XPUOJ C500 submission sources.

## Active source roles

- [`2026-08-08-submissions/cuda_105952.cpp`](2026-08-08-submissions/cuda_105952.cpp) — the immutable source of the currently selected best submission and the default optimization control.
- [`../cuda_maca_optimized.cpp`](../cuda_maca_optimized.cpp) — the mutable optimization and iteration working file. It may diverge while an experiment is active.
- [`../cuda_maca_version.cpp`](../cuda_maca_version.cpp) — the earlier maintenance/control implementation, retained for historical comparison.

There is intentionally no separate `best` or `frozen` source copy. When a new best is selected, use that submission's immutable snapshot directly and update the current-best references in `AGENTS.md` and `results/cuda_result.md`.

## Archive collections

- [`SUBMISSIONS.md`](SUBMISSIONS.md) — generated manifest for all 108 raw OJ records currently in `results/raw/`, including submission time, status, score, SHA-256, exact source snapshot, and raw result links.
- [`2026-08-08-submissions/`](2026-08-08-submissions/) — 22 byte-exact submitted sources, one `cuda_<id>.cpp` file per attempt.
- [`2026-08-07-submissions/`](2026-08-07-submissions/) — 72 byte-exact submitted sources, one `cuda_<id>.cpp` file per attempt.
- [`2026-08-06-submissions/`](2026-08-06-submissions/) — 14 byte-exact submitted sources, one `cuda_<id>.cpp` file per attempt.
- [`2026-08-07-experiments/`](2026-08-07-experiments/) — 64 historical CUDA candidates from the 2026-08-07 optimization cycle. Historical sources are tied to experiments or submissions in `results/cuda_result.md`; raw OJ responses are in `results/raw/`.

The `*-submissions/` collections are immutable provenance snapshots. They deliberately keep a separate file for every attempt even when two submissions used identical code. Files are extracted without adding or removing a trailing newline, so their SHA-256 hashes match `raw_detail.content.code` exactly. Regenerate the collections and manifest from the repository root with:

```bash
python3 tools/archive_cuda_submissions.py
```

Promote a new best only after evaluating the complete OJ result. Keep its immutable `*-submissions/cuda_<id>.cpp` snapshot in place and update documentation to point to it; do not create another source copy.

### Important rejected candidates in the 2026-08-07 collection

- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_kv8_grouped_pv_case9.cpp` — #104518: correct but case 9 regressed to 1.325 ms.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_fullpage_case79.cpp` — #104552: correct but cases 7/9 regressed.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_case9_mma.cpp` — #104472: KV8 MMA-QK was correct but performance-negative.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_broadcast8_case7.cpp` — #104461: WrongAnswer from a lane-dependent shuffle source.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_lb128_case7.cpp` — #104468: no measurable launch-bounds benefit.
