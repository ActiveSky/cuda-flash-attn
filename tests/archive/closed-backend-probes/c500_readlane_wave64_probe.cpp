#include <stdint.h>

#include <cuda_runtime.h>

// Capability-only probe for a different cross-half-wave exchange backend.
// The current z8 producer uses raw BSM bpermute for lane^32; this verifies
// whether the official readlane primitive has the same exact 64-lane payload
// semantics before it is ever considered as a distinct production exchange.

__device__ __forceinline__ float readlane_wave64_xor32(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    bits.i = __builtin_mxc_readlane(bits.i, __lane_id() ^ 32u);
    return bits.f;
#else
    return __shfl_xor_sync(~0ull, value, 32, 64);
#endif
}

__global__ void readlane_wave64_xor32_probe_kernel(
    float* __restrict__ output,
    unsigned* __restrict__ lane_ids) {
    const int tx = threadIdx.x;
    const int ty = threadIdx.y;
    const int tz = threadIdx.z;
    const int linear = (tz * blockDim.y + ty) * blockDim.x + tx;
    const unsigned lane = __lane_id();

    // z0/z1, z2/z3, z4/z5 and z6/z7 each form one physical 64-lane wave.
    // The wave prefix makes every source value unique across the CTA.
    const float value = static_cast<float>((tz >> 1) * 64 + lane) + 0.25f;
    output[linear] = readlane_wave64_xor32(value);
    lane_ids[linear] = lane;
}

extern "C" void run_readlane_wave64_xor32_probe(
    float* output,
    unsigned* lane_ids) {
    readlane_wave64_xor32_probe_kernel<<<1, dim3(16, 2, 8)>>>(
        output, lane_ids);
}
