// Diagnostic-only wrapper for the historical paged BF16-MMA candidate.
//
// The archived source guarded its complete device body with __CUDA_ARCH__,
// but MXMACA's xcore device pass exposes __MACA_ARCH__.  Define the former
// only during the device pass so we can execute the intended historical body
// without modifying the immutable submission snapshot.
#if defined(__MACA_ARCH__) && !defined(__CUDA_ARCH__)
#define __CUDA_ARCH__ __MACA_ARCH__
#endif

#include "../../../solutions/archive/2026-08-07-submissions/cuda_104175.cpp"
