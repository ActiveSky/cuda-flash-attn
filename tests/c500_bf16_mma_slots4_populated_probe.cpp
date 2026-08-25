#include <stdint.h>

#include <cuda_bf16.h>
#include <cuda_runtime.h>
#include <mctlass/arch/wmma.h>

// Standalone capability probe only.  This is deliberately not a production
// candidate: it asks whether the two A-row groups that were zero-filled by
// the historical QK probe produce real, numerically useful accumulator slots.
//
// The launch and MMA sequence are the minimum common shape of
// c500_bf16_mma_qk_resource_probe.cpp: one 64-thread block, laid out as
// (tx=16, ty=4), four z blocks, and eight chained 16-wide BF16 MMAs.  The
// only capability change is that every row_in_group [0, 3] is populated.
//
// With q shaped [16, 128] and k shaped [16, 128], the intended mapping to be
// checked by the companion driver is, for lane (z, ty, tx):
//
//   token = 4*z + (tx & 3)
//   c[s]  = dot(q[ty + 4*s], k[token]), s = 0..3.
//
// The q_head expression below supplies all sixteen distinct Q rows to the
// custom fragment mapping.  There is no row>=2 zero guard in this probe.
__global__ void __launch_bounds__(64)
bf16_mma_slots4_populated_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ lane_scores)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using namespace mxmaca;

    const int tx = static_cast<int>(threadIdx.x);
    const int ty = static_cast<int>(threadIdx.y);
    const int z = static_cast<int>(blockIdx.x);
    const int row_in_group = tx & 3;
    const int q_owner = tx >> 2;
    const int q_head = q_owner + row_in_group * 4;
    const int token = z * 4 + (tx & 3);

    wmma::fragment<wmma::matrix_a, 16, 16, 16, __nv_bfloat16,
                   wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, __nv_bfloat16,
                   wmma::row_major> b_frag;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;
    wmma::fill_fragment(c_frag, 0.f);

#pragma unroll
    for (int kt = 0; kt < 8; ++kt) {
        // Every row_in_group, including 2 and 3, is loaded from a distinct
        // nonzero Q row supplied by the driver.  Keep the raw 8-byte moves
        // and wmma::mma_sync sequence identical to the historical probe.
        const uint2 a_bits = *reinterpret_cast<const uint2*>(
            q + q_head * 128 + kt * 16 + ty * 4);
        const uint2 b_bits = *reinterpret_cast<const uint2*>(
            k + token * 128 + kt * 16 + ty * 4);
        *reinterpret_cast<uint2*>(&a_frag.x) = a_bits;
        *reinterpret_cast<uint2*>(&b_frag.x) = b_bits;
        wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
    }

    const int out = ((z * 4 + ty) * 16 + tx) * 4;
    lane_scores[out] = c_frag.x[0];
    lane_scores[out + 1] = c_frag.x[1];
    lane_scores[out + 2] = c_frag.x[2];
    lane_scores[out + 3] = c_frag.x[3];
#else
    (void)q;
    (void)k;
    (void)lane_scores;
#endif
}

extern "C" void run_bf16_mma_slots4_populated_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* lane_scores)
{
    bf16_mma_slots4_populated_probe_kernel<<<4, dim3(16, 4, 1)>>>(
        q, k, lane_scores);
}
