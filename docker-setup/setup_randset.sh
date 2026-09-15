#!/bin/bash

cp -r /workspace/RandSet /fuzzer/randset || exit 1
cd /fuzzer/randset || exit 1

# Build AFL++ using LLVM 18 explicitly.
# LLVM 12 is reserved for original AFL (via /usr/bin/llvm-config -> llvm-config-12).
# We MUST set LLVM_CONFIG to avoid picking up the LLVM 12 symlink.

export LLVM_CONFIG=/usr/bin/llvm-config-18
export CC=/usr/bin/clang-18
export CXX=/usr/bin/clang++-18
export AR=/usr/bin/llvm-ar-18
export RANLIB=/usr/bin/llvm-ranlib-18
export NM=/usr/bin/llvm-nm-18

make -j$(nproc) all NO_NYX=1 || exit 1

