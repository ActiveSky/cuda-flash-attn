# exp680 static audit

Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case14_bf16_hier_tree_exp680.cpp`

Parent control is `#124611 / exp666`, SHA-256
`3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`.
Candidate SHA-256 is recorded in `log/exp680_candidate_sha.log`.

## Workspace proof

The exact dispatch is case14: `batch=1`, `num_heads=32`, `n_split=257`,
`pages_per_split=15`, `HEAD_DIM=128`. Therefore

* `need = 257 * 1 * 32 = 8224` FP32 allocation slots;
* normalized BF16 producer input is 128 BF16 values per slot, i.e. 256
  bytes, and is addressed densely at `reinterpret_cast<bf16*>(partial_acc)`;
  it occupies the first `need * 64 = 526336` FP32 words of the
  `need * 128 = 1052672`-word allocation;
* `group_count = ceil(257/16) = 17`, `group_slots = 17 * 1 * 32 = 544`;
  raw group accumulators need `544 * 128 = 69632` FP32 words;
* `tree_acc = partial_acc + need*64` starts at the exact end of the BF16
  input region and is 256-byte aligned; its end is
  `need*64 + 544*128 = 595968 < need*128 = 1052672` words;
* `partial_l` is not written by the packed-metadata producer. `tree_m` uses
  its first 544 FP32 words and `tree_l` the next 544; `2*544=1088 <= 8224`.
  Both ranges are disjoint and naturally FP32 aligned.

The source has a runtime `tree_storage_ok` guard. The fallback is the parent
raw normalized-BF16 reducer and is unreachable for the exact dispatch above.
No group output overlaps producer BF16 input or packed metadata.

## Live-state and ordering proof

Both producer and group reducer use the fused-tail count
`full_pages>0 ? min(n_split,ceil(full_pages/15)) : tail_present`, so they
agree for tail-only, exact page/split boundaries, short requests, and the full
61519-token request. Group `g` reads only contiguous source splits
`[16*g, min(16*g+16, live_splits))`; inactive groups return before touching
workspace. The raw final reducer receives `pages_per_split=16*15=240` and
`n_split=17`, so its live group count is exactly
`ceil(live_splits/16)`. Every active group rewrites all 128 accumulator
words and both metadata words; inactive group state is not read. This makes
full-short-full and short-full workspace reuse independent of old group data.

The producer, group, and raw final kernels are consecutive launches on the
same default stream; no device-side global synchronization is used. The group
kernel has one CTA per `(group,batch,query_head)` and its output ownership is
distinct from the final 32-CTA reducer ownership.

## Static validation

* normal build: PASS, `build/exp680_candidate_normal.so`;
* resource build: PASS, `build/exp680_candidate_resource.so`;
  current case14 producer `82 MT / 66 ST / 8320 BSM / 0 stack / 5 waves`;
  group reducer `16 MT / 28 ST / 0 static BSM / 0 stack / 8 waves`;
  raw 17-state final reducer `40 MT / 36 ST / 0 static BSM / 0 stack / 8 waves`;
* device LLVM: PASS, `build/exp680_candidate_device.ll`; it contains the
  group launch followed by the raw 17-state final launch with dynamic shared
  sizes 80 and 152 bytes respectively.

No C500, benchmark, or OJ command was run by this task.
