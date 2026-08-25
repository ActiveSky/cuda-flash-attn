# Recent isolated-candidate admission audit (2026-08-23)

Parent/control for this audit is `#113889 / exp559`, SHA
`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`.
The audit is read-only for source/results and did not run C500, A/B, or OJ.

## Scope inventory

`solutions/archive/2026-08-23-experiments/` contains exactly these two
candidate source files:

| candidate | SHA-256 | disposition at audit time |
|---|---|---|
| `cuda_case1_per_word_raw_bsm_v_fanout_exp646.cpp` | `812fc9d6fe71a25682b7b974ca88788a4bb30d82c260af732d8512dd43c4e39f` | already terminal: static resource gate failed / closed |
| `cuda_case11_wave_owner_readfirstlane_pid_exp647.cpp` | `f4c56496933d091f1d22250318498feaed2c3df9e80edd7d7e0f3c9c0538788a` | already terminal: admission rejected |

The same-day `2026-08-23-submissions/` directory contains only the
immutable OJ sources for terminal `#122912` (exp641) and `#122987` (exp644);
neither is an unrecorded candidate. There is no `results/raw` entry for
exp646 or exp647.

## Candidate decisions

### exp646 — not admissible

The source-level proposal is a real source-owner/BSM consumer change for the
fixed case1 shape: lines 229-291 add a 128-thread kernel in which each
physical 64-lane wave reads one V-row word and uses raw
`__builtin_mxc_bsm_bpermute`; lines 5250-5264 route only `batch_size == 1,
num_heads_k == 4` to it. It therefore has a unique target (case1), but it
does not pass the mandatory resource gate. The recorded static evidence in
`notes.md:4435-4439` reports target resources `14 MTreg / 14 STreg / 0 B
shared / 0 stack / 8 waves`, versus the control target `6 / 18 / 0 / 0 / 8`;
the `MTreg=14 > 6` hard bound is a direct stop. No device-LLVM, correctness,
C500, A/B, or OJ evidence exists, and no raw submission exists. This exact
contract is already closed; source lane, word order, BSM address, store
spelling, helper, template, and enable-range variants are not changed
preconditions.

### exp647 — not admissible

Lines 3154-3171 insert `WAVE_OWNER_NEXT_PID` and lines 3441-3452 replace the
existing `bt_row[p + 1]` lookahead with one `tx == 0 && ty == 0` page-table
read plus `__builtin_mxc_readfirstlane`. This changes neither Q/K/V,
attention state, partial storage, page identity, workspace lifetime, nor
launch ownership; it is the already-closed PID/cache/broadcast family, not a
new storage backend or lifetime contract. The existing terminal audit at
`notes.md:4441-4445` also records that inserting the template boolean in the
middle without updating all explicit instantiations shifts case8/case14/case5
arguments and leaves the case11 final `SYMMETRIC_FINALIZER` argument at its
default. Thus it does not meet even the minimal isolated-build premise.
There is no C500, A/B, or OJ evidence and no raw submission. `readfirstlane`,
lane, builtin, address, layout, template, and enable-range scans cannot reopen
this contract.

## Result

**NO CANDIDATE.** Both files in the dated experiment scope already have a
recorded terminal disposition, and neither provides an unclosed candidate with
a plausible path through the required safety gates. No candidate is approved
for staging, workfile modification, or OJ probe.

Evidence used: `AGENTS.md`, `goal.md`, `results/cuda_result.md`,
`notes.md:4428-4445`, the two dated experiment sources above, and the existing
`log/exp646_*` static-resource records.
