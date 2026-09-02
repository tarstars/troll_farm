#!/usr/bin/env python3
"""Replay the champion's 160 real ladder recordings through the package's referee.py,
one turn at a time, and count where referee.py's next state disagrees with the
platform's actual next state.  Each turn starts from the RECORDED state, so
errors do not compound.  Reviewer's instrument (local_claude_1, 2026-09-01);
not part of the package.

Run from anywhere:  python3 local_claude_1/cleanroom-review/referee_vs_recordings.py [N games]
"""
import collections
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cleanroom", "spec-work"))
sys.path.insert(0, os.path.join(ROOT, "cleanroom", "package", "harness"))
import corpus    # noqa: E402
import referee   # noqa: E402


def make_game(g, state):
    spec = {"width": g["width"], "height": g["height"], "rows": g["rows"],
            "inventories": state["inventories"],
            "trees": [{"type": p["type"], "x": p["x"], "y": p["y"], "size": p["size"],
                       "health": p["health"], "fruits": p["fruits"],
                       "cooldown": p["cooldown"]} for p in state["plants"]],
            "trolls": [{"id": u["id"], "player": u["player"], "x": u["x"], "y": u["y"],
                        "ms": u["ms"], "cc": u["cc"], "hp": u["hp"], "chop": u["chop"]}
                       for u in state["units"]]}
    game = referee.Game(spec)
    for u in game.units:
        u["carry"] = list(corpus.unit_by_id(state, u["id"])["carry"])
    return game


def line_of(cmds):
    return ";".join(v + " " + " ".join(str(a) for a in args) for v, args in cmds)


def main(limit=None):
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    end_report = collections.Counter()
    for g in corpus.games(limit):
        seat = g["seat"]
        countdown = 0
        predicted_end = None
        for t in range(g["turns"]):
            before, after = g["states"][t], g["states"][t + 1]
            game = make_game(g, before)
            game.turn = t + 1
            game.countdown = countdown
            lines = {seat: line_of(g["commands"][t]), 1 - seat: line_of(g["opp_commands"][t])}
            parsed = {}
            bad = False
            for s in (0, 1):
                try:
                    parsed[s] = referee.parse(lines[s], game, s)
                except referee.Illegal as exc:
                    counts["turns skipped: parse raised Illegal"] += 1
                    examples["illegal"].append((g["game_id"], t + 1, s, str(exc)[:60]))
                    bad = True
            if bad:
                continue
            counts["turns compared"] += 1
            pre = {u["id"]: (u["x"], u["y"], u["ms"]) for u in game.units}
            targets = {**parsed[0]["MOVE"], **parsed[1]["MOVE"]}
            game.apply_turn(parsed)
            over, why = game.ended()
            countdown = game.countdown
            if over and predicted_end is None:
                predicted_end = t + 1

            got = {u["id"]: u for u in game.units}
            want = {u["id"]: u for u in after["units"]}
            if set(got) != set(want):
                counts["unit set differs (TRAIN outcome)"] += 1
                examples["unit set"].append((g["game_id"], t + 1, sorted(got), sorted(want)))
            for uid in set(got) & set(want):
                a, b = got[uid], want[uid]
                if (a["x"], a["y"]) != (b["x"], b["y"]):
                    x0, y0, ms = pre[uid]
                    tgt = targets.get(uid)
                    far = None
                    if tgt is not None:
                        d = referee.Game.distances(game, [(x0, y0)]).get(tgt)
                        far = d is None or d > ms
                    key = ("unit position differs: target beyond speed (tie-break zone)" if far
                           else "unit position differs: target within speed" if tgt is not None
                           else "unit position differs: no MOVE issued")
                    counts[key] += 1
                    examples[key].append((g["game_id"], t + 1, uid, (x0, y0), tgt, (a["x"], a["y"]), (b["x"], b["y"])))
                if a["carry"] != list(b["carry"]):
                    counts["unit carry differs"] += 1
                    examples["carry"].append((g["game_id"], t + 1, uid, a["carry"], b["carry"]))
                if (a["ms"], a["cc"], a["hp"], a["chop"]) != (b["ms"], b["cc"], b["hp"], b["chop"]):
                    counts["unit talents differ"] += 1
            for p in (0, 1):
                if game.inventories[p] != list(after["inventories"][p]):
                    counts["inventory differs"] += 1
                    examples["inventory"].append((g["game_id"], t + 1, p, game.inventories[p], after["inventories"][p]))
            gt = {(x["x"], x["y"]): x for x in game.trees}
            wt = {(x["x"], x["y"]): x for x in after["plants"]}
            if set(gt) != set(wt):
                counts["tree set differs (PLANT/death)"] += 1
                examples["tree set"].append((g["game_id"], t + 1, sorted(set(gt) ^ set(wt))))
            for c in set(gt) & set(wt):
                a, b = gt[c], wt[c]
                if a["type"] != b["type"]:
                    counts["tree type differs"] += 1
                if a["size"] != b["size"]:
                    counts["tree size differs"] += 1
                    examples["size"].append((g["game_id"], t + 1, c, a["size"], b["size"]))
                if a["fruits"] != b["fruits"]:
                    counts["tree fruits differ"] += 1
                    examples["fruits"].append((g["game_id"], t + 1, c, a["fruits"], b["fruits"]))
                if a["health"] != b["health"]:
                    counts["tree health differs (decoder-inferred field)"] += 1
                    examples["health"].append((g["game_id"], t + 1, c, a["health"], b["health"]))
                if a["cooldown"] != b["cooldown"]:
                    counts["tree cooldown differs (decoder-inferred field)"] += 1
                    examples["cooldown"].append((g["game_id"], t + 1, c, a["cooldown"], b["cooldown"]))
        actual = g["turns"]
        if actual == 300 and predicted_end is None:
            end_report["300-turn game: referee.py also never ended it"] += 1
        elif predicted_end == actual:
            end_report["early end predicted on the same turn"] += 1
        elif predicted_end is None:
            end_report["early end NOT predicted"] += 1
            examples["end"].append((g["game_id"], actual, None))
        else:
            end_report["end predicted on a different turn"] += 1
            examples["end"].append((g["game_id"], actual, predicted_end))
        counts["games"] += 1
    print("== counts ==")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("%8d  %s" % (v, k))
    print("== endings ==")
    for k, v in end_report.items():
        print("%8d  %s" % (v, k))
    print("== examples ==")
    for k, v in examples.items():
        print(k, len(v))
        for e in v[:6]:
            print("   ", e)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
