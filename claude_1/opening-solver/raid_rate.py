"""The balance question: how fast do enemies fell trees planted next to a shack?

Every collected game with a full per-turn replay is rebuilt exactly the way
`local_claude_1/funding-order/analyze_funding.py` and `reconstructions/fits/reconstruct.py` do it
(the referee mirror `sim/engine.py` predicts each turn, the platform's own keyframe diff overlays
the truth).  Every PLANT that produced a tree is tagged with its planter, turn, kind and walking
distance from the planter's shack; when the tree dies the CHOP commands on that cell that turn say
who felled it: the enemy (a raid), the owner (a conversion) or both.  Trees standing at the end
are censored.  Output: raid-rate.json (per-tree records and the hazard tables) and a printed read.

Sources: orchard 6's 160 ladder games (`local_claude_1/ladder-queue/games-41209711/`), and the raw
replays of the top players on this laptop (`data/raw/games/`, the games `player_games.json` names).
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import Counter, defaultdict, deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "local_claude_1", "reconstructions", "fits"))
import reconstruct as rc                    # noqa: E402
from sim.engine import step                 # noqa: E402

ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))
RAW = os.path.join(ROOT, "data", "raw", "games")
ORCHARD6 = os.path.join(ROOT, "local_claude_1", "ladder-queue", "games-41209711",
                        "games-agent6671418-submission41209711.jsonl.gz")
ORCHARD6_AGENT = 6671418


def bfs(walkable, sources):
    dist, dq = {}, deque()
    for s in sources:
        dist[s] = 0
        dq.append(s)
    while dq:
        c = dq.popleft()
        for dx, dy in ORTH:
            n = (c[0] + dx, c[1] + dy)
            if n in walkable and n not in dist:
                dist[n] = dist[c] + 1
                dq.append(n)
    return dist


def make_reconstructor(game_dict):
    r = rc.Reconstructor.__new__(rc.Reconstructor)
    r.game_id = game_dict["gameId"]
    r.replay = game_dict
    r.frames = game_dict["frames"]
    w, h, rows, units, plants, inv = rc.parse_frame0(r.frames[0])
    r.map = dict(w=w, h=h, rows=rows)
    r.game = rc.build_game(w, h, rows, units, plants, inv)
    r.unit_by_eid, r.plant_by_eid = {}, {}
    by_id = {u.id: u for u in r.game.units}
    for eid, u in units.items():
        r.unit_by_eid[eid] = by_id[u["id"]]
    by_pos = {p.pos: p for p in r.game.plants}
    for eid, p in plants.items():
        r.plant_by_eid[eid] = by_pos[(p["x"], p["y"])]
    r.mismatch = Counter()
    r.examples = {}
    r.agents = {a["index"]: a for a in r.replay["agents"]}
    r.n_turns = (len(r.frames) - 1) // 2
    return r


def geometry(rows):
    walkable, shacks = set(), [None, None]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                shacks[0] = (x, y)
            elif ch == "1":
                shacks[1] = (x, y)
            elif ch == ".":
                walkable.add((x, y))
    dist = []
    for p in (0, 1):
        doors = [d for d in [(shacks[p][0] + dx, shacks[p][1] + dy) for dx, dy in ORTH] if d in walkable]
        dist.append(bfs(walkable, doors))
    return shacks, dist


def analyze_game(g, label):
    r = make_reconstructor(g)
    shacks, dist = geometry(r.map["rows"])
    owned = {}          # cell -> record
    records = []
    agents = {a["index"]: a["agentId"] for a in g["agents"]}
    for t in range(1, r.n_turns + 1):
        c0, c1 = r.commands(t)
        pre_units = {u.id: (u.player, (u.x, u.y)) for u in r.game.units}
        pre_plants = {p.pos: (p.type, p.size) for p in r.game.plants}
        planters, choppers = {}, defaultdict(set)
        for player, cmds in ((0, c0), (1, c1)):
            for cmd in cmds:
                f = cmd.split()
                if len(f) >= 2 and f[0] in ("PLANT", "CHOP") and f[1].lstrip("-").isdigit():
                    uid = int(f[1])
                    if uid in pre_units and pre_units[uid][0] == player:
                        cell = pre_units[uid][1]
                        if f[0] == "PLANT":
                            planters[cell] = player
                        else:
                            choppers[cell].add(player)
        r._pre_units = {u.id: (u.x, u.y, list(u.carry)) for u in r.game.units}
        r._pre_plants = [(p.pos, p.size, p.fruits, p.health) for p in r.game.plants]
        step(r.game, c0, c1)
        j = rc.view_payload(r.frames[2 * t].get("view"))
        inv_after = [[int(v) for v in ln.split()] for ln in j["inputmodule"].split("\n")]
        r.apply_diff(t, j.get("diff", ""), inv_after)
        post_plants = {p.pos: (p.type, p.size) for p in r.game.plants}
        for cell in post_plants:
            if cell not in pre_plants and cell in planters:
                p = planters[cell]
                rec = dict(game=g["gameId"], label=label, planter=p, planter_agent=agents.get(p),
                           kind=post_plants[cell][0], cell=list(cell), turn=t,
                           dist=dist[p].get(cell), fate="standing", death_turn=None, size_at_death=None)
                owned[cell] = rec
                records.append(rec)
        for cell in pre_plants:
            if cell not in post_plants and cell in owned:
                rec = owned.pop(cell)
                who = choppers.get(cell, set())
                if not who:
                    rec["fate"] = "vanished"
                elif who == {rec["planter"]}:
                    rec["fate"] = "converted"
                elif rec["planter"] in who:
                    rec["fate"] = "both"
                else:
                    rec["fate"] = "raided"
                rec["death_turn"] = t
                rec["size_at_death"] = pre_plants[cell][1]
    for rec in owned.values():
        rec["end_turn"] = r.n_turns
    return records, r.n_turns


def load_games(max_top=400):
    games = []
    with gzip.open(ORCHARD6, "rt") as fh:
        for line in fh:
            games.append((json.loads(line), "orchard6"))
    pg = json.load(open(os.path.join(ROOT, "local_claude_1", "reconstructions", "fits", "player_games.json")))
    seen = {g["gameId"] for g, _ in games}
    for player, rows in pg.items():
        for row in rows:
            gid = row["gameId"]
            path = os.path.join(RAW, f"{gid}.json")
            if gid in seen or not os.path.exists(path):
                continue
            seen.add(gid)
            games.append((json.load(open(path)), player))
            if len(games) >= max_top + 200:
                break
    return games


def dist_bin(d):
    if d is None:
        return "unreachable"
    return "1" if d <= 1 else "2" if d == 2 else "3" if d == 3 else "4-5" if d <= 5 else "6+"


def turn_bin(t):
    return "1-50" if t <= 50 else "51-100" if t <= 100 else "101-150" if t <= 150 else "151-200" if t <= 200 else "201-300"


def hazards(records):
    """Raids per 100 tree-turns of exposure, by distance bin and by turn bin (own-planted trees)."""
    exp = Counter()
    raids = Counter()
    for rec in records:
        end = rec["death_turn"] if rec["death_turn"] else rec["end_turn"]
        db = dist_bin(rec["dist"])
        for t in range(rec["turn"], end + 1):
            exp[(db, turn_bin(t))] += 1
        if rec["fate"] == "raided":
            raids[(db, turn_bin(rec["death_turn"]))] += 1
    table = {}
    for key in sorted(exp):
        table[f"{key[0]}|{key[1]}"] = {"tree_turns": exp[key], "raids": raids[key],
                                       "raids_per_100_tree_turns": 100.0 * raids[key] / exp[key]}
    return table


def main():
    games = load_games()
    records, skipped = [], []
    per_label = Counter()
    for g, label in games:
        try:
            recs, n_turns = analyze_game(g, label)
            records.extend(recs)
            per_label[label] += 1
        except Exception as e:      # a malformed replay (one is known in the orchard 6 batch)
            skipped.append((g.get("gameId"), f"{type(e).__name__}: {e}"))
    print(f"games: {dict(per_label)}  skipped {len(skipped)}: {skipped[:3]}")
    print(f"planted trees tracked: {len(records)}")
    fates = Counter(r["fate"] for r in records)
    print("fates:", dict(fates))
    own6 = [r for r in records if r["label"] == "orchard6" and r["planter_agent"] == ORCHARD6_AGENT]
    print(f"orchard 6's own trees: {len(own6)} fates {dict(Counter(r['fate'] for r in own6))}")
    print("\nraids per 100 tree-turns (all planters), distance | turns:")
    tab = hazards(records)
    for k, v in tab.items():
        if v["tree_turns"] >= 500:
            print(f"  {k:>14}: {v['raids_per_100_tree_turns']:.3f}  ({v['raids']} raids / {v['tree_turns']} tree-turns)")
    # survival of an early near tree to turn 100 / 150
    near_early = [r for r in records if r["dist"] is not None and r["dist"] <= 2 and r["turn"] <= 30]
    for horizon in (60, 100, 150):
        alive = sum(1 for r in near_early if not (r["fate"] == "raided" and r["death_turn"] <= horizon)
                    and (r["end_turn"] if r["death_turn"] is None else r["death_turn"]) >= horizon or (r["fate"] in ("converted", "both") and r["death_turn"] <= horizon))
        raided = sum(1 for r in near_early if r["fate"] == "raided" and r["death_turn"] <= horizon)
        print(f"trees planted at distance <=2 by turn 30 (n={len(near_early)}): raided by turn {horizon}: {raided} ({100.0*raided/len(near_early):.1f} %)")
    first_raid = sorted(r["death_turn"] for r in records if r["fate"] == "raided" and r["dist"] is not None and r["dist"] <= 2)
    if first_raid:
        import statistics
        print(f"raids of trees at distance <=2: n={len(first_raid)}, earliest turn {first_raid[0]}, 10th pct {first_raid[len(first_raid)//10]}, median {statistics.median(first_raid)}")
    out = {"games": dict(per_label), "skipped": skipped, "records": records, "hazard": tab}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "raid-rate.json"), "w") as fh:
        json.dump(out, fh)


if __name__ == "__main__":
    main()
