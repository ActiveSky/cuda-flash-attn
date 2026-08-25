# C500 cluster/DSM backend capability probe

Date: 2026-08-23  
Parent/control: #113889 / exp559  
Control SHA-256: `a92f74e6aae22bc8e9a0a08b627ee9441c014cce9d950cf984f23c8987840972`  
Target: `xcore1000`, compiler `/opt/maca/mxgpu_llvm/bin/mxcc` version `1.0.0 (d9102a1572)`

## Scope

This is a compile/lowering probe only. It does not modify the production
workfile, run C500, query OJ, or change project records. The only proposed
mechanism would have been a real cluster-shared/DSM or multicast backend that
could remove a cross-CTA partial round trip.

## Evidence

1. `tests/cluster_backend_probe_compile.cpp` declares the standard LLVM NVVM
   cluster entry points and reaches the `-emit-llvm` stage. The resulting IR
   retains unresolved calls to `llvm.nvvm.read.ptx.sreg.cluster.*`,
   `llvm.nvvm.fence.sc.cluster`, and `llvm.nvvm.barrier.cluster.*`; this is
   front-end acceptance, not a lowering.
2. Compiling the same source to an xcore1000 object fails in instruction
   selection at `llvm.nvvm.barrier.cluster.wait` (`Cannot select`).
3. The isolated matrix in `tests/cluster_backend_probe_variants.cpp` fails
   object generation for every tested cluster entry point:

   | ID | entry point | result |
   |---:|---|---|
   | 1 | `llvm.nvvm.read.ptx.sreg.cluster.ctarank` | `Cannot select` |
   | 2 | `llvm.nvvm.read.ptx.sreg.cluster.nctarank` | `Cannot select` |
   | 3 | `llvm.nvvm.read.ptx.sreg.cluster.ctaid.x` | `Cannot select` |
   | 4 | `llvm.nvvm.read.ptx.sreg.cluster.nctaid.x` | `Cannot select` |
   | 5 | `llvm.nvvm.fence.sc.cluster` | `Cannot select` |
   | 6 | `llvm.nvvm.barrier.cluster.arrive` | `Cannot select` |
   | 7 | `llvm.nvvm.barrier.cluster.wait` | `Cannot select` |
   | 9 | `llvm.nvvm.isspacep.shared.cluster` | `Cannot select` |

   IDs 8/10 (`getctarank.shared.cluster`/`mapa.shared.cluster`) cannot even
   form a valid MACA LLVM module through the declared address-space signature;
   the compiler reports `Broken module found`. This is also not a usable
   backend surface.
4. The bundled CUTE implementation in
   `/opt/maca-3.7.1/include/cute/arch/cluster_sm90.hpp` has
   `CUTE_ARCH_CLUSTER_SM90_ENABLED` commented out. Its default xcore1000 path
   compiles, but the emitted IR contains only `llvm.mxc.block.id.*` and
   dispatch/grid arithmetic; there is no cluster or DSM operation.
5. Forcing the CUTE SM90 path in `tests/cluster_backend_probe_cute_forced.cpp`
   fails at the front end with `invalid % escape in inline assembly string`
   for the cluster register/`mapa` spellings. Raw PTX probes fail too:
   `barrier.cluster.arrive/wait` report `invalid instruction`, while raw
   `mapa.shared::cluster` and
   `cp.async.bulk.shared::cluster...multicast::cluster` report
   `unexpected token at start of statement`.
6. The bridge's host-side multicast/cluster management names are present in
   runtime headers, but they are allocation/launch API aliases. They do not
   provide a device instruction lowering and therefore cannot remove the
   kernel's cross-CTA workspace traffic under the current ABI.

## Decision

**NO CANDIDATE.** There is no compileable and lowered cluster/DSM/cross-CTA
shared-memory or multicast device backend in the installed xcore1000 MACA
toolchain. Do not pre-register, implement, C500-test, A/B-test, or submit a
cluster/DSM candidate under the current ABI. Reopen only if a future toolchain
provides a real xcore1000 device lowering plus launch/ordering and storage
lifetime proof.
