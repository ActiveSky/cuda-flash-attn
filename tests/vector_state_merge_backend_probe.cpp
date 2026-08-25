// Compile-only capability probe for xcore1000 vector/warp state-merge backends.
//
// This file is intentionally isolated from the production translation unit.  The
// baseline kernel exercises the widest documented interfaces that could be
// relevant to an FP32 online-softmax state: scalar FP32 atomics, scalar FP32
// warp reduction, and scalar FP32 shuffle, alongside an ordinary float4 value.
// Optional VECTOR_ATOMIC_ATTEMPT and VECTOR_COLLECTIVE_ATTEMPT builds are
// expected capability probes; they are not production code and need not link.
#include <stdint.h>
#include <cuda_runtime.h>

using F32x4 = float __attribute__((ext_vector_type(4)));

__global__ void vector_state_merge_backend_probe_kernel(
    float* __restrict__ state,
    float* __restrict__ output) {
  const unsigned lane = static_cast<unsigned>(threadIdx.x) & 63u;
  F32x4 value = reinterpret_cast<const F32x4*>(state)[lane];

  // These are scalar interfaces only; their presence is recorded to make the
  // negative result precise rather than confusing a missing vector overload
  // with a missing atomic/reduction facility altogether.
  const float old_add = atomicAdd(state + lane * 4u, value.x);
  const float old_max = __reduce_max_sync(~uint64_t(0), value.y);
  const float peer = __shfl_sync(~uint64_t(0), value.z, 0, 64);

#if defined(VECTOR_ATOMIC_ATTEMPT)
  // There is no documented FP32 vector atomicAdd overload in the installed
  // headers.  Keep this deliberate failed probe behind a macro so the
  // baseline remains compilable while the diagnostic captures the exact error.
  (void)atomicAdd(reinterpret_cast<float4*>(state), *reinterpret_cast<float4*>(&value));
#endif

#if defined(VECTOR_COLLECTIVE_ATTEMPT)
  // Likewise, the CUDA/MACA warp collective wrappers accept scalar arithmetic
  // types, not float4/ext_vector_type(4).  This tests whether the compiler adds
  // an undocumented vector overload independently of the headers.
  value = __shfl_sync(~uint64_t(0), value, 0, 64);
#endif

  value.x += old_add;
  value.y += old_max;
  value.z += peer;
  reinterpret_cast<F32x4*>(output)[lane] = value;
}

