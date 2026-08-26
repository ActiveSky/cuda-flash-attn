# Goal：MetaX C500 FlashAttention 打榜前三

持续优化本仓库的 XPUOJ Contest 11 FlashAttention paged KV-cache decode CUDA/MACA 实现，直到有一份 14/14 Accepted 提交达到或超过 leadboard.md 记录的第三名总分。

## 当前起点

| 项目 | 当前值 |
|---|---|
| 结构性 control | #124611 / exp666 / 66.00 / 14/14 Accepted |
| control SHA-256 | 3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe |
| 历史最高 timing 样本 | #115574、#116965 并列 / 66.14；不是结构性 control |
| 最新安全 probe | #125788 / exp710 / 14/14 Accepted / 65.57；未胜出 control，暂不切换 |
| 动态执行状态 | 不在本文件固化；每次 session/压缩后实时查询 OJ 队列、活跃 subagent 和工作文件 SHA；最新逐提交事实见 results/cuda_result.md |
| 第三名门槛 | 69.64 |

详细 OJ 事实见 results/cuda_result.md；本地实验和关闭依据见 notes.md。不要在本文件追加逐实验过程。

## 当前阶段焦点

优先真实改变 memory consumer、producer/reducer/finalizer ownership、storage lifetime 或跨请求数据流的机制。case7、case11、case12 等长路径只是当前观察范围，不在本文件固定实验顺序；主 agent 根据最新 OJ 反馈动态决定下一个 target。`AGENTS.md` 只保留宏观方向；具体候选、OJ 事实和反证分别维护在 `results/cuda_result.md` 与 `notes.md`，旧失败不得被自动解释成永久禁区。

exp710 的尾页 padding 安全修复必须由从 #124611 分叉的候选继承；在完成 random、split 边界和 workspace reuse 等完整覆盖前，只把它视为安全参考，不把它提升为新 control。工作文件保持当前结构性 control。

## 执行权限与方法

- 先完整阅读 AGENTS.md，并将其中的真值优先级、正确性语义底线、OJ 闭环、文件边界和多 agent 规则视为强制要求。
- 因为任务运行时间很长，新 session 或上下文压缩后必须实时核验 subagent、OJ 队列和工作文件状态，并围绕当前 target 定向检索历史；不要把旧 `PENDING` 或局部关闭结论自动当成当前任务。
- 本 goal 授权主 agent：对有明确源码差异或复测目的、target/观察范围且达到最低安全门槛的候选，决定并批准及时的串行 OJ probe；不要求先证明全新结构机制或本地性能收益。实际命令可由主 agent 或其明确指派的 subagent 执行。
- 主 agent 只负责研究方向、决策适配、任务拆分、候选准入、证据复核、OJ 时序、control 切换和最终归因。除即时、不可独立的状态核验和证据复核外，检索、实现、编译、测试、benchmark、归档、OJ 命令和记录更新都交给边界清晰的 subagent 任务执行；无法安全委派时，主 agent 先重新划分任务和风险边界。
- subagent 只执行主 agent 明确派发的任务，不自行改变方向、扩大范围、批准候选、决定 OJ 时机、切换 control 或作最终归因。经明确授权，subagent 可以修改指定文件并执行 C500、归档或 OJ 命令；每个 subagent 都不得创建、调用或管理其他 subagent。
- 同时最多四个活跃、单层 subagent。工作文件、真实 C500、OJ 队列和共享记录必须由一个明确执行者持锁串行操作；任务完成、失败、被替代或不再需要时立即收集结论并回收。
- OJ 是真实编译、运行、correctness、性能和 display tier 的最终反馈；本地 timing、资源数字、A/B、本地性能收益、覆盖缺失或本地环境不可用只作辅助诊断，不能单独阻止 OJ。探索性 probe 的候选否决条件只有编译失败、确定 correctness 问题或明显非法 launch/resource 风险；某项 smoke 或扩展本地验证尚未完成本身不是前置门槛。网络、API、限流等平台提交故障只影响操作恢复和重试时机，不否决候选。高风险 workspace、split、tail、padding 或跨调用状态改动可安排更强 correctness，但只有验证实际发现确定错误或非法风险时才阻止 probe；候选切换为 control 前，GPU 可用时应完成短长度、页/split 边界、random、padding trap 和 workspace reuse 等覆盖；当前无 GPU 时不得把覆盖缺失作为绝对阻塞，可依据 OJ 14/14 与必要安全证据判断并记录未覆盖风险，未来换到有 GPU 的 host 后回补。
- 一定以 OJ 的最终反馈作为实验调整的核心。候选达到最低安全门槛后应及时进行串行 OJ probe；不要求先证明本地性能收益或完成全量本地覆盖。允许主 agent 为确认线上方差、复核异常结果或验证 changed precondition 有目的地复投相同源码或相关已试过合同；同一源码的复测单独登记为新的 probe，不引入人为频率限制，但不得无目的刷提交。
- OJ 是性能和 display tier 的最终反馈，提交保持宽松而严格串行：除平台明确返回的限流或服务故障外，不设置每日次数上限、提交间隔、冷却时间、固定复测轮数或人为等待；上一笔进入终态并确认无在途且提交身份无误后即可立即推进下一提交，同一天可以连续进行多次独立 probe。该最低确认不要求先归档、长篇复盘或完成额外本地性能实验。任何时刻最多一笔非终态提交，Pending/Running 不取消、不并行重投；每个已批准的 probe（同一源码的有目的复测也视为新的 probe）只调用一次实际 `--submit`，拿到 submission ID 后只能继续监看同一 ID，命令超时也不得再次提交。若 POST 超时、断连或未返回 submission ID，先查询最近提交/队列恢复这次请求的身份，身份未厘清前不得再次 POST；不能把不确定状态当作“未提交”。串行只约束线上 POST/队列；在途期间可继续实现或做本地辅助验证，但不得创建第二笔提交、改动冻结源码或破坏冻结证据。raw/SHA 归档和详细复盘可随后补写，不得拖延下一次以 OJ 反馈为核心的 probe。
- 排名只读取用户维护的 leadboard.md，不主动联网刷新。

## 终止条件

只有 14/14 Accepted 且总分达到或超过当时 leadboard.md 第三名门槛，才可将本 goal 标记为完成。分数暂时不升、候选失败、OJ 排队或本地环境受限都不是终止条件；仍有安全、独立的研究或验证工作时继续推进。
