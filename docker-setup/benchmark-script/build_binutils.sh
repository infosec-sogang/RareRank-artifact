#!/bin/bash

INSTALL_DIR="/build_output"

rm -rf "$INSTALL_DIR"/*
rm -rf ./binutils
cp -r /benchmark/src/binutils ./

cd binutils
CONFIG_OPTIONS="--disable-shared --disable-gdb \
                 --disable-libdecnumber --disable-readline \
                 --disable-sim --disable-ld"
./configure $CONFIG_OPTIONS || exit 1
make -j"$(nproc)" || exit 1
cp binutils/readelf "$INSTALL_DIR/readelf" || exit 1
cp binutils/objdump "$INSTALL_DIR/objdump" || exit 1
cp binutils/strip-new "$INSTALL_DIR/strip" || exit 1
