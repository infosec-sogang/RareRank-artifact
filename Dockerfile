FROM ubuntu:22.04

RUN sed -i 's/kr.archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget gnupg lsb-release software-properties-common \
 && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/llvm.sh https://apt.llvm.org/llvm.sh \
 && chmod +x /tmp/llvm.sh \
 && /tmp/llvm.sh 18 \
 && rm -f /tmp/llvm.sh

RUN apt-get update && apt-get install -y \
    clang-12 clang-18 \
    llvm-12 llvm-12-dev llvm-12-tools \
    llvm-18 llvm-18-dev llvm-18-tools \
    libc6-dev binutils libncurses5 \
    wget apt-transport-https git unzip curl texinfo \
    build-essential libtool libtool-bin gdb cmake pkg-config \
    automake autoconf bison flex \
    python3 python3-dev python3-pip sudo vim bc libfreetype6-dev python3-pyelftools \
    ninja-build libz3-dev zlib1g-dev libacl1-dev \
    libpcap-dev libboost-all-dev libeigen3-dev swig libjpeg-dev \
    liblzma-dev gcc-multilib g++-multilib \
    gettext autopoint \
 && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/clang-12 /usr/bin/clang
RUN ln -s /usr/bin/clang++-12 /usr/bin/clang++
RUN ln -s /usr/bin/llvm-config-12 /usr/bin/llvm-config

# Start the setup of benchmark and fuzzers
RUN mkdir /workspace /fuzzer /benchmark /build_output /output /box
WORKDIR /workspace

COPY docker-setup/download_benchmark.sh ./
RUN ./download_benchmark.sh && rm -f download_benchmark.sh
COPY docker-setup/benchmark-script ./
COPY docker-setup/harness /workspace/harness

# Coverage measurement
COPY docker-setup/build_coverage.sh ./
RUN ./build_coverage.sh && rm -f build_coverage.sh

# AFL++ (uses LLVM 18 — must NOT conflict with AFL's LLVM 12)
COPY docker-setup/AFLPP /fuzzer/aflpp
COPY docker-setup/setup_aflpp.sh ./
RUN ./setup_aflpp.sh && rm -f setup_aflpp.sh
COPY docker-setup/build_with_aflpp.sh ./
RUN ./build_with_aflpp.sh && rm -f build_with_aflpp.sh

# RandSet
COPY docker-setup/RandSet/randset_aflpp ./RandSet
COPY docker-setup/patches/afl-cc.c ./RandSet/src/afl-cc.c
COPY docker-setup/setup_randset.sh ./
RUN ./setup_randset.sh && rm -f setup_randset.sh
COPY docker-setup/build_with_randset.sh ./
RUN ./build_with_randset.sh && rm -f build_with_randset.sh

# RareRank: AFL++ with improved seed queue culling mechanism (binary build unneeded)
COPY docker-setup/RareRank /fuzzer/rarerank
COPY docker-setup/setup_rarerank.sh ./
RUN ./setup_rarerank.sh && rm -f setup_rarerank.sh

# Additional scripts and files needed to run experiments.
COPY docker-setup/seed /benchmark/seed
COPY docker-setup/fuzzer-script/ /workspace/fuzzer-script
