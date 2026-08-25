# exp677 case11 vec4 register-coefficient rebase

Date: 2026-08-24

## Scope

- Parent/control: `#124611 / exp666`,
  `solutions/archive/2026-08-24-submissions/cuda_124611.cpp`
- Parent SHA-256: `3ebd35f58147ccab4de6637f32689384dadc5a4cd68590fd1efd39e3f22bc1fe`
- Candidate: `solutions/archive/2026-08-24-experiments/cuda_control124611_case11_regcoeff_exp677.cpp`
- Candidate SHA-256: `7d2e0f10e8808e9f338395c27601090e8d448a7e3b806f2dd43ce163a8938c4e`
- Historical mechanism: exp504 (`2bf461f6ed3562d7095f24feed1489b01308610dd20506f8f902b86b3053c602`)

The candidate is a byte-for-byte control copy before the following two source
hunks:

1. Add `REGISTER_ALL_COEFFICIENTS=false` as the fourth template bool of
   `paged_decode_reduce_vec4_kernel`.  The true branch retains two owner-lane
   `(m,l)` pairs (`s0=lane`, `s1=lane+32`) and derives both weights in
   registers.  Accumulator consumers obtain the selected weight with
   `__shfl_sync`; the true branch does not materialize `s_m` or `s_w`.
2. Only the `num_heads_k==4 && batch_size==16 && seqlen_k==12251` dispatch
   passes the fourth bool as `true` and changes dynamic shared memory from
   `2*reduce_splits*sizeof(float)` to zero.  The case8 vec4 call remains the
   default-false instance with its original shared-memory expression.

The producer signatures, partial `float*` ABI, split count, fused-tail bool,
grid (`batch_size*32`), and block (`32`) are unchanged.  No C500, benchmark,
correctness harness, or OJ command was run in this static task.

## Static builds

All six manual `mxcc` builds completed successfully (the build script was not
used because it runs a C500 probe automatically):

- `build/exp677_candidate_normal.so`
- `build/exp677_control_normal.so`
- `build/exp677_candidate_resource.so`
- `build/exp677_control_resource.so`
- `build/exp677_candidate_device.ll`
- `build/exp677_control_device.ll`

Corresponding command output is in the six `log/exp677_{candidate,control}_*.log`
files.

## Resource comparison

`-resource-usage` exposed 31 control rows and 32 candidate rows.  Every
pre-existing row matched exactly; the extra row is the new true template
specialization.  Relevant vec4 rows:

| instance | MTreg | STreg | shared | stack | staticMaxWarps/PEU |
|---|---:|---:|---:|---:|---:|
| control/candidate case8 vec4 (`REGISTER_ALL_COEFFICIENTS=false`) | 64 | 35 | 0 | 0 | 8 |
| control vec4 reducer | 64 | 35 | 0 | 0 | 8 |
| candidate case11 vec4 (`REGISTER_ALL_COEFFICIENTS=true`) | 26 | 26 | 0 | 0 | 8 |

No spill, stack frame, or wave-count regression was observed.  The case11
candidate launch requests zero dynamic shared bytes; the control requests
`2*39*4 = 312` bytes for its `s_m/s_w` arrays.

## Device LLVM checks

The candidate true vec4 kernel has direct global loads of the two owned
`partial_m/partial_l` pairs, bpermute lowering for the max/sum and coefficient
shuffles, and no `addrspace(3)` shared-memory access or barrier in that kernel.
The default-false vec4 kernel retains the control shared-memory path.  Both
kernel stubs and registrations are present, and the dispatch order selects the
false specialization for case8 and true specialization only for case11.

## Minimum follow-up correctness set

Before any online probe, run at least case11 target-shape smoke/full,
boundary, random, and padding-trap checks, plus same-process workspace reuse
(`full -> short -> full` and `short -> full`).  Include exact lengths around
the page/split transitions:

`1,2,15,16,17,319,320,321,639,640,641,12159,12160,12161,12239,12240,12241,12250,12251`

The case11 producer/partial contract is unchanged, but the reducer's no-shared
branch should be checked for inactive-split and fused-tail behavior before the
main Agent makes an admission or submission decision.
