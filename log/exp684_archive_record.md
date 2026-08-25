## exp684 / #125200 terminal archive record

- purpose: same-source, intentional online variance probe of current control `#124611 / exp666`; no source or mechanism delta.
- result: `#125200` was terminal `Accepted`, `14/14`, total `66.07`; case1-14 were `3/92, 4/90, 9/83, 23/72, 17/73, 28/63, 228/55, 93/54, 235/57, 39/62, 223/52, 377/60, 181/57, 139/55 us/points`. Non-target timing variation is not attributed.
- raw: `results/raw/cuda_125200_raw.json`; raw JSON SHA-256 `95eb59c3c4cbd321038b27d88ebf00a6ee48970565792cd1bc2d4e5115748b91`.
- source identity: candidate/work file `solutions/cuda_maca_optimized.cpp`, submitted raw code, control `solutions/archive/2026-08-24-submissions/cuda_124611.cpp`, and immutable `solutions/archive/2026-08-24-submissions/cuda_125200.cpp` all have SHA-256 `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`; manifest contains #125200 after `python3 tools/archive_cuda_submissions.py`.
- decision: retain structural control `#124611 / exp666`; this replay does not justify a control change. No resubmit, scan, or second submission was made by the archive task.
- final state: work file remains the control SHA; `log/exp684_oj_watch.md` records the terminal queue check with no `Pending` or `Running` submission. `git diff --check` and final SHA checks were run after this record was written.
