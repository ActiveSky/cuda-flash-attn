# exp694 / OJ #125561 archive record

Date: 2026-08-24 (UTC)

## Terminal fact

- Submission: `#125561`, submitted at `2026-08-24T15:11:40Z`
- Status: `Accepted`, `14/14`, total score `65.86`
- OJ time/memory: `1602 ms` / `23060560 KB`
- Case time/score (`case1..14`): `3/92, 4/90, 10/82, 23/72, 17/73, 28/63, 233/54, 94/54, 233/57, 38/62, 224/52, 374/60, 182/56, 139/55`
- Registered target: case7 (`B64/KV8/L2048`), at least `56` points. Observed `233 us / 54` points, below target and one display tier below the `226 us / 55` control observation.
- Decision supplied by the main agent: close the exact raw physical-wave `lane^32` first-z merge contract; do not switch control, resubmit, or scan variants. Non-target cases and aggregate/timing-tier changes are not attributed.

## Source and raw identity

| Item | Path | SHA-256 |
|---|---|---|
| Candidate | `solutions/archive/2026-08-24-experiments/cuda_control124611_case7_raw_wave_rebase_exp694.cpp` | `abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2` |
| Raw result | `results/raw/cuda_125561_raw.json` | `7106b47ef070efcc409b8a8069dddd1306893a8a1cf761ebac154e6fb7f0354a` |
| Immutable submitted source | `solutions/archive/2026-08-24-submissions/cuda_125561.cpp` | `abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2` |
| Current control | `solutions/archive/2026-08-24-submissions/cuda_124611.cpp` | `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe` |
| Work file after terminal result | `solutions/cuda_maca_optimized.cpp` | `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe` |

The candidate, raw embedded `code`, and immutable submitted source are byte-identical at the candidate SHA. The manifest row is present in `solutions/archive/SUBMISSIONS.md` as `#125561`, `Accepted`, score `65.86`, with the same submitted-source SHA and raw path.

## Archive operation

Only the existing terminal raw records were archived; no OJ submit, watch, cancel, or queue operation was performed by this record task. Command and output:

```text
python3 tools/archive_cuda_submissions.py
archived 389 submissions; manifest: /data/cuda-flash-attn/solutions/archive/SUBMISSIONS.md
```

The archive script extracted the raw source to `solutions/archive/2026-08-24-submissions/cuda_125561.cpp` and regenerated the complete manifest. The subsequent identity checks were:

```text
sha256sum candidate raw immutable
abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2  candidate
7106b47ef070efcc409b8a8069dddd1306893a8a1cf761ebac154e6fb7f0354a  raw
abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2  immutable

cmp candidate immutable
identical (exit 0)

git diff --check
pass
```

The current work file remains the control snapshot. This archive task did not modify `AGENTS.md`, `goal.md`, the control source, the work file, the experiment candidate, or the subsequent exp695 OJ task.
