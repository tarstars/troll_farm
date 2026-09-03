#!/usr/bin/env python3
"""The owner's three live observations, measured on collected ladder games (task
20260903-owner-live-observations). One pass per game through the exact reconstructor
(`local_claude_1/reconstructions/fits/reconstruct.py`, the referee diff as the authority for
positions, carries, trees and inventories), then three readings per game:

1. SWITCHING, measured without reading intent. Neither bot's record carries a target: the champion's
   MOVE is rewritten by its resolver into a single step, and the v6 telemetry's chosen target reads
   NONE on exactly those turns (its "want" field ignores teammates' claims). So a troll's timeline is
   cut into *trips*: from the turn after its last action (or its spawn) to the turn it next acts
   (HARVEST/CHOP/DROP/PICK/PLANT/MINE) at a cell D. The shortest trip is ceil(bfs(start, D)/speed)
   turns; the EXCESS is the turns spent beyond it, and it is split into steps AWAY from D (the troll
   walked away from where it ended up going: a change of mind, or a dance), blocked moves (a MOVE
   that did not move it) and idle turns en route. The two-cell dance (on the same cell as two turns
   ago, having moved) is counted beside it. A trip the game ends before it finishes is counted apart.
   Split by phase at our third troll's TRAIN (the dispatcher's window in the new bot) and at turn 70.

2. TREES LEFT STANDING. At the final state: every living tree with kind, size, health, fruits and
   BFS distance from our shack's doors. `chop_candidates`' own arithmetic (predict_tree,
   chop_outcome, the carry-home test) replayed for every troll of ours at every turn of the last
   phase, so each end-standing tree has the last turn on which it was a candidate for any of our
   trolls, and, on the turn our chop candidates emptied for good, the cause that ruled it out per
   troll: hands full, unreachable, predicted dead, chop unfinishable, too far to return. The value of
   an unbanked cut: for each end-standing tree, the earliest turn one of our trolls could have felled
   it ignoring the walk home, and what the opponent then took from that tree after that turn.

3. ENEMY-PLANTED TREES. The replay carries both seats' commands, so provenance is exact: a tree that
   appears on a cell where a troll issued PLANT the same turn belongs to that troll's owner. Per game:
   the opponent's plants, how many we felled, how many still stand at the end, the fruit the opponent
   harvested from the ones we left and the fruit we took from them. Beside it, the adjacency inference
   the bot could run live (a new tree with an opponent troll orthogonally adjacent or on the cell the
   turn before) is scored against the exact provenance: hits, misses, false attributions.

    python3 claude_1/live-observations/observe.py --raw <dir of <gameId>.json> --agent 6693889 --out <json>
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE / "local_claude_1" / "reconstructions" / "fits"))
import reconstruct as R  # noqa: E402

TOTAL_TURNS = 300
LATE_FROM = 200  # the last phase for the chop-candidate replay
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}
ACT_HERE = ("HARVEST", "CHOP", "PLANT", "MINE")
ACT_SHACK = ("DROP", "PICK")
ORTH = ((1, 0), (-1, 0), (0, 1), (0, -1))


def ceil_div(a, b):
    return -(-a // b) if b > 0 else 10 ** 6


def bfs(walkable, starts):
    dist = {}
    frontier = []
    for s in starts:
        if s in walkable and s not in dist:
            dist[s] = 0
            frontier.append(s)
    while frontier:
        nxt = []
        for x, y in frontier:
            d = dist[(x, y)]
            for dx, dy in ORTH:
                c = (x + dx, y + dy)
                if c in walkable and c not in dist:
                    dist[c] = d + 1
                    nxt.append(c)
        frontier = nxt
    return dist


def parse_cmds(cmds):
    out = []
    for c in cmds:
        toks = c.split()
        if not toks:
            continue
        v = toks[0].upper()
        if v in ("MSG", "WAIT", "TRAIN"):
            out.append((v, None, toks[1:]))
        elif len(toks) >= 2 and toks[1].lstrip("-").isdigit():
            out.append((v, int(toks[1]), toks[2:]))
        else:
            out.append((v, None, toks[1:]))
    return out


def near_water(water, cell):
    return any((cell[0] + dx, cell[1] + dy) in water for dx, dy in ORTH)


def effective_cd(kind, wet):
    return PLANT_COOLDOWN[kind] - (WATER_BOOST[kind] if wet else 0)


def predict_tree(plant, turns, opp_chop, wet):
    size, health, fruits, cd = plant["size"], plant["health"], plant["fruits"], plant["cooldown"]
    for _ in range(turns):
        if opp_chop > 0:
            health -= opp_chop
            if health <= 0:
                return None
        if cd > 0:
            cd -= 1
        if cd == 0 and health > 0:
            if size < 4:
                size += 1
                health += HEALTH_SLOPE[plant["type"]]
                cd = effective_cd(plant["type"], wet)
            elif fruits < 3:
                fruits += 1
                cd = effective_cd(plant["type"], wet)
    return size, health, cd


def chop_outcome(kind, size, health, cd, chop_power, wet):
    if chop_power <= 0:
        return None
    reset = effective_cd(kind, wet)
    for turns in range(1, 101):
        health -= chop_power
        if health <= 0:
            return turns, size
        if cd > 0:
            cd -= 1
        if cd == 0 and size < 4:
            size += 1
            health += HEALTH_SLOPE[kind]
            cd = reset
    return None


def chop_verdict(st, unit, plant, turn, walkable, water, shack, from_unit, to_shack, opp_units):
    """chop_candidates' decision for one (troll, tree) at pre-turn state of `turn`.
    Returns (status, turns_total, turns_unbanked). status 'feasible' or the first rule that ruled it out."""
    free = unit["cc"] - sum(unit["carry"])
    if unit["chop"] <= 0:
        return "no_chop", None, None
    if free <= 0:
        return "hands_full", None, None
    cell = (plant["x"], plant["y"])
    if plant["health"] <= 0 or cell not in from_unit:
        return "unreachable", None, None
    travel = ceil_div(from_unit[cell], unit["ms"])
    opp_chop = sum(u["chop"] for u in opp_units if (u["x"], u["y"]) == cell)
    wet = near_water(water, cell)
    pred = predict_tree(plant, travel, opp_chop, wet)
    if pred is None or pred[0] <= 0 or pred[1] <= 0:
        return "predicted_dead", None, None
    ret = to_shack.get(cell)
    ret = ceil_div(ret, unit["ms"]) if ret is not None else ceil_div(abs(cell[0] - shack[0]) + abs(cell[1] - shack[1]), unit["ms"])
    oc = chop_outcome(plant["type"], pred[0], pred[1], pred[2], unit["chop"], wet)
    if oc is None:
        return "unfinishable", None, None
    chop_turns, final_size = oc
    turns = max(travel + chop_turns + ret + 1, 1)
    unbanked = travel + chop_turns
    if turns > TOTAL_TURNS - turn + 1:
        return "too_far_to_return", turns, unbanked
    if min(final_size, free) <= 0:
        return "hands_full", turns, unbanked
    return "feasible", turns, unbanked


def target_of(v, args, unit, shack):
    if v == "MOVE" and len(args) >= 2:
        return ("cell", (int(args[0]), int(args[1])))
    if v in ACT_HERE:
        return ("act", (unit["x"], unit["y"]))
    if v in ACT_SHACK:
        return ("shack", shack)
    return None


def target_valid(prev, st, unit, ours_ids):
    """Is last turn's target still worth going to, for this troll, at this pre-turn state?"""
    kind, cell = prev
    if kind == "shack":
        return sum(unit["carry"]) > 0
    plant = next((p for p in st["plants"] if (p["x"], p["y"]) == cell and p["health"] > 0), None)
    free = unit["cc"] - sum(unit["carry"])
    if plant is None:
        return True  # an empty cell (a seed's cell, a door): nothing on the board invalidated it
    if free <= 0:
        return False
    if plant["fruits"] > 0 and unit["hp"] > 0:
        return True
    if unit["chop"] > 0:
        return True
    return False


def analyse(path, agent):
    gid = int(Path(path).stem)
    r = R.Reconstructor(gid)
    states = r.run(keep_states=True)
    ours = next(a["index"] for a in r.replay["agents"] if a["agentId"] == agent)
    theirs = 1 - ours
    walkable = set(r.game.walkable)
    water = set(r.game.water)
    shack = tuple(r.game.shacks[ours])
    opp_shack = tuple(r.game.shacks[theirs])
    doors = [(shack[0] + dx, shack[1] + dy) for dx, dy in ORTH if (shack[0] + dx, shack[1] + dy) in walkable]
    to_shack = bfs(walkable, doors)
    opp_doors = [(opp_shack[0] + dx, opp_shack[1] + dy) for dx, dy in ORTH if (opp_shack[0] + dx, opp_shack[1] + dy) in walkable]
    to_opp_shack = bfs(walkable, opp_doors)
    n = r.n_turns
    final = states[n]
    out = {"gameId": gid, "our_seat": ours, "n_turns": n, "mismatch": dict(r.mismatch),
           "score": {"ours": r.agents[ours]["score"], "theirs": r.agents[theirs]["score"]}}

    # roster: our third troll's TRAIN turn (first pre-turn state with three of ours)
    t3 = next((t for t in range(1, n + 1) if sum(1 for u in states[t - 1]["units"] if u["player"] == ours) >= 3), None)
    t2 = next((t for t in range(1, n + 1) if sum(1 for u in states[t - 1]["units"] if u["player"] == ours) >= 2), None)
    out["third_troll_turn"] = t3
    out["second_troll_turn"] = t2

    # ---- per-turn command tables, both seats
    cmds = {}
    for t in range(1, n + 1):
        c0, c1 = r.commands(t)
        cmds[t] = {0: parse_cmds(c0), 1: parse_cmds(c1)}

    # ---- 1. switching, intent-free: trips between actions, scored against the shortest path
    # A trip starts the turn after a troll's last action (or at its spawn) and ends on the turn it next
    # acts (HARVEST/CHOP/DROP/PICK/PLANT/MINE) at cell D. Its cost is the turns from start to arrival;
    # the shortest is ceil(bfs(start, D) / speed); the excess is turns lost on the way, split into
    # steps AWAY from D (a change of mind: the troll walked away from where it ended up going),
    # blocked moves (a MOVE that did not move the troll) and idle turns (no command while en route).
    # A trip that never ends before the game does is counted apart (no destination to score against).
    sw = {ph: collections.Counter() for ph in ("opening", "after", "le70", "gt70")}
    trip = {}   # unit -> dict(start_turn, start_pos, moves, blocked, idle, away, path)
    sw_examples = []
    dist_cache = {}

    def dist_to(cell):
        if cell not in dist_cache:
            dist_cache[cell] = bfs(walkable, [cell])
        return dist_cache[cell]

    def phases_of(t):
        return ("opening" if (t3 is None or t < t3) else "after", "le70" if t <= 70 else "gt70")

    for t in range(1, n + 1):
        st, nxt = states[t - 1], states[t]
        units = {u["id"]: u for u in st["units"] if u["player"] == ours}
        pos_next = {u["id"]: (u["x"], u["y"]) for u in nxt["units"]}
        by_unit = {}
        for v, uid, args in cmds[t][ours]:
            if uid in units:
                by_unit[uid] = (v, args)
        for uid, u in units.items():
            pos = (u["x"], u["y"])
            for ph in phases_of(t):
                sw[ph]["troll_turns"] += 1
            v, args = by_unit.get(uid, (None, []))
            if uid not in trip:
                trip[uid] = dict(start_turn=t, start_pos=pos, moves=0, blocked=0, idle=0, path=[pos], speed=u["ms"])
            tr = trip[uid]
            if v in ACT_HERE or v in ACT_SHACK:
                # the trip ends here at D = pos (DROP/PICK act at the shack from a door cell)
                if tr["moves"] + tr["idle"] + tr["blocked"] > 0 or tr["start_turn"] < t:
                    d = dist_to(pos)
                    shortest = ceil_div(d.get(tr["start_pos"], 0), max(tr["speed"], 1))
                    turns = t - tr["start_turn"]
                    away = 0
                    for a, b in zip(tr["path"], tr["path"][1:]):
                        if d.get(b, 10 ** 6) > d.get(a, 10 ** 6):
                            away += 1
                    excess = max(turns - shortest, 0)
                    for ph in phases_of(tr["start_turn"]):
                        c = sw[ph]
                        c["trips"] += 1
                        c["trip_turns"] += turns
                        c["shortest_turns"] += shortest
                        c["excess_turns"] += excess
                        c["away_steps"] += away
                        c["blocked_moves"] += tr["blocked"]
                        c["idle_in_trip"] += tr["idle"]
                        if away > 0:
                            c["trips_with_a_step_away"] += 1
                        if excess >= 3:
                            c["trips_excess_ge3"] += 1
                    if away > 0 and len(sw_examples) < 8:
                        sw_examples.append({"unit": uid, "start_turn": tr["start_turn"], "end_turn": t, "from": list(tr["start_pos"]),
                                            "to": list(pos), "shortest": shortest, "turns": turns, "away_steps": away, "path": [list(c) for c in tr["path"]]})
                # a new trip begins after this action (consecutive actions at the same cell extend nothing)
                trip[uid] = dict(start_turn=t + 1, start_pos=pos_next.get(uid, pos), moves=0, blocked=0, idle=0, path=[pos_next.get(uid, pos)], speed=u["ms"])
                continue
            if v == "MOVE":
                tr["moves"] += 1
                if pos_next.get(uid, pos) == pos:
                    tr["blocked"] += 1
            else:
                tr["idle"] += 1
            tr["path"].append(pos_next.get(uid, pos))
            h = tr["path"]
            if len(h) >= 3 and h[-1] == h[-3] and h[-1] != h[-2]:
                for ph in phases_of(t):
                    sw[ph]["dance_turns"] += 1
    for uid, tr in trip.items():
        turns = n + 1 - tr["start_turn"]
        if turns > 0:
            for ph in phases_of(tr["start_turn"]):
                sw[ph]["unfinished_trip_turns"] += turns
                sw[ph]["unfinished_trip_moves"] += tr["moves"]
                sw[ph]["unfinished_trip_idle"] += tr["idle"]
    out["switching"] = {k: dict(v) for k, v in sw.items()}
    out["switching_examples"] = sw_examples

    # ---- 2. trees left standing
    our_units_final = [u for u in final["units"] if u["player"] == ours]
    standing = []
    for p in final["plants"]:
        if p["health"] <= 0:
            continue
        cell = (p["x"], p["y"])
        standing.append({"cell": list(cell), "type": p["type"], "size": p["size"], "health": p["health"], "fruits": p["fruits"],
                         "door_dist": to_shack.get(cell), "opp_door_dist": to_opp_shack.get(cell)})
    # last chop by us; the chop-candidate replay over the last phase
    last_chop_turn = 0
    last_feasible_turn = collections.defaultdict(int)     # cell -> last turn feasible for any of ours
    last_feasible_unbanked = collections.defaultdict(int)
    earliest_unbanked_fell = {}                             # cell -> earliest turn a troll of ours could have felled it (no walk home), evaluated from LATE_FROM
    for t in range(1, n + 1):
        if any(v == "CHOP" for v, uid, a in cmds[t][ours]):
            last_chop_turn = t
    standing_cells = {tuple(s["cell"]) for s in standing}
    cause_at_empty = collections.Counter()
    empty_turn = None
    for t in range(LATE_FROM, n + 1):
        st = states[t - 1]
        opp_units = [u for u in st["units"] if u["player"] == theirs]
        any_feasible = False
        causes_this_turn = collections.Counter()
        for u in st["units"]:
            if u["player"] != ours:
                continue
            from_unit = bfs(walkable, [(u["x"], u["y"])])
            for p in st["plants"]:
                cell = (p["x"], p["y"])
                status, turns, unbanked = chop_verdict(st, u, p, t, walkable, water, shack, from_unit, to_shack, opp_units)
                if status == "feasible":
                    any_feasible = True
                if cell in standing_cells:
                    causes_this_turn[status] += 1
                    if status == "feasible":
                        last_feasible_turn[cell] = t
                    if unbanked is not None and unbanked <= TOTAL_TURNS - t + 1:
                        last_feasible_unbanked[cell] = t
                        if cell not in earliest_unbanked_fell:
                            earliest_unbanked_fell[cell] = t + unbanked
                        else:
                            earliest_unbanked_fell[cell] = min(earliest_unbanked_fell[cell], t + unbanked)
        if not any_feasible and empty_turn is None and t > last_chop_turn:
            empty_turn = t
            cause_at_empty = causes_this_turn
    # the opponent's take from end-standing trees after the earliest unbanked fell turn, and after our last chop
    opp_take_after_fell = 0     # points (fruit 1 each; wood 4 each)
    opp_take_after_last_chop = 0
    opp_take_late_all = 0
    our_take_late_standing = 0
    for t in range(1, n + 1):
        st, nxt = states[t - 1], states[t]
        before = {(p["x"], p["y"]): p for p in st["plants"]}
        after = {(p["x"], p["y"]): p for p in nxt["plants"]}
        opp_here = collections.defaultdict(list)
        our_here = collections.defaultdict(list)
        by_id = {u["id"]: u for u in st["units"]}
        for v, uid, a in cmds[t][theirs]:
            if uid in by_id and v == "HARVEST":
                opp_here[(by_id[uid]["x"], by_id[uid]["y"])].append(uid)
        for v, uid, a in cmds[t][ours]:
            if uid in by_id and v == "HARVEST":
                our_here[(by_id[uid]["x"], by_id[uid]["y"])].append(uid)
        for cell, p in before.items():
            taken = p["fruits"] - (after[cell]["fruits"] if cell in after else 0)
            if cell in after and after[cell]["fruits"] > p["fruits"]:
                taken = 0  # grew
            if taken <= 0:
                continue
            o, m = len(opp_here[cell]), len(our_here[cell])
            if o + m == 0:
                continue
            opp_share = taken * o / (o + m)
            if t >= LATE_FROM:
                opp_take_late_all += opp_share
            if cell in standing_cells:
                if cell in earliest_unbanked_fell and t > earliest_unbanked_fell[cell]:
                    opp_take_after_fell += opp_share
                if t > last_chop_turn:
                    opp_take_after_last_chop += opp_share
                if t >= LATE_FROM:
                    our_take_late_standing += taken * m / (o + m)
    for s in standing:
        cell = tuple(s["cell"])
        s["last_feasible_turn"] = last_feasible_turn.get(cell, 0)
        s["last_feasible_unbanked_turn"] = last_feasible_unbanked.get(cell, 0)
        s["earliest_unbanked_fell_turn"] = earliest_unbanked_fell.get(cell)
    out["standing"] = {
        "trees": standing, "count": len(standing),
        "our_trolls_final": [{"id": u["id"], "cell": [u["x"], u["y"]], "carry": sum(u["carry"]), "cc": u["cc"], "chop": u["chop"], "ms": u["ms"]} for u in our_units_final],
        "last_chop_turn": last_chop_turn, "candidates_empty_turn": empty_turn,
        "cause_at_empty": dict(cause_at_empty),
        "ever_feasible_since_200": sum(1 for s in standing if s["last_feasible_turn"] > 0),
        "ever_feasible_unbanked_since_200": sum(1 for s in standing if s["last_feasible_unbanked_turn"] > 0),
        "opp_take_from_standing_after_unbanked_fell_pts": round(opp_take_after_fell, 2),
        "opp_take_from_standing_after_our_last_chop_pts": round(opp_take_after_last_chop, 2),
        "opp_take_all_trees_since_200_pts": round(opp_take_late_all, 2),
        "our_take_from_standing_since_200_pts": round(our_take_late_standing, 2),
        "final_wood_ours": final["inv"][ours][5], "final_wood_theirs": final["inv"][theirs][5],
    }

    # ---- 3. enemy-planted trees (exact provenance from both command streams; the live inference scored)
    owner = {}          # cell -> ("ours"/"theirs"/"unknown", turn)
    infer = {}          # cell -> inferred owner by adjacency
    prov = collections.Counter()
    infer_score = collections.Counter()
    felled = collections.Counter()
    opp_plant_fruit_to_opp = 0.0
    opp_plant_fruit_to_us = 0.0
    for t in range(1, n + 1):
        st, nxt = states[t - 1], states[t]
        before = {(p["x"], p["y"]) for p in st["plants"]}
        after = {(p["x"], p["y"]): p for p in nxt["plants"]}
        by_id = {u["id"]: u for u in st["units"]}
        planters = {}
        for seat in (0, 1):
            for v, uid, a in cmds[t][seat]:
                if v == "PLANT" and uid in by_id and by_id[uid]["player"] == seat:
                    planters[(by_id[uid]["x"], by_id[uid]["y"])] = "ours" if seat == ours else "theirs"
        for cell in after:
            if cell in before:
                continue
            who = planters.get(cell, "unknown")
            owner[cell] = (who, t)
            prov[who] += 1
            # the live inference: an opponent troll on the cell or orthogonally adjacent at the pre-turn state
            opp_near = any(u["player"] == theirs and abs(u["x"] - cell[0]) + abs(u["y"] - cell[1]) <= 1 for u in st["units"])
            our_near = any(u["player"] == ours and abs(u["x"] - cell[0]) + abs(u["y"] - cell[1]) <= 1 for u in st["units"])
            guess = "theirs" if opp_near and not our_near else ("ours" if our_near and not opp_near else ("ambiguous" if opp_near and our_near else "nobody_near"))
            infer[cell] = guess
            infer_score[(who, guess)] += 1
        # fells and harvests on opponent-planted trees
        choppers = collections.defaultdict(set)
        harv = collections.defaultdict(lambda: [0, 0])
        for seat in (0, 1):
            for v, uid, a in cmds[t][seat]:
                if uid in by_id and by_id[uid]["player"] == seat:
                    c = (by_id[uid]["x"], by_id[uid]["y"])
                    if v == "CHOP":
                        choppers[c].add(seat)
                    if v == "HARVEST":
                        harv[c][seat] += 1
        for cell in before:
            if cell not in after and cell in owner and owner[cell][0] == "theirs":
                s = choppers.get(cell, set())
                felled["by_us" if ours in s and theirs not in s else "by_them" if theirs in s and ours not in s else "both" if s else "vanished_no_chop"] += 1
        bmap = {(p["x"], p["y"]): p for p in st["plants"]}
        for cell, (o, m) in ((c, (h[theirs], h[ours])) for c, h in harv.items()):
            if cell in owner and owner[cell][0] == "theirs" and cell in bmap:
                taken = bmap[cell]["fruits"] - (after[cell]["fruits"] if cell in after else 0)
                if cell in after and after[cell]["fruits"] > bmap[cell]["fruits"]:
                    taken = 0
                if taken > 0 and o + m > 0:
                    opp_plant_fruit_to_opp += taken * o / (o + m)
                    opp_plant_fruit_to_us += taken * m / (o + m)
    final_cells = {(p["x"], p["y"]) for p in final["plants"] if p["health"] > 0}
    theirs_standing = sum(1 for c, (w, t) in owner.items() if w == "theirs" and c in final_cells)
    ours_standing = sum(1 for c, (w, t) in owner.items() if w == "ours" and c in final_cells)
    out["provenance"] = {
        "planted": dict(prov), "opp_planted_felled": dict(felled),
        "opp_planted_standing_at_end": theirs_standing, "our_planted_standing_at_end": ours_standing,
        "fruit_opp_took_from_own_plants": round(opp_plant_fruit_to_opp, 2),
        "fruit_we_took_from_opp_plants": round(opp_plant_fruit_to_us, 2),
        "inference": {f"{w}->{g}": c for (w, g), c in infer_score.items()},
    }
    return out


def agg(games, label):
    ok = [g for g in games if "error" not in g]
    print(f"== {label}: {len(ok)} games ok of {len(games)} ==")
    t3 = [g["third_troll_turn"] for g in ok if g["third_troll_turn"]]
    print(f"third troll in {len(t3)}/{len(ok)} games, median turn {sorted(t3)[len(t3)//2] if t3 else None}")
    print("-- 1. switching, intent-free (trips between actions against the shortest path)")
    for ph in ("opening", "after", "le70", "gt70"):
        c = collections.Counter()
        for g in ok:
            c.update(g["switching"].get(ph, {}))
        tt = c["troll_turns"] or 1
        tr = c["trips"] or 1
        print(f"  {ph:8s} troll-turns {c['troll_turns']:7d}  trips {c['trips']:6d}  turns/trip {c['trip_turns']/tr:5.2f} shortest {c['shortest_turns']/tr:5.2f}  "
              f"EXCESS {c['excess_turns']:6d} ({c['excess_turns']/len(ok):5.2f}/game, {100*c['excess_turns']/tt:4.2f}% of troll-turns)  "
              f"away-steps {c['away_steps']:5d} ({100*c['away_steps']/tt:4.2f}/100)  trips-with-a-step-away {c['trips_with_a_step_away']:5d} ({100*c['trips_with_a_step_away']/tr:4.1f}%)  "
              f"blocked {c['blocked_moves']:5d}  idle-en-route {c['idle_in_trip']:5d}  dance {c['dance_turns']:5d} ({100*c['dance_turns']/tt:4.2f}/100)  "
              f"unfinished: turns {c['unfinished_trip_turns']:5d} moves {c['unfinished_trip_moves']:5d} idle {c['unfinished_trip_idle']:5d}")
    print("-- 2. trees left standing at the last turn")
    cnt = [g["standing"]["count"] for g in ok]
    trees = [s for g in ok for s in g["standing"]["trees"]]
    print(f"  standing per game mean {sum(cnt)/len(ok):.2f} median {sorted(cnt)[len(cnt)//2]}  total {len(trees)}")
    if trees:
        sz = collections.Counter(s["size"] for s in trees)
        print(f"  size mix {dict(sorted(sz.items()))}  mean health {sum(s['health'] for s in trees)/len(trees):.1f}  "
              f"door-dist median {sorted(s['door_dist'] if s['door_dist'] is not None else 99 for s in trees)[len(trees)//2]}  "
              f"unreachable-from-doors {sum(1 for s in trees if s['door_dist'] is None)}")
        lf = [s["last_feasible_turn"] for s in trees]
        print(f"  ever a banked chop candidate for one of ours in turns 200-300: {sum(1 for x in lf if x>0)} of {len(trees)}; "
              f"last such turn median {sorted(x for x in lf if x>0)[max(0,sum(1 for x in lf if x>0)//2-1)] if any(lf) else None}")
        lu = [s["last_feasible_unbanked_turn"] for s in trees]
        print(f"  fellable without the walk home at some turn 200-300: {sum(1 for x in lu if x>0)} of {len(trees)}")
    ce = collections.Counter()
    et = []
    for g in ok:
        ce.update(g["standing"]["cause_at_empty"])
        if g["standing"]["candidates_empty_turn"]:
            et.append(g["standing"]["candidates_empty_turn"])
    print(f"  chop candidates emptied for good in {len(et)} games, median turn {sorted(et)[len(et)//2] if et else None}; "
          f"cause per (troll, standing tree) on that turn: {dict(ce.most_common())}")
    print(f"  last CHOP by us: median turn {sorted(g['standing']['last_chop_turn'] for g in ok)[len(ok)//2]}")
    for k in ("opp_take_from_standing_after_unbanked_fell_pts", "opp_take_from_standing_after_our_last_chop_pts", "opp_take_all_trees_since_200_pts", "our_take_from_standing_since_200_pts"):
        v = [g["standing"][k] for g in ok]
        print(f"  {k:52s} mean {sum(v)/len(v):6.2f}/game  median {sorted(v)[len(v)//2]:6.2f}")
    print(f"  final wood ours mean {sum(g['standing']['final_wood_ours'] for g in ok)/len(ok):.1f}  theirs {sum(g['standing']['final_wood_theirs'] for g in ok)/len(ok):.1f}")
    print("-- 3. enemy-planted trees (exact provenance from the replay's two command streams)")
    pv = collections.Counter(); fe = collections.Counter(); inf = collections.Counter()
    ts = 0; os_ = 0; fo = 0.0; fu = 0.0
    for g in ok:
        p = g["provenance"]
        pv.update(p["planted"]); fe.update(p["opp_planted_felled"]); inf.update(p["inference"])
        ts += p["opp_planted_standing_at_end"]; os_ += p["our_planted_standing_at_end"]
        fo += p["fruit_opp_took_from_own_plants"]; fu += p["fruit_we_took_from_opp_plants"]
    n = len(ok)
    print(f"  planted per game: theirs {pv['theirs']/n:.2f}  ours {pv['ours']/n:.2f}  unattributed {pv['unknown']/n:.2f}  (totals {dict(pv)})")
    print(f"  opponent's plants: felled by us {fe['by_us']/n:.2f}/game, by them {fe['by_them']/n:.2f}, both {fe['both']/n:.2f}, vanished without a chop {fe['vanished_no_chop']/n:.2f}; standing at end {ts/n:.2f}/game")
    print(f"  fruit the opponent harvested from its own plants {fo/n:.2f}/game; fruit we took from them {fu/n:.2f}/game")
    print(f"  the live adjacency inference against the truth: {dict(inf)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--agent", type=int, default=6693889)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    R.RAW = Path(a.raw)
    games = sorted(Path(a.raw).glob("*.json"))
    if a.limit:
        games = games[: a.limit]
    res = []
    for i, g in enumerate(games, 1):
        try:
            res.append(analyse(g, a.agent))
        except Exception as e:
            res.append({"gameId": int(g.stem), "error": repr(e)})
        if i % 40 == 0:
            print(f"{i}/{len(games)}", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"raw": a.raw, "agent": a.agent, "games": res}, open(a.out, "w"), indent=1, sort_keys=True)
    errs = [g for g in res if "error" in g]
    if errs:
        print("errors", [(g["gameId"], g["error"]) for g in errs[:5]])
    agg(res, a.label or a.raw)


if __name__ == "__main__":
    main()
