#!/usr/bin/env python3
"""The three observation packets chatgpt_1's cross-review (2026-09-01) asked for, from replays only.

1. The endgame truth table: every pre-251 turn with at most four living trees, classified by
   score relation, shack fruit, and whether a worker had a tree left to work — and whether the
   conversion started on that turn.  Written both as counts (observations-extra.json) and as
   the per-turn table the implementer gets (cleanroom/package/endgame-truth-table.json).
2. Tree commitment: after a worker's first chop on a map tree, does it stay until the tree
   falls, leave and return, hand over to its teammate, or abandon it?
3. Worker coordination: co-chopping, journeys to a tree the teammate already stood on, and
   moves blocked by the teammate.

Run:  python3 cleanroom/spec-work/measure_extra.py
"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "observations-extra.json")
TABLE = os.path.join(HERE, "..", "package", "endgame-truth-table.json")


def score(inv):
    return sum(inv[:4]) + 4 * inv[5]


def relation(mine, opp):
    return "behind" if mine < opp else "ahead" if mine > opp else "tied"


def endgame_table(games):
    rows = []
    starts = []
    for g in games:
        seat = g["seat"]
        first_pick = next((t + 1 for t, cmds in enumerate(g["commands"])
                           if any(v == "PICK" for v, _ in cmds)), None)
        for t in range(1, min(251, g["turns"] + 1)):
            st = g["states"][t - 1]
            trees = [p for p in st["plants"] if p["health"] > 0]
            if len(trees) > 4:
                continue
            if first_pick is not None and t > first_pick:
                break
            own = corpus.own_units(st, seat)
            occupied = {(u["x"], u["y"]) for u in own}
            trees_free = sum(1 for p in trees if (p["x"], p["y"]) not in occupied)
            workers_on_a_tree = sum(1 for u in own if corpus.plant_at(st, u["x"], u["y"]) is not None
                                    and corpus.plant_at(st, u["x"], u["y"])["health"] > 0)
            workers_carrying = sum(1 for u in own if sum(u["carry"]) > 0)
            workers_free = sum(1 for u in own if sum(u["carry"]) == 0
                               and corpus.plant_at(st, u["x"], u["y"]) is None)
            mine, opp = score(st["inventories"][seat]), score(st["inventories"][1 - seat])
            verbs = sorted({v for v, _ in g["commands"][t - 1]})
            row = {"game": g["game_id"], "turn": t, "trees_alive": len(trees),
                   "trees_not_under_an_own_worker": trees_free,
                   "own_workers": len(own), "workers_on_a_tree": workers_on_a_tree,
                   "workers_carrying": workers_carrying, "workers_free": workers_free,
                   "score_mine": mine, "score_opponent": opp, "relation": relation(mine, opp),
                   "shack_fruit": sum(st["inventories"][seat][:4]),
                   "commands": verbs,
                   "conversion_starts_this_turn": first_pick == t}
            rows.append(row)
            if first_pick == t:
                starts.append(row)
    counts = collections.Counter()
    for r in rows:
        key = ("start" if r["conversion_starts_this_turn"] else "no start",
               r["relation"],
               "a worker is free and no tree is left for it" if r["workers_free"] > 0 and r["trees_not_under_an_own_worker"] == 0
               else "a free worker and a free tree" if r["workers_free"] > 0
               else "no free worker")
        counts[key] += 1
    by_relation_at_start = collections.Counter(r["relation"] for r in starts)
    free_tree_at_start = collections.Counter(r["trees_not_under_an_own_worker"] for r in starts)
    no_fruit = sum(1 for r in rows if not r["conversion_starts_this_turn"] and r["shack_fruit"] == 0)
    return rows, {
        "pre_251_turns_with_at_most_4_trees_before_or_at_the_first_pick": len(rows),
        "of_which_the_conversion_started": len(starts),
        "score_relation_at_the_102_early_starts": dict(by_relation_at_start),
        "trees_not_under_an_own_worker_at_the_early_starts": {str(k): v for k, v in sorted(free_tree_at_start.items())},
        "no_start_turns_with_an_empty_shack": no_fruit,
        "turns_by_start_relation_and_worker_state": {" / ".join(k): v for k, v in sorted(counts.items())},
    }


def commitment(games):
    """For each (game, natural tree) chopped by an own worker: what happened after its first chop."""
    outcome = collections.Counter()
    for g in games:
        seat = g["seat"]
        natural = {(p["x"], p["y"]) for p in g["states"][0]["plants"]}
        # chops per turn: turn -> {cell: set(own uids)}
        chops = collections.defaultdict(lambda: collections.defaultdict(set))
        for t, cmds in enumerate(g["commands"], 1):
            st = g["states"][t - 1]
            for v, args in cmds:
                if v == "CHOP":
                    u = corpus.unit_by_id(st, args[0])
                    if u:
                        chops[t][(u["x"], u["y"])].add(args[0])
        alive = [{(p["x"], p["y"]) for p in st["plants"]} for st in g["states"]]
        seen = set()
        for t in sorted(chops):
            for cell, uids in chops[t].items():
                if cell not in natural or cell in seen or cell not in alive[t - 1]:
                    continue
                seen.add(cell)
                first = min(uids)
                # follow the tree until it dies (absent from alive) or the game ends
                death = next((tt for tt in range(t, g["turns"] + 1) if cell not in alive[tt]), None)
                last = death if death is not None else g["turns"]
                turns = list(range(t, last))
                by_first = [first in chops[tt].get(cell, set()) for tt in turns]
                by_mate = [bool(chops[tt].get(cell, set()) - {first}) for tt in turns]
                if death is None:
                    outcome["tree still standing at the end of the match"] += 1
                elif all(by_first):
                    outcome["the first worker chopped every turn until it fell" + (" (teammate helped)" if any(by_mate) else "")] += 1
                elif any(by_first[i] for i in range(len(by_first)) if not all(by_first[:i + 1])) and by_first[-1]:
                    outcome["the first worker left and came back to finish it"] += 1
                elif any(by_mate) and by_mate[-1]:
                    outcome["handed over: the teammate felled it"] += 1
                else:
                    outcome["abandoned: felled by nobody of ours (opponent) after our first chop"] += 1
    total = sum(outcome.values())
    return {"natural_trees_first_chopped_by_us": total, "outcomes": dict(outcome.most_common())}


def coordination(games):
    co_chop = 0
    both_alive_turns = 0
    journeys = 0
    journeys_to_teammates_tree = 0
    blocked = 0
    moves_within_speed = 0
    for g in games:
        seat = g["seat"]
        walk = corpus.walkable_set(g)
        last_cell = {}
        for t, cmds in enumerate(g["commands"], 1):
            st, nxt = g["states"][t - 1], g["states"][t]
            own = corpus.own_units(st, seat)
            if len(own) >= 2:
                both_alive_turns += 1
            chopped = collections.Counter()
            for v, args in cmds:
                u = corpus.unit_by_id(st, args[0]) if args else None
                if u is None:
                    continue
                cell = (u["x"], u["y"])
                if v == "CHOP":
                    chopped[cell] += 1
                    if last_cell.get(u["id"]) != cell:
                        journeys += 1
                        mates_on = any(o["id"] != u["id"] and (o["x"], o["y"]) == cell for o in own)
                        journeys_to_teammates_tree += mates_on
                    last_cell[u["id"]] = cell
                elif v == "MOVE":
                    tgt = (args[1], args[2])
                    d = corpus.bfs(walk, [cell]).get(tgt)
                    if d is not None and d <= u["ms"]:
                        moves_within_speed += 1
                        after = corpus.unit_by_id(nxt, u["id"])
                        if after and (after["x"], after["y"]) == cell:
                            mate_there = any(o["id"] != u["id"] and (o["x"], o["y"]) == tgt for o in own) or \
                                any(o["id"] != u["id"] and (o["x"], o["y"]) == tgt for o in corpus.own_units(nxt, seat))
                            blocked += mate_there
            co_chop += sum(1 for c, n in chopped.items() if n >= 2)
    return {"turns_with_two_workers": both_alive_turns,
            "turns_both_workers_chopped_the_same_tree": co_chop,
            "chop_journeys": journeys,
            "journeys_that_ended_on_a_tree_the_teammate_was_standing_on": journeys_to_teammates_tree,
            "moves_within_speed": moves_within_speed,
            "moves_within_speed_that_did_not_happen_with_the_teammate_on_the_target_cell": blocked}


def main():
    games = list(corpus.games())
    rows, summary = endgame_table(games)
    obs = {"endgame_trigger": summary, "tree_commitment": commitment(games),
           "worker_coordination": coordination(games)}
    with open(OUT, "w") as handle:
        json.dump(obs, handle, indent=1, sort_keys=True)
    with open(os.path.abspath(TABLE), "w") as handle:
        json.dump({"what": "every turn before 251 in the reference bot's 160 recorded matches on which at most "
                           "four trees were alive, up to and including the turn its fruit-to-wood conversion "
                           "started (its first PICK); relation = its score against the opponent's at the start "
                           "of the turn; 'free' worker = carrying nothing and not standing on a tree",
                   "summary": summary, "rows": rows}, handle, indent=1)
    print(json.dumps(obs, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
