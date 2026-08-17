#include <stdint.h>

#include <cuda_runtime.h>

// This is a capability gate for the lazy page-max proposal.  Attention uses
// one physical 64-lane wave per z partition and one 16-lane row per ty.  The
// probe verifies that the documented 64-bit vote primitive can be restricted
// to that row without leaking predicates from another row or z wave.

__device__ __forceinline__ bool guard_pattern(int pattern, int tx, int ty,
                                              int tz) {
    switch (pattern) {
    case 0:
        // Only row 1 is positive in both physical waves.
        return ty == 1 && tx == 2;
    case 1:
        // Exercise a high-half mask in z=0 while z=1 stays empty.
        return tz == 0 && ty == 3 && tx == 15;
    case 2:
        return false;
    default:
        // Every row has a different source lane, covering all row masks.
        return tx == ((ty * 3 + tz * 5) & 15);
    }
}

__global__ void lazy_page_guard_runtime_probe_kernel(
    int* __restrict__ any_out,
    int* __restrict__ full_wave_any_out,
    unsigned long long* __restrict__ ballot_out,
    unsigned* __restrict__ lane_ids) {
    const int tx = threadIdx.x;
    const int ty = threadIdx.y;
    const int tz = threadIdx.z;
    const int linear_tid = (tz * 4 + ty) * 16 + tx;
    const unsigned lane = __lane_id();
    const unsigned long long row_mask = 0xffffULL << (ty * 16);
    lane_ids[linear_tid] = lane;

#pragma unroll
    for (int pattern = 0; pattern < 4; ++pattern) {
        const bool pred = guard_pattern(pattern, tx, ty, tz);
        const int any = __any_sync(row_mask, pred);
        const int full_wave_any = __any_sync(~0ULL, pred);
        const unsigned long long ballot = __ballot_sync(row_mask, pred);
        any_out[pattern * 128 + linear_tid] = any;
        full_wave_any_out[pattern * 128 + linear_tid] = full_wave_any;
        ballot_out[pattern * 128 + linear_tid] = ballot;
    }
}

// Keep an owner-score shaped value live across the vote and branch so the
// resource report is relevant to the proposed hot-path guard rather than only
// to a compile-time constant semantic test.
__global__ void __launch_bounds__(256) lazy_page_guard_codegen_probe_kernel(
    const float* __restrict__ scores,
    const float* __restrict__ references,
    float* __restrict__ output) {
    const int tx = threadIdx.x;
    const int ty = threadIdx.y;
    const int tz = threadIdx.z;
    const int linear_tid = (tz * 4 + ty) * 16 + tx;
    const unsigned long long row_mask = 0xffffULL << (ty * 16);
    const float score = scores[linear_tid];
    const float reference = references[linear_tid];
    // !(score <= reference + 8) is deliberately conservative for NaN/+Inf.
    const int guard_hit = __any_sync(row_mask, !(score <= reference + 8.f));
    output[linear_tid] = guard_hit ? score : reference;
}

extern "C" void run_lazy_page_guard_probe(
    int* any_out,
    int* full_wave_any_out,
    unsigned long long* ballot_out,
    unsigned* lane_ids,
    const float* scores,
    const float* references,
    float* output) {
    lazy_page_guard_runtime_probe_kernel<<<1, dim3(16, 4, 2)>>>(
        any_out, full_wave_any_out, ballot_out, lane_ids);
    lazy_page_guard_codegen_probe_kernel<<<1, dim3(16, 4, 4)>>>(
        scores, references, output);
}
