// Probe the bundled CUTE cluster/DSM surface.  The guarded macro is *not*
// enabled by the installed MACA headers; this file tests the actual default
// path and, separately, whether forcing the NVIDIA SM90 PTX path is accepted.
#include <stdint.h>
#include <cuda_runtime.h>
#include <cute/arch/cluster_sm90.hpp>

__global__ void cluster_backend_probe_cute_default(unsigned int* out) {
    const dim3 a = cute::cluster_grid_dims();
    const dim3 b = cute::cluster_id_in_grid();
    const dim3 c = cute::block_id_in_cluster();
    out[threadIdx.x] = a.x ^ (b.x << 8) ^ (c.x << 16);
}

extern "C" void launch_cluster_backend_probe_cute_default(unsigned int* out) {
    cluster_backend_probe_cute_default<<<1, 64>>>(out);
}
