#!/usr/bin/env bash
# Build one XPUOJ CUDA/MACA solution as a local shared library for ctypes tests.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE=${1:-"$ROOT/solutions/cuda_maca_version.cpp"}
OUTPUT=${2:-"$ROOT/build/$(basename "${SOURCE%.*}").so"}
EXTRA_FLAGS=()
if (( $# > 2 )); then
    EXTRA_FLAGS=("${@:3}")
fi
MXCC=${MXCC:-/opt/maca/mxgpu_llvm/bin/mxcc}
MACA_PATH=${MACA_PATH:-/opt/maca}
CU_BRIDGE_PATH=${CU_BRIDGE_PATH:-/opt/maca-3.7.1/tools/cu-bridge}
ARCH=${MACA_ARCH:-xcore1000}

if [[ ! -f "$SOURCE" ]]; then
    printf 'source file does not exist: %s\n' "$SOURCE" >&2
    exit 2
fi
if [[ ! -x "$MXCC" ]]; then
    printf 'mxcc is not executable: %s\n' "$MXCC" >&2
    exit 2
fi

mkdir -p "$(dirname "$OUTPUT")"
printf 'Building %s\n' "$SOURCE"
if [[ ! -d "$CU_BRIDGE_PATH/include" ]]; then
    printf 'CUDA bridge headers are unavailable: %s/include\n' "$CU_BRIDGE_PATH" >&2
    exit 2
fi

printf 'Compiler: %s\nMACA path: %s\nCUDA bridge: %s\nTarget: %s\nOutput: %s\n' \
    "$MXCC" "$MACA_PATH" "$CU_BRIDGE_PATH" "$ARCH" "$OUTPUT"
"$MXCC" \
    -x maca \
    -std=c++17 \
    -O3 \
    -fPIC \
    -shared \
    -offload-arch="$ARCH" \
    --maca-path="$MACA_PATH" \
    -I"$CU_BRIDGE_PATH/include" \
    "${EXTRA_FLAGS[@]}" \
    "$SOURCE" \
    -o "$OUTPUT"

printf 'Built %s\n' "$OUTPUT"
