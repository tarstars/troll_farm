"""The premise the whole card rests on, measured: **is the wild forest actually empty when the
third troll arrives?**

The wood-charging gate died because the third troll adds no whole-game wood, and the owner's
reading was that the defect is not the troll but that there is nothing left for it to cut. That
reading is a claim about the board at turn ~108, and it has never been measured. This does it on
the collected 160-game champion corpus, replayed through the exact reconstructor
(`local_claude_1/reconstructions/fits/reconstruct.py`), so every turn carries the real board.

A tree is **wild** if it stands at turn 1; it is counted dead from the first turn its cell is empty
and never counted again even if something is replanted there. Standing wood is the sum of sizes
(each size unit is one wood at 4 points). Everything is restricted to the cells our shack can
reach.

    python3 forest_census.py --raw /data/scratch/claude1-lo/champ --agent 6693889 \
        --out results/forest-census-champ.json
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "local_claude_1" / "reconstructions" / "fits"))
import reconstruct as R  # noqa: E402

TURNS = (1, 50, 75, 100, 108, 125, 150, 200, 250, 300)
ORTH = ((1, 0), (-1, 0), (0, 1), (0, -1))


def bfs(walkable, starts):
    d, q = {c: 0 for c in starts if c in walkable}, deque(c for c in starts if c in walkable)
    while q:
        c = q.popleft()
        for dx, dy in ORTH:
            n = (c[0] + dx, c[1] + dy)
            if n in walkable and n not in d:
                d[n] = d[c] + 1
                q.append(n)
    return d


def census(path, agent):
    gid = int(Path(path).stem)
    r = R.Reconstructor(gid)
    states = r.run(keep_states=True)
    ours = next(a["index"] for a in r.replay["agents"] if a["agentId"] == agent)
    walk = set(r.game.walkable)
    shack = tuple(r.game.shacks[ours])
    doors = [(shack[0] + dx, shack[1] + dy) for dx, dy in ORTH if (shack[0] + dx, shack[1] + dy) in walk]
    dist = bfs(walk, doors)
    n = r.n_turns

    wild = {}          # cell -> (kind, alive)
    for p in states[1]["plants"]:
        c = (p["x"], p["y"])
        if c in dist:
            wild[c] = p["type"]
    alive = set(wild)
    out = {"gameId": gid, "our_seat": ours, "n_turns": n, "wild_trees_reachable": len(wild),
           "wild_by_dd": {}, "at": {}}
    for c in wild:
        b = "1-2" if dist[c] <= 2 else "3-4" if dist[c] <= 4 else "5-8" if dist[c] <= 8 else "9+"
        out["wild_by_dd"][b] = out["wild_by_dd"].get(b, 0) + 1

    for t in range(1, min(n, 300) + 1):
        here = {(p["x"], p["y"]): p for p in states[t]["plants"]}
        alive = {c for c in alive if c in here}
        if t in TURNS:
            wood = sum(here[c]["size"] for c in alive)
            near = [c for c in alive if dist[c] <= 4]
            all_st = [p for p in states[t]["plants"] if (p["x"], p["y"]) in dist]
            dds = sorted(dist[c] for c in alive)
            out["at"][t] = dict(wild_alive=len(alive), wild_wood=wood,
                                wild_dd_median=(dds[len(dds) // 2] if dds else None),
                                wild_dd_min=(dds[0] if dds else None),
                                wild_alive_dd_le4=len(near), wild_wood_dd_le4=sum(here[c]["size"] for c in near),
                                all_trees_reachable=len(all_st), all_wood_reachable=sum(p["size"] for p in all_st),
                                our_trolls=sum(1 for u in states[t]["units"] if u["player"] == ours))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--agent", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    R.RAW = Path(a.raw)
    games = sorted(Path(a.raw).glob("*.json"))
    if a.limit:
        games = games[: a.limit]
    res = []
    for i, g in enumerate(games, 1):
        try:
            res.append(census(g, a.agent))
        except Exception as e:                       # a game the reconstructor cannot fit is reported, not hidden
            res.append({"gameId": int(g.stem), "error": repr(e)})
        if i % 40 == 0:
            print(f"{i}/{len(games)}", flush=True)
    ok = [g for g in res if "error" not in g]
    summary = {"n_games": len(res), "n_ok": len(ok), "raw": a.raw, "agent": a.agent,
               "wild_trees_reachable": {"median": st.median(g["wild_trees_reachable"] for g in ok)},
               "at": {}}
    for t in TURNS:
        rows = [g["at"][t] for g in ok if t in g["at"]]
        if not rows:
            continue
        summary["at"][t] = {k: (round(st.median(v), 2) if (v := [r[k] for r in rows if r[k] is not None]) else None)
                            for k in rows[0]}
        summary["at"][t]["n"] = len(rows)
        summary["at"][t]["wild_wood_q1q3"] = [
            sorted(r["wild_wood"] for r in rows)[len(rows) // 4],
            sorted(r["wild_wood"] for r in rows)[3 * len(rows) // 4]]
        summary["at"][t]["games_with_no_wild_left"] = sum(1 for r in rows if r["wild_alive"] == 0)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"summary": summary, "games": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    errs = [g for g in res if "error" in g]
    if errs:
        print("errors", len(errs), [(g["gameId"], g["error"]) for g in errs[:3]])


if __name__ == "__main__":
    main()
