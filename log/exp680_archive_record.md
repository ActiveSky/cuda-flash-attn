## exp680 / #125124 terminal archive record

- queue check: `python3 tools/xpuoj_submit.py --list 20`; #125124 was terminal `Accepted` and no non-terminal submission remained.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case14_bf16_hier_tree_exp680.cpp`; candidate SHA-256 `f9d6677a9d63b149205c2d5316cb92d557f86873bde16c99dd1bd638dba2a01e`.
- watch: `python3 tools/xpuoj_submit.py --watch 125124 --poll-seconds 30 --timeout-seconds 900`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_125124_raw.json`. No `--submit` was run by this archive task.
- result: `14/14 Accepted`, total `65.93`; case1-14 were `3/92, 4/90, 9/83, 23/72, 17/73, 28/63, 225/55, 93/54, 234/57, 38/62, 224/52, 373/60, 182/56, 142/54 us/points`. The sole target case14 (B1/KV4/L61519) was `142 us / 54 points`, below the registered `>=56` target tier and slower than control `139 us / 55`.
- raw SHA-256: `e4aab505bc62bc2b026dcd17fd85ec875feea9c91bd3496d9341129383f6996f`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_125124.cpp`; candidate and immutable source are byte-identical and both SHA-256 `f9d6677a9d63b149205c2d5316cb92d557f86873bde16c99dd1bd638dba2a01e`; raw embedded code has the same SHA. `solutions/archive/SUBMISSIONS.md` contains #125124 after `python3 tools/archive_cuda_submissions.py`.
- decision: close the exp680 case14 hierarchical normalized-BF16 partial-tree exact contract; the extra group stage did not produce target online gain. Retain structural control `#124611 / exp666`; non-target timing changes are not attributed; no resubmit, scan, or second submission.
- final state: `solutions/cuda_maca_optimized.cpp` SHA-256 is control `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`; final queue has no non-terminal submission. `git diff --check` passed for the touched archive/record paths.
