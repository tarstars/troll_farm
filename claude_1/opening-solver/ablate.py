"""Where do orchard 6's turns go?  Counterfactuals on the solver itself, same roster as orchard 6
on each map-seat (its second and third troll talents):

  optimal      : the solver as is (second troll the turn the draw or the stock affords it).
  late_second  : the second troll may not be bought before the turn orchard 6 bought it.
  no_water     : seeds go next door only, never next to water (orchard 6 never seeks water).
  carry_one    : every troll brings one item a trip (the harvest and mine tasks want one unit).
  near_only    : wild trees farther than four steps from the shack are off limits.

Each ablation's completion turn minus the optimal one is the cost of that habit in turns, on that
map-seat, everything else re-optimised.  Runs a subset (the first N maps, both seats)."""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import statistics
import sys
import time

import world
import driver
import solver
import baseline

HERE = os.path.dirname(os.path.abspath(__file__))


def run_variant(item, seat, base, variant):
    t2 = tuple(base["orchard6_second_talents"])
    t3 = tuple(base["orchard6_third_talents"])
    kw = dict(t2_list=[t2], t3=t3, rollouts=6, refine=3)
    if variant == "late_second":
        kw["t2_not_before"] = base["orchard6_second"]
    elif variant == "no_water":
        kw["programmes"] = [p for p in driver.SEED_PROGRAMMES if all(m == "near" for _, m in p)]
    elif variant == "carry_one":
        solver.CARRY_ONE = True
    elif variant == "near_only":
        solver.NEAR_ONLY = 4
    try:
        r = driver.solve_map(item, seat, **kw)
    finally:
        solver.CARRY_ONE = False
        solver.NEAR_ONLY = None
    return r["turn"] if r["done"] else None


def one(job):
    item, seat, base = job
    out = {"map_hash": item["rec"]["map_hash"], "seat": seat, "orchard6_third": base["orchard6_third"],
           "orchard6_second": base["orchard6_second"]}
    for v in ("optimal", "late_second", "no_water", "carry_one", "near_only"):
        out[v] = run_variant(item, seat, base, v)
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    jobs_n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    items = world.load_panel(os.path.join(HERE, "..", "h2h-panel", "panel-200-seed1.jsonl"), n)
    base = baseline.load(os.path.join(HERE, "..", "h2h-panel", "results", "champion-vs-orchard6.json"))
    jobs = [(it, seat, base[(it["rec"]["map_hash"], seat)]) for it in items for seat in (0, 1)
            if base.get((it["rec"]["map_hash"], seat), {}).get("orchard6_third_talents")]
    t0 = time.time()
    rows = []
    with mp.Pool(jobs_n) as pool:
        for r in pool.imap_unordered(one, jobs):
            rows.append(r)
            print(r, f"{time.time()-t0:.0f}s", flush=True)
    json.dump(rows, open(os.path.join(HERE, "ablation.json"), "w"), indent=1)
    for v in ("late_second", "no_water", "carry_one", "near_only"):
        costs = [r[v] - r["optimal"] for r in rows if r[v] is not None and r["optimal"] is not None]
        print(f"{v:>12}: median cost {statistics.median(costs) if costs else None} turns, mean {statistics.mean(costs) if costs else None:.1f}, n {len(costs)}")
    gaps = [r["orchard6_third"] - r["optimal"] for r in rows if r["optimal"] is not None]
    print(f"orchard 6 minus optimal, same roster: median {statistics.median(gaps)} n {len(gaps)}")


if __name__ == "__main__":
    main()
