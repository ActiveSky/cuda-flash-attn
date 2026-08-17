#include <stdint.h>

#include <cuda_runtime.h>

// This is a capability probe, not a production implementation.  The
// swizzled destination is the ordinary k128B path from
// mcflashinfer/permuted_smem.cuh:
//
//   offset = row * stride + (chunk ^ (row % 8)), stride = 16 b128 chunks.
//
// It deliberately uses ordinary 128-bit shared loads/stores.  The separate
// LDS_TRANS 4x16 instruction is not part of the C500 target and is not tested
// here.

constexpr int kChunksPerRow = 16;  // 128 BF16 values = 16 x 128-bit chunks
constexpr int kRegions = 2;        // independent K and V shared regions
constexpr int kInputRows = 4;      // fixed host stride for both 32/64 probes
constexpr int kU32PerRow = 64;     // 256 B, matching the decode page row

template <int Rows, bool Swizzled>
__device__ __forceinline__ int physical_chunk(int row, int chunk) {
    static_assert(Rows == 2 || Rows == 4, "probe models 32 or 64 active lanes");
    if constexpr (Swizzled) {
        return chunk ^ (row & 7);
    } else {
        return chunk;
    }
}

template <int Rows, bool Swizzled>
__global__ void permuted_smem_probe_kernel(
    const uint32_t* __restrict__ input,
    uint32_t* __restrict__ output,
    uint64_t* __restrict__ producer_cycles,
    uint64_t* __restrict__ consumer_cycles,
    uint32_t* __restrict__ checksums,
    int rounds,
    int repetition) {
    // Keep two identical physical copies per independent K/V region.
    // Selecting the copy from the runtime iteration prevents LLVM from
    // hoisting a plain vector load out of the timing loop while preserving
    // the same bank phase in both copies.
    __shared__ __align__(16)
        uint32_t smem[kRegions][kInputRows][kU32PerRow * 2];

    const int lane = threadIdx.x;
    const int row = lane / kChunksPerRow;
    const int chunk = lane % kChunksPerRow;
    const int physical = physical_chunk<Rows, Swizzled>(row, chunk);
    const volatile uint32_t* input_scalar = input;

    const uint64_t start = clock64();
#pragma unroll
    for (int region = 0; region < kRegions; ++region) {
        // Keep global ingress scalar and volatile: otherwise this small probe
        // is eligible for a C500 vector-global lowering whose component layout
        // is not the ordinary host uint32 layout.  The capability under test
        // is ordinary 128-bit *shared* traffic, not that global ABI.
        const int input_offset =
            (region * kInputRows * kChunksPerRow + lane) * 4;
        const uint32_t x = input_scalar[input_offset + 0];
        const uint32_t y = input_scalar[input_offset + 1];
        const uint32_t z = input_scalar[input_offset + 2];
        const uint32_t w = input_scalar[input_offset + 3];
        const uint4 value = make_uint4(x, y, z, w);
        *reinterpret_cast<uint4*>(&smem[region][row][physical * 4]) = value;
        *reinterpret_cast<uint4*>(
            &smem[region][row][(physical + kChunksPerRow) * 4]) = value;
    }
    __syncthreads();
    const uint64_t ready = clock64();

    // This is the current KV8 consumer pattern: for each logical token row,
    // all four 16-lane subgroups read the same row while retaining their own
    // dimension chunk. The runtime-selected duplicate forces every round to
    // issue the ordinary shared transaction instead of reusing a register.
    uint32_t mix = 0x9e3779b9u + static_cast<uint32_t>(lane);
#pragma unroll 1
    for (int iteration = 0; iteration < rounds; ++iteration) {
#pragma unroll
        for (int region = 0; region < kRegions; ++region) {
#pragma unroll
            for (int logical_row = 0; logical_row < Rows; ++logical_row) {
                const int logical_physical =
                    physical_chunk<Rows, Swizzled>(logical_row, chunk);
                const int copy = (iteration & 1) * kChunksPerRow;
                const uint4 loaded =
                    *reinterpret_cast<const uint4*>(
                        &smem[region][logical_row][
                            (logical_physical + copy) * 4]);
                mix ^= loaded.x + 0x7f4a7c15u + (mix << 6) + (mix >> 2);
                mix ^= loaded.y + 0x94d049bbu + (mix << 5) + (mix >> 3);
                mix ^= loaded.z + 0x369dea0fu + (mix << 7) + (mix >> 1);
                mix ^= loaded.w + 0xbb67ae85u + (mix << 3) + (mix >> 5);
            }
        }
    }
    const uint64_t done = clock64();

    // Read the logical rows back through the same layout and expose every
    // word to the host.  Scalar global egress avoids conflating the shared
    // layout check with C500's host-facing uint4 ABI.  The output shape is
    // [lane][region][logical_row][word].
    volatile uint32_t* output_lane =
        output + lane * kRegions * Rows * 4;
#pragma unroll 1
    for (int region = 0; region < kRegions; ++region) {
#pragma unroll 1
        for (int logical_row = 0; logical_row < Rows; ++logical_row) {
            const int logical_physical =
                physical_chunk<Rows, Swizzled>(logical_row, chunk);
            const uint4 loaded = *reinterpret_cast<const uint4*>(
                &smem[region][logical_row][logical_physical * 4]);
            volatile uint32_t* destination =
                output_lane + (region * Rows + logical_row) * 4;
            destination[0] = loaded.x;
            destination[1] = loaded.y;
            destination[2] = loaded.z;
            destination[3] = loaded.w;
        }
    }

    if (lane == 0) {
        producer_cycles[repetition] = ready - start;
        consumer_cycles[repetition] = done - ready;
        checksums[repetition] = mix;
    }
}

template <int Rows>
void launch_permuted_smem_probe(
    const uint32_t* input,
    uint32_t* row_major_output,
    uint32_t* swizzled_output,
    uint64_t* row_major_producer_cycles,
    uint64_t* row_major_consumer_cycles,
    uint64_t* swizzled_producer_cycles,
    uint64_t* swizzled_consumer_cycles,
    uint32_t* row_major_checksums,
    uint32_t* swizzled_checksums,
    int rounds,
    int repetitions) {
    constexpr int threads = Rows * kChunksPerRow;
    for (int repetition = 0; repetition < repetitions; ++repetition) {
        // Alternate launch order so a persistent stream/clock-temperature
        // trend does not always favor one layout.
        if ((repetition & 1) == 0) {
            permuted_smem_probe_kernel<Rows, false><<<1, threads>>>(
                input, row_major_output, row_major_producer_cycles,
                row_major_consumer_cycles, row_major_checksums, rounds,
                repetition);
            permuted_smem_probe_kernel<Rows, true><<<1, threads>>>(
                input, swizzled_output, swizzled_producer_cycles,
                swizzled_consumer_cycles, swizzled_checksums, rounds,
                repetition);
        } else {
            permuted_smem_probe_kernel<Rows, true><<<1, threads>>>(
                input, swizzled_output, swizzled_producer_cycles,
                swizzled_consumer_cycles, swizzled_checksums, rounds,
                repetition);
            permuted_smem_probe_kernel<Rows, false><<<1, threads>>>(
                input, row_major_output, row_major_producer_cycles,
                row_major_consumer_cycles, row_major_checksums, rounds,
                repetition);
        }
    }
}

extern "C" void run_permuted_smem_probe(
    const uint32_t* input,
    uint32_t* row_major_output,
    uint32_t* swizzled_output,
    uint64_t* row_major_producer_cycles,
    uint64_t* row_major_consumer_cycles,
    uint64_t* swizzled_producer_cycles,
    uint64_t* swizzled_consumer_cycles,
    uint32_t* row_major_checksums,
    uint32_t* swizzled_checksums,
    int threads,
    int rounds,
    int repetitions) {
    if (threads == 32) {
        launch_permuted_smem_probe<2>(
            input, row_major_output, swizzled_output,
            row_major_producer_cycles, row_major_consumer_cycles,
            swizzled_producer_cycles, swizzled_consumer_cycles,
            row_major_checksums, swizzled_checksums, rounds, repetitions);
    } else if (threads == 64) {
        launch_permuted_smem_probe<4>(
            input, row_major_output, swizzled_output,
            row_major_producer_cycles, row_major_consumer_cycles,
            swizzled_producer_cycles, swizzled_consumer_cycles,
            row_major_checksums, swizzled_checksums, rounds, repetitions);
    }
}
