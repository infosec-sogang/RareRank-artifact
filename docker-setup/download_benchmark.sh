#!/bin/bash

mkdir /benchmark/src
cd /benchmark/src

# libtiff
wget https://download.osgeo.org/libtiff/tiff-4.2.0.tar.gz || exit 1
tar -xf tiff-4.2.0.tar.gz
rm tiff-4.2.0.tar.gz
mv tiff-4.2.0 libtiff

# binutil
wget https://ftp.gnu.org/gnu/binutils/binutils-2.37.tar.gz || exit 1
tar -xf binutils-2.37.tar.gz
rm binutils-2.37.tar.gz
mv binutils-2.37 binutils

# libpng
git clone --branch libpng17 --single-branch https://github.com/pnggroup/libpng.git || exit 1

# cyclonedds
git clone https://github.com/eclipse-cyclonedds/cyclonedds.git || exit 1
cd cyclonedds
git checkout 53cf7c
cd ..

# nasm
wget -O nasm-2.15.05.tar.xz https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.xz || exit 1
tar -xf nasm-2.15.05.tar.xz
rm nasm-2.15.05.tar.xz
mv nasm-2.15.05 nasm

# exiv2
wget https://github.com/Exiv2/exiv2/archive/refs/tags/v0.28.0.tar.gz || exit 1
tar -xf v0.28.0.tar.gz
rm v0.28.0.tar.gz
mv exiv2-0.28.0 exiv2

# xpdf(pdftotext)
wget https://dl.xpdfreader.com/old/xpdf-4.04.tar.gz || exit 1
tar -xf xpdf-4.04.tar.gz
rm xpdf-4.04.tar.gz
mv xpdf-4.04 xpdf
