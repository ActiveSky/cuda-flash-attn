# Goal 命令：MetaX C500 打榜前三

将下面整段作为长期 goal 执行：

```text
/goal 持续优化本仓库的 XPUOJ Contest 11 FlashAttention paged KV-cache decode CUDA/MACA 实现，直到我们的有效成绩达到仓库内 leadboard.md 所记录的前三名门槛。

开始前完整阅读 AGENTS.md，并把其中的规格、正确性底线、真值优先级、文件组织、已验证结论和失败路线视为强制约束。当前选定最佳是 Accepted #105952，分数 57.43，唯一基线源码是 solutions/archive/2026-08-08-submissions/cuda_105952.cpp；solutions/cuda_maca_optimized.cpp 是唯一日常迭代文件。排名目标只根据用户复制到仓库的 leadboard.md 判断，不主动联网查询或刷新榜单；当前文件记录的第三名门槛为 66.64。若用户之后更新该文件，则直接采用文件中的新门槛。

目标与自主权限：
1. 目标不是进行一次优化，而是持续形成“假设 -> 实现 -> correctness -> 交错 A/B -> 真实 OJ -> 归档 -> 复盘 -> 下一假设”的闭环。允许进行多轮本地实验、构建、真实 C500 测试和有信息价值的 OJ 提交；用户已授权为本目标使用 --submit，不必为每次正常提交重复询问。
2. 每个首轮候选只验证一个可证伪的核心假设。先保留源码 SHA-256、唯一命名的 .so 和 control/candidate 对应关系，再解释目标 case、预期机制和观测结果。不要用分别运行的绝对 p50 代替交错 ratio，也不要把 OJ timing tier 波动强行解释为源码因果。
3. 可以提交局部收益候选，也可以为了判定本地/OJ 差异做少量诊断提交，但必须先通过完整正确性门槛，并说明该提交能回答什么问题。不得无假设地批量试参，不得把多个 loader、split、layout、reducer 改动混在首轮候选里。
4. 每次 OJ 尝试都保存 raw，运行 tools/archive_cuda_submissions.py 提取字节精确源码，并及时更新 results/cuda_result.md。Accepted、WrongAnswer、CompilationError 和无提升结果都要如实记录；有复现价值但未提交的候选归档到日期化 experiments 目录。

优先研究顺序：
1. 先把 #105835 在 case 11 达到 439 us 的 Q shared-memory 复用思路以唯一差异移植到当前 token-parallel 最佳源码，检查寄存器/shared-memory/occupancy 阈值及其他 13 个 case 的影响；随后继续研究长 KV4 case 11/14/8 的 Q staging、同步向量 loader、producer/reducer 开销和 split policy。
2. 对 case 4/5/10/14 做距离下一计分 tier 约 1 us 的低风险局部优化。不同提交的历史最佳只能当线索，必须在同一最终源码中重新验证，不能拼接计时结论。
3. 对长 KV8 case 7/9/12/13 保留 token-parallel 主架构和同步 uint4 loader 作为 control，重点减少 launch、tail、shared-state 合并和 reducer 开销；BSM async 只允许按 shape 重新 A/B，不能默认更快。
4. 在以上方向边际收益耗尽后，再基于资源报告和 profile 提出新架构假设，例如减少一次 kernel launch、减少 partial 状态流量、提高有效 occupancy 或按 shape 特化 reducer。任何新方向都必须先证明数值语义和 page-table 安全。

长期分阶段路线图：
阶段 0，重建基线与计分地图。确认 control/candidate 哈希、14-case correctness、本地交错噪声范围、每个 case 当前 tier 和下一 tier 所需时延，按“潜在得分 / 实验成本 / 正确性风险”维护候选队列。
阶段 1，先收割低风险 tier。复现并组合当前不同 Accepted 提交中 case 4/5/10/14 的局部历史最佳，每次只移植一个差异；扫描 dispatch threshold、短序列 launch、tail 分支和小 split reducer，但最终必须在同一源码上全量验证。
阶段 2，深入长 KV4。围绕 case 11/14/8 系统测试 Q reuse/staging、每 CTA head 数、token partition 数、pages per split、同步向量 K/V loader、full/tail 处理、partial 布局、register/shared reducer 和 occupancy。先探索离散邻域，再根据趋势扩大搜索，不做没有归因的笛卡尔积穷举。
阶段 3，深入长 KV8。保持同步 uint4 control，分别研究 case 7/9/12/13 的 split 粒度、head grouping、z-state 合并、tail、producer/reducer 流量和 launch 数；BSM、预取或其他 loader 只能作为按 shape 的单变量候选。
阶段 4，降低跨 kernel 成本。测量 producer、workspace 写回、reducer 和 direct-out 各自成本，研究减少 partial 数量/字节、压缩或重排 m/l/acc、单 live-split 直出、分层 reduction、按 shape 合并 launch，以及在不依赖非法跨 CTA 同步的前提下消除一次 launch 或 workspace round trip。
阶段 5，资源与代码生成。读取编译资源信息并用真实 A/B 验证 register pressure、shared-memory、occupancy、指令数、向量 load/store、分支和模板实例化的影响；分别为 B1 长序列、低 batch 和 B32/B64 高并发设计资源配置，不能用单一 occupancy 指标代替端到端时延。
阶段 6，架构级突破。如果前述微优化不足以达到 66.64，必须主动探索新的、可回退的分支，包括 alternate token/head/CTA mapping、不同 heads-per-CTA 与 token partition 组合、面向 B1 长序列的 persistent/work scheduling、多级或 CTA 内 reduction、跨 query-head 的 Q/KV 数据复用、减少 score/partial materialization，以及数学等价但状态流量更小的 online-softmax 组织。首个原型只针对一个代表 case，正确且显著获益后再扩展 dispatch。

可持续实验池：
- Dispatch：围绕 L=2/17/64、KV4/KV8、batch 和 live-split 边界测试邻近阈值；每个阈值候选必须解释影响哪些 OJ case。
- CTA layout：测试 heads-per-CTA、tx/ty/tz、token partition、每线程维度数和每轮 token 数；同时记录 threads、register、shared-memory 和 occupancy 变化。
- Loader/staging：分别测试 Q 常驻 register/shared、K/V 同步向量宽度、对齐访问、page/tail 分离、预取和单/双 staging；不得把 loader 与 layout 首轮混改。
- Softmax/state：测试条件 max 更新、m/l/acc 保存格式、z-state 合并位置、空 split 跳过和 live-split reducer；所有变换都要写出稳定合并等价关系。
- Split/reducer：按 case 扫描有理论依据的邻近 split 点，测试 grouped head、register/shuffle/shared reducer、direct-out 和两级 reduction；避免重复已经显示单调回退的范围。
- Launch/workspace：量化每次 launch 和每字节 partial 流量，评估合并 full/tail、producer/reducer 或持久调度的收益上限，再决定是否实现复杂原型。
- 编译器后端：比较模板常量、unroll、向量类型、restrict/alias、安全 shuffle 和资源限制生成的代码；编译成功不等于运行正确，静态指标改善不等于性能改善。
- 组合阶段：两个方向各自唯一差异获益后，才在当前最佳上组合；组合必须重新跑全量 correctness 和全 case A/B，检查资源阈值导致的非线性交互。

已验证结构与探索边界：token-parallel CTA、FP32 global-max online softmax、cooperative/live-split/grouped reducer、packed FP32 热循环、full/tail 分离、KV4 Q staging、CTA 内 z-state 合并，以及 L=1/L=2 专用路径和 L>=17 token-parallel dispatch，是新实验的默认强基线，不是永远不可替换的教条。微优化阶段没有反证时保留它们；架构阶段可以建立隔离候选替换其中一项，但必须以当前最佳为 control，并先通过正确性和代表 case A/B。不要无假设重试 lane-dependent shuffle、8-lane subgroup、raw WMMA、native packed BF16 conversion、forced CUTE、MMA-QK/PV、双 shared-memory buffer、grouped-V PV、K transpose、4 KB sequential staging、duplicated full-page branch、lane-0-only partial store、launch_bounds 第二参数或长 KV8 默认 BSM。只有当线程布局、数据组织、后端能力或其他关键前提已经改变时才允许重开失败路线，并必须先写明“旧实验为何不再能否定新假设”。

实验管理与停滞转向：
1. 为每个候选记录实验 ID、父源码/哈希、唯一差异、目标 case、预期机制、correctness、A/B p10/p50/p90、OJ ID/结果和最终决定。未记录归因的候选不计入有效进展。
2. 同一个参数或微假设连续 3 个有效候选均无目标收益时，停止继续细扫并记录边界；同一研究主线连续 5 个正确候选既没有稳定本地收益、没有跨 OJ tier、也没有产生可改变下一步的新信息时，切换到另一主线。
3. 每完成 8–12 个有效候选做一次阶段复盘：更新每 case 瓶颈、已关闭区间、当前最佳、预计得分空间和下一阶段队列；优先选择预期得分高且能区分机制的实验，而不是按文件名顺序试验。
4. 已关闭方向只有在新 profile、OJ 反例、编译器变化或关键设计前提改变后才重开。重开实验从最小代表 case 开始，不直接恢复大范围参数扫描。
5. 某候选目标 case 获益但其他 case 回退时，先判断能否用已有 shape 字段安全 dispatch，再测试组合；不能直接拿不同二进制的逐 case 最佳计时相加。
6. 微优化队列耗尽不是结束条件，而是进入阶段 4–6 的触发器。至少并行维护一条低风险 tier 路线和一条架构突破路线，避免长期困在单一局部最优。

每个候选的强制门槛：
1. 运行 CPU 语义回归；构建后对同一个 .so 完成真实 C500 full-length、boundary、random、padding-page trap，以及改动涉及 workspace 时的同进程 full-short/full 复用测试。任何 numerical mismatch、NaN/Inf、非法 page 预读或旧 workspace 依赖都禁止提交。
2. 对当前最佳不可变提交快照与候选做多轮交错 A/B，报告目标和关键非目标 case 的 ratio p10/p50/p90。小于测量噪声的变化只能记为中性；可能换 tier 的微小收益可进入 OJ 验证，但必须标明不确定性。
3. 真实提交前先执行 dry-run，确认提交的是 solutions/cuda_maca_optimized.cpp 并记录 SHA-256；提交后等待终态并核对 raw 内嵌源码哈希。CompilationError、WrongAnswer 和约 36 秒失败占位不是性能数据。

不可突破的约束：
- 不修改 results/raw/、任何 archive/*-submissions/ 快照、solutions/cuda_maca_version.cpp、third/flash-attn 或 tools/.env；不读取、打印、复制或提交凭据。
- 不再创建内容重复的 cuda_maca_best.cpp、cuda_maca_frozen.cpp 或其他“稳定最佳”副本。当前最佳始终直接指向某个不可变提交快照；新最佳出现后只更新 AGENTS.md/results 报告中的 ID 和路径，并让空闲状态的 solutions/cuda_maca_optimized.cpp 与它一致。
- 不覆盖用户的无关工作树改动，不删除实验的唯一证据，不提交 .so、cache、profiler 数据库或 profiler.log，不在 run_kernel 内增加 cudaDeviceSynchronize()。
- 结论只覆盖 OJ 固定 fast path；不得把 generic fallback 描述为任意 shape 已正确。

进度策略：每轮都从尚未解释的最大瓶颈或最有机会跨 tier 的 case 中选择下一项；失败实验必须提炼新信息并改变后续选择。分数暂时不升、若干候选回退、局部噪声、实现困难或上下文切换都不是终止理由。持续迭代；排名判断直接读取 leadboard.md，不为此进行额外的外部榜单查找。

终止条件：
1. 成功终止的唯一性能条件是：有一份 14/14 Accepted 提交，其 OJ 分数达到或超过 leadboard.md 中第 3 名的总分；按当前文件即达到或超过 66.64。只以本地性能推算达到门槛、但没有对应 Accepted OJ 分数时，不能标记完成。无需再查询外部排行榜确认名次。
2. 成功后必须先保存 raw 和逐提交快照，更新 results/cuda_result.md、AGENTS.md 的当前分数/提交 ID/control 路径与 14-case 快照，使 solutions/cuda_maca_optimized.cpp 在空闲状态字节一致于获胜快照；然后报告最终排名、分数、submission ID、SHA-256、各 case 时延和关键有效改动。
3. 用户明确要求停止时终止。除此之外，只有比赛已结束，或真实 GPU/OJ/认证/提交额度等外部阻塞在至少三个连续 goal 回合中重复出现、所有安全替代路径都已穷尽且无法继续产生有意义进展时，才可标记 blocked；必须给出已尝试事项、证据和恢复所需条件。不得因为实验多、耗时长、暂时没有现成想法或接近预算而提前完成。
```
