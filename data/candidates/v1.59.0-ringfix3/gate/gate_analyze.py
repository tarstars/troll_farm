#!/usr/bin/env python3
"""Parse gate log files (collect_debug_games.py stdout) + the .raw stderr dumps to compute:
  - win rate
  - wood avg (mine / opp), from the log's own summary line already printed
  - ring_planted at turn 20 (from @TFFARM t=20 ... ring_planted=N in the .raw file)
Usage: gate_analyze.py <label> <opponent_dir_name> <log_file> [more_log_files...]
"""
import re, sys, statistics

BOSS5 = "/home/tarstars/prj/troll_farm/data/boss5_games"

def main():
    label, opp_dir = sys.argv[1], sys.argv[2]
    log_files = sys.argv[3:]
    text = "\n".join(open(lf).read() for lf in log_files)
    games = re.findall(r"game \d+/\d+ (\d+): (\w) +wood (\d+)-(\d+)", text)
    if not games:
        print(f"{label}: NO GAMES PARSED from {log_files}")
        print(text[-2000:])
        return
    wins = sum(1 for g in games if g[1] == "W")
    mywood = [int(g[2]) for g in games]
    oppwood = [int(g[3]) for g in games]
    ring20 = []
    missing_raw = []
    for gid, *_ in games:
        try:
            raw = open(f"{BOSS5}/{opp_dir}/game_{gid}.raw").read()
        except FileNotFoundError:
            missing_raw.append(gid)
            continue
        m = re.search(r"@TFFARM t=20 .*?ring_planted=(\d+)", raw)
        if m:
            ring20.append(int(m.group(1)))
    ring_str = f"{ring20} (mean {statistics.mean(ring20):.2f})" if ring20 else f"NONE FOUND (missing_raw={missing_raw})"
    print(f"== {label} vs {opp_dir}: {wins}/{len(games)} wins | "
          f"wood {statistics.mean(mywood):.1f}-{statistics.mean(oppwood):.1f} (n={len(games)}) | "
          f"ring_planted@t20: {ring_str}")

if __name__ == "__main__":
    main()
