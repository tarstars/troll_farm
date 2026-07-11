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


def paired_stats(pairs):
    n = len(pairs)
    deltas = [p["delta"] for p in pairs]
    mean = sum(deltas) / n
    var = sum((d - mean) ** 2 for d in deltas) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    ci = 1.96 * sd / math.sqrt(n)
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
    print("check-stats: ALL OK")


if __name__ == "__main__":
    # Task 5 replaces this
    if "--check-stats" in sys.argv:
        check_stats()
    else:
        print(__doc__)
        sys.exit(2)
