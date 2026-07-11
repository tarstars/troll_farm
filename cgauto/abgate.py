#!/usr/bin/env python3
"""Paired self-play A/B gate — REJECT filter before the arena (never an accepter).
Spec: docs/superpowers/specs/2026-07-11-selfplay-gate-design.md

usage (from repo root):
  uv run --no-sync python cgauto/abgate.py CAND_BIN CHAMP_BIN [--seeds 200]
      [--max-turns 300] [--jobs 1] [--playmatch rust/target/release/playmatch]
      [--csv PATH]
  uv run --no-sync python cgauto/abgate.py --selftest BOT_BIN   # 5 seeds, pair delta == 0
  uv run --no-sync python cgauto/abgate.py --check-stats        # pure stats self-test

Verdict: REJECT if CI95 entirely < 0 OR the candidate crashed in any game;
PASS-TO-ARENA otherwise. Champion crash => INVALID (harness problem, exit 2).
Exit codes: 0 PASS, 1 REJECT, 2 INVALID/usage.
"""
import argparse
import csv
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["seed", "turns", "score0", "score1", "fruit0", "wood0", "fruit1", "wood1", "crash0", "crash1"]


def run_playmatch(playmatch, bot0, bot1, seed, max_turns):
    out = subprocess.run(
        [playmatch, bot0, bot1, str(seed), str(max_turns)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(f"playmatch failed (seed={seed}): {out.stderr.strip()}")
    parts = out.stdout.split()
    if len(parts) != len(FIELDS):
        raise RuntimeError(f"bad playmatch line (seed={seed}): {out.stdout!r}")
    return dict(zip(FIELDS, map(int, parts)))


def pair_rows(g_a, g_b):
    """Candidate-centric per-pair numbers. Game A: candidate=bot0; game B: candidate=bot1."""
    d_a = g_a["score0"] - g_a["score1"]
    d_b = g_b["score1"] - g_b["score0"]
    return {
        "delta": (d_a + d_b) / 2.0,
        "wood_delta": ((g_a["wood0"] - g_a["wood1"]) + (g_b["wood1"] - g_b["wood0"])) / 2.0,
        "fruit_delta": ((g_a["fruit0"] - g_a["fruit1"]) + (g_b["fruit1"] - g_b["fruit0"])) / 2.0,
        "wins": int(d_a > 0) + int(d_b > 0),
        "draws": int(d_a == 0) + int(d_b == 0),
        "losses": int(d_a < 0) + int(d_b < 0),
        "cand_crash": bool(g_a["crash0"] or g_b["crash1"]),
        "champ_crash": bool(g_a["crash1"] or g_b["crash0"]),
    }


_T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
         2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
         2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def t975(df):
    """Two-sided 95% Student-t critical value (upper 97.5% quantile).
    Exact table for df<=30, first-order Cornish-Fisher beyond (error <0.2%).
    The spec requires t-based CIs: small runs (calibration timing probes, n=10)
    are where z=1.96 would be materially too narrow."""
    if df <= 0:
        raise ValueError("df must be positive")
    if df <= 30:
        return _T975[df - 1]
    return 1.96 + 2.372 / df


def paired_stats(pairs):
    if not pairs:
        raise ValueError("paired_stats: no pairs (seeds must be >= 1)")
    n = len(pairs)
    deltas = [p["delta"] for p in pairs]
    mean = sum(deltas) / n
    var = sum((d - mean) ** 2 for d in deltas) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    # n==1: zero-width CI — verdict degenerates to the sign of the single pair's delta
    ci = t975(n - 1) * sd / math.sqrt(n) if n > 1 else 0.0
    return {
        "n": n, "mean": mean, "sd": sd, "ci_lo": mean - ci, "ci_hi": mean + ci,
        "wins": sum(p["wins"] for p in pairs),
        "draws": sum(p["draws"] for p in pairs),
        "losses": sum(p["losses"] for p in pairs),
        "wood": sum(p["wood_delta"] for p in pairs) / n,
        "fruit": sum(p["fruit_delta"] for p in pairs) / n,
        "cand_crashes": sum(p["cand_crash"] for p in pairs),
        "champ_crashes": sum(p["champ_crash"] for p in pairs),
    }


def verdict(st):
    if st["champ_crashes"]:
        return "INVALID"
    if st["cand_crashes"]:
        return "REJECT"
    if st["ci_hi"] < 0:
        return "REJECT"
    return "PASS-TO-ARENA"


def check_stats():
    """Pure self-test on synthetic rows; hand-computed expectations. Exits non-zero on failure."""
    mk = lambda s0, s1, w0, w1, f0, f1, c0=0, c1=0: {
        "seed": 0, "turns": 300, "score0": s0, "score1": s1,
        "fruit0": f0, "wood0": w0, "fruit1": f1, "wood1": w1, "crash0": c0, "crash1": c1,
    }
    # pair 1: candidate wins both seatings by 8 -> delta 8
    p1 = pair_rows(mk(20, 12, 4, 2, 4, 4), mk(12, 20, 2, 4, 4, 4))
    assert p1["delta"] == 8.0 and p1["wins"] == 2 and p1["losses"] == 0, p1
    assert p1["wood_delta"] == 2.0 and p1["fruit_delta"] == 0.0, p1
    # pair 2: candidate loses both by 4 -> delta -4
    p2 = pair_rows(mk(10, 14, 1, 2, 6, 6), mk(14, 10, 2, 1, 6, 6))
    assert p2["delta"] == -4.0 and p2["losses"] == 2, p2
    # pair 3: split 6 / -6 -> delta 0, one win one loss
    p3 = pair_rows(mk(22, 16, 3, 3, 10, 4), mk(22, 16, 3, 3, 10, 4))
    assert p3["delta"] == 0.0 and p3["wins"] == 1 and p3["losses"] == 1, p3
    st = paired_stats([p1, p2, p3])
    assert st["n"] == 3 and abs(st["mean"] - (8 - 4 + 0) / 3.0) < 1e-9, st
    assert st["wins"] == 3 and st["losses"] == 3 and st["draws"] == 0, st
    assert verdict(st) == "PASS-TO-ARENA", st
    # crash semantics
    pc = pair_rows(mk(20, 12, 4, 2, 4, 4, c0=1), mk(12, 20, 2, 4, 4, 4))
    stc = paired_stats([pc])
    assert stc["cand_crashes"] == 1 and verdict(stc) == "REJECT", stc
    pch = pair_rows(mk(20, 12, 4, 2, 4, 4, c1=1), mk(12, 20, 2, 4, 4, 4))
    assert verdict(paired_stats([pch])) == "INVALID"
    # clearly-negative CI
    neg = [dict(p2, delta=p2["delta"] + i * 0.01) for i in range(30)]
    assert verdict(paired_stats(neg)) == "REJECT"
    # INVALID dominates REJECT when both sides crash in the same pair
    pboth = pair_rows(mk(20, 12, 4, 2, 4, 4, c0=1, c1=1), mk(12, 20, 2, 4, 4, 4))
    assert verdict(paired_stats([pboth])) == "INVALID"
    # game-B crash legs (crash flags on the swapped game attribute correctly)
    pb_cand = pair_rows(mk(20, 12, 4, 2, 4, 4), mk(12, 20, 2, 4, 4, 4, c1=1))
    assert pb_cand["cand_crash"] and not pb_cand["champ_crash"], pb_cand
    pb_champ = pair_rows(mk(20, 12, 4, 2, 4, 4), mk(12, 20, 2, 4, 4, 4, c0=1))
    assert pb_champ["champ_crash"] and not pb_champ["cand_crash"], pb_champ
    # draws counted (equal scores both seatings)
    pd = pair_rows(mk(16, 16, 2, 2, 8, 8), mk(16, 16, 2, 2, 8, 8))
    assert pd["draws"] == 2 and pd["delta"] == 0.0, pd
    # t-quantile sanity
    assert t975(9) == 2.262
    assert abs(t975(199) - 1.9719) < 1e-3
    # empty input rejected loudly
    try:
        paired_stats([])
        raise AssertionError("paired_stats([]) must raise")
    except ValueError:
        pass
    print("check-stats: ALL OK")


def play_pair(job):
    """Top-level for ProcessPoolExecutor picklability."""
    playmatch, cand, champ, seed, max_turns = job
    g_a = run_playmatch(playmatch, cand, champ, seed, max_turns)  # candidate = bot0
    g_b = run_playmatch(playmatch, champ, cand, seed, max_turns)  # candidate = bot1
    return seed, g_a, g_b


def csv_rows_for(seed, g_a, g_b):
    return [
        {"seed": seed, "cand_seat": 0, "turns": g_a["turns"],
         "cand_score": g_a["score0"], "champ_score": g_a["score1"],
         "cand_fruit": g_a["fruit0"], "cand_wood": g_a["wood0"],
         "champ_fruit": g_a["fruit1"], "champ_wood": g_a["wood1"],
         "cand_crash": g_a["crash0"], "champ_crash": g_a["crash1"]},
        {"seed": seed, "cand_seat": 1, "turns": g_b["turns"],
         "cand_score": g_b["score1"], "champ_score": g_b["score0"],
         "cand_fruit": g_b["fruit1"], "cand_wood": g_b["wood1"],
         "champ_fruit": g_b["fruit0"], "champ_wood": g_b["wood0"],
         "cand_crash": g_b["crash1"], "champ_crash": g_b["crash0"]},
    ]


def run_gate(cand, champ, seeds, max_turns, jobs, playmatch, csv_path):
    jobs_list = [(playmatch, cand, champ, s, max_turns) for s in range(seeds)]
    t0 = time.time()
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            results = list(ex.map(play_pair, jobs_list))
    else:
        results = [play_pair(j) for j in jobs_list]
    results.sort(key=lambda r: r[0])  # deterministic order regardless of jobs
    pairs, rows = [], []
    for seed, g_a, g_b in results:
        pairs.append(pair_rows(g_a, g_b))
        rows.extend(csv_rows_for(seed, g_a, g_b))
    st = paired_stats(pairs)
    v = verdict(st)
    if csv_path:
        d = os.path.dirname(csv_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    dt = time.time() - t0
    print(f"abgate: {st['n']} pairs ({st['n']*2} games) in {dt:.0f}s "
          f"| cand={os.path.basename(cand)} champ={os.path.basename(champ)}")
    print(f"  pair delta mean {st['mean']:+.2f}  sd {st['sd']:.2f}  "
          f"CI95 [{st['ci_lo']:+.2f}, {st['ci_hi']:+.2f}]")
    print(f"  W/D/L {st['wins']}/{st['draws']}/{st['losses']}  "
          f"wood {st['wood']:+.2f}  fruit {st['fruit']:+.2f}  "
          f"crashes cand={st['cand_crashes']} champ={st['champ_crashes']}")
    if csv_path:
        print(f"  csv: {csv_path}")
    print(f"GATE: {v}")
    return v


def selftest(bot, max_turns, playmatch):
    """Same binary both roles: the swapped game is the identical matchup with labels
    exchanged, so pair delta must be EXACTLY 0 for every seed."""
    for seed in range(5):
        _, g_a, g_b = play_pair((playmatch, bot, bot, seed, max_turns))
        p = pair_rows(g_a, g_b)
        assert p["delta"] == 0.0, (seed, p, g_a, g_b)
        print(f"  seed {seed}: pair delta 0.0 OK (scores {g_a['score0']}-{g_a['score1']})")
    print("selftest: ALL OK (pair delta exactly 0 on 5 seeds)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bots", nargs="*", help="CAND_BIN CHAMP_BIN (or BOT_BIN with --selftest)")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--max-turns", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--playmatch", default=os.path.join(REPO, "rust/target/release/playmatch"))
    ap.add_argument("--csv", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-stats", action="store_true")
    a = ap.parse_args()
    if a.check_stats:
        check_stats()
        return 0
    if a.seeds < 1:
        ap.error("--seeds must be >= 1")
    if not os.path.exists(a.playmatch):
        print(f"playmatch not found at {a.playmatch} — build it: "
              f"cd rust && cargo build --release --bin playmatch", file=sys.stderr)
        return 2
    if a.selftest:
        if len(a.bots) != 1:
            print("--selftest needs exactly one BOT_BIN (or WAIT)", file=sys.stderr)
            return 2
        selftest(a.bots[0], a.max_turns, a.playmatch)
        return 0
    if len(a.bots) != 2:
        ap.print_help()
        return 2
    cand, champ = a.bots
    csv_path = a.csv
    if csv_path is None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        csv_path = os.path.join(REPO, "data/abgate",
                                f"{ts}_{os.path.basename(cand)}_vs_{os.path.basename(champ)}.csv")
    v = run_gate(cand, champ, a.seeds, a.max_turns, a.jobs, a.playmatch, csv_path)
    return {"PASS-TO-ARENA": 0, "REJECT": 1, "INVALID": 2}[v]


if __name__ == "__main__":
    sys.exit(main())
