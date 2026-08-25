// Compile-only backend capability matrix for the installed MACA toolchain.
// Select one PROBE_ID per translation-unit compile; do not use in production.
#include <stdint.h>
#include <cuda_runtime.h>

extern "C" __device__ unsigned int probe_ctarank()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.ctarank");
extern "C" __device__ unsigned int probe_nctarank()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.nctarank");
extern "C" __device__ unsigned int probe_ctaid_x()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.ctaid.x");
extern "C" __device__ unsigned int probe_nctaid_x()
    __asm__("llvm.nvvm.read.ptx.sreg.cluster.nctaid.x");
extern "C" __device__ void probe_fence_cluster()
    __asm__("llvm.nvvm.fence.sc.cluster");
extern "C" __device__ void probe_barrier_arrive()
    __asm__("llvm.nvvm.barrier.cluster.arrive");
extern "C" __device__ void probe_barrier_wait()
    __asm__("llvm.nvvm.barrier.cluster.wait");

// These declarations use the standard NVVM signatures.  They are included
// only to test whether MACA's backend has a real cluster-shared address path.
using cluster_shared_const_ptr = const void __attribute__((address_space(3))) *;
using cluster_shared_ptr = void __attribute__((address_space(3))) *;
extern "C" __device__ unsigned int probe_getctarank(cluster_shared_const_ptr)
    __asm__("llvm.nvvm.getctarank.shared.cluster");
extern "C" __device__ bool probe_isspacep(const void*)
    __asm__("llvm.nvvm.isspacep.shared.cluster");
extern "C" __device__ cluster_shared_ptr probe_mapa(
    unsigned int, cluster_shared_const_ptr)
    __asm__("llvm.nvvm.mapa.shared.cluster");
extern "C" __device__ unsigned int probe_dummy_shared(cluster_shared_const_ptr);

__global__ void cluster_backend_probe_variant_kernel(unsigned int* out) {
    __shared__ unsigned int shared_word;
    unsigned int value = 0;
#if PROBE_ID == 1
    value = probe_ctarank();
#elif PROBE_ID == 2
    value = probe_nctarank();
#elif PROBE_ID == 3
    value = probe_ctaid_x();
#elif PROBE_ID == 4
    value = probe_nctaid_x();
#elif PROBE_ID == 5
    probe_fence_cluster();
    value = 5;
#elif PROBE_ID == 6
    probe_barrier_arrive();
    value = 6;
#elif PROBE_ID == 7
    probe_barrier_wait();
    value = 7;
#elif PROBE_ID == 8
    value = probe_getctarank(
        reinterpret_cast<cluster_shared_const_ptr>(&shared_word));
#elif PROBE_ID == 9
    value = probe_isspacep(&shared_word) ? 1u : 0u;
#elif PROBE_ID == 10
    value = static_cast<unsigned int>(
        reinterpret_cast<uintptr_t>(probe_mapa(
            0, reinterpret_cast<cluster_shared_const_ptr>(&shared_word))));
#elif PROBE_ID == 11
    value = probe_dummy_shared(&shared_word);
#else
    shared_word = threadIdx.x;
    value = shared_word;
#endif
    out[threadIdx.x] = value;
}

extern "C" void launch_cluster_backend_probe_variant(unsigned int* out) {
    cluster_backend_probe_variant_kernel<<<1, 64>>>(out);
}
