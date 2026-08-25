# exp657 short-row owner shape audit（只读源码/历史审计）

日期：2026-08-24  
父 control：`#113889 / exp559`，SHA-256 `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`  
审计候选：`solutions/archive/2026-08-24-experiments/cuda_case6_separate_shortrow_owner_exp657.cpp`，SHA-256 `b658d566d67a9822dcf8256eece1666c61f9f63858bb6bc5e0b348254aa0befc`

本记录只做源码和历史审计；没有修改源码、工作文件或共享记录，没有运行 C500、benchmark 或 OJ。

## 结论

`case5` 是 exp657 机制唯一值得登记的自然延伸；case4 和 case10 不形成合格的独立合同。

### 形状事实

| case | OJ shape | control split / pages-per-split | `live_splits==1` 的实际长度 | 审计结论 |
|---|---|---:|---:|---|
| 4 | B64/KV8/L64 | 1 / 4 | 1–64 | 已是 `CASE4_DEDICATED` 单 CTA direct-output，没有 producer→partial→reducer 往返可删除；额外 owner 只是重复/替换同一工作。 |
| 5 | B16/KV4/L141 | 5 / 2 | 1–32 | 有 16 条 batch row，且短 row 恰好只写 split0；可由独立 `(batch,kv_head)` owner 完成 attention/output，同时让原 producer 和 group8 reducer 对同一 row 早退。 |
| 10 | B1/KV4/L8192 | 128 / 4 | 1–64 | 虽然存在 single-live 区间，但 B1 每次调用只有一个 row；owner launch 的固定成本无法由 batch 内短 row 摊销。历史上 B1 KV4 的额外 tail launch 已稳定回退。 |

上述 split/page 数与 OJ manifest 的 `split_policy` 一致（`tests/c500_case_manifest.py:127-140`）。exp657 当前 owner 已证明的结构是：独立 `(b,kv_head)` launch（源码 `:1215-1225`、`:5575-5584`），普通 producer 在任何 Q/shared/partial 工作前按真实 `cache_seqlens` 早退（`:1513-1519`），group8 reducer 在读取 partial 前早退（`:5136-5141`）。

## 唯一可登记合同：exp657-case5-separate-short-owner

### target 与机制

- 唯一 target：case5，B16/KV4/L141，control 为约 `17 us / 73 分`。
- 只处理真实 `0 < cache_seqlens[b] <= 32` 的 row；`seqlen==0` 保持 control 的 zero-output 路径，`33..141` 完全保持 control producer→partial→group8 reducer ABI。
- 新增一个独立 `case5_short_owner` kernel，grid 固定为 `tail_grid = (batch_size * KV_HEADS, 1) = (64,1)`，block 采用现有 case5 的 `(16,4,4)` z4/head-pair 几何。每个 CTA 独占一个 `(b,kv_head)`，按真实前 `ceil(seqlen/16)` 个 page 做 FP32 online-softmax/PV，完成 z-state 合并后直接写 8 个 GQA query-head 的 BF16 output。
- 同一 default stream 中，case5 普通 producer 对 `1..32` 在 Q/shared staging 前返回；case5 group8 reducer 在读取任意 partial 前返回。这样短 row 不写、不读 workspace，独立 owner 是唯一 output owner；长 row和 zero row仍由旧路径负责。

### 必须改变的源码位置

1. 在 `paged_decode_case11_headpair_z4_kernel` 的模板/入口（当前 `:3382-3499`）增加 case5 专用 short-owner skip 开关，并把 guard 放在 shared staging 和 partial 写入之前；不得把 direct output 代码编译进普通 case5 producer 的实例。
2. 在当前 case5 dispatch（`:5755-5769`）启用该 producer skip 实例，并在其前面增加独立 `case5_short_owner` launch。启用条件必须只绑定 `num_heads_k==4 && batch_size==16 && seqlen_k==141`。
3. 在 `paged_decode_reduce_group8_kernel` 的最后模板参数（当前 `:5111-5117`）使用通用 short-owner skip 语义；当前 case5 reducer dispatch（`:6072-6080`）启用它。case6 现有 skip 语义不得被改变。
4. owner 的 page loader/PV 必须沿用 case5 的 KV4/GQA8、真实 `block_table` 页范围和 tail mask；不能把 KV8/GQA4 的 exp657 映射或 case4 的 `CASE4_DEDICATED` 直接套用。

这不是 split、threshold、lane、template 或 launch 参数扫描：核心差异是短 row 的 producer/partial/reducer ownership 从既有三段式路径迁移到一个物理独立的 direct-output consumer，且只在天然 single-live 的 case5 合同生效。

### 与旧反证的 changed-precondition

- `exp591` 已覆盖同一 case5、同一 `1..32` single-live 范围，但把 direct BF16 output 编译进普通 z4 producer，并让 group8 reducer early-return；producer 为 `74/52`，reducer 由 control `66/26/7 waves` 退化为 `62/28/8 waves`，因此 resource gate 失败（`notes.md:3650-3654`）。本合同把 direct conversion/store 移到独立 owner，普通 producer/reducer 不生成该 live range；这是实质的物理 owner/编译实例变化，不是 exp591 的 store 或模板微调重试。
- `exp590` 的 case6 producer 内嵌 direct-output 同样因普通 producer 资源增加而关闭（`notes.md:3644-3648`）；它否定的是 producer 内嵌前提，不否定独立 owner。
- `exp592` 已证明独立 owner 的固定额外 launch 是真实风险：case7 每次调用约增加 `3.2–3.6 us`，本地 full/random/boundary 均重复回退，后续 OJ `#124170` 为 `276 us / 50 分`，低于 control 的 `226 us / 55 分`（`notes.md:3662-3670`、`results/cuda_result.md:105-108`）。这关闭的是 case7 的 exact B64/KV8/43-page owner 合同，不能把 case5 的 B16/KV4/two-page owner 当作已被同一 shape 反证；但它使本合同必须把固定 launch 风险列为线上主要可证伪点，不得宣称本地一定获益。
- case4 已经是单 CTA direct-output（当前 dispatch `:5914-5932`），没有 producer/reducer round trip；case10 的 B1/KV4 launch/latency-bound 反证明确记录在 `notes.md:63`，且其 single-live owner launch 即使 row 非短也会发射。两者没有与 exp657 相同的“多 row short owner 可摊销固定 launch + skip partial consumer”前提。

### 最低 correctness 风险集

实现后、在任何 OJ probe 前至少需要针对同一 candidate binary 检查：

- case5 exact lengths：`0, 1, 2, 15, 16, 17, 31, 32, 33, 47, 48, 63, 64, 65, 127, 128, 129, 140, 141`；其中 `32→33` 是 owner/普通 producer 的 live-split 分界，`15/16/17` 和各页尾用于 tail mask。
- B16 mixed batch：同时放入 zero、`1..32` short-owner、`33..141` multi-split 长 row；确认 owner 与普通 producer/reducer 不互相读取或覆盖 workspace。
- 对 short tail token 及 block-table padding page 做 NaN/poison；candidate/reference 必须 finite 且满足既有容差，不能读取 `cache_seqlens[b]` 之外的 page/token。
- output guards、Q/K/V、`cache_seqlens`、`block_table` 不变；确认 GQA8 head 映射、FP32 online-softmax/LSE、BF16 output 和 `seqlen==0` zero-output 语义。
- 同进程 `141→1→141`、`1→141`、`141→0→141` workspace reuse，并重复 full output 确定性检查；短 row 不能读旧 partial，长 row 不能被上一轮 owner 输出污染。
- 静态上确认独立 owner 已注册且普通 case5 producer/reducer 没有 direct-output 分支；至少无明显 spill/stack/非法 launch 风险。资源或本地 timing 的中性/回退按当前 OJ-first 规则不单独否决探索 probe，但 correctness/越界/未初始化问题必须阻止提交。

### 线上唯一成功判据

预注册一次、仅一次 case5 目标 probe：`14/14 Accepted`，且 case5 从 control 的 `17 us / 73 分` 跨到约 `<=16 us / >=74 分`。其它 case、aggregate 或未覆盖 timing 不能归因；未达到该 target tier 即关闭该 exact case5 independent-short-owner contract，不扫描 short threshold、store、lane、template、grid 或同源码复投。

## 最终审计判定

`CASE5 NATURAL EXTENSION — AUDIT ONLY / NOT IMPLEMENTED`。它是唯一同时满足“天然 single-live page contract、可删除普通 partial consumer、B16 batch 内存在可摊销的短 row、且旧失败可由物理 owner changed-precondition 区分”的候选。case4/10 不登记；exp592 的固定 launch OJ 风险必须由 case5 的一次串行 OJ probe 直接裁决。
