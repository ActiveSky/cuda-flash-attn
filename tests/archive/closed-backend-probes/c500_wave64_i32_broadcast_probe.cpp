#include <stdint.h>

#include <cuda_runtime.h>

// Capability gate for a fixed-source 64-lane page-ID broadcast in the exact
// dim3(16,2,8) KV8 producer geometry.  It is deliberately a raw int32 move:
// no floating-point conversion is permitted for block-table indices.
__device__ __forceinline__ int32_t raw_wave64_broadcast_i32(int32_t value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    const unsigned source_lane = __lane_id() & ~63u;
    return __builtin_mxc_bsm_bpermute(source_lane << 2, value);
#else
    return __shfl_sync(~0ull, value, 0, 64);
#endif
}

__global__ void wave64_i32_broadcast_probe_kernel(
    int32_t* __restrict__ output,
    unsigned* __restrict__ lanes) {
    const int linear =
        (threadIdx.z * blockDim.y + threadIdx.y) * blockDim.x + threadIdx.x;
    const unsigned lane = __lane_id();
    const int wave = linear >> 6;
    // Each physical 64-lane wave has a different raw payload, while only its
    // fixed lane-zero source holds that payload before the exchange.
    const int32_t value = lane == 0
        ? static_cast<int32_t>(0x13570000 + wave)
        : static_cast<int32_t>(0x7f7f7f7f);
    output[linear] = raw_wave64_broadcast_i32(value);
    lanes[linear] = lane;
}

extern "C" void run_wave64_i32_broadcast_probe(
    int32_t* output,
    unsigned* lanes) {
    wave64_i32_broadcast_probe_kernel<<<1, dim3(16, 2, 8)>>>(output, lanes);
}
