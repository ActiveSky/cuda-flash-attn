// Compile-only capability probe.  This is not a FlashAttention candidate and
// must never be submitted to OJ.  It records whether the installed xcore1000
// front end exposes a global-memory movement primitive beyond the already
// audited register-returning async load and ordinary global stores.
#include <stdint.h>

#include <cuda_runtime.h>
#include <common/irif.h>

using AsyncI4 = __NATIVE_VECTOR__(4, int);

// Keep the known primitives live in device IR so the emitted LLVM identifies
// their lowering.  The async load is the existing register-returning family;
// the two stores are cache-policy variants, not global-to-global engines.
__device__ __forceinline__ AsyncI4 probe_async128(const uint32_t* src) {
#if __has_builtin(__builtin_mxc_load_global_async128)
  return __builtin_mxc_load_global_async128(
      reinterpret_cast<AsyncI4*>(const_cast<uint32_t*>(src)));
#else
  return AsyncI4{};
#endif
}

__device__ __forceinline__ void probe_stx_b16(void* dst, uint16_t payload) {
#if __has_builtin(__builtin_mxc_stx_b16_devc)
  __builtin_mxc_stx_b16_devc(dst, 0, payload);
#else
  (void)dst;
  (void)payload;
#endif
}

__device__ __forceinline__ void probe_stg_b128(void* dst, AsyncI4 payload) {
#if __has_builtin(__builtin_mxc_stg_b128_devc)
  __builtin_mxc_stg_b128_devc(dst, 0, payload);
#else
  (void)dst;
  (void)payload;
#endif
}

__global__ void global_async_backend_probe_kernel(
    const uint32_t* __restrict__ src,
    uint32_t* __restrict__ dst) {
  const int lane = static_cast<int>(threadIdx.x);
  const AsyncI4 value = probe_async128(src + lane * 4);
  if ((lane & 1) == 0) {
    probe_stg_b128(dst + lane * 4, value);
    probe_stx_b16(dst + lane * 4, static_cast<uint16_t>(value[0]));
  }
}

// Host-side declarations are intentionally absent: this translation unit is
// compiled with -emit-llvm -S only, so no GPU execution or ABI integration is
// implied by the probe.

// Capability inventory (kept as preprocessor constants for the report).
#if __has_builtin(__builtin_mxc_load_global_async128)
#define PROBE_HAS_ASYNC128 1
#else
#define PROBE_HAS_ASYNC128 0
#endif

#if __has_builtin(__builtin_mxc_stx_b16_devc)
#define PROBE_HAS_STX_B16_DEVC 1
#else
#define PROBE_HAS_STX_B16_DEVC 0
#endif

#if __has_builtin(__builtin_mxc_stg_b32_devc)
#define PROBE_HAS_STG_B32_DEVC 1
#else
#define PROBE_HAS_STG_B32_DEVC 0
#endif

#if __has_builtin(__builtin_mxc_stg_b64_devc)
#define PROBE_HAS_STG_B64_DEVC 1
#else
#define PROBE_HAS_STG_B64_DEVC 0
#endif

#if __has_builtin(__builtin_mxc_stg_b128_devc)
#define PROBE_HAS_STG_B128_DEVC 1
#else
#define PROBE_HAS_STG_B128_DEVC 0
#endif

#if __has_builtin(__builtin_mxc_stx_b32_devc)
#define PROBE_HAS_STX_B32_DEVC 1
#else
#define PROBE_HAS_STX_B32_DEVC 0
#endif

#if __has_builtin(__builtin_mxc_stx_b64_devc)
#define PROBE_HAS_STX_B64_DEVC 1
#else
#define PROBE_HAS_STX_B64_DEVC 0
#endif

// Candidate source-level names for a genuinely different bulk/cross-CTA
// producer are tested explicitly.  The compiler must expose one of these
// before any production ownership hypothesis can be formed.  A false result
// means only that this spelling is unavailable; the report also inventories
// the compiler strings and installed headers.
#if __has_builtin(__builtin_mxc_cp_async_global_to_shared)
#define PROBE_HAS_CP_ASYNC_G2S 1
#else
#define PROBE_HAS_CP_ASYNC_G2S 0
#endif

#if __has_builtin(__builtin_mxc_cp_async_private_to_shared)
#define PROBE_HAS_CP_ASYNC_P2S 1
#else
#define PROBE_HAS_CP_ASYNC_P2S 0
#endif

#if __has_builtin(__builtin_mxc_load_global_bulk)
#define PROBE_HAS_GLOBAL_BULK_LOAD 1
#else
#define PROBE_HAS_GLOBAL_BULK_LOAD 0
#endif

#if __has_builtin(__builtin_mxc_store_global_bulk)
#define PROBE_HAS_GLOBAL_BULK_STORE 1
#else
#define PROBE_HAS_GLOBAL_BULK_STORE 0
#endif

#if __has_builtin(__builtin_mxc_tma_load)
#define PROBE_HAS_TMA_LOAD 1
#else
#define PROBE_HAS_TMA_LOAD 0
#endif

#if __has_builtin(__builtin_mxc_tma_store)
#define PROBE_HAS_TMA_STORE 1
#else
#define PROBE_HAS_TMA_STORE 0
#endif

#if __has_builtin(__builtin_mxc_multicast)
#define PROBE_HAS_MULTICAST 1
#else
#define PROBE_HAS_MULTICAST 0
#endif

#if __has_builtin(__builtin_mxc_cluster_load)
#define PROBE_HAS_CLUSTER_LOAD 1
#else
#define PROBE_HAS_CLUSTER_LOAD 0
#endif

enum {
  probe_has_async128 = PROBE_HAS_ASYNC128,
  probe_has_stx_b16_devc = PROBE_HAS_STX_B16_DEVC,
  probe_has_stg_b32_devc = PROBE_HAS_STG_B32_DEVC,
  probe_has_stg_b64_devc = PROBE_HAS_STG_B64_DEVC,
  probe_has_stg_b128_devc = PROBE_HAS_STG_B128_DEVC,
  probe_has_stx_b32_devc = PROBE_HAS_STX_B32_DEVC,
  probe_has_stx_b64_devc = PROBE_HAS_STX_B64_DEVC,
  probe_has_cp_async_g2s = PROBE_HAS_CP_ASYNC_G2S,
  probe_has_cp_async_p2s = PROBE_HAS_CP_ASYNC_P2S,
  probe_has_global_bulk_load = PROBE_HAS_GLOBAL_BULK_LOAD,
  probe_has_global_bulk_store = PROBE_HAS_GLOBAL_BULK_STORE,
  probe_has_tma_load = PROBE_HAS_TMA_LOAD,
  probe_has_tma_store = PROBE_HAS_TMA_STORE,
  probe_has_multicast = PROBE_HAS_MULTICAST,
  probe_has_cluster_load = PROBE_HAS_CLUSTER_LOAD,
};
