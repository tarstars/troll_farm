#!/usr/bin/env python3
"""Measure turn-by-turn Python simulator conformance against official replay states."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_state import decode_replay, to_game_state  # noqa: E402
from sim.engine import step  # noqa: E402

RAW = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
ITEM_NAMES = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")


def action_commands(line: str | None) -> list[str]:
    commands = [
        command.strip()
        for command in re.split(r"[;\n]", line or "")
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]
    normalized = []
    for command in commands:
        fields = command.split()
        if (
            fields
            and fields[0].upper() in ("PICK", "PLANT")
            and len(fields) >= 3
            and fields[2].isdigit()
        ):
            index = int(fields[2])
            if 0 <= index < len(ITEM_NAMES):
                fields[2] = ITEM_NAMES[index]
                command = " ".join(fields)
        normalized.append(command)
    return normalized


def effective_chop_unit_ids(commands: list[str]) -> list[int]:
    """Return CHOP ids that survive the referee's first-command-per-unit rule."""

    used = set()
    chops = []
    for command in commands:
        fields = command.split()
        if len(fields) < 2 or fields[0] in ("TRAIN", "WAIT"):
            continue
        unit_id = int(fields[1])
        if unit_id in used:
            continue
        used.add(unit_id)
        if fields[0] == "CHOP":
            chops.append(unit_id)
    return chops


def read_trajectory(game_id: int) -> list[dict]:
    path = TRAJECTORIES / f"{game_id}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def unit_signature(game, *, include_position: bool) -> list[tuple]:
    rows = []
    for unit in game.units:
        row = (
            unit.id,
            unit.player,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
            tuple(unit.carry),
        )
        if include_position:
            row += (unit.x, unit.y)
        rows.append(row)
    return sorted(rows)


def unit_position_signature(game) -> list[tuple]:
    return sorted((unit.id, unit.x, unit.y) for unit in game.units)


def plant_signature(game) -> list[tuple]:
    return sorted(
        (
            plant.type,
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        )
        for plant in game.plants
    )


def plant_deltas(before, predicted, official) -> list[dict]:
    def by_cell(game):
        return {
            (plant.x, plant.y): {
                "type": plant.type,
                "size": plant.size,
                "health": plant.health,
                "fruits": plant.fruits,
                "cooldown": plant.cooldown,
            }
            for plant in game.plants
        }

    snapshots = [by_cell(game) for game in (before, predicted, official)]
    rows = []
    for cell in sorted(set().union(*(snapshot for snapshot in snapshots))):
        values = [snapshot.get(cell) for snapshot in snapshots]
        if values[1] != values[2]:
            rows.append(
                {
                    "cell": list(cell),
                    "before": values[0],
                    "predicted": values[1],
                    "official": values[2],
                }
            )
    return rows


def transition_differences(predicted, official) -> list[str]:
    differences = []
    if predicted.inventories != official.inventories:
        differences.append("inventories")
    if predicted.scores != official.scores:
        differences.append("scores")
    if unit_signature(predicted, include_position=False) != unit_signature(
        official, include_position=False
    ):
        differences.append("unit_economy")
    if unit_position_signature(predicted) != unit_position_signature(official):
        differences.append("unit_position")
    if plant_signature(predicted) != plant_signature(official):
        differences.append("plants")
    return differences


def classify_transition(predicted, official) -> tuple[str, list[str]]:
    differences = transition_differences(predicted, official)
    if not differences:
        return "exact", differences
    if differences == ["unit_position"]:
        return "movement_rng_only", differences
    return "material_mismatch", differences


def analyze_game(path: Path) -> dict:
    game_id = int(path.stem)
    trajectory = read_trajectory(game_id)
    chop_unit_ids_by_turn = []
    for row in trajectory:
        commands0 = action_commands(row.get("commands0"))
        commands1 = action_commands(row.get("commands1"))
        chop_unit_ids_by_turn.append(
            effective_chop_unit_ids(commands0) + effective_chop_unit_ids(commands1)
        )
    decoded = decode_replay(path, chop_unit_ids_by_turn=chop_unit_ids_by_turn)
    states = decoded["states"]
    usable = min(len(states) - 1, len(trajectory))
    seen_unit_ids = {unit["id"] for unit in states[0]["units"]}
    counts = {"exact": 0, "movement_rng_only": 0, "material_mismatch": 0}
    mismatch_fields: dict[str, int] = {}
    examples = []
    example_counts = Counter()
    command_parse_errors = []

    for turn in range(1, usable + 1):
        predicted = to_game_state(decoded["map"], states[turn - 1])
        seen_unit_ids.update(unit.id for unit in predicted.units)
        predicted.next_id = max(seen_unit_ids, default=-1) + 1
        row = trajectory[turn - 1]
        commands = [
            action_commands(row.get("commands0")),
            action_commands(row.get("commands1")),
        ]
        try:
            step(predicted, commands[0], commands[1])
        except (IndexError, ValueError) as error:
            if len(command_parse_errors) < 3:
                command_parse_errors.append(
                    {"turn": turn, "commands": commands, "error": str(error)}
                )
            continue
        official = to_game_state(decoded["map"], states[turn])
        seen_unit_ids.update(unit.id for unit in official.units)
        classification, differences = classify_transition(predicted, official)
        counts[classification] += 1
        for field in differences:
            mismatch_fields[field] = mismatch_fields.get(field, 0) + 1
        if classification != "exact" and example_counts[classification] < 3:
            example = {
                "turn": turn,
                "classification": classification,
                "differences": differences,
                "commands": commands,
            }
            if "plants" in differences:
                before = to_game_state(decoded["map"], states[turn - 1])
                example["plant_deltas"] = plant_deltas(before, predicted, official)
            examples.append(example)
            example_counts[classification] += 1

    return {
        "game_id": game_id,
        "turns": usable,
        "comparable_turns": sum(counts.values()),
        "decoded_turns": len(states) - 1,
        "trajectory_turns": len(trajectory),
        "unknown_diff_updates": len(decoded["unknown_updates"]),
        "counts": counts,
        "mismatch_fields": mismatch_fields,
        "examples": examples,
        "command_parse_errors": command_parse_errors,
    }


def aggregate(rows: list[dict]) -> dict:
    classifications = ("exact", "movement_rng_only", "material_mismatch")
    totals = {
        classification: sum(row["counts"][classification] for row in rows)
        for classification in classifications
    }
    turns = sum(row["turns"] for row in rows)
    comparable_turns = sum(row["comparable_turns"] for row in rows)
    fields = sorted({field for row in rows for field in row["mismatch_fields"]})
    return {
        "games": len(rows),
        "turns": turns,
        "comparable_turns": comparable_turns,
        "command_parse_errors": turns - comparable_turns,
        "transition_counts": totals,
        "transition_rates": {
            classification: (
                totals[classification] / comparable_turns if comparable_turns else None
            )
            for classification in classifications
        },
        "games_all_exact": sum(
            row["counts"]["exact"] == row["turns"] for row in rows
        ),
        "games_with_only_rng_drift": sum(
            row["counts"]["material_mismatch"] == 0
            and row["counts"]["movement_rng_only"] > 0
            for row in rows
        ),
        "games_with_material_mismatch": sum(
            row["counts"]["material_mismatch"] > 0 for row in rows
        ),
        "unknown_diff_updates": sum(row["unknown_diff_updates"] for row in rows),
        "mismatch_fields": {
            field: sum(row["mismatch_fields"].get(field, 0) for row in rows)
            for field in fields
        },
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=0, help="0 means every available replay")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/replay-conformance-2026-07-16.json",
    )
    args = parser.parse_args()
    paths = sorted(RAW.glob("*.json"), key=lambda path: int(path.stem))
    paths = [path for path in paths if (TRAJECTORIES / f"{path.stem}.jsonl").exists()]
    if args.games < 0:
        raise SystemExit("--games cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")
    if args.games:
        paths = paths[: args.games]
    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {executor.submit(analyze_game, path): path for path in paths}
        for index, future in enumerate(as_completed(futures), 1):
            rows.append(future.result())
            if index % 100 == 0:
                print(f"checked {index}/{len(paths)} games", flush=True)
    rows.sort(key=lambda row: row["game_id"])
    payload = {
        "schema": 1,
        "scope": "one-turn official-command simulator conformance; every turn resets to official state",
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
