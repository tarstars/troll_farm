#!/usr/bin/env python3
"""Measure the actionable window for dynamic training-resource denial."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
from collections import Counter
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bot.main import ITEM_INDEX, training_cost  # noqa: E402
from cgauto.idle_harvest_study import (  # noqa: E402
    action_commands,
    BotSession,
    compile_source,
)
from sim.engine import step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402
from sim.terminal import focus_kind  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
TRAIN_ITEMS = ("PLUM", "LEMON", "APPLE", "IRON")


def training_command(commands: list[str]) -> tuple[int, int, int, int] | None:
    for command in commands:
        fields = command.split()
        if len(fields) == 5 and fields[0].upper() == "TRAIN":
            return tuple(int(value) for value in fields[1:])
    return None


def selected_focus_trees(game, player: int, commands: list[str], focus: str) -> list[dict]:
    units = {unit.id: unit for unit in game.units if unit.player == player}
    plants = {plant.pos: plant for plant in game.plants}
    selected = []
    for command in commands:
        fields = command.split()
        if len(fields) < 2 or fields[0].upper() not in ("MOVE", "CHOP"):
            continue
        try:
            unit = units.get(int(fields[1]))
        except ValueError:
            continue
        if unit is None:
            continue
        if fields[0].upper() == "CHOP":
            target = unit.pos
        elif len(fields) >= 4:
            try:
                target = (int(fields[2]), int(fields[3]))
            except ValueError:
                continue
        else:
            continue
        plant = plants.get(target)
        if plant is not None and plant.type == focus:
            selected.append({"unit": unit.id, "command": command, "tree": plant.type})
    return selected


def annotate_commitment(commitment: dict, opponent_train: dict | None) -> dict:
    row = dict(commitment)
    if opponent_train is None:
        return {**row, "opponent_train": None}
    talents = tuple(opponent_train["talents"])
    cost = training_cost(1, talents)
    inventory = row["opponent_inventory"]
    deficits = {
        item: max(cost[ITEM_INDEX[item]] - inventory[ITEM_INDEX[item]], 0)
        for item in TRAIN_ITEMS
    }
    fruit_deficits = {item: deficits[item] for item in ("PLUM", "LEMON")}
    scarcer = min(("LEMON", "PLUM"), key=lambda item: (inventory[ITEM_INDEX[item]], item))
    return {
        **row,
        "opponent_train": opponent_train,
        "turns_before_train": opponent_train["turn"] - row["turn"],
        "eventual_cost": cost,
        "eventual_deficits": deficits,
        "target_deficit": deficits[row["tree"]],
        "target_is_max_train_deficit": deficits[row["tree"]] == max(deficits.values()),
        "target_is_max_plum_lemon_deficit": fruit_deficits[row["tree"]]
        == max(fruit_deficits.values()),
        "raw_inventory_scarcer_kind": scarcer,
        "raw_inventory_scarcer_deficit": deficits[scarcer],
        "raw_inventory_scarcer_is_max_train_deficit": deficits[scarcer]
        == max(deficits.values()),
        "raw_inventory_scarcer_is_max_plum_lemon_deficit": deficits[scarcer]
        == max(fruit_deficits.values()),
        "focus_matches_raw_scarcer_kind": row["focus"] == scarcer,
    }


def run_seed(seed: int, binary: Path, max_turn: int = 60) -> dict:
    game = generate_bronze(seed)
    focus = [focus_kind(game, player) for player in (0, 1)]
    sessions = [BotSession(binary, game, player) for player in (0, 1)]
    training = [None, None]
    commitments = []
    try:
        while game.turn <= max_turn and any(event is None for event in training):
            turn = game.turn
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for player in (0, 1):
                opponent = 1 - player
                opponent_units = sum(
                    unit.player == opponent for unit in game.units
                )
                if opponent_units < 2:
                    for selected in selected_focus_trees(
                        game, player, commands[player], focus[player]
                    ):
                        commitments.append(
                            {
                                "player": player,
                                "opponent": opponent,
                                "turn": turn,
                                "focus": focus[player],
                                "opponent_inventory": list(game.inventories[opponent]),
                                **selected,
                            }
                        )
            for player in (0, 1):
                talents = training_command(commands[player])
                if talents is not None and training[player] is None:
                    training[player] = {"turn": turn, "talents": list(talents)}
            step(game, commands[0], commands[1])
    finally:
        stderrs = [session.close() for session in sessions]
    if any(stderrs):
        raise RuntimeError("the exact baseline unexpectedly wrote to stderr")
    annotated = [
        annotate_commitment(commitment, training[commitment["opponent"]])
        for commitment in commitments
    ]
    return {
        "seed": seed,
        "focus": focus,
        "training": training,
        "focus_commitments_before_opponent_train": annotated,
    }


def aggregate(rows: list[dict]) -> dict:
    training = [event for row in rows for event in row["training"] if event is not None]
    commitments = [
        event
        for row in rows
        for event in row["focus_commitments_before_opponent_train"]
        if event["opponent_train"] is not None
    ]
    actionable = [event for event in commitments if event["turns_before_train"] > 0]
    return {
        "games": len(rows),
        "sides": 2 * len(rows),
        "sides_with_train_by_horizon": len(training),
        "training_turn": {
            "median": statistics.median(event["turn"] for event in training)
            if training
            else None,
            "turn_1": sum(event["turn"] == 1 for event in training),
            "by_turn_5": sum(event["turn"] <= 5 for event in training),
            "by_turn_15": sum(event["turn"] <= 15 for event in training),
            "by_turn_35": sum(event["turn"] <= 35 for event in training),
            "maximum": max((event["turn"] for event in training), default=None),
        },
        "training_specs": {
            " ".join(str(value) for value in talents): count
            for talents, count in Counter(
                tuple(event["talents"]) for event in training
            ).most_common()
        },
        "focus_commitments_before_opponent_train": len(commitments),
        "actionable_commitments_at_least_one_turn_early": len(actionable),
        "sides_with_actionable_commitment": len(
            {(row["seed"], event["player"]) for row in rows for event in row["focus_commitments_before_opponent_train"] if event.get("turns_before_train", 0) > 0}
        ),
        "actionable_target_has_positive_deficit": sum(
            event["target_deficit"] > 0 for event in actionable
        ),
        "actionable_target_is_max_train_deficit": sum(
            event["target_is_max_train_deficit"] for event in actionable
        ),
        "actionable_target_is_max_plum_lemon_deficit": sum(
            event["target_is_max_plum_lemon_deficit"] for event in actionable
        ),
        "fixed_focus_matches_raw_scarcer_kind": sum(
            event["focus_matches_raw_scarcer_kind"] for event in actionable
        ),
        "raw_scarcer_has_positive_deficit": sum(
            event["raw_inventory_scarcer_deficit"] > 0 for event in actionable
        ),
        "raw_scarcer_is_max_train_deficit": sum(
            event["raw_inventory_scarcer_is_max_train_deficit"] for event in actionable
        ),
        "raw_scarcer_is_max_plum_lemon_deficit": sum(
            event["raw_inventory_scarcer_is_max_plum_lemon_deficit"]
            for event in actionable
        ),
        "median_action_lead": statistics.median(
            event["turns_before_train"] for event in actionable
        )
        if actionable
        else None,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--max-turn", type=int, default=60)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/training-denial-telemetry.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="training-denial-study-") as directory:
        binary = Path(directory) / "baseline"
        compile_source(BASELINE, binary, "training_denial_baseline")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_seed, seed, binary, args.max_turn): seed
                for seed in range(args.seeds)
            }
            for future in as_completed(futures):
                rows.append(future.result())
        rows.sort(key=lambda row: row["seed"])

    payload = {
        "schema": 1,
        "scope": "behavior-neutral exact-live local opening telemetry; not an arena predictor",
        "source": str(BASELINE.relative_to(REPO)),
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
