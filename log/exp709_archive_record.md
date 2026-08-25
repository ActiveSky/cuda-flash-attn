# exp709 / #125776 OJ archive and record

Date: 2026-08-25 (UTC+8)

This record covers the terminal exp709 submission only. The subsequent
in-flight submission `#125788 / exp710` was not queried, watched, submitted,
cancelled, or modified, and the current work file was not touched.

## Submission identity

- Raw: `results/raw/cuda_125776_raw.json`
- Raw SHA-256: `644101222b6c698a19a9815e51b740bd6b702280d2295d1955c9b85591da3752`
- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_short123_bundle_exp709.cpp`
- Candidate and raw-embedded source SHA-256:
  `1499ce69d186977fb5c49ce75791238fcfcfac83d5e465a48e255a752cac7a36`
- Immutable submitted source:
  `solutions/archive/2026-08-25-submissions/cuda_125776.cpp`
- OJ result: `Accepted`, 14/14, total `66.07`.

## Online target attribution

The registered target cases 1/2/3 were respectively `3 us / 92`,
`4 us / 90`, and `9 us / 83`, for a display-score sum of `265`. The
pre-registered thresholds were case1 `>=93`, case2 `>=91`, and case3 `>=84`;
none was reached. The exact short123 bundle contract is closed and control
`#124611` is retained. In particular, case3's 83-point result is not treated
as a structural gain. Non-target cases, aggregate score, and same-run timing
are not attributed to this candidate.

## Archive verification

Ran:

```text
python3 tools/archive_cuda_submissions.py
```

The generated manifest now contains `#125776`. The immutable source bytes
match the raw-embedded source and candidate SHA above. No raw JSON, control,
work file, GPU, or OJ queue state was changed by this archive operation.
