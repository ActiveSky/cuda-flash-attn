#include <stdint.h>
#include <cuda_runtime.h>

__global__ void bx_cast_probe_kernel(
    const uint32_t* __restrict__ words,
    float* __restrict__ out)
{
    const int lane = static_cast<int>(threadIdx.x);
    const uint32_t word = words[lane];
    out[4 * lane + 0] = __builtin_mxc_b0_cast_to_f32(word);
    out[4 * lane + 1] = __builtin_mxc_b1_cast_to_f32(word);
    out[4 * lane + 2] = __builtin_mxc_b2_cast_to_f32(word);
    out[4 * lane + 3] = __builtin_mxc_b3_cast_to_f32(word);
}

extern "C" void run_bx_cast_probe(const uint32_t* words, float* out)
{
    bx_cast_probe_kernel<<<1, 64>>>(words, out);
}
