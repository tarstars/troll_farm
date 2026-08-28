#!/usr/bin/env python3
"""Decision tables (W4): one row per unit "trip" and per player-turn, from exact
reconstructed states (reconstruct.py).

A TRIP is a maximal run of MOVE (or idle) turns of one unit followed by the first
non-move action (HARVEST / CHOP / PLANT / PICK / DROP / MINE); zero-length trips
(an action without moving) are included.  The decision state is the PRE-turn
state at the trip's first turn; the destination is the cell where the unit acted.
The top bots emit step-wise MOVEs (target = next cell), so the destination cannot
be read from the MOVE command itself.

Outputs (gzipped jsonl, under fits/tables/):
  <player>_trips.jsonl.gz   one row per trip, with the candidate list (every tree
                            alive at the decision turn, with distances) embedded
  <player>_turns.jsonl.gz   one row per (game, turn): inventories, troll count,
                            TRAIN command if any, tree counts -- for the training
                            and endgame fits
Usage: python3 decision_tables.py <player> [max_games]
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reconstruct import Reconstructor, split_cmds  # noqa: E402

GAMES_INDEX = Path("/tmp/claude-1001/-home-tarstars-prj-troll-farm/b3cfddd0-5e42-47a2-92c0-d235979a1e81/scratchpad/w4/player_games.json")
TABLES = HERE / "tables"
ACTIONS = ("HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE")


def bfs(walkable, src):
    dist = {src: 0}
    q = deque([src])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)] + 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in walkable and (nx, ny) not in dist:
                dist[(nx, ny)] = d
                q.append((nx, ny))
    return dist


def unit_commands(cmds):
    """first command per unit id (the referee ignores re-used ids); TRAIN list."""
    per_unit, trains = {}, []
    for c in cmds:
        p = c.split()
        if not p:
            continue
        v = p[0].upper()
        if v == "TRAIN" and len(p) >= 5:
            trains.append([int(x) for x in p[1:5]])
        elif v in ("MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE") and len(p) >= 2 and p[1].lstrip("-").isdigit():
            uid = int(p[1])
            if uid not in per_unit:
                per_unit[uid] = (v, p[2:])
    return per_unit, trains


def build_tables(player, max_games=None, agent_id=None):
    games = json.load(open(GAMES_INDEX))[player]
    games = [g for g in games if g["n_turns"] == 300 and (agent_id is None or g["agentId"] == agent_id)]
    if max_games:
        games = games[:max_games]
    TABLES.mkdir(exist_ok=True)
    ftrips = gzip.open(TABLES / f"{player}_trips.jsonl.gz", "wt")
    fturns = gzip.open(TABLES / f"{player}_turns.jsonl.gz", "wt")
    n_trips = 0
    for gi, gm in enumerate(games):
        gid, seat = gm["gameId"], gm["seat"]
        r = Reconstructor(gid)
        # planter bookkeeping: plants created at turn t at a unit's cell -> that unit's seat
        planter = {}  # (x,y) -> [(seat, creation turn), ...] history; -1 = unknown planter

        def planter_at(pos, turn):
            """seat that planted the tree standing on pos at the start of `turn` (-1 = initial tree)."""
            who = -1
            for w, tc in planter.get(pos, ()):
                if tc < turn:
                    who = w
            return who
        states = []
        cmd_rows = []
        for t in range(1, r.n_turns + 1):
            st = r.snapshot(t)
            states.append(st)
            c0, c1 = r.commands(t)
            cmd_rows.append((c0, c1))
            before = {(p.x, p.y) for p in r.game.plants}
            r._pre_units = {u.id: (u.x, u.y, list(u.carry)) for u in r.game.units}
            r._pre_plants = [(p.pos, p.size, p.fruits, p.health) for p in r.game.plants]
            from sim.engine import step
            step(r.game, c0, c1)
            j = json.loads(r.frames[2 * t]["view"].split("\n", 1)[1])
            inv_after = [[int(v) for v in ln.split()] for ln in j["inputmodule"].split("\n")]
            r.apply_diff(t, j.get("diff", ""), inv_after)
            for p in r.game.plants:
                if p.pos not in before:
                    # who stood there with a PLANT command?
                    who = -1
                    for s_, cm in ((0, c0), (1, c1)):
                        pu, _ = unit_commands(cm)
                        for uid, (v, args) in pu.items():
                            if v == "PLANT":
                                uu = next((u for u in st["units"] if u["id"] == uid), None)
                                if uu and (uu["x"], uu["y"]) == p.pos:
                                    who = s_
                    planter.setdefault(p.pos, []).append((who, t))
        bad = {k: v for k, v in r.mismatch.items() if not k.startswith("growth")}
        g = r.game
        walk = g.walkable
        shack_own, shack_opp = g.shacks[seat], g.shacks[1 - seat]
        d_own = bfs(walk | {shack_own}, shack_own)
        d_opp = bfs(walk | {shack_opp}, shack_opp)
        water_adj = {c for c in walk if any((c[0] + dx, c[1] + dy) in g.water for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        iron_adj = {c for c in walk if any((c[0] + dx, c[1] + dy) in g.iron for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        # per-turn player rows
        T = r.n_turns
        per_turn_cmds = []
        for t in range(1, T + 1):
            cm = cmd_rows[t - 1][seat]
            pu, trains = unit_commands(cm)
            per_turn_cmds.append(pu)
            st = states[t - 1]
            own = [u for u in st["units"] if u["player"] == seat]
            trees = st["plants"]
            fturns.write(json.dumps({
                "g": gid, "seat": seat, "t": t, "inv": st["inv"][seat], "inv_opp": st["inv"][1 - seat],
                "n": len(own), "n_opp": len(st["units"]) - len(own),
                "talents": [[u["ms"], u["cc"], u["hp"], u["chop"]] for u in own],
                "carry": [sum(u["carry"]) for u in own],
                "train": trains[0] if trains else None,
                "trees": len(trees), "trees_fruit": sum(p["fruits"] for p in trees),
                "own_planted_alive": sum(1 for p in trees if planter_at((p["x"], p["y"]), t) == seat),
                "verbs": sorted(v for v, _ in pu.values()),
            }, separators=(",", ":")) + "\n")
        # trips
        unit_ids = sorted({u["id"] for st in states for u in st["units"] if u["player"] == seat})
        for uid in unit_ids:
            t = 1
            trip_start = None
            while t <= T:
                st = states[t - 1]
                u = next((x for x in st["units"] if x["id"] == uid), None)
                if u is None:
                    t += 1
                    continue
                cmd = per_turn_cmds[t - 1].get(uid)
                verb = cmd[0] if cmd else None
                if verb in ACTIONS:
                    s = trip_start if trip_start is not None else t
                    st_s = states[s - 1]
                    us = next(x for x in st_s["units"] if x["id"] == uid)
                    dest = (u["x"], u["y"])
                    # how many consecutive turns the same action continues at dest
                    k, tt = 0, t
                    outcome = {}
                    while tt <= T:
                        c2 = per_turn_cmds[tt - 1].get(uid)
                        u2 = next((x for x in states[tt - 1]["units"] if x["id"] == uid), None)
                        if not c2 or c2[0] != verb or u2 is None or (u2["x"], u2["y"]) != dest:
                            break
                        k += 1
                        tt += 1
                    # outcome of the action run: carry delta over the run
                    u_end = next((x for x in states[min(tt, T + 1) - 1]["units"] if x["id"] == uid), None) if tt <= T else next((x for x in states[T]["units"] if x["id"] == uid), None) if len(states) > T else None
                    dsrc = bfs(walk | {(us["x"], us["y"])}, (us["x"], us["y"]))
                    tree_at_dest = next((p for p in st_s["plants"] if (p["x"], p["y"]) == dest), None)
                    tree_at_dest_now = next((p for p in st["plants"] if (p["x"], p["y"]) == dest), None)
                    cands = []
                    for p in st_s["plants"]:
                        c = (p["x"], p["y"])
                        occ_own = sum(1 for x in st_s["units"] if x["player"] == seat and x["id"] != uid and (x["x"], x["y"]) == c)
                        occ_opp = sum(1 for x in st_s["units"] if x["player"] != seat and (x["x"], x["y"]) == c)
                        cands.append([c[0], c[1], p["type"][0], p["size"], p["fruits"], p["health"], p["cooldown"],
                                      dsrc.get(c, -1), d_own.get(c, -1), d_opp.get(c, -1), int(c in water_adj),
                                      planter_at(c, s), occ_own, occ_opp])
                    row = {
                        "g": gid, "seat": seat, "u": uid, "tal": [us["ms"], us["cc"], us["hp"], us["chop"]],
                        "s": s, "e": t, "k": k, "pos": [us["x"], us["y"]], "dest": list(dest),
                        "act": verb, "arg": (cmd[1][0] if cmd[1] else None),
                        "carry_s": us["carry"], "carry_e": u["carry"],
                        "carry_after": (u_end["carry"] if u_end else None),
                        "inv": st_s["inv"][seat], "inv_opp": st_s["inv"][1 - seat],
                        "n_own": sum(1 for x in st_s["units"] if x["player"] == seat),
                        "others": [[x["id"], x["x"], x["y"], x["ms"], x["cc"], x["hp"], x["chop"], sum(x["carry"])]
                                   for x in st_s["units"] if x["id"] != uid],
                        "others_player": [x["player"] for x in st_s["units"] if x["id"] != uid],
                        "dest_tree_s": ([tree_at_dest["type"][0], tree_at_dest["size"], tree_at_dest["fruits"], tree_at_dest["health"]] if tree_at_dest else None),
                        "dest_tree_e": ([tree_at_dest_now["type"][0], tree_at_dest_now["size"], tree_at_dest_now["fruits"], tree_at_dest_now["health"]] if tree_at_dest_now else None),
                        "dest_shack_adj": int(abs(dest[0] - shack_own[0]) + abs(dest[1] - shack_own[1]) == 1),
                        "dest_iron_adj": int(dest in iron_adj), "dest_water_adj": int(dest in water_adj),
                        "dest_d_own": d_own.get(dest, -1), "dest_d_opp": d_opp.get(dest, -1),
                        "dest_d_unit": dsrc.get(dest, -1),
                        "dest_planter": planter_at(dest, s),
                        "cands": cands,
                    }
                    ftrips.write(json.dumps(row, separators=(",", ":")) + "\n")
                    n_trips += 1
                    trip_start = None
                    t = max(tt, t + 1)
                    continue
                if verb == "MOVE" or verb is None:
                    if trip_start is None:
                        trip_start = t
                t += 1
        print(f"[{gi+1}/{len(games)}] game {gid} seat {seat}: trips so far {n_trips}; validator {bad if bad else 'exact'}", flush=True)
    ftrips.close()
    fturns.close()


if __name__ == "__main__":
    build_tables(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "0" else None,
                 int(sys.argv[3]) if len(sys.argv) > 3 else None)
