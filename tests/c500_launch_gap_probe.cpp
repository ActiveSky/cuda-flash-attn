// Measures the in-stream back-to-back kernel launch gap on C500.
//
// The reducer phase ablation shows a ~9 us fixed cost for the B=1 reduce phase
// that does not scale with split count or bytes.  Either the second launch
// itself costs that much, or the reducer body does.  This probe isolates the
// launch side: it runs N trivial kernels per call, so the per-kernel cost is
// (time(N=k) - time(N=1)) / (k - 1) with no memory traffic involved.

#include <stdint.h>
#include <cuda_bf16.h>

__global__ void __launch_bounds__(64) launch_gap_touch_kernel(int32_t* sink)
{
    if (blockIdx.x == 0 && threadIdx.x == 0) {
        sink[0] = sink[0] + 1;
    }
}

extern "C" void run_launch_chain(int32_t* sink, int kernels, int blocks)
{
    for (int i = 0; i < kernels; ++i) {
        launch_gap_touch_kernel<<<blocks, 64>>>(sink);
    }
}
