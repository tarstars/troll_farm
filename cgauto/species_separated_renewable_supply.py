#!/usr/bin/env python3
"""Analyze the frozen canonical PLUM renewable-supply intervention."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path
import statistics
import tempfile

try:
    from cgauto.prefruit_reproductive_interruption import (
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        OUTCOME_IDENTITY_FIELDS,
        compare,
        identity,
        summarize as base_summarize,
        trimmed_mean,
    )
except ModuleNotFoundError:  # Direct script execution.
    from prefruit_reproductive_interruption import (  # type: ignore[no-redef]
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        OUTCOME_IDENTITY_FIELDS,
        compare,
        identity,
        summarize as base_summarize,
        trimmed_mean,
    )


PROFILES = {"resident", "adaptive_density", "species_separated_plum"}
OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}
KINDS = ("plum", "lemon", "apple", "banana")
ORIGINS = ("natural", "ours", "opponent", "unknown")
RUNNER_EXTRA_FIELDS = (
    "capacity_ready_turns",
    "capacity_separation_violations",
    "entry_state_violations",
    "forbidden_post_entry_commands",
    "post_entry_commands",
    "lineage_recovery_turns",
    "entry_banked_banana",
    "entry_carried_banana",
    "entry_crop_banana_fruits",
    "entry_opponent_banana_crops",
    "entry_own_score",
    "entry_opponent_score",
    "entry_margin",
    "terminal_plants",
    "terminal_banana_plants",
)
SPECIES_FIELDS = tuple(
    f"{collector}_plant_commands_{kind}"
    for collector in ("own", "opponent")
    for kind in KINDS
) + tuple(
    f"{collector}_successful_plants_{kind}"
    for collector in ("own", "opponent")
    for kind in KINDS
) + tuple(f"terminal_plants_{kind}" for kind in KINDS) + (
    "total_harvested_fruit",
    "assigned_harvested_fruit",
) + tuple(
    f"{collector}_fruit_from_{origin}_{kind}"
    for collector in ("own", "opponent")
    for origin in ORIGINS
    for kind in KINDS
)
INTEGER_FIELDS = BASE_INTEGER_FIELDS + RUNNER_EXTRA_FIELDS + SPECIES_FIELDS
REFERENCE_FIELDS = OUTCOME_IDENTITY_FIELDS + (
    "terminal_plants",
    "terminal_banana_plants",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def read_reference(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row["profile"] not in {"resident", "adaptive_density"}:
                continue
            for field in ("seed", "seat") + REFERENCE_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def control_identity(rows: list[dict], reference: list[dict] | None) -> dict:
    if reference is None:
        return {"checked": False, "mismatches": [], "passed": False}
    current = {
        (identity(row), row["profile"]): row
        for row in rows
        if row["profile"] in {"resident", "adaptive_density"}
    }
    prior = {
        (identity(row), row["profile"]): row
        for row in reference
        if row["profile"] in {"resident", "adaptive_density"}
    }
    if current.keys() != prior.keys():
        return {
            "checked": True,
            "mismatches": ["control grids differ"],
            "passed": False,
        }
    mismatches = []
    for key in sorted(current):
        fields = {
            field: [current[key][field], prior[key][field]]
            for field in REFERENCE_FIELDS
            if current[key][field] != prior[key][field]
        }
        if fields:
            mismatches.append({"identity_profile": key, "fields": fields})
    return {"checked": True, "mismatches": mismatches, "passed": not mismatches}


def summarize(rows: list[dict]) -> dict:
    report = base_summarize(rows)
    total_fruit = sum(row["total_harvested_fruit"] for row in rows)
    assigned_fruit = sum(row["assigned_harvested_fruit"] for row in rows)
    report.update(
        {
            "plant_commands": {
                collector: {
                    kind: sum(row[f"{collector}_plant_commands_{kind}"] for row in rows)
                    for kind in KINDS
                }
                for collector in ("own", "opponent")
            },
            "successful_plants_by_kind": {
                collector: {
                    kind: sum(
                        row[f"{collector}_successful_plants_{kind}"] for row in rows
                    )
                    for kind in KINDS
                }
                for collector in ("own", "opponent")
            },
            "fruit_assignment_rate": (
                assigned_fruit / total_fruit if total_fruit else None
            ),
            "harvested_fruit": {
                collector: {
                    origin: {
                        kind: sum(
                            row[f"{collector}_fruit_from_{origin}_{kind}"]
                            for row in rows
                        )
                        for kind in KINDS
                    }
                    for origin in ORIGINS
                }
                for collector in ("own", "opponent")
            },
            "mean_terminal_plants_by_kind": {
                kind: statistics.mean(row[f"terminal_plants_{kind}"] for row in rows)
                for kind in KINDS
            },
        }
    )
    return report


def analyze(
    rows: list[dict],
    phase: str,
    repeat_exact: bool | None = None,
    reference: list[dict] | None = None,
) -> dict:
    unique = [(identity(row), row["profile"]) for row in rows]
    if len(unique) != len(set(unique)):
        raise ValueError("duplicate scenario-profile rows")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    if set(grouped) != PROFILES:
        raise ValueError(f"expected profiles {sorted(PROFILES)}")

    expected_range = {
        "mechanism": range(0, 30),
        "discovery": range(2260, 2320),
        "confirmation": range(2320, 2380),
    }[phase]
    expected_opponents = {"gold_adaptive"} if phase == "mechanism" else OPPONENTS
    expected = {
        (seed, seat, opponent)
        for seed in expected_range
        for seat in (0, 1)
        for opponent in expected_opponents
    }
    grids = [{identity(row) for row in group} for group in grouped.values()]
    if any(grid != expected for grid in grids):
        raise ValueError("input is not the frozen complete grid")

    candidate = grouped["species_separated_plum"]
    banana = grouped["adaptive_density"]
    resident = grouped["resident"]
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    candidate_report = reports["species_separated_plum"]
    control = control_identity(rows, reference) if phase == "mechanism" else {
        "checked": False,
        "mismatches": [],
        "passed": True,
    }
    integrity = {
        "complete_grid": len(rows) == len(expected) * 3,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "wood_provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "fruit_provenance_assignment": all(
            report["fruit_assignment_rate"] is not None
            and report["fruit_assignment_rate"] >= 0.99
            for report in reports.values()
        ),
        "candidate_only_commands_plum": (
            candidate_report["plant_commands"]["own"]["lemon"] == 0
            and candidate_report["plant_commands"]["own"]["apple"] == 0
            and candidate_report["plant_commands"]["own"]["banana"] == 0
        ),
        "candidate_zero_banana_crop_births": (
            candidate_report["successful_plants_by_kind"]["own"]["banana"] == 0
        ),
        "candidate_plum_breadth": (
            candidate_report["successful_plants_by_kind"]["own"]["plum"] >= 300
        ),
        "historical_control_identity": control["passed"],
    }
    candidate_banana = compare(candidate, banana)
    candidate_resident = compare(candidate, resident)
    opponent_banana_from_ours = candidate_report["harvested_fruit"]["opponent"][
        "ours"
    ]["banana"]
    payload = {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "species_separated_minus_banana_farm": candidate_banana,
        "species_separated_minus_resident": candidate_resident,
        "opponent_banana_fruit_from_candidate_crops": opponent_banana_from_ours,
        "control_identity": control,
        "integrity_checks": integrity,
    }

    if phase == "mechanism":
        integrity["repeat_run_identity"] = repeat_exact is True
        checks = {
            "integrity": all(integrity.values()),
            "own_score_preservation": candidate_banana["mean_own_score_delta"] >= -60,
            "opponent_score_suppression": candidate_banana[
                "mean_opponent_score_delta"
            ]
            <= -15,
            "opponent_plant_suppression": candidate_banana[
                "mean_opponent_successful_plants_delta"
            ]
            <= -2,
            "zero_reproductive_banana_leak": opponent_banana_from_ours == 0,
        }
        passed = all(checks.values())
        return {
            **payload,
            "mechanism_checks": checks,
            "passed": passed,
            "decision": (
                "open frozen discovery"
                if passed
                else "close static commodity-species substitution"
            ),
        }

    margin_deltas = [
        left["margin"] - right["margin"]
        for left, right in zip(
            sorted(candidate, key=identity), sorted(resident, key=identity), strict=True
        )
    ]
    trimmed = trimmed_mean(margin_deltas, 0.10)
    opponent_deltas = {
        opponent: compare(
            [row for row in candidate if row["opponent"] == opponent],
            [row for row in resident if row["opponent"] == opponent],
        )["mean_margin_delta"]
        for opponent in sorted(OPPONENTS)
    }
    adaptive_candidate = [
        row for row in candidate if row["opponent"] == "gold_adaptive"
    ]
    adaptive_banana = [row for row in banana if row["opponent"] == "gold_adaptive"]
    adaptive_resident = [
        row for row in resident if row["opponent"] == "gold_adaptive"
    ]
    adaptive_vs_banana = compare(adaptive_candidate, adaptive_banana)
    adaptive_vs_resident = compare(adaptive_candidate, adaptive_resident)
    positive = sum(delta > 0 for delta in opponent_deltas.values())
    worst = min(opponent_deltas.values())
    confirmation = phase == "confirmation"
    checks = {
        "integrity": all(integrity.values()),
        "mean_margin": candidate_resident["mean_margin_delta"]
        >= (2.0 if confirmation else 3.0),
        "trimmed_10pct_margin": trimmed >= 0,
        "own_score": candidate_resident["mean_own_score_delta"]
        >= (20.0 if confirmation else 25.0),
        "opponent_breadth": positive >= 5,
        "worst_opponent": worst >= -12.0,
        "adaptive_margin": adaptive_vs_resident["mean_margin_delta"] >= 0,
        "adaptive_opponent_score_suppression_vs_banana": adaptive_vs_banana[
            "mean_opponent_score_delta"
        ]
        <= (-15.0 if confirmation else -20.0),
        "adaptive_opponent_plant_suppression_vs_banana": adaptive_vs_banana[
            "mean_opponent_successful_plants_delta"
        ]
        <= (-2.0 if confirmation else -3.0),
        "adaptive_own_score_preservation_vs_banana": adaptive_vs_banana[
            "mean_own_score_delta"
        ]
        >= -40.0,
    }
    passed = all(checks.values())
    return {
        **payload,
        "trimmed_10pct_mean_margin_delta": trimmed,
        "opponent_mean_margin_deltas": opponent_deltas,
        "positive_opponents": positive,
        "worst_opponent_mean_margin_delta": worst,
        "adaptive_gold": {
            "species_separated_minus_resident": adaptive_vs_resident,
            "species_separated_minus_banana_farm": adaptive_vs_banana,
        },
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for source integration and arena-transfer audit"
            if phase == "confirmation" and passed
            else "close static commodity-species substitution"
        ),
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--phase", choices=("mechanism", "discovery", "confirmation"), required=True
    )
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--control-reference", type=Path)
    args = parser.parse_args()
    repeat_exact = (
        args.repeat.read_bytes() == args.input.read_bytes() if args.repeat else None
    )
    reference = read_reference(args.control_reference) if args.control_reference else None
    payload = analyze(read_rows(args.input), args.phase, repeat_exact, reference)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
