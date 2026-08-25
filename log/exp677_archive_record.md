## exp677 / #124788 terminal archive record

- queue check: `python tools/xpuoj_submit.py --list 20`; all listed submissions were terminal and no non-terminal submission remained.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case11_regcoeff_exp677.cpp`; candidate SHA-256 `7d2e0f10e8808e9f338395c27601090e8d448a7e3b806f2dd43ce163a8938c4e`.
- watch: `python tools/xpuoj_submit.py --watch 124788 --poll-seconds 1`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_124788_raw.json`.
- result: `14/14 Accepted`, total `65.93`; target case11 (B16/KV4/L12251) was `232 us / 51 points`, versus control `224 us / 52 points`, so the registered `>=53` target tier was not reached.
- raw SHA-256: `89552212f42a48838f000401d17bc9150b3a467fc19045ed50efa86c5a39b3ca`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_124788.cpp`; raw embedded code, candidate, and immutable source all SHA-256 `7d2e0f10e8808e9f338395c27601090e8d448a7e3b806f2dd43ce163a8938c4e` and are byte-identical.
- archive: `python tools/archive_cuda_submissions.py`; `solutions/archive/SUBMISSIONS.md` contains #124788.
- decision: close the exp677 case11 register-coefficient contract; keep structural control `#124611 / exp666`; non-target timing changes are not attributed; no resubmit and no new `--submit` was run.
