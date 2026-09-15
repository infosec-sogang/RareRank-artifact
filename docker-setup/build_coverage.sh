#!/bin/bash

mkdir -p /benchmark/bin/cov

export CC=/usr/lib/llvm-18/bin/clang
export CFLAGS="-g -fprofile-instr-generate -fcoverage-mapping"
export CXX=/usr/lib/llvm-18/bin/clang++
export CXXFLAGS="-g -fprofile-instr-generate -fcoverage-mapping"
export LDFLAGS="-fprofile-instr-generate -fcoverage-mapping"
export PATH=/usr/lib/llvm-18/bin:$PATH

./build_libtiff.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_binutils.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_libpng.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_cyclonedds.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_nasm.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_exiv2.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1

./build_xpdf.sh || exit 1
cp /build_output/* /benchmark/bin/cov/ || exit 1
