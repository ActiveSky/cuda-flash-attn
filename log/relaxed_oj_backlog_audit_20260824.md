# Relaxed OJ backlog audit (2026-08-24)

## Scope and result

本审计只做历史事实筛查，不修改源码、工作文件或共享结果，不运行 build、C500、benchmark、OJ 或归档命令。权威父 control 为 `#113889 / exp559`，SHA-256
`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`；当前 OJ 终态与 case tier 以 `results/cuda_result.md` 为准。

对 `notes.md`、`results/cuda_result.md`、近期 backlog 审计、所有日期化 experiment 源码及所有 immutable submission `.cpp` 做了定向核对。下列 SHA 均未在 `solutions/archive/*-submissions/` 中出现，也未在 `results/cuda_result.md` 或 raw 记录中找到相同源码的 OJ 终态。严格 gate-pass frontier 仍为 NO CANDIDATE；下面是放宽 OJ-first 后最多三个“有条件后备”，不是主 Agent 已批准的候选或提交。

## Conditional backlog, ordered by expected information per next serial probe

### 1. exp631 — case2 single-launch source-owner native B128 fanout

- **Source / identity**: `solutions/archive/2026-08-22-experiments/cuda_case2_source_owner_native_b128_single_launch_exp631.cpp`, SHA-256 `a61ef873b62fe81fa96b714d1a4ce44cb10c9a7e0ade61d4487e23697dd222af`.
- **Parent**: exact current `#113889 / exp559`, SHA `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`; no rebase is needed merely to preserve the current case7 control.
- **Mechanism and target**: only case2 `B4/KV8/cap=2`, real `seqlen==1`, uses one 128-thread launch in which 16 source owners read token-0 V by native B128 and fan out to four GQA output rows; `seqlen==2` and all other dispatches stay control. Target is current case2 `4 us / 90 points`; a useful result would be `14/14` and a cross-tier `>=91` case2 score.
- **Existing evidence**: normal and resource builds succeeded. Target `<8,4,true>` is `23 MTreg / 37 STreg / 0 B / 0 stack / 8 waves`, versus control `22 / 26 / 0 / 0 / 8`; no spill, stack, or wave loss. No CPU/C500 correctness, A/B, or LLVM deep audit was run.
- **Why it was not submitted**: only the old per-component resource gate (`+1 MTreg/+11 STreg`) stopped it; there is no recorded correctness, compile, or illegal-launch failure. The related B32 streaming source-owner contract was submitted as `#124235` and stayed at `4 us / 90 points`, but B128 payload lifetime/fanout is a different exact contract, so this would not be a same-source resubmission.
- **Minimum supplemental gate**: one current-toolchain target smoke on the frozen source: `seqlen` 1/2, all-one/all-two/mixed/reverse batches, token-1 and padding sentinels, raw-bit GQA mapping, output guards, and workspace reuse. Also verify the exact dispatch/launch path and SHA immediately before staging. Do not require full 14-case/A-B before a probe; if this target smoke is finite and correct, the main Agent may decide on one serial OJ probe.

### 2. exp451 — case14 FP32 single-LSE partial-state contract

- **Source / identity**: `solutions/archive/2026-08-14-experiments/cuda_case14_single_lse_state_exp451.cpp`, SHA-256 `5d307b0f43b5a394750f6aea3bf7b9daf57719c437243dae9f2ea441c1a0df1d`.
- **Parent**: historical `#111918`, SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`; this is not directly stageable as the current control. The mechanism must be rebased onto `#113889` while retaining the current case7 change, yielding a new candidate SHA.
- **Mechanism and target**: only case14 fixed-15-page producer/reducer changes 4-byte metadata from packed FP16 `(m,l)` to FP32 `lse=m+log2(l)`, with empty state `-Inf` and reducer weight `exp2(lse-lse_max)`; QK/PV, normalized BF16 accumulator, loader, z merge, split257, workspace and other shapes stay unchanged. Current control target is case14 `139 us / 55 points`; success requires a higher display tier with `14/14`.
- **Existing evidence**: producer `82/62/8320 B/0 stack/5 waves`, single-LSE reducer `40/32/0/0/8`; CPU/manifest and C500 full/random/boundary are `14/14`, finite, and exact lengths including padding trap plus `full->short->full` and `short->full` reuse pass. Fresh old-control A/B had full p10/p50/p90 `0.9924/0.9971/1.0096`, random `0.9850/0.9933/1.0054`, boundary `0.9436/1.0015/1.0790`; no distribution exceeded the old `1%` regression stop.
- **Why it was not submitted**: it was accepted as a valid state-contract experiment but withheld because its roughly `0.4%` full-length local improvement did not meet the old local-confidence/display expectation. No correctness, compile, or illegal-launch failure is recorded. The later exp452 combined guard+LSE contract is a different exact source and is not an OJ result for bare exp451.
- **Minimum supplemental gate**: rebase and rebuild the current full TU; run only target case14 smoke covering fixed15/full, short and tail/page boundaries, padding trap, finite output and both workspace-reuse orders. Recheck that all non-target dispatches, especially current case7, match control. A fresh full A/B is diagnostic, not a probe prerequisite. A probe is informative because no immutable submission has this single-LSE state ABI.

### 3. exp487 — case12 async-register K/V lookahead with verified wait contract

- **Source / identity**: `solutions/archive/2026-08-15-experiments/cuda_case12_async_register_gvm_wait_exp487.cpp`, SHA-256 `66a494520f7c0d74d6a4c39b907f5bee5ff59eb4a661a46726a41d4b4493eb82`.
- **Parent**: historical `#112716`, SHA `411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`; it must be rebased onto current `#113889` before any candidate SHA can be frozen.
- **Mechanism and target**: only case12 z8 producer changes the next-page K and V loads to register-returning async 16-byte loads, uses verified `arrive(64)`/barrier wait, and writes the existing shared rows only after wait; split40, z8 ownership, synchronous page buffer, partial ABI, reducer and other dispatches remain control. Target is current case12 `378 us / 60 points`; useful success requires `14/14` and `>=61` points.
- **Existing evidence**: the independent C500 async-register probe passed 64-thread and 256-thread payload semantics for 257 iterations and showed real `llvm.mxc.load.global.async.v4i32`, arrive and barrier lowering. Candidate LLVM had two async loads and wait-before-store ordering; resource was `82/52/8448 B/0 stack/5 waves` versus control `82/50/8448/0/5`. CPU/manifest, C500 full/random/boundary, exact lengths, padding and workspace reuse all passed. Old A/B was a repeatable local regression: full `0.9988/1.0042/1.0055`, random `1.0035/1.0057/1.0075`, boundary `1.0139/1.0164/1.0202`.
- **Why it was not submitted**: the old policy treated the all-distribution local regression as sufficient to defer OJ. There is no recorded correctness, compile, or illegal-launch failure, and the verified async-register K/V contract has no exact OJ terminal. Related synchronous/direct-K or async-Q experiments do not test this K/V register-lifetime contract.
- **Minimum supplemental gate**: rebase/current-toolchain compile and a target case12 smoke for page/split/tail boundaries, padding sentinels, finite output and both workspace-reuse orders; verify async load, arrive and wait ordering remains in current LLVM. Do not require a new full A/B before a serial probe. The main Agent should treat the old local regression as risk evidence, not as an automatic veto.

## Near misses excluded from the three-item backlog

- `exp494` is correct and unsubmitted, but its case12 full/random A/B p50 regressions are about `1.0423/1.0406`; it is a weaker duplicate of the same K-lifetime question and is not faster information than exp487.
- `exp495` is not carried forward because the current source SHA is `dc8e0afd5b83eb557885fb358f70fce417356ce58965dc9b823a6292e485a75b`, while the historical correctness/A-B note binds evidence to a different recorded SHA `cd6cdffe...`; the evidence is not identity-safe without reconstruction. Its old A/B also had full/random p50 regressions.
- `exp627/628` are per-output native-B128 copies, not source-owner fanout; their resource-only stop and the related online `exp632` result do not provide a new ownership edge. `exp639/640/645` are superseded normalized-BF16 direct-fanin resource failures with related online probes. `exp602/607/621/622` have determined correctness failures and are excluded. `exp632` itself has the online terminal `#124235` and is excluded.

## Decision boundary

These are conditional records for the main Agent. No item is approved for staging, control change, or OJ submission by this audit. If exp631's target smoke passes, it is the fastest current-control probe; exp451 and exp487 require a real rebase, so their archived SHA must never be submitted as if it were a current-control candidate. Any later OJ probe remains one-at-a-time and must use a freshly frozen SHA.

No source, work file, OJ queue, raw data, or shared research record was changed by this audit.
