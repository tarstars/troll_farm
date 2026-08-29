#!/usr/bin/env python3
"""Rule fits over the decision tables (W4).  python3 fit_rules.py <player> [aspect...]

Aspects: chop, train, plant, harvest, endgame, roles.  Each prints descriptive
statistics and the accuracy of every candidate rule (share of decisions whose
actual target is in the rule's argmax set; the tie rate is reported alongside).
"""
from __future__ import annotations

import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLES = HERE / "tables"
KIND = {"P": "PLUM", "L": "LEMON", "A": "APPLE", "B": "BANANA"}
HEALTH_BASE = {"P": 4, "L": 4, "A": 8, "B": 2}
HEALTH_SLOPE = {"P": 2, "L": 2, "A": 3, "B": 1}
# candidate column layout (decision_tables.py)
X, Y, K, SIZE, FRUITS, HEALTH, CD, D_UNIT, D_OWN, D_OPP, WATER, PLANTER, OCC_OWN, OCC_OPP = range(14)


def load(player, kind):
    with gzip.open(TABLES / f"{player}_{kind}.jsonl.gz", "rt") as f:
        return [json.loads(l) for l in f]


def ceil_div(a, b):
    return -(-a // b)


def argmax_set(cands, key):
    best, out = None, []
    for c in cands:
        v = key(c)
        if v is None:
            continue
        if best is None or v > best + 1e-12:
            best, out = v, [c]
        elif abs(v - best) <= 1e-12:
            out.append(c)
    return out


def score_rules(rows, rules, cand_filter, label, top_examples=3):
    """rows: trips; rules: name -> key(row, cand) returning a number (higher = better)."""
    print(f"\n== {label}: {len(rows)} decisions ==")
    res = {}
    for name, key in rules.items():
        hit = ties = n = 0
        expected = 0.0
        misses = []
        for r in rows:
            cands = [c for c in r["cands"] if cand_filter(r, c)]
            if not cands:
                continue
            n += 1
            best = argmax_set(cands, lambda c: key(r, c))
            if any((c[X], c[Y]) == tuple(r["dest"]) for c in best):
                hit += 1
                expected += 1.0 / len(best)
                if len(best) > 1:
                    ties += 1
            elif len(misses) < top_examples:
                chosen = next((c for c in cands if (c[X], c[Y]) == tuple(r["dest"])), None)
                misses.append((r["g"], r["s"], r["u"], "chose", chosen, "rule", best[0]))
        res[name] = (hit, n, ties, round(expected, 1))
        print(f"  {name:58s} {hit:5d}/{n:5d} = {100*hit/max(n,1):5.1f}%  (ties among hits {ties}; expected with random tie-break {100*expected/max(n,1):5.1f}%)")
        for m in misses:
            print("        miss:", m)
    return res


# ---------------------------------------------------------------- chop -----
def chop_value_champion(r, c):
    """Our champion's chop value: min(final size, free carry) * 1000 / (travel + chop turns + return + 1)."""
    ms, cc, hp, chop = r["tal"]
    free = cc - sum(r["carry_s"])
    if chop <= 0 or c[D_UNIT] < 0:
        return None
    travel = ceil_div(c[D_UNIT], ms)
    chops = ceil_div(c[HEALTH], chop)
    ret = ceil_div(c[D_OWN], ms)
    wood = min(c[SIZE], max(free, 0))
    return wood * 1000.0 / (travel + chops + ret + 1)


def chop_rules(r_free_aware=True):
    def wood(r, c):
        ms, cc, hp, chop = r["tal"]
        free = cc - sum(r["carry_s"])
        return min(c[SIZE], max(free, 0)) if r_free_aware else c[SIZE]

    def travel(r, c):
        return ceil_div(c[D_UNIT], r["tal"][0])

    def chops(r, c):
        return ceil_div(c[HEALTH], max(r["tal"][3], 1))

    def ret(r, c):
        return ceil_div(c[D_OWN], r["tal"][0])

    return {
        "nearest tree (BFS from unit)": lambda r, c: -c[D_UNIT] if c[D_UNIT] >= 0 else None,
        "nearest tree, ties -> bigger": lambda r, c: -c[D_UNIT] + 0.01 * c[SIZE] if c[D_UNIT] >= 0 else None,
        "champion value: wood/(travel+chops+return+1)": chop_value_champion,
        "wood/(travel+chops)": lambda r, c: wood(r, c) / (travel(r, c) + chops(r, c)) if c[D_UNIT] >= 0 else None,
        "wood/(travel+chops+1)": lambda r, c: wood(r, c) / (travel(r, c) + chops(r, c) + 1) if c[D_UNIT] >= 0 else None,
        "size/(travel+chops+return)": lambda r, c: c[SIZE] / max(travel(r, c) + chops(r, c) + ret(r, c), 1) if c[D_UNIT] >= 0 else None,
        "size/(travel+chops)": lambda r, c: c[SIZE] / max(travel(r, c) + chops(r, c), 1) if c[D_UNIT] >= 0 else None,
        "size/travel(+1)": lambda r, c: c[SIZE] / (travel(r, c) + 1) if c[D_UNIT] >= 0 else None,
        "biggest tree, ties -> nearest": lambda r, c: c[SIZE] - 0.01 * c[D_UNIT] if c[D_UNIT] >= 0 else None,
        "fewest chop turns, ties -> nearest": lambda r, c: -chops(r, c) - 0.01 * c[D_UNIT] if c[D_UNIT] >= 0 else None,
        "min (travel + chops)": lambda r, c: -(travel(r, c) + chops(r, c)) if c[D_UNIT] >= 0 else None,
        "min (travel + chops + return)": lambda r, c: -(travel(r, c) + chops(r, c) + ret(r, c)) if c[D_UNIT] >= 0 else None,
        "closest to own shack": lambda r, c: -c[D_OWN] if c[D_OWN] >= 0 else None,
        "closest to opponent shack": lambda r, c: -c[D_OPP] if c[D_OPP] >= 0 else None,
        "nearest non-own-planted tree": lambda r, c: (-c[D_UNIT] if c[PLANTER] != r["seat"] else -999) if c[D_UNIT] >= 0 else None,
        "nearest fruitless tree (fruits==0)": lambda r, c: (-c[D_UNIT] if c[FRUITS] == 0 else -999) if c[D_UNIT] >= 0 else None,
        "nearest full-size (4) tree": lambda r, c: (-c[D_UNIT] if c[SIZE] == 4 else -999) if c[D_UNIT] >= 0 else None,
        "nearest tree within 2 of the opponent shack (else nearest)": lambda r, c: (-c[D_UNIT] + (100 if c[D_OPP] <= 2 else 0)) if c[D_UNIT] >= 0 else None,
        "nearest opponent-planted tree (else nearest)": lambda r, c: (-c[D_UNIT] + (100 if c[PLANTER] == 1 - r["seat"] else 0)) if c[D_UNIT] >= 0 else None,
        "nearest tree on the opponent half (else nearest)": lambda r, c: (-c[D_UNIT] + (100 if c[D_OPP] < c[D_OWN] else 0)) if c[D_UNIT] >= 0 else None,
        "wood/(travel+chops), opp-half trees x2": lambda r, c: wood(r, c) * (2 if c[D_OPP] < c[D_OWN] else 1) / (travel(r, c) + chops(r, c)) if c[D_UNIT] >= 0 else None,
        "wood/(travel+chops) + denial: (size+fruits)/(travel+chops) for opp-half trees": lambda r, c: ((wood(r, c) + (c[SIZE] + c[FRUITS] if c[D_OPP] < c[D_OWN] else 0)) / (travel(r, c) + chops(r, c))) if c[D_UNIT] >= 0 else None,
        "min d_opp, ties -> nearest": lambda r, c: -c[D_OPP] - 0.01 * c[D_UNIT] if c[D_UNIT] >= 0 else None,
    }


def describe_chop(rows):
    print("\n-- descriptive: chop targets --")
    cnt = Counter()
    rank_d = Counter()
    kinds = Counter()
    sizes = Counter()
    fr = Counter()
    planter = Counter()
    half = Counter()
    dist = Counter()
    for r in rows:
        chosen = next((c for c in r["cands"] if (c[X], c[Y]) == tuple(r["dest"])), None)
        if chosen is None:
            cnt["dest not a tree at start"] += 1
            continue
        ds = sorted(c[D_UNIT] for c in r["cands"] if c[D_UNIT] >= 0)
        rank_d[ds.index(chosen[D_UNIT]) + 1 if chosen[D_UNIT] in ds else -1] += 1
        kinds[chosen[K]] += 1
        sizes[chosen[SIZE]] += 1
        fr[chosen[FRUITS]] += 1
        planter["own" if chosen[PLANTER] == r["seat"] else ("opp" if chosen[PLANTER] == 1 - r["seat"] else "initial")] += 1
        half["own half" if chosen[D_OWN] < chosen[D_OPP] else ("opp half" if chosen[D_OWN] > chosen[D_OPP] else "middle")] += 1
        dist[min(chosen[D_UNIT], 15)] += 1
    print("  dest not tree:", cnt, "| rank of chosen by distance:", sorted(rank_d.items())[:8])
    print("  kind:", kinds.most_common(), "| size:", sorted(sizes.items()), "| fruits:", sorted(fr.items()))
    print("  planter:", planter.most_common(), "| half:", half.most_common(), "| BFS dist (capped 15):", sorted(dist.items()))


def fit_chop(player):
    trips = load(player, "trips")
    rows = [r for r in trips if r["act"] == "CHOP" and r["tal"][3] > 0 and r["dest_tree_s"] is not None]
    moved = [r for r in rows if r["dest_d_unit"] >= 1]
    print(f"chop trips: {len(rows)} (moved to the tree: {len(moved)}, chopped where standing: {len(rows)-len(moved)})")
    describe_chop(moved)
    can = lambda r, c: c[D_UNIT] >= 0 and c[HEALTH] > 0
    res = score_rules(moved, chop_rules(), can, "chop target, unit moved >=1 cell, candidates = every living tree")
    for lo, hi in ((1, 100), (101, 200), (201, 300)):
        sub = [r for r in moved if lo <= r["s"] <= hi]
        score_rules(sub, chop_rules(), can, f"chop target, decision turn {lo}-{hi}", top_examples=0)
    # restricted candidates: trees on the unit's own half / not own planted etc.
    can2 = lambda r, c: c[D_UNIT] >= 0 and c[HEALTH] > 0 and c[PLANTER] != r["seat"]
    res2 = score_rules(moved, {k: v for k, v in chop_rules().items() if "nearest tree" in k or "champion" in k or "wood/(travel+chops)" in k or "min (travel" in k},
                       can2, "chop target, candidates = trees NOT planted by the player")
    can3 = lambda r, c: c[D_UNIT] >= 0 and c[HEALTH] > 0 and c[OCC_OWN] == 0
    res3 = score_rules(moved, {k: v for k, v in chop_rules().items() if "nearest tree" in k or "champion" in k or "wood/(travel+chops)" in k or "min (travel" in k},
                       can3, "chop target, candidates = trees with no other own troll on them")
    return {"n": len(rows), "moved": len(moved), "all": res, "not_own_planted": res2, "unoccupied": res3}


# --------------------------------------------------------------- train -----
def train_cost(n, tal):
    ms, cc, hp, ch = tal
    return [n + ms * ms, n + cc * cc, n + hp * hp, 0, n + ch * ch, 0]


def affordable(inv, n, tal):
    return all(inv[i] >= c for i, c in enumerate(train_cost(n, tal)))


def fit_train(player):
    turns = load(player, "turns")
    by_game = defaultdict(list)
    for r in turns:
        by_game[r["g"]].append(r)
    ladders = Counter()
    events = []
    spec_by_index = defaultdict(Counter)
    turn_by_index = defaultdict(list)
    for g, rows in by_game.items():
        rows.sort(key=lambda r: r["t"])
        seq = []
        for i, r in enumerate(rows):
            if r["train"]:
                # did the roster grow next turn? (TRAIN may fail)
                grew = i + 1 < len(rows) and rows[i + 1]["n"] > r["n"]
                seq.append(tuple(r["train"]))
                idx = len(seq)  # 2nd, 3rd troll ...
                # first turn at which this spec was affordable with the current roster size
                first_aff = None
                for r2 in rows[: i + 1]:
                    if r2["n"] == r["n"] and affordable(r2["inv"], r2["n"], r["train"]):
                        first_aff = r2["t"]
                        break
                events.append(dict(g=g, t=r["t"], n=r["n"], spec=r["train"], inv=r["inv"], grew=grew, first_aff=first_aff,
                                   wood=r["inv"][5], trees=r["trees"]))
                spec_by_index[idx][tuple(r["train"])] += 1
                turn_by_index[idx].append(r["t"])
        ladders[tuple(seq)] += 1
    print(f"\n== training ({player}): {len(by_game)} games, {len(events)} TRAIN commands ==")
    print("  trolls trained per game:", Counter(len(l) for l in ladders.elements()).most_common())
    print("  most common ladders:", ladders.most_common(8))
    for idx in sorted(spec_by_index):
        ts = sorted(turn_by_index[idx])
        med = ts[len(ts) // 2]
        print(f"  troll #{idx+1}: specs {spec_by_index[idx].most_common(6)} | turn median {med}, min {ts[0]}, max {ts[-1]}")
    delays = Counter()
    for e in events:
        d = (e["t"] - e["first_aff"]) if e["first_aff"] is not None else None
        delays[d if d is None or d < 6 else "6+"] += 1
    print("  delay (train turn - first turn the same spec was affordable at the same roster size):", sorted(delays.items(), key=lambda kv: str(kv[0])))
    # spec choice: among all affordable specs at the train turn, does the chosen one maximise an objective?
    objectives = {
        "max ms+cc+hp+chop": lambda t: sum(t),
        "max ms+cc+chop": lambda t: t[0] + t[1] + t[3],
        "max ms*cc + chop": lambda t: t[0] * t[1] + t[3],
        "max cc, then ms, then chop": lambda t: t[1] * 100 + t[0] * 10 + t[3],
        "max chop, then cc, then ms": lambda t: t[3] * 100 + t[1] * 10 + t[0],
        "max ms, then cc, then chop": lambda t: t[0] * 100 + t[1] * 10 + t[3],
        "max min(ms,cc,chop)": lambda t: min(t[0], t[1], t[3]) * 10 + t[0] + t[1] + t[3],
        "max cc*chop": lambda t: t[1] * t[3],
    }
    specs = [(a, b, c, d) for a in range(0, 5) for b in range(0, 5) for c in range(0, 5) for d in range(0, 5)]
    hits = Counter(); n_ev = 0
    ranks = Counter()
    for e in events:
        aff = [sp for sp in specs if affordable(e["inv"], e["n"], sp)]
        if not aff:
            continue
        n_ev += 1
        ch = tuple(e["spec"])
        for name, obj in objectives.items():
            best = max(obj(sp) for sp in aff)
            if obj(ch) == best:
                hits[name] += 1
        # was a strictly "bigger" spec (>= in every talent, > in one) affordable?
        dominated = any(all(sp[i] >= ch[i] for i in range(4)) and sp != ch for sp in aff)
        ranks["a strictly bigger spec was affordable"] += dominated
    print(f"  spec choice among affordable specs (n={n_ev}):", {k: f"{100*v/n_ev:.0f}%" for k, v in hits.most_common()}, dict(ranks))
    # talents by roster size
    for nn in (1, 2, 3, 4):
        ev = [e for e in events if e["n"] == nn]
        if ev:
            print(f"  roster {nn} -> new troll: hp>=2 in {sum(1 for e in ev if e['spec'][2]>=2)}/{len(ev)}, chop>=3 in {sum(1 for e in ev if e['spec'][3]>=3)}/{len(ev)}, cc>=4 in {sum(1 for e in ev if e['spec'][1]>=4)}/{len(ev)}, ms>=3 in {sum(1 for e in ev if e['spec'][0]>=3)}/{len(ev)}; wood at train median {sorted(e['wood'] for e in ev)[len(ev)//2]}")
    failed = sum(1 for e in events if not e["grew"])
    print("  TRAIN commands that did not add a troll:", failed)
    # affordability of the spec one turn earlier: was a *different* affordable spec skipped?
    return {"ladders": [(list(map(list, k)), v) for k, v in ladders.most_common(12)], "events": events[:400], "delays": {str(k): v for k, v in delays.items()}}


# --------------------------------------------------------------- plant -----
def fit_plant(player):
    trips = load(player, "trips")
    rows = [r for r in trips if r["act"] == "PLANT"]
    print(f"\n== planting ({player}): {len(rows)} PLANT actions ==")
    kinds = Counter(r["arg"] for r in rows)
    print("  kinds:", kinds.most_common())
    by_t = defaultdict(Counter)
    for r in rows:
        by_t[min(r["e"] // 50, 5)][r["arg"]] += 1
    print("  kind by 50-turn bucket:", {k * 50: dict(v) for k, v in sorted(by_t.items())})
    d_own = Counter(min(r["dest_d_own"], 12) for r in rows)
    print("  BFS distance of the planted cell to own shack:", sorted(d_own.items()))
    print("  shack-adjacent:", sum(r["dest_shack_adj"] for r in rows), " water-adjacent:", sum(r["dest_water_adj"] for r in rows),
          " own half:", sum(1 for r in rows if r["dest_d_own"] < r["dest_d_opp"]), " opp half:", sum(1 for r in rows if r["dest_d_own"] > r["dest_d_opp"]))
    print("  distance moved for the plant:", sorted(Counter(min(r["dest_d_unit"], 10) for r in rows).items()))
    # neighbourhood: trees adjacent to the planted cell at decision time
    adj = Counter()
    for r in rows:
        n_adj = sum(1 for c in r["cands"] if abs(c[X] - r["dest"][0]) + abs(c[Y] - r["dest"][1]) == 1)
        adj[n_adj] += 1
    print("  living trees orthogonally adjacent to the planted cell:", sorted(adj.items()))
    # cell choice rules (need the map): candidates = walkable cells without a tree at decision time
    maps = load_maps({r["g"] for r in rows})
    def cell_rules():
        return {
            "empty cell nearest to own shack (BFS)": lambda r, f: -f["d_own"],
            "empty cell nearest to own shack, ties -> nearest to unit": lambda r, f: -f["d_own"] - 0.01 * f["d_unit"],
            "empty cell nearest to the unit": lambda r, f: -f["d_unit"],
            "empty cell nearest to the unit, ties -> nearest shack": lambda r, f: -f["d_unit"] - 0.01 * f["d_own"],
            "water-adjacent empty cell nearest to shack (else nearest to shack)": lambda r, f: -f["d_own"] + (100 if f["water"] else 0),
            "water-adjacent empty cell nearest to the unit (else nearest)": lambda r, f: -f["d_unit"] + (100 if f["water"] else 0),
            "nearest-to-shack cell with >=1 adjacent tree": lambda r, f: -f["d_own"] + (100 if f["adj_trees"] >= 1 else 0),
            "nearest-to-unit cell with <=1 adjacent tree": lambda r, f: -f["d_unit"] + (100 if f["adj_trees"] <= 1 else 0),
            "nearest-to-unit cell NOT adjacent to a tree": lambda r, f: -f["d_unit"] + (100 if f["adj_trees"] == 0 else 0),
            "shack-adjacent empty cell (else nearest to shack)": lambda r, f: -f["d_own"] + (100 if f["d_own"] == 1 else 0),
            "min d_own + d_unit": lambda r, f: -(f["d_own"] + f["d_unit"]),
            "min 2*d_own + d_unit": lambda r, f: -(2 * f["d_own"] + f["d_unit"]),
        }
    print("\n== plant cell, candidates = empty walkable cells on the map ==")
    hit = Counter(); n = 0; ties = Counter()
    kind_water = Counter()
    for r in rows:
        m = maps.get(r["g"])
        if not m:
            continue
        walk, shack_own, water, d_own_map = m["walk"][r["seat"]], m["shacks"][r["seat"]], m["water_adj"], m["d_own"][r["seat"]]
        walk = walk - {shack_own} | {tuple(r["pos"])}
        trees = {(c[X], c[Y]) for c in r["cands"]}
        d_unit = bfs_map(walk, tuple(r["pos"]))
        feats = {}
        for cell in walk:
            if cell in trees or cell not in d_unit:
                continue
            adj = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (cell[0] + dx, cell[1] + dy) in trees)
            feats[cell] = {"d_own": d_own_map.get(cell, 99), "d_unit": d_unit[cell], "water": int(cell in water), "adj_trees": adj}
        if not feats:
            continue
        n += 1
        dest = tuple(r["dest"])
        kind_water[(r["arg"], feats[dest]["water"] if dest in feats else -1)] += 1
        for name, key in cell_rules().items():
            best = None; bset = []
            for cell, f in feats.items():
                v = key(r, f)
                if best is None or v > best + 1e-9:
                    best, bset = v, [cell]
                elif abs(v - best) <= 1e-9:
                    bset.append(cell)
            if dest in bset:
                hit[name] += 1
                if len(bset) > 1:
                    ties[name] += 1
    for name in cell_rules():
        print(f"  {name:66s} {hit[name]:5d}/{n:5d} = {100*hit[name]/max(n,1):5.1f}%  (ties among hits {ties[name]})")
    print("  planted kind x water-adjacent cell:", sorted(kind_water.items()))
    return {"n": len(rows), "kinds": dict(kinds), "d_own": dict(d_own), "cell_rules": {k: (hit[k], n) for k in cell_rules()}}


def bfs_map(walk, src):
    from collections import deque
    dist = {src: 0}
    q = deque([src])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)] + 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in walk and (nx, ny) not in dist:
                dist[(nx, ny)] = d
                q.append((nx, ny))
    return dist


def load_maps(game_ids):
    """map geometry per game from games.jsonl (walkable cells, shacks, water-adjacent cells, BFS from each shack)."""
    out = {}
    want = set(game_ids)
    with open("/home/tarstars/prj/troll_farm/data/processed/games.jsonl") as f:
        for line in f:
            gid = int(line[10:line.index(",")])
            if gid not in want:
                continue
            g = json.loads(line)
            rows = g["map"]["rows"]
            walk = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "."}
            water = {(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == "~"}
            shacks = [tuple(g["map"]["shacks"]["p0"]), tuple(g["map"]["shacks"]["p1"])]
            water_adj = {c for c in walk if any((c[0] + dx, c[1] + dy) in water for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
            d_own = [bfs_map(walk | {shacks[p]}, shacks[p]) for p in (0, 1)]
            out[gid] = {"walk": [walk | {shacks[0]}, walk | {shacks[1]}], "shacks": shacks, "water_adj": water_adj, "d_own": d_own}
    return out


# ------------------------------------------------------------- harvest -----
def fit_harvest(player):
    trips = load(player, "trips")
    rows = [r for r in trips if r["act"] == "HARVEST" and r["dest_d_unit"] >= 1 and r["dest_tree_s"] is not None]
    print(f"\n== harvest target ({player}): {len(rows)} harvest trips with movement ==")
    kinds = Counter(r["dest_tree_s"][0] for r in rows)
    print("  kind harvested:", kinds.most_common(), "| fruits on the tree at decision:", sorted(Counter(r['dest_tree_s'][2] for r in rows).items()))
    print("  planter:", Counter("own" if r["dest_planter"] == r["seat"] else ("opp" if r["dest_planter"] == 1 - r["seat"] else "initial") for r in rows).most_common())
    print("  tree distance to own shack:", sorted(Counter(min(r["dest_d_own"], 12) for r in rows).items()))
    def fruit_now(r, c):
        return c[FRUITS] > 0
    rules = {
        "nearest tree with fruit": lambda r, c: -c[D_UNIT] if c[FRUITS] > 0 else None,
        "nearest tree with fruit, ties -> more fruit": lambda r, c: -c[D_UNIT] + 0.01 * c[FRUITS] if c[FRUITS] > 0 else None,
        "max fruits/(travel+1)": lambda r, c: c[FRUITS] / (ceil_div(c[D_UNIT], r["tal"][0]) + 1) if c[FRUITS] > 0 else None,
        "max min(fruits,free)/(travel+harvest turns+return+1)": lambda r, c: (min(c[FRUITS], r["tal"][1] - sum(r["carry_s"])) / (ceil_div(c[D_UNIT], r["tal"][0]) + ceil_div(min(c[FRUITS], r["tal"][1] - sum(r["carry_s"])), r["tal"][2]) + ceil_div(c[D_OWN], r["tal"][0]) + 1)) if c[FRUITS] > 0 else None,
        "nearest fruit tree (incl. ripening within 2 ticks)": lambda r, c: -c[D_UNIT] if (c[FRUITS] > 0 or (c[SIZE] == 4 and c[CD] <= 2)) else None,
        "nearest own-planted tree with fruit": lambda r, c: (-c[D_UNIT] if c[PLANTER] == r["seat"] else -999) if c[FRUITS] > 0 else None,
        "closest-to-shack tree with fruit": lambda r, c: -c[D_OWN] if c[FRUITS] > 0 else None,
        "nearest tree with fruit, no other own troll on it": lambda r, c: (-c[D_UNIT] if c[OCC_OWN] == 0 else -999) if c[FRUITS] > 0 else None,
    }
    can = lambda r, c: c[D_UNIT] >= 0
    res = score_rules(rows, rules, can, "harvest target, candidates = every living tree")
    return {"n": len(rows), "rules": res}


# ------------------------------------------------------------- endgame -----
def fit_endgame(player):
    turns = load(player, "turns")
    trips = load(player, "trips")
    by_game = defaultdict(list)
    for r in trips:
        by_game[r["g"]].append(r)
    last_plant, first_own_chop, last_harvest = [], [], []
    for g, rows in by_game.items():
        pl = [r["e"] for r in rows if r["act"] == "PLANT"]
        last_plant.append(max(pl) if pl else None)
        oc = [r["e"] for r in rows if r["act"] == "CHOP" and r["dest_planter"] == r["seat"]]
        first_own_chop.append(min(oc) if oc else None)
        hv = [r["e"] for r in rows if r["act"] == "HARVEST"]
        last_harvest.append(max(hv) if hv else None)
    def q(xs):
        xs = sorted(x for x in xs if x is not None)
        return (xs[len(xs)//10], xs[len(xs)//2], xs[9*len(xs)//10], len(xs)) if xs else None
    print(f"\n== endgame ({player}) — per game (10th pct, median, 90th pct, n) ==")
    print("  last PLANT turn:", q(last_plant), "| games with no plant:", sum(1 for x in last_plant if x is None))
    print("  first CHOP of an own-planted tree:", q(first_own_chop), "| never:", sum(1 for x in first_own_chop if x is None))
    print("  last HARVEST turn:", q(last_harvest))
    # own-planted trees alive by turn bucket
    alive = defaultdict(list)
    for r in turns:
        alive[r["t"]].append(r["own_planted_alive"])
    print("  own-planted trees alive (mean) at t=50,100,...,300:", {t: round(sum(alive[t])/len(alive[t]), 1) for t in (50, 100, 150, 200, 250, 270, 280, 290, 300) if alive[t]})
    trees = defaultdict(list)
    for r in turns:
        trees[r["t"]].append(r["trees"])
    print("  all trees alive (mean):", {t: round(sum(trees[t])/len(trees[t]), 1) for t in (1, 50, 100, 150, 200, 250, 280, 300) if trees[t]})
    # chop of own-planted trees by turn bucket
    oc = Counter(min(r["e"] // 25 * 25, 300) for r in trips if r["act"] == "CHOP" and r["dest_planter"] == r["seat"])
    print("  CHOP actions on own-planted trees by 25-turn bucket:", sorted(oc.items()))
    ac = Counter(min(r["e"] // 25 * 25, 300) for r in trips if r["act"] == "CHOP")
    print("  all CHOP actions by 25-turn bucket:", sorted(ac.items()))
    hc = Counter(min(r["e"] // 25 * 25, 300) for r in trips if r["act"] == "HARVEST")
    print("  all HARVEST actions by 25-turn bucket:", sorted(hc.items()))
    pc = Counter(min(r["e"] // 25 * 25, 300) for r in trips if r["act"] == "PLANT")
    print("  all PLANT actions by 25-turn bucket:", sorted(pc.items()))


# --------------------------------------------------------------- roles -----
def fit_roles(player):
    trips = load(player, "trips")
    by = defaultdict(Counter)
    tal = {}
    for r in trips:
        key = (r["g"], r["u"])
        by[key][r["act"]] += r["k"] if r["act"] in ("CHOP", "HARVEST") else 1
        tal[key] = tuple(r["tal"])
    print(f"\n== unit roles ({player}) — action turns per unit, grouped by talents (ms,cc,hp,chop) ==")
    agg = defaultdict(lambda: Counter())
    n_units = Counter()
    for key, c in by.items():
        agg[tal[key]] += c
        n_units[tal[key]] += 1
    for t, c in sorted(agg.items(), key=lambda kv: -n_units[kv[0]])[:10]:
        tot = sum(c.values())
        print(f"  {t}: {n_units[t]} units; " + ", ".join(f"{a} {100*v/tot:.0f}%" for a, v in c.most_common()))


if __name__ == "__main__":
    player = sys.argv[1]
    aspects = sys.argv[2:] or ["chop", "train", "plant", "harvest", "endgame", "roles"]
    out = {}
    for a in aspects:
        out[a] = globals()[f"fit_{a}"](player)
    (HERE / f"{player}_fit_results.json").write_text(json.dumps(out, default=str, indent=1))
