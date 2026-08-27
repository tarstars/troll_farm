#!/usr/bin/env python3
"""Compare champion-v6 and keep-v6 real ladder replays from a hash-pinned manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.cut_fixtures import decode, narrate_fragment

UNIT = re.compile(r"^u(?P<id>\d+)=(?P<chosen>[^/]+)/(?P<available>[^/]+)/r=(?P<branch>[A-Z])/b=(?P<blocked>\d+)/k=(?P<keep>[012])$")
ACTION = re.compile(r"^(MOVE|HARVEST|CHOP|PLANT|PICK|DROP|TRAIN|WAIT)\b")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 3) if d else None


def summarize(values: list[int]) -> dict:
    return {
        "n": len(values),
        "mean": round(mean(values), 3) if values else None,
        "median": median(values) if values else None,
        "max": max(values) if values else None,
    }


def game_metrics(path: Path, seat: int) -> dict:
    replay = json.loads(path.read_text())
    rows, actions = [], []
    for frame in replay["frames"]:
        if frame.get("agentId") != seat or not frame.get("stdout"):
            continue
        fragment = narrate_fragment(frame["stdout"])
        if fragment:
            rows.append(decode(fragment))
        for command in frame["stdout"].split(";"):
            command = command.strip()
            match = ACTION.match(command)
            if match:
                actions.append(command.split())

    lifetimes, active = [], {}
    keep_turns = 0
    chosen_turns = 0
    for row in rows:
        present = set()
        for uid, unit in row["units"].items():
            present.add(uid)
            goal = unit["chosen"]
            chosen_turns += goal != "NONE"
            keep_turns += unit["keep"] != "0"
            if goal == "NONE":
                if uid in active:
                    lifetimes.append(active.pop(uid)[1])
            elif uid not in active or active[uid][0] != goal:
                if uid in active:
                    lifetimes.append(active[uid][1])
                active[uid] = [goal, 1]
            else:
                active[uid][1] += 1
        for uid in set(active) - present:
            lifetimes.append(active.pop(uid)[1])
    lifetimes.extend(length for _, length in active.values())

    counts = Counter(action[0] for action in actions)
    positions: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for action in actions:
        if action[0] == "MOVE" and len(action) >= 4:
            positions[action[1]].append((int(action[2]), int(action[3])))
    reversals = sum(
        1 for seq in positions.values() for i in range(2, len(seq))
        if seq[i] == seq[i - 2] and seq[i] != seq[i - 1]
    )
    score = float(replay["scores"][seat])
    opponent = float(replay["scores"][1 - seat])
    margin = score - opponent
    return {
        "turns": len(rows), "score": score, "margin": margin,
        "outcome": "win" if margin > 0 else "loss",
        "bad_loss": margin <= -50,
        "actions": counts, "moves": counts["MOVE"],
        "working_actions": sum(counts[x] for x in ("HARVEST", "CHOP", "PLANT", "PICK", "DROP", "TRAIN")),
        "reverse_within_two_moves": reversals,
        "goal_lifetimes": lifetimes, "chosen_turns": chosen_turns, "keep_turns": keep_turns,
    }


def arm_summary(games: list[dict]) -> dict:
    actions = Counter()
    for game in games:
        actions.update(game["actions"])
    turns = sum(g["turns"] for g in games)
    moves = sum(g["moves"] for g in games)
    work = sum(g["working_actions"] for g in games)
    commands = sum(sum(g["actions"].values()) for g in games)
    lifetimes = [v for g in games for v in g["goal_lifetimes"]]
    groups = {}
    for label, selected in (
        ("won", [g for g in games if g["outcome"] == "win"]),
        ("lost", [g for g in games if g["outcome"] == "loss"]),
        ("lost_badly_margin_le_minus_50", [g for g in games if g["bad_loss"]]),
    ):
        groups[label] = {
            "games": len(selected),
            "mean_score": round(mean(g["score"] for g in selected), 3) if selected else None,
            "mean_margin": round(mean(g["margin"] for g in selected), 3) if selected else None,
            "move_command_share_pct": pct(sum(g["moves"] for g in selected), sum(sum(g["actions"].values()) for g in selected)),
            "working_command_share_pct": pct(sum(g["working_actions"] for g in selected), sum(sum(g["actions"].values()) for g in selected)),
        }
    return {
        "games": len(games), "turns": turns,
        "mean_score": round(mean(g["score"] for g in games), 3),
        "mean_margin": round(mean(g["margin"] for g in games), 3),
        "actions": dict(sorted(actions.items())),
        "move_command_share_pct": pct(moves, commands),
        "working_command_share_pct": pct(work, commands),
        "reverse_within_two_moves": sum(g["reverse_within_two_moves"] for g in games),
        "reverse_per_100_moves": round(100 * sum(g["reverse_within_two_moves"] for g in games) / moves, 3) if moves else None,
        "goal_lifetimes": summarize(lifetimes),
        "turns_with_chosen_goal": sum(g["chosen_turns"] for g in games),
        "turns_with_keep_active": sum(g["keep_turns"] for g in games),
        "splits": groups,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--games-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    by_arm = defaultdict(list)
    errors = []
    for entry in manifest["entries"]:
        path = args.games_dir / f"{entry['game_id']}.json"
        if not path.exists() or digest(path) != entry["file_sha256"]:
            errors.append(f"missing or hash-mismatched replay {entry['game_id']}")
            continue
        key = "keep_v6" if str(entry["source_sha256_prefix"]).startswith("04e3db43") else "champion_v6"
        by_arm[key].append(game_metrics(path, int(entry["our_seat"])))
    result = {
        "schema_version": 1,
        "manifest_sha256": digest(args.manifest),
        "errors": errors,
        "arms": {key: arm_summary(games) for key, games in sorted(by_arm.items())},
        "unavailable_from_v6_replays": [
            "why a goal ceased to be valid (opponent took tree/cell/plant)",
            "contested-tree episode outcome",
            "score composition by resource and timing",
        ],
        "dead_condition": len(by_arm["keep_v6"]) < 20,
        "dead_condition_reason": f"only {len(by_arm['keep_v6'])} keep-rule games versus {len(by_arm['champion_v6'])} champion games",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if errors:
        raise SystemExit("; ".join(errors))


if __name__ == "__main__":
    main()
