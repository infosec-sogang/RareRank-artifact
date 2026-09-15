#!/bin/bash

INSTALL_DIR="/build_output"
OUTPUT_BIN="idlc"

rm -rf "$INSTALL_DIR"/*
rm -rf ./cyclonedds
cp -r /benchmark/src/cyclonedds ./


cd cyclonedds

sed -i 's/add_library(idl SHARED/add_library(idl STATIC/' src/idl/CMakeLists.txt
printf '\nset_target_properties(idl PROPERTIES POSITION_INDEPENDENT_CODE ON)\n' >> src/idl/CMakeLists.txt

mkdir cmakebuild
cd cmakebuild

cmake .. \
  -DCMAKE_INSTALL_PREFIX="./" \
  -DCMAKE_C_COMPILER="${CC:-clang-18}" \
  -DCMAKE_CXX_COMPILER="${CXX:-clang++-18}" \
  -DCMAKE_C_FLAGS="${CFLAGS} -fno-omit-frame-pointer -O0" \
  -DCMAKE_CXX_FLAGS="${CXXFLAGS} -fno-omit-frame-pointer -O0" \
  -DCMAKE_EXE_LINKER_FLAGS="${LDFLAGS}" \
  -DCMAKE_SHARED_LINKER_FLAGS="${LDFLAGS}" \
  -DBUILD_SHARED_LIBS=OFF

cmake --build . --target idlc -j"$(nproc)" || exit 1

cp "./bin/$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
