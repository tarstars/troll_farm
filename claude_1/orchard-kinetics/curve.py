"""Question 1: how much wood can an orchard deliver, and when — on every panel map-seat.

The orchard the map allows: the reachable, non-door, empty cells by walking distance from the
doors (`dd`), water-adjacent or inland.  A planting schedule: from turn `t0` the starter (speed 1,
carry 1) plants `k` seeds of one kind, one a trip, nearest cells first, water cells before inland
at equal distance; a trip is PICK at the door, `dd` steps out, PLANT, `dd` steps back: 2*dd + 2
turns, so tree i is planted on turn t_i = t0 + sum of the trips before it.  Each tree then follows
`kinetics.timeline` (checked against the referee) and is raided at the record's hazard
(`../opening-solver/raid-rate.json`: raids per 100 tree-turns by distance band and turn band).

Standing wood at turn T = sum over trees of size_i(T) * S_i(T), S_i the survival to T under the
hazard (the expected wood of the trees the enemy has not yet taken).  `raw` is the same with no
raids.  Convertible wood = min(standing, what the chop power on hand can fell in the window) is
question 2's job (charge.py); here the felling capacity is reported beside the curve.

Outputs results/curve.json: per kind and k the median / quartiles over 400 map-seats at turns
100/150/200/250/300, the wild forest's standing wood for comparison, and the per-map cell counts."""
from __future__ import annotations

import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "opening-solver"))
sys.path.insert(0, HERE)
import world                                   # noqa: E402
from kinetics import size_at, eff_cd, chop_turns  # noqa: E402

TURNS = (100, 150, 200, 250, 300)
KS = (5, 10, 15, 20, 30)
KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")
PANEL = os.path.join(HERE, "..", "h2h-panel", "panel-200-seed1.jsonl")
RAIDS = os.path.join(HERE, "..", "opening-solver", "raid-rate.json")


def dist_bin(d):
    return "1" if d <= 1 else "2" if d == 2 else "3" if d == 3 else "4-5" if d <= 5 else "6+"


def turn_bin(t):
    return "1-50" if t <= 50 else "51-100" if t <= 100 else "101-150" if t <= 150 else "151-200" if t <= 200 else "201-300"


def load_hazard():
    tab = json.load(open(RAIDS))["hazard"]
    h = {}
    for key, v in tab.items():
        db, tb = key.split("|")
        h[(db, tb)] = v["raids_per_100_tree_turns"] / 100.0 if v["tree_turns"] >= 200 else None
    # thin bands borrow the nearest populated band at the same turn
    for tb in ("1-50", "51-100", "101-150", "151-200", "201-300"):
        last = None
        for db in ("1", "2", "3", "4-5", "6+"):
            if h.get((db, tb)) is None:
                h[(db, tb)] = last
            last = h[(db, tb)]
    return h


HAZ = load_hazard()
# cumulative hazard per band from turn 1 to t (inclusive), for fast survival lookups
_CUM = {}
for db in ("1", "2", "3", "4-5", "6+"):
    acc, arr = 0.0, [0.0]
    for t in range(1, 321):
        acc += HAZ[(db, turn_bin(t))]
        arr.append(acc)
    _CUM[db] = arr


def survival(dd, t_plant, T):
    """Probability a tree planted on turn t_plant at door-distance dd is still ours at turn T."""
    if T <= t_plant:
        return 1.0
    c = _CUM[dist_bin(dd)]
    return math.exp(-(c[min(T, 320)] - c[t_plant]))


def cells_by_distance(m: world.Map, trees0_cells):
    """(dd, water, cell) for every reachable non-door empty cell, nearest first, water first."""
    out = []
    for c in m.reach:
        if c in m.doors or c in trees0_cells:
            continue
        dd = min(m.d(d, c) for d in m.doors)
        if dd >= 9999:
            continue
        out.append((dd, 0 if m.near_water[c] else 1, c))
    out.sort()
    return out


def schedule(cells, k, t0, carry=1):
    """Plant turns and cells for the first k cells: one seed a trip with carry 1."""
    plan, t = [], t0
    for dd, inland, c in cells[:k]:
        t = t + 2 * dd + 1           # PICK on turn t (at the door), walk dd, PLANT on turn t + dd + 1
        plan.append((t, dd, inland == 0, c))
        t += dd                      # walk back to the door before the next PICK
    return plan


def standing(plan, kind, T, raids=True):
    w = 0.0
    for t_i, dd, water, _ in plan:
        s = size_at(kind, water, T - t_i)
        w += s * (survival(dd, t_i, T) if raids else 1.0)
    return w


def wild_standing(m, trees0, T):
    """The wild forest's standing wood at turn T if nobody touched it (sizes grow to 4), on this
    seat's reachable side only counted by distance band: all reachable wild trees."""
    raw = 0
    for t in trees0:
        c = (t["x"], t["y"])
        if c not in m.reach:
            continue
        cd = t["cd_eff"]
        # from cur_cd it needs cur_cd ticks to the next step, then cd each
        steps_done = 0 if T <= 1 else (1 if t["cur_cd"] <= T - 1 else 0) + max(0, (T - 1 - t["cur_cd"]) // cd)
        raw += min(4, t["size"] + steps_done)
    return raw


def main():
    items = world.load_panel(PANEL)
    per_seat = []
    for idx, item in enumerate(items):
        for seat in (0, 1):
            m = world.Map(item["rec"], seat)
            t0cells = {(t["x"], t["y"]) for t in item["rec"]["trees0"]}
            cells = cells_by_distance(m, t0cells)
            row = dict(map_hash=item["rec"]["map_hash"], seat=seat, draw_fruit=sum(item["draw"][:4]), draw=item["draw"],
                       cells_le2=sum(1 for dd, _, _ in cells if dd <= 2), water_le2=sum(1 for dd, w, _ in cells if dd <= 2 and w == 0),
                       cells_le4=sum(1 for dd, _, _ in cells if dd <= 4), water_le4=sum(1 for dd, w, _ in cells if dd <= 4 and w == 0),
                       water_le8=sum(1 for dd, w, _ in cells if dd <= 8 and w == 0),
                       wild_now=wild_standing(m, item["rec"]["trees0"], 1), wild_100=wild_standing(m, item["rec"]["trees0"], 100),
                       wild_trees=sum(1 for t in item["rec"]["trees0"] if (t["x"], t["y"]) in m.reach), curves={})
            for k in KS:
                plan = schedule(cells, k, 2)
                row["curves"][k] = dict(last_plant_turn=plan[-1][0] if plan else None, mean_dd=st.mean(p[1] for p in plan) if plan else None,
                                        water_share=st.mean(1.0 if p[2] else 0.0 for p in plan) if plan else None)
                for kind in KINDS:
                    row["curves"][k][kind] = {"raided": [round(standing(plan, kind, T), 2) for T in TURNS],
                                              "raw": [standing(plan, kind, T, raids=False) for T in TURNS]}
            per_seat.append(row)
    # summaries
    def q(xs):
        xs = sorted(xs)
        return dict(median=round(st.median(xs), 1), q1=round(xs[len(xs) // 4], 1), q3=round(xs[3 * len(xs) // 4], 1), min=round(xs[0], 1), max=round(xs[-1], 1))
    summary = dict(n_map_seats=len(per_seat), turns=list(TURNS), ks=list(KS),
                   cells=dict(le2=q([r["cells_le2"] for r in per_seat]), water_le2=q([r["water_le2"] for r in per_seat]),
                              le4=q([r["cells_le4"] for r in per_seat]), water_le4=q([r["water_le4"] for r in per_seat]),
                              water_le8=q([r["water_le8"] for r in per_seat]), draw_fruit=q([r["draw_fruit"] for r in per_seat])),
                   wild=dict(trees=q([r["wild_trees"] for r in per_seat]), standing_turn1=q([r["wild_now"] for r in per_seat]),
                             standing_turn100_untouched=q([r["wild_100"] for r in per_seat])),
                   curves={})
    for k in KS:
        summary["curves"][k] = dict(last_plant_turn=q([r["curves"][k]["last_plant_turn"] for r in per_seat]),
                                    mean_dd=q([r["curves"][k]["mean_dd"] for r in per_seat]),
                                    water_share=q([r["curves"][k]["water_share"] for r in per_seat]))
        for kind in KINDS:
            summary["curves"][k][kind] = {mode: [q([r["curves"][k][kind][mode][i] for r in per_seat]) for i in range(len(TURNS))] for mode in ("raided", "raw")}
    summary["hazard_per_tree_turn"] = {f"{db}|{tb}": HAZ[(db, tb)] for db in ("1", "2", "3", "4-5", "6+") for tb in ("1-50", "51-100", "101-150", "151-200", "201-300")}
    summary["survival_examples"] = {f"dd{dd}_planted{t}_to{T}": round(survival(dd, t, T), 3) for dd in (1, 3) for t in (10, 40) for T in (100, 150, 200)}
    summary["fell_turns_c3_lone"] = {kind: chop_turns(kind, 3) for kind in KINDS}
    json.dump(dict(summary=summary, per_seat=per_seat), open(os.path.join(HERE, "results", "curve.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
