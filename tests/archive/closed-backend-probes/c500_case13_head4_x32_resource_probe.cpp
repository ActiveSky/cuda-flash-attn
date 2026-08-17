#include <stdint.h>

#include <cuda_bf16.h>
#include <math_constants.h>
#include <cuda_runtime.h>

// Resource-only feasibility probe for a different case13 KV8 producer
// ownership.  It deliberately models the full hot state rather than a tiny
// arithmetic microkernel:
//
//   control: dim3(16, 2, 8), 2 query heads x 8 output dims/thread
//   probe:   dim3(32, 1, 8), 4 query heads x 4 output dims/thread
//
// Both layouts have 256 threads and keep 16 Q plus 16 accumulator scalars per
// thread.  The probe makes all four heads consume the same K/V payload, uses
// two tokens per z partition, preserves eight next-page K/V uint32 payload
// registers across PV, and exercises the same three-stage 8->4->2->1 z tree.
// It has no numerical/OJ role: its only question is whether the changed
// x=32/head4 state can retain a spill-free five-wave C500 resource tier.

namespace {

constexpr int kHeadDim = 128;
constexpr int kPageTokens = 16;
constexpr int kU32PerRow = kHeadDim / 2;
constexpr int kKvBytes = 2 * kPageTokens * kU32PerRow *
    static_cast<int>(sizeof(uint32_t));
constexpr int kMdBytes = 32 * 2 * static_cast<int>(sizeof(float));

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

__device__ __forceinline__ float row32_sum(float value) {
    value += __shfl_xor_sync(0xffffffffu, value, 16);
    value += __shfl_xor_sync(0xffffffffu, value, 8);
    value += __shfl_xor_sync(0xffffffffu, value, 4);
    value += __shfl_xor_sync(0xffffffffu, value, 2);
    value += __shfl_xor_sync(0xffffffffu, value, 1);
    return value;
}

__device__ __forceinline__ void merge_head_state(
    float& m, float& l, float* acc,
    float peer_m, float peer_l, const float* peer_acc)
{
    const float merged_m = fmaxf(m, peer_m);
    const float self_scale = l > 0.f ? __builtin_exp2f(m - merged_m) : 0.f;
    const float peer_scale = peer_l > 0.f
        ? __builtin_exp2f(peer_m - merged_m) : 0.f;
    l = l * self_scale + peer_l * peer_scale;
    m = merged_m;
#pragma unroll
    for (int d = 0; d < 4; ++d) {
        acc[d] = acc[d] * self_scale + peer_acc[d] * peer_scale;
    }
}

}  // namespace

__global__ void __launch_bounds__(256)
case13_head4_x32_z8_resource_probe_kernel(
    const __nv_bfloat16* __restrict__ q,
    const __nv_bfloat16* __restrict__ k_cache,
    const __nv_bfloat16* __restrict__ v_cache,
    float* __restrict__ sink,
    int page_count,
    float sm_scale)
{
    const int tx = static_cast<int>(threadIdx.x);
    const int tz = static_cast<int>(threadIdx.z);
    const int token0 = tz * 2;
    const int token1 = token0 + 1;

    // Model the production 8 KiB double K/V page buffer plus its 256 B
    // metadata tail.  The z-tree overlays accumulator state on the K/V half
    // after the page loop, exactly as the control does.
    __shared__ __align__(16) uint8_t s_storage[kKvBytes + kMdBytes];
    uint32_t (*s_k)[kU32PerRow] =
        reinterpret_cast<uint32_t (*)[kU32PerRow]>(s_storage);
    uint32_t (*s_v)[kU32PerRow] =
        reinterpret_cast<uint32_t (*)[kU32PerRow]>(s_storage + kKvBytes / 2);
    float* s_acc = reinterpret_cast<float*>(s_storage);
    float (*s_md)[2] = reinterpret_cast<float (*)[2]>(
        s_storage + kKvBytes);

    // Four heads times four output dimensions has the same 16-float Q/acc
    // footprint as the control's two heads times eight dimensions.
    float qv[4][4];
#pragma unroll
    for (int h = 0; h < 4; ++h) {
        const uint2 pack = *reinterpret_cast<const uint2*>(
            q + h * kHeadDim + tx * 4);
        qv[h][0] = bf16_lo(pack.x) * sm_scale;
        qv[h][1] = bf16_hi(pack.x) * sm_scale;
        qv[h][2] = bf16_lo(pack.y) * sm_scale;
        qv[h][3] = bf16_hi(pack.y) * sm_scale;
    }

    float m[4] = {
        -CUDART_INF_F, -CUDART_INF_F, -CUDART_INF_F, -CUDART_INF_F};
    float l[4] = {0.f, 0.f, 0.f, 0.f};
    float acc[4][4] = {};

    // Keep a runtime page loop: resource accounting must include current-page
    // QK, next-page K/V registers live through PV, and the shared overwrite.
    const int pages = page_count > 0 ? page_count : 1;
    {
        const uint2 k0 = *reinterpret_cast<const uint2*>(
            k_cache + token0 * kHeadDim + tx * 4);
        const uint2 k1 = *reinterpret_cast<const uint2*>(
            k_cache + token1 * kHeadDim + tx * 4);
        const uint2 v0 = *reinterpret_cast<const uint2*>(
            v_cache + token0 * kHeadDim + tx * 4);
        const uint2 v1 = *reinterpret_cast<const uint2*>(
            v_cache + token1 * kHeadDim + tx * 4);
        *reinterpret_cast<uint2*>(&s_k[token0][tx * 2]) = k0;
        *reinterpret_cast<uint2*>(&s_k[token1][tx * 2]) = k1;
        *reinterpret_cast<uint2*>(&s_v[token0][tx * 2]) = v0;
        *reinterpret_cast<uint2*>(&s_v[token1][tx * 2]) = v1;
    }

    for (int page = 0; page < pages; ++page) {
        __syncthreads();

        const uint2 kpack0 = *reinterpret_cast<const uint2*>(
            &s_k[token0][tx * 2]);
        const uint2 kpack1 = *reinterpret_cast<const uint2*>(
            &s_k[token1][tx * 2]);
        const float k0v[4] = {
            bf16_lo(kpack0.x), bf16_hi(kpack0.x),
            bf16_lo(kpack0.y), bf16_hi(kpack0.y)};
        const float k1v[4] = {
            bf16_lo(kpack1.x), bf16_hi(kpack1.x),
            bf16_lo(kpack1.y), bf16_hi(kpack1.y)};

        float score0[4];
        float score1[4];
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            float dot0 = 0.f;
            float dot1 = 0.f;
#pragma unroll
            for (int d = 0; d < 4; ++d) {
                dot0 += qv[h][d] * k0v[d];
                dot1 += qv[h][d] * k1v[d];
            }
            score0[h] = row32_sum(dot0);
            score1[h] = row32_sum(dot1);
        }

        // These eight payload words deliberately remain live while PV runs;
        // they model the case13 synchronous K+V next-page lookahead.
        uint2 next_k0 = make_uint2(0u, 0u);
        uint2 next_k1 = make_uint2(0u, 0u);
        uint2 next_v0 = make_uint2(0u, 0u);
        uint2 next_v1 = make_uint2(0u, 0u);
        const bool has_next = page + 1 < pages;
        if (has_next) {
            const int next_base = (page + 1) * kPageTokens * kHeadDim;
            next_k0 = *reinterpret_cast<const uint2*>(
                k_cache + next_base + token0 * kHeadDim + tx * 4);
            next_k1 = *reinterpret_cast<const uint2*>(
                k_cache + next_base + token1 * kHeadDim + tx * 4);
            next_v0 = *reinterpret_cast<const uint2*>(
                v_cache + next_base + token0 * kHeadDim + tx * 4);
            next_v1 = *reinterpret_cast<const uint2*>(
                v_cache + next_base + token1 * kHeadDim + tx * 4);
        }

        const uint2 vpack0 = *reinterpret_cast<const uint2*>(
            &s_v[token0][tx * 2]);
        const uint2 vpack1 = *reinterpret_cast<const uint2*>(
            &s_v[token1][tx * 2]);
        const float v0v[4] = {
            bf16_lo(vpack0.x), bf16_hi(vpack0.x),
            bf16_lo(vpack0.y), bf16_hi(vpack0.y)};
        const float v1v[4] = {
            bf16_lo(vpack1.x), bf16_hi(vpack1.x),
            bf16_lo(vpack1.y), bf16_hi(vpack1.y)};

#pragma unroll
        for (int h = 0; h < 4; ++h) {
            const float m_new = fmaxf(m[h], fmaxf(score0[h], score1[h]));
            const float alpha = l[h] > 0.f
                ? __builtin_exp2f(m[h] - m_new) : 0.f;
            const float w0 = __builtin_exp2f(score0[h] - m_new);
            const float w1 = __builtin_exp2f(score1[h] - m_new);
            l[h] = l[h] * alpha + w0 + w1;
            m[h] = m_new;
#pragma unroll
            for (int d = 0; d < 4; ++d) {
                acc[h][d] = acc[h][d] * alpha +
                    w0 * v0v[d] + w1 * v1v[d];
            }
        }

        if (has_next) {
            __syncthreads();
            *reinterpret_cast<uint2*>(&s_k[token0][tx * 2]) = next_k0;
            *reinterpret_cast<uint2*>(&s_k[token1][tx * 2]) = next_k1;
            *reinterpret_cast<uint2*>(&s_v[token0][tx * 2]) = next_v0;
            *reinterpret_cast<uint2*>(&s_v[token1][tx * 2]) = next_v1;
        }
    }

    // Model the control's live 8->4->2->1 state tree.  Four state rows per
    // z partition preserve the same 16-row/8 KiB peak shared payload.
    if (tz >= 4) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            const int row = (tz - 4) * 4 + h;
            float* dst = s_acc + row * kHeadDim + tx * 4;
#pragma unroll
            for (int d = 0; d < 4; ++d) dst[d] = acc[h][d];
            if (tx == 0) {
                s_md[row][0] = m[h];
                s_md[row][1] = l[h];
            }
        }
    }
    __syncthreads();

    if (tz < 4) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            const int peer = tz * 4 + h;
            merge_head_state(m[h], l[h], acc[h],
                             s_md[peer][0], s_md[peer][1],
                             s_acc + peer * kHeadDim + tx * 4);
        }
    }
    __syncthreads();

    if (tz == 2 || tz == 3) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            const int row = (tz - 2) * 4 + h;
            float* dst = s_acc + row * kHeadDim + tx * 4;
#pragma unroll
            for (int d = 0; d < 4; ++d) dst[d] = acc[h][d];
            if (tx == 0) {
                s_md[row][0] = m[h];
                s_md[row][1] = l[h];
            }
        }
    }
    __syncthreads();

    if (tz < 2) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            const int peer = tz * 4 + h;
            merge_head_state(m[h], l[h], acc[h],
                             s_md[peer][0], s_md[peer][1],
                             s_acc + peer * kHeadDim + tx * 4);
        }
    }
    __syncthreads();

    if (tz == 1) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            float* dst = s_acc + h * kHeadDim + tx * 4;
#pragma unroll
            for (int d = 0; d < 4; ++d) dst[d] = acc[h][d];
            if (tx == 0) {
                s_md[h][0] = m[h];
                s_md[h][1] = l[h];
            }
        }
    }
    __syncthreads();

    if (tz == 0) {
#pragma unroll
        for (int h = 0; h < 4; ++h) {
            merge_head_state(m[h], l[h], acc[h],
                             s_md[h][0], s_md[h][1],
                             s_acc + h * kHeadDim + tx * 4);
            sink[(blockIdx.x * 4 + h) * 32 + tx] =
                (acc[h][0] + acc[h][1] + acc[h][2] + acc[h][3]) /
                (l[h] > 0.f ? l[h] : 1.f) + m[h] * 0.f;
        }
    }
}

extern "C" void run_case13_head4_x32_z8_resource_probe(
    const __nv_bfloat16* q,
    const __nv_bfloat16* k_cache,
    const __nv_bfloat16* v_cache,
    float* sink)
{
    case13_head4_x32_z8_resource_probe_kernel<<<1, dim3(32, 1, 8)>>>(
        q, k_cache, v_cache, sink, 57, 1.f);
}
