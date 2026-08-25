# exp608 relaxed non-GPU safety smoke

Date: 2026-08-23

Scope: candidate-only SHA, cross-compilation/resource inspection, LLVM inspection,
CPU semantic replay, and source-level owner/tail checks. No real C500 execution,
no shared workfile write, no OJ command, and no project-record update.

## Identity and isolation

- Candidate:
  `solutions/archive/2026-08-20-experiments/cuda_case12_direct_k_wave_bsm_exp608.cpp`
  SHA-256 `1ed233b3ba65106c80024d0aece5c006f9b05678d8f36069800c1f84fd6d4f5f`.
- Parent/control:
  `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`
  SHA-256 `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`.
- Workfile was unchanged and still has the control SHA.
- New build products are isolated as
  `build/exp608_relaxed_candidate_resource.so` and
  `build/exp608_relaxed_control_resource.so`.

## Checks performed

- Cross-build commands (both exit 0):
  `tools/build_local_maca.sh <candidate> build/exp608_relaxed_candidate_resource.so -resource-usage`
  and the corresponding control command. The compiler emitted only the known
  `-Wmaca-min-blocks-per-multiprocessor` warnings; there was no compile or link
  error.
- CPU semantic smoke:
  `python3 tests/test_kernel_logic.py --quick-max-seqlen 64`
  returned `14/14` passed.
- Source checks passed for the single case12 opt-in dispatch, `lane^16` owner
  mapping, 16-byte alignment geometry, `p+1 < p_end` lookahead guard, tail
  `token < tail_tokens` mask, and SHA identity.
- Existing target LLVM was re-inspected: candidate target
  `paged_decode_case13_kv8_headpair_z8_kernel<true,false,false>` contains 8
  `llvm.mxc.bsm.bpermute` calls; the same control function contains 0. Neither
  target function contains an `s_k` reference. Existing full-TU LLVM/resource
  logs remain the authority for the complete specialization set.

## Semantic/launch conclusion

No definite correctness or illegal-launch risk was found in this non-GPU pass.
The `dim3(16,2,8)` launch is 256 threads; `lane^16` preserves `tx` and the
physical z-wave while flipping only `ty`. All target CTA barriers are on
uniform page/split branches. Full-page page-table reads are bounded by `p_end`;
a tail reads only the valid page-table entry `bt_row[full_pages]` when a real
tail exists, and QK/PV token ownership is masked by `token < tail_tokens` (the
whole valid tail-page vector load follows the inherited control contract). The
direct K helper uses aligned 16-byte rows and is compile-time enabled only for
the `batch_size==8,
seqlen_k==32768` KV8 dispatch.

This does not clear the existing static resource gate: target candidate
resources are `84 MTreg / 52 STreg / 8448 B / 0 stack / 5 waves`, versus control
`82 / 50 / 8448 B / 0 / 5`. The candidate is therefore statically buildable but
resource-gate failed; this is not a correctness or OJ result.

## Difference from exp623

exp608 keeps `direct_kpack` alive through PV and preloads the next page into
`direct_next_kpack` before PV, then promotes it after the page barrier. exp623
(`cuda_case12_direct_k_wave_bsm_no_lookahead_exp623.cpp`, SHA
`8daf875522d473d4c19aa44e6f3523190e098ef22ec3036f6a7ef4320ff4cc43`) kills K
after QK and reloads the next K only after PV, removing that next-K live range.
exp623 had target resources `76 / 52 / 8448 / 0 / 6` but was later submitted as
#121954 and measured online at `406 us / 58` for case12 versus control `378 us /
60`; that online result belongs to exp623, not exp608.

## Minimum C500 smoke command (not run here)

```text
python3 tests/c500_paged_decode_harness.py --library build/exp608_relaxed_candidate_resource.so --cases 12 --length-values 1,2,15,16,17,31,32,33,831,832,833,32767,32768 --seed 20260809
```
