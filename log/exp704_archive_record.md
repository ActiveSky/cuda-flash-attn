# exp704 / #125765 OJ archive and record

Date: 2026-08-25 (UTC+8)

This record covers the terminal exp704 submission only. The subsequent
in-flight submission `#125776 / exp709` was not queried, watched, submitted,
cancelled, or modified, and the current work file was not touched.

## Submission identity

- Raw: `results/raw/cuda_125765_raw.json`
- Raw SHA-256: `b4da62b47dd71c46baf53b9f31781a387647fa51301d35610020a3d4a139b9d0`
- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_z8_all_async_register_kv_exp704.cpp`
- Candidate and raw-embedded source SHA-256:
  `53cca7e99f7d43066a7beb53323c93c0ed2f249e0438f4398d18f8e7e6c75e78`
- Immutable submitted source:
  `solutions/archive/2026-08-25-submissions/cuda_125765.cpp`
- OJ result: `Accepted`, 14/14, total `65.93`.

## Online target attribution

The registered target cases 7/9/12/13 were respectively `229 us / 55`,
`236 us / 57`, `375 us / 60`, and `184 us / 56`. Their display-score sum was
`228`, below the current control's corresponding sum `229` (`55/57/60/57`).
The exact z8 all-async register-K/V backend contract is closed and control
`#124611` is retained. Non-target cases, aggregate score, and same-run timing
are not attributed to this candidate.

## Archive verification

Ran:

```text
python3 tools/archive_cuda_submissions.py
```

The generated manifest now contains `#125765`. The immutable source bytes
match the raw-embedded source and candidate SHA above. No raw JSON, control,
work file, GPU, or OJ queue state was changed by this archive operation.
