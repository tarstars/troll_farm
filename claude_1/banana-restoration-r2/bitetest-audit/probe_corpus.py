#!/usr/bin/env python3
"""Deterministic liveness-probe corpus for the detector mutation experiment.

WHY THIS EXISTS.  A mutant that survives the bite-test suite has two very
different possible causes:

  (a) the mutation really changed detector semantics and the suite cannot see
      it  -> a genuine finding about the suite;
  (b) the patch was inert -- it edited a dead branch, or the intended semantic
      change is unreachable in this code -> a defective mutant, and reporting
      it as "survived" overstates the finding.

The 2026-08-08 audit could not distinguish these, which is one reason its
mutation ledger was rejected (review BAR-1).  This module supplies the
missing discriminator: a fixed, seeded corpus of synthetic traces that is
authored INDEPENDENTLY of ``test_trace_detectors.py`` (it does not import it
and does not reuse its fixtures), run through all nine detectors.  Two
digests are produced per detector.  If a mutant changes the pristine digest
of the detector it targets, the mutation is LIVE; if it does not, the mutant
is UNWITNESSED and must not be counted as evidence that the suite is weak.

The corpus is NOT a truth oracle and is NOT a validity test.  It only asks
"does this edit change observable detector behaviour anywhere".

Deterministic: stdlib ``random.Random`` with fixed seeds, no clock, no I/O.
Run standalone to print the digest table:  python3 probe_corpus.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys

import trace_detectors as td

# Two maps.  MAP_A is dry and open (exercises the CD_dry branch); MAP_B has
# water next to several ring cells and an iron block (exercises near_water and
# an unwalkable interior cell, so BFS distances are not pure Manhattan).
MAP_A = [
    "9 7",
    ".........",
    ".........",
    ".........",
    "....0....",
    ".........",
    ".........",
    "........1",
]

MAP_B = [
    "9 7",
    ".........",
    "..~......",
    "...~.....",
    "....0....",
    "...~.+...",
    ".........",
    "........1",
]

VERBS_UNIT = ["MOVE", "CHOP", "HARVEST", "DROP", "MINE", "PICK", "PLANT",
              "WAIT"]
ITEMS = ["BANANA", "WOOD", "IRON"]
PLANT_KINDS = ["BANANA", "PLUM"]


def _walkable(map_rows):
    cells = []
    for y, row in enumerate(map_rows[1:]):
        for x, ch in enumerate(row):
            if ch == ".":
                cells.append((x, y))
    return cells


def _unit_line(rng, uid, player, cell, carry=None):
    carry = carry or [0] * 6
    return " ".join(str(v) for v in [
        uid, player, cell[0], cell[1],
        rng.choice([1, 1, 2]),          # speed
        rng.choice([2, 2, 3]),          # capacity
        rng.choice([0, 1, 1]),          # harvest power
        rng.choice([0, 1, 1, 2]),       # chop power
    ] + list(carry))


def _plant_line(rng, cell):
    kind = rng.choice(PLANT_KINDS)
    size = rng.randint(1, 4)
    return "%s %d %d %d %d %d %d" % (
        kind, cell[0], cell[1], size, 2 + size,
        rng.randint(0, 2) if size == 4 else 0, rng.randint(0, 6))


def _command(rng, uid, cells):
    verb = rng.choice(VERBS_UNIT)
    if verb == "MOVE":
        x, y = rng.choice(cells)
        return "MOVE %d %d %d" % (uid, x, y)
    if verb == "PICK":
        return "PICK %d %s" % (uid, rng.choice(ITEMS))
    if verb == "PLANT":
        return "PLANT %d %s" % (uid, rng.choice(PLANT_KINDS))
    if verb == "WAIT":
        return "WAIT"
    return "%s %d" % (verb, uid)


def build_trace(seed, map_rows):
    """One deterministic pseudo-random trace.  Positions drift by at most one
    orthogonal step per turn so that movement runs, stalls and A<->B
    alternations all occur naturally somewhere in the corpus."""
    rng = random.Random(seed)
    cells = _walkable(map_rows)
    turns = rng.randint(4, 22)
    n_own = rng.randint(1, 3)
    n_opp = rng.randint(1, 2)
    own_ids = list(range(n_own))
    opp_ids = [10 + i for i in range(n_opp)]
    pos = {uid: rng.choice(cells) for uid in own_ids + opp_ids}
    carry = {uid: [0] * 6 for uid in own_ids + opp_ids}
    live_plants = {}
    body = list(map_rows)
    cmd_lines = []
    inv0 = [rng.randint(0, 3) for _ in range(6)]
    inv1 = [rng.randint(0, 3) for _ in range(6)]

    for t in range(1, turns + 1):
        # ---- emit state S_t -------------------------------------------
        plant_rows = list(live_plants.values())
        body.append(" ".join(str(v) for v in inv0))
        body.append(" ".join(str(v) for v in inv1))
        body.append(str(len(plant_rows)))
        body.extend(plant_rows)
        unit_rows = []
        for uid in own_ids:
            unit_rows.append(_unit_line(rng, uid, 0, pos[uid], carry[uid]))
        for uid in opp_ids:
            unit_rows.append(_unit_line(rng, uid, 1, pos[uid], carry[uid]))
        body.append(str(len(unit_rows)))
        body.extend(unit_rows)

        # ---- commands of turn t ---------------------------------------
        parts = [_command(rng, uid, cells) for uid in own_ids]
        if rng.random() < 0.12:
            parts.append("TRAIN %d %d %d %d" % tuple(
                rng.randint(1, 3) for _ in range(4)))
        cmd_lines.append(";".join(parts))

        # ---- transition to S_{t+1} ------------------------------------
        for uid in list(pos):
            if rng.random() < 0.65:
                x, y = pos[uid]
                cand = [c for c in ((x + 1, y), (x - 1, y), (x, y + 1),
                                    (x, y - 1)) if c in set(cells)]
                if cand:
                    pos[uid] = rng.choice(cand)
            if rng.random() < 0.25:
                idx = rng.randrange(6)
                carry[uid] = list(carry[uid])
                carry[uid][idx] = max(0, carry[uid][idx]
                                      + rng.choice([-1, 1]))
        if rng.random() < 0.30:
            c = rng.choice(cells)
            live_plants[c] = _plant_line(rng, c)
        if live_plants and rng.random() < 0.15:
            live_plants.pop(rng.choice(sorted(live_plants)))
        for i in range(6):
            if rng.random() < 0.2:
                inv0[i] = max(0, inv0[i] + rng.choice([-1, 1]))
                inv1[i] = max(0, inv1[i] + rng.choice([-1, 1]))

    transcript = "\n".join(body) + "\n"
    commands = "\n".join(cmd_lines) + "\n"
    return td.build_trace(transcript, commands)


# ---------------------------------------------------------------------------
# Structured scenario families
#
# Purely random drift never produces a D-1 oscillation run, a D-2 door churn
# window, a D-3 shared-target run or a D-8 diagonal-mother chop, so those four
# detectors would have an all-zero pristine baseline and narrowing mutations on
# them could not be witnessed.  The families below are randomized SHAPES that
# reach those code paths.  They are authored here, from the protocol grammar
# and the detector docstrings' named quantities, not copied from
# ``test_trace_detectors.py``; their geometry, lengths, carries and opponents
# are all drawn per seed.
# ---------------------------------------------------------------------------

TENT = (4, 3)
DOORS = [(4, 2), (5, 3), (4, 4), (3, 3)]
DIAGS = [(3, 2), (5, 2), (3, 4), (5, 4)]


class _Builder:
    def __init__(self, map_rows):
        self.body = list(map_rows)
        self.cmds = []
        self.walkable = set(_walkable(map_rows))

    def turn(self, unit_rows, plant_rows, inv0, inv1, command):
        self.body.append(" ".join(str(v) for v in inv0))
        self.body.append(" ".join(str(v) for v in inv1))
        self.body.append(str(len(plant_rows)))
        self.body.extend(plant_rows)
        self.body.append(str(len(unit_rows)))
        self.body.extend(unit_rows)
        self.cmds.append(command)

    def finish(self):
        return td.build_trace("\n".join(self.body) + "\n",
                              "\n".join(self.cmds) + "\n")


def _u(uid, player, cell, speed=1, cap=2, hp=1, cp=1, carry=None):
    carry = carry or [0] * 6
    return " ".join(str(v) for v in
                    [uid, player, cell[0], cell[1], speed, cap, hp, cp]
                    + list(carry))


def _carry(**kw):
    c = [0] * 6
    for name, v in kw.items():
        c[td.ITEM_NAMES.index(name.upper())] = v
    return c


def _scen_osc(rng, map_rows):
    """A<->B alternation of randomized length, sometimes with a progress
    event injected (carry delta or a plant appearing under the unit)."""
    b = _Builder(map_rows)
    cells = sorted(b.walkable)
    a = rng.choice(cells)
    nbrs = [c for c in ((a[0] + 1, a[1]), (a[0] - 1, a[1]),
                        (a[0], a[1] + 1), (a[0], a[1] - 1))
            if c in b.walkable]
    if not nbrs:
        return None
    bb = rng.choice(nbrs)
    length = rng.randint(3, 15)
    inject = rng.random() < 0.4
    inject_at = rng.randint(2, max(2, length - 1))
    other = rng.choice(cells)
    for t in range(1, length + 1):
        here = a if t % 2 == 1 else bb
        nxt = bb if t % 2 == 1 else a
        carry = _carry(wood=1) if (inject and t >= inject_at) else [0] * 6
        rows = [_u(0, 0, here, carry=carry), _u(7, 1, other)]
        b.turn(rows, [], [0] * 6, [0] * 6, "MOVE 0 %d %d" % nxt)
    return b.finish()


def _scen_churn(rng, map_rows):
    """PICK/DROP cycles at a door (or, with probability, off-door) with a
    randomized number of cycles and a randomized net balance."""
    b = _Builder(map_rows)
    cell = rng.choice(DOORS) if rng.random() < 0.75 else rng.choice(
        sorted(b.walkable))
    if cell not in b.walkable:
        return None
    cycles = rng.randint(1, 4)
    inv = rng.randint(3, 8)
    leak = rng.random() < 0.3       # break net-zero on the last DROP
    seq = []
    for i in range(cycles):
        seq.append(("PICK 0 BANANA", 0, inv))
        seq.append(("DROP 0", 1, inv - 1))
        if i == cycles - 1 and leak:
            inv -= 1
    seq.append(("WAIT", 0, inv))
    other = rng.choice(sorted(b.walkable))
    for cmd, held, iv in seq:
        b.turn([_u(0, 0, cell, carry=_carry(banana=held)), _u(7, 1, other)],
               [], _carry(banana=iv), [0] * 6, cmd)
    return b.finish()


def _scen_contend(rng, map_rows):
    """Two own units sharing a MOVE target for a randomized run length, and
    (independently) one unit moving onto a stationary working peer's cell."""
    b = _Builder(map_rows)
    cells = sorted(b.walkable)
    target = rng.choice(cells)
    run = rng.randint(1, 4)
    total = run + rng.randint(1, 3)
    p0 = rng.choice(cells)
    p1 = rng.choice(cells)
    peer_mode = rng.random() < 0.5
    peer_cell = rng.choice(cells)
    for t in range(1, total + 1):
        if peer_mode:
            rows = [_u(0, 0, p0), _u(2, 0, peer_cell), _u(7, 1, p1)]
            cmd = "MOVE 0 %d %d;%s" % (peer_cell[0], peer_cell[1],
                                       rng.choice(["CHOP 2", "HARVEST 2",
                                                   "WAIT"]))
            p0 = peer_cell
        else:
            rows = [_u(0, 0, p0), _u(2, 0, p1), _u(7, 1, rng.choice(cells))]
            if t <= run:
                cmd = "MOVE 0 %d %d;MOVE 2 %d %d" % (target + target)
            else:
                alt = rng.choice(cells)
                cmd = "MOVE 0 %d %d;MOVE 2 %d %d" % (target + alt)
        b.turn(rows, [], [0] * 6, [0] * 6, cmd)
    return b.finish()


def _scen_ringplant(rng, map_rows):
    """PLANT on a ring cell (or off-ring) at a randomized turn, with a
    randomized opponent, then a randomized number of own CHOPs on it."""
    b = _Builder(map_rows)
    cells = sorted(b.walkable)
    ring = [c for c in DIAGS + DOORS if c in b.walkable]
    if not ring:
        return None
    cell = rng.choice(ring) if rng.random() < 0.7 else rng.choice(cells)
    opp = rng.choice(cells)
    ohp = rng.choice([0, 1])
    ocp = rng.choice([0, 1, 2])
    size = rng.randint(1, 4)
    health = 2 + size
    cd = rng.randint(0, 6)
    chops = rng.randint(0, 4)
    total = 2 + chops + rng.randint(0, 2)
    for t in range(1, total + 1):
        if t == 1:
            rows = [_u(0, 0, cell, carry=_carry(banana=1)),
                    _u(7, 1, opp, hp=ohp, cp=ocp)]
            b.turn(rows, [], [0] * 6, [0] * 6, "PLANT 0 BANANA")
            continue
        alive = health > 0
        prow = ["%s %d %d %d %d %d %d" % ("BANANA", cell[0], cell[1], size,
                                          health, 0, cd)] if alive else []
        rows = [_u(0, 0, cell), _u(7, 1, opp, hp=ohp, cp=ocp)]
        cmd = "CHOP 0" if (2 <= t <= 1 + chops and alive) else "WAIT"
        b.turn(rows, prow, [0] * 6, [0] * 6, cmd)
        if cmd == "CHOP 0":
            health -= 1
        if cd > 0:
            cd -= 1
        elif size < 4:
            size += 1
            health += 1
            cd = 6
    return b.finish()


def _scen_wood(rng, map_rows):
    """A wood carrier committing to a door and then progressing, stalling or
    retreating for a randomized number of turns, with a randomized DROP."""
    b = _Builder(map_rows)
    door = rng.choice(DOORS)
    if door not in b.walkable:
        return None
    cells = sorted(b.walkable)
    pos = rng.choice(cells)
    total = rng.randint(3, 9)
    drop_at = rng.randint(2, total) if rng.random() < 0.6 else None
    other = rng.choice(cells)
    dropped = False
    for t in range(1, total + 1):
        held = 0 if dropped else 1
        inv = _carry(wood=1) if dropped else [0] * 6
        rows = [_u(0, 0, pos, carry=_carry(wood=held)), _u(7, 1, other)]
        if t == 1:
            cmd = "MOVE 0 %d %d" % door
        elif drop_at is not None and t == drop_at and pos == door:
            cmd = "DROP 0"
        else:
            cmd = rng.choice(["MOVE 0 %d %d" % door, "CHOP 0", "WAIT",
                              "MOVE 0 %d %d" % rng.choice(cells)])
        b.turn(rows, [], inv, [0] * 6, cmd)
        if cmd == "DROP 0":
            dropped = True
        step = rng.random()
        nbrs = [c for c in ((pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]),
                            (pos[0], pos[1] + 1), (pos[0], pos[1] - 1))
                if c in b.walkable]
        if step < 0.55 and nbrs:
            pos = min(nbrs, key=lambda c: abs(c[0] - door[0])
                      + abs(c[1] - door[1]))
        elif step < 0.8 and nbrs:
            pos = rng.choice(nbrs)
    return b.finish()


def _scen_harvest(rng, map_rows):
    """HARVEST then a randomized disposal: DROP at a door with an inventory
    increase, DROP at a door without one, DROP off-door, PLANT, or nothing."""
    b = _Builder(map_rows)
    door = rng.choice(DOORS)
    cells = sorted(b.walkable)
    cell = door if rng.random() < 0.5 else rng.choice(cells)
    if cell not in b.walkable:
        return None
    mode = rng.choice(["bank", "refused", "plant", "hold", "drop_off"])
    total = rng.randint(3, 16)
    other = rng.choice(cells)
    inv = 0
    held = 0
    for t in range(1, total + 1):
        prow = ["BANANA %d %d 4 6 %d 3" % (cell[0], cell[1],
                                           1 if t == 1 else 0)]
        rows = [_u(0, 0, cell, carry=_carry(banana=held)), _u(7, 1, other)]
        if t == 1:
            cmd = "HARVEST 0"
            held_next = 1
            inv_next = inv
        elif t == 2 and mode != "hold":
            cmd = {"bank": "DROP 0", "refused": "DROP 0",
                   "plant": "PLANT 0 BANANA",
                   "drop_off": "DROP 0"}[mode]
            held_next = 0
            inv_next = inv + (1 if mode == "bank" else 0)
        else:
            cmd = "WAIT"
            held_next, inv_next = held, inv
        b.turn(rows, prow, _carry(banana=inv), [0] * 6, cmd)
        held, inv = held_next, inv_next
    return b.finish()


def _scen_train(rng, map_rows):
    """Banana commands around a randomized TRAIN turn and a randomized own
    unit count."""
    b = _Builder(map_rows)
    door = rng.choice(DOORS)
    cells = sorted(b.walkable)
    if door not in b.walkable:
        return None
    total = rng.randint(3, 8)
    train_at = rng.choice([None] + list(range(1, total + 1)))
    banana_at = rng.randint(1, total)
    second_from = rng.randint(1, total)
    other = rng.choice(cells)
    for t in range(1, total + 1):
        rows = [_u(0, 0, door, carry=_carry(banana=1))]
        if t >= second_from:
            rows.append(_u(2, 0, rng.choice(cells)))
        rows.append(_u(7, 1, other))
        parts = []
        if train_at == t:
            parts.append("TRAIN 1 1 1 1")
        if banana_at == t:
            parts.append(rng.choice(["PICK 0 BANANA", "PLANT 0 BANANA"]))
        if not parts:
            parts.append("WAIT")
        b.turn(rows, [], _carry(banana=3), [0] * 6, ";".join(parts))
    return b.finish()


SCENARIOS = [("osc", _scen_osc), ("churn", _scen_churn),
             ("contend", _scen_contend), ("ringplant", _scen_ringplant),
             ("wood", _scen_wood), ("harvest", _scen_harvest),
             ("train", _scen_train)]

SEEDS = list(range(1, 41))
SCENARIO_SEEDS = list(range(1, 25))
DETECTOR_NAMES = ["D-1", "D-2", "D-3", "D-4", "D-5", "D-6", "D-7", "D-8",
                  "D-9"]
_FNS = [td.detect_d1, td.detect_d2, td.detect_d3, td.detect_d4, td.detect_d5,
        td.detect_d6, td.detect_d7, td.detect_d8, td.detect_d9]


def _episode_signature(ep):
    """Order-independent, field-stable signature of one episode."""
    return sorted((k, json.dumps(v, sort_keys=True, default=str))
                  for k, v in ep.items())


def _corpus():
    """Yield (tag, trace) for every corpus member, in a fixed order."""
    for seed in SEEDS:
        for map_rows, mtag in ((MAP_A, "A"), (MAP_B, "B")):
            yield ("rand-%d-%s" % (seed, mtag), build_trace(seed, map_rows))
    for seed in SCENARIO_SEEDS:
        for fam, fn in SCENARIOS:
            for map_rows, mtag in ((MAP_A, "A"), (MAP_B, "B")):
                tr = fn(random.Random("%s-%d-%s" % (fam, seed, mtag)),
                        map_rows)
                if tr is not None:
                    yield ("%s-%d-%s" % (fam, seed, mtag), tr)


def digests(with_counts=False):
    """Return {detector_name: sha256-hex} over the whole corpus, plus a
    combined digest under key ``ALL`` (and, optionally, episode totals)."""
    per_det = {name: hashlib.sha256() for name in DETECTOR_NAMES}
    counts = {name: 0 for name in DETECTOR_NAMES}
    combined = hashlib.sha256()
    for tag, tr in _corpus():
        for name, fn in zip(DETECTOR_NAMES, _FNS):
            try:
                res = fn(tr)
                counts[name] += res["count"]
                payload = json.dumps(
                    {"verdict": res["verdict"], "count": res["count"],
                     "episodes": [_episode_signature(e)
                                  for e in res["episodes"]]},
                    sort_keys=True, default=str)
            except Exception as exc:            # a mutant may crash
                payload = "EXC:%s:%s" % (type(exc).__name__, exc)
            blob = ("%s|%s|%s" % (name, tag, payload)).encode()
            per_det[name].update(blob)
            combined.update(blob)
    out = {name: h.hexdigest() for name, h in per_det.items()}
    out["ALL"] = combined.hexdigest()
    if with_counts:
        out["_episode_totals"] = counts
    return out


def main():
    out = digests(with_counts="--counts" in sys.argv)
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
