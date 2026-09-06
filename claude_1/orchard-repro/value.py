#!/usr/bin/env python3
"""The value run: 49 policies x 24 development map-seats, then the two exclusion
rules, the leave-one-map-out selector, the fixed-policy table and the margin curve.

Everything this file computes was registered in PREREGISTRATION-2026-09-04.md (secs 4,
5, 6) and ADDENDUM-2026-09-04-gates.md before a single value number existed.

    python3 claude_1/orchard-repro/value.py --maps 24
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness as H          # noqa: E402
import policy as P           # noqa: E402
import semantic_harness as sh  # noqa: E402


def longest_no_command_streak(cmds, uid, start_turn):
    """The longest run of consecutive turns, from `start_turn` on, in which the applied
    command line names `uid` in no fragment. This is my exclusion statistic and it is a
    STREAK, not a loss label (PREREGISTRATION sec 5)."""
    best = cur = 0
    for i in range(start_turn - 1, len(cmds)):
        if any(H.fragment_uid(f) == uid for f in H.split_fragments(cmds[i])):
            cur = 0
        else:
            cur += 1
            best = max(best, cur)
    return best


def margin_curve(ref_scores):
    return ref_scores


def play(binary, rec, draw, profile, turns, pol=None):
    ref = H.make_referee(rec, draw, profile)
    curve = []

    def post(turn, r):
        if pol is not None and hasattr(pol, "note_planted"):
            pol.note_planted(r)
        curve.append(H.own_score(r.inv) - H.own_score(r.opp_inv))

    _, cmds = H.run_arm(binary, ref, turns, pol, post)
    return ref, cmds, curve


def ci95(xs):
    n = len(xs)
    if n < 2:
        return (float("nan"), float("nan"))
    m = statistics.fmean(xs)
    sd = statistics.stdev(xs)
    h = 1.96 * sd / (n ** 0.5)
    return (m - h, m + h)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", type=int, default=24)
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="value.json")
    args = ap.parse_args()

    plan, corpus = H.sample_plan(args.maps, args.seed)
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="orchard-value-") as wd:
        binary = Path(wd) / "champion.bin"
        sh.compile_text(H.CHAMPION.read_text(), binary, crate="orchard_repro_champion")
        print("compiled; %d maps in the corpus, %d sampled (seed %d)"
              % (corpus, len(plan), args.seed))

        # ---- arm A, once per map-seat -----------------------------------
        base = []
        for rec, draw, profile in plan:
            ref, cmds, curve = play(binary, rec, draw, profile, args.turns)
            probe = P.PassThrough()
            # the planter uid and branch turn are a property of arm A, so read them
            # from a pass-through replay rather than assuming them
            r2 = H.make_referee(rec, draw, profile)
            H.run_arm(binary, r2, args.turns, probe)
            base.append({
                "map_hash": rec["map_hash"], "profile": profile,
                "own": H.own_score(ref.inv), "opp": H.own_score(ref.opp_inv),
                "margin": H.own_score(ref.inv) - H.own_score(ref.opp_inv),
                "curve": curve, "branch_turn": probe.branch_turn,
                "planter": probe.planter,
                "streak": longest_no_command_streak(cmds, probe.planter,
                                                    probe.branch_turn),
                "errors": dict(ref.error_counts),
            })
        print("arm A done: %d map-seats, mean margin %.2f  (%.0fs)"
              % (len(base), statistics.fmean(b["margin"] for b in base),
                 time.time() - t0))

        # ---- arm B, every policy on every map-seat ----------------------
        names = [p.name for p in P.grid()]
        rows = {}
        for k, name in enumerate(names):
            per = []
            for i, (rec, draw, profile) in enumerate(plan):
                pol = P.fresh(name)
                ref, cmds, curve = play(binary, rec, draw, profile, args.turns, pol)
                b = base[i]
                acct = getattr(pol, "plant_accounting", [])
                landed = sum(1 for a in acct if a["landed"])
                per.append({
                    "map_hash": rec["map_hash"], "profile": profile,
                    "own": H.own_score(ref.inv), "opp": H.own_score(ref.opp_inv),
                    "margin": H.own_score(ref.inv) - H.own_score(ref.opp_inv),
                    "d_margin": (H.own_score(ref.inv) - H.own_score(ref.opp_inv))
                                - b["margin"],
                    "d_own": H.own_score(ref.inv) - b["own"],
                    "curve": curve,
                    "streak": longest_no_command_streak(cmds, pol.planter,
                                                        pol.branch_turn),
                    "base_streak": b["streak"],
                    "plants_attempted": len(acct),
                    "plants_landed": landed,
                    "emitted": dict(getattr(pol, "emitted", {})),
                    "passed": dict(getattr(pol, "passed", {})),
                    "errors": dict(ref.error_counts),
                })
            rows[name] = per
            dm = [p["d_margin"] for p in per]
            print("  %-26s  dMargin %+8.2f  planted %3d/%3d  maxstreak %3d"
                  % (name, statistics.fmean(dm),
                     sum(p["plants_landed"] for p in per),
                     sum(p["plants_attempted"] for p in per),
                     max(p["streak"] for p in per)))

    out = {
        "what": "value run: 49 policies x %d development map-seats" % len(plan),
        "champion": str(H.CHAMPION.relative_to(H.REPO)),
        "referee_sha256": __import__("fuzz_panel").referee_sha256(),
        "maps_in_corpus": corpus, "map_seats": len(plan), "turns": args.turns,
        "seed": args.seed, "policies": names,
        "baseline": base, "arms": rows,
        "elapsed_s": round(time.time() - t0, 1),
    }
    path = HERE / "results" / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True) + "\n")
    print("\nwrote %s (%.0fs)" % (path, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
