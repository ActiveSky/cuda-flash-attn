#include <stdint.h>

#include <cuda_bf16.h>
#include <cuda_runtime.h>

// Validate the lane-local BF16-MMA mapping needed by the long-KV8
// head-pair/z8 producer.  A physical C500 wave spans two logical z values:
//
//   lane row = ty + 2 * (tz & 1),  tx = 0..15
//
// The four MMA columns in that wave are the four tokens owned by the z pair.
// Q rows are duplicated so rows 0/2 produce heads 0/2 and rows 1/3 produce
// heads 1/3.  The production consumer will select columns 0/1 for even z and
// columns 2/3 for odd z without materializing a shared score tile.
__global__ void __launch_bounds__(256)
bf16_mma_qk_kv8_z8_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k,
    float* __restrict__ lane_scores)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    using mma_bf16_vec = _Float16 __attribute__((ext_vector_type(4)));
    using mma_acc_vec = float __attribute__((ext_vector_type(4)));

    const int tx = static_cast<int>(threadIdx.x);
    const int ty = static_cast<int>(threadIdx.y);
    const int tz = static_cast<int>(threadIdx.z);
    const int z_in_wave = tz & 1;
    const int wave_row = ty + 2 * z_in_wave;
    const int row_in_group = tx & 3;
    const int q_owner = tx >> 2;
    const int q_head = (q_owner & 1) + (row_in_group == 1 ? 2 : 0);
    const int token = (tz >> 1) * 4 + (tx & 3);

    mma_acc_vec c = {0.f, 0.f, 0.f, 0.f};
#pragma unroll
    for (int kt = 0; kt < 8; ++kt) {
        uint2 a_bits = make_uint2(0u, 0u);
        if (row_in_group < 2) {
            a_bits = *reinterpret_cast<const uint2*>(
                q + q_head * 128 + kt * 16 + wave_row * 4);
        }
        const uint2 b_bits = *reinterpret_cast<const uint2*>(
            k + token * 128 + kt * 16 + wave_row * 4);
        const mma_bf16_vec a =
            *reinterpret_cast<const mma_bf16_vec*>(&a_bits);
        const mma_bf16_vec b =
            *reinterpret_cast<const mma_bf16_vec*>(&b_bits);
        c = __builtin_mxc_mma_16x16x16bf16(a, b, c);
    }

    const int out = ((tz * 2 + ty) * 16 + tx) * 2;
    lane_scores[out] = c[0];
    lane_scores[out + 1] = c[1];
#else
    (void)q;
    (void)k;
    (void)lane_scores;
#endif
}

extern "C" void run_bf16_mma_qk_kv8_z8_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k,
    float* lane_scores)
{
    bf16_mma_qk_kv8_z8_probe_kernel<<<1, dim3(16, 2, 8)>>>(
        q, k, lane_scores);
}
