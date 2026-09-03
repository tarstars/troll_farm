"""Orchard 6's and the champion's real funding turns on the panel maps, per map and seat, read
off the h2h panel results (`claude_1/h2h-panel/results/champion-vs-orchard6.json`: orchard 6 is
the `bot`, the champion the `policy`; every row names the policy's seat)."""
import json
import sys


def load(path="../h2h-panel/results/champion-vs-orchard6.json"):
    d = json.load(open(path))
    rows = [v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "bot_trains" in v[0]][0]
    out = {}
    for r in rows:
        seat_bot = 1 - r["policy_seat"]
        bt = [t for t in r["bot_trains"] if t["spawned"]]
        pt = [t for t in r["policy_trains"] if t["spawned"]]
        out[(r["map_hash"], seat_bot)] = {
            "orchard6_second": bt[0]["turn"] if len(bt) > 0 else None,
            "orchard6_second_talents": bt[0]["talents"] if len(bt) > 0 else None,
            "orchard6_third": bt[1]["turn"] if len(bt) > 1 else None,
            "orchard6_third_talents": bt[1]["talents"] if len(bt) > 1 else None,
            "champion_second": pt[0]["turn"] if pt else None,
            "champion_second_talents": pt[0]["talents"] if pt else None,
            "start_inventory": r["start_inventory"],
            "orchard6_score": r["bot_score"], "champion_score": r["policy_score"],
        }
    return out


if __name__ == "__main__":
    b = load()
    import statistics
    print(len(b), "map-seats")
    print("orchard6 third median", statistics.median([v["orchard6_third"] for v in b.values() if v["orchard6_third"]]))
    json.dump({f"{k[0]}:{k[1]}": v for k, v in b.items()}, open("baseline-orchard6-panel.json", "w"), indent=0)
