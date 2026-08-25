#include <cuda_runtime.h>

#include <algorithm>
#include <cstddef>

// A host-runtime capability probe only.  It launches no device work and restores
// every process-global setting before returning.  The production ABI does not
// expose a caller stream, so probing stream 0 is deliberately part of the test.
extern "C" int xpuoj_persist_l2_api_probe(int* max_persisting_l2_bytes,
                                          int* max_access_policy_window_bytes,
                                          int* set_limit_status,
                                          int* set_window_status,
                                          int* reset_window_status,
                                          int* restore_limit_status) {
    if (max_persisting_l2_bytes == nullptr ||
        max_access_policy_window_bytes == nullptr ||
        set_limit_status == nullptr || set_window_status == nullptr ||
        reset_window_status == nullptr || restore_limit_status == nullptr) {
        return static_cast<int>(cudaErrorInvalidValue);
    }

    *max_persisting_l2_bytes = 0;
    *max_access_policy_window_bytes = 0;
    *set_limit_status = static_cast<int>(cudaErrorNotSupported);
    *set_window_status = static_cast<int>(cudaErrorNotSupported);
    *reset_window_status = static_cast<int>(cudaErrorNotSupported);
    *restore_limit_status = static_cast<int>(cudaErrorNotSupported);

    int device = 0;
    cudaError_t status = cudaGetDevice(&device);
    if (status != cudaSuccess) {
        return static_cast<int>(status);
    }

    status = cudaDeviceGetAttribute(
        max_persisting_l2_bytes, cudaDevAttrMaxPersistingL2CacheSize, device);
    if (status != cudaSuccess) {
        return static_cast<int>(status);
    }
    status = cudaDeviceGetAttribute(
        max_access_policy_window_bytes, cudaDevAttrMaxAccessPolicyWindowSize,
        device);
    if (status != cudaSuccess) {
        return static_cast<int>(status);
    }
    if (*max_persisting_l2_bytes <= 0 ||
        *max_access_policy_window_bytes <= 0) {
        return static_cast<int>(cudaSuccess);
    }

    size_t original_limit = 0;
    status = cudaDeviceGetLimit(&original_limit, cudaLimitPersistingL2CacheSize);
    if (status != cudaSuccess) {
        return static_cast<int>(status);
    }

    const size_t probe_bytes = static_cast<size_t>(std::min(
        *max_persisting_l2_bytes, *max_access_policy_window_bytes));
    const size_t requested_limit = std::min(probe_bytes, size_t{4096});
    *set_limit_status = static_cast<int>(cudaDeviceSetLimit(
        cudaLimitPersistingL2CacheSize, requested_limit));
    if (*set_limit_status != static_cast<int>(cudaSuccess)) {
        *restore_limit_status = static_cast<int>(cudaDeviceSetLimit(
            cudaLimitPersistingL2CacheSize, original_limit));
        return static_cast<int>(cudaSuccess);
    }

    void* allocation = nullptr;
    status = cudaMalloc(&allocation, requested_limit);
    if (status != cudaSuccess) {
        *restore_limit_status = static_cast<int>(cudaDeviceSetLimit(
            cudaLimitPersistingL2CacheSize, original_limit));
        return static_cast<int>(status);
    }

    cudaStreamAttrValue policy{};
    policy.accessPolicyWindow.base_ptr = allocation;
    policy.accessPolicyWindow.num_bytes = requested_limit;
    policy.accessPolicyWindow.hitRatio = 1.0f;
    policy.accessPolicyWindow.hitProp = cudaAccessPropertyPersisting;
    policy.accessPolicyWindow.missProp = cudaAccessPropertyStreaming;
    *set_window_status = static_cast<int>(cudaStreamSetAttribute(
        static_cast<cudaStream_t>(0), cudaStreamAttributeAccessPolicyWindow,
        &policy));

    cudaStreamAttrValue reset{};
    reset.accessPolicyWindow.num_bytes = 0;
    *reset_window_status = static_cast<int>(cudaStreamSetAttribute(
        static_cast<cudaStream_t>(0), cudaStreamAttributeAccessPolicyWindow,
        &reset));

    const cudaError_t free_status = cudaFree(allocation);
    *restore_limit_status = static_cast<int>(cudaDeviceSetLimit(
        cudaLimitPersistingL2CacheSize, original_limit));
    return static_cast<int>(free_status);
}
