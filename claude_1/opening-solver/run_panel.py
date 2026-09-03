"""Solve every panel map on both seats, three ways, and write the schedules.

  free   : the solver picks the second troll from the draw; third troll (2,3,0,3) (orchard 6's).
  same   : the roster orchard 6 actually bought on that map-seat (its second AND third talents).
  chop2  : the solver's second troll; a third troll of chop 2, (2,3,0,2) -- the P sweep's middle point.
  chop1  : the solver's second troll; a third troll of chop 1, (2,3,0,1) -- the P sweep's cheap point.

Every kept schedule is replayed through sim/engine.py before it is written; a disagreement is a
hard error.  Output: schedules/<map_hash>-s<seat>.json and panel-summary.json."""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import time

import world
import driver
import replay
import baseline

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedules")


def solve_one(job):
    idx, item, seat, base = job
    out = {"map_hash": item["rec"]["map_hash"], "seat": seat, "draw": item["draw"], "index": idx,
           "orchard6": base, "solves": {}}
    variants = {"free": dict(t2_list=None, t3=(2, 3, 0, 3)), "chop2": dict(t2_list=None, t3=(2, 3, 0, 2)),
                "chop1": dict(t2_list=None, t3=(2, 3, 0, 1))}
    if base and base.get("orchard6_third_talents") and base.get("orchard6_second_talents"):
        variants["same"] = dict(t2_list=[tuple(base["orchard6_second_talents"])], t3=tuple(base["orchard6_third_talents"]))
    for name, kw in variants.items():
        r = driver.solve_map(item, seat, rollouts=8, refine=4, **kw)
        if not r["done"]:
            out["solves"][name] = {"done": False, "rollouts": r["rollouts"], "seconds": r["seconds"]}
            continue
        rep = replay.replay(item, r["log"], seat)
        if not rep["ok"] or rep["trains"] != r["trains"]:
            raise SystemExit(f"referee disagrees on {item['rec']['map_hash']} seat {seat} {name}: {rep} vs {r['trains']}")
        s = r["state"]
        out["solves"][name] = {
            "done": True, "turn": r["turn"], "bank": r["bank"], "plan": {k: (list(v) if isinstance(v, tuple) else v) for k, v in r["plan"].items()},
            "trains": [[t, list(tal), uid] for t, tal, uid in r["trains"]],
            "second_turn": r["trains"][0][0], "second_talents": list(r["trains"][0][1]),
            "third_turn": r["trains"][-1][0], "third_talents": list(r["trains"][-1][1]),
            "inventory_at_done": r["inv"], "score_at_done": s.score,
            "own_trees": [[list(c), p.kind, p.size] for c, p in s.plants.items() if p.own],
            "rollouts": r["rollouts"], "seconds": r["seconds"],
            "referee_score": rep["score"], "commands": r["log"],
        }
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    jobs_n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    items = world.load_panel(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "h2h-panel", "panel-200-seed1.jsonl"), n)
    base = baseline.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "h2h-panel", "results", "champion-vs-orchard6.json"))
    os.makedirs(OUT, exist_ok=True)
    jobs = [(i, it, seat, base.get((it["rec"]["map_hash"], seat))) for i, it in enumerate(items) for seat in (0, 1)]
    t0 = time.time()
    results = []
    with mp.Pool(jobs_n) as pool:
        for k, r in enumerate(pool.imap_unordered(solve_one, jobs), 1):
            results.append(r)
            with open(os.path.join(OUT, f"{r['map_hash']}-s{r['seat']}.json"), "w") as fh:
                json.dump(r, fh)
            f = r["solves"].get("free", {})
            s = r["solves"].get("same", {})
            print(f"[{k}/{len(jobs)}] {r['map_hash']} s{r['seat']} free {f.get('turn')} same {s.get('turn')} "
                  f"orchard6 {r['orchard6'] and r['orchard6'].get('orchard6_third')}  {time.time()-t0:.0f}s", flush=True)
    results.sort(key=lambda r: (r["index"], r["seat"]))
    summary = [{"map_hash": r["map_hash"], "seat": r["seat"], "draw": r["draw"],
                "orchard6_second": r["orchard6"] and r["orchard6"].get("orchard6_second"),
                "orchard6_third": r["orchard6"] and r["orchard6"].get("orchard6_third"),
                "orchard6_third_talents": r["orchard6"] and r["orchard6"].get("orchard6_third_talents"),
                "champion_second": r["orchard6"] and r["orchard6"].get("champion_second"),
                **{f"{name}_{k}": v for name, sol in r["solves"].items() for k, v in sol.items()
                   if k in ("done", "turn", "bank", "second_turn", "second_talents", "third_talents", "seconds", "rollouts")}}
               for r in results]
    with open(os.path.join(os.path.dirname(OUT), "panel-summary.json"), "w") as fh:
        json.dump({"maps": len(items), "map_seats": len(jobs), "wall_seconds": time.time() - t0, "rows": summary}, fh, indent=1)
    print("done", len(results), f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
