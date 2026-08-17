#include <stdint.h>
#include <cuda_runtime.h>

// Isolated xcore1000 signed INT8 dot-product capability probe.  Attention may
// only use this primitive after runtime equality and resource/codegen checks;
// this file does not change the production solution.

__global__ void sdot4_runtime_probe_kernel(
    int32_t* __restrict__ builtin_out,
    int32_t* __restrict__ scalar_out)
{
    const int lane = static_cast<int>(threadIdx.x);
    const char4 a = make_char4(
        static_cast<signed char>(lane - 32),
        static_cast<signed char>(lane + 16),
        static_cast<signed char>(-lane - 1),
        static_cast<signed char>(2 * lane - 63));
    const char4 b = make_char4(
        static_cast<signed char>(-7),
        static_cast<signed char>(11),
        static_cast<signed char>(-13),
        static_cast<signed char>(17));
    const int seed = lane * 19 - 257;
    builtin_out[lane] = __mckl_sdot4(a, b, seed, false);
    scalar_out[lane] = seed +
        static_cast<int>(a.x) * static_cast<int>(b.x) +
        static_cast<int>(a.y) * static_cast<int>(b.y) +
        static_cast<int>(a.z) * static_cast<int>(b.z) +
        static_cast<int>(a.w) * static_cast<int>(b.w);
}

__global__ void sdot4_codegen_probe_kernel(
    const char4* __restrict__ a,
    const char4* __restrict__ b,
    const int32_t* __restrict__ seed,
    int32_t* __restrict__ out)
{
    const int lane = static_cast<int>(threadIdx.x);
    out[lane] = __mckl_sdot4(a[lane], b[lane], seed[lane], false);
}

__global__ void sdot8_runtime_probe_kernel(
    int32_t* __restrict__ builtin_out,
    int32_t* __restrict__ nibble_signed_out,
    int32_t* __restrict__ byte_signed_out)
{
    const int lane = static_cast<int>(threadIdx.x);
    const uint32_t a_bits = 0x81f2073cu ^ (0x11111111u * lane);
    const uint32_t b_bits = 0xe34a9671u ^ (0x01010101u * lane);
    const int seed = lane * 23 - 311;
    builtin_out[lane] = __mckl_sdot8(
        static_cast<int>(a_bits), static_cast<int>(b_bits), seed, false);

    int nibble_sum = seed;
    int byte_sum = seed;
#pragma unroll
    for (int i = 0; i < 8; ++i) {
        const int an = static_cast<int>((a_bits >> (4 * i)) & 0xfu);
        const int bn = static_cast<int>((b_bits >> (4 * i)) & 0xfu);
        const int as = an >= 8 ? an - 16 : an;
        const int bs = bn >= 8 ? bn - 16 : bn;
        nibble_sum += as * bs;
    }
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        const int ab = static_cast<int>((a_bits >> (8 * i)) & 0xffu);
        const int bb = static_cast<int>((b_bits >> (8 * i)) & 0xffu);
        const int as = ab >= 128 ? ab - 256 : ab;
        const int bs = bb >= 128 ? bb - 256 : bb;
        byte_sum += as * bs;
    }
    nibble_signed_out[lane] = nibble_sum;
    byte_signed_out[lane] = byte_sum;
}

__global__ void cvt_pk_f32tou8_runtime_probe_kernel(
    uint32_t* __restrict__ out0,
    uint32_t* __restrict__ out1,
    uint32_t* __restrict__ out2,
    uint32_t* __restrict__ out3)
{
    const int lane = static_cast<int>(threadIdx.x);
    const float x = (static_cast<float>(lane) - 16.f) * 16.f + 0.625f;
    out0[lane] = __builtin_mxc_cvt_pk_f32tou8(x, 0u, 0x11223344u);
    out1[lane] = __builtin_mxc_cvt_pk_f32tou8(x, 1u, 0x11223344u);
    out2[lane] = __builtin_mxc_cvt_pk_f32tou8(x, 2u, 0x11223344u);
    out3[lane] = __builtin_mxc_cvt_pk_f32tou8(x, 3u, 0x11223344u);
}

__global__ void cvt_pk_f32tou8_sequence_probe_kernel(
    const float* __restrict__ values,
    uint32_t* __restrict__ packed_out,
    float* __restrict__ unpacked_out)
{
    const int lane = static_cast<int>(threadIdx.x);
    uint32_t packed = 0xa1b2c3d4u;
#pragma unroll
    for (uint32_t slot = 0; slot < 4; ++slot) {
        packed = __builtin_mxc_cvt_pk_f32tou8(
            values[4 * lane + slot], slot, packed);
    }
    packed_out[lane] = packed;
    unpacked_out[4 * lane + 0] = __builtin_mxc_b0_cast_to_f32(packed);
    unpacked_out[4 * lane + 1] = __builtin_mxc_b1_cast_to_f32(packed);
    unpacked_out[4 * lane + 2] = __builtin_mxc_b2_cast_to_f32(packed);
    unpacked_out[4 * lane + 3] = __builtin_mxc_b3_cast_to_f32(packed);
}

extern "C" void run_sdot4_runtime_probe(
    int32_t* builtin_out,
    int32_t* scalar_out)
{
    sdot4_runtime_probe_kernel<<<1, 64>>>(builtin_out, scalar_out);
}

extern "C" void run_sdot8_runtime_probe(
    int32_t* builtin_out,
    int32_t* nibble_signed_out,
    int32_t* byte_signed_out)
{
    sdot8_runtime_probe_kernel<<<1, 64>>>(
        builtin_out, nibble_signed_out, byte_signed_out);
}

extern "C" void run_cvt_pk_f32tou8_runtime_probe(
    uint32_t* out0,
    uint32_t* out1,
    uint32_t* out2,
    uint32_t* out3)
{
    cvt_pk_f32tou8_runtime_probe_kernel<<<1, 64>>>(out0, out1, out2, out3);
}

extern "C" void run_cvt_pk_f32tou8_sequence_probe(
    const float* values,
    uint32_t* packed_out,
    float* unpacked_out)
{
    cvt_pk_f32tou8_sequence_probe_kernel<<<1, 64>>>(
        values, packed_out, unpacked_out);
}
