#!/usr/bin/env python3
"""Pool #4 — margin decomposition on the EXISTING 240-game matched floor.

Question (iteration charter, owner priority 2026-08-17): does game margin track
the whole-bot NO-PROGRESS STALL (P4 liveness windows: no own-inventory/cargo
progress while work remains) or the OSCILLATION itself (D-1 episodes)?

Subject: the resident's own behaviour — `claude_1/t1/t1-matched-floor.json`
(resident replayed on the 240-game c5 corpus, the same file the T-1 acceptance
panel used as its floor). No new runs; everything below is recomputed from the
committed rows. Margin = the panel's internal per-game score margin (candidate
seat vs the frozen opponent command stream) — NOT arena rating points; use it
only for within-corpus comparison.

Definitions:
  osc_turns   = sum of (turn_end - turn_start) over the game's D-1 episodes;
  stall_turns = sum of (min(window_end, live_end) - window_start) over the
                game's P4 liveness violations (live-trimmed, per the P4 rule);
  par         = mean margin over all 240 games.

Run: python3 local_claude_1/pool4/decompose.py   (from the repo root)
"""
import json
import pathlib
import random

REPO = pathlib.Path(__file__).resolve().parents[2]


def load_rows():
    d = json.load(open(REPO / "claude_1/t1/t1-matched-floor.json"))
    rows = []
    for g in d["games"]:
        osc = osc_n = stall = stall_n = 0
        for v in g["violations"]:
            if v.get("detector") == "D-1":
                for e in v["episodes"]:
                    osc += e["turn_end"] - e["turn_start"]
                    osc_n += 1
            if v["property"] == "P4":
                det = v["detail"]
                stall += min(det["window_end"], det["live_end"]) - det["window_start"]
                stall_n += 1
        rows.append(dict(map=g["map_id"], seat=g["seat"],
                         margin=g["candidate"]["margin"],
                         osc=osc, osc_n=osc_n, stall=stall, stall_n=stall_n))
    return rows


def mean(xs):
    return sum(xs) / len(xs)


def sd(xs):
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den if den else float("nan")


def perm_p(a, b, seed, k=20000):
    """One-sided permutation p for mean(a) - mean(b) being this low."""
    obs = mean(a) - mean(b)
    pool = a + b
    rng = random.Random(seed)
    cnt = 0
    for _ in range(k):
        sh = pool[:]
        rng.shuffle(sh)
        if mean(sh[:len(a)]) - mean(sh[len(a):]) <= obs:
            cnt += 1
    return obs, cnt / k


def main():
    rows = load_rows()
    allm = [r["margin"] for r in rows]
    par = mean(allm)
    print(f"games {len(rows)}  par {par:.2f}  sd {sd(allm):.1f}")
    groups = {"clean": [], "D1_only": [], "P4_only": [], "D1_and_P4": []}
    for r in rows:
        k = (("D1_and_P4" if r["stall_n"] else "D1_only") if r["osc_n"]
             else ("P4_only" if r["stall_n"] else "clean"))
        groups[k].append(r)
    for k, g in groups.items():
        ms = [r["margin"] for r in g]
        print(f"{k:<10} n={len(g):<4} margin {mean(ms):7.2f} ({mean(ms)-par:+6.2f} vs par)"
              f"  osc {mean([r['osc'] for r in g]):6.1f}  stall {mean([r['stall'] for r in g]):6.1f}")
    stall_g = [r["margin"] for r in rows if r["stall_n"]]
    nostall = [r["margin"] for r in rows if not r["stall_n"]]
    obs, p = perm_p(stall_g, nostall, seed=20260817)
    print(f"stall vs no-stall: {obs:+.2f} pts, one-sided p={p:.4f}")
    d1_nop4 = [r["margin"] for r in groups["D1_only"]]
    clean = [r["margin"] for r in groups["clean"]]
    obs2, p2 = perm_p(d1_nop4, clean, seed=20260817)
    print(f"dance-without-stall vs clean: {obs2:+.2f} pts, one-sided p={p2:.4f}")
    print(f"corr(margin, stall) {pearson(allm, [r['stall'] for r in rows]):+.3f}   "
          f"corr(margin, osc) {pearson(allm, [r['osc'] for r in rows]):+.3f}")


if __name__ == "__main__":
    main()
