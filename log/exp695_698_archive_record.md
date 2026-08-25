# exp695 / exp698 archive and terminal record

Date: 2026-08-24

This record covers only the two supplied terminal submissions. The archive
executor did not query, submit, cancel, watch, or otherwise operate on the
OJ queue; in particular it did not touch the current exp693 submission.

## Shared control and archive procedure

- Parent/current control: `#124611 / exp666`
- Control SHA-256: `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`
- Work-file SHA after the probes: `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`
- Ran `python3 tools/archive_cuda_submissions.py`.
- The generated manifest reports 391 raw submissions. Both requested IDs are
  present with `Accepted` status and the SHA of their archived source.

## #125585 / exp695

- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case9_raw_wave_rebase_exp695.cpp`
- Immutable source: `solutions/archive/2026-08-24-submissions/cuda_125585.cpp`
- Raw: `results/raw/cuda_125585_raw.json`
- Submission: one serialized POST; `#125585`, `Accepted`, 14/14, score
  `65.86`, submitted `2026-08-24T15:32:14.000Z`, OJ time `1607 ms`, memory
  `23060512 KB`.
- Target: case9 (`B32/KV8/L4096`), `244 us / 56` display points; the
  pre-registered `>=58` target was not met. The exact case9 raw-wave
  `lane^32` first-z merge contract is closed and control is unchanged.
- Case display scores: `92/90/82/72/73/63/55/54/56/62/52/60/56/55`.
- Raw JSON SHA-256:
  `107727616ccca83b1a846608b1930229f6dbda171bd764ba56baa2a4e20d025b`
- Candidate SHA-256:
  `8efee54b8335ce391da7aab12f6607f685a58b01bacdbd6bb1a6982b54f472a8`
- Embedded raw source SHA-256:
  `8efee54b8335ce391da7aab12f6607f685a58b01bacdbd6bb1a6982b54f472a8`
- Immutable archive source SHA-256:
  `8efee54b8335ce391da7aab12f6607f685a58b01bacdbd6bb1a6982b54f472a8`
- Identity checks: candidate == embedded source == immutable archive source.
- Source manifest entry: `#125585`, `Accepted`, `65.86`, source
  `2026-08-24-submissions/cuda_125585.cpp`, raw
  `results/raw/cuda_125585_raw.json`.

## #125625 / exp698

- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case5_single_live_direct_output_exp698.cpp`
- Immutable source: `solutions/archive/2026-08-24-submissions/cuda_125625.cpp`
- Raw: `results/raw/cuda_125625_raw.json`
- Submission: one serialized POST; `#125625`, `Accepted`, 14/14, score
  `66.00`, submitted `2026-08-24T15:57:15.000Z`, OJ time `1594 ms`, memory
  `23060584 KB`.
- Target: case5 (`B16/KV4/L141`), `17 us / 73` display points; the
  pre-registered `>=74` target was not met. The exact seqlen 1..32 single-live
  direct-output + reducer-return contract is closed and control is unchanged.
- Case display scores: `92/90/82/72/73/63/55/54/57/62/52/60/57/55`.
- Raw JSON SHA-256:
  `6b3329c445f83e6d92699fa7d747419b97264c77d859a6f29f56e7f83766c0fc`
- Candidate SHA-256:
  `716c620f804c39086c1873aa50696d3a09ec91be4e639fcb701670f2797826f6`
- Embedded raw source SHA-256:
  `716c620f804c39086c1873aa50696d3a09ec91be4e639fcb701670f2797826f6`
- Immutable archive source SHA-256:
  `716c620f804c39086c1873aa50696d3a09ec91be4e639fcb701670f2797826f6`
- Identity checks: candidate == embedded source == immutable archive source.
- Source manifest entry: `#125625`, `Accepted`, `66.00`, source
  `2026-08-24-submissions/cuda_125625.cpp`, raw
  `results/raw/cuda_125625_raw.json`.

## Evidence and scope

- exp695 submission and safety summary: `log/exp695_oj_submit.log`,
  `log/exp695_summary.log`, and `log/exp695_resource_llvm_summary.log`.
- exp698 submission/final identity summary:
  `log/exp698_oj_submit.log` and `log/exp698_oj_final.log`.
- Detailed experiment closure is recorded in `notes.md`; the two terminal
  entries are marked `CLOSED` and do not attribute non-target or aggregate
  movement.
