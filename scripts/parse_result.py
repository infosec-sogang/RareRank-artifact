#!/usr/bin/env python3
import sys, os, numpy
from utils import *

COVERAGE_LOG_NAME = "coverage.txt"


# Compute the average of code coverage at time point 't' second.
def compute_cov_at(outdir, iter_cnt, bench_name, t):
    line_data = []
    branch_data = []
    for i in range(0, iter_cnt):
        bench_dir = os.path.join(outdir, "%s-%d" % (bench_name, i))
        cov_path = os.path.join(bench_dir, COVERAGE_LOG_NAME)
        f = open(cov_path)
        lines = f.readlines()
        f.close()
        cur_line = 0
        cur_branch = 0
        for line in lines:
            tokens = line.split('",')[1].split(",")
            elapsed = int(tokens[0])
            line = int(tokens[1].split("/")[0])
            branch = int(tokens[2].split("/")[0])
            if elapsed > t:
                break
            cur_line = line
            cur_branch = branch
        line_data.append(cur_line)
        branch_data.append(cur_branch)

    line_sum = sum(line_data)
    line_avg = line_sum / iter_cnt
    line_std = numpy.std(line_data)
    line_max = max(line_data)
    line_min = min(line_data)
    branch_sum = sum(branch_data)
    branch_avg = branch_sum / iter_cnt
    branch_std = numpy.std(branch_data)
    branch_max = max(branch_data)
    branch_min = min(branch_data)
    line_cov = (line_avg, line_std, line_min, line_max)
    branch_cov = (branch_avg, branch_std, branch_min, branch_max)
    return (line_cov, branch_cov)


def plot_coverage(outdir, plot_unit, timelimit, iter_cnt, bench_name):
    for t in range(0, timelimit + 1, plot_unit):
        line_cov, branch_cov = compute_cov_at(outdir, iter_cnt, bench_name, t)
        avg, std, min_v, max_v = line_cov
        delta = max_v - min_v
        line_str = "%d (%d ~ %d, Δ = %d, σ = %d)" % \
                    (avg, min_v, max_v, delta, std)
        avg, std, min_v, max_v = branch_cov
        delta = max_v - min_v
        branch_str = "%d (%d ~ %d, Δ = %d, σ = %d)" % \
                    (avg, min_v, max_v, delta, std)
        print("%d sec: %s lines, %s branches" % (t, line_str, branch_str))


def parse_each_bench(outdir, plot_unit, timelimit, iter_cnt):
    done_benchmarks = []
    for dirname in os.listdir(outdir):
        if dirname == FUZZ_LOG_NAME:
            continue
        bench_name = "".join(dirname.split("-")[:-1])
        if bench_name in done_benchmarks:
            continue
        print("[*] Plotting avg. coverage for %s" % bench_name)
        plot_coverage(outdir, plot_unit, timelimit, iter_cnt, bench_name)
        print("===================================")
        done_benchmarks.append(bench_name)


def main():
    if len(sys.argv) != 3:
        print("Usage: %s <outdir path> <cov. plot unit>" % sys.argv[0])
        exit(1)
    outdir = sys.argv[1]
    plot_unit = convert_unit(sys.argv[2])
    _, timelimit, iter_cnt = check_fuzzlog(outdir)
    parse_each_bench(outdir, plot_unit, timelimit, iter_cnt)


if __name__ == "__main__":
    main()
