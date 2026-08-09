# MetaX C500 FlashAttention 优化手册

本仓库用于优化 XPUOJ Contest 11 的 FlashAttention paged KV-cache decode CUDA/MACA 实现。本文件是后续 agent 的首要入口，集中记录文件组织、真值来源、验证闭环、已经证实的优化方向、失败路线和接续流程。

## 1. 当前状态与源码角色

当前真实 OJ 最高分为 **`57.64`**：#106626 将 case 11 改为 256-thread `(16,4,4)` head-pair/z4 CTA，一次 K/V load/unpack 服务两个 query head，四个 z-state 通过 8 KiB shared 两级归约；本地 case 11 ratio p50 `0.9528`，OJ `438→417 μs`、`36→37` 分。当前选定最优提交为 **#106626**。

| 路径 | 角色 | 修改规则 |
|---|---|---|
| `solutions/archive/2026-08-09-submissions/cuda_106626.cpp` | **当前选定最优提交的不可变源码**，同时作为新实验的默认 control。它已由 raw 字节精确提取，不再额外维护“当前最佳”副本。 | 永远不修改；新最优出现后保留本文件作为历史事实，并把本文的当前最佳指针改到新提交快照。 |
| `solutions/cuda_maca_optimized.cpp` | **可变优化工作文件**。本地实验、迭代和下一次提交都在这里进行。空闲状态应与当前选定最优提交快照一致，实验期间允许偏离。 | 可以持续修改；提交前必须记录 SHA-256，并完成本文要求的验证。 |
| `solutions/cuda_maca_version.cpp` | **早期维护/对照源码**。用于复现历史实现和本地 control，不是当前最优，也不是默认的新优化起点。 | 除非明确在修复或复现历史基线，否则不要修改。 |

后续开始新实验时，若工作文件含有失败或未完成改动，先归档有价值的候选，再用当前选定最优提交快照恢复 `solutions/cuda_maca_optimized.cpp`，不要从早期 `cuda_maca_version.cpp` 重新分叉。当前最佳路径写在本节和 `results/cuda_result.md` 中；新最优出现时更新文档指针即可，不创建内容重复的 stable/best/frozen 源码。

## 2. 真值优先级

当源码、文档和计时互相矛盾时，按以下顺序判断：

1. `results/raw/cuda_<id>_raw.json`：OJ 原始状态、分数、测试点、SPJ、编译信息和提交源码；
2. `solutions/archive/<date>-submissions/cuda_<id>.cpp`：从 raw 的 `raw_detail.content.code` 提取的字节精确提交源码；
3. 当前选定最优提交对应的不可变逐提交快照；
4. `results/cuda_result.md`：整理后的提交索引、14-case 数据和实验结论；
5. 具有源码 SHA-256 的本地 C500 correctness/A-B 记录；
6. `build/` 里的 `.so`、临时候选、研究笔记和静态推断；
7. `problem.md` 中可能不完整或字段错位的静态测试点表格。

真实 14 个 OJ shape 统一由 `tests/c500_case_manifest.py` 从 Accepted raw 的 SPJ 配置解析。不要另抄一份容易漂移的 case 配置。

## 3. 问题固定规格与正确性底线

OJ 主路径固定为：

```text
seqlen_q        = 1
num_heads       = 32
num_heads_k     = 4 或 8
headdim         = 128
page_block_size = 16
causal          = 0
输入/输出        = BF16
score/LSE/PV    = FP32
```

必须始终遵守：

- `seqlen_k` 是 KV cache 容量，`cache_seqlens[b]` 才是 batch `b` 的真实可读 token 数。
- `block_table` 每行只有前 `ceil(cache_seqlens[b] / 16)` 个 page slot 有效。padding slot 可能仍存放合法物理 page ID，不能按 ID 值判断有效性，也不能预读。
- query head `h` 使用 `kv_head = h / (num_heads / num_heads_k)`。
- 不完整尾页必须逐 token mask；长度 1、2、15、16、17 和随机变长 batch 都是关键边界。
- online softmax 必须在 FP32 中稳定合并 `(m, l, acc)`；split reducer 使用 log-sum-exp 权重合并 partial。
- 不允许 NaN/Inf，不允许依靠未初始化或旧 workspace 内容。
- 不在 `run_kernel` 内调用 `cudaDeviceSynchronize()`；OJ 会在计时边界同步。
- 当前 generic fallback 不是已证明的任意 shape 完整 attention。所有性能和正确性结论只覆盖 OJ 固定 fast path，不能外推。

本项目验证采用的 OJ 容差复刻为：

```text
ATOL = 0.016
RTOL = 0.016
edge case：100% 元素在 tolerance 内
perf case：至少 99% 元素在 tolerance 内
任一元素不得超过 8 * (ATOL + RTOL * abs(reference))
```

## 4. 当前 14-case 结果快照

下表来自 #106626 raw，耗时单位为 `μs`。历史最佳只统计整次 14/14 Accepted 的提交；它们分散在不同源码中，不能直接拼接并假定同时成立。

| Case | Shape | #106626 | 分数 | Accepted 历史最佳 |
|---:|---|---:|---:|---|
| 1 | B1 / L1 / KV4 / edge | 3 | 92 | 3（#105899 等） |
| 2 | B4 / L2 / KV8 / edge | 4 | 90 | 4（#105899 等） |
| 3 | B16 / L17 / KV4 / edge | 10 | 82 | 10（#105915 等） |
| 4 | B64 / L64 / KV8 | 30 | 66 | 29（#105814/#105915） |
| 5 | B16 / L141 / KV4 | 25 | 64 | 25（#105932/#106069） |
| 6 | B16 / L362 / KV8 | 33 | 59 | 33（多次） |
| 7 | B64 / L2048 / KV8 | 322 | 46 | 320（#105899） |
| 8 | B16 / L4096 / KV4 | 174 | 38 | 174（多次） |
| 9 | B32 / L4096 / KV8 | 322 | 49 | 321（#105915/#105952） |
| 10 | B1 / L8192 / KV4 | 57 | 52 | 57（#105801/#106626） |
| 11 | B16 / L12251 / KV4 | 417 | 37 | 417（#106626） |
| 12 | B8 / L32768 / KV8 | 533 | 51 | 533（#105823/#105899/#105952） |
| 13 | B1 / L58966 / KV8 | 294 | 45 | 294（多次） |
| 14 | B1 / L61519 / KV4 | 296 | 36 | 296（#105801/#106626） |

115 份现有 raw 的状态统计为：102 Accepted、9 WrongAnswer、4 CompilationError。#105561–#105952 的 20 次连续优化以及最新 #106069/#106116/#106170/#106503/#106556/#106584/#106626 均为 14/14 Accepted。

## 5. 已建立的真实 C500 验证闭环

### 5.1 Case 与 CPU 语义验证

- `tests/c500_case_manifest.py` 从 Accepted OJ SPJ 解析 case ID、batch、capacity、KV heads、edge/perf、baseline 和既有 split policy。
- `tests/test_kernel_logic.py` 用 NumPy 重放 GQA、paged lookup、split-KV、online softmax 和 reducer，适合快速发现数学、索引和 split 边界错误。

常用命令：

```bash
python3 tests/c500_case_manifest.py
python3 tests/test_kernel_logic.py
```

### 5.2 本地 MACA 构建与 GPU correctness

`tools/build_local_maca.sh` 使用本机 `/opt/maca/mxgpu_llvm/bin/mxcc` 和 CUDA compatibility bridge 编译 shared object。实验必须让“源码 SHA-256、`.so` 路径、测试结果”形成一一对应，不能只凭相似文件名归因。

```bash
sha256sum solutions/cuda_maca_optimized.cpp
tools/build_local_maca.sh \
  solutions/cuda_maca_optimized.cpp \
  build/cuda_maca_optimized.so
```

`tests/c500_paged_decode_harness.py` 通过 `ctypes.CDLL` 调用题目 ABI，使用系统安装的 `flash_attn_with_kvcache` 作 reference，不构建仓库子模块。输入会随机化物理 page 映射，并在 padding slot 放置合法 page ID，用来捕获越界 page-table 读取。

同一个 `.so` 至少执行：

```bash
python3 tests/c500_paged_decode_harness.py \
  --library build/cuda_maca_optimized.so --full-length
python3 tests/c500_paged_decode_harness.py \
  --library build/cuda_maca_optimized.so --lengths boundary
python3 tests/c500_paged_decode_harness.py \
  --library build/cuda_maca_optimized.so --lengths random --seed 20260809
```

若 producer 会跳过空 split，而 reducer 只读 live split，还必须在同一进程验证 full→short、short→full，排除 static workspace 复用旧 partial。

多个长 case 连续跑 reference 时可能因驱动/cache/显存压力出现 `Exit 137 / Killed`。这代表资源压力，不等于 numerical mismatch；应拆成单 case process 重跑，也不能把它报告为通过。

### 5.3 交错 A/B 性能测试

`tests/c500_benchmark.py` 每个 round 都让 control/candidate 紧邻执行，并交替顺序：

```text
round 0: control → candidate
round 1: candidate → control
round 2: control → candidate
...
```

结论使用每轮 `candidate/control` ratio 的 p10/p50/p90，不使用分别跑出的两个绝对 p50。这样可以减弱 C500 时钟、温度、功耗状态和 warm-cache 偏差。

```bash
tools/build_local_maca.sh \
  solutions/archive/2026-08-09-submissions/cuda_106626.cpp \
  build/cuda_106626_control.so
python3 tests/c500_benchmark.py \
  --control build/cuda_106626_control.so \
  --candidate build/cuda_maca_optimized.so \
  --cases 7,9,12,13 --warmup 5 --iterations 20 --rounds 9
```

### 5.4 官方 MXMACA 内建函数指南与使用规则

官方参考资料为[《沐曦通用 GPU MXMACA 编译器内建函数编程指南》](https://developer.metax-tech.com/api/client/document/preview/1395/index.html)。其接口与本机 MACA 3.7.1 的 `/opt/maca-3.7.1/include/mctlass/`、`/opt/maca-3.7.1/include/mcflashinfer/` 用法相符；实现新候选时先查官方签名和架构限制，再核对本机头文件中的真实包装与调用方式。文档说明接口语义，但不能替代本地 C500 correctness、资源报告和交错 A/B。

不要只依赖这一份指南。[沐曦开发者平台](https://developer.metax-tech.com/)的文档中心还应作为优化研究入口；针对当前假设，优先检索 C500/xcore 执行模型、MXMACA 编译器与 release notes、CUDA compatibility 差异、内存模型与 BSM/异步流水、barrier/shuffle、MMA fragment/布局/精度、性能分析和资源占用等资料。只阅读与当前假设直接相关的文档，不做无目标的资料堆积。

官方资料也有版本和架构边界。引用其结论时应在实验记录中保留文档标题、URL、访问日期、适用 MACA 版本/`offload-arch` 和它支持的具体假设；随后检查本机 MACA 3.7.1 头文件和 `mxcc -offload-arch=xcore1000` 是否一致。若网页、安装头文件、编译行为和真实 C500 runtime 互相冲突，以本机编译与 correctness/A-B 证据决定当前生产路径，并把差异写入本手册，不能仅凭其他代际或其他架构文档移植代码。不要整篇复制官方资料，只沉淀能改变实现、验证或关闭方向的结论。

与本项目直接相关的架构事实和约束：

- 一个原生 MXMACA warp 有 64 个线程，分成四个连续的 16-lane row。`__builtin_mxc_mov_shfl`/`__builtin_mxc_update_shfl` 只在各自 row 内交换；`__builtin_mxc_bsm_bpermute`/`__builtin_mxc_bsm_permute` 才能覆盖整个 64-lane warp。这解释了当前 16-lane 最小安全粒度。原生 builtin 与 CUDA compatibility shuffle 的 lane/mask 语义不能混用；已有 32-lane full-mask 路径继续以实测 correctness 为准，新交换方式必须隔离验证。
- `__builtin_mxc_ldg_b32/b64/b128_bsm` 用于 global→shared，`mask` 参数只能填 `-1`；返回值是交给 `__builtin_mxc_barrier_and_wait*` 的同步 token，不是加载数据。`is_async=true` 时必须显式安排 arrive/wait，不能依赖编译器隐式同步。
- `__builtin_mxc_barrier_and_wait*` 的 `scope=0` 仅执行内存栅栏，适用于没有跨 warp shared 数据交换的依赖；`scope=1` 同时执行内存栅栏和指令屏障，语义等同 `__syncthreads()`，用于跨 warp shared 数据。`__builtin_mxc_barrier_ex(flag)` 中 `0` 为指令屏障加自动内存栅栏，`1` 为指令屏障加 shared 栅栏，`2` 仅指令屏障，`3` 仅阻止编译优化且不产生同步。后续可据此研究缩小 barrier 范围和 BSM loader/compute pipeline，但首轮只能做唯一差异 A/B。
- `__builtin_mxc_pk_fma_f32(v2f32,v2f32,v2f32)`、`__builtin_mxc_pk_mul_f32` 和 `__builtin_mxc_pk_add_f32` 可用于标量 QK/PV 热循环；是否优于普通 CUDA vector 表达式仍由 codegen、资源和实测决定。
- `__builtin_mxc_pk_fma_bf16` 与 `__builtin_mxc_fma_bf16` 要求 `offload-arch >= xcore1500`，而本项目 C500 编译目标为 `xcore1000`，不得用于生产路径。
- `__builtin_mxc_mma_16x16x16bf16` 暴露 FP32 accumulator/result 并不能证明硬件内部是真 FP32 累加，现有 BF16 MMA-QK 数值失败结论仍有效。官方另提供 `__builtin_mxc_mma_16x16x4f32(float,float,v4f32)`，其接口为 FP32 输入与 FP32 accumulator/result，构成一条新的 QK 研究路线：只能从未 launch 编译 probe、fragment/layout 核对和单 case 原型开始，不能直接重新启用旧 BF16 MMA dispatch。
- `__builtin_mxc_get_time()` 可用于仅诊断版本的 kernel phase timing；探针会改变调度和资源，不能作为最终性能结论，也不能进入提交源码。

采用新 builtin 的固定流程：

1. 查官方指南的签名、参数、同步语义和架构门槛。
2. 查本机 MACA 3.7.1 头文件中的同接口实例，确认 `mxcc -offload-arch=xcore1000` 的实际用法。
3. 先编译未 launch probe，读取寄存器、shared memory、spill 和 static occupancy；“能编译”不算 runtime 证据。
4. runtime 候选先只 dispatch 一个代表 case，完成数值、tail、page-table padding trap 和 workspace 复用验证。
5. 与当前最佳 control 做交错 A/B；只有明确收益且无非目标回退，才扩大 shape 覆盖并进入完整回归。

### 5.5 沐曦官方 `op_optimization` 仓库

官方仓库为 [`metax-maca/op_optimization`](https://www.gitlink.org.cn/metax-maca/op_optimization/tree/master)，并以只读参考子模块固定在 `third/op_optimization/`。2026-08-09 已审阅并 pin 到 `master` commit `4f2aa14e92353e382e59bae98abe2c19e652ebd7`；远端仓库更新频繁，但后续实验默认读取父仓库记录的固定 commit，不能把浮动 `master` 内容悄悄混入归因。该仓库采用木兰宽松许可证第 2 版（Mulan PSL v2）；若复制实现而不只是参考思路，必须记录源文件和 commit，并保留许可证及版权声明。

优先按以下路径提取信息：

| 官方路径 | 主要用途 | 使用边界 |
|---|---|---|
| `README.md`、`FAQ.md` | 规则、环境版本、baseline/榜单调整和资料入口。 | 可改变规则判断；正式成绩仍以 XPU-OJ raw 为准，前三门槛仍只读本仓库 `leadboard.md`，不要借此主动刷新排行榜。 |
| `基于AI Agent开发范式的国产GPU大模型推理算子库优化/FlashAttention关键算子迁移与优化.md` | ABI、paged decode 语义、mctlass 要求、benchmark 和优化路线。 | 教程附录明确只是 smoke code，不是最优实现或评分参考；其中较宽泛的容差、shape 和性能数据不能覆盖本题 raw/SPJ。 |
| `.../operator_task_package/flashattn_task_package/` | 官方 starter 与 `benchmark_kvcache.py`。 | 用于 API、环境和趋势诊断；默认 H8/KV8/D256 等扫描不是本题 H32/KV4/8/D128 的 case 真值。 |
| `.../fused_moe_task_package/benchmark/standalone/` | xcore1000 上 BSM、barrier、packed FMA、MMA guard 和 shared layout 的真实源码实例。 | 跨算子代码只能提取底层用法，不能假定 MoE 的 tile/layout 在 Attention 上也更快或正确。 |
| GitLink commit/Issue | 查看规则变更、已知问题和维护者答复。 | 默认只读；没有用户明确授权，不创建 Issue、PR 或其他外部写入。 |

本次已提取并需要长期保留的事实：

- 官方统一环境标注为 `PyTorch-Agent 2.8.0 / Python 3.12 / MACA 3.7.1.5`。本机 2026-08-09 实测为 Python `3.12.11`、PyTorch `2.8.0+metax3.7.1.3`，`mxcc` build `d9102a1572` 位于 `/opt/maca-3.7.1/`；本地与 OJ 存在至少 patch-version 标识差异。本地 correctness/A-B 仍负责筛选，但 codegen、资源阈值和约 1% 以内收益可能不能原样映射到 OJ，提交归因必须注明该差异。
- 官方 FAQ 明确 FlashAttention KV Cache Decode 新增 `mctlass/cute` 要求；教程进一步写明 QK/PV 核心矩阵计算应使用 mctlass 组件或其基础计算原语，不应完全由手写 CUDA 循环替代。当前最佳源码包含 mctlass/cute 探测和未 launch CUTE probe，且已被 OJ Accepted，但 **OJ 接受不等于最终人工合规审查已经满足**；后续不得把这些 include/probe 当无用代码清理，也要继续寻找在生产热路径中可说明、可复现且正确的 mctlass/基础原语用法。若规则解释仍有歧义，先读取官方 Issue/公告并向用户报告，不自行降低要求。
- 官方 README/FAQ 曾发布 XPU-OJ baseline 修复和榜单清空通知，证明 baseline、环境和评分规则可能在比赛期间变化。若再次出现官方变更，应按变更点把提交分段比较，重新建立 post-change control；不得把调整前后的绝对耗时或分数直接归因为源码。该规则不改变 `leadboard.md` 作为本项目前三门槛的唯一来源。
- 官方优化建议包括 kernel fusion、Split-K、online softmax、合并/向量化访存、寄存器/shared 分层、软件流水和减少分支；这些多数已进入本项目主架构，只作为方向索引。是否仍有余量必须结合第 7–9 节已有 A/B 和失败边界，不能退回官方 smoke baseline 重做。
- 官方 xcore1000 standalone 示例确认 packed FP32 FMA 的实际写法，也展示了 BSM `ldg_b128_bsm(..., mask=-1, ..., is_async=true)` 后使用 `__builtin_mxc_arrive(64 + count)` 与 `__builtin_mxc_barrier_inst()` 等待的模式，以及用 `__MACA_ARCH__` 对原生 MMA 做架构 guard。该模式可作为当前 BSM 路线的新 pipeline probe，但样例是 I8 MoE；必须在单一 Attention case 上重新验证同步、布局、资源和收益，不能推翻“当前长 KV8 BSM 慢约 2.5–2.7%”的既有证据。
- 官方 FAQ 确认比赛镜像提供 Linux `mcprofiler`；本机可见 `/opt/mcProfiler-ubuntu18.04/`。可在 OJ 排队期间用它做诊断，但 profiler 会扰动计时，生成的 `.db`/`profiler.log` 必须放在仓库外临时目录或测试后清理，不能提交，也不能替代交错 A/B。
- 官方 `benchmark_kvcache.py` 使用 PyTorch profiler、warmup/repeat 和有效带宽估算，可用于检查大尺度趋势。套用带宽模型到本题变长 batch 时必须按 `sum(cache_seqlens)` 计算实际读取的 live K/V token，不能按 `seqlen_k` 容量把 padding 当有效流量。

官方仓库复查流程：正常查阅直接读取 `third/op_optimization/`，并用 `git -C third/op_optimization rev-parse HEAD` 记录证据版本。在开始新的大方向、遇到无法解释的本地/OJ差异、环境编译变化或官方公告时，用 `git ls-remote https://www.gitlink.org.cn/metax-maca/op_optimization.git HEAD` 与当前 pin 比较；若远端变化，可先 `git -C third/op_optimization fetch origin master` 并只读检查 `HEAD..origin/master` 的新增 commit 和上表相关路径。只有确认新内容会改变规则、环境、实现或验证时，才移动 submodule gitlink，并在同一改动中更新本节审阅 commit 和提取结论；不要只执行 `git submodule update --remote` 后留下无说明的版本漂移。不得修改子模块内容、执行未经审查的脚本、把它变成提交运行依赖，也不要因资料更新而联网刷新 `leadboard.md`。

## 6. 分数演进与关键里程碑

| 提交 | 分数 | 已确认的主要贡献 |
|---:|---:|---|
| #103799 | 28.29 | 初始正确基线。 |
| #104025 | 34.79 | `uint4` K/V page load 与 `n_split==1` 直接输出。 |
| #104091 | 36.21 | cooperative split-KV reducer，建立后续主结构。 |
| #104217/#104221 | 35.21/37.07 | KV8 16-lane paired-token QK，以及与选择性 KV4 路径组合。 |
| #104278–#104441 | 38.21–38.64 | 按 shape 扫描 split/page 粒度，建立 7/9/12/11/8/6/5/10 等策略。 |
| #105501 | 40.71 | 编译期模板特化与 global-max page softmax 化简。 |
| #105561 | 48.93 | 首次 token-parallel CTA，结构性大跃升。 |
| #105601 | 50.29 | 单 live-split 直出与 8 heads/CTA grouped reducer。 |
| #105616 | 51.29 | packed FMA/scale/accumulate 热循环。 |
| #105738 | 51.93 | packed pair QK/PV 与条件 max 更新。 |
| #105762 | 54.21 | KV4 Q staging，token-parallel full-page/tail 专门循环。 |
| #105814/#105823 | 55.29/55.36 | full/tail 分离 launch；KV8 z-state 在 CTA 内合并。 |
| #105899 | 56.21 | 单 token 直接 V copy、双 token 专用 attention。 |
| #105915 | **57.43** | token-parallel threshold 从 64 下调到 17，case 3 从 22 降到 10 μs。 |
| #105932/#105952 | **57.43** | 小 split register/shuffle reducer；短 KV8 loader A/B，保持最高分。 |
| #106069 | **57.57** | case 11 Q shared-memory 复用（`INPLACE_SHARED_Q`）移植到 token-parallel：`sync_kv4+separate_tail` 去掉 2 KiB 动态 Q、case 11 `0.448→0.438 ms`；本地交错 A/B 确认 case 11 ratio p50 `0.9727`，其余中性。 |
| #106116 | 57.43 | case 8 的 KV4 `separate_tail` occupancy 候选：本地 case 8 ratio p50 `0.941`，但 OJ case 8 `175 μs` 未超过 #106069 `174 μs`、case 11 `443 μs` 回退，总分未保持；14/14 Accepted，拒绝为 baseline。 |
| #106170 | 57.57 | full-page QK 双 token 交错 packed-FMA/shuffle：本地各目标 case 约 `0.2–0.3%`，OJ 14/14 与 #106069 并列；case 4 `29 μs` 有利、但 case 8/11/12 为 `179/440/537 μs` 回退，**不得取代 baseline**。证明 scalar QK 是主要余量但该微调不足跨越 OJ timing tier。 |
| #106503 | 57.57 | 只在 case 4 启用同一双-token schedule：本地 ratio p50 `0.9758`，非目标 case 中性；OJ case 4 仍为 `30 μs`、总分并列。隔离调度仍未稳定跨 tier，拒绝为 baseline。 |
| #106556 | 57.43 | case 11 使用 128-thread `(16,4,2)` head-pair reuse，一次 K/V shared load/unpack 服务两个 head且不重复 page loader；本地 p50 `0.9472`，但 OJ case 11 `452 μs`，exact 版本不替代 baseline。 |
| #106584 | 57.29 | 在 #106556 head-pair 内把每个 z 的 8-token score 改成两个顺序 4-token chunk，full kernel `100→82 MTreg`、本地 case 11 ratio p50 `0.9703`；OJ case 11 却为 `467 μs`。降低 live score 的 exact 局部扫描未跨 OJ tier，不替代 baseline。 |
| #106626 | **57.64** | case 11 改为 256-thread `(16,4,4)` head-pair/z4：每个 z 处理 4 token，K/V page 仍只加载一次，四个 z-state 在原 8 KiB shared 中两级归约；full/tail `84/50 MTreg`，本地 p50 `0.9528`，OJ case 11 `417 μs/37`，刷新总分并成为新 baseline。 |

#105952 相比初始 #103799 的各 case OJ 观测耗时改善约 `3.43x–8.88x`；相比 #105501 改善约 `1.80x–2.67x`。这些跨提交绝对比值会混入 OJ timing tier 波动，结构性因果仍以本地交错 A/B 和目标 case 为准。

## 7. 核心有效架构与实验归因

### 7.1 Token-parallel 是主要收益来源

KV8/GQA4 的核心布局为 `dim3(16, 4, 4)`：

```text
tx = 0..15：每线程负责连续 8 个 head dimensions
ty = 0..3 ：一个 query head
tz = 0..3 ：一个 token partition，每组处理 4 个 token
```

KV4/GQA8 使用同一思想和两个 `tz` partition。每个 partition 独立维护 `(m, l, acc[8])`，随后在 CTA 内或 split reducer 中稳定合并。相对旧 paired-QK，QK 和 PV 都减少串行 token 工作，并提高一页内的并行度。

本地真实 C500 相对 #105501 的长 KV8 p50 结果：

| Case | candidate/control | 推导加速 |
|---:|---:|---:|
| 7 | 0.6798x | 1.471x |
| 9 | 0.6802x | 1.470x |
| 12 | 0.6677x | 1.498x |
| 13 | 0.6252x | 1.599x |

case 13 的同步 loader 独立复测为 control `0.6617 ms`、candidate `0.4120 ms`，ratio p10/p50/p90 为 `0.6218/0.6228/0.6236`，说明不是一次性噪声。

### 7.2 Global-max softmax 化简

页状态直接按新的 global max 计算：

```cpp
const float m_new = max(m, m_page);
const float p = exp(logit - m_new);
const float alpha = exp(m - m_new);
m = m_new;
l = l * alpha + l_page;
acc = acc * alpha + acc_page;
```

它等价于先按 `m_page` 计权再乘 `beta = exp(m_page - m_new)`，但消除了 beta 及后续缩放链。#105501 的 14/14 Accepted 和本地 correctness 已验证这一变换。

### 7.3 Loader：同步 `uint4` 与 BSM 必须分开归因

唯一差异 A/B 显示，在长 KV8 上当前 BSM async page-copy 比同步 `uint4` loader 慢：

| Case | BSM/sync p50 | 结论 |
|---:|---:|---|
| 7 | 1.0250x | BSM 慢约 2.5% |
| 9 | 1.0259x | BSM 慢约 2.6% |
| 12 | 1.0270x | BSM 慢约 2.7% |

因此 token-parallel 的收益不来自 BSM。长 KV8 默认保留同步 loader；BSM 只能按 shape 重新验证。#105952 为 B64/KV8/L64 选择 BSM 后，OJ case 4 仍为 30 μs，没有超过 29 μs 历史最佳。

### 7.4 Split policy 是架构相关的

- 不存在统一最优 split；batch、KV heads、序列长度、CTA 大小和 reducer 成本共同决定粒度。
- case 7/9 的旧 paired-QK 路径在约 8 pages/split 附近较好，压到 4 pages/split 已回退。
- case 12：只把旧 #105501 从 256 改成 128 split 几乎无收益（ratio `1.0020x`）；token-parallel 的 256 split 又比 128 split 慢约 3%（ratio `1.0301x`）。所以加速主因是 token-parallel，128 只是该布局的配套最优点。
- aggregate 分数不能替代目标 case 计时。例如 #104334 的目标 case 回退但总分刷新；#105835 把 case 11 做到 439 μs，总分却受其他 case 波动降到 54.86。

### 7.5 其他已确认正方向

- 单缓冲 8 KB shared memory 保持更高 occupancy；双缓冲 16 KB 会使驻留 block 约减半。
- cooperative/live-split/grouped reducer、小 split register/shuffle reducer。
- packed FP32 FMA、scale、PV accumulate 与条件 max 更新。
- 在 token-parallel 架构中分离 full-page 和 tail-page，并为 KV4 staging Q。
- 完成 page loop 后复用 K/V shared memory合并 z-partition FP32 状态。
- L=1 直接复制 V、L=2 专用 attention、L=17 起启用 token-parallel。
- case 11 的 Q shared-memory 复用（`INPLACE_SHARED_Q`，`sync_kv4+separate_tail` 去掉 2 KiB 动态 Q）已在 #106069 稳定复现并把目标时延从 448 μs 降到 438 μs，本地交错 A/B ratio p50 `0.9727`、其余 case 中性；该机制保留在后续最佳源码中。
- case 11 的 head-pair 数据复用已由 #106626 转化为真实 OJ 收益：256-thread `(16,4,4)` CTA 保持每页 K/V 只加载一次，一个 unpack 服务两个 query head；每个 z 只处理 4 token，z2/z3 先写入原 8 KiB K/V shared，z0/z1 成对合并后再由 z0 完成第二级归约，不需要 16 KiB state。full/tail 为 `84/50 MTreg`、0 spill、8320 B shared、staticMaxWarps `5/7`；本地两轮 case 11 p50=`0.9531/0.9528`，OJ `438→417 μs`。收益关键不只是降低 live score，而是恢复 256-thread CTA 并改变 token partition/归约数据流。

注意：旧 paired-QK 中单纯复制 full-page predicate-free 分支是负优化；#105762 的正收益来自 token-parallel 循环、KV4 Q staging、full/tail 资源布局的组合，不能把两次实验混为一谈。

## 8. 已证伪或不得无假设重试的方向

正确性/后端风险：

- lane-dependent cross-subgroup shuffle：大范围 WrongAnswer；只使用已验证的 32-lane `0xffffffffu` shuffle mask，不盲改 64-bit mask。
- 8-lane/quad-token subgroup：超时式 WrongAnswer；16-lane subgroup 是当前最小安全粒度。
- raw 128-thread/two-wave WMMA：长 KV4 约 36 秒失败占位后 WrongAnswer。
- native packed BF16 conversion：目标 KV8 超时式 WrongAnswer；其他平台编译通过不代表 MACA 可用。
- forced CUTE four-wave QK/PV、V staging 扩展：长 case WrongAnswer。只编译未 launch 的 probe 不构成 runtime 证据。
- direct-out 跨类型别名写：曾出现输出未正确写入。
- 本地 C500 上历史 BF16 MMA-QK dispatch 对完整 KV4 paged input 无法稳定满足 OJ tolerance，当前生产 dispatch 保持关闭。2026-08-08 复诊确认根因不是布局或 accumulator 声明类型：`paged_decode_mma_qk_kernel` 已用 `wmma::accumulator<...,float>`（F32BF16BF16F32），逐行核对 A/B/C fragment、K 转置、online softmax、PV、output 均数学正确，但实测 case3(L17)=NaN、case5(L141) max_err=0.79、case8(L4096) max_err=0.12——误差随序列变短而增大。结论：**MACA `F32BF16BF16F32` 的 k=16 内积并非真 FP32 累加（硬件/后端精度限制）**，短序列 softmax 不够尖使分数扰动放大、更短时 `exp` 溢出→`l=Inf,acc=Inf`→direct-out `Inf*0=NaN`。该 BF16 MMA 路线属于不可由软件修正的精度墙，不得重开；第 5.4 节的原生 FP32 `mma_16x16x4f32` 是不同数据类型和 k 粒度的新路线，必须从零验证，不能继承旧 dispatch 的正确性或性能假设。

明确性能负优化：

- shared-memory 双缓冲；
- KV8 MMA-QK；
- BF16 P×V MMA；
- CTA-wide grouped-V PV；
- 手工 vectorized K transpose；
- 4 KB sequential K→V staging；
- 单纯 duplicated full-page branch；
- lane-0-only partial m/l store；
- 只调 `__launch_bounds__(threads, minBlocks)`，MACA 会忽略第二参数；
- 长 KV8 默认 BSM async loader；
- KV4 case 8 默认启用 `separate_tail`：#106116 虽本机 case 8 p50 `0.941x`，但 OJ case 8 `175 μs` 未优于 #106069 `174 μs`、case 11 还从 `438→443 μs`，14/14 Accepted 总分仅 `57.43`。B1 case 10/14 与短 case 5 的本机 A/B 已明确回退；该 dispatch 不得作为 baseline 重试。
- 全局 full-page QK 双-token interleaving：#106170 本地 `0.2–0.3%` 微增益但 OJ 与 #106069 同为 `57.57`，且 case 8/11/12 为 `179/440/537 μs`。该 source-level schedule 不足以稳定超越 timing tier；不作为 baseline 重投。其诊断反而确认 long KV4 QK 是主要余量，下一步须是更大粒度 QK architecture。
- case-4-only 双-token interleaving：#106503 已将 #106170 的唯一正向 shape 完全隔离，本地 ratio p50 `0.9758`、非目标 case 8/11/12 中性，但 OJ case 4 仍为 `30 μs` 且总分仍 `57.57`。同源 schedule 的全局版和局部版都已真实提交判定；不得复投或继续扫描 4/8-token group。4-token interleave 本地回退约 1.2%，8-token回退约 2.75%，说明扩大同时 live 的 dot 只会增加寄存器压力。
- FP32 K shared staging 探针在 case 11 回退约 46.9%；旧 512-thread/two-page 探针在 case 14 回退约 17.9%。二者身份只足够作为方向筛选证据，不据此归因细节，也不重构提交。
- case 11 KV4 `(32,8,1)` full-warp state-elision（exp6，未提交）：虽只用已验证的 32-lane full-mask XOR、并非 #104263 的 8-lane/broadcast 路径，去除 Q staging/z merge 后 full-only codegen 仍从 control 的 `70 MTreg / staticMaxWarps=7` 恶化为 `118 / 4`（0 B stack；shared `8320→8192 B`），而且每线程每页 QK shuffle `32→80`。资源门槛已反证该配置的 occupancy/state-traffic 假设；不得以同一布局再调 split/reducer/loader/launch 参数补偿。
- case 11 KV4 `(16,4,4)` head-group 拆分（exp10，未提交）：把一个 8-head CTA 拆成两个 4-head CTA 后，full/tail 寄存器从 `70/42→58/34 MTreg`，但 8320 B shared 使 staticMaxWarps 仍为 7；每页 K/V 被两个 CTA 重载，交错 A/B p10/p50/p90=`1.1267/1.1281/1.1298`。不得继续扫描同一“减少 CTA heads、增加 z、重复 loader”的布局或用 split 参数补偿。
- case 11 full-page QK 双 accumulator（exp11，未提交）：把每个 dot 的 4 级 packed-FMA 链拆成两条 2 级链，资源 `70→72 MTreg`、仍 7 warps，但 A/B p10/p50/p90=`1.0137/1.0148/1.0173`。结合 2/4/8 live-token interleave 的转折，当前 scalar QK source-level scheduling 已关闭；下一候选必须减少实际指令/转换或改变数据流。
- case 11 K 的 BF16 bitcast 解包（exp12，未提交）：用 `uint32` shift/mask + float bitcast 取代 `__bfloat162float` 后资源完全相同，A/B p10/p50/p90=`0.9976/0.9997/1.0008`。编译器已生成等价成本；纯源码 unpack 改写中性，不扩展到 PV/其他 case。
- case 11 `(16,4,2)` head-pair exact 版本（#106556）：它不是负方向——本地两轮均稳定快约 5.3%，且证明不重复 loader 的跨-head K/V unpack reuse 可行；但 full kernel `100 MTreg/staticMaxWarps=4`，OJ case 11 `452 μs` 未超过当时 baseline `438 μs`。禁止原样复投；#106626 的成功前提是恢复 256-thread/z4 与两级 reducer，不能把收益归给旧 exact 版本。
- case 11 shared-score producer/consumer（exp14，未提交）：256-thread CTA 中仅 4 个 head-pair producer 计算 QK，将 32 个 score 通过 512 B shared 交给 8 个 consumer 做 softmax/PV；full/tail 资源 `86/36 MTreg`、shared `8832 B`，case 11 full correctness PASS，但 A/B p10/p50/p90=`1.6010/1.6029/1.6040`。shared score handoff、额外同步和 producer 不均衡造成约 60% 稳定回退，关闭该 exact 数据流。
- case 11 head-pair 4-token sequential chunk（#106584）：保持 #106556 的 `(16,4,2)`/z=2 和不重复 loader，只把每个 z 的 8 个 score 拆成两个顺序 4-token chunk；full/tail 资源 `82/64 MTreg`、staticMaxWarps `5/7`。CPU 与 GPU full/boundary/random 均 14/14 PASS，本地 case 11 p10/p50/p90=`0.9689/0.9703/0.9733`，非目标 case 4/8/12 中性；但 OJ case 11 `467 μs/34`、总分 `57.29`。单纯降低同时 live score/register 仍不能消除本地/OJ 反转，z=2 下的 4/8-token live-score 局部扫描关闭。
- 无依据地过度或不足 split。

CompilationError、WrongAnswer 和约 36 秒失败占位时间不是 kernel 性能数据，不得用于计算 speedup。

## 9. 当前瓶颈与后续优先级

当前最值得投入的顺序：

1. **长 KV4 case 11/14/8**：当前分数分别为 37/36/38。case 11 以 #106626 的 256-thread `(16,4,4)` head-pair/z4 两级 reducer 为新 control；下一步先判断该架构能否安全扩展到 case 8，或在 case 11 上减少两级 reducer、partial/writeback 与 tail 成本。case 14 是 B1 长序列，仍需独立 CTA/split/work scheduling。旧 BF16 MMA-QK 继续禁用，但可按第 5.4 节从零验证 FP32 `mma_16x16x4f32`；`(32,8,1)`、重复-loader head-group、shared-score producer/consumer 和 128-thread z=2 的 4/8-live-score 点均已关闭。
2. **长 KV8 case 7/9/12/13**：token-parallel 计算布局已有效，下一步主要减少 launch、tail、shared-state 和 reducer 开销，长 KV8 继续以同步 `uint4` 为 control。
3. **距离 tier 仅约 1 μs 的 case 4/5/10/14**：局部 patch 必须在同一最终源码中验证，不能直接拼接不同提交的历史最佳。case 4 的双-token source schedule 已由 #106503 关闭，只能尝试会改变 launch、资源或数据流的新机制。
4. **case 11 head-pair/z4 已落地**（#106626，438→417 μs）：case 8/11/14 仍显著慢于题目 baseline，且均用 scalar QK（旧 BF16 MMA-QK 因 correctness 被禁）。继续从标量热循环、shared/reducer、split、原生 FP32 MMA probe 和 B1/B16 不同工作调度寻找架构收益，不把本次跨 tier 当成路线终点。

任何新方向都应先提出可证伪假设，例如“减少一次 tail launch”“降低某 reducer shared-memory 大小”，然后做唯一差异 A/B。不要把多个 loader、split、layout 和 reducer 改动混在一个首轮候选里。

## 10. 文件与目录组织

```text
.
├── solutions/                 可变工作源码、早期对照
│   └── archive/               不可变逐提交源码和历史实验
├── results/                   人类可读报告
│   └── raw/                   OJ 原始 JSON，一次提交一个文件
├── tests/                     CPU 语义、C500 correctness、交错 A/B
├── tools/                     构建、OJ 操作、源码归档
├── log/                       人工保留的编译诊断
├── build/                     可丢弃、可重建的本地 `.so`
├── third/flash-attn/          FlashAttention 上游只读参考子模块
├── third/op_optimization/     沐曦赛事资料与官方示例只读子模块
└── .claude/                   本地 agent/worktree 状态
```

归档类目录只说明到目录层次，不在本手册枚举每一个归档源码。

### 10.1 根目录文件

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | 本手册，后续 agent 的首要入口。 |
| `goal.md` | 可直接交给 goal agent 的长期打榜目标、权限边界和终止条件。 |
| `CLAUDE.md` | 兼容入口，仅引导阅读 `AGENTS.md`，不要重复维护规则。 |
| `problem.md` | 题目语义、ABI、张量布局和 page-table 约束。 |
| `requirement.md` | XPUOJ 评测流程、计分和 CUDA/Triton/TileLang 规则。 |
| `leadboard.md` | 用户复制的排行榜快照，是 `goal.md` 判断前三门槛的唯一榜单来源；不要主动联网刷新，保持现有文件名。 |
| `notes.md` | 临时笔记占位。稳定结论必须写入本手册或结果报告。 |
| `.gitignore` | 忽略凭据、缓存、编译产物和 profiler 生成物。 |
| `.gitmodules` | 声明 `third/flash-attn` 与 `third/op_optimization` 两个只读参考子模块。 |

### 10.2 `solutions/` 与归档

- `solutions/cuda_maca_optimized.cpp`：唯一常用可变优化工作文件。
- `solutions/cuda_maca_version.cpp`：早期 control。
- `solutions/archive/YYYY-MM-DD-submissions/`：按提交号保存的不可变字节精确源码，即使同源复投也各保留一份。
- `solutions/archive/YYYY-MM-DD-experiments/`：失败、未采用或局部验证候选，均视为只读历史记录。
- `solutions/archive/SUBMISSIONS.md`：由脚本生成的 ID、时间、状态、分数、SHA-256、源码和 raw 映射。

### 10.3 `results/`

- `results/cuda_result.md`：全部提交索引、关键 checkpoint、14-case 矩阵、源码归因和接受/拒绝结论。时间使用 UTC+8，同日倒序。
- `results/raw/cuda_<id>_raw.json`：完整 OJ 原始响应，禁止手工改写。

### 10.4 `tests/`

- `c500_case_manifest.py`：权威 case 配置与集中 split/dispatch policy。
- `test_kernel_logic.py`：无 GPU 的 NumPy 语义回归。
- `c500_paged_decode_harness.py`：真实 C500 与 FlashAttention reference correctness。
- `c500_benchmark.py`：真实 C500 交错 control/candidate A/B。
- `.pytest_cache/`、`__pycache__/`：生成缓存，不是结果资产。

### 10.5 `tools/`

- `build_local_maca.sh`：源码→MACA shared object。
- `xpuoj_submit.py`：dry-run、提交、list、watch、monitor、cancel 和 raw 保存；没有 `--submit` 时不会创建提交。
- `archive_cuda_submissions.py`：从 raw 提取每次提交源码并重建 manifest。
- `README.md`：OJ 工具凭据边界和使用说明。
- `.env.example`：可提交模板。
- `.env`：本地真实凭据，禁止读取、打印、修改、提交或写入报告；工具会自动加载。

### 10.6 其他目录

- `log/cuda_compile_log.md`：OJ/MACA 编译诊断，最新记录置顶。
- `build/`：本地 `.so`，文件名不能证明源码身份；可安全重建。
- `third/flash-attn/`：算法和源码参考，不安装、不修改、不作为提交运行依赖；其目录内另有 `AGENTS.md`。
- `third/op_optimization/`：沐曦官方赛事规则、FAQ、教程、task package 和跨算子底层示例；默认读取父仓库固定的 commit，不修改、不构建、不作为提交依赖，使用方法见第 5.5 节。
- `.claude/`：忽略的本地 agent 数据，不保存唯一实验结论。

## 11. 标准迭代、提交和归档流程

1. 从本手册确认当前选定最优提交快照；必要时将它复制到 `solutions/cuda_maca_optimized.cpp`，开始一个单一假设实验。
2. 记录工作源码 SHA-256，编译唯一命名 `.so`。
3. 依次完成 CPU 语义、GPU full、boundary、random、padding trap 和必要的同进程 workspace 复用测试。
4. 对当前选定最优提交快照 control 与工作 candidate 做交错 A/B；先看目标 case ratio，再看其他 case 是否回退。
5. OJ 只用于本地筛选后的 finalist。确认没有其他非终态提交且队列状态正常，再运行 `python3 tools/xpuoj_submit.py solutions/cuda_maca_optimized.cpp` dry-run。只有用户明确要求真实提交时才增加 `--submit`。
6. 一次提交后先等待其进入终态，再保存 `results/raw/cuda_<id>_raw.json`，运行 `python3 tools/archive_cuda_submissions.py`，确认逐提交源码哈希等于 raw 嵌入源码；完成这些步骤前不发起下一次提交。
7. 更新 `results/cuda_result.md`。不能因 aggregate 刷新就自动认定新最优，必须结合目标 case、A/B 和 correctness。
8. 若确认产生新的最优结果，将其不可变逐提交快照选为后续 control，更新本手册与结果报告中的当前最佳提交 ID/路径，并让工作文件在空闲状态同步到新最优；不要再复制一份 best/frozen 源码。
9. 若候选失败，当前选定最优提交指针保持不变；有复现价值的失败源码移入日期化 experiments 目录，普通临时产物可清理。

### 11.1 OJ 提交节流与队列异常

2026-08-09 已观察到多笔提交长时间排队；用户判断短时间大量提交可能导致评测优先级下降。平台调度机制尚无公开证据，不能把“降权”写成已确认事实，但必须按该风险执行保守节流：

- 同一时间最多保留一个非终态提交。OJ 不是参数扫描器；多个 split、threshold、loader 或 schedule 候选必须先在本地批量筛选，只提交少量能回答明确问题的 finalist。
- 不进行“取消后立即重投”、同源码连续复投或为了查看抖动而密集提交。取消只用于已确认提交错误、平台明确要求或用户明确指示；取消本身不证明队列会恢复。
- 出现多个任务持续排队、单笔等待明显异常或平台整体 backlog 时，立即进入 OJ 暂停状态：不再 submit/cancel，也不创建替代提交；继续进行官方文档调研、本地 correctness、资源 probe 和交错 A/B。待已有队列恢复正常终态流转或用户确认平台恢复后再提交。
- 状态查询使用 `watch/monitor` 的合理间隔，不用高频手工轮询轰击接口。查询不会被假定会影响优先级，但同样应减少无意义请求。
- 每次恢复提交前重新检查源码 SHA-256、唯一假设、完整 correctness 和多轮稳定的目标 case A/B。只有新的源码证据或明确诊断价值才消耗一次 OJ 机会；不足以区分噪声的候选继续留在本地。
- 不预设未经平台证实的固定冷却分钟数；以“上一笔已终态并归档、当前无非终态提交、队列流转正常”为下一次提交的最低事件门槛。即使长期 goal 已授权真实提交，也仍必须遵守该门槛。

### 11.2 OJ 暂停期间的本地研究流水线

**OJ 暂停只暂停远端提交，不暂停优化任务，也不能成为等待或空转的理由。** 只要真实 C500、本地编译器和仓库仍可用，就必须继续产生有证据的本地进展：

- 从第 9 节优先级、官方文档的新能力和现有失败边界中选择下一条可证伪假设；可以连续开展多个本地实验，但每个首轮候选仍只改变一个核心因素。
- 优先完成不依赖 OJ 的工作：官方资料和本机头文件核对、未 launch 编译 probe、codegen/寄存器/shared/spill/occupancy 分析、CPU/GPU correctness、边界与 workspace 复用测试、目标及非目标 case 交错 A/B。
- 建立本地候选队列。每个候选至少记录实验 ID、父源码与 SHA-256、唯一差异、目标 case、资源变化、correctness、A/B p10/p50/p90 和接受/拒绝理由；有复现价值的源码或 patch 放入日期化 experiments 归档，不能只留一个不断覆盖的工作文件。
- 根据正确性、收益幅度、稳定性、非目标回退和能否回答关键问题对候选排序。OJ 恢复时不按完成时间逐个补交，只提交排名最高、信息价值明确且再次对当前 control 复验通过的少量 finalist；其余候选继续作为本地证据或直接关闭。
- 一个候选进入长时间 benchmark、correctness 或资源分析时，可以准备和静态审查下一条独立假设，但不得混淆 `.so`、源码哈希或 control/candidate 身份，也不得并发运行会互相污染 C500 性能计时的 GPU benchmark。
- 若某条路线本地失败，立即记录反证并转向下一条路线；不要为了等待 OJ 而反复微调已经落入噪声或已关闭的参数。队列异常本身不满足任务 blocked 条件，只有本地 GPU、编译器或其他必要资源也持续不可用且安全替代工作已经穷尽时，才可能构成外部阻塞。

## 12. 安全与维护约束

- 不修改 `results/raw/` 和 `archive/*-submissions/` 的历史事实；不一致时修复提取或报告流程。
- 不修改当前最佳或任何其他逐提交快照；日常变化只进入 `solutions/cuda_maca_optimized.cpp`。
- 不提交 `tools/.env`、API token、密码、本地 `.so`、Python cache、profiler 数据库或 `profiler.log`。
- 不修改或构建 `third/flash-attn`、`third/op_optimization`，除非用户明确把对应子模块本身纳入任务；只读 fetch 不等于授权移动父仓库的 submodule pin。
- 不删除失败实验的唯一证据；先确认 raw、逐提交快照或 experiments 中仍有可复现副本。
- 工作树可能包含用户的并行修改。只改任务要求的文件，不重置、不覆盖无关变化。
