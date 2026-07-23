#!/usr/bin/env python3
"""Measure the exact live bot's renewable-supply timeline in paired local self-play."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from sim.engine import has_stalled, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
CHECKPOINTS = (1, 50, 100, 150, 200, 250, 300)
SUPPLY_VERBS = ("HARVEST", "PICK", "PLANT")
FRUIT_KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")


def side_snapshot(game, seat: int) -> dict:
    inventory = game.inventories[seat]
    return {
        "score": game.scores[seat],
        "wood": inventory[5],
        "fruit": sum(inventory[:4]),
        "fruit_by_kind": dict(zip(FRUIT_KINDS, inventory[:4])),
        "trees": len(game.plants),
        "ripe_trees": sum(plant.fruits > 0 for plant in game.plants),
        "units": sum(unit.player == seat for unit in game.units),
    }


def run_seed(seed: int, binary: Path) -> list[dict]:
    game = generate_bronze(seed)
    initial_trees = len(game.plants)
    sessions = [BotSession(binary, game, 0), BotSession(binary, game, 1)]
    events: list[list[dict]] = [[], []]
    checkpoints: list[dict[int, dict]] = [{}, {}]
    first_empty: list[dict | None] = [None, None]
    grace_plant_commands: list[list[dict]] = [[], []]
    grace_recoveries: list[dict] = []
    turns_until_end = 0
    ended_by_stall = False
    try:
        while game.turn <= 300:
            turn = game.turn
            board_was_empty = not game.plants
            if not game.plants:
                for seat in (0, 1):
                    if first_empty[seat] is None:
                        first_empty[seat] = {"turn": turn, **side_snapshot(game, seat)}
            if turn in CHECKPOINTS:
                for seat in (0, 1):
                    checkpoints[seat][turn] = side_snapshot(game, seat)
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for seat in (0, 1):
                for command in commands[seat]:
                    fields = command.split()
                    if fields:
                        events[seat].append(
                            {"turn": turn, "verb": fields[0].upper(), "command": command}
                        )
                        if board_was_empty and fields[0].upper() == "PLANT":
                            grace_plant_commands[seat].append(
                                {"turn": turn, "command": command}
                            )
            step(game, commands[0], commands[1])
            if board_was_empty and game.plants:
                grace_recoveries.append(
                    {
                        "turn": turn,
                        "planting_seats": [
                            seat
                            for seat in (0, 1)
                            if any(
                                command.split()
                                and command.split()[0].upper() == "PLANT"
                                for command in commands[seat]
                            )
                        ],
                        "trees_after": len(game.plants),
                    }
                )
            if not game.plants:
                for seat in (0, 1):
                    if first_empty[seat] is None:
                        first_empty[seat] = {
                            "turn": game.turn,
                            **side_snapshot(game, seat),
                        }
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("the exact baseline unexpectedly wrote to stderr")

    terminal_turn = game.turn - 1
    for seat in (0, 1):
        terminal_snapshot = side_snapshot(game, seat)
        for turn in CHECKPOINTS:
            checkpoints[seat].setdefault(turn, terminal_snapshot)

    rows = []
    for seat in (0, 1):
        counts = Counter(event["verb"] for event in events[seat])
        supply = [event for event in events[seat] if event["verb"] in SUPPLY_VERBS]
        rows.append(
            {
                "seed": seed,
                "seat": seat,
                "initial_trees": initial_trees,
                "final": side_snapshot(game, seat),
                "command_counts": dict(counts),
                "supply_events": supply,
                "supply_counts_after_150": {
                    verb: sum(
                        event["verb"] == verb and event["turn"] >= 150
                        for event in supply
                    )
                    for verb in SUPPLY_VERBS
                },
                "last_supply_turn": {
                    verb: max(
                        (event["turn"] for event in supply if event["verb"] == verb),
                        default=None,
                    )
                    for verb in SUPPLY_VERBS
                },
                "checkpoints": {str(turn): snapshot for turn, snapshot in checkpoints[seat].items()},
                "first_empty": first_empty[seat],
                "grace_plant_commands": grace_plant_commands[seat],
                "grace_recoveries": grace_recoveries,
                "terminal_turn": terminal_turn,
                "ended_by_stall": ended_by_stall,
            }
        )
    return rows


def summarize_rows(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("cannot summarize empty supply rows")
    verbs = sorted({verb for row in rows for verb in row["command_counts"]})
    result = {
        "side_games": len(rows),
        "mean_final_score": statistics.mean(row["final"]["score"] for row in rows),
        "mean_final_wood": statistics.mean(row["final"]["wood"] for row in rows),
        "mean_command_counts": {
            verb: statistics.mean(row["command_counts"].get(verb, 0) for row in rows)
            for verb in verbs
        },
        "mean_supply_after_150": {
            verb: statistics.mean(row["supply_counts_after_150"][verb] for row in rows)
            for verb in SUPPLY_VERBS
        },
        "sides_with_supply_after_150": {
            verb: sum(row["supply_counts_after_150"][verb] > 0 for row in rows)
            for verb in SUPPLY_VERBS
        },
        "median_last_supply_turn": {},
        "mean_tree_count": {},
        "mean_ripe_tree_count": {},
        "terminal": {
            "ended_by_stall": sum(row.get("ended_by_stall", False) for row in rows),
            "median_turn": statistics.median(
                row.get("terminal_turn", 300) for row in rows
            ),
        },
        "grace_window": {
            "side_games_with_plant_command": sum(
                bool(row.get("grace_plant_commands")) for row in rows
            ),
            "plant_commands": sum(
                len(row.get("grace_plant_commands", [])) for row in rows
            ),
            "matches_with_successful_replant": len(
                {
                    row["seed"]
                    for row in rows
                    if row.get("grace_recoveries")
                }
            ),
            "successful_replants": sum(
                len(row.get("grace_recoveries", []))
                for row in rows
                if row.get("seat") == 0
            ),
        },
        "first_empty": {
            "sides": 0,
            "median_turn": None,
            "sides_with_fruit": 0,
            "mean_fruit_by_kind": {kind: 0 for kind in FRUIT_KINDS},
        },
    }
    for verb in SUPPLY_VERBS:
        turns = [
            row["last_supply_turn"][verb]
            for row in rows
            if row["last_supply_turn"][verb] is not None
        ]
        result["median_last_supply_turn"][verb] = statistics.median(turns) if turns else None
    for turn in CHECKPOINTS:
        key = str(turn)
        result["mean_tree_count"][key] = statistics.mean(
            row["checkpoints"][key]["trees"] for row in rows
        )
        result["mean_ripe_tree_count"][key] = statistics.mean(
            row["checkpoints"][key]["ripe_trees"] for row in rows
        )
    exhausted = [row["first_empty"] for row in rows if row.get("first_empty") is not None]
    if exhausted:
        result["first_empty"] = {
            "sides": len(exhausted),
            "median_turn": statistics.median(snapshot["turn"] for snapshot in exhausted),
            "sides_with_fruit": sum(snapshot["fruit"] > 0 for snapshot in exhausted),
            "mean_fruit_by_kind": {
                kind: statistics.mean(snapshot["fruit_by_kind"][kind] for snapshot in exhausted)
                for kind in FRUIT_KINDS
            },
        }
    return result


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=60)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/renewable-supply-baseline.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="renewable-supply-study-") as directory:
        binary = Path(directory) / "baseline"
        compile_source(BASELINE, binary, "renewable_supply_baseline")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary): seed
                for seed in range(args.seed_start, args.seed_start + args.seeds)
            }
            for future in as_completed(futures):
                rows.extend(future.result())
        rows.sort(key=lambda row: (row["seed"], row["seat"]))

    payload = {
        "schema": 1,
        "scope": "exact live local self-play supply timeline; not an arena predictor",
        "source": str(BASELINE.relative_to(REPO)),
        "seed_start": args.seed_start,
        "seeds": args.seeds,
        "jobs": args.jobs,
        "aggregate": summarize_rows(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
