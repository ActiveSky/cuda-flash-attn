# Solution experiment archive

This directory stores historical and rejected XPUOJ C500 candidate sources. The active `solutions/` directory intentionally contains only the maintained implementation:

- `../cuda_maca_version.cpp`

## Archive collections

- [`2026-08-07-experiments/`](2026-08-07-experiments/) — 65 historical CUDA candidates from the 2026-08-07 optimization cycle. Each source is tied to an experiment or submission in `results/cuda_result.md`; raw OJ responses are in `results/raw/`.

### Important rejected candidates in the 2026-08-07 collection

- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_kv8_grouped_pv_case9.cpp` — #104518: correct but case 9 regressed to 1.325 ms.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_fullpage_case79.cpp` — #104552: correct but cases 7/9 regressed.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_case9_mma.cpp` — #104472: KV8 MMA-QK was correct but performance-negative.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_broadcast8_case7.cpp` — #104461: WrongAnswer from a lane-dependent shuffle source.
- `2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_lb128_case7.cpp` — #104468: no measurable launch-bounds benefit.
