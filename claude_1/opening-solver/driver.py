"""Solve one panel map (one seat): sweep the third troll's chop power, the second troll's
talents the draw affords, N rollouts each; keep the earliest completion, tie-break the bank."""
from __future__ import annotations

import random
import time

import world
import solver
import enumerate as en


def bank_points(s: world.State):
    """The bank in points plus the standing wood of the trees we planted (4 a size unit)."""
    own_wood = sum(p.size for p in s.plants.values() if p.own)
    return s.score + 4 * own_wood


def evaluate(s0, plan_args, rng, horizon):
    plan = solver.Plan(**plan_args)
    s = solver.rollout(s0, plan, rng, horizon=horizon)
    done = len(s.trains) >= (2 if plan_args["t2"] else 1)
    t_done = s.trains[-1][0] if done else None
    return s, done, t_done


def solve_map(item, seat=0, t3_list=None, rollouts=24, temps=(0.0, 0.15, 0.4), horizon=120,
              seed=1, t2_list=None, seed_sets=None):
    s0 = world.make_state(item, seat)
    draw = item["draw"]
    t2s = t2_list if t2_list is not None else en.t2_candidates(draw, s0.m.has_iron)
    t3s = t3_list if t3_list is not None else en.T3_SWEEP["chop3"]
    seed_sets = seed_sets if seed_sets is not None else ([], ["LEMON"], ["LEMON", "LEMON"], ["LEMON", "PLUM"], ["LEMON", "LEMON", "PLUM"])
    best = None
    n = 0
    t0 = time.time()
    for t3 in t3s:
        for t2 in t2s:
            for seeds in seed_sets:
                for temp in temps:
                    for k in range(rollouts if temp > 0 else 1):
                        rng = random.Random(seed * 100003 + n)
                        n += 1
                        args = dict(t2=t2, t3=t3, seeds=list(seeds), temp=temp)
                        s, done, t_done = evaluate(s0, args, rng, horizon)
                        if not done:
                            continue
                        key = (t_done, -bank_points(s))
                        if best is None or key < best[0]:
                            best = (key, s, args)
    dt = time.time() - t0
    if best is None:
        return {"done": False, "rollouts": n, "seconds": dt}
    key, s, args = best
    return {"done": True, "turn": key[0], "bank": -key[1], "plan": args, "trains": s.trains,
            "log": s.log, "rollouts": n, "seconds": dt, "inv": s.inv, "state": s}


if __name__ == "__main__":
    import sys
    import json
    import baseline
    n_maps = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    items = world.load_panel("../h2h-panel/panel-200-seed1.jsonl", n_maps)
    base = baseline.load()
    for it in items:
        for seat in (0, 1):
            r = solve_map(it, seat, rollouts=8)
            b = base[(it["rec"]["map_hash"], seat)]
            if r["done"]:
                print(f"{it['rec']['map_hash']} seat {seat} draw {it['draw']}: solver third troll turn {r['turn']} bank {r['bank']} "
                      f"plan t2={r['plan']['t2']} t3={r['plan']['t3']} seeds={r['plan']['seeds']} temp={r['plan']['temp']} | "
                      f"orchard6 second {b['orchard6_second']} third {b['orchard6_third']} {b['orchard6_third_talents']} | "
                      f"{r['rollouts']} rollouts {r['seconds']:.1f}s")
            else:
                print(f"{it['rec']['map_hash']} seat {seat}: NOT DONE within horizon ({r['rollouts']} rollouts {r['seconds']:.1f}s) | orchard6 third {b['orchard6_third']}")
