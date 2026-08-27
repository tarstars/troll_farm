#!/usr/bin/env python3
"""Read a collected package of ladder games (sanitised replays) for the floor question: per game --
our second troll (its four talents and the turn it was trained), the win, the scores, the opponent's
troll count and rating. Then the cuts: the split by our second troll (at/above 2/2/0/2 against below
-- the floor's bot must never be below), training-turn buckets, wins by opponent troll count, the
talent vectors bought. Facts only; works on any bot's package (the champion's, the apple farm's).

    python3 local_claude_1/the-floor/ladder_read.py <package.jsonl.gz> <our agent id> [label]
"""
import gzip
import json
import re
import statistics
import sys
from collections import Counter


def read_game(g, agent_id):
    seat = [a["index"] for a in g["agents"] if a["agentId"] == agent_id][0]
    opp = 1 - seat
    trained = Counter()
    for t in g.get("tooltips", []):
        try:
            tt = json.loads(t)
        except Exception:
            continue
        m = re.match(r"\$(\d) trained a unit", tt.get("text", ""))
        if m:
            trained[int(m.group(1))] += 1
    turn = 0
    spec, train_turn, last_inv = None, None, None
    for fr in g["frames"][1:]:
        if fr.get("keyframe") and fr.get("view"):
            v = fr["view"]
            try:
                j = json.loads(v[v.index("{"):])
                ls = [l for l in j.get("inputmodule", "").split("\n") if l.strip()]
                if len(ls) >= 2 and all(len(l.split()) == 6 for l in ls[:2]):
                    last_inv = [list(map(int, ls[0].split())), list(map(int, ls[1].split()))]
            except Exception:
                pass
        if fr.get("agentId") != seat:
            continue
        turn += 1
        out = fr.get("stdout") or ""
        if spec is None and "TRAIN" in out:
            for frag in out.split(";"):
                f = frag.split()
                if f and f[0] == "TRAIN" and len(f) >= 5:
                    spec = [int(x) for x in f[1:5]]
                    train_turn = turn
                    break
    return {
        "gameId": g["gameId"], "seat": seat, "own": g["scores"][seat], "opp": g["scores"][opp],
        "win": g["scores"][seat] > g["scores"][opp], "turns": turn,
        "second_troll": spec, "train_turn": train_turn,
        "floored": spec is not None and spec[0] >= 2 and spec[1] >= 2 and spec[3] >= 2,
        "own_inv": last_inv[seat] if last_inv else None,
        "opp_score_agent": [a["score"] for a in g["agents"] if a["index"] == opp][0],
        "own_trolls": 1 + trained[seat], "opp_trolls": 1 + trained[opp],
    }


def stat(sub, name):
    if not sub:
        print(f"  {name:<34} n=0")
        return
    n = len(sub)
    wins = sum(r["win"] for r in sub)
    own = sum(r["own"] for r in sub) / n
    opp = sum(r["opp"] for r in sub) / n
    oppr = sum(r["opp_score_agent"] for r in sub) / n
    big = sum(1 for r in sub if r["opp_trolls"] >= 3)
    print(f"  {name:<34} n={n:>3}  wins {wins:>3} ({100*wins/n:4.1f}%)  own {own:6.1f}  opp {opp:6.1f}"
          f"  margin {own-opp:+6.1f}  opp rating {oppr:5.1f}  opp with 3+ trolls {big:>3} ({100*big/n:4.1f}%)")


def summarize(rows, label):
    print(f"== {label}: {len(rows)} games ==")
    stat(rows, "all")
    trained = [r for r in rows if r["second_troll"]]
    stat([r for r in trained if r["floored"]], "second troll at/above 2/2/0/2")
    stat([r for r in trained if not r["floored"]], "second troll BELOW the floor")
    stat([r for r in rows if not r["second_troll"]], "never trained")
    for lo, hi in ((1, 5), (6, 10), (11, 20), (21, 40), (41, 400)):
        stat([r for r in trained if lo <= r["train_turn"] <= hi], f"trained on turns {lo}-{hi}")
    stat([r for r in rows if r["opp_trolls"] <= 2], "vs 2-troll opponents")
    stat([r for r in rows if r["opp_trolls"] == 3], "vs 3-troll opponents")
    stat([r for r in rows if r["opp_trolls"] >= 4], "vs 4+-troll opponents")
    specs = Counter(" ".join(map(str, r["second_troll"])) for r in trained)
    turns = sorted(r["train_turn"] for r in trained)
    if turns:
        print(f"  second troll bought: {specs.most_common(8)}; training turn median {turns[len(turns)//2]},"
              f" mean {statistics.mean(turns):.1f}, max {turns[-1]}")
    wood = [r["own_inv"][5] for r in rows if r["own_inv"]]
    fruit = [sum(r["own_inv"][:4]) for r in rows if r["own_inv"]]
    if wood:
        print(f"  final wood mean {statistics.mean(wood):.1f} ({4*statistics.mean(wood):.0f} points),"
              f" fruit mean {statistics.mean(fruit):.1f}")


if __name__ == "__main__":
    path, agent_id = sys.argv[1], int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else path
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rows.append(read_game(json.loads(line), agent_id))
    summarize(rows, label)
    out = path.rsplit("/", 1)[0] + "/ladder-read.json"
    json.dump(rows, open(out, "w"), indent=1, default=str)
    print(f"  -> {out}")
