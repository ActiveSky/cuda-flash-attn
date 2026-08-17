#include <stdint.h>
#include <cuda_runtime.h>

// Isolated xcore1000 FP32 MMA probe from the official MXMACA builtin guide,
// section 3.6.2.  One 64-lane wave supplies A[16,4], B[4,16], and owns four
// C/D values per lane.  Production attention must not use this primitive
// until both the fragment mapping and K=128 FP32 accumulation are validated.

using v4f32 = __NATIVE_VECTOR__(4, float);

__global__ void fp32_mma_k128_probe_kernel(
    const float* __restrict__ a,
    const float* __restrict__ b,
    float* __restrict__ out)
{
    const int lane = static_cast<int>(threadIdx.x);
    // xcore1000's 64-lane fragment mapping follows its four native rows:
    // A lanes select matrix row in the low nibble and K in the row index;
    // B uses the same lane decomposition: column in the low nibble and K in
    // the native-row index.  The basis probe below validates this mapping.
    const int row = lane & 15;
    const int k_lane = lane >> 4;
    const int b_k_lane = lane >> 4;
    const int col = lane & 15;

    v4f32 accum = {0.f, 0.f, 0.f, 0.f};
#pragma unroll
    for (int kb = 0; kb < 32; ++kb) {
        const float av = a[row * 128 + kb * 4 + k_lane];
        const float bv = b[(kb * 4 + b_k_lane) * 16 + col];
        // MCTLASS's row-major A / column-major B wrapper for xcore1000
        // forwards operands to the raw builtin as (B, A).
        accum = __builtin_mxc_mma_16x16x4f32(bv, av, accum);
    }

    // The guide states that 64 lanes collectively own a 16x16 FP32 output.
    // Validate the natural four-contiguous-columns mapping explicitly.
    const int out_col = (lane >> 4) * 4;
    out[row * 16 + out_col + 0] = accum[0];
    out[row * 16 + out_col + 1] = accum[1];
    out[row * 16 + out_col + 2] = accum[2];
    out[row * 16 + out_col + 3] = accum[3];
}

__global__ void fp32_mma_basis_map_kernel(float* __restrict__ out)
{
    const int lane = static_cast<int>(threadIdx.x);
    const int pair = static_cast<int>(blockIdx.x);
    const int a_slot = pair >> 6;
    const int b_slot = pair & 63;
    const float av = lane == a_slot ? 1.f : 0.f;
    const float bv = lane == b_slot ? 1.f : 0.f;
    const v4f32 zero = {0.f, 0.f, 0.f, 0.f};
    const v4f32 result = __builtin_mxc_mma_16x16x4f32(bv, av, zero);
    float* dst = out + pair * 256 + lane * 4;
    dst[0] = result[0];
    dst[1] = result[1];
    dst[2] = result[2];
    dst[3] = result[3];
}

extern "C" void run_fp32_mma_k128_probe(
    const float* a,
    const float* b,
    float* out)
{
    fp32_mma_k128_probe_kernel<<<1, 64>>>(a, b, out);
}

extern "C" void run_fp32_mma_basis_map_probe(float* out)
{
    fp32_mma_basis_map_kernel<<<4096, 64>>>(out);
}
