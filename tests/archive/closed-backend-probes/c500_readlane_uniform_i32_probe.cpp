#include <stdint.h>

#include <cuda_runtime.h>

// A deliberately narrower capability question than the archived lane^32
// probe: does the official readlane backend broadcast a fixed int32 source
// inside each physical 64-lane z8 wave?  That is the only semantic needed by
// a uniform block-table page ID; this probe does not test a peer permutation.
__device__ __forceinline__ int32_t readlane_wave64_uniform_i32(int32_t value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_readlane(value, 0u);
#else
    return __shfl_sync(~0ull, value, 0, 64);
#endif
}

__global__ void readlane_uniform_i32_probe_kernel(
    int32_t* __restrict__ output,
    unsigned* __restrict__ lanes) {
    const int linear =
        (threadIdx.z * blockDim.y + threadIdx.y) * blockDim.x + threadIdx.x;
    const unsigned lane = __lane_id();
    const int wave = linear >> 6;
    const int32_t value = lane == 0
        ? static_cast<int32_t>(0x24680000 + wave)
        : static_cast<int32_t>(0x7f7f7f7f);
    output[linear] = readlane_wave64_uniform_i32(value);
    lanes[linear] = lane;
}

extern "C" void run_readlane_uniform_i32_probe(
    int32_t* output,
    unsigned* lanes) {
    readlane_uniform_i32_probe_kernel<<<1, dim3(16, 2, 8)>>>(output, lanes);
}
