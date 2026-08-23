#!/usr/bin/env python3
r"""Phase 3b REACH -- the second number: EPISODES, not turns.

339 reach turns are not 339 independent occasions.  The idle-regeneration state persists, so one
troll standing on one replant cell contributes one reach row per turn for as long as it stands
there -- and the counterfactual is per-tick: if the option had been restored on the FIRST turn of
a run, the state on the following turn would not have been the state we replayed.

This module collapses the reach rows into maximal runs of consecutive turns for the same unit in
the same game.  The episode count is the number that should be quoted for "how many times did
this happen"; the turn count is the number that should be quoted for "how many turns were spent
in it".  Both are reported; neither is allowed to travel alone.

Run:  python3 claude_1/reach1/episode_analysis.py [--games-dir DIR] [--probe BIN]
"""
from __future__ import annotations

import argparse, glob, json, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import reach_drive                                  # noqa: E402


def concrete(target: str) -> bool:
    return target.startswith(("TREE(", "BANK(", "CELL(", "SHACK"))


def episodes_of(turns_by_unit, game_id):
    out = []
    for unit, turns in turns_by_unit.items():
        turns = sorted(turns)
        start = prev = turns[0]
        for turn in turns[1:] + [None]:
            if turn is None or turn != prev + 1:
                out.append({"game": game_id, "unit": unit, "start": start, "end": prev,
                            "turns": prev - start + 1})
                if turn is not None:
                    start = turn
            if turn is not None:
                prev = turn
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", default="~/.cache/troll-farm/reach1/games")
    ap.add_argument("--probe", default="~/.cache/troll-farm/reach1/probe-honest")
    ap.add_argument("--out", default=str(HERE / "results" / "reach-episodes-2026-08-23.json"))
    args = ap.parse_args(argv)

    probe = Path(args.probe).expanduser()
    reach_eps, nn_eps, verified = [], [], 0
    for path in sorted(glob.glob(str(Path(args.games_dir).expanduser() / "*.json.gz"))):
        game = reach_drive.drive(path, probe)
        if not game["parity"]:
            continue
        verified += 1
        reach_by_unit, nn_by_unit = defaultdict(list), defaultdict(list)
        for row in game["rows"]:
            if row["bchosen"] == "NONE" and row["bavail"] == "NONE":
                nn_by_unit[row["unit"]].append(row["turn"])
                if concrete(row["cavail"]):
                    reach_by_unit[row["unit"]].append(row["turn"])
        reach_eps += episodes_of(reach_by_unit, game["game_id"])
        nn_eps += episodes_of(nn_by_unit, game["game_id"])

    lengths = sorted(e["turns"] for e in reach_eps)
    per_game = Counter(e["game"] for e in reach_eps)
    result = {
        "verified_games": verified,
        "reach": {
            "turns": sum(lengths),
            "episodes": len(reach_eps),
            "distinct_game_unit_pairs": len({(e["game"], e["unit"]) for e in reach_eps}),
            "games_with_at_least_one_episode": len(per_game),
            "episode_turns": {"min": lengths[0], "median": lengths[len(lengths) // 2],
                              "mean": round(sum(lengths) / len(lengths), 2), "max": lengths[-1]}
            if lengths else {},
            "episode_turns_histogram": dict(sorted(Counter(lengths).items())),
            "episodes_per_game_histogram": dict(sorted(Counter(per_game.values()).items())),
            "longest": sorted(reach_eps, key=lambda e: -e["turns"])[:10],
            "all_episodes": sorted(reach_eps, key=lambda e: (e["game"], e["unit"], e["start"])),
        },
        "nothing_nothing": {
            "turns": sum(e["turns"] for e in nn_eps),
            "episodes": len(nn_eps),
        },
        "not_claimed": [
            "that 339 turns are 339 independent occasions -- they are 34 episodes",
            "that restoring the option on turn N leaves turn N+1 as replayed; the counterfactual "
            "is per-tick and divergence is not simulated",
            "anything about score",
        ],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in result["reach"].items() if k != "all_episodes"}, indent=1))
    print("written:", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
