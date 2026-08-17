#include <stdint.h>

#include <cuda_bf16.h>
#include <cuda_runtime.h>

// Probe the exact wave-local P*V fragment mapping proposed for exp423.
//
// One physical 64-thread C500 wave is laid out as (tx=16, ty=4).  It owns
// eight query heads and four tokens.  A single BF16 m16n16k16 MMA therefore
// computes one 16-column output tile of P[8,4] * V[4,128], with the unused
// eight rows and twelve K positions padded to zero.  Eight independent MMAs
// cover the 128 output dimensions.  The expected lane-local accumulator is:
//
//   c[0] = output[ty,     tx * 8 + d]
//   c[1] = output[ty + 4, tx * 8 + d]
//
// This deliberately uses the same row packing as the proven case11 QK MMA,
// but exercises a strided V column gather and K=4 utilization.
__global__ void __launch_bounds__(64)
bf16_mma_pv_probe_kernel(
    const __nv_bfloat16* __restrict__ probability,
    const __nv_bfloat16* __restrict__ value,
    float* __restrict__ output)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using mma_bf16_vec = _Float16 __attribute__((ext_vector_type(4)));
    using mma_acc_vec = float __attribute__((ext_vector_type(4)));

    const int tx = static_cast<int>(threadIdx.x);
    const int ty = static_cast<int>(threadIdx.y);
    const int row_in_group = tx & 3;
    const int head_group = tx >> 2;

    uint2 a_bits = make_uint2(0u, 0u);
    if (ty == 0 && row_in_group < 2) {
        const int head = head_group + (row_in_group == 1 ? 4 : 0);
        a_bits = *reinterpret_cast<const uint2*>(probability + head * 4);
    }
    const mma_bf16_vec a =
        *reinterpret_cast<const mma_bf16_vec*>(&a_bits);

#pragma unroll
    for (int d = 0; d < 8; ++d) {
        const int dim = tx * 8 + d;
        uint2 b_bits = make_uint2(0u, 0u);
        if (ty == 0) {
            const __nv_bfloat162 b01 = __halves2bfloat162(
                value[0 * 128 + dim], value[1 * 128 + dim]);
            const __nv_bfloat162 b23 = __halves2bfloat162(
                value[2 * 128 + dim], value[3 * 128 + dim]);
            uint32_t lo;
            uint32_t hi;
            static_assert(sizeof(lo) == sizeof(b01), "packed BF16 size");
            lo = *reinterpret_cast<const uint32_t*>(&b01);
            hi = *reinterpret_cast<const uint32_t*>(&b23);
            b_bits = make_uint2(lo, hi);
        }
        const mma_bf16_vec b =
            *reinterpret_cast<const mma_bf16_vec*>(&b_bits);
        mma_acc_vec c = {0.f, 0.f, 0.f, 0.f};
        c = __builtin_mxc_mma_16x16x16bf16(a, b, c);
        output[(ty + 0) * 128 + dim] = c[0];
        output[(ty + 4) * 128 + dim] = c[1];
    }
#else
    (void)probability;
    (void)value;
    (void)output;
#endif
}

extern "C" void run_bf16_mma_pv_probe(
    const __nv_bfloat16* probability,
    const __nv_bfloat16* value,
    float* output)
{
    bf16_mma_pv_probe_kernel<<<1, dim3(16, 4, 1)>>>(
        probability, value, output);
}
