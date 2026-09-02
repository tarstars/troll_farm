#!/usr/bin/env python3
"""Diagnostics behind the review's findings 2, 3 and 7 and the tie-break proof.

For every move where referee.py and the platform disagree and the target was beyond
the troll's speed, checks whether the platform's cell is in referee.py's own set of
equal-best cells (a genuine random tie-break) and, if not, whether a teammate stood
on a tie cell (the platform picked the blocked step at random and logged "target
blocked").  Also prints the same-turn plant/chop case, the numeric-item PICK/PLANT
effect, and every time-strike line in the recordings.

Reviewer's instrument (local_claude_1, 2026-09-01); not part of the package.
"""
import collections
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cleanroom", "spec-work"))
sys.path.insert(0, os.path.join(ROOT, "cleanroom", "package", "harness"))
sys.path.insert(0, HERE)
import corpus    # noqa: E402
import referee   # noqa: E402
from referee_vs_recordings import make_game, line_of  # noqa: E402

SPECIAL = {(900572315, 258), (900572315, 262), (900571120, 1), (900571120, 4)}


def equal_best_cells(game, start, target, speed):
    """All cells referee.py considers equal-best for this move (its tie set)."""
    src = game.distances([start])
    if src.get(target, 1 << 30) <= speed:
        return {target}
    if target in src:
        tdist = game.distances([target])
    else:
        best = min(abs(target[0] - c[0]) + abs(target[1] - c[1]) for c in src)
        goals = [c for c in src if abs(target[0] - c[0]) + abs(target[1] - c[1]) == best]
        tdist = game.distances(goals)
    reach = [c for c, d in src.items() if d <= speed and c in tdist]
    if not reach:
        return {start}
    b = min(tdist[c] for c in reach)
    return {c for c in reach if tdist[c] == b}


def main():
    tie = collections.Counter()
    illegal_chunks = collections.Counter()
    for g in corpus.games():
        seat = g["seat"]
        for t in range(g["turns"]):
            before, after = g["states"][t], g["states"][t + 1]
            game = make_game(g, before)
            lines = {seat: line_of(g["commands"][t]), 1 - seat: line_of(g["opp_commands"][t])}
            parsed, bad = {}, False
            for s in (0, 1):
                try:
                    parsed[s] = referee.parse(lines[s], game, s)
                except referee.Illegal as exc:
                    bad = True
                    cmds = g["commands"][t] if s == seat else g["opp_commands"][t]
                    for verb, args in cmds:
                        if verb in ("PICK", "PLANT") and (len(args) < 2 or str(args[1]).upper() not in referee.INDEX):
                            illegal_chunks[(verb, str(args[1:2]))] += 1
                        elif verb not in referee.PRIORITY and verb not in ("MSG", "WAIT"):
                            illegal_chunks[(verb, "unknown verb")] += 1
                    if (g["game_id"], t + 1) in SPECIAL:
                        print("NUMERIC-ITEM", g["game_id"], "turn", t + 1, "seat", s, str(exc), "raw:", cmds)
                        for u in [a[0] for v, a in cmds if v in ("PICK", "PLANT")]:
                            print("   unit", u, "carry before", corpus.unit_by_id(before, u)["carry"],
                                  "after", corpus.unit_by_id(after, u)["carry"],
                                  "shack before", before["inventories"][s], "after", after["inventories"][s])
            if bad:
                continue
            pre = {u["id"]: (u["x"], u["y"], u["ms"], u["player"]) for u in game.units}
            targets = {**parsed[0]["MOVE"], **parsed[1]["MOVE"]}
            game.apply_moves(targets)
            got = {u["id"]: (u["x"], u["y"]) for u in game.units}
            want = {u["id"]: (u["x"], u["y"]) for u in after["units"]}
            for uid in set(got) & set(want):
                if got[uid] == want[uid] or uid not in targets:
                    continue
                x0, y0, ms, pl = pre[uid]
                g2 = make_game(g, before)
                d = g2.distances([(x0, y0)]).get(targets[uid])
                if d is not None and d <= ms:
                    tie["within-speed difference (a cascade of a teammate's random tie-break)"] += 1
                    continue
                ties = equal_best_cells(g2, (x0, y0), targets[uid], ms)
                if want[uid] in ties:
                    tie["platform's cell is in referee.py's equal-best set (random tie-break)"] += 1
                    continue
                mates = {(u["x"], u["y"]) for u in after["units"] + before["units"]
                         if u["player"] == pl and u["id"] != uid}
                stayed = want[uid] == (x0, y0)
                blocked = bool(ties & mates)
                tie[("stayed put" if stayed else "moved elsewhere")
                    + (", a teammate on a tie cell (platform: 'target blocked')" if blocked
                       else ", NO teammate on any tie cell — unexplained")] += 1
            if (g["game_id"], t + 1) in SPECIAL:
                print("SAME-TURN PLANT+CHOP", g["game_id"], "turn", t + 1, "seat0:", lines[0], "| seat1:", lines[1])
                c = (10, 7)
                print("   tree at", c, "before", corpus.plant_at(before, *c), "after (platform)", corpus.plant_at(after, *c))
                print("   units on it before:", [u["id"] for u in before["units"] if (u["x"], u["y"]) == c])
    print("== every move difference, classified ==")
    for k, v in tie.most_common():
        print("%8d  %s" % (v, k))
    print("== command shapes referee.py rejects as fatal but the platform executed ==")
    for k, v in illegal_chunks.most_common(12):
        print("%8d  %s" % (v, k))
    print("== time-strike lines in the recordings ==")
    with gzip.open(corpus.GAMES, "rt") as handle:
        for line in handle:
            game = json.loads(line)
            for i, fr in enumerate(game["frames"]):
                s = fr.get("summary") or ""
                if "strike" in s or "timeout" in s.lower():
                    print("  game", game["gameId"], "frame", i, "|",
                          " / ".join(l for l in s.splitlines() if "strike" in l or "time" in l.lower()))


if __name__ == "__main__":
    main()
