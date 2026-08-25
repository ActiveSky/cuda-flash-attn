# exp690 / #125388 OJ archive record

## Identity and terminal result

- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case7_threechunk_fused_direct_exp690.cpp`
- Candidate SHA-256: `bc90ae1b38e7c79daced75c8495c7426542c500cd30c3e7956b7f410950e8ce2`
- Parent/current control: `#124611 / exp666`
- Control SHA-256: `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`
- Submission: `#125388`, `Accepted`, 14/14, score `65.71`
- Submit time: `2026-08-24T12:25:57Z`
- OJ time/memory: `1636 ms` / `23060628 KB`
- Raw: `results/raw/cuda_125388_raw.json`
- Raw SHA-256: `b3a3f0de94f390952dae314f9af132f0920076dcfcbbac601c91351c10facf79`
- Immutable source: `solutions/archive/2026-08-24-submissions/cuda_125388.cpp`
- Raw embedded code and immutable source SHA-256: `bc90ae1b38e7c79daced75c8495c7426542c500cd30c3e7956b7f410950e8ce2`

## OJ facts and disposition

Case 1–14 times/scores from the raw record:

`3/92, 4/90, 10/82, 23/72, 17/73, 28/63, 269/51, 93/54, 235/57, 38/62, 222/52, 374/60, 181/57, 139/55 us/score`.

The sole target was case7 (B64/KV8/L2048): `269 us / 51`, versus approximately `226 us / 55` for the current control. The `43/43/42` three-bucket same-CTA FP32-state direct-output path, which skipped the partial+reducer round trip, is closed as an exact contract. It does not replace the control and is not being re-submitted or parameter-scanned. Non-target cases, aggregate score, and same-run timing movement are not attributed.

## Submission/watch and archive checks

- Actual `--submit` created `#125388` once.
- Two watch attempts each reached the 900-second timeout; both continued watching the original ID. The later same-ID watch reached `Finished/Accepted`.
- No duplicate POST, cancellation, or parallel submission was performed.
- `tools/archive_cuda_submissions.py` completed and registered `#125388` in `solutions/archive/SUBMISSIONS.md`.
- The mutable work file remains byte-identical to the control (`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`). This archive task did not modify AGENTS/goal, the work file, candidate, control, raw JSON, or any other OJ task.

