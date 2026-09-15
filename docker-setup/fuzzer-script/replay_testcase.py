#!/usr/bin/env python3

import sys, subprocess, os
from subprocess import PIPE


def run_cmd(cmd_str):
    env = os.environ.copy()
    env["PATH"] = "/usr/lib/llvm-18/bin:" + env["PATH"]
    try:
        p = subprocess.run(cmd_str, shell=True, stdout=PIPE, stderr=PIPE, env=env)
    except Exception as e:
        print(e)


def get_coverage(log_path):
    with open(log_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "TOTAL" in line:
                line_total = int(line.split()[7])
                line_missed = int(line.split()[8])
                br_total = int(line.split()[10])
                br_missed = int(line.split()[11])
                return (line_total, line_missed,br_total, br_missed)


def replay_testcase(prog, cmdline, input_name, tc_csv, output_path):
    print("[*] Calculating coverage for %s" % prog)
    with open(tc_csv, "r") as f:
        tc_lines = f.readlines()
    output_lines = []
    ind = 1
    for row in tc_lines:
        tokens = row.split('",')
        input_file = tokens[0][1:]
        found_time = int(tokens[1])
        if input_name == "":
            exec_cmdline = cmdline + " < " + input_file
        else:
            run_cmd("cp %s %s" % (input_file, input_name))
            exec_cmdline = cmdline
        cmd = "LLVM_PROFILE_FILE=\"/coverage/%d.profraw\" timeout -k 3 10 %s %s" % (ind, prog, exec_cmdline)
        print("[*] Running: %s" % cmd)
        run_cmd(cmd)
        if ind == 1:
            cmd = "llvm-profdata merge -sparse /coverage/1.profraw -o /coverage/merged.profdata"
        else:
            cmd = "llvm-profdata merge -sparse /coverage/%d.profraw /coverage/merged.profdata -o /coverage/merged.profdata" % ind
        run_cmd(cmd)
        cmd = "llvm-cov report %s -instr-profile=/coverage/merged.profdata > /coverage/llvm-cov.log" % prog
        run_cmd(cmd)
        (ln_total, ln_missed, br_total, br_missed) = get_coverage("/coverage/llvm-cov.log")
        ln_cover = ln_total - ln_missed
        br_cover = br_total - br_missed
        output_lines.append("\"%s\", %d, %d/%d, %d/%d\n" %
                (input_file, found_time, ln_cover, ln_total, br_cover, br_total))
        ind += 1
    with open(output_path, "w") as f:
        for line in output_lines:
            f.write(line)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: %s <progpath> <cmdline> <input> <TC csv> <outpath>" %
                sys.argv[0])
        sys.exit(1)
    replay_testcase(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
