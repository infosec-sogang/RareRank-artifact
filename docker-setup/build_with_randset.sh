#!/bin/bash

mkdir -p /benchmark/bin/randset
mkdir -p /output

export CC="/fuzzer/randset/afl-clang-fast"
export CFLAGS="-g -fno-omit-frame-pointer -fsanitize=address"
export CXX="/fuzzer/randset/afl-clang-fast++"
export CXXFLAGS="-g -fno-omit-frame-pointer -fsanitize=address"

export LDFLAGS="-fuse-ld=lld -no-pie"
# unset AFL_LLVM_INSTRUMENT


./build_libtiff.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/tiff_read_rgba_fuzzer || exit 1
mv sancov_cfg tiff_read_rgba_fuzzer.sancov_cfg || exit 1
cp /build_output/tiff_read_rgba_fuzzer /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_binutils.sh || exit 1

cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/objdump || exit 1
mv sancov_cfg objdump.sancov_cfg || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/readelf || exit 1
mv sancov_cfg readelf.sancov_cfg || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/strip || exit 1
mv sancov_cfg strip.sancov_cfg || exit 1

cp /build_output/objdump /benchmark/bin/randset/ || exit 1
cp /build_output/readelf /benchmark/bin/randset/ || exit 1
cp /build_output/strip /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_libpng.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/libpng_read_fuzzer || exit 1
mv sancov_cfg libpng_read_fuzzer.sancov_cfg || exit 1
cp /build_output/libpng_read_fuzzer /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_cyclonedds.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/idlc || exit 1
mv sancov_cfg idlc.sancov_cfg || exit 1
cp /build_output/idlc /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_nasm.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/nasm || exit 1
mv sancov_cfg nasm.sancov_cfg || exit 1
cp /build_output/nasm /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_exiv2.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/exiv2 || exit 1
mv sancov_cfg exiv2.sancov_cfg || exit 1
cp /build_output/exiv2 /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1

./build_xpdf.sh || exit 1
cd /benchmark/bin/randset/  || exit 1
python3 /fuzzer/randset/gen_graph.py /build_output/pdftotext || exit 1
mv sancov_cfg pdftotext.sancov_cfg || exit 1
cp /build_output/pdftotext /benchmark/bin/randset/ || exit 1
cd /workspace || exit 1
