#include <stdint.h>
#include <cuda_runtime.h>

// Runtime and code-generation probes for BSM bpermute on an xcore1000
// 64-lane wave.  The row-local path validates the production QK XOR
// reduction.  The cross-row path validates broadcasting lane tx in row 0 to
// the same tx in rows 1..3 before that exchange is used by attention code.

__device__ __forceinline__ float raw_row16_xor(float value, int offset) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    const unsigned source_lane = __lane_id() ^ static_cast<unsigned>(offset);
    bits.i = __builtin_mxc_bsm_bpermute(source_lane << 2, bits.i);
    return bits.f;
#else
    return __shfl_xor_sync(0xffffffffu, value, offset, 16);
#endif
}

__device__ __forceinline__ float raw_row0_broadcast(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    const unsigned source_lane = __lane_id() & 15u;
    bits.i = __builtin_mxc_bsm_bpermute(source_lane << 2, bits.i);
    return bits.f;
#else
    return __shfl_sync(~0ull, value, threadIdx.x & 15, 64);
#endif
}

// Exchange the two 32-lane halves of one physical 64-lane wave.  For the
// case13 dim3(16,2,8) producer, lane ^ 32 preserves tx/ty and selects the
// adjacent z partition, exactly matching the proposed pairwise state merge.
__device__ __forceinline__ float raw_wave64_xor32(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    const unsigned source_lane = __lane_id() ^ 32u;
    bits.i = __builtin_mxc_bsm_bpermute(source_lane << 2, bits.i);
    return bits.f;
#else
    return __shfl_xor_sync(~0ull, value, 32, 64);
#endif
}

// Row-local broadcast from an arbitrary tx source.  Every lane in a native
// 16-lane row chooses the same source tx, while the row prefix remains local.
// This is the exact mapping needed by grouped reducers that broadcast one
// split weight to the eight dimensions owned by each tx lane.
__device__ __forceinline__ float raw_row16_broadcast(
    float value, unsigned source_tx) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    const unsigned source_lane = (__lane_id() & ~15u) | (source_tx & 15u);
    bits.i = __builtin_mxc_bsm_bpermute(source_lane << 2, bits.i);
    return bits.f;
#else
    return __shfl_sync(0xffffffffu, value, source_tx, 16);
#endif
}

template <int MODE>
__device__ __forceinline__ float native_row16_shuffle(float value)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union {
        float f;
        int i;
    } bits;
    bits.f = value;
    bits.i = __builtin_mxc_mov_shfl(bits.i, MODE, 0xf, 0xf, 0);
    return bits.f;
#else
    return value;
#endif
}

// MXMACA builtin guide section 3.4.1 defines 0x150..0x15f as native
// row-broadcast modes, with the low nibble selecting source tx.  Validate the
// exact lane-0 mode before using it to distribute online-softmax weights.
__device__ __forceinline__ float native_row16_broadcast0(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return native_row16_shuffle<0x150>(value);
#else
    return __shfl_sync(0xffffffffu, value, 0, 16);
#endif
}

// XOR-8/XOR-4 can be replaced by row rotate-right 8/4 in an all-reduce:
// after the first stage, each pair eight lanes apart already has identical
// state.  XOR-2/XOR-1 are native quad permutations with source maps
// {2,3,0,1} (0x4e) and {1,0,3,2} (0xb1).
__device__ __forceinline__ float native_row16_allreduce(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    value += native_row16_shuffle<0x128>(value);
    value += native_row16_shuffle<0x124>(value);
    value += native_row16_shuffle<0x04e>(value);
    value += native_row16_shuffle<0x0b1>(value);
    return value;
#else
    value += __shfl_xor_sync(0xffffffffu, value, 8, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 4, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 2, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 1, 16);
    return value;
#endif
}

__global__ void bpermute_runtime_probe_kernel(
    float* __restrict__ raw,
    float* __restrict__ wrapped,
    float* __restrict__ row0_broadcast,
    float* __restrict__ row16_broadcast_raw,
    float* __restrict__ row16_broadcast_wrapped,
    float* __restrict__ row16_broadcast_native0,
    float* __restrict__ raw_allreduce,
    float* __restrict__ native_allreduce,
    float* __restrict__ wave64_xor32,
    unsigned* __restrict__ lane_ids)
{
    const unsigned lane = __lane_id();
    const float value = static_cast<float>(lane) + 0.25f;
    const int offsets[4] = {8, 4, 2, 1};
    lane_ids[threadIdx.x] = lane;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        raw[i * 64 + threadIdx.x] = raw_row16_xor(value, offsets[i]);
        wrapped[i * 64 + threadIdx.x] =
            __shfl_xor_sync(0xffffffffu, value, offsets[i], 16);
    }
    row0_broadcast[threadIdx.x] = raw_row0_broadcast(value);
#pragma unroll
    for (unsigned source_tx = 0; source_tx < 16; ++source_tx) {
        row16_broadcast_raw[source_tx * 64 + threadIdx.x] =
            raw_row16_broadcast(value, source_tx);
        row16_broadcast_wrapped[source_tx * 64 + threadIdx.x] =
            __shfl_sync(0xffffffffu, value, source_tx, 16);
    }
    row16_broadcast_native0[threadIdx.x] =
        native_row16_broadcast0(value);
    float raw_sum = value;
    raw_sum += raw_row16_xor(raw_sum, 8);
    raw_sum += raw_row16_xor(raw_sum, 4);
    raw_sum += raw_row16_xor(raw_sum, 2);
    raw_sum += raw_row16_xor(raw_sum, 1);
    raw_allreduce[threadIdx.x] = raw_sum;
    native_allreduce[threadIdx.x] = native_row16_allreduce(value);
    wave64_xor32[threadIdx.x] = raw_wave64_xor32(value);
}

// Keep raw and wrapper variants in separate kernels so their final xcore1000
// machine code can be compared without common-subexpression elimination.
__global__ void bpermute_raw_codegen_probe_kernel(
    const float* __restrict__ input,
    float* __restrict__ output)
{
    float value = input[threadIdx.x];
    value += raw_row16_xor(value, 8);
    value += raw_row16_xor(value, 4);
    value += raw_row16_xor(value, 2);
    value += raw_row16_xor(value, 1);
    output[threadIdx.x] = value;
}

__global__ void bpermute_wrapper_codegen_probe_kernel(
    const float* __restrict__ input,
    float* __restrict__ output)
{
    float value = input[threadIdx.x];
    value += __shfl_xor_sync(0xffffffffu, value, 8, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 4, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 2, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 1, 16);
    output[threadIdx.x] = value;
}

__global__ void bpermute_row0_broadcast_codegen_probe_kernel(
    const float* __restrict__ input,
    float* __restrict__ output)
{
    output[threadIdx.x] = raw_row0_broadcast(input[threadIdx.x]);
}

extern "C" void run_bpermute_runtime_probe(
    float* raw,
    float* wrapped,
    float* row0_broadcast,
    float* row16_broadcast_raw,
    float* row16_broadcast_wrapped,
    float* row16_broadcast_native0,
    float* raw_allreduce,
    float* native_allreduce,
    float* wave64_xor32,
    unsigned* lane_ids)
{
    bpermute_runtime_probe_kernel<<<1, 64>>>(
        raw, wrapped, row0_broadcast, row16_broadcast_raw,
        row16_broadcast_wrapped, row16_broadcast_native0,
        raw_allreduce, native_allreduce, wave64_xor32, lane_ids);
}
