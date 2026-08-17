#include <stdint.h>
#include <cuda_runtime.h>

// Isolated capability probe for packed two-element floating-point dot
// products with an FP32 accumulator.  Compiler builds can contain generic
// Clang builtin names even when the xcore1000 backend cannot lower them, so
// this file deliberately tests compilation and runtime without touching the
// production solution.

using f16x2 = _Float16 __attribute__((ext_vector_type(2)));
using bf16x2 = __bf16 __attribute__((ext_vector_type(2)));

#if __has_builtin(__builtin_amdgcn_fdot2_f16_f16)
#define C500_HAS_FDOT2_F16 1
#else
#define C500_HAS_FDOT2_F16 0
#endif

#if __has_builtin(__builtin_amdgcn_fdot2_bf16_bf16)
#define C500_HAS_FDOT2_BF16 1
#else
#define C500_HAS_FDOT2_BF16 0
#endif

__global__ void fdot2_capability_probe_kernel(
    const uint32_t* __restrict__ f16_words,
    const uint32_t* __restrict__ bf16_words,
    const float* __restrict__ seeds,
    float* __restrict__ f16_out,
    float* __restrict__ bf16_out,
    int32_t* __restrict__ capability)
{
    const int lane = static_cast<int>(threadIdx.x);
    if (lane == 0) {
        capability[0] = C500_HAS_FDOT2_F16;
        capability[1] = C500_HAS_FDOT2_BF16;
    }

#if C500_HAS_FDOT2_F16
    const f16x2 a_f16 = __builtin_bit_cast(f16x2, f16_words[2 * lane]);
    const f16x2 b_f16 = __builtin_bit_cast(f16x2, f16_words[2 * lane + 1]);
    f16_out[lane] = __builtin_amdgcn_fdot2_f16_f16(
        a_f16, b_f16, seeds[lane], false);
#else
    f16_out[lane] = 0.0f;
#endif

#if C500_HAS_FDOT2_BF16
    const bf16x2 a_bf16 = __builtin_bit_cast(bf16x2, bf16_words[2 * lane]);
    const bf16x2 b_bf16 = __builtin_bit_cast(bf16x2, bf16_words[2 * lane + 1]);
    bf16_out[lane] = __builtin_amdgcn_fdot2_bf16_bf16(
        a_bf16, b_bf16, seeds[lane], false);
#else
    bf16_out[lane] = 0.0f;
#endif
}

extern "C" void run_fdot2_capability_probe(
    const uint32_t* f16_words,
    const uint32_t* bf16_words,
    const float* seeds,
    float* f16_out,
    float* bf16_out,
    int32_t* capability)
{
    fdot2_capability_probe_kernel<<<1, 64>>>(
        f16_words, bf16_words, seeds, f16_out, bf16_out, capability);
}
