#include <stdint.h>
#include <cuda_runtime.h>

// Validate the MXMACA BSM load token returned by
// __builtin_mxc_ldg_b128_bsm_predicator and the scope-0 (wave-scope)
// barrier_and_wait4 dependency.  Each lane waits on its own K/V token but
// reads a different lane's shared-memory row afterwards, matching the
// token-parallel case-4 producer where one 64-lane wave owns four token rows.

typedef b128vectype BsmToken128;

__device__ __forceinline__ BsmToken128 issue_bsm_128(
    uint32_t* dst_shared, const uint32_t* src_global)
{
    return memcpy_async_pred<16, MACA_ICMP_EQ>(
        dst_shared, const_cast<uint32_t*>(src_global), 1, 1);
}

__device__ __forceinline__ void wait_bsm_128_block(BsmToken128 token)
{
    __builtin_mxc_barrier_and_wait4(0, token);
}

__global__ void bsm_token_wait_probe_kernel(
    const uint32_t* __restrict__ k_input,
    const uint32_t* __restrict__ v_input,
    uint32_t* __restrict__ k_output,
    uint32_t* __restrict__ v_output,
    int iterations)
{
    __shared__ __align__(16) uint32_t s_k[64][4];
    __shared__ __align__(16) uint32_t s_v[64][4];

    const int lane = threadIdx.x;
    for (int iteration = 0; iteration < iterations; ++iteration) {
        const int input_row = iteration * 64 + lane;
        BsmToken128 k_token = issue_bsm_128(
            s_k[lane], k_input + input_row * 4);
        BsmToken128 v_token = issue_bsm_128(
            s_v[lane], v_input + input_row * 4);

        // K becomes usable first.  Reading another lane's row checks that
        // wave-scope execution is sufficient for the producer's shared K use.
        wait_bsm_128_block(k_token);
        const int k_source_lane = lane ^ 16;
        const uint4 k4 = *reinterpret_cast<const uint4*>(s_k[k_source_lane]);

        // Keep a small independent arithmetic window between the two waits so
        // V is allowed to remain in flight while K is consumed.
        uint32_t mix = k4.x ^ k4.y;
        mix = (mix << 7) | (mix >> 25);
        mix ^= k4.z + 0x9e3779b9u;

        wait_bsm_128_block(v_token);
        const int v_source_lane = lane ^ 32;
        const uint4 v4 = *reinterpret_cast<const uint4*>(s_v[v_source_lane]);

        uint32_t* k_dst = k_output + input_row * 4;
        uint32_t* v_dst = v_output + input_row * 4;
        *reinterpret_cast<uint4*>(k_dst) = k4;
        *reinterpret_cast<uint4*>(v_dst) = v4;

        // Prevent the arithmetic window from being optimized away without
        // changing the values checked by the host.
        if (mix == 0xffffffffu) v_dst[0] ^= mix;

        // The next iteration overwrites both buffers.
        __syncwarp();
    }
}

extern "C" void run_bsm_token_wait_probe(
    const uint32_t* k_input,
    const uint32_t* v_input,
    uint32_t* k_output,
    uint32_t* v_output,
    int iterations)
{
    bsm_token_wait_probe_kernel<<<1, 64>>>(
        k_input, v_input, k_output, v_output, iterations);
}
