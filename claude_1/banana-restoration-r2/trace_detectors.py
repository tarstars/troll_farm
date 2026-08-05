#!/usr/bin/env python3
"""Deterministic offline trace detectors D-1..D-9 for the banana restoration (r2).

Implements the "Detector catalog (acceptance check 5)" of
invariant-spec-2026-08-04.md over recorded traces:

  trace = transcript (exact stdin stream: static map, then one block per turn)
        + command stream (one line per turn; commands joined by ';').

Protocol mirrored from the parent bot's `mod protocol` (read_static_map /
read_turn) and `game::rules` / `game::nav`:

  static map : "W H" header, then H rows; '0'/'1' = shacks, '.' = walkable,
               '+' = iron, '~' = water, anything else = obstacle.
  turn block : 2 inventory lines (6 ints: PLUM LEMON APPLE BANANA IRON WOOD),
               plant count, plant lines "KIND x y size health fruits cooldown",
               unit count, unit lines
               "id player x y move_speed carry_cap harvest_pow chop_pow c0..c5".
  own side   : player == 0 (the transcript is the bot's own view; own tent is
               shacks[0], own inventory inventories[0]).
  commands   : MOVE id x y | HARVEST id | CHOP id | DROP id | MINE id |
               PICK id ITEM | PLANT id KIND | TRAIN ms cc hp cp | WAIT | MSG ...
               HARVEST/CHOP/PLANT/PICK/DROP act on the unit's own cell
               (the parent only emits CHOP/HARVEST when plant.cell == unit.cell,
               and banks by DROP while standing on a door cell).

Everything is pure Python 3 stdlib and deterministic (no randomness, no time).

Ambiguity resolutions (strictest implementable reading; see also each
detector's docstring):

  A1. D-1 is evaluated for OWN units only: progress-event attribution
      ("inventory delta credited to u's DROP/PICK") requires our command
      stream, which exists only for our side.
  A2. D-1 progress events are exactly the spec's list, evaluated on state
      transitions whose both endpoints lie inside the window [t, t+2k]:
      (i) any change of u's carry vector, (ii) own-inventory change on a turn
      where u issued DROP or PICK, (iii) a plant created/removed at u's cell.
  A3. D-2 "net inv + carry change of zero" = element-wise equality of the
      6-vector (own inventory + u's carry) between S_[window start] and
      S_[window end + 1]; windows ending on the final turn (no post-state)
      cannot be evaluated and are skipped.
  A4. D-3: declared target(u,t) telemetry does not exist in recorded traces,
      so the two observable proxies are used: (a) two own units emitting MOVE
      to the identical destination cell on >= 2 consecutive turns (door
      destinations included -- I-22 requires distinct door cells when both
      bank), (b) a MOVE whose realized landing (pos in the next state) equals
      the cell of a stationary-working own peer, >= 2 consecutive turns.
      A unit with no command this turn is treated as WAIT (stationary-working).
  A5. D-4 commitment start (I-19/I-21): carry[WOOD] > 0 and (MOVE whose
      destination is a door cell, or DROP while standing on a door cell, or
      forced: free_capacity == 0). Death terminates the interval as cargo
      loss (not a violation).
  A6. D-5 "own banana" = a cell where our PLANT BANANA executed and a banana
      plant has been continuously present since. chop_power for the I-5
      cutoffs = max own chop_power at the plant turn (no chopper => cutoff
      formula degenerates and the plant is flagged). Global late cutoff
      (I-5, "size-1 chop" clause): t > 300 - (ceil(health(1)=3 / chop) + 1).
  A7. D-6 clause (a) takes min own ETA over ALL own units (D-6/I-10 wording),
      not the I-7 wood-committed restriction.
  A8. D-7 uses per-unit FIFO banana accounting. Bananas PICKed from the bank
      are tracked with provenance 'bank_pick' and are subject to the same
      age-12 and loss rules (strictest). Death while carrying bananas counts
      as lost. End-of-game carry is excused only for 'harvest' provenance
      acquired within the final 6 turns.
  A9. D-8 chop target = the plant on the chopping unit's own cell (mirrors
      the parent's emission rule CHOP only when plant.cell == unit.cell).
  A10. D-9 literal reading: any banana-attributable command (PLANT ... BANANA
      or PICK ... BANANA) while |own units| == 1 before the first own TRAIN
      is flagged, even if training is infeasible (I-16's infeasibility
      exemption is NOT applied -- D-9's text does not carry it). The paired
      parent clauses (TRAIN turn/stats parity) run only when a parent command
      stream is supplied (--parent-commands-file).
  A11. If the transcript holds more (or fewer) turn blocks than the command
      stream has lines, the trace is truncated to the common prefix and the
      report notes it.

CLI:
  python3 trace_detectors.py --transcript-file X --commands-file Y --report OUT.json
  python3 trace_detectors.py --packet packet.json.gz --game-id N --report OUT.json
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import deque

# --- items / rules (game::rules, verified against family-readable-guide.rs) --
ITEM_NAMES = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = range(6)
TOTAL_TURNS = 300  # rules::TOTAL_TURNS

BANANA_PLANT_COOLDOWN = 6   # plant_cooldown(Banana)  [spec sec. 0]
BANANA_WATER_BOOST = 2      # water_boost(Banana) => CD_wet = 4, CD_dry = 6
BANANA_HEALTH_BASE = 2      # tree_health_params(Banana) = (2, 1): health = 2 + size
BANANA_HEALTH_SLOPE = 1

UNREACHABLE = 10000         # spec sec. 0: unreachable ETA = 10000

WORKING_VERBS = {"HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE", "WAIT"}
D4_BANNED_VERBS = {"HARVEST", "CHOP", "PLANT", "MINE", "PICK"}  # D-4 non-bank verbs


def ceil_div(a: int, b: int) -> int:
    """MoisanBot::ceil_div — b <= 0 yields the 10000 sentinel."""
    if b <= 0:
        return UNREACHABLE
    return -(-a // b)


# ---------------------------------------------------------------------------
# Exact banana growth arithmetic (mirrors of the candidate's own
# MoisanBot::predict_tree / MoisanBot::chop_outcome in research-banana-r2.rs:
# per turn, an existing cooldown ticks down; when it reaches zero a
# size-below-4 tree grows one size, gains tree_health_params(Banana).1 = 1
# health, and the cooldown resets to the effective plant cooldown (6 dry,
# 4 near water); a size-4 tree ripens one fruit instead, up to 3. Banana
# health = 2 + size. A chop is applied before the growth tick of the same
# turn (rules order verified against the referee of make_banana_traces and
# chop_outcome).
# ---------------------------------------------------------------------------

def banana_effective_cooldown(near_water: bool) -> int:
    return (BANANA_PLANT_COOLDOWN - BANANA_WATER_BOOST if near_water
            else BANANA_PLANT_COOLDOWN)


def banana_predict_tree(size, health, fruits, cooldown, turns,
                        near_water=False):
    """Growth-only forward simulation of a banana tree over ``turns`` turns
    (mirror of MoisanBot::predict_tree with no opponent chopper). Returns
    (size, health, fruits, cooldown)."""
    for _ in range(turns):
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and health > 0:
            if size < 4:
                size += 1
                health += BANANA_HEALTH_SLOPE
                cooldown = banana_effective_cooldown(near_water)
            elif fruits < 3:
                fruits += 1
                cooldown = banana_effective_cooldown(near_water)
    return size, health, fruits, cooldown


def banana_exact_chop_turns(size, health, cooldown, chop_power,
                            near_water=False):
    """Exact growth-aware number of chop turns needed to fell a banana tree
    from the given state (mirror of MoisanBot::chop_outcome): each turn the
    chop lands first, then the cooldown ticks and a size-below-4 tree that
    reaches cooldown 0 grows (+1 size, +1 health, cooldown reset). Returns
    the chop-turn count, or UNREACHABLE if chop_power <= 0 or the tree
    cannot be felled within 100 turns.

    Review counterexample (successor host review 2026-08-05, terminal
    failure 1): size 2, health 4, cooldown 1, chop_power 1 needs FIVE chops
    (the tree grows after chop 1), while the rejected candidate's static
    ceil(health / chop_power) claims four.
    """
    if chop_power <= 0:
        return UNREACHABLE
    for turns in range(1, 101):
        health -= chop_power
        if health <= 0:
            return turns
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and size < 4:
            size += 1
            health += BANANA_HEALTH_SLOPE
            cooldown = banana_effective_cooldown(near_water)
    return UNREACHABLE


# ---------------------------------------------------------------------------
# Protocol mirror
# ---------------------------------------------------------------------------

class StaticMap:
    def __init__(self, width, height, walkable, shacks, iron, water):
        self.width = width
        self.height = height
        self.walkable = walkable      # frozenset[(x, y)]
        self.shacks = shacks          # [own_tent, enemy_tent]
        self.iron = iron
        self.water = water


class Plant:
    __slots__ = ("kind", "cell", "size", "health", "fruits", "cooldown")

    def __init__(self, kind, cell, size, health, fruits, cooldown):
        self.kind = kind
        self.cell = cell
        self.size = size
        self.health = health
        self.fruits = fruits
        self.cooldown = cooldown


class Unit:
    __slots__ = ("id", "player", "cell", "speed", "capacity", "harvest_power",
                 "chop_power", "carry")

    def __init__(self, uid, player, cell, speed, capacity, harvest_power,
                 chop_power, carry):
        self.id = uid
        self.player = player
        self.cell = cell
        self.speed = speed
        self.capacity = capacity
        self.harvest_power = harvest_power
        self.chop_power = chop_power
        self.carry = carry            # list of 6 ints

    def total_carried(self):
        return sum(self.carry)

    def free_capacity(self):
        return self.capacity - self.total_carried()


class GameState:
    __slots__ = ("inventories", "plants", "units", "turn",
                 "_plant_by_cell", "_unit_by_id")

    def __init__(self, inventories, plants, units, turn):
        self.inventories = inventories
        self.plants = plants
        self.units = units
        self.turn = turn
        self._plant_by_cell = {p.cell: p for p in plants}
        self._unit_by_id = {u.id: u for u in units}

    def plant_at(self, cell):
        return self._plant_by_cell.get(cell)

    def unit(self, uid):
        return self._unit_by_id.get(uid)

    def own_units(self):
        return [u for u in self.units if u.player == 0]

    def opp_units(self):
        return [u for u in self.units if u.player == 1]


class TraceParser:
    """Mirror of protocol::read_static_map + repeated protocol::read_turn."""

    def parse(self, transcript_text):
        lines = transcript_text.split("\n")
        it = iter(lines)

        def next_line():
            for line in it:
                return line.rstrip("\r")
            return None

        header = next_line()
        if header is None:
            raise ValueError("empty transcript")
        parts = header.split()
        width, height = int(parts[0]), int(parts[1])
        walkable, iron, water = set(), set(), set()
        shacks = [(0, 0), (0, 0)]
        for y in range(height):
            row = next_line()
            if row is None:
                raise ValueError("truncated static map")
            for x, ch in enumerate(row):
                cell = (x, y)
                if ch == "0":
                    shacks[0] = cell
                elif ch == "1":
                    shacks[1] = cell
                elif ch == ".":
                    walkable.add(cell)
                elif ch == "+":
                    iron.add(cell)
                elif ch == "~":
                    water.add(cell)
        smap = StaticMap(width, height, frozenset(walkable), shacks,
                         frozenset(iron), frozenset(water))

        states = []
        turn = 0
        while True:
            turn += 1
            state = self._read_turn(next_line, turn)
            if state is None:
                break
            states.append(state)
        return smap, states

    @staticmethod
    def _read_turn(next_line, turn):
        inventories = []
        for _ in range(2):
            line = next_line()
            if line is None or not line.strip():
                return None
            values = [int(v) for v in line.split()]
            if len(values) != 6:
                return None
            inventories.append(values)
        line = next_line()
        if line is None or not line.strip():
            return None
        plant_count = int(line.strip())
        plants = []
        for _ in range(plant_count):
            line = next_line()
            if line is None:
                return None
            f = line.split()
            if len(f) != 7:
                return None
            plants.append(Plant(f[0].upper(), (int(f[1]), int(f[2])),
                                int(f[3]), int(f[4]), int(f[5]), int(f[6])))
        line = next_line()
        if line is None or not line.strip():
            return None
        unit_count = int(line.strip())
        units = []
        for _ in range(unit_count):
            line = next_line()
            if line is None:
                return None
            v = [int(x) for x in line.split()]
            if len(v) != 14:
                return None
            units.append(Unit(v[0], v[1], (v[2], v[3]), v[4], v[5], v[6],
                              v[7], v[8:14]))
        return GameState(inventories, plants, units, turn)


# ---------------------------------------------------------------------------
# Command parsing
# ---------------------------------------------------------------------------

class Command:
    __slots__ = ("verb", "unit_id", "args", "raw")

    def __init__(self, verb, unit_id, args, raw):
        self.verb = verb
        self.unit_id = unit_id
        self.args = args
        self.raw = raw


class TurnCommands:
    __slots__ = ("by_unit", "train", "all")

    def __init__(self):
        self.by_unit = {}   # unit_id -> Command (first one wins)
        self.train = None   # Command or None
        self.all = []


class CommandParser:
    """One line per turn; commands joined by ';'. Grammar per the parent bot
    (harness VALID_ARITIES): WAIT | MOVE id x y | CHOP id | HARVEST id |
    DROP id | MINE id | PICK id ITEM | PLANT id KIND | TRAIN a b c d | MSG.
    """

    def parse(self, commands_text):
        lines = commands_text.split("\n")
        while lines and lines[-1] == "":
            lines.pop()                     # trailing newline(s) only
        return [self.parse_line(line) for line in lines]

    @staticmethod
    def parse_line(line):
        tc = TurnCommands()
        for raw in line.split(";"):
            raw = raw.strip()
            if not raw:
                continue
            tok = raw.split()
            verb = tok[0].upper()
            if verb == "MSG":
                continue
            cmd = None
            if verb == "WAIT":
                cmd = Command("WAIT", None, [], raw)
            elif verb == "TRAIN" and len(tok) == 5:
                cmd = Command("TRAIN", None, [int(t) for t in tok[1:5]], raw)
            elif verb in ("CHOP", "HARVEST", "DROP", "MINE") and len(tok) == 2:
                cmd = Command(verb, int(tok[1]), [], raw)
            elif verb == "MOVE" and len(tok) == 4:
                cmd = Command("MOVE", int(tok[1]),
                              [(int(tok[2]), int(tok[3]))], raw)
            elif verb in ("PICK", "PLANT") and len(tok) == 3:
                cmd = Command(verb, int(tok[1]), [tok[2].upper()], raw)
            if cmd is None:
                continue
            tc.all.append(cmd)
            if cmd.verb == "TRAIN":
                if tc.train is None:
                    tc.train = cmd
            elif cmd.unit_id is not None:
                tc.by_unit.setdefault(cmd.unit_id, cmd)
        return tc


# ---------------------------------------------------------------------------
# Navigation (game::nav mirror: orthogonal 4-neighbour BFS on walkable)
# ---------------------------------------------------------------------------

def bfs_distances(walkable, sources):
    dist = {}
    queue = deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        cell = queue.popleft()
        d = dist[cell]
        x, y = cell
        for nxt in ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)):
            if nxt in walkable and nxt not in dist:
                dist[nxt] = d + 1
                queue.append(nxt)
    return dist


def cheby(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


# ---------------------------------------------------------------------------
# Trace context
# ---------------------------------------------------------------------------

class Trace:
    """Aligned (StaticMap, states S_1..S_T, commands C_1..C_T). 1-based turns."""

    def __init__(self, smap, states, commands):
        self.notes = []
        n = min(len(states), len(commands))
        if len(states) != len(commands):
            self.notes.append(
                "turn-count mismatch: %d states vs %d command lines; "
                "truncated to %d (A11)" % (len(states), len(commands), n))
        self.smap = smap
        self.states = states[:n]
        self.commands = commands[:n]
        self.T = n

        self.tent = smap.shacks[0]
        tx, ty = self.tent
        self.doors = frozenset(c for c in ((tx, ty + 1), (tx + 1, ty),
                                           (tx, ty - 1), (tx - 1, ty))
                               if c in smap.walkable)
        self.diag = frozenset(c for c in ((tx - 1, ty - 1), (tx + 1, ty - 1),
                                          (tx - 1, ty + 1), (tx + 1, ty + 1))
                              if c in smap.walkable)
        self.ring = frozenset(c for c in smap.walkable
                              if cheby(c, self.tent) == 1)
        self.door_dist = bfs_distances(smap.walkable, sorted(self.doors))

        ids = set()
        for st in self.states:
            for u in st.own_units():
                ids.add(u.id)
        self.own_ids = sorted(ids)
        self._own_banana = None

    # 1-based accessors -----------------------------------------------------
    def state(self, t):
        return self.states[t - 1]

    def cmds(self, t):
        return self.commands[t - 1]

    def unit(self, uid, t):
        return self.state(t).unit(uid)

    def pos(self, uid, t):
        u = self.unit(uid, t)
        return u.cell if u is not None else None

    def cmd_of(self, uid, t):
        return self.cmds(t).by_unit.get(uid)

    def near_water(self, cell):
        x, y = cell
        return any(w in self.smap.water
                   for w in ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)))

    # own-planted banana bookkeeping (shared by D-5 / D-6(b) / D-8) ---------
    def own_banana_history(self):
        """Returns (plant_events, alive_per_turn).

        plant_events: [(t, uid, cell)] for each own `PLANT <id> BANANA`.
        alive_per_turn[t] (1-based dict): set of cells holding a live
        own-planted banana in S_t — planted by us and continuously holding a
        banana plant since the state after the plant command (A6).
        """
        if self._own_banana is not None:
            return self._own_banana
        events = []
        for t in range(1, self.T + 1):
            for cmd in self.cmds(t).all:
                if cmd.verb == "PLANT" and cmd.args and cmd.args[0] == "BANANA":
                    u = self.unit(cmd.unit_id, t)
                    if u is not None and u.player == 0:
                        events.append((t, cmd.unit_id, u.cell))
        alive_per_turn = {}
        alive = set()
        planted_prev = set()
        events_by_turn = {}
        for (t, _uid, cell) in events:
            events_by_turn.setdefault(t, set()).add(cell)
        for t in range(1, self.T + 1):
            st = self.state(t)
            alive = {c for c in alive
                     if st.plant_at(c) is not None
                     and st.plant_at(c).kind == "BANANA"}
            for c in planted_prev:
                p = st.plant_at(c)
                if p is not None and p.kind == "BANANA":
                    alive.add(c)
            alive_per_turn[t] = set(alive)
            planted_prev = events_by_turn.get(t, set())
        self._own_banana = (events, alive_per_turn)
        return self._own_banana


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

def _result(name, episodes):
    return {
        "detector": name,
        "episodes": episodes,
        "count": len(episodes),
        # All detector thresholds are 0 episodes (spec: "All thresholds are
        # 0 episodes unless stated").
        "verdict": "PASS" if not episodes else "FAIL",
    }


def detect_d1(tr: Trace):
    """D-1 A->B->A movement.

    Predicate (spec D-1): exists own unit u, cells a != b, window [t, t+2k]
    with k >= 3 (>= 7 states / >= 6 transitions -- threshold cited from D-1:
    "window [t, t+2k], k >= 3"), pos alternating a,b,a,b,...,a, and ZERO
    progress events for u inside the window. Threshold: 0 episodes.
    Progress events per A2: carry change / inv change on u's DROP-PICK turn /
    plant created-removed at u's cell. Own units only (A1).
    """
    episodes = []
    T = tr.T
    for uid in tr.own_ids:
        pos = [None] * (T + 2)
        for t in range(1, T + 1):
            pos[t] = tr.pos(uid, t)

        def progress(t):
            # progress event on transition S_t -> S_{t+1} for unit uid
            if t + 1 > T:
                return True
            u0 = tr.unit(uid, t)
            u1 = tr.unit(uid, t + 1)
            if u0 is None or u1 is None:
                return True
            if u0.carry != u1.carry:
                return True
            cmd = tr.cmd_of(uid, t)
            if cmd is not None and cmd.verb in ("DROP", "PICK"):
                if tr.state(t).inventories[0] != tr.state(t + 1).inventories[0]:
                    return True
            p0 = tr.state(t).plant_at(u0.cell)
            p1 = tr.state(t + 1).plant_at(u0.cell)
            if (p0 is None) != (p1 is None):
                return True
            return False

        s = 1
        t = 2
        runs = []
        while t <= T + 1:
            ok = False
            if t <= T:
                ok = (pos[t] is not None and pos[t - 1] is not None
                      and pos[t] != pos[t - 1]
                      and (t == s + 1 or pos[t] == pos[t - 2])
                      and not progress(t - 1))
            if ok:
                t += 1
                continue
            if (t - 1) - s >= 6:            # >= 7 states => k >= 3 (D-1)
                runs.append((s, t - 1))
            if t <= T and pos[t] is not None and pos[t - 1] is not None \
                    and pos[t] != pos[t - 1] and not progress(t - 1):
                s = t - 1
            else:
                s = t
            t += 1
        for (a, b) in runs:
            episodes.append({
                "unit": uid,
                "turn_start": a,
                "turn_end": b,
                "k": (b - a) // 2,
                "cells": [list(pos[a]), list(pos[a + 1])],
            })
    return _result("D-1", episodes)


def detect_d2(tr: Trace):
    """D-2 Repeated PICK/DROP.

    Predicate (spec D-2): exists own unit u and a window of <= 12 turns
    (threshold cited from D-2: "window of <= 12 turns" = 2 dry banana
    cooldowns) containing >= 2 PICKs and >= 2 DROPs by u at door cells with
    net (own inv + u's carry) change of zero over the window (A3).
    Threshold: 0 episodes.
    """
    episodes = []
    T = tr.T
    for uid in tr.own_ids:
        events = []
        for t in range(1, T + 1):
            cmd = tr.cmd_of(uid, t)
            if cmd is None or cmd.verb not in ("PICK", "DROP"):
                continue
            p = tr.pos(uid, t)
            if p in tr.doors:
                events.append((t, cmd.verb))
        i = 0
        while i < len(events):
            s = events[i][0]
            found = None
            for j in range(i + 1, len(events)):
                e = events[j][0]
                if e - s + 1 > 12:          # window length <= 12 turns (D-2)
                    break
                if e + 1 > T:
                    continue                # no observable post-state (A3)
                window = [ev for ev in events[i:j + 1]]
                picks = sum(1 for ev in window if ev[1] == "PICK")
                drops = sum(1 for ev in window if ev[1] == "DROP")
                if picks < 2 or drops < 2:  # >= 2 PICKs and >= 2 DROPs (D-2)
                    continue
                u0 = tr.unit(uid, s)
                u1 = tr.unit(uid, e + 1)
                if u0 is None or u1 is None:
                    continue
                v0 = [tr.state(s).inventories[0][k] + u0.carry[k]
                      for k in range(6)]
                v1 = [tr.state(e + 1).inventories[0][k] + u1.carry[k]
                      for k in range(6)]
                if v0 == v1:                # net zero over window (D-2)
                    found = (s, e, picks, drops)
                    break
            if found is not None:
                s, e, picks, drops = found
                episodes.append({"unit": uid, "turn_start": s, "turn_end": e,
                                 "picks": picks, "drops": drops})
                # advance past this window to avoid re-reporting overlaps
                while i < len(events) and events[i][0] <= e:
                    i += 1
            else:
                i += 1
    return _result("D-2", episodes)


def detect_d3(tr: Trace):
    """D-3 Same-target/occupied-cell contention.

    Predicate (spec D-3): two own units share a nontrivial target, or one
    unit's MOVE lands on a stationary-working own peer's cell, for >= 2
    consecutive turns (threshold cited from D-3 / I-23: "for >= 2 consecutive
    turns"; 1-turn transients belong to the conflict resolver).
    Threshold: 0 episodes. Observable proxies per A4.
    """
    episodes = []
    T = tr.T

    # (a) identical MOVE destinations, per own-unit pair
    pair_flags = {}
    for t in range(1, T + 1):
        dests = {}
        for uid in tr.own_ids:
            cmd = tr.cmd_of(uid, t)
            if cmd is not None and cmd.verb == "MOVE" \
                    and tr.unit(uid, t) is not None:
                dests.setdefault(cmd.args[0], []).append(uid)
        for dest, uids in sorted(dests.items()):
            if len(uids) >= 2:
                for a in range(len(uids)):
                    for b in range(a + 1, len(uids)):
                        pair_flags.setdefault((uids[a], uids[b]), {})[t] = dest
    for (u, v), turns in sorted(pair_flags.items()):
        ts = sorted(turns)
        run = [ts[0]]
        for t in ts[1:] + [None]:
            if t is not None and t == run[-1] + 1:
                run.append(t)
                continue
            if len(run) >= 2:               # >= 2 consecutive turns (D-3)
                episodes.append({
                    "kind": "shared_move_target", "units": [u, v],
                    "turn_start": run[0], "turn_end": run[-1],
                    "cells": [list(turns[x]) for x in run]})
            if t is not None:
                run = [t]

    # (b) MOVE landing on a stationary-working peer's cell
    for u in tr.own_ids:
        for v in tr.own_ids:
            if u == v:
                continue
            flags = []
            for t in range(1, T):
                cu = tr.cmd_of(u, t)
                if cu is None or cu.verb != "MOVE":
                    flags.append(False)
                    continue
                pu1 = tr.pos(u, t + 1)
                pv0, pv1 = tr.pos(v, t), tr.pos(v, t + 1)
                if pu1 is None or pv0 is None or pv1 is None or pv0 != pv1:
                    flags.append(False)
                    continue
                cv = tr.cmd_of(v, t)
                working = (cv is None) or (cv.verb in WORKING_VERBS)
                flags.append(working and pu1 == pv0)
            run_start = None
            for idx, f in enumerate(flags + [False]):
                t = idx + 1
                if f and run_start is None:
                    run_start = t
                elif not f and run_start is not None:
                    if t - run_start >= 2:  # >= 2 consecutive turns (D-3)
                        episodes.append({
                            "kind": "landing_on_working_peer",
                            "units": [u, v],
                            "turn_start": run_start, "turn_end": t - 1})
                    run_start = None
    return _result("D-3", episodes)


def detect_d4(tr: Trace):
    """D-4 Abandoned carried-wood return.

    Predicate (spec D-4 / I-19..I-21): within a wood-committed interval,
    either a non-bank verb (HARVEST/CHOP/PLANT/MINE/PICK) for u, or 2
    consecutive turns with no decrease of door_dist(u) and no DROP/cargo-loss
    (threshold cited from D-4/I-20: "2 consecutive turns"; 1 turn of slack
    absorbs resolver displacement). Threshold: 0 episodes.
    Commitment start/end per A5.
    """
    episodes = []
    T = tr.T
    for uid in tr.own_ids:
        committed = False
        start = None
        nd_run = 0
        for t in range(1, T + 1):
            u = tr.unit(uid, t)
            if u is None:
                committed = False           # death = cargo loss, ends interval
                continue
            if committed and u.total_carried() == 0:
                committed = False           # cargo loss ends interval (I-19)
            if committed and tr.door_dist.get(u.cell) is None:
                committed = False           # no door reachable ends interval
            cmd = tr.cmd_of(uid, t)
            if not committed and u.carry[WOOD] > 0:
                starts = False
                if u.free_capacity() == 0:  # forced commitment (I-21)
                    starts = True
                elif cmd is not None and cmd.verb == "MOVE" \
                        and cmd.args[0] in tr.doors:
                    starts = True           # bank-target command (I-19, A5)
                elif cmd is not None and cmd.verb == "DROP" \
                        and u.cell in tr.doors:
                    starts = True
                if starts:
                    committed = True
                    start = t
                    nd_run = 0
            if not committed:
                continue
            if cmd is not None and cmd.verb in D4_BANNED_VERBS:
                episodes.append({"unit": uid, "kind": "non_bank_verb",
                                 "verb": cmd.verb, "turn_start": start,
                                 "turn_end": t})
            executed_drop = (cmd is not None and cmd.verb == "DROP"
                             and u.cell in tr.doors)
            if t + 1 > T:
                committed = False
                continue
            nu = tr.unit(uid, t + 1)
            if executed_drop or nu is None or nu.total_carried() == 0:
                committed = False           # DROP / death / cargo loss
                nd_run = 0
                continue
            d0 = tr.door_dist.get(u.cell)
            d1 = tr.door_dist.get(nu.cell)
            if d1 is None:
                committed = False
                nd_run = 0
                continue
            if d0 is not None and d1 >= d0:
                nd_run += 1
                if nd_run == 2:             # 2 consecutive non-progress (D-4)
                    episodes.append({"unit": uid, "kind": "no_progress",
                                     "turn_start": t - 1, "turn_end": t + 1})
            else:
                nd_run = 0
    return _result("D-4", episodes)


def detect_d5(tr: Trace):
    """D-5 Unbounded planting.

    Predicate (spec D-5 / I-12, I-13, I-5): any own PLANT BANANA with
    cheby(c, tent) != 1; concurrent live own bananas > |Ring|; cumulative
    distinct plant cells > |Ring| (|Ring| <= 8, I-13); or any plant after its
    I-5 cutoff:
      orthogonal slot: t > 300 - (2*CD(c) + ceil(health(2)=4 / chop) + 2),
        CD(c) = 4 near water else 6 (I-5);
      global (size-1 chop clause, A6): t > 300 - (ceil(health(1)=3/chop) + 1).
    Threshold: 0 violations.
    """
    episodes = []
    events, alive_per_turn = tr.own_banana_history()
    ring_size = len(tr.ring)
    cumulative = set()
    for (t, uid, c) in events:
        if cheby(c, tr.tent) != 1:          # I-12: Ring only (D-5)
            episodes.append({"unit": uid, "kind": "outside_ring",
                             "turn_start": t, "turn_end": t, "cell": list(c)})
        cumulative.add(c)
        if len(cumulative) > ring_size:     # I-13 cumulative bound (D-5)
            episodes.append({"unit": uid, "kind": "cumulative_over_ring",
                             "turn_start": t, "turn_end": t, "cell": list(c),
                             "cumulative": len(cumulative),
                             "ring_size": ring_size})
        chop = max((u.chop_power for u in tr.state(t).own_units()
                    if u.chop_power > 0), default=0)
        cd = (BANANA_PLANT_COOLDOWN - BANANA_WATER_BOOST) \
            if tr.near_water(c) else BANANA_PLANT_COOLDOWN  # CD_wet=4/CD_dry=6
        if c in tr.doors:
            # I-5 orthogonal-slot cutoff: T_late = 300 - (2*CD + ceil(4/chop) + 2)
            t_late = TOTAL_TURNS - (2 * cd + ceil_div(
                BANANA_HEALTH_BASE + BANANA_HEALTH_SLOPE * 2, chop) + 2)
            if t > t_late:
                episodes.append({"unit": uid, "kind": "orth_cutoff",
                                 "turn_start": t, "turn_end": t,
                                 "cell": list(c), "t_late": t_late})
        # I-5 global cutoff (size-1 chop must still yield >= 4 pts, A6)
        t_glob = TOTAL_TURNS - (ceil_div(
            BANANA_HEALTH_BASE + BANANA_HEALTH_SLOPE * 1, chop) + 1)
        if t > t_glob:
            episodes.append({"unit": uid, "kind": "global_cutoff",
                             "turn_start": t, "turn_end": t,
                             "cell": list(c), "t_late": t_glob})
    over_start = None
    for t in range(1, tr.T + 1):
        over = len(alive_per_turn[t]) > ring_size   # I-13 concurrent bound
        if over and over_start is None:
            over_start = t
        elif not over and over_start is not None:
            episodes.append({"unit": None, "kind": "concurrent_over_ring",
                             "turn_start": over_start, "turn_end": t - 1,
                             "ring_size": ring_size})
            over_start = None
    if over_start is not None:
        episodes.append({"unit": None, "kind": "concurrent_over_ring",
                         "turn_start": over_start, "turn_end": tr.T,
                         "ring_size": ring_size})
    return _result("D-5", episodes)


def detect_d6(tr: Trace):
    """D-6 Opponent-favored fruit creation.

    Predicate (spec D-6 / I-10, I-11):
    (a) at any own PLANT BANANA (c, t): eta_opp_h(c,t) <= min_u eta_u(c,t)
        (ties to the opponent), or eta_opp_x(c,t) <= 2 (thresholds cited from
        D-6: "<= min_u eta_u" and "eta_opp_x <= 2"); min over ALL own units
        (A7); ETA = ceil(bfs/speed), unreachable = 10000.
    (b) an opponent unit on an own-planted banana cell whose fruits decrease
        while that opponent's banana carry increases. Threshold: 0.
    """
    episodes = []
    events, alive_per_turn = tr.own_banana_history()
    for (t, uid, c) in events:
        dist = bfs_distances(tr.smap.walkable, [c])

        def eta(u):
            d = dist.get(u.cell)
            if d is None:
                return UNREACHABLE
            return ceil_div(d, u.speed)

        st = tr.state(t)
        own_etas = [eta(u) for u in st.own_units()]
        min_own = min(own_etas) if own_etas else UNREACHABLE
        opp_h = min((eta(u) for u in st.opp_units() if u.harvest_power > 0),
                    default=UNREACHABLE)
        opp_x = min((eta(u) for u in st.opp_units() if u.chop_power > 0),
                    default=UNREACHABLE)
        if opp_h <= min_own:                # D-6(a) harvest race (tie loses)
            episodes.append({"unit": uid, "kind": "opp_harvest_eta",
                             "turn_start": t, "turn_end": t, "cell": list(c),
                             "eta_opp_h": opp_h, "min_own_eta": min_own})
        if opp_x <= 2:                      # D-6(a) chopper within 2 turns
            episodes.append({"unit": uid, "kind": "opp_chop_eta",
                             "turn_start": t, "turn_end": t, "cell": list(c),
                             "eta_opp_x": opp_x})
    for t in range(1, tr.T):
        st0, st1 = tr.state(t), tr.state(t + 1)
        for c in sorted(alive_per_turn[t]):
            p0, p1 = st0.plant_at(c), st1.plant_at(c)
            if p0 is None or p1 is None or p1.fruits >= p0.fruits:
                continue
            for v in st0.opp_units():
                if v.cell != c:
                    continue
                v1 = st1.unit(v.id)
                if v1 is not None and v1.carry[BANANA] > v.carry[BANANA]:
                    episodes.append({"unit": None, "kind": "opp_harvested_ours",
                                     "opp_unit": v.id, "turn_start": t,
                                     "turn_end": t + 1, "cell": list(c)})
    return _result("D-6", episodes)


def detect_d7(tr: Trace):
    """D-7 Lost harvested fruit.

    Predicate (spec D-7 / I-8): FIFO banana ledger per own unit — every
    carried banana must end as banked (DROP at a door with own inv[BANANA]
    increase) or planted (PLANT BANANA); end-of-game carry excused only for
    bananas harvested in the final 6 turns (threshold cited from D-7:
    "final 6 turns" = one dry cooldown); any carried banana older than 12
    turns (D-7/I-8: "age > 12" = two dry cooldowns) without bank/plant is a
    violation. Threshold: 0 lost units. Provenance/death handling per A8.
    """
    episodes = []
    T = tr.T
    for uid in tr.own_ids:
        fifo = deque()   # entries: {"acq": turn, "prov": str, "aged": bool}
        prev_present = False
        for t in range(1, T + 1):
            u = tr.unit(uid, t)
            if u is None:
                if prev_present and fifo:
                    episodes.append({"unit": uid, "kind": "lost_on_death",
                                     "turn_start": t, "turn_end": t,
                                     "bananas": len(fifo)})
                    fifo.clear()
                prev_present = False
                continue
            prev_present = True
            for entry in fifo:
                if not entry["aged"] and t - entry["acq"] > 12:  # age > 12
                    entry["aged"] = True
                    episodes.append({"unit": uid, "kind": "carried_overage",
                                     "turn_start": entry["acq"],
                                     "turn_end": t,
                                     "provenance": entry["prov"]})
            if t + 1 > T:
                break
            u1 = tr.unit(uid, t + 1)
            if u1 is None:
                continue    # death handled at t+1
            delta = u1.carry[BANANA] - u.carry[BANANA]
            cmd = tr.cmd_of(uid, t)
            if delta > 0:
                if cmd is not None and cmd.verb == "HARVEST":
                    prov = "harvest"
                elif cmd is not None and cmd.verb == "PICK" \
                        and cmd.args and cmd.args[0] == "BANANA":
                    prov = "bank_pick"
                else:
                    prov = "unknown"
                for _ in range(delta):
                    fifo.append({"acq": t + 1, "prov": prov, "aged": False})
            elif delta < 0:
                n = -delta
                banked = (cmd is not None and cmd.verb == "DROP"
                          and u.cell in tr.doors
                          and tr.state(t + 1).inventories[0][BANANA]
                          > tr.state(t).inventories[0][BANANA])
                planted = (cmd is not None and cmd.verb == "PLANT"
                           and cmd.args and cmd.args[0] == "BANANA")
                if not banked and not planted:
                    episodes.append({"unit": uid, "kind": "lost_bananas",
                                     "turn_start": t, "turn_end": t + 1,
                                     "bananas": n})
                for _ in range(min(n, len(fifo))):
                    fifo.popleft()
        # end-of-game carry: excused only if harvested in final 6 turns (D-7)
        for entry in fifo:
            if entry["prov"] == "harvest" and entry["acq"] > T - 6:
                continue
            episodes.append({"unit": uid, "kind": "unbanked_at_end",
                             "turn_start": entry["acq"], "turn_end": T,
                             "provenance": entry["prov"]})
    return _result("D-7", episodes)


def _d8_resident_id(tr: Trace):
    """I-7 committed harvester = the resident = the starter (min-id own unit
    at turn 1; spec B3 ambiguity resolution)."""
    own = tr.state(1).own_units()
    return min(u.id for u in own) if own else None


def _d8_opp_harvester_eta(tr: Trace, t, dist):
    """Min ETA over opponent harvest-capable units toward the mother cell at
    turn t (I-7 opponent side: harvest-capable only; ceil(bfs/speed))."""
    best = UNREACHABLE
    for v in tr.state(t).opp_units():
        if v.harvest_power <= 0:
            continue
        d = dist.get(v.cell)
        if d is None:
            continue
        best = min(best, ceil_div(d, max(v.speed, 1)))
    return best


def _d8_ownership_lost_by(tr: Trace, cell, turn, alive_per_turn):
    """True iff I-7 ownership of ``cell`` flipped to lost at some turn
    f <= ``turn`` while the own-planted mother was alive: NOT
    (eta_res(cell,f) < eta_opp_h(cell,f)), strict inequality, ties conceded
    ('ties are treated as not owned', I-7). Once lost the flip is latched:
    the asset does not silently become owned again for D-8 purposes.
    Returns (True, f, eta_res, eta_opp) or (False, None, None, None)."""
    rid = _d8_resident_id(tr)
    if rid is None:
        return False, None, None, None
    dist = bfs_distances(set(tr.smap.walkable) | {cell}, [cell])
    for f in range(1, turn + 1):
        if cell not in alive_per_turn[f]:
            continue
        res = tr.state(f).unit(rid)
        if res is None or res.player != 0:
            continue
        d = dist.get(res.cell)
        eta_res = ceil_div(d, max(res.speed, 1)) if d is not None \
            else UNREACHABLE
        eta_opp = _d8_opp_harvester_eta(tr, f, dist)
        if not (eta_res < eta_opp):
            return True, f, eta_res, eta_opp
    return False, None, None, None


def detect_d8(tr: Trace):
    """D-8 Diagonal-mother chop (amended per the integrator's narrow D-8/I-10a
    ruling, successor host review
    data/analysis/live-agent-6553250/banana-restoration-r2-successor-host-review-2026-08-05.md
    and ACK coordination/messages/local_codex_1/20260805T083001Z-20260802-banana-restoration-r2-ack.md,
    branch origin/agent/local_codex_1).

    Base predicate (spec D-8 / I-14): any own chop-class command targeting a
    cell in diag(tent) holding a live own banana (chop target = the unit's
    own cell, A9). Threshold: 0, at any turn including endgame.

    Amendment (integrator-sanctioned, option (a) narrowly): the I-10a
    ownership-loss conversion overrides diagonal-mother protection ONLY when
    BOTH hold at the start of the chop sequence on that cell:

      (a) ownership of the mother had actually flipped to lost at or before
          the chop-start turn — per the I-7 committed-harvester ETA test
          (eta of the resident vs min opponent harvest-capable ETA, strict,
          ties conceded), latched once lost; AND
      (b) the conversion wins the strict exact race, growth-aware: the exact
          chop-turn count from the plant state at the chop-start turn
          (banana_exact_chop_turns, mirroring MoisanBot::chop_outcome —
          growth during the chop included) is strictly less than the
          opponent harvester ETA at the chop-start turn.

    While the mother remains owned, every discretionary diagonal-mother chop
    remains forbidden (I-14). A chop after a flip that loses the exact race
    is likewise flagged (the required response is abandon, I-10a).
    The exemption is decided once, at the first CHOP on the cell, and covers
    the subsequent chops of that same conversion sequence.
    """
    episodes = []
    _events, alive_per_turn = tr.own_banana_history()
    exempt_cells = {}      # cell -> bool (decision at chop-start, latched)
    for t in range(1, tr.T + 1):
        st = tr.state(t)
        for cmd in tr.cmds(t).all:
            if cmd.verb != "CHOP":
                continue
            u = st.unit(cmd.unit_id)
            if u is None or u.player != 0:
                continue
            c = u.cell
            if c in tr.diag and c in alive_per_turn[t]:
                p = st.plant_at(c)
                if p is not None and p.kind == "BANANA":
                    if c not in exempt_cells:
                        # chop-start turn: decide the I-10a exemption
                        lost, flip_t, eta_res, eta_opp_f = \
                            _d8_ownership_lost_by(tr, c, t, alive_per_turn)
                        dist = bfs_distances(set(tr.smap.walkable) | {c},
                                             [c])
                        eta_opp_now = _d8_opp_harvester_eta(tr, t, dist)
                        exact_chops = banana_exact_chop_turns(
                            p.size, p.health, p.cooldown, u.chop_power,
                            tr.near_water(c))
                        race_won = exact_chops < eta_opp_now
                        exempt_cells[c] = {
                            "exempt": lost and race_won,
                            "flip_turn": flip_t,
                            "eta_res_at_flip": eta_res,
                            "eta_opp_at_flip": eta_opp_f,
                            "chop_start": t,
                            "exact_chop_turns": exact_chops,
                            "eta_opp_at_chop_start": eta_opp_now,
                            "reason": None if (lost and race_won) else (
                                "flip_but_infeasible" if lost
                                else "discretionary_owned"),
                        }
                    decision = exempt_cells[c]
                    if decision["exempt"]:
                        continue
                    health_drop = None
                    if t + 1 <= tr.T:
                        p1 = tr.state(t + 1).plant_at(c)
                        health_drop = (p1 is None or p1.health < p.health)
                    episodes.append({"unit": u.id, "kind": "diag_mother_chop",
                                     "turn_start": t, "turn_end": t,
                                     "cell": list(c),
                                     "health_decreased": health_drop,
                                     "reason": decision["reason"],
                                     "flip_turn": decision["flip_turn"],
                                     "exact_chop_turns":
                                         decision["exact_chop_turns"],
                                     "eta_opp_at_chop_start":
                                         decision["eta_opp_at_chop_start"]})
    return _result("D-8", episodes)


def detect_d9(tr: Trace, parent_commands=None):
    """D-9 Second-worker TRAIN displacement.

    Predicate (spec D-9 / I-16..I-18): candidate TRAIN turn > parent TRAIN
    turn, TRAIN absent where the parent trains, or a different stats tuple
    (paired clauses require --parent-commands-file); or any
    banana-attributable command (PLANT/PICK ... BANANA, A10) before the
    candidate's TRAIN while |own units| == 1. Threshold: 0 displaced turns.
    """
    episodes = []
    first_train = None
    train_stats = None
    for t in range(1, tr.T + 1):
        if tr.cmds(t).train is not None:
            first_train = t
            train_stats = tr.cmds(t).train.args
            break
    for t in range(1, tr.T + 1):
        if first_train is not None and t >= first_train:
            break
        st = tr.state(t)
        if len(st.own_units()) != 1:
            continue
        for cmd in tr.cmds(t).all:
            if cmd.verb in ("PLANT", "PICK") and cmd.args \
                    and cmd.args[0] == "BANANA":
                u = st.unit(cmd.unit_id)
                if u is not None and u.player == 0:
                    episodes.append({"unit": cmd.unit_id,
                                     "kind": "banana_before_train",
                                     "verb": cmd.verb,
                                     "turn_start": t, "turn_end": t})
    if parent_commands is not None:
        p_train, p_stats = None, None
        for t, tc in enumerate(parent_commands, start=1):
            if tc.train is not None:
                p_train, p_stats = t, tc.train.args
                break
        if p_train is not None:
            if first_train is None:
                episodes.append({"unit": None, "kind": "train_missing",
                                 "turn_start": p_train, "turn_end": p_train})
            elif first_train > p_train:
                episodes.append({"unit": None, "kind": "train_late",
                                 "turn_start": p_train,
                                 "turn_end": first_train})
            elif train_stats != p_stats:
                episodes.append({"unit": None, "kind": "train_stats_differ",
                                 "turn_start": first_train,
                                 "turn_end": first_train,
                                 "candidate_stats": train_stats,
                                 "parent_stats": p_stats})
    return _result("D-9", episodes)


DETECTORS = [detect_d1, detect_d2, detect_d3, detect_d4, detect_d5,
             detect_d6, detect_d7, detect_d8, detect_d9]


def run_all(tr: Trace, parent_commands=None):
    results = []
    for det in DETECTORS:
        if det is detect_d9:
            results.append(det(tr, parent_commands))
        else:
            results.append(det(tr))
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_trace(transcript_text, commands_text):
    smap, states = TraceParser().parse(transcript_text)
    commands = CommandParser().parse(commands_text)
    return Trace(smap, states, commands)


def load_packet_row(packet_path, game_id):
    with gzip.open(packet_path, "rt", encoding="utf-8") as fh:
        packet = json.load(fh)
    rows = packet["rows"] if isinstance(packet, dict) else packet
    for row in rows:
        if int(row.get("game_id", -1)) == int(game_id):
            return row
    raise SystemExit("game_id %s not found in %s" % (game_id, packet_path))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript-file")
    ap.add_argument("--commands-file")
    ap.add_argument("--packet")
    ap.add_argument("--game-id")
    ap.add_argument("--parent-commands-file")
    ap.add_argument("--report")
    args = ap.parse_args(argv)

    game_id = None
    if args.packet:
        if not args.game_id:
            raise SystemExit("--packet requires --game-id")
        row = load_packet_row(args.packet, args.game_id)
        transcript, commands = row["transcript"], row["baseline_output"]
        game_id = int(row["game_id"])
    elif args.transcript_file and args.commands_file:
        with open(args.transcript_file, encoding="utf-8") as fh:
            transcript = fh.read()
        with open(args.commands_file, encoding="utf-8") as fh:
            commands = fh.read()
    else:
        raise SystemExit("need --transcript-file+--commands-file or "
                         "--packet+--game-id")

    parent_commands = None
    if args.parent_commands_file:
        with open(args.parent_commands_file, encoding="utf-8") as fh:
            parent_commands = CommandParser().parse(fh.read())

    tr = build_trace(transcript, commands)
    results = run_all(tr, parent_commands)
    report = {
        "game_id": game_id,
        "turns": tr.T,
        "tent": list(tr.tent),
        "ring_size": len(tr.ring),
        "notes": tr.notes,
        "detectors": results,
        "overall": "PASS" if all(r["verdict"] == "PASS" for r in results)
                   else "FAIL",
    }
    text = json.dumps(report, indent=1, sort_keys=True)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    for r in results:
        print("%s: %s (%d episodes)" % (r["detector"], r["verdict"],
                                        r["count"]))
    print("overall:", report["overall"])
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
