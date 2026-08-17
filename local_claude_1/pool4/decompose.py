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


def perm_p_v1_SUPERSEDED(a, b, seed, k=20000):
    """WITHDRAWN METHOD — kept only as the record of what v1 did. RAISES on call.

    The unblocked permutation treats 240 games as independent; the panel is 120
    matched map pairs, so these p-values are INVALID for this design (codex_1 v2
    review). Hardened per claude_1's 2026-08-17 hazard note: a retained, uncalled
    function is one careless call away from returning, so this one refuses to run.
    Use exact_signflip_p() over paired_deltas() instead.
    """
    raise RuntimeError(
        "perm_p_v1_SUPERSEDED: unblocked permutation is INVALID for the matched "
        "120-map design — use exact_signflip_p(paired_deltas(...)) (v2)")
    obs = mean(a) - mean(b)  # unreachable, kept as the record of the method
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
    print("inference: see the map-blocked exact sign-flip tests below (v2). The v1")
    print("unblocked permutation p-values are SUPERSEDED and INVALID for this matched")
    print("design (codex_1 v2 review) and are no longer emitted; the withdrawn method")
    print("is kept as perm_p_v1_SUPERSEDED(), which raises if called.")
    print(f"corr(margin, stall) {pearson(allm, [r['stall'] for r in rows]):+.3f}   "
          f"corr(margin, osc) {pearson(allm, [r['osc'] for r in rows]):+.3f}")


# (v1's standalone entry point removed in v3: the single entry point at the
# bottom runs the descriptive table and then the v2 blocked inference, so the
# superseded numbers can never print by default.)


# --- v2 (2026-08-17, after codex_1 method review REVISION_REQUIRED) -----------
# The v1 permutation shuffled 240 games as independent, breaking the panel's
# matched 120-map structure (both seats of a map share the map effect). Primary
# inference is now the exact sign-flip test on discordant map pairs.

from itertools import product as _product


def map_pairs(rows):
    by_map = {}
    for r in rows:
        by_map.setdefault(r["map"], []).append(r)
    return {m: g for m, g in by_map.items() if len(g) == 2}


def group_of(r):
    if r["osc_n"] and r["stall_n"]:
        return "D1P4"
    if r["osc_n"]:
        return "D1"
    if r["stall_n"]:
        return "P4"
    return "clean"


def paired_deltas(rows, cond_a, cond_b):
    """margin(cond_a seat) - margin(cond_b seat) over discordant map pairs."""
    out = []
    for m, (a, b) in sorted(map_pairs(rows).items()):
        ga, gb = group_of(a), group_of(b)
        if cond_a(ga) and cond_b(gb):
            out.append(a["margin"] - b["margin"])
        elif cond_a(gb) and cond_b(ga):
            out.append(b["margin"] - a["margin"])
    return out


def exact_signflip_p(deltas):
    n = len(deltas)
    obs = sum(deltas) / n
    cnt = sum(
        1 for signs in _product((1, -1), repeat=n)
        if sum(s * d for s, d in zip(signs, deltas)) / n <= obs
    )
    return obs, cnt / 2 ** n, n


def main_v2():
    rows = load_rows()
    is_stall = lambda g: g in ("P4", "D1P4")
    no_stall = lambda g: g in ("clean", "D1")
    obs, p, n = exact_signflip_p(paired_deltas(rows, is_stall, no_stall))
    print(f"[blocked] stall vs no-stall:   n={n} pairs, delta {obs:+.2f}, exact p={p:.7f}")
    obs2, p2, n2 = exact_signflip_p(
        paired_deltas(rows, lambda g: g == "D1", lambda g: g == "clean"))
    print(f"[blocked] dance-only vs clean: n={n2} pairs, delta {obs2:+.2f}, exact p={p2:.4f}")


if __name__ == "__main__":
    main()      # descriptive table (valid) — no unblocked p-values since v3
    main_v2()   # primary inference: map-blocked exact sign-flip tests
