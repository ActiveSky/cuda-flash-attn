# exp691 / #125367 terminal archive record

- queue check: `python tools/xpuoj_submit.py --list 20`; #125367 was terminal `Accepted`; the independent exp690 submission `#125388` was still `Pending` and was not watched, canceled, or otherwise touched by this task.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case6_static_weight8_exp691.cpp`; candidate SHA-256 `39db393846e782ee07bd389b8f8adfb1314becd1da3be96d4b0fb5ec985b1291`.
- result: #125367 `Accepted`, 14/14, total `65.93`; case1-14 us/score=`3/92,4/90,9/83,23/72,17/73,29/62,225/55,94/54,232/57,38/62,224/52,373/60,182/56,139/55`.
- attribution: the sole target case6 (B16/KV8/L362) was `29 us / 62 points`, versus control `28 us / 63 points`; the fixed `STATIC_WEIGHT_SPLITS=8` row16 case6 contract regressed and is closed. No non-target, aggregate, or same-tier timing is attributed; control remains `#124611 / exp666`.
- raw: `results/raw/cuda_125367_raw.json`; raw JSON SHA-256 `9a4861af40146e46108f0825528b7ba71d5b3a04a5499db216bfb8795fac5f8c`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_125367.cpp`; raw embedded code, candidate, submitted code, and immutable source are byte-identical, all with SHA-256 `39db393846e782ee07bd389b8f8adfb1314becd1da3be96d4b0fb5ec985b1291`.
- archive: ran `python tools/archive_cuda_submissions.py`; `solutions/archive/SUBMISSIONS.md` contains #125367.
- safety/cleanup: work file was not modified and remains control SHA `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`; `git diff --check` passed. No resubmit or parameter scan.
- completed UTC: `2026-08-24T12:26:48Z`.
