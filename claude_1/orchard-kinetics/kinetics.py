"""One tree's kinetics from the referee's constants, checked against `sim/engine.py` by planting.

A seed planted on turn t (the PLANT resolves in phase 3, the tick at the end of the same turn):
the tick sees cd 0 and health > 0, so the tree is size 1 the turn it is planted, with cooldown
`eff_cd` (PLANT_COOLDOWN minus the water boost when an orthogonal neighbour is water).  Each
further `eff_cd` ticks add one size up to 4 (each adding the kind's health slope), then one fruit
up to 3.  Felling: CHOP takes `chop` health a turn; at health 0 the tree yields its size in wood
(4 at full size), 4 points a unit.  A harvested fruit on a full tree regrows after one cooldown.

    kind    eff_cd inland/water   full size at   health at full   first fruit at
    PLUM      8 / 3               t+24 / t+9         12            t+32 / t+12
    LEMON     8 / 3               t+24 / t+9         12            t+32 / t+12
    APPLE     9 / 2               t+27 / t+6         20            t+36 / t+8
    BANANA    6 / 4               t+18 / t+12         6            t+24 / t+16

`python3 kinetics.py` prints the table and asserts it against the referee on a panel map."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "opening-solver"))
from world import PLANT_COOLDOWN, WATER_BOOST, HEALTH_BASE, HEALTH_SLOPE, MAX_SIZE, MAX_FRUITS, WOOD_POINTS  # noqa: E402

KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")


def eff_cd(kind, water):
    return PLANT_COOLDOWN[kind] - (WATER_BOOST[kind] if water else 0)


def timeline(kind, water, horizon=320):
    """(size, health, fruits) at the START of turn t+dt for dt = 0..horizon, a seed planted on
    turn t and never touched.  dt = 0 is the state before the planting turn's tick (no tree)."""
    cd = eff_cd(kind, water)
    size, health, fruits, cool = 0, HEALTH_BASE[kind], 0, 0
    out = [(0, 0, 0)]
    for _ in range(horizon):
        if cool > 0:
            cool -= 1
        if cool == 0:
            if size < MAX_SIZE:
                size += 1
                health += HEALTH_SLOPE[kind]
                cool = cd
            elif fruits < MAX_FRUITS:
                fruits += 1
                cool = cd
        out.append((size, health, fruits))
    return out


def full_at(kind, water):
    """Turns after planting until size 4 (wood 4)."""
    return 3 * eff_cd(kind, water)


def first_fruit_at(kind, water):
    return 4 * eff_cd(kind, water)


def health_full(kind):
    return HEALTH_BASE[kind] + HEALTH_SLOPE[kind] * MAX_SIZE


def chop_turns(kind, chop, size=MAX_SIZE):
    """CHOP turns to fell a tree of `size` with one troll of chop power `chop`."""
    h = HEALTH_BASE[kind] + HEALTH_SLOPE[kind] * size
    return -(-h // chop)


def size_at(kind, water, dt):
    return min(MAX_SIZE, 1 + dt // eff_cd(kind, water)) if dt >= 0 else 0


def table():
    rows = []
    for k in KINDS:
        for w in (False, True):
            rows.append(dict(kind=k, water=w, eff_cd=eff_cd(k, w), full_at=full_at(k, w),
                             first_fruit_at=first_fruit_at(k, w), health_full=health_full(k),
                             chop_turns={c: chop_turns(k, c) for c in (1, 2, 3)},
                             wood_per_chop_turn={c: round(MAX_SIZE / chop_turns(k, c), 2) for c in (1, 2, 3)}))
    return rows


def check_against_referee():
    """Plant every kind on a water cell and an inland cell of a panel map through sim/engine.py
    and compare the referee's tree after every tick with `timeline`."""
    ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
    sys.path.insert(0, ROOT)
    import json
    from sim.engine import step
    sys.path.insert(0, os.path.join(HERE, "..", "opening-solver"))
    import replay
    items = [json.loads(l) for l in open(os.path.join(HERE, "..", "h2h-panel", "panel-200-seed1.jsonl")) if l.strip()]
    item = items[0]
    g = replay.referee_state(item, 0)
    # a walkable cell next to water and one not, both empty
    plant_cells = {p.pos for p in g.plants}
    water_cell = next(c for c in sorted(g.walkable) if c not in plant_cells and any((c[0] + dx, c[1] + dy) in g.water for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))))
    inland_cell = next(c for c in sorted(g.walkable) if c not in plant_cells and not any((c[0] + dx, c[1] + dy) in g.water for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))))
    checked = 0
    for kind in KINDS:
        for cell, water in ((water_cell, True), (inland_cell, False)):
            gg = replay.referee_state(item, 0)
            gg.inventories[0] = [10, 10, 10, 10, 10, 0]
            u = gg.units[0]
            u.x, u.y = cell
            u.carry = [0] * 6
            u.carry[KINDS.index(kind)] = 1
            step(gg, [f"PLANT 0 {kind}"], [])
            tl = timeline(kind, water, 120)
            for dt in range(1, 121):
                p = next(p for p in gg.plants if p.pos == cell)
                assert (p.size, p.health, p.fruits) == tl[dt], (kind, water, dt, (p.size, p.health, p.fruits), tl[dt])
                step(gg, ["WAIT 0"], [])
            checked += 1
    return checked


if __name__ == "__main__":
    for r in table():
        print(f"{r['kind']:>6} {'water' if r['water'] else 'inland':>6}: cd {r['eff_cd']}  full at +{r['full_at']:>2}  first fruit +{r['first_fruit_at']:>2}  "
              f"health {r['health_full']:>2}  chop turns c1/c2/c3 {r['chop_turns'][1]}/{r['chop_turns'][2]}/{r['chop_turns'][3]}  "
              f"wood per chop-turn {r['wood_per_chop_turn'][1]}/{r['wood_per_chop_turn'][2]}/{r['wood_per_chop_turn'][3]}")
    n = check_against_referee()
    print(f"referee check: {n} kind x cell timelines agree tick by tick over 120 turns")
