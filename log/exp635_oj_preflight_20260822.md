# exp635 OJ read-only preflight

Date: 2026-08-22 UTC

Read-only identity check at preflight: work/control
`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`;
exp635 candidate
`f1d2515b3f8f592e990b55d302fe49965e4b18d06198bfecba52431afae80d0f`.

Commands run without staging, submitting, canceling, or changing the work file:

```text
python3 tools/xpuoj_submit.py --list 20
python3 tools/xpuoj_submit.py --list 100
python3 tools/xpuoj_submit.py --watch 122261 --no-archive --poll-seconds 0 --timeout-seconds 30
```

Both list queries returned the same ten most recent submissions. The newest was
`#122261 WrongAnswer 60.14`; all listed submissions were terminal. The detail
query returned `#122261 progress=Finished status=WrongAnswer`, with case 3
`WrongAnswer` and cases 1, 2, 4--14 `Accepted`; no non-terminal submission was
observed.

The scripts' help was checked. `xpuoj_submit.py` defaults to dry-run; the
actual command used by prior probes is:

```text
python3 tools/xpuoj_submit.py solutions/cuda_maca_optimized.cpp
python3 tools/xpuoj_submit.py --submit solutions/cuda_maca_optimized.cpp
```

After a terminal result, archive with:

```text
python3 tools/archive_cuda_submissions.py
```

Note: `archive_cuda_submissions.py` has no argparse help mode; invoking it with
`--help` runs the archive generator and rewrites its manifest. It must only be
run after the terminal result and then its manifest/source/SHA effects must be
checked. This was discovered during preflight; the generated tracked manifest
change was restored immediately, and no raw result or work/control source was
modified. The generated historical source snapshots remain byte-exact copies
of their raw records.
