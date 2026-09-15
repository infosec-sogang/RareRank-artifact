#!/bin/bash

INSTALL_DIR="/build_output"
OUTPUT_BIN="pdftotext"

rm -rf "$INSTALL_DIR"/*
rm -rf ./xpdf
cp -r /benchmark/src/xpdf ./

cd xpdf
mkdir cmakebuild
cd cmakebuild

cmake .. \
  -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_C_COMPILER="${CC:-clang-18}" \
  -DCMAKE_CXX_COMPILER="${CXX:-clang++-18}" \
  -DCMAKE_C_FLAGS="${CFLAGS}" \
  -DCMAKE_CXX_FLAGS="${CXXFLAGS}" \
  -DCMAKE_EXE_LINKER_FLAGS="${LDFLAGS}" || exit 1

cmake --build . --target "$OUTPUT_BIN" -j"$(nproc)" || exit 1

cp "./xpdf/$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
