#include <stdint.h>
#include <cuda_runtime.h>

// Compare the low-level mov_raw_shfl used by CUTE register transposes with
// the production mov_shfl spelling for the exact four-mode row allreduce.

template <int MODE>
__device__ __forceinline__ uint32_t mov_row(uint32_t value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_mov_shfl(value, MODE, 0xf, 0xf, false);
#else
    return value;
#endif
}

template <int MODE>
__device__ __forceinline__ uint32_t raw_row(uint32_t value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_mov_raw_shfl(value, MODE, 0xf, 0xf, false);
#else
    return value;
#endif
}

template <int MODE, bool RAW>
__device__ __forceinline__ float shuffle_float(float value) {
    union Bits {
        float f;
        uint32_t u;
    } bits;
    bits.f = value;
    if constexpr (RAW) {
        bits.u = raw_row<MODE>(bits.u);
    } else {
        bits.u = mov_row<MODE>(bits.u);
    }
    return bits.f;
}

template <bool RAW>
__device__ __forceinline__ float allreduce(float value) {
    value += shuffle_float<0x128, RAW>(value);
    value += shuffle_float<0x124, RAW>(value);
    value += shuffle_float<0x04e, RAW>(value);
    value += shuffle_float<0x0b1, RAW>(value);
    return value;
}

__global__ void raw_shfl_runtime_probe_kernel(
    uint32_t* __restrict__ mov_values,
    uint32_t* __restrict__ raw_values,
    float* __restrict__ mov_reduce,
    float* __restrict__ raw_reduce,
    uint32_t* __restrict__ lane_ids) {
    const uint32_t lane = __lane_id();
    const uint32_t value = 0x10000000u + lane;
    const int out_lane = static_cast<int>(threadIdx.x);
    lane_ids[out_lane] = lane;
#define STORE(INDEX, MODE)                                                  \
    do {                                                                    \
        mov_values[(INDEX) * 64 + out_lane] = mov_row<MODE>(value);         \
        raw_values[(INDEX) * 64 + out_lane] = raw_row<MODE>(value);         \
    } while (0)
    STORE(0, 0x128);
    STORE(1, 0x124);
    STORE(2, 0x04e);
    STORE(3, 0x0b1);
#undef STORE
    const float input = static_cast<float>(lane) + 0.25f;
    mov_reduce[out_lane] = allreduce<false>(input);
    raw_reduce[out_lane] = allreduce<true>(input);
}

__global__ void raw_shfl_mov_codegen_probe_kernel(
    const float* __restrict__ input, float* __restrict__ output) {
    output[threadIdx.x] = allreduce<false>(input[threadIdx.x]);
}

__global__ void raw_shfl_raw_codegen_probe_kernel(
    const float* __restrict__ input, float* __restrict__ output) {
    output[threadIdx.x] = allreduce<true>(input[threadIdx.x]);
}

extern "C" void run_raw_shfl_runtime_probe(
    uint32_t* mov_values,
    uint32_t* raw_values,
    float* mov_reduce,
    float* raw_reduce,
    uint32_t* lane_ids) {
    raw_shfl_runtime_probe_kernel<<<1, 64>>>(
        mov_values, raw_values, mov_reduce, raw_reduce, lane_ids);
}
