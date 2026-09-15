#!/bin/bash

INSTALL_DIR="/build_output"
OUTPUT_BIN="libpng_read_fuzzer"

rm -rf "$INSTALL_DIR"/*
rm -rf ./libpng
cp -r /benchmark/src/libpng ./

cd libpng
autoreconf -f -i
./configure --disable-shared || exit 1
make -j"$(nproc)" || exit 1

cp /workspace/harness/libpng/libpng_read_fuzzer.cc ./
$CXX $CXXFLAGS -I. \
     libpng_read_fuzzer.cc -o $OUTPUT_BIN \
     $LDFLAGS .libs/libpng17.a $LIBS -lz -lm || exit 1

cp "./$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
