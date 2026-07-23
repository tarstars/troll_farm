#!/usr/bin/env python3
"""Evaluate intent-specific goal selectors for Norxondor movement episodes.

The controller decomposition assigns different evidence standards to different goals.  DROP,
PICK, and MINE destinations are equivalent action cells and are audited as candidate/tie sets.
CHOP and HARVEST select strategic trees and use fivefold held-game ranking.  PLANT is audited as
a compact base-footprint invariant before a later counterfactual prototype chooses a concrete
free cell.  This is iterative discovery on consumed replays, not untouched confirmation.
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

from cgauto.escdemon_tree_target_study import (  # noqa: E402
    baseline_predict,
    candidate_features,
    fit_ranker,
    ranker_predict,
)
from cgauto.norxondor_navigation_intent_study import (  # noqa: E402
    extract_game as extract_navigation_game,
)
from cgauto.replay_conformance import effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402
from cgauto.top_player_opening_analysis import (  # noqa: E402
    RAW_GAMES,
    adjacent,
    bfs,
    player_commands,
    read_trajectory,
    terrain,
)


Cell = tuple[int, int]
TRUNCATION_COUNTS = (8, 16, 32, 64, 128)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def episode_starts(rows: list[dict]) -> list[dict]:
    timelines: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        timelines[(row["game_id"], row["unit_id"])].append(row)
    starts = []
    for timeline in timelines.values():
        timeline.sort(key=lambda row: row["turn"])
        moving = False
        for row in timeline:
            if row["verb"] == "MOVE":
                if not moving:
                    starts.append(row)
                moving = True
            else:
                moving = False
    starts.sort(key=lambda row: (row["game_id"], row["turn"], row["unit_id"]))
    return starts


def accuracy(events: list[dict], predictions: list[Cell | None]) -> dict:
    exact = [prediction == event["target"] for event, prediction in zip(events, predictions)]
    return {
        "events": len(events),
        "exact": sum(exact),
        "accuracy": statistics.mean(exact) if exact else None,
    }


def truncate_weights(weights: dict[str, float], count: int) -> dict[str, float]:
    ranked = sorted(weights.items(), key=lambda item: (-abs(item[1]), item[0]))
    return dict(ranked[:count])


def tree_selector_report(
    events: list[dict], minimum_accuracy: float, minimum_gain: float
) -> dict:
    baselines = {}
    for rule in ("nearest_unit", "minimum_cycle"):
        predictions = [
            baseline_predict(event, rule) if event["candidates"] else None
            for event in events
        ]
        baselines[rule] = accuracy(events, predictions)

    held_predictions: dict[tuple[int, int, int], Cell | None] = {}
    compact_predictions = {count: {} for count in TRUNCATION_COUNTS}
    compact_folds = {count: [] for count in TRUNCATION_COUNTS}
    folds = []
    for fold in range(5):
        training = [
            event
            for event in events
            if event["game_id"] % 5 != fold and event["covered"]
        ]
        held = [event for event in events if event["game_id"] % 5 == fold]
        weights = fit_ranker(training, 20)
        predictions = [
            ranker_predict(weights, event) if event["candidates"] else None
            for event in held
        ]
        report = accuracy(held, predictions)
        report.update(
            {
                "fold": fold,
                "training_games": len({event["game_id"] for event in training}),
                "held_games": len({event["game_id"] for event in held}),
            }
        )
        folds.append(report)
        for event, prediction in zip(held, predictions):
            held_predictions[(event["game_id"], event["turn"], event["ordinal"])] = prediction
        for count in TRUNCATION_COUNTS:
            compact_weights = truncate_weights(weights, count)
            compact = [
                ranker_predict(compact_weights, event) if event["candidates"] else None
                for event in held
            ]
            compact_report = accuracy(held, compact)
            compact_folds[count].append(
                {
                    "fold": fold,
                    "events": compact_report["events"],
                    "accuracy": compact_report["accuracy"],
                }
            )
            for event, prediction in zip(held, compact):
                compact_predictions[count][
                    (event["game_id"], event["turn"], event["ordinal"])
                ] = prediction
    predictions = [
        held_predictions[(event["game_id"], event["turn"], event["ordinal"])]
        for event in events
    ]
    held = accuracy(events, predictions)
    held.update(
        {
            "folds": folds,
            "worst_fold_accuracy": min(row["accuracy"] for row in folds),
            "gain_over_minimum_cycle": (
                held["accuracy"] - baselines["minimum_cycle"]["accuracy"]
            ),
        }
    )
    compact_reports = {}
    for count in TRUNCATION_COUNTS:
        compact = accuracy(
            events,
            [
                compact_predictions[count][
                    (event["game_id"], event["turn"], event["ordinal"])
                ]
                for event in events
            ],
        )
        compact.update(
            {
                "gain_over_minimum_cycle": (
                    compact["accuracy"] - baselines["minimum_cycle"]["accuracy"]
                ),
                "worst_fold_accuracy": min(
                    fold["accuracy"] for fold in compact_folds[count]
                ),
                "folds": compact_folds[count],
            }
        )
        compact["gate_passed"] = bool(
            compact["accuracy"] >= minimum_accuracy
            and compact["gain_over_minimum_cycle"] >= minimum_gain
            and compact["worst_fold_accuracy"] >= 0.30
        )
        compact_reports[str(count)] = compact
    candidate_counts = [len(event["candidates"]) for event in events]
    full_data_weights = fit_ranker(
        [event for event in events if event["covered"]], 20
    )
    eligible_counts = [
        count
        for count in TRUNCATION_COUNTS
        if compact_reports[str(count)]["gate_passed"]
    ]
    selected_count = min(eligible_counts) if eligible_counts else None
    return {
        "events": len(events),
        "goal_covered": sum(event["covered"] for event in events),
        "goal_coverage_rate": statistics.mean(event["covered"] for event in events),
        "candidate_count": {
            "mean": statistics.mean(candidate_counts),
            "median": statistics.median(candidate_counts),
            "maximum": max(candidate_counts),
        },
        "baselines": baselines,
        "held_ranker": held,
        "full_data_ranker": {
            "training_events": sum(event["covered"] for event in events),
            "weights": dict(sorted(full_data_weights.items())),
            "nonzero_weights": sum(value != 0 for value in full_data_weights.values()),
        },
        "compact_ranker": {
            "selected_weight_count": selected_count,
            "weights": (
                truncate_weights(full_data_weights, selected_count)
                if selected_count is not None
                else None
            ),
            "held_reports": compact_reports,
            "gate_passed": selected_count is not None,
        },
    }


def endpoint_summary(events: list[dict]) -> dict:
    result = {}
    for verb in ("DROP", "PICK", "MINE"):
        selected = [event for event in events if event["verb"] == verb]
        nearest_exact = 0
        nearest_tie = 0
        for event in selected:
            reachable = [
                candidate
                for candidate in event["candidates"]
                if candidate in event["distance"]
            ]
            if not reachable:
                continue
            minimum = min(event["distance"][candidate] for candidate in reachable)
            tied = [
                candidate
                for candidate in reachable
                if event["distance"][candidate] == minimum
            ]
            nearest_exact += event["target"] == min(tied)
            nearest_tie += event["target"] in tied
        result[verb] = {
            "episodes": len(selected),
            "goal_in_equivalent_candidates": sum(
                event["target"] in event["candidates"] for event in selected
            ),
            "goal_in_equivalent_candidates_rate": statistics.mean(
                event["target"] in event["candidates"] for event in selected
            ),
            "nearest_lexicographic_exact": nearest_exact,
            "nearest_lexicographic_exact_rate": nearest_exact / len(selected),
            "goal_in_nearest_distance_tie": nearest_tie,
            "goal_in_nearest_distance_tie_rate": nearest_tie / len(selected),
            "mean_candidate_count": statistics.mean(
                len(event["candidates"]) for event in selected
            ),
        }
    return result


def extract_game(occurrence: dict) -> dict:
    navigation = extract_navigation_game(occurrence)
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
    mine_cells = sorted(
        cell
        for cell in board["walkable"]
        if any(
            abs(cell[0] - iron[0]) + abs(cell[1] - iron[1]) == 1
            for iron in board["iron"]
        )
    )
    tree_events = {"CHOP": [], "HARVEST": []}
    endpoint_events = []
    plant_events = []
    for row in episode_starts(navigation["rows"]):
        verb = row["action_verb"]
        if verb is None:
            continue
        state = decoded["states"][row["turn"] - 1]
        unit = next(unit for unit in state["units"] if unit["id"] == row["unit_id"])
        distance = bfs(board["walkable"], [row["cell"]])
        if verb in ("DROP", "PICK", "MINE"):
            endpoint_events.append(
                {
                    "verb": verb,
                    "target": row["goal_cell"],
                    "candidates": own_doors if verb in ("DROP", "PICK") else mine_cells,
                    "distance": distance,
                }
            )
            continue
        plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
        if verb in tree_events:
            candidates = sorted(plants)
            features = (
                candidate_features(
                    candidates=candidates,
                    plants=plants,
                    unit=unit,
                    ordinal=row["ordinal"],
                    turn=row["turn"],
                    from_unit=distance,
                    from_bank=from_bank,
                    from_opponent_bank=from_opponent_bank,
                    other_units=[
                        other
                        for other in state["units"]
                        if other["player"] == player and other["id"] != row["unit_id"]
                    ],
                    opponents=[
                        other for other in state["units"] if other["player"] != player
                    ],
                    water=board["water"],
                )
                if candidates
                else {}
            )
            tree_events[verb].append(
                {
                    "game_id": game_id,
                    "turn": row["turn"],
                    "ordinal": row["ordinal"],
                    "target": row["goal_cell"],
                    "candidates": candidates,
                    "features": features,
                    "covered": row["goal_cell"] in plants,
                }
            )
            continue
        if verb == "PLANT":
            occupied = {(other["x"], other["y"]) for other in state["units"]}
            static_footprint = {
                cell
                for cell in board["walkable"]
                if from_bank.get(cell, 99) <= 3
            }
            currently_free = static_footprint - set(plants) - occupied
            goal = row["goal_cell"]
            plant_events.append(
                {
                    "target": goal,
                    "in_static_footprint": goal in static_footprint,
                    "currently_free": goal in currently_free,
                    "adjacent_existing_tree": any(
                        abs(goal[0] - cell[0]) + abs(goal[1] - cell[1]) == 1
                        for cell in plants
                    ),
                    "footprint_size": len(static_footprint),
                    "free_candidates": len(currently_free),
                }
            )
    return {
        "game_id": game_id,
        "tree_events": tree_events,
        "endpoint_events": endpoint_events,
        "plant_events": plant_events,
    }


def plant_summary(events: list[dict]) -> dict:
    return {
        "episodes": len(events),
        "goal_in_static_base_footprint": sum(
            event["in_static_footprint"] for event in events
        ),
        "goal_in_static_base_footprint_rate": statistics.mean(
            event["in_static_footprint"] for event in events
        ),
        "goal_currently_free": sum(event["currently_free"] for event in events),
        "goal_currently_free_rate": statistics.mean(
            event["currently_free"] for event in events
        ),
        "goal_adjacent_existing_tree": sum(
            event["adjacent_existing_tree"] for event in events
        ),
        "goal_adjacent_existing_tree_rate": statistics.mean(
            event["adjacent_existing_tree"] for event in events
        ),
        "mean_static_footprint_size": statistics.mean(
            event["footprint_size"] for event in events
        ),
        "mean_current_free_candidates": statistics.mean(
            event["free_candidates"] for event in events
        ),
    }


def study(analyzed: list[dict], agent_id: int) -> dict:
    analyzed.sort(key=lambda row: row["game_id"])
    endpoint_events = [
        event for game in analyzed for event in game["endpoint_events"]
    ]
    plant_events = [event for game in analyzed for event in game["plant_events"]]
    tree = {
        verb: tree_selector_report(
            [event for game in analyzed for event in game["tree_events"][verb]],
            0.40 if verb == "CHOP" else 0.35,
            0.15 if verb == "CHOP" else 0.25,
        )
        for verb in ("CHOP", "HARVEST")
    }
    endpoints = endpoint_summary(endpoint_events)
    plants = plant_summary(plant_events)
    passed = (
        all(
            endpoints[verb]["goal_in_equivalent_candidates_rate"] == 1.0
            for verb in ("DROP", "PICK", "MINE")
        )
        and endpoints["DROP"]["goal_in_nearest_distance_tie_rate"] >= 0.95
        and endpoints["MINE"]["goal_in_nearest_distance_tie_rate"] >= 0.80
        and tree["CHOP"]["held_ranker"]["accuracy"] >= 0.40
        and tree["CHOP"]["held_ranker"]["gain_over_minimum_cycle"] >= 0.15
        and tree["CHOP"]["held_ranker"]["worst_fold_accuracy"] >= 0.30
        and tree["HARVEST"]["held_ranker"]["accuracy"] >= 0.35
        and tree["HARVEST"]["held_ranker"]["gain_over_minimum_cycle"] >= 0.25
        and tree["HARVEST"]["held_ranker"]["worst_fold_accuracy"] >= 0.30
        and tree["CHOP"]["compact_ranker"]["gate_passed"]
        and tree["HARVEST"]["compact_ranker"]["gate_passed"]
        and plants["goal_in_static_base_footprint_rate"] == 1.0
    )
    return {
        "schema": 1,
        "scope": (
            "iterative Norxondor goal-selection discovery on consumed replays; DROP/PICK/MINE "
            "equivalent action-cell sets, fivefold held-game tree rankers, and descriptive "
            "PLANT footprint; oracle movement intent and future action goal define labels; no "
            "complete policy, counterfactual rollout, causal value, sealed holdout, or arena"
        ),
        "agent_id": agent_id,
        "games": len(analyzed),
        "equivalent_endpoints": endpoints,
        "tree_selectors": tree,
        "plant_footprint": plants,
        "research_gate": {
            "requirements": [
                "all DROP, PICK, and MINE goals belong to their equivalent action-cell sets",
                "at least 95% of DROP and 80% of MINE goals are in the nearest-distance tie",
                "CHOP ranker exact at least 0.40, gains 0.15 over cycle, every fold at least 0.30",
                "HARVEST ranker exact at least 0.35, gains 0.25 over cycle, every fold at least 0.30",
                "all PLANT goals belong to the static three-step base footprint",
            ],
            "passed": passed,
        },
        "decision": {
            "authorize_local_research_prototype": passed,
            "build_submission_candidate": False,
            "prototype_limit": (
                "Use equivalent nearest endpoints, held-derived tree scoring, and a deterministic "
                "free base-footprint planter. Local rollouts must establish that the joined "
                "controller funds its ladder and preserves worker productivity."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text())
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == args.agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    analyzed = []
    for index, occurrence in enumerate(occurrences, 1):
        analyzed.append(extract_game(occurrence))
        if index % 10 == 0 or index == len(occurrences):
            print(f"decoded {index}/{len(occurrences)} games", flush=True)
    payload = study(analyzed, args.agent_id)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
