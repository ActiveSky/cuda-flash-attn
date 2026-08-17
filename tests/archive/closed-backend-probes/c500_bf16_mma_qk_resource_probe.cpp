#include <stdint.h>

#include <cuda_bf16.h>
#include <cuda_runtime.h>
#include <mctlass/arch/wmma.h>

// QK-only mapping/resource probe for the current head-pair/z4 producer.
//
// One physical 64-thread C500 wave is laid out as (tx=16, ty=4).  A 16x16
// BF16 MMA tile is arranged so accumulator lane (ty, tx) owns:
//
//   acc[s] = dot(q[ty + 4*s], k[4*z + (tx & 3)]), s in [0, 3]
//
// The production path uses only acc[0]/acc[1] because one KV head owns exactly
// eight query heads.  This probe deliberately fills the two former zero rows
// to determine whether acc[2]/acc[3] are real C500 outputs or inert slots; it
// does not imply a production ownership mapping.  The four tokens belonging to
// the physical z wave are repeated across the sixteen MMA columns, preserving
// the production-relevant lane-local score replication with no shared score
// tile or cross-wave handoff.
__global__ void __launch_bounds__(64)
bf16_mma_qk_resource_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ lane_scores)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using namespace mxmaca;

    const int tx = static_cast<int>(threadIdx.x);
    const int ty = static_cast<int>(threadIdx.y);
    const int z = static_cast<int>(blockIdx.x);
    const int mma_row = tx;
    const int row_in_group = mma_row & 3;
    const int q_owner = mma_row >> 2;
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
        uint2 a_bits = make_uint2(0u, 0u);
        if (row_in_group < 2) {
            a_bits = *reinterpret_cast<const uint2*>(
                q + q_head * 128 + kt * 16 + ty * 4);
        }
        const uint2 b_bits = *reinterpret_cast<const uint2*>(
            k + token * 128 + kt * 16 + ty * 4);

        // MXMACA's row-major BF16 fragment loaders are raw 8-byte moves for
        // A and four bit-preserving BF16-to-storage moves for B.  Populate the
        // same storage directly to isolate the production-relevant register
        // mapping and avoid introducing shared-memory staging in this probe.
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

extern "C" void run_bf16_mma_qk_resource_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* lane_scores)
{
    bf16_mma_qk_resource_probe_kernel<<<4, dim3(16, 4, 1)>>>(
        q, k, lane_scores);
}
