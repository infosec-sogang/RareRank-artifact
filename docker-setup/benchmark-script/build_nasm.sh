#!/bin/bash
INSTALL_DIR="/build_output"
OUTPUT_BIN="nasm"

rm -rf "$INSTALL_DIR"/*
rm -rf ./nasm
cp -r /benchmark/src/nasm ./

cd nasm
./autogen.sh || exit 1
./configure --disable-shared || exit 1
make -j"$(nproc)" || exit 1


cp "./$OUTPUT_BIN" "$INSTALL_DIR/" || exit 1
