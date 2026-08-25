// Raw DSM/multicast instruction spellings.  This deliberately uses literal
// operands so the result tests instruction recognition, not C++ address-space
// typing or a lane/parameter choice.
#include <stdint.h>
#include <cuda_runtime.h>

__global__ void cluster_backend_probe_raw_dsm_kernel(unsigned int* out) {
    asm volatile("mapa.shared::cluster.u32 r0, r1, r2;");
    asm volatile("cp.async.bulk.shared::cluster.global.mbarrier::complete_tx::bytes.multicast::cluster [0], [0], 16, [0], 1;");
    out[threadIdx.x] = threadIdx.x;
}

extern "C" void launch_cluster_backend_probe_raw_dsm(unsigned int* out) {
    cluster_backend_probe_raw_dsm_kernel<<<1, 64>>>(out);
}
