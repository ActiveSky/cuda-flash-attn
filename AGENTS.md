# MetaX C500 FlashAttention 作战手册

本仓库优化 XPUOJ Contest 11 的 FlashAttention paged KV-cache decode CUDA/MACA 实现。本文件是后续 agent 的短入口：只保存当前决策、研究方向、项目规则和协作流程，不是实验日记。

## 1. 阅读顺序与记录边界

开始工作前依次阅读：

1. AGENTS.md：当前状态、研究方向、强制规则和协作流程；
2. goal.md：长期目标、OJ 授权和终止条件；
3. results/cuda_result.md：OJ 逐提交事实、case 数据和 control 归因；
4. notes.md：本地实验、资源、A/B、失败反证和 changed-precondition 论证；
5. results/raw/cuda_<id>_raw.json 与不可变提交源码：发生矛盾时的最终事实来源。

文档职责不可混用：

| 文档 | 只记录什么 |
|---|---|
| AGENTS.md | 当前 control/队列、宏观方向、稳定的关闭边界、验证与协作规则 |
| goal.md | 长期目标、权限、当前起点和终止条件 |
| results/cuda_result.md | 每次 OJ 的状态、case、提交源码、归因和 control 决策 |
| notes.md | 每个候选的实现、资源、A/B、失败原因和下一步细化 |

维护规则：

- control、最高分、研究优先级、强制约束或协作流程变化时，只更新本文件和 goal.md 中的对应短条目。
- 每次 OJ 终态更新 results/cuda_result.md、raw 和不可变提交源码；每个本地实验更新 notes.md。
- 不在 AGENTS.md 或 goal.md 追加逐实验长叙述、资源数字、A/B 表格、SHA 清单或提交流水。一个结论若需要解释，链接或指向 notes.md/results 即可。
- 新关闭项在本文件最多写一条“路线/前提/重开条件”；精确实现和反证必须留在 notes.md。

## 2. 当前决策快照

| 项目 | 当前值 |
|---|---|
| 结构性 control | #113889 / exp559 / 66.00 / 14/14 Accepted |
| control 源码 | solutions/archive/2026-08-16-submissions/cuda_113889.cpp |
| control SHA-256 | a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972 |
| 历史最高 timing 样本 | #115574 / 66.14；未形成目标 case 的可归因 display 收益，不是 control |
| 最新 OJ 终态 | #115744 / exp578 / 66.07 / 14/14 Accepted；case12 shared-Q 目标未跨档，已关闭 |
| OJ 队列 | 无在途提交 |
| 工作文件 | solutions/cuda_maca_optimized.cpp；空闲时必须与 #113889 字节一致 |
| 第三名门槛 | leadboard.md 中的 69.64；按结构性 display 基线仍约差 51 点 |

#113889 的 case7 固定三 split static row16 weight handoff 是当前唯一被接受的最新结构性收益。新候选从该不可变快照分叉；空闲工作文件恢复它。最新提交的详细事实、以及所有已关闭的 exact contract，以 results/cuda_result.md 和 notes.md 为准。

## 3. 真值、规格与安全底线

### 3.1 真值优先级

冲突时按以下顺序裁决：

1. raw JSON；
2. 从 raw 提取的逐提交不可变源码；
3. 当前 control 的不可变快照；
4. results/cuda_result.md；
5. 绑定源码 SHA 的本地资源、correctness 与交错 A/B；
6. notes.md 的解释；
7. build 产物和静态推断。

OJ 固定快路径是 seqlen_q=1、32 query heads、4 或 8 KV heads、headdim=128、page=16、causal=0、BF16 I/O、FP32 score/LSE/PV。所有结论只覆盖该快路径，不能外推为 generic fallback 支持任意 shape。

### 3.2 不可放宽的正确性规则

- cache_seqlens[b] 才是真实可读长度；block_table 的 padding slot 即使看似合法也不得读取。
- 保持正确 GQA head 映射、尾页逐 token mask、FP32 online-softmax 与 split LSE 合并。
- 覆盖长度 1、2、15、16、17、受影响 split 边界、随机变长、padding trap，以及同进程 full-short-full 和 short-full workspace 复用。
- 不允许 NaN、Inf、未初始化 workspace 或跨调用旧 partial；run_kernel 内不得调用 cudaDeviceSynchronize()。
- 长 case reference 的 Exit 137/Killed 只是资源问题，必须拆为单 case 重跑，不能报告为数值通过。

## 4. 研究方向与关闭边界

目标不是把不同提交的偶发最好 case 拼成分数，而是取得可归因、可跨 display tier 的结构性收益。距第三名仍远，优先寻找跨 shape 的数据流、ownership、lifetime 或后端能力变化；约 1 微秒的近档优化只作为辅线。

### 4.1 主线

1. KV4 长路径（主要是 case8/11/14）：关注 QK、online-state、PV、加载与 reducer 间真正的 producer/consumer ownership 或状态生命周期变化；不要只重排同一 MMA 指令、阈值或 shuffle。
2. KV8 长路径（主要是 case7/9/12/13）：关注实际长度下的 producer/partial 数据流、跨页/跨请求 pipeline、独立 memory consumer 的后端能力，或能跨 shape 复用的 partial consumer ownership。
3. 近档辅线（case4/5/6/10 等）：只能以单一、明确且可证伪的机制并行推进，不能把 timing 噪声当成可拼接收益。

### 4.2 已关闭路线的使用方式

详细 closure 在 notes.md；提出候选前必须先检索目标 case 的既有反证。下列类别在相同前提下禁止重试：

- 只调 lane、mask、阈值、模板、grid、地址表达式、cache 布局或 loop 拼写的参数扫描；
- 已验证的 reducer row/shuffle、metadata packing、native store/load、static live-split mapping 的同源变体；
- 当前 case12 的 shared-Q、PID broadcast/cache、既有 K/V native-LDG、token-BSM 与 early-K 数据流；
- 当前 case13 的 z8 tree/barrier、lazy page-max、direct-V register 与既有 partial/reducer ownership 变体；
- 已关闭的 case4 PV weight 分发和其他只改 source schedule 的短路径微调。

“关闭”只约束已有 contract。只有线程/consumer ownership、partial 格式、跨请求数据流、实际存储生命周期或独立后端能力发生实质变化，并在 notes.md 说明旧反证为何不适用，才能重开。

## 5. 实验与 OJ 验证闭环

### 5.1 候选准入

每个候选必须先写清：父源码与 SHA、唯一核心差异、预注册 target case、可证伪机制、已关闭路线的 changed-precondition 理由和唯一成功判据。一次只验证一个核心假设；不做参数扫描或同源码复投。

候选先保存为日期化 experiments 目录中的完整源码。主 agent 才能把已选候选放入唯一可变工作文件。至少完成：

- 编译和资源检查：无意外 spill、stack 或驻留回退；
- CPU 和真实 C500 correctness，覆盖 full、boundary、random、padding 与复用；
- control/candidate 严格交错 A/B，报告每轮 ratio 的 p10/p50/p90；改变 split、ownership、live-split、workspace 或 producer/reducer 合同时，三种长度分布都要覆盖。

本地 correctness、资源和覆盖范围匹配的 A/B 是安全门禁。文档、静态 codegen 和单个满长测试都不能替代它。

### 5.2 OJ 优先

OJ 是性能与 display tier 的最终真值。本地性能只用于筛选、风险定位和归因：中性、轻微回退或噪声不能阻止一个机制明确、已预注册目标 case、且已通过安全门禁的单次 OJ probe。只有与改动范围一致、明显且可重复的系统性本地回退，才可暂缓 probe；理由和复测必须写入 notes.md。

由主 agent 串行执行以下闭环：

1. 确认没有非终态 OJ，冻结 candidate SHA，并停止其他工作文件写入；
2. 运行 xpuoj_submit.py dry-run；实际 --submit 前再次核验工作文件 SHA 与预注册 SHA 相同；
3. 每次只提交一个预注册候选，始终最多一笔非终态 OJ；Pending/Running 不取消重投；
4. 终态后保存 raw、运行 archive_cuda_submissions.py、核对 raw/提交快照/SHA；
5. 更新 results/cuda_result.md 和 notes.md，按唯一 target case 归因；只有 target 因果、correctness 与结构证据都成立才切换 control；
6. 立即把工作文件恢复到当前 control，除非主 agent 已明确开始下一次集成。

## 6. 多 agent 协作与生命周期

主 agent 是唯一的调度者和集成者：它选择方向、拆分任务、维护计划、决定候选、审查证据、控制工作文件、串行 GPU benchmark，并独占 OJ 与项目记录写入。subagent 用于加速探索和执行边界清晰的子任务，不能自行改变实验路线。

### 6.1 并发与层级

- 同时最多 4 个活跃 subagent；主 agent 不计入这四个名额。上限不是配额，没有独立任务时不创建。
- 只允许一层：仅主 agent 可以创建或管理 subagent。每个委派 prompt 必须明确写“不得创建、调用或管理 subagent”。
- 新一轮委派前，主 agent 先检查活跃 agent 和写集合；若已达上限、任务重叠或当前结论已足够，先收敛而非继续派发。

### 6.2 分工与写权限

可并行的典型角色是：方向/反证检索、后端与资源审查、独立 correctness 边界设计、以及一个隔离候选实现。任务必须有单一问题、父 SHA、允许读取的权威资料、唯一产物路径和完成判据。

- subagent 默认只读；需要实现时，只能写主 agent 指定的唯一 experiments 文件或隔离目录。
- subagent 不得修改当前工作文件、control、raw、submission archive、AGENTS.md、goal.md、results/cuda_result.md 或 notes.md。
- subagent 不得读取 tools/.env，不得执行 OJ 操作，也不得并发运行真实 C500 benchmark。
- 主 agent 收到结果后，自己复核 diff、SHA、资源、correctness 和 A/B，才可选择集成。

### 6.3 及时回收

- 创建时记录任务名、目的、写集合和开始时刻；完成、失败、被替代或不再需要时，主 agent 在同一管理轮收集必要结论并立即结束/回收该 agent。
- 不把已完成 agent 保留为“以后可能有用”的常驻会话；需要新工作时重新派发一个边界清晰的任务。
- 主任务改向、取消或进入 OJ SHA 冻结窗口时，立即停止仍会写入或影响当前候选的 subagent。

## 7. 文件、安全与维护

- results/raw/、archive/*-submissions/、当前 control 和第三方子模块是历史/只读事实，禁止手工改写。
- solutions/cuda_maca_optimized.cpp 是唯一常用可变工作文件；不要创建重复 best/frozen 副本。build 文件名不能证明源码身份，结论必须绑定 SHA。
- 不读取、打印、复制、修改或提交 tools/.env、凭据、token、.so、cache、profiler 数据库或 profiler.log。
- 保留用户已有无关改动和实验证据；不得 reset、清理或删除唯一证据。
- CompilationError、WrongAnswer、Canceled 和约 36 秒失败占位不是性能数据。
