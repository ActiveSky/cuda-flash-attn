#include <stdint.h>
#include <cuda_runtime.h>

// Isolate the xcore1000 row-shuffle builtins.  In particular, determine
// whether update_shfl performs arithmetic or merely preserves old destination
// lanes that are disabled by the row/bank masks.

template <int MODE, int ROW_MASK = 0xf, int BANK_MASK = 0xf>
__device__ __forceinline__ uint32_t mov_row(uint32_t value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_mov_shfl(value, MODE, ROW_MASK, BANK_MASK, 0);
#else
    return value;
#endif
}

template <int MODE, int ROW_MASK = 0xf, int BANK_MASK = 0xf>
__device__ __forceinline__ uint32_t update_row(
    uint32_t old_value, uint32_t source_value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_update_shfl(
        old_value, source_value, MODE, ROW_MASK, BANK_MASK, 0);
#else
    return source_value;
#endif
}

template <int MODE>
__device__ __forceinline__ float mov_float(float value) {
    union Bits {
        float f;
        uint32_t u;
    } bits;
    bits.f = value;
    bits.u = mov_row<MODE>(bits.u);
    return bits.f;
}

template <int MODE>
__device__ __forceinline__ float update_float(float value) {
    union Bits {
        float f;
        uint32_t u;
    } bits;
    bits.f = value;
    bits.u = update_row<MODE>(bits.u, bits.u);
    return bits.f;
}

__device__ __forceinline__ float mov_allreduce(float value) {
    value += mov_float<0x128>(value);
    value += mov_float<0x124>(value);
    value += mov_float<0x04e>(value);
    value += mov_float<0x0b1>(value);
    return value;
}

__device__ __forceinline__ float update_allreduce(float value) {
    value += update_float<0x128>(value);
    value += update_float<0x124>(value);
    value += update_float<0x04e>(value);
    value += update_float<0x0b1>(value);
    return value;
}

__global__ void update_shfl_runtime_probe_kernel(
    uint32_t* __restrict__ mov_full,
    uint32_t* __restrict__ update_same_full,
    uint32_t* __restrict__ update_old_full,
    uint32_t* __restrict__ update_row_masks,
    uint32_t* __restrict__ update_bank_masks,
    float* __restrict__ mov_reduce,
    float* __restrict__ update_reduce,
    uint32_t* __restrict__ lane_ids) {
    const uint32_t lane = __lane_id();
    const uint32_t source = 0x10000000u + lane;
    const uint32_t old = 0x70000000u + lane;
    const int out_lane = static_cast<int>(threadIdx.x);
    lane_ids[out_lane] = lane;

#define STORE_FULL(INDEX, MODE)                                             \
    do {                                                                    \
        mov_full[(INDEX) * 64 + out_lane] = mov_row<MODE>(source);          \
        update_same_full[(INDEX) * 64 + out_lane] =                         \
            update_row<MODE>(source, source);                               \
        update_old_full[(INDEX) * 64 + out_lane] =                          \
            update_row<MODE>(old, source);                                  \
    } while (0)
    STORE_FULL(0, 0x128);
    STORE_FULL(1, 0x124);
    STORE_FULL(2, 0x04e);
    STORE_FULL(3, 0x0b1);
#undef STORE_FULL

    // Sweep one mask field at a time for a single, easily recognized rotate
    // mode.  The old/source high nibbles make destination preservation visible
    // without relying on floating-point bit patterns.
#define STORE_ROW_MASK(INDEX, MASK)                                        \
    update_row_masks[(INDEX) * 64 + out_lane] =                            \
        update_row<0x128, MASK, 0xf>(old, source)
    STORE_ROW_MASK(0, 0x0);
    STORE_ROW_MASK(1, 0x1);
    STORE_ROW_MASK(2, 0x3);
    STORE_ROW_MASK(3, 0x5);
    STORE_ROW_MASK(4, 0x7);
    STORE_ROW_MASK(5, 0xf);
#undef STORE_ROW_MASK

#define STORE_BANK_MASK(INDEX, MASK)                                       \
    update_bank_masks[(INDEX) * 64 + out_lane] =                           \
        update_row<0x128, 0xf, MASK>(old, source)
    STORE_BANK_MASK(0, 0x0);
    STORE_BANK_MASK(1, 0x1);
    STORE_BANK_MASK(2, 0x3);
    STORE_BANK_MASK(3, 0x5);
    STORE_BANK_MASK(4, 0x7);
    STORE_BANK_MASK(5, 0xf);
#undef STORE_BANK_MASK

    const float value = static_cast<float>(lane) + 0.25f;
    mov_reduce[out_lane] = mov_allreduce(value);
    update_reduce[out_lane] = update_allreduce(value);
}

// Keep the equivalent networks in separate kernels so optimizer CSE cannot
// hide a code-generation difference between the two builtin spellings.
__global__ void update_shfl_mov_codegen_probe_kernel(
    const float* __restrict__ input, float* __restrict__ output) {
    output[threadIdx.x] = mov_allreduce(input[threadIdx.x]);
}

__global__ void update_shfl_update_codegen_probe_kernel(
    const float* __restrict__ input, float* __restrict__ output) {
    output[threadIdx.x] = update_allreduce(input[threadIdx.x]);
}

extern "C" void run_update_shfl_runtime_probe(
    uint32_t* mov_full,
    uint32_t* update_same_full,
    uint32_t* update_old_full,
    uint32_t* update_row_masks,
    uint32_t* update_bank_masks,
    float* mov_reduce,
    float* update_reduce,
    uint32_t* lane_ids) {
    update_shfl_runtime_probe_kernel<<<1, 64>>>(
        mov_full, update_same_full, update_old_full, update_row_masks,
        update_bank_masks, mov_reduce, update_reduce, lane_ids);
}
