#!/usr/bin/env python3
"""Recover and held-game test Norxondor's staged workforce ladder.

The study treats official replay states as teacher-forced observations.  It asks whether a
compact online rule reproduces successful TRAIN decisions: at workforce size ``n``, wait until
the stage's minimum spec is affordable, then train the componentwise maximum affordable spec
clamped by that stage's observed caps.  Cross-validation learns both minima and caps without
the held games.  It does not claim that another continuation policy will generate the same
inventories, so passing this study authorizes a research controller rather than a submission.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
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
    player_commands,
    read_trajectory,
    training_cost,
)


Spec = tuple[int, int, int, int]
STAT_INVENTORY_INDICES = (0, 1, 2, 4)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def can_afford(inventory: list[int], cost: list[int], has_iron: bool) -> bool:
    """Apply the game rule that iron is free on maps without an iron source."""

    return all(
        (index == 4 and not has_iron) or inventory[index] >= cost[index]
        for index in STAT_INVENTORY_INDICES
    )


def infer_ladder(occurrences: list[dict], games: set[int] | None = None) -> dict[int, dict]:
    """Infer each stage's affordability floor and componentwise stat caps."""

    by_stage: dict[int, list[Spec]] = defaultdict(list)
    for occurrence in occurrences:
        if games is not None and occurrence["game_id"] not in games:
            continue
        for event in occurrence["training_events"]:
            by_stage[event["n_before"]].append(tuple(event["spec"]))
    return {
        stage: {
            "base": tuple(min(spec[index] for spec in specs) for index in range(4)),
            "cap": tuple(max(spec[index] for spec in specs) for index in range(4)),
        }
        for stage, specs in sorted(by_stage.items())
    }


def proposed_spec(row: dict, ladder: dict[int, dict]) -> Spec | None:
    """Return this ladder's TRAIN spec for one pre-command state, if any."""

    stage = row["n"]
    if stage not in ladder:
        return None
    rung = ladder[stage]
    base: Spec = tuple(rung["base"])
    inventory = row["inventory"]
    has_iron = row["has_iron"]
    if not can_afford(inventory, training_cost(stage, base), has_iron):
        return None

    cap: Spec = tuple(rung["cap"])
    available = []
    for stat_index, inventory_index in enumerate(STAT_INVENTORY_INDICES):
        if inventory_index == 4 and not has_iron:
            level = cap[stat_index]
        else:
            level = math.isqrt(max(0, inventory[inventory_index] - stage))
        available.append(min(level, cap[stat_index]))
    return tuple(available)  # type: ignore[return-value]


def build_decision_rows(occurrences: list[dict]) -> list[dict]:
    """Decode every pre-command state for the selected archived occurrences."""

    rows = []
    for occurrence in sorted(occurrences, key=lambda row: row["game_id"]):
        game_id = occurrence["game_id"]
        seat = occurrence["seat"]
        trajectory = read_trajectory(game_id)
        parsed = [
            [player_commands(turn, player) for player in (0, 1)]
            for turn in trajectory
        ]
        chop_ids = [
            effective_chop_unit_ids(turn[0]) + effective_chop_unit_ids(turn[1])
            for turn in parsed
        ]
        decoded = decode_replay(
            RAW_GAMES / f"{game_id}.json", chop_unit_ids_by_turn=chop_ids
        )
        usable = min(occurrence["turns"], len(trajectory), len(decoded["states"]) - 1)
        event_by_turn = {event["turn"]: event for event in occurrence["training_events"]}
        if len(event_by_turn) != len(occurrence["training_events"]):
            raise ValueError(f"multiple successful TRAIN events on one turn in game {game_id}")
        has_iron = any("+" in line for line in decoded["map"]["rows"])
        seen_events = 0
        for turn in range(1, usable + 1):
            state = decoded["states"][turn - 1]
            own_units = [unit for unit in state["units"] if unit["player"] == seat]
            event = event_by_turn.get(turn)
            actual = tuple(event["spec"]) if event else None
            if event:
                seen_events += 1
                if event["n_before"] != len(own_units):
                    raise ValueError(
                        f"worker-count mismatch in game {game_id}, turn {turn}"
                    )
            rows.append(
                {
                    "game_id": game_id,
                    "turn": turn,
                    "n": len(own_units),
                    "inventory": list(state["inventories"][seat]),
                    "has_iron": has_iron,
                    "actual": actual,
                }
            )
        if seen_events != len(event_by_turn):
            raise ValueError(f"TRAIN event lies beyond decoded decisions in game {game_id}")
    return rows


def prediction_metrics(rows: list[dict], predictions: dict[tuple[int, int], Spec | None]) -> dict:
    actual_events = 0
    predicted_events = 0
    exact_specs = 0
    trigger_exact = 0
    false_positives = 0
    misses = 0
    wrong_specs = 0
    mismatches = []
    sequences: dict[int, dict[str, list[list[int]]]] = defaultdict(
        lambda: {"actual": [], "predicted": []}
    )
    stage_counts: dict[int, Counter] = defaultdict(Counter)
    for row in rows:
        key = row["game_id"], row["turn"]
        if key not in predictions:
            raise ValueError(f"missing prediction for {key}")
        sequence = sequences[row["game_id"]]
        actual = tuple(row["actual"]) if row["actual"] is not None else None
        predicted = predictions[key]
        actual_events += actual is not None
        predicted_events += predicted is not None
        trigger_exact += (actual is None) == (predicted is None)
        stage = stage_counts[row["n"]]
        stage["decisions"] += 1
        stage["actual_events"] += actual is not None
        stage["predicted_events"] += predicted is not None
        if actual is not None:
            sequence["actual"].append(list(actual))
        if predicted is not None:
            sequence["predicted"].append(list(predicted))
        if actual is not None and predicted == actual:
            exact_specs += 1
            stage["exact_specs"] += 1
        elif actual is None and predicted is not None:
            false_positives += 1
        elif actual is not None and predicted is None:
            misses += 1
        elif actual is not None and predicted is not None:
            wrong_specs += 1
        if actual != predicted:
            mismatches.append(
                {
                    "game_id": row["game_id"],
                    "turn": row["turn"],
                    "stage": row["n"],
                    "actual": list(actual) if actual is not None else None,
                    "predicted": list(predicted) if predicted is not None else None,
                }
            )

    sequence_exact = sum(row["actual"] == row["predicted"] for row in sequences.values())
    return {
        "decision_rows": len(rows),
        "trigger_exact": trigger_exact,
        "trigger_accuracy": trigger_exact / len(rows) if rows else None,
        "actual_events": actual_events,
        "predicted_events": predicted_events,
        "exact_specs": exact_specs,
        "spec_exact_rate": exact_specs / actual_events if actual_events else None,
        "false_positive_events": false_positives,
        "missed_events": misses,
        "wrong_spec_events": wrong_specs,
        "sequence_exact_games": sequence_exact,
        "games": len(sequences),
        "stage_counts": {str(key): dict(value) for key, value in sorted(stage_counts.items())},
        "mismatches": mismatches,
    }


def evaluate_ladder(rows: list[dict], ladder: dict[int, dict]) -> dict:
    predictions = {
        (row["game_id"], row["turn"]): proposed_spec(row, ladder) for row in rows
    }
    return prediction_metrics(rows, predictions)


def ladder_json(ladder: dict[int, dict]) -> dict:
    return {
        str(stage): {"base": list(rung["base"]), "cap": list(rung["cap"])}
        for stage, rung in sorted(ladder.items())
    }


def held_game_evaluation(
    rows: list[dict], occurrences: list[dict], folds: dict[int, int]
) -> dict:
    games = sorted({row["game_id"] for row in rows})
    predictions = {}
    fold_rows = []
    for fold in sorted(set(folds.values())):
        training_games = {game for game in games if folds[game] != fold}
        held_games = {game for game in games if folds[game] == fold}
        ladder = infer_ladder(occurrences, training_games)
        held_rows = [row for row in rows if row["game_id"] in held_games]
        held_predictions = {
            (row["game_id"], row["turn"]): proposed_spec(row, ladder)
            for row in held_rows
        }
        predictions.update(held_predictions)
        fold_rows.append(
            {
                "fold": fold,
                "training_games": len(training_games),
                "held_games": len(held_games),
                "inferred_ladder": ladder_json(ladder),
                "held_metrics": prediction_metrics(held_rows, held_predictions),
            }
        )
    result = prediction_metrics(rows, predictions)
    result["folds"] = fold_rows
    return result


def stage_summary(occurrences: list[dict], ladder: dict[int, dict]) -> dict:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        for event in occurrence["training_events"]:
            grouped[event["n_before"]].append(event)
    result = {}
    for stage, events in sorted(grouped.items()):
        turns = [event["turn"] for event in events]
        specs = Counter("/".join(map(str, event["spec"])) for event in events)
        roles = Counter(event["role"] for event in events)
        rung = ladder[stage]
        capped_max_matches = 0
        for event in events:
            capped = tuple(
                min(value, rung["cap"][index])
                for index, value in enumerate(event["max_affordable_spec"])
            )
            capped_max_matches += tuple(event["spec"]) == capped
        result[str(stage)] = {
            "events": len(events),
            "turn_median": statistics.median(turns),
            "turn_min": min(turns),
            "turn_max": max(turns),
            "zero_delay_after_base_affordable": sum(
                event["delay_after_affordable"] == 0 for event in events
            ),
            "uncapped_max_affordable_matches": sum(
                event["matches_max_affordable_spec"] for event in events
            ),
            "capped_max_affordable_matches": capped_max_matches,
            "roles": dict(roles.most_common()),
            "specs": dict(specs.most_common()),
        }
    return result


def workforce_summary(occurrences: list[dict]) -> dict:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        for worker in occurrence["workers"]:
            grouped[worker["ordinal"]].append(worker)
    by_ordinal = {}
    for ordinal, workers in sorted(grouped.items()):
        active = sum(worker["active_turns"] for worker in workers)
        productive = sum(worker["productive_turns"] for worker in workers)
        trained = [worker for worker in workers if worker["ordinal"] > 0]
        by_ordinal[str(ordinal)] = {
            "workers": len(workers),
            "active_turns": active,
            "productive_turns": productive,
            "productive_rate": productive / active if active else None,
            "mean_direct_banked_value": statistics.mean(
                worker["direct_banked_value"] for worker in workers
            ),
            "direct_payback": sum(
                worker["direct_payback_turn"] is not None for worker in trained
            ),
            "direct_payback_eligible": len(trained),
        }
    trained_workers = [
        worker
        for occurrence in occurrences
        for worker in occurrence["workers"]
        if worker["ordinal"] > 0
    ]
    return {
        "final_worker_count_distribution": dict(
            sorted(Counter(occurrence["final_worker_count"] for occurrence in occurrences).items())
        ),
        "trained_workers": len(trained_workers),
        "direct_payback": sum(
            worker["direct_payback_turn"] is not None for worker in trained_workers
        ),
        "direct_payback_rate": sum(
            worker["direct_payback_turn"] is not None for worker in trained_workers
        )
        / len(trained_workers),
        "by_ordinal": by_ordinal,
    }


def study(analysis: dict, agent_id: int, rows: list[dict]) -> dict:
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    if not occurrences:
        raise ValueError(f"agent {agent_id} has no occurrences")
    occurrence_games = {row["game_id"] for row in occurrences}
    if {row["game_id"] for row in rows} != occurrence_games:
        raise ValueError("decision-row coverage does not match occurrences")

    ladder = infer_ladder(occurrences)
    fixed = evaluate_ladder(rows, ladder)
    fivefold = held_game_evaluation(
        rows, occurrences, {game: game % 5 for game in occurrence_games}
    )
    leave_one_out = held_game_evaluation(
        rows,
        occurrences,
        {game: index for index, game in enumerate(sorted(occurrence_games))},
    )
    workforce = workforce_summary(occurrences)
    held_folds_with_events = [
        fold["held_metrics"]
        for fold in fivefold["folds"]
        if fold["held_metrics"]["actual_events"]
    ]
    worst_fold_spec_rate = min(
        fold["spec_exact_rate"] for fold in held_folds_with_events
    )
    trained_productivity = [
        row["productive_rate"]
        for ordinal, row in workforce["by_ordinal"].items()
        if int(ordinal) > 0
    ]
    gate_passed = (
        fivefold["trigger_exact"] == fivefold["decision_rows"]
        and fivefold["false_positive_events"] == 0
        and fivefold["missed_events"] == 0
        and fivefold["spec_exact_rate"] >= 0.90
        and worst_fold_spec_rate >= 0.75
        and workforce["direct_payback_rate"] == 1.0
        and min(trained_productivity) >= 0.95
    )
    return {
        "schema": 1,
        "scope": (
            "observational teacher-forced official replay states for one archived agent; "
            "successful TRAIN timing and specs only; stage minima and caps inferred without held "
            "games; worker productivity and direct score-cost payback are descriptive, not "
            "counterfactual or causal; sealed holdout and arena untouched"
        ),
        "agent_id": agent_id,
        "games": len(occurrences),
        "decision_rows": len(rows),
        "successful_train_events": sum(
            len(row["training_events"]) for row in occurrences
        ),
        "wins": sum(row["won"] for row in occurrences),
        "mean_margin": statistics.mean(row["margin"] for row in occurrences),
        "inferred_full_ladder": ladder_json(ladder),
        "stage_summary": stage_summary(occurrences, ladder),
        "full_data_reproduction": fixed,
        "fivefold_held_game": fivefold,
        "leave_one_game_out": leave_one_out,
        "workforce_observation": workforce,
        "gate": {
            "requirements": [
                "fivefold trigger exact on every decision row with no false or missed TRAIN",
                "fivefold held-spec exact rate at least 0.90",
                "each event-bearing fivefold split has held-spec exact rate at least 0.75",
                "every trained worker directly repays its fruit-score cost",
                "each trained-worker ordinal is productive on at least 95% of active turns",
            ],
            "worst_fold_spec_exact_rate": worst_fold_spec_rate,
            "passed": gate_passed,
        },
        "decision": {
            "workforce_architecture_recovered": gate_passed,
            "authorize_research_controller": gate_passed,
            "build_submission_candidate": False,
            "reason": (
                "The online ladder generalizes, but replay states are supplied by Norxondor's "
                "unrecovered continuation policy.  A local controller must demonstrate that it "
                "can fund and productively assign the ladder before any candidate is built."
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
    rows = build_decision_rows(occurrences)
    payload = study(analysis, args.agent_id, rows)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "decision_rows": payload["decision_rows"],
        "events": payload["successful_train_events"],
        "ladder": payload["inferred_full_ladder"],
        "full": {
            key: payload["full_data_reproduction"][key]
            for key in (
                "trigger_exact",
                "exact_specs",
                "false_positive_events",
                "missed_events",
            )
        },
        "fivefold": {
            key: payload["fivefold_held_game"][key]
            for key in (
                "trigger_exact",
                "decision_rows",
                "exact_specs",
                "actual_events",
                "false_positive_events",
                "missed_events",
            )
        },
        "workforce": payload["workforce_observation"],
        "gate": payload["gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
