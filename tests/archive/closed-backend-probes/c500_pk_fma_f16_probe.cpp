#include <stdint.h>
#include <cuda_runtime.h>

using f16x2 = _Float16 __attribute__((ext_vector_type(2)));

__global__ void pk_fma_f16_probe_kernel(
    const uint32_t* __restrict__ a_words,
    const uint32_t* __restrict__ b_words,
    const uint32_t* __restrict__ c_words,
    uint32_t* __restrict__ one_step,
    uint32_t* __restrict__ four_step)
{
    const int lane = static_cast<int>(threadIdx.x);
    const f16x2 a = __builtin_bit_cast(f16x2, a_words[lane]);
    const f16x2 b = __builtin_bit_cast(f16x2, b_words[lane]);
    const f16x2 c = __builtin_bit_cast(f16x2, c_words[lane]);
    const f16x2 once = __builtin_mxc_pk_fma_f16(a, b, c);
    one_step[lane] = __builtin_bit_cast(uint32_t, once);

    f16x2 accum = c;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        accum = __builtin_mxc_pk_fma_f16(a, b, accum);
    }
    four_step[lane] = __builtin_bit_cast(uint32_t, accum);
}

extern "C" void run_pk_fma_f16_probe(
    const uint32_t* a_words,
    const uint32_t* b_words,
    const uint32_t* c_words,
    uint32_t* one_step,
    uint32_t* four_step)
{
    pk_fma_f16_probe_kernel<<<1, 64>>>(
        a_words, b_words, c_words, one_step, four_step);
}
