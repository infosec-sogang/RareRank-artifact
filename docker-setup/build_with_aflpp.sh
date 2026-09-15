#!/bin/bash

mkdir -p /benchmark/bin/aflpp

export CC="/fuzzer/aflpp/afl-clang-fast"
export CFLAGS="-g -fno-omit-frame-pointer -fsanitize=address"
export CXX="/fuzzer/aflpp/afl-clang-fast++"
export CXXFLAGS="-g -fno-omit-frame-pointer -fsanitize=address"
export LDFLAGS="-fuse-ld=lld"

./build_libtiff.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_binutils.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_libpng.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_cyclonedds.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_nasm.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_exiv2.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1

./build_xpdf.sh || exit 1
cp /build_output/* /benchmark/bin/aflpp/ || exit 1
