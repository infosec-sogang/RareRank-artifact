#!/bin/bash

# Arg1 : Time limitation
# Arg2 : Target program name
# Arg3 : Command line arguments for the target program
# Arg4 : Input file name in the command line argument (if empty, it's STDIN)
# Prerequisites: './seed' contains initial seed corpus.

INPUT_OPTION=""
if [ -n "$4" ]; then
  INPUT_OPTION="-f $4"
fi

export AFL_CFG_PATH="/benchmark/bin/randset/$2.sancov_cfg"

timeout "$1" /fuzzer/randset/afl-fuzz -H -m none -i seed -o /output $INPUT_OPTION -- /benchmark/bin/randset/$2 $3 > randset.stdout

/workspace/fuzzer-script/replay_testcase.py "/benchmark/bin/cov/$2" "$3" "$4" \
  "/output/default/tc_birth.csv" "/output/coverage.txt"
