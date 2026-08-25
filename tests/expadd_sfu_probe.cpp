#include <stdint.h>

#include <cuda_runtime.h>
#include <common/irif.h>

// Narrow capability probe for the xcore1000 SFU-facing expaddf intrinsic.
// The output is deliberately a small matrix: column 0 is the intrinsic under
// admission, while the following columns are ordinary semantic candidates
// useful for identifying whether it is ldexp-like or exp2-like.  This probe
// does not touch the FlashAttention work file or any production dispatch.
__global__ void expadd_sfu_probe_kernel(
    const float* __restrict__ x,
    const int* __restrict__ scale,
    float* __restrict__ out,
    int count) {
  const int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= count) return;

  const float a = x[i];
  const int b = scale[i];
  float* row = out + static_cast<int64_t>(i) * 8;
 #ifdef EXPADD_SFU_EXP2_ONLY
  row[0] = __builtin_exp2f(a);
 #else
  row[0] = __llvm_mxc_expaddf(a, b);
 #endif
#if !defined(EXPADD_SFU_ONLY) && !defined(EXPADD_SFU_EXP2_ONLY)
  row[1] = ldexpf(a, b);
  row[2] = __builtin_exp2f(a);
  row[3] = __builtin_exp2f(a + static_cast<float>(b));
  row[4] = __builtin_exp2f(a) * __builtin_exp2f(static_cast<float>(b));
  row[5] = a * __builtin_exp2f(static_cast<float>(b));
  row[6] = __builtin_exp2f(a - static_cast<float>(b));
  row[7] = __builtin_exp2f(a) + static_cast<float>(b);
#endif
}

extern "C" void run_expadd_sfu_probe(
    const float* host_x,
    const int* host_scale,
    float* host_out,
    int count) {
  if (count <= 0) return;
  float* device_x = nullptr;
  int* device_scale = nullptr;
  float* device_out = nullptr;
  const size_t x_bytes = static_cast<size_t>(count) * sizeof(float);
  const size_t scale_bytes = static_cast<size_t>(count) * sizeof(int);
  const size_t out_bytes = static_cast<size_t>(count) * 8 * sizeof(float);
  cudaMalloc(reinterpret_cast<void**>(&device_x), x_bytes);
  cudaMalloc(reinterpret_cast<void**>(&device_scale), scale_bytes);
  cudaMalloc(reinterpret_cast<void**>(&device_out), out_bytes);
  cudaMemcpy(device_x, host_x, x_bytes, cudaMemcpyHostToDevice);
  cudaMemcpy(device_scale, host_scale, scale_bytes, cudaMemcpyHostToDevice);
  const int threads = 64;
  const int blocks = (count + threads - 1) / threads;
  expadd_sfu_probe_kernel<<<blocks, threads>>>(
      device_x, device_scale, device_out, count);
  cudaMemcpy(host_out, device_out, out_bytes, cudaMemcpyDeviceToHost);
  cudaFree(device_x);
  cudaFree(device_scale);
  cudaFree(device_out);
}
