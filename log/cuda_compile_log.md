# OJ提交的编译日志

> 文件上面的是最新的日志

---

## #110941 — 2026-08-13 06:44:02（CompilationError / compile TLE）

- 按用户要求再次进行一次平台恢复探测；提交前队列为空，只创建这一笔。任务长时间保持`Pending`后直接终态，没有进入测试点，等待期间没有取消或并行复投。
- OJ首条诊断仍为`A TimeLimitExceeded encountered while compiling the code.`；输出只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。
- raw内嵌源码、逐提交快照及已14/14 Accepted的#110895/exp367、同源#110916字节一致，SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- 结论：提交创建入口可用，但OJ编译服务尚未稳定恢复；本次不是源码回归或性能数据，不继续同源复投，baseline保持#110426。
- 完整日志：`results/raw/cuda_110941_raw.json`。

---

## #110916 — 2026-08-13 05:52:57（CompilationError / compile TLE）

- 按用户要求进行一次平台试投；提交成功创建并从`Pending`进入`Compiling`，随后在测试点前以`A TimeLimitExceeded encountered while compiling the code.`终止。
- 输出只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。
- 提交源码、raw内嵌源码、工作文件及已14/14 Accepted的#110895/exp367快照字节一致，SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- 结论：提交与调度链路可用，本次失败是OJ编译服务偶发TLE，不是源码回归或性能数据；不立即同源复投，baseline保持#110426。
- 完整日志：`results/raw/cuda_110916_raw.json`。

---

## #110809 — 2026-08-13 02:50:15（CompilationError / compile TLE）

- OJ 原始消息：`A TimeLimitExceeded encountered while compiling the code.`
- 按用户要求只创建这一笔平台试投；OJ没有进入测试点，输出只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。
- 提交源码与已14/14 Accepted的#110771/exp356字节一致；工作文件、#110771快照、#110809快照及raw内嵌代码的SHA-256均为`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`。
- 结论：这是OJ编译服务的偶发TLE，不是源码回归或性能数据；不立即同源复投，baseline保持#110426。
- 完整日志：`results/raw/cuda_110809_raw.json`。

---

## #110760 — 2026-08-13 01:41:49（CompilationError / compile TLE）

- OJ 原始消息：`A TimeLimitExceeded encountered while compiling the code.`
- exp353提交前已通过CPU14/14、GPU full/boundary/random各14/14及case13/14精确长度复用；OJ没有进入测试点。
- 输出只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。提交源码SHA-256为`b5e12d6e6fc480100ba3ab6d51f3bee1595be41c7d4e8d096b227ad0a6b731ff`，大小216088 bytes。
- 等价运行语义的exp356删除一个新增模板参数并缩到215920 bytes后，由#110771正常编译且14/14 Accepted。可据此保留“减少模板表面”的工程措施，但不能把168-byte缩减宣称为TLE消失的唯一因果。
- 完整日志：`results/raw/cuda_110760_raw.json`。

---

## #110621 — 2026-08-12 23:07:27（CompilationError / compile TLE）

- OJ 原始消息：`A TimeLimitExceeded encountered while compiling the code.`
- 任务长时间保持 `Pending`；首轮 watch 超时后没有取消或复投，后续以编译超时终态结束，无测试点。
- 输出只有 MACA 忽略 `minBlocks` 的既有 warnings，没有源码 compiler error。
- 提交源码与已 14/14 Accepted 的 #110426、同样 compile TLE 的 #110546 字节一致，SHA-256 均为 `20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。
- 结论：这是第二个同源 OJ 编译环境故障样本，不是源码回归或性能数据；不创建第三笔重复任务，baseline 保持 #110426。
- 完整日志：`results/raw/cuda_110621_raw.json`。

---

## #110546 — 2026-08-12 22:08:54（CompilationError / compile TLE）

- OJ 原始消息：`A TimeLimitExceeded encountered while compiling the code.`
- 唯一任务成功从 `Pending` 进入 `Compiling`，随后在编译阶段超时；输出只有 MACA 忽略 `minBlocks` 的既有 warnings，没有源码 compiler error。
- 提交源码与已 14/14 Accepted 的 #110426 字节一致，SHA-256 均为 `20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。
- 结论：这是 OJ 编译环境故障，不是源码回归或性能数据；不自动重投，baseline 保持 #110426。
- 完整日志：`results/raw/cuda_110546_raw.json`。

---

## #108257 — 2026-08-10 17:30:21（CompilationError / compile TLE）

- OJ 原始消息：`A TimeLimitExceeded encountered while compiling the code.`
- 编译输出只有 CUTE 未初始化变量和 MACA 忽略 `minBlocks` 的既有 warnings，没有源码 compiler error。
- 同一 SHA-256 `b3ba2b89f707ee960f5df1198e32eefa133a6bd920b951a7728f693ce7c4a045` 已在本机 C500/MACA 环境约 10 秒构建成功。
- 结论：这是 OJ 编译阶段超时，不能作为 exp134 源码无法编译或性能回退的证据；不自动重投。
- 完整日志：`results/raw/cuda_108257_raw.json`。

---


MACA_DEVICE_IMAGE_MALLOC_POLICY=1
PWD=/xpuoj/work/1/working
HOME=/root/sandbox_home
PYTHONPATH=/root/triton-sandbox
SHLVL=1
LC_ALL=C.UTF-8
PATH=/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
_=/usr/bin/env
In file included from /sandbox/source/main.cu:31:
In file included from /opt/maca/include/cute/tensor.hpp:956:
In file included from /opt/maca/include/cute/algorithm/gemm.hpp:40:
In file included from /opt/maca/include/cute/atom/mma_atom.hpp:1060:
In file included from /opt/maca/include/cute/atom/mma_traits_sm80.hpp:33:
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:50: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:14: note: initialize the variable 'cc0' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:55: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:19: note: initialize the variable 'cc1' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:60: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:24: note: initialize the variable 'cc2' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:65: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:29: note: initialize the variable 'cc3' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:50: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:14: note: initialize the variable 'cc0' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:55: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:19: note: initialize the variable 'cc1' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:60: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:24: note: initialize the variable 'cc2' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:65: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:29: note: initialize the variable 'cc3' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
8 warnings generated when compiling for xcore1000.
In file included from /sandbox/source/main.cu:31:
In file included from /opt/maca/include/cute/tensor.hpp:956:
In file included from /opt/maca/include/cute/algorithm/gemm.hpp:40:
In file included from /opt/maca/include/cute/atom/mma_atom.hpp:1060:
In file included from /opt/maca/include/cute/atom/mma_traits_sm80.hpp:33:
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:50: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:14: note: initialize the variable 'cc0' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:55: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:19: note: initialize the variable 'cc1' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:60: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:24: note: initialize the variable 'cc2' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:65: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:29: note: initialize the variable 'cc3' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:50: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:14: note: initialize the variable 'cc0' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:55: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:19: note: initialize the variable 'cc1' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:60: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:24: note: initialize the variable 'cc2' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:65: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:29: note: initialize the variable 'cc3' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
8 warnings generated when compiling for xcore1000.



---
MACA_DEVICE_IMAGE_MALLOC_POLICY=1
PWD=/xpuoj/work/1/working
HOME=/root/sandbox_home
PYTHONPATH=/root/triton-sandbox
SHLVL=1
LC_ALL=C.UTF-8
PATH=/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
_=/usr/bin/env
In file included from /sandbox/source/main.cu:31:
In file included from /opt/maca/include/cute/tensor.hpp:956:
In file included from /opt/maca/include/cute/algorithm/gemm.hpp:40:
In file included from /opt/maca/include/cute/atom/mma_atom.hpp:1060:
In file included from /opt/maca/include/cute/atom/mma_traits_sm80.hpp:33:
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:50: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:14: note: initialize the variable 'cc0' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:55: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:19: note: initialize the variable 'cc1' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:60: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:24: note: initialize the variable 'cc2' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:334:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  334 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:352:65: note: uninitialized use occurs here
  352 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:334:12: note: remove the 'if' if its condition is always true
  334 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:321:29: note: initialize the variable 'cc3' to silence this warning
  321 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc0' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:50: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                  ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:14: note: initialize the variable 'cc0' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |              ^
      |               = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc1' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:55: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                       ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:19: note: initialize the variable 'cc1' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                   ^
      |                    = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc2' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:60: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                            ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:24: note: initialize the variable 'cc2' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                        ^
      |                         = 0.0
/opt/maca/include/cute/arch/mma_sm80.hpp:608:16: warning: variable 'cc3' is used uninitialized whenever 'if' condition is false [-Wsometimes-uninitialized]
  608 |     } else if (lane_id < 64) {
      |                ^~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:626:65: note: uninitialized use occurs here
  626 |                                                 {cc0, cc1, cc2, cc3});
      |                                                                 ^~~
/opt/maca/include/cute/arch/mma_sm80.hpp:608:12: note: remove the 'if' if its condition is always true
  608 |     } else if (lane_id < 64) {
      |            ^~~~~~~~~~~~~~~~~
/opt/maca/include/cute/arch/mma_sm80.hpp:595:29: note: initialize the variable 'cc3' to silence this warning
  595 |     float cc0, cc1, cc2, cc3;
      |                             ^
      |                              = 0.0
/sandbox/source/main.cu:59:31: error: expected '(' for function-style cast or type construction
   59 |     return cute::convert<float>(x);
      |                          ~~~~~^
/sandbox/source/main.cu:59:18: error: no member named 'convert' in namespace 'cute'
   59 |     return cute::convert<float>(x);
      |            ~~~~~~^
8 warnings and 2 errors generated when compiling for xcore1000.
