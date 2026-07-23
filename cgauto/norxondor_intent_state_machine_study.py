#!/usr/bin/env python3
"""Test Norxondor's movement intent as an episode-level state machine.

The preceding navigation study showed that literal MOVE targets are one-turn endpoints and that
intent should persist across a run of MOVE commands.  This follow-up predicts only once, at the
start of each movement episode, using current-state features plus the worker's previous completed
action.  Fivefold splits exclude whole games.  The feature refinement was nominated after the
row-level navigation diagnostic, so this is iterative discovery rather than untouched
confirmation.
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

from cgauto.norxondor_navigation_intent_study import (  # noqa: E402
    action_family,
    extract_game,
)
from cgauto.top_policy_objective_study import classification_summary  # noqa: E402


BACKOFFS = (
    (
        "phase",
        "ordinal",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "unit_count",
        "score_bucket",
        "nearest_ripe",
        "nearest_tree",
        "nearest_iron",
        "cheap_train_affordable",
        "previous_action",
    ),
    (
        "phase",
        "ordinal",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "unit_count",
        "previous_action",
    ),
    (
        "phase",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "previous_action",
    ),
    ("role", "carry_class", "full", "on_cell", "previous_action"),
    ("carry_class", "full", "on_cell", "previous_action"),
    ("carry_class", "full", "previous_action"),
    ("previous_action",),
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def episode_rows(rows: list[dict]) -> list[dict]:
    timelines: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        timelines[(row["game_id"], row["unit_id"])].append(row)
    episodes = []
    for timeline in timelines.values():
        timeline.sort(key=lambda row: row["turn"])
        previous_action = "START"
        index = 0
        while index < len(timeline):
            row = timeline[index]
            if row["verb"] != "MOVE":
                if row["verb"] != "WAIT":
                    previous_action = action_family(row["verb"])
                index += 1
                continue
            end = index + 1
            while end < len(timeline) and timeline[end]["verb"] == "MOVE":
                end += 1
            labels = {item["intent"] for item in timeline[index:end]}
            if len(labels) != 1:
                raise ValueError("intent changed inside one movement episode")
            features = dict(row["features"])
            features["previous_action"] = previous_action
            episodes.append(
                {
                    "game_id": row["game_id"],
                    "unit_id": row["unit_id"],
                    "ordinal": row["ordinal"],
                    "start_turn": row["turn"],
                    "moves": end - index,
                    "label": next(iter(labels)),
                    "previous_action": previous_action,
                    "features": features,
                    "game_fold": row["game_id"] % 5,
                }
            )
            index = end
    episodes.sort(key=lambda row: (row["game_id"], row["start_turn"], row["unit_id"]))
    return episodes


def key(row: dict, fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(row["features"][field] for field in fields)


def majority(counts: Counter) -> str:
    return min(counts, key=lambda label: (-counts[label], label))


def fit(rows: list[dict]) -> dict:
    tables = [defaultdict(Counter) for _ in BACKOFFS]
    global_counts = Counter()
    for row in rows:
        global_counts[row["label"]] += 1
        for table, fields in zip(tables, BACKOFFS):
            table[key(row, fields)][row["label"]] += 1
    return {
        "tables": tables,
        "global": majority(global_counts),
        "global_counts": global_counts,
    }


def predict(model: dict, row: dict) -> tuple[str, str]:
    for index, (table, fields) in enumerate(zip(model["tables"], BACKOFFS)):
        counts = table.get(key(row, fields))
        if counts:
            return majority(counts), f"backoff_{index}"
    return model["global"], "global"


def cross_validate(rows: list[dict]) -> dict:
    actual = []
    predicted = []
    baselines = []
    coverage = Counter()
    folds = []
    for fold in range(5):
        training = [row for row in rows if row["game_fold"] != fold]
        held = [row for row in rows if row["game_fold"] == fold]
        model = fit(training)
        held_predictions = []
        for row in held:
            label, level = predict(model, row)
            held_predictions.append(label)
            coverage[level] += 1
        held_actual = [row["label"] for row in held]
        report = classification_summary(held_actual, held_predictions)
        baseline = classification_summary(
            held_actual, [model["global"]] * len(held_actual)
        )
        folds.append(
            {
                "fold": fold,
                "training_games": len({row["game_id"] for row in training}),
                "held_games": len({row["game_id"] for row in held}),
                "held_episodes": len(held),
                "accuracy": report["accuracy"],
                "macro_f1": report["macro_f1"],
                "majority_accuracy": baseline["accuracy"],
            }
        )
        actual.extend(held_actual)
        predicted.extend(held_predictions)
        baselines.extend([model["global"]] * len(held))
    result = classification_summary(actual, predicted)
    baseline = classification_summary(actual, baselines)
    result.update(
        {
            "folds": folds,
            "majority_baseline": baseline,
            "accuracy_gain": result["accuracy"] - baseline["accuracy"],
            "worst_fold_accuracy": min(row["accuracy"] for row in folds),
            "worst_fold_macro_f1": min(row["macro_f1"] for row in folds),
            "coverage": dict(sorted(coverage.items())),
        }
    )
    return result


def study(analyzed: list[dict], agent_id: int, row_level_accuracy: float) -> dict:
    analyzed.sort(key=lambda row: row["game_id"])
    rows = [row for game in analyzed for row in game["rows"]]
    episodes = episode_rows(rows)
    held = cross_validate(episodes)
    common_labels = {
        label
        for label, count in Counter(row["label"] for row in episodes).items()
        if count >= 500
    }
    minimum_common_f1 = min(held["per_label"][label]["f1"] for label in common_labels)
    row_gain = held["accuracy"] - row_level_accuracy
    passed = (
        held["accuracy"] >= 0.72
        and held["macro_f1"] >= 0.50
        and held["worst_fold_accuracy"] >= 0.70
        and held["worst_fold_macro_f1"] >= 0.45
        and held["accuracy_gain"] >= 0.35
        and minimum_common_f1 >= 0.50
        and row_gain >= 0.02
    )
    transitions = Counter(
        (row["previous_action"], row["label"]) for row in episodes
    )
    return {
        "schema": 1,
        "scope": (
            "iterative discovery on consumed Norxondor replays; one row per movement episode; "
            "fivefold whole-game exclusion; predictor inputs are current state and previous "
            "completed action only; no future inputs, goal coordinates, counterfactual rollout, "
            "causal value, sealed holdout, or arena evidence"
        ),
        "agent_id": agent_id,
        "games": len(analyzed),
        "unit_rows": len(rows),
        "episodes": len(episodes),
        "episode_labels": dict(sorted(Counter(row["label"] for row in episodes).items())),
        "mean_moves_per_episode": statistics.mean(row["moves"] for row in episodes),
        "features": BACKOFFS,
        "held_game": held,
        "row_level_intent_accuracy": row_level_accuracy,
        "episode_accuracy_gain_over_row_level": row_gain,
        "minimum_common_label_f1": minimum_common_f1,
        "transitions": {
            previous: dict(
                sorted(
                    (label, count)
                    for (source, label), count in transitions.items()
                    if source == previous
                )
            )
            for previous in sorted({source for source, _ in transitions})
        },
        "gate": {
            "requirements": [
                "held episode accuracy at least 0.72 and macro F1 at least 0.50",
                "every fold accuracy at least 0.70 and macro F1 at least 0.45",
                "accuracy beats fold-majority by at least 0.35",
                "every intent with at least 500 episodes has F1 at least 0.50",
                "episode formulation improves over row-level intent by at least 0.02",
            ],
            "passed": passed,
        },
        "decision": {
            "state_machine_supported": passed,
            "authorize_goal_selector_study": passed,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--navigation-study", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text())
    navigation = json.loads(args.navigation_study.read_text())
    if navigation["agent_id"] != args.agent_id:
        raise SystemExit("navigation-study agent does not match --agent-id")
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == args.agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    analyzed = []
    for index, occurrence in enumerate(occurrences, 1):
        analyzed.append(extract_game(occurrence))
        if index % 10 == 0 or index == len(occurrences):
            print(f"decoded {index}/{len(occurrences)} games", flush=True)
    payload = study(
        analyzed,
        args.agent_id,
        navigation["held_game_intent"]["accuracy"],
    )
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "episodes": payload["episodes"],
        "labels": payload["episode_labels"],
        "held": {
            key: payload["held_game"][key]
            for key in (
                "accuracy",
                "macro_f1",
                "accuracy_gain",
                "worst_fold_accuracy",
                "worst_fold_macro_f1",
            )
        },
        "row_level_accuracy": payload["row_level_intent_accuracy"],
        "episode_gain": payload["episode_accuracy_gain_over_row_level"],
        "minimum_common_label_f1": payload["minimum_common_label_f1"],
        "gate": payload["gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
