import os
import time
import subprocess
from subprocess import PIPE

# Name of fuzzing log stored in the output directory
FUZZ_LOG_NAME = "fuzz.log"
start_time = time.time()


def print_log(msg):
    elapsed = int(time.time() - start_time)
    hours = elapsed // 3600
    minutes = (elapsed // 60) % 60
    secs = elapsed % 60
    print("[%02d:%02d:%02d] %s" % (hours, minutes, secs, msg))


def run_cmd(cmd_str, check=True):
    print_log("Executing command '%s'" % cmd_str)
    args = cmd_str.split()
    try:
        p = subprocess.run(args, check=check, stdout=PIPE, stderr=PIPE)
        return p.stdout
    except Exception as e:
        print_log(e)
        exit(1)


def run_cmd_in_docker(container, cmd_str, check=True):
    print_log("Executing '%s' in container %s" % (cmd_str, container))
    docker_prefix = "docker exec %s /bin/bash -c" % container
    args = docker_prefix.split() + [cmd_str]
    try:
        p = subprocess.run(args, check=check, stdout=PIPE, stderr=PIPE)
        return (p.stdout,p.stderr)
    except Exception as e:
        print_log(e)
        exit(1)


def check_cpu_count(n_required):
    n_str = run_cmd("nproc")
    try:
        if int(n_str) < n_required:
            print_log("Not enough CPU cores, please decrease MAX_INSTANCE_NUM")
            exit(1)
    except Exception as e:
        print_log(e)
        print_log("Failed to estimate the # of CPU cores with 'nproc'")
        exit(1)


def check_core_pattern():
    try:
        with open('/proc/sys/kernel/core_pattern', 'r') as f:
            pattern = f.read().strip()

        if pattern.startswith('|'):
            print_log(f"ERROR: Current core pattern is: {pattern}")
            print_log("AFL requires the core_pattern to be 'core' or a simple file pattern without pipes.")
            print_log("To fix this issue, run: echo core | sudo tee /proc/sys/kernel/core_pattern")
            exit(1)
    except Exception as e:
        print_log(f"WARNING: Error checking core pattern: {str(e)}")
        exit(1)


def convert_unit(s):
    if s.endswith("s"):
        return int(s[:-1])
    elif s.endswith("m"):
        return 60 * int(s[:-1])
    elif s.endswith("h"):
        return 3600 * int(s[:-1])
    else:
        print("Must specify 's', 'm', or'h' suffix in unit (e.g., 15s, 1m)")
        exit(1)


def check_fuzzlog(outdir):
    f = open(os.path.join(outdir, FUZZ_LOG_NAME), 'r')
    lines = f.readlines()
    fuzzer = lines[0].split()[1].strip()
    timelimit = int(lines[1].split()[1])
    iter_cnt = int(lines[2].split()[1])
    f.close()
    return fuzzer, timelimit, iter_cnt
