#!/usr/bin/env python3
import sys, os
from scipy.stats import mannwhitneyu
from utils import *

COVERAGE_LOG_NAME = "coverage.txt"


def read_last_coverage(outdir, bench_name, iter_cnt):
    line_coverages = []
    branch_coverages = []
    for i in range(iter_cnt):
        bench_dir = os.path.join(outdir, "%s-%d" % (bench_name, i))
        cov_path = os.path.join(bench_dir, COVERAGE_LOG_NAME)
        with open(cov_path, 'r') as f:
            lines = f.readlines()
            tokens = lines[-1].split('",')[1].split(",")
            line = int(tokens[1].split("/")[0])
            branch = int(tokens[2].split("/")[0])
            line_coverages.append(line)
            branch_coverages.append(branch)
    return line_coverages, branch_coverages


def compute_coverage_mwu(base_outdir, target_outdir, iter_cnt, bench_name):

    base_line_coverages, base_branch_coverages = read_last_coverage(base_outdir, bench_name, iter_cnt)
    target_line_coverages, target_branch_coverages = read_last_coverage(target_outdir, bench_name, iter_cnt)

    # Perform Mann-Whitney U test 
    base_line_cov_avg = sum(base_line_coverages) / len(base_line_coverages)
    target_line_cov_avg = sum(target_line_coverages) / len(target_line_coverages)
    _, line_p_value = mannwhitneyu(base_line_coverages, target_line_coverages, alternative = 'less')

    base_branch_cov_avg = sum(base_branch_coverages) / len(base_branch_coverages)
    target_branch_cov_avg = sum(target_branch_coverages) / len(target_branch_coverages)
    _, branch_p_value = mannwhitneyu(base_branch_coverages, target_branch_coverages, alternative = 'less')

    # Calculate difference rates ((target - base) / base)
    line_cov_diff = ((target_line_cov_avg - base_line_cov_avg) / base_line_cov_avg) * 100 if base_line_cov_avg else 0
    branch_cov_diff = ((target_branch_cov_avg - base_branch_cov_avg) / base_branch_cov_avg) * 100 if base_branch_cov_avg else 0

    line_cov = (line_cov_diff, base_line_cov_avg, target_line_cov_avg, line_p_value)
    branch_cov = (branch_cov_diff, base_branch_cov_avg, target_branch_cov_avg, branch_p_value)

    return (line_cov, branch_cov)


def analyze_bench_coverage(base_outdir, target_outdir, iter_cnt):
    done_benchmarks = []
    target_benchmarks = []
    for dirname in os.listdir(target_outdir):
        if dirname == FUZZ_LOG_NAME:
            continue
        bench_name = "".join(dirname.split("-")[:-1])
        if bench_name in target_benchmarks:
            continue
        target_benchmarks.append(bench_name)

    for dirname in os.listdir(base_outdir):
        if dirname == FUZZ_LOG_NAME:
            continue
        bench_name = "".join(dirname.split("-")[:-1])
        if bench_name in done_benchmarks:
            continue

        # If the benchmark is not in the target directory, then skip it.
        if bench_name not in target_benchmarks:
            print("[*] Skip %s benchmark: Not found in %s directory" % (bench_name, target_outdir))
            done_benchmarks.append(bench_name)
            continue

        line_cov, branch_cov = compute_coverage_mwu(base_outdir, target_outdir, iter_cnt, bench_name)

        line_str = "%.1f%% (Base: %d, Target: %d), p-value: %.4f" % line_cov
        branch_str = "%.1f%% (Base: %d, Target: %d), p-value: %.4f" % branch_cov

        print("[*] Benchmark: %s (Iter count: %d)" % (bench_name, iter_cnt))
        print("Line coverage rate (avg.): %s" % line_str)
        print("Branch coverage rate (avg.): %s" % branch_str)
        print("=====================================")

        done_benchmarks.append(bench_name)


def main():
    if len(sys.argv) != 3:
        print("Usage: %s <base outdir path> <target outdir path>" % sys.argv[0])
        exit(1)
    base_outdir = sys.argv[1]
    target_outdir = sys.argv[2]

    _, _, base_iter = check_fuzzlog(base_outdir)
    _, _, target_iter = check_fuzzlog(target_outdir)

    # Match sample sizes to the minimum to prevent statistical bias.
    iter_cnt = min(base_iter, target_iter)

    analyze_bench_coverage(base_outdir, target_outdir, iter_cnt)


if __name__ == "__main__":
    main()
