#include <stdint.h>

#include <cuda_runtime.h>

// Probe the documented multistage use-def contract for the register-returning
// 128-bit global async load.  The production exp479 candidate consumed the
// returned value without the official GVM-counter wait.  This probe instead
// follows MCTLASS's sequence: issue the loads in every 64-lane physical wave,
// then arrive_gvmcnt(0) and barrier before exposing the register payload.
using AsyncI4 = __NATIVE_VECTOR__(4, int);

__device__ __forceinline__ uint4 issue_async128(const uint32_t* src)
{
    const AsyncI4 raw = __builtin_mxc_load_global_async128(
        reinterpret_cast<AsyncI4*>(const_cast<uint32_t*>(src)));
    return *reinterpret_cast<const uint4*>(&raw);
}

__global__ void async_register_gld_probe_kernel(
    const uint32_t* __restrict__ input,
    uint32_t* __restrict__ output,
    int iterations)
{
    const int lane = threadIdx.x;
    const int lanes = blockDim.x;
    for (int iteration = 0; iteration < iterations; ++iteration) {
        const int row = iteration * lanes + lane;
        const uint4 value = issue_async128(input + row * 4);

        // Official MCTLASS calls this arrive value "gvmcnt(0)".  Every
        // 64-lane physical wave reaches it uniformly, including the 256-thread
        // launch that matches the case12 z8 producer's four-wave CTA.
        __builtin_mxc_arrive(64);
        __builtin_mxc_barrier();

        *reinterpret_cast<uint4*>(output + row * 4) = value;

        // Keep the next issue after all same-wave consumers of this payload.
        __syncwarp();
    }
}

extern "C" void run_async_register_gld_probe(
    const uint32_t* input,
    uint32_t* output,
    int iterations,
    int threads)
{
    if (threads != 64 && threads != 256) return;
    async_register_gld_probe_kernel<<<1, threads>>>(input, output, iterations);
}
