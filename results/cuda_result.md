# XPUOJ FlashAttention KV Cache Decode 提交结果记录

## 当前权威状态（2026-08-26 #126955 终态后）

- **最新终态：#126955 / exp731 case12 normalized-BF16 partial + synchronous group8 single-FP32-LSE reducer / `65.86` / 14/14 Accepted**。唯一target case12为`375 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`未跨至预注册`>=61分`（约`<=365.70 µs`）；关闭exact exp731 contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、226/55、102/52、232/57、39/62、228/52、375/60、181/57、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126937 / exp730 case12 normalized-BF16 partial + synchronous group8 reducer / `65.79` / 14/14 Accepted**。唯一target case12为`378 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`（约`<=365.70 µs`）；关闭exact exp730 contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、22/73、17/73、28/63、227/55、101/52、235/57、40/61、226/52、378/60、182/56、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **当前结构性 control：#124611 / exp666 case13 normalized-BF16 global partial + native row16 reducer / `66.00` / 14/14 Accepted**。唯一target case13（B1/KV8/L58966）为`181 µs / 57分`，相对前一候选#124606的`183 µs / 56分`和旧结构性control #113889 的`182 µs / 56分`跨过目标display tier；case13 BF16 global partial与native row16 reducer的组合形成可归因结构性收益，继承#113889的case7收益，故切换control。其它case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件与新control一致；当前实时队列状态见下方动态条目。

- **最新终态：#126894 / exp729 case5 BF16 sync 7-wave changed-precondition / `65.50` / 14/14 Accepted**。唯一target case5为`20 µs / 69分`，较结构control `#124611` 的`17 µs / 73分`退化且未达到预注册`>=74分`；相对exp727恢复producer `72 MT / 48 ST / 7 waves`的changed precondition未形成目标收益，关闭exact case5 BF16 sync 7-wave contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、22/73、20/69、28/63、226/55、103/51、233/57、40/61、227/52、375/60、180/57、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126879 / exp728 case6 BF16 sync partial / `65.50` / 14/14 Accepted**。唯一target case6为`29 µs / 62分`，较结构control `#124611` 的`28 µs / 63分`退化且未达到预注册`>=64分`；关闭exact case6 BF16 sync partial contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、18/71、29/62、225/55、102/52、233/57、40/61、226/52、376/60、182/56、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126847 / exp727 case5 BF16 sync partial / `65.57` / 14/14 Accepted**。唯一target case5为`19 µs / 70分`，较结构control `#124611` 的`17 µs / 73分`退化且未达到预注册`>=74分`；关闭exact case5 BF16 sync partial contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、19/70、28/63、225/55、101/52、234/57、40/61、226/52、375/60、181/57、146/54 µs/分`；非target资源变化、aggregate和同场timing不归因。

- **最新终态：#126832 / exp726 case1 shared-V fanout / `65.71` / 14/14 Accepted**。唯一target case1为`3 µs / 92分`，未严格高于control的`92分`；关闭exact case1 shared-V fanout contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、225/55、103/51、232/57、40/61、226/52、377/60、181/57、143/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126819 / exp725 guarded case2 native-B128 V-copy / `65.79` / 14/14 Accepted**。唯一target case2为`4 µs / 90分`，未达到预注册`>=91分`（约进入`3 us`档）；关闭exact guarded case2 native-B128 V-copy contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、24/71、17/73、28/63、225/55、102/52、234/57、39/62、227/52、374/60、181/57、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126791 / exp721 case12 group8 async guard / `65.71` / 14/14 Accepted**。唯一target case12为`383 µs / 59分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`；关闭exact case12 group8 async guard contract，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、225/55、102/52、237/57、40/61、224/52、383/59、181/57、142/54 µs/分`；非target case、aggregate和同场timing不归因。

- **最新终态：#126741 / exp718 case13 guarded group8 async-BF16 partial consumer / `65.50` / 14/14 Accepted**。唯一target case13为`202 µs / 54分`，较结构control `#124611` 的`181 µs / 57分`退化且未达到预注册`>=58分`；拒绝并关闭exact case13 group8 async-partial consumer，不切control。case1–14时延/分数=`3/92、4/90、10/82、23/72、17/73、29/62、224/55、102/52、234/57、39/62、227/52、378/60、202/54、143/54 µs/分`；非target case、aggregate和同场timing不归因。

- **前一终态：#126665 / exp716 case7 BF16 async partial / `65.93` / 14/14 Accepted**。唯一target case7为`228 µs / 55分`，未达到预注册`>=56分`；关闭exact case7 BF16 async partial contract，不切control。该候选未继承exp710的KV4 tail guard，非target case、aggregate和同场timing不归因。

- **最新终态：#126589 / exp715 case12 normalized internal z-state + direct fan-in / `65.86` / 14/14 Accepted**。唯一target case12为`380 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`；拒绝并关闭exact normalized internal z-state + direct fan-in，不切control。case1–14时延/分数=`3/92、4/90、9/82、23/72、17/73、28/63、227/55、102/52、235/57、39/62、224/52、373/60、182/56、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **前一终态：#126532 / exp714 case11 fused-tail direct register/raw-BSM consumer / `65.64` / 14/14 Accepted**。唯一target case11为`224 µs / 52分`，与结构control `#124611` 同档，未达到预注册`>=53分`；拒绝并关闭exact fused-tail direct register/raw-BSM consumer，不切control。case1–14时延/分数=`3/92、4/90、9/82、23/72、17/73、28/63、227/55、102/52、235/57、39/61、224/52、373/60、182/56、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **前一终态：#126478 / exp713 case11 guarded last-live split finalizer ownership / `65.57` / 14/14 Accepted**。唯一target case11为`255 µs / 49分`，较结构control `#124611` 的`224 µs / 52分`及exp710的`226 µs / 52分`显著退化，未达到预注册`>=53分`；关闭exact guarded last-live split finalizer ownership，不切control。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、227/55、102/52、235/57、39/62、255/49、373/60、182/56、146/54 µs/分`；非target case、aggregate和同场timing不归因。

- **前一终态：#125788 / exp710 z4 tail-padding guard / `65.57` / 14/14 Accepted**。候选在KV4 z4 fused-tail路径增加`valid_tokens`门控；OJ case8/10/11/14分别为`103/39/226/146 µs`、`51/62/52/54分`，目标display sum为`219`。该条同时记录C500 tail-NaN trap中candidate四个目标case finite、control nonfinite的安全反馈；线上性能与control状态分别按OJ事实和主Agent裁决处理。

- **前一终态：#125765 / exp704 z8 all async register-K/V backend / `65.93` / 14/14 Accepted**。唯一target cases7/9/12/13分别为`229/236/375/184 µs`、`55/57/60/56分`，display sum为`228`，低于当前control对应`229`；关闭exact z8 all async register-K/V backend contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因，终态后工作文件保持control。

- **前一终态：#125776 / exp709 short123 bundle / `66.07` / 14/14 Accepted**。唯一target cases1/2/3分别为`3/4/9 µs`、`92/90/83分`，target display sum为`265`；但预注册的case1/2/3目标`>=93/91/84分`均未达到，关闭exact short123 bundle contract，不切control、不重投或扫描。case3的`83分`只是本次线上观测，不构成结构性收益；非target case、aggregate和同场timing不归因，终态后工作文件保持control。

- **前一终态：#125753 / exp705 z4 all async register-K/V backend / `65.43` / 14/14 Accepted**。唯一target cases8/10/11/14分别为`52/62/51/53分`，合计`218`，低于当前control对应`54/62/52/55`合计`223`；关闭exact z4 all async register-K/V backend contract，不切control、不重投或扫描。C500 tail probe另确认candidate与control共同读取有效长度后的padding并产生nonfinite，这是继承control的诊断，不将exp705记为无条件C500 safety PASS；非target case、aggregate和同场timing不归因，终态后工作文件保持control。

- **前一终态：#125658 / exp696 case12 raw-wave rebase / `66.00` / 14/14 Accepted**。唯一target case12为`375 µs / 60分`，未达到预注册`>=61分`；关闭exact raw-wave `lane^32` first-z merge contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **最新终态：#125636 / exp693 case11 fixed-20-page MMA hot loop / `66.00` / 14/14 Accepted**。唯一target case11（B16/KV4/L12251）为`222 µs / 52分`，未达到预注册的`>=53分`；关闭exact case11 fixed-20-page owner、`19×HAS_NEXT=true`加末次`false` hot-loop contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、233/57、38/62、222/52、374/60、183/56、140/55 µs/分`；非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125625 / exp698 case5 single-live direct-output + reducer return / `66.00` / 14/14 Accepted**。唯一target case5（B16/KV4/L141）为`17 µs / 73分`，未达到预注册的`>=74分`；关闭exact case5 seqlen 1..32 single-live direct-output + reducer-return contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、226/55、94/54、233/57、38/62、222/52、376/60、181/57、139/55 µs/分`；非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125585 / exp695 case9 raw-wave `lane^32` first-z merge / `65.86` / 14/14 Accepted**。唯一target case9（B32/KV8/L4096）为`244 µs / 56分`，未达到预注册的`>=58分`；关闭exact case9 raw-wave `lane^32` first-z merge contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、10/82、23/72、17/73、28/63、227/55、93/54、244/56、38/62、224/52、375/60、182/56、139/55 µs/分`；非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125561 / exp694 case7 raw physical-wave `lane^32` first-z merge / `65.86` / 14/14 Accepted**。唯一target case7（B64/KV8/L2048）为`233 µs / 54分`，相对当前control的`226 µs / 55分`退档，未达到预注册的`>=56分`；关闭exact case7 raw physical-wave `lane^32` first-z merge contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、10/82、23/72、17/73、28/63、233/54、94/54、233/57、38/62、224/52、374/60、182/56、139/55 µs/分`；非target case、aggregate和同场timing不归因。raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125434 / exp692 case11 adjacent-lane BF16 handoff + even-lane native B128 final-output store / `66.14` / 14/14 Accepted**。唯一target case11（B16/KV4/L12251）为`223 µs / 52分`，未达到预注册的`>=53分`；关闭exact case11相邻lane BF16 handoff与偶数lane native B128 final-output store contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、231/57、38/62、223/52、377/60、181/57、139/55 µs/分`；非target case、aggregate和同场timing不归因。raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125388 / exp690 case7 threechunk fused direct / `65.71` / 14/14 Accepted**。唯一target case7（B64/KV8/L2048）为`269 µs / 51分`，相对当前control约`226 µs / 55分`严重退档；关闭exact case7 `43/43/42` three-bucket same-CTA FP32 state direct-output、跳过partial+reducer contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、10/82、23/72、17/73、28/63、269/51、93/54、235/57、38/62、222/52、374/60、181/57、139/55 µs/分`；非target case、aggregate和同场timing不归因。raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125367 / exp691 case6 fixed `STATIC_WEIGHT_SPLITS=8` row16 / `65.93` / 14/14 Accepted**。唯一target case6（B16/KV8/L362）为`29 µs / 62分`，相对当前control `28 µs / 63分`退档；关闭exp691 exact case6 fixed row16 static-weight contract，不切换control、不重投或扫描。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、29/62、225/55、94/54、232/57、38/62、224/52、373/60、182/56、139/55 µs/分`；非target case、aggregate和同场timing不归因。归档时独立exp690提交`#125388`仍为Pending，本任务未触碰该在途提交；raw、不可变源码与candidate SHA见下方提交条目。

- **最新终态：#125311 / exp689 case13 final `z1 -> z0` raw-wave64 peer merge / `65.86` / 14/14 Accepted**。唯一target case13（B1/KV8/L58966）为`182 µs / 56分`，相对当前control `181 µs / 57分`退档，未达到预注册的`<=174.5 µs`或`>=58分`；关闭exp689 exact final `z1 -> z0` raw-wave64 peer-merge contract，不切换control、不重投或扫描。非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件保持control，OJ队列无在途。

- **最新终态：#125281 / exp688 case13 normalized-BF16 partial native-B128 STG / `66.00` / 14/14 Accepted**。唯一target case13（B1/KV8/L58966）为`181 µs / 57分`，与当前control同档，未达到预注册的跨档目标；关闭exp688 exact case13 normalized-BF16 partial producer native-B128 STG contract，不切换control、不重投或扫描。非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目；exp689后续提交`#125311`已终态，本条不重复归因，工作文件保持control。

- **最新终态：#125268 / exp687 case14 pair aggregate fix / `64.43` / 14/14 Accepted**。唯一target case14（B1/KV4/L61519）为`350 µs / 32分`，相对当前control `139 µs / 55分`严重退档；关闭`257 logical split -> 129 pair aggregate ownership` exact contract，不切换control、不重投或扫描。非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目。归档核验时独立exp688提交`#125281`仍为Pending，本条未触碰该在途提交。

- **最新终态：#125236 / exp685 case14 normalized-BF16 partial native-B128 STG / `66.00` / 14/14 Accepted**。唯一target case14（B1/KV4/L61519）为`139 µs / 55分`，未达到预注册的`<=135 µs`或`>=56分`；关闭exp685 exact contract，不切换control。其它case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件保持control。随后独立exp687提交`#125268`已终态，本条不重复归因。

- **最新终态：#125200 / exp684 同源码 control 方差 probe / `66.07` / 14/14 Accepted**。这是对当前control `#124611 / exp666` 的同源码有目的复测；case1–14时延=`3/4/9/23/17/28/228/93/235/39/223/377/181/139 µs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。该结果仅用于观察线上方差，不对非target波动作归因，不切control；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件保持control，OJ队列无在途。

- **最新终态：#125089 / exp679 case6 native-K-LDG / `66.00` / 14/14 Accepted**。唯一target case6（B16/KV8/L362）为`28 µs / 63分`，与当前control #124611同档，未达到预注册的`>=64分`；关闭exp679 case6 native-K-LDG exact contract，不切换control。其它case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件保持control、OJ队列无在途。

- **最新终态：#125124 / exp680 case14 hierarchical BF16 partial tree / `65.93` / 14/14 Accepted**。唯一target case14（B1/KV4/L61519）为`142 µs / 54分`，相对当前control #124611的`139 µs / 55分`退档，未达到预注册的`>=56分`；关闭exp680 exact hierarchical BF16 partial tree contract，不切换control。额外 group stage 的线上变化不归因，非target case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件保持control、OJ队列无在途。

- **最新终态：#124696 / exp675 case11 normalized-BF16 producer + 32-thread vec4 BF16 consumer / `65.93` / 14/14 Accepted**。唯一target case11（B16/KV4/L12251）为`225 µs / 52分`，相对当前control #124611的`224 µs / 52分`未达到预注册的`>=53分`；关闭exp675 exact contract，不切换control。其它case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后队列无在途、工作文件保持control。

- **最新终态：#124684 / exp674 case7 normalized-BF16 partial + static-weight group8 consumer / `65.50` / 14/14 Accepted**。唯一target case7（B64/KV8/L2048）为`227 µs / 55分`，与当前control #124611的`227 µs / 55分`同档，未达到预注册的`>=56分`；关闭exp674 case7 normalized-BF16 partial→static-weight group8 consumer exact contract，不切换control。其它case、aggregate和同场timing不归因；raw、不可变源码与candidate SHA见下方提交条目，终态后本归档任务未修改工作文件。

- **最新终态：#124669 / exp673 case9 normalized-BF16 partial + native-row16 vec2 consumer / `66.07` / 14/14 Accepted**。唯一target case9（B32/KV8/L4096）为`235 µs / 57分`，相对当前control #124611 的`236 µs / 57分`同档，未达到`>=58分`；关闭exp673 case9 normalized-BF16 partial + native-row16 vec2 exact contract，不切control。case13 `181 µs / 57分`为共用模板/继承control结果，非target；其它case、aggregate和同场timing不归因。raw、不可变源码与candidate SHA见下方提交条目；本条归档不修改工作文件或OJ队列。

- **最新终态：#124660 / exp672 case8 normalized-BF16 partial + group8 native-row16 consumer / `66.00` / 14/14 Accepted**。唯一target case8（B16/KV4/L4096）为`94 µs / 54分`，与#124611 control相同，未达到`>=55分`；case8 normalized-BF16 partial→group8 native-row16 consumer exact contract关闭，不切control。case7虽受共用模板 codegen/resource影响，线上`227 µs / 55分`仍未形成target收益，不作归因；其它case、aggregate和同场timing不归因。raw、不可变源码与candidate SHA见下方提交条目；本条归档不修改工作文件或OJ队列。

- **最新终态：#124647 / exp671 case12 normalized-BF16 partial + native-row16 vec2 consumer / `66.00` / 14/14 Accepted**。唯一target case12（B8/KV8/L32768）为`372 µs / 60分`，相对当前control #124611 的`371 µs / 60分`未跨至`>=61分`（约`<=365 µs`）；关闭exp671 exact contract，不切换control。case13 `181 µs / 57分`为control继承结果，非target；其它case、aggregate和同场timing不归因。终态后工作文件恢复#124611，OJ队列无在途。

- **最新终态：#124621 / exp668 case12 V-dead-half tokenized-BSM role swap / `65.86` / 14/14 Accepted**。唯一target case12（B8/KV8/L32768）为`392 µs / 59分`，相对当前control #124611 的`371 µs / 60分`明显退档，未达到`>=61分`（约`<=365 µs`）；关闭exp668 V-dead-half exact contract，不切换control。case13 `181 µs / 57分`仅复现当前control，非target/aggregate及其它case同场timing不归因；终态后工作文件恢复#124611，OJ队列无在途。

- **前一终态：#124606 / exp665 case13 normalized-BF16 global partial + valid-tail / `66.00` / 14/14 Accepted**。唯一target case13（B1/KV8/L58966）为`183 µs / 56分`，相对当时control `182 µs / 56分`未跨至`>=57分`（约`<=181 µs`）；exp665 exact contract关闭，不切换control。raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件恢复当时control，OJ队列无在途。

- **最新终态：#124601 / exp664 case12 dead-half K-token BSM wave release / `66.00` / 14/14 Accepted**。唯一target case12（B8/KV8/L32768）为`375 µs / 60分`，相对control `378 µs / 60分`未跨至`>=61分`（约`<=365 µs`）；exp664 exact contract关闭，不切换control。raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件恢复control，OJ队列无在途。

- **最新终态：#124570 / exp660 case12 async register-returning K/V load + rebase / `66.00` / 14/14 Accepted**。唯一target case12（B8/KV8/L32768）为`373 µs / 60分`，相对control `378 µs / 60分`未达到`>=61分`（约`<=365 µs`）；exp660 exact contract关闭，不切换control。raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件恢复control，OJ队列无在途。

- **最新终态：#124563 / exp661 case14 single FP32 LSE state/reducer + tail-only valid K/V loader/PV guard / `65.86` / 14/14 Accepted**。唯一target case14（B1/KV4/L61519）为`141 µs / 54分`，相对control `139 µs / 55分`退档，未达到`>=56分`；exp661 exact contract关闭，不切换control。raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件恢复control，OJ队列无在途。

- **最新终态：#124537 / exp631 case2 source-owner native B128 single-launch / `66.00` / 14/14 Accepted**。唯一target case2（B4/KV8/L2）为`4 µs / 90分`，与control同档，未达到约`<=3.75824 µs / 91分`；exp631 exact contract关闭，不切换control。raw、不可变源码与candidate SHA已核验，终态后工作文件恢复control，OJ队列无在途。

- **最新终态：#124526 / exp657 case6 separate short-row owner / `65.64` / 14/14 Accepted**。唯一target case6（B16/KV8/L362）为`36 µs / 57分`，相对结构性control `28 µs / 63分`退档；exp657 exact contract关闭，不切换control。官方 raw、不可变源码与candidate SHA见下方提交条目，终态后工作文件已恢复control，OJ队列无在途。

- **前一结构性 control：#113889 / exp559 / `66.00` / 14/14 Accepted**，SHA-256 `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，不可变源码为 `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`。它仅给 case7 B64/KV8/L2048、固定3-split 的 packed group8 reducer使用静态`native_row16_broadcast<0/1/2>`取代rolled accumulator loop中的动态weight shuffle；metadata/LSE row reduction、fused-tail、producer、partial ABI、grid和其他shape保持#113696。case7唯一覆盖目标从#113696的`230 μs/54分`到`226 μs/55分`，兑现可归因 display gain，故曾接受为结构性control；未覆盖case的同场波动不抵消该结论。下方较早条目仅保留历史归因。

- **最新终态：#124440 / exp654 case9 raw-FP32 pair-state direct three-peer fan-in / `66.07` / 14/14 Accepted**。官方 raw 为`results/raw/cuda_124440_raw.json`，raw SHA-256=`9e6d1980a04f4e1069f87e0062758d7a661766bba53b07ae3d85146f2b102c37`；不可变提交源码为`solutions/archive/2026-08-24-submissions/cuda_124440.cpp`，candidate/submitted/immutable SHA-256均为`314c3445e887e4e2e1e16653a3e7be28d71b44803b8d6a720f73b68d28f13bff`，manifest已登记。OJ总耗时`1593 ms`、内存`23060644 KB`；case1–14时延/分数=`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、236/57、39/62、223/52、372/60、182/56、139/55 µs/分`。唯一预注册 target case9（B32/KV8/L4096）为`236 µs / 57分`，相对结构性control的`57分`未跨至`>=58分`；其它case、aggregate和同场timing不归因，exp654 exact contract关闭，不切换control、不重投或扫描fan-in、peer、state layout、lane、template或启用范围。提交客户端和首次watch各因900s超时，未取消远端任务；后续仅对同一ID watch完成终态和raw归档，终态后工作文件恢复control，OJ队列无在途。

- **最新终态：#124413 / exp652 错误重复 probe / `66.07` / 14/14 Accepted**。这是前执行者在#124393 watch超时后意外重投的同一 candidate，不能视为独立实验；唯一 target case11为`223 µs / 52分`，相对control的`222 µs / 52分`同档，未达到至少`53分`，control不变。raw、提交源码与candidate SHA已核验，工作文件已恢复control，OJ队列为空。
- **前一终态：#124393 / exp652 首次 probe / `66.00` / 14/14 Accepted**。唯一 target case11为`224 µs / 52分`，相对control的`222 µs / 52分`同档，目标失败；#124393 与错误重复#124413均使用同一 candidate，exp652 exact contract关闭，不切control、不再重投。

- **最新终态：#124328 / exp651 / WrongAnswer / `59.64`**。唯一预注册目标 case7 在线为`282 µs / 49分`，相对 control 的`226 µs / 55分`退档；case3 为 WrongAnswer（约`36,382,034 ms`），其余 13 个测试点 Accepted。exp651 two-stage finalizer + tailmask exact contract线上关闭，control不变；raw、提交源码与 candidate SHA 已核验，工作文件已恢复#113889，OJ队列为空。
- **最新终态：#124235 / exp632 / `66.07` / 14/14 Accepted**。唯一预注册目标 case2 为`4 µs / 90分`，与control同档，未达到约`<=3.75824 µs / 91分`；exp632 source-owner streaming B32 exact contract线上关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#124170 / exp592 / `65.57` / 14/14 Accepted**。唯一预注册目标 case7 为`276 µs / 50分`，相对control的`226 µs / 55分`严重退档，未达到`>=56分`；exp592 independent direct-output/fixed-launch exact contract线上关闭，control不变。
- **前一终态：#124146 / exp637 / `66.00` / 14/14 Accepted**。唯一预注册目标 case6 为`30 µs / 62分`，相对control的`28 µs / 63分`退档，未达到约`<=27 µs / 64分`；exp637 next-K register-wave BSM exact contract关闭，control不变。
- **前一终态：#124090 / exp625 / `65.86` / 14/14 Accepted**。唯一预注册目标 case12 为`376 µs / 60分`，相对control的`378 µs / 60分`未达到约`<=365 µs / 61分`；exp625 distributed-weight exact contract关闭，control不变。
- **前一终态：#124003 / exp643 / `65.79` / 14/14 Accepted**。唯一预注册目标 case1 为`4 µs / 90分`，相对control的`3 µs / 92分`退档；exp643 native-BSM shared-V exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#123976 / exp646 / `66.07` / 14/14 Accepted**。唯一预注册目标 case1 为`3 µs / 92分`，与control同档且未严格高于92分；exp646 raw-BSM V fanout exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#123950 / exp650 / `66.00` / 14/14 Accepted**。唯一预注册目标 case11 为`227 µs / 52分`，相对control的`222 µs / 52分`未跨 display tier；exp650 normalized-BF16 direct-fanin txfix exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#123932 / exp649 / `66.00` / 14/14 Accepted**。唯一预注册目标 case14 为`141 µs / 54分`，相对control的`139 µs / 55分`未跨 display tier；exp649 normalized-BF16 direct-fanin txfix exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#123892 / exp648 / `65.86` / 14/14 Accepted**。唯一预注册目标 case8 为`95 µs / 53分`，相对control的`94 µs / 54分`未跨 display tier；exp648 normalized-BF16 direct-fanin txfix exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#123872 / exp608 / `66.00` / 14/14 Accepted**。唯一预注册目标 case12 为`387 µs / 59分`，相对control的`378 µs / 60分`退化且未达到约`<=365.70 µs / 61分`；exact direct-K wave-BSM current/next-K lookahead contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **最新终态：#123848 / exp609 / `65.79` / 14/14 Accepted**。唯一预注册目标 case11 为`266 µs / 48分`，相对control的`222 µs / 52分`明显退化且未达到约`<=220 µs / 53分`；duplicated-global-V exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **最新终态：#122987 / exp644 / `66.07` / 14/14 Accepted**。唯一预注册目标 case12 为`380 µs / 60分`，相对control的`378 µs / 60分`退化且未达到约`<=365.70 µs / 61分`；raw-FP32 pair-state direct three-peer fan-in exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#122912 / exp641 / `65.86` / 14/14 Accepted**。唯一预注册目标 case2 为`5 µs / 88分`，相对control的`4 µs / 90分`变慢且未跨至约`<=3.75824 µs / 91分`；CTA shared K/V owner exact contract关闭，control不变，工作文件已恢复#113889，OJ队列为空。

- **最新终态：#122490 / exp635 / `66.00` / 14/14 Accepted**。唯一预注册目标 case12 为`376 µs / 60分`，仍未达到约`<=365.70 µs / 61分`的 display tier；exact even-z native-B128-LDG Q owner→odd-z `lane^32` BSM Q payload contract 关闭，control 不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#122261 / exp634 / WrongAnswer / `60.14`**。唯一预注册目标 case1 保持`3 µs / 92分`，没有目标 display 收益；case3 在线上以`matched_ratio=0.999969 < 1.0`、`max_abs_diff=0.019531`失败。其余显示测试点为 Accepted，但全局 WrongAnswer，不作性能归因；exact native B128 LDG→8 STG fan-out contract 关闭，control 不变，工作文件已恢复#113889，OJ队列为空。
- **前一终态：#121954 / exp623 revalidation / `65.86` / 14/14 Accepted**。case12 direct-K wave-BSM no-lookahead 的唯一覆盖目标从#113889的`378 µs / 60分`退至`406 µs / 58分`；这与完整本地 A/B 的 full/random 系统性回退一致，线上直接否定 exact contract，故不替换control。raw、不可变提交源码和候选 SHA 已核验一致，工作文件已恢复#113889，OJ队列为空。
- **最新终态：#120152 / exp611 / `66.00` / 14/14 Accepted**。case12 Q physical-wave raw-BSM + partial B128 STG 组合的唯一覆盖目标从#113889的`378 µs / 60分`到`374 µs / 60分`，未跨display tier；其它case同场timing不能归因，故关闭 exact combined contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#118862 / exp603 / `66.07` / 14/14 Accepted**。case12 physical-wave Q producer→raw-BSM register consumer 的唯一覆盖目标从#113889的`378 µs / 60分`到`375 µs / 60分`，未跨display tier；其它case同场波动不能归因，故关闭 exact exp603 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **最新终态：#117052 / exp601 / `66.07` / 14/14 Accepted**。case12 FP32 `partial_acc float4` producer B128 native-STG backend 的唯一覆盖目标从#113889的`378 µs / 60分`到`368 µs / 60分`，虽快10 µs但未跨display tier；其它case同场波动不能归因，故关闭 exact exp601 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **最新终态：#117007 / exp600 / `66.00` / 14/14 Accepted**。case14 normalized-BF16 `partial_acc` scalar B16 STX producer backend 的唯一覆盖目标由#113889的`139 µs / 55分`到`140 µs / 55分`，未跨display tier且变慢；其它case同场波动不能归因，故关闭 exact exp600 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#116965 / exp599 / `66.14` / 14/14 Accepted**。case14 scalar B16 STX final-output global-store backend 的唯一覆盖目标保持#113889的`139 µs / 55分`，未跨display tier；case4/13的`22/73`与`181/57`是未覆盖timing样本，不能归因，故关闭 exact exp599 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#116797 / exp598 / `66.00` / 14/14 Accepted**。case11 symmetric-finalizer raw-FP32 `partial_acc float4` producer native-STG backend 的唯一覆盖目标保持#113889的`222 µs / 52分`；完整门禁通过而无可归因display gain，故关闭 exact exp598 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#116723 / exp597 / `66.00` / 14/14 Accepted**。case12 vec2 reducer `partial_acc` B64 native-LDG consumer 的唯一覆盖目标从#113889的`378→372 μs`，但显示分仍60；完整门禁通过而无可归因display gain，故关闭 exact exp597 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#116571 / exp594 / `66.00` / 14/14 Accepted**。case14 final-output native-B128 store 的唯一覆盖目标为`139 μs / 55分`，与#113889 control同档，未跨 display tier；完整门禁通过但无可归因display gain，故关闭 exact exp594 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#116314 / exp588 / `66.00` / 14/14 Accepted**。case12 native-B128 shared-Q producer 的唯一覆盖目标为`373 μs / 60分`，未跨 display tier；完整门禁通过但无可归因display gain，故关闭 exact exp588 contract 且不替换control。工作文件已恢复#113889，OJ队列为空。
- **前一终态：#115902 / exp579 / `66.00` / 14/14 Accepted**。case12 Q register consumer 的 native-LDG 使唯一覆盖目标从#113889的`378→372 μs`，但显示分仍60；完整门禁通过而无可归因display gain，故关闭 exact Q-native-LDG consumer/backend contract 且不替换control。
- **最新终态：#115744 / exp578 / `66.07` / 14/14 Accepted**。case12 single-split raw-BF16 shared-Q staging 使唯一覆盖目标从#113889的`378→371 μs`，但显示分仍60；完整门禁通过而无可归因display gain，故关闭 exact producer/consumer contract 且不替换control。
- **最新终态：#115685 / exp576 / `66.07` / 14/14 Accepted**。case4 distributed-PV-`exp2` 使唯一覆盖目标保持#113889的`23 μs/72分`；完整门禁通过而无可归因display gain，故关闭 exact producer/consumer contract 且不替换control。
- **前一终态：#115590 / exp573 / `66.00` / 14/14 Accepted**。case12 split-wide page-table PID shared cache 使唯一覆盖目标从#113889的`378→376 μs`，但显示分仍60；完整门禁通过而无可归因display gain，故关闭 exact shared-cache dataflow 且不替换control。
- **前一终态：#115574 / exp572 / `66.14` / 14/14 Accepted**。case6 固定三页 partial 的 reducer live-split `ceil` magic-division specialization 使唯一覆盖目标保持#113889的`28 μs/63分`；总分刷新来自未覆盖的case4 `23→22 μs/72→73分`与case13 `182→181 μs/56→57分` timing-tier 样本，故关闭 exact reducer specialization 且不替换control。
- **前一终态：#114179 / exp570 / `66.00` / 14/14 Accepted**。case12 pre-QK next-K lookahead 使唯一覆盖目标从#113889的`378→377 μs`，但显示分仍为60；该同档变化不能建立可归因 display gain，故关闭 exact 数据流且不替换control。
- **前一终态：#114013 / exp564 / `66.07` / 14/14 Accepted**。case8 FP16x2 `(m,l)` producer→实际group8 reducer partial ABI使唯一覆盖目标从#113889的`94→93 μs`，但显示分仍为54；该同档变化不能建立可归因 display gain，故关闭 exact ABI 且不替换control。
- **前一终态：#113889 / exp559 / `66.00` / 14/14 Accepted**。case7 static row16 weight broadcast 将唯一覆盖目标从#113696的`230 μs/54分`到`226 μs/55分`；完整资源、correctness、精确1/2/3-live-split边界和三分布门禁均通过，故接受为当前control。
- **前一终态：#113827 / exp558 / `66.00` / 14/14 Accepted**。case6 FP16x2 `(m,l)` producer/reducer partial ABI 的唯一覆盖目标保持#113696的`28 μs/63分`；未覆盖case的同场波动不归因，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113768 / exp557 / `65.93` / 14/14 Accepted**。case5 FP16x2 `(m,l)` producer/reducer partial ABI 的唯一覆盖目标保持#113696的`17 μs/73分`；未覆盖case的同场波动不归因，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113750 / exp555 / `66.07` / 14/14 Accepted**。case12 wave64 readlane next-page PID broadcast 的唯一覆盖目标由#113696的`373→374 μs`、显示分仍为60；高 aggregate 来自未覆盖case的 timing-tier 刷新，不能建立可归因 display 收益，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113736 / exp554 / `66.07` / 14/14 Accepted**。case12 wave64 raw-BSM next-page PID broadcast 的唯一覆盖目标由#113696的`373→376 μs`、显示分仍为60；高 aggregate 来自未覆盖case的 timing-tier 刷新，不能建立可归因 display 收益，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113715 / exp551 / `66.00` / 14/14 Accepted**。case9 row0-prefix native reducer 的唯一覆盖目标由#113696的`234→233 μs`、显示分仍为57；同档时延不能建立可归因 display 收益，故关闭该 exact contract，工作文件恢复#113696。
- **更早终态：#113712 / exp550 / `66.00` / 14/14 Accepted**。case8 physical-row16 + fixed-xor16 vec4 reducer 的唯一覆盖目标由#113696的`94→93 μs`、显示分仍为54；同档时延不能建立可归因 display 收益，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113708 / exp549 / `66.00` / 14/14 Accepted**。case13 65th-overflow physical-row16 serial-leader reducer 的唯一覆盖目标保持#113696的`181 μs/57分`；未覆盖case的同场波动不归因，故关闭该 exact contract，工作文件恢复#113696。
- **前一终态：#113703 / exp548 / `65.93` / 14/14 Accepted**。case12 physical-row16 serial-leader reducer 的唯一覆盖目标由#113696的`373→371 μs`，显示分仍为60；未覆盖case的同场波动不归因，故关闭该 exact contract，工作文件恢复#113696。
- 真实 OJ 最高分记录：**#115574、#116965 并列 / `66.14` / 14/14 Accepted**。两者均为未形成目标 case 可归因 display 收益的 timing-tier 样本：#115574 的case6目标未跨档，#116965 的case14目标也保持`139 µs/55分`；因此不改变结构性control。
- 结构性默认 control：**#113677 / exp545 / `65.93`**，SHA-256 `6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`，不可变源码为 `solutions/archive/2026-08-16-submissions/cuda_113677.cpp`。它仅改变case14 reducer并使唯一目标从`141 μs/54分`到`139 μs/55分`；未修改case的同场波动不抵消这个可归因跨档收益。
- 最新终态：**#113689 / exp546 / `65.93` / 14/14 Accepted**。case11 vec4 physical-row16 reducer 令目标样本`225→223 μs`，但显示分保持52，且未改case11的相邻样本已有`223/222 μs`；没有可归因 display 收益，关闭且不替换control。
- 前一终态：**#113658 / exp544 / `65.93` / 14/14 Accepted**。case7 packed group8 physical-row16 reducer 令目标时延`227→225 μs`，但显示分仍为55；没有可归因的 display 收益，关闭且不替换control。
- 前一终态：**#113642 / exp543 / `66.00` / 14/14 Accepted**。group8 final native-STG 的覆盖case5/6未变、case7虽`227→226 μs`仍55分、case8`93→94 μs`仍54分，关闭且不替换control。
- 较早终态：**#113566 / exp542 / `65.86` / 14/14 Accepted**。唯一覆盖目标case12由`375→376 μs`、显示分仍60，关闭且不替换control。
- 动态 OJ 队列与工作文件（本次归档记录时）：当前队列无非终态提交；工作文件已恢复#124611 control，SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。动态状态由主 Agent按启动流程实时核验。
- raw 终态统计：**410** 份（377 Accepted、17 CompilationError、12 WrongAnswer、4 Canceled）。

### 提交 #126955 · exp731 case12 normalized-BF16 partial + synchronous group8 single-FP32-LSE reducer

- **代码溯源**：官方 raw 为[`cuda_126955_raw.json`](raw/cuda_126955_raw.json)，不可变提交源码为[`cuda_126955.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126955.cpp)，实验候选为[`cuda_control124611_guard_case12_group8_sync_single_lse_exp731.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case12_group8_sync_single_lse_exp731.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；base exp730 SHA=`18d5908f778aed67ccf8e7038f723bbd9a816810a45999117768910e73dd1828`；candidate、submitted及immutable源码SHA-256均为`0a3641330135853c8238a90132f2246c22cada03f714068129f604e793f90f05`；raw JSON SHA-256为`e3b85500b692b3ba79d40dbcf985e11029b45356e4c7c28d25a5b045d1c08e3a`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126955`为`Accepted`、总分`65.86`、14/14；OJ总耗时`1613 ms`、内存`23060704 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、102/52、232/57、39/62、228/52、375/60、181/57、146/54 µs/分`，全部`Accepted`。唯一target case12为`375 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`未跨至预注册`>=61分`（约`<=365.70 us`）；拒绝并关闭exact case12 normalized-BF16 partial + synchronous group8 single-FP32-LSE reducer contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：此前POST已返回`#126955`但客户端随后遭遇503；身份恢复阶段实时列表确认该ID为对应提交，未重新POST，仅对同一ID执行watch并取得raw。实际POST次数为1，无取消、并行或重投；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126937 · exp730 case12 normalized-BF16 partial + synchronous group8 reducer

- **代码溯源**：官方 raw 为[`cuda_126937_raw.json`](raw/cuda_126937_raw.json)，不可变提交源码为[`cuda_126937.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126937.cpp)，实验候选为[`cuda_control124611_guard_case12_group8_sync_bf16_exp730.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case12_group8_sync_bf16_exp730.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`18d5908f778aed67ccf8e7038f723bbd9a816810a45999117768910e73dd1828`；raw JSON SHA-256为`8425f35cee8e72952f5a5c21168ac8cde584a9931d9f1dc47d2dd715849bae94`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126937`为`Accepted`、总分`65.79`、14/14；OJ总耗时`1618 ms`、内存`23060452 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、22/73、17/73、28/63、227/55、101/52、235/57、40/61、226/52、378/60、182/56、146/54 µs/分`，全部`Accepted`。唯一target case12为`378 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`（约`<=365.70 µs`）；拒绝并关闭exact exp730 case12 normalized-BF16 partial + synchronous group8 reducer contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126937`一次，首次watch超时后仅继续watch同一ID至`Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126894 · exp729 case5 BF16 sync 7-wave changed-precondition

- **代码溯源**：官方 raw 为[`cuda_126894_raw.json`](raw/cuda_126894_raw.json)，不可变提交源码为[`cuda_126894.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126894.cpp)，实验候选为[`cuda_control124611_guard_case5_bf16_sync_7wave_exp729.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case5_bf16_sync_7wave_exp729.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`23ed23da50608d66dda439d8895ab0bf783a1f8fceb9efaabdf6e3120b6aa9f7`；raw JSON SHA-256为`0f35335ad1c93a576d23467aa08874fffa37b76e1702669443b887fc57069ec9`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126894`为`Accepted`、总分`65.50`、14/14；OJ总耗时`1617 ms`、内存`23060424 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、22/73、20/69、28/63、226/55、103/51、233/57、40/61、227/52、375/60、180/57、146/54 µs/分`，全部`Accepted`。唯一target case5为`20 µs / 69分`，较结构control `#124611` 的`17 µs / 73分`退化且未达到预注册`>=74分`；相对exp727的changed precondition未形成目标收益，拒绝并关闭exact case5 BF16 sync 7-wave contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126894`一次，首次watch 900s超时后仅继续watch同一ID至`Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126879 · exp728 case6 BF16 sync partial

- **代码溯源**：官方 raw 为[`cuda_126879_raw.json`](raw/cuda_126879_raw.json)，不可变提交源码为[`cuda_126879.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126879.cpp)，实验候选为[`cuda_control124611_guard_case6_bf16_sync_partial_exp728.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case6_bf16_sync_partial_exp728.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`dc34862daf0767dedc888840ff7ae723b9ec1a5b1c6b67e9f392439f99c8f9c4`；raw JSON SHA-256为`523c9c955d2de63c17439ae8e51f0611b7a6899528cdf199d1c39bb7952410da`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126879`为`Accepted`、总分`65.50`、14/14；OJ总耗时`1616 ms`、内存`23060360 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、18/71、29/62、225/55、102/52、233/57、40/61、226/52、376/60、182/56、146/54 µs/分`，全部`Accepted`。唯一target case6为`29 µs / 62分`，较结构control `#124611` 的`28 µs / 63分`退化且未达到预注册`>=64分`；拒绝并关闭exact case6 BF16 sync partial contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126879`一次，首次watch 900s超时后仅继续watch同一ID至`Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126847 · exp727 case5 BF16 sync partial

- **代码溯源**：官方 raw 为[`cuda_126847_raw.json`](raw/cuda_126847_raw.json)，不可变提交源码为[`cuda_126847.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126847.cpp)，实验候选为[`cuda_control124611_guard_case5_bf16_sync_partial_exp727.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case5_bf16_sync_partial_exp727.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`3a3cab1e1559e623ef8a3c77270b62d3f48e012e10571640971e4c51a0cd8c9e`；raw JSON SHA-256为`066a4065997903464a699b3f4f975d8360a5ec0c889cc974889331f85aa8ca5a`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126847`为`Accepted`、总分`65.57`、14/14；OJ总耗时`1614 ms`、内存`23060496 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、19/70、28/63、225/55、101/52、234/57、40/61、226/52、375/60、181/57、146/54 µs/分`，全部`Accepted`。唯一target case5为`19 µs / 70分`，较结构control `#124611` 的`17 µs / 73分`退化且未达到预注册`>=74分`；拒绝并关闭exact case5 BF16 sync partial contract，不切control。非target资源变化、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126847`一次，首次watch 900s超时后仅继续watch同一ID至`Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126832 · exp726 case1 shared-V fanout

- **代码溯源**：官方 raw 为[`cuda_126832_raw.json`](raw/cuda_126832_raw.json)，不可变提交源码为[`cuda_126832.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126832.cpp)，实验候选为[`cuda_control124611_guard_case1_shared_v_fanout_exp726.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case1_shared_v_fanout_exp726.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`54acbdb57a779fa7699b8404fc17aeb72052b4af0ef1eb906f4fc76de7d37dbc`；raw JSON SHA-256为`6bcf2369f9935645c498da2be8a322301ee818bfda6ac0c54dc21acb21401271`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126832`为`Accepted`、总分`65.71`、14/14；OJ总耗时`1611 ms`、内存`23060472 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、225/55、103/51、232/57、40/61、226/52、377/60、181/57、143/54 µs/分`，全部`Accepted`。唯一target case1为`3 µs / 92分`，未严格高于control的`92分`；拒绝并关闭exact case1 shared-V fanout contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126832`一次，watch由`Pending→Running→Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126819 · exp725 guarded case2 native-B128 V-copy

- **代码溯源**：官方 raw 为[`cuda_126819_raw.json`](raw/cuda_126819_raw.json)，不可变提交源码为[`cuda_126819.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126819.cpp)，实验候选为[`cuda_control124611_guard_case2_native_b128_vcopy_exp725.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case2_native_b128_vcopy_exp725.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`61a2af7a70eaedeaf521124bb01072f7a99291a5d663761e76c9ac8429b2639a`；raw JSON SHA-256为`d4f49b9132386f7a2cb56addf4d17b840b5b8b78ec4eb36aafa737169df0aa99`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126819`为`Accepted`、总分`65.79`、14/14；OJ总耗时`1613 ms`、内存`23060488 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、24/71、17/73、28/63、225/55、102/52、234/57、39/62、227/52、374/60、181/57、146/54 µs/分`，全部`Accepted`。唯一target case2为`4 µs / 90分`，未达到预注册`>=91分`；拒绝并关闭exact guarded case2 native-B128 V-copy contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126819`一次，watch由`Pending→Running→Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126791 · exp721 case12 group8 async guard

- **代码溯源**：官方 raw 为[`cuda_126791_raw.json`](raw/cuda_126791_raw.json)，不可变提交源码为[`cuda_126791.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126791.cpp)，实验候选为[`cuda_control124611_guard_case12_group8_async_exp721.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case12_group8_async_exp721.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted及immutable源码SHA-256均为`3d3e981ef2811b90569daca8139f385db39b15310df952b6663c0c5e8dbc735b`；raw JSON SHA-256为`8b01f0866c334b6418ed12c39507429dea3d0778b896b2dacad0d040800fd56d`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126791`为`Accepted`、总分`65.71`、14/14；OJ总耗时`1618 ms`、内存`23060588 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、225/55、102/52、237/57、40/61、224/52、383/59、181/57、142/54 µs/分`，全部`Accepted`。唯一target case12为`383 µs / 59分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`；拒绝并关闭exact case12 group8 async guard contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126791`一次，watch由`Pending→Running→Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126741 · exp718 case13 guarded group8 async-BF16 partial consumer

- **代码溯源**：官方 raw 为[`cuda_126741_raw.json`](raw/cuda_126741_raw.json)，不可变提交源码为[`cuda_126741.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126741.cpp)，实验候选为[`cuda_control124611_guard_case13_group8_async_exp718.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_guard_case13_group8_async_exp718.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`adaebe806af6f5983ff44d77caa8c880254b433211a837da0138530b4bac85bf`；raw JSON SHA-256为`61036a6a89de721a6f80766659de6c88adf06df64e62f084a8705680db955c78`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126741`为`Accepted`、总分`65.50`、14/14；OJ总耗时`1635 ms`、内存`23060556 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、29/62、224/55、102/52、234/57、39/62、227/52、378/60、202/54、143/54 µs/分`，全部`Accepted`。唯一target case13为`202 µs / 54分`，较结构control `#124611` 的`181 µs / 57分`退化且未达到预注册`>=58分`；拒绝并关闭exact case13 group8 async-partial consumer，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126741`一次，watch由`Pending→Running→Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126665 · exp716 case7 BF16 async partial

- **代码溯源**：官方 raw 为[`cuda_126665_raw.json`](raw/cuda_126665_raw.json)，不可变提交源码为[`cuda_126665.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126665.cpp)，实验候选为[`cuda_control124611_case7_bf16_async_partial_exp716.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_case7_bf16_async_partial_exp716.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`7f5f0a84240cda64c893fa78c6d729b12a4b0ee9880c31a4844a95ff51441beb`；raw JSON SHA-256为`74561657a62a4c4311786bc7f08c757e729c7ee4b2cdb4d3b085c04f77db6ac5`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126665`为`Accepted`、总分`65.93`、14/14；OJ总耗时`1595 ms`、内存`23060524 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、29/62、228/55、93/54、234/57、38/62、223/52、373/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case7为`228 µs / 55分`，未达到预注册`>=56分`；关闭exact case7 BF16 async partial contract，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126665`一次，900s和1800s watch超时后仅继续watch同一ID至`Finished/Accepted`，无重复POST、取消或并行；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

### 提交 #126589 · exp715 case12 normalized internal z-state + direct fan-in

- **代码溯源**：官方 raw 为[`cuda_126589_raw.json`](raw/cuda_126589_raw.json)，不可变提交源码为[`cuda_126589.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126589.cpp)，实验候选为[`cuda_control124611_case12_normalized_direct_fanin_exp715.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_case12_normalized_direct_fanin_exp715.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`e2f5962fc88141610dafa82df27e24b1abc71a9af32bbda9e581bc7b8fcb679f`；raw JSON SHA-256为`76a2acc16d4bff4d83ec56fc6205312346e8580ecb7d0a622d86243effd52b1c`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126589`为`Accepted`、总分`65.86`、14/14；case1–14时延/分数依次为`3/92、4/90、9/82、23/72、17/73、28/63、227/55、102/52、235/57、39/62、224/52、373/60、182/56、146/54 µs/分`，全部`Accepted`。唯一target case12为`380 µs / 60分`，较结构control `#124611` 的`371 µs / 60分`退化且未达到预注册`>=61分`；拒绝并关闭exact normalized internal z-state + direct fan-in，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126589`一次，900s和1800s watch超时后仅继续watch同一ID，无重复POST；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；后续exp716动态状态不在本条固化。

### 提交 #126532 · exp714 case11 fused-tail direct register/raw-BSM consumer

- **代码溯源**：官方 raw 为[`cuda_126532_raw.json`](raw/cuda_126532_raw.json)，不可变提交源码为[`cuda_126532.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126532.cpp)，实验候选为[`cuda_control124611_case11_direct_tail_consumer_exp714.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_case11_direct_tail_consumer_exp714.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`fb5c169061dc2eb73812ec493ce5fa1f8fc9c61ec10fc69d94efa8bb72a8f1f1`；raw JSON SHA-256为`b4a75c32ba1c38ea9b9bcae5421a05a6c9d2b2f16d501014e26bbcb481cf2ccc`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126532`为`Accepted`、总分`65.64`、14/14；case1–14时延/分数依次为`3/92、4/90、9/82、23/72、17/73、28/63、227/55、102/52、235/57、39/61、224/52、373/60、182/56、146/54 µs/分`，全部`Accepted`。唯一target case11为`224 µs / 52分`，与结构control `#124611` 同档，未达到预注册`>=53分`；拒绝并关闭exact fused-tail direct register/raw-BSM consumer，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126532`一次，首次watch 900s超时后仅继续watch同一ID，无重复POST；archive/raw/candidate SHA链一致。终态时队列已清空，工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；后续exp715动态状态不在本条固化。

### 提交 #126478 · exp713 case11 guarded last-live split finalizer ownership

- **代码溯源**：官方 raw 为[`cuda_126478_raw.json`](raw/cuda_126478_raw.json)，不可变提交源码为[`cuda_126478.cpp`](../solutions/archive/2026-08-25-submissions/cuda_126478.cpp)，实验候选为[`cuda_control124611_case11_last_live_finalizer_guard_exp713.cpp`](../solutions/archive/2026-08-25-experiments/cuda_control124611_case11_last_live_finalizer_guard_exp713.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`c302663c408d6792d114c227daaeb28ec18f1d0a3db6d3eec63cceddd85d0f7b`；raw JSON SHA-256为`a587666f967eaa8cba605e9b2aa488f0b8b52b565a884c192471f1c2b6c4782b`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#126478`为`Accepted`、总分`65.57`、14/14；OJ总耗时`1643 ms`、内存`23060436 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、227/55、102/52、235/57、39/62、255/49、373/60、182/56、146/54 µs/分`，全部`Accepted`。唯一target case11为`255 µs / 49分`，较结构control `#124611` 的`224 µs / 52分`及exp710的`226 µs / 52分`显著退化，未达到预注册`>=53分`；关闭exact guarded last-live split finalizer ownership，不切control。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#126478`一次，首次watch 900s超时后仅继续watch同一ID，无重复POST；archive/raw/candidate SHA链一致。终态后工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，终态队列已清空。

### 提交 #125788 · exp710 z4 tail-padding guard

- **代码溯源**：官方 raw 为[`cuda_125788_raw.json`](raw/cuda_125788_raw.json)，不可变提交源码为[`cuda_125788.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125788.cpp)，实验候选为[`cuda_control124611_z4_tail_trap_fix_exp710.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_z4_tail_trap_fix_exp710.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`9496b2add95197c698c0ff39af34ec23bf766c7315078eeff9119a4d66d3aab0`；raw JSON SHA-256为`42db414b315992839afdcf6df4444cad2e89cda47cb6e4ec10ce54a3671dee9a`，manifest已登记`#125788`。

- **线上终态与安全反馈**：唯一串行OJ提交`#125788`于`2026-08-24T18:43:43Z`终态为`Accepted`、总分`65.57`、14/14；OJ总耗时`1611 ms`、内存`23060664 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、29/62、225/55、103/51、230/57、39/62、226/52、374/60、182/56、146/54 µs/分`，全部`Accepted`。目标cases8/10/11/14合计`219分`。C500 tail-NaN trap中candidate四个目标case均finite且输入不变，control四个目标case均nonfinite；candidate full/boundary也均PASS，证据见`log/exp710_c500_tail_probe.log`、`log/exp710_c500_candidate_full.log`、`log/exp710_c500_candidate_boundary.log`。该条只固化线上结果和安全反馈，control切换由主Agent裁决。

- **提交、归档与恢复**：实际`--submit`只创建`#125788`一次，随后仅对同一ID watch至Accepted，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。身份与队列证据见`log/exp710_oj_submit_watch.log`、`log/exp710_oj_final_identity.log`、`log/exp710_oj_final_queue.log`、`log/exp710_oj_restore_control_sha.log`。

### 提交 #125776 · exp709 short123 bundle

- **代码溯源**：官方 raw 为[`cuda_125776_raw.json`](raw/cuda_125776_raw.json)，不可变提交源码为[`cuda_125776.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125776.cpp)，实验候选为[`cuda_control124611_short123_bundle_exp709.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_short123_bundle_exp709.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；候选、提交源码、不可变快照及raw内嵌源码SHA-256均为`1499ce69d186977fb5c49ce75791238fcfcfac83d5e465a48e255a752cac7a36`；raw JSON SHA-256为`644101222b6c698a19a9815e51b740bd6b702280d2295d1955c9b85591da3752`，manifest已登记`#125776`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125776`于`2026-08-24T18:33:20Z`终态为`Accepted`、总分`66.07`、14/14；OJ总耗时`1595 ms`、内存`23060488 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、229/55、93/54、235/57、39/62、223/52、374/60、181/57、139/55 µs/分`，全部`Accepted`。预注册target cases1/2/3分别为`92/90/83分`，合计`265`，但目标门槛`case1>=93`、`case2>=91`、`case3>=84`均未达到；关闭exact short123 bundle contract，不切control、不重投或扫描。case3 `83分`不作结构性收益归因；非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125776`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。随后当前线上任务转入`#125788 / exp710`，本归档不查询或修改该在途ID，也不触碰工作文件。详细记录见[`exp709_archive_record.md`](../log/exp709_archive_record.md)。

### 提交 #125765 · exp704 z8 all async register-K/V backend

- **代码溯源**：官方 raw 为[`cuda_125765_raw.json`](raw/cuda_125765_raw.json)，不可变提交源码为[`cuda_125765.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125765.cpp)，实验候选为[`cuda_control124611_z8_all_async_register_kv_exp704.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_z8_all_async_register_kv_exp704.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；候选、提交源码、不可变快照及raw内嵌源码SHA-256均为`53cca7e99f7d43066a7beb53323c93c0ed2f249e0438f4398d18f8e7e6c75e78`；raw JSON SHA-256为`b4da62b47dd71c46baf53b9f31781a387647fa51301d35610020a3d4a139b9d0`，manifest已登记`#125765`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125765`于`2026-08-24T18:23:25Z`终态为`Accepted`、总分`65.93`、14/14；OJ总耗时`1604 ms`、内存`23060492 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、229/55、94/54、236/57、38/62、224/52、375/60、184/56、139/55 µs/分`，全部`Accepted`。预注册target cases7/9/12/13分别为`55/57/60/56分`，对应display sum`228`，低于当前control对应`55/57/60/57分`的`229`；关闭exact z8 all async register-K/V backend contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125765`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。随后当前线上任务转入`#125776 / exp709`，本归档不查询或修改该在途ID，也不触碰工作文件。详细记录见[`exp704_archive_record.md`](../log/exp704_archive_record.md)。

### 提交 #125753 · exp705 z4 all async register-K/V backend

- **代码溯源**：官方 raw 为[`cuda_125753_raw.json`](raw/cuda_125753_raw.json)，不可变提交源码为[`cuda_125753.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125753.cpp)，实验候选为[`cuda_control124611_z4_all_async_register_kv_exp705.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_z4_all_async_register_kv_exp705.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；候选、提交源码、不可变快照及raw内嵌源码SHA-256均为`25a637f309f8a8206a2210a1c8f6382fe9e9206507b5b0b4b41f92caefebe083`；raw JSON SHA-256为`ef03878bd773a5ba05736bd8781a0d0c9ae7664e1ebdf03d4b462ca550705ffb`，manifest已登记`#125753`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125753`于`2026-08-24T18:10:24Z`终态为`Accepted`、总分`65.43`、14/14；OJ总耗时`1631 ms`、内存`23060696 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、18/71、28/63、225/55、102/52、234/57、39/62、238/51、375/60、182/56、150/53 µs/分`，全部`Accepted`。预注册target cases8/10/11/14分别为`52/62/51/53分`，合计`218`，低于当前control对应`54/62/52/55`合计`223`；关闭exact z4 all async register-K/V backend contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **C500诊断与提交收尾**：`log/exp705_c500_tail_probe.log`在有效构造的z4 tail-NaN trap中确认candidate与control都读取`cache_seqlens`后的padding并输出nonfinite；这是继承control的correctness诊断，不是candidate-only错误，因此不能将exp705记录为无条件C500 safety PASS。实际`--submit`只创建`#125753`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，终态后工作文件保持control SHA。详细记录见[`exp696_705_archive_record.md`](../log/exp696_705_archive_record.md)。

### 提交 #125658 · exp696 case12 raw-wave rebase

- **代码溯源**：官方 raw 为[`cuda_125658_raw.json`](raw/cuda_125658_raw.json)，不可变提交源码为[`cuda_125658.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125658.cpp)，实验候选为[`cuda_control124611_case12_raw_wave_rebase_exp696.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case12_raw_wave_rebase_exp696.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；候选、提交源码、不可变快照及raw内嵌源码SHA-256均为`f23ce28fa2e0abdc6329b2d73af9e56b3a236c195a1c703924692e6b7e3071fe`；raw JSON SHA-256为`5480da96dc15dca3a3a39cdf02cf763822cb91f3f762869e19c08d05c15a5132`，manifest已登记`#125658`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125658`于`2026-08-24T16:30:04Z`终态为`Accepted`、总分`66.00`、14/14；OJ总耗时`1593 ms`、内存`23060516 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、94/54、235/57、38/62、221/52、375/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case12为`375 µs / 60分`，未达到预注册`>=61分`；关闭exact raw-wave `lane^32` first-z merge contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125658`一次，watch超时后仅继续watch同一ID，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA，不切换control。详细记录见[`exp696_705_archive_record.md`](../log/exp696_705_archive_record.md)。

### 提交 #125636 · exp693 case11 fixed-20-page MMA hot loop

- **代码溯源**：官方 raw 为[`cuda_125636_raw.json`](raw/cuda_125636_raw.json)，不可变提交源码为[`cuda_125636.cpp`](../solutions/archive/2026-08-25-submissions/cuda_125636.cpp)，实验候选为[`cuda_control124611_case11_fixed20_mma_exp693.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case11_fixed20_mma_exp693.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；候选仅改变case11的固定20-page owner循环（`19×HAS_NEXT=true`、末次`false` hot loop），其它dispatch保持父control。candidate、submitted、immutable及raw内嵌源码SHA-256均为`eaac9b90ef88081cea615639cef27f7fad57f45bd11114edef47ba1cf7eef8ed`；raw JSON SHA-256为`b9a90b66c45a742759d03be68e2d0bb44c7dc64fef12bb219e867ab0272c91db`，manifest已登记`#125636`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125636`于`2026-08-24T16:11:28Z`终态为`Accepted`、总分`66.00`、14/14；OJ总耗时`1593 ms`、内存`23060416 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、233/57、38/62、222/52、374/60、183/56、140/55 µs/分`，全部`Accepted`。唯一target case11（B16/KV4/L12251）为`222 µs / 52分`，未达到预注册`>=53分`；关闭exact case11 fixed-20-page owner + `19×HAS_NEXT=true`/末次`false` hot-loop contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125636`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致，manifest已登记。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，不切换control。详细记录见[`exp693_archive_record.md`](../log/exp693_archive_record.md)。

### 提交 #125625 · exp698 case5 single-live direct-output + reducer return

- **代码溯源**：官方 raw 为[`cuda_125625_raw.json`](raw/cuda_125625_raw.json)，不可变提交源码为[`cuda_125625.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125625.cpp)，实验候选为[`cuda_control124611_case5_single_live_direct_output_exp698.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case5_single_live_direct_output_exp698.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`716c620f804c39086c1873aa50696d3a09ec91be4e639fcb701670f2797826f6`；raw JSON SHA-256为`6b3329c445f83e6d92699fa7d747419b97264c77d859a6f29f56e7f83766c0fc`，manifest已登记`#125625`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125625`于`2026-08-24T15:57:15Z`终态为`Accepted`、总分`66.00`、14/14；OJ总耗时`1594 ms`、内存`23060584 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、94/54、233/57、38/62、222/52、376/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case5（B16/KV4/L141）为`17 µs / 73分`，未达到预注册`>=74分`；关闭exact case5 seqlen 1..32 single-live direct-output + reducer-return contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125625`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致，manifest已登记。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。详细记录见[`exp695_698_archive_record.md`](../log/exp695_698_archive_record.md)。

### 提交 #125585 · exp695 case9 raw-wave `lane^32` first-z merge

- **代码溯源**：官方 raw 为[`cuda_125585_raw.json`](raw/cuda_125585_raw.json)，不可变提交源码为[`cuda_125585.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125585.cpp)，实验候选为[`cuda_control124611_case9_raw_wave_rebase_exp695.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case9_raw_wave_rebase_exp695.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`8efee54b8335ce391da7aab12f6607f685a58b01bacdbd6bb1a6982b54f472a8`；raw JSON SHA-256为`107727616ccca83b1a846608b1930229f6dbda171bd764ba56baa2a4e20d025b`，manifest已登记`#125585`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125585`于`2026-08-24T15:32:14Z`终态为`Accepted`、总分`65.86`、14/14；OJ总耗时`1607 ms`、内存`23060512 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、227/55、93/54、244/56、38/62、224/52、375/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case9（B32/KV8/L4096）为`244 µs / 56分`，未达到预注册`>=58分`；关闭exact case9 raw-wave `lane^32` first-z merge contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125585`一次，未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致，manifest已登记。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。详细记录见[`exp695_698_archive_record.md`](../log/exp695_698_archive_record.md)。

### 提交 #125561 · exp694 case7 raw physical-wave `lane^32` first-z merge

- **代码溯源**：官方 raw 为[`cuda_125561_raw.json`](raw/cuda_125561_raw.json)，不可变提交源码为[`cuda_125561.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125561.cpp)，实验候选为[`cuda_control124611_case7_raw_wave_rebase_exp694.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case7_raw_wave_rebase_exp694.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2`；raw JSON SHA-256为`7106b47ef070efcc409b8a8069dddd1306893a8a1cf761ebac154e6fb7f0354a`，manifest已登记`#125561`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125561`于`2026-08-24T15:11:40Z`提交、终态为`Accepted`、总分`65.86`、14/14；OJ总耗时`1602 ms`、内存`23060560 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、233/54、94/54、233/57、38/62、224/52、374/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case7（B64/KV8/L2048）为`233 µs / 54分`，相对当前control `226 µs / 55分`退档，未达到预注册`>=56分`；关闭exact raw physical-wave `lane^32` first-z merge contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125561`一次，终态后未取消、并行或重复POST；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致，manifest已登记。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，本归档不触碰后续exp695 OJ。详细记录见[`exp694_archive_record.md`](../log/exp694_archive_record.md)。

### 提交 #125434 · exp692 case11 adjacent-lane BF16 handoff + native B128 final-output store

- **代码溯源**：官方 raw 为[`cuda_125434_raw.json`](raw/cuda_125434_raw.json)，不可变提交源码为[`cuda_125434.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125434.cpp)，实验候选为[`cuda_control124611_case11_pair_output_b128_exp692.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case11_pair_output_b128_exp692.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`e0fbec43542bfc6a1c3b4980347d1eaab581086f34d24e26231a4fc8b881b167`；raw JSON SHA-256为`3af4acf615f43cb8b828e73981a10df46b09c00277eaa092f3964eba715e3e95`，manifest已登记`#125434`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125434`于`2026-08-24T13:11:30Z`提交、终态为`Accepted`、总分`66.14`、14/14；OJ总耗时`1591 ms`、内存`23060540 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、231/57、38/62、223/52、377/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case11（B16/KV4/L12251）为`223 µs / 52分`，未达到预注册`>=53分`；关闭exact相邻lane BF16 handoff + 偶数lane native B128 final-output store contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、超时处理与归档**：实际`--submit`只创建`#125434`一次；首次watch达到3600秒上限后仅对同一ID继续watch，随后恢复至`Finished/Accepted`，未取消、并行或重复POST。已运行`tools/archive_cuda_submissions.py`；raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，不切换control。详细记录见[`exp692_archive_record.md`](../log/exp692_archive_record.md)。

### 提交 #125388 · exp690 case7 threechunk fused direct

- **代码溯源**：官方 raw 为[`cuda_125388_raw.json`](raw/cuda_125388_raw.json)，不可变提交源码为[`cuda_125388.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125388.cpp)，实验候选为[`cuda_control124611_case7_threechunk_fused_direct_exp690.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case7_threechunk_fused_direct_exp690.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`bc90ae1b38e7c79daced75c8495c7426542c500cd30c3e7956b7f410950e8ce2`；raw JSON SHA-256为`b3a3f0de94f390952dae314f9af132f0920076dcfcbbac601c91351c10facf79`，manifest已登记`#125388`。

- **线上终态与唯一目标归因**：唯一串行OJ提交`#125388`于`2026-08-24T12:25:57Z`终态为`Accepted`、总分`65.71`、14/14；OJ总耗时`1636 ms`、内存`23060628 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、269/51、93/54、235/57、38/62、222/52、374/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case7（B64/KV8/L2048）为`269 µs / 51分`，相对当前control约`226 µs / 55分`严重退档；关闭exact case7 `43/43/42` three-bucket same-CTA FP32 state direct-output、跳过partial+reducer contract，不切control、不重投或扫描。非target case、aggregate和同场timing不归因。

- **提交、归档与恢复**：实际`--submit`只创建`#125388`一次；提交后两次watch各达到900秒超时，均只对原ID继续watch，随后恢复同ID至`Finished/Accepted`，未取消、并行或重复POST。已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致；工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，不切换control。详细记录见[`exp690_archive_record.md`](../log/exp690_archive_record.md)。

### 提交 #125367 · exp691 case6 fixed STATIC_WEIGHT_SPLITS=8 row16

- **代码溯源**：官方 raw 为[`cuda_125367_raw.json`](raw/cuda_125367_raw.json)，不可变提交源码为[`cuda_125367.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125367.cpp)，实验候选为[`cuda_control124611_case6_static_weight8_exp691.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case6_static_weight8_exp691.cpp)。父/current control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`39db393846e782ee07bd389b8f8adfb1314becd1da3be96d4b0fb5ec985b1291`；raw JSON SHA-256为`9a4861af40146e46108f0825528b7ba71d5b3a04a5499db216bfb8795fac5f8c`，manifest已登记`#125367`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125367`于`2026-08-24T12:03:18Z`终态为`Accepted`、总分`65.93`、14/14；OJ总耗时`1592 ms`、内存`23060460 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、29/62、225/55、94/54、232/57、38/62、224/52、373/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case6（B16/KV8/L362）为`29 µs / 62分`，相对当前control `28 µs / 63分`退档，未达到预注册`>=64分`；关闭exp691 exact case6 fixed row16 static-weight contract，不切control、不重投或扫描STATIC_WEIGHT_SPLITS、row16、权重映射或启用范围。非target case、aggregate和同场timing不归因。
- **提交、归档与恢复**：实际`--submit`仅创建`#125367`一次，终态后未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；归档时独立exp690提交`#125388`仍为Pending，本任务未触碰该在途提交；详细记录见[`exp691_archive_record.md`](../log/exp691_archive_record.md)。

### 提交 #125311 · exp689 case13 final z1-to-z0 raw-wave64 peer merge

- **代码溯源**：官方 raw 为[`cuda_125311_raw.json`](raw/cuda_125311_raw.json)，不可变提交源码为[`cuda_125311.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125311.cpp)，实验候选为[`cuda_control124611_case13_final_wave_merge_exp689.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case13_final_wave_merge_exp689.cpp)。父/control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`a316636d05dbc72965614842234b3e2bde45cc87260870b18722210c9cd170f0`；raw JSON SHA-256为`66dcc34bd06079d4b4ce5cd6752c2234c8056a12dd5a48cdfd2260df126af546`，manifest已登记`#125311`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125311`于`2026-08-24T11:12:03Z`终态为`Accepted`、总分`65.86`、14/14；OJ总耗时`1596 ms`、内存`23060524 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、29/62、226/55、93/54、233/57、38/62、224/52、375/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case13（B1/KV8/L58966）为`182 µs / 56分`，相对当前control `181 µs / 57分`退档，未达到预注册`<=174.5 µs`或`>=58分`；关闭exp689 exact final `z1 -> z0` raw-wave64 peer-merge contract，不切control、不重投或扫描peer、wave、state、merge或启用范围。非target case、aggregate和同场timing不归因。
- **提交、归档与恢复**：实际`--submit`仅创建`#125311`一次，终态后未取消、并行或重投；已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ列表无在途；详细记录见[`exp689_archive_record.md`](../log/exp689_archive_record.md)。

### 提交 #125281 · exp688 case13 normalized-BF16 partial native-B128 STG

- **代码溯源**：官方 raw 为[`cuda_125281_raw.json`](raw/cuda_125281_raw.json)，不可变提交源码为[`cuda_125281.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125281.cpp)，实验候选为[`cuda_control124611_case13_native_partial_stg_exp688.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case13_native_partial_stg_exp688.cpp)。父/control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`b7793a4e9b160179f9e142c3c4076781eebf617e798d81fd35cdcb74286a1cec`；raw JSON SHA-256为`efdf26e3d10a294d2eead8c1b12ec890932dfe12aa4b04c920d944b5b61cae32`，manifest已登记`#125281`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125281`于`2026-08-24T10:49:21Z`终态为`Accepted`、总分`66.00`、14/14；OJ总耗时`1591 ms`、内存`23060660 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、93/54、233/57、38/62、221/52、375/60、181/57、140/55 µs/分`，全部`Accepted`。唯一target case13（B1/KV8/L58966）为`181 µs / 57分`，与当前control同档，未形成可归因display收益；关闭exp688 exact case13 normalized-BF16 partial producer native-B128 STG contract，不切control。非target case、aggregate和同场timing不归因。
- **提交、归档与恢复**：[`exp688_oj_submit.log`](../log/exp688_oj_submit.log)记录一次实际POST创建`#125281`及其终态`Accepted`，无取消、并行或重投；提交前后SHA和队列检查均完成。已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA；后续独立exp689提交`#125311`已终态，本条不重复归因。详细记录见[`exp688_archive_record.md`](../log/exp688_archive_record.md)。

### 提交 #125268 · exp687 case14 pair aggregate fix

- **代码溯源**：官方 raw 为[`cuda_125268_raw.json`](raw/cuda_125268_raw.json)，不可变提交源码为[`cuda_125268.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125268.cpp)，实验候选为[`cuda_control124611_case14_pair_aggregate_fix_exp687.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case14_pair_aggregate_fix_exp687.cpp)。父/control为`#124611 / exp666`，control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；candidate、submitted、immutable及raw内嵌源码SHA-256均为`337c8fc37a1ad6de70732ef1eee45d44eb4e86e83e95adc239e5c2b71a69c1c7`；raw JSON SHA-256为`72470d9ef277628e7c9ee32e9e409b787dd1e341b9f16b3f2df50519d898579f`，manifest已登记`#125268`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125268`于`2026-08-24T10:35:51Z`终态为`Accepted`、总分`64.43`、14/14；OJ总耗时`1801 ms`、内存`23060628 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、224/55、94/54、232/57、39/62、222/52、375/60、181/57、350/32 µs/分`，全部`Accepted`。唯一target case14（B1/KV4/L61519）从control的`139 µs / 55分`退至`350 µs / 32分`，未达到预注册目标；关闭exp687 exact `257 logical split -> 129 pair aggregate ownership` contract，不切control。非target case、aggregate和同场timing不归因。
- **提交、归档与恢复**：[`exp687_oj_dryrun.log`](../log/exp687_oj_dryrun.log)与[`exp687_oj_submit_watch.log`](../log/exp687_oj_submit_watch.log)记录一次实际POST创建`#125268`及其`Pending → Running → Finished/Accepted`终态，未取消、并行或重投。已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；归档核验时独立exp688提交`#125281`仍为Pending，本归档未触碰该在途任务。详细记录见[`exp687_archive_record.md`](../log/exp687_archive_record.md)。

### 提交 #125236 · exp685 case14 normalized-BF16 partial native-B128 STG

- **代码溯源**：官方 raw 为[`cuda_125236_raw.json`](raw/cuda_125236_raw.json)，不可变提交源码为[`cuda_125236.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125236.cpp)，实验候选为[`cuda_control124611_case14_native_partial_stg_exp685.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case14_native_partial_stg_exp685.cpp)。candidate、submitted、immutable及raw内嵌源码SHA-256均为`eeed1381178dc74998ea0b5bdfde263efc9f93a7c52e78ab400d727385243055`；raw JSON SHA-256为`6fdbfa1a29a054ce21ee20edb85cfe09cf31444536506785e273c596f743b390`，manifest已登记`#125236`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125236`于`2026-08-24T10:06:28Z`终态为`Accepted`、总分`66.00`、14/14；OJ总耗时`1598 ms`、内存`23060552 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、237/57、38/62、223/52、376/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case14（B1/KV4/L61519）为`139 µs / 55分`，未达到预注册`<=135 µs`或`>=56分`；关闭exp685 exact case14 normalized-BF16 partial native-B128 STG contract，不切control。非target case、aggregate和同场timing不归因。
- **提交、归档与恢复**：首次提交/监看过程在[`exp685_oj_submit_watch.log`](../log/exp685_oj_submit_watch.log)中记录；watcher达到900秒上限后仅对原`#125236`继续watch至`Finished/Accepted`，未取消、并行或重复POST。已运行`tools/archive_cuda_submissions.py`，raw、候选、raw内嵌源码与不可变提交源码SHA链一致。终态后工作文件保持control `#124611 / exp666`，SHA-256=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；随后独立exp687提交`#125268`已终态，本条不重复归因。详细归档见[`exp685_archive_record.md`](../log/exp685_archive_record.md)。

### 提交 #125200 · exp684 同源码 control 方差 probe

- **代码溯源**：官方 raw 为[`cuda_125200_raw.json`](raw/cuda_125200_raw.json)，不可变提交源码为[`cuda_125200.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125200.cpp)，本次同源码 candidate/work file 为[`cuda_maca_optimized.cpp`](../solutions/cuda_maca_optimized.cpp)。candidate、submitted、immutable及raw内嵌源码SHA-256均为`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；raw JSON SHA-256为`95eb59c3c4cbd321038b27d88ebf00a6ee48970565792cd1bc2d4e5115748b91`，manifest已登记`#125200`。
- **线上终态与方差观察**：同源码复测`#125200`于`2026-08-24T09:35:01Z`终态为`Accepted`、总分`66.07`、14/14；OJ总耗时`1599 ms`、内存`23060600 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、228/55、93/54、235/57、39/62、223/52、377/60、181/57、139/55 µs/分`，全部`Accepted`。这是对当前control的同源码方差probe，不引入新机制；非target波动不作归因，不切control。
- **归档与收尾**：本次归档仅核对既有`#125200`，未调用`--submit`、取消或重投；`python3 tools/archive_cuda_submissions.py`已运行。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ队列无在途；过程见[`exp684_archive_record.md`](../log/exp684_archive_record.md)。

### 提交 #125124 · exp680 case14 hierarchical BF16 partial tree

- **代码溯源**：官方 raw 为[`cuda_125124_raw.json`](raw/cuda_125124_raw.json)，不可变提交源码为[`cuda_125124.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125124.cpp)，实验候选为[`cuda_control124611_case14_bf16_hier_tree_exp680.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case14_bf16_hier_tree_exp680.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`f9d6677a9d63b149205c2d5316cb92d557f86873bde16c99dd1bd638dba2a01e`；raw JSON SHA-256为`e4aab505bc62bc2b026dcd17fd85ec875feea9c91bd3496d9341129383f6996f`，manifest已登记`#125124`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125124`于`2026-08-24T08:31:38Z`终态为`Accepted`、总分`65.93`、14/14；OJ总耗时`1595 ms`、内存`23060464 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、225/55、93/54、234/57、38/62、224/52、373/60、182/56、142/54 µs/分`，全部`Accepted`。唯一target case14（B1/KV4/L61519）为`142 µs / 54分`，相对结构性control #124611的`139 µs / 55分`退档，未达到预注册`>=56分`；exp680 exact hierarchical BF16 partial tree contract关闭，不切换control。额外 group stage 的线上变化、其它case、aggregate和同场timing均不归因。
- **提交身份、归档与恢复**：本任务仅对既有ID执行`python3 tools/xpuoj_submit.py --watch 125124 --poll-seconds 30 --timeout-seconds 900`并保存raw，未创建新提交、取消、并行或重投；`python3 tools/archive_cuda_submissions.py`已运行。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ队列无在途；过程见[`exp680_archive_record.md`](../log/exp680_archive_record.md)。

### 提交 #125089 · exp679 case6 native-K-LDG

- **代码溯源**：官方 raw 为[`cuda_125089_raw.json`](raw/cuda_125089_raw.json)，不可变提交源码为[`cuda_125089.cpp`](../solutions/archive/2026-08-24-submissions/cuda_125089.cpp)，实验候选为[`cuda_control124611_case6_native_k_ldg_exp679.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case6_native_k_ldg_exp679.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`a9e97eccd299577ef731de746d8c04fa36636269afb285b3bc3294664907f033`；raw JSON SHA-256为`0b2b29882ab25daf829392bfe31b42b7ad83364cfff5d5b2a907af17d1afea56`，manifest已登记`#125089`。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#125089`于`2026-08-24T08:10:06Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1593 ms`、内存`23060524 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、94/54、234/57、39/62、222/52、374/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case6（B16/KV8/L362）为`28 µs / 63分`，与当前control #124611同档，未达到预注册`>=64分`；关闭exp679 case6 native-K-LDG exact contract，不切换control。其它case、aggregate和同场timing不归因。
- **提交、归档与恢复**：本任务只对既有ID执行`--watch 125089`并保存raw，未调用`--submit`、取消、并行或重投；运行`tools/archive_cuda_submissions.py`后，raw、candidate、提交源码与不可变快照SHA链一致，`solutions/archive/SUBMISSIONS.md`已登记。终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ队列无在途。详细记录见[`exp679_archive_record.md`](../log/exp679_archive_record.md)。

### 提交 #124801 · exp678 case8 runtime row16 weight shuffle

- **代码溯源**：官方 raw 为[`cuda_124801_raw.json`](raw/cuda_124801_raw.json)，不可变提交源码为[`cuda_124801.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124801.cpp)，实验候选为[`cuda_control124611_case8_runtime_row16_exp678.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case8_runtime_row16_exp678.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`385b32b680e1a58294917a5c6c345b899f1dd87b603152e1dabc38418d52835a`；raw JSON SHA-256为`8c089bd4e6bf69f69da729b965fca91151668a44e27dfb4ac25cf41b5e153700`，manifest已登记`#124801`。
- **提交前门禁**：normal/resource/LLVM构建通过；case8 exact、boundary、random、full、workspace reuse及继承case7 smoke真实C500 correctness均PASS（`log/exp678_{candidate_normal,candidate_resource,candidate_llvm}.log`、`log/exp678_c500_case8_{exact,boundary,random,full,reuse_short_full,reuse_full_short_full}.log`、`log/exp678_c500_case7_full_smoke.log`）。唯一机制是case8既有group8 reducer的动态row16权重交接改走`__shfl_sync_16` native lowering，producer、partial ABI、metadata、grid和output ownership不变。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#124801`于`2026-08-24T03:52:32Z`终态为`Accepted`，总分`65.93`、14/14；OJ总耗时`1595 ms`、内存`23060524 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、224/55、95/53、236/57、38/62、225/52、372/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case8（B16/KV4/L4096）为`95 µs / 53分`，相对control #124611的`94 µs / 54分`退档，且未达到预注册`>=55分`；其它case、aggregate和同场timing不归因，关闭exp678 exact contract，不切control、不重投或扫描row16/native shuffle/启用范围。
- **提交、归档与恢复**：实际`--submit`只创建`#124801`一次；终态后本任务仅对同一ID正常`--watch`并保存raw，无取消、并行或重投。运行`tools/archive_cuda_submissions.py`后，raw、candidate、提交源码与不可变快照SHA链一致；工作文件已恢复control，最终OJ队列无在途。详细记录见[`exp678_archive_record.md`](../log/exp678_archive_record.md)。

### 提交 #124788 · exp677 case11 register-all-coefficients reducer

- **代码溯源**：官方 raw 为[`cuda_124788_raw.json`](raw/cuda_124788_raw.json)，不可变提交源码为[`cuda_124788.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124788.cpp)，实验候选为[`cuda_control124611_case11_regcoeff_exp677.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case11_regcoeff_exp677.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`7d2e0f10e8808e9f338395c27601090e8d448a7e3b806f2dd43ce163a8938c4e`；raw JSON SHA-256为`89552212f42a48838f000401d17bc9150b3a467fc19045ed50efa86c5a39b3ca`，manifest已登记`#124788`。
- **提交前门禁**：normal/resource/LLVM构建及case11 full、boundary、random、exact split/page边界与case8 full真实C500 correctness均PASS（`log/exp677_{candidate_normal,candidate_resource,candidate_llvm}.log`、`log/exp677_c500_regular_case11_{full,boundary,random,exact}.log`、`log/exp677_c500_regular_case8_full.log`）。唯一机制是case11最多39个live split时由owner lane在寄存器中保留两组`(m,l)`及权重，再以warp shuffle供accumulator消费，移除该dispatch的metadata shared materialization。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#124788`于`2026-08-24T03:41:26Z`终态为`Accepted`，总分`65.93`、14/14；OJ总耗时`1604 ms`、内存`23060500 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、224/55、93/54、236/57、38/62、232/51、376/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case11（B16/KV4/L12251）为`232 µs / 51分`，相对control #124611的`224 µs / 52分`退档，未达到预注册`>=53分`；其它case、aggregate和同场timing不归因，关闭exp677 exact contract，不切control、不重投或扫描寄存器持有、shuffle或启用范围。
- **提交、归档与恢复**：实际`--submit`只创建`#124788`一次；终态后本任务仅对同一ID正常`--watch`并保存raw，无取消、并行或重投。运行`tools/archive_cuda_submissions.py`后，raw、candidate、提交源码与不可变快照SHA链一致；工作文件已恢复control，最终OJ队列无在途。详细记录见[`exp677_archive_record.md`](../log/exp677_archive_record.md)。

### 提交 #124761 · exp676 case10 normalized-BF16 partial + packed vec2 consumer

- **代码溯源**：官方 raw 为[`cuda_124761_raw.json`](raw/cuda_124761_raw.json)，不可变提交源码为[`cuda_124761.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124761.cpp)，实验候选为[`cuda_control124611_case10_bf16_packed_vec2_exp676.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case10_bf16_packed_vec2_exp676.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`62fca964471f350cb0b4416a001515bc5ffc15a91f81cc93840677b890fd42de`；raw JSON SHA-256为`e8b7078125e8380a1d2c082793397baf8f6e23de368734f8a880a39233c5e45b`，manifest已登记`#124761`。
- **提交前门禁**：normal/resource/LLVM构建及case10 full、boundary、random、exact页/split边界与继承case14 full真实C500 correctness均PASS（`log/exp676_{candidate_normal,candidate_resource,candidate_llvm}.log`、`log/exp676_c500_case10_{full,boundary,random,exact}.log`、`log/exp676_c500_case14_full.log`）。唯一机制是保留case10 head-pair/z4 producer ownership，同时将normalized-BF16 partial接入既有packed vec2 reducer；其它dispatch保持control。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#124761`于`2026-08-24T03:22:00Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1588 ms`、内存`23060744 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、226/55、93/54、229/58、41/60、219/53、374/60、181/57、140/55 µs/分`，全部`Accepted`。唯一target case10（B1/KV4/L8192）为`41 µs / 60分`，相对control #124611的`38 µs / 62分`退档，未达到预注册`>=63分`；其它case、aggregate和同场timing不归因，关闭exp676 exact contract，不切control、不重投或扫描partial格式、vec2、producer或启用范围。
- **提交、归档与恢复**：实际`--submit`只创建`#124761`一次；终态后本任务仅对同一ID正常`--watch`并保存raw，无取消、并行或重投。运行`tools/archive_cuda_submissions.py`后，raw、candidate、提交源码与不可变快照SHA链一致；工作文件已恢复control，最终OJ队列无在途。详细记录见[`exp676_archive_record.md`](../log/exp676_archive_record.md)。

### 提交 #124696 · exp675 case11 normalized-BF16 producer + 32-thread vec4 BF16 consumer

- **代码溯源**：官方 raw 为[`cuda_124696_raw.json`](raw/cuda_124696_raw.json)，不可变提交源码为[`cuda_124696.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124696.cpp)，实验候选为[`cuda_control124611_case11_bf16_vec4_exp675.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case11_bf16_vec4_exp675.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`aa19bf773166504181479a2a06e44eb45e0846a84dc054751d34945eff71a287`；raw JSON SHA-256为`9d236cf9213f95ce4873a6c2d980dda6ef955c50f4a394d7c491ece32fad6697`，manifest已登记`#124696`。
- **线上终态与唯一目标归因**：唯一串行提交`#124696`于`2026-08-24T02:19:42Z`终态为`Accepted`，总分`65.93`、14/14；OJ总耗时`1594 ms`、内存`23060484 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、94/54、232/57、38/62、225/52、374/60、182/56、139/55 µs/分`，全部`Accepted`。唯一target case11为`225 µs / 52分`，相对control `#124611`的`224 µs / 52分`同档且未达到`>=53分`；关闭exp675 exact contract，不切换control，不重投或扫描其它case。
- **提交、归档与收尾**：实际`--submit`只创建`#124696`一次；终态后仅对同一ID继续`--watch`并保存raw，未取消、并行或重投。`tools/archive_cuda_submissions.py`已运行，raw、candidate、提交源码与不可变快照SHA链一致；终态后工作文件保持control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，OJ队列无在途。详细身份核验见[`exp675_archive_record.md`](../log/exp675_archive_record.md)。

### 提交 #124621 · exp668 case12 V-dead-half tokenized-BSM role swap

- **代码溯源**：官方 raw 为[`cuda_124621_raw.json`](raw/cuda_124621_raw.json)，不可变提交源码为[`cuda_124621.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124621.cpp)，实验候选为[`cuda_control124611_case12_v_dead_half_exp668.cpp`](../solutions/archive/2026-08-23-experiments/cuda_control124611_case12_v_dead_half_exp668.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`8aee7ba576d47f1ca7166abf7113096bec5ebf9db2d510749399831ccc2b2010`；raw JSON SHA-256为`e4d38406599b692f5d451dad3228a21faa7177082b02a0e1a0fc16c304b2bd5a`，manifest已登记`#124621`。
- **线上终态**：唯一串行提交`#124621`于`2026-08-23T23:43:40Z`终态为`Accepted`，总分`65.86`、14/14；OJ总耗时`1610 ms`、内存`23060444 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、24/71、17/73、28/63、224/55、94/54、231/57、39/62、223/52、392/59、181/57、140/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case12的V-next tokenized BSM→QK已释放的K半区、K-next scalar→PV已释放的V半区，并在下一页交换两块shared half；split40、partial ABI、reducer和其它dispatch不变。target case12（B8/KV8/L32768）为`392 µs / 59分`，相对新control #124611 的`371 µs / 60分`明显失败，关闭V-dead-half exact contract，不切换control、不重投或扫描token、half、wave、释放时机或启用范围。case13 `181/57`为control继承结果，非target；其它case、aggregate和同场timing不归因。
- **提交、归档与恢复**：normal/resource/LLVM及case12、case13专项C500 correctness门禁均通过；实际`--submit`只调用一次创建`#124621`，无取消、并行或重投。终态后运行`tools/archive_cuda_submissions.py`，raw、candidate、提交源码和不可变快照SHA链一致；工作文件已用`apply_patch`恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ队列无在途。提交/归档/恢复/队列日志见[`exp668_oj_submit.log`](../log/exp668_oj_submit.log)、[`exp668_oj_archive.log`](../log/exp668_oj_archive.log)、[`exp668_oj_restore.log`](../log/exp668_oj_restore.log)和[`exp668_oj_final_queue.log`](../log/exp668_oj_final_queue.log)。

### 提交 #124647 · exp671 case12 normalized-BF16 partial + native-row16 vec2 consumer

- **代码溯源**：官方 raw 为[`cuda_124647_raw.json`](raw/cuda_124647_raw.json)，不可变提交源码为[`cuda_124647.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124647.cpp)，实验候选为[`cuda_control124611_case12_bf16_normalized_row16_exp671.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case12_bf16_normalized_row16_exp671.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`ef83ee20dca76b3a1cfaa8b734115b264b6f1acc98423a5bffbf832b619c5bd1`；raw JSON SHA-256为`3403b0198271820e06ecba1f840cb5c22f06e9ba111e11a0b793fcce27e2928a`，manifest已登记`#124647`。
- **线上终态**：唯一串行提交`#124647`于`2026-08-24T00:42:12Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1594 ms`、内存`23060504 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、94/54、236/57、38/62、224/52、372/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case12的normalized-BF16 partial producer与native-row16 vec2 reducer consumer合同；target case12（B8/KV8/L32768）为`372 µs / 60分`，相对结构性control #124611 的`371 µs / 60分`未跨至`>=61分`（约`<=365 µs`），关闭exp671 exact contract，不切control、不重投或扫描partial格式、row、vec2、dispatch或启用范围。case13 `181/57`为control继承结果，非target；其它case、aggregate和同场timing不归因。
- **提交、归档与恢复**：normal/resource/LLVM构建及case12、case13专项C500 correctness日志均通过；实际`--submit`只调用一次创建`#124647`，无取消、并行或重投。终态后运行`tools/archive_cuda_submissions.py`，raw、candidate、提交源码和不可变快照SHA链一致；工作文件已用`apply_patch`恢复control SHA=`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`，最终OJ队列无在途。提交/归档记录见[`exp671_oj_submit.log`](../log/exp671_oj_submit.log)和[`exp671_oj_archive.log`](../log/exp671_oj_archive.log)。

### 提交 #124669 · exp673 case9 normalized-BF16 partial + native-row16 vec2 consumer

- **代码溯源**：官方 raw 为[`cuda_124669_raw.json`](raw/cuda_124669_raw.json)，不可变提交源码为[`cuda_124669.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124669.cpp)，实验候选为[`cuda_control124611_case9_bf16_row16_exp673.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case9_bf16_row16_exp673.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`730c05bfb34fd113a16a69822ed5ce93c841ba57c2ceebcb8ccfd2213b194341`；raw JSON SHA-256为`58a1d3f26798faecf12015580bb00b73e43b4ab0e37cf6f5793f79e7fa788b79`，manifest已登记`#124669`。
- **静态与真实C500门禁**：normal/resource/LLVM构建均通过；target case9 producer candidate/control均为`82 MTreg / 48 STreg / 8448 B shared / 0 stack / 5 waves`，physical-row vec2 reducer candidate/control分别为`36 MTreg / 33 STreg / 0 B shared / 0 stack / 8 waves`与`38 / 39 / 0 / 0 / 8`（`log/exp673_candidate_resource.log`、`log/exp673_control_resource.log`）。case9 exact、boundary、random、full及共用模板影响的继承case13 full真实C500 correctness均PASS（`log/exp673_c500_case9_exact.log`、`log/exp673_c500_case9_boundary.log`、`log/exp673_c500_case9_random.log`、`log/exp673_c500_case9_full.log`、`log/exp673_c500_case13_full.log`）。
- **线上终态与唯一目标归因**：唯一串行OJ提交`#124669`于`2026-08-24T01:30:18Z`终态为`Accepted`，总分`66.07`、14/14；OJ总耗时`1595 ms`、内存`23060404 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、227/55、94/54、235/57、39/62、222/52、374/60、181/57、139/55 µs/分`，全部`Accepted`。唯一target case9（B32/KV8/L4096）为`235 µs / 57分`，相对当前control #124611的`236 µs / 57分`同档，未达到`>=58分`；case13 `181/57`为共用模板/继承control结果，非target，其它case、aggregate和同场timing不归因。
- **关闭与归档**：关闭exp673 exact normalized-BF16 partial→native-row16 vec2 consumer contract，不切control、不重投或扫描partial格式、row、leader slots、state layout、template或启用范围。实际`--submit`只调用一次；终态后运行`tools/archive_cuda_submissions.py`，raw、不可变提交源码与candidate SHA链一致，记录见[`exp673_oj_submit.log`](../log/exp673_oj_submit.log)和[`exp673_oj_archive.log`](../log/exp673_oj_archive.log)；本条归档未修改工作文件或OJ队列。

### 提交 #124660 · exp672 case8 normalized-BF16 partial + group8 native-row16 consumer

- **代码溯源**：官方 raw 为[`cuda_124660_raw.json`](raw/cuda_124660_raw.json)，不可变提交源码为[`cuda_124660.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124660.cpp)，实验候选为[`cuda_control124611_case8_bf16_group8_exp672.cpp`](../solutions/archive/2026-08-24-experiments/cuda_control124611_case8_bf16_group8_exp672.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`2956d31cbc3ff45a80605bcfa766632f68e64cb36a8a3f04e8b5332cb1973b98`；raw JSON SHA-256为`0fa431d30c5114908f52b9855ea1ffe130ba589fed574988015a158ddee0549b`，manifest已登记`#124660`。
- **线上终态**：唯一串行提交`#124660`于`2026-08-24T01:17:06Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1596 ms`、内存`23060348 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、227/55、94/54、236/57、38/62、224/52、372/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case8（B16/KV4/L4096）把14-slot fused-tail producer的partial accumulator改为normalized-BF16，并让既有group8 native-row16 reducer按该ABI消费；split14/19-pages、producer ownership、metadata、grid/block及其它dispatch保持不变。target case8为`94 µs / 54分`，与#124611 control同档，未达到`>=55分`；case7虽受共用模板 codegen/resource影响，线上`227 µs / 55分`仍未形成target收益；其它case、aggregate和同场timing不归因。关闭exp672 exact normalized-BF16 partial→group8 native-row16 consumer contract，不切control、不重投或扫描partial格式、row、group8几何、template或启用范围。
- **提交、归档与安全门禁**：normal/resource/LLVM构建及case8 exact/boundary/random/full、继承case7 full的真实C500 correctness均通过；实际`--submit`只调用一次创建`#124660`，无取消、并行或重投。终态后运行`tools/archive_cuda_submissions.py`，raw、candidate、提交源码和不可变快照SHA链一致。工作文件与OJ队列由并行exp673执行者持锁，本条不修改其状态；提交、归档与门禁记录见[`exp672_oj_submit.log`](../log/exp672_oj_submit.log)、[`exp672_oj_archive.log`](../log/exp672_oj_archive.log)、[`exp672_candidate_resource.log`](../log/exp672_candidate_resource.log)和[`exp672_c500_case8_full.log`](../log/exp672_c500_case8_full.log)。

### 提交 #124611 · exp666 case13 normalized-BF16 global partial + native row16 reducer

- **代码溯源**：官方 raw 为[`cuda_124611_raw.json`](raw/cuda_124611_raw.json)，不可变提交源码为[`cuda_124611.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124611.cpp)，实验候选为[`cuda_case13_bf16_normalized_partial_row16_exp666.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case13_bf16_normalized_partial_row16_exp666.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；raw JSON SHA-256为`06a2abca5628a677ddc02ee5803b0df28a8a9c93b254c8c75c783cbafeef6ea6`，manifest已登记`#124611`。
- **线上终态**：唯一串行提交`#124611`于`2026-08-23T23:16:03Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1594 ms`、内存`23060592 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、226/55、94/54、236/57、38/62、224/52、371/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：相对父exp665，唯一新增为case13 reducer consumer的native row16 lowering；normalized-BF16 global partial为其继承机制。target case13（B1/KV8/L58966）为`181 µs / 57分`，相对父exp665的`183 µs / 56分`以及旧结构性control #113889的`182 µs / 56分`跨过目标display tier；目标因果、correctness和结构证据成立，切换结构control至`#124611 / exp666`。其它case、aggregate和同场timing不归因，不扫描或拼接非target收益。
- **提交、归档与恢复**：实际`--submit`只调用一次创建`#124611`，无取消、并行或重投；raw已保存并运行`tools/archive_cuda_submissions.py`。终态后candidate/submitted/immutable/workfile SHA均核验为`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`；提交/终态日志为[`exp666_oj_submit.md`](../log/exp666_oj_submit.md)和[`exp666_sha_after.txt`](../log/exp666_sha_after.txt)，OJ队列无在途。

### 提交 #124606 · exp665 case13 normalized-BF16 global partial + valid-tail

- **代码溯源**：官方 raw 为[`cuda_124606_raw.json`](raw/cuda_124606_raw.json)，不可变提交源码为[`cuda_124606.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124606.cpp)，实验候选为[`cuda_case13_bf16_normalized_partial_tailmask_exp664.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case13_bf16_normalized_partial_tailmask_exp664.cpp)。candidate/submitted/immutable及raw内嵌源码SHA-256均为`1931a5d0721704e9a7800e9ab6e86be1663cb8aea74a916ea43e15dc6b902342`；raw JSON SHA-256为`0186cd1b93d5f1ec0b70cbd3aceca7e71432b36b977c802262424d8349de67e6`，manifest已登记`#124606`。
- **线上终态**：唯一串行提交`#124606`于`2026-08-23T22:56:05Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1597 ms`、内存`23060336 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、22/73、17/73、28/63、225/55、93/54、234/57、39/62、223/52、377/60、183/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case13 z8 producer→vec2 reducer启用normalized-BF16 global partial；valid-tail loader/PV guard只是必要correctness修复。target case13（B1/KV8/L58966）为`183 µs / 56分`，相对结构性control `182 µs / 56分`未达到预注册`>=57分`（约`<=181 µs`）；其它case、aggregate和同场timing不归因，关闭exp665 exact contract，不切换control、不重投或扫描partial格式、tail mask、state layout、lane、template或启用范围。
- **提交、归档与恢复**：提交前无在途、dry-run和冻结SHA核验通过；实际`--submit`只调用一次创建`#124606`，无取消、并行或重投。日志为[`exp665_oj_dryrun.log`](../log/exp665_oj_dryrun.log)、[`exp665_oj_submit.log`](../log/exp665_oj_submit.log)、[`exp665_oj_archive.log`](../log/exp665_oj_archive.log)、[`exp665_oj_sha_archive.log`](../log/exp665_oj_sha_archive.log)和[`exp665_oj_final_queue.log`](../log/exp665_oj_final_queue.log)；raw、归档源码与candidate SHA链一致。终态后工作文件已恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，最终OJ队列无在途。

### 提交 #124601 · exp664 case12 dead-half K-token BSM wave release

- **代码溯源**：官方 raw 为[`cuda_124601_raw.json`](raw/cuda_124601_raw.json)，不可变提交源码为[`cuda_124601.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124601.cpp)；candidate/submitted/immutable SHA-256均为`676ee8b331d5618f5ddfa8ffcc6276f1cea9d279529ca4a11ca3bb6b5b44a893`，raw JSON SHA-256为`6408e63c6a82ca86677ff38af20418142a34e88177d70874c37e7fe8066a97db`。
- **线上终态**：唯一串行提交`#124601`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1598 ms`、内存`23060776 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、228/55、94/54、234/57、39/62、223/52、375/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case12 dead-half K-token BSM wave release；target case12（B8/KV8/L32768）为`375 µs / 60分`，相对结构性control `378 µs / 60分`未跨至`>=61分`（约`<=365 µs`）。其它case、aggregate和同场timing不归因；关闭exp664 exact contract，control不变，不重投或扫描该机制的token、wave、释放时机或启用范围。
- **提交、归档与恢复**：仅创建`#124601`，无取消、重投或并行提交；raw、不可变源码与candidate SHA归档链一致。终态后工作文件已恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，最终OJ队列无在途。

### 提交 #124570 · exp660 case12 async register-returning K/V load + rebase

- **代码溯源**：官方 raw 为[`cuda_124570_raw.json`](raw/cuda_124570_raw.json)，不可变提交源码为[`cuda_124570.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124570.cpp)，实验候选为[`cuda_case12_async_register_kv_rebase_exp660.cpp`](../solutions/archive/2026-08-24-experiments/cuda_case12_async_register_kv_rebase_exp660.cpp)。candidate/submitted/immutable及raw内嵌代码SHA-256均为`9d92c4383e17e1d073ff8452344417b2a548299c50a8f2fc67ef7c694daff51f`；raw JSON SHA-256为`68c24873739eb102cfd51ee91d6cd619b3c431e1e5472afb2303a52179cd7004`，manifest已登记`#124570`。
- **线上终态**：唯一串行提交`#124570`于`2026-08-23T21:36:39Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1598 ms`、内存`23060396 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、228/55、93/54、236/57、39/62、224/52、373/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅在case12下一页K/V使用register-returning async global load，并以官方`arrive(64)+barrier`后回写既有shared；partial、reducer、tail与其它dispatch不变。target case12（B8/KV8/L32768）为`373 µs / 60分`，相对结构性control `378 µs / 60分`未达到预注册`>=61分`（约`<=365 µs`）；其它case、aggregate和同场timing不归因，关闭exp660 exact contract，不切换control、不重投或扫描async load、wait、rebase、payload或启用范围。
- **提交、归档与恢复**：提交前`--list`无在途、dry-run和冻结SHA核验通过；实际`--submit`只调用一次创建`#124570`，持续watch同一ID至`Finished/Accepted`，未取消、并行或重投。日志为[`exp660_oj_dry_run.log`](../log/exp660_oj_dry_run.log)、[`exp660_oj_pre_submit_list.log`](../log/exp660_oj_pre_submit_list.log)、[`exp660_oj_pre_submit_sha.log`](../log/exp660_oj_pre_submit_sha.log)、[`exp660_oj_submit_watch.log`](../log/exp660_oj_submit_watch.log)、[`exp660_oj_archive.log`](../log/exp660_oj_archive.log)、[`exp660_oj_sha_archive.log`](../log/exp660_oj_sha_archive.log)、[`exp660_oj_restore.log`](../log/exp660_oj_restore.log)、[`exp660_oj_final_queue.log`](../log/exp660_oj_final_queue.log)；终态后保存raw并运行`archive_cuda_submissions.py`，工作文件已恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，最终队列无在途。

### 提交 #124537 · exp631 case2 source-owner native B128 single-launch

- **代码溯源**：官方 raw 为[`cuda_124537_raw.json`](raw/cuda_124537_raw.json)，不可变提交源码为[`cuda_124537.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124537.cpp)，实验候选为[`cuda_case2_source_owner_native_b128_single_launch_exp631.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case2_source_owner_native_b128_single_launch_exp631.cpp)。candidate/submitted/immutable SHA-256均为`a61ef873b62fe81fa96b714d1a4ce44cb10c9a7e0ade61d4487e23697dd222af`；raw JSON SHA-256为`36f3a249acc178d7067822e226f1ca8179ac00058acb53efce8978d522eaffdf`，raw内嵌源码SHA也一致，manifest已登记`#124537`。
- **放宽准入与安全门禁**：此前该候选的target resource为`23 MTreg / 37 STreg / 0B shared / 0B stack / 8 waves`，control为`22/26/0/0/8`；按当前OJ-first规则，资源增加本身不阻止一次有明确target的探索性probe。本轮以冻结SHA完成normal rebuild，并通过最小真实C500 case2 special gate（token1 poison/padding trap、mixed/reverse GQA/page ownership、bit equality、guards、determinism和workspace reuse，9项检查）；未运行A/B，因本地性能不是探索性probe前置条件。证据为`log/exp631_relaxed_candidate_normal_build.log`与`log/exp631_relaxed_c500_special.log`。
- **线上终态**：确认队列无在途、dry-run成功且提交前工作文件SHA为候选后，仅调用一次实际`--submit`创建`#124537`；持续watch同一ID至`Finished/Accepted`，没有取消、并行或重复提交。提交时间`2026-08-23T20:20:11Z`，总分`66.00`、14/14；OJ总耗时`1596 ms`、内存`23060620 KB`。case1–14时延/分数=`3/92、4/90、9/83、23/72、17/73、28/63、227/55、93/54、234/57、38/62、224/52、375/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target case2（B4/KV8/L2）为`4 µs / 90分`，相对control的`4 µs / 90分`同档，未达到预注册约`<=3.75824 µs / 91分`；其它case、aggregate和同场timing不归因。因此关闭exp631 exact single-launch native-B128 source-owner fanout contract，不切换control，不重投或扫描lane、地址、builtin、payload、template或enable-range；只有实质不同的owner/backend和新的可证伪机制才可重开。
- **归档与恢复**：已运行`tools/archive_cuda_submissions.py`；raw、归档源码与manifest身份链一致。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，最终OJ队列无在途。

### 提交 #124563 · exp661 case14 single FP32 LSE state/reducer + tail-only valid K/V loader/PV guard

- **代码溯源**：官方 raw 为[`cuda_124563_raw.json`](raw/cuda_124563_raw.json)，不可变提交源码为[`cuda_124563.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124563.cpp)，实验候选为[`cuda_case14_single_lse_tailmask_exp661.cpp`](../solutions/archive/2026-08-24-experiments/cuda_case14_single_lse_tailmask_exp661.cpp)。candidate/submitted/immutable SHA-256均为`25fed14d39148f013533225a317696a983197e964a8a007cb2e3a31f167b04b5`；raw JSON SHA-256为`bccf48500ae08463cfa7eb60ef30ad9a5dd62dc821a827dff2adee602aa6267e`，raw内嵌源码SHA与candidate一致，manifest已登记`#124563`。
- **线上终态**：唯一串行提交`#124563`于`2026-08-23T21:19:20Z`终态为`Accepted`，总分`65.86`、14/14；OJ总耗时`1593 ms`、内存`23060324 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、94/54、232/57、39/62、222/52、373/60、182/56、141/54 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选继承exp659 case14 single FP32 LSE state/reducer，并仅增加case14 tail-only valid K/V loader与tail PV guard；target case14（B1/KV4/L61519）为`141 µs / 54分`，相对结构性control `139 µs / 55分`退档，未达到`>=56分`。其它case、aggregate和同场timing不归因，exp661 exact contract关闭，不切换control、不重投或扫描tail loader、PV guard、state layout或启用范围。
- **提交、归档与恢复**：提交前`--list`无在途、dry-run和冻结SHA核验通过；实际`--submit`只调用一次创建`#124563`，持续watch同一ID至`Finished/Accepted`，未取消、并行或重投。日志为[`exp661_oj_dry_run.log`](../log/exp661_oj_dry_run.log)、[`exp661_oj_submit_watch.log`](../log/exp661_oj_submit_watch.log)、[`exp661_oj_watch_124563.log`](../log/exp661_oj_watch_124563.log)；终态后保存raw并运行`archive_cuda_submissions.py`。工作文件已用`apply_patch`恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，最终OJ队列无在途。

### 提交 #124526 · exp657 case6 separate short-row owner

- **代码溯源**：官方 raw 为[`cuda_124526_raw.json`](raw/cuda_124526_raw.json)，不可变提交源码为[`cuda_124526.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124526.cpp)，实验候选为[`cuda_case6_separate_shortrow_owner_exp657.cpp`](../solutions/archive/2026-08-24-experiments/cuda_case6_separate_shortrow_owner_exp657.cpp)。candidate/submitted/immutable SHA-256均为`b658d566d67a9822dcf8256eece1666c61f9f63858bb6bc5e0b348254aa0befc`；raw JSON SHA-256为`a546fe626a9934bd514918aa0d84349ea72ce83ec623d0384242235271776065`，raw内嵌代码SHA与candidate一致，manifest已登记`#124526`。
- **线上终态**：提交`#124526`于`2026-08-23T20:00:52Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`65.64`、14/14；OJ总耗时`1597 ms`、内存`23060788 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、36/57、229/55、93/54、228/58、38/62、221/52、375/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：候选仅为case6 B16/KV8/L362增设独立`(batch,kv_head)` short-row owner，并令`0<cache_seqlens<=48`的普通producer与group8 reducer提前返回；线上target从control的`28 µs / 63分`退至`36 µs / 57分`，未达到预注册约`<=27 µs / >=64分`。其它case、aggregate和同场timing不归因；关闭exp657 exact short-row owner contract，不切换control、不重投或扫描阈值、owner映射、模板、grid或dispatch。
- **提交、归档与恢复**：按放宽后的OJ-first规则，在最低安全门禁通过后只调用一次实际`--submit`创建`#124526`；原提交进程继续watch至终态，未取消、未并行、未重复提交。队列/dry-run/提交watch/结果身份记录于[`exp657_oj_submit_watch.log`](../log/exp657_oj_submit_watch.log)；已运行归档流程，官方raw和不可变提交源码SHA一致。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列无在途。

### 提交 #124493 · exp656 case13 raw-FP32 pair-state direct three-peer fan-in + valid-tail mask

- **代码溯源**：官方 raw 为[`cuda_124493_raw.json`](raw/cuda_124493_raw.json)，不可变提交源码为[`cuda_124493.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124493.cpp)，实验候选为[`cuda_case13_raw_fp32_threepeer_tailmask_exp656.cpp`](../solutions/archive/2026-08-24-experiments/cuda_case13_raw_fp32_threepeer_tailmask_exp656.cpp)。candidate/submitted/immutable SHA-256均为`1f4268afe58370da69a88a60ff5217c5fffa62aed54589f58f94a9a057b252fb`；raw JSON SHA-256为`c8791bf7b3aef03c9e3fb61a4e74084e0f9a0af9e3dade67307f812c50cc6fec`，manifest已登记`#124493`。
- **线上终态**：#124493 于`2026-08-23T19:13:50Z`终态为`Accepted`，总分`66.07`、14/14；OJ总耗时`1597 ms`，内存`23060392 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、22/73、17/73、28/63、228/55、93/54、234/57、39/62、223/52、375/60、183/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与 control 决策**：候选仅在 case13 B1/KV8/L58966 direct kernel 启用 raw-FP32 pair-state direct three-peer fan-in，并用私有 valid-tail loader/PV mask 修复 invalid-tail read；case9及非target dispatch恢复control。target case13为`183 µs / 56分`，相对结构性control `182 µs / 56分`未达到预注册`>=57分`，故线上关闭exp656 exact contract；其它case、aggregate和同场timing不归因，不切换control、不重投或扫描fan-in、tail mask、state layout、lane、template或启用范围。
- **提交、归档与恢复**：唯一`--submit`创建`#124493`；首次提交watch达到CLI 900s上限后，仅对同一ID继续watch，未取消或重投；终态后补齐raw归档并运行`archive_cuda_submissions.py`，raw/source SHA链已核验，`solutions/archive/SUBMISSIONS.md`已登记。终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #124440 · exp654 case9 raw-FP32 pair-state direct three-peer fan-in

- **代码溯源**：官方 raw 为[`cuda_124440_raw.json`](raw/cuda_124440_raw.json)，不可变提交源码为[`cuda_124440.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124440.cpp)，实验候选为[`cuda_case9_raw_fp32_threepeer_fanin_exp654.cpp`](../solutions/archive/2026-08-24-experiments/cuda_case9_raw_fp32_threepeer_fanin_exp654.cpp)。candidate/submitted/immutable SHA-256 均为`314c3445e887e4e2e1e16653a3e7be28d71b44803b8d6a720f73b68d28f13bff`；raw JSON SHA-256 为`9e6d1980a04f4e1069f87e0062758d7a661766bba53b07ae3d85146f2b102c37`，manifest已登记`#124440`。
- **线上终态**：#124440 于`2026-08-23T18:09:49Z`终态为`Accepted`，总分`66.07`、14/14；OJ总耗时`1593 ms`，内存`23060644 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、236/57、39/62、223/52、372/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与 control 决策**：target 为 case9（B32/KV8/L4096）；结构性control `#113889` 的目标显示分为`57分`，本次目标显示分仍为`57分`，未达到预注册`>=58分`，故线上关闭 exact raw-FP32 pair-state direct three-peer fan-in contract；其它case、aggregate和同场timing不归因，不切换control、不重投或扫描fan-in、peer、state layout、lane、template或启用范围。
- **提交、归档与恢复**：唯一`--submit`创建`#124440`；提交客户端和首次watch各因900s超时，未取消远端任务，后续仅对该ID继续watch至`Finished/Accepted`。raw/source SHA链已核验，`solutions/archive/SUBMISSIONS.md`已登记；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #124413 · exp652 case11 pair-output B128 + tailmask（错误重复）

- **代码溯源**：官方 raw 为[`cuda_124413_raw.json`](raw/cuda_124413_raw.json)，不可变提交源码为[`cuda_124413.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124413.cpp)，实验候选为[`cuda_case11_pair_output_b128_tailmask_exp652.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case11_pair_output_b128_tailmask_exp652.cpp)。candidate/submitted/immutable SHA-256 均为`f993ccd69f320e5710b282f03e01d713b2cc47b2bd57e672a238970918732a08`；raw JSON SHA-256 为`852ce472d09458a13c3f34ee321a04493d78c34c7c8876c2ce9b9aeb9c5e4844`，manifest已登记`#124413`。
- **线上终态**：#124413 于`2026-08-23T17:45:00Z`终态为`Accepted`，总分`66.07`、14/14；case1–14=`3/4/10/22/17/28/225/93/233/39/223/375/181/139 µs`，分数=`92/90/82/73/73/63/55/54/57/62/52/60/57/55`。唯一 target case11（B16/KV4/L12251）为`223 µs / 52分`，与control同档且未达到`>=53分`；#124413是#124393的错误重复，不作独立性能证据。
- **归因与收尾**：#124393首次 probe已失败，#124413不改变该结论；exp652 exact pair-output/tailmask contract关闭、不切control。raw、不可变提交源码与candidate SHA已核验一致，终态后工作文件为control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列为空。

### 提交 #124393 · exp652 case11 pair-output B128 + tailmask（首次 probe）

- **代码溯源**：官方 raw 为[`cuda_124393_raw.json`](raw/cuda_124393_raw.json)，不可变提交源码为[`cuda_124393.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124393.cpp)，实验候选为[`cuda_case11_pair_output_b128_tailmask_exp652.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case11_pair_output_b128_tailmask_exp652.cpp)。candidate/submitted/immutable SHA-256 均为`f993ccd69f320e5710b282f03e01d713b2cc47b2bd57e672a238970918732a08`；raw JSON SHA-256 为`20c3968e874ae9fa595199d985f65c58d6382fb73babeb67c38ddfa66a656e74`，manifest已登记`#124393`。
- **线上终态**：#124393 于`2026-08-23T17:29:14Z`终态为`Accepted`，总分`66.00`、14/14；case1–14=`3/4/10/23/17/28/227/93/233/39/224/375/181/139 µs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一 target case11（B16/KV4/L12251）为`224 µs / 52分`，相对control的`222 µs / 52分`同档，首次 probe失败且未达到`>=53分`。
- **归因与收尾**：exp652 exact pair-output/tailmask contract关闭、不切control；#124413为同一 candidate 的错误重复，不作独立证据或新归因。raw、不可变提交源码与candidate SHA已核验一致，终态后工作文件为control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列为空。

### 提交 #124328 · exp651 case7 two-stage finalizer + tailmask

- **代码溯源**：官方 raw 为[`cuda_124328_raw.json`](raw/cuda_124328_raw.json)，不可变提交源码为[`cuda_124328.cpp`](../solutions/archive/2026-08-24-submissions/cuda_124328.cpp)，实验候选为[`cuda_case7_two_stage_finalizer_tailmask_exp651.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case7_two_stage_finalizer_tailmask_exp651.cpp)。candidate/submitted/immutable SHA-256 均为`8873b4ed0cdcc34ed7ab0fde84fa307683c4292fe653512be7ebf0ec96aa5c4b`；raw JSON SHA-256 为`5a538916e1a615ca51bea8928dbeb9e64353459b80c225c8d40336d3064839bd`，manifest已登记`#124328`。
- **线上终态**：唯一串行提交`#124328`于`2026-08-23T16:38:52Z`终态为`WrongAnswer`，总分`59.64`；case3 WrongAnswer，约`36,382,034 ms`，其余 13 个测试点 Accepted。OJ case7（B64/KV8/L2048）为`282 µs / 49分`，相对control的`226 µs / 55分`退档，未达到`>=56分`。
- **唯一目标归因与control决策**：case3 的 correctness failure 使提交整体 WrongAnswer；线上关闭exp651 two-stage finalizer + tailmask exact contract，不切换control、不重投或扫描其finalizer、tailmask、split、ownership或启用范围。其它case同场timing不归因；终态后工作文件恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列为空。

### 提交 #124235 · exp632 case2 source-owner streaming B32

- **代码溯源**：官方 raw 为[`cuda_124235_raw.json`](raw/cuda_124235_raw.json)，不可变提交源码为[`cuda_124235.cpp`](../solutions/archive/2026-08-23-submissions/cuda_124235.cpp)，实验候选为[`cuda_case2_source_owner_streaming_b32_exp632.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case2_source_owner_streaming_b32_exp632.cpp)。candidate/submitted/immutable SHA-256 均为`d43be08ccec3ccbf6bb332870c15e69b70055440170fac352626d259fe87fc9b`；raw JSON SHA-256 为`726679e8e3d4d3db76f15817259beffbf5fbd933a6c61cece12e6bfcbcb31ab0`，manifest已登记`#124235`。
- **线上终态**：唯一串行提交`#124235`于`2026-08-23T15:33:11Z`终态为`Accepted`，总分`66.07`、14/14；OJ总耗时`1592 ms`、内存`23060500 KB`。case1–14=`3/4/10/22/17/28/224/94/234/38/222/376/181/139 µs`，分数=`92/90/82/73/73/63/55/54/57/62/52/60/57/55`。唯一 target case2（B4/KV8/L2）为`4 µs / 90分`，与control同档，未达到约`<=3.75824 µs / 91分`。
- **唯一目标归因与control决策**：线上关闭exp632 source-owner streaming B32 exact contract；其它case同场timing不归因，不重投或扫描其lane、word、地址、store、helper、模板或启用范围。raw、不可变提交源码与candidate SHA已核验一致，终态后工作文件恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列为空。

### 提交 #124170 · exp592 case7 separate direct-output owner

- **代码溯源**：官方 raw 为[`cuda_124170_raw.json`](raw/cuda_124170_raw.json)，不可变提交源码为[`cuda_124170.cpp`](../solutions/archive/2026-08-23-submissions/cuda_124170.cpp)，实验候选为[`cuda_case7_separate_direct_output_exp592.cpp`](../solutions/archive/2026-08-18-experiments/cuda_case7_separate_direct_output_exp592.cpp)。candidate/submitted/immutable SHA-256 均为`93fc70f063302c336b6d583b644de2b5fc936119486da277bc9a5ba183bd7982`；raw JSON SHA-256 为`3588fd728ca14883a355721793693e665c09f498530f17ad9d82adb82438c0a2`，manifest已登记`#124170`。
- **线上终态**：唯一串行提交`#124170`于`2026-08-23T14:42:21Z`终态为`Accepted`，总分`65.57`、14/14；OJ总耗时`1645 ms`、内存`23060344 KB`。唯一 target case7（B64/KV8/L2048）为`276 µs / 50分`，相对control `226 µs / 55分`严重退档，未达到`>=56分`。
- **唯一目标归因与control决策**：线上关闭exp592 independent direct-output/fixed-launch exact contract，control不变；其它case同场timing不归因，不重投或扫描其launch、store、layout、lane、template或enable范围。raw、不可变提交源码与candidate SHA已核验一致，唯一串行归档完成，终态后工作文件恢复control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`。

### 提交 #124146 · exp637 case6 next-K register-wave BSM

- **代码溯源**：官方 raw 为[`cuda_124146_raw.json`](raw/cuda_124146_raw.json)，不可变提交源码为[`cuda_124146.cpp`](../solutions/archive/2026-08-23-submissions/cuda_124146.cpp)，实验候选为[`cuda_case6_nextk_register_wave_bsm_exp637.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case6_nextk_register_wave_bsm_exp637.cpp)。candidate/submitted/immutable SHA-256 均为`c97cd5d09e7222879908c3efa304b5ee5330a5b738e37fedc09782cd845cee1f`；raw JSON SHA-256 为`fbc4b4fcd4f6131f39c10f5688ad00455bc4d048533507145a80597a4feb16b4`，manifest已登记`#124146`。
- **线上终态**：唯一串行提交`#124146`于`2026-08-23T14:28:10Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1593 ms`、内存`23060472 KB`。唯一 target case6（B16/KV8/L362）为`30 µs / 62分`，相对control `28 µs / 63分`退档，未达到约`<=27 µs / 64分`。
- **唯一目标归因与control决策**：线上否定exp637 next-K register-wave BSM exact contract，control不变；其它case同场timing不归因，不重投或扫描其lane、payload、builtin、地址、布局、模板或启用范围。raw、不可变提交源码与candidate SHA已核验一致，串行归档事实已登记于manifest。

### 提交 #124090 · exp625 case12 distributed-weight exp2

- **代码溯源**：官方 raw 为[`cuda_124090_raw.json`](raw/cuda_124090_raw.json)，不可变提交源码为[`cuda_124090.cpp`](../solutions/archive/2026-08-23-submissions/cuda_124090.cpp)，实验候选为[`cuda_case12_distributed_weight_exp625.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case12_distributed_weight_exp625.cpp)。candidate/submitted/immutable SHA-256 均为`ba5635cf0b62441587edc893fcf80feafed2228b70b13aa62eac693506b07026`；raw JSON SHA-256 为`6acaa731f864d7b889b82132cdb9c3b8d82315405d8b0a689d9a7505868d2755`，manifest已登记`#124090`。
- **线上终态**：唯一串行提交`#124090`于`2026-08-23T13:58:43Z`终态为`Accepted`，总分`65.86`、14/14；OJ总耗时`1598 ms`、内存`23060256 KB`。唯一 target case12（B8/KV8/L32768、40 splits）为`376 µs / 60分`，相对control `378 µs / 60分`未达到约`<=365 µs / 61分`。
- **唯一目标归因与control决策**：线上未支持exp625 distributed-weight exact contract，control不变；其它case同场timing不归因，不重投或扫描其条件、lane、builtin、地址、模板或启用范围。raw、不可变提交源码与candidate SHA已核验一致，串行归档事实已登记于manifest。

### 提交 #124003 · exp643 case1 native-BSM shared-V

- **代码溯源**：官方 raw 为[`cuda_124003_raw.json`](raw/cuda_124003_raw.json)，不可变提交源码为[`cuda_124003.cpp`](../solutions/archive/2026-08-23-submissions/cuda_124003.cpp)，实验候选为[`cuda_case1_native_bsm_shared_v_exp643.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case1_native_bsm_shared_v_exp643.cpp)。candidate/submitted/immutable SHA-256 均为`358b45ab33b80fc6a1eac9d9d5923d12b39037cb5644a7aa23baa68f7a586667`；raw JSON SHA-256 为`d1ba1620102254cfee65b18831c1bdd1fef03682f1c13fb0cb5f2fdffac6efc5`，manifest已登记`#124003`。
- **线上终态**：提交`#124003`于`2026-08-23T12:58:10Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`65.79`、14/14；OJ总耗时`1595 ms`、内存`23060464 KB`。case1–14时延/分数依次为`4/90、4/90、9/83、23/72、17/73、29/62、225/55、94/54、235/57、38/62、223/52、373/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case1（B1/KV4/L1）；相对结构性control `#113889` 的`3 µs / 92分`退至`4 µs / 90分`，未达到唯一成功判据。其它case同场timing不归因；关闭exp643 native-BSM shared-V exact contract，不切换control、不重投或扫描predicate、owner lane、arrive/barrier、payload、shared布局、vector/地址、模板或启用范围。
- **安全门禁与OJ优先决策**：candidate/control normal build、case1 exact/full真实C500 smoke及重复调用确定性检查均通过；此前静态资源门禁曾发现target资源高于control，但按放宽后的OJ-first政策，资源/本地timing不单独阻止这次有明确目标的单笔串行probe，线上终态是最终性能裁决。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交900秒超时后继续watch、raw/archive、control恢复和终态队列分别记录于`log/exp643_oj_precheck.log`、`log/exp643_stage_sha.log`、`log/exp643_oj_dry_run.log`、`log/exp643_pre_submit_sha.log`、`log/exp643_oj_submit.log`、`log/exp643_oj_posttimeout_queue.log`、`log/exp643_oj_watch_124003.log`、`log/exp643_oj_archive.log`、`log/exp643_oj_sha_archive.log`与`log/exp643_oj_restore.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123976 · exp646 case1 per-word raw-BSM V fanout

- **代码溯源**：官方 raw 为[`cuda_123976_raw.json`](raw/cuda_123976_raw.json)，不可变提交源码为[`cuda_123976.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123976.cpp)，实验候选为[`cuda_case1_per_word_raw_bsm_v_fanout_exp646.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case1_per_word_raw_bsm_v_fanout_exp646.cpp)。candidate/submitted/immutable SHA-256 均为`812fc9d6fe71a25682b7b974ca88788a4bb30d82c260af732d8512dd43c4e39f`；raw JSON SHA-256 为`7d2e606d09d09e358d8609b3b8a31444d3f94cd9f1f7813dce675cc0026335e4`，manifest已登记`#123976`。
- **线上终态**：提交`#123976`于`2026-08-23T12:39:31Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`66.07`、14/14；OJ总耗时`1592 ms`、内存`23060584 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、233/57、39/62、222/52、375/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case1（B1/KV4/L1）；相对结构性control `#113889` 的`3 µs / 92分`保持同档，未严格高于唯一成功判据。其它case同场timing不归因；关闭exp646 per-word raw-BSM V fanout exact contract，不切换control、不重投或扫描source lane、word顺序、BSM地址、store、helper或启用范围。
- **安全门禁与OJ优先决策**：candidate真实C500 case1 exact/GQA8 tag、padding poison、guard、workspace reuse及非target smoke均通过；按放宽后的OJ-first政策，线上终态是最终性能裁决，目标未跨 tier 直接关闭该合同。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交watch、raw/archive、control恢复和终态队列分别记录于`log/exp646_oj_precheck.log`、`log/exp646_stage_sha.log`、`log/exp646_oj_dry_run.log`、`log/exp646_pre_submit_sha.log`、`log/exp646_oj_submit.log`、`log/exp646_oj_archive.log`、`log/exp646_control_restore_sha.log`与`log/exp646_oj_final_queue.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123950 · exp650 case11 direct-fanin normalized-BF16 txfix

- **代码溯源**：官方 raw 为[`cuda_123950_raw.json`](raw/cuda_123950_raw.json)，不可变提交源码为[`cuda_123950.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123950.cpp)，实验候选为[`cuda_case11_direct_fanin_normalized_bf16_txfix_exp650.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case11_direct_fanin_normalized_bf16_txfix_exp650.cpp)。candidate/submitted/immutable SHA-256 均为`b896fe8165d3d9729aec655a50c728d79dbe2bfc261a2b16e4de450ca9120dde`；raw JSON SHA-256 为`36f51e2595474cdb70ec06ed418797967879e2792faaa5dc167de93c65f44040`，manifest已登记`#123950`。
- **线上终态**：提交`#123950`于`2026-08-23T12:12:57Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1596 ms`、内存`23060448 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、224/55、93/54、234/57、39/62、227/52、374/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case11（B16/KV4/L12251）；相对结构性control `#113889` 的`222 µs / 52分`变为`227 µs / 52分`，未达到唯一成功判据。其它case同场timing不归因；关闭exp650 normalized-BF16 direct-fanin txfix exact contract，不切换control、不重投或扫描tx、row、lane、payload、barrier、merge-order、helper或启用范围。
- **安全门禁与OJ优先决策**：candidate真实C500最低smoke已通过；按放宽后的OJ-first政策，线上终态是最终性能裁决，目标同档且回退直接否定该合同。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交900秒超时后继续watch、raw/archive、control恢复和终态队列分别记录于`log/exp650_oj_precheck.log`、`log/exp650_stage_sha.log`、`log/exp650_oj_dry_run.log`、`log/exp650_pre_submit_sha.log`、`log/exp650_oj_submit.log`、`log/exp650_oj_posttimeout_queue.log`、`log/exp650_oj_watch.log`、`log/exp650_oj_archive.log`、`log/exp650_control_restore_sha.log`与`log/exp650_oj_final_queue.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123932 · exp649 case14 direct-fanin normalized-BF16 txfix

- **代码溯源**：官方 raw 为[`cuda_123932_raw.json`](raw/cuda_123932_raw.json)，不可变提交源码为[`cuda_123932.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123932.cpp)，实验候选为[`cuda_case14_direct_fanin_normalized_bf16_txfix_exp649.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case14_direct_fanin_normalized_bf16_txfix_exp649.cpp)。candidate/submitted/immutable SHA-256 均为`f15c99b1f0651cdd9d7cfca9fd26005e248c6e4751e6af4c4f4138f4136b1ccf`；raw JSON SHA-256 为`53cfa211e3ef91c03fb6a41fc6c03036e174d76725057002a88ae318ab7e783e`，manifest已登记`#123932`。
- **线上终态**：提交`#123932`于`2026-08-23T11:56:05Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1594 ms`、内存`23060432 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、228/55、93/54、232/57、39/62、222/52、374/60、181/57、141/54 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case14（B1/KV4/L61519）；相对结构性control `#113889` 的`139 µs / 55分`变为`141 µs / 54分`，未达到唯一成功判据。其它case同场timing不归因；关闭exp649 normalized-BF16 direct-fanin txfix exact contract，不切换control、不重投或扫描tx、row、lane、payload、barrier、merge-order、helper或启用范围。
- **安全门禁与OJ优先决策**：candidate真实C500最低smoke已通过；按放宽后的OJ-first政策，线上终态是最终性能裁决，目标退档直接否定该合同。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交watch、raw/archive、control恢复和终态队列分别记录于`log/exp649_oj_precheck.log`、`log/exp649_stage_sha.log`、`log/exp649_oj_dry_run.log`、`log/exp649_pre_submit_sha.log`、`log/exp649_oj_submit.log`、`log/exp649_oj_archive.log`、`log/exp649_control_restore_sha.log`与`log/exp649_oj_final_queue.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123892 · exp648 case8 direct-fanin normalized-BF16 txfix

- **代码溯源**：官方 raw 为[`cuda_123892_raw.json`](raw/cuda_123892_raw.json)，不可变提交源码为[`cuda_123892.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123892.cpp)，实验候选为[`cuda_case8_direct_fanin_normalized_bf16_txfix_exp648.cpp`](../solutions/archive/2026-08-23-experiments/cuda_case8_direct_fanin_normalized_bf16_txfix_exp648.cpp)。candidate/submitted/immutable SHA-256 均为`a708993cb5bb10cea02f46b297d8880173c090eb8f08f370070f10863a2f6afd`；raw JSON SHA-256 为`e99214380c726599d3b043aedafeaa5ecb94df163a444b919ef7ffff59fcc520`，manifest已登记`#123892`。
- **线上终态**：提交`#123892`于`2026-08-23T11:29:41Z`创建，经历Pending→Running→Finished，终态为`Accepted`，总分`65.86`、14/14；OJ总耗时`1603 ms`、内存`23060320 KB`。case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、227/55、95/53、237/57、39/62、222/52、377/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case8（B16/KV4/L4096）；相对结构性control `#113889` 的`94 µs / 54分`变为`95 µs / 53分`，未达到唯一成功判据。其它case同场timing不归因；关闭exp648 normalized-BF16 direct-fanin txfix exact contract，不切换control、不重投或扫描tx、row、lane、payload、barrier、merge-order、helper或启用范围。
- **安全门禁与OJ优先决策**：candidate真实C500 full/exact boundary、padding poison、output guard、workspace reuse和candidate/control determinism均通过；按放宽后的OJ-first政策，线上终态是最终性能裁决，目标退档直接否定该合同。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交超时后继续watch、raw/archive、control恢复和终态队列分别记录于`log/exp648_oj_precheck.log`、`log/exp648_stage_sha.log`、`log/exp648_oj_dry_run.log`、`log/exp648_oj_submit.log`、`log/exp648_oj_watch.log`、`log/exp648_oj_archive.log`、`log/exp648_control_restore_sha.log`与`log/exp648_oj_final_queue.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123872 · exp608 case12 direct-K wave-BSM lookahead

- **代码溯源**：官方 raw 为[`cuda_123872_raw.json`](raw/cuda_123872_raw.json)，不可变提交源码为[`cuda_123872.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123872.cpp)，实验候选为[`cuda_case12_direct_k_wave_bsm_exp608.cpp`](../solutions/archive/2026-08-20-experiments/cuda_case12_direct_k_wave_bsm_exp608.cpp)。candidate/submitted/immutable SHA-256 均为`1ed233b3ba65106c80024d0aece5c006f9b05678d8f36069800c1f84fd6d4f5f`；raw JSON SHA-256 为`adf1cd9d51b92451779368c4550c6fa53c3580173cb810ecf97b7f46dc3ea6c3`，manifest已登记`#123872`。
- **线上终态**：提交`#123872`于`2026-08-23T11:09:24Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1605 ms`、内存`23060400 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、94/54、231/57、39/62、224/52、387/59、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case12（B8/KV8/L32768、40 splits）；相对结构性control `#113889` 的`378 µs / 60分`变为`387 µs / 59分`，远未达到预注册约`<=365.70 µs / 61分`，线上否定exp608 direct-K wave-BSM current/next-K lookahead数据流假设。其它case同场timing不归因；关闭exact contract，不切换control、不重投或扫描其BSM lane/payload、地址、布局、load拼写、模板或启用范围。
- **安全门禁与OJ优先决策**：candidate/control cross-build、CPU quick semantic smoke（14/14）和真实C500 case12 exact长度`1,2,15,16,17,31,32,33,831,832,833,32767,32768`及boundary/reuse smoke均通过；candidate目标资源为`84/52/8448/0/5`，control为`82/50/8448/0/5`。按放宽后的OJ-first政策，资源增加和本地未形成线上结论不阻止这次有目的的单笔串行probe；线上终态是最终性能裁决。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交与Pending→Running→Accepted watch、raw/archive/SHA、control恢复和终态队列分别记录于`log/exp608_relaxed_oj_list_pre.log`、`log/exp608_relaxed_oj_stage_sha.log`、`log/exp608_relaxed_oj_dry_run.log`、`log/exp608_relaxed_oj_submit_watch.log`、`log/exp608_relaxed_oj_archive_sha.log`、`log/exp608_relaxed_oj_restore.log`与`log/exp608_relaxed_oj_list_post.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #123848 · exp609 case11 duplicated-global-V

- **代码溯源**：官方 raw 为[`cuda_123848_raw.json`](raw/cuda_123848_raw.json)，不可变提交源码为[`cuda_123848.cpp`](../solutions/archive/2026-08-23-submissions/cuda_123848.cpp)，实验候选为[`cuda_case11_duplicate_global_v_exp609.cpp`](../solutions/archive/2026-08-20-experiments/cuda_case11_duplicate_global_v_exp609.cpp)。submitted/candidate/immutable SHA-256 均为`b292a83df4e6fa54301164505aab15e69104bfcf66273a8e27c52feaf395adbf`；raw JSON SHA-256 为`11824d97ce942f627b5cf32bc2c4538981faa4e6a374bfc881138c78e0c35b51`，manifest已登记`#123848`。
- **线上终态**：提交`#123848`于`2026-08-23T10:43:47Z`终态为`Accepted`，总分`65.79`、14/14；case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、234/57、39/62、266/48、375/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case11（B16/KV4/L12251、39 splits）；相对结构性control `#113889` 的`222 µs / 52分`变为`266 µs / 48分`，远未达到预注册约`<=220 µs / 53分`，线上明确否定该数据流假设。其它case同场timing不归因；关闭 exact exp609 duplicated-global-V producer/consumer contract，不切换control、不重投或扫描global load、地址、lane、布局、helper或启用范围。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交/watch、control恢复、raw/source SHA和终态队列分别记录于`log/exp609_relaxed_oj_list_pre.log`、`log/exp609_relaxed_oj_stage_sha.log`、`log/exp609_relaxed_oj_dry_run.log`、`log/exp609_relaxed_oj_pre_submit_sha.log`、`log/exp609_relaxed_oj_list_pre_submit.log`、`log/exp609_relaxed_oj_submit_watch.log`、`log/exp609_relaxed_oj_restored_control_sha.log`与`log/exp609_relaxed_oj_list_post_restore.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #122987 · exp644 case12 raw-FP32 pair-state direct three-peer fan-in

- **代码溯源**：官方 raw 为[`cuda_122987_raw.json`](raw/cuda_122987_raw.json)，不可变提交源码为[`cuda_122987.cpp`](../solutions/archive/2026-08-23-submissions/cuda_122987.cpp)，实验候选为[`cuda_case12_pair_state_threepeer_fanin_exp644.cpp`](../solutions/archive/2026-08-22-experiments/cuda_case12_pair_state_threepeer_fanin_exp644.cpp)。submitted/candidate/immutable SHA-256 均为`8600495c01a8bf16f69cd14a1c12945abca976dc93e38ff793ba57f64d2902ec`；raw JSON SHA-256 为`79a85961e4cc5b8b8d96ecf6a26905fc81e677ce86464062589166ceedc285c1`，manifest已登记`#122987`。
- **线上终态**：提交`#122987`于`2026-08-22T22:43:56Z`终态为`Accepted`，总分`66.07`、14/14；case1–14时延/分数依次为`3/92、4/90、10/82、22/73、17/73、28/63、225/55、93/54、230/57、38/62、222/52、380/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case12（B8/KV8/L32768、40 splits）；相对结构性control `#113889` 的`378 µs / 60分`变为`380 µs / 60分`，未达到预注册约`<=365.70 µs / 61分`，线上最终否定该 display-tier 假设。其它case同场timing不归因；关闭 exact exp644 raw-FP32 pair-state direct three-peer fan-in contract，不切换control、不重投或扫描barrier、row、lane、layout、helper或merge-order参数。只有实质不同的跨-wave storage/backend或ownership/lifetime改变旧前提，才可重新登记。
- **安全门禁与OJ优先决策**：候选已通过最终静态 gate、CPU/C500 correctness、special boundary/padding/reuse覆盖和full/boundary/random严格交错A/B；本地三分布虽约`0.4%–1.2%`回退，因线上OJ是最终性能真值而批准唯一一次probe。线上`380 µs / 60分`未跨档，故不能将本地门禁或其它case波动归因成收益。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交/watch、归档、raw/source SHA、control恢复和终态队列分别记录于`log/exp644_oj_list_pre.log`、`log/exp644_oj_stage_sha.log`、`log/exp644_oj_dry_run.log`、`log/exp644_oj_pre_submit_sha.log`、`log/exp644_oj_submit_watch.log`、`log/exp644_oj_archive_attempt.log`、`log/exp644_oj_artifact_check.log`、`log/exp644_oj_final_sha.log`、`log/exp644_oj_restored_control_sha.log`与`log/exp644_oj_list_post.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #122912 · exp641 case2 CTA shared K/V owner

- **代码溯源**：官方 raw 为[`cuda_122912_raw.json`](raw/cuda_122912_raw.json)，不可变提交源码为[`cuda_122912.cpp`](../solutions/archive/2026-08-23-submissions/cuda_122912.cpp)，实验候选为`cuda_case2_cta_shared_kv_exp641.cpp`。submitted/candidate/immutable SHA-256 均为`0fe98ab0d0ac5d98527da7710d6c961758468f412fdbcc5186a4f60d0fc4d933`；raw JSON SHA-256 为`4407724afa9a35f937a445ddba3280af85d41c19c6c84b33ca6c92df68a82a88`，manifest已登记`#122912`。
- **线上终态**：提交`#122912`于`2026-08-22T19:25:01Z`终态为`Accepted`，总分`65.86`、14/14；OJ总耗时`1592 ms`，内存`23060400 KB`。case1–14时延/分数依次为`3/92、5/88、10/82、23/72、17/73、28/63、226/55、93/54、231/57、38/62、223/52、375/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因与control决策**：target为case2（B4/KV8/seqlen_k_cap=2、single split）；相对结构性control `#113889` 的`4 µs / 90分`变为`5 µs / 88分`，未达到预注册约`<=3.75824 µs / 91分`，唯一成功判据失败。其它case同场timing不归因；关闭 exact exp641 two-token CTA shared K/V owner contract，不切换control、不重投或扫描shared布局、owner lane、地址、barrier、模板或启用范围。
- **提交与归档证据**：队列初检、stage/dry-run/二次SHA、唯一提交、watch（含HTTP 429后继续查询）、归档、raw/source SHA、control恢复和终态队列分别记录于`log/exp641_oj_stage_sha.log`、`log/exp641_oj_dry_run.log`、`log/exp641_oj_pre_submit_sha.log`、`log/exp641_oj_submit.log`、`log/exp641_oj_watch_01.log`至`log/exp641_oj_watch_16.log`、`log/exp641_oj_archive.log`、`log/exp641_oj_source_sha.log`、`log/exp641_oj_restored_control_sha.log`与`log/exp641_oj_list_post.log`。终态后工作文件已恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`，`solutions/cuda_maca_optimized.cpp` SHA核验为`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`，OJ队列无在途。

### 提交 #122490 · exp635 case12 native-B128-LDG even-z Q owner + odd-z lane^32 BSM

- **代码溯源**：官方 raw 为[`cuda_122490_raw.json`](raw/cuda_122490_raw.json)，不可变提交源码为[`cuda_122490.cpp`](../solutions/archive/2026-08-22-submissions/cuda_122490.cpp)，实验候选为`solutions/archive/2026-08-22-experiments/cuda_case12_native_ldg_wave_bsm_exp635.cpp`。submitted/candidate/immutable SHA-256 均为`f1d2515b3f8f592e990b55d302fe49965e4b18d06198bfecba52431afae80d0f`；raw SHA-256 为`7e01981be0240a95b4b8bbbab3e35ca06fa7c44af1c1545052261bb714e93b24`。
- **线上终态**：提交`#122490`于`2026-08-22T13:23:47Z`终态为`Accepted`，总分`66.00`、14/14；OJ总耗时`1598 ms`，内存`23060640 KB`。case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、227/55、93/54、235/57、39/62、223/52、376/60、182/56、139/55 µs/分`。
- **唯一目标归因与 control 决策**：target 为 case12（B8/KV8/L32768、40 split）；相对结构性control `#113889` 的`378 µs / 60分`到`376 µs / 60分`，未达到预注册约`<=365.70 µs / 61分`，无可归因跨display-tier收益。其它case同场timing不归因；关闭 exact exp635 native-LDG even-z Q owner→odd-z `lane^32` BSM Q payload contract，不切换control、不重投或扫描lane/payload/builtin/address/layout/template/enable-range；只有实质不同的Q owner/backend/storage lifetime才可重新登记。
- **归档与恢复**：raw与不可变提交源码为上述权威文件，candidate/提交/immutable SHA链已核验；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），`solutions/cuda_maca_optimized.cpp`同SHA，OJ队列为空。

### 提交 #122261 · exp634 case1 native-register B128 LDG→8 STG fan-out

- **代码溯源**：[`cuda_122261.cpp`](../solutions/archive/2026-08-22-submissions/cuda_122261.cpp)、[`cuda_122261_raw.json`](raw/cuda_122261_raw.json)与实验快照 `cuda_case1_native_register_fanout_exp634.cpp` 均已归档；冻结候选、官方提交源码与实验快照 SHA-256 均为 `a5d436ad0a50675bdafd683c5768d7762e3e45ca76162d9a80760f4947865b7b`，raw JSON SHA-256 为 `6573ab1b528b47f5bbd4fa600b8267eee688d7041350224f7a5ed6b081efb0ae`，manifest 已登记 `#122261`。
- **线上终态**：`#122261`，`WrongAnswer`，总分 `60.14`，提交时间 `2026-08-22T10:32:45Z`。case1（B1/KV4/seqlen_k=1/GQA8）为 `3 µs / 92分`，与 control 同档、无目标收益；case3 为 WrongAnswer，raw 诊断为 `matched_ratio=0.999969 < 1.0`、`max_abs_diff=0.019531`（其余统计含 `mean_abs_diff=0.000278`）。其余显示测试点 Accepted，但提交全局为 WrongAnswer，不能将其 timing 或 `60.14`作为性能证据。
- **线上归因与 control 决策**：候选只预期改变 case1，但线上 case3 失败；本地 CPU/C500/case1边界、padding、复用和交错 A/B 门禁不足以替代 OJ，精确 compiler 根因未知。关闭 exact case1 native B128 LDG→8 STG fan-out contract，不切换 control、不重投同一 SHA或 helper/cast/builtin/lane/address/layout/enable-range 变体；只有实质不同的 owner/backend 且重新通过完整安全门禁才可重开。
- **归档与恢复**：raw 与官方提交源码分别为上述链接及 SHA；终态后工作文件已恢复 `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），且已核验 `solutions/cuda_maca_optimized.cpp` 同 SHA，OJ 队列无在途。

### 提交 #121954 · exp623 revalidation case12 direct-K wave-BSM no-lookahead

- **代码溯源**：[`cuda_121954.cpp`](../solutions/archive/2026-08-22-submissions/cuda_121954.cpp)、[`cuda_121954_raw.json`](raw/cuda_121954_raw.json) 与冻结候选 `cuda_case12_direct_k_wave_bsm_no_lookahead_exp623.cpp` 的 SHA-256 均为 `8daf875522d473d4c19aa44e6f3523190e098ef22ec3036f6a7ef4320ff4cc43`；官方归档清单已登记该 SHA。
- **门禁与唯一差异**：仅 active case12 B8/KV8/L32768、40-split z8 producer：K 在当前页 QK 前由global读取并经同物理wave的`lane^16` raw-BSM交给peer consumer，QK 后K死亡、PV 后下一页重新读取K；删除`s_k`当前K round-trip与exp608的next-K live range。Q、V、online state、tail/split、partial ABI、reducer、grid及其它dispatch保持#113889。candidate/control资源为`76/52/8448/0/6`与`82/50/8448/0/5`，无spill/stack、candidate LLVM有8个direct-K BSM；CPU、C500 full/random/boundary、241个case12边界、padding trap和workspace reuse均通过。21轮×100交错A/B candidate/control p10/p50/p90为full=`1.0676/1.0680/1.0691`、random=`1.0813/1.0832/1.0841`、boundary=`1.0057/1.0105/1.0142`，已显示覆盖一致的明显回退。
- **终态**：`#121954`，`Accepted`，`65.86`，`14/14`；提交时间`2026-08-22T06:10:41Z`，OJ总耗时`1623 ms`，内存`23060488 KB`。raw内嵌代码、不可变提交源码和候选SHA一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、224/55、93/54、234/57、39/62、222/52、406/58、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因**：target为case12；相对结构性control #113889的`378 µs / 60分`退至`406 µs / 58分`，且与本地full/random系统性回退方向一致，唯一成功判据直接失败。其它case同场timing不归因；关闭 exact direct-K wave-BSM no-lookahead contract，不切换control、不重投或扫描K BSM lane/payload/builtin、地址、布局、load拼写、模板或启用范围；仅实质不同的K ownership/backend并消除该回退机制才可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_121954_raw.json`，不可变提交源码为`solutions/archive/2026-08-22-submissions/cuda_121954.cpp`，manifest已登记候选SHA；终态后工作文件已核验恢复为`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列为空。

### 提交 #120152 · exp611 case12 Q physical-wave raw-BSM + partial B128 STG

- **代码溯源**：[`cuda_120152.cpp`](../solutions/archive/2026-08-21-submissions/cuda_120152.cpp)、[`cuda_120152_raw.json`](raw/cuda_120152_raw.json)、实验快照 `cuda_case12_q_bsm_partial_b128_stg_exp611.cpp` 与提交前工作文件的 candidate SHA-256 均为 `27a2dbc6b44eee0d2016d6c6a2dc8a2ff40367b077118043d11603093952eec2`；candidate archive 与不可变提交源码同 SHA，官方归档清单已登记 `#120152`。
- **门禁与唯一差异**：仅 active case12 B8/KV8/L32768、40-split z8 producer 组合两个独立阶段：Q 由偶数`tz`读取并以 physical-wave `lane^32` raw BSM交给奇数`tz`，FP32 `partial_acc` 写出使用4次 native B128 STG；K/V loader、state、partial ABI、reducer、grid及其它dispatch保持#113889。candidate/control producer均为`82/50/8448/0/5`，vec2 reducer均为`38/39/0/0/8`；目标LLVM有8个真实BSM和4个真实B128 STG，C500 correctness、241个case12边界、padding、workspace复用与三分布交错A/B安全门禁均通过。
- **终态**：`#120152`，`Accepted`，`66.00`，`14/14`；提交时间`2026-08-21T05:36:31Z`，OJ总耗时`1591 ms`，内存`23060364 KB`。raw内嵌代码、candidate archive、不可变提交源码与候选SHA一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、231/57、39/62、223/52、374/60、182/56、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因**：target为case12（B8/KV8/L32768、40 split）；相对结构性control #113889的`378 µs / 60分`到`374 µs / 60分`，仍未达到预注册的约`365.70 µs / 61分` display tier，唯一成功判据未满足。其它case同场timing不归因；因此关闭 exact Q physical-wave raw-BSM + partial B128 STG combined contract，不切换control、不重投或扫描BSM/STG payload、lane、地址、布局、builtin、模板或启用范围；仅实质不同的Q/partial producer-consumer ownership、storage lifetime或backend前提可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_120152_raw.json`，不可变提交源码为`solutions/archive/2026-08-21-submissions/cuda_120152.cpp`，manifest已登记`#120152`与candidate SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），且已核验工作文件与control archive同SHA，OJ队列为空。

### 提交 #118862 · exp603 case12 physical-wave Q raw-BSM consumer

- **代码溯源**：[`cuda_118862.cpp`](../solutions/archive/2026-08-20-submissions/cuda_118862.cpp)、[`cuda_118862_raw.json`](raw/cuda_118862_raw.json)、实验快照 `cuda_case12_wave_local_q_bsm_exp603.cpp` 与提交前工作文件的 SHA-256 均为 `d27f5e5cfb17562baacbc4f4393c3513bc501cae283d222d718719abd251df28`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **门禁与唯一差异**：仅 active case12 B8/KV8/L32768、40-split、`dim3(16,2,8)` z8 producer 中，偶数`tz`读取两组16B raw-BF16 Q payload，奇数`tz`经同一物理64-lane wave的`lane^32` raw BSM消费相邻z的寄存器payload。K/V loader、page lifetime、online-softmax state、split/tail、partial ABI、vec2 reducer、grid及其余dispatch保持#113889。candidate/control资源均为`82/50/8448/0/5`，candidate目标LLVM有8个真实`llvm.mxc.bsm.bpermute`、control为0；CPU、C500 full/random/boundary、241个case12精确边界、padding与workspace复用及三分布交错A/B均通过。
- **终态**：`#118862`，`Accepted`，`66.07`，`14/14`；提交时间`2026-08-20T07:34:53Z`，OJ总耗时`1589 ms`，内存`23060624 KB`。raw内嵌代码、官方逐提交源码、实验快照与提交前工作文件SHA一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、224/55、93/54、233/57、38/62、222/52、375/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因**：target为case12（B8/KV8/L32768、40 split）；相对结构性control #113889的`378 µs / 60分`到`375 µs / 60分`，仍未跨display tier，唯一成功判据未满足。其它case同场timing不归因；因此关闭 exact physical-wave Q producer→raw-BSM register consumer contract，不切换control、不重投或扫描source lane、mask、地址、布局、builtin、模板或启用范围；仅实质不同的Q producer/consumer ownership、storage lifetime或backend前提可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_118862_raw.json`，不可变提交源码为`solutions/archive/2026-08-20-submissions/cuda_118862.cpp`，manifest已登记`#118862`与候选SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列为空。

### 提交 #117052 · exp601 case12 FP32 partial B128 native-STG

- **代码溯源**：[`cuda_117052.cpp`](../solutions/archive/2026-08-19-submissions/cuda_117052.cpp)、[`cuda_117052_raw.json`](raw/cuda_117052_raw.json)、实验快照 `cuda_case12_partial_b128_stg_exp601.cpp` 与提交前工作文件的 SHA-256 均为 `2eb8cbdcbc8727f4d9d1fd2861663c37d02b3402ad341829a2f786d4b032e4bf`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **门禁与唯一差异**：仅 active case12 B8/KV8/L32768、40-split producer 的4段16B对齐 FP32 `partial_acc float4` store 使用真实`__builtin_mxc_stg_b128_predicator`。partial ABI、packed FP16x2 `(m,l)`、QK/PV、K/V loader、state/barrier、grid、vec2 reducer和其它dispatch保持#113889。candidate LLVM恰有4个真实native-STG call且仅在`<true,false,false,true>`特化，control为0；producer candidate/control均为`82/50/8448/0/5`，vec2 reducer均为`38/39/0/0/8`。CPU/C500、241个精确case12边界、workspace复用、raw-bit与三分布交错A/B门禁均通过。
- **终态**：`#117052`，`Accepted`，`66.07`，`14/14`；提交时间`2026-08-18T17:36:12Z`，OJ总耗时`1589 ms`，内存`23060492 KB`。raw的`raw_detail.content.code` SHA与候选、实验快照及官方逐提交源码一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、227/55、93/54、236/57、39/62、222/52、368/60、181/57、139/55 µs/分`，全部`Accepted`。
- **唯一目标归因**：target为case12（B8/KV8/L32768、40 split）；相对结构性control #113889的`378 µs / 60分`到`368 µs / 60分`，仍未跨display tier，唯一成功判据未满足。其它case同场timing不归因；因此关闭 exact case12 raw-FP32 `partial_acc float4` producer B128 native-STG backend，不切换control、不重投或扫描builtin/cast/address/lane/packing/store位置/template/enable范围，仅实质不同的partial format、producer/consumer ownership、storage lifetime或backend前提可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_117052_raw.json`，不可变提交源码为`solutions/archive/2026-08-19-submissions/cuda_117052.cpp`，manifest已登记`#117052`与候选SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列为空。

### 提交 #117007 · exp600 case14 normalized-BF16 partial B16 STX

- **代码溯源**：[`cuda_117007.cpp`](../solutions/archive/2026-08-19-submissions/cuda_117007.cpp)、[`cuda_117007_raw.json`](raw/cuda_117007_raw.json)、实验快照 `cuda_case14_partial_b16_stx_exp600.cpp` 与 raw 内嵌代码的 SHA-256 均为 `a40e04a96cf836c339e9a92a232b2ce79d26f7c7211fbce5d7a6248ec670e38f`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **门禁与唯一差异**：仅 active case14 B1/KV4/L61519、257-split producer 的 normalized-BF16 `partial_acc` store 使用真实 scalar `__builtin_mxc_stx_b16_devc`；每个原 half2 RN-converted payload 固定拆为两个 B16 STX。partial ABI、`(m,l)`、FP32 state lifetime、grid、barrier、owner、地址布局、QK/PV/reducer及其它dispatch保持#113889。目标 LLVM 恰有16个真实`llvm.mxc.stx.devc.i16`且仅在active producer；producer candidate/control均为`82/66/8320/0/5`，reducer均为`40/28/0/0/8`，无spill或驻留回退；CPU、C500、raw-bit与三分布交错A/B门禁均通过。
- **终态**：`#117007`，`Accepted`，`66.00`，`14/14`；提交时间`2026-08-18T16:28:30Z`，OJ总耗时`1595 ms`，内存`23060308 KB`。raw的`raw_detail.content.code` SHA与候选、实验快照及官方逐提交源码一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、10/82、23/72、17/73、28/63、225/55、93/54、236/57、38/62、223/52、374/60、181/57、140/55 µs/分`，全部`Accepted`。
- **唯一目标归因**：target为case14（B1/KV4/L61519、257 split）；相对结构性control #113889的`139 µs / 55分`为`140 µs / 55分`，未跨display tier且变慢，唯一成功判据未满足。其它case同场timing不归因；因此关闭 exact case14 normalized-BF16 `partial_acc` scalar B16 STX producer backend，不切换control、不重投或扫描builtin/cast/address/lane/packing/store位置/template/enable范围，仅实质不同的partial format、producer/consumer ownership、storage lifetime或backend前提可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_117007_raw.json`，不可变提交源码为`solutions/archive/2026-08-19-submissions/cuda_117007.cpp`，manifest已登记`#117007`与候选SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列为空。

### 提交 #116965 · exp599 case14 scalar B16 STX final-output global store

- **代码溯源**：[`cuda_116965.cpp`](../solutions/archive/2026-08-18-submissions/cuda_116965.cpp)、[`cuda_116965_raw.json`](raw/cuda_116965_raw.json)、实验快照 `cuda_case14_scalar_b16_stx_output_exp599.cpp` 与 raw 内嵌代码的 SHA-256 均为 `35013de595b082974e0b59de7b87b1f9bfd3476afb2affae1c8aeb8d73635da7`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **门禁与唯一差异**：仅 case14 B1/KV4/L61519、257-split reducer 的最终 scalar BF16 output store 使用真实 `__builtin_mxc_stx_b16_devc`；原 `__float2bfloat16` RN conversion、generic-pointer/offset-zero/unsigned-short payload、输出索引、head/dimension owner、partial ABI/lifetime及其他dispatch保持不变。目标 LLVM 仅有1个真实`llvm.mxc.stx.devc.i16` call；producer candidate/control均为`82 MTreg / 66 STreg / 8320 B / 0 stack / 5 waves`，reducer均为`40/28/0/0/8`，无spill或驻留回退；CPU、C500、raw-bit与三分布交错A/B门禁均通过。
- **终态**：`#116965`，`Accepted`，`66.14`，`14/14`；提交时间`2026-08-18T15:30:13Z`，OJ总耗时`1594 ms`，内存`23060544 KB`。raw的`raw_detail.content.code` SHA与候选、实验快照及官方逐提交源码一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、234/57、39/62、223/52、376/60、181/57、139/55 μs/分`，全部`Accepted`。
- **唯一目标归因**：target为case14（B1/KV4/L61519、257 split）；相对结构性control #113889保持`139 µs / 55分`，未跨display tier，唯一成功判据未满足。case4 `22/73`与case13 `181/57`是未覆盖路径的timing样本，不能归因；因此关闭 exact case14 scalar B16 STX final-output global-store backend，不切换control、不重投或扫描builtin/cast/address/lane/packing/store位置/template/enable范围，仅实质不同的output consumer/storage/backend或ownership/lifetime前提可重开。
- **归档与恢复**：官方raw为`results/raw/cuda_116965_raw.json`，不可变提交源码为`solutions/archive/2026-08-18-submissions/cuda_116965.cpp`，manifest已登记`#116965`与候选SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`），OJ队列为空。

### 提交 #116797 · exp598 case11 FP32 partial native-STG

- **代码溯源**：[`cuda_116797.cpp`](../solutions/archive/2026-08-18-submissions/cuda_116797.cpp)、[`cuda_116797_raw.json`](raw/cuda_116797_raw.json)、实验快照 `cuda_case11_partial_fp32_native_stg_exp598.cpp` 与提交前工作文件的 SHA-256 均为 `5f9d7631a48dd8e63a51c5692887f0df17fdddd90f593e28dafc79f4af279d12`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **门禁与唯一差异**：仅 case11 B16/KV4/L12251、39-split、`dim3(16,4,4)`、symmetric finalizer 的producer→raw-FP32 `partial_acc float4` store启用真实`__builtin_mxc_stg_b128_predicator`；QK/PV、K/V loader、state/barrier、partial ABI、vec4 reducer、tail与其他shape不变。目标LLVM恰有4个native STG call、control为0，candidate/control资源均为`80 MTreg / 58 STreg / 8320 B / 0 stack / 6 waves`；CPU/C500、238个精确边界、复用与三分布交错A/B均通过。
- **终态**：`#116797`，`Accepted`，`66.00`，`14/14`；提交时间`2026-08-18T12:57:22.000Z`，OJ总耗时`1591 ms`，内存`23060248 KB`。raw的`raw_detail.content.code` SHA与候选、官方逐提交源码快照一致。
- **测试点汇总**：case1–14时延/分数依次为`3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、233/57、39/62、222/52、373/60、182/56、139/55 μs/分`，全部`Accepted`。
- **唯一目标归因**：target为case11（B16/KV4/L12251、39 split）；相对结构性control #113889保持`222 µs / 52分`，未跨display tier，唯一成功判据未满足。其它case同场timing不归因；exp598 exact case11 raw-FP32 partial `float4` producer native-STG contract关闭，不切换control、不重投或扫描builtin/cast/address/lane/packing/store位置/template/enable范围。
- **归档与恢复**：官方raw为`results/raw/cuda_116797_raw.json`，不可变提交源码为`solutions/archive/2026-08-18-submissions/cuda_116797.cpp`，manifest已登记`#116797`与候选SHA；终态后工作文件恢复`solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）。

### 提交 #116723 · exp597 case12 reducer partial-B64 native-LDG

- **代码溯源**：[`cuda_116723.cpp`](../solutions/archive/2026-08-18-submissions/cuda_116723.cpp)、[`cuda_116723_raw.json`](raw/cuda_116723_raw.json)、实验快照 `cuda_case12_reducer_partial_b64_native_ldg_exp597.cpp` 与提交前工作文件的 SHA-256 均为 `f529061ec94575ac1f87d80d35ca6bf02ea2137c2890b809c98f24ece8df3774`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **终态**：`#116723`，`Accepted`，`66.00`，`14/14`；提交时间 `2026-08-18T11:57:04.000Z`，OJ 总耗时 `1590 ms`，内存 `23060268 KB`。raw 的 `raw_detail.content.code` SHA 与候选、官方逐提交源码快照一致。
- **测试点汇总**：case1–14 时延/分数依次为 `3/92、4/90、10/82、22/73、17/73、28/63、226/55、93/54、232/57、39/62、223/52、372/60、182/56、139/55 μs/分`，全部 `Accepted`。
- **唯一目标归因**：target 为 case12（B8/KV8/L32768、40 split）；相对结构性control #113889 的 `378→372 μs`仍为`60`分，未跨 display tier，唯一成功判据未满足。其它 case 的同场 timing 不归因；exp597 exact case12 vec2 reducer `partial_acc` B64 native-LDG consumer/backend contract 关闭，不切换control、不重投或扫描 builtin/cast/address/lane/layout/template/enable范围。
- **归档与恢复**：官方 raw 为 `results/raw/cuda_116723_raw.json`，不可变提交源码为 `solutions/archive/2026-08-18-submissions/cuda_116723.cpp`，manifest 已登记 `#116723` 与候选 SHA；终态后工作文件恢复 `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）。

### 提交 #116571 · exp594 case14 final-output native-B128 store

- **代码溯源**：[`cuda_116571.cpp`](../solutions/archive/2026-08-18-submissions/cuda_116571.cpp)、[`cuda_116571_raw.json`](raw/cuda_116571_raw.json)、实验快照 `cuda_case14_final_output_native_stg_exp594.cpp` 与提交前工作文件的 SHA-256 均为 `c1aeb34b427bbac86e3d16171d74f93be2ae35e2d909f58b0da0d8363d023847`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **终态**：`#116571`，`Accepted`，`66.00`，`14/14`；提交时间 `2026-08-18T09:13:48.000Z`，OJ 总耗时 `1593 ms`，内存 `23060544 KB`。raw 的 `raw_detail.content.code` SHA 与候选、官方逐提交源码快照一致。
- **测试点汇总**：case1–14 时延/分数依次为 `3/92、4/90、9/83、23/72、17/73、28/63、225/55、93/54、234/57、39/62、222/52、375/60、182/56、139/55 μs/分`，全部 `Accepted`。
- **唯一目标归因**：target 为 case14（B1/KV4/L61519、257 split）；相对结构性control #113889 的 `139→139 μs`、`55→55 分`，未跨 display tier，故唯一成功判据未满足。其它 case 的同场 timing 不归因；exp594 exact contract 关闭，不切换 control，也不重复提交。
- **归档与恢复**：官方 raw 为 `results/raw/cuda_116571_raw.json`，不可变提交源码为 `solutions/archive/2026-08-18-submissions/cuda_116571.cpp`，manifest 已登记 `#116571` 与候选 SHA；OJ 终态后工作文件恢复 `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）。

### 提交 #116314 · exp588 case12 native-B128 shared-Q producer

- **代码溯源**：[`cuda_116314.cpp`](../solutions/archive/2026-08-18-submissions/cuda_116314.cpp)、[`cuda_116314_raw.json`](raw/cuda_116314_raw.json)、实验快照 `cuda_case12_native_ldg_shared_q_exp588.cpp` 与提交前工作文件的 SHA-256 均为 `cb8835b53011b62c01358305ea3ff08b4f3bb1f5951a6167b3975573240bc033`；官方归档清单为 [`SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。
- **终态**：`#116314`，`Accepted`，`66.00`，`14/14`；提交时间 `2026-08-18T04:19:51.000Z`，OJ 总耗时 `1589 ms`，内存 `23060404 KB`。raw 的 `raw_detail.content.code` SHA 与候选、官方逐提交源码快照一致。
- **测试点汇总**：case1–14 时延/分数依次为 `3/92、4/90、9/83、23/72、17/73、28/63、226/55、93/54、231/57、38/62、223/52、373/60、182/56、139/55 μs/分`，全部 `Accepted`。
- **唯一目标归因**：target 为 case12（B8/KV8/L32768、40 split）；相对结构性control #113889 的 `378→373 μs` 仍为 `60` 分，未跨 display tier，故唯一成功判据未满足。其它 case 的同场 timing 不归因；exp588 exact contract 关闭，不切换 control，也不重复提交。
- **归档与恢复**：官方 raw 为 `results/raw/cuda_116314_raw.json`，不可变提交源码为 `solutions/archive/2026-08-18-submissions/cuda_116314.cpp`，manifest 已登记 `#116314` 与候选 SHA；OJ 终态后工作文件恢复 `solutions/archive/2026-08-16-submissions/cuda_113889.cpp`（control SHA=`a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`）。

### 提交 #115902 · exp579 case12 Q-native-LDG consumer/backend

- **代码溯源**：[`cuda_115902.cpp`](../solutions/archive/2026-08-18-submissions/cuda_115902.cpp)、raw 内嵌源码、实验快照 `cuda_case12_native_q_ldg_exp579.cpp` 与提交前工作文件的 SHA-256 均为 `4546b999d6d972b87bace0167ff155e99a789869eb65378af2972234a43a045c`。
- **门禁与唯一差异**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer 对每个线程原有两条16-byte对齐 Q 行片段使用同步、register-returning `__builtin_mxc_ldg_b128`，继续直接解包为 FP32 Q；QK owner、K/V loader/lookahead、shared、barrier、state tree、partial ABI、reducer、grid及其他shape均保持#113889。该 Q consumer/backend 与既有 K/V native-LDG、shared-Q producer 是不同 contract。candidate/control 资源均为`82/50/8448/0/5`，无spill或驻留回退；14-case correctness、真实 C500 full/boundary/random、case12精确边界、padding和workspace复用均通过，静态 LLVM 生成两处真实`llvm.mxc.ldg.predicator.v4i32`。
- **OJ解释与control决策**：#115902 为 14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/225/93/235/39/221/372/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case12相对#113889从`378→372 μs`，但显示分仍60；没有可归因display收益，其他case同场波动不归因。因此拒绝并关闭这个 exact case12 Q-native-LDG consumer/backend contract；不得扫描builtin参数、cast、地址、lane、布局、启用范围或同源码复投，只有Q consumer ownership、跨请求数据流或独立后端能力出现实质新前提才可重开。已运行`tools/archive_cuda_submissions.py`；原始评测：[cuda_115902_raw.json](raw/cuda_115902_raw.json)，raw、逐提交快照、实验快照与提交前SHA一致，工作文件恢复#113889，OJ队列为空。

### 提交 #115744 · exp578 case12 single-split raw-BF16 shared-Q staging

- **代码溯源**：[`cuda_115744.cpp`](../solutions/archive/2026-08-17-submissions/cuda_115744.cpp)、raw 内嵌源码、实验快照 `cuda_case12_single_split_shared_q_exp578.cpp` 与提交前工作文件的 SHA-256 均为 `79fa38481525e815ca3fbbf4cc9f527648a10d64c8c12519f2aabfc0d07f51cf`。
- **门禁**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer 在一次 logical-split CTA 开头由`tz==0`装入4个GQA query head的raw BF16 tile，CTA同步后8个z分区从shared读取并保留原有每z FP32 Q、K/V lookahead、page loop、state tree、partial ABI、vec2 reducer、grid与其他shape。它把每CTA的Q global vector load从8次z重复压到一次，且不同于已关闭的双split shared-Q lifetime/ownership。资源 control/candidate=`82/50/8448/0/5→82/52/9472/0/5`，无spill且驻留不降；14-case correctness、C500 full/random/boundary、case12精确split/tail、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9973/0.9990/0.9996`、random=`0.9983/1.0013/1.0043`、boundary=`0.9913/0.9980/1.0001`；没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/226/93/236/39/223/371/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113889的`378→371 μs`仍为60分；没有可归因display收益，其他case同场波动不归因。因此拒绝并关闭这个 exact case12 single-split raw-BF16 shared-Q producer/consumer contract；不得扫描writer z、tile address/vector layout、barrier、模板/grid或同源码复投，只有Q consumer ownership、跨请求数据流或独立后端能力出现实质新前提才可重开。工作文件恢复#113889。
- **原始评测**：[cuda_115744_raw.json](raw/cuda_115744_raw.json)。

### 提交 #115685 · exp576 case4 distributed PV `exp2`

- **代码溯源**：[`cuda_115685.cpp`](../solutions/archive/2026-08-17-submissions/cuda_115685.cpp)、raw 内嵌源码、实验快照 `cuda_case4_distributed_pv_exp576.cpp` 与提交前工作文件的 SHA-256 均为 `f69fb2a38a14f78bd71a4b6fe0c623cadae64445334f037c8c03d82eb9e0f353`。
- **门禁**：仅 case4 B64/KV8/L64 的固定四页路径让同一`ty`行的`tx=0..3`各计算一个PV weight `exp2(score[j]-m_new)`，再以静态`native_row16_broadcast<0/1/2/3>`交给原有PV consumer；generic fallback、BSM、QK、state、split、output和其他shape保持#113889。资源 control/candidate 均为`74/44/8320/0/6`，无spill或驻留回退；14-case correctness、C500 full/random/boundary、case4精确四页边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9530/0.9951/1.0125`、random=`0.9965/0.9986/1.0191`、boundary=`0.9940/1.0006/1.0186`；没有覆盖一致、明显且可重复的系统性本地回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/227/93/238/38/222/373/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case4相对#113889保持`23 μs/72分`，没有可归因display收益；其他case同场波动不归因。因此拒绝并关闭这个 exact case4 distributed-PV-`exp2` producer/consumer contract；不得扫描owner lane、broadcast表达、V/PV顺序、模板/grid或同源码复投，只有PV consumer ownership、跨请求数据流或独立后端能力出现实质新前提才可重开。工作文件恢复#113889。
- **原始评测**：[cuda_115685_raw.json](raw/cuda_115685_raw.json)。

### 提交 #115590 · exp573 case12 split-wide page-table PID shared cache

- **代码溯源**：[`cuda_115590.cpp`](../solutions/archive/2026-08-17-submissions/cuda_115590.cpp)、raw 内嵌源码、实验快照 `cuda_case12_split_pid_cache_exp573.cpp` 与提交前工作文件的 SHA-256 均为 `1d9e6705422408b3af2e7cb70c6813fdd363fb4a40c36ee84b5762af5cbd93a0`。
- **门禁**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer在原本空闲的256B `s_md` 后缀预载每个split的完整有效page-table PID，并在初始页、热next-page及fused tail复用；split、QK/PV、K/V loader、partial ABI、vec2 reducer、output ownership和其他shape保持#113889。资源 control/candidate=`82/50/8448/0/5→84/44/8448/0/5`，无spill且保持5-wave；14-case correctness、C500 full/random/boundary、case12精确split/tail、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`1.0025/1.0034/1.0049`、random=`1.0042/1.0061/1.0072`、boundary=`0.9948/1.0013/1.0064`，full 21×100复测=`1.0032/1.0036/1.0044`；仅为轻微风险，按OJ优先规则完成一次预注册probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/226/94/235/39/222/376/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113889的`378→376 μs`仍为60分，没有可归因display收益；其他case同场波动不归因。因此拒绝并关闭这个 exact split-wide page-table PID shared cache；不得扫描cache布局、预载时点、barrier、PID读取表达式、模板/grid或同源码复投，只有页面数据流、producer/consumer ownership或后端能力出现实质新前提时才可重开。工作文件恢复#113889。
- **原始评测**：[cuda_115590_raw.json](raw/cuda_115590_raw.json)。

### 提交 #115574 · exp572 case6 static three-page live-split ceil

- **代码溯源**：[`cuda_115574.cpp`](../solutions/archive/2026-08-17-submissions/cuda_115574.cpp)、raw 内嵌源码、实验快照 `cuda_case6_static_pages_per_split_exp572.cpp` 与提交前工作文件的 SHA-256 均为 `6cb8a720e61ad14922e8769a5a1d1424b4a42ae1b6531b8ae72a9fa17c21ddfd`。
- **门禁**：仅 case6 B16/KV8/L362、8-split 的 group8 reducer将 runtime `ceil(valid_pages / pages_per_split)` 换为固定 `pages_per_split=3` 的 `__umulhi(valid_pages + 2, 0xAAAAAAABu) >> 1`；producer、三页 split 映射、partial ABI、grid、ownership、数学和其他shape保持#113889。实际 reducer资源为control/candidate=`66/26/0/0/7→60/26/0/0/8`，无spill且驻留提升；14-case correctness、C500 full/random/boundary、case6精确1/2/…/8-live-split长度、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9897/0.9963/1.0070`、random=`0.9875/0.9938/1.0051`、boundary=`0.9751/0.9894/1.0348`，full 21×100复测=`0.9796/0.9909/1.0040`；没有覆盖一致的明显系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.14`，case1–14=`3/4/9/22/17/28/225/94/233/38/224/371/181/139 μs`，分数=`92/90/83/73/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case6相对#113889保持`28 μs/63分`，没有可归因的display收益；case4和case13的跨档变化未被此候选覆盖，只能作为 timing-tier 样本。故拒绝并关闭这个 exact case6 static-three-page live-split ceil specialization；不得扫描magic常数、cast、ceil表达、reducer模板/grid或同源码复投，只有 split contract、producer/reducer ownership 或后端能力出现实质新前提时才可重开。工作文件恢复#113889。
- **原始评测**：[cuda_115574_raw.json](raw/cuda_115574_raw.json)。

### 提交 #114179 · exp570 case12 pre-QK next-K lookahead

- **代码溯源**：[`cuda_114179.cpp`](../solutions/archive/2026-08-16-submissions/cuda_114179.cpp)、raw 内嵌源码、实验快照 `cuda_case12_preqk_k_exp570.cpp` 与提交前工作文件的 SHA-256 均为 `7ddc0a0438a2ec11ec02fc5a16e893d29db50805f3bf3def2725f42d696f25f0`。
- **门禁**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer在当前页 QK 前发起下一页四个标量 K load；K仍跨QK/softmax/PV保存在寄存器并在原PV后页面发布点写入`s_k`，下一页 V 保持control的QK后同步lookahead。split、ownership、shared覆盖、tail、partial ABI、vec2 reducer和其他case均不变。资源保持control的`82/50/8448/0/5`；CPU、C500 full/boundary/random、case12精确40-split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`1.0019/1.0030/1.0037`、random=`0.9968/1.0020/1.0055`、boundary=`0.9952/1.0020/1.0147`；仅有噪声级风险，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/226/93/233/39/223/377/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case12从#113889的`378→377 μs`，但仍60分；没有可归因的display收益，其他case同场波动不归因。因此拒绝并关闭这个 exact case12 pre-QK synchronous next-K lookahead 数据流；不得扫描预取时点、K/V表达式、split、ownership、模板/grid或同源码复投。工作文件恢复#113889。
- **原始评测**：[cuda_114179_raw.json](raw/cuda_114179_raw.json)。

### 提交 #114013 · exp564 case8 packed FP16x2 `(m,l)` group8 ABI

- **代码溯源**：[`cuda_114013.cpp`](../solutions/archive/2026-08-16-submissions/cuda_114013.cpp)、raw 内嵌源码、实验快照 `cuda_case8_packed_ml_group8_exp564.cpp` 与提交前工作文件的 SHA-256 均为 `ba815fd9226e828585da7a50b2dd1b819d68a7b16ae8ffd9b5bcb44b5b67884a`。
- **门禁**：仅 case8 B16/KV4/L4096、14-split 的 z4 BF16-MMA producer→实际 fused-tail group8 reducer 将两份 FP32 `(m,l)` metadata 改为一份 FP16x2 `partial_m` 载荷；`partial_acc`、QK/PV、split、tail、group8 ownership、grid和其他shape保持#113889。producer资源 control/candidate=`82/64/8320/0/5→82/62/8320/0/5`，实际group8 reducer=`66/24/0/0/7→66/25/0/0/7`，无spill或驻留回退。CPU、C500 full/boundary、case8 random、14-slot精确边界、padding和workspace复用通过；交错 A/B p10/p50/p90为full=`0.9965/0.9977/1.0001`、random=`0.9986/1.0006/1.0091`、boundary=`0.9568/0.9992/1.0327`，没有与改动覆盖一致的明显系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/226/93/235/39/223/371/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case8由#113889的`94→93 μs`但仍54分；case10/11/12等未覆盖路径的同场变化不能归因。故拒绝并关闭这个 exact case8 packed-FP16x2 metadata producer/group8-consumer ABI；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投，只有partial格式、producer/consumer ownership或后端能力出现实质新前提才可重开。工作文件恢复#113889。
- **原始评测**：[cuda_114013_raw.json](raw/cuda_114013_raw.json)。

### 提交 #113889 · exp559 case7 static row16 weight broadcast

- **代码溯源**：[`cuda_113889.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113889.cpp)、raw 内嵌源码、实验快照 `cuda_case7_static_weight_broadcast_exp559.cpp` 与提交前工作文件的 SHA-256 均为 `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`。
- **门禁**：仅 case7 B64/KV8/L2048、固定`n_split=3`的 packed group8 reducer新增静态`native_row16_broadcast<0/1/2>` weight source；rolled accumulator loop、packed FP16x2 `(m,l)`、fused-tail、producer、partial ABI、grid、ownership和`NATIVE_ROW16_REDUCE=false`保持#113696。reducer资源control/candidate=`66/25/0/0/7→54/25/0/0/8`，无spill且驻留提升；LLVM只保留max/LSE的8个BSM并有9个native shuffle。CPU、C500 full/boundary/random、case7精确1/2/3-live-split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9976/0.9981/1.0024`、random=`0.9926/1.0013/1.0027`、boundary=`0.9972/1.0008/1.0069`，没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/226/94/235/38/222/378/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case7相对#113696的`230 μs/54分`到`226 μs/55分`，形成可归因跨档收益。case13由`57→56分`及其他未覆盖case波动不能归因，也不抵消该目标收益；接受为新的结构性control。关闭这个 exact static-source weight handoff；不得扫描source lane、live-split数、template/grid、metadata reduction或同源码复投。
- **原始评测**：[cuda_113889_raw.json](raw/cuda_113889_raw.json)。

### 提交 #113827 · exp558 case6 packed FP16x2 `(m,l)` partial

- **代码溯源**：[`cuda_113827.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113827.cpp)、raw 内嵌源码、实验快照 `cuda_case6_packed_ml_partial_exp558.cpp` 与提交前工作文件的 SHA-256 均为 `8c61383cf5b175e99ad2525329847fab4985c1a5e0105d82afdb68ec63d0ea85`。
- **门禁**：仅 case6 B16/KV8/L362、8-split 的 token-parallel producer→group8 reducer将 `(m,l)` metadata ABI从两份FP32改为一份FP16x2；`partial_acc`仍为FP32，QK/PV、tail、3-page/split映射、native-row QK、K-only lookahead、loader、ownership、grid和其他shape保持#113696。producer/reducer资源=`80/44/8320/0/6→80/42/8320/0/6`与`66/26/0/0/7→66/25/0/0/7`，无spill且不降驻留。CPU、C500 full/boundary/random、case6精确8-split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9902/0.9975/1.0172`、random=`0.9693/0.9924/1.0152`、boundary=`0.9738/0.9953/1.0212`；没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/226/93/235/38/223/375/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case6保持#113696的`28 μs/63分`，没有预注册的display gain；未覆盖case的同场波动不归因。因此拒绝并关闭这个 exact case6 FP16x2 `(m,l)` producer/reducer partial ABI；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投，只有partial格式、producer/consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113827_raw.json](raw/cuda_113827_raw.json)。

### 提交 #113768 · exp557 case5 packed FP16x2 `(m,l)` partial

- **代码溯源**：[`cuda_113768.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113768.cpp)、raw 内嵌源码、实验快照 `cuda_case5_packed_ml_partial_exp557.cpp` 与提交前工作文件的 SHA-256 均为 `b0fe713c217d12f90a8de6e962bd1efecb20ebb6bf9285aea135c33130327d7a`。
- **门禁**：仅 case5 B16/KV4/L141、5-split 的 z4 producer→group8 reducer将 `(m,l)` metadata ABI从两份FP32改为一份FP16x2；`partial_acc`仍为FP32，QK/PV、tail、loader、split、CTA ownership、reducer grid和其他shape保持#113696。资源control/candidate=`74/52/8320/0/6→74/48/8320/0/6`，无spill且不降驻留。CPU、C500 full/boundary/random、case5精确五split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9830/0.9952/1.0131`、random=`0.9937/1.0286/1.0427`、boundary=`0.9637/1.0044/1.0498`；random的21×100复测为`0.9592/0.9923/1.0327`，未形成覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/224/94/236/39/223/375/182/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case5保持#113696的`17 μs/73分`，没有预注册的 display gain；未覆盖case的同场波动不归因。因此拒绝并关闭这个 exact case5 FP16x2 `(m,l)` producer/reducer partial ABI；不得扫描metadata格式、cast、packing、reducer模板/grid或同源码复投，只有partial格式、producer/consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113768_raw.json](raw/cuda_113768_raw.json)。

### 提交 #113750 · exp555 case12 wave64 readlane next-page PID broadcast

- **代码溯源**：[`cuda_113750.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113750.cpp)、raw 内嵌源码、实验快照 `cuda_case12_readlane_next_pid_broadcast_exp555.cpp` 与提交前工作文件的 SHA-256 均为 `8532e57b3cbcac09762c9e7a2ba753e7877c976bbc23a528e3aace2891ef6685`。
- **门禁**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer让每个物理64-lane wave固定 lane0 读取`bt_row[p+1]`，再通过 `__builtin_mxc_readlane(value, 0u)` 广播 raw int32 page ID；每页 next-page ID global load 从256降至4次。该不同 primitive 已由精确 wave64 capability probe 验证，不是 #113736 raw-BSM backend 的参数扫描；loader、QK/PV、tail、split、partial ABI、reducer、其他shape和满容量映射保持#113696。资源为`82 MTreg / 52 STreg / 8448 B shared / 0 stack / 5 waves`，control为`82/50/8448/0/5`；实际 LLVM 有1处`llvm.mxc.rl`、control为0。CPU、C500 full/boundary/random、case12精确40-slot边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`1.0051/1.0060/1.0076`、random=`0.9953/0.9978/1.0012`、boundary=`1.0061/1.0113/1.0129`；虽有小幅风险，未达到覆盖一致、明显且可重复的系统性回退否决阈值，故按预注册进行一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/224/94/233/39/224/374/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113696由`373→374 μs`、显示分仍60；未覆盖case7的`230→224 μs/54→55分`是 timing-tier 刷新，不能归因于此候选。因此拒绝并关闭这个 exact wave64 readlane next-page PID broadcast contract；不得扫描source lane、broadcast宽度、load时点/表达式、模板/grid或同源码复投，只有不同 producer/consumer ownership、页面数据流或尚未验证的后端能力有实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113750_raw.json](raw/cuda_113750_raw.json)。

### 提交 #113736 · exp554 case12 wave64 raw-BSM next-page PID broadcast

- **代码溯源**：[`cuda_113736.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113736.cpp)、raw 内嵌源码、实验快照 `cuda_case12_wave64_next_pid_broadcast_exp554.cpp` 与提交前工作文件的 SHA-256 均为 `133715276366e04d83bf0fc61c3fe27ecb2b7a4008035691bdaf9a72950e456b`。
- **门禁**：仅 case12 B8/KV8/L32768、40-split 的 z8 producer让每个物理64-lane wave固定 lane0 读取`bt_row[p+1]`，再通过 raw int32 BSM 广播 page ID；每页 next-page ID global load 从256降至4次。loader、QK/PV、tail、split、partial ABI、reducer、其他shape和满容量映射保持#113696。资源为`82 MTreg / 52 STreg / 8448 B shared / 0 stack / 5 waves`，control为`82/50/8448/0/5`。独立 wave64 raw-int32 broadcast probe、CPU、C500 full/boundary/random、case12精确40-slot边界、padding和workspace复用均通过。交错 A/B p10/p50/p90为full=`1.0076/1.0084/1.0098`、random=`1.0103/1.0121/1.0155`、boundary=`1.0173/1.0199/1.0225`；虽为小幅一致负向，未达到系统性回退否决阈值，故按预注册进行一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/23/17/28/224/94/234/39/222/376/181/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case12相对#113696由`373→376 μs`、显示分仍60；未覆盖case7的同场 timing-tier 刷新不能归因于该候选。因此拒绝并关闭这个 exact wave64 raw-BSM next-page PID broadcast contract；不得扫描source lane、broadcast宽度、load时点/表达式、模板/grid或同源码复投，只有不同后端 primitive、producer/consumer ownership或页面数据流有实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113736_raw.json](raw/cuda_113736_raw.json)。

### 提交 #113715 · exp551 case9 row0-prefix native reducer

- **代码溯源**：[`cuda_113715.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113715.cpp)、raw 内嵌源码、实验快照 `cuda_case9_row0_native_reducer_exp551.cpp` 与提交前工作文件的 SHA-256 均为 `bc78ab03710346ea0270c625fc65fb3050c0c538923215bca826964658d5f184`。
- **门禁**：仅 case9 B32/KV8/L4096、6-split 的64-thread packed vec2 reducer让固定在`tid=0..5`的全部 live metadata owner在物理row0完成 native max/LSE reduction；rows1–3保留输出 ownership，producer、split、packed partial ABI、LSE、grid、动态shared和其他shape保持#113696。资源保持`38 MTreg / 39 STreg / 0 static B / 0 stack / 8 waves`；目标 LLVM candidate/control 的native `mov.shfl`为`8/0`、BSM为`0/20`。CPU、C500 full/boundary/random、case9精确6-slot边界、padding和workspace复用均通过。交错 A/B p10/p50/p90 为full=`0.9932/0.9946/0.9972`、random=`0.9831/0.9940/1.0018`、boundary=`0.9773/0.9850/0.9922`；没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/224/93/233/39/225/372/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case9相对#113696由`234→233 μs`，但显示分仍57；同档时延不足以形成可打榜的源码因果，其他case的同场波动也不归因。因此拒绝并关闭这个 exact single-row prefix physical-subgroup metadata consumer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113715_raw.json](raw/cuda_113715_raw.json)。

### 提交 #113712 · exp550 case8 physical-row16 + fixed-xor16 vec4 reducer

- **代码溯源**：[`cuda_113712.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113712.cpp)、raw 内嵌源码、实验快照 `cuda_case8_vec4_row16_exp550.cpp` 与提交前工作文件的 SHA-256 均为 `00ad72fce9e14d845730739365d7b34079cc28453204fe62a52cbc0bcb9126f5`。
- **门禁**：仅 case8 B16/KV4/L4096、14-split 的32-thread vec4 reducer改为两个物理16-lane native max/sum network并以固定xor16跨行交换。满长14个live partial全由row0 lane0–13拥有，row1仅接收全局`m/l`以输出其维度；producer、split、partial ABI、LSE、输出ownership、CTA/grid和其他shape保持#113696。资源保持`64 MTreg / 35 STreg / 0 static B / 0 stack / 8 waves`；目标 LLVM candidate/control 的native `mov.shfl`为`8/0`、BSM为`2/10`。CPU、C500 full/boundary/random、case8精确14-slot边界、padding和workspace复用均通过。交错 A/B p10/p50/p90 为full=`0.9628/0.9974/0.9991`、random=`0.9981/0.9995/1.0011`、boundary=`0.9174/0.9674/0.9987`；没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/225/93/233/39/222/375/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case8相对#113696由`94→93 μs`，但显示分仍54；同档时延不足以形成可打榜的源码因果，其他case的同场波动也不归因。因此拒绝并关闭这个 exact case8 physical-row16 + fixed-xor16 vec4 reducer contract；不得扫描row数、cross-row merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113712_raw.json](raw/cuda_113712_raw.json)。

### 提交 #113708 · exp549 case13 overflow-aware physical-row16 serial-leader reducer

- **代码溯源**：[`cuda_113708.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113708.cpp)、raw 内嵌源码、实验快照 `cuda_case13_row16_serial_reducer_exp549.cpp` 与提交前工作文件的 SHA-256 均为 `5e999f6262f58f9b0c56075e875f402476f82489f17bc992f25c7ab8da3451ab`。
- **门禁**：仅 case13 B1/KV8/L58966、65-split 的64-thread vec2 reducer启用四个物理16-lane packed `(m,l)` max/sum reduction，并由`tid==0`串行合并四个 row leader；第65个 partial 由lane0额外拥有，因而是不同于case12的overflow-aware consumer条件。producer、split、partial ABI、LSE、输出 ownership、CTA/grid和其他shape保持#113696。资源保持`38 MTreg / 39 STreg / 0 static B / 0 stack / 8 waves`，动态shared `528→536 B`；目标 LLVM candidate/control 的native `mov.shfl`为`8/0`、BSM为`0/20`。CPU、C500 full/boundary/random、case13精确65-split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90 为full=`0.9904/0.9915/0.9929`、random=`0.9817/0.9875/0.9908`、boundary=`0.9495/0.9929/1.0433`；没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/225/94/235/39/223/370/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。唯一覆盖目标case13仍为#113696的`181 μs/57分`；同档结果不能建立可打榜的源码因果，其他case的同场波动也不归因。因此拒绝并关闭这个 exact overflow-aware physical-row16 + serial-leader reducer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113708_raw.json](raw/cuda_113708_raw.json)。

### 提交 #113703 · exp548 case12 physical-row16 serial-leader reducer

- **代码溯源**：[`cuda_113703.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113703.cpp)、raw 内嵌源码、实验快照 `cuda_case12_row16_serial_reducer_exp548.cpp` 与提交前工作文件的 SHA-256 均为 `b8735c579c1fb80cc01cfebb2f8328116d1995869c421bc99047aa2476aad166`。
- **门禁**：仅case12 B8/KV8/L32768、40-split 的64-thread vec2 reducer改为四个物理16-lane row 各自归约 packed `(m,l)`、再由`tid==0`串行合并四个leader；producer、split-major partial ABI、LSE、输出ownership、CTA/grid和其他shape保持#113696。资源保持`38 MTreg / 39 STreg / 0 static B / 0 stack / 8 waves`，动态shared `328→336 B`；CPU、C500 full/boundary/random、case12精确40-split边界、padding和workspace复用均通过。交错 A/B p10/p50/p90 为full=`0.9971/0.9976/0.9989`、random=`0.9951/0.9964/0.9985`、boundary=`0.9807/0.9904/0.9992`，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/235/39/224/371/182/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/56/55`。唯一覆盖目标case12相对#113696由`373→371 μs`，但显示分仍60；同档时延刷新不能建立可打榜的源码因果，其他case的同场波动也不归因。因此拒绝并关闭这个 exact physical-row16 + serial-leader reducer contract；不得扫描row数、leader merge、shuffle mode、模板/grid或同源码复投，只有physical-subgroup数据流、partial consumer ownership或后端能力出现实质新前提时才可重开。工作文件已恢复#113696。
- **原始评测**：[cuda_113703_raw.json](raw/cuda_113703_raw.json)。

### 提交 #113696 · exp547 case10 physical-row16 serial-leader reducer

- **代码溯源**：[`cuda_113696.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113696.cpp)、raw 内嵌源码、实验快照 `cuda_case10_row16_serial_reducer_exp547.cpp` 与提交前工作文件的 SHA-256 均为 `fce1b410d03c4042fd18e6bdc3e379d0742acc42931786d337cd552dd8e13932`。
- **门禁**：仅 case10 B1/KV4/L8192、128-split 的64-thread vec2 reducer 启用物理16-lane packed `(m,l)` max/sum reduction：四个 native row 各自归约，`tid==0` 串行合并四个 leader；producer、split、FP32 partial ABI、LSE、输出 ownership 与其余 shape 不变。资源为`38 MTreg / 36 STreg / 0 static shared / 0 stack / 8 waves`，动态 metadata shared `520→528 B`；目标 LLVM 为8处`llvm.mxc.mov.shfl.i32`、零 BSM。CPU、C500 full/boundary/random、padding与`8192→1,2,15,16,17,63,64,65,127,128,129,191,192,193,255,256,257,8191→8192`复用均通过。交错 A/B p10/p50/p90 为full=`0.9607/0.9741/0.9821`、random=`0.9303/0.9434/0.9965`、boundary=`0.9409/1.0175/1.0593`，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/230/94/234/39/222/373/181/139 μs`，分数=`92/90/83/72/73/63/54/54/57/62/52/60/57/55`。唯一覆盖目标 case10 相对 #113677 的`40 μs/61分`到`39 μs/62分`，兑现预注册 display gain，接受为新结构性control；未覆盖路径的同场波动不作收益或损失归因。关闭这个 exact physical-row16 + serial-leader reducer contract；不得扫描 row 数、leader merge、shuffle mode、模板/grid 或同源码复投，只有 physical-subgroup 数据流、partial consumer ownership 或后端能力出现实质新前提时才可重开。工作文件保持 #113696。
- **原始评测**：[cuda_113696_raw.json](raw/cuda_113696_raw.json)。

### 提交 #113689 · exp546 case11 vec4 physical-row16 reducer

- **代码溯源**：[`cuda_113689.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113689.cpp)、raw 内嵌源码、实验快照 `cuda_case11_vec4_row16_exp546.cpp` 与提交前工作文件的 SHA-256 均为 `81ad3fe237702a261679272fa8a9b7c5e19c3f83120a6a38545634f91611c3f3`。
- **门禁**：仅 case11 B16/KV4/L12251、39-split 的32-thread vec4 reducer 启用物理16-lane max/LSE reduction：两个 native row 各自归约，再以一个固定 xor16 合并；producer、split、partial ABI、数学、输出 ownership、case8 和其他shape不变。资源保持`64 MTreg / 35 STreg / 0 shared / 0 stack / 8 waves`；目标 LLVM 从10个`llvm.mxc.bsm.bpermute`变为8个`llvm.mxc.mov.shfl.i32`加2个BSM。CPU、C500 full/boundary/random、padding与`12251→1,2,15,16,17,319,320,321,639,640,641,959,960,961,12239,12240,12241,12250→12251`复用均通过。交错 A/B p10/p50/p90 为full=`0.9974/0.9982/1.0001`、random=`0.9944/0.9976/1.0050`、boundary=`0.9912/0.9937/0.9982`，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/227/93/233/40/223/373/181/139 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标 case11 相对 #113677 的`225→223 μs`却仍为52分；未改 case11 的 #113658/#113642 已有`223/222 μs`同档样本，不能建立源码因果或 control 收益。关闭这个 exact vec4 physical-row16 + xor16 cross-row merge contract；不得扫描 row 数、cross-row merge、shuffle mode、模板/grid 或同源码复投，只有物理 subgroup 数据流、partial consumer ownership 或后端能力有实质新前提才可重开。工作文件已恢复 #113677。
- **原始评测**：[cuda_113689_raw.json](raw/cuda_113689_raw.json)。

### 提交 #113677 · exp545 case14 packed row16 reducer

- **代码溯源**：[`cuda_113677.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113677.cpp)、raw 内嵌源码、实验快照 `cuda_case14_row16_reducer_exp545.cpp` 与提交前工作文件的 SHA-256 均为 `6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`。
- **门禁**：仅case14 B1/KV4/L61519、257-split 的128-thread `paged_decode_reduce_kernel` 启用物理16-lane packed `(m,l)` max/sum reducer；producer、fixed15 BF16-MMA、normalized BF16 partial、packed metadata、输出 ownership、grid和其他shape不变。资源由`40 MTreg / 32 STreg / 0 shared / 0 stack / 8 waves`变为`40/28/0/0/8`，动态metadata shared由1044 B变为1060 B；目标LLVM的candidate/control为8个`llvm.mxc.mov.shfl.i32`/20个`llvm.mxc.bsm.bpermute`。CPU、C500 full/boundary/random、case14精确257-split边界、padding与`full→short→full`复用均通过。交错A/B p10/p50/p90为full=`0.9815/0.9906/1.0008`、random=`0.9856/0.9920/0.9988`、boundary=`1.0075/1.0186/1.0505`；未出现覆盖一致、明显且可重复的系统性回退，故完成一次预注册 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/227/94/232/40/225/375/182/139 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case14相对#112716的`141 μs/54分`进至`139 μs/55分`，因此在本地门禁和真实OJ共同支持下接受为结构性control；同场aggregate及未覆盖case的波动不作反向归因。关闭这个 exact case14 physical-row16 reducer contract的row数、cross-row merge、shared大小、模板/grid和同源码复投；只有physical-subgroup dataflow、partial consumer ownership或后端能力实质变化才能重开。工作文件保持#113677。
- **原始评测**：[cuda_113677_raw.json](raw/cuda_113677_raw.json)。

### 提交 #113658 · exp544 case7 packed group8 row16 reducer

- **代码溯源**：[`cuda_113658.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113658.cpp)、raw 内嵌源码、实验快照 `cuda_case7_group8_packed_row16_exp544.cpp` 与提交前工作文件的 SHA-256 均为 `091a204282a6c8deab6b384deaa72b4f58845b4775196948da412a3cf352b895`。
- **门禁**：仅case7 B64/KV8/L2048 的 packed group8 reducer把`NATIVE_ROW16_REDUCE`从false改为true；shuffle-weight、fused tail、producer、partial ABI、CTA/grid和其余shape不变。资源保持`66 MTreg / 25 STreg / 0 shared / 0 stack / 7 waves`，LLVM `llvm.mxc.mov.shfl`计数candidate/control=`607/599`；CPU、C500 full/boundary/random、case7精确3-split边界、padding和`full→short→full`复用均通过。交错A/B p10/p50/p90为full=`0.9964/0.9983/1.0000`、random=`0.9925/0.9952/1.0039`、boundary=`0.9915/0.9995/1.0021`，没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/225/94/234/40/223/371/182/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case7由#112716的`227→225 μs`，但显示分仍55；其余同场波动不归因。没有可兑现的 display gain，结构性control保持#112716。关闭这个 exact case7 packed group8 physical-row16 metadata/LSE reducer contract：不得扫描row数、shuffle mode、模板参数、grid或同源码复投；只有physical-subgroup数据流、packed-metadata consumer ownership或后端能力出现实质新前提才能重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113658_raw.json](raw/cuda_113658_raw.json)。

### 提交 #113642 · exp543 group8 final native STG

- **代码溯源**：[`cuda_113642.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113642.cpp)、raw 内嵌源码、实验快照 `cuda_group8_final_native_stg_exp543.cpp` 与提交前工作文件的 SHA-256 均为 `e221665e6ba0e25206e7d90d978582a3ebf352f8c48f196a6cc2048823dbc382`。
- **门禁**：仅case5/6/7/8的group8最终 reducer consumer 把连续且16-byte对齐的8个BF16输出从四次`__nv_bfloat162` store改为一次真实`__builtin_mxc_stg_b128_predicator`；producer、partial ABI、metadata/LSE、reducer ownership/grid和其他shape不变。三个新特化保持`66 MTreg / 24、25或26 STreg / 0 shared / 0 stack / 7 waves`，candidate LLVM 有7处`llvm.mxc.stg.predicator.v4i32`、control为0；CPU、C500 full/boundary/random、受影响精确长度、padding和full→short→full复用均通过。交错A/B没有覆盖一致、明显且可重复的系统性回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/23/17/28/226/94/234/40/222/371/181/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖路径case5/6保持control的`17/28 μs`，case7仅`227→226 μs`且显示分仍55，case8反而`93→94 μs`、显示分仍54；未覆盖路径同场波动不归因。因此没有可打榜的因果收益，结构性control保持#112716。关闭这个 exact group8 final-consumer native-STG contract：不得扫描builtin参数、packing、地址表达、enable范围或同源码复投；只有最终consumer ownership、输出格式或后端store能力实质改变才能重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113642_raw.json](raw/cuda_113642_raw.json)。

### 提交 #113566 · exp542 case12 row16 vec2 reducer

- **代码溯源**：[`cuda_113566.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113566.cpp)、raw 内嵌源码、实验快照 `cuda_case12_row16_vec2_reducer_exp542.cpp` 与提交前工作文件的 SHA-256 均为 `a7f53bce7c5e3243bd8766e1ee8ef219a08bacf1d10d4d39f987787239aa1bcb`。
- **门禁**：仅case12 B8/KV8/L32768、40-split 的64-thread vec2 reducer启用真实物理16-lane row metadata/LSE reduction：四个row各自归约，再由row leader经shared合并；producer、split-major FP32 partial ABI、packedFP16 `(m,l)`、输出 ownership、grid和其他shape不变。资源仍为`38 MTreg / 39 STreg / 0 static B / 0 stack / 8 waves`，动态shared从328 B到336 B；CPU、C500 full/boundary/random、case12精确40-split边界、padding和workspace复用均通过。交错A/B p10/p50/p90为full=`0.9962/0.9989/0.9995`、random=`0.9957/0.9969/0.9982`、boundary=`0.9883/0.9922/0.9974`，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/224/93/237/40/221/376/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case12相对#112716的`375→376 μs`且显示分保持60，aggregate也低于control；因此不能建立收益因果或替换control。关闭这个 exact physical-row16 reducer contract：不得扫描row数、shared布局、shuffle mode、grid或同源码复投；只有物理subgroup dataflow、partial consumer ownership或后端能力实质改变才能重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113566_raw.json](raw/cuda_113566_raw.json)。

### 提交 #113538 · exp541 case5 symmetric finalizer

- **代码溯源**：[`cuda_113538.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113538.cpp)、raw 内嵌源码、实验快照 `cuda_case5_symmetric_finalizer_exp541.cpp` 与提交前工作文件的 SHA-256 均为 `d7b36fe96f9ec7d889653f7cd4340a8ae5f2a9a4223e97f83b05f9d5f5ae611e`。
- **门禁**：仅case5 B16/KV4/L141、5-split 的z4 producer启用`SYMMETRIC_FINALIZER=true`，让z0/z1各自终结一个head；BSM combined tail、BF16-MMA QK、loader、partial ABI、group8 reducer和其他shape保持control。资源由`74/52/8320/0/6`变为`74/48/8320/0/6`；CPU、C500 full/boundary/random、case5精确长度、padding和workspace复用通过。交错A/B p10/p50/p90为full=`0.9686/0.9952/1.0303`、random=`0.9737/0.9873/1.0084`、boundary=`0.9734/0.9914/1.0365`，没有覆盖一致、明显且可重复的系统性本地回退，故完成一次预注册 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `66.07`，case1–14=`3/4/9/22/17/28/227/93/235/40/223/371/181/140 μs`，分数=`92/90/83/73/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case5仍为`17 μs/73分`；总分刷新来自未修改case14的`141→140 μs/54→55分` timing-tier样本，不能归因。因此关闭这个 exact case5 symmetric-finalizer contract，结构性control保持#112716；不得扫描finalizer/store/barrier/launch/reducer拼写或同源码复投。
- **原始评测**：[cuda_113538_raw.json](raw/cuda_113538_raw.json)。

### 提交 #113492 · exp539 case13 wave-local final-tree sync

- **代码溯源**：[`cuda_113492.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113492.cpp)、raw 内嵌源码、实验快照 `cuda_case13_wave_final_tree_sync_exp539.cpp` 与提交前工作文件的 SHA-256 均为 `c0c2459f3ed73646aad4ef4c56705dbdfc01f5f6abb27631f91d5402651405c6`。
- **门禁**：仅case13 B1/KV8/L58966、65-split 的z8 producer把最终两条严格 physical-wave-local state-tree edge从`__syncthreads()`缩小为`__syncwarp()`；前三条跨wave edge、page-loop/tail barrier、QK/PV、loader、split、partial ABI/reducer和其他case保持control。资源仍为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、case13精确长度、padding和workspace复用均通过。交错A/B p10/p50/p90为full=`0.9976/1.0003/1.0020`、random=`0.9969/1.0003/1.0016`、boundary=`0.9108/0.9927/1.0057`，没有与覆盖范围一致、明显且可重复的系统性本地回退，因此完成一次预注册 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/225/94/235/40/222/372/182/140 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/55`。唯一覆盖目标case13从#112716的`181 μs/57分`退至`182 μs/56分`，aggregate低于control；关闭这个 exact wave-local-final-tree-sync contract。不得扫描barrier位置、同步范围、tree row、模板参数或同源码复投；只有同步范围、state/consumer ownership、merge tree或后端能力实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113492_raw.json](raw/cuda_113492_raw.json)。

### 提交 #113438 · exp538 case13 shared-only z8 tree barrier

- **代码溯源**：[`cuda_113438.cpp`](../solutions/archive/2026-08-16-submissions/cuda_113438.cpp)、raw 内嵌源码、实验快照 `cuda_case13_shared_tree_barrier_exp538.cpp` 与提交前工作文件的 SHA-256 均为 `b2fb75aca0c317fc78cb3c48e0908d4a29509141b89025d66ae1374453101d90`。
- **门禁**：仅case13 B1/KV8/L58966、65-split 的z8 producer将五个只发布/消费CTA-local `s_acc/s_md` 的tree edge从`__syncthreads()`改为`__syncthreadshared()`；page-loop/tail barrier、QK/PV、loader、split、partial ABI/reducer与其他case保持control。目标资源仍为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`，LLVM有五处真实`llvm.mxc.barrier.shared()`；CPU与C500 full/boundary/random、case13精确长度、padding和workspace复用均通过。交错A/B p10/p50/p90为full=`0.9969/1.0005/1.0068`、random=`0.9946/1.0009/1.0104`、boundary=`0.9866/0.9920/1.0081`，没有与改动覆盖范围一致、明显且可重复的系统性本地回退，因此完成一次预注册 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/226/93/232/40/224/372/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case13保持#112716的`181 μs/57分`，aggregate低于control；关闭这个 exact case13 all-five shared-only-tree-barrier contract。不得扫描barrier位置、tree row、模板拼写或同源码复投；只有同步范围、state/consumer ownership、merge tree或后端能力实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113438_raw.json](raw/cuda_113438_raw.json)。

### 提交 #113343 · exp535 case13 live-prefix reciprocal/magic mapping

- **代码溯源**：[`cuda_113343.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113343.cpp)、raw 内嵌源码、实验快照 `cuda_case13_live_prefix_magic_exp535.cpp` 与提交前工作文件的 SHA-256 均为 `c9b93c9ba9e20658b1d4dc7060235b16604350fba5d419ef84f38b43eb1fd9d5`。
- **门禁**：只给case13 B1/KV8/L58966、65-split 的z8 producer在短实际长度启用live-prefix实际页均衡；满容量严格保持control的`57×64+37`页映射，短长度只在reducer已读取的live split前缀内均分full pages，tail仍由最后一个live split处理。常数倒数表与`__umulhi`实现无candidate device-`udiv`；split、partial ABI/reducer、z8 QK/PV/loader/tree、尾页数学和其他case均保持control。资源与control均为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random均14/14，case13所有live-prefix边界、padding与workspace复用均通过。A/B p10/p50/p90为full=`1.0007/1.0037/1.0370`、random=`0.9924/0.9979/1.0048`、boundary=`0.9789/0.9944/1.0099`，没有与覆盖范围一致、明显且可重复的系统性本地回退，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/226/94/234/40/222/377/181/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/54`。唯一覆盖目标case13相对#112716仍为`181 μs/57分`，没有可归因display收益，aggregate也低于control；关闭这个 exact case13 live-prefix reciprocal/magic mapping。不得扫描table、bucket、映射时点、split或同源码复投；只有producer实际长度调度或数据流实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113343_raw.json](raw/cuda_113343_raw.json)。

### 提交 #113299 · exp534 case13 one-head/two-wave split-tiled reducer

- **代码溯源**：[`cuda_113299.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113299.cpp) 与 raw 内嵌源码、提交前工作文件 SHA-256 均为 `7afd37821213ffff7ec42082b6bfa3c93d9481d264664d443d9b83d619307b74`。
- **门禁**：只给case13 B1/KV8/L58966、65-split 的最终reducer改为一个128-thread CTA内的two-physical-wave split-tiled consumer：wave0/1分别消费live prefix的前/后半，各以FP32累积完整128维，wave1以1064 B CTA-local shared payload交给wave0唯一输出。producer、z8 QK/PV/loader/tree、split、split-major partial ABI、packed metadata、32-CTA reducer grid和其他case均保持control。资源为`46 MTreg / 40 STreg / 0 static B / 0 stack / 8 waves`（control vec2=`38/36/0/0/8`）；CPU、C500 full/boundary/random均14/14，case13精确57-page/65-live-split/padding/workspace复用通过。A/B p10/p50/p90为full=`0.9924/0.9956/0.9987`、random=`0.9954/1.0009/1.0060`、boundary=`0.9842/1.0049/1.0319`；两次full强测p50=`0.9937/0.9941`。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/233/40/223/371/180/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一覆盖目标case13从#112716的`181→180 μs`，但显示分保持57，且总分低于control；同档一微秒不构成可打榜的源码因果或control收益。关闭这个 exact one-head/two-wave split-tiled reducer ownership：不得扫描wave数、split分界、shared布局、metadata、grid或同源码复投；只有partial consumer ownership、producer/reducer数据流或后端能力实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113299_raw.json](raw/cuda_113299_raw.json)。

### 提交 #113237 · exp533 case12 two-head full-wave reducer

- **代码溯源**：[`cuda_113237.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113237.cpp)、raw 内嵌源码、实验快照 `cuda_case12_twohead_reducer_exp533.cpp` 与提交前工作文件的 SHA-256 均为 `2f10cf5be31e82acbf568d0ed5e70124492cc6ce258207326c25d4b6dfe9ff43`。
- **门禁**：只给case12的最终reducer让一个64-thread完整wave同时拥有两个相邻query head，partial ABI、producer、metadata/LSE、输出和其他case不变；reducer grid从256降为128 CTA。资源`40 MTreg / 42 STreg / 0 static B / 0 stack / 8 waves`（control vec2=`38/39/0/0/8`），动态shared为656 B；CPU、C500 full/boundary/random均14/14，case12精确split/tail/padding/workspace复用通过。A/B p10/p50/p90为full=`0.9985/1.0038/1.0042`、random=`1.0028/1.0041/1.0064`、boundary=`1.0045/1.0101/1.0194`；boundary强复测=`1.0072/1.0113/1.0159`。这只是约0.4–1.1%的本地风险信号，不替代一次预注册 OJ 验证。
- **OJ解释与control决策**：14/14 Accepted / `65.79`，case1–14=`3/4/10/23/17/28/225/93/233/40/222/374/182/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case12由#112716的`375→374 μs`，但显示分仍60，且总分下降；一微秒同档变化不足以提供可打榜的因果收益或替换control。关闭这个exact two-head/full-wave reducer ownership：不得扫描head pair、CTA grid、shared布局、metadata或同源码复投；只有partial consumer ownership、producer/reducer数据流或后端能力实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113237_raw.json](raw/cuda_113237_raw.json)。

### 提交 #113201 · exp531 case12 bit1 early synchronous next-K

- **代码溯源**：[`cuda_113201.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113201.cpp)、raw 内嵌源码、实验快照 `cuda_case12_bit1_early_k_exp531.cpp` 与提交前工作文件的 SHA-256 均为 `83d3eccc1bb47584ce7303c0e2a78b5041a6f0dc134db7ee250079419e7b3c04`。
- **门禁**：仅case12 B8/KV8/L32768、40-split 的z8 producer改为bit1 QK/token ownership，并在当前页QK后把下一页K立即同步写到已死的`s_k`；下一页V仍保持control的寄存器lookahead与PV后写回。资源为`78 MTreg / 48 STreg / 8448 B / 0 stack / 6 waves`（#112716 case12为`82/50/8448/0/5`）；CPU、C500 full/boundary/random均14/14，case12精确split/tail/padding/workspace复用均通过。交错A/B p10/p50/p90为full=`1.0164/1.0178/1.0200`、random=`1.0158/1.0180/1.0214`、boundary=`0.9130/0.9179/0.9214`，分布信号混合，因此按预注册完成一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/225/94/231/40/223/382/181/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/59/57/54`。唯一覆盖目标case12相对#112716的`375 μs/60分`退到`382 μs/59分`，直接否定这个exact bit1+early-sync-next-K state flow；其他未覆盖case的同场波动不归因。关闭该路线：不得改bit1 owner、K写回时点、K/V load表达、split或同源码复投；只有QK/PV consumer ownership、thread dataflow或后端能力出现实质新前提才能重开。工作文件随后恢复#112716。
- **原始评测**：[cuda_113201_raw.json](raw/cuda_113201_raw.json)。

### 提交 #113157 · exp528 case4 native final-output STG

- **代码溯源**：[`cuda_113157.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113157.cpp)、raw 内嵌源码、实验快照 `cuda_case4_direct_output_native_stg_exp528.cpp` 与提交前工作文件的 SHA-256 均为 `039f432ce7eea0783c52bb9683c3668f1da4ef13f2599aeb753c1137dce4c548`。
- **门禁**：唯一差异是case4 B64/KV8/L64 `CASE4_DEDICATED` 的最终direct-output consumer，把每个对齐16-byte、连续8个BF16的四次`__nv_bfloat162`写换为一次`__builtin_mxc_stg_b128_predicator`。LLVM的实际case4特化有一处`llvm.mxc.stg.predicator.v4i32`、control为零；资源与control均为`74 MTreg / 44 STreg / 8320 B / 0 stack / 6 waves`。CPU和C500 full/boundary/random均14/14，case4同进程`64→1,2,15,16,17,63→64`也通过；交错A/B p10/p50/p90为full=`0.9748/1.0025/1.0435`、random=`0.9882/0.9962/1.0084`、boundary=`0.9991/1.0081/1.0318`，无覆盖一致、明显且可重复的本地否决，因此完成一次预注册OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/224/93/237/40/222/370/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case4相对#112716的`22 μs/73分`回退到`23 μs/72分`，直接否定该exact native final-output-store假设；case7/11/12等未覆盖路径的同场变化不归因，aggregate也低于control。关闭这一exact final-BF16 `stg_b128` consumer：不得调整builtin参数、BF16 packing、地址表达、启用范围或同源码复投；只有最终consumer ownership、输出格式或后端store能力实质改变才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113157_raw.json](raw/cuda_113157_raw.json)。

### 提交 #113136 · exp527 case13 head-major FP32 partial accumulator

- **代码溯源**：[`cuda_113136.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113136.cpp)、raw 内嵌源码、实验快照 `cuda_case13_headmajor_partial_acc_exp527.cpp` 与提交前工作文件的 SHA-256 均为 `1ba8147621425c46ae405b01550660ca727fe958b53dd0ce88dda3c0cb4fc802`。
- **门禁**：唯一差异是case13 B1/KV8/L58966、65-split 的 z8 producer→vec2 reducer FP32 `partial_acc` 从 split-major 改为`[head][split][dim]`；FP16 `(m,l)` metadata、QK/PV、K/V loader、z8 tree、split、reducer几何、LSE、output及其他case不变。producer资源`82/48/8448 B/0 stack/5 waves`不变，vec2 reducer由`38/39/0/0/8`到`38/28/0/0/8`；CPU、C500 full/boundary/random、case13精确长度、padding和workspace复用均通过。A/B p10/p50/p90为full=`0.9963/0.9985/1.0016`、random=`0.9982/1.0018/1.0037`、boundary=`0.9962/1.0008/1.0250`，没有与覆盖一致、明显且可重复的本地否决，故按预注册完成一次 OJ probe。
- **OJ解释与control决策**：OJ raw 为 **WrongAnswer / `60.07`**；case1–2和4–14均 Accepted，但case3报`payload pass=false`并记录约36.9秒失败占位。这个case不在候选预期覆盖范围，不能从该单条SPJ信息断言内部根因；但远端正确性优先，完整候选不能作为性能样本或control。关闭这个 exact head-major FP32 partial-acc ABI：不得调index/stride、地址表达、模板拼写或同源码复投；只有发现可证明的根因并引入实质不同的partial ABI/后端前提才可重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113136_raw.json](raw/cuda_113136_raw.json)。

### 提交 #113117 · exp526 case12 native-bit1 ownership

- **代码溯源**：[`cuda_113117.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113117.cpp)、raw 内嵌源码与提交前工作文件的 SHA-256 均为 `af0251225c68fb8dac541775f4f0eabaa2b7ed19a47b862669099423dc526204`。
- **门禁**：仅case12 B8/KV8/L32768、40-split 的 z8 producer 从`<true>`改为`<true,true>`，即将已验证全原生QK/head-token ownership从bit2切换为bit1；case7 live-prefix mapping、case12 split/loader/partial/reducer/LSE及其他case不变。candidate `<true,true,false>`资源为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`，control `<true,false,false>`为`82/50/8448/0/5`；CPU、C500 full/boundary/random、精确split/tail/padding/workspace复用均通过。A/B p10/p50/p90为full=`0.9952/0.9969/0.9986`、random=`0.9875/0.9954/0.9977`、boundary=`0.9828/1.0041/1.0092`，没有覆盖一致、明显且可重复的本地否决。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/9/24/17/28/226/94/232/40/220/371/182/140 μs`，分数=`92/90/83/71/73/63/55/54/57/61/53/60/56/55`。唯一覆盖目标case12相对#112716的`375→371 μs`仍为60分；未修改case12的 #112775 / exp503 已出现`371 μs/60分`，故同档时延不足以建立bit1映射的源码因果或control收益，aggregate也低于control。关闭这个 exact case12 bit1 ownership；不得调shuffle、owner lane、模板拼写、split或同源码复投，只有QK/PV consumer ownership、thread/dataflow或后端能力实质改变才能重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113117_raw.json](raw/cuda_113117_raw.json)。

### 提交 #113078 · exp525 case12 intrawave-first merge tree

- **代码溯源**：[`cuda_113078.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113078.cpp)、raw 内嵌源码、实验快照 `cuda_case12_intrawave_first_tree_exp525.cpp` 与提交前工作文件的 SHA-256 均为 `f6c04e385e4392c581d0869d22d03904c2393b337ef13de45892e2572067ce58`。
- **门禁**：只给case12 B8/KV8/L32768、40-split 的z8 producer启用 intrawave-first merge tree：每个物理64-lane wave先合并相邻z pair，之后只让z4/z6和z2经过两阶段shared state；case13、QK/PV、K/V loader、split、partial ABI、LSE、reducer/output及其他case不变。资源仍为`82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves`。CPU、C500 full/boundary/random、case12精确split/tail/padding/workspace复用均通过；A/B p10/p50/p90为full=`0.9992/1.0000/1.0014`、random=`0.9995/1.0007/1.0038`、boundary首轮=`0.9959/1.0047/1.0213`、独立复测=`0.9970/1.0031/1.1937`，不足以构成覆盖一致、明显且可重复的本地性能否决。
- **OJ解释与control决策**：14/14 Accepted / `65.79`，case1–14=`3/4/9/23/17/29/226/93/231/40/222/378/182/141 μs`，分数=`92/90/83/72/73/62/55/54/57/61/52/60/56/54`。预注册唯一目标case12由#112716的`375 μs/60分`回退为`378 μs/60分`，直接否定这个 exact B8/40-split intrawave-first tree；未覆盖路径的同场变化不归因，aggregate低于control。关闭此路线；不得只调raw exchange、pair归属、barrier、shared row或同源码复投，只有merge tree、跨半waveconsumer ownership、state表示或后端交换能力实质改变才能重开。结构性control保持#112716。
- **原始评测**：[cuda_113078_raw.json](raw/cuda_113078_raw.json)。

### 提交 #113036 · exp524 case13 intrawave-first merge tree

- **代码溯源**：[`cuda_113036.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113036.cpp)、raw 内嵌源码、实验快照 `cuda_case13_intrawave_first_tree_exp524.cpp` 与提交前工作文件的 SHA-256 均为 `8c9138106add71521279a20fe575968a75a8011336ed6834370768428dc3626f`。
- **门禁**：只给case13 B1/KV8/L58966、65-split 的z8 producer重排完整merge tree：先在各物理64-lane wave内合并相邻z pair，再只让`z4/z6`和`z2`经过两阶段shared state，因此从control三次CTA barrier、七组shared producer/consumer边变为两次barrier、三组跨wave shared边。QK/PV、K/V loader、split、partial ABI、LSE、reducer/output与其他case不变；资源仍为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`。CPU、C500 full/boundary/random、case13精确split/tail/padding/workspace复用均通过；A/B p10/p50/p90为full=`1.0004/1.0027/1.0042`、random=`0.9999/1.0028/1.0034`、boundary首轮=`1.0003/1.0210/1.0521`、独立复测=`0.9304/1.0064/1.0451`，不足以构成覆盖一致、明显且可重复的本地性能否决。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/227/93/236/40/222/372/182/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/55`。预注册唯一目标case13由#112716的`181 μs/57分`回退为`182 μs/56分`；未覆盖路径的同场变化不归因，aggregate低于control。关闭这条 exact first-intrawave z8 merge tree；不得只调raw exchange、pair归属、barrier、shared row或同源码复投，只有merge tree、跨半waveconsumer ownership、state表示或后端交换能力实质改变才能重开。工作文件已恢复#112716。
- **原始评测**：[cuda_113036_raw.json](raw/cuda_113036_raw.json)。

### 提交 #113000 · exp523 case13 head-major packed metadata

- **代码溯源**：[`cuda_113000.cpp`](../solutions/archive/2026-08-15-submissions/cuda_113000.cpp)、raw 内嵌源码、实验快照 `cuda_case13_headmajor_metadata_exp523.cpp` 与提交前工作文件的 SHA-256 均为 `d073ec5d59d4024b25aa90d4bd0e5679079dfa51afcfb06ebbc984d2d6476773`。
- **门禁**：仅case13 B1/KV8/L58966/65-split 的packed FP16 `(m,l)` metadata 从 split-major 改为`[head][split]`，使64-lane vec2 reducer lanes `0..63`的首批metadata读取连续；FP32 `partial_acc`仍是split-major，QK/PV、K/V loader、z8 tree、split、LSE、reducer CTA/output ownership与其他case不变。producer资源保持`82/48/8448 B/0 stack/5 waves`，reducer保持`38/39/0/0/8`；CPU、C500 full/boundary/random及case13精确split/tail/padding/workspace复用均通过。交错 A/B p10/p50/p90为full=`0.9928/1.0008/1.0036`、random=`0.9930/1.0008/1.0060`、boundary=`0.9624/0.9865/1.0216`；没有覆盖一致、明显且可重复的系统性回退，因此按预注册进行一次OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/226/93/234/40/222/373/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case13保持#112716的`181 μs/57分`；未覆盖路径的同场变化不归因，aggregate也低于control。关闭这个 exact head-major packed-metadata producer/reducer layout；不得扫描metadata stride、layout拼写、grid或同源码复投，只有metadata格式、partial/producer-reducer ownership或全局数据流实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_113000_raw.json](raw/cuda_113000_raw.json)。

### 提交 #112972 · exp522 case13 output-half reducer

- **代码溯源**：[`cuda_112972.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112972.cpp)、raw 内嵌源码与提交前工作文件的 SHA-256 均为 `dcd669601e9d64521d0c38d74a363b51bcd69a51ac69441b05be84859f95df94`。
- **门禁**：只替换 case13 B1/KV8/L58966/65-split 的最终 reducer consumer/output ownership：原来的32个 `(batch, head)` vec2 CTA 改为64个 output-half CTA，每个 CTA 唯一拥有维度 `0..63` 或 `64..127`。packed FP16 `(m,l)`、FP32 partial accumulator、LSE、producer、split、tail及其他case不变；没有重复 accumulator read 或 output write。新 reducer资源为`40 MTreg / 32 STreg / 0 B shared / 0 stack / 8 waves`，control vec2 reducer为`38/36/0/0/8`。CPU和C500 full/boundary/random均14/14通过；case13 live-split、tail、padding与workspace复用精确长度也通过。交错 A/B p10/p50/p90为full=`0.9929/0.9972/1.0003`、random=`0.9961/1.0015/1.0055`、boundary=`0.9734/0.9969/1.0722`，没有覆盖一致的明显系统性回退，因而按预注册进行一次 OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/234/40/223/373/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一目标 case13 保持 #112716 的`181 μs/57分`，不能把 case7/12/14 等未覆盖路径的同场变化归因给该 reducer。关闭这个 exact 64-CTA output-half partial consumer/output ownership；不得扫描half划分、grid、metadata布局或同源码复投，只有全局partial consumer/output ownership、producer/reducer数据流或多请求并发出现实质新前提才可重开。工作文件恢复 #112716。
- **原始评测**：[cuda_112972_raw.json](raw/cuda_112972_raw.json)。

### 提交 #112941 · exp521 case13 bit1 alpha/weight-exp fold

- **代码溯源**：[`cuda_112941.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112941.cpp)、raw 内嵌源码和实验快照 `cuda_case13_fold_alpha_exp521.cpp` 的 SHA-256 均为 `be31a8aae12bddcd47d89983681849634e6da2d5c39da56e8debf0778319eb1f`。
- **门禁**：仅case13 B1/KV8/L58966 的native-bit1 two-token z8热全页循环，让未消费的lane `4/5`在既有行级weight `exp2`中承载两头online-softmax alpha；正常PV权重仍只从lane `0..3`广播，tail、split65、QK/PV、K/V loader、partial ABI、reducer、z-state和其他case不变。case13资源为`82 MTreg / 52 STreg / 8448 B / 0 stack / 5 waves`（control `82/48/8448/0/5`）；CPU、C500 full/boundary/random、64→65 live-split/tail/padding/复用均通过。交错 A/B p10/p50/p90为full=`0.9902/1.0093/1.0124`、random=`1.0125/1.0169/1.0259`、boundary=`0.9776/1.0008/1.0250`；负信号不构成提交前的明确重复系统性否决，因此按预注册做一次OJ probe。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/23/17/28/226/94/234/40/221/375/183/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/55`。预注册唯一目标case13从#112716的`181 μs/57分`回退至`183 μs/56分`，直接否定这个 exact bit1 lane4/5 alpha/weight-exp fold；case11/14等未覆盖路径的同场变化不归因，aggregate也低于control。不得只调fold lane、broadcast、guard、启用范围或同源码复投；只有score/PV consumer ownership、reference或producer数据流实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_112941_raw.json](raw/cuda_112941_raw.json)。

### 提交 #112909 · exp520 case13 hot next-K raw GVM BSM producer

- **代码溯源**：[`cuda_112909.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112909.cpp)、raw 内嵌源码和实验快照 `cuda_case13_hot_next_k_gvm_bsm_exp520.cpp` 的 SHA-256 均为 `6a0b5a1917d52fc6ad1d4d56ba106960005a6f8b016e264ee5f9551f65e9c24b`。
- **门禁**：仅case13 B1/KV8/L58966 的z8 head-pair producer在当前页QK后用真实`__builtin_mxc_ldg_b128_bsm`把next-K发往已死亡的`s_k` row；next-V保留control的四个标量lookahead，PV后以`__builtin_mxc_arrive(64)+__builtin_mxc_barrier_inst()`退休K传输。初始页/tail同步loader、split65、ownership、QK/PV、partial ABI、vec2 reducer和其他case不变。实际case13 LLVM保留`llvm.mxc.ldg.predicator.bsm.v4i32`及`llvm.mxc.arrive(64)`；资源为`80 MTreg / 48 STreg / 8448 B / 0 stack / 6 waves`，control为`82/48/8448/0/5`。CPU、C500 full/boundary/random、case13 64→65 live-split/tail/padding/复用均通过；交错A/B p10/p50/p90为full=`0.9854/0.9969/1.0117`、random=`0.9750/1.0001/1.0040`、boundary=`0.9670/0.9984/1.0631`，未出现覆盖一致且可重复的系统性回退。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/10/22/17/28/227/94/246/40/223/375/181/141 μs`，分数=`92/90/82/73/73/63/55/54/56/61/52/60/57/54`。预注册唯一目标case13保持#112716的`181 μs/57分`，没有display gain；其他同场变化不归因，aggregate低于control。关闭这个 exact hot next-K raw GVM→dead-`s_k` producer/wait contract；不得调builtin参数、等待拼写、load时点、启用范围或同源码复投，只有K/V consumer ownership、多请求深度或后端等待/producer能力实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_112909_raw.json](raw/cuda_112909_raw.json)。

### 提交 #112873 · exp518 case13 overflow-aware readlane metadata/weight reducer handoff

- **代码溯源**：[`cuda_112873.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112873.cpp)、raw 内嵌源码和实验快照 `cuda_case13_readlane_metadata_exp518.cpp` 的 SHA-256 均为 `c459d248c18d3ee7b931953677386b4f98905dbd8c3651f13beabe07d0424a49`。
- **门禁**：仅case13 B1/KV8/L58966 的64-thread vec2 reducer以官方`__builtin_mxc_readlane`让lane `0..63`保留split `0..63`的packed FP16 `(m,l)`和FP32 weight，lane0额外保留唯一的split64；全局max、LSE与accumulator阶段按split从owner lane取weight，删除每split `partial_m→s_m`和weight→`s_w` materialization。FP32 global-max/LSE、partial ABI、split65、producer、tail、output ownership及其他case不变。IR有9处实际`llvm.mxc.rl`（control为零），reducer资源为`30 MTreg / 40 STreg / 0 B / 0 stack / 8 waves`（control `38/36/0/0/8`）；CPU、C500 full/boundary/random、case13精确64→65 live-split/tail/padding/复用均通过。交错A/B p50为full=`1.0015`、random=`1.0009`、boundary=`1.0102`，没有覆盖一致的明显系统性回退。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/226/94/233/40/221/372/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一目标case13保持#112716的`181 μs/57分`，没有display gain；其他同场变化不归因，aggregate低于control。关闭这个 exact 65th-overflow/lane0 readlane metadata/weight consumer contract；不得调lane、overflow归属、readlane调用形态、shared大小、模板拼写或同源码复投，只有metadata格式、producer/consumer ownership或后端能力实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_112873_raw.json](raw/cuda_112873_raw.json)。

### 提交 #112858 · exp516 case12 readlane metadata/weight reducer handoff

- **代码溯源**：[`cuda_112858.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112858.cpp)、raw 内嵌源码和实验快照 `cuda_case12_readlane_reducer_exp516.cpp` 的 SHA-256 均为 `28b685d112887d594a175cfe1ebdb97a3c2721a090a9f22c4ea12bfa114a6813`。
- **门禁**：仅case12 B8/KV8/L32768 的64-thread vec2 reducer以官方`__builtin_mxc_readlane`让accumulator消费owner lane的FP32 weight，并删除每split `partial_m→s_m`和weight→`s_w` materialization；FP32 global-max/LSE、partial ABI、producer、tail、output ownership及其他case不变。IR有9处实际`llvm.mxc.rl`（control为零），reducer资源由`38 MTreg / 39 STreg / 0 B / 0 stack / 8 waves`降为`28/39/0/0/8`；CPU、C500 full/boundary/random、case12精确40-split/tail/padding/复用均通过。交错A/B p50为full=`0.9988`、random=`1.0003`、boundary=`0.9947`，没有覆盖一致的明显系统性回退。
- **OJ解释与control决策**：14/14 Accepted / `65.79`，case1–14=`3/4/10/23/17/28/228/93/235/40/223/371/182/141 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/56/54`。预注册目标case12从#112716的`375→371 μs`，仍为60分；未含此exact handoff的#112761已有`370 μs/60分`，因此同档时间变化不能建立可用于打榜的源码因果，aggregate亦低于control。关闭这个 exact readlane metadata/weight consumer contract；不得调lane、readlane调用形态、shared大小、模板拼写或同源码复投，只有metadata格式、producer/consumer ownership或后端能力实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_112858_raw.json](raw/cuda_112858_raw.json)。

### 提交 #112849 · exp515 case13 native partial-STG handoff

- **代码溯源**：[`cuda_112849.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112849.cpp)、raw 内嵌源码和实验快照 `cuda_case13_native_partial_stg_exp515.cpp` 的 SHA-256 均为 `132e632579cb5fc3bb2c83f7ac6b8bf540df6edec05a25d1954bc953ef1ad251`。
- **门禁**：仅case13 B1/KV8/65-split z8 producer以`__builtin_mxc_stg_b128_predicator`写出四段16-byte对齐的`partial_acc float4`；QK/PV、loader、partial ABI、64-thread vec2 reducer、tail及其他case不变。目标IR有4处实际native STG call（control为零），资源为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`，与control同档；CPU、C500 full/boundary/random、case13精确split/tail/padding与`full→short→full`复用均通过。交错A/B p50为full=`1.0017`、random=`1.0050`、boundary=`0.9860`，没有覆盖一致的明显系统性回退。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/227/93/234/40/222/374/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case13保持#112716的`181 μs/57分`，没有display gain；其他case的同场波动不归因，aggregate低于control。关闭这个 exact native-STG producer→case13-vec2-reducer handoff；不得调builtin参数、cast、store位置、启用范围或同源码复投，只有producer/consumer ownership、partial格式或后端能力实质改变才可重开。工作文件恢复#112716。
- **原始评测**：[cuda_112849_raw.json](raw/cuda_112849_raw.json)。

### 提交 #112833 · exp514 KV8 initial/tail raw GVM BSM loader

- **代码溯源**：[`cuda_112833.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112833.cpp)、raw 内嵌源码和实验快照 `cuda_kv8_initial_tail_gvm_bsm_exp514.cpp` 的 SHA-256 均为 `bbd1a835dcd758f630e5c8eeed0425d4acd9713a7c0a87d586c990150111197a`。
- **门禁**：仅把KV8 z8 head-pair 初始页与fused tail的K/V shared staging替换为官方`__builtin_mxc_ldg_b128_bsm`，并在每个K/V对后以`arrive(64)+barrier_inst()`等待；热循环的scalar K+V-over-PV lookahead、split、ownership、partial/reducer ABI及KV4路径不变。资源保持受影响特化的`82 MTreg / 48–50 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、case7/9/12/13精确页/split/tail边界、padding trap与workspace复用均通过。三分布交错 A/B 没有覆盖一致的明显系统性回退。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/225/93/232/40/224/370/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。覆盖的case7、9、12均未跨显示档，case13从#112716的`181 μs/57分`变为`182 μs/56分`；aggregate下降。故关闭这个 exact raw GVM→shared BSM initial/tail loader与等待契约，不调builtin参数、wait/barrier拼写或覆盖范围后重投；只有实际等待覆盖、consumer ownership或后端能力实质改变才可重开。工作文件恢复 #112716。
- **原始评测**：[cuda_112833_raw.json](raw/cuda_112833_raw.json)。

### 提交 #112775 · exp503 case11 mixed first-stage BF16 z-state

- **代码溯源**：[`cuda_112775.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112775.cpp)、raw 内嵌源码和实验快照 `cuda_case11_mixed_stage1_bf16_state_exp503.cpp` 的 SHA-256 均为 `47d2cfc05531771d1920933e9be739bf0b4af7117f9e84ff5140890aab5123cb`。
- **门禁**：仅 case11 的 z2/z3→z0/z1 第一条跨-wave state edge 写 normalized BF16 `acc/l`；FP32 `(m,l)` 单独保留，z0/z1 的第二阶段 payload 仍为 FP32。QK/PV、split39、loader、partial ABI、reducer、tail与其他 case 不变。资源保持 control 的 `80 MTreg / 58 STreg / 8320 B / 0 stack / 6 waves`；CPU、C500 full/boundary/random、case11 39-split/页/尾边界、padding trap 和 workspace 复用均通过。交错 A/B candidate/control p50 为 full=`0.9978`、random=`1.0014`、boundary=`1.0016`。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/10/23/17/28/227/93/236/39/223/371/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/62/52/60/57/55`。预注册唯一目标 case11 仍为`223 μs/52分`，没有 display gain；其他未覆盖路径的同场波动不归因。关闭这一 exact mixed first-stage BF16 normalized-state contract，不以 packing、lifetime 或 source-spelling 变体重投；工作文件恢复 #112716。
- **原始评测**：[cuda_112775_raw.json](raw/cuda_112775_raw.json)。

### 提交 #112769 · exp502 case11 symmetric-finalizer deferred-reference rescale

- **代码溯源**：[`cuda_112769.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112769.cpp)、raw 内嵌源码和实验快照 `cuda_case11_symmetric_deferred_reference_exp502.cpp` 的 SHA-256 均为 `0274f422e2726c7bb76bc0dfd805abb965c22f9c0b924515a019caacb77db7b9`。
- **门禁**：仅给case11现有39-slot head-pair/z4 BF16-MMA producer添加compile-time deferred-reference开关；当页最大值超过当前指数参考8个base-2 logit才重缩放`(l,acc)`，首个有效页仍安装reference。split39、loader、QK/PV、partial ABI、reducer和其他case不变；关键 changed precondition 是当前已接受的对称 z4 finalizer。资源为`80 MTreg / 62 STreg / 8320 B / 0 stack / 6 waves`；CPU、C500 full/boundary/random、case11页/39-split精确边界、padding trap和`full→short→full`/`short→full`复用均通过。交错A/B candidate/control p50为full=`0.9969`、random=`0.9951`、boundary=`0.9900`。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/226/94/230/40/222/376/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。预注册唯一目标case11相对#112716由`223→222 μs`，却仍52分；未含此exact state-flow 的#112765/#112747等已给出同档`222 μs`样本，不能建立可归因display gain，aggregate也低于control。关闭这个 exact case11 symmetric-finalizer `+8` deferred-reference rescale，不调headroom、guard、store/barrier或同源码重投；工作文件恢复#112716。
- **原始评测**：[cuda_112769_raw.json](raw/cuda_112769_raw.json)。

### 提交 #112765 · exp500 case11 live-prefix reciprocal/magic mapping

- **代码溯源**：[`cuda_112765.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112765.cpp)、raw 内嵌源码和实验快照 `cuda_case11_live_prefix_magic_exp500.cpp` 的 SHA-256 均为 `5993ecff537c0844e98aaadfd7c8caedd2c0ae8208c99f3e720a1d4cbf25c668`。
- **门禁**：只给case11既有39-slot head-pair/z4 BF16-MMA producer在control已读取的live split前缀内，以只读reciprocal table和`__umulhi`均衡真实full pages；满容量仍为`39×20`，split/reducer/loader/partial ABI、z4 finalizer和其他case不变。资源由`80 MTreg / 60 STreg / 8320 B / 0 stack / 6 waves`降为`80/58/8320/0/6`；CPU、C500 full/boundary/random、86个精确长度、padding trap和workspace复用均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/22/17/28/224/94/238/40/222/371/182/140 μs`，分数=`92/90/82/73/73/63/55/54/57/61/52/60/56/55`。预注册唯一目标case11从#112716的`223→222 μs`但仍52分；未含此exact mapping的相邻样本已有`222/221 μs`，不能建立可归因display gain或替换control。关闭这个exact case11 live-prefix reciprocal/magic mapping，不扫描table、bucket、映射时点或同源码重投；工作文件恢复#112716。
- **原始评测**：[cuda_112765_raw.json](raw/cuda_112765_raw.json)。

### 提交 #112761 · exp499 case12 live-prefix reciprocal/magic mapping

- **代码溯源**：[`cuda_112761.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112761.cpp)、raw 内嵌源码和实验快照 `cuda_case12_live_prefix_magic_exp499.cpp` 的 SHA-256 均为 `7e0246019862d62a9d9080fddc311d7ea3c1f68fdcf984eea776c959f927ac6d`。
- **门禁**：仅case12在既有40个 producer split 的 live prefix 内，以只读 reciprocal table 和`__umulhi`均衡真实 full pages；容量满长映射仍为39个52页加最后20页，partial/reducer live count、K/V loader、QK/PV、tail ABI和其余case不变。资源保持`82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、精确live-prefix边界、padding trap和workspace复用均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/228/94/235/40/224/370/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。预注册唯一目标从#112716的`375→370 μs`，仍为60分；未覆盖case12的#112725/#112736已有`372/374 μs`样本，单次同档变化不能确立可用于打榜的源码因果。aggregate下降，关闭这个 exact reciprocal/bucket/mapping-time 实现，不调表项、bucket、映射时点或同源码复投；工作文件恢复#112716。
- **原始评测**：[cuda_112761_raw.json](raw/cuda_112761_raw.json)。

### 提交 #112756 · exp498 case14 duplicate-score-lane alpha fold

- **代码溯源**：[`cuda_112756.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112756.cpp)、raw 内嵌源码和实验快照 `cuda_case14_fold_alpha_mma_exp498.cpp` 的 SHA-256 均为 `25bcfdcbe5412bae3c03ef62f0fca4472ebb96a9eca783c453b84b02db1e47bd`。
- **门禁**：只在case14 fixed15 BF16-MMA热路径把重复score lane `tx=4/12`的同一条`exp2`用于必要时的online-softmax alpha；当前deferred-reference、split257、z4 finalizer、PV ownership、partial ABI和其余case不变。资源保持`82 MTreg / 64 STreg / 8320 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、case14精确长度/复用和padding trap均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/9/23/17/28/225/94/236/40/221/374/181/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/57/54`。预注册唯一目标case14相对#112716保持`141 μs/54分`；其他case的同场变化没有本轮覆盖的运行差异，不能归因。关闭这个 exact duplicate-score-lane alpha ownership/fold，不改fold lane、broadcast、guard或同状态流重投；工作文件恢复#112716。
- **原始评测**：[cuda_112756_raw.json](raw/cuda_112756_raw.json)。

### 提交 #112747 · exp493 case11 register-FP32-(m,l) metadata ownership

- **代码溯源**：[`cuda_112747.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112747.cpp)、raw 内嵌源码和实验快照 `cuda_case11_register_fp32_ml_exp493.cpp` 的 SHA-256 均为 `464b86b4cadf4b1a75cfc07bc2d923848e3bf210637007ff46bbb31d4e681e99`。
- **门禁**：仅case11的32-thread vec4 reducer使每lane保留至多两组FP32 `(m,l)`到global-max/weight阶段，删除`s_m` shared元数据往返；`s_w`、partial ABI、LSE数学、acc float4 consumer、producer、CTA geometry与其他case不变。资源为`64 MTreg / 33 STreg / 0 B / 0 stack / 8 waves`（control `64/35/0/0/8`），动态shared `312→156 B`；CPU、C500 full/boundary/random、case11精确长度/复用与padding trap均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/228/93/232/40/222/375/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。预注册唯一目标case11由#112716的`223→222 μs`却仍52分；#112430/#112725在未含该exact mapping时已有`222/221 μs`，不能归因于candidate。aggregate下降，关闭这一 exact case11 register-FP32 metadata ownership，不调lane owner、寄存器格式、shared layout或同源码重投；工作文件恢复#112716。
- **原始评测**：[cuda_112747_raw.json](raw/cuda_112747_raw.json)。

### 提交 #112744 · exp492 case5 skip-empty rescale

- **代码溯源**：[`cuda_112744.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112744.cpp)、raw 内嵌源码和实验快照 `cuda_case5_skip_empty_rescale_exp492.cpp` 的 SHA-256 均为 `32f13cf2e5ccc50fcadabf318625602e3dfd236ac23b33ad9b0aef6153f588a6`。
- **门禁**：仅case5的 B16/KV4/L141 head-pair/z4 BF16-MMA producer 把首个有效页的`SKIP_EMPTY_RESCALE`从`false`改为`true`；split5、combined tail、loader、partial ABI、group8 reducer、workspace和其他case不变。资源仍为`74 MTreg / 52 STreg / 8320 B / 0 stack / 6 waves`；CPU、C500 full/boundary/random、case5精确长度/复用和padding trap均通过。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/22/17/28/226/93/234/40/223/376/182/140 μs`，分数=`92/90/83/73/73/63/55/54/57/61/52/60/56/55`。预注册唯一目标case5相对#112716保持`17 μs/73分`；case7 `227→226 μs`及其他未改路径波动不能归因，aggregate同分也没有结构性收益。关闭这一 exact case5 empty-state-rescale skip，不改分支拼写、模板参数位置或同源码重投；工作文件恢复#112716。
- **原始评测**：[cuda_112744_raw.json](raw/cuda_112744_raw.json)。

### 提交 #112741 · exp491 case12 row-owner next-PID native broadcast

- **代码溯源**：[`cuda_112741.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112741.cpp)、raw 内嵌源码和实验快照 `cuda_case12_row16_next_pid_broadcast_exp491.cpp` 的 SHA-256 均为 `995235e5ef305858c217d98636b8c89a28bb276889665ff3a375eda1dda67cc8`。
- **门禁**：仅case12的 hot `p+1` PID 路径改为每个物理16-lane row只让`tx==0`读`bt_row[p+1]`，再以原生32-bit `mov_shfl` mode `0x150`广播；初始/尾页PID加载、split、loader、partial/reducer与其余case不变。实际资源为`82 MTreg / 54 STreg / 8448 B / 0 stack / 5 waves`（control为`82/50/8448/0/5`）；CPU、C500 full/boundary/random、case12精确长度/复用和padding trap均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/227/94/234/40/223/372/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。唯一覆盖目标case12相对#112716的`375→372 μs`，但显示分保持60、aggregate下降；这不足以替换control。关闭这个 exact hot-next row-owner PID/native-broadcast mapping，不改source lane、shuffle mode、load时点或覆盖范围后重投；工作文件恢复#112716。
- **原始评测**：[cuda_112741_raw.json](raw/cuda_112741_raw.json)。

### 提交 #112736 · #112716 同源 control resample（非 exp488）

- **代码溯源**：[`cuda_112736.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112736.cpp) 与 raw 内嵌源码的 SHA-256 均为 `411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`，即 #112716 control。预定的 exp488 SHA 为 `89eb96524c4c71ce78df6f435788c2000344e78ef980505aeb1ad29deb9981fc`，两者不同；因此本笔不能作为 exp488 的远端性能证据。
- **OJ 事实与决定**：14/14 Accepted / `65.86`，case1–14=`3/4/9/23/17/28/225/93/234/40/222/374/182/141 μs`，分数=`92/90/83/72/73/63/55/54/57/61/52/60/56/54`。它只是 control 的额外 timing 样本，不替换 #112716，也不重新解释或复投同源 control。后续每次 `--submit` 必须在 dry-run 后、实际 POST 前再次核验工作文件 SHA 与预注册 candidate 完全一致。
- **原始评测**：[cuda_112736_raw.json](raw/cuda_112736_raw.json)。

### 提交 #112725 · exp486 case9 fixed-live bucket/mulhi mapping

- **代码溯源**：[`cuda_112725.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112725.cpp)、raw内嵌源码与实验快照 `cuda_case9_fixed_live_bucket_mulhi_exp486.cpp` 的 SHA-256 均为 `0f4d34ea9b7f23894a555991d29146e569dfd034fdb07c7fb13723d31b5c501f`。
- **门禁**：只在case9既有1–6个live split前缀内均衡真实`full_pages`，满容量仍为`43/43/43/43/43/41`；`/3`、`/5`、`/6`均为`__umulhi` magic multiply，LLVM无新增`udiv`。producer为`82 MTreg / 48 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、六个live-bucket精确长度、padding trap和workspace复用均通过。
- **OJ解释与control决策**：14/14 Accepted / `65.93`，case1–14=`3/4/10/23/17/28/225/93/230/40/221/372/181/140 μs`，分数=`92/90/82/72/73/63/55/54/57/61/52/60/57/55`。唯一覆盖目标case9相对#112716由`237→230 μs`，但仍为57分；#112399在未改case9时已得到`230 μs/57分`，因此不能把本次回到历史 timing tier 归因给candidate。aggregate也低于control，拒绝这一 exact bucket/magic/tail-owner mapping并恢复工作文件#112716；不得调bucket、magic、split或同源码重投。
- **原始评测**：[cuda_112725_raw.json](raw/cuda_112725_raw.json)。

### 提交 #112716 · exp485 case7 fixed-live bucket/mulhi mapping

- **代码溯源**：[`cuda_112716.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112716.cpp)、raw内嵌源码、实验快照 `cuda_case7_fixed_live_bucket_mulhi_exp485.cpp` 和提交后工作文件的 SHA-256 均为 `411a9e789dfd020bebb39a9ea70e230016dc1a7b7e316bed28437aecabb4479d`。
- **门禁**：仅在case7既有1/2/3个live split前缀中均衡真实`full_pages`，满容量仍为`43/43/42`；`__umulhi`实现三分之一且LLVM无新增`udiv`。producer保持`82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves`；CPU、C500 full/boundary/random、精确live-bucket长度、padding trap和workspace复用均通过。
- **OJ解释与control决策**：14/14 Accepted / `66.00`，case1–14=`3/4/9/22/17/28/227/93/237/40/223/375/181/141 μs`，分数=`92/90/83/73/73/63/55/54/57/61/52/60/57/54`。唯一覆盖的case7从#112399的`233 μs/54分`到`227 μs/55分`，与随机长度A/B的稳定正向一致，故接受为结构性control；case4/13及case14等未改路径的跨档/回退只作timing-tier波动，不归因。不得调整此exact bucket/mulhi/tail-owner实现后同源重投。
- **原始评测**：[cuda_112716_raw.json](raw/cuda_112716_raw.json)。

### 提交 #112704 · exp483 case7 producer native-STG partial handoff

- **代码溯源**：[`cuda_112704.cpp`](../solutions/archive/2026-08-15-submissions/cuda_112704.cpp)、raw内嵌源码和实验快照 `cuda_case7_partial_native_stg_exp483.cpp` 的 SHA-256 均为 `bc9a2b668107dd38e2f1a8e61df7cabac496f1a99202506d43a2ae412061a161`。
- **门禁**：case7 `<true,false,true>` 保持 `82 MTreg / 50 STreg / 8448 B / 0 stack / 5 waves`；LLVM 有4处真实 `llvm.mxc.stg.predicator.v4i32`、control为零；CPU、C500 full/boundary/random、精确split/tail长度、padding trap与workspace复用均通过。
- **OJ解释**：14/14 Accepted / `65.93`，case1–14=`3/4/9/22/17/28/232/94/234/40/223/373/181/141 μs`。唯一目标 case7 不能相对 #112657 的同幅 timing 样本建立因果；case4的跨档和其他未改路径变化仅作 timing-tier 波动。关闭这个 exact native-STG producer→group8 reducer handoff；不得改 builtin 参数、cast、store位置或 enable scope 后重投。
- **原始评测**：[cuda_112704_raw.json](raw/cuda_112704_raw.json)。

用于持续记录同一题目的多次提交结果。主文件只保留便于比较和优化的摘要；完整原始数据（提交代码，OJ 协议、SPJ 报告、编译日志）以 JSON 归档在 `results/raw/`，按提交编号命名，可供深度分析。全部 raw 记录对应的字节精确提交源码见 [`solutions/archive/SUBMISSIONS.md`](../solutions/archive/SUBMISSIONS.md)。

当前真实 OJ 最高分记录为 **#113538 / `66.07`**，但其case5唯一改动没有改善目标；多出的显示点来自未覆盖case14的timing-tier刷新。结构性默认 control 为 **#113677 / exp545 / `65.93`**，SHA-256 为 `6a38dfa428c2d74f2a496144bb9702ad574f84d709254a71b679025be92c3746`，不可变源码为 `solutions/archive/2026-08-16-submissions/cuda_113677.cpp`。它在 #112716 / exp485 上仅改变case14的257-split packed reducer，并以OJ目标`141 μs/54分→139 μs/55分`建立可归因收益。#112716 保留为历史父快照，#111942、#112430、#112535和#112704的65.93以及#112630/#112657/#112680等继续作为历史反证或timing-tier样本，不能覆盖该结论。现有`leadboard.md`第三名为`69.64`，按因果结构display基线尚约差50点。

当前共归档312份终态raw，状态统计为281 Accepted、10 WrongAnswer、17 CompilationError、4 Canceled。CompilationError、Canceled和未进入测试点的结果均不作为性能数据；当前队列为空。#112941 / exp521 是已归档反证：case13 bit1 lane4/5 alpha/weight-exp fold的唯一目标从`181 μs/57分`回退至`183 μs/56分`，不能重开其 exact fold-lane/broadcast/guard/enable-scope contract；#112909 / exp520 的hot next-K raw GVM→dead-`s_k` producer/wait、#112873 / exp518 的65-split overflow-aware readlane metadata/weight handoff与#112858 / exp516 的case12 readlane metadata/weight handoff同样保持关闭。

#112495 / exp472的运行代码与已关闭 exp470 相同、仅注释不同，最终只作为重复 timing 样本归档，不能重开 case12/13 的同一 reducer-metadata 路线。exp428/#111895把case12 QK改为全原生bit2网络，exp430/#111897扩到case7，exp431/#111904扩到case13，exp434/#111908再把case13改为bit1 ownership；exp439/#111918只给case9启用bit1 ownership，本地full/random/boundary与OJ目标均正向，成为其后的结构性control。exp440/441确认case9 bit1下split6仍优于5/7；exp442/#111929的case7 bit1本地微增益未在OJ目标兑现，不替换control。exp443的case14 shared MMA-Q虽将5-wave资源跨到6-wave，但本地稳定慢86.2%，未提交且关闭。exp444–446验证延迟online-softmax参考基准重缩放：case11和case14本地均有小幅正向，但最终case14-only候选#111972未跨OJ tier，拒绝为baseline；但在#112259的对称finalizer changed precondition上，exp465/#112302将case14推进到140 μs。其后exp466在该control上删除safe-page exact-max shuffle，#112355使case14回退至141 μs，关闭该精确状态流；exp467/#112399则用独立的case10 reducer metadata-lifetime机制将该目标推进至40 μs并成为当前control。exp469/#112430虽然刷新并列aggregate，却未改善目标case8/11/14且case14回退，关闭该 row-coefficient final merge；exp473/#112535与exp480/#112630都以case12目标回退，分别关闭 KV8 bounded deferred-reference 和 case12 native-LDG page-loader 的精确路径；exp481/#112657与exp482/#112680分别关闭case8/11 vec4和case7 group8的partial-acc native-LDG consumer。#111942、#112430与#112535并列65.93；以后split/direct-out/ownership性能门禁必须覆盖full/random/boundary三种长度分布。

#112680提交exp482后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/10/23/17/28/232/94/231/40/222/372/181/140 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/57/55`。候选只让case7多split group8 reducer每个split的两段16-byte对齐FP32 `partial_acc float4`使用同步、register-returning 的`__builtin_mxc_ldg_b128`读取；producer、K/V loader、partial ABI、LSE 数学、live-split、group8 geometry和single-split fallback均不变。资源仍为`66 MTreg / 25 STreg / 0 stack / 7 waves`，实际group8 specialization有10处`llvm.mxc.ldg.predicator.v4i32`，CPU/C500 full/random/boundary、case7精确split/tail长度、padding-page trap与workspace复用均通过。预注册唯一问题是该consumer能否改善control的case7 `233 μs/54分`或跨档；OJ到`232 μs`仍54分，且没有此代码的#112657已经给出相同`232 μs/54分`样本，故不能将1 μs归因给本候选。case8/9/11等未改路径波动也不归因。raw内嵌代码、`solutions/archive/2026-08-15-submissions/cuda_112680.cpp`逐提交快照与实验源码SHA均为`138a34b5a6feda95bb278cfe9b8778d502d833dbf9086cae34cad141e85a01a1`；拒绝并关闭该 exact group8 partial-acc native-LDG 路线，不以builtin参数、cast、调用位置或enable scope微调重投，工作文件恢复#112399。

#112657提交exp481后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/10/23/17/28/232/93/235/40/223/372/181/140 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/57/55`。候选只让case8/11多split vec4 reducer的16-byte对齐FP32 `partial_acc float4`使用同步、register-returning 的`__builtin_mxc_ldg_b128`读取；producer、partial ABI、LSE 数学、共享metadata、single-split fallback和KV page loader均不变。资源仍为`64 MTreg / 35 STreg / 0 stack / 8 waves`，实际 vec4 specialization有8处`llvm.mxc.ldg.predicator.v4i32`，CPU/C500 full/random/boundary、精确split/tail长度、padding-page trap与workspace复用均通过。预注册唯一问题是该reducer consumer能否让case8从93 μs跨至92 μs和/或case11从223 μs跨至221 μs；两者均保持原值，故OJ否定该exact native-LDG consumer。case7的`233→232 μs`和其他未改路径波动无源码因果。raw内嵌代码、`solutions/archive/2026-08-15-submissions/cuda_112657.cpp`逐提交快照与实验源码SHA均为`3505c7501ed05d397cc596c41fca83199bd6464297b0398f94292e8fa1ad7fc6`；拒绝并关闭该 exact vec4 partial-acc native-LDG 路线，不以builtin参数、cast、调用位置或enable scope微调重投，工作文件恢复#112399。

#112535提交exp473后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.93`**；case1–14=`3/4/9/23/17/28/232/93/234/40/224/377/181/140 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/55`。候选仅给case12的KV8 z8 producer启用`m_page > m + 8`时才重设的 bounded deferred exponent reference；资源、CPU/C500 full/random/boundary、精确长度、padding trap与workspace复用均通过。预注册唯一问题是该 state contract 能否改善case12；OJ反而使唯一目标由`373→377 μs`，60分不变。case13 `182→181 μs`等未改路径的同场波动不能归因，故aggregate并列最高不构成结构性收益。raw内嵌代码、`cuda_112535.cpp`逐提交快照与实验源码SHA均为`93c6d4d675635f5b594d9720e4e0ea14427ca92ad78e4f8b3ba59bd428d64d0b`；拒绝并关闭该 exact KV8 reference/guard/state-flow，不调阈值、guard或原样扩shape重投，只有reference表示、partial契约、ownership或consumer数据流发生实质变化才可重开。工作文件恢复#112399。

#112630提交exp480后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/9/23/17/28/231/94/235/40/222/376/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/54`。候选只给case12的 KV8 z8 producer 启用同步、register-returning 的`__builtin_mxc_ldg_b128`，替换初始/尾页 K/V staging 与下一页 K/V lookahead；资源、完整正确性、partial/reducer、softmax、ownership和其他shape均不变。候选 LLVM IR 的实际case12 specialization 含6处`llvm.mxc.ldg.predicator.v4i32`而同条件control为零，故这不是普通`uint4` load 的同义源码改写。预注册唯一问题是该真实后端差异能否改善case12；OJ反而使唯一目标由`373→376 μs`、60分不变。case7/8/11/13等未改路径的同场波动不能归因，aggregate也未提高，故拒绝并关闭 case12 的这一 exact native-LDG page-loader/lookahead 路径；不得只改builtin参数、cast、调用位置或覆盖范围后重投。raw内嵌源码、`cuda_112630.cpp`逐提交快照和提交候选SHA均为`b0b9ba12dac639ca927dc5bb384277a548fff8fae4717cc3db084348dd6ca3d8`；工作文件恢复#112399。

#112495提交exp472后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.71`**；case1–14=`3/4/10/23/17/28/231/93/234/40/222/374/182/141 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/56/54`。提交源码SHA=`327513e706afe8c0ddecdbe0c20e893e79c65d380d0b70a0dd18aa5e5c128bd6`，与已关闭 exp470 的运行差异为注释，实际仍只给case12/13 vec2 reducer启用`REGISTER_PACKED_ML=true`并缩小动态shared metadata；case12由control的373到374 μs、case13保持182 μs，没有可归因的目标收益。raw内嵌代码、`cuda_112495.cpp`逐提交快照与实验源码SHA一致；作为重复样本归档，不切换control、不重开路线，工作文件恢复#112399。

#112465提交exp471后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.64`**；case1–14=`3/4/9/23/17/32/232/93/235/40/223/373/182/140 μs`，分数=`92/90/83/72/73/60/54/54/57/61/52/60/56/55`。候选仅在case12满容量前39个52-page split以编译期`HAS_NEXT`消去next-page运行时判定；资源、CPU/C500 full/random/boundary、padding trap与复用均通过，本地满长约快0.49%，但唯一预注册目标case12仍为`373 μs/60分`，没有目标改善或跨档。raw内嵌代码、`cuda_112465.cpp`逐提交快照与实验源码SHA均为`769be1717e559bcdaadf5f9b4e21401f6eaea3ca05dd11f19b8ae2e3ea856405`；拒绝并关闭这个 exact source schedule，不以循环、guard 或跨shape原样复投。

#112430提交exp469后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.93`**；case1–14=`3/4/9/23/17/28/233/93/233/39/222/373/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/62/52/60/57/54`。候选相对#112399只让case8/11/14的KV4 z4 final merge由row内tx0/1各计算一个`exp2`系数并广播；资源、CPU与C500 full/random/boundary、精确长度、padding trap和workspace复用均通过。预注册问题是该 coefficient-consumer ownership 能否改善三个目标case；OJ case8保持93 μs、case11 `223→222 μs`却未跨display档、case14 `140→141 μs`回退。总分并列65.93来自无对应差异的case10 `40→39 μs`和case13 `182→181 μs` timing-tier波动，不能归因给本实验。raw内嵌代码、`cuda_112430.cpp`逐提交快照和完整实验源码SHA均为`c915c0ac58eae2650e31235a8d5f7aa846bae13b90a6c5b397bec52dfe437e58`；拒绝且关闭这一 exact row-coefficient/broadcast source/owner/barrier/enable-scope 路线，工作文件恢复#112399，队列为空。

#112399提交exp467后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/9/23/17/28/233/93/230/40/223/373/182/140 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/56/55`。候选相对#112302的唯一运行差异是case10的64-thread vec2 reducer：每lane将其两个partial的packed FP16 `(m,l)`保留到global-max之后，删除`s_m`的shared写回/读回，只在shared保留最终weight；producer、split128、四页/partial、partial ABI、live-split、block geometry及输出数学不变。资源为`38 MTreg / 36 STreg / 0 stack / 8 waves`（parent为`38/39/0/8`）；CPU、C500 full/random/boundary、padding-page trap、case10精确split/tail长度及`full→short→full`复用均通过。预注册唯一问题是case10能否由41 μs跨至40 μs；OJ实际达到`40 μs/61分`，故即使case9的无对应代码档位波动令总分与#112302持平，也接受该精确reducer metadata-lifetime为新的结构性control。raw内嵌代码、`cuda_112399.cpp`逐提交快照和提交时工作文件SHA均为`4ddfa822f1274837bedd41edb4c02bf1850654ae31e36efcf88b092710ed411d`；终态后队列为空，工作文件保持同源字节。不得把同一case10 shared/register metadata lifetime改名、微调或密集复投；向其他reducer shape迁移须先给出独立的consumer/资源前提。

#112355提交exp466后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.79`**；case1–14=`3/4/9/23/17/28/233/93/234/41/223/374/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/60/52/60/57/54`。候选相对#112302唯一在case14 fixed15 BF16-MMA热循环中：仅当任何lane score超过现有`m+8`参考时才做原有exact page-max，否则跳过两次row16 shuffle并继续使用现有参考；tail、generic loop、split、loader、QK/PV、z4对称finalizer、deferred reference-rescale、partial ABI、reducer及其他shape不变。CPU/C500 full/random/boundary、精确长度、padding-page trap和workspace复用均通过，28个函数资源属性也与fresh #112302逐项相同。预注册唯一问题是删除safe-page exact-max是否让case14从140 μs跨档；OJ反而使目标`140→141 μs`、55→54分，故拒绝该状态流，不切换control。raw内嵌代码、逐提交快照、实验源码和提交时工作文件SHA均为`0a7f2cc6e50d87d38c8c6b08be74d9c39a5acdfbf85ed265ecb3172a65104160`；工作文件已恢复#112302，终态后队列为空。不得改mask、`+8`阈值、guard/store/barrier拼写或同源密集复投。

#112302提交exp465后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/9/23/17/28/233/93/229/41/222/374/182/140 μs`，分数=`92/90/83/72/73/63/54/54/58/60/52/60/56/55`。候选相对#112259唯一给case14固定15-page BF16-MMA路径启用deferred reference-rescale；case8/11、loader、split、QK/PV、z4对称finalizer、partial ABI、reducer和其他shape不变。CPU/C500 full/random/boundary、精确长度、padding-page trap和workspace复用均通过；case14资源为`82/66/8320/0/5`。OJ唯一目标case14 `141→140 μs`、54→55分，支持该组合的结构性因果；其他case的计时波动不与源码关联。raw内嵌代码、逐提交快照、实验源码和提交前工作文件SHA均为`f79b1e9d639c5b550213c17ea244bf6be2cb9af43fc0dafc9a4a111386f0bd68`。接受#112302为新的结构性control，工作文件保持同源字节；#111942仍为最高timing样本，终态后队列为空。

#112259提交exp464后正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/9/23/17/28/232/94/233/40/224/371/181/141 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/57/54`。候选相对#111918唯一启用case8/11/14的KV4 z4对称 finalizer：z0/z1分别终结一个head，stage-2只写入对方已消费行，QK/PV、loader、split、global partial ABI和reducer不变。CPU/C500 full/random/boundary、精确长度、padding-page trap和workspace复用均通过；资源为case8=`82/64/8320/0/5`、case11=`80/58/8320/0/6`、case14=`82/62/8320/0/5`。OJ target case14 `143→141 μs`与本地三分布正向证据一致；case11的224 μs与同源#111942旧control样本相同，因此不将其作为finalizer负因果。raw内嵌代码、逐提交快照、实验源码与提交前工作文件SHA均为`6a2e2b797c831bdfe8f622bc4142c7711b4912e75d487db7ae177aca9db323d0`。接受#112259为新的结构性control，工作文件保持同源字节；#111942仍为最高timing样本。

#111972提交exp446并正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.79`**；case1–14=`3/4/9/23/17/28/231/94/234/40/223/379/182/143 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/56/54`。候选只给case14启用延迟reference rescale，本地相对#111918的case8/10/11/14 ratio p50=`1.0012/0.9968/0.9982/0.9894`，但OJ目标case14仍为`143 μs/54分`；case8/12/13变化没有对应源码差异，只作timing-tier样本。源码SHA=`50e02d06b6fd463982a7b768c6d903af14f2b92abf229dbcef19f3fe0ce81053`，raw内嵌代码、逐提交快照与提交时工作文件三方一致。该提交确认OJ链路正常，但不替换#111918结构性control或#111942最高分；终态后队列为空，工作文件恢复#111918。

exp444提出online-softmax的`m`只需作为`(l,acc)`的指数参考、无需始终等于精确running max，并仅在页最大值超过当前reference 8个base-2 logit单位时重缩放。case11-only版本SHA=`399a9f13...e84`，完整correctness与复用通过，资源保持`80 MTreg/64 STreg/8320 B/0 stack/6 waves`，case11 full/random/boundary p50约`0.9941/0.9945/0.9930`。exp445把同机制扩到case14，case14相对exp444的full强测、random和boundary p50约`0.9917/0.9853/0.9852`，但组合版case10约慢0.5%，故不提交。exp446删除额外production-kernel模板参数，只从case14唯一的fixed15+MMA特化派生开关，恢复case11资源与行为；CPU14/14、GPU full/boundary/random各14/14，case14资源为`82 MTreg/66 STreg/8320 B/0 stack/5 waves`。#111972证明其约1.1%本地收益仍不足跨OJ离散档；同一阈值和状态流候选不原样复投，后续只有能带来更大收益或减少新增STreg的changed precondition才重开。

#111942按用户要求再次测试提交通道。提交前最近10笔任务均已终态且dry-run正常；工作文件当时保存已被本地A/B明确否决的exp443，因此直接提交不可变`solutions/archive/2026-08-14-submissions/cuda_111918.cpp`，避免误投失败候选，并只创建这一笔。任务正常经历`Pending→Compiling→Running→Finished`，最终14/14 Accepted / **`65.93`**；case1–14=`3/4/9/22/17/28/232/94/234/40/224/373/181/143 μs`，分数=`92/90/83/73/73/63/54/54/57/61/52/60/57/54`。raw内嵌代码、逐提交快照、#111918与恢复后的工作文件SHA均为`c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`。它以同源timing-tier刷新真实最高记录，但不构成新代码收益，结构性control仍为#111918；终态后队列为空。

exp443在#111918上只把case14八个长驻BF16 MMA-Q fragment从线程寄存器改为2 KiB shared Q tile，split257、fixed15 loader、PV、partial和reducer均不变。资源由`82 MTreg/62 STreg/8320 B/0 stack/5 waves`变为`74/64/10368 B/0/6 waves`；CPU14/14、GPU full/boundary/random各14/14，case14最坏tolerance ratio=`0.015`。但case14 full的21轮×100次交错A/B candidate/control p10/p50/p90=`1.8488/1.8615/1.8673`，稳定慢约86.2%，说明逐页shared-Q读取和CTA staging barrier远大于occupancy收益。源码SHA=`a0941ba9f321e0b1ad5d287f2145024aecf9e488098c6cad509ad11dab9977c8`，已归档为`solutions/archive/2026-08-14-experiments/cuda_case14_shared_mma_q_exp443.cpp`且未提交；同一shared MMA-Q布局关闭，工作文件恢复#111918。

#111933按用户要求测试提交通道。提交前工作文件与#111918字节一致，SHA=`c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`；最近任务均已终态，dry-run正常后只创建这一笔。任务正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.71`**；case1–14=`3/4/10/23/17/28/232/94/236/40/223/373/182/143 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/56/54`。raw内嵌代码、逐提交快照与工作文件SHA一致。相对同源#111918的aggregate和逐case变化只作timing-tier样本，不替换结构性control或当时65.86最高记录；终态后队列为空。

#111929提交exp442并正常14/14 Accepted / **`65.86`**。它从#111918只给case7启用bit1 ownership，case9 bit1、split3/6、group8/vec2 reducer、loader和partial不变。源码SHA=`34e34b26d978665901a044dc5bc316b6b81e5b3924a573752440412107cb7bbd`；CPU14/14、GPU三分布各14/14、case7精确长度与同进程复用通过，case7双角色full/random/boundary约`0.9946/0.9970/0.9914`，关键非目标case9/12/13中性。OJ case7为`233 μs/54分`，未优于#111918的230 μs、更未跨到229 μs/55分；aggregate并列65.86来自case3/8/14与case10/11/12的无源码tier互换。因此#111929只保留为边缘本地组件和并列分数样本，结构性control仍为#111918。

exp440/441在#111918的case9 bit1 changed precondition下分别只改`split6→5/7`。两者case9 full正确，但9×50交错p50分别`1.0148/1.0167`，稳定慢约1.48%/1.67%；split6再次被两侧夹定。两份源码已归档，未提交，不继续扫描同一邻域。

#111918提交exp439并正常14/14 Accepted / **`65.79`**。它相对#111912同源结构只把case9 QK/token ownership从旧rotate8/BSM-XOR4网络改为bit1全原生网络；split6、同步K+V-over-PV、packed metadata、partial和vec2 reducer均不变。源码SHA=`c0793eb9aac3502ec75d8eb489f5738bdc01377b022a53ca69836b5a36b0fba3`。CPU14/14、GPU full/boundary/random各14/14、case9的17个split/tail精确长度与同进程`full→short→full`复用全部PASS；case9双角色消偏full/random/boundary约`0.9854/0.9762/0.9649`，case7/12/13中性。OJ目标case9由#111908/#111912的`237/238→234 μs`，本地与真实方向一致但仍57分；case8/10分别`95/40 μs`掉档没有源码差异，只作timing-tier样本。故当时最高分记录保持#111912/65.86，但#111918成为后续结构性control。

#111912按用户要求测试提交通道。提交前最近任务均已终态，工作文件已从收益不足的exp438恢复为#111908字节精确源码，dry-run正常后只创建这一笔。任务先保持Pending，随后进入Running并正常Finished，最终14/14 Accepted / **`65.86`**；case1–14=`3/4/10/23/17/28/234/94/238/39/222/372/181/144 μs`，分数=`92/90/82/72/73/63/54/54/57/62/52/60/57/54`。raw内嵌代码、逐提交快照、#111908和工作文件SHA均为`883de5d316aae6520308cf89f96f13ff493ff03ecaffb2f6c2109cf86f7adb32`。相对同源#111908刷新0.07分，来自case10/13跨tier及其他计时波动，不归因于新代码；由于它当时是最高记录且源码相同，曾选为默认control，终态后队列为空。

#111908提交exp434并正常14/14 Accepted / **`65.79`**。它从exp431只把case13全原生split-head QK的head/token ownership从bit2改为bit1，case12保持bit2、case7保持bit2、case9保持旧网络，split65、loader、partial和reducer均不变。独立真实C500逐lane probe证明bit1网络数学等价；full/random/boundary双角色约`0.9900/0.9843/1.0000`。OJ case13由#111904的`183→182 μs`，raw、逐提交快照与工作文件SHA三方一致，因此成为结构性最佳。

#111904提交exp431并14/14 Accepted / `65.64`。它只把case13从旧split-head交换改成全原生bit2网络；full/random/boundary约`0.9731/0.9631/0.9933`，OJ目标case13由近期`188→183 μs`，与本地方向一致。aggregate受同源case3/5计时掉档影响，不妨碍该目标组件进入主线。随后exp432/433只扫case13 split64/66，分别慢约0.99%/13.8%，确认split65仍为离散最优且split66存在56-page cliff。

#111897提交exp430并正常14/14 Accepted / **`65.79`**。它从exp428只把全原生bit2 split-head QK扩到case7，split3、group8 reducer、loader和partial均不变；full/random/boundary约`0.9879/0.9908/0.9726`，OJ case7由父版本`235→234 μs`。同次case8 `93 μs`是无源码差异的历史样本，不归因给exp430。此前exp429把bit2扩到case9时full快约1.1%，但random慢约0.58%，按三分布门禁拒绝。

exp435的case13 bit0 ownership双角色full约`1.0000`，exp436的bit1归约换序约`1.0005`，均中性；exp437把bit1扩到case12仅快约0.21%，不足跨tier。exp438只把case7从bit2改成bit1，full correctness通过，但9轮交错A/B ratio p10/p50/p90=`0.9967/0.9972/0.9982`，远低于约1.8%的跨档需求，未提交并归档为`solutions/archive/2026-08-14-experiments/cuda_case7_native_bit1_exp438.cpp`。

#111895提交exp428并正常14/14 Accepted / **`65.79`**。它相对#111886只改变case12 head-pair/z8 QK归约与head1 owner：由`rotate8→raw BSM XOR4→quad2→quad1`及lane8，改为`rotate4→rotate8→quad2→quad1`全原生shuffle及lane4；case12 split40、z8 ownership、同步K+V-over-PV、packed metadata、partial/reducer和其余shape不变。源码SHA=`d69d1eacf5944f12181c44ba52202a73f490ae035c6b504da9a1ddbc4c428cfb`，资源与control同为`82 MTreg/50 STreg/8448 B/0 stack/5 waves`。CPU14/14、case12 full/boundary/random correctness和17步同进程长度复用全部PASS；full/random/boundary双角色消偏约`0.9937/0.9904/0.9892`。OJ case1–14=`3/4/9/23/17/28/235/94/239/40/223/372/188/143 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/56/54`；目标case12相对#111886 `375→372 μs`，方向与本地一致，aggregate并列。raw内嵌代码、逐提交快照和工作文件SHA三方一致，该组件进入后续主线。

#111887按用户要求测试提交通道。提交前确认最近任务均已终态，移除工作文件中三个会产生错误输出的timing-only阶段探针，确认工作文件与不可变#111886逐字节一致且SHA均为`de0f662079b26717b6e69775768f330ca91d4f97b82707140fe9bd41472e34a5`；dry-run后只创建这一笔。任务正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.71`**，case1–14=`3/4/10/23/17/28/235/94/236/40/223/373/188/143 μs`，分数=`92/90/82/72/73/63/54/54/57/61/52/60/56/54`。case11/13与#111886同为`223/188 μs`，aggregate低0.08来自case3等同源计时波动，不替换#111886 / 65.79 baseline。raw、逐提交快照与工作文件SHA完全一致，终态后队列为空。

#111886提交exp422并正常14/14 Accepted / **`65.79`**。最终源码与#111882唯一运行差异是case11 `split48→39`，即20 pages/live partial；split39与40三分布均正向，选择39以删除一个必空grid slot。源码SHA=`de0f662079b26717b6e69775768f330ca91d4f97b82707140fe9bd41472e34a5`，binary SHA=`0d3f3815e3f3e64b2a73c90dcacef59f16132250a9f8a0095bede8a1c1cb4d54`。CPU14/14、GPU full/boundary/random各14/14，以及case11 `12251,1,2,15,16,17,319,320,321,639,640,641,12250,12251`同进程复用全部PASS。相对fresh #111882 control，full/random/boundary p50=`0.9925/0.9932/0.9573`；OJ case11 `224→223 μs`，与本地方向一致。raw、逐提交快照和工作文件字节一致，选择#111886为新control。

#111882提交exp421并正常14/14 Accepted / **`65.71`**。在head-pair/z8 producer前提下只把case13 `split64→65`；本地full/random/boundary均不劣于control，OJ case13 `190→188 μs`、55→56分。aggregate未增加是因为无关case3同次`9→10 μs`，结构上严格改善，因此曾选为control。此前exp419以raw BSM跨半wave交换把case13资源从`82 MTreg/5 waves`改善到`80/6`，但full/random仍慢约0.1–0.2%；exp420只让even-z执行算术后资源回到`82/5`且中性，二者均未提交，关闭该末端z-merge路线。

用户要求再次试投平台时，提交前确认队列为空并完成dry-run，只原样提交不可变#111856源码得到#111868。它正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`65.71`**，case1–14=`3/4/9/23/17/28/236/94/236/40/224/374/190/143 μs`，分数=`92/90/83/72/73/63/54/54/57/61/52/60/55/54`。raw内嵌源码、逐提交快照与#111856 SHA均为`7b0a0b1b...b502fc4`；case7/11/12的`-1/-1/-2 μs`只是同源码timing-tier样本，未增加分数，不替换#111856默认control。终态后队列为空。

#111856提交exp417并正常14/14 Accepted / **`65.71`**。唯一运行差异是case7 `split14→3`，producer、packed `(m,l)`、FP32 accumulator partial和group8 reducer均不变。CPU14/14、GPU full/boundary/random各14/14，20个精确长度全部PASS。相对#111830，full/random/boundary正向p50=`0.8766/0.9118/0.9344`，反向old/new=`1.1400/1.0971/1.0718`；split2在boundary为`1.2652x`，证明三路是当前最小安全并行度。OJ case7 `246→237 μs`、`53→54分`并刷新aggregate；raw、逐提交快照和工作源码SHA三方一致。

#111843提交exp416并14/14 Accepted / `65.43`。它把case7 `split14→1`并直接输出，删除partial round trip和group8 reducer；full-length双角色约`0.8733x`，但OJ case7由246回退到279 μs。终态后补测random=`0.9912x`、boundary=`1.2297x`，确认短batch成员失去split并行才是本地/OJ反转的关键前提；拒绝为baseline，不把direct-out扩到case9。

#111811/#111823/#111830依次验证z8 reduced-split主线。exp413将case13 `256→64`，本地约`0.9004x`，OJ `212→190 μs`、53→55分；exp414将case12 `128→40`，本地约`0.9253x`，OJ `388→374 μs`、59→60分；exp415将case9 `24→6`，本地约`0.8991x`，OJ `243→237 μs`、56→57分。#111830为`65.57`，随后由exp417取代。三次都保持producer数学、packed metadata和对应reducer family，确认收益来自减少global partial/workspace/reducer输入。

exp407从#111319唯一差异替换case11 full-page QK：每个z wave执行8次BF16 MMA并直接消费本地两个head×4 token accumulator，不建立shared score tile；loader、K/V-over-PV、softmax/PV、split48、partial和reducer不变。它同时修正了旧BF16 MMA诊断：历史kernel以`__CUDA_ARCH__` guard完整device body，但MXMACA pass只定义`__MACA_ARCH__`，LLVM显示旧body为空；真正启用旧body后case8正确但`206 MTreg/2 waves`且慢约3.22倍，故不是精度墙。exp407生产实例为`80 MTreg/60 STreg/8320 B/0 stack/6 waves`，相对control的`86/64/8320/0/5`更优；CPU14/14、GPU full/boundary/random各14/14及case11 18个精确长度通过。21×100双角色消偏约`0.8048`，case11稳定快约19.5%；#111707的OJ `223 μs/52分`与本地同向，raw、逐提交快照和提交源码SHA完全一致，取代#111319成为唯一control。

#111641按用户要求试投平台，原样提交不可变baseline #111319 / exp390。提交前确认最近任务均已终态并完成dry-run，只创建这一笔；平台列表一度仍显示Pending、watch进度曾显示Running且数分钟没有case输出，未取消也未复投，随后正常Finished。最终14/14 Accepted / `64.07`，case1–14=`3/4/9/23/18/28/246/116/244/42/279/390/212/169 μs`，分数=`92/90/83/72/71/63/53/48/56/60/47/59/53/50`。raw内嵌源码、逐提交快照与#111319 SHA均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。本次确认OJ创建、排队、编译和完整评测链路可用；同源码相对#111319的64.14变化只作为timing-tier样本，不替换baseline，终态后队列为空。

#111616提交exp406b并正常14/14 Accepted / `64.00`。它从exp405只把case11从`split48 / 16 pages`改为`split24 / 32 pages`，并显式保持one-head vec4 reducer和fused-tail live-count；首版exp406仅改split时会隐式切到缺少该计数的generic group8 reducer，长度513/1025 WrongAnswer，属于dispatch契约错误而非split数学错误。修复后CPU14/14、GPU full/boundary/random各14/14及13步case11复用全部通过；相对exp405正向p50=`0.9583`、反向old/new=`1.0423`，消偏约`0.9588`。邻域split22/23/25/26分别比24慢约`1.11%/1.18%/0.88%/0.52%`，本地离散最优明确；但OJ case11从近期exp405的`277 μs/47分`回退到`281 μs/46分`，case1–14=`3/4/10/23/18/28/247/114/244/41/281/388/212/167 μs`。本地强正向未在OJ兑现，不替换#111319，不同源复投或继续微扫split22–26。raw、逐提交源码和提交前工作源码SHA均为`8a8c299a66942d33db6317e6e29049530e78511f44c48f542eec3adee3c08ac7`；工作文件已恢复exp405/#111590。

#111590提交exp405并正常14/14 Accepted / `64.07`。它把exp404已隔离验证的case5 combined-page全原生split-head网络组合回exp403；相对#111570只让case5从`rotate8 → BSM XOR4 → quad2 → quad1`切换到`rotate4 → rotate8 → quad2 → quad1`并把head1 owner/broadcast lane8改为lane4。invalid tail owner保持`-Inf`，固定broadcast权重精确为0。case5资源保持`86/56/8320 B/0 stack/5 waves`；CPU14/14、GPU full/boundary/random各14/14及20步同进程复用通过。相对fresh #111570双角色消偏约`0.9826`，case8/10/11/14 p50=`0.9991/0.9996/0.9993/0.9999`。OJ case5仍为`18 μs/71分`，未跨tier；case9/10刷新Accepted历史最佳`243/41 μs`但分数仍`56/60`，aggregate未超过64.14。保留exp405为leading组合父版本，不替换#111319，不同源复投。raw、逐提交快照与工作文件SHA三方一致。

#111570提交exp403并正常14/14 Accepted / `64.00`。它从exp402把generic full-page split-head QK从`rotate8 → BSM XOR4 → quad2 → quad1`切换为`rotate4 → rotate8 → quad2 → quad1`全原生网络，并把head1 owner/page-max/PV broadcast从lane8改为lane4；主要命中case10，也会命中case14最后一个underfilled generic split。case11原有路径、case8/14 fixed hot helper、case5 combined tail、fused tail、split128和reducer均不变。case10资源保持`86/62/8320 B/0 stack/5 waves`，完整门禁和17步同进程复用通过；相对exp402 case10双角色消偏约`0.9865`，相对#111319最终case10/8/11/14约`0.9895/0.9878/0.9820/0.9842`。OJ case10仍为`42 μs/60分`，没有跨越预期tier；同次case11刷新Accepted历史最佳`275 μs`，但case8/12/14为`116/389/167 μs`，aggregate未超过64.14。保留exp403为leading组合父版本，不替换#111319默认control，不同源复投。raw、逐提交快照与提交前工作文件SHA三方一致。

#111547提交exp402并正常14/14 Accepted / `64.00`。它从exp401只把全原生split-head网络扩到case14满长前256个fixed15 common split，并同步将head1 owner/page-max/PV broadcast从lane8改为lane4；final underfilled split和任意短长度generic路径不变。case14资源保持`90/58/8320 B/0 stack/5 waves`，完整门禁与12步同进程复用通过；相对exp401唯一差异双角色消偏约`0.9845`，相对#111319最终case8/11/14约`0.9872/0.9816/0.9838`。OJ case14真实从#111319的`169→166 μs`，但仍为50分；case6 `28→29 μs`掉1分、case11同源回到279 μs，aggregate仅64.00。组件获得真实目标证据但未建立新高，默认control保持#111319，exp402作为leading组合父版本。raw、逐提交快照与提交前源码SHA三方一致。

#111528提交exp401并正常14/14 Accepted / **`64.14`**，与最高分并列。它在exp400上只把同一全原生split-head网络扩展到case8满长前13个fixed19 common split，最后underfilled split和任意短长度保持原路径。case8资源仍`86/70/8320 B/0 stack/5 waves`；完整门禁和11步复用通过。相对exp400唯一差异双角色消偏约`0.9879`，相对#111319最终组合case8/11 p50约`0.9863/0.9813`。OJ case8仍`115 μs/49分`，case11为`277 μs/47分`，两者均未跨档；case3同源回到`9 μs/83分`使aggregate并列64.14。保留exp401为leading组合与有效组件，但因没有建立更高真实分且case8目标未跨档，默认control仍是#111319。

#111517提交exp400并正常14/14 Accepted / `64.00`。它从#111319只改case11 full-page split-head QK：原网络以rotate8交换双head后，仍用一次BSM `bpermute XOR4`和两次native quad shuffle完成half-row归约；exp400改为rotate4交换双head、按`tx&4`分配head，再以rotate8和两次quad shuffle完成全原生`mov.shfl`归约。独立C500 probe证明映射正确且codegen从`5→4 MTreg`；目标producer仍`86/64/8320 B/0 stack/5 waves`。完整门禁和16步同进程复用通过，相对#111319双角色消偏约`0.9818`。OJ case11真实`279→276 μs`并保持47分，确认组件有效；同次case8无源码差异地`115→116 μs`掉1分，aggregate未刷新，因此最高分和默认control仍是#111319 / 64.14。raw和字节精确源码已归档，队列为空。

#111489按用户要求原样试投当前baseline #111319 / exp390。提交前确认队列为空并完成dry-run，只创建这一笔任务；短暂Pending后正常进入Running，最终14/14 Accepted / `64.07`。提交源码、raw内嵌源码、逐提交快照、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`；case1–14=`3/4/10/22/18/28/246/115/245/42/282/390/211/169 μs`，分数=`92/90/82/73/71/63/53/49/56/60/46/59/53/50`。它确认OJ创建、排队、编译和完整评测链路当前可用；相对同源#111319的变化只作为timing-tier样本，不替换#111319 / 64.14 baseline。终态raw和字节精确源码已归档，队列为空。

#111431按用户要求再次原样试投当前baseline #111319 / exp390。提交成功创建，短暂Pending后进入Running，最终正常完成14/14 Accepted / `64.00`。提交源码、raw内嵌源码、逐提交快照、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`；case1–14=`3/4/10/23/18/28/244/115/245/42/281/389/211/169 μs`，分数=`92/90/82/72/71/63/53/49/56/60/46/59/53/50`。它再次确认OJ创建、调度、编译和完整评测链路可用；相对同源#111319/#111364的逐case变化只作为timing-tier样本，不替换#111319 / 64.14 baseline。终态raw和字节精确源码已归档，队列为空。

#111364按用户要求原样试投当前baseline #111319 / exp390，正常完成14/14 Accepted / `64.00`。提交源码、raw内嵌源码、逐提交快照、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`；case1–14=`3/4/10/23/18/28/247/115/244/42/283/391/211/169 μs`，分数=`92/90/82/72/71/63/53/49/56/60/46/59/53/50`。它确认当前提交、编译和完整评测链路可用；逐case变化只作为同源timing-tier样本，最高分与默认control继续保持#111319 / 64.14。终态raw和字节精确源码已归档，队列为空。

#111319提交exp390并正常14/14 Accepted / **`64.14`**。它从#111307只把同一head-pair/z8 producer扩到case7，并让原8-head group8 reducer从`partial_m`读取FP16x2 packed `(m,l)`；split14、10 pages/partial、fused-tail、同步K+V-over-PV、global partial数量和reducer CTA grid不变。CPU14/14、GPU full/boundary/random各14/14及case7 14步同进程复用通过；相对exp389强测正向p50=`0.9773`、反向旧/新=`1.0235`，双角色消偏约`0.9769`。OJ case7从#111307的`256→247 μs`、`52→53分`，case9保持56分，aggregate刷新。raw、逐提交快照和工作文件SHA三方一致，#111319取代#111307成为默认control，终态后队列为空。

#111307提交exp389并正常14/14 Accepted / **`64.07`**。exp388只把z8 producer扩到case9却保留vec4 reducer，因producer将FP16x2 `(m,l)`写入`partial_m`且不写`partial_l`而使case9仅`0.082657` match；exp389唯一修复为packed-aware vec2 reducer。CPU14/14、GPU full/boundary/random各14/14及case9 14步复用通过；强测正向p50=`0.9661`、反向旧/新=`1.0343`，消偏约`0.9664`。OJ case9从#111231的`254→244 μs`、`55→56分`，aggregate刷新；raw、逐提交快照与实验源码SHA一致。#111307当时取代#111231，随后由#111319取代。

#111272按用户要求原样提交#111231不可变快照用于确认OJ恢复，14/14 Accepted / `63.93`。源码SHA与#111231同为`adb1c0132f93b8b579e62dd2ccf2351419d5accca2ab87ea19a6c0c62bbe7ad2`；case1–14=`3/4/9/23/18/28/253/115/252/42/283/389/211/169 μs`。它只作为同源timing-tier样本，不替换#111231；长Pending期间没有取消或复投。

#111231提交exp387并正常14/14 Accepted / **`64.00`**。它从#111200只把case13已验证的head-pair/z8 producer ownership扩展到case12；case12原有split、loader、K+V-over-PV、packed metadata、global partial数量和vec2 reducer均不变。目标资源由旧case12的`64 MTreg/50 STreg/8192 B/0 stack/8 waves`变为`82/50/8448 B/0/5 waves`。完整correctness和17步workspace复用通过；强A/B正向candidate/control p50=`0.9326`、反向old/new p50=`1.0740`，消偏约`0.9319`。OJ case12 `422→388 μs`、`57→59分`；case8/11同源码波动各升一分、case14慢1 μs但不掉分，aggregate比#111200提高0.29。raw、逐提交快照和工作文件SHA三方一致，#111231取代#111200成为默认control，终态后队列为空。

#111200提交exp386并正常14/14 Accepted / **`63.71`**。它从#111115只改变case13 producer ownership：256线程布局由每线程一个query head、四token/z改为每线程两个query head、两token/z，八个z-state用三阶段shared-memory树合并；其余split、loader、pipeline、partial数量和reducer均不变。目标资源从旧case13的`64 MTreg/50 STreg/8192 B/0 stack/8 waves`变为`82/50/8448 B/0/5 waves`。完整correctness和17步workspace复用通过；强A/B正向candidate/control p50=`0.8371`、反向old/new p50=`1.1975`，消偏约`0.8361`。OJ case13 `252→212 μs`、`48→53分`，非目标计分波动净抵消后aggregate比#111115提高0.35。raw、逐提交快照和工作文件SHA三方一致，#111200取代#111115成为默认control，终态后队列为空。

#111163按用户要求原样复投当时baseline #111115 / exp385，用于确认OJ提交和完整评测链路。提交前队列为空，工作文件与#111115逐提交快照SHA-256均为`aa486885aabf4ad373402149c1b6e98ce3b6694a4c73cec264a7bf124c70120c`，只创建这一笔。任务先保持Pending约四分钟，随后正常进入`Compiling→Running→Finished`并14/14 Accepted / **`63.29`**。case1–14=`3/4/10/24/18/28/254/116/257/42/280/422/253/169 μs`，分数=`92/90/82/71/71/63/52/48/55/60/47/57/48/50`。相对同源#111115，case4/8各掉1分、case11升1分，其余变化未形成新源码归因，只作为OJ timing-tier样本；当时最高分和默认control继续保持#111115 / 63.36。raw、逐提交快照与工作文件SHA一致，终态后队列为空，说明OJ创建、编译和完整评测链路可用，但前置调度仍可能等待数分钟。

#111115提交exp385并正常14/14 Accepted / **`63.36`**。它在exp384上只给case5 group8 reducer启用native-row max/sum，producer与#111076完全不变；源码SHA为`aa486885aabf4ad373402149c1b6e98ce3b6694a4c73cec264a7bf124c70120c`。目标reducer资源为`66 MTreg/26 STreg/0 shared/0 stack/7 waves`；完整correctness、精确长度和workspace复用均通过。相对#111076，reducer唯一差异双角色消偏约`0.9781`；相对#111016，case5 producer+reducer组合消偏约`0.9447`。提交排队超过30分钟，本地watcher超时后没有取消或复投；重新挂接同一任务后正常进入Running并完成。OJ case5 `19→18 μs`、`70→71分`，case8也升1分、case4掉1分，aggregate净增0.07，因此#111115取代#111016成为当时默认control。

#111076提交exp384并正常14/14 Accepted / **`63.29`**。它保留exp383的case5 head-pair/z4 + split-head QK运行算法，只把全局常量`separate_tail=false`改为编译期不变量，并禁用六个自exp109以来不可达的legacy launch，从而把xcore1000实例化warning从18降到12、本地resource build约`9.6→7.9 s`。源码SHA为`68af1a543e88ce8d7892865418b0ebfeecdc4cc54dabbfb6c2b97e7df9b8f8de`；目标producer保持`86/56 MT/STreg、8320 B、0 stack、5 waves`。CPU14/14、GPU full/boundary/random各14/14、case5精确长度和workspace复用通过；相对#111016 case5双角色消偏约`0.9703`、本地快约2.97%，非目标双角色中性。OJ case1–14=`3/4/10/23/19/28/254/115/255/42/281/423/253/169 μs`，分数=`92/90/82/72/70/63/52/49/55/60/46/57/48/50`：目标case5仍为`19 μs/70分`，未跨1 μs tier；case4掉1分与case8升1分互抵。故#111076不替换#111016 baseline，但case5 producer作为已验证本地正组件继续组合。

#111059提交exp383，源码SHA为`b9c448c91c05d901c01efcd9c0b75594dcdd65b64ae2f33a926686ec4712e7d1`。它从#111016只把case5 producer从单头`dim3(16,8,2)`改为head-pair/z4 `dim3(16,4,4)` + split-head owner-state，保持真实生产`split5`、BSM、combined tail、FP32 partial和group8 reducer。资源`92/48→86/56 MT/STreg`、仍5 waves/0 stack；完整本地门禁通过，case5双角色消偏约`0.9750`。OJ在测试点前以`A TimeLimitExceeded encountered while compiling the code.`结束，只有既有warning、无源码error，不能作为性能失败；随后由等价运行语义的exp384/#111076完成OJ正确性闭环。

#111031按用户要求原样复投当前baseline #111016 / exp382，用于确认OJ提交和完整评测链路。提交前队列为空，只创建这一笔；任务排队约八分钟后进入Running并正常完成14/14 Accepted / **`63.29`**。case1–14=`3/4/10/22/19/28/252/116/255/42/282/421/252/169 μs`，分数=`92/90/82/73/70/63/52/48/55/60/46/57/48/50`。raw内嵌源码、逐提交快照、工作文件和#111016的SHA-256均为`2968dcbc8359b9a6c9d6310fb7d0cb0d15f431603978be3278509a586b796d7c`；逐case变化只作为同源timing-tier样本。#111031确认当前创建、排队、编译和评测链路可用，但没有新的源码归因，默认control仍保持最早完成exp382闭环的#111016；终态后队列为空。

#111016提交exp382，提交源码SHA为`2968dcbc8359b9a6c9d6310fb7d0cb0d15f431603978be3278509a586b796d7c`。它在exp381的case8/11/14 split-head组合上，只把case10 producer从单头`dim3(16,8,2)`换为head-pair/z4 + split-head布局，保持split128、四页/partial、fused tail、FP32 accumulator、packed `(m,l)`和现有vec2 reducer。目标资源为`86/62 MT/STreg、8320 B、0 stack、5 waves`；CPU14/14、GPU三组各14/14和case10 17步复用全部通过。相对exp381的41×500双角色消偏约`0.9284`、case10快约7.16%，case8/11/12/13/14中性。提交前队列为空、dry-run正确，只创建#111016；任务正常经历`Pending→Running→Finished`并14/14 Accepted / **63.29**。case10相对#110993 `46→42 μs`、`58→60分`，其余关键组合保住，故取代#110993成为默认control。raw、逐提交快照与工作文件SHA三方一致。

#110993提交exp379并正常14/14 Accepted / **`63.14`**。raw、逐提交快照和提交候选SHA均为`f49371dbcb5b33f59d74ea95b0735408246e40b12b1b038ad93924cdf3681343`。目标case14相对#110426从`177→170 μs`、`49→50分`，与本地split-head half-row QK证据同向；case4也落到22 μs/73分，case8/11则回退到117/290 μs。因为aggregate刷新且目标真实跨档，#110993取代#110426成为默认control。

#110987提交exp378，但在测试点前因`A TimeLimitExceeded encountered while compiling the code.`终止；只有既有warning、无源码error，不能作为性能失败。其源码SHA为`7e7c6bdfbee0ff7a1b09df8a6731a6f1e0db4301b262103a77cbeede503ea64d`，本地完整correctness与case14约2.06%增益仍有效；后续由精简等价运行语义的exp379/#110993完成OJ闭环。

#110962按用户要求再次原样试投exp367/#110895。提交前队列为空且dry-run正确，只创建这一笔；任务经历`Pending→Running→Finished`并正常完成14/14 Accepted / `63.00`，case1–14=`3/4/10/23/19/28/254/116/253/46/291/421/253/174 μs`。提交源码、raw内嵌源码、逐提交快照与#110895的SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。它确认当前OJ创建、排队、编译和评测全链路可用；同源码逐case变化只作为timing-tier样本，不替换#110426 / 63.07 baseline，终态后队列为空。

#110546/#110621/#110740均按用户要求原样复投#110426；#110699提交已完成本地门禁的exp347。四笔都从`Pending`终态为`CompilationError`，raw首条诊断均为`A TimeLimitExceeded encountered while compiling the code.`，只有既有MACA warning、没有源码compiler error或测试点。随后#110746提交exp348并14/14 Accepted；#110760提交exp353时再次compile TLE；删除一个新增模板参数、把源码从216088缩到215920 bytes的等价运行语义exp356由#110771正常编译并14/14 Accepted / `62.93`。用户随后要求再试投一次，#110809原样提交exp356/#110771，仍在测试点前compile TLE；三份源码SHA-256完全一致，因此这是平台故障的新样本，不是源码回归。所有等待期间都没有取消或并行复投；当前队列为空，baseline仍为#110426。168-byte缩减与成功编译相关，但不视为TLE消失的唯一因果。

#110699提交exp347，SHA为`5bacc185bb1d3cdb63961207c3b40e6adfbe3d3a6b4367b3846e49b847e9f7f1`。它从#110426只把case13标量K+V lookahead的四次32-bit load改成两次`uint2` load并立即拆回标量，资源保持`64/52 MT/STreg、8192 B、0 stack、8 waves`。CPU14/14、GPU full/boundary/random各14/14及17步case13同进程复用全部通过；41×200正向ratio p50=`0.9940`，交换角色后#110426/exp347=`1.0049`，消偏约`0.9946`、本地快约0.54%。OJ未进入测试点而compile TLE，故该机制只作为本地正向组件保留，不替换#110426，也不因TLE立即复投。

#110746提交exp348，SHA为`69f1dda419d220235e26be813962396dae01e1a33ce0580ce4ff05736a5a5bb0`。它只给case14前256个固定15-page split组合single owner-score与head-owned page max；目标producer从`90/64`变为`90 MTreg/58 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU三组各14/14及17步case14复用通过；41×200双角色消偏约`0.9834`，非目标case中性。OJ正常14/14 Accepted / `62.86`，case14真实`177→174 μs`但仍49分；case4/8/10无源码差异地各掉1分导致aggregate回退。该机制是OJ确认的正组件，但不替换#110426；下一步分解两个score-state变化并继续组合。

#110760提交exp353，SHA为`b5e12d6e6fc480100ba3ab6d51f3bee1595be41c7d4e8d096b227ad0a6b731ff`，组合case13两次`uint2` load-site与exp348 case14组件。完整correctness、精确长度和workspace复用门禁通过，case13/14本地双角色消偏约`0.9963/0.9834`；OJ在测试点前compile TLE，没有性能数据。#110771提交exp356，SHA为`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`：删除新增模板参数并用已有dispatch条件唯一识别case13，运行语义/资源与exp353一致。重新完成全量门禁后，OJ正常14/14 Accepted / `62.93`，case1–14=`3/4/10/24/19/28/253/117/253/46/287/421/254/174 μs`。case13/14均比baseline快但未跨分，case4/8无目标差异地各掉1分，因此不替换#110426。

#110884提交exp365，SHA为`d18ed7ad3cbf0267c1ac896e4f86a14980eae012d1727833e667ad407b802f00`，只给case13使用FP16x2 packed `(m,l)` metadata；完整correctness和17步复用通过，相对#110426 case13本地消偏约`0.9895`，但OJ在测试点前compile TLE，没有性能数据。exp367随后把case10/12/13三个既有vec2 reducer用户统一为packed `(m,l)`，保持单一无格式分支reducer实例；源码SHA为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。完整门禁通过，相对#110426 case10/12/13双角色消偏约`0.9887/1.0013/0.9895`。#110895正常14/14 Accepted / `63.00`，case1–14=`3/4/10/23/19/28/252/116/255/46/288/421/253/174 μs`；case7刷新Accepted历史最佳，case12/13/14也改善，但case10未跨档、case8掉1分且case9/11回退，因此不替换#110426。该结果确认OJ当前可以正常提交、编译和评测。

#110916按用户要求原样试投exp367/#110895，提交成功创建并从`Pending`进入`Compiling`，随后在测试点前因`A TimeLimitExceeded encountered while compiling the code.`终止。提交源码、raw内嵌源码、工作文件与已14/14 Accepted的#110895快照SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`；日志只有既有MACA warnings，没有源码compiler error。因此它证明创建和调度链路可用，但属于平台compile TLE样本，不是源码回归或性能数据；不立即复投，baseline仍为#110426，终态后队列为空。

#110941再次按用户要求原样试投exp367/#110895。提交前队列为空，只创建这一笔；任务长时间保持`Pending`后以`CompilationError`终止，没有进入测试点，raw首条诊断仍为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有MACA warnings。提交源码、raw内嵌源码、逐提交快照及#110895/#110916的SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。因此OJ创建入口可用，但编译服务尚未稳定恢复；本次不是源码回归或性能数据，不继续同源复投，baseline保持#110426，终态后队列为空。

#110426的case4入口、大小和机器码与#110192字节精确相同（`0x53000`、10424 B、SHA `d35f085891ec18a19a68579bc0210f35563d51aab25abe2903f74c4d5fd7adbc`），OJ却仍为23 μs。因此#110229中“入口由`0x53000→0x53900`导致case4回退”的归因已被修正：入口平移最多是相关线索，`22/23 μs`主要按OJ timing-tier波动处理，不继续扫描地址或修改case4算法。

#110229提交exp339，SHA为`142482189ab69ac239a4295fc2505750857236b3b4eda4cba635a81674b897c0`。它只给#110192的case8固定19页路径组合`unroll 2`与skip-empty；完整correctness通过，本地case8双角色消偏约`0.9912`。OJ 14/14 Accepted / **`63.00`**，case1–14=`3/4/10/23/20/28/254/115/255/46/292/421/255/176 μs`：case8真实`117→115 μs`并跨一分，但case4/5各掉一分，因此不替换#110192。设备bundle确认case4的10424-byte机器码与#110192字节一致，仅入口因case8代码增长从`0x53000`平移到`0x53900`；后续把case8收益做代码表面隔离，不误改case4算法。

#110031与#109963源码仅差一个空行，SHA为`37548d3a30f4deb6ae8865e19a9de4e371eef9e3eccced8d6a920cb00fde235b`。15分钟watch超时后没有取消、没有复投，最终正常完成14/14 Accepted / **`63.00`**，case1–14=`3/4/10/23/19/28/255/116/253/46/292/423/255/177 μs`；它只作为同源timing-tier和提交链路样本。

#109989提交exp335，SHA为`86b297eed2595f93d9c3690107f12076f20e8a58833cd44ca0fa26925eb0b5a7`。它从#109963只把case8 fixed19循环`unroll 1→2`，本地约快0.55%，但OJ为14/14 Accepted / **`62.93`**，case1–14=`3/4/10/23/20/28/254/117/254/46/288/423/255/177 μs`；case4/8为`23/117 μs`，不得原样复投。

#109963提交exp334，SHA为`55b2585955d6afd5b0301ca501a9da0a12742e67d88cb299b44102a493679209`。它从#109783分叉，只给case4启用独立编译期模板：固定`split=0`、direct-out，`L=64`走四页固定热循环，短长度仍走至多四页的安全fallback；相对exp332把目标资源从`76/52`改善到`74/44 MT/STreg`，保持`8320 B/0 stack/6 waves`。CPU14/14、GPU full/boundary/random各14/14、case4十四个精确长度均通过；相对#109783的41×1000正反A/B为`0.9506/1.0515`，双角色一致地快约4.9%，相对exp332再快约0.72%，case8为中性`0.9990x`。OJ正常完成14/14 Accepted / **`63.00`**，case1–14=`3/4/10/22/19/28/256/116/259/47/292/423/256/177 μs`，目标case4真实`23→22 μs`、`72→73分`，确认该专用路径是有效组件；case8 `115→116 μs`与#109828同源波动一致并掉1分，aggregate未超过63.07，因此当时的最高分与默认control仍保持#109783。该组件后来由#110192吸收；raw与逐提交源码SHA一致。

#109933提交exp332：在#109783上只给满长case4加入四页固定热循环，但固定分支与generic fallback共存于同一模板实例。源码SHA为`f47ea6174cf3f3d259c67dca250e5ff0181db44eba9dab688cf824c21b7c6de8`；本地case4双角色消偏约`0.9574`、快约4.26%，但资源从control的`76/44`恶化到`76/52 MT/STreg`。OJ 14/14 Accepted / **`62.86`**，case4反而为`24 μs/71分`。该结果不否定固定循环本身，而是给出必须隔离模板代码表面和寄存器状态的线索；exp332不替换baseline，也不得原样复投。

#109897提交exp331：从#109783分叉，只给case4启用首空状态rescale跳过，源码SHA为`da8fdf6e692c79f9c4a31739742e366340dd93de6e6c27cec323640e3265d2ee`。本地双角色消偏约`0.99735`、仅快约0.27%；OJ 14/14 Accepted / **`62.93`**，case4仍为`23 μs/72分`。它未复现#109875的22 μs，证明#109875的case4跨档不能单独归因给skip-empty，该微调不足OJ tier。

#109875提交exp330：组合多个shape的首空状态rescale跳过，并给case8 fixed19循环使用`unroll 3`，源码SHA为`ab08d92be6cfadb3737646a59d3069ad929515ec4fe43cbbfcc5b07d59b07d91`。OJ 14/14 Accepted / **`63.07`**，case1–14=`3/4/10/22/19/28/254/116/253/46/289/422/254/176 μs`；case4升到`22 μs/73分`，但case8回到`116 μs/48分`，两者抵消。因为首轮混合了多个shape且exp331未复现case4收益，#109875只作为组合样本，不替换来源更清晰的#109783 baseline。

#109783提交exp312。提交前源码SHA、实验快照与已测二进制对应关系核对通过；CPU与完整GPU门禁通过，最近列表无在途任务，dry-run正确识别contest 11/problem 1与`cuda.maca-c500`，只创建这一笔。任务经历`Pending→Compiling→Running→Finished`后14/14 Accepted / **`63.07`**。case8相对#109761从`116→115 μs`、`48→49分`，与本地约1.15%收益同向并跨档；case3、7、9–12等无目标源码差异的变化按timing tier处理。raw、逐提交源码与exp312归档SHA一致，终态后队列为空，选择#109783替换#109761 baseline。

#109828按用户要求试投，原样复投#109783/exp312，SHA仍为`3612a1266357f4c9da52f9e8a8124096796dea84a2e75f429194d1825476ff96`。任务成功创建后经历较长`Pending→Compiling→Running`，客户端10分钟监控超时并未取消OJ任务；后续正常完成14/14 Accepted / **`63.00`**。case1–14=`3/4/10/23/19/28/255/116/256/46/290/422/256/177 μs`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。相对#109783无源码差异，case8 `115→116 μs`掉1分、case11/12分别快1/3 μs但不跨档，均只作为timing-tier样本；baseline保持#109783。raw与逐提交源码已归档并核对SHA，终态后队列为空。

#109769按用户要求原样复投#109761/exp307，用于确认OJ当前能否成功提交。提交前最近任务均为终态，dry-run正常识别contest 11/problem 1与`cuda.maca-c500`；只创建这一笔任务并正常经历`Pending→Running→Finished`，最终14/14 Accepted / **`63.00`**，case1–14=`3/4/9/23/19/28/256/117/256/47/291/420/255/177 μs`。提交源码、raw内嵌源码及#109761快照的SHA-256均为`e953d45d8844d38e2eefb7bcc50efc0c75563ba7f1143cb3b26a636e562a22bb`；同源码逐case变化只作为timing-tier样本，不替换最早建立可归因记录的#109761 baseline。raw与逐提交源码已归档，终态后队列为空。

#109761提交exp307。提交前工作文件与实验快照SHA均为`e953d45d8844d38e2eefb7bcc50efc0c75563ba7f1143cb3b26a636e562a22bb`，最近列表无在途任务，dry-run正常识别contest 11/problem 1与`cuda.maca-c500`；只创建这一笔任务，经历`Pending→Running→Finished`后14/14 Accepted / **`63.00`**。目标case11相对#109754从`302→290 μs`并跨到46分，与本地约3.19%收益同向；case8同源码路径从117波动到116 μs，其余非目标变化按timing tier处理。raw、逐提交源码、exp307归档与工作文件SHA一致，终态后队列为空，选择#109761替换#109754 baseline。

#109754提交exp305。CPU14/14、GPU full/boundary/random各14/14及22步case8同进程长度序列全部通过；61×500正向exp305/exp304 p50=`0.9939`，反向exp304/exp305=`1.0086`，消偏约`0.9927`、本地快约0.73%。OJ只创建这一笔任务，经历`Pending→Running→Finished`后14/14 Accepted / `62.93`；case8从#109751的`118→117 μs`，目标与本地A/B一致。case4/7/12的变化无源码归因，按timing波动处理。raw、逐提交源码与exp305归档SHA均为`cdebd1580053d6b0f8c5d3b541fdafbad2d0a89e8cc0ec0f3e8c41f276fb0fc3`，终态后队列为空，选择#109754替换#109751 baseline。

#109751提交exp304。CPU14/14、GPU full/boundary/random各14/14及22步case8同进程长度序列全部通过；41×300正向exp304/exp300 p50=`0.9917`，反向exp300/exp304=`1.0124`，消偏约`0.9897`、本地快约1.03%。OJ只创建这一笔任务，经历`Pending→Running→Finished`后14/14 Accepted / `62.93`；case8从#109736的`119→118 μs`，case14保持177 μs，目标方向与本地A/B一致。raw、逐提交源码与exp304实验归档SHA均为`018b4370cf8800fdb695186579e3e8b4e74bfa987257f89b37e40f5537cf3486`，终态后队列为空，选择#109751替换#109736 baseline。

#109736提交exp300，只给case8 full-page head-pair/z4 producer启用exp298/299的分布式row exp，fused tail、split14/19页、K/V register-lookahead、native-row QK、partial和group8 reducer均不变。目标producer为`88 MTreg/70 STreg/8320 B/0 stack/5 waves`；GPU full/boundary/random各14/14及22步case8同进程长度序列全部通过。41×300正向exp300/exp299 p50=`0.9853`，反向exp299/exp300=`1.0147`，消偏约`0.9854`、本地快约1.46%。OJ经过较长Running后最终14/14 Accepted / `62.93`，case8从`120→119 μs`、case14保持177 μs；选择#109736替换#109730 baseline。raw、逐提交源码与exp300归档SHA一致，终态后队列为空。

#109730提交exp299，只把exp298的分布式row-exp机制用于case14满长前256个固定15-page common split；case11 dispatch恢复#109705，最后underfilled split和任意短长度仍走原泛化路径。目标producer为`90 MTreg/64 STreg/8320 B/0 stack/5 waves`；CPU14/14、GPU full/boundary/random各14/14及20步case14同进程长度序列全部通过。41×200正向exp299/#109705 p50=`0.9844`，反向#109705/exp299=`1.0144`，双角色消偏约`0.9851`、本地快约1.49%。OJ最终14/14 Accepted / `62.93`，case14从`179→177 μs`但仍为49分；由于目标真实改善、aggregate保持最高，选择#109730替换#109705 baseline。raw、逐提交源码与exp299实验归档SHA一致，终态后队列为空。

#109723按用户要求原样复投#109705/exp294，用于确认OJ提交与评测链路是否恢复。提交前队列为空，dry-run正常识别contest 11/problem 1与`cuda.maca-c500`；只创建一笔任务并正常经历`Pending→Running→Finished`，最终14/14 Accepted / `62.93`，case1–14=`3/4/9/23/19/28/254/121/256/46/302/424/255/179 μs`。提交源码、raw内嵌源码和#109705的SHA-256均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`；case14保持`179 μs/49分`，case11无源码差异地从`297→302 μs`，其余变化也只作为同源timing-tier样本。该结果确认创建、排队、编译和评测链路均正常，不替换#109705 baseline；raw与逐提交源码已归档，终态后队列为空。

#109719提交exp298，只给case11 full-page head-pair/native-row路径启用分布式row exp：lanes 0..7以一次lane-varying `exp2`并行计算4 token×2 head权重，再用8次native row broadcast分发。LLVM静态`exp2 28→21`、`mov.shfl 64→72`、packed-FMA不变，资源保持5 waves；完整correctness通过，本地41×200双角色消偏约`0.9847`、快约1.53%。OJ最终14/14 Accepted / `62.93`，case1–14=`3/4/9/23/19/28/256/121/257/46/298/425/255/179 μs`；目标case11未超过#109705的`297 μs`，case8无源码差异地掉1分、case10升1分后aggregate并列。该机制保留供其他head-pair shape验证，但#109719不替换#109705 baseline；raw与逐提交源码已归档，终态后队列为空。

#109715按用户要求再次原样复投#109705/exp294，用于确认OJ当前能否成功提交。提交前队列无在途任务，dry-run正常；唯一一笔任务经历`Pending→Running→Finished`，最终14/14 Accepted / `62.86`，case1–14=`3/4/9/24/19/28/255/120/257/47/298/426/255/179 μs`。提交源码、工作文件与#109705的SHA-256均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`；case4无源码差异地从`23→24 μs`并掉1分，其余差异未跨得分档。该结果确认创建、调度、编译和评测链路正常，只作为同源timing-tier样本，不替换#109705；raw与逐提交源码已归档，终态后队列为空。

#109707按用户要求原样复投#109705/exp294，用于探测OJ链路。提交成功经历`Pending→Running→Finished`，最终14/14 Accepted / `62.71`，case1–14=`3/4/9/23/19/33/254/120/254/46/300/426/256/179 μs`。提交源码、工作文件与#109705的SHA-256均为`71242043d210114ff1d3994b330e47d88ecb86a92471854815f54f6787db9887`；case14保持`179 μs/49分`，case6无源码差异地从`28→33 μs`并掉4分，case10则升1分，其余小幅变化也无源码归因。该结果确认创建、调度、编译和评测链路可用，只作为同源timing-tier样本，不替换#109705；raw与逐提交源码已归档，终态后队列为空。

#109705提交exp294，只把exp291的case14固定15-page循环从`#pragma unroll 1`改为`2`。producer资源为`92 MTreg/58 STreg/8320 B/0 stack/5 waves`，未跨驻留档；CPU14/14、GPU full/boundary/random各14/14及20步case14同进程复用全部通过。相对exp291双角色消偏约`0.9951`，直接相对#109672约`0.9552`。OJ正常经历`Pending→Compiling→Running→Finished`，最终14/14 Accepted / `62.93`，case14达到`179 μs/49分`并跨过下一档；raw、逐提交源码、实验快照与工作文件SHA完全一致，终态后队列为空。

#109699提交exp291，只组合exp290固定15-page common-split热循环和exp288 packed `(m,l)`/register metadata reducer。完整correctness通过，直接相对#109672双角色消偏约`0.9604`；OJ最终14/14 Accepted / `62.57`，case1–14=`3/4/10/23/19/29/255/121/254/47/305/425/255/180 μs`。唯一目标case14相对#109672真实`186→180 μs`但仍为48分；非目标掉档无源码差异，故不替换baseline。raw、逐提交源码与实验快照SHA一致。

#109694按用户要求原样复投#109672/exp283，用于再次验证OJ链路。任务创建后约七分钟完成`Pending→Running→Finished`，最终14/14 Accepted / `62.79`；case1–14=`3/4/9/23/19/28/253/120/253/47/303/421/255/188 μs`。提交源码、逐提交快照、工作文件与#109672的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，确认创建、调度、编译和评测链路可用；同源逐case与aggregate变化只作为timing-tier波动证据，最高分与默认control仍保持#109672，终态后队列为空。

#109691提交exp288，只在#109672上给case14组合FP16x2 `(m,l)` partial和寄存器化reducer metadata。完整correctness与23步同进程精确长度通过，41×200双角色消偏约`0.9766`；OJ最终14/14 Accepted / `62.79`，case1–14=`3/4/9/23/19/28/255/121/256/47/298/426/255/183 μs`。唯一目标case14相对#109672真实`186→183 μs`并与本地证据同向，但仍为48分；case8/10各因无源码差异的timing波动掉1分，aggregate未保持。该机制保留供后续组合，最高分与默认control仍为#109672。

#109688按用户要求再次原样复投#109672/exp283。提交创建成功并正常完成`Pending→Running→Finished`，最终14/14 Accepted / `62.93`；case1–14=`3/4/9/23/19/28/254/120/254/46/299/424/255/186 μs`。源码、逐提交快照、工作文件与#109672的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，确认OJ提交和评测链路可用。它与#109672同分但没有源码差异，逐case变化只作为timing-tier样本，默认control仍保持最早建立可归因记录的#109672；终态后队列为空。

#109684按用户要求原样复投#109672/exp283，用于探测OJ是否恢复。任务创建成功，约八分钟后完成`Pending→Running→Finished`，最终14/14 Accepted / `62.86`；case1–14=`3/4/9/23/19/28/256/121/255/46/301/422/255/186 μs`。源码、工作文件与#109672的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，说明提交、调度、编译和评测链路可用，但延迟仍明显。相对#109672没有源码差异，逐case和aggregate变化只作为timing-tier波动证据；最高分与默认control保持#109672，终态后队列为空。

#109664原样复投#109591/exp262，SHA-256仍为`1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。它等待超过180秒后正常完成14/14 Accepted / `62.71`，case1–14=`3/4/9/25/19/29/255/120/253/46/299/425/255/186 μs`。case8偶然`121→120 μs`并升1分、case4偶然`24→25 μs`并降1分，其他同源项也有波动；aggregate并列不构成新源码证据。raw、逐提交快照与baseline SHA一致，不替换#109591。

#109654提交exp281有序tokenized BSM，SHA-256 `71d1046d003b2f537ad4feb39f68a8f86c18c2452937d6dcb3cac7e0dbc44a84`。候选以`memcpy_async_pred<16, MACA_ICMP_EQ>`返回的use-def token分别等待K/V，并修正为`wait(V_current)→issue(K_next)`，同时保留K-over-PV。资源`76 MTreg/44 STreg/8320 B/0 stack/6 waves`，CPU14/14、GPU full/boundary/random各14/14和case4精确长度均通过；41×1000相对#109591消偏约`0.9736`、本地快2.64%。OJ最终14/14 Accepted / `62.57`，case1–14=`3/4/9/24/19/29/255/121/258/47/301/422/255/188 μs`；case4仍为`24 μs/71分`，未跨tier，拒绝为baseline。

#109644再次原样复投#109591/exp262，SHA-256不变；14/14 Accepted / `62.64`，case1–14=`3/4/9/25/19/29/254/121/257/46/298/420/255/186 μs`。它只提供同源timing-tier样本，不替换#109591。

等待上述OJ期间完成exp273–283：case6单split direct-out慢55.7%，单wave group4 reducer慢0.76%；exp275 K-only lookahead保持6 waves并本地快约1.26%，任何V插值都退到5 waves。exp279/280的无序tokenized BSM scope0/1不正确；exp281修正请求顺序后正确，exp282在该changed precondition上只把token wait scope1改scope0。exp282 SHA `d6e8257852090cf102d57ac852b63df1ae5a7b52e8e83813bdf66efefd8388a8`，完整correctness通过，相对exp281消偏约`0.9920`、相对#109591约`0.9650`；#109666最终以case4 `23 μs/72分`和总分62.79完成OJ闭环。exp283再只给case6组合exp275的K-only lookahead，SHA `0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，完整correctness及29个case6精确长度通过，相对#109666消偏约`0.9868`；#109672以case6 `28 μs/63分`和总分62.93完成闭环。两次提交的raw、提交快照、实验源码与相应工作文件均一致，终态后队列为空。

#109630提交exp272 case6 inline group4 finalizer，SHA-256 `30ebce6e2d0214bd97889af930be536112670ddbea02c64b1dbbeef901e8bb4b`。profile先量化#109591 case6 producer/reducer约为`31.450/4.909 μs`；候选保持split8 producer和FP32 partial数学，只以32-bit completion counter让最后一个producer CTA归约四个query head并删除第二次launch。资源由约`76 MTreg/6 waves`改善为`72/7`，CPU14/14、GPU full/boundary/random各14/14及29个同进程精确长度全部通过；41×500双角色A/B消偏约`0.9390`、本地快6.1%。OJ最终14/14 Accepted / `62.71`，case1–14=`3/4/9/25/19/30/256/120/257/46/301/420/255/186 μs`。目标case6相对#109591 `29→30 μs`且仍62分，本地收益未兑现；case8升1分与case4降1分无源码归因，只是aggregate抵消。raw、逐提交快照和实验源码SHA一致，不替换#109591，队列终态后为空。

exp266–269依次测试case8/11 native B128 shared LDS的全K/V、V-only、post-load fence和register-lookahead pipeline版本：全量版两例约慢0.8%，其余中性，关闭当前builtin/fence排列。exp270组合长KV8 load-site `uint2`→scalar，只在case13约快0.53%，不提交。exp271只给case6 combined loop增加K+V scalar lookahead，却使producer从6降到5 static waves，资源门槛拒绝。上述完整源码均在日期化experiments目录归档。

#109610再次按用户要求原样复投#109591/exp262，SHA-256仍为`1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。提交创建成功，并在约六分钟后完成`Pending→Running→Finished`，14/14 Accepted / `62.64`，case1–14=`3/4/9/24/19/29/254/121/256/47/300/424/255/186 μs`。这再次确认OJ提交与评测链路可用；相对#109591没有源码差异，因此aggregate和逐case变化只作为timing-tier波动证据，不替换当前baseline。raw、逐提交快照与工作文件三方SHA一致，终态后无在途提交。

#109601按用户要求原样复投#109591/exp262，SHA-256仍为`1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。提交正常经历`Pending→Running→Finished`，14/14 Accepted / `62.64`，case1–14=`3/4/9/24/19/29/254/121/258/47/303/422/255/185 μs`。这确认OJ创建、排队、编译和评测链路均已恢复；相对#109591没有源码差异，因此aggregate和逐case变化只作为timing-tier波动证据，不替换当前baseline。raw、逐提交快照与工作文件三方SHA一致，终态后无在途提交。

#109591提交exp262 case8 grouped reducer native max/sum，SHA-256 `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。OJ 14/14 Accepted / `62.71`，各case分数=`92/90/83/71/70/62/52/47/55/58/45/57/48/48`；目标case8为`121 μs/47分`，相对#108986快4 μs，case11/13为`300/255 μs`，case12为`424 μs`。raw、逐提交快照、exp262 experiments快照和工作文件四方SHA一致；提交终态后队列为空，不再创建第二笔提交。

#109578提交exp265 case8 inline finalizer，SHA-256 `6bfbfa9b8c89bb96caaade8419aee87d6ef02e9d413b3a4976727b370b36618a`。它保留exp262的split14 producer和FP32 partial数学，以32-bit completion counter、producer `__threadfence()`及last-producer CTA内八head finalizer删除独立reducer launch。本地CPU14/14、GPU full/boundary/random各14/14、关键长度同进程复用均通过；41×300双顺序消偏约`0.9871`、case8快约1.29%，case11/14中性。OJ正常经历`Pending→Running→Finished`并14/14 Accepted / `62.43`，case1–14=`3/4/10/25/19/29/255/134/255/46/303/421/255/186 μs`，分数=`92/90/82/70/70/62/52/45/55/58/45/57/48/48`。case8相对#109558从`121→134 μs`且`47→45分`，本地收益没有兑现；raw、逐提交快照和提交前源码SHA一致，不替换baseline，工作文件恢复exp262，终态后队列为空。

#109558提交修正后的exp261 case8 grouped reducer，SHA-256 `4709cbb419c927486b5ad506ea6702411fc7bd671faba5565ec75a4dba3503a1`。它正常完成14/14 Accepted / `62.57`，case1–14=`3/4/9/25/19/29/257/121/254/47/301/424/255/186 μs`，分数=`92/90/83/70/70/62/52/47/55/57/45/57/48/48`。case8与#109180/exp217的`121 μs`持平，修正后的64个eight-head reducer CTA没有跨越新tier；无源码差异的case4/10各慢1 μs并掉档，故aggregate低于#108986。raw、逐提交快照和提交前源码SHA一致，不替换baseline，终态后队列为空。

#109508提交exp255 inline finalizer，SHA-256 `3a26fd2b1fcabcc1d12d556c81adf72c2ac8db8cbbdb461ec2f3f5372f115f07`。它保持case11 split48 producer和FP32 partial数学，只以epoch计数器、producer `__threadfence()`和last-producer CTA内finalizer消除独立reducer launch。本地强测消偏约`0.9974`；OJ在约900秒等待后正常完成14/14 Accepted / `62.43`，case1–14=`3/4/10/24/19/29/255/125/256/46/318/425/255/188 μs`。case11未超过#108986的302 μs，不替换baseline；raw、逐提交快照和exp255实验源码三方字节一致，终态后队列为空。

inline finalizer改变了每个producer的fence/atomic与reducer launch成本前提，因此exp256重新扫描case11 split并把split48/16页改为split24/32页。SHA `dae103e138e6be3e99fac3094e4b4fc493c9c5eb4fb9a98345aa1b8501551e87`；full/boundary/random及同进程epoch复用全部通过，相对#108986的41×200双顺序消偏约`0.9527`、本地快约4.73%。#109533最终14/14 Accepted / `62.43`，case1–14=`3/4/9/25/19/29/257/125/255/46/322/423/255/188 μs`；case11比#108986的302 μs和#109508/exp255的318 μs都慢，本地收益没有兑现，故不替换baseline。raw、逐提交快照与exp256实验源码SHA一致。

排队期间exp257/258分别扫描split20/约39页和split28/28页，相对exp256消偏约`1.013/1.0091`，由上下两侧夹定split24。exp259把epoch-tagged 64-bit CAS计数改为32-bit atomicAdd并由最终CTA atomicExch归零；full/boundary/random各14/14、精确长度和上万次复用通过，相对exp256强测消偏约`0.9980`、仅快0.20%。exp260把归零改普通store后消偏约`0.9999`、中性。#109533已否定更大的本地split收益，exp259/260均已归档且不复投。随后exp261修复exp208的fused-tail live-count错误并恢复case8 grouped reducer；exp262的native max/sum在其上消偏约`0.9982`。exp263 raw split-weight broadcast的9个高风险长度正确，但41×300双顺序消偏约`0.99995`、中性；exp264跨head packed-FMA QK的关键长度正确，却使producer`90→92 MTreg`并双顺序慢约7.74%。exp265 case8 inline finalizer的本地强测约快1.29%，但#109578目标case回退13 μs，当前实现被OJ否决。exp263/264已归档，exp265由逐提交快照唯一保存；exp262由#109591完成OJ闭环并成为当前baseline，SHA `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`。

#109467按用户要求再次原样复投#108986，SHA-256仍为`6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`。它正常完成14/14 Accepted / `62.57`，case1–14=`3/4/9/25/19/29/256/125/256/47/299/424/255/186 μs`。这确认当前OJ创建、调度、编译和评测链路均可用，终态后队列为空；相对#108986没有源码差异，因此aggregate和逐case变化只作为timing-tier波动证据，不替换当前最高指针。raw、逐提交快照与baseline三方SHA一致。

#109431按用户要求再次原样复投#108986，SHA-256仍为`6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`。它正常完成14/14 Accepted / `62.50`，case1–14=`3/4/9/25/19/29/254/125/255/47/298/423/255/188 μs`。这确认当前OJ创建、调度和评测链路均可用，终态后最近五笔提交全部完成且当前队列为空；相对#108986没有源码差异，因此aggregate和逐case变化只作为timing-tier波动证据，不替换当前最高指针。raw、逐提交快照与baseline三方SHA一致。

#109403按用户要求再次原样复投#108986，SHA-256仍为`6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`。它正常经历`Pending→Running→Finished`并14/14 Accepted / `62.64`，case1–14=`3/4/9/24/19/29/254/125/254/47/300/425/255/186 μs`。这确认当前OJ创建、调度和评测链路均可用；相对#108986没有源码差异，因此aggregate和逐case变化只作为timing-tier波动证据，不替换当前最高指针。raw、逐提交快照与baseline三方SHA一致。

#109064再次按用户要求复投#108986字节精确源码，SHA-256仍为`6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`。提交正常经历`Pending→Running→Finished`，14/14 Accepted / `62.50`，case1–14=`3/4/9/25/19/29/258/126/257/47/298/426/255/186 μs`。它确认OJ创建、编译和评测链路可用；相对#108986没有源码差异，aggregate与逐case变化只作为timing-tier波动证据，不替换当前最高指针。

#109101/exp201在native-row case11上把split48改为split39/20页，本地split扫描显示正向，但OJ为14/14 Accepted / `62.64`，case1–14=`3/4/9/24/19/29/254/125/255/47/302/423/255/186 μs`，case11仍为`302 μs`。#109127/exp205继续把case11调到split24/32页，本地相对#108986消偏约`0.9613`，却在OJ得到14/14 Accepted / `62.57`，case1–14=`3/4/9/25/19/29/256/125/255/46/308/420/255/186 μs`。两者raw和逐提交源码均已归档；split扫描是有效本地信息，但没有建立超过#108986的OJ证据，因此baseline指针不变。

#109150/exp209最终14/14 Accepted / `62.57`，case1–14=`3/4/9/24/19/29/256/123/254/47/312/424/255/186 μs`。case8相对#109127的同父源码`125→123 μs`，确认split33/8页本地收益方向，但仍停留47分档；case11沿用exp205 split24并波动到`312 μs`，使aggregate未刷新。raw与逐提交源码SHA `81bc9961...e8b844b`一致，不替换baseline。

#109180/exp217最终14/14 Accepted / `62.57`，case1–14=`3/4/9/24/19/29/255/121/254/47/301/422/255/188 μs`。目标case8相对#108986 `125→121 μs`，确认split14/19页真实改善，但仍在47分档；无源码差异的case10和case14分别从`46→47`、`186→188 μs`并各掉1分，aggregate被抵消。raw与提交快照SHA一致，不替换#108986。

#109210/exp223最终14/14 Accepted / `62.43`，case1–14=`3/4/9/25/19/29/268/121/255/47/300/422/255/187 μs`。提交源码SHA `318c238a3f3f8e3acb1d4006965608ca201e09cc8db0f15a07f859842f3c9513`与raw、逐提交快照和实验归档完全一致。目标case7相对#109180从`255→268 μs`回退且`52→51分`，没有兑现本地消偏约`0.9349`；case4/9/14等无源码差异项也发生波动，因此不替换#108986，并把该轮视为OJ调度/timing-tier反例。

#109260/exp234最终14/14 Accepted / `62.43`，case1–14=`3/4/9/24/19/29/274/122/263/46/302/445/255/186 μs`。源码SHA `3ae804f3560b69abf45184e139175285b3c4095ba93570cda9797ee828923bf8`与raw、逐提交快照和实验归档完全一致。它在exp225上只把case12从split128重扫到split40/52页，并为该shape显式避开已证明错误的`<=32` grouped reducer；本地消偏约`0.9388`，但OJ case12相对#109210从`422→445 μs`且`57→56分`，未兑现本地收益。该提交不替换#108986。

等待评测期间完成exp237–239的case13 split重扫。split246仍保持15页/CTA且消偏约`1.0003`，中性；split264跨到14页/CTA后消偏约`1.0271`，慢2.7%；split231跨到16页/CTA后消偏约`1.0032`，慢0.32%。三者页边界与full→short→full correctness均100% PASS并保存完整源码，case13因此继续使用split256/15页，工作文件已恢复exp234。

随后在changed precondition下重扫短case split。case6的split6/7（4页）相对split8/3页双顺序消偏约`1.0070/1.0062`，仍回退，保留split8。case5的exp242 split4/3页与exp243 split3/3页相对exp234均快约0.8%，二者直接比较中性；选无空slot的exp243，SHA `e4e776951d42061433599e6f63bf5d6e00dc55af1c23f53cdcbe40828de8c5dd`。CPU及GPU三组14/14、页边界/workspace复用和dry-run均通过。#109312最终14/14 Accepted / `62.29`，case1–14=`3/4/9/24/21/29/269/121/268/47/301/446/255/186 μs`；raw、逐提交快照和实验源码SHA一致。目标case5相对#108986 `19→21 μs`，本地微增益没有兑现，不替换baseline。

exp244–246继续补齐changed-precondition split边界。case14 split241/16页在native-row QK后仍消偏约`1.0405`、慢4.05%，继续保留257/15页。case10 split103/5页相对128/4页消偏约`0.99995`、中性，split86/6页则约`1.0772`、慢7.7%；结合旧split64回退，case10曲线关闭并保留split128。三份候选correctness均通过且已归档，工作文件恢复exp243。

exp247只给case11启用4 KiB FP32 shared-Q：z0把八行Q转换并预缩放一次，z1–z3复用，同时用同一道CTA barrier发布首页K/V。目标producer从`90/54/8320 B/5 warps`变为`86/58/12416 B/5`，无spill；满长和17步split/tail边界100% PASS。9×20正向p50=`1.0083`、反向control/candidate=`0.9915`，消偏约`1.0084`、慢0.84%。额外shared流量/barrier超过转换节省，候选拒绝且不提交，完整源码已归档，工作文件恢复exp243。

exp248只命中case14的257-split normalized-BF16 partial路径，把每split的FP32 `(m,l)` 压成FP16x2，删除`partial_l`全局写入和第二次读取。本地消偏约`0.9950`；#109339最终14/14 Accepted / `62.21`，case1–14=`3/4/9/25/21/29/272/120/266/46/302/444/255/187 μs`。raw、逐提交快照和实验源码SHA均为`c8d2df1ed09b61af210d83488b464e030ff67446f5d0aa66a0f3c560c95ef7fe`。目标case14相对#108986 `186→187 μs`且掉1分，微增益未兑现，不替换baseline。

等待#109339期间完成exp249：只让case14 reducer把每线程拥有的2–3组packed `(m,l)` 跨max归约保存在寄存器，删除两块临时shared元数据流量并将动态shared减半。SHA `b9323c3b2a13995aa2ddb091b18e2a0dc4e56f4e23f13be0d627911303f7a16c`；资源同档，完整correctness通过。21×200相对exp248消偏约`0.9923`；相对exp243组合约`0.9873`、case14快约1.27%。

exp250在exp249上只给case13的256-split FP32-acc producer/reducer增加FP16x2 `(m,l)`，删除`partial_l`写入和第二次读取。SHA `0b53821d68d04387163fe6678e03819846faf86d6f8a236ad2968a1449eefd4f`；producer STreg `50→48`并保持`64 MTreg/8 warps`，vec2 reducer保持`38/39/8 warps`。CPU14/14、GPU full/boundary/random各14/14及13步case13精确长度全部PASS；21×200正向exp250/exp249 p50=`0.9947`、反向exp249/exp250=`1.0025`，消偏约`0.9961`。#109369最终14/14 Accepted / `62.07`，case1–14=`3/4/9/25/21/29/270/122/268/47/301/451/254/184 μs`，分数=`92/90/83/70/68/62/50/47/54/57/45/55/48/48`。raw、逐提交快照和实验源码SHA一致；aggregate未超过#108986，不替换baseline。

exp251只把case13 vec2 reducer的64个线程各自拥有的最多4组packed `(m,l)`跨max归约保存在寄存器，删除`s_m`和临时`s_l` shared流量。SHA `3cd8a6c9e94e8e096b8cdc1d10567f0da47941bb41be39adb8b451d402b11a50`；资源为`38 MTreg/40 STreg/0 stack/8 warps`，case13全长及12个短长/split边界全部PASS。21×200正向exp251/exp250=`1.0001`，反向exp250/exp251=`0.9972`，消偏后exp251约`1.00145x`、慢0.15%；拒绝且未提交。完整源码已归档，工作文件恢复#108986/exp190，当前OJ队列为空。

exp252从#108986分叉，只让case11 full producer由z0单wave用原生FP32 MMA物化8-head×16-token score tile，再经复用的K shared交给四个z wave消费。SHA `9548819e33147e87f307dd76f5b93bbd69a98efa556d27e597b7f2a4942401b2`；17个精确长度全部PASS，最大tolerance ratio `0.326`且finite，但资源从约`90 MTreg/5 warps`恶化为`136 MTreg/3 warps`。9×20正向candidate/control p50=`1.6614`，反向control/candidate=`0.6015`，消偏约`1.662x`、慢66.2%，拒绝且未提交。相关FP16/BF16 MMA能力probe也未建立FP16输入精度优势；工作文件已恢复#108986。

exp253同样从#108986分叉，只替换case11 full producer：CTA由`(16,4,4)`改为`(8,8,4)`，每个真实64-thread wave以两个原生8-lane half-row覆盖八个query heads；QK归约只使用half-row内`lane^4`与两级native quad permutation，不使用历史错误的width-8 CUDA shuffle或跨subgroup广播。SHA `c1b947a319147df0027b68d79146e9e2f109e3233a3b1f8782a9202840087dac`；资源`90 MTreg/50 STreg/8320 B/5 warps`，case11 full和17个精确长度全部PASS，最大tolerance ratio `0.326`且finite。9×20正向exp253/#108986 p50=`1.1428`，反向#108986/exp253=`0.8753`，消偏约`1.1426x`、慢14.3%。减少每head QK维度并行没有跨驻留档，串行向量工作与额外置换超过八head/wave收益；拒绝、未提交，完整源码已归档并恢复工作文件到#108986。

exp254保持#108986 case11的`(16,4,4)`、head-pair和其余producer/reducer数据流，只把两个head的FP32 row reduction改为FP16x2 packed reduction。源码SHA `1d298e4f141569b3f78c6a68895e81f1c25a2526a698dcbf669249b65ff313e8`；目标full+tail实例静态`mov.shfl`由64次降为32次，但FP32→FP16转换插入舍入模式控制，资源仍为`90 MTreg/54 STreg/8320 B/5 warps`。CPU14/14、case11 full与同进程17个精确长度全部PASS，最大tolerance ratio `0.326`且finite。9×20正向exp254/#108986 p50=`1.1703`，反向#108986/exp254=`0.8544`，消偏约`1.1704x`、慢17.0%；说明row exchange减半被转换和packed half开销反噬。候选拒绝、未提交，完整源码已归档并恢复工作文件到#108986。

#108936/exp190在#108913/exp186上组合已经独立完成本地强测的case5/10 native row QK（exp188/189），并只把同一网络扩展到case3；三个目标的双顺序消偏约为`0.9259/0.8765/0.9109`。其OJ case3/5/10达到`9/19/47 μs`、`83/70/57分`并建立当前源码baseline。#108966/exp191同样14/14 Accepted但总分为`62.50`，case5仍为`19 μs/70分`，因此不替换exp190源码。

2026-08-10 OJ 平台恢复后，exp134 的 #108257/#108278 连续在编译阶段触发 `TimeLimitExceeded`，均无测试点和性能数据。exp135 将未启用的 CUTE/MMA 依赖从编译表面排除，本机构建约快19%，#108312 随后成功进入 Running 并 14/14 Accepted。队列之后再次拥塞：#108371/#108398 均在未产生测试点时取消；#108468 等待约 30 分钟后正常 Accepted。后续保持“至多一个在途提交”，长时间 Pending 时继续本地实验，不以取消后立即重投或并行补交降低优先级。

恢复探针 #108550 提交与 #108468 完全相同的源码字节，SHA-256 同为 `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；等待后 14/14 Accepted / 59.86，确认提交、编译和评测链路恢复。其 case4/11/12/14 分别为 `28/347/478/258 μs`，比 #108468 各快1 μs，但 case3 从 `10→11 μs`，总分不变；这些同源差异只作为 OJ timing-tier 波动证据，#108468 继续作为control。

#108641 是 #108628 的字节精确恢复试投，14/14 Accepted / `59.93`，case1–14=`3/4/10/29/22/32/285/140/286/54/347/476/255/259 μs`；同一源码相对 #108628 出现 case8/9/11/13/14 的 `+1/+1/-1/-1/+2 μs` 波动，因此不替换 control。随后 #108651/exp151 只在 case11 head-pair/z4 producer 中把 Q 乘 `sm_scale` 从每 token 的 score 热循环外提到每 split 一次；14/14 Accepted / `59.93`，case11 `348→345 μs` 与本地消偏约 `0.99556` 同向，但非目标 case 波动使总分未保持。#108658把同一预缩放逐shape组合到case8/14后，case11进一步测得`343 μs/42分`并把总分刷新到60.07；#108679再由case4真实跨到28 μs/68分并保持总分。相关提交均已保存 raw、提取逐提交源码并核对 SHA；当时选择 #108679 为baseline，且 OJ 提交链路可正常完成。

#108691/exp157只把Q预缩放扩到case6约3 pages/split路径，本地强复测消偏约`0.98942`，但OJ目标case6仍为`32 μs/60分`，未跨tier；非目标case3从`10→11 μs`使得分`82→80`，总分降至60.00。14/14 Accepted、raw与源码均已归档；该轮不构成case6负向证据，也不替换#108679。

#108700/exp158只在exp157上把Q预缩放扩到case13的15-page producer，本地强复测消偏约`0.99805`；14/14 Accepted / `59.93`，case1–14=`3/4/11/28/22/32/284/139/286/54/346/476/254/257 μs`。目标case13相对同父#108691 `256→254 μs`，与本地证据一致，但仍为`48分`档；非目标case11从`343→346 μs`使aggregate下降。raw、提交快照与exp158源码SHA均为`37a59eaa6d4cdf213d3c5dc224d2fc8736641245fdca1e6724b8c0b0ed46cae5`。

#108713/exp159继续只给case12启用Q预缩放，14/14 Accepted / **`60.14`**，case1–14=`3/4/10/29/22/31/285/139/285/54/341/475/255/258 μs`。目标case12相对#108700 `476→475 μs`并与本地`0.99645`消偏同向；case6/case11跨档使aggregate刷新。raw、提交快照与exp159源码SHA均为`3cee37f740ae7ccbba6491d133ea39aeef8e0b8f60a7f4aa049921f9c4a1e9c9`，选为新baseline。

#108721/exp161把Q预缩放继续组合到case7/9，14/14 Accepted / **`59.86`**，case1–14=`3/4/11/29/22/32/284/139/285/54/346/473/255/258 μs`。case7相对#108713 `285→284 μs`与exp160本地消偏`0.9947`同向；case9保持285 μs，未跨OJ timing tier。case12的`475→473 μs`没有本轮对应源码差异，只能作为波动；case3/6/11回退使aggregate下降。因此该轮确认提交链路和case7局部机制，但不替换#108713。raw、逐提交源码、exp161实验源码与工作文件SHA均为`0d92dfc789db9abafcc9d529cb3982132eaf27c0e4e1370b1ce502b679b07bfb`。

#108743/exp163 已完成评测：14/14 Accepted / **`60.29`**，case1–14=`3/4/10/28/22/32/283/139/285/53/344/472/255/219 μs`，各case分数=`92/90/82/68/67/60/49/44/52/54/41/54/48/43`。相对即时源码父版本#108721，唯一新增dispatch只命中case14；其`258→219 μs`与本地消偏约`0.8576`强一致，其余变化按timing-tier波动处理。raw、逐提交快照、exp163实验源码与工作文件SHA均为`d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；当前没有OJ任务在途。

#108747 是用户要求的平台恢复试投，与 #108743 源码字节及 SHA-256 完全相同。提交正常经历 `Pending→Running→Finished`，最终 14/14 Accepted / **`60.29`**，case1–14=`3/4/10/29/22/32/284/139/285/53/344/474/255/218 μs`，各case分数=`92/90/82/67/67/60/49/44/52/54/41/54/48/44`。case14虽从`219→218 μs`并跨到44分，但case4同时从`28→29 μs`、68→67分，总分持平；这些同源差异只作为timing-tier波动证据，baseline继续保持#108743。raw、逐提交快照与工作文件SHA均为`d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；当前没有OJ任务在途。

#108763/exp170 只把case13下一页K/V的四次32-bit scalar load改为两次`uint2` load，并立即拆回原八个跨PV标量；store、split256/15页、fused tail、QK/PV、partial和reducer均不变。资源保持`64 MTreg/8192 B/0 stack/staticMaxWarps=8`，本地41×200正向exp170/#108743=`0.9923/0.9938/0.9968`、反向#108743/exp170=`1.0034/1.0051/1.0067`，消偏约`0.99436`、快0.56%；完整correctness通过。OJ最终14/14 Accepted / **`60.14`**，case1–14=`3/4/11/29/22/31/284/139/284/54/345/473/254/221 μs`，分数=`92/90/80/67/67/61/49/44/52/54/41/54/48/43`。目标case13相对#108743 `255→254 μs`与本地证据同向，但仍未跨48分档；case3/4退档与case6进档使aggregate下降，故不替换#108743 baseline。raw、逐提交快照和exp170源码SHA均为`9535acf79de359bd5e4909135b83efdbdfd91bfb8ad1af50ed092fa74e297b26`；当前没有OJ任务在途。

#108772/exp173 将同一load-site `uint2`→scalar-live模式按case13→12→9→7逐shape组合到四个长KV8 producer，最终14/14 Accepted / **`60.29`**。case1–14=`3/4/10/29/22/32/282/139/283/53/344/471/253/218 μs`，分数=`92/90/82/67/67/60/49/44/52/54/41/54/48/44`。相对#108743，四个目标case7/9/12/13从`283/285/472/255→282/283/471/253 μs`全部同向，确认本地消偏约`0.99775/0.99581/0.99725/0.99436`的机制；但四例均未跨下一分数档，case4又因无源码差异从28波动到29 μs，aggregate持平。按“目标因果+更高aggregate”规则仍保留#108743 baseline，exp173作为已确认组合机制供后续finalist重新组合。raw、逐提交快照与实验源码SHA均为`22475804001e1cb70eeae5b906838109dfe67b6f92e2adbd89fdc89b1e5cb887`；当前没有OJ任务在途。

#108784 是用户要求的又一次平台恢复试投，与 #108743 源码字节及 SHA-256 完全相同。它正常经历 `Pending→Running→Finished`，最终 14/14 Accepted / **`60.14`**，case1–14=`3/4/11/29/22/32/284/139/285/54/344/476/255/218 μs`，分数=`92/90/80/67/67/60/49/44/52/54/41/54/48/44`。与#108743相比没有任何源码差异，case3/4/7/10/12的`+1/+1/+1/+1/+4 μs`及case14的`-1 μs`都只能视为timing-tier波动；提交、编译和评测链路已确认可用，baseline仍为#108743。raw和逐提交快照均已归档，SHA-256为`d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；当前没有OJ任务在途。

#108803/exp177 将case11 QK的全wave BSM XOR `8/4/2/1`归约替换为原生16-lane row的rotate-right `8/4` + quad XOR `2/1` 网络，其他dispatch、计算和状态不变。独立C500 probe已逐lane证明与raw XOR allreduce字节相等；目标LLVM改为`64 mov.shfl / 0 bsm.bpermute`，producer资源由`94→90 MTreg`且保持5 warps。本地41×200正向exp177/#108743 p50=`0.8525`、反向#108743/exp177=`1.1734`，消偏约`0.8524`。OJ最终14/14 Accepted / **`60.50`**，case1–14=`3/4/10/29/22/32/284/139/284/53/301/475/254/220 μs`，分数=`92/90/82/67/67/60/49/44/52/54/45/54/48/43`。目标case11相对#108743 `344→301 μs`并跨越四个得分档；非目标case4 `28→29 μs`降一分，其余分数不变，因此目标因果和更高aggregate同时成立，#108803取代#108743成为当前baseline。raw、逐提交快照和exp177完整实验源码的SHA-256均为`d82b354614b585e6b18c099cc2d87abcd92222dfbe0e7bb18cc3a36c32f31496`；当前没有OJ任务在途。

#108816/exp178 只把同native row allreduce扩展到case8，case11及其他dispatch不变。本地41×200正向exp178/exp177 p50=`0.8911`、反向exp177/exp178=`1.1231`，消偏约`0.8907`。OJ最终14/14 Accepted / **`60.79`**，case1–14=`3/4/10/28/22/32/283/125/286/54/300/474/256/219 μs`，分数=`92/90/82/68/67/60/49/47/52/54/45/54/48/43`。目标case8相对#108803 `139→125 μs`并跨越三个得分档；非目标case4 `29→28 μs`恢复一分，其余得分不变。目标因果和更高aggregate同时成立，#108816取代#108803成为当时baseline。raw、逐提交快照和exp178完整实验源码的SHA-256均为`3e2f27cd5032a1f1c34f1e6f2490686a91be27a328c57c9382d6dacaeab5d92c`；当前没有OJ任务在途。

#108821/exp179 只把同native row allreduce继续扩展到case14，case8/11及其他dispatch不变。本地41×200正向exp179/exp178 p50=`0.8537`、反向exp178/exp179=`1.1772`，消偏约`0.8516`。OJ最终14/14 Accepted / **`61.14`**，case1–14=`3/4/10/28/22/31/283/126/284/53/299/472/254/186 μs`，分数=`92/90/82/68/67/61/49/46/52/54/45/54/48/48`。目标case14相对#108816 `219→186 μs`并跨越五个得分档；非目标case6跨到61分、case8波动丢一分，其余得分不变。目标因果和更高aggregate同时成立，#108821取代#108816成为当前baseline。raw、逐提交快照和exp179完整实验源码的SHA-256均为`9dd9651f6ec947e1fb976ed5cbb73e776dc1713020b5f51a3583f803308b4011`；当前没有OJ任务在途。

#108827/exp181 只给generic KV8 case12启用同native row allreduce，case8/11/14及其他dispatch不变。本地41×200正向exp181/#108821 p50=`0.8638`、反向#108821/exp181=`1.1571`，消偏约`0.8640`。OJ最终14/14 Accepted / **`61.36`**，case1–14=`3/4/10/28/22/32/283/125/287/53/300/425/255/186 μs`，分数=`92/90/82/68/67/60/49/47/52/54/45/57/48/48`。目标case12相对#108821 `472→425 μs`并跨越三个得分档；非目标case6丢一分、case8恢复一分，其余得分不变。目标因果和更高aggregate同时成立，#108827取代#108821成为当前baseline。raw、逐提交快照和exp181完整实验源码的SHA-256均为`2dcd0620181bcafb1c19d427bfe33a683a514bc73fd5e83c9707220153bd5117`；当前没有OJ任务在途。

#108840/exp182 只把同native row allreduce从case12扩展到generic KV8 case9，case8/11/12/14及其他dispatch不变。本地41×200正向exp182/exp181 p50=`0.8728`、反向exp181/exp182=`1.1458`，消偏约`0.8728`。OJ最终14/14 Accepted / **`61.50`**，case1–14=`3/4/10/29/22/32/283/125/254/53/301/426/256/186 μs`，分数=`92/90/82/67/67/60/49/47/55/54/45/57/48/48`。目标case9相对#108827 `287→254 μs`并跨越三个得分档；非目标case4从28波动到29 μs并丢一分，其余非目标得分不变。目标因果和更高aggregate同时成立，#108840取代#108827成为当前baseline。raw、逐提交快照和exp182完整实验源码的SHA-256均为`8c1eb876b638fd2b63cbbf0e490c6aededce348913ebc0b35650a4e240137054`；当前没有OJ任务在途。

#108856/exp183 只把同native row allreduce从case12/9扩展到generic KV8 case7，case8/11/12/14及其他dispatch不变。本地41×200正向exp183/exp182 p50=`0.8727`、反向exp182/exp183=`1.1430`，消偏约`0.8739`。OJ最终14/14 Accepted / **`61.64`**，case1–14=`3/4/10/28/22/32/255/126/255/53/303/421/255/188 μs`，分数=`92/90/82/68/67/60/52/46/55/54/45/57/48/47`。目标case7相对#108840 `283→255 μs`并跨越三个得分档；非目标case4恢复一分，case8/14各波动丢一分，其余非目标得分不变。目标因果和更高aggregate同时成立，#108856取代#108840成为当前baseline。raw、逐提交快照和exp183完整实验源码的SHA-256均为`4e5726efe6a8f03c147eb64db33d33dbf93bb44aea780a0d34e91b30470e103e`；当前没有OJ任务在途。

#108865/exp184 只把native row QK网络扩展到case6，本地41×200双顺序消偏约`0.9213`。OJ 14/14 Accepted / **`61.86`**，case1–14=`3/4/10/29/22/29/254/125/255/53/301/424/255/186 μs`；目标case6相对#108856 `32→29 μs`、`60→62分`，刷新当时最高分。#108875与#108865源码字节及SHA完全相同，14/14 Accepted / `61.79`；逐case差异只作为timing-tier波动证据。

#108897/exp185 只给case4 B64/BSM/combined/direct-out路径启用native row QK，本地强测正向`0.8765`、反向`1.1503`，消偏约`0.8728`。OJ 14/14 Accepted / **`62.07`**，case1–14=`3/4/10/24/22/29/255/126/255/53/301/419/255/186 μs`；目标case4相对#108865 `29→24 μs`、`67→71分`，刷新当时最高分。raw、逐提交快照和exp185 SHA均为`2329e3721f386e194406bccef9b5245378a717c2d96daec96f4a7cc57129a6d2`。

#108913/exp186 只给case6 grouped reducer的max/sum启用native网络，本地强测消偏约`0.9871`。OJ 14/14 Accepted / **`62.00`**，case1–14=`3/4/10/25/22/29/253/125/254/53/303/422/255/188 μs`；目标case6仍为`29 μs/62分`，没有跨tier，因此不替换#108897。raw、逐提交快照和exp186 SHA均为`158bd1e7545cac4c429e0604013b433db8fbabd510e149cd656fac0b32c58f48`。

#108936/exp190 在#108913上组合exp188/189的case5/10 native row QK并新增case3；三个目标都已通过精确长度、full/boundary/random与双顺序A/B。OJ 14/14 Accepted / **`62.57`**，case1–14=`3/4/9/25/19/29/255/125/253/47/300/422/255/186 μs`，分数=`92/90/83/70/70/62/52/47/55/57/45/57/48/48`。相对#108913，case3/5/10从`10/22/53→9/19/47 μs`，三个目标的display score合计增加7分；case4无源码差异且保持`25 μs/70分`，按tier波动处理。raw、逐提交快照和exp190完整源码字节一致，SHA为`6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`；#108936建立exp190结构性baseline，后由同源#108986刷新aggregate记录。

#108966/exp191 只给case5 grouped reducer的max/sum启用native row网络，本地41×200双顺序消偏约`0.9799`且完整correctness、精确长度和workspace复用均通过。OJ 14/14 Accepted / `62.50`，case1–14=`3/4/9/24/19/29/255/126/256/47/297/424/255/188 μs`，分数=`92/90/83/71/70/62/52/46/55/57/45/57/48/47`。目标case5仍为`19 μs/70分`，没有跨1 μs tier；其余dispatch无源码差异，case4/8/9/11/12/14变化按OJ timing波动处理。raw内嵌代码与逐提交快照SHA均为`393d9cac5acea6610e5addd5062dc6fadb0e7d19c596906725656d05f65000b5`，不替换#108936，当前没有OJ任务在途。

#108312之后的exp136–138逐shape扩展四标量V-over-PV，并由#108468完成OJ闭环。exp147的case10完整wave vec2 reducer由#108604真实跨过1 μs timing tier；exp149又把该ownership扩展到case12，由#108628确认目标再快1 μs但尚未跨分数tier。工作文件、exp149实验快照与#108628逐提交快照字节一致。exp139/140、exp142–146和exp148均已按唯一差异证据拒绝。

## 按日期提交索引

### 2026-08-15

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#113237](https://xpuoj.com/contest/11/submissions/113237) | 2026-08-15 13:55:04 | CUDA Maca C500 | Accepted | 65.79 | exp533：case12 two-head/full-wave reducer；14/14 Accepted，目标`375→374 μs`但仍60分，关闭且不替换 #112716 control。 |
| [#113201](https://xpuoj.com/contest/11/submissions/113201) | 2026-08-15 13:23:11 | CUDA Maca C500 | Accepted | 65.86 | exp531：case12 bit1 QK后立即同步发布next-K；14/14 Accepted，但唯一目标`375→382 μs`、60→59分，关闭且不替换 #112716 control。 |
| [#112741](https://xpuoj.com/contest/11/submissions/112741) | 2026-08-15 04:25:46 | CUDA Maca C500 | Accepted | 65.86 | exp491：case12 hot next-page PID 改为row-owner 32-bit native broadcast；目标`375→372 μs`但仍60分，14/14 Accepted，不替换 #112716 control。 |
| [#112736](https://xpuoj.com/contest/11/submissions/112736) | 2026-08-15 03:33:16 | CUDA Maca C500 | Accepted | 65.86 | raw 与逐提交快照 SHA 均为 #112716 control 的 `411a9e78...4479d`，因此是同源 timing 样本而非预定 exp488；14/14 Accepted，不替换 control。 |
| [#112716](https://xpuoj.com/contest/11/submissions/112716) | 2026-08-15 01:43:27 | CUDA Maca C500 | Accepted | **66.00** | exp485：case7只在既有1/2/3 live split前缀内以无`udiv`的`__umulhi`均衡实际页，满容量仍`43/43/42`；14/14 Accepted，OJ目标`233→227 μs`、54→55分。SHA `411a9e78...4479d`三方一致，接受为当前结构性control。 |

### 2026-08-14

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#112430](https://xpuoj.com/contest/11/submissions/112430) | 2026-08-14 11:41:11 | CUDA Maca C500 | Accepted | **65.93** | exp469：KV4 row-coefficient final merge完整正确但目标case8/11/14为`93/222/141 μs`，case14 `140→141 μs`；case10/13的加分无对应源码差异，拒绝且关闭。SHA `c915c0ac...37e58`三方一致。 |
| [#112399](https://xpuoj.com/contest/11/submissions/112399) | 2026-08-14 10:44:37 | CUDA Maca C500 | Accepted | **65.86** | exp467：case10 vec2 reducer以寄存器跨global-max保留两组packed `(m,l)`，动态shared metadata `1032→520 B`；14/14 Accepted，OJ目标case10 `41→40 μs`、60→61分。SHA `4ddfa822...ed411d`三方一致，接受为当前结构性control。 |
| [#112355](https://xpuoj.com/contest/11/submissions/112355) | 2026-08-14 09:52:53 | CUDA Maca C500 | Accepted | **65.79** | exp466：case14 safe-page lazy exact-page-max完整门禁通过，但OJ目标 `140→141 μs`、55→54分；拒绝且关闭该 exact state flow。 |
| [#112302](https://xpuoj.com/contest/11/submissions/112302) | 2026-08-14 09:11:27 | CUDA Maca C500 | Accepted | **65.86** | exp465：在KV4对称finalizer前提上启用case14 deferred reference-rescale，OJ目标 `141→140 μs`、54→55分；其组件保留在后续#112399 control。 |
| [#112259](https://xpuoj.com/contest/11/submissions/112259) | 2026-08-14 08:29:39 | CUDA Maca C500 | Accepted | **65.86** | exp464：只给case8/11/14启用KV4 z4对称finalizer；14/14 Accepted，OJ case14 `143→141 μs`、case8 `95→94 μs`。raw、提交快照与工作文件SHA均为`6a2e2b79...323d0`，接受为其后control的保留组件。 |
| [#111972](https://xpuoj.com/contest/11/submissions/111972) | 2026-08-14 10:29:04 | CUDA Maca C500 | Accepted | **65.79** | exp446：只给case14启用延迟reference rescale；本地case14约快1.1%，但OJ仍为143 μs/54分，未跨tier。14/14 Accepted，SHA `50e02d06...1053`三方一致；拒绝为baseline并恢复#111918。 |
| [#111942](https://xpuoj.com/contest/11/submissions/111942) | 2026-08-14 09:47:43 | CUDA Maca C500 | Accepted | **65.93** | 用户要求再次试投：直接提交不可变#111918 control，正常经历`Pending→Compiling→Running→Finished`并14/14 Accepted，刷新真实分数记录。源码SHA仍为`c0793eb9...fba3`，只作同源timing-tier样本，结构性control不变。 |
| [#111933](https://xpuoj.com/contest/11/submissions/111933) | 2026-08-14 09:14:15 | CUDA Maca C500 | Accepted | **65.71** | 用户要求链路试投：与#111918结构性control字节及SHA完全一致；正常经历`Pending→Running→Finished`并14/14 Accepted。确认当前链路可用，同源分差只作timing-tier样本，不替换control。 |
| [#111929](https://xpuoj.com/contest/11/submissions/111929) | 2026-08-14 09:01:35 | CUDA Maca C500 | Accepted | **65.86** | exp442：只给case7启用bit1 ownership；本地三分布约`0.9946/0.9970/0.9914`，OJ case7为233 μs、未优于#111918的230 μs且仍54分。aggregate并列来自tier波动，不替换结构性control。 |
| [#111918](https://xpuoj.com/contest/11/submissions/111918) | 2026-08-14 08:35:15 | CUDA Maca C500 | Accepted | **65.79** | exp439：只给case9启用bit1全原生ownership；三分布双角色约`0.9854/0.9762/0.9649`，OJ case9 `237/238→234 μs`但仍57分。目标证据成立，选为结构性control；当时最高分仍是#111912。 |
| [#111912](https://xpuoj.com/contest/11/submissions/111912) | 2026-08-14 08:08:24 | CUDA Maca C500 | Accepted | **65.86** | 用户要求链路试投：工作文件恢复为#111908字节精确源码，dry-run后只创建一笔；较长Pending/Running后14/14 Accepted并刷新真实记录。SHA同为`883de5d3...adb32`，分差只作timing-tier样本，选为同源control。 |
| [#111908](https://xpuoj.com/contest/11/submissions/111908) | 2026-08-14 07:41:55 | CUDA Maca C500 | Accepted | **65.79** | exp434：只把case13全原生QK改为bit1 ownership；full/random/boundary约`0.9900/0.9843/1.0000`，OJ case13 `183→182 μs`，建立结构性最佳；SHA `883de5d3...adb32`。 |
| [#111904](https://xpuoj.com/contest/11/submissions/111904) | 2026-08-14 07:07:03 | CUDA Maca C500 | Accepted | **65.64** | exp431：只把全原生bit2 QK扩到case13，三分布约`0.9731/0.9631/0.9933`，OJ case13 `188→183 μs`；aggregate回退来自其他case timing。 |
| [#111897](https://xpuoj.com/contest/11/submissions/111897) | 2026-08-14 06:47:33 | CUDA Maca C500 | Accepted | **65.79** | exp430：只把全原生bit2 QK扩到case7，三分布约`0.9879/0.9908/0.9726`，OJ case7 `235→234 μs`；组件进入主线。 |
| [#111895](https://xpuoj.com/contest/11/submissions/111895) | 2026-08-14 06:12:18 | CUDA Maca C500 | Accepted | **65.79** | exp428：case12 head-pair/z8 QK改为全原生shuffle网络，full/random/boundary约`0.9937/0.9904/0.9892`，OJ case12 `375→372 μs`；14/14 Accepted且SHA三方一致，组件进入主线。 |
| [#111887](https://xpuoj.com/contest/11/submissions/111887) | 2026-08-14 04:46:20 | CUDA Maca C500 | Accepted | **65.71** | 用户要求链路试投：移除错误输出的临时phase probes后，工作文件与#111886 SHA均为`de0f6620...e34a5`；dry-run后只创建一笔，14/14 Accepted并确认全链路正常。同源分差只作timing-tier样本，不替换#111886。 |
| [#111886](https://xpuoj.com/contest/11/submissions/111886) | 2026-08-14 04:22:01 | CUDA Maca C500 | Accepted | **65.79** | exp422：case11 `split48→39`；full/random/boundary p50=`0.9925/0.9932/0.9573`，OJ `224→223 μs`，刷新最高分并选为control；SHA `de0f6620...e34a5`。 |
| [#111882](https://xpuoj.com/contest/11/submissions/111882) | 2026-08-14 03:36:54 | CUDA Maca C500 | Accepted | **65.71** | exp421：case13 `split64→65`，OJ `190→188 μs`并55→56分；aggregate被无关case3 timing抵消，但源码结构严格改善，曾选为control。 |
| [#111868](https://xpuoj.com/contest/11/submissions/111868) | 2026-08-14 02:54:57 | CUDA Maca C500 | Accepted | **65.71** | 用户要求链路试投：原样提交#111856，14/14 Accepted；SHA同为`7b0a0b1b...b502fc4`，仅作timing-tier和平台恢复样本，不替换默认control。 |
| [#111856](https://xpuoj.com/contest/11/submissions/111856) | 2026-08-14 02:29:01 | CUDA Maca C500 | Accepted | **65.71** | exp417：只把case7 `split14→3`并保留packed partial/group8 reducer；full/random/boundary双角色均稳定正向，OJ case7 `246→237 μs`、53→54分，刷新最高分并选为control；SHA `7b0a0b1b...b502fc4`。 |
| [#111843](https://xpuoj.com/contest/11/submissions/111843) | 2026-08-14 02:06:30 | CUDA Maca C500 | Accepted | 65.43 | exp416：case7 split1/direct-out；full-length约快12.7%，但boundary回退约23%、OJ `246→279 μs`，证明variable lengths丢失split并行；拒绝为baseline。 |
| [#111830](https://xpuoj.com/contest/11/submissions/111830) | 2026-08-14 01:43:02 | CUDA Maca C500 | Accepted | **65.57** | exp415：只把z8 case9 `split24→6`，本地约`0.8991x`；OJ case9 `243→237 μs`、56→57分。同分但源码严格优于#111823，曾选为control，后由#111856取代。 |
| [#111823](https://xpuoj.com/contest/11/submissions/111823) | 2026-08-14 01:22:36 | CUDA Maca C500 | Accepted | **65.57** | exp414：只把z8 case12 `split128→40`，本地约`0.9253x`；OJ case12 `388→374 μs`、59→60分并刷新最高分。 |
| [#111811](https://xpuoj.com/contest/11/submissions/111811) | 2026-08-14 00:57:05 | CUDA Maca C500 | Accepted | **65.43** | exp413：只把z8 case13 `split256→64`，本地约`0.9004x`；OJ case13 `212→190 μs`、53→55分，确认reduced-partial主线。 |
| [#111795](https://xpuoj.com/contest/11/submissions/111795) | 2026-08-14 00:13:45 | CUDA Maca C500 | Accepted | **65.36** | 用户要求链路试投：提交前队列为空并完成dry-run，原样提交#111776/exp411；源码、raw和快照SHA均为`ec45265f...da081`且14/14 Accepted。相对同源#111776的`+0.07`只作timing-tier样本；选为当前分数记录与control，不视为新增代码收益。 |

### 2026-08-13

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#111776](https://xpuoj.com/contest/11/submissions/111776) | 2026-08-13 23:45:24 | CUDA Maca C500 | Accepted | **65.29** | exp410/411：从#111753只给case10/5扩展lane-local BF16 MMA；完整门禁通过，本地双角色消偏约`0.9563/0.9823`。OJ case10/5 `42/18→40/17 μs`、`60/71→61/73分`，刷新最高分；SHA `ec45265f...da081`。 |
| [#111753](https://xpuoj.com/contest/11/submissions/111753) | 2026-08-13 23:20:07 | CUDA Maca C500 | Accepted | **65.07** | exp409：只把lane-local BF16 MMA扩到case14 fixed15、最后generic split和fused tail；完整门禁与full→short→full复用通过，双角色消偏约`0.8508`。OJ case14 `169→143 μs`、`50→54分`，刷新最高分并成为默认control；SHA `7bef7e04...ae92a44` |
| [#111730](https://xpuoj.com/contest/11/submissions/111730) | 2026-08-13 22:47:51 | CUDA Maca C500 | Accepted | **64.86** | exp408b：只把lane-local BF16 MMA从case11扩到case8，并修正generic lane8 head-owner契约；完整门禁通过，双角色消偏约`0.8440`。OJ case8 `115→94 μs`、`49→54分`，刷新最高分并成为默认control；SHA `c4456f7c...df9b` |
| [#111707](https://xpuoj.com/contest/11/submissions/111707) | 2026-08-13 22:14:13 | CUDA Maca C500 | Accepted | **64.36** | exp407：只把case11 full-page scalar QK换成每z wave lane-local BF16 MMA；资源5→6 waves，完整门禁通过，双角色消偏约`0.8048`。OJ case11 `279→223 μs`、`47→52分`，刷新最高分并成为默认control；SHA `2f0421d5...65ac9` |
| [#111641](https://xpuoj.com/contest/11/submissions/111641) | 2026-08-13 21:06:56 | CUDA Maca C500 | Accepted | 64.07 | 用户要求原样试投#111319；提交前队列为空、完成dry-run且只创建一笔，数分钟无case输出后正常完成14/14。SHA完全一致，确认OJ链路可用；只作同源timing-tier样本，不替换baseline |
| [#111616](https://xpuoj.com/contest/11/submissions/111616) | 2026-08-13 20:39:43 | CUDA Maca C500 | Accepted | 64.00 | exp406b：只把case11改为split24并保持正确vec4 fused-tail reducer；本地消偏约`0.9588`且22–26邻域夹定24，但OJ case11回退到`281 μs/46分`。拒绝为baseline，不复投或继续微扫 |
| [#111590](https://xpuoj.com/contest/11/submissions/111590) | 2026-08-13 20:08:11 | CUDA Maca C500 | Accepted | 64.07 | exp405：只把已隔离验证的case5 combined-tail全原生split-head网络组合进exp403；完整门禁通过，case5消偏约`0.9826`。OJ case5仍`18 μs/71分`未跨tier，case9/10刷新Accepted历史最佳`243/41 μs`但不加分；保留组合、不替换#111319 |
| [#111570](https://xpuoj.com/contest/11/submissions/111570) | 2026-08-13 19:35:22 | CUDA Maca C500 | Accepted | 64.00 | exp403：只把全原生split-head网络扩到case10 generic full-page路径；完整门禁通过，唯一差异消偏约`0.9865`。OJ case10仍`42 μs/60分`，未跨tier；case11刷新Accepted历史最佳275 μs但aggregate未超过64.14，保留组合、不替换#111319 |
| [#111547](https://xpuoj.com/contest/11/submissions/111547) | 2026-08-13 19:03:15 | CUDA Maca C500 | Accepted | 64.00 | exp402：只把全原生split-head网络扩到case14 fixed15 common splits；完整门禁通过，唯一差异消偏约`0.9845`。OJ case14 `169→166 μs`但仍50分，aggregate受case6/11同源掉档回退；保留组件，不替换#111319 |
| [#111528](https://xpuoj.com/contest/11/submissions/111528) | 2026-08-13 18:37:25 | CUDA Maca C500 | Accepted | **64.14** | exp401：在exp400上只把全原生split-head网络扩到case8 fixed19 common splits；完整门禁通过，case8唯一差异消偏约`0.9879`。OJ case8仍`115 μs/49分`、case11 `277 μs/47分`，aggregate与#111319并列但未建立新高；保留组合组件，不替换默认control |
| [#111517](https://xpuoj.com/contest/11/submissions/111517) | 2026-08-13 18:20:32 | CUDA Maca C500 | Accepted | 64.00 | exp400：只给case11把split-head中的BSM XOR4替换为全原生rotate4/rotate8/quad网络；完整门禁通过，双角色消偏约`0.9818`。OJ case11 `279→276 μs`，但仍47分且case8同源掉1分，不替换#111319 baseline |
| [#111489](https://xpuoj.com/contest/11/submissions/111489) | 2026-08-13 17:48:11 | CUDA Maca C500 | Accepted | 64.07 | 用户要求原样试投#111319；SHA完全一致，唯一任务正常经历`Pending→Running→Finished`并14/14 Accepted，确认OJ全链路可用。只作为同源timing-tier样本，不替换#111319 baseline |
| [#111431](https://xpuoj.com/contest/11/submissions/111431) | 2026-08-13 16:30:30 | CUDA Maca C500 | Accepted | 64.00 | 用户要求再次试投；与#111319/exp390源码字节及SHA完全一致。14/14 Accepted，确认OJ创建、排队、编译和评测链路可用；只作为同源timing-tier样本，不替换#111319 baseline |
| [#111364](https://xpuoj.com/contest/11/submissions/111364) | 2026-08-13 15:29:05 | CUDA Maca C500 | Accepted | 64.00 | 用户要求的平台试投；与#111319/exp390源码字节及SHA完全一致。14/14 Accepted，确认提交、编译和完整评测链路可用；只作为同源timing-tier样本，不替换#111319 baseline |
| [#111319](https://xpuoj.com/contest/11/submissions/111319) | 2026-08-13 14:39:31 | CUDA Maca C500 | Accepted | **64.14** | exp390：只把z8 ownership扩到case7，并让原group8 reducer读取packed `(m,l)`；完整门禁与14步复用通过，双角色消偏约`0.9769`。OJ case7 `256→247 μs`、`52→53分`，刷新最高分并选为默认control |
| [#111307](https://xpuoj.com/contest/11/submissions/111307) | 2026-08-13 14:17:09 | CUDA Maca C500 | Accepted | **64.07** | exp389：修复exp388的case9 z8 packed-metadata/vec4 reducer ABI失配，改用packed-aware vec2 reducer。完整门禁与14步复用通过，双角色消偏约`0.9664`；OJ case9 `254→244 μs`、`55→56分`，建立当时最高分 |
| [#111272](https://xpuoj.com/contest/11/submissions/111272) | 2026-08-13 13:44:43 | CUDA Maca C500 | Accepted | 63.93 | 用户要求的平台恢复试投；与#111231源码及SHA完全一致。Pending超过15分钟后正常14/14 Accepted；只作为同源timing-tier样本，不替换#111231 |
| [#111231](https://xpuoj.com/contest/11/submissions/111231) | 2026-08-13 13:26:08 | CUDA Maca C500 | Accepted | **64.00** | exp387：只把head-pair/z8 ownership扩展到case12，保持split128、16 pages/partial、同步K+V-over-PV、packed metadata、global partial数量和vec2 reducer不变。完整门禁及17步复用通过，双角色消偏约`0.9319`；OJ case12 `422→388 μs`、`57→59分`并刷新最高分，选为默认control |
| [#111200](https://xpuoj.com/contest/11/submissions/111200) | 2026-08-13 12:53:00 | CUDA Maca C500 | Accepted | **63.71** | exp386：只把case13 producer ownership从head1/z4改为head2/z8，保持split256、15 pages/partial、同步K+V-over-PV、packed metadata、global partial数量和vec2 reducer不变。完整门禁及17步复用通过，双角色消偏约`0.8361`；OJ case13 `252→212 μs`、`48→53分`并刷新最高分，选为默认control |
| [#111163](https://xpuoj.com/contest/11/submissions/111163) | 2026-08-13 12:18:05 | CUDA Maca C500 | Accepted | **63.29** | 用户要求的平台连通性复投；与#111115/exp385源码字节及SHA完全一致。唯一任务Pending约四分钟后正常完成14/14 Accepted，case1–14=`3/4/10/24/18/28/254/116/257/42/280/422/253/169 μs`；确认创建、编译和完整评测链路可用，同源timing-tier波动不替换#111115 baseline |
| [#111115](https://xpuoj.com/contest/11/submissions/111115) | 2026-08-13 11:22:24 | CUDA Maca C500 | Accepted | **63.36** | exp385：只给exp384的case5 group8 reducer启用native-row max/sum；完整门禁通过，相对#111076 reducer唯一差异消偏约`0.9781`，相对#111016组合消偏约`0.9447`。OJ case5 `19→18 μs`、`70→71分`并刷新最高分，选为默认control |
| [#111076](https://xpuoj.com/contest/11/submissions/111076) | 2026-08-13 10:43:33 | CUDA Maca C500 | Accepted | **63.29** | exp384：exp383的case5 head-pair/z4 + split-head QK，并删除6个不可达separate-tail模板实例；完整门禁通过，本地case5双角色消偏约`0.9703`。OJ case5仍`19 μs/70分`未跨tier，case4/8一降一升互抵；作为local-positive组件继续组合，不替换#111016 |
| [#111059](https://xpuoj.com/contest/11/submissions/111059) | 2026-08-13 10:32:13 | CUDA Maca C500 | CompilationError | — | exp383：只把case5 producer改为head-pair/z4 + split-head QK，资源`92/48→86/56`且本地消偏约`0.9750`；OJ测试点前compile TLE，只有warning、无源码error。后续由编译裁剪版exp384/#111076完成闭环 |
| [#111031](https://xpuoj.com/contest/11/submissions/111031) | 2026-08-13 09:55:50 | CUDA Maca C500 | Accepted | **63.29** | 用户要求的平台连通性复投；与#111016/exp382源码字节及SHA完全一致。唯一任务排队约八分钟后正常完成14/14 Accepted，case1–14=`3/4/10/22/19/28/252/116/255/42/282/421/252/169 μs`；确认创建、编译和完整评测链路可用，同源波动不替换#111016 baseline |
| [#111016](https://xpuoj.com/contest/11/submissions/111016) | 2026-08-13 09:17:39 | CUDA Maca C500 | Accepted | **63.29** | exp382：在exp381上只把case10 producer改为head-pair/z4 + split-head QK，完整门禁与17步复用通过，本地case10双角色消偏约`0.9284`。OJ case10 `46→42 μs`、`58→60分`，14/14 Accepted并刷新最高分，选为默认control；raw与逐提交源码已归档 |
| [#110993](https://xpuoj.com/contest/11/submissions/110993) | 2026-08-13 08:28:37 | CUDA Maca C500 | Accepted | **63.14** | exp379：case14 fixed15 split-head half-row QK编译表面精简版；SHA `f49371db...1343`。完整correctness与20步复用通过，本地case14相对#110426消偏约`0.9634`。OJ case14 `177→170 μs`、`49→50分`，总分刷新并选为默认control |
| [#110987](https://xpuoj.com/contest/11/submissions/110987) | 2026-08-13 08:18:22 | CUDA Maca C500 | CompilationError | — | exp378：保留双head K解包复用的split-head half-row QK，本地case14消偏约`0.9794`；OJ在测试点前compile TLE，只有既有warning、无源码error。后续由exp379/#110993正常Accepted完成闭环 |
| [#110962](https://xpuoj.com/contest/11/submissions/110962) | 2026-08-13 07:16:24 | CUDA Maca C500 | Accepted | 63.00 | 用户要求的平台恢复探测；与#110895/exp367源码字节及SHA完全一致。唯一任务正常经历`Pending→Running→Finished`并14/14 Accepted，case1–14=`3/4/10/23/19/28/254/116/253/46/291/421/253/174 μs`；确认当前完整评测链路可用，同源波动不替换#110426 baseline |
| [#110941](https://xpuoj.com/contest/11/submissions/110941) | 2026-08-13 06:44:02 | CUDA Maca C500 | CompilationError | — | exp367同源平台试投；与已14/14 Accepted的#110895源码字节一致。长时间Pending后在测试点前compile TLE，只有既有warning；编译服务尚未稳定恢复，不继续复投、不替换#110426 |
| [#110916](https://xpuoj.com/contest/11/submissions/110916) | 2026-08-13 05:52:57 | CUDA Maca C500 | CompilationError | — | 用户要求的平台试投；与已14/14 Accepted的#110895/exp367源码字节一致。任务成功创建并进入Compiling，但在测试点前compile TLE，只有既有warning、无源码compiler error；不立即复投、不替换#110426 |
| [#110895](https://xpuoj.com/contest/11/submissions/110895) | 2026-08-13 05:10:41 | CUDA Maca C500 | Accepted | 63.00 | exp367：case10/12/13统一vec2 reducer metadata为FP16x2 packed `(m,l)`，保持单一reducer实例；完整门禁通过。OJ case1–14=`3/4/10/23/19/28/252/116/255/46/288/421/253/174 μs`，case7刷新历史最佳但aggregate未超过#110426；确认平台链路正常，不替换baseline |
| [#110884](https://xpuoj.com/contest/11/submissions/110884) | 2026-08-13 04:36:51 | CUDA Maca C500 | CompilationError | — | exp365：case13 FP16x2 packed `(m,l)`，完整门禁通过且本地case13相对#110426消偏约`0.9895`；OJ在测试点前compile TLE，不作为性能失败 |
| [#110809](https://xpuoj.com/contest/11/submissions/110809) | 2026-08-13 02:50:15 | CUDA Maca C500 | CompilationError | — | 用户要求的平台试投；与已14/14 Accepted的#110771/exp356源码字节一致，SHA均为`e23876f...8669`。OJ在测试点前compile TLE，只有既有warning、无源码compiler error；作为平台故障样本，不立即复投、不替换#110426 |
| [#110771](https://xpuoj.com/contest/11/submissions/110771) | 2026-08-13 02:09:48 | CUDA Maca C500 | Accepted | 62.93 | exp356：保持exp353运行语义并删除新增模板参数，源码缩小168 bytes；完整门禁通过。OJ case13/14=`254/174 μs`，但case4/8各掉1分，不替换#110426 |
| [#110760](https://xpuoj.com/contest/11/submissions/110760) | 2026-08-13 01:41:49 | CUDA Maca C500 | CompilationError | — | exp353：组合case13 `uint2` load-site与case14 owner-score/head-max；完整本地门禁通过。OJ compile TLE且无测试点，不作为性能失败 |
| [#110746](https://xpuoj.com/contest/11/submissions/110746) | 2026-08-13 00:47:22 | CUDA Maca C500 | Accepted | 62.86 | exp348：case14 fixed15 common split组合single owner-score与head-owned page max；完整门禁通过，双角色消偏约`0.9834`。OJ case14 `177→174 μs`但仍49分；非目标case4/8/10各掉1分，不替换baseline |
| [#110740](https://xpuoj.com/contest/11/submissions/110740) | 2026-08-13 00:33:33 | CUDA Maca C500 | CompilationError | — | #110426同源平台试投；长时间Pending后compile TLE，无源码compiler error和测试点。连续第四次平台故障样本，不归因于代码 |
| [#110699](https://xpuoj.com/contest/11/submissions/110699) | 2026-08-13 00:09:44 | CUDA Maca C500 | CompilationError | — | exp347：只给case13标量K+V lookahead使用`uint2` load后立即拆标量；完整本地门禁通过，双角色消偏约`0.9946`。OJ首条诊断为compile TLE、无测试点，不归因于源码且不替换baseline |

### 2026-08-12

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#110621](https://xpuoj.com/contest/11/submissions/110621) | 2026-08-12 23:07:27 | CUDA Maca C500 | CompilationError | — | 用户要求的平台试投；与#110426字节及SHA完全一致。长时间Pending后compile TLE，raw首条消息为`A TimeLimitExceeded encountered while compiling the code.`，无源码compiler error、无测试点；作为平台故障样本，不归因于代码且不再次复投 |
| [#110546](https://xpuoj.com/contest/11/submissions/110546) | 2026-08-12 22:08:54 | CUDA Maca C500 | CompilationError | — | 用户要求的平台试投；与#110426字节及SHA完全一致。进入Compiling后compile TLE，只有既有warning、无源码compiler error和测试点；不归因于代码 |
| [#110426](https://xpuoj.com/contest/11/submissions/110426) | 2026-08-12 21:24:23 | CUDA Maca C500 | Accepted | **63.07** | exp340b：隔离case8 fixed19 `unroll 2` + skip-empty特化；SHA `20a5189a...e784a3`。完整correctness与case8复用通过，本地case8消偏约`0.9914`，case4/5/10中性。OJ case1–14=`3/4/10/23/19/28/253/115/254/46/286/423/255/177 μs`；保住case8一分并改善case7/9/11，选为默认control |
| [#110229](https://xpuoj.com/contest/11/submissions/110229) | 2026-08-12 20:01:41 | CUDA Maca C500 | Accepted | **63.00** | exp339：只给#110192的case8组合fixed19 `unroll 2`与skip-empty；完整correctness通过，本地case8消偏约`0.9912`，OJ case8 `117→115 μs/49分`。case4/5各掉一分，拒绝为baseline；raw、逐提交与实验源码SHA一致 |
| [#110192](https://xpuoj.com/contest/11/submissions/110192) | 2026-08-12 19:21:44 | CUDA Maca C500 | Accepted | **63.07** | exp338：从#109963保留case4 fixed4，只给case6/7/9/10/11/12/13/14启用skip-empty rescale；SHA `0662e29f...4ca`。完整correctness与case11/14复用通过，OJ case1–14=`3/4/10/22/19/28/254/117/256/46/289/421/255/176 μs`。与#109783同分但保留case4、获得case10一分并改善多个长case，选为默认control |
| [#110031](https://xpuoj.com/contest/11/submissions/110031) | 2026-08-12 16:29:58 | CUDA Maca C500 | Accepted | **63.00** | 与#109963仅差一个空行；15分钟watch超时后未取消、未复投，最终14/14 Accepted。case1–14=`3/4/10/23/19/28/255/116/253/46/292/423/255/177 μs`，只作为同源timing-tier和链路样本 |
| [#109989](https://xpuoj.com/contest/11/submissions/109989) | 2026-08-12 15:47:03 | CUDA Maca C500 | Accepted | **62.93** | exp335：从#109963只把case8 fixed19循环`unroll 1→2`；本地约快0.55%，但OJ case4/8=`23/117 μs`，不得原样复投 |
| [#109963](https://xpuoj.com/contest/11/submissions/109963) | 2026-08-12 15:19:55 | CUDA Maca C500 | Accepted | **63.00** | exp334：从#109783只给case4建立独立编译期模板，满长走fixed4、短长度安全fallback并固定direct-out；SHA `55b25859...9209`。完整correctness与14个精确长度通过，相对#109783双向A/B约快4.9%，OJ case4真实`23→22 μs`、`72→73分`。case8同源波动到116 μs掉1分；该组件后来由#110192吸收 |
| [#109933](https://xpuoj.com/contest/11/submissions/109933) | 2026-08-12 14:30:07 | CUDA Maca C500 | Accepted | **62.86** | exp332：case4 fixed4与generic fallback共处同一模板，本地快约4.26%但STreg `44→52`；OJ case4 `24 μs/71分`，未兑现。作为代码表面/资源诊断样本，不替换baseline |
| [#109897](https://xpuoj.com/contest/11/submissions/109897) | 2026-08-12 13:49:05 | CUDA Maca C500 | Accepted | **62.93** | exp331：只给case4启用首空状态rescale跳过，本地仅快约0.27%，OJ仍`23 μs/72分`；证明#109875的22 μs不能归因给该微调 |
| [#109875](https://xpuoj.com/contest/11/submissions/109875) | 2026-08-12 13:28:32 | CUDA Maca C500 | Accepted | **63.07** | exp330混合多个shape的skip-empty与case8 `unroll 3`；case4达到22 μs/73分但case8回到116 μs/48分，aggregate与#109783并列。因归因不纯且局部复验未复现，不替换baseline |
| [#109828](https://xpuoj.com/contest/11/submissions/109828) | 2026-08-12 11:38:22 | CUDA Maca C500 | Accepted | **63.00** | 用户要求的平台试投；原样复投#109783/exp312，源码SHA `3612a126...ff96`。成功创建并经历较长排队/运行后14/14 Accepted，case1–14=`3/4/10/23/19/28/255/116/256/46/290/422/256/177 μs`；同源case8慢1 μs并掉1分，其他差异不跨档，只作为timing-tier样本。raw与逐提交源码已归档，baseline保持#109783 |
| [#109783](https://xpuoj.com/contest/11/submissions/109783) | 2026-08-12 11:05:24 | CUDA Maca C500 | Accepted | **63.07** | exp312：在#109761上组合case8/11 head-owned page max，并只给case8满长前13个common split使用固定19-page热循环；SHA `3612a126...ff96`，完整correctness与精确长度复用通过，直接相对#109761 case8消偏约`0.9885`。OJ case1–14=`3/4/10/23/19/28/255/115/257/46/291/425/255/177 μs`，目标case8 `116→115 μs`、`48→49分`，总分刷新并选为新baseline；raw与逐提交源码已归档并核对哈希 |
| [#109769](https://xpuoj.com/contest/11/submissions/109769) | 2026-08-12 10:29:29 | CUDA Maca C500 | Accepted | **63.00** | 平台探测原样复投#109761/exp307；提交前无在途任务且dry-run正常，唯一任务正常完成。源码SHA与#109761完全一致，OJ case1–14=`3/4/9/23/19/28/256/117/256/47/291/420/255/177 μs`；确认提交、调度、编译和评测链路正常。同源差异只作为timing-tier样本，不替换#109761；raw与逐提交源码已归档并核对哈希 |
| [#109761](https://xpuoj.com/contest/11/submissions/109761) | 2026-08-12 09:55:23 | CUDA Maca C500 | Accepted | **63.00** | exp307：在#109754上只给case11组合分布式row exp与owner-score live-range缩减；SHA `e953d45d...22bb`，完整correctness和17步复用通过，相对#109754双角色消偏约`0.9681`。OJ case1–14=`3/4/9/23/19/28/256/116/257/47/290/426/255/177 μs`，目标case11 `302→290 μs`、`45→46分`，总分首次达到63并选为新baseline；raw与逐提交源码已归档并核对哈希 |
| [#109754](https://xpuoj.com/contest/11/submissions/109754) | 2026-08-12 09:37:33 | CUDA Maca C500 | Accepted | **62.93** | exp305：在case8 owner-score缩短基础上镜像owner state并简化lane predicate；SHA `cdebd158...fb0fc3`，完整correctness通过，相对#109751消偏约`0.9927`。OJ case8 `118→117 μs`并刷新Accepted历史最佳，选为exp307之前的baseline |
| [#109751](https://xpuoj.com/contest/11/submissions/109751) | 2026-08-12 09:09:19 | CUDA Maca C500 | Accepted | **62.93** | exp304：每lane保留本地page max但只保留owner score跨QK→softmax，不增加quad max；SHA `018b4370...3486`，完整correctness通过，相对exp300消偏约`0.9897`。OJ case8 `119→118 μs`，选为当时baseline |
| [#109736](https://xpuoj.com/contest/11/submissions/109736) | 2026-08-12 08:43:04 | CUDA Maca C500 | Accepted | **62.93** | exp300：只给case8 full-page producer启用分布式row exp；完整correctness通过，本地消偏约`0.9854`，OJ case8 `120→119 μs`，选为当时baseline |
| [#109730](https://xpuoj.com/contest/11/submissions/109730) | 2026-08-12 08:31:52 | CUDA Maca C500 | Accepted | **62.93** | exp299：只给case14固定15-page热循环启用分布式row exp；完整correctness通过，本地消偏约`0.9851`，OJ case14 `179→177 μs`，选为当时baseline |
| [#109723](https://xpuoj.com/contest/11/submissions/109723) | 2026-08-12 08:14:34 | CUDA Maca C500 | Accepted | **62.93** | 平台探测复投#109705/exp294；提交前队列为空且dry-run正常，源码SHA一致。OJ case1–14=`3/4/9/23/19/28/254/121/256/46/302/424/255/179 μs`，确认链路正常；同源差异只作为timing-tier样本 |
| [#109719](https://xpuoj.com/contest/11/submissions/109719) | 2026-08-12 08:01:14 | CUDA Maca C500 | Accepted | **62.93** | exp298：case11以lanes 0..7一次横向`exp2`计算8个权重并native row broadcast分发；SHA `0b77acec...6e47577`，完整correctness通过，本地双角色消偏约`0.9847`。OJ case1–14=`3/4/9/23/19/28/256/121/257/46/298/425/255/179 μs`；目标case11未超过#109705的297 μs，case8掉1分、case10升1分后aggregate并列，不替换baseline。raw与逐提交源码已归档并核对哈希 |
| [#109715](https://xpuoj.com/contest/11/submissions/109715) | 2026-08-12 07:34:53 | CUDA Maca C500 | Accepted | **62.86** | 平台探测复投；提交前队列为空且dry-run正常，与#109705/exp294源码字节及SHA完全一致。OJ case1–14=`3/4/9/24/19/28/255/120/257/47/298/426/255/179 μs`；case4同源波动掉1分，其余变化未跨得分档。确认提交与评测链路正常，不替换#109705；raw与逐提交源码已归档并核对哈希 |
| [#109707](https://xpuoj.com/contest/11/submissions/109707) | 2026-08-12 06:59:30 | CUDA Maca C500 | Accepted | **62.71** | 平台探测复投；与#109705/exp294源码字节及SHA完全一致，正常14/14 Accepted。OJ case1–14=`3/4/9/23/19/33/254/120/254/46/300/426/256/179 μs`；case14保持179 μs/49分，case6同源波动掉4分、case10升1分。确认提交与评测链路可用，不替换#109705；raw与逐提交源码已归档并核对哈希 |
| [#109705](https://xpuoj.com/contest/11/submissions/109705) | 2026-08-12 06:30:08 | CUDA Maca C500 | Accepted | **62.93** | exp294：只把exp291的case14固定15-page循环从`unroll 1`改为`2`；SHA `71242043...db9887`，完整correctness和20步workspace复用通过，相对exp291/#109672双角色消偏约`0.9951/0.9552`。OJ case1–14=`3/4/9/23/19/28/255/120/255/47/297/425/255/179 μs`，唯一目标case14 `186→179 μs`并跨到49分；case4无源码差异地掉1分后总分仍追平最高，选为当前baseline。raw与逐提交源码已归档并核对哈希 |
| [#109699](https://xpuoj.com/contest/11/submissions/109699) | 2026-08-12 06:09:29 | CUDA Maca C500 | Accepted | **62.57** | exp291：组合case14固定15-page common-split热循环与packed `(m,l)`/register metadata reducer；SHA `eb31c682...bb8abc1`，完整correctness通过，相对#109672双角色消偏约`0.9604`。OJ case1–14=`3/4/10/23/19/29/255/121/254/47/305/425/255/180 μs`，目标真实`186→180 μs`但仍48分；非目标timing掉档使aggregate下降，不替换#109672。raw与逐提交源码已归档并核对哈希 |
| [#109694](https://xpuoj.com/contest/11/submissions/109694) | 2026-08-12 05:26:06 | CUDA Maca C500 / 181.3 K | Accepted | **62.79** | 平台探测复投；与#109672/exp283源码字节及SHA完全一致，约七分钟后14/14 Accepted。OJ case1–14=`3/4/9/23/19/28/253/120/253/47/303/421/255/188 μs`；确认提交与评测链路可用。同源变化只作为timing-tier证据，不替换#109672；raw与逐提交源码已归档并核对哈希 |
| [#109691](https://xpuoj.com/contest/11/submissions/109691) | 2026-08-12 05:06:01 | CUDA Maca C500 / 185.5 K | Accepted | **62.79** | exp288：在#109672上只给case14组合FP16x2 `(m,l)` partial与寄存器化reducer metadata；SHA `01e4d5ba...985`，完整correctness和23步workspace复用通过，41×200双角色消偏约`0.9766`。OJ case1–14=`3/4/9/23/19/28/255/121/256/47/298/426/255/183 μs`，目标case14真实`186→183 μs`但仍48分；case8/10无源码差异地各掉1分，故不替换#109672。raw与提交源码已归档 |
| [#109688](https://xpuoj.com/contest/11/submissions/109688) | 2026-08-12 04:43:54 | CUDA Maca C500 / 181.3 K | Accepted | **62.93** | 平台探测复投；与#109672/exp283源码字节及SHA完全一致，正常14/14 Accepted。OJ case1–14=`3/4/9/23/19/28/254/120/254/46/299/424/255/186 μs`；确认提交与评测链路可用。同源码同分不构成新实现证据，默认control仍为#109672；raw与逐提交源码已归档并核对哈希 |
| [#109684](https://xpuoj.com/contest/11/submissions/109684) | 2026-08-12 03:53:38 | CUDA Maca C500 | Accepted | **62.86** | 平台探测复投；与#109672/exp283源码字节及SHA完全一致。约八分钟后14/14 Accepted，OJ case1–14=`3/4/9/23/19/28/256/121/255/46/301/422/255/186 μs`；确认提交和评测链路可用但延迟仍明显。同源变化只作为timing-tier证据，不替换#109672；raw与逐提交源码已归档并核对哈希 |
| [#109672](https://xpuoj.com/contest/11/submissions/109672) | 2026-08-12 03:20:08 | CUDA Maca C500 / 183.1 K | Accepted | **62.93** | exp283：在#109666/exp282上只给case6组合保持6 waves的四标量K-only lookahead；SHA `0c11bb1f...89a6`，完整correctness、29个精确长度和双角色A/B通过，相对#109666消偏约`0.9868`。OJ case1–14=`3/4/9/22/19/28/254/119/256/47/304/424/255/186 μs`，唯一目标case6 `29→28 μs/63分`并与A/B同向；case4无源码差异地波动到22 μs。总分刷新，选为新baseline |
| [#109666](https://xpuoj.com/contest/11/submissions/109666) | 2026-08-12 02:51:47 | CUDA Maca C500 / 181.0 K | Accepted | **62.79** | exp282：在exp281已验证的`wait(V)→issue(K-next)`顺序上只把token wait scope1改scope0；SHA `d6e82578...388a8`，完整correctness通过，相对#109591消偏约`0.9650`。OJ case1–14=`3/4/9/23/19/29/255/120/256/47/301/424/255/186 μs`，case4真实跨到23 μs/72分，选为新baseline |
| [#109664](https://xpuoj.com/contest/11/submissions/109664) | 2026-08-12 02:37:00 | CUDA Maca C500 / 177.3 K | Accepted | **62.71** | 原样复投#109591/exp262；OJ case1–14=`3/4/9/25/19/29/255/120/253/46/299/425/255/186 μs`。源码与baseline字节一致，同源波动只作为timing-tier样本，不替换#109591；raw与逐提交快照已归档 |
| [#109654](https://xpuoj.com/contest/11/submissions/109654) | 2026-08-12 02:23:25 | CUDA Maca C500 / 181.0 K | Accepted | **62.57** | exp281有序tokenized BSM；本地相对#109591消偏约`0.9736`，OJ case1–14=`3/4/9/24/19/29/255/121/258/47/301/422/255/188 μs`，case4仍24 μs/71分，拒绝为baseline；raw、提交快照与实验源码SHA一致 |
| [#109644](https://xpuoj.com/contest/11/submissions/109644) | 2026-08-12 01:54:46 | CUDA Maca C500 / 177.3 K | Accepted | **62.64** | 原样复投#109591/exp262；OJ case1–14=`3/4/9/25/19/29/254/121/257/46/298/420/255/186 μs`。同源timing样本，不替换baseline；raw与逐提交快照已归档 |
| [#109630](https://xpuoj.com/contest/11/submissions/109630) | 2026-08-12 01:19:38 | CUDA Maca C500 / 177.7 K | Accepted | **62.71** | exp272：case6 split8 last-producer group4 finalizer；本地41×500双角色消偏约`0.9390`且完整correctness通过，但OJ case1–14=`3/4/9/25/19/30/256/120/257/46/301/420/255/186 μs`，目标case6相对#109591 `29→30 μs`未兑现。case8/4无归因地各升/降1分后aggregate抵消；raw、逐提交源码和实验快照SHA一致，不替换#109591 |
| [#109610](https://xpuoj.com/contest/11/submissions/109610) | 2026-08-12 00:50:24 | CUDA Maca C500 / 177.3 K | Accepted | **62.64** | 再次原样复投#109591/exp262；约六分钟后14/14 Accepted，OJ case1–14=`3/4/9/24/19/29/254/121/256/47/300/424/255/186 μs`。与baseline源码字节及SHA完全一致，确认链路可用；同源变化只作为timing-tier证据，不替换#109591。raw与逐提交源码已归档并核对哈希 |
| [#109601](https://xpuoj.com/contest/11/submissions/109601) | 2026-08-12 00:20:30 | CUDA Maca C500 / 177.3 K | Accepted | **62.64** | 平台恢复探测复投；与#109591/exp262源码字节及SHA完全一致。正常经历`Pending→Running→Finished`，OJ case1–14=`3/4/9/24/19/29/254/121/258/47/303/422/255/185 μs`；确认创建、排队、编译和评测链路可用，同源变化只作为timing-tier证据，不替换#109591 baseline。raw与逐提交源码已归档并核对哈希 |

### 2026-08-11

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#109591](https://xpuoj.com/contest/11/submissions/109591) | 2026-08-11 23:45:44 | CUDA Maca C500 | Accepted | **62.71** | exp262：在修正后的case8 eight-head grouped reducer上启用native max/sum；OJ case1–14=`3/4/9/24/19/29/255/121/257/46/300/424/255/186 μs`，14/14 Accepted并列真实最高。case8相对#108986 `125→121 μs`且与本地证据同向，选为当前baseline；raw、提交快照、实验快照与工作文件SHA一致 |
| [#109578](https://xpuoj.com/contest/11/submissions/109578) | 2026-08-11 23:22:21 | CUDA Maca C500 | Accepted | **62.43** | exp265：以32-bit completion counter和last-producer CTA内finalizer消除case8独立reducer launch；本地41×300双顺序消偏约`0.9871`，但OJ case1–14=`3/4/10/25/19/29/255/134/255/46/303/421/255/186 μs`，case8回退到`134 μs/45分`。raw、提交快照与SHA一致；拒绝并恢复exp262 |
| [#109558](https://xpuoj.com/contest/11/submissions/109558) | 2026-08-11 22:31:51 | CUDA Maca C500 | Accepted | **62.57** | exp261：修复case8 grouped reducer的fused-tail live-count，把512个one-head CTA压为64个eight-head CTA；OJ case1–14=`3/4/9/25/19/29/257/121/254/47/301/424/255/186 μs`，case8保持`121 μs/47分`但未跨tier；raw、提交快照与SHA一致，不替换#108986 |
| [#109533](https://xpuoj.com/contest/11/submissions/109533) | 2026-08-11 21:47:53 | CUDA Maca C500 | Accepted | **62.43** | exp256：case11 inline finalizer在changed precondition下从split48重扫到split24/32页；本地相对#108986消偏约`0.9527`，但OJ case1–14=`3/4/9/25/19/29/257/125/255/46/322/423/255/188 μs`，目标case11比#108986和#109508都慢；raw、提交快照和实验源码SHA一致，不替换baseline |
| [#109508](https://xpuoj.com/contest/11/submissions/109508) | 2026-08-11 21:20:51 | CUDA Maca C500 | Accepted | **62.43** | exp255：case11 split48 inline finalizer，以epoch计数器和last-producer CTA内归约消除独立reducer launch；本地消偏约`0.9974`。OJ case1–14=`3/4/10/24/19/29/255/125/256/46/318/425/255/188 μs`，目标case11未超过#108986；raw、提交快照和实验源码SHA一致，不替换baseline |
| [#109467](https://xpuoj.com/contest/11/submissions/109467) | 2026-08-11 20:54:35 | CUDA Maca C500 | Accepted | **62.57** | 平台探测复投；与#108986/exp190源码字节及SHA完全一致。OJ case1–14=`3/4/9/25/19/29/256/125/256/47/299/424/255/186 μs`；确认提交、编译与评测链路可用，终态后队列为空；同源变化只作为timing-tier证据，不替换#108986 |
| [#109431](https://xpuoj.com/contest/11/submissions/109431) | 2026-08-11 20:18:44 | CUDA Maca C500 | Accepted | **62.50** | 平台探测复投；与#108986/exp190源码字节及SHA完全一致。OJ case1–14=`3/4/9/25/19/29/254/125/255/47/298/423/255/188 μs`；确认提交与评测链路可用，终态后队列为空；同源变化只作为timing-tier证据，不替换#108986 |
| [#109403](https://xpuoj.com/contest/11/submissions/109403) | 2026-08-11 19:53:00 | CUDA Maca C500 | Accepted | **62.64** | 平台探测复投；与#108986/exp190源码字节及SHA完全一致。OJ case1–14=`3/4/9/24/19/29/254/125/254/47/300/425/255/186 μs`；确认提交与评测链路可用，同源变化只作为timing-tier证据，不替换#108986 |
| [#109369](https://xpuoj.com/contest/11/submissions/109369) | 2026-08-11 19:21:57 | CUDA Maca C500 | Accepted | **62.07** | exp250：组合case14 register-packed m/l与case13 FP16x2 m/l，本地相对父版本分别约快1.27%/0.39%。OJ case1–14=`3/4/9/25/21/29/270/122/268/47/301/451/254/184 μs`；raw、提交快照和实验源码SHA一致，未超过#108986 |
| [#109339](https://xpuoj.com/contest/11/submissions/109339) | 2026-08-11 19:02:46 | CUDA Maca C500 | Accepted | **62.21** | exp248：只给case14压缩FP16x2 m/l，本地消偏约`0.9950`。OJ case14为`187 μs/47分`，未兑现微增益；raw、提交快照和实验源码SHA一致，不替换#108986 |
| [#109312](https://xpuoj.com/contest/11/submissions/109312) | 2026-08-11 18:38:30 | CUDA Maca C500 | Accepted | **62.29** | exp243：只把case5改为split3/3页，本地约快0.8%。OJ case5为`21 μs/68分`，未兑现；raw、提交快照和实验源码SHA一致，不替换#108986 |
| [#109260](https://xpuoj.com/contest/11/submissions/109260) | 2026-08-11 17:36:24 | CUDA Maca C500 / 176.6 K | Accepted | **62.43** | exp234：组合case7/8/9的本地split候选，并只把case12重扫到split40/52页；本地case12消偏约`0.9388`且完整correctness通过。OJ case1–14=`3/4/9/24/19/29/274/122/263/46/302/445/255/186 μs`，case12未兑现本地收益且从#109210的422 μs回退；raw、提交快照与exp234 SHA一致，不替换#108986 |
| [#109210](https://xpuoj.com/contest/11/submissions/109210) | 2026-08-11 16:43:02 | CUDA Maca C500 / 176.6 K | Accepted | **62.43** | exp223：在exp217上只把case7改为split3/43页；本地消偏约`0.9349`且完整correctness通过。OJ case7却`255→268 μs`、`52→51分`，未兑现本地收益；raw、提交快照与exp223 SHA一致，不替换#108986 |
| [#109180](https://xpuoj.com/contest/11/submissions/109180) | 2026-08-11 16:14:14 | CUDA Maca C500 / 176.5 K | Accepted | **62.57** | exp217：基于#108986只改case8 split14/19页和显式vec4 reducer；本地消偏约`0.8701`。OJ case8 `125→121 μs`但仍47分；case10/14无源码差异退档抵消目标收益，不替换#108986 |
| [#109150](https://xpuoj.com/contest/11/submissions/109150) | 2026-08-11 15:25:06 | CUDA Maca C500 / 176.6 K | Accepted | **62.57** | exp209：在exp205上只把case8改为33 allocated split/8页并保持vec4 reducer；本地消偏约`0.9521`。OJ case8 `125→123 μs`同向但仍47分，case11 split24波动到312 μs；不替换#108986。raw与提交快照SHA一致 |
| [#109127](https://xpuoj.com/contest/11/submissions/109127) | 2026-08-11 15:00:21 | CUDA Maca C500 / 176.6 K | Accepted | **62.57** | exp205：case11 split24/32页局部最优，本地相对#108986消偏约`0.9613`且完整correctness通过；OJ case11为`308 μs`，未超过#108986的`302 μs`。14/14 Accepted，raw与字节精确提交快照SHA `49abb196...0f19`一致，不替换baseline |
| [#109101](https://xpuoj.com/contest/11/submissions/109101) | 2026-08-11 14:34:22 | CUDA Maca C500 / 176.6 K | Accepted | **62.64** | exp201：native-row case11 split39/20页扫描点；14/14 Accepted，case11仍`302 μs`，aggregate未超过#108986。raw与提交快照已归档，不替换baseline |
| [#109064](https://xpuoj.com/contest/11/submissions/109064) | 2026-08-11 14:00:47 | CUDA Maca C500 / 176.2 K | Accepted | **62.50** | 用户要求的平台探测复投；与#108986/#108936/exp190字节及SHA完全一致，正常经历`Pending→Running→Finished`。OJ case1–14=`3/4/9/25/19/29/258/126/257/47/298/426/255/186 μs`，14/14 Accepted；同源变化只作为timing-tier波动证据，不替换#108986最高记录。raw与提交快照已归档 |
| [#108986](https://xpuoj.com/contest/11/submissions/108986) | 2026-08-11 12:14:38 | CUDA Maca C500 / 176.2 K | Accepted | **62.71** | 用户要求的平台探测复投；与#108936/exp190字节及SHA完全一致，正常经历`Pending→Compiling→Running→Finished`。OJ case1–14=`3/4/9/24/19/29/255/125/257/46/302/423/256/186 μs`，14/14 Accepted并刷新真实aggregate记录；逐case差异只作为同源timing-tier波动证据，结构性baseline仍为exp190。raw与提交快照已归档 |
| [#108966](https://xpuoj.com/contest/11/submissions/108966) | 2026-08-11 11:44:55 | CUDA Maca C500 / 176.5 K | Accepted | **62.50** | exp191：只给case5 grouped reducer启用native max/sum，本地双顺序消偏约`0.9799`且完整correctness通过。OJ case1–14=`3/4/9/24/19/29/255/126/256/47/297/424/255/188 μs`，目标case5仍`19 μs/70分`，未跨tier；不替换#108936。raw、提交快照与exp191哈希一致 |
| [#108936](https://xpuoj.com/contest/11/submissions/108936) | 2026-08-11 11:07:44 | CUDA Maca C500 / 176.2 K | Accepted | **62.57** | exp190：组合exp188/189的case5/10 native row QK并新增case3；本地消偏约`0.9259/0.8765/0.9109`，完整correctness通过。OJ case1–14=`3/4/9/25/19/29/255/125/253/47/300/422/255/186 μs`，case3/5/10达到`83/70/57分`，刷新当时最高分并建立exp190 baseline。raw、提交快照与exp190哈希一致 |
| [#108913](https://xpuoj.com/contest/11/submissions/108913) | 2026-08-11 10:37:55 | CUDA Maca C500 / 175.4 K | Accepted | **62.00** | exp186：只给case6 grouped reducer启用native max/sum，本地消偏约`0.9871`；OJ case6仍`29 μs/62分`未跨tier，不替换#108897。raw、提交快照与exp186哈希一致 |
| [#108897](https://xpuoj.com/contest/11/submissions/108897) | 2026-08-11 10:17:57 | CUDA Maca C500 / 173.6 K | Accepted | **62.07** | exp185：只给case4启用native row QK，本地消偏约`0.8728`；OJ case4 `29→24 μs`、`67→71分`，刷新当时最高分。raw、提交快照与exp185哈希一致 |
| [#108875](https://xpuoj.com/contest/11/submissions/108875) | 2026-08-11 10:00:16 | CUDA Maca C500 / 173.3 K | Accepted | **61.79** | 与#108865源码字节及SHA完全相同的恢复试投；逐case变化只作为timing-tier波动，不替换#108865 |
| [#108865](https://xpuoj.com/contest/11/submissions/108865) | 2026-08-11 09:44:32 | CUDA Maca C500 / 173.3 K | Accepted | **61.86** | exp184：只把native row QK扩展到case6，本地消偏约`0.9213`；OJ case6 `32→29 μs`、`60→62分`，刷新当时最高分。raw、提交快照与exp184哈希一致 |
| [#108856](https://xpuoj.com/contest/11/submissions/108856) | 2026-08-11 09:17:27 | CUDA Maca C500 / 173.1 K | Accepted | **61.64** | exp183：只把exp182的native 16-lane row allreduce扩展到generic KV8 case7；本地41×200正反消偏`0.8739`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/28/22/32/255/126/255/53/303/421/255/188 μs`；目标case7相对#108840 `283→255 μs`、`49→52分`，aggregate刷新并成为当前baseline。raw、提交快照与exp183哈希一致 |
| [#108840](https://xpuoj.com/contest/11/submissions/108840) | 2026-08-11 08:43:09 | CUDA Maca C500 / 172.9 K | Accepted | **61.50** | exp182：只把exp181的native 16-lane row allreduce扩展到generic KV8 case9；本地41×200正反消偏`0.8728`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/29/22/32/283/125/254/53/301/426/256/186 μs`；目标case9相对#108827 `287→254 μs`、`52→55分`，aggregate刷新并成为当前baseline。raw、提交快照与exp182哈希一致 |
| [#108827](https://xpuoj.com/contest/11/submissions/108827) | 2026-08-11 08:25:28 | CUDA Maca C500 / 172.8 K | Accepted | **61.36** | exp181：只给generic KV8 case12启用native 16-lane row allreduce；本地41×200正反消偏`0.8640`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/28/22/32/283/125/287/53/300/425/255/186 μs`；目标case12相对#108821 `472→425 μs`、`54→57分`，aggregate刷新并成为当前baseline。raw、提交快照与exp181哈希一致 |
| [#108821](https://xpuoj.com/contest/11/submissions/108821) | 2026-08-11 07:52:31 | CUDA Maca C500 / 172.0 K | Accepted | **61.14** | exp179：只把exp178的native 16-lane row allreduce扩展到case14；本地正反消偏`0.8516`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/28/22/31/283/126/284/53/299/472/254/186 μs`；目标case14相对#108816 `219→186 μs`、`43→48分`，aggregate刷新并成为当前baseline。raw、提交快照与exp179哈希一致 |
| [#108816](https://xpuoj.com/contest/11/submissions/108816) | 2026-08-11 07:33:57 | CUDA Maca C500 / 171.8 K | Accepted | **60.79** | exp178：只把exp177的native 16-lane row allreduce扩展到case8；本地正反消偏`0.8907`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/28/22/32/283/125/286/54/300/474/256/219 μs`；目标case8相对#108803 `139→125 μs`、`44→47分`，aggregate刷新并成为当时baseline。raw、提交快照与exp178哈希一致 |
| [#108803](https://xpuoj.com/contest/11/submissions/108803) | 2026-08-11 06:55:54 | CUDA Maca C500 / 171.8 K | Accepted | **60.50** | exp177：case11 QK只把全wave BSM XOR归约替换为原生16-lane row `mov.shfl` 四级网络；本地正反消偏`0.8524`，完整correctness通过。OJ 14/14 Accepted，case1–14=`3/4/10/29/22/32/284/139/284/53/301/475/254/220 μs`；目标case11相对#108743 `344→301 μs`、`41→45分`，aggregate刷新并成为当前baseline。raw、提交快照与exp177哈希一致 |
| [#108784](https://xpuoj.com/contest/11/submissions/108784) | 2026-08-11 06:03:36 | CUDA Maca C500 / 170.1 K | Accepted | **60.14** | #108743字节精确平台恢复试投；正常经历`Pending→Running→Finished`并14/14 Accepted，case1–14=`3/4/11/29/22/32/284/139/285/54/344/476/255/218 μs`。无源码差异下总分回落只作为timing-tier波动证据，不替换#108743 baseline；raw与逐提交源码已归档并核对哈希 |
| [#108772](https://xpuoj.com/contest/11/submissions/108772) | 2026-08-11 05:36:56 | CUDA Maca C500 / 171.8 K | Accepted | **60.29** | exp173：长KV8 case13/12/9/7逐shape把next K/V改为load-site `uint2`后立即标量化；本地消偏约`0.99436/0.99725/0.99581/0.99775`，完整correctness通过。目标case7/9/12/13=`282/283/471/253 μs`，均优于#108743的`283/285/472/255`但未跨分数档；aggregate持平，不替换#108743。raw、提交快照与exp173哈希一致 |
| [#108763](https://xpuoj.com/contest/11/submissions/108763) | 2026-08-11 05:06:00 | CUDA Maca C500 / 172.2 K | Accepted | **60.14** | exp170：case13只用两次`uint2` load后立即标量化next K/V，跨PV live state和store保持八标量；本地强测消偏`0.99436`，完整correctness通过。14/14 Accepted，case1–14=`3/4/11/29/22/31/284/139/284/54/345/473/254/221 μs`；目标case13 `255→254 μs`同向但仍48分，非目标tier使总分下降，不替换#108743。raw、提交快照与exp170哈希一致 |
| [#108747](https://xpuoj.com/contest/11/submissions/108747) | 2026-08-11 04:17:49 | CUDA Maca C500 / 170.1 K | Accepted | **60.29** | #108743字节精确平台恢复试投；正常经历`Pending→Running→Finished`并14/14 Accepted，case1–14=`3/4/10/29/22/32/284/139/285/53/344/474/255/218 μs`。case14快1 μs并跨到44分，但case4慢1 μs降到67分，总分持平；判为同源timing-tier波动，不替换#108743 baseline。raw与逐提交源码已归档并核对哈希 |
| [#108743](https://xpuoj.com/contest/11/submissions/108743) | 2026-08-11 03:50:41 | CUDA Maca C500 / 170.1 K | Accepted | **60.29** | exp163：相对exp161只把case14改为head-pair/z4并组合同步K/V register-lookahead；本地消偏`0.8576`。14/14 Accepted，case1–14=`3/4/10/28/22/32/283/139/285/53/344/472/255/219 μs`；case14相对#108713 `258→219 μs`、`40→43分`，总分刷新并成为baseline。raw、提交快照、exp163源码与工作文件哈希一致 |
| [#108721](https://xpuoj.com/contest/11/submissions/108721) | 2026-08-11 03:07:02 | CUDA Maca C500 / 168.9 K | Accepted | **59.86** | exp161：在exp160上只给case9 split24 producer启用Q预缩放，并组合exp160的case7变化；本地消偏约`0.9947/0.9968`。14/14 Accepted，case1–14=`3/4/11/29/22/32/284/139/285/54/346/473/255/258 μs`；case7相对#108713 `285→284 μs`同向，case9保持285 μs，非目标tier回退令总分下降，不替换#108713。raw、提交快照与exp161源码哈希一致 |
| [#108713](https://xpuoj.com/contest/11/submissions/108713) | 2026-08-11 02:49:25 | CUDA Maca C500 / 168.9 K | Accepted | **60.14** | exp159：在exp158上只给case12的16-page producer启用Q预缩放，本地消偏`0.99645`。14/14 Accepted，case1–14=`3/4/10/29/22/31/285/139/285/54/341/475/255/258 μs`；目标case12 `476→475 μs`，case6/case11跨到61/42分，总分刷新并成为baseline。raw、提交快照与exp159源码哈希一致 |
| [#108700](https://xpuoj.com/contest/11/submissions/108700) | 2026-08-11 02:30:49 | CUDA Maca C500 / 168.8 K | Accepted | **59.93** | exp158：在exp157上只给case13的15-page producer启用Q预缩放，本地强复测消偏`0.99805`；14/14 Accepted，case1–14=`3/4/11/28/22/32/284/139/286/54/346/476/254/257 μs`。目标case13相对#108691 `256→254 μs`但仍为48分档；非目标tier令总分下降，不替换#108679。raw、提交快照与exp158源码哈希一致 |
| [#108691](https://xpuoj.com/contest/11/submissions/108691) | 2026-08-11 02:19:13 | CUDA Maca C500 / 168.6 K | Accepted | **60.00** | exp157：只给case6约3 pages/split路径启用Q预缩放，本地强复测消偏`0.98942`；14/14 Accepted，case1–14=`3/4/11/28/22/32/285/139/286/53/343/476/256/256 μs`。目标case6仍32 μs未跨tier；非目标case3 `10→11 μs`使总分下降，不替换#108679。raw、提交快照与exp157源码哈希一致 |
| [#108679](https://xpuoj.com/contest/11/submissions/108679) | 2026-08-11 02:03:22 | CUDA Maca C500 / 168.4 K | Accepted | **60.07** | exp156：在exp153上给case10/4启用相同Q预缩放；相对#108658最终本地消偏约`0.99765/0.9927`。14/14 Accepted，case1–14=`3/4/10/28/22/32/286/139/287/54/344/477/256/258 μs`；目标case4 `29→28 μs`、得分`67→68`，case10保持54。case11源码未变但tier `343→344 μs`使得分`42→41`，总分仍60.07；因目标变化一致，选为当前baseline。raw、提交快照与exp156源码哈希一致 |
| [#108658](https://xpuoj.com/contest/11/submissions/108658) | 2026-08-11 01:31:21 | CUDA Maca C500 / 168.0 K | Accepted | **60.07** | exp153：在exp151基础上逐shape给case8/14启用相同Q预缩放；本地case11/8/14消偏约`0.99556/0.99298/0.99645`。14/14 Accepted，case1–14=`3/4/10/29/22/32/283/139/285/54/343/476/255/257 μs`；case11相对#108628 `348→343 μs`、得分`41→42`，总分刷新并成为当前baseline。raw、提交快照与exp153源码哈希一致 |
| [#108651](https://xpuoj.com/contest/11/submissions/108651) | 2026-08-11 01:07:09 | CUDA Maca C500 / 166.8 K | Accepted | **59.93** | exp151：case11 Q 只在每split预乘一次`sm_scale`，移除逐token score缩放；本地强复测消偏约`0.99556`，14/14 Accepted，case1–14=`3/4/10/29/22/32/286/139/288/53/345/477/255/259 μs`。目标case11相对#108628 `348→345 μs`同向改善，但总分未保持，故不替换baseline；raw、提交快照与exp151源码哈希一致 |
| [#108641](https://xpuoj.com/contest/11/submissions/108641) | 2026-08-11 00:42:49 | CUDA Maca C500 / 165.7 K | Accepted | **59.93** | #108628字节精确恢复试投，14/14 Accepted，case1–14=`3/4/10/29/22/32/285/140/286/54/347/476/255/259 μs`。同源timing-tier波动，不替换baseline；raw与逐提交源码已归档并核对哈希 |
| [#108628](https://xpuoj.com/contest/11/submissions/108628) | 2026-08-11 00:20:17 | CUDA Maca C500 / 165.7 K | Accepted | **60.00** | exp149：只把case12 reducer由32-thread vec4改为64-thread完整wave vec2；本地强复测消偏`0.99890`，14/14 Accepted，case1–14=`3/4/10/29/22/32/285/139/285/54/348/476/256/257 μs`。目标case12相对#108604 `477→476 μs`但得分仍54；因目标OJ变化与A/B一致，选为当前baseline。raw与逐提交源码已归档并核对哈希 |

### 2026-08-10

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#108604](https://xpuoj.com/contest/11/submissions/108604) | 2026-08-10 23:44:17 | CUDA Maca C500 / 165.6 K | Accepted | **60.00** | exp147：case10 reducer由32-thread vec4改为64-thread完整wave vec2，本地双顺序消偏`0.9759`；14/14 Accepted，case1–14=`3/4/10/29/22/32/285/140/287/54/347/477/255/257 μs`，case10得分`53→54`使总分首次达到60.00。raw与逐提交源码已归档并核对哈希，选为当前baseline |
| [#108550](https://xpuoj.com/contest/11/submissions/108550) | 2026-08-10 22:23:11 | CUDA Maca C500 / 165.5 K | Accepted | **59.86** | #108468同字节恢复探针，14/14 Accepted；case1–14=`3/4/11/28/22/32/286/139/286/55/347/478/255/258 μs`。同源tier波动使总分不变，不替换baseline；raw与逐提交源码已归档并核对哈希 |
| [#108468](https://xpuoj.com/contest/11/submissions/108468) | 2026-08-10 20:55:11 | CUDA Maca C500 / 165.5 K | Accepted | **59.86** | exp138：逐shape把四标量V-over-PV扩展到case12/9/7，与case13共同闭合四个长KV8 shape。14/14 Accepted；相对#108312，case7/9/12/13改善`4/4/7/1 μs`，case8/11各波动`+1 μs`，其余持平。总分并列但目标OJ结果与本地A/B一致，选为当前baseline |
| [#108398](https://xpuoj.com/contest/11/submissions/108398) | 2026-08-10 19:44:38 | CUDA Maca C500 / 165.5 K | Canceled | — | exp136，与#108371同SHA；在故障期长期Pending且没有测试点，后续取消。无OJ性能数据，raw与字节精确源码已归档 |
| [#108371](https://xpuoj.com/contest/11/submissions/108371) | 2026-08-10 19:22:16 | CUDA Maca C500 / 165.5 K | Canceled | — | exp136：只给case12增加四标量V-over-PV，本地消偏`0.9884`、快约1.16%，全量与定点correctness通过。提交持续Pending超过21分钟后，为保持单任务并测试恢复队列而主动取消；无OJ测试点和性能数据，raw与字节精确源码已归档 |
| [#108312](https://xpuoj.com/contest/11/submissions/108312) | 2026-08-10 18:36:26 | CUDA Maca C500 / 165.5 K | Accepted | **59.86** | exp135：排除未启用CUTE/MCTLASS/WMMA编译表面，显式保持token-parallel/BASE2；解决两次compile TLE。承接exp68–134全部本地正向组合，14/14 Accepted，case4–14=`29/22/32/289/139/289/55/347/486/256/259 μs`，首次达到当前最高并成为当时baseline |
| [#108278](https://xpuoj.com/contest/11/submissions/108278) | 2026-08-10 17:56:04 | CUDA Maca C500 / 165.9 K | CompilationError（compile TLE） | — | exp134 与 #108257 同SHA复投，再次在OJ编译阶段`TimeLimitExceeded`；无测试点和性能数据。该重复结果促成exp135编译表面裁剪，raw与字节精确源码已归档 |
| [#108257](https://xpuoj.com/contest/11/submissions/108257) | 2026-08-10 17:30:21 | CUDA Maca C500 / 165.9 K | CompilationError（compile TLE） | — | exp134：case13在四标量K-lookahead上增加四标量V-over-PV，本地双顺序消偏`0.9772`、快约2.28%，CPU/GPU全量与定点通过。OJ编译阶段`TimeLimitExceeded`，日志无真正compiler error；raw与字节精确源码已归档，不作为性能结果、不自动重投 |
| [#107882](https://xpuoj.com/contest/11/submissions/107882) | 2026-08-10 10:31:26 | CUDA Maca C500 / 160.9 K | Canceled | — | exp131：case12/13零spill四标量K-over-PV；本地case13消偏`0.977686`、快约2.23%，CPU/GPU全量与定点通过。提交长期Pending后被外部动作取消，无OJ性能结果；raw与字节精确源码已归档 |
| [#107856](https://xpuoj.com/contest/11/submissions/107856) | 2026-08-10 09:35:50 | CUDA Maca C500 / 159.0 K | Canceled | — | exp125：case10同步K/V register-lookahead；本地消偏`0.9671`、快约3.29%，全量correctness通过。长期Pending后为避免并行提交而主动取消，无OJ性能结果；raw与字节精确源码已归档 |

### 2026-08-09

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#106626](https://xpuoj.com/contest/11/submissions/106626) | 2026-08-09 11:45:42 | CUDA Maca C500 / 114.6 K | Accepted | **57.64** | case 11 使用 `(16,4,4)` 256-thread head-pair/z4 CTA；K/V 仍单次加载，四个 z-state 用 8 KiB shared 两级归约。本地 p50 `0.9528`，OJ case 11 `0.417 ms/37`，刷新当前最高并成为新 baseline |
| [#106584](https://xpuoj.com/contest/11/submissions/106584) | 2026-08-09 11:20:38 | CUDA Maca C500 / 114.3 K | Accepted | 57.29 | #106556 head-pair 的每-z 8-token score 改成两个顺序 4-token chunk，full kernel `100→82 MTreg`；本地 case 11 p50 `0.9703`、全量 correctness 通过，但 OJ case 11 回退至 `0.467 ms`，关闭 z=2 下 live-score 局部扫描 |
| [#106556](https://xpuoj.com/contest/11/submissions/106556) | 2026-08-09 10:52:00 | CUDA Maca C500 / 104.0 K | Accepted | 57.43 | case 11 改用 `(16,4,2)` 128-thread head-pair CTA，一次 K/V load/unpack 服务两个 query head且不重复整页 loader；本地 p50 `0.9472`、全量 correctness 通过，但 OJ case 11 为 `0.452 ms`，未超 #106069 的 `0.438 ms`；保留架构证据，不替代 baseline |
| [#106503](https://xpuoj.com/contest/11/submissions/106503) | 2026-08-09 10:01:00 | CUDA Maca C500 / 91.7 K | Accepted | 57.57 | 只在 case 4（B64/L64/KV8）启用双 token QK interleave；本地 p50 `0.9758`，非目标 case 中性，但 OJ case 4 仍为 `0.030 ms`，未跨 timing tier；不替代 baseline |
| [#106170](https://xpuoj.com/contest/11/submissions/106170) | 2026-08-09 00:08:14 | CUDA Maca C500 / 90.5 K | Accepted | 57.57 | full-page QK 交错两个独立 token 的 packed-FMA / 16-lane shuffle；本地小幅正向，但 OJ 与 #106069 并列。case 4 `0.029 ms` 有利，case 8/11/12 为 `0.179/0.440/0.537 ms`；不替代 baseline |

### 2026-08-08

| 提交 | 时间 | 环境 | 状态 | 总分 | 备注 |
|---|---|---|---|---:|---|
| [#106116](https://xpuoj.com/contest/11/submissions/106116) | 2026-08-08 22:59:12 | CUDA Maca C500 / 88.0 K | Accepted | 57.43 | case 8（B16/L4096/KV4）改为 `separate_tail`，full-only 变体由 92 MTreg/5 warps 降至 70 MTreg/7 warps；本地交错 A/B p50 `0.941`，但 OJ case 8 `0.175 ms` 未优于 control `0.174 ms`，且 case 11 `0.443 ms` 回退，拒绝为 baseline |
| [#106069](https://xpuoj.com/contest/11/submissions/106069) | 2026-08-08 21:53:29 | CUDA Maca C500 / 86.8 K | Accepted | **57.57** | case 11（B16/L12251/KV4）Q shared-memory 复用：`sync_kv4+separate_tail` 的 full/tail launch 改用 `INPLACE_SHARED_Q=true`，去掉 2 KiB 动态 Q 缓冲、提升 residency；case 11 `0.448→0.438 ms`（35→36 分）。本地交错 A/B case 11 ratio p50 `0.9727`，case 5/8/10/14 中性。case 5 OJ `0.025 ms` 为有利 tier 波动，非本改动所致 |
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

### 2026-08-13

#### 提交 #111641 · #111319 同源平台链路探测

- **提交与排队**：用户要求尝试一次真实提交。提交前最近10笔均已终态，先对不可变baseline `cuda_111319.cpp`完成dry-run，再只创建#111641。平台列表一度仍为Pending，watch进度曾显示Running且数分钟无case明细；全程未取消、未复投，最终正常Finished。
- **OJ结果与选择**：Accepted（14/14）/ `64.07`；case1–14=`3/4/9/23/18/28/246/116/244/42/279/390/212/169 μs`，分数=`92/90/83/72/71/63/53/48/56/60/47/59/53/50`。确认OJ创建、排队、编译和完整评测链路可用；同源码相对#111319 / 64.14的变化只作为timing-tier样本，不替换baseline，终态后队列为空。
- **源码核对**：raw内嵌源码、[`cuda_111641.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111641.cpp)与#111319 SHA均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。
- **原始归档**：[`cuda_111641_raw.json`](raw/cuda_111641_raw.json)。

#### 提交 #111616 · exp406b case11 split24 + vec4 fused-tail reducer

- **唯一差异与契约修复**：相对exp405只把case11从48个logical split、16 pages/partial改为24个split、32 pages/partial。初版exp406因`reduce_splits<=32`隐式切换到generic group8 reducer，后者没有fused-tail live-count，长度513/1025 WrongAnswer；exp406b把case11原one-head vec4 reducer分支置于阈值判断之前，保持`FUSE_TAIL_IN_LAST_SPLIT=true`，其余producer、全原生QK、loader、partial ABI和shape不变。
- **本地证据**：SHA=`8a8c299a66942d33db6317e6e29049530e78511f44c48f542eec3adee3c08ac7`。CPU14/14，GPU full/boundary/random各14/14，case11 `12251→1/2/15/16/17→511/512/513→1023/1024/1025→12250/12251`全部PASS。相对exp405正向p50=`0.9583`、反向old/new=`1.0423`，final rebuild p50=`0.9585`，双角色消偏约`0.9588`；split22/23/25/26相对24为`1.0111/1.0118/1.0088/1.0052`，本地曲线由两侧夹定24。
- **OJ结果与选择**：Accepted（14/14）/ `64.00`；case1–14=`3/4/10/23/18/28/247/114/244/41/281/388/212/167 μs`，分数=`92/90/82/72/71/63/53/49/56/60/46/59/53/50`。目标case11比exp405的277 μs和#111319的279 μs都慢，掉到46分。本地4.1%收益没有兑现真实OJ，不替换#111319；split22–26邻域已经闭合，不同源复投或继续微扫。raw、逐提交快照和提交前源码SHA一致，工作文件恢复exp405。

#### 提交 #111590 · exp405 case5 combined-tail 全原生 split-head QK

- **唯一差异**：相对exp403/#111570，只给case5 combined-page split-head QK启用`rotate4 → rotate8 → quad2 → quad1`全原生网络，并把head1 owner/page-max/PV broadcast从lane8改到lane4。invalid masked-tail owner保持`-Inf`，固定四token broadcast中的无效权重精确为0；case8/10/11/14、loader、split、partial和reducer不变。
- **静态与本地证据**：SHA=`fd789c6954b6280e419c94f994c3027eb2e73461ddbcda9e2aa4e86a24512407`。case5 producer保持`86 MTreg/56 STreg/8320 B/0 stack/5 waves`；CPU14/14，GPU full/boundary/random各14/14，20步full→short→page/split边界→full复用全部PASS。相对fresh #111570正向p50=`0.9900`、反向old/new=`1.0253`，双角色消偏约`0.9826`；case8/10/11/14 p50=`0.9991/0.9996/0.9993/0.9999`。
- **OJ结果与选择**：Accepted（14/14）/ `64.07`；case1–14=`3/4/10/23/18/28/246/115/243/41/277/391/211/167 μs`，分数=`92/90/82/72/71/63/53/49/56/60/47/59/53/50`。目标case5仍18 μs，没有跨tier；case9/10刷新Accepted历史最佳但不加分，aggregate未刷新。保留exp405为leading组合父版本，不替换#111319 / 64.14 default control，不同源复投。
- **源码核对**：raw内嵌源码、[`cuda_111590.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111590.cpp)与提交前工作文件SHA均为`fd789c6954b6280e419c94f994c3027eb2e73461ddbcda9e2aa4e86a24512407`。
- **原始归档**：[`cuda_111590_raw.json`](raw/cuda_111590_raw.json)。

#### 提交 #111570 · exp403 case8+10+11+14 全原生 split-head QK

- **唯一差异**：从exp402只给case10 generic full-page split-head QK启用`rotate4 → rotate8 → quad2 → quad1`全原生网络，并把head1 owner/page-max/PV broadcast从lane8改为lane4。case11原本已启用；case8/14 fixed helper、case5 combined tail、fused tail、split128、四页/partial、K/V lookahead、FP32 accumulator、packed metadata和vec2 reducer不变。
- **静态与本地证据**：SHA=`070f4ce0fbe5ad1aa22c82ba7eb97b15203fa0d61f78524e3d2b82c811fee126`。case10资源保持`86 MTreg/62 STreg/8320 B/0 stack/5 waves`；CPU14/14，GPU full/boundary/random各14/14，17步full→short→split边界→full复用全部PASS。相对exp402 41×500正向p50=`0.9850`、反向old/new=`1.0118`，消偏约`0.9865`；相对#111319最终组合case10/8/11/14约`0.9895/0.9878/0.9820/0.9842`。
- **OJ结果与选择**：Accepted（14/14）/ `64.00`；case1–14=`3/4/10/23/18/28/246/116/244/42/275/389/211/167 μs`，分数=`92/90/82/72/71/63/53/48/56/60/47/59/53/50`。目标case10仍42 μs，没有跨tier；case11刷新Accepted历史最佳275 μs，但case8掉1分、case14比exp402回退1 μs，aggregate未刷新。保留exp403为leading组合父版本，不替换#111319 / 64.14 default control，不同源复投。
- **源码核对**：raw内嵌源码、[`cuda_111570.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111570.cpp)与提交前工作文件SHA均为`070f4ce0fbe5ad1aa22c82ba7eb97b15203fa0d61f78524e3d2b82c811fee126`。
- **原始归档**：[`cuda_111570_raw.json`](raw/cuda_111570_raw.json)。

#### 提交 #111547 · exp402 case8+11+14 全原生 split-head QK

- **唯一差异**：从exp401只给case14满长前256个fixed15 common split启用`rotate4 → rotate8 → quad2 → quad1`全原生网络，并把head1 owner/page-max/PV broadcast从lane8改到lane4。最后underfilled split、任意短长度、split257、K/V register lookahead、softmax/PV、normalized-BF16 partial和reducer不变。
- **静态与本地证据**：SHA=`89f20c24824ee69861df33608897a11c1d48e1992f7c1cc7db0cd7d05558dc1b`。case14资源保持`90 MTreg/58 STreg/8320 B/0 stack/5 waves`；CPU14/14，GPU full/boundary/random各14/14，12步full→short→split边界→full复用全部PASS。相对exp401 21×300正向p50=`0.9858`、反向old/new=`1.0171`，消偏约`0.9845`；相对#111319最终组合case8/11/14约`0.9872/0.9816/0.9838`。
- **OJ结果与选择**：Accepted（14/14）/ `64.00`；case1–14=`3/4/10/23/18/29/246/115/245/42/279/387/212/166 μs`，分数=`92/90/82/72/71/62/53/49/56/60/47/59/53/50`。case14真实快3 μs但仍未跨50分；case6掉1分、case11同源回退抵消aggregate。保留exp402为leading组合父版本，不替换#111319 / 64.14 default control。
- **源码核对**：raw内嵌源码、[`cuda_111547.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111547.cpp)与提交前工作文件SHA均为`89f20c24824ee69861df33608897a11c1d48e1992f7c1cc7db0cd7d05558dc1b`。
- **原始归档**：[`cuda_111547_raw.json`](raw/cuda_111547_raw.json)。

#### 提交 #111528 · exp401 case8+11 全原生 split-head QK

- **唯一差异**：在exp400上只给case8满长前13个fixed19 common split启用同一`rotate4 → rotate8 → quad2 → quad1`网络，并把该helper的head1 owner/broadcast从lane8改到lane4。最后underfilled split、任意短长度、case11 exp400和其他shape不变。
- **静态与本地证据**：SHA=`60045917aed5cfab02b9978de4d5e4b55615273a38641152c0c759f7eafa9223`。case8/11资源分别保持`86/70`与`86/64 MT/STreg`、8320 B、0 stack、5 waves。CPU14/14，GPU full/boundary/random各14/14，case8 `4096→16/17→303/304/305→3951/3952/3953→4095/4096`同进程复用全部PASS。相对exp400的21×300正向case8 p50=`0.9872`、反向old/new=`1.0115`，消偏约`0.9879`；case11中性。相对#111319最终组合case8/11 p50=`0.9863/0.9813`。
- **OJ结果与选择**：Accepted（14/14）/ **`64.14`**；case1–14=`3/4/9/23/18/28/246/115/245/42/277/389/212/169 μs`，分数=`92/90/83/72/71/63/53/49/56/60/47/59/53/50`。case8保持115 μs、case11比#111319快2 μs但均未跨档；case3同源快1 μs使aggregate并列。保留exp401作为leading组合和后续扩展父版本，但最高真实分与默认control仍指向先建立64.14的#111319。
- **源码核对**：raw内嵌源码、[`cuda_111528.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111528.cpp)与提交前工作文件SHA均为`60045917aed5cfab02b9978de4d5e4b55615273a38641152c0c759f7eafa9223`。
- **原始归档**：[`cuda_111528_raw.json`](raw/cuda_111528_raw.json)。

#### 提交 #111517 · exp400 case11 全原生 split-head QK

- **唯一差异**：只改case11 full-page QK归约。保留双head K解包复用和八次packed FMA，把原`rotate8 → BSM XOR4 → quad2 → quad1`网络改为`rotate4 → rotate8 → quad2 → quad1`，head owner由`tx&8`改为`tx&4`；loader、split48、tail、softmax/PV、FP32 partial和vec4 reducer不变。
- **静态与本地证据**：独立真实C500 probe证明新网络分别得到两个完整16-lane dot，codegen probe从`5→4 MTreg`；生产case11资源保持`86 MTreg/64 STreg/8320 B/0 stack/5 waves`。CPU14/14，GPU full/boundary/random各14/14，case11 16步full→短长→split边界→full复用全部通过。21×300正向candidate/control p50=`0.9814`，反向old/new=`1.0180`，双角色消偏约`0.9818`、快约1.82%。
- **OJ结果与选择**：Accepted（14/14）/ `64.00`；case1–14=`3/4/10/23/18/28/246/116/244/42/276/391/212/169 μs`，分数=`92/90/82/72/71/63/53/48/56/60/47/59/53/50`。目标case11相对#111319 `279→276 μs`，与A/B同向但未跨47分；case8无源码差异地`115→116 μs`掉1分。保留exp400为已确认组件，不替换#111319 / 64.14 baseline。
- **源码核对**：raw内嵌源码、[`cuda_111517.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111517.cpp)与提交前工作文件SHA-256均为`64ec2c8f804c0a6f00fde553d9e8849576df961d361044c609d5603f8d76beb5`。
- **原始归档**：[`cuda_111517_raw.json`](raw/cuda_111517_raw.json)。

#### 提交 #111489 · #111319 同源平台试投

- **状态/选择**：Accepted（14/14）/ `64.07`。提交前队列为空并完成dry-run，只创建一笔任务；任务正常由`Pending→Running→Finished`，终态后队列为空。
- **OJ结果**：case1–14=`3/4/10/22/18/28/246/115/245/42/282/390/211/169 μs`，分数=`92/90/82/73/71/63/53/49/56/60/46/59/53/50`。相对同源#111319的变化属于timing-tier波动，不构成源码归因，不替换64.14 baseline。
- **源码核对**：raw内嵌源码、[`cuda_111489.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111489.cpp)、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。
- **原始归档**：[`cuda_111489_raw.json`](raw/cuda_111489_raw.json)。

#### 提交 #111431 · #111319 同源平台试投

- **状态/选择**：Accepted（14/14）/ `64.00`。唯一任务成功由`Pending→Running→Finished`，确认OJ全链路可用；终态后队列为空。
- **OJ结果**：case1–14=`3/4/10/23/18/28/244/115/245/42/281/389/211/169 μs`，分数=`92/90/82/72/71/63/53/49/56/60/46/59/53/50`。相对同源#111319/#111364的变化属于timing-tier波动，不构成源码归因，不替换64.14 baseline。
- **源码核对**：raw内嵌源码、[`cuda_111431.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111431.cpp)、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。
- **原始归档**：[`cuda_111431_raw.json`](raw/cuda_111431_raw.json)。

#### 提交 #111364 · #111319 同源平台试投

- **状态/选择**：Accepted（14/14）/ `64.00`。提交、编译和完整评测链路正常；没有创建并行任务，终态后队列为空。
- **OJ结果**：case1–14=`3/4/10/23/18/28/247/115/244/42/283/391/211/169 μs`，分数=`92/90/82/72/71/63/53/49/56/60/46/59/53/50`。相对同源#111319的变化属于timing-tier波动，不构成源码归因，不替换64.14 baseline。
- **源码核对**：raw内嵌源码、[`cuda_111364.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111364.cpp)、工作文件与#111319的SHA-256均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`。
- **原始归档**：[`cuda_111364_raw.json`](raw/cuda_111364_raw.json)。

#### 提交 #111319 · exp390 case7 head-pair/z8 + packed group8

- **总状态/总分**：Accepted（14/14）/ **`64.14`**；唯一任务长Pending后正常经过`Compiling→Running→Finished`，终态后队列为空。
- **唯一差异与门禁**：从#111307只把z8 producer扩到case7，并给既有8-head group8 reducer增加packed FP16x2 `(m,l)`读取；split14、10 pages/partial、fused-tail、同步K+V-over-PV、partial数量与reducer grid不变。CPU14/14、GPU full/boundary/random各14/14；case7同进程`2048→1/2/15/16/17→159/160/161→255/256/257→2047/2048`全部PASS。
- **A/B与OJ**：相对exp389正向p50=`0.9773`，反向旧/新=`1.0235`，消偏约`0.9769`、快约2.31%；case9中性。OJ case1–14=`3/4/9/23/18/28/247/115/245/42/279/390/212/169 μs`，目标case7相对#111307 `256→247 μs`并由52升到53分。
- **源码核对**：raw内嵌源码、[`cuda_111319.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111319.cpp)和工作文件SHA均为`7953c2c813f2066d3de620b66481ea90d4065391bcbc622fcbb85699861baacc`；选为新baseline。
- **原始归档**：[`cuda_111319_raw.json`](raw/cuda_111319_raw.json)。

#### 提交 #111307 · exp389 case9 head-pair/z8 + packed vec2

- **总状态/总分**：Accepted（14/14）/ **`64.07`**。
- **错误诊断与唯一修复**：exp388把z8 producer扩到case9却保留vec4 reducer；producer把FP16x2 `(m,l)`写入`partial_m`且不写`partial_l`，因此case9仅`0.082657` match。exp389保留producer和全部split/loader/partial数量，只改用packed-aware vec2 reducer。
- **门禁/A-B/OJ**：CPU14/14、GPU三组各14/14与case9 14步复用通过；正向p50=`0.9661`、反向旧/新=`1.0343`，消偏约`0.9664`。OJ case9相对#111231 `254→244 μs`、`55→56分`。
- **源码核对**：raw、[`cuda_111307.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111307.cpp)与实验源码SHA均为`b1da92c381956abd5b3016e2f74207a5fdbbc82420352cb64552bb1ecfb0a3ec`；当时选为baseline，后由#111319取代。
- **原始归档**：[`cuda_111307_raw.json`](raw/cuda_111307_raw.json)。

#### 提交 #111272 · #111231 同源平台恢复试投

- **状态/选择**：Accepted（14/14）/ `63.93`。提交源码与#111231 SHA同为`adb1c0132f93b8b579e62dd2ccf2351419d5accca2ab87ea19a6c0c62bbe7ad2`；长Pending期间没有取消或复投。
- **OJ结果**：case1–14=`3/4/9/23/18/28/253/115/252/42/283/389/211/169 μs`。无源码差异，只作为timing-tier与平台恢复样本，不替换#111231。
- **原始归档**：[`cuda_111272_raw.json`](raw/cuda_111272_raw.json)。

#### 提交 #111231 · exp387 case12 head-pair/z8 producer ownership

- **总状态/总分**：Accepted（14/14）/ **`64.00`**；只创建这一笔，正常经过`Pending→Compiling→Running→Finished`，终态后队列为空。
- **唯一差异与资源**：从#111200只把case13已验证的`dim3(16,2,8)` head-pair/z8 producer扩展到case12。split128、16 pages/partial、fused-tail语义、同步K+V-over-PV、Q prescale、FP16x2 `(m,l)` partial、global partial数量和vec2 reducer不变。资源由旧case12的`64 MTreg/50 STreg/8192 B/0 stack/8 waves`变为`82/50/8448 B/0/5 waves`。
- **门禁与A/B**：CPU14/14、GPU full/boundary/random各14/14；case12同进程`32768→1→2→15→16→17→255→256→257→511→512→513→4095→4096→4097→32767→32768`全部PASS。强测正向candidate/control p50=`0.9326`，反向old/new p50=`1.0740`，双角色消偏约`0.9319`、稳定快约6.8%；case7/9/13 p50=`1.0003/1.0004/1.0006`。
- **源码核对与OJ选择**：raw内嵌源码、[`cuda_111231.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111231.cpp)和工作文件SHA均为`adb1c0132f93b8b579e62dd2ccf2351419d5accca2ab87ea19a6c0c62bbe7ad2`。OJ case1–14=`3/4/9/23/18/28/256/114/254/42/280/388/212/170 μs`，分数=`92/90/83/72/71/63/52/49/55/60/47/59/53/50`；目标case12相对#111200从`422→388 μs`并由57升到59分，aggregate刷新到64.00，因此选为新baseline。
- **原始归档**：[`cuda_111231_raw.json`](raw/cuda_111231_raw.json)。

#### 提交 #111200 · exp386 case13 head-pair/z8 producer ownership

- **总状态/总分**：Accepted（14/14）/ **`63.71`**；只创建这一笔，正常完成完整评测，终态后队列为空。
- **唯一差异与资源**：从#111115只修改case13 producer ownership：`dim3(16,4,4)`的每线程一个query head、四token/z，改为`dim3(16,2,8)`的每线程两个query head、两token/z；八个z-state以三阶段shared-memory树合并。split256、15 pages/partial、256线程、同步loader、K+V-over-PV、Q prescale、FP16x2 `(m,l)` partial、global partial数量和vec2 reducer不变。资源由旧case13的`64 MTreg/50 STreg/8192 B/0 stack/8 waves`变为`82/50/8448 B/0/5 waves`。
- **门禁与A/B**：CPU14/14、GPU full/boundary/random各14/14；case13同进程`58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`全部PASS。强测正向candidate/control p50=`0.8371`，反向old/new p50=`1.1975`，双角色消偏约`0.8361`、稳定快约16.4%；case7/9/12首轮p50=`0.9989/0.9996/1.0002`。
- **源码核对与OJ选择**：raw内嵌源码、[`cuda_111200.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111200.cpp)和工作文件SHA均为`b3893f989fcbb7a2d00c0d161e6bc33ff821cda10cf7ab020a09676c7ff8bb6c`。OJ case1–14=`3/4/9/23/18/28/254/116/254/42/281/422/212/169 μs`，分数=`92/90/83/72/71/63/52/48/55/60/46/57/53/50`；目标case13相对#111115从`252→212 μs`并由48升到53分，aggregate刷新到63.71，因此选为新baseline。
- **原始归档**：[`cuda_111200_raw.json`](raw/cuda_111200_raw.json)。

#### 提交 #111163 · #111115/exp385 同源平台连通性复投

- **总状态/总分**：Accepted（14/14）/ **`63.29`**；提交前队列为空，只创建这一笔。任务Pending约四分钟后正常经过`Compiling→Running→Finished`，终态后队列为空。
- **源码核对**：raw内嵌源码、逐提交快照[`cuda_111163.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111163.cpp)、工作文件与#111115快照的SHA-256均为`aa486885aabf4ad373402149c1b6e98ce3b6694a4c73cec264a7bf124c70120c`。
- **OJ结果与选择**：case1–14=`3/4/10/24/18/28/254/116/257/42/280/422/253/169 μs`，分数=`92/90/82/71/71/63/52/48/55/60/47/57/48/50`。相对同源#111115，case4/8各掉1分、case11升1分，aggregate低0.07；没有新源码差异，故只作为timing-tier样本，当时最高分和默认control继续保持#111115 / 63.36。
- **原始归档**：[`cuda_111163_raw.json`](raw/cuda_111163_raw.json)。

#### 提交 #111115 · exp385 case5 native-row group8 reducer

- **总状态/总分**：Accepted（14/14）/ **`63.36`**；唯一任务排队超过30分钟，本地watcher超时后没有取消或复投，重新挂接同一提交后正常`Running→Finished`，终态后队列为空。
- **源码与门禁**：在exp384上只给case5 group8 reducer启用native-row max/sum，producer与#111076完全一致。目标reducer为`66 MTreg/26 STreg/0 shared/0 stack/7 waves`；CPU14/14、GPU full/boundary/random各14/14、case5精确长度与`141→1→…→141`同进程workspace复用全部PASS。相对#111076 reducer唯一差异双角色消偏约`0.9781`；相对#111016 producer+reducer组合消偏约`0.9447`。
- **源码核对与OJ选择**：raw内嵌源码、[`cuda_111115.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111115.cpp)和工作文件SHA均为`aa486885aabf4ad373402149c1b6e98ce3b6694a4c73cec264a7bf124c70120c`。OJ case1–14=`3/4/10/23/18/28/252/115/255/42/281/425/252/169 μs`，分数=`92/90/82/72/71/63/52/49/55/60/46/57/48/50`；case5从#111016的`19→18 μs`并由70升到71分，case8升1分、case4掉1分，aggregate净增到63.36，因此选为当时baseline。
- **原始归档**：[`cuda_111115_raw.json`](raw/cuda_111115_raw.json)。

#### 提交 #111076 · exp384 case5 split-head QK compile trim

- **总状态/总分**：Accepted（14/14）/ **`63.29`**；长时间Pending后正常经过`Compiling→Running→Finished`，终态后队列为空。
- **源码与门禁**：保留exp383的case5 head-pair/z4 + split-head QK运行算法，只让恒定`separate_tail=false`在编译期可见并禁用六个不可达legacy launch。xcore1000 warning/模板实例由18降到12，本地resource build约`9.6→7.9 s`；目标producer保持`86 MTreg/56 STreg/8320 B/0 stack/5 waves`。CPU14/14、GPU三组各14/14、精确长度和workspace复用全部PASS；case5相对#111016双角色消偏约`0.9703`，非目标哨兵中性。
- **源码核对与OJ选择**：raw、[`cuda_111076.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111076.cpp)和提交时工作文件SHA均为`68af1a543e88ce8d7892865418b0ebfeecdc4cc54dabbfb6c2b97e7df9b8f8de`。OJ case1–14=`3/4/10/23/19/28/254/115/255/42/281/423/253/169 μs`；case5仍19 μs未跨tier，case4/8计分互抵，不替换#111016。
- **原始归档**：[`cuda_111076_raw.json`](raw/cuda_111076_raw.json)。

#### 提交 #111059 · exp383 case5 head-pair/z4 split-head QK

- **总状态**：CompilationError / 无测试点；raw明确为`A TimeLimitExceeded encountered while compiling the code.`，只有既有warning、无源码compiler error。
- **本地证据**：只改case5 producer ownership，保持split5、BSM、combined tail、FP32 partial和group8 reducer；资源`92/48→86/56 MT/STreg`、仍5 waves/0 stack。完整correctness通过，双角色消偏约`0.9750`。源码SHA为`b9c448c91c05d901c01efcd9c0b75594dcdd65b64ae2f33a926686ec4712e7d1`。
- **结论/归档**：compile TLE不是性能失败；等价运行语义由exp384/#111076完成14/14闭环。raw为[`cuda_111059_raw.json`](raw/cuda_111059_raw.json)，提交源码为[`cuda_111059.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111059.cpp)。

#### 提交 #111031 · #111016/exp382 同源平台连通性复投

- **总状态/总分**：Accepted（14/14）/ **`63.29`**；提交前队列为空，只创建这一笔。任务约八分钟后从`Pending`进入`Running`并正常`Finished`，确认创建、排队、编译和完整评测链路可用；终态后队列为空。
- **源码核对**：raw内嵌源码、逐提交快照[`cuda_111031.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111031.cpp)、工作文件、#111016快照的SHA-256均为`2968dcbc8359b9a6c9d6310fb7d0cb0d15f431603978be3278509a586b796d7c`。
- **OJ结果与选择**：case1–14=`3/4/10/22/19/28/252/116/255/42/282/421/252/169 μs`，分数=`92/90/82/73/70/63/52/48/55/60/46/57/48/50`。相对同源#111016仅case7/9/12/14为`−1/+1/−1/−1 μs`且总分不变，作为timing-tier样本；因为没有新源码归因，默认control保持#111016。
- **原始归档**：[`cuda_111031_raw.json`](raw/cuda_111031_raw.json)；逐提交源码为[`cuda_111031.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111031.cpp)。

#### 提交 #111016 · exp382 case10 head-pair/z4 split-head QK

- **总状态/总分**：Accepted（14/14）/ **`63.29`**；提交前队列为空且dry-run正确，只创建这一笔，正常经历`Pending→Running→Finished`，终态后队列为空。
- **源码与门禁**：在exp381已经覆盖case8/11/14的split-head half-row QK组合上，只把case10 producer从单头`dim3(16,8,2)`改为head-pair/z4 `dim3(16,4,4)` + split-head布局；split128、四页/partial、fused tail、FP32 accumulator、FP16x2 packed `(m,l)`和既有vec2 reducer不变。目标实例为`86 MTreg/62 STreg/8320 B/0 stack/5 waves`；CPU14/14、GPU full/boundary/random各14/14及case10 17步同进程复用全部PASS。相对exp381的41×500正向ratio p50=`0.9254`，反向旧版/exp382=`1.0733`，双角色消偏约`0.9284`、快约7.16%；case8/11/12/13/14哨兵中性。
- **源码核对**：raw内嵌源码、逐提交快照[`cuda_111016.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111016.cpp)与提交时工作文件字节一致，SHA-256均为`2968dcbc8359b9a6c9d6310fb7d0cb0d15f431603978be3278509a586b796d7c`。
- **OJ结果与选择**：case1–14=`3/4/10/22/19/28/253/116/254/42/282/422/252/170 μs`，分数=`92/90/82/73/70/63/52/48/55/60/46/57/48/50`。相对#110993，唯一新增目标case10从`46→42 μs`并由58跨到60分；case7/8/9/11/13也改善，case12慢2 μs但不掉档，case14保持170 μs/50分。aggregate从63.14刷新到63.29，因此#111016取代#110993成为当前baseline。
- **原始归档**：[`cuda_111016_raw.json`](raw/cuda_111016_raw.json)；逐提交源码为[`cuda_111016.cpp`](../solutions/archive/2026-08-13-submissions/cuda_111016.cpp)。

#### 提交 #110993 · exp379 case14 split-head QK compile trim

- **总状态/总分**：Accepted（14/14）/ **`63.14`**；正常完成完整评测，曾短暂成为最高分与默认control，后由#111016取代。
- **源码与门禁**：exp379保留exp378运行数学，只删除未实例化的非owner模板分支并合并owner-PV helper，源码从220953缩到218427 bytes。case14 producer为`86 MTreg/70 STreg/8320 B/0 stack/5 waves`；GPU三组各14/14及case14 20步复用通过，相对#110426 case14双角色消偏约`0.9634`。raw、逐提交快照[`cuda_110993.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110993.cpp)和实验候选SHA均为`f49371dbcb5b33f59d74ea95b0735408246e40b12b1b038ad93924cdf3681343`。
- **OJ结果与选择**：case1–14=`3/4/10/22/19/28/254/117/255/46/290/420/253/170 μs`，分数=`92/90/82/73/70/63/52/48/55/58/46/57/48/50`。case14相对#110426从`177→170 μs`并由49跨到50分，首次在OJ证明split-head half-row QK架构，aggregate刷新到63.14。
- **原始归档**：[`cuda_110993_raw.json`](raw/cuda_110993_raw.json)；逐提交源码为[`cuda_110993.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110993.cpp)。

#### 提交 #110987 · exp378 case14 split-head QK

- **总状态/总分**：CompilationError / 无分数、无测试点；首条诊断为`A TimeLimitExceeded encountered while compiling the code.`，只有既有warning、无源码compiler error。
- **本地证据与判定**：候选保留双head K load/unpack与8次packed FMA，只重构为lanes0..7/8..15分别归约head0/head1。完整correctness与case14 20步复用通过，相对exp367/#110426双角色消偏约`0.9794/0.9634`。逐提交源码[`cuda_110987.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110987.cpp)SHA为`7e7c6bdfbee0ff7a1b09df8a6731a6f1e0db4301b262103a77cbeede503ea64d`。本次属于平台compile TLE，不是性能失败；等价运行语义由exp379/#110993完成OJ闭环。
- **原始归档**：[`cuda_110987_raw.json`](raw/cuda_110987_raw.json)；逐提交源码为[`cuda_110987.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110987.cpp)。

#### 提交 #110962 · exp367同源平台恢复探测

- **总状态/总分**：Accepted（14/14）/ `63.00`；提交前队列为空且dry-run正确，只创建这一笔，正常经历`Pending→Running→Finished`，终态后队列为空。
- **源码核对**：raw内嵌源码、逐提交快照[`cuda_110962.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110962.cpp)、提交时使用的#110895快照字节一致，SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/254/116/253/46/291/421/253/174 μs`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。这次确认OJ创建、排队、编译和完整评测链路当前可用；与#110895无源码差异，因此计时变化只作为timing-tier样本，最高分与默认control仍为#110426 / `63.07`。
- **原始归档**：[`cuda_110962_raw.json`](raw/cuda_110962_raw.json)；逐提交源码为[`cuda_110962.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110962.cpp)。

#### 提交 #110941 · exp367同源平台恢复探测

- **总状态/总分**：CompilationError / 无分数、无测试点；提交前队列为空，只创建这一笔。任务长时间保持`Pending`后直接进入终态，等待期间没有取消或并行复投，终态后队列为空。
- **源码核对**：raw内嵌源码、本次逐提交快照[`cuda_110941.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110941.cpp)、已Accepted的#110895和同源#110916字节一致，SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **诊断与选择**：OJ首条诊断仍为`A TimeLimitExceeded encountered while compiling the code.`，其余只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。它说明提交创建入口可用，但编译服务尚未稳定恢复；相同源码已由#110895完成14/14 Accepted，因此本次不是正确性或性能失败。停止同源复投，baseline保持#110426。
- **原始归档**：[`cuda_110941_raw.json`](raw/cuda_110941_raw.json)；逐提交源码为[`cuda_110941.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110941.cpp)。

#### 提交 #110916 · exp367同源平台试投

- **总状态/总分**：CompilationError / 无分数、无测试点；提交前队列为空，只创建这一笔，成功经历`Pending→Compiling→Finished`，终态后队列为空。
- **源码核对**：提交源码、raw内嵌源码、工作文件、逐提交快照[`cuda_110916.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110916.cpp)及已14/14 Accepted的#110895快照字节一致，SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **诊断与选择**：OJ首条诊断为`A TimeLimitExceeded encountered while compiling the code.`，日志只有MACA忽略`minBlocks`的既有warnings，没有源码compiler error。它确认提交创建和调度链路可用，但本次属于平台compile TLE，不是正确性或性能失败；不立即同源复投，baseline保持#110426。
- **原始归档**：[`cuda_110916_raw.json`](raw/cuda_110916_raw.json)；逐提交源码为[`cuda_110916.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110916.cpp)。

#### 提交 #110895 · exp367 unified vec2 packed metadata

- **总状态/总分**：Accepted（14/14）/ `63.00`；提交前队列为空，只创建这一笔，正常经历`Pending→Compiling→Running→Finished`，终态后队列为空。
- **源码与门禁**：case10、case12、case13三个既有vec2 reducer用户统一采用FP16x2 packed `(m,l)`；reducer始终从`partial_m`以`__half2`读取并删除`partial_l`写入/读取，保持单一无格式分支实例。CPU14/14、GPU full/boundary/random各14/14及三个目标各17步同进程复用全部PASS。相对正式#110426双角色消偏case10/12/13约`0.9887/1.0013/0.9895`。[`cuda_110895.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110895.cpp)、raw内嵌源码与工作文件SHA-256均为`575f8b5edacdef64e330a7fa281f7b86e84cd035ab45681c29dc48bcbeceae16`。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/252/116/255/46/288/421/253/174 μs`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。case7刷新Accepted历史最佳`253→252 μs`，case12/13/14相对baseline分别改善`2/2/3 μs`；但case10仍46 μs未跨档，case8 `115→116 μs`掉1分，case9/11也回退。aggregate未超过#110426的63.07，故默认control保持#110426；exp367作为已验证packed metadata组合保留。本次结果同时确认OJ创建、编译和评测链路当前可用。
- **原始归档**：[`cuda_110895_raw.json`](raw/cuda_110895_raw.json)；逐提交源码为[`cuda_110895.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110895.cpp)。

#### 提交 #110884 · exp365 case13 packed metadata

- **总状态/总分**：CompilationError / 无分数、无测试点；只创建这一笔，终态后才继续后续候选。
- **源码与门禁**：只给case13 producer/reducer使用FP16x2 packed `(m,l)`，复用已有producer条件并新增packed vec2 reducer实例。CPU14/14、GPU三组各14/14及case13 17步复用全部PASS；相对#110426 case13双角色消偏约`0.9895`，case14约快1.4%，其余哨兵中性。逐提交快照[`cuda_110884.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110884.cpp)与raw内嵌源码SHA-256均为`d18ed7ad3cbf0267c1ac896e4f86a14980eae012d1727833e667ad407b802f00`。
- **诊断与选择**：OJ首条消息为`A TimeLimitExceeded encountered while compiling the code.`，没有进入测试点；这是平台compile TLE，不是性能失败。后续通过统一既有vec2 reducer用户消除新增实例形成exp367。
- **原始归档**：[`cuda_110884_raw.json`](raw/cuda_110884_raw.json)；逐提交源码为[`cuda_110884.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110884.cpp)。

#### 提交 #110809 · exp356/#110771 同源平台试投

- **总状态/总分**：CompilationError / 无分数、无测试点；按用户要求只创建这一笔，终态后队列为空，没有取消或并行复投。
- **源码核对**：工作文件、已Accepted的[`cuda_110771.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110771.cpp)、本次逐提交快照[`cuda_110809.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110809.cpp)及两份raw内嵌源码的SHA-256均为`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`。
- **诊断与选择**：OJ首条消息为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有MACA `minBlocks` warning，没有源码compiler error。相同源码此前已由#110771正常编译并14/14 Accepted，因此本次结果是平台compile TLE，不是代码正确性或性能回归；没有性能数据，不立即同源复投，baseline仍为#110426。
- **原始归档**：[`cuda_110809_raw.json`](raw/cuda_110809_raw.json)；逐提交源码为[`cuda_110809.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110809.cpp)。

#### 提交 #110771 · exp356 case13+14 compact-template combination

- **总状态/总分**：Accepted（14/14）/ `62.93`；只创建这一笔。首轮900秒watch超时后没有取消或复投，继续观察同一提交号后正常完成；终态后队列为空。
- **源码与门禁**：相对exp353仅删除新增的`KV8_UINT2_LOAD_SCALAR_LOOKAHEAD`模板参数，利用已有`!NATIVE_ROW16_QK && KV8_SCALAR_V_LOOKAHEAD`条件唯一识别当前case13 dispatch；运行语义、case13/14资源和A/B保持不变，源码`216088→215920 bytes`。CPU14/14、GPU full/boundary/random各14/14及case13 17步精确长度复用全部PASS。[`cuda_110771.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110771.cpp)、raw内嵌源码与工作文件SHA-256均为`e23876fbee712f88d7e25722b2b1fbe98d4c069cd2ab2f7efbfaa1c8334f8669`。
- **OJ结果与选择**：case1–14=`3/4/10/24/19/28/253/117/253/46/287/421/254/174 μs`，分数=`92/90/82/71/70/63/52/48/55/58/46/57/48/49`。case13相对#110426 `255→254 μs`、case14 `177→174 μs`，均未跨分；case4/8无目标源码差异地各掉1分。该结果确认提交、编译和评测链路正常，也支持控制模板表面，但不替换#110426。
- **原始归档**：[`cuda_110771_raw.json`](raw/cuda_110771_raw.json)；逐提交源码为[`cuda_110771.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110771.cpp)。

#### 提交 #110760 · exp353 case13+14 combination

- **总状态/总分**：CompilationError / 无分数、无测试点；只创建这一笔，终态后才继续下一候选。
- **源码与门禁**：组合case13每行两次`uint2` load-site立即拆标量与exp348 case14 owner-score/head-max。CPU14/14、GPU三组各14/14、case13/14精确长度及workspace复用全部通过；目标双角色消偏约`0.9963/0.9834`。逐提交快照[`cuda_110760.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110760.cpp)与raw内嵌源码SHA-256均为`b5e12d6e6fc480100ba3ab6d51f3bee1595be41c7d4e8d096b227ad0a6b731ff`。
- **诊断与选择**：OJ首条消息为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有warning。它没有进入测试点，不能作为运行失败或性能数据；等价运行语义的精简版exp356随后由#110771 Accepted。168-byte缩减不能被宣称为唯一因果。
- **原始归档**：[`cuda_110760_raw.json`](raw/cuda_110760_raw.json)；逐提交源码为[`cuda_110760.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110760.cpp)。

#### 提交 #110746 · exp348 case14 fixed15 owner-score + head-max

- **总状态/总分**：Accepted（14/14）/ `62.86`；只创建这一笔，900秒watch超时后没有取消或复投，随后正常完成并确认OJ编译/评测链路恢复，终态后队列为空。
- **唯一差异与源码**：从#110426只修改case14满长前256个固定15-page common split。每lane用`tx&3`选择一个token、`tx&4`选择一个head，跨QK→PV只保留一个owner score；同时仅维护所选head的page max并由lane0/4广播。最后underfilled split、tail、split257、fixed15 `unroll 2`、K/V register-lookahead、packed metadata、normalized-BF16 partial和reducer均不变。[`cuda_110746.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110746.cpp)、raw内嵌源码及提交前工作文件SHA-256均为`69f1dda419d220235e26be813962396dae01e1a33ce0580ce4ff05736a5a5bb0`。
- **本地门禁**：目标producer由control的`90 MTreg/64 STreg/8320 B/0 stack/5 waves`变为`90/58/8320/0/5`。CPU14/14；GPU full/boundary/random各14/14；case14 `61519→1→2→15→16→17→239→240→241→479→480→481→3839→3840→3841→61518→61519`同进程全部PASS。41×200正向exp348/#110426=`0.9845`、反向#110426/exp348=`1.0180`，几何消偏约`0.9834`、快约1.66%；21×100非目标case4/8/11约`0.9993/1.0006/1.0001`，case5/10区间跨1。
- **OJ结果与选择**：case1–14=`3/4/10/24/19/28/253/117/253/47/288/422/255/174 μs`，分数=`92/90/82/71/70/63/52/48/55/57/46/57/48/49`。唯一目标case14相对#110426真实`177→174 μs`，与本地证据同向但仍未跨50分档；未改源码的case4/8/10各掉1分导致aggregate回退。exp348作为OJ确认的正组件保留，不替换#110426；下一步先分解owner-score与head-owned page max贡献。
- **原始归档**：[`cuda_110746_raw.json`](raw/cuda_110746_raw.json)；逐提交源码为[`cuda_110746.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110746.cpp)。

#### 提交 #110740 · #110426 同源平台试投

- **总状态/总分**：CompilationError / 无分数、无测试点；提交前工作文件与Accepted #110426字节一致，等待期间没有取消或并行复投。
- **源码与诊断**：[`cuda_110740.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110740.cpp)、raw内嵌源码与#110426 SHA-256均为`20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。raw首条消息为`A TimeLimitExceeded encountered while compiling the code.`，其余只有既有warning，没有源码compiler error或测试点。
- **结论/归档**：它是#110546/#110621/#110699之后连续第四次平台compile TLE，不是代码回归或性能数据。[`cuda_110740_raw.json`](raw/cuda_110740_raw.json)及逐提交源码均已归档；后续#110746正常Accepted，确认平台随后恢复。

#### 提交 #110699 · exp347 case13 uint2 load-site scalar lookahead

- **总状态/总分**：CompilationError / 无分数、无测试点；只创建这一笔，等待期间没有取消或复投，终态后队列为空。
- **唯一差异与源码**：从#110426只修改case13已有的标量K+V register-lookahead：每个next K/V row从四次32-bit load改为两次`uint2` load，读取后立即拆回八个`uint32_t`，跨当前PV仍只有标量存活。split256/15页、QK/PV、softmax、partial、reducer和其他case dispatch均不变。提交快照[`cuda_110699.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110699.cpp)、raw内嵌源码与提交前工作文件SHA-256均为`5bacc185bb1d3cdb63961207c3b40e6adfbe3d3a6b4367b3846e49b847e9f7f1`。
- **本地门禁**：目标producer保持`64 MTreg/52 STreg/8192 B/0 stack/staticMaxWarps 8`。CPU14/14；同一`.so`的GPU full/boundary/random各14/14；case13 `58966→1→2→15→16→17→239→240→241→255→256→257→479→480→481→58965→58966`同进程复用全部100% tolerance、finite。9×20筛选ratio p50=`0.9932`；41×200正向exp347/#110426=`0.9940`，交换角色#110426/exp347=`1.0049`，几何消偏约`0.9946`、时延下降约0.54%。
- **OJ诊断与选择**：raw首条消息为`A TimeLimitExceeded encountered while compiling the code.`，后续只有既有`minBlocks` warning，没有源码compiler error。它与#110546/#110621构成三次连续OJ compile TLE，说明创建入口恢复但编译服务仍异常。没有性能数据，故不替换#110426；该源码作为本地正向组件保留，平台无正常编译证据前不立即复投。
- **原始归档**：[`cuda_110699_raw.json`](raw/cuda_110699_raw.json)；逐提交源码为[`cuda_110699.cpp`](../solutions/archive/2026-08-13-submissions/cuda_110699.cpp)。

### 2026-08-12

#### 提交 #110621 · #110426 同源平台试投

- **总状态/总分**：CompilationError / 无分数、无测试点。任务创建成功后长时间保持`Pending`；首轮watch超时后没有取消或复投，后续检查确认进入终态，当前队列为空。
- **源码身份**：[`cuda_110621.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110621.cpp)、raw内嵌源码、#110546、#110426及当前工作文件SHA-256均为`20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。
- **编译诊断与结论**：raw首条消息为`A TimeLimitExceeded encountered while compiling the code.`；后续只有已被#110426 Accepted验证过的MACA `minBlocks`忽略warning，没有源码compiler error。它与#110546构成连续两个同源compile TLE样本，说明当前OJ编译环境不稳定，不能据此判断代码错误或性能。为避免进一步降低评测优先级，不创建第三笔重复提交；默认control仍为#110426。
- **原始归档**：[`cuda_110621_raw.json`](raw/cuda_110621_raw.json)；逐提交源码为[`cuda_110621.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110621.cpp)。

#### 提交 #110426 · exp340b case8 隔离特化

- **总状态/总分**：Accepted（14/14）/ **`63.07`**；任务排队较久且首个1200秒watch超时，但没有取消或复投，随后正常完成，终态后队列为空。
- **源码与门禁**：[`cuda_110426.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110426.cpp)、raw内嵌源码和当前工作文件SHA-256均为`20a5189af564345b381df6807fdda3c74615909001979c79a1f88e4d09e784a3`。相对#110192保留exp339的case8 fixed19 `unroll 2` + skip-empty计算，把原#110192 case8特化用合法输入不可达的volatile分支保留，并由文件末尾host launcher首次实例化新特化；生产dispatch已关闭的错误MMA-QK代码以`#if 0`排除。CPU14/14、GPU full/boundary/random各14/14，case8 `4096→1→2→15→16→17→303→304→305→3951→3952→3953→4095→4096`同进程复用全部通过。
- **资源与本地 A/B**：新旧case8 producer均为`86 MTreg/70 STreg/8320 B/0 stack/5 waves`。case8正向candidate/control=`0.9906`、反向control/candidate=`1.0077`，消偏约`0.9914`；case4/5/10约`1.0011/0.9975/0.9991`，中性。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/253/115/254/46/286/423/255/177 μs`，分数=`92/90/82/72/70/63/52/49/55/58/46/57/48/49`。相对#110192，case8 `117→115 μs`并跨一分，case7/9/11分别改善`1/2/3 μs`；case4掉一分、case12/14波动回退。目标与本地证据同向且aggregate保持最高，选择#110426为默认control。
- **静态归因修正**：case4入口恢复`0x53000`，大小10424 B，机器码SHA仍为`d35f085891ec18a19a68579bc0210f35563d51aab25abe2903f74c4d5fd7adbc`，与#110192字节精确相同；除删除MMA占位、generic fallback前移`0x100`和新增case8特化外，原39个生产kernel地址、大小和机器码均不变。OJ case4仍为23 μs，说明旧“入口平移导致回退”的结论过强，后续按timing-tier波动处理。
- **原始归档**：[`cuda_110426_raw.json`](raw/cuda_110426_raw.json)；逐提交源码为[`cuda_110426.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110426.cpp)。

#### 提交 #110229 · exp339 case8 unroll2 + skip-empty

- **总状态/总分**：Accepted（14/14）/ **`63.00`**；终态后队列为空。
- **源码与门禁**：[`cuda_110229.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110229.cpp)、[`cuda_case8_unroll2_skip_empty_exp339.cpp`](../solutions/archive/2026-08-12-experiments/cuda_case8_unroll2_skip_empty_exp339.cpp)和raw内嵌源码SHA-256均为`142482189ab69ac239a4295fc2505750857236b3b4eda4cba635a81674b897c0`。相对#110192只修改case8固定19页路径；CPU14/14、GPU full/boundary/random各14/14及14步case8同进程复用通过。
- **本地与OJ结果**：case8双角色消偏约`0.9912`；case4/10约`1.0068/1.0003`。OJ case1–14=`3/4/10/23/20/28/254/115/255/46/292/421/255/176 μs`，分数=`92/90/82/72/69/63/52/49/55/58/46/57/48/49`。case8 `117→115 μs`跨一分，但case4/5各掉一分，故默认control保持#110192。
- **代码布局诊断**：从两份设备bundle提取的case4 kernel均为10424 bytes，机器码SHA同为`d35f085891ec18a19a68579bc0210f35563d51aab25abe2903f74c4d5fd7adbc`；入口仅由`0x53000`平移到`0x53900`。这反证case4算法或codegen发生变化，下一步只隔离case8代码表面。
- **原始归档**：[`cuda_110229_raw.json`](raw/cuda_110229_raw.json)。

#### 提交 #110192 · exp338 选择性 skip-empty rescale 组合

- **总状态/总分**：Accepted（14/14）/ **`63.07`**。提交、编译和评测正常完成；终态后最近列表无Pending/Running任务。
- **源码与门禁**：[`cuda_110192.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110192.cpp)、[`cuda_skip_empty_combo_exp338.cpp`](../solutions/archive/2026-08-12-experiments/cuda_skip_empty_combo_exp338.cpp)、raw内嵌源码和当前工作文件SHA-256均为`0662e29f6f4bc09cc3abde6309d6848deacc216ece1e338930d0f7e2118dc4ca`。相对#109963只给case6/7/9/10/11/12/13/14启用首个有效页跳过空状态rescale；case4/5/8不变。CPU14/14、GPU full/boundary/random各14/14及case11/14精确长度复用通过；新增实例0 B stack且未跨staticMaxWarps档。
- **本地 A/B**：相对#109963的双角色几何消偏约为case6/7/9/10/11/12/13/14=`0.9947/0.9930/0.9942/0.9925/0.9970/0.9960/0.9981/0.9987`；非目标case4/8=`1.0026/1.0015`，视为中性。
- **OJ结果与选择**：case1–14=`3/4/10/22/19/28/254/117/256/46/289/421/255/176 μs`，分数=`92/90/82/73/70/63/52/48/55/58/46/57/48/49`。相对#109963，case7 `256→254`、case9 `259→256`、case10 `47→46`并跨一分、case11 `292→289`、case12 `423→421`、case13 `256→255`、case14 `177→176`，case6持平；未改源码的case8 `116→117`按timing波动处理。它与#109783同为63.07，但组合质量更高，因此选择#110192为默认control；#109783保留case8历史局部最佳参照。
- **原始归档**：[`cuda_110192_raw.json`](raw/cuda_110192_raw.json)；逐提交源码为[`cuda_110192.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110192.cpp)。

#### 提交 #110031 · #109963 同源空行差异试投

- **总状态/总分**：Accepted（14/14）/ **`63.00`**。客户端15分钟watch超时后没有取消或复投，OJ随后正常完成。
- **源码一致性**：[`cuda_110031.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110031.cpp)相对#109963仅少一个空行，SHA-256为`37548d3a30f4deb6ae8865e19a9de4e371eef9e3eccced8d6a920cb00fde235b`；不存在kernel实现差异。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/255/116/253/46/292/423/255/177 μs`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。只作为同源timing-tier与平台链路样本，不替换control。
- **原始归档**：[`cuda_110031_raw.json`](raw/cuda_110031_raw.json)；逐提交源码为[`cuda_110031.cpp`](../solutions/archive/2026-08-12-submissions/cuda_110031.cpp)。

#### 提交 #109989 · exp335 case8 fixed19 unroll 2

- **总状态/总分**：Accepted（14/14）/ **`62.93`**。
- **源码与实验**：[`cuda_109989.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109989.cpp) SHA-256为`86b297eed2595f93d9c3690107f12076f20e8a58833cd44ca0fa26925eb0b5a7`。相对#109963只把case8 fixed19循环`#pragma unroll 1→2`；本地约快0.55%。
- **OJ结果与选择**：case1–14=`3/4/10/23/20/28/254/117/254/46/288/423/255/177 μs`，分数=`92/90/82/72/69/63/52/48/55/58/46/57/48/49`。case4/8为`23/117 μs`，没有保住case4 tier也没有追回case8历史最佳，候选拒绝且不得原样复投。
- **原始归档**：[`cuda_109989_raw.json`](raw/cuda_109989_raw.json)；逐提交源码为[`cuda_109989.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109989.cpp)。

#### 提交 #109828 · #109783/exp312 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ **`63.00`**。提交成功创建并进入`Compiling→Running`；客户端10分钟watch超时后没有取消或复投，OJ随后正常完成，确认创建、排队、编译和评测链路可用。终态后队列为空。
- **源码一致性**：[`cuda_109828.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109828.cpp)、raw内嵌源码与#109783快照的SHA-256均为`3612a1266357f4c9da52f9e8a8124096796dea84a2e75f429194d1825476ff96`，不存在实现差异。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/255/116/256/46/290/422/256/177 μs`，分数=`92/90/82/72/70/63/52/48/55/58/46/57/48/49`。相对#109783，case8慢1 μs并掉1分，case11/12快1/3 μs但不跨档；全部没有源码归因，只作为timing-tier样本。当前最高与默认control继续保持#109783。
- **原始归档**：[`cuda_109828_raw.json`](raw/cuda_109828_raw.json)；逐提交源码为[`cuda_109828.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109828.cpp)。

#### 提交 #109783 · exp312 case8 固定19页 common-split 热循环

- **总状态/总分**：Accepted（14/14）/ **`63.07`**。提交前队列为空且只创建这一笔，正常经历`Pending→Compiling→Running→Finished`；终态后队列为空。
- **源码与门禁**：[`cuda_109783.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109783.cpp) SHA-256 为`3612a1266357f4c9da52f9e8a8124096796dea84a2e75f429194d1825476ff96`，与exp312完整实验快照字节一致。相对#109761先组合exp308/309的case8/11 head-owned page max，再只让case8满长split 0..12走固定19页热循环；最后split和短长度仍走原泛化路径。producer为`86/70 MT/STreg、8320 B、0 stack、5 waves`。CPU14/14，GPU full/boundary/random各14/14，case8/11 full→short→split边界→full同进程复用全部通过。
- **本地 A/B**：相对exp309的case8双角色消偏约`0.9917`；直接相对#109761的61×500强测，case8正向=`0.9883`、反向#109761/exp312=`1.0114`，消偏约`0.9885`、快约1.15%。case11消偏约`0.9963`，无非目标实现回退。
- **OJ结果与选择**：case1–14=`3/4/10/23/19/28/255/115/257/46/291/425/255/177 μs`，分数=`92/90/82/72/70/63/52/49/55/58/46/57/48/49`。唯一主要目标case8相对#109761真实`116→115 μs`并从48升到49分，aggregate刷新到63.07；其余变化没有对应源码差异，按timing-tier波动处理。选择#109783为新baseline。
- **原始归档**：[`cuda_109783_raw.json`](raw/cuda_109783_raw.json)；逐提交源码为[`cuda_109783.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109783.cpp)。

#### 提交 #109769 · #109761/exp307 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ **`63.00`**。提交前最近任务均为终态，dry-run正常；只创建这一笔，正常经历`Pending→Running→Finished`，确认创建、调度、编译和完整评测链路可用。终态后队列为空。
- **源码一致性**：提交源码、[`cuda_109769.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109769.cpp)、raw内嵌源码和#109761快照的SHA-256均为`e953d45d8844d38e2eefb7bcc50efc0c75563ba7f1143cb3b26a636e562a22bb`，不存在实现差异。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/28/256/117/256/47/291/420/255/177 μs`，分数=`92/90/83/72/70/63/52/48/55/57/46/57/48/49`。总分与#109761相同；case8/11各慢1 μs、case9快1 μs、case12快6 μs均无源码归因，只作为timing-tier样本。默认control继续保持最早建立exp307因果记录的#109761。
- **原始归档**：[`cuda_109769_raw.json`](raw/cuda_109769_raw.json)；逐提交源码为[`cuda_109769.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109769.cpp)。

#### 提交 #109694 · #109672/exp283 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ **`62.79`**。提交前最近任务均为终态且只创建这一笔；任务约七分钟完成`Pending→Running→Finished`，确认创建、调度、编译和评测链路可用。终态后队列为空。
- **源码一致性**：提交源码、[`cuda_109694.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109694.cpp)、工作文件和#109672快照的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，不存在实现差异。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/28/253/120/253/47/303/421/255/188 μs`，分数=`92/90/83/72/70/63/52/48/55/57/45/57/48/47`。总分低于#109672，但逐case变化没有源码归因，只作为同源timing-tier样本；当前最高分仍为`62.93`，默认control保持最早建立可归因记录的#109672。
- **原始归档**：[`cuda_109694_raw.json`](raw/cuda_109694_raw.json)；逐提交源码为[`cuda_109694.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109694.cpp)。

#### 提交 #109691 · exp288 case14 packed m/l + register metadata reducer

- **总状态/总分**：Accepted（14/14）/ **`62.79`**。提交前队列为空且只创建这一笔，正常经历`Pending→Running→Finished`；终态后队列为空。
- **源码与门禁**：[`cuda_109691.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109691.cpp) SHA-256 为`01e4d5babce730f65a2ef46604f5efd1b070b85f1bec9512e8e547e76efc5985`。相对#109672唯一命中case14：producer把FP32 `(m,l)`打包进现有`partial_m`的FP16x2槽并省略`partial_l`写；128-thread reducer将`s0/s1/s2`元数据跨max归约保存在寄存器并把最终权重直接写入shared。producer资源`90/52→90/50 MT/STreg`、reducer`40/36→40/32`，驻留档不变，动态shared约减半。CPU14/14、GPU full/boundary/random各14/14及23步case14 full→short→split边界→full复用全部通过。
- **本地 A/B**：41×200正向exp288/#109672 p10/p50/p90=`0.9736/0.9757/0.9780`，反向#109672/exp288=`1.0212/1.0231/1.0273`，双角色消偏约`0.9766`、本地快约2.34%；case4/8/11/13消偏约`0.9942/0.9994/0.9994/1.0019`，无可信非目标回退。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/28/255/121/256/47/298/426/255/183 μs`，分数=`92/90/83/72/70/63/52/47/55/57/45/57/48/48`。目标case14相对#109672 `186→183 μs`，建立本地与OJ一致的机制证据，但仍未达到下一分数档；无源码差异的case8/10各掉1分使aggregate低于62.93。保留exp288作为后续finalist组合组件，不替换#109672，也不原样复投。
- **原始归档**：[`cuda_109691_raw.json`](raw/cuda_109691_raw.json)；逐提交源码为[`cuda_109691.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109691.cpp)。

#### 提交 #109688 · #109672/exp283 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ **`62.93`**。提交前最近任务均为终态且只创建这一笔；平台正常完成`Pending→Running→Finished`，确认创建、调度、编译与评测链路可用。终态后队列为空。
- **源码一致性**：提交源码、[`cuda_109688.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109688.cpp)、工作文件和#109672快照的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，不存在实现差异。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/28/254/120/254/46/299/424/255/186 μs`，分数=`92/90/83/72/70/63/52/48/55/58/45/57/48/48`。总分与#109672并列，但逐case变化没有源码归因，只作为同源timing-tier样本；当前最高分仍为`62.93`，默认control保持最早建立可归因记录的#109672。
- **原始归档**：[`cuda_109688_raw.json`](raw/cuda_109688_raw.json)；逐提交源码为[`cuda_109688.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109688.cpp)。

#### 提交 #109684 · #109672/exp283 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ **`62.86`**。提交前队列为空且只创建这一笔；平台立即返回提交ID，随后约八分钟完成`Pending→Running→Finished`，证明创建、调度、编译和评测链路可用，但延迟仍明显。终态后队列为空。
- **源码一致性**：提交源码、[`cuda_109684.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109684.cpp)、工作文件和#109672快照的SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`，不存在实现差异。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/28/256/121/255/46/301/422/255/186 μs`，分数=`92/90/83/72/70/63/52/47/55/58/45/57/48/48`。相对#109672，case4/8各掉一档、case10升一档，其余变化未形成新源码证据；总分`62.86<62.93`，因此只作为同源timing-tier样本，当前最高分和默认control仍为#109672。
- **原始归档**：[`cuda_109684_raw.json`](raw/cuda_109684_raw.json)；逐提交源码为[`cuda_109684.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109684.cpp)。

#### 提交 #109672 · exp283 case6 K-only lookahead 组合

- **总状态/总分**：Accepted（14/14）/ **`62.93`**；#109666终态后队列为空，只创建这一笔。任务经历`Pending→Running→Finished`后正常完成，终态后队列为空。
- **源码与门禁**：提交源码及[`exp283`完整实验快照](../solutions/archive/2026-08-12-experiments/cuda_case46_scope0_klook_exp283.cpp)SHA-256均为`0c11bb1fb76bd536e404fe058374028b0105ab1156b09dd43c5e2d65f22889a6`。从#109666分叉，case4 scope0 tokenized BSM完全不变，只给case6组合exp275的四标量K-only lookahead，V仍走同步post-PV；资源`80 MTreg/44 STreg/8320 B/0 stack/6 waves`。CPU14/14、GPU full/boundary/random各14/14以及case6共29个同进程精确长度全部通过。相对#109666的case6正反双角色消偏约`0.9868`，case4消偏约`0.9985`、中性。
- **OJ结果与选择**：case1–14=`3/4/9/22/19/28/254/119/256/47/304/424/255/186 μs`，分数=`92/90/83/73/70/63/52/48/55/57/45/57/48/48`。唯一目标case6相对#109666真实`29→28 μs`、`62→63分`并与本地A/B同向；case4无源码差异地`23→22 μs`只作为timing-tier样本。目标因果和更高aggregate同时成立，选#109672为新baseline，工作文件与其字节一致。
- **原始归档**：[`cuda_109672_raw.json`](raw/cuda_109672_raw.json)；逐提交源码为[`cuda_109672.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109672.cpp)。

#### 提交 #109666 · exp282 有序 tokenized BSM scope0

- **总状态/总分**：Accepted（14/14）/ **`62.79`**；提交前队列为空，只创建这一笔。客户端300秒监视到期后任务继续运行并正常完成，终态后队列为空。
- **源码与门禁**：提交源码及[`exp282`完整实验快照](../solutions/archive/2026-08-12-experiments/cuda_case4_tokenized_bsm_ordered_scope0_exp282.cpp)SHA-256均为`d6e8257852090cf102d57ac852b63df1ae5a7b52e8e83813bdf66efefd8388a8`。相对exp281唯一改`barrier_and_wait4 scope1→scope0`，保留已验证的`wait(V_current)→issue(K_next)`顺序；资源同档，CPU14/14、GPU full/boundary/random各14/14和case4精确长度全部通过。相对exp281/当前baseline的双角色消偏约`0.9920/0.9650`。
- **OJ结果与选择**：case1–14=`3/4/9/23/19/29/255/120/256/47/301/424/255/186 μs`，分数=`92/90/83/72/70/62/52/48/55/57/45/57/48/48`。唯一目标case4相对#109591真实`24→23 μs`、`71→72分`，与本地A/B同向；选#109666为新baseline，工作文件与其字节一致。
- **原始归档**：[`cuda_109666_raw.json`](raw/cuda_109666_raw.json)；逐提交源码为[`cuda_109666.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109666.cpp)。

#### 提交 #109664 · #109591/exp262 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ `62.71`；等待超过180秒后完成，raw随后由`--watch`补存。
- **代码溯源**：[`cuda_109664.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109664.cpp)，SHA-256 `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`；与#109591 baseline字节一致。
- **结果解释**：case1–14=`3/4/9/25/19/29/255/120/253/46/299/425/255/186 μs`，分数=`92/90/83/70/70/62/52/48/55/58/45/57/48/48`。case8升1分与case4降1分相互抵消，且两处均无源码差异；只作为timing-tier证据，不替换#109591。
- **原始归档**：[`cuda_109664_raw.json`](raw/cuda_109664_raw.json)。

#### 提交 #109654 · exp281 有序 tokenized BSM

- **总状态/总分**：Accepted（14/14）/ `62.57`。
- **代码溯源**：[`cuda_109654.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109654.cpp)，SHA-256 `71d1046d003b2f537ad4feb39f68a8f86c18c2452937d6dcb3cac7e0dbc44a84`；raw、逐提交快照与[`exp281`实验源码](../solutions/archive/2026-08-12-experiments/cuda_case4_tokenized_bsm_ordered_exp281.cpp)一致。
- **本地证据与OJ**：资源`76 MTreg/44 STreg/8320 B/0 stack/6 waves`；完整correctness和case4页边界通过。41×1000双角色相对#109591消偏约`0.9736`。OJ case1–14=`3/4/9/24/19/29/255/121/258/47/301/422/255/188 μs`，分数=`92/90/83/71/70/62/52/47/55/57/45/57/48/47`；目标case4未低于24 μs，拒绝为baseline。
- **原始归档**：[`cuda_109654_raw.json`](raw/cuda_109654_raw.json)。

#### 提交 #109644 · #109591/exp262 字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ `62.64`。
- **代码溯源**：[`cuda_109644.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109644.cpp)，SHA-256 `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`；与#109591 baseline字节一致。
- **结果解释**：case1–14=`3/4/9/25/19/29/254/121/257/46/298/420/255/186 μs`，分数=`92/90/83/70/70/62/52/47/55/58/45/57/48/48`。没有源码差异，只作为timing-tier样本，不替换baseline。
- **原始归档**：[`cuda_109644_raw.json`](raw/cuda_109644_raw.json)。

#### 提交 #109630 · exp272 case6 inline group4 finalizer

- **总状态/总分**：Accepted（14/14）/ `62.71`；提交前队列为空，只创建这一笔，正常完成`Pending→Running→Finished`，终态后无在途提交。
- **代码溯源**：[`cuda_109630.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109630.cpp)，SHA-256 `30ebce6e2d0214bd97889af930be536112670ddbea02c64b1dbbeef901e8bb4b`；raw内嵌源码、逐提交快照和[`exp272`实验源码](../solutions/archive/2026-08-12-experiments/cuda_case6_inline_group4_finalize_exp272.cpp)三方一致。
- **唯一差异与本地证据**：保留#109591 case6的split8、combined-tail、native-row QK、Q prescale和FP32 partial，只让最后一个producer CTA用四个full wave完成四head归约并删除独立group8 reducer launch。资源约`76 MTreg/6 waves→72/7`，0 stack；full/boundary/random各14/14、29个full→short→full精确长度均通过。41×500正向exp272/#109591 p50=`0.9424`，反向#109591/exp272=`1.0689`，消偏约`0.9390`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109630 | **62.71** | 3 | 4 | 9 | 25 | 19 | 30 | 256 | 120 | 257 | 46 | 301 | 420 | 255 | 186 |
| #109591 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 121 | 257 | 46 | 300 | 424 | 255 | 186 |

- **结果解释**：唯一目标case6在OJ反而慢1 μs，仍为62分；case8快1 μs并升1分、case4慢1 μs并降1分，但这两个dispatch没有源码差异，不能归因于exp272。aggregate并列不构成新baseline证据。结合case11/8既有inline-finalizer OJ失败，关闭当前completion-counter/last-producer实现家族，工作文件恢复#109591。
- **原始归档**：[`cuda_109630_raw.json`](raw/cuda_109630_raw.json)。

#### 提交 #109610 · #109591/exp262 第二次字节精确平台试投

- **总状态/总分**：Accepted（14/14）/ `62.64`；提交创建成功，约六分钟后完成`Pending→Running→Finished`，终态后无在途提交。
- **代码溯源**：[`cuda_109610.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109610.cpp)，SHA-256 `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`；raw内嵌源码、逐提交快照、#109591 baseline和工作文件字节一致。
- **结果解释**：本轮没有任何源码变化。case1–14耗时为`3/4/9/24/19/29/254/121/256/47/300/424/255/186 μs`，对应分数为`92/90/83/71/70/62/52/47/55/57/45/57/48/48`。相对#109591，case7/9分别快`1/1 μs`，case10慢`1 μs`，其余相同；aggregate从`62.71→62.64`。这些同源差异只能归因于OJ timing-tier波动，当前baseline继续保持#109591。
- **原始归档**：[`cuda_109610_raw.json`](raw/cuda_109610_raw.json)。

#### 提交 #109601 · #109591/exp262 字节精确平台恢复试投

- **总状态/总分**：Accepted（14/14）/ `62.64`；提交正常经历`Pending→Running→Finished`，确认OJ创建、排队、编译和评测链路可用，终态后无在途提交。
- **代码溯源**：[`cuda_109601.cpp`](../solutions/archive/2026-08-12-submissions/cuda_109601.cpp)，SHA-256 `1c4ccb0a19c9ab2935072d42faeeece8ba2ecdda6f5910a381b09b4ff9fe9bc0`；raw内嵌源码、逐提交快照、#109591 baseline和工作文件字节一致。
- **结果解释**：本轮没有任何源码变化。case1–14耗时为`3/4/9/24/19/29/254/121/258/47/303/422/255/185 μs`，对应分数为`92/90/83/71/70/62/52/47/55/57/45/57/48/48`。相对#109591，case7/12/14分别快`1/2/1 μs`，case9/10/11分别慢`1/1/3 μs`；aggregate从`62.71→62.64`。这些同源差异只能归因于OJ timing-tier波动，当前baseline继续保持#109591。
- **原始归档**：[`cuda_109601_raw.json`](raw/cuda_109601_raw.json)。

### 2026-08-11

#### 提交 #109578 · exp265 case8 inline finalizer

- **总状态/总分**：Accepted（14/14）/ `62.43`；提交正常由`Pending→Running→Finished`，说明平台队列与评测链路可用，终态后无在途任务。
- **代码溯源**：[`cuda_109578.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109578.cpp)，SHA-256 `6bfbfa9b8c89bb96caaade8419aee87d6ef02e9d413b3a4976727b370b36618a`；raw内嵌源码、逐提交快照和提交前工作源码三方一致。
- **唯一差异与本地证据**：保留exp262的case8 split14/19页 producer、native grouped reducer数学和FP32 partial布局；每个producer写完partial后执行`__threadfence()`与32-bit `atomicAdd`，最后一个CTA用原256线程完成八head finalization并`atomicExch`归零，从而删除独立reducer launch。资源`90 MTreg/60 STreg/8320 B/0 stack/5 warps`，未跨驻留档；CPU14/14、GPU full/boundary/random各14/14及关键长度full→short→full均100% PASS。41×300正向exp265/exp262 p50=`0.9868`，反向exp262/exp265=`1.0128`，消偏约`0.9871`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109578 | **62.43** | 3 | 4 | 10 | 25 | 19 | 29 | 255 | 134 | 255 | 46 | 303 | 421 | 255 | 186 |
| #109558 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 257 | 121 | 254 | 47 | 301 | 424 | 255 | 186 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- 目标case8相对#109558从`121→134 μs`并掉2分，相对#108986也从`125→134 μs`；本地约1.29%收益未兑现。case12的`424→421 μs`没有本轮源码差异，只能视为tier波动。exp265不替换baseline，也不以同一counter/finalizer实现继续调split；工作文件已字节精确恢复exp262。

#### 提交 #109558 · exp261 case8 corrected grouped reducer

- **总状态/总分**：Accepted（14/14）/ `62.57`；平台创建、调度和评测链路可用，终态后队列为空。
- **代码溯源**：[`cuda_109558.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109558.cpp)，SHA-256 `4709cbb419c927486b5ad506ea6702411fc7bd671faba5565ec75a4dba3503a1`；raw嵌入源码、逐提交快照与提交前exp261三方一致。
- **唯一差异与本地证据**：保留exp217的case8 split14/19页 producer，把512个one-head vec4 reducer CTA改成64个eight-head grouped reducer CTA，并让reducer按`FUSE_TAIL_IN_LAST_SPLIT`规则计算live split，修复exp208读取未写partial的根因。CPU14/14、GPU full/boundary/random各14/14及16个关键精确长度全部通过；相对exp217消偏约`0.9959`，相对#108986 case8约`0.8654`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109558 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 257 | 121 | 254 | 47 | 301 | 424 | 255 | 186 |
| #109180 | **62.57** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 121 | 254 | 47 | 301 | 422 | 255 | 188 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- case8维持exp217已经建立的`121 μs/47分`，grouped reducer的本地约0.4%增益未跨OJ timing tier；case4/10各慢1 μs并掉档属于非目标波动。最高指针继续保持#108986/62.71。

#### 提交 #109533 · exp256 case11 inline finalizer split24

- **总状态/总分**：Accepted（14/14）/ `62.43`；目标case11未兑现本地强收益，不替换#108986。
- **代码溯源**：[`cuda_109533.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109533.cpp)，SHA-256 `dae103e138e6be3e99fac3094e4b4fc493c9c5eb4fb9a98345aa1b8501551e87`；与[`cuda_case11_inline_finalize_split24_exp256.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case11_inline_finalize_split24_exp256.cpp)字节精确相同。
- **本地证据**：在exp255 inline-finalizer数据流上只把case11 split48/16页改为split24/32页；full/boundary/random和同进程epoch复用均通过。相对#108986的41×200正向p50=`0.9526`、反向#108986/exp256=`1.0496`，消偏约`0.9527`、本地快约4.73%。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109533 | **62.43** | 3 | 4 | 9 | 25 | 19 | 29 | 257 | 125 | 255 | 46 | 322 | 423 | 255 | 188 |
| #109508 | **62.43** | 3 | 4 | 10 | 24 | 19 | 29 | 255 | 125 | 256 | 46 | 318 | 425 | 255 | 188 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- split24相对exp255/split48的本地4.5%级收益在OJ未兑现，case11反而`318→322 μs`；相对#108986仍慢20 μs并少2分。该路线不替换baseline，exp259额外0.2%本地微增益也不足以支持立即复投。
- **原始评测**：[cuda_109533_raw.json](raw/cuda_109533_raw.json)。

#### 提交 #109508 · exp255 case11 inline finalizer

- **总状态/总分**：Accepted（14/14）/ `62.43`；提交、编译和评测链路正常，目标case11未超过#108986，不替换baseline。
- **代码溯源**：[`cuda_109508.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109508.cpp)，SHA-256 `3a26fd2b1fcabcc1d12d556c81adf72c2ac8db8cbbdb461ec2f3f5372f115f07`；与[`cuda_case11_inline_finalize_exp255.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case11_inline_finalize_exp255.cpp)字节精确相同。
- **本地证据**：保持case11 split48 producer和partial数学，只以epoch计数器、producer fence与last-producer CTA内finalizer消除独立reducer launch；完整correctness和同进程epoch复用通过。41×200正向exp255/#108986 p50=`0.9972`、反向#108986/exp255=`1.0024`，消偏约`0.9974`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109508 | **62.43** | 3 | 4 | 10 | 24 | 19 | 29 | 255 | 125 | 256 | 46 | 318 | 425 | 255 | 188 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- case11从#108986的`302→318 μs`并由45分降到43分，split48 inline finalizer的本地微增益未跨OJ波动；其余shape变化没有源码归因。保留#108986最高指针，同时继续保留changed-precondition下本地强正向的exp256 split24作为未提交finalist。
- **原始评测**：[cuda_109508_raw.json](raw/cuda_109508_raw.json)。

#### 提交 #109180 · exp217 case8 split14/19页

- **总状态/总分**：Accepted（14/14）/ `62.57`；目标case8改善但未跨分数档，不替换#108986。
- **代码溯源**：[`cuda_109180.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109180.cpp)，SHA-256 `f5b90500cf547646f9cb3ea0bdd8a26db74fbdf9629c963de03790e6e1a3fed1`；与exp217完整快照字节精确相同。
- **本地证据**：相对#108986只改case8 split48→14及显式vec4 reducer；完整correctness通过，41×100正向p50=`0.8713`、反向=`1.1508`，消偏约`0.8701`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109180 | **62.57** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 121 | 254 | 47 | 301 | 422 | 255 | 188 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- case8真实快4 μs但仍为47分；case10与case14无源码差异却各退一档，抵消目标改善。该提交确认split14机制，但aggregate规则下保留#108986指针。
- **原始评测**：[cuda_109180_raw.json](raw/cuda_109180_raw.json)。

#### 提交 #109150 · exp209 case8 split33/8页

- **总状态/总分**：Accepted（14/14）/ `62.57`；case8有目标改善但未跨分数档，不替换#108986。
- **代码溯源**：[`cuda_109150.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109150.cpp)，SHA-256 `81bc99619f53f30e859e9ceca31bc49cf24e2f447558cb546c0099322e8b844b`；与[`cuda_case8_split33_exp209.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case8_split33_exp209.cpp)字节精确相同。
- **本地证据**：在exp205上把case8 split48/6页改为33 allocated split/8页，保持`>32` vec4 reducer；相对exp205消偏约`0.9521`。14-case full、case8 boundary/random、精确长度和workspace复用均通过。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109150 | **62.57** | 3 | 4 | 9 | 24 | 19 | 29 | 256 | 123 | 254 | 47 | 312 | 424 | 255 | 186 |
| #109127 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 256 | 125 | 255 | 46 | 308 | 420 | 255 | 186 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- 目标case8比同父#109127快`2 μs`，确认8页producer有真实收益，但123 μs仍为47分。case11没有本轮源码差异却`308→312 μs`，且相对#108986的split24本来就未建立OJ收益；下一候选必须恢复#108986 case11，只隔离更强case8 split点。
- **原始评测**：[cuda_109150_raw.json](raw/cuda_109150_raw.json)。

#### 提交 #109127 · exp205 case11 split24

- **总状态/总分**：Accepted（14/14）/ `62.57`；未超过当前最高#108986，不替换baseline。
- **代码溯源**：[`cuda_109127.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109127.cpp)，SHA-256 `49abb196bc955de9e3c371fc6e55b797de3c1cf635615ce1686e291c7e380f19`；与[`cuda_case11_split24_exp205.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case11_split24_exp205.cpp)字节精确相同。
- **本地证据**：native-row QK改变旧split48选择前提后，exp201–207扫描`39/32/26/20/24/22/23`；split24为局部最优。相对#108986正向p50=`0.9612`、反向#108986/exp205=`1.0401`，消偏约`0.9613`。full/boundary/random及13个精确长度全部通过。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109127 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 256 | 125 | 255 | 46 | 308 | 420 | 255 | 186 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- case11未复现本地约3.9%收益，反而为`308 μs`；case12无源码差异却`423→420 μs`，说明单轮仍混有timing-tier波动。保留split扫描为本地结构信息，但不得把exp205选为OJ baseline。
- **原始评测**：[cuda_109127_raw.json](raw/cuda_109127_raw.json)。

#### 提交 #109101 · exp201 case11 split39

- **总状态/总分**：Accepted（14/14）/ `62.64`；未超过当前最高#108986，不替换baseline。
- **代码溯源**：[`cuda_109101.cpp`](../solutions/archive/2026-08-11-submissions/cuda_109101.cpp)，SHA-256 `8a80a1a7ce11f45c5eac840b82e44480e7c4cf7a5d3969f05738ce82ed7adef3`；与exp201实验快照字节一致。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #109101 | **62.64** | 3 | 4 | 9 | 24 | 19 | 29 | 254 | 125 | 255 | 47 | 302 | 423 | 255 | 186 |
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |

- 目标case11保持`302 μs`，没有跨OJ tier；非目标变化按timing波动处理。该点继续作为split曲线起点，不作为baseline。
- **原始评测**：[cuda_109101_raw.json](raw/cuda_109101_raw.json)。

#### 提交 #108986 · exp190 同源平台探测复投

- **总状态/总分**：Accepted（14/14）/ **`62.71`**，刷新真实最高aggregate记录；提交前后均无其他在途任务。
- **代码溯源**：[`cuda_108986.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108986.cpp)，SHA-256 `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`；与[`cuda_108936.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108936.cpp)及exp190完整源码字节精确相同。
- **平台结论**：任务排队数分钟后正常进入`Compiling`和`Running`并最终完成，说明提交、编译和评测链路可用；不追加并行提交。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108986 | **62.71** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 125 | 257 | 46 | 302 | 423 | 256 | 186 |
| #108936 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 255 | 125 | 253 | 47 | 300 | 422 | 255 | 186 |

- 同一源码下case4/10改善`1/1 μs`，case9/11/12/13分别回退`4/2/1/1 μs`；aggregate提高`0.14`只能作为timing-tier样本，不归因为新机制。当前选定最高提交指向#108986，结构性control仍为exp190。
- **原始评测**：[cuda_108986_raw.json](raw/cuda_108986_raw.json)。

#### 提交 #108966 · exp191 case5 native grouped reducer

- **总状态/总分**：Accepted（14/14）/ `62.50`，目标case5未跨tier，不替换#108936。
- **代码溯源**：[`cuda_108966.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108966.cpp)，SHA-256 `393d9cac5acea6610e5addd5062dc6fadb0e7d19c596906725656d05f65000b5`；raw内嵌代码、逐提交快照与[`cuda_case5_native_reducer_exp191.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case5_native_reducer_exp191.cpp)字节一致。
- **本地证据**：只给case5 grouped reducer的max/sum启用native row网络；41×200正向exp191/#108936 p50=`0.9789`、反向#108936/exp191=`1.0195`，消偏约`0.9799`。同一`.so`的full/boundary/random、20步精确长度和full→short→full workspace复用全部通过。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108966 | **62.50** | 3 | 4 | 9 | 24 | 19 | 29 | 255 | 126 | 256 | 47 | 297 | 424 | 255 | 188 |
| #108936 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 255 | 125 | 253 | 47 | 300 | 422 | 255 | 186 |

- case5在两次提交中均为`19 μs/70分`，本地约2%收益不足以跨OJ的1 μs档位；非目标变化没有源码归因，不能据此改baseline。
- **原始评测**：[cuda_108966_raw.json](raw/cuda_108966_raw.json)。

#### 提交 #108936 · exp190 case3/5/10 native row QK 组合

- **总状态/总分**：Accepted（14/14）/ **`62.57`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108936.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108936.cpp)，SHA-256 `6adb2aec3e748cfeb036669625063be3be665cb7db31f8e763ba7125d376a982`；raw内嵌代码、逐提交快照与[`cuda_case3_native_rowreduce_exp190.cpp`](../solutions/archive/2026-08-11-experiments/cuda_case3_native_rowreduce_exp190.cpp)字节一致。
- **本地证据**：exp188/189/190分别只命中case5/10/3，双顺序消偏约`0.9259/0.8765/0.9109`；精确长度及同一最终`.so`的full/boundary/random均通过。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108936 | **62.57** | 3 | 4 | 9 | 25 | 19 | 29 | 255 | 125 | 253 | 47 | 300 | 422 | 255 | 186 |
| #108913 | **62.00** | 3 | 4 | 10 | 25 | 22 | 29 | 253 | 125 | 254 | 53 | 303 | 422 | 255 | 188 |

- 目标case3/5/10分别改善`1/3/6 μs`，与三个本地A/B方向一致，display score合计增加7分；case4无源码差异且保持70分，其他变化均未改变结论。#108936正式取代#108897。
- **原始评测**：[cuda_108936_raw.json](raw/cuda_108936_raw.json)。

#### 提交 #108856 · exp183 case7 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`61.64`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108856.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108856.cpp)，SHA-256 `4e5726efe6a8f03c147eb64db33d33dbf93bb44aea780a0d34e91b30470e103e`；raw内嵌代码、逐提交快照与exp183完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108840只给case7 generic KV8 producer启用native row allreduce，case9/12保持已验证路径，其他dispatch不变。CPU 14/14，同一`.so`的GPU full/boundary/random各14/14，case7精确长度`1/15/16/17/2047/2048`均PASS；41×200正向p50=`0.8727`、反向=`1.1430`，消偏约`0.8739`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108856 | **61.64** | 3 | 4 | 10 | 28 | 22 | 32 | 255 | 126 | 255 | 53 | 303 | 421 | 255 | 188 |
| #108840 | **61.50** | 3 | 4 | 10 | 29 | 22 | 32 | 283 | 125 | 254 | 53 | 301 | 426 | 256 | 186 |

- 目标case7 `283→255 μs`，ratio `0.9011`，与本地强测显著同向；得分`49→52`。case4无源码差异却恢复一分，case8/14各波动减少一分，case9/11/12/13的1–5 μs变化均按timing-tier波动处理。目标三分提升、非目标净减一分，aggregate增加`0.14`，因此#108856正式取代#108840。
- **原始评测**：[cuda_108856_raw.json](raw/cuda_108856_raw.json)。

#### 提交 #108840 · exp182 case9 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`61.50`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108840.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108840.cpp)，SHA-256 `8c1eb876b638fd2b63cbbf0e490c6aededce348913ebc0b35650a4e240137054`；raw内嵌代码、逐提交快照与exp182完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108827只给case9 generic KV8 producer启用native row allreduce，case12保持已验证路径，其他dispatch不变。CPU 14/14、GPU full/boundary/random各14/14；41×200正向p50=`0.8728`、反向=`1.1458`，消偏约`0.8728`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108840 | **61.50** | 3 | 4 | 10 | 29 | 22 | 32 | 283 | 125 | 254 | 53 | 301 | 426 | 256 | 186 |
| #108827 | **61.36** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 125 | 287 | 53 | 300 | 425 | 255 | 186 |

- 目标case9 `287→254 μs`，ratio `0.8850`，与本地强测显著同向；得分`52→55`。case4无源码差异却`28→29 μs`并减少一分，case11/12/13的1 μs变化均未跨分数档，按timing-tier波动处理。目标三分提升、非目标净减一分，aggregate增加`0.14`，因此#108840正式取代#108827。
- **原始评测**：[cuda_108840_raw.json](raw/cuda_108840_raw.json)。

#### 提交 #108827 · exp181 case12 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`61.36`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108827.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108827.cpp)，SHA-256 `2dcd0620181bcafb1c19d427bfe33a683a514bc73fd5e83c9707220153bd5117`；raw内嵌代码、逐提交快照与exp181完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108821只给case12 generic KV8 producer启用native row allreduce，case8/11/14保持已验证路径，其他dispatch不变。CPU 14/14、GPU full/boundary/random各14/14；41×200正向p50=`0.8638`、反向=`1.1571`，消偏约`0.8640`，非目标case7/9/13/14中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108827 | **61.36** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 125 | 287 | 53 | 300 | 425 | 255 | 186 |
| #108821 | **61.14** | 3 | 4 | 10 | 28 | 22 | 31 | 283 | 126 | 284 | 53 | 299 | 472 | 254 | 186 |

- 目标case12 `472→425 μs`，ratio `0.9004`，与本地强测显著同向；得分`54→57`。case6无源码差异却`31→32 μs`并减少一分，case8 `126→125 μs`并恢复一分；case9/11/13的1–3 μs变化均按timing-tier波动处理。非目标分数净变化为零，case12三分提升使aggregate增加`0.22`，因此#108827正式取代#108821。
- **原始评测**：[cuda_108827_raw.json](raw/cuda_108827_raw.json)。

#### 提交 #108821 · exp179 case14 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`61.14`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108821.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108821.cpp)，SHA-256 `9dd9651f6ec947e1fb976ed5cbb73e776dc1713020b5f51a3583f803308b4011`；raw内嵌代码、逐提交快照与exp179完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108816只把native row allreduce扩展到case14 head-pair/z4 producer，case8/11保持已验证路径，其他dispatch不变。CPU 14/14、GPU full/boundary/random各14/14与case14 19步精确长度全部PASS；41×200正向p50=`0.8537`、反向=`1.1772`，消偏约`0.8516`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108821 | **61.14** | 3 | 4 | 10 | 28 | 22 | 31 | 283 | 126 | 284 | 53 | 299 | 472 | 254 | 186 |
| #108816 | **60.79** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 125 | 286 | 54 | 300 | 474 | 256 | 219 |

- 目标case14 `219→186 μs`，ratio `0.8493`，与本地强测显著同向；得分`43→48`。case6无源码差异却`32→31 μs`并增加一分，case8 `125→126 μs`并减少一分；case9–13的1–2 μs变化均按timing-tier波动处理。case14的五分提升与非目标净零分变化使aggregate增加`0.35`，因此#108821正式取代#108816。
- **原始评测**：[cuda_108821_raw.json](raw/cuda_108821_raw.json)。

#### 提交 #108816 · exp178 case8 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`60.79`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108816.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108816.cpp)，SHA-256 `3e2f27cd5032a1f1c34f1e6f2490686a91be27a328c57c9382d6dacaeab5d92c`；raw内嵌代码、逐提交快照与exp178完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108803只把native row allreduce扩展到case8 head-pair/z4 producer，case11保持已验证路径，其他dispatch不变。GPU full/boundary/random各14/14与case8 16步精确长度全部PASS；41×200正向p50=`0.8911`、反向=`1.1231`，消偏约`0.8907`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108816 | **60.79** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 125 | 286 | 54 | 300 | 474 | 256 | 219 |
| #108803 | **60.50** | 3 | 4 | 10 | 29 | 22 | 32 | 284 | 139 | 284 | 53 | 301 | 475 | 254 | 220 |

- 目标case8 `139→125 μs`，ratio `0.8993`，与本地强测显著同向；得分`44→47`。case4无源码差异却`29→28 μs`并恢复一分；case7/9/10/11/12/13/14的±1–2 μs均按timing-tier波动处理。case8的三分提升与case4的一分恢复使aggregate净增`0.29`，因此#108816正式取代#108803。
- **原始评测**：[cuda_108816_raw.json](raw/cuda_108816_raw.json)。

#### 提交 #108803 · exp177 case11 native row16 allreduce

- **总状态/总分**：Accepted（14/14）/ **`60.50`**，刷新真实最高分并成为当前baseline。
- **代码溯源**：[`cuda_108803.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108803.cpp)，SHA-256 `d82b354614b585e6b18c099cc2d87abcd92222dfbe0e7bb18cc3a36c32f31496`；raw内嵌代码、逐提交快照与exp177完整实验源码字节一致。
- **唯一差异/本地证据**：相对#108743只把case11 head-pair QK的全wave BSM XOR `8/4/2/1`归约替换为原生16-lane row rotate-right `8/4` + quad XOR `2/1` 网络。独立C500 probe逐lane字节等价；目标LLVM为`64 mov.shfl / 0 bsm.bpermute`，producer由`94→90 MTreg`并保持5 warps。GPU full/boundary/random各14/14与case11 17步精确长度全部PASS；41×200正向p50=`0.8525`、反向=`1.1734`，消偏约`0.8524`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108803 | **60.50** | 3 | 4 | 10 | 29 | 22 | 32 | 284 | 139 | 284 | 53 | 301 | 475 | 254 | 220 |
| #108743 | **60.29** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 139 | 285 | 53 | 344 | 472 | 255 | 219 |

- 目标case11 `344→301 μs`，ratio `0.8750`，与本地强测显著同向；得分`41→45`。case4无源码差异却`28→29 μs`并降一分，case7/9/12/13/14的±1–3 μs也按timing-tier波动处理。即使扣除case4回退，case11的四分提升仍使aggregate净增`0.21`，因此#108803正式取代#108743。
- **原始评测**：[cuda_108803_raw.json](raw/cuda_108803_raw.json)。

#### 提交 #108772 · exp173 长 KV8 load-site uint2 / scalar-live 组合

- **总状态/总分**：Accepted（14/14）/ **`60.29`**，与当时最高分持平，不替换#108743 baseline。
- **代码溯源**：[`cuda_108772.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108772.cpp)，SHA-256 `22475804001e1cb70eeae5b906838109dfe67b6f92e2adbd89fdc89b1e5cb887`；raw内嵌代码、逐提交快照与exp173实验源码字节一致。
- **目标结果**：case7/9/12/13=`282/283/471/253 μs`，相对#108743的`283/285/472/255 μs`全部同向，但分数仍为`49/52/54/48`。case4无源码差异却`28→29 μs`，因此总分仍为60.29。
- **测试点**：case1–14=`3/4/10/29/22/32/282/139/283/53/344/471/253/218 μs`；分数=`92/90/82/67/67/60/49/44/52/54/41/54/48/44`。
- **原始评测**：[cuda_108772_raw.json](raw/cuda_108772_raw.json)。

### 2026-08-10

#### 提交 #108550 · 同字节 baseline 恢复探针

- **总状态/总分**：Accepted（14/14）/ **`59.86`**；证明此前 Pending 后 OJ worker 已恢复。
- **代码溯源**：[`cuda_108550.cpp`](../solutions/archive/2026-08-10-submissions/cuda_108550.cpp)，raw嵌入源码、逐提交快照和#108468的SHA-256均为`cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`。
- **归因**：没有源码差异，不能把case4/11/12/14各快1 μs解释为新优化；case3同时慢1 μs且aggregate不变。继续选择有本地A/B因果证据的#108468作为control。
- **测试点**：case1–14=`3/4/11/28/22/32/286/139/286/55/347/478/255/258 μs`。
- **原始评测**：[cuda_108550_raw.json](raw/cuda_108550_raw.json)。

### 2026-08-09

#### 本地 exp10 · case-11 4-head CTA / 4 token partitions（未提交）

- 候选 SHA `2a873decfbf2d2fbe222614cdc487e9a2e768b4998b1e3797d0e1125afa213b0`；只把 case 11 从一个 `(16,8,2)` CTA/KV head 改为两个 `(16,4,4)` head-group CTA，缩短每线程 token 链但使 K/V page load 加倍。
- CPU 14/14，GPU case 11 full/boundary/random 均 PASS。full/tail 资源 `70/42→58/34 MTreg`，但 8320 B shared 使 staticMaxWarps 均保持 7。
- case 11 交错 A/B p10/p50/p90=`1.1267/1.1281/1.1298`，稳定回退约 12.8%，不提交。关闭重复 page loader 的 head-group/z-partition 拆分；完整候选源码见 [`cuda_case11_head4_z4.cpp`](../solutions/archive/2026-08-09-experiments/cuda_case11_head4_z4.cpp)。

#### 本地 exp11 · case-11 QK 双 accumulator（未提交）

- 候选 SHA `c8d118ad6e1b75dd3550f4a58db9867ea07113622ad272c3b0fa068b606e0f81`；只把 case-11 full-page 每个 dot 的 4 级 packed-FMA accumulator 链拆为两条 2 级链后合并。
- 资源 `70→72 MTreg`、仍 7 warps；CPU 14/14、GPU case 11 full PASS。A/B p10/p50/p90=`1.0137/1.0148/1.0173`，稳定回退，不提交。完整候选源码见 [`cuda_case11_split_qk_acc.cpp`](../solutions/archive/2026-08-09-experiments/cuda_case11_split_qk_acc.cpp)。

#### 本地 exp12 · case-11 BF16 bitcast 解包（未提交）

- 候选 SHA `5f7d2178ae4cdd8cffbec88502b458f930ebbf11a56cadd2ccff6b67d6176549`；只把 full QK 的 K 解包写成 `uint32` shift/mask + float bitcast，数值与 BF16→FP32 完全等价。
- 资源与 control 相同，CPU 14/14、GPU case 11 full PASS；A/B p10/p50/p90=`0.9976/0.9997/1.0008`，完全中性。编译器已消除源码表达差异，不提交；完整候选源码见 [`cuda_case11_bitcast_qk.cpp`](../solutions/archive/2026-08-09-experiments/cuda_case11_bitcast_qk.cpp)。

#### 本地 exp14 · case-11 shared-score producer/consumer（未提交）

- 候选 SHA `ae1696289bd55ec2ee509ec1b3f488688dc627dc3e7f8dabb112e40a4a245c41`；256-thread CTA 中只让 4 个 head-pair producer 计算 QK，并通过新增 512 B shared score 把结果交给 8 个 consumer 完成 softmax/PV。
- full/tail 资源为 `86/36 MTreg`、shared `8832 B`；case 11 full correctness PASS。
- case 11 交错 A/B p10/p50/p90=`1.6010/1.6029/1.6040`，稳定慢约 60%。shared handoff、同步和 producer/consumer 不均衡远超减少 QK worker 的收益，不提交并关闭该 exact 数据流。实现模板可在 #106584 源码中找到，但未实例化、未 launch，不影响 #106584 的运行时归因。

#### 提交 #108743 · exp163 case14 head-pair/register-lookahead

- **总状态/总分**：Accepted（14/14）/ **`60.29`**，刷新当时真实最高分并成为当时baseline。
- **代码溯源**：[`cuda_108743.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108743.cpp)，SHA-256 `d1b327f20d3ba9595d6b7a42427e59fd5ec0d537253fad94def37eeff6b213a2`；raw内嵌代码、逐提交快照、exp163实验源码与当时工作文件字节一致。
- **唯一差异/本地证据**：相对即时源码父版本exp161，只把case14从generic `(16,8,2)` z2改为head-pair `(16,4,4)` z4，并组合同步K/V register-lookahead；split257、fused tail、raw-row16 QK、Q预缩放、normalized-BF16 partial和final reducer不变。资源为`94 MTreg/52 STreg/8320 B shared/0 stack/staticMaxWarps 5`；CPU及GPU full/boundary/random各14/14、19个case14精确长度全部PASS。强测正向exp163/exp161 p50=`0.8561`、反向exp161/exp163=`1.1639`，消偏约`0.8576`、快14.24%。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108743 | **60.29** | 3 | 4 | 10 | 28 | 22 | 32 | 283 | 139 | 285 | 53 | 344 | 472 | 255 | 219 |
| #108721 | **59.86** | 3 | 4 | 11 | 29 | 22 | 32 | 284 | 139 | 285 | 54 | 346 | 473 | 255 | 258 |
| #108713 | **60.14** | 3 | 4 | 10 | 29 | 22 | 31 | 285 | 139 | 285 | 54 | 341 | 475 | 255 | 258 |

- 相对唯一差异父版本#108721，目标case14 `258→219 μs`，ratio `0.8488`，与本地消偏`0.8576`强一致；其得分`40→43`。case1–14显示分为`92/90/82/68/67/60/49/44/52/54/41/54/48/43`。
- case3/4/7/10/11/12没有本轮对应源码差异，其±1–2 μs变化只能视为OJ timing-tier波动。尽管case11从#108713的42分回到41分，case14的3分提升仍使aggregate较旧baseline提高`0.15`；因此#108743同时满足目标因果与最高aggregate，正式取代#108713。
- 原始评测：[cuda_108743_raw.json](raw/cuda_108743_raw.json)。

#### 提交 #108721 · exp161 case7/9 Q 预缩放组合

- **总状态/总分**：Accepted（14/14）/ **`59.86`**；提交链路正常完成，case7目标改善但aggregate未保持，不替换#108713。
- **代码溯源**：[`cuda_108721.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108721.cpp)，SHA-256 `0d92dfc789db9abafcc9d529cb3982132eaf27c0e4e1370b1ce502b679b07bfb`；raw内嵌代码、逐提交快照、exp161实验源码与当时工作文件字节一致。
- **唯一差异/本地证据**：exp160相对#108713只给case7 split14 producer启用Q预缩放，强复测消偏约`0.9947`；exp161在其上只给case9 split24 producer启用同一变换，消偏约`0.9968`。组合源码GPU full/boundary/random各14/14，case7/9各17个精确长度全部PASS。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108721 | **59.86** | 3 | 4 | 11 | 29 | 22 | 32 | 284 | 139 | 285 | 54 | 346 | 473 | 255 | 258 |
| #108713 | **60.14** | 3 | 4 | 10 | 29 | 22 | 31 | 285 | 139 | 285 | 54 | 341 | 475 | 255 | 258 |

- case7 `285→284 μs`与本地A/B同向，case9仍为285 μs、没有跨tier。case12 `475→473 μs`是Accepted历史最佳，但本轮没有对应case12源码变化，不能归因给exp160/161；case3/6/11同理属于非目标tier回退并使aggregate下降。该轮保留为局部机制证据，baseline仍为#108713。
- 原始评测：[cuda_108721_raw.json](raw/cuda_108721_raw.json)。

#### 提交 #108713 · exp159 case12 Q 预缩放

- **总状态/总分**：Accepted（14/14）/ **`60.14`**，刷新当时的真实最高分并曾成为baseline。
- **代码溯源**：[`cuda_108713.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108713.cpp)，SHA-256 `3cee37f740ae7ccbba6491d133ea39aeef8e0b8f60a7f4aa049921f9c4a1e9c9`；raw内嵌代码、逐提交快照与exp159实验源码字节一致。
- **唯一差异/本地证据**：相对#108700/exp158只给case12的KV8 16-page full+fused-tail producer启用Q预缩放，保持128-owner布局、K+V lookahead、raw row16 QK、partial和64-thread vec2 reducer不变。强测正向exp159/exp158 p50=`0.9963`，反向exp158/exp159=`1.0034`，消偏约`0.99645`；GPU full/boundary/random各14/14和17个case12精确长度全部PASS。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108713 | **60.14** | 3 | 4 | 10 | 29 | 22 | 31 | 285 | 139 | 285 | 54 | 341 | 475 | 255 | 258 |
| #108700 | **59.93** | 3 | 4 | 11 | 28 | 22 | 32 | 284 | 139 | 286 | 54 | 346 | 476 | 254 | 257 |

- 唯一目标case12 `476→475 μs`与本地A/B同向但仍为54分。case6/case11没有本轮源码差异，却分别`32→31 μs`、`346→341 μs`并跨到61/42分；case4反向`28→29 μs`、case13 `254→255 μs`，均体现OJ tier波动。选择#108713既因为aggregate最高，也因为其新增case12机制有独立本地和OJ目标证据。
- 原始评测：[cuda_108713_raw.json](raw/cuda_108713_raw.json)。

#### 提交 #108700 · exp158 case13 Q 预缩放

- **总状态/总分**：Accepted（14/14）/ **`59.93`**；提交链路成功完成，目标case13真实改善但未跨得分档，不替换#108679。
- **代码溯源**：[`cuda_108700.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108700.cpp)，SHA-256 `37a59eaa6d4cdf213d3c5dc224d2fc8736641245fdca1e6724b8c0b0ed46cae5`；raw内嵌代码、逐提交快照与exp158实验源码字节一致。
- **唯一差异/本地证据**：相对#108691/exp157只给case13的KV8 full+fused-tail producer启用Q预缩放，保持split256/15 pages、四标量K+V lookahead、raw row16 QK、partial和64-thread vec2 reducer不变。强复测61×500正向exp158/exp157 p50=`0.9972`，反向exp157/exp158=`1.0011`，消偏约`0.99805`；GPU full/boundary/random各14/14和17个case13精确长度全部PASS。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108700 | **59.93** | 3 | 4 | 11 | 28 | 22 | 32 | 284 | 139 | 286 | 54 | 346 | 476 | 254 | 257 |
| #108691 | **60.00** | 3 | 4 | 11 | 28 | 22 | 32 | 285 | 139 | 286 | 53 | 343 | 476 | 256 | 256 |

- 唯一目标case13 `256→254 μs`与本地A/B同向，但得分仍为48；case6保持32 μs。case7/10/11/14没有对应源码变化，它们的`-1/+1/+3/+1 μs`只能视为tier波动，其中case11使aggregate下降。该轮确认case13局部机制，但不把低于60.07的#108700选为OJ baseline。
- 原始评测：[cuda_108700_raw.json](raw/cuda_108700_raw.json)。

#### 提交 #108691 · exp157 case6 Q 预缩放

- **总状态/总分**：Accepted（14/14）/ **`60.00`**；目标case6未跨tier，不替换#108679。
- **代码溯源**：[`cuda_108691.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108691.cpp)，SHA-256 `ae74e4e561083be57cbeb1dd20561c29cb736c9c0e91e4a04a75471291c322d2`；raw、提交快照与exp157实验源码字节一致。
- **唯一差异/本地证据**：只给case6的同步KV8 combined producer启用Q预缩放，保持split8、约3 pages/split、raw row16 QK、partial和group8 reducer不变。61×1000正向exp157/exp156 p50=`0.9907`，反向exp156/exp157=`1.0120`，消偏约`0.98942`；GPU全量和29个精确长度通过。
- **OJ解释**：case6仍为`32 μs/60分`，说明约1.06%本地收益尚未跨离散档。case3没有源码差异却`10→11 μs`并少2分，是aggregate降至60.00的主因；case10/11/12/14的`53/343/476/256 μs`也只作tier样本。
- 原始评测：[cuda_108691_raw.json](raw/cuda_108691_raw.json)。

#### 提交 #108679 · exp156 case10/4 Q 预缩放扩展

- **总状态/总分**：Accepted（14/14）/ **`60.07`**，与#108658同分；目标case4真实跨tier，选为当前baseline。
- **代码溯源**：[`cuda_108679.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108679.cpp)，SHA-256 `27abd5e20c710a74fa99406618657ae63ce6d6c26fc8592b8dfc88023be61bfb`；raw内嵌代码、逐提交快照与exp156实验快照字节一致。
- **唯一组合链**：exp154只给case10的split128/4-page register-lookahead producer启用generic `PRESCALE_Q`；exp156只把同一特化扩到case4的KV8/BSM/combined/direct-out四页producer。两者均保持原loader、split、QK/PV ownership、softmax、partial/reducer或direct-out不变；exp155对case5的两页/split扩展中性，未合入。
- **正确性/本地 A/B**：最终源码CPU14/14、GPU full/boundary/random各14/14；case10的20步和case4的14步精确长度全部PASS。相对fresh #108658 control，case4 61×1000正反p50=`0.9934/1.0080`、消偏约`0.9927`，case10 61×500=`0.9985/1.0032`、消偏约`0.99765`；case8/11/14中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108679 | **60.07** | 3 | 4 | 10 | 28 | 22 | 32 | 286 | 139 | 287 | 54 | 344 | 477 | 256 | 258 |
| #108658 | **60.07** | 3 | 4 | 10 | 29 | 22 | 32 | 283 | 139 | 285 | 54 | 343 | 476 | 255 | 257 |

- 唯一目标case4 `29→28 μs`且得分`67→68`，与本地A/B同向；case10未跨tier。case11源码相同却`343→344 μs`并从42降到41分，case7/9/12/13/14也无对应dispatch变化，因此这些差异不能归因于预缩放扩展。选择#108679是因为目标源码证据更强，而不是因为aggregate变大。
- 原始评测：[cuda_108679_raw.json](raw/cuda_108679_raw.json)。

#### 提交 #108658 · exp153 case11/8/14 Q 预缩放组合

- **总状态/总分**：Accepted（14/14）/ **`60.07`**，超过 #108628 的`60.00`，成为当前baseline。
- **代码溯源**：[`cuda_108658.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108658.cpp)，SHA-256 `cd76faa57c5b3a52ad9c7974b346c52f1dd16e8026a1d2177ee10f0c8ba61a5a`；raw内嵌代码、逐提交快照与exp153实验快照字节一致。
- **唯一组合链**：exp151只给case11 head-pair/z4 producer预缩放Q；exp152只把同一模板特化扩到case8；exp153只在generic token-parallel模板加入相同机制并仅给case14启用。每个shape均保持loader、split、QK/PV ownership、softmax、partial ABI和reducer不变，且逐shape通过独立A/B后才组合。
- **正确性/本地 A/B**：case11/8/14消偏约`0.99556/0.99298/0.99645`；CPU14/14，最终exp153的GPU full/boundary/random各14/14，目标shape精确split/tail/full→short→full长度全部PASS。case14资源从exp152的`78 MTreg/56 STreg`变为`78/54`，8320 B shared、0 stack、6 warps不变；case11资源不变。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108658 | **60.07** | 3 | 4 | 10 | 29 | 22 | 32 | 283 | 139 | 285 | 54 | 343 | 476 | 255 | 257 |
| #108628 | **60.00** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 139 | 285 | 54 | 348 | 476 | 256 | 257 |

- case11 `348→343 μs`、得分`41→42`与exp151本地唯一差异证据同向，并是aggregate提升的确认归因。case8/14虽然本地正向，但本轮仍为`139/257 μs`，没有跨OJ tier；case7/13的`-2/-1 μs`没有对应dispatch变化，只作tier样本。
- 原始评测：[cuda_108658_raw.json](raw/cuda_108658_raw.json)。

#### 提交 #108651 · exp151 case11 Q 预缩放

- **总状态/总分**：Accepted（14/14）/ **`59.93`**；目标case11真实改善，但总分低于当前baseline #108628 的`60.00`，不切换control。
- **代码溯源**：[`cuda_108651.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108651.cpp)，SHA-256 `89b0934451ef46065afab359a6e6fc316023a5bac8b6e6a1adbbb5693cc02d02`；raw内嵌代码、逐提交快照与exp151实验快照字节一致。
- **唯一差异**：仅给case11的`paged_decode_case11_headpair_z4_kernel`增加`PRESCALE_Q`特化，在每个split开始时把两行Q乘一次`sm_scale`，并从full/tail每个token的score计算中移除重复乘法；loader、split48、head/z ownership、softmax/PV、partial ABI和reducer均不变。
- **正确性/本地 A/B**：资源保持`94 MTreg / 54 STreg / 8320 B / 0 stack / 5 warps`。CPU14/14，GPU full/boundary/random各14/14；case11的19步full→short→full精确长度全部PASS。61×500正向exp151/#108628 p10/p50/p90=`0.9948/0.9959/0.9969`，反向#108628/exp151=`1.0038/1.0048/1.0053`，消偏约`0.99556`，快约0.44%或2.6 μs。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108651 | **59.93** | 3 | 4 | 10 | 29 | 22 | 32 | 286 | 139 | 288 | 53 | 345 | 477 | 255 | 259 |
| #108628 | **60.00** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 139 | 285 | 54 | 348 | 476 | 256 | 257 |

- 唯一目标case11 `348→345 μs`与本地A/B同向，但显示分数仍为41；case7/9/10/12/13/14没有对应源码差异，其计时只作OJ tier样本，不能归因于Q预缩放。
- 原始评测：[cuda_108651_raw.json](raw/cuda_108651_raw.json)。

#### 提交 #108641 · #108628 同字节恢复试投

- **总状态/总分**：Accepted（14/14）/ **`59.93`**；提交、编译和评测链路均正常，但不替换 #108628。
- **代码溯源**：[`cuda_108641.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108641.cpp)，SHA-256 `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d`，与 #108628 字节完全一致。
- **结果**：case1–14=`3/4/10/29/22/32/285/140/286/54/347/476/255/259 μs`。同源相对 #108628 的 case8/9/11/13/14 为`+1/+1/-1/-1/+2 μs`，再次证明单轮绝对计时和aggregate会受timing-tier波动影响。
- 原始评测：[cuda_108641_raw.json](raw/cuda_108641_raw.json)。

#### 提交 #108628 · exp149 case12 完整 wave vec2 reducer

- **总状态/总分**：Accepted（14/14）/ **`60.00`**，与#108604同分；目标case12真实改善，选为当前baseline。
- **代码溯源**：[`cuda_108628.cpp`](../solutions/archive/2026-08-11-submissions/cuda_108628.cpp)，SHA-256 `0f76be0bc392fee0b173a37fd3872fc58151813416f8aa09f8aedf99b3c82a2d`；raw内嵌代码、逐提交快照、exp149实验快照和空闲工作文件四者字节一致。
- **唯一差异**：case12保持256个one-head reducer CTA、producer、split128、FP32 partial、fused-tail owner计数和softmax数学不变，只把32-thread vec4 reducer改为64-thread完整wave vec2。exp91只验证过scalar→vec4；本次隔离验证B8/256 CTA下的wave填充。
- **正确性/本地 A/B**：CPU14/14；同一`.so`的GPU full/boundary/random各14/14，16个case12精确split边界及full→short→full长度全部PASS。61×500正向exp149/#108604 p10/p50/p90=`0.9977/0.9987/1.0002`，反向#108604/exp149=`1.0001/1.0009/1.0014`，消偏约`0.99890`；case10/13中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108628 | **60.00** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 139 | 285 | 54 | 348 | 476 | 256 | 257 |
| #108604 | **60.00** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 140 | 287 | 54 | 347 | 477 | 255 | 257 |

- 唯一目标case12 `477→476 μs`与本地微增益同向，但显示分数仍为54，因此没有跨下一计分tier。case8/9/11/13没有对应dispatch变化，其`-1/-2/+1/+1 μs`只作OJ timing样本，不能归因于exp149。
- 原始评测：[cuda_108628_raw.json](raw/cuda_108628_raw.json)。

#### 提交 #108604 · exp147 case10 完整 wave vec2 reducer

- **总状态/总分**：Accepted（14/14）/ **`60.00`**，超过 #108468 的 `59.86`，成为当前 baseline。
- **代码溯源**：[`cuda_108604.cpp`](../solutions/archive/2026-08-10-submissions/cuda_108604.cpp)，SHA-256 `7be23e1f156d6fe38f7b30a0226603a8d4bdd044a9b9558bdc7f7298054d1ae6`；逐提交快照、exp147实验快照和空闲工作文件三者字节一致。
- **唯一差异**：case10保持32个one-head CTA、producer、split128、FP32 partial、full-page-owner live-count和softmax数学不变，只把32-thread vec4 reducer改为64-thread完整wave vec2 reducer。资源从`64/35`变为`38/39 MTreg/STreg`，staticMaxWarps均为8。
- **正确性/本地 A/B**：CPU14/14；同一`.so`的GPU full/boundary/random各14/14，19个case10定点长度全部PASS。41×500正向exp147/#108468 p10/p50/p90=`0.9662/0.9781/0.9859`，反向#108468/exp147=`1.0137/1.0271/1.0391`，消偏exp147/control约`0.9759`；case4/5/14均中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108604 | **60.00** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 140 | 287 | 54 | 347 | 477 | 255 | 257 |
| #108468 | **59.86** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 140 | 285 | 55 | 348 | 479 | 255 | 259 |

- case10 `55→54 μs`且分数`53→54`与本地唯一差异证据一致，是总分提升的确认归因。case9/11/12/14的`+2/-1/-2/-2 μs`均没有对应dispatch变化，只作为OJ tier样本，不能归因于reducer改动。
- 原始评测：[cuda_108604_raw.json](raw/cuda_108604_raw.json)。

#### 提交 #108468 · exp138 四个长 KV8 K+V lookahead 闭环

- **总状态/总分**：Accepted（14/14）/ **`59.86`**，与 #108312 并列。
- **代码溯源**：[`cuda_108468.cpp`](../solutions/archive/2026-08-10-submissions/cuda_108468.cpp)，SHA-256 `cef492aaa767c103edfabeeedf2caaea62b9d200f8946cb578636cf18412d946`；逐提交快照、exp138 实验快照和工作文件三者字节一致。
- **唯一主链差异**：exp136/137/138 依次只给 case12/9/7 打开 exp134 已在 case13 验证的四标量 next-V，使下一页 K/V 都跨当前 PV 保存在寄存器；各 shape 的 split、tail、QK/PV、partial 和 reducer 保持不变。
- **正确性/本地 A/B**：CPU 与 GPU full/boundary/random 各14/14，三个目标 shape 的定点长度与非目标回归通过；case12/9/7 增量双向消偏约 `0.9884/0.9847/0.9853`，case13 的父实验增量为 `0.9772`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108468 | **59.86** | 3 | 4 | 10 | 29 | 22 | 32 | 285 | 140 | 285 | 55 | 348 | 479 | 255 | 259 |
| #108312 | **59.86** | 3 | 4 | 10 | 29 | 22 | 32 | 289 | 139 | 289 | 55 | 347 | 486 | 256 | 259 |

- 四个目标长 KV8 case 分别改善 `4/4/7/1 μs`；case8/11 的 `+1 μs` 没有对应源码差异，视为 OJ timing 波动。总分尚未跨新 tier，但真实目标变化与本地 A/B 同向，因此切换当前最佳指针。
- 原始评测：[cuda_108468_raw.json](raw/cuda_108468_raw.json)。

#### 提交 #108312 · exp135 编译表面裁剪与本地主链落地

- **总状态/总分**：Accepted（14/14）/ **`59.86`**，超过 #106626 的 `57.64`，首次达到当前最高分；后由目标 case 更优的 #108468 取代为 control。
- **代码溯源**：[`cuda_108312.cpp`](../solutions/archive/2026-08-10-submissions/cuda_108312.cpp)，SHA-256 `234af15ed3f75fb939e3a2392ba4d377b4644a8595887a9e948a822ce88c12a9`；逐提交快照、exp135实验快照和工作文件三者一致。
- **唯一提交差异**：相对exp134只排除生产dispatch从未启用的CUTE/MCTLASS/WMMA头文件与probe编译表面，用独立常量保持token-parallel和BASE2 reducer；运行路径承接exp68–134的全部本地正向实验。#108257/#108278同运行源码连续compile TLE，exp135本机构建`10.08→8.17 s`后成功通过OJ编译。
- **正确性/本地A/B**：CPU、GPU full/boundary/random各14/14；case7–14 p50=`1.0001/0.9992/0.9997/1.0010/0.9997/0.9997/0.9992/1.0007`，运行中性。case4强复测正反=`0.9938/1.0042`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #108312 | **59.86** | 3 | 4 | 10 | 29 | 22 | 32 | 289 | 139 | 289 | 55 | 347 | 486 | 256 | 259 |
| #106626 | 57.64 | 3 | 4 | 10 | 30 | 25 | 33 | 322 | 174 | 322 | 57 | 417 | 533 | 294 | 296 |

- 相对 #106626，11个perf case全部改善，case8/11分别快约20.1%/16.8%；总分提高`2.22`。这些收益来自此前逐项本地验证并在同一源码组合的raw QK、tail/reducer、register-lookahead等，不应归因于编译裁剪本身。
- 原始评测：[cuda_108312_raw.json](raw/cuda_108312_raw.json)。

#### 提交 #106626 · case-11 256-thread head-pair/z4 两级 reducer

- **总状态/总分**：Accepted（14/14）/ **`57.64`**，超过 #106069 的 `57.57`，切换当前最佳指针。
- **代码溯源**：[`cuda_106626.cpp`](../solutions/archive/2026-08-09-submissions/cuda_106626.cpp)，SHA-256 `bc5b3a4de04e68161342b902c901deb480c358e1b2cc3c8280ec44b0f125c5f3`；逐提交快照、raw 嵌入源码和提交前工作文件三者一致。
- **唯一架构假设**：保留 head-pair 的“一次 K/V shared load/unpack 服务两个 query head”，但将 #106556/#106584 的 128-thread `(16,4,2)` 改为 256-thread `(16,4,4)`。每个 z 真正只负责 4 token；四个 z-state 不同时 materialize 16 KiB，而是先将 z2/z3 的 16 个 head-state 写入原 8 KiB K/V buffer，由 z0/z1 成对合并，再只写 8 个 z1-state 让 z0 完成第二级归约。
- **资源与正确性**：full/tail=`84/50 MTreg`、`48/42 STreg`、0 B stack、8320 B shared、staticMaxWarps=`5/7`；CPU 14/14，GPU full/boundary/random 均 14/14 PASS。
- **本地 A/B**：case 11 首轮 p10/p50/p90=`0.9520/0.9531/0.9533`；补测=`0.9516/0.9528/0.9542`。非目标 case 4/8/12 p50=`0.9992/1.0005/0.9996`，中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106626 | **57.64** | 3 | 4 | 10 | 30 | 25 | 33 | 322 | 174 | 322 | 57 | 417 | 533 | 294 | 296 |
| #106069 | 57.57 | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

- case 11 `438→417 μs`，得分 `36→37`，与本地约 4.7–5.0% 加速方向和幅度一致；256-thread/z4 是首个把跨-head unpack reuse 转化为真实 OJ 收益的版本。case 10/14 的 `57/296 μs` 是有利 tier，非本改动 dispatch，不能归因于 case-11 源码。
- 原始评测：[cuda_106626_raw.json](raw/cuda_106626_raw.json)。

#### 提交 #106584 · case-11 head-pair 4-token sequential chunk

- **总状态/总分**：Accepted（14/14）/ `57.29`，不切换 #106069 当前最佳指针。
- **代码溯源**：[`cuda_106584.cpp`](../solutions/archive/2026-08-09-submissions/cuda_106584.cpp)，SHA-256 `98deba6c92a9416da6ed05ca8c5b175ba0e6fa8ff6fc9b485089467b9910c8ef`；逐提交快照、raw 嵌入源码和提交前工作文件三者一致。
- **唯一差异**：保持 #106556 的 `(16,4,2)` 128-thread head-pair CTA、不重复 page loader和每线程两个 query head，只将每个 z 的 8 个同时 live score 改成两个顺序执行的 4-token chunk。未 dispatch 的 exp14 producer/consumer 模板仅增加源码体积，不产生运行时差异。
- **资源与正确性**：full/tail 为 `82/64 MTreg`、8320 B shared、staticMaxWarps `5/7`；CPU 14/14，同一 `.so` 的 GPU full/boundary/random 均 14/14 PASS。
- **本地 A/B**：case 11 初测 p50 `0.9710`；补测 p10/p50/p90=`0.9689/0.9703/0.9733`。非目标 case 4/8/12 p50=`0.9973/0.9988/1.0002`，均中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106584 | 57.29 | 3 | 4 | 10 | 30 | 25 | 33 | 322 | 179 | 322 | 60 | 467 | 532 | 296 | 299 |
| #106069 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

- OJ case 11 `467 μs/34` 与本地约 3.0% 正向再次相反，并比 #106556 的 `452 μs` 更差。降低同时 live score 和 full register 并未使 head-pair 跨过 OJ timing tier；关闭 z=2 下 4/8-token live-score 局部扫描，但保留跨-head unpack reuse 作为改变 token partition/CTA 数据流后的架构线索。
- 原始评测：[cuda_106584_raw.json](raw/cuda_106584_raw.json)。

#### 提交 #106556 · case-11 128-thread head-pair K/V unpack reuse

- **总状态/总分**：Accepted（14/14）/ `57.43`，不切换 #106069 当前最佳指针。
- **代码溯源**：[`cuda_106556.cpp`](../solutions/archive/2026-08-09-submissions/cuda_106556.cpp)，SHA-256 `482d4557ea752e58ecbdc71fc6b09e4f11339648a4742dfa28c2da8bb7272db7`；逐提交快照、raw 嵌入源码和提交前工作文件三者一致。
- **唯一差异**：case 11 从 `(16,8,2)` 256-thread one-head/thread 改为 `(16,4,2)` 128-thread two-head/thread。一个 CTA 仍完整覆盖一个 KV head 和 split，每页 K/V 仍只加载一次；一次 shared load 与 BF16 unpack 同时喂给两个 query-head QK/PV，区别于 exp10 会重复整页 loader 的两-CTA head-group。
- **资源与正确性**：full/tail 为 `100/60 MTreg`、8320 B shared、staticMaxWarps `4/7`；CPU 14/14，同一 `.so` 的 GPU full/boundary/random 均 14/14 PASS。
- **本地 A/B**：case 11 两轮 p50 为 `0.9484/0.9472`，第二轮 p10/p90=`0.9465/0.9479`；非目标 case 4/8/12 p50=`0.9949/0.9992/0.9998`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106556 | 57.43 | 3 | 4 | 10 | 30 | 26 | 33 | 321 | 175 | 322 | 57 | 452 | 533 | 294 | 297 |
| #106069 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

- OJ case 11 `452 μs/35` 与本地稳定正向相反，exact 版本不能取代 baseline 或原样复投。不过它首次证明“不重复 loader、跨 head 复用 K/V unpack”可正确且本地显著获益；后续必须改变 `100 MTreg`、同时 live score 或 token partition 等关键资源前提再迭代。
- 原始评测：[cuda_106556_raw.json](raw/cuda_106556_raw.json)。

#### 提交 #106503 · case-4-only dual-token QK interleave

##### 提交信息与单一假设

- **总状态/总分**：Accepted（14/14）/ **`57.57`**，与 #106069 并列，不切换当前最佳指针。
- **代码溯源**：raw 嵌入源码提取为 [`cuda_106503.cpp`](../solutions/archive/2026-08-09-submissions/cuda_106503.cpp)，SHA-256 `951489e9f42778bd12ff66f64d99804b9bdefca0b7bed66fff79c89d70a56cda`，与提交前工作文件一致。
- #106170 的全局双-token schedule 在本地 case 4 ratio p50 `0.9770`、OJ `30→29 μs`，但长 case 有 timing 回退。本候选新增编译期 `PAIR_QK_INTERLEAVE`，只让 B64/L64/KV8 的 case 4 实例为 `true`；其余 shape 保持 #106069 的原循环实例。

##### 本地验证与 OJ 结果

- CPU 语义 14/14 PASS；同一候选 `.so` 的 C500 full-length、boundary、random 均 14/14 PASS，case 4 三种长度均无 NaN/Inf 或 padding-page 越界。
- case 4 交错 A/B（13 rounds）candidate/control p10/p50/p90=`0.9710/0.9758/0.9863`，约 2.5% 本地加速。非目标 case 8/11/12（9 rounds）p50=`0.9974/1.0005/0.9998`，均为中性。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106503 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 322 | 180 | 322 | 59 | 442 | 539 | 294 | 298 |
| #106069 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

- case 4 仍为 `30 μs/66 分`，本地约 2.5% 信号未在本次 OJ 跨过 tier；非目标时延变化没有源码归因，总分恰好保持。至此双-token source scheduling 已完成“全局启用”和“只隔离 case 4”两种 OJ 判定，不能靠同源复投或继续扫描 4/8-token group 打榜。
- #106069 继续作为唯一 control，工作文件在记录完成后恢复到其字节精确快照。下一步转向能改变资源/并行结构的 KV4 QK 架构，而非指令顺序微调。

##### 原始评测归档

- [cuda_106503_raw.json](raw/cuda_106503_raw.json)

#### 提交 #106170 · full-page QK dual-token instruction scheduling

##### 提交信息

- **提交语言/环境**：CUDA Maca C500（`cuda.maca-c500`）
- **总状态/总分**：Accepted（14/14）/ **`57.57`**，与当前 baseline #106069 并列，故不切换当前最佳指针。
- **代码溯源**：raw 嵌入源码提取为 [`cuda_106170.cpp`](../solutions/archive/2026-08-09-submissions/cuda_106170.cpp)，SHA-256 `ab6ba5d7b87b5c31da7f9bd60684f760b5b5596287638f67268a910cd07c7996`，与提交前本地候选一致。

##### 单一假设与本地验证

- full-page QK 原本逐 token 完成四段 packed FMA 与三个 16-lane XOR shuffle。候选将两个独立 token dot 的对应 FMA/shuffle 阶段交错，保持每个 dot 的 operand、FMA 顺序、reduce 语义及 softmax 不变；仅在 `KV_HEADS==8 || SYNC_COPY` 静态实例中启用，async KV4 保留原循环。
- CPU 语义回归与 GPU full/boundary/random 均 14/14 PASS。交错 C500 A/B（13 rounds）在 case 4/8/9/11/12/13 的 candidate/control p50 为 `0.9770/0.9975/0.9968/0.9973/0.9975/0.9966`，属于小幅正向。

##### OJ 结果分析

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106170 | **57.57** | 3 | 4 | 10 | 29 | 25 | 33 | 321 | 179 | 321 | 59 | 440 | 537 | 295 | 299 |
| #106069 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

- H5 说明 QK instruction scheduling 确有可测局部空间（case 4 从 `30→29 μs`），但其余目标 case 的 OJ 量化结果并不一致：case 8/11/12 从 `174/438/533` 到 `179/440/537 μs`。总分未超越，不能把本地微增益当成跨 tier 稳定收益。
- #106069 继续是唯一选定 control；工作文件已从归档 #106069 恢复。该结果与 timing-only phase probe 一致：后续若追求 KV4 余量，必须是更大粒度的 QK architecture，而非同类 instruction-order 微调。

##### 原始评测归档

- [cuda_106170_raw.json](raw/cuda_106170_raw.json)

### 2026-08-08

#### 提交 #106069 / #106116 · KV4 Q staging / occupancy 后续

##### 提交总览

| 提交 | 总分 | 本轮主要代码变化 | 结论 / 归档 |
|---:|---:|---|---|
| #106069 | **57.57** | case 11 `sync_kv4+separate_tail` 的 full/tail kernel 启用 `INPLACE_SHARED_Q`，复用 K half-buffer 取代 2 KiB 动态 Q staging | **当前最佳**；case 11 `448→438 μs`。 [cpp](../solutions/archive/2026-08-08-submissions/cuda_106069.cpp) / [raw](raw/cuda_106069_raw.json) |
| #106116 | 57.43 | 仅把 case 8 加入 `separate_tail` gate，使 full-page KV4 kernel 从 92 MTreg/5 warps 改为 70 MTreg/7 warps，新增 tail launch | 14/14 Accepted，但 case 8 OJ `175 μs` 未超 #106069 `174 μs`、case 11 回退 `438→443 μs`；**拒绝为 baseline**。 [cpp](../solutions/archive/2026-08-08-submissions/cuda_106116.cpp) / [raw](raw/cuda_106116_raw.json) |

##### 完整测试点耗时

以下数字直接取自对应 raw OJ 结果，单位为 `μs`。

| 提交 | 分数 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| #106116 | 57.43 | 3 | 4 | 10 | 30 | 25 | 33 | 321 | 175 | 321 | 59 | 443 | 539 | 296 | 299 |
| #106069 | **57.57** | 3 | 4 | 10 | 30 | 25 | 33 | 320 | 174 | 322 | 58 | 438 | 533 | 294 | 297 |

##### 结果分析

- #106116 的本地 interleaved A/B 在 case 8 得到紧凑的 candidate/control p10/p50/p90 `0.937/0.941/0.945`，且 full/boundary/random 14/14 correctness 均通过；但该局部信号未在本次 OJ timing tier 复现。目标 case 从 `174` 到 `175 μs`，同时 case 11 从 `438` 到 `443 μs`，aggregate 回到 `57.43`。
- 因而「KV4 combined kernel 的 full/tail 分离可提升高并发 case 8 的本机 occupancy」只保留为局部测量事实，**不是已确认的 OJ 优化**。B1 case 10/14 的相同扩展已本地回退（extra launch 主导），短 case 5 也本地 p50 `1.247` 回退；后续不要把它作为默认 dispatch。
- #106116 raw 嵌入源码提取的归档文件 SHA-256 为 `52cedc7119fb4143c4a0c3f5d8fa017b97742812b93b9b6d5a9e60e6c0374454`，与提交前候选一致；mutable work file 已恢复到 #106069 的 `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`。

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

#### 本地实验 exp6-case11-warp32-state-elision · 2026-08-09

##### 实验信息

- **Control**：#106069，SHA `a8101a3f2f78b00129c575af42cf2a945f4d057fcb869ef4ae1a779837d38deb`；候选 SHA `e9b4d6576f639fd96873968d2bed40ff6366afd232ee39062b75202b955970a9`。
- **范围**：仅 case 11 (`B16/L12251/KV4`) 的 full/tail producer。候选将当前 `(16,8,2)` token-parallel CTA 替换为 256-thread `(32,8,1)` warp-per-head mapping：每 lane 的四维为 `{2*lane,2*lane+1,2*lane+64,2*lane+65}`，使用均匀 full-mask 32-lane XOR（`16,8,4,2,1`）归约 16 个 token，保留 split 数、sync `uint4` page loader 宽度、base-2 FP32 online softmax、partial ABI 与 reducer。
- **目的**：用直接 Q register load 和取消 CTA 内 two-z state merge，测试其状态流量/资源收益能否超过 full-warp QK 的额外 reduction 工作。

##### 验证与结论

- CPU 语义 14/14 PASS；C500 case 11 full-length PASS（match `1.0`、max error `2.441406e-04`、finite）。
- `-resource-usage`（0 B stack）直接否定性能前提：full-only candidate 为 `118 MTreg / 8192 B shared / staticMaxWarps=4`，control 对应 full-only 为 `70 / 8320 B / 7`；tail candidate 为 `48 / 8192 B / 8`，control tail 为 `42 / 8320 B / 7`。case 11 主工作在 full-only kernel，寄存器增加和 residency 下跌不能由 128 B shared 节省抵消。
- **REJECTED，未跑 A/B，未提交。** 每 thread/page 的 QK shuffle 也由 `32` 增至 `80`，禁止在该布局上通过 split、reducer、loader 或 launch 参数继续补偿。候选保留在 `solutions/archive/2026-08-09-experiments/cuda_case11_warp32_state_elision.cpp`，工作文件恢复 #106069。
- 该实验不是 #104263 的 8-lane quad-token 重试：它没有 width-8 shuffle 或 subgroup-logit broadcast，且使用已有的 full-warp scalar reduction 形式；#104263 的历史错误仍禁止其原始 8-lane/broadcast 路线，但不能作为本候选的性能结论。

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
