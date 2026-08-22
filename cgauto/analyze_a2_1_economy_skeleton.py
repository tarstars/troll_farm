#!/usr/bin/env python3
"""Analyze A2-1 development or locked confirmation panels."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.waste_sweep import DETECTORS, build_decoded_game  # noqa: E402

DEVELOPMENT_START = 9_880_000
DEVELOPMENT_MAPS = 32
CONFIRMATION_START = 9_881_000
CONFIRMATION_MAPS = 128
OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)
ALLOWED_OWN_REASONS = frozenset({"move_blocked", "opponent_plant_blocking"})

INT_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "action_hash",
    "state_hash",
    "own_workers_final",
    "own_commands",
    "own_generations_created",
    "own_harvest_plum",
    "own_harvest_lemon",
    "own_harvest_apple",
    "own_harvest_banana",
    "own_bank_plum",
    "own_bank_lemon",
    "own_bank_apple",
    "own_bank_banana",
    "own_bill_fruit_harvested",
    "own_bill_fruit_banked",
    "fruit_funded_worker3",
    "worker3_bill_needs_owned_fruit",
    "mined_iron_roster2",
    "mined_iron_roster3plus",
    "iron_directed_moves",
    "commands_checked",
    "legality_issues",
    "own_legality_issues",
    "opponent_legality_issues",
    "critical_issues",
    "own_critical_issues",
    "opponent_critical_issues",
    "unclassified_issues",
    "movement_rng_draws",
    "movement_tied_draws",
)
COUNT_FIELDS = (
    "legality_reason_counts",
    "own_legality_reason_counts",
    "opponent_legality_reason_counts",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def parse_counts(text: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not text:
        return counts
    for entry in text.split(","):
        key, value = entry.rsplit("=", 1)
        if not key or not value.isdigit():
            raise ValueError(f"invalid count entry: {entry!r}")
        counts[key] += int(value)
    return counts


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        row["first_worker3_turn"] = (
            int(row["first_worker3_turn"]) if row["first_worker3_turn"] else None
        )
        row["worker3_bill"] = (
            tuple(int(value) for value in row["worker3_bill"].split(","))
            if row["worker3_bill"]
            else None
        )
        for field in COUNT_FIELDS:
            row[field] = parse_counts(row[field])
    return rows


def expected_keys(start_seed: int, maps: int) -> set[tuple[int, int, int]]:
    return {
        (seed, seat, opponent)
        for seed in range(start_seed, start_seed + maps)
        for seat in range(2)
        for opponent in range(len(OPPONENTS))
    }


def task_key(row: dict) -> tuple[int, int, int]:
    return row["map_seed"], row["seat"], row["opponent_index"]


def coverage_summary(rows: list[dict], start_seed: int, maps: int) -> dict:
    expected = expected_keys(start_seed, maps)
    observed = [task_key(row) for row in rows]
    counts = Counter(observed)
    observed_set = set(observed)
    labels_ok = all(
        0 <= row["opponent_index"] < len(OPPONENTS)
        and row["opponent"] == OPPONENTS[row["opponent_index"]]
        for row in rows
    )
    checks = {
        "row_count_exact": len(rows) == len(expected),
        "task_matrix_exact": observed_set == expected,
        "no_duplicates": all(count == 1 for count in counts.values()),
        "labels_exact": labels_ok,
        "all_terminal": all(row["done"] == 1 for row in rows),
    }
    return {
        "expected_rows": len(expected),
        "observed_rows": len(rows),
        "missing_examples": [list(key) for key in sorted(expected - observed_set)[:20]],
        "unexpected_examples": [
            list(key) for key in sorted(observed_set - expected)[:20]
        ],
        "duplicate_examples": [
            list(key) for key, count in sorted(counts.items()) if count != 1
        ][:20],
        "checks": checks,
        "pass": all(checks.values()),
    }


def command_quality_summary(rows: list[dict]) -> dict:
    own_reasons: Counter[str] = Counter()
    all_reasons: Counter[str] = Counter()
    row_invariant_failures = []
    for row in rows:
        own_reasons.update(row["own_legality_reason_counts"])
        all_reasons.update(row["legality_reason_counts"])
        if (
            row["legality_issues"]
            != row["own_legality_issues"] + row["opponent_legality_issues"]
            or sum(row["legality_reason_counts"].values())
            != row["legality_issues"]
            or sum(row["own_legality_reason_counts"].values())
            != row["own_legality_issues"]
            or row["legality_reason_counts"]
            != row["own_legality_reason_counts"]
            + row["opponent_legality_reason_counts"]
        ):
            row_invariant_failures.append(list(task_key(row)))

    own_issues = sum(row["own_legality_issues"] for row in rows)
    own_commands = sum(row["own_commands"] for row in rows)
    issue_tasks = sum(row["own_legality_issues"] > 0 for row in rows)
    disallowed = {
        reason: count
        for reason, count in sorted(own_reasons.items())
        if reason not in ALLOWED_OWN_REASONS and count
    }
    issue_rate = own_issues / own_commands if own_commands else 0.0
    task_rate = issue_tasks / len(rows) if rows else 0.0
    checks = {
        "row_accounting_exact": not row_invariant_failures,
        "global_critical_zero": sum(row["critical_issues"] for row in rows) == 0,
        "global_unclassified_zero": sum(row["unclassified_issues"] for row in rows)
        == 0,
        "own_critical_zero": sum(row["own_critical_issues"] for row in rows) == 0,
        "own_reasons_allowed": not disallowed,
        "own_issue_rate_at_most_0_005": issue_rate <= 0.005,
        "own_issue_task_rate_at_most_0_10": task_rate <= 0.10,
    }
    return {
        "own_commands": own_commands,
        "own_issues": own_issues,
        "own_issue_rate": issue_rate,
        "own_issue_tasks": issue_tasks,
        "own_issue_task_rate": task_rate,
        "own_reason_counts": dict(sorted(own_reasons.items())),
        "all_reason_counts": dict(sorted(all_reasons.items())),
        "disallowed_own_reasons": disallowed,
        "row_invariant_failure_examples": row_invariant_failures[:20],
        "checks": checks,
        "pass": all(checks.values()),
    }


def rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def mechanism_summary(rows: list[dict]) -> dict:
    fruit_funded = sum(row["fruit_funded_worker3"] == 1 for row in rows)
    first_turns = [
        row["first_worker3_turn"]
        for row in rows
        if row["first_worker3_turn"] is not None
    ]
    harvested = sum(row["own_bill_fruit_harvested"] for row in rows)
    banked = sum(row["own_bill_fruit_banked"] for row in rows)
    mine2 = sum(row["mined_iron_roster2"] for row in rows)
    mine3 = sum(row["mined_iron_roster3plus"] for row in rows)
    iron_moves = sum(row["iron_directed_moves"] for row in rows)
    checks = {
        "fruit_funded_worker3_rate_at_least_0_40": rate(fruit_funded, len(rows))
        >= 0.40,
        "own_crop_harvest_positive": harvested > 0,
        "own_crop_bank_positive": banked > 0,
        "mine_roster2_positive": mine2 > 0,
        "mine_roster3plus_positive": mine3 > 0,
        "iron_directed_moves_zero": iron_moves == 0,
    }
    return {
        "fruit_funded_worker3_tasks": fruit_funded,
        "fruit_funded_worker3_rate": rate(fruit_funded, len(rows)),
        "worker3_turn": {
            "count": len(first_turns),
            "median": statistics.median(first_turns) if first_turns else None,
            "minimum": min(first_turns) if first_turns else None,
            "maximum": max(first_turns) if first_turns else None,
        },
        "conservative_bill_needs_owned_fruit_tasks": sum(
            row["worker3_bill_needs_owned_fruit"] == 1 for row in rows
        ),
        "own_bill_fruit_harvested": harvested,
        "own_bill_fruit_banked": banked,
        "own_generations_created": sum(
            row["own_generations_created"] for row in rows
        ),
        "mined_iron_roster2": mine2,
        "mined_iron_roster3plus": mine3,
        "iron_directed_moves": iron_moves,
        "checks": checks,
        "pass": all(checks.values()),
    }


def group_summary(rows: list[dict], field: str) -> dict:
    groups: dict[object, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    result = {}
    for key, selected in sorted(groups.items(), key=lambda item: str(item[0])):
        margins = [row["margin"] for row in selected]
        result[str(key)] = {
            "tasks": len(selected),
            "fruit_funded_worker3_rate": rate(
                sum(row["fruit_funded_worker3"] == 1 for row in selected),
                len(selected),
            ),
            "own_bill_fruit_banked": sum(
                row["own_bill_fruit_banked"] for row in selected
            ),
            "mean_own_score": statistics.mean(
                row["own_score"] for row in selected
            ),
            "mean_opponent_score": statistics.mean(
                row["opponent_score"] for row in selected
            ),
            "mean_margin": statistics.mean(margins),
            "catastrophes": sum(margin < -50 for margin in margins),
            "negative_margin_mass": sum(max(-margin, 0) for margin in margins),
            "own_issues": sum(row["own_legality_issues"] for row in selected),
        }
    return result


def _expand_unit(values: list) -> dict:
    return {
        "id": values[0],
        "player": values[1],
        "x": values[2],
        "y": values[3],
        "ms": values[4],
        "cc": values[5],
        "hp": values[6],
        "chop": values[7],
        "carry": values[8:14],
    }


def _expand_plant(values: list) -> dict:
    return {
        "x": values[0],
        "y": values[1],
        "type": values[2],
        "size": values[3],
        "health": values[4],
        "fruits": values[5],
        "cooldown": values[6],
    }


def _expand_state(raw: dict) -> dict:
    return {
        "units": [_expand_unit(unit) for unit in raw["u"]],
        "plants": [_expand_plant(plant) for plant in raw["p"]],
        "inventories": raw["b"],
    }


def decode_record(record: dict, start_seed: int):
    states = [_expand_state(state) for state in record["states"]]
    trajectory = [
        {
            "commands0": ";".join(record["c0"][index]),
            "commands1": ";".join(record["c1"][index]),
        }
        for index in range(len(record["c0"]))
    ]
    me = record["seat"]
    opponent = 1 - me
    scores = record["scores"]
    margin = scores[me] - scores[opponent]
    ranks = [0, 0]
    if margin > 0:
        ranks[me], ranks[opponent] = 0, 1
    elif margin < 0:
        ranks[me], ranks[opponent] = 1, 0
    game_id = (
        (record["seed"] - start_seed) * 16
        + record["seat"] * 8
        + record["opp"]
        + 20_000_000
    )
    return build_decoded_game(
        game_id=game_id,
        me=me,
        map_rows=record["map_rows"],
        states=states,
        trajectory=trajectory,
        scores=scores,
        ranks=ranks,
        opponent_name=record["opp_name"],
    )


def trajectory_summary(
    path: Path,
    rows: list[dict],
    start_seed: int,
    maps: int,
) -> dict:
    expected = expected_keys(start_seed, maps)
    rows_by_key = {task_key(row): row for row in rows}
    seen: set[tuple[int, int, int]] = set()
    duplicates = []
    errors = []
    detector_episodes: Counter[str] = Counter()
    detector_turns: Counter[str] = Counter()
    records = 0

    with path.open() as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            records += 1
            try:
                record = json.loads(line)
                key = (record["seed"], record["seat"], record["opp"])
                if key in seen:
                    duplicates.append(list(key))
                seen.add(key)
                row = rows_by_key[key]
                if record["arm"] != "a2_1":
                    raise ValueError("arm mismatch")
                if record["opp_name"] != row["opponent"]:
                    raise ValueError("opponent label mismatch")
                if record["turns"] != row["turn"] - 1:
                    raise ValueError("turn count mismatch")
                if len(record["states"]) != record["turns"] + 1:
                    raise ValueError("state count mismatch")
                if len(record["c0"]) != record["turns"]:
                    raise ValueError("player-zero command count mismatch")
                if len(record["c1"]) != record["turns"]:
                    raise ValueError("player-one command count mismatch")
                expected_scores = (
                    [row["own_score"], row["opponent_score"]]
                    if row["seat"] == 0
                    else [row["opponent_score"], row["own_score"]]
                )
                if record["scores"] != expected_scores:
                    raise ValueError("score mismatch")
                decoded = decode_record(record, start_seed)
                for detector_name, detector in DETECTORS.items():
                    episodes = detector(decoded)
                    detector_episodes[detector_name] += len(episodes)
                    detector_turns[detector_name] += sum(
                        episode["duration"] for episode in episodes
                    )
            except Exception as error:
                if len(errors) < 20:
                    errors.append(
                        {
                            "line": line_number,
                            "error": f"{type(error).__name__}: {error}",
                        }
                    )

    detector_names_exact = set(detector_episodes) == set(DETECTORS)
    checks = {
        "record_count_exact": records == len(expected),
        "task_coverage_exact": seen == expected,
        "no_duplicates": not duplicates,
        "all_records_decoded": not errors,
        "six_detectors_executed": detector_names_exact and len(DETECTORS) == 6,
        "repeated_failed_command_zero": detector_episodes[
            "repeated_failed_command"
        ]
        == 0,
    }
    return {
        "path": display_path(path),
        "sha256": sha256_file(path),
        "records": records,
        "unique_tasks": len(seen),
        "missing_examples": [list(key) for key in sorted(expected - seen)[:20]],
        "unexpected_examples": [list(key) for key in sorted(seen - expected)[:20]],
        "duplicate_examples": duplicates[:20],
        "decode_or_detector_errors": errors,
        "detectors": {
            name: {
                "episodes": detector_episodes[name],
                "flagged_turns": detector_turns[name],
            }
            for name in sorted(DETECTORS)
        },
        "checks": checks,
        "pass": all(checks.values()),
    }


def analyze(args) -> dict:
    if args.stage == "development":
        start_seed, maps = DEVELOPMENT_START, DEVELOPMENT_MAPS
    else:
        start_seed, maps = CONFIRMATION_START, CONFIRMATION_MAPS
    rows = read_rows(args.jobs20)
    coverage = coverage_summary(rows, start_seed, maps)
    quality = command_quality_summary(rows)
    mechanism = mechanism_summary(rows)
    parity = {
        "jobs1": {
            "path": display_path(args.jobs1),
            "sha256": sha256_file(args.jobs1),
        },
        "jobs20": {
            "path": display_path(args.jobs20),
            "sha256": sha256_file(args.jobs20),
        },
    }
    parity["byte_identical"] = args.jobs1.read_bytes() == args.jobs20.read_bytes()
    trajectories = trajectory_summary(args.trajectories, rows, start_seed, maps)
    integrity_pass = coverage["pass"] and parity["byte_identical"] and trajectories["pass"]
    all_pass = integrity_pass and quality["pass"] and mechanism["pass"]
    if args.stage == "development":
        verdict = "READY_FOR_IMPLEMENTATION_LOCK" if all_pass else "FAILED_DEVELOPMENT"
    elif all_pass:
        verdict = "QUALIFIED"
    elif (
        integrity_pass
        and quality["pass"]
        and not mechanism["checks"]["fruit_funded_worker3_rate_at_least_0_40"]
    ):
        verdict = "FAILED_K1"
    else:
        verdict = "BLOCKED"
    margins = [row["margin"] for row in rows]
    return {
        "schema": "troll-farm-a2-1-economy-skeleton-result-v1",
        "stage": args.stage,
        "panel": {
            "start_seed": start_seed,
            "maps": maps,
            "rows": len(rows),
            "seats": [0, 1],
            "families": list(OPPONENTS),
        },
        "coverage": coverage,
        "thread_parity": parity,
        "mechanism": mechanism,
        "command_quality": quality,
        "trajectories_and_detectors": trajectories,
        "descriptive_value": {
            "mean_own_score": statistics.mean(
                row["own_score"] for row in rows
            )
            if rows
            else None,
            "mean_opponent_score": statistics.mean(
                row["opponent_score"] for row in rows
            )
            if rows
            else None,
            "mean_margin": statistics.mean(margins) if margins else None,
            "catastrophes": sum(margin < -50 for margin in margins),
            "negative_margin_mass": sum(max(-margin, 0) for margin in margins),
            "by_seat": group_summary(rows, "seat"),
            "by_family": group_summary(rows, "opponent"),
        },
        "verdict": verdict,
    }


def self_test() -> None:
    assert parse_counts("") == Counter()
    assert parse_counts("move_blocked=2,no_capacity=1") == Counter(
        {"move_blocked": 2, "no_capacity": 1}
    )
    assert len(expected_keys(DEVELOPMENT_START, DEVELOPMENT_MAPS)) == 512
    assert len(expected_keys(CONFIRMATION_START, CONFIRMATION_MAPS)) == 2_048
    assert len(DETECTORS) == 6
    row = {
        "fruit_funded_worker3": 1,
        "first_worker3_turn": 42,
        "own_bill_fruit_harvested": 1,
        "own_bill_fruit_banked": 1,
        "mined_iron_roster2": 1,
        "mined_iron_roster3plus": 1,
        "iron_directed_moves": 0,
        "worker3_bill_needs_owned_fruit": 1,
        "own_generations_created": 1,
    }
    assert mechanism_summary([row])["pass"]
    failed = dict(row)
    failed["fruit_funded_worker3"] = 0
    assert not mechanism_summary([failed])["pass"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("development", "confirmation"),
        default="development",
    )
    parser.add_argument("--jobs1", type=Path)
    parser.add_argument("--jobs20", type=Path)
    parser.add_argument("--trajectories", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: ok")
        return 0
    for name in ("jobs1", "jobs20", "trajectories", "output"):
        if getattr(args, name) is None:
            parser.error(f"--{name.replace('_', '-')} is required without --self-test")
    result = analyze(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "stage": result["stage"],
                "rows": result["panel"]["rows"],
                "fruit_funded_worker3_rate": result["mechanism"][
                    "fruit_funded_worker3_rate"
                ],
                "own_issue_rate": result["command_quality"]["own_issue_rate"],
                "verdict": result["verdict"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["verdict"] in {"READY_FOR_IMPLEMENTATION_LOCK", "QUALIFIED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
