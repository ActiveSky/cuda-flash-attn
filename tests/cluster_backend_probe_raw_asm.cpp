// Raw PTX spelling probe.  MACA's inline-assembly parser and xcore1000
// backend must both accept this before it could be considered a backend.
#include <stdint.h>
#include <cuda_runtime.h>

__global__ void cluster_backend_probe_raw_asm_kernel(unsigned int* out) {
    asm volatile("barrier.cluster.arrive;" : : : "memory");
    asm volatile("barrier.cluster.wait;" : : : "memory");
    out[threadIdx.x] = threadIdx.x;
}

extern "C" void launch_cluster_backend_probe_raw_asm(unsigned int* out) {
    cluster_backend_probe_raw_asm_kernel<<<1, 64>>>(out);
}
