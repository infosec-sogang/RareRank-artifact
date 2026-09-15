#!/usr/bin/env python3

import sys, os, time, queue
from threading import Thread
from config import *
from utils import *

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
CWD = os.path.abspath(os.getcwd())
IMAGE_NAME = "cull-exp"
OUTDIR_ROOT = "output"
SUPPORTED_FUZZERS = ["aflpp", "randset", "rarerank"]

work_queue = queue.Queue()

def spawn_container(container, worker_id):
    option = "-dit --rm --name %s " % container
    option += "--cpuset-cpus=%d -m=%dg " % (worker_id, MEM_PER_CONTAINER)
    cmd = "docker run %s %s" % (option, IMAGE_NAME)
    run_cmd(cmd)


def run_fuzzing(container, fuzzer, timelimit, prog, seed, cmdline, input_file):
    cmd = "/workspace/fuzzer-script/run_fuzzer.sh %s %d %s %s '%s' '%s'" % \
            (fuzzer, timelimit, prog, seed, cmdline, input_file)
    run_cmd_in_docker(container, cmd, check=False)


def copy_output(container, outdir):
    cmd = "docker cp %s:/output/ %s" % (container, outdir)
    run_cmd(cmd)


def cleanup_container(container):
    cmd = "docker kill %s" % (container)
    run_cmd(cmd)


def worker(worker_id, fuzzer, timelimit, outdir_base):
    while True:
        try:
            (target, nth) = work_queue.get_nowait()
            prog, seed, cmdline, input_file = target
            container = "%s-%d" % (prog, nth)
            outdir = os.path.join(outdir_base, container)
            print_log("Worker #%d is running %s" % (worker_id, container))
            spawn_container(container, worker_id)
            run_fuzzing(container, fuzzer, timelimit, prog, seed, cmdline, input_file)
            copy_output(container, outdir)
            cleanup_container(container)
        except queue.Empty:
            break


def log(outdir_base):
    fuzzer = sys.argv[1]
    start_time = int(time.time())
    timelimit = sys.argv[2]
    iters = sys.argv[3]
    commit_hash = run_cmd("git rev-parse HEAD").strip().decode()
    with open(os.path.join(outdir_base, "fuzz.log"), 'w') as f:
        f.write("Fuzzer: %s\n" % fuzzer)
        f.write("Timeout: %s\n" % timelimit)
        f.write("Iterations: %s\n" % iters)
        f.write("Start Time: %d\n" % start_time)
        f.write("Commit Hash: %s\n" % commit_hash)


def main():
    if len(sys.argv) != 5:
        print("Usage: %s <fuzzer> <timelimit> <iters> <outdir name>"
                % sys.argv[0])
        exit(1)

    check_cpu_count(MAX_CONTAINER_NUM)
    check_core_pattern()

    fuzzer = sys.argv[1]
    timelimit = int(sys.argv[2])
    iteration = int(sys.argv[3])
    outdir_base = os.path.join(CWD, OUTDIR_ROOT, sys.argv[4])

    if fuzzer not in SUPPORTED_FUZZERS:
        print("Invalid fuzzer name provided")
        exit(1)

    if os.path.exists(outdir_base):
        print("Output directory (%s) already exists" % outdir_base)
        exit(1)
    os.makedirs(outdir_base, exist_ok=True, mode=0o777)

    log(outdir_base)

    # Initialize the work queue
    for target in TARGETS:
        for i in range(iteration):
            work_queue.put((target, i))
    threads = []
    for i in range(0, MAX_CONTAINER_NUM):
        t = Thread(target=worker, args=(i, fuzzer, timelimit, outdir_base))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print_log("All workds done!")


if __name__ == "__main__":
    main()
