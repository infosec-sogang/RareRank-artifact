#!/bin/bash

cd /fuzzer/aflpp || exit 1

# Build AFL++ using LLVM 18 explicitly.
# LLVM 12 is reserved for original AFL (via /usr/bin/llvm-config -> llvm-config-12).
# We MUST set LLVM_CONFIG to avoid picking up the LLVM 12 symlink.
export LLVM_CONFIG=/usr/bin/llvm-config-18
make -j$(nproc) all NO_NYX=1 || exit 1
