# MetaX C500 FlashAttention 作战手册

本仓库优化 XPUOJ Contest 11 的 FlashAttention paged KV-cache decode CUDA/MACA 实现。本文件是长程任务和上下文压缩后的短入口：只回答“当前事实是什么、接下来往哪里走、谁负责判断、哪些底线不能破坏”。它不是实验总账，也不维护逐候选黑名单。

## 1. 启动与上下文恢复

每次新 session 或上下文压缩后按以下顺序恢复：

1. 阅读 `AGENTS.md` 和 `goal.md`，获得当前快照、宏观方向与职责边界；
2. 实时检查 subagent 状态、OJ 队列和工作文件 SHA，不沿用压缩前的动态状态；
3. 根据当前 target，在 `results/cuda_result.md` 和 `notes.md` 中定向检索相关提交、机制和反证；不要默认把两份历史总账全文装入当前决策上下文；
4. 发生矛盾时，再核对对应的 raw JSON、不可变提交源码和绑定 SHA 的原始证据。

历史记录中的 `PENDING`、候选建议或关闭结论都只是当时状态。除非当前快照和实时检查仍然支持，不得自动把它们当作当前任务；旧失败只否定原实验前提，不自动禁止新的机制。

文档职责：

| 文档 | 内容 |
|---|---|
| `AGENTS.md` | 当前快照、宏观方向、长期底线和协作流程 |
| `goal.md` | 长期目标、授权和终止条件 |
| `results/cuda_result.md` | OJ 逐提交事实、case 数据、源码归档和 control 归因 |
| `notes.md` | 候选实现、本地资源、correctness、A/B、失败反证和重开论证 |
| raw JSON / 不可变源码 | 冲突时的最终事实来源 |

维护时保持本文件短小：control、研究优先级、全局底线或协作方式变化时更新这里；逐实验数字、SHA、实现细节和逐候选关闭/禁止项只写入 `results` 或 `notes`。

## 2. 当前快照

| 项目 | 当前值 |
|---|---|
| 结构性 control | `#124611 / exp666 / 66.00 / 14/14 Accepted` |
| control 源码 | `solutions/archive/2026-08-24-submissions/cuda_124611.cpp` |
| control SHA-256 | `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe` |
| 历史最高 timing 样本 | `#115574`、`#116965` 并列 `66.14`；不是可归因的结构性 control |
| 最新安全 probe | `#125788 / exp710 / 14/14 Accepted / 65.57`；未胜出 control，暂不切换 |
| 当前 host GPU 能力 | 当前无可运行 GPU：`nvidia-smi` 不存在，`mx-smi` rc=2 无设备，仅有 `/dev/mxcd`（不视为 GPU）；每次新 session/换 host 必须重新核验 |
| 动态执行状态 | 不在本文件固化；每次 session/压缩后实时查询 OJ 队列、活跃 subagent 和工作文件 SHA；最新逐提交事实见 `results/cuda_result.md` |
| 工作文件 | `solutions/cuda_maca_optimized.cpp`；空闲时应与 control 字节一致，使用前必须实时核验 |
| 第三名门槛 | `leadboard.md` 中的 `69.64` |

当前 control 的新增结构性收益来自 #124611 的 case13 BF16 global partial + native row16 reducer，并继承 #113889 的 case7 收益。最新 OJ 事实以 `results/cuda_result.md` 顶部为准；详细实验状态以 `notes.md` 最新相关条目为准。

exp710 同时确认并修复了 control 在尾页 padding 读取上的安全风险；其完整 random、split 边界和 workspace reuse 覆盖尚未完成，因此只作为宏观安全参考，不作为新 control。后续从 #124611 分叉的候选必须继承该尾页安全修复；工作文件继续保持当前结构性 control。

## 3. 宏观研究地图

目标是获得可归因、能跨线上 display tier 的结构性收益，而不是拼接不同提交的偶发最好值。OJ 是性能真值，本地数据用于安全门禁、风险定位和归因。

### 3.1 已经广泛尝试过的方向

以下类别已有大量实验，精确事实和反证在 `notes.md` 与 `results/cuda_result.md`：

- 单 CTA 内的 lane、shuffle、地址、分支、局部缓存、寄存器和短路径算术调整；
- Q/K/V 与 partial/output 的 native load/store、BSM、MMA 和共享内存 handoff；
- state merge tree、partial 编码、split 聚合、finalizer 和 direct-output ownership；
- 跨 CTA/跨请求协作，以及 cluster/DSM、async movement、graph、multistream、持久缓存等后端或生命周期能力；
- case1/2 等极短路径和 case4/5/6/10 等近档单 shape 微调。

这些实验说明：在当前 control、编译器和 ABI 前提下，局部变体经常同档、资源退化或线上无收益。因此它们暂不作为默认主线，但这不是永久禁令。若所有权、存储生命周期、后端能力、调用 ABI 或硬件 lowering 的前提实质变化，主 Agent 可以重新评估。

### 3.2 下一阶段方向

当前优先观察 case7、case11、case12 等长路径，但不在入口文件固化 case 顺序。主 Agent 应以最新 OJ 反馈选择下一笔候选，并可随时调整 target。

1. **长路径的数据流与所有权。** 在 producer、partial、finalizer、reducer 或 output consumer 之间寻找能删除真实流量、同步边或重复工作的变化，具体落到哪个 case 由线上反馈决定。
2. **新的存储生命周期或后端能力。** 探索跨 wave、跨请求、独立 memory consumer、编译器 intrinsic、runtime ABI 或硬件 backend；先确认能力真实存在，再选择受益 shape。
3. **伴随机会。** 同一机制自然覆盖其他长路径或近档 case 时一并观察，不为小幅局部收益强行固定路线。

方向选择不是固定路线图。主 Agent 应结合最新线上反馈、历史反证和实现成本形成候选；如果新证据推翻当前判断，应直接改向并更新本节，而不是服从旧实验留下的细粒度限制。

## 4. 真值与正确性底线

事实冲突时按以下优先级裁决：raw JSON → raw 中的提交源码/不可变提交源码 → 当前 control 快照 → `results/cuda_result.md` → 绑定 SHA 的本地证据 → `notes.md` 解释 → build 产物或静态推断。

OJ 固定快路径为 `seqlen_q=1`、32 query heads、4 或 8 KV heads、headdim=128、page=16、causal=0、BF16 I/O、FP32 score/LSE/PV。结论不能无证据外推到 generic fallback。

任何实现都不得放宽以下正确性语义底线：

- 只按 `cache_seqlens[b]` 读取有效 KV；不得读取 block table padding；
- 保持 GQA head 映射、尾页 mask、FP32 online-softmax 和 split LSE 合并；
- 不允许 NaN、Inf、未初始化或跨调用旧 partial；`run_kernel` 内不得调用 `cudaDeviceSynchronize()`；
- 长 case reference 的 Exit 137/Killed 只表示资源失败，不能报告为数值通过。

这些是实现必须保持的语义，不等于每次 OJ 前都必须完成全量本地覆盖。当前 host 无可用 GPU：`nvidia-smi` 不存在，`mx-smi` rc=2 返回 `No available devices were discovered`，仅有 `/dev/mxcd`，不能视为可运行 GPU。本地仅做必要的 CPU/静态/源码审计及按需 compile-only、resource 或 LLVM 检查，均不得称为 GPU 验证；真实运行、correctness、性能和 display tier 以远端 OJ 为核心，本地无 GPU、覆盖缺失或无法复现不得阻止达到最低安全门槛且有明确目标的串行 probe。GPU 可用时再补齐 full、boundary、random、padding 和 workspace reuse 等覆盖；当前无 GPU 时依据 OJ 14/14 与必要安全证据判断 control，记录未覆盖风险并在具备 GPU 的环境后回补。

## 5. 候选与 OJ 闭环

主 Agent 在批准实现前，用最小记录写清：源码差异或复测目的、target case（或观察范围）和线上观察问题。无需先写完整实验报告或证明本地性能收益；一次候选尽量只验证一个主要假设。允许为了确认线上方差、复核异常结果或验证 changed precondition 而有目的地复投；同一源码的复测单独登记为新的 probe，不引入人为频率限制，但不得无目的刷提交。

候选只设最低安全门槛：源码能够编译，且没有已经确认的 correctness 错误或明显非法 launch/resource 风险。达到该门槛即可及时 probe。完整本地 correctness、全量资源审计、A/B、本地 timing、本地性能收益以及某项 smoke 是否已完成，都不是探索性 probe 的前置条件；本地环境只负责尽早暴露明显安全/语义风险，不能替代线上试验。主 Agent 可对 workspace、split、tail、padding 或跨调用状态等高风险改动安排更强 correctness，但只有验证实际发现确定错误或非法风险时才能据此阻止提交。

以下证据主要用于诊断、归因和后续调整，不是每次 OJ 提交的普遍硬门槛：

- 完整资源对照与 LLVM/codegen 审计；影响共享模板或 helper 时检查所有可达路径；
- CPU 与真实 C500 的扩展/完整 correctness 覆盖，包含受影响的 full、boundary、random、padding 和复用场景；
- control/candidate 交错 A/B，用于发现系统性风险，不用来替代 OJ 性能结论。

本地中性、回退、资源增加、A/B 噪声、覆盖缺失或本地环境不可用均不得单独否决 OJ；只有编译失败、确定 correctness 问题或明显非法 launch/resource 风险才否决候选。网络、API、限流等平台提交故障只影响本次操作的恢复与重试时机，不构成候选否决。即使本地无法复现收益，只要安全门槛已过，也应优先保留一次有明确观察目标的线上 probe。OJ 是性能与 display tier 的最终真值，本地结果只用于安全判断、风险定位和线上结果解释。

OJ 是性能与 display tier 的最终反馈；本地验证只承担安全、语义和归因辅助职责，不得替代或拖延有明确目标的线上 probe。提交节奏采用“宽松但严格串行”规则：

- 除平台明确返回的限流或服务故障外，不设置每日次数上限、提交间隔、冷却时间、固定复测轮数或人为等待；上一笔进入终态并完成最低身份确认后即可立即提交下一笔，同一天可以连续进行多次独立 probe。
- 最低确认只包括上一笔已进入终态、队列中没有其他非终态提交、待测源码与提交身份/SHA 已核对；不要求先归档、长篇复盘或完成额外本地性能实验。
- 任何时刻最多一笔非终态提交；Pending/Running 不取消、不并行重投。每个已批准的 probe（同一源码的有目的复测也视为新的 probe）只调用一次实际 `--submit`；拿到 submission ID 后，命令超时或监看中断只能继续 `--watch <同一 ID>`，不得再次提交。
- 若实际 POST 超时、断连或未返回 submission ID，先查询最近提交/队列恢复这次请求的身份；在身份未厘清前不得再次 POST。确认 ID 后只对该 ID `--watch`，不得把不确定状态当作“未提交”。
- 每次提交前实时查队列并冻结待测源码 SHA；“串行”只约束线上 POST 和队列，不阻止在途期间对隔离 experiment 文件继续实现或做本地辅助验证，但不得改动冻结源码或创建第二笔提交。raw/SHA 归档和详细复盘可在终态后补齐，不得成为等待下一次线上 probe 的理由。空闲工作文件恢复当前 control。

## 6. 主 Agent 与 subagent 分工

### 6.1 主 Agent：判断与适配

主 Agent 是唯一决策者，负责：

- 读取当前事实，选择和调整研究方向；
- 拆分任务、指定资料、写集合、资源锁和完成判据；
- 判断历史反证是否仍适用，决定候选是否准入以及需要哪些门禁；
- 批准 candidate SHA、OJ 提交时机、control 切换和最终归因；
- 复核 subagent 的关键证据，处理冲突并维护任务生命周期。

主 Agent 不把判断外包给 subagent，也不把自己当作默认执行者。除即时、不可独立的状态核验和证据复核外，检索、实现、构建、测试、benchmark、归档、OJ 命令和记录更新都应拆成边界清晰的任务交给 subagent；若暂时无法安全委派，主 Agent 先重新划分任务和风险边界。

### 6.2 Subagent：按派发范围执行

Subagent 只执行主 Agent 明确派发的任务，在指定范围内完成检索、实现、构建、静态检查、correctness、benchmark、归档或记录，并报告命令、改动和证据。

Subagent 不得自行改变研究方向、扩大任务范围、批准或否决候选、冻结 candidate、决定 OJ 时机、切换 control 或作最终归因；发现新机会或冲突时先报告主 Agent。每个 subagent 都不得创建、调用或管理其他 subagent。

Subagent 不是默认只读：只要主 Agent 的任务明确授权，它可以修改指定文件并执行 C500、归档或 OJ 命令。权限服务于执行，决策仍归主 Agent。

### 6.3 并发、锁和回收

- 同时最多 4 个活跃 subagent，只允许一层；上限不是配额；
- 每个任务必须有单一目标、输入事实、写集合和完成判据；
- 唯一工作文件、真实 C500、OJ 队列和共享记录分别只能由一个明确执行者串行持锁；
- 新 session 或压缩恢复后先检查 agent 状态，避免重复派发；
- 完成、失败、被替代或不再需要时，主 Agent 立即收集结论并回收，不保留常驻会话。

## 7. 文件与安全

- `results/raw/`、`archive/*-submissions/`、当前 control 和第三方子模块是历史事实，禁止手工改写；
- `solutions/cuda_maca_optimized.cpp` 是唯一常用可变工作文件；候选保存为日期化 experiments 完整源码，身份绑定 SHA；
- 不读取、打印、复制、修改或提交 `tools/.env`、凭据、token、`.so`、cache、profiler 数据库或 `profiler.log`；
- 保留用户已有无关改动和实验证据，不 reset、清理或删除唯一证据；
- CompilationError、WrongAnswer、Canceled 和失败占位不是性能数据。
