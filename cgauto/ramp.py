#!/usr/bin/env python3
"""Wood-ramp analyzer for collected games (the sub-100 climb's primary metric).

Reads the parsed game summaries `data/boss5_games/<opp>/game_*.log` written by
collect_debug_games.py and prints:
  - avg wood us/opp + delta at t75/150/225/300  (compare vs the v1.20.0 baseline below)
  - per-game lines: W/L, final wood, late-quarter (t225->t300) gains us vs opp
  - aggregate: win rate, avg final wood, avg late-quarter gain us vs opp

BASELINE (v1.20.0-era, 115 real Boss-5 games, 2026-07-06):
  t75 +4.1   t150 +2.8   t225 -3.1   t300 -15.3   | wins 14% | our avg final wood 38.7
  late-quarter gain: us +10..16, boss +20..30 (~2x). See docs/ROADMAP.md.

Usage: ramp.py [dir] [--last N]
  dir defaults to data/boss5_games/boss ; --last N = only the N most recent games.
"""
import glob, os, statistics, sys

CHECKPOINTS = (75, 150, 225, 300)


def load(path):
    """-> (won: bool, {t: (mywood, oppwood)}) or None if unparsable."""
    won, ramp = None, {}
    for line in open(path):
        if line.startswith("#"):
            if "scores" in line:
                won = "WIN" in line
            continue
        p = line.strip().split("\t")
        if len(p) >= 5:
            ramp[int(p[0])] = (float(p[3]), float(p[4]))
    return (won, ramp) if ramp else None


def near(ramp, t):
    return ramp.get(t) or ramp[min(ramp, key=lambda k: abs(k - t))]


def main():
    args = [a for a in sys.argv[1:]]
    last = None
    if "--last" in args:
        i = args.index("--last")
        last = int(args[i + 1]); del args[i:i + 2]
    d = args[0] if args else "data/boss5_games/boss"
    files = sorted(glob.glob(os.path.join(d, "game_*.log")), key=os.path.getmtime)
    if last:
        files = files[-last:]
    games = [(f, g) for f in files if (g := load(f))]
    if not games:
        print(f"no parsable game_*.log in {d}"); return
    print(f"{len(games)} games from {d}" + (f" (last {last})" if last else ""))
    for t in CHECKPOINTS:
        us = [near(g[1], t)[0] for _, g in games]
        op = [near(g[1], t)[1] for _, g in games]
        print(f"  t{t:<3}: us {statistics.mean(us):5.1f}  opp {statistics.mean(op):5.1f}  "
              f"delta {statistics.mean(us) - statistics.mean(op):+5.1f}")
    wins = sum(1 for _, g in games if g[0])
    finals = [near(g[1], 300) for _, g in games]
    lus, lop = [], []
    print("  --- per game (late quarter t225->t300) ---")
    for f, (won, ramp) in games:
        a, b = near(ramp, 225), near(ramp, 300)
        gu, go = b[0] - a[0], b[1] - a[1]
        lus.append(gu); lop.append(go)
        print(f"  {os.path.basename(f):26} {'W' if won else 'L'}  final {b[0]:5.1f}-{b[1]:5.1f}  "
              f"late us {gu:+5.1f} opp {go:+5.1f}")
    print(f"AGGREGATE: wins {wins}/{len(games)} ({100 * wins / len(games):.0f}%)  "
          f"our avg final wood {statistics.mean(x[0] for x in finals):.1f}  "
          f"late gain us {statistics.mean(lus):+.1f} vs opp {statistics.mean(lop):+.1f}")
    print("baseline: wins 14% | final wood 38.7 | t300 delta -15.3 | late us ~+12 opp ~+23")


if __name__ == "__main__":
    main()
