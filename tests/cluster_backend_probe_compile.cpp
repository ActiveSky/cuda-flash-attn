// Narrow capability probe only.  This file is intentionally not part of the
// production translation unit and is not a correctness/performance candidate.
// It probes whether the installed MACA/C500 compiler accepts NVIDIA-style
// cluster/DSM IR entry points and lowers them for xcore1000.
#include <stdint.h>
#include <cuda_runtime.h>

extern "C" __device__ unsigned int probe_cluster_ctarank()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.ctarank");
extern "C" __device__ unsigned int probe_cluster_nctarank()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.nctarank");
extern "C" __device__ unsigned int probe_cluster_ctaid_x()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.ctaid.x");
extern "C" __device__ unsigned int probe_cluster_nctaid_x()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.nctaid.x");
extern "C" __device__ void probe_cluster_sync()
    __asm__("llvm.nvvm.barrier.cluster.arrive");
extern "C" __device__ void probe_cluster_wait()
    __asm__("llvm.nvvm.barrier.cluster.wait");
extern "C" __device__ void probe_cluster_fence()
    __asm__("llvm.nvvm.fence.sc.cluster");

__global__ void cluster_backend_probe_kernel(unsigned int* out) {
    const unsigned int r = probe_cluster_ctarank();
    const unsigned int nr = probe_cluster_nctarank();
    const unsigned int x = probe_cluster_ctaid_x();
    const unsigned int nx = probe_cluster_nctaid_x();
    probe_cluster_fence();
    probe_cluster_sync();
    probe_cluster_wait();
    out[threadIdx.x] = r ^ (nr << 8) ^ (x << 16) ^ (nx << 24);
}

extern "C" void launch_cluster_backend_probe(unsigned int* out) {
    cluster_backend_probe_kernel<<<1, 64>>>(out);
}
