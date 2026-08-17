# C500 测试资产说明

`tests/` 根层只保留长期回归和仍能支撑下一阶段假设的 active probe。已经完成能力判定、且在相同前提下不应继续扫描的一次性 probe 进入 `archive/closed-backend-probes/`。归档表示“结论已闭合”，不表示证据可以删除。

## 长期回归

| 文件 | 作用 | 状态与使用边界 |
|---|---|---|
| `c500_case_manifest.py` | 从当前结构性 control #113696 的 Accepted raw 解析 14 个权威 shape，并镜像当前 split 数和 producer family。 | **持续使用**。control 的 dispatch/split 改变时必须同步；不把 `problem.md` 的静态表当 shape 真值。 |
| `test_kernel_logic.py` | 用 NumPy 重放 paged lookup、GQA、split partial、online softmax 和 reducer 数学。 | **持续使用**。验证数学契约，不等价于真实 MACA 指令、资源或竞态验证；历史 MMA/PV 模型只在 `--extended-candidates` 下运行。 |
| `c500_paged_decode_harness.py` | 通过题目 ABI 加载 `.so`，与系统 FlashAttention reference 比较，支持 full/boundary/random 和同进程 exact-length 序列。 | **持续使用**。负责 padding-page trap、finite/tolerance、split 边界及 workspace 复用门禁；长 case 被系统 Kill 时拆成单 case，不得记为通过。 |
| `c500_benchmark.py` | control/candidate 紧邻、交替顺序的真实 C500 A/B，报告每轮 ratio p10/p50/p90。 | **持续使用**。改变 split/ownership/调度时分别跑 full/random/boundary；`--skip-correctness` 只供故意错误输出的 phase-ablation 上界探针，结果不可提交。 |

## Active backend probes

下列 `.cpp/.py` 成对使用，均不是可提交 solution：

| 文件族 | 已知能力 | 下一阶段用途 |
|---|---|---|
| `c500_bpermute_probe.*` | 验证 C500 row-local/cross-row BSM bpermute 与已用 shuffle mode 的逐 lane 语义和 codegen。 | ownership/shuffle 网络或 BSM 数据交换前提变化时复核；结论只覆盖 probe 已测 mode/offset。 |
| `c500_bsm_token_wait_probe.*` | 验证 token-returning BSM load 与 scope-0 `barrier_and_wait4` 的 use-def 语义。 | P2：为当前 z8 数据流的有序 token-BSM 流水提供能力门禁；独立 probe 通过不代表任意多请求顺序安全。 |
| `c500_bsm_dual_token_pipeline_probe.*` | 验证 K-current 完成后、V-current 仍在飞行时安全发布 K-next，并在 V-current 完成后回收 V buffer 发布 V-next。 | 多请求深度的能力门禁；只有该交错复用通过，才可设计不同于 exp454 的 K/V 双 token page pipeline。 |
| `c500_async_register_gld_probe.*` | 验证官方 MCTLASS `__builtin_mxc_load_global_async128` 在 `arrive(64)` + barrier 后的 register payload 语义。 | 为 exp479 的 async-register lookahead 建立独立同步/lifetime前提；只有64与256线程 probe 都正确才可设计不同于旧无等待布局的 production candidate。 |
| `c500_split_head_native_probe.*` | 验证 split-head 全原生 `mov.shfl` 网络、head ownership 与旧混合网络等价。 | 当前 bit1/bit2 ownership 的回归和新 fragment/ownership 映射验证；不得外推未测 shuffle mode。 |
| `c500_cooperative_phase_probe.*` | 查询 cooperative launch、精确 #111918 case13 z8 producer 的 runtime occupancy，并在该 producer 可全驻留时验证最小 `grid.sync()` phase 语义和单 barrier 相对当前 case13 reducer launch 的成本。 | P2-2 能力门禁；不足 520 个 resident blocks 时明确关闭，不改 solution、不测 barrier 成本或 OJ。 |

典型运行方式：

```bash
tools/build_local_maca.sh \
  tests/c500_bf16_mma_qk_resource_probe.cpp \
  build/c500_bf16_mma_qk_resource_probe.so
python3 tests/c500_bf16_mma_qk_resource_probe.py \
  --library build/c500_bf16_mma_qk_resource_probe.so
```

## 历史 probe 归档

`archive/closed-backend-probes/` 保存以下已经闭合的证据族：

- BF16/FP16/FP32/INT8 MMA 映射、精度和旧集成：确认了哪些指令/fragment 可用，也确认完整 score tile、KV8 z8 BF16 MMA、BF16 P×V、FP32 runtime 和 INT8 量化集成在已测数据流下不成立。
- `c500_bf16_mma_qk_resource_probe.*`：12个scale/seed均确认填充A fragment后`c[2]/c[3]`仍为零；当前lane-local BF16 MMA不具备额外score密度，除非硬件或fragment ownership实质改变，不重开。
- `c500_case13_head4_x32_resource_probe.cpp`：`(32,1,8)`、每线程四头×四维的资源模型可达`80/22/8448 B/0 stack/6 waves`，但对应完整 exp567 producer 的 full/random/boundary 均明显回退；资源通过不代表这个四头/32-lane QK ownership 有性能前景，不再以 x、shuffle 或 load 拼写扫描重开。
- `c500_lazy_page_guard_probe.*`：确认固定row/full-wave vote语义，但exp449–452已夹定当前case14 fixed15 guard、single-LSE和`+8`状态流；不以mask或阈值变体重跑。
- `c500_ldcs_probe.*`：确认`__ldcs/__ldlu`对`uint4`的payload正确，却在xcore1000 LLVM中同样变成带`nontemporal/l2rp` metadata的四个标量load；没有独立async/prefetch语义或两种cache-policy差异，不能只改loader拼写重开。
- `c500_readlane_wave64_probe.*`：在z8精确 `(16,2,8)` CTA 中，`readlane(lane^32)`把同一physical wave的lane32值广播给整条wave，而非让每lane取自己的`lane^32` peer；它只支持uniform source-lane broadcast，不能替代 raw BSM bpermute 的cross-half XOR。
- `c500_wave64_i32_broadcast_probe.*`：验证 raw BSM 的固定lane0 int32 wave64广播在精确z8几何中语义正确；其唯一 production 候选 exp554 已由#113736显示case12 `373→376 μs`而关闭。不得扫描source lane、broadcast宽度、load时点或覆盖范围；保留证据，后续仅能以不同 primitive 的 readlane backend 重新提出独立假设。
- `c500_readlane_uniform_i32_probe.*`：验证官方 `readlane` 在精确 z8 `(16,2,8)` 几何内能从每个物理64-lane wave 的固定lane0广播 raw int32 payload，且四条wave彼此隔离。其唯一 production 候选 exp555 已由#113750显示case12 `373→374 μs`、仍60分而关闭；不得扫描source lane、broadcast宽度、load时点、模板/grid或同源码复投。只有producer/consumer ownership、页面数据流或后端能力实质改变时才能以新的 probe 重开。
- `c500_permuted_smem_probe.*`：普通128-bit LDS 下的官方 k128B XOR-permuted layout 在32/64 active-thread 双区域 payload 中逐字正确；driver 必须使用一维 raw input backing storage，避免 C500 bridge 对多维 int32 输入的分量布局干扰。完整32次时钟采样的consumer p50为32-thread `1.0001`、64-thread `1.0466`（swizzled/row-major），没有共同正向，故不接入当前KV8 consumer或提交OJ。
- `c500_cooperative_phase_resource_probe.py` 与 `c500_cooperative_persistent_resource_probe.py`：exp456确认cooperative endpoint不降5-block residency，exp457进一步确认完整520-CTA phase/reducer数值正确；但full/random/boundary均回退，关闭当前single-request case13 cooperative persistent布局，不以reducer block、wave barrier或launch拼写重试。
- packed dot/FMA、byte cast 与 BF16 unpack codegen：确认 xcore1000 缺少所需 fdot/pk-FMA feature，byte-cast 不是 BF16 解包，纯 unpack 表达式改写没有生产收益。
- raw/update/pair shuffle 与 z-group barrier：确认原语语义和数据宽度，但对应生产替换中性、回退或资源不合格。
- legacy-body 与 block-accum 诊断：修正了早期 BF16 MMA “精度墙”误诊，同时关闭旧完整 Attention body 的资源/性能布局。

详细实验数字、SHA、反证和 changed-precondition 见根目录 `notes.md`。除非编译器、目标架构、线程布局、fragment ownership、状态契约或流水前提发生明确变化，不把归档 probe 移回根层，也不在原前提下重复运行。

## 维护规则

1. 新 probe 必须回答一个可证伪问题，文件名包含能力或数据流，不以临时编号替代含义。
2. probe 结论写入 `notes.md`，并绑定源码 SHA、构建产物和真实 C500 输出；`build/` 文件名不能证明身份。
3. 能直接支撑当前实验队列的 probe 留在根层；结论闭合后连同 companion driver 一起归档，并修复 Markdown 引用。
4. 核心回归不得被一次性 probe 替代。任何 production finalist 仍须经过 CPU、GPU 三分布、精确边界、workspace 复用和交错 A/B。
