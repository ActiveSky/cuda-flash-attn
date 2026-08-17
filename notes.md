# 实验笔记与研究历史（notes.md）

本文件是仓库唯一的逐实验研究台账，保存候选假设、父源码与 SHA、资源、correctness、交错 A/B、OJ 反馈、失败反证、changed-precondition 和阶段复盘。稳定的当前状态、宏观方向和强制约束提炼到 `AGENTS.md`；OJ 逐提交事实以 `results/cuda_result.md`、`results/raw/` 和不可变提交源码为准。本文中的历史“当前/最佳/control”只代表记录当时的状态，开始新实验必须先查 `AGENTS.md` 的当前指针。

## 候选队列 / 实验记录

### exp1-case11-q-reuse  (CONFIRMED, 2026-08-08 — new best #106069, 57.57)
- **实验 ID**: exp1-case11-q-reuse
- **父源码/control**: #105952, SHA `eba3c95b18f5e62eb13d00f17de346946de6b8293fd00daaa0cece5d94f7c34a`
- **候选 SHA**: `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`
- **候选 .so**: build/cuda_case11_inplace_q.so
- **唯一差异**: 把 #105835 的 Q shared-memory 复用移植到 token-parallel kernel。
  - 新增模板参 `INPLACE_SHARED_Q`；static KV storage 上移到 Q staging 之前。
  - KV4 Q staging 在 INPLACE 时 alias s_k（复用 K 半缓冲，省 2 KiB 动态 Q），并在 K 预取前加 `__syncthreads()`。
  - dispatch：case 11 (sync_kv4 + separate_tail) 的 full/tail launch 改用 `<…,true>` 且去掉动态 shared（=0）。case 8 (sync_kv4 非 separate_tail) 不受影响。
- **可证伪假设**: case 11 (B16/L12251/KV4) 因独立 2 KiB 动态 Q 缓冲降低 occupancy；去掉后 residency↑ → 时延↓（OJ 448→~439 us）。
- **目标 case**: 11。**非目标**: 5/8/10/14 及短 case。
- **correctness**: CPU 逻辑 14/14；GPU full-length 14/14（case11 max_err 2.44e-4 同 control）；boundary 14/14；random+padding-trap 14/14。无 NaN/Inf，无越界 page 读。
- **本地交错 A/B** (control #105952 vs candidate, full, 11 rounds):
  | case | cand/ctrl p50 | p10/p90 |
  |---:|---:|---:|
  | 5 | 1.006 | 1.003/1.009 |
  | 8 | 1.001 | 0.995/1.005 |
  | 10 | 1.004 | 0.972/1.068 |
  | 11 | **0.9727** | 0.971/0.974 |
  | 14 | 1.000 | 0.995/1.003 |
- **结论**: case 11 稳定 ~2.7% 加速，其余中性。提交 OJ 验证。
- **OJ**: **#106069 Accepted 57.57**（#105952 57.43 → +0.14）。case 11 `448→438 μs`（35→36 分，目标改动确认）；case 5 `26→25 μs`（+1 分，有利 tier 波动，非本改动——本地 A/B case 5 ratio 1.006 中性）；其余 12 case 持平。**归档源码 SHA = a8101a3f… = 工作文件**。已设为新 control/baseline。

### exp2-case9-group8-reducer  (REJECTED, 2026-08-08)
- **父/control**: #105952 (eba3c95b...)
- **候选**: /tmp/case9_group8reduce.cpp；build/cuda_case9_group8reduce.so
- **唯一差异**: reducer 阈值 `reduce_splits <= 32` → `<= 48`，使 case 9 (reduce_splits=33，n_split=32+separate_tail) 走 group8 快速 reducer(128 CTA) 而非 general reducer(1024 CTA)。33-48 区间仅 case 9。
- **假设**: case 9 reducer 开销显著，group8(8 heads/CTA、更少 launch) 更快。
- **correctness**: KV8 7/9/12/13 full-length 14... 实际 4 case 全 PASS，case9 max_err=4.88e-4 同 control。
- **本地 A/B** (control vs cand, full, 11 rounds): case9 ratio p50=1.0002(p10/p90 0.999/1.002)；case7/12/13 全 1.000。完全中性。
- **结论**: **reducer 不是 case 9 瓶颈**（572us 中占比极小）。KV8 token-parallel 时间在每页 QK/PV 计算，不在 launch/reducer。拒绝。方向记录：KV8 优化须针对 compute，不针对 reducer/launch。

### MMA-QK precision block  (CLOSED with evidence, 2026-08-08)
- `paged_decode_mma_qk_kernel` 用 `wmma::accumulator<...,float>`（F32BF16BF16F32），逐行核对 A/B/C fragment 布局、K 转置、softmax、PV、output 均数学正确。但仍 fail tolerance。
- **诊断**（gate `use_mma_qk` 仅 case 8/3/5，本地实测 max_err）：
  | case | L | result |
  |---|---|---|
  | 3 | 17 | **NaN** (finite=False) |
  | 5 | 141 | max_err=0.793, match=0.096 |
  | 8 | 4096 | max_err=0.119, match=0.474 |
- 误差随序列**变短而变大**（反长度方向）+ NaN → 不是累加漂移、不是布局 bug。结论：**MACA `F32BF16BF16F32` WMMA 的 k=16 内积并非真 FP32 累加**（硬件/后端精度限制）。短序列 softmax 不够尖，分数扰动放大→输出误差；更短时溢出→`l=Inf,acc=Inf`→direct-out `Inf*0=NaN`。
- **结论**：MMA-QK 在本硬件无法满足 tolerance，不可作为 KV4 compute 突破口。除非硬件/编译器变化或找到真 F32 内积累加的 MMA，不再重开。已写入 AGENTS §8。

### exp3-case8-separate-tail-occupancy  (submitted, 2026-08-08)
- **父/control**: #106069 (a8101a3f...)
- **候选 SHA**: `52cedc7119fb4143c4a0c3f5d8fa017b97742812b93b9b6d5a9e60e6c0374454`
- **唯一差异**: separate_tail gate 新增 `num_heads_k==4 && batch_size==16 && seqlen_k==4096`（case 8）一行。case 8 从 combined `<4,8,true>`(92 MTreg, staticMaxWarps=5) 改走 sync_kv4+separate_tail+INPLACE：full `<4,8,true,true,false,true>`(70 reg, 7 warps) + tail `<4,8,true,false,true,true>`(42 reg)。
- **可证伪假设**: case 8 (B16/L4096, 高并发 2048 CTA) 的 combined kernel 寄存器压力(92 reg)压低 occupancy(warps=5)；split 成 full-only(70 reg, warps=7) 提 occupancy → 提速。tail 由 tail-kernel 处理（reducer live-skip 跳空 split），boundary-safe。
- **资源诊断** (`-resource-usage`): 全部 token-parallel 变体 0 bytes stack（无 spill）。combined KV4 `<4,8,*,false,false,false>`=92 MTreg/warps=5；separate-tail full=70 reg/warps=7。KV8 已用 separate-tail(60 reg/warps=8)，KV4 case 8 是唯一未用的长高并发 KV4。
- **correctness**: CPU 14/14；GPU full-length 14/14、boundary 14/14、random 14/14。case 8 boundary 从 full-only 的 FAIL(3.75) 修正为 PASS。
- **本地 A/B** (control #106069 vs cand, 11-13 rounds):
  | case | cand/ctrl p50 | p10/p90 |
  |---:|---:|---:|
  | 8 | **0.941** | 0.937/0.945 |
  | 5 | 1.005 | 0.975/1.025 |
  | 11 | 1.000 | 1.000/1.001 |
- **case 10/14 扩展被拒**: 同 gate 加 B1 case 10(L8192)/14(L61519) 后 A/B **回退**（case10 p50=1.051、case14=1.019）。原因：B1 grid 仅 4 CTA/split，launch/latency-bound 而非 occupancy-bound，额外 tail launch 反而拖慢。**occupancy 杠杆仅对高 batch KV4(case 8) 有效，B1 KV4 无效**。故只保留 case 8。
- **OJ**: **#106116 Accepted 57.43**（14/14），但低于 control #106069 的 57.57，故**拒绝作为 baseline**。目标 case 8 在 OJ 为 `175 μs/38 分`，未超过 control 的 `174 μs/38 分`；case 11 为 `443 μs/35 分`（control `438 μs/36 分`）。说明本地 case-8 +6.3% 虽紧凑，却没有在该次 OJ 环境中转化为稳定的最终计分收益。raw 与逐提交源已归档，提交源 SHA `52cedc…` 已核对。工作文件已恢复 #106069 (`a8101a…`)。

### exp4-case8-inplace-q-combined  (REJECTED locally, 2026-08-08)
- **父/control**: #106069 (`a8101a3f…`)；候选 `/tmp/case8_inplaceq.cpp`，SHA `5fc5f4e851240c26cb6f689fc08deee433627667cf7558e46cfbd52484e58e95`，`.so`=`build/cuda_case8_inplaceq.so`。
- **唯一差异 / 假设**: case 8 保持 single combined launch，但把 `<4,8,true>` 改为 `<4,8,true,false,false,true>`，移除该 launch 的 2 KiB dynamic Q；复用 `s_k` staging（与 #106069 case 11 已验收的 Q alias 相同），希望越过 residency/resource 阈值而避免 #106116 的 tail-launch 成本。
- **correctness**: full、boundary、random 均 14/14 PASS。
- **本地交错 A/B**（13 rounds）: case 8 candidate/control p10/p50/p90=`1.0006/1.0016/1.0052`；case 5=`0.9736/1.0072/1.0352`、case 11=`0.9997/1.0003/1.0010`，均无正向收益。
- **结论**: **REJECTED**。case 8 的 combined kernel 不因 Q alias 降到更高 residency；不要为 case 8 默认启用 `INPLACE_SHARED_Q`。

### exp5-selected-full-page-qk-pair-ilp  (submitted, 2026-08-08)
- **父/control**: #106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。
- **候选 SHA**: `ab6ba5d7b87b5c31da7f9bd60684f760b5b5596287638f67268a910cd07c7996`；`.so`=`build/cuda_qkpair_selected.so`。
- **唯一假设**: full-page QK 两个独立 token dot 交错发射，重叠 packed FMA 与 16-lane shuffle 的指令延迟，保持每个 dot 的输入、FMA 次序和 softmax 数学不变。仅静态选择 `KV_HEADS==8 || SYNC_COPY`（所有 KV8 + sync KV4 case 8/11）；async KV4 case 3/5/10/14 保留原循环，规避 broad probe case 10 p50 `1.0094` 的回退。
- **correctness**: CPU `tests/test_kernel_logic.py` 14/14；GPU full/boundary/random 14/14（全均 PASS）。
- **本地交错 A/B**（selected, 13 rounds）: case 4=`0.9770`、8=`0.9975`、9=`0.9968`、11=`0.9973`、12=`0.9975`、13=`0.9966`；非目标 async KV4 case 3/5/10/14=`1.0054/1.0063/0.9970/0.9995`（短 case 噪声范围，未见系统性回退）。
- **OJ**: **#106170 Accepted 57.57**（14/14），与 #106069 并列、未刷新，故**不替代 baseline**。case 4 `30→29 μs`，但 case 8 `174→179 μs`、case 11 `438→440 μs`、case 12 `533→537 μs`；本地微增益没有稳定跨过 OJ timing tier。归档源 `solutions/archive/2026-08-09-submissions/cuda_106170.cpp` SHA `ab6ba5d7…` 已核对；工作文件已恢复 #106069 `a8101a…`。
- **QK/PV phase diagnostics**（#106069 control、timing-only invalid-output probes，13-round interleaved）: 删除 full-page QK→case 8/11 ratio p50=`0.743/0.720`（上界 `25.7%/28.0%`）；删除 full-page PV→`0.960/0.959`（上界 `4.0%/4.1%`）。资源变化使这不是可直接加和的精确占比，但方向明确：长 KV4 的主要剩余成本是 scalar **QK**，PV / loader / z-merge 不是下一架构突破优先级。

### exp6-case11-warp32-state-elision  (REJECTED at resource gate, 2026-08-09)
- **父/control**: #106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。
- **候选 SHA**: `e9b4d6576f639fd96873968d2bed40ff6366afd232ee39062b75202b955970a9`；`.so`=`build/cuda_case11_warp32.so`。
- **唯一假设**: 仅 case 11 (`B16/L12251/KV4`) 把 producer 从 `dim3(16,8,2)` 改为 256-thread 的 warp-per-head `(32,8,1)`：lane 持有 `{2*lane,2*lane+1,2*lane+64,2*lane+65}` 四维，full-mask 32-lane XOR 归约 16 个 token，直接加载 Q，消除 KV4 Q staging 和 CTA 内 two-z `(m,l,acc)` shared-memory merge。保留 64 个 full split + live tail、sync `uint4` K/V loader 宽度、base-2 FP32 softmax、partial ABI 和 reducer。
- **#104263 边界**: 本候选不是重试受禁的 KV8 8-lane quad-token 路径：没有 width-8 shuffle、subgroup-owned logit broadcast 或 lane-dependent source lane；每个 dot 的所有 32 lanes 都执行固定 `16,8,4,2,1` XOR。该 full-warp 4-dim 归约也已有 `paged_decode_split_kernel` 运行前例。#104263 的失败不提供本候选的性能结论。
- **correctness**: CPU `tests/test_kernel_logic.py` 14/14 PASS；候选 GPU case 11 full-length PASS（match=1.0，max_err=`2.441406e-04`，finite=True）。未继续全量 correctness，因为资源门槛已明确否定可证伪的 occupancy/state-traffic 机制。
- **资源**（`-resource-usage`，0 B stack）: full-only candidate=`118 MTreg / 8192 B / staticMaxWarps=4`，而 #106069 case-11 full-only=`70 MTreg / 8320 B / staticMaxWarps=7`；tail candidate=`48 MTreg / 8192 B / 8`，control tail=`42 MTreg / 8320 B / 7`。full-only producer 覆盖 case 11 的主工作量，寄存器和 residency 明显反向，直接拒绝。
- **结论**: **REJECTED，未跑 A/B，未提交**。`score[16]` 与 full-warp QK codegen 抵消了 `q_reg/acc` 缩减并把 full producer 从 70 到 118 MTreg；同时 QK shuffle 工作理论上从每 thread/page 32 增至 80。不得在本轮用 split/reducer/loader/launch 参数补偿；候选源码已归档 `solutions/archive/2026-08-09-experiments/cuda_case11_warp32_state_elision.cpp`，工作文件恢复 #106069。

### exp7-loader-and-cta-probes  (REJECTED direction probes, 2026-08-09)
- **父/control**: #106069。两个旧 `.so` 没有足够的源码身份，只作为方向筛选，不作为可归因候选或提交证据。
- `build/cuda_maca_case11_fp32k.so`：case 11 candidate/control p50=`1.4692`。用 FP32 shared K staging 换取少量转换消除会大幅增加 shared 流量，关闭该方向。
- `build/cuda_maca_case14_two_page_512.so`：case 14 p10/p50/p90 约=`1.1759/1.1793/1.1863`。512-thread/two-page 组织明显回退，不重构、不提交。

### exp8-case11-qk-group-interleave  (REJECTED, 2026-08-09)
- **父/control**: #106069。目标是验证同时保持更多独立 token dot 是否能隐藏 packed-FMA/shuffle latency。
- **8-token候选**: SHA `e12c22a8921bc647d615b282431e242d3d0a09b836402acf3a93da540cef1ee4`，归档 `solutions/archive/2026-08-09-experiments/cuda_case11_qk_wave8_interleave.cpp`；CPU 14/14、GPU case 11 PASS，资源 `70→76 MTreg`、static warps `7→6`，case 11 p10/p50/p90=`1.0269/1.0275/1.0289`。
- **4-token候选**: SHA `57bdb333b72fef22902a8bc088eff0bdbc729a7a4503e924f0ad7d0890fede78`，归档 `solutions/archive/2026-08-09-experiments/cuda_case11_qk_group4_interleave.cpp`；CPU 14/14、benchmark correctness PASS，资源 `74 MTreg/6 warps`，case 11 p10/p50/p90=`1.0116/1.0123/1.0132`。
- 结合 #106170 的 2-token 约 `0.2–0.3%` 微增益，2/4/8-token 转折已经完整：扩大 live dots 单调增加寄存器压力并回退，不再扫描更多 group size。

### exp9-case4-only-qk-pair-ilp  (submitted, REJECTED, 2026-08-09)
- **父/control**: #106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。
- **候选**: SHA `951489e9f42778bd12ff66f64d99804b9bdefca0b7bed66fff79c89d70a56cda`；`.so`=`build/cuda_case4_pair_qk_only_951489e9.so`；提交归档 `solutions/archive/2026-08-09-submissions/cuda_106503.cpp`。
- **唯一差异**: 新增编译期 `PAIR_QK_INTERLEAVE`，只在 case 4（B64/L64/KV8）的 `<8,4,false,...>` 实例启用 #106170 双-token full-page QK，所有其他 launch 保持 false。
- **correctness**: CPU 14/14；GPU full-length、boundary、random 均 14/14 PASS。
- **本地 A/B**: case 4（13 rounds）p10/p50/p90=`0.9710/0.9758/0.9863`；非目标 case 8/11/12（9 rounds）p50=`0.9974/1.0005/0.9998`，中性。
- **OJ**: #106503 Accepted 57.57，14/14；case 4 仍 `30 μs`，其余 C7/C8/C11/C12 为 `322/180/442/539 μs`，总分与 #106069 并列。局部隔离没有稳定跨过 timing tier，拒绝为 baseline；raw 与源码哈希已核对，工作文件恢复 #106069。

### exp10-case11-head4-z4  (REJECTED locally, 2026-08-09)
- **父/control**: #106069；候选 SHA `2a873decfbf2d2fbe222614cdc487e9a2e768b4998b1e3797d0e1125afa213b0`，`.so`=`build/cuda_case11_head4_z4.so`。
- **唯一假设**: case 11 每个 KV head 从一个 `(16,8,2)` CTA 拆为两个 `(16,4,4)` head-group CTA；每个 z 从串行 8 token 降为 4 token，保留 16-lane/8-dim dot、in-place Q、FP32 softmax、split/reducer ABI，但 K/V page 被两个 CTA 重载。
- **correctness**: CPU 14/14；GPU case 11 full/boundary/random 全 PASS，max error 分别 `2.44e-4/7.81e-3/1.95e-3`。
- **资源**: full `70→58 MTreg`、tail `42→34`，均 0 B stack；shared 仍 8320 B，staticMaxWarps 仍为 7，未跨 occupancy 档。
- **A/B**: case 11（13 rounds）p10/p50/p90=`1.1267/1.1281/1.1298`，稳定回退约 12.8%。page 重载与 CTA 数翻倍明显超过串行链缩短收益。
- **结论**: 不提交；关闭“通过拆 query-head CTA group 增加 z partition、但重复 loader”的布局。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4.cpp`，SHA-256 已核对；工作文件恢复 #106069。

### exp11-case11-split-qk-acc  (REJECTED locally, 2026-08-09)
- **父/control**: #106069；候选 SHA `c8d118ad6e1b75dd3550f4a58db9867ea07113622ad272c3b0fa068b606e0f81`，`.so`=`build/cuda_case11_split_qk_acc.so`。
- **唯一假设**: 只在 case-11 full-page QK 内把 4 个 packed FMA 从单一 accumulator 链改为两组交替 accumulator（各 2 级）后合并；不增加 live token，不改 loader/CTA/split/tail。
- **资源/correctness**: `70→72 MTreg`，仍 7 warps/8320 B/0 B stack；CPU 14/14，GPU case 11 full PASS（max error `2.44e-4`）。
- **A/B**: case 11（13 rounds）p10/p50/p90=`1.0137/1.0148/1.0173`，回退约 1.5%。额外 accumulator 与合并指令超过依赖链缩短收益。
- **结论**: 不提交；结合 2/4/8 live-token interleave，关闭当前 scalar QK source-scheduling family。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_split_qk_acc.cpp`，SHA-256 已核对；工作文件恢复 #106069。

### exp12-case11-bitcast-qk  (NEUTRAL, 2026-08-09)
- **父/control**: #106069；候选 SHA `5f7d2178ae4cdd8cffbec88502b458f930ebbf11a56cadd2ccff6b67d6176549`，`.so`=`build/cuda_case11_bitcast_qk.so`。
- **唯一假设**: 只在 case-11 full QK 的 K 解包中，以 `uint32` shift/mask + `__uint_as_float` 表达 BF16→FP32 的位等价转换；Q、PV、FMA 顺序、loader/CTA/split 不变。
- **资源/correctness**: 与 control 相同的 `70 MTreg/7 warps/8320 B`；CPU 14/14、GPU case 11 full PASS（max error `2.44e-4`）。
- **A/B**: p10/p50/p90=`0.9976/0.9997/1.0008`，完全中性，说明 MACA 已把原 `__bfloat162float` 路径优化到等价成本。
- **结论**: 不提交；关闭纯源码 BF16 bitcast 改写。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_bitcast_qk.cpp`，SHA-256 已核对；工作文件恢复 #106069。

### exp13-case11-headpair-reuse  (submitted, locally positive / OJ rejected, 2026-08-09)
- **父/control**: #106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。
- **候选**: SHA `482d4557ea752e58ecbdc71fc6b09e4f11339648a4742dfa28c2da8bb7272db7`；`.so`=`build/cuda_case11_headpair128.so`；提交 #106556；不可变源码 `solutions/archive/2026-08-09-submissions/cuda_106556.cpp`。
- **唯一假设**: case 11 改用 128-thread `(16,4,2)` CTA，每线程同时维护两个 query head。一个 CTA 仍覆盖完整 `(b,kv_head,split)`，每页 K/V 仍只加载一次；同一个 K/V packed row 的 shared load 与 BF16 解包同时服务两个 head，将重复转换/LDS 理论上减半。它不同于 exp10 的 `(16,4,4)` 两-CTA head group，不重复 page loader。
- **生成代码资源**: full=`100 MTreg/50 STreg/8320 B/staticMaxWarps=4`，tail=`60/48/8320 B/7`；control full/tail=`70/42 MTreg`。full 候选每 block 2 waves、可驻留 2 block，control 每 block 4 waves、只能驻留 1 block，因此两者实际都是 4 active waves，资源增长未直接降低活动 wave 数。
- **correctness**: CPU 14/14；同一候选 `.so` 的 GPU full/boundary/random 均 14/14 PASS，case 11 max error 分别 `2.44e-4/7.81e-3/1.95e-3`，padding trap 与 tail mask 正确。
- **本地交错 A/B**: case 11 首轮 p10/p50/p90=`0.9477/0.9484/0.9494`；扩展复测=`0.9465/0.9472/0.9479`，稳定加速约 5.3%。非目标 case 4/8/12 p50=`0.9949/0.9992/0.9998`，中性。
- **OJ**: #106556 14/14 Accepted、`57.43`；case 11 为 `452 us/35`，没有超过 #106069 的 `438 us/36`，其余 case 为 `3,4,10,30,26,33,321,175,322,57,452,533,294,297 us`。raw/code/hash 已核对，拒绝为 baseline。
- **结论**: 这是首个真实减少 K/V unpack 并在本地显著正向的 head-pair 架构，不能与“重复 loader”失败路线合并关闭；但 exact `100-reg + 8-token/head` 版本不能原样复投。下一步只允许改变其关键资源/工作粒度前提（降低 full register、调整 pair/z token 粒度或减少同时 live score），仍以 #106069 做最终 control。

### exp14-case11-shared-score-producer  (REJECTED locally, 2026-08-09)
- **父/control**: #106069；候选 SHA `ae1696289bd55ec2ee509ec1b3f488688dc627dc3e7f8dabb112e40a4a245c41`，`.so`=`build/cuda_case11_score_producer.so`。
- **唯一假设**: 在 256-thread CTA 内只让 4 个 head-pair producer 做 QK，把 32 个 score 写入新增 512 B shared，8 个 consumer 再读取并做 softmax/PV，试图减少重复 K 解包与 QK worker。
- **资源/correctness**: full/tail=`86/36 MTreg`，shared=`8832 B`；GPU case 11 full PASS。
- **A/B**: case 11 p10/p50/p90=`1.6010/1.6029/1.6040`，稳定回退约 60%。
- **结论**: shared score handoff、额外同步和 producer/consumer 不均衡远超理论收益，不提交并关闭 exact 数据流。实现模板仍存在于 #106584 提交源码，但未实例化/未 launch，不影响该提交运行时归因。

### exp15-case11-headpair-chunk4  (submitted, locally positive / OJ rejected, 2026-08-09)
- **父/control**: #106069；候选 SHA `98deba6c92a9416da6ed05ca8c5b175ba0e6fa8ff6fc9b485089467b9910c8ef`，`.so`=`build/cuda_case11_headpair_chunk4.so`；提交 #106584；不可变源码 `solutions/archive/2026-08-09-submissions/cuda_106584.cpp`。
- **唯一假设**: 保持 #106556 的 `(16,4,2)` 128-thread head-pair、不重复 loader 和每线程两个 query head，只把每个 z 的 8 个同时 live score拆成两个顺序 4-token chunk，以降低 register/live range。
- **资源/correctness**: full/tail=`82/64 MTreg`、8320 B shared、staticMaxWarps=`5/7`；CPU 14/14，GPU full/boundary/random 均 14/14 PASS。
- **本地 A/B**: case 11 补测 p10/p50/p90=`0.9689/0.9703/0.9733`，稳定快约 3.0%；case 4/8/12 p50=`0.9973/0.9988/1.0002`，中性。
- **OJ**: #106584 14/14 Accepted、`57.29`；case 11=`467 us/34`，其余为 `3,4,10,30,25,33,322,179,322,60,532,296,299 us`。raw/逐提交源码/工作文件 SHA 三者一致。
- **结论**: 降低同时 live score 与 full register 仍未消除本地/OJ 反转，甚至比 #106556 的 `452 us` 更差；关闭 z=2 下 4/8-token live-score exact 扫描。跨-head unpack reuse 只有在改变 token partition 数、CTA 工作划分或状态数据流后才值得重开。

### exp16-case11-headpair-z4  (submitted, NEW BEST, 2026-08-09)
- **父/control**: #106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。
- **候选**: SHA `bc5b3a4de04e68161342b902c901deb480c358e1b2cc3c8280ec44b0f125c5f3`；`.so`=`build/cuda_case11_headpair_z4.so`；提交 #106626；不可变源码 `solutions/archive/2026-08-09-submissions/cuda_106626.cpp`。
- **唯一假设**: 保留一次 K/V load/unpack 服务两个 query head，将 128-thread `(16,4,2)` 改为 256-thread `(16,4,4)`，让每个 z 真正只负责 4 token。四个 z-state 先由 z0/z1 各自合并 z2/z3，再由 z0 合并 z1，复用原 8 KiB K/V shared 而不扩成 16 KiB。
- **资源/correctness**: full/tail=`84/50 MTreg`、`48/42 STreg`、0 B stack、8320 B shared、staticMaxWarps=`5/7`；CPU、GPU full/boundary/random 全部 14/14 PASS。
- **本地 A/B**: case 11 首轮 p10/p50/p90=`0.9520/0.9531/0.9533`，补测=`0.9516/0.9528/0.9542`；case 4/8/12 p50=`0.9992/1.0005/0.9996`。
- **OJ**: #106626 14/14 Accepted、**`57.64`**；各 case=`3,4,10,30,25,33,322,174,322,57,417,533,294,296 us`。case 11 `438→417 us`、`36→37` 分，raw/code/workfile SHA 三者一致。
- **结论**: 256-thread/z4 与两级 reducer 成功把 head-pair reuse 转成真实 OJ 收益，#106626 替代 #106069 成为新 baseline。下一步从此快照探索 case 8 扩展、case 11 reducer/partial/tail 降本，以及独立的 B1 case 14 路线。

### exp17-case8-headpair-z4  (submitted, OJ pending, 2026-08-09)
- **父/control**: #106626，SHA `bc5b3a4de04e68161342b902c901deb480c358e1b2cc3c8280ec44b0f125c5f3`。
- **候选**: SHA `fb2e0ca452ef8b39b204e8a172d9afec3f12b010924a245d4947ad0e7d725db3`；`.so`=`build/cuda_case8_headpair_z4.so`；提交 #106781。第一次同源 #106684 因长时间 Pending 按用户要求取消，#106781 为完全相同源码的重提。
- **唯一假设**: 只把 #106626 已在 case 11 真实获益的 `(16,4,4)` head-pair/z4 full/tail producer 扩展到 case 8 (`B16/L4096/KV4`)；split 仍为 48，其他 shape 不变。
- **correctness**: CPU、GPU full/boundary/random 均 14/14 PASS。
- **本地 A/B**: case 8 首轮 p10/p50/p90=`0.9192/0.9221/0.9255`；在后续组合候选中复测=`0.9206/0.9233/0.9261`。case 11 p50=`0.9999`，非目标 case 4/12 中性。
- **状态**: #106781 自 2026-08-09 05:44:40 UTC 起仍为 Pending；不再为同一 SHA 创建重复提交。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case8_headpair_z4.cpp`。

### exp18-case11-headpair-z4-split48  (locally positive, 2026-08-09)
- **父/control**: #106626；本实验叠加在 exp17 的精确源码上，但新增差异只命中 case 11，因此 case-11 A/B 仍以 #106626 为唯一 control。
- **候选**: SHA `445e7046bd994d186d72957dcbd55fe16fa6549797528f0bd3b63db6bc55cff3`；`.so`=`build/cuda_case11_headpair_z4_split48.so`。
- **唯一假设**: 新 head-pair/z4 producer 的最佳 split 不必继承旧 producer。只把 case 11 从 64 splits/12 pages 调到 48 splits/16 pages，减少 25% producer CTA、partial write 和 reducer 输入；`48×16=768` 恰好以 16-page chunk 覆盖 766 个 page。
- **split 扫描**: 相对 64-split control 的 p50 ratio：32=`0.9965`、40=`0.9998`、48=`0.9900`（21-round 复测仍 `0.9900`）、56=`0.9996`、64=`1.0000`。只有 48 的 16-page 对齐点稳定正向，停止继续细扫。
- **correctness**: CPU 14/14；同一最终 `.so` 的 GPU full/boundary/random 均 14/14 PASS；同进程 `full→boundary→full→random→full` 全 PASS，排除 static workspace 旧 partial 污染。
- **组合 A/B**: case 4/8/11/12 p10/p50/p90 分别为 `0.9975/1.0008/1.0069`、`0.9206/0.9233/0.9261`、`0.9889/0.9897/0.9910`、`0.9965/0.9996/1.0004`。case 8 快约 7.7%、case 11 快约 1.0%，非目标中性。
- **结论**: 达到真实提交门槛；完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_case11_headpair_z4_split48.cpp`，工作文件保持候选 SHA，等待 OJ 判定。

### exp19-case14-headpair-z4-combined  (REJECTED locally, 2026-08-09)
- **父/control**: #106626；候选叠加在 #106903 源码上，但新增 dispatch 只命中 case 14。候选 SHA `7308ce75392ef5ae4e2ed242d42b354c8f78483adb8929098fb1e8b64894f922`，`.so`=`build/cuda_case14_headpair_z4_combined.so`。
- **唯一假设**: case 14 (`B1/L61519/KV4`) 也能从 case 8/11 已有效的跨-head K/V unpack reuse 获益。只把该 shape 派发到 `(16,4,4)` head-pair/z4 的 combined `<false,false>` kernel，保留 256 splits、combined full/tail 和 reducer policy；未叠加 B1 已有回退线索的 separate-tail launch。
- **correctness**: CPU 14/14；GPU case 14 full PASS，match=`1.0`、max error=`1.220703e-04`、finite=True。
- **A/B**: case 14（13 rounds）p10/p50/p90=`1.0119/1.0195/1.0235`，稳定回退约 2.0%。
- **结论**: B1 上 exact combined head-pair/z4 不获益；不提交，也不再叠加 separate-tail。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_headpair_z4_combined.cpp`。

### exp20-case14-split257  (locally positive, 2026-08-09)
- **父/control**: #106903 候选源码（case 8 head-pair/z4 + case 11 split48），case 14 运行路径与 #106626 相同；control `.so`=`build/cuda_case11_headpair_z4_split48.so`。
- **候选**: SHA `42cb6e435ec93f8a07ccf001a798d5637882c0b64f30348ea04ea2bd01410c99`；`.so`=`build/cuda_case14_split257.so`。
- **唯一假设**: case 14 的 cap-derived 256 splits 会形成 16 pages/split，但 3845 个 page 只需 241 个 live split。将 split 改为 257 会跨到 15 pages/split，形成 257 个 live producer，CTA 总数仅从 1024 增到 1028，却缩短每 CTA 串行 page loop。
- **离散 sweep**: 相对 256 control，241/16-page p50=`0.9989`，257/15-page=`0.9589`（21-round 复测=`0.9563`），275/14-page=`0.9811`，296/13-page=`0.9910`。清除空 CTA 本身中性；15-page 点在 producer 串行度、并发与 reducer 之间形成明确最优，停止继续细扫。
- **correctness**: CPU 14/14；同一最终 `.so` 的 GPU full/boundary/random 全部 14/14 PASS；case 14 同进程 `full→boundary→full→random→full` 全 PASS。
- **组合 A/B**: 相对 #106626，case 4/8/11/14 p10/p50/p90=`0.9811/0.9992/1.0101`、`0.9168/0.9219/0.9274`、`0.9890/0.9903/0.9912`、`0.9525/0.9557/0.9591`。三个目标 case 同时正向，非目标中性。
- **结论**: 达到真实提交门槛；完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_split257.cpp`，工作文件保持候选 SHA，等待 OJ 判定。

### exp21-case10-split171  (REJECTED locally, 2026-08-09)
- **父/control**: #106930 候选，case 10 与 #106626 相同的 token-parallel 128-split/4-page 路径；control `.so`=`build/cuda_case14_split257.so`。
- **候选**: SHA `aa61eddec96ad5a4c886a4e4fdb5d21cbc88c123e0eda083a08e2eb4fbcc0b2f`；`.so`=`build/cuda_case10_split171.so`。
- **重开前提**: 旧 3-page 负结果使用 `n_split=192` 且发生在 token-parallel 之前；本次 producer 架构不同，并使用精确 171 live splits 避免 21 个空 CTA，因此旧实验不能直接否定。
- **唯一假设**: 把 case 10 从 128/4-page 调到精确 171/3-page，以更多 live producer 和更短 page loop 换取额外 partial/reducer 成本。
- **correctness/A-B**: CPU 14/14、GPU case 10 full PASS；17 rounds p10/p50/p90=`1.0633/1.0831/1.1005`，稳定回退约 8.3%。
- **结论**: 新 token-parallel 前提下 3-page 仍明确负向；关闭 case 10 split 重扫，继续保留 128/4-page。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case10_split171.cpp`。

### exp22-case5-split5  (locally positive, 2026-08-09)
- **父/control**: #106930 候选，case 5 与 #106626 相同的 token-parallel 3-split/3-page 路径；control `.so`=`build/cuda_case14_split257.so`。
- **候选**: SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；`.so`=`build/cuda_case5_split5.so`。
- **唯一假设**: case 5 只有 9 个 cache page；把 3 splits/3-page 提高到 5 live splits/2-page，以 192→320 producer CTA 和更短 page loop 换取小 split reducer 的少量额外工作。
- **离散 sweep**: split5 初测 p50=`0.9443`，31-round/200-iteration 复测 p10/p50/p90=`0.9126/0.9345/0.9704`；split9/1-page=`0.9859/1.0242/1.0580`，已越过最优点。保留 split5，不继续插值。
- **correctness**: CPU 14/14；同一最终 `.so` 的 GPU full/boundary/random 全部 14/14 PASS；case 5 同进程 `full→boundary→full→random→full` 全 PASS。
- **结论**: 达到真实提交门槛并与 case 8/11/14 正收益组合；完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case5_split5.cpp`，工作文件保持候选 SHA，等待 OJ 判定。

### exp23-case6-split12  (REJECTED locally, 2026-08-09)
- **父/control**: #106947 候选，case 6 使用 token-parallel 8 splits/3-page；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `98704dd09e17e2ccf18794558dd40ac4bd46c4535f437658228b4fb81e6b057b`；`.so`=`build/cuda_case6_split12.so`。
- **唯一假设**: 把 23-page case 6 从 8 live splits/3-page 提高到 12/2-page，producer CTA 1024→1536，且 reducer 仍处于 `<=16` 的 shuffle-only 路径。
- **correctness/A-B**: CPU 14/14、GPU case 6 full PASS；31 rounds p10/p50/p90=`1.0568/1.0638/1.0689`，稳定回退约 6.4%。
- **结论**: 额外 producer/partial 成本超过缩短 page loop 的收益；结合旧 6-split/4-page 回退，case 6 的 8/3-page 点两侧均已关闭。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case6_split12.cpp`。

### exp24-case13-split264  (REJECTED locally, 2026-08-09)
- **父/control**: #106947 候选，case 13 为 token-parallel + separate-tail 的 256-grid/15-page 路径；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `06f18cfeb5fe51513c2d8c1c0954b9fca73a0ee6f6ce87ea831042a327a3cb2f`；`.so`=`build/cuda_case13_split264.so`。
- **唯一假设**: 3686-page case 13 从 256 grid（约 246 live）跨到精确 264 live splits/14-page，以更短 page loop 和更多 B1 producer 复现 case14 的离散边界收益。
- **correctness/A-B**: CPU 14/14、GPU case 13 full PASS；21 rounds p10/p50/p90=`1.0155/1.0196/1.0219`，稳定回退约 2.0%。
- **结论**: B1 KV8 的额外 producer/reducer 成本更高，case14 机制不能跨 KV-head 布局外推；恢复 256/15-page。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case13_split264.cpp`。
- **验证工具修复**: 本实验发现 `tests/c500_case_manifest.py` 对生产源码 case7/8/9/13 的最终 split override 漂移；已同步为 14/48/24/256（实验期间 case13 临时264），CPU 语义测试现报告真实生产 split。

### exp25-case8-headpair-z4-split-boundary  (REJECTED locally, 2026-08-09)
- **父/control**: #106947 候选，case 8 使用 head-pair/z4 + separate-tail 的 48-grid/6-page 配置；control `.so`=`build/cuda_case5_split5.so`。
- **52-split 候选**: SHA `2e065e528196ddd8c0ff3dc7cd96a3a563f8f25fe588ed96e93c082b37cdfaa5`，`.so`=`build/cuda_case8_headpair_z4_split52.so`；CPU 14/14、GPU case 8 full PASS，A/B p10/p50/p90=`1.0217/1.0255/1.0300`。
- **43-split 候选**: SHA `d47ce21692873581282ad72aee184bf31aacfee9f64bf1ce09070eafdd128b70`，`.so`=`build/cuda_case8_headpair_z4_split43.so`；CPU 14/14、GPU case 8 full PASS，A/B=`0.9966/1.0009/1.0040`。
- **机制结论**: 52/5-page 的额外 live producer 与 reducer 成本导致约2.6%回退；43/6-page 只去掉48-grid中的5个空 split而完全中性。保留48/6-page，不再细扫该 head-pair split 区间。
- **归档**: 完整候选源码 `cuda_case8_headpair_z4_split52.cpp` 与 `cuda_case8_headpair_z4_split43.cpp`。

### exp26-case11-group8-reduce49  (NEUTRAL, 2026-08-09)
- **父/control**: #106947 候选，case11 split48 + live tail共49 partial，默认使用512个 one-CTA/head reducer；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `dbff3f247fbcd382f4a8b3ef0ea3f17b8a1ec7a727d8c2a6c45ecfb15fddff83`；`.so`=`build/cuda_case11_group8_reduce49.so`。
- **唯一假设**: 将既有 group8 reducer 的动态 shared 路径精确扩展到 case11的49 splits；约3.1 KiB shared，把 reducer grid从512 CTA降到64 CTA，producer/split/partial ABI不变。
- **correctness/A-B**: CPU14/14、GPU case11 full PASS；21 rounds p10/p50/p90=`0.9988/1.0002/1.0031`，完全中性。
- **结论**: reducer CTA数量不是当前case11端到端瓶颈；不提交，不扩展到同为49-grid的case8。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_group8_reduce49.cpp`。

### exp27-case5-headpair-z4-combined  (REJECTED locally, 2026-08-09)
- **父/control**: #106947 候选，case5 split5 + async combined token-parallel；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `8f7ad8b8d5ffa1cd8fae465b53b5853ea44fb86019664574f896c8ec4dda4120`；`.so`=`build/cuda_case5_headpair_z4_combined.so`。
- **唯一假设**: 保持case5 split5、combined launch和reducer，只换成case8/11有效的`(16,4,4)` head-pair/z4 producer，让一次K/V unpack服务两个query head。
- **correctness/A-B**: CPU14/14、GPU case5 full PASS；31 rounds p10/p50/p90=`1.0082/1.0232/1.0333`，稳定回退约2.3%。
- **结论**: 仅2-page/partial的短路径无法摊销同步head-pair状态成本；不提交，不扩展到更短case3。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case5_headpair_z4_combined.cpp`。

### exp28-case14-inplace-q-split257  (NEUTRAL, 2026-08-09)
- **父/control**: #106947 候选，case14 BSM combined token-parallel + split257，动态Q shared为2 KiB；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `215bd318e4f7be1cdeb2f55af35a1ded6510a0062e62ce233778c48158cd714c`；`.so`=`build/cuda_case14_inplace_q_split257.so`。
- **唯一假设**: 只对case14 combined实例启用`INPLACE_SHARED_Q`，在首个page覆盖前复用K shared保存Q，动态shared从2 KiB降为0；loader/layout/split/reducer不变。
- **correctness/A-B**: CPU14/14、GPU case14 full PASS；21 rounds p10/p50/p90=`0.9957/0.9991/1.0031`，完全中性。
- **结论**: case14未跨资源/occupancy档，动态Q不是端到端杠杆；不提交。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_inplace_q_split257.cpp`。

### exp29-case14-sync-loader-split257  (REJECTED locally, 2026-08-09)
- **父/control**: #106947 候选，case14 BSM async combined producer + split257；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `8d4a66322ff1b4debfbc7bb645f772b776da25b370df9899c74c602e8d30c924`；`.so`=`build/cuda_case14_sync_loader_split257.so`。
- **唯一假设**: 仅将case14的`SYNC_COPY`模板参数从false改为true，用同步`uint4`替代BSM async；CTA布局、Q shared、combined、split257和reducer均不变。
- **correctness/A-B**: CPU14/14、GPU case14 full PASS；21 rounds p10/p50/p90=`1.0041/1.0076/1.0110`，稳定回退约0.8%。
- **结论**: B1 KV4 case14继续保留BSM；长KV8的同步loader结论不能外推到该shape。完整候选源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_sync_loader_split257.cpp`。

### exp30-case14-phase-diagnostics  (TIMING-ONLY, 2026-08-09)
- **父/control**: #106986 待判定组合候选，源码 SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case14_phase_control.so`。
- **目的**: 在 case14 split257 后量化 full-page QK、full-page PV 和最终 split reducer 的端到端上界，决定下一项架构应优化哪一段。三种探针输出故意无效，只用于 timing，不作为 correctness 或提交证据。
- **方法**: 同一来源分别用 `-DXPUOJ_PHASE_PROBE=1/2/3` 构建 no-QK、no-PV、no-reducer；case14 21轮交错、每轮100次。探针保留外围 page pipeline；删除计算会改变资源/codegen，因此 QK/PV 结果只能视为上界，no-reducer 则保持 producer 不变。
- **结果**:
  - no-QK：control/candidate p50=`0.2885/0.1515 ms`，ratio p10/p50/p90=`0.5230/0.5253/0.5282`；QK 上界约47.5%。
  - no-PV：`0.2878/0.2414 ms`，ratio=`0.8358/0.8402/0.8438`；PV 上界约16.0%。
  - no-reducer：`0.2883/0.2640 ms`，ratio=`0.9137/0.9158/0.9185`；最终 reducer 端到端约8.4%。
- **结论**: 当前 B1/KV4 的首要杠杆仍是 scalar QK，且比旧 case8/11 probe 的约26–28%上界更突出；reducer 有可测成本，但不足以替代 QK 架构突破。正式工作源码随后恢复到原 SHA。

### exp31-case14-pair32-fixed-xor-broadcast  (REJECTED locally, 2026-08-09)
- **父/control**: #106986 待判定组合候选，SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `dd73f669812f489ec0d6cbc4d801735d9153dd496c12d1aeb3c4bc73c7ef2a92`；`.so`=`build/cuda_case14_pair32_broadcast.so`。
- **唯一假设**: case14 改用256-thread `dim3(32,4,2)`。每个32-lane x-row的两个16-lane半组各处理一个query head；只让下半组读取shared K/V，再用已验证 full mask 的固定 `xor 16` 传递四个packed `uint32` 给上半组。保持每线程单head、z=2、split257、BSM loader、online softmax、partial ABI和reducer不变，测试shared K/V LDS减半能否抵消固定shuffle成本。它不使用已导致WA的8-lane或lane-dependent source shuffle。
- **correctness**: CPU 14/14；真实C500 case14 full PASS，match=`1.0`、max error=`1.220703e-04`、finite=True。因性能已明确失败，未继续boundary/random。
- **资源**: candidate combined实例=`96 MTreg/52 STreg/8320 B/staticMaxWarps=5`；control=`92/48/8320 B/5`。residency档未变，但寄存器略增。
- **A/B**: case14 21轮、每轮100次，control/candidate p50=`0.2881/0.5296 ms`，ratio p10/p50/p90=`1.8309/1.8377/1.8443`，稳定回退约83.8%。
- **结论**: 固定跨半组packed shuffle远贵于节省的shared LDS；关闭此exact `(32,4,2)` broadcast family，不用split/reducer参数补偿。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_case14_pair32_broadcast.cpp`，工作源码恢复至 `e4827a...de8e`。

### exp32-case14-headpair-z4-split257  (REJECTED locally, 2026-08-09)
- **父/control**: #106986 待判定组合候选，SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `86fae30ec819a259bf278af9d834568f437f7fe26f9a51e9a3c3985ace003b9c`；`.so`=`build/cuda_case14_headpair_z4_split257.so`。
- **重开前提与唯一差异**: exp19 的 B1 head-pair/z4 combined 候选只在256-grid/16-page上测过；exp20已证明scalar split257/15-page快约4.4%。本次保持当前split257、BSM、combined full/tail和reducer，仅把case14 producer换为已有 `(16,4,4)` head-pair/z4，判定新page/scheduling边界是否改变旧结论。
- **correctness**: CPU14/14；C500 case14 full PASS，match=`1.0`、max error=`1.220703e-04`、finite=True。性能明确失败后未继续boundary/random。
- **A/B**: 21轮、每轮100次，control/candidate p50=`0.2898/0.2962 ms`，ratio p10/p50/p90=`1.0207/1.0222/1.0248`，稳定回退约2.2%。
- **结论**: 与exp19在split256的p50 `1.0195`一致，split257未改变B1 head-pair代价；关闭case14 head-pair/z4，无新的资源/数据流前提不得重开。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_case14_headpair_z4_split257.cpp`，工作源码恢复至 `e4827a...de8e`。

### exp33-case14-reducer-vec2  (NEUTRAL, 2026-08-09)
- **父/control**: #106986 待判定组合候选，SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `acf1b18463a7a476ac4c66deff36bb75f2066275025313a41707c79ce4390f98`；`.so`=`build/cuda_case14_reducer_vec2.so`。
- **唯一假设**: 只把case14的257-way final reducer从128线程×每线程1维改为64线程×每线程连续2维；保持32个 `(b,h)` CTA、partial ABI、权重数学和producer不变。用float2读取/双FMA减少partial_acc load指令，并把metadata归约从4 warp降为2 warp，不牺牲B1 block数量。
- **correctness**: CPU14/14；C500 case14 full PASS，match=`1.0`、max error=`1.220703e-04`、finite=True。
- **资源**: vec2=`38 MTreg/36 STreg/staticMaxWarps=8`，scalar=`40/36/8`，静态资源略好但未形成运行收益。
- **A/B**: 31轮、每轮150次，control/candidate p50=`0.2896/0.2899 ms`，ratio p10/p50/p90=`0.9997/1.0016/1.0045`，完全中性。
- **结论**: vector load和更小metadata归约被每线程双维串行工作抵消；不提交，不继续扫描同一64-thread reducer。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_case14_reducer_vec2.cpp`，工作源码恢复至 `e4827a...de8e`。

### exp34-headpair-stage2-row8-barrier-elision  (NEUTRAL, 2026-08-09)
- **父/control**: #106986 待判定组合候选，SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `ab15fc5100c9b25cefed05a604ad32de722163245238bf54b5bc8acab285155a`；`.so`=`build/cuda_headpair_stage2_row8.so`。
- **唯一假设**: head-pair/z4两级state merge中，z1原先把合并结果写到rows0–7，会覆盖z0第一阶段正在读取的z2 state，因此需要pre-store barrier。改为写回z1刚读完且z0未访问的rows8–15，可删除这一道CTA barrier；数学、寄存器、shared大小、producer page loop、partial ABI和final reducer均不变。
- **correctness**: CPU14/14；C500 case8/case11 full均PASS，match=`1.0`，max error分别=`4.882812e-04/2.441406e-04`，finite=True。
- **A/B**: 31轮、每轮100次：case8 ratio p10/p50/p90=`0.9987/1.0009/1.0028`；case11=`0.9992/0.9999/1.0015`，完全中性。
- **结论**: 该barrier不是端到端可见瓶颈；不提交，不继续做同一state-row重排。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_headpair_stage2_row8.cpp`，工作源码恢复至 `e4827a...de8e`。

### exp35-headpair-direct-q  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: #106986 待判定组合候选，SHA `e4827a6542fe9e7280d7a746d56a242311584323ed5f9c47fa843abc335cde8e`；control `.so`=`build/cuda_case5_split5.so`。
- **候选**: SHA `c86788872a0513d63d3f61f7d8c2d9eba487ead2467b00f3943339c1859cf040`；`.so`=`build/cuda_headpair_direct_q.so`。
- **唯一假设**: head-pair/z4原路径由z0把8行Q写入s_k，再由四个z读取，包含2 KiB global→shared staging、shared广播和两道初始CTA barrier。改为每个z直接从global/L2加载两个Q head rows；Q在同一batch的数千split CTA间高度cache复用，额外读取可能低于shared+barrier成本。page loader、QK/PV、z-state merge、split、partial ABI和final reducer均不变。
- **资源**: full从`84 MTreg/48 STreg`降至`82/46`，staticMaxWarps仍5；tail为`50/36`，相比原`50/42`降低ST register，staticMaxWarps仍7；shared仍8320 B。
- **correctness**: CPU14/14；同一候选`.so`的GPU full/boundary/random全部14/14 PASS。case8与case11同进程`full→boundary→full→random→full`全部PASS；padding trap、finite和workspace复用均正确。
- **A/B**:
  - 31轮×100：case8 p10/p50/p90=`0.9915/0.9940/0.9964`；case11=`0.9950/0.9958/0.9962`。
  - 41轮×200复测：case8=`0.9934/0.9942/0.9954`；case11=`0.9951/0.9955/0.9963`。
- **结论**: 两例稳定正向约0.6%/0.45%，达到微秒tier诊断提交门槛。因用户正在排查OJ全局Pending问题，本轮暂停所有OJ操作；工作源码保持候选SHA，平台恢复后先dry-run再提交。完整候选源码归档为 `solutions/archive/2026-08-09-experiments/cuda_headpair_direct_q.cpp`。

### exp36-case14-bf16-normalized-partial  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp35 direct-Q，SHA `c86788872a0513d63d3f61f7d8c2d9eba487ead2467b00f3943339c1859cf040`；control `.so`=`build/cuda_headpair_direct_q.so`。
- **候选**: SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；`.so`=`build/cuda_case14_bf16_partial.so`。
- **唯一假设**: case14 的257个split会物化约4.2 MiB FP32 `partial_acc`。producer仍以FP32计算，但把每个split的`acc/l`归一化后以BF16保存；reducer用完整系数 `l_s * exp(m_s-m)` 合并，保持稳定log-sum-exp数学，仅把workspace acc读写减半。
- **资源/correctness**: producer保持`92 MTreg/48 STreg/8320 B/staticMaxWarps=5`，reducer保持`40/36/8`。CPU 14/14；同一`.so`的GPU full/boundary/random均14/14 PASS。case14 max error分别为`1.22e-4/0/2.44e-4`；同进程`case14 full→case13 full→case14 boundary→full→random→full`全部PASS。
- **A/B**: 相对exp35，21轮×100 p10/p50/p90=`0.9900/0.9930/0.9948`；41轮×200复测约=`0.9880/0.9923/0.9963`，稳定快约0.8%。
- **结论**: 保留为当前本地工作基线；收益来自2-byte partial workspace，不外推到其他shape。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_bf16_normalized_partial.cpp`。

### exp37-case14-bf16-vec2-reducer  (REJECTED, 2026-08-09)
- **父/control**: exp36 normalized-BF16，SHA `eab62e0...`；候选SHA `bc01c38bb6da292b0dc9afd985c91c85d4536aaaaccfb21cb33c85fe8d3fc09c`。
- **唯一假设**: 将case14 reducer改为每线程连续处理2维，以`bfloat162`读acc并把线程数从128降到64；producer、partial格式和数学不变。
- **correctness/A-B**: case14 full PASS；相对scalar-BF16 p10/p50/p90=`0.9981/1.0031/1.0060`。
- **结论**: 轻微回退；关闭同一64-thread/vec2 reducer扫描。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_bf16_normalized_partial_vec2.cpp`。

### exp38-case13-bf16-normalized-partial  (REJECTED, 2026-08-09)
- **父/control**: exp36代码框架，仅把BF16 partial目标shape切换到case13；候选SHA `61941a8de6e6a8c307e80be5596322547010be50ef845593b9d8d4a7f8726c0d`。
- **correctness/A-B**: GPU full/boundary/random全部PASS；两轮相对FP32 case13 control的p50分别为`1.0017`、`1.0021`。
- **结论**: 中性偏慢，不扩展到case13。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case13_bf16_normalized_partial.cpp`。

### exp39-case12-bf16-normalized-partial  (REJECTED, 2026-08-09)
- **父/control**: exp36代码框架，仅把BF16 partial目标shape切换到case12；候选SHA `41c8d2049228dc32208872d3c34b62706d836959609e45219bd5df88769d218a`。
- **correctness/A-B**: GPU full/boundary/random全部PASS；有效交错A/B p10/p50/p90=`1.0064/1.0070/1.0078`，稳定慢约0.7%。两次更重测试因长reference/显存压力未产出最终case行，不是numerical failure，也不纳入结论。
- **结论**: 拒绝；结合case13关闭KV8 normalized-partial扩展。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case12_bf16_normalized_partial.cpp`。

### exp40-case14-bf16-raw-partial  (NEUTRAL VS NORMALIZED, 2026-08-09)
- **父/control**: exp36 normalized-BF16；候选SHA `5d8f931db05420bedf000d7f51bfa0b5fa2a4dfb84a560f925d0a1a04a1c42f4`。
- **唯一假设**: 仍以BF16存case14 partial acc，但保存raw `acc`而非`acc/l`，测试producer reciprocal与reducer权重表达的净成本；workspace字节数不变。
- **correctness/A-B**: full/boundary/random全部PASS。相对normalized-BF16，31轮×150 p50=`0.9983`，41轮×200 p50=`0.9994`，无法稳定分离；相对direct-Q的41轮×200 p10/p50/p90=`0.9877/0.9914/0.9938`。
- **结论**: 进一步确认收益来自2-byte workspace，而非normalized表达；保留验证更完整、数学更清晰的normalized-BF16。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_bf16_raw_partial.cpp`。

### exp41-case14-fp16-normalized-partial  (NEUTRAL, REJECTED, 2026-08-09)
- **父/control**: exp36 normalized-BF16；候选SHA `56493fc078c6fc680a5cda3bb50d63b9df04d197b0cf5f03b54a1a2bc666ecaa`；`.so`=`build/cuda_case14_fp16_normalized_partial.so`。
- **唯一假设**: 保持normalized算法、2-byte workspace和线程布局不变，只把partial acc存储/读取格式从BF16改为FP16，隔离C500两种16-bit转换和load路径。
- **correctness**: CPU 14/14；GPU case14 full/boundary/random均PASS，max error分别为`1.22e-4/0/2.44e-4`。
- **A/B**: 相对normalized-BF16，41轮×200 p10/p50/p90=`0.9959/0.9979/1.0001`；61轮×300复测=`0.9984/0.9995/1.0012`。首轮微增益未复现为稳定分离。
- **结论**: 不替换BF16；相同字节量下格式差异属于噪声层，避免增加双格式生产复杂度。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_fp16_normalized_partial.cpp`；工作文件恢复exp36 SHA。

### exp42-case11-bf16-normalized-partial  (REJECTED, 2026-08-09)
- **父/control**: exp36代码框架，case11生产路径仍以FP32 partial为control；候选SHA `f37a49726c8354cda8bf4a4975ba90dbaf880e272c014008b81444b9bac2bf38`；`.so`=`build/cuda_case11_bf16_normalized_partial.so`。
- **唯一假设**: case11的49个partial会物化约12.25 MiB FP32 accumulator；保持head-pair/z4计算不变，仅将每个split的`acc/l`以BF16保存，并在reducer恢复`l_s * exp(m_s-m)`权重。
- **correctness/A-B**: GPU full/boundary/random全部14/14 PASS；相对FP32 case11 control p10/p50/p90=`1.0067/1.0075/1.0088`，稳定慢约0.75%。
- **结论**: 拒绝。B16 producer/reducer并发和短得多的每split工作使转换成本超过workspace收益。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_bf16_normalized_partial.cpp`。

### exp43-case11-bf16-raw-partial  (REJECTED, 2026-08-09)
- **父/control**: exp42 normalized-BF16，SHA `f37a4972...`；候选SHA `37a94818dfb7d927a9a0783791e81be64f7cb630cc1cf064d4ee8a65681d63df`；`.so`=`build/cuda_case11_bf16_raw_partial.so`。
- **唯一假设**: 保持2-byte workspace，只保存raw BF16 `acc`，去掉producer reciprocal并在reducer按`acc/l`恢复，判断normalized表达是否是case11回退来源。
- **correctness/A-B**: GPU full PASS；相对normalized-BF16=`0.9937/0.9945/0.9956`，但相对FP32=`1.0014/1.0019/1.0025`，仍中性偏慢。
- **结论**: raw表达回收了normalized的转换成本，但没有超过FP32 control；不继续做case11 16-bit partial。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_bf16_raw_partial.cpp`。

### exp44-case8-bf16-raw-partial  (REJECTED, 2026-08-09)
- **父/control**: exp36代码框架，case8 FP32 partial为control；候选SHA `45e0c8c79219ba2576aea5bd7c96e96825ed110bb5a4fa1f3023ba1c039fd918`；`.so`=`build/cuda_case8_bf16_raw_partial.so`。
- **唯一假设**: case8同样有49个partial和约12.25 MiB FP32 accumulator，直接测试开销更小的raw-BF16格式。
- **correctness/A-B**: GPU full PASS；相对FP32 p10/p50/p90=`1.0005/1.0022/1.0043`。
- **结论**: 中性偏慢；结合exp42/43，16-bit partial压缩只在B1 case14正向，不能按workspace总字节盲目扩展到B16 case8/11。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case8_bf16_raw_partial.cpp`。

### exp45-native-fp32-mma-fragment-probe  (CONFIRMED CAPABILITY, 2026-08-09)
- **探针**: `tests/archive/closed-backend-probes/c500_mma_f32_fragment_probe.cpp`（SHA `723d4fb8...172549`）、`tests/archive/closed-backend-probes/c500_mma_f32_fragment_probe.py`（SHA `b3d44dd4...267e`）、`.so`=`build/c500_mma_f32_fragment_probe.so`。
- **目标**: 从runtime而非接口声明恢复`__builtin_mxc_mma_16x16x4f32` fragment布局，并验证它是否真正提供FP32内积精度。
- **fragment映射**:
  ```text
  A_lane = 16*k + row
  B_lane = 16*k + col
  C_lane = 16*(row//4) + col
  C_slot = row%4
  ```
  4096个A/B one-hot组合中恰有1024个产生一个非零输出（其余3072为零），与上式逐项一致。
- **K=128精度**: BF16输入先精确转为FP32后调用原生MMA，四个seed的max error分别为`3.814697e-06`、`5.722046e-06`、`9.536743e-06`、`7.629395e-06`。
- **结论**: 原生FP32 MMA能力真实存在且避开旧BF16-MMA精度墙；后续失败只能否定具体集成数据流，不能否定该指令本身。

### exp46-case14-native-fp32-mma-warp64-v1  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp36，SHA `eab62e0e...`；候选SHA `de1b4559592d9abeb9970139c4619bd8328354ab84df3136a77a308d16732244`；`.so`=`build/cuda_case14_mma_f32_v1.so`。
- **唯一架构假设**: 一个64-lane原生warp完成8-head×16-token QK tile，并由同一warp维护每head 16维PV状态；score通过512 B shared发布，K/V按页同步搬运。
- **资源/correctness**: `100 MTreg / 72 STreg / 10752 B shared / 0 B stack / staticMaxWarps=4`；case14 full PASS，max error=`1.220703e-04`。
- **A/B**: 相对exp36 p10/p50/p90=`1.6687/1.6735/1.6787`。
- **结论**: 数值正确但慢约67%；单warp PV串行度和顺序loader抵消MMA-QK收益。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_mma_f32_warp64_v1.cpp`。

### exp47-case14-native-fp32-mma-token-parallel-v2  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp46；候选SHA `0ba220024c598724c0945d8f935ee6164a5e0158aaf794032d52046ffa1fb76e`；`.so`=`build/cuda_case14_mma_f32_v2.so`。
- **唯一架构假设**: 恢复256-thread token-parallel PV/异步loader，仅由第一64-lane wave生产完整8×16 score tile，再交给全部consumer。
- **资源/correctness**: `138 MTreg / 64 STreg / 10752 B / 0 B stack / staticMaxWarps=3`；case14 full PASS，max error=`1.220703e-04`。
- **A/B**: 相对exp36 p10/p50/p90=`1.9788/1.9832/1.9871`。
- **结论**: 第一wave producer失衡、shared score handoff和寄存器膨胀比v1更差；完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_mma_f32_token_parallel_v2.cpp`。

### exp48-case14-native-fp32-mma-bsm-pipeline-v3  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp46 v1；候选SHA `ac59f3760835c93b3d8ff5376640189b8235109ccfd1cc53dc0778a2b54f3e47`；`.so`=`build/cuda_case14_mma_f32_bsm_pipeline_v3.so`。
- **唯一差异**: 保持v1的64-thread QK/softmax/PV和state布局不变，只把每页同步K/V搬运改为单缓冲BSM流水：当前score发布后预取下一页K，当前PV结束后预取下一页V，下一轮`cp_async_bsm_wait<0>()`等待两者。
- **资源/correctness**: CPU 14/14；case14 full PASS，max error=`1.220703e-04`；目标kernel=`110 MTreg / 80 STreg / 10752 B / 0 B stack / staticMaxWarps=4`。
- **A/B**: 直接相对v1 p10/p50/p90=`0.9331/0.9339/0.9347`，loader流水快约7.1%；但相对exp36仍为`1.5623/1.5652/1.5714`，慢约56.5%。
- **结论**: loader只解释v1回退的一小部分。关闭当前“共享score + 单warp完整PV”集成family，不再用split/loader微调补偿；未来FP32 MMA必须设计不同的score/PV数据流，同时避免单wave producer和16维/head串行PV。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_mma_f32_bsm_pipeline_v3.cpp`。

### exp49-case14-native-fp32-mma-wave-headpair  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp36；候选SHA `87ae7ccef35d149b4a73bf78bc7d2179e3485ba25d14a76daa8b480e9e12589e`；`.so`=`build/cuda_case14_mma_f32_wave_headpair_exp49.so`。
- **关键新前提**: 四个64-lane wave都执行MMA，但每个wave只拥有两个query head并直接完成其scalar PV/output；没有第一wave producer、跨wave score消费或`(m,l,acc)`归约。代价是同一K tile的QK MMA重复四次。
- **资源/correctness**: `155 MTreg / 74 STreg / 8704 B / 0 B stack / staticMaxWarps=3`；case14 full PASS，max error=`1.220703e-04`。
- **A/B**: 相对exp36 p10/p50/p90=`3.3964/3.4054/3.4166`。
- **结论**: 重复四次QK MMA和高寄存器压力远超producer平衡收益；关闭“按query-head分wave、重复完整QK、scalar PV”数据流。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_mma_f32_wave_headpair_exp49.cpp`。

### exp50-case14-native-fp32-mma-qk-pv  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp49代码框架，最终仍以exp36为性能control；候选SHA `750f53501164ff5bb8fdee542842e94b6352092ac43fdc87fde49948c6e993cf`；`.so`=`build/cuda_case14_mma_f32_qk_pv_exp50.so`。
- **关键新前提**: 每个wave负责互不重叠的32个输出维度；QK仍按wave重复，但将score转为FP32 P tile后继续用`mma_16x16x4f32`计算P×V，消除scalar token-by-token PV和跨wave状态归约。
- **资源/correctness**: `153 MTreg / 52 STreg / 10240 B / 0 B stack / staticMaxWarps=3`；case14 full PASS，max error=`1.220703e-04`，同时证明FP32 MMA用于P×V的fragment重排和online-softmax数学正确。
- **A/B**: 相对exp36 p10/p50/p90=`3.6632/3.6711/3.6790`。
- **结论**: P权重shared重排、同步、四次重复QK和FP32 P×V MMA总成本比exp49还高。exp46–50已形成五个正确但全部显著回退的runtime候选；按停滞规则关闭当前case14原生FP32 MMA集成主线。只有新的硬件/编译器证据，或能同时避免QK重复、单wave producer、shared score/P重排和高寄存器state的全新数据流，才允许重开。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_mma_f32_qk_pv_exp50.cpp`。

### exp51-case14-split275  (REJECTED, 2026-08-09)
- **父/control**: exp36 的 case14 split257，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `2280bbad9bc8560a46e8fe4ab76f348a8ec6eb18a33b7a0efecccc8c1fea477d`；`.so`=`build/cuda_case14_split275_exp51.so`。
- **唯一假设**: 仅将 case14 从 257 split/15 pages-per-split 提高到 275 split/14 pages-per-split，保持 BSM、CTA layout、normalized-BF16 partial 和 reducer 不变，验证下一个离散 page 边界能否用更多 B1 producer 并行换取收益。
- **correctness/A-B**: CPU 14/14、GPU case14 full PASS；相对 split257 p10/p50/p90=`1.0229/1.0258/1.0284`，稳定慢约 2.6%。
- **结论**: 拒绝。结合 exp20 已有同源 sweep（相对旧 split256：241=`0.9989`、257=`0.9563`、275=`0.9811`、296=`0.9910`），257/15-page 是已验证的离散最优点；向上、向下邻域均已闭合，不再扫描 case14 split。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_split275_exp51.cpp`。

### exp52-case14-int8-normalized-partial  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp36 normalized-BF16 partial，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `243604528b397a23a7d0d746ae1acdf0a25c21e1d4f96977fab4b425638b6b56`；`.so`=`build/cuda_case14_int8_normalized_partial_exp52.so`。
- **唯一假设**: producer 继续 FP32 计算，但每个 partial head 对 `acc/l` 做 symmetric int8 量化；16 个 tx lane 归约 max-abs，每 head 保存一个 FP32 scale，reducer 按 `int8 * scale * l_s * exp(m_s-m)` 合并。int8 数据和 scale 复用既有 `partial_acc` 分配，不增加 persistent allocation。
- **资源/correctness**: producer=`92 MTreg / 52 STreg / 8320 B / 5 warps`（BF16 control=`92/48/8320 B/5`）；reducer=`50 MTreg / 48 STreg / 8 warps`（control=`40/36/8`）。CPU 14/14；case14 full、boundary、random seed 20260809 全部 PASS，max error 分别为 `1.525879e-04`、`1.562500e-02`、`3.542900e-04`，boundary 最大 tolerance ratio=`0.835`。
- **A/B**: 相对 exp36 p10/p50/p90=`1.0270/1.0278/1.0307`，稳定慢约 2.8%。
- **结论**: 数值上可行但拒绝。每 head max-reduce、scale 和整数转换成本超过 partial traffic 再减半的收益；关闭同一 per-head-scale symmetric-int8 路线，不再通过位宽细扫补偿。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_int8_normalized_partial_exp52.cpp`。

### exp53-case11-headpair-bsm-loader  (NEUTRAL, REJECTED, 2026-08-09)
- **父/control**: exp36 的 case11 head-pair/z4 同步 `uint4` loader，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `17295dfb0f8abcbcfaf734edfbfa450cc3dc9d66adfecfde47f3d16fcba7f46e`；control/candidate `.so`=`build/cuda_case11_headpair_sync_exp53_control.so` / `build/cuda_case11_headpair_bsm_exp53.so`。
- **唯一假设**: 仅让 B16/KV4/L12251 的 head-pair/z4 full/tail page loader 使用 BSM async；case8 仍为同步 `uint4`，direct-Q、split48、two-stage state reducer、partial ABI 和 launch 数不变。关键新前提是 #106626 已把旧 token-parallel 改为 head-pair/z4，因此旧 loader A/B 不能直接否定此布局。
- **资源/correctness**: BSM full=`82 MTreg / 46 STreg / 8320 B / 5 warps`，与同一二进制内的同步 full 完全相同；BSM tail=`50/40/8320 B/7`，同步 tail=`50/36/8320 B/7`，均 0 B stack。CPU 14/14；case11 full PASS，match=`1.0`、max error=`2.441406e-04`、max tolerance ratio=`0.015`。
- **A/B**: 21 rounds × 100 iterations，相对字节精确重建的 exp36 control，p10/p50/p90=`0.9994/1.0002/1.0012`，完全不可分离。
- **结论**: 不提交，也不追加 boundary/random；候选已在 full correctness 后因性能门槛失败。关闭 case11 head-pair/z4 的 exact BSM loader 替换，继续保留同步 `uint4`。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case11_headpair_bsm_exp53.cpp`。

### exp54-case14-two-head-bf16-reducer  (NEUTRAL, REJECTED, 2026-08-09)
- **父/control**: exp36，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `b1ff372b5139a2d436870fd26db4841bef4d00d339d0f536d330430f1db25aab`；`.so`=`build/cuda_case14_two_head_reducer_exp54.so`。
- **唯一假设**: case14 继续让每个 head 使用 128 个 one-dimension worker，但把两个独立 head 配成一个 256-thread CTA，使 reducer grid 从 32 降到 16。总线程数、normalized-BF16 partial、每维累加、共享权重数学和 producer 均不变；它不同于 exp37 的 64-thread/vec2 和 exp26 的 16-lane/group8 reducer。
- **资源/correctness**: 新 reducer=`42 MTreg / 28 STreg / staticMaxWarps=8`、0 B stack，动态 shared=`4144 B`；CPU 14/14，case14 full PASS，match=`1.0`、max error=`1.220703e-04`、max tolerance ratio=`0.008`。
- **A/B**: 21×100 为 `0.9957/0.9978/1.0020`；41×200 为 `0.9957/0.9983/1.0003`。两次中位数轻微偏正，但上尾均触及或跨过 1，未稳定分离。随后两次 61×300 只输出测试头部、未产出 case 结果行，不纳入性能证据，也不报告为 mismatch。
- **结论**: 归类中性，不替换 exp36，也不把约 0.2% 中位差当成可组合收益。关闭 exact two-head CTA pairing；若继续研究 reducer，必须改变权重分发、partial layout 或跨 head 数据流，而不是只扫描 4/8-head block packing。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_two_head_bf16_reducer_exp54.cpp`。

### exp55-case14-z1-chunk4  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp36，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `a3e7fe4454d624cfaaf3af51ae9bc5e9407870bc758396ace85997e9d25058ff`；`.so`=`build/cuda_case14_z1_chunk4_exp55.so`。
- **架构假设**: case14 从 `dim3(16,8,2)`/256-thread z2 改为安全的 `dim3(16,8)`/128-thread z1；每页按四个 4-token chunk 顺序更新 online softmax，消除 Q staging、z-state shared merge 和一部分 barrier。K/V 每页仍只加载一次、split257 与 normalized-BF16 partial/reducer 不变。它不同于已关闭的 `(32,8,1)` full-warp 方案，不使用 32-lane QK 或 16-token live score。
- **代价/资源**: 为保持低 live state，下一页 K/V 只能在当前页四个 QK/PV chunk 全部结束后一起发起，失去原 K-over-PV/V-over-QK pipeline。资源仅从 exp36 producer 的 `92 MTreg/8320 B/staticMaxWarps=5` 降到 `86/8192 B/5`；128-thread block 可驻留 2 个、仍只有 4 active waves，与 control 的一个 256-thread block相同，没有兑现 occupancy 假设。
- **correctness/A-B**: CPU 14/14；case14 full PASS，match=`1.0`、max error=`1.220703e-04`、max tolerance ratio=`0.008`。21×100 p10/p50/p90=`1.4800/1.4840/1.4895`，稳定慢约 48.4%。
- **结论**: 拒绝。active waves 不增、流水丢失和四次 chunk softmax 更新远超减少 shared merge/barrier 的收益；关闭 exact 16-lane z1/chunk4 结构，不以 split、loader 或 reducer 微调补偿。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case14_z1_chunk4_exp55.cpp`。

### exp45–55 阶段复盘（2026-08-09）
- 本阶段完成 11 个有判别力的节点：exp45 证实原生 FP32 MMA fragment/精度能力；exp46–50 五种 runtime 数据流全部显著回退；exp51 关闭 case14 split257 的上邻域；exp52 关闭 per-head-scale int8 partial；exp53 判定 case11 head-pair BSM 中性；exp54 判定 case14 two-head reducer packing 中性；exp55 关闭 128-thread z1/chunk4。
- 当前本地正向 control 仍是 exp36。case14 QK 上界约 47.5% 的诊断没有变化，但“现有 FP32 MMA ownership 微调”“同一 split 邻域”“仅压缩更多位宽”“只打包 reducer CTA”“不提高 active waves 的 z1”均已耗尽，不能继续围绕这些参数细扫。
- 下一轮低风险队列转向仍有改变关键前提的 shape-specific loader：case8 已从旧 token-parallel 改为 head-pair/z4，但尚未在该新布局上独立比较 BSM。架构队列只保留能同时改变 QK ownership/通信或有效 active waves 的方案，避免继续在 case14 相同数据流上堆微调。

### exp56-case8-headpair-bsm-loader  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp36，SHA `eab62e0e84f538ac75ff0bda8835349f3f8c9c3682598dba56cd4ccfd17f1bd6`；候选 SHA `c5f57a2d23d1b99cedfb45114448e3c6e4522c343f579205456353ecc2a7cc1a`；control/candidate `.so`=`build/cuda_case11_headpair_sync_exp53_control.so` / `build/cuda_case8_headpair_bsm_exp56.so`。
- **唯一假设**: 仅让 B16/KV4/L4096 case8 的 head-pair/z4 full/tail page loader 使用 BSM async；case11 保持同步 `uint4`，direct-Q、split48、two-stage state reducer、partial ABI 和 launch 数不变。关键新前提是 exp17 已把 case8 从旧 token-parallel 改为 head-pair/z4，因此旧 loader 结论不能直接继承。
- **资源**: BSM full=`82 MTreg / 46 STreg / 8320 B / 5 warps`，与同步 full 相同；BSM tail=`50/40/8320 B/7`，同步 tail=`50/36/8320 B/7`，均 0 B stack。
- **correctness**: CPU 14/14；case8 独立 full/boundary/random 全部 PASS，max error=`4.882812e-04/7.812500e-03/9.765625e-04`。同一进程 `full→boundary→full→random→full` 全部 PASS，padding trap、finite、tail 和 static workspace 复用均正确。
- **A/B**: case8 21×100=`0.9938/0.9953/0.9976`，41×200=`0.9943/0.9953/0.9963`，两轮稳定快约 0.47%；非目标 case11 21×100=`0.9992/1.0000/1.0013`，中性。
- **结论**: 保留为新的本地候选基线，完整源码为 `solutions/archive/2026-08-09-experiments/cuda_case8_headpair_bsm_exp56.cpp`；工作文件保持同一 SHA。收益幅度约 1.3 μs，可能跨 case8 OJ tier，但平台仍处暂停状态，不 submit/watch/cancel/query；恢复后只把当前最高优先级组合 finalist 送 OJ。

### exp57-headpair-page-loop-wave-barrier  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp56，SHA `c5f57a2d23d1b99cedfb45114448e3c6e4522c343f579205456353ecc2a7cc1a`；候选 SHA `46a3952188a27f346989015a75cbf12328274de00154660e76a591fc8f8edda5`；`.so`=`build/cuda_headpair_wave_barrier_exp57.so`。
- **唯一假设与所有权证明**: head-pair/z4 的 `dim3(16,4,4)` 中，固定 z 的 `16×4=64` threads 恰好组成一个 C500 wave；该 wave 在 page loop 中只读写 `s_k/s_v[4*z:4*z+4]`，其他 wave 不访问这些 token row。因此有下一页时，K-dead 和 V-dead 的 CTA-wide `__syncthreads()` 可改为 MACA `__syncwarp()`（warp-scope release fence + `__builtin_mxc_barrier_warp` + acquire fence）。最后一页后整个 K/V buffer 会被跨-z state reducer复用，故最后一次 V-dead 仍保留 CTA barrier。loader、QK/PV、split、partial、state reducer和dispatch均不变。
- **资源**: full 从 exp56 的 `82→84 MTreg`，STreg=`46`、8320 B shared、staticMaxWarps=5不变；tail仍 `50 MTreg`，BSM/sync分别为`40/36 STreg`、staticMaxWarps=7，全部0 B stack。资源小幅增加但未跨 residency 档。
- **correctness**: CPU 14/14；case8/case11 的 full、boundary、random全部100% PASS，full max error分别=`4.882812e-04/2.441406e-04`，boundary最大=`7.812500e-03`，random最大=`9.765625e-04/1.953125e-03`。两 shape 各自同进程 `full→boundary→full→random→full` 全部 PASS，验证短序列 wave 不均衡、tail、padding trap和workspace复用。
- **A/B**: 相对 exp56，case8 21×100=`0.9850/0.9895/0.9923`、41×200=`0.9890/0.9902/0.9928`；case11 21×100=`0.9694/0.9701/0.9709`、15×80复测=`0.9677/0.9700/0.9716`。case11 两次更重尝试未产出结果行，不纳入统计；有效两轮完全一致。
- **结论**: 保留为新的本地候选基线；case8再快约1.0%，case11再快约3.0%，是能跨 OJ timing tier 的明确本地收益。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_headpair_wave_barrier_exp57.cpp`，工作文件保持同一 SHA；OJ继续暂停。

### exp58-headpair-sync-page-ready-wave  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp57，SHA `46a3952188a27f346989015a75cbf12328274de00154660e76a591fc8f8edda5`；候选 SHA `df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8`；`.so`=`build/cuda_headpair_sync_ready_wave_exp58.so`。
- **唯一假设与所有权证明**: head-pair/z4 的固定 z 是一个完整64-thread C500 wave；同步 `uint4` loader 的该 wave 写入且只消费 `s_k/s_v[4*z:4*z+4]`，所以 case11 每页开始的 page-ready CTA `__syncthreads()` 可缩为 `__syncwarp()`。case8 的 BSM arrive/wait保持原样，exp57的next-page K/V overwrite wave barrier、最终跨-z shared复用 CTA barrier、loader、QK/PV、split、partial、state reducer和dispatch均不变。
- **资源**: 与exp57一致：BSM/sync full均=`84 MTreg / 46 STreg / 8320 B / staticMaxWarps=5`，tail分别=`50/40`与`50/36 MTreg/STreg / 8320 B / 7`，全部0 B stack。
- **correctness**: CPU 14/14；同一候选binary的GPU full、boundary、random均14/14 PASS。case8/case11各自同进程`full→boundary→full→random→full`全部100% PASS；full max error分别=`4.882812e-04/2.441406e-04`，boundary最大=`7.812500e-03`，random最大=`9.765625e-04/1.953125e-03`，padding trap、finite、tail和workspace复用均正确。
- **A/B**: 相对exp57，首轮21×100 case11=`0.9528/0.9532/0.9540`、case8=`0.9987/0.9994/1.0002`；case11独立21×100复测=`0.9526/0.9532/0.9540`。两轮case11稳定快约4.7%，BSM case8如预期中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。三处wave-private page-loop同步（page-ready、K-dead、V-dead）现已全部缩小；最终页后的CTA barrier保护跨-z state reducer复用整个K/V buffer，不能以同一假设继续删除。完整源码为 `solutions/archive/2026-08-09-experiments/cuda_headpair_sync_ready_wave_exp58.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp59-headpair-shared-only-cta-barrier  (CORRECT, NEUTRAL/REJECTED, 2026-08-09)
- **父/control**: exp58，SHA `df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8`；候选 SHA `3f0a460caaa293742c8c0d98e5d7a9feafbbfc8fccdc19368c99316247273c3f`；`.so`=`build/cuda_headpair_shared_barrier_exp59.so`。
- **唯一假设**: 本机MACA头文件中`__syncthreadshared()`实现为block-scope release/acquire fence加`__builtin_mxc_barrier_shared()`；head-pair最后一页K/V shared复用和两级state reducer的四个CTA barrier前后都没有global-memory依赖，因此仅将这四个`__syncthreads()`换成shared-only版本。page-loop wave barrier、loader、数学、split、partial、dispatch均不变。
- **资源/correctness**: full/tail资源与exp58逐项一致，均0 B stack；CPU14/14，case8/case11 full均100% PASS，max error=`4.882812e-04/2.441406e-04`。
- **A/B/结论**: 21×100相对exp58，case8=`0.9988/0.9998/1.0011`、case11=`0.9994/0.9999/1.0008`，完全中性；不追加boundary/random，不替换基线。证明这四处通用block fence不是端到端成本，关闭同一路径的fence/barrier flag微调。完整源码为`solutions/archive/2026-08-09-experiments/cuda_headpair_shared_barrier_exp59.cpp`，工作文件恢复exp58。

### exp60-kv8-token-parallel-wave-barriers  (LOCALLY POSITIVE, SUPERSEDED, 2026-08-09)
- **父/control**: exp58，SHA `df34a4176002f9d98575ca8630dc86ce9f6fae269328189be986e857722ffdc8`；候选SHA `63d16579dd0e139f1fc3689e288914f40923352c50fd69f3b427542ac836eb92`；`.so`=`build/cuda_kv8_wave_barrier_exp60.so`。
- **唯一假设与所有权证明**: 通用KV8 token-parallel也是`dim3(16,4,4)`，固定z的64线程构成一个C500 wave并只读写`s_k/s_v[4*z:4*z+4]`。仅在`GQA==4 && SYNC_COPY`实例把page-ready、存在下一页时的K-dead和V-dead从CTA缩为wave barrier；最后一页后跨-z复用shared仍保留CTA barrier，KV4与case4 BSM不改变同步语义。
- **资源/correctness**: 所有实例资源与exp58一致、0 B stack；CPU14/14，受影响cases6/7/9/12/13 full均100% PASS。
- **A/B**: 首次多case benchmark无结果行，不纳入证据；拆成单case 21×100后，case6=`0.9588/0.9781/0.9948`、case7=`0.9630/0.9643/0.9654`、case9=`0.9593/0.9603/0.9614`、case12=`0.9543/0.9549/0.9555`、case13=`0.9560/0.9571/0.9581`。非目标case4=`0.9963/0.9978/0.9996`，case14=`0.9988/1.0030/1.0081`。
- **结论**: wave-row ownership在同步KV8上形成3.6–4.5%长case收益，机制成立；但V-dead的运行时if/else重排改变了所有模板实例的源码形状，case14出现轻微噪声上尾，因此以exp61做编译期隔离后再选baseline。完整源码为`solutions/archive/2026-08-09-experiments/cuda_kv8_wave_barrier_exp60.cpp`。

### exp61-kv8-wave-barrier-codegen-isolation  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp60，SHA `63d16579dd0e139f1fc3689e288914f40923352c50fd69f3b427542ac836eb92`；候选SHA `f43f4aa0d5090f06a57e8c7cb119398453f628dba42e795d1b3852301b30df37`；`.so`=`build/cuda_kv8_wave_barrier_isolated_exp61.so`。
- **唯一差异**: 目标KV8同步分支与exp60语义和操作顺序完全一致；仅将V-dead写成外层`if constexpr (GQA==4 && SYNC_COPY)`，让KV4和BSM实例恢复exp58原有“无条件CTA barrier、条件issue”源码形状，隔离非目标codegen。
- **资源/correctness**: 资源与exp60/58逐项一致，0 B stack；CPU14/14，同一binary的GPU full/boundary/random均14/14 PASS。cases6/7/9/12/13各自同进程`full→boundary→full→random→full`全部100% PASS，覆盖combined/separate-tail、padding trap、finite、workspace扩容和旧partial复用。
- **A/B**: 相对exp58，case9 21×100=`0.9595/0.9607/0.9617`、case12=`0.9541/0.9548/0.9553`，复现exp60收益；case14=`0.9976/1.0016/1.0068`，零附近噪声。相对exp60直接验证目标不变：case7 15×100=`0.9996/1.0000/1.0015`，case13=`0.9969/0.9985/1.0000`。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist；exp58的KV4收益与exp60的长KV8收益已在同一源码组合。完整源码为`solutions/archive/2026-08-09-experiments/cuda_kv8_wave_barrier_isolated_exp61.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp62-case4-bsm-overwrite-wave-barriers  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp61，SHA `f43f4aa0d5090f06a57e8c7cb119398453f628dba42e795d1b3852301b30df37`；候选SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；`.so`=`build/cuda_case4_bsm_wave_barrier_exp62.so`。
- **唯一假设**: case4虽然使用BSM loader，但通用KV8/GQA4的固定z仍是一个独占4个token row的64-thread wave。仅把K-dead/V-dead条件从`GQA==4 && SYNC_COPY`放宽为`GQA==4`；BSM page-ready wait、loader、QK/PV、split、state reducer和其他shape均不变。
- **资源/correctness**: 资源与exp61逐项一致、0 B stack；CPU14/14，同一binary的GPU full/boundary/random均14/14 PASS，case4同进程`full→boundary→full→random→full`全部100% PASS。
- **A/B**: case4两轮41×200分别=`0.9904/0.9924/1.0047`、`0.9920/0.9934/0.9960`，p50稳定快约0.7–0.8%；非目标长同步case12 15×100=`0.9994/0.9998/1.0003`，中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。收益约0.2–0.3 μs，幅度不大但case4距计分tier很近；必须由OJ判断是否跨tier。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case4_bsm_wave_barrier_exp62.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp63-case14-headpair-wave-bf16  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；候选SHA `b00b455f3c9cbe3961be15022ce9d1ccd2b7e13c65a0481336bee45d9f3af7d1`；`.so`=`build/cuda_case14_headpair_wave_bf16_exp63.so`。
- **唯一假设**: 旧exp32的case14 `(16,4,4)` head-pair/z4在split257下回退约2.2%，但当时没有direct-Q、head-pair K/V overwrite wave barriers和normalized-BF16 partial。仅让case14改走已有head-pair producer，并保留BSM、combined单launch、split257、原reducer和normalized-BF16 partial，验证这些新前提能否抵消旧回退。
- **资源/correctness**: producer为`88 MTreg / 54 STreg / 8320 B / staticMaxWarps=5`，exp62通用case14 control为`92 / 48 / 8320 B / 5`，均0 spill。CPU语义14/14 PASS；真实C500 case14 full匹配率100%，`max_error=1.220703e-04`、`max_tol_ratio=0.008`、finite PASS。
- **A/B**: 相对exp62的两轮21×100分别为`1.0113/1.0149/1.0176`和`1.0123/1.0145/1.0162`，稳定慢约1.45%。新前提只把旧exp32约2.2%的回退收窄，未翻为收益。
- **结论**: rejected；性能门槛已明确失败，因此不浪费资源跑全量GPU correctness。case14复用case11 head-pair/z4 producer的exact路线在direct-Q、wave barrier、split257和normalized-BF16 partial前提下仍关闭，不再用loader/split/reducer微调补偿。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_headpair_wave_bf16_exp63.cpp`；工作文件已恢复exp62，OJ继续暂停。

### exp64-case14-generic-direct-q  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`。exp64a候选SHA `2b1ab720693aabccb96a9b8ea9c32ef6d02f0bec0d170f9953f50d767d47184b`、`.so`=`build/cuda_case14_direct_q_exp64.so`；exp64b候选SHA `8e6b5899224ee56a73e40fa5c4bb9cadf8666b582716f10cefef59339993d821`、`.so`=`build/cuda_case14_direct_q_nodyn_exp64b.so`。
- **唯一假设**: 通用KV4/z2 producer原先由z0把8行Q写入2 KiB动态shared、CTA barrier后两个z读取。case14的257个split反复使用同一32行Q，故只让case14两个z直接从L2-hot Q读取，删除global→shared staging、shared广播和初始CTA barrier；BSM、z2、split257、normalized-BF16 partial与reducer不变。exp64a误保留2 KiB launch动态shared配额；exp64b只把该配额改为0，补齐资源前提。
- **资源/correctness**: direct-Q producer从control的`92 MTreg / 48 STreg`变为`96 / 46`，静态shared仍8320 B、staticMaxWarps仍5、0 spill。CPU14/14；exp64a和exp64b的真实C500 case14 full均100% PASS，`max_error=1.220703e-04`、`max_tol_ratio=0.008`、finite PASS。
- **A/B**: exp64a相对exp62的21×100=`1.0000/1.0044/1.0065`，41×200=`1.0032/1.0053/1.0075`。exp64b相对exp64a的31×150=`0.9987/0.9994/1.0022`，证明动态shared配额归零中性；exp64b相对exp62的41×200=`1.0023/1.0042/1.0053`，仍稳定慢约0.4%。
- **结论**: rejected。通用KV4/z2只有一道Q staging barrier，额外Q读取与`+4 MTreg`超过删除shared读写的收益；释放2 KiB动态shared未跨occupancy档。完整源码分别为`cuda_case14_direct_q_dynamic_exp64a.cpp`和`cuda_case14_direct_q_nodyn_exp64b.cpp`；工作文件已恢复exp62，OJ继续暂停。

### exp65-case10-normalized-bf16-partial  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；候选SHA `d19fa936477f321e3b213f9863248b1c660377ce4a5b6b1ce67355057e868a4c`；`.so`=`build/cuda_case10_bf16_normalized_partial_exp65.so`。
- **唯一假设**: case10同为B1/KV4并有128个split，producer/reducer约读写2 MiB FP32 accumulator workspace。只把case10加入case14已验证的normalized-BF16 partial dispatch，将accumulator流量减半；split128、4 page/partial、BSM、z2、Q staging和128-thread reducer均不变。
- **correctness**: CPU14/14；真实C500 case10 full匹配率100%，`max_error=2.441406e-04`、`max_tol_ratio=0.015`、finite PASS。
- **A/B**: 相对exp62，41×300=`0.9965/1.0010/1.0122`，61×500=`1.0008/1.0034/1.0069`；没有复现case14约0.8%的稳定收益，强复测反而慢约0.34%。
- **结论**: rejected。128-split/约2 MiB workspace不足以摊销producer归一化和reducer BF16转换；16-bit partial正收益边界仍只覆盖case14的257-split B1路径。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case10_bf16_normalized_partial_exp65.cpp`；工作文件已恢复exp62，OJ继续暂停。

### exp66-case6-bsm-wave-loader  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；候选SHA `0c97d91a1d803efa0fb528b6e0ebee3e6403056b68cfff7e2f2468af74bf3d46`；`.so`=`build/cuda_case6_bsm_wave_exp66.so`。
- **唯一假设**: case6每split仅3页，可能与case4一样对page-ready latency敏感。只将case6的token-parallel loader从同步`uint4`切为BSM；exp62已让GQA4 BSM的K/V overwrite barrier保持wave scope，split8、CTA、QK/PV、state merge和reducer均不变。
- **correctness/A-B**: CPU14/14；真实C500 case6 full匹配率100%，`max_error=1.953125e-03`、`max_tol_ratio=0.097`、finite PASS。相对exp62的41×500为`1.0352/1.0375/1.0411`，稳定慢约3.75%。
- **结论**: rejected。case4的单页短路径BSM收益不能扩展到3页/split的case6；同步`uint4`配合exp60/61 wave barrier仍是case6 control。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case6_bsm_wave_exp66.cpp`；工作文件已恢复exp62，OJ继续暂停。

### exp67-case14-headpair-z2-wave-bf16  (CORRECT, REJECTED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；候选SHA `fd1c9bba511ce84388232acca8bba5aaff1857acca4fa4e88078cb0586fd56af`；`.so`=`build/cuda_case14_headpair_z2_wave_bf16_exp67.so`。
- **关键前提与唯一架构假设**: #106556的128-thread `(16,4,2)` head-pair/z2只在case11的旧同步/staged-Q/CTA-barrier前提下使用过。exp67仅对case14移植该数值数据流，并同时采用当前direct-Q、BSM、每个z独占8行K/V的wave-private page-loop barrier、split257和normalized-BF16 partial；原case14 reducer不变。与exp63的256-thread z4不同，本候选每线程保留两个head×8 token，但只做一次z-state merge。
- **资源/correctness**: producer=`118 MTreg / 66 STreg / 8320 B / 0 B stack / staticMaxWarps=4`。128-thread block可驻留两个，仍为4 active waves，与exp62的256-thread control同档。CPU14/14；真实C500 case14 full 100% PASS，`max_error=1.220703e-04`、`max_tol_ratio=0.008`、finite PASS。
- **A/B/结论**: 相对exp62的21×100为`1.1692/1.1757/1.1779`，稳定慢约17.6%，直接rejected。双头×8-token live state、118-register codegen与每线程双行loader远超跨head K/V解包复用及更简单z2 reducer的收益。case14的安全head-pair z2与z4均已关闭，不以loader/split/reducer继续补偿。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_headpair_z2_wave_bf16_exp67.cpp`；工作文件已恢复exp62，OJ继续暂停。

### exp68-case14-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp62，SHA `badab6023d97ded3faa2a125c12fa23f3955b9bcc0b6c8bb3b1d6acf055d9a19`；候选SHA `cbd8d4ea88eb2c4d7561bd3e67894aa09459dad7c23e6c5f5df31ff02c029f4a`；`.so`=`build/cuda_case14_raw_bperm_qk_exp68.so`。
- **唯一假设**: case14通用KV4/z2 producer的每个token QK使用4次`__shfl_xor_sync(..., width=16)`。MACA 3.7.1包装器为每次交换生成subgroup上界比较与回退；offset固定为8/4/2/1时，`lane^offset`永不离开连续16-lane row。只给case14模板实例启用`__builtin_mxc_bsm_bpermute((__lane_id() ^ offset) << 2, bits)`，loader、split257、Q staging、softmax、PV、normalized-BF16 partial与reducer均不变；其他shape继续使用包装器。
- **独立probe/codegen**: `tests/c500_bpermute_probe.cpp/.py`以一个64-thread wave覆盖全部四个row，真实C500上offset 8/4/2/1均逐元素满足`raw == wrapper == lane^offset`。四次交换的隔离probe从包装器`8 MTreg/10 STreg`降为raw `5/8`。完整producer的BSM bpermute仍为64次，但LLVM IR计数从exp62的`91 icmp/76 select`降到`27/12`，恰好删除64组边界逻辑；producer资源保持`92 MTreg/48 STreg/8320 B shared/0 B stack/staticMaxWarps=5`。
- **correctness**: CPU语义14/14 PASS；同一`.so`的真实C500 full、boundary、random均14/14 PASS，case14最大误差分别为`1.220703e-04/0/2.441406e-04`且全部finite。`case14 full→case13 full→case14 boundary→full→random→full`同进程workspace复用序列全部PASS。
- **A/B**: 相对exp62，21×100=`0.9819/0.9843/0.9862`，41×200=`0.9854/0.9866/0.9880`；两轮稳定快约1.3–1.6%，control/candidate绝对p50约`0.2860→0.2814 ms`与`0.2858→0.2820 ms`。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。该原语只对已证明不跨row的固定16-lane XOR安全；不得据此重开8-lane、跨subgroup或任意lane-dependent shuffle。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_raw_bperm_qk_exp68.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp69-case10-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp68，SHA `cbd8d4ea88eb2c4d7561bd3e67894aa09459dad7c23e6c5f5df31ff02c029f4a`；候选SHA `bbb0ede409a4833d7fe7495102d0d50eff9cb7c443732afec5760a0f9ebedde8`；`.so`=`build/cuda_case10_raw_bperm_qk_exp69.so`。
- **唯一假设**: case10与case14使用同一通用KV4/z2、16-lane固定XOR QK reduction，且约60 μs本地时延距离下一OJ档约1 μs。只给`B1/L8192/KV4` dispatch启用exp68已runtime验证的raw BSM bpermute；case10继续使用split128、BSM loader、shared-Q staging、FP32 partial和原reducer，case14 raw+normalized-BF16路径及其他shape不变。
- **资源/correctness**: case10 raw producer仍为`92 MTreg/48 STreg/8320 B shared/0 B stack/staticMaxWarps=5`。CPU14/14；最终binary的真实C500 full/boundary/random均14/14 PASS。`case10 full→case14 full→case10 boundary→full→case14 random→case10 random→full→case14 full`同进程序列全部PASS，覆盖FP32与normalized-BF16 partial交替复用。
- **A/B**: 相对exp68，case10 41×300=`0.9817/0.9863/0.9897`，61×500=`0.9841/0.9881/0.9920`，绝对p50约`0.0606→0.0598 ms`与`0.0605→0.0598 ms`；非目标case14 21×100=`0.9995/1.0013/1.0045`中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。case10约0.7–0.8 μs收益有机会跨OJ计时档；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case10_raw_bperm_qk_exp69.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp70-case5-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp69，SHA `bbb0ede409a4833d7fe7495102d0d50eff9cb7c443732afec5760a0f9ebedde8`；候选SHA `9cf8b0680062fa124922e0dc900ac702dc0edb384e364fc17c29e897fd98d49a`；`.so`=`build/cuda_case5_raw_bperm_qk_exp70.so`。
- **唯一假设**: case5同样使用通用KV4/z2固定16-lane QK，但每个split只有约2页，需判定raw交换收益会否被launch/reducer淹没。只给`B16/L141/KV4`复用exp69已实例化的raw模板；split5、BSM loader、shared-Q staging、FP32 partial、reducer及case10/14 dispatch均不变。
- **correctness**: CPU14/14；最终binary的真实C500 full/boundary/random均14/14 PASS。`case5 full→case10 full→case14 full→case5 boundary/full→case10/14/5 random→case5/10/14 full`同进程序列全部PASS。
- **A/B**: 相对exp69，case5 41×500=`0.9743/0.9806/0.9837`，61×1000=`0.9571/0.9719/0.9921`，绝对p50约`0.0270→0.0264 ms`与`0.0269→0.0261 ms`。非目标case10 21×200=`0.9822/0.9971/1.0054`、case14=`0.9988/1.0009/1.0030`，均中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。case5约0.6–0.8 μs收益同样有机会跨OJ计时档，并证明raw包装开销在短producer中仍可见；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case5_raw_bperm_qk_exp70.cpp`，工作文件保持同一SHA；OJ继续暂停。

### exp71-case11-headpair-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp70，SHA `9cf8b0680062fa124922e0dc900ac702dc0edb384e364fc17c29e897fd98d49a`；候选SHA `61661232512d4fa11f1d133c3f2289eeded1e9d62bb03ba04ca26a704c1013a5`；`.so`=`build/cuda_case11_headpair_raw_bperm_qk_exp71.so`。
- **唯一假设**: case11 head-pair/z4 的同一K pack同时计算两个query-head dot，但每个dot仍调用4次CUDA compatibility `__shfl_xor_sync(..., width=16)`并生成通用row边界路径。只给case11同步full/tail模板打开exp68 probe已证明安全的raw row16 BSM bpermute；case8保持wrapper，loader、direct-Q、split48、softmax/PV、两级z-state reducer、FP32 partial和final reducer均不变。
- **资源/correctness**: full/tail保持`84/50 MTreg`、`46/36 STreg`、8320 B shared、0 B stack、staticMaxWarps=`5/7`。CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。case5/8/10/11/14的12步同进程序列覆盖full/boundary/random、full→short→full及FP32/normalized-BF16 workspace交替，全部100% PASS；case11 full最大误差=`2.441406e-04`且finite。
- **A/B**: case11相对exp70的21×100=`0.9881/0.9890/0.9906`，41×200强复测=`0.9885/0.9890/0.9896`，绝对p50约`0.6553→0.6481 ms`，稳定快约1.1%。非目标case8的21×100=`0.9988/1.0024/1.0052`，41×200强复测=`0.9988/1.0005/1.0029`，收敛为中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。raw交换在head-pair双dot布局中仍能删除可测包装开销，但结论只覆盖固定16-lane XOR；不得外推到8-lane、跨row、任意lane-dependent交换或reducer。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_headpair_raw_bperm_qk_exp71.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp72-case9-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp71，SHA `61661232512d4fa11f1d133c3f2289eeded1e9d62bb03ba04ca26a704c1013a5`；候选SHA `c06c332f753002149d19c324f569ae07209b842d84af2388f7a3b90f6173ba76`；`.so`=`build/cuda_case9_raw_bperm_qk_exp72.so`。
- **唯一假设**: case9是计分对时延最敏感的shape，KV8 token-parallel每页仍对4个token dot各执行4次固定16-lane XOR wrapper。只给`B32/L4096/KV8`的同步full/tail模板打开raw row16 BSM bpermute；case7/12/13保持wrapper，split24、同步`uint4` loader、wave barrier、softmax/PV、z-state merge、partial和reducer不变。
- **资源/correctness**: raw与wrapper full/tail均为`60/36 MTreg`、`42/36 STreg`、8192 B shared、0 B stack、staticMaxWarps=8，没有occupancy变化。CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case9/7/12/13/11/14的12步同进程序列覆盖workspace扩容后缩小、full→short→full、tail split及FP32/BF16交替，全部100% PASS；case9 full最大误差=`4.882812e-04`且finite。
- **A/B**: case9相对exp71的21×100=`0.9692/0.9713/0.9734`，41×200=`0.9707/0.9713/0.9726`，绝对p50约`0.5480→0.5322 ms`，两轮稳定快约2.9%。未打开raw的case7/12/13分别=`0.9991/1.0000/1.0011`、`0.9987/1.0000/1.0016`、`0.9962/0.9995/1.0035`，均中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。收益在相同资源档下来自QK热循环边界控制流删除，对case9有显著计分潜力；仍须逐shape验证case7/12/13，不能一次性全局替换。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case9_raw_bperm_qk_exp72.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp73-case7-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp72，SHA `c06c332f753002149d19c324f569ae07209b842d84af2388f7a3b90f6173ba76`；候选SHA `454e74c6a7ddded7357909c822feb0df03c19a5c963f1371026a75b1fdf08fd9`；`.so`=`build/cuda_case7_raw_bperm_qk_exp73.so`。
- **唯一假设**: 只把exp72已在case9验证的raw KV8 full/tail specialization dispatch扩展到`B64/L2048/KV8` case7；case12/13继续使用wrapper，case9 raw dispatch、split14、同步loader、wave barrier、QK/PV、z-state merge、partial与reducer不变。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case7/9/12/13/14的10步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS；case7 full最大误差=`9.765625e-04`且finite。
- **A/B**: case7相对exp72的21×100=`0.9684/0.9698/0.9724`，41×200=`0.9700/0.9704/0.9708`，绝对p50约`0.5544→0.5380 ms`，稳定快约3.0%。已经打开raw的非目标case9=`0.9984/0.9997/1.0011`，组合中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。KV8 raw QK收益已在B32 case9与B64 case7独立复现，下一步仍按shape验证case12/13。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case7_raw_bperm_qk_exp73.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp74-case12-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp73，SHA `454e74c6a7ddded7357909c822feb0df03c19a5c963f1371026a75b1fdf08fd9`；候选SHA `9da260120c01d2a0e72beac9dcf4d091aff8bec2ae928bd6405614daafafac1f`；`.so`=`build/cuda_case12_raw_bperm_qk_exp74.so`。
- **唯一假设**: 只把exp73已在case9/7验证的raw KV8 full/tail specialization dispatch扩展到`B8/L32768/KV8` case12；case13继续使用wrapper，既有raw路径、split128、同步loader、wave barrier、QK/PV、z-state merge、partial与reducer不变。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case12/7/9/13/14的10步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS；case12 full最大误差=`1.220703e-04`且finite。
- **A/B**: case12相对exp73的21×100=`0.9697/0.9711/0.9721`，41×200=`0.9703/0.9708/0.9713`，绝对p50约`1.0490→1.0184 ms`，稳定快约2.9%。既有raw非目标case7/9 p50=`0.9987/0.9996`，中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。KV8 raw QK在B64/B32/B8三种并发与split配置均复现约3%，只剩B1 case13需独立验证。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case12_raw_bperm_qk_exp74.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp75-case13-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp74，SHA `9da260120c01d2a0e72beac9dcf4d091aff8bec2ae928bd6405614daafafac1f`；候选SHA `07cb13baf9b8b99ec32852086f7447b5dc3ab6d81dd642b7f8fddb5120855bab`；`.so`=`build/cuda_case13_raw_bperm_qk_exp75.so`。
- **唯一假设**: 只把exp74已在case9/7/12验证的raw KV8 full/tail specialization dispatch扩展到`B1/L58966/KV8` case13，判断低并发B1下wrapper删除是否仍可见；case7/9/12 raw路径、split256、同步loader、wave barrier、QK/PV、z-state merge、partial与reducer不变。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case13/12/7/9/14的11步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS；case13 full最大误差=`1.220703e-04`且finite。
- **A/B**: case13相对exp74的21×100=`0.9686/0.9720/0.9765`，41×200=`0.9702/0.9714/0.9728`，绝对p50约`0.2855→0.2773 ms`，稳定快约2.9%。既有raw非目标case7/9/12 p50=`0.9990/0.9997/0.9996`，中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。四个长KV8 shape已逐一独立复现约2.9–3.0%，该raw wrapper消除扩展闭合；下一步转向case8 head-pair或新的launch/state数据流。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case13_raw_bperm_qk_exp75.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp76-case8-headpair-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp75，SHA `07cb13baf9b8b99ec32852086f7447b5dc3ab6d81dd642b7f8fddb5120855bab`；候选SHA `af8f6a894ad4802b44b666b5b17caf7a74f7df3a93a37b2001edd9a499de65f9`；`.so`=`build/cuda_case8_headpair_raw_bperm_qk_exp76.so`。
- **唯一假设**: 只给`B16/L4096/KV4` case8的BSM head-pair/z4 full/tail模板打开exp71已在同步case11验证的raw row16双dot QK；case11与全部KV8 raw路径保持不变，BSM loader、split48、wave barrier、direct-Q、softmax/PV、两级z-state reducer、partial与final reducer均不变。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case8/11/13/12/14的10步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS；case8 full最大误差=`4.882812e-04`且finite。
- **A/B**: case8相对exp75的21×100=`0.9869/0.9920/0.9950`，41×200=`0.9920/0.9928/0.9951`，绝对p50约`0.2673→0.2655 ms`，稳定快约0.7–0.8%。非目标case9/11 p50=`0.9989/1.0009`，中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist。BSM head-pair同样受益，但幅度小于同步case11；两个head-pair shape的raw交换扩展至此闭合。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case8_headpair_raw_bperm_qk_exp76.cpp`，工作文件与归档字节一致；OJ继续暂停。

### exp77-case4-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp76，SHA `af8f6a894ad4802b44b666b5b17caf7a74f7df3a93a37b2001edd9a499de65f9`；候选SHA `2529e6e4e9467bb815f95d2d6b898565ca2dc28376ace82eea3e9a2400ead993`；`.so`=`build/cuda_case4_raw_bperm_qk_exp77.so`。
- **唯一假设**: 只给`B64/L64/KV8` case4的BSM combined token-parallel实例打开raw row16 QK；n_split/direct-out、BSM loader、wave barrier、QK/PV、z-state merge及其他shape均保持exp76，判断约31 μs短路径能否穿透launch占比并跨1 μs OJ tier。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case4/8/13/14/6/12的11步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS；case4 full最大误差=`7.812500e-03`且finite。
- **A/B**: case4相对exp76的41×500=`0.9756/0.9841/0.9925`，61×1000=`0.9772/0.9782/0.9791`，绝对p50约`0.0313→0.0306 ms`，稳定快约1.6–2.2%。非目标case8 p50=`1.0003`中性；未改源码的case6 p50=`0.9949`只记为噪声，不归因。
- **结论**: 约0.7 μs本地收益有机会让case4跨OJ计时档；该候选已作为唯一差异父源码继续形成exp78。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case4_raw_bperm_qk_exp77.cpp`；OJ继续暂停。

### exp78-case6-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp77，SHA `2529e6e4e9467bb815f95d2d6b898565ca2dc28376ace82eea3e9a2400ead993`；候选SHA `6e2d3473cc90bc0b0c45ba143e21c5153b094a2b5ffcf52ac6df55456211e9df`；`.so`=`build/cuda_case6_raw_bperm_qk_exp78.so`。
- **唯一假设**: 只给`B16/L362/KV8` case6的同步combined token-parallel实例打开raw row16 QK；case4及其他shape、loader、wave barrier、softmax/PV、z-state merge和direct-out均保持exp77。case6是除case3外最后一个仍使用width=16 wrapper的OJ token-parallel shape。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。跨case6/4/8/13/14/12的11步同进程序列覆盖full→short→full、workspace扩容/缩小和FP32/BF16交替，全部100% PASS。
- **A/B与加载顺序消偏**: 正向加载exp78/exp77时，case6的41×500=`0.9640/0.9726/0.9838`、61×1000=`0.9640/0.9762/0.9875`；反向加载exp77/exp78时，脚本报告的原control/原candidate p50=`1.0181`。原candidate/control消偏估计为`√(0.9762/1.0181)=0.9792`，即快约2.1%。case4正向=`1.0154`、反向=`1.0152`，消偏`√(1.0154/1.0152)≈1.0001`，中性；host launch stub地址与反汇编一致，表面回退由模块加载顺序造成。
- **结论**: 微秒级A/B必须分别以control-first和candidate-first加载，不能把单一加载顺序的1–2%偏差归因给源码。该候选已作为唯一差异父源码继续形成exp79；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case6_raw_bperm_qk_exp78.cpp`，OJ继续暂停。

### exp79-case3-raw-row16-bpermute-qk  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp78，SHA `6e2d3473cc90bc0b0c45ba143e21c5153b094a2b5ffcf52ac6df55456211e9df`；候选SHA `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`；`.so`=`build/cuda_case3_raw_bperm_qk_exp79.so`。
- **唯一假设**: 只给`B16/L17/KV4` case3的BSM combined token-parallel实例打开raw row16 QK；n_split=1、direct-out、BSM loader、Q staging、CTA `(16,8,2)`、softmax/PV及其他shape均保持exp78。这是最后一个仍使用width=16 wrapper的OJ token-parallel shape。
- **correctness**: CPU14/14；同一fresh-build binary的GPU full/boundary/random均14/14 PASS。`case14 full→case3 full→case12 full→case3 boundary→case6 random→case3 random→case8 full→case3 full→case14 full`同进程序列全部PASS，覆盖大workspace分配前后及single-split direct-out。
- **A/B与加载顺序消偏**: case3的61×2000正向p50=`0.9966`，反向脚本报告原control/原candidate=`1.0090`；121×5000强复测为`0.9939/1.0116`，消偏`√(0.9939/1.0116)=0.9912`，约快0.9%，绝对约0.1 μs。非目标case4/5/6的61×1000正向=`1.0093/1.0028/1.0036`、反向=`1.0145/1.0020/0.9983`，消偏=`0.9974/1.0004/1.0027`，均中性。
- **结论**: 保留为新的本地候选基线和OJ恢复后的当前finalist，但绝对收益大概率不足以单独跨1 μs OJ tier。至此raw row16 wrapper消除已按shape覆盖全部OJ token-parallel路径，该微表达式路线关闭；不得继续细扫或外推到8-lane/跨row交换。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case3_raw_bperm_qk_exp79.cpp`，工作文件与归档字节一致；OJ继续暂停，下一步转向QK ownership、page pipeline、launch或partial/state流量的结构变化。

### exp80-case11-headpair-combined  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp79，SHA `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`；候选SHA `5cf52f0f08214abbfb05bcf391f3e9c27152e4b5414ae8a6b8040a7987cc8e1e`；`.so`=`build/cuda_case11_headpair_combined_exp80.so`。
- **唯一假设**: case11保持head-pair/z4、同步`uint4` loader、split48、raw row16 QK、softmax/PV和final reducer数学，只把full-only+tail-only两个producer合并为一个combined producer，使partial split数`49→48`并删除一次tail launch；由combined模板独立承担full/tail predicate与资源变化。
- **资源/correctness**: combined producer=`88 MTreg/54 STreg/8320 B shared/0 B stack/staticMaxWarps=5`，control full=`84/46/8320/5`、tail=`50/36/8320/7`，主full occupancy档未变。CPU14/14、GPU full/boundary/random各14/14；`case11 full→boundary→full→case14 full→case11 random→case12 full→case11 full→case3 full→case11 boundary→full`同进程序列全部PASS。
- **A/B**: 正向exp80/exp79的41×200 p10/p50/p90=`1.1113/1.1125/1.1136`；反向脚本报告原control/原candidate的21×100=`0.8976/0.8988/0.9002`，消偏`√(1.1125/0.8988)=1.1125`，稳定慢约11.3%。
- **结论**: rejected，未提交；删除一次tail launch和一个partial的收益远小于combined predicate/codegen在765个full page上的代价。该exact full+tail combined head-pair模板关闭，不允许继续用split/reducer/loader参数补偿。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_headpair_combined_exp80.cpp`；工作文件已恢复exp79字节，OJ继续暂停。

### case11-kernel-phase-profile  (DIAGNOSTIC, OJ PAUSED, 2026-08-09)
- **方法**: 使用内存内 PyTorch profiler 分解 case11，不生成 `.db` 或 `profiler.log`；profiler 只用于定位，不作为交错 A/B 性能证据。
- **结果**: full producer=`613.026 μs / 94.87%`，final reducer=`24.030 μs / 3.72%`，tail producer=`9.139 μs / 1.41%`。
- **结论**: case11 的绝对主瓶颈是765个full page上的 producer；单独优化 reducer 或 tail 的理论上限不足，后续优先改变 full producer 的 QK ownership、active waves、寄存器状态或 page pipeline。

### exp81-case11-head4-z4  (CORRECT, REJECTED / ARCHITECTURAL DIAGNOSTIC, OJ PAUSED, 2026-08-09)
- **父/control**: exp79，SHA `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`；候选SHA `b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43`；`.so`=`build/cuda_case11_head4_z4_exp81.so`。
- **唯一假设**: case11 改为128-thread `dim3(16,2,4)`，每个16-lane row负责4个query head；同一K/V pack只解包一次并服务4个head，z4、split48、同步loader、raw row16 QK、full/tail分离和两级shared state reducer保持不变。每线程加载两行，整页K/V总读取量不变。
- **资源/correctness**: full=`132 MTreg/44 STreg/8320 B shared/staticMaxWarps=3`，tail=`84/40/8320/5`，均0 B stack/spill；case11 full correctness PASS。
- **A/B与加载顺序消偏**: 正向exp81/exp79 p50=`1.0027`；反向脚本报告exp79/exp81 p50=`0.9963`；消偏`√(1.0027/0.9963)=1.0032`，约慢0.32%。
- **结论**: rejected，不替代exp79；但这是有价值的架构证据：即使full预计从4 active waves降到2，四head共享一次K/V解包几乎完全抵消occupancy损失。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4_exp81.cpp`；只有能把full寄存器跨到至少4 warps且不增加转换/交换成本的新状态表示才值得沿此ownership重开。

### exp82-case11-head4-z4-fp16-score  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp81，SHA `b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43`；候选SHA `a9f5666a6dd80b9ee6a16eb890fa3a93ee74b3b2f179adf5bf5c9fb029e68824`；`.so`=`build/cuda_case11_head4_z4_fp16score_exp82.so`。
- **唯一假设**: 只把head4 producer每页的`float score[4][4]`改为`__half2 score[4][2]`，并让`m_page`和softmax使用重新展开后的实际FP16 logit；FP32 `m/l/acc`、CTA、loader、split、partial和reducer全部不变，目标是压低full live score寄存器并恢复第二个128-thread block。
- **资源/correctness**: full反而从exp81的`132→134 MTreg`，`44 STreg/8320 B shared/staticMaxWarps=3`不变；tail为`80/36/8320/staticMaxWarps=6`。case11 full correctness PASS，match=`1.0`、max error=`2.441406e-04`、max tolerance ratio=`0.015`、finite。
- **A/B与加载顺序消偏**: 正向exp82/exp81的21×50=`1.0923/1.0933/1.0950`；反向脚本报告exp81/exp82=`0.9138/0.9143/0.9152`；消偏`√(1.0933/0.9143)=1.0935`，稳定慢约9.35%。
- **结论**: rejected，未跑全量correctness也不提交；FP16 score的转换与重新展开代价显著，且没有降低full寄存器/occupancy。该exact score位宽压缩关闭。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4_fp16score_exp82.cpp`，SHA已核对；工作文件恢复exp79字节。

### exp83-case11-head4-z4-packed-q  (CORRECT, NEUTRAL / REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp81，SHA `b18f76770f2097adbd981422dbb3d0887bbd47bd5879e9d9a4e3b3076075cd43`；候选SHA `c126d73918567df42c9945aa729acb0614a642d5f42770b1ac0ddf2101ada31a`；`.so`=`build/cuda_case11_head4_z4_packedq_exp83.so`。
- **唯一假设**: 将跨page loop的`float qh[4][8]`改为`uint4 qh[4]`，在每个token QK中按K pair展开Q；其余head4 ownership、score、FP32 state、loader、split和reducer保持exp81。
- **资源/correctness**: full仍为`132 MTreg/44 STreg/8320 B/staticMaxWarps=3`，tail仅`84→82 MTreg`；case11 full correctness PASS，max error=`2.441406e-04`。
- **A/B**: 正向exp83/exp81=`0.9983/1.0005/1.0014`；反向exp81/exp83=`0.9968/0.9983/1.0003`；消偏`√(1.0005/0.9983)=1.0011`，中性。
- **结论**: 编译器对full重新做Q转换的循环不变量提升，源码位宽没有改变full codegen资源或性能。rejected；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4_packedq_exp83.cpp`。

### exp84-case11-head4-z4-dimension-major-qk  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp83，SHA `c126d73918567df42c9945aa729acb0614a642d5f42770b1ac0ddf2101ada31a`；候选SHA `0463aea9c0cb42ab7f11468c791878f776fded1f24509b8a38a6cb7dc589bb24`；`.so`=`build/cuda_case11_head4_z4_dimmajor_exp84.so`。
- **唯一假设**: 只改full producer QK次序：每页按4个dimension-pair推进四head×四token，保留每个dot的两个packed-FMA partial；tail仍用exp83 token-major路径。目标是缩短Q live range并跨4-warp档。
- **资源/correctness**: 32组双分量partial使full从`132→144 MTreg`，仍3 warps；tail保持`82 MTreg/5 warps`。case11 full correctness PASS，max error=`2.441406e-04`。
- **A/B**: 正向exp84/exp81=`1.0303/1.0331/1.0342`；反向exp81/exp84=`0.9653/0.9666/0.9678`；消偏`√(1.0331/0.9666)=1.0338`，慢约3.38%。
- **结论**: dimension-major同时live的32个packed partial超过Q live-range收益；rejected。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4_dimmajor_exp84.cpp`。

### exp85-case11-head4-z4-shared-q-dimension-major  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp84，SHA `0463aea9c0cb42ab7f11468c791878f776fded1f24509b8a38a6cb7dc589bb24`；候选SHA `cd340bdaaa25a0c58f707925437e958499838864a66053a2d82d972a10b563c3`；`.so`=`build/cuda_case11_head4_z4_sharedq_dimmajor_exp85.so`。
- **唯一假设**: full producer新增2 KiB独立BF16 Q shared区并用volatile load阻止Q hoist，沿用exp84 dimension-major QK；tail与其他路径不变，目标是删除16个packed-Q常驻值后跨4-warp档。
- **资源/correctness**: full从exp84的`144→132 MTreg`，但`STreg=52`、shared=`10368 B`且仍3 warps；tail=`82/40/10368/5`。case11 full correctness PASS，max error=`2.441406e-04`。
- **A/B**: 正向exp85/exp81=`1.1743/1.1766/1.1779`；反向exp81/exp85=`0.8474/0.8482/0.8501`；消偏`√(1.1766/0.8482)=1.1778`，慢约17.78%。
- **结论**: shared Q确实移除约12个full MTreg，但未跨occupancy档，重复shared load/转换和额外staging成为纯成本。rejected；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4_sharedq_dimmajor_exp85.cpp`；工作文件恢复exp79。head4的score位宽、packed-Q源码表示、dimension-major和shared-Q局部压缩至此关闭。

### near-tier-kernel-phase-profile  (DIAGNOSTIC, OJ PAUSED, 2026-08-09)
- **方法**: 对exp79使用内存内PyTorch profiler，每例50次full调用，不生成`.db`或`profiler.log`；仅用于阶段占比定位，不替代交错A/B。
- **结果**: case4只有direct-out producer=`28.605 μs/100%`；case5 producer=`17.521 μs/78.49%`、group8 reducer=`4.803 μs/21.51%`；case10 producer=`42.522 μs/73.68%`、one-head reducer=`15.191 μs/26.32%`；case14 producer=`256.881 μs/91.77%`、normalized-BF16 reducer=`23.025 μs/8.23%`。
- **结论**: case10 reducer是近tier shape中最大的独立低风险阶段，足以容纳1 μs收益；case4没有reducer可省，case14继续优先producer，case5 reducer绝对上限较小。

### long-case-kernel-phase-profile  (DIAGNOSTIC, OJ PAUSED, 2026-08-09)
- **方法**: 对exp79主链使用相同的内存内PyTorch profiler，每例50次full调用，不生成`.db`或`profiler.log`；结果只用于选择实验，不替代交错A/B。
- **结果**: case7 total=`530.406 μs`，producer/reducer/tail=`511.377/15.983/3.046 μs`；case8=`265.728`，`238.899/24.491/2.338 μs`；case9=`525.986`，`506.752/16.887/2.347 μs`；case11=`646.810`，`612.514/24.781/9.515 μs`；case12=`1016.465`，`983.535/30.711/2.219 μs`；case13=`274.338`，`241.169/25.549/7.620 μs`。
- **结论**: producer仍占长case绝对多数，但case8/11/12各有约24–31 μs的独立one-head reducer，适合先做低风险数据流优化；case13虽同样有25.5 μs reducer，却只有32个reducer CTA，必须单独验证并发边界。

### exp86-case10-group8-reduce128  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp79，SHA `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`；候选SHA `56eb1fb927339bf9ed0bfb6cb820c83d19017b32698d61877f736ca8a0d09ec3`；`.so`=`build/cuda_case10_group8_reduce128_exp86.so`。
- **唯一假设**: producer、128 split、FP32 partial和LSE数学不变，只让case10复用现有group8/shared-weight reducer，将32个one-head CTA压成4个eight-head CTA，判断CTA调度与vector output能否覆盖并发下降。
- **资源/correctness**: group8=`66 MTreg/26 STreg/staticMaxWarps=7`、动态shared=8192 B；case10 full correctness PASS，max error=`2.441406e-04`。
- **profile/A-B**: reducer=`23.749 μs`，比control `15.191 μs`慢约56%；正向exp86/exp79=`1.1232/1.1375/1.1444`，反向exp79/exp86=`0.8705/0.8848/0.8902`，消偏`√(1.1375/0.8848)=1.1338`，端到端慢约13.4%。
- **结论**: rejected；4 CTA/8 active waves并发不足，不能直接把小split group8外推到128 split。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case10_group8_reduce128_exp86.cpp`。

### exp87-case10-vec4-reduce128  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp79，SHA `5eccfc50acd46b1b416dd9157c930a4c6a20d92fd33010a8e725fffb82b4f973`；候选SHA `6c1de4a3736dd6b565ab515a0ad3c5b5cdc3650b79a97c2458145c49769173a6`；`.so`=`build/cuda_case10_vec4_reduce128_exp87.so`。
- **唯一假设**: 保持32个one-head CTA和全部producer/workspace/LSE数学，只把case10 reducer从128 threads×1维改为32 threads×连续4维；一个32-lane row完成max/l归约，partial acc使用`float4`读取，删除四warp二级归约。
- **资源/correctness**: vec4 reducer=`64 MTreg/35 STreg/staticMaxWarps=8`、动态shared=1024 B。CPU14/14；同一binary GPU full/boundary/random均14/14；`case10 full→boundary→full→case14 full→case10 random→full`同进程扩容/复用全部PASS。
- **profile/A-B**: reducer `15.191→13.373 μs`，profile总时延`57.713→55.898 μs`。正向exp87/exp79的41×200=`0.9645/0.9703/0.9788`；反向exp79/exp87=`1.0248/1.0317/1.0385`；消偏`√(0.9703/1.0317)=0.9698`，端到端稳定快约3.0%。case5/14消偏约`1.0041/1.0006`，均视为中性。
- **结论**: 提升为当前本地candidate baseline和OJ恢复后的finalist；收益约1.8–2.0 μs，足以跨case10 tier。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case10_vec4_reduce128_exp87.cpp`，工作文件与归档SHA一致；OJ继续暂停。

### exp88-case8-vec4-reduce49  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp87，SHA `6c1de4a3736dd6b565ab515a0ad3c5b5cdc3650b79a97c2458145c49769173a6`；候选SHA `e368f80dbc47d5ebc485a1eea1fc4f33e924e83e00521110fcbf8e0efbd41293`；`.so`=`build/cuda_case8_vec4_reduce49_exp88.so`。
- **唯一假设**: 只把exp87的32-thread×连续4维one-head reducer扩展到case8的48 main split+独立tail（49 partial），新增严格按full-page与tail计算live split的模板分支；producer、workspace ABI、split、数学和512个reducer CTA均不变。
- **profile/A-B**: reducer=`24.491→16.010 μs`，profile总时延=`265.728→257.244 μs`。正向exp88/exp87=`0.9654/0.9692/0.9713`，反向exp87/exp88=`1.0293/1.0328/1.0377`，消偏`√(0.9692/1.0328)=0.9687`，端到端快约3.1%；case10消偏约1.000，中性。
- **correctness/结论**: CPU14/14，GPU full/boundary/random各14/14及同进程workspace复用全部PASS。提升为本地主链节点；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case8_vec4_reduce49_exp88.cpp`。

### exp89-case11-vec4-reduce49  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp88，SHA `e368f80dbc47d5ebc485a1eea1fc4f33e924e83e00521110fcbf8e0efbd41293`；候选SHA `b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a`；`.so`=`build/cuda_case11_vec4_reduce49_exp89.so`。
- **唯一假设**: 仅将相同的49-partial vec4 reducer扩展到case11；保持head-pair/z4同步producer、48 main split+tail、partial ABI和512个one-head CTA不变。
- **profile/A-B**: reducer=`24.781→16.302 μs`，profile总时延=`646.810→638.060 μs`。正向exp89/exp88=`0.9853/0.9871/0.9886`，反向exp88/exp89=`1.0113/1.0129/1.0144`，消偏`√(0.9871/1.0129)=0.9872`，端到端快约1.28%；case8/10消偏均约1.000。
- **correctness/结论**: CPU14/14，GPU full/boundary/random各14/14及10步同进程workspace复用全部PASS。提升为本地主链节点；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_vec4_reduce49_exp89.cpp`。

### exp90-case13-vec4-reduce257  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp89，SHA `b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a`；候选SHA `eb0384b2843a21c74674386af9954a58acdb9be9dcffd6174fca8d5b8ba7125f`；`.so`=`build/cuda_case13_vec4_reduce257_exp90.so`。
- **唯一假设**: 只把separate-tail vec4 reducer扩展到case13的256 main split+tail（257 partial）和32个one-head CTA，判断B1长KV8能否靠`float4`读取与单row归约获益。
- **profile/A-B**: full correctness PASS；reducer=`25.549→27.822 μs`，profile总时延=`274.338→277.407 μs`。正向exp90/exp89=`1.0051/1.0080/1.0116`，反向exp89/exp90=`0.9844/0.9872/0.9912`，消偏`√(1.0080/0.9872)=1.0105`，端到端慢约1.05%。
- **结论**: rejected。只有32个CTA时，降低单CTA线程数后的总active wave不足，257-partial循环又放大每线程串行工作；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case13_vec4_reduce257_exp90.cpp`，主链保持exp89。

### exp91-case12-vec4-reduce129  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp89，SHA `b4333f5c069292ccc9755adc616769a56872645163883aa45f2ec3c4d2bce25a`；候选SHA `de9bc8c3c947134990e83069e7b13e934be0ddc6a40c1696664c00b2777faf90`；`.so`=`build/cuda_case12_vec4_reduce129_exp91.so`。
- **唯一假设**: 只把separate-tail vec4 reducer扩展到case12的128 main split+tail（129 partial）与256个one-head CTA，用来区分exp90的反转来自257-partial串行长度还是B1并发不足；producer、workspace、split和数学不变。
- **资源/profile**: reducer保持`64 MTreg/35 STreg/staticMaxWarps=8`、动态shared约1 KiB。相同50-call profiler中control producer/reducer/tail=`984.556/30.479/2.299 μs`，candidate=`983.675/23.905/2.227 μs`，总时延=`1017.334→1009.807 μs`。
- **A/B**: 正向exp91/exp89=`0.9915/0.9927/0.9944`，反向exp89/exp91=`1.0050/1.0061/1.0075`，消偏`√(0.9927/1.0061)=0.9933`，端到端快约0.67%。case8/10/11消偏约`1.0001/1.0005/1.0001`，均中性。
- **correctness/结论**: CPU14/14；同一binary的GPU full/boundary/random各14/14；覆盖case12/13/14/11/8/10的10步同进程full→short→full workspace扩容/复用全部PASS。提升为当前本地candidate baseline；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case12_vec4_reduce129_exp91.cpp`且与工作文件字节一致。exp88/89/91证明vec4 reducer在256–512个CTA、49–129 partial下正向，exp90则关闭32 CTA/257 partial的直接扩展；OJ继续暂停。

### exp92-case9-vec4-reduce25  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp91，SHA `de9bc8c3c947134990e83069e7b13e934be0ddc6a40c1696664c00b2777faf90`；候选SHA `84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86`；`.so`=`build/cuda_case9_vec4_reduce25_exp92.so`。
- **唯一假设**: case9的24 main split+tail（25 partial）原本走128个eight-head group8 CTA。保持producer、split、partial ABI和稳定合并数学不变，只改为1024个one-head、32-thread×连续4维vec4 CTA；总输出线程数不变，用更多独立CTA和更小metadata shared换取`float4` acc数据流。
- **profile/A-B**: reducer=`16.814→15.089 μs`，同轮profile总时延=`526.316→524.206 μs`。41×200正向exp92/exp91=`0.9946/0.9963/0.9981`，反向exp91/exp92=`1.0014/1.0019/1.0024`，消偏`√(0.9963/1.0019)=0.9972`，端到端快约0.28%、绝对约1.5–2.0 μs。非目标case7/12消偏约`1.0005/0.9999`，中性。
- **correctness/结论**: CPU14/14；同一binary GPU full/boundary/random各14/14；case9与case12/14/11/13/8交替的10步同进程full→short→full序列全部PASS。提升为当前本地candidate baseline。它证明vec4可越过`reduce_splits<=32`边界，但收益很小且只覆盖25 partial/1024 CTA，不能据此全局替换small-group8；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case9_vec4_reduce25_exp92.cpp`并与工作文件字节一致，OJ继续暂停。

### exp93-case7-vec4-reduce15  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp92，SHA `84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86`；候选SHA `fdc6c8ef03b5e1a10cbc906792d64afce594df4627c1f04207c19c451344c66e`；`.so`=`build/cuda_case7_vec4_reduce15_exp93.so`。
- **唯一假设**: 只把case7的14 main split+tail（15 partial）从256个eight-head、无动态shared的group8 CTA改为2048个one-head vec4 CTA；producer、split、partial ABI和数学不变，验证exp92 small-split收益能否延伸到`<=16`专用分支。
- **profile/A-B**: case7 full correctness PASS。reducer=`16.328→17.280 μs`，profile总时延=`531.569→532.224 μs`。正向exp93/exp92=`1.0009/1.0019/1.0025`，反向exp92/exp93=`0.9946/0.9967/0.9988`，消偏`√(1.0019/0.9967)=1.0026`，端到端慢约0.26%。
- **结论**: rejected，不跑全量correctness。15 partial时现有无动态shared group8专用路径已更优；vec4 small-split扩展边界停在case9的25 partial，不得覆盖case7。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case7_vec4_reduce15_exp93.cpp`，工作文件恢复exp92。

### exp94-case13-vec2-reduce257  (LOCALLY POSITIVE, OJ PAUSED, 2026-08-09)
- **父/control**: exp92，SHA `84537ed7319d03d0cd46171d126cc819d0b7a15d744e259339facd6dfe729f86`；候选SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；`.so`=`build/cuda_case13_vec2_reduce257_exp94.so`。
- **关键新前提/唯一假设**: exp90的32-thread vec4在B1 case13只有32个CTA，未填满原生64-lane wave且回退。exp94只把该shape改为64-thread×连续2维的one-head reducer，使每CTA使用完整wave，同时保持`float2` acc读取；256 main split+tail、FP32 partial、producer与稳定合并数学不变。
- **profile/A-B**: reducer=`25.134→23.859 μs`，同轮profile总时延=`274.575→272.922 μs`。强复测61×500正向exp94/exp92=`0.9896/0.9917/0.9931`，反向exp92/exp94=`1.0009/1.0045/1.0077`，消偏`√(0.9917/1.0045)=0.9936`，端到端快约0.64%、绝对约1.8 μs。非目标case9/12消偏均约`0.9995`，中性。
- **correctness/结论**: CPU14/14；同一binary GPU full/boundary/random各14/14；case13与case9/12/14/11/8交替的10步同进程full→short→full序列全部PASS。提升为当前本地candidate baseline。exp90/94共同证明case13应保留完整64-lane wave而不是32-thread vec4；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case13_vec2_reduce257_exp94.cpp`且与工作文件字节一致，OJ继续暂停。

### exp95-case11-page-id-prefetch  (CORRECT, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `bf1b613c2f7686d3e90af10ef1af7d87954c5b1c1f436b0c433df7e826dd073e`；`.so`=`build/cuda_case11_pid_prefetch_exp95.so`。
- **唯一假设**: case11 full producer每split处理16页，只把下一页物理page ID提前一个完整page循环读取，使block-table load与当前页QK/PV重叠；同步K/V loader、head-pair/z4、split48、tail、partial和reducer不变。
- **资源/profile/A-B**: case11 full correctness PASS。full producer保持`84 MTreg/8320 B/staticMaxWarps=5`，但`STreg 46→52`；profile producer=`612.669→616.402 μs`。正向exp95/exp94=`1.0040/1.0062/1.0073`，反向exp94/exp95=`0.9940/0.9946/0.9954`，消偏`√(1.0062/0.9946)=1.0058`，端到端慢约0.58%。
- **结论**: rejected。block-table ID读取不是可见瓶颈，提前一页只延长uniform/scalar状态；该exact page-ID预取关闭。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_pid_prefetch_exp95.cpp`，工作文件恢复exp94。

### exp96-case11-headpair-packed-q  (RESOURCE-GATE REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `67dce5a3814f3949b5110cb37ee42cfe1c2bfdcb47758a7286a54eea11be9e8b`；资源构建=`build/cuda_case11_headpair_packedq_exp96_resource.so`。
- **关键新前提/唯一假设**: exp83只在128-thread head4/z4布局中测试过packed Q，full被编译器重新hoist且资源不变；exp96改在当前256-thread head-pair/z4关键路径上，仅让case11 full producer把两行Q以`uint4 qpack0/qpack1`跨page loop保存，并在每个dimension pair的packed FMA处转换。case8、case11 tail、同步loader、split48、raw row16 shuffle、softmax/PV和reducer均不变。
- **资源门槛**: 候选full实例仍为`84 MTreg / 46 STreg / 8320 B shared / 0 B stack / staticMaxWarps=5`，与exp94逐项相同；tail仍为`50/36/8320/7`。源码位宽没有缩短后端关键live range，也没有跨occupancy档。
- **结论**: 在预先声明的静态门槛失败后停止，不运行GPU correctness、profile或A/B，也不提交。关闭head-pair布局下继续做Q位宽/转换位置微调；下一步必须改变QK ownership、通信或page pipeline。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_headpair_packedq_exp96.cpp`，工作文件恢复exp94。

### exp97-case11-wave-broadcast-unpacked-k  (CORRECT FULL, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `125b7f31f3066ea9e6ea419a6baf895791431db717ec2f7ace091fa536fb9a14`；`.so`=`build/cuda_case11_wave_broadcast_k_exp97.so`。
- **新原语验证**: 扩展`tests/c500_bpermute_probe.cpp/.py`，真实C500逐lane确认`__builtin_mxc_bsm_bpermute((__lane_id() & 15) << 2, value)`可把row0的16个值正确广播到同一64-lane wave的四个row；独立广播codegen仅`3 MTreg/8 STreg/staticMaxWarps=8`。这只授权该固定row0→same-tx映射，不外推任意跨row交换。
- **唯一假设**: case11 full中同一z wave的四个ty row对每个token读取相同K。只让ty0执行一次`uint4` LDS和8个BF16→FP32转换，再用8次跨row raw bpermute把FP32 K分发给全部8个query head；保留16-lane dot ownership、Q/score/acc、同步page loader、split48、softmax/PV、tail和reducer。
- **资源/correctness**: full仍为`84 MTreg/46 STreg/8320 B/5 warps`，tail仍`50/36/8320/7`，0 B stack。CPU14/14；C500 case11 full PASS，match=`1.0`、max error=`2.441406e-04`、max tolerance ratio=`0.015`、finite。
- **A/B/结论**: 正向exp97/exp94 p10/p50/p90=`1.4118/1.4130/1.4146`；反向exp94/exp97=`0.7069/0.7075/0.7084`，几乎精确互逆，稳定慢约41.3%。8次跨row BSM交换的吞吐/依赖链成本远大于省下的三份LDS和BF16解包；拒绝，不跑全量correctness、不提交。关闭FP32 K跨row广播及同一8-value变体，不用split/loader补偿。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_wave_broadcast_k_exp97.cpp`，工作文件恢复exp94。

### exp98-case11-head4-pairwise-z4  (RESOURCE-GATE REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `25dc89019e7eb6417c964cb07957bc17d5db900bf2b56d334130e0dd1cc4ed25`；资源构建=`build/cuda_case11_head4_pairwise_exp98_resource.so`。
- **关键新前提/唯一假设**: exp81的128-thread `(16,2,4)` head4/z4 full只比head-pair慢约0.32%，但`132 MTreg/3 warps`卡住；AGENTS只允许在能跨到至少4 warps时重开。exp98仍让一个CTA只加载一次K/V page、每线程保持4个head的Q与online state，但把每页四head QK/score/PV拆成两个顺序head-pair，目标是把同时live score从16降到8；case11 tail继续使用exp94 head-pair，其他shape不变。
- **资源门槛/结论**: full反而为`140 MTreg / 52 STreg / 8320 B shared / 0 B stack / staticMaxWarps=3`，比exp81的`132/44/8320/3`更差，也远高于exp94的`84/46/8320/5`。重复pairwise热循环、额外控制和延后的page pipeline没有让后端复用临时寄存器；静态门槛失败后不运行GPU correctness/profile/A-B，也不提交。关闭exact head4 sequential-pair布局，不以split/reducer/loader补偿。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_head4_pairwise_exp98.cpp`，工作文件恢复exp94。

### exp99-case10-single-full-only  (DIAGNOSTIC, SEMANTICALLY INCOMPLETE / REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `87174eea31dcb7a1d078da80bc7954184d3ddb42c270a7832f7ca37f5d3bc7a2`；资源构建=`build/cuda_case10_single_full_exp99_resource.so`。
- **关键新前提/唯一假设**: 旧case10 separate-tail p50约`1.051`的负结果来自总会增加一个tail launch；case10容量`8192=512×16`恰为整页。exp99只把case10现有single combined launch换成single full-only launch，不启动tail kernel，split128、BSM、shared-Q、raw row16 QK、FP32 partial和vec4 reducer不变，用来测量删除full-loop predicate的性能上界。
- **资源/full结果**: producer从`92 MTreg/48 STreg/5 warps`降为`70/46/7`，8320 B static shared、0 B stack；CPU语义14/14，C500 case10 full PASS，max error=`2.441406e-04`。正向exp99/exp94=`0.9808/0.9905/1.0029`，反向exp94/exp99=`0.9951/1.0056/1.0128`，消偏`√(0.9905/1.0056)=0.9925`，仅快约0.75%（约0.4–0.5 μs）。
- **正确性反证/结论**: host只知道capacity，`cache_seqlens`仍可含非整页长度；full-only producer会丢失尾token。boundary实测match=`0.015625`、max error=`4.03125`、max tolerance ratio=`50.078`，明确失败。该收益不足以覆盖已知约5.1%的额外tail launch，也不足以证明复杂fused-tail reducer可净获益；拒绝且绝不提交。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case10_single_full_exp99.cpp`，工作文件恢复exp94。

### exp100-case14-separate-tail-current-stack  (CORRECT TARGET, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94，SHA `441da88b5fd4e2e26495be0047e1be4a0c425dd6ac7d7ce84c76a8ed6e7dfeec`；候选SHA `8d8e0f995271c08a827550abf40c9f54a55521eb9784c18876d07b4a33f81193`；`.so`=`build/cuda_case14_separate_tail_exp100_resource.so`。
- **关键新前提/唯一假设**: 旧case14 separate-tail约慢1.9%，但没有在当前raw-row16 QK、wave barrier、split257和normalized-BF16 partial组合上分解。exp100只把case14 combined producer拆成full-only+tail-only两个launch并让reducer读取258个partial，其他数学与shape不变。
- **资源/correctness**: full=`70 MTreg/46 STreg/8320 B/7 warps`，tail=`40/46/8320/7`，reducer=`40/36/8`，均0 spill；CPU语义14/14，case14 full/boundary/random全部PASS。
- **profile/A-B/结论**: control producer/reducer=`256.865/22.072 μs`；candidate full/tail/reducer=`251.003/10.255/22.287 μs`。正向exp100/exp94=`1.0159/1.0179/1.0221`，反向exp94/exp100=`0.9829/0.9861/0.9888`，消偏`√(1.0179/0.9861)=1.0160`，慢约1.60%。full-only确实省5.862 μs，但独立4-CTA tail launch耗10.255 μs；拒绝。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_separate_tail_exp100.cpp`。

### exp101-case14-fused-tail-reducer  (CORRECT TARGET, REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp94；候选SHA `51df69110f7576e6c6c0c4840e209a14baf486006fa7f00363b53ba834748e9b`；`.so`=`build/cuda_case14_fused_tail_reduce_exp101_resource.so`。
- **唯一假设**: 保留exp100的低寄存器full-only producer，但删除tail kernel与第258个workspace partial；32个one-head reducer CTA各自计算末页15-token QK/PV并与257个normalized-BF16 full partial稳定合并。
- **资源/correctness**: producer保持`70/46/8320/7`；融合reducer=`38 MTreg/52 STreg/0 spill/8 warps`。CPU14/14，case14 full/boundary/random均PASS。
- **profile/A-B/结论**: control=`257.029+22.139=279.168 μs`；candidate=`250.726+30.817=281.543 μs`。正向exp101/exp94 p50=`1.0093`，反向exp94/exp101=`0.9910`，消偏约`1.0092`，慢0.92%。融合优于exp100但tail计算仍多花8.678 μs，拒绝。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_fused_tail_reduce_exp101.cpp`。

### exp102-case14-direct-global-max-tail-reducer  (CORRECT FULL, NEUTRAL / REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp101；候选SHA `a54eaa06603260dbb9e56778ba5a389a1e9cda4d112256e273d3ebcbcbcfacfb`；`.so`=`build/cuda_case14_direct_tail_reduce_exp102_resource.so`。
- **唯一假设**: tail logits不再先形成独立`(m_tail,l_tail,acc_tail)`后二次缩放，而是直接参与full partial的global-max；15个权重一次计算并直接累加V，删除tail局部max/l归约与额外scale exp。
- **资源/correctness/profile**: reducer仍为`38/52/0 spill/8 warps`；case14 full PASS。相同profile中reducer从exp101的`31.329→28.165 μs`，追回3.164 μs。
- **A/B/结论**: 相对exp94正向p50=`0.9999`、反向exp94/exp102=`1.0010`，消偏`0.99945`，仅约0.055%且分布跨1，归类中性。它证明reducer融合可抵消独立tail launch，但没有可用利润；完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_direct_tail_reduce_exp102.cpp`。

### exp103-case14-underfilled-last-split-tail  (PERF POSITIVE, SUPERSEDED BY CORRECTNESS FIX, OJ PAUSED, 2026-08-09)
- **父/control**: exp94；候选SHA `3830789e9c960591f2544ba6991de3c69ad3039429107503be99f803c33aa3c3`；资源构建=`build/cuda_case14_last_split_tail_exp103_resource.so`。
- **关键新前提/唯一假设**: case14的`full_pages=3844`、`split257`、`pages_per_split=15`使最后live split只有4个full page，远短于15-page grid critical path。exp103保持full-page hot loop独立编译，在循环外只让underfilled last-split CTA顺带处理tail page，并把它合并到同一个partial；仍是一次producer launch、257个partial和原reducer。与exp80的combined模板不同，tail predicate从不进入每个full-page热循环。
- **资源/profile**: producer=`70 MTreg/56 STreg/8320 B/0 spill/7 warps`，MT register与full-only完全相同；control combined=`92/48/8320/5`。同轮profile producer=`257.096→250.266 μs`，reducer保持`22.044 μs`，总计约省6.83 μs。
- **A/B**: 正向exp103/exp94 p10/p50/p90=`0.9742/0.9768/0.9796`；反向exp94/exp103=`1.0223/1.0236/1.0264`；消偏`√(0.9768/1.0236)=0.9769`，case14稳定快约2.31%、约6.6 μs。
- **初始correctness与后续反证**: CPU14/14；同一binary GPU full/boundary/random各14/14，且原workspace序列PASS，但B1 boundary只取length=1，random seed也未命中split模数边界。后续定点发现reducer仍按`ceil(valid_pages/pages_per_split)`计数：当`full_pages`恰为15的倍数且有tail时会多读未写partial；真实C500 length 241/481的match仅约`0.190/0.306`，明确错误。性能机制仍有效，但原始exp103绝不能作为control或提交源码；完整源码仅作为发现过程保留。

### exp103b-fused-tail-live-split-count  (CORRECTNESS FIX, PERF NEUTRAL, OJ PAUSED, 2026-08-09)
- **父/control**: exp103，SHA `3830789e9c960591f2544ba6991de3c69ad3039429107503be99f803c33aa3c3`；候选SHA `1864bb1c7be47f61dfb8560afd46b981dd77292756afcb52113a43c0108152f8`；资源构建=`build/cuda_case14_fused_live_count_exp103b_resource.so`。
- **唯一修复**: fused-tail producer把tail并入最后一个拥有full page的split，因此reducer的live split必须按`ceil(full_pages/pages_per_split)`计数；零full-page的tail-only序列使用split0。只给case14 fused reducer增加该编译期模式，满长度仍读取257个partial，producer完全不变。
- **资源/correctness**: case14 producer保持`70 MTreg/56 STreg/8320 B/7 warps`，reducer保持`40/36/0 B static shared/8 warps`，均0 spill。CPU14/14；case14 full/boundary/random PASS；同进程61519→240→241→255→256→480→481→3840→3841→241全部PASS，原失败点恢复100% match且finite。
- **A/B/结论**: 满长度正向exp103b/exp103 p50=`0.9987`，反向exp103/exp103b=`0.9993`，消偏`√(0.9987/0.9993)=0.9997`，性能中性。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case14_fused_tail_live_count_exp103b.cpp`；它取代原始exp103成为exp104的正确父节点。

### exp104-case13-underfilled-last-split-tail  (LOCALLY POSITIVE, SUPERSEDED BY EXP105, OJ PAUSED, 2026-08-09)
- **父/control**: exp103b，SHA `1864bb1c7be47f61dfb8560afd46b981dd77292756afcb52113a43c0108152f8`；候选SHA `62f9ec33f55b228b961177299d7c1144a5f865dfd7e69eed2e0cff0fcdcef6a8`；最终构建=`build/cuda_case13_last_split_tail_exp104.so`，资源构建=`build/cuda_case13_last_split_tail_exp104_resource.so`。
- **唯一假设**: case13有`full_pages=3685`、`n_split=256`、`pages_per_split=15`，最后live split仅10个full page；把6-token tail放在该CTA的branchless full循环之后并合并到同一FP32 partial，删除独立8-CTA tail launch和第257个partial。case13既有同步`uint4` loader、raw row16 QK、wave barrier、split256和64-thread vec2 reducerownership均保持。
- **资源/profile**: fused producer=`60 MTreg/52 STreg/8192 B/0 spill/8 warps`，control full-only为`60/42/8192/8`，未降低occupancy；vec2 reducer保持`38/39/8`。100-call profiler中control full/tail/reducer=`241.495/7.557/23.345 μs`，candidate producer/reducer=`241.830/23.619 μs`，净省约`6.95 μs`。
- **A/B**: 41×200正向exp104/exp103b p10/p50/p90=`0.9708/0.9728/0.9746`，反向exp103b/exp104=`1.0273/1.0288/1.0344`，消偏`√(0.9728/1.0288)=0.9724`。无资源参数最终构建再测为正向p50=`0.9734`、反向=`1.0293`，消偏`0.9725`，case13稳定快约2.75%、约7.5 μs；case12/14正反均中性。
- **correctness/结论**: CPU14/14；同一最终`.so`的GPU full/boundary/random各14/14；case13精确length 1/2/15/16/17、240/241/255/256、480/481、3840/3841和full→short→full全部PASS；case13/14/12跨shape、FP32/BF16 workspace扩缩序列全部PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case13_last_split_tail_exp104.cpp`且与工作文件字节一致。提升为当前本地candidate baseline；OJ继续暂停。

### exp105-case11-headpair-z4-underfilled-last-split-tail  (LOCALLY POSITIVE, SUPERSEDED BY EXP106, OJ PAUSED, 2026-08-09)
- **父/control**: exp104，SHA `62f9ec33f55b228b961177299d7c1144a5f865dfd7e69eed2e0cff0fcdcef6a8`；候选SHA `f52f0b9452b9588da661610ba4178b34c51bc6a3a938b9dd6a2753dd94103dc4`；最终构建=`build/cuda_case11_last_split_tail_exp105.so`，资源构建=`build/cuda_case11_last_split_tail_exp105_resource.so`。
- **唯一假设**: case11有`full_pages=765`、`n_split=48`、`pages_per_split=16`，最后live split只拥有13个full page。让该split在branchless full循环之后吸收11-token tail，删除独立64-CTA tail launch和第49个partial；case8继续使用独立tail。head-pair/z4 CTA、同步`uint4` loader、raw row16双head QK、两级z-state归约和32-thread vec4 reducerownership均保持。
- **资源**: fused producer=`84 MTreg/54 STreg/8320 B/0 spill/staticMaxWarps=5`，control full producer=`84/46/8320/0/5`；vec4 reducer=`64 MTreg/35 STreg/staticMaxWarps=8`。tail冷路径没有抬高MT寄存器或降低occupancy。
- **A/B**: 资源构建41×200正向exp105/exp104 p10/p50/p90=`0.9901/0.9905/0.9911`，反向exp104/exp105=`1.0080/1.0088/1.0099`，消偏`√(0.9905/1.0088)=0.9909`。无资源参数最终构建正向=`0.9900/0.9907/0.9911`、反向=`1.0072/1.0080/1.0090`，消偏`0.9914`；case11稳定快约0.86%、约5.5 μs。case8/13/14双向消偏约`0.9988/1.0007/1.0002`，均中性。
- **correctness/结论**: CPU14/14；同一最终`.so`的GPU full/boundary/random各14/14。case11同进程`12251→1→2→15→16→17→256→257→271→272→512→513→12251`全部PASS；case11/14/13/12交替的9步full/short/cross-shape workspace扩缩全部PASS，所有输出finite且100%元素在容差内。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_last_split_tail_exp105.cpp`，与工作文件字节一致。提升为当前本地candidate baseline；OJ继续暂停。

### exp106-case8-bsm-headpair-z4-last-split-tail  (LOCALLY POSITIVE, SUPERSEDED BY EXP107, OJ PAUSED, 2026-08-09)
- **父/control**: exp105，SHA `f52f0b9452b9588da661610ba4178b34c51bc6a3a938b9dd6a2753dd94103dc4`；候选SHA `f5b0fd660e97b94095296769823bbf3120df5c8c3331b1c422ad4b709aabcffb`；最终构建=`build/cuda_case8_last_split_tail_exp106.so`，资源构建=`build/cuda_case8_last_split_tail_exp106_resource.so`。
- **唯一假设**: case8满容量有256个page、`n_split=48`、`pages_per_split=6`，43个live split中的最后一个只有4/6页；满长度没有tail，但旧separate-tail仍发出64-CTA空kernel并预留第49个partial。删除该launch/slot，变长输入的真实tail则由最后full-page owner在branchless循环后吸收。case8既有BSM loader、head-pair/z4 CTA、raw row16双head QK、wave barrier与32-thread vec4 reducerownership均保持；case11继续走exp105同步融合路径。
- **资源**: BSM fused producer=`84 MTreg/54 STreg/8320 B/0 spill/staticMaxWarps=5`，control BSM full producer=`84/46/8320/0/5`；vec4 reducer=`64 MTreg/35 STreg/staticMaxWarps=8`。冷尾页没有降低occupancy。
- **A/B**: 资源构建41×200正向exp106/exp105 p10/p50/p90=`0.9880/0.9892/0.9901`，反向exp105/exp106=`1.0094/1.0106/1.0117`，消偏`0.9894`。无资源参数最终构建正向=`0.9870/0.9885/0.9897`、反向=`1.0089/1.0098/1.0105`，消偏`√(0.9885/1.0098)=0.9894`；case8稳定快约1.06%、约2.8 μs。case11/13/14双向消偏约`1.0000/0.9995/0.9997`，均中性。
- **correctness/结论**: CPU14/14；同一最终`.so`的GPU full/boundary/random各14/14。case8同进程`4096→1→2→15→16→17→95→96→97→111→112→191→192→193→4095→4096`全部PASS；case8/14/11/13/12交替的9步workspace扩缩全部PASS，所有输出finite且100%元素在容差内。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case8_last_split_tail_exp106.cpp`，与工作文件字节一致。提升为当前本地candidate baseline；OJ继续暂停。

### exp107-case9-kv8-last-split-tail  (LOCALLY POSITIVE, SUPERSEDED BY EXP108, OJ PAUSED, 2026-08-09)
- **父/control**: exp106，SHA `f5b0fd660e97b94095296769823bbf3120df5c8c3331b1c422ad4b709aabcffb`；候选SHA `51337fb6f0885ab41eea3a730f61970150db55790df562774d8c3b2a74444855`；最终构建=`build/cuda_case9_last_split_tail_exp107.so`，资源构建=`build/cuda_case9_last_split_tail_exp107_resource.so`。
- **唯一假设**: case9满容量有256个page、`n_split=24`、`pages_per_split=11`，最后live split只有3/11页；满长度无tail但旧路径仍发出256-CTA空tail kernel并让vec4 reducer/partial布局使用25 slots。删除该launch/slot，变长tail由最后full-page owner在branchless循环后吸收。同步`uint4` loader、KV8 `(16,4,4)` CTA、raw row16 QK、wave barrier和exp92 vec4 reducerownership均保持。
- **资源**: fused producer=`60 MTreg/52 STreg/8192 B/0 spill/staticMaxWarps=8`，control full producer=`60/42/8192/0/8`；vec4 reducer=`64 MTreg/35 STreg/staticMaxWarps=8`，occupancy不变。
- **A/B**: 资源构建41×200正向exp107/exp106 p10/p50/p90=`0.9968/0.9973/0.9979`，反向exp106/exp107=`1.0032/1.0036/1.0044`，消偏`0.9968`。最终构建正向=`0.9970/0.9974/0.9987`、反向=`1.0026/1.0037/1.0042`，消偏`√(0.9974/1.0037)=0.9969`；case9稳定快约0.31%、约1.6 μs。case8/11/13/14双向消偏约`0.9995/0.9997/1.0002/1.0003`，均中性。收益虽小，但case9的每1%计分杠杆最高，保留为组合主链节点。
- **correctness/结论**: CPU14/14；同一最终`.so`的GPU full/boundary/random各14/14。case9同进程`4096→1→2→15→16→17→175→176→177→191→192→351→352→353→4095→4096`全部PASS；case9/14/8/11/13/12交替的10步workspace扩缩全部PASS，所有输出finite且100%元素在容差内。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case9_last_split_tail_exp107.cpp`，与工作文件字节一致。提升为当前本地candidate baseline；OJ继续暂停。

### exp108-case7-kv8-last-split-tail-group8  (LOCALLY POSITIVE, SUPERSEDED BY EXP109, OJ PAUSED, 2026-08-09)
- **父/control**: exp107，SHA `51337fb6f0885ab41eea3a730f61970150db55790df562774d8c3b2a74444855`；候选SHA `9b67b66fb94987c634143ca39e1970f833c524bd021f6af633b3ffd63a2c3454`；最终构建=`build/cuda_case7_last_split_tail_exp108.so`，资源构建=`build/cuda_case7_last_split_tail_exp108_resource.so`。
- **唯一假设**: case7满容量有128个page、`n_split=14`、`pages_per_split=10`，最后live split有8/10页；旧路径仍发出512-CTA空tail kernel并使用15 slots。删除该launch/slot，变长tail由最后full-page owner吸收。producer继续使用同步`uint4`、KV8 `(16,4,4)`、raw row16 QK和wave barrier；reducer继续使用case7已证明的8-head/CTA、16-lane shuffle权重布局，只新增fused-tail full-page-owner计数。
- **资源**: fused producer=`60 MTreg/52 STreg/8192 B/0 spill/staticMaxWarps=8`，control full producer=`60/42/8192/0/8`；fused group8 reducer=`66 MTreg/24 STreg/0 spill/staticMaxWarps=7`，与原shuffle reducer同档。
- **A/B**: 资源构建41×200正向exp108/exp107 p10/p50/p90=`0.9950/0.9954/0.9960`，反向exp107/exp108=`1.0046/1.0050/1.0058`，消偏约`0.9952`。最终构建正向=`0.9943/0.9953/0.9958`、反向=`1.0042/1.0052/1.0057`，消偏`√(0.9953/1.0052)=0.9951`；case7稳定快约0.49%、约2.6 μs。case8/9/11/12/13/14双向消偏约`1.0010/1.0006/1.0002/1.0000/1.0005/0.9999`，均中性。
- **correctness/结论**: CPU14/14；同一最终`.so`的GPU full/boundary/random各14/14。case7同进程`2048→1→2→15→16→17→159→160→161→175→176→319→320→321→2047→2048`全部PASS；case7/14/9/8/11/13/12交替的11步workspace扩缩全部PASS，所有输出finite且100%元素在容差内。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case7_last_split_tail_exp108.cpp`，与工作文件字节一致。当时提升为本地candidate baseline，后由exp109取代；OJ继续暂停。

### exp109-case12-kv8-empty-tail-removal  (LOCALLY POSITIVE, SUPERSEDED BY EXP110, OJ PAUSED, 2026-08-09)
- **父/control**: exp108，SHA `9b67b66fb94987c634143ca39e1970f833c524bd021f6af633b3ffd63a2c3454`；候选SHA `a4185589ccf01ac01485cb9ee1d26b9f28043d24d343dde0ba9402d8cef81718`；最终fresh build=`build/cuda_case12_empty_tail_exp109_verified.so`，资源构建=`build/cuda_case12_empty_tail_exp109_resource.so`。
- **唯一假设**: case12满容量有2048页，`n_split=128`、`pages_per_split=16`，恰好被128个full owner完全覆盖；旧路径仍发出64-CTA空tail kernel并为vec4 reducer保留第129个partial。只对case12删除该空launch/slot，变长输入的真实tail由最后full-page owner在branchless full循环后处理；同步`uint4` loader、KV8 `(16,4,4)`、raw row16 QK、wave barrier、split128和one-head vec4 reducerownership均保持。
- **资源**: fused producer=`60 MTreg/52 STreg/8192 B/0 spill/staticMaxWarps=8`，vec4 reducer=`64 MTreg/35 STreg/staticMaxWarps=8`；冷tail路径未降低occupancy。
- **A/B**: fresh build满长41×200正向exp109/exp108 p10/p50/p90=`0.9985/0.9988/0.9992`，反向exp108/exp109=`1.0013/1.0018/1.0026`，消偏`√(0.9988/1.0018)=0.9985`，约快0.15%。随机长度21×100正向=`0.9925/0.9933/0.9955`、反向=`1.0070/1.0079/1.0087`，消偏`0.9927`，约快0.73%。case7/8/9/11/13/14满长双向消偏约`0.9998/0.9997/0.9998/0.9998/0.9994/1.0012`，均为噪声范围内中性。
- **correctness/结论**: fresh build CPU14/14；同一`.so`的GPU full/boundary/random各14/14且全部finite。case12同进程`32768→1→2→15→16→17→255→256→257→271→272→511→512→513→32767→32768`全部PASS；`case12 full→case14 full→case12 exact257→case7 full→case12 full→case9/8/11/13 full→case12 exact513→case12 full`的11步workspace扩缩序列全部PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case12_empty_tail_exp109.cpp`且与工作文件字节一致。当时接纳为本地candidate baseline，后由exp110取代；所有既有separate-tail长shape的last-split/empty-tail路线至此闭合；OJ继续暂停。

### exp110-case11-sync-kv-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED BY EXP112, OJ PAUSED, 2026-08-09)
- **父/control**: exp109，SHA `a4185589ccf01ac01485cb9ee1d26b9f28043d24d343dde0ba9402d8cef81718`；候选SHA `5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81`；最终构建=`build/cuda_case11_register_prefetch_exp110.so`，资源构建=`build/cuda_case11_register_prefetch_exp110_resource.so`。
- **唯一假设/数据流**: 仅对case11同步head-pair/z4 full producer，把下一页K/V各16 B先读入每线程`uint4`寄存器，当前页PV结束后用一次wave barrier同时保护K/V覆盖，再写回同一个8 KiB shared page buffer；下一迭代原page-ready wave barrier负责发布。baseline的K-dead与V-dead分两次barrier，并在当前PV前同步global→shared写K、PV后再同步写V。候选不增加第二个shared buffer，不改变QK/PV/softmax、split48、fused tail、partial或reducer，也不同于只预取page ID的exp95。
- **资源**: candidate full=`92 MTreg/54 STreg/8320 B/0 spill/staticMaxWarps=5`，exp109 full=`84/54/8320/5`；两组lookahead恰增加8个MT寄存器，但未降低occupancy。未启用该模板参数的case8及其他shape资源不变。
- **A/B**: resource build首轮21×100正向exp110/exp109=`0.9390/0.9409/0.9435`，反向exp109/exp110=`1.0627/1.0633/1.0641`，消偏`0.9407`。fresh final 41×200正向=`0.9407/0.9412/0.9417`，反向=`1.0629/1.0634/1.0640`，消偏`√(0.9412/1.0634)=0.9408`；case11稳定快约5.92%、绝对p50约`0.638→0.600 ms`。case7/8/9/12/13/14双向消偏约`1.0001/0.9993/1.0002/0.9998/1.0000/0.9991`，均中性。
- **correctness/结论**: CPU14/14；同一fresh final `.so`的GPU full/boundary/random各14/14且全部finite。case11同进程`12251→1→2→15→16→17→255→256→257→271→272→511→512→513→767→768→769→12250→12251`全部PASS；`case11 full→case14 full→case11 exact257→case12 full→case11 full→case8/9/13 full→case11 exact513→case7 full→case11 full`的11步workspace序列PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_register_prefetch_exp110.cpp`。当时接纳为本地candidate baseline，后由exp112取代；同步global→shared直写是已确认的case11 full-producer瓶颈；OJ继续暂停。

### exp111-case12-k-only-register-lookahead  (RESOURCE-GATE REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp110，SHA `5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81`；候选SHA `7f34d8c706a6354bcacc3de496b9dbd80e0467c8ce6945a5795553c46d7505b1`；资源构建=`build/cuda_case12_k_register_prefetch_exp111_resource.so`。
- **唯一假设**: 只对case12同步KV8 full producer移植exp110流水的一半：下一页K以一个`uint4`留在寄存器跨越当前PV，随后一次wave barrier写K并按baseline直接加载V；不预取V，目标是把额外live state限制为4个MT寄存器并维持`staticMaxWarps=8`。其他case、split128、fused tail、raw QK、z-state和vec4 reducer不变。
- **资源门槛/结论**: 后端目标实例显示`60 MTreg/52 STreg/8192 B/staticMaxWarps=8`，表面寄存器数未升，但出现`32 B stack frame`；control为同资源且0 B stack。说明lookahead值被spill到local stack，而非获得可用寄存器流水。每页反复local-memory往返违反零spill强基线，因此不运行GPU correctness/A-B，直接rejected。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case12_k_register_prefetch_exp111.cpp`，工作文件恢复exp110。KV8的8-warps资源档不能直接套用此C++ live range；只有能静态保持0 stack的新表示或关键布局变化才允许重开。

### exp112-case8-sync-kv-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED BY EXP114, OJ PAUSED, 2026-08-09)
- **父/control**: exp110，SHA `5500309e3a17cc3c8cab8eceecb7ba8d1ac7fa6b661a0971adf55cd6bcc16a81`；候选SHA `867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20`；fresh A/B构建=`build/cuda_exp112_fresh_ab.so`，资源构建=`build/cuda_case8_sync_register_prefetch_exp112_resource.so`。
- **唯一假设**: 只把case8从BSM head-pair/z4 full producer切换到exp110已验证的同步K/V register-lookahead实例；split48、fused tail、raw row16双head QK、softmax/PV、两级z-state合并、partial与vec4 reducer全部保持exp110。该候选检验register-lookahead的barrier合并与load/compute调度窗口能否超过case8原BSM async copy，而不是重新比较baseline同步直写与BSM。
- **资源**: 目标同步lookahead实例=`92 MTreg/54 STreg/8320 B shared/0 spill/staticMaxWarps=5`，与exp110的case11实例同档；没有第二个shared buffer，也没有stack frame。
- **A/B**: fresh 41×200正向exp112/exp110 p10/p50/p90=`0.8961/0.8969/0.8979`，反向exp110/exp112=`1.1147/1.1166/1.1180`，加载顺序消偏`√(0.8969/1.1166)=0.8963`；case8稳定快约10.37%，绝对p50约`0.2595→0.2326 ms`。case7/9/11/12/13/14的21×100双向消偏约`1.0002/0.9997/0.9994/0.9999/0.9998/1.0001`，全部中性；case11保持约`0.600 ms`。
- **correctness/结论**: CPU14/14；同一final `.so`的GPU full/boundary/random各14/14且全部finite。case8同进程`4096→1→2→15→16→17→95→96→97→111→112→191→192→193→4095→4096`全部PASS；`case8 full→case14 full→case8 exact97→case12 full→case8 full→case11/9/13 full→case8 exact193→case7 full→case8 full`的11步跨shape workspace序列PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case8_sync_register_prefetch_exp112.cpp`，与工作文件字节一致。接纳为当前本地candidate baseline；case8/11都证明同步register-lookahead显著优于各自旧loader时序，OJ继续暂停。

### exp113-case11-k-only-register-lookahead  (REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp112，SHA `867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20`；候选SHA `3f339244e6c6c4a7df3c305b5b76004f18d3e578fc4e82bb648c1ed581e7277d`；资源构建=`build/cuda_case11_k_only_prefetch_exp113_resource.so`。
- **唯一假设**: 只对case11把K+V lookahead改成K-only：下一页K仍跨当前PV保存在寄存器，当前PV后用一次wave barrier同时保护K/V overwrite，但下一页V改为barrier后同步global→shared直写。case8继续使用exp112 K+V实例，split/fused-tail/QK/PV/state/reducer均不变。这样隔离V-over-PV重叠的贡献，并测试少一个`uint4` live state能否改善调度。
- **资源/correctness**: K-only full=`90 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`，比K+V control少2个MTreg但未跨occupancy档；CPU14/14、真实C500 case11 full 100% PASS，max error=`2.441406e-04`且finite。
- **A/B/结论**: 21×100正向K-only/exp112=`1.0306/1.0324/1.0338`，反向exp112/K-only=`0.9685/0.9693/0.9710`，消偏`√(1.0324/0.9693)=1.0320`；K-only稳定慢约3.20%，绝对p50约`0.600→0.619 ms`。两MTreg下降没有资源档收益，V load与PV重叠本身约有3.2%价值；性能门槛失败后不跑全量correctness。完整源码归档为`solutions/archive/2026-08-09-experiments/cuda_case11_k_only_register_prefetch_exp113.cpp`，工作文件恢复exp112；不得再以“只减少V live state”重试。

### exp114-case11-register-lookahead-early-page-id  (LOCALLY POSITIVE, SUPERSEDED BY EXP115, OJ PAUSED, 2026-08-09)
- **父/control**: exp112，SHA `867deaf62ae2767831451fb94a0c51273b2456a525fb87137cbefdc347a5de20`；候选SHA `c0b50cf2523b1b5439aa3fd128f0dc44a043b7ea29581f3ad005f433269b5409`；final build=`build/cuda_case11_early_pid_prefetch_exp114.so`，资源构建=`build/cuda_case11_early_pid_prefetch_exp114_resource.so`。
- **关键新前提/唯一假设**: 旧exp95在同步直写路径提前page ID慢0.58%，但exp110已把下一页K/V global load移到QK后并让两者直接依赖`bt_row[p+1]`。exp114只对case11在每轮page-ready之后、QK之前解析next page ID，使标量page-table load与当前QK重叠；K+V register-lookahead、单overwrite barrier、case8 dispatch、split/fused-tail/QK/PV/state/reducer均保持exp112。
- **资源**: early-ID full=`94 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`，control=`92/54/8320/0/5`；多2个MTreg但未跨occupancy档。
- **A/B**: resource首轮21×100正向exp114/exp112=`0.9896/0.9919/0.9938`，反向exp112/exp114=`1.0079/1.0086/1.0098`，消偏约`0.9917`。fresh final 41×200正向=`0.9915/0.9921/0.9929`，反向=`1.0079/1.0084/1.0087`，消偏`√(0.9921/1.0084)=0.9919`；case11稳定快约0.81%，绝对p50约`0.5996→0.5948 ms`。case8双向消偏约`1.0008`，中性。
- **correctness/结论**: CPU14/14；同一final `.so`的GPU full/boundary/random各14/14且finite。case11同进程`12251→1→2→15→16→17→255→256→257→271→272→511→512→513→767→768→769→12250→12251`全部PASS；跨case11/14/12/8/9/13/7的11步workspace序列PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case11_early_pid_prefetch_exp114.cpp`，与工作文件字节一致。接纳为当前本地candidate baseline；这次重开成立的原因是register-lookahead新增了真实PID→K/V依赖链，不能把结论外推回旧同步直写路径；OJ继续暂停。

### exp115-case8-register-lookahead-early-page-id  (LOCALLY POSITIVE, SUPERSEDED BY EXP120, OJ PAUSED, 2026-08-09)
- **父/control**: exp114，SHA `c0b50cf2523b1b5439aa3fd128f0dc44a043b7ea29581f3ad005f433269b5409`；候选SHA `b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`；final build=`build/cuda_case8_early_pid_prefetch_exp115.so`。
- **唯一假设**: 只把case8 dispatch从K+V register-lookahead切到exp114已经编译和验证的early-page-ID同一实例；case11保持exp114，kernel代码、资源、split48、fused-tail、QK/PV/state/reducer与其他shape均不变。验证较短的case8每split page-loop是否也受PID→K/V load依赖约束。
- **A/B**: 首轮21×100正向exp115/exp114=`0.9900/0.9915/0.9963`，反向exp114/exp115=`1.0045/1.0069/1.0095`，消偏约`0.9923`。强复测41×200正向=`0.9911/0.9931/0.9950`，反向=`1.0071/1.0076/1.0087`，消偏`√(0.9931/1.0076)=0.9928`；case8稳定快约0.72%，绝对p50约`0.2332→0.2315 ms`。case11 21×100双向消偏约`1.0000`，中性。
- **correctness/结论**: CPU14/14；同一candidate `.so`的GPU full/boundary/random各14/14且finite。case8同进程`4096→1→2→15→16→17→95→96→97→111→112→191→192→193→4095→4096`全部PASS；跨case8/14/12/11/9/13/7的11步workspace序列PASS。完整源码为`solutions/archive/2026-08-09-experiments/cuda_case8_early_pid_prefetch_exp115.cpp`，与工作文件字节一致。接纳为当前本地candidate baseline；early-ID收益已分别在case11/case8复现，但仅覆盖K+V register-lookahead head-pair/z4实例；OJ继续暂停。

### exp116-case11-one-page-ahead-pid-pipeline  (REJECTED, OJ PAUSED, 2026-08-09)
- **父/control**: exp115，SHA `b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`；候选SHA `8673c1fbf5ed1620560b634b3bfcb7ba5a7ff16f2ecdb3e662e494f0f376f61e`；资源构建=`build/cuda_case11_pipelined_pid_exp116_resource.so`。
- **唯一假设**: 只对case11把exp114的“当前轮QK前读取p+1 ID”改为one-page-ahead：初始化p+1，当前轮保存该ID并同时读取p+2供下一轮，令page-table latency覆盖一整页；case8保持exp115同轮early-ID，K+V lookahead、barrier、split、数学和reducer均不变。
- **资源/correctness**: pipelined-ID full=`92 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`，比同轮early-ID的94 MTreg少2个且不跨档；CPU14/14、真实C500 case11 full 100% PASS，max error=`2.441406e-04`且finite。
- **A/B/结论**: 21×100正向exp116/exp115=`1.0109/1.0115/1.0122`，反向exp115/exp116=`0.9882/0.9893/0.9907`，消偏`√(1.0115/0.9893)=1.0112`；case11稳定慢约1.12%，绝对p50约`0.595→0.601 ms`。跨整页保存/更新PID的依赖与控制代价超过更长重叠窗口，MTreg下降没有性能价值；性能门槛失败后不跑全量correctness。完整源码归档为`solutions/archive/2026-08-09-experiments/cuda_case11_pipelined_pid_exp116.cpp`，工作文件恢复exp115。同一PID family的最佳粒度是exp114/115的同轮QK前读取，不再扫描更早页距。

### exp86–116 阶段复盘（2026-08-09，OJ PAUSED）
- **已组合收益**: exp87/88/89/91/92/94分别收割case10/8/11/12/9/13 reducer，端到端消偏约`0.9698/0.9687/0.9872/0.9933/0.9972/0.9936`；exp103b/104/105/106/107/108/109再让case14/13/11/8/9/7/12消除独立tail launch并在需要时由last split吸收尾页，分别消偏`0.9769/0.9725/0.9914/0.9894/0.9969/0.9951/0.9985`；exp110让case11同步full producer再消偏`0.9408`，exp112把同一流水扩展到case8并替换BSM后再消偏`0.8963`，exp114/115又让case11/case8提前解析register-lookahead的page ID依赖并分别消偏`0.9919/0.9928`。exp115是当前正确主链末端，SHA `b73fb54d…d6`，同一candidate `.so`三组GPU 14/14、16个case8定点长度和跨shape workspace复用均已通过。
- **reducer边界**: exp86的case10 group8因CTA不足慢13.4%；exp90证明B1 case13的32-thread vec4低填充慢1.05%，exp94恢复64-thread vec2后翻正；exp93证明15-partial case7应保留无动态shared group8。线程数必须按总CTA与原生64-lane wave填充选择，不再做全局统一。
- **case11 full producer转折**: exp95 page-ID预取慢0.58%、exp96 packed-Q资源不变、exp97 FP32 K跨row广播慢41.3%、exp98 head4 sequential-pair资源恶化到140 MTreg/3 warps，关闭了四条局部路线；exp110改动真正的global-load/shared-overwrite时序后翻为约5.92%收益。后续优先研究同类单buffer寄存器lookahead及barrier合并的资源边界，不再回到标量ID、Q表示或跨row广播微调。
- **lookahead资源边界**: exp110的head-pair full从84增至92 MTreg仍保持5 warps、0 spill；exp112在相同资源档把该流水扩展到case8并获得10.37%收益。exp113的case11 K-only虽降到90 MTreg，未跨档且因失去V-over-PV重叠慢3.20%；exp111的KV8 K-only源码则在60 MTreg/8 warps下产生32 B stack。不能仅看MTreg和staticMaxWarps判断流水可行性，stack frame与实际load overlap都是硬门槛；KV8扩展必须先解决live value表示，不能用A/B掩盖spill。
- **PID依赖边界**: 旧同步直写exp95提前PID慢0.58%；register-lookahead改变关键依赖后，exp114/115在case11/8同轮QK前读取分别快0.81%/0.72%；exp116提前一整页反而慢1.12%。因此只保留同轮early-ID，不再扫描p+2或更长距离，也不能把该结论外推到没有K+V register-lookahead的路径。
- **tail调度边界**: exp99证明case10忽略尾页虽有约0.75%上界但语义错误；exp100独立tail launch慢1.60%，exp101 reducer融合慢0.92%，exp102直接global-max融合仅中性。exp103b–109已完成全部既有separate-tail长shape扩展：underfilled owner的收益可达约0.3–2.8%，case12即使last split无slack，单纯删除满长空launch/partial仍有约0.15%收益，但该微方向已经耗尽。新实验必须转向full producer/page pipeline、barrier/shared state或真正不同的数据流，不再继续细扫相同tail模板。

## 评分地图 (Phase 0)
连续评分 S(Tk)=100/(1+(Tk-Th)/(Tb-Th))，总分=14 case 均值。每 1% 降速得分收益：
case9=0.86, case7=0.30, case8/13=0.26, case11/14=0.24, 4/5/6=0.22。
但 case7/9/12/13 已≈baseline(case9: 321 vs Tb 317)，进一步须 *超越* flash_attn，难。
**最大可达成 headroom 在 KV4: case8(175 vs 111, +57%)、case14(297 vs 172, +73%)、case11(448 vs 249, +80%)**，均用 scalar QK(MMA-QK 因 correctness 被禁)。KV4 compute 是最高杠杆架构方向。

### exp117-case14-independent-z-cta  (REJECTED, OJ PAUSED, 2026-08-10)
- **父/control**: exp115，SHA `b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`；候选SHA `783a1af158db38a211d25a436c4d087782652ecdfbca15fa07d1ed1c80d7557c`；资源构建=`build/cuda_case14_independent_z_exp117_resource.so`。
- **关键新前提/唯一假设**: 与exp55丢失page pipeline的z1/chunk4不同，本候选保留case14的BSM单bufferpage pipeline、每z完整8-token QK/PV、Q staging、raw row16 QK、fused tail和normalized-BF16 partial数学。只把原`dim3(16,8,2)`的两个z拆成两个`dim3(16,8,1)` CTA；每CTA在shared中只保存自己的8个token row，K/V static shared从8320降到4096 B，并把z-state直接导出给最终reducer。逻辑split仍257，因此物理CTA/partial从257增到514。
- **资源**: 目标producer=`78 MTreg/52 STreg/4096 B shared/0 B stack/staticMaxWarps=6`；control fused producer=`70/56/8320 B/0/7`，但256-thread control实际只能驻留1 block/4 waves，候选128-thread静态上可驻留3 blocks/6 waves。资源门槛首次满足低线程布局的occupancy前提。
- **correctness**: CPU语义14/14；真实C500 case14 full 100% PASS，`max_error=1.220703e-04`、finite。定点`1,2,7,8,9,15,16,17,127,128,129,239,240,241,255,256,257,479,480,481,3839,3840,3841,61518,61519`全部100% PASS，覆盖z1启用、tail-only、15-pages/split模数和full边界。
- **A/B/结论**: 21×100正向exp117/exp115 p10/p50/p90=`1.0616/1.0659/1.0682`；反向exp115/exp117=`0.9325/0.9361/0.9961`，消偏`√(1.0659/0.9361)=1.0671`，稳定慢约6.71%。完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case14_independent_z_exp117.cpp`。occupancy与shared前提成立仍不足以覆盖物理CTA和reducer翻倍，拒绝但保留split数量归因问题给exp118。

### exp118-case14-independent-z-split129  (REJECTED, OJ PAUSED, 2026-08-10)
- **父/control**: exp117，SHA `783a1af158db38a211d25a436c4d087782652ecdfbca15fa07d1ed1c80d7557c`；候选SHA `f324ac23590f1b22777cc5160245a1ce5e72cd258ad9b111d18a72ac64abf5da`；资源构建=`build/cuda_case14_independent_z_split129_exp118_resource.so`。
- **唯一假设**: 只把case14独立-z架构的逻辑split从257降到129，使物理CTA/partial从514降到258、接近control的257；每CTA上限从15增到30个half-page。kernel数据流、4 KiB shared、资源、fused tail和reducer数学均保持exp117。
- **correctness**: case14 full 100% PASS且finite；定点`1,2,7,8,9,15,16,17,479,480,481,959,960,961,61518,61519`全部PASS，覆盖30-pages/split模数与z/tail边界。
- **A/B/结论**: 21×100正向exp118/exp115=`1.0283/1.0361/1.0383`，反向exp115/exp118=`0.9602/0.9632/0.9679`，消偏`√(1.0361/0.9632)=1.0372`，仍慢约3.72%。相较exp117收回约3个百分点，证明partial/CTA翻倍是部分成本，但独立-z本身仍不优于CTA内合并。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case14_independent_z_split129_exp118.cpp`。

### exp119-case14-independent-z-split86  (REJECTED, FAMILY CLOSED, OJ PAUSED, 2026-08-10)
- **父/control**: exp118，SHA `f324ac23590f1b22777cc5160245a1ce5e72cd258ad9b111d18a72ac64abf5da`；候选SHA `c10c0acee426cf831a9766c66d2c5d14ee2cc1297632e9d9e0b9922447298795`；最终构建=`build/cuda_case14_independent_z_split86_exp119.so`。
- **唯一假设**: 作为第三个且最后一个split节点，只把逻辑split`129→86`，得到172个物理partial、45 half-pages/CTA，在保持足够grid工作的同时进一步摊薄Q staging和reducer。
- **correctness**: case14 full 100% PASS，`max_error=1.220703e-04`且finite；定点`1,8,9,15,16,17,719,720,721,1439,1440,1441,61518,61519`全部PASS。
- **A/B/结论**: 21×100正向exp119/exp115=`1.1930/1.1951/1.1994`，反向exp115/exp119=`0.8306/0.8356/0.8384`，消偏`√(1.1951/0.8356)=1.1959`，慢约19.59%，说明45-page串行深度和较少grid work已跨入陡降区。三个有效节点split257/129/86均未获益，最佳仍慢3.72%；独立-z 128-thread CTA + exported partial family按规则关闭，不再扫描附近split、loader或reducer。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case14_independent_z_split86_exp119.cpp`；工作文件已恢复exp115（SHA `b73fb54d…d6`）。

### exp120-case14-generic-z2-register-lookahead  (LOCALLY POSITIVE, CURRENT LOCAL BASELINE, OJ PAUSED, 2026-08-10)
- **父/control**: exp115，SHA `b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`；候选SHA `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`；final build=`build/cuda_case14_register_lookahead_exp120.so`，资源构建=`build/cuda_case14_register_lookahead_exp120_resource.so`。
- **关键新前提/唯一假设**: exp112已证明case8的同步K/V register-lookahead可显著超过BSM，但case14 generic-z2从未验证。本候选只对case14 full producer把下一页K/V各16 B预读到每线程`uint4`寄存器，在当前PV期间保持；PV后一次CTA barrier同时保护当前K/V消费者，随后把两组向量写回同一个8 KiB shared buffer，下一轮page-ready CTA barrier发布。保留`dim3(16,8,2)`、BSM cold fused-tail、split257、Q staging、raw row16 QK、online softmax/PV、CTA内z合并、normalized-BF16 partial和原reducer。generic每z跨两个wave，不能照搬head-pair的wave barrier。
- **资源**: candidate fused producer=`78 MTreg/56 STreg/8320 B shared/0 B stack/staticMaxWarps=6`；control=`70/56/8320/0/7`。两者256-thread CTA实际均为1 block/4 active waves，寄存器增加未降低实际occupancy；无spill。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14，全部finite。case14同进程`61519→1→8→9→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS，覆盖tail-only、首次full page、z边界、15-pages/split模数与full-short-full workspace复用。
- **A/B**: 初轮21×100正向exp120/exp115=`0.9426/0.9478/0.9517`，反向exp115/exp120=`1.0436/1.0525/1.0571`，消偏约`0.9489`。final 41×200正向=`0.9467/0.9486/0.9501`，反向=`1.0514/1.0524/1.0536`，消偏`√(0.9486/1.0524)=0.9495`，稳定快约5.05%，绝对p50约`0.2778→0.2636 ms`。case8/11/13的双加载顺序消偏约`1.0000/0.9998/0.9984`，均中性。
- **结论**: 接纳为当前本地candidate baseline；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case14_register_lookahead_exp120.cpp`且与`solutions/cuda_maca_optimized.cpp`字节一致。同步register-lookahead现在已在case11/8/14三种KV4布局复现；下一步只对case14验证同轮early-page-ID，不能同时改loader、split、barrier或reducer。OJ继续暂停。

### exp121-case14-register-lookahead-early-page-id  (REJECTED, OJ PAUSED, 2026-08-10)
- **父/control**: exp120，SHA `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`；候选SHA `ccc58a6ecc9262a5e6a38a958ea57b5ce4d9ff46f5046e2f76ea6f5019ea295c`；final build=`build/cuda_case14_early_pid_exp121.so`，资源构建=`build/cuda_case14_early_pid_exp121_resource.so`。
- **唯一假设**: 保持exp120的generic `(16,8,2)`、同步K/V register-lookahead、split257、两道page-loop CTA barrier、raw row16 QK、fused tail、CTA内z合并、normalized-BF16 partial和reducer不变；只把`bt_row[p+1]`读取从QK后移到page-ready之后、QK之前，使标量page-table latency与当前QK重叠。
- **资源/correctness**: 目标实例=`78 MTreg/54 STreg/8320 B shared/0 B stack/staticMaxWarps=6`，control=`78/56/8320/0/6`，两者实际均为4 active waves；CPU14/14、真实C500 case14 full 100% PASS，`max_error=1.220703e-04`且finite。
- **A/B/结论**: 21×100正向exp121/exp120 p10/p50/p90=`1.0106/1.0123/1.0146`，反向exp120/exp121=`0.9812/0.9854/0.9884`，消偏`√(1.0123/0.9854)=1.0136`，稳定慢约1.36%。generic-z2中提前ID虽少2个STreg，却延长uniform PID live range/调度并回退；head-pair exp114/115的early-ID收益不能外推到generic-z2。完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case14_early_pid_exp121.cpp`，工作文件已恢复exp120；不继续扫描PID放置或预取距离，OJ继续暂停。

### exp122-case14-initial-page-ready-q-barrier-fusion  (NEUTRAL / REJECTED, OJ PAUSED, 2026-08-10)
- **父/control**: exp120，SHA `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`；候选SHA `ad72414094d768f79f26b0701bce559d5b5271f68f3c1ffae3368a3ebcae772c`；final build=`build/cuda_case14_initial_barrier_fusion_exp122.so`，资源构建=`build/cuda_case14_initial_barrier_fusion_exp122_resource.so`。
- **唯一假设**: case14的Q使用独立2 KiB dynamic shared，和8 KiB K/V static shared不别名；因此只把首页同步K/V写提前到Q staging之后、既有Q CTA barrier之前，让同一道barrier同时发布Q和首页K/V，并把后续page-ready barrier移到前一轮K/V store之后。每个full producer CTA恰好少一次barrier；register-lookahead、每页overwrite/page-ready依赖、split257、QK/PV、fused tail、z合并、partial和reducer不变。
- **资源/correctness**: 目标实例=`78 MTreg/54 STreg/8320 B shared/0 B stack/staticMaxWarps=6`，实际4 active waves；CPU14/14、真实C500 case14 full 100% PASS，`max_error=1.220703e-04`且finite。
- **A/B/结论**: 21×100正向exp122/exp120=`0.9991/1.0017/1.0062`，反向exp120/exp122=`0.9935/0.9968/0.9994`，消偏`√(1.0017/0.9968)=1.0025`，约慢0.25%且区间跨1，归类中性/拒绝。一次性barrier并非case14当前可见瓶颈，不进入41×200或全量correctness；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case14_initial_barrier_fusion_exp122.cpp`，工作文件恢复exp120。下一步必须针对每页热循环而不是CTA固定开销，OJ继续暂停。

### exp123-case14-stagger-next-v-at-pv-midpoint  (REJECTED, FAMILY CLOSED, OJ PAUSED, 2026-08-10)
- **父/control**: exp120，SHA `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`；候选SHA `3e85bd766f1987bfabea8ed62c5644ea2ca303a160f607799653c0ce1d992c59`；final build=`build/cuda_case14_stagger_v_exp123.so`，资源构建=`build/cuda_case14_stagger_v_exp123_resource.so`。
- **唯一假设**: 保留next-K在完整当前PV期间的重叠，只把next-V vector load从QK后延到8-token PV循环的中点；目标是避免K/V两次global load连发并缩短V live range，同时仍保留后半段PV的V-load latency hiding。loader宽度、shared overwrite、两道每页CTA barrier、split、QK/PV数学和reducer不变。
- **资源/correctness**: 在unrolled PV中插入load反而使目标实例从exp120的`78 MTreg/56 STreg/6 warps`恶化到`94/56/5`，shared仍8320 B、0 stack；256-thread CTA实际仍4 active waves。CPU14/14、真实C500 case14 full 100% PASS，`max_error=1.220703e-04`且finite。
- **A/B/结论**: 21×100正向exp123/exp120=`1.0229/1.0248/1.0271`，反向exp120/exp123=`0.9708/0.9730/0.9751`，消偏`√(1.0248/0.9730)=1.0263`，稳定慢约2.63%。中点load破坏后端unroll/live-range复用且半程overlap不足；完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case14_stagger_v_exp123.cpp`，工作文件恢复exp120。generic-z2中在PV内部扫描2/4/6-token next-V插入点的family关闭，OJ继续暂停。

### exp124-case10-full-only-last-split-tail  (CORRECTNESS INCOMPLETE, SUPERSEDED BY EXP124B, OJ PAUSED, 2026-08-10)
- **父/control**: exp120，SHA `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`；候选SHA `35a6a16478e0e061e8c26f7f50be1f66f4fa85a0542c189e23c3bf0f12a76cc3`；资源构建=`build/cuda_case10_full_fused_tail_exp124_resource.so`。
- **关键新前提/唯一假设**: exp99证明case10 branchless full-only有约0.75%上界，但没有处理真实tail而语义错误；exp124保持BSM loader、raw row16 QK、split128、FP32 partial和vec4 reducerownership，只让最后一个拥有full page的split在branchless循环后吸收tail，从而不增加独立tail launch。
- **资源与初始correctness**: full producer从combined control的`92 MTreg/48 STreg/8320 B/5 warps`降到`70/56/8320 B/7`，0 stack、实际仍4 active waves。CPU14/14、case10 full/boundary/random表面均100% PASS，但这些分布未命中4-pages/split的关键模数。
- **反例/结论**: 同进程定点在length `65/129/193`分别仅`0.6875/0.92627/0.985596`元素满足容差；producer已把tail写进前一个full-page owner，case10 vec4 reducer却仍按`ceil(valid_pages/pages_per_split)`多读一个未写partial。原始exp124不可提交、不可作为control；完整源码保留在`solutions/archive/2026-08-10-experiments/cuda_case10_full_fused_tail_exp124.cpp`，随后只修reducer计数形成exp124b。

### exp124b-case10-fused-tail-live-split-fix  (LOCALLY POSITIVE, SUPERSEDED BY EXP125, 2026-08-10)
- **父/control**: exp124，SHA `35a6a16478e0e061e8c26f7f50be1f66f4fa85a0542c189e23c3bf0f12a76cc3`；候选SHA `f98112aa776b2cf80ecdb3880baa402475a4db4a07c8a4ce8518398caa50d016`；final build=`build/cuda_case10_full_fused_tail_exp124b.so`，资源构建=`build/cuda_case10_full_fused_tail_exp124b_resource.so`。
- **唯一修复**: producer、dispatch、split和数学完全保持exp124，只给case10的32-thread vec4 reducer打开`FUSE_TAIL_IN_LAST_SPLIT`计数，令live split为`ceil(full_pages/pages_per_split)`；零full-page tail-only仍使用split0。这与exp103b相同语义，但首次覆盖case10 vec4 reducer。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。case10同进程`1,2,15,16,17,63,64,65,127,128,129,191,192,193,8191,8192`全部100% PASS，原三个失败点均修复；full最大误差`2.441406e-04`、random最大误差`4.882812e-04`。
- **A/B**: 初轮21×100正向exp124b/exp120=`0.9763/0.9912/1.0109`，反向exp120/exp124b=`0.9938/1.0085/1.0181`，消偏约`0.9914`。强复测61×500正向=`0.9867/0.9921/0.9996`，反向=`1.0001/1.0064/1.0111`，消偏`√(0.9921/1.0064)=0.9929`，case10稳定快约0.71%，绝对p50约`0.0607→0.0602 ms`。非目标case14正反p50=`0.9988/0.9997`，消偏约`0.9995`，中性。
- **结论**: 接纳为本地主链节点，后续已被exp125取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case10_full_fused_tail_exp124b.cpp`。branchless full-only在正确last-split tail前提下兑现了exp99的性能上界，并为单独测试case10 generic K/V register-lookahead建立了正确父版本。

### exp125-case10-register-lookahead  (LOCALLY POSITIVE, OJ #107856 CANCELED / SUPERSEDED LOCALLY BY EXP130, 2026-08-10)
- **父/control**: exp124b，SHA `f98112aa776b2cf80ecdb3880baa402475a4db4a07c8a4ce8518398caa50d016`；候选SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；final build=`build/cuda_case10_register_lookahead_exp125.so`，资源构建=`build/cuda_case10_register_lookahead_exp125_resource.so`。
- **唯一假设**: 只把case10的full producer从BSM切为同步K/V register-lookahead；exp124b的full-only+last-split fused tail、split128/4 pages、raw row16 QK、FP32 partial、vec4 reducer和corrected live-split计数全部不变。目标是让下一页K/V global load与当前页PV重叠，并仍复用单个8 KiB shared buffer。
- **资源/correctness**: full producer从exp124b的`70 MTreg/56 STreg/8320 B/0 stack/staticMaxWarps=7`变为`78/56/8320 B/0/6`，两者在256-thread CTA上实际均为4 active waves。CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite；case10同进程`1,2,15,16,17,63,64,65,127,128,129,191,192,193,8191,8192`全部100% PASS。
- **A/B**: case10强复测61×500正向exp125/exp124b=`0.9611/0.9671/0.9726`，反向exp124b/exp125=`1.0267/1.0340/1.0392`，消偏`√(0.9671/1.0340)=0.9671`，稳定快约3.29%，绝对p50约`60.1→58.1 μs`。非目标case14的21×100正反p50=`0.9983/0.9998`，消偏`0.99925`，中性。
- **结论/OJ**: 完整源码为`solutions/archive/2026-08-10-experiments/cuda_case10_register_lookahead_exp125.cpp`。2026-08-10串行创建唯一提交#107856，长时间保持Pending；平台恢复后为避免与更强候选并行，于提交exp131前先取消并确认状态为Canceled。它未产生性能结果，后续在本地已被exp130取代。case10成为同步register-lookahead在case11/8/14之外的第四个正向shape。

### exp126-case5-full-only-last-split-tail  (REJECTED, 2026-08-10)
- **父/control**: exp125，SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；候选SHA `6a5b9115819bc439fc9e814d94fae1c3bcc9e2f87280b4ee06bab087f38bbfb3`；final build=`build/cuda_case5_full_fused_tail_exp126.so`。
- **唯一假设**: case5保持split5/2 pages、BSM loader、raw row16 QK、FP32 partial和group8 reducer，只把combined producer改为branchless full-only并由最后full-page owner吸收tail；reducer同步按full-page owner计数，避免exact split模数读取未写partial。
- **correctness**: CPU14/14；case5 full 100% PASS且finite。单进程精确长度`1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140,141`全部100% PASS，覆盖2-pages/split的两侧模数；最大误差`1.5625e-02`仍在OJ容差内。
- **A/B/结论**: 41×500首轮exp126/exp125=`1.1372/1.1452/1.1524`，稳定慢约14.52%，差异远离噪声，因此不再浪费一次反向长测。case5的combined split4可让第5个CTA独立并行处理tail；融合后tail被串到已处理两页的最后full-owner，critical split从约2页变成3页，远大于branchless收益。完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case5_full_fused_tail_exp126.cpp`，工作文件恢复exp125；case5在split5下的last-split tail融合方向关闭。

### exp127-case5-combined-register-lookahead  (REJECTED, 2026-08-10)
- **父/control**: exp125，SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；候选SHA `477a4424da53cf728f32f37707c1af8fdd558fc3ffbf4452c0d9107ca62780f4`；final build=`build/cuda_case5_combined_register_lookahead_exp127.so`。
- **唯一假设**: 保持case5 combined split5的独立tail CTA、raw row16 QK、FP32 partial与group8 reducer完全不变；仅放宽generic-z2 register-lookahead到combined producer，让每个两页split的第二页K/V load与第一页PV重叠。tail masking和page ownership不变。
- **correctness**: 单进程精确长度`1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140,141`全部100% PASS且finite，证明register-held完整物理tail page仍被既有token mask正确约束。
- **A/B/结论**: 41×500正向exp127/exp125=`1.0032/1.0193/1.0343`，反向exp125/exp127=`0.9805/0.9873/1.0008`，消偏`√(1.0193/0.9873)=1.0161`，稳定慢约1.61%。两页split只有一次后继页重叠机会，register live range与CTA barrier成本超过收益；完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case5_combined_register_lookahead_exp127.cpp`，工作文件恢复exp125。case5 split5的generic register-lookahead关闭，不向该短循环叠加early-ID或V-load位置微调。

### exp128-case10-initial-page-ready-q-barrier-fusion  (NEUTRAL / REJECTED, 2026-08-10)
- **父/control**: exp125，SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；候选SHA `414ccc67bc66407aaf2fcaa4ac841bff955744412aff69a48e2348afea07b5a8`；final build=`build/cuda_case10_initial_barrier_fusion_exp128.so`。
- **唯一假设**: case10只有4 pages/split，相比exp122的case14约15 pages/split，首页固定barrier占比约高3.75倍。保持exp125 register-lookahead、full/fused-tail、split128、raw QK、partial和reducer不变，仅在dynamic Q与static K/V不别名的前提下把首页K/V发布合入Q staging barrier，并把后续page-ready从loop顶部移到register store之后；每个producer恰少一道CTA barrier。
- **correctness**: case10同进程`1,2,15,16,17,63,64,65,127,128,129,191,192,193,8191,8192`全部100% PASS且finite，最大误差`7.8125e-03`在OJ容差内。
- **A/B/结论**: 61×500正向exp128/exp125=`0.9980/1.0028/1.0068`，反向exp125/exp128=`0.9914/0.9971/1.0037`，消偏`√(1.0028/0.9971)=1.00285`，约慢0.29%且区间跨1，归类中性/拒绝。即使缩短到4页循环，少一次固定barrier仍不可见；完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case10_initial_barrier_fusion_exp128.cpp`，工作文件恢复exp125。generic-z2首页barrier融合已在case14/10两种循环长度均关闭。

### exp129-case10-split64-register-lookahead  (REJECTED, SPLIT NEIGHBORHOOD CLOSED, 2026-08-10)
- **父/control**: exp125，SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；候选SHA `1e84ef239ba4dca8154289fe6b86574e36cd09cd1eb2800f630dfb574799dc14`；final build=`build/cuda_case10_split64_register_lookahead_exp129.so`。
- **关键新前提/唯一假设**: 旧scalar与早期token-parallel已证明3页/2页不如4页；exp125的register-lookahead显著改变producer流水，且64 partial可将128-split vec4 reducer流量减半，因此仅重开旧8页点。除了case10 `n_split 128→64`、`pages/split 4→8`外，register pipeline、full/fused-tail、raw QK、FP32 partial与reducer实现均不变。
- **correctness**: case10同进程`1,2,15,16,17,127,128,129,255,256,257,8191,8192`全部100% PASS且finite，覆盖8-pages/split模数两侧。
- **A/B/结论**: 41×500 exp129/exp125=`1.0523/1.0559/1.0608`，稳定慢约5.59%，差异远离噪声，无需反向长测。减半partial/reducer无法补偿producer CTA从512降到256造成的并行不足；完整源码归档为`solutions/archive/2026-08-10-experiments/cuda_case10_split64_register_lookahead_exp129.cpp`，工作文件恢复exp125。结合早期3页exp21慢8.3%与旧2页结果，register-lookahead新前提下仍保留128 split/4页；case10 split离散邻域关闭。

### exp130-case12-scalar-k-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED LOCALLY BY EXP131, 2026-08-10)
- **父/control**: exp125，SHA `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`；候选SHA `4115934ebfe577f829f8aff21750c20cc79b057d3f25ae00a6f6122c6c88581d`；final build=`build/cuda_case12_scalar_k_lookahead_exp130.so`，资源构建=`build/cuda_case12_scalar_k_lookahead_exp130_resource.so`。
- **关键新前提/唯一假设**: exp111已证明case12把下一页K保存在`uint4` aggregate会产生32 B stack；本次只把该live value改为四个`uint32_t`标量，并用四个scalar shared store恢复下一页K。case12仍为同步KV8 `(16,4,4)`、128 split/16 pages、raw row16 QK、wave-private page rows、K-only lookahead、V在PV后直接加载、fused tail、FP32 partial与vec4 reducer；其他shape不启用新模板参数。
- **资源**: 目标实例=`62 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`，control=`60/52/8192/0/8`。标量表示消除了exp111的spill且保持8-wave档，满足静态门槛。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。case12定点`1,2,15,16,17,255,256,257,271,272,511,512,513,32767,32768`全部100% PASS；同进程`32768→1→2→15→16→17→256→257→271→272→512→513→32768`亦全部PASS，覆盖16-pages/split模数、fused tail和workspace旧partial复用。
- **A/B**: case12 41×200正向exp130/exp125=`0.9803/0.9811/0.9817`，反向exp125/exp130=`1.0184/1.0189/1.0198`，消偏`√(0.9811/1.0189)=0.9813`，稳定快约1.87%，绝对p50约`1.0145→0.9952 ms`。非目标case7/9/13的21×100正反消偏约`1.00045/1.00030/0.99930`，均中性。
- **结论**: 当时接纳为本地candidate baseline，后由exp131取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case12_scalar_k_lookahead_exp130.cpp`。它证明KV8 lookahead失败源于aggregate表示导致的spill，而非K-over-PV数据流本身。

### exp131-case13-scalar-k-register-lookahead  (LOCALLY POSITIVE, OJ #107882 CANCELED / SUPERSEDED LOCALLY BY EXP132, 2026-08-10)
- **父/control**: exp130，SHA `4115934ebfe577f829f8aff21750c20cc79b057d3f25ae00a6f6122c6c88581d`；候选SHA `2dfd46488ce6b050859ac32328db58c347471a38112acc2e095260b6f145dfd7`；final build=`build/cuda_case13_scalar_k_lookahead_exp131.so`。
- **唯一假设**: 只把exp130已经在case12验证的零spill四标量next-K模板扩展到case13；case13继续使用B1/KV8、split256/15 pages、full-only加last-split fused tail、raw row16 QK、FP32 partial和64-thread vec2 reducer。case12保持exp130，V仍在当前PV后同步写入shared，其他shape、loader、split、QK/PV和reducer均不变；源码相对exp130只有case13这一处dispatch实例差异。
- **资源**: case13与case12调用同一组full producer模板参数，目标实例保持已验证的`62 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`，没有重现exp111的32 B stack。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部100% PASS，覆盖15-pages/split边界、fused tail、full→short→full及旧workspace复用。
- **A/B**: case13 41×200正向exp131/exp130=`0.9749/0.9769/0.9788`，反向exp130/exp131=`1.0201/1.0220/1.0236`，消偏`√(0.9769/1.0220)=0.977686`，稳定快约2.23%，绝对p50约`270.7→264.6 μs`。非目标case7/9/12的21×100正反p50分别为`0.9991/0.9990`、`0.9986/0.9992`、`0.9998/0.9999`，消偏约`1.00005/0.99970/0.99995`，均中性。
- **结论/OJ**: 当时接纳为本地candidate baseline，后由exp132取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case13_scalar_k_lookahead_exp131.cpp`。取消长期Pending的#107856并确认终态后，串行创建唯一提交#107882；它随后被外部动作取消，没有性能结果。之后观察到#107890 Pending但源码身份无raw证据；用户要求平台异常期间暂停全部提交，不取消、不补交。零spill标量K-over-PV现已在case12/13两种长KV8并发形态独立成立。

### exp132-case9-scalar-k-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED LOCALLY BY EXP133, OJ PAUSED, 2026-08-10)
- **父/control**: exp131，SHA `2dfd46488ce6b050859ac32328db58c347471a38112acc2e095260b6f145dfd7`；候选SHA `357ce23cb09d9d71fa45f6385e223b0c93269d5b20f6ca0c7bd27ba716a0a057`；final build=`build/cuda_case9_scalar_k_lookahead_exp132.so`。
- **唯一假设**: 只把零spill四标量next-K模板扩展到case9；保留B32/KV8、split24/11 pages、full-only加last-split fused tail、raw row16 QK、FP32 partial和既有small/grouped reducer。case12/13保持exp130/131，V仍在当前PV后同步写shared，其他shape、split、QK/PV和reducer不变。
- **资源**: case9复用exp130/131已经编译的同一full producer模板实例，保持`62 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`，没有新增模板资源档或stack spill。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。case9同进程`4096→1→2→15→16→17→175→176→177→191→192→351→352→353→4095→4096`全部100% PASS，覆盖11-pages/split边界、fused tail和full→short→full workspace复用。
- **A/B**: case9 41×200正向exp132/exp131=`0.9843/0.9854/0.9861`，反向exp131/exp132=`1.0124/1.0133/1.0137`，消偏`√(0.9854/1.0133)=0.986137`，稳定快约1.39%，绝对p50约`529→522 μs`。非目标case7/12/13的21×100正反p50分别为`0.9994/0.9990`、`0.9994/1.0001`、`0.9983/1.0000`，消偏约`1.00020/0.99965/0.99915`，均在噪声内。
- **结论**: 当时接纳为本地candidate baseline，后由exp133取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case9_scalar_k_lookahead_exp132.cpp`。零spill标量K-over-PV已在case12/13/9三种并发形态连续成立。

### exp133-case7-scalar-k-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED LOCALLY BY EXP134, OJ PAUSED, 2026-08-10)
- **父/control**: exp132，SHA `357ce23cb09d9d71fa45f6385e223b0c93269d5b20f6ca0c7bd27ba716a0a057`；候选SHA `9f611f4dd92b0d73d173b9fbb08c580ab5c5c85efc54acf679694102a44bd754`；final build=`build/cuda_case7_scalar_k_lookahead_exp133.so`。
- **唯一假设**: 只把零spill四标量next-K模板扩展到最后一个长KV8 shape case7；保留B64/KV8、split14/10 pages、full-only加last-split fused tail、raw row16 QK、FP32 partial和既有group8 reducer。case9/12/13保持exp132/130/131，V仍在当前PV后同步写shared，其他shape、split、QK/PV和reducer不变。
- **资源**: case7复用exp130–132已经编译的同一full producer模板实例，保持`62 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`，没有新增模板资源档或stack spill。
- **correctness**: CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。case7同进程`2048→1→2→15→16→17→159→160→161→175→176→319→320→321→2047→2048`全部100% PASS，覆盖10-pages/split边界、fused tail和full→short→full workspace复用。
- **A/B**: case7 41×200正向exp133/exp132=`0.9847/0.9852/0.9858`，反向exp132/exp133=`1.0135/1.0142/1.0146`，消偏`√(0.9852/1.0142)=0.985599`，稳定快约1.44%，绝对p50约`535→527 μs`。非目标case9/12/13的21×100正反p50分别为`0.9997/1.0004`、`0.9994/1.0003`、`0.9985/0.9982`，消偏约`0.99965/0.99955/1.00015`，均在噪声内。
- **结论/OJ**: 当时接纳为本地candidate baseline，后由exp134取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case7_scalar_k_lookahead_exp133.cpp`。零spill标量K-over-PV在case7/9/12/13四个长KV8 shape全部独立正向，逐shape扩展闭合。OJ平台再次异常且用户明确暂停全部OJ操作；不对已观察到的#107890执行提交、查询、监控、取消或补交，继续本地探索下一结构方向。

### exp134-case13-scalar-kv-register-lookahead  (LOCALLY POSITIVE, SUPERSEDED BY EXP135/#108312, OJ #108257/#108278 COMPILE TLE, 2026-08-10)
- **父/control**: exp133，SHA `9f611f4dd92b0d73d173b9fbb08c580ab5c5c85efc54acf679694102a44bd754`；候选SHA `b3ba2b89f707ee960f5df1198e32eefa133a6bd920b951a7728f693ce7c4a045`；correctness/A-B build=`build/cuda_case13_scalar_kv_lookahead_exp134_resource.so`。
- **唯一假设**: 只给case13的同步KV8 full producer在既有四标量next-K外增加四标量next-V，使下一页K/V都跨当前页PV保存在寄存器；PV后执行一次wave barrier，再把K/V一起发布到原8 KiB shared。case13仍保持split256/15 pages、full-only加last-split fused tail、raw row16 QK、FP32 partial与64-thread vec2 reducer；case7/9/12继续使用K-only模板，其他loader、split、QK/PV、tail和reducer不变。
- **资源**: case13目标实例从exp133 K-only的`62 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`变为`64/52/8192/0/8`；仅增加2个MTreg，未spill、未降低驻留档。
- **correctness**: CPU14/14；同一resource `.so`的GPU full/boundary/random seed20260810各14/14且finite。case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部100% PASS，覆盖15-pages/split边界、fused tail、full→short→full及旧workspace复用。
- **A/B**: case13 41×200正向exp134/exp133=`0.9747/0.9763/0.9782`，反向exp133/exp134=`1.0214/1.0225/1.0241`，消偏`√(0.9763/1.0225)=0.9772`，稳定快约2.28%，正向绝对p50约`263.0→256.8 μs`。非目标case7/9/12的21×100正反p50分别为`0.9999/0.9998`、`1.0005/0.9991`、`1.0003/0.9999`，消偏约`1.00005/1.00070/1.00020`，均在噪声内。
- **结论/OJ**: 当时接纳为本地candidate baseline，后由exp135/#108312取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case13_scalar_kv_lookahead_exp134.cpp`。case13的零spillV-over-PV在K-only主链上继续给出独立收益，但该结论尚未授权case7/9/12。#108257/#108278 两次相同SHA提交均在OJ编译阶段触发`TimeLimitExceeded`，没有测试点和性能数据；这不是运行源码反证，而是exp135裁剪编译表面的直接动机。

### exp135-compile-surface-prune  (CONFIRMED, FIRST 59.86 MILESTONE #108312, 2026-08-10)
- **父/control**: exp134，SHA `b3ba2b89f707ee960f5df1198e32eefa133a6bd920b951a7728f693ce7c4a045`；候选SHA `234af15ed3f75fb939e3a2392ba4d377b4644a8595887a9e948a822ce88c12a9`；final build=`build/cuda_compile_surface_prune_exp135.so`。
- **唯一假设**: 生产dispatch自MMA-QK精度失败后始终`use_mma_qk=false`，但源码仍解析CUTE/MCTLASS/WMMA头文件与未launch probe。只把这些不可达依赖从编译表面排除，并用`XPUOJ_ENABLE_OPTIMIZED_MACA=1`与`XPUOJ_USE_BASE2=1`显式保持既有token-parallel选择和BASE2 reducer；所有14-case kernel模板参数、split、loader、QK/PV、tail、workspace和reducer运行逻辑不变。
- **编译/correctness**: 同机完整构建exp134=`10.08 s`、exp135=`8.17 s`，约快18.9%，CUTE巨量warning消失。CPU14/14；同一final `.so`的GPU full/boundary/random seed20260810各14/14且finite。
- **A/B**: case7–14的21×100 candidate/control p50依次为`1.0001/0.9992/0.9997/1.0010/0.9997/0.9997/0.9992/1.0007`；短case1–6均在计时噪声内。case4 61×1000正反p50=`0.9938/1.0042`，消偏约`0.9948`，未见运行回退。
- **OJ/结论**: 串行提交#108312成功跨过Compiling并14/14 Accepted，分数`59.86`；case1–14=`3/4/10/29/22/32/289/139/289/55/347/486/256/259 μs`。它将exp68–134积累的本地收益首次完整落到OJ，相对#106626总分提高`2.22`，并作为baseline服务到#108468；完整实验源码与逐提交源码分别为`solutions/archive/2026-08-10-experiments/cuda_compile_surface_prune_exp135.cpp`和`solutions/archive/2026-08-10-submissions/cuda_108312.cpp`。后续提交不得重新引入已关闭MMA probe，且始终保持至多一个OJ任务在途。

### exp136-case12-scalar-kv-register-lookahead  (POSITIVE, OJ #108371/#108398 CANCELED, INCLUDED IN #108468, 2026-08-10)
- **父/control**: #108312/exp135，SHA `234af15ed3f75fb939e3a2392ba4d377b4644a8595887a9e948a822ce88c12a9`；候选SHA `4df13ff63446190b7dec7482cf2479fd05e83956a5897f58b95bd1f1994382c5`；final build=`build/cuda_case12_scalar_kv_lookahead_exp136.so`。
- **唯一假设**: 只给case12在既有四标量next-K外打开exp134已验证的四标量next-V，使下一页K/V都跨当前PV保存在寄存器；case7/9仍K-only、case13保持K+V，case12的split128/16 pages、fused tail、raw QK、FP32 partial和vec4 reducer全部不变，不新增模板实例。
- **correctness/A-B**: CPU14/14；同一`.so`的GPU full/boundary/random各14/14且finite，case12同进程16步full→short→full定点序列全部PASS。41×200正向exp136/#108312=`0.9865/0.9880/0.9890`，反向#108312/exp136=`1.0105/1.0117/1.0125`，消偏约`0.9884`，稳定快约1.16%、绝对约`995→983 μs`；case7/9/13双向均中性。
- **OJ/结论**: 完整源码为`solutions/archive/2026-08-10-experiments/cuda_case12_scalar_kv_lookahead_exp136.cpp`。同SHA的#108371/#108398均在故障期长期Pending后取消，没有测试点；raw与逐提交快照已归档且哈希一致。该改动随后经exp137/138组合，并由#108468的case12 `486→479 μs`完成OJ确认。

### exp137-case9-scalar-kv-register-lookahead  (POSITIVE, SUPERSEDED BY EXP138/#108468, 2026-08-10)
- **父/control**: exp136，SHA `4df13ff63446190b7dec7482cf2479fd05e83956a5897f58b95bd1f1994382c5`；候选SHA `6bec5e024eee31ef981d14d4efb5ec8ce8a6e6cf9a11122dc0363d922de9be0e`；final build=`build/cuda_case9_scalar_kv_lookahead_exp137.so`。
- **唯一假设**: 只把K+V四标量lookahead扩展到case9；case7仍K-only，case12/13保持K+V，split24/11 pages、fused tail、raw QK、partial/reducer均不变并复用既有`64 MTreg/52 STreg/8192 B/0 stack/8 warps`模板。
- **correctness/A-B**: CPU14/14；GPU full/boundary/random各14/14，case9 16步精确长度序列全部PASS。41×200正向exp137/exp136=`0.9836/0.9842/0.9849`，反向exp136/exp137=`1.0144/1.0148/1.0153`，消偏约`0.9847`，稳定快约1.53%；case7/12/13双向中性。
- **结论**: 接纳后由exp138取代；完整源码为`solutions/archive/2026-08-10-experiments/cuda_case9_scalar_kv_lookahead_exp137.cpp`。

### exp138-case7-scalar-kv-register-lookahead  (CONFIRMED, CURRENT OJ BASELINE #108468 / 59.86, 2026-08-10)
- **父/control**: exp137，SHA `6bec5e024eee31ef981d14d4efb5ec8ce8a6e6cf9a11122dc0363d922de9be0e`；候选SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；final build=`build/cuda_case7_scalar_kv_lookahead_exp138.so`。
- **唯一假设**: 只把K+V四标量lookahead扩展到最后一个长KV8 shape case7；case9/12/13保持各自K+V，split14/10 pages、fused tail、raw QK、group8 reducer和全部非目标路径不变。K-only模板不再被四个长KV8 shape使用，运行模板资源仍为`64/52/8192/0/8`。
- **correctness/A-B**: CPU14/14；GPU full/boundary/random各14/14且finite，case7 16步精确长度序列全部PASS。41×200正向exp138/exp137=`0.9844/0.9849/0.9865`，反向exp137/exp138=`1.0135/1.0145/1.0155`，消偏约`0.9853`，稳定快约1.47%；case9/12/13双向中性。
- **OJ/结论**: #108468排队约30分钟后14/14 Accepted，分数`59.86`；case1–14=`3/4/10/29/22/32/285/140/285/55/348/479/255/259 μs`。相对#108312，四个目标长KV8 case7/9/12/13改善`4/4/7/1 μs`，case8/11各有`+1 μs`非目标波动，其余持平。目标OJ变化与逐shape本地A/B同向，因此四个长KV8 K+V-over-PV扩展闭合，并选#108468为新baseline。完整实验源码为`solutions/archive/2026-08-10-experiments/cuda_case7_scalar_kv_lookahead_exp138.cpp`；工作文件、实验快照与`solutions/archive/2026-08-10-submissions/cuda_108468.cpp`字节一致。

### exp139-case11-z-pair-partial-offload  (CORRECT, REJECTED, 2026-08-10)
- **父/control**: exp138，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `00299b7076ff3f38f89b884394f03549ad7834102779bc2b90478e060344e520`；resource build=`build/cuda_case11_pairwise_partial_exp139.so`。
- **唯一假设**: 只改case11 z4状态合并：z0/z1完成第一次pair merge后各写一个partial，使每producer owner从1个partial变成2个（48→96），删除第二级shared state写读和两次CTA barrier；final vec4 reducer按96个连续live partial合并。page pipeline、split48、K/V lookahead、QK/PV和数学不变。
- **资源/correctness**: producer从control的`94 MTreg/54 STreg/8320 B/5 warps`降至`92/50/8320/5`，0 stack；新96-partial vec4 reducer为`62/52/0/8`。CPU14/14，case11的19步full→short→full精确长度全部100% PASS且finite。
- **A/B/结论**: 正向exp139/exp138=`1.0077/1.0086/1.0094`，反向exp138/exp139=`0.9905/0.9919/0.9930`，消偏约`1.0084`，稳定慢约0.84%。额外global partial与更长final reducer超过两次barrier/第二级shared merge的节省；拒绝且不扩展到case8。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case11_pairwise_partial_exp139.cpp`，工作文件已恢复exp138。

### exp140-case11-scalar-kv-register-lookahead  (CORRECT, REJECTED, 2026-08-10)
- **父/control**: exp138，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `3a8383adebdff9ca66f520c4da5642ab9a8af7c246c92d3268e6da6216720701`；resource build=`build/cuda_case11_scalar_kv_lookahead_exp140.so`。
- **唯一假设**: 只把case11 register-lookahead中跨PV保存的next-K/next-V各一个`uint4`改为八个独立`uint32_t`标量，并以四次标量global load/shared store替代每组向量操作；head-pair/z4、early page ID、单overwrite barrier、split48、fused tail、QK/PV、partial与reducer全部保持exp138。目标是复制KV8 exp130的“标量表示消除aggregate spill/暴露调度”机制，但case11 control本来已经0 stack，因此该实验只检验后端调度与寄存器档位。
- **资源/correctness**: case11 full producer从control的`94 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`降为`90/54/8320/0/5`，没有跨occupancy档。CPU语义与真实C500 full correctness通过，输出100%在容差内且finite。
- **A/B/结论**: 正向exp140/exp138 p10/p50/p90=`1.0053/1.0063/1.0076`；反向exp138/exp140=`0.9938/0.9944/0.9948`，原始candidate/control消偏`sqrt(1.0063/0.9944)≈1.0060`，稳定慢约0.60%。在既有0-stack head-pair路径中，四标量load/store增加的指令与调度成本超过4个MTreg下降，`uint4`聚合表示更优；拒绝，不以同一标量化继续扫描case8/14，工作文件恢复exp138。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case11_scalar_kv_lookahead_exp140.cpp`。

### exp141-case14-two-wave-zgroup-mbarrier-probe  (CAPABILITY CORRECT, PERFORMANCE REJECTED, 2026-08-10)
- **假设/范围**: case14 generic `(16,8,2)` 中每个z由两条64-lane wave共享8个token row，但现有page-ready/overwrite使用CTA-wide barrier并连带等待另一个独立z。官方指南确认`barrier_ex`只能同步整个block、`barrier_and_wait*`只配合BSM use-def；本机3.7.1另有shared `__mbarrier_*`软件原语。因此先做隔离probe，不修改solution：每个z用expected-count=2的reusable mbarrier，由两条wave leader到达/等待，并以wave barrier包围；对照为同一256-thread CTA的两次`__syncthreads()`。
- **实现/语义**: `tests/archive/closed-backend-probes/c500_zgroup_barrier_probe.cpp` SHA `2549702f8475d645e435f59005a6249b88f8efc0253dd8df2ac15feb0665317f`，驱动 `tests/archive/closed-backend-probes/c500_zgroup_barrier_probe.py` SHA `2ae622117053ef3858a55f487e4b704ac459d0ff1f3c9eeea1a0e8be9f6cef57`。本机`mc_awbarrier_primitives.h`会与自身helper重复定义，probe直接包含`mc_awbarrier_helpers.h`的同一公开接口。4 blocks×8 iterations与64 blocks×128 iterations中，CTA和z-group都逐元素exact PASS，证明两-wave共享交换语义成立。
- **性能/结论**: 小样本zgroup/CTA p50=`1.3370`；强复测64 blocks×128 iterations p10/p50/p90=`2.7754/3.6993/4.7664`，软件mbarrier慢约`3.70x`。头文件实现使用shared `atomicAdd_block`、threadfence和spin，并非低成本硬件named barrier；热循环成本远超消除z0/z1无关互等的上界。拒绝，不形成solution候选、不改工作文件，也不在case14中集成或微调该mbarrier。只有编译器/硬件新增真正的128-thread named barrier时才重开。

### exp142-case14-register-z0-state  (CORRECT, NEUTRAL/REJECTED, 2026-08-10)
- **父/control**: #108468/exp138，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `c00494568735e2d73a6ae7146b3827a2eae5f3f701a36efb3705d4a721bd5e8b`；final/resource build=`build/cuda_case14_register_z0_exp142.so`/`build/cuda_case14_register_z0_exp142_resource.so`。
- **唯一假设**: case14 generic `(16,8,2)` 原先把z0/z1两份accumulator都写入复用后的K/V shared，再由z0读回合并。只让`BF16_NORMALIZED_PARTIAL && REGISTER_KV_LOOKAHEAD`这一case14唯一组合复用KV8已有的`REGISTER_Z0`路径：z0保留寄存器、只物化z1，并把m/l metadata放进空闲z0 rows；loader、split257、fused tail、QK/PV、CTA barrier、partial ABI与final reducer均不变。
- **资源/correctness**: case14 producer从control的`78 MTreg/56 STreg/8320 B/0 stack/6 warps`变为`78/58/8192/0/6`；shared减少128 B但STreg增加2，未跨occupancy档。真实C500 full correctness 100% PASS，max error=`1.220703e-04`、max tolerance ratio=`0.008`、finite。
- **A/B/结论**: 41×200正向exp142/#108468 p10/p50/p90=`0.9983/1.0005/1.0031`；反向#108468/exp142=`0.9954/0.9969/0.9987`，原始candidate/control消偏`√(1.0005/0.9969)≈1.0018`，约慢0.18%。页循环后的一次z0 shared写读太小，不足以覆盖更长live range和`+2 STreg`；拒绝、不提交，不以同一REGISTER_Z0机制扩展或叠加split/reducer补偿。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case14_register_z0_exp142.cpp`，工作文件恢复#108468。

### exp143-case8-pair2-vec4-reducer  (CORRECT, NEUTRAL/REJECTED, 2026-08-10)
- **父/control**: #108468/exp138，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `b5fe8d7d29a4c99047b9ef217886915a98ce76c47e4582e99a5ad8c34df7ece1`；resource build=`build/cuda_case8_pair2_vec4_reducer_exp143_resource.so`。
- **唯一假设**: case8现有32-thread vec4 reducer每CTA只占C500半个64-lane wave。仅把两个彼此独立的query-head reducer装入一个64-thread CTA，使reducer grid从`B×32=512`减为`B×16=256`；producer、48 partial ABI、每head数学、global读写和vec4 ownership均不变，两个head之间不共享softmax状态。
- **资源/correctness**: 新pair2 reducer为`70 MTreg/28 STreg/0 stack/staticMaxWarps=7`，原one-head reducer为`64/35/0/8`。真实C500 case8 full correctness通过且finite。
- **A/B/结论**: 正向exp143/#108468 p50=`0.9985`，反向#108468/exp143 p50=`0.9998`；双顺序消偏candidate/control约`0.99935`，仅快约0.07%且区间跨1，判为测量中性。减少256个短reducer CTA没有产生可见端到端收益，拒绝、不提交，也不把同一pair2封装扩展到case11。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case8_pair2_vec4_reducer_exp143.cpp`，工作文件已恢复#108468。

### exp144-case4-register-z0-state  (CORRECT, REJECTED, 2026-08-10)
- **父/control**: #108468/exp138，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `330caba578869aba1c70eabe8692106e826ad562a21a7ee91d9117712012f372`；resource build=`build/cuda_case4_register_z0_exp144_resource.so`。
- **唯一假设**: case4是当前唯一`KV8 + BSM + raw-row16 + combined/direct-out`实例，只有四页且没有final reducer；仅让该模板复用branchless KV8已有的`REGISTER_Z0`合并，令z0 accumulator保留在寄存器并把m/l metadata放入空闲shared rows。loader、QK/PV、四页循环、softmax和direct-out全部不变。
- **资源/correctness**: producer从control的`76 MTreg/46 STreg/8320 B/0 stack/6 warps`变为`76/46/8192/0/6`，只少128 B shared，未跨资源档。真实C500 case4 full correctness通过，max error=`7.8125e-03`、max tolerance ratio=`0.224`且finite。
- **A/B/结论**: 61×1000正向exp144/#108468 p10/p50/p90=`1.0128/1.0139/1.0152`；反向#108468/exp144=`0.9819/0.9833/0.9845`，双顺序消偏candidate/control约`1.0154`，稳定慢约1.54%。短combined路径的z0 shared写读不是瓶颈，寄存器live-range/codegen代价反而明显；拒绝、不提交。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case4_register_z0_exp144.cpp`，工作文件已恢复并逐字节匹配#108468。

### exp145-case4-kv8-headpair-bsm  (CORRECTNESS REJECTED, 2026-08-10)
- **父/control**: #108468/exp138，候选SHA `957aa06800eece598283f33c5afe20427c8fd2ce5b3864d56bf2d07a60b1b1b4`；resource build=`build/cuda_case4_kv8_headpair_exp145_resource.so`。
- **唯一架构假设**: 只针对case4的四页、单split、KV8/GQA4 direct-out路径，把CTA从`dim3(16,4,4)`改为`dim3(16,2,4)`；每线程计算两个query head、每个`(ty,tz)`发两行K/V load，使整页流量不变而一次K/V解包服务两个head。它不同于已关闭的长KV4 head-pair前提。
- **资源/correctness**: 新producer为`86 MTreg/46 STreg/8320 B/0 stack/staticMaxWarps=5`，control为`76/46/8320/0/6`。真实C500 full仅`match=0.002537`且大范围NaN。
- **结论**: exp146只把同一线程每buffer的两条BSM load改为同步`uint4`即100%正确，定位失败前提为当前BSM路径不能安全支持该双发模式；禁止提交。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case4_kv8_headpair_bsm_exp145.cpp`。

### exp146-case4-kv8-headpair-sync  (CORRECT, PERFORMANCE REJECTED, 2026-08-10)
- **父/control**: exp145架构/#108468；候选SHA `aa120f07f147f9bc80f4cef88a10b7c7ce9a9090250f7acd26d93ab517cc957a`；build=`build/cuda_case4_kv8_headpair_sync_exp146.so`。
- **唯一差异/correctness**: 保持exp145的双-head ownership、QK/PV和reducer，仅改同步`uint4` loader。CPU14/14；C500 case4 full 100% PASS，max error=`7.8125e-03`、max tolerance ratio=`0.224`且finite，证明数学、head映射和reducer正确。
- **A/B/结论**: 31×1000正向p10/p50/p90=`1.1126/1.1323/1.1532`，反向baseline/exp146=`0.8770/0.8785/0.8820`，双顺序消偏exp146/baseline约`1.1353`，稳定慢13.5%。同步双行loader、双head live state与`staticMaxWarps 6→5`超过解包复用收益；关闭该exact KV8 `(16,2,4)`布局，不以state/reducer微调补偿。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case4_kv8_headpair_sync_exp146.cpp`，工作文件恢复#108468。

### exp147-case10-vec2-reduce128  (CONFIRMED, CURRENT OJ BASELINE #108604 / 60.00, 2026-08-10)
- **父/control**: #108468，SHA `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；候选SHA `7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`；build=`build/cuda_case10_vec2_reduce_exp147_resource.so`。
- **唯一假设**: case10只有B1×32个one-head reducer CTA，exp87的32-thread vec4每CTA只填半条C500 wave。保持CTA数32、producer、split128、FP32 partial、full-page owner live-count和数学不变，只改为64-thread完整wave、每线程连续2维的既有vec2 reducer；不同于exp86/143的跨head CTA packing。
- **资源/correctness**: vec2为`38 MTreg/39 STreg/0 static shared/8 warps`，vec4为`64/35/0/8`。CPU14/14；同一`.so` full/boundary/random各14/14，case10 full及19个精确长度`1,2,15,16,17,63,64,65,127,128,129,191,192,193,255,256,257,8191,8192`全部100% PASS且finite。
- **A/B**: 41×500正向exp147/#108468 p10/p50/p90=`0.9662/0.9781/0.9859`，反向#108468/exp147=`1.0137/1.0271/1.0391`，双顺序消偏exp147/control约`0.9759`，快约2.4%或1.3–1.5 μs。case4/5/14消偏约`1.0022/0.9986/1.0002`，均中性。
- **OJ/决定**: #108604 为14/14 Accepted / `60.00`；case1–14=`3/4/10/29/22/32/285/140/287/54/347/477/255/257 μs`。case10相对#108468从`55→54 μs`、得分`53→54`，真实跨过目标tier；其他约1–2 μs变化无对应dispatch，视为OJ波动。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case10_vec2_reduce_exp147.cpp`，逐提交快照为`solutions/archive/2026-08-10-submissions/cuda_108604.cpp`，两者SHA一致；#108604取代#108468成为control。

### exp148-case6-full-only-fused-tail  (CORRECT, PERFORMANCE REJECTED, 2026-08-10)
- **父/control**: #108604/exp147，SHA `7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`；候选SHA `837cbad3295d572c461be91150f4c94d699666f912df3e4e5d9d2e71593a1e1d`；resource build=`build/cuda_case6_full_fused_tail_exp148_resource.so`。
- **唯一假设**: case6 B16/L362/KV8有22个full page加10-token tail；保持split8、3 pages/split、同步loader、raw-row16 QK、partial ABI与group8 reducer，只把combined producer改为branchless full-only并让最后full-page owner吸收tail，不增加launch、partial或critical-split长度。
- **资源/correctness**: producer从control combined的`76 MTreg/46 STreg/8320 B/staticMaxWarps=6`变为`60/52/8192/8`，均0 stack。CPU14/14、case6 full PASS；同进程28个长度`1,2,15,16,17,47,48,49,95,96,97,143,144,145,191,192,193,239,240,241,287,288,289,335,336,337,361,362`全部100% PASS，覆盖3-pages/split模数两侧和零full-page情形。
- **A/B/结论**: 41×1000正向exp148/#108604 p10/p50/p90=`1.0166/1.0221/1.0248`；反向#108604/exp148=`0.9669/0.9731/0.9858`，折算双顺序消偏exp148/control约`1.0249`，稳定慢约2.49%。资源档改善不能补偿full-only实例控制流/代码生成代价；拒绝、不提交，关闭case6的同一fused-tail迁移。完整源码为`solutions/archive/2026-08-10-experiments/cuda_case6_full_fused_tail_exp148.cpp`；工作文件已恢复并逐字节匹配#108604。

### exp149-case12-vec2-reduce128  (CONFIRMED, CURRENT OJ BASELINE #108628 / 60.00, 2026-08-10)
- **父/control**: #108604/exp147，SHA `7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`；候选SHA `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d`；fresh control/candidate build=`build/cuda_108604_control_fresh.so`/`build/cuda_case12_vec2_reduce_exp149.so`。
- **唯一假设**: case12与case10同为128个FP32 partial和one-head vec4 reducer；只把case12从32-thread半wave vec4切为64-thread完整wave vec2，保持256个reducer CTA、producer、split128、fused-tail owner计数、workspace和数学不变。exp91只验证过scalar→vec4，exp147只验证过B1 case10，因此B8 case12是未覆盖的新CTA填充前提。
- **资源/correctness**: vec2复用已验证的`38 MTreg/39 STreg/0 static shared/staticMaxWarps=8`模板，vec4为`64/35/0/8`。CPU14/14；同一candidate `.so`的GPU full/boundary/random各14/14且finite。case12同进程精确长度`1,2,15,16,17,255,256,257,511,512,513,4095,4096,4097,32767,32768`全部100% PASS，覆盖16-pages/split模数、tail-only、full→short→full与旧workspace复用。
- **A/B/OJ决定**: 初轮41×200正向exp149/#108604=`0.9978/0.9985/0.9997`，反向#108604/exp149=`0.9993/1.0014/1.0022`，消偏约`0.99855`。强复测61×500正向=`0.9977/0.9987/1.0002`，反向=`1.0001/1.0009/1.0014`，消偏`√(0.9987/1.0009)≈0.99890`，稳定快约0.11%（约0.5 μs）；非目标case10/13 p50=`1.0004/0.9996`中性。#108628为14/14 Accepted / `60.00`，case1–14=`3/4/10/29/22/32/285/139/285/54/348/476/256/257 μs`；唯一目标case12相对#108604 `477→476 μs`，但得分仍54。完整实验源码为`solutions/archive/2026-08-10-experiments/cuda_case12_vec2_reduce_exp149.cpp`，逐提交源码为`solutions/archive/2026-08-11-submissions/cuda_108628.cpp`；因目标OJ变化与A/B一致，#108628取代#108604成为control。

### exp150-case8-vec2-reduce48  (CORRECT, NEUTRAL/REJECTED, 2026-08-11)
- **父/control**: #108628/exp149，SHA `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d`；候选SHA `088982697af6e6a33b45ce5bd7376d28745db64a9eaf498a2cdfd04216e0985b`；build=`build/cuda_case8_vec2_reduce_exp150.so`。
- **唯一假设**: 保持case8的512个one-head CTA、48 fused-tail partial、producer/workspace和数学不变，只把32-thread vec4半wave切为64-thread vec2完整wave。它不同于exp143的双head packing：exp143把CTA数`512→256`，本次CTA数不变。
- **correctness/A-B/结论**: CPU14/14，真实C500 case8 full 100% PASS且finite。41×500正向exp150/#108628 p10/p50/p90=`0.9974/1.0005/1.0024`；反向#108628/exp150=`0.9981/0.9993/1.0006`，消偏exp150/control约`1.0006`，完全中性。512 CTA已足以隐藏half-wave ownership，完整wave没有复现B1/B8较低CTA形状的收益；拒绝、不提交，不向同为B16/48 partial的case11继续推广。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case8_vec2_reduce_exp150.cpp`，工作文件恢复#108628。

### exp151-case11-prescale-q  (LOCALLY POSITIVE, OJ #108651 ACCEPTED/59.93, 2026-08-11)
- **父/control**: #108628/exp149，SHA `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d`；候选SHA `89b0934451ef46065afab359a6e6fc316023a5bac8b6e6a1adbbb5693cc02d02`；build=`build/cuda_case11_prescale_q_exp151.so`。
- **唯一假设**: 只给case11的`paged_decode_case11_headpair_z4_kernel`增加`PRESCALE_Q`模板参数；每个split把两行Q各乘一次`sm_scale`，随后full/tail每个token的score不再重复执行`dot * sm_scale`。loader、split48、head-pair/z4 ownership、softmax/PV、partial ABI和reducer全部不变。
- **资源/correctness**: 目标producer保持`94 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`。CPU14/14；GPU full/boundary/random各14/14且finite；case11同进程`12251→1→2→15→16→17→255→256→257→511→512→513→767→768→769→12250→12251`等19步full→short→full序列全部100% PASS。
- **A/B/OJ决定**: 61×500正向exp151/#108628=`0.9948/0.9959/0.9969`，反向#108628/exp151=`1.0038/1.0048/1.0053`，消偏约`0.99556`，快约0.44%或2.6 μs。#108651为14/14 Accepted / `59.93`，case1–14=`3/4/10/29/22/32/286/139/288/53/345/477/255/259 μs`；唯一目标case11相对#108628 `348→345 μs`同向改善，但非目标tier波动令总分低于60.00，故#108628仍为control。raw、逐提交快照与完整实验源码三者SHA一致；实验源码为`solutions/archive/2026-08-11-experiments/cuda_case11_prescale_q_exp151.cpp`。

### exp152-case8-prescale-q  (LOCALLY POSITIVE, NOT SUBMITTED ALONE, 2026-08-11)
- **父/control**: exp151，SHA `89b0934451ef46065afab359a6e6fc316023a5bac8b6e6a1adbbb5693cc02d02`；候选SHA `6cd44cd9015d58a2fed4e23ae97cecb8839e23dcd6cf24fcd09a0a5d602ea19a`；build=`build/cuda_case8_prescale_q_exp152.so`。
- **唯一假设**: 只把同一head-pair/z4 `PRESCALE_Q`特化扩展到case8；case11保持exp151，case8的loader、split48、QK/PV、partial和reducer不变。
- **correctness/A-B**: GPU full/boundary/random各14/14；case8同进程`4096→1→2→15→16→17→95→96→97→111→112→191→192→193→4095→4096`全部PASS。61×500正向exp152/exp151=`0.9897/0.9932/0.9991`，反向exp151/exp152=`1.0062/1.0073/1.0093`，消偏约`0.99298`，稳定快约0.70%或1.6 μs。
- **结论**: 接纳为可提交的本地组合候选，完整源码为`solutions/archive/2026-08-11-experiments/cuda_case8_prescale_q_exp152.cpp`。当前没有在途任务，但先完成exp153组合与文档闭环，再按单任务约束决定下一次OJ验证。

### exp153-case14-prescale-q  (CONFIRMED, CURRENT OJ BASELINE #108658 / 60.07, 2026-08-11)
- **父/control**: exp152，SHA `6cd44cd9015d58a2fed4e23ae97cecb8839e23dcd6cf24fcd09a0a5d602ea19a`；候选SHA `cd76faa57c5b3a52ad9c7974b346c52f1dd16e8026a1d2177ee10f0c8ba61a5a`；fresh build=`build/cuda_case14_prescale_q_exp153.so`。
- **唯一假设**: 给generic `paged_decode_token_parallel_kernel`增加`PRESCALE_Q`，只在case14启用；每split把`q_reg[8]`预乘`sm_scale`，并从full、masked和fused-tail QK score中移除逐token缩放。case8/11保持exp152/151，其余dispatch、loader、split257、QK ownership、softmax/PV、normalized-BF16 partial和reducer不变。
- **资源/correctness**: case14从exp152的`78 MTreg/56 STreg`变为`78/54`，shared 8320 B、0 stack和6 static warps不变。CPU14/14；同一fresh `.so`的GPU full/boundary/random各14/14且finite；case14同进程`61519→1→8→9→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS，覆盖tail-only、15-pages/split边界与full→short→full复用。
- **A/B/OJ决定**: 初筛41×300正向/反向p50=`0.9959/1.0027`；强复测61×500正向exp153/exp152=`0.9891/0.9957/1.0020`，反向exp152/exp153=`0.9473/1.0028/1.0219`，按p50消偏约`sqrt(0.9957/1.0028)=0.99645`，快约0.36%或0.9 μs。#108658为14/14 Accepted / `60.07`，case1–14=`3/4/10/29/22/32/283/139/285/54/343/476/255/257 μs`；case11相对#108628 `348→343 μs`、得分`41→42`，case8/14保持`139/257 μs`。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case14_prescale_q_exp153.cpp`，逐提交源码为`solutions/archive/2026-08-11-submissions/cuda_108658.cpp`，两者与raw SHA一致；#108658取代#108628成为control。

### 64-bit shuffle静态结论  (NO SOLUTION CANDIDATE, 2026-08-11)
- MACA CUDA compatibility headers会把64-bit整数或double shuffle拆成两次32-bit `__shfl_xor_sync`；底层BSM bpermute同样是32-bit数据宽度。因此把两个FP32 dot打包成64 bit不能把QK交换次数减半，只会保留两次底层交换并增加打包/解包。除非编译器或硬件文档出现新的原生64-bit交换证据，不以此方向建立runtime候选。

### exp154-case10-prescale-q  (LOCALLY POSITIVE, NEXT LOCAL CANDIDATE, 2026-08-11)
- **父/control**: exp153，SHA `cd76faa57c5b3a52ad9c7974b346c52f1dd16e8026a1d2177ee10f0c8ba61a5a`；候选SHA `f77ccca3b61b0e37b321f14a899f951045ab94542e9c120ad153293ea81d88ef`；build=`build/cuda_case10_prescale_q_exp154.so`。
- **唯一假设**: 只把generic `PRESCALE_Q`扩展到case10，保持case10的split128/4 pages、full-only+last-split fused tail、同步K/V register-lookahead、raw row16 QK、FP32 partial、corrected live-owner计数和64-thread vec2 reducer不变。每split对8个Q分量预缩放一次，替代最多约64个token score的重复缩放。
- **correctness**: GPU full/boundary/random各14/14且finite；case10同进程`8192→1→2→15→16→17→63→64→65→127→128→129→191→192→193→255→256→257→8191→8192`全部100% PASS，覆盖tail-only、4-pages/split边界和full→short→full workspace复用。
- **A/B/结论**: 初轮41×300正向/反向p50=`0.9983/1.0003`；强复测61×500正向exp154/exp153=`0.9918/0.9988/1.0063`，反向exp153/exp154=`0.9984/1.0076/1.0170`，按p50消偏约`sqrt(0.9988/1.0076)=0.99562`，快约0.44%或0.25 μs。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case10_prescale_q_exp154.cpp`；#108658确认exp153成为新control后，该增量继续保留在后续exp156本地candidate中。

### exp155-case5-prescale-q  (CORRECT, NEUTRAL/REJECTED, 2026-08-11)
- **父/control**: exp154，SHA `f77ccca3b61b0e37b321f14a899f951045ab94542e9c120ad153293ea81d88ef`；候选SHA `25d6ad4a34e0b5e231700ea8e1fccb21fc586ae65ba2c23a5e2efb51e4b2deb2`；build=`build/cuda_case5_prescale_q_exp155.so`。
- **唯一假设**: 只把Q预缩放扩到case5，保持split5、约2 pages/split、combined producer、raw row16 QK、FP32 partial和reducer不变，用它判定较短split能否摊薄每split 8次Q乘法。
- **correctness/A-B/结论**: case5 full 100% PASS且finite。41×1000正向exp155/exp154=`0.9861/0.9976/1.0087`，反向exp154/exp155=`0.9946/0.9982/1.0023`，消偏约`0.99970`，仅快约0.03%且区间跨1，判为中性。两页/split不足以稳定摊薄预缩放开销；拒绝、不提交，不在同一case5布局继续微调。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case5_prescale_q_exp155.cpp`，工作文件已恢复exp154。

### exp156-case4-prescale-q  (CONFIRMED, CURRENT OJ BASELINE #108679 / 60.07, 2026-08-11)
- **父/control**: exp154，SHA `f77ccca3b61b0e37b321f14a899f951045ab94542e9c120ad153293ea81d88ef`；候选SHA `27abd5e20c710a74fa99406618657ae63ce6d6c26fc8592b8dfc88023be61bfb`；build=`build/cuda_case4_prescale_q_exp156.so`。
- **唯一假设**: 只把generic `PRESCALE_Q`扩展到case4的KV8/BSM/combined/direct-out四页producer，保持单split、raw row16 QK、CTA内z-state合并、loader/barrier和直接输出不变。没有partial或final reducer，因此可隔离判断收益是否来自producer score热循环。
- **correctness**: CPU14/14；GPU full/boundary/random各14/14且finite；case4同进程`64→1→2→15→16→17→31→32→33→47→48→49→63→64`全部100% PASS，覆盖每个页边界和full→short→full。
- **A/B/OJ决定**: 初轮41×1000正向exp156/exp154=`0.9867/0.9889/0.9902`，反向exp154/exp156=`1.0076/1.0083/1.0099`，消偏约`0.9903`。强复测61×1000正向=`0.9801/0.9893/0.9956`，反向=`1.0088/1.0120/1.0159`，消偏约`0.98872`。相对fresh #108658最终复验，case4消偏约`0.9927`、case10约`0.99765`，case8/11/14中性。#108679为14/14 Accepted / `60.07`，case1–14=`3/4/10/28/22/32/286/139/287/54/344/477/256/258 μs`；目标case4 `29→28 μs`、得分`67→68`，case10保持54，case11相同源码tier从42降到41分使总分仍60.07。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case4_prescale_q_exp156.cpp`，逐提交源码为`solutions/archive/2026-08-11-submissions/cuda_108679.cpp`；因目标变化一致，#108679取代#108658成为control。

### exp157-case6-prescale-q  (LOCALLY POSITIVE, OJ #108691 ACCEPTED/60.00, 2026-08-11)
- **父/control**: exp156/#108679，SHA `27abd5e20c710a74fa99406618657ae63ce6d6c26fc8592b8dfc88023be61bfb`；候选SHA `ae74e4e561083be57cbeb1dd20561c29cb736c9c0e91e4a04a75471291c322d2`；build=`build/cuda_case6_prescale_q_exp157.so`。
- **唯一假设**: 只把generic `PRESCALE_Q`扩展到case6的KV8同步combined producer，保持split8、约3 pages/split、raw row16 QK、loader、partial和group8 reducer不变。exp155已证明约2 pages/split中性，而case4/10的4 pages正向，因此本实验定位摊销阈值。
- **correctness**: GPU full/boundary/random各14/14且finite；case6同进程`362→1→2→15→16→17→47→48→49→95→96→97→143→144→145→191→192→193→239→240→241→287→288→289→335→336→337→361→362`全部100% PASS，覆盖3-pages/split模数和full→short→full。
- **A/B/OJ决定**: 初轮41×1000正向exp157/exp156=`0.9716/0.9950/1.0262`，反向exp156/exp157=`1.0023/1.0104/1.0183`，消偏约`0.99235`。强复测61×1000正向=`0.9845/0.9907/1.0002`，反向=`1.0018/1.0120/1.0195`，消偏约`0.98942`。#108691为14/14 Accepted / `60.00`，case1–14=`3/4/11/28/22/32/285/139/286/53/343/476/256/256 μs`；目标case6仍32 μs未跨tier，非目标case3 `10→11 μs`使得分82→80。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case6_prescale_q_exp157.cpp`，逐提交源码为`solutions/archive/2026-08-11-submissions/cuda_108691.cpp`；不替换#108679，但该机制继续保留在exp158组合中。

### exp158-case13-prescale-q  (CONFIRMED, OJ #108700 ACCEPTED/59.93, 2026-08-11)
- **父/control**: exp157，SHA `ae74e4e561083be57cbeb1dd20561c29cb736c9c0e91e4a04a75471291c322d2`；候选SHA `37a59eaa6d4cdf213d3c5dc224d2fc8736641245fdca1e6724b8c0b0ed46cae5`；build=`build/cuda_case13_prescale_q_exp158.so`。
- **唯一假设**: 只给case13的KV8 full+fused-tail producer启用Q预缩放，保持split256/15 pages、四标量K+V lookahead、raw row16 QK、partial和64-thread vec2 reducer不变。
- **correctness**: GPU full/boundary/random各14/14且finite；case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部100% PASS。
- **A/B/OJ决定**: 初轮41×500正向exp158/exp157 p50=`0.9969`、反向=`1.0005`，消偏约`0.9982`；强复测61×500正向=`0.9944/0.9972/1.0005`，反向=`0.9978/1.0011/1.0045`，消偏约`sqrt(0.9972/1.0011)=0.99805`，快约0.20%或0.5 μs。#108700为14/14 Accepted / `59.93`，case1–14=`3/4/11/28/22/32/284/139/286/54/346/476/254/257 μs`；唯一目标case13相对同父#108691 `256→254 μs`，但得分仍为48，非目标case11 tier令aggregate下降。raw、逐提交快照和完整实验源码SHA一致；确认局部机制但不替换#108679。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case13_prescale_q_exp158.cpp`。

### exp159-case12-prescale-q  (CONFIRMED, FORMER OJ BASELINE #108713 / 60.14, 2026-08-11)
- **父/control**: exp158，SHA `37a59eaa6d4cdf213d3c5dc224d2fc8736641245fdca1e6724b8c0b0ed46cae5`；候选SHA `3cee37f740ae7ccbba6491d133ea39aeef8e0b8f60a7f4aa049921f9c4a1e9c9`；build=`build/cuda_case12_prescale_q_exp159.so`。
- **唯一假设**: 只给case12的KV8 16-page full+fused-tail producer启用Q预缩放，保持128-owner布局、四标量K+V lookahead、raw row16 QK、partial和64-thread vec2 reducer不变。
- **correctness**: GPU full/boundary/random各14/14且finite；case12同进程`32768→1→2→15→16→17→255→256→257→511→512→513→4095→4096→4097→32767→32768`全部100% PASS，覆盖页、split和full→short→full边界。
- **A/B/OJ决定**: 强测正向exp159/exp158=`0.9960/0.9963/0.9968`，反向exp158/exp159=`1.0025/1.0034/1.0043`，按p50消偏约`sqrt(0.9963/1.0034)=0.99645`，快约0.35%。#108713为14/14 Accepted / `60.14`，case1–14=`3/4/10/29/22/31/285/139/285/54/341/475/255/258 μs`；目标case12 `476→475 μs`与A/B同向，case6/case11本轮跨到61/42分使aggregate刷新。raw、逐提交快照与完整实验源码SHA一致；#108713取代#108679成为control。

### exp160-case7-prescale-q  (LOCALLY POSITIVE, 2026-08-11)
- **父/control**: exp159/#108713，SHA `3cee37f740ae7ccbba6491d133ea39aeef8e0b8f60a7f4aa049921f9c4a1e9c9`；候选SHA `cfabb423ea4db855d0531e35e841f7f2df24ce9000775424f66dd05b882344dc`；build=`build/cuda_case7_prescale_q_exp160.so`。
- **唯一假设**: 只给case7的KV8 split14 full+fused-tail producer启用Q预缩放，保持K+V lookahead、raw row16 QK、partial和8-head grouped reducer不变。
- **correctness**: GPU full/boundary/random各14/14且finite；case7同进程`2048→1→2→15→16→17→159→160→161→319→320→321→2031→2032→2033→2047→2048`全部100% PASS。
- **A/B/结论**: 初轮正向exp160/exp159 p50=`0.9948`、反向exp159/exp160=`1.0058`，消偏约`0.9945`；61×500强复测正向=`0.9933/0.9952/1.0455`，反向=`1.0053/1.0058/1.0065`，按p50消偏约`0.9947`，快约0.53%。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case7_prescale_q_exp160.cpp`，收益已组合进exp161。

### exp161-case9-prescale-q  (CONFIRMED LOCALLY/OJ, NOT BASELINE, 2026-08-11)
- **父/control**: exp160，SHA `cfabb423ea4db855d0531e35e841f7f2df24ce9000775424f66dd05b882344dc`；候选SHA `0d92dfc789db9abafcc9d529cb3982132eaf27c0e4e1370b1ce502b679b07bfb`；build=`build/cuda_case9_prescale_q_exp161.so`。
- **唯一假设**: 只给case9的KV8 split24 full+fused-tail producer启用Q预缩放，保持K+V lookahead、raw row16 QK、partial和grouped reducer不变；与exp160的case7 dispatch互不重叠。
- **correctness**: 组合源码GPU full/boundary/random各14/14且finite；case9同进程`4096→1→2→15→16→17→175→176→177→351→352→353→4079→4080→4081→4095→4096`全部100% PASS。
- **A/B/OJ结论**: 初轮正向exp161/exp160 p50=`0.9959`、反向exp160/exp161=`1.0030`，消偏约`0.99645`；61×500强复测正向=`0.9959/0.9965/0.9974`，反向=`1.0014/1.0029/1.0047`，按p50消偏约`0.9968`，快约0.32%。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case9_prescale_q_exp161.cpp`。#108721为14/14 Accepted / `59.86`，case1–14=`3/4/11/29/22/32/284/139/285/54/346/473/255/258 μs`；相对#108713，case7 `285→284 μs`与exp160本地证据同向，case9保持285 μs未跨tier。case3/6/11的非目标回退使aggregate下降，case12 `475→473 μs`没有本轮对应源码差异、只能视为tier波动；故#108721不替换#108713。raw、逐提交源码、实验源码和工作文件SHA均一致；当前无OJ任务在途，Q预缩放主线闭环。

### exp162-case14-split-pair  (REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: exp161/#108721源码，SHA `0d92dfc789db9abafcc9d529cb3982132eaf27c0e4e1370b1ce502b679b07bfb`；候选SHA `e43434473162e88d2da5354fe8e3b42da08f733fcfc29d695d44fa527d546605`；build=`build/cuda_case14_splitpair_exp162.so`。
- **唯一假设**: 保持case14 `dim3(16,8,2)`、split257、normalized BF16 partial和final reducer不变，改让z0/z1各自拥有两个相邻logical split；每个z顺序处理完整页的两个8-token chunk并直接写原logical partial，删除CTA内z-state merge，同时以16 KiB独立K/V plane和两行register-lookahead把Q staging/CTA调度摊到两个split。不同于exp117–119，本轮不增加global partial。
- **资源/correctness**: 首版引用返回造成80 B stack，改为单行按值load/store后为`0 B stack / 80 MTreg / 46 STreg / 16384 B shared / staticMaxWarps=4`。CPU 14/14，GPU full/boundary/random各14/14；case14同进程`61519→1→8→9→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS且finite。
- **A/B/结论**: 相对从归档源码重建的exp161 control，case14 9 rounds×20交错A/B：control p50=`0.2611 ms`、candidate p50=`0.3226 ms`，ratio p10/p50/p90=`1.2334/1.2350/1.2375`，稳定慢23.5%。删除z merge与摊薄Q/CTA不足以抵消每z顺序整页和更大shared/同步成本；完整源码归档为`solutions/archive/2026-08-11-experiments/cuda_case14_splitpair_exp162.cpp`，不提交并关闭同一split-pair布局。工作文件已恢复exp161。

### exp163-case14-headpair-register-lookahead  (OJ CONFIRMED, CURRENT BASELINE #108743 / 60.29, 2026-08-11)
- **父/control**: exp161，SHA `0d92dfc789db9abafcc9d529cb3982132eaf27c0e4e1370b1ce502b679b07bfb`；候选SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；build=`build/cuda_case14_headpair_reglook_exp163.so`。
- **关键新前提/唯一假设**: exp63在split257/direct-Q/raw-QK/normalized-BF16前提下重开case14 head-pair/z4仍慢约1.45%，但它只使用BSM page pipeline；exp120随后证明generic case14的同步K/V register-lookahead约快5.05%。exp163只把case14切换为head-pair/z4并组合该register pipeline；split257、fused tail、raw QK、Q预缩放、normalized-BF16 partial和final reducer不变。每个z是一条完整wave，下一页K/V可在寄存器中跨当前PV并用wave barrier覆盖overwrite/page-ready。
- **资源/correctness**: `94 MTreg / 52 STreg / 8320 B shared / 0 B stack / staticMaxWarps=5`，与generic control均为一个实际4-wave CTA驻留档。CPU14/14、GPU full/boundary/random各14/14；case14同进程`61519→1→4→5→8→9→12→13→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS且finite。
- **A/B/OJ决定**: 首轮9×20 p50=`0.8553`；41×200强测正向exp163/exp161=`0.8542/0.8561/0.8591`，反向exp161/exp163=`1.1614/1.1639/1.1659`，按p50消偏约`sqrt(0.8561/1.1639)=0.8576`，快约14.24%。#108743为14/14 Accepted / **`60.29`**，case1–14=`3/4/10/28/22/32/283/139/285/53/344/472/255/219 μs`，分数=`92/90/82/68/67/60/49/44/52/54/41/54/48/43`。相对#108713，目标case14 `258→219 μs`、`40→43分`，总分`60.14→60.29`；其余shape没有exp163源码差异，按timing-tier波动处理。raw、逐提交快照、完整实验源码与当时工作文件SHA一致；#108743正式成为当时baseline，该轮无OJ任务在途。

### exp164-case14-headpair-early-page-id  (NEUTRAL, REJECTED, 2026-08-11)
- **父/control**: exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `94ff62591aa38cda0dcf393ddaa298f4bcf16ca572bdc91db8f8e787608ae145`；build=`build/cuda_case14_headpair_earlypid_exp164.so`。
- **唯一假设/结果**: 只把已有`PREFETCH_NEXT_PID`从false改为true，让next page ID在QK前解析；其他字节路径保持exp163。资源仅`STreg 52→54`，0 stack/5 warps不变，case14 full 100% PASS。相对exp163的21×100交错A/B p10/p50/p90=`0.9971/1.0004/1.0058`，完全中性；不保留、不提交，工作文件已恢复exp163。

### exp165-case14-headpair-split275  (REJECTED, 2026-08-11)
- **父/control**: exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `c33579875601f3e853cad97ad46f0e497fdd2ae6d5fdf15b6ab7fca579c24702`；build=`build/cuda_case14_headpair_split275_exp165.so`。
- **唯一假设/结果**: split policy架构相关，因此在exp163快14.24%的head-pair/register新前提下，只把case14 `n_split 257→275`、pages/split `15→14`；其余producer、partial和reducer不变。case14 full 100% PASS；相对exp163的21×100 p10/p50/p90=`1.0229/1.0256/1.0293`，稳定慢2.56%，与generic exp51同向。257仍是该架构离散最优点，不继续同一邻域扫描；完整源码已归档，工作文件恢复exp163。

### exp166-case14-headpair-early-data  (REJECTED, 2026-08-11)
- **父/control**: exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `09ac4880e23856da8754fabdb891ded064eaf37c81a76594d4e6f49f469718b0`；build=`build/cuda_case14_headpair_earlydata_exp166.so`。
- **唯一假设/结果**: 保持next page ID位置、ownership、split和数学不变，只把已有next K/V register load从当前QK后提前到QK前，使global load可跨QK+PV；next值因此多跨一段QK live range。资源`94→96 MTreg`、52 STreg、0 stack/5 warps；case14 full 100% PASS。相对exp163的21×100 A/B=`1.0138/1.0160/1.0185`，稳定慢1.6%。PV已足以隐藏原位置加载，提前只增加live-range/调度成本；完整源码已归档，工作文件恢复exp163。

### exp167-case14-headpair-interleaved-partial  (REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: exp163/#108743，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `a52468febf378826e04e2de784af920bee14f31a2862fe6a6d4f1b6a04f1c38f`；build=`build/cuda_headpair_partial_exp167.so`。
- **唯一假设**: producer天然同时拥有`h0/h1`，因此保持m/l的head-major契约、split257、fused tail、数学和workspace总字节数不变，只把normalized-BF16 accumulator改为`{h0[d],h1[d]}`交错BF16x2；matching 128-thread reducer把grid从32个one-head CTA改为16个head-pair CTA，一次32-bit load同时更新两头。它不同于exp54仅把两个原布局reducer装进同一CTA，本轮确实改变partial布局和acc数据流。
- **资源/correctness**: producer仍为`94 MTreg/52 STreg/8320 B/0 stack/5 warps`；新reducer为`28 MTreg/42 STreg/0 stack/8 warps`，control one-head reducer为`40/36/0/8`。CPU14/14，GPU full/boundary/random各14/14且finite；case14同进程`61519→1→4→5→8→9→12→13→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS，覆盖tail-only、split边界和full→short→full workspace复用。
- **A/B/结论**: 正向exp167/exp163 9×20=`1.0363/1.0386/1.0438`；交换角色后exp163/exp167=`0.9520/0.9600/0.9640`，按p50消偏得到exp167/control约`sqrt(1.0386/0.9600)=1.0401`，稳定慢约4.01%。总acc字节没有减少，单次packed load不足以抵消reducer CTA `32→16`后的并行度下降和每CTA双head权重/acc工作；拒绝且不提交。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case14_headpair_partial_exp167.cpp`，工作文件已恢复#108743。不得以相同interleaved布局继续调线程数或metadata；下一次partial实验必须真正减少总状态字节、权重工作或kernel round trip。

### exp168-case11-head4-register-lookahead  (REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `11954afc5baf56956413215ed7ce5967b3f9a6f59b2e6b92ef0041bb413f76c1`；build=`build/cuda_case11_head4_reglook_exp168.so`。
- **关键新前提/唯一假设**: 旧exp81的128-thread `(16,2,4)` head4/z4只在同步K→PV→V page pipeline上测试过，四head共享一次K/V解包几乎抵消active waves减半，消偏仅慢0.32%；exp110后来让当前head-pair的同步K/V register-lookahead快约5.9%。本轮在当前split48、fused tail、raw-row16 QK、Q预缩放、FP32 partial和vec4 reducer上，只把case11 ownership改为head4，并让每线程预取两行next K/V，判断新pipeline能否翻转旧结果。
- **资源/correctness**: full producer为`146 MTreg/46 STreg/8320 B/0 stack/staticMaxWarps=3`；128-thread CTA实际仍只能驻留一个2-wave block，相比#108743 head-pair的一个4-wave block没有恢复并发。case11 full 100% PASS、max_error=`2.441406e-04`、finite；性能已明确失败，因此按门槛未继续全量correctness。
- **A/B/结论**: 正向exp168/#108743 9×20=`1.0566/1.0584/1.0592`；交换角色后#108743/exp168=`0.9429/0.9439/0.9448`，消偏后exp168/control约`sqrt(1.0584/0.9439)=1.0589`，稳定慢约5.89%。双行K/V lookahead把head4资源从旧exp81的132提高到146 MTreg，却没有增加active waves；四head解包复用不能覆盖并发减半及双行register pipeline成本。拒绝且不提交，完整源码为`solutions/archive/2026-08-11-experiments/cuda_case11_head4_reglook_exp168.cpp`，工作文件恢复#108743。head4路线在旧同步和新register两种pipeline下均未胜出；除非先有能把资源跨到至少4 static warps且不增加热循环转换的新状态表示，否则不得重开。

### exp169-case13-uint2-kv-register-lookahead  (RESOURCE-GATE REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `57a203a3dc5b34a582aee96be0c68901339bd4d0f82014f99bea50a5e81e22c9`；resource build=`build/cuda_case13_uint2_kv_exp169.so`。
- **关键前提/唯一假设**: exp111把next-K保持为一个`uint4`时产生32 B stack，exp130–138改为独立`uint32_t`后消除spill并让长KV8 K+V-over-PV连续获益。本轮只把case13跨PV存活的next-K/next-V各四个标量重排为两个`uint2` pair，以两次64-bit load/store替代四次标量操作；split256/15页、fused tail、raw QK、Q预缩放、FP32 partial和vec2 reducer均不变。
- **资源门槛/结论**: CPU语义14/14；候选目标实例为`66 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=7`，而同次编译的既有标量K+V实例为`64/50/8192/0/8`。256-thread CTA占4条64-lane wave，`8→7`会使静态可驻留CTA从2个降到1个；虽未重现stack，pair aggregate仍跨过关键occupancy档。按预设门槛不运行GPU correctness/A-B、不提交；完整源码为`solutions/archive/2026-08-11-experiments/cuda_case13_uint2_kv_exp169.cpp`，工作文件已恢复#108743。KV8跨PV live aggregate现已在`uint4`（spill）和`uint2`（occupancy减半）两种粒度失败，后续若优化向量load，必须在加载后立即拆成标量并保持8-warps档，不能让vector aggregate跨PV存活。

### exp170-case13-uint2-load-scalar-live  (OJ CONFIRMED LOCALLY, #108763 ACCEPTED/60.14, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `9535acf79de359bd5e4909135b83efdbdfd91bfb8ad1af50ed092fa74e297b26`；final/resource builds=`build/cuda_case13_uint2_load_scalar_exp170_final.so`/`build/cuda_case13_uint2_load_scalar_exp170.so`。
- **关键新前提/唯一假设**: exp169证明`uint2`跨PV存活会让staticMaxWarps `8→7`；本轮仍以两个`uint2`读取每个next K/V row，但在load site立即拆回原八个`uint32_t`，只让标量跨当前PV存活，并保持原四次scalar shared store。case13的split256/15页、fused tail、raw QK、Q预缩放、FP32 partial和vec2 reducer均不变。
- **资源/correctness**: 目标实例`64 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps=8`，相对同次编译的标量control `64/50/8192/0/8`只多2 STreg，保持两个四-wave CTA驻留档。CPU14/14；同一final `.so`的GPU full/boundary/random各14/14；case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部100% PASS且finite。
- **A/B/OJ决定**: 初轮9×20正向/反向p50=`0.9951/1.0070`；41×200强测正向exp170/#108743=`0.9923/0.9938/0.9968`，反向#108743/exp170=`1.0034/1.0051/1.0067`，消偏约`sqrt(0.9938/1.0051)=0.99436`、快0.56%。#108763为14/14 Accepted / `60.14`，case1–14=`3/4/11/29/22/31/284/139/284/54/345/473/254/221 μs`；目标case13相对#108743 `255→254 μs`同向但仍48分，非目标case3/4退档与case6进档使aggregate下降。局部机制确认但不替换#108743 baseline；raw、逐提交快照和完整实验源码SHA一致。

### exp171-case12-uint2-load-scalar-live  (LOCALLY POSITIVE, 2026-08-11)
- **父/control**: exp170，SHA `9535acf79de359bd5e4909135b83efdbdfd91bfb8ad1af50ed092fa74e297b26`；候选SHA `1a23d1ffcb233a78404da0b7f8cb727e7e6ab5498a221ffea36f12a8a64ff721`；build=`build/cuda_case12_uint2_load_scalar_exp171.so`。
- **唯一假设**: 只把exp170已在case13确认的“两个`uint2` load后立即标量化、八标量跨PV”扩展到case12；case13保持exp170，case12的split128/16页、fused tail、raw QK、Q预缩放、FP32 partial和64-thread vec2 reducer不变，并复用同一`64/52/8192/0/8`模板实例。
- **correctness/A-B**: CPU14/14、case12 full 100% PASS；同进程`32768→1→2→15→16→17→255→256→257→511→512→513→4095→4096→4097→32767→32768`全部PASS且finite。初轮9×20正向/反向p50=`0.9967/1.0026`；41×100复测正向exp171/exp170=`0.9958/0.9972/0.9982`，反向exp170/exp171=`1.0017/1.0027/1.0034`，消偏约`0.99725`、快0.28%或约2.7 μs。41×200正向受频率波动污染但p50方向一致，不用于区间结论。
- **结论**: 接纳为本地组合候选，尚未提交；完整源码为`solutions/archive/2026-08-11-experiments/cuda_case12_uint2_load_scalar_exp171.cpp`，工作文件与其字节一致。下一步按shape逐一验证case9/7，不能未经A/B全局打开。

### exp172-case9-uint2-load-scalar-live  (LOCALLY POSITIVE, 2026-08-11)
- **父/control**: exp171，SHA `1a23d1ffcb233a78404da0b7f8cb727e7e6ab5498a221ffea36f12a8a64ff721`；候选SHA `9f3dfb59de24dbd24f2ed8c8f51562f6b7f19ddbedb1b9c742a1f20953aad0ca`；build=`build/cuda_case9_uint2_load_scalar_exp172.so`。
- **唯一假设**: 只把load-site `uint2`→scalar-live K+V lookahead扩展到case9；case12/13保持exp171，case9的split24/11页、fused tail、raw QK、Q预缩放、FP32 partial和grouped reducer不变，并复用同一`64/52/8192/0/8`模板实例。
- **correctness/A-B**: CPU14/14、case9 full通过；同进程`4096→1→2→15→16→17→175→176→177→351→352→353→4079→4080→4081→4095→4096`全部PASS且finite。初轮9×20正向/反向p50=`0.9958/1.0041`；41×100正向exp172/exp171=`0.9941/0.9953/0.9962`，反向exp171/exp172=`1.0022/1.0037/1.0046`，消偏约`0.99581`，快0.42%或约2.1 μs。
- **结论**: 接纳为本地组合候选，未单独提交；完整源码为`solutions/archive/2026-08-11-experiments/cuda_case9_uint2_load_scalar_exp172.cpp`。下一步只验证case7，不能将结论外推到短KV8 combined路径。

### exp173-case7-uint2-load-scalar-live  (OJ CONFIRMED, NOT BASELINE, 2026-08-11)
- **父/control**: exp172，SHA `9f3dfb59de24dbd24f2ed8c8f51562f6b7f19ddbedb1b9c742a1f20953aad0ca`；候选SHA `22475804001e1cb70eeae5b906838109dfe67b6f92e2adbd89fdc89b1e5cb887`；build=`build/cuda_case7_uint2_load_scalar_exp173.so`。
- **唯一假设**: 只把同一load-site pair/scalar-live模式扩展到最后一个长KV8 shape case7；case9/12/13保持各自已验证扩展，case7的split14/10页、fused tail、raw QK、Q预缩放、FP32 partial和group8 reducer不变。四shape从此共享`64/52/8192/0/8`目标实例，旧scalar K+V实例不再被长KV8 dispatch使用。
- **correctness/A-B**: CPU14/14；case7 full和`2048→1→2→15→16→17→159→160→161→319→320→321→2031→2032→2033→2047→2048`全部PASS。初轮9×20正向/反向p50=`0.9977/1.0015`；41×100正向exp173/exp172=`0.9966/0.9977/0.9980`，反向exp172/exp173=`1.0014/1.0022/1.0032`，消偏约`0.99775`、快0.23%。最终组合GPU full/boundary/random各14/14且finite；对未改dispatch的case9/12/13做21×100正反回归，消偏均在噪声内。
- **结论/OJ**: 四个长KV8 shape已按case13→12→9→7逐一独立复现。#108772最终14/14 Accepted / `60.29`，case1–14=`3/4/10/29/22/32/282/139/283/53/344/471/253/218 μs`；目标case7/9/12/13相对#108743从`283/285/472/255→282/283/471/253 μs`全部同向，但得分仍为`49/52/54/48`，case4无源码差异却波动`28→29 μs`，aggregate持平。机制确认但不替换#108743 baseline；raw、提交快照和完整实验源码SHA一致。工作文件空闲状态已恢复#108743。

### exp174-case11-lane0-softmax-broadcast  (REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: exp173，SHA `22475804001e1cb70eeae5b906838109dfe67b6f92e2adbd89fdc89b1e5cb887`；候选SHA `42eab01d8d7e3be4bfb7eb61cff47f3d153978eb7f26c2a99fa8aefdb0b16ab5`；build=`build/cuda_case11_lane0_softmax_exp174.so`。
- **唯一假设**: case11 head-pair/z4的每个16-lane row拥有相同两头logit；只让`tx=0`维护`(m,l)`并计算两头的`alpha/w[4]`，再用`width=16` shuffle广播给其余维度lane。QK、PV、K/V register-lookahead、split48、fused tail、FP32 partial和reducer不变。它不同于#104000的早期32-lane架构与同时改split版本。
- **correctness/A-B**: CPU14/14、C500 case11 full 100% PASS，max error=`2.441406e-04`、finite。首轮9×20相对exp173的ratio p10/p50/p90=`1.1796/1.1797/1.1808`，稳定慢约17.97%。
- **结论**: 逐页新增的广播依赖和lane0串行软最大于省掉的冗余`exp2`；差异已远离噪声，无需反向长测或OJ。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case11_lane0_softmax_exp174.cpp`，工作文件已恢复exp173。关闭当前head-pair热循环的lane0-softmax/broadcast路线，不以raw broadcast、split或loader微调补偿。

### exp175-native-packed-multiply-scale  (NEUTRAL, NOT SUBMITTED, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `60526c065c92a6577576fd59d8035b30eaeecb7502347359bdd9c6e289486d94`；build=`build/cuda_pk_mul_scale_exp175.so`。
- **唯一假设**: 官方指南列出xcore1000原生`__builtin_mxc_pk_mul_f32`；只把`packed_scale(a,s)`从`pk_fma(a,{s,s},0)`改为`pk_mul(a,{s,s})`。QK/PV累加FMA、数学、dispatch、split、loader和reducer布局不变。binary字符串确认候选新增`llvm.mxc.pk.mul.f32`，control只有packed FMA。
- **correctness/A-B**: CPU14/14且构建成功。9×20交错A/B的case10/11/14 p50分别为`1.0018/0.9995/0.9996`，各区间均处于中性量级，远不足以跨OJ tier。
- **结论**: native packed multiply可用，但当前缩放占比或后端吞吐没有形成端到端收益；不做更重测试、不提交。完整源码为`solutions/archive/2026-08-11-experiments/cuda_pk_mul_scale_exp175.cpp`，工作文件恢复#108743。除非新的profile证明scale成为主瓶颈，不继续按shape拆分同一builtin替换。

### case11-current-phase-ablation  (TIMING-ONLY DIAGNOSTIC, INVALID OUTPUT, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；control=`build/cuda_108743_control.so`，探针为`build/cuda_case11_noqk_probe.so`与`build/cuda_case11_nopv_probe.so`。
- **方法/边界**: 分别删除case11当前head-pair/register-lookahead producer的QK或PV计算，使用`tests/c500_benchmark.py --skip-correctness`做21轮×100次交错计时。两个探针故意产生错误输出，删除计算也会改变资源和调度，因此结果只表示阶段成本上界，严禁提交；临时probe宏已从工作源码完全移除。
- **结果/推导**: no-QK ratio p10/p50/p90=`0.5173/0.5182/0.5193`，QK上界约48.2%；no-PV=`0.8490/0.8496/0.8503`，PV上界约15.0%。在#108743的新pipeline上，QK仍明显是case11最大可压缩计算阶段，下一架构应优先攻击QK，并保持K/V register-lookahead与PV重叠。

### exp176-case11-packed-k-row-broadcast  (REJECTED, NOT SUBMITTED, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `b6398be4d333514831747f389eed063f293e875ca50769550713136b3939ac72`；build=`build/cuda_case11_packed_k_broadcast_exp176.so`。
- **唯一假设**: exp97广播8个已解包FP32 K并慢41.3%；本轮把跨row交换减半，只让`ty=0`加载K，并将4个packed-BF16 `uint32_t`从row0广播到同一`tx`，各row再本地解包。QK/PV、split48、register-lookahead、softmax、partial和reducer不变。
- **资源/correctness**: full producer从control的`94 MTreg/54 STreg/8320 B/0 stack/5 warps`变为`90/56/8320/0/5`；CPU语义14/14，C500 case11 full 100% PASS、max error=`2.441406e-04`、finite。
- **A/B/结论**: 初轮9×20 ratio p10/p50/p90=`1.2488/1.2492/1.2504`，稳定慢约24.9%。即便交换数从8次FP32降到4次packed，跨row bpermute仍远贵于三份冗余shared `uint4` load；拒绝，不做反向长测、全量correctness或OJ。关闭等价packed K/V row broadcast及仅靠source重排减少同一广播数的路线；完整源码已归档，工作文件恢复#108743。

### exp177-case11-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control**: #108743/exp163，SHA `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；候选SHA `d82b354614b585e6b18c099cc2d87abcd92222dfbe0e7bb18cc3a36c32f31496`；build=`build/cuda_case11_native_rowreduce_exp177.so`。
- **关键新前提/唯一假设**: 官方指南确认xcore1000一个64-thread warp由四个原生16-lane row组成，`__builtin_mxc_mov_shfl`在每个row内独立混洗。当前raw QK虽已删除wrapper边界判断，仍用全wave BSM bpermute做XOR `8/4/2/1`。本轮只给case11目标实例改用四条native网络：row rotate-right `8/4`（mode `0x128/0x124`）与quad XOR `2/1`（mode `0x04e/0x0b1`）；QK FMA、head/token ownership、split48、K/V register-lookahead、softmax/PV、partial和reducer不变。
- **原语/codegen/资源**: 扩展`tests/c500_bpermute_probe.cpp/.py`并在真实C500逐lane确认native网络与raw XOR allreduce字节精确相等。最终目标LLVM实例为`64 mov.shfl / 0 bsm.bpermute`，其余BF16转换、packed FMA和exp2计数不变；producer从`94 MTreg/54 STreg/8320 B/0 stack/5 warps`降为`90/54/8320/0/5`。
- **correctness**: CPU语义14/14；同一`.so`的GPU full/boundary/random各14/14且finite（random按case独立进程，避免reference资源累积）。case11同进程`12251→1→2→15→16→17→255→256→257→511→512→513→767→768→769→12250→12251`全部100% PASS，最大误差不超过`1.5625e-02`，覆盖tail-only、split边界和full→short→full workspace复用。
- **A/B/OJ决定**: 初轮9×20 ratio=`0.8513/0.8526/0.8532`。41×200正向exp177/#108743=`0.8521/0.8525/0.8538`，反向#108743/exp177=`1.1728/1.1734/1.1741`，按p50消偏约`sqrt(0.8525/1.1734)=0.8524`，时延下降约14.76%。#108803正常经历`Pending→Running→Finished`，14/14 Accepted / **`60.50`**；case1–14=`3/4/10/29/22/32/284/139/284/53/301/475/254/220 μs`，目标case11相对#108743 `344→301 μs`、`41→45分`。aggregate刷新，exp177/#108803成为当时baseline；raw、提交快照和完整实验源码SHA均为`d82b354614b585e6b18c099cc2d87abcd92222dfbe0e7bb18cc3a36c32f31496`。

### exp178-case8-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control**: #108803/exp177，SHA `d82b354614b585e6b18c099cc2d87abcd92222dfbe0e7bb18cc3a36c32f31496`；候选SHA `3e2f27cd5032a1f1c34f1e6f2490686a91be27a328c57c9382d6dacaeab5d92c`；build=`build/cuda_case8_native_rowreduce_exp178.so`。
- **唯一假设**: 只把exp177已在case11获得OJ证据的native 16-lane row allreduce扩展到case8；case11保持已验证网络，case8的head/token ownership、split48、K/V register-lookahead、softmax/PV、partial和reducer全部不变。
- **correctness**: CPU语义14/14；同一`.so`的GPU full/boundary/random各14/14且finite，random按case独立进程避免reference资源累积。case8同进程`4096→1→2→15→16→17→95→96→97→111→112→191→192→193→4095→4096`全部100% PASS，覆盖tail-only、6-pages/split边界和full→short→full workspace复用。
- **A/B/OJ决定**: 初测9×20 exp178/exp177 ratio=`0.8908/0.8916/0.8925`。41×200正向=`0.8904/0.8911/0.8919`，反向exp177/exp178=`1.1218/1.1231/1.1242`，消偏约`sqrt(0.8911/1.1231)=0.8907`，时延下降约10.9%。#108816为14/14 Accepted / **`60.79`**，case8相对#108803 `139→125 μs`、`44→47分`，成为当时baseline；raw、提交快照和完整实验源码SHA均为`3e2f27cd5032a1f1c34f1e6f2490686a91be27a328c57c9382d6dacaeab5d92c`。

### exp179-case14-native-row16-allreduce  (OJ CONFIRMED / CURRENT BASELINE, 2026-08-11)
- **父/control**: #108816/exp178，SHA `3e2f27cd5032a1f1c34f1e6f2490686a91be27a328c57c9382d6dacaeab5d92c`；候选SHA `9dd9651f6ec947e1fb976ed5cbb73e776dc1713020b5f51a3583f803308b4011`；build=`build/cuda_case14_native_rowreduce_exp179.so`。
- **唯一假设**: 只把已经在case11/8得到本地与OJ证据的native 16-lane row allreduce扩展到case14 head-pair/z4 producer；case8/11保持已验证网络，case14 ownership、split257、K/V register-lookahead、softmax/PV、normalized-BF16 partial和reducer全部不变。
- **correctness**: CPU语义14/14；同一`.so`的GPU full/boundary/random各14/14且finite，random按case独立进程避免reference资源累积。case14同进程`61519→1→4→5→8→9→12→13→15→16→17→239→240→241→479→480→481→61518→61519`全部100% PASS，覆盖tail-only、15-pages/split边界和full→short→full workspace复用。
- **A/B/OJ决定**: 初测9×20 exp179/exp178 p50=`0.8538`。41×200正向exp179/exp178=`0.8522/0.8537/0.8558`，反向exp178/exp179=`1.1747/1.1772/1.1791`，消偏约`sqrt(0.8537/1.1772)=0.8516`，时延下降约14.8%。#108821为14/14 Accepted / **`61.14`**，case1–14=`3/4/10/28/22/31/283/126/284/53/299/472/254/186 μs`；目标case14相对#108816 `219→186 μs`、`43→48分`，aggregate刷新。raw、提交快照和完整实验源码SHA一致，exp179/#108821成为当前baseline。

### exp180-case13-native-row16-allreduce  (NEUTRAL, NOT SUBMITTED, 2026-08-11)
- **父/control**: #108821/exp179，SHA `9dd9651f6ec947e1fb976ed5cbb73e776dc1713020b5f51a3583f803308b4011`；候选SHA `e1443cc93ef6388142309294caee951ff35990c610494554ec45493bea0b42c3`；build=`build/cuda_case13_native_rowreduce_exp180.so`。
- **唯一假设**: generic KV8 token-parallel仍在固定16-lane QK归约中使用raw BSM bpermute；只给B1/L58966 case13模板增加与head-pair KV4相同的native `mov.shfl` allreduce，保持split256/15页、K+V scalar lookahead、Q预缩放、fused tail、FP32 partial和vec2 reducer不变，其他shape默认关闭。
- **correctness/A-B**: CPU语义14/14；目标case13的GPU full/boundary/random均100% PASS且finite。9×20正向exp180/exp179 p50=`1.0009`，交换模块角色后的exp179/exp180 p50=`1.0011`，消偏约`sqrt(1.0009/1.0011)=0.9999`，完全中性。
- **结论**: head-pair KV4上的两位数收益不能直接外推到case13 generic KV8当前实例；该exact替换不足以进入41×200或OJ，拒绝且不提交。完整源码为`solutions/archive/2026-08-11-experiments/cuda_case13_native_rowreduce_exp180.cpp`；工作文件已字节精确恢复#108821。该结论只关闭case13当前模板，不能未经A/B外推到pages/split与并发不同的其他generic KV8 shape。

### exp181-case12-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control**: #108821/exp179，SHA `9dd9651f6ec947e1fb976ed5cbb73e776dc1713020b5f51a3583f803308b4011`；候选SHA `2dcd0620181bcafb1c19d427bfe33a683a514bc73fd5e83c9707220153bd5117`；build=`build/cuda_case12_native_rowreduce_exp181.so`。
- **关键前提/唯一假设**: exp180已证明B1/split256/15页的case13同一替换中性，但不能否定B8/split128/16页且producer CTA更多的case12。本轮只给case12 generic KV8 full/fused-tail模板启用native `mov.shfl` row allreduce；K+V scalar lookahead、Q预缩放、partial、vec2 reducer及所有其他shape保持#108821。
- **correctness**: CPU语义14/14；同一候选`.so`的GPU full/boundary/random各14/14且finite，padding-page trap随harness覆盖。目标case12三种长度分布均100% PASS；改动不改变workspace ownership或live-split计数。
- **A/B**: 初轮9×20正向exp181/#108821=`0.8631/0.8637/0.8645`，反向#108821/exp181=`1.1556/1.1564/1.1575`。41×200正向=`0.8632/0.8638/0.8645`，反向=`1.1554/1.1571/1.1579`，消偏约`sqrt(0.8638/1.1571)=0.8640`，case12稳定快约13.6%。非目标case7/9/13/14的9×20 p50=`0.9995/1.0002/0.9996/1.0018`，均在噪声内。
- **OJ决定**: #108827为14/14 Accepted / **`61.36`**，case1–14=`3/4/10/28/22/32/283/125/287/53/300/425/255/186 μs`；目标case12相对#108821 `472→425 μs`、`54→57分`，与本地强测同向。case6丢一分与case8恢复一分相互抵消，aggregate刷新；raw、逐提交快照和完整实验源码SHA均为`2dcd0620181bcafb1c19d427bfe33a683a514bc73fd5e83c9707220153bd5117`，exp181/#108827成为当前baseline。

### exp182-case9-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control**: #108827/exp181，SHA `2dcd0620181bcafb1c19d427bfe33a683a514bc73fd5e83c9707220153bd5117`；候选SHA `8c1eb876b638fd2b63cbbf0e490c6aededce348913ebc0b35650a4e240137054`；build=`build/cuda_case9_native_rowreduce_exp182.so`。
- **唯一假设**: 只把exp181已经在case12本地/OJ确认的native row allreduce扩展到case9的B32/split24/11页producer；case12保持native，case9的K+V lookahead、Q预缩放、fused tail、FP32 partial和grouped reducer不变，case7/13仍用raw BSM。
- **correctness/A-B**: CPU语义14/14；同一`.so`的GPU full/boundary/random各14/14且finite。初轮9×20正向exp182/exp181 p50=`0.8734`、反向exp181/exp182=`1.1457`。41×200正向=`0.8724/0.8728/0.8738`，反向=`1.1445/1.1458/1.1473`，消偏约`sqrt(0.8728/1.1458)=0.8728`，case9稳定快约12.7%。
- **OJ决定**: #108840正常经历`Pending→Running→Finished`，14/14 Accepted / **`61.50`**；case1–14=`3/4/10/29/22/32/283/125/254/53/301/426/256/186 μs`，分数=`92/90/82/67/67/60/49/47/55/54/45/57/48/48`。目标case9相对#108827 `287→254 μs`、`52→55分`，与本地强测同向；case4非目标波动丢一分，aggregate仍从61.36刷新到61.50。raw内嵌代码、逐提交快照和完整实验源码SHA均为`8c1eb876b638fd2b63cbbf0e490c6aededce348913ebc0b35650a4e240137054`，exp182/#108840成为当前baseline；当前没有OJ任务在途。

### exp183-case7-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control**: #108840/exp182，SHA `8c1eb876b638fd2b63cbbf0e490c6aededce348913ebc0b35650a4e240137054`；候选SHA `4e5726efe6a8f03c147eb64db33d33dbf93bb44aea780a0d34e91b30470e103e`，build=`build/cuda_case7_native_rowreduce_exp183.so`。
- **唯一假设**: 只在exp182上继续给case7的B64/split14/10页dispatch启用同native row allreduce，case12/9保持native，case13保持raw BSM，其他路径不变。
- **correctness/A-B**: CPU语义14/14；同一`.so`的GPU full/boundary/random各14/14且finite，case7精确长度`1/15/16/17/2047/2048`均PASS。初轮9×20正向exp183/exp182 p50=`0.8733`、反向exp182/exp183=`1.1430`。41×200正向=`0.8724/0.8727/0.8730`，反向=`1.1421/1.1430/1.1438`，消偏约`sqrt(0.8727/1.1430)=0.8739`，case7稳定快约12.6%。非目标case9/12/13的9×20 p50=`0.9982/1.0000/1.0000`，均中性。
- **OJ决定**: #108856为14/14 Accepted / **`61.64`**，case1–14=`3/4/10/28/22/32/255/126/255/53/303/421/255/188 μs`，分数=`92/90/82/68/67/60/52/46/55/54/45/57/48/47`。目标case7相对#108840 `283→255 μs`、`49→52分`，与本地强测同向；case4恢复一分，case8/14各波动丢一分，aggregate仍从61.50刷新到61.64。raw内嵌代码、逐提交快照和完整实验源码SHA均为`4e5726efe6a8f03c147eb64db33d33dbf93bb44aea780a0d34e91b30470e103e`，exp183/#108856成为当时baseline。

### exp184-case6-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control与唯一差异**: #108856/exp183，SHA `4e5726efe6a8f03c147eb64db33d33dbf93bb44aea780a0d34e91b30470e103e`；只把native row QK扩到B16/sync-copy case6，候选SHA `a4178c4c7361b618fac3931d1ea3ad93bd580e80d8df146433d1de3c6fed5819`。
- **结果**: 完整correctness通过，41×200双顺序消偏约`0.9213`。#108865为14/14 Accepted/61.86，case6 `32→29 μs`、`60→62分`，成为当时baseline。#108875与其字节相同而得61.79，只作为tier波动证据。

### exp185-case4-native-row16-allreduce  (OJ CONFIRMED / FORMER BASELINE, 2026-08-11)
- **父/control与唯一差异**: #108865/exp184；只给case4 B64/BSM/combined/direct-out路径启用native row QK，候选SHA `2329e3721f386e194406bccef9b5245378a717c2d96daec96f4a7cc57129a6d2`。
- **结果**: 强测正向`0.8765`、反向`1.1503`，消偏约`0.8728`；完整correctness通过。#108897为14/14 Accepted/62.07，case4 `29→24 μs`、`67→71分`。

### exp186/187-native-grouped-reducer  (MIXED, 2026-08-11)
- exp186只给case6 grouped reducer启用native max/sum，SHA `158bd1e7545cac4c429e0604013b433db8fbabd510e149cd656fac0b32c58f48`；消偏约`0.9871`，#108913 Accepted/62.00但case6仍`29 μs/62分`，不替换#108897。
- exp187只把同类替换扩到case7，SHA `15b0439bc74175b2f79d48ccad90150f58474f8f886b9c603625677b969e03ec`；消偏约`0.9992`，中性拒绝、未提交。

### exp188/189/190-native-row-QK  (OJ CONFIRMED / CURRENT BASELINE, 2026-08-11)
- exp188只给case5启用native row QK，SHA `cff011f8a48ff050f2c7b17755581f895a0492ef535d91a08c2095f5ce805feb`，消偏约`0.9259`；exp189再只给case10启用，SHA `191e3c4127769222d8d5d60e7b4cacbac35d85fecc6bc71e63158bac678243be`，消偏约`0.8765`；exp190再只给case3启用，SHA `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`，消偏约`0.9109`。
- 三个候选均完成目标精确长度，最终exp190同一`.so`的full/boundary/random全部通过。#108936为14/14 Accepted/62.57，case3/5/10=`9/19/47 μs`、`83/70/57分`，建立exp190结构性baseline；同源#108986后续以62.71刷新aggregate记录。raw、逐提交快照与exp190完整源码字节一致。

### exp191-case5-native-grouped-reducer  (OJ ACCEPTED / NO TIER, 2026-08-11)
- **父/control**: exp190/#108936；候选SHA `393d9cac5acea6610e5addd5062dc6fadb0e7d19c596906725656d05f65000b5`。
- **结果**: 只给case5 grouped reducer启用native max/sum；最终41×200正向p50=`0.9789`、反向=`1.0195`，消偏约`0.9799`。变长live-split、full/boundary/random和workspace复用通过。
- **OJ**: #108966为14/14 Accepted/62.50，case1–14=`3/4/9/24/19/29/255/126/256/47/297/424/255/188 μs`；目标case5仍`19 μs/70分`，本地收益未跨tier，不替换#108936。raw、逐提交快照与候选SHA一致。

### exp192-case11-native-halfwave-reducer  (CORRECT / NEUTRAL, 2026-08-11)
- **源码**: 在exp191上加入`native_halfwave32_allreduce/maxreduce`，修正早期误开case8的dispatch后严格只给case11 vec4 reducer使用“raw XOR-16 + native row16”的32-thread half-wave网络；最终SHA `e51a6344f64f23fbb5190ce6f71dac033378f7eb4c3707a630cf7389f0d2e244`。
- **结果**: CPU 14/14、case11 full/boundary/random和17步精确长度全部通过；9×20消偏约`0.9985`，21×100消偏约`0.9991`且区间跨1。判定中性，不提交；完整源码已归档。

### exp193-case5-raw-weight-broadcast  (CORRECT / NEUTRAL, 2026-08-11)
- **源码/假设**: 在exp191上只把case5 grouped reducer的五次权重广播从CUDA shuffle wrapper换成`raw_row16_broadcast`；source tx 0..15 均已由真实C500 probe证明raw与wrapper一致。SHA `9035afcb505deb04757bd9fe7f59188a8c22112edc803d62ed3386cd25e7c6fe`。
- **结果**: CPU 14/14，case5 full/boundary/random均PASS；9×20正向exp193/exp191 p50=`0.9947`、反向exp191/exp193=`1.0000`，消偏约`0.9973`，属于噪声。判定中性，不提交；完整源码已归档，工作文件恢复#108936。

### exp194-case11-native-lane0-softmax  (CORRECT / NEGATIVE, 2026-08-11)
- **假设/probe**: 旧exp174的lane0-softmax慢约18%，但native `mov.shfl`可能降低广播代价。官方指南指出`0x150..0x15f`为row broadcast；扩展`c500_bpermute_probe`后，真实C500逐lane证明mode `0x150`精确广播每个16-lane row的lane0。
- **结果**: 候选SHA `2638448061e06b0134e8f66b6dfc303c69e7937ea72610f2007dc76136c8d0f9`；CPU 14/14、case11 full correctness PASS，max error `2.441406e-04`。9×20 candidate/control p50=`1.1241`，稳定慢12.4%。native broadcast回收旧路径约5.6个百分点，但lane0串行依赖仍不可接受；拒绝、不提交，完整源码已归档。

### exp195/196-case11-native-QK-source-schedules  (NEGATIVE/NEUTRAL, 2026-08-11)
- exp195只把双head dot最终水平加法改为packed FP32 add，候选SHA `0c9600ef8f93e6adbac3dafd1d50d0fc973fee75b8292e7915a8c07994aa9978`；correctness通过，但双顺序消偏约`1.0284`、慢2.84%。
- exp196只交错两个head的native row shuffle与累加，资源档不变，候选SHA `a567024e9b3d16e776c4c1b55ca7710677aa97208dd739b4edd9fbde2dec2648`；双顺序消偏约`1.00045`，完全中性。两者均拒绝并归档，不能继续围绕相同source schedule微调。

### exp198/199/200-case11-int8-mma  (CORRECT BUT CLOSED, 2026-08-11)
- 独立probe证明`__builtin_mxc_mma_16x16x16i8`在C500上可用且整数结果逐元素精确。exp198将case11整页QK量化为INT8 MMA，full正确、max error=`1.495361e-03`，但p50=`1.6517`；exp199改成每个z wave独立MMA并删除CTA shared-score handoff，仍full正确且p50=`1.6985`。exp200用与`round(x*32)`对全部有限BF16编码等价的位级整数舍入，端到端进一步回退到`4.086x`。
- 结论：量化、fragment组织、MMA调用和score恢复成本远大于标量native-row QK；当前整页INT8 MMA布局关闭，不得通过量化表达式、split、loader或同一fragment ownership继续补偿。完整源码和SHA见当日实验README。

### exp201-207-case11-split-rescan  (LOCAL OPTIMUM, OJ NO TIER, 2026-08-11)
- native-row QK缩短producer后，旧split48不再可假定最优。依次扫描split39/20页、32/24页、26/30页、20/39页，exp201/202/203相邻比较约`0.9876/0.9864/0.9911`，exp204相对exp203约`1.0043`并出现拐点。回填split24/32页得到exp205；相对#108986正向p50=`0.9612`、反向=`1.0401`，消偏约`0.9613`。split22/35页和23/34页相对exp205分别回退约`1.0090/1.0122`，所以24是当前本地离散最优。
- correctness：exp205 SHA `49abb196bc955de9e3c371fc6e55b797de3c1cf635615ce1686e291c7e380f19`；full/boundary/random及`1,2,15,16,17,511,512,513,1023,1024,1025,12250,12251`全部满足OJ标准。
- OJ：#109101/exp201为14/14 Accepted/62.64，case11=`302 μs`；#109127/exp205为14/14 Accepted/62.57，case11=`308 μs`。两者均未超过#108986，split曲线保留为本地结构证据，但不能替换OJ baseline。

### exp208-case8-split32  (FAST BUT INVALID, 2026-08-11)
- **唯一差异**：在exp205上把case8从split48/6页改为split32/8页；满容量producer CTA从3072降到2048，并让reducer dispatch从`>32` vec4切换到`<=32` grouped family。候选SHA `a484711222274c7dbfc3f2086b8a454d95a3a9b4f9a4eb49ee8500eb0754148e`。
- **结果**：相对exp205的正向41×100 p50=`0.9625`、反向exp205/exp208=`1.0392`，消偏约`0.9624`。但精确L=129仅`0.897964`元素满足容差，max error=`7.202148e-02`；L=257虽达到perf标准也不能挽救该错误。严禁提交，完整源码已归档。

### exp209-case8-split33  (CORRECT / SUBMITTED #109150, 2026-08-11)
- **假设与修复**：用33个allocated split保持`ceil(256/33)=8`页、满容量仍只有32个live producer，却让case8继续走已验证的`>32` vec4 reducer。候选SHA `81bc99619f53f30e859e9ceca31bc49cf24e2f447558cb546c0099322e8b844b`，与`cuda_case8_split33_exp209.cpp`字节一致。
- **correctness**：CPU 14/14；GPU 14-case full全部PASS；case8 boundary/random、`127,128,129,255,256,257,4095,4096`及同进程`4096→129→4096→127→4095`全部100% PASS。L=129 max error降回`3.90625e-03`，确认exp208错误来自reducer家族切换而非8页producer。
- **A/B与OJ**：初轮9×20 p50=`0.9518`；41×100正向exp209/exp205=`0.9531`，反向exp205/exp209=`1.0514`，消偏`sqrt(0.9531/1.0514)=0.9521`、case8快约4.8%。dry-run通过，作为唯一在途任务提交为#109150；终态前不并发提交。

### exp210-case8-split33-on-108986  (CORRECT / LOCAL FINALIST, 2026-08-11)
- **唯一差异**：从#108986/exp190字节精确源码出发，只把case8 split48改为33；case11保持baseline split48。候选SHA `e6dc2885b2e824a35357b7ceb833a032693fc116a77cfefb9b4a41cd3db2ff0d`，与归档源码字节一致。
- **correctness/A-B**：CPU 14/14；GPU 14-case full、case8 boundary/random、`4096→129→4096→127→128→255→256→257→4095`全部100% PASS。9×20 p50=`0.9521`；41×100正向exp210/#108986=`0.9525`，反向#108986/exp210=`1.0517`，消偏约`0.9517`、快4.83%。这证明收益与case11 split24无关；#109150终态不理想时优先提交该baseline-isolated版本。

### exp211-case8-split32-explicit-vec4  (CORRECT / NEUTRAL, 2026-08-11)
- **唯一差异**：在exp210上把33个allocated split恢复为32，并在reducer dispatch显式排除case8，使它仍进入现有vec4 reducer。SHA `af1c65d33ec074f2db3f5bed3cd439ebb7c831c41fced2d8cb66bda56cc4159c`。
- **结果**：`127,128,129,255,256,257,4095,4096`全部100% PASS，直接确认exp208错误只来自grouped reducer分派。相对exp210的41×100正向p50=`1.0002`、反向exp210/exp211=`1.0012`，消偏约`0.9995`，完全中性。第33个空slot没有可测成本；保留差异更小的exp210为finalist，工作文件已恢复其SHA。

### exp212-218-case8-native-row-split-rescan  (EXP217 FINALIST, 2026-08-11)
- **动机/方法**：#109150确认split33/8页能把OJ case8 `125→123 μs`但未跨47分。固定#108986全部其他路径和case8 vec4 reducer，依次测试split26/10页、22/12页、16/16页、13/20页、11/24页，再补相邻14/19页与15/18页；每点先测对应整页边界和L=129。
- **曲线**：exp212相对exp210强测消偏约`0.9732`；exp213相对exp212快速消偏约`0.9703`；exp214相对exp213约`0.9920`；exp215相对exp214约`0.9932`。exp216的24页点转为`1.0346`回退。邻接点中exp217 split14/19页相对exp215约`0.9852`，而exp218 split15/18页相对exp217约`1.0345`，锁定split14离散甜点。
- **exp217门禁/OJ**：SHA `f5b90500cf547646f9cb3ea0bdd8a26db74fbdf9629c963de03790e6e1a3fed1`。CPU14/14；GPU 14-case full、case8 boundary/random、`4096→129→4096→303/304/305→607/608/609→4095`全部100% PASS。41×100正向exp217/#108986 p50=`0.8713`、反向#108986/exp217=`1.1508`，消偏约`0.8701`、case8快约13.0%。工作文件和完整归档字节一致；已作为唯一在途任务提交为#109180。

### exp219-223-case7-native-row-split-rescan  (EXP223 LOCAL FINALIST, 2026-08-11)
- **动机/曲线**：case7 native-row QK后仍沿用split14/10页。固定exp217其余路径，split8/16页相对exp217快速消偏约`0.9662`，split6/22页再约`0.9792`，split4/32页再约`0.9905`；split2/64页转为`1.0088`回退。邻接split3/43页相对split4的41×100消偏约`0.9978`，因此局部最优为split3。
- **exp223门禁**：SHA `318c238a3f3f8e3acb1d4006965608ca201e09cc8db0f15a07f859842f3c9513`。case7所有对应页边界PASS；14-case full、case7 boundary/random、同进程`2048→1→2048→687/688/689→1375/1376/1377→2047`全部100% PASS。41×100正向exp223/exp217 p50=`0.9344`、反向exp217/exp223=`1.0690`，消偏约`0.9349`、case7快约6.5%。当前#109180终态前不提交，工作文件与完整归档一致。

### exp224-227-case9-native-row-split-rescan  (EXP225 FINALIST, 2026-08-11)
- **动机/曲线**：固定exp223的case7 split3与其余路径，只重扫case9 native-row producer。exp224 split12/22页相对exp223消偏约`0.9557`；exp225 split8/32页相对exp224约`0.9899`；exp226 split6/43页相对exp225约`1.0000`，进入平台；exp227 split4/64页正向exp227/exp225 p50=`1.0112`，反向exp225/exp227=`0.9902`，确认低并行度拐点并拒绝。
- **exp225门禁/A-B**：SHA `ddd8ca956d179b04f37cbf9694a4788fe4b9dfcb3c27a36afe0e9b7a20e3064a`。CPU 14/14；GPU 14-case full、case9 boundary/random、同进程`4096→511→512→513→4096`全部100% PASS且finite。相对exp223的41×100正向p50=`0.9473`、反向exp223/exp225=`1.0570`，消偏约`0.9467`，case9快约5.6%。完整候选与exp227失败源码均已归档；exp225达到下一次OJ提交门槛，但#109210终态前不得并发提交。

### exp228-case9-split5  (REJECTED, 2026-08-11)
- **唯一差异/结果**：在exp225上只把case9从split8/32页改为split5/52页，补齐split6平台与split4回退之间的唯一点。页边界`831/832/833`、`1663/1664/1665`与full→short→full全部PASS；候选SHA `6a0555273b21ce331e9c6a3b5d1444199a1201206d95e94f4f803924858682b1`。
- **A/B/结论**：正向exp228/exp225 p50=`1.0300`，反向exp225/exp228=`0.9724`，消偏后稳定慢约2.9%。split5已进入低并行度悬崖，case9保留更稳健的split8；完整源码已归档，不提交。

### exp229-236-case12-native-row-split-rescan  (EXP234 SUBMITTED #109260, 2026-08-11)
- **动机/曲线**：native-row QK后case12仍沿用旧token-parallel split128/16页。固定exp225其他路径，exp229 split64/32页相对split128消偏约`0.9680`；exp231 split33/63页相对split64约`0.9786`；exp232 split24/86页转为约`1.0222`回退；exp233 split32/general/64页相对split33约`1.0128`回退；exp234 split40/52页相对split33约`0.9908`；exp235 split48/43页相对split40约`1.0093`；exp236邻接split41/50页出现显著调度悬崖，约`1.0326`。离散最优锁定split40。
- **reducer正确性边界**：exp230直接使用split32会进入`reduce_splits<=32` grouped reducer；满容量虽PASS，但L=`1025/2049`分别只有`0.355713/0.571960`元素满足容差。exp233显式保留general reducer后同样长度全部PASS，证明错误来自reducer family而非producer。case12低split候选必须排除grouped reducer；exp230 SHA `7732f4ef4d0f45a927bf98881c46059b48922fe93ba9abb21955ee1b45a85d2`，完整无效源码已归档且严禁提交。
- **exp234门禁/A-B**：SHA `3ae804f3560b69abf45184e139175285b3c4095ba93570cda9797ee828923bf8`。CPU14/14；GPU 14-case full、case12 boundary/random、`32768→831/832/833→1663/1664/1665→32768`全部100% PASS且finite。相对exp225的41×100正向p50=`0.9394`、反向exp225/exp234=`1.0659`，消偏约`0.9388`、case12本地快约6.1%。dry-run通过，已作为唯一在途任务提交#109260。

### exp237-239-case13-split-rescan  (SPLIT256 RETAINED, 2026-08-11)
- **动机**：固定exp234的case7/8/9/12及case13 K+V register-lookahead、Q预缩放、fused tail、raw-row QK和64-thread vec2 reducer，只重扫旧split256/15页两侧的离散边界。
- **exp237/split246**：仍为15页/CTA，只减少10个分配slot；SHA `aae3e60673fa99eba774a4c50afbd9512b032bd24a93349a05e3bc9a9caddcbc`。correctness通过；正向exp237/exp234 p50=`0.9985`，反向exp234/exp237=`0.9980`，消偏约`1.0003`，中性。
- **exp238/split264**：跨到14页/CTA；SHA `f6f8cb1507fa1e7038a10b06d01b04502f5e69f1853c9a7b45c991a6a2b43478`。`58966→223/224/225→447/448/449→58966`全部100% PASS。21×200正向exp238/exp234 p50=`1.0256`，反向exp234/exp238=`0.9722`，消偏约`1.0271`，稳定慢2.7%。
- **exp239/split231**：跨到16页/CTA并减少约9.8% producer/reducer slot；SHA `9dba5c4bead01f6dd2f39e47556487fd5673112cffc9358fd2d4a6d228a87fd9`。`58966→255/256/257→511/512/513→58966`全部100% PASS。21×200正向exp239/exp234 p50=`1.0019`，反向exp234/exp239=`0.9955`，消偏约`1.0032`，慢0.32%。
- **结论**：当前case13的split256/15页被同页slot缩减、14页上界和16页下界共同夹定；三个完整候选均已归档，均不提交。工作文件已字节精确恢复exp234；除非producer/reducer或ownership前提改变，不重扫同一邻域。

### exp240/241-case6-native-row-split-rescan  (SPLIT8 RETAINED, 2026-08-11)
- **动机**：旧split6/8/12曲线早于native-row QK和native grouped reducer；固定exp234其他shape，只重测4页/split下侧的split6与唯一邻点split7。
- **结果**：exp240/split6 SHA `4ce0545afcfa677d4f21ebbf729ba5683692b316a41e11899d1aca796949e231`，21×500正向exp240/exp234 p50=`1.0090`、反向exp234/exp240=`0.9950`，消偏约`1.0070`。exp241/split7 SHA `b21400e784b02c8206813231f6ccc902df7359b86778bc7df741e6d7755e1775`，正向p50=`1.0057`、反向=`0.9933`，消偏约`1.0062`。两者`362→63/64/65→127/128/129→191/192/193→361/362`均100% PASS。
- **结论**：changed precondition不足以翻转case6；split6/7分别慢0.70%/0.62%，保留split8/3页。两份完整源码已归档，不提交。

### exp242/243-case5-native-row-split-rescan  (EXP243 SUBMITTED #109312 / NOT BASELINE, 2026-08-11)
- **动机**：case5原split5/2页是在native-row QK前选定。固定exp234其他路径，exp242只改split4/3页；exp243再改split3/3页，让9个page由三个live split精确覆盖并去掉split4的空容量slot。
- **exp242**：SHA `7abea34fa2cfd409195fa1906989edd2e7ecfd47255c2da8a0b7a53eaa6c5b92`。页边界correctness全PASS；41×2000正向exp242/exp234 p50=`0.9873`、反向exp234/exp242=`1.0039`，消偏约`0.9917`，快约0.83%。
- **exp243**：SHA `e4e776951d42061433599e6f63bf5d6e00dc55af1c23f53cdcbe40828de8c5dd`。相对exp242正向p50=`0.9906`、反向exp242/exp243=`0.9926`，消偏约`0.9990`，两者中性；相对exp234正向p50=`0.9879`、反向exp234/exp243=`1.0038`，消偏约`0.9921`、快约0.8%。
- **门禁/OJ结论**：`tests/c500_case_manifest.py`已同步split3/3页；CPU14/14、同一binary的GPU full/boundary/random各14/14、case5 `141→47/48/49→95/96/97→140→141`全部100% PASS且finite，dry-run通过。#109312最终14/14 Accepted / `62.29`，case1–14=`3/4/9/24/21/29/269/121/268/47/301/446/255/186 μs`；raw、逐提交快照和实验源码SHA一致。目标case5没有兑现本地微增益，不替换baseline，同一split邻域关闭。

### exp244-case14-native-row-split241  (REJECTED, 2026-08-11)
- **唯一差异**：在exp243上只把case14从split257/15页降到split241/16页；native-row QK、head-pair/z4、K/V register-lookahead、normalized-BF16 partial、fused tail和reducer不变。SHA `601d2e9faace662c1d712013d5b054b80e35b28c610035d402d1ca2bca368baf`。
- **结果**：`61519→255/256/257→511/512/513→61518/61519`全部100% PASS。21×200正向exp244/exp243 p50=`1.0395`，反向exp243/exp244=`0.9601`，消偏约`1.0405`，稳定慢4.05%。native-row changed precondition仍未移动case14离散最优，恢复split257并关闭同一邻域；完整源码已归档，不提交。

### exp245/246-case10-native-row-split-rescan  (SPLIT128 RETAINED, 2026-08-11)
- **动机**：case10旧split64/128扫描早于native-row QK和64-thread vec2 reducer。固定exp243其他路径，exp245测试split103/5页，exp246测试split86/6页；已知split64/8页是更低并行回退点。
- **exp245**：SHA `cb61311177ddce9a8014195c91634c53e03427850a0a4b0bba3f018339145b7c`；5页边界correctness全PASS。41×1000正向exp245/exp243 p50=`0.9907`，反向exp243/exp245=`0.9908`，消偏约`0.99995`，完全中性。
- **exp246**：SHA `ca648d48366d937618794475c0a9cb4cacb55eed9b257c8405fdff79c8c67c0d`；6页边界correctness全PASS。41×1000正向exp246/exp243 p50=`1.0684`，反向exp243/exp246=`0.9208`，消偏约`1.0772`，稳定慢7.7%。
- **结论**：当前曲线为split128/4页最佳、103/5页中性、86/6页进入明显悬崖、旧64/8页更慢；不继续插值或重扫。两份源码已归档，工作文件字节恢复exp243。

### submission-109210-exp223  (ACCEPTED / NOT BASELINE, 2026-08-11)
- **结果/归档**：14/14 Accepted / `62.43`，case1–14=`3/4/9/25/19/29/268/121/255/47/300/422/255/187 μs`。raw、逐提交快照和exp223 SHA均为`318c238a3f3f8e3acb1d4006965608ca201e09cc8db0f15a07f859842f3c9513`。
- **判定**：目标case7相对#109180 `255→268 μs`、`52→51分`，未兑现本地约6.5%收益；case4/9/14等无源码差异项也发生tier波动。保持#108986最高指针，不把单轮OJ结果反向覆盖稳定本地split曲线。

### submission-109260-exp234  (ACCEPTED / NOT BASELINE, 2026-08-11)
- **结果/归档**：14/14 Accepted / `62.43`，case1–14=`3/4/9/24/19/29/274/122/263/46/302/445/255/186 μs`。raw、`solutions/archive/2026-08-11-submissions/cuda_109260.cpp`和exp234实验源码SHA均为`3ae804f3560b69abf45184e139175285b3c4095ba93570cda9797ee828923bf8`。
- **判定**：目标case12相对#109210 `422→445 μs`、`57→56分`，没有兑现本地相对exp225约6.1%的收益；case7/9也出现非目标退档。保持#108986最高指针，exp234不作为OJ baseline；终态归档完成后队列为空，允许顺序提交exp243。

### exp247-case11-fp32-shared-q  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：固定exp243的split、head-pair/z4、native-row QK、K/V register-lookahead、softmax/PV、partial和reducer；只让z0把八行Q做一次BF16→FP32转换与预缩放并写入4 KiB shared，z1–z3直接读取FP32，同时用同一道CTA barrier发布首页K/V。相对direct-Q，这会删除3/4的Q全局读取、转换和缩放，但增加shared流量与一道CTA barrier。
- **资源/correctness**：SHA `28b20b933e743c56053f3703366034c1d68c916d8a93dcdda8a2519a34550c2e`；producer从`90 MTreg/54 STreg/8320 B/5 warps`变为`86/58/12416 B/5`，0 stack且驻留档不变。case11 full以及`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite。
- **A/B/结论**：9×20正向exp247/exp243 p50=`1.0083`，反向exp243/exp247=`0.9915`，消偏约`sqrt(1.0083/0.9915)=1.0084`，稳定慢约0.84%。额外FP32 shared读写和CTA barrier超过转换/缩放节省；完整源码为`solutions/archive/2026-08-11-experiments/cuda_case11_fp32_shared_q_exp247.cpp`，不提交，工作文件字节恢复exp243。除非能消除新增barrier/shared流量，不重试同一shared-Q。

### submission-109312-exp243  (ACCEPTED / NOT BASELINE, 2026-08-11)
- **结果/归档**：14/14 Accepted / `62.29`，case1–14=`3/4/9/24/21/29/269/121/268/47/301/446/255/186 μs`。raw、`solutions/archive/2026-08-11-submissions/cuda_109312.cpp`和exp243实验源码SHA均为`e4e776951d42061433599e6f63bf5d6e00dc55af1c23f53cdcbe40828de8c5dd`。
- **判定**：目标case5相对#108986 `19→21 μs`且`70→68分`，没有兑现本地约0.8%的收益；case7/9/12也处于较慢tier。保持#108986最高指针，case5同一split邻域关闭。

### exp248-case14-fp16-packed-ml  (ACCEPTED #109339 / NOT BASELINE, 2026-08-11)
- **唯一假设**：固定exp243的case14 split257/15页、head-pair/z4、native-row QK、K/V register-lookahead、normalized-BF16 partial、fused tail和reducer CTA数，只把每split的FP32 `(m,l)` 压成原`partial_m`槽中的FP16x2；reducer首次加载时同时解包并把`l`暂存到已有shared权重区，删除`partial_l`写入和第二次全局读取。
- **资源/correctness**：SHA `c8d2df1ed09b61af210d83488b464e030ff67446f5d0aa66a0f3c560c95ef7fe`。producer保持`90 MTreg/8320 B/5 warps`且STreg `54→50`；reducer为`40 MTreg/32 STreg/0 B/8 warps`，均0 stack。CPU14/14、GPU full/boundary/random各14/14，case14同进程`61519→1/15/16/17→239/240/241→255/256/257→479/480/481→61518/61519`全部100% PASS且finite。
- **A/B/OJ**：21×200正向exp248/exp243 p50=`0.9941`、反向exp243/exp248=`1.0041`，消偏约`0.9950`、case14快约0.5%。#109339最终14/14 Accepted / `62.21`，case1–14=`3/4/9/25/21/29/272/120/266/46/302/444/255/187 μs`；raw、逐提交快照和实验源码SHA一致。目标case14未兑现微增益，不替换baseline。

### exp249-case14-register-packed-ml  (CORRECT / INCLUDED IN EXP250, 2026-08-11)
- **唯一假设**：固定exp248的producer、FP16x2 metadata、split257/15页、normalized-BF16 acc与最终acc循环；只让128个reducer线程各自把2组、tid0额外1组packed `(m,l)` 跨max归约保存在寄存器并直接生成权重，删除`s_m`和临时`s_l`的shared写读，同时把动态shared从`(2*257+4)*4`降到`(257+4)*4`字节。
- **资源/correctness**：SHA `b9323c3b2a13995aa2ddb091b18e2a0dc4e56f4e23f13be0d627911303f7a16c`。case14 reducer仍为`40 MTreg/32 STreg/0 stack/staticMaxWarps=8`，未跨资源档。CPU14/14、GPU full/boundary/random各14/14，case14同进程`61519→1/15/16/17→239/240/241→255/256/257→479/480/481→61518/61519`全部100% PASS且finite。
- **A/B/结论**：21×200正向exp249/exp248 p50=`0.9901`、反向exp248/exp249=`1.0055`，消偏约`0.9923`、在exp248上再快约0.77%；相对exp243组合约`0.9873`、case14快约1.27%。完整源码已归档，机制保留在exp250中。

### exp250-case13-fp16-packed-ml  (ACCEPTED #109369 / NOT BASELINE, 2026-08-11)
- **唯一假设**：固定exp249全部路径，只给case13的B1/split256/FP32-acc producer和64-thread vec2 reducer增加FP16x2 `(m,l)`；删除`partial_l`写入与第二次读取，split、K/V lookahead、QK/PV、acc partial和reducer数学不变。
- **资源/correctness**：SHA `0b53821d68d04387163fe6678e03819846faf86d6f8a236ad2968a1449eefd4f`。producer保持`64 MTreg/8192 B/8 warps`且STreg `50→48`；vec2 reducer保持`38/39/0 B/8 warps`，均0 stack。CPU14/14、GPU full/boundary/random各14/14，case13同进程`58966→1/15/16/17→239/240/241→479/480/481→58965/58966`全部100% PASS且finite。
- **A/B/OJ**：21×200正向exp250/exp249 p50=`0.9947`、反向exp249/exp250=`1.0025`，消偏约`sqrt(0.9947/1.0025)=0.9961`、case13快约0.39%。#109369最终14/14 Accepted / `62.07`，case1–14=`3/4/9/25/21/29/270/122/268/47/301/451/254/184 μs`；raw、逐提交快照和实验源码SHA一致。目标case13为`254 μs/48分`，但aggregate未超过#108986，exp250不替换baseline。

### exp251-case13-register-packed-ml  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：固定exp250 producer、FP16x2 metadata、split256、QK/PV和acc归约，只让64线程vec2 reducer各自把最多4组packed `(m,l)`跨max归约保存在寄存器，删除`s_m`和临时`s_l` shared流量，并把动态shared从`(2*256+2)*4`降到`(256+2)*4`字节。
- **资源/correctness**：SHA `3cd8a6c9e94e8e096b8cdc1d10567f0da47941bb41be39adb8b451d402b11a50`；reducer为`38 MTreg/40 STreg/0 stack/staticMaxWarps=8`，只比exp250多1 STreg且未跨驻留档。case13同进程`58966→1/15/16/17→239/240/241→479/480/481→58965/58966`全部100% PASS且finite。
- **A/B/结论**：21×200正向exp251/exp250 p50=`1.0001`，反向exp250/exp251=`0.9972`，换算并消偏后exp251约`1.00145x`、慢0.15%。shared metadata并非当前case13 reducer瓶颈；候选未提交，完整源码已归档，工作文件恢复#108986/exp190。

### platform-recovery-probe-108986  (ACCEPTED / NEW AGGREGATE RECORD, 2026-08-11)
- **目的/源码**: 用户要求尝试一次真实提交确认OJ可用；提交前无在途任务。使用#108936/exp190字节精确源码，SHA `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`，不占用新实验编号，也不覆盖正在验证的exp195工作文件。
- **OJ结果**: #108986正常经历`Pending→Compiling→Running→Finished`，14/14 Accepted / `62.71`；case1–14=`3/4/9/24/19/29/255/125/257/46/302/423/256/186 μs`。平台提交、编译和评测链路可用，当前没有在途任务。
- **归因/归档**: 与#108936同字节但aggregate从`62.57→62.71`；case4/10改善、case9/11/12/13回退均只能作为timing-tier波动。它刷新真实最高记录，结构性baseline仍为exp190。raw为`results/raw/cuda_108986_raw.json`，字节精确源码为`solutions/archive/2026-08-11-submissions/cuda_108986.cpp`。

### platform-recovery-probe-108784  (ACCEPTED, NOT A NEW EXPERIMENT, 2026-08-11)
- **目的/源码**: 用户要求尝试一次真实提交以确认OJ是否恢复。提交前最近10笔均为终态且没有在途任务；工作文件与#108743字节一致，SHA为`d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`，因此本次不占用新的优化实验编号。
- **OJ结果**: #108784正常经历`Pending→Running→Finished`，14/14 Accepted / `60.14`；case1–14=`3/4/11/29/22/32/284/139/285/54/344/476/255/218 μs`。平台提交、编译和评测链路可用，当前没有在途任务。
- **归因/归档**: 与#108743完全同源，case级变化和aggregate回落只能作为timing-tier波动，baseline保持#108743/60.29。raw为`results/raw/cuda_108784_raw.json`，字节精确源码为`solutions/archive/2026-08-11-submissions/cuda_108784.cpp`；工作文件仍与#108743一致。

### platform-probe-109403  (ACCEPTED, NOT A NEW EXPERIMENT, 2026-08-11)
- **目的/源码**：用户要求尝试一次真实提交确认当前OJ可用。提交前队列为空；为避免误交尚未完成门禁的工作候选，直接提交不可变baseline `solutions/archive/2026-08-11-submissions/cuda_108986.cpp`，SHA `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`，未改动工作文件。
- **OJ结果**：#109403正常经历`Pending→Running→Finished`，14/14 Accepted / `62.64`；case1–14=`3/4/9/24/19/29/254/125/254/47/300/425/255/186 μs`。平台创建、调度和评测链路可用，终态后队列为空。
- **归因/归档**：raw、`solutions/archive/2026-08-11-submissions/cuda_109403.cpp`与#108986三方SHA完全一致；同源逐case与aggregate变化只作为timing-tier样本，不替换#108986/62.71最高指针。raw为`results/raw/cuda_109403_raw.json`。

### exp252-case11-single-wave-fp32-mma-score-tile  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：固定#108986的case11 split、K/V loader、PV、online softmax、partial和reducer，只让z0的64-thread wave用官方原生`16x16x4f32`对完整K=128做32次MMA，物化8-head×16-token FP32 score tile到已失效的K shared，再由四个z wave消费各自4-token slice。
- **资源/correctness**：SHA `9548819e33147e87f307dd76f5b93bbd69a98efa556d27e597b7f2a4942401b2`；full producer为`136 MTreg/58 STreg/8320 B/0 stack/staticMaxWarps=3`，baseline约`90/54/8320/0/5`。case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部PASS，最大tolerance ratio `0.326`且finite。
- **A/B/结论**：9×20正向exp252/#108986 p10/p50/p90=`1.6592/1.6614/1.6632`，反向#108986/exp252=`0.6007/0.6015/0.6018`，消偏约`1.662x`、稳定慢66.2%。单wave串行MMA、完整score物化、两次CTA barrier与3-warps驻留共同否定该数据流；未提交，完整源码已归档，工作文件恢复#108986。不得靠split/reducer/loader微调补偿。

### fp16-vs-bf16-native-mma-precision-probe  (NO FP16 ADVANTAGE, 2026-08-11)
- **范围**：`tests/archive/closed-backend-probes/c500_mma_f16_precision_probe.cpp/.py`在真实C500上比较FP16-input和BF16-input原生MMA，3个scale×4个seed，reference强制放在CPU以避免复用同一GPU后端。
- **结果**：两路12组最大输出差仅`1.490116e-08`；11组平均dot误差并列，1组只有数值噪声级FP16微胜。probe正常以0退出并明确报告“无一致精度优势”。这不推翻历史端到端BF16 MMA短序列NaN/大误差证据，但关闭“仅换FP16输入即可修复同布局QK精度”的前提。

### platform-probe-109431  (ACCEPTED, NOT A NEW EXPERIMENT, 2026-08-11)
- **目的/源码**：用户要求尝试一次真实提交确认当前OJ是否可用。为避免提交仍在完成本地门禁的exp253，直接提交不可变baseline `solutions/archive/2026-08-11-submissions/cuda_108986.cpp`，SHA `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`；未修改或覆盖工作文件。
- **OJ结果**：#109431正常完成14/14 Accepted / `62.50`；case1–14=`3/4/9/25/19/29/254/125/255/47/298/423/255/188 μs`。平台创建、调度和评测链路可用；终态后最近五笔提交全部完成，当前队列为空。
- **归因/归档**：raw、`solutions/archive/2026-08-11-submissions/cuda_109431.cpp`与#108986三方SHA完全一致；同源逐case与aggregate变化只作为timing-tier样本，不替换#108986/62.71最高指针。raw为`results/raw/cuda_109431_raw.json`。

### exp253-case11-native-halfrow8-producer  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：固定#108986的case11 split48、同步K/V register-lookahead、fused tail、PV、online softmax、partial和reducer，只把full producer CTA从`dim3(16,4,4)`改为`dim3(8,8,4)`。每个64-thread wave覆盖八个heads，每head连续8 lanes；QK先做安全的`lane^4`，再用两级native quad permutation完成half-row归约，不使用#104263的width-8 shuffle或跨subgroup广播。
- **资源/correctness**：SHA `c1b947a319147df0027b68d79146e9e2f109e3233a3b1f8782a9202840087dac`；producer为`90 MTreg/50 STreg/8320 B/0 stack/staticMaxWarps=5`，baseline为`90/54/8320/0/5`。CPU 14/14、case11 full以及同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部PASS，最大tolerance ratio `0.326`且finite。
- **A/B/结论**：9×20正向exp253/#108986=`1.1422/1.1428/1.1443`，反向#108986/exp253=`0.8739/0.8753/0.8760`，消偏约`1.1426x`、稳定慢14.3%。STreg减少未跨驻留档；每head维度并行减半后增加的串行向量工作和native置换成本超过八head/wave并行收益。候选未提交，完整源码已归档为`cuda_case11_halfrow8_exp253.cpp`，工作文件字节精确恢复#108986；不得以同一half-row8布局继续调split/reducer/loader。

### exp254-case11-fp16x2-row-reduction  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：保持#108986 case11的`dim3(16,4,4)`、head-pair、split48、同步K/V register-lookahead、fused tail、PV、online softmax、partial和reducer不变；只把两个head的lane-local FP32 dot转成一个FP16x2，并在四级row reduction中用一次native shuffle和一次packed half add同时推进两个head。
- **资源/codegen/correctness**：SHA `1d298e4f141569b3f78c6a68895e81f1c25a2526a698dcbf669249b65ff313e8`；producer仍为`90 MTreg/54 STreg/8320 B/0 stack/staticMaxWarps=5`。目标full+tail实例静态`mov.shfl`从baseline的64次降为32次，但FP32→FP16转换插入`gethwreg/sethwreg`舍入模式控制。CPU 14/14、case11 full以及同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部PASS，最大tolerance ratio `0.326`且finite。
- **A/B/结论**：9×20正向exp254/#108986 p10/p50/p90=`1.1688/1.1703/1.1721`，反向#108986/exp254=`0.8534/0.8544/0.8554`，消偏约`sqrt(1.1703/0.8544)=1.1704`、稳定慢17.0%。shuffle减半不足以抵消FP16转换、舍入模式控制和packed half运算；候选未提交，完整源码归档为`cuda_case11_fp16x2_rowreduce_exp254.cpp`，工作文件字节精确恢复#108986。关闭同一“先降精度再打包两个head row exchange”布局。

### exp255-case11-inline-finalize  (ACCEPTED #109508 / NOT BASELINE, 2026-08-11)
- **唯一假设**：保持#108986的case11 split48 producer、QK、同步K/V register-lookahead、fused tail、softmax/PV、FP32 partial布局和数学不变，删除独立reducer kernel。每个producer写完partial后执行`__threadfence()`，再以epoch-tagged 64-bit计数器发布完成；最后一个producer CTA复用256线程在kernel内完成八head归约。短长度的inactive split仍参与计数，但finalizer只读取live split，epoch避免每次调用清零和旧状态污染。
- **资源/correctness**：SHA `3a26fd2b1fcabcc1d12d556c81adf72c2ac8db8cbbdb461ec2f3f5372f115f07`；producer从`90 MTreg/54 STreg/8320 B/5 warps`变为`90/62/8320/5`，0 stack且未跨驻留档。CPU14/14、GPU full/boundary/random各14/14；同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部PASS，数千次benchmark迭代也未出现epoch复用错误。
- **A/B/OJ**：41×200正向exp255/#108986 p50=`0.9972`，反向#108986/exp255=`1.0024`，消偏约`0.9974`、快约0.26%。#109508最终14/14 Accepted / `62.43`，case1–14=`3/4/10/24/19/29/255/125/256/46/318/425/255/188 μs`；目标case11未超过#108986的302 μs，故不替换baseline。raw、提交快照和实验源码SHA一致。

### exp256-case11-inline-finalize-split24  (ACCEPTED #109533 / NOT BASELINE, 2026-08-11)
- **changed precondition**：inline finalizer现在为每个producer支付一次fence/atomic并消除独立reducer launch，因此旧split48最优前提已变化。exp256只把case11改为split24/32页，其余与exp255一致；SHA `dae103e138e6be3e99fac3094e4b4fc493c9c5eb4fb9a98345aa1b8501551e87`。
- **correctness/A-B/OJ**：GPU full/boundary/random各14/14；同进程`12251→1/2/15/16/17→511/512/513→1023/1024/1025→12250/12251`全部PASS。相对exp255的9×20为`0.9549`，相对#108986的41×200正向p50=`0.9526`、反向#108986/exp256=`1.0496`，消偏约`0.9527`、本地快约4.73%（绝对p50约`504→480 μs`）。#109533最终14/14 Accepted / `62.43`，case1–14=`3/4/9/25/19/29/257/125/255/46/322/423/255/188 μs`；目标case11比#108986的302 us和#109508/exp255的318 us都慢，不替换baseline。

### exp257-case11-inline-finalize-split20  (CORRECT / REJECTED, 2026-08-11)
- **唯一差异/结果**：只把exp256的case11 split24/32页降到split20/约39页；SHA `3c9958b978cc00ad933e206a658e16c92dbdcfac199eea9d84441e7d4c28148a`。case11 full 100% PASS，最大误差`2.441406e-04`且finite。
- **A/B/结论**：9×20正向exp257/exp256 p50=`1.0113`，反向exp256/exp257=`0.9869`，两方向一致表明split20稳定慢约1.3%。候选已完整归档，工作文件恢复exp256；当前inline-finalize split局部最优保留split24，不继续向更低split细扫。

### exp258-case11-inline-finalize-split28  (CORRECT / REJECTED, 2026-08-11)
- **唯一差异/结果**：在exp256上只把case11 split24/32页提高到split28/28页，SHA `e1bc502412898d8a9dd948bd914bff50e5b1dcbda0791ec2965a7686c5a59881`。CPU14/14、case11 full 100% PASS，最大误差`2.441406e-04`且finite。
- **A/B/结论**：9×20正向exp258/exp256 p50=`1.0087`，反向exp256/exp258=`0.9906`，消偏约`1.0091`、split28慢约0.91%。结合exp257/split20慢约1.3%，split24已被上下两侧夹定；除非finalizer或producer成本前提再次改变，不重扫同一split邻域。完整源码已归档。

### exp259-case11-inline-finalize-atomic32  (CORRECT / ARCHIVED, SUPERSEDED, 2026-08-11)
- **唯一假设**：固定exp256的split24 producer、per-writer `__threadfence()`、last-CTA finalizer、partial布局和数学，只把epoch-tagged 64-bit CAS retry计数改为32-bit `atomicAdd`。最后一个CTA输出后以`atomicExch`归零；此时全部split已完成唯一一次计数，且下一次同流kernel必须等待当前kernel完成，因此无需host-side epoch和每次memset。
- **correctness**：SHA `00ccf11795bf2e951fbecaf457b45bc8726f96f50864e2ee0157f3c5a1543965`。GPU full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→511/512/513→1023/1024/1025→12250/12251`全部PASS。两轮41×200加短测累计上万次调用，无旧计数或竞态错误。
- **A/B/结论**：相对exp256，41×200正向exp259/exp256 p50=`0.9973`，反向exp256/exp259=`1.0013`，消偏约`0.9980`、快约0.20%。收益虽小但方向稳定、实现更简单；当时曾作为本地finalist，#109533未兑现更大的exp256收益后决定不提交。完整源码保留在实验归档，当前工作文件已继续到exp263。

### exp260-case11-inline-finalize-plain-reset  (CORRECT / NEUTRAL, 2026-08-11)
- **唯一差异/结果**：在exp259上只把最终CTA的counter归零从`atomicExch`改为普通global store；SHA `14e804cbbd16d9c2141dc1f0fcfa56e7a2c2eba65e62127a609d981993ab6696`。同进程反复full→short→full全部PASS。
- **A/B/结论**：9×20正向exp260/exp259 p50=`0.9992`，反向exp259/exp260=`0.9994`，消偏约`0.9999`，完全中性。保留内存语义更明确的exp259 `atomicExch`归零；exp260源码已归档，不提交。

### submission-109508-exp255  (ACCEPTED / NOT BASELINE, 2026-08-11)
- **结果/归档**：#109508在约900秒Pending/Running后正常完成，14/14 Accepted / `62.43`。raw为`results/raw/cuda_109508_raw.json`；`solutions/archive/2026-08-11-submissions/cuda_109508.cpp`与exp255实验快照SHA均为`3a26fd2b1fcabcc1d12d556c81adf72c2ac8db8cbbdb461ec2f3f5372f115f07`。
- **判定**：平台创建、调度、编译和评测链路可用，终态后队列为空。目标case11为`318 μs/43分`，未兑现split48 inline-finalizer的本地微增益；最高指针保持#108986/62.71，不据此否定changed-precondition下本地强正向的exp256。

### submission-109533-exp256  (ACCEPTED / NOT BASELINE, 2026-08-11)
- **结果/归档**：#109533正常经历Pending→Compiling→Running→Finished，14/14 Accepted / `62.43`；case1–14=`3/4/9/25/19/29/257/125/255/46/322/423/255/188 μs`。raw为`results/raw/cuda_109533_raw.json`；`solutions/archive/2026-08-11-submissions/cuda_109533.cpp`与exp256实验源码SHA均为`dae103e138e6be3e99fac3094e4b4fc493c9c5eb4fb9a98345aa1b8501551e87`。
- **判定**：split24相对exp255/split48的本地4.5%级改善没有在OJ兑现，case11反而`318→322 μs`；相对#108986仍慢20 us并少2分。inline-finalizer/split重扫路线不替换baseline，exp259的额外0.2%本地微增益不足以支持立即复投；下一结构从#108986重新分叉。

### platform-probe-109467  (ACCEPTED, NOT A NEW EXPERIMENT, 2026-08-11)
- **目的/源码**：用户要求尝试一次真实提交确认OJ能否成功。exp254已由双向A/B明确判为慢17.0%并归档，因此提交前把工作文件字节精确恢复#108986，并只提交不可变baseline；SHA `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`。
- **OJ结果**：#109467正常完成14/14 Accepted / `62.57`；case1–14=`3/4/9/25/19/29/256/125/256/47/299/424/255/186 μs`。平台创建、调度、编译和评测链路均可用；终态后队列为空。
- **归因/归档**：raw、`solutions/archive/2026-08-11-submissions/cuda_109467.cpp`、#108986与工作文件四方SHA完全一致；同源逐case与aggregate变化只作为timing-tier样本，不替换#108986/62.71最高指针。raw为`results/raw/cuda_109467_raw.json`。

### exp261-case8-corrected-group8-reducer  (ACCEPTED #109558 / NOT BASELINE, 2026-08-11)
- **唯一假设/修复**：从#108986分叉，保留exp217的case8 split14/19页 producer，把512个one-head vec4 reducer CTA改为64个eight-head grouped reducer CTA。exp208的WA根因是fused-tail producer把tail并入最后full split，而reducer仍按普通ceil规则读取live split；exp261统一采用`FUSE_TAIL_IN_LAST_SPLIT`计数，不是无假设重试。
- **correctness/A-B**：SHA `4709cbb419c927486b5ad506ea6702411fc7bd671faba5565ec75a4dba3503a1`。CPU14/14、GPU full/boundary/random各14/14；case8同进程`1/2/15/16/17/127/128/129/303/304/305/607/608/609/4095/4096`全部100% PASS，旧错误点L=129由不足90%修复为100%。资源`66 MTreg/24 STreg/0 shared/7 warps`；相对exp217消偏约`0.9959`，相对#108986 case8约`0.8654`，case11/14中性。
- **OJ/归档**：#109558正常完成14/14 Accepted / `62.57`，case1–14=`3/4/9/25/19/29/257/121/254/47/301/424/255/186 μs`。case8与#109180的121 μs持平且仍为47分，未跨tier；最高指针保持#108986。raw与`solutions/archive/2026-08-11-submissions/cuda_109558.cpp`SHA一致，exp261由该逐提交快照唯一保存。

### exp262-case8-group8-native-maxsum  (CORRECT / LOCAL POSITIVE, 2026-08-11)
- **唯一差异**：只给exp261 grouped reducer的max/sum启用native 16-lane `mov.shfl`；源码归档为`cuda_case8_group8_native_exp262.cpp`，SHA `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。
- **结果**：case8关键精确长度全部PASS。相对exp261正向p50=`0.9975`，反向exp261/exp262 p50=`1.0011`，消偏约`0.9982`、快约0.18%；收益很小但方向稳定。

### exp263-case8-group8-raw-weight-broadcast  (CORRECT / NEUTRAL, 2026-08-11)
- **唯一差异**：在exp262上增加`raw_row16_broadcast()`，将grouped reducer的14个split weight broadcast从CUDA wrapper换为已验证的row-local BSM mapping。当前工作文件、实验归档源码SHA均为`d64d3fa7a014bb9631004348da7ade6493abc900c5ac1c7345a920970fa7f0eb`。
- **correctness/A-B**：资源仍为`66 MTreg/24 STreg/0 shared/7 warps`；`129/303/304/305/607/608/609/4095/4096`全部100% PASS。41×300正向exp263/exp262 p50=`0.9992`，反向exp262/exp263=`0.9993`，消偏约`sqrt(0.9992/0.9993)=0.99995`，完全中性。候选归档、不提交，工作文件恢复exp262。

### exp264-case8-head-packed-fp32-qk  (CORRECT / REJECTED, 2026-08-11)
- **唯一假设**：只命中case8 head-pair/z4 producer；保持8次packed FP32 FMA及native row reduction精度不变，把packed accumulator从两个相邻维度改为两个query head，使每个head直接得到lane-local dot，尝试删除每token两个横向标量加法并缩短临时live range。
- **资源/correctness**：SHA `928e72e857da47921258498eef78c2914d41efd81e10b3da5934e494ceb43618`；producer从exp262约`90 MTreg`升到`92 MTreg`，保持`54 STreg/8320 B/0 stack/5 warps`。case8 `129/304/4095/4096`全部100% PASS且finite。
- **A/B/结论**：21×100正向exp264/exp262 p50=`1.0765`，反向exp262/exp264=`0.9274`，消偏约`sqrt(1.0765/0.9274)=1.0774`、稳定慢7.74%。跨head向量构造和串行依赖远超省掉的标量add，关闭该exact packed-QK数据流；完整源码已归档，工作文件恢复exp262。

### exp265-case8-inline-finalizer  (ACCEPTED #109578 / REJECTED, 2026-08-11)
- **唯一假设**：固定exp262的case8 split14/19页 producer、QK、K/V register-lookahead、fused tail、softmax/PV和FP32 partial数学，只删除独立group8 reducer launch。每个producer在partial写完后执行`__threadfence()`并对每个`(batch,kv_head)`的32-bit counter做`atomicAdd`；最后一个producer CTA复用原256线程完成八head finalization，输出后以`atomicExch`归零。case8仅有`64×14=896`个producer发布，显著少于此前case11 split48 inline-finalizer。
- **资源/correctness**：提交前源码SHA `6bfbfa9b8c89bb96caaade8419aee87d6ef02e9d413b3a4976727b370b36618a`；目标producer为`90 MTreg/60 STreg/8320 B/0 stack/5 warps`，对比exp262约`90/54/8320/0/5`，未降低驻留档。CPU14/14；GPU full/boundary/random各14/14；同进程`4096→1/2/15/16/17→129/303/304/305→607/608/609→4095/4096`全部100% PASS且finite，确认counter reset、inactive split与fused-tail live-count正确。
- **本地A/B**：21×100正向exp265/exp262 p50=`0.9819`，反向exp262/exp265=`1.0169`，消偏约`0.9826`。41×300强测正向p50=`0.9868`，反向exp262/exp265=`1.0128`，换算消偏约`sqrt(0.9868/1.0128)=0.9871`，case8稳定快约1.29%；case11/14相对#108986均为`0.9994`，中性。
- **OJ/结论**：#109578正常经历`Pending→Running→Finished`，14/14 Accepted / `62.43`；case1–14=`3/4/10/25/19/29/255/134/255/46/303/421/255/186 μs`。目标case8相对#109558从`121→134 μs`并由47掉到45分，相对#108986也慢9 μs；本地收益没有兑现。raw为`results/raw/cuda_109578_raw.json`，逐提交快照为`solutions/archive/2026-08-11-submissions/cuda_109578.cpp`且SHA一致。关闭当前case8 counter/last-producer inline-finalizer实现，不通过同一路线调split或finalizer线程布局补偿；工作文件字节精确恢复exp262，当前队列为空。

### exp262-oj-109591  (ACCEPTED / SELECTED BASELINE, 2026-08-11)
- **目的/源码**：用户要求尝试一次真实提交确认OJ能否成功；提交前队列为空，工作文件为已归档且本地正向的exp262，SHA `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。dry-run确认目标为Contest 11 / CUDA Maca C500后，仅创建一笔#109591。
- **OJ结果**：#109591正常经历`Pending→Running→Finished`，14/14 Accepted / `62.71`；case1–14=`3/4/9/24/19/29/255/121/257/46/300/424/255/186 μs`，分数=`92/90/83/71/70/62/52/47/55/58/45/57/48/48`。平台提交、调度与评测链路可用，终态后队列为空。
- **归因/归档**：case8相对#108986从`125→121 μs`且与exp261/262本地正向证据一致；总分并列真实最高，故选#109591/exp262为新baseline。raw、`solutions/archive/2026-08-11-submissions/cuda_109591.cpp`、experiments快照与工作文件四方SHA一致；#108986继续保留为exp190历史事实。
### exp266-case8/11-native-b128-shared-lds  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一假设**：从#109591/exp262分叉，只在case8/11 head-pair producer把shared K/V热循环的普通向量LDS换成沐曦native B128 shared load；split、register-lookahead、QK/PV、softmax、partial和reducer不变。SHA `c6aa27c0f3361797b3314528d2b06dd24b44ea92986bc795051f482ff7341380`。
- **结果**：资源略降且correctness通过，但case8/11交错A/B均稳定慢约0.8%。native B128 LDS没有降低当前已对齐shared访问的真实成本；候选未提交，完整源码归档为`solutions/archive/2026-08-11-experiments/cuda_case811_native_b128_lds_exp266.cpp`。

### exp267-case8/11-native-b128-v-only  (CORRECT / NEUTRAL, 2026-08-12)
- **唯一假设/结果**：在exp266诊断基础上只让V读取使用native B128、K恢复control，并移除无必要的附加fence；SHA `909317ab69058e98dbfcf9d23cc3d7f81291b710f754d88e74664c740c489e07`。case8/11 correctness通过，双顺序A/B均在噪声内，说明exp266回退不能归因到单独V读取，也没有可保留收益；未提交并完整归档。

### exp268-case8/11-native-b128-post-load-fence  (CORRECT / NEUTRAL, 2026-08-12)
- **唯一假设/结果**：只在exp267的native V B128读取后增加最小post-load fence，检查后端依赖调度；SHA `4cb7252f3c3797aff2efa4e1b8d3381ac2a71f7d0715131e74b1a818928ca0f2`。case8中性，case11约快0.07%，远小于本地噪声和OJ tier；不提交。native B128 shared-load家族在当前case8/11数据流上关闭，除非shared布局或consumer ownership改变。

### exp269-case8/11-native-b128-register-pipeline  (CORRECT / NEUTRAL, 2026-08-12)
- **唯一假设/结果**：把native B128限定到已经采用register-lookahead的page pipeline，避免与旧同步加载前提混淆；SHA `4d55a7cde6de458074b6a6c06c3b5cb2fc532370ee2d632828a361847b9ec96a`。case8/11完整correctness通过，双顺序A/B均中性；完整源码为`solutions/archive/2026-08-12-experiments/cuda_case811_native_pipeline_exp269.cpp`，不提交，不再做同一builtin/fence排列。

### exp270-long-kv8-uint2-load-site-combination  (CORRECT / REJECTED, 2026-08-12)
- **唯一假设**：从#109591只把此前逐shape验证过的`uint2` load-site后立即拆成标量的K/V lookahead组合到长KV8 case7/9/12/13，保持跨PV live state、split、QK、partial和reducer不变。SHA `353b915af9699656ace5e16f1ccc87bbbc8b934ff590c21bed4b426c6e228178`。
- **结果**：correctness通过；case7/9/12中性，只有case13约快0.53%。该局部收益不足以支持组合提交，尤其历史exp170–173已证明同类微增益难跨OJ tier；候选未提交，完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_longkv8_uint2_load_exp270.cpp`。

### exp271-case6-combined-kv-register-lookahead  (RESOURCE-GATE REJECTED, 2026-08-12)
- **唯一假设**：固定#109591的case6 split8、combined-tail、native-row QK、Q prescale、FP32 partial和group8 reducer，只把下一页K/V各四个scalar word跨当前PV保存在寄存器，试图合并overwrite barrier。SHA `622d9406998322d757fbdb0176cde306e7185b100bce18ba189ebe25eb362308`。
- **资源/结论**：目标producer从control约`76 MTreg/46 STreg/8320 B/0 stack/6 waves`变为`84/44/8320/0/5`，跨过关键驻留档。按预先门槛未跑GPU、未提交；完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_case6_combined_kv_lookahead_exp271.cpp`。旧case5 KV4/BSM反例虽不直接覆盖本实验，但资源事实已单独否定当前KV8/sync实现。

### exp272-case6-inline-group4-finalizer  (ACCEPTED #109630 / REJECTED AS BASELINE, 2026-08-12)
- **唯一假设**：profile显示#109591 case6 producer约`31.450 μs`、group8 reducer约`4.909 μs`（reducer占device时间约13.5%）。保持split8 producer计算、combined-tail、native-row QK、Q prescale和FP32 partial不变；每个`(batch,kv_head)`用32-bit completion counter选出最后一个producer CTA，并让其256线程按4个full-wave直接归约四个query head，删除第二次launch。SHA `30ebce6e2d0214bd97889af930be536112670ddbea02c64b1dbbeef901e8bb4b`。
- **资源/correctness**：目标实例由约`76 MTreg/6 waves`变为`72 MTreg/52 STreg/8320 B/0 stack/7 waves`。CPU14/14、GPU full/boundary/random各14/14；同进程`362→1/2/15/16/17→47/48/49→95/96/97→143/144/145→191/192/193→239/240/241→287/288/289→335/336/337→361/362`全部100% PASS且finite。非目标case4/5/7–14 A/B均在噪声内。
- **A/B/OJ**：41×500正向exp272/#109591 p50=`0.9424`，反向#109591/exp272=`1.0689`，消偏约`sqrt(0.9424/1.0689)=0.9390`、本地快约6.1%。#109630正常完成14/14 Accepted / `62.71`，case1–14=`3/4/9/25/19/30/256/120/257/46/301/420/255/186 μs`；目标case6相对#109591 `29→30 μs`、仍62分，本地收益再次未兑现。case8偶然`121→120 μs`升1分、case4 `24→25 μs`降1分而aggregate抵消，均无源码归因。raw、逐提交快照和实验源码SHA一致；不替换#109591，工作文件已恢复baseline，当前队列为空。case8/11/6三种last-producer counter finalizer均已出现本地正向但OJ目标回退，当前实现家族整体关闭。

### exp273-case6-single-split-direct-out  (CORRECT / REJECTED, 2026-08-12)
- **唯一假设/结果**：只把case6从split8+grouped reducer改为`n_split=1` direct-out，量化消除partial/reducer launch能否覆盖单CTA串行23页的代价。源码SHA `989e449206f3946249826b909bd8472a45c854139d3782f910a343a8decde8db`；目标正确性通过，但交错A/B p50=`1.5568`、慢约55.7%。case6需要split并行，不提交。

### exp274-case6-single-wave-group4-reducer  (CORRECT / REJECTED, 2026-08-12)
- **唯一假设/结果**：保持case6 split8 producer不变，只把grouped reducer改为单64-lane wave同时归约四个head。源码SHA `d320cf8245bd97003855ee62ea8cd181843b76b9edd22353ef9e28c69d9b61d5`；目标正确性通过，p50=`1.0076`、慢约0.76%。当前group8 reducer更优，不提交。

### exp275-278-case6-scalar-lookahead-envelope  (MIXED / CLOSED, 2026-08-12)
- **exp275 K-only**：只让下一页四个K scalar word跨当前PV存活；SHA `c944da893bfe6015a622588b62678a6657256458377c06183099a961acff7230`，资源`80 MTreg/44 STreg/8320 B/0 stack/6 waves`。完整正确且双向消偏约`0.9874`、快约1.26%，方向成立但不足单独跨OJ tier，未提交。
- **V插值资源门槛**：exp276增加两个V word后为`82 MTreg/5 waves`（SHA `de3ccf362554b5c92f88ff49031922e2dd1f92d413468c32cc0ff6d231565eef`）；exp277只增加一个V word仍为`82/5`（SHA `ceccfbbb9952a527a42bb61ac399a01254ae3e71a8228141b3623b9e43adaef1`）；exp278保持四个总live word但由4K换成3K+1V，因双源地址与补载生命周期恶化到`84 MTreg/5 waves`（SHA `fd844d63c42d1eaa9b8d0d503d2a2f3e4f4139dec6394df7774dfe4ccb7b2b29`）。三者按资源门槛未跑GPU、未提交；case6当前V-lookahead插值关闭。

### exp279/280-case4-tokenized-BSM-wait  (INVALID / REJECTED, 2026-08-12)
- **内建函数证据**：编译器的`memcpy_async_pred<16,...>`返回`b128vectype` use-def token，调用约定不同于`mcflashinfer::cp_async`的GVM-counter模式；`barrier_and_wait4(scope, token)`可精确等待。独立真实C500 probe连续1025次K/V覆盖与跨row读取均通过scope0，证明原语本身可用。
- **生产失败**：exp279只给case4 dual-token流水使用scope0，SHA `602e653d60e42067db59d7309d3ca0416e3f590b85fb6c70ffbff8fb825ff3d9`，资源`76 MTreg/44 STreg/8320 B/0 stack/6 waves`，但case4 full仅`0.987232` match、max error `0.7246094`。exp280唯一改scope1，SHA `251425e2be1d96e974c7f0e120b8942d143784f3e8d8ba51b8dfd8dd2af8dfc7`，match改善到`0.995392`但max error仍`0.7753906`。两者均违反正确性底线、禁止提交；scope强度不是完整根因。

### exp281-case4-ordered-tokenized-BSM  (ACCEPTED #109654 / REJECTED AS BASELINE, 2026-08-12)
- **根因与唯一差异**：在exp280上只把`wait(V_current)`移到`issue(K_next)`之前；不再跨一个未完成V token发布新K请求，但K-next仍在当前PV前发出，保留K-over-PV。源码SHA `71d1046d003b2f537ad4feb39f68a8f86c18c2452937d6dcb3cac7e0dbc44a84`，资源保持`76 MTreg/44 STreg/8320 B/0 stack/6 waves`。
- **correctness**：CPU14/14；同一`.so`的GPU full/boundary/random各14/14且finite；case4同进程`64→1/2/15/16/17→31/32/33→47/48/49→63/64`全部100% PASS。说明tokenized BSM允许K/V部分等待，但请求发布顺序必须串行retire旧V。
- **A/B与提交**：41×1000正向exp281/#109591 p50=`0.9624`，反向#109591/exp281=`1.0152`，消偏约`sqrt(0.9624/1.0152)=0.9736`、case4快约2.64%。候选具备跨1 μs tier潜力，队列为空且dry-run/SHA核对后只提交一笔#109654；等待终态期间不创建第二笔任务。
- **OJ/结论**：#109654最终14/14 Accepted / `62.57`，case1–14=`3/4/9/24/19/29/255/121/258/47/301/422/255/188 μs`。case4仍为`24 μs/71分`，没有超过#109591的24 μs；case10/14掉档来自未改源码的计时波动。raw与逐提交快照SHA一致，不替换baseline，工作文件恢复#109591后继续exp282。

### exp282-case4-ordered-tokenized-BSM-scope0  (ACCEPTED #109666 / SELECTED BASELINE, 2026-08-12)
- **changed precondition与唯一差异**：从exp281字节精确源码分叉，只把`__builtin_mxc_barrier_and_wait4(1, token)`改为scope0；请求顺序继续严格保持`wait(V_current)→issue(K_next)`。这和exp279的无序scope0不同：exp279失败已定位为旧V未退役时发布新K，而独立scope0 probe连续1025次K/V覆盖与跨row读取已通过。源码SHA `d6e8257852090cf102d57ac852b63df1ae5a7b52e8e83813bdf66efefd8388a8`。
- **资源/correctness**：资源保持`76 MTreg/44 STreg/8320 B/0 stack/6 waves`。CPU14/14；GPU full/boundary/random各14/14且finite；case4同进程`64→1/2/15/16/17→31/32/33→47/48/49→63/64`全部100% PASS。
- **A/B与提交**：相对exp281，41×1000正向exp282/exp281 p50=`0.9804`、反向exp281/exp282=`0.9962`，消偏约`0.9920`、额外快约0.8%。相对#109591，正向exp282/control=`0.9549`、反向control/exp282=`1.0253`，消偏约`0.9650`、case4本地快约3.5%。源码已完整归档并在队列为空时作为唯一任务提交#109666。
- **OJ/选择**：#109666最终14/14 Accepted / **`62.79`**，case1–14=`3/4/9/23/19/29/255/120/256/47/301/424/255/186 μs`，分数=`92/90/83/72/70/62/52/48/55/57/45/57/48/48`。唯一目标case4相对#109591真实`24→23 μs`、`71→72分`，与本地A/B同向；raw、逐提交快照、实验源码与工作文件SHA一致。选#109666为新baseline，队列终态后为空。

### exp283-case6-K-only-lookahead-on-scope0  (ACCEPTED #109672 / SELECTED BASELINE, 2026-08-12)
- **父版本/唯一差异**：从#109666/exp282字节精确源码分叉，完整保留case4有序scope0 tokenized BSM；只给case6组合exp275已独立验证的四标量K-only lookahead，V继续使用同步post-PV路径。源码SHA `0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，资源`80 MTreg/44 STreg/8320 B/0 stack/6 waves`。
- **correctness/A-B**：CPU14/14、GPU full/boundary/random各14/14以及case6共29个精确长度同进程测试全部PASS。case6正向exp283/#109666 p50=`0.9911`，反向#109666/exp283=`1.0178`，消偏约`0.9868`、快约1.32%；case4消偏约`0.9985`，中性。队列为空、dry-run与SHA核对后只提交一笔#109672。
- **OJ/选择**：#109672最终14/14 Accepted / **`62.93`**，case1–14=`3/4/9/22/19/28/254/119/256/47/304/424/255/186 μs`，分数=`92/90/83/73/70/63/52/48/55/57/45/57/48/48`。唯一目标case6相对#109666真实`29→28 μs`、`62→63分`，与本地A/B同向；case4无源码差异地`23→22 μs`仅作为timing-tier样本。raw内嵌源码、逐提交快照、实验源码与工作文件四方SHA一致。选#109672为新baseline，终态后队列为空。

### exp284-case5-ordered-tokenized-BSM  (CORRECT / NEUTRAL, 2026-08-12)
- **父版本/唯一假设**：从#109672/exp283分叉，只给case5 KV4/GQA8把GVM-counter BSM wait替换为case4已验证的有序scope0 use-def token wait；因每个z partition跨两个物理wave，在K/V精确wait后保留CTA barrier。split5、staged Q、native row QK、softmax/PV、partial和grouped reducer均不变。SHA `75ba002d3b53521e6700e75f942ee9bda8f66a914b00d02d7adc92f3fb3e15c7`。
- **资源/correctness**：目标producer与control同为`92 MTreg/48 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14；case5同进程`141→1/2/15/16/17→31/32/33→63/64/65→95/96/97→127/128/129→140/141`全部100% PASS且finite。
- **A/B/结论**：41×1000正向exp284/#109672 p50=`0.9976`，反向#109672/exp284=`0.9962`，消偏约`sqrt(0.9976/0.9962)=1.0007`、中性偏慢；未改源码的case4角色差异确认模块加载顺序仍会造成偏置。KV4补回跨wave可见性后精确token wait没有净收益；候选未提交并完整归档，工作文件字节精确恢复#109672。

### exp285-case6-native-b32-K-lookahead-load  (CORRECT / INSUFFICIENT, 2026-08-12)
- **父版本/唯一假设**：从#109672/exp283分叉，只把case6现有四标量next-K lookahead的四次普通`uint32_t` global load换成官方xcore1000示例使用的`__builtin_mxc_ldg_b32`；split8、CTA、native-row QK、K-over-PV时序、同步post-PV V路径、partial和group8 reducer不变。源码SHA `7083bba65c477644def4606a106a5d52931e17ac8a599957d49a6dd0dfe4e48c`。
- **资源/correctness**：目标producer保持`80 MTreg/44 STreg/8320 B/0 stack/6 waves`。CPU14/14、同一`.so`的GPU full/boundary/random各14/14；case6同进程`362→1/2/15/16/17→47/48/49→95/96/97→143/144/145→191/192/193→239/240/241→287/288/289→335/336/337→361/362`全部100% PASS且finite。
- **A/B/结论**：41×1000正向exp285/#109672 p50=`0.9981`，反向#109672/exp285=`1.0062`，换算消偏约`sqrt(0.9981/1.0062)=0.9960`、仅快约0.4%；正向区间仍跨1，远不足case6跨1 μs tier。候选不提交并完整归档；该结果只支持在每页执行次数更多的长KV4 register pipeline上单独验证native global load，不授权全shape展开。

### exp286-case11-native-b128-register-lookahead-load  (CORRECT / NEUTRAL, 2026-08-12)
- **父版本/唯一假设**：从#109672/exp283分叉，只把case11 head-pair/z4 register-lookahead的next-K/next-V两次普通`uint4` global load换成官方`__builtin_mxc_ldg_b128`；split48、head-pair/z4、native 16-lane QK、K/V-over-PV、fused tail、FP32 partial和reducer均保持不变，case8/10/14不启用。源码SHA `0901f5380e346fd660df11cda5da3b3ea6f6659e71923e5d8266b43b7c0ca5b2`。
- **资源/correctness**：目标producer与control同为`90 MTreg/54 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite，最大tolerance ratio `0.326`。
- **A/B/结论**：41×200正向exp286/#109672 p10/p50/p90=`0.9985/0.9990/1.0001`，反向#109672/exp286=`0.9994/0.9997/1.0001`，消偏约`sqrt(0.9990/0.9997)=0.99965`、仅快约0.035%。差异完全处于噪声且不足跨OJ tier，候选不提交；完整源码已归档为`solutions/archive/2026-08-12-experiments/cuda_case11_native_kv_ldg_exp286.cpp`，工作文件字节精确恢复#109672。当前register pipeline上的native global-load简单替换路线关闭，除非数据布局或load ownership改变。

### exp287-case11-single-wave-serial-chunks  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一架构假设**：从#109672/exp283分叉，仅替换case11 producer。一个64-thread wave仍以四个16-lane row覆盖四组head-pair、保持两头共享一次K解包、split48、native row QK、FP32 partial和原vec4 reducer，但串行处理四个4-token chunk；下一页K在当前chunk QK后发布、V在PV后发布。目标是把每split的Q读取/转换降到1/4、删除两级跨z shared-state merge，并让单-wave block利用更高occupancy。源码SHA `aa65b8c1bd60a262b34376fc8df1bd98baa3b65fe3cda0d090bb5336f8067684`。
- **资源/correctness**：编译器首次完全展开四个chunk时为`132 MTreg/3 waves`；只禁止外层展开后降到`80 MTreg/54 STreg/8192 B/0 stack/6 waves`，相对control `90/54/8320/0/5`形成预期资源优势。CPU14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite，最大tolerance ratio `0.326`。
- **A/B/结论**：9×20正向exp287/#109672 p10/p50/p90=`1.4813/1.4820/1.4829`，稳定慢约48.2%。实际active waves从control整块约4提升到6、Q setup和z merge都减少，仍完全无法覆盖四个token chunk从四wave并行变为单wave串行的critical-path增长；差异已远离噪声，无需反向长测、全量GPU门禁或OJ。完整源码已归档为`solutions/archive/2026-08-12-experiments/cuda_case11_wave_serial_exp287.cpp`，工作文件字节精确恢复#109672。case11“单wave拥有完整16-token page并串行chunk”的family关闭，不通过split、loader builtin、reducer或同一chunk大小微调补偿；新的低线程布局必须保留至少两个物理token wave并避免导出额外partial。

### exp288-case14-packed-ml-register-reducer  (OJ TARGET-POSITIVE / NO TIER, 2026-08-12)
- **父版本/唯一差异**：从#109672/exp283（`0c11bb1f...89a6`）分叉，只给case14移植旧exp248+249的FP16x2 `(m,l)` partial与寄存器化metadata reducer，不继承旧父版本其他split实验。候选SHA `01e4d5babce730f65a2ef46604f5efd1b070b85f1bec9512e8e547e76efc5985`；producer`90/52→90/50 MT/STreg`、reducer`40/36→40/32`，动态shared约减半且驻留档不变。
- **门禁/A-B**：CPU14/14、GPU full/boundary/random各14/14和23步case14 full→short→split边界→full复用全部通过。41×200正向exp288/#109672=`0.9736/0.9757/0.9780`，反向#109672/exp288=`1.0212/1.0231/1.0273`，消偏约`0.9766`、本地快2.34%；case4/8/11/13中性。
- **OJ/结论**：#109691 14/14 Accepted / 62.79，case14真实`186→183 μs`但仍48分；case8/10无源码差异地各掉1分。机制获本地和OJ目标双重确认，保留供后续finalist组合，不替换#109672、不原样复投；raw与逐提交源码已归档，工作文件恢复#109672。

### exp289-case14-stagger-next-v-after-alpha  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一假设**：从#109672/exp283分叉，保持case14 head-pair/z4、split257、native-row QK、K register-lookahead、fused tail、normalized-BF16 partial和reducer不变；只把下一页V的global load从当前QK后延到online-softmax的alpha缩放之后、当前PV之前，试图缩短V live range并保留四个PV token的延迟隐藏。候选SHA `5aef1f3949193e7fa59697dd2745162c86c68c2ab000049e8c4c0e1e080d1dbe`，完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_case14_stagger_v_after_alpha_exp289.cpp`。
- **资源/correctness**：资源从case14 control约`90 MTreg/54 STreg/8320 B/0 stack/5 waves`变为`90/56/8320/0/5`；CPU14/14，真实C500 case14 full 100% PASS，max error=`1.220703e-04`且finite。一次与correctness并发运行的性能进程已作废；最终数据均来自干净、顺序执行的测试。
- **A/B/结论**：21×100正向exp289/#109672 p50=`1.0189`，反向#109672/exp289 p50=`0.9771`，消偏约`sqrt(1.0189/0.9771)=1.0212`，稳定慢约2.1%。性能反证已充分，因此按门槛跳过full boundary/random且不提交。结合exp123在generic-z2中把next-V移到PV中点也慢约2.63%，当前register-lookahead上的V-load插入位置扫描关闭；后续必须改变producer ownership或流水前提，而不是继续挪动同一load。

### exp290-case14-fixed-15-page-hot-loop  (LOCALLY POSITIVE, 2026-08-12)
- **父版本/唯一假设**：从#109672/exp283字节精确分叉。case14满长`L=61519`时，split257/15页使前256个split恰好各处理15个full page，仅split256处理4个full page并融合tail。只给这256个common split使用“14次编译期`HAS_NEXT=true`+1次`false`”的固定trip热循环，消除每页多处动态`p+1<p_end`判断；最后split和任意短`cache_seqlens`仍走原泛化路径。split、head-pair/z4、native-row QK、K/V register-lookahead、softmax/PV、normalized-BF16 partial和reducer不变。SHA `5fb03cd095c77eb36530495ad06a08d2955c4c33e533ee82c0ac125b9bd0eb43`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case14_fixed15_hotloop_exp290.cpp`。
- **资源/correctness**：producer从control约`90/54`变为`90 MTreg/60 STreg/8320 B/0 stack/5 waves`，未跨驻留档。CPU14/14；GPU full/boundary/random各14/14；case14同进程`61519→1/2/15/16/17→239/240/241→255/256/257→479/480/481→3839/3840/3841→61518/61519`全部100% PASS且finite，确认固定分支和泛化fallback均安全。
- **A/B/结论**：41×200正向exp290/#109672 p10/p50/p90=`0.9771/0.9791/0.9827`，反向#109672/exp290=`1.0160/1.0191/1.0237`，消偏约`sqrt(0.9791/1.0191)=0.9802`、case14快约1.98%；case4/8/11/13双角色均中性。该收益独立成立，但单独约只能把186 μs推到182 μs，故不单投，进入exp291与已由#109691确认的exp288 metadata组件组合。

### exp291-case14-fixed15-plus-packed-metadata  (ACCEPTED #109699 / TARGET-POSITIVE, NO TIER, 2026-08-12)
- **组合边界**：只组合两个已经独立验证的case14机制：exp290固定15-page common-split热循环，以及exp288的FP16x2 `(m,l)` partial+register-held reducer metadata。没有改变split、CTA ownership、QK/PV数学、K/V pipeline、fused tail或normalized-BF16 accumulator。SHA `eb31c6829f3219c8f2ce98e82fe7495a62445d0360e35ac9a5b059139bb8abc1`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case14_fixed15_packed_exp291.cpp`，工作文件与其字节一致。
- **资源/门禁**：producer=`90 MTreg/58 STreg/8320 B/0 stack/5 waves`，reducer=`40/32/0/8 waves`；CPU14/14、GPU full/boundary/random各14/14，上述20步case14同进程序列全部100% PASS且finite。相对#109672的41×200正向p10/p50/p90=`0.9559/0.9575/0.9597`，反向#109672/exp291=`1.0364/1.0381/1.0401`，消偏约`sqrt(0.9575/1.0381)=0.9604`、case14稳定快约3.96%，理论时延约`186→179 μs`，具备跨下一档潜力。
- **OJ/选择**：提交前队列为空、dry-run目标与SHA核对完成，只创建一笔#109699。最终14/14 Accepted / `62.57`，case1–14=`3/4/10/23/19/29/255/121/254/47/305/425/255/180 μs`；唯一目标case14相对#109672真实`186→180 μs`、相对#109691 `183→180 μs`，与本地强正向一致，但仍为48分且距推定下一档约1 μs。case3/4/6/8/11的非目标掉档均无源码差异，aggregate因此下降；不替换#109672 baseline，也不原样复投。raw=`results/raw/cuda_109699_raw.json`、逐提交源码=`solutions/archive/2026-08-12-submissions/cuda_109699.cpp`，两份提交源码与exp291归档SHA一致。该机制保留为case14当前最快源码组件，后续只需再找稳定约0.6%以上独立收益即可尝试跨档。

### exp292-case11-fixed-16-page-hot-loop  (CORRECT / NEUTRAL, 2026-08-12)
- **changed precondition/唯一差异**：排队期间从已归档exp291分叉，只把exp290的固定-trip机制扩展到case11。full `L=12251`、split48/16页使前47个split恰好各处理16个full page；候选保留case11已验证的early-page-ID，在QK前读取确定存在的next PID，并使用“15次`HAS_NEXT=true`+1次`false`”热循环。case14 exp291、split、QK/PV、K/V pipeline、partial和reducer均不变。SHA `68588fa4cbc975e83186873014fd58bb3af37f245c6b6d5c2484d7ac085b0963`，源码为`solutions/archive/2026-08-12-experiments/cuda_case11_fixed16_hotloop_exp292.cpp`。
- **资源/correctness**：case11 producer从exp291/control的`90 MTreg/54 STreg`变为`90/56`，保持8320 B/0 stack/5 waves；CPU14/14、真实C500 case11 full 100% PASS，max error=`2.441406e-04`且finite。
- **A/B/结论**：21×100正向exp292/exp291 p50=`1.0009`，反向exp291/exp292也为`1.0009`，消偏后的exp292/control约`sqrt(1.0009/1.0009)=1.0000`，完全中性。case11的early-PID与B16并发已隐藏动态后继判断，固定16-page源码特化没有收益；跳过全量门禁、不提交，工作文件字节精确恢复exp291。该exact case11 fixed-trip关闭，不通过unroll或末页拆分继续微调。

### exp293-case10-fixed-4-page-split  (CORRECT / REJECTED, 2026-08-12)
- **唯一假设**：从已归档exp291分叉，只给case10满长`L=8192`的128个split指定固定4页`p_end`，并把`p+1<p_end`改为split内page index `<3`；任意短`cache_seqlens`继续走原动态fallback。CTA、register-lookahead、native-row QK、softmax/PV、fused-tail能力、FP32 partial和vec2 reducer均不变。SHA `df73c4d071f7e8bd7cc7425b332abb695d2ba429b5c958fb9075c7572dae4de0`，源码为`solutions/archive/2026-08-12-experiments/cuda_case10_fixed4_hotloop_exp293.cpp`。
- **资源/correctness**：目标producer约从control的`76 MTreg/54 STreg`变为`78/56`，保持8320 B/0 stack/staticMaxWarps 6；CPU14/14、真实C500 case10 full 100% PASS，max error=`2.441406e-04`且finite。
- **A/B/结论**：61×500正向exp293/exp291 p50=`1.0087`，反向exp291/exp293=`0.9832`，消偏后的exp293/control约`sqrt(1.0087/0.9832)=1.0129`，稳定慢约1.29%。四页循环过短，新增shape分支/induction与资源增量超过动态比较简化；不做全量门禁、不提交，工作文件恢复exp291。case10这一exact fixed-end/index实现关闭，不以同样源码形式继续调page count或launch。

### exp294-case14-fixed15-unroll2  (ACCEPTED #109705 / NEW BASELINE, 2026-08-12)
- **父版本/唯一差异**：从exp291字节精确分叉，只把case14固定15-page common-split循环的`#pragma unroll 1`改为`2`；其他case、split、ownership、K/V pipeline、softmax/PV、packed metadata与reducer均不变。SHA `71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case14_fixed15_unroll2_exp294.cpp`。
- **资源/门禁**：producer=`92 MTreg/58 STreg/8320 B/0 stack/5 waves`，相对exp291只增加2 MTreg、未跨驻留档。CPU14/14、GPU full/boundary/random各14/14，case14 20步full→short→split边界→full同进程复用全部100% PASS且finite。
- **A/B**：相对exp291正向p50=`0.9935`、反向exp291/exp294=`1.0034`，消偏约`0.9951`、额外快约0.49%；直接相对#109672正向=`0.9534`、反向#109672/exp294=`1.0449`，消偏约`0.9552`、快约4.48%。
- **OJ/选择**：只创建一笔#109705，正常经历`Pending→Compiling→Running→Finished`，最终14/14 Accepted / `62.93`；case1–14=`3/4/9/23/19/28/255/120/255/47/297/425/255/179 μs`。唯一目标case14相对#109672 `186→179 μs`并从48跨到49分；case4无源码差异地`22→23 μs`掉1分，因此aggregate恰好追平最高。raw、逐提交源码、实验快照和工作文件SHA完全一致；目标跨档、本地证据同向且总分保持最高，故#109705/exp294取代#109672成为当前baseline，OJ队列终态后为空。

### exp295-case14-fixed15-unroll4  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一差异**：从#109705/exp294字节精确分叉，只把case14固定15-page common-split循环的`#pragma unroll 2`改为`4`；源码SHA `ff47005771222a7b744f37ab82dcda97825cb925d8ce472cad2ee93d3d005f20`，完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_case14_fixed15_unroll4_exp295.cpp`。
- **资源/correctness**：目标producer从exp294的`92 MTreg/58 STreg/8320 B/0 stack/5 waves`膨胀到`110/58/8320/0/4`；CPU14/14、真实C500 case14 full 100% PASS，max error=`1.220703e-04`且finite。
- **A/B/结论**：21×100正向exp295/exp294 p50=`1.0038`，反向exp294/exp295=`0.9930`，消偏后的exp295/control约`sqrt(1.0038/0.9930)=1.0054`，稳定慢约0.54%。更高展开造成的寄存器与调度膨胀超过循环控制收益；不跑全量门禁、不提交，工作文件恢复#109705。unroll4及更高展开关闭；只允许再用unroll3夹定2与4之间的离散最优点。

### exp296-case14-fixed15-unroll3  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一差异**：从#109705/exp294字节精确分叉，只把case14固定15-page common-split循环的`#pragma unroll 2`改为`3`；源码SHA `c880b6195f5891db4e279679fb11d1445d8ae60ee9b700a4039ad4267ae88a75`，完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_case14_fixed15_unroll3_exp296.cpp`。
- **资源/correctness**：目标producer为`108 MTreg/58 STreg/8320 B/0 stack/4 waves`，与unroll4的`110/58/8320/0/4`几乎相同，明显高于exp294的`92/58/8320/0/5`；真实C500 case14 full 100% PASS，max error=`1.220703e-04`且finite。
- **A/B/结论**：21×100正向exp296/exp294 p50=`1.0071`，反向exp294/exp296=`0.9932`，消偏后的exp296/control约`sqrt(1.0071/0.9932)=1.0070`，稳定慢约0.70%。unroll2已经被3/4两侧负向夹定为当前离散最优；exp296不做全量门禁、不提交，工作文件恢复#109705，case14该固定循环的展开度扫描关闭。

### platform-probe-109707  (ACCEPTED / SAME-SOURCE SAMPLE, 2026-08-12)
- **目的/源码**：用户要求尝试一次真实提交以确认OJ能否成功。提交前最新任务均为终态，dry-run目标为contest 11/problem 1、`cuda.maca-c500`；工作文件与#109705/exp294字节一致，SHA均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`。只创建一笔#109707，没有并发或取消复投。
- **OJ/选择**：#109707正常经历`Pending→Running→Finished`，最终14/14 Accepted / `62.71`；case1–14=`3/4/9/23/19/33/254/120/254/46/300/426/256/179 μs`，分数=`92/90/83/72/70/59/52/48/55/58/45/57/48/49`。case14保持#109705的`179 μs/49分`，case6无源码差异地`28→33 μs`并掉4分、case10升1分，其他变化也只作为timing-tier样本。raw=`results/raw/cuda_109707_raw.json`、逐提交源码=`solutions/archive/2026-08-12-submissions/cuda_109707.cpp`，提交源码与工作文件SHA一致；不替换#109705 baseline，终态后队列为空。

### exp297-case11-wave-token-fp32-mma  (CORRECT / REJECTED, 2026-08-12)
- **changed precondition/唯一假设**：从#109705/exp294字节精确分叉，只替换case11 head-pair/z4 producer的QK。四个物理wave分别用原生`__builtin_mxc_mma_16x16x4f32`计算本wave的8-head×4-token tile；Q按`A_lane=16*k+row`压为16个非连续BF16 pair，K只由`tx<4`按`B_lane=16*k+col`从shared读取，C fragment的两个head score经已验证的`0x150..0x153`原生row broadcast直接在本wave消费。保留split48、K/V register-lookahead、early PID、fused tail、online softmax/PV、CTA内z merge、partial与reducer；因此相对exp252不再有单wave整页QK、shared score tile或CTA handoff。SHA `697c29627139b08dee4a3955981fefa4dbed5c46f612904a30d67dfae1f497c5`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case11_wave_token_fp32_mma_exp297.cpp`。
- **资源/correctness**：首版未展开16-pair循环为`68 MTreg/56 STreg/8320 B/68 B stack/7 waves`，拒绝local spill；全展开虽消除stack却变为`116/58/8320/0/4 waves`。最终用四个命名`uint4`保存Q、外层4-group循环且每组连续8次MMA，得到`84 MTreg/56 STreg/8320 B/0 stack/5 waves`，相比control `90/54/8320/0/5`保持驻留档。CPU语义14/14；真实C500 case11 full 100% PASS，`max_error=2.441406e-04`、`max_tol_ratio=0.015`、finite。
- **A/B/结论**：9×20交错初筛control p50=`0.5060 ms`、candidate=`0.9057 ms`，candidate/control p10/p50/p90=`1.7892/1.7918/1.7939`，稳定慢79.2%。这在资源同档且完全移除exp252的单producer/shared-score前提下，直接反证每wave串行32次FP32 MMA能胜过当前packed-FMA+native-row reduction；不扩展全量门禁、不提交，工作文件恢复#109705。结合case14 exp46–50和case11 exp252，当前原生FP32 MMA-QK runtime集成族关闭；只有新的更高吞吐MMA指令/后端证据或能显著减少每wave串行MMA次数的新数学分解才允许重开。

### platform-probe-109715  (ACCEPTED / SAME-SOURCE SAMPLE, 2026-08-12)
- **目的/源码**：用户要求再尝试一次真实提交确认OJ能否成功。提交前最近任务均为终态，dry-run正常识别contest 11/problem 1与`cuda.maca-c500`；工作文件与#109705/exp294字节一致，SHA均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`。只创建一笔#109715，没有并发、取消或复投。
- **OJ/选择**：#109715正常经历`Pending→Running→Finished`，最终14/14 Accepted / `62.86`；case1–14=`3/4/9/24/19/28/255/120/257/47/298/426/255/179 μs`，分数=`92/90/83/71/70/63/52/48/55/57/45/57/48/49`。相对同源#109705，case4从`23→24 μs`并掉1分，其余变化未跨得分档；仅作为timing-tier样本，不替换#109705 baseline。raw=`results/raw/cuda_109715_raw.json`、逐提交源码=`solutions/archive/2026-08-12-submissions/cuda_109715.cpp`，提交源码与工作文件SHA一致；终态后队列为空。

### exp298-case11-distributed-row-exp  (ACCEPTED #109719 / TARGET NO TIER, 2026-08-12)
- **父版本/唯一假设**：从#109705/exp294字节精确分叉，只改case11 full-page softmax权重计算。现有16-lane row已经在QK allreduce后让每个lane拥有相同的4 token×2 head logits；候选让lanes 0..3分别持有head0四个指数输入、lanes 4..7持有head1四个输入，以一次lane-varying `exp2`横向计算8个权重，再用已验证的native `0x150..0x157` row broadcast逐个分发给不变的PV。不同于exp174/194把8个exp串行压到lane0，本候选真正把8个输入映射到8 lanes；QK、alpha、K/V register-lookahead、split48、fused tail、PV、z merge、partial和reducer均不变。源码SHA `0b77acec9bd5754d61393da5d3a4d6cc86b988c72d708819c6310401a6e47577`，完整归档为`solutions/archive/2026-08-12-experiments/cuda_case11_distributed_row_exp_exp298.cpp`。
- **codegen/资源**：目标full实例的LLVM静态计数由control的`28 exp2 / 64 mov.shfl / 176 packed-FMA`变为`21 / 72 / 176`，即热循环每页准确减少7次exp2并增加8次row broadcast，QK/PV packed-FMA不变。producer从`90 MTreg/54 STreg/8320 B/0 stack/5 waves`变为`88/70/8320/0/5`，没有spill或驻留档下降。
- **correctness/A-B/OJ**：CPU14/14；GPU full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite。41×200正向exp298/#109705 p50=`0.9840`，反向#109705/exp298=`1.0154`，双角色消偏约`sqrt(0.9840/1.0154)=0.9847`、稳定快约1.53%；case4/6/8/14双角色中性。只创建#109719，最终14/14 Accepted / `62.93`，case1–14=`3/4/9/23/19/28/256/121/257/46/298/425/255/179 μs`。目标case11未超过#109705的297 μs，case8同源波动掉1分、case10升1分后aggregate并列；不替换#109705。raw与逐提交源码SHA一致，终态后队列为空；横向exp机制保留供case14等changed precondition验证。

### platform-probe-109723  (ACCEPTED / SAME-SOURCE SAMPLE, 2026-08-12)
- **目的/源码**：用户要求尝试一次真实提交确认OJ能否成功。当前工作文件仍是尚未完成验证的exp299，因此没有提交候选；提交前队列为空，dry-run正常识别contest 11/problem 1与`cuda.maca-c500`，只复投不可变的#109705快照。提交源码、raw内嵌源码与#109705的SHA均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`。
- **OJ/选择**：#109723正常经历`Pending→Running→Finished`，最终14/14 Accepted / `62.93`；case1–14=`3/4/9/23/19/28/254/121/256/46/302/424/255/179 μs`，分数=`92/90/83/72/70/63/52/47/55/58/45/57/48/49`。case14保持#109705的`179 μs/49分`，case11无源码差异地`297→302 μs`，其余变化只作为同源timing-tier样本；不替换#109705 baseline。raw=`results/raw/cuda_109723_raw.json`、逐提交源码=`solutions/archive/2026-08-12-submissions/cuda_109723.cpp`，终态后队列为空。

### exp299-case14-distributed-row-exp  (ACCEPTED #109730 / SELECTED BASELINE, 2026-08-12)
- **父版本/唯一假设**：从#109705/exp294字节精确分叉；case11恢复为原路径，只在case14满长前256个固定15-page common split中用exp298的分布式row exp，最后underfilled split和任意短长度仍走泛化路径。源码SHA `debf5a07f824f12022ebb462b9f0f0cb1b140c21feb3ac30179de9d8bd36289b`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case14_distributed_row_exp_exp299.cpp`。
- **资源/correctness/A-B**：目标producer=`90 MTreg/64 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14，case14同进程`61519→1/2/15/16/17→239/240/241→255/256/257→479/480/481→3839/3840/3841→61518/61519`全部PASS。41×200正向exp299/#109705 p50=`0.9844`，反向#109705/exp299=`1.0144`，消偏约`sqrt(0.9844/1.0144)=0.9851`、本地快约1.49%。
- **OJ/选择**：提交前队列为空且dry-run正常，只创建#109730；最终14/14 Accepted / `62.93`，case1–14=`3/4/9/23/19/28/255/120/256/47/297/424/255/177 μs`。唯一目标case14相对#109705真实`179→177 μs`但仍为49分；目标因果成立且aggregate保持最高，故#109730/exp299取代#109705成为当前baseline。raw、逐提交源码与实验归档SHA一致，终态后队列为空。

### exp300-case8-distributed-row-exp  (LOCAL-POSITIVE LEADING FINALIST, 2026-08-12)
- **父版本/唯一假设**：在exp299上只给case8 full-page head-pair/z4 specialization设置`DISTRIBUTED_ROW_EXP=true`；case14 exp299、case8 fused tail、split14/19页、K/V register-lookahead、QK、partial与grouped reducer均不变。SHA `02c5aa24bfccf636a55aa019625562bf24950407d4b56adb71ee993a0ccea492`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case8_distributed_row_exp_exp300.cpp`。
- **资源/correctness**：目标producer=`88 MTreg/70 STreg/8320 B/0 stack/5 waves`。GPU full/boundary/random各14/14；case8同进程`4096→1/2/15/16/17→95/96/97→111/112→191/192/193→303/304/305→607/608/609→4095/4096`全部PASS且finite。
- **A/B/状态**：41×300正向exp300/exp299 p50=`0.9853`，反向exp299/exp300=`1.0147`，消偏约`sqrt(0.9853/1.0147)=0.9854`、case8本地快约1.46%。证据达到提交门槛；当前作为下一笔leading finalist，提交前仍须确认队列为空并完成dry-run。

### exp301-case14-fold-alpha-into-distributed-exp  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一假设**：在exp300上只改case14固定15-page热循环；分布式row-exp已用lanes 0..7计算八个token/head权重，本轮让lanes 8/9在同一条SIMD `exp2`中计算两个head的online-softmax alpha，再row broadcast回所有维度线程。case8 exp300、split、QK、K/V pipeline、PV、partial与reducer均不变。SHA `ab1dcc19d765962eafa3b623cf63e612d218ba1cd197af9cdcbda4fe67a65109`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case14_fold_alpha_exp301.cpp`。
- **资源/correctness/A-B**：case14满长100% PASS且finite；目标producer从exp299的`90/64`变为`90/70 MT/STreg`，保持8320 B/0 stack/5 waves。41×200正向exp301/exp300 p50=`1.0059`，反向exp300/exp301=`0.9977`，消偏约`sqrt(1.0059/0.9977)=1.0041`、稳定慢约0.41%。alpha只在page max刷新时有用，而新增两次广播与状态生命周期每页付费，净收益为负；候选不做全量门禁、不提交，工作文件恢复exp300。除非能零额外广播地复用alpha，否则关闭同一spare-lane折叠。

### exp302-case8-distributed-score-ownership  (RESOURCE-GATE REJECTED, 2026-08-12)
- **父版本/唯一假设**：在exp300上只改case8 full-page score state。lanes 0..3各保留head0一个token score、lanes 4..7各保留head1一个token score，以两次native quad permutation分别归约四lane，再broadcast lane0/4得到两个page max；目标是删除每线程跨页阶段的八个score并跨到6-wave occupancy。case14、QK数学、K/V pipeline、PV、partial和reducer均不变。源码SHA `02344305dae3204916a51cf6dd948cd93494bb249258e2779e49ccc28f3bb1d4`，完整归档为`solutions/archive/2026-08-12-experiments/cuda_case8_owned_score_exp302.cpp`。
- **资源门禁/结论**：producer只从exp300的`88 MTreg/70 STreg/5 waves`变为`86/74/5`，仍为8320 B/0 stack，未跨到预设6-wave档；同时每页确定增加两次quad reduction与两次max broadcast。核心occupancy前提已被反证，因此不运行GPU correctness/A-B、不提交，工作文件恢复exp300。除非先有能把目标压到6 waves的新状态表示，否则不以同一quad4 max网络继续调owner lane或split。

### exp303-case10-distributed-token-exp  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一假设**：从exp300分叉，只给case10的KV4/GQA8 full-page producer启用分布式token exp。该16-lane row的所有lane已经持有同一head的8个score，候选由lanes 0..7各计算一个权重，再用8次native row broadcast驱动不变的V-load/PV；split128/4页、K/V register-lookahead、native-row QK、fused tail、partial和vec2 reducer不变。SHA `27f388f9b57bfce82de9f95830cc489b9747eb45cbb09f002f640b4dc3bd64f1`，完整源码为`solutions/archive/2026-08-12-experiments/cuda_case10_distributed_exp_exp303.cpp`。
- **资源/correctness/A-B**：producer=`74 MTreg/56 STreg/8320 B/0 stack/6 waves`，未降低occupancy；case10 full 100% PASS且finite。61×1000正向exp303/exp300 p50=`1.0413`，反向exp300/exp303=`0.9638`，消偏约`sqrt(1.0413/0.9638)=1.0394`、稳定慢约3.94%。单head路径原8次exp可与连续V-load/PV调度重叠，而8次广播形成更长依赖链；候选拒绝、不做全量门禁、不提交，工作文件恢复exp300。该结果关闭向更短case5/3等token-parallel GQA8路径的同类分布式exp扩展，不影响已在head-pair case14/8成立的机制。

### exp304-case8-owned-score-local-max  (ACCEPTED #109751 / SELECTED BASELINE, 2026-08-12)
- **父版本/唯一假设**：从#109736/exp300字节精确分叉；每个lane继续计算全部4 token×2 head score并本地得到两个page max，但只让lanes0..3各保留head0一个score、lanes4..7各保留head1一个score跨越QK→softmax，删除page-live `score0[4]/score1[4]`。不使用exp302的quad max网络，case14、split14、K/V pipeline、分布式exp/PV、partial和reducer均不变。SHA `018b4370cf8800fdb695186579e3e8b4e74bfa987257f89b37e40f5537cf3486`。
- **资源/correctness/A-B**：producer从exp300的`88/70`变为`86 MTreg/74 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14及case8同进程`4096→1/2/15/16/17→95/96/97→111/112→191/192/193→303/304/305→607/608/609→4095/4096`全部PASS且finite。41×300正向exp304/exp300 p50=`0.9917`、反向exp300/exp304=`1.0124`，消偏约`0.9897`、稳定快约1.03%。
- **OJ/选择**：只创建一笔#109751，正常完成14/14 Accepted / `62.93`；case1–14=`3/4/9/23/19/28/255/118/255/47/302/424/255/177 μs`。唯一目标case8相对#109736 `119→118 μs`并刷新Accepted历史最佳，case14保持177 μs；raw、逐提交快照和实验源码SHA一致。因目标与本地证据同向且aggregate保持最高，#109751/exp304取代#109736成为baseline，终态后队列为空。

### exp302-case8-distributed-score-ownership changed-precondition复诊  (CORRECT / REJECTED, 2026-08-12)
- **重开理由**：exp302最初因`86/74/5 waves`未跨occupancy档而只做资源门禁；exp304随后证明同一驻留档下缩短score live range仍可获得约1%并兑现OJ，旧门禁不足以单独排除exp302。因此使用已归档二进制对exp304重新做唯一差异比较。
- **结果/结论**：case8 full 100% PASS且finite。41×300正向exp302/exp304 p50=`1.0145`，反向exp304/exp302=`0.9899`，消偏约`sqrt(1.0145/0.9899)=1.0123`、稳定慢约1.23%。exp302为page max增加的两次quad reduction和两次broadcast明确超过其state收益；该网络关闭，不提交。

### exp305-case8-mirrored-owned-score  (LOCAL-POSITIVE LEADING FINALIST, 2026-08-12)
- **父版本/唯一假设**：从#109751/exp304分叉；lanes8..15镜像lanes0..7的owner score，真正的broadcast source仍只有lanes0..7，因此数值语义不变。owner选择由两个离散比较改为`(tx&3)==j`及`tx&4`头选择，softmax前由两段range分支改为位选择；QK、本地page max、exp数量、PV、case14和所有非case8路径不变。SHA `cdebd1580053d6b0f8c5d3b541fdafbad2d0a89e8cc0ec0f3e8c41f276fb0fc3`。
- **资源/correctness**：producer为`86 MTreg/64 STreg/8320 B/0 stack/5 waves`，相对exp304少10个STreg且驻留档不变。CPU14/14；GPU full/boundary/random各14/14；上述22步case8同进程序列全部100% PASS且finite。
- **A/B/OJ**：41×300初筛正向p50=`0.9952`、反向=`1.0090`，消偏约`0.9931`。61×500强测正向exp305/exp304=`0.9939`、反向exp304/exp305=`1.0086`，消偏约`sqrt(0.9939/1.0086)=0.9927`、稳定快约0.73%。只创建#109754，最终14/14 Accepted / `62.93`，case1–14=`3/4/9/24/19/28/257/117/254/46/302/426/255/177 μs`；目标case8 `118→117 μs`并刷新Accepted历史最佳，非目标变化按timing波动处理。raw、逐提交源码和实验归档SHA一致；#109754/exp305取代#109751成为baseline，终态后队列为空。

### exp306-case11-distributed-exp-current  (CORRECT / CONTROL DECOMPOSITION, 2026-08-12)
- **父版本/唯一假设**：从#109754/exp305分叉，只给case11重新启用exp298已验证的分布式row exp；case8 exp305、case14、QK、K/V pipeline、split48、tail、partial和reducer均不变。目的不是直接组合提交，而是先在当前源码上复现row-exp收益，再隔离exp307的owner-score增量。SHA `0b17e86d2029ad06e6da14fb0442ed58a9ababea71e28ed54ac2f1ce06eac6b5`。
- **结果**：资源`88 MTreg/70 STreg/8320 B/0 stack/5 waves`，case11 full 100% PASS。41×200正向exp306/exp305 p50=`0.9852`、反向exp305/exp306=`1.0158`，消偏约`0.9847`，与历史exp298精确一致。它作为分解control保留，不单独提交。

### exp307-case11-owned-score  (ACCEPTED #109761 / SELECTED BASELINE, 2026-08-12)
- **父版本/唯一假设**：在exp306上只给case11打开已经由case8 exp304/305证明的owner-score live-range缩减；每lane仍计算全部score和本地page max，lanes0..7作为真实权重owner，lanes8..15镜像并以tx位选择，完全不增加exp302的quad max。case8、case14、QK、K/V pipeline、split48、tail、partial和reducer不变。SHA `e953d45d8844d38e2eefb7bcc50efc0c75563ba7f1143cb3b26a636e562a22bb`。
- **资源/correctness**：case11 producer从exp306的`88/70`降到`86 MTreg/64 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite。
- **A/B/OJ**：相对exp306的41×200正反p50=`0.9835/1.0170`，消偏约`0.9832`、owner-state增量快约1.68%。直接相对#109754/exp305的61×300正向=`0.9684`、反向=`1.0322`，消偏约`sqrt(0.9684/1.0322)=0.9681`，case11稳定快约3.19%。提交前队列为空、SHA与dry-run核对通过，只创建#109761；最终14/14 Accepted / **`63.00`**，case1–14=`3/4/9/23/19/28/256/116/257/47/290/426/255/177 μs`。目标case11相对#109754 `302→290 μs`、`45→46分`并与本地证据同向；case8 116 μs和其他非目标变化按timing tier处理。raw、逐提交快照、实验源码与工作文件SHA一致，选择#109761/exp307为新baseline，终态后队列为空。

### exp308-case11-head-owned-page-max  (CORRECT / LOCAL-POSITIVE, 2026-08-12)
- **父版本/唯一假设**：从#109761/exp307分叉；native-row QK后每lane已有相同的两个head logits，因此每lane按`tx&4`只维护一个head page max，再由lane0/lane4各做一次native row broadcast。没有使用exp302的quad max网络，QK、score ownership、分布式exp、PV、partial和reducer不变。SHA `16b07e1280764923bfbdc145f3124ff197696979042127f06079f26c1c61fc11`。
- **资源/correctness/A-B**：producer保持`86 MTreg/64 STreg/8320 B/0 stack/5 waves`；CPU14/14、case11 full 100% PASS，max error=`2.441406e-04`。相对exp307正向p50=`0.9967`、反向exp307/exp308=`1.0042`，消偏约`0.9963`、快约0.37%。正向但不足单独跨tier，不提交。

### exp309-case8+11-head-owned-page-max  (CORRECT / LOCAL-POSITIVE, 2026-08-12)
- **父版本/唯一假设**：在exp308上只把同一head-owned page-max机制扩到case8 full-page producer；case11保持exp308，其他路径不变。SHA `79de67455fb1b83faedcaabd969d53713abc4b7739713c8c1af973073b648e9b`。
- **correctness/A-B**：case8 full 100% PASS，max error=`4.882812e-04`、max tolerance ratio=`0.029`。相对exp308的case8正向p50=`0.9949`、反向exp308/exp309=`1.0041`，消偏约`0.9954`、快约0.46%。直接相对#109761强测，case8正反=`0.9966/1.0026`、消偏约`0.9970`；case11正反=`0.9959/1.0033`、消偏约`0.9963`。保留为组合父版本，但case8距离`116→115 μs`约需0.86%，当前证据不足单独提交。

### exp310-case8-native-fixed14-weight-broadcast  (RESOURCE-GATE REJECTED, 2026-08-12)
- **父版本/唯一假设**：在exp309上只改case8 grouped reducer；满长14个live split各用编译期`native_row16_broadcast<SPLIT>`分发weight，短长度保留原动态shuffle fallback。SHA `8eff02addf110a62154c9cd7c911467dec4e6d83691ffc067b9f85931aa5d470`，完整源码归档为`solutions/archive/2026-08-12-experiments/cuda_case8_native_fixed14_weight_exp310.cpp`。
- **资源门禁/结论**：control reducer为`66 MTreg/24 STreg/0 shared/7 waves`；完全展开后变为`114/24/0/4`，跨过关键驻留档。按资源门禁不跑GPU correctness/A-B、不提交，工作文件恢复exp309。该exact固定14次完全展开实现关闭；只有能保留循环并维持7 waves的固定边界版本才允许重开。

### exp311-case8-rolled-group8-reducer  (CORRECT / REJECTED, 2026-08-12)
- **父版本/唯一假设**：从exp309分叉，只给case8 eight-head grouped reducer的14-split accumulator循环加`#pragma unroll 1`；weight仍用原动态`__shfl_sync`，partial布局、max/sum、FP32 FMA和producer全部不变。SHA `f64b9012716f731a73c5724ac312fd8ca0ff05fa0bd331a75e39169de5fa5774`。
- **资源/correctness**：case8 reducer从exp309的`66 MTreg/24 STreg/0 shared/7 waves`降到`34/24/0/8`，0 stack；CPU14/14、case8 full 100% PASS，max error=`4.882812e-04`。
- **A/B/结论**：41×300正向exp311/exp309 p50=`1.0141`，反向exp309/exp311=`0.9860`，换算消偏约`sqrt(1.0141/0.9860)=1.0142`、稳定慢约1.42%。更高occupancy不足以补偿rolled循环控制与动态地址依赖；不提交，工作文件恢复exp309。该exact rolled-loop实现关闭。

### exp312-case8-fixed-19-page-common-splits  (FINALIST / LOCAL-POSITIVE, 2026-08-12)
- **changed precondition/唯一假设**：从exp309分叉。case8满长`L=4096`、split14/19页时，split 0..12各恰好处理19个full page，split13只处理9页。仅给前13个common split使用18次编译期`HAS_NEXT=true`加末页`false`的固定trip循环，删除每页动态next-page判断；最后split与任意短`cache_seqlens`保留原泛化路径。exp309的case8/11 head-owned page max、owner-score、分布式exp、native QK、K/V register-lookahead、split、partial和reducer全部不变。SHA `3612a1266357f4c9da52f9e8a8124096796dea84a2e75f429194d1825476ff96`。
- **profile/资源**：exp309当前case8内存内profile为producer/reducer=`158.387/7.322 μs`，producer占约95.6%，因此固定trip针对主要瓶颈。exp312 producer为`86 MTreg/70 STreg/8320 B/0 stack/5 waves`，相对exp309只多6 STreg，MTreg与驻留档不变。
- **correctness**：CPU14/14；GPU full/boundary/random各14/14且全部finite；case8 `4096→1/2/15/16/17→303/304/305→3951/3952/3953→4095/4096`、case11 `12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`同进程复用全部100% PASS。case8满长max error=`4.882812e-04`。
- **A/B/状态**：相对exp309的41×300正向p50=`0.9918`、反向exp309/exp312=`1.0085`，消偏约`0.9917`、快约0.83%。直接相对#109761的61×500强测，case8正向=`0.9883`、反向#109761/exp312=`1.0114`，消偏约`0.9885`、快约1.15%；case11正反=`0.9957/1.0031`，消偏约`0.9963`。case8幅度超过`116→115 μs`所需约0.86%，具备真实OJ提交价值。

### exp313-case8-fixed19-unroll2  (CORRECT / LOCAL-POSITIVE, 2026-08-12)
- **父版本/唯一差异**：在已冻结并提交为#109783的exp312上，只把case8固定19页common循环从`#pragma unroll 1`改为`2`；固定分支条件、18+1页结构、producer数学、最后split fallback和所有其他case均不变。SHA `7cc405e6959b6f14225fac8db79486299fb7168bb184455aee9617f42b757bdf`。
- **资源/correctness/A-B**：producer保持`86 MTreg/70 STreg/8320 B/0 stack/5 waves`，case8 full 100% PASS，max error=`4.882812e-04`。相对exp312的41×300正向p50=`0.9968`、反向exp312/exp313=`1.0036`，消偏约`0.9966`、额外快约0.34%。#109783仍在途，不并行提交；先作为下一finalist保留。

### exp314-case8-fixed19-unroll3  (CORRECT / MARGINAL, 2026-08-12)
- **父版本/唯一差异**：在exp313上只把case8固定19页common循环从`unroll 2`改为`3`。SHA `1fcef56abf1c1a42f92613bdb74569a67707e5a0bf0ef1d02e8aea1032dd5d09`。
- **资源/correctness/A-B**：producer仍保持`86/70/8320/0/5 waves`，case8 full 100% PASS。41×300正向exp314/exp313 p50=`0.9995`、反向exp313/exp314=`1.0019`，消偏约`0.9988`、仅快约0.12%。幅度接近噪声，尚未强测或完成全量门禁，不提交；先归档，后续由更强A/B决定是否保留。

### exp315-case8-fixed19-early-pid  (CORRECT / NEUTRAL, 2026-08-12)
- **父版本/唯一差异**：在exp313上只把固定19页helper的`pid = bt_row[p + 1]`从QK之后提前到QK之前；K/V数据load、PV、page ownership、固定trip、`unroll 2`和所有其他case不变。SHA `e4e0a8e4a576bd862a8a0a31631e4f7ea86764f0bce43e13e3e6e8db9a584cf1`。
- **资源/correctness**：producer保持`86 MTreg/70 STreg/8320 B/0 stack/5 waves`；CPU14/14，真实C500 case8 full 100% PASS，max error=`4.882812e-04`。
- **A/B/结论**：相对exp313正向exp315/exp313 p50=`0.9996`，反向exp313/exp315 p50=`1.0015`，双角色消偏约`sqrt(0.9996/1.0015)=0.9991`、仅约0.09%。属于计时噪声，不完成全门禁、不提交；固定循环内early-PID精确路线关闭，归档源码为`solutions/archive/2026-08-12-experiments/cuda_case8_fixed19_earlypid_exp315.cpp`。

### exp316-case8-fixed19-block-table-cursor  (CORRECT / NEUTRAL, 2026-08-12)
- **父版本/唯一差异**：在exp313上只把固定19页helper的`bt_row[p + 1]`和外层`p_beg + page_i`改为单调`bt_cursor`；next PID仍在QK之后读取，K/V load、固定trip、`unroll 2`、数学和所有其他case不变。SHA `ada0aff0bf4933428642432ee95bda353ddfba12da2ecd27f3603999ea072026`。
- **资源/correctness**：目标producer从exp313的`86/70`变为`86 MTreg/66 STreg/8320 B/0 stack/5 waves`，证明后端确实减少地址状态但没有跨驻留档；CPU14/14，真实C500 case8 full 100% PASS，max error=`4.882812e-04`。
- **A/B/结论**：正向exp316/exp313 p50=`1.0010`，反向exp313/exp316 p50=`1.0005`，换算双角色消偏约`sqrt(1.0010/1.0005)=1.00025`，完全中性。地址计算不是当前可见瓶颈；不完成全门禁、不提交，固定循环cursor/strength-reduction精确路线关闭。源码归档为`solutions/archive/2026-08-12-experiments/cuda_case8_fixed19_cursor_exp316.cpp`。

### exp330–334-case4-fixed4-decomposition  (OJ COMPONENT CONFIRMED, 2026-08-12)
- **exp330/#109875**：混合多个shape的首空状态rescale跳过与case8 fixed19 `unroll 3`，SHA `ab08d92be6cfadb3737646a59d3069ad929515ec4fe43cbbfcc5b07d59b07d91`。14/14 Accepted / `63.07`，case4为`22 μs/73分`但case8为`116 μs/48分`；归因不纯，不换baseline。
- **exp331/#109897**：从#109783只给case4启用skip-empty，SHA `da8fdf6e692c79f9c4a31739742e366340dd93de6e6c27cec323640e3265d2ee`。本地消偏约`0.99735`，OJ 14/14 Accepted / `62.93`且case4仍23 μs；排除skip-empty为跨档主因。
- **exp332/#109933**：只给case4满长加入四页固定tokenized-BSM热循环，SHA `f47ea6174cf3f3d259c67dca250e5ff0181db44eba9dab688cf824c21b7c6de8`。本地消偏约`0.9574`，但fixed/generic共处模板使资源`76/44→76/52 MT/STreg`；OJ 14/14 Accepted / `62.86`且case4回退24 μs，原实现拒绝。
- **exp333**：只把exp332 rolled三页改为四个模板常量调用；资源仍`76/52/8320/0/6 waves`，相对exp332消偏约`1.0105`、慢约1.05%，不提交。它仅是代码生成诊断，不创建与提交快照混淆的baseline。
- **exp334/#109963**：独立`CASE4_DEDICATED`模板固定`split=0`、direct-out和满长fixed4，短长度保留安全fallback；SHA `55b2585955d6afd5b0301ca501a9da0a12742e67d88cb299b44102a493679209`，资源`74/44/8320/0/6 waves`。CPU14/14、GPU full/boundary/random各14/14以及case4 `64,1,2,15,16,17,31,32,33,47,48,49,63,64`同进程全部通过。相对#109783正反A/B=`0.9506/1.0515`，相对exp332=`0.9928`，case8=`0.9990`中性。OJ 14/14 Accepted / `63.00`，case4真实`23→22 μs`、`72→73分`；case8波动`115→116 μs`掉1分，故最高control保持#109783，但工作文件保留这一已确认case4组件。raw与`solutions/archive/2026-08-12-submissions/cuda_109963.cpp`均已归档且SHA一致，终态后队列为空。

### exp335–338-case8/layout-and-skip-empty-combination  (EXP338 ACCEPTED #110192 / SELECTED CONTROL, 2026-08-12)
- **exp335/#109989**：从#109963只把case8 fixed19循环`unroll 1→2`，SHA `86b297eed2595f93d9c3690107f12076f20e8a58833cd44ca0fa26925eb0b5a7`；本地约快0.55%，但OJ 14/14 Accepted / `62.93`，case1–14=`3/4/10/23/20/28/254/117/254/46/288/423/255/177 μs`。case4/8为`23/117 μs`，不得原样复投。
- **exp336/337**：代码布局诊断。exp336显式提前实例化case4，使修改case8后case4入口固定，但相对exp334慢约0.27%；exp337再给case4入口强制4 KiB对齐，约`1.0011x`、中性。两者均未提交；只有相关二进制，没有完整`.cpp`快照，不能冒充可复现源码归档。
- **#110031**：与#109963仅差一个空行，SHA `37548d3a30f4deb6ae8865e19a9de4e371eef9e3eccced8d6a920cb00fde235b`。15分钟watch超时后未取消、未复投，最终14/14 Accepted / `63.00`，case1–14=`3/4/10/23/19/28/255/116/253/46/292/423/255/177 μs`；只作为同源timing-tier和链路样本。
- **exp338/#110192唯一假设**：在#109963上保留case4 fixed4，只给case6/7/9/10/11/12/13/14启用skip-empty rescale；case4/5/8不变。每个split初始`l=0, acc=0`，首个有效页提升max时alpha对空状态无作用，可以严格跳过。SHA `0662e29f6f4bc09cc3abde6309d6848deacc216ece1e338930d0f7e2118dc4ca`。
- **门禁/A-B**：CPU14/14、GPU full/boundary/random各14/14；case11 `12251→1→16→17→240→241→12251`和case14 `61519→240→241→3840→3841→61519`同进程复用全部通过。新增实例0 B stack且未跨staticMaxWarps档。相对#109963双角色消偏约case6/7/9/10/11/12/13/14=`0.9947/0.9930/0.9942/0.9925/0.9970/0.9960/0.9981/0.9987`；非目标case4/8=`1.0026/1.0015`，中性。
- **OJ/选择**：#110192最终14/14 Accepted / `63.07`，case1–14=`3/4/10/22/19/28/254/117/256/46/289/421/255/176 μs`，分数=`92/90/82/73/70/63/52/48/55/58/46/57/48/49`。相对#109963，case7/9/11/12/13/14分别改善`2/3/3/2/1/1 μs`，case10 `47→46 μs`并跨一分，case6持平；未改源码的case8 `116→117 μs`按timing波动处理。即使与#109783同为63.07，#110192同时保留case4和case10得分且多个长case严格更优，因此选为默认control；工作文件、实验快照、逐提交快照与raw内嵌源码SHA一致，队列为空。下一步从#110192为case8组合exp313 `unroll 2`和exp318/319 skip-empty，并强测case4哨兵，目标追回#109783的`115 μs/49分`。

### exp339-case8-unroll2-skip-empty-on-exp338  (OJ POSITIVE COMPONENT / REJECTED AS BASELINE, 2026-08-12)
- **父版本/唯一差异**：从#110192/exp338字节精确分叉，只在case8固定19页common-split路径组合首空状态rescale跳过与`#pragma unroll 2`；其他shape、split、loader、reducer和dispatch不变。源码SHA `142482189ab69ac239a4295fc2505750857236b3b4eda4cba635a81674b897c0`，完整实验源码为`solutions/archive/2026-08-12-experiments/cuda_case8_unroll2_skip_empty_exp339.cpp`。
- **门禁/A-B**：producer保持`86 MTreg/70 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14；case8同进程`4096→1→2→15→16→17→303→304→305→3951→3952→3953→4095→4096`全部100% PASS且finite。相对#110192，case8正向p50=`0.9908`、反向control/candidate=`1.0085`，双角色消偏约`0.9912`；case4消偏约`1.0068`，case10约`1.0003`。
- **OJ/静态归因**：只创建#110229，最终14/14 Accepted / `63.00`，case1–14=`3/4/10/23/20/28/254/115/255/46/292/421/255/176 μs`，分数=`92/90/82/72/69/63/52/49/55/58/46/57/48/49`。目标case8 `117→115 μs`并跨一分，与本地A/B一致；case4/5各掉一分，总分未超过#110192，故不换baseline。设备bundle对照进一步确认case4 kernel的10424-byte机器码SHA在exp338/339中完全相同（`d35f0858...adbc`），仅因case8 kernel增长使入口从`0x53000`平移到`0x53900`；case4回退应作为代码布局/缓存现象处理，不修改其算法。raw、逐提交快照、experiments源码三方SHA一致，终态后队列为空。

### exp340b-case8-isolated-specialization  (ACCEPTED #110426 / SELECTED BASELINE, 2026-08-12)
- **父版本/唯一假设**：从#110192/exp338字节精确分叉，保留exp339已证明有效的case8 fixed19 `unroll 2` + skip-empty计算，同时隔离其代码表面。原#110192 case8特化通过合法输入不可达的volatile分支保留，新case8特化由文件末尾host launcher首次实例化；生产dispatch已关闭且永久错误的MMA-QK kernel以`#if 0`排除，死dispatch删除。源码SHA `20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。
- **静态门禁**：case4入口恢复`0x53000`、大小10424 B、机器码SHA `d35f085891ec18a19a68579bc0210f35563d51aab25abe2903f74c4d5fd7adbc`，与#110192字节精确相同。除删除MMA占位、generic fallback前移`0x100`和新增case8特化外，原39个生产kernel的地址、大小和机器码均不变。新旧case8 producer均为`86 MTreg/70 STreg/8320 B/0 stack/5 waves`。
- **correctness**：CPU14/14；GPU full/boundary/random各14/14；case8同进程`4096→1→2→15→16→17→303→304→305→3951→3952→3953→4095→4096`全部100% PASS且finite。
- **双角色 A/B**：相对#110192，case8正向candidate/control=`0.9906`、反向control/candidate=`1.0077`，消偏约`0.9914`、快约0.86%；case4/5/10约`1.0011/0.9975/0.9991`，中性。
- **OJ/选择**：只创建#110426。任务排队较久且首个1200秒watch超时，但未取消、未复投，随后正常14/14 Accepted / `63.07`；case1–14=`3/4/10/23/19/28/253/115/254/46/286/423/255/177 μs`，分数=`92/90/82/72/70/63/52/49/55/58/46/57/48/49`。case8保住`115 μs/49分`，case7/9/11改善，aggregate保持最高，故选择#110426为新baseline。raw、逐提交快照和工作文件SHA完全一致，终态后队列为空。
- **归因修正/下一步**：case4机器码和入口均与#110192相同但OJ仍为23 μs，反证“exp339的case4回退由入口平移导致”这一强因果；入口最多是相关线索，22/23 μs主要视为OJ timing-tier波动。case8代码表面隔离已完成，不再扫描地址/对齐，也不继续reducer、PID/cursor或边缘`unroll 3`微调。后续从#110426转向scalar QK、page producer、partial/writeback或真正不同producer ownership。

### exp341/342-case11-native-int8-sdot4-qk  (CORRECT / REJECTED, 2026-08-12)
- **changed precondition/唯一假设**：旧exp198/199的INT8路线量化精度正确，但16x16 MMA fragment、score tile或fragment广播使case11慢65–70%。本次保留#110426的16-lane row ownership、K/V register-lookahead、softmax/PV、z merge、partial和reducer；每lane只把已有8维Q/K量化为两个`char4`，用四次已在C500逐元素验证的`__mckl_sdot4`直接产生两head局部点积，再沿用native row16 allreduce。量化仍为`round(x*32)`并clamp到`[-127,127]`。
- **资源迭代**：exp341仅让full-page使用sdot4、tail保留FP32 QK，导致FP32/INT8 Q同时常驻，producer=`102 MTreg/64 STreg/8320 B/0 stack/4 waves`，按资源门禁拒绝。exp342让fused tail也使用同一sdot4 QK，恢复`86/64/8320/0/5 waves`，与baseline同一occupancy档；源码SHA=`de3cb1d7957f15ecfcec08e07159d786a308a0dae386e914d5ccdf71f7369c9f`。
- **correctness/A-B/结论**：case11 full 100% PASS，max error=`1.495361e-03`、max tolerance ratio=`0.093`、finite，确认打包、缩放与量化精度正确。9×20交错A/B中control/candidate p50=`0.4855/0.8243 ms`，candidate/control p10/p50/p90=`1.6928/1.6975/1.7000`，稳定慢69.8%。拒绝且不提交；证明瓶颈不是旧MMA handoff alone，运行时BF16→INT8量化与dot4的净成本本身也远高于当前packed-FMA。除非Q/K原生已是INT8或出现无量化成本的数据来源，不再重开相同sdot4路径。

### exp343–345-case11-shared-packed-integer-dot  (CORRECT / REJECTED, 2026-08-12)
- **changed precondition**：exp342让四个`ty`重复量化同一K。exp343把K量化移入loader，每个token row只做一次并以shared INT8供四个query row复用，producer=`84/64/8320 B/0 stack/5 waves`、full max error=`1.495361e-03`；9×20 ratio=`1.3633/1.3656/1.3690`。重复量化确实是成本之一，但去除后仍慢36.6%。
- **INT4预筛与exp344**：真实case11 BF16输入的fixed-scale扫描中scale 2.5可达100% tolerance内，故把每lane 8D Q/K压为一个signed INT4 packet，并用独立probe已逐元素验证的`__mckl_sdot8`。三个full seed均100% PASS，max error=`0.01224–0.01355`；资源`94/64/8320/0/5 waves`，9×20 ratio=`1.3796/1.3801/1.3812`，慢38.0%。
- **exp345 packed conversion**：唯一把通用`__float2int_rn`+clamp替换为`__builtin_mxc_cvt_pk_f32tou8(value*2.5+8)`、U8饱和后sign-bit XOR到signed INT4；资源降到`88/64/8320/0/5 waves`。seed 20260808/09/10均100% PASS，max error=`0.01318/0.01315/0.01199`；9×20 control/candidate p50=`0.4854/0.6429 ms`，ratio=`1.3226/1.3231/1.3255`，仍慢32.3%。
- **结论**：exp342→343证明K量化去重有效，exp344→345证明更窄packet与官方packed conversion也能降低部分开销，但四种正确候选全部显著慢于FP32 packed-FMA。当前瓶颈不是整数dot指令数量，而是运行时量化、打包、shared表示和整数/浮点恢复的总成本；这一族不提交并整体关闭。只有Q/K输入原生量化，或后端出现近零成本signed packed conversion时才允许重开。完整源码与SHA见当日experiments README；工作文件恢复#110426。

### oj-platform-probe-110621  (COMPILE TLE / NO CODE REGRESSION, 2026-08-12)
- **目的/源码**：用户要求尝试一次真实提交确认OJ能否成功。#110546已终态后才创建唯一一笔#110621，原样提交当前不可变baseline #110426；提交源码、raw内嵌源码、逐提交快照、工作文件与#110426 SHA均为`20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。
- **OJ结果**：#110621长时间保持Pending，首轮watch超时后没有取消或复投；后续终态为CompilationError，无测试点。raw首条消息为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有MACA `minBlocks`忽略warning，没有源码compiler error。
- **判定**：它与同源#110546构成连续两个OJ compile TLE样本，不能作为代码错误或性能数据。raw与逐提交源码已归档，当前队列为空；不创建第三笔同源探测提交，baseline保持#110426。

### backend-capability-probes-after-exp345  (DIRECTIONS CLOSED, 2026-08-12)
- **packed floating dot/FMA**：`fdot2`真实C500 capability为`f16=0 bf16=0`，没有暴露FP16/BF16乘积到FP32 accumulator的packed dot。`__builtin_mxc_pk_fma_bf16`及FP16对应入口在`xcore1000`编译阶段被拒绝，要求`xcore1500`或更高target feature；不绕过架构限制。
- **byte cast**：`b0/b1/b2/b3_cast_to_f32`对`0x01020304`输出`[4,3,2,1]`，对`0x7f80ff01`输出`[1,255,128,127]`，确认只是unsigned byte→FP32，不是BF16解包。
- **update shuffle**：full mask时`update_shfl(old, source)`与`mov_shfl(source)`逐lane一致，未选row/bank保留old；四级allreduce仍有4 shuffle+4 fadd，mov/update独立kernel同为`2 MTreg/8 STreg/0 stack/8 waves`和`0x100`机器码。它不是shuffle+add融合。
- **raw shuffle**：官方CUTE `mov_raw_shfl`对四个生产mode逐lane和四级allreduce均与`mov_shfl`一致，机器码大小同为`0x100`，但资源从普通mov的`2/8`变为raw的`3/8 MT/STreg`；LLVM仍有4次fadd。不能减少native-row QK reduction。
- **结论**：packed BF16/FP16 dot/FMA、byte-cast、`update_shfl`与`mov_raw_shfl`均不能提供当前case11所需的精确快速BF16 dot或更少的真实row-reduction指令。后续转向真正不同的scalar-QK/page-producer ownership，而不是继续换builtin名称。

### exp346-case11-two-wave-sequential-two-chunk  (CPU PASS / RESOURCE-GATE REJECTED, 2026-08-12)
- **唯一假设**：从#110426把case11 producer改为128-thread `dim3(16,4,2)`；两个物理token wave各顺序处理两个4-token chunk，保持native-row QK、head-owned score/max、distributed exp、K/V register lookahead、split/global partial数和reducer ABI，只把四路z-state merge缩为一次两路merge。它与exp287单wave整页串行不同，保留两个物理token wave。
- **验证/资源**：CPU语义14/14 PASS。rolled两chunk版为`80 MTreg/64 STreg/8192 B/48 B stack/staticMaxWarps 6`；tail改为逐token online update后资源不变，排除tail score数组是stack根因；两个chunk显式展开后反而恶化为`90/64/8192/48 B stack/5 waves`。
- **结论**：stack spill和显式展开资源恶化已经否定当前helper/codegen实现，按资源门禁不跑GPU、不提交。完整源码SHA `72328a5112613f31a3cbfc4cf3c27a62912a544c166dd72703d711a03f549fce` 已归档；只关闭该顺序双chunk原型，不把所有可证明0 stack的双wave ownership一并关闭。工作文件恢复#110426。

### exp347-case13-uint2-load-scalar-lookahead  (LOCAL POSITIVE / OJ COMPILE TLE #110699, 2026-08-13)
- **唯一假设**：从#110426只改case13现有标量K+V register-lookahead的load site；每行四次32-bit K/V load改成两次`uint2` load并立即拆回八个标量，跨当前PV仍只保留标量。其余producer数学、split256/15页、partial、reducer和dispatch不变。
- **资源/correctness**：SHA `5bacc185bb1d3cdb63961207c3b40e6adfbe3d3a6b4367b3846e49b847e9f7f1`；目标实例`64 MTreg/52 STreg/8192 B/0 stack/8 waves`。CPU14/14、GPU full/boundary/random各14/14；case13 17步full→short→page/split边界→full同进程复用全部PASS。
- **A/B**：9×20 ratio p50=`0.9932`。41×200正向exp347/#110426=`0.9940`，交换角色#110426/exp347=`1.0049`，几何消偏约`0.9946`、稳定快约0.54%，第三次在不同baseline上复现旧exp170/270机制。
- **OJ/选择**：只创建#110699；终态CompilationError且无测试点，raw首条诊断为`A TimeLimitExceeded encountered while compiling the code.`。这是连续第三次平台compile TLE，不是源码回归或性能证据。逐提交快照已归档，不立即复投，不替换#110426；工作文件恢复#110426。

### platform-probe-110740  (COMPILE TLE / SAME-SOURCE, 2026-08-13)
- **目的/源码**：用户要求再尝试一次提交。提交前队列为空，工作文件与Accepted #110426字节一致，SHA均为`20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`；只创建#110740，没有取消或并行复投。
- **OJ/判定**：长时间Pending后终态CompilationError、无测试点；raw首条仍是`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有warning。它是连续第四次平台compile TLE，不是代码回归；raw和逐提交源码已归档。

### exp348-case14-fixed15-owner-score-headmax  (OJ POSITIVE COMPONENT #110746, 2026-08-13)
- **唯一假设**：从#110426只改case14满长前256个固定15-page common split。native-row QK让16 lanes拥有重复score；候选让每lane用`tx&3`选择一个token、`tx&4`选择一个head，跨QK→PV仅保留一个owner score，同时只维护所选head的page max并由lane0/4广播。最后underfilled split、tail、split257、fixed15 `unroll 2`、K/V register-lookahead、packed metadata、normalized-BF16 partial和reducer不变。源码SHA `69f1dda419d220235e26be813962396dae01e1a33ce0580ce4ff05736a5a5bb0`。
- **资源/correctness**：producer从control的`90 MTreg/64 STreg/8320 B/0 stack/5 waves`变为`90/58/8320/0/5`。CPU14/14；GPU full/boundary/random各14/14；case14 `61519→1→2→15→16→17→239→240→241→479→480→481→3839→3840→3841→61518→61519`同进程全部PASS且finite。
- **A/B**：9×20正反p50=`0.9860/1.0189`。41×200正向exp348/#110426=`0.9845`，反向#110426/exp348=`1.0180`，几何消偏约`sqrt(0.9845/1.0180)=0.9834`、稳定快约1.66%。21×100非目标case4/8/11为`0.9993/1.0006/1.0001`，case5/10区间跨1；case14同轮`0.9870`。
- **OJ/选择**：只创建#110746；它正常通过编译并14/14 Accepted / `62.86`，case1–14=`3/4/10/24/19/28/253/117/253/47/288/422/255/174 us`。目标case14相对#110426真实`177→174 us`，与本地证据同向但仍49分；未改源码的case4/8/10各掉1分导致aggregate回退。因此exp348作为OJ确认的正组件保留，不替换#110426。raw与逐提交快照SHA一致，队列为空；下一步分解owner-score与head-owned page max贡献。

### exp349-case14-owner-score-only-decomposition  (CORRECT / DIAGNOSTIC, 2026-08-13)
- **唯一差异**：从exp348只撤回head-owned page max，恢复每lane同时维护`m_page0/m_page1`，保留single owner-score PV；相对#110426因此只剩score live-range缩减。源码SHA `f812cd485e320d752d43f5ae9abe291cb4fd7ddc65b4857c197d7eed821267a0`，完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case14_owner_score_only_exp349.cpp`。
- **资源/correctness**：目标producer仍为`90 MTreg/58 STreg/8320 B/0 stack/5 waves`；CPU14/14、case14 full 100% PASS且finite。
- **A/B/归因**：41×200正向exp349/#110426=`0.9889`，反向#110426/exp349=`1.0148`，消偏约`0.9872`、owner-score-only快约1.28%。exp348/exp349正向=`0.9981`，反向exp349/exp348=`1.0075`，消偏约`0.9953`，说明head-owned page max另贡献约0.47%。两部分乘积与exp348总收益`0.9834`一致；分解完成，不单独提交。

### exp350-case14-fixed15-first-page-empty-specialization  (RESOURCE-GATE REJECTED, 2026-08-13)
- **唯一假设**：从exp348只把每个fixed15 common split的第一页单独实例化；因`m=-inf,l=0,acc=0`，直接安装page max并删除第一次max比较及alpha-rescale控制，后14页与全部其他路径不变。源码SHA `a24856b103ea663f3753fee2363520ff532ad385981189295e97d98acf5e81f1`。
- **资源/结论**：CPU14/14，但目标producer从exp348的`90/58/8320 B/0 stack/5 waves`膨胀到`104/58/8320/0/4 waves`。单独首调用加`1..13`的奇数rolled主体破坏了原`unroll 2`代码生成，静态资源门禁失败；不跑GPU/A-B、不提交。它否定该exact实例化，不否定保持偶数展开主体的首页面向空状态表达。

### exp351-case14-fixed15-first-pair-specialization  (CORRECT / REJECTED, 2026-08-13)
- **changed precondition**：从exp348显式处理page0空状态和普通page1，剩余page2..13保持12次偶数`unroll 2`，page14仍为末页；目的在保留exp350数学优化时恢复原展开资源形态。源码SHA `09d5fc45f4864550e954d9cedc328b6795b04ae409eb1ceee2b3395fc4c2b4f0`，完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case14_first_pair_exp351.cpp`。
- **资源/correctness/A-B**：producer恢复5 waves但为`92 MTreg/58 STreg/8320 B/0 stack`，仍高于exp348的90 MTreg；case14 full 100% PASS。9×20正向exp351/exp348 p50=`1.0067`，反向exp348/exp351=`0.9931`，消偏约`1.0068`、稳定慢约0.68%。两种代码形态均失败，fixed15首页面向空状态专门化家族关闭，不提交。

### exp352–356-case13+14-combination-and-compile-surface  (ACCEPTED #110771 / NOT BASELINE, 2026-08-13)
- **exp352**：从exp348只让case14 z-state stage2写rows8–15并删除一道CTA barrier；资源不变、full正确，但双角色消偏约`1.0026`、慢0.26%，拒绝。归档SHA为`61b285a2e7e08f791fd788c3d103d8bf8020796d1428157f10ab802540b64132`，与最初测量工作源码记录`cd643a...`不一致；该记录保留为源码身份告警，复现前先做字节审计。
- **exp353/#110760**：组合case13每行两次`uint2` load-site立即拆标量与exp348 case14 owner-score/head-max；case13/14资源分别`64/52/8192/0/8 waves`和`90/58/8320/0/5`。CPU14/14、GPU full/boundary/random各14/14、case13/14精确长度和同进程workspace复用全部通过。41×200双角色消偏case13约`0.9963`、case14约`0.9834`，case4/8/10/11中性。源码SHA=`b5e12d6e6fc480100ba3ab6d51f3bee1595be41c7d4e8d096b227ad0a6b731ff`、216088 bytes；#110760在测试点前compile TLE，不能作为运行失败或性能数据。
- **exp354/355**：exp354在owner-score前提交错两个token和两个query head的QK，资源不变、case14 full正确，但41×200消偏仅`0.99885`；exp355把case13两次`uint2`变成一次`uint4`并立即拆标量，保持8 waves/0 stack，双角色消偏约`1.00045`。二者均不足提交并拒绝，SHA分别为`b4727304a50f193282ad766710da60fd0908c16e31cc00ad87ee954906abe61e`和`3eb418cdb31f695f6cb9b638a9665be5b0286c49f883ab0ca45e135d95c80dfc`。
- **exp356/#110771**：删除exp353新增的`KV8_UINT2_LOAD_SCALAR_LOOKAHEAD`模板参数，改用已有`!NATIVE_ROW16_QK && KV8_SCALAR_V_LOOKAHEAD`条件唯一识别当前case13 dispatch；运行语义、case13/14资源与A/B保持不变，源码缩到215920 bytes，SHA=`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`。重新完成CPU14/14、GPU full/boundary/random各14/14及case13 17步精确长度复用；只创建#110771，首轮900秒watch超时后不取消、不复投，随后正常14/14 Accepted / `62.93`。case1–14=`3/4/10/24/19/28/253/117/253/46/287/421/254/174 us`；case13相对#110426 `255→254 us`、case14 `177→174 us`但均未跨分，case4/8无目标差异却各掉1分。raw、逐提交快照和工作文件SHA三方一致；不替换#110426，队列终态后为空。168-byte缩减与成功编译相关但不能认定为compile TLE的唯一因果。

### exp357-case14-vector-bf16-unpack  (CORRECT / NEUTRAL, 2026-08-13)
- **唯一假设**：从exp356/#110771只修改case14 fixed15 QK的BF16解包，把标量转换换成vector widen/shift；producer ownership、fixed15循环、softmax/PV、partial和reducer均不变。源码SHA=`0418919f03b301fec9ab9e609450df19fc2dbf0b8e41ce77c3cbebcb2565a20c`。
- **资源/correctness**：CPU14/14与case14 full通过；producer保持`90 MTreg/58 STreg/8320 B/0 stack/5 waves`。
- **A/B/结论**：41×200正向exp357/exp356=`1.0010`，反向exp356/exp357=`1.0015`，几何消偏约`0.99975`，完全中性。拒绝、不提交；纯BF16解包表达式改写继续关闭。

### exp358-case14-current-vec2-reducer  (CORRECT / REJECTED, 2026-08-13)
- **changed precondition**：旧exp37之后，case14 partial已变为normalized BF16，`(m,l)`改为FP16x2 packed并将metadata寄存器化；在这一当前前提下重开64-thread、每线程2维的vec2 reducer。源码SHA=`2e009f2b887715cf739c82340157d31a594658ce01311324edb6a12307e5adba`。
- **资源/correctness**：reducer从control的`40/32`增至`52 MTreg/40 STreg`，0 stack、仍8 waves；producer保持`90/58/8320 B/0 stack/5 waves`。CPU14/14，case14 full/boundary/random及25步同进程精确长度全部通过。
- **A/B/结论**：41×200正向exp358/exp356=`1.0129`，反向exp356/exp358=`0.9880`，消偏约`1.0125`、稳定慢约1.25%。changed precondition下仍被反证，64-thread vec2 reducer路线关闭，不提交。

### exp359-case14-dual-accumulator-reducer  (CORRECT / REJECTED, 2026-08-13)
- **唯一假设**：保持128线程、normalized-BF16 partial、packed metadata和所有producer不变，只把reducer的257项accumulator FMA链拆成偶/奇两条独立链。源码SHA=`3e8544e49c82c6bc54bcccdad1524c038c632a95df134a6e683ca864af14cd23`。
- **资源/correctness**：reducer静态资源意外从`40/32`改善到`19 MTreg/32 STreg`，0 stack、仍8 waves；producer不变。CPU14/14，case14 full/boundary/random和25步精确长度复用全部通过。
- **A/B/结论**：41×200正向exp359/exp356=`1.1168`，反向exp356/exp359=`0.8963`，消偏约`1.1167`、稳定慢约11.7%。静态寄存器下降没有转化为时延，pair-loop、地址与累加调度成本显著恶化；双累加器reducer路线关闭，不提交。

### platform-probe-110809  (COMPILE TLE / SAME AS ACCEPTED SOURCE, 2026-08-13)
- **目的/源码**：用户要求尝试一次提交确认OJ能否成功。提交前队列为空，只创建#110809；源码与已14/14 Accepted的#110771/exp356字节一致，工作文件、两份逐提交快照及raw内嵌源码SHA均为`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`。
- **OJ/判定**：终态CompilationError、无测试点，首条消息为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有warning、无源码compiler error。相同源码已有Accepted事实，因此这是平台compile TLE，不是源码回归或性能数据；不取消、不立即复投，baseline保持#110426，终态后队列为空。

### pair-shuffle-codegen-probe  (NO 64-BIT SHUFFLE, 2026-08-13)
- **目的/证据**：`tests/archive/closed-backend-probes/c500_pair_shfl_codegen_probe.cpp`直接检查`__builtin_mxc_mov_shfl`能否一次交换两个FP32。`uint2`参数在编译期被拒绝，不能转换为builtin要求的`int`；`uint64_t`虽然表面可编译，但LLVM先`trunc i64 to i32`，只生成`llvm.mxc.mov.shfl.i32`，再把结果符号扩展回i64。
- **结论**：该builtin没有64-bit数据通路，`uint64_t`写法会丢失高32位，不能进入生产代码。连同compatibility wrapper把64-bit shuffle拆成两次32-bit交换的既有证据，关闭“单次shuffle搬运两个FP32”路线，除非编译器或目标架构出现新的原生接口。

### exp360-case14-head-packed-qk  (CORRECT / RESOURCE-GATE REJECTED, 2026-08-13)
- **唯一假设**：从exp356/#110771出发，只在case14 fixed15 producer中把同一K对应的两个query-head dot放入packed-FMA的两个vector槽；每个head仍保持原有偶/奇维累加顺序，softmax、PV、ownership、partial和reducer不变。源码SHA=`8bbfcab1f3c91eec2c7b22fd577149f38ddf99387f8aa1261cab00d886961a0f`。
- **correctness/资源**：CPU14/14，case14 full 100% PASS、finite，max error=`1.220703e-04`、max tolerance ratio=`0.008`。producer从control的`90 MTreg/58 STreg/8320 B/0 stack/5 waves`恶化为`102/58/8320/0/4 waves`。
- **结论**：同时保持两个head的vector Q状态导致寄存器跨驻留档，静态资源门禁已反证核心假设；不跑完整A/B、不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case14_head_packed_qk_exp360.cpp`，工作文件恢复exp356/#110771。后续scalar-QK候选必须避免扩大同时live的跨head向量状态。

### exp361-case14-sequential-head-qk  (CORRECT / REJECTED, 2026-08-13)
- **changed precondition/唯一假设**：exp360证明跨head packed vector扩大live state会跨资源档；本轮保持case14 fixed15的两头完整native-row QK和owner-score数学，只让head0的lane-local dot完成归约后再形成head1，尝试以重复BF16 K解包换取更短峰值live range。源码SHA=`b24a66d869bbcc1f6bc06997b3f2c3fb51529a670b64cbf3ece054b62a9c2aec`。
- **资源/correctness**：CPU14/14；case14 full 100% PASS、max error=`1.220703e-04`、max tolerance ratio=`0.008`、finite。producer仍为`90 MTreg/8320 B/0 stack/5 waves`，但STreg从exp356的58升到64，后端没有兑现临时状态复用。
- **A/B/结论**：相对exp356的9×50短轮交错ratio p10/p50/p90=`1.0536/1.0567/1.0625`，稳定慢约5.67%。重复K解包和串行依赖明显超过live-range假设；不扩大correctness、不提交。完整源码已归档，工作文件字节精确恢复exp356/#110771；当前两头QK的并行/顺序source schedule均关闭，下一路线切到case13独立producer组件。

### exp362-case13-uint2-shared-publish  (CORRECT / NEUTRAL, 2026-08-13)
- **changed precondition/唯一假设**：exp169的`uint2`跨PV存活使case13从8降到7 waves；exp356已经让两个`uint2` global load立即拆成八个标量并保持8 waves。本轮让标量继续跨PV，只在现有wave barrier后的shared发布点临时重组为K/V各两个`uint2` store，地址、同步和数据布局不变。源码SHA=`e02aba66c87fd68abd016d22e6626eb29484e6145254f6eebaeb4c8839b2d677`。
- **资源/correctness**：CPU14/14；case13 full 100% PASS、max error=`1.220703e-04`、max tolerance ratio=`0.008`、finite。目标实例保持`64 MTreg/52 STreg/8192 B/0 stack/8 waves`。
- **A/B/结论**：9×50正向exp362/exp356=`0.9975/1.0014/1.0064`；交换角色exp356/exp362=`0.9987/1.0024/1.0077`，几何消偏约`sqrt(1.0014/1.0024)=0.9995`，完全中性。shared store表达式没有独立可见收益；不扩大correctness、不提交，源码归档后工作文件恢复exp356。

### exp363-case14-uint4-partial-store  (CORRECT / EDGE-NEUTRAL, 2026-08-13)
- **唯一假设**：case14 normalized-BF16 partial的每个head row为256-byte对齐，每个tx写连续对齐16 bytes；保留四个`__floats2bfloat162_rn`和workspace布局，只把每头四次32-bit写表达为一次`uint4` store。源码SHA=`ca3afda47db170283e6eedf07aefdd33e8901fbb928b3a60b0b6a1a7840cbf1f`。
- **资源/correctness**：CPU14/14；case14 full 100% PASS、max error=`1.220703e-04`、max tolerance ratio=`0.008`、finite。producer保持`90 MTreg/58 STreg/8320 B/0 stack/5 waves`。
- **A/B/结论**：9×50正向exp363/exp356=`0.9952/0.9979/1.0044`；交换角色exp356/exp363=`0.9966/1.0012/1.0063`，消偏约`sqrt(0.9979/1.0012)=0.99835`，仅边缘快约0.17%且两轮区间均跨1。收益不足跨tier，不扩大强测、不提交；归档后恢复exp356。partial writeback若继续研究必须减少转换、字节或状态，不再只改store聚合语法。

### exp364-case5-fixed-two-full-pages  (CORRECT / REJECTED, 2026-08-13)
- **唯一假设/资源**：从exp356只给case5满长建立固定两整页循环；源码SHA=`e1d7fc11c10d199d974ffa0d8c283f9f986f39059c4b7a22fe5036ca70105527`。CPU14/14与case5 full通过，但producer从`92/48→94/54 MT/STreg`，仍5 waves。
- **A/B/结论**：exp364/exp356正向p50=`1.0175`，交换角色消偏后约`1.012x`、稳定慢约1.2%。固定两页代码形态关闭，不提交；完整源码已归档。

### exp365-case13-packed-ml  (LOCAL POSITIVE / COMPILE TLE #110884, 2026-08-13)
- **唯一假设**：只给case13 producer/reducer使用FP16x2 packed `(m,l)` metadata；复用已有producer编译期条件，新增packed vec2 reducer实例。源码SHA=`d18ed7ad3cbf0267c1ac896e4f86a14980eae012d1727833e667ad407b802f00`。
- **门禁/A-B**：CPU14/14、GPU full/boundary/random各14/14及case13 17步同进程复用全部通过。相对exp356 case13消偏约`0.9936`；相对#110426 case13约`0.9895`，case14约快1.4%，其余哨兵中性。
- **OJ/判定**：只创建#110884；终态CompilationError且无测试点，首条诊断为`A TimeLimitExceeded encountered while compiling the code.`。raw、逐提交快照与提交源码SHA一致；这是平台compile TLE，不是性能失败，baseline保持#110426。

### exp366-case13-packed-ml-runtime-reducer  (CORRECT / REJECTED, 2026-08-13)
- **唯一假设/结果**：删除exp365新增reducer模板实例，改用`batch_size==1 && n_split==256`运行时判断packed case13。源码SHA=`57a8e3678ce604e979b392c9aca00d4243ddbfe9ddb53279ca44b4f46be73ddc`；vec2 reducer由`38/39→38/43 STreg`、仍8 waves。case13仍相对#110426快约0.77%，但case10相对exp365双角色消偏约`1.0052`、慢0.52%；case10处于计分边界，因此拒绝提交。

### exp367-unified-vec2-packed-ml  (ACCEPTED #110895 / NOT BASELINE, 2026-08-13)
- **唯一假设/资源**：case10、case12、case13三个既有vec2 reducer用户统一采用FP16x2 packed `(m,l)`，reducer始终从`partial_m`以`__half2`读取并删除`partial_l`写入/读取，保持单一无格式分支实例。case10/13由已有producer编译期条件决定packed；case12只在page loop后的metadata writeback用`batch_size==8 && n_split==128`判断。源码SHA=`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。reducer为`38/39 MT/STreg、8 waves、0 stack`；case10 producer STreg约`54→52`，case12/13仍8 waves、0 stack。
- **门禁/A-B**：CPU14/14；GPU full/boundary/random各14/14；case10/12/13各17步full→short→split边界→full同进程复用全部通过。相对exp356双角色消偏case10/12/13约`0.9850/1.0015/0.9942`；相对正式#110426约`0.9887/1.0013/0.9895`。
- **OJ/选择**：提交前队列为空，只创建#110895；正常经历`Pending→Compiling→Running→Finished`并14/14 Accepted / `63.00`。case1–14=`3/4/10/23/19/28/252/116/255/46/288/421/253/174 us`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。case7刷新Accepted历史最佳`253→252 us`；case12/13/14相对baseline为`-2/-2/-3 us`，但case10仍46 us未跨档，case8 `115→116 us`掉1分，case9/11回退。aggregate未超过#110426的63.07，故不替换baseline；exp367作为已验证packed metadata组件保留。raw、工作文件和逐提交快照SHA三方一致，终态后队列为空。

### platform-probe-110941  (COMPILE TLE / SAME AS ACCEPTED SOURCE, 2026-08-13)
- **目的/源码**：用户要求尝试一次真实提交确认OJ能否成功。提交前队列为空，只创建#110941；为避免把平台状态与尚未完成门禁的exp373混淆，提交已完整验证且由#110895 14/14 Accepted的exp367不可变快照。#110941、#110916与#110895源码SHA均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **OJ/判定**：任务长时间保持Pending后终态CompilationError，无测试点；首条诊断为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有warning、无源码compiler error。说明提交入口可用但编译服务尚未稳定恢复；不取消、不继续同源复投，baseline保持#110426，终态后队列为空。raw与逐提交源码已归档。

### platform-probe-110962  (ACCEPTED / SAME AS #110895, 2026-08-13)
- **目的/源码**：用户要求再次尝试一笔真实提交。提交前队列为空，exp374虽已通过case14 full correctness但相对exp367的9×50 A/B p50=`1.0020`、中性略慢，因此没有提交工作文件；dry-run后只提交已14/14 Accepted的#110895/exp367不可变快照。提交源码、raw内嵌源码、#110962逐提交快照与#110895 SHA均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **OJ/判定**：#110962正常经历`Pending→Running→Finished`，14/14 Accepted / `63.00`；case1–14=`3/4/10/23/19/28/254/116/253/46/291/421/253/174 us`。确认当前创建、排队、编译和完整评测链路可用；同源计时只作为tier波动样本，不替换#110426 / `63.07` baseline。raw与逐提交源码已归档，终态后队列为空。

### exp370–374 case14 partial/QK diagnostics  (REJECTED, 2026-08-13)
- **U8 partial家族**：exp370–372依次测试packed U8 conversion、标量恢复与weight-scale变体，均未形成可用端到端收益。exp373进一步使用32-thread vec4 reducer，使每split只读一个`uint32_t`；case14 full仍PASS（max error=`1.831055e-04`），但5×20相对exp367 ratio p10/p50/p90=`1.0903/1.0953/1.1021`、慢约9.5%。并行度下降和转换/恢复成本压倒workspace字节下降，整个U8 partial家族关闭。
- **exp374双head归约调度**：只把两个同时存活head dot的四级native row shuffle按层交错，不改FMA次序、归约树、lane mapping或数学。case14 full PASS（max error=`1.220703e-04`），9×50相对exp367 p10/p50/p90=`0.9972/1.0020/1.0045`，中性略慢；纯shuffle调度不能减少case14约47.6%的QK主体成本。完整源码均见当日experiments目录，工作文件恢复exp367 SHA `575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。

### exp375-case14-distributed-alpha  (CORRECT / REJECTED, NOT SUBMITTED, 2026-08-13)

- **父版本/唯一假设**：从exp367/#110895分叉，仅在case14 fixed15两个head同时触发online-softmax rescale时，把两个scalar `exp2`替换为一次lane-varying `exp2`，再由lane0/lane4广播alpha；单head rescale路径保持不变。
- **资源/correctness**：SHA `b54abc4ce3128ac006b509d1b9b32c2e182bf04e2ec0ebd694dc740a4ed4d310`；producer=`90 MTreg/64 STreg/8320 B/0 stack/5 waves`。case14 full 100% PASS，max error `1.220703e-04`、max tolerance ratio `0.008`、finite。
- **A/B/结论**：相对exp367 9×50 ratio p10/p50/p90=`1.0477/1.0508/1.0539`，稳定慢约5.1%。双alpha SFU不是可见热点，新增分支和broadcast更贵；完整源码已归档，不提交。

### exp376-case14-halfrow-qk-invalid-qmap  (STATIC INVALID / REJECTED, NOT SUBMITTED, 2026-08-13)

- **假设/错误**：首版尝试把16-lane row拆成两个8-lane head组，但错误地让每组继续读取原来的`q0[8]/q1[8]`。half-row每lane必须覆盖一个head的连续16维，旧表示只能提供8维，因此语义上无法成立。
- **资源/结论**：SHA `ebc0b2e6b7281ac51b541deba65556ebaebc0190949611c10613a517028d4917`；producer恶化到`98 MTreg/4 waves`。未运行GPU；源码作为无效原型归档，不能据此判断修正后的half-row性能。

### exp377-case14-halfrow-qk-fixed-qmap  (CORRECT / REJECTED, NOT SUBMITTED, 2026-08-13)

- **唯一假设**：修复exp376映射。lanes0..7/8..15分别计算head0/head1，每lane加载所选head连续16维Q和K，执行8次packed FMA；QK以XOR4+两次native quad完成half-row归约，再一次rotate8交换两个head结果，保持现有owner-score/PV ABI。fixed15 `q_half[16]`与generic/final split的`q0[8]+q1[8]`处于互斥分支，不增加理论Q寄存器总数。
- **资源/correctness**：SHA `b181dc7eb752d427c74cbc55c1919c6819bfb34186a3fc0dc0267f4e631348d6`；目标producer=`82 MTreg/72 STreg/8320 B/0 stack/5 waves`，相对exp367约`90 MTreg/5 waves`，互斥Q表示生效且无spill。CPU14/14；真实C500 case14 full 100% PASS，max error `1.220703e-04`、max tolerance ratio `0.008`、finite。
- **A/B/结论**：相对exp367 9×50 ratio p10/p50/p90=`1.0995/1.1043/1.1106`，稳定慢约10.4%。每token每lane shuffle从双head各4次降为half-row3次+交换1次，但K BF16解包从4 words复用两个head变为8 words只服务一个head；解包/加载代价远大于shuffle节省。修正候选完整归档，不提交；case14 half-row8局部QK家族关闭，后续QK重构必须保留跨head K解包复用。

### exp378-case14-split-head-halfrow-qk  (LOCAL POSITIVE / OJ COMPILE TLE #110987, 2026-08-13)

- **changed precondition/唯一假设**：exp377证明丢失双head K解包复用会慢10.4%。exp378保留baseline每lane的一次`uint4` K读取、四次BF16 pair解包和同时喂两个head的8次packed FMA；只重构归约。配对lanes0/8交换一次对侧所需head partial，lanes0..7/8..15分别得到head0/head1两lane和，再并行执行XOR4与两次native quad归约。head0/head1 owner-score与PV broadcast源改为lanes0..3/8..11，不做额外恢复交换。fixed15以外路径不变。
- **资源/correctness**：SHA `7e7c6bdfbee0ff7a1b09df8a6731a6f1e0db4301b262103a77cbeede503ea64d`；case14 producer=`86 MTreg/70 STreg/8320 B/0 stack/5 waves`，相对exp367约少4 MTreg且保持驻留档。CPU14/14；GPU full/boundary/random各14/14；case14同进程`61519→1/2/15/16/17→239/240/241→255/256/257→479/480/481→3839/3840/3841→61518/61519`全部100% PASS且finite。
- **A/B**：相对exp367正向21×100 p50=`0.9807`，交换角色旧版/exp378=`1.0224`，消偏约`sqrt(0.9807/1.0224)=0.9794`、case14快约2.06%。相对正式#110426，case13/14正向=`0.9889/0.9623`，反向#110426/exp378=`1.0086/1.0368`，消偏约`0.9902/0.9634`；case7/8约`1.0019/1.0009`中性。
- **OJ**：提交前队列为空，只创建#110987。终态CompilationError且无测试点，首条诊断为`A TimeLimitExceeded encountered while compiling the code.`；xcore与host阶段只有既有warning、无源码error。因此这是平台compile TLE，不反证性能；raw与逐提交源码已归档。

### exp379-case14-split-head-compile-trim  (ACCEPTED #110993 / FORMER BASELINE, 2026-08-13)

- **唯一差异**：在exp378上删除case14 fixed15 helper从未实例化的非owner模板分支，并把case8 lane4与case14 lane8 owner-score PV helper合并为`owned_score_full_page_pv<HEAD1_LANE>`。源码从`220953`降到`218427 bytes`，SHA `f49371dbcb5b33f59d74ea95b0735408246e40b12b1b038ad93924cdf3681343`；目标是减少compile TLE风险，不改变运行数学。
- **门禁**：资源仍`86 MTreg/70 STreg/8320 B/0 stack/5 waves`；GPU full/boundary/random各14/14及上述case14 20步复用全部通过。相对exp378，case8/14正向p50=`0.9974/1.0044`，反向exp378/exp379=`1.0000/1.0029`，消偏约`0.9987/1.0007`，运行性能中性。
- **OJ/选择**：提交前队列为空，dry-run确认218427 bytes后只创建#110993；正常14/14 Accepted / `63.14`。case1–14=`3/4/10/22/19/28/254/117/255/46/290/420/253/170 μs`，case14相对#110426从`177→170 μs`并由49升到50分，首次在OJ兑现split-head half-row QK并成为当时baseline。raw、逐提交源码和候选SHA一致；后由#111016/exp382以63.29取代。

### exp380-case8+14-split-head-halfrow-qk  (LOCAL POSITIVE / NOT YET SUBMITTED, 2026-08-13)

- **changed precondition/唯一差异**：exp378/379已证明split-head half-row QK在case14有效；本轮保持exp379的case14实现，只把同一归约映射扩展到case8满长前13个fixed19 common split。每lane仍只读取/解包一份K并同时执行两个head的8次packed FMA；lanes0..7/8..15分别归约head0/head1。case8 final split、短长度generic路径、split14、fixed19 `unroll2`、skip-empty、K/V lookahead、partial和group8 reducer不变。
- **资源/correctness**：SHA `a1bddf35b8eb0aa7d85779a4c1c087f7a43e8bf3212bad339ca61b1f6a120576`；无stack且目标producer保持5-wave驻留档。GPU full/boundary/random各14/14；case8同进程`4096→1/2/15/16/17→95/96/97→303/304/305→607/608/609→4095/4096`全部100% PASS且finite。
- **A/B/结论**：相对exp379，case8正向21×100 p50=`0.9731`，反向exp379/exp380=`1.0261`，消偏约`sqrt(0.9731/1.0261)=0.9735`、快约2.65%；case14正反p50=`1.0018/1.0007`，中性。说明新归约不是case14偶然特例，可复用到head-pair fixed producer。因#110993仍Pending，严格未提交第二笔；源码已归档。

### exp381-case8+11+14-split-head-halfrow-qk  (LOCAL POSITIVE / SUPERSEDED BY EXP382, 2026-08-13)

- **唯一差异/编译表面**：从exp380只把split-head half-row QK扩展到case11的generic full-page producer。没有新增模板参数或kernel实例，而是用现有唯一编译期条件`FULL_PAGES_ONLY && DISTRIBUTED_SCORE_STATE && DISTRIBUTED_HEAD_MAX && SKIP_EMPTY_RESCALE && !CASE8_FIXED_19_PAGES`识别case11；fused tail、split48、K/V register-lookahead、partial和vec4 reducer均不变。源码SHA=`3b74e870269ed9ebc94f9e1a9c7a271faf90800cdf6821b92710dc96b753cbb5`，大小`220601 bytes`，完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case81114_split_head_qk_exp381.cpp`。
- **资源/correctness**：case11目标实例保持`86 MTreg/64 STreg/8320 B/0 stack/5 waves`。CPU14/14；真实C500 full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite，full最大误差`2.441406e-04`。
- **A/B**：相对exp380，case11 41×200正向ratio p50=`0.9751`，交换角色旧版/exp381=`1.0247`，双角色消偏约`sqrt(0.9751/1.0247)=0.9752`、快约2.48%；case8/14相对exp380中性。相对正式#110426，case8/11/14正向=`0.9722/0.9749/0.9673`，反向#110426/exp381=`1.0261/1.0250/1.0420`，消偏约`0.9734/0.9753/0.9635`，分别快约2.66%/2.47%/3.65%。
- **提交策略/结论**：#110993在途期间没有并行提交。exp381完整覆盖exp380且新增case11稳定收益；随后exp382在其上增加case10强收益，因此跳过exp380/381单独提交，直接提交更完整的exp382，以减少OJ提交次数。

### exp382-case10-headpair-z4-split-head-qk  (ACCEPTED #111016 / SELECTED BASELINE, 2026-08-13)

- **changed precondition/唯一差异**：从exp381只把case10 producer由单头`dim3(16,8,2)`改为head-pair/z4 `dim3(16,4,4)` + split-head QK；split128、四页/partial、fused tail、FP32 accumulator、FP16x2 packed `(m,l)`和vec2 reducer不变。旧exp27的case5 head-pair在两页/partial慢约2.3%，但case10每split工作量翻倍且producer约占73.7%，因此不沿用旧结论。
- **资源/门禁**：源码SHA=`2968dcbc8359b9a6c9d6310fb7d0cb0d15f431603978be3278509a586b796d7c`，大小220465 bytes；目标实例`86 MTreg/62 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14，case10 17步同进程复用全部PASS，full最大误差`2.441406e-04`。
- **A/B**：相对exp381的41×500正向ratio p50=`0.9254`，交换角色后旧版/exp382=`1.0733`，消偏约`sqrt(0.9254/1.0733)=0.9284`、case10快约7.16%；case8/11/12/13/14双角色哨兵中性。
- **OJ/选择**：提交前队列为空且dry-run正确，只创建#111016；任务正常经历`Pending→Running→Finished`并14/14 Accepted / **`63.29`**。case1–14=`3/4/10/22/19/28/253/116/254/42/282/422/252/170 μs`，目标case10相对#110993 `46→42 μs`、`58→60分`，case8/11/14组合也保住。raw、逐提交快照与工作文件SHA一致，选择#111016取代#110993为当前baseline，终态后队列为空。

### exp383/384-case5-headpair-z4-split-head-qk  (LOCAL POSITIVE / OJ 63.29, 2026-08-13)

- **唯一算法差异**：从#111016只把case5 producer由单头z2改为head-pair/z4 + split-head owner-state；保持真实split5、BSM、combined tail、FP32 partial和group8 reducer。manifest历史split3漂移已按生产源码修正为5。
- **资源/门禁**：producer从`92/48`变为`86 MTreg/56 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU full/boundary/random各14/14、19个精确长度与workspace full→short→full均PASS。exp383相对#111016双角色消偏约`0.9750`，非目标中性。
- **#111059**：SHA `b9c448c91c05d901c01efcd9c0b75594dcdd65b64ae2f33a926686ec4712e7d1`；OJ测试点前compile TLE，只有既有warning。不能作为性能失败。
- **exp384编译裁剪**：将恒定`separate_tail=false`编译期化并禁用六个不可达legacy launch，xcore1000实例warning `18→12`、本地resource build约`9.6→7.9 s`；运行算法不变。SHA `68af1a543e88ce8d7892865418b0ebfeecdc4cc54dabbfb6c2b97e7df9b8f8de`，完整门禁重跑通过，双角色消偏约`0.9703`。
- **#111076/OJ选择**：14/14 Accepted / `63.29`，case1–14=`3/4/10/23/19/28/254/115/255/42/281/423/253/169 μs`。case5仍19 μs未跨tier，case4/8一降一升；不替换#111016。exp384作为leading local-positive component继续组合旧exp191的独立reducer收益，不原样复投。

### exp385-case5-native-row-group8-reducer  (ACCEPTED #111115 / FORMER BASELINE, 2026-08-13)

- **唯一差异**：在exp384上只给case5 group8 reducer启用native-row max/sum；case5 head-pair/z4 + split-head producer与#111076字节语义一致，其他shape不变。
- **资源/门禁**：源码SHA=`aa486885aabf4ad373402149c1b6e98ce3b6694a4c73cec264a7bf124c70120c`；目标reducer为`66 MTreg/26 STreg/0 shared/0 stack/7 waves`。CPU14/14、GPU full/boundary/random各14/14、case5精确长度与`141→1→…→141`同进程workspace复用全部PASS。
- **A/B**：相对#111076，reducer唯一差异正向ratio p50=`0.9787`、反向旧版/exp385=`1.0230`，双角色消偏约`0.9781`；相对#111016，producer+reducer组合正向=`0.9467`、反向旧版/exp385=`1.0605`，消偏约`0.9447`、快约5.53%。非目标case4/8/10/11/12/13/14约`0.992–1.002`，无稳定回退。
- **OJ/选择**：提交#111115排队超过30分钟，本地watcher超时后没有取消或复投，重新挂接同一任务后正常`Running→Finished`。最终14/14 Accepted / **`63.36`**，case1–14=`3/4/10/23/18/28/252/115/255/42/281/425/252/169 μs`；case5从#111016的`19→18 μs`并由70升到71分，case8升1分、case4掉1分，aggregate净增。raw、逐提交快照和工作文件SHA一致，选择#111115取代#111016为当时baseline，终态后队列为空。

### exp386-case13-headpair-z8-ownership  (ACCEPTED #111200 / FORMER BASELINE, 2026-08-13)

- **唯一差异**：从#111115/exp385只把case13 producer ownership由`dim3(16,4,4)`的每线程一个query head、四token/z改为`dim3(16,2,8)`的每线程两个query head、两token/z。split256、15 pages/partial、256线程、同步loader、K+V-over-PV、Q prescale、FP16x2 `(m,l)` partial、global partial数量和vec2 reducer均不变；新kernel为`paged_decode_case13_kv8_headpair_z8_kernel`，八个z-state使用三阶段shared-memory树合并。
- **资源/门禁**：源码SHA=`b3893f989fcbb7a2d00c0d161e6bc33ff821cda10cf7ab020a09676c7ff8bb6c`。candidate=`82 MTreg/50 STreg/8448 B shared/0 stack/5 waves`，旧case13=`64/50/8192 B/0/8 waves`。CPU14/14、GPU full/boundary/random各14/14；case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部PASS。
- **A/B**：强测正向candidate/control p50=`0.8371`，反向old/new p50=`1.1975`，双角色消偏约`0.8361`、稳定快约16.4%；非目标case7/9/12首轮p50=`0.9989/0.9996/1.0002`。
- **OJ/选择**：#111200最终14/14 Accepted / **`63.71`**，case1–14=`3/4/9/23/18/28/254/116/254/42/281/422/212/169 μs`，分数=`92/90/83/72/71/63/52/48/55/60/46/57/53/50`。目标case13相对#111115从`252→212 μs`、`48→53分`，aggregate刷新。raw、逐提交快照和工作文件SHA三方一致，选择#111200取代#111115为当前baseline，终态后队列为空。下一步按case12、case9、case7顺序逐shape验证同一z8 ownership，每轮只扩一个dispatch。

### exp387-case12-headpair-z8-ownership  (ACCEPTED #111231 / SELECTED BASELINE, 2026-08-13)

- **唯一差异**：从#111200/exp386只把同一`dim3(16,2,8)` head-pair/z8 producer ownership扩展到case12；split128、16 pages/partial、fused-tail语义、同步K+V-over-PV、Q prescale、FP16x2 `(m,l)` partial、global partial数量和vec2 reducer均不变。
- **资源/门禁**：源码SHA=`adb1c0132f93b8b579e62dd2ccf2351419d5accca2ab87ea19a6c0c62bbe7ad2`。candidate=`82 MTreg/50 STreg/8448 B shared/0 stack/5 waves`，旧case12=`64/50/8192 B/0/8 waves`。CPU14/14、GPU full/boundary/random各14/14；case12同进程`32768→1→2→15→16→17→255→256→257→511→512→513→4095→4096→4097→32767→32768`全部PASS。
- **A/B**：强测正向candidate/control p50=`0.9326`，反向old/new p50=`1.0740`，双角色消偏约`0.9319`、稳定快约6.8%；非目标case7/9/13 p50=`1.0003/1.0004/1.0006`。
- **OJ/选择**：#111231最终14/14 Accepted / **`64.00`**，case1–14=`3/4/9/23/18/28/256/114/254/42/280/388/212/170 μs`，分数=`92/90/83/72/71/63/52/49/55/60/47/59/53/50`。目标case12相对#111200从`422→388 μs`、`57→59分`，aggregate刷新。raw、逐提交快照和工作文件SHA三方一致，选择#111231取代#111200为当前baseline，终态后队列为空。下一步按case9、case7顺序逐shape验证同一z8 ownership，每轮只扩一个dispatch。

### exp388-case9-z8-bad-vec4  (LOCAL WRONG ANSWER / REJECTED, 2026-08-13)

- **唯一差异**：从#111231只把case9 producer改成`dim3(16,2,8)` head-pair/z8，保持原case9 vec4 reducer。
- **根因/证据**：z8 producer把FP16x2 `(m,l)`写入`partial_m`且不写`partial_l`；vec4 reducer仍按FP32 `partial_m/partial_l`分别读取，形成确定性ABI失配。case9 full `match=0.082657`、`max_error=3.790283`，其余13例通过。
- **结论**：不得提交。源码SHA=`286d090f8aba0f83df65512cb752c0aea83a22e0d21e0106dec77a98643d3058`，完整归档为`cuda_case9_z8_bad_vec4_exp388.cpp`。新producer推广必须同时审计metadata/accumulator/reducer契约，不能只看dispatch表面。

### exp389-case9-z8-packed-vec2  (ACCEPTED #111307 / FORMER BASELINE, 2026-08-13)

- **唯一修复**：保留exp388 producer和case9 split24、11 pages/partial、fused-tail、同步K+V-over-PV、Q prescale与partial数量，只把reducer换成已支持packed `(m,l)`的64-thread vec2。
- **门禁/A-B**：SHA=`b1da92c381956abd5b3016e2f74207a5fdbbc82420352cb64552bb1ecfb0a3ec`；CPU14/14、GPU full/boundary/random各14/14；case9同进程`4096→1/2/15/16/17→175/176/177→255/256/257→4095/4096`全部PASS。强测正向p50=`0.9661`，反向旧/新=`1.0343`，消偏约`0.9664`、快约3.36%。
- **OJ**：#111307 14/14 Accepted / `64.07`，case9相对#111231 `254→244 μs`、`55→56分`。raw、逐提交快照和实验源码SHA一致；当时刷新baseline，后由exp390取代。

### exp390-case7-z8-packed-group8  (ACCEPTED #111319 / SELECTED BASELINE, 2026-08-13)

- **唯一差异**：从exp389只把z8 producer扩到case7，并给原8-head group8 reducer增加packed FP16x2 `(m,l)`读取。保留split14、10 pages/partial、fused-tail、同步K+V-over-PV、global partial数量和reducer CTA grid，避免以vec2将B64 reducer grid放大8倍。
- **门禁/A-B**：SHA=`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`；CPU14/14、GPU三组各14/14；case7同进程`2048→1/2/15/16/17→159/160/161→255/256/257→2047/2048`全部PASS。相对exp389正向p50=`0.9773`、反向旧/新=`1.0235`，消偏约`0.9769`、快约2.31%；case9中性。
- **OJ/选择**：#111319 14/14 Accepted / **`64.14`**，case1–14=`3/4/9/23/18/28/247/115/245/42/279/390/212/169 μs`；目标case7相对#111307 `256→247 μs`并由52升到53分。raw、逐提交快照和工作文件SHA三方一致，选择#111319为当前baseline。长KV8 case13/12/9/7 z8逐shape扩展主线至此闭环，下一步转向长KV4架构。

### exp391-case11-pair32-z2  (LOCAL CORRECT / REJECTED, 2026-08-13)

- **唯一假设**：从#111319只替换case11 producer为`dim3(32,4,2)`。CTA仍256线程并完整拥有一个KV-head/split；每个32-lane logical row处理一个head pair，两个原生16-lane half-row通过一次固定`xor16`交换partial完成两头；保持split48、page只加载一次、FP32 partial和原vec4 reducer。
- **资源/正确性**：SHA=`7dbfc2c9d15cbf14a6aa5340787dd787026f6f882b472c51118c53b9a25f8561`；candidate=`80 MTreg/68 STreg/8256 B/0 stack/6 waves`，control=`86/64/8320 B/0/5 waves`。CPU14/14；case11 full PASS，max error=`2.441406e-04`；同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部PASS。
- **A/B/结论**：case11 candidate/control p10/p50/p90=`1.3436/1.3447/1.3455`，稳定慢34.5%；case8/14哨兵约中性。静态跨到6-wave档仍无法补偿8-token串行链和z2跨waveCTA barrier。关闭该exact ownership，不以split、reducer、loader或launch参数补偿，不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case11_pair32_z2_exp391.cpp`；工作文件恢复#111319。

### exp392-case11-direct-global-k  (STATIC RESOURCE REJECTED, 2026-08-13)

- **唯一假设**：从#111319只改变case11 full producer的QK数据源。四个query-row不再从shared读取已经发布的K，而是直接读取相同global/L2 K地址；V staging、CTA布局、split48、QK数学、softmax、PV、partial和reducer全部不变。目标是删除K的shared store、barrier可见性负担和四行重复LDS。
- **资源门禁**：SHA=`352c373a8c36c47d3b514a449a431729bc72b3a62d5e5e9ce3434821603bdc3b`。global地址与K值live range使producer从control的`86 MTreg/64 STreg/8320 B/0 stack/5 waves`恶化为`102/64/8320 B/0/4 waves`。删除LDS没有抵消occupancy降档，按静态资源门禁拒绝；未跑GPU A/B、未提交。资源日志为`build/exp392_resource.log`，完整源码已归档。除非load ownership或地址生命周期发生结构变化，不再重试同一direct-global-K表达式。

### exp393-395-case5-split-rescan-current-producer  (LOCAL CORRECT / REJECTED, 2026-08-13)

- **changed precondition**：旧case5 split3结论来自不同producer/reducer；当前#111319已使用head-pair/z4 split-head producer、native-row group8 reducer和生产split5，因此只重扫相邻split3/4/6，其他路径保持不变。
- **exp393 split4**：SHA=`3a196514faa7f938252026e0a2414be89134e7f6016db1975f7622e7a577015a`。资源与control相同：producer`86/56/8320 B/5 waves`、reducer`66/26/7 waves`；case5 full PASS，max error=`1.953125e-03`。正向candidate/control p10/p50/p90=`0.9770/0.9866/1.0006`，交换角色old/new=`0.9366/0.9958/1.0607`，双角色消偏约`sqrt(0.9866/0.9958)=0.9954`，仅快约0.46%且区间宽，不足跨tier。
- **exp394 split6**：SHA=`2d3fb8490cf2e2f16d303780e5ef54fc18044f92329fa146db5986fb85af5611`；case5 full PASS，candidate/control p10/p50/p90=`0.9636/1.0011/1.0345`，中性略慢。
- **exp395 split3**：SHA=`332193b83208ef9406b1fcd58472f8578c867101d76f1723141e8935ed909d6b`；case5 full PASS，candidate/control p10/p50/p90=`1.0001/1.0161/1.0354`，稳定慢约1.6%。
- **结论**：当前case5曲线为split3负向、split4边缘、split5最优、split6中性略负；changed-precondition邻域已经闭合，三份候选均不提交。后续不得继续case5 split/reducer微调，除非producer ownership或tail/partial契约再次发生关键改变。

### exp396-case11-head4-z4-split-head  (STATIC REJECTED, NOT SUBMITTED, 2026-08-13)

- **changed precondition/唯一假设**：旧exp168的128-thread `(16,2,4)` head4/z4在四套完整row reduction和`score[4][4]`下为`146 MTreg/3 waves`、慢约5.89%；当前#111319已验证split-head QK和owner-score，因此重开时让一次K/V解包服务四个heads，并以两套split-half网络分别处理`(ty,ty+4)`与`(ty+2,ty+6)`，保持case11 split48、同步K/V register-lookahead、fused tail、FP32 partial与既有reducer ABI。
- **资源/结论**：SHA=`22bf4254625f0f28fc43be5b0b85f66dbc30d2f4af051ace2651eb2fd8bcbf1b`。CPU语义14/14通过，但目标kernel为`166 MTreg/60 STreg/8320 B/20 B stack/staticMaxWarps=3`，比exp168还恶化且远低于#111319 control的`86/64/8320/0/5 waves`。四套FP32 accumulator/softmax状态本身主导峰值live range，两套split-head网络与分布式score不足以跨到预设至少4 waves；按静态门槛不跑GPU、不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case11_head4_splithead_exp396.cpp`，该exact 128-thread head4/z4 ownership关闭；后续新ownership优先保留当前256-thread wave-private双head状态。

### exp397-case11-normalized-bf16-partial  (LOCAL CORRECT / REJECTED, NOT SUBMITTED, 2026-08-13)

- **唯一假设**：从#111319只让case11 producer把每split accumulator先除以`l`并以BF16写入原workspace前半区；matching vec4 reducer以完整`l*exp(m-m_global)`权重恢复合并。split48、head-pair/z4、split-head QK、同步K/V register-lookahead、fused tail、FP32 `(m,l)`、global partial数量、reducer CTA/grid和其余shape均不变。目标是将case11 accumulator workspace读写从FP32降为BF16，而不改producer热循环。
- **门禁**：SHA=`2ff7b572bee3fb6e9ac8a1324f48119624f33d659724986e0a392d3a14bed27c`。producer保持`86 MTreg/64 STreg/8320 B/0 stack/5 waves`；新BF16 vec4 reducer为`42/26/0/0/8 waves`，control vec4为`64/35/0/0/8`。CPU14/14、GPU full/boundary/random各14/14；case11同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite，满长max error=`2.441406e-04`。
- **A/B/结论**：21×300正向candidate/control p10/p50/p90=`1.0285/1.0305/1.0315`；交换角色old/new=`0.9700/0.9712/0.9721`，双角色消偏约`sqrt(1.0305/0.9712)=1.0301`、稳定慢约3.0%。BF16转换/normalized weight成本高于workspace流量节省，说明case11 accumulator round-trip不是当前主瓶颈；不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case11_bf16_partial_exp397.cpp`。该exact normalized-BF16 accumulator契约对case11关闭；后续partial候选必须减少metadata、global partial数或kernel round trip，而不是仅压缩acc字节。

### exp398-case11-fp16x2-metadata  (LOCAL CORRECT / NEUTRAL, NOT SUBMITTED, 2026-08-13)

- **唯一假设**：从#111319只把case11每split的FP32 `(m,l)` 两槽压成`partial_m`中的FP16x2，matching vec4 reducer首次读取时解包并把`l`暂存在已有shared weight区；FP32 accumulator、split48、producer ownership/QK/loader/tail、partial数量和reducer grid不变。
- **资源/correctness**：SHA=`cf5004492e1f2423563b9517a6641dd152904b0e0af0a8af04a3b696d544fed1`。producer由control `86/64/8320 B/0/5 waves`变为`86/62/8320 B/0/5`，vec4 reducer保持`64/35/0/0/8`。case11 full与同进程`12251→1/2/15/16/17→255/256/257→511/512/513→767/768/769→12250/12251`全部100% PASS且finite，满长max error=`2.441406e-04`。
- **A/B/结论**：21×300正向candidate/control p10/p50/p90=`0.9960/0.9995/1.0008`；交换角色old/new=`0.9993/1.0006/1.0015`，双角色消偏约`sqrt(0.9995/1.0006)=0.99945`，仅快约0.055%、完全在噪声内。case11 metadata流量也不是可见瓶颈；不扩大全量门禁、不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case11_packed_ml_exp398.cpp`。结合exp397，case11纯partial字节压缩主线关闭，后续必须减少global partial数量或round trip。

### exp399-case11-single-page-headpair-z8-512  (LOCAL CORRECT / REJECTED, NOT SUBMITTED, 2026-08-13)

- **changed precondition/唯一假设**：旧case14 512-thread/two-page探针慢17.9%，但同时改变shape、双页buffer与page ownership。exp399在#111319当前split-head/K+V-lookahead前提下只替换case11 producer为单页`dim3(16,4,8)`：八个物理z wave各处理2 token，保持双head K解包复用、split48、FP32 partial和vec4 reducer。原8 KiB buffer分批物化两z peer，以三层in-place树合并八个z，避免16 KiB shared。
- **资源/correctness**：SHA=`d8e82db4017ef6c221f963b1a3b60fab71d150f95b9c210ed10680a9c195bf19`。目标kernel=`84 MTreg/52 STreg/8320 B/0 stack/staticMaxWarps=5`，静态未降档；CPU14/14、真实C500 case11 full 100% PASS，max error=`2.441406e-04`、finite，证明512-thread launch与分批barrier语义可用。
- **A/B/结论**：9×100 candidate/control p10/p50/p90=`1.4256/1.4271/1.4289`，稳定慢42.7%，差异远离任何角色/时钟噪声，无需反向长测或全量门禁。512-thread/8-wave block调度与三层z merge完全压倒每z token链4→2的收益；不提交。完整源码归档为`solutions/archive/2026-08-13-experiments/cuda_case11_headpair_z8_512_exp399.cpp`。结合旧case14反例，KV4 512-thread ownership关闭，不以split、reducer、loader或双页/单页微调补偿。

### exp400-case11-all-native-split-head-qk  (ACCEPTED #111517 / OJ-POSITIVE COMPONENT, 2026-08-13)

- **能力探针**：首先尝试DPP `row_half_mirror`模式`0x141`，本机xcore1000后端明确报`Invalid shfl_mode value`，不进入生产。随后`tests/c500_split_head_native_probe.cpp/.py`在真实C500验证合法网络：rotate4交换双head后按`tx&4`分组，rotate8和quad2/quad1归约各head的八个two-lane partial；逐head结果与生产rotate8+BSM-XOR4网络一致。codegen probe由`5→4 MTreg`。
- **唯一差异/资源**：从#111319只给case11 full-page split-head QK启用全原生网络；K解包、八次packed FMA、split48、K/V register-lookahead、fused tail、softmax/PV、FP32 partial和vec4 reducer不变。SHA=`64ec2c8f804c0a6f00fde553d9e8849576df961d361044c609d5603f8d76beb5`；producer保持`86 MTreg/64 STreg/8320 B/0 stack/5 waves`。
- **correctness/A-B**：CPU14/14；GPU full/boundary/random各14/14；case11同进程`12251→16/17→767/768/769→12240/12241/12250/12251→1/2/15/16/17→12251`全部PASS。21×300正向p10/p50/p90=`0.9797/0.9814/0.9832`，反向old/new=`1.0176/1.0180/1.0186`，双角色消偏约`0.9818`、快约1.82%。
- **OJ/结论**：#111517 14/14 Accepted / `64.00`，case11相对#111319 `279→276 μs`且保持47分，证明组件真实有效；case8无源码差异地`115→116 μs`掉1分，aggregate未刷新。保留为后续组合组件，不替换#111319 baseline；逐提交快照与raw已归档。

### exp401-case8+11-all-native-split-head-qk  (ACCEPTED #111528 / 64.14 TIE, 2026-08-13)

- **唯一差异**：在exp400上只给case8满长前13个fixed19 common split启用全原生rotate4/rotate8/quad网络，并同步把该helper的head1 owner/broadcast从lane8改为lane4；最后underfilled split与短长度generic路径不变。SHA=`60045917aed5cfab02b9978de4d5e4b55615273a38641152c0c759f7eafa9223`。
- **门禁/A-B**：case8资源仍`86 MTreg/70 STreg/8320 B/0 stack/5 waves`，case11仍`86/64/8320/0/5`。CPU14/14、GPU三组14/14、case8 11步复用通过。相对exp400 21×300正向case8 p50=`0.9872`、反向old/new=`1.0115`，消偏约`0.9879`、快约1.21%；case11中性。相对#111319最终case8/11 p50=`0.9863/0.9813`。
- **OJ/结论**：#111528 14/14 Accepted / `64.14`，case8/11=`115/277 μs`，均未跨计分档；case3同源回到9 μs使aggregate与#111319并列。保留为leading组合父版本和有效组件，但默认control仍为先建立最高分的#111319。

### exp402-case8+11+14-all-native-split-head-qk  (ACCEPTED #111547 / OJ-POSITIVE COMPONENT, 2026-08-13)

- **唯一差异**：从exp401只给case14满长前256个fixed15 common split启用exp400的全原生rotate4/rotate8/quad split-head网络，并同步把head1 owner/page-max/PV broadcast从lane8改为lane4。最后underfilled split和任意短长度继续走原generic split-head路径；split257、register K/V lookahead、softmax/PV、normalized-BF16 partial与reducer均不变。源码SHA=`89f20c24824ee69861df33608897a11c1d48e1992f7c1cc7db0cd7d05558dc1b`。
- **资源/correctness**：case14 producer保持`90 MTreg/58 STreg/8320 B/0 stack/5 waves`，case8/11也保持`86/70`与`86/64`的5-wave档。CPU14/14；同一candidate `.so`的GPU full/boundary/random各14/14；case14同进程`61519→15/16/17→239/240/241→61439/61440/61441→61518/61519`全部100% PASS且finite。首次满长进程曾以Exit137无输出终止，显存和系统内存随后正常；Accepted exp401同shape与candidate独立重跑均PASS，因此按规则只视为资源/驱动瞬态，不计作数值证据。
- **A/B**：相对exp401唯一差异，21×300正向candidate/control p10/p50/p90=`0.9842/0.9858/0.9873`，交换角色old/new=`1.0131/1.0171/1.0193`，消偏约`sqrt(0.9858/1.0171)=0.9845`、case14快约1.55%。相对从#111319不可变源码fresh build的最终组合，case8正向/反向old-new p50=`0.9857/1.0115`、case11=`0.9815/1.0180`、case14=`0.9848/1.0169`，双角色消偏约`0.9872/0.9816/0.9838`，三个组件同时成立。
- **OJ/结论**：提交前SHA、dry-run和队列空闲均已核对，只创建#111547；任务未取消、未复投并正常14/14 Accepted / `64.00`。case1–14=`3/4/10/23/18/29/246/115/245/42/279/387/212/166 μs`；case14相对#111319 `169→166 μs`但仍50分，case6掉1分且case11同源回到279 μs。raw、逐提交快照与工作文件SHA一致；组件获得真实目标证据但不替换#111319，exp402作为leading组合父版本，队列为空。

### exp403-case10-all-native-split-head-qk  (LOCAL POSITIVE / OJ ACCEPTED, 2026-08-13)

- **唯一差异**：从已归档exp402只放宽generic full-page的编译期全原生判定，使packed `(m,l)` 的case10也从`rotate8 → BSM XOR4 → quad2 → quad1`切为`rotate4 → rotate8 → quad2 → quad1`，并把head1 owner/page-max/PV broadcast从lane8改为lane4。case11原本已启用；case8/14 fixed helper、case5 combined tail、fused tail、split128、四页/partial、K/V lookahead、FP32 acc、packed metadata与vec2 reducer均不变。SHA=`070f4ce0fbe5ad1aa22c82ba7eb97b15203fa0d61f78524e3d2b82c811fee126`。
- **资源/correctness**：case10 producer保持`86 MTreg/62 STreg/8320 B/0 stack/5 waves`，case8/11/14资源档也不变。CPU14/14；GPU full/boundary/random各14/14；case10同进程`8192→1/2/15/16/17→63/64/65→127/128/129→191/192/193→8191/8192`全部PASS且finite。首次在连续构建后立即运行full的进程无输出Exit137；exp402同shape与candidate独立重跑均PASS，只按瞬态资源终止记录。
- **A/B**：相对exp402唯一差异，41×500正向candidate/control p50=`0.9850`、反向old/new=`1.0118`，双角色消偏约`0.9865`、case10快约1.35%。相对fresh #111319最终组合，case10正向/反向old-new p50=`0.9870/1.0078`，消偏约`0.9895`；case8/11/14约`0.9878/0.9820/0.9842`，既有组件未被削弱。
- **OJ/结论**：提交前SHA、dry-run和队列空闲均已核对，只创建#111570；约五分钟无中间case输出后正常`Pending→Running→Finished`，14/14 Accepted / `64.00`。case1–14=`3/4/10/23/18/28/246/116/244/42/275/389/211/167 μs`；目标case10仍42 μs，未跨预期tier，case11刷新Accepted历史最佳275 μs但aggregate未超过64.14。raw、逐提交快照与工作文件SHA一致；保留exp403为leading组合父版本，不替换#111319，不同源复投，队列为空。
- **归因修正**：源码复审确认`FULL_PAGES_ONLY && SKIP_EMPTY_RESCALE`选择器除case10外也命中case14最后一个underfilled generic split；不影响前256个fixed15热split和既有A/B结论，但“唯一新增命中只有case10”的旧表述不精确。后续唯一差异必须显式考虑该冷split。

### exp404-exp405-case5-all-native-split-head-qk  (LOCAL POSITIVE / OJ ACCEPTED, 2026-08-13)

- **唯一差异/语义**：exp404从exp402只给case5 combined-page split-head QK启用全原生rotate4/rotate8/quad网络并把head1 owner从lane8改为lane4，显式排除case10与case14 generic split。invalid tail token不写owned state、保持`-Inf`，对应fixed broadcast权重精确为0；lane0/4 token0在tail page存在时必然有效。exp405再把该唯一组件组合进exp403。
- **门禁/性能**：exp404 SHA=`393ca42530c42f378ea1afa2ad1b5ac4d8771560a81af5a1dcf541429933ecdc`，producer保持`86/56/8320 B/0 stack/5 waves`；CPU/GPU三组14/14和20步复用通过，相对exp402正向/反向p50=`0.9825/1.0190`，消偏约`0.9819`。exp405 SHA=`fd789c6954b6280e419c94f994c3027eb2e73461ddbcda9e2aa4e86a24512407`，完整门禁重跑通过；相对fresh exp403正向p50=`0.9900`、反向old/new=`1.0253`，消偏约`0.9826`，case8/10/11/14=`0.9991/0.9996/0.9993/0.9999`。
- **OJ/结论**：只创建#111590，约七分钟后正常14/14 Accepted / `64.07`。case1–14=`3/4/10/23/18/28/246/115/243/41/277/391/211/167 μs`；case5仍18 μs未跨tier，case9/10刷新Accepted历史最佳但不加分。raw/逐提交/工作SHA一致，保留exp405为leading组合，不替换#111319，不同源复投，队列为空。

### exp406-exp410-case11-split-neighborhood  (LOCAL POSITIVE / OJ REJECTED #111616, 2026-08-13)

- **changed precondition/唯一假设**：exp406b从exp405只将case11 `split48/16 pages`改为`split24/32 pages`。全原生split-head QK让每页producer更便宜，而vec4 reducer仍随partial数增长，因此重新验证旧split24点；producer、loader、partial ABI和其他shape不变。
- **正确性契约**：初版exp406只改split后因`reduce_splits<=32`隐式切到generic group8 reducer；该实例缺少fused-tail live-count，长度513/1025 WrongAnswer。exp406b把case11原one-head vec4 reducer分支提前，保持`FUSE_TAIL_IN_LAST_SPLIT=true`。修复后CPU14/14、GPU full/boundary/random各14/14，以及`12251→1/2/15/16/17→511/512/513→1023/1024/1025→12250/12251`全部PASS。
- **A/B与邻域**：SHA=`8a8c299a66942d33db6317e6e29049530e78511f44c48f542eec3adee3c08ac7`。相对exp405正向p50=`0.9583`、反向old/new=`1.0423`、final rebuild=`0.9585`，消偏约`0.9588`。exp407 split22、exp410 split23、exp409 split25、exp408 split26相对split24分别为`1.0111/1.0118/1.0088/1.0052`，两侧均慢，本地离散曲线闭合。
- **OJ/结论**：只创建#111616，正常14/14 Accepted / `64.00`；case1–14=`3/4/10/23/18/28/247/114/244/41/281/388/212/167 μs`。目标case11比exp405 `277→281 μs`并从47掉到46分，本地4.1%正向未兑现；不替换#111319，不同源复投或继续微扫22–26。raw/逐提交/提交前源码SHA一致，工作文件与manifest已恢复exp405的split48，队列为空。

### #111364-#111319-same-source-platform-probe  (ACCEPTED / TIMING SAMPLE, 2026-08-13)

- **提交/核对**：按用户要求原样试投当前baseline，只创建#111364。任务正常完成14/14 Accepted / `64.00`；raw、逐提交快照、工作文件与#111319 SHA均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。
- **OJ**：case1–14=`3/4/10/23/18/28/247/115/244/42/283/391/211/169 μs`。链路可用；无源码差异，逐case变化只作为timing-tier样本，不替换#111319 / 64.14 baseline。raw和`cuda_111364.cpp`已归档，队列为空。

### #111641-#111319-same-source-platform-probe  (ACCEPTED / TIMING SAMPLE, 2026-08-13)

- **提交/核对**：用户要求尝试一次真实提交。提交前最近10笔均已终态，先dry-run，再原样提交不可变baseline `solutions/archive/2026-08-13-submissions/cuda_111319.cpp`；只创建#111641。平台列表一度仍为Pending，watch进度曾显示Running且数分钟无case输出；未取消、未复投。
- **OJ/结论**：正常14/14 Accepted / `64.07`，case1–14=`3/4/9/23/18/28/246/116/244/42/279/390/212/169 μs`。raw内嵌源码、逐提交快照和#111319 SHA均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。确认OJ创建、排队、编译和完整评测链路可用；同源波动不替换#111319 / 64.14 baseline，队列恢复为空。

### bf16-mma-zero-started-k16-precision-probe  (DIAGNOSTIC POSITIVE, 2026-08-13)

- **假设/方法**：历史BF16 MMA端到端QK失败被归因为K=16内部低精度。新probe固定同一16×128 BF16输入，同时计算常规8次K=16 chained MMA，以及8个从精确零开始的K=16 tile；后者拷回CPU后以FP32求和，并与CPU FP32 reference比较。源码已归档为`tests/archive/closed-backend-probes/c500_mma_block_accum_precision_probe.cpp/.py`，构建产物为可重建的`build/c500_mma_block_accum_precision_probe.so`，未修改生产源码。
- **结果**：真实MetaX C500覆盖scale=`0.125/1/4`、4个seed，共12组；zero-start+CPU FP32 merge平均误差12/12均低于chained。scale=4时chained max/mean约`7.63e-5–1.53e-4 / 1.22e-5–1.46e-5`，zero-start约`6.10e-5–9.16e-5 / 8.43e-6–1.07e-5`，单tile max/mean约`1.53e-5–3.05e-5 / 1.04e-6–1.14e-6`。
- **终局修正**：随后字节精确复现`cuda_104175.cpp`发现，即使Q=K=0，case8输出仍整段为0而非V均值；`build/exp62_device.ll`又显示历史`paged_decode_mma_qk_kernel`只有`ret void`，资源为`1 MTreg/4 STreg/0 shared`。根因是完整device body使用`defined(__CUDA_ARCH__)`，而MXMACA xcore pass只定义`__MACA_ARCH__`。因此旧NaN/大误差不是MMA精度数据，而是空kernel后reducer读取零/旧workspace；zero-start略准只是普通数值差异，不是生产correctness所必需。

### bf16-mma-legacy-body-macro-root-cause  (DIAGNOSTIC CLOSED, 2026-08-13)

- **方法**：`tests/archive/closed-backend-probes/c500_mma_legacy_body_probe.cpp`不修改不可变#104175，只在`defined(__MACA_ARCH__) && !defined(__CUDA_ARCH__)`的device pass映射宏后include历史源码，使预期body真实发射。
- **正确性/资源**：真实历史body的case8 100% PASS，max error=`4.882812e-04`、max tolerance ratio=`0.029`、finite；资源为`206 MTreg/98 STreg/9824 B/0 stack/2 waves`。相对fresh #111319的case8 A/B p50=`3.2217`，慢约3.22倍。
- **结论**：BF16 MMA指令正确可用，历史“硬件精度墙”关闭并禁止再引用。旧完整64-thread Attention布局仍因一个wave承担完整8-head softmax/PV、高寄存器和2-wave驻留而关闭；后续必须设计consumer-local score数据流。

### exp407-case11-lane-local-bf16-mma-qk  (ACCEPTED / NEW BASELINE #111707, 2026-08-13)

- **父版本/唯一假设**：从不可变#111319字节精确分叉，只替换case11 full-page scalar split-head QK。每个物理z wave独立执行8次`m16n16k16` BF16 MMA；16行重排为每个ty的`head ty/head ty+4/zero/zero`，四个本地token列复制到16列，使lane `(ty,tx)`的accumulator `x[0]/x[1]`正好对应两个head和`tx&3` token。loader、K/V register-lookahead、online softmax、PV、split48、fused tail、partial和vec4 reducer全部保持。
- **probe**：`tests/c500_bf16_mma_qk_resource_probe.cpp/.py`覆盖3 scale×4 seed，12/12逐lane映射正确，worst max/mean error=`1.220703e-04/1.478009e-05`；QK-only资源`16 MTreg/16 STreg/0 shared/8 waves`。
- **生产资源/correctness**：SHA=`2f0421d578b221f6689146e7588205d4563ae7caea0a770aa477e9062d365ac9`。case11 producer由#111319的`86 MTreg/64 STreg/8320 B/0 stack/5 waves`改善为`80/60/8320/0/6 waves`。CPU14/14；同一final `.so` GPU full/boundary/random各14/14；case11精确长度`1,2,15,16,17,255,256,257,271,272,511,512,513,767,768,769,12250,12251`全部PASS，满长max error=`2.441406e-04`、max tolerance ratio=`0.015`、finite。
- **A/B**：9×20初筛candidate/control p50=`0.8052`；21×100正向exp407/#111319=`0.8039/0.8046/0.8070`，反向#111319/exp407=`1.2375/1.2423/1.2447`，几何消偏约`0.8048`、稳定快约19.5%。关键非目标case4/5/8/10/14 p50=`1.0005/1.0142/0.9978/1.0068/0.9989`，短case区间宽、未建立系统回退。
- **OJ结果/选择**：提交前dry-run且队列为空，只创建#111707；任务经历`Pending→Running→Finished`，最终14/14 Accepted / **`64.36`**。case1–14=`3/4/10/23/18/28/246/115/243/43/223/390/212/169 μs`，分数=`92/90/82/72/71/63/53/49/56/59/52/59/53/50`。目标case11相对#111319 `279→223 μs`、`47→52分`，与本地19.5%收益一致；case3/10各掉一档属于非目标timing波动，aggregate仍刷新。raw、逐提交快照和提交源码SHA完全一致，#111707成为新唯一baseline，队列为空。

### exp408b-case8-lane-local-bf16-mma-qk  (ACCEPTED / NEW BASELINE #111730, 2026-08-13)

- **父版本/唯一假设**：从#111707字节精确分叉，只把同一lane-local BF16 MMA QK扩到case8；split14、前13个fixed19 split、最后underfilled split、fused tail、K/V register-lookahead、owner softmax/PV、partial和group8 reducer均保持。最终源码SHA=`c4456f7c28f0ee870ac3ea6e74839dde8e56fc9cd6d260848b7cd2fc8789df9b`。
- **首版错误与修复**：exp408初版fixed19 helper按MMA的lane0/lane8发布head0/head1，但generic full-page分支仍按旧非-split lane0/lane4读取；满长仅最后split错误而侥幸达到`99.649%` tolerance，变长generic路径大范围失败。exp408b把generic page-max和owner-PV两处契约统一为lane8；随后case8长度`17,255,256,257,511,512,513,1024,2048,3072,4095,4096`全部100% PASS。该错误不是BF16精度问题，不得保留初版数据作为精度结论。
- **资源/correctness**：case8 producer从#111707的`86 MTreg/70 STreg/8320 B/0 stack/5 waves`改善为`82/66/8320/0/5 waves`。CPU14/14；GPU full/boundary/random各14/14；满长max error=`4.882812e-04`、max tolerance ratio=`0.029`、finite。
- **A/B**：21×100正向exp408b/#111707=`0.8406/0.8422/0.8438`，反向#111707/exp408b=`1.1799/1.1823/1.1837`，消偏约`0.8440`、快约15.6%。9×20关键非目标case4/5/10/11/14 p50=`1.0035/0.9939/1.0122/0.9999/1.0011`，均未建立系统回退。
- **OJ结果/选择**：提交前dry-run、队列为空，只创建#111730；任务经历`Pending→Running→Finished`，最终14/14 Accepted / **`64.86`**。case1–14=`3/4/9/23/18/28/245/94/243/42/224/390/212/169 μs`，分数=`92/90/83/72/71/63/53/54/56/60/52/59/53/50`。目标case8相对#111707 `115→94 μs`、`49→54分`，与本地15.6%收益一致；case11保持52分，非目标计分恢复。raw、逐提交快照和源码SHA一致，#111730成为新唯一baseline，队列为空。

### exp409-case14-lane-local-bf16-mma-qk  (ACCEPTED / NEW BASELINE #111753, 2026-08-13)

- **父版本/唯一差异**：从#111730只把lane-local BF16 MMA扩到case14的fixed15 helper、最后generic split与fused tail；split257、fixed15 `unroll 2`、K/V register-lookahead、online softmax/PV、normalized-BF16 partial、packed metadata和reducer不变。提交SHA=`7bef7e049605535f259df23363558d62c13db41fad8160121b1b81e12ae92a44`。
- **资源/correctness**：case14 producer由`90 MTreg/58 STreg/8320 B/0 stack/5 waves`变为`82/62/8320/0/5`。CPU14/14，GPU full/boundary/random各14/14；19个split/tail精确长度及`61519→1/...→61518→61519`同进程复用全部100% PASS且finite。
- **A/B**：9×20初筛new/old p50=`0.8521`；21×100正向new/old=`0.8505`，反向old/new=`1.1749`，消偏约`0.8508`、快约14.9%。case8/11中性，case5/10短时波动远小于目标收益。
- **OJ结果/选择**：只创建#111753，长Pending后正常`Compiling→Running→Finished`；14/14 Accepted / **`65.07`**。case1–14=`3/4/10/23/18/28/247/94/244/42/223/392/212/143 μs`，分数=`92/90/82/72/71/63/53/54/56/60/52/59/53/54`。case14相对#111730 `169→143 μs`、`50→54分`，与本地一致。raw与逐提交快照SHA精确一致，#111753成为新唯一baseline。

### exp410-exp411-case10-case5-lane-local-bf16-mma  (ACCEPTED / NEW BASELINE #111776, SAME-SOURCE RECORD #111795, 2026-08-13/14)

- **唯一差异**：exp410从#111753只给case10打开`BF16_MMA_QK`；exp411再只给case5的BSM combined-page producer打开同一参数，并把静态前置条件放宽到已验证的`COMBINED_SPLIT_HEAD_QK`。最终相对#111753仅两处dispatch开关和该assert变化，SHA=`ec45265f6fbba5829a2e86c56800ef4541a6596a9b3ae969837d01abb35da081`。
- **资源/correctness**：case10从`86/62/5 waves→80/58/6`，case5从`86/56/5→74/52/6`，均8320 B shared、0 stack。CPU及GPU full/boundary/random各14/14；case10 16步、case5 19步精确长度和full→short→full均PASS。
- **A/B**：相对#111753双角色消偏约case10=`0.9563`、case5=`0.9823`，case14=`0.9981`；case4/6/7/8/9/11/12/13中性。提交前dry-run且队列为空，只创建#111776。
- **OJ结果/选择**：#111776最终14/14 Accepted / `65.29`，case1–14=`3/4/10/23/17/28/246/94/244/40/224/392/211/143 μs`，分数=`92/90/82/72/73/63/53/54/56/61/52/59/53/54`；相对#111753，目标case5/10从`18/42→17/40 μs`并分别增加2/1分，建立新baseline。用户随后要求试投平台，提交前队列为空且完成dry-run，只原样创建#111795；其正常14/14 Accepted / `65.36`，源码、raw和快照SHA与#111776完全一致。#111795选为当前分数记录与control，但`+0.07`及case3/9/12/13差异只作同源timing-tier样本。

### exp412-case13-kv8-z8-wave-local-bf16-mma  (LOCAL NEGATIVE / NOT SUBMITTED, 2026-08-13)

- **父版本/唯一假设**：从#111776/exp411只模板化`paged_decode_case13_kv8_headpair_z8_kernel`并仅给case13启用专用MMA QK；case12/9/7继续scalar z8。一个64-lane物理wave覆盖相邻两个z和四token，even z消费列0/1，odd z以quad XOR-2把列2/3送到既有owner；split256、K+V-over-PV、softmax/PV、packed metadata、partial和vec2 reducer不变。源码SHA=`a9ab4ab934a1daf515fe28950cafa5394ff00f296b25b2ec30710c4fc0890f15`，归档为`solutions/archive/2026-08-13-experiments/cuda_case13_kv8_z8_bf16_mma_exp412.cpp`。
- **正确性/资源**：独立probe 3 scales×4 seeds共12/12 PASS，最坏max error=`9.155273e-05`；生产case13的19个精确长度`1,2,15,16,17,239,240,241,255,256,257,479,480,481,3839,3840,3841,58965,58966`全部PASS，满长max error=`1.220703e-04`且finite。producer与scalar control同为`82 MTreg/50 STreg/8448 B/0 stack/5 waves`。
- **A/B/结论**：相对#111776 case13的9×20交错初筛`candidate/control p10/p50/p90=1.0699/1.0750/1.0794`，慢约7.5%。说明资源档不变仍不足抵消该映射的MMA准备/shuffle成本；候选未提交，工作文件恢复#111795。不得把同一映射扩到case12/9/7后期待补偿。

### exp413-415-z8-reduced-partial-splits  (ACCEPTED #111811/#111823/#111830, 2026-08-14)

- **唯一差异链**：从#111795依次只改变一个z8 shape的split，保留producer数学、同步K+V-over-PV、Q prescale、FP16x2 packed `(m,l)`、FP32 accumulator partial与原reducer family。exp413 case13 `256→64`；exp414 case12 `128→40`；exp415 case9 `24→6`。
- **本地/OJ**：双角色消偏约`0.9004/0.9253/0.8991`。#111811 case13 `212→190 μs`、53→55分，总分65.43；#111823 case12 `388→374 μs`、59→60分，总分65.57；#111830 case9 `243→237 μs`、56→57分，总分仍65.57（case3同源9→10 μs）。#111830源码严格优于#111823，曾选为control。
- **结论**：z8 ownership使旧split前提失效；减少global partial/workspace/reducer输入是当前真实有效主线。三个raw、逐提交源码与提交前SHA均已归档。

### exp416-case7-split1-direct-out  (ACCEPTED #111843 / REJECTED, 2026-08-14)

- **唯一差异**：从#111830给z8 kernel增加case7-only direct-out，case7 `split14→1`；CTA内合并八个z-state后直接归一化写BF16 output，删除partial workspace round trip和group8 reducer。其他shape保持原模板默认partial路径。源码SHA=`3b0567dce2d98536f4306c2d41d5200fb5c7c2b544e7067c0d3a4a25bf4aa604`。
- **初始门禁**：CPU/GPU full/boundary/random correctness各14/14及20个case7精确长度通过。full-length相对#111830正向p50约`0.8727`、反向old/new=`1.1441`，消偏约`0.8733`；但当时性能只强测了full-length。
- **OJ与事后归因**：#111843 14/14 Accepted / 65.43，case7却`246→279 μs`、53→50分。终态后补测同一binary：random candidate/control=`0.9912`，boundary=`1.2297`。OJ的capacity固定但batch内`cache_seqlens`变长；单split对短成员丢失并行度，解释本地full与OJ反转。不得把split1/direct-out扩到case9，也不得再用full-only性能门禁评估split/live-split候选。

### exp417-case7-split3-variable-length-safe  (ACCEPTED #111856 / FORMER BASELINE, 2026-08-14)

- **唯一差异**：从不可变#111830只把case7 `split14→3`，保留z8 producer、packed metadata、FP32 partial、fused-tail live count和group8 reducer。源码SHA=`7b0a0b1bac0b96255db49115562841a60ae8fa43d4be19395c28fa9f7b502fc4`，fresh binary SHA=`99da07be431febd0f11f31bc05467451f74c93182afbb30037922d37fa2e2a94`且两次构建字节一致。
- **正确性**：CPU14/14；GPU full/boundary/random各14/14；case7同进程`2048,1,2,15,16,17,42,43,44,85,86,87,127,128,129,1023,1024,1025,2047,2048`全部PASS、finite。
- **三分布A/B**：相对#111830正向full/random/boundary p50=`0.8766/0.9118/0.9344`；反向old/new=`1.1400/1.0971/1.0718`，三类均稳定正向。对照split2的random=`0.9554`但boundary=`1.2652`，证明split3是当前最小安全并行度。
- **OJ/选择**：提交前队列为空、dry-run正常，只创建#111856；14/14 Accepted / **65.71**，case1–14=`3/4/9/23/17/28/237/94/236/40/225/376/190/143 μs`，目标case7 `246→237 μs`并53→54分，14项均不劣于#111830。raw内嵌源码、逐提交快照与工作文件SHA一致，选择#111856为新control，队列为空。

### exp418-case13-wave-first-z-merge  (LOCAL NEGATIVE / NOT SUBMITTED, 2026-08-14)

- **父版本/唯一假设**：从#111856只给case13启用`WAVE_FIRST_Z_MERGE=true`。原z8状态用五次CTA barrier完成shared tree；候选先让物理wave内相邻z通过shared发布和`__syncwarp()`合并，再用两次CTA barrier合并剩余四路。case7/9/12保持原路径。源码SHA=`25a6ad8d30b5bcf9ad6fb0dae6f710978b2058df19ea73533c3ce0a50a0f5914`，binary SHA=`29fdcc161f2a325277424dcc31cf05c4605ea2f734dd88148596f78ee60e45ae`，完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case13_wavefirst_z_merge_exp418.cpp`。
- **资源/correctness**：control和candidate均为`82 MTreg/50 STreg/8448 B/0 stack/5 waves`；case13满长和17个split/tail边界长度全部PASS且finite。
- **A/B/结论**：正向candidate/control p50=`1.0052`，反向old/new p50=`0.9976`，双角色消偏约`sqrt(1.0052/0.9976)=1.0038`，稳定慢约0.38%。减少CTA barrier未抵消第一层shared发布/读取，拒绝且未提交；工作文件恢复#111856。

### submission-111868-baseline-chain-probe  (ACCEPTED / SAME SOURCE, 2026-08-14)

- **目的/过程**：用户要求尝试一次真实提交。提交前队列为空，#111856不可变源码SHA=`7b0a0b1bac0b96255db49115562841a60ae8fa43d4be19395c28fa9f7b502fc4`，dry-run正常；只创建#111868，不并发复投。任务正常经历`Pending→Running→Finished`。
- **结果/选择**：14/14 Accepted / **65.71**，case1–14=`3/4/9/23/17/28/236/94/236/40/224/374/190/143 μs`。raw内嵌源码与`solutions/archive/2026-08-14-submissions/cuda_111868.cpp` SHA均和#111856一致；case7/11/12的同源微小变化不作源码归因，不替换#111856默认control。raw、逐提交快照和manifest均已归档，终态后队列为空。

### exp419-exp420-case13-raw-wave-z-merge  (LOCAL NEGATIVE / NOT SUBMITTED, 2026-08-14)

- **假设/实现**：真实C500 probe确认FP32 raw BSM `lane^32`可逐bit交换物理64-lane wave两半，因此从#111856只替换case13末端z-state第一层shared merge。exp419让所有lane执行raw交换，exp420只让even-z做合并算术。
- **资源/性能**：exp419源码SHA=`904a0224fa82daee0bfa243965a9b854cac69826f054898ab84b5b10cf3a706a`，资源从`82 MTreg/5 waves`改善到`80/6`，correctness通过，但full/random双角色慢约0.1–0.2%。exp420 SHA=`8b093b41fa14dff24dda05544531fdc4b3dd7446743be7a5c27863ba1cfd8cbd`，资源回到`82/5`且full中性。
- **结论**：case13末端z-tree不是当前可兑现瓶颈；两份源码已归档，不提交，不再以同一raw交换微调算术参与lane。

### exp421-case13-z8-split65  (ACCEPTED #111882 / FORMER CONTROL, 2026-08-14)

- **changed precondition/扫描**：head-pair/z8 ownership和packed vec2 reducer使旧split结论失效。相对#111856重扫case13：split48/63/66/80 p50约`1.0724/1.0184/1.1068/1.1232`；split65相对split64在full约`0.9902`、random约`0.9875`、boundary约`0.9977`。split32错误落入generic group8 reducer导致correctness失败，不是性能证据。
- **门禁/OJ**：最终源码只改case13 `split64→65`，CPU14/14、GPU full/boundary/random各14/14和20个精确长度通过。#111882 14/14 Accepted / `65.71`，case1–14=`3/4/10/23/17/28/236/94/238/40/224/377/188/144 μs`；case13 `190→188 μs`并55→56分。aggregate被无关case3 `9→10 μs`抵消，但结构严格改善，故曾选为control。SHA=`db5ef3e5a4a00da5b585f3859843efa1a2ea0ed402bcf781bfd4424cad80e796`。

### exp422-case11-mma-split39  (ACCEPTED / CURRENT BASELINE #111886, 2026-08-14)

- **changed precondition/扫描**：lane-local BF16 MMA已让case11 producer快约20%，因此从#111882重新扫描producer/reducer平衡。split24满长最快但random回退；split32 full/random正向但boundary=`1.0580x`；split39/40是仅有三分布均正向的点。两者同为20 pages/live partial，选择39以少一个必空grid slot。
- **最终门禁**：源码SHA=`de0f662079b26717b6e69775768f330ca91d4f97b82707140fe9bd41472e34a5`，fresh binary SHA=`0d3f3815e3f3e64b2a73c90dcacef59f16132250a9f8a0095bede8a1c1cb4d54`。CPU14/14；GPU full/boundary/random各14/14；case11 `12251,1,2,15,16,17,319,320,321,639,640,641,12250,12251`同进程全部PASS。相对fresh #111882 control，full/random/boundary p50=`0.9925/0.9932/0.9573`。
- **OJ/选择**：提交前最近10笔全部终态、dry-run正确，只创建#111886；正常`Pending→Running→Finished`，14/14 Accepted / **65.79**。case1–14=`3/4/9/23/17/28/232/94/237/40/223/375/188/143 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/56/54`。唯一目标case11相对#111882 `224→223 μs`，与本地方向一致；其余变化无源码差异，不作因果归因。raw、逐提交快照和工作文件字节一致，#111886成为当前control，队列为空。

### exp423-case11-post-mma-phase-diagnosis  (TIMING-ONLY / NOT SUBMITTABLE, 2026-08-14)

- **目的/方法**：在#111886上临时加入默认关闭的`NO_MMA_QK`、`NO_PV`、`NO_NEXT_PAGE_IO`三种phase probe，分别删除case11 full-page的MMA-QK、softmax/PV或下一页K/V加载与shared发布；用`--skip-correctness`进行21轮×100次交错计时。三者都故意输出错误，删除阶段也会改变资源/live range，因此结果只表示成本上界，不能作为候选提交或直接相加。
- **结果/结论**：no-MMA-QK、no-PV、no-next-page-I/O相对#111886 p50分别为`0.8098/0.8279/0.9036`，对应约`19.0%/17.2%/9.6%`上界。旧scalar路径QK约占一半的结论已不适用于lane-local BF16 MMA基线；当前QK与softmax/PV成本接近，下一结构优先减少PV/softmax或同时改善page pipeline。正式exp423尚未选择；三个临时宏和条件分支已用`apply_patch`完全移除，工作文件SHA恢复为`de0f6620...e34a5`并与#111886逐字节一致。

### submission-111887-baseline-chain-probe  (ACCEPTED / SAME SOURCE, 2026-08-14)

- **目的/过程**：用户要求尝试一次提交。提交前最近任务全部终态；先移除上述错误输出的phase probes，以SHA-256和`cmp`确认工作文件与不可变#111886完全一致，再完成dry-run，只创建#111887，不取消、不并发复投。
- **结果/选择**：任务正常经历`Pending→Running→Finished`，14/14 Accepted / **65.71**；case1–14=`3/4/10/23/17/28/235/94/236/40/223/373/188/143 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/56/54`。raw内嵌源码、`solutions/archive/2026-08-14-submissions/cuda_111887.cpp`、工作文件与#111886 SHA均为`de0f662079b26717b6e69775768f330ca91d4f97b82707140fe9bd41472e34a5`。case11/13与#111886持平，总分低0.08属于同源timing-tier波动，不替换#111886 / 65.79 baseline；终态后队列为空。

### exp423-case11-wave-local-bf16-mma-pv  (LOCAL NEGATIVE / NOT SUBMITTED, 2026-08-14)

- **changed precondition/唯一假设**：旧BF16 P×V MMA结论来自不同producer与错误宏门控，本次在#111886的lane-local BF16 MMA-QK、K/V register-lookahead和owner-local softmax均已成立的新前提下，只把case11的四tokenFP32 PV替换为wave-local BF16 MMA P×V；QK、split39、loader、partial与reducer保持不变。独立probe 12/12 PASS，最坏误差`9.54e-7`；生产rolled源码SHA=`bdb1b04d767d17fa6c0351d8bdc9f92879a01a0642ab60751fad2fc6319590db`。
- **资源/correctness/A-B**：目标实例为`78 MTreg/68 STreg/8320 B/0 stack/6 waves`，完整case11 correctness通过；相对#111886交错A/B p10/p50/p90=`1.4490/1.4508/1.4537`，稳定慢约45.1%。BF16权重打包、fragment准备和MMA结果恢复远大于四token标量PV，拒绝且不提交。完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case11_wave_local_bf16_mma_pv_exp423.cpp`。

### exp424-case11-wave-private-shared-weights  (LOCAL NEGATIVE / NOT SUBMITTED, 2026-08-14)

- **唯一假设**：保持exp423的wave-local BF16 MMA P×V，只把每lane重复构造的softmax权重改为wave-private shared发布/读取，判断减少权重fragment准备能否兑现MMA吞吐；其他数据流不变。源码SHA=`db003554f62bb4e07d76b1140f0263973e40d71c51e932b9041d111a646be76f`。
- **资源/correctness/A-B**：目标实例恶化为`86 MTreg/64 STreg/8320 B/0 stack/5 waves`，full correctness PASS；candidate/control p10/p50/p90=`1.1214/1.1237/1.1257`，仍慢约12.4%。shared权重减轻部分重复转换但引入LDS/同步并降occupancy，拒绝且不提交。完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case11_shared_weight_pv_exp424.cpp`。

### xcore1000-official-v-fragment-loader-audit  (BACKEND LIMIT / CLOSED, 2026-08-14)

- **宏门控修正**：历史CUTE代码以`defined(__CUDA_ARCH__)`保护device body，而C500 MXMACA device pass只定义`__MACA_ARCH__`；因此历史部分probe/runtime从未把预期body发射到xcore1000，不能作为官方V-fragment loader可用证据。
- **官方实现审计**：`/opt/maca-3.7.1/include/cute/arch/copy_sm80.hpp`中的`MACA_ARCH_LDS_TRANS_ENABLED`只对xcore1500/1600开启；其`MACA_LDS_TRANS_4X16`依赖`__builtin_mxc_load_shared_trans_4x16_i64`，xcore1000/C500不支持。历史#104250只编译未launch probe，#104253实际走fallback；强制运行的#104255/#104259均约36秒后WA。
- **结论**：结合exp423已证明手工构造V fragment数值正确却慢45%，官方LDS_TRANS loader路线在C500关闭；除非后端新增xcore1000支持，不再集成或微调P×V MMA。

### exp425-case12-raw-wave-z-merge  (LOCAL MIXED / NOT SUBMITTED, 2026-08-14)

- **唯一假设**：从#111886只给`B8/L32768/KV8/split40` case12启用exp419已验证的raw `lane^32`第一层z-state合并；case7/9/13仍用原五barrier shared tree，producer page loop、同步K+V-over-PV、packed metadata、partial数量和vec2 reducer均不变。源码SHA=`74dce397663a641d956a1be4b15ec200866a9b507b9975515adb2cd64863b747`，完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case12_raw_wave_merge_exp425.cpp`。
- **资源/门禁**：case12专属实例从`82 MTreg/50 STreg/8448 B/0 stack/5 waves`变为`80/50/8448/0/6`，其他z8 shape保留control实例。CPU14/14；case12 GPU full/boundary/random、padding trap及同进程`32768→1→2→15→16→17→831→832→833→1663→1664→1665→32767→32768`全部100% PASS且finite。
- **三分布A/B**：21×100 full正向/交换角色p50均为`1.0002`，严格中性；random正向candidate/control=`0.9986`，反向old/new=`1.0020`，消偏约`0.9983`；boundary正向=`0.8861`，反向old/new=`1.1288`，消偏约`0.8859`，短live-split快约11.4%。
- **结论**：OJ case12当前容量workload为`373–375 μs`，full无收益、random约0.17%不足可靠跨分；不消耗OJ提交。该结果证明raw-wave树只在少量live split时明显有利，不能由静态`5→6 waves`推导满长收益。exact case12迁移关闭；按shape继续验证case9/7，不能全局打开。

### exp426-case9-raw-wave-z-merge  (LOCAL DISTRIBUTION REGRESSION / NOT SUBMITTED, 2026-08-14)

- **唯一假设**：从#111886只给`B32/L4096/KV8/split6` case9启用与exp425相同的raw `lane^32`第一层z-state合并；case7/12/13保持原shared tree，page producer、43 pages/split、packed metadata、partial和vec2 reducer不变。源码SHA=`d02b065541df5167af80da6bc92fbac3663a3077de31b25c8b46e1925cb44c7e`，完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case9_raw_wave_merge_exp426.cpp`。
- **资源/门禁**：目标实例同样由`82 MTreg/50 STreg/8448 B/0 stack/5 waves`变为`80/50/8448/0/6`。CPU14/14；case9 full/boundary/random及同进程20步`688 tokens/live split`边界全部100% PASS且finite。
- **三分布A/B**：21×100 full正向candidate/control=`0.9920`、反向old/new=`1.0089`，消偏约`0.9916`（快约0.84%）；random正向=`1.0352`、反向old/new=`0.9708`，消偏约`1.0328`（慢约3.28%）；boundary正向=`1.1081`、反向old/new=`0.9019`，消偏约`1.1084`（慢约10.84%）。
- **结论**：满长小收益与variable-length显著回退形成明确反转，违反OJ门禁，不提交。case9 exact raw-wave树关闭；静态occupancy提升和减少barrier仍不能替代live-split分布A/B。

### exp427-case7-raw-wave-z-merge  (LOCAL DISTRIBUTION REGRESSION / NOT SUBMITTED, 2026-08-14)

- **唯一假设**：从#111886只给`B64/L2048/KV8/split3` case7启用raw `lane^32`第一层z-state合并；split3、43 pages/split、packed metadata、partial和group8 reducer均不变。源码SHA=`49b6f23bb6a89f73cf90be705e760eb02ce1d1bcb418687a63b5f55d920fe4c3`，完整源码归档为`solutions/archive/2026-08-14-experiments/cuda_case7_raw_wave_merge_exp427.cpp`。
- **资源/门禁**：目标实例仍为`80 MTreg/50 STreg/8448 B/0 stack/6 waves`，相对control跨过`82/50/8448/0/5`档。CPU14/14；case7 full/boundary/random和`688 tokens/live split`的14步同进程边界复用全部100% PASS且finite。
- **三分布A/B**：21×100 full正向candidate/control=`0.9912`、反向old/new=`1.0106`，消偏约`0.9903`（快约0.97%）；random正向=`1.0412`、反向old/new=`0.9641`，消偏约`1.0393`（慢约3.93%）；boundary正向=`1.1130`、反向old/new=`0.8995`，消偏约`1.1124`（慢约11.24%）。
- **结论**：与case9相同，容量小收益不能覆盖variable-length回退，不提交。结合exp419/420 case13、exp425 case12、exp426 case9，本轮已按shape覆盖全部四个长KV8 z8 producer；raw-wave第一层z merge生产路线关闭，不再扩展或组合。

## 2026-08-14 最新实验续记（exp428–446）

以下条目补齐原 `notes.md` 未覆盖的 exp428–446。逐提交的完整 case 数据仍查 `results/cuda_result.md`，这里记录改变后续决策的实验因果。

### exp428-case12-all-native-bit2-qk  (ACCEPTED #111895 / COMPONENT KEPT)

- **唯一差异**：只把 case12 head-pair/z8 QK 从 `rotate8 → raw BSM XOR4 → quad2 → quad1` 改为 `rotate4 → rotate8 → quad2 → quad1` 全原生 shuffle，并把 head1 owner/broadcast 从 lane8 改为 lane4；split40、同步 K+V-over-PV、packed metadata、partial 和 vec2 reducer不变。SHA=`d69d1eacf5944f12181c44ba52202a73f490ae035c6b504da9a1ddbc4c428cfb`。
- **门禁/A-B**：资源保持 `82 MTreg/50 STreg/8448 B/0 stack/5 waves`；CPU14/14，case12 full/boundary/random correctness 与17步同进程复用通过；三分布双角色消偏约 `0.9937/0.9904/0.9892`。
- **OJ/结论**：#111895 14/14 Accepted / `65.79`，case12 `375→372 μs`；目标方向与本地一致，组件进入后续主线。

### exp429-case9-all-native-bit2-qk  (LOCAL DISTRIBUTION REGRESSION)

- **唯一差异**：把 exp428 的 bit2 网络只扩到 case9，其他结构不变。
- **结果/结论**：full 快约1.1%，但 random 慢约0.58%；违反三分布门禁，拒绝且未提交。后续 case9 改用不同 ownership 前提，而非原样扩展 bit2。

### exp430-case7-all-native-bit2-qk  (ACCEPTED #111897 / COMPONENT KEPT)

- **唯一差异**：只把 exp428 的全原生 bit2 QK 扩到 case7，保留 split3、group8 reducer、loader 与 partial。
- **门禁/OJ**：full/random/boundary 双角色约 `0.9879/0.9908/0.9726`；#111897 14/14 Accepted / `65.79`，case7 `235→234 μs`。组件进入主线，无源码差异的 case8 tier 波动不归因于它。

### exp431-case13-all-native-bit2-qk  (ACCEPTED #111904 / COMPONENT KEPT)

- **唯一差异**：只把全原生 bit2 QK 扩到 case13，保留 split65、同步 loader、z8、packed metadata、partial 与 reducer。
- **门禁/OJ**：full/random/boundary 约 `0.9731/0.9631/0.9933`；#111904 14/14 Accepted / `65.64`，case13 `188→183 μs`。目标收益成立，aggregate 回退来自其他 case timing。

### exp432/433-case13-split64/66  (LOCAL NEGATIVE / NEIGHBORHOOD CLOSED)

- **changed precondition**：在 exp431 更便宜的全原生 QK 下重新夹定 case13 split65 邻域。
- **结果/结论**：split64 慢约0.99%，split66 慢约13.8%并触发56-page cliff；split65仍是离散最优。不得继续同一前提下的 split 微扫。

### exp434-case13-native-bit1-ownership  (ACCEPTED #111908 / COMPONENT KEPT)

- **唯一差异**：case13 的全原生 QK 从 bit2 head/token ownership 改为 bit1；split65、page pipeline、partial 与 reducer不变。
- **门禁/OJ**：逐 lane probe 和完整门禁通过，full/random/boundary 约 `0.9900/0.9843/1.0000`；#111908 14/14 Accepted / `65.79`，case13 `183→182 μs`。进入主线。

### exp435/436-case13-bit0-and-order  (LOCAL NEUTRAL)

- exp435 的 bit0 ownership full 双角色约 `1.0000`；exp436 的 bit1 归约换序约 `1.0005`。
- **结论**：两者均为中性 source schedule，不提交、不继续排列同一 shuffle 顺序。

### exp437-case12-native-bit1-ownership  (LOCAL MARGINAL)

- **唯一差异**：只把 case13 已验证的 bit1 ownership 扩到 case12。
- **结果/结论**：约快0.21%，不足稳定跨 tier，拒绝提交；不得把这一亚百分比结果外推到其他 shape。

### exp438-case7-native-bit1-ownership  (LOCAL MARGINAL)

- **唯一差异**：只把 case7 从 bit2 改为 bit1。full correctness 通过，9轮交错 p10/p50/p90=`0.9967/0.9972/0.9982`。
- **结论**：远低于当时约1.8%的跨档需求，归档后拒绝提交。

### exp439-case9-native-bit1-ownership  (ACCEPTED #111918 / CURRENT STRUCTURAL CONTROL)

- **唯一差异**：只把 case9 改为 bit1 全原生 ownership；保留 split6、同步 K+V-over-PV、packed metadata、partial 与 vec2 reducer。源码 SHA=`c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`。
- **门禁/A-B**：CPU14/14，GPU full/boundary/random各14/14，17个 split/tail 精确长度和同进程 `full→short→full` 通过；full/random/boundary 双角色消偏约 `0.9854/0.9762/0.9649`，case7/12/13中性。
- **OJ/结论**：#111918 14/14 Accepted / `65.79`，case9 `237/238→234 μs`。目标有本地与 OJ 双证据，故成为结构性 control；case8/10 掉档没有源码差异。

### exp440/441-case9-bit1-split5/7  (LOCAL NEGATIVE / NEIGHBORHOOD CLOSED)

- **changed precondition**：在 case9 bit1 ownership 下分别只改 `split6→5/7`。
- **结果/结论**：full p50=`1.0148/1.0167`，分别慢约1.48%/1.67%；split6再次被两侧夹定，不继续同一邻域扫描。

### exp442-case7-native-bit1-finalist  (ACCEPTED #111929 / NOT CONTROL)

- **唯一差异**：从 #111918 只给 case7 启用 bit1 ownership。完整三分布、精确长度和复用门禁通过；full/random/boundary 双角色约 `0.9946/0.9970/0.9914`。
- **OJ/结论**：#111929 14/14 Accepted / `65.86`，目标 case7=`233 μs/54分`，未优于 #111918 的230 μs、更未跨到229 μs；aggregate并列来自无源码差异的 tier 波动。拒绝替换 control。

### exp443-case14-shared-mma-q  (LOCAL SEVERE REGRESSION)

- **唯一差异**：只把 case14 八个长驻 BF16 MMA-Q fragment 移入2 KiB shared Q tile；split257、fixed15 loader、PV、partial 与 reducer不变。SHA=`a0941ba9f321e0b1ad5d287f2145024aecf9e488098c6cad509ad11dab9977c8`。
- **资源/门禁**：`82 MTreg/62 STreg/8320 B/5 waves → 74/64/10368 B/6 waves`，CPU/GPU完整correctness通过；但 case14 21×100 A/B p10/p50/p90=`1.8488/1.8615/1.8673`。
- **结论**：逐页 LDS 和 staging barrier 远大于 occupancy 收益，稳定慢约86.2%。同一 shared MMA-Q 布局关闭；只有同时消除逐页 LDS 与 barrier 的全新数据流才可重开。

### submission-111942-control-resample  (HIGHEST SCORE / NO CODE CHANGE)

- 直接提交不可变 #111918 control，源码、raw 和逐提交快照 SHA 均为 `c0793eb9...fba3`。
- #111942 14/14 Accepted / **`65.93`**，case1–14=`3/4/9/22/17/28/232/94/234/40/224/373/181/143 μs`。
- **结论**：它仅以同源码 timing-tier 刷新最高分，不构成代码收益，结构性 control 仍是 #111918。

### exp444-case11-deferred-reference-basis  (LOCAL SMALL POSITIVE)

- **唯一差异**：online-softmax 的 `m` 改为 `(l,acc)` 的指数参考，只在 `m_page > m + 8` 时重缩放；不再要求每页更新成精确 running max。case11-only SHA=`399a9f13d16e6d0ae020b338e9a1c4e3fa91f130a762a976ff81aae24cea5e84`。
- **门禁/A-B**：完整correctness与workspace复用通过，资源保持 `80 MTreg/64 STreg/8320 B/0 stack/6 waves`；full/random/boundary p50约 `0.9941/0.9945/0.9930`。
- **结论**：数学与机制成立，但收益约0.6%，不足单独提交。

### exp445-case11-case14-deferred-reference  (LOCAL MIXED)

- **唯一差异**：把 exp444 同一状态流扩到 case14。SHA=`75fc8544ecdc1146788a494747adb105f35725b680baac1a02ebc7532070f8be`。
- **结果/结论**：case14 相对 exp444 的 full强测/random/boundary p50约 `0.9917/0.9853/0.9852`，但 case10 约慢0.5%；组合版不提交，先隔离模板/资源副作用。

### exp446-case14-only-deferred-reference  (ACCEPTED #111972 / NOT CONTROL)

- **唯一差异**：删除新增 production-kernel 模板参数，只从 case14 唯一 fixed15+MMA 特化派生 deferred-reference 开关，恢复 case11 原行为。提交 SHA=`50e02d06b6fd463982a7b768c6d903af14f2b92abf229dbcef19f3fe0ce81053`。
- **门禁/A-B**：case14资源 `82 MTreg/66 STreg/8320 B/0 stack/5 waves`；CPU14/14，GPU full/boundary/random各14/14；相对 #111918 的 case8/10/11/14 p50=`1.0012/0.9968/0.9982/0.9894`。
- **OJ/结论**：#111972 14/14 Accepted / `65.79`，目标 case14 仍为 `143 μs/54分`，未跨 tier；其余变化无源码差异。延迟 reference rescale 是本地约1.1%的正确组件，但同一阈值/状态流不得原样复投；只有能减少新增 STreg、避免每页 page-max 工作或改变 metadata 契约时才重开。工作文件恢复 #111918。

## 2026-08-14 深度进度审查与下一阶段实验队列

### A. 排名与真实收益规模

当前排名第5。结构性 control #111918 的14个整数 display point 合计为 `921`，平均 `65.79`；同源码最高 timing 样本 #111942 合计 `923`，平均 `65.93`。`leadboard.md` 的第三、第二、第一名分别对应约 `975/997/1002` 个整数点：

| 目标 | 榜单分 | 从 #111918 出发 | 从最高 timing 样本 #111942 出发 |
|---|---:|---:|---:|
| 第三名 | 69.64 | **差54点**；严格超过需55点 | 差52点；严格超过需53点 |
| 第二名 | 71.21 | 差76点 | 差74点 |
| 第一名 | 71.57 | **差81点**；严格超过需82点 | 差79点；严格超过需80点 |

结构决策必须以 #111918 的921点为起点；#111942多出的 case4/case8 两点没有代码差异，不能列入预计收益。六个“约1 μs到下一档”的 case 即使全部升一档也只增加 `6/14≈0.43` 总分，无法承担打榜主线。

按 `floor(100 * baseline / (baseline + time))` 对 #111918 做连续时延投影，并保持 edge case不变：

| 所有11个 perf case 同时改善 | 新增 display points | 推算总分 |
|---:|---:|---:|
| 5% | +14 | 66.79 |
| 10% | +30 | 67.93 |
| 15% | +42 | 68.79 |
| 20% | +57 | **69.86** |
| 25% | +72 | 70.93 |
| 30% | +88 | **72.07** |

如果只改善 case7/8/9/11/12/13/14 七个长 case，20%/25%/30% 只能得到 `68.57/69.21/70.07`；进入前三约需这七个 case 同时接近28%，冲击第一约需接近39%。因此下一阶段必须寻找可跨 shape 复用的数据流；单 case 亚百分比 schedule 只能作为最终收尾。

### B. 当前离散档位与杠杆

| Case | Shape | #111918 `μs/分` | 下一档最大时延 | 角色 |
|---:|---|---:|---:|---|
| 4 | B64/L64/KV8 | 23/72 | 22 μs | 近档辅线 |
| 5 | B16/L141/KV4 | 17/73 | 16 μs | 近档辅线 |
| 6 | B16/L362/KV8 | 28/63 | 27 μs | 近档辅线 |
| 7 | B64/L2048/KV8 | 230/54 | 229 μs | KV8主线兼近档 |
| 8 | B16/L4096/KV4 | 95/53 | 94 μs | KV4主线兼近档 |
| 9 | B32/L4096/KV8 | 234/57 | 229 μs | KV8主线 |
| 10 | B1/L8192/KV4 | 40/61 | 39 μs | 近档辅线 |
| 11 | B16/L12251/KV4 | 222/52 | 220 μs | KV4主线 |
| 12 | B8/L32768/KV8 | 372/60 | 365 μs | KV8主线 |
| 13 | B1/L58966/KV8 | 181/57 | 174 μs | KV8主线 |
| 14 | B1/L61519/KV4 | 143/54 | 140 μs | KV4主线 |

### C. 源码级瓶颈复核

1. **KV4 已从 scalar QK 转入平衡瓶颈。** case8/11/14 使用 `paged_decode_case11_headpair_z4_kernel` 和 lane-local BF16 MMA。case11 当前错误输出 phase probe 的成本上界为：MMA-QK约19.0%、softmax/PV约17.2%、下一页I/O约9.6%；三者不能相加，但足以否定“继续只排 MMA 指令就能大幅提速”。
2. **当前 Q operand 已经 hoist。** `mma_q_frag_bits[8]` 在 page loop 前一次装入；把 Q fragment“再移出循环”不是新方向。shared-Q exp443即使将5-wave推到6-wave仍慢86.2%，也不能换一种命名重试。
3. **当前 page pipeline 已经 wave-private。** 中间页 K/V register lookahead 以 `__syncwarp()` 发布本 wave 的4-token stripe；最后一页才因 K/V shared 被跨-z state reducer复用而执行 CTA barrier。笼统的“把 page barrier 改成 wave barrier”已经完成，剩余同步主要在最终 z-state 合并。
4. **KV8 的旧 partial 数量已大幅下降。** case7/9/12/13 的 split3/6/40/65来自真实收益；normalized-BF16 partial 在 case12/13 已中性或回退，raw/shared z merge也已逐 shape 关闭。下一步不能只压缩字节或换 reducer 线程数，必须改变长度调度、状态契约或有效 partial 数量。
5. **variable `cache_seqlens` 是真实性能维度。** case7 split1 full快12.7%，boundary却慢23%；raw-wave merge在 case7/9同样出现 full小增益、random/boundary大回退。固定 capacity 的静态 split 不能代表 batch 内真实长度分布。
6. **当前 MMA fragment 仍可能有结构余量。** `qk_two_heads_mma_owned_score` 每页执行8次 BF16 MMA，但 A-row group 明确为 `{head0, head1, zero, zero}`，最终只消费 `c[0]/c[1]`。`c[2]/c[3]` 是否能在不增加 MMA 次数、shared score或跨-wave handoff的前提下承载额外 head/token score，尚无生产映射证据；这是少数仍具有接近两位数理论上界的 QK 方向。

### D. 排序后的可证伪实验队列

下表的“预期”是进入实现的假设门槛，不是承诺。首轮均只改一个关键因素；凡未过静态门禁，不进入完整 GPU/OJ。

| 优先级 | 实验与目标 case | 首轮唯一差异 | 历史边界/为何不是原样重试 | 预期与停止条件 |
|---|---|---|---|---|
| P0-1 | **BF16 MMA fragment 有效密度 probe**；先 case11，成功后8/14 | 在独立 QK probe 中把当前 A-row 的两个 zero row 映射为额外有效 query/token，验证同样8次 MMA 能否正确消费 `c[2]/c[3]`；不先改 production | 不同于完整 score-tile、shared-Q、FP32 MMA和四head scalar布局：仍是当前 wave-local BF16 MMA，无 shared score、无额外 barrier、无 reducer变化 | probe须12/12映射正确且资源不高于当前 QK probe；若不能产生独立有效score或 production 预计需要额外 MMA/跨-wave handoff，立即关闭。若能把QK有效吞吐提高约2倍，case11端到端理论上界约9.5% |
| P0-2 | **lazy page-max + deferred basis**；case14→11→8 | 保留 `+8` 数值界，只把 page-max归约改为lazy fast path：owner score均未越过 reference guard 时跳过精确 page-max shuffle和acc rescale，越界时走原精确fallback | exp444–446仍每页无条件计算 page max；本实验改变的是 page-max工作量，不是阈值扫描 | 首轮目标 case14 p50至少快1.5%，STreg不高于66、0 stack，三分布均不回退；否则关闭。成功后再逐shape扩展 |
| P0-3 | **按 batch 实际长度均衡 split**；先 case7 | n_split仍为3，但 producer/reducer按每个 `cache_seqlens[b]` 计算 `pages_per_split_b=ceil(valid_pages/target_live)`，让非极短成员使用全部3个producer；full容量映射保持不变 | 不同于 split1/2/3静态扫描：消除的正是旧候选在短成员上只剩1个live split的失败前提 | full应在±0.5%内，random/boundary至少一项快2%且另一项不退；correctness覆盖每个动态分界。成立后才在新前提下单点复诊 split2，不做邻域扫描 |
| P0-4 | **单-LSE partial/state 契约**；case14 | normalized BF16 acc不变，把 packed `(m,l)` 改为单个 FP32 `lse=m+log2(l)`；reducer以 `exp2(lse-lse_max)` 合并，不再受 FP16 `l` 上界约束 | 不是 normalized-BF16/FP16x2 字节压缩重试：metadata仍4 B，核心目的是改变指数参考契约并为更稀疏rescale提供数学前提 | 隔离版允许中性，但资源不得降档、端到端不得慢超过1%；若 `log2` 成本明显回退则关闭。通过后与 P0-2 组合，使用由FP32范围推导的单一guard，不做阈值扫参 |
| P0-5 | **case11 动态均衡 split + 旧split32复诊** | 第一候选保持 n_split39，只按实际长度均衡39个逻辑owner；若三分布成立，第二候选才在新映射下固定测试 split32 | exp422 的 split32 boundary慢5.8%发生在 cap-derived静态分配；动态均衡直接改变该失败机制 | 第一候选 full中性、random/boundary合计有明确收益才继续；split32必须三分布全部不退且端到端至少快1.5%，否则保持39并关闭 |
| P1-1 | **MMA后 two-wave/z2 ownership资源探针（exp453 closed）**；case11 | 当前 lane-local BF16 MMA 下两个物理token wave各处理两个4-token chunk、一次z2 state merge | exp346/391发生在 scalar/split-head QK前提，分别48 B stack或慢34.5%；exp453改变为当前MMA数据流 | exp453=`84 MTreg/44 STreg/8320 B/0 stack/5 waves`，仅MTreg超`<=80`硬门槛；不跑GPU，关闭exact dataflow，不用split/reducer/loader/launch参数补偿 |
| P1-2 | **KV8 deferred/lazy basis**；case12→13→9/7 | 先仅把exp444的reference状态流移到一个z8 shape，split、z merge、partial/reducer全不变；后续再尝试lazy page-max | 旧证据只覆盖KV4 case11/14；不是raw-wave merge、BF16 partial或split扫描 | 目标shape三分布p50至少快1%，资源不降档；若只是亚0.5%或任一分布回退，不继续扩shape |
| P1-3 | **当前 control 的跨shape phase envelope**；case8/14/12/13 | 分别构建一次只删除一个阶段的不可提交 probe：MMA/QK、softmax/PV、page I/O、z merge、partial/reducer；绑定源码与binary SHA | 现有最新phase数据只有case11；旧case14比例来自scalar QK时代，不能指导MMA后架构 | 只用于排序，不要求correct output、不提交OJ。每个probe只改一阶段，记录资源变化，完成成本上界矩阵后停止，不把上界相加 |
| P2-1 | **z8有序 token-BSM 完整流水（exp454 closed）**；case12 | `wait(K)→QK→wait(V)→issue(Knext)→PV→issue(Vnext)`，保留z8/split40/partial/reducer | case4 token语义正确且case12 I/O上界高；exp454首次在实际两z/physical-wave布局验证 | exp454资源升级至`74/50/8448/0/6`且三分布正确，但full/random p50=`1.0067/1.0073`，boundary=`0.8933`；不扩shape，不重排同一wait/issue或仅改load拼写 |
| P2-2 | **cooperative/persistent phase能力门禁**；B1 case14/13 | 先做独立probe，确认C500 cooperative launch、全驻留grid sync、最大resident grid与一次phase barrier成本；不改solution | 旧 completion-counter/last-producer 与软件mbarrier均已失败；只有硬件/运行时确定性grid phase是changed precondition | 若不支持、需要超过可驻留grid或barrier成本接近现有reducer launch，立即关闭。只有probe成立才设计“producer→grid sync→reducer”且不得复用原atomic finalizer |

### E. 阶段执行顺序

1. 先完成 P1-3 当前控制的 phase envelope，同时并行做 P0-1 fragment probe；它们分别决定“钱花在哪”和“QK是否仍有架构级翻倍空间”。
2. KV4 主线按 P0-2 → P0-4 → 两者组合推进；P0-2隔离 page-max 工作，P0-4隔离 metadata/指数参考，不能首轮混在一起。
3. 调度主线按 P0-3 → P0-5 推进；同一实现框架先在 case7证明动态均衡语义，再覆盖case11，避免两个shape同时改。
4. P1-1只有通过资源门禁才占用GPU；P1-2在KV4状态流得到明确收益后再扩KV8。
5. P2方向先做builtin/runtime probe。没有新的后端能力或真实流水codegen，就不创建production候选。
6. 每3个同一微假设或每5个同一主线候选进行一次关闭审查；累计8–12个有效候选后重算 display-point空间。进入 OJ 的 finalist 必须先在最终组合 binary 上复测所有11个perf case和3个edge case，不能拼接历史逐case最佳。

## 2026-08-14 当前控制诊断与 exp448

### c500-bf16-mma-qk-resource-probe-slots4  (CLOSED / NO PRODUCTION MAPPING)

- **问题与边界**：保持当前 `(16,4,1)` lane-local BF16 MMA、相同8次 MMA、无 shared/barrier；把原本为零的 A rows 填成16个 Q rows，并写出 `c[0..3]`。这只验证 fragment capability，不代表存在合法 production ownership。
- **产物**：probe/driver SHA 分别为 `9fd45ded1005ca2ee8a0d204b7c42fc3bf535dae5b55b8a1d21f903edd3d2c81` / `cef52dd293afa5f5e185cfc423e945ff9e153da8b746d7e830cfc46bf218bb12`；C500 binary `build/c500_bf16_mma_qk_resource_probe_slots4.so` SHA=`44560c796e284a2081f2f9ca3b5552b175bc7f445d30f0c0f4e46e3320871be6`。
- **真实 C500 结果**：3个 scale × 4个 seed 共12轮中 `c[0]/c[1]` 均映射正确；填充后的 `c[2]/c[3]` 的 absmax 均为 `0.0`，driver 输出 `[PASS] c[0]/c[1] map correctly; populated c[2]/c[3] remain inert on C500`。
- **结论**：当前硬件/编译器下这两个槽不能形成额外有效 score；关闭“不增加 MMA、shared score 或跨-wave handoff 即翻倍 QK 有效密度”的 production 路线。不得把静态 fragment 推断替代真实 C500 结果。

### exp447-current-control-phase-envelope  (TIMING-ONLY / CLOSED)

- **父/control 与产物**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉。不可提交源 `solutions/archive/2026-08-14-experiments/cuda_phase_envelope_exp447.cpp` SHA=`41e2c5b64e3eef68ecf402f30c3d56c3d10db7e76f852e4771b6d0d6099d4914`；default binary SHA=`68f665a5c643d59c879275ba344455537af5cde469bab3090d804f43aec8ce78`。错误输出 variant binary SHA（no-MMA/no-PV/no-next-I/O/no-z-merge/no-reducer）依次为 `d8e8853b78e08f38b4a38c0c35bf8d699c122cd20688df094653d887da5ace11` / `0e5143d2b5b537cd2bd743f69c1ca3f268dbe02267d47c97ed7bf7e84e4b97d7` / `3243ca178ed063a6a889837bf9a62502ce4ea4373460b62cd41a71d4dfe0e876` / `2e6b760d24e1dc3477446f977a2f28e4571e339a0cde12cffa5c9e573d16f846` / `f7dbf12081bc903904e5da84da42e8b09bee0d3db2df241f00cdfd1da18378a7`。
- **方法**：default 相对 control 的 full p50 为 case8/12/13/14=`1.0020/1.0012/1.0017/1.0002`。每个 variant 只删除一个阶段，以 full-capacity `--skip-correctness` 测量 candidate/control p50；输出故意错误，禁止当作 correctness 或提交证据。

  | 删除阶段 | case8 | case12 | case13 | case14 |
  |---|---:|---:|---:|---:|
  | MMA/QK | 0.7991 | 1.0005 | 1.0035 | 0.8153 |
  | PV | 0.8861 | 0.9892 | 0.9476 | 0.8328 |
  | next-page I/O | 0.9121 | 0.8135 | 0.8361 | 0.9050 |
  | z merge + partial write | 0.7132 | 0.9373 | 0.8983 | 0.7538 |
  | reducer launch | 0.9354 | 0.9837 | 0.9456 | 0.8653 |

- **结论**：KV4 case8/14 的 QK、PV 和 z-state merge 都是大块上界；KV8 case12/13 最强新杠杆是下一页 I/O（约16–19%）。这些数值会随错误路径的资源/codegen 改变而变化，不能相加、不能承诺为可兑现收益、不能提交 OJ。

### exp448-case7-dynamic-valid-pages  (CORRECT / REJECTED LOCALLY)

- **父/control 与唯一差异**：从 #111918 分叉，最终源码 `solutions/archive/2026-08-14-experiments/cuda_case7_dynamic_pages_exp448.cpp` SHA=`df2483265c310e4b688b4fce87af50ec10bcede618e61501fd3f6bd727214738`，binary SHA=`b7358349aab8e48d3f1f47258af7f65de35ab8aef37c3b5857628bf1e0fd669f`。只给 case7 的 z8 producer/reducer 启用 `DYNAMIC_SPLIT_PAGES`：保留 `n_split=3`、grid、ownership、loader、partial ABI 和 reducer family；每个 batch row 用 `ceil(valid_pages/3)` 计算连续 page ranges。满容量仍是 `43/43/42` 页。
- **partial 契约修正**：尾页仍融合到最后 full-page owner，故 reducer 的 live count 必须按 `full_pages` 和动态 pages/split 计算；按 `valid_pages` 会在 full-page 数恰为局部倍数的尾页长度读到旧 partial。最终实现已用同一实际写槽公式，未改变 padding-page 边界。
- **资源/correctness**：case7 producer 从 control 的 `82 MTreg/50 STreg/8448 B/0 stack/5 waves` 变为 `86/44/8448/0/5`；group8 reducer 为 `66/23/0/0/7`（control `66/25/0/0/7`）。`c500_case_manifest.py`、`test_kernel_logic.py` 通过；最终 binary 的 GPU full/random/boundary 14/14 均通过。case7 同进程 exact `2048→1,2,15,16,17,42,43,44,85,86,87,127,128,129,1023,1024,1025,2047→2048` 全部100%匹配、finite，覆盖 workspace `full→short→full` 与 padding-page trap。
- **交错 A/B**：相对重新构建的 #111918 control，case7 的 9 rounds × 20 iterations（warmup=5）candidate/control p10/p50/p90 为 full=`1.0135/1.0150/1.0162`、random=`1.0463/1.0490/1.0652`、boundary=`1.0400/1.0444/1.0463`。
- **结论**：per-CTA 动态页数除法、尾页 ownership 控制和新增 producer registers 的成本压过了非满长度并行度；三分布均回退，不提交、不迁移到 case11、也不借此扫描 split2/32。只有能消除该动态调度成本的关键新前提才可重开。

### P0-2-lazy-page-max-row-guard  (OPEN BACKEND GATE)

- **changed precondition**：此前关闭的是未经实测的64-bit mask、lane-dependent cross-subgroup shuffle和8-lane subgroup。这里不把它们直接带入 attention：只验证 MACA 内建 `__any_sync`/`__ballot_sync` 对一个物理64-lane wave内、固定16-lane `ty` row mask 的语义和编译资源；guard 的输入仍是已有 owner score，既不交换数据也不改变 ownership。
- **可证伪门槛**：独立 probe 必须对 row-local true/false、跨-row isolation、两物理 z-wave 和高32位 mask 全部逐 lane 正确，并显示无 stack/无明显 resource 降档；否则 lazy page-max 不进入 production。即使通过，只证明 guard 能力，不证明端到端收益。

### exp450-case14-lazy-page-max-full-wave-guard  (OPEN CHANGED PRECONDITION)

- **为何可在 exp449 后再测一次**：exp449 的 row-local guard 正确但 case14 full 强测仅 p50=`0.9910`，且 producer 从 `82` 增至 `84 MTreg`。本轮不扫阈值或 split；唯一改为已由更新后 C500 probe 逐 lane 验证的固定 `~0ULL` physical-wave mask。任一 row/head hit 都使全部四个 `ty` rows 回到各自的精确 page max，因此它比 row mask 更保守但省去动态64-bit shift/mask；只有 resource 回到 control 且 full 强测达到原约1.5%门槛才继续。

### c500-lazy-page-guard-probe  (PASS / BACKEND CAPABILITY ONLY)

- **产物**：probe/driver SHA=`43dac2ce2c55f4686879d135e36b6a2bc0cb9ca7145ca38b2678d710bb447544` / `fc942b40d11a10b3ac8c7c087379b49fe012f411d258743b12853b932084375a`；binary SHA=`9cf92c97575a0b87286a80fd6af6c97c68125398fa6c7ed43ad8cba1a12cc70b`。
- **真实 C500**：`dim3(16,4,2)` 证明两物理 z-wave 各自 lane ID 重置为0–63。四个 pattern 覆盖 row-local true/false、高32位 bit、跨-row isolation、一个 z wave 命中而另一个空、所有 row 命中；`__any_sync(row_mask)`、`__ballot_sync(row_mask)` 和 `__any_sync(~0ULL)` 都逐 lane 匹配。semantic kernel=`14 MTreg/20 STreg/0 B/8 waves`，guard-shaped codegen kernel=`8/12/0/8`。
- **结论**：该结果只证明 fixed row/full-wave vote 的语义和轻量 codegen；不证明 attention 的端到端收益，也不解除其他未验证 mask/shuffle 前提。

### exp449-case14-lazy-page-max-row-guard  (CORRECT / REJECTED LOCALLY)

- **唯一差异**：从 #111918 分叉；source/binary SHA=`388dc2a6d69faeacb030daf4484974048928214fbd0c81c24ed8e9146af227ad` / `6845de4ad22d49fcab75d9aaf4211b695f09c3bf0ce33485c6e5a118734bc37e`。只在 case14 fixed15 BF16-MMA loop 使用已验证的16-lane row guard：安全页跳过两次 page-max shuffle 与 rescale，首次页或 hit 走原 exact max；generic/tail 保持 #111918。
- **资源/correctness**：producer=`84 MTreg/62 STreg/8320 B/0 stack/5 waves`（control=`82/62/8320/0/5`）。CPU回归通过；case14 full、random、boundary、20个精确长度及 `61519→short→61519` workspace 复用均100%通过。
- **A/B**：9×20 p10/p50/p90 为 full=`0.9816/0.9884/0.9947`、random=`0.9937/0.9985/1.0036`、boundary=`0.9749/0.9891/1.0532`；full 21×100 强测=`0.9867/0.9910/1.0001`。
- **结论**：数值正确但额外 row-mask 计算使 full 收益只有约0.9%，不提交。

### exp450-case14-lazy-page-max-full-wave-guard  (CORRECT / REJECTED LOCALLY)

- **changed precondition / 唯一差异**：保留 exp449 的 fixed15 lazy state和 exact fallback，只把动态16-lane row mask 换成 probe 已验证的固定 `~0ULL` physical-wave mask；任一 row/head guard hit 让全部 rows 各自精确归约。source/binary SHA=`0785ca618a301b7996b102b87b0ef444322f1d703c35b75f1ad5c5c5cf8f9ce8` / `3c41bfadc7350590aab9993b7c6f946ef21bc8f3ae3c392844be8cd15d343b4c`。
- **资源/correctness**：恢复 control 的 case14 `82 MTreg/62 STreg/8320 B/0 stack/5 waves`；case14 full/random/boundary和与exp449相同的20个精确长度、`full→short→full` 均100%通过、finite。
- **A/B**：full 21×100 p10/p50/p90=`0.9837/0.9879/0.9952`；random 9×20=`0.9904/0.9993/1.0058`；boundary 9×20=`0.9788/0.9836/0.9879`。
- **结论**：移除+2 MTreg后 full 仍只快约1.2%，低于预设约1.5%门槛，也不足 case14 从143降到140 µs所需约2.1%。row 与 full-wave guard 已夹定当前 exact fixed15 lazy-page-max 机制；不提交、不扫 mask/threshold。只有单-LSE或其他状态契约改变时才可重开。

### exp451-case14-single-lse-state  (CORRECT / STATE CONTRACT ACCEPTED / NO OJ)

- **changed precondition / 首轮边界**：exp449/450 的关闭结论只覆盖“保留 packed FP16 `(m,l)` partial metadata 与其 reducer 系数”的 exact/lazy page-max 家族。本轮保持 case14 的 fixed15 producer、BF16 MMA-QK、页最大值/重缩放、split257、normalized BF16 accumulator、loader、z merge 和 workspace 尺寸不变；唯一改变 partial state contract：4-byte metadata 从 FP16 `(m,l)` 改为 FP32 `lse=m+log2(l)`（空 partial 为 `-Inf`），reducer 以 `exp2(lse-lse_max)` 加权 normalized partial。它不扫 guard/mask/threshold，也不声称 byte-compression 收益；目的是先验证可作为后续 sparse-rescale/lazy-basis 前提的单一指数参考。
- **门禁**：producer/reducer 均须0 stack/spill、无静态 residency 降档；case14端到端若较 #111918 慢超过1%即关闭。资源通过后才跑CPU、full/random/boundary、精确长度与workspace复用；没有显著强于既有本地证据时不提交 OJ。
- **产物与资源**：父源码为 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）；完整候选 `solutions/archive/2026-08-14-experiments/cuda_case14_single_lse_state_exp451.cpp` 与当时工作文件SHA均为 `5d307b0f43b5a394750f6aea3bf7b9daf57719c437243dae9f2ea441c1a0df1d`，binary SHA=`fb6f680267c6360158b6703020ccbe3dfebaac9e585f08c6e7df0c210b6b5573`。producer=`82 MTreg/62 STreg/8320 B/0 stack/5 waves`，single-LSE reducer=`40/32/0/8`；均不低于control实例的驻留档。
- **correctness**：`c500_case_manifest.py`与`test_kernel_logic.py`通过；同一binary的C500 full/random/boundary各14/14均100% match、finite。case14在同一进程按 `61519→1,2,15,16,17,239,240,241,255,256,257,479,480,481,3839,3840,3841,61518→61519` 逐项100%匹配，覆盖padding-page trap、full→short→full与short→full workspace复用。
- **交错A/B**：相对fresh #111918 control的9×20轮candidate/control p10/p50/p90为 full=`0.9924/0.9971/1.0096`、random=`0.9850/0.9933/1.0054`、boundary=`0.9436/1.0015/1.0790`；case14 full 21×100强测=`0.9926/0.9956/0.9987`。无分布超过1%回退，但约0.4%满长收益不足现有case14约3 us OJ跨tier需要。
- **结论**：single-LSE在数学与资源上成立，但不替换结构性control、不提交OJ，也不把其亚百分比当作独立收益。它授权的唯一full-wave guard组合已在exp452完成；后者直接对exp450中性，因此当前case14 lazy/LSE state-flow整体关闭。

### exp452-case14-single-lse-lazy-wave-guard  (CORRECT / REJECTED LOCALLY / CLOSED)

- **changed precondition / 唯一差异**：exp450 已夹定“packed FP16 `(m,l)` metadata + fixed full-wave lazy guard”的收益，禁止重扫mask或`+8`。exp451 现已单独证明FP32 single-LSE partial/reducer既正确又不降档，因此本轮从#111918重新分叉，只把这两个已验证组件组合：case14 fixed15 MMA pages保留exp450的`~0ULL` guard、exact fallback和`+8`，partial/reducer使用exp451的FP32 `lse` contract。split257、QK/PV、loader、z merge、tail/generic exact path、workspace尺寸和所有其他shape均保持control；不引入第三项变化。
- **门禁/停止**：producer和reducer必须继续0 stack/spill且不低于`82/62/8320/5`与`40/32/0/8`；完整case14三分布和精确复用均须通过。full强测必须明显优于exp450的`0.9879`和exp451的`0.9956`，否则不再细调该guard/state组合、不提交OJ，并关闭当前case14 lazy-state-flow分支。
- **产物与资源**：父/control=#111918，SHA=`c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`；完整候选 `solutions/archive/2026-08-14-experiments/cuda_case14_single_lse_lazy_wave_guard_exp452.cpp` 与工作文件SHA=`bc8e4472543bdb9594b27ba78fc640be91716686410410b430ad7df614bf65a8`，binary SHA=`c5e63097acfcd74a3636ef50671adc508922e714c33bfa860e9afe6597640af5`。case14 producer=`82/62/8320 B/0 stack/5 waves`，single-LSE reducer=`40/32/0/8`，均通过资源门禁。
- **correctness**：CPU两项回归通过；同一binary C500 full/random/boundary各14/14均100% match、finite。case14同进程 `61519→1,2,15,16,17,239,240,241,255,256,257,479,480,481,3839,3840,3841,61518→61519` 全部100% match，覆盖padding-page trap、full→short→full及short→full workspace复用。
- **交错A/B**：对fresh #111918的9×20 candidate/control p10/p50/p90为 full=`0.9748/0.9846/0.9918`、random=`0.9916/0.9949/0.9998`、boundary=`0.9036/0.9839/1.0130`；full 21×100=`0.9822/0.9856/0.9907`。为消除跨时段timing tier影响，fresh exp450 binary与exp452同场full 21×100直接交错，exp452/exp450=`0.9966/0.9998/1.0039`。
- **结论**：尽管control-relative样本看似约快1.4%，直接A/B证明FP32 LSE没有给full-wave lazy guard带来可归因增益；其余分布也不形成跨tier证据。拒绝、不提交OJ，工作文件恢复#111918。关闭case14 fixed15 guard/LSE的所有当前前提，不以mask、阈值、同一guard source schedule或重命名metadata再试。

### exp453-case11-mma-two-wave-z2-resource-probe  (PLANNED / COMPILE ONLY)

- **父/control 与 changed precondition**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）重新分叉。exp346 的 `(16,4,2)` 两 wave / 每 wave 两个四-token chunk 使用的是 pre-current lane-local BF16 MMA 的 scalar/native-row QK，虽为 `80 MTreg` 却有 `48 B` stack；exp391 的 pair32/z2 则是另一套 `(32,4,2)`、每线程八 token 串行和跨 wave `xor16` handoff，虽无 stack 仍慢约34.5%。两者都不能直接否定当前控制中 `(16,4,4)`、8 次 BF16 MMA、register-local Q fragment、lane-local owner score 的数据流。
- **唯一假设与边界**：只为 case11 full producer 构造 `(16,4,2)` 资源探针。每个物理 token wave 顺序消费自身的两个四-token chunk，并对每个 chunk 复用当前 `qk_two_heads_mma_owned_score` 的 8 次 MMA、owner-score/max、FP32 online softmax 和 PV；K/V 仍按 chunk 做 register lookahead。z1 仅导出八个 head state，z0 做一次两路 `(m,l,acc)` merge。case11 split39、partial ABI、reducer、其他 shape、workspace 和 OJ dispatch均不作为本轮变量；本轮不得运行 C500 correctness、A/B 或 OJ。
- **预注册资源门禁/停止条件**：完整候选源码先归档到 `solutions/archive/2026-08-14-experiments/`，只用 `-resource-usage` 编译 full producer。只有 `0 B stack/spill`、`staticMaxWarps >= 5` 且 `MTreg <= 80` 三项同时成立才允许进入下一轮正确性设计；任一项失败即静态拒绝，记录源码/二进制 SHA 与资源输出，恢复工作文件到 #111918，且不以 split、reducer、loader 或 launch 参数补偿。
- **产物与资源结果**：完整源码为 `solutions/archive/2026-08-14-experiments/cuda_case11_mma_two_wave_z2_resource_exp453.cpp`，source/binary SHA=`b01d3976156582bc7fa2c48009ae77f88eae3508aad79e556d0abddb8b65ee12` / `63c463c9952f23ab07c7d55e66ce489b81ca425d6ae4d1a54b5b28713d408ac3`。`-resource-usage` 对 `paged_decode_case11_mma_two_wave_z2_resource_kernel` 报告 `84 MTreg / 44 STreg / 8320 B shared / 0 B stack / staticMaxWarps=5`。构建成功；既有的 `__launch_bounds__(..., 6)` MACA warning 与本 probe 无关。
- **结论**：虽然没有 spill 且保持5-wave，但 `84 MTreg > 80`，硬门槛失败。未运行 CPU/C500 correctness、A/B 或 OJ，也不把未验证的 full-only probe 当作可运行候选；工作文件始终保持 #111918 SHA。关闭“当前 register-local BF16 MMA + 两个顺序4-token chunk/wave + z2 single merge”的 exact source/dataflow，不以 split、reducer、loader 或 launch 参数作补偿性扫描。只有能实质减少 Q/state/next-page live range 或改变 consumer ownership 的新前提才可重开。

### exp454-case12-ordered-token-bsm-z8  (CORRECT / REJECTED LOCALLY)

- **父/control 与 changed precondition**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉。长KV8的旧默认 BSM async loader 在未证明请求 retire 顺序的流水下已回退，不能仅替换 load 拼写；但 exp281/282 已证明 `wait(V_current)→issue(K_next)` 是 scope-0 token BSM 正确的关键前提，且本轮重新构建 active probe 后，C500 对1025次 K/V 覆盖和跨lane读取再次通过。probe/driver/binary SHA=`23ec49438cddf53baa7c92993c6b3299a7937cc01a5f937487e46a4d450b8fb0` / `df1662071891ee525def397e27964decfd994c5c3c8ea89b7ac3cb83ecf48132` / `a9cf5ad6083b7092556555d47a01de79f0829b2d55a093ec327c4945919c1ee6`；probe资源=`14 MTreg/22 STreg/2048 B/0 stack/8 waves`。
- **唯一假设与边界**：只给 case12 的现有 `(16,2,8)` head-pair/z8 producer 增加 compile-time tokenized-BSM page pipeline。每页严格按 `wait(K_current)→QK→wait(V_current)→issue(K_next)→online-softmax/PV→issue(V_next)` 执行；K/V token use-def、split40、head-pair/z8 ownership、all-native bit2 QK、packed `(m,l)` partial、z merge、reducer、workspace 和所有其他shape不变。case12每物理64-lane wave含两个32-lane z partition，因此必须以该实际布局重新审查 page-ready/overwrite范围；case4 probe 不直接证明端到端安全。
- **预注册资源与验证门禁**：先只编译并检查 case12 producer。必须 `0 B stack/spill`、`staticMaxWarps >= 5`、`MTreg <= 82` 且 shared 不超过control的8448 B；否则静态拒绝且不跑C500。通过后才依次做CPU回归、同一binary的全14 case full/random/boundary、case12精确长度及workspace复用，再以#111918交错A/B覆盖三分布；三种p50均须至少约1%正向才保留，不满足不提交OJ，也不扩到case13/9/7。
- **产物与资源**：完整源码 `solutions/archive/2026-08-14-experiments/cuda_case12_ordered_token_bsm_z8_exp454.cpp` 的SHA=`2830dce29de887f96b08c0c85e565f55b950aed7003d91c4b1e9a6ad24eea940`，binary SHA=`a0c47df45cf898da4fdf49dff0536ecfa766c82f3b53f5c1f20126e90af0da97`。case12 token-BSM producer=`74 MTreg/50 STreg/8448 B/0 stack/6 waves`，相对同步control=`82/50/8448 B/0/5`通过资源门禁；fresh #111918 control binary SHA=`8d7469a6fd0eb40b33b2627c4f2434dfe0862c353c13a3318a79bf24ca787a30`。
- **correctness**：`c500_case_manifest.py`和`test_kernel_logic.py`通过；同一candidate binary的C500 full/random/boundary各14/14均100% match、finite。case12同进程精确序列 `32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768` 均100%匹配，覆盖split40的52-page边界、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B**：相对fresh #111918 control的case12 9 rounds×20 iterations（warmup=5）candidate/control p10/p50/p90为 full=`1.0061/1.0067/1.0078`、random=`1.0052/1.0073/1.0087`、boundary=`0.8894/0.8933/0.8972`。前两种分布紧密且稳定回退约0.7%，boundary虽快约10.7%，不能替代三分布共同门槛。
- **结论**：有序 token BSM 的 z8 semantic/dataflow 在当前 C500 上数值正确且降到6 waves，却没有把下一页I/O上界兑现为可复用收益；full/random反证其适合作为默认长KV8 loader。拒绝、不提交、不扩到case13/9/7，也不重排同一wait/issue schedule或仅改load拼写。只有改变实际等待覆盖、consumer ownership或多请求流水深度的关键前提才可重开；工作文件保持 #111918。

### exp447–454 阶段复盘与 P2-2 预注册（2026-08-14）

- **八个有效决策节点**：exp447完成当前control的跨shape phase envelope；exp448否决case7动态valid-page映射；exp449–452逐层夹定case14 lazy page-max/FP32 LSE state-flow；exp453以`84 MTreg`静态否决当前MMA two-wave/z2；exp454以full/random稳定回退否决case12有序token-BSM。所有结论均已绑定源码、资源或三分布A/B，工作文件仍为#111918。
- **display-point复核**：结构性control仍为921 display points，距用户维护的第三名69.64仍差54点；仅靠约1微秒的近档候选不足以弥合缺口。case8/14仍受QK/PV/z-state merge共同约束，KV8 I/O的最大错误路径上界虽高但exp454表明单一token-BSM不兑现为跨分布加速。禁止把错误phase上界相加或拼接不同提交的历史case时延。
- **下一能力门禁（P2-2）**：唯一尚未验证的全局契约是硬件 cooperative launch + full-resident grid phase，而非已关闭的completion-counter、last-producer或software mbarrier。先做独立 `c500_cooperative_phase_probe.*`：查询`cudaDevAttrCooperativeLaunch`、以当前case13 z8 producer实例计算实际active blocks/MP及总resident grid，并用最小`grid.sync()` cooperative kernel验证launch/phase语义。case13/14 producer grids分别为`1*8*65=520`与`1*4*257=1028`；若runtime不支持、实际resident grid不足任一目标，或硬件grid barrier不可用，立即关闭，不改solution、不跑OJ。只有case13至少可全驻留且phase语义成立才测一次barrier成本；case14若先天超过容量只作为独立否定事实，不外推给case13。

### P2-2 probe implementation contract (pre-run)

- **scope**：probe translation unit只 `#include` 不可变的 #111918 control，以`paged_decode_case13_kv8_headpair_z8_kernel<true,true>`向运行时查询实际 active blocks/MP；不修改、调用或替换 production `run_kernel`。另一个256-thread最小 cooperative kernel只做“各block写唯一值→全部线程`grid.sync()`→读取相邻block值”的phase可见性检查。
- **gate ordering**：先查询`cudaDevAttrCooperativeLaunch`、SM数、每SM线程/blocks/shared限制、exact case13 resource和occupancy；case13 resident grid不足520时直接记录关闭，绝不launch该grid、测barrier或改solution。只有case13满足520且最小kernel同样可驻留时才运行一次520-block semantic probe；case14的1028 block仅同其256-thread的thread-only上界比较，保持为不外推给case13的独立事实。
- **semantic-pass后的唯一测量**：若且仅若上述520-block语义通过，以相同256-thread cooperative launch、相同520 grid的无barrier/single-grid-barrier kernel交替计时；用两者每launch差值除以kernel内barrier次数得到一项 full-grid phase barrier 代价。作为停止尺度，另计时 exact #111918 case13 `paged_decode_reduce_vec2_kernel<true,false,true>` 的32-CTA reducer（finite dummy partial只用于量级，非正确性或候选）。若barrier已经与该reducer同量级则直接关闭；否则仅授权后续纸面设计审查，仍不改solution、不跑OJ。

### exp455-c500-cooperative-phase-capability  (CAPABILITY PASS / CASE14 CLOSED)

- **产物与边界**：独立probe源码/driver为 `tests/c500_cooperative_phase_probe.cpp` / `.py`，SHA=`3b5608d946f16b5933168b673a18eb04f41fff114bbbd217bcfc24d17749cbfc` / `0edc4bbbb0ce93670e8226801b388cee817f9d56c19b9107770b7ed45fdbe3d4`；最终binary SHA=`4901919707cbaf702f6045053f0669269b4740438fb79095f6df9adb197b7103`。它只include不可变#111918来取得精确template函数指针，不调用或改写production `run_kernel`；所有结果均为C500 capability/timing证据，不能提交OJ。
- **runtime capacity**：`cudaDevAttrCooperativeLaunch=1`；C500为104 SM、2048 threads/SM、16 blocks/SM上限、64 KiB shared/SM。`paged_decode_case13_kv8_headpair_z8_kernel<true,true>`的runtime attributes为`82 regs/8448 B shared/256 max threads`、`5 active blocks/SM`，所以case13的`8*65=520` CTA恰好完整驻留。最小phase kernel为`6 regs/0 B/8 blocks/SM`；barrier baseline/sync kernels为`4/0 B/8`与`9/0 B/8`，均能驻留832 CTA。case14的1028 CTA即使忽略寄存器/shared也超过`104*floor(2048/256)=832`的thread-only上界；这独立关闭case14，不能外推否定case13。
- **semantic/timing**：520 blocks×256 threads的cooperative launch完成“write unique phase-one→`grid.sync()`→read neighbor”且所有block匹配。以32个barrier/launch、4 launches/sample、9轮交替的额外单barrier p10/p50/p90=`2.811/2.830/2.854 µs`；exact current case13 32-CTA vec2 reducer在finite dummy partial上的launch p10/p50/p90=`11.310/11.354/11.384 µs`，barrier/reducer=`0.247/0.250/0.252`。barrier虽非免费，但约为reducer四分之一，未达到“同量级即关闭”的停止条件。
- **结论**：P2-2对case13通过且capacity没有余量；它不是可直接集成的solution，唯一许可的后续是下面的compile-only resource probe。case14 cooperative/persistent永久关闭；不提交、不改工作文件。

### P2-3 case13 cooperative producer-phase resource probe (pre-run)

- **changed precondition / 唯一差异**：exp455已证明此前不存在的硬件契约：精确520 CTA可全驻留并完成grid phase，且barrier仅为现有reducer约25%。从#111918完整复制一份experiment源码，只在case13 `paged_decode_case13_kv8_headpair_z8_kernel<true,true>`加入第三个compile-time开关；该实例在所有partial state完成写回后调用一次`cooperative_groups::this_grid().sync()`。不改default template、dispatch、split65、partial ABI、reducer、loader或其他shape。
- **特别边界**：原kernel对不live split会early-return，因此该resource-only实例绝不launch，也不运行CPU/GPU correctness；它只量化cooperative implicit argument/barrier是否使producer从5 blocks/SM降档。真正实现必须先重构为所有520 CTA（包括short/random的空split）均达到grid sync，并将exact reducer改为同kernel第二phase；那是本probe通过后独立的下一候选，不可混入本轮。
- **硬门槛/停止**：用`-resource-usage`和`cudaOccupancyMaxActiveBlocksPerMultiprocessor`检查目标实例。必须0 stack/spill、shared不超过8448 B、runtime active blocks/SM仍为5、总resident grid仍至少520；任一失败立即关闭case13 cooperative路线，不用reducer线程、launch参数或split补偿，也不占用GPU。通过只授权后续phase/reducer的纸面所有权审查。

### exp456-case13-cooperative-phase-resource  (STATIC PASS / NO LAUNCH)

- **产物与唯一差异**：完整源码 SHA=`a03a936ce1f836164266f080e218cbdc1eee12b896c5903234e4188235e3aa80`，driver 已归档为 `tests/archive/closed-backend-probes/c500_cooperative_phase_resource_probe.py`（SHA=`e6340d84b0cd548efb1fbb0dbd115565df9f96d5d04089cf1cd7317a9b266859`），重建 binary SHA=`a0b4647dbbe56c3c40420d08dcac3f2390eba2bdf71c374ba2a196f3f895100b`。相对#111918只加入`<cooperative_groups.h>`和case13第三个compile-time参数；`<true,true,true>`实例在原partial写回后调用一次`this_grid().sync()`，default dispatch仍是`<true,true,false>`。额外的host query只强制实例化并读取该specialization，未运行它。
- **静态/runtime资源**：`-resource-usage` 对特殊实例报告`82 MTreg/54 STreg/8448 B shared/0 B stack/staticMaxWarps=5`，与control case13的`82/48/8448/0/5`相比只增加6 STreg。C500 runtime attributes再次给出`82 regs/8448 B/5 active blocks/SM=520`，满足精确capacity gate。既有`__launch_bounds__(...,6)` warning来自control死模板，和probe无关。
- **结论**：cooperative implicit grid state和单barrier本身没有跨过case13的5-block residency悬崖，P2-3通过；因empty split仍会early-return，此binary绝不运行correctness/perf/OJ。只授权下列完整producer→phase→reducer resource candidate。

### P2-4 case13 cooperative persistent producer-reducer (pre-run)

- **唯一假设/所有权**：从exp456完整分叉，只给case13改变为一个cooperative 520-CTA kernel：所有CTA先按原producer写partial，空split只跳过page工作但绝不return；全部256线程执行同一`grid.sync()`；随后固定32个block（`blockIdx.y<4, blockIdx.x<8`）各合并一个`h=blockIdx.y*8+blockIdx.x`。每个chosen block仅其`tz<2`的64个线程（一个已验证的physical wave）执行当前`paged_decode_reduce_vec2_kernel<true,false,true>`的同一FP16x2 metadata/LSE/FP32 acc数学，原32/64-thread reducer的三道`__syncthreads()`改为该完整physical wave的`__syncwarp()`；其余448 block和其余线程在phase后直接退出。K/V buffer在producer写partial后已死，复用其8448 B shared的前528 B作reducer scratch；不新增global workspace、partial slot、split、loader、QK、state或reducer公式。
- **正确性边界**：full下65个split均生产；random/boundary空split仍参加grid sync，reducer以原`live_splits`只读已写slot。只在grid sync后访问cross-CTA partial，故不读padding block-table slot。该wave reducer改变了reducer同步scope，是同一persistent ownership假设的必要部分，必须先通过所有14 case三分布、case13精确split边界、padding trap与`full→short→full`/`short→full`，才有任何A/B。
- **资源门槛/停止**：先只build resource；目标cooperative full producer必须0 stack/spill、shared≤8448 B、runtime active blocks/SM≥5且resident grid≥520。任一失败静态关闭，不跑GPU，不改split/launch/reducer线程补偿。通过后才做CPU与C500 correctness；任何deadlock/mismatch/NaN立即关闭。性能A/B若full/random/boundary任一p50不正向或收益不超过barrier噪声，不提交OJ、不扩shape；case14仍禁止。

### exp457-case13-cooperative-persistent  (CORRECT / REJECTED LOCALLY / CLOSED)

- **父/control、唯一差异与产物**：从#111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉；完整候选为 `solutions/archive/2026-08-14-experiments/cuda_case13_coop_persistent_exp457.cpp`，SHA=`f425a4c8552085fe9dcdc78b9d969e03a7d7d9435949482e0c0b94632b7ad298`，binary SHA=`35b2105d356383943afa8e924f05b150d3977114929d80f073e4686f3a0d0968`。它只给 B1/L58966 case13 改为 520-CTA cooperative producer→`grid.sync()`→reducer：空 split 跳过 page work 但不 return；phase 后 `(blockIdx.y<4, blockIdx.x<8)` 的32个 CTA 各归约一个输出 head，且仅 `tz<2` 的一个物理64-lane wave 运行原 packed-metadata vec2 reducer的等价数学。前528 B producer-dead shared 重用为 reducer scratch；partial ABI、split65、loader、QK/PV、z-state merge、workspace和其余 dispatch不变。resource driver 已归档为 `tests/archive/closed-backend-probes/c500_cooperative_persistent_resource_probe.py`，SHA=`6661d73361352c2267b8061e1f996898e429fb60fff49c46fde82d35bf9c5643`。
- **资源门禁**：`-resource-usage` 的 persistent `<true,true,true>` 实例为 `82 MTreg / 60 STreg / 8448 B shared / 0 B stack / staticMaxWarps=5`。runtime query 为 `82 regs / 8448 B / 5 active blocks/SM = 520/520 resident CTA`，通过 P2-4 的严格容量门槛；说明 cooperative implicit state、wave reducer和共享 scratch没有跨过5-block residency cliff。
- **correctness**：`c500_case_manifest.py`、`test_kernel_logic.py`均通过。相同 binary 的 C500 full、boundary、random 全14/14均为100% match、finite；case13 full 首先单独通过，未发生 cooperative deadlock。case13随后在同一进程通过 `58966→1,2,15,16,17,239,240,241,255,256,257,479,480,481,911,912,913,1823,1824,1825,1839,1840,1841,3647,3648,3649,3839,3840,3841,58367,58368,58369,58383,58384,58385,58965→58966`，覆盖短尾、57-page owner/live-split转换、末端65-split转换、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B**：对fresh #111918 binary（SHA=`8d7469a6fd0eb40b33b2627c4f2434dfe0862c353c13a3318a79bf24ca787a30`）做case13 9 rounds×20 iterations（warmup=5）紧邻交替。candidate/control p10/p50/p90为 full=`1.0018/1.0038/1.0067`、random=`1.0235/1.0257/1.0271`、boundary=`1.1258/1.1445/1.1700`；各自 control/candidate p50 为 `0.1840/0.1846 ms`、`0.1511/0.1550 ms`、`0.0158/0.0182 ms`。三分布皆无正向，短长度固定启动520 CTA和全局barrier尤为不利。
- **结论**：能力与数值正确均不能兑现端到端收益；case13 exact 520-CTA single-request cooperative persistent producer、一次全grid phase和64-lane in-place reducer的组合关闭，不提交OJ、不改变control。不得仅更换chosen reducer block、`__syncwarp()`细节、launch顺序或把同一phase/reducer改名重试。只有多请求同驻留网格、producer/consumer ownership、partial contract或能消除短请求520-CTA固定成本的实质新前提，才可重新审查；case14的cooperative/persistent永久关闭保持不变。

### exp458-case12-dead-k-half-token-bsm  (INCORRECT / REJECTED)

- **父/control、唯一假设与 changed precondition**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉，完整源码为 `solutions/archive/2026-08-14-experiments/cuda_case12_dead_half_k_token_bsm_exp458.cpp`，SHA=`99c03427023868a881df61827d714a49a65920f9082582d0c58ee49f7ad70f26`。只给 case12 的 z8 producer 将 next-K 的四标量跨PV寄存器保存/回写，改为当前页 QK 后直接以 token-returning BSM 写入已经死亡的 `s_k` half；next-V 仍是control的四标量 K+V lookahead与原 `s_v` 写回。它不是 exp454 的双token `wait(K)→QK→wait(V)→issue(Knext)→PV→issue(Vnext)`：没有 outstanding V token，K producer/consumer ownership 改为 dead shared half。
- **静态门禁**：预处理输出确认实际路径含 `memcpy_async_pred<16, MACA_ICMP_EQ>` 和 `__builtin_mxc_barrier_and_wait4(0, token)`，不是同步fallback。source/binary/resource-binary SHA分别为上述 source、`048a54de9cf1279f14719f6815cf3badb3210e06d6be409ad830acfa744ae13e`、`87052d209fded49e7a248b71d675dbfe288898a39d94f29f9acfb8af128045ac`。case12 specialisation为`80 MTreg / 52 STreg / 8448 B shared / 0 stack / 6 waves`，对control `<true,false,false>` 的`82/52/8448/0/5`通过资源门禁。
- **CPU 与 C500 correctness**：`c500_case_manifest.py`和`test_kernel_logic.py`均通过。相同 C500 binary 的full、boundary各14/14通过、finite；但random中仅case12失败：match=`0.965942`、max_error=`4.431152e-02`、max_tol_ratio=`2.731`、finite，低于perf要求的99%元素容差率。其他13 case通过。
- **结论/停止**：随机变长已经否定该无pre-issue-wave-convergence的精确 token lifecycle；不得跑精确长度、A/B或OJ，也不得把full/boundary通过当作正确性。疑点是当前K shared sector在同一physical wave所有consumer退役前被异步producer覆盖；若继续，只允许把已证明需要的wave收敛作为单独exp459语义修复，并重新从资源与三分布correctness开始，不能把exp458结果作为性能证据。

### exp459-case12-dead-k-half-token-bsm-wave-release  (CORRECT / REJECTED LOCALLY)

- **changed precondition / 唯一差异**：仅在 exp458 的 next-K dead-half token lifecycle 发射前添加一次 physical `__syncwarp()` release；它确保同一wave的当前页K shared consumer在异步producer覆盖前全部退役，next页仍只以 token wait acquire。没有增加shared、split、partial、reducer、QK/PV、V lookahead或其他shape改动。完整源码为 `solutions/archive/2026-08-14-experiments/cuda_case12_dead_half_k_token_bsm_wave_release_exp459.cpp`，source/binary/resource-binary SHA=`a51a0a4bb94bd9ecd3d44e43ad69b58473841d41baf0a0c1aadd662bc3efc9c1` / `ebeacf86625170f4f58edad6210030f555589903d3eac140ee099f6364240587` / `a8e0ea357298d2c0da87b2f0e23ebc642d3600276d218f31e8ee58e259065119`。
- **资源与正确性**：case12仍为`80 MTreg / 52 STreg / 8448 B / 0 stack / 6 waves`，超过control的5-wave资源档。CPU两项回归通过；同一binary的C500 full/random/boundary全14/14均100% match、finite。case12在同进程 `32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768` 全部100%通过，覆盖52-page split边界、tail、padding-page trap、`full→short→full`与`short→full` workspace复用。
- **交错 A/B 与结论**：以fresh #111918 control（binary SHA=`8d7469a6fd0eb40b33b2627c4f2434dfe0862c353c13a3318a79bf24ca787a30`）跑case12 full 9 rounds×20，candidate/control p10/p50/p90=`1.0025/1.0037/1.0042`，即稳定慢约0.37%。已在full门禁失败，按预注册规则不再占用GPU跑random/boundary或OJ。关闭当前“single K token→dead s_k half、scalar V、每页wave release”的exact dataflow；不得只改release位置、token wait拼写或扩case13/9/7重试。V-only half-role-swap属于不同consumer ownership，若未来重开须独立资源/正确性论证。

### exp460-case12-v-dead-half-token-bsm-role-swap  (CORRECT / REJECTED LOCALLY / CLOSED)

- **父/control、唯一 changed precondition**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）重新分叉；完整候选为 `solutions/archive/2026-08-14-experiments/cuda_case12_v_dead_half_token_bsm_swap_exp460.cpp`，source SHA=`a35157eee08264dcdad5390e2ee330cb5154889c2315f106e05e93a2c6af6841`，binary SHA=`f9575a1453e88ec92045fe6a756c6b4bc03107019f7f7554160eb27ab0b84b73`。只给case12的z8 producer改变next-page V的consumer ownership：当前页QK后先retire已pending的V token，再以token BSM把V-next写入QK已死亡的当前`s_k` half；K-next仍按control读入四个scalar，在当前PV后写入已死亡的`s_v` half，随后每页交换局部K/V shared pointer。于是单个V token覆盖当前PV及下一页QK，且不与exp454的双token有序流或exp459的K-only dead-half流混合。
- **同步/后端与资源门禁**：每次异步V覆盖前保留一个physical `__syncwarp()` release，避免重现exp458的同wave K-consumer竞态；下一页QK之后、PV之前以该token的`__builtin_mxc_barrier_and_wait4(0, token)` acquire。预处理输出确认实际路径有`memcpy_async_pred<16, MACA_ICMP_EQ>`及该scope-0 wait，不是同步fallback。case12 specialisation为`76 MTreg / 56 STreg / 8448 B shared / 0 B stack / 6 waves`，相对fresh control `<true,false,false>` 的`82/52/8448/0/5`没有spill或驻留降档；MTreg下降而STreg上升4。
- **正确性**：`c500_case_manifest.py`与`test_kernel_logic.py`通过。相同binary的C500 full、boundary、random各14/14均为100% match且finite，包含padding-page trap。case12同进程精确序列 `32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768` 全部100%通过，覆盖52-page split边界、奇偶full-page角色交换、tail及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与结论**：以fresh #111918 control binary SHA=`8d7469a6fd0eb40b33b2627c4f2434dfe0862c353c13a3318a79bf24ca787a30`跑case12 full 9 rounds×20（warmup=5），candidate/control p10/p50/p90=`1.0159/1.0163/1.0184`；control/candidate p50=`0.7211/0.7329 ms`。full稳定慢约1.63%，故按门禁不再占用GPU跑random/boundary性能A/B，也不提交OJ。关闭“single V token→QK-dead s_k、scalar K→PV-dead s_v、per-page half-role swap”的exact dataflow；不得仅移动wait/release、改pointer swap拼写或扩case13/9/7重试。只有多请求流水深度或其他实质producer/consumer契约改变时才可重新审查。

### exp461-kv4-normalized-bf16-zstate  (CORRECT / REJECTED LOCALLY)

- **父/control、唯一假设与边界**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉；完整三-shape候选为 `solutions/archive/2026-08-14-experiments/cuda_kv4_bf16_normalized_zstate_exp461.cpp`，SHA=`6c50406e41e817a5aa5af3f81a50e9bb24740756100630aac1dba39d063cb251`。只改变head-pair/z4 CTA内共享z-state的accumulator contract：peer状态将`acc/l`以BF16x2写入已死K/V shared半区，`m,l`继续FP32；consumer按`peer_l * exp2(peer_m-m_all)`恢复其raw contribution。z-tree、barrier、QK/PV、split、loader、global partial ABI、reducer和workspace尺寸均不变。它不同于exp34的barrier-only row relocation，也不同于exp139的额外global partial offload。
- **资源门禁（已按完整19个模板参数复核）**：实际运行的case8 `<...,SKIP_EMPTY_RESCALE=true,BF16_MMA_QK=true,BF16_NORMALIZED_Z_STATE=true>`、case11 `<...,true,true,true>` 与case14 `<...,true,true>`特化分别为`82 MTreg / 66 STreg / 8320 B / 0 stack / 5 waves`、`80/60/8320/0/6`、`82/62/8320/0/5`，逐项保持#111918资源档。最初误读的`86/70/8320/0/5`属于源内早已存在、运行时由`preserve_case8_control < 0`排除的case8 exp300 dead specialization；重新以#111918 `-resource-usage`编译后确认control也生成同一`86/70`符号，不能归因给exp461。
- **correctness**：CPU manifest 与 `test_kernel_logic.py` 均为14/14；同一 candidate binary 的C500 full、random、boundary 各14/14、finite。case8、11、14 还分别覆盖了 split/tail 交界的17/17/20个精确长度，以及 `full→short→full`、`short→full` 同进程 workspace 复用和 padding-page trap；本回合再次运行CPU两项回归，仍通过。
- **交错 A/B**：以fresh #111918 control `build/cuda_111918_control.so`（SHA=`223ea7678df9e9f8635934098ca6516da91799ca70792df7b664b7ab7a4dbb5b`）对 candidate binary（SHA=`3294f82a043dbbec3f2780e6ef9382c436d3806b1e538cab322f151f16c0f703`）做 case8/11/14 各9 rounds×20 iterations、warmup=5 的紧邻交替。candidate/control p10/p50/p90 分别为：full：case8=`1.0093/1.0124/1.0154`、case11=`0.9998/1.0016/1.0092`、case14=`0.9980/0.9993/1.0046`；random：case8=`1.0129/1.0193/1.0244`、case11=`1.0015/1.0044/1.0100`、case14=`1.0009/1.0054/1.0122`；boundary：case8=`0.9944/1.0170/1.0779`、case11=`1.0074/1.0090/1.0115`、case14=`0.8465/1.0753/1.1522`。
- **结论**：资源档相同并未兑现为端到端收益：case8三分布中位数稳定慢约`1.24%/1.93%/1.70%`，case11慢约`0.16%/0.44%/0.90%`，case14只有full近中性、random慢约`0.54%`且boundary中位数慢约`7.53%`并高度离散。拒绝、不提交OJ；关闭当前“保持原z-tree/ownership、仅以BF16x2 normalized `acc/l` 经过共享存储、FP32 `(m,l)`不变”的完整三shape state contract。不得只改转换/打包拼写、启用范围或重新测同一契约；只有finalizer ownership、merge tree或实际共享读写量发生实质变化时才可重开。工作文件恢复#111918。

### exp462-case11-case14-normalized-bf16-zstate  (SUPERSEDED / NO GPU)

- **父/control、唯一收窄**：从#111918重建与exp461相同的CTA-local normalized-BF16 state contract，但只给case11/14 dispatch启用；case8显式保持`BF16_NORMALIZED_Z_STATE=false`。完整源码为`solutions/archive/2026-08-14-experiments/cuda_case11_case14_normalized_bf16_zstate_exp462.cpp`，source/binary SHA=`ba002c0a63b0eee0766e46a576ad2a0fd2becf57c5e071e8076ca2705141794c` / `6e9707b7a832a58f667b8982ba853f50f74257f7ea6ce852d94a60413460db5b`。
- **复核更正**：case8 false特化实际为`82/66/8320/0/5`，而非先前误归因的`86/70` dead exp300符号；因此没有“pointer污染”这一证据。此two-shape source既未运行CPU/C500，也不提供独立假设或收益空间，直接由资源已通过且覆盖更完整的exp461取代。
- **结论**：不构成接受或拒绝normalized-BF16 z-state的性能证据，不提交OJ；工作文件恢复exp461的三shape source继续门禁。

### exp463-case11-case14-normalized-bf16-zstate-scope  (SUPERSEDED / NO GPU)

- **产物与更正检查**：为验证先前误判而把BF16 pointer移动进true-only `if constexpr`，source/binary SHA=`eb809541b5784f42f5817ad117366dc6540421a0bb90eee6eb294866f1541d3a` / `0fc4566c155c3bff0315bdd25d7ea62b71ee1557ec300306032cee4d4627dacc`。它同样显示实际case8 false为`82/66/8320/0/5`，证明86/70从一开始就是control的dead exp300 specialization。
- **结论**：这是资源报告归因校正，不是新的数据流候选；未运行CPU/C500/OJ，恢复并继续exp461。

### c500-ldcs-ldlu-cache-policy-probe  (PASS / CLOSED)

- **问题与产物**：验证 MXMACA 的同步cache-policy builtin `__ldcs/__ldlu` 是否能对16-byte `uint4`提供独立、可安全集成的下一页I/O机制。源码/driver/binary SHA=`1e774469664a1b79bdb2767b487ab55d75b70d6993498cb37e9f93fee33e998d` / `0e79ca87abbd2e208d1ee9e119efea896ae596ce2d7d9125c43db97aa288abcb` / `9c3ad142696d74319aff8ce52952f9fb6828a7c4a560bf894be17532c804a2a7`。
- **静态与运行时证据**：`-resource-usage`为`20 MTreg / 20 STreg / 0 B shared / 0 stack / 8 waves`。device LLVM对`uint4 __ldcs`和`__ldlu`都降成四个32-bit普通load，且均带同一`!nontemporal`与`!metaxgpu.l2rp` metadata；没有单独的异步token、缓存预取或两种policy的codegen差异。真实C500以65537个随机`uint4`验证normal/`__ldcs`/`__ldlu`均逐字完全相同。
- **结论**：该同步cache hint有精确payload语义，但当前表达式会把控制中的16-byte vector load标量化，且不提供可与QK/PV重叠的请求生命周期。它不能作为“只换load拼写”的生产候选或OJ probe；只有后续有实质不同的loader consumer ownership、cache reuse或多请求数据流时才可重新审查。源码与driver移入`tests/archive/closed-backend-probes/`，不留在active root。

### exp465-case14-symmetric-deferred-reference-rescale  (CORRECT / OJ ACCEPTED / CURRENT CONTROL)

- **父/control、唯一 changed precondition**：从当前#112259 / exp464（source SHA=`6a2e2b797c831bdfe8f622bc4142c7711b4912e75d487db7ae177aca9db323d0`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case14_symmetric_deferred_rescale_exp465.cpp`，source SHA=`f79b1e9d639c5b550213c17ea244bf6be2cb9af43fc0dafc9a4a111386f0bd68`，binary SHA=`9656e1bc6a00c88e0615a042693bf5bb530775d10390ba805794a0531933a281`。唯一运行差异是仅在case14固定15-page BF16-MMA实例让`m`保持为`(l,acc)`的指数参考，只有页最大值超过当前reference 8个base-2 logit时才重缩放；case8/11、loader、split、QK/PV、z4对称finalizer、partial ABI、reducer与所有其他shape保持#112259。
- **changed-precondition 论证与资源**：exp444–446 已证明同一deferred reference rescale在旧z0-only finalizer下本地约快但#111972的case14仍为143 μs，故不得原样复投。本轮的父代码已把stage-2 z-state的共享写/终结ownership改为#112259对称finalizer，实际case14从143降至141 μs；因此旧OJ反证不能直接否定这一次独立组合。`-resource-usage`报告case14=`82 MTreg / 66 STreg / 8320 B / 0 stack / 5 waves`，与#112259同为5 waves且无spill/stack；fresh control binary SHA=`3dbaf3f00130ce7b69cb4871bdf09b83cc7c1b619695cf95886c8c3e06ae0db6`。
- **correctness**：`c500_case_manifest.py`与`test_kernel_logic.py`均通过；同一candidate binary的C500 full/random/boundary各14/14、100% match、finite。case14同进程精确序列`61519→1,2,15,16,17,239,240,241,479,480,481,3839,3840,3841,61518→61519`全通过，覆盖fixed15 split边界、tail、padding-page trap与`full→short→full`/`short→full`复用。
- **交错 A/B**：相对fresh #112259 control、case14的9 rounds×20 candidate/control p10/p50/p90为full=`0.9905/0.9988/1.0035`、random=`0.9748/0.9867/0.9928`、boundary=`0.9785/0.9936/1.0062`；满长21 rounds×100强测为`0.9965/0.9983/1.0002`。因此本地满长仅约0.17%正向，random/boundary有正向但不能外推为OJ收益。
- **OJ 终态与控制决策**：依照“OJ为性能真值、本地为筛选与归因”的持续授权，#112259终态且队列为空后，于2026-08-14创建唯一一次 OJ probe **#112302**（提交前/工作文件SHA均为上述`f79b…bd68`）。它正常经历`Pending→Running→Finished`，最终14/14 Accepted / `65.86`；case1–14=`3/4/9/23/17/28/233/93/229/41/222/374/182/140 μs`，分数=`92/90/83/72/73/63/54/54/58/60/52/60/56/55`。唯一目标case14真实`141→140 μs`、54→55分；虽然无关case的 timing-tier 波动抵消总分，目标因果、完整正确性、资源门禁和四方源码 SHA 一致性足以接受它为新的结构性control。工作文件恢复并保持#112302字节一致；相同`+8`阈值、store/barrier 拼写或启用范围不得复投/扫描。

### exp464-kv4-symmetric-finalizer  (CORRECT / OJ ACCEPTED / COMPONENT KEPT)

- **父/control、唯一 changed precondition**：从 #111918（SHA `c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`）分叉；完整候选为 `solutions/archive/2026-08-14-experiments/cuda_kv4_symmetric_finalizer_exp464.cpp`，source SHA=`6a2e2b797c831bdfe8f622bc4142c7711b4912e75d487db7ae177aca9db323d0`，运行 binary SHA=`f2e388f34c01f04646e5cb6c1c6ee213623289a39fc56bb229718ae095c1a7e9`。仅给 case8/11/14 的 KV4 z4 head-pair producer 启用 `SYMMETRIC_FINALIZER`：z0 将已合并 h1 写回已消费的 z2 row、z1 将 h0 写回已消费的 z3 row；一次 CTA barrier 后 z0 只终结 h0、z1 只终结 h1。QK/PV、loader、split、workspace、global partial ABI、reducer 与其他 dispatch 均保持 #111918。
- **资源门禁**：case8=`82 MTreg / 64 STreg / 8320 B / 0 stack / 5 waves`（control=`82/66/8320/0/5`）；case11=`80/58/8320/0/6`（control=`80/60/8320/0/6`）；case14=`82/62/8320/0/5`（control相同）。无 spill、无 resident-wave 降档；本轮 fresh control binary SHA=`223ea7678df9e9f8635934098ca6516da91799ca70792df7b664b7ab7a4dbb5b`。
- **正确性**：`c500_case_manifest.py` 与 `test_kernel_logic.py` 重新通过。相同 candidate binary 先前的 C500 full/random/boundary 均为14/14、100% match、finite；本轮再完成同进程精确长度：case8 `4096→1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095→4096`、case11 `12251→1,2,15,16,17,319,320,321,639,640,641,767,768,769,12250→12251`、case14 `61519→1,2,15,16,17,239,240,241,479,480,481,3839,3840,3841,61518→61519` 全部100% match、finite，覆盖 split/tail 边界、padding-page trap、`full→short→full` 与 `short→full` workspace 复用。
- **交错 A/B**：以同场 #111918 control 运行 case8/11/14、每种长度分布各 9 rounds × 20 iterations（warmup=5）。candidate/control p10/p50/p90 分别为：full：case8=`0.9977/0.9990/1.0018`、case11=`0.9944/0.9972/0.9980`、case14=`0.9785/0.9822/0.9904`；random：case8=`0.9868/0.9960/1.0026`、case11=`0.9926/0.9970/1.0022`、case14=`0.9779/0.9847/0.9872`；boundary：case8=`0.9522/1.0161/1.0824`、case11=`0.9884/0.9930/0.9977`、case14=`0.9539/0.9659/1.0176`。
- **OJ 终态与控制决策**：用户授权的一次 OJ probe **#112259**正常经历`Pending→Running→Finished`并14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/232/94/233/40/224/371/181/141 μs`、分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/54`。相对#111918，唯一改动覆盖的case14从`143→141 μs`、case8从`95→94 μs`；case11为224 μs，与同源#111942的224 μs旧control timing样本相同。raw内嵌源码、`cuda_112259.cpp`逐提交快照、实验源码和提交前工作文件SHA均为`6a2e2b797c831bdfe8f622bc4142c7711b4912e75d487db7ae177aca9db323d0`。OJ目标收益、完整正确性、资源门禁和本地机制证据共同足以接受该 exact finalizer ownership 为新的结构性 control；工作文件保持#112259字节一致。以后不得只换store row、barrier拼写或启用范围重试；只有merge tree、producer/consumer ownership或实际共享状态读写量的实质新前提才可重开。

### exp466-case14-symmetric-lazy-page-max  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112302 / exp465（source SHA=`f79b1e9d639c5b550213c17ea244bf6be2cb9af43fc0dafc9a4a111386f0bd68`）分叉；完整候选为 `solutions/archive/2026-08-14-experiments/cuda_case14_symmetric_lazy_page_max_exp466.cpp`，提交工作文件 SHA=`0a7f2cc6e50d87d38c8c6b08be74d9c39a5acdfbf85ed265ecb3172a65104160`。只在 case14 的 `seqlen==61519 && split<256` 固定15页 BF16-MMA 热循环中，先计算 lane-owned score；若整物理 wave 的任一 score 超过其所属 head 的现有 `m+8` reference，则回落到原来的两次 row16 exact page-max shuffle，否则直接以现有 reference 作 basis。tail、generic loop、split、loader、QK/PV、z4 对称 finalizer、deferred reference-rescale、partial ABI、reducer 与其他 case 不变。exp450/452 在旧 finalizer/reference 数据流下的反证不能直接覆盖此组合；#112302 已由 exp464/465 建立新的 symmetric-finalizer + deferred-reference control。`~0ULL` full-wave guard mask 不引入未验证 primitive，已由归档 `c500_lazy_page_guard_probe` 的真实 C500 语义验证。
- **资源与正确性**：重新从该 SHA 构建 normal/resource binaries，SHA 分别为`62b799ba25c630892f51b0715b135c5b788db745773e3c598684fbf8ede58020`和`c8eb19c9f9ac9b9c2c622d30cbaaddb6916dc6ab63c650526776128f5277552f`；与 fresh #112302 resource build 的28个 function properties逐项相同，均无stack/spill或static-wave降档。`c500_case_manifest.py`和`test_kernel_logic.py`通过；相同 candidate binary 的 C500 full/boundary/random 均为14/14、100% match、finite，且 padding slot 保持合法物理 page ID。case14同进程序列`61519→1,2,15,16,17,239,240,241,479,480,481,3839,3840,3841,61518→61519`全部通过，覆盖 fixed/generic 边界、tail、padding trap 与`full→short→full`/`short→full` workspace复用。
- **交错 A/B、OJ终态与关闭**：相对 fresh #112302 control（binary SHA=`e59d700d909e3326dd16ee1c09f4c3d02897bef879a43c27b808642e545f1e4b`）以9 rounds×20、warmup=5紧邻交替，case14 candidate/control p10/p50/p90 为 full=`0.9959/0.9983/1.0058`、random=`0.9933/1.0009/1.0078`、boundary=`1.0052/1.0146/1.0307`。lazy path只在 OJ full-capacity fixed15 common splits运行，random/boundary数字主要检验未改generic路径与binary布局；本地 full 信号约0.17%，不足以独立证明跨约3 µs tier。依照“OJ为性能真值、本地性能为辅助”的持续授权，队列为空后只提交该 SHA 一次，预注册唯一问题是：删除 safe-page exact-max shuffle 是否使 OJ case14 从140 µs跨到下一档。#112355正常经历`Pending→Running→Finished`，最终14/14 Accepted / `65.79`，case1–14=`3/4/9/23/17/28/233/93/234/41/223/374/181/141 μs`、分数=`92/90/83/72/73/63/54/54/57/60/52/60/57/54`；目标case14反而`140→141 μs`、55→54分。OJ直接否定该预注册性能假设，拒绝且关闭，不切换control；不得以本结果扫阈值、换mask/guard/store/barrier拼写或密集复投。
- **源码身份隔离与恢复**：raw内嵌源码、`cuda_112355.cpp`逐提交快照、实验源码和提交时工作文件SHA均为`0a7f2cc6e50d87d38c8c6b08be74d9c39a5acdfbf85ed265ecb3172a65104160`。并行 sidecar 曾把当时工作文件复制为 `solutions/archive/2026-08-14-experiments/cuda_kv8_symmetric_finalizer_exp466.cpp`（SHA=`429ef2cc27a24c85eb95d98b6ea20bfd4320362d4a42a6ad118b8a0aa0120e2b`），随后又叠加 KV8 case13 finalizer 差异；它不是相对 #112302 的单一差异，故其局部 C500 结果不计入本 exp、不构成 OJ finalist 或 future control。保留该文件仅作可追溯证据；最终工作文件已恢复#112302的`f79b1e9d639c5b550213c17ea244bf6be2cb9af43fc0dafc9a4a111386f0bd68`。

### exp467-case10-vec2-register-packed-ml  (CORRECT / OJ ACCEPTED / CURRENT CONTROL)

- **父/control与唯一差异**：从 #112302（SHA=`f79b1e9d639c5b550213c17ea244bf6be2cb9af43fc0dafc9a4a111386f0bd68`）分叉；候选工作文件 SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`。仅让case10的64-thread vec2 reducer在global-max期间以寄存器保留每lane的两组packed FP16 `(m,l)`，shared中只写最终softmax weight，动态shared metadata从`1032 B→520 B`。producer、split128/每split四页、partial ABI、live-split公式、block geometry及输出数学均不变。
- **资源与正确性门禁**：candidate case10 reducer=`38 MTreg / 36 STreg / 0 stack / 8 waves`，control=`38 / 39 / 0 / 8`。CPU manifest/logic回归通过；同一C500 binary的full、boundary、random各14/14通过。case10同进程精确序列`8192→1,2,15,16,17,63,64,65,127,128,129,255,256,257,8191→8192`全部finite且在容差内，覆盖split/tail边界、padding-page trap与`full→short→full`复用。
- **交错 A/B 与预注册**：candidate/control p10/p50/p90为full=`0.9664/0.9991/1.0090`、random=`0.9801/0.9965/1.0111`、boundary=`0.9382/1.0047/1.1023`。本地信号接近噪声，但metadata-lifetime机制、资源门禁和完整correctness使一次OJ probe具有信息价值。确认无在途任务并对同一SHA dry-run后创建唯一提交 #112399；预注册问题是此reducer能否使OJ case10 `41→40 μs`。不得参数扫描、改guard/threshold或同源复投。
- **OJ终态与 control 决策**：#112399经历`Pending→Running→Finished`后14/14 Accepted / `65.86`；case1–14=`3/4/9/23/17/28/233/93/230/40/223/373/182/140 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/56/55`。唯一预注册目标case10实际从#112302的`41→40 μs`、60→61分。case9同场从229到230 μs没有对应运行差异，aggregate因该timing-tier波动持平，不能用它否定case10的直接源码因果；资源、完整correctness、本地A/B和OJ目标共同支持接受该exact reducer metadata-lifetime为新结构性control。raw内嵌代码、`solutions/archive/2026-08-14-submissions/cuda_112399.cpp`和提交时工作文件SHA均为`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`，当前工作文件保持该字节内容。关闭case10这一 exact metadata-lifetime 的参数/拼写微调和同源复投；其他reducer shape只有出现不同的live metadata、consumer ownership或资源前提时才可独立重开。

### exp469-kv4-row-coeff-final-merge  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异**：从 #112399（SHA=4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d）分叉；完整候选为 solutions/archive/2026-08-14-experiments/cuda_kv4_row_coeff_final_merge_exp469.cpp，候选/工作文件 SHA=c915c0ac58eae2650e31235a8d5f7aa846bae13b90a6c5b397bec52dfe437e58，normal/resource binary SHA=3b21b0bb4a00b61ca3ad1a2060eee9f63b77538399d560952c73b1a779eccce0 / e72ad5b613784c7f62683acded1d588c3be9ecff879f496e4b567907d1c3d94b。仅给 case8/11/14 的 KV4 z4 final merge 启用 row coefficient ownership：每个 native 16-lane row 的 tx=0/1 分别计算 local/peer 的 exp2 merge 系数，再以 row-local broadcast 分给原有 lane-private accumulator scaling。producer、QK/PV、split、z4 对称 finalizer、case14 deferred reference-rescale、partial ABI、reducer、barrier 和其他 shape 不变。
- **资源与正确性**：resource build 保持 case8=82 MTreg/64 STreg/8320 B/0 stack/5 waves、case11=80/58/8320/0/6、case14=82/66/8320/0/5，没有驻留档或 stack/spill 回退。manifest 与 CPU logic 14/14 通过；同一 C500 binary 的 full/random/boundary 均为14/14、100% match、finite。case8 的 4096→1,2,15,16,17,303,304,305,4095→4096，case11 的 12251→1,2,15,16,17,319,320,321,639,640,641,12250→12251，以及 case14 的 61519→1,2,15,16,17,239,240,241,479,480,481,3839,3840,3841,61518→61519 均在同一进程通过，覆盖 padding-page trap、split/tail 边界、full→short→full 与 short→full 复用。
- **交错 A/B**：以 fresh #112399 control、warmup=5、20 iterations、9 rounds 得到 candidate/control p10/p50/p90：full case8=0.9967/1.0057/1.0144、case11=0.9981/1.0001/1.0019、case14=1.0015/1.0045/1.0070；random case8=0.9963/0.9981/1.0069、case11=0.9982/1.0007/1.0038、case14=1.0033/1.0058/1.0135；boundary case8=1.0349/1.0509/1.1023、case11=0.9981/0.9997/1.0025、case14=1.0095/1.0202/1.1090。没有共同本地正向，尤其 case8/14 boundary 有稳定回退。
- **预注册 OJ 问题、终态与关闭**：本地 C500 与 OJ 计时环境不是同一真值；本候选具有单一可证伪的 coefficient-consumer ownership 变化、完整正确性和资源门禁，故按 goal 的持续 OJ 授权只提交一次，检验真实 OJ 是否会让已部署的 case8/11/14 final-merge 路径产生任何目标改善或跨档。#112430正常经历`Pending→Running→Finished`，最终14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/233/93/233/39/222/373/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/62/52/60/57/54`。目标case8保持93 μs，case11从223降到222 μs但仍52分，case14从140回退到141 μs、55→54分；case10/13的同场加分无对应运行差异，只是timing-tier波动。OJ直接否定该预注册性能假设，拒绝且关闭这条 exact row-coefficient final-merge 路线；不得改变broadcast source、tx owner、barrier或enable scope后密集复投。raw内嵌代码、`cuda_112430.cpp`逐提交快照和实验源码SHA均为`c915c0ac58eae2650e31235a8d5f7aa846bae13b90a6c5b397bec52dfe437e58`，工作文件已恢复#112399。

### exp470-kv8-vec2-register-packed-ml  (CORRECT / REJECTED LOCALLY / CLOSED)

- **父/control与唯一差异**：从#112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_kv8_vec2_register_packed_ml_exp470.cpp`，SHA=`99b101fe1de8f7104bec043adf757b03e5127e036d90be9bdcda19d2ce795668`。只给case12/13的64-thread vec2 reducer启用`REGISTER_PACKED_ML=true`：每lane把一至两组packed FP16 `(m,l)`保留跨global-max，shared只承载最终weight，动态shared metadata由`2*n_split+2`个float降为`n_split+2`个float；producer、split40/65、partial ABI、live-split、block geometry和数学不变。
- **资源、正确性与交错 A/B**：reducer为`38 MTreg / 36 STreg / 0 stack / 8 waves`，通过资源门槛。CPU与C500 full/random/boundary、精确split/tail长度、padding-page trap和`full→short→full`/`short→full`复用均通过。相对fresh #112399、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full：case12=`0.9996/1.0003/1.0015`、case13=`0.9998/1.0006/1.0018`；random：case12=`0.9990/1.0020/1.0041`、case13=`0.9997/1.0009/1.0026`；boundary：case12=`0.9960/0.9976/1.0014`、case13=`1.0102/1.0287/1.0534`。没有共同正向且case13 boundary稳定回退，故不提交OJ；关闭这一 exact case12/13 register-packed-metadata lifetime，不以shared大小、注册owner或同一reducer树拼写重试。工作文件保持#112399。

### exp468-kv8-z8-symmetric-finalizer  (CORRECT / REJECTED LOCALLY / CLOSED)

- **父/control、唯一 changed precondition**：从当前#112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_kv8_z8_symmetric_finalizer_exp468.cpp`，source SHA=`a1dbe827308fec3881862be44b29524daf7e9f865ca4bce0abbf4f0bf9ac4674`，normal/resource binary SHA=`f7132d6ce1ecb4fe4a03056790eba19457538f5cf0e57eefef4f595dfe29f5a2` / `62894e294f70dcd9cee3e48620810bbb447d39d415f8a1dcac04c20a02a16e9a`。只改KV8 z8 in-place tree 的最后一层：原先z1写入两个head状态、z0顺序合并并写两个partial；候选让z0把已合并的h1写入已死row、z1把h0写入另一已死row，经原有CTA barrier后z0/z1各合并并写一个head的partial。两个logical z半波位于同一physical 64-lane wave；producer、QK/PV、loader、split、partial ABI、live-split、reducer和workspace均不变。
- **资源门禁**：对#112399与候选分别以`-resource-usage`构建。两条KV8 z8特化`<true,false>`/`<true,true>`均为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`与`82/48/8448/0/5`；无spill、无驻留档变化，静态门禁通过。
- **correctness**：CPU manifest与`test_kernel_logic.py`均14/14通过。相同candidate binary的C500 full、boundary、random各14/14、100% match且finite，padding slot保持合法物理page ID。受影响case的同进程精确复用亦全通过：case7 `2048→1,2,15,16,17,687,688,689,1375,1376,1377,2047→2048`；case9 `4096→1,2,15,16,17,687,688,689,1375,1376,1377,2063,2064,2065,4095→4096`；case12 `32768→1,2,15,16,17,831,832,833,1663,1664,1665,32767→32768`；case13 `58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58965→58966`。这覆盖tail、各split边界、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与结论**：以fresh #112399 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为：full case7=`0.9979/0.9999/1.0010`、case9=`0.9991/1.0004/1.0017`、case12=`0.9996/1.0006/1.0017`、case13=`1.0009/1.0022/1.0046`；random case7=`0.9954/0.9986/1.0082`、case9=`0.9983/1.0000/1.0033`、case12=`0.9991/1.0005/1.0053`、case13=`0.9996/1.0011/1.0075`；boundary case7=`0.9952/1.0009/1.0102`、case9=`0.9955/1.0011/1.0106`、case12=`0.9921/0.9995/1.0057`、case13=`0.9188/1.0656/1.1041`。没有任何可重复、多分布的正向，case13 boundary反而高噪声且中位数慢约6.6%。因此不提交OJ；关闭“KV8 z8最后树层以dead-row handoff让z0/z1分别终结一个head”的exact finalizer ownership。不得只改store row、barrier拼写或选定head重试；只有merge tree、跨半波consumer ownership或实际共享读写量出现实质新前提时才可重开。工作文件已恢复#112399字节一致。

### exp471-case12-fixed-full-page-producer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case12_fixed_full_page_exp471.cpp`，候选/工作文件 SHA=`769be1717e559bcdaadf5f9b4e21401f6eaea3ca05dd11f19b8ae2e3ea856405`。只给case12满容量的z8 producer增加一个严格guard：`seqlen==32768 && n_split==40 && pages_per_split==52 && split<39`。2048个full page中的前39个split各有52页；其前51次next-page转移以编译期`HAS_NEXT=true`专用helper处理，末页以`HAS_NEXT=false`收尾，因而不再在该热循环中计算`p+1<p_end`或携带两条运行时路径。QK/PV、K+V-over-PV register lookahead、z8 ownership、split40、partial ABI、reducer、shared布局与所有变长/最后20-page split保持#112399语义。
- **资源与正确性门禁**：`-resource-usage`中实际case12 `<true,false,true>` producer为`82 MTreg / 56 STreg / 8448 B shared / 0 B stack / 5 waves`；control `<true,false,false>`为`82/50/8448/0/5`。因此MTreg、shared、stack和驻留档均未退化，STreg增加6但未跨档。CPU manifest与logic回归通过；同一C500 binary的full、boundary、random各14/14均100% match、finite。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,32767→32768`全部通过，覆盖padding-page trap、40-split边界、tail、`full→short→full`与`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：fresh #112399 control、warmup=5、20 iterations、9 rounds的case12 candidate/control p10/p50/p90为full=`0.9941/0.9953/0.9967`，random=`0.9982/0.9999/1.0038`，boundary=`1.0021/1.0118/1.0221`。独立满长21 rounds×100 iterations强测仍为`0.9943/0.9951/0.9962`，确认约0.49%局部正向；random近中性，boundary约慢1.18%。后两者保留为本地风险证据而不外推为OJ结论。按照“OJ是性能真值、本地性能仅作辅助”的持续授权，在确认无在途任务并完成dry-run后于2026-08-14创建唯一一次probe **#112465**。唯一预注册问题是：该固定满容量数据流能否在真实OJ使case12（当前373 μs/60分）产生可归因改善或跨至下一显示档；不得基于结果扫描页数、guard或同源重投。
- **OJ终态与关闭**：#112465正常经历`Pending→Running→Finished`后14/14 Accepted / `65.64`，case1–14=`3/4/9/23/17/32/232/93/235/40/223/373/182/140 μs`，分数=`92/90/83/72/73/60/54/54/57/61/52/60/56/55`。唯一目标case12保持`373 μs/60分`，故OJ直接否定“消去固定满容量next-page predicate 能产生目标收益”的预注册假设。raw内嵌源码、`cuda_112465.cpp`逐提交快照与候选SHA均为`769be1717e559bcdaadf5f9b4e21401f6eaea3ca05dd11f19b8ae2e3ea856405`；恢复#112399，关闭这一 exact full-page source schedule，不以循环、guard或向case7/9/13原样迁移重试。

### exp472-case12-case13-register-packed-ml  (DUPLICATE / OJ ACCEPTED / CLOSED)

- **重复审计与 OJ 终态**：候选源码为`solutions/archive/2026-08-14-experiments/cuda_case12_case13_register_packed_ml_exp472.cpp`，SHA=`327513e706afe8c0ddecdbe0c20e893e79c65d380d0b70a0dd18aa5e5c128bd6`。与已关闭 exp470 的diff只含两段注释；运行语义仍是case12/13 vec2 reducer启用`REGISTER_PACKED_ML=true`、缩小动态shared metadata，绝非新的 changed precondition。已经创建的唯一提交#112495正常14/14 Accepted / `65.71`，case1–14=`3/4/10/23/17/28/231/93/234/40/222/374/182/141 μs`；case12由control的373到374 μs、case13保持182 μs。raw内嵌源码、`cuda_112495.cpp`逐提交快照和候选SHA一致。此结果仅作为重复 timing 样本归档，禁止继续提交或改名重开这一 exact reducer metadata-lifetime 路线；工作文件恢复#112399。

### exp473-case12-kv8-deferred-reference  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control 与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case12_kv8_deferred_reference_exp473.cpp`，SHA=`93c6d4d675635f5b594d9720e4e0ea14427ca92ad78e4f8b3ba59bd428d64d0b`。只给 case12 的 KV8 z8 producer 实例启用 bounded deferred exponent reference：`m` 只在首个有效页或`m_page > m + 8`时重设，否则保留旧 reference 并以较大的 FP32 `l/acc`表达同一 online-softmax 状态。K/V register lookahead、synchronous loader、QK、PV、split40/52页、z8 tree、packed FP16 `(m,l)` partial、reducer 和其他 shape 均不变。
- **数值/资源门禁**：每个 partial 至多52页、每页两个 token，guard 内 `l < 2 * 52 * 2^8 = 26624 < 65504`，因此保持既有 FP16 `l` ABI 的表示范围；reducer 仍以 partial reference `m` 做 log-sum-exp 合并。`-resource-usage` 的实际 case12 `<true,false,true>` producer 为`82 MTreg / 54 STreg / 8448 B shared / 0 stack / 5 waves`，control `<true,false,false>`为`82/50/8448/0/5`：无 spill、无 shared 或驻留档退化。normal/resource binary SHA=`a3dfe7a1bae34ed6ecf12c301848dc7bff7bc504ca10941bf3988cfa4a2d9faf` / `f2f8be2e887245b59ac8f328b1c602d1544b532b88ffc6c69b30b8bf20c0b4f0`。
- **correctness**：`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一 C500 binary 的full、boundary、random各14/14为100% match、finite，padding slots保持合法物理page ID。case12同进程精确序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全部通过，覆盖40-split的52/104-page边界、尾页以及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册问题**：以fresh #112399 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9997/1.0009/1.0019`、random=`0.9984/1.0027/1.0066`、boundary=`1.0017/1.0075/1.0218`。本地没有共同正向，full仅为噪声量级；但候选有独立的 KV8 state-contract 前提、完整正确性和未降驻留档，且本地/OJ性能环境并非同一真值。按 goal 的持续授权，在确认队列为空和 dry-run 后仅创建一次 OJ probe，唯一问题是该 bounded reference 是否能在 OJ case12 使当前`373 μs/60分`产生可归因改善；不得据此扫描阈值、扩 shape 或同源复投。
- **OJ终态与关闭**：#112535正常经历`Pending→Running→Finished`后14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/232/93/234/40/224/377/181/140 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/55`。唯一目标case12从control的`373→377 μs`，60分不变，OJ直接否定该 bounded deferred-reference 对目标路径的性能假设；case13 `182→181 μs`等未改运行路径的同场波动不能归因，aggregate并列65.93不构成结构性收益。raw内嵌源码、`cuda_112535.cpp`逐提交快照与候选SHA均为`93c6d4d675635f5b594d9720e4e0ea14427ca92ad78e4f8b3ba59bd428d64d0b`。拒绝并关闭该 exact KV8 reference/guard/state-flow：不得扫阈值、改guard、原样扩shape或同源密集复投；只有reference表示、partial契约、ownership或consumer数据流出现实质新前提才可重开。工作文件恢复#112399，队列为空。

### exp474-case12-alternate-register-page-p2-bsm  (RESOURCE GATE FAILED / CLOSED)

- **父/control 与唯一假设**：从 #112399（SHA=4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d）分叉；完整候选为 solutions/archive/2026-08-14-experiments/cuda_case12_alternate_register_bsm_exp474.cpp，SHA=47ec5fedcb8e8ddb2a63470356b26607e51c39518e6946245f4ce5e56256deb8。case12 交替消费 shared 的偶数页与每线程直接持有两 token K/V 的奇数页；当前 shared 页的 K/V half 退休后，token-BSM 将 p+2 写入 shared，尝试把其 I/O 覆盖到中间的 direct-register 页。它不同于 exp454/458/460 的相邻页 token-BSM，但仍以复制完整 direct page K/V 为代价。
- **静态资源门禁**：重新以 -resource-usage 编译归档源码，实际 case12 <true,false,true> 为 90 MTreg / 56 STreg / 8448 B shared / 0 B stack / 5 static waves；#112399 的 <true,false,false> 为 82/50/8448/0/5。资源二进制 SHA=e27f62e748d82fc1b2a791a0c383750f36830d211f526336ee1885a84f009fe6。虽然没有 spill 且仍为 5 waves，候选越过预注册的 MTreg<=82、STreg<=50 上限。
- **结论与边界**：不运行 GPU correctness、A/B 或 OJ，也不得用 split、reducer 或 launch 参数补偿这个资源退化。关闭“完整 two-token register page + 交替 shared/direct consumer + p+2 BSM”这一 exact dataflow；只有能减少 direct-page K/V live state、实质改变 register consumer ownership，或出现新的缓存/加载能力时才能重开。工作文件已恢复并核验为 #112399 的 SHA。

### exp475-case12-streamed-register-page-p2-bsm  (RESOURCE GATE FAILED / CLOSED)

- **父/control 与 changed precondition**：从 #112399 分叉，并以 exp474 的 p+2 BSM/shared-even-page 布局为父；完整候选为 solutions/archive/2026-08-14-experiments/cuda_case12_streamed_register_bsm_exp475.cpp，SHA=183d8dbf58a1283c819a53a3049521766425ebb40e30311b38cb74504b8391ac。为满足 exp474 的重开条件，direct 页不再同时保存两 token 的 K/V：当前 shared 页 PV 后才发起 p+2 V BSM，direct K 在各 token QK 前按需读，direct V 在各 token PV 前按需读。
- **静态资源门禁**：实际 case12 <true,false,true> 为 88 MTreg / 60 STreg / 8448 B shared / 0 B stack / 5 static waves；control 为 82/50/8448/0/5，资源二进制 SHA=b8211345fb2a8baf62dd7276c30e425a44d4cc01db9d2ee5591f56f01ff72aa9。相对 exp474 的 90/56，MTreg 只降 2、STreg 反升 4，仍双双超过上限。
- **结论与边界**：这个已缩短 direct K/V live range 的 changed precondition 仍未通过资源门禁，故不运行 GPU correctness、A/B 或 OJ。关闭当前 z8 线程布局下所有“shared 偶数页 + direct 奇数页 + p+2 token-BSM”的完整 direct-page 变体；不得再靠 direct K/V 加载时点、scope、split、reducer 或 launch 拼写细扫。只有不复制完整 direct page 的 consumer ownership、不同线程布局，或已验证的新缓存/加载能力才能重开。工作文件已恢复并核验为 #112399。

### exp476-case12-shared-k-p2-bsm  (RESOURCE GATE FAILED / CLOSED)

- **父/control 与 changed precondition**：从 #112399 分叉，并以 exp475 的 p+2 token-BSM 作为基础；完整候选为 solutions/archive/2026-08-14-experiments/cuda_case12_shared_k_p2_bsm_exp476.cpp，SHA=0db179fdb8db70fa547aeaabf21f6157e07d0fce2b7bf52a2b97778df6822e75。当前页 QK 后把 K[p+2] BSM 写回 s_k；当前页 PV 后把 K[p+1] 同步写入已退休 s_v，p+1 QK 直接从该 shared K 读取，随后 V[p+2] BSM 覆盖 s_v，并让 p+1 V 逐 token 直读。它避免复制完整 direct K page，且改变了 K 的 producer/consumer ownership。
- **静态资源门禁**：实际 case12 <true,false,true> 为 84 MTreg / 58 STreg / 8448 B shared / 0 B stack / 5 static waves；control 为 82/50/8448/0/5，资源二进制 SHA=d408ebdac7c6e424f199515cea313ba998127014e0134f00b3fb4489e1ca7aef。尽管相较 exp475 的 88/60 有所下降，仍越过 MTreg 和 STreg 的上限。
- **结论与边界**：不运行 GPU correctness、A/B 或 OJ。exp474 完整 direct page、exp475 streamed direct K/V、exp476 shared-K/streamed-V 三种 p+2 单请求交替页数据流均在当前 z8 布局被资源门禁否决；不得继续调 direct load 时点、token wait/release、shared pointer swap、split、reducer 或 launch。只有不依赖完整 single-request p+2 staged page 的多请求并发、不同线程布局，或已验证的新缓存/加载能力才能重开。工作文件已恢复并核验为 #112399。

### exp477-case5-cooperative-grid-sync-resource  (STATIC PASS / NO LAUNCH)

- **父/control 与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整 probe 源码为`solutions/archive/2026-08-14-experiments/cuda_case5_coop_grid_sync_exp477.cpp`，SHA=`fe4517e4bf5751bb0e22b6cd25483c12d330f3dafdd2d28e5b583a142f3618d8`。只为 B16/KV4/L141 case5 的既有 async combined z4 producer 实例增加末尾一次`cooperative_groups::this_grid().sync()`；空 split CTA 不 return，而是仅加入同一 barrier 后退出。默认实例、dispatch、split5、partial ABI、group8 reducer、loader、QK/PV 与其余 shape 不变。一个 `used` host stub 和 ABI 外 resource query 只强制实例化该 specialisation，绝不由`run_kernel`调用。
- **静态/runtime资源门禁**：`-resource-usage` 的 `<false,false,false,false,false,false,false,false,false,true,false,false,false,true,true,true,false,true,false,true>` 实例为`74 MTreg / 58 STreg / 8320 B shared / 0 B stack / staticMaxWarps=6`；control case5为`74/52/8320/0/6`。C500 runtime query 返回`74 regs / 8320 B / 6 active blocks/SM`，104 SM 合计`624`个resident CTA，大于精确 cooperative grid `64 × 5 = 320`。resource binary SHA=`a801ad687b92517c869cb4b447559eac750ca8c88b4360452e1d555361275de6`。既有`__launch_bounds__(...,6)` warning来自控制源码中的死模板，非本probe失败。
- **结论与下一门禁**：P5-1通过；本probe绝不运行 correctness、A/B 或 OJ，因为它没有 in-grid reducer。它只授权一个新的单变量候选：同一320 CTA grid 在 barrier 后由`blockIdx.y==0`的64个 CTA，以已验证 case5 group8 的 FP32 `(m,l,acc)` LSE 公式输出8个head；其余 CTA 退出。完整候选必须重新检查资源和624-CTA resident capacity，再覆盖full/random/boundary、padding、精确长度和workspace复用，最后才可做串行A/B。

### exp478-case5-cooperative-persistent  (CORRECT / REJECTED LOCALLY / CLOSED)

- **父/control、唯一差异与资源**：从#112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case5_coop_persistent_exp478.cpp`，source SHA=`859715b8018cf9040d28e135892ba4a25c4324453e2c43d3dfcfbeb023abfdd6`，normal/resource binary SHA=`bc5401a13743f04621695f0edd94e72f9c1f3a91f27063d7ab2902c5f3dabad5` / `e24a89e18d8d9a3e14d69622a17f76461c4a05e6beae1d55d2ef60f1fe083ebe`。只给case5启动同一`64×5=320` cooperative producer grid：空split仍参加`grid.sync()`；phase后y=0的64 CTA用z0/z1的八个16-lane row执行既有 group8 的FP32 `(m,l,acc)` log-sum-exp reducer，其余CTA退出。partial ABI、split5、BSM loader、QK/PV、z4 state tree、workspace和其他shape不变；cooperative launch失败才回退到control producer+外部reducer。资源为`76 MTreg / 58 STreg / 8320 B shared / 0 stack / staticMaxWarps=6`，runtime为`76 regs / 8320 B / 6 active blocks/SM = 624` resident，仍完整覆盖320 CTA。
- **correctness**：CPU manifest/logic均14/14通过；同一C500 binary 的full、boundary、random各14/14均100% match且finite，所有输入的padding `block_table` slot均保持合法物理ID。case5又在同一进程通过`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140→141`，覆盖5个two-page split边界、tail、padding trap及`full→short→full`/`short→full` workspace复用。
- **交错A/B 与结论**：以fresh #112399 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`0.9808/0.9968/1.0180`、random=`1.0667/1.0965/1.1106`、boundary=`1.0986/1.1251/1.1606`。满长约0.32%弱信号远低于噪声，random/boundary稳定慢9.65%/12.51%；固定320 CTA、全局barrier和短请求phase成本没有被删除一个external reducer launch抵消。拒绝、不提交OJ，并关闭这个 exact B16/L141 single-request cooperative producer→phase→in-grid group8 reducer；不得只换selected CTA、barrier/wave或launch拼写重试。只有多请求并驻留、实质减少固定CTA成本或改变producer/consumer contract才能重开；工作文件恢复#112399。

### exp479-case12-async-register-global-load  (C500 MEMORY VIOLATION / CLOSED)

- **父/control 与唯一假设**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case12_async_register_ldg_exp479.cpp`，SHA=`1ec0d0d7a54cb05463d6a128bbdfe0befbf0c8e237e0989a9c4c8acfb58deab0`。它只给 case12 的 KV8 z8 producer（`<true,false,true>`）把下一页 K/V 的两个对齐 128-bit scalar-register lookahead 改为 C500 官方 multistage 代码使用的`__builtin_mxc_load_global_async128`；请求仍在当前页 QK 后发出、数据仍跨当前页 softmax/PV 活到写回同一`s_k/s_v`、page/split/ownership/partial/reducer 均不变。预注册问题是该真实 register-returning async global load 能否在不增加 live state 的前提下覆盖一部分 next-page I/O；这不是已关闭的 p+2 BSM 或 direct-page 数据流。
- **静态资源与 codegen 门禁**：candidate case12 producer 是`82 MTreg / 50 STreg / 8448 B shared / 0 B stack / 5 waves`，与 fresh #112399 resource binary 的`82/50/8448/0/5`一致。candidate resource `.so` 含`llvm.mxc.load.global.async.v4i32`，fresh control 同一检索为零，证明 intrinsic 未被降回普通 load；资源二进制为`build/cuda_case12_async_register_ldg_exp479_resource.so`。CPU `c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过。
- **C500 correctness 与关闭**：同一 normal candidate binary 的full-length harness 中 case1–11 均100% match且finite，但首次进入 case12 时，C500 precise trap 报告`Memory Violation(0x4)`，kernel 为`paged_decode_case13_kv8_headpair_z8_kernel<true,false,true>`；进程随后以`mcErrorIllegalAddress`失败。因此没有 boundary/random、精确长度、A/B 或 OJ 提交，不能把该 intrinsic 描述为本题 KV8 lookahead 的可用新加载能力。关闭“case12 z8 下一页 K/V register lookahead 直接使用`__builtin_mxc_load_global_async128`”这一 exact builtin/consumer-lifetime/layout；不得仅改 cast、load 拼写、issue位置或把它扩到case7/9/13。只有官方语义/所需同步或生命周期得到独立 C500 probe 证实，或后端能力发生实质变化时才可重开。工作文件已恢复并核验为 #112399。

### exp480-case12-native-ldg-b128  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control 与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case12_native_ldg_b128_exp480.cpp`，候选与提交时工作文件 SHA 均为`b0b9ba12dac639ca927dc5bb384277a548fff8fae4717cc3db084348dd6ca3d8`。只给 case12 的 KV8 z8 producer `<true,false,true>` 启用同步、register-returning 的`__builtin_mxc_ldg_b128`：初始页/尾页 K/V staging 和 K+V-over-PV 的下一页 lookahead 均以同一个对齐 128-bit native load 读取；split40、partial/reducer、online softmax、z8 ownership、barrier和所有其他 shape 不变。它不同于 exp479：没有 async token/lifetime，且没有改变 buffer producer/consumer 契约。
- **资源、正确性与后端证据**：case12 producer 保持`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，与 control 相同。CPU manifest/logic 均14/14通过；同一 C500 binary 的full、boundary、random各14/14、finite。case12同进程精确序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`通过，覆盖padding-page trap、split/tail边界与`full→short→full`/`short→full`复用。以`mxcc -emit-llvm -S`复编译后，候选的实际case12 specialization `paged_decode_case13_kv8_headpair_z8_kernel<true,false,true>` 含6处`llvm.mxc.ldg.predicator.v4i32`；同条件重新编译的 #112399 control 为零处。这证明 builtin 在前端 IR 中保留为原生 LDG，而非普通`uint4` load 的同义表达；最终 ISA 与性能仍以 C500/OJ 为准。
- **交错 A/B、OJ终态与关闭**：相对 fresh #112399 control，candidate/control p10/p50/p90 为full=`0.9989/1.0002/1.0013`、random=`0.9973/1.0004/1.0028`、boundary=`0.9922/1.0026/1.0053`；本地没有共同正向。由于本地与 OJ 计时环境并非同一性能真值，且候选具备真实后端差异、完整正确性和不降资源档，按已授权流程于2026-08-14提交唯一一次 probe **#112630**。它正常经历`Pending→Running→Finished`，最终14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/231/94/235/40/222/376/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/54`。唯一目标case12从control的`373→376 μs`、仍60分，OJ直接否定这条 native-LDG page-loader/lookahead 的性能假设；case7/8/11/13等未改路径的同场波动不能归因，aggregate也未提高。raw内嵌源码、`solutions/archive/2026-08-14-submissions/cuda_112630.cpp`和提交候选SHA均为`b0b9ba12dac639ca927dc5bb384277a548fff8fae4717cc3db084348dd6ca3d8`。拒绝并关闭 case12 的这一 exact builtin参数、初始/尾页 staging 与next-page lookahead覆盖范围；不得只改参数、cast、调用位置或覆盖范围后重投。工作文件恢复并核验为#112399。

### exp481-case8-case11-vec4-partial-native-ldg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control 与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case8_case11_reducer_native_ldg_exp481.cpp`，候选 SHA=`3505c7501ed05d397cc596c41fca83199bd6464297b0398f94292e8fa1ad7fc6`。仅让 case8/11 的多 split `paged_decode_reduce_vec4_kernel` 将已有的 16-byte 对齐 FP32 `partial_acc` `float4` 消费改为同步、register-returning 的`__builtin_mxc_ldg_b128`；producer、partial ABI、LSE 数学、共享 metadata、single-split fallback、case8/11以外 dispatch 和所有 K/V page loader 均不变。`head_idx * 128 + lane * 4` 始终是16-byte对齐，且 producer本已用`float4`写该消费地址。这是 producer→reducer 的独立 read-only workspace consumer，不是已由 exp480 关闭的 case12 K/V page-loader/lookahead 路线。
- **资源与 LLVM 门禁**：fresh #112399 resource build的既有 vec4 实例`<true,false,true>`为`64 MTreg / 35 STreg / 0 B shared / 0 stack / 8 waves`；candidate新实例`<true,false,true,true>`仍为`64/35/0/0/8`。`mxcc -emit-llvm -S`的candidate实际 vec4 specialization含8个循环展开后的`llvm.mxc.ldg.predicator.v4i32`调用，fresh control为0；全文件candidate仅此实例有该 intrinsic。故此builtin确实保留为原生LDG，且没有资源或驻留档退化。
- **数值/边界门禁**：CPU manifest和kernel-logic均14/14通过；同一C500 normal binary的full、boundary、random（seed=20260809）均14/14、finite、100% tolerance match，短长度输入均保留合法物理padding page ID。case8同进程序列`4096→1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095→4096`全通过；case11同进程序列`12251→1,2,15,16,17,319,320,321,639,640,641,959,960,961,12239,12240,12241,12250→12251`全通过，覆盖 page、split、tail、padding trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：以fresh #112399 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为case8 full=`0.9983/1.0017/1.0069`、random=`0.9983/0.9999/1.0046`、boundary=`0.9843/1.0076/1.0755`；case11 full=`0.9992/0.9994/1.0003`、random=`0.9966/0.9980/1.0017`、boundary=`0.9902/0.9969/1.0013`。本地没有稳定共同正向，case8 boundary还有轻微噪声性回退；如实作为风险证据，而非性能否定。按“OJ是性能与跨档真值、本地性能为辅助”的持续授权，此候选可创建且只创建一次OJ probe。预注册唯一问题：该native partial-acc consumer能否在真实OJ使case8从`93→92 μs`和/或case11从`223→221 μs`跨显示档；不得据此变更builtin参数、范围或同源复投。
- **OJ终态与关闭**：#112657正常经历`Pending→Running→Finished`后14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/232/93/235/40/223/372/181/140 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/57/55`。两个预注册目标均保持case8=`93 μs/54分`、case11=`223 μs/52分`，OJ直接否定这个reducer-side native-LDG consumer；case7 `233→232 μs`等未改路径波动不归因。raw内嵌源码、`solutions/archive/2026-08-15-submissions/cuda_112657.cpp`逐提交快照与候选SHA均为`3505c7501ed05d397cc596c41fca83199bd6464297b0398f94292e8fa1ad7fc6`。拒绝并关闭这个 exact case8/11 vec4 `partial_acc` native-LDG 路线；不得改builtin参数、cast、调用位置或enable scope后重投，工作文件恢复#112399。

### exp482-case7-group8-partial-native-ldg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control 与唯一差异**：从#112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case7_group8_partial_native_ldg_exp482.cpp`，SHA=`138a34b5a6feda95bb278cfe9b8778d502d833dbf9086cae34cad141e85a01a1`。只让case7多split `paged_decode_reduce_group8_kernel` 的每个split读取两段16-byte对齐FP32 `partial_acc float4`时，使用同步、register-returning 的`__builtin_mxc_ldg_b128`；producer、K/V page loader、partial ABI、LSE 数学、live-split、group8 block geometry和single-split fallback均不变。它与exp481不同：consumer 是case7的group8 reducer而非case8/11 vec4 reducer，且每split有两个独立float4消费地址。
- **资源与LLVM门禁**：fresh #112399及候选的实际case7 group8 reducer均为`66 MTreg / 25 STreg / 0 B shared / 0 stack / 7 waves`。candidate LLVM IR有10处实际`llvm.mxc.ldg.predicator.v4i32`调用（检索总数11含声明），control为零；因此这不是普通vector load的同义源码改写，也没有资源或驻留档退化。
- **数值/边界门禁**：CPU manifest和kernel-logic均14/14通过；同一C500 candidate binary的full、boundary、random（seed=20260809）均14/14、finite、100% tolerance match，padding slot保持合法物理page ID。case7同进程序列`2048→1,2,15,16,17,687,688,689,1375,1376,1377,2047→2048`全通过，覆盖3-split边界、tail、padding trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：以fresh #112399 control、warmup=5、20 iterations、9 rounds，case7 candidate/control p10/p50/p90为full=`0.9991/1.0035/1.0043`、random=`0.9964/0.9994/1.0042`、boundary=`0.9982/1.0020/1.0065`。本地没有共同正向，作为风险证据而非性能否定。它具备独立的group8 workspace-consumer前提、真实LDG codegen、完整资源和数值门禁；在确认无在途任务、记录SHA并完成dry-run后，于2026-08-14只创建一次OJ probe **#112680**。预注册唯一问题：它能否使当前#112399的case7 `233 μs/54分`产生可归因改善或跨显示档；不得据此扫描builtin参数、范围或同源重投。
- **OJ终态与关闭**：#112680正常经历`Pending→Running→Finished`后14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/232/94/231/40/222/372/181/140 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/57/55`。唯一目标case7从结构control的`233→232 μs`，但显示分仍54；更关键的是，不含该改变的#112657已给出同样`232 μs/54分`，故本次一微秒没有源码因果，不能作为control收益。raw内嵌源码、`solutions/archive/2026-08-15-submissions/cuda_112680.cpp`逐提交快照与候选SHA均为`138a34b5a6feda95bb278cfe9b8778d502d833dbf9086cae34cad141e85a01a1`。拒绝并关闭这个 exact case7 group8 `partial_acc` native-LDG consumer；不得改builtin参数、cast、调用位置或enable scope后重投，工作文件恢复#112399。

### exp483-case7-producer-partial-native-stg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与隔离**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选已在提交前保存为`solutions/archive/2026-08-14-experiments/cuda_case7_partial_native_stg_exp483.cpp`，与当前工作文件 SHA 均为`bc9a2b668107dd38e2f1a8e61df7cabac496f1a99202506d43a2ae412061a161`。只给 case7 的 KV8 z8 producer `paged_decode_case13_kv8_headpair_z8_kernel<true,false,true>` 写出每个 head 的两段16-byte对齐 `partial_acc float4` 时启用同步的`__builtin_mxc_stg_b128_predicator`；group8 reducer、partial ABI、K/V page loader、online softmax、live-split、CTA geometry和其他 case 均保持control。它改变的是 producer→紧邻 reducer 的 native-store handoff，和已关闭的 case7 native-LDG consumer（exp482）是不同方向。
- **资源与后端门禁**：fresh `-resource-usage` 中 control case7 `<true,false,false>` 和候选 `<true,false,true>` 均为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`。以`mxcc -emit-llvm -S`分别重编译后，候选实际case7 specialization含4处`llvm.mxc.stg.predicator.v4i32`调用，fresh #112399 control为0；因此 builtin 未被降低为普通 `float4` store 的同义表达，且没有资源或驻留档退化。
- **数值与边界门禁**：CPU manifest和kernel-logic均14/14通过；同一 C500 candidate binary 的full、boundary、random（seed=20260809）各14/14、100% tolerance match且finite。case7同进程序列`2048→1,2,15,16,17,687,688,689,1375,1376,1377,2047→2048`全部通过，覆盖3-split/page/tail边界、padding-page trap以及`full→short→full`和`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112399 control、warmup=5、20 iterations、9 rounds，case7 candidate/control p10/p50/p90为full=`0.9955/0.9990/1.0010`、random=`0.9922/1.0013/1.0070`、boundary=`0.9914/0.9976/1.0067`。本地没有共同、可归因的性能正向，但不存在系统性回退；按“本地性能为辅助、OJ是性能真值”的授权，这不否决一次单笔 probe。预注册唯一问题：该真实 native producer-store handoff 能否使 OJ case7 相对结构control的`233 μs/54分`产生可归因改善或跨显示档；不得据此扫描 builtin 参数、enable scope 或同源码复投。
- **OJ终态与关闭**：#112704 正常经历`Pending→Running→Finished`后14/14 Accepted / `65.93`，case1–14=`3/4/9/22/17/28/232/94/234/40/223/373/181/141 μs`，分数=`92/90/83/73/73/63/54/54/57/61/52/60/57/54`。唯一目标case7从control的`233→232 μs`却仍54分，而不含本改动的#112657同样为`232 μs/54分`，所以这1 μs没有源码因果；case4的`23→22 μs/72→73分`及其他未改路径波动也不能归因。raw内嵌源码、`solutions/archive/2026-08-15-submissions/cuda_112704.cpp`逐提交快照、实验源码和提交时工作文件SHA均为`bc9a2b668107dd38e2f1a8e61df7cabac496f1a99202506d43a2ae412061a161`。拒绝并关闭这个 exact case7 z8 `partial_acc` native-STG producer→group8 reducer handoff；不得只改builtin参数、cast、store位置或enable scope后重投，只有不同partial consumer、producer/consumer ownership或后端能力出现实质新前提才可重新提出。

### exp484-case7-fixed-live-bucket-literal-div  (STATIC GATE FAILED / CLOSED)

- **父/control与唯一差异**：从 #112399（SHA=`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`）分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case7_fixed_live_bucket_exp484.cpp`，SHA=`32c5c9a76b975511722047404b585dbf9a8a0e92455be991cbe83b87681c3323`。case7 仍固定`n_split=3`、`43/43/42`满容量映射、grid/CTA/z8 ownership、同步 loader、partial ABI 与group8 reducer；仅在现有active split前缀内，按`full_pages`的1/2/3 live bucket均衡实际有效页，避免exp448的每行动态`valid_pages/n_split`。
- **静态关闭**：three-live bucket 的 literal `/3` 在实际device LLVM IR 中仍留下`udiv`，未满足“消除动态除法且不降资源档”的前置门禁。因此未运行C500 correctness、A/B或OJ；不以同一literal除法的拼写、guard或启用范围重试。只有以明确无除法的等价常数运算并重新通过资源门禁，才是新的 changed precondition。

### exp485-case7-fixed-live-bucket-mulhi  (CORRECT / OJ ACCEPTED / CURRENT CONTROL)

- **父/control、唯一差异与预注册问题**：从 #112399 分叉；完整候选为`solutions/archive/2026-08-14-experiments/cuda_case7_fixed_live_bucket_mulhi_exp485.cpp`，提交前工作文件与快照SHA均为`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`。case7 保持固定`n_split=3`、grid/CTA、z8 ownership、同步loader、partial ABI和group8 reducer；容量满长严格仍为`43/43/42`页。唯一运行差异是按真实`full_pages`重新均衡既有active前缀：`0..43`页只live split0，`44..86`页由两个split约均分，`87..128`页由三个split约均分，tail仍由最后一个live split处理。`/3`以`__umulhi(n, 0xAAAAAAAB) >> 1`实现，避免exp484的IR `udiv`。预注册OJ问题：在不增CTA、不改变live-prefix/reducer契约或满容量映射的前提下，随机实际长度的producer失衡减少能否让control的case7 `233 μs/54分`产生可归因改善或跨显示档；不据此扫描bucket阈值、split或同源码复投。
- **资源与codegen门禁**：case7 producer `<true,false,true>` 为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，与#112399 `<true,false,false>`相同。候选IR的三分之一运算为`mul i64 ..., 2863311531`加`lshr 33`，没有新增`udiv`；仅剩control已有的full-page `/16`。因此不是exp484的同一后端前提。
- **correctness与边界**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一C500 binary的full、boundary、random均14/14、finite、100% tolerance match。case7同进程精确序列`2048→1,15,16,17,672,688,689,704,705,1360,1376,1377,1392,1393,2047→2048`通过，覆盖新live bucket边界、page/tail、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错A/B与OJ终态/control决策**：相对fresh #112399 control（9 rounds × 20 iterations），candidate/control p10/p50/p90为full=`0.9961/0.9992/1.0000`、random=`0.9774/0.9797/0.9872`、boundary=`0.9965/0.9992/0.9995`；random强复测（21 rounds × 100）=`0.9825/0.9869/0.9895`。满长/边界中性且随机长度稳定快约1.3–2.1%，满足一次OJ finalist条件。确认队列无非终态、完成同一SHA dry-run后，于2026-08-14只创建提交 **#112716**。它正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`66.00`**，case1–14=`3/4/9/22/17/28/227/93/237/40/223/375/181/141 μs`，分数=`92/90/83/73/73/63/55/54/57/61/52/60/57/54`。唯一运行差异只覆盖case7，且该目标从#112399的`233 μs/54分`到`227 μs/55分`，与随机长度A/B的方向和机制一致，故是可归因的跨display收益；case4/13的加分与case14的失分、case9/12的时延波动均不覆盖本改变，不能归因。raw内嵌源码、`solutions/archive/2026-08-15-submissions/cuda_112716.cpp`、实验快照和工作文件SHA均为`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`。资源、完整数值门禁和OJ目标因果共同支持把这条 exact case7 fixed-live bucket/mulhi mapping 接受为新的结构性control；不得改bucket边界、magic除法、tail owner或同源重投。它建立了“既有live前缀 + 无device除法均衡”的新前提；后续若迁移到case9等其他shape，必须以独立资源、full/random/boundary和精确边界门禁证明，不可直接外推。

### exp486-case9-fixed-live-bucket-mulhi  (CORRECT / OJ ACCEPTED / REJECTED AS CONTROL)

- **父/control、唯一差异与changed precondition**：从#112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case9_fixed_live_bucket_mulhi_exp486.cpp`，与工作文件SHA均为`0f4d34ea9b7f23894a555991d29146e569dfd034fdb07c7fb13723d31b5c501f`。只给case9（B32/KV8/Lcap4096）启用新的模板特化；case7已经接受的mapping、所有其他dispatch、grid、split6、CTA/z8 ownership、同步loader、K+V-over-PV、packed partial ABI与vec2 reducer不变。满容量严格仍为`43/43/43/43/43/41`页；按`full_pages`只重分配control已经live的1–6 split前缀，tail仍给最后live split。exp485 已经证明“固定live prefix、无device除法”是对exp448的实质新前提；本轮独立覆盖case9的六个bucket而非将case7数值外推。
- **算术、codegen与资源门禁**：0..256页逐值验证每个bucket等于`ceil(full_pages/live_splits)`，连续覆盖且live count仍等于control的`ceil(full_pages/43)`；无未写partial。`/3`、`/5`、`/6`分别以`__umulhi` magic乘法表示，`/2`、`/4`为shift。candidate LLVM 的实际`<true,true,false,true>` case9 producer只有control已有的`full_pages / 16`，无候选`udiv`；三个magic路径为64-bit multiply + `lshr 33/34`。`-resource-usage`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control case9 `<true,true,false,false>`同档。
- **correctness/边界门禁**：CPU manifest与logic均14/14；同一C500 binary full、boundary、random各14/14、finite、100% tolerance match。case9同进程序列`4096→1,15,16,17,672,688,689,704,705,1360,1376,1377,1392,1393,2048,2064,2065,2080,2081,2736,2752,2753,2768,2769,3424,3440,3441,3456,3457,4080,4095,4096`均通过，覆盖六个live-bucket转换、page/tail、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错A/B与预注册OJ问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`1.0004/1.0012/1.0045`、random=`0.9784/0.9833/0.9896`、boundary=`1.0030/1.0048/1.0089`；21 rounds × 100强复测为random=`0.9800/0.9831/0.9849`、boundary=`0.9982/1.0034/1.0071`。random稳定快约1.7%，full中性，boundary约0.3–0.5%轻微风险而远小于exp448的系统性退化。OJ是性能与跨档真值，且候选具备独立资源/codegen/数值证据；一次且仅一次预注册probe的问题是：case9的fixed-live bucket能否相对当前#112716代码路径取得可归因改善或display gain。不得据此扫描bucket阈值、magic、split或同源码重投。
- **OJ终态与control决策**：确认队列无非终态、同一SHA dry-run后只创建 **#112725**。它正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/225/93/230/40/221/372/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖的case9由#112716的`237→230 μs`，却仍为57分；未改case9的#112399已经有`230 μs/57分`，故本次回到历史快速 timing tier不能单独归因给mapping，更没有兑现预注册的display gain。其余case7/11/12/14的改善与case3/4的回退均不覆盖源码差异，仅作同场波动；aggregate亦低于control。raw内嵌源码、`solutions/archive/2026-08-15-submissions/cuda_112725.cpp`、实验快照和提交前工作文件SHA均为`0f4d34ea9b7f23894a555991d29146e569dfd034fdb07c7fb13723d31b5c501f`。拒绝这条 exact case9 bucket/magic/tail-owner mapping，不调bucket、magic、split或同源码重投；工作文件已逐字节恢复#112716。

### exp487-case12-async-register-gvm-wait  (CORRECT / LOCAL REJECTED / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_async_register_gvm_wait_exp487.cpp`，SHA=`66a494520f7c0d74d6a4c39b907f5bee5ff59eb4a661a46726a41d4b4493eb82`。exp479曾把`__builtin_mxc_load_global_async128`的返回值直接用于case12下一页K/V lookahead而在C500触发非法地址。本轮先以独立`c500_async_register_gld_probe`验证官方 MCTLASS `__builtin_mxc_arrive(64)` + `__builtin_mxc_barrier()` 的使用契约：64-thread与256-thread、各257次迭代均逐payload正确；probe LLVM含真实`llvm.mxc.load.global.async.v4i32`、arrive与barrier。生产候选只在case12的`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`中，将下一页K/V各一次16B load改为async-register payload，跨当前页softmax/PV存活，等待后才写回既有`s_k/s_v`；split40、z8 ownership、同步页buffer、partial ABI、reducer和其余case均不变。
- **后端/资源门禁**：目标LLVM特化含两处`llvm.mxc.load.global.async.v4i32`，其后有`llvm.mxc.arrive(64)`和`llvm.mxc.barrier()`再首次写入next-page shared row；LLVM的早期`extractelement`与已通过probe的降法相同，实际寄存器consumer仍在wait后。fresh `-resource-usage`为`82 MTreg / 52 STreg / 8448 B shared / 0 B stack / 5 waves`；相对control case12的`82/50/8448/0/5`仅增加两枚STreg，未跨驻留档。normal/resource binary SHA分别为`27095010c4584ca09474033d7ebd5ac530048e16c144bb22bc8f5fcb03b53965`/`21133bbbac4c8de90024f57594b70d3fbfb3c94fa9fa544badb3ed74cab84e92`。
- **正确性门禁**：manifest与CPU logic均14/14。相同候选binary的C500 full、boundary、random（seed=20260809）均14/14，全部finite且100% tolerance match。case12精确同进程序列`32768→1,2,15,16,17,831,832,833,847,848,849,863,864,865,1663,1664,1665,1679,1680,1681,1695,1696,1697,32767→32768`全部通过，覆盖page/split/tail、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与结论**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为case12 full=`0.9988/1.0042/1.0055`、random=`1.0035/1.0057/1.0075`、boundary=`1.0139/1.0164/1.0202`。三种长度分布均回退，尤其boundary全样本为负，属于可重复的系统性本地风险而非可由一次OJ probe甄别的弱信号；因此不提交OJ。关闭这个 exact “官方wait后双async-register K/V跨PV lookahead→shared回写”数据流；不得只调cast/extract、wait/barrier、issue位置或扩到case7/9/13。只有不同async consumer ownership、多个独立请求深度或其他实质数据流改变才能重开。工作文件已逐字节恢复#112716。

### exp488-case12-pow2-live-prefix (CORRECT / STATIC RESOURCE FAIL / REJECTED LOCALLY / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_pow2_live_prefix_exp488.cpp`，SHA=`89eb96524c4c71ce78df6f435788c2000344e78ef980505aeb1ad29deb9981fc`。只给case12的既有40个producer CTA在2/4/8/16/32个live split前缀内以shift均衡实际页；其他live count仍用control的52-page mapping，满容量仍40×52，tail仍由最后live split拥有。partial ABI、loader、ownership、数学、reducer和其他case不变。
- **资源/codegen门禁**：candidate case12 `<true,false,false,true>` 为`86 MTreg / 44 STreg / 8448 B shared / 0 stack / 5 waves`；相对control `82/50/8448/0/5` 增加4个MTreg，未满足预注册的`MTreg<=82`硬门槛。故即使静态波数未降，也不应作为可提交 finalist。
- **correctness与边界**：CPU manifest和`test_kernel_logic.py`均通过；同一candidate binary的full、boundary、random均14/14、100% tolerance match且finite。case12精确`1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767,32768`以及同进程`full→short→full`、`short→full`均通过，覆盖live-prefix转换、52-page边界、tail、padding trap与workspace复用。
- **交错A/B与结论**：相对`build/cuda_112716_control.so`，9 rounds×20 iterations（warmup=5）candidate/control p10/p50/p90为full=`1.0073/1.0078/1.0089`、random=`1.0083/1.0093/1.0114`、boundary=`1.0103/1.0148/1.0211`；三分布均系统性回退，故不提交OJ。关闭该exact case12 fixed-live pow2/mapping；不得调live集合、magic、bucket、tail owner或同源复投，只有不同producer/consumer ownership、实际多请求深度或其他实质新前提才可重开。工作文件恢复#112716。

### submission-112736-control-resample  (ACCEPTED / NOT exp488)

- **事实核对**：本轮曾预定以 exp488 SHA `89eb96524c4c71ce78df6f435788c2000344e78ef980505aeb1ad29deb9981fc` 做一次 OJ probe；终态后，raw 内嵌源码和 `cuda_112736.cpp` 的 SHA 均为 #112716 control 的 `411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`。因此 #112736 不是 exp488 的远端测量，不能把它的 case12 `374 μs/60分`归因给 pow2 live-prefix 映射。
- **OJ 终态**：#112736 正常经历 Pending→Running→Finished，14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/225/93/234/40/222/374/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。它只补充 #112716 同源 timing 样本；最高分和结构性 control 均不变。raw=`results/raw/cuda_112736_raw.json`，逐提交快照=`solutions/archive/2026-08-15-submissions/cuda_112736.cpp`。
- **流程修正**：今后预注册 SHA 只能在实际 `--submit` 前的最后一次 `sha256sum solutions/cuda_maca_optimized.cpp` 得到，并须逐字节等于该 candidate；dry-run 后至 POST 期间不允许任何任务写工作文件。终态归档仍以 raw 内嵌代码 SHA 为最终事实。exp488 已由资源门禁及三分布 A/B 关闭，不把 #112736 误记作它的 OJ 反例或正例。

### exp489-kv8-early-page-id  (CORRECT / REJECTED LOCALLY / NO OJ)

- **父/control 与实际影响范围**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_early_pid_exp489.cpp`，SHA=`9b4b85386f9d97f558c270f4be26df2442ffdd7eb693fdcdda5ab5c50f7d5b54`。在 z8 producer 的每页 page-ready `__syncwarp()` 后、当前页 QK 前，把已有 `pid = bt_row[p+1]` 前移；下一页 K/V scalar lookahead、PV、shared 回写、split、partial ABI、reducer 与尾页路径不变。虽然文件名最初写 case12，该 kernel 特化实际覆盖 KV8 case7/9/12/13，故四个 case 都是本轮性能范围，不能只把它称作 case12 候选。
- **changed-precondition 与资源**：当前控制已有 PID→K/V scalar lookahead 跨当前页 PV 的依赖链，本候选只尝试把 page-table PID load 置入 QK 窗口；它不同于已关闭的 token-BSM、async/LDG、fixed-page 与 live-bucket 路线。用 `-resource-usage` 分别重编译 candidate 和 control，三个 z8 producer 实例均不变：`<true,false,false>`=`82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves`，`<true,false,true>`=`82/50/8448/0/5`，`<true,true,false>`=`82/48/8448/0/5`；无 spill 或驻留降档。
- **correctness**：CPU manifest/logic 均14/14；同一 C500 candidate binary 的full、boundary、random（seed=20260809）均14/14 Accepted、finite、100% tolerance match。该移动不在 QK/PV 后继续读取旧 pid，也保留 `p + 1 < p_end` guard，未扩大 padding-page 可读范围。
- **交错 A/B 与结论**：以 fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90 分别为：case7 full=`1.0029/1.0045/1.0064`、random=`0.9997/1.0061/1.0156`、boundary=`1.0061/1.0083/1.0139`；case9=`1.0042/1.0066/1.0065`（三分布 p50）；case12=`1.0020/1.0021/1.0054`；case13=`1.0074/1.0159/0.9992`，最后一个 boundary 信号宽且中性。四个受影响路径在 full/random 均无共同正向，case7/9/12在 boundary 也稳定回退，case13 random 慢约1.6%。这属于重复、跨形状的系统性风险，故不提交 OJ。关闭当前 z8 ownership 下这一 exact early-PID page-ready-before-QK placement；不得仅扫描 PID 时点、预取距离或扩缩同一范围。只有 page-table consumer、loader ownership 或多请求深度发生实质改变才可重开。工作文件已恢复并核验为 #112716。

### exp491-case12-row16-next-pid-broadcast  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从#112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_row16_next_pid_broadcast_exp491.cpp`，提交前工作文件、raw内嵌源码与`solutions/archive/2026-08-15-submissions/cuda_112741.cpp`的SHA均为`995235e5ef305858c217d98636b8c89a28bb276889665ff3a375eda1dda67cc8`。只给case12的`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`热`p+1`路径增加 row-owner PID consumer：每个物理16-lane row只让`tx==0`读取`bt_row[p+1]`，随后每lane执行原生`mov_shfl.i32` mode `0x150`取得本row PID；初始与tail PID加载、K/V lookahead、split40、z8 ownership、partial ABI、reducer、数学和其他case保持control。它与exp489仅移动每lane PID时点不同，实质改变了page-table load ownership/数量（每次transition约256→16次）。
- **资源、codegen与正确性门禁**：实际case12 specialization确认有guarded row-leader global PID load和原生32-bit shuffle、没有float PID转换或BSM bpermute；资源为`82 MTreg / 54 STreg / 8448 B shared / 0 stack / 5 waves`，相对control的`82/50/8448/0/5`未降驻留。`c500_case_manifest.py`和`test_kernel_logic.py`通过；同一binary C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case12同进程精确序列`32768→1,2,15,16,17,831,832,833,847,848,849,863,864,865,1663,1664,1665,1679,1680,1681,1695,1696,1697,32767,32768`通过，覆盖split/tail、padding trap以及`full→short→full`与`short→full`复用。
- **交错 A/B、OJ问题与终态**：相对fresh #112716，9×20轮次candidate/control p10/p50/p90为full=`1.0007/1.0020/1.0032`、random=`0.9967/1.0001/1.0037`、boundary=`0.9942/1.0041/1.0081`；21×100强复测为full=`1.0006/1.0018/1.0032`、random=`0.9974/0.9990/1.0009`、boundary=`0.9987/1.0025/1.0065`。没有共同系统性回退，且该owner/dataflow问题只能由OJ最终检验，故按预注册只提交一次#112741：它能否使case12从#112716的`375 μs/60分`跨到下一显示档。OJ正常终态为14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/227/94/234/40/223/372/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。目标虽到372 μs却仍60分、aggregate低于control，不能接受为结构性收益。关闭这个 exact case12 hot-next row-owner `int32` native-broadcast mapping；不得只改source lane、shuffle mode、load时点或覆盖范围后重投。工作文件已逐字节恢复#112716。

### exp492-case5-skip-empty-rescale  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case5_skip_empty_rescale_exp492.cpp`，提交前工作文件SHA为`32f13cf2e5ccc50fcadabf318625602e3dfd236ac23b33ad9b0aef6153f588a6`。只把case5（B16/KV4/L141）`paged_decode_case11_headpair_z4_kernel` dispatch的第17个模板参数`SKIP_EMPTY_RESCALE`从`false`改为`true`；split5、combined tail、BF16 MMA-QK、z4 ownership、loader、partial ABI、group8 reducer、workspace和其他case均保持control。每个live split初始`m=-Inf,l=0,acc=0`，其首个有效页的空状态rescale严格为无效；后续页均已`l>0`。旧exp330/331只覆盖case4 dedicated/direct-out BSM ownership，不能否定这个case5 head-pair/z4 BF16-MMA producer前提。
- **资源、正确性与边界门禁**：实际case5 candidate和control均为`74 MTreg / 52 STreg / 8320 B shared / 0 stack / 6 waves`。`c500_case_manifest.py`与`test_kernel_logic.py`均通过；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case5同进程序列`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140,141`均通过，覆盖5个split的页/尾边界、padding trap和`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716、warmup=5，9×20的candidate/control p10/p50/p90为full=`0.9774/1.0312/1.0417`、random=`0.9332/0.9914/1.0169`、boundary=`0.9853/0.9972/1.0413`。满长首轮的3.1%中位回退未在21×100强复测重现：full=`0.9733/0.9942/1.0123`、random=`0.9560/0.9938/1.0487`、boundary=`0.9613/1.0031/1.0314`；未见可重复的三分布系统性风险。本地效果接近噪声但候选具备完整安全门禁和单一数学机制，因此按OJ优先规则预注册一次且仅一次probe：该case5 empty-state rescale消除能否使#112716的`17 μs/73分`跨到`16 μs/74分`。不得据此扫阈值、分支拼写、启用范围或同源码复投。
- **OJ终态与control决策**：#112744 14/14 Accepted / **`66.00`**，case1–14=`3/4/9/22/17/28/226/93/234/40/223/376/182/140 μs`，分数=`92/90/83/73/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case5保持`17 μs/73分`，未跨预注册的`16 μs/74分`档；case7 `227→226 μs`、case12 `375→376 μs`等未改路径同场波动不构成源码收益。raw内嵌源码、逐提交快照、实验快照与提交前工作文件SHA均为`32f13cf2e5ccc50fcadabf318625602e3dfd236ac23b33ad9b0aef6153f588a6`。因此即使aggregate与#112716同为66.00，也不建立结构性收益或替换control；关闭这条 exact case5 B16/KV4/L141 empty-state-rescale skip，不改分支拼写、模板参数位置、启用范围或同源码重投。工作文件已逐字节恢复#112716，队列为空。

### exp494-case12-register-owned-next-k  (CORRECT / REJECTED LOCALLY / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_register_owned_k_exp494.cpp`，SHA=`241ed11c552060acc4369d0edd32d0a94c8e3b8e581ac94ed8fd4cf9ec043f08`。仅在case12的`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`中，让每线程把既有的下一页K payload跨页循环带回，并直接供自己的QK token使用；peer token仍按control从`s_k`读取。K global-load计数、split40、尾页、V path、partial ABI、reducer、数学与其他dispatch不变。这不同于已关闭的dead-half BSM或direct-page路线，但当前K consumer ownership只减少一个共享读取。
- **资源与correctness**：实际case12 producer为`80 MTreg / 52 STreg / 8448 B shared / 0 stack / 6 waves`，control为`82/50/8448/0/5`；runtime resource query确认`6 active blocks/SM`。`c500_case_manifest.py`与`test_kernel_logic.py`均通过；同一candidate的C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,32767→32768`通过，覆盖split/tail、padding trap和`full→short→full`/`short→full`复用。
- **交错 A/B、决策与重开边界**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`1.0417/1.0423/1.0429`、random=`1.0374/1.0406/1.0436`、boundary=`0.9658/0.9723/0.9767`。虽然boundary约快2.8%，full/random稳定约慢4%，不具备OJ finalist资格，故不提交。关闭当前z8 ownership下这一 exact direct-register-owned-next-K consumer；只改branch拼写、helper返回形式或轻微source重排不是changed precondition，只有实质改变K consumer ownership或跨页数据流才可重开。工作文件保持并核验为#112716，队列为空。

### exp495-case12-early-sync-k-store  (CORRECT / REJECTED LOCALLY / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_early_sync_k_store_exp495.cpp`，SHA=`cd6cdffe991d06c4dfa96cc52c4716046fda904f43424cb0f6b9e915f8a5ddef`。只给case12的`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`启用`EARLY_SYNC_NEXT_K_STORE`：当前页QK读取完成后，所有physical-wave lanes先`__syncwarp()` release，再由同一同步global-load owner把next-K写回已死亡的`s_k` row；next-V仍走原有scalar register lookahead并在PV后发布。K/V global-load计数、split40、tail、partial ABI、reducer、数学与其他dispatch不变。它不同于exp458/459的token-BSM producer：没有异步token/wait，尝试的是同步K寄存器lifetime与shared publish时点。
- **资源与correctness**：实际case12 producer为`78 MTreg / 50 STreg / 8448 B shared / 0 stack / 6 waves`，相对control `82/50/8448/0/5`跨入更高驻留；构建无新诊断。`c500_case_manifest.py`和`test_kernel_logic.py`均通过；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,32767→32768`通过，覆盖split/tail、padding trap和`full→short→full`/`short→full`复用。
- **交错 A/B、决策与重开边界**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`1.0188/1.0207/1.0234`、random=`1.0058/1.0095/1.0114`、boundary=`0.9239/0.9297/0.9373`。资源升级只在短边界显著受益，full/random均稳定回退，不能以边界收益外推或作为OJ finalist，故不提交。关闭当前z8 ownership下这一 exact synchronous early-K-store/lifetime mapping；只改wave release/barrier、store位置或load拼写不是changed precondition，只有K/V consumer ownership、实际等待覆盖或跨页数据流实质改变才可重开。工作文件保持并核验为#112716，队列为空。

### exp496-case14-early-sync-k-store  (CORRECT / REJECTED LOCALLY / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case14_early_sync_k_store_exp496.cpp`，SHA=`eaec84a0a6cae03ddf977d82cb1e3829564cae033315a615d315758cdd07fb03`。只给case14 exact fixed15 `paged_decode_case11_headpair_z4_kernel`新增`EARLY_SYNC_NEXT_K_STORE`：BF16-MMA QK完成后，z4 physical wave先release，再将同步loaded next-K `uint4`提前写入死亡`s_k` row；next-V仍跨PV保留并于PV后写入`s_v`。该B1/KV4/z4、四token/wave、fixed15 helper与case12 z8不同，其他case、split257、tail、deferred reference、symmetric finalizer、partial ABI和reducer均不变。
- **资源与correctness**：实际case14 producer仍为`82 MTreg / 64 STreg / 8320 B shared / 0 stack / 5 waves`，没有兑现预期的lifetime资源下降。`c500_case_manifest.py`和`test_kernel_logic.py`均通过；同一candidate C500 full、boundary、random均14/14、finite且满足容差。case14同进程序列`61519→1,2,15,16,17,239,240,241,479,480,481,911,912,913,61518→61519`通过，覆盖full fixed path、page/tail、padding trap和`full→short→full`/`short→full`复用。
- **交错 A/B、决策与重开边界**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`1.0303/1.0314/1.0415`、random=`0.9961/1.0013/1.0056`、boundary=`0.9914/1.0133/1.1065`。full稳定慢约3.1%，其它分布没有可接受共同收益，故不提交OJ。关闭这个 exact case14 z4 fixed15 synchronous early-K-store/lifetime mapping；只改release/barrier、store位置或load拼写不是changed precondition，只有K/V consumer ownership、实际等待覆盖或跨页数据流实质改变才可重开。工作文件保持并核验为#112716，队列为空。

### exp493-case11-register-fp32-ml  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case11_register_fp32_ml_exp493.cpp`，提交前工作文件SHA为`464b86b4cadf4b1a75cfc07bc2d923848e3bf210637007ff46bbb31d4e681e99`。只给case11（B16/KV4/L12251）的32-thread vec4 reducer增加`REGISTER_FP32_ML=true`：lane `0..31`各保留split `s0=lane`，lane `0..6`额外保留`s1=lane+32`的FP32 `(m,l)`到全局max/weight阶段，删除`partial_m→s_m→readback`的shared元数据往返；`s_w`仍为39个FP32 weight，partial ABI、log-sum-exp数学、acc float4读取、CTA geometry、producer与其他case不变。它不同于exp398的FP16x2压缩（仍使用`s_m`）和exp481的native-LDG partial-acc consumer（metadata ownership不变）。
- **资源、codegen与正确性门禁**：实际新case11 reducer为`64 MTreg / 33 STreg / 0 B static shared / 0 stack / 8 waves`，control为`64/35/0/0/8`；launch dynamic shared从`2×39×4=312 B`降为`39×4=156 B`。LLVM特化不再有`smem+n_split`的`s_m`访问，只写读`s_w`，case8/default vec4路径保持原特化。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case11同进程序列`12251→1,2,15,16,17,255,256,257,511,512,513,767,768,769,12250→12251`全部通过，覆盖live-split、page/tail、padding trap和`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716、warmup=5，9×20 candidate/control p10/p50/p90为full=`0.9973/0.9980/0.9992`、random=`0.9956/0.9993/1.0012`、boundary=`0.9854/0.9902/0.9953`；21×100强复测为full=`0.9963/0.9999/1.0019`、random=`0.9971/0.9990/1.0022`、boundary=`0.9787/0.9874/1.0028`。full/random接近噪声、boundary正向，未见可重复的系统性风险。它具备完整安全门禁、明确metadata-lifetime机制和只覆盖case11的问题，故按OJ优先规则预注册一次且仅一次probe：能否将#112716的case11 `223 μs/52分`推进到下一显示档。不得据此扫lane ownership、寄存器格式、shared layout或同源码复投。
- **OJ终态与control决策**：#112747 14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/228/93/232/40/222/375/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case11从`223→222 μs`但仍52分；未含此exact mapping的#112430/#112725已分别给出`222/221 μs`，故这一1 μs不能建立源码因果，更没有预注册display gain。raw内嵌源码、逐提交快照、实验快照与提交前工作文件SHA均为`464b86b4cadf4b1a75cfc07bc2d923848e3bf210637007ff46bbb31d4e681e99`。aggregate降至65.93，拒绝并关闭这条 exact case11 register-FP32 `(m,l)` metadata ownership；不得调lane owner、寄存器格式、shared layout或同源码重投。工作文件已逐字节恢复#112716，队列为空。

### exp497-case8-live-prefix-mulhi  (CORRECT / REJECTED LOCALLY / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case8_live_prefix_mulhi_exp497.cpp`，SHA=`ff3950489c25f31cbd63fdfa2ebec96e61ac0b67dae74572f02bda9b606c6953`。只给case8（B16/KV4/L4096）固定19页、14 split producer增加 `CASE8_LIVE_PREFIX_BALANCE`：满容量严格保持`19×13+9`，短实际长度只在control已live的前缀内均衡full pages，tail仍给最后live split。0..256 full-pages 已逐值核对 bucket、coverage 与partial slot写入；candidate LLVM不含新`udiv`，实际bucket为`__umulhi`/shift路径。
- **资源与正确性**：运行case8特化由control的`82 MTreg / 64 STreg / 8320 B / 0 stack / 5 waves`变为`90 MTreg / 56 STreg / 8320 B / 0 stack / 5 waves`。`c500_case_manifest.py`和`test_kernel_logic.py`均通过；同一candidate binary的C500 full、boundary、random各14/14，finite且满足容差。14个live-prefix转换边界、tail、padding-page trap和`4096→1→4096`同进程复用均通过。
- **交错 A/B、决策与重开边界**：相对fresh #112716、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`1.0038/1.0069/1.0096`、random=`1.0272/1.0302/1.0340`、boundary=`1.1725/1.1796/1.2321`。随机稳定慢约3%、boundary慢约18%，是跨分布的系统性回退，故不以OJ当作重试或参数扫描而提交。关闭这一 exact 14-way bucket/magic/switch/tail-owner 映射；只有实质消除mapping控制流或寄存器成本的表示、或不同producer数据流，才能以changed precondition重开。工作文件保持#112716，队列为空。

### exp498-case14-fold-alpha-into-duplicate-mma-lanes  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case14_fold_alpha_mma_exp498.cpp`，提交前工作文件、raw内嵌源码和逐提交快照SHA均为`25bcfdcbe5412bae3c03ef62f0fca4472ebb96a9eca783c453b84b02db1e47bd`。只在case14 fixed15 BF16-MMA热路径中，把本已重复token0 score的`tx=4/12` lane在同一条`exp2`内改为计算两个head的`alpha=m_old-m_new`；只有实际`new_max && l>0`时才row-broadcast并消费alpha，正常token权重仍由`tx=0..3/8..11`产生。当前deferred-reference、split257、z4 finalizer、PV ownership、partial ABI、tail和其他case均不变。这与旧exp301在非延迟状态流中额外安排alpha不同；本轮alpha消费受已接受的deferred-reference guard稀疏化。
- **资源与correctness**：case14 producer保持`82 MTreg / 64 STreg / 8320 B shared / 0 stack / 5 waves`，无stack/spill。`c500_case_manifest.py`和`test_kernel_logic.py`通过；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case14同进程序列`61519→1,2,15,16,17,239,240,241,479,480,481,3839,3840,3841,61518→61519`通过，覆盖fixed15、split/tail、padding trap与`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5，9×20的candidate/control p10/p50/p90为full=`1.0035/1.0056/1.0093`、random=`0.9961/1.0007/1.0026`、boundary=`0.9914/1.0105/1.0820`；full 21×100强复测为`1.0018/1.0033/1.0079`。满长约0.3%负信号但并未在三分布形成可重复的系统性回退；该候选具有单一数学/ownership机制、完整安全门禁，故按OJ优先规则预注册一次且仅一次probe：能否让#112716的case14 `141 μs/54分`回到`140 μs/55分`。不得据此扫描fold lane、broadcast、guard、阈值或同源码复投。
- **OJ终态与control决策**：#112756 14/14 Accepted / **`65.93`**，case1–14=`3/4/9/23/17/28/225/94/236/40/221/374/181/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case14保持`141 μs/54分`，所以不支持该exact fold产生真实OJ收益；case7/8/11/12等无覆盖路径的同场改变只作timing-tier样本。raw内嵌代码、`cuda_112756.cpp`逐提交快照和实验源码SHA均为上述`25bc…e47bd`。拒绝并关闭此exact duplicate-score-lane alpha ownership/fold；不得只换fold lane、broadcast、guard或同状态流重投，只有score/PV consumer ownership、reference或producer数据流出现实质新前提才可重开。工作文件已逐字节恢复#112716，队列为空。

### exp499-case12-live-prefix-magic  (CORRECT / LOCAL NEUTRAL / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_live_prefix_magic_exp499.cpp`，候选、提交raw和逐提交快照SHA均为`7e0246019862d62a9d9080fddc311d7ea3c1f68fdcf984eea776c959f927ac6d`（终态后工作文件已恢复#112716）。只给case12（B8/KV8/L32768）现有40个split的`paged_decode_case13_kv8_headpair_z8_kernel`启用`CASE12_LIVE_PREFIX_MAGIC=true`。满容量仍严格是39个52页加最后20页的control映射；短实际长度仅在control既有的`ceil(full_pages/52)`个live slot内均衡页。`ceil(x/n)`使用n=2..40的只读32-bit reciprocal table与`__umulhi`，不执行per-CTA动态除法；split数、partial slot count、live reducer count、K/V loader、QK/PV、tail ABI和其他case均不变。这不同于exp448的runtime valid-pages/n_split除法，也不同于exp484/485的case7三个bucket：本轮为case12独立的、固定40-slot、动态magic-index precondition。
- **静态页契约与资源门禁**：对`full_pages=0..2048`逐值验证`live_splits=ceil(full_pages/52)`、`bucket_pages=ceil(full_pages/live_splits)`、所有split区间连续覆盖`[0,full_pages)`且无重叠/漏页；`full_pages=0`仍只由split0拥有tail。C500 `-resource-usage` 的实际case12特化 `<true,false,false,true>` 为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,false,false>`相同；constant-table读没有降低驻留档。
- **correctness**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16639,16640,16641,32447,32448,32449,32751,32752,32767→32768`全部通过，覆盖live-prefix 1/2/3/20/21/39/40转换、页/尾边界、padding trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9993/1.0013/1.0016`、random=`0.9986/0.9995/1.0034`、boundary=`0.9950/1.0036/1.0054`。三个分布均接近噪声，未见与映射覆盖一致、明显且可重复的系统性回退；本地A/B只作为风险证据，不能取代OJ真实性能。按单一差异和OJ优先规则，预注册一次且仅一次probe：在真实OJ实际`cache_seqlens`分布下，是否能让case12相对#112716的`375 μs/60分`产生可归因改善或跨显示档；不得据此扫描magic、bucket、映射时点或同源码复投。
- **OJ终态与control决策**：#112761 14/14 Accepted / **`65.86`**，case1–14=`3/4/9/23/17/28/228/94/235/40/224/370/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。目标`375→370 μs`却仍为60分；未修改case12的#112725/#112736已有`372/374 μs`，故单次同档样本无法排除 timing tier，既无可归因 display gain也不支持替换control。raw内嵌代码、实验快照、逐提交快照与提交前工作文件SHA均为上述`7e0246…7ac6`。关闭这一 exact reciprocal/bucket/mapping-time 路线，不调表项、bucket、映射时点或同源码复投；只有不同shape独立的页契约、资源和正确性前提才可另行提出。工作文件已逐字节恢复#112716，队列为空。

### exp502-case11-symmetric-deferred-reference  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case11_symmetric_deferred_reference_exp502.cpp`，提交前工作文件、raw内嵌源码与`solutions/archive/2026-08-15-submissions/cuda_112769.cpp`的SHA均为`0274f422e2726c7bb76bc0dfd805abb965c22f9c0b924515a019caacb77db7b9`。只在case11既有39-slot head-pair/z4 BF16-MMA producer新增`CASE11_DEFERRED_REFERENCE_RESCALE`模板开关：`m`仍是FP32 `(l,acc)`的指数参考，首个有效页安装`m_page`，之后仅`m_page > m + 8`时才重缩放`l`和16个FP32 accumulator；split39、K+V register lookahead、QK/PV、partial ABI、vec4 reducer、tail和其他case不变。exp444在旧z0-only finalizer下已建立数学与本地正向，但不能直接证明当前状态流；#112716继承了exp464的对称z4 finalizer，故这是唯一的 finalizer/consumer-state changed precondition，而非阈值或guard扫描。
- **资源与完整正确性门禁**：实际case11特化为`80 MTreg / 62 STreg / 8320 B shared / 0 stack / 6 waves`；control的同一路径为`80/58/8320/0/6`，STreg增加但无spill、无shared增长且驻留档不变。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且100% tolerance match。case11同进程序列`12251→1→2→15→16→17→319→320→321→639→640→641→12143→12144→12145→12159→12160→12161→12175→12176→12177→12239→12240→12241→12250→12251`及额外`12251→1→12251`均通过，覆盖页、39-split、tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册OJ问题**：以fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为case11 full=`0.9953/0.9969/0.9991`、random=`0.9906/0.9951/0.9971`、boundary=`0.9858/0.9900/1.0023`。三分布均没有系统性回退，且机制与旧finalizer反证不同；按OJ性能真值和单一差异规则，预注册一次且仅一次probe：当前对称finalizer下的case11 deferred reference能否将#112716的`223 μs/52分`推进到下一显示档。不得据此调headroom、guard、store/barrier或同源码重投。
- **OJ终态与control决策**：确认队列为空、dry-run和实际POST前两次SHA一致后只创建 **#112769**。它正常完成14/14 Accepted / **`65.86`**，case1–14=`3/4/9/23/17/28/226/94/230/40/222/376/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。唯一目标case11由`223→222 μs`却保持52分；未含此exact state-flow的#112765与#112747已有`222 μs`样本，不能把同档变化归因给candidate，更没有display gain或aggregate收益。关闭这个 exact case11 symmetric-finalizer `+8` deferred-reference state-flow；只有reference表示、finalizer/merge-tree、producer/consumer ownership或实际共享状态读写量发生实质新前提才可重开。工作文件恢复#112716，队列为空。

### exp501-case7-single-live-direct-out  (STATIC RESOURCE FAIL / NO C500 / NO OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉。首版快照为`solutions/archive/2026-08-15-experiments/cuda_case7_single_live_direct_out_exp501.cpp`（SHA=`e8f8ea02a6fd660727a8dae2e96e8b773a1efc36b04c23769bd84fe0aa2edc11`）；最终资源收敛版为`solutions/archive/2026-08-15-experiments/cuda_case7_single_live_direct_out_exp501_lifetime.cpp`（SHA=`40a33f78425a36e069010efefcceed9f059fd54a059c192d56946ea6c2c1e48c`）。只给case7的既有z8 producer/reducer增加编译期`DIRECT_OUT_SINGLE_LIVE`：仍固定3个CTA、满容量仍严格为`43/43/42`页；仅当某个batch row实际`full_pages<=43`（含tail-only）时由split0在完成FP32 z-tree后直接归一化写BF16 output，并让匹配group8 reducer在同一row的`live_splits==1`、且读取workspace前直接返回。0-live row仍走既有零输出路径，2/3-live row仍走原packed partial/reducer ABI。它不同于exp416的全局`split→1`串行化，也不引入counter、atomic或改变workspace/grid。
- **静态资源门禁与一次收敛尝试**：control case7 producer `<true,false,true>` 为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`。首版direct-out特化 `<true,false,true,true>` 为`84/54/8448/0/5`，超过`MTreg<=82`和`STreg<=50`硬门槛；reducer特化为`60 MTreg / 22 STreg / 0 shared / 0 stack / 8 waves`，没有问题。为缩短direct写回的寄存器寿命，只做过一次有数据流依据的收敛：利用`h1=h0+2`以`out2 += HEAD_DIM`复用head-pair输出地址，且在h0 stores退休后复用同一`inv_l`寄存器给h1。最终仍为producer`84/54/8448/0/5`，没有改善；因此不做表达式、store次序或模板拼写扫描。
- **结论与重开边界**：静态资源未过门槛，故不占用C500、不跑correctness/A-B，也不提交OJ。关闭这条 exact “case7 single-live producer direct BF16 output + reducer early return”实现；只有能实质改变direct-output consumer ownership、状态格式或消除完整转换/地址活跃区间的另一个数据流前提，才可重新提出。工作文件已恢复为#112716。

### exp500-case11-live-prefix-magic  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case11_live_prefix_magic_exp500.cpp`，SHA=`5993ecff537c0844e98aaadfd7c8caedd2c0ae8208c99f3e720a1d4cbf25c668`。只给case11（B16/KV4/L12251）的既有39-slot head-pair/z4 BF16-MMA producer启用`CASE11_LIVE_PREFIX_MAGIC=true`。满容量仍严格为`39×20`个full page；短真实长度只在control reducer本已读取的`ceil(full_pages/20)`个live prefix 内，用只读32-bit reciprocal table和`__umulhi`均衡full pages。split数、partial slot count、reducer live count、K/V register lookahead、QK/PV、tail ABI、z4 finalizer和其他case均不变；这是case11独立的39-slot页契约，非已关闭的case8/case12 exact mapping。
- **静态页契约、codegen与资源门禁**：对`full_pages=0..765`逐值验证magic table、`live_splits=ceil(full_pages/20)`、`bucket_pages=ceil(full_pages/live_splits)`、连续无重叠覆盖和满容量`39×20`映射。实际case11 LLVM只保留control已有的`seqlen/16`，live-prefix为64-bit multiply-high/shift与constant-table读，无候选`udiv`。`-resource-usage`中实际新特化`<true,true,false,true,true,true,true,true,false,true,false,false,false,true,true,true,true,true,true,true>`为`80 MTreg / 58 STreg / 8320 B shared / 0 stack / 6 waves`；control同一路径为`80/60/8320/0/6`，没有spill或驻留档回退。
- **correctness**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一candidate C500 full、boundary、random（seed=20260809）各14/14、finite且满足容差。case11在同一进程额外通过86个精确长度：`1,2,15,16,17`、每个live-prefix `1→2`至`38→39`转换前后的页边界、`12239,12240,12241,12250,12251`，覆盖tail、padding-page trap、inactive split和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case11 candidate/control p10/p50/p90为full=`1.0003/1.0014/1.0023`、random=`0.9912/0.9951/0.9981`、boundary=`0.9910/0.9964/1.0109`。满长约0.14%负信号、random/boundary小幅正向，未见与变更范围一致、明显且可重复的系统性回退。本地性能只作风险证据；按单一差异和OJ优先规则，预注册一次且仅一次probe：真实OJ case11实际`cache_seqlens`分布下，该无除法live-prefix调度能否让#112716的`223 μs/52分`产生可归因改善或跨显示档；不得据此扫描table、bucket、mapping时点或同源码复投。
- **OJ终态与control决策**：#112765 14/14 Accepted / **`65.93`**，case1–14=`3/4/10/22/17/28/224/94/238/40/222/371/182/140 μs`，分数=`92/90/82/73/73/63/55/54/57/61/52/60/56/55`。唯一目标case11从control的`223→222 μs`但仍为52分；未含此exact mapping的相邻样本已有`222/221 μs`，不能建立可归因display gain，aggregate也低于control。raw内嵌代码、`solutions/archive/2026-08-15-submissions/cuda_112765.cpp`、实验快照与提交前工作文件SHA均为`5993ecff537c0844e98aaadfd7c8caedd2c0ae8208c99f3e720a1d4cbf25c668`。关闭这个exact case11 live-prefix reciprocal/magic mapping；不得扫描table、bucket、mapping时点或同源码重投。工作文件已逐字节恢复#112716，队列为空。

### exp503-case11-mixed-first-stage-bf16-state  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case11_mixed_stage1_bf16_state_exp503.cpp`，提交前工作文件、raw内嵌源码与`solutions/archive/2026-08-15-submissions/cuda_112775.cpp`的SHA均为`47d2cfc05531771d1920933e9be739bf0b4af7117f9e84ff5140890aab5123cb`。只把case11对称 z4 tree 的第一条跨-wave边（z2/z3→z0/z1）改为写 normalized BF16 `acc/l`；FP32 `(m,l)`另存，z0/z1恢复 peer 后的第二阶段 payload 仍为FP32。它改变的是第一阶段 producer/consumer state contract，而非 exp461 的完整 z-tree BF16 round-trip；QK/PV、loader、split39、partial ABI、reducer、tail与其他case不变。
- **资源与正确性门禁**：实际 case11 producer 为`80 MTreg / 58 STreg / 8320 B shared / 0 stack / 6 waves`，与 control 同档；CPU 语义回归通过。C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差；case11按39-split/page/tail精确边界、padding-page trap、`full→short→full`和`short→full`复用均通过。混合状态的空 split 与`l<=0`路径也始终发布有限的零 normalized payload，不依赖旧workspace。
- **交错 A/B 与预注册 OJ 问题**：相对 fresh #112716，candidate/control p50 为 full=`0.9978`、random=`1.0014`、boundary=`1.0016`。本地未见与改动范围一致的明显可重复系统性回退，但也没有共同正向；按OJ优先规则，预注册一次且仅一次 probe：第一条跨-wave BF16 normalized state edge 能否让case11从`223 μs/52分`跨档。不得据此扫描packing、lifetime或同一source-spelling。
- **OJ终态与control决策**：#112775 14/14 Accepted / **`66.00`**，case1–14=`3/4/10/23/17/28/227/93/236/39/223/371/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case11仍为`223 μs/52分`，没有预注册的display gain；其他case的同场变化没有运行差异覆盖，不能归因。关闭这一 exact mixed first-stage BF16 normalized-state contract；不得以packing、lifetime或source-spelling变体重投，只有merge tree、producer/consumer ownership或实际共享状态读写量实质改变才可重开。工作文件已逐字节恢复#112716，队列为空。

### exp504-case11-vec4-register-coefficients  (CORRECT / REJECTED LOCALLY / NO OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case11_vec4_register_coefficients_exp504.cpp`，SHA=`2bf461f6ed3562d7095f24feed1489b01308610dd20506f8f902b86b3053c602`。case11 32-lane vec4 reducer让 owner lane 保留每个 live split 的FP32 `(m,l)`及其`w=exp2(m_s-m)`，通过32-lane shuffle向accumulator consumer广播，删除`s_m`和`s_w` materialization。它不同于 exp493：后者只让`(m,l)`入寄存器但仍写读`s_w`；本轮改变的是完整 coefficient producer/consumer contract。
- **资源与正确性**：reducer 资源从control的`64 MTreg / 35 STreg / 0 B / 0 stack / 8 waves`变为`26 MTreg / 26 STreg / 0 B / 0 stack / 8 waves`，producer未变。目标case11的C500 full、boundary、random均数值正确、finite且满足容差；live split owner、fused tail和inactive split均未读取旧partial。
- **交错 A/B、决策与重开边界**：尽管寄存器和shared traffic明显减少，candidate/control p50 系统性回退：full=`1.0280`、random=`1.0375`、boundary=`1.0775`。动态每split coefficient shuffle的开销超过消除shared的收益，符合与变更覆盖一致的明显重复负信号；不消耗OJ probe。关闭这一 exact all-register coefficient ownership；不得只改shuffle语法、lane编号或minor ownership变体，只有显著不同的coefficient-consumer contract才可重开。工作文件保持#112716。

### exp505–510-case12-split-phase-dual-token-bsm  (CORRECTNESS BOUNDARY FOUND / LOCAL REJECTED / NO OJ / CLOSED)

- **父/control、唯一机制与完整快照**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉。初版`exp505`为`solutions/archive/2026-08-15-experiments/cuda_case12_split_phase_token_bsm_exp505.cpp`（SHA=`170e31bf0196762260904db545dd9e585259541f30c4e02c94b8f924c55d0666`），只给case12现有head-pair/z8 producer启用两个独立的tokenized BSM流：`wait(K_current) → QK → issue(K_next) while V_current is live → wait(V_current) → PV → issue(V_next)`；split40、z8 ownership、partial ABI、reducer和其他case不变。独立`c500_bsm_dual_token_pipeline_probe`的1025次K/V复用通过，但production说明“单物理wave原语可用”不能外推到所有live-split/tail生命周期。
- **初版反证与修补边界**：exp505在满长正确，但case12 boundary和精确`17`出现NaN；fresh精确`16/32/832`也失败，说明问题不仅是tail。exp507将fused tail并入最后full page的K-next/V-next链，修复17却使tail-only `1`不稳定，暴露opaque BSM token不能跨full-loop/tail控制流。exp508以同步tail替换token tail后，连一页full stream都出现不稳定，表明只改cold branch也会改变该特化的后端token代码生成。exp506保留为一次未通过编译的机械补丁证据，不是性能数据。上述版本均不提交。
- **容量行分流（exp510）与资源/数值门禁**：最终完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_split_phase_token_bsm_capacity_rows_exp510.cpp`，SHA=`2cf4c05c6fe41fc961a50ffb5252979ca828d1c8e20c744de2b363f21bc9fdf5`。它用两个顺序producer互斥写partial：只有`cache_seqlens[b] == pages_per_batch*16`的满容量行走exp505 BSM特化，所有短行（含exact-page、tail和mixed batch）走原同步z8特化；随后仍用同一vec2 reducer。实际resource分别为BSM `<true,false,false,true,true,false>`=`74 MTreg / 50 STreg / 8448 B / 0 stack / 6 waves`、同步short `<true,false,false,false,false,true>`=`82/50/8448/0/5`，均不低于control档。CPU manifest与logic均14/14；同一C500 binary full/boundary/random各14/14、finite且100% tolerance match。case12精确复用序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全通过；boundary batch同时含满容量和短行，验证两个producer的partial集合互斥且无旧workspace读取。
- **交错 A/B、拒绝与重开条件**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`1.0222/1.0239/1.0244`、random=`1.0222/1.0229/1.0254`、boundary=`1.3457/1.3555/1.3765`。第二producer的固定launch及短行完整同步路径构成与覆盖范围一致、跨三分布重复的系统性回退，尤其boundary慢约35.6%；因此按本地否决条件不占用OJ。关闭这一exact双token `K-next while V-current live`生命周期及其“满容量BSM + 非满容量同步双producer”安全分流；不得仅重排wait/issue、改tail分支、改row filter或同源码复投。只有能够消除额外producer launch并证明不同token consumer ownership、跨请求深度或后端等待覆盖的实质新前提，才可重新审查。工作文件恢复#112716。

### exp511-case7-single-live-direct-out-recheck  (STATIC RESOURCE FAIL / NO C500 / NO OJ / CLOSED)

- **父/control 与定位**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整快照为`solutions/archive/2026-08-15-experiments/cuda_case7_single_live_direct_out_exp511.cpp`，SHA=`45a13e63a1a79d7bb8f2bdb68a2bcd89682a2fd35c638c34e53f42f672d0518c`。它保持case7的3个producer CTA及`43/43/42`满容量映射，只在实际`live_splits==1`的row令split0完成z8树后直接归一化写BF16 output、并让group8 reducer在读workspace前返回；0-live仍由reducer清零、2/3-live保留原partial ABI。实现上与既有exp501相同的核心数据流，故本条只作为当前control上的独立资源复核，不构成可重开的新方向。
- **资源结论**：CPU `test_kernel_logic.py` 14/14通过，但`-resource-usage`的case7 producer `<true,false,true,true>`为`84 MTreg / 54 STreg / 8448 B / 0 stack / 5 waves`，超过control `<true,false,true>`的`82/50/8448/0/5`及预注册上限；配对reducer为`62/22/0/0/8`。一次使用已验证成对BF16 store形态的收敛没有改变该档位。因此不运行C500 correctness/A-B，也不提交OJ；不再以store顺序、循环写法或同一direct-output dataflow细扫。

### exp512-case7-single-live-compact-bf16-partial  (STATIC RESOURCE FAIL / NO C500 / NO OJ / CLOSED)

- **父/control、唯一 changed precondition 与完整快照**：从 #112716 分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case7_single_live_compact_bf16_partial_exp512.cpp`，SHA=`f0eb0035e87583ff545e4c999320ccebccd94681adfee089e6abebbd1b98c98c`。为消除exp511对output地址的活跃区间，只有case7的实际单live row将已完成FP32 z8 state归一化为8个BF16值，写入自身既有FP32-sized partial slot的前半；group8 reducer在`live_splits==1`时按同一slot拷贝16-byte BF16 payload到output，且不读取`partial_m/l`。满长及2/3-live row仍走原FP32 partial/reducer，0-live仍写零。它改变了单live row的partial producer/consumer格式，而不是重排exp511的direct store。
- **资源结论与边界**：最终收敛源码的实际case7 producer仍为`84 MTreg / 52 STreg / 8448 B / 0 stack / 5 waves`，control为`82/50/8448/0/5`；compact reducer为`64 MTreg / 22 STreg / 0 B / 0 stack / 8 waves`。即使移除output pointer活跃区间也未满足MT/ST硬门槛，故不跑C500 correctness/A-B或OJ。关闭当前z8 ownership下“single-live normalized BF16 compact partial + reducer copy”这一exact contract；只有能实质消除BF16转换/partial地址状态、改变producer/consumer ownership或线程布局的前提才可重开。工作文件须恢复#112716。

### exp513-case14-hierarchical-partial-tree  (CORRECT / REJECTED LOCALLY / NO OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case14_hierarchical_partial_tree_exp513.cpp`，SHA=`122b08576caa39e4fd5342343bc1bfdf3f0e81b7cb4bf6dcf5ee1c798a525b46`。case14保留其257个producer partial、fixed15 BF16-MMA、z4 finalizer和primary normalized-BF16 ABI；新增第一层按连续16个split进行稳定LSE合并的544-CTA `(group,head)` kernel，写出FP32 raw `(m,l,acc)`，随后以现有32-CTA one-head reducer合并17个group state。它复用`partial_acc`仅在normalized-BF16主partial未触及的上半分配，以及case14未使用的`partial_l`，不扩容、不依赖旧workspace。exp33/37/54/167/358/359/373分别只改单层线程/维度/heads/partial位宽或FMA链；都未覆盖“更多CTA的独立第一层 + 小fan-in终归约”这一tree/temporary-state契约。
- **资源与数值门禁**：primary case14 producer仍为`82 MTreg / 64 STreg / 8320 B / 0 stack / 5 waves`。新group reducer为`13 MTreg / 30 STreg / 0 B / 0 stack / 8 waves`；17-way FP32 final reducer为`40/36/0/0/8`。CPU manifest 与 logic 均通过；同一candidate C500 full、boundary、random（seed=20260809）均14/14、finite且满足容差。case14额外同进程覆盖`1,2,15,16,17,239,240,241`、16个`3840`-token tree-group边界各自的`-1/0/+1/+15/+16/+17`、`61518,61519`，以及`61519→1→61519`，均100% match；padding slot保持合法物理page ID而未被预读。
- **交错 A/B、决策与重开边界**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case14 candidate/control p10/p50/p90为full=`1.0078/1.0126/1.0173`、random=`1.0342/1.0367/1.0520`、boundary=`1.3470/1.3940/1.4839`。两次kernel launch和中间FP32写读的固定成本压过了32-CTA终归约并发不足的收益，且三个分布均为覆盖范围一致的系统性回退（boundary约39%）。因此按本地性能否决条件不提交OJ，也不扫描group size、group边界、temporary pointer或同一two-kernel tree。只有能去除额外launch/中间global round trip、改变跨CTA producer/consumer ownership，或出现新的硬件phase能力时才可重新提出；工作文件恢复#112716。

### exp514-kv8-initial-tail-gvm-bsm  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_kv8_initial_tail_gvm_bsm_exp514.cpp`，SHA=`bbd1a835dcd758f630e5c8eeed0425d4acd9713a7c0a87d586c990150111197a`。只改KV8 z8 head-pair helper的初始页与 fused-tail staging：以官方`__builtin_mxc_ldg_b128_bsm`直接写既有shared K/V行，并在每个K/V对之后执行`__builtin_mxc_arrive(64)`与`__builtin_mxc_barrier_inst()`；热循环的K+V-over-PV scalar next-page lookahead、split、ownership、partial/reducer ABI与所有KV4路径保持不变。它不是exp454/458–460的token-BSM生命周期，也不是exp487的async-register payload：这里测试的是此前未用于本shape的raw GVM→shared BSM loader及官方等待契约；预期仅改变case7/9/12/13的初始页和tail装载后端数据路径。
- **资源与正确性门禁**：`-resource-usage`中受影响的case13-kv8-z8特化仍为`82 MTreg / 48–50 STreg / 8448 B shared / 0 stack / 5 waves`，没有驻留档回退。CPU manifest与logic均14/14；同一C500 binary的full、boundary、random（seed=20260809）均14/14、finite且100% tolerance match。case7/9/12/13又分别通过同进程`full→1,2,15,16,17→`各自pages-per-split的`-1/0/+1`边界、下一split边界和`capacity-1→capacity`序列，覆盖tail、padding-page trap、inactive split及workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full：case7=`0.9983/0.9994/1.0028`、case9=`0.9969/0.9982/1.0003`、case12=`0.9991/0.9998/1.0004`、case13=`0.9974/1.0012/1.0062`；random：`0.9942/1.0005/1.0066`、`0.9851/0.9933/0.9970`、`0.9977/1.0015/1.0029`、`0.9952/1.0011/1.0111`；boundary：`0.9909/0.9986/1.0023`、`0.9921/1.0017/1.0034`、`0.9940/1.0003/1.0032`、`0.9927/1.0000/1.0647`。没有与改动覆盖一致、明显且可重复的系统性回退。本地数据只作为风险标签；按 OJ 优先规则预注册一次且仅一次 probe：raw GVM→shared BSM 的初始/尾页路径能否在OJ实际长度分布下令case7/9/12/13产生可归因改善或跨显示档。不得据此扫描builtin参数、等待拼写、覆盖范围或同源码复投。
- **OJ终态与control决策**：确认队列为空、dry-run和实际POST前两次SHA一致后只创建 **#112833**。它正常完成14/14 Accepted / **`65.86`**，case1–14=`3/4/9/23/17/28/225/93/232/40/224/370/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。覆盖的case7（`227→225 μs`）、case9（`237→232 μs`）和case12（`375→370 μs`）均没有显示分收益；case13从`181 μs/57分`到`182 μs/56分`。因此既无预注册的display gain，且覆盖路径出现一档反向，aggregate也低于control；关闭这一 exact raw GVM→shared BSM initial/tail loader与`arrive(64)+barrier_inst()`等待契约。不得调builtin参数、等待拼写或启用范围后复投；只有实际等待覆盖、consumer ownership或后端能力发生实质变化才可重开。raw内嵌源码、实验快照、逐提交源码与提交前SHA均为上述`bbd1a835…197a`；工作文件须恢复#112716，当前队列为空。

### exp515-case13-native-partial-stg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_native_partial_stg_exp515.cpp`，工作文件与快照 SHA 均为`132e632579cb5fc3bb2c83f7ac6b8bf540df6edec05a25d1954bc953ef1ad251`。只给case13（B1/KV8/L58966、65 split）的z8 producer启用`__builtin_mxc_stg_b128_predicator`，写出每个head-pair四段16-byte对齐的`partial_acc float4`；split、QK/PV、K/V loader、partial ABI、64-thread vec2 reducer、tail及其他case均不变。它不同于已关闭的exp483：后者是case7的producer→group8 reducer几何，本轮是B1/65-split producer→vec2-reducer handoff。
- **静态后端与资源门禁**：control LLVM的`llvm.mxc.stg.predicator.v4i32`计数为0；candidate IR有4个实际调用（全局5个匹配含1个declaration），确认不是普通float4 store的同义源码改写。`-resource-usage`中case13候选`<true,true,false,true>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false,false>`同档，无spill或驻留回退。
- **correctness**：当前SHA上`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；fresh candidate binary的C500 full、boundary、random（seed=20260809）也均14/14、finite、100% tolerance match。case13同进程精确序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58965,58966`全通过，覆盖尾页、57-page split边界、padding-page trap以及`full→short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9947/1.0017/1.0028`、random=`0.9938/1.0050/1.0110`、boundary=`0.9148/0.9860/1.0271`。本地没有与变更覆盖一致、明显且可重复的系统性回退；轻微中性/负信号只作风险标记。确认OJ队列没有非终态后，预注册一次且仅一次probe：在OJ实际case13长度分布下，native producer→vec2-reducer partial store是否能让#112716的`181 μs/57分`产生可归因改善或跨显示档。不得据此调builtin参数、cast、store位置、启用范围或同源码复投。
- **OJ终态与control决策**：确认dry-run与实际POST前两次SHA均为`132e632579cb5fc3bb2c83f7ac6b8bf540df6edec05a25d1954bc953ef1ad251`后只创建 **#112849**。它14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/227/93/234/40/222/374/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case13保持`181 μs/57分`，没有display gain；case11/12/14等未改路径的同场变化不归因，aggregate低于control。raw内嵌源码、逐提交快照和实验快照SHA一致。关闭这个 exact native-STG producer→case13-vec2-reducer partial handoff；不得调builtin参数、cast、store位置、启用范围或同源码复投，只有producer/consumer ownership、partial格式或后端能力实质改变才可重开。工作文件已逐字节恢复#112716，队列为空。

### exp516-case12-readlane-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_readlane_reducer_exp516.cpp`，SHA=`28b685d112887d594a175cfe1ebdb97a3c2721a090a9f22c4ea12bfa114a6813`。只给case12 B8/KV8/L32768的64-thread vec2 reducer启用官方`__builtin_mxc_readlane`：每个physical lane持有一个最多40-slot的packed FP16 `(m,l)`及FP32 weight，accumulator按split读其owner lane的weight，删除`partial_m→s_m`和weight→`s_w` materialization。FP32 global-max/LSE、partial ABI、producer、tail、其他case和output ownership均不变；这是64-lane readlane metadata producer→consumer契约，非exp493/504的普通shuffle或旧vec4/group8 partial-LDG路线。
- **静态后端、资源与正确性门禁**：candidate IR有9处实际`llvm.mxc.rl` call（另1处declaration，control为零）；case12 reducer为`28 MTreg / 39 STreg / 0 B shared / 0 stack / 8 waves`，control为`38/39/0/0/8`，无spill或驻留回退。当前candidate binary的C500 full、boundary、random均14/14、finite且100% tolerance match；case12同进程精确序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767,32768`全通过，覆盖40-slot live split、tail、padding trap和workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9978/0.9988/1.0011`、random=`0.9986/1.0003/1.0016`、boundary=`0.9898/0.9947/1.0100`。本地没有与变更覆盖一致、明显且可重复的系统性回退；已排在#112849终态后的下一次且仅一次probe：OJ实际case12长度分布下，该64-lane readlane metadata handoff能否让#112716的`375 μs/60分`产生可归因改善或跨显示档。不得据此调lane、读法、shared大小、模板拼写或同源码复投。
- **OJ终态与control决策**：确认raw后运行`tools/archive_cuda_submissions.py`，raw内嵌源码、逐提交快照、实验快照与提交前工作文件SHA均为`28b685d112887d594a175cfe1ebdb97a3c2721a090a9f22c4ea12bfa114a6813`。#112858 14/14 Accepted / **`65.79`**，case1–14=`3/4/10/23/17/28/228/93/235/40/223/371/182/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case12从`375→371 μs`但仍60分；未含此exact handoff的#112761已有`370 μs/60分`，同档变化不能建立可兑现的源码收益，aggregate亦低于control。拒绝并关闭这条 exact readlane metadata/weight consumer contract；不得调lane、readlane调用形态、shared大小、模板拼写或同源码复投，只有metadata格式、producer/consumer ownership或后端能力实质改变才可重开。工作文件已逐字节恢复#112716，队列为空。

### exp517-case13-vec2-partial-native-ldg  (CORRECTNESS FAIL / NO OJ / CLOSED)

- **父/control、唯一差异与静态门禁**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_vec2_partial_native_ldg_exp517.cpp`，SHA=`362d5e3f0a802394ccf43478a0a3feba35b17ccb5d3459a22c18ef7c83d05d51`。只给case13 B1/KV8/L58966的64-thread vec2 reducer让偶数lane以`__builtin_mxc_ldg_b128`读取对齐的两段`partial_acc float4`，奇数lane经同warp handoff取得高两个FP32；metadata、LSE、split65、tail、producer、output ownership及其他case不变。IR有5处实际`llvm.mxc.ldg.predicator.v4i32`（control为零），reducer资源为`18 MTreg / 36 STreg / 0 B / 0 stack / 8 waves`，control为`38/39/0/0/8`。
- **真实C500正确性失败与决策**：CPU `test_kernel_logic.py`通过，candidate binary的14-case full与boundary harness通过；full case13为`match=0.991943`、`max_error=2.221680e-02`、`max_tol_ratio=1.358`，仍满足perf容差。但14-case random（seed=`20260809`）中case13失败：`match=0.974121`、`max_error=2.990723e-02`、`max_tol_ratio=1.815`；随后单独重跑case13 random得到完全相同的失败。该random长度错误违反99% match门槛，故不跑精确复用/A-B、不创建OJ probe。关闭这个 exact even-lane native-LDG `partial_acc` consumer→odd-lane handoff；不得只调builtin参数、cast、偶奇lane、shuffle拼写或加载覆盖范围，只有partial格式、producer/consumer ownership或后端能力实质改变才可重开。工作文件保持#112716。

### exp518-case13-readlane-metadata-overflow  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_readlane_metadata_exp518.cpp`，SHA=`c459d248c18d3ee7b931953677386b4f98905dbd8c3651f13beabe07d0424a49`。只给case13 B1/KV8/L58966的64-thread vec2 reducer启用`__builtin_mxc_readlane` metadata/weight handoff：physical lanes`0..63`分别持有split`0..63`的packed FP16 `(m,l)`及FP32 weight，唯一的split64由lane0额外持有；在全局max、LSE与accumulator阶段，s=64专门从lane0读overflow weight，其余s从同号physical lane读。删除每split的`s_m/s_w` materialization，FP32 global-max/LSE、partial ABI、split65、producer、tail、output ownership与其他case不变。这与exp516的case12≤40 one-owner-per-lane契约不同，关键新前提是case13的65th overflow partial与lane0双metadata owner。
- **静态资源、codegen与正确性门禁**：resource binary SHA=`7a00ff88d20d0587c6467e3a58eec8ba78a89f9791cec5ae9e43bf4a53bf67bf`；实际case13 reducer `<true,false,true,false,true>`为`30 MTreg / 40 STreg / 0 B shared / 0 stack / 8 waves`，control `<true,false,true,false,false>`为`38/36/0/0/8`，无spill或驻留档变化。device LLVM有9处实际`llvm.mxc.rl`（外加1处declaration），且实际case13 specialization保留s=64→lane0的select，不是普通shared-load拼写。CPU `test_kernel_logic.py`通过；同一candidate的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖page/tail、64→65 live-split边界、padding trap与`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9976/1.0015/1.0040`、random=`0.9978/1.0009/1.0069`、boundary=`0.9941/1.0102/1.0328`。三个分布没有与该contract覆盖一致、明显且可重复的系统性回退；本地数据只作为风险证据，不能替代真实OJ。已预注册一次且仅一次probe：该65-split overflow-aware readlane metadata/weight handoff能否将#112716的case13 `181 μs/57分`推进到下一显示档。不得据此调lane、overflow归属、readlane调用形态、shared大小、模板拼写或同源码复投。
- **提交身份、OJ终态与control决策**：确认没有非终态提交后，dry-run前后和实际POST前工作文件SHA均为`c459d248c18d3ee7b931953677386b4f98905dbd8c3651f13beabe07d0424a49`，只创建 **#112873**。终态后保存raw并运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照、实验快照和提交前SHA均一致。#112873 14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/226/94/233/40/221/372/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一目标case13保持#112716的`181 μs/57分`，没有display gain；case7/8/9/11/12/14等未覆盖路径的同场波动不归因，aggregate低于control。拒绝并关闭这条 exact 65th-overflow/lane0 readlane metadata consumer contract；不得调lane、overflow归属、readlane调用形态、shared大小、模板拼写或同源码复投，只有metadata格式、producer/consumer ownership或后端能力实质改变才可重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp519-case13-final-wave-peer-merge  (CORRECT / LOCAL REJECTED / NO OJ / CLOSED)

- **父/control、唯一差异与 changed-precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_final_wave_merge_exp519.cpp`，SHA=`430f0bbc9d3b009019f5ffe5cad47328768dbf1920c72fd5ae7081ad789dfd3e`。只给case13 B1/KV8/L58966的`dim3(16,2,8)` z8 producer改最后一条z-state边：已有前两层跨物理wave的shared tree不变，最后同一物理64-lane wave内的`z1→z0` FP32 `(m,l,acc[8])`改为全64 lane执行`lane^32` raw BSM exchange、仅z0消费并直接输出partial。它省去最后两个state-row shared write/read及其CTA barrier，partial ABI、split65、QK/PV、loader、tail、earlier tree和其他case不变。它不同于exp419/420把四个相邻z pair提前全部raw-merge后重排整棵树；本轮仅收缩最后一条同wave consumer edge。
- **资源与数值门禁**：`-resource-usage`中实际case13新特化`<true,true,false,true>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，control `<true,true,false,false>`也为`82/48/8448/0/5`，无spill或驻留降档；candidate binary SHA=`ca68743e0f2407b7be0ccc5f8714ffa4e648916356827524be07d683c9a57753`。CPU `test_kernel_logic.py` 14/14通过；同一C500 binary的full、boundary、random（seed=20260809）均14/14、finite且100% tolerance match。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`亦全部通过，覆盖tail、split、64→65 live-split、padding trap及`full→short→full`/`short→full`复用。
- **交错 A/B、拒绝与边界**：相对fresh #112716 control（control binary SHA=`52ebd4edc7e4f2e037baf6dc7d1c3f0d72c3331b20072f6797b82e1300d97e75`）、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`1.0029/1.0054/1.0076`、random=`0.9989/1.0063/1.0103`、boundary=`0.9753/1.0184/1.0465`。三个分布的p50均回退，且boundary高尾更差；这构成覆盖范围一致、可重复的系统性负信号，按本地性能否决条件不占用OJ。关闭“case13只用raw lane^32替换最后z1→z0 shared edge”这一exact merge-stage placement；不得以raw/readlane同语义交换、参与lane、barrier删减或source拼写继续细扫。只有跨半waveconsumer ownership、state表示、merge tree或后端交换能力实质改变才能重新提出。工作文件仍冻结为在途exp518，未被本实验改写。

### exp520-case13-hot-next-k-gvm-bsm  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_hot_next_k_gvm_bsm_exp520.cpp`，工作文件与快照 SHA 均为`6a0b5a1917d52fc6ad1d4d56ba106960005a6f8b016e264ee5f9551f65e9c24b`。只给case13 B1/KV8/L58966的`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`启用`HOT_NEXT_K_GVM_BSM`：当前页QK消费完`s_k`后，next-K 由真实`__builtin_mxc_ldg_b128_bsm`直接写入这个在PV期间已死的shared K row；next-V保留control的四个标量register lookahead，在PV后照常写`s_v`。每个热页在PV完成后以`__builtin_mxc_arrive(64)+__builtin_mxc_barrier_inst()`退休K传输，下一页才读取`s_k`。初始页和tail仍保持control同步loader，split65、z8 ownership、QK/PV、partial ABI、vec2 reducer及其他case均不变。这与exp514的初始/尾页raw-BSM覆盖、以及exp458/459的token-BSM producer/lifetime均不同：本轮只改变热next-K的producer目的地、寄存器寿命和等待覆盖。
- **静态后端与资源门禁**：candidate LLVM 的实际case13特化保留`llvm.mxc.ldg.predicator.bsm.v4i32`和`llvm.mxc.arrive(64)`，不是同步普通load的降级；其后为warp/barrier等待。`-resource-usage`中candidate case13为`80 MTreg / 48 STreg / 8448 B shared / 0 stack / 6 waves`，control同一路径为`82/48/8448/0/5`，无spill且驻留档提升。
- **正确性**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一fresh candidate的C500 full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。case13同进程精确序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖57-page split、64→65 live-split、tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9854/0.9969/1.0117`、random=`0.9750/1.0001/1.0040`、boundary=`0.9670/0.9984/1.0631`。random中性、full/boundary p50轻微正向；boundary单轮高尾不足以构成与覆盖范围一致、明显且可重复的系统性回退。本地性能仅作风险证据。按OJ优先规则，预注册一次且仅一次probe：真实OJ case13中，将next-K从跨PV标量寿命改为raw GVM→dead-`s_k` producer能否让#112716的`181 μs/57分`产生可归因改善或跨显示档。不得据此改builtin参数、等待拼写、load时点、启用范围或同源码复投。
- **OJ终态与control决策**：确认OJ队列为空、dry-run和实际POST前两次SHA均为`6a0b5a1917d52fc6ad1d4d56ba106960005a6f8b016e264ee5f9551f65e9c24b`后只创建 **#112909**。它正常完成14/14 Accepted / **`65.86`**，case1–14=`3/4/10/22/17/28/227/94/246/40/223/375/181/141 μs`，分数=`92/90/82/73/73/63/55/54/56/61/52/60/57/54`。唯一覆盖目标case13保持#112716的`181 μs/57分`，没有display gain；case9的`237→246 μs`等未改路径同场波动不归因，aggregate低于control。`tools/archive_cuda_submissions.py`从raw内嵌源码提取的逐提交快照、实验快照和提交前SHA均为上述值。因此拒绝并关闭这个 exact hot next-K raw GVM→dead-`s_k` producer/wait contract；不得调builtin参数、wait/barrier拼写、load时点、启用范围或同源码复投，只有K/V consumer ownership、多请求深度或后端等待/producer能力实质改变才可重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp521-case13-fold-alpha-into-bit1-weight-exp  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_fold_alpha_exp521.cpp`，工作文件与候选SHA均为`be31a8aae12bddcd47d89983681849634e6da2d5c39da56e8debf0778319eb1f`。只给case13 B1/KV8/L58966的native-bit1、two-token z8热全页循环增加`FOLD_ALPHA_IN_WEIGHT_EXP=true`：正常PV权重仍仅从lane `0..3`广播；此前未被该映射消费的lane `4/5`在同一行级`exp2`中承载两头`m_old-m_new`的alpha，随后仅在`new_max && l>0`时从这两lane广播并重缩放。tail、split65、QK、K/V loader、partial ABI、reducer、z-state与所有其他dispatch保持control。这不是已关闭的exp498：后者是case14 MMA重复score lane及其deferred-reference数据流；本轮的关键前提是case13 bit1 two-token score→PV consumer只消费lane `0..3`。
- **资源与正确性门禁**：实际case13 candidate specialization为`82 MTreg / 52 STreg / 8448 B shared / 0 stack / 5 waves`；control为`82/48/8448/0/5`，没有spill或驻留降档，但`+4 STreg`是明确风险。`c500_case_manifest.py`与`test_kernel_logic.py`通过；同一candidate binary（SHA=`9cd5c6c6871e68a2e7b1cad9547011e6bb36555ea9dedf76ba5887ac6fe7525a`）的C500 full、boundary、random（seed=`20260809`）均14/14、finite且满足容差，case13 full/random最大误差均为`1.220703e-04`。同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`通过，覆盖尾页、64→65 live-split、padding trap与`full→short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control（control binary SHA=`52ebd4edc7e4f2e037baf6dc7d1c3f0d72c3331b20072f6797b82e1300d97e75`）、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`0.9902/1.0093/1.0124`、random=`1.0125/1.0169/1.0259`、boundary=`0.9776/1.0008/1.0250`。full和random有约0.9%/1.7%的小负信号，但未形成与覆盖范围一致、明显且可重复的系统性否决；本地性能只作为风险证据。按OJ优先规则预注册一次且仅一次probe：这一case13 bit1 alpha/weight-exp复用能否令#112716的case13 `181 μs/57分`产生可归因改善或跨下一显示档。不得据此扫描fold lane、broadcast、guard、启用范围或同源码复投。
- **提交身份、OJ终态与control决策**：确认没有非终态提交后，dry-run及实际POST前的工作文件SHA均为`be31a8aae12bddcd47d89983681849634e6da2d5c39da56e8debf0778319eb1f`，只创建 **#112941**。终态后保存raw并运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照和实验快照SHA均一致。#112941 14/14 Accepted / **`65.86`**，case1–14=`3/4/10/23/17/28/226/94/234/40/221/375/183/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/55`。预注册的唯一覆盖目标case13从#112716的`181 μs/57分`回退到`183 μs/56分`，因此明确否定这条exact bit1 lane4/5 alpha/weight-exp fold；其他未覆盖路径的同场变化不归因。不得只改fold lane、broadcast、guard、启用范围或同源码复投；只有score/PV consumer ownership、reference或producer数据流实质改变才能重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp522-case13-output-half-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；当前候选SHA=`dcd669601e9d64521d0c38d74a363b51bcd69a51ac69441b05be84859f95df94`。只替换case13 B1/KV8/L58966、65-split 的最终reducer consumer/output ownership：原`paged_decode_reduce_vec2_kernel`每个`(b,h)`用一个64-lane CTA处理相邻两维，整个launch仅32 CTA；新`paged_decode_reduce_vec1_half_kernel`为每个`(b,h)`发两个完整64-lane CTA，分别唯一拥有输出维度`0..63`或`64..127`，因此grid为64 CTA。packed FP16 `(m,l)` metadata、FP32 accumulator partial ABI、global-max/LSE 数学、一个reducer launch、producer、split、tail与所有其他case均不变；只重复小的metadata/weight归约，不重复任何accumulator global read或BF16 output write。这是全局partial consumer/output ownership与block并发的改变，不是已关闭的case13 readlane/native-STG/final-wave merge或仅调reducer线程数。
- **资源与正确性门禁**：`-resource-usage`中实际新reducer `<BASE2=true, SEPARATE_TAIL=false, FUSE_TAIL_IN_LAST_SPLIT=true>`为`40 MTreg / 32 STreg / 0 B shared / 0 B stack / 8 waves`，control case13 vec2 reducer为`38/36/0/0/8`；无spill、无驻留回退。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一fresh candidate的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case13在同一进程通过`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`，覆盖64→65 live-split、尾页、合法padding page trap以及`full→short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9929/0.9972/1.0003`、random=`0.9961/1.0015/1.0055`、boundary=`0.9734/0.9969/1.0722`。随机长度约`+0.15%`负信号处于噪声且没有三分布一致、明显、可重复的系统性回退；本地性能只记录为风险证据。按OJ优先规则预注册一次且仅一次probe：在真实OJ case13长度分布下，这个64-CTA output-half partial consumer/output ownership能否让#112716的`181 μs/57分`产生可归因改善或跨下一显示档；不得由此扫描half划分、grid、metadata布局或同源码复投。
- **提交身份、OJ终态与control决策**：确认队列为空、dry-run后和实际POST前两次SHA均为`dcd669601e9d64521d0c38d74a363b51bcd69a51ac69441b05be84859f95df94`后只创建 **#112972**。终态后保存raw并运行`tools/archive_cuda_submissions.py`；raw内嵌源码、不可变提交快照与提交前工作文件SHA完全一致。#112972 14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/225/93/234/40/223/373/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一目标case13保持#112716的`181 μs/57分`，没有display gain；case7/12/14等未覆盖路径的同场变化不归因，aggregate也低于control。关闭这个exact 64-CTA output-half partial consumer/output ownership；不得扫描half划分、grid、metadata布局或同源码复投，只有全局partial consumer/output ownership、producer/reducer数据流或多请求并发出现实质新前提才可重开。工作文件恢复#112716，当前队列为空。

### exp523-case13-head-major-packed-metadata  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_headmajor_metadata_exp523.cpp`，候选/工作文件 SHA=`d073ec5d59d4024b25aa90d4bd0e5679079dfa51afcfb06ebbc984d2d6476773`。仅对case13 B1/KV8/L58966的65-split packed FP16 `(m,l)` metadata改变 global producer/reducer layout：producer按`[head][split]`写入，64-lane vec2 reducer按同一布局读取；FP32 `partial_acc` 保持原`[split][head][dim]`布局。这样 reducer 的lanes`0..63`首批metadata load从相隔128 B变为连续256 B。QK/PV、K/V loader、split65、z8 tree、partial_acc、LSE数学、reducer CTA/output ownership和其他shape均不变；这不是#112972已关闭的output-half grid/consumer变体。
- **资源、correctness与A/B**：`-resource-usage`中case13 producer `<true,true,false,true>`=`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`，与control `<true,true,false,false>`相同；head-major vec2 reducer `<true,false,true,false,true>`=`38/39/0/0/8`，也与control相同。`test_kernel_logic.py`及同一candidate binary的C500 full/boundary/random（seed=`20260809`）均14/14、100% tolerance match、finite；case13同进程`58966→1,2,15,16,17,911,912,913,1823,1824,1825,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖tail、64→65 live-split、padding trap与workspace复用。相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9928/1.0008/1.0036`、random=`0.9930/1.0008/1.0060`、boundary=`0.9624/0.9865/1.0216`；无覆盖一致、明显且可重复的系统性回退。
- **预注册 OJ 问题**：队列确认为空且完成SHA双核验后，只提交该SHA一次，检验case13 reducer的head-major packed-metadata producer/consumer layout能否使 #112716 的`181 μs/57分`获得可归因改善或跨下一显示档；不得据此扫描metadata stride、layout拼写、grid或同源码复投。
- **提交身份、OJ终态与control决策**：确认没有非终态提交后，dry-run和实际POST前的工作文件SHA均为`d073ec5d59d4024b25aa90d4bd0e5679079dfa51afcfb06ebbc984d2d6476773`，只创建 **#113000**。终态后保存raw并运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照、实验快照与提交前SHA完全一致。#113000 14/14 Accepted / **`65.93`**，case1–14=`3/4/10/23/17/28/226/93/234/40/222/373/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case13保持#112716的`181 μs/57分`，没有display gain；case7/11/12/14等未覆盖路径的同场变化不归因，aggregate低于control。因此关闭这个 exact head-major packed-metadata producer/reducer layout；不得扫描metadata stride、layout拼写、grid或同源码复投，只有metadata格式、partial/producer-reducer ownership或全局数据流实质改变才能重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp524-case13-intrawave-first-merge-tree  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_intrawave_first_tree_exp524.cpp`，工作文件与候选SHA均为`8c9138106add71521279a20fe575968a75a8011336ed6834370768428dc3626f`。只给case13 B1/KV8/L58966、65-split 的z8 producer启用`INTRAWAVE_FIRST_TREE`：每个物理64-lane wave先合并其相邻的`z0/z1`、`z2/z3`、`z4/z5`、`z6/z7`，随后仅让`z4/z6`经第一阶段shared state、`z2`经第二阶段shared state、最终由`z0`完成。故从control的三次CTA barrier、七组shared producer/consumer边改为两次barrier、三组跨wave shared边；QK/PV、K/V loader、split65、partial ABI、LSE、output/reducer与其他case保持不变。这不是exp519只将最后`z1→z0`边替换为raw lane^32 handoff，而是整棵merge tree及shared-state流量的changed precondition。
- **资源与fresh correctness门禁**：实际case13特化为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control同档、无spill。重新构建同一SHA后，`c500_case_manifest.py`、`test_kernel_logic.py`均14/14；同一candidate二进制的C500 full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。case13同进程精确序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖tail、64→65 live-split、padding-page trap与`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`1.0004/1.0027/1.0042`、random=`0.9999/1.0028/1.0034`、boundary=`1.0003/1.0210/1.0521`；boundary以独立seed=`20260809`、15 rounds复测为`0.9304/1.0064/1.0451`。满长与随机仅约0.3%负信号，boundary两轮高方差且没有形成三分布一致、明显、可重复的系统性回退，因而不构成本地性能否决条件。本地数据仅作为风险证据。按OJ优先规则预注册一次且仅一次probe：这条先wave内、后shared的case13 z8 merge tree能否将#112716的`181 μs/57分`推进到下一显示档或得到可归因改善；不得据此调raw-exchange拼写、pair归属、barrier、shared row或同源码复投。
- **提交身份、OJ终态与control决策**：确认没有非终态提交后，dry-run后与实际POST前两次SHA均为`8c9138106add71521279a20fe575968a75a8011336ed6834370768428dc3626f`，只创建 **#113036**。终态后保存raw并运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照、实验快照和提交前SHA完全一致。#113036 14/14 Accepted / **`65.86`**，case1–14=`3/4/10/23/17/28/227/93/236/40/222/372/182/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/55`。预注册唯一覆盖目标case13从#112716的`181 μs/57分`回退为`182 μs/56分`，直接否定这个exact first-intrawave merge tree；其他case的同场变化不归因，aggregate也低于control。不得仅调raw-exchange拼写、pair归属、barrier、shared row或同源码复投；只有merge tree、跨半waveconsumer ownership、state表示或后端交换能力出现实质新前提才可重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp517-case13-vec2-partial-native-ldg  (INCORRECT / LOCAL REJECTED / NO OJ / CLOSED)

- **父/control、唯一差异与资源意图**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_vec2_partial_native_ldg_exp517.cpp`，SHA=`362d5e3f0a802394ccf43478a0a3feba35b17ccb5d3459a22c18ef7c83d05d51`。只给case13 B1/KV8/L58966的64-thread vec2 reducer改变partial-acc consumer：偶数thread对16-byte对齐的四个FP32发起`__builtin_mxc_ldg_b128`，保留低两个值，奇数thread经同warp shuffle取得高两个值；metadata、LSE、partial ABI、producer、output ownership与其他case不变。编译成功，静态资源候选为`18 MTreg / 36 STreg / 0 B shared / 0 stack / 8 waves`（control reducer `38/39/0/0/8`），但静态降寄存器不能替代数值门禁。
- **真实 C500 数值反证与关闭**：同一fresh binary的case13 full仅`match=0.991943`（max_error=`2.221680e-02`，max_tol_ratio=`1.358`），boundary为100% match；random（seed=`20260809`）却为`match=0.974121`（max_error=`2.990723e-02`，max_tol_ratio=`1.815`，finite），低于perf要求的99%元素容差比例。因此该exact even-lane native-LDG plus odd-lane shuffle partial consumer错误，禁止A/B和OJ；不得只调builtin参数、cast、pairing、shuffle source或对齐表达重试。只有partial格式、producer/consumer ownership或后端内存语义出现实质新前提才可重开。

### exp525-case12-intrawave-first-merge-tree  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_intrawave_first_tree_exp525.cpp`，工作文件与候选 SHA 均为`f6c04e385e4392c581d0869d22d03904c2393b337ef13de45892e2572067ce58`。只给case12 B8/KV8/L32768、40 split 的 `paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>` 启用 `INTRAWAVE_FIRST_TREE`：每个物理64-lane wave先合并相邻 z pair，之后只让 z4/z6 和 z2 经过两阶段 shared state；case13仍走 control 树，QK/PV、K/V loader、split、partial ABI、LSE、reducer/output及其他case保持不变。它与 #113036 / exp524 的B1/65-split case13 probe 不同：本轮只检验 B8、40-split 和其批调度下的独立 tree/producer precondition，不能把 case13 的 OJ 回退机械外推到 case12。
- **资源与正确性门禁**：`-resource-usage` 中实际case12新特化为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / staticMaxWarps=5`，与case12 control特化同档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一fresh candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case12在同一进程通过`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`，覆盖尾页、40-split相关长度、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9992/1.0000/1.0014`、random=`0.9995/1.0007/1.0038`、boundary=`0.9959/1.0047/1.0213`；boundary 15-round复测为`0.9970/1.0031/1.1937`。轻微中性/负信号集中在高方差boundary，未构成三分布一致、明显且可重复的系统性本地否决条件。按 OJ 优先规则预注册一次且仅一次 probe：case12 的 B8/40-split z8 intrawave-first merge tree 能否令 #112716 的`375 μs/60分`获得可归因改善或跨下一显示档；不得据此调 raw-exchange、pair归属、barrier、shared row 或同源码复投。

- **OJ终态与control决策**：#113078 14/14 Accepted / `65.79`，case1–14=`3/4/9/23/17/29/226/93/231/40/222/378/182/141 μs`，分数=`92/90/83/72/73/62/55/54/57/61/52/60/56/54`。唯一覆盖目标case12由#112716的`375 μs/60分`回退为`378 μs/60分`，直接否定这条 exact B8/40-split intrawave-first tree；未覆盖路径的同场变化不归因。终态 raw、逐提交快照、实验快照与提交前工作文件SHA均为`f6c04e385e4392c581d0869d22d03904c2393b337ef13de45892e2572067ce58`，并已运行`tools/archive_cuda_submissions.py`。关闭此路线；不得调raw exchange、pair归属、barrier、shared row或同源码复投，只有merge tree、跨半waveconsumer ownership、state表示或后端交换能力实质改变才能重开。工作文件随后恢复#112716。

### c500-readlane-wave64-xor32  (FAILED CAPABILITY / CLOSED)

- **问题与产物**：检验官方 `__builtin_mxc_readlane` 是否能在 z8 生产者的精确`dim3(16,2,8)`布局中实现逐lane的`lane^32`跨半wave FP32 exchange，从而构成不同于 raw BSM bpermute 的 backend-exchange precondition。完整源码/driver 已归档为`tests/archive/closed-backend-probes/c500_readlane_wave64_probe.cpp/.py`，SHA分别为`65d374632e93c2abe3ff4eeb87ecd07716c68de34edf7f15e4cd2e7d54dae265`和`999456ac28565621b1c07b5aa6047035f9c3a316bb430b39fecf099f740216db`；二进制SHA为`989c4d41ac88223e30e30d6ab79945a1fd368cfe943d4d2f15dcf63fa57416b0`。
- **资源与真实 C500 反证**：probe为`6 MTreg / 12 STreg / 0 B shared / 0 stack / 8 waves`。四个physical 64-lane wave的lane ID布局均正确为`0..63`，但给每lane传入`source_lane=lane^32`时，每一个wave的64个输出都变为该wave lane32的值（首wave全为`32.25`、其后全为`96.25/160.25/224.25`），相对逐lane期望的最大误差为32。因而readlane的source selector在wave内必须uniform，语义是广播，而不是per-lane gather/XOR。
- **结论**：不能用readlane替换 z8 raw BSM bpermute 的`lane^32` tree edge；这不是一个可提交的production候选，也不得以lane表达、cast、循环或source拼写重试。exp516/518的reducer使用仍不受影响，因为它们每次调用的source lane对整个wave统一；只有硬件/编译器提供不同的per-lane gather语义才可重开。

### exp526-case12-native-bit1-ownership  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control与唯一差异**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；当前工作文件候选 SHA=`af0251225c68fb8dac541775f4f0eabaa2b7ed19a47b862669099423dc526204`。只把case12 B8/KV8/L32768、40-split 的 dispatch 从`paged_decode_case13_kv8_headpair_z8_kernel<true>`改为`<true,true>`，即把全原生 QK/head-token ownership 从 bit2 改为case9/13已验证的 bit1 映射；case7的已接受live-prefix mapping、case12 split/loader/partial/reducer/LSE、所有其他case均保持 #112716。不与已关闭 exp525 tree 叠加。
- **资源与完整正确性门禁**：`-resource-usage`中candidate `<true,true,false>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，control case12 `<true,false,false>`为`82/50/8448/0/5`，无spill或驻留降档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一fresh candidate的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case12同进程序列`1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767,32768`及`32768→1→32768`均通过，覆盖40-split/tail、padding trap与`short→full`/`full→short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9952/0.9969/0.9986`、random=`0.9875/0.9954/0.9977`、boundary=`0.9828/1.0041/1.0092`。boundary约0.4% p50负信号与full/random正向不构成三分布一致、明显且可重复的系统性回退；本地仅作风险证据。预注册一次且仅一次 probe：在真实 OJ 中，这个case12 bit1 ownership能否让#112716的`375 μs/60分`产生可归因改善或跨下一显示档；不得据此调shuffle、owner lane、模板拼写、split或同源码复投。确认队列为空、dry-run后和POST前SHA均为上述候选后，只创建 **#113117**。
- **OJ终态、归档与control决策**：#113117 正常完成14/14 Accepted / **`65.93`**，case1–14=`3/4/9/24/17/28/226/94/232/40/220/371/182/140 μs`，分数=`92/90/83/71/73/63/55/54/57/61/53/60/56/55`。终态后已保存 raw 并运行归档；raw 内嵌源码、逐提交快照与提交前候选SHA均为`af0251225c68fb8dac541775f4f0eabaa2b7ed19a47b862669099423dc526204`。唯一覆盖目标case12由#112716的`375→371 μs`，但显示分仍为60；未修改case12路径的#112775 / exp503 已有相同`371 μs/60分`样本，因此同档时延不足以建立bit1 mapping的源码因果或control收益，aggregate也低于control。关闭这一 exact case12 bit1 ownership；不得调shuffle、owner lane、模板拼写、split或同源码复投，只有QK/PV consumer ownership、thread/dataflow或后端能力实质改变才能重开。工作文件已逐字节恢复#112716，当前队列为空。

### exp527-case13-headmajor-partial-acc  (REJECTED: OJ WRONGANSWER)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_headmajor_partial_acc_exp527.cpp`，工作文件与快照SHA均为`1ba8147621425c46ae405b01550660ca727fe958b53dd0ce88dda3c0cb4fc802`。只给case13 B1/KV8/L58966、65-split 的 z8 producer→vec2 reducer FP32 `partial_acc` 改为`[head][split][dim]`，让每个64-thread reducer CTA按自身消费次序走65个连续的head-local payload；FP16 `(m,l)` metadata、producer QK/PV/loader/z8 tree、partial数量、LSE、reducer geometry、output和其他case维持control。exp523只改变8 KiB metadata的head-major平面并保持1 MiB accumulator split-major；本轮改变主导的FP32 producer/reducer payload ABI，故不受该metadata-only反证覆盖。
- **资源与正确性门禁**：实际case13 producer `<true,true,false,true>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false,false>`同档；candidate vec2 reducer `<true,false,true,false,true>`为`38 MTreg / 28 STreg / 0 B shared / 0 stack / 8 waves`，control `<true,false,true,false,false>`为`38/39/0/0/8`。CPU manifest与`test_kernel_logic.py`均14/14通过；candidate normal/resource binary SHA分别为`fcec6bf2a5f9f9746db3b048aedea9a598777c30ae81d8d77f0ebbbe9045ec23`/`2e5e723abacefe976c4baecd9c5c3d30c0420bdeff58f80200c0ccdcd121737d`。同一候选 C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match；case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全部通过，覆盖65 live-split、tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control（binary SHA=`52ebd4edc7e4f2e037baf6dc7d1c3f0d72c3331b20072f6797b82e1300d97e75`）、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9963/0.9985/1.0016`、random=`0.9982/1.0018/1.0037`、boundary=`0.9962/1.0008/1.0250`。三分布仅有噪声级混合信号，没有与改动覆盖一致、明显且可重复的系统性回退；本地性能仅作风险证据。按 OJ 优先规则预注册一次且仅一次probe：将FP32 partial accumulator改为head-major consumer layout，能否让#112716的case13 `181 μs/57分`获得可归因改善或跨下一显示档；不得据此扫描layout stride、地址表达、template拼写或同源码复投。
- **OJ终态、归档与关闭理由**：#113136 已归档为 **WrongAnswer / `60.07`**；raw内嵌源码、逐提交快照和提交前工作文件SHA均为`1ba8147621425c46ae405b01550660ca727fe958b53dd0ce88dda3c0cb4fc802`。case1–2、4–14均Accepted，case3却报`payload pass=false`并记录约36.9秒失败占位；该case不属于预期覆盖范围，故不能凭这一条SPJ信息虚构具体内部根因。尽管本地全部门禁通过，远端正确性是最终事实：这份完整编译产物不安全，且WrongAnswer不是性能数据。关闭 exact case13 head-major FP32 partial-acc ABI，不扫描index/stride、地址表达或模板拼写，不同源码也不能作为该layout的原样重投；仅在先证明远端失败根因、并改变partial ABI/consumer ownership/后端前提时才可重开。工作文件已逐字节恢复#112716，当前无在途提交。

### exp528-case4-direct-output-native-stg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选已在提交前保存为`solutions/archive/2026-08-15-experiments/cuda_case4_direct_output_native_stg_exp528.cpp`，它与提交前工作文件 SHA 均为`039f432ce7eea0783c52bb9683c3668f1da4ef13f2599aeb753c1137dce4c548`。只在case4（B64/KV8/L64）的`CASE4_DEDICATED`最终direct-output consumer中，将每个`tx`原有四次`__nv_bfloat162`写替换为一次`__builtin_mxc_stg_b128_predicator`：八个已归一化BF16先打包为`uint4`，写入`out + (b*32+h)*128 + tx*8`。每次恰好写16 bytes，head stride为256 bytes、tx stride为16 bytes，因而地址16-byte对齐；QK、online softmax、K/V loader、split、z-state、reducer及其余case均保持control。这与exp515的FP32 partial producer→reducer native STG不同：本轮是最终BF16 output consumer，不改变workspace ABI或producer/reducer所有权。
- **静态后端与资源门禁**：normal/resource binary SHA 分别为`99613945799af68179ef7952b3a41db38b9dc142c3d908dd8f2bc95f5cc9fe1a`/`8c752e005f02c8bc1d7df166a488eff9a324cba581ba70eeea7ec40378524e44`。以`mxcc -emit-llvm -S`重编译后，candidate case4实际`paged_decode_token_parallel_kernel<8,4,...,CASE4_DEDICATED=true>`含一处真实`llvm.mxc.stg.predicator.v4i32`，fresh #112716 control为零；不是普通BF16 store的源码同义改写。`-resource-usage`中这一case4特化与fresh control均为`74 MTreg / 44 STreg / 8320 B shared / 0 B stack / staticMaxWarps=6`，无spill或驻留降档。
- **数值、边界与复用门禁**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14。相同candidate二进制的C500 full、boundary、random（seed=`20260809`）也均14/14、finite、100% tolerance match。case4同进程精确序列`64→1,2,15,16,17,63→64`逐项通过，覆盖full direct path、generic/tail切换、合法padding-page trap和`full→short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case4 candidate/control p10/p50/p90为full=`0.9748/1.0025/1.0435`、random=`0.9882/0.9962/1.0084`、boundary=`0.9991/1.0081/1.0318`。这是噪声级混合信号，不构成与改动覆盖范围一致、明显且可重复的系统性本地性能否决。本地性能仅作风险记录；按OJ优先规则预注册一次且仅一次probe：真实 OJ case4 中，native 128-bit最终BF16 store能否让 #112716 的`22 μs/73分`得到可归因改善或跨下一显示档。不得据此调整builtin参数、BF16 packing、地址表达、启用范围或同源码复投。
- **OJ终态、归档与关闭理由**：#113157 已终态为 **14/14 Accepted / `65.86`**，case1–14=`3/4/9/23/17/28/224/93/237/40/222/370/182/141 μs`、分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case4从#112716的`22 μs/73分`回退到`23 μs/72分`，因此OJ直接否定该exact final-output native-STG hypothesis；case7/11/12等未覆盖路径的同场变化不归因，aggregate低于control。`results/raw/cuda_113157_raw.json`、逐提交快照和实验快照均与提交前SHA一致，随后已运行`tools/archive_cuda_submissions.py`。关闭这条exact final-BF16 native-STG consumer，不调builtin参数、BF16 packing、地址表达、启用范围或同源码复投；只有最终consumer ownership、输出格式或后端store能力实质改变才可重开。工作文件已逐字节恢复#112716，当前无在途提交。

### exp529-case12-paired-token-bsm-single-producer  (STATIC RESOURCE GATE FAILED / NO C500 OR OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从#112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_paired_token_bsm_single_producer_exp529.cpp`，SHA=`d7c02e9d554cde3e6b6693b4c60b4a49bec3272fbb4e3ce08031eebc2eb7c658`。它尝试消除 exp510 的第二个 producer launch：同一 case12 producer 内由容量行走 paired token-BSM、短行继续走同步路径，期望保留 split40/z8 ownership、partial ABI、vec2 reducer和其他case不变。
- **静态门禁与结论**：`log/cuda_case12_paired_token_bsm_single_producer_exp529_resource.log` 的实际case12特化为`88 MTreg / 64 STreg / 8448 B shared / 0 stack / 5 waves`，超过#112716同一路径的`82/50/8448/0/5`硬上限；没有以split、reducer或launch补偿，也未运行C500 correctness、A/B或OJ。关闭这个 exact 容量行-BSM/短行同步的单-kernel producer分流；不得以容量阈值、行分类、第二producer的去留、wait拼写或同一两路数据流重试。只有实质改变 loader/consumer ownership、BSM后端能力或多请求流水深度时才能重新提出。

### exp530-case12-paired-token-bsm-all-rows  (C500 INCORRECT / NO OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从#112716分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_paired_token_bsm_all_rows_exp530.cpp`，SHA=`d25ab7f81aa9901d691051947486aeab7e9d643b1927e6124b4e152859fe95cf`。它放弃 exp529 的行分流，令case12所有行使用同一 token-BSM page-pair 流：K/V token只在相邻两页内存活，奇页前退休该pair的两个token，禁止token跨loop backedge、tail路径或z-state scratch复用。这是对 exp505–510 跨循环token、tail修补和双producer分流的更强生命周期前提，而非只改wait拼写。
- **后端/资源和正确性反证**：`build/cuda_case12_paired_token_bsm_all_rows_exp530.ll` 含真实`llvm.mxc.ldg.predicator.bsm.v4i32`、`llvm.mxc.arrive(64)`和`llvm.mxc.barrier.inst()`；资源日志为`74 MTreg / 52 STreg / 8448 B shared / 0 stack / 6 waves`，没有stack且未降驻留。CPU manifest/logic通过，C500 full中其余13/14个case通过；但case12满容量输出NaN。case12精确长度`1/2/15`通过，**从16开始**（含`16/17/32`、split边界和`32768`）全部NaN，故这是完整页路径的数值反证，而不是长case参考被Killed或单个tail错误。
- **结论**：即使把两个BSM token限制在self-contained page pair内，也不能使当前case12 z8完整页的后端/生命周期契约正确；因此不跑A/B、不提交OJ。关闭当前KV8 case12 token-BSM族的跨循环token、tail修补、容量/短行双producer以及pair内退休token变体。只有K/V consumer ownership、独立加载后端或多请求深度出现实质新前提，且先通过新的单shape capability/correctness门禁，才可重开。

### exp531-case12-bit1-early-sync-next-k  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一假设与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_bit1_early_k_exp531.cpp`，提交前工作文件与快照 SHA 均为`83d3eccc1bb47584ce7303c0e2a78b5041a6f0dc134db7ee250079419e7b3c04`。唯一可证伪假设是：case12 B8/KV8/40-split 的 bit1 QK/token ownership在当前页 QK 后已经消费本 wave 的 K row，故可立即把同线程的下一页 K 同步写回已死的`s_k`，不再让4个 K `uint32`跨当前页 PV 存活；下一页 V 仍完全保留 control 的寄存器 lookahead 与 PV 后写回。只有case12 dispatch 改为`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`；case7 live-prefix、case9/13、split、z8 tree、partial/reducer ABI、tail和其余路径不变。它不是已关闭的 token-BSM 族：没有异步 token、跨循环等待或K/V双缓冲角色交换。
- **资源与数值门禁**：`log/cuda_case12_bit1_early_k_exp531_resource.log`中实际case12特化为`78 MTreg / 48 STreg / 8448 B shared / 0 stack / 6 waves`，优于#112716 case12 control的`82/50/8448/0/5`，无spill。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一C500候选的full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全部通过，覆盖page/tail、40-split边界、合法padding page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为case12 full=`1.0164/1.0178/1.0200`、random=`1.0158/1.0180/1.0214`、boundary=`0.9130/0.9179/0.9214`。长分布约1.8%回退而boundary约8.2%加速，属于分布相关的混合信号，不是三分布一致、明显且可重复的系统性回退；如实记录为风险证据，不把本地性能作为提交否决。按OJ优先规则预注册一次且仅一次 probe：这个提前同步 next-K 数据流能否在真实 OJ case12 相对#112716的`375 μs/60分`得到可归因改善或跨下一显示档；不得据此扫描bit1 owner、store时点、K/V load表达、split或同源码复投。
- **OJ终态与关闭理由**：#113201 14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/225/94/231/40/223/382/181/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/59/57/54`。唯一覆盖目标case12从#112716的`375 μs/60分`退到`382 μs/59分`，直接否定这个 exact bit1+early-sync-next-K state flow；其他case的同场变化不归因。raw内嵌源码、逐提交快照、实验快照与提交前SHA均为`83d3eccc1bb47584ce7303c0e2a78b5041a6f0dc134db7ee250079419e7b3c04`，随后已归档。不得调bit1 owner、K写回时点、K/V load表达、split或同源码复投；只有QK/PV consumer ownership、thread dataflow或后端能力实质改变才能重开。工作文件已恢复#112716。

### exp533-case12-twohead-fullwave-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从#112716分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_twohead_reducer_exp533.cpp`，SHA=`2f10cf5be31e82acbf568d0ed5e70124492cc6ce258207326c25d4b6dfe9ff43`。只给case12 B8/KV8/L32768、40-split 的最终reducer改变consumer ownership：一个64-thread完整物理wave同时拥有同一batch的两个相邻query head，而每个lane仍为每个head拥有连续两个FP32维度；producer与`[split][batch][head][dim]` partial ABI、metadata/LSE、split、z8 QK/PV/loader、输出格式和其他case均保持control。reducer grid由`8*32=256`降至`8*16=128` CTA，两个head的partial读取不重复。
- **资源与数值门禁**：`log/cuda_case12_twohead_reducer_exp533_resource.log`中实际新reducer为`40 MTreg / 42 STreg / 0 static shared / 0 stack / 8 waves`，control vec2为`38/39/0/0/8`；动态shared为`(4*40+4)*4=656 B`，无spill或驻留退化。C500 full、boundary、random均14/14、finite、100% tolerance match；case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`也全通过，覆盖split/tail、padding trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`0.9985/1.0038/1.0042`、random=`1.0028/1.0041/1.0064`、boundary=`1.0045/1.0101/1.0194`；boundary强复测（21 rounds × 100）=`1.0072/1.0113/1.0159`。三分布均为约0.4–1.1%的轻微负向，记录为风险，不构成“明显且可重复的系统性回退”这一性能否决门槛；它仍具备独立的full-wave two-head consumer ownership和完整数值资源门禁。按OJ优先规则预注册一次且仅一次probe：该reducer ownership能否在真实OJ case12相对#112716的`375 μs/60分`产生可归因改善或跨下一显示档；不得据此扫描head pair、grid、shared布局、metadata或同源码复投。
- **OJ终态与关闭理由**：#113237 14/14 Accepted / `65.79`，case1–14=`3/4/10/23/17/28/225/93/233/40/222/374/182/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case12从#112716的`375→374 μs`，但仍为60分；同档一微秒变化没有兑现预注册的display收益，aggregate也低于control，因此不建立可打榜的源码因果或替换control。raw内嵌源码、逐提交快照、实验快照与提交前SHA均为`2f10cf5be31e82acbf568d0ed5e70124492cc6ce258207326c25d4b6dfe9ff43`，已归档。关闭这个exact two-head/full-wave reducer ownership；不得扫描head pair、CTA grid、shared布局、metadata或同源码复投。只有partial consumer ownership、producer/reducer数据流或后端能力实质改变才可重开；工作文件已恢复#112716。

### exp532-case12-batchlocal-producer-linearization  (CORRECT / LOCAL REJECTED / NO OJ)

- **父/control、唯一差异与 changed precondition**：从 #112716 分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_batchlocal_launch_exp532.cpp`，SHA=`c1224933f7f0b7fddb8403b4e37083d56ff473dae44b6d08de68525229b7e67a`。只给case12 B8/KV8/40-split 的z8 producer把物理 grid 从`(batch*8, 40)`改为`(8, batch*40)`，使CTA线性顺序由`[split][batch][kv_head]`变成`[batch][split][kv_head]`；CTA总数仍为2560，partial ABI、page owner、split、reducer、QK/PV、K/V loader和其他case均保持control。`blockIdx.y`以`__umulhi(linear, 0xCCCCCCCD) >> 5`解出`b=floor(linear/40)`，并以余数确定split。
- **静态与正确性门禁**：初版的直接`linear / 40`在设备IR留下`udiv i32`, 已保留为`log/cuda_case12_batchlocal_launch_exp532_udiv_v1_resource.log`且不进入C500；最终magic映射的目标IR为`mul 3435973837`加`lshr`，没有该候选的device `udiv`。`log/cuda_case12_batchlocal_launch_exp532_resource.log`中最终case12特化为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，与control同档。其C500 full、boundary、random均14/14、finite、100% tolerance match；case12同进程`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`也全通过，覆盖padding trap、page/split/tail边界及workspace复用。
- **A/B 与关闭理由**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`1.0242/1.0291/1.0317`、random=`0.9993/1.0011/1.0052`、boundary=`1.0278/1.0363/1.0438`。full与boundary均为约3%且窄分位一致的回退，random中性，构成与该batch-local launch重排覆盖范围一致、明显且可重复的系统性本地负信号；因此不具备OJ probe资格。关闭这条 exact case12 `[batch][split][kv_head]` physical producer linearization；不得改magic常数、二维维度表达、blockIdx解码拼写或同一CTA顺序重投。只有CTA consumer locality、跨CTA数据流或后端调度前提实质改变才能重开。

### exp534-case13-one-head-two-wave-split-tiled-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；候选工作文件 SHA=`7afd37821213ffff7ec42082b6bfa3c93d9481d264664d443d9b83d619307b74`。只给case13 B1/KV8/L58966、65-split 的最终 reducer 改为单个`(b,h)` CTA内的128-thread/two-physical-wave split-tiled ownership：wave0消费`[0,mid)`、wave1消费`[mid,live_splits)`（`mid=(live_splits+1)>>1`），各自为完整128维累积FP32 partial；wave1经CTA-local FP32 shared payload交给wave0唯一写BF16 output。producer、z8 QK/PV/loader/tree、split65、`[split][batch][head][dim]` partial ABI、packed FP16 `(m,l)`、reducer grid=32 CTA及其他case保持#112716。它既不是exp522的output-half CTA，也不是exp513的两kernel global round-trip。
- **资源与数值门禁**：最终资源 binary SHA=`55e50dd1a0e34a89cde0826bd0c0a9bef7e2ba14b8103014ce3acbba05ebfbb5`；实际新reducer为`46 MTreg / 40 STreg / 0 static shared / 0 stack / 8 waves`，launch动态shared为`(2*65+8+128)*4=1064 B`，相对control vec2=`38/36/0/0/8`没有spill或驻留降档。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14；同一C500 candidate的full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case13同一进程精确序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖tail、57-page/65-live-split边界、合法padding page trap和`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control（warmup=5、20 iterations、9 rounds），case13 candidate/control p10/p50/p90为full=`0.9924/0.9956/0.9987`、random=`0.9954/1.0009/1.0060`、boundary=`0.9842/1.0049/1.0319`。full小幅正向，random/boundary为噪声级混合信号，不构成覆盖一致、明显且可重复的系统性本地回退；本地性能仅作风险证据。按OJ优先规则预注册一次且仅一次probe：这个one-head/two-wave split-tiled partial consumer能否在真实OJ case13相对#112716的`181 μs/57分`产生可归因改善或跨下一显示档。不得据此扫描wave数、split分界、shared布局、metadata、grid或同源码复投；终态后归档raw与逐提交源码，再决定是否切换control。
- **OJ终态与关闭理由**：#113299 14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/233/40/223/371/180/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case13从#112716的`181→180 μs`，但仍为57分；同档一微秒没有兑现预注册的display收益，aggregate也低于control，因此不建立可打榜的源码因果或替换control。`results/raw/cuda_113299_raw.json`、逐提交快照、实验快照与提交前工作文件SHA均为`7afd37821213ffff7ec42082b6bfa3c93d9481d264664d443d9b83d619307b74`，已归档。关闭这个 exact one-head/two-wave split-tiled reducer ownership；不得调wave数、split分界、shared布局、metadata、grid或同源码复投。只有partial consumer ownership、producer/reducer数据流或后端能力实质改变才可重开；工作文件已恢复#112716，当前队列为空。

### exp535-case13-live-prefix-magic  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；候选工作文件 SHA=`c9b93c9ba9e20658b1d4dc7060235b16604350fba5d419ef84f38b43eb1fd9d5`。只给case13（B1/KV8/L58966、65 split）的z8 producer启用实际长度 live-prefix mapping：满容量严格保持control的`57×64+37`页区间；短真实长度只在control reducer已读取的`ceil(full_pages/57)`个live split前缀内，以`ceil(full_pages/live_splits)`均分full pages，tail仍只由最后一个live split处理。该映射用`__umulhi`和65项常量倒数表实现，不改split数、partial ABI/reducer、z8 QK/PV/loader/tree、尾页数学或其他case。它是case13 B1/65-slot/57-page前提下的独立无除法实际长度调度，不能由case9/12的已关闭exact mapping替代，也不是exp448的每CTA动态除法。
- **静态、资源与正确性门禁**：Python已穷举`full_pages=0..3685`，验证候选full-page区间连续、无重叠/漏页、inactive split不写partial，且满容量映射与control逐区间一致。fresh LLVM中实际`<true,true,false,true>` case13特化含64-bit multiply-high/`lshr 32`及常量表读，**无候选`udiv`**；只允许控制路径原有的`seqlen/16`。fresh `-resource-usage`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false>`相同。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一C500候选的full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case13又在同进程覆盖`1,2,15,16,17`、每个live-prefix `n=1..64`的`n×57×16-1/0/+1`、`58965/58966`，并覆盖padding-page trap与`full→short→full`/`short→full`复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control（warmup=5、20 iterations、9 rounds），case13 candidate/control p10/p50/p90为full=`1.0007/1.0037/1.0370`、random=`0.9924/0.9979/1.0048`、boundary=`0.9789/0.9944/1.0099`。full是噪声级风险，random/boundary小幅正向；没有与改动覆盖一致、明显且可重复的系统性回退。按OJ优先规则预注册一次且仅一次probe：在真实OJ实际`cache_seqlens`分布下，该无device除法的case13 live-prefix均衡能否相对#112716的`181 μs/57分`产生可归因改善或跨下一显示档；不得据此扫描magic表、bucket、映射时点、split或同源码复投。提交前再次核验队列为空、dry-run和实际POST前SHA一致；终态后归档raw与逐提交源码，再决定是否切换control。
- **OJ终态与关闭理由**：#113343 14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/226/94/234/40/222/377/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case13相对#112716仍为`181 μs/57分`，没有兑现预注册的display收益，aggregate也低于control，故不建立可打榜的源码因果或替换control。`results/raw/cuda_113343_raw.json`、逐提交快照、实验快照与提交前工作文件SHA均为`c9b93c9ba9e20658b1d4dc7060235b16604350fba5d419ef84f38b43eb1fd9d5`，已归档。关闭这个 exact case13 live-prefix reciprocal/magic mapping；不得扫描table、bucket、映射时点、split或同源码复投。只有producer实际长度调度或数据流实质改变才可重开；工作文件已恢复#112716，当前队列为空。

### exp536-case10-twohead-registerml-reducer  (CORRECT / LOCAL REJECTED / NO OJ / CLOSED)

- **父/control与唯一 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case10_twohead_registerml_reducer_exp536.cpp`，当前 SHA=`0ae703074c8cbc2a1d814c42b17e42991e19f4045f0ceb4a40e5cc15dd78712c`。只给case10（B1/KV4/L8192、128 split）的最终reducer让一个64-thread完整物理wave同时消费相邻两个query head：grid由32个one-head CTA降为16个two-head CTA；每lane仍为每头持有连续两个FP32输出维度，并保留exp467已经接受的两个packed FP16 `(m,l)` per-head/per-lane寄存器生命周期。producer、split128/四页、`[split][batch][head][dim]` FP32 partial ABI、fused-tail live count、LSE数学和其他case不变。
- **旧反证与预注册资源门禁**：exp54的case14 two-head reducer使用257 split、128线程和normalized-BF16 partial；exp533的case12 two-head reducer使用40 split且把metadata经shared物化；两者均不是当前B1/128-slot/register-metadata consumer契约，不能替代本probe。先只编译资源：必须0 B stack/spill、保持8 static waves，且动态shared严格为`(2*128+4)*4=1040 B`；任一条件失败即关闭，不运行C500、A/B或OJ。即使资源通过，仍须依次完成完整correctness、case10精确长度/复用、full/random/boundary交错A/B，才可预注册一次OJ probe；不得把head pair、grid、shared或metadata写法变成参数扫描。
- **资源结果**：`tools/build_local_maca.sh ... -resource-usage` 已成功编译；目标`paged_decode_reduce_twohead_vec2_kernel<BASE2=true,SEPARATE_TAIL=false,FUSE_TAIL=true,REGISTER_PACKED_ML=true>`为`42 MTreg / 42 STreg / 0 B static shared / 0 B stack / 8 static waves`。相对case10 control reducer的`38/36/0/0/8`增加寄存器但不降resident wave，动态shared按dispatch为1040 B；通过预注册资源门禁。编译器仅报告既有`__launch_bounds__(...,6)` MACA warning，和本64-thread reducer无关。
- **数值门禁**：normal binary SHA=`7d894bbb428f98ff77a2b909524909c53f6b22a2134a95a2c5a3ca92c753ecca`，resource binary SHA=`43b580408cb909caf3bda4f79c280abb7515086668812bde13d91dafda55a418`。`test_kernel_logic.py`为14/14；同一C500 candidate的14-case full、boundary、random（seed=`20260809`）也均14/14、finite且满足容差。case10在同进程序列`8192→1,2,15,16,17,63,64,65,127,128,129,191,192,193,255,256,257,8191→8192`均100% match，覆盖页、四页split、tail、padding-page trap与`full→short→full` workspace复用。
- **交错 A/B 与关闭理由**：相对fresh #112716 control（warmup=5、20 iterations、9 rounds），case10 candidate/control p10/p50/p90为full=`1.1287/1.1558/1.1700`、random=`1.0515/1.0656/1.1029`、boundary=`0.9654/1.0066/1.0238`。full稳定慢约15.6%、random慢约6.6%，而boundary只有噪声级混合；前两种主分布均有窄分位的明显回退，直接否定“以两头共享一个64-lane CTA减少B1 reducer调度”的假设。关闭这个 exact case10 two-head/register-packed-metadata consumer ownership；不得调整head pair、CTA grid、shared布局或metadata source spelling重试。未进行 OJ probe，工作文件仍与#112716 SHA一致。

### exp537-case10-twowave-split-registerml-reducer  (CORRECT / LOCAL REJECTED / NO OJ / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case10_twowave_split_registerml_reducer_exp537.cpp`，SHA=`9d4a7e05116f94cb9623c9395f816634a45c615f962b85f219e8fcb7ae85af9e`。只给case10（B1/KV4/L8192、128 split）的最终reducer改为一个head/128-thread CTA内的two-physical-wave split-tiled consumer：wave0/1各消费`[0,64)`/`[64,live_splits)`，各保留一个packed FP16 `(m,l)` metadata于寄存器、以wave-local FP32 reference计算权重和partial accumulator，最后以FP32 LSE尺度合并；wave1经CTA-local FP32 payload交给wave0唯一写BF16 output。producer、128 split/four pages、fused-tail live count、split-major FP32 partial ABI、exp467 register-packed metadata契约和其他case均保持control。它不是exp536的two-head CTA，也不是exp534的case13 65-slot/shared-metadata layout：唯一重开前提是case10的128-slot reducer允许两条wave各自把128次serial split accumulation缩至64次，且不重复global partial读取。
- **资源与数值门禁**：`-resource-usage` 的新reducer为`20 MTreg / 30 STreg / 0 B static shared / 0 stack / 8 static waves`；动态shared为`(128 + 8 + 128) * 4 = 1056 B`，无spill且驻留档不低于case10 control vec2的`38/36/0/0/8`。`test_kernel_logic.py`为14/14；同一C500 binary的14-case full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case10同进程序列`8192→1,2,15,16,17,63,64,65,127,128,129,191,192,193,255,256,257,8191→8192`全通过，覆盖tail、split/page边界、合法padding page trap与`full→short→full` workspace复用。
- **交错 A/B 与关闭理由**：相对fresh #112716 control（warmup=5、20 iterations、9 rounds），case10 candidate/control p10/p50/p90为full=`1.1782/1.2010/1.2185`、random=`1.0129/1.2439/1.2652`、boundary=`1.0025/1.0153/1.0898`。full稳定慢约20.1%、random中位慢约24.4%，boundary也无正向；two-wave CTA-local merge/barrier/shared handoff超过缩短split循环带来的收益。该回退与新consumer覆盖范围一致且在两个主分布可重复，故不具备OJ probe资格。关闭这个 exact case10 one-head/two-wave split-tiled/register-packed-metadata reducer ownership；不得调整wave分界、CTA grid、shared payload、LSE合并或metadata source spelling重试。工作文件随后恢复#112716。

### exp538-case13-shared-tree-barrier  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_shared_tree_barrier_exp538.cpp`，候选 SHA=`b2fb75aca0c317fc78cb3c48e0908d4a29509141b89025d66ae1374453101d90`。只给case13 B1/KV8/L58966、65-split 的`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`把三层 z8 `(m,l,acc)` merge tree 的五个 CTA edge 从`__syncthreads()`改为`__syncthreadshared()`；它们只发布/消费` s_acc/s_md`的CTA-local shared payload。page-loop、tail K/V-reuse barrier、QK/PV、loader、split、partial ABI、reducer和其他shape保持control。旧exp59只测KV4/z4的四个shared-only边且局部中性；本轮z8、八分区、五边tree是不同拓扑，但不是barrier拼写扫描。
- **静态资源与后端门禁**：fresh `-resource-usage` 的实际case13新特化为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false>`相同。candidate LLVM target function精确有5个`llvm.mxc.barrier.shared()`，control对应位置为5个`llvm.mxc.barrier()`；page-loop既有warp/CTA barrier未改变，证明不是源码同义改写或无效能力调用。
- **数值、边界与复用门禁**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一candidate C500 full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。case13同进程`58966→1,2,15,16,17,911,912,913,1823,1824,1825,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖极短页/尾页、57-page/65-live-split边界、合法padding page trap和`full→short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9969/1.0005/1.0068`、random=`0.9946/1.0009/1.0104`、boundary=`0.9866/0.9920/1.0081`。三分布没有与该五个shared-only tree edge覆盖一致、明显且可重复的系统性回退；本地性能仅作风险标签。按OJ优先规则预注册一次且仅一次probe：真实OJ中共享内存专用fence能否使case13相对#112716的`181 μs/57分`获得可归因改善或跨下一显示档。不得由此扫描barrier位置、树拓扑、shared row、模板参数或同源码复投。
- **OJ终态、归档与关闭理由**：#113438 14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/226/93/232/40/224/372/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case13相对#112716保持`181 μs/57分`，没有可归因display收益，aggregate也低于control；因此关闭这个 exact case13 all-five shared-only-tree-barrier contract。`results/raw/cuda_113438_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113438.cpp`、实验快照与提交前工作文件SHA均为`b2fb75aca0c317fc78cb3c48e0908d4a29509141b89025d66ae1374453101d90`。不得扫描barrier位置、tree row、模板拼写或同源码复投；只有同步范围、state/consumer ownership、merge tree或后端能力出现实质新前提时才可重开。工作文件已恢复#112716，当前队列为空。

### exp539-case13-wave-local-final-tree-sync  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case13_wave_final_tree_sync_exp539.cpp`，SHA=`c0c2459f3ed73646aad4ef4c56705dbdfc01f5f6abb27631f91d5402651405c6`。只给case13 B1/KV8/L58966、65-split 的 z8 producer增加第四个模板参数`WAVE_LOCAL_FINAL_TREE_SYNC=true`：在三阶段 state tree 的后两条依赖边，`tz=0/1`分别完成stage-2消费、`tz=1`发布最后peer state、`tz=0`消费该state；一个physical C500 wave恰好包含相邻的`tz=0/1`（每个z为`16×2=32`线程，wave为64线程），且`tz=2..7`在stage-2后不再被共享状态消费。因此只把这两次无条件CTA barrier改为每个wave的`__syncwarp()`；第一、二、三条跨wave tree edge、tail/page barrier、QK/PV、loader、split、partial ABI/reducer和其他shape保持control。这是按真实依赖图缩小同步范围，不是exp538已关闭的`__syncthreadshared()`拼写或barrier位置扫描。
- **资源与数值门禁**：`tools/build_local_maca.sh ... -resource-usage`的实际case13新实例`<true,true,false,true>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false,false>`同档。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一C500 candidate二进制的full、boundary、random（seed=`20260809`）也均14/14、finite、100% tolerance match。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖tail、57-page/65-live-split边界、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9976/1.0003/1.0020`、random=`0.9969/1.0003/1.0016`、boundary=`0.9108/0.9927/1.0057`。三分布总体是噪声级中性、没有覆盖一致且明显可重复的系统性回退；按OJ优先规则，它不是性能否决条件。预注册一次且仅一次 OJ probe：这个缩小后两条state-tree同步范围的真实C500/OJ实现，能否相对#112716的case13 `181 μs/57分`产生可归因改善或跨下一显示档；不得由此调整barrier位置、范围、tree row、模板参数或同源码复投。
- **OJ终态、归档与关闭理由**：#113492 14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/225/94/235/40/222/372/182/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case13从#112716的`181 μs/57分`退至`182 μs/56分`，aggregate低于control；因此关闭这个 exact wave-local-final-tree-sync contract。`results/raw/cuda_113492_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113492.cpp`、实验快照与提交前工作文件SHA均为`c0c2459f3ed73646aad4ef4c56705dbdfc01f5f6abb27631f91d5402651405c6`。不得扫描barrier位置、同步范围、tree row、模板参数或同源码复投；只有同步范围、state/consumer ownership、merge tree或后端能力出现实质新前提时才可重开。工作文件已恢复#112716，当前队列为空。

### exp540-case10-symmetric-finalizer  (RESOURCE GATE REJECTED / NO C500 / NO OJ / CLOSED)

- **父/control与唯一差异**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case10_symmetric_finalizer_exp540.cpp`，SHA=`bcfda8ee5a78ba6e29bb0996e62526399cd958fc07f013b9d3c09b060d391012`。只给case10 B1/KV4/L8192的z4 producer在dispatch追加`SYMMETRIC_FINALIZER=true`，使z0/z1各终结一个head；BF16-MMA QK、split128、packed reducer ABI、loader、partial和其他shape均保持control。
- **资源否决与关闭范围**：control case10约为`80 MTreg / 58 STreg / 8320 B / 0 stack / 6 waves`，候选变为`82/64/8320/0/5`，寄存器/驻留档反向，未满足生产资源门禁。因此不运行C500 correctness、A/B或OJ，关闭这个 exact case10 symmetric-finalizer dispatch；不得以同一case10 finalizer只改源码拼写、launch或reducer补偿重开。只有state/consumer ownership、merge tree或资源前提实质变化时才可再提出。

### exp541-case5-symmetric-finalizer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case5_symmetric_finalizer_exp541.cpp`，提交候选与工作文件SHA均为`d7b36fe96f9ec7d889653f7cd4340a8ae5f2a9a4223e97f83b05f9d5f5ae611e`。只给case5 B16/KV4/L141、5-split 的`paged_decode_case11_headpair_z4_kernel`增加第19个模板参数`SYMMETRIC_FINALIZER=true`，由z0/z1各终结一个head并在已消费的peer row合并state；BSM combined tail、BF16-MMA QK、split-head ownership、K/V loader、FP32 partial、group8 reducer和其他shape均保持control。这是state consumer ownership/merge topology改变，不是exp59的shared-fence拼写或exp540的case10资源条件。
- **资源与数值门禁**：实际case5 control特化为`74 MTreg / 52 STreg / 8320 B shared / 0 stack / 6 waves`，候选为`74/48/8320/0/6`，无spill且不降低驻留档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一C500 candidate二进制full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case5同进程序列`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140→141`全通过，覆盖page/tail、五split边界、padding-page trap和`full→short→full` workspace复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case5 candidate/control p10/p50/p90为full=`0.9686/0.9952/1.0303`、random=`0.9737/0.9873/1.0084`、boundary=`0.9734/0.9914/1.0365`。三个分布均为小幅正向或噪声，没有与覆盖范围一致的系统性回退。预注册一次且仅一次 OJ probe：这个case5对称finalizer能否相对#112716的`17 μs/73分`达到`≤16 μs`并跨下一显示档；不得由此扫描finalizer拼写、barrier、launch、reducer或同源码复投。终态后保存raw和逐提交源码，再决定是否关闭或替换control。
- **OJ终态、归档与关闭理由**：#113538 14/14 Accepted / `66.07`，case1–14=`3/4/9/22/17/28/227/93/235/40/223/371/181/140 μs`。唯一覆盖目标case5仍为`17 μs/73分`，没有兑现预注册的display收益；总分新增一点来自未修改case14的`141→140 μs` timing-tier刷新，不能归因给case5 finalizer。因此结构性control保持#112716。`results/raw/cuda_113538_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113538.cpp`与实验快照均为`d7b36fe96f9ec7d889653f7cd4340a8ae5f2a9a4223e97f83b05f9d5f5ae611e`。关闭这个 exact case5 symmetric-finalizer contract；不得扫描finalizer/store/barrier/launch/reducer拼写或同源码复投，只有state/consumer ownership、merge tree或资源前提出现实质变化时才可重开。

### exp542-case12-row16-vec2-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选为`solutions/archive/2026-08-15-experiments/cuda_case12_row16_vec2_reducer_exp542.cpp`，工作文件与候选SHA=`a7f53bce7c5e3243bd8766e1ee8ef219a08bacf1d10d4d39f987787239aa1bcb`。只给case12 B8/KV8/L32768、40-split 的64-thread `paged_decode_reduce_vec2_kernel`启用第5个模板参数`NATIVE_ROW16_REDUCE=true`：原先两组32-lane XOR metadata reduction改成四个物理16-lane row分别调用既有C500 `native_row16_maxreduce/allreduce`，四个row leader经CTA-local shared合成最终`m/l`。producer、split-major FP32 partial ABI、packedFP16 `(m,l)`、weight buffer、输出每head/vec2 ownership、reducer grid和其他shape保持control。这是物理subgroup/dataflow改变，不是已关闭的readlane metadata、two-head CTA或partial layout路线。
- **资源与后端门禁**：`-resource-usage`的实际新实例`<BASE2=true,SEPARATE_TAIL=false,FUSE_TAIL_IN_LAST_SPLIT=true,REGISTER_PACKED_ML=false,NATIVE_ROW16_REDUCE=true>`为`38 MTreg / 39 STreg / 0 B static shared / 0 stack / 8 waves`，与case12 control vec2 reducer同档。动态shared只从`(2*40+2)*4=328 B`增加为`(2*40+4)*4=336 B`，为四个row leader提供存储。candidate LLVM 的目标实例含真实`llvm.mxc.mov.shfl.i32` row16指令；不是默认32-lane shuffle源码同义改写。
- **数值与边界门禁**：`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一C500 candidate二进制的full、boundary、random（seed=`20260809`）也均14/14、finite、100% tolerance match。case12同进程精确序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全通过，覆盖tail、40-slot live split边界、合法padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control（warmup=5、20 iterations、9 rounds），case12 candidate/control p10/p50/p90为full=`0.9962/0.9989/0.9995`、random=`0.9957/0.9969/0.9982`、boundary=`0.9883/0.9922/0.9974`。三种长度分布没有与覆盖范围一致、明显且可重复的系统性回退。按OJ优先规则预注册一次且仅一次probe：这个真实16-lane row metadata/LSE reducer能否让case12相对#112716的`375 μs/60分`获得可归因改善或跨下一显示档；不得据此扫描row数、shared布局、shuffle mode、grid或同源码复投。终态后保存raw和逐提交源码，再决定是否切换control。
- **OJ终态、归档与关闭理由**：#113566 14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/224/93/237/40/221/376/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case12由#112716的`375→376 μs`，显示分仍60，aggregate亦低于control；因此不能建立可打榜因果或替换control。`results/raw/cuda_113566_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113566.cpp`、实验快照和提交前工作文件SHA均为`a7f53bce7c5e3243bd8766e1ee8ef219a08bacf1d10d4d39f987787239aa1bcb`，已运行`tools/archive_cuda_submissions.py`核验。关闭这个 exact physical-row16 reducer contract；不得扫描row数、shared布局、shuffle mode、grid或同源码复投。只有物理subgroup dataflow、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复#112716。

### probe-permuted-k128b-ordinary-lds  (C500 CORRECT / NO-GO / CLOSED)

- **问题与源码**：独立检验官方 k128B XOR-permuted ordinary shared-memory 地址 `chunk ^ (row & 7)`，是否能改善当前 KV8 四个 16-lane row 同时读取同一 K/V page row 的128-bit LDS consumer。最终 probe 源码 SHA 为 `c500_permuted_smem_probe.cpp=671e7dc3c2eb217799d8fa50de148b8562f86acb2e5e0dc6d6aa6b02fea8ffc1`、driver SHA 为 `c500_permuted_smem_probe.py=d6f39a3777c73d2fa45aa942fb91acf478470927a2f917cba5f20830c2a4ecd7`。两份文件随后归档至 `tests/archive/closed-backend-probes/`。
- **校准与数值结论**：初版把四维 `torch.int32` 输入直接传给 raw-pointer ABI，桥接层的物理分量布局使连续字出现跨 row 假象；改为一维 raw backing storage、同时用 scalar host ingress/egress 后，32/64 active-thread 的 row-major 与 XOR-swizzled 双区域 payload 均逐字一致。probe 仍在 shared 端使用普通对齐128-bit `uint4` load/store，因此该校准没有把待验证 LDS 访问降级为 host-side 假测。
- **完整 C500 时钟门禁**：以 `python3 tests/c500_permuted_smem_probe.py --library build/c500_permuted_smem_probe.so` 的32次、2048轮有效采样为准，32-thread consumer 的 swizzled/row-major p50=`974982/974864=1.0001`（中性），64-thread 为`2023456/1933328=1.0466`（稳定慢约4.7%）；producer p50 分别为`0.9799/1.0581`，没有跨两种活跃布局的一致正向。payload虽正确，但没有性能资格。
- **关闭范围**：不为当前 KV8 K/V shared-page consumer 接入这个 exact k128B XOR ordinary-LDS layout，不扫描 XOR 掩码、数组维度、pointer spelling 或单独偏向某一 full-length 样本，也不提交 OJ。只有 shared-memory 指令、线程/consumer ownership 或真实消费布局出现实质 changed precondition 时，才可重新建立单独 probe。

### exp543-group8-final-native-stg  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选冻结为`solutions/archive/2026-08-15-experiments/cuda_group8_final_native_stg_exp543.cpp`，工作文件和快照 SHA 均为`e221665e6ba0e25206e7d90d978582a3ebf352f8c48f196a6cc2048823dbc382`。只给 group8 最终 reducer 的 case5/6/7/8 dispatch 启用`NATIVE_OUTPUT_STG=true`：每个`tx`在 split/LSE 合并完成后写出连续8个BF16（天然16-byte对齐），由四次`__nv_bfloat162` store 改为一次`__builtin_mxc_stg_b128_predicator`。producer、partial ABI、metadata/LSE、reducer线程/CTA ownership、grid与其他shape保持control。它不同于已关闭 exp528 的case4 producer direct-output：本轮是多split group8 **reducer** 的最终consumer，具有不同的输入状态与输出地址前提。
- **资源与后端门禁**：fresh `-resource-usage` 显示三个实际新增的 group8 特化均为`66 MTreg / 24、25或26 STreg / 0 B shared / 0 stack / 7 waves`，与相应control驻留档一致。candidate LLVM 的`llvm.mxc.stg.predicator.v4i32`文本出现7处、control为0，证明该路径没有退化为普通store源码同义改写。
- **数值、边界与复用门禁**：`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一fresh C500 candidate的full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。受影响case的同进程精确长度序列全部通过：case5=`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140→141`；case6=`362→1,2,15,16,17,47,48,49,95,96,97,143,144,145,191,192,193,239,240,241,287,288,289,335,336,337,361→362`；case7=`2048→1,2,15,16,17,42,43,44,85,86,87,127,128,129,1023,1024,1025,2047→2048`；case8=`4096→1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095→4096`。这覆盖页尾、split边界、padding-page trap以及full→short→full的输出/reducer复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90 为：full（case5–8）=`0.9582/0.9930/1.0062`、`0.9788/0.9941/1.0072`、`0.9952/0.9996/1.0009`、`0.9952/0.9995/1.0010`；random=`0.9535/0.9930/1.0431`、`0.9582/0.9851/1.0242`、`0.9979/1.0000/1.0033`、`0.9990/1.0021/1.0066`；boundary=`0.5699/0.9673/1.0348`、`0.9996/1.0130/1.0354`、`0.9899/1.0023/1.0069`、`0.9695/0.9967/1.0571`。case6 boundary的1.3%中位负信号未在full/random复现，且其余覆盖路径均为中性或轻微正向；没有覆盖一致、明显且可重复的系统性回退。
- **预注册的一次 OJ probe**：唯一问题是这个真实C500 B128 final-store consumer能否让其覆盖的case5/6/7/8相对#112716的`17/28/227/93 μs`取得可归因的**显示档**收益；具体微秒仅作选题线索，OJ display score 才是通过判据。不以未覆盖case的同场波动归因，不扫描builtin参数、packing、地址表达或enable范围，也不对同一源码密集复投；终态后保存raw、提取逐提交源码，再决定接受或关闭这条 exact group8 final-consumer native-STG contract。
- **OJ终态、归档与关闭理由**：#113642 14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/226/94/234/40/222/371/181/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/57/55`。覆盖case5/6保持#112716的`17/28 μs`，case7虽从`227→226 μs`仍为55分（说明一微秒估计不等于显示跨档），case8则由`93→94 μs`、仍54分；因此没有预注册的display收益，aggregate也只与control同分。`results/raw/cuda_113642_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113642.cpp`、实验快照与提交前SHA均为`e221665e6ba0e25206e7d90d978582a3ebf352f8c48f196a6cc2048823dbc382`，并已运行`tools/archive_cuda_submissions.py`核验。关闭这个 exact group8 final-consumer native-STG contract；不得扫描builtin参数、packing、地址表达、enable范围或同源码复投，只有最终consumer ownership、输出格式或后端store能力出现实质新前提才可重开。工作文件已恢复#112716，当前无在途提交。

### exp544-case7-packed-group8-row16-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与完整快照**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选冻结为`solutions/archive/2026-08-15-experiments/cuda_case7_group8_packed_row16_exp544.cpp`，工作文件与快照 SHA 均为`091a204282a6c8deab6b384deaa72b4f58845b4775196948da412a3cf352b895`。唯一改动只在 case7（B64/KV8/L2048）group8 reducer dispatch：保留 packed `(m,l)`、shuffle-weight、fused-tail、producer、partial ABI、CTA/grid 和其他 shape，单独将`paged_decode_reduce_group8_kernel<BASE2,false,true,true,false,true>`的`NATIVE_ROW16_REDUCE`改为`true`。这使每个物理16-lane metadata row用已验证的 native max/sum network，而非原先32-lane shuffle reduction；它不同于已关闭 exp542 的 case12 vec2/40-split reducer，拥有 case7 的 packed metadata 与1–3 live-split group8 consumer 前提。
- **静态资源与后端门禁**：fresh `-resource-usage` 显示 case7 candidate实例为`66 MTreg / 25 STreg / 0 B shared / 0 stack / 7 waves`，与 #112716 的对应实例同档。当前源码生成的 LLVM 中`llvm.mxc.mov.shfl`计数为607、control为599，确认该开关产生实际后端差异，而非源码同义改写。
- **数值、边界与复用门禁**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一 freshly rebuilt C500 candidate的full、boundary、random（seed=`20260809`）也均14/14、finite、100% tolerance match。case7同进程序列`2048→1,2,15,16,17,687,688,689,1375,1376,1377,2047→2048`均通过，覆盖尾页、3个live-split边界、padding-page trap及`full→short→full` workspace复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case7 candidate/control p10/p50/p90为full=`0.9964/0.9983/1.0000`、random=`0.9925/0.9952/1.0039`、boundary=`0.9915/0.9995/1.0021`。三种分布均没有与改动覆盖面一致、明显且可重复的系统性回退；本地数据只作为风险标签。按 OJ 优先规则预注册一次且仅一次 probe：这个 case7 packed group8 physical-row16 metadata/LSE reducer 能否使 #112716 的`227 μs/55分`取得可归因的 display gain。不得据此扫描 row 数、shuffle mode、模板参数、grid 或同源码复投；终态后保存 raw、逐提交源码并据 OJ 目标 case 决定接受或关闭。
- **OJ终态、归档与关闭理由**：#113658 14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/225/94/234/40/223/371/182/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case7从#112716的`227→225 μs`，却保持55分；未覆盖case的同场变化不归因。因此没有预注册的display收益，不能替换control。`results/raw/cuda_113658_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113658.cpp`、实验快照与提交前工作文件SHA均为`091a204282a6c8deab6b384deaa72b4f58845b4775196948da412a3cf352b895`，已运行`tools/archive_cuda_submissions.py`核验。关闭这个 exact case7 packed group8 physical-row16 metadata/LSE reducer contract；不得扫描row数、shuffle mode、模板参数、grid或同源码复投。只有physical-subgroup数据流、packed-metadata consumer ownership或后端能力有实质新前提时才可重开；工作文件已恢复#112716，当前队列为空。

### exp545-case14-packed-row16-reducer  (CORRECT / OJ ACCEPTED / SELECTED CONTROL)

- **父/control、唯一差异与 changed precondition**：从 #112716（SHA=`411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`）分叉；完整候选冻结为`solutions/archive/2026-08-15-experiments/cuda_case14_row16_reducer_exp545.cpp`，工作文件和快照 SHA 均为`6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`。仅给 case14（B1/KV4/L61519、257 split）的128-thread `paged_decode_reduce_kernel<BASE2,false,true,true,true,true>`追加`NATIVE_ROW16_REDUCE=true`：每个物理16-lane row以已有C500 native max/sum network归约自己的 packed `(m,l)`，8个row leader沿既有CTA-local metadata staging由thread0合成全局max/LSE。producer、fixed15 BF16-MMA、normalized BF16 partial、register-packed FP16 metadata、输出每维 ownership、grid和其他shape均保持control。这与已关闭的case14 vec2/two-head reducer、case12 vec2 row16和case7 group8 row16分别具有不同的线程/partial/consumer契约。
- **资源与后端门禁**：fresh `-resource-usage` 的目标candidate实例为`40 MTreg / 28 STreg / 0 B static shared / 0 stack / 8 waves`，control为`40/32/0/0/8`；动态metadata shared 从`(257+4)*4=1044 B`变为`(257+8)*4=1060 B`，无驻留档回退。`mxcc -emit-llvm -S` 的目标candidate特化含8处真实`llvm.mxc.mov.shfl.i32`，control的同一特化为20处`llvm.mxc.bsm.bpermute`，证明物理row路径未退化为原logical-32 shuffle源码同义改写。
- **数值、边界与复用门禁**：`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一C500 candidate二进制full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。case14同进程序列`61519→1,2,15,16,17,239,240,241,3839,3840,3841,61518→61519`逐项通过，覆盖tail、15-page/split256边界、padding-page trap及`full→short→full` workspace复用。
- **交错 A/B 与预注册的一次 OJ 问题**：相对fresh #112716 control、warmup=5、20 iterations、9 rounds，case14 candidate/control p10/p50/p90为full=`0.9815/0.9906/1.0008`、random=`0.9856/0.9920/0.9988`、boundary=`1.0075/1.0186/1.0505`。full/random为稳定小幅正向，boundary单独轻微回退，不构成覆盖一致、可重复的系统性性能否决。按OJ优先规则预注册一次且仅一次probe：该physical-row16 reducer能否使#112716的case14 `141 μs/54分`获得可归因的display gain。不得据此扫描row数、cross-row merge、shared大小、模板参数、grid或同源码复投；终态后保存raw、提取逐提交源码并据目标case裁决。
- **OJ终态、归档与control决策**：#113677 正常完成14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/227/94/232/40/225/375/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case14由#112716的`141 μs/54分`进至`139 μs/55分`，形成真实OJ跨档收益；未覆盖case的同场波动及aggregate下降不能反向归因。因此接受为新的结构性control。`results/raw/cuda_113677_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113677.cpp`、实验快照和提交前工作文件SHA均为`6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`；已运行`tools/archive_cuda_submissions.py`核验。关闭这个 exact case14 physical-row16 reducer contract的row数、cross-row merge、shared大小、模板/grid与同源码复投；只有physical-subgroup dataflow、partial consumer ownership或后端能力有实质新前提时才可重开。工作文件保持#113677，当前队列为空。

### exp546-case11-vec4-row16-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #113677 / exp545（SHA=`6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case11_vec4_row16_exp546.cpp`，提交前工作文件与候选 SHA 均为`81ad3fe237702a261679272fa8a9b7c5e19c3f83120a6a38545634f91611c3f3`。唯一改动只在 case11 B16/KV4/L12251、39-split 的32-thread vec4 reducer：原先两次完整32-lane XOR max/sum reduction改为两个物理16-lane native row分别归约、再各以一次固定 xor16 跨行合并。producer、split、partial ABI、FP32 LSE 数学、输出 ownership、case8 和其他shape不变；这是物理 subgroup reducer dataflow，非已关闭 case7 group8、case12 vec2 或 case14 128-thread row16 consumer 几何。
- **资源、codegen 与 correctness 门禁**：实际特化保持`64 MTreg / 35 STreg / 0 B shared / 0 stack / 8 waves`。目标 LLVM control 为10个`llvm.mxc.bsm.bpermute`，candidate 为8个`llvm.mxc.mov.shfl.i32`加2个BSM，确认不是源码同义改写。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一 candidate C500 binary 的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case11同进程序列`12251→1,2,15,16,17,319,320,321,639,640,641,959,960,961,12239,12240,12241,12250→12251`全通过，覆盖页尾、39-slot live split、padding-page trap与`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对 fresh #113677 control、warmup=5、20 iterations、9 rounds，case11 candidate/control p10/p50/p90为full=`0.9974/0.9982/1.0001`、random=`0.9944/0.9976/1.0050`、boundary=`0.9912/0.9937/0.9982`。三种分布仅给出轻微正向或噪声，未构成覆盖一致的系统性回退；按 OJ 优先规则预注册一次且仅一次probe：这个 physical-row16 + fixed-xor16 reducer是否能让 #113677 的case11 `225 μs/52分`获得可归因 display gain。不得据此扫描row数、cross-row merge、shuffle mode、模板/grid或同源码复投。
- **OJ终态、归档与关闭理由**：确认队列为空、dry-run后实际POST前 SHA 均为`81ad3fe237702a261679272fa8a9b7c5e19c3f83120a6a38545634f91611c3f3`后只创建 **#113689**。它14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/227/93/233/40/223/373/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case11从#113677的`225→223 μs`，但显示分仍52；且未修改case11的 #113658/#113642 已分别出现`223/222 μs`、同为52分。这个同档刷新不能建立源码因果或 control 收益，故关闭这个 exact vec4 physical-row16 + fixed-xor16 cross-row merge contract；不得改 row 数、cross-row merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力实质改变时才可重开。已运行`tools/archive_cuda_submissions.py`，raw、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113689.cpp`、实验快照与提交前SHA一致；工作文件已恢复 #113677，当前队列为空。

### exp547-case10-row16-serial-reducer  (CORRECT / OJ ACCEPTED / SELECTED CONTROL)

- **OJ终态、归档与control决策**：确认队列空闲、dry-run后与实际POST前 SHA 均为`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`后只创建 **#113696**。它14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/230/94/234/39/222/373/181/139 μs`，分数=`92/90/83/72/73/63/54/54/57/62/52/60/57/55`。唯一覆盖目标case10从#113677的`40 μs/61分`进至`39 μs/62分`，兑现预注册的display gain；未覆盖case的同场变化不归因。因此接受为新的结构性control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113696_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113696.cpp`、实验快照和工作文件 SHA 均完全一致。关闭这个 exact physical-row16 + serial-leader reducer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件保持#113696，当前队列为空。

- **父/control、唯一差异与 changed precondition**：从 #113677 / exp545（SHA=`6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case10_row16_serial_reducer_exp547.cpp`，候选与提交前工作文件 SHA 均为`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`。唯一改动只在case10 B1/KV4/L8192、128-split 的64-thread vec2 reducer：维持 exp467 的每lane两个 packed FP16 `(m,l)` register pair、producer、split、FP32 partial ABI、LSE和每lane两个输出维度不变；改为四个物理16-lane row各自以native max/sum归约，再仅由`tid==0`串行合并四个row leader。它不同于exp542的case12/40-slot “row leader后再16-lane allreduce”，也不同于exp546的case11/39-slot vec4 physical-row16+xor16；这里是128-slot register-packed metadata下的最终consumer serial-leader dataflow，而不是row数、shuffle模式或grid扫描。
- **资源与后端门禁**：`-resource-usage`的实际新特化`paged_decode_reduce_vec2_kernel<true,false,true,true,true>`为`38 MTreg / 36 STreg / 0 B static shared / 0 stack / 8 waves`，与#113677的case10 register-packed vec2 control同档；动态shared仅由`(128+2)*4=520 B`增至`(128+4)*4=528 B`以容纳四个leader。候选目标LLVM精确为8处`llvm.mxc.mov.shfl.i32`且没有`llvm.mxc.bsm.bpermute`；control同函数为20处BSM，故不是源码同义改写。
- **数值与复用门禁**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case10同进程序列`8192→1,2,15,16,17,63,64,65,127,128,129,191,192,193,255,256,257,8191→8192`全通过，覆盖tail、4-page/split边界、padding-page trap和`full→short→full` workspace复用。
- **交错 A/B 与预注册的一次 OJ 问题**：相对fresh #113677 control、warmup=5、20 iterations、9 rounds，case10 candidate/control p10/p50/p90为full=`0.9607/0.9741/0.9821`、random=`0.9303/0.9434/0.9965`、boundary=`0.9409/1.0175/1.0593`。full/random均正向，boundary只有轻微混合负信号，未构成与覆盖范围一致、明显且可重复的系统性回退。按OJ优先规则，预注册一次且仅一次probe：这个physical-row16 + serial-leader case10 reducer能否使#113677的`40 μs/61分`得到可归因display gain或跨至下一档；不得据结果扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，终态后按目标case而非未覆盖路径同场波动决定control。

### exp548-case12-row16-serial-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case12_row16_serial_reducer_exp548.cpp`，候选与当前工作文件 SHA 均为`b8735c579c1fb80cc01cfebb2f8328116d1995869c421bc99047aa2476aad166`。唯一差异只在 case12 B8/KV8/L32768、40-split 的64-thread vec2 reducer：原 #113696 的两组32-lane XOR max/LSE reduction 改为四个物理16-lane row 各自 native max/sum reduction，且只由`tid==0`串行合并四个 row leader。producer、split40/fused-tail live count、split-major packed FP16 `(m,l)`/FP32 partial ABI、输出每lane两个维度、CTA/grid和其他shape保持control。它不同于已关闭 exp542：后者在 row leader 后让整个 row0 再执行 native allreduce；本轮改为 #113696/exp547 已证明有效的 serial-leader consumer 数据流，故是新的 physical-subgroup/consumer precondition，不是 row 数、shuffle 模式或 grid 扫描。
- **资源与后端门禁**：目标实例`paged_decode_reduce_vec2_kernel<true,false,true,false,true>`为`38 MTreg / 39 STreg / 0 B static shared / 0 stack / 8 waves`，与 #113696 case12 control的`38/39/0/0/8`同档；动态 shared 由`(2*40+2)*4=328 B`增至`(2*40+4)*4=336 B`。candidate/control LLVM 目标函数的`llvm.mxc.mov.shfl`计数为`8/0`、`llvm.mxc.bsm.bpermute`为`5/20`，确认实际后端数据流已改变。
- **数值、边界与复用门禁**：`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一 candidate C500 binary 的full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case12 同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全通过，覆盖tail、40-slot live-split边界、padding-page trap与full→short→full/short→full复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90 为full=`0.9971/0.9976/0.9989`、random=`0.9951/0.9964/0.9985`、boundary=`0.9807/0.9904/0.9992`。三分布均为正向，没有与覆盖面一致、明显且可重复的系统性回退。按OJ优先规则预注册一次且仅一次probe：这个 physical-row16 + serial-leader reducer能否使 #113696 的case12 `373 μs/60分`取得可归因 display gain或跨下一档；不得据此扫描row数、leader merge、shuffle mode、模板/grid或同源码复投。终态后保存 raw、归档逐提交源码，再按目标case决定接受或关闭。
- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`b8735c579c1fb80cc01cfebb2f8328116d1995869c421bc99047aa2476aad166`后只创建 **#113703**。它14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/235/39/224/371/182/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case12相对#113696由`373→371 μs`，但显示分保持60；同档样本不构成可归因的 display 收益，未覆盖case同场波动亦不归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113703_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113703.cpp`与实验快照 SHA 一致。关闭这个 exact physical-row16 + serial-leader reducer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp549-case13-row16-serial-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case13_row16_serial_reducer_exp549.cpp`，工作文件与快照 SHA 均为`5e999f6262f58f9b0c56075e875f402476f82489f17bc992f25c7ab8da3451ab`。唯一改动只在 case13 B1/KV8/L58966、65-split 的64-thread vec2 reducer：开启`NATIVE_ROW16_SERIAL_REDUCE`，让四个物理16-lane row分别进行 native max/sum reduction，再仅由`tid==0`串行合并四个 row leader；producer、split、packed FP16 `(m,l)`/FP32 partial ABI、LSE、每lane两维输出、CTA/grid和其他shape保持control。它不是exp548的case12重试：case13有第65个live partial由lane0额外拥有，因而是不同的overflow-aware partial consumer condition。
- **资源、codegen与数值门禁**：目标实例保持`38 MTreg / 39 STreg / 0 B static shared / 0 stack / 8 waves`，不低于#113696对应case13 reducer的驻留档；动态shared由`(2*65+2)*4=528 B`至`(2*65+4)*4=536 B`。目标 LLVM candidate/control 的`llvm.mxc.mov.shfl`为`8/0`、`llvm.mxc.bsm.bpermute`为`0/20`。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一C500 candidate的full、boundary、random均14/14、finite且100% tolerance。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`通过，覆盖65-slot边界、padding-page trap和`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册的一次 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`0.9904/0.9915/0.9929`、random=`0.9817/0.9875/0.9908`、boundary=`0.9495/0.9929/1.0433`。full/random正向，boundary的p90噪声未形成覆盖一致、明显且可重复的系统性回退。按OJ优先规则，预注册一次且仅一次probe：这个overflow-aware physical-row16 + serial-leader reducer能否使#113696的case13 `181 μs/57分`取得可归因 display gain或跨下一档；不得据结果扫描row数、leader merge、shuffle mode、模板/grid或同源码复投。终态后保存raw、逐提交快照并仅按目标case作control裁决。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`5e999f6262f58f9b0c56075e875f402476f82489f17bc992f25c7ab8da3451ab`后只创建 **#113708**。它14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/225/94/235/39/223/370/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case13保持#113696的`181 μs/57分`；同档结果不能建立可归因的 display 收益，未覆盖case同场波动亦不归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113708_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113708.cpp`与实验快照 SHA 一致。关闭这个 exact overflow-aware physical-row16 + serial-leader reducer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp550-case8-vec4-physical-row-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control与唯一可证伪假设**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉，完整候选为`solutions/archive/2026-08-16-experiments/cuda_case8_vec4_row16_exp550.cpp`；提交前工作文件与快照 SHA 均为`00ad72fce9e14d845730739365d7b34079cc28453204fe62a52cbc0bcb9126f5`。仅让case8 B16/KV4/L4096、14-split 的32-thread vec4 reducer以两个物理16-lane native max/sum network加一次固定xor16跨行交换替代原32-lane shuffle tree。producer、split14、partial ABI、LSE、输出ownership、CTA/grid和其他shape保持control。它不重开exp546的case11 exact contract：case8满长度的14个live partial全落在物理row0（lane0–13），row1只需接收全局`m/l`以输出自己的维度；case11的39-slot前提则两行均有活跃metadata，且lane0–6额外拥有第二项，物理row的metadata/LSE工作分布不同。
- **资源、后端与数值门禁**：fresh `-resource-usage` 的实际新实例`paged_decode_reduce_vec4_kernel<true,false,true,true>`为`64 MTreg / 35 STreg / 0 B static shared / 0 B stack / 8 waves`，与control `<true,false,true>`同档。目标LLVM函数candidate/control的`llvm.mxc.mov.shfl`为`8/0`，`llvm.mxc.bsm.bpermute`为`2/10`，确认改变了真实物理subgroup数据流。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一fresh C500 binary的full、boundary、random（seed=`20260809`）也均14/14、finite且100% tolerance match。case8同进程序列`4096→1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095→4096`逐项通过，覆盖页尾、19-page/split边界、14-slot live prefix、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`0.9628/0.9974/0.9991`、random=`0.9981/0.9995/1.0011`、boundary=`0.9174/0.9674/0.9987`。三分布为轻微正向或噪声，无与覆盖范围一致、明显且可重复的系统性回退。按OJ优先原则，预注册一次且仅一次probe：该case8 physical-row + fixed-xor16 reducer能否相对#113696的`94 μs/54分`取得可归因 display gain；不得据结果扫描row数、cross-row merge、shuffle mode、模板/grid或同源码复投。
- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`00ad72fce9e14d845730739365d7b34079cc28453204fe62a52cbc0bcb9126f5`后只创建 **#113712**。它14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/225/93/233/39/222/375/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case8相对#113696由`94→93 μs`，但显示分仍54；同档一微秒不足以建立可归因的 display 收益，未覆盖case同场波动亦不归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113712_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113712.cpp`与实验快照 SHA 一致。关闭这个 exact case8 physical-row16 + fixed-xor16 vec4 reducer contract；不得扫描row数、cross-row merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp551-case9-row0-prefix-native-reducer  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case9_row0_native_reducer_exp551.cpp`，提交前工作文件与候选 SHA 均为`bc78ab03710346ea0270c625fc65fb3050c0c538923215bca826964658d5f184`。唯一改动只在 case9 B32/KV8/L4096、6-split 的64-thread packed vec2 reducer：`live_splits` 最大为6，且现有 metadata loop 将所有有效 `(m,l)` owner 固定映射到 `tid=0..5`，即一个 physical 16-lane row。候选只让 row0 原生归约 global-max 与 weighted LSE，rows1–3 保留64-thread vec2 output ownership并在 barrier 后只消费共享权重。producer、split、packed partial ABI、LSE 数学、grid、动态 shared 大小与输出不变。这不是 exp548/549 的四-row serial-leader reducer：本轮没有空 row leader 或串行跨行合并，关键前提是短 live-prefix 的单 row metadata consumer。
- **资源与后端门禁**：fresh `-resource-usage` 的新实例`paged_decode_reduce_vec2_kernel<true,false,true,false,false,true>`为`38 MTreg / 39 STreg / 0 B static shared / 0 stack / 8 waves`，与 #113696 case9 control同档，动态shared仍为`(2*6+2)*4=56 B`。目标 LLVM 中 candidate 精确含8处`llvm.mxc.mov.shfl.i32`、无本函数 BSM metadata tree；control含20处`llvm.mxc.bsm.bpermute`。因此不是 source spelling 变体。
- **数值、边界与复用门禁**：`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一 candidate C500 binary 的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case9同进程序列`4096→1,15,16,17,672,688,689,704,705,1360,1376,1377,1392,1393,2048,2064,2065,2080,2081,2736,2752,2753,2768,2769,3424,3440,3441,3456,3457,4080,4095→4096`逐项通过，覆盖六个 live-prefix 转换、tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case9 candidate/control p10/p50/p90为full=`0.9932/0.9946/0.9972`、random=`0.9831/0.9940/1.0018`、boundary=`0.9773/0.9850/0.9922`。三分布均无系统性回退；按 OJ 优先规则预注册一次且仅一次 probe：该 single-row physical-subgroup metadata consumer 能否使 #113696 的case9 `234 μs/57分`取得可归因 display gain或跨下一档。不得据结果扫描 row 数、leader merge、shuffle mode、模板/grid或同源码复投；终态后按目标 case 裁决并保存 raw/逐提交源码。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`bc78ab03710346ea0270c625fc65fb3050c0c538923215bca826964658d5f184`后只创建 **#113715**。它14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/224/93/233/39/225/372/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case9相对#113696由`234→233 μs`，但显示分保持57；同档样本不构成可归因的 display 收益，未覆盖case同场波动亦不归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113715_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113715.cpp`与实验快照 SHA 一致。关闭这个 exact single-row prefix physical-subgroup metadata consumer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp552-case13-kv8-mma-direct-odd-columns  (CORRECT / REJECTED LOCALLY / NO OJ, 2026-08-16)

- **父/control、唯一 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case13_kv8_mma_direct_odd_exp552.cpp`，SHA=`0f1eb7162213fa652166cb028afc8f475941fbf2093f8abc40810f696fd59655`。它重新审查 exp412 的 case13 KV8 z8 BF16-MMA QK，但不是旧的 cross-quad handoff：同一物理 wave 的 even z 仍消费原生 MMA columns 0/1，odd z 改由本地 columns 2/3、10/11 直接完成 page-max、权重和 PV consumer ownership，不再把 odd score 经 shuffle 交回 scalar layout 的0/1、8/9 owner。只有 case13 B1/KV8/L58966、65-split 启用；split、page loader、tail、z-state tree、packed partial ABI、vec2 reducer 与其他shape保持control。
- **资源与数值门禁**：修正候选中重复 template 声明后，fresh `-resource-usage` 的目标实例`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`为`92 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，相对control `<true,true,false>` 的`82/48/8448/0/5`增加10个MTreg但未跌出5-wave档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 full-length 14/14均finite、100% tolerance。受影响case13的boundary与random（seed=`20260809`）均PASS；同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`逐项通过，覆盖65-slot边界、tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B、拒绝与重开边界**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`1.1757/1.1814/1.1855`、random=`1.1904/1.1925/1.1965`、boundary=`0.9824/1.0508/1.0809`。full和random稳定慢约18–19%，已经是与改动覆盖面一致、明显且可重复的系统性回退；因此不满足受控OJ probe资格，也不提交。它也表明去掉旧cross-quad handoff无法抵消该MMA fragment/layout的准备与寄存器成本。关闭这个 exact direct odd-column score/max/PV consumer mapping；不得只调source base、列号、lane broadcast、fragment placement或原样换名重试。只有能实质改变MMA fragment/Q load或score/PV owner数据流并重新给出资源预算的新前提才可重开。工作文件已核验仍与#113696字节一致，队列为空。

### exp553-case7-threechunk-fused-direct  (STATIC RESOURCE FAIL / NO C500 / NO OJ, 2026-08-16)

- **父/control、唯一差异与重开边界**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case7_threechunk_fused_direct_exp553.cpp`，SHA=`b608117f387faf67a363996b65df0101f88b7830dd71be3af11bbc5593ff32d0`。仅给 case7 B64/KV8/L2048 保留现有 `n_split=3` 与 `1/2/3` 个 live bucket（满容量严格`43/43/42`）的逻辑页区间，却让一个 `(b,kv_head)` CTA依次保持FP32 online state穿过这些区间，最终完成z8 tree后直接写BF16 output，并跳过case7 group8 partial/reducer round trip。它不是把host `n_split` 改回1的参数扫描，但仍必须通过比单live direct-output更严的生产资源门槛，才可讨论C500或OJ。
- **资源门禁与关闭**：`-resource-usage` 成功构建（资源binary SHA=`c9c0f97bd8b246fc834032155d63d0457a5ca7370a48e1e8d17d8e47c46fdaf5`）；新case7特化`paged_decode_case13_kv8_headpair_z8_kernel<true,false,true,true>`为`86 MTreg / 58 STreg / 8448 B shared / 0 stack / 5 waves`，相对#113696当前case7 control `<true,false,true>` 的`82/50/8448/0/5`增加`4 MTreg + 8 STreg`。这已经劣于已关闭exp511 single-live direct-output的`84/54`静态反证，未满足case7 direct-output路径的资源上限；不运行CPU/C500 correctness、A/B或OJ，也不修改工作文件。关闭这个 exact `1/2/3` logical-chunk CTA-local direct finalizer；不得仅调chunk循环、store顺序、scratch/指针表达式或launch形状重试。只有能实质改变跨chunk state consumer ownership、消除direct BF16转换活跃区间或保持/降低control资源档的新前提才能重开。

### exp554-case12-wave64-next-pid-broadcast  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case12_wave64_next_pid_broadcast_exp554.cpp`，SHA=`133715276366e04d83bf0fc61c3fe27ecb2b7a4008035691bdaf9a72950e456b`。仅在 case12 B8/KV8/L32768、split40 的 z8 producer 启用第四模板参数`WAVE64_PID_BROADCAST=true`：每个物理64-lane wave只由其固定lane0读取`bt_row[p + 1]`，随后以raw int32 `__builtin_mxc_bsm_bpermute`广播 page ID；每页的 next-page ID global load 从256次降至4次。loader、QK/PV、tail、split、partial ABI、reducer、其他case及满容量映射保持control。这不同于已关闭的16-lane row-owner PID broadcast：本轮先在精确`dim3(16,2,8)`几何中验证了固定源、wave隔离的raw int32 BSM能力。
- **资源、能力与数值门禁**：独立`c500_wave64_i32_broadcast_probe`在真实C500通过，输出`[PASS] fixed lane-0 raw int32 BSM broadcast is isolated per z8 wave`。fresh candidate实例`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`为`82 MTreg / 52 STreg / 8448 B shared / 0 stack / 5 waves`，相对case12 control `<true,false,false>` 的`82/50/8448/0/5`仅增加2个STreg而不降驻留档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的14-case full、boundary、random（seed=`20260809`）全通过、finite且100% tolerance。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`逐项通过，覆盖tail、40-slot边界、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册的一次 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`1.0076/1.0084/1.0098`、random=`1.0103/1.0121/1.0155`、boundary=`1.0173/1.0199/1.0225`。本地为小幅一致负向，记录为风险证据，但幅度未达到与该单点global-ID-load变更相称的明显系统性回退否决阈值；按OJ优先规则预注册一次且仅一次probe：该wave64 page-ID broadcast能否使#113696的case12 `373 μs/60分`取得可归因display gain或跨下一档。不得据结果扫描source lane、broadcast宽度、load表达、模板/grid或同源码复投；终态后按目标case裁决、归档raw和逐提交源码。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`133715276366e04d83bf0fc61c3fe27ecb2b7a4008035691bdaf9a72950e456b`后只创建 **#113736**。它14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/224/94/234/39/222/376/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12由#113696的`373→376 μs`、显示分仍60；case7的`230→224 μs`未被该改动覆盖，是 timing-tier 刷新而非源码收益，故不替换control。已运行`tools/archive_cuda_submissions.py`，`results/raw/cuda_113736_raw.json`、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113736.cpp`与实验快照 SHA 一致。关闭这个 exact wave64 raw-BSM next-page PID broadcast contract；不得扫描source lane、broadcast宽度、load时点/表达式、模板/grid或同源码复投。只有不同后端 primitive、producer/consumer ownership或页面数据流出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### c500-readlane-uniform-i32-probe  (CAPABILITY PASS / CLOSED BACKEND EVIDENCE, 2026-08-16)

- **问题与 changed precondition**：已归档的`c500_readlane_wave64_probe`只否定了将非均匀`lane^32` peer permutation替换为`readlane`；它观察到readlane适合uniform source broadcast，但没有对raw int32 page ID的固定lane0语义作直接验证。本probe在精确case12 z8 `dim3(16,2,8)`中让每个physical 64-lane wave的lane0独占不同int32 payload，其余lane写sentinel，并以`__builtin_mxc_readlane(value, 0u)`广播。
- **C500事实与用途边界**：source/driver/binary SHA分别为`5fed86d73604057f5780c3bba4cc15d2227b754da5e765b27c653c05388144c2` / `c15dc3b3019b08b5c851b214cd6418a28f17bb1a59515a270676f5c0a8d9b257` / `48b03afe4f80110cff9c833fcc770c0c38ff0ab1cf2488e389cfedf64fcbee71`；真实C500输出`[PASS] fixed lane-0 readlane int32 broadcast is isolated per z8 wave`。exp554 已由 #113736 关闭 raw-BSM backend；本 probe 因此提供不同 primitive 的uniform page-ID producer能力前提，并已作为 exp555 的后端门禁。该能力本身不证明端到端收益；#113750 已否定这一 exact readlane page-ID dataflow，故 probe 归档为关闭后端证据，不能以同一 ownership/页面数据流再次进入 OJ。

### exp555-case12-readlane-next-pid-broadcast  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case12_readlane_next_pid_broadcast_exp555.cpp`，SHA=`8532e57b3cbcac09762c9e7a2ba753e7877c976bbc23a528e3aace2891ef6685`。仅在 case12 B8/KV8/L32768、40-split 的 z8 producer新增第四模板参数`WAVE64_PID_READLANE=true`：每个物理64-lane wave仅固定lane0读取`bt_row[p+1]`，再由`__builtin_mxc_readlane(value,0u)`广播 raw int32 page ID；每页 next-page ID global load 从256次降至4次。它不是exp554的raw-BSM参数扫描：exp554的raw BSM backend 已完整关闭，本轮只替换为独立probe已验证的`readlane` primitive；loader、QK/PV、tail、split、partial ABI、reducer、其他shape及满容量映射保持control。
- **资源、后端与数值门禁**：normal/resource binary SHA分别为`15098cae8c6e182dc99d2f95659e7b4d3fd2a23e03fd4bd1f09855fe343d93e4` / `e36616bf165ef40240161ad524a2a4ddb978a8fb456c956e4e493d23f426c866`。fresh `-resource-usage` 的实际新case12特化`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`为`82 MTreg / 52 STreg / 8448 B shared / 0 stack / 5 waves`；control为`82/50/8448/0/5`，无spill或驻留降档。以`mxcc -emit-llvm -S`复编译后，candidate实际特化含1处`llvm.mxc.rl`，control为0，确认readlane没有退化为普通load/源码同义表达。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`逐项通过，覆盖tail、40-slot边界、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册的一次 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case12 candidate/control p10/p50/p90为full=`1.0051/1.0060/1.0076`、random=`0.9953/0.9978/1.0012`、boundary=`1.0061/1.0113/1.0129`。full/boundary为约0.6–1.1%小幅风险、random轻微正向，尚未达到与覆盖范围一致、明显且可重复的系统性回退否决阈值；按 OJ 优先规则预注册一次且仅一次probe：此不同readlane backend能否使#113696的case12 `373 μs/60分`取得可归因display gain或跨下一档。不得据结果扫描source lane、broadcast宽度、load时点/表达式、模板/grid或同源码复投；终态后按目标case裁决、归档raw和逐提交源码。

- **OJ终态、归档与关闭理由**：#113750 已终态为 **14/14 Accepted / `66.07`**，case1–14=`3/4/9/23/17/28/224/94/233/39/224/374/181/139 μs`、分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12由#113696的`373→374 μs`、显示分仍60；case7的`230→224 μs/54→55分`未被该改动覆盖，只是同场 timing-tier 刷新。故 OJ 直接否定这个 exact wave64 `__builtin_mxc_readlane` next-page PID broadcast contract；不得扫描source lane、broadcast宽度、load时点/表达式、模板/grid或同源码复投。已运行`tools/archive_cuda_submissions.py`，raw 内嵌源码、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113750.cpp`、实验快照及提交前 SHA 均为`8532e57b3cbcac09762c9e7a2ba753e7877c976bbc23a528e3aace2891ef6685`。工作文件已恢复 #113696；只有不同 producer/consumer ownership、页面数据流或尚未验证的后端能力有实质新前提时才可重开。

### exp556-case12-paired-logical-split-q-reuse  (STATIC RESOURCE FAIL / NO C500 / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case12_pair_split_q_reuse_exp556.cpp`，SHA=`9328d3e5d16345b8e5e6834011eb6c2625501cdc3d22d1528195debf3bb5b275`。只给case12 B8/KV8/L32768的40-split z8 producer把每个CTA的`blockIdx.y`映射为两个连续logical split：同一个256-thread CTA顺序完成两个独立FP32 online-softmax/z-tree partial，保留40个partial槽和原vec2 reducer ABI，但只加载、解包并预缩放一次不随split变化的Q。producer grid从`8×8×40=2560`降为`8×8×20=1280` CTA；每个logical split的page区间、K/V page loop、tail、z merge、packed `(m,l)` partial和所有其他shape保持control。这不是case12 split39/41参数扫描，也不同于case14 exp162的z0/z1双split、16KiB双buffer布局：本轮保持单8KiB page buffer与完整z8 tree，只改变跨logical-split CTA/Q consumer ownership。
- **静态资源门禁与关闭**：`tools/build_local_maca.sh ... -resource-usage`成功完成，详见`log/cuda_case12_pair_split_q_reuse_exp556_resource.log`。实际新特化`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`为`102 MTreg / 80 STreg / 8448 B shared / 0 stack / 4 waves`，相对control `<true,false,false>`的`82/50/8448/0/5`丢失一档驻留；外层pair loop使Q、state及双logical-split控制区间同时拉长，节省一次Q加载不足以抵消该寄存器压力。故不运行CPU/C500 correctness、A/B或OJ，不以loop写法、pair边界、Q加载位置、split/reducer补偿或同一CTA-pair数据流细扫。只有可实质缩短双split live range、改变Q/state consumer ownership或保持control资源档的新前提才可重新提出；工作文件仍为#113696。

### exp557-case5-packed-ml-partial  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control 与唯一差异**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case5_packed_ml_partial_exp557.cpp`，SHA=`b0fe713c217d12f90a8de6e962bd1efecb20ebb6bf9285aea135c33130327d7a`。仅 case5 B16/KV4/L141、5-split 的 z4 producer→group8 reducer `(m,l)` metadata ABI 从两份FP32改为一份FP16x2；`partial_acc`仍为FP32，QK/PV、tail、loader、split、CTA ownership、reducer grid 和其他case不变。case6已显式保留FP32 metadata reducer，因而不受影响。
- **资源、数值与边界门禁**：完整命令/资源结果已保存于`log/cuda_case5_packed_ml_partial_exp557_resource.log`；case5 control/candidate 分别为`74/52/8320/0/6`与`74/48/8320/0/6`，无spill且不降驻留。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case5同进程序列`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140→141`全通过，覆盖五个2-page split边界、tail、padding-page trap和`full→short→full`/`short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case5 candidate/control p10/p50/p90为full=`0.9830/0.9952/1.0131`、random=`0.9937/1.0286/1.0427`、boundary=`0.9637/1.0044/1.0498`。random的首次小幅负信号在更长的21×100复测中变为`0.9592/0.9923/1.0327`，故不构成覆盖一致、明显且可重复的系统性回退。按 OJ 优先规则预注册一次且仅一次probe：该case5 packed FP16x2 `(m,l)` producer/reducer ABI能否相对#113696的`17 μs/73分`达到`≤16 μs`并取得可归因display gain；不得据结果扫描metadata格式、cast、packing、reducer模板/grid或同源码复投。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`b0fe713c217d12f90a8de6e962bd1efecb20ebb6bf9285aea135c33130327d7a`后只创建 **#113768**。它14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/224/94/236/39/223/375/182/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case5相对#113696保持`17 μs/73分`，未兑现预注册display gain；未覆盖case的同场波动不作归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，raw 内嵌源码、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113768.cpp`、实验快照与提交前 SHA 均为`b0fe713c217d12f90a8de6e962bd1efecb20ebb6bf9285aea135c33130327d7a`。关闭这个 exact case5 FP16x2 `(m,l)` producer/reducer partial ABI；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投。只有partial格式、producer/consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp558-case6-packed-ml-partial  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case6_packed_ml_partial_exp558.cpp`，工作文件与快照 SHA 均为`8c61383cf5b175e99ad2525329847fab4985c1a5e0105d82afdb68ec63d0ea85`。唯一改动只在 case6 B16/KV8/L362、8-split 的 token-parallel producer→group8 reducer partial ABI：producer 将每个 `(m,l)` 从两份 FP32 写入改为一份 FP16x2，case6 group8 reducer选用对应的解包路径；`partial_acc`仍为FP32，QK/PV、tail、3-page/split 映射、native-row QK、K-only lookahead、loader、split、ownership、grid和其他shape保持control。这不是 #113768 / exp557 的原样重投：后者是case5 B16/KV4/L141、5-split 的z4 MMA producer契约；本轮是KV8 token-parallel的8-live-split producer/reducer handoff。
- **资源、正确性与边界门禁**：`log/cuda_case6_packed_ml_partial_exp558_control_resource.log`与`log/cuda_case6_packed_ml_partial_exp558_resource.log`确认case6 producer从`80/44/8320/0/6`到`80/42/8320/0/6`，group8 reducer从`66/26/0/0/7`到`66/25/0/0/7`，均无stack/spill且不降驻留。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case6同进程序列`362→1,2,15,16,17,47,48,49,95,96,97,143,144,145,191,192,193,239,240,241,287,288,289,335,336,337,361→362`通过，覆盖8个live split边界、tail、padding-page trap及`full→short→full`/`short→full`复用。
- **交错 A/B 与唯一 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case6 candidate/control p10/p50/p90为full=`0.9902/0.9975/1.0172`、random=`0.9693/0.9924/1.0152`、boundary=`0.9738/0.9953/1.0212`。三分布未出现与改动覆盖范围一致、明显且可重复的系统性回退；队列核对为空。按 OJ 优先规则预注册一次且仅一次probe：该case6 packed FP16x2 `(m,l)` producer/reducer ABI能否相对#113696的`28 μs/63分`达到`≤27 μs`并取得可归因display gain；不得据结果扫描metadata格式、cast、packing、reducer模板/grid或同源码复投。终态后保存raw、逐提交源码，并仅按case6目标裁决control。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前 SHA 均为`8c61383cf5b175e99ad2525329847fab4985c1a5e0105d82afdb68ec63d0ea85`后只创建 **#113827**。它14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/226/93/235/38/223/375/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case6保持#113696的`28 μs/63分`，未兑现预注册display gain；未覆盖case的同场波动不作归因，故不替换control。已运行`tools/archive_cuda_submissions.py`，raw 内嵌源码、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113827.cpp`、实验快照与提交前 SHA 均为`8c61383cf5b175e99ad2525329847fab4985c1a5e0105d82afdb68ec63d0ea85`。关闭这个 exact case6 FP16x2 `(m,l)` producer/reducer partial ABI；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投。只有partial格式、producer/consumer ownership或后端能力出现实质新前提时才可重开；工作文件已恢复 #113696，当前队列为空。

### exp559-case7-static-row16-weight-broadcast  (CORRECT / OJ ACCEPTED / CONTROL, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113696 / exp547（SHA=`fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case7_static_weight_broadcast_exp559.cpp`，工作文件与快照 SHA 均为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`。仅 case7 B64/KV8/L2048、固定`n_split=3`的packed group8 reducer新增`STATIC_WEIGHT_SPLITS=3`：保持rolled accumulator loop、packed FP16x2 `(m,l)`、fused-tail、producer、partial ABI、grid、ownership和`NATIVE_ROW16_REDUCE=false`不变，只将每个accumulator迭代中runtime `__shfl_sync(..., w_lane, s, 16)`替换为`native_row16_broadcast<0/1/2>`的静态source lane。它不是exp544的metadata/LSE row16 reduce，也不是exp263的runtime raw-BSM broadcast；与exp310同属静态weight broadcast但当前只存在1–3个live split，且不复制/完全展开14-way accumulator，因此构成新的live-prefix前提。
- **资源、后端与数值门禁**：case7目标reducer为`54 MTreg / 25 STreg / 0 B shared / 0 stack / 8 static waves`，优于control的`66/25/0/0/7`；精确LLVM特化含8个`llvm.mxc.bsm.bpermute`（仅max/LSE）和9个`llvm.mxc.mov.shfl`，不再保留动态weight handoff。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case7同进程序列`2048→1,2,15,16,17,687,688,689,703,704,705,1375,1376,1377,1391,1392,1393,2047→2048`逐项通过，覆盖1/2/3-live-split、full/tail、padding-page trap及`full→short→full`复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113696 control、warmup=5、20 iterations、9 rounds，case7 candidate/control p10/p50/p90为full=`0.9976/0.9981/1.0024`、random=`0.9926/1.0013/1.0027`、boundary=`0.9972/1.0008/1.0069`。三种分布均为噪声级中性或轻微正向，没有与覆盖范围一致、明显且可重复的系统性回退。按OJ优先规则预注册一次且仅一次probe：静态row16 weight source能否使case7相对#113696的`230 μs/54分`取得可归因改善或跨下一显示档；不得据此扫描source lane、live-split数、template/grid、metadata reduction或同源码复投。提交前确认队列空闲，并在dry-run后和实际POST前分别核对本SHA。

- **OJ终态、归档与control决策**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`后只创建 **#113889**。它14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/226/94/235/38/222/378/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case7由#113696的`230 μs/54分`到`226 μs/55分`，兑现预注册display gain；case13的`57→56分`和其他未覆盖路径变化只是同场timing-tier波动，不能抵消这条因果。已运行`tools/archive_cuda_submissions.py`，raw内嵌源码、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`、实验快照与工作文件 SHA 一致；接受为新的结构性control。关闭这个 exact static-source weight handoff；不得扫描source lane、live-split数、template/grid、metadata reduction或同源码复投。工作文件保持 #113889，当前队列为空。

### exp560-case5-static-row16-weight-broadcast  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case5_static_weight_broadcast_exp560.cpp`，SHA=`3ee1f9b0534e32ab4db350a64e398625f29efe9e9f43878b8fc5e0628724a631`。只给case5 B16/KV4/L141、最多5个fused-tail live split 的 group8 reducer 添加`STATIC_WEIGHT_SPLITS=5`：保持rolled accumulator loop、native-row max/LSE reduction、packed FP16x2 `(m,l)`、producer、partial ABI、tail、grid、ownership和其余dispatch不变，仅将每轮runtime weight `__shfl_sync(..., w_lane, s, 16)`换成`native_row16_broadcast<0..4>`静态source。它与exp559的case7固定1–3-live-prefix共享机制，但case5的KV4/z4与1–5-live-prefix是独立资源/长度前提；不重开exp310的固定14-way完整展开。
- **资源、后端与正确性门禁**：case5 group8 reducer从control的`66 MTreg / 26 STreg / 0 B shared / 0 stack / 7 waves`变为`36/26/0/0/8`，无spill；候选精确特化不再保留动态 BSM weight handoff（control 5处、candidate 0处）。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；candidate C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance。case5同进程序列`141→1,2,15,16,17,31,32,33,63,64,65,95,96,97,127,128,129,140→141`通过，覆盖1–5-live-split、tail、padding-page trap和`full→short→full`复用。
- **交错 A/B 与关闭**：为排除旧二进制身份，在同一轮先从两个冻结源码重建control/candidate；随后严格串行运行case5、warmup=5、20 iterations、9 rounds。candidate/control p10/p50/p90分别为full=`0.9836/1.0244/1.0585`、random=`1.0250/1.0594/1.0824`、boundary=`1.0160/1.0273/1.0751`。三种长度分布的p50均为负，随机长度约慢5.9%，构成与改动覆盖范围一致、明显且可重复的系统性本地回退；因此按OJ优先规则的唯一本地性能否决条件，**不提交 OJ**。关闭这个 exact case5 1–5-live-split static-source weight handoff；不得扫描source lane、live-split数、template/grid、metadata reduction或同源码复投。实验快照保留，工作文件继续保持 #113889，OJ 队列为空。

### exp561-case6-static-weight-unrolled8  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选为`solutions/archive/2026-08-16-experiments/cuda_case6_static_weight_unrolled8_exp561.cpp`，SHA=`fefcfa55bc17f0456ef7a984e2fe301ec8d39be7019f714207c15af62dde25e1`。仅 case6 B16/KV8/L362、8个物理partial slot 的 group8 reducer启用固定1–8 live prefix：保持 producer、partial ABI、native-row max/LSE、tail、grid、ownership与其他dispatch不变；每个CTA-uniform的`live_splits>S` guard下，以固定`native_row16_broadcast<S>`完成第S个weight handoff，并按原递增split顺序有界累加，故不读未写partial。它不是exp310的固定14-way完整展开：本轮针对KV8 token-parallel producer的全部8个实际slot，唯一机制是将runtime source BSM替换成固定source与有界live-prefix consumer。
- **资源与数值门禁**：fresh `-resource-usage` 的实际case6 reducer从control的`66 MTreg / 26 STreg / 0 B shared / 0 stack / 7 waves`变为`34/24/0/0/8`，无spill并升一档。`test_kernel_logic.py` 14/14通过；同一candidate C500 binary的full、boundary、random（seed=`20260809`）各14/14通过、finite且100% tolerance。case6同进程序列`362→1,2,15,16,17,47,48,49,95,96,97,143,144,145,191,192,193,239,240,241,287,288,289,335,336,337,361→362`逐项通过，覆盖1–8 live prefix、tail、padding-page trap和`full→short→full`复用。
- **交错 A/B 与关闭**：从两个冻结源码重建control/candidate后，严格串行运行case6、warmup=5、20 iterations、9 rounds；candidate/control p10/p50/p90为full=`1.0249/1.0288/1.0435`、random=`1.0161/1.0329/1.0592`、boundary=`1.0105/1.0331/1.0489`。三个分布均稳定约慢3%，构成明显且可重复的系统性本地回退，即使资源升至8 waves也不能抵消；按OJ优先规则不具备一次probe资格，**不提交 OJ**。关闭这个 exact case6 static 8-slot/unrolled-prefix group8 weight handoff；不得扫描source lane、live-split数、展开/模板、metadata reduction或同源码复投。与exp560一起说明当前 static-source weight family只保留已接受的case7固定1–3前缀；工作文件仍逐字节保持 #113889，队列为空。

### exp562-case13-first-tree-normalized-bf16-state  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case13_first_tree_normalized_bf16_exp562.cpp`，SHA=`ae220852d4a75ab0f97f76e65947d14738d45bcab6ce6da2a36b7a99c06ac639`。仅 case13 B1/KV8/L58966、65-split 的 z8 producer在第一条 tree edge（`tz=4..7 -> tz=0..3`）把 peer shared payload 从FP32 raw `acc` 改为BF16 normalized `acc/l`，同时保持FP32 `(m,l)`；consumer以`peer_l * exp2(peer_m-m_all)`恢复 raw contribution。第二、第三条 tree edge仍为control的FP32 state，split、QK/PV、同步loader、tail、packed global partial ABI、vec2 reducer和其他shape均不变。它不是exp461的KV4/z4完整BF16 round-trip，也不是exp503的case11/z4 symmetric-finalizer stage-1 layout：本轮是case13 in-place z8第一层16个peer state由8 KiB降至4 KiB、其后才复用同一buffer的producer/consumer shared-state契约。
- **资源与数值门禁**：normal/resource binary SHA分别为`90b21f54aeb294bd5b9206aadc8b0955a44b585dc26d9a17fd824ddbe2b3bc10` / `846bc8a618f0dd18df01496c01dbf548b4f6bd706be5770ce2fb4aeb0851c4de`。fresh `-resource-usage` 的精确case13实例`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，与control `<true,true,false,false>`一致，无spill/驻留降档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate C500 full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`逐项通过，覆盖65-slot转换、tail、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B、拒绝与重开边界**：相对fresh #113889 control，首轮warmup=5、20 iterations、9 rounds的candidate/control p10/p50/p90为full=`1.0019/1.0054/1.0074`、random=`1.0034/1.0064/1.0096`、boundary=`0.9878/1.0436/1.0658`。为区分短边界噪声，随后21 rounds×100 iterations复测：full=`0.9969/1.0032/1.0054`、random=`0.9986/1.0034/1.0100`、boundary=`1.0189/1.0524/1.1126`。三分布中位数均为负，尤其boundary复测所有分位都回退；这是与该CTA-local state conversion/恢复开销覆盖一致、明显且可重复的系统性本地回退，满足唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case13 first-tree normalized-BF16 payload contract；不得只改packing、BF16 cast、buffer半区、store/load lifetime、FMA拼写或同源码复投。只有merge tree、producer/consumer ownership、状态表示或实际共享读写量出现实质新前提时才可重开。工作文件已恢复并核验为 #113889，OJ队列为空。

### exp563-case8-packed-ml-vec4  (INVALID DISPATCH / NO A-B / NO OJ / NOT PERFORMANCE EVIDENCE, 2026-08-16)

- **实现审计与资源**：该源码只将 producer 改为FP16x2并新建了packed vec4 reducer分支。随后发现真实case8固定`n_split=14`，会在`run_kernel`走`reduce_splits <= 16`的 group8 reducer，而不是这个vec4分支；运行中的 group8 实例仍为`PACKED_ML=false`，会把FP16x2 `partial_m`按FP32 `m`读取且读取未写的`partial_l`。因此资源中的`82/62/8320/0/5` producer和未被调用的vec4 `64/35/0/0/8`都不能构成有效端到端ABI门禁；CPU manifest 与 `test_kernel_logic.py`的14/14也没有覆盖该设备派发错误。
- **真实 C500 结果与处理**：candidate normal binary SHA=`c1160b409e7e9dc19018d53811e74edbb8a61f923dc94362ee18f6fbf374a076`。14-case `--full-length`中其余13个case通过、case8为`match=0.474182`、`max_error=1.186523e-01`、`max_tol_ratio=6.629`；该失败证明producer/reducer ABI不匹配，**不证明FP16 `(m,l)`本身数值不可用**。未运行boundary/random、A/B或OJ；本无效源码只作审计证据，不得用于性能结论。正确的case8 group8 packed-metadata契约须以独立候选重建并从资源、真实C500 correctness重新开始。工作文件已恢复并核验为 #113889，OJ队列为空。

### exp564-case8-packed-ml-group8  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case8_packed_ml_group8_exp564.cpp`，工作文件与快照 SHA=`ba815fd9226e828585da7a50b2dd1b819d68a7b16ae8ffd9b5bcb44b5b67884a`。只给 case8 B16/KV4/L4096、14-split 的 z4 BF16-MMA producer→实际 fused-tail group8 reducer，把每个 partial 的两份 FP32 `(m,l)` 改为`partial_m`内的一份 FP16x2，并让**真正运行的**`paged_decode_reduce_group8_kernel<BASE2,false,true,true,true,true>`读取该 packed metadata；`partial_acc`、QK/PV、split、tail、group8 ownership、grid和所有其他shape不变。exp563只改了未被14-split路径调用的vec4 reducer而导致 ABI mismatch；本轮将生产端和实际group8 consumer作为一个完整契约重建。case5/6的 exact packed-ABI OJ反证不外推到这里：case8有不同的14-slot full-page z4 producer、fused-tail计数和 native-row group8 consumer。目标机制是将每split metadata读写从两份FP32降为一份4-byte packed载荷；case8每partial最多19页/304 tokens，FP16 `l` 没有表示范围风险。
- **资源、静态身份与正确性门禁**：normal/resource binary SHA=`c9b8e136023d32bea2325dcede04fd87f8b3b6cfe6d1c7a3ffb282ea387d3250` / `8012fae728534bf4389aa2287e521d6fc21e9b3183b22dd4b955a313e11eb278`。fresh `-resource-usage` 对实际case8 producer给出 control/candidate=`82/64/8320/0/5 -> 82/62/8320/0/5`，实际 group8 reducer为 control/candidate=`66/24/0/0/7 -> 66/25/0/0/7`；无spill、无shared或resident-wave回退。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14；同一candidate C500 `--full-length`与`--lengths boundary`均14/14、finite、100% tolerance，受影响case8 `--lengths random --seed 20260809`也为100% match。case8同进程精确序列`4096 -> 1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095 -> 4096`全部通过，覆盖page/tail、19-page/split的14-slot live-prefix边界、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：从 #113889 不可变快照和候选重新构建的二进制，严格串行以warmup=5、iterations=20、rounds=9测试case8。candidate/control p10/p50/p90为full=`0.9965/0.9977/1.0001`、random=`0.9986/1.0006/1.0091`、boundary=`0.9568/0.9992/1.0327`。三分布均为噪声级中性或轻微正向，没有与该ABI覆盖一致、明显且可重复的系统性回退；本地性能不替代OJ。按OJ优先规则预注册一次且仅一次probe：该实际group8 FP16x2 `(m,l)` producer/reducer ABI能否使#113889的唯一覆盖目标case8 `94 μs/54分`获得可归因改善或跨下一显示档。不得据此扫描metadata格式、cast、packing、reducer模板/grid或同源码复投；提交前须确认队列空闲，并在dry-run后和实际POST前分别核对本 SHA。
- **OJ #114013、归因与关闭**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/226/93/235/39/223/371/181/139 μs`，显示分=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case8仅`94→93 μs`、仍54分，不能建立可归因display收益；总分刷新来自未覆盖case13的`182/56→181/57` timing-tier样本。故拒绝并关闭这个 exact case8 packed FP16x2 metadata producer/group8-consumer ABI，不替换#113889 control；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投。raw、逐提交快照和候选快照SHA均为`ba815fd9226e828585da7a50b2dd1b819d68a7b16ae8ffd9b5bcb44b5b67884a`，工作文件已恢复并核验#113889，OJ队列为空。

### exp565-case11-fixed20-mma-pipeline  (RESOURCE GATE REJECTED / NO C500 / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case11_fixed20_mma_exp565.cpp`，SHA=`4ea44746589c45248fc8d9d711db1e214deab986e5ac76db3a8a6b040368c055`。只给 case11 B16/KV4/L12251、39-split 的完整20-page owner追加一个编译期固定 hot loop：19个`HAS_NEXT=true`页加末页`false`，短长度、最后5个full-page/fused-tail owner和所有其他shape继续走control泛化路径。它复用当前已有的`process_case8_fixed_full_page`、BF16-MMA QK、distributed score state和对称 z4 finalizer；相对旧 scalar-QK exp292 的固定16页流水，QK、state ownership与每页代码形态已实质改变，故先按资源门禁独立复审。
- **资源否决与关闭范围**：`log/cuda_case11_fixed20_exp565_resource.log` 的实际20参数 case11 specialization 为`102 MTreg / 62 STreg / 8320 B shared / 0 stack / 4 static waves`，而 #113889 control 的同一case11实例为`80/58/8320/0/6`。尽管无spill，寄存器增长使驻留从6降至4 waves，违反生产资源门禁；因此不运行CPU/C500 correctness、A/B或OJ。关闭这个 exact current-MMA/symmetric-finalizer case11 fixed20 pipeline；不得只扫固定页数、unroll、分支表达或同源码重投。只有显著缩短QK/state/next-page live range或改变producer/consumer ownership的实质新前提才能重开。工作文件已恢复并核验为#113889，OJ队列为空。

### exp566-case13-head4-x32-z8-initial  (INVALID TAIL STATE / NO PERFORMANCE EVIDENCE / NO OJ, 2026-08-16)

- **资源前提与初版失效**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉。先以`tests/archive/closed-backend-probes/c500_case13_head4_x32_resource_probe.cpp`完整模拟`dim3(32,1,8)`、四头×四维、双 token K/V lookahead 和8→4→2→1 state tree；资源为`80 MTreg / 22 STreg / 8448 B shared / 0 stack / 6 waves`。随后初版 production candidate `solutions/archive/2026-08-16-experiments/cuda_case13_head4_x32_z8_exp566.cpp`（SHA=`2355c811fa981d2bf81ceb9a368b792a261ce7c53e3f59097882c1712f77bcab`）也为`78/44/8448/0/6`，但 case13 `--lengths boundary` 的长度1发生 NaN。
- **失效根因与隔离**：短 tail 中没有 token 的 z 分区仍计算`exp2(-inf - -inf)`，把空 `(m=-inf,l=0)` state 变为 NaN；这不是性能数据，也不表示四头 ownership 数值不可实现。仅修复“本 z 至少拥有一个 tail token 才更新 online state”的语义保护后，作为独立 exp567 从完整资源、correctness 和 A/B 重新开始；本初版保留为实现审计证据，不提交 OJ。

### exp567-case13-head4-x32-z8  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case13_head4_x32_z8_exp567.cpp`，SHA=`83cef20936ec79abdd6b1f35331435a65c62c64e3109968f899b396695fbd4f6`。仅 case13 B1/KV8/L58966、65-split producer从`dim3(16,2,8)`、每线程两头×八维改为`dim3(32,1,8)`、每线程四头×四维；一个 K/V `uint2` payload及其 BF16 解包服务四个 GQA head，两个 token 由每个 z 共同所有，四个独立32-lane QK allreduce后沿用同步 K+V-over-PV、packed FP16x2 `(m,l)` partial、8→4→2→1 shared state tree、split65/57页映射和原 vec2 reducer。它不同于已关闭的旧128-thread `(16,2,4)` head4：Q/acc 常驻标量仍各16个，且真实资源先通过6-wave门槛。
- **资源与正确性门禁**：active resource probe 为`80/22/8448/0/6`，完整实际case13 kernel 为`78 MTreg / 44 STreg / 8448 B shared / 0 stack / 6 waves`，相对control case13的`82/48/8448/0/5`无spill且升一档。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一candidate C500 binary的14-case full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖padding-page trap、65-split转换、tail和`full→short→full`/`short→full`复用。
- **交错 A/B、关闭与重开边界**：相对fresh #113889 control，以warmup=5、iterations=20、rounds=9严格串行，candidate/control p10/p50/p90为full=`2.2117/2.2252/2.2358`、random=`2.2316/2.2364/2.2473`、boundary=`1.1110/1.1688/1.1822`。三个分布均为窄而巨大的负向，full/random约慢2.23×；四个32-lane QK allreduce和四头 state/PV 计算远超过共享 K/V 解包收益。它满足 OJ 优先规则中唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case13 `(32,1,8)` head4/x32/z8 ownership；不得仅扫描 x/z、shuffle/reduction拼写、tail guard、load表达、state store或同源码复投。只有能实质改变四头 QK/PV consumer ownership、减少四套score/state工作或改变跨头数据流的新前提才可重开。工作文件已恢复并核验 #113889，OJ队列为空。

### exp568-case12-paired-split-raw-q-lifetime  (STATIC RESOURCE GATE FAILED / NO C500 / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case12_pair_q_shared_lifetime_exp568.cpp`，SHA=`1cae82e573ad319262fc3f32a6356da6705c5290cf8c15304de16793715f0eb9`。只给case12 B8/KV8/L32768、40-split z8 producer把相邻两个 logical split 放到同一256-thread CTA（producer grid `2560→1280`），并保持40个global partial槽与原vec2 reducer ABI。相对exp556，唯一的新前提是把Q的跨split生存期由16个FP32每线程寄存器改成一次性、只由`tz==0`写入的1 KiB raw-BF16 shared tile；每个split才从该tile重建自己的FP32 Q、online `(m,l,acc)`、page loop、z-tree和partial写出，两个split state不共存。
- **旧反证为何不直接覆盖**：exp443把case14的MMA Q fragment在**每页**从shared读入MMA，即使5→6 waves仍因逐页LDS与barrier慢86.2%；本轮的shared raw Q只在一个case12 paired CTA的开头写一次、每logical split读取一次，目的仅是缩短paired split间的Q/state寄存器寿命。它也不是exp556的外层pair-loop原样重试：后者为`102/80/8448/0/4`，FP32 Q跨两个逻辑状态常驻。
- **静态资源门禁与关闭范围**：`tools/build_local_maca.sh ... -resource-usage`成功，资源binary SHA=`a989b8c41a98d09b35f8a6f2c4c57cdad73dc7b83d479c0d1201375fb3645476`。实际case12新特化`paged_decode_case13_kv8_headpair_z8_kernel<true,false,false,true>`为`100 MTreg / 76 STreg / 9472 B shared / 0 stack / 4 waves`，虽较exp556少`2 MTreg/4 STreg`，仍远差于control `<true,false,false>`的`82/50/8448/0/5`。额外1 KiB shared也没有换回驻留档；因此不运行CPU、C500 correctness、A/B或OJ。关闭这个 exact paired-CTA raw-Q shared-lifetime contract；不得只改Q tile地址、vector type、barrier、pair边界或循环拼写重试。只有能使每split state真正编译隔离、改变Q/state consumer ownership且保持至少control的5-wave资源档的实质新前提，才可重开。工作文件已恢复并核验#113889，OJ队列为空。

### exp569-case12-concurrent-dual-split-z8  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-16)

- **父/control、唯一 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case12_dual_split_exp569.cpp`，SHA=`0be66388ee386832f9125b29d027a41584df734135e327ee9a351cedaf6dd5f4`。只给case12 B8/KV8/L32768、40-split z8 producer把相邻两个logical split置入一个`dim3(16,2,16)`、512-thread CTA：`tz=0..7`和`8..15`各自保留独立的K/V shared half、online `(m,l,acc)`和in-place z8 tree，故不重现exp556/568的同线程双状态寄存器重叠；两半CTA仅共享一次性1 KiB raw-BF16 Q staging。page loop仍是每physical wave的同步K+V-over-PV lookahead，40个partial槽与既有vec2 reducer ABI不变，producer grid从`64×40`降为`64×20`。这是与exp568“同一256-thread CTA顺序跑两状态”不同的并发ownership前提。
- **资源与数值门禁**：独立简化resource probe曾给出`80/22/17920/0/6`，完整端到端kernel的resource binary SHA=`de3230580f4c021bae9060083671ad7fd19f974c77a279e492fe02c85e6e010f`，实际为`90 MTreg / 54 STreg / 17920 B shared / 0 stack / 5 waves`；虽保持control的5-wave档且无spill，但寄存器、shared均显著增加。normal binary SHA=`7eff4bf154f14a0536dec81b7f2340ff5e736bb7ef92fe0c7352f48d699c13a4`。`c500_case_manifest.py`与`test_kernel_logic.py`均14/14通过；同一candidate C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`逐项通过，覆盖split40的52-page边界、tail、padding-page trap、`full→short→full`与`short→full` workspace复用。
- **交错 A/B、关闭与重开边界**：从 #113889 不可变快照重新构建control，严格串行以warmup=5、iterations=20、rounds=9测试case12。candidate/control p10/p50/p90为full=`1.2123/1.2145/1.2153`、random=`1.1670/1.1697/1.1710`、boundary=`1.1484/1.1524/1.1603`；三分布都窄而稳定地慢15–21%，说明减少producer CTA数和扩大每CTA的state/shared工作无法被一次Q staging摊销。这是与改动覆盖面一致、明显且可重复的系统性本地回退，满足OJ优先规则唯一的性能否决条件，**不提交 OJ**。关闭这个 exact case12 concurrent adjacent-dual-split z8 / shared-raw-Q contract；不得只调pair边界、Q tile地址或vector类型、barrier、launch形状、split pairing或循环拼写后重投。只有能实质减少每半CTA state/QK/PV工作、改变跨请求并驻留调度或更换producer/consumer数据流的关键新前提才可重开。工作文件已恢复并核验为 #113889，OJ队列为空。

### exp570-case12-preqk-k-lookahead  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-16)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-16-experiments/cuda_case12_preqk_k_exp570.cpp`，工作文件与快照 SHA 均为`7ddc0a0438a2ec11ec02fc5a16e893d29db50805f3bf3def2725f42d696f25f0`。仅 case12 B8/KV8/L32768、40-split 的 z8 producer 新增`PREQK_K_LOOKAHEAD=true`：在当前页 QK 前，若存在下一页则同步读取下一页的四个标量 K word；它们跨当前 QK、softmax 与 PV 留在寄存器，仍在原有 PV 后的页面发布点写入下一页 `s_k`。下一页 V 仍完全保留control的 QK 后同步标量 lookahead 与同一页面发布点。split、z8 ownership、K/V shared覆盖时机、tail、partial ABI、vec2 reducer和其他case保持control。这不是已关闭的 early-K shared store、token-BSM 或 raw-BSM producer：K仍是同步全局读、寄存器寿命和 shared consumer均保持control，唯一改变是把其发起移入更长的当前页 QK/PV计算窗口。
- **资源、数值与精确长度门禁**：实际case12特化资源为`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`，与control相同。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case12同进程精确序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`逐项通过，覆盖40-split的52-page边界、tail、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：从 #113889 不可变快照fresh重建control后，严格串行以warmup=5、iterations=20、rounds=9测试case12，candidate/control p10/p50/p90为full=`1.0019/1.0030/1.0037`、random=`0.9968/1.0020/1.0055`、boundary=`0.9952/1.0020/1.0147`。三种分布只有约0.2–0.3%的中位数负信号、且低分位混合，未构成与改动覆盖范围一致、明显且可重复的系统性本地回退。本地性能仅作为风险标注；按OJ优先规则预注册一次且仅一次probe：真实OJ能否验证“把case12下一页K读取提前至当前页QK前”的数据流，使唯一目标case12获得可归因的显示档收益。不得据此扫描预取时点、K/V表达式、split、ownership、模板/grid或同源码复投；终态后保存raw、提取逐提交源码并只按case12目标作归因。

- **OJ终态、归档与关闭理由**：#114179 已终态为 **14/14 Accepted / `66.00`**，case1–14=`3/4/9/23/17/28/226/93/233/39/223/377/182/139 μs`、分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case12相对#113889仅`378→377 μs`、显示分仍60；未兑现预注册的display gain，其他case同场波动不归因。因此关闭这个 exact case12 pre-QK synchronous next-K lookahead 数据流；不得扫描预取时点、K/V表达式、split、ownership、模板/grid或同源码复投。已运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照`solutions/archive/2026-08-16-submissions/cuda_114179.cpp`、实验快照与提交前SHA均为`7ddc0a0438a2ec11ec02fc5a16e893d29db50805f3bf3def2725f42d696f25f0`。工作文件恢复#113889，OJ队列为空。

### exp571-case8-runtime-row16-weight-shuffle  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case8_runtime_row16_weight_shuffle_exp571.cpp`，SHA=`5f290b14ed5cb23bdd5c3ac608ef0da07c41903fb99d6dcc36dfab850addc19c`。只给case8 B16/KV4/L4096、14-split 的实际 fused-tail group8 reducer新增`RUNTIME_ROW16_WEIGHT_SHUFFLE=true`：rolled accumulator loop的每个动态source `(m,l)` weight handoff 从`__shfl_sync(..., s, 16)`换为MACA header提供的`__shfl_sync_16(..., s)`。后者以runtime `s % 16`选择row16 `mov_shfl` mode；producer、partial ABI、FP32 metadata、max/LSE row reduction、grid、output ownership及其他shape完全保持control。它不是exp310的14-way fully-unrolled reducer，也不是exp559/560/561的静态source/live-prefix模板扫描；唯一新前提是未经production验证的厂商动态source row16 lowering。
- **资源与数值门禁**：`-resource-usage` 的实际candidate group8实例为`32 MTreg / 24 STreg / 0 B shared / 0 stack / 8 waves`，而control同一case8实例为`66/24/0/0/7`，无spill且驻留提高；因此不能仅凭寄存器数拒绝。`c500_case_manifest.py`、`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case8同进程精确序列`4096→1,2,15,16,17,303,304,305,607,608,609,911,912,913,4095→4096`全部通过，覆盖14-slot live-prefix、page/tail、padding-page trap及`full→short→full`/`short→full`复用。
- **交错 A/B、关闭与重开边界**：相对从#113889重建的control，warmup=5、20 iterations、9 rounds的candidate/control p10/p50/p90为full=`1.0126/1.0163/1.0191`、random=`1.0094/1.0151/1.0223`、boundary=`0.9978/1.0370/1.0598`；full的21 rounds×100 iterations复测仍为`1.0105/1.0169/1.0200`。三分布中位数均回退，full复测确认约1.7%的负信号，不是单次资源/计时偶然。该runtime branch/mode selection虽显著减寄存器，却在实际case8 reducer产生覆盖一致、明显且可重复的系统性回退，满足OJ优先规则唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case8 `__shfl_sync_16` runtime-source weight handoff；不得只改mask、source表达、mode选择、模板/loop拼写或同源码复投。只有reducer consumer ownership、partial格式或后端能提供无runtime选择的不同动态source primitive时才可重开。工作文件已恢复并核验为#113889，OJ队列为空。

### exp572-case6-static-three-page-live-split-ceil  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case6_static_pages_per_split_exp572.cpp`，SHA=`6cb8a720e61ad14922e8769a5a1d1424b4a42ae1b6531b8ae72a9fa17c21ddfd`。仅 case6 B16/KV8/L362、8-split 的 group8 reducer新增`STATIC_PAGES_PER_SPLIT=3`：原有runtime `live_splits=min(n_split, ceil(valid_pages / pages_per_split))`在这个固定三页 partial contract 下，改为`min(n_split, __umulhi(valid_pages + 2, 0xAAAAAAABu) >> 1)`。producer、每个三页 split 的映射、partial ABI、max/LSE、output ownership、grid、其他case和固定case7 static-weight reducer均保持#113889。它不是对已关闭case6 FP16x2 metadata ABI的重投：只改变最终consumer计算已有的live-prefix长度，并在LLVM中消除该exact specialization的runtime除法。
- **资源、数值与精确长度门禁**：实际case6 reducer资源由control的`66 MTreg / 26 STreg / 0 B shared / 0 stack / 7 waves`变为`60/26/0/0/8`，无spill且提升一档驻留；除预期`valid_pages / 16`外，精确reducer LLVM没有`udiv`。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random均14/14、finite、100% tolerance。case6同进程精确复用序列`362→1,2,15,16,17,47,48,49,95,96,97,143,144,145,191,192,193,239,240,241,287,288,289,335,336,337,361→362`全通过，覆盖1–8 live split、page/tail、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113889 control、warmup=5、20 iterations、9 rounds，candidate/control p10/p50/p90为full=`0.9897/0.9963/1.0070`、random=`0.9875/0.9938/1.0051`、boundary=`0.9751/0.9894/1.0348`；full的21 rounds×100 iterations复测为`0.9796/0.9909/1.0040`。本地中性到轻微正向，只作为辅助证据；按OJ优先规则预注册一次且仅一次probe：固定三页case6 reducer live-split ceil specialization能否使#113889的唯一目标case6 `28 μs/63分`取得可归因 display-tier 收益。不得据此扫描magic常数、cast、ceil表达、reducer模板/grid或同源码复投；终态只按case6目标归因。
- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`6cb8a720e61ad14922e8769a5a1d1424b4a42ae1b6531b8ae72a9fa17c21ddfd`后只创建 **#115574**。它为 **14/14 Accepted / `66.14`**，case1–14=`3/4/9/22/17/28/225/94/233/38/224/371/181/139 μs`，分数=`92/90/83/73/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case6保持#113889的`28 μs/63分`，未兑现预注册display gain；case4的`23→22 μs/72→73分`和case13的`182→181 μs/56→57分`并不在候选覆盖范围，只能视为 timing-tier 刷新，不能与case6的资源改善拼接成因果收益。已运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照`solutions/archive/2026-08-17-submissions/cuda_115574.cpp`、实验快照与提交前SHA均为`6cb8a720e61ad14922e8769a5a1d1424b4a42ae1b6531b8ae72a9fa17c21ddfd`。因此拒绝并关闭这个 exact case6 static-three-page live-split ceil specialization；不得扫描magic常数、cast、ceil表达、reducer模板/grid或同源码复投，只有split contract、producer/reducer ownership或后端能力出现实质新前提时才可重开。工作文件恢复#113889，OJ队列为空。

### exp573-case12-split-wide-page-table-pid-cache  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case12_split_pid_cache_exp573.cpp`，SHA=`1d9e6705422408b3af2e7cb70c6813fdd363fb4a40c36ee84b5762af5cbd93a0`。仅 case12 B8/KV8/L32768、40-split 的z8 producer在原本空闲的256B `s_md` 后缀预载每个split的有效page-table PID；初始页、热循环的next-page与fused tail全都从共享cache取PID。它改变了整段PID存储/数据流：消去热路径对global page-table的重复依赖，而非已关闭的逐页lane-owner broadcast、PID读取时点或表达式变体；QK/PV、K/V loader、split、partial ABI、reducer、grid、ownership及其他shape保持control。
- **资源、数值与精确长度门禁**：实际case12特化资源从control的`82 MTreg / 50 STreg / 8448 B shared / 0 stack / 5 waves`变为`84/44/8448/0/5`，无spill且保持驻留档。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance。case12精确split/tail、padding-page trap及同进程`full→short→full`/`short→full` workspace复用全部通过。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113889 control、warmup=5、iterations=20、rounds=9，candidate/control p10/p50/p90为full=`1.0025/1.0034/1.0049`、random=`1.0042/1.0061/1.0072`、boundary=`0.9948/1.0013/1.0064`；full的21 rounds×100 iterations复测=`1.0032/1.0036/1.0044`。轻微本地负信号只作为风险标注，未构成覆盖一致、明显且可重复的系统性回退；按OJ优先规则预注册一次且仅一次probe：整段PID cache能否使#113889的唯一目标case12 `378 μs/60分`取得可归因display-tier收益。不得据此扫描cache布局、预载时点、barrier、PID读取表达式、模板/grid或同源码复投。
- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`1d9e6705422408b3af2e7cb70c6813fdd363fb4a40c36ee84b5762af5cbd93a0`后只创建 **#115590**。它为 **14/14 Accepted / `66.00`**，case1–14=`3/4/10/23/17/28/226/94/235/39/222/376/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113889从`378→376 μs`，但显示分仍60，未兑现预注册display gain；其他case同场波动不归因。已运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照`solutions/archive/2026-08-17-submissions/cuda_115590.cpp`、实验快照与提交前SHA均为`1d9e6705422408b3af2e7cb70c6813fdd363fb4a40c36ee84b5762af5cbd93a0`。因此拒绝并关闭这个 exact case12 split-wide page-table PID shared cache；只有页面数据流、producer/consumer ownership或后端能力出现实质新前提时才可重开。工作文件恢复#113889，OJ队列为空。

### exp574-case13-exact-lazy-page-max  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case13_lazy_page_max_exp574.cpp`，SHA=`865de0bcac12653d7d4594a9c1c78d3041a0e3106f581d6098253779eeaabf8b`。仅 case13 B1/KV8/L58966、65-split 的`paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`在每个full page的已有owner score后添加`__any_sync(~0ULL, !(owned_score <= reference))`；`reference`按既有`tx&2` head ownership选择精确`m0/m1`。整条physical wave无命中时直接令`m_page0/1=m0/1`，跳过两次原生page-max broadcast及rescale；任一head、ty或z命中时走原有`owned_page_max`和两次broadcast。首个full page因`m=-Inf`自然命中，fused tail仍是未改exact路径。这是KV8 z8 owner-score→state-flow的真实变化，并且与case14 exp466的`m+8` deferred-reference guard不同：本轮只在每个score都不超过当前**精确**`m`时走safe path，数学不改变。
- **静态资源与后端门禁**：`-resource-usage`的实际case13 candidate为`80 MTreg / 48 STreg / 8448 B shared / 0 stack / 6 waves`，对照fresh #113889的`82/48/8448/0/5`，无spill且提升一档驻留。candidate LLVM 实际specialization保留`llvm.mxc.fcmp.i64.f32` vote及条件fallback中的两处原生`mov.shfl` page-max broadcast；无命中分支的`m_page`直接来自既有`m`，不是源码同义改写。
- **数值、精确长度与复用门禁**：`c500_case_manifest.py`、`test_kernel_logic.py`均14/14通过；同一candidate C500二进制的14-case full、boundary、random（seed=`20260809`）均14/14、finite、100% tolerance match。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全部通过，覆盖首页、full/tail、57-page split、64→65 live-split、合法padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B、关闭与重开边界**：相对fresh #113889 control、严格串行warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`1.0212/1.0276/1.0305`、random=`1.0418/1.0454/1.0493`、boundary=`0.9808/0.9962/1.0272`；full 21 rounds×100 iterations复测仍为`1.0244/1.0267/1.0325`。full与random均为窄且清晰的覆盖一致回退，强复测重复full约2.7%回退；6-wave资源改善不能抵消vote/分支成本。这满足OJ优先规则中唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case13 full-wave owner-score exact-`m` lazy-page-max contract；不得只扫vote mask/row scope、reference、branch/fallback拼写、模板/grid或同源码复投。只有score/state consumer ownership、跨请求数据流或后端vote能力发生实质改变时才可重新提出。工作文件已恢复并核验#113889，OJ队列为空。

### exp575-case13-v-register-direct-consumer  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case13_v_direct_consumer_exp575.cpp`，SHA=`fbb935581af05092ac23c92fbd27b36abe65a8492f49caaec86457487a5698f1`。只给 case13 B1/KV8/L58966、65-split 的z8 producer新增`DIRECT_OWN_V_REGISTER`：每个`ty`把当前owned token的V保存在四个scalar寄存器，先直接完成own-token PV，再在peer token仍从既有shared-V完成PV期间滚动读取下一页V到同一寄存器，随后照旧发布给peer。K路径、split、partial/reducer ABI、tail、grid、其他case保持 #113889；这是真实的V producer/consumer/lifetime改动，不是已关闭的K dead-half或page-max路径重投。
- **静态资源与数值门禁**：重新从冻结源码以`-resource-usage`编译，实际case13 `paged_decode_case13_kv8_headpair_z8_kernel<true,true,false,true>`为`94 MTreg / 54 STreg / 8448 B shared / 0 stack / 5 waves`，control `<true,true,false,false>`为`82/48/8448/0/5`；无spill但两类寄存器均明显上升。`c500_case_manifest.py`与`test_kernel_logic.py`通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance。case13同进程序列`58966→1,2,15,16,17,911,912,913,1823,1824,1825,3647,3648,3649,58351,58352,58367,58368,58369,58383,58384,58385,58965→58966`全通过，覆盖57-page split、64→65 live-split、padding-page trap和`full→short→full`/`short→full` workspace复用。
- **交错 A/B、关闭与重开边界**：相对fresh #113889 control、严格串行warmup=5、20 iterations、9 rounds，case13 candidate/control p10/p50/p90为full=`1.2380/1.2413/1.2536`、random=`1.2431/1.2469/1.2514`、boundary=`1.0081/1.0232/1.0854`；full的21 rounds×100 iterations复测仍为`1.2376/1.2402/1.2457`。full与random均稳定约慢24%，强复测重复，boundary也未显示正向；这是与case13 V-register direct-consumer覆盖一致、明显且可重复的系统性回退，满足OJ优先规则唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case13 direct-own-V-register rolling pipeline；不得只扫direct/shared PV顺序、next-V load时点、scalar packing、`ty` owner、模板/grid或同源码复投。只有V consumer ownership、跨请求数据流或独立register-load后端能力出现实质新前提时才可重开。工作文件已恢复并核验为#113889，OJ队列为空。

### exp576-case4-distributed-pv-exp2  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-17)

- **父/control、唯一差异与机制**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case4_distributed_pv_exp576.cpp`，工作文件与快照 SHA=`f69fb2a38a14f78bd71a4b6fe0c623cadae64445334f037c8c03d82eb9e0f353`。只给 case4 B64/KV8/L64 的固定四页`process_case4_fixed_full_page`路径改变PV weight生成：同一`ty`行的16条lane本来各自重复计算四个相同的`exp2(score[j]-m_new)`；现在仅`tx=0..3`分别计算其中一个，再以`native_row16_broadcast<0/1/2/3>`分发给原有逐lane V/PV consumer。短长度generic fallback、BSM时序、QK、online state、split、output及所有其他case保持control。这是每页从64次row-redundant `exp2`压缩为4次的实际PV producer/consumer数据流变化，不是已关闭的case4最终native-STG store契约。
- **资源、correctness与精确长度门禁**：fresh `-resource-usage` 的实际case4 token-parallel实例control/candidate均为`74 MTreg / 44 STreg / 8320 B shared / 0 stack / 6 waves`，无spill或驻留回退。`test_kernel_logic.py`与`c500_case_manifest.py`通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance。case4同进程序列`64→1,2,15,16,17,31,32,33,47,48,49,63→64`也全部通过，覆盖四页边界、tail、padding-page trap及`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：从冻结#113889 control和候选二进制严格串行执行case4（warmup=5、iterations=20、rounds=9），candidate/control p10/p50/p90为full=`0.9530/0.9951/1.0125`、random=`0.9965/0.9986/1.0191`、boundary=`0.9940/1.0006/1.0186`。三分布均处于噪声级、没有与case4覆盖一致的明显且可重复系统性回退；本地性能只作风险标记。按OJ优先规则预注册一次且仅一次probe：该case4 distributed-PV-`exp2`数据流能否使#113889的唯一覆盖目标case4 `23 μs/72分`得到可归因的display-tier改善。不得把本次probe扩展为source lane、broadcast表达、V/PV顺序、模板/grid或同源码扫描；终态后仅按case4目标归因。

- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`f69fb2a38a14f78bd71a4b6fe0c623cadae64445334f037c8c03d82eb9e0f353`后只创建 **#115685**。它为 **14/14 Accepted / `66.07`**，case1–14=`3/4/9/23/17/28/227/93/238/38/222/373/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case4保持#113889的`23 μs/72分`，没有预注册的display收益；其余case的同场波动不归因。已运行`tools/archive_cuda_submissions.py`；raw内嵌源码、逐提交快照`solutions/archive/2026-08-17-submissions/cuda_115685.cpp`、实验快照与提交前SHA均为`f69fb2a38a14f78bd71a4b6fe0c623cadae64445334f037c8c03d82eb9e0f353`。因此关闭这个 exact case4 distributed-PV-`exp2` producer/consumer contract；不得扫描owner lane、broadcast表达、V/PV顺序、模板/grid或同源码复投。只有PV consumer ownership、跨请求数据流或独立后端能力出现实质新前提时才可重开。工作文件已恢复并核验#113889，OJ队列为空。

### exp577-case3-sparse-single-token-tail-loader  (CORRECT / LOCAL SYSTEMATIC REGRESSION / NO OJ / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case3_sparse_single_tail_loader_exp577.cpp`，SHA=`291b3094ea09a76e8cba279d753bfef42aed67656409421889faf8daa97ae9bc`。仅 case3 B16/KV4/L17 的现有单 split、BSM combined/direct-output producer，在实际`cache_seqlens[b]==17`的第二页改为由原有`(tz=0,ty=0)` group同步搬运唯一 live token 的 K/V row；原路径会搬运全部16行。K 在当前页QK后发布，V 在当前PV后发布，并以CTA barrier完成，再跳过下一轮不存在的BSM wait。任何非17实际长度继续control的完整行 loader、QK/PV、state、direct output和其他case保持不变。这是利用精确一token tail 的加载/consumer数据流变化，而非已关闭的row16 QK或BSM wait拼写重试。
- **资源、数值与精确边界门禁**：实际case3 producer由control的`92 MTreg / 48 STreg / 8320 B shared / 0 stack / 5 waves`变为`96/54/8320/0/5`，无spill但两类寄存器上升。`test_kernel_logic.py`为14/14；同一candidate C500 binary 的full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance。case3同进程序列`17→1,2,15,16,17,1→17`全部通过，覆盖完整两页、一token tail、短路径、padding-page trap及`full→short→full`/`short→full`复用。
- **交错 A/B、关闭与重开边界**：相对fresh #113889 control、严格串行warmup=5、iterations=20、rounds=9，candidate/control p10/p50/p90为full=`1.0164/1.0231/1.0509`、random=`1.0157/1.0243/1.0552`、boundary=`1.0290/1.0313/1.0334`。三个覆盖分布均清晰回退（p10也大于1），与新增同步及资源增长一致，满足OJ优先规则唯一的本地性能否决条件，**不提交 OJ**。关闭这个 exact case3 sparse-one-token tail K/V loader and extra-barrier contract；不得只扫描tail loader backend、barrier、row owner、K/V发布时点、模板或同源码复投。只有tail consumer ownership、独立低开销异步加载后端或跨请求数据流出现实质新前提时才可重开。工作文件已恢复并核验为#113889，OJ队列为空。

### exp578-case12-single-split-raw-bf16-shared-q  (CORRECT / OJ ACCEPTED / REJECTED / CLOSED, 2026-08-17)

- **父/control、唯一差异与 changed precondition**：从 #113889 / exp559（SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）分叉；完整候选冻结为`solutions/archive/2026-08-17-experiments/cuda_case12_single_split_shared_q_exp578.cpp`，提交前工作文件、raw内嵌源码和逐提交快照 SHA 均为`79fa38481525e815ca3fbbf4cc9f527648a10d64c8c12519f2aabfc0d07f51cf`。仅 case12 B8/KV8/L32768、40-split 的单logical-split z8 producer新增`STAGE_Q_ONCE=true`：在既有split有效性判断之后，`tz==0`的32个线程写入四个GQA head的64个raw-BF16 `uint4` Q向量；一次CTA barrier后全部8个z分区从该1 KiB tile读取自己的两头Q，再沿用原每z FP32 Q、同步K+V-over-PV、page loop、z-state tree和partial写出。K/V、split、partial ABI、reducer、grid、output与其他shape保持#113889。它不同于exp443的逐页shared MMA-Q、exp247的KV4/FP32 shared-Q和exp568/569的成对split Q lifetime：本轮只去除同一single-split CTA内八个z的重复Q global loads，不让两个logical split或两个状态共存。
- **资源、correctness、精确长度与复用门禁**：实际case12特化 control/candidate=`82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves → 82/52/9472/0/5`，无spill且驻留档不降。`c500_case_manifest.py`和`test_kernel_logic.py`均14/14通过；同一candidate binary的C500 full、boundary、random（seed=`20260809`）均14/14、finite且100% tolerance match。case12同进程序列`32768→1,2,15,16,17,831,832,833,1663,1664,1665,16383,16384,16385,32767→32768`全部通过，覆盖1/2/40 live split、page/tail、padding-page trap与`full→short→full`/`short→full` workspace复用。
- **交错 A/B 与预注册 OJ 问题**：相对fresh #113889 control、warmup=5、iterations=20、rounds=9严格串行，candidate/control p10/p50/p90为full=`0.9973/0.9990/0.9996`、random=`0.9983/1.0013/1.0043`、boundary=`0.9913/0.9980/1.0001`。本地仅为混合噪声级信号，未形成与覆盖范围一致、明显且可重复的系统性回退；按OJ优先规则预注册一次且仅一次probe：该single-split raw-BF16 shared-Q producer/consumer数据流能否使#113889的唯一目标case12 `378 μs/60分`取得可归因display-tier收益。不得把本次probe扩展为writer z、tile地址/vector layout、barrier、模板/grid或同源码扫描。
- **OJ终态、归档与关闭理由**：确认队列空闲、dry-run后与实际POST前工作文件 SHA 均为`79fa38481525e815ca3fbbf4cc9f527648a10d64c8c12519f2aabfc0d07f51cf`后只创建 **#115744**。它14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/226/93/236/39/223/371/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113889从`378→371 μs`，但显示分仍60；同档时延不能建立可归因display收益，未覆盖case同场波动也不归因。因此关闭这个 exact case12 single-split raw-BF16 shared-Q producer/consumer contract；不得扫描writer z、tile address/vector layout、barrier、模板/grid或同源码复投。只有Q consumer ownership、跨请求数据流或独立后端能力出现实质新前提时才可重开。已运行`tools/archive_cuda_submissions.py`；`results/raw/cuda_115744_raw.json`、逐提交快照和实验快照 SHA 一致，工作文件随后恢复#113889，OJ队列为空。
