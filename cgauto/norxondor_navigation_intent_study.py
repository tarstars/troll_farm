#!/usr/bin/env python3
"""Test Norxondor's movement as intent, goal, and one-turn routing layers.

Norxondor almost always commands the cell a worker will occupy at the end of the current turn,
so literal MOVE coordinates are not persistent objectives.  This study retrospectively labels
each MOVE with the worker's next non-MOVE action, then tests whether that intent is predictable
from current-state features on held games.  Future actions are labels only; predictors never see
future state.  Goal-coordinate selection remains a separate, unresolved layer.
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
    assigned_unit_commands,
    bfs,
    player_commands,
    read_trajectory,
    terrain,
)
from cgauto.top_policy_objective_study import (  # noqa: E402
    cross_validate,
    objective_label,
    row_features,
)


Cell = tuple[int, int]


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def move_target(command: str) -> Cell | None:
    fields = command.split()
    if len(fields) < 4 or fields[0].upper() != "MOVE":
        return None
    try:
        return int(fields[2]), int(fields[3])
    except ValueError:
        return None


def action_family(verb: str) -> str:
    return "FARM" if verb in ("PICK", "PLANT") else verb


def attach_next_actions(timeline: list[dict]) -> None:
    """Add future action supervision to MOVE rows of one worker timeline."""

    next_action = None
    for row in reversed(timeline):
        verb = row["verb"]
        if verb == "MOVE":
            if next_action is None:
                row["intent"] = "GO_END"
                row["action_verb"] = None
                row["action_turn"] = None
                row["goal_cell"] = None
            else:
                row["intent"] = f"GO_{action_family(next_action['verb'])}"
                row["action_verb"] = next_action["verb"]
                row["action_turn"] = next_action["turn"]
                row["goal_cell"] = next_action["cell"]
        elif verb == "WAIT":
            next_action = None
        else:
            next_action = {
                "verb": verb,
                "turn": row["turn"],
                "cell": row["cell"],
            }


def extract_game(occurrence: dict) -> dict:
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
    usable = min(len(decoded["states"]) - 1, len(trajectory))
    ordinals = {}
    next_ordinal = 0
    timelines: dict[int, list[dict]] = defaultdict(list)
    for turn in range(1, usable + 1):
        state = decoded["states"][turn - 1]
        after = decoded["states"][turn]
        units = sorted(
            [unit for unit in state["units"] if unit["player"] == player],
            key=lambda unit: unit["id"],
        )
        after_units = {
            unit["id"]: unit
            for unit in after["units"]
            if unit["player"] == player
        }
        for unit in units:
            if unit["id"] not in ordinals:
                ordinals[unit["id"]] = next_ordinal
                next_ordinal += 1
        assigned = assigned_unit_commands(parsed[turn - 1][player], units)
        plants = {(plant["x"], plant["y"]): plant for plant in state["plants"]}
        context = {
            "own_shack": board["shacks"][player],
            "opponent_shack": board["shacks"][1 - player],
            "iron": board["iron"],
            "plants": plants,
        }
        for unit in units:
            command = assigned.get(unit["id"], "WAIT")
            fields = command.split()
            verb = fields[0].upper() if fields else "WAIT"
            after_unit = after_units.get(unit["id"])
            timelines[unit["id"]].append(
                {
                    "game_id": game_id,
                    "turn": turn,
                    "unit_id": unit["id"],
                    "ordinal": ordinals[unit["id"]],
                    "role": row_features(
                        state,
                        board,
                        player,
                        unit,
                        ordinals[unit["id"]],
                        turn,
                    )["role"],
                    "verb": verb,
                    "endpoint_label": objective_label(command, context),
                    "cell": (unit["x"], unit["y"]),
                    "after_cell": (
                        (after_unit["x"], after_unit["y"])
                        if after_unit is not None
                        else None
                    ),
                    "target": move_target(command),
                    "movement_speed": unit["ms"],
                    "features": row_features(
                        state,
                        board,
                        player,
                        unit,
                        ordinals[unit["id"]],
                        turn,
                    ),
                }
            )
    for timeline in timelines.values():
        attach_next_actions(timeline)

    distance_cache: dict[Cell, dict[Cell, int]] = {}

    def distances(source: Cell) -> dict[Cell, int]:
        if source not in distance_cache:
            distance_cache[source] = bfs(board["walkable"], [source])
        return distance_cache[source]

    rows = [row for timeline in timelines.values() for row in timeline]
    for row in rows:
        if row["verb"] != "MOVE":
            continue
        current = row["cell"]
        target = row["target"]
        goal = row["goal_cell"]
        distance_to_target = distances(current).get(target) if target is not None else None
        row["target_equals_after"] = target == row["after_cell"]
        row["target_within_speed"] = (
            distance_to_target is not None
            and distance_to_target <= row["movement_speed"]
        )
        row["target_distance"] = distance_to_target
        if target is None or goal is None:
            row["target_on_shortest_route"] = None
            row["target_makes_progress"] = None
            continue
        before = distances(current).get(goal)
        first_leg = distance_to_target
        remaining = distances(target).get(goal)
        row["target_on_shortest_route"] = (
            before is not None
            and first_leg is not None
            and remaining is not None
            and before == first_leg + remaining
        )
        row["target_makes_progress"] = (
            before is not None and remaining is not None and remaining < before
        )
    return {
        "game_id": game_id,
        "rows": rows,
        "quality": {
            "decoded_turns": len(decoded["states"]) - 1,
            "trajectory_turns": len(trajectory),
            "unknown_diff_updates": len(decoded["unknown_updates"]),
        },
    }


def classifier_rows(rows: list[dict], field: str) -> list[dict]:
    return [
        {
            **row,
            "label": row[field],
            "game_fold": row["game_id"] % 5,
        }
        for row in rows
        if row["verb"] == "MOVE"
    ]


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def navigation_summary(move_rows: list[dict]) -> dict:
    by_intent = {}
    for intent in sorted({row["intent"] for row in move_rows}):
        selected = [row for row in move_rows if row["intent"] == intent]
        routed = [
            row for row in selected if row["target_on_shortest_route"] is not None
        ]
        by_intent[intent] = {
            "moves": len(selected),
            "target_equals_after": sum(row["target_equals_after"] for row in selected),
            "target_within_speed": sum(row["target_within_speed"] for row in selected),
            "shortest_route_eligible": len(routed),
            "target_on_shortest_route": sum(
                row["target_on_shortest_route"] for row in routed
            ),
            "target_on_shortest_route_rate": rate(
                sum(row["target_on_shortest_route"] for row in routed), len(routed)
            ),
        }
    routed = [row for row in move_rows if row["target_on_shortest_route"] is not None]
    distances = [
        row["target_distance"]
        for row in move_rows
        if row["target_distance"] is not None
    ]
    return {
        "moves": len(move_rows),
        "target_equals_after": sum(row["target_equals_after"] for row in move_rows),
        "target_equals_after_rate": statistics.mean(
            row["target_equals_after"] for row in move_rows
        ),
        "target_within_speed": sum(row["target_within_speed"] for row in move_rows),
        "target_within_speed_rate": statistics.mean(
            row["target_within_speed"] for row in move_rows
        ),
        "mean_target_distance": statistics.mean(distances),
        "shortest_route_eligible": len(routed),
        "target_on_shortest_route": sum(
            row["target_on_shortest_route"] for row in routed
        ),
        "target_on_shortest_route_rate": statistics.mean(
            row["target_on_shortest_route"] for row in routed
        ),
        "by_intent": by_intent,
    }


def assignment_summary(rows: list[dict]) -> dict:
    move_rows = [row for row in rows if row["verb"] == "MOVE"]
    episodes: dict[tuple, list[dict]] = defaultdict(list)
    for row in move_rows:
        key = row["game_id"], row["unit_id"], row["action_turn"], row["intent"]
        episodes[key].append(row)
    by_ordinal = {}
    for ordinal in sorted({row["ordinal"] for row in rows}):
        selected = [row for row in rows if row["ordinal"] == ordinal]
        selected_moves = [row for row in selected if row["verb"] == "MOVE"]
        by_ordinal[str(ordinal)] = {
            "rows": len(selected),
            "roles": dict(sorted(Counter(row["role"] for row in selected).items())),
            "actions": dict(sorted(Counter(row["verb"] for row in selected).items())),
            "movement_intents": dict(
                sorted(Counter(row["intent"] for row in selected_moves).items())
            ),
        }
    episode_lengths = [len(selected) for selected in episodes.values()]
    episode_intents = Counter(key[3] for key in episodes)
    return {
        "movement_episodes": len(episodes),
        "episode_intents": dict(sorted(episode_intents.items())),
        "mean_moves_per_episode": statistics.mean(episode_lengths),
        "median_moves_per_episode": statistics.median(episode_lengths),
        "maximum_moves_per_episode": max(episode_lengths),
        "by_ordinal": by_ordinal,
    }


def study(analyzed: list[dict], agent_id: int) -> dict:
    analyzed.sort(key=lambda row: row["game_id"])
    rows = [row for game in analyzed for row in game["rows"]]
    move_rows = [row for row in rows if row["verb"] == "MOVE"]
    intents = cross_validate(
        classifier_rows(move_rows, "intent"), "game_fold", list(range(5))
    )
    endpoints = cross_validate(
        classifier_rows(move_rows, "endpoint_label"), "game_fold", list(range(5))
    )
    navigation = navigation_summary(move_rows)
    accuracy_gain = intents["accuracy"] - endpoints["accuracy"]
    passed = (
        navigation["target_equals_after_rate"] >= 0.995
        and navigation["target_within_speed_rate"] >= 0.99
        and navigation["target_on_shortest_route_rate"] >= 0.90
        and intents["accuracy"] >= 0.70
        and intents["macro_f1"] >= 0.50
        and intents["worst_fold_accuracy"] >= 0.65
        and intents["worst_fold_macro_f1"] >= 0.45
        and intents["accuracy_gain"] >= 0.30
        and accuracy_gain >= 0.08
    )
    return {
        "schema": 1,
        "scope": (
            "observational Norxondor MOVE rows; next non-MOVE action is retrospective training "
            "supervision only; fivefold predictors use current state and exclude held games; "
            "shortest-route checks use observed future action cells; goal selection, "
            "counterfactual play, causal value, sealed holdout, and arena are excluded"
        ),
        "agent_id": agent_id,
        "games": len(analyzed),
        "rows": len(rows),
        "move_rows": len(move_rows),
        "quality": {
            "turn_count_matches": sum(
                game["quality"]["decoded_turns"]
                == game["quality"]["trajectory_turns"]
                for game in analyzed
            ),
            "unknown_diff_updates": sum(
                game["quality"]["unknown_diff_updates"] for game in analyzed
            ),
        },
        "navigation": navigation,
        "held_game_intent": intents,
        "held_game_literal_endpoint_class": endpoints,
        "intent_accuracy_gain_over_endpoint_class": accuracy_gain,
        "assignment": assignment_summary(rows),
        "gate": {
            "requirements": [
                "at least 99.5% of MOVE targets equal the observed end-of-turn cell",
                "at least 99% of MOVE targets are within the worker's speed",
                "at least 90% of eligible targets lie on a shortest route to the next action",
                "held intent accuracy at least 0.70 and macro F1 at least 0.50",
                "every fold intent accuracy at least 0.65 and macro F1 at least 0.45",
                "intent accuracy beats fold-majority by at least 0.30",
                "intent abstraction gains at least 0.08 accuracy over literal endpoint class",
            ],
            "passed": passed,
        },
        "decision": {
            "controller_decomposition_supported": passed,
            "next_layer": "held-game goal-cell selection per GO_* intent",
            "build_submission_candidate": False,
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
    compact = {
        "games": payload["games"],
        "rows": payload["rows"],
        "moves": payload["move_rows"],
        "navigation": payload["navigation"],
        "intent": {
            key: payload["held_game_intent"][key]
            for key in (
                "accuracy",
                "macro_f1",
                "accuracy_gain",
                "worst_fold_accuracy",
                "worst_fold_macro_f1",
            )
        },
        "endpoint_accuracy": payload["held_game_literal_endpoint_class"]["accuracy"],
        "intent_accuracy_gain_over_endpoint": payload[
            "intent_accuracy_gain_over_endpoint_class"
        ],
        "assignment": payload["assignment"],
        "gate": payload["gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
