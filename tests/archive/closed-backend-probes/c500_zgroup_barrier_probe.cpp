#include <stdint.h>
#include <cuda_runtime.h>
// The 3.7.1 primitives wrapper redundantly redefines the functions already
// emitted by its helper.  Include the helper directly to use the same public
// __mbarrier_* definitions without triggering duplicate definitions.
#include <mcr/mc_awbarrier_helpers.h>

// Probe whether two adjacent native 64-lane waves can synchronize through a
// reusable shared-memory mbarrier without forcing the other z partition in a
// 256-thread CTA to rendezvous.  This mirrors the case-14 generic-z2 ownership:
// waves 0/1 share z0 rows and waves 2/3 share z1 rows.

constexpr int kThreads = 256;

__device__ __forceinline__ void sync_two_wave_group(
    __mbarrier_t* barrier, unsigned lane)
{
    // Every lane first publishes its own shared-memory access at wave scope.
    // One leader then represents the complete wave at the two-arrival barrier;
    // the trailing wave sync keeps all lanes behind the leader's wait.
    __syncwarp();
    if (lane == 0) {
        const __mbarrier_token_t token = __mbarrier_arrive(barrier);
        while (!__mbarrier_test_wait(barrier, token)) {
        }
    }
    __syncwarp();
}

template <bool Z_GROUP>
__global__ void zgroup_barrier_probe_kernel(
    uint32_t* __restrict__ output, int iterations)
{
    __shared__ __align__(16) volatile uint32_t slots[kThreads];
    __shared__ __align__(8) __mbarrier_t barriers[2];

    const unsigned tid = threadIdx.x;
    const unsigned lane = __lane_id();
    const unsigned wave = tid >> 6;
    const unsigned z = wave >> 1;
    const unsigned peer_tid = ((wave ^ 1u) << 6) | lane;

    if constexpr (Z_GROUP) {
        if (tid == 0) __mbarrier_init(&barriers[0], 2);
        if (tid == 128) __mbarrier_init(&barriers[1], 2);
    }
    __syncthreads();

    uint32_t checksum = 0;
    for (int i = 0; i < iterations; ++i) {
        slots[tid] = static_cast<uint32_t>(i + 1) * 257u + tid;
        if constexpr (Z_GROUP) {
            sync_two_wave_group(&barriers[z], lane);
        } else {
            __syncthreads();
        }

        checksum += slots[peer_tid];

        // The second rendezvous prevents a fast wave from overwriting the next
        // iteration before its paired wave has consumed the current value.
        if constexpr (Z_GROUP) {
            sync_two_wave_group(&barriers[z], lane);
        } else {
            __syncthreads();
        }
    }
    output[blockIdx.x * kThreads + tid] = checksum;
}

extern "C" void run_zgroup_barrier_probe(
    uint32_t* output, int blocks, int iterations, int use_zgroup)
{
    if (use_zgroup) {
        zgroup_barrier_probe_kernel<true><<<blocks, kThreads>>>(
            output, iterations);
    } else {
        zgroup_barrier_probe_kernel<false><<<blocks, kThreads>>>(
            output, iterations);
    }
}
