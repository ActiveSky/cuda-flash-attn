## exp678 / #124801 terminal archive record

- queue check: `python tools/xpuoj_submit.py --list 20`; all listed submissions were terminal and no non-terminal submission remained.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case8_runtime_row16_exp678.cpp`; candidate SHA-256 `385b32b680e1a58294917a5c6c345b899f1dd87b603152e1dabc38418d52835a`.
- watch: `python tools/xpuoj_submit.py --watch 124801 --poll-seconds 1`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_124801_raw.json`.
- result: `14/14 Accepted`, total `65.93`; target case8 (B16/KV4/L4096) was `95 us / 53 points`, versus control `94 us / 54 points`, a regression and below the registered `>=55` target tier.
- raw SHA-256: `8c089bd4e6bf69f69da729b965fca91151668a44e27dfb4ac25cf41b5e153700`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_124801.cpp`; raw embedded code, candidate, and immutable source all SHA-256 `385b32b680e1a58294917a5c6c345b899f1dd87b603152e1dabc38418d52835a` and are byte-identical.
- archive: `python tools/archive_cuda_submissions.py`; `solutions/archive/SUBMISSIONS.md` contains #124801.
- decision: close the exp678 case8 runtime-row16 contract; keep structural control `#124611 / exp666`; non-target timing changes are not attributed; no resubmit and no new `--submit` was run.
