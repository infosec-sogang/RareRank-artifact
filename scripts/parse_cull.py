#!/usr/bin/env python3
import sys, os, re, numpy

FUZZ_LOG_NAME = "fuzz.log"
STATS_LOG_NAME = os.path.join("default", "fuzzer_stats")
CULL_LOG_NAME = os.path.join("default", "cull_stats")
CYCLE_LOG_NAME = os.path.join("default", "cycle_stats")

# "cycle 2, 2767 queued, 372 favored (372 rare-edge round, 0 original round)"
CULL_LINE_RE = re.compile(
    r"cycle (\d+), (\d+) queued, (\d+) favored "
    r"\((\d+) rare-edge round, (\d+) original round\)")

# "fuzzed 3837 seeds (1948 favored, 1889 normal)", one per cycle_stats line.
CYCLE_LINE_RE = re.compile(
    r"fuzzed (\d+) seeds \((\d+) favored, (\d+) normal\)")

# The rare-edge pass only runs from cycle 2 onwards (see cull_queue()), so
# earlier cycles trivially fall back to the full-map round.
FIRST_RARE_EDGE_CYCLE = 2


# Read fuzz.log to learn the time limit and the number of iterations per
# benchmark. Kept local so this script has no dependency on utils.py.
def check_fuzzlog(outdir):
    log_path = os.path.join(outdir, FUZZ_LOG_NAME)
    f = open(log_path)
    lines = f.readlines()
    f.close()
    fuzzer = None
    timelimit = None
    iter_cnt = None
    for line in lines:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if key == "Fuzzer":
            fuzzer = val
        elif key == "Timeout":
            timelimit = int(val)
        elif key == "Iterations":
            iter_cnt = int(val)
    if fuzzer is None or timelimit is None or iter_cnt is None:
        print("[-] Malformed %s" % log_path)
        exit(1)
    return (fuzzer, timelimit, iter_cnt)


# Parse a 'fuzzer_stats' file into a dict of key -> raw string value.
def parse_stats_file(stats_path):
    stats = {}
    f = open(stats_path)
    lines = f.readlines()
    f.close()
    for line in lines:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        stats[key.strip()] = val.strip()
    return stats


# Parse a 'cull_stats' file and measure how often the rare-edge round failed
# to claim every edge on its own, i.e. how many cull_queue() calls still had
# the full-map ("original") round pick up at least one favored seed.
#
# Culls from cycles 0-1 are ignored: the rare-edge round does not run there
# (see cull_queue()), so the fallback would be counted as a guaranteed hit.
#
# Returns (calls, fallbacks) over the culls from FIRST_RARE_EDGE_CYCLE onwards.
def parse_cull_stats_file(cull_path):
    calls = 0
    fallbacks = 0
    f = open(cull_path)
    lines = f.readlines()
    f.close()
    for line in lines:
        m = CULL_LINE_RE.search(line)
        if m is None:
            continue
        cycle = int(m.group(1))
        original_round = int(m.group(5))
        if cycle < FIRST_RARE_EDGE_CYCLE:
            continue
        calls += 1
        if original_round > 0:
            fallbacks += 1
    return (calls, fallbacks)


# Parse a 'cycle_stats' file and accumulate how many seeds were fuzzed over the
# whole campaign, split into favored and normal ones. Each line reports the
# numbers of one cycle, so the campaign totals are just their sums.
#
# Returns (fuzzed, favored) over every cycle recorded in the file.
def parse_cycle_stats_file(cycle_path):
    fuzzed = 0
    favored = 0
    f = open(cycle_path)
    lines = f.readlines()
    f.close()
    for line in lines:
        m = CYCLE_LINE_RE.search(line)
        if m is None:
            continue
        fuzzed += int(m.group(1))
        favored += int(m.group(2))
    return (fuzzed, favored)


# Collect the per-iteration numbers of one benchmark, as a dict of metric name
# to a list holding one entry per usable iteration. The 'cull_stats' derived
# metrics are only present for iterations that have that log file.
def collect_bench_data(outdir, iter_cnt, bench_name):
    data = {"cull_time": [], "found": [], "favored": [], "favored_ratio": [],
            "cull_calls": [], "fallback_ratio": [],
            "fuzzed": [], "fuzzed_favored": [], "fuzzed_favored_ratio": []}
    for i in range(0, iter_cnt):
        bench_dir = os.path.join(outdir, "%s-%d" % (bench_name, i))
        stats_path = os.path.join(bench_dir, STATS_LOG_NAME)
        if not os.path.isfile(stats_path):
            print("[-] Missing %s, skipping this iteration" % stats_path)
            continue
        stats = parse_stats_file(stats_path)
        if "corpus_count" not in stats or "corpus_favored" not in stats:
            print("[-] Incomplete %s, skipping this iteration" % stats_path)
            continue
        found = int(stats["corpus_count"])
        favored = int(stats["corpus_favored"])
        data["found"].append(found)
        data["favored"].append(favored)
        data["favored_ratio"].append(100.0 * favored / found if found else 0.0)

        # Runs from a build without the cull_queue() timer still contribute
        # their corpus numbers; only the timing is left out.
        if "cull_time" in stats:
            data["cull_time"].append(float(stats["cull_time"]))

        # Runs whose build does not write 'cycle_stats' still contribute the
        # metrics above; only the per-cycle fuzzing counts are left out.
        cycle_path = os.path.join(bench_dir, CYCLE_LOG_NAME)
        if os.path.isfile(cycle_path):
            fuzzed, fuzzed_favored = parse_cycle_stats_file(cycle_path)
            if fuzzed > 0:
                data["fuzzed"].append(fuzzed)
                data["fuzzed_favored"].append(fuzzed_favored)
                data["fuzzed_favored_ratio"].append(
                    100.0 * fuzzed_favored / fuzzed)

        cull_path = os.path.join(bench_dir, CULL_LOG_NAME)
        if not os.path.isfile(cull_path):
            continue
        calls, fallbacks = parse_cull_stats_file(cull_path)
        if calls > 0:
            data["cull_calls"].append(calls)
            data["fallback_ratio"].append(100.0 * fallbacks / calls)
    return data


# Summarize one list of per-iteration numbers as (avg, std, min, max).
def summarize(data):
    avg = sum(data) / len(data)
    std = numpy.std(data)
    return (avg, std, min(data), max(data))


def format_summary(data, fmt, unit=""):
    avg, std, min_v, max_v = summarize(data)
    delta = max_v - min_v
    # The unit is baked into the pattern, so '%' has to be escaped there.
    suffix = (" " + unit.replace("%", "%%")) if unit else ""
    pattern = "%s%s (%s ~ %s, Δ = %s, σ = %s)" % \
                (fmt, suffix, fmt, fmt, fmt, fmt)
    return pattern % (avg, min_v, max_v, delta, std)


# Flag metrics that only some of the iterations could contribute to.
def partial_note(data, iters):
    if len(data) == iters:
        return ""
    return "  [over %d of %d iterations]" % (len(data), iters)


def report_bench(outdir, iter_cnt, bench_name):
    data = collect_bench_data(outdir, iter_cnt, bench_name)
    iters = len(data["found"])
    if iters == 0:
        print("[-] No usable iteration for %s" % bench_name)
        return
    print("[*] %s (averaged over %d iterations)" % (bench_name, iters))
    if len(data["cull_time"]) == 0:
        print("  cull_queue() time: n/a (no 'cull_time' in fuzzer_stats)")
    else:
        print("  cull_queue() time: %s%s" %
              (format_summary(data["cull_time"], "%.6f", "sec"),
               partial_note(data["cull_time"], iters)))
    print("  seeds found      : %s" % format_summary(data["found"], "%.1f"))
    print("  seeds favored    : %s" % format_summary(data["favored"], "%.1f"))
    print("  favored ratio    : %s" %
          format_summary(data["favored_ratio"], "%.2f", "%"))

    if len(data["fuzzed"]) == 0:
        print("  (no cycle_stats data, skipping fuzzed seed analysis)")
    else:
        print("  seeds fuzzed     : %s%s" %
              (format_summary(data["fuzzed"], "%.1f"),
               partial_note(data["fuzzed"], iters)))
        print("  fuzzed favored   : %s%s" %
              (format_summary(data["fuzzed_favored"], "%.1f"),
               partial_note(data["fuzzed_favored"], iters)))
        print("  fuzzed fav. ratio: %s%s" %
              (format_summary(data["fuzzed_favored_ratio"], "%.2f", "%"),
               partial_note(data["fuzzed_favored_ratio"], iters)))

    if len(data["cull_calls"]) == 0:
        print("  (no cull_stats data, skipping rare-edge round analysis)")
        return
    print("  cull_queue() calls: %s  [cycle %d+]%s" %
          (format_summary(data["cull_calls"], "%.1f"), FIRST_RARE_EDGE_CYCLE,
           partial_note(data["cull_calls"], iters)))
    print("  orig-round used   : %s" %
          format_summary(data["fallback_ratio"], "%.2f", "%"))


def parse_each_bench(outdir, iter_cnt):
    done_benchmarks = []
    for dirname in sorted(os.listdir(outdir)):
        if dirname == FUZZ_LOG_NAME:
            continue
        if not os.path.isdir(os.path.join(outdir, dirname)):
            continue
        bench_name = "-".join(dirname.split("-")[:-1])
        if bench_name in done_benchmarks:
            continue
        report_bench(outdir, iter_cnt, bench_name)
        print("===================================")
        done_benchmarks.append(bench_name)


def main():
    if len(sys.argv) != 2:
        print("Usage: %s <outdir path>" % sys.argv[0])
        exit(1)
    outdir = sys.argv[1]
    fuzzer, timelimit, iter_cnt = check_fuzzlog(outdir)
    print("[*] Fuzzer: %s, timeout: %d sec, iterations: %d" %
          (fuzzer, timelimit, iter_cnt))
    print("===================================")
    parse_each_bench(outdir, iter_cnt)


if __name__ == "__main__":
    main()
