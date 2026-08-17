# 2026-08-10 实验源码清单

本目录只保存可直接阅读、比较和编译的完整 `.cpp` 候选源码，不使用 `.patch/.diff` 作为唯一归档。详细假设、correctness、资源用量和交错 A/B 数据见仓库根目录的 [`notes.md`](../../../notes.md)。

| 实验 | 完整源码 | 父源码（SHA-256） | 候选 SHA-256 | 状态 |
|---|---|---|---|---|
| exp117 | [`cuda_case14_independent_z_exp117.cpp`](cuda_case14_independent_z_exp117.cpp) | exp115 (`b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`) | `783a1af158db38a211d25a436c4d087782652ecdfbca15fa07d1ed1c80d7557c` | rejected（case14 消偏约慢 6.71%） |
| exp118 | [`cuda_case14_independent_z_split129_exp118.cpp`](cuda_case14_independent_z_split129_exp118.cpp) | exp117 (`783a1af158db38a211d25a436c4d087782652ecdfbca15fa07d1ed1c80d7557c`) | `f324ac23590f1b22777cc5160245a1ce5e72cd258ad9b111d18a72ac64abf5da` | rejected（case14 消偏约慢 3.72%） |
| exp119 | [`cuda_case14_independent_z_split86_exp119.cpp`](cuda_case14_independent_z_split86_exp119.cpp) | exp118 (`f324ac23590f1b22777cc5160245a1ce5e72cd258ad9b111d18a72ac64abf5da`) | `c10c0acee426cf831a9766c66d2c5d14ee2cc1297632e9d9e0b9922447298795` | rejected（case14 消偏约慢 19.59%，关闭 family） |
| exp120 | [`cuda_case14_register_lookahead_exp120.cpp`](cuda_case14_register_lookahead_exp120.cpp) | exp115 (`b73fb54d9457d7bf2d02649a33a394669af965a9956b34ae57d46f68017e02d6`) | `e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332` | positive，已被exp124b取代（case14 消偏约快 5.05%） |
| exp121 | [`cuda_case14_early_pid_exp121.cpp`](cuda_case14_early_pid_exp121.cpp) | exp120 (`e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`) | `ccc58a6ecc9262a5e6a38a958ea57b5ce4d9ff46f5046e2f76ea6f5019ea295c` | rejected（case14 消偏约慢 1.36%） |
| exp122 | [`cuda_case14_initial_barrier_fusion_exp122.cpp`](cuda_case14_initial_barrier_fusion_exp122.cpp) | exp120 (`e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`) | `ad72414094d768f79f26b0701bce559d5b5271f68f3c1ffae3368a3ebcae772c` | neutral/rejected（case14 消偏约慢 0.25%） |
| exp123 | [`cuda_case14_stagger_v_exp123.cpp`](cuda_case14_stagger_v_exp123.cpp) | exp120 (`e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`) | `3e85bd766f1987bfabea8ed62c5644ea2ca303a160f607799653c0ce1d992c59` | rejected（case14 消偏约慢 2.63%） |
| exp124 | [`cuda_case10_full_fused_tail_exp124.cpp`](cuda_case10_full_fused_tail_exp124.cpp) | exp120 (`e173303359fcee1040b8db3e86d56cc42df4fa5d721dde3952ee343e49e38332`) | `35a6a16478e0e061e8c26f7f50be1f66f4fa85a0542c189e23c3bf0f12a76cc3` | correctness incomplete（65/129/193 split模数错误） |
| exp124b | [`cuda_case10_full_fused_tail_exp124b.cpp`](cuda_case10_full_fused_tail_exp124b.cpp) | exp124 (`35a6a16478e0e061e8c26f7f50be1f66f4fa85a0542c189e23c3bf0f12a76cc3`) | `f98112aa776b2cf80ecdb3880baa402475a4db4a07c8a4ce8518398caa50d016` | positive，已被exp125取代（case10 消偏约快 0.71%） |
| exp125 | [`cuda_case10_register_lookahead_exp125.cpp`](cuda_case10_register_lookahead_exp125.cpp) | exp124b (`f98112aa776b2cf80ecdb3880baa402475a4db4a07c8a4ce8518398caa50d016`) | `e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0` | positive，OJ #107856 因长期Pending取消，已被exp130取代（case10快约3.29%） |
| exp126 | [`cuda_case5_full_fused_tail_exp126.cpp`](cuda_case5_full_fused_tail_exp126.cpp) | exp125 (`e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`) | `6a5b9115819bc439fc9e814d94fae1c3bcc9e2f87280b4ee06bab087f38bbfb3` | rejected（case5 慢约 14.52%，tail融合拉长critical split） |
| exp127 | [`cuda_case5_combined_register_lookahead_exp127.cpp`](cuda_case5_combined_register_lookahead_exp127.cpp) | exp125 (`e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`) | `477a4424da53cf728f32f37707c1af8fdd558fc3ffbf4452c0d9107ca62780f4` | rejected（case5 双顺序消偏约慢 1.61%） |
| exp128 | [`cuda_case10_initial_barrier_fusion_exp128.cpp`](cuda_case10_initial_barrier_fusion_exp128.cpp) | exp125 (`e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`) | `414ccc67bc66407aaf2fcaa4ac841bff955744412aff69a48e2348afea07b5a8` | neutral/rejected（case10 双顺序消偏约慢 0.29%） |
| exp129 | [`cuda_case10_split64_register_lookahead_exp129.cpp`](cuda_case10_split64_register_lookahead_exp129.cpp) | exp125 (`e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`) | `1e84ef239ba4dca8154289fe6b86574e36cd09cd1eb2800f630dfb574799dc14` | rejected（case10 8 pages/split 慢约 5.59%） |
| exp130 | [`cuda_case12_scalar_k_lookahead_exp130.cpp`](cuda_case12_scalar_k_lookahead_exp130.cpp) | exp125 (`e84f0a38ca930d4e2bde36f6cdc9b83e88ce45059b607e520d895a922d423aa0`) | `4115934ebfe577f829f8aff21750c20cc79b057d3f25ae00a6f6122c6c88581d` | positive，已被exp131本地主链取代（case12 双顺序消偏约快 1.87%） |
| exp131 | [`cuda_case13_scalar_k_lookahead_exp131.cpp`](cuda_case13_scalar_k_lookahead_exp131.cpp) | exp130 (`4115934ebfe577f829f8aff21750c20cc79b057d3f25ae00a6f6122c6c88581d`) | `2dfd46488ce6b050859ac32328db58c347471a38112acc2e095260b6f145dfd7` | positive，OJ #107882 Canceled，已被exp132取代（case13 双顺序消偏约快 2.23%） |
| exp132 | [`cuda_case9_scalar_k_lookahead_exp132.cpp`](cuda_case9_scalar_k_lookahead_exp132.cpp) | exp131 (`2dfd46488ce6b050859ac32328db58c347471a38112acc2e095260b6f145dfd7`) | `357ce23cb09d9d71fa45f6385e223b0c93269d5b20f6ca0c7bd27ba716a0a057` | positive，已被exp133本地主链取代（case9 双顺序消偏约快 1.39%） |
| exp133 | [`cuda_case7_scalar_k_lookahead_exp133.cpp`](cuda_case7_scalar_k_lookahead_exp133.cpp) | exp132 (`357ce23cb09d9d71fa45f6385e223b0c93269d5b20f6ca0c7bd27ba716a0a057`) | `9f611f4dd92b0d73d173b9fbb08c580ab5c5c85efc54acf679694102a44bd754` | positive，已被exp134本地主链取代（case7 双顺序消偏约快 1.44%） |
| exp134 | [`cuda_case13_scalar_kv_lookahead_exp134.cpp`](cuda_case13_scalar_kv_lookahead_exp134.cpp) | exp133 (`9f611f4dd92b0d73d173b9fbb08c580ab5c5c85efc54acf679694102a44bd754`) | `b3ba2b89f707ee960f5df1198e32eefa133a6bd920b951a7728f693ce7c4a045` | positive，已被exp135/#108312取代；OJ #108257/#108278 compile TLE（case13 V-over-PV双顺序消偏约快2.28%） |
| exp135 | [`cuda_compile_surface_prune_exp135.cpp`](cuda_compile_surface_prune_exp135.cpp) | exp134 (`b3ba2b89f707ee960f5df1198e32eefa133a6bd920b951a7728f693ce7c4a045`) | `234af15ed3f75fb939e3a2392ba4d377b4644a8595887a9e948a822ce88c12a9` | confirmed，#108312首次达到59.86，后由#108468取代为control（排除未启用CUTE/MMA编译表面，运行A/B中性） |
| exp136 | [`cuda_case12_scalar_kv_lookahead_exp136.cpp`](cuda_case12_scalar_kv_lookahead_exp136.cpp) | exp135/#108312 (`234af15ed3f75fb939e3a2392ba4d377b4644a8595887a9e948a822ce88c12a9`) | `4df13ff63446190b7dec7482cf2479fd05e83956a5897f58b95bd1f1994382c5` | positive，case12 K+V消偏约快1.16%；OJ #108371/#108398 Canceled，组合改动由#108468确认 |
| exp137 | [`cuda_case9_scalar_kv_lookahead_exp137.cpp`](cuda_case9_scalar_kv_lookahead_exp137.cpp) | exp136 (`4df13ff63446190b7dec7482cf2479fd05e83956a5897f58b95bd1f1994382c5`) | `6bec5e024eee31ef981d14d4efb5ec8ce8a6e6cf9a11122dc0363d922de9be0e` | positive，已被exp138本地主链取代（case9消偏约快1.53%） |
| exp138 | [`cuda_case7_scalar_kv_lookahead_exp138.cpp`](cuda_case7_scalar_kv_lookahead_exp138.cpp) | exp137 (`6bec5e024eee31ef981d14d4efb5ec8ce8a6e6cf9a11122dc0363d922de9be0e`) | `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946` | confirmed，#108468 / 59.86，后由exp147/#108604取代（case7消偏约快1.47%，四个长KV8 K+V扩展闭合） |
| exp139 | [`cuda_case11_pairwise_partial_exp139.cpp`](cuda_case11_pairwise_partial_exp139.cpp) | exp138 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `00299b7076ff3f38f89b884394f03549ad7834102779bc2b90478e060344e520` | rejected（case11两partial/owner消偏约慢0.84%） |
| exp140 | [`cuda_case11_scalar_kv_lookahead_exp140.cpp`](cuda_case11_scalar_kv_lookahead_exp140.cpp) | exp138 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `3a8383adebdff9ca66f520c4da5642ab9a8af7c246c92d3268e6da6216720701` | rejected（case11 K/V lookahead标量化消偏约慢0.60%） |
| exp142 | [`cuda_case14_register_z0_exp142.cpp`](cuda_case14_register_z0_exp142.cpp) | exp138/#108468 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `c00494568735e2d73a6ae7146b3827a2eae5f3f701a36efb3705d4a721bd5e8b` | rejected（case14 z0寄存器保留，shared `8320→8192 B`但STreg `56→58`，双顺序消偏约慢0.18%） |
| exp143 | [`cuda_case8_pair2_vec4_reducer_exp143.cpp`](cuda_case8_pair2_vec4_reducer_exp143.cpp) | exp138/#108468 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `b5fe8d7d29a4c99047b9ef217886915a98ce76c47e4582e99a5ad8c34df7ece1` | neutral/rejected（case8双head/64-thread vec4 reducer消偏约快0.07%，区间跨1） |
| exp144 | [`cuda_case4_register_z0_exp144.cpp`](cuda_case4_register_z0_exp144.cpp) | exp138/#108468 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `330caba578869aba1c70eabe8692106e826ad562a21a7ee91d9117712012f372` | rejected（case4 register-z0 shared少128 B但双顺序消偏慢约1.54%） |
| exp145 | [`cuda_case4_kv8_headpair_bsm_exp145.cpp`](cuda_case4_kv8_headpair_bsm_exp145.cpp) | exp138/#108468 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `957aa06800eece598283f33c5afe20427c8fd2ce5b3864d56bf2d07a60b1b1b4` | correctness rejected（128-thread KV8双-head中每线程双BSM load导致大范围NaN） |
| exp146 | [`cuda_case4_kv8_headpair_sync_exp146.cpp`](cuda_case4_kv8_headpair_sync_exp146.cpp) | exp145/#108468 (`957aa06800eece598283f33c5afe20427c8fd2ce5b3864d56bf2d07a60b1b1b4`) | `aa120f07f147f9bc80f4cef88a10b7c7ce9a9090250f7acd26d93ab517cc957a` | rejected（同步loader后正确，但case4双顺序消偏慢约13.5%） |
| exp147 | [`cuda_case10_vec2_reduce_exp147.cpp`](cuda_case10_vec2_reduce_exp147.cpp) | exp138/#108468 (`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`) | `7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6` | confirmed，#108604 / 60.00，后由exp149/#108628取代（case10 64-thread vec2 reducer消偏约快2.4%，OJ `55→54 μs`） |
| exp148 | [`cuda_case6_full_fused_tail_exp148.cpp`](cuda_case6_full_fused_tail_exp148.cpp) | exp147/#108604 (`7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`) | `837cbad3295d572c461be91150f4c94d699666f912df3e4e5d9d2e71593a1e1d` | rejected（case6 full-only+last-owner fused tail正确，但双顺序消偏慢约2.49%） |
| exp149 | [`cuda_case12_vec2_reduce_exp149.cpp`](cuda_case12_vec2_reduce_exp149.cpp) | exp147/#108604 (`7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`) | `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d` | confirmed，当前OJ baseline #108628 / 60.00（case12消偏约快0.11%，OJ `477→476 μs`但未跨分数tier） |

## 实验关系

```text
exp115 b73fb54d...  (2026-08-09主链末端)
  |-> exp117 783a1af1...  (独立 z CTA，split257 / 514 partial)
  |   -> exp118 f324ac23...  (split129 / 258 partial)
  |   -> exp119 c10c0ace...  (split86 / 172 partial)
  `-> exp120 e1733033...  (case14 generic-z2 K/V register lookahead)
      |-> exp121 ccc58a6e...  (同轮 early page ID，rejected)
      |-> exp122 ad724140...  (首次 page-ready/Q barrier 合并，中性)
      |-> exp123 3e85bd76...  (next-V 延到 PV 中点，rejected)
      `-> exp124 35a6a164...  (case10 full-only + fused tail；原reducer计数错误)
          `-> exp124b f98112aa...  (fused live-split修复)
              `-> exp125 e84f0a38...  (case10同步K/V register-lookahead，OJ #107856 Canceled)
                  |-> exp126 6a5b9115...  (case5 full-only+fused tail，rejected分支)
                  |-> exp127 477a4424...  (case5 combined register-lookahead，rejected分支)
                  |-> exp128 414ccc67...  (case10首页barrier融合，中性分支)
                  |-> exp129 1e84ef23...  (case10 split64/8页，rejected分支)
                  `-> exp130 4115934e...  (case12标量K-lookahead)
                      `-> exp131 2dfd4648...  (case13同模板标量K-lookahead，OJ #107882 Canceled)
                          `-> exp132 357ce23c...  (case9同模板标量K-lookahead)
                              `-> exp133 9f611f4d...  (case7同模板标量K-lookahead)
                                  `-> exp134 b3ba2b89...  (case13再加标量V-lookahead)
                                      `-> exp135 234af15e...  (裁剪CUTE/MMA编译表面；#108312首次达到59.86)
                                          `-> exp136 4df13ff6...  (case12再加标量V-lookahead；#108371/#108398 Canceled)
                                              `-> exp137 6bec5e02...  (case9再加标量V-lookahead)
                                                  `-> exp138 cef492aa...  (case7再加标量V-lookahead；#108468阶段baseline)
                                                      |-> exp139 00299b70...  (case11 z-pair partial offload，rejected分支)
                                                      |-> exp140 3a8383ad...  (case11 K/V lookahead标量化，rejected分支)
                                                      |-> exp142 c0049456...  (case14 z0寄存器保留，中性/rejected分支)
                                                      |-> exp143 b5fe8d7d...  (case8双head vec4 reducer，中性/rejected分支)
                                                      |-> exp144 330caba5...  (case4 z0寄存器保留，rejected分支)
                                                      |-> exp145 957aa068...  (case4 KV8双-head + 双BSM，NaN分支)
                                                      |-> exp146 aa120f07...  (同布局同步loader，正确但慢13.5%)
                                                      `-> exp147 7be23e1f...  (case10完整wave vec2 reducer；#108604阶段baseline)
                                                          `-> exp148 837cbad3...  (case6 full-only+fused tail，正确但慢2.49%)
                                                          `-> exp149 0f76be0b...  (case12完整wave vec2 reducer；#108628当前OJ baseline)
```

三十三份源码均为完整候选。exp117–119、exp121–123、exp126–129、exp139–140、exp142–146、exp148 未进入主链，原始exp124不得单独使用；exp135由#108312首次以59.86分确认，exp138由#108468完成四个目标长KV8的OJ闭环，exp147由#108604以60.00分确认case10完整wave reducer，exp149再由#108628确认case12 `477→476 μs`。当前工作文件、exp149和#108628逐提交快照字节一致，#108628是真实OJ control；case12尚未跨下一分数tier。
