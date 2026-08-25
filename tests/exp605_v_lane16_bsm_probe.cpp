#include <stdint.h>
#include <cuda_runtime.h>

// Minimal exp605 capability check.  A dim3(16,2,8) block maps each physical
// 64-lane wave as lane=(tz&1)*32 + ty*16 + tx.  lane^16 must therefore select
// the other ty at the same tx and z, and all four words of one V payload must
// follow that same mapping.
__device__ __forceinline__ uint32_t exp605_raw_bsm_lane16(
    uint32_t value)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    const unsigned peer_lane = __lane_id() ^ 16u;
    return __builtin_mxc_bsm_bpermute(peer_lane << 2, value);
#else
    return value;
#endif
}

__global__ void exp605_v_lane16_bsm_probe_kernel(uint32_t* output)
{
    const int tx = threadIdx.x;
    const int ty = threadIdx.y;
    const int tz = threadIdx.z;
    const int row = (tz * 2 + ty) * 16 + tx;
    const uint32_t base = (static_cast<uint32_t>(tz) << 24) |
        (static_cast<uint32_t>(ty) << 16) |
        (static_cast<uint32_t>(tx) << 8);
    output[row * 4 + 0] = exp605_raw_bsm_lane16(base | 0u);
    output[row * 4 + 1] = exp605_raw_bsm_lane16(base | 1u);
    output[row * 4 + 2] = exp605_raw_bsm_lane16(base | 2u);
    output[row * 4 + 3] = exp605_raw_bsm_lane16(base | 3u);
}

extern "C" void run_exp605_v_lane16_bsm_probe(uint32_t* output)
{
    exp605_v_lane16_bsm_probe_kernel<<<1, dim3(16, 2, 8)>>>(output);
}
