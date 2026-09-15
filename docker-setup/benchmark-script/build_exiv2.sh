#!/bin/bash

INSTALL_DIR="/build_output"
OUTPUT_BIN="exiv2"

rm -rf "$INSTALL_DIR"/*
rm -rf ./exiv2
cp -r /benchmark/src/exiv2 ./

cd exiv2
mkdir cmakebuild
cd cmakebuild

cmake .. \
  -DBUILD_SHARED_LIBS=OFF \
  -DEXIV2_ENABLE_BROTLI=OFF \
  -DEXIV2_ENABLE_INIH=OFF \
  -DEXIV2_BUILD_SAMPLES=OFF \
  -DEXIV2_BUILD_UNIT_TESTS=OFF \
  -DEXIV2_BUILD_FUZZ_TESTS=OFF \
  -DCMAKE_C_COMPILER="${CC:-clang-18}" \
  -DCMAKE_CXX_COMPILER="${CXX:-clang++-18}" \
  -DCMAKE_C_FLAGS="${CFLAGS}" \
  -DCMAKE_CXX_FLAGS="${CXXFLAGS}" \
  -DCMAKE_EXE_LINKER_FLAGS="${LDFLAGS}" || exit 1

cmake --build . --target exiv2 -j"$(nproc)" || exit 1

cp "./bin/$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
