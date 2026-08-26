#!/usr/bin/env python3
"""Downstream analysis of ring_pressure.py output: fe/fw per game-seat by cohort.

fe/fw = enemy_chop_on_my_ring / (harvest_ring + chop_ring)  (whole game, per game-seat)
Cohorts: leaders = {goq, yaichi, Stounate}; tass = our bot; field = everyone else.
"""
import json, sys, math, collections

LEADERS = {"goq", "yaichi", "Stounate"}

def quart(v):
    """Quartiles the way most quick analyses do it: numpy-style linear interpolation."""
    if not v:
        return None
    s = sorted(v)
    def q(p):
        if len(s) == 1:
            return s[0]
        i = p * (len(s) - 1)
        lo = math.floor(i); hi = math.ceil(i)
        return s[lo] + (s[hi] - s[lo]) * (i - lo)
    return dict(n=len(s), min=round(s[0], 3), q1=round(q(0.25), 3), median=round(q(0.5), 3),
                q3=round(q(0.75), 3), max=round(s[-1], 3),
                gt1=round(sum(1 for x in s if x > 1.0) / len(s), 4),
                gt056=round(sum(1 for x in s if x > 0.56) / len(s), 4),
                n_gt1=sum(1 for x in s if x > 1.0), n_gt056=sum(1 for x in s if x > 0.56))

def cohort(name):
    if name in LEADERS:
        return "leaders"
    if name == "tass":
        return "tass"
    return "field"

def main(path, mode="drop_zero_den"):
    d = json.load(open(path))
    rows = d["per_game_seat"]
    by = collections.defaultdict(list)
    stats = collections.Counter()
    turns = []
    unattr_tot = 0
    unattr_seats = 0
    for r in rows:
        turns.append(r["turns"])
        unattr_tot += r["unattributed"]
        if r["unattributed"]:
            unattr_seats += 1
        fe = r["enemy_chop_on_my_ring"]
        fw = r["harvest_ring"] + r["chop_ring"]
        c = cohort(r["name"])
        stats[c + "_rows"] += 1
        if fw == 0:
            stats[c + "_zero_den"] += 1
            if fe == 0:
                stats[c + "_zero_both"] += 1
            if mode == "drop_zero_den":
                continue
            elif mode == "zero_as_zero":
                val = 0.0
            elif mode == "drop_only_00":
                if fe == 0:
                    continue
                val = float(fe)  # den treated as 1
            elif mode == "den_max1":
                val = float(fe)
            else:
                continue
        else:
            val = fe / (max(fw, 1) if mode == "den_max1" else fw)
        by[c].append(val)
    out = {"mode": mode, "counts": dict(stats),
           "cohorts": {k: quart(v) for k, v in sorted(by.items())},
           "all_seats": len(rows),
           "unattributed_events_total": unattr_tot,
           "unattributed_seats": unattr_seats,
           "turns": quart([float(t) for t in turns]) if turns else None,
           "turn_hist": dict(sorted(collections.Counter(
               (t // 25) * 25 for t in turns).items()))}
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "drop_zero_den")
