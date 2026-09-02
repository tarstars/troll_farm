#!/usr/bin/env python3
"""The two endgame signatures and the roster, read from an `h2h.py --replays` file (Track P, rung 1's loss read;
card 20260902-norxondor-port, the two signatures carried from Track E's read).

Every game is replayed through the same referee the run used (`bench.make_referee`, `h2h.apply_pair`, `grow`),
so each turn has the pre-turn roster and the end has the standing trees. Per game and seat:
  * MOVE per troll-turn in turns 251-300: MOVE commands by the seat over turns >= 251 that were played, divided
    by the seat's troll-turns over the same turns (a game that ends before 251 contributes nothing);
  * tree-size units standing at the end: the sum of `size` over every plant still on the board when the game
    ended (a felled tree leaves the board); the same for both seats, so it is one number a game;
  * the roster (trolls on the board) before turn 150 and at the end.
Prints the policy's and the opponent's medians and means, and writes a JSON beside the replays.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h2h                                   # noqa: E402  (brings bench and the referee)
import bench                                 # noqa: E402

LATE_FROM = 251
ROSTER_AT = 150


def replay_game(rec, draw, rep):
    ref = bench.make_referee(rec, draw)
    seat = rep["policy_seat"]
    late_moves = {0: 0, 1: 0}
    late_troll_turns = {0: 0, 1: 0}
    roster_150 = {0: None, 1: None}
    for row in rep["turns"]:
        t = row["turn"]
        roster = {s: sum(1 for u in ref.units.values() if u["player"] == s) for s in (0, 1)}
        if t == ROSTER_AT:
            roster_150 = dict(roster)
        if t >= LATE_FROM:
            for s, key in ((0, "seat0"), (1, "seat1")):
                moves = sum(1 for c in row[key].split(";") if c.strip().upper().startswith("MOVE "))
                late_moves[s] += moves
                late_troll_turns[s] += roster[s]
        h2h.apply_pair(ref, row["seat0"], row["seat1"])
        ref.grow()
    ended = len(rep["turns"])
    roster_end = {s: sum(1 for u in ref.units.values() if u["player"] == s) for s in (0, 1)}
    if roster_150[0] is None:            # the game ended before turn 150: the end roster stands for it
        roster_150 = dict(roster_end)
    standing = sum(p["size"] for p in ref.plants.values())
    standing_trees = len(ref.plants)
    out = {"map_hash": rep["map_hash"], "policy_seat": seat, "turns": ended, "standing_size_units": standing,
           "standing_trees": standing_trees}
    for who, s in (("policy", seat), ("opponent", 1 - seat)):
        out[who] = {"late_moves": late_moves[s], "late_troll_turns": late_troll_turns[s],
                    "move_per_troll_turn_251_300": (late_moves[s] / late_troll_turns[s]) if late_troll_turns[s] else None,
                    "roster_150": roster_150[s], "roster_end": roster_end[s]}
    return out


def summarise(games):
    def stats(vals):
        vals = [v for v in vals if v is not None]
        return {"n": len(vals), "median": round(statistics.median(vals), 3) if vals else None,
                "mean": round(statistics.mean(vals), 3) if vals else None}
    late = [g for g in games if g["policy"]["late_troll_turns"] > 0]
    summ = {"games": len(games), "games_reaching_turn_251": len(late),
            "standing_size_units_at_end": stats([g["standing_size_units"] for g in games]),
            "standing_trees_at_end": stats([g["standing_trees"] for g in games])}
    for who in ("policy", "opponent"):
        pooled_moves = sum(g[who]["late_moves"] for g in late)
        pooled_tt = sum(g[who]["late_troll_turns"] for g in late)
        summ[who] = {
            "move_per_troll_turn_251_300_pooled": round(pooled_moves / pooled_tt, 3) if pooled_tt else None,
            "move_per_troll_turn_251_300_per_game": stats([g[who]["move_per_troll_turn_251_300"] for g in late]),
            "roster_150": stats([g[who]["roster_150"] for g in games]),
            "roster_end": stats([g[who]["roster_end"] for g in games]),
        }
    return summ


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--replays", type=Path, required=True)
    ap.add_argument("--panel", type=Path, default=HERE / "panel-200-seed1.jsonl")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()
    plan = {rec["map_hash"]: (rec, draw) for rec, draw in h2h.load_panel(args.panel)}
    games = []
    with open(args.replays) as fh:
        for line in fh:
            if line.strip():
                rep = json.loads(line)
                rec, draw = plan[rep["map_hash"]]
                games.append(replay_game(rec, draw, rep))
    summ = summarise(games)
    report = {"replays": h2h.rel(args.replays), "replays_sha256": h2h.sha_file(args.replays),
              "panel_sha256": h2h.sha_file(args.panel), "summary": summ, "games": games}
    print(json.dumps(summ, indent=1))
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=1) + "\n")
        print(f"-> {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
