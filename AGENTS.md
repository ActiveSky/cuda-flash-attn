# MetaX C500 FlashAttention 优化手册

本仓库用于优化 XPUOJ Contest 11 的 FlashAttention paged KV-cache decode CUDA/MACA 实现。本文件是后续 agent 的首要入口，集中记录文件组织、真值来源、验证闭环、已经证实的优化方向、失败路线和接续流程。

## 1. 当前状态与源码角色

当前真实 OJ 最高分为 **`57.43`**：#105915 首次达到，#105932/#105952 保持；当前选定最优提交为 **#105952**。

| 路径 | 角色 | 修改规则 |
|---|---|---|
| `solutions/archive/2026-08-08-submissions/cuda_105952.cpp` | **当前选定最优提交的不可变源码**，同时作为新实验的默认 control。它已由 raw 字节精确提取，不再额外维护“当前最佳”副本。 | 永远不修改；新最优出现后保留本文件作为历史事实，并把本文的当前最佳指针改到新提交快照。 |
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

下表来自 #105952 raw，耗时单位为 `μs`。历史最佳只统计整次 14/14 Accepted 的提交；它们分散在不同源码中，不能直接拼接并假定同时成立。

| Case | Shape | #105952 | 分数 | Accepted 历史最佳 |
|---:|---|---:|---:|---|
| 1 | B1 / L1 / KV4 / edge | 3 | 92 | 3（#105899 等） |
| 2 | B4 / L2 / KV8 / edge | 4 | 90 | 4（#105899 等） |
| 3 | B16 / L17 / KV4 / edge | 10 | 82 | 10（#105915 等） |
| 4 | B64 / L64 / KV8 | 30 | 66 | 29（#105814/#105915） |
| 5 | B16 / L141 / KV4 | 26 | 63 | 25（#105932） |
| 6 | B16 / L362 / KV8 | 33 | 59 | 33（多次） |
| 7 | B64 / L2048 / KV8 | 322 | 46 | 320（#105899） |
| 8 | B16 / L4096 / KV4 | 175 | 38 | 174（多次） |
| 9 | B32 / L4096 / KV8 | 321 | 49 | 321（#105915/#105952） |
| 10 | B1 / L8192 / KV4 | 58 | 52 | 57（#105801） |
| 11 | B16 / L12251 / KV4 | 448 | 35 | 439（#105835） |
| 12 | B8 / L32768 / KV8 | 533 | 51 | 533（#105823/#105899/#105952） |
| 13 | B1 / L58966 / KV8 | 294 | 45 | 294（多次） |
| 14 | B1 / L61519 / KV4 | 297 | 36 | 296（#105801） |

108 份现有 raw 的状态统计为：95 Accepted、9 WrongAnswer、4 CompilationError。最新 #105561–#105952 的 20 次连续优化全部 14/14 Accepted。

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
  solutions/archive/2026-08-08-submissions/cuda_105952.cpp \
  build/cuda_105952_control.so
python3 tests/c500_benchmark.py \
  --control build/cuda_105952_control.so \
  --candidate build/cuda_maca_optimized.so \
  --cases 7,9,12,13 --warmup 5 --iterations 20 --rounds 9
```

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
- case 11 的 Q shared-memory 复用曾把目标时延降到 439 μs，值得在完整候选中继续稳定复现。

注意：旧 paired-QK 中单纯复制 full-page predicate-free 分支是负优化；#105762 的正收益来自 token-parallel 循环、KV4 Q staging、full/tail 资源布局的组合，不能把两次实验混为一谈。

## 8. 已证伪或不得无假设重试的方向

正确性/后端风险：

- lane-dependent cross-subgroup shuffle：大范围 WrongAnswer；只使用已验证的 32-lane `0xffffffffu` shuffle mask，不盲改 64-bit mask。
- 8-lane/quad-token subgroup：超时式 WrongAnswer；16-lane subgroup 是当前最小安全粒度。
- raw 128-thread/two-wave WMMA：长 KV4 约 36 秒失败占位后 WrongAnswer。
- native packed BF16 conversion：目标 KV8 超时式 WrongAnswer；其他平台编译通过不代表 MACA 可用。
- forced CUTE four-wave QK/PV、V staging 扩展：长 case WrongAnswer。只编译未 launch 的 probe 不构成 runtime 证据。
- direct-out 跨类型别名写：曾出现输出未正确写入。
- 本地 C500 上历史 MMA-QK dispatch 对完整 KV4 paged input 无法稳定满足 OJ tolerance，当前生产 dispatch 保持关闭。

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
- 无依据地过度或不足 split。

CompilationError、WrongAnswer 和约 36 秒失败占位时间不是 kernel 性能数据，不得用于计算 speedup。

## 9. 当前瓶颈与后续优先级

当前最值得投入的顺序：

1. **长 KV4 case 11/14/8**：最终分数分别只有 35/36/38；优先调查 occupancy、Q staging、reducer 和 loader，避免重新启用未经正确性证明的 MMA。
2. **长 KV8 case 7/9/12/13**：token-parallel 计算布局已有效，下一步主要减少 launch、tail、shared-state 和 reducer 开销，长 KV8 继续以同步 `uint4` 为 control。
3. **距离 tier 仅约 1 μs 的 case 4/5/10/14**：局部 patch 必须在同一最终源码中验证，不能直接拼接不同提交的历史最佳。
4. **case 11 已验证局部路径**：把 #105835 的 439 μs Q-reuse 思路移植到当前完整候选，检查资源阈值和其他 case 是否受影响。

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
├── third/flash-attn/          上游只读参考子模块
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
| `.gitmodules` | 声明 `third/flash-attn` 子模块。 |

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
- `.claude/`：忽略的本地 agent 数据，不保存唯一实验结论。

## 11. 标准迭代、提交和归档流程

1. 从本手册确认当前选定最优提交快照；必要时将它复制到 `solutions/cuda_maca_optimized.cpp`，开始一个单一假设实验。
2. 记录工作源码 SHA-256，编译唯一命名 `.so`。
3. 依次完成 CPU 语义、GPU full、boundary、random、padding trap 和必要的同进程 workspace 复用测试。
4. 对当前选定最优提交快照 control 与工作 candidate 做交错 A/B；先看目标 case ratio，再看其他 case 是否回退。
5. 提交前运行 `python3 tools/xpuoj_submit.py solutions/cuda_maca_optimized.cpp` dry-run。只有用户明确要求真实提交时才增加 `--submit`。
6. 保存 `results/raw/cuda_<id>_raw.json`，运行 `python3 tools/archive_cuda_submissions.py`，确认逐提交源码哈希等于 raw 嵌入源码。
7. 更新 `results/cuda_result.md`。不能因 aggregate 刷新就自动认定新最优，必须结合目标 case、A/B 和 correctness。
8. 若确认产生新的最优结果，将其不可变逐提交快照选为后续 control，更新本手册与结果报告中的当前最佳提交 ID/路径，并让工作文件在空闲状态同步到新最优；不要再复制一份 best/frozen 源码。
9. 若候选失败，当前选定最优提交指针保持不变；有复现价值的失败源码移入日期化 experiments 目录，普通临时产物可清理。

## 12. 安全与维护约束

- 不修改 `results/raw/` 和 `archive/*-submissions/` 的历史事实；不一致时修复提取或报告流程。
- 不修改当前最佳或任何其他逐提交快照；日常变化只进入 `solutions/cuda_maca_optimized.cpp`。
- 不提交 `tools/.env`、API token、密码、本地 `.so`、Python cache、profiler 数据库或 `profiler.log`。
- 不修改或构建 `third/flash-attn`，除非用户明确把子模块本身纳入任务。
- 不删除失败实验的唯一证据；先确认 raw、逐提交快照或 experiments 中仍有可复现副本。
- 工作树可能包含用户的并行修改。只改任务要求的文件，不重置、不覆盖无关变化。
