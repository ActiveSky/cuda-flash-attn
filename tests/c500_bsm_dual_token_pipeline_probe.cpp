#include <stdint.h>
#include <cuda_runtime.h>

// Validate the precise lifecycle needed by a two-token KV page pipeline:
// after K-current has been consumed by every lane of a physical wave, launch
// K-next into the recycled K buffer while V-current is still outstanding; then
// consume V-current and launch V-next into its recycled V buffer.  Every loop
// iteration consumes both the current and next pair before recycling again.
// This preserves the production dependency test for 1025 repeated buffer
// reuses without carrying an opaque BSM token through a loop back-edge (which
// is pathological for the current MXMACA optimizer).

typedef b128vectype BsmToken128;

__device__ __forceinline__ BsmToken128 issue_bsm_128(
    uint32_t* dst_shared, const uint32_t* src_global)
{
    return memcpy_async_pred<16, MACA_ICMP_EQ>(
        dst_shared, const_cast<uint32_t*>(src_global), 1, 1);
}

__device__ __forceinline__ void wait_bsm_128(BsmToken128 token)
{
    __builtin_mxc_barrier_and_wait4(0, token);
}

__global__ void bsm_dual_token_pipeline_probe_kernel(
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
        const int current_row = (2 * iteration) * 64 + lane;
        const int next_row = current_row + 64;
        BsmToken128 k_current = issue_bsm_128(
            s_k[lane], k_input + current_row * 4);
        BsmToken128 v_current = issue_bsm_128(
            s_v[lane], v_input + current_row * 4);

        wait_bsm_128(k_current);
        const uint4 k4 = *reinterpret_cast<const uint4*>(s_k[lane ^ 16]);

        // All current-page K consumers have retired before its buffer is
        // overwritten.  V-current deliberately remains outstanding here.
        __syncwarp();
        BsmToken128 k_next = issue_bsm_128(
            s_k[lane], k_input + next_row * 4);

        uint32_t mix = k4.x ^ k4.y;
        mix = (mix << 7) | (mix >> 25);
        mix ^= k4.z + 0x9e3779b9u;

        wait_bsm_128(v_current);
        const uint4 v4 = *reinterpret_cast<const uint4*>(s_v[lane ^ 32]);

        // V-current is now retired, while K-next may still be in flight.
        // Recycle only the disjoint V buffer for the next request.
        __syncwarp();
        BsmToken128 v_next = issue_bsm_128(
            s_v[lane], v_input + next_row * 4);

        // V-next is published while K-next can still be in flight.  Consume
        // both replacements through the same cross-lane shared rows used by
        // the current pair, then repeat with the buffers fully recycled.
        wait_bsm_128(k_next);
        const uint4 k_next4 =
            *reinterpret_cast<const uint4*>(s_k[lane ^ 16]);
        wait_bsm_128(v_next);
        const uint4 v_next4 =
            *reinterpret_cast<const uint4*>(s_v[lane ^ 32]);

        uint32_t* k_dst = k_output + current_row * 4;
        uint32_t* v_dst = v_output + current_row * 4;
        *reinterpret_cast<uint4*>(k_dst) = k4;
        *reinterpret_cast<uint4*>(v_dst) = v4;
        k_dst = k_output + next_row * 4;
        v_dst = v_output + next_row * 4;
        *reinterpret_cast<uint4*>(k_dst) = k_next4;
        *reinterpret_cast<uint4*>(v_dst) = v_next4;
        if (mix == 0xffffffffu) v_dst[0] ^= mix;
        __syncwarp();
    }
}

extern "C" void run_bsm_dual_token_pipeline_probe(
    const uint32_t* k_input,
    const uint32_t* v_input,
    uint32_t* k_output,
    uint32_t* v_output,
    int iterations)
{
    bsm_dual_token_pipeline_probe_kernel<<<1, 64>>>(
        k_input, v_input, k_output, v_output, iterations);
}
