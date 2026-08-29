#!/usr/bin/env python3
"""The dataset's Python observation-plane builder, and its drift test.

Why this file exists.  The shards never carry planes (the parent card: ~20 GB of them against
~45 MB of compact states); the planes are built at load time by the Rust
`tf_full_obs_from_state` that the training environment itself uses.  A single implementation of a
104-plane layout is a single point of silent failure: if Rust and the trainer agree on the same
wrong plane, nothing in the programme notices.  So the card asks for a *second* implementation, in
Python, written from the signed table `local_claude_1/nn-bot/OBS-PLANES.md`, and a drift test that
requires the two to be byte-equal on 1,000 states.

Honesty about how independent this is.  The planes below were written from the signed table.  The
table is silent or ambiguous on six points, listed in `PLANES-READ-2026-08-29.md`; those six were
resolved by reading `rust/src/rl_full.rs`, so on those six the drift test is a consistency check
and not a blind reimplementation.  Everything else is written from the table alone.

Two generations of the plan vocabulary live here.

  * `v144-legacy`   — the vocabulary the signed table and the delivered Phase 1 environment
                      (`agent/codex_1@dc420b44`, `TF_FULL_PLAN_SIZE = 144`) are built to.
  * `v400-2026-08-29` — amendment 8 of the parent card, accepted 2026-08-29 18:2xZ: 400 plans and
                      the widened talent scales.  The dataset is built to this one.

The drift test refuses to compare across generations: an environment reporting 144 plans can only
be compared in `v144-legacy`, because a v400 plan index is not even representable in its ABI.

Usage:

    # the table's own arithmetic, both generations, no library needed
    python3 local_claude_1/nn-bot/build_planes.py --self-test

    # the drift test against the compiled environment
    python3 local_claude_1/nn-bot/build_planes.py --drift \
        --library /path/to/libtroll_farm.so \
        --replays local_claude_1/nn-bot/replays-slice-10 --states 1000
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import random
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# --- the tensor -------------------------------------------------------------------------------

CHANNELS = 104
GRID_H = 11
GRID_W = 22
CELLS = GRID_H * GRID_W                                         # 242
OBS_SIZE = CHANNELS * CELLS                                     # 25,168

ITEM_NAMES = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = range(6)
FRUIT_NAMES = ITEM_NAMES[:4]
WOOD_POINTS = 4
DIST_CLIP = 40
NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class Vocabulary:
    """A plan vocabulary and the plane scales that travel with it."""

    def __init__(self, name, speeds, carries, harvests, chops, scales):
        self.name = name
        self.speeds, self.carries = speeds, carries
        self.harvests, self.chops = harvests, chops
        self.size = speeds * carries * harvests * chops
        self.scales = scales

    def index(self, speed, carry, harvest, chop):
        """The flat plan index of a talent tuple, or None if outside the vocabulary."""
        if not (1 <= speed <= self.speeds and 1 <= carry <= self.carries):
            return None
        if not (0 <= harvest < self.harvests and 0 <= chop < self.chops):
            return None
        rest = (speed - 1) * self.carries + (carry - 1)
        return (rest * self.harvests + harvest) * self.chops + chop

    def decode(self, index):
        """The talent tuple of a flat index.  Index 0 is 'train nothing' -> (0, 0, 0, 0)."""
        if not 0 <= index < self.size:
            raise ValueError(f"plan index {index} outside {self.name}")
        if index == 0:
            return (0, 0, 0, 0)
        chop = index % self.chops
        rest = index // self.chops
        harvest = rest % self.harvests
        rest //= self.harvests
        carry = rest % self.carries + 1
        speed = rest // self.carries + 1
        return (speed, carry, harvest, chop)


def _scales(speed_s, carry_s, harvest_s, chop_s, cargo_s, carried_s,
            max_s, sum_s, target_s, cost_s):
    """The per-plane scale table; only the planes whose scale a generation moves are listed."""
    table = {}
    for base in (18, 28):                                       # own / opponent troll talents
        table[base + 0], table[base + 1] = speed_s, carry_s
        table[base + 2], table[base + 3] = harvest_s, chop_s
        for kind in range(6):                                   # cargo planes 22-27 / 32-37
            table[base + 4 + kind] = cargo_s
    for base in (93, 95):                                       # carried total / free capacity
        table[base], table[base + 1] = carried_s, carried_s
    for offset in range(4):
        table[72 + offset] = max_s[offset]                      # own maxima
        table[80 + offset] = max_s[offset]                      # opponent maxima
        table[76 + offset] = sum_s[offset]                      # own sums
        table[84 + offset] = sum_s[offset]                      # opponent sums
        table[60 + offset] = target_s[offset]                   # the train target
        table[64 + offset] = cost_s                             # effective train cost
        table[68 + offset] = cost_s                             # train deficit
    return table


V144 = Vocabulary(
    "v144-legacy", speeds=3, carries=4, harvests=3, chops=4,
    scales=_scales(speed_s=3, carry_s=4, harvest_s=3, chop_s=3, cargo_s=4, carried_s=4,
                   max_s=(3, 4, 3, 3), sum_s=(36, 48, 36, 36),
                   target_s=(3, 4, 2, 3), cost_s=32),
)

# Amendment 8, second completion: every talent-bearing plane widens with the vocabulary.
V400 = Vocabulary(
    "v400-2026-08-29", speeds=4, carries=5, harvests=4, chops=5,
    scales=_scales(speed_s=4, carry_s=5, harvest_s=3, chop_s=4, cargo_s=5, carried_s=5,
                   max_s=(4, 5, 3, 4), sum_s=(48, 60, 36, 48),
                   target_s=(4, 5, 3, 4), cost_s=48),
)

GENERATIONS = {V144.name: V144, V400.name: V400}
DATASET_GENERATION = V400.name                                  # what build_dataset.py writes


# --- the arithmetic of a plane ----------------------------------------------------------------

def quant(value, scale):
    """OBS-PLANES.md: q(v, S) = floor(255 * clamp(v, 0, S) / S + 0.5), non-negative rounding."""
    if scale <= 0:
        return 0
    value = min(max(value, 0), scale)
    return int(255.0 * value / scale + 0.5)


def view_cell(cell, seat, w, h):
    """Seat 1 is the board rotated 180 degrees inside the real w by h, not inside the padding."""
    if seat == 0:
        return cell
    return (w - 1 - cell[0], h - 1 - cell[1])


def _set(obs, plane, cell, value):
    x, y = cell
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        obs[plane * CELLS + y * GRID_W + x] = value


def _broadcast(obs, plane, value, w, h):
    """Scalar planes cover the valid board only; padding stays zero."""
    for y in range(h):
        for x in range(w):
            _set(obs, plane, (x, y), value)


def bfs(walkable, sources):
    """Steps over walkable cells.  Each source is seeded at 0 whether or not it is walkable."""
    dist, queue = {}, deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        x, y = queue.popleft()
        step = dist[(x, y)] + 1
        for dx, dy in NEIGHBOURS:
            nxt = (x + dx, y + dy)
            if nxt in walkable and nxt not in dist:
                dist[nxt] = step
                queue.append(nxt)
    return dist


def _distance_plane(obs, plane, sources, walkable, seat, w, h):
    dist = bfs(walkable, sources)
    for y in range(h):
        for x in range(w):
            value = min(max(dist.get((x, y), DIST_CLIP), 0), DIST_CLIP)
            _set(obs, plane, view_cell((x, y), seat, w, h), quant(value, DIST_CLIP))


def training_cost(troll_count, talents):
    """PLUM <- speed, LEMON <- carry, APPLE <- harvest, IRON <- chop; each cost = n + stat^2."""
    speed, carry, harvest, chop = talents
    cost = [0] * 6
    cost[PLUM] = troll_count + speed * speed
    cost[LEMON] = troll_count + carry * carry
    cost[APPLE] = troll_count + harvest * harvest
    cost[IRON] = troll_count + chop * chop
    return cost


# --- the map ----------------------------------------------------------------------------------

class Board:
    """The terrain sets the map rows imply.  '.' walkable, '#' rock, '+' iron, '~' water."""

    def __init__(self, rows):
        self.h = len(rows)
        self.w = len(rows[0]) if rows else 0
        self.walkable, self.iron, self.water = set(), set(), set()
        self.shacks = [None, None]
        for y, row in enumerate(rows):
            if len(row) != self.w:
                raise ValueError("ragged map rows")
            for x, char in enumerate(row):
                cell = (x, y)
                if char == "0":
                    self.shacks[0] = cell
                elif char == "1":
                    self.shacks[1] = cell
                elif char == "+":
                    self.iron.add(cell)
                elif char == "~":
                    self.water.add(cell)
                elif char == "#":
                    pass
                else:
                    self.walkable.add(cell)
        if self.shacks[0] is None or self.shacks[1] is None:
            raise ValueError("a map carries exactly one shack for each player")


def _next_cell(walkable, start, target, speed):
    """Where a MOVE ends, by the referee's rule as `sim/engine.py` states it.

    Of the cells within `speed` walking steps of the troll, take the one whose walking distance to
    the target is smallest; ties go to the lexicographically smallest cell (the referee breaks them
    at random and the simulator settles them this way).  An unreachable target is replaced by the
    reachable cells nearest it in Manhattan distance.  The troll's own cell is seeded at zero
    whether or not it is walkable, so a troll standing on its shack can leave it.
    """
    source = bfs(walkable, [start])
    if target in source and source[target] <= speed:
        return target
    if target not in source:
        best = min(abs(target[0] - c[0]) + abs(target[1] - c[1]) for c in source)
        goals = [c for c in source
                 if abs(target[0] - c[0]) + abs(target[1] - c[1]) == best]
        field = bfs(walkable, goals)
    else:
        field = bfs(walkable, [target])
    in_range = [c for c, d in source.items() if d <= speed and c in field]
    if not in_range:
        return start
    best = min(field[c] for c in in_range)
    return min(c for c in in_range if field[c] == best)


# --- the observation --------------------------------------------------------------------------

def observation(state, seat, active_troll_id, phase, plan_index,
                prior_target_trained=False, generation=DATASET_GENERATION):
    """The 104-plane u8 tensor of one mini-step, flattened channel-major.

    `state` is the compact per-turn state the environment's own `tf_full_obs_from_state` reads:
    `w`, `h`, `rows`, `turn`, `inv`, `units`, `plants`, and an optional `staged_actions`.
    `phase` is 0 for the plan mini-step and 1 for a troll mini-step.
    """
    vocab = GENERATIONS[generation]
    if seat not in (0, 1) or phase not in (0, 1):
        raise ValueError("seat is 0 or 1 and phase is 0 or 1")
    if not 0 <= plan_index < vocab.size:
        raise ValueError(f"plan index {plan_index} outside {vocab.name}")

    board = Board(state["rows"])
    w, h = board.w, board.h
    if (w, h) != (state["w"], state["h"]):
        raise ValueError("map rows do not match the declared width and height")
    if w > GRID_W or h > GRID_H:
        raise ValueError("map larger than the padded tensor")
    obs = bytearray(OBS_SIZE)
    scales = vocab.scales

    units = [dict(unit) for unit in state["units"]]
    shown = _stage(units, state.get("staged_actions", []), board, seat, w, h)

    # planes 0-6, 40, 41: the terrain the map row is authoritative for
    for y in range(h):
        for x in range(w):
            absolute = (x, y)
            cell = view_cell(absolute, seat, w, h)
            _set(obs, 0, cell, 255)
            if absolute in board.walkable:
                _set(obs, 1, cell, 255)
            elif absolute in board.water:
                _set(obs, 2, cell, 255)
            elif absolute in board.iron:
                _set(obs, 4, cell, 255)
            elif absolute not in board.shacks:
                _set(obs, 3, cell, 255)
            if absolute == board.shacks[seat]:
                _set(obs, 5, cell, 255)
            if absolute == board.shacks[1 - seat]:
                _set(obs, 6, cell, 255)
            if any(abs(ix - x) + abs(iy - y) == 1 for ix, iy in board.iron):
                _set(obs, 40, cell, 255)
            if any(abs(wx - x) + abs(wy - y) == 1 for wx, wy in board.water):
                _set(obs, 41, cell, 255)

    # planes 7-15: the living trees
    for plant in state["plants"]:
        if plant["health"] <= 0:
            continue
        cell = view_cell((plant["x"], plant["y"]), seat, w, h)
        _set(obs, 7, cell, 255)
        if plant["type"] in FRUIT_NAMES:
            _set(obs, 8 + FRUIT_NAMES.index(plant["type"]), cell, 255)
        _set(obs, 12, cell, quant(plant["size"], 4))
        _set(obs, 13, cell, quant(plant["health"], 20))
        _set(obs, 14, cell, quant(plant["fruits"], 3))
        _set(obs, 15, cell, quant(plant["cooldown"], 9))

    # planes 16-37, 93-96, 99-103: the trolls, at their staged cells
    for unit in shown:
        own = unit["player"] == seat
        cell = view_cell((unit["x"], unit["y"]), seat, w, h)
        base = 18 if own else 28
        _set(obs, 16 if own else 17, cell, 255)
        _set(obs, base + 0, cell, quant(unit["ms"], scales[base + 0]))
        _set(obs, base + 1, cell, quant(unit["cc"], scales[base + 1]))
        _set(obs, base + 2, cell, quant(unit["hp"], scales[base + 2]))
        _set(obs, base + 3, cell, quant(unit["chop"], scales[base + 3]))
        for kind in range(6):
            _set(obs, base + 4 + kind, cell,
                 quant(unit["carry"][kind], scales[base + 4 + kind]))
        total = sum(unit["carry"])
        free = unit["cc"] - total
        _set(obs, 93 if own else 95, cell, quant(total, scales[93 if own else 95]))
        _set(obs, 94 if own else 96, cell, quant(free, scales[94 if own else 96]))
        if total == unit["cc"]:
            _set(obs, 100 if own else 102, cell, 255)
            if not any(unit["carry"][kind] for kind in (PLUM, LEMON, APPLE, BANANA)):
                _set(obs, 101 if own else 103, cell, 255)
        if own and phase == 1 and unit["id"] == active_troll_id:
            _set(obs, 99, cell, 255)

    # planes 38, 39: walking distance to each shack's doors, the shack cell itself zero
    for plane, shack in ((38, board.shacks[seat]), (39, board.shacks[1 - seat])):
        doors = [cell for cell in board.walkable
                 if abs(cell[0] - shack[0]) + abs(cell[1] - shack[1]) == 1]
        _distance_plane(obs, plane, doors, board.walkable, seat, w, h)
        _set(obs, plane, view_cell(shack, seat, w, h), 0)

    # planes 88-92: distance to the nearest living tree of each kind, and to a mining cell
    for kind, name in enumerate(FRUIT_NAMES):
        sources = [(p["x"], p["y"]) for p in state["plants"]
                   if p["health"] > 0 and p["type"] == name]
        _distance_plane(obs, 88 + kind, sources, board.walkable, seat, w, h)
    mines = [cell for cell in board.walkable
             if any(abs(cell[0] - ix) + abs(cell[1] - iy) == 1 for ix, iy in board.iron)]
    _distance_plane(obs, 92, mines, board.walkable, seat, w, h)

    # planes 42-58: the turn, the two banks, the two scores, the two troll counts
    _broadcast(obs, 42, quant(state["turn"], 300), w, h)
    inventories = state["inv"]
    for kind in range(6):
        scale = 128 if kind == WOOD else 64
        _broadcast(obs, 43 + kind, quant(inventories[seat][kind], scale), w, h)
        _broadcast(obs, 49 + kind, quant(inventories[1 - seat][kind], scale), w, h)
    scores = [sum(inv[PLUM:BANANA + 1]) + WOOD_POINTS * inv[WOOD] for inv in inventories]
    _broadcast(obs, 55, quant(scores[seat], 1024), w, h)
    _broadcast(obs, 56, quant(scores[1 - seat], 1024), w, h)
    ours = [unit for unit in units if unit["player"] == seat]
    theirs = [unit for unit in units if unit["player"] != seat]
    _broadcast(obs, 57, quant(len(ours), 12), w, h)
    _broadcast(obs, 58, quant(len(theirs), 12), w, h)

    # planes 59-71: the train target, its effective cost and its deficit against our bank
    if plan_index != 0:
        target = vocab.decode(plan_index)
        _broadcast(obs, 59, 255, w, h)
        for offset in range(4):
            _broadcast(obs, 60 + offset, quant(target[offset], scales[60 + offset]), w, h)
        cost = training_cost(len(ours), target)
        if not board.iron:                          # the referee charges no iron on such a map
            cost[IRON] = 0
        for offset, kind in enumerate((PLUM, LEMON, APPLE, IRON)):
            _broadcast(obs, 64 + offset, quant(cost[kind], scales[64 + offset]), w, h)
            deficit = max(cost[kind] - inventories[seat][kind], 0)
            _broadcast(obs, 68 + offset, quant(deficit, scales[68 + offset]), w, h)

    # planes 72-87: the maxima and the sums of both sides' talents
    for offset, key in enumerate(("ms", "cc", "hp", "chop")):
        for side, (max_plane, sum_plane) in ((ours, (72, 76)), (theirs, (80, 84))):
            values = [unit[key] for unit in side]
            _broadcast(obs, max_plane + offset,
                       quant(max(values) if values else 0, scales[max_plane + offset]), w, h)
            _broadcast(obs, sum_plane + offset,
                       quant(sum(values), scales[sum_plane + offset]), w, h)

    # planes 97, 98: the plan is decided; the previous turn's target was trained
    if phase == 1:
        _broadcast(obs, 97, 255, w, h)
    if phase == 0 and prior_target_trained:
        _broadcast(obs, 98, 255, w, h)
    return bytes(obs)


def _stage(units, staged, board, seat, w, h):
    """Earlier own trolls are drawn at the end cell their already-chosen command implies."""
    shown = [dict(unit) for unit in units]
    by_id = {unit["id"]: unit for unit in shown}
    for action in staged:
        index = max(int(action["action_index"]), 0)
        if index >= 13 * CELLS or index // CELLS != 0:          # only MOVE stages a new cell
            continue
        cell = index % CELLS
        target = view_cell((cell % GRID_W, cell // GRID_W), seat, w, h)
        unit = by_id.get(action["troll_id"])
        if unit is None or unit["player"] != seat:
            continue
        unit["x"], unit["y"] = _next_cell(
            board.walkable, (unit["x"], unit["y"]), target, unit["ms"])
    return shown


# --- the self-test ----------------------------------------------------------------------------

def self_test():
    """The table's own arithmetic, on both generations.  No compiled library needed."""
    failures = []

    def check(name, condition):
        if not condition:
            failures.append(name)

    # the quantizer is the table's, not NumPy's ties-to-even
    check("q(0,S)=0", quant(0, 40) == 0)
    check("q(S,S)=255", quant(40, 40) == 255 and quant(3, 3) == 255)
    check("q clamps above", quant(99, 4) == 255)
    check("q clamps below", quant(-3, 4) == 0)
    check("q rounds a half up", quant(1, 2) == 128)             # 127.5 -> 128, not 128 by parity
    check("q(2,4)=128", quant(2, 4) == 128)

    for vocab in (V144, V400):
        size = vocab.speeds * vocab.carries * vocab.harvests * vocab.chops
        check(f"{vocab.name} size", vocab.size == size)
        seen = set()
        for index in range(vocab.size):
            talents = vocab.decode(index)
            if index == 0:
                check(f"{vocab.name} entry 0 is train nothing", talents == (0, 0, 0, 0))
                continue
            check(f"{vocab.name} bijection at {index}", vocab.index(*talents) == index)
            seen.add(talents)
        check(f"{vocab.name} covers every tuple but one", len(seen) == vocab.size - 1)
        check(f"{vocab.name} rejects out of range", vocab.index(9, 1, 0, 1) is None)

    check("v144 index of (2,2,0,2)", V144.index(2, 2, 0, 2) == ((1 * 4 + 1) * 3 + 0) * 4 + 2)
    check("v400 index of (2,2,0,2)", V400.index(2, 2, 0, 2) == ((1 * 5 + 1) * 4 + 0) * 5 + 2)
    check("v400 holds speed 4", V400.index(4, 1, 0, 1) is not None)
    check("v144 refuses speed 4", V144.index(4, 1, 0, 1) is None)
    check("v400 holds carry 5", V400.index(1, 5, 0, 1) is not None)
    check("v400 holds harvest 3", V400.index(1, 3, 3, 0) is not None)
    check("v400 holds chop 4", V400.index(1, 1, 0, 4) is not None)

    # the widened scales saturate where the vocabulary now reaches, and the old ones did not
    check("v144 speed plane saturates at 3", V144.scales[18] == 3)
    check("v400 speed plane saturates at 4", V400.scales[18] == 4)
    check("v400 carry plane saturates at 5", V400.scales[19] == 5)
    check("v400 chop plane saturates at 4", V400.scales[21] == 4)
    check("v400 cargo plane saturates at 5", V400.scales[27] == 5)
    check("v400 cost planes S=48", V400.scales[64] == 48 and V400.scales[71] == 48)
    check("v400 sums", (V400.scales[76], V400.scales[77], V400.scales[78], V400.scales[79])
          == (48, 60, 36, 48))
    check("harvest planes unmoved", V144.scales[20] == 3 and V400.scales[20] == 3)

    # a tiny board: padding stays zero, the seat rotation is a point symmetry, planes are exact
    rows = ["0.+.", ".~..", "...1"]
    state = {
        "w": 4, "h": 3, "rows": rows, "turn": 7,
        "inv": [[1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0]],
        "units": [
            {"id": 0, "player": 0, "x": 1, "y": 0, "ms": 2, "cc": 3, "hp": 1, "chop": 2,
             "carry": [0, 0, 0, 0, 2, 1]},
            {"id": 1, "player": 1, "x": 2, "y": 2, "ms": 1, "cc": 1, "hp": 0, "chop": 1,
             "carry": [0, 0, 0, 0, 0, 0]},
        ],
        "plants": [{"type": "LEMON", "x": 3, "y": 1, "size": 2, "health": 8, "fruits": 1,
                    "cooldown": 3}],
    }
    obs0 = observation(state, 0, 0, 1, 0)
    check("tensor size", len(obs0) == OBS_SIZE)
    check("padding is zero", all(
        obs0[plane * CELLS + y * GRID_W + x] == 0
        for plane in range(CHANNELS) for y in range(GRID_H) for x in range(GRID_W)
        if x >= 4 or y >= 3))
    check("valid-cell plane", all(obs0[0 * CELLS + y * GRID_W + x] == 255
                                  for y in range(3) for x in range(4)))
    check("own shack", obs0[5 * CELLS + 0] == 255)
    check("opponent shack", obs0[6 * CELLS + 2 * GRID_W + 3] == 255)
    check("shack is not rock", obs0[3 * CELLS + 0] == 0 and obs0[1 * CELLS + 0] == 0)
    check("iron cell", obs0[4 * CELLS + 2] == 255)
    check("water cell", obs0[2 * CELLS + 1 * GRID_W + 1] == 255)
    check("adjacent to iron", obs0[40 * CELLS + 1] == 255 and obs0[40 * CELLS + 0] == 0)
    check("the tree", obs0[7 * CELLS + 1 * GRID_W + 3] == 255
          and obs0[9 * CELLS + 1 * GRID_W + 3] == 255
          and obs0[13 * CELLS + 1 * GRID_W + 3] == quant(8, 20))
    check("the active troll", obs0[99 * CELLS + 1] == 255)
    check("own bank wood", obs0[48 * CELLS + 0] == quant(6, 128))
    check("own score", obs0[55 * CELLS + 0] == quant(1 + 2 + 3 + 4 + 4 * 6, 1024))
    check("own carried total", obs0[93 * CELLS + 1] == quant(3, V400.scales[93]))
    check("own troll is full", obs0[100 * CELLS + 1] == 255)
    check("full of iron and wood only", obs0[101 * CELLS + 1] == 255)
    check("plan phase has no active troll", all(
        v == 0 for v in observation(state, 0, -1, 0, 0)[99 * CELLS:100 * CELLS]))
    check("phase 1 latches plane 97", obs0[97 * CELLS + 0] == 255)
    check("plane 97 is zero at the plan phase",
          observation(state, 0, -1, 0, 0)[97 * CELLS + 0] == 0)
    check("plane 98 latches only at the plan phase",
          observation(state, 0, -1, 0, 0, True)[98 * CELLS + 0] == 255
          and observation(state, 0, 0, 1, 0, True)[98 * CELLS + 0] == 0)

    # the required equality check 1: seat 1 is seat 0 rotated, with the players relabelled
    obs1 = observation(state, 1, 1, 1, 0)
    rotated_ok = True
    for plane in (0, 1, 2, 3, 4, 7, 12, 13, 42):     # the map, the trees, the turn: seat-blind
        for y in range(3):
            for x in range(4):
                left = obs0[plane * CELLS + y * GRID_W + x]
                right = obs1[plane * CELLS + (2 - y) * GRID_W + (3 - x)]
                if left != right:
                    rotated_ok = False
    check("seat 1 is the rotated view", rotated_ok)
    check("own and opponent swap with the seat",                 # seat 1's shack is at (3,2),
          obs1[5 * CELLS + 0] == 255                              # which rotates onto (0,0)
          and obs1[6 * CELLS + 2 * GRID_W + 3] == 255
          and obs1[55 * CELLS + 0] == obs0[56 * CELLS + 0])

    # a nonzero plan fills 59-71, and index 0 zeroes them
    planned = observation(state, 0, 0, 1, V400.index(2, 2, 0, 2), generation=V400.name)
    check("plan present", planned[59 * CELLS + 0] == 255)
    check("plan speed", planned[60 * CELLS + 0] == quant(2, V400.scales[60]))
    check("plan cost plum", planned[64 * CELLS + 0] == quant(1 + 4, 48))
    check("plan deficit plum", planned[68 * CELLS + 0] == quant(max(5 - 1, 0), 48))
    check("iron charged where iron exists", planned[67 * CELLS + 0] == quant(1 + 4, 48))
    check("train nothing zeroes 59-71", all(
        obs0[plane * CELLS + 0] == 0 for plane in range(59, 72)))

    # an iron-free map waives the iron cost and its deficit
    ironless = dict(state, rows=["0...", ".~..", "...1"])
    free = observation(ironless, 0, 0, 1, V400.index(2, 2, 0, 2), generation=V400.name)
    check("iron waived on an iron-free map",
          free[67 * CELLS + 0] == 0 and free[71 * CELLS + 0] == 0)

    # saturation at the old and the new maxima, both seats (amendment 8's requirement)
    big = dict(state, units=[
        dict(state["units"][0], ms=4, cc=5, hp=3, chop=4, carry=[0, 0, 0, 0, 5, 0]),
        state["units"][1]])
    for seat in (0, 1):
        wide = observation(big, seat, 0, 1, 0, generation=V400.name)
        narrow_base = 18 if seat == 0 else 28
        cell = view_cell((1, 0), seat, 4, 3)
        at = cell[1] * GRID_W + cell[0]
        check(f"v400 speed 4 saturates seat {seat}",
              wide[narrow_base * CELLS + at] == 255)
        check(f"v400 carry 5 saturates seat {seat}",
              wide[(narrow_base + 1) * CELLS + at] == 255)
        check(f"v400 chop 4 saturates seat {seat}",
              wide[(narrow_base + 3) * CELLS + at] == 255)
        check(f"v400 cargo 5 saturates seat {seat}",
              wide[(narrow_base + 4 + IRON) * CELLS + at] == 255)
        legacy = observation(dict(state), seat, 0, 1, 0, generation=V144.name)
        legacy_cell = view_cell((1, 0), seat, 4, 3)
        legacy_at = legacy_cell[1] * GRID_W + legacy_cell[0]
        check(f"v144 speed 2 of 3 seat {seat}",
              legacy[narrow_base * CELLS + legacy_at] == quant(2, 3))

    # the distances: a door is 1, the shack itself 0, the unreachable clipped
    check("the shack cell is zero", obs0[38 * CELLS + 0] == 0)
    check("a door is a source, so zero", obs0[38 * CELLS + 1] == 0)
    check("one step past a door is one", obs0[38 * CELLS + 2 * GRID_W + 0] == quant(1, 40))
    check("two steps past a door is two", obs0[38 * CELLS + 2 * GRID_W + 1] == quant(2, 40))
    check("water is unreachable, so clipped", obs0[38 * CELLS + 1 * GRID_W + 1] == 255)
    check("no banana tree anywhere is the clip",
          obs0[91 * CELLS + 0] == quant(40, 40) == 255)

    if failures:
        for name in failures:
            print(f"FAIL {name}")
    print(f"self-test: {'PASS' if not failures else 'FAIL'} "
          f"({len(failures)} failures)")
    return 0 if not failures else 1


# --- the drift test ---------------------------------------------------------------------------

class Environment:
    """The compiled `tf_full_obs_from_state`, loaded through ctypes."""

    def __init__(self, library):
        self.lib = ctypes.CDLL(str(library))
        self.lib.tf_full_obs_from_state.restype = ctypes.c_int
        self.lib.tf_full_obs_from_state.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_ubyte,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte)]
        self.plan_size = None
        for symbol in ("tf_full_plan_size", "tf_full_plan_action_size"):
            if hasattr(self.lib, symbol):
                fn = getattr(self.lib, symbol)
                fn.restype = ctypes.c_size_t
                fn.argtypes = []
                self.plan_size = int(fn())
                break

    def observation(self, state, seat, active_troll_id, phase, plan_index,
                    prior_target_trained=False):
        payload = json.dumps(state).encode()
        buffer = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        obs = (ctypes.c_ubyte * OBS_SIZE)()
        code = self.lib.tf_full_obs_from_state(
            buffer, len(payload), seat, active_troll_id, phase, plan_index,
            1 if prior_target_trained else 0, obs, None, None)
        if code != 0:
            raise RuntimeError(f"tf_full_obs_from_state returned {code}")
        return bytes(obs)


def _states_from_replays(replay_dir, wanted, seed):
    """Compact per-turn states with their map, taken from the exact reconstruction."""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "local_claude_1" / "reconstructions" / "fits"))
    import reconstruct as rc                                    # noqa: PLC0415

    rc.RAW = Path(replay_dir)
    games = sorted(int(p.stem) for p in Path(replay_dir).glob("*.json")
                   if p.stem.isdigit())
    rng = random.Random(seed)
    out = []
    for game in games:
        recon, states = rc.reconstruct(game)
        rows, w, h = recon.map["rows"], recon.map["w"], recon.map["h"]
        for state in states:
            out.append(dict(state, w=w, h=h, rows=rows))
        if len(out) >= wanted * 3:
            break
    rng.shuffle(out)
    return out[:wanted]


def drift(library, replay_dir, wanted, seed, generation, staged_share=0.5):
    env = Environment(library)
    if env.plan_size is not None and env.plan_size != GENERATIONS[generation].size:
        print(f"REFUSED: the library reports {env.plan_size} plans, "
              f"{generation} has {GENERATIONS[generation].size}; "
              f"a drift test across generations proves nothing")
        return 2
    vocab = GENERATIONS[generation]
    states = _states_from_replays(replay_dir, wanted, seed)
    if len(states) < wanted:
        print(f"only {len(states)} states available, wanted {wanted}")
    rng = random.Random(seed ^ 0x5eed)
    checked, mismatched, digest = 0, [], hashlib.sha256()
    staged_states = 0
    for state in states:
        seat = rng.randrange(2)
        own = sorted(u["id"] for u in state["units"] if u["player"] == seat)
        phase = 0 if (not own or rng.random() < 0.25) else 1
        active = -1 if phase == 0 else rng.choice(own)
        plan_index = 0 if rng.random() < 0.3 else rng.randrange(vocab.size)
        prior = rng.random() < 0.2
        # Required check 2 names the staged earlier-troll commands explicitly, so a share of the
        # states stages a MOVE for an own troll that is not the active one.
        earlier = [troll for troll in own if troll != active]
        if phase == 1 and earlier and rng.random() < staged_share:
            cell = rng.randrange(CELLS)
            state = dict(state, staged_actions=[
                {"troll_id": rng.choice(earlier), "action_index": cell}])
            staged_states += 1
        mine = observation(state, seat, active, phase, plan_index, prior, generation)
        theirs = env.observation(state, seat, active, phase, plan_index, prior)
        checked += 1
        digest.update(theirs)
        if mine != theirs:
            planes = sorted({index // CELLS for index in range(OBS_SIZE)
                             if mine[index] != theirs[index]})
            mismatched.append({"turn": state["turn"], "seat": seat, "phase": phase,
                               "plan_index": plan_index, "planes": planes[:12],
                               "differing_bytes": sum(1 for index in range(OBS_SIZE)
                                                      if mine[index] != theirs[index])})
    print(f"drift test, generation {generation}: {checked - len(mismatched)}/{checked} "
          f"states byte-identical ({staged_states} of them with a staged earlier troll)")
    print(f"environment observation digest sha256 {digest.hexdigest()}")
    if mismatched:
        counts = {}
        for row in mismatched:
            for plane in row["planes"]:
                counts[plane] = counts.get(plane, 0) + 1
        print(f"{len(mismatched)} states differ; planes by frequency: "
              f"{sorted(counts.items(), key=lambda kv: -kv[1])[:15]}")
        for row in mismatched[:5]:
            print("  ", row)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--drift", action="store_true")
    parser.add_argument("--library")
    parser.add_argument("--replays", default=str(HERE / "replays-slice-10"))
    parser.add_argument("--states", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--staged-share", type=float, default=0.5,
                        help="the share of troll mini-steps that stage an earlier troll's MOVE")
    parser.add_argument("--generation", default=None,
                        help="v144-legacy or v400-2026-08-29; default: what the library reports")
    args = parser.parse_args()

    status = 0
    if args.self_test or not args.drift:
        status |= self_test()
    if args.drift:
        if not args.library:
            parser.error("--drift needs --library")
        generation = args.generation
        if generation is None:
            env = Environment(args.library)
            generation = next((name for name, vocab in GENERATIONS.items()
                               if vocab.size == env.plan_size), DATASET_GENERATION)
        status |= drift(args.library, args.replays, args.states, args.seed,
                        generation, args.staged_share)
    return status


if __name__ == "__main__":
    sys.exit(main())
