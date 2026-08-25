# exp694 case7 raw-wave rebase admission audit

- Parent/current control: `#124611 / exp666`, source SHA
  `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`.
- Isolated candidate:
  `solutions/archive/2026-08-24-experiments/cuda_control124611_case7_raw_wave_rebase_exp694.cpp`
  with source SHA
  `abd65ca70ef44da9f39eec2a0d1fe86af4178eb928a8c21acf0c4df040b934b2`.
- Difference: add an opt-in raw physical-wave `lane^32` first z-state merge
  and enable it only for case7 specialization
  `<true,false,true,false,true>`. Current all-native row-QK, fixed-live-bucket
  page mapping, packed metadata, BF16/FP32 partial ABI, grid and reducer
  contracts remain unchanged elsewhere.
- Normal and `-resource-usage` builds passed. Target resource is
  `80 MTreg / 50 STreg / 8448 B shared / 0 stack / 6 waves`; current case7
  control is `82 / 50 / 8448 / 0 / 5`.
- LLVM build passed. The candidate target specialization contains 20 actual
  `llvm.mxc.bsm.bpermute` calls; the control specialization contains none.
- Real C500 correctness passed: case7 full, boundary, random, exact lengths
  `1,2,15,16,17,687,688,689,703,704,705,1375,1376,1377,2047,2048`, mixed
  per-row lengths, legal padding sentinel trap, and same-process workspace
  reuse. All results were finite and within tolerance.
- OJ status: no submission created. `#125388` was still Pending during this
  audit, so the candidate remains isolated until the queue is terminal and a
  fresh pre-submit identity check is possible.
