#include <stdint.h>

#include <cuda_runtime.h>

// Capability-only probe for the documented synchronous cache-policy loads.
// It checks whether the C500 compiler accepts uint4 __ldcs/__ldlu and whether
// they preserve the exact 16-byte payload.  It is not an attention kernel and
// does not assert that either cache policy is profitable in production.

__global__ void c500_ldcs_probe_kernel(
    const uint4* __restrict__ input,
    uint4* __restrict__ normal_output,
    uint4* __restrict__ ldcs_output,
    uint4* __restrict__ ldlu_output,
    int count)
{
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= count) return;

    const uint4* src = input + index;
    normal_output[index] = *src;
    ldcs_output[index] = __ldcs(src);
    ldlu_output[index] = __ldlu(src);
}

extern "C" void run_c500_ldcs_probe(
    const uint32_t* input,
    uint32_t* normal_output,
    uint32_t* ldcs_output,
    uint32_t* ldlu_output,
    int count)
{
    const int threads = 64;
    const int blocks = (count + threads - 1) / threads;
    c500_ldcs_probe_kernel<<<blocks, threads>>>(
        reinterpret_cast<const uint4*>(input),
        reinterpret_cast<uint4*>(normal_output),
        reinterpret_cast<uint4*>(ldcs_output),
        reinterpret_cast<uint4*>(ldlu_output),
        count);
}
