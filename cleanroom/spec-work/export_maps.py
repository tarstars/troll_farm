#!/usr/bin/env python3
"""Freeze a map slice for the clean-room harness.

The maps are the *real* starting states of recorded ranked matches, not
generated ones: the package therefore carries no map generator, and every map in
it is one the platform actually dealt.  24 matches are taken, six of each map
height (8, 9, 10, 11), by ascending match id so the choice is not a selection.
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "package", "harness", "maps")
PER_HEIGHT = 6


def main():
    picked = collections.defaultdict(list)
    for game in corpus.games():
        if len(picked[game["height"]]) >= PER_HEIGHT:
            continue
        state = game["states"][0]
        picked[game["height"]].append({
            "map_id": "m%d" % game["game_id"],
            "source": "starting state of ranked match %d" % game["game_id"],
            "width": game["width"],
            "height": game["height"],
            "rows": game["rows"],
            "inventories": [list(inv) for inv in state["inventories"]],
            "trees": [{"type": p["type"], "x": p["x"], "y": p["y"], "size": p["size"],
                       "health": p["health"], "fruits": p["fruits"],
                       "cooldown": p["cooldown"]}
                      for p in sorted(state["plants"], key=lambda p: (p["y"], p["x"]))],
            "trolls": [{"id": u["id"], "player": u["player"], "x": u["x"], "y": u["y"],
                        "ms": u["ms"], "cc": u["cc"], "hp": u["hp"], "chop": u["chop"]}
                       for u in sorted(state["units"], key=lambda u: u["id"])],
        })
        if all(len(picked[h]) >= PER_HEIGHT for h in (8, 9, 10, 11)):
            break
    os.makedirs(OUT, exist_ok=True)
    written = []
    for height in sorted(picked):
        for m in picked[height]:
            path = os.path.join(OUT, "%s.json" % m["map_id"])
            with open(path, "w") as handle:
                json.dump(m, handle, indent=1, sort_keys=True)
            written.append(os.path.basename(path))
    print("wrote %d maps: %s" % (len(written), " ".join(sorted(written))))


if __name__ == "__main__":
    main()
