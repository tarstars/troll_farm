#!/usr/bin/env python3
"""Separate Escdemon's TRAIN timing rule from its opening-spec selection.

The timing audit is conditional on the worker spec observed in each replay.  The policy-grid
audit asks a different question: can one compact turn-one Yamo planner select that eventual spec
on held games?  Keeping those questions separate prevents an oracle timing result from being
mistaken for a deployable controller.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics


Spec = tuple[int, int, int, int]


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def parse_train(command: str) -> Spec:
    fields = command.split()
    if len(fields) != 5 or fields[0] != "TRAIN":
        raise ValueError(f"bad TRAIN command {command!r}")
    return tuple(int(value) for value in fields[1:])  # type: ignore[return-value]


def read_plans(path: Path, *, policy: str, seat: int = 0) -> dict[int, Spec]:
    result = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row["policy"] != policy or int(row["seat"]) != seat:
                continue
            game_id = int(row["seed"])
            if game_id in result:
                raise ValueError(f"duplicate {policy} plan for game {game_id}")
            result[game_id] = parse_train(row["train"])
    return result


def read_grid(path: Path, *, seat: int = 0) -> tuple[dict[str, dict[int, Spec]], dict]:
    predictions: dict[str, dict[int, Spec]] = defaultdict(dict)
    metadata = {}
    parameter_fields = (
        "train_horizon",
        "preferred_min_carry",
        "max_carry_capacity",
        "preferred_min_chop",
        "max_chop_power",
        "require_preferred",
        "max_extra_eta",
        "hard_train_turn",
        "prefer_movement_ties",
    )
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if int(row["seat"]) != seat:
                continue
            policy = row["policy"]
            game_id = int(row["seed"])
            if game_id in predictions[policy]:
                raise ValueError(f"duplicate grid row for {policy}, game {game_id}")
            predictions[policy][game_id] = parse_train(row["train"])
            current = {field: int(row[field]) for field in parameter_fields}
            if policy in metadata and metadata[policy] != current:
                raise ValueError(f"policy metadata changes across rows: {policy}")
            metadata[policy] = current
    return dict(predictions), metadata


def talent_l1(left: Spec, right: Spec) -> int:
    return sum(abs(a - b) for a, b in zip(left, right))


def prediction_metrics(
    actual: dict[int, Spec], predictions: dict[int, Spec], games: list[int]
) -> dict:
    errors = [talent_l1(actual[game], predictions[game]) for game in games]
    return {
        "games": len(games),
        "exact": sum(error == 0 for error in errors),
        "exact_rate": sum(error == 0 for error in errors) / len(errors),
        "mean_talent_l1": statistics.mean(errors),
        "maximum_talent_l1": max(errors),
    }


def selection_key(
    policy: str,
    actual: dict[int, Spec],
    grid: dict[str, dict[int, Spec]],
    games: list[int],
) -> tuple:
    metrics = prediction_metrics(actual, grid[policy], games)
    return (
        -metrics["exact"],
        metrics["mean_talent_l1"],
        metrics["maximum_talent_l1"],
        policy,
    )


def select_policy(
    actual: dict[int, Spec], grid: dict[str, dict[int, Spec]], games: list[int]
) -> str:
    if not games:
        raise ValueError("cannot select a policy without training games")
    return min(grid, key=lambda policy: selection_key(policy, actual, grid, games))


def held_game_predictions(
    actual: dict[int, Spec],
    grid: dict[str, dict[int, Spec]],
    folds: dict[int, int],
) -> dict:
    games = sorted(actual)
    predictions = {}
    selected = Counter()
    fold_rows = []
    for fold in sorted(set(folds.values())):
        train = [game for game in games if folds[game] != fold]
        test = [game for game in games if folds[game] == fold]
        policy = select_policy(actual, grid, train)
        selected[policy] += len(test)
        for game in test:
            predictions[game] = grid[policy][game]
        fold_rows.append(
            {
                "fold": fold,
                "train_games": len(train),
                "test_games": len(test),
                "selected_policy": policy,
                "training_metrics": prediction_metrics(actual, grid[policy], train),
                "held_metrics": prediction_metrics(actual, grid[policy], test),
            }
        )
    result = prediction_metrics(actual, predictions, games)
    result.update(
        {
            "folds": fold_rows,
            "selected_policy_game_counts": dict(selected.most_common()),
            "predictions": {
                str(game): list(predictions[game]) for game in games
            },
        }
    )
    return result


def occurrence_rows(analysis: dict, agent_id: int) -> list[dict]:
    rows = []
    for occurrence in analysis["occurrences"]:
        if occurrence["agent_id"] != agent_id:
            continue
        events = occurrence["training_events"]
        if len(events) != 1:
            raise ValueError(
                f"game {occurrence['game_id']} has {len(events)} successful trains"
            )
        event = events[0]
        actual = tuple(event["spec"])
        maximum = tuple(event["max_affordable_spec"])
        rows.append(
            {
                "game_id": occurrence["game_id"],
                "turn": event["turn"],
                "spec": actual,
                "is_max_affordable_hp0": actual
                == (maximum[0], maximum[1], 0, maximum[3]),
                "first_affordable_turn": event["first_affordable_turn"],
                "delay_after_affordable": event["delay_after_affordable"],
            }
        )
    rows.sort(key=lambda row: row["game_id"])
    return rows


def study(
    analysis: dict,
    agent_id: int,
    baseline: dict[int, Spec],
    baseline_policy: str,
    grid: dict[str, dict[int, Spec]],
    metadata: dict,
) -> dict:
    rows = occurrence_rows(analysis, agent_id)
    games = [row["game_id"] for row in rows]
    expected = set(games)
    if set(baseline) != expected:
        raise ValueError("baseline plan coverage does not match agent games")
    for policy, predictions in grid.items():
        if set(predictions) != expected:
            raise ValueError(f"policy-grid coverage does not match for {policy}")

    actual = {row["game_id"]: row["spec"] for row in rows}
    delays = [row["delay_after_affordable"] for row in rows]
    trigger_exact = sum(delay == 0 for delay in delays)
    trigger_gate = trigger_exact / len(rows) >= 0.90 and statistics.mean(delays) <= 1.0

    signatures = {
        tuple(grid[policy][game] for game in games) for policy in sorted(grid)
    }
    best = select_policy(actual, grid, games)
    best_key = selection_key(best, actual, grid, games)[:-1]
    tied_best = sum(
        selection_key(policy, actual, grid, games)[:-1] == best_key for policy in grid
    )

    leave_one_out = held_game_predictions(
        actual, grid, {game: index for index, game in enumerate(games)}
    )
    five_fold = held_game_predictions(actual, grid, {game: game % 5 for game in games})
    baseline_metrics = prediction_metrics(actual, baseline, games)
    target_gate = (
        leave_one_out["exact"] >= baseline_metrics["exact"]
        and leave_one_out["mean_talent_l1"] <= baseline_metrics["mean_talent_l1"]
        and five_fold["exact"] >= baseline_metrics["exact"]
        and five_fold["mean_talent_l1"] <= baseline_metrics["mean_talent_l1"]
    )

    def detailed(predictions: dict[int, Spec]) -> list[dict]:
        return [
            {
                "game_id": game,
                "actual": list(actual[game]),
                "predicted": list(predictions[game]),
                "talent_l1": talent_l1(actual[game], predictions[game]),
            }
            for game in games
        ]

    return {
        "schema": 1,
        "scope": (
            "observational Escdemon one-worker replays; timing conditional on the observed "
            "target spec plus nested held-game selection over a fixed Yamo opening-policy grid; "
            "no causal worker-value, continuation, holdout, or arena evidence"
        ),
        "agent_id": agent_id,
        "games": len(games),
        "worker_invariants": {
            "one_successful_train": len(rows),
            "harvest_zero": sum(row["spec"][2] == 0 for row in rows),
            "max_affordable_hp0_at_actual_turn": sum(
                row["is_max_affordable_hp0"] for row in rows
            ),
        },
        "conditional_trigger": {
            "rule": "given the eventual target spec, train on its first affordable turn",
            "exact_turn": trigger_exact,
            "exact_rate": trigger_exact / len(rows),
            "mean_absolute_turn_error": statistics.mean(delays),
            "maximum_turn_error": max(delays),
            "delay_distribution": dict(sorted(Counter(delays).items())),
            "outliers": [row for row in rows if row["delay_after_affordable"]],
            "gate": {
                "requirements": [
                    "at least 90% exact first-affordability timing",
                    "mean absolute timing error at most one turn",
                ],
                "passed": trigger_gate,
            },
            "interpretation_limit": (
                "The rule is conditional on an oracle eventual spec. It validates the trigger "
                "mechanism but cannot be deployed until target selection generalizes."
            ),
        },
        "target_policy_grid": {
            "policies": len(grid),
            "unique_prediction_signatures": len(signatures),
            "baseline": {
                "policy": baseline_policy,
                **baseline_metrics,
                "rows": detailed(baseline),
            },
            "in_sample_best": {
                "policy": best,
                "parameters": metadata[best],
                "tied_policy_count": tied_best,
                **prediction_metrics(actual, grid[best], games),
                "rows": detailed(grid[best]),
            },
            "leave_one_game_out_selection": leave_one_out,
            "five_fold_selection": five_fold,
            "gate": {
                "requirements": [
                    "nested leave-one-game-out exact count no worse than the pre-existing baseline",
                    "nested leave-one-game-out mean talent L1 no worse than baseline",
                    "nested five-fold exact count no worse than baseline",
                    "nested five-fold mean talent L1 no worse than baseline",
                ],
                "passed": target_gate,
            },
        },
        "decision": {
            "trigger_identified": trigger_gate,
            "target_selection_generalizes": target_gate,
            "build_candidate": trigger_gate and target_gate,
            "next": (
                "Retain the first-affordability trigger as a recovered component, but do not "
                "tune or deploy a new opening planner. Move to exact target/assignment recovery; "
                "the target-spec residual may become identifiable from that complete policy."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--baseline-plans", type=Path, required=True)
    parser.add_argument("--baseline-policy", default="tuned_carry")
    parser.add_argument("--policy-grid", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    grid, metadata = read_grid(args.policy_grid)
    payload = study(
        json.loads(args.analysis.read_text()),
        args.agent_id,
        read_plans(args.baseline_plans, policy=args.baseline_policy),
        args.baseline_policy,
        grid,
        metadata,
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "conditional_trigger": {
            key: payload["conditional_trigger"][key]
            for key in ("exact_turn", "exact_rate", "mean_absolute_turn_error")
        },
        "baseline": payload["target_policy_grid"]["baseline"],
        "in_sample_best": payload["target_policy_grid"]["in_sample_best"],
        "leave_one_game_out": payload["target_policy_grid"][
            "leave_one_game_out_selection"
        ],
        "five_fold": payload["target_policy_grid"]["five_fold_selection"],
        "decision": payload["decision"],
    }
    for key in ("baseline", "in_sample_best", "leave_one_game_out", "five_fold"):
        compact[key] = {
            field: compact[key][field]
            for field in (
                "policy",
                "exact",
                "exact_rate",
                "mean_talent_l1",
                "maximum_talent_l1",
            )
            if field in compact[key]
        }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
