#!/usr/bin/env python3
"""Read a collected package of ladder games (sanitised replays) for the apple-farm question:
per game -- did the map have a farm cell (a door of our shack touching water, >= 2 doors, empty or
holding an apple), did the farm run (PLANT/HARVEST/DROP by our starting troll on that cell), the
final inventories, the scores. Then the split: farm maps vs the rest, and the same split on the
champion's package for comparison. Facts only.

    python3 local_claude_1/apple-farm/ladder_read.py <package.jsonl.gz> <our agent id> [label]
"""
import gzip, json, re, sys
from collections import Counter

ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))

def parse_map(view):
    j = json.loads(view[view.index("{"):])
    im = j["global"]["inputmodule"]
    lines = im.split("\n")
    w, h = map(int, lines[0].split())
    return lines[1:1 + h], w, h

def farm_cell(rows, w, h, seat, trees0):
    ch = "0" if seat == 0 else "1"
    shack = [(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == ch][0]
    doors = [(shack[0] + dx, shack[1] + dy) for dx, dy in ORTH
             if 0 <= shack[0] + dx < w and 0 <= shack[1] + dy < h and rows[shack[1] + dy][shack[0] + dx] == "."]
    if len(doors) < 2:
        return shack, None
    wet = [d for d in doors if any(0 <= d[0] + dx < w and 0 <= d[1] + dy < h and rows[d[1] + dy][d[0] + dx] == "~" for dx, dy in ORTH)]
    for d in wet:
        if trees0.get(d) == "APPLE":
            return shack, d
    for d in wet:
        if d not in trees0:
            return shack, d
    return shack, None

def initial_trees(frame0_view):
    """Trees at turn 1 from the first keyframe's entity diff are not trivially parsable; use the
    first turn's inputmodule of OUR seat's frame instead (the referee input we were given)."""
    return {}

def read_game(g, agent_id):
    seat = [a["index"] for a in g["agents"] if a["agentId"] == agent_id][0]
    opp = 1 - seat
    frames = g["frames"]
    rows, w, h = parse_map(frames[0]["view"])
    # Our first-turn referee input (trees) lives in the stdin we were given; the replay does not
    # carry it, so trees are read from our own first command line's context: not available.
    # The farm cell is therefore predicted WITHOUT the initial trees (empty-or-apple assumed): a
    # wet door blocked by a foreign tree at turn 1 would be counted as a farm map that did not
    # run -- the 'ran' column separates the two.
    shack, farm = farm_cell(rows, w, h, seat, {})
    me = str(seat)
    trained = Counter()
    for t in g.get("tooltips", []):
        try:
            tt = json.loads(t)
        except Exception:
            continue
        m = re.match(r"\$(\d) trained a unit", tt.get("text", ""))
        if m:
            trained[int(m.group(1))] += 1
    counts = Counter(); first = {}
    at_farm = False
    last_inv = None
    turn = 0
    for fr in frames[1:]:
        if fr.get("keyframe") and fr.get("view"):
            v = fr["view"]
            try:
                j = json.loads(v[v.index("{"):])
                im = j.get("inputmodule", "")
                ls = [l for l in im.split("\n") if l.strip()]
                if len(ls) >= 2 and all(len(l.split()) == 6 for l in ls[:2]):
                    last_inv = [list(map(int, ls[0].split())), list(map(int, ls[1].split()))]
            except Exception:
                pass
        if fr.get("agentId") != seat:
            continue
        turn += 1
        out = fr.get("stdout") or ""
        for frag in out.split(";"):
            f = frag.split()
            if not f or f[0] == "MSG":
                continue
            # Our starting troll's id is our seat number (the referee creates troll 0 for player 0,
            # troll 1 for player 1); it keeps that id all game.
            if f[0] == "MOVE" and len(f) == 4 and f[1] == me:
                at_farm = farm is not None and (int(f[2]), int(f[3])) == farm
                continue
            if len(f) >= 2 and f[1] == me and f[0] in ("PICK", "PLANT", "HARVEST", "DROP", "CHOP"):
                key = f"{f[0]}@farm" if at_farm else f"{f[0]}@else"
                counts[key] += 1; first.setdefault(key, turn)
    own_inv = last_inv[seat] if last_inv else None
    return {
        "gameId": g["gameId"], "seat": seat, "farm_cell": farm, "own": g["scores"][seat], "opp": g["scores"][opp],
        "win": g["scores"][seat] > g["scores"][opp], "turns": turn,
        "ran": counts.get("HARVEST@farm", 0) >= 5, "harvests": counts.get("HARVEST@farm", 0),
        "plants": counts.get("PLANT@farm", 0), "first_plant": first.get("PLANT@farm"),
        "own_inv": own_inv, "opp_score_agent": [a["score"] for a in g["agents"] if a["index"] == opp][0],
        "own_trolls": 1 + trained[seat], "opp_trolls": 1 + trained[opp],
    }

def summarize(rows, label):
    def stat(sub, name):
        if not sub:
            print(f"  {name:<28} n=0"); return
        n = len(sub); wins = sum(r["win"] for r in sub)
        own = sum(r["own"] for r in sub) / n; opp = sum(r["opp"] for r in sub) / n
        oppr = sum(r["opp_score_agent"] for r in sub) / n
        big = sum(1 for r in sub if r["opp_trolls"] >= 3)
        print(f"  {name:<28} n={n:>3}  wins {wins:>3} ({100*wins/n:4.1f}%)  own {own:6.1f}  opp {opp:6.1f}  margin {own-opp:+6.1f}  opp rating {oppr:5.1f}  opp with 3+ trolls {big:>3} ({100*big/n:4.1f}%)")
    print(f"== {label}: {len(rows)} games ==")
    farm = [r for r in rows if r["farm_cell"]]
    stat(rows, "all")
    stat(farm, "farm maps (cell exists)")
    stat([r for r in farm if r["ran"]], "  farm ran (>=5 harvests)")
    stat([r for r in farm if not r["ran"]], "  farm did not run")
    stat([r for r in rows if not r["farm_cell"]], "no farm cell")
    ran = [r for r in farm if r["ran"]]
    if ran:
        hv = sorted(r["harvests"] for r in ran)
        apples = [r["own_inv"][2] for r in ran if r["own_inv"]]
        wood = [r["own_inv"][5] for r in ran if r["own_inv"]]
        print(f"  farm ran: harvests median {hv[len(hv)//2]}, min {hv[0]}, max {hv[-1]}; first plant turns {Counter(r['first_plant'] for r in ran).most_common(4)};"
              f" final apples mean {sum(apples)/max(1,len(apples)):.1f}, final wood mean {sum(wood)/max(1,len(wood)):.1f}; replants (plants>1): {sum(1 for r in ran if r['plants']>1)}")
    return farm

if __name__ == "__main__":
    path, agent_id = sys.argv[1], int(sys.argv[2]); label = sys.argv[3] if len(sys.argv) > 3 else path
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rows.append(read_game(json.loads(line), agent_id))
    summarize(rows, label)
    out = path.rsplit("/", 1)[0] + "/ladder-read.json"
    json.dump(rows, open(out, "w"), indent=1, default=str)
    print(f"  -> {out}")
