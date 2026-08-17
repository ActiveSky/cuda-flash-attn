#include <stdint.h>
#include <cuda_runtime.h>

// Capability probe: determine whether xcore1000 mov_shfl can move two FP32
// row values with one builtin invocation.  The production native-row QK path
// currently issues one 32-bit shuffle network per query head.

#if defined(PROBE_U64)
using probe_word = unsigned long long;
#elif defined(PROBE_U2)
using probe_word = uint2;
#else
using probe_word = unsigned int;
#endif

template <int MODE>
__device__ __forceinline__ probe_word probe_mov(probe_word value) {
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    return __builtin_mxc_mov_shfl(value, MODE, 0xf, 0xf, false);
#else
    return value;
#endif
}

__global__ void pair_shfl_codegen_probe_kernel(
    const probe_word* __restrict__ input,
    probe_word* __restrict__ output) {
    probe_word value = input[threadIdx.x];
    value = probe_mov<0x128>(value);
    value = probe_mov<0x124>(value);
    value = probe_mov<0x04e>(value);
    value = probe_mov<0x0b1>(value);
    output[threadIdx.x] = value;
}

extern "C" void run_pair_shfl_codegen_probe(
    const probe_word* input, probe_word* output) {
    pair_shfl_codegen_probe_kernel<<<1, 64>>>(input, output);
}
