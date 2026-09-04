"""Questions 3 and 4: the value of a planting turn on the same scale as a chopping turn.

Everything here is in **points per worker-turn** — the only scale on which a planner can compare
PLANT against CHOP against HARVEST, which is what the card's amendment asks for.  A banked fruit
is 1 point and a banked wood is 4 (`sim/engine.py`: score = sum(inv[0:4]) + 4*inv[WOOD]).

Rather than price the cycles on paper, each one is **driven through the referee** on a real panel
map and the turns and the score delta are read off the referee's own world.  `python3 value.py`
prints the cycle table, the orchard break-even and the champion baseline, and writes
results/value.json.

A cycle is one round trip by one worker from the shack door:

    CHOP    walk d, chop ceil(health/chop) turns, walk d, DROP     -> 4 * min(size, carry) points
    HARVEST walk d, HARVEST, walk d, DROP                          -> min(hp, carry, fruits) points
    PLANT   PICK, walk d, PLANT, walk d                            -> 0 points now; a tree later

The planting turn's value is the deferred one: a tree planted at turn t is, at the turn it is
felled, worth 4 * size * S (S the raid survival from `curve.survival`) minus the chop cycle that
fells it.  So the honest comparison is

    plant-turn value = (16 * S - chop cycle points forgone elsewhere) / (plant cycle turns)

and the break-even is the survival S at which a planting turn matches a chopping turn on the wild
forest that is already standing."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(HERE, "..", "opening-solver"))
sys.path.insert(0, HERE)

import world                                        # noqa: E402
import replay as rp                                 # noqa: E402
from sim.engine import step                         # noqa: E402
from kinetics import KINDS, eff_cd, health_full, chop_turns, size_at  # noqa: E402
from curve import survival, cells_by_distance, PANEL  # noqa: E402

WOOD_PTS = 4
WOOD_IDX = 5          # sim.engine.ITEM_INDEX: PLUM 0, LEMON 1, APPLE 2, BANANA 3, IRON 4, WOOD 5


def _path(m, a, b):
    """The cells a speed-1 unit walks from a to b, engine's own next_cell tie-break."""
    from sim.engine import next_cell
    cur, out = a, []
    while cur != b:
        cur = next_cell(m.walk | {m.shack}, cur, b, 1)
        out.append(cur)
    return out


def _fresh(item, seat=0):
    return rp.referee_state(item, seat)


def run_cycle(item, seat, cell, verb, kind=None, unit=(1, 1, 1, 1), seed_kind=None, max_turns=200):
    """Drive one worker from its shack through one cycle at `cell` and return (turns, points).

    verb 'CHOP'  : the tree at `cell` is felled and the wood banked.
    verb 'HARVEST': one HARVEST at `cell`, fruit banked.
    verb 'PLANT' : PICK a `seed_kind` seed, walk to `cell`, PLANT, walk back.  Points 0.
    """
    g = _fresh(item, seat)
    m = world.Map(item["rec"], seat)
    u = g.units[seat]
    u.ms, u.cc, u.hp, u.chop = unit
    g.inventories[seat] = [40, 40, 40, 40, 0, 0]
    score0 = sum(g.inventories[seat][0:4]) + WOOD_PTS * g.inventories[seat][WOOD_IDX]
    cmds, turns = [], 0

    def go(line):
        nonlocal turns
        step(g, [line], []) if seat == 0 else step(g, [], [line])
        turns += 1
        cmds.append(line)

    if verb == "PLANT":
        go(f"PICK {u.id} {seed_kind}")
    # out
    for nxt in _path(m, u.pos, cell):
        go(f"MOVE {u.id} {nxt[0]} {nxt[1]}")
        if turns > max_turns:
            return None
    if verb == "CHOP":
        while any(p.pos == cell for p in g.plants):
            go(f"CHOP {u.id}")
            if turns > max_turns:
                return None
    elif verb == "HARVEST":
        go(f"HARVEST {u.id}")
    elif verb == "PLANT":
        go(f"PLANT {u.id} {seed_kind}")
    # home
    home = min(m.doors, key=lambda d: m.d(cell, d))
    for nxt in _path(m, g.units[seat].pos, home):
        go(f"MOVE {u.id} {nxt[0]} {nxt[1]}")
    if verb != "PLANT":
        go(f"DROP {u.id}")
    inv = g.inventories[seat]
    pts = sum(inv[0:4]) + WOOD_PTS * inv[WOOD_IDX] - score0
    return turns, pts, cmds


def cycle_table(item, seat=0):
    """Referee-measured cycles on one seat, for each species and each chop power, at the nearest
    cell holding a mature tree we grow ourselves (so the size is 4 and the comparison is fair)."""
    m = world.Map(item["rec"], seat)
    t0 = {(t["x"], t["y"]) for t in item["rec"]["trees0"]}
    cells = cells_by_distance(m, t0)
    rows = []
    for kind in KINDS:
        for water_wanted in (True, False):
            pick = next(((dd, c) for dd, w, c in cells if (w == 0) == water_wanted), None)
            if pick is None:
                continue
            dd, cell = pick
            # plant it, let it mature, then measure the chop and harvest cycles on the referee
            g = _fresh(item, seat)
            u = g.units[seat]
            g.inventories[seat] = [40, 40, 40, 40, 0, 0]
            for nxt in _path(m, u.pos, cell):
                step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], [])
            u.carry[KINDS.index(kind)] = 1
            step(g, [f"PLANT {u.id} {kind}"], [])
            grow = 4 * eff_cd(kind, water_wanted) + 2
            for _ in range(grow):
                step(g, [f"WAIT {u.id}"], [])
            tree = next(p for p in g.plants if p.pos == cell)
            mature = (tree.size, tree.health, tree.fruits)
            for chop in (1, 2, 3):
                for cc in (1, 4):
                    r = _measure_on(item, seat, m, cell, kind, water_wanted, grow, "CHOP", (1, cc, 1, chop))
                    if r:
                        rows.append(dict(kind=kind, water=water_wanted, dd=dd, verb="CHOP", chop=chop, carry=cc,
                                         turns=r[0], points=r[1], per_turn=round(r[1] / r[0], 3), mature=mature))
            for hp in (1, 3):
                r = _measure_on(item, seat, m, cell, kind, water_wanted, grow + 4 * eff_cd(kind, water_wanted),
                                "HARVEST", (1, 3, hp, 1))
                if r:
                    rows.append(dict(kind=kind, water=water_wanted, dd=dd, verb="HARVEST", hp=hp, carry=3,
                                     turns=r[0], points=r[1], per_turn=round(r[1] / r[0], 3)))
            r = run_cycle(item, seat, cell, "PLANT", seed_kind=kind)
            if r:
                rows.append(dict(kind=kind, water=water_wanted, dd=dd, verb="PLANT", turns=r[0], points=r[1],
                                 per_turn=0.0))
    return rows


def _measure_on(item, seat, m, cell, kind, water, grow_turns, verb, unit):
    """Plant `kind` at `cell`, wait `grow_turns`, then measure one `verb` cycle with `unit`."""
    g = _fresh(item, seat)
    u = g.units[seat]
    u.ms, u.cc, u.hp, u.chop = unit
    g.inventories[seat] = [40, 40, 40, 40, 0, 0]
    for nxt in _path(m, u.pos, cell):
        step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], [])
    u.carry[KINDS.index(kind)] = 1
    step(g, [f"PLANT {u.id} {kind}"], [])
    for _ in range(grow_turns):
        step(g, [f"WAIT {u.id}"], [])
    # walk home so the cycle is measured from the door like every other cycle
    home = min(m.doors, key=lambda d: m.d(cell, d))
    for nxt in _path(m, u.pos, home):
        step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], [])
    step(g, [f"DROP {u.id}"], [])
    g.inventories[seat] = [40, 40, 40, 40, 0, 0]
    score0 = sum(g.inventories[seat][0:4]) + WOOD_PTS * g.inventories[seat][WOOD_IDX]
    turns = 0
    for nxt in _path(m, u.pos, cell):
        step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], []); turns += 1
    if verb == "CHOP":
        guard = 0
        while any(p.pos == cell for p in g.plants) and guard < 60:
            step(g, [f"CHOP {u.id}"], []); turns += 1; guard += 1
        if guard >= 60:
            return None
    else:
        step(g, [f"HARVEST {u.id}"], []); turns += 1
    for nxt in _path(m, u.pos, home):
        step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], []); turns += 1
    step(g, [f"DROP {u.id}"], []); turns += 1
    inv = g.inventories[seat]
    return turns, sum(inv[0:4]) + WOOD_PTS * inv[WOOD_IDX] - score0


def wild_chop_cycle(item, seat, chop=3, carry=4):
    """The referee-measured cycle for felling the NEAREST WILD tree — the thing a planting turn is
    actually competing with, since that tree is already standing and needs no growing."""
    m = world.Map(item["rec"], seat)
    trees = [(min(m.d(d, (t["x"], t["y"])) for d in m.doors), (t["x"], t["y"]), t["type"])
             for t in item["rec"]["trees0"] if (t["x"], t["y"]) in m.reach]
    if not trees:
        return None
    trees.sort()
    out = []
    for dd, cell, kind in trees[:5]:
        g = _fresh(item, seat)
        u = g.units[seat]
        u.ms, u.cc, u.hp, u.chop = 1, carry, 1, chop
        g.inventories[seat] = [40, 40, 40, 40, 0, 0]
        s0 = sum(g.inventories[seat][0:4])
        turns, guard = 0, 0
        for nxt in _path(m, u.pos, cell):
            step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], []); turns += 1
        while any(p.pos == cell for p in g.plants) and guard < 60:
            step(g, [f"CHOP {u.id}"], []); turns += 1; guard += 1
        home = min(m.doors, key=lambda d: m.d(cell, d))
        for nxt in _path(m, u.pos, home):
            step(g, [f"MOVE {u.id} {nxt[0]} {nxt[1]}"], []); turns += 1
        step(g, [f"DROP {u.id}"], []); turns += 1
        inv = g.inventories[seat]
        pts = sum(inv[0:4]) + WOOD_PTS * inv[WOOD_IDX] - s0
        out.append(dict(dd=dd, kind=kind, turns=turns, points=pts, per_turn=round(pts / turns, 3)))
    return out


def breakeven(rows, wild):
    """The raid survival S at which the whole plant->grow->fell chain matches one wild chop cycle.

    chain: PICK + 2*dd walking + PLANT  (the plant cycle, P turns, no points)
         + the chop cycle on our own mature tree (C turns, 16 points if it survives)
    wild : one chop cycle on a tree that is already standing (W turns, its own points).

    16*S/(P+C) = pts_wild/W   =>   S* = pts_wild*(P+C)/(16*W).  S* > 1 means a planting turn can
    never match a chopping turn while any wild tree still stands."""
    wbest = max(wild, key=lambda r: r["per_turn"])
    out = []
    for kind in KINDS:
        for water in (True, False):
            p = next((r for r in rows if r["kind"] == kind and r["water"] == water and r["verb"] == "PLANT"), None)
            c = next((r for r in rows if r["kind"] == kind and r["water"] == water and r["verb"] == "CHOP"
                      and r["chop"] == 3 and r["carry"] == 4), None)
            if not p or not c:
                continue
            chain_turns = p["turns"] + c["turns"]
            s_star = wbest["per_turn"] * chain_turns / c["points"] if c["points"] else None
            out.append(dict(kind=kind, water=water, plant_turns=p["turns"], chop_turns=c["turns"],
                            chain_turns=chain_turns, chain_points_if_survives=c["points"],
                            chain_per_turn_S1=round(c["points"] / chain_turns, 3),
                            wild_per_turn=wbest["per_turn"], S_star=round(s_star, 3) if s_star else None,
                            reachable=(s_star is not None and s_star <= 1.0)))
    return out


def orchard_budget(item, seat, kind, k, t0=2, chop=3, carry=4, fell_at=None):
    """Question 4, on one seat: plant k trees of `kind` from turn t0 with the starter, fell them
    all from turn `fell_at` with one chop-`chop` worker, and price the whole programme in
    points and in worker-turns against spending the same turns felling wild trees."""
    from curve import schedule
    m = world.Map(item["rec"], seat)
    t0cells = {(t["x"], t["y"]) for t in item["rec"]["trees0"]}
    cells = cells_by_distance(m, t0cells)
    plan = schedule(cells, k, t0)
    if len(plan) < k:
        return None
    plant_turns = plan[-1][0] + plan[-1][1] - t0        # starter turns consumed, PICK..walk home
    fell_at = fell_at or 200
    ch = chop_turns(kind, chop)
    pts, fell_turns, felled = 0.0, 0, 0.0
    t = fell_at
    for t_i, dd, water, _ in sorted(plan, key=lambda p: p[1]):
        cycle = 2 * dd + ch + 1
        size = size_at(kind, water, t - t_i)
        if size <= 0:
            continue
        s = survival(dd, t_i, t)
        pts += WOOD_PTS * min(size, carry) * s
        fell_turns += cycle
        felled += s
        t += cycle
        if t > 300:
            break
    return dict(kind=kind, k=k, last_plant_turn=plan[-1][0], plant_turns=plant_turns,
                fell_from=fell_at, fell_turns=fell_turns, trees_felled_expected=round(felled, 2),
                points=round(pts, 1), total_turns=plant_turns + fell_turns,
                per_turn=round(pts / (plant_turns + fell_turns), 3))


def main():
    items = world.load_panel(PANEL)
    item, seat = items[0], 0
    rows = cycle_table(item, seat)
    wild = wild_chop_cycle(item, seat)
    be = breakeven(rows, wild)

    print("== referee-measured cycles, one worker from the shack door (points per worker-turn) ==")
    for r in rows:
        tag = f"{r['kind']:>6} {'water' if r['water'] else 'inland':>6} dd{r['dd']}"
        if r["verb"] == "CHOP":
            print(f"{tag}  CHOP    chop{r['chop']} carry{r['carry']}  {r['turns']:>3} turns  {r['points']:>3} pts  {r['per_turn']:.2f}/turn")
        elif r["verb"] == "HARVEST":
            print(f"{tag}  HARVEST hp{r['hp']}            {r['turns']:>3} turns  {r['points']:>3} pts  {r['per_turn']:.2f}/turn")
        else:
            print(f"{tag}  PLANT                    {r['turns']:>3} turns  {r['points']:>3} pts  (deferred)")

    print("\n== the wild tree a planting turn competes with (chop 3, carry 4) ==")
    for r in wild:
        print(f"  dd{r['dd']} {r['kind']:>6}: {r['turns']} turns, {r['points']} pts, {r['per_turn']:.2f}/turn")

    print("\n== break-even: the raid survival S at which planting matches chopping what stands ==")
    for r in be:
        print(f"  {r['kind']:>6} {'water' if r['water'] else 'inland':>6}: chain {r['plant_turns']}+{r['chop_turns']}={r['chain_turns']} turns for "
              f"{r['chain_points_if_survives']} pts ({r['chain_per_turn_S1']:.2f}/turn at S=1) vs wild {r['wild_per_turn']:.2f}/turn -> "
              f"S* = {r['S_star']}  {'REACHABLE' if r['reachable'] else 'IMPOSSIBLE (S*>1)'}")

    print("\n== question 4: the whole programme on 20 seats, plant k then fell from turn 200 ==")
    prog = []
    for kind in ("BANANA", "PLUM", "APPLE"):
        for k in (5, 10, 20, 30):
            xs = [orchard_budget(it, s, kind, k) for it in items[:10] for s in (0, 1)]
            xs = [x for x in xs if x]
            if not xs:
                continue
            import statistics as st
            row = dict(kind=kind, k=k,
                       plant_turns=st.median(x["plant_turns"] for x in xs),
                       fell_turns=st.median(x["fell_turns"] for x in xs),
                       points=round(st.median(x["points"] for x in xs), 1),
                       per_turn=round(st.median(x["per_turn"] for x in xs), 3),
                       trees_felled=round(st.median(x["trees_felled_expected"] for x in xs), 2))
            prog.append(row)
            print(f"  {kind:>6} k={k:<3} plant {row['plant_turns']:>4.0f} turns + fell {row['fell_turns']:>4.0f} turns -> "
                  f"{row['points']:>6.1f} pts ({row['trees_felled']:.1f} trees survive)  {row['per_turn']:.2f}/turn")

    wbest = max(wild, key=lambda r: r["per_turn"])["per_turn"]
    champ = dict(trees=9.8, top4_trees=29.0)
    for name, n in (("champion_unaided", 9.8), ("top4_ceiling", 29.0)):
        b = next(r for r in prog if r["kind"] == "PLUM" and r["k"] == 10)
        champ[name + "_wood_points_if_all_felled"] = round(n * 16, 1)
        champ[name + "_wood_points_raided_to_200"] = round(n * 16 * survival(2, 40, 200), 1)
    print(f"\n== champion baseline on the same scale ==")
    print(f"  the champion's unaided 9.8 trees: {champ['champion_unaided_wood_points_if_all_felled']} pts of standing wood if every one is felled, "
          f"{champ['champion_unaided_wood_points_raided_to_200']} pts after raids to turn 200")
    print(f"  the top four's ~29 trees:         {champ['top4_ceiling_wood_points_if_all_felled']} pts, "
          f"{champ['top4_ceiling_wood_points_raided_to_200']} pts after raids to turn 200")
    print(f"  best wild chop cycle on this seat: {wbest:.2f} points per worker-turn")

    json.dump(dict(cycles=rows, wild=wild, breakeven=be, programme=prog, champion=champ),
              open(os.path.join(HERE, "results", "value.json"), "w"), indent=1)


if __name__ == "__main__":
    main()


def panel_breakeven(items, n_seats=40, chop=3, carry=4):
    """The one number the read turns on, over many map-seats rather than one: the best wild chop
    cycle available to a chop-3 carry-4 worker, against the plant->grow->fell chain on our own
    tree at the same worker, at raid survival S=1 and at the survival the record measures."""
    import statistics as st
    rows = []
    for it in items[:n_seats // 2]:
        for seat in (0, 1):
            w = wild_chop_cycle(it, seat, chop, carry)
            if not w:
                continue
            best = max(r["per_turn"] for r in w)
            m = world.Map(it["rec"], seat)
            t0 = {(t["x"], t["y"]) for t in it["rec"]["trees0"]}
            cells = cells_by_distance(m, t0)
            dd = cells[0][0] if cells else 1
            chain = {}
            for kind in KINDS:
                ct = chop_turns(kind, chop)
                chain_turns = (2 * dd + 2) + (2 * dd + ct + 1)   # plant cycle + chop cycle
                chain[kind] = dict(turns=chain_turns, per_turn_S1=round(16.0 / chain_turns, 3))
            rows.append(dict(seat=seat, best_wild_per_turn=best, nearest_free_dd=dd, chain=chain,
                             n_wild_reachable=sum(1 for t in it["rec"]["trees0"] if (t["x"], t["y"]) in m.reach)))
    out = dict(n=len(rows), best_wild_per_turn=dict(
        median=round(st.median(r["best_wild_per_turn"] for r in rows), 3),
        min=round(min(r["best_wild_per_turn"] for r in rows), 3),
        max=round(max(r["best_wild_per_turn"] for r in rows), 3)))
    for kind in KINDS:
        pts = [r["chain"][kind]["per_turn_S1"] for r in rows]
        ratio = [r["chain"][kind]["per_turn_S1"] / r["best_wild_per_turn"] for r in rows]
        out[kind] = dict(chain_per_turn_S1=dict(median=round(st.median(pts), 3), min=round(min(pts), 3), max=round(max(pts), 3)),
                         S_star=dict(median=round(st.median(1.0 / r for r in ratio), 3),
                                     min=round(min(1.0 / r for r in ratio), 3),
                                     max=round(max(1.0 / r for r in ratio), 3)),
                         seats_where_S_star_le_1=sum(1 for r in ratio if 1.0 / r <= 1.0))
    return out


def fell_on_maturity(items, n_seats=40, chop=3, carry=4, t_plant=10):
    """The fairest case for the orchard: plant at `t_plant` and fell the moment the tree is full,
    so the raid hazard only runs over the growing window instead of to the end of the game.

    This is the number the read turns on, because the standing-wood curve in curve.json prices an
    orchard that is LEFT standing, and an orchard that is left standing is mostly raided away."""
    import statistics as st
    from kinetics import full_at
    rows = []
    for it in items[:n_seats // 2]:
        for seat in (0, 1):
            w = wild_chop_cycle(it, seat, chop, carry)
            if not w:
                continue
            best = max(r["per_turn"] for r in w)
            m = world.Map(it["rec"], seat)
            t0 = {(t["x"], t["y"]) for t in it["rec"]["trees0"]}
            cells = cells_by_distance(m, t0)
            if not cells:
                continue
            dd, wflag, _ = cells[0]
            water = (wflag == 0)
            r = dict(seat=seat, dd=dd, water=water, best_wild_per_turn=best)
            for kind in KINDS:
                ct = chop_turns(kind, chop)
                grow = full_at(kind, water)
                turns = (2 * dd + 2) + (2 * dd + ct + 1)
                t_fell = t_plant + max(grow, 2 * dd + 2)
                s = survival(dd, t_plant, t_fell)
                r[kind] = dict(grow=grow, t_fell=t_fell, S=round(s, 4), turns=turns,
                               per_turn=round(16.0 * s / turns, 3),
                               vs_wild=round((16.0 * s / turns) / best, 3))
            rows.append(r)
    out = dict(n=len(rows), t_plant=t_plant,
               best_wild_per_turn_median=round(st.median(r["best_wild_per_turn"] for r in rows), 3))
    for kind in KINDS:
        out[kind] = dict(S_median=round(st.median(r[kind]["S"] for r in rows), 4),
                         per_turn_median=round(st.median(r[kind]["per_turn"] for r in rows), 3),
                         vs_wild_median=round(st.median(r[kind]["vs_wild"] for r in rows), 3),
                         seats_beating_wild=sum(1 for r in rows if r[kind]["vs_wild"] >= 1.0))
    return out


def cycle_by_distance(items, seat=0, chop=3, carry=4, kinds=("BANANA", "PLUM", "APPLE")):
    """The referee-measured chop cycle as a function of door-distance, which is the axis the
    forest census turns on: at turn 108 the surviving wild trees sit at median door-distance 13
    while an orchard sits at 1 or 2, and the cycle's points per turn is what that costs."""
    item = items[0]
    m = world.Map(item["rec"], seat)
    t0 = {(t["x"], t["y"]) for t in item["rec"]["trees0"]}
    cells = cells_by_distance(m, t0)
    out = []
    for want in (1, 2, 4, 8, 12, 16):
        pick = next(((dd, w, c) for dd, w, c in cells if dd >= want), None)
        if pick is None:
            continue
        dd, wflag, cell = pick
        for kind in kinds:
            grow = 4 * eff_cd(kind, wflag == 0) + 2
            r = _measure_on(item, seat, m, cell, kind, wflag == 0, grow, "CHOP", (1, carry, 1, chop))
            if r:
                out.append(dict(dd=dd, kind=kind, turns=r[0], points=r[1], per_turn=round(r[1] / r[0], 3)))
    return out
