# exp675 / #124696 terminal archive record

- completed_utc: `2026-08-24T02:36:21Z`
- queue check: `python tools/xpuoj_submit.py --list 20`; #124696 and all listed submissions were terminal, with no non-terminal OJ submission.
- submission: `#124696`, `Accepted`, `14/14`, score `65.93`, submit time `2026-08-24T02:19:42Z`.
- watch: `python tools/xpuoj_submit.py --watch 124696 --poll-seconds 5 --timeout-seconds 120`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_124696_raw.json`.
- raw SHA-256: `9d236cf9213f95ce4873a6c2d980dda6ef955c50f4a394d7c491ece32fad6697`.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case11_bf16_vec4_exp675.cpp`
- immutable: `solutions/archive/2026-08-24-submissions/cuda_124696.cpp`
- candidate, immutable, and raw embedded code SHA-256: `aa19bf773166504181479a2a06e44eb45e0846a84dc054751d34945eff71a287`.
- identity check: raw embedded code, candidate, and immutable source are byte-identical; each is 271385 bytes.
- archive command: `python tools/archive_cuda_submissions.py`; `solutions/archive/SUBMISSIONS.md` contains #124696.
- target result: case11 (`B16/KV4/L12251`) was `225 us / 52 points`; control #124611 was `224 us / 52 points`, so the registered `>=53` target tier was not reached.
- decision: close exp675's normalized-BF16 producer + 32-thread vec4 BF16 consumer contract; keep structural control #124611 / exp666; no resubmit or scan.
- post-archive queue: no non-terminal OJ submission; work file was not modified by this task and verified at control SHA `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`.
