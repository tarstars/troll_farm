"""Replay a schedule (the per-turn command lines the model produced) through the referee mirror
`sim/engine.py`, the opponent idle on its shack, and compare the two worlds after every turn.

Returns the first disagreement (turn and what differs) or None.  The completion turns (TRAIN
events) are read off the referee's world, never the model's."""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from sim.state import GameState, SimUnit, SimPlant   # noqa: E402
from sim.engine import step                          # noqa: E402


def referee_state(item, seat=0):
    rec = item["rec"]
    rows = rec["rows"]
    walk, iron, water = set(), set(), set()
    shacks = [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                shacks[0] = (x, y)
            elif ch == "1":
                shacks[1] = (x, y)
            elif ch == "+":
                iron.add((x, y))
            elif ch == "~":
                water.add((x, y))
            elif ch == ".":
                walk.add((x, y))
    units = [SimUnit(p, p, shacks[p][0], shacks[p][1], 1, 1, 1, 1, [0] * 6) for p in (0, 1)]
    plants = [SimPlant(t["type"], t["x"], t["y"], t["size"], t["health"], t["fruits"], t["cur_cd"])
              for t in rec["trees0"]]
    draw = list(item["draw"])
    return GameState(width=len(rows[0]), height=len(rows), walkable=walk, shacks=shacks,
                     inventories=[list(draw), list(draw)], units=units, plants=plants,
                     scores=[0, 0], turn=1, next_id=2, iron=iron, water=water)


def snapshot_model(s):
    units = sorted((u.id, u.x, u.y, u.ms, u.cc, u.hp, u.chop, tuple(u.carry)) for u in s.units)
    plants = sorted((c, p.kind, p.size, p.health, p.fruits, p.cd) for c, p in s.plants.items())
    return (tuple(s.inv), tuple(units), tuple(plants))


def snapshot_referee(g, seat):
    units = sorted((u.id, u.x, u.y, u.ms, u.cc, u.hp, u.chop, tuple(u.carry)) for u in g.units if u.player == seat)
    plants = sorted((p.pos, p.type, p.size, p.health, p.fruits, p.cooldown) for p in g.plants)
    return (tuple(g.inventories[seat]), tuple(units), tuple(plants))


def replay(item, log, seat=0, model_states=None):
    """`log`: list of command lines per turn (each a list of strings).  `model_states`: optional
    list of the model's snapshots after each turn (same length) for a turn-by-turn diff.
    Returns dict(ok, turn, detail, trains, referee_final)."""
    g = referee_state(item, seat)
    trains = []
    for t, line in enumerate(log, start=1):
        before = {u.id for u in g.units}
        step(g, line, []) if seat == 0 else step(g, [], line)
        for u in g.units:
            if u.id not in before and u.player == seat:
                trains.append((t, (u.ms, u.cc, u.hp, u.chop), u.id))
        if model_states is not None:
            ref = snapshot_referee(g, seat)
            if ref != model_states[t - 1]:
                return {"ok": False, "turn": t, "detail": _diff(model_states[t - 1], ref), "trains": trains}
    return {"ok": True, "turn": len(log), "detail": None, "trains": trains,
            "score": g.scores[seat], "inv": list(g.inventories[seat])}


def _diff(a, b):
    out = []
    if a[0] != b[0]:
        out.append(("inventory", a[0], b[0]))
    if a[1] != b[1]:
        out.append(("units", a[1], b[1]))
    if a[2] != b[2]:
        for x, y in zip(a[2], b[2]):
            if x != y:
                out.append(("plant", x, y))
                break
        else:
            out.append(("plants", len(a[2]), len(b[2])))
    return out
