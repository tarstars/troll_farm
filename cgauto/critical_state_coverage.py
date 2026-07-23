#!/usr/bin/env python3
"""Price the current etude oracle's practical envelope on terminal fixtures."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "data/analysis/live-agent-6553250/terminal-fixtures"


def terrain(map_data: dict) -> tuple[list[tuple[int, int]], set, set]:
    shacks = [None, None]
    iron = set()
    walkable = set()
    for y, row in enumerate(map_data["rows"]):
        for x, char in enumerate(row):
            if char == "0":
                shacks[0] = (x, y)
            elif char == "1":
                shacks[1] = (x, y)
            elif char == "+":
                iron.add((x, y))
            elif char == ".":
                walkable.add((x, y))
    return shacks, iron, walkable


def manhattan(left, right) -> int:
    return abs(left[0] - right[0]) + abs(left[1] - right[1])


def troll_action_count(state: dict, unit: dict, map_data: dict) -> int:
    shacks, iron, walkable = terrain(map_data)
    position = (unit["x"], unit["y"])
    plants = state.get("plants", [])
    targets = {(plant["x"], plant["y"]) for plant in plants} | iron | {
        shacks[unit["player"]]
    }
    actions = 1 + sum(target != position for target in targets)  # WAIT + MOVEs
    plant = next(
        (
            plant
            for plant in plants
            if (plant["x"], plant["y"]) == position
        ),
        None,
    )
    free = unit["cc"] - sum(unit["carry"])
    if plant is not None:
        actions += unit["chop"] > 0
        actions += unit["hp"] > 0 and free > 0 and plant["fruits"] > 0
    if manhattan(position, shacks[unit["player"]]) <= 1:
        if free > 0:
            actions += sum(value > 0 for value in state["inventories"][unit["player"]][:4])
        actions += sum(unit["carry"]) > 0
    if position in walkable and plant is None:
        actions += sum(value > 0 for value in unit["carry"][:4])
    if unit["chop"] > 0 and free > 0:
        actions += any(manhattan(position, cell) == 1 for cell in iron)
    return actions


def position_metrics(fixture: dict, frame: dict) -> dict:
    state = frame["state"]
    units_by_side = [
        sum(unit["player"] == side for unit in state["units"]) for side in (0, 1)
    ]
    joint = []
    for side in (0, 1):
        counts = [
            troll_action_count(state, unit, fixture["map"])
            for unit in state["units"]
            if unit["player"] == side
        ]
        joint.append(math.prod(counts))
    horizon_to_observed_end = max(0, fixture["n_turns"] - frame["resolved_turn"])
    strict = max(units_by_side) <= 1 and horizon_to_observed_end <= 16
    relaxed = (
        max(units_by_side) <= 2
        and len(state["plants"]) <= 2
        and horizon_to_observed_end <= 8
        and joint[0] * joint[1] <= 1_000
    )
    return {
        "game_id": fixture["game_id"],
        "resolved_turn": frame["resolved_turn"],
        "horizon_to_observed_end": horizon_to_observed_end,
        "units_by_side": units_by_side,
        "plants": len(state["plants"]),
        "joint_actions_by_side": joint,
        "immediate_joint_edges": joint[0] * joint[1],
        "documented_size_envelope": strict,
        "relaxed_probe_envelope": relaxed,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/critical-state-coverage-2026-07-16.json",
    )
    args = parser.parse_args()
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    rows = []
    for item in manifest["fixtures"]:
        fixture = json.loads((FIXTURES / item["file"]).read_text())
        rows.extend(position_metrics(fixture, frame) for frame in fixture["terminal_history"])
    aggregate = {
        "fixtures": len(manifest["fixtures"]),
        "positions": len(rows),
        "documented_size_envelope_positions": sum(
            row["documented_size_envelope"] for row in rows
        ),
        "documented_size_envelope_fixtures": len(
            {row["game_id"] for row in rows if row["documented_size_envelope"]}
        ),
        "relaxed_probe_envelope_positions": sum(
            row["relaxed_probe_envelope"] for row in rows
        ),
        "relaxed_probe_envelope_fixtures": len(
            {row["game_id"] for row in rows if row["relaxed_probe_envelope"]}
        ),
        "units_by_side_pairs": dict(
            Counter(str(row["units_by_side"]) for row in rows).most_common()
        ),
        "maximum_immediate_joint_edges": max(
            (row["immediate_joint_edges"] for row in rows), default=0
        ),
    }
    payload = {
        "schema": 1,
        "scope": "static tractability census; does not claim a solved official position",
        "oracle": {
            "node_budget": 100_000,
            "documented_envelope": "about one troll per side, small map, horizon 5-20",
            "validated_sample": {
                "file": "rust/data/etudes/sample-forced-win.txt",
                "verdict": "ForcedWin(side=0)",
                "line": ["CHOP 0", "CHOP 0", "MOVE 0 1 0", "DROP 0"],
                "score_diff": 8,
                "proof_validated": True,
            },
            "full_referee_gaps": [
                "TRAIN is absent from oracle action enumeration",
                "movement tie-breaks use the deterministic local engine, while the referee is random",
                "the conservative proof is for the modeled action set, not automatically the full arena game",
            ],
        },
        "aggregate": aggregate,
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(aggregate, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
