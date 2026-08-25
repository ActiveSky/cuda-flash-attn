# exp607 relaxed static audit (2026-08-23)

## Scope

- Candidate: `solutions/archive/2026-08-20-experiments/cuda_case11_last_live_split_finalizer_exp607.cpp`
- Candidate SHA-256: `bac7e4727f490224af6d1b30cc0165131203181a5b7950ca09f40a13927df655`
- Parent/control: `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`
- Parent SHA-256: `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`
- Target: case11, B16/KV4/seqlen_k=12251
- No real C500, OJ, work-file, or shared-record operation was performed.

## Build and identity

The isolated normal, `-resource-usage`, and `-c -emit-llvm -S` builds all succeeded:

- `log/exp607_relaxed_audit_normal.log`, output `build/exp607_relaxed_audit_normal.so`
- `log/exp607_relaxed_audit_resource.log`, output `build/exp607_relaxed_audit_resource.so`
- `log/exp607_relaxed_audit_llvm.log`, output `build/exp607_relaxed_audit_candidate.ll`

`log/exp607_relaxed_diff.log` shows 8 intended hunks (113 added, 6 removed by
`diff --numstat`): the two last-live template flags, the producer/finalizer
body, the exact case11 dispatch, and the reducer guard. No unrelated source
change was found. `run_kernel` is exported by the normal shared object.

## Exact dispatch and workspace arithmetic

At source lines 5410-5555, the candidate is enabled only when optimized MACA
and `(num_heads_k,batch_size,seqlen_k)=(4,16,12251)`. The exact path is the
KV4 synchronous headpair/z4 branch: producer template arguments end in
`SYMMETRIC_FINALIZER=true, SKIP_LAST_LIVE_SPLIT=true,
LAST_LIVE_SPLIT_FINALIZER=false`; a same-stream finalizer launch ends in
`..., true, false, true`. The producer launch is `grid=(64,39)` with
`block=(16,4,4)` (256 threads); the finalizer is `grid=(64,1)` with the same
block. The reducer is skipped by `n_split > 1 && !use_case11_last_live_finalizer`.

For the target, `max_pages=766`, `n_split=39`, `pages_per_split=20`, and the
workspace allocation is 19,968 `(m/l)` entries plus 2,555,904 FP32 accumulator
entries (10,223,616 bytes). The producer writes only slots `0..L-2`; the
finalizer computes slot `L-1` and reads only `s < L-1`, with
`L=min(n_split,ceil(full_pages/pages_per_split))` for nonempty full pages.
Thus:

- empty (`full_pages=0`, no tail): `L=0`, finalizer writes zero output and
  returns without reading workspace;
- tail-only or one-to-20 full pages: `L=1`, producer writes no slot and the
  finalizer reads no prefix slot;
- `L>=2` (including target max `cache_seqlens=12251`, `full_pages=765`,
  `tail=11`, `L=39`): every prefix slot read by the finalizer was written by
  the producer, and the last full-page owner fuses the tail.

The source index `(s*batch_size+b)*32+h` and raw-FP32 `tx*8` stride match the
existing producer partial ABI. The finalizer IR has input-only partial
arguments and no partial stores; extracted body evidence is in
`log/exp607_relaxed_audit_finalizer_ir.txt`.

## Static safety and resources

- Normal/LLVM compilation: **PASS** (only existing ignored `__launch_bounds__`
  minimum-block warnings).
- Dispatch/block/grid arithmetic: **PASS** for the exact target; compiler
  accepted all launches and the 256-thread block matches the kernel contract.
- Empty/one/multiple-live-split and stale-slot reasoning: **PASS**; no
  unwritten partial is read by the new finalizer.
- `cudaDeviceSynchronize` source/LLVM scan: no hits. No new synchronization or
  atomic publication protocol was introduced; launches remain same-stream.
- Resource output: ordinary producer is `80 MTreg / 58 STreg / 8320 B shared /
  0 B stack / 6 waves`, matching the control. The new finalizer is
  `88 MTreg / 52 STreg / 8320 B shared / 0 B stack / 5 waves`.
- No spill diagnostic was emitted; all reported function stack frames are
  zero. The finalizer's 8-register increase and 6-to-5 wave drop are a real
  residency risk and **FAIL the old hard resource/occupancy admission gate**,
  although they are not an illegal launch or compile failure.

## Minimum C500 smoke to run before accepting the candidate

This audit did not run C500. The minimum risk-matched smoke should use the
exact target dispatch and reference comparison with:

1. full target `seqlen_k/cache_seqlens=12251` (multi-split plus fused tail);
2. per-batch lengths covering L0/L1/L2 and boundaries, e.g.
   `0,1,15,16,17,320,321,336,337,12160,12176,12240,12251`, with poisoned
   block-table padding and output guards;
3. same-process `full -> short -> full` and `short -> full` workspace reuse,
   checking numerical tolerance and NaN/Inf.

**Overall static result:** identity, compilation, launch shape, and partial
lifetime safety pass; legacy resource gate fails solely on the finalizer's
5-wave/88-MTreg resource cost. OJ admission remains a main-agent decision
under the relaxed exploratory-probe policy.
