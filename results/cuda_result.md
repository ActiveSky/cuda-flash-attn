# XPUOJ FlashAttention KV Cache Decode 提交结果记录

用于持续记录同一题目的多次提交结果。主文件只保留便于比较和优化的摘要；完整原始数据（提交代码，OJ 协议、SPJ 报告、编译日志）以 JSON 归档在 `results/raw/`，按提交编号命名，可供深度分析。全部 raw 记录对应的字节精确提交源码见 [`solutions/archive/SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。

当前最高真实 OJ 分数为 **`57.43`**：#105915 首次达到，#105932 与 #105952 保持该记录；最新归档提交为 #105952。

## 按日期提交索引

### 2026-08-08

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#105952](https://xpuoj.com/contest/11/submissions/105952) | 2026-08-08 19:28:37 | CUDA Maca C500 / 86.8 K | Accepted | **57.43** | 最终归档候选；为 B64/KV8/L64 增加短序列 BSM loader dispatch，case 4 OJ 仍为 `0.030 ms`，总分与最高记录持平 |
| [#105932](https://xpuoj.com/contest/11/submissions/105932) | 2026-08-08 19:01:37 | CUDA Maca C500 / 86.2 K | Accepted | **57.43** | `reduce_splits<=16` 使用寄存器/shuffle reducer；case 5/6 为 `0.025/0.033 ms`，总分保持最高记录 |
| [#105915](https://xpuoj.com/contest/11/submissions/105915) | 2026-08-08 18:36:05 | CUDA Maca C500 / 84.6 K | Accepted | **57.43** | token-parallel 阈值由 `seqlen_k>=64` 下调到 `>=17`，case 3 `0.022→0.010 ms`；首次达到当前最高分 |
| [#105899](https://xpuoj.com/contest/11/submissions/105899) | 2026-08-08 18:06:45 | CUDA Maca C500 / 84.6 K | Accepted | 56.21 | 新增单 token 直接 V copy 与双 token 专用 attention；case 1/2 降至 `0.003/0.004 ms` |
| [#105835](https://xpuoj.com/contest/11/submissions/105835) | 2026-08-08 16:58:56 | CUDA Maca C500 / 79.3 K | Accepted | 54.86 | case 11 专用 Q shared-memory 复用将其降到 `0.439 ms`，但短 case 波动令 aggregate 回退 |
| [#105823](https://xpuoj.com/contest/11/submissions/105823) | 2026-08-08 16:43:17 | CUDA Maca C500 / 78.9 K | Accepted | 55.36 | KV8 z-partition 在 CTA 内借用 K/V shared memory 完成合并；长 case 继续改善并刷新分数 |
| [#105814](https://xpuoj.com/contest/11/submissions/105814) | 2026-08-08 16:25:59 | CUDA Maca C500 / 77.4 K | Accepted | 55.29 | full-page 与 tail-page 分离 launch/reduce，case 7/9/12/13 为 `0.324/0.328/0.547/0.300 ms` |
| [#105801](https://xpuoj.com/contest/11/submissions/105801) | 2026-08-08 16:09:52 | CUDA Maca C500 / 70.5 K | Accepted | 54.29 | 调整 B64/KV8/L2048、B32/KV8/L4096 与 B16/KV8/L362 的 split 数；小幅刷新 |
| [#105762](https://xpuoj.com/contest/11/submissions/105762) | 2026-08-08 15:43:33 | CUDA Maca C500 / 70.4 K | Accepted | 54.21 | KV4 Q staging + full-page/tail 专门循环；case 7–14 全线跃升，比分提高 `2.35` |
| [#105749](https://xpuoj.com/contest/11/submissions/105749) | 2026-08-08 15:29:38 | CUDA Maca C500 / 66.3 K | Accepted | 51.86 | 撤回 split canonicalization 并恢复 case 12 的 128 splits；长 case 小幅改善但 aggregate 略降 |
| [#105738](https://xpuoj.com/contest/11/submissions/105738) | 2026-08-08 15:23:02 | CUDA Maca C500 / 66.6 K | Accepted | 51.93 | packed pair QK/PV 读取与条件 max 更新；刷新该阶段最高分 |
| [#105704](https://xpuoj.com/contest/11/submissions/105704) | 2026-08-08 15:04:44 | CUDA Maca C500 / 65.9 K | Accepted | 51.43 | 调整长 KV8 split 并按 pages-per-split canonicalize；目标 case 持平，aggregate 回退 |
| [#105674](https://xpuoj.com/contest/11/submissions/105674) | 2026-08-08 14:45:43 | CUDA Maca C500 / 65.6 K | Accepted | 51.79 | 按 shape 在同步 `uint4` copy 与 BSM loader 之间选择；case 6/13 继续小幅改善 |
| [#105650](https://xpuoj.com/contest/11/submissions/105650) | 2026-08-08 14:26:32 | CUDA Maca C500 / 64.9 K | Accepted | 51.79 | KV8 使用同步 `uint4` loader，最长 KV4 保留 BSM；case 7/9/12/13 明显改善 |
| [#105636](https://xpuoj.com/contest/11/submissions/105636) | 2026-08-08 14:12:46 | CUDA Maca C500 / 64.6 K | Accepted | 51.50 | 三个固定 shape 的 split 微调；case 6/13 降到 `0.038/0.369 ms` |
| [#105616](https://xpuoj.com/contest/11/submissions/105616) | 2026-08-08 13:51:06 | CUDA Maca C500 / 64.3 K | Accepted | 51.29 | packed FMA/scale/accumulate 替代标量热循环；相对 #105608 提升 `0.93` 分 |
| [#105608](https://xpuoj.com/contest/11/submissions/105608) | 2026-08-08 13:41:57 | CUDA Maca C500 / 62.7 K | Accepted | 50.36 | 热路径改用 exp2 标度并按编译环境特化 reducer；长 case 小幅改善 |
| [#105601](https://xpuoj.com/contest/11/submissions/105601) | 2026-08-08 13:30:27 | CUDA Maca C500 / 62.3 K | Accepted | 50.29 | 单 live-split 直出 + 8 heads/CTA grouped reducer；首次突破 50 分 |
| [#105570](https://xpuoj.com/contest/11/submissions/105570) | 2026-08-08 12:52:35 | CUDA Maca C500 / 56.4 K | Accepted | 48.71 | reducer 只遍历 live splits；长 case 改善但 case 3/5/6 波动使总分略降 |
| [#105561](https://xpuoj.com/contest/11/submissions/105561) | 2026-08-08 12:45:19 | CUDA Maca C500 / 56.2 K | Accepted | 48.93 | 首个 token-parallel + MetaX BSM 版本；从 #105501 的 `40.71` 大幅跃升 |
| [#105501](https://xpuoj.com/contest/11/submissions/105501) | 2026-08-08 12:22:30 | CUDA Maca C500 / 45.1 K | Accepted | **40.71** | #105492 的模板特化 + softmax 化简版本，撤回空 split prune；KV8 case 7/9/12/13 为 `0.726/0.739/1.346/0.656 ms`，但停用 MMA 后 KV4 case 8/10/11/14 仍为 `0.408/0.118/1.094/0.701 ms` |
| [#105492](https://xpuoj.com/contest/11/submissions/105492) | 2026-08-08 12:14:21 | CUDA Maca C500 / 45.0 K | Accepted | 38.36 | #104441 派生的 softmax 化简 + empty-split/live-split contract + MMA rollback；KV8 局部改善被失去的 KV4 MMA 路径抵消，拒绝作为维护基线 |

### 2026-08-07

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#104552](https://xpuoj.com/contest/11/submissions/104552) | 2026-08-07 13:57:14 | CUDA Maca C500 / 45.9 K | Accepted | 38.71 | case 7/9 paired-QK full-page predicate-free branch: case 7 `0.895 ms`, case 9 `0.904 ms`; no repeatable benefit, reject |
| [#104518](https://xpuoj.com/contest/11/submissions/104518) | 2026-08-07 13:27:30 | CUDA Maca C500 / 45.9 K | Accepted | 38.14 | case 9 grouped KV8/GQA4 shared-V PV 正确但 `1.325 ms`，远慢于 paired-QK；CTA-wide handoff/barriers 与 register pressure 吞没 V-load 复用，拒绝 |
| [#104472](https://xpuoj.com/contest/11/submissions/104472) | 2026-08-07 12:48:56 | CUDA Maca C500 / 45.9 K | Accepted | 38.43 | 仅 case 9 改走 64-lane MMA-QK：`1.155 ms`，显著慢于同层 paired-QK control `0.858 ms`；KV8/GQA4 禁用该 MMA 路径 |
| [#104468](https://xpuoj.com/contest/11/submissions/104468) | 2026-08-07 12:38:05 | CUDA Maca C500 / 45.9 K | Accepted | 39.00 | 仅 case 7 paired-QK 声明为准确 128-thread `__launch_bounds__`：`0.854 ms`，处于既有 `0.845–0.858 ms` 区间，无结构性收益 |
| [#104461](https://xpuoj.com/contest/11/submissions/104461) | 2026-08-07 12:25:06 | CUDA Maca C500 / 45.9 K | WrongAnswer | 38.43 | case 7 paired-QK 将 16 次 uniform shuffle 减为 8 次 lane-dependent cross-subgroup shuffle；数学模拟正确但 C500 输出大范围错误，禁止此 shuffle 形式 |
| [#104441](https://xpuoj.com/contest/11/submissions/104441) | 2026-08-07 11:58:28 | CUDA Maca C500 / 45.9 K | Accepted | 38.64 | 同期复测稳定 case-8 `n_split=32` / 8 页路径：`0.401 ms`，优于 #104429 的 11 页 `0.409 ms`；确认不采用 24 splits |
| [#104429](https://xpuoj.com/contest/11/submissions/104429) | 2026-08-07 11:38:43 | CUDA Maca C500 / 45.9 K | Accepted | **40.07** | 当前最高真实 OJ 分数：case 8 `n_split=24`（11 页/partial）试验；其 case 8 `0.409 ms` 慢于已建立的 8 页路径，不能据 aggregate 单独合入 |
| [#104419](https://xpuoj.com/contest/11/submissions/104419) | 2026-08-07 11:27:27 | CUDA Maca C500 / 45.9 K | Accepted | 38.79 | case 6 `n_split=6`（4 页/partial）`0.096 ms`，慢于当前 3 页策略 `0.082 ms`；不合入 |
| [#104406](https://xpuoj.com/contest/11/submissions/104406) | 2026-08-07 11:11:58 | CUDA Maca C500 / 45.7 K | Accepted | 38.43 | case 5 `n_split=2`（5 页/partial）`0.080 ms`，显著慢于精确 3 页策略 `0.056 ms`；不合入 |
| [#104394](https://xpuoj.com/contest/11/submissions/104394) | 2026-08-07 11:00:57 | CUDA Maca C500 / 45.9 K | Accepted | 38.79 | case 6 paired-token KV8 QK：`0.087 ms`，慢于相邻标量路径的 `0.082 ms`；不合入 |
| [#104386](https://xpuoj.com/contest/11/submissions/104386) | 2026-08-07 10:47:52 | CUDA Maca C500 / 45.9 K | Accepted | 39.64 | case 10 MMA-QK 的 3 页/partial 重测：`0.132 ms`，明显差于 4 页 MMA 策略的 `0.114 ms`；不合入 |
| [#104380](https://xpuoj.com/contest/11/submissions/104380) | 2026-08-07 10:36:37 | CUDA Maca C500 / 45.9 K | Accepted | 38.64 | #104368 的无修改复测；case 10 MMA-QK + 4 页/partial 稳定为 `0.114 ms` / 35 分 |
| [#104368](https://xpuoj.com/contest/11/submissions/104368) | 2026-08-07 10:23:40 | CUDA Maca C500 / 45.9 K | Accepted | 38.64 | case 10 在已验证的 4 页/partial split 下改用 KV4 MMA-QK，`0.124→0.114 ms`、34→35 分，目标路径新最佳 |
| [#104355](https://xpuoj.com/contest/11/submissions/104355) | 2026-08-07 10:01:39 | CUDA Maca C500 / 45.7 K | Accepted | 38.43 | case 12 `n_split=192`（11 页/partial），`1.574 ms`；但该轮全局变慢，无法据此替代 8 页策略 |
| [#104341](https://xpuoj.com/contest/11/submissions/104341) | 2026-08-07 09:39:56 | CUDA Maca C500 / 45.7 K | Accepted | 39.79 | case 11 `n_split=48`（16 页/partial），`0.981 ms`；不如当前 12 页策略约 `0.977–0.978 ms` |
| [#104335](https://xpuoj.com/contest/11/submissions/104335) | 2026-08-07 09:28:49 | CUDA Maca C500 / 45.7 K | Accepted | 39.71 | case 10 `n_split=192`（3 页/partial），`0.126 ms`；不如 #104328 的 4 页/partial `0.124 ms` |
| [#104334](https://xpuoj.com/contest/11/submissions/104334) | 2026-08-07 09:19:37 | CUDA Maca C500 / 45.7 K | Accepted | 39.86 | case 10 `64→256` splits（8→2 页/partial）；目标 case 10 `0.124→0.127 ms` 回退，但其余 case 的时序波动使总分刷新 |
| [#104328](https://xpuoj.com/contest/11/submissions/104328) | 2026-08-07 09:04:55 | CUDA Maca C500 / 45.7 K | Accepted | 39.79 | case 10 `64→128` splits（8→4 页/partial），`0.142→0.124 ms` |
| [#104327](https://xpuoj.com/contest/11/submissions/104327) | 2026-08-07 08:55:48 | CUDA Maca C500 / 45.7 K | Accepted | 39.57 | case 4 `1→2` splits（4→2 页/partial）反而 `0.064→0.070 ms`，保留不 split |
| [#104322](https://xpuoj.com/contest/11/submissions/104322) | 2026-08-07 08:47:04 | CUDA Maca C500 / 45.4 K | Accepted | **39.71** | 当前最佳可提交源：case 5 精确 3 splits（3 页/partial、无空 partial）与 4 splits 同为 `0.056 ms`，选择 3 splits 作为精简设置 |
| [#104318](https://xpuoj.com/contest/11/submissions/104318) | 2026-08-07 08:38:13 | CUDA Maca C500 / 45.2 K | Accepted | 39.71 | case 5 `1→4` splits（9→3 页/partial），`0.071→0.056 ms` |
| [#104316](https://xpuoj.com/contest/11/submissions/104316) | 2026-08-07 08:29:24 | CUDA Maca C500 / 45.0 K | Accepted | 38.00 | case 6 `n_split=12`（2 页 ceiling）为 `0.089 ms`，且全局慢速；仍未胜过 8 split |
| [#104314](https://xpuoj.com/contest/11/submissions/104314) | 2026-08-07 08:20:40 | CUDA Maca C500 / 45.0 K | Accepted | 39.29 | case 6 `3→8` splits（约 8→3 页/partial），`0.117→0.082 ms` |
| [#104312](https://xpuoj.com/contest/11/submissions/104312) | 2026-08-07 08:11:36 | CUDA Maca C500 / 45.0 K | Accepted | 38.71 | case 14 `16→8` 页/split 后 `0.520→0.543 ms`，B=1 KV4 不应继续切分 |
| [#104310](https://xpuoj.com/contest/11/submissions/104310) | 2026-08-07 08:02:47 | CUDA Maca C500 / 44.7 K | Accepted | 38.71 | case 8 再到 4 页/split 后 `0.386→0.398 ms`，确认 8 页是局部最优 |
| [#104307](https://xpuoj.com/contest/11/submissions/104307) | 2026-08-07 07:54:02 | CUDA Maca C500 / 44.7 K | Accepted | 38.79 | case 8 `16→8` 页/split，`0.432→0.386 ms`；与 7/9/12/11 的既有优化合并 |
| [#104306](https://xpuoj.com/contest/11/submissions/104306) | 2026-08-07 07:44:57 | CUDA Maca C500 / 44.5 K | Accepted | 37.29 | case 11 6 页/partial（`n_split=128`）进一步退至 `1.032 ms`；确认最佳区间在 12 页附近 |
| [#104302](https://xpuoj.com/contest/11/submissions/104302) | 2026-08-07 07:36:12 | CUDA Maca C500 / 44.5 K | Accepted | 37.29 | case 11 固定 8 页/partial（`n_split=96`）为 `1.000 ms`，慢速环境下未胜过 12 页的 #104301 |
| [#104301](https://xpuoj.com/contest/11/submissions/104301) | 2026-08-07 07:27:24 | CUDA Maca C500 / 44.5 K | Accepted | 38.57 | 在 7/9/12 的 8 页策略上，case 11 `48→12` 页/split，`1.117→0.978 ms` |
| [#104299](https://xpuoj.com/contest/11/submissions/104299) | 2026-08-07 07:18:42 | CUDA Maca C500 / 44.5 K | Accepted | 37.29 | case 11 split `16→32`（48→24 页/partial）使 `1.117→1.028 ms`；全局慢速轮次下仍呈现强正收益 |
| [#104298](https://xpuoj.com/contest/11/submissions/104298) | 2026-08-07 07:09:39 | CUDA Maca C500 / 44.3 K | Accepted | 38.43 | case 7/9/12 均采用 8 页/split，case 12 `1.643→1.579 ms`（与 16 页点接近） |
| [#104294](https://xpuoj.com/contest/11/submissions/104294) | 2026-08-07 07:00:58 | CUDA Maca C500 / 44.3 K | Accepted | 38.21 | case 12 `32→16` 页/split，`1.643→1.569 ms`；目标路径仍提升，但其他 case 计时波动拉低总分 |
| [#104293](https://xpuoj.com/contest/11/submissions/104293) | 2026-08-07 06:52:18 | CUDA Maca C500 / 44.3 K | Accepted | 38.36 | case 12 进一步 `64→32` 页/split，`1.793→1.643 ms` |
| [#104290](https://xpuoj.com/contest/11/submissions/104290) | 2026-08-07 06:43:39 | CUDA Maca C500 / 44.3 K | Accepted | 38.29 | 保留 case 7/9 的 8 页/split，并将 case 12 `128→64` 页/split，`1.996→1.793 ms` |
| [#104288](https://xpuoj.com/contest/11/submissions/104288) | 2026-08-07 06:35:10 | CUDA Maca C500 / 44.1 K | Accepted | 38.00 | case 7 维持 8 页/split、case 9 用 7 页/split；目标时延与 #104278 持平，但总分未胜出 |
| [#104285](https://xpuoj.com/contest/11/submissions/104285) | 2026-08-07 06:26:01 | CUDA Maca C500 / 44.1 K | Accepted | 36.79 | 10x（7 页/split）与同轮 8 页路径几乎持平但无确定胜出；仅值得作 case 9 独立混合验证 |
| [#104282](https://xpuoj.com/contest/11/submissions/104282) | 2026-08-07 06:17:21 | CUDA Maca C500 / 44.1 K | Accepted | 36.79 | #104278 的同源复测也受同一全局慢速环境影响；仍显示 8 页/split 小幅优于 nominal 6 页/split |
| [#104281](https://xpuoj.com/contest/11/submissions/104281) | 2026-08-07 06:08:38 | CUDA Maca C500 / 44.1 K | Accepted | 36.79 | 12x（nominal 6 页/split）全 case 普遍变慢；随后 #104282 校准证明此批环境较慢 |
| [#104279](https://xpuoj.com/contest/11/submissions/104279) | 2026-08-07 05:59:48 | CUDA Maca C500 / 44.1 K | Accepted | 38.07 | case 7/9 split 数提高到 generic 的 16 倍（4 页/split）后回退，确认过度切分开始超过收益 |
| [#104278](https://xpuoj.com/contest/11/submissions/104278) | 2026-08-07 05:51:07 | CUDA Maca C500 / 44.1 K | Accepted | 38.21 | case 7/9 split 数提高到 generic 的 8 倍，`0.878→0.848 ms` / `0.895→0.857 ms` |
| [#104275](https://xpuoj.com/contest/11/submissions/104275) | 2026-08-07 05:42:16 | CUDA Maca C500 / 44.1 K | Accepted | 38.07 | case 7/9 split 数提高到 generic 的 4 倍，`0.951→0.878 ms` / `0.969→0.895 ms` |
| [#104273](https://xpuoj.com/contest/11/submissions/104273) | 2026-08-07 05:34:02 | CUDA Maca C500 / 44.1 K | Accepted | 37.79 | #104271 的独立复测，证实 2x split 的 case 7/9 改善可复现 |
| [#104271](https://xpuoj.com/contest/11/submissions/104271) | 2026-08-07 05:19:18 | CUDA Maca C500 / 44.1 K | Accepted | 37.71 | case 7/9 split 数翻倍，`1.172→0.962 ms` / `1.122→0.975 ms` |
| [#104270](https://xpuoj.com/contest/11/submissions/104270) | 2026-08-07 05:10:18 | CUDA Maca C500 / 44.1 K | Accepted | 37.14 | case 7 `n_split 2→1`：正确但 `1.172→1.413 ms`，split/reduce 并非瓶颈 |
| [#104267](https://xpuoj.com/contest/11/submissions/104267) | 2026-08-07 05:00:10 | CUDA Maca C500 / 44.0 K | Accepted | 37.21 | case 13 n_split `128→192`：正确但 `0.701→0.735 ms`，高 split 也退化，128 是当前最佳 |
| [#104265](https://xpuoj.com/contest/11/submissions/104265) | 2026-08-07 04:51:18 | CUDA Maca C500 / 44.1 K | Accepted | 36.36 | case 13 n_split `128→64`：正确但 `0.701→0.825 ms`，减少并行度明显退化 |
| [#104263](https://xpuoj.com/contest/11/submissions/104263) | 2026-08-07 04:42:01 | CUDA Maca C500 / 52.3 K | WrongAnswer | 33.21 | KV8 case 7/9 的 8-lane quad-token QK 均约 `36 s` 超时式 WA；16-lane paired-QK 是当前最小安全 subgroup |
| [#104262](https://xpuoj.com/contest/11/submissions/104262) | 2026-08-07 04:39:33 | CUDA Maca C500 / 44.3 K | CompilationError | — | quad-QK builder 初版遗漏保留 paired-QK fallback definition；已修复为 #104263 后验证 |
| [#104259](https://xpuoj.com/contest/11/submissions/104259) | 2026-08-07 04:26:29 | CUDA Maca C500 / 59.6 K | WrongAnswer | 35.43 | case 13 V staging 扩到 4× D128 tile 后仍约 `36.182 s` 超时式 WA；排除单纯 V LDS 越界解释 |
| [#104255](https://xpuoj.com/contest/11/submissions/104255) | 2026-08-07 04:17:02 | CUDA Maca C500 / 59.1 K | WrongAnswer | 34.29 | forced official native four-wave PV launch：仅 case 13 约 `35.879 s` 超时式 WA；#104253 确认是 header-guard fallback |
| [#104253](https://xpuoj.com/contest/11/submissions/104253) | 2026-08-07 04:07:20 | CUDA Maca C500 / 59.0 K | Accepted | 36.14 | case 13 guarded native CUTE P×V runtime checkpoint：14/14 正确；case 13 `0.707 ms`，未胜过 #104235 的 `0.701 ms` |
| [#104250](https://xpuoj.com/contest/11/submissions/104250) | 2026-08-07 03:41:42 | CUDA Maca C500 / 48.0 K | Accepted | 36.14 | official four-wave CUTE PV epilogue surface（FP32→BF16 P、V LDS swizzle、permute、GEMM）编译成功；生产 dispatch 不变 |
| [#104247](https://xpuoj.com/contest/11/submissions/104247) | 2026-08-07 03:29:19 | CUDA Maca C500 / 45.3 K | Accepted | 37.36 | official MetaX `MACA_16x16x16` / `mctlass::bfloat16_t` CUTE K=128 probe 编译成功；生产 dispatch 不变 |
| [#104246](https://xpuoj.com/contest/11/submissions/104246) | 2026-08-07 03:17:49 | CUDA Maca C500 / 43.2 K | Accepted | 37.14 | 64-thread CUTE QK + 已验证 scalar-PV：完整正确但略低于 #104235，确认单-wave CUTE K=128 QK materialization 可运行 |
| [#104240](https://xpuoj.com/contest/11/submissions/104240) | 2026-08-07 03:04:54 | CUDA Maca C500 / 50.2 K | WrongAnswer | 31.14 | naive 256-thread CUTE four-wave KV8 score path：case 7/9/12/13 全部约 36 s 超时式 WA，已拒绝 |
| [#104239](https://xpuoj.com/contest/11/submissions/104239) | 2026-08-07 03:00:25 | CUDA Maca C500 / 50.2 K | CompilationError | — | 首个 CUTE four-wave KV8 production candidate；host pass 中 `gqa_ratio` launch scope 遗漏，已修复后重试 |
| [#104235](https://xpuoj.com/contest/11/submissions/104235) | 2026-08-07 02:47:02 | CUDA Maca C500 / 43.8 K | Accepted | **37.43** | 当前最高真实 OJ 分数：未 launch 的 CUTE K=128 materialization probe + 已验证 KV4 MMA-QK / 全 KV8 paired-QK dispatch；分数包含 OJ 计时波动 |
| [#104232](https://xpuoj.com/contest/11/submissions/104232) | 2026-08-07 02:35:01 | CUDA Maca C500 / 41.8 K | Accepted | 36.29 | #104227 的独立复测：KV8 case 12/13 加速稳定，整体计时仍有波动 |
| [#104227](https://xpuoj.com/contest/11/submissions/104227) | 2026-08-07 02:18:56 | CUDA Maca C500 / 41.8 K | Accepted | 36.29 | paired-token QK 扩至 KV8 case 12/13：四个 KV8 长序列均加速，单轮总分受评测波动影响低于 #104221 |
| [#104225](https://xpuoj.com/contest/11/submissions/104225) | 2026-08-07 02:16:00 | CUDA Maca C500 / 26.2 K | Accepted | 36.29 | CUTE shared-tensor partition + explicit `gemm` probe 可编译，生产路径不变 |
| [#104221](https://xpuoj.com/contest/11/submissions/104221) | 2026-08-07 02:07:51 | CUDA Maca C500 / 41.7 K | Accepted | 37.07 | 精确 KV4 MMA-QK（8/11/14）+ KV8 paired-token QK（7/9）组合，14/14 通过；后续 #104235 在扩展 KV8 dispatch 上取得更高单轮分数 |
| [#104220](https://xpuoj.com/contest/11/submissions/104220) | 2026-08-07 02:04:17 | CUDA Maca C500 / 26.3 K | Accepted | 35.14 | CUTE thread-partition tensor + 三参数 `gemm` API probe 编译通过；生产路径不变，补录 raw checkpoint |
| [#104217](https://xpuoj.com/contest/11/submissions/104217) | 2026-08-07 01:56:19 | CUDA Maca C500 / 31.6 K | Accepted | 35.21 | KV8 case 7/9 paired-token scalar QK；两例均显著加速，值得与精确 MMA-QK dispatch 组合 |
| [#104216](https://xpuoj.com/contest/11/submissions/104216) | 2026-08-07 01:54:50 | CUDA Maca C500 / 26.1 K | Accepted | 36.21 | CUTE shared tensor partition + tiled-MMA `gemm` probe 编译通过；生产路径不变，补录 raw checkpoint |
| [#104210](https://xpuoj.com/contest/11/submissions/104210) | 2026-08-07 01:40:44 | CUDA Maca C500 / 25.2 K | Accepted | 36.21 | 基线保持不变；CUTE MMA_Atom/TiledMMA 类型构造 probe 可编译，验证全量 CUTE kernel 的下一道编译边界 |
| [#104202](https://xpuoj.com/contest/11/submissions/104202) | 2026-08-07 01:28:41 | CUDA Maca C500 / 31.2 K | WrongAnswer | 33.50 | KV8 case 7/9 native packed BF16x2 conversion；两例均超时式 WA，已禁用 |
| [#104197](https://xpuoj.com/contest/11/submissions/104197) | 2026-08-07 01:12:10 | CUDA Maca C500 / 31.7 K | Accepted | 36.14 | 4 KB sequential K→V shared staging on KV8 case 7/9；正确但两 case 退化，已禁用 |
| [#104188](https://xpuoj.com/contest/11/submissions/104188) | 2026-08-07 00:55:45 | CUDA Maca C500 / 32.9 K | WrongAnswer | 30.29 | 两个 64-lane group 均重复 raw QK WMMA；仍在长 KV4 发生超时式 WA，已弃用整个 raw 128-thread WMMA 变体 |
| [#104181](https://xpuoj.com/contest/11/submissions/104181) | 2026-08-07 00:36:21 | CUDA Maca C500 / 32.8 K | WrongAnswer | 30.36 | 128-thread two-wave：仅一个 64-lane group 执行 QK WMMA；长 KV4 全部超时式 WA，已弃用 |
| [#104175](https://xpuoj.com/contest/11/submissions/104175) | 2026-08-07 00:30:34 | CUDA Maca C500 / 32.9 K | Accepted | 35.79 | MMA-QK 仅精确启用 case 8/11/14；目标 case 稳定获益但仍未超过 #104091 |
| [#104164](https://xpuoj.com/contest/11/submissions/104164) | 2026-08-07 00:19:55 | CUDA Maca C500 / 33.4 K | Accepted | 35.21 | MMA-QK page K/V loader 的 uint4 尝试；正确但打散转置写入导致长 KV4 回退，已禁用 |
| [#104153](https://xpuoj.com/contest/11/submissions/104153) | 2026-08-07 00:06:44 | CUDA Maca C500 / 34.0 K | Accepted | 35.43 | BF16 P×V raw WMMA；数学正确但 case 8/10/11/14 全部显著退化，已禁用 |

### 2026-08-06

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#104147](https://xpuoj.com/contest/11/submissions/104147) | 2026-08-06 23:57:45 | CUDA Maca C500 / 32.5 K | Accepted | 35.57 | 仅长 KV4 启用 MMA-QK；case 8/11/14 保持实质提升，但全局分数受非目标路径本轮变慢影响 |
| [#104142](https://xpuoj.com/contest/11/submissions/104142) | 2026-08-06 23:43:37 | CUDA Maca C500 / 31.9 K | Accepted | 31.64 | 全量 64-lane MMA-QK + FP32 scalar-PV；正确但混合 KV4/KV8 dispatch 退化，改为选择性启用 |
| [#104130](https://xpuoj.com/contest/11/submissions/104130) | 2026-08-06 23:10:21 | CUDA Maca C500 / 24.3 K | Accepted | 35.86 | raw WMMA API probe 加入 device-pass guard 后编译并 14/14 通过；生产路径不变 |
| [#104128](https://xpuoj.com/contest/11/submissions/104128) | 2026-08-06 23:07:24 | CUDA Maca C500 / 24.1 K | CompilationError | — | raw WMMA API probe 暴露给 host pass，`mxmaca/wmma` namespace 不可见；由 #104130 修复 |
| [#104101](https://xpuoj.com/contest/11/submissions/104101) | 2026-08-06 22:11:22 | CUDA Maca C500 / 23.1 K | Accepted | 35.29 | lane-0-only partial m/l store；负优化，已回退 |
| [#104091](https://xpuoj.com/contest/11/submissions/104091) | 2026-08-06 21:53:05 | CUDA Maca C500 / 22.9 K | Accepted | **36.21** | 协作式 split-KV reduce；当前最佳 |
| [#104025](https://xpuoj.com/contest/11/submissions/104025) | 2026-08-06 20:44:46 | CUDA Maca C500 / 20.8 K | Accepted | 34.79 | `uint4` K/V page load + n_split==1 标量直写 |
| [#104000](https://xpuoj.com/contest/11/submissions/104000) | 2026-08-06 20:06:53 | CUDA Maca C500 / 12.6 K | Accepted | 31.14 | lane-0 softmax + 定向降 split；负优化 |
| [#103932](https://xpuoj.com/contest/11/submissions/103932) | 2026-08-06 18:49:00 | CUDA Maca C500 / 19.4 K | Accepted | 31.57 | v4（回退双缓冲）；此前最佳 |
| [#103918](https://xpuoj.com/contest/11/submissions/103918) | 2026-08-06 18:35:06 | CUDA Maca C500 / 20.1 K | Accepted | 30.21 | v3c（双缓冲+标量写）；占用率下降致大 case 退化 |
| [#103891](https://xpuoj.com/contest/11/submissions/103891) | 2026-08-06 18:03:55 | CUDA Maca C500 / 20.4 K | WrongAnswer | 0 | v3（direct-out）；样例 #1 输出未写入，WA |
| [#103870](https://xpuoj.com/contest/11/submissions/103870) | 2026-08-06 17:39:43 | CUDA Maca C500 / 18.3 K | Accepted | 31.14 | v2；当前最佳 |
| [#103799](https://xpuoj.com/contest/11/submissions/103799) | 2026-08-06 16:33:33 | CUDA Maca C500 / 15.4 K | Accepted | 28.29 | v1 基线 |
| [#103773](https://xpuoj.com/contest/11/submissions/103773) | 2026-08-06 16:16:36 | CUDA Maca C500 / 15.2 K | CompilationError | — | 初版在 C500 CUTE 中调用不存在的 `cute::convert<float>`；后续改用可用的 BF16 转换路径 |

## 记录编排

- 提交索引按日期分组，日期与同一日期内的提交均按时间倒序排列。
- 详细记录按相同日期分组；同一提交内固定使用以下顺序：提交信息、提交总览（如有）、结果分析、测试点汇总（如有）、原始归档链接。
- 提交索引覆盖所有已归档提交；详细记录保留有分析内容的实验 checkpoint。
- 原始数据归档为 `results/raw/cuda_<id>_raw.json`（完整接口响应，含提交的代码、OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）。每条 raw 中的 `raw_detail.content.code` 同时按原始字节提取到 `solutions/archive/<date>-submissions/cuda_<id>.cpp`。

## 详细记录

### 2026-08-08

#### 提交 #105561–#105952 · token-parallel 连续优化批次

##### 提交总览

- 本批 20 次提交全部为 Accepted（14/14）。总分从前序 #105501 的 `40.71` 提高到 `57.43`，净增 `16.72` 分。
- #105915 首次达到当前最高分 `57.43`；#105932 与最终 #105952 保持同分。最终源码 SHA-256 为 `eba3c95b18f5e62eb13d00f17de346946de6b8293fd00daaa0cece5d94f7c34a`。
- 每一次提交的字节精确源码与 raw JSON 都已独立归档；同源复投也保留各自的提交号文件，不做去重替代。

| 提交 | 总分 | 本轮主要代码变化 | 归档 |
|---:|---:|---|---|
| #105952 | **57.43** | B64/KV8/L64 改走短序列 BSM loader dispatch；OJ case 4 未进一步下降 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105952.cpp) / [raw](raw/cuda_105952_raw.json) |
| #105932 | **57.43** | `reduce_splits<=16` 增加寄存器/shuffle reducer | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105932.cpp) / [raw](raw/cuda_105932_raw.json) |
| #105915 | **57.43** | token-parallel 阈值 `seqlen_k>=64→>=17` | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105915.cpp) / [raw](raw/cuda_105915_raw.json) |
| #105899 | 56.21 | 单 token 直接复制 V；双 token 专用 attention kernel | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105899.cpp) / [raw](raw/cuda_105899_raw.json) |
| #105835 | 54.86 | case 11 复用 K shared-memory 存 Q，降低 full/tail 变体资源压力 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105835.cpp) / [raw](raw/cuda_105835_raw.json) |
| #105823 | 55.36 | KV8 z-partition 在 CTA 内借用 K/V shared-memory 合并 FP32 状态 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105823.cpp) / [raw](raw/cuda_105823_raw.json) |
| #105814 | 55.29 | full-page 与 tail-page 独立 launch，并匹配 reducer 的有效 split | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105814.cpp) / [raw](raw/cuda_105814_raw.json) |
| #105801 | 54.29 | 三个 KV8 shape 的 split 数微调 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105801.cpp) / [raw](raw/cuda_105801_raw.json) |
| #105762 | 54.21 | KV4 Q staging；完整页 predicate-free 循环与 tail 循环分离 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105762.cpp) / [raw](raw/cuda_105762_raw.json) |
| #105749 | 51.86 | 撤回 split canonicalization，case 12 恢复 128 splits | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105749.cpp) / [raw](raw/cuda_105749_raw.json) |
| #105738 | 51.93 | packed pair QK/PV 读取和条件 max/scale 更新 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105738.cpp) / [raw](raw/cuda_105738_raw.json) |
| #105704 | 51.43 | 长 KV8 split 调整，并按 pages-per-split 收敛实际 split 数 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105704.cpp) / [raw](raw/cuda_105704_raw.json) |
| #105674 | 51.79 | 按 shape 模板化同步 `uint4` copy / BSM loader | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105674.cpp) / [raw](raw/cuda_105674_raw.json) |
| #105650 | 51.79 | KV8 loader 改为同步 `uint4`，最长 KV4 保留 BSM | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105650.cpp) / [raw](raw/cuda_105650_raw.json) |
| #105636 | 51.50 | case 6/8/13 对应 shape 的 split 微调 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105636.cpp) / [raw](raw/cuda_105636_raw.json) |
| #105616 | 51.29 | packed FMA、scale 与 accumulate 覆盖 QK/PV 热循环 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105616.cpp) / [raw](raw/cuda_105616_raw.json) |
| #105608 | 50.36 | exp2 标度与 reducer 编译期特化 | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105608.cpp) / [raw](raw/cuda_105608_raw.json) |
| #105601 | 50.29 | 单 live-split 直出；8 heads/CTA grouped reducer | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105601.cpp) / [raw](raw/cuda_105601_raw.json) |
| #105570 | 48.71 | reducer 由全部 splits 改为只遍历 live splits | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105570.cpp) / [raw](raw/cuda_105570_raw.json) |
| #105561 | 48.93 | 首次加入 token-parallel page kernel 与 MetaX BSM 128-bit load | [cpp](../solutions/archive/2026-08-08-submissions/cuda_105561.cpp) / [raw](raw/cuda_105561_raw.json) |

##### 完整测试点耗时

以下数字直接取自 raw OJ 结果，单位为 `μs`；行按提交时间倒序排列。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #105952 | **57.43** | 3 | 4 | 10 | 30 | 26 | 33 | 322 | 175 | 321 | 58 | 448 | 533 | 294 | 297 |
| #105932 | **57.43** | 3 | 4 | 10 | 30 | 25 | 33 | 322 | 180 | 322 | 60 | 454 | 539 | 294 | 300 |
| #105915 | **57.43** | 3 | 4 | 10 | 29 | 26 | 34 | 321 | 174 | 321 | 60 | 453 | 539 | 294 | 299 |
| #105899 | 56.21 | 3 | 4 | 22 | 30 | 26 | 33 | 320 | 179 | 322 | 60 | 454 | 533 | 296 | 297 |
| #105835 | 54.86 | 8 | 9 | 22 | 30 | 26 | 34 | 321 | 174 | 322 | 60 | 439 | 534 | 296 | 300 |
| #105823 | 55.36 | 7 | 9 | 18 | 30 | 26 | 34 | 321 | 174 | 323 | 58 | 448 | 533 | 294 | 297 |
| #105814 | 55.29 | 7 | 9 | 18 | 29 | 26 | 33 | 324 | 175 | 328 | 60 | 453 | 547 | 300 | 299 |
| #105801 | 54.29 | 8 | 11 | 22 | 30 | 26 | 34 | 338 | 180 | 342 | 57 | 458 | 576 | 315 | 296 |
| #105762 | 54.21 | 7 | 11 | 22 | 30 | 26 | 35 | 342 | 179 | 342 | 60 | 463 | 583 | 316 | 300 |
| #105749 | 51.86 | 7 | 9 | 18 | 33 | 30 | 37 | 387 | 220 | 389 | 70 | 585 | 657 | 354 | 386 |
| #105738 | 51.93 | 7 | 9 | 18 | 32 | 30 | 38 | 386 | 220 | 389 | 70 | 587 | 658 | 355 | 386 |
| #105704 | 51.43 | 8 | 11 | 18 | 32 | 30 | 38 | 391 | 225 | 394 | 72 | 599 | 676 | 361 | 391 |
| #105674 | 51.79 | 7 | 9 | 18 | 33 | 30 | 37 | 389 | 221 | 396 | 70 | 591 | 670 | 359 | 389 |
| #105650 | 51.79 | 7 | 9 | 18 | 33 | 30 | 38 | 391 | 221 | 395 | 70 | 591 | 670 | 360 | 389 |
| #105636 | 51.50 | 7 | 9 | 18 | 34 | 30 | 38 | 404 | 221 | 411 | 70 | 590 | 694 | 369 | 389 |
| #105616 | 51.29 | 7 | 9 | 18 | 33 | 30 | 41 | 405 | 224 | 410 | 70 | 590 | 693 | 381 | 389 |
| #105608 | 50.36 | 7 | 9 | 18 | 35 | 31 | 43 | 432 | 235 | 438 | 74 | 619 | 739 | 405 | 409 |
| #105601 | 50.29 | 7 | 9 | 18 | 35 | 31 | 43 | 438 | 239 | 444 | 75 | 628 | 748 | 409 | 414 |
| #105570 | 48.71 | 7 | 9 | 22 | 35 | 43 | 55 | 451 | 247 | 451 | 77 | 634 | 771 | 412 | 417 |
| #105561 | 48.93 | 8 | 10 | 18 | 35 | 37 | 50 | 469 | 257 | 472 | 75 | 653 | 830 | 410 | 416 |

##### 结果分析

- 最大的结构跃升有两次。#105561 的 token-parallel/BSM 路径将 score `40.71→48.93`；#105762 的 KV4 Q staging 与 full-page/tail 专门循环又将 `51.86→54.21`。两次都同时改善多组中长序列，而不是依赖单 case 波动。
- #105601 的 grouped reducer、#105616 的 packed arithmetic、#105650–#105749 的 loader/split/PV 微调把第一阶段稳定推进到约 `51.8–51.9`。其中 #105704 和 #105749 表明 aggregate 会受短 case 波动影响，shape-specific 决策仍应优先看目标 case。
- #105814 分离完整页与尾页，#105823 再把 KV8 z-state 合并收进 CTA，长 case 达到新平台。#105835 将 case 11 刷新到 `439 μs`，但 case 1/3 的本轮波动令总分下降，不能据 aggregate 否定该局部路径。
- #105899 的 1/2-token kernel 把 case 1/2 固定到 `3/4 μs`。#105915 只把 token-parallel 阈值从 64 改到 17，case 3 随即由 `22→10 μs`，并首次得到 `57.43`。
- #105932 的小 split reducer 和 #105952 的短 KV8 loader dispatch 在 OJ 上没有突破 `57.43`，但分别保留了 case 5/6 的 `25/33 μs` 样本，以及最终轮 case 10–14 的 `58/448/533/294/297 μs`。当前最高分应表述为“#105915 首次达到，#105932/#105952 保持”，而不是只归因于最后一次提交。

#### 提交 #105501 · 2026-08-08 12:22:30

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/105501)

- **提交语言/环境**：CUDA Maca C500 / 45.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`40.71`**
- **代码溯源**：原始归档的嵌入源码 SHA-256 为 `541c1ceee4938962f9e7d36c3c8b369c5a1234a8bcf6d98c3fa74eb32c00cf41`。它是 #105492 的模板特化后续版本：固定 KV4/KV8 fast path 的编译期参数、直接按新的 global max 累积 page softmax；同时撤回 #105492 的 empty-split early return 与 live-split reducer 剪枝。
- **策略**：保持 KV8 的 paired-QK，并关闭本机 MACA 3.7.1 数值不可靠的 MMA-QK dispatch。所有 fast path 都走编译期特化 scalar/paired kernel。

##### 结果分析

- 相对 #104441，KV8 long case 均显著改善：case 7 `0.858→0.726 ms`、case 9 `0.866→0.739 ms`、case 12 `1.600→1.346 ms`、case 13 `0.709→0.656 ms`。真实 C500 交错 A/B 也独立复现 case 7/9 均约 `1.151x`。
- KV4 的 MMA rollback 仍是主要代价：case 8/10/11/14 分别为 `0.408/0.118/1.094/0.701 ms`，后两例明显慢于 #104441 的 MMA 路径。因此 aggregate `40.71` 含评测 timing tier 影响，不能仅凭总分把 scalar KV4 视为胜过已验收的 MMA 版本。
- #105501 与后续 token-parallel 链不是同一候选；其提交源码现已单独归档为 [`cuda_105501.cpp`](../solutions/archive/2026-08-08-submissions/cuda_105501.cpp)，不能把 #105561–#105952 的收益回溯归因给本次提交。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 1 | `0.008 ms` | 82 |
| 2 | `0.010 ms` | 79 |
| 3 | `0.018 ms` | 71 |
| 4 | `0.061 ms` | 49 |
| 5 | `0.053 ms` | 46 |
| 6 | `0.078 ms` | 38 |
| 7 | `0.726 ms` | 27 |
| 8 | `0.408 ms` | 21 |
| 9 | `0.739 ms` | 30 |
| 10 | `0.118 ms` | 35 |
| 11 | `1.094 ms` | 18 |
| 12 | `1.346 ms` | 29 |
| 13 | `0.656 ms` | 26 |
| 14 | `0.701 ms` | 19 |

##### 原始评测归档

- [cuda_105501_raw.json](raw/cuda_105501_raw.json)

#### 提交 #105492 · 2026-08-08 12:14:21

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/105492)

- **提交语言/环境**：CUDA Maca C500 / 45.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.36`
- **代码溯源**：原始归档的嵌入源码 SHA-256 为 `5c80382799394028e707d4d66f023c4acb4cacb0cff5d196e98103c457bc20dc`；字节精确源码现已归档为 [`cuda_105492.cpp`](../solutions/archive/2026-08-08-submissions/cuda_105492.cpp)。其最近祖先是 #104441 / `cuda_maca_version.cpp`。
- **策略**：page softmax 的 `beta` rescale elimination、empty-split early return 和与之配对的 live-split reduce；同时将原先固定 KV4 的 MMA-QK dispatch 固定关闭。

##### 结果分析

- KV8 的 softmax/split 改动具有局部正收益：case 7 `0.858→0.837 ms`、case 9 `0.866→0.853 ms`、case 12 `1.600→1.538 ms`、case 13 `0.709→0.703 ms`。
- 但被关闭的 MMA-QK 使 KV4 case 8/10/11/14 退化为 `0.419/0.124/1.124/0.723 ms`；尤其 case 14 比 #104441 慢 `0.194 ms`。因此它不是可保留的完整维护基线，只有其已验证的模板化/softmax 思路被后续 #105501 继承。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 1 | `0.010 ms` | 79 |
| 2 | `0.012 ms` | 75 |
| 3 | `0.024 ms` | 65 |
| 4 | `0.064 ms` | 48 |
| 5 | `0.066 ms` | 41 |
| 6 | `0.092 ms` | 34 |
| 7 | `0.837 ms` | 25 |
| 8 | `0.419 ms` | 20 |
| 9 | `0.853 ms` | 27 |
| 10 | `0.124 ms` | 34 |
| 11 | `1.124 ms` | 18 |
| 12 | `1.538 ms` | 27 |
| 13 | `0.703 ms` | 25 |
| 14 | `0.723 ms` | 19 |

##### 原始评测归档

- [cuda_105492_raw.json](raw/cuda_105492_raw.json)

#### 本地 C500 验证（#105501 后续开发的阶段性记录）

##### 验证信息

- **设备/运行时**：MetaX C500，PyTorch `2.8.0+metax3.7.1.3`，MACA `3.7.1`；`flash_attn_with_kvcache` 仅作为本地 GPU reference，未安装或构建仓库子模块。
- **当时候选代码**：`solutions/cuda_maca_optimized.cpp`；相对于历史维护源 `solutions/cuda_maca_version.cpp`，将固定的 KV4/KV8 fast path 编译期特化，并将每页 softmax 直接累计到新的全局 max 标度，消除 `beta = exp(m_page - m_new)` 及其 5 次后续缩放。本节保留的是进入 OJ 连续优化前的本地筛选记录。
- **正确性**：`tests/c500_paged_decode_harness.py` 在真实 14 个 OJ shape 上完成 full-length、boundary-length 和随机长度/page-table padding-trap 验证，均为 14/14 Pass，且无 NaN/Inf 或超 `8×tol` 元素。
- **已发现并修复的本地问题**：原 MMA-QK dispatch 在本机完整 KV4 case 8/10/11/14 上无法满足 OJ 容差，而 scalar QK 在相同张量上通过。因此维护源已经停止派发该 candidate，保留其代码仅用于后续 fragment/layout 调查。

##### 本地交错 A/B

对 `cuda_maca_version.so`（control）和 `cuda_maca_optimized.so`（candidate）交替顺序进行 event timing；下表为 candidate/control p50。该数据是本地筛选依据，不与 OJ 的绝对时间或 aggregate 分数混用。

| case | candidate/control p50 | 本地加速 |
|---:|---:|---:|
| 7 | `0.8690x` | `1.151x` |
| 8 | `0.9644x` | `1.037x` |
| 9 | `0.8687x` | `1.151x` |
| 11 | `0.9658x` | `1.035x` |
| 12 | `0.8656x` | `1.155x` |
| 13 | `0.9360x` | `1.068x` |
| 14 | `0.9694x` | `1.032x` |

- 最大获益集中在 KV8 paired-QK 的 case 7/9/12（约 15%），显著超过同次 A/B 约 0.1% 的 ratio spread。
- 模板特化/softmax 路径先由 #105501 在 OJ 14/14 Accepted；随后 token-parallel/BSM 路径从 #105561 起完成 20 次连续 OJ Accepted，并在 #105915/#105932/#105952 达到 `57.43`。因此这里的 “WIP” 判断只代表提交前的历史阶段，不再是当前状态。

### 2026-08-07

#### 提交 #104552 · 2026-08-07 13:57:14

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104552)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.71`
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_fullpage_case79.cpp`
- **策略**：仅为 paired-token QK 的 case 7/9 加入每页 `t_base + 16 <= cache_seqlens[b]` 的完整页分支。完整页中移除 QK 和 scalar-PV 循环的 token-validity predicate；末页保留原有 logical-token tail mask，accepted uniform-source shuffle、CTA layout、split policy 和 reduce 均不变。

##### 结果分析

- 14/14 Accepted，说明完整页与末页分支的语义等价，仍严格按每个 batch 的 `cache_seqlens` 读取 valid page，未触及 `block_table` padding。
- 目标 case 7 为 **`0.895 ms`（23 分）**，差于 paired-QK 控制 #104441 `0.858 ms` / #104429 `0.845 ms`；case 9 为 **`0.904 ms`（25 分）**，也未超过 #104441 `0.866 ms`。两者没有出现预期的 2% 以上改善。
- 这表明 C500 对原循环的 predicate 已能有效调度，反而 duplicate full/tail loop body 增加了代码尺寸或寄存器压力。该微优化被拒绝；维护源继续使用紧凑的 accepted paired-QK kernel。
- 本次提交命令在 900 秒轮询期限内尚未结束，但 `--watch 104552` 后获得完整最终结果；原始归档已保存。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 4 | `0.069 ms` | 46 |
| 5 | `0.066 ms` | 41 |
| 6 | `0.082 ms` | 37 |
| 7 | **`0.895 ms`** | **23** |
| 8 | `0.399 ms` | 21 |
| 9 | **`0.904 ms`** | **25** |
| 10 | `0.114 ms` | 35 |
| 11 | `0.991 ms` | 20 |
| 12 | `1.600 ms` | 26 |
| 13 | `0.702 ms` | 25 |
| 14 | `0.522 ms` | 24 |

##### 原始评测归档

- [cuda_104552_raw.json](raw/cuda_104552_raw.json)

#### 提交 #104518 · 2026-08-07 13:27:30

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104518)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.14`
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_kv8_grouped_pv_case9.cpp`
- **策略**：只在 case 9 `(B=32, KV8, L=4096, GQA=4)` 将已 accepted 的 paired-token QK 保持不变；QK 后由四个 CTA owner 计算独立 FP32 online `(m,l)` 与 4×16 权重，`tid<64` 每个 V `uint32`（两个维度）只读取/转换一次并更新四个 query-head accumulator。其余 dispatch、split policy 和 reduce kernel 不变。

##### 结果分析

- 14/14 Accepted 验证了显式 ownership：每 warp 的 lane 0 在 accepted uniform-source QK broadcast 后写一行 logits；`tid<4` 独立写四行 softmax state/weights；`tid<64` 独占每一对 V 维度；尾 token 权重为零，空 split 仍输出 `(-inf, 0, 0)` partial。paged table clipping 与 stable split reduction 保持正确。
- case 9 为 **`1.325 ms`（19 分）**。这比 paired-QK 参考 #104441 的 `0.866 ms` 慢约 53%，也比已拒绝的 case-9 MMA-QK #104472 (`1.155 ms`) 更慢；不属于评测噪声范围。
- 虽然该设计消除了四份 V shared-memory load/BF16 conversion，它新增的全 CTA logits handoff、softmax publish、PV completion barriers，以及每个 V owner 维持四行 accumulator 的寄存器压力，显著超过了复用收益。pair-QK 原先的 warp-local PV 保持更高效，因此该 grouped-PV 路线被拒绝，不扩展到 case 7/12/13，也不并入维护源。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 4 | `0.069 ms` | 46 |
| 5 | `0.065 ms` | 41 |
| 6 | `0.092 ms` | 34 |
| 7 | `0.858 ms` | 24 |
| 8 | `0.398 ms` | 21 |
| 9 | **`1.325 ms`** | **19** |
| 10 | `0.114 ms` | 35 |
| 11 | `0.987 ms` | 20 |
| 12 | `1.585 ms` | 26 |
| 13 | `0.702 ms` | 25 |
| 14 | `0.529 ms` | 24 |

##### 原始评测归档

- [cuda_104518_raw.json](raw/cuda_104518_raw.json)

#### 提交 #104472 · 2026-08-07 12:48:56

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104472)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.43`
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_case9_mma.cpp`
- **策略**：仅将 case 9 `(B=32, KV8, L=4096)` 从 accepted paired-token QK 路由到既有 64-lane MMA-QK + FP32 scalar-PV kernel；case 7、所有 split policy、归约和其余 dispatch 均未改变。

##### 结果分析

- 14/14 正确，说明 64-lane MMA 的 GQA4 layout、paged-KV addressing、tail masking 和 split partial 输出在固定 KV8 规格上也是正确的。
- case 9 为 **`1.155 ms`（21 分）**，慢于同一 timing tier 的 accepted paired-QK control #104468 `0.858 ms`，也明显慢于 #104441 `0.866 ms`。即使考虑评测噪声，约 34% 的回退足以拒绝该方向。
- 这与结构成本一致：KV8/GQA4 仅使用 MMA `16×16` score tile 的 4 个 M rows，仍需执行完整 16 行 tile，同时额外承担 Q/K staging、score materialization 和同步；一波 CTA 的 V 复用不足以抵消这些成本。因此 KV8 long cases 保持 paired-token QK，MMA-QK 仅保留已验证的 KV4/GQA8 dispatch。

##### 原始评测归档

- [cuda_104472_raw.json](raw/cuda_104472_raw.json)

#### 提交 #104468 · 2026-08-07 12:38:05

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104468)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.00`
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_lb128_case7.cpp`
- **策略**：只为 case 7 `(B=64, KV8, L=2048)` duplicate 已 accepted 的 paired-token QK code，并把声明从 `__launch_bounds__(256, 6)` 改为精确的 `__launch_bounds__(128)`；运行时 CTA 原本就是 128 threads，其他 case 均未改变。

##### 结果分析

- 14/14 正确；case 7 为 **`0.854 ms`（24 分）**，位于 accepted control #104429 `0.845 ms` 与 #104441 `0.858 ms` 的正常波动区间。
- 因此 C500 会接受精确 launch-bounds 声明，但它没有可重复的时延收益。为避免维护相同 kernel 的重复源码，不合入此专用 variant；保留 accepted shared paired-QK definition。
- aggregate `39.00` 仍低于 #104429 的 `40.07`，不能取代最高记录。

##### 原始评测归档

- [cuda_104468_raw.json](raw/cuda_104468_raw.json)

#### 提交 #104461 · 2026-08-07 12:25:06

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104461)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer / `38.43`
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_case6_case5_case10_mma_qk_pair_broadcast8_case7.cpp`
- **策略**：仅在 case 7 `(B=64, KV8, L=2048)` 用一个独立 kernel 替换 paired-QK 的 logit broadcast：每个 16-lane subgroup 保留自己计算的 8 个 parity logits，仅以 8 个 shuffle 从另一个 subgroup 获取剩余 8 个；其他 case 和 split/softmax/PV 路径不变。

##### 结果分析

- 主机端 ownership 检查证明每 lane 在逻辑上最终拥有完整 16 logits，且 `test_kernel_logic.py` 为 **23/23 通过**；这只能证明数学数据流，不能证明 C500 shuffle 指令的实际语义。
- case 7 发生数值 WrongAnswer：`14,922` 个元素超过 `8×` tolerance，最大绝对误差 `2.5703125`；评测记录的该 case 时间为 **`35,819.191 ms`**，它包含 checker/失败处理，不作为 kernel 性能计时。其余 13 个 case 均 Accepted。
- 失败原因是该形式令 `__shfl_sync` 的 source lane 在同一 SIMD 指令内随 `pair_group` 分歧（lane 0–15 请求 16，lane 16–31 请求 0）。虽然这个用法在逻辑模拟中成立，C500 对此跨 16-lane subgroup 的行为不具备可用的正确性保证。保留原有 16 次 uniform-source broadcast；后续 paired-QK 变体不得使用 lane-dependent source lane。

##### 原始评测归档

- [cuda_104461_raw.json](raw/cuda_104461_raw.json)

#### 提交 #104441 · 2026-08-07 11:58:28

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104441)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.64`
- **代码**：`solutions/cuda_maca_version.cpp`
- **策略**：对 #104429 的唯一策略差异作同期复测：case 8 恢复 `n_split=32`（8 页/partial）；其余已验证的 MMA-QK、paired-token QK 和 split policy 保持不变。

##### 结果分析

- case 8 为 **`0.401 ms`（21 分）**，快于 #104429 的 `n_split=24` / 11 页 **`0.409 ms`**。同一时间段的直接对照消除了“24 splits 带来 case-8 收益”的可能；长期组合应保持 `n_split=32` / 8 页路径。
- 同轮其他 case 也处于更慢 timing tier：case 5 `0.066 ms`、case 6 `0.092 ms`、case 11 `0.987 ms`、case 12 `1.600 ms`、case 14 `0.529 ms`。因此 aggregate `38.64` 不与 #104429 的 `40.07` 直接比较。
- case 10 仍为精确复现的 **`0.114 ms`（35 分）**，进一步支持 MMA-QK + `n_split=128` / 4 页为稳定结构性组合。CPU 数学回归亦为 23/23 通过。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 4 | `0.069 ms` | 46 |
| 5 | `0.066 ms` | 41 |
| 6 | `0.092 ms` | 34 |
| 7 | `0.858 ms` | 24 |
| 8 | `0.401 ms` | 21 |
| 9 | `0.866 ms` | 26 |
| 10 | `0.114 ms` | 35 |
| 11 | `0.987 ms` | 20 |
| 12 | `1.600 ms` | 26 |
| 13 | `0.709 ms` | 25 |
| 14 | `0.529 ms` | 24 |

##### 原始评测归档

- [cuda_104441_raw.json](raw/cuda_104441_raw.json)

#### 提交 #104429 · 2026-08-07 11:38:43

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104429)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`40.07`**
- **代码**：`solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_split24_case6_case5_case10_mma_qk.cpp`
- **策略**：仅将 case 8 `(B=16, KV4, L=4096)` 从已建立的 `n_split=32`（8 页/partial）切到 `n_split=24`（11 页/partial、1536 个 split CTA）；case 10 的 MMA-QK 与 `n_split=128` / 4 页策略及其他 dispatch 均保持。

##### 结果分析

- case 8 测得 **`0.409 ms`（21 分）**。这慢于同一 MMA-QK 路径上已反复观察到的 `n_split=32` / 8 页结果约 `0.386–0.390 ms`，故 11 页不能作为 case-8 的已验证替换策略。
- 本轮 case 10 为 **`0.107 ms`（37 分）**，优于两次独立复测已确认的 `0.114 ms`；这属于已验证 MMA-QK + 4 页路径的有利 timing sample，不能归因于与其无关的 case-8 修改。
- 尽管目标 case 回退，14/14 全部正确且 aggregate 刷新至 `40.07`。保留本源作为当前最高真实 OJ 记录，同时保留原 `n_split=32` 源作为更强的逐 case 结构性基线；后续需同一时期复测原策略，避免以 aggregate 波动误判 case-8 决策。

##### 测试点汇总

| case | 时间 | 分数 |
|---:|---:|---:|
| 4 | `0.064 ms` | 48 |
| 5 | `0.056 ms` | 45 |
| 6 | `0.082 ms` | 37 |
| 7 | `0.845 ms` | 24 |
| 8 | `0.409 ms` | 21 |
| 9 | `0.871 ms` | 26 |
| 10 | `0.107 ms` | 37 |
| 11 | `0.975 ms` | 20 |
| 12 | `1.589 ms` | 26 |
| 13 | `0.701 ms` | 25 |
| 14 | `0.521 ms` | 24 |

##### 原始评测归档

- [cuda_104429_raw.json](raw/cuda_104429_raw.json)

#### 提交 #104419 · 2026-08-07 11:27:27

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104419)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.79`
- **策略**：仅将 case 6 `(B=16, KV8, L=362)` 改成 `n_split=6`（约 4 页/partial，768 split CTA）；仍使用原标量 QK，case-10 MMA-QK / 4 页策略保持。

##### 结果分析

- case 6 测得 **`0.096 ms`（33 分）**，慢于当前 `n_split=8` / 约 3 页策略在可比结果中的 `0.082 ms`（37 分）。因此 3 页仍是已测试的最佳切分颗粒度。
- 与 #104394 的 paired-QK 负结果共同说明 case 6 的最佳组合是：标量 QK + `n_split=8`，不要减少 split 或套用 long-KV paired QK。
- 14/14 正确；最高 aggregate 保持 #104334 的 `39.86`，而结构性组合基线继续使用 case-10 MMA-QK 的 #104368 源。

##### 原始评测归档

- [cuda_104419_raw.json](raw/cuda_104419_raw.json)

#### 提交 #104406 · 2026-08-07 11:11:58

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104406)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.43`
- **策略**：仅将 case 5 `(B=16, KV4, L=141)` 从精确 `n_split=3` 调为 `n_split=2`，即 5 页/partial；case 10 的 64-lane MMA-QK 和 4 页 split 策略保持。

##### 结果分析

- case 5 测得 **`0.080 ms`（36 分）**，远慢于 #104328/#104334 的 `n_split=3` / 3 页策略 `0.056 ms`（45 分）。对这个 9-page shape，减少 partial 会同时损失并行度和细粒度 LSE/PV 局部工作分解。
- 这补全 case 5 的关键曲线：9 页 generic `0.071 ms`、5 页 `0.080 ms`、3 页 `0.056 ms`，因此保留 `n_split=3`，不再向较少 split 试探。
- 全部 14 case 正确；当前最高 aggregate 记录依然是 #104334 `39.86`，但之后的组合候选必须保留 case-10 MMA-QK 结构性收益。

##### 原始评测归档

- [cuda_104406_raw.json](raw/cuda_104406_raw.json)

#### 提交 #104394 · 2026-08-07 11:00:57

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104394)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.79`
- **策略**：仅把 case 6 `(B=16, KV8, L=362)` 加入已验证的 16-lane paired-token QK dispatch；其既有 split policy 仍为 `n_split=8`（约 3 页/partial）。

##### 结果分析

- case 6 测得 `0.087 ms`（36 分），慢于相邻相同组合、仅使用标量 QK 的 #104386 `0.082 ms`（37 分）。此序列只有约 3 页/CTA，paired QK 的 extra Q-register load、subgroup broadcast 与控制成本不能摊销。
- case 7/9/12/13 的 paired-token long-KV dispatch 保持不变；case 10 的 MMA-QK `0.114 ms` 亦保持。因而 case 6 不加入长期组合。
- #104394 的 aggregate 不替代 #104334 的最高 `39.86`；该 OJ timing tier 中多个未改路径也较慢。

##### 原始评测归档

- [cuda_104394_raw.json](raw/cuda_104394_raw.json)

#### 提交 #104386 · 2026-08-07 10:47:52

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104386)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.64`
- **策略**：保留 case 10 的 64-lane KV4 MMA-QK，唯一改变为 `n_split=192`（3 页/partial）以重扫 MMA 后的 split 边界。

##### 结果分析

- case 10 为 **`0.132 ms`（32 分）**，显著慢于 #104368/#104380 的 MMA `n_split=128` / 4 页 partial 的稳定 **`0.114 ms`（35 分）**。MMA 缩短每页 QK 后，额外 partial 和 reduce 开销依然没有被更多 CTA 抵消。
- 本轮 aggregate `39.64` 是一个较好的环境计时样本，但不能替代 #104334 的 `39.86`；case 10 的负向直接对照是确定性的。
- case-10 MMA split boundary 因此固定为 `n_split=128` / 4 页。下一个独立低成本试点改为 case 6：它是尚未测试 paired-token QK 的 KV8 shape，并且当前有 1024 个 3 页 split CTA，适合验证该已获益 QK 重构能否缩短中长序列。

##### 原始评测归档

- [cuda_104386_raw.json](raw/cuda_104386_raw.json)

#### 提交 #104380 · 2026-08-07 10:36:37

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104380)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.64`
- **策略**：#104368 源文件不作修改的独立复测。

##### 结果分析

- case 10 再次精确测得 **`0.114 ms`（35 分）**，与 #104368 一致。这确认 KV4 64-lane MMA-QK 与 `n_split=128` / 4 页 partial 的组合不是一次性噪声。
- 两次运行 aggregate 均为 `38.64`，同时非 case-10 路径也显示完全相同的较慢样本；这说明当前 OJ 批次存在环境级 timing tier。#104334 的 `39.86` 仍为最高记录，但本 candidate 是后续组合/复测应使用的结构性基线。
- 下一步只重新扫描 case 10 的 split boundary：MMA 降低了每页 QK 工作，可能改变 scalar-only sweep 得出的 4 页最优点；首先测试 3 页/`n_split=192`。

##### 原始评测归档

- [cuda_104380_raw.json](raw/cuda_104380_raw.json)

#### 提交 #104368 · 2026-08-07 10:23:40

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104368)

- **提交语言/环境**：CUDA Maca C500 / 45.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.64`
- **策略**：保留 case 10 `(B=1, KV4, L=8192)` 的 `n_split=128` / 4 页 partial，仅将其 QK 替换为已在 KV4 长序列证明正确的 64-lane BF16→FP32 MMA 路径；PV、softmax、split reduce 均保持 FP32 标量/既有实现。

##### 结果分析

- case 10 从 #104328 的 `0.124 ms`（34 分）降至 **`0.114 ms`（35 分）**，较 scalar 4 页版本再降 **8.1%**；14/14 正确。这是 case 10 目前最快的真实 OJ 结果。
- 本次 aggregate `38.64` 不应替代 #104334 的最高总分 `39.86`：本轮所有无关路径同时明显变慢，例如 case 5 `0.066 ms`、case 6 `0.092 ms`、case 8 `0.400 ms`。唯一算法改动是 case 10 dispatch，不能引起这些 case 的退化。
- 该结果推翻了此前“case 10 MMA-QK 无可复现收益”的旧结论：在 generic 8 页 partial 时收益不稳定，但与 case-10 4 页 split policy 结合后有明确收益。应将 MMA-QK 纳入下一份组合候选，并通过同源复测追踪 aggregate。

##### 原始评测归档

- [cuda_104368_raw.json](raw/cuda_104368_raw.json)

#### 提交 #104355 · 2026-08-07 10:01:39

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104355)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.43`
- **策略**：仅将 case 12 `(B=8, KV8, L=32768)` 设为 `n_split=192`（11 页/partial，12,288 个 split CTA）。

##### 结果分析

- case 12 测得 `1.574 ms`（26 分），表面上接近甚至略低于此前 8 页策略附近的 `1.578–1.590 ms`，但本轮无关 case 也普遍变慢（例如 case 5 `0.066 ms`、case 6 `0.092 ms`、case 10 `0.131 ms`），aggregate 因而降至 `38.43`。
- 此单轮无法证明 11 页优于现有 8 页 / `n_split=256` 路径；不将其合入当前最高 aggregate 源 #104334。现有 curve 的可靠结论仍是 16 页与 8 页均在相近噪声带，且 8 页曾参与最佳组合结果。
- 继续工作应转向结构性 D128 QK/PV 设计，而非在 case-12 8–16 页之间进行低信息的微调。

##### 原始评测归档

- [cuda_104355_raw.json](raw/cuda_104355_raw.json)

#### 提交 #104341 · 2026-08-07 09:39:56

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104341)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.79`
- **策略**：仅将 case 11 `(B=16, KV4, L=12251)` 调整为 `n_split=48`（generic `16×3`，16 页/partial）。

##### 结果分析

- case 11 为 `0.981 ms`（20 分），慢于现有 `n_split=64` / 12 页路径在相邻真实提交中的 `0.975–0.978 ms`；16 页并未改善 12 页策略。
- 已确认的曲线为 24 页 `1.028 ms`、16 页 `0.981 ms`、12 页 `0.975–0.978 ms`、8 页 `1.000 ms`、6 页 `1.032 ms`。因此保留 case 11 的 `n_split*=4`（12 页/partial），本 sweep 结束。
- OJ 排队耗时超过默认轮询时限，但实际评测完成后为 14/14 Accepted；结果已由 `--watch 104341` 归档。

##### 原始评测归档

- [cuda_104341_raw.json](raw/cuda_104341_raw.json)

#### 提交 #104335 · 2026-08-07 09:28:49

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104335)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.71`
- **策略**：仅把 case 10 `(B=1, KV4, L=8192)` 设为 `n_split=192`，即 3 页/partial、768 CTA。

##### 结果分析

- case 10 为 `0.126 ms`（33 分）：比 2 页策略的 `0.127 ms` 略好，但仍不如 4 页策略 #104328 的 `0.124 ms`（34 分）。
- 三个相邻点形成明确边界：4 页 / 128 split = `0.124 ms`，3 页 / 192 split = `0.126 ms`，2 页 / 256 split = `0.127 ms`。因此 case 10 的 split sweep 完成，继续使用 4 页/partial 的 `n_split=128` 路径；最高 aggregate 记录仍是 #104334 的 `39.86`。

##### 原始评测归档

- [cuda_104335_raw.json](raw/cuda_104335_raw.json)

#### 提交 #104334 · 2026-08-07 09:19:37

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104334)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`39.86`**
- **当前最高真实 OJ 分数**：由 case 10 `(B=1, KV4, L=8192)` 的 `n_split 64→256`（8→2 页/partial）候选获得。该提交是总分记录，但并未改善该目标 case 的单项时延。

##### 结果分析

- case 10 使用 1024 CTA，测得 `0.127 ms`（33 分），比 #104328 的 `0.124 ms`（34 分）略差，表明 2 页/partial 已越过该 case 的最佳分块区间或处于 OJ 波动范围。
- 其余 case 正确且时序在相邻提交的噪声带内；case 11 `0.975 ms`、case 12 `1.578 ms` 的偶然改善将 aggregate 推到 **`39.86`**。
- 因为目标 case 的直接比较不支持 2 页策略，继续单独测试 3 页区间（优先 `n_split=192`）；保留 #104334 作为当前最高 aggregate OJ 记录，并保留 #104328 的 4 页策略作为 case-10 的单项参考。

##### 原始评测归档

- [cuda_104334_raw.json](raw/cuda_104334_raw.json)

#### 提交 #104328 · 2026-08-07 09:04:55

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104328)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`39.79`**
- **当前最高真实 OJ 分数**：#104322 的 case 5 精确 3-split 策略保持不变；仅将 case 10 `(B=1, KV4, L=8192)` 的 `n_split 64→128`。

##### 结果分析

- case 10 由 8 页/partial（256 CTA）变为 4 页/partial（512 CTA），时延 `0.142→0.124 ms`，评分 `31→34`。该标量 KV4 B=1 路径也能显著受益于高于 generic 1024-work-target 的 split parallelism。
- case 5 `0.056 ms`、case 6 `0.082 ms`、case 7 `0.848 ms`、case 8 `0.390 ms`、case 11 `0.977 ms`、case 12 `1.590 ms` 均保持期望范围；14/14 正确，总分刷新为 **`39.79`**。
- 下一点直接测试 `n_split=256`（2 页/partial，1024 CTA），以确定 case 10 的过度切分边界。

##### 原始评测归档

- [cuda_104328_raw.json](raw/cuda_104328_raw.json)

#### 提交 #104327 · 2026-08-07 08:55:48

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104327)

- **提交语言/环境**：CUDA Maca C500 / 45.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.57`
- **性质**：只把 case 4 `(B=64, KV8, L=64)` 从 1 个 4-page partial 改成 2 个 2-page partial。

##### 结果分析

- case 4 从 `0.064→0.070 ms`，评分 `48→46`。该 shape 已有 512 CTA，只有 4 个 page，额外 partial-buffer 与 reduce 远大于有限的 page-loop 缩短收益。
- 固定保留 case 4 的 generic `n_split=1`。当前最高真实 OJ 仍是 #104318/#104322 的 `39.71`；后续任何新候选都从无 case-4 override 的 #104322 继承。

##### 原始评测归档

- [cuda_104327_raw.json](raw/cuda_104327_raw.json)

#### 提交 #104322 · 2026-08-07 08:47:04

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104322)

- **提交语言/环境**：CUDA Maca C500 / 45.4 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `39.71`
- **性质**：仅将 #104318 的 case 5 `n_split=4` 改为精确 `n_split=3`。

##### 结果分析

- 两个配置的页上界同为 3；`n_split=3` 正好覆盖 9 个 cache page，避免 `n_split=4` 的最后一个空 partial。case 5 仍为 `0.056 ms`、45 分，总分也同为 `39.71`。
- 以 `n_split=3` 为 case 5 的规范化策略：性能不变而减少一组 partial 输出/merge work。后续 case 4 测试从此源继承全部已验证 dispatch。

##### 原始评测归档

- [cuda_104322_raw.json](raw/cuda_104322_raw.json)

#### 提交 #104318 · 2026-08-07 08:38:13

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104318)

- **提交语言/环境**：CUDA Maca C500 / 45.2 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`39.71`**
- **当前最高真实 OJ 分数**：在 #104314 的所有长/中上下文策略上，只为 case 5 `(B=16, KV4, L=141)` 固定 `n_split=4`。

##### 结果分析

- case 5 有 9 个 cache page；generic 单 split 只创建 64 个 CTA。`n_split=4` 将逻辑 partial 长度压至最多 3 页，提升为 256 CTA，时延 `0.071→0.056 ms`，评分 `39→45`。
- 所有其他关键路径维持当前区间：case 6 `0.082 ms`、case 7 `0.851 ms`、case 8 `0.389 ms`、case 11 `0.980 ms`、case 12 `1.582 ms`。14/14 正确，总分刷新至 **`39.71`**。
- 由于 9 page 在 4 splits 下的最后一份为空，下一项测试精确 `n_split=3`（仍为 3 页/partial、无空 partial）来减少 reduce 和空 CTA 开销。

##### 原始评测归档

- [cuda_104318_raw.json](raw/cuda_104318_raw.json)

#### 提交 #104316 · 2026-08-07 08:29:24

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104316)

- **提交语言/环境**：CUDA Maca C500 / 45.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.00`
- **性质**：只把 case 6 的 split 从 #104314 的 `n_split=8` 改为 12（23 页按最多 2 页/partial 切分）。

##### 结果分析

- case 6 为 `0.089 ms`，劣于 #104314 的 `0.082 ms`；同时所有不相关 case 也同步变慢，说明本次存在全局噪声。不过 12 个 partial 并未显出超过 8 个 partial 的收益。
- 选择 `n_split=8` 作为 case 6 的固定策略：它已将 generic `0.117 ms` 大幅降至 `0.082 ms`，又避免 12-way 路径的更多 partial/reduce 开销。停止 case 6 split sweep。

##### 原始评测归档

- [cuda_104316_raw.json](raw/cuda_104316_raw.json)

#### 提交 #104314 · 2026-08-07 08:20:40

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104314)

- **提交语言/环境**：CUDA Maca C500 / 45.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`39.29`**
- **当前最高真实 OJ 分数**：在 #104307 的长上下文优化路径上，仅为 case 6 `(B=16, KV8, L=362)` 固定 `n_split=8`。

##### 结果分析

- generic policy 为 `n_split=3`、每 CTA 约 8 页、总计 384 CTA；固定 `n_split=8` 后每 CTA 约 3 页、总计 1024 CTA。case 6 时延 `0.117→0.082 ms`，评分 `29→37`，是当前最显著的单项积分提升。
- 其余路径保持稳定：case 7 `0.847 ms`、case 8 `0.388 ms`、case 9 `0.861 ms`、case 11 `0.977 ms`、case 12 `1.582 ms`。14/14 正确，聚合总分跃升为 **`39.29`**。
- 下一点不盲目倍增到 16 splits，而先验证 `n_split=12`（同为 2 页上界但少于 16 个 partial），定位 case 6 的 reduce/parallelism 平衡。

##### 原始评测归档

- [cuda_104314_raw.json](raw/cuda_104314_raw.json)

#### 提交 #104312 · 2026-08-07 08:11:36

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104312)

- **提交语言/环境**：CUDA Maca C500 / 45.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.71`
- **性质**：在 #104307 的最佳路径上，仅将 case 14 `(B=1, KV4, L=61519)` 从 generic `n_split=256` 翻倍到 512。

##### 结果分析

- case 14 从约 16 页/partial 压到 8 页/partial 后，`0.520→0.543 ms`。该固定 B=1 路径的额外 partial/reduce 开销大于 CTA 内 page-scan 缩短的收益。
- 保留 case 14 的 generic `n_split=256`；不再为此 shape 测试更高 split。当前最佳仍为 #104307 / `38.79`。

##### 原始评测归档

- [cuda_104312_raw.json](raw/cuda_104312_raw.json)

#### 提交 #104310 · 2026-08-07 08:02:47

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104310)

- **提交语言/环境**：CUDA Maca C500 / 44.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.71`
- **性质**：case 8 的 split 从 #104307 的 8 页/partial 继续压缩为 4 页/partial；其他路径不变。

##### 结果分析

- case 8 `0.398 ms`，慢于 #104307 的 `0.386 ms`，评分 `22→21`。这在同一稳定快速环境的相邻提交中直接确认了 4 页已经越过 split/reduce 的过度切分点。
- 因此 case 8 固定回 #104307 的 `n_split=32` / 8 页/partial；当前最佳源不变为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_split2x.cpp`。

##### 原始评测归档

- [cuda_104310_raw.json](raw/cuda_104310_raw.json)

#### 提交 #104307 · 2026-08-07 07:54:02

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104307)

- **提交语言/环境**：CUDA Maca C500 / 44.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.79`**
- **当前最高真实 OJ 分数**：在 #104301 的 case 7/9/12/11 split 策略上，仅将 case 8 `(B=16, KV4, L=4096)` 从 generic 16 页/partial 提高至 8 页/partial。

##### 结果分析

- case 8：`n_split 16→32`、`16→8` 页/partial、CTA `1024→2048`，时延 `0.432→0.386 ms`，评分 `20→22`。这是当前 sweep 中最显著的相对单 case 收益之一。
- case 7 `0.850 ms`、case 9 `0.856 ms`、case 11 `0.971 ms`、case 12 `1.588 ms` 均保持此前优化路径的预期区间。14/14 正确，聚合总分刷新为 **`38.79`**。
- 当前最佳源为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_case11_case8_split2x.cpp`。下一点将 case 8 压至 4 页/partial（`n_split=64`）以探测过度切分边界；case 14 保持独立，避免耦合评测。

##### 原始评测归档

- [cuda_104307_raw.json](raw/cuda_104307_raw.json)

#### 提交 #104306 · 2026-08-07 07:44:57

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104306)

- **提交语言/环境**：CUDA Maca C500 / 44.5 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.29`
- **性质**：case 11 使用 `n_split=128`，每 partial 为 6 页；所有其他 #104301 dispatch 保持不变。

##### 结果分析

- case 11 `1.032 ms`，慢于 #104302 的 8 页 `1.000 ms` 与 #104301 的 12 页 `0.978 ms`。即使此轮环境整体较慢，6 页相对于同轮的 8 页也仍退化 `0.032 ms`，过度切分边界已经明确。
- 因此固定采用 #104301 的 case-11 `n_split=64`（12 页/partial）：该点在 48→24→12 页单调改善后达到最优，8/6 页均未带来可确认收益。停止这一 case 的 split sweep。

##### 原始评测归档

- [cuda_104306_raw.json](raw/cuda_104306_raw.json)

#### 提交 #104302 · 2026-08-07 07:36:12

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104302)

- **提交语言/环境**：CUDA Maca C500 / 44.5 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.29`
- **性质**：case 11 显式 `n_split=96`，使 766 个 KV page 分配为 8 页/partial。

##### 结果分析

- case 11 为 `1.000 ms`，在本轮全局慢速环境中，未超过 #104301 的 12 页路径 `0.978 ms`；其余未更改 case 同时大幅变慢，不能把两者的 `0.022 ms` 差异作为最终临界点判定。
- 该结果已显示 8 页不是明显优于 12 页的方向。唯一剩余的高信息点是 6 页/partial (`n_split=128`)；完成该边界试验后结束 case-11 split sweep，并转向 case 8。

##### 原始评测归档

- [cuda_104302_raw.json](raw/cuda_104302_raw.json)

#### 提交 #104301 · 2026-08-07 07:27:24

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104301)

- **提交语言/环境**：CUDA Maca C500 / 44.5 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.57`**
- **当前最高真实 OJ 分数**：cases 7/9/12 维持 8 页/partial，case 11 的 split 数从 generic `16→64`，每 partial 为 12 页。

##### 结果分析

- case 11：`48→12` 页/partial、CTA `1024→4096`，时延 `1.117→0.978 ms`，评分 `18→20`。与 #104299 的 24 页路径 `1.028 ms` 一起构成稳定的单调优化趋势。
- 其余目标路径处于当前最优量级：case 7 `0.845 ms`、case 9 `0.859 ms`、case 12 `1.590 ms`。14/14 正确，总分从 #104298 的 `38.43` 提升到 **`38.57`**。
- 继续在 case 11 插入精确 8 页/partial 的 `n_split=96`（generic 的 6x）；这比直接压到 6 页的 8x 设置更能定位过度切分转折。

##### 原始评测归档

- [cuda_104301_raw.json](raw/cuda_104301_raw.json)

#### 提交 #104299 · 2026-08-07 07:18:42

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104299)

- **提交语言/环境**：CUDA Maca C500 / 44.5 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.29`
- **性质**：在 #104298 的 case 7/9/12 8 页/partial 设置上，只将 case 11 `(B=16, KV4, L=12251)` 的 `n_split 16→32`。

##### 结果分析

- case 11 从 generic 的 `48→24` 页/partial，CTA 约 `1024→2048`，时延从 #104298 的 `1.117 ms` 降至 `1.028 ms`，评分 `18→19`。尽管此轮所有未改 case 都整体变慢（如 case 7 `0.846→0.861`、case 8 `0.424→0.444`），case 11 仍大幅改善，证明其收益是结构性的。
- 总分 `37.29` 低是环境性能波动，不能覆盖单独变更的 case-11 强收益。继续测试 12 页/partial (`n_split=64`) 以寻找此 KV4 长序列的分块临界点。

##### 原始评测归档

- [cuda_104299_raw.json](raw/cuda_104299_raw.json)

#### 提交 #104298 · 2026-08-07 07:09:39

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104298)

- **提交语言/环境**：CUDA Maca C500 / 44.3 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.43`**
- **当前最高真实 OJ 分数**：case 7/9/12 全部采用 8 页/partial 的固定分块路径；源文件为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_split16x.cpp`。

##### 结果分析

- case 12 的 `n_split=256`（8 页/partial，16384 CTA）获得 `1.579 ms`，明显好于 32 页的 `1.643 ms`，但与 #104294 的 16 页 `1.569 ms` 只相差 `0.010 ms`；后者仍是该 case 的最低单次时延。两者处于 OJ 测量噪声带内，因此以 #104298 的更高实际聚合分数作为当前提交基线。
- case 7 `0.846 ms`、case 9 `0.863 ms` 保持已经验证的 8 页/partial 吞吐水平；case 8 `0.424 ms`、case 11 `1.117 ms` 也处于该轮相对较好区间。14/14 正确，总分刷新到 `38.43`。
- case 12 的单调分块收益已在 `128→64→32→16` 页之间证实，8 页接近饱和。停止继续压缩 case 12；下一项转向 case 11 的独立 split-parallelism 测试，其当前 48 页/partial 仍比已验证高效粒度更粗。

##### 原始评测归档

- [cuda_104298_raw.json](raw/cuda_104298_raw.json)

#### 提交 #104294 · 2026-08-07 07:00:58

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104294)

- **提交语言/环境**：CUDA Maca C500 / 44.3 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.21`
- **性质**：case 12 单独使用 `n_split=128`（16 页/partial，8192 CTA）；case 7/9 仍保留 8 页/partial。

##### 结果分析

- case 12 持续改善：`1.643→1.569 ms`，评分 `25→26`，验证其 split-parallelism 曲线在 16 页/partial 处仍未反转。
- 聚合分数低于 #104293 并不代表目标路径退化：#104294 的 test 2、case 11 等未修改路径同时波动，而 case 12 是唯一结构变更且有明确增益。保留 #104293 的 `38.36` 作为最高单次总分记录，同时以 #104294 的 case-12 数据继续边界搜索。
- 下一点为 8 页/partial（`n_split=256`）：它与 case 7/9 的已验证局部最优颗粒度相同，能直接检验 case 12 是否可在 16384 CTA 下继续获益。

##### 原始评测归档

- [cuda_104294_raw.json](raw/cuda_104294_raw.json)

#### 提交 #104293 · 2026-08-07 06:52:18

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104293)

- **提交语言/环境**：CUDA Maca C500 / 44.3 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.36`**
- **当前最高真实 OJ 分数**：case 7/9 维持 8 页/split，case 12 从 #104290 的 64 页/partial 继续缩短到 32 页/partial。

##### 结果分析

- case 12：`n_split 16→64`（generic 的 4x），约 `1024→4096` CTA，`1.793→1.643 ms`，评分 `24→25`。连续 `128→64→32` 页/partial 都获益，说明该大 KV8 shape 仍远未遇到 split-reduce 的临界点。
- case 7 `0.851 ms`、case 9 `0.864 ms`、其他不相关路径均保持可信区间；全体 14 case 正确，总分升至 `38.36`。
- 当前最佳源为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_case12_split4x.cpp`。按已验证的单调趋势，继续测试 case 12 16 页/partial（`n_split=128`）是成本最低、信息增益最高的下一个点。

##### 原始评测归档

- [cuda_104293_raw.json](raw/cuda_104293_raw.json)

#### 提交 #104290 · 2026-08-07 06:43:39

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104290)

- **提交语言/环境**：CUDA Maca C500 / 44.3 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.29`**
- **当前最高真实 OJ 分数**：在 #104278 的 case 7/9 8 页/split 路径上，仅将 case 12 `(B=8, L=32768, KV8)` 的 split 数 `16→32`。

##### 结果分析

- case 12：每 partial 从 `128→64` 页，split CTA 从约 `1024→2048`；时延 `1.793 ms`，显著优于此前 #104278 的 `1.996 ms`，评分 `22→24`。
- case 7 `0.852 ms`、case 9 `0.864 ms`，维持 #104278 的已验证量级；其他路径没有功能变更。所有 14 case 正确，总分首次达到 `38.29`。
- 这证明分块 page-scan 仍是 case 12 的关键瓶颈，且它也能从约 2048 CTA 获益。下一条直接测试 case 12 `n_split=64`（32 页/partial、4096 CTA），保持 case 7/9 与全部其余 dispatch 不变。

##### 原始评测归档

- [cuda_104290_raw.json](raw/cuda_104290_raw.json)

#### 提交 #104288 · 2026-08-07 06:35:10

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104288)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.00`
- **性质**：按 shape 拆分局部策略：case 7 为 8 页/split，case 9 为 7 页/split。

##### 结果分析

- case 7 `0.849 ms`，与 #104278 的 `0.848 ms` 等价；case 9 `0.858 ms`，与 #104278 的 `0.857 ms` 等价。局部 7 页/8 页策略没有产生可重复的确定增益。
- 总分低于 #104278 的 `38.21`，同时 case 11/12 存在独立测量回退。因此不采纳此变体，继续以统一 8 页/split 的 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_split8x.cpp` 为已有最佳基础。

##### 原始评测归档

- [cuda_104288_raw.json](raw/cuda_104288_raw.json)

#### 提交 #104285 · 2026-08-07 06:26:01

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104285)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.79`
- **性质**：case 7/9 均使用 `n_split *= 10`，给出 7 页/split 的局部插值点。

##### 结果分析

- 与同一慢速轮次的 #104282（8 页/split）比较：case 7 `0.862 > 0.856 ms`，case 9 `0.866 < 0.871 ms`。差异只有 `0.006/0.005 ms`，无法用一次含全局噪声的评测确认单一共同 split 更优。
- 该结果支持按固定 shape 分别调度：case 7 暂保留 8 页/split，case 9 值得单独验证 7 页/split。它不改变 #104278 / `38.21` 作为当前最高记录的结论。

##### 原始评测归档

- [cuda_104285_raw.json](raw/cuda_104285_raw.json)

#### 提交 #104282 · 2026-08-07 06:17:21

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104282)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.79`
- **性质**：#104278 的相同 8 页/split 源复测，用作 #104281 的环境校准。

##### 结果分析

- #104282 相对于 #104278 的所有 case 都变慢，证明 #104281 的低总分主要包含 OJ 全局性能波动，不能拿它直接同早先最佳横比。
- 与同一轮 #104281 相比，8 页路径仍在受关注 case 更快：case 7 `0.856 < 0.861 ms`、case 9 `0.871 < 0.877 ms`。这排除了 6 页明显优于 8 页的可能。
- 继续保留 #104278（`38.21`）为最佳归档；后续只测试产生 7 页/split 的 10x policy，以最小实验数补齐局部拐点。

##### 原始评测归档

- [cuda_104282_raw.json](raw/cuda_104282_raw.json)

#### 提交 #104281 · 2026-08-07 06:08:38

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104281)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.79`
- **性质**：case 7/9 使用 `n_split *= 12`，即 nominal 6 页/split 的中间点。

##### 结果分析

- case 7 为 `0.861 ms`、case 9 为 `0.877 ms`，均未超过 #104278 的 8 页/split 成绩 `0.848/0.857 ms`。
- 本次所有不相关 case 也同步变慢（例如 case 8 `0.439→0.451 ms`、case 10 `0.142→0.149 ms`、case 13 `0.703→0.709 ms`），表明该次 OJ 测量有明显全局噪声；不能把 6 页/split 的小幅目标退化单独归因于 split 选择。
- 随后的同源 #104282 复测也整体慢（总分同为 `36.79`），确认本轮存在全局慢速环境；但在同一轮直接对照下，#104282 的 8 页路径仍以 case 7/9 `0.856/0.871 ms` 小幅优于 #104281 的 nominal 6 页路径 `0.861/0.877 ms`。因此不改变 #104278 为当前最佳的结论，下一点只测 7 页/split。

##### 原始评测归档

- [cuda_104281_raw.json](raw/cuda_104281_raw.json)

#### 提交 #104279 · 2026-08-07 05:59:48

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104279)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `38.07`
- **性质**：仅将 case 7/9 从 #104278 的 8 页/split 继续压缩为 4 页/split。

##### 结果分析

- case 7：`n_split 2→32`（generic 16x）后为 `0.876 ms`，劣于 #104278 的 `0.848 ms`。
- case 9：`n_split 4→64`（generic 16x）后为 `0.887 ms`，劣于 #104278 的 `0.857 ms`，评分也由 27 回落至 26。
- 因此 4 页/split 的 partial 数量、额外 launch/reduce 及较小单 CTA 工作量开始压过并行化收益。该提交保留为上界证据；当前最佳仍为 8 页/split 的 #104278。

##### 原始评测归档

- [cuda_104279_raw.json](raw/cuda_104279_raw.json)

#### 提交 #104278 · 2026-08-07 05:51:07

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104278)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.21`**
- **当前最高真实 OJ 分数**：case 7/9 的 split 数提高至 generic policy 的 8 倍，保持每份 partial 恰为 8 个 page。

##### 结果分析

- case 7 `(B=64, L=2048, KV8)`：`n_split 2→16`，`64→8` 页/split，CTA 数约 `1024→8192`；时延 `0.848 ms`，相比 4x split #104275 的 `0.878 ms` 继续下降。
- case 9 `(B=32, L=4096, KV8)`：`n_split 4→32`，`64→8` 页/split，CTA 数约 `1024→8192`；时延 `0.857 ms`，相比 4x split #104275 的 `0.895 ms` 继续下降，评分 `26→27`。
- 这证实在 C500 上 case 7/9 尚未达到 split-reduce 的过度切分点；减少 CTA 内的 page-loop 长度和扩大调度并行度仍优于额外 partial/reduce 工作。当前保留所有已验证 MMA-QK、paired-QK 和 scalar fallback dispatch。
- 当前最佳源更新为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_split8x.cpp`。随后的 4 page/split（generic 的 16x split）测试 #104279 已回退，因此继续只用中间的 6 page/split 点定位最优区间，而不将该策略外推到长 KV8 case。

##### 原始评测归档

- [cuda_104278_raw.json](raw/cuda_104278_raw.json)

#### 提交 #104275 · 2026-08-07 05:42:16

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104275)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`38.07`**
- **当前最高真实 OJ 分数**：在 #104235 全部 kernel dispatch 不变的前提下，case 7/9 的 split 数提高至 generic policy 的 4 倍。

##### 结果分析

- case 7 `(B=64, L=2048, KV8)`：`n_split 2→8`，每 split 由 64 页变为 16 页，CTA 数约 `1024→4096`；`0.951 ms`，相比 #104273 的 2x 路径 `0.878 ms`，评分 `22→24`。
- case 9 `(B=32, L=4096, KV8)`：`n_split 4→16`，每 split 由 64 页变为 16 页，CTA 数约 `1024→4096`；`0.969 ms`，相比 #104273 的 2x 路径 `0.895 ms`，评分 `24→26`。
- 所有 14 个测试均正确。除 case 7/9 外没有代码或 dispatch 更改，其余计时保持在随机测量的窄幅波动中。这是明确的结构性吞吐提升而非单次偶然得分。
- 当前最佳源为 `solutions/archive/2026-08-07-experiments/cuda_maca_case7_case9_split4x.cpp`。下一项只继续测试同样两个 shape 的更高 split，观察 8 页/split 是否超过 CTA/reduce 开销的转折点。

##### 原始评测归档

- [cuda_104275_raw.json](raw/cuda_104275_raw.json)

#### 提交 #104273 · 2026-08-07 05:34:02

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104273)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.79`
- **性质**：对 #104271 当前 2x split 最佳路径的独立复测。

##### 结果分析

- case 7 `0.951 ms`、case 9 `0.969 ms`，分别接近 #104271 的 `0.962 ms`、`0.975 ms`，确认双倍 split 的收益稳定。
- #104273 不引入任何代码变更，只量化 OJ 的正常计时波动；它提供了 #104275 继续上推 split 前的可靠对照。

##### 原始评测归档

- [cuda_104273_raw.json](raw/cuda_104273_raw.json)

#### 提交 #104271 · 2026-08-07 05:19:18

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104271)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`37.71`**
- **当前最高真实 OJ 分数**：在 #104235 的 full dispatch 上，仅提高 case 7/9 的 split parallelism。

##### 结果分析

- 仅将 case 7 `(B=64, L=2048, KV8)` 的 `n_split 2→4`、case 9 `(B=32, L=4096, KV8)` 的 `n_split 4→8`；两者都从约 1024 CTA 扩至约 2048 CTA。paired-token QK、partial contract、reduce kernel及其余 12 case dispatch 未变。
- 真实时延出现结构性收益：case 7 `1.172→0.962 ms`（-17.9%，19→22 分）；case 9 `1.122→0.975 ms`（-13.1%，21→24 分）。14/14 都正确，总分 `37.71` 超过 #104235 的 `37.43`，成为当前最佳可提交源。
- 和 #104270 的 `n_split=1` 回归结合，这确认 case 7/9 的瓶颈仍主要是单 CTA page-scan 吞吐/调度，不是 split reduce；增加到约 2048 CTA 能隐藏更多延迟。继续只在这两个固定 shape 上测试更高 split count。

##### 原始评测归档

- [cuda_104271_raw.json](raw/cuda_104271_raw.json)

#### 提交 #104270 · 2026-08-07 05:10:18

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104270)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.14`

##### 结果分析

- 仅将 case 7 `(B=64, KV8, L=2048)` 的 `n_split` 从通用规则的 `2` 改为 `1`，使 paired-QK CTA 直写 output、跳过 partial buffers 和 reduce kernel；CTA 数从 `1024` 降为 `512`。
- case 7 `1.413 ms`，相比 #104235 的 `1.172 ms` 显著退化。高 batch 并未使 split/reduce 成为主瓶颈；两 split 提供的并行度更有价值。恢复通用 `n_split=2`。

##### 原始评测归档

- [cuda_104270_raw.json](raw/cuda_104270_raw.json)

#### 提交 #104267 · 2026-08-07 05:00:10

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104267)

- **提交语言/环境**：CUDA Maca C500 / 44.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.21`

##### 结果分析

- 仅将 case 13 的 split 数从 `128` 提高为 `192`：每个 KV head CTA 数 `128→192`，page/split `29→20`，总 CTA `1024→1536`。其余路径保持 #104235 dispatch。
- case 13 为 `0.735 ms`，优于 split=64 的 `0.825 ms`，但仍弱于 split=128 的 `0.701–0.708 ms`。结合 #104265，case 13 的 split=128 是可复现的局部最优区域，恢复该通用规则；无需继续细扫该 shape 的 split count。

##### 原始评测归档

- [cuda_104267_raw.json](raw/cuda_104267_raw.json)

#### 提交 #104265 · 2026-08-07 04:51:18

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104265)

- **提交语言/环境**：CUDA Maca C500 / 44.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.36`

##### 结果分析

- 仅将 case 13 `(B=1, KV8, L=58966)` 的 split 数由通用规则得出的 `128` 降为 `64`：每个 KV head 的 CTA 数 `128→64`，每 split page 数 `29→58`。其余 dispatch 与 #104235 一致。
- 所有 case 正确，但 case 13 从已重复验证的约 `0.701–0.708 ms` 退化为 `0.825 ms`（-17.7%）；说明 C500 上该 shape 更需要约 1024 总 CTA 的并行度，不能为了减少 partial/reduce 而把 split 数降到 64。恢复通用 `n_split=128`。

##### 原始评测归档

- [cuda_104265_raw.json](raw/cuda_104265_raw.json)

#### 提交 #104263 · 2026-08-07 04:42:01

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104263)

- **提交语言/环境**：CUDA Maca C500 / 52.3 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（12/14）/ `33.21`

##### 结果分析

- 将 KV8 case 7/9 的 paired-token QK 从两个 16-lane subgroup 改为四个 8-lane subgroup：每 lane 累加 16 dims，同时计算四个 token，以两级 `width=8` shuffle reduction 合并。case 12/13 和所有非目标分支保持 #104235 dispatch。
- case 7 `36.271163 s`、case 9 `36.386262 s` 均超时式 WA；其余12个 case全 Accepted。该平台的这个 8-lane shuffle subgroup / generated code 组合不可用，不能再将 paired-QK 缩至 8 lanes。保留已证实正确、且有真实收益的 16-lane paired QK。

##### 原始评测归档

- [cuda_104263_raw.json](raw/cuda_104263_raw.json)

#### 提交 #104262 · 2026-08-07 04:39:33

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104262)

- **提交语言/环境**：CUDA Maca C500 / 44.3 K（`cuda.maca-c500`）
- **总状态/总分**：CompilationError

##### 结果分析

- 生成脚本在替换 paired-QK kernel 时删除了 fallback definition，但 dispatch 保留了对它的调用，OJ device compiler 报 `paged_decode_split_qk_pair_kernel` 未声明。
- 该纯生成错误已在 #104263 修复；#104263 的 runtime WA 是独立、有效的 8-lane subgroup 结论。

##### 原始评测归档

- [cuda_104262_raw.json](raw/cuda_104262_raw.json)

#### 提交 #104259 · 2026-08-07 04:26:29

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104259)

- **提交语言/环境**：CUDA Maca C500 / 59.6 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（13/14）/ `35.43`

##### 结果分析

- 针对 #104255 的 V source-span 假设，将 native kernel 的 V staging 从一个 D128 tile 扩到四份完整复制（`8192` BF16），完全覆盖 official LDS source view 所及的最大 offset 后重新强制 launch case 13。
- case 13 仍在 `36.182457 s` 后超时式 WA，其余 13 case Accepted。这排除了“仅由 V LDS address 越界造成 timeout”的解释；目前设计还将四个 GQA rows 串行地执行全 four-wave score/PV pipeline，远偏离 official 以一个 `Q[16,128]` / 一个 `P[16,16]` tile 同时处理 M rows 的模式。该串行 D128 port 已停止，不再仅靠 V replication 继续试错。
- #104235 的 paired-token QK 仍是 case 13 的可信路径。后续若重启 CUTE P×V，必须一次性处理 GQA rows，并从 `TiledMmaO` 的 D128 fragment partition（而不是手工套用 D512 `tOrVt` register shape）推导 V copy / LDS layout。

##### 原始评测归档

- [cuda_104259_raw.json](raw/cuda_104259_raw.json)

#### 提交 #104255 · 2026-08-07 04:17:02

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104255)

- **提交语言/环境**：CUDA Maca C500 / 59.1 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（13/14）/ `34.29`

##### 结果分析

- 删除 host-side CUTE availability guard 后，case 13 确实启动了 native four-wave P×V kernel，并在 `35.879298 s` 后超时式 WA；其余 13 case 都保持 Accepted。这证明 #104253 的 `0.707 ms` 是 host guard 跳过 dispatch 后的 paired-QK fallback，不能作为 native runtime 数据。
- 当前 D128 port 直接复用了 official V LDS addressing（每 physical wave 的 base 增加 `16*64 = 1024` BF16）。初步判断是 official analogous kernel 的 value width为 512、而 D128 staging太窄；#104259 已用四份 D128 V tile 完整覆盖这个 LDS source span，仍然 timeout，因此该差异只是未完成 port 的一个风险，而不是已证明的根因。
- 保留 #104235 作为最高分 source。当前串行 GQA-row native PV design 已被 #104255/#104259 否定；后续 runtime experiment必须基于 D128-specific `TiledMmaO` fragment partition 同时处理 GQA rows，不能继续直接套用 D512 `tOrVt` register shape或仅修改 V storage 容量。

##### 原始评测归档

- [cuda_104255_raw.json](raw/cuda_104255_raw.json)

#### 提交 #104253 · 2026-08-07 04:07:20

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104253)

- **提交语言/环境**：CUDA Maca C500 / 59.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.14`

##### 结果分析

- 首个严格只针对 case 13 的 guarded runtime checkpoint：每个 CTA 仍对应 `(b, kv_head, split)`，paged K/V 按 group 一次 staging，按四个 GQA row 串行形成 score/P，并以 `MACA_16x16x16_F32BF16BF16F32` 和 `TiledMMA<..., Layout<_1,_4,_1>>` 编写 native four-wave P×V；V 采用 #104250 已编译的 `lds4x4_with_swizzle424 → permute_4x4_b16` register contract。
- 14/14 Accepted，case 13 为 `0.707 ms`。但 #104255 的 forced dispatch 随后证实 host CUTE availability guard 为 false，因此此提交实际执行的是 paired-token QK fallback；它只验证完整源的回退安全性，**不构成 native runtime 的正确性或性能证据**。

##### 原始评测归档

- [cuda_104253_raw.json](raw/cuda_104253_raw.json)

#### 提交 #104250 · 2026-08-07 03:41:42

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104250)

- **提交语言/环境**：CUDA Maca C500 / 48.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.14`

##### 结果分析

- 未 launch 的 native PV epilogue probe 已用 OJ 编译器完成官方 C500 operand pipeline：score accumulator 的 layout-preserving FP32→`mctlass::bfloat16_t` conversion、shared V 的 `lds4x4_with_swizzle424`、`permute_4x4_b16`，再进入 `TiledMMA<MACA_16x16x16..., Layout<_1,_4,_1>>` GEMM。
- 这是此前缺失的关键 CUTE 编译边界；它与 #104247 的 official atom probe 共同证明 full official PV port 所需的 native API 均可解析。由于 kernel 未 launch，`36.14` 仅为 baseline dispatch 的一次计时，不应视作性能结果。

##### 原始评测归档

- [cuda_104250_raw.json](raw/cuda_104250_raw.json)

#### 提交 #104247 · 2026-08-07 03:29:19

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104247)

- **提交语言/环境**：CUDA Maca C500 / 45.3 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.36`

##### 结果分析

- 未 launch 的 probe 以官方 MetaX 类型完成 K=128 CUTE score operation：`mctlass::bfloat16_t`、`MMA_Atom<MACA_16x16x16_F32BF16BF16F32>`、`TiledMMA<..., Layout<Shape<_1,_1,_1>>>`，及 accumulator 到 shared score 的 materialization。
- C500 OJ 实际编译和完整回归均通过，排除了先前 convenience `wmma::MMA_16x16x16...` atom 与 official native atom 不同导致后续无法移植的风险。
- 生产 dispatch 未改变，故 `37.36` 与 #104235 的 `37.43` 均是扩展 KV8 paired-QK + 精确 KV4 MMA-QK 路径的有利计时样本；当前最高记录仍为 #104235。

##### 原始评测归档

- [cuda_104247_raw.json](raw/cuda_104247_raw.json)

#### 提交 #104246 · 2026-08-07 03:17:49

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104246)

- **提交语言/环境**：CUDA Maca C500 / 43.2 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `37.14`

##### 结果分析

- 将已证实正确的 64-thread raw WMMA QK 置换为 CUTE K=128 `partition_A/B/C → gemm → copy-to-shared`，而 scalar FP32 PV、split partial contract、精确 KV4 dispatch 和所有 KV8 paired-token dispatch 均保持不变。
- 14/14 Accepted 证明这条一-wave CUTE score materialization 在实际 decode 数据上数值正确，不只是 unlaunched compile probe；其 score `37.14` 稍低于 #104235，且目标 KV4 时延没有结构性更优，因此不替代当前最佳 source。
- 此结果与 #104240 合并给出明确边界：single 64-lane CUTE score API 可用；将四个 wave 以普通 tensor/scalar PV 直接拼作一个 CTA 不可用。下一阶段必须直接 port official swizzled PV epilogue，而不是再重排 raw wave。

##### 原始评测归档

- [cuda_104246_raw.json](raw/cuda_104246_raw.json)

#### 提交 #104240 · 2026-08-07 03:04:54

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104240)

- **提交语言/环境**：CUDA Maca C500 / 50.2 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（10/14）/ `31.14`

##### 结果分析

- 这是首个实际 launch 的 256-thread four-wave CUTE QK candidate：四个 64-lane wave 以 `tid & 63` 重复 materialize score，随后每 wave 处理一个 KV8 GQA row 的标量 FP32 PV。
- 编译通过，但所有被启用的 KV8 long case 均在约 36 s 后超时式 WA：case 7 `36.128 s`、case 9 `36.149 s`、case 12 `36.229 s`、case 13 `36.123 s`；未走该 dispatch 的全部十个 case 正常 Accepted。
- 这严格否定“CUTE QK four-wave + 普通 row-major shared tensors + scalar PV”的简化设计。C500 four-wave 路径必须按官方 `MACA_16x16x16` atom、swizzled Q/K/V layout、`lds4x4_with_swizzle424`、`permute_4x4_b16` 和 tiled P×V epilogue 完整实现；不再对这个 raw simplification 做变形尝试。

##### 原始评测归档

- [cuda_104240_raw.json](raw/cuda_104240_raw.json)

#### 提交 #104239 · 2026-08-07 03:00:25

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104239)

- **提交语言/环境**：CUDA Maca C500 / 50.2 K（`cuda.maca-c500`）
- **总状态**：CompilationError

##### 结果分析

- 初次在 `run_kernel` 中接入 256-thread CUTE candidate 时，paired-QK fallback 的 launch 使用了仅在另一个分支定义的 `gqa_ratio`。
- OJ host pass 明确报 `use of undeclared identifier 'gqa_ratio'`。这是 dispatch scope 错误而非 CUTE device API/layout 失败；下一次 #104240 修复为 local `gqa_ratio` 后通过编译并得到实际 runtime 结论。

##### 原始评测归档

- [cuda_104239_raw.json](raw/cuda_104239_raw.json)

#### 提交 #104235 · 2026-08-07 02:47:02

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104235)

- **提交语言/环境**：CUDA Maca C500 / 43.8 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`37.43`**
- **当前最高真实 OJ 分数**：该源保留扩展后的 KV8 paired-QK、精确 KV4 MMA-QK，并仅新增未 launch 的 CUTE K=128 score materialization probe。

##### 结果分析

- 新 probe 将 #104225 的 CUTE surface 从单一 K=16 tile 推至 `[16,128] × [128,16]`：64-lane slice、FP32 C fragment 到 shared score 的 `copy(tCrC, tCsC)` 均被 C500 OJ 实际编译；四物理 wave 用 `tid & 63` 复用 native score slice 也被前端接受。
- 生产 dispatch 与 `cuda_maca_combo_kv8long.cpp` 相同：KV4 case 8/11/14 走已验证 64-lane MMA-QK，KV8 case 7/9/12/13 走 paired-token scalar QK；CUTE probe 没有 launch。因此分数相对 #104227 的提升应被视为同一有效 candidate 的有利 OJ 计时样本，而非 probe 自身带来的性能。
- 逐 case 同时保持所有长路径收益：case 7 `1.172 ms`、case 8 `0.430 ms`、case 9 `1.122 ms`、case 11 `1.185 ms`、case 12 `1.994 ms`、case 13 `0.701 ms`、case 14 `0.522 ms`。该文件目前是应保留的最高分可提交候选。

##### 原始评测归档

- [cuda_104235_raw.json](raw/cuda_104235_raw.json)

#### 提交 #104232 · 2026-08-07 02:35:01

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104232)

- **提交语言/环境**：CUDA Maca C500 / 41.8 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.29`

##### 结果分析

- #104227 的独立重复评测确认扩展 paired-token QK 的 target trend：case 12 `2.002 ms`、case 13 `0.707 ms`，均远低于未扩展时的 #104221（`2.461 ms`、`0.757 ms`）。
- 本轮 aggregate score 仍受非目标 baseline 计时摇摆影响，故以 #104235 的同 dispatch 37.43 作为当前可复交最佳成绩，并保留多次 target 数据而非只按一轮 aggregate 选择算法。

##### 原始评测归档

- [cuda_104232_raw.json](raw/cuda_104232_raw.json)

#### 提交 #104227 · 2026-08-07 02:18:56

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104227)

- **提交时间**：2026-08-07 02:18:56
- **提交语言/环境**：CUDA Maca C500 / 41.8 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.29`

##### 结果分析

- 在 #104221 的精确组合上，将 paired-token scalar QK 扩展到另两个 KV8 长序列：case 12 `(batch=8, L=32768)`、case 13 `(batch=1, L=58966)`；case 7/9 与 KV4 MMA-QK case 8/11/14 保持原有分支。
- 新增目标出现显著且同向的真实收益：case 12 `2.461→2.010 ms`（-18.3%，18→22 分），case 13 `0.757→0.701 ms`（-7.4%，24→25 分）。case 7/9 也仍优于 #104091（`1.184 ms`、`1.126 ms`）。因此 paired-token QK 应覆盖所有四个 KV8 long shapes。
- 单次总分仅 `36.29`，低于 #104221 的 `37.07`，但同时 edge 和非目标 scalar case 出现明显微秒级波动（case 2 `0.010→0.012 ms`、case 3 `0.020→0.024 ms`、case 6 `0.118→0.128 ms`），且已验证的新增路径没有任何 target 回退。保留该完整 dispatch，后续以重新评测确认综合分数，而不是误删确有大幅收益的 case 12/13 分支。

##### 原始评测归档

- [cuda_104227_raw.json](raw/cuda_104227_raw.json)

#### 提交 #104225 · 2026-08-07 02:16:00

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104225)

- **提交时间**：2026-08-07（该实验的 OJ 返回未保留精确秒）
- **提交语言/环境**：CUDA Maca C500 / 26.2 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.29`

##### 结果分析

- isolated device-only CUTE probe 成功走通官方所需的共享张量与计算路径：`MMA_Atom<wmma::MMA_16x16x16_F32BF16BF16F32>`、four-atom `AtomLayout`、`make_smem_ptr/make_tensor`、`partition_A/B/C`、`make_fragment_C/clear` 和显式 `cute::gemm(...)`。
- `run_kernel` 没有 launch probe，生产行为保持 #104091，因此这个结果只确认 C500 OJ 编译器可接受 CUTE tensor partition 和 MMA GEMM 表面；不把其 36.29 score 当作新算法性能数据。
- 编译为 0 errors；仅出现 CUTE 内部潜在未初始化 accumulator 警告和 MACA 对 `__launch_bounds__` 的已知提示。该 checkpoint 解除 faithful four-wave CUTE port 的最基础 API 风险。

##### 原始评测归档

- [cuda_104225_raw.json](raw/cuda_104225_raw.json)

#### 提交 #104221 · 2026-08-07 02:07:51

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104221)

- **提交时间**：2026-08-07 02:07:51
- **提交语言/环境**：CUDA Maca C500 / 41.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`37.07`**
- **最佳记录**：超过 #104091 的 `36.21`，成为当前最高真实 OJ 分数。

##### 结果分析

- 合并两条独立验证过的精确 dispatch：KV4 case 8/11/14 使用 64-lane MMA-QK + FP32 scalar-PV；KV8 case 7/9 使用 paired-token 16-lane-subgroup QK；其它所有 shape 保持 #104091 标量路径。
- 四个重点 case 同时获益：case 7 `1.207→1.179 ms`（-2.3%，18→19 分）、case 8 `0.479→0.428 ms`（-10.6%，18→20 分）、case 9 `1.230→1.120 ms`（-8.9%，20→22 分）、case 11 `1.344→1.154 ms`（-14.1%，15→17 分），case 14 `0.724→0.523 ms`（-27.8%，19→24 分）。
- 这次总分提升 `+0.86` 并非只来自单 case 波动：各优化分支互不重叠，且分别在 #104175/#104217 中通过过完整 OJ 正确性与目标 case 时延验证；组合后也 14/14 Accepted。此源码是当前可用候选。
- 仍有明显差距：case 7/9/12/13 的 KV8 decode 与 case 11 的长 KV4 仍远慢于参考实现。下一个低风险推进是把已正确的 paired-token QK 单独扩展至尚未覆盖的 KV8 long cases 12/13，严格依据下一次真实 OJ 结果决定保留。

##### 原始评测归档

- [cuda_104221_raw.json](raw/cuda_104221_raw.json)

#### 提交 #104217 · 2026-08-07 01:56:19

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104217)

- **提交时间**：2026-08-07 01:56:19
- **提交语言/环境**：CUDA Maca C500 / 31.6 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `35.21`

##### 结果分析

- 仅在 KV8 case 7/9 启用 paired-token 标量 QK：每个 32-lane warp 切成两个 16-lane subgroup，同时算相邻两个 token 的 128-D dot product；每 lane 从 4 维改为 8 维、shuffle reduction 从 5 级缩为 4 级，随后把 16 个 logits 广播给未改动的 FP32 PV。
- 目标 case 都出现真实收益：case 7 `1.207→1.183 ms`（-2.0%），case 9 `1.230→1.124 ms`（-8.6%，20→21 分）。这说明 KV8 主路径的主要余量确实存在于标量 QK 的 16-token 串行 reduction，而非 shared-memory 大小。
- 总分仍为 `35.21`，源于本轮非目标 baseline 计时波动，不能单独替代 #104091；但两个低分 case 的同向改善足以将此分支与 #104175 的精确 MMA-QK case 8/11/14 组合后重新评估。

##### 原始评测归档

- [cuda_104217_raw.json](raw/cuda_104217_raw.json)

#### 提交 #104210 · 2026-08-07 01:40:44

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104210)

- **提交时间**：2026-08-07 01:40:44
- **提交语言/环境**：CUDA Maca C500 / 25.2 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.21`

##### 结果分析

- 生产 dispatch 完全保留 #104091；新增但未 launch 的 device-only probe 成功构造 `cute::MMA_Atom<wmma::MMA_16x16x16_F32BF16BF16F32>`、`Layout<Shape<_1,_4,_1>>` 和 `make_tiled_mma(...).get_thread_slice(...)`。
- 该 checkpoint 证明 OJ C500 安装的 MCTlass/CUTE 提供了官方 16×16 four-wave kernel 所需的基础 tiled-MMA 类型表面，同时没有影响基线性能。
- 它**不**证明 tensor partition、LDS/permute、CUTE `gemm_rr` 或 paged D128 V epilogue 已经兼容；下一阶段将以官方 D128/FlashMLA source 为蓝图，逐步建立可编译的 four-wave PV 路径，而不是再次扩展 raw 128-thread WMMA。

##### 原始评测归档

- [cuda_104210_raw.json](raw/cuda_104210_raw.json)

#### 提交 #104202 · 2026-08-07 01:28:41

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104202)

- **提交时间**：2026-08-07 01:28:41
- **提交语言/环境**：CUDA Maca C500 / 31.2 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（12/14）/ `33.50`

##### 结果分析

- 该候选只在 case 7/9 将每个 `uint32` 中两个 BF16 的标量拆包替换为 `__nv_bfloat162_raw → __bfloat1622float2`；Q、K/V layout、算术顺序和其它 shape 均维持 #104091。
- OJ 在两个启用 shape 上均出现约 `35.9–36.5 s` 的超时式 WrongAnswer，其它 case 正确。这表明 MACA C500 后端对该 native packed-BF16 conversion 形式存在不适合生产 kernel 的代码生成/执行问题；本机 NVCC 能编译不是 MACA 可用性的证据。
- 结论：停止 BF16x2 intrinsic 路线，继续使用 #104091 已验证的显式 `uint16→__nv_bfloat16→float` 标量拆包。该失败也强化了后续仅通过小范围 OJ checkpoint 验证 MACA 特有 intrinsic 的原则。

##### 原始评测归档

- [cuda_104202_raw.json](raw/cuda_104202_raw.json)

#### 提交 #104197 · 2026-08-07 01:12:10

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104197)

- **提交时间**：2026-08-07 01:12:10
- **提交语言/环境**：CUDA Maca C500 / 31.7 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `36.14`

##### 结果分析

- 此版本保留 #104091 作为所有非目标 shape 的逐字回退，仅将低分 KV8 case 7/9 改为 4 KB shared page buffer：先加载 K、完成 QK，再经两次 barrier 覆盖为 V 进行 PV。
- 数值正确，但目标性能均退化：case 7 `1.207→1.235 ms`（+2.3%），case 9 `1.230→1.280 ms`（+4.1%）。更多驻留空间未补偿 K/V 分时加载、额外两次同步和失去并行 global load 的代价。
- 总分 `36.14` 也低于 #104091 的 `36.21`。因此 4 KB K→V reuse 被正式排除；KV8 主路径必须保留 8 KB 同时 K/V staging，不能再以减 shared memory 为目标微调。

##### 原始评测归档

- [cuda_104197_raw.json](raw/cuda_104197_raw.json)

#### 提交 #104188 · 2026-08-07 00:55:45

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104188)

- **提交时间**：2026-08-07 00:55:45
- **提交语言/环境**：CUDA Maca C500 / 32.9 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（10/14）/ `30.29`

##### 结果分析

- 这是 #104181 的受控修复验证：两个 64-lane group 都执行完整、相同的 8-stage QK WMMA；仅 wave 0 materialize `s_score`，两个 wave 仍各自负责不重叠的 scalar-PV 输出维度。
- 结果与 #104181 相同：long-KV4 case 8、10、11、14 全部在约 `35.8–36.3 s` 后 WrongAnswer，证明失败并非由 wave 1 未参与 QK collective 引起。
- 因此明确排除当前 raw WMMA API 下的 `blockDim=128` 双 wave 设计。官方多-wave kernel 依赖 CuTe/MCTlass 的特定 tiled-MMA、LDS/permutation 和线程布局，不能仅把已验证的 64-thread raw WMMA kernel 扩大为 128 threads。该系列停止，保留严格 `blockDim=64` 的 QK 路径作为唯一已验证 WMMA 方案。

##### 原始评测归档

- [cuda_104188_raw.json](raw/cuda_104188_raw.json)

#### 提交 #104181 · 2026-08-07 00:36:21

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104181)

- **提交时间**：2026-08-07 00:36:21
- **提交语言/环境**：CUDA Maca C500 / 32.8 K（`cuda.maca-c500`）
- **总状态/总分**：WrongAnswer（10/14）/ `30.36`

##### 结果分析

- 此版本以 128 threads（两个 C500 64-lane group）分配 scalar-PV 输出：wave 0 负责 dim `0..63`，wave 1 负责 dim `64..127`；为避免重复工作，只有 wave 0 运行 QK WMMA，随后两个 wave 读取其 materialize 的 score。
- OJ 明确否定了该做法：长 KV4 case 8、10、11、14 均以约 `35.9–36.2 s` 的异常耗时后 WrongAnswer，短路径和未走 MMA 的 KV8 case 均正确。该模式不是常规数值误差，而是 C500 的 WMMA collective / wave scheduling 不支持让另一个 wave 闲置并等待其 collective 结果的实现方式。
- 后续若继续测试多 wave，必须令每个 64-lane group 执行完整相同的 QK WMMA collective（官方 4-wave 内核也显式重复 score MMA），并只在 PV/output 维度写入阶段分工；绝不复用“单 wave QK、另一 wave 等待”的变体。

##### 原始评测归档

- [cuda_104181_raw.json](raw/cuda_104181_raw.json)

#### 提交 #104175 · 2026-08-07 00:30:34

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104175)

- **提交时间**：2026-08-07 00:30:34
- **提交语言/环境**：CUDA Maca C500 / 32.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `35.79`

##### 结果分析

- MMA-QK 仅精确派发给已多次实测获益的 KV4 case：`(batch,seqlen_k)=(16,4096)、(16,12251)、(1,61519)`，即 case 8、11、14；case 10 与所有其它 shape 均走 #104091 标量回退。
- 三个目标 case 均维持收益：相较 #104091，case 8 `0.479→0.436 ms`（-9.0%）、case 11 `1.344→1.158 ms`（-13.8%）、case 14 `0.724→0.527 ms`（-27.2%）。这再次确认 MMA-QK 对这些 long-KV4 shape 有效。
- 但总分 `35.79` 仍低于 #104091 的 `36.21`。非目标标量 shape 的本轮时延仍有可见波动（例如 case 6 `0.118→0.128 ms`），因此该提交不是可替代最佳分数的版本；其价值是确定可保留的精确 case dispatch 和可重复的主路径收益。

##### 原始评测归档

- [cuda_104175_raw.json](raw/cuda_104175_raw.json)

#### 提交 #104164 · 2026-08-07 00:19:55

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104164)

- **提交时间**：2026-08-07 00:19:55
- **提交语言/环境**：CUDA Maca C500 / 33.4 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `35.21`

##### 结果分析

- 此提交只把选择性 MMA-QK 的 K/V page staging 改为全局对齐 `uint4` load，随后在 shared memory 中保留明确的 K 转置 / V token-major 写法；CPU staging test 与 OJ 正确性均通过。
- 实测为负优化：相较 #104147，case 8 `0.426→0.471 ms`、case 11 `1.166→1.366 ms`、case 14 `0.522→0.654 ms`。载入指令虽减少，但每 16-B 向量需拆成 8 次非连续 shared 转置写，破坏了单-wave loader 的实际调度。
- 结论：保持每 BF16 标量的 K 转置 loader；不再在这个 direct shared-transpose 写法上重试 `uint4`。若要 vectorize，必须改为官方 copy atom / LDS transpose 类共享布局，而非手工标量散写。

##### 原始评测归档

- [cuda_104164_raw.json](raw/cuda_104164_raw.json)

#### 提交 #104153 · 2026-08-07 00:06:44

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104153)

- **提交时间**：2026-08-07 00:06:44
- **提交语言/环境**：CUDA Maca C500 / 34.0 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `35.43`

##### 结果分析

- 此提交在选择性长 KV4 MMA-QK 路径中，将 FP32 page probability 量化为 BF16，并以 8 个 raw `P[16,16]×V[16,16]` WMMA tile 替换 scalar PV；split-LSE 的 `m/l` 保持 FP32。
- 14 个 case 全部正确，和离线 BF16 rounding 模型一致，证明概率量化处于 OJ 精度容差内。
- 性能结论明确为**负优化**：case 8 `0.426→0.574 ms`、case 10 `0.143→0.191 ms`、case 11 `1.166→1.673 ms`、case 14 `0.522→0.739 ms`。8 次小 16×16 PV MMA、重复 fragment materialization 和增加的同步无法抵消原 scalar-PV 的轻量成本。
- 后续禁止重试 raw 小 tile PV MMA；保留 `cuda_maca_mma_qk.cpp` 的 MMA-QK + FP32 scalar-PV 路径，并转向减少 QK/loader 开销或借鉴官方多-wave shared/register 编排。已在后续工作中重新读取 `cuda_104153_raw.json` 并通过 `--watch 104153` 核验：归档与 OJ 状态一致，结论不变。

##### 原始评测归档

- [cuda_104153_raw.json](raw/cuda_104153_raw.json)

### 2026-08-06

#### 提交 #104147 · 2026-08-06 23:57:45

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104147)

- **提交时间**：2026-08-06 23:57:45
- **提交语言/环境**：CUDA Maca C500 / 32.5 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `35.57`

##### 结果分析

- 仅在 `num_heads_k==4 && seqlen_k>=4096` 启动 64-lane MMA-QK；KV8、edge 和短 KV4 全部回退 #104091 scalar kernel。
- 目标 case 的结构性收益复现：case 8 `0.479→0.426 ms`（18→20 分）、case 11 `1.344→1.166 ms`（15→17 分）、case 14 `0.724→0.522 ms`（19→24 分）。这些提升与 #104142 的方向一致，说明不是单次噪声。
- 总分仍为 35.57，略低于 #104091 的 36.21，是因为非目标 scalar case 在本轮有 OJ 波动（例如 case 2 `0.010→0.013 ms`、case 4 `0.064→0.069 ms`、case 6 `0.118→0.128 ms`），并非选择性分支改变了其 kernel body。该 dispatch 应在后续候选中保留，结论须继续以多次数据判定。

##### 原始评测归档

- [cuda_104147_raw.json](raw/cuda_104147_raw.json)

#### 提交 #104142 · 2026-08-06 23:43:37

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104142)

- **提交时间**：2026-08-06 23:43:37
- **提交语言/环境**：CUDA Maca C500 / 31.9 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ `31.64`

##### 结果分析

- 此提交首次真实启动一整个 64-lane C500 WMMA group：将 GQA group 的 Q 打包为 `[8,16,16]`、K 显式转置为 `[8,16,16]`，执行 8 个 BF16-input/FP32-accumulate `m16n16k16` QK tile；fragment 统一 materialize 到 row-major shared memory 后再做 FP32 LSE 和 scalar PV。
- **正确性完整通过**，因此验证了 host/device guard、WMMA 行主序输入方向、64-lane collective 调用、fragment store mapping、GQA padding row、tail mask 和 split partial layout；这是后续 PV MMA 的可信语义基线。
- 全量派发不是正确的最终策略：KV4 长序列有明显收益（case 8 `0.479→0.431 ms`、case 10 `0.142→0.136 ms`、case 11 `1.344→1.160 ms`、case 14 `0.724→0.521 ms`），但 KV8 和短 KV4 退化（case 7 `1.207→1.496 ms`、case 9 `1.230→1.415 ms`、case 12 `2.439→2.660 ms`），总分降至 31.64。
- 结论：保留 scalar kernel 为 KV8 和短 KV4 回退；后继候选只对 `num_heads_k==4 && seqlen_k>=4096` 启用已获利的 MMA-QK 路径，并将主攻点转为 PV MMA。

##### 原始评测归档

- [cuda_104142_raw.json](raw/cuda_104142_raw.json)

#### 提交 #104101 · 2026-08-06 22:11:22

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104101)

- **提交时间**：2026-08-06 22:11:22
- **提交语言/环境**：CUDA Maca C500 / 23.1 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted / `35.29`

##### 结果分析

- 本次只将主 kernel 中 `partial_m[head_idx]` 与 `partial_l[head_idx]` 限制为每个 query-head warp 的 lane 0 写入；数学与 partial_acc 写入均保持不变。
- 14 个测试点全部正确，但总分比 #104091 的 36.21 低 **0.92**；低分长序列没有一致收益：case 7 `1.207→1.224 ms`、case 11 `1.344→1.361 ms`、case 14 `0.724→0.729 ms` 均退化，其他变化也落在 OJ 波动范围。
- 结论：MACA 上同地址的 warp store 很可能已被合并，或 lane 分歧/代码生成抵消了收益。此方向已被 OJ 证伪，源码已回退到 #104091 的全 warp 写入版本。

##### 原始评测归档

- [cuda_104101_raw.json](raw/cuda_104101_raw.json)

#### 提交 #104091 · 2026-08-06 21:53:05

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104091)

- **提交时间**：2026-08-06 21:53:05
- **提交语言/环境**：CUDA Maca C500 / 22.9 K（`cuda.maca-c500`）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：Accepted（14/14）
- **总分**：**`36.21`**，较 #104025 的 34.79 提升 **+1.42**。
- **OJ 内存**：`23059680 K`（约 22.0 G）

##### 结果分析

- 本提交只替换了 `n_split > 1` 的 split-KV 合并：一个 128-thread CTA 处理一个 `(batch, query_head)`，将各 split 的 max、指数权重和归一化分母协作计算一次；主 decode kernel、`uint4` K/V page load、8 KB 单缓冲和 split 调度均未改动。
- 合并开销大的 case 获得稳定收益：case 8 `0.488→0.479 ms`（-1.8%）、case 11 `1.350→1.344 ms`（-0.4%）、case 12 `2.452→2.439 ms`（-0.5%）、case 14 `0.747→0.724 ms`（-3.1%）。case 13 `0.772→0.756 ms`（-2.1%）也改善。
- 总分的大幅提升也包含 OJ 运行波动：case 4 `0.069→0.064 ms`、case 5 `0.079→0.071 ms`、case 6 `0.127→0.118 ms`、case 10 `0.153→0.142 ms` 的改善不能全部归因于 reduce（这些 shape 的 `n_split` 很低或为 1）。后续实验应只以多次/逐 case 的一致趋势判断收益。
- case 7/9 基本持平（`1.208→1.207 ms`、`1.239→1.230 ms`），说明它们的主瓶颈仍在 decode 的 QK/PV 数据路径，而不是 split 合并。

##### 测试点汇总

| 测试点 | 状态 | 配置 | 基准 (ms) | User kernel (ms) | 加速比 | 得分 | 检查结果 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Accepted | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge` | 0.038 | 0.009 | 4.222x | 80/100 | OK |
| 2 | Accepted | `batch=4, seqlen_k_cap=2, kv_heads=8, kind=edge` | 0.038 | 0.010 | 3.800x | 79/100 | OK |
| 3 | Accepted | `batch=16, seqlen_k_cap=17, kv_heads=4, kind=edge` | 0.046 | 0.020 | 2.300x | 69/100 | OK |
| 4 | Accepted | `batch=64, seqlen_k_cap=64, kv_heads=8, kind=perf` | 0.060 | 0.064 | 0.938x | 48/100 | OK |
| 5 | Accepted | `batch=16, seqlen_k_cap=141, kv_heads=4, kind=perf` | 0.046 | 0.071 | 0.648x | 39/100 | OK |
| 6 | Accepted | `batch=16, seqlen_k_cap=362, kv_heads=8, kind=perf` | 0.049 | 0.118 | 0.415x | 29/100 | OK |
| 7 | Accepted | `batch=64, seqlen_k_cap=2048, kv_heads=8, kind=perf` | 0.281 | 1.207 | 0.233x | 18/100 | OK |
| 8 | Accepted | `batch=16, seqlen_k_cap=4096, kv_heads=4, kind=perf` | 0.111 | 0.479 | 0.232x | 18/100 | OK |
| 9 | Accepted | `batch=32, seqlen_k_cap=4096, kv_heads=8, kind=perf` | 0.317 | 1.230 | 0.258x | 20/100 | OK |
| 10 | Accepted | `batch=1, seqlen_k_cap=8192, kv_heads=4, kind=perf` | 0.064 | 0.142 | 0.451x | 31/100 | OK |
| 11 | Accepted | `batch=16, seqlen_k_cap=12251, kv_heads=4, kind=perf` | 0.249 | 1.344 | 0.185x | 15/100 | OK |
| 12 | Accepted | `batch=8, seqlen_k_cap=32768, kv_heads=8, kind=perf` | 0.572 | 2.439 | 0.235x | 18/100 | OK |
| 13 | Accepted | `batch=1, seqlen_k_cap=58966, kv_heads=8, kind=perf` | 0.241 | 0.756 | 0.319x | 24/100 | OK |
| 14 | Accepted | `batch=1, seqlen_k_cap=61519, kv_heads=4, kind=perf` | 0.172 | 0.724 | 0.238x | 19/100 | OK |

##### 原始评测归档

- [cuda_104091_raw.json](raw/cuda_104091_raw.json)

#### 提交 #104025 · 2026-08-06 20:44:46

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/104025)

- **提交时间**：2026-08-06 20:44:46
- **提交语言/环境**：CUDA Maca C500 / 20.8 K（`cuda.maca-c500`）
- **总状态/总分**：Accepted / `34.79`
- **结果结论**：将 K/V 整页搬运从 `uint32` 扩为对齐的 `uint4` 后，14 个 case 都较 #103932 更快；此版本为 #104091 的直接基线。

##### 原始评测归档

- [cuda_104025_raw.json](raw/cuda_104025_raw.json)

#### 提交 #103932 · 2026-08-06 18:49:00

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/103932)

- **提交时间**：2026-08-06 18:49:00
- **提交语言/环境**：CUDA Maca C500 / 19.4 K（cuda.maca-c500）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：Accepted
- **总分**：`31.57`
- **OJ 内存**：`22.0 G`（页面精确值：`23059816 K / 41943040 K`）
- **测试点**：14 个

##### 结果分析

- 14 个测试点全部 Pass，总分 31.57（当前最佳，较 v2 提升 +0.43）。
- 本版为 v4（回退双缓冲）：单缓冲 8KB smem 恢复高占用率（每 SM 6 block），保留标量写修复与 split 1024。
- 相对 v2（#103870）逐 case 对比见下方表格；双缓冲回退后 case 7/9/12/13 的退化应已恢复。

##### 测试点汇总

| 测试点 | 状态 | 配置 | 基准 (ms) | User kernel (ms) | 加速比 | 得分 | 检查结果 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Accepted | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge` | 0.038 | 0.015 | 2.533x | 71/100 | OK |
| 2 | Accepted | `batch=4, seqlen_k_cap=2, kv_heads=8, kind=edge` | 0.038 | 0.019 | 2.000x | 66/100 | OK |
| 3 | Accepted | `batch=16, seqlen_k_cap=17, kv_heads=4, kind=edge` | 0.046 | 0.032 | 1.438x | 58/100 | OK |
| 4 | Accepted | `batch=64, seqlen_k_cap=64, kv_heads=8, kind=perf` | 0.06 | 0.088 | 0.682x | 40/100 | OK |
| 5 | Accepted | `batch=16, seqlen_k_cap=141, kv_heads=4, kind=perf` | 0.046 | 0.085 | 0.541x | 35/100 | OK |
| 6 | Accepted | `batch=16, seqlen_k_cap=362, kv_heads=8, kind=perf` | 0.049 | 0.147 | 0.333x | 25/100 | OK |
| 7 | Accepted | `batch=64, seqlen_k_cap=2048, kv_heads=8, kind=perf` | 0.281 | 1.347 | 0.209x | 17/100 | OK |
| 8 | Accepted | `batch=16, seqlen_k_cap=4096, kv_heads=4, kind=perf` | 0.111 | 0.516 | 0.215x | 17/100 | OK |
| 9 | Accepted | `batch=32, seqlen_k_cap=4096, kv_heads=8, kind=perf` | 0.317 | 1.411 | 0.225x | 18/100 | OK |
| 10 | Accepted | `batch=1, seqlen_k_cap=8192, kv_heads=4, kind=perf` | 0.064 | 0.164 | 0.390x | 28/100 | OK |
| 11 | Accepted | `batch=16, seqlen_k_cap=12251, kv_heads=4, kind=perf` | 0.249 | 1.457 | 0.171x | 14/100 | OK |
| 12 | Accepted | `batch=8, seqlen_k_cap=32768, kv_heads=8, kind=perf` | 0.572 | 2.817 | 0.203x | 16/100 | OK |
| 13 | Accepted | `batch=1, seqlen_k_cap=58966, kv_heads=8, kind=perf` | 0.241 | 0.912 | 0.264x | 20/100 | OK |
| 14 | Accepted | `batch=1, seqlen_k_cap=61519, kv_heads=4, kind=perf` | 0.172 | 0.793 | 0.217x | 17/100 | OK |

##### 原始评测归档

完整 OJ 原始响应（含 OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）已保存为 JSON：

- [cuda_103932_raw.json](raw/cuda_103932_raw.json)

#### 提交 #103918 · 2026-08-06 18:35:06

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/103918)

- **提交时间**：2026-08-06 18:35:06
- **提交语言/环境**：CUDA Maca C500 / 20.1 K（cuda.maca-c500）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：Accepted
- **总分**：`30.21`
- **OJ 内存**：`22.0 G`（页面精确值：`23059860 K / 41943040 K`）
- **测试点**：14 个

##### 结果分析

- 14 个测试点全部 Pass：正确性恢复（v3 的 direct-out 缺陷已修复）。
- 相比 v2（#103870），本版为「v3 结构 + 标量写 + 回退 direct-out」：双缓冲 + split 2048 保留。
- 总分 30.21 < v2 的 31.14：**双缓冲负优化**——smem 8KB→16KB 使每 SM 驻留 block 从 6→3，占用率减半。case 7（1.38→1.62ms）、case 9（1.41→1.68ms）、case 12（2.81→3.06ms）、case 13（0.91→1.27ms）均退化；case 2 反而提升（25→19μs）。
- 下一步：回退双缓冲（v4），恢复单缓冲 + 8KB smem 的高占用率。

##### 测试点汇总

| 测试点 | 状态 | 配置 | 基准 (ms) | User kernel (ms) | 加速比 | 得分 | 检查结果 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Accepted | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge` | 0.038 | 0.015 | 2.533x | 71/100 | OK |
| 2 | Accepted | `batch=4, seqlen_k_cap=2, kv_heads=8, kind=edge` | 0.038 | 0.019 | 2.000x | 66/100 | OK |
| 3 | Accepted | `batch=16, seqlen_k_cap=17, kv_heads=4, kind=edge` | 0.046 | 0.032 | 1.438x | 58/100 | OK |
| 4 | Accepted | `batch=64, seqlen_k_cap=64, kv_heads=8, kind=perf` | 0.06 | 0.104 | 0.577x | 36/100 | OK |
| 5 | Accepted | `batch=16, seqlen_k_cap=141, kv_heads=4, kind=perf` | 0.046 | 0.089 | 0.517x | 34/100 | OK |
| 6 | Accepted | `batch=16, seqlen_k_cap=362, kv_heads=8, kind=perf` | 0.049 | 0.145 | 0.338x | 25/100 | OK |
| 7 | Accepted | `batch=64, seqlen_k_cap=2048, kv_heads=8, kind=perf` | 0.281 | 1.622 | 0.173x | 14/100 | OK |
| 8 | Accepted | `batch=16, seqlen_k_cap=4096, kv_heads=4, kind=perf` | 0.111 | 0.528 | 0.210x | 17/100 | OK |
| 9 | Accepted | `batch=32, seqlen_k_cap=4096, kv_heads=8, kind=perf` | 0.317 | 1.68 | 0.189x | 15/100 | OK |
| 10 | Accepted | `batch=1, seqlen_k_cap=8192, kv_heads=4, kind=perf` | 0.064 | 0.173 | 0.370x | 27/100 | OK |
| 11 | Accepted | `batch=16, seqlen_k_cap=12251, kv_heads=4, kind=perf` | 0.249 | 1.43 | 0.174x | 14/100 | OK |
| 12 | Accepted | `batch=8, seqlen_k_cap=32768, kv_heads=8, kind=perf` | 0.572 | 3.062 | 0.187x | 15/100 | OK |
| 13 | Accepted | `batch=1, seqlen_k_cap=58966, kv_heads=8, kind=perf` | 0.241 | 1.27 | 0.190x | 15/100 | OK |
| 14 | Accepted | `batch=1, seqlen_k_cap=61519, kv_heads=4, kind=perf` | 0.172 | 0.865 | 0.199x | 16/100 | OK |

##### 原始评测归档

完整 OJ 原始响应（含 OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）已保存为 JSON：

- [cuda_103918_raw.json](raw/cuda_103918_raw.json)

#### 提交 #103891 · 2026-08-06 18:03:55

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/103891)

- **提交时间**：2026-08-06 18:03:55
- **提交语言/环境**：CUDA Maca C500 / 20.4 K（cuda.maca-c500）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：WrongAnswer
- **总分**：`0`
- **OJ 内存**：`22.0 G`（页面精确值：`23061884 K / 41943040 K`）
- **评测进度**：样例 #1 失败，14 个测试点全部跳过

##### 结果分析

- 样例 #1（单 token）失败：3596/4096 元素超差，max_abs_diff=5.0 —— 输出几乎全 0，判定为 v3 新增的 direct-out 路径用 `reinterpret_cast<float2*>(bf16_ptr)` 跨类型别名写，在 maca 编译器上未生效。
- 14 个测试点全部跳过。

##### 测试点汇总

| 测试点 | 状态 | 说明 |
|---:|---|---|
| 样例 #1 | Wrong Answer | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge`；3596 个元素超出容差 |
| 测试点 #1 至 #14 | Skipped | 样例 #1 先失败，未执行 |

##### 原始评测归档

完整 OJ 原始响应（含 OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）已保存为 JSON：

- [cuda_103891_raw.json](raw/cuda_103891_raw.json)

#### 提交 #103870 · 2026-08-06 17:39:43

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/103870)

- **提交时间**：2026-08-06 17:39:43
- **提交语言/环境**：CUDA Maca C500 / 18.3 K（cuda.maca-c500）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：Accepted
- **总分**：`31.14`
- **OJ 内存**：`22.0 G`（页面精确值：`23059600 K / 41943040 K`）
- **测试点**：14 个

##### 结果分析

- 14 个测试点全部 Pass，总分 31.14（当前最佳）。
- v2（第一轮优化）：uint32 向量化加载消除 bank conflict + page 级 2-pass softmax + split 目标 1024。
- 相比 v1：case 3-11、13、14 全部提升（case 5: 0.41→0.61x，case 10: 0.18→0.39x）；case 1/2 轻微退化（2-pass 固定开销）；case 12 持平。
- 瓶颈：单 block 每-token 效率（有效算力 ~0.8 TFLOPS vs baseline ~3.7 TFLOPS）。

##### 测试点汇总

| 测试点 | 状态 | 配置 | 基准 (ms) | User kernel (ms) | 加速比 | 得分 | 检查结果 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Accepted | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge` | 0.038 | 0.015 | 2.533x | 71/100 | OK |
| 2 | Accepted | `batch=4, seqlen_k_cap=2, kv_heads=8, kind=edge` | 0.038 | 0.025 | 1.520x | 60/100 | OK |
| 3 | Accepted | `batch=16, seqlen_k_cap=17, kv_heads=4, kind=edge` | 0.046 | 0.031 | 1.484x | 59/100 | OK |
| 4 | Accepted | `batch=64, seqlen_k_cap=64, kv_heads=8, kind=perf` | 0.06 | 0.097 | 0.619x | 38/100 | OK |
| 5 | Accepted | `batch=16, seqlen_k_cap=141, kv_heads=4, kind=perf` | 0.046 | 0.075 | 0.613x | 38/100 | OK |
| 6 | Accepted | `batch=16, seqlen_k_cap=362, kv_heads=8, kind=perf` | 0.049 | 0.148 | 0.331x | 24/100 | OK |
| 7 | Accepted | `batch=64, seqlen_k_cap=2048, kv_heads=8, kind=perf` | 0.281 | 1.382 | 0.203x | 16/100 | OK |
| 8 | Accepted | `batch=16, seqlen_k_cap=4096, kv_heads=4, kind=perf` | 0.111 | 0.524 | 0.212x | 17/100 | OK |
| 9 | Accepted | `batch=32, seqlen_k_cap=4096, kv_heads=8, kind=perf` | 0.317 | 1.41 | 0.225x | 18/100 | OK |
| 10 | Accepted | `batch=1, seqlen_k_cap=8192, kv_heads=4, kind=perf` | 0.064 | 0.164 | 0.390x | 28/100 | OK |
| 11 | Accepted | `batch=16, seqlen_k_cap=12251, kv_heads=4, kind=perf` | 0.249 | 1.449 | 0.172x | 14/100 | OK |
| 12 | Accepted | `batch=8, seqlen_k_cap=32768, kv_heads=8, kind=perf` | 0.572 | 2.805 | 0.204x | 16/100 | OK |
| 13 | Accepted | `batch=1, seqlen_k_cap=58966, kv_heads=8, kind=perf` | 0.241 | 0.911 | 0.265x | 20/100 | OK |
| 14 | Accepted | `batch=1, seqlen_k_cap=61519, kv_heads=4, kind=perf` | 0.172 | 0.797 | 0.216x | 17/100 | OK |

##### 原始评测归档

完整 OJ 原始响应（含 OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）已保存为 JSON：

- [cuda_103870_raw.json](raw/cuda_103870_raw.json)

#### 提交 #103799 · 2026-08-06 16:33:33

##### 提交信息

提交记录：[打开 OJ 页面](https://xpuoj.com/contest/11/submissions/103799)

- **提交时间**：2026-08-06 16:33:33
- **提交语言/环境**：CUDA Maca C500 / 15.4 K（cuda.maca-c500）
- **提交者**：`muxi2026C2009`

##### 提交总览

- **总状态**：Accepted
- **总分**：`28.29`
- **OJ 内存**：`22.0 G`（页面精确值：`23059660 K / 41943040 K`）
- **测试点**：14 个

##### 结果分析

- v1 基线：GQA 组内复用 + split-KV + 逐 token 在线 softmax。
- edge case（1-3）快于基准（2.9x/2.4x/1.2x）；perf case 全线慢于基准（0.13-0.58x）。
- 问题：每 token 串行依赖链长、2B 粒度加载、smem 2-way bank conflict、每 page 2 次同步。

##### 测试点汇总

| 测试点 | 状态 | 配置 | 基准 (ms) | User kernel (ms) | 加速比 | 得分 | 检查结果 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Accepted | `batch=1, seqlen_k_cap=1, kv_heads=4, kind=edge` | 0.038 | 0.013 | 2.923x | 74/100 | OK |
| 2 | Accepted | `batch=4, seqlen_k_cap=2, kv_heads=8, kind=edge` | 0.038 | 0.016 | 2.375x | 70/100 | OK |
| 3 | Accepted | `batch=16, seqlen_k_cap=17, kv_heads=4, kind=edge` | 0.046 | 0.038 | 1.211x | 54/100 | OK |
| 4 | Accepted | `batch=64, seqlen_k_cap=64, kv_heads=8, kind=perf` | 0.06 | 0.104 | 0.577x | 36/100 | OK |
| 5 | Accepted | `batch=16, seqlen_k_cap=141, kv_heads=4, kind=perf` | 0.046 | 0.111 | 0.414x | 29/100 | OK |
| 6 | Accepted | `batch=16, seqlen_k_cap=362, kv_heads=8, kind=perf` | 0.049 | 0.293 | 0.167x | 14/100 | OK |
| 7 | Accepted | `batch=64, seqlen_k_cap=2048, kv_heads=8, kind=perf` | 0.281 | 1.492 | 0.188x | 15/100 | OK |
| 8 | Accepted | `batch=16, seqlen_k_cap=4096, kv_heads=4, kind=perf` | 0.111 | 0.83 | 0.134x | 11/100 | OK |
| 9 | Accepted | `batch=32, seqlen_k_cap=4096, kv_heads=8, kind=perf` | 0.317 | 1.554 | 0.204x | 16/100 | OK |
| 10 | Accepted | `batch=1, seqlen_k_cap=8192, kv_heads=4, kind=perf` | 0.064 | 0.361 | 0.177x | 15/100 | OK |
| 11 | Accepted | `batch=16, seqlen_k_cap=12251, kv_heads=4, kind=perf` | 0.249 | 1.671 | 0.149x | 12/100 | OK |
| 12 | Accepted | `batch=8, seqlen_k_cap=32768, kv_heads=8, kind=perf` | 0.572 | 2.374 | 0.241x | 19/100 | OK |
| 13 | Accepted | `batch=1, seqlen_k_cap=58966, kv_heads=8, kind=perf` | 0.241 | 1.118 | 0.216x | 17/100 | OK |
| 14 | Accepted | `batch=1, seqlen_k_cap=61519, kv_heads=4, kind=perf` | 0.172 | 1.02 | 0.169x | 14/100 | OK |

##### 原始评测归档

完整 OJ 原始响应（含 OJCHAL/OJRESULT 协议、SPJ 报告、编译日志）已保存为 JSON：

- [cuda_103799_raw.json](raw/cuda_103799_raw.json)
