// Probe CCCL's generated PTX cluster wrapper as shipped in the CUDA bridge.
// It is a wrapper-surface check only; no production code includes it.
#include <stdint.h>
#include <cuda_runtime.h>
#include <cuda/__ptx/instructions/barrier_cluster.h>
#include <cuda/__ptx/instructions/getctarank.h>

__global__ void cluster_backend_probe_cccl_kernel(unsigned int* out) {
    cuda::ptx::barrier_cluster_arrive();
    cuda::ptx::barrier_cluster_wait();
    const uint32_t rank = cuda::ptx::getctarank(
        cuda::ptx::space_cluster, reinterpret_cast<const void*>(out));
    out[threadIdx.x] = rank;
}

extern "C" void launch_cluster_backend_probe_cccl(unsigned int* out) {
    cluster_backend_probe_cccl_kernel<<<1, 64>>>(out);
}
