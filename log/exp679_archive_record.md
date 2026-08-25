## exp679 / #125089 terminal archive record

- queue check: `python tools/xpuoj_submit.py --list 20`; #125089 was already terminal `Accepted`, and no non-terminal submission remained.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case6_native_k_ldg_exp679.cpp`; candidate SHA-256 `a9e97eccd299577ef731de746d8c04fa36636269afb285b3bc3294664907f033`.
- watch: `python tools/xpuoj_submit.py --watch 125089 --poll-seconds 5 --timeout-seconds 900`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_125089_raw.json`. No `--submit` was run.
- result: `14/14 Accepted`, total `66.00`; case1-14 were `3/92, 4/90, 10/82, 23/72, 17/73, 28/63, 225/55, 94/54, 234/57, 39/62, 222/52, 374/60, 181/57, 139/55 us/points`. The sole target case6 (B16/KV8/L362) was `28 us / 63 points`, equal to control and below the registered `>=64` target tier.
- raw SHA-256: `0b2b29882ab25daf829392bfe31b42b7ad83364cfff5d5b2a907af17d1afea56`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_125089.cpp`; candidate and immutable source are byte-identical and both SHA-256 `a9e97eccd299577ef731de746d8c04fa36636269afb285b3bc3294664907f033`; raw embedded code has the same SHA. `solutions/archive/SUBMISSIONS.md` contains #125089 after `python tools/archive_cuda_submissions.py`.
- decision: close the exp679 case6 native-K-LDG exact contract; retain structural control `#124611 / exp666`. Non-target timing changes are not attributed; no resubmit, scan, or second submission.
- final state: `solutions/cuda_maca_optimized.cpp` SHA-256 is the control `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`; final queue has no non-terminal submission. `git diff --check` passed for the touched archive/record paths.
