#!/bin/bash

INSTALL_DIR="/build_output"
OUTPUT_BIN="tiff_read_rgba_fuzzer"

rm -rf "$INSTALL_DIR"/*
rm -rf ./libtiff
cp -r /benchmark/src/libtiff ./

cd libtiff
WORK="$PWD/work"
./autogen.sh
./configure --disable-shared --prefix="$WORK" || exit 1
make -j"$(nproc)" || exit 1
make install || exit 1

cp /workspace/harness/libtiff/tiff_read_rgba_fuzzer.cc ./
$CXX $CXXFLAGS -DSTANDALONE -I$WORK/include \
  tiff_read_rgba_fuzzer.cc -o tiff_read_rgba_fuzzer \
  $LDFLAGS $WORK/lib/libtiffxx.a $WORK/lib/libtiff.a \
  -lm -lz -ljpeg -Wl,-Bstatic -llzma -Wl,-Bdynamic || exit 1

cp "./$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
