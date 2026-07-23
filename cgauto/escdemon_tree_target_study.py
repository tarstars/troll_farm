#!/usr/bin/env python3
"""Learn Escdemon's hard new-tree choices with held-game ranking.

This study is conditional on the observed decision already being a new `MOVE_TREE` or
`MOVE_TREE_RIPE` objective.  It compares simple geometry rules with a small averaged ranking
perceptron and deliberately excludes repeated targets, singleton targets, and open-cell detours.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    adjacent,
    assigned_unit_commands,
    bfs,
    player_commands,
    read_trajectory,
    terrain,
)


Cell = tuple[int, int]


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def ceil_div(left: int, right: int) -> int:
    return (left + right - 1) // right


def candidate_features(
    *,
    candidates: list[Cell],
    plants: dict[Cell, dict],
    unit: dict,
    ordinal: int,
    turn: int,
    from_unit: dict[Cell, int],
    from_bank: dict[Cell, int],
    from_opponent_bank: dict[Cell, int],
    other_units: list[dict],
    opponents: list[dict],
    water: set[Cell],
) -> dict[Cell, dict[str, float]]:
    raw = {}
    free_capacity = max(0, unit["cc"] - sum(unit["carry"]))
    for order, cell in enumerate(candidates):
        plant = plants[cell]
        unit_distance = from_unit.get(cell, 99)
        bank_distance = from_bank.get(cell, 99)
        opponent_bank_distance = from_opponent_bank.get(cell, 99)
        travel = ceil_div(unit_distance, unit["ms"])
        home = ceil_div(bank_distance, unit["ms"])
        chops = ceil_div(plant["health"], max(1, unit["chop"]))
        cycle = travel + chops + home + 1
        wood = min(plant["size"], free_capacity)
        other_distance = min(
            (
                abs(other["x"] - cell[0]) + abs(other["y"] - cell[1])
                for other in other_units
            ),
            default=20,
        )
        opponent_distance = min(
            (
                abs(opponent["x"] - cell[0]) + abs(opponent["y"] - cell[1])
                for opponent in opponents
            ),
            default=20,
        )
        raw[cell] = {
            "unit_distance": unit_distance,
            "bank_distance": bank_distance,
            "opponent_bank_distance": opponent_bank_distance,
            "travel": travel,
            "home": home,
            "chops": chops,
            "cycle": cycle,
            "efficiency": wood / max(1, cycle),
            "health": plant["health"],
            "size": plant["size"],
            "fruits": plant["fruits"],
            "cooldown": plant["cooldown"],
            "other_distance": other_distance,
            "opponent_distance": opponent_distance,
            "near_water": int(
                any(
                    abs(cell[0] - wet[0]) + abs(cell[1] - wet[1]) == 1
                    for wet in water
                )
            ),
            "kind": plant["type"],
            "input_order": order,
        }

    rankers = {
        "unit": lambda cell: (raw[cell]["unit_distance"], cell),
        "bank": lambda cell: (raw[cell]["bank_distance"], cell),
        "cycle": lambda cell: (raw[cell]["cycle"], cell),
        "efficiency": lambda cell: (-raw[cell]["efficiency"], cell),
        "health": lambda cell: (raw[cell]["health"], cell),
        "size": lambda cell: (-raw[cell]["size"], cell),
        "fruits": lambda cell: (-raw[cell]["fruits"], cell),
        "input": lambda cell: (raw[cell]["input_order"],),
    }
    ranks = {
        name: {
            cell: index + 1
            for index, cell in enumerate(sorted(candidates, key=sort_key))
        }
        for name, sort_key in rankers.items()
    }
    phase = "early" if turn <= 25 else "mid" if turn <= 100 else "late"
    features = {}
    for cell in candidates:
        row = raw[cell]
        values: dict[str, float] = {
            "bias": 1.0,
            "travel": row["travel"] / 10,
            "home": row["home"] / 10,
            "chops": row["chops"] / 20,
            "cycle": row["cycle"] / 30,
            "efficiency": row["efficiency"],
            "health": row["health"] / 40,
            "size": row["size"] / 4,
            "fruits": row["fruits"] / 3,
            "cooldown": row["cooldown"] / 10,
            "other_distance": row["other_distance"] / 20,
            "opponent_distance": row["opponent_distance"] / 20,
            "territory": (
                row["opponent_bank_distance"] - row["bank_distance"]
            )
            / 20,
            "near_water": row["near_water"],
            f"kind={row['kind']}": 1.0,
        }
        for name in rankers:
            values[f"{name}_first"] = float(ranks[name][cell] == 1)
            values[f"{name}_reciprocal_rank"] = 1 / ranks[name][cell]
        for name, value in list(values.items()):
            if name != "bias":
                values[f"ordinal{ordinal}:{name}"] = value
        for name in (
            "cycle",
            "efficiency",
            "travel",
            "home",
            "health",
            "size",
            "fruits",
            "near_water",
        ):
            values[f"{phase}:{name}"] = values[name]
        features[cell] = values
    return features


def extract_game(occurrence: dict) -> list[dict]:
    game_id = occurrence["game_id"]
    player = occurrence["seat"]
    trajectory = read_trajectory(game_id)
    parsed = [
        [player_commands(turn, seat) for seat in (0, 1)] for turn in trajectory
    ]
    chop_ids = [
        effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
        for turn in parsed
    ]
    decoded = decode_replay(
        RAW_GAMES / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
    )
    board = terrain(decoded["map"])
    own_doors = [
        cell
        for cell in adjacent(board["shacks"][player])
        if cell in board["walkable"]
    ]
    opponent_doors = [
        cell
        for cell in adjacent(board["shacks"][1 - player])
        if cell in board["walkable"]
    ]
    from_bank = bfs(board["walkable"], own_doors)
    from_opponent_bank = bfs(board["walkable"], opponent_doors)
    ordinals = {}
    next_ordinal = 0
    prior_target: dict[int, Cell] = {}
    events = []
    usable = min(len(decoded["states"]) - 1, len(trajectory))
    for turn in range(1, usable + 1):
        state = decoded["states"][turn - 1]
        units = sorted(
            [unit for unit in state["units"] if unit["player"] == player],
            key=lambda unit: unit["id"],
        )
        for unit in units:
            if unit["id"] not in ordinals:
                ordinals[unit["id"]] = next_ordinal
                next_ordinal += 1
        assigned = assigned_unit_commands(parsed[turn - 1][player], units)
        plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
        opponents = [unit for unit in state["units"] if unit["player"] != player]
        for unit in units:
            command = assigned.get(unit["id"], "WAIT")
            fields = command.split()
            verb = fields[0].upper() if fields else "WAIT"
            if verb == "MOVE" and len(fields) >= 4:
                target = int(fields[2]), int(fields[3])
                repeated = prior_target.get(unit["id"]) == target
                prior_target[unit["id"]] = target
                if repeated or target not in plants:
                    continue
                target_is_ripe = plants[target]["fruits"] > 0
                candidates = [
                    cell
                    for cell, plant in plants.items()
                    if (plant["fruits"] > 0) == target_is_ripe
                ]
                if len(candidates) <= 1:
                    continue
                other_units = [other for other in units if other["id"] != unit["id"]]
                events.append(
                    {
                        "game_id": game_id,
                        "turn": turn,
                        "ordinal": ordinals[unit["id"]],
                        "target": target,
                        "candidates": candidates,
                        "features": candidate_features(
                            candidates=candidates,
                            plants=plants,
                            unit=unit,
                            ordinal=ordinals[unit["id"]],
                            turn=turn,
                            from_unit=bfs(
                                board["walkable"], [(unit["x"], unit["y"])]
                            ),
                            from_bank=from_bank,
                            from_opponent_bank=from_opponent_bank,
                            other_units=other_units,
                            opponents=opponents,
                            water=board["water"],
                        ),
                    }
                )
            elif verb != "WAIT":
                prior_target.pop(unit["id"], None)
    return events


def dot(weights: dict[str, float], features: dict[str, float]) -> float:
    return sum(weights.get(name, 0.0) * value for name, value in features.items())


def ranker_predict(weights: dict[str, float], event: dict) -> Cell:
    return max(
        event["candidates"],
        key=lambda cell: (dot(weights, event["features"][cell]), -cell[0], -cell[1]),
    )


def fit_ranker(events: list[dict], epochs: int = 20) -> dict[str, float]:
    weights: dict[str, float] = defaultdict(float)
    averaged: dict[str, float] = defaultdict(float)
    steps = 0
    for epoch in range(epochs):
        ordered = sorted(events, key=lambda row: ((row["game_id"] + epoch) % 997, row["turn"]))
        for event in ordered:
            predicted = ranker_predict(weights, event)
            actual = event["target"]
            if predicted != actual:
                for name, value in event["features"][actual].items():
                    weights[name] += value
                for name, value in event["features"][predicted].items():
                    weights[name] -= value
            steps += 1
            for name, value in weights.items():
                averaged[name] += value
    return {name: value / steps for name, value in averaged.items()}


def baseline_predict(event: dict, rule: str) -> Cell:
    def feature(cell: Cell, name: str) -> float:
        return event["features"][cell][name]

    if rule == "nearest_unit":
        key = lambda cell: (-feature(cell, "unit_first"), -feature(cell, "unit_reciprocal_rank"), cell)
    elif rule == "minimum_cycle":
        key = lambda cell: (-feature(cell, "cycle_first"), -feature(cell, "cycle_reciprocal_rank"), cell)
    else:
        raise ValueError(f"unknown baseline rule {rule}")
    return min(event["candidates"], key=key)


def accuracy(events: list[dict], predictions: list[Cell]) -> dict:
    exact = [prediction == event["target"] for event, prediction in zip(events, predictions)]
    return {
        "events": len(events),
        "exact": sum(exact),
        "accuracy": statistics.mean(exact),
    }


def study(events: list[dict], epochs: int = 20) -> dict:
    events.sort(key=lambda row: (row["game_id"], row["turn"], row["ordinal"]))
    baselines = {
        rule: accuracy(events, [baseline_predict(event, rule) for event in events])
        for rule in ("nearest_unit", "minimum_cycle")
    }
    held_predictions: dict[tuple[int, int, int], Cell] = {}
    folds = []
    for fold in range(5):
        train = [event for event in events if event["game_id"] % 5 != fold]
        test = [event for event in events if event["game_id"] % 5 == fold]
        weights = fit_ranker(train, epochs)
        predictions = [ranker_predict(weights, event) for event in test]
        report = accuracy(test, predictions)
        report.update(
            {
                "fold": fold,
                "train_games": len({event["game_id"] for event in train}),
                "held_games": len({event["game_id"] for event in test}),
            }
        )
        folds.append(report)
        for event, prediction in zip(test, predictions):
            held_predictions[(event["game_id"], event["turn"], event["ordinal"])] = prediction
    predictions = [
        held_predictions[(event["game_id"], event["turn"], event["ordinal"])]
        for event in events
    ]
    held = accuracy(events, predictions)
    held["folds"] = folds
    held["worst_fold_accuracy"] = min(row["accuracy"] for row in folds)
    held["by_ordinal"] = {
        str(ordinal): accuracy(
            [event for event in events if event["ordinal"] == ordinal],
            [
                prediction
                for event, prediction in zip(events, predictions)
                if event["ordinal"] == ordinal
            ],
        )
        for ordinal in sorted({event["ordinal"] for event in events})
    }
    gain = held["accuracy"] - baselines["minimum_cycle"]["accuracy"]
    passed = (
        held["accuracy"] >= 0.55
        and gain >= 0.08
        and held["worst_fold_accuracy"] >= 0.50
    )
    return {
        "schema": 1,
        "scope": (
            "conditional exact-coordinate choice for non-repeated, non-singleton Escdemon tree "
            "MOVE objectives; state/candidate features only; five-fold held-game averaged ranking "
            "perceptron; excludes objective timing, open-cell detours, TRAIN, and causal value"
        ),
        "games": len({event["game_id"] for event in events}),
        "events": len(events),
        "events_by_ordinal": dict(sorted(Counter(event["ordinal"] for event in events).items())),
        "candidate_count": {
            "mean": statistics.mean(len(event["candidates"]) for event in events),
            "median": statistics.median(len(event["candidates"]) for event in events),
            "maximum": max(len(event["candidates"]) for event in events),
        },
        "baselines": baselines,
        "ranker": {
            "algorithm": "20-epoch deterministic averaged ranking perceptron",
            **held,
            "gain_over_minimum_cycle": gain,
        },
        "conditional_tree_gate": {
            "requirements": [
                "held-game exact tree-coordinate accuracy at least 0.55",
                "gain over minimum-cycle baseline at least 0.08",
                "every held-game fold accuracy at least 0.50",
            ],
            "passed": passed,
        },
        "decision": {
            "implement_research_tree_ranker": passed,
            "build_complete_candidate": False,
            "next": (
                "Integrate the frozen tree ranker only into an offline teacher-forced policy "
                "skeleton. The complete candidate remains blocked by opening-spec generalization "
                "and MOVE_OTHER collision/waypoint recovery."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.epochs != 20:
        raise SystemExit("the discovery protocol freezes --epochs at 20")
    analysis = json.loads(args.analysis.read_text())
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == args.agent_id
    ]
    events = []
    for index, occurrence in enumerate(occurrences, 1):
        events.extend(extract_game(occurrence))
        if index % 10 == 0 or index == len(occurrences):
            print(f"decoded {index}/{len(occurrences)} games", flush=True)
    payload = study(events, args.epochs)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
