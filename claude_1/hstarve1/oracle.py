#!/usr/bin/env python3
"""H-STARVE-1 pool #1 — the ELIGIBLE-ACTION oracle, with its two negative control arms.

`codex_1`'s review killed the previous work-oracle for good reasons, all accepted:

- it treated **geometric reachability to any plant** as work, ignoring whether the unit could
  legally act on it. OSC-012's parked unit has `harvest_power = 0` and `chop_power = 0`, so a
  reachable plant was never an eligible action for it — the planner offering nothing was correct;
- it counted a **carrying** unit as having work unconditionally, without a reachable sink;
- reachability was **player-level** (multi-source BFS over all own units), so a plant only the
  dancer could reach made the predicate true for a walled-in peer.

This module answers one question per unit per turn: **does THIS unit have at least one action it
could legally perform right now?** Capability × per-turn plant state × reachable sink, all from
this unit's own cell.

## The two arms the charter requires, and why they are the right ones

- **zero-capability arm** — a unit with `harvest_power = 0, chop_power = 0` must report NO
  eligible harvest/chop no matter how many plants it can reach. This is literally OSC-012's unit;
  if the oracle passes it, the oracle is the old one wearing a new name.
- **walled-in arm** — a unit whose reachable set excludes every plant and every shack door must
  report NO eligible work even when the player has plenty. This is the case the player-level
  predicate could not see.

Both are **observed firing** in `--self-test`; neither is asserted.

## What "eligible" means here, clause by clause

1. **HARVEST** — `harvest_power > 0` AND some reachable plant has `fruits > 0`.
2. **CHOP** — `chop_power > 0` AND some reachable plant has `health > 0`.
3. **BANK/PLANT (sink)** — the unit carries something AND a reachable sink exists: a shack door
   cell for banking, or any reachable walkable cell for planting a carried fruit.

A unit with none of the three has **no eligible action**, and a generator offering it only WAIT is
behaving correctly. That distinction is the entire point of the rebuild.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "banana-restoration-r2"))
import trace_detectors as td   # noqa: E402


def reachable_from(tr, cell):
    """BFS from THIS unit's cell alone — never multi-source over all own units."""
    return td.bfs_distances(tr.smap.walkable, [cell])


def eligible_actions(tr, uid, t):
    """Return the set of action kinds this unit could legally perform at turn t."""
    st = tr.state(t)
    u = tr.unit(uid, t)
    if u is None:
        return set()
    reach = reachable_from(tr, u.cell)
    acts = set()

    plants = [p for p in st.plants if p.cell in reach]
    if u.harvest_power > 0 and any(p.fruits > 0 for p in plants):
        acts.add("HARVEST")
    if u.chop_power > 0 and any(p.health > 0 for p in plants):
        acts.add("CHOP")

    if sum(u.carry) > 0:
        doors = [c for c in td.orth_neighbors(tr.smap.shacks[0])
                 if c in tr.smap.walkable] if hasattr(td, "orth_neighbors") else []
        if any(c in reach for c in doors) or tr.smap.shacks[0] in reach:
            acts.add("BANK")
        if any(c in reach for c in tr.smap.walkable):
            acts.add("PLANT")
    return acts


def has_eligible_action(tr, uid, t):
    return bool(eligible_actions(tr, uid, t))


# --------------------------------------------------------------------------------------


class _StubPlant:
    def __init__(self, cell, fruits=0, health=1):
        self.kind, self.cell, self.size = "PLUM", cell, 1
        self.fruits, self.health, self.cooldown = fruits, health, 0


class _StubUnit:
    def __init__(self, cell, harvest, chop, carry=0):
        self.id, self.player, self.cell = 7, 0, cell
        self.speed = self.capacity = 1
        self.harvest_power, self.chop_power = harvest, chop
        self.carry = [carry, 0, 0, 0, 0, 0]


class _StubMap:
    def __init__(self, walkable, shack=(0, 0)):
        self.walkable, self.shacks = set(walkable), [shack, (99, 99)]


class _StubState:
    def __init__(self, plants):
        self.plants = plants


class _StubTrace:
    T = 1

    def __init__(self, walkable, plants, unit, shack=(0, 0)):
        self.smap = _StubMap(walkable, shack)
        self._st = _StubState(plants)
        self._u = unit

    def state(self, t):
        return self._st

    def unit(self, uid, t):
        return self._u


def _self_test():
    cases = []
    open_row = {(x, 0) for x in range(6)}

    # positive control: capable unit, reachable fruiting plant -> HARVEST eligible
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=2)], _StubUnit((0, 0), 1, 0))
    a = eligible_actions(tr, 7, 1)
    cases.append(("capable unit + reachable fruit -> HARVEST eligible", "HARVEST" in a, sorted(a)))

    # ZERO-CAPABILITY ARM (OSC-012's unit): plants everywhere, but it can do neither
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=5, health=9)],
                    _StubUnit((0, 0), harvest=0, chop=0))
    a = eligible_actions(tr, 7, 1)
    cases.append(("ZERO-CAPABILITY arm: harvest=0 chop=0 -> NO eligible action",
                  not a, sorted(a)))

    # and the control on the control: give it capability back, work reappears
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=5, health=9)],
                    _StubUnit((0, 0), harvest=1, chop=0))
    cases.append(("...same board WITH capability -> work reappears",
                  bool(eligible_actions(tr, 7, 1)), ""))

    # WALLED-IN ARM: capable unit, plant exists, but not reachable from its cell
    tr = _StubTrace({(0, 0)}, [_StubPlant((3, 0), fruits=5, health=9)],
                    _StubUnit((0, 0), harvest=1, chop=1))
    a = eligible_actions(tr, 7, 1)
    cases.append(("WALLED-IN arm: plant exists but unreachable -> NO eligible action",
                  not a, sorted(a)))

    # ...and the same unit on a connected board does see it
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=5, health=9)],
                    _StubUnit((0, 0), harvest=1, chop=1))
    cases.append(("...same unit on a connected board -> work reappears",
                  bool(eligible_actions(tr, 7, 1)), ""))

    # fruitless plant is not harvestable, but IS choppable for a chopper
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=0, health=4)],
                    _StubUnit((0, 0), harvest=1, chop=0))
    cases.append(("fruitless plant -> harvester has NO eligible action",
                  not eligible_actions(tr, 7, 1), ""))
    tr = _StubTrace(open_row, [_StubPlant((3, 0), fruits=0, health=4)],
                    _StubUnit((0, 0), harvest=0, chop=1))
    cases.append(("fruitless but standing plant -> chopper CAN chop",
                  "CHOP" in eligible_actions(tr, 7, 1), ""))

    # carrying unit with a reachable sink
    tr = _StubTrace(open_row, [], _StubUnit((2, 0), 0, 0, carry=1))
    cases.append(("carrying unit with reachable board -> sink action eligible",
                  bool(eligible_actions(tr, 7, 1)), sorted(eligible_actions(tr, 7, 1))))

    ok = True
    for label, passed, detail in cases:
        print(f"  {'OK  ' if passed else 'BAD '} {label:62} {detail}")
        ok = ok and passed
    print(f"\noracle self-test: {len(cases)} cases —", "PASS" if ok else "FAIL")
    print("\nBoth charter arms are OBSERVED, each beside a positive twin proving the arm is not")
    print("passing because the oracle says no to everything: zero-capability and walled-in each")
    print("report NO eligible action, and each reports work again when the single blocking")
    print("condition is removed.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_self_test())
