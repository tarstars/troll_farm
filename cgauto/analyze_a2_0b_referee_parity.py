#!/usr/bin/env python3
"""Analyze the frozen A2-0b r1 referee-parity calibration.

Development validates the fixed 16-map smoke and legality-accounting invariants.
Confirmation additionally requires byte-identical one/20-thread panels, exact D173b
resident reproduction, exact trajectory coverage in both modes, and successful execution
of all six standing waste detectors.
"""

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

ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "a2-0b-referee-parity"
DEFAULT_JOBS1 = ARTIFACT_BASE / "a2-0b-jobs1-9854000-9854127.tsv"
DEFAULT_JOBS20 = ARTIFACT_BASE / "a2-0b-jobs20-9854000-9854127.tsv"
DEFAULT_LEGACY_TRAJECTORIES = (
    ARTIFACT_BASE / "a2-0b-trajectories-legacy-9854000-9854127.ndjson"
)
DEFAULT_REFEREE_TRAJECTORIES = (
    ARTIFACT_BASE / "a2-0b-trajectories-referee-9854000-9854127.ndjson"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "analysis"
    / "live-agent-6553250"
    / "a2-0b-r1-referee-parity-result.json"
)

START_SEED = 9_854_000
DEVELOPMENT_MAPS = 16
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
MODES = ("legacy", "referee")
SUPPORTED_NONCRITICAL_REASONS = frozenset(
    {
        "unit_not_found",
        "unit_not_owned",
        "unit_already_used",
        "out_of_board",
        "invalid_skill",
        "cant_afford_train",
        "no_plant",
        "no_fruit",
        "no_capacity",
        "no_harvest",
        "invalid_plant",
        "no_grass",
        "existing_plant",
        "no_seeds",
        "no_chop",
        "out_of_stock",
        "no_shack",
        "nothing_to_drop",
        "no_iron",
        "move_blocked",
        "opponent_plant_blocking",
        "pick_stock_lost",
        "train_affordability_lost",
        "train_shack_blocked",
    }
)

BASE_INT_FIELDS = ("map_seed", "seat", "opponent_index")
SIDE_INT_FIELDS = (
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "action_hash",
    "state_hash",
    "own_workers_final",
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


def sorted_counts(counts: Counter[str]) -> dict[str, int]:
    return dict(sorted(counts.items()))


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in BASE_INT_FIELDS:
            row[field] = int(row[field])
        for mode in MODES:
            for field in SIDE_INT_FIELDS:
                row[f"{mode}_{field}"] = int(row[f"{mode}_{field}"])
            for field in (
                "legality_reason_counts",
                "own_legality_reason_counts",
                "opponent_legality_reason_counts",
                "legality_phase_reason_counts",
                "own_legality_phase_reason_counts",
                "opponent_legality_phase_reason_counts",
            ):
                row[f"{mode}_{field}"] = parse_counts(row[f"{mode}_{field}"])
        row["first_state_divergence_turn"] = (
            int(row["first_state_divergence_turn"])
            if row["first_state_divergence_turn"]
            else None
        )
    return rows


def expected_task_keys(maps: int) -> set[tuple[int, int, int]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + maps)
        for seat in range(2)
        for opponent in range(len(OPPONENTS))
    }


def task_key(row: dict) -> tuple[int, int, int]:
    return row["map_seed"], row["seat"], row["opponent_index"]


def first_nonempty(rows: list[dict], field: str) -> str | None:
    return next((row[field] for row in rows if row[field]), None)


def summarize_issue_accounting(rows: list[dict], mode: str) -> dict:
    total_reasons: Counter[str] = Counter()
    total_phases: Counter[str] = Counter()
    role_reasons = {"own": Counter(), "opponent": Counter()}
    role_phases = {"own": Counter(), "opponent": Counter()}
    by_family: dict[str, dict] = {}
    row_invariants = []

    for row in rows:
        issues = row[f"{mode}_legality_issues"]
        own = row[f"{mode}_own_legality_issues"]
        opponent = row[f"{mode}_opponent_legality_issues"]
        critical = row[f"{mode}_critical_issues"]
        own_critical = row[f"{mode}_own_critical_issues"]
        opponent_critical = row[f"{mode}_opponent_critical_issues"]
        reasons = row[f"{mode}_legality_reason_counts"]
        own_reasons = row[f"{mode}_own_legality_reason_counts"]
        opponent_reasons = row[f"{mode}_opponent_legality_reason_counts"]
        phases = row[f"{mode}_legality_phase_reason_counts"]
        own_phases = row[f"{mode}_own_legality_phase_reason_counts"]
        opponent_phases = row[f"{mode}_opponent_legality_phase_reason_counts"]

        checks = (
            issues == own + opponent,
            critical == own_critical + opponent_critical,
            sum(reasons.values()) == issues,
            sum(own_reasons.values()) == own,
            sum(opponent_reasons.values()) == opponent,
            reasons == own_reasons + opponent_reasons,
            sum(phases.values()) == issues,
            sum(own_phases.values()) == own,
            sum(opponent_phases.values()) == opponent,
            phases == own_phases + opponent_phases,
        )
        if not all(checks):
            row_invariants.append(list(task_key(row)))

        total_reasons.update(reasons)
        total_phases.update(phases)
        role_reasons["own"].update(own_reasons)
        role_reasons["opponent"].update(opponent_reasons)
        role_phases["own"].update(own_phases)
        role_phases["opponent"].update(opponent_phases)

        family = row["opponent"]
        if family not in by_family:
            by_family[family] = {
                "issues": 0,
                "own_issues": 0,
                "opponent_issues": 0,
                "critical_issues": 0,
                "reason_counts": Counter(),
                "phase_reason_counts": Counter(),
            }
        family_result = by_family[family]
        family_result["issues"] += issues
        family_result["own_issues"] += own
        family_result["opponent_issues"] += opponent
        family_result["critical_issues"] += critical
        family_result["reason_counts"].update(reasons)
        family_result["phase_reason_counts"].update(phases)

    for family_result in by_family.values():
        family_result["reason_counts"] = sorted_counts(family_result["reason_counts"])
        family_result["phase_reason_counts"] = sorted_counts(
            family_result["phase_reason_counts"]
        )

    issue_total = sum(row[f"{mode}_legality_issues"] for row in rows)
    own_total = sum(row[f"{mode}_own_legality_issues"] for row in rows)
    opponent_total = sum(row[f"{mode}_opponent_legality_issues"] for row in rows)
    critical_total = sum(row[f"{mode}_critical_issues"] for row in rows)
    own_critical_total = sum(row[f"{mode}_own_critical_issues"] for row in rows)
    opponent_critical_total = sum(
        row[f"{mode}_opponent_critical_issues"] for row in rows
    )
    unclassified_total = sum(row[f"{mode}_unclassified_issues"] for row in rows)
    unsupported_reasons = sorted(set(total_reasons) - SUPPORTED_NONCRITICAL_REASONS)
    first_critical = first_nonempty(rows, f"{mode}_first_critical_issue")

    return {
        "issues": issue_total,
        "own_issues": own_total,
        "opponent_issues": opponent_total,
        "critical_issues": critical_total,
        "own_critical_issues": own_critical_total,
        "opponent_critical_issues": opponent_critical_total,
        "unclassified_issues": unclassified_total,
        "reason_counts": sorted_counts(total_reasons),
        "phase_reason_counts": sorted_counts(total_phases),
        "by_role": {
            role: {
                "issues": own_total if role == "own" else opponent_total,
                "reason_counts": sorted_counts(role_reasons[role]),
                "phase_reason_counts": sorted_counts(role_phases[role]),
            }
            for role in ("own", "opponent")
        },
        "by_family": dict(sorted(by_family.items())),
        "first_issue": first_nonempty(rows, f"{mode}_first_legality_issue"),
        "first_own_issue": first_nonempty(
            rows, f"{mode}_first_own_legality_issue"
        ),
        "first_opponent_issue": first_nonempty(
            rows, f"{mode}_first_opponent_legality_issue"
        ),
        "first_critical_issue": first_critical,
        "unsupported_reasons": unsupported_reasons,
        "row_invariant_failures": row_invariants[:20],
        "pass": (
            not row_invariants
            and issue_total == own_total + opponent_total
            and critical_total == own_critical_total + opponent_critical_total
            and critical_total == 0
            and unclassified_total == 0
            and not unsupported_reasons
            and first_critical is None
        ),
    }


def panel_integrity(rows: list[dict], maps: int) -> dict:
    expected = expected_task_keys(maps)
    actual_order = [task_key(row) for row in rows]
    actual = set(actual_order)
    matrix_exact = actual == expected and len(actual_order) == len(expected)
    all_terminal = all(
        row[f"{mode}_done"] == 1 for row in rows for mode in MODES
    )
    family_labels = all(
        row["opponent"] == OPPONENTS[row["opponent_index"]] for row in rows
    )
    margin_fields = all(
        row[f"{mode}_margin"]
        == row[f"{mode}_own_score"] - row[f"{mode}_opponent_score"]
        for row in rows
        for mode in MODES
    )
    issue_accounting = {
        mode: summarize_issue_accounting(rows, mode) for mode in MODES
    }
    checks = {
        "row_count_exact": len(rows) == len(expected),
        "task_matrix_exact": matrix_exact,
        "rows_sorted": actual_order == sorted(actual_order),
        "all_terminal": all_terminal,
        "family_labels_exact": family_labels,
        "margin_fields_exact": margin_fields,
        "legality_accounting": all(
            issue_accounting[mode]["pass"] for mode in MODES
        ),
    }
    return {
        "expected_rows": len(expected),
        "actual_rows": len(rows),
        "checks": checks,
        "issue_accounting": issue_accounting,
        "pass": all(checks.values()),
    }


def aggregate(values: list[int]) -> dict:
    return {
        "count": len(values),
        "mean": statistics.fmean(values) if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "sum": sum(values),
    }


def digest_integers(values: list[int]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.to_bytes(8, "little", signed=False))
    return digest.hexdigest()


def semantics_summary(rows: list[dict]) -> dict:
    deltas: dict[str, dict[str, dict[str, list[int]]]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "own_score_delta": [],
                "opponent_score_delta": [],
                "margin_delta": [],
            }
        )
    )
    for row in rows:
        bucket = deltas[row["opponent"]][str(row["seat"])]
        bucket["own_score_delta"].append(
            row["referee_own_score"] - row["legacy_own_score"]
        )
        bucket["opponent_score_delta"].append(
            row["referee_opponent_score"] - row["legacy_opponent_score"]
        )
        bucket["margin_delta"].append(
            row["referee_margin"] - row["legacy_margin"]
        )
    by_family_and_seat = {
        family: {
            seat: {
                metric: aggregate(values)
                for metric, values in sorted(metrics.items())
            }
            for seat, metrics in sorted(by_seat.items())
        }
        for family, by_seat in sorted(deltas.items())
    }
    legacy_margins = [row["legacy_margin"] for row in rows]
    referee_margins = [row["referee_margin"] for row in rows]
    legacy_catastrophes = sum(margin <= -100 for margin in legacy_margins)
    legacy_negative_mass = sum(max(-margin, 0) for margin in legacy_margins)
    referee_catastrophes = sum(margin <= -100 for margin in referee_margins)
    referee_negative_mass = sum(max(-margin, 0) for margin in referee_margins)
    return {
        "state_divergence_tasks": sum(
            row["first_state_divergence_turn"] is not None for row in rows
        ),
        "first_state_divergence_turns": aggregate(
            [
                row["first_state_divergence_turn"]
                for row in rows
                if row["first_state_divergence_turn"] is not None
            ]
        ),
        "margin_delta": {
            "overall": {
                "own_score_delta": aggregate(
                    [
                        row["referee_own_score"] - row["legacy_own_score"]
                        for row in rows
                    ]
                ),
                "opponent_score_delta": aggregate(
                    [
                        row["referee_opponent_score"]
                        - row["legacy_opponent_score"]
                        for row in rows
                    ]
                ),
                "margin_delta": aggregate(
                    [
                        row["referee_margin"] - row["legacy_margin"]
                        for row in rows
                    ]
                ),
            },
            "by_family_and_seat": by_family_and_seat,
        },
        "tail": {
            "legacy": {
                "catastrophes": legacy_catastrophes,
                "negative_margin_mass": legacy_negative_mass,
            },
            "referee": {
                "catastrophes": referee_catastrophes,
                "negative_margin_mass": referee_negative_mass,
            },
        },
        "movement_rng": {
            mode: {
                "draws": sum(row[f"{mode}_movement_rng_draws"] for row in rows),
                "true_ties": sum(
                    row[f"{mode}_movement_tied_draws"] for row in rows
                ),
            }
            for mode in MODES
        },
        "hash_accounting": {
            mode: {
                "unique_action_hashes": len(
                    {row[f"{mode}_action_hash"] for row in rows}
                ),
                "unique_state_hashes": len(
                    {row[f"{mode}_state_hash"] for row in rows}
                ),
                "action_hash_vector_sha256": digest_integers(
                    [row[f"{mode}_action_hash"] for row in rows]
                ),
                "state_hash_vector_sha256": digest_integers(
                    [row[f"{mode}_state_hash"] for row in rows]
                ),
            }
            for mode in MODES
        },
        "cross_mode_hash_equality": {
            "action_hash_tasks": sum(
                row["legacy_action_hash"] == row["referee_action_hash"]
                for row in rows
            ),
            "state_hash_tasks": sum(
                row["legacy_state_hash"] == row["referee_state_hash"]
                for row in rows
            ),
        },
    }


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


def game_id_for(seed: int, seat: int, opponent: int, mode: str) -> int:
    base = (seed - START_SEED) * 16 + seat * 8 + opponent
    return base if mode == "legacy" else base + 10_000_000


def decode_record(record: dict):
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
    return build_decoded_game(
        game_id=game_id_for(
            record["seed"], record["seat"], record["opp"], record["arm"]
        ),
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
    mode: str,
    rows_by_key: dict[tuple[int, int, int], dict],
    expected: set[tuple[int, int, int]],
) -> dict:
    seen: set[tuple[int, int, int]] = set()
    duplicates = []
    errors = []
    detector_episodes: Counter[str] = Counter()
    detector_turns: Counter[str] = Counter()
    record_count = 0

    with path.open() as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            record_count += 1
            try:
                record = json.loads(line)
                key = (record["seed"], record["seat"], record["opp"])
                if key in seen:
                    duplicates.append(list(key))
                seen.add(key)
                row = rows_by_key[key]
                if record["arm"] != mode:
                    raise ValueError(f"arm {record['arm']!r}, expected {mode!r}")
                if record["opp_name"] != row["opponent"]:
                    raise ValueError("opponent label mismatch")
                if record["turns"] != row[f"{mode}_turn"] - 1:
                    raise ValueError("turn count mismatch")
                if len(record["states"]) != record["turns"] + 1:
                    raise ValueError("state count mismatch")
                if len(record["c0"]) != record["turns"]:
                    raise ValueError("player-zero command count mismatch")
                if len(record["c1"]) != record["turns"]:
                    raise ValueError("player-one command count mismatch")
                expected_scores = (
                    [
                        row[f"{mode}_own_score"],
                        row[f"{mode}_opponent_score"],
                    ]
                    if row["seat"] == 0
                    else [
                        row[f"{mode}_opponent_score"],
                        row[f"{mode}_own_score"],
                    ]
                )
                if record["scores"] != expected_scores:
                    raise ValueError("score mismatch")
                decoded = decode_record(record)
                for detector_name, detector in DETECTORS.items():
                    episodes = detector(decoded)
                    detector_episodes[detector_name] += len(episodes)
                    detector_turns[detector_name] += sum(
                        episode["duration"] for episode in episodes
                    )
            except Exception as error:  # evidence report retains bounded examples
                if len(errors) < 20:
                    errors.append(
                        {"line": line_number, "error": f"{type(error).__name__}: {error}"}
                    )

    missing = sorted(expected - seen)
    unexpected = sorted(seen - expected)
    detector_names_exact = set(detector_episodes) == set(DETECTORS)
    return {
        "path": display_path(path),
        "sha256": sha256_file(path),
        "records": record_count,
        "unique_tasks": len(seen),
        "missing_tasks": [list(key) for key in missing[:20]],
        "unexpected_tasks": [list(key) for key in unexpected[:20]],
        "duplicate_tasks": duplicates[:20],
        "decode_or_detector_errors": errors,
        "detectors": {
            name: {
                "episodes": detector_episodes[name],
                "flagged_turns": detector_turns[name],
            }
            for name in sorted(DETECTORS)
        },
        "checks": {
            "record_count_exact": record_count == len(expected),
            "task_coverage_exact": seen == expected,
            "no_duplicates": not duplicates,
            "all_records_decoded": not errors,
            "six_detectors_executed": detector_names_exact and len(DETECTORS) == 6,
        },
        "pass": (
            record_count == len(expected)
            and seen == expected
            and not duplicates
            and not errors
            and detector_names_exact
            and len(DETECTORS) == 6
        ),
    }


def analyze(args) -> dict:
    expected_maps = (
        DEVELOPMENT_MAPS if args.stage == "development" else CONFIRMATION_MAPS
    )
    rows = read_rows(args.jobs20)
    expected = expected_task_keys(expected_maps)
    rows_by_key = {task_key(row): row for row in rows}
    integrity = panel_integrity(rows, expected_maps)
    semantics = semantics_summary(rows)

    input_hashes = {
        "jobs20": {
            "path": display_path(args.jobs20),
            "sha256": sha256_file(args.jobs20),
        }
    }
    thread_parity = {"required": args.stage == "confirmation", "pass": None}
    trajectories = {"required": args.stage == "confirmation", "pass": None}
    baseline = {
        "required": args.stage == "confirmation",
        "expected": {"catastrophes": 49, "negative_margin_mass": 12_749},
        "observed": semantics["tail"]["legacy"],
        "pass": None,
    }

    if args.stage == "confirmation":
        input_hashes["jobs1"] = {
            "path": display_path(args.jobs1),
            "sha256": sha256_file(args.jobs1),
        }
        thread_parity["pass"] = args.jobs1.read_bytes() == args.jobs20.read_bytes()
        baseline["pass"] = (
            semantics["tail"]["legacy"]["catastrophes"] == 49
            and semantics["tail"]["legacy"]["negative_margin_mass"] == 12_749
        )
        trajectories = {
            "required": True,
            "legacy": trajectory_summary(
                args.legacy_trajectories, "legacy", rows_by_key, expected
            ),
            "referee": trajectory_summary(
                args.referee_trajectories, "referee", rows_by_key, expected
            ),
        }
        trajectories["pass"] = all(
            trajectories[mode]["pass"] for mode in MODES
        )
        qualified = (
            integrity["pass"]
            and thread_parity["pass"]
            and baseline["pass"]
            and trajectories["pass"]
        )
        verdict = "QUALIFIED" if qualified else "BLOCKED"
    else:
        qualified = integrity["pass"]
        verdict = "READY_FOR_IMPLEMENTATION_LOCK" if qualified else "BLOCKED"

    return {
        "schema": "troll-farm-a2-0b-referee-parity-r1-result-v1",
        "stage": args.stage,
        "panel": {
            "start_seed": START_SEED,
            "maps": expected_maps,
            "rows": len(rows),
            "seats": [0, 1],
            "families": list(OPPONENTS),
        },
        "input_hashes": input_hashes,
        "integrity": integrity,
        "thread_parity": thread_parity,
        "legacy_reproduction": baseline,
        "semantics_change": semantics,
        "trajectories_and_detectors": trajectories,
        "verdict": verdict,
    }


def self_test() -> None:
    assert parse_counts("") == Counter()
    assert parse_counts("move_blocked=2,no_capacity=1") == Counter(
        {"move_blocked": 2, "no_capacity": 1}
    )
    assert len(expected_task_keys(DEVELOPMENT_MAPS)) == 256
    assert len(expected_task_keys(CONFIRMATION_MAPS)) == 2_048
    assert len(SUPPORTED_NONCRITICAL_REASONS) == 24
    assert len(DETECTORS) == 6
    assert game_id_for(START_SEED, 0, 0, "legacy") == 0
    assert game_id_for(START_SEED, 0, 0, "referee") == 10_000_000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("development", "confirmation"),
        default="confirmation",
    )
    parser.add_argument("--jobs1", type=Path, default=DEFAULT_JOBS1)
    parser.add_argument("--jobs20", type=Path, default=DEFAULT_JOBS20)
    parser.add_argument(
        "--legacy-trajectories",
        type=Path,
        default=DEFAULT_LEGACY_TRAJECTORIES,
    )
    parser.add_argument(
        "--referee-trajectories",
        type=Path,
        default=DEFAULT_REFEREE_TRAJECTORIES,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("self-test: ok")
        return 0

    result = analyze(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "stage": result["stage"],
                "rows": result["panel"]["rows"],
                "verdict": result["verdict"],
            },
            sort_keys=True,
        )
    )
    return 0 if result["verdict"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
