# Alternate source admission audit: `solutions/cuda_maca_version.cpp`

Date: 2026-08-23

## Provenance

- Audited source SHA-256: `a56c12f7d64ffe548204b089a4b36e9c9f8bfabb2db5ce358090178a40e85627`.
- It is tracked in git. `git show e6cbbcf:solutions/cuda_maca_version.cpp` is byte-identical to the immutable `#104441` source SHA `f8930880fb083124f4807c834cc44bcd1abbcb8125cb85530d26c86b218090f2`; commit `ff52ec8` changes only the host `use_mma_qk` dispatch block, making the audited source a local rollback with `use_mma_qk = false`.
- `solutions/archive/2026-08-07-submissions/cuda_104441.cpp` has SHA `f8930880...` and differs from the audited source only in that dispatch block. The audited source is not byte-identical to `#104441` and has no matching OJ raw/archive SHA.
- `solutions/archive/2026-08-08-submissions/cuda_105492.cpp` has SHA `5c803827...` and is a different derivative: it adds empty-split early returns/live-split reduction and removes page-beta rescaling. The audited source retains the old beta path, scans all `n_split`, and has no new ABI/backend.
- Current structural control remains `#113889` / exp559, SHA `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`; the audited source is not the control and is far older (1053 lines vs. the 5974-line control snapshot).

## Mechanism/closure audit

The source contains only the historical scalar/paired-token QK path, old shape-specific `n_split` policy, synchronous shared K/V page loader, FP32 `(m,l,acc)` global partial workspace, and a disabled WMMA MMA-QK candidate. The enabled `use_qk_pair` dispatch is the already accepted historical paired-token QK family documented for #104217/#104441; the WMMA path is disabled and its precision contract is closed in `notes.md` (MMA-QK precision block) and the current AGENTS closure rules. There is no new Q/K/V consumer backend, cross-request flow, producer/reducer ownership change, partial-format/storage lifetime change, cross-CTA storage, or synchronization ABI.

Therefore this file is historical/closed material, not an unregistered candidate.

## Admission result

**NO CANDIDATE. NO BUILD. NO C500. NO A/B. NO OJ.**

No production or shared record was changed; the workfile and OJ queue were not touched.
