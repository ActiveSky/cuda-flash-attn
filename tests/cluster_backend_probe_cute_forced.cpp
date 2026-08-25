// Deliberately force the bundled CUTE SM90 PTX spelling.  A successful
// front-end parse is not sufficient; this probe requires xcore1000 backend
// object generation to establish a usable lowering.
#include <stdint.h>
#include <cuda_runtime.h>
#define CUTE_ARCH_CLUSTER_SM90_ENABLED 1
#include <cute/arch/cluster_sm90.hpp>

__global__ void cluster_backend_probe_cute_forced_kernel(unsigned int* out) {
    __shared__ unsigned int smem_word;
    cute::cluster_arrive();
    cute::cluster_wait();
    const uint32_t mapped = cute::set_block_rank(
        static_cast<uint32_t>(reinterpret_cast<uintptr_t>(&smem_word)), 0);
    out[threadIdx.x] = mapped;
}

extern "C" void launch_cluster_backend_probe_cute_forced(unsigned int* out) {
    cluster_backend_probe_cute_forced_kernel<<<1, 64>>>(out);
}
