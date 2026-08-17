#include <stdint.h>

#include <cuda_bf16.h>
#include <cuda_runtime.h>
#include <math_constants.h>

// Resource-only probe for a case12 changed ownership proposal:
// one 512-thread CTA contains two independent z8 producers, each owning one
// logical split.  Unlike exp556's sequential pair, no thread holds two
// `(m,l,acc)` states.  The groups only share a compact, once-written raw-BF16
// Q tile; their K/V buffers and z trees are disjoint.
//
// It deliberately has no numerical or OJ role.  The question is only whether
// this layout can preserve a spill-free production occupancy tier before an
// end-to-end kernel is designed.

namespace {

constexpr int kHeadDim = 128;
constexpr int kPageTokens = 16;
constexpr int kU32PerRow = kHeadDim / 2;
constexpr int kKvBytes = 2 * kPageTokens * kU32PerRow *
    static_cast<int>(sizeof(uint32_t));
constexpr int kMdBytes = 32 * 2 * static_cast<int>(sizeof(float));
constexpr int kGroupBytes = kKvBytes + kMdBytes;
constexpr int kQBytes = 4 * (kHeadDim / 8) * static_cast<int>(sizeof(uint4));

__device__ __forceinline__ __nv_bfloat16 bf16_from_bits(uint16_t bits) {
    __nv_bfloat16_raw raw;
    raw.x = bits;
    return __nv_bfloat16(raw);
}

__device__ __forceinline__ float bf16_lo(uint32_t value) {
    return __bfloat162float(bf16_from_bits(
        static_cast<uint16_t>(value & 0xffffu)));
}

__device__ __forceinline__ float bf16_hi(uint32_t value) {
    return __bfloat162float(bf16_from_bits(
        static_cast<uint16_t>(value >> 16)));
}

__device__ __forceinline__ float row16_sum(float value) {
    value += __shfl_xor_sync(0xffffffffu, value, 8, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 4, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 2, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 1, 16);
    return value;
}

__device__ __forceinline__ void merge_state(
    float& m, float& l, float* acc,
    float peer_m, float peer_l, const float* peer_acc)
{
    const float all_m = fmaxf(m, peer_m);
    const float self_w = l > 0.f ? __builtin_exp2f(m - all_m) : 0.f;
    const float peer_w = peer_l > 0.f
        ? __builtin_exp2f(peer_m - all_m) : 0.f;
    l = l * self_w + peer_l * peer_w;
    m = all_m;
#pragma unroll
    for (int d = 0; d < 8; ++d) {
        acc[d] = acc[d] * self_w + peer_acc[d] * peer_w;
    }
}

__device__ __forceinline__ void store_state(
    float* s_acc, float (*s_md)[2], int row, int tx,
    float m, float l, const float* acc)
{
    float* dst = s_acc + row * kHeadDim + tx * 8;
#pragma unroll
    for (int d = 0; d < 8; ++d) dst[d] = acc[d];
    if (tx == 0) {
        s_md[row][0] = m;
        s_md[row][1] = l;
    }
}

}  // namespace

__global__ void __launch_bounds__(512)
case12_dual_split_z8_resource_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k_cache,
    const __nv_bfloat16* __restrict__ v_cache,
    float* __restrict__ sink,
    int page_count,
    float sm_scale)
{
    const int tx = static_cast<int>(threadIdx.x);
    const int ty = static_cast<int>(threadIdx.y);
    const int z_all = static_cast<int>(threadIdx.z);
    const int split_in_cta = z_all >> 3;
    const int tz = z_all & 7;
    const int local_h0 = ty;
    const int local_h1 = ty + 2;

    // Two full control-sized 8 KiB K/V+metadata regions are live at once.
    // The final 1 KiB raw Q tile is once-written by the first z8 group and
    // read by both groups before their split-local FP32 reconstruction.
    __shared__ __align__(16) uint8_t
        s_storage[2 * kGroupBytes + kQBytes];
    uint8_t* group_storage = s_storage + split_in_cta * kGroupBytes;
    uint32_t (*s_k)[kU32PerRow] =
        reinterpret_cast<uint32_t (*)[kU32PerRow]>(group_storage);
    uint32_t (*s_v)[kU32PerRow] =
        reinterpret_cast<uint32_t (*)[kU32PerRow]>(
            group_storage + kKvBytes / 2);
    float* s_acc = reinterpret_cast<float*>(group_storage);
    float (*s_md)[2] = reinterpret_cast<float (*)[2]>(
        group_storage + kKvBytes);
    uint4 (*s_q)[kHeadDim / 8] = reinterpret_cast<uint4 (*)[kHeadDim / 8]>(
        s_storage + 2 * kGroupBytes);

    if (split_in_cta == 0 && tz == 0) {
        const uint32_t* q0_src = reinterpret_cast<const uint32_t*>(
            q + local_h0 * kHeadDim) + tx * 4;
        const uint32_t* q1_src = reinterpret_cast<const uint32_t*>(
            q + local_h1 * kHeadDim) + tx * 4;
        s_q[ty][tx] = *reinterpret_cast<const uint4*>(q0_src);
        s_q[ty + 2][tx] = *reinterpret_cast<const uint4*>(q1_src);
    }
    __syncthreads();

    const uint4 qpack0 = s_q[ty][tx];
    const uint4 qpack1 = s_q[ty + 2][tx];
    float q0[8] = {
        bf16_lo(qpack0.x) * sm_scale, bf16_hi(qpack0.x) * sm_scale,
        bf16_lo(qpack0.y) * sm_scale, bf16_hi(qpack0.y) * sm_scale,
        bf16_lo(qpack0.z) * sm_scale, bf16_hi(qpack0.z) * sm_scale,
        bf16_lo(qpack0.w) * sm_scale, bf16_hi(qpack0.w) * sm_scale};
    float q1[8] = {
        bf16_lo(qpack1.x) * sm_scale, bf16_hi(qpack1.x) * sm_scale,
        bf16_lo(qpack1.y) * sm_scale, bf16_hi(qpack1.y) * sm_scale,
        bf16_lo(qpack1.z) * sm_scale, bf16_hi(qpack1.z) * sm_scale,
        bf16_lo(qpack1.w) * sm_scale, bf16_hi(qpack1.w) * sm_scale};

    float m0 = -CUDART_INF_F;
    float m1 = -CUDART_INF_F;
    float l0 = 0.f;
    float l1 = 0.f;
    float acc0[8] = {};
    float acc1[8] = {};

    const int pages = page_count > 0 ? page_count : 1;
    for (int page = 0; page < pages; ++page) {
        const int token = tz * 2 + ty;
        const int base = ((split_in_cta * pages + page) * kPageTokens + token)
            * kHeadDim;
        const uint4 initial_k = *reinterpret_cast<const uint4*>(
            reinterpret_cast<const uint32_t*>(k_cache + base) + tx * 4);
        const uint4 initial_v = *reinterpret_cast<const uint4*>(
            reinterpret_cast<const uint32_t*>(v_cache + base) + tx * 4);
        *reinterpret_cast<uint4*>(&s_k[token][tx * 4]) = initial_k;
        *reinterpret_cast<uint4*>(&s_v[token][tx * 4]) = initial_v;
        __syncthreads();

        const uint4 kpack = *reinterpret_cast<const uint4*>(
            &s_k[token][tx * 4]);
        const float k0 = bf16_lo(kpack.x);
        const float k1 = bf16_hi(kpack.x);
        const float k2 = bf16_lo(kpack.y);
        const float k3 = bf16_hi(kpack.y);
        const float k4 = bf16_lo(kpack.z);
        const float k5 = bf16_hi(kpack.z);
        const float k6 = bf16_lo(kpack.w);
        const float k7 = bf16_hi(kpack.w);
        float dot0 = q0[0] * k0 + q0[1] * k1 + q0[2] * k2 + q0[3] * k3;
        dot0 += q0[4] * k4 + q0[5] * k5 + q0[6] * k6 + q0[7] * k7;
        float dot1 = q1[0] * k0 + q1[1] * k1 + q1[2] * k2 + q1[3] * k3;
        dot1 += q1[4] * k4 + q1[5] * k5 + q1[6] * k6 + q1[7] * k7;
        const float score0 = row16_sum(dot0);
        const float score1 = row16_sum(dot1);

        // These payloads are intentionally live across the softmax/PV body.
        const int next_base = ((split_in_cta * pages + page + 1) *
            kPageTokens + token) * kHeadDim;
        const uint2 next_k01 = *reinterpret_cast<const uint2*>(
            reinterpret_cast<const uint32_t*>(k_cache + next_base) + tx * 2);
        const uint2 next_k23 = *reinterpret_cast<const uint2*>(
            reinterpret_cast<const uint32_t*>(k_cache + next_base) + tx * 2 + 1);
        const uint2 next_v01 = *reinterpret_cast<const uint2*>(
            reinterpret_cast<const uint32_t*>(v_cache + next_base) + tx * 2);
        const uint2 next_v23 = *reinterpret_cast<const uint2*>(
            reinterpret_cast<const uint32_t*>(v_cache + next_base) + tx * 2 + 1);

        const float m_new0 = fmaxf(m0, score0);
        const float m_new1 = fmaxf(m1, score1);
        const float alpha0 = l0 > 0.f ? __builtin_exp2f(m0 - m_new0) : 0.f;
        const float alpha1 = l1 > 0.f ? __builtin_exp2f(m1 - m_new1) : 0.f;
        const float w0 = __builtin_exp2f(score0 - m_new0);
        const float w1 = __builtin_exp2f(score1 - m_new1);
        const uint4 vpack = *reinterpret_cast<const uint4*>(
            &s_v[token][tx * 4]);
        const float vv[8] = {
            bf16_lo(vpack.x), bf16_hi(vpack.x), bf16_lo(vpack.y), bf16_hi(vpack.y),
            bf16_lo(vpack.z), bf16_hi(vpack.z), bf16_lo(vpack.w), bf16_hi(vpack.w)};
        l0 = l0 * alpha0 + w0;
        l1 = l1 * alpha1 + w1;
#pragma unroll
        for (int d = 0; d < 8; ++d) {
            acc0[d] = acc0[d] * alpha0 + w0 * vv[d];
            acc1[d] = acc1[d] * alpha1 + w1 * vv[d];
        }
        m0 = m_new0;
        m1 = m_new1;
        __syncthreads();
        *reinterpret_cast<uint2*>(&s_k[token][tx * 4]) = next_k01;
        *reinterpret_cast<uint2*>(&s_k[token][tx * 4 + 2]) = next_k23;
        *reinterpret_cast<uint2*>(&s_v[token][tx * 4]) = next_v01;
        *reinterpret_cast<uint2*>(&s_v[token][tx * 4 + 2]) = next_v23;
        __syncthreads();
    }

    if (tz >= 4) {
        store_state(s_acc, s_md, (tz - 4) * 4 + local_h0, tx, m0, l0, acc0);
        store_state(s_acc, s_md, (tz - 4) * 4 + local_h1, tx, m1, l1, acc1);
    }
    __syncthreads();
    if (tz < 4) {
        const int peer0 = tz * 4 + local_h0;
        const int peer1 = tz * 4 + local_h1;
        merge_state(m0, l0, acc0, s_md[peer0][0], s_md[peer0][1],
                    s_acc + peer0 * kHeadDim + tx * 8);
        merge_state(m1, l1, acc1, s_md[peer1][0], s_md[peer1][1],
                    s_acc + peer1 * kHeadDim + tx * 8);
    }
    __syncthreads();
    if (tz == 2 || tz == 3) {
        store_state(s_acc, s_md, (tz - 2) * 4 + local_h0, tx, m0, l0, acc0);
        store_state(s_acc, s_md, (tz - 2) * 4 + local_h1, tx, m1, l1, acc1);
    }
    __syncthreads();
    if (tz < 2) {
        const int peer0 = tz * 4 + local_h0;
        const int peer1 = tz * 4 + local_h1;
        merge_state(m0, l0, acc0, s_md[peer0][0], s_md[peer0][1],
                    s_acc + peer0 * kHeadDim + tx * 8);
        merge_state(m1, l1, acc1, s_md[peer1][0], s_md[peer1][1],
                    s_acc + peer1 * kHeadDim + tx * 8);
    }
    __syncthreads();
    if (tz == 1) {
        store_state(s_acc, s_md, local_h0, tx, m0, l0, acc0);
        store_state(s_acc, s_md, local_h1, tx, m1, l1, acc1);
    }
    __syncthreads();
    if (tz == 0) {
        merge_state(m0, l0, acc0, s_md[local_h0][0], s_md[local_h0][1],
                    s_acc + local_h0 * kHeadDim + tx * 8);
        merge_state(m1, l1, acc1, s_md[local_h1][0], s_md[local_h1][1],
                    s_acc + local_h1 * kHeadDim + tx * 8);
        sink[(split_in_cta * 32 + local_h0) * kHeadDim + tx * 8] = acc0[0];
        sink[(split_in_cta * 32 + local_h1) * kHeadDim + tx * 8] = acc1[0];
    }
}
