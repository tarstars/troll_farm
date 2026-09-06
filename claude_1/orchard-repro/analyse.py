#!/usr/bin/env python3
"""Turn the value run into the numbers the card asks for.

Registered before the run (PREREGISTRATION secs 5, 6):
  * exclusion rule, RELATIVE: a policy is excluded on a map-seat only if its longest
    no-command streak exceeds the CHAMPION'S OWN on that same map-seat;
  * an ABSOLUTE-threshold variant reported side by side, with what the dropped
    policies score;
  * selector: leave-one-map-out across the 24 map-seats;
  * beside it, the fixed-policy delta of every surviving policy with NO selection --
    the table that tells "the selector never planted" apart from "planting gained
    nothing";
  * a per-map hindsight oracle, labelled as an upper bound, never as a result;
  * the margin as a curve over turns, not only at 300.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABS_THRESHOLD = 60      # fuzz_panel's own stall window (>= 60 live turns), sec 5 variant


def ci95(xs):
    n = len(xs)
    m = statistics.fmean(xs)
    if n < 2:
        return m, m, m
    h = 1.96 * statistics.stdev(xs) / (n ** 0.5)
    return m, m - h, m + h


def main():
    d = json.load(open(HERE / "results" / (sys.argv[1] if len(sys.argv) > 1
                                           else "value.json")))
    names = d["policies"]
    arms = d["arms"]
    base = d["baseline"]
    n_maps = len(base)
    CONTROLS = ("NO_PLANT", "BANK_ONLY")
    planting = [p for p in names if p not in CONTROLS]

    if "BANK_ONLY" in arms:
        dm = [r["d_margin"] for r in arms["BANK_ONLY"]]
        do = [r["d_own"] for r in arms["BANK_ONLY"]]
        m, lo, hi = ci95(dm)
        mo, lo2, hi2 = ci95(do)
        bank_only = {"d_margin": round(m, 3), "d_margin_ci": [round(lo, 3), round(hi, 3)],
                     "d_own": round(mo, 3), "d_own_ci": [round(lo2, 3), round(hi2, 3)],
                     "n": len(dm)}
    else:
        bank_only = None

    # ---- the two exclusion rules ---------------------------------------
    rel_excl, abs_excl = {}, {}
    for p in names:
        rel_excl[p] = [r["map_hash"] for r in arms[p]
                       if r["streak"] > r["base_streak"]]
        abs_excl[p] = [r["map_hash"] for r in arms[p]
                       if r["streak"] > ABS_THRESHOLD]
    champ_streaks = [b["streak"] for b in base]

    # a policy survives a rule if it is excluded on NO map-seat (chatgpt_1's shape:
    # "excluded 17 of 20 policies", i.e. policy-level, not map-level)
    rel_survivors = [p for p in planting if not rel_excl[p]]
    abs_survivors = [p for p in planting if not abs_excl[p]]

    # ---- fixed-policy table, no selection at all ------------------------
    fixed = {}
    for p in planting:
        dm = [r["d_margin"] for r in arms[p]]
        do = [r["d_own"] for r in arms[p]]
        m, lo, hi = ci95(dm)
        mo, lo2, hi2 = ci95(do)
        fixed[p] = {
            "d_margin": round(m, 3), "d_margin_ci": [round(lo, 3), round(hi, 3)],
            "d_own": round(mo, 3), "d_own_ci": [round(lo2, 3), round(hi2, 3)],
            "n": len(dm),
            "planted": sum(r["plants_landed"] for r in arms[p]),
            "attempted": sum(r["plants_attempted"] for r in arms[p]),
            "max_streak": max(r["streak"] for r in arms[p]),
            "rel_excluded_on": len(rel_excl[p]), "abs_excluded_on": len(abs_excl[p]),
        }

    # ---- leave-one-map-out selector -------------------------------------
    def loo(pool):
        chosen, deltas, own = [], [], []
        for i in range(n_maps):
            best, best_v = "NO_PLANT", 0.0
            for p in pool:
                v = statistics.fmean([arms[p][j]["d_margin"]
                                      for j in range(n_maps) if j != i])
                if v > best_v:
                    best, best_v = p, v
            chosen.append(best)
            deltas.append(arms[best][i]["d_margin"] if best != "NO_PLANT" else 0.0)
            own.append(arms[best][i]["d_own"] if best != "NO_PLANT" else 0.0)
        return chosen, deltas, own

    out = {"map_seats": n_maps, "turns": d["turns"], "seed": d["seed"],
           "champion_streaks": {"min": min(champ_streaks), "median":
                                statistics.median(champ_streaks),
                                "max": max(champ_streaks)},
           "abs_threshold": ABS_THRESHOLD,
           "champion_itself_would_be_excluded_by_absolute_rule":
               sum(1 for s in champ_streaks if s > ABS_THRESHOLD),
           "exclusion": {
               "relative": {"survivors": len(rel_survivors), "of": len(planting),
                            "survivor_names": rel_survivors},
               "absolute": {"survivors": len(abs_survivors), "of": len(planting),
                            "survivor_names": abs_survivors}},
           "bank_only_control": bank_only,
           "fixed_policy_table": fixed}

    for label, pool in (("relative", rel_survivors), ("absolute", abs_survivors),
                        ("no_exclusion", planting)):
        chosen, deltas, own = loo(pool)
        m, lo, hi = ci95(deltas)
        mo, lo2, hi2 = ci95(own)
        out.setdefault("selected", {})[label] = {
            "pool_size": len(pool),
            "chose_NO_PLANT_on": sum(1 for c in chosen if c == "NO_PLANT"),
            "of_folds": n_maps,
            "choices": chosen,
            "d_margin": round(m, 3), "d_margin_ci": [round(lo, 3), round(hi, 3)],
            "d_own": round(mo, 3), "d_own_ci": [round(lo2, 3), round(hi2, 3)],
        }

    # ---- hindsight oracle: an UPPER BOUND, not a result -----------------
    oracle_d, oracle_planted = [], 0
    for i in range(n_maps):
        best = max(planting + ["NO_PLANT"],
                   key=lambda p: 0.0 if p == "NO_PLANT" else arms[p][i]["d_margin"])
        v = 0.0 if best == "NO_PLANT" else arms[best][i]["d_margin"]
        oracle_d.append(v)
        if best != "NO_PLANT":
            oracle_planted += 1
    m, lo, hi = ci95(oracle_d)
    out["hindsight_oracle_UPPER_BOUND_NOT_A_RESULT"] = {
        "planted_on": oracle_planted, "of": n_maps,
        "d_margin": round(m, 3), "d_margin_ci": [round(lo, 3), round(hi, 3)]}

    # ---- margin curve: baseline vs the best fixed policy ----------------
    best_fixed = max(planting, key=lambda p: fixed[p]["d_margin"])
    curve = []
    for t in range(d["turns"]):
        a = statistics.fmean(b["curve"][t] for b in base)
        b_ = statistics.fmean(r["curve"][t] for r in arms[best_fixed])
        curve.append(round(b_ - a, 3))
    out["margin_curve"] = {"best_fixed_policy": best_fixed,
                           "d_margin_by_turn": curve,
                           "at": {str(t): curve[t - 1]
                                  for t in (25, 50, 75, 100, 150, 200, 250, 300)}}

    # worst/best and how many of the 48 are negative
    negs = sum(1 for p in planting if fixed[p]["d_margin"] < 0)
    out["headline"] = {
        "planting_policies": len(planting),
        "negative_mean_d_margin": negs,
        "best": {"policy": best_fixed, **{k: fixed[best_fixed][k]
                                          for k in ("d_margin", "d_margin_ci")}},
        "worst": {"policy": min(planting, key=lambda p: fixed[p]["d_margin"])},
        "baseline_mean_margin": round(statistics.fmean(b["margin"] for b in base), 3),
    }

    path = HERE / "results" / "analysis.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in out.items()
                      if k != "fixed_policy_table" and k != "margin_curve"},
                     indent=2, sort_keys=True))
    print("\nmargin curve (best fixed policy %s):" % best_fixed)
    print(json.dumps(out["margin_curve"]["at"], sort_keys=True))
    print("\nwrote %s" % path)


if __name__ == "__main__":
    main()
