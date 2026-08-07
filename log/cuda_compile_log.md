# OJ提交的编译日志

> 文件上面的是最新的日志

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