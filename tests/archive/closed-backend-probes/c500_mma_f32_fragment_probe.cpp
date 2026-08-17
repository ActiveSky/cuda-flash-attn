#include <stdint.h>
#include <cuda_runtime.h>
#include <cuda_bf16.h>

// Runtime mapping probe for the xcore1000 native FP32 MMA instruction.
// Each block evaluates one pair of one-hot A/B fragment lanes.  The output is
// kept lane-major so the companion Python script can recover the exact input
// compatibility classes and accumulator lane/slot mapping without assuming
// CUDA/NVIDIA warp semantics.
using ProbeFloat4 = __NATIVE_VECTOR__(4, float);

__global__ void mma_f32_fragment_probe_kernel(float* __restrict__ output) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    const int pair = (int)blockIdx.x;
    const int a_lane = pair >> 6;
    const int b_lane = pair & 63;
    const int lane = (int)threadIdx.x;
    const float a = lane == a_lane ? 1.f : 0.f;
    const float b = lane == b_lane ? 1.f : 0.f;
    const ProbeFloat4 zero = {0.f, 0.f, 0.f, 0.f};
    const ProbeFloat4 result = __builtin_mxc_mma_16x16x4f32(a, b, zero);
    float* dst = output + ((pair * 64 + lane) * 4);
#pragma unroll
    for (int i = 0; i < 4; ++i) dst[i] = result[i];
#else
    (void)output;
#endif
}

__global__ void mma_f32_k128_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ output) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    const int lane = (int)threadIdx.x;
    const int fragment_k = lane >> 4;
    const int fragment_index = lane & 15;
    ProbeFloat4 acc = {0.f, 0.f, 0.f, 0.f};
#pragma unroll
    for (int k_base = 0; k_base < 128; k_base += 4) {
        const int kk = k_base + fragment_k;
        const float a = __bfloat162float(q[fragment_index * 128 + kk]);
        const float b = __bfloat162float(k[fragment_index * 128 + kk]);
        acc = __builtin_mxc_mma_16x16x4f32(a, b, acc);
    }
    const int row_base = fragment_k * 4;
    const int col = fragment_index;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        output[(row_base + i) * 16 + col] = acc[i];
    }
#else
    (void)q;
    (void)k;
    (void)output;
#endif
}

extern "C" void run_mma_f32_fragment_probe(float* output) {
    mma_f32_fragment_probe_kernel<<<4096, 64>>>(output);
}

extern "C" void run_mma_f32_k128_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* output) {
    mma_f32_k128_probe_kernel<<<1, 64>>>(q, k, output);
}
