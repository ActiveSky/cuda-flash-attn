#include <stdint.h>
#include <cuda_runtime.h>

// Compile-only probe for xcore1000 BF16 unpack lowering.  Both kernels map a
// packed little-endian BF16 pair to the exact FP32 bit patterns
// {low << 16, high << 16}; no floating-point conversion is involved.
using U16x2 = __NATIVE_VECTOR__(2, uint16_t);
using U32x2 = __NATIVE_VECTOR__(2, uint32_t);
using F32x2 = __NATIVE_VECTOR__(2, float);

__global__ void bf16_unpack_scalar_probe(
    const uint32_t* __restrict__ input,
    float* __restrict__ output)
{
    const uint32_t packed = input[threadIdx.x];
    const U32x2 bits = {
        packed << 16,
        packed & 0xffff0000u,
    };
    *reinterpret_cast<F32x2*>(output + 2 * threadIdx.x) =
        *reinterpret_cast<const F32x2*>(&bits);
}

__global__ void bf16_unpack_vector_widen_probe(
    const uint32_t* __restrict__ input,
    float* __restrict__ output)
{
    const uint32_t packed = input[threadIdx.x];
    const U16x2 halves = *reinterpret_cast<const U16x2*>(&packed);
    U32x2 bits = __builtin_convertvector(halves, U32x2);
    bits <<= U32x2{16u, 16u};
    *reinterpret_cast<F32x2*>(output + 2 * threadIdx.x) =
        *reinterpret_cast<const F32x2*>(&bits);
}
