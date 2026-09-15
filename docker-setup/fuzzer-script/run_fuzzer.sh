#!/bin/bash

if [ $# -ne 6 ]; then
    echo "Usage: $0 <fuzzer> <timelimit> <prog> <seed> <cmdline> <input_file>"
    exit 1
fi

# Prepare a fresh environment
# rm -rf /output/*
rm -rf /box/*
cd /box

export AFL_NO_AFFINITY=1
export AFL_SKIP_CRASHES=1
export AFL_FRAMESHIFT_DISABLE=1

date "+%s%3N" > "/output/start.txt"
cp -r /benchmark/seed/$4 ./seed

/workspace/fuzzer-script/run_$1.sh $2 $3 "$5" "$6"
