#include <stdint.h>

#include <cuda_runtime.h>
#include <cooperative_groups.h>

// Compile the immutable #111918 control into this probe translation unit so
// cudaOccupancyMaxActiveBlocksPerMultiprocessor sees the exact current case13
// z8 producer specialization, not a look-alike surrogate.  This does not
// modify or invoke the production run_kernel entry point.
#include "../solutions/archive/2026-08-14-submissions/cuda_111918.cpp"

namespace cg = cooperative_groups;

// Keep this ABI intentionally plain so the Python driver can inspect every
// runtime query without relying on CUDA bridge enum layout.
struct CooperativePhaseProbeInfo {
    int device;
    int cooperative_launch;
    int multiprocessors;
    int max_threads_per_multiprocessor;
    int max_blocks_per_multiprocessor;
    int max_shared_bytes_per_multiprocessor;
    int case13_active_blocks_per_multiprocessor;
    int case13_num_regs;
    int case13_shared_bytes;
    int case13_max_threads_per_block;
    int phase_active_blocks_per_multiprocessor;
    int phase_num_regs;
    int phase_shared_bytes;
    int phase_max_threads_per_block;
    int cost_baseline_active_blocks_per_multiprocessor;
    int cost_baseline_num_regs;
    int cost_baseline_shared_bytes;
    int cost_sync_active_blocks_per_multiprocessor;
    int cost_sync_num_regs;
    int cost_sync_shared_bytes;
};

// All threads must arrive at grid.sync().  Thread zero in each block writes a
// unique phase-one value; after the global barrier, thread zero validates a
// neighbor block's write.  A successful launch therefore checks both
// cooperative launch setup and cross-block phase visibility.
__global__ void __launch_bounds__(256) cooperative_phase_probe_kernel(
    int* __restrict__ phase_one,
    int* __restrict__ phase_two)
{
    const unsigned int block = blockIdx.x;
    if (threadIdx.x == 0) phase_one[block] = static_cast<int>(block) + 1;

    const cg::grid_group grid = cg::this_grid();
    grid.sync();

    if (threadIdx.x == 0) {
        const unsigned int neighbor =
            block + 1 == gridDim.x ? 0 : block + 1;
        phase_two[block] = phase_one[neighbor] ==
                static_cast<int>(neighbor) + 1
            ? 1
            : 0;
    }
}

// The two variants have identical arithmetic and cooperative-launch geometry.
// Their timed delta divided by barrier_iterations is an upper-bound estimate
// for one full-grid phase barrier at the current case13-resident 520-block
// scale.  The output store keeps the loop live in both variants.
template <bool WITH_GRID_SYNC>
__global__ void __launch_bounds__(256) cooperative_phase_cost_probe_kernel(
    uint32_t* __restrict__ sink,
    int barrier_iterations)
{
    uint32_t value = static_cast<uint32_t>(blockIdx.x) * 257u + threadIdx.x;
    const cg::grid_group grid = cg::this_grid();
    for (int iteration = 0; iteration < barrier_iterations; ++iteration) {
        value = value * 1664525u + 1013904223u;
        if constexpr (WITH_GRID_SYNC) grid.sync();
        value ^= value >> 13;
    }
    if (threadIdx.x == 0) sink[blockIdx.x] = value;
}

namespace {

inline int status_code(cudaError_t status)
{
    return static_cast<int>(status);
}

template <typename Kernel>
int query_kernel_info(
    Kernel kernel,
    int* active_blocks_per_multiprocessor,
    int* num_regs,
    int* shared_bytes,
    int* max_threads_per_block)
{
    cudaFuncAttributes attributes{};
    cudaError_t status = cudaFuncGetAttributes(&attributes, kernel);
    if (status != cudaSuccess) return status_code(status);

    *num_regs = attributes.numRegs;
    *shared_bytes = static_cast<int>(attributes.sharedSizeBytes);
    *max_threads_per_block = attributes.maxThreadsPerBlock;

    status = cudaOccupancyMaxActiveBlocksPerMultiprocessor(
        active_blocks_per_multiprocessor, kernel, 256, 0);
    if (status != cudaSuccess) return status_code(status);
    return 0;
}

}  // namespace

extern "C" int query_cooperative_phase_probe_info(
    CooperativePhaseProbeInfo* info)
{
    if (info == nullptr) return -1;
    *info = {};
    info->device = -1;

    cudaError_t status = cudaGetDevice(&info->device);
    if (status != cudaSuccess) return status_code(status);

    status = cudaDeviceGetAttribute(
        &info->cooperative_launch, cudaDevAttrCooperativeLaunch, info->device);
    if (status != cudaSuccess) return status_code(status);
    status = cudaDeviceGetAttribute(
        &info->multiprocessors, cudaDevAttrMultiProcessorCount, info->device);
    if (status != cudaSuccess) return status_code(status);
    status = cudaDeviceGetAttribute(
        &info->max_threads_per_multiprocessor,
        cudaDevAttrMaxThreadsPerMultiProcessor, info->device);
    if (status != cudaSuccess) return status_code(status);
    status = cudaDeviceGetAttribute(
        &info->max_blocks_per_multiprocessor,
        cudaDevAttrMaxBlocksPerMultiprocessor, info->device);
    if (status != cudaSuccess) return status_code(status);
    status = cudaDeviceGetAttribute(
        &info->max_shared_bytes_per_multiprocessor,
        cudaDevAttrMaxSharedMemoryPerMultiprocessor, info->device);
    if (status != cudaSuccess) return status_code(status);

    const auto case13_kernel =
        paged_decode_case13_kv8_headpair_z8_kernel<true, true>;
    int query_status = query_kernel_info(
        case13_kernel,
        &info->case13_active_blocks_per_multiprocessor,
        &info->case13_num_regs,
        &info->case13_shared_bytes,
        &info->case13_max_threads_per_block);
    if (query_status != 0) return query_status;

    const auto phase_kernel = cooperative_phase_probe_kernel;
    query_status = query_kernel_info(
        phase_kernel,
        &info->phase_active_blocks_per_multiprocessor,
        &info->phase_num_regs,
        &info->phase_shared_bytes,
        &info->phase_max_threads_per_block);
    if (query_status != 0) return query_status;

    const auto cost_baseline_kernel =
        cooperative_phase_cost_probe_kernel<false>;
    int ignored_max_threads = 0;
    query_status = query_kernel_info(
        cost_baseline_kernel,
        &info->cost_baseline_active_blocks_per_multiprocessor,
        &info->cost_baseline_num_regs,
        &info->cost_baseline_shared_bytes,
        &ignored_max_threads);
    if (query_status != 0) return query_status;
    const auto cost_sync_kernel = cooperative_phase_cost_probe_kernel<true>;
    query_status = query_kernel_info(
        cost_sync_kernel,
        &info->cost_sync_active_blocks_per_multiprocessor,
        &info->cost_sync_num_regs,
        &info->cost_sync_shared_bytes,
        &ignored_max_threads);
    if (query_status != 0) return query_status;
    return 0;
}

extern "C" int run_cooperative_phase_probe(
    int* phase_one,
    int* phase_two,
    int grid_blocks)
{
    if (phase_one == nullptr || phase_two == nullptr || grid_blocks <= 0) {
        return -1;
    }
    void* args[] = {&phase_one, &phase_two};
    const cudaError_t status = cudaLaunchCooperativeKernel(
        (void*)cooperative_phase_probe_kernel,
        dim3(static_cast<unsigned int>(grid_blocks)), dim3(256), args, 0, 0);
    return status_code(status);
}

extern "C" int run_cooperative_phase_cost_probe(
    uint32_t* sink,
    int grid_blocks,
    int barrier_iterations,
    int with_grid_sync)
{
    if (sink == nullptr || grid_blocks <= 0 || barrier_iterations <= 0) {
        return -1;
    }
    void* args[] = {&sink, &barrier_iterations};
    const void* kernel = with_grid_sync
        ? (const void*)cooperative_phase_cost_probe_kernel<true>
        : (const void*)cooperative_phase_cost_probe_kernel<false>;
    const cudaError_t status = cudaLaunchCooperativeKernel(
        kernel, dim3(static_cast<unsigned int>(grid_blocks)), dim3(256),
        args, 0, 0);
    return status_code(status);
}

// Launch the exact #111918 case13 one-wave vec2 reducer.  The driver supplies
// finite dummy partials because this is a launch-cost comparison, not a
// correctness test or a production replacement.
extern "C" int run_case13_reducer_cost_probe(
    const float* partial_m,
    const float* partial_l,
    const float* partial_acc,
    __nv_bfloat16* output,
    const int32_t* cache_seqlens)
{
    if (partial_m == nullptr || partial_l == nullptr || partial_acc == nullptr ||
        output == nullptr || cache_seqlens == nullptr) {
        return -1;
    }
    constexpr int kCase13Splits = 65;
    constexpr int kCase13PagesPerSplit = 57;
    constexpr size_t kReducerSharedBytes =
        (2 * kCase13Splits + 2) * sizeof(float);
    paged_decode_reduce_vec2_kernel<true, false, true><<<
        32, 64, kReducerSharedBytes>>>(
        partial_m, partial_l, partial_acc, output, cache_seqlens,
        1, kCase13PagesPerSplit, kCase13Splits);
    return status_code(cudaGetLastError());
}
