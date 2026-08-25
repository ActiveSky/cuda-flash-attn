# exp692 / #125434 archive record

日期：2026-08-24

## 终态事实

- OJ submission：`#125434`，`Finished/Accepted`，14/14，total score `66.14`。
- case1–14 time/score：`3/92、4/90、9/83、22/73、17/73、28/63、226/55、93/54、231/57、38/62、223/52、377/60、181/57、139/55 µs/分`。
- 唯一预注册 target：case11（B16/KV4/L12251），`223 µs / 52分`，未达到 `>=53分`；主 Agent 已决定关闭 exact adjacent-lane BF16 handoff + even-lane native B128 final-output store contract，不切 control。

## 身份核验

- Raw：`results/raw/cuda_125434_raw.json`，SHA-256 `3af4acf615f43cb8b828e73981a10df46b09c00277eaa092f3964eba715e3e95`。
- Candidate：`solutions/archive/2026-08-24-experiments/cuda_control124611_case11_pair_output_b128_exp692.cpp`，SHA-256 `e0fbec43542bfc6a1c3b4980347d1eaab581086f34d24e26231a4fc8b881b167`。
- Immutable submitted source：`solutions/archive/2026-08-24-submissions/cuda_125434.cpp`，SHA-256 `e0fbec43542bfc6a1c3b4980347d1eaab581086f34d24e26231a4fc8b881b167`。
- Raw embedded code, candidate and immutable source are byte-identical; manifest entry is `solutions/archive/SUBMISSIONS.md` row `#125434`。
- Parent/current control SHA：`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`。

## Archive and submission handling

- Ran `python3 tools/archive_cuda_submissions.py`; it processed existing terminal raw records and regenerated `solutions/archive/SUBMISSIONS.md`。
- The submit path created `#125434` once. The first 3600-second watch timed out; recovery watched the same ID to `Finished/Accepted`. No cancel, parallel submit, or resubmit was performed。
- This record did not modify `AGENTS.md`, `goal.md`, the control, the mutable work file, the candidate source, or any other OJ queue。
