#include <stdint.h>
#include <cuda_runtime.h>
#include <cuda_bf16.h>
#include <mctlass/arch/wmma.h>

// Diagnose the xcore1000 BF16 MMA precision wall without changing production.
// The chained result is the usual K=128 accumulator.  The eight tile outputs
// instead start every K=16 MMA from exact zero, allowing the host to merge the
// tiles in FP32 and distinguish intra-instruction error from cross-tile state
// accumulation error.
__global__ void mma_bf16_block_accum_precision_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ chained,
    float* __restrict__ zero_started_tiles)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using namespace mxmaca;
    const int tid = static_cast<int>(threadIdx.x);

    __shared__ __nv_bfloat16 s_a[16][16];
    __shared__ __nv_bfloat16 s_b[16][16];

    wmma::fragment<wmma::matrix_a, 16, 16, 16, __nv_bfloat16,
                   wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, __nv_bfloat16,
                   wmma::row_major> b_frag;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> chain_frag;
    wmma::fill_fragment(chain_frag, 0.f);

#pragma unroll 1
    for (int kt = 0; kt < 8; ++kt) {
        for (int idx = tid; idx < 256; idx += 64) {
            const int row = idx >> 4;
            const int col = idx & 15;
            s_a[row][col] = q[row * 128 + kt * 16 + col];
            s_b[row][col] = k[col * 128 + kt * 16 + row];
        }
        __syncthreads();
        wmma::load_matrix_sync(a_frag, &s_a[0][0], 16);
        wmma::load_matrix_sync(b_frag, &s_b[0][0], 16);

        wmma::fragment<wmma::accumulator, 16, 16, 16, float> tile_frag;
        wmma::fill_fragment(tile_frag, 0.f);
        wmma::mma_sync(tile_frag, a_frag, b_frag, tile_frag);
        wmma::store_matrix_sync(
            zero_started_tiles + kt * 256, tile_frag, 16,
            wmma::mem_row_major);

        wmma::mma_sync(chain_frag, a_frag, b_frag, chain_frag);
        __syncthreads();
    }
    wmma::store_matrix_sync(chained, chain_frag, 16, wmma::mem_row_major);
#else
    (void)q;
    (void)k;
    (void)chained;
    (void)zero_started_tiles;
#endif
}

extern "C" void run_mma_bf16_block_accum_precision_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* chained,
    float* zero_started_tiles)
{
    mma_bf16_block_accum_precision_probe_kernel<<<1, 64>>>(
        q, k, chained, zero_started_tiles);
}
