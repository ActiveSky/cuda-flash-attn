## exp676 / #124761 terminal archive record

- queue check: `python tools/xpuoj_submit.py --list 20`; all listed submissions were terminal and no non-terminal submission remained.
- candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case10_bf16_packed_vec2_exp676.cpp`; candidate SHA-256 `62fca964471f350cb0b4416a001515bc5ffc15a91f81cc93840677b890fd42de`.
- watch: `python tools/xpuoj_submit.py --watch 124761 --poll-seconds 1`; same ID returned `Finished / Accepted` and saved `results/raw/cuda_124761_raw.json`.
- result: `14/14 Accepted`, total `66.00`; target case10 (B1/KV4/L8192) was `41 us / 60 points`, versus control `38 us / 62 points`, so the registered `>=63` target tier was not reached.
- raw SHA-256: `e8b7078125e8380a1d2c082793397baf8f6e23de368734f8a880a39233c5e45b`.
- immutable: `solutions/archive/2026-08-24-submissions/cuda_124761.cpp`; raw embedded code, candidate, and immutable source all SHA-256 `62fca964471f350cb0b4416a001515bc5ffc15a91f81cc93840677b890fd42de` and are byte-identical.
- archive: `python tools/archive_cuda_submissions.py`; `solutions/archive/SUBMISSIONS.md` contains #124761.
- decision: close the exp676 case10 BF16 packed-vec2 contract; keep structural control `#124611 / exp666`; non-target timing changes are not attributed; no resubmit and no new `--submit` was run.
