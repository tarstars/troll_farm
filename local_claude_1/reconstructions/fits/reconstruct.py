#!/usr/bin/env python3
"""Exact per-turn state reconstruction of a Troll Farm replay (W4, 2026-08-28).

Route: replay both seats' commands through our referee mirror `sim/engine.py`
(pre-turn state -> post-turn state), then overlay the keyframe's logical `diff`
(the referee's own entity changes: unit x/y/carry slots, plant health/stage/
cooldown resets, new units/plants) and the keyframe `inputmodule` inventories.
Every diff token is compared with the engine's prediction BEFORE it overwrites it,
so the run reports exactly where the engine and the referee disagree.  The diff
is the authority for positions, carries, plant health/stage and inventories; the
engine is the authority for the implicit plant cooldown countdown (the diff only
reports resets).

Usage:  python3 reconstruct.py <gameId> [--quiet]   -> prints a validation summary
Library: states = reconstruct(game_id) -> list of per-turn dicts (see `snapshot`).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/tarstars/prj/troll_farm-local_claude_1")
sys.path.insert(0, str(ROOT))
RAW = Path("/home/tarstars/prj/troll_farm/data/raw/games")

from sim.state import GameState, SimUnit, SimPlant  # noqa: E402
from sim.engine import step, recompute_scores  # noqa: E402

TYPES = ("PLUM", "LEMON", "APPLE", "BANANA")
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")


def b36(c):
    return int(c, 36)


def split_cmds(stdout):
    """';'/newline-separated commands; numeric plant aliases (PICK/PLANT id 0..3)
    are rewritten to the type names, as the referee accepts both spellings."""
    out = []
    for c in stdout.replace("\n", ";").split(";"):
        c = c.strip()
        if not c:
            continue
        p = c.split()
        if len(p) >= 3 and p[0].upper() in ("PICK", "PLANT") and p[2] in ("0", "1", "2", "3"):
            p[2] = TYPES[int(p[2])]
            c = " ".join(p)
        out.append(c)
    return out


def view_payload(view):
    if not view or "{" not in view:
        return None
    return json.loads(view.split("\n", 1)[1])


def parse_frame0(frame):
    j = view_payload(frame["view"])
    grid = j["global"]["inputmodule"].split("\n")
    w, h = (int(v) for v in grid[0].split())
    rows = grid[1:]
    units, plants = {}, {}
    for ent in j["frame"].get("diff", "").split(";"):
        p = ent.split()
        if len(p) != 3:
            continue
        eid, kind, val = p
        if kind == "W":
            uid, x, y, pl, ms, cc, hp, chop = (b36(c) for c in val)
            units[int(eid)] = dict(id=uid, player=pl, x=x, y=y, ms=ms, cc=cc, hp=hp, chop=chop)
        elif kind == "P":
            x, y, t, stage, cur_cd, health, cd_eff = (b36(c) for c in val)
            plants[int(eid)] = dict(type=TYPES[t], x=x, y=y, stage=stage, cooldown=cur_cd,
                                    health=health, cd_eff=cd_eff)
    inv = [[int(v) for v in ln.split()] for ln in j["frame"]["inputmodule"].split("\n")]
    return w, h, rows, units, plants, inv


def build_game(w, h, rows, units, plants, inv):
    walkable, iron, water = set(), set(), set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            c = (x, y)
            if ch == "0":
                shacks[0] = c
            elif ch == "1":
                shacks[1] = c
            elif ch == ".":
                walkable.add(c)
            elif ch == "+":
                iron.add(c)
            elif ch == "~":
                water.add(c)
    sim_units = [SimUnit(u["id"], u["player"], u["x"], u["y"], u["ms"], u["cc"], u["hp"], u["chop"], [0] * 6)
                 for u in units.values()]
    sim_plants = [SimPlant(p["type"], p["x"], p["y"], min(p["stage"], 4), p["health"],
                           max(p["stage"] - 4, 0), p["cooldown"]) for p in plants.values()]
    g = GameState(w, h, walkable, shacks, [list(inv[0]), list(inv[1])], sim_units, sim_plants,
                  [0, 0], 1, max(u.id for u in sim_units) + 1, iron, water)
    recompute_scores(g)
    return g


class Reconstructor:
    """Walks one replay; keeps engine state + entity-id maps; records mismatches."""

    def __init__(self, game_id):
        self.game_id = int(game_id)
        self.replay = json.loads((RAW / f"{game_id}.json").read_text())
        self.frames = self.replay["frames"]
        w, h, rows, units, plants, inv = parse_frame0(self.frames[0])
        self.map = dict(w=w, h=h, rows=rows)
        self.game = build_game(w, h, rows, units, plants, inv)
        self.unit_by_eid = {}   # entity id -> SimUnit
        self.plant_by_eid = {}  # entity id -> SimPlant
        by_id = {u.id: u for u in self.game.units}
        for eid, u in units.items():
            self.unit_by_eid[eid] = by_id[u["id"]]
        by_pos = {p.pos: p for p in self.game.plants}
        for eid, p in plants.items():
            self.plant_by_eid[eid] = by_pos[(p["x"], p["y"])]
        self.mismatch = Counter()
        self.examples = {}
        self.agents = {a["index"]: a for a in self.replay["agents"]}
        self.n_turns = (len(self.frames) - 1) // 2

    def note(self, kind, turn, detail):
        self.mismatch[kind] += 1
        self.examples.setdefault(kind, (turn, detail))

    def snapshot(self, turn):
        g = self.game
        return {
            "turn": turn,
            "inv": [list(g.inventories[0]), list(g.inventories[1])],
            "units": [dict(id=u.id, player=u.player, x=u.x, y=u.y, ms=u.ms, cc=u.cc, hp=u.hp,
                           chop=u.chop, carry=list(u.carry)) for u in g.units],
            "plants": [dict(type=p.type, x=p.x, y=p.y, size=p.size, health=p.health,
                            fruits=p.fruits, cooldown=p.cooldown) for p in g.plants],
        }

    def commands(self, t):
        f0, f1 = self.frames[2 * t - 1], self.frames[2 * t]
        assert f0.get("agentId") == 0 and f1.get("agentId") == 1 and f1.get("keyframe"), (self.game_id, t)
        return split_cmds(f0.get("stdout") or ""), split_cmds(f1.get("stdout") or "")

    def apply_diff(self, t, diff, inv_after):
        g = self.game
        pre_units = self._pre_units
        pre_plants = self._pre_plants
        reported_u, reported_p = {}, {}
        for ent in diff.split(";"):
            p = ent.split()
            if len(p) < 2:
                continue
            eid = int(p[0])
            if p[1] == "W":
                uid, x, y, pl, ms, cc, hp, chop = (b36(c) for c in p[2])
                match = [u for u in g.units if u.id == uid]
                if not match:
                    self.note("unit_created_unpredicted", t, ent)
                    u = SimUnit(uid, pl, x, y, ms, cc, hp, chop, [0] * 6)
                    g.units.append(u)
                    g.next_id = max(g.next_id, uid + 1)
                else:
                    u = match[0]
                    if (u.player, u.x, u.y, u.ms, u.cc, u.hp, u.chop) != (pl, x, y, ms, cc, hp, chop):
                        self.note("unit_created_fields", t, (ent, (u.player, u.x, u.y, u.ms, u.cc, u.hp, u.chop)))
                        u.player, u.x, u.y, u.ms, u.cc, u.hp, u.chop = pl, x, y, ms, cc, hp, chop
                self.unit_by_eid[eid] = u
                reported_u[u.id] = {"x", "y", "carry"}
                continue
            if p[1] == "P":
                x, y, ty, stage, cd, health, cd_eff = (b36(c) for c in p[2])
                match = [pl for pl in g.plants if pl.pos == (x, y)]
                pre_match = [pl for pl in pre_plants if pl[0] == (x, y)]
                if not match or pre_match:
                    self.note("plant_created_unpredicted", t, ent)
                    pl = SimPlant(TYPES[ty], x, y, min(stage, 4), health, max(stage - 4, 0), cd)
                    g.plants = [q for q in g.plants if q.pos != (x, y)] + [pl]
                else:
                    pl = match[0]
                    exp = (TYPES[ty], min(stage, 4), max(stage - 4, 0), health, cd)
                    got = (pl.type, pl.size, pl.fruits, pl.health, pl.cooldown)
                    if exp != got:
                        self.note("plant_created_fields", t, (ent, got))
                        pl.type, pl.size, pl.fruits, pl.health, pl.cooldown = exp
                self.plant_by_eid[eid] = pl
                reported_p[id(pl)] = {"health", "stage", "cooldown"}
                continue
            if eid in self.unit_by_eid:
                u = self.unit_by_eid[eid]
                rep = reported_u.setdefault(u.id, set())
                for tok in p[1:]:
                    if tok == "D":
                        self.note("unit_deleted", t, ent)
                    elif tok[0] == "x":
                        v = b36(tok[1:]); rep.add("x")
                        if u.x != v:
                            self.note("unit_x", t, (ent, u.x)); u.x = v
                    elif tok[0] == "y":
                        v = b36(tok[1:]); rep.add("y")
                        if u.y != v:
                            self.note("unit_y", t, (ent, u.y)); u.y = v
                    elif tok[0] in "012345":
                        v = b36(tok[1:]); i = int(tok[0]); rep.add("carry")
                        if u.carry[i] != v:
                            self.note("unit_carry", t, (ent, list(u.carry))); u.carry[i] = v
                    else:
                        self.note("unit_unknown_token", t, ent)
            elif eid in self.plant_by_eid:
                pl = self.plant_by_eid[eid]
                rep = reported_p.setdefault(id(pl), set())
                for tok in p[1:]:
                    if tok == "D":
                        rep.add("dead")
                        if pl in g.plants:
                            self.note("plant_deleted_unpredicted", t, ent); g.plants.remove(pl)
                    elif tok[0] == "h":
                        v = b36(tok[1:]); rep.add("health")
                        if v == 0:
                            rep.add("dead")
                            if pl in g.plants:
                                self.note("plant_death_unpredicted", t, (ent, pl.health)); g.plants.remove(pl)
                        elif pl not in g.plants:
                            self.note("plant_death_overpredicted", t, ent); g.plants.append(pl); pl.health = v
                        elif pl.health != v:
                            self.note("plant_health", t, (ent, pl.health, pl.type, pl.size)); pl.health = v
                    elif tok[0] == "s":
                        v = b36(tok[1:]); rep.add("stage")
                        size, fruits = min(v, 4), max(v - 4, 0)
                        if "dead" in rep:
                            pass
                        elif (pl.size, pl.fruits) != (size, fruits):
                            self.note("plant_stage", t, (ent, pl.size, pl.fruits)); pl.size, pl.fruits = size, fruits
                    elif tok[0] == "c":
                        v = b36(tok[1:]); rep.add("cooldown")
                        if "dead" in rep:
                            pass
                        elif pl.cooldown != v:
                            self.note("plant_cooldown", t, (ent, pl.cooldown, pl.type)); pl.cooldown = v
                    else:
                        self.note("plant_unknown_token", t, ent)
            else:
                self.note("unknown_entity", t, ent)
        # engine changes that the diff did not report
        for u in g.units:
            pre = pre_units.get(u.id)
            if pre is None:
                if u.id not in reported_u:
                    self.note("unit_created_overpredicted", t, u.id)
                continue
            rep = reported_u.get(u.id, set())
            if "x" not in rep and u.x != pre[0]:
                self.note("unit_x_unreported", t, (u.id, pre[0], u.x)); u.x = pre[0]
            if "y" not in rep and u.y != pre[1]:
                self.note("unit_y_unreported", t, (u.id, pre[1], u.y)); u.y = pre[1]
            if "carry" not in rep and u.carry != pre[2]:
                self.note("unit_carry_unreported", t, (u.id, pre[2], u.carry)); u.carry = list(pre[2])
        pre_by_pos = {pp[0]: pp for pp in pre_plants}
        for pl in g.plants:
            pre = pre_by_pos.get(pl.pos)
            rep = reported_p.get(id(pl), set())
            if pre is None:
                if "health" not in rep and "stage" not in rep and "cooldown" not in rep:
                    self.note("plant_created_overpredicted", t, pl.pos)
                continue
            _, psize, pfruits, phealth = pre[0], pre[1], pre[2], pre[3]
            if "health" not in rep and pl.health != phealth:
                self.note("plant_health_unreported", t, (pl.pos, pl.type, phealth, pl.health, psize, pl.size))
            if "stage" not in rep and (pl.size, pl.fruits) != (psize, pfruits):
                grew = (pl.size == psize + 1 and pl.fruits == pfruits == 0) or (pl.size == psize == 4 and pl.fruits == pfruits + 1)
                if grew:
                    self.mismatch["growth_engine_only(expected)"] += 1
                else:
                    self.note("plant_stage_unreported", t, (pl.pos, pl.type, (psize, pfruits), (pl.size, pl.fruits)))
        # inventories
        for pidx in (0, 1):
            if g.inventories[pidx] != inv_after[pidx]:
                self.note("inventory", t, (pidx, g.inventories[pidx], inv_after[pidx]))
                g.inventories[pidx] = list(inv_after[pidx])
        recompute_scores(g)

    def run(self, keep_states=True):
        states = []
        for t in range(1, self.n_turns + 1):
            if keep_states:
                states.append(self.snapshot(t))
            c0, c1 = self.commands(t)
            self._pre_units = {u.id: (u.x, u.y, list(u.carry)) for u in self.game.units}
            self._pre_plants = [(p.pos, p.size, p.fruits, p.health) for p in self.game.plants]
            step(self.game, c0, c1)
            j = view_payload(self.frames[2 * t].get("view"))
            inv_after = [[int(v) for v in ln.split()] for ln in j["inputmodule"].split("\n")]
            self.apply_diff(t, j.get("diff", ""), inv_after)
        if keep_states:
            states.append(self.snapshot(self.n_turns + 1))
        final = [sum(i[:4]) + 4 * i[5] for i in self.game.inventories]
        if [float(x) for x in final] != [float(x) for x in self.replay["scores"]]:
            self.note("final_score", self.n_turns, (final, self.replay["scores"]))
        return states


def reconstruct(game_id, keep_states=True):
    r = Reconstructor(game_id)
    states = r.run(keep_states)
    return r, states


if __name__ == "__main__":
    gid = sys.argv[1]
    r, states = reconstruct(gid)
    print(f"game {gid}: {r.n_turns} turns, agents {[(a['index'], a['codingamer'].get('pseudo'), a['agentId']) for a in r.replay['agents']]}")
    print("mismatch counts:", dict(r.mismatch))
    for k, v in r.examples.items():
        print("  first", k, "->", v)
