#include <stdint.h>
#include <cuda_runtime.h>
#include <cuda_bf16.h>
#include <cuda_fp16.h>
#include <mctlass/arch/wmma.h>

// Compare the xcore1000 FP16-input and BF16-input 16x16x16 MMA paths on the
// exact K=128 dot-product shape used by decode attention.  Inputs originate as
// BF16.  FP16 conversion is exact for the ordinary finite range used by the
// harness, so a lower error directly tests whether the FP16 MMA accumulation
// path changes the precision premise that invalidated production BF16 MMA-QK.

template <bool USE_FP16>
__global__ void mma_f16_bf16_k128_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ output)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using namespace mxmaca;
    const int tid = static_cast<int>(threadIdx.x);

    __shared__ __half s_a_f16[16][16];
    __shared__ __half s_b_f16[16][16];
    __shared__ __nv_bfloat16 s_a_bf16[16][16];
    __shared__ __nv_bfloat16 s_b_bf16[16][16];

    if constexpr (USE_FP16) {
        wmma::fragment<wmma::matrix_a, 16, 16, 16, __half,
                       wmma::row_major> a_frag;
        wmma::fragment<wmma::matrix_b, 16, 16, 16, __half,
                       wmma::row_major> b_frag;
        wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;
        wmma::fill_fragment(c_frag, 0.f);
#pragma unroll
        for (int kt = 0; kt < 8; ++kt) {
            for (int idx = tid; idx < 256; idx += 64) {
                const int row = idx >> 4;
                const int col = idx & 15;
                s_a_f16[row][col] = __float2half_rn(
                    __bfloat162float(q[row * 128 + kt * 16 + col]));
                s_b_f16[row][col] = __float2half_rn(
                    __bfloat162float(k[col * 128 + kt * 16 + row]));
            }
            __syncthreads();
            wmma::load_matrix_sync(a_frag, &s_a_f16[0][0], 16);
            wmma::load_matrix_sync(b_frag, &s_b_f16[0][0], 16);
            wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
            __syncthreads();
        }
        wmma::store_matrix_sync(output, c_frag, 16, wmma::mem_row_major);
    } else {
        wmma::fragment<wmma::matrix_a, 16, 16, 16, __nv_bfloat16,
                       wmma::row_major> a_frag;
        wmma::fragment<wmma::matrix_b, 16, 16, 16, __nv_bfloat16,
                       wmma::row_major> b_frag;
        wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;
        wmma::fill_fragment(c_frag, 0.f);
#pragma unroll
        for (int kt = 0; kt < 8; ++kt) {
            for (int idx = tid; idx < 256; idx += 64) {
                const int row = idx >> 4;
                const int col = idx & 15;
                s_a_bf16[row][col] = q[row * 128 + kt * 16 + col];
                s_b_bf16[row][col] = k[col * 128 + kt * 16 + row];
            }
            __syncthreads();
            wmma::load_matrix_sync(a_frag, &s_a_bf16[0][0], 16);
            wmma::load_matrix_sync(b_frag, &s_b_bf16[0][0], 16);
            wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
            __syncthreads();
        }
        wmma::store_matrix_sync(output, c_frag, 16, wmma::mem_row_major);
    }
#else
    (void)q;
    (void)k;
    (void)output;
#endif
}

extern "C" void run_mma_f16_bf16_k128_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* output_f16,
    float* output_bf16)
{
    mma_f16_bf16_k128_probe_kernel<true><<<1, 64>>>(q, k, output_f16);
    mma_f16_bf16_k128_probe_kernel<false><<<1, 64>>>(q, k, output_bf16);
}
