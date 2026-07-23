#!/usr/bin/env python3
"""Compare local continuation openings with preserved arena opponent commands."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.arena_rollout_forensics import (  # noqa: E402
    DEFAULT_MANIFEST,
    candidate_seat,
    initial_replay_state,
    manifest_records,
    observed_first_stdout,
)
from cgauto.battles import call  # noqa: E402


UNIT_VERBS = {"MOVE", "PICK", "PLANT", "HARVEST", "CHOP", "MINE", "DROP"}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def commands(text: str) -> tuple[tuple[str, ...], ...]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ()
    parsed = []
    # A replay frame can contain eagerly printed lines for later turns. Only the
    # first command line belongs to the opening decision represented by the frame.
    used_units = set()
    for raw in lines[0].split(";"):
        fields = tuple(raw.strip().split())
        if not fields or fields[0] in {"MSG", "MESSAGE"}:
            continue
        if (
            fields[0] in UNIT_VERBS
            and len(fields) >= 2
            and fields[1].lstrip("-").isdigit()
        ):
            unit_id = int(fields[1])
            if unit_id in used_units:
                continue
            used_units.add(unit_id)
        parsed.append(fields)
    return tuple(sorted(parsed))


def train_spec(parsed: tuple[tuple[str, ...], ...]) -> tuple[int, ...] | None:
    matches = [row for row in parsed if row[0] == "TRAIN"]
    if not matches:
        return None
    if len(matches) != 1 or len(matches[0]) != 5:
        raise ValueError(f"unexpected TRAIN commands {matches}")
    return tuple(int(value) for value in matches[0][1:])


def unit_command(
    parsed: tuple[tuple[str, ...], ...], unit_id: int
) -> tuple[str, ...] | None:
    matches = [
        row
        for row in parsed
        if row[0] in UNIT_VERBS
        and len(row) >= 2
        and row[1].lstrip("-").isdigit()
        and int(row[1]) == unit_id
    ]
    if len(matches) > 1:
        raise ValueError(f"multiple commands for unit {unit_id}: {matches}")
    return matches[0] if matches else None


def compare(observed: dict, predicted_text: str) -> dict:
    actual = commands(observed["command"])
    predicted = commands(predicted_text)
    actual_train = train_spec(actual)
    predicted_train = train_spec(predicted)
    actual_unit = unit_command(actual, observed["starter_id"])
    predicted_unit = unit_command(predicted, observed["starter_id"])
    both_train = actual_train is not None and predicted_train is not None
    train_l1 = (
        sum(abs(left - right) for left, right in zip(actual_train, predicted_train))
        if both_train
        else None
    )
    actual_verb = actual_unit[0] if actual_unit else None
    predicted_verb = predicted_unit[0] if predicted_unit else None
    return {
        "commands_exact": actual == predicted,
        "train_presence_exact": (actual_train is None) == (predicted_train is None),
        "train_exact": actual_train == predicted_train,
        "both_train": both_train,
        "train_l1": train_l1,
        "starter_present_exact": (actual_unit is None) == (predicted_unit is None),
        "starter_verb_exact": actual_verb == predicted_verb,
        "starter_command_exact": actual_unit == predicted_unit,
        "opening_signature_exact": (actual_train, actual_verb)
        == (predicted_train, predicted_verb),
        "actual_train": actual_train,
        "predicted_train": predicted_train,
        "actual_starter_command": actual_unit,
        "predicted_starter_command": predicted_unit,
    }


def read_predictions(path: Path) -> dict[tuple[int, int, str], str]:
    rows = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = (int(row["seed"]), int(row["seat"]), row["model"])
            if key in rows:
                raise ValueError(f"duplicate prediction {key}")
            rows[key] = row["commands"]
    if not rows:
        raise ValueError(f"empty prediction grid {path}")
    return rows


def metric_summary(rows: list[dict]) -> dict:
    count = len(rows)
    boolean_fields = (
        "commands_exact",
        "train_presence_exact",
        "train_exact",
        "starter_present_exact",
        "starter_verb_exact",
        "starter_command_exact",
        "opening_signature_exact",
    )
    both_train = [row["train_l1"] for row in rows if row["both_train"]]
    return {
        "samples": count,
        **{
            field: {
                "count": sum(row[field] for row in rows),
                "rate": sum(row[field] for row in rows) / count if count else None,
            }
            for field in boolean_fields
        },
        "both_train_samples": len(both_train),
        "train_l1_when_both": {
            "mean": statistics.mean(both_train) if both_train else None,
            "median": statistics.median(both_train) if both_train else None,
            "maximum": max(both_train) if both_train else None,
        },
    }


def calibrate(
    observed: dict[int, dict],
    prediction_runs: list[dict[tuple[int, int, str], str]],
) -> dict:
    if not prediction_runs:
        raise ValueError("at least one prediction grid is required")
    game_ids = set(observed)
    models = tuple(sorted({key[2] for key in prediction_runs[0] if key[1] == 1}))
    expected = {(game_id, 1, model) for game_id in game_ids for model in models}
    for index, predictions in enumerate(prediction_runs):
        scoped = {key for key in predictions if key[1] == 1}
        if scoped != expected:
            missing = sorted(expected - scoped)[:5]
            extra = sorted(scoped - expected)[:5]
            raise ValueError(
                f"prediction coverage mismatch in run {index}; missing={missing}, extra={extra}"
            )

    rows = []
    by_model = defaultdict(list)
    by_opponent_model = defaultdict(list)
    for repeat, predictions in enumerate(prediction_runs):
        for game_id in sorted(game_ids):
            for model in models:
                result = compare(observed[game_id], predictions[(game_id, 1, model)])
                row = {
                    "game_id": game_id,
                    "prediction_repeat": repeat,
                    "model": model,
                    "opponent": observed[game_id]["opponent"],
                    "opponent_agent": observed[game_id]["opponent_agent"],
                    **result,
                }
                rows.append(row)
                by_model[model].append(row)
                by_opponent_model[(row["opponent"], model)].append(row)

    repeatability = {}
    for model in models:
        exact_games = 0
        for game_id in game_ids:
            predictions = [
                commands(run[(game_id, 1, model)]) for run in prediction_runs
            ]
            exact_games += all(value == predictions[0] for value in predictions[1:])
        repeatability[model] = {
            "exact_games": exact_games,
            "games": len(game_ids),
            "rate": exact_games / len(game_ids),
        }

    actual_commands = [commands(row["command"]) for row in observed.values()]
    actual_trains = [train_spec(row) for row in actual_commands]
    actual_verbs = [
        (unit_command(parsed, observed[game_id]["starter_id"]) or (None,))[0]
        for game_id, parsed in zip(observed, actual_commands)
    ]
    summary_by_model = {
        model: metric_summary(model_rows)
        for model, model_rows in sorted(by_model.items())
    }
    ranking = sorted(
        models,
        key=lambda model: (
            summary_by_model[model]["opening_signature_exact"]["rate"],
            summary_by_model[model]["starter_command_exact"]["rate"],
            summary_by_model[model]["commands_exact"]["rate"],
            model,
        ),
        reverse=True,
    )
    return {
        "schema": 1,
        "scope": (
            "turn-one action agreement on diagnosis-only arena opponent trajectories; local "
            "models see the candidate-relative initial state as seat 1; agreement is not a "
            "terminal-value calibration or causal outcome estimate"
        ),
        "games": len(game_ids),
        "prediction_repeats": len(prediction_runs),
        "models": models,
        "field_openings": {
            "train_games": sum(value is not None for value in actual_trains),
            "train_specs": {
                " ".join(map(str, spec)): count
                for spec, count in sorted(Counter(actual_trains).items(), key=lambda item: str(item[0]))
                if spec is not None
            },
            "starter_verbs": dict(sorted(Counter(actual_verbs).items(), key=lambda item: str(item[0]))),
        },
        "model_summary": summary_by_model,
        "model_opening_repeatability": repeatability,
        "agreement_ranking": ranking,
        "by_opponent_model": [
            {
                "opponent": opponent,
                "model": model,
                **metric_summary(model_rows),
            }
            for (opponent, model), model_rows in sorted(by_opponent_model.items())
        ],
        "rows": rows,
        "interpretation_limit": (
            "Turn-one similarity can reject unsupported continuations and describe field opening "
            "coverage. It cannot by itself assign rollout-value weights: models with the same "
            "opening may diverge later, and the live controller cannot condition a simultaneous "
            "turn-one decision on the opponent's unseen first command."
        ),
    }


def fetch_observed(manifest: dict, jobs: int) -> dict[int, dict]:
    records = manifest_records(manifest)
    candidate_agent = int(manifest["candidate_agent_id"])

    def fetch(record: tuple[int, str]) -> dict:
        game_id, _window = record
        return call("gameResult/findByGameId", [game_id, None])

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        results = list(executor.map(fetch, records))

    observed = {}
    for result in results:
        game_id = int(result["gameId"])
        candidate = candidate_seat(result, candidate_agent)
        opponent_seat = 1 - candidate
        _map, state = initial_replay_state(result)
        starters = [
            unit["id"] for unit in state["units"] if unit["player"] == opponent_seat
        ]
        if len(starters) != 1:
            raise ValueError(f"game {game_id} has {len(starters)} opponent starters")
        opponent = next(agent for agent in result["agents"] if agent["index"] == opponent_seat)
        observed[game_id] = {
            "command": observed_first_stdout(result, opponent_seat),
            "starter_id": starters[0],
            "opponent": (opponent.get("codingamer") or {}).get("pseudo"),
            "opponent_agent": opponent.get("agentId"),
        }
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--predictions", type=Path, action="append", required=True)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")
    manifest = json.loads(args.manifest.read_text())
    observed = fetch_observed(manifest, args.jobs)
    payload = calibrate(observed, [read_predictions(path) for path in args.predictions])
    payload["manifest"] = str(args.manifest)
    payload["prediction_sources"] = [str(path) for path in args.predictions]
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "games": payload["games"],
        "field_openings": payload["field_openings"],
        "agreement_ranking": payload["agreement_ranking"],
        "models": {
            model: {
                "signature": row["opening_signature_exact"],
                "starter_command": row["starter_command_exact"],
                "full": row["commands_exact"],
                "repeatability": payload["model_opening_repeatability"][model],
            }
            for model, row in payload["model_summary"].items()
        },
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
