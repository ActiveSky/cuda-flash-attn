# exp696/exp705 OJ archive and record update

Date: 2026-08-25 (UTC+8)

This record covers only the two terminal submissions whose raw results were
already present. It does not inspect, watch, submit, or modify the separate
in-flight exp704 submission `#125765`.

## exp696 / #125658

- Raw: `results/raw/cuda_125658_raw.json`
- Raw SHA-256: `5480da96dc15dca3a3a39cdf02cf763822cb91f3f762869e19c08d05c15a5132`
- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case12_raw_wave_rebase_exp696.cpp`
- Candidate and raw-embedded source SHA-256: `f23ce28fa2e0abdc6329b2d73af9e56b3a236c195a1c703924692e6b7e3071fe`
- Immutable submitted source: `solutions/archive/2026-08-25-submissions/cuda_125658.cpp`
- OJ result: `Accepted`, 14/14, total `66.00`; case12 `375 us / 60`.
- The registered case12 target `>=61` was not reached. The candidate is
  closed and does not replace control `#124611`.

## exp705 / #125753

- Raw: `results/raw/cuda_125753_raw.json`
- Raw SHA-256: `ef03878bd773a5ba05736bd8781a0d0c9ae7664e1ebdf03d4b462ca550705ffb`
- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_z4_all_async_register_kv_exp705.cpp`
- Candidate and raw-embedded source SHA-256: `25a637f309f8a8206a2210a1c8f6382fe9e9206507b5b0b4b41f92caefebe083`
- Immutable submitted source: `solutions/archive/2026-08-25-submissions/cuda_125753.cpp`
- OJ result: `Accepted`, 14/14, total `65.43`; target cases 8/10/11/14
  scored `52/62/51/53` (`218` total versus control `223`).
- The target contract is closed and control `#124611` is retained. The C500
  tail probe (`log/exp705_c500_tail_probe.log`) additionally found that both
  candidate and control read poisoned padding after `cache_seqlens` in the
  constructed tail-NaN trap and produce non-finite output. This is an
  inherited control diagnostic, not a candidate-only failure; exp705 must
  not be recorded as an unconditional C500 safety pass.

## Archive verification

Ran:

```text
python3 tools/archive_cuda_submissions.py
```

The generated manifest contains both submissions. The SHA-256 of each
generated immutable source matches the raw-embedded source and the candidate
SHA listed above. No control, work file, raw JSON, OJ queue, or in-flight
submission was changed by this record update.
