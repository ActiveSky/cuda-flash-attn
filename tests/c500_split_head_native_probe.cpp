#include <stdint.h>
#include <cuda_runtime.h>

// Compare the production split-head QK reduction (rotate8 + BSM XOR4 +
// quad XOR2/1) with an all-mov.shfl network.  The candidate pairs lanes via
// rotate4, assigns heads by tx bit 2, then reduces each head group with
// rotate8 and the same two quad permutations.

template <int MODE>
__device__ __forceinline__ float native_row_shuffle(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union Bits {
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

__device__ __forceinline__ float bsm_row_xor4(float value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    union Bits {
        float f;
        int i;
    } bits;
    bits.f = value;
    const unsigned source_lane = __lane_id() ^ 4u;
    bits.i = __builtin_mxc_bsm_bpermute(source_lane << 2, bits.i);
    return bits.f;
#else
    return __shfl_xor_sync(0xffffffffu, value, 4, 16);
#endif
}

__device__ __forceinline__ float baseline_split_head_reduce(
    float local0, float local1, int tx) {
    const float outbound = (tx & 8) ? local0 : local1;
    const float peer = native_row_shuffle<0x128>(outbound);
    float selected = ((tx & 8) ? local1 : local0) + peer;
    selected += bsm_row_xor4(selected);
    selected += native_row_shuffle<0x04e>(selected);
    selected += native_row_shuffle<0x0b1>(selected);
    return selected;
}

__device__ __forceinline__ float all_native_split_head_reduce(
    float local0, float local1, int tx) {
    // rotate4 toggles tx bit 2.  Each source therefore sends the opposite
    // head needed by its destination.  Afterwards rotate8 and both quad
    // permutations preserve bit 2, reducing eight 2-lane partials per head.
    const float outbound = (tx & 4) ? local0 : local1;
    const float peer = native_row_shuffle<0x124>(outbound);
    float selected = ((tx & 4) ? local1 : local0) + peer;
    selected += native_row_shuffle<0x128>(selected);
    selected += native_row_shuffle<0x04e>(selected);
    selected += native_row_shuffle<0x0b1>(selected);
    return selected;
}

__device__ __forceinline__ float all_native_bit1_split_head_reduce(
    float local0, float local1, int tx) {
    // Pair the two heads through tx bit 1 instead of bit 2.  The remaining
    // bit 0 maps directly to the two token owners used by the z8 producer.
    const float outbound = (tx & 2) ? local0 : local1;
    const float peer = native_row_shuffle<0x04e>(outbound);
    float selected = ((tx & 2) ? local1 : local0) + peer;
    selected += native_row_shuffle<0x124>(selected);
    selected += native_row_shuffle<0x128>(selected);
    selected += native_row_shuffle<0x0b1>(selected);
    return selected;
}

__device__ __forceinline__ float all_native_bit0_split_head_reduce(
    float local0, float local1, int tx) {
    // Pair heads through bit 0; bit 1 then encodes the z8 producer's two
    // token owners. The remaining bit-1/2/3 exchanges reduce eight lanes.
    const float outbound = (tx & 1) ? local0 : local1;
    const float peer = native_row_shuffle<0x0b1>(outbound);
    float selected = ((tx & 1) ? local1 : local0) + peer;
    selected += native_row_shuffle<0x04e>(selected);
    selected += native_row_shuffle<0x124>(selected);
    selected += native_row_shuffle<0x128>(selected);
    return selected;
}

__global__ void split_head_native_runtime_probe_kernel(
    uint32_t* __restrict__ lane_ids,
    float* __restrict__ baseline,
    float* __restrict__ candidate,
    float* __restrict__ bit1_candidate,
    float* __restrict__ bit0_candidate) {
    const unsigned lane = __lane_id();
    const int tx = static_cast<int>(lane & 15u);
    const float local0 = static_cast<float>(lane) + 0.25f;
    const float local1 = static_cast<float>(lane) + 100.5f;
    const int out = static_cast<int>(threadIdx.x);
    lane_ids[out] = lane;
    baseline[out] = baseline_split_head_reduce(local0, local1, tx);
    candidate[out] = all_native_split_head_reduce(local0, local1, tx);
    bit1_candidate[out] =
        all_native_bit1_split_head_reduce(local0, local1, tx);
    bit0_candidate[out] =
        all_native_bit0_split_head_reduce(local0, local1, tx);
}

__global__ void split_head_bsm_codegen_probe_kernel(
    const float* __restrict__ input0,
    const float* __restrict__ input1,
    float* __restrict__ output) {
    const int tx = static_cast<int>(threadIdx.x & 15u);
    output[threadIdx.x] = baseline_split_head_reduce(
        input0[threadIdx.x], input1[threadIdx.x], tx);
}

__global__ void split_head_native_codegen_probe_kernel(
    const float* __restrict__ input0,
    const float* __restrict__ input1,
    float* __restrict__ output) {
    const int tx = static_cast<int>(threadIdx.x & 15u);
    output[threadIdx.x] = all_native_split_head_reduce(
        input0[threadIdx.x], input1[threadIdx.x], tx);
}

extern "C" void run_split_head_native_runtime_probe(
    uint32_t* lane_ids,
    float* baseline,
    float* candidate,
    float* bit1_candidate,
    float* bit0_candidate) {
    split_head_native_runtime_probe_kernel<<<1, 64>>>(
        lane_ids, baseline, candidate, bit1_candidate, bit0_candidate);
}
