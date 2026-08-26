#!/usr/bin/env python3
"""Calibrate the banana-farm latch and the denial round criterion from raw replays.

Reads data/raw/games/*.json (read-only). For every (game, seat) it rebuilds the
seat's hut ring from the setup map, replays the referee's ACCEPTED events, and
counts what happens on that ring.

Why the replays and not data/processed/turns.jsonl.gz: the turn export keeps the
commands a bot ISSUED and drops the board, so hut coordinates -- and therefore the
ring -- are not reconstructible from it (codex_1, field-comparison-2026-08-26 sec.4).
The replay setup frame carries the map with both huts marked '0' and '1', and the
per-frame `summary` carries the referee's accepted events. Troll cells come from the
accepted "moved to (x, y)" lines, so an event is attributed to a cell the referee
agreed the troll stood on.

Limits, stated not hidden: a summary line says "damaged a tree", never which tree or
for how much, so a chop is attributed to the chopping troll's own cell (CHOP acts on
the actor's cell, as HARVEST does). A troll's cell is unknown until its first accepted
move; events before that are counted as UNATTRIBUTED and reported.

Output: JSON on stdout, one record per (game, seat) plus per-bot aggregates.
"""
import argparse, collections, glob, json, os, re, sys

MOVED = re.compile(r"\$(\d+): troll (\d+) moved to \((\d+), (\d+)\)")
PLANTED = re.compile(r"\$(\d+): troll (\d+) planted a (\w+)")
DAMAGED = re.compile(r"\$(\d+): troll (\d+) damaged a tree")
HARVEST = re.compile(r"\$(\d+): troll (\d+) harvested (\d+) (\w+?)s?$")
TRAINED = re.compile(r"\$(\d+): trained a troll")


def parse_map(frame0):
    view = frame0.get("view") or ""
    body = view.split("\n", 1)[1] if "\n" in view else ""
    g = json.loads(body)["global"]
    rows = g["inputmodule"].split("\n")
    w, h = (int(x) for x in rows[0].split())
    grid = rows[1:1 + h]
    huts = {}
    walkable = set()
    water = set()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in "01":
                huts[int(ch)] = (x, y)
            if ch in ".+01":
                walkable.add((x, y))
            if ch == "~":
                water.add((x, y))
    return w, h, huts, walkable, water


def ring(hut, w, h):
    x, y = hut
    ortho = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    diag = [(x + dx, y + dy) for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1))]
    inb = lambda c: 0 <= c[0] < w and 0 <= c[1] < h
    return [c for c in ortho if inb(c)], [c for c in diag if inb(c)]


def analyse(path):
    d = json.load(open(path))
    frames = d.get("frames") or []
    if not frames:
        return None
    w, h, huts, walkable, water = parse_map(frames[0])
    if 0 not in huts or 1 not in huts:
        return None
    names = {}
    for a in d.get("agents", []):
        names[a.get("index")] = (a.get("codingamer") or {}).get("pseudo") or a.get("name")
    rings = {}
    for s in (0, 1):
        o, dg = ring(huts[s], w, h)
        rings[s] = {"ortho": set(o), "diag": set(dg), "all": set(o) | set(dg)}
    cell = {}          # (seat, troll) -> cell
    owner = {}         # (seat, troll) -> seat  (troll ids are global in the summaries)
    turn = 0
    rec = {s: dict(plant_ring=0, plant_ring_ortho=0, plant_ring_diag=0, plant_off=0,
                   harvest_ring=0, harvest_off=0, chop_ring=0, chop_off=0,
                   enemy_chop_on_my_ring=0, unattributed=0, trained=0,
                   plant_turns=[], enemy_chop_turns=[], my_ring_work_turns=[],
                   plant_near_hut=0) for s in (0, 1)}
    for f in frames:
        if f.get("keyframe") in (True, "True"):
            turn += 1
        s = f.get("summary") or ""
        for line in s.split("\n"):
            line = line.strip()
            if not line:
                continue
            m = MOVED.match(line)
            if m:
                seat, troll, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                cell[(seat, troll)] = (x, y)
                owner[troll] = seat
                continue
            m = TRAINED.match(line)
            if m:
                rec[int(m.group(1))]["trained"] += 1
                continue
            m = PLANTED.match(line)
            if m:
                seat, troll, kind = int(m.group(1)), int(m.group(2)), m.group(3)
                c = cell.get((seat, troll))
                if c is None:
                    rec[seat]["unattributed"] += 1
                    continue
                if c in rings[seat]["all"]:
                    rec[seat]["plant_ring"] += 1
                    if c in rings[seat]["ortho"]:
                        rec[seat]["plant_ring_ortho"] += 1
                    else:
                        rec[seat]["plant_ring_diag"] += 1
                else:
                    rec[seat]["plant_off"] += 1
                if max(abs(c[0] - huts[seat][0]), abs(c[1] - huts[seat][1])) <= 2:
                    rec[seat]["plant_near_hut"] += 1
                rec[seat]["plant_turns"].append(turn)
                continue
            m = HARVEST.match(line)
            if m:
                seat, troll = int(m.group(1)), int(m.group(2))
                c = cell.get((seat, troll))
                if c is None:
                    rec[seat]["unattributed"] += 1
                    continue
                if c in rings[seat]["all"]:
                    rec[seat]["harvest_ring"] += 1
                    rec[seat]["my_ring_work_turns"].append(turn)
                else:
                    rec[seat]["harvest_off"] += 1
                continue
            m = DAMAGED.match(line)
            if m:
                seat, troll = int(m.group(1)), int(m.group(2))
                c = cell.get((seat, troll))
                if c is None:
                    rec[seat]["unattributed"] += 1
                    continue
                if c in rings[seat]["all"]:
                    rec[seat]["chop_ring"] += 1
                    rec[seat]["my_ring_work_turns"].append(turn)
                else:
                    rec[seat]["chop_off"] += 1
                foe = 1 - seat
                if c in rings[foe]["all"]:
                    rec[foe]["enemy_chop_on_my_ring"] += 1
                    rec[foe]["enemy_chop_turns"].append(turn)
                continue
    out = []
    for s in (0, 1):
        r = dict(rec[s])
        r["gameId"] = d.get("gameId")
        r["seat"] = s
        r["name"] = names.get(s)
        r["opponent"] = names.get(1 - s)
        r["turns"] = turn
        r["hut"] = huts[s]
        r["ring_water"] = len(rings[s]["all"] & water)
        r["ring_walkable"] = len(rings[s]["all"] & walkable)
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", default="data/raw/games")
    ap.add_argument("--out", default="-")
    a = ap.parse_args()
    rows = []
    for p in sorted(glob.glob(os.path.join(a.games, "*.json"))):
        try:
            r = analyse(p)
        except Exception as e:                      # a malformed replay must not kill the run
            print(f"skip {p}: {e}", file=sys.stderr)
            continue
        if r:
            rows.extend(r)
    agg = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in rows:
        b = agg[r["name"]]
        b["games"] += 1
        for k in ("plant_ring", "plant_ring_ortho", "plant_ring_diag", "plant_off",
                  "harvest_ring", "harvest_off", "chop_ring", "chop_off",
                  "enemy_chop_on_my_ring", "unattributed", "plant_near_hut", "turns"):
            b[k] += r[k]
    summary = {}
    for name, b in agg.items():
        g = b["games"]
        summary[name] = {k: round(v / g, 3) for k, v in b.items() if k != "games"}
        summary[name]["games"] = int(g)
    json.dump({"per_game_seat": rows, "per_bot_mean": summary}, 
              sys.stdout if a.out == "-" else open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
