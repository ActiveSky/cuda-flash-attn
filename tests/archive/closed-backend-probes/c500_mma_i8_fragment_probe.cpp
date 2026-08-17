#include <stdint.h>
#include <cuda_runtime.h>

// Validate the xcore1000 16x16x16 signed-INT8 MMA fragment mapping before any
// attention integration.  The assumed mapping mirrors the already-proven
// FP32 MMA mapping, with each lane packing four consecutive K values.
using ProbeInt4 = __NATIVE_VECTOR__(4, int32_t);

__device__ __forceinline__ int32_t pack_i8x4(
    int8_t x0, int8_t x1, int8_t x2, int8_t x3)
{
    return static_cast<int32_t>(static_cast<uint8_t>(x0)) |
        (static_cast<int32_t>(static_cast<uint8_t>(x1)) << 8) |
        (static_cast<int32_t>(static_cast<uint8_t>(x2)) << 16) |
        (static_cast<int32_t>(static_cast<uint8_t>(x3)) << 24);
}

__global__ void mma_i8_fragment_probe_kernel(
    const int8_t* __restrict__ a,
    const int8_t* __restrict__ b,
    int32_t* __restrict__ output)
{
#if defined(__MACA_ARCH__) && (__MACA_ARCH__ == 1000)
    const int lane = static_cast<int>(threadIdx.x);
    const int k_group = lane >> 4;
    const int index = lane & 15;
    const int k0 = k_group * 4;
    const int32_t a_frag = pack_i8x4(
        a[index * 16 + k0 + 0], a[index * 16 + k0 + 1],
        a[index * 16 + k0 + 2], a[index * 16 + k0 + 3]);
    const int32_t b_frag = pack_i8x4(
        b[(k0 + 0) * 16 + index], b[(k0 + 1) * 16 + index],
        b[(k0 + 2) * 16 + index], b[(k0 + 3) * 16 + index]);
    const ProbeInt4 zero = {0, 0, 0, 0};
    const ProbeInt4 result =
        __builtin_mxc_mma_16x16x16i8(a_frag, b_frag, zero);
    const int row_base = k_group * 4;
#pragma unroll
    for (int i = 0; i < 4; ++i) {
        output[(row_base + i) * 16 + index] = result[i];
    }
#else
    (void)a;
    (void)b;
    (void)output;
#endif
}

extern "C" void run_mma_i8_fragment_probe(
    const int8_t* a,
    const int8_t* b,
    int32_t* output)
{
    mma_i8_fragment_probe_kernel<<<1, 64>>>(a, b, output);
}
