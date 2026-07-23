#!/usr/bin/env python3
"""Analyze the frozen terminal-value-rate orchard task-market experiment."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
import os
from pathlib import Path
import statistics
import tempfile

try:
    from cgauto.prefruit_reproductive_interruption import (
        OUTCOME_IDENTITY_FIELDS,
        compare,
        identity,
        trimmed_mean,
    )
    from cgauto.species_separated_renewable_supply import (
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        REFERENCE_FIELDS,
        read_reference,
        summarize,
    )
except ModuleNotFoundError:  # Direct script execution.
    from prefruit_reproductive_interruption import (  # type: ignore[no-redef]
        OUTCOME_IDENTITY_FIELDS,
        compare,
        identity,
        trimmed_mean,
    )
    from species_separated_renewable_supply import (  # type: ignore[no-redef]
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        REFERENCE_FIELDS,
        read_reference,
        summarize,
    )


PROFILES = {"resident", "task_market_orchard"}
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
ORCHARD_FIELDS = (
    "orchard_activation_turn",
    "orchard_seed_repaid_turn",
    "orchard_market_turns",
    "orchard_offers",
    "orchard_selections",
    "orchard_harvest_selections",
    "orchard_first_selection_turn",
    "orchard_forced_setup_actions",
    "orchard_premarket_mismatches",
)
INTEGER_FIELDS = BASE_INTEGER_FIELDS + ORCHARD_FIELDS
INACTIVE_IDENTITY_FIELDS = tuple(dict.fromkeys(OUTCOME_IDENTITY_FIELDS + REFERENCE_FIELDS))


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def reference_identity(rows: list[dict], reference: list[dict] | None) -> dict:
    if reference is None:
        return {"checked": False, "overlap": 0, "mismatches": [], "passed": False}
    current = {
        identity(row): row for row in rows if row["profile"] == "resident"
    }
    prior = {
        identity(row): row for row in reference if row["profile"] == "resident"
    }
    missing = sorted(set(prior) - set(current))
    mismatches = []
    for key in sorted(set(prior) & set(current)):
        fields = {
            field: [current[key][field], prior[key][field]]
            for field in REFERENCE_FIELDS
            if current[key][field] != prior[key][field]
        }
        if fields:
            mismatches.append({"identity": key, "fields": fields})
    if missing:
        mismatches.append({"missing_reference_identities": missing})
    return {
        "checked": True,
        "overlap": len(set(prior) & set(current)),
        "mismatches": mismatches,
        "passed": bool(prior) and not mismatches,
    }


def lower_quantile(values: list[int], fraction: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[math.floor((len(ordered) - 1) * fraction)]


def worst_fraction_mean(values: list[int], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    count = max(1, math.ceil(len(ordered) * fraction))
    return statistics.mean(ordered[:count])


def paired_rows(candidate: list[dict], resident: list[dict]) -> list[dict]:
    candidate_map = {identity(row): row for row in candidate}
    resident_map = {identity(row): row for row in resident}
    if candidate_map.keys() != resident_map.keys():
        raise ValueError("candidate and resident grids differ")
    return [
        {
            "identity": key,
            "candidate": candidate_map[key],
            "resident": resident_map[key],
            "margin_delta": candidate_map[key]["margin"] - resident_map[key]["margin"],
            "own_score_delta": candidate_map[key]["own_score"]
            - resident_map[key]["own_score"],
            "opponent_score_delta": candidate_map[key]["opponent_score"]
            - resident_map[key]["opponent_score"],
            "wood_delta": candidate_map[key]["own_inventory_wood"]
            - resident_map[key]["own_inventory_wood"],
        }
        for key in sorted(candidate_map)
    ]


def inactive_identity(pairs: list[dict]) -> dict:
    inactive = [pair for pair in pairs if pair["candidate"]["orchard_seed_repaid_turn"] < 0]
    mismatches = []
    for pair in inactive:
        fields = {
            field: [pair["candidate"][field], pair["resident"][field]]
            for field in INACTIVE_IDENTITY_FIELDS
            if pair["candidate"][field] != pair["resident"][field]
        }
        if fields:
            mismatches.append({"identity": pair["identity"], "fields": fields})
    return {
        "inactive_cells": len(inactive),
        "mismatches": mismatches,
        "passed": not mismatches,
    }


def orchard_timing_integrity(candidate: list[dict]) -> dict:
    violations = []
    for row in candidate:
        activation = row["orchard_activation_turn"]
        repaid = row["orchard_seed_repaid_turn"]
        first = row["orchard_first_selection_turn"]
        if repaid >= 0 and (activation < 0 or activation > repaid):
            violations.append((identity(row), "repayment_without_ordered_activation"))
        if row["orchard_market_turns"] > 0 and repaid < 0:
            violations.append((identity(row), "market_before_repayment"))
        if row["orchard_offers"] > 0 and repaid < 0:
            violations.append((identity(row), "offer_before_repayment"))
        if row["orchard_selections"] > row["orchard_offers"]:
            violations.append((identity(row), "selection_without_offer"))
        if row["orchard_harvest_selections"] > row["orchard_selections"]:
            violations.append((identity(row), "harvest_without_selection"))
        if (row["orchard_selections"] > 0) != (first >= 0):
            violations.append((identity(row), "first_selection_presence"))
        if first >= 0 and (repaid < 0 or first <= repaid):
            violations.append((identity(row), "selection_not_after_repayment"))
        if activation >= 0 and row["orchard_forced_setup_actions"] == 0:
            violations.append((identity(row), "activation_without_setup"))
    return {"violations": violations, "passed": not violations}


def active_summary(pairs: list[dict]) -> dict:
    active = [pair for pair in pairs if pair["candidate"]["orchard_seed_repaid_turn"] >= 0]
    margin = [pair["margin_delta"] for pair in active]
    own = [pair["own_score_delta"] for pair in active]
    opponent = [pair["opponent_score_delta"] for pair in active]
    return {
        "cells": len(active),
        "mean_margin_delta": statistics.mean(margin) if margin else None,
        "trimmed_10pct_mean_margin_delta": trimmed_mean(margin, 0.10) if margin else None,
        "mean_own_score_delta": statistics.mean(own) if own else None,
        "mean_opponent_score_delta": statistics.mean(opponent) if opponent else None,
        "mean_wood_delta": (
            statistics.mean(pair["wood_delta"] for pair in active) if active else None
        ),
        "improved_tied_regressed": {
            "improved": sum(value > 0 for value in margin),
            "tied": sum(value == 0 for value in margin),
            "regressed": sum(value < 0 for value in margin),
        },
        "minimum_margin_delta": min(margin) if margin else None,
        "tenth_percentile_margin_delta": lower_quantile(margin, 0.10),
        "worst_5pct_mean_margin_delta": worst_fraction_mean(margin, 0.05),
        "maximum_margin_delta": max(margin) if margin else None,
        "margin_deltas": sorted(margin),
    }


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
        "mechanism": range(0, 100),
        "discovery": range(2380, 2440),
        "confirmation": range(2440, 2500),
    }[phase]
    expected = {
        (seed, seat, opponent)
        for seed in expected_range
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    if any({identity(row) for row in group} != expected for group in grouped.values()):
        raise ValueError("input is not the frozen complete grid")

    candidate = grouped["task_market_orchard"]
    resident = grouped["resident"]
    pairs = paired_rows(candidate, resident)
    active = active_summary(pairs)
    inactive = inactive_identity(pairs)
    timing = orchard_timing_integrity(candidate)
    reference_check = (
        reference_identity(rows, reference)
        if phase == "mechanism"
        else {"checked": False, "overlap": 0, "mismatches": [], "passed": True}
    )
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    candidate_report = reports["task_market_orchard"]
    resident_report = reports["resident"]
    fruit_rates = {
        profile: report["fruit_assignment_rate"] for profile, report in reports.items()
    }
    integrity = {
        "complete_grid": len(rows) == len(expected) * len(PROFILES),
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "wood_provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "fruit_provenance_assignment": all(
            rate is not None and rate >= 0.95 for rate in fruit_rates.values()
        ),
        "historical_resident_identity": reference_check["passed"],
        "inactive_candidate_identity": inactive["passed"],
        "premarket_command_identity": sum(
            row["orchard_premarket_mismatches"] for row in candidate
        )
        == 0,
        "orchard_timing": timing["passed"],
    }
    if phase == "mechanism":
        integrity["repeat_run_identity"] = repeat_exact is True

    comparison = compare(candidate, resident)
    opponent_deltas = {
        opponent: compare(
            [row for row in candidate if row["opponent"] == opponent],
            [row for row in resident if row["opponent"] == opponent],
        )["mean_margin_delta"]
        for opponent in sorted(OPPONENTS)
    }
    telemetry = {
        "activated_cells": sum(row["orchard_activation_turn"] >= 0 for row in candidate),
        "repaid_cells": active["cells"],
        "market_turns": sum(row["orchard_market_turns"] for row in candidate),
        "offers": sum(row["orchard_offers"] for row in candidate),
        "selections": sum(row["orchard_selections"] for row in candidate),
        "harvest_selections": sum(
            row["orchard_harvest_selections"] for row in candidate
        ),
        "forced_setup_actions": sum(
            row["orchard_forced_setup_actions"] for row in candidate
        ),
        "median_activation_turn": (
            statistics.median(
                row["orchard_activation_turn"]
                for row in candidate
                if row["orchard_activation_turn"] >= 0
            )
            if any(row["orchard_activation_turn"] >= 0 for row in candidate)
            else None
        ),
        "median_seed_repaid_turn": (
            statistics.median(
                row["orchard_seed_repaid_turn"]
                for row in candidate
                if row["orchard_seed_repaid_turn"] >= 0
            )
            if active["cells"]
            else None
        ),
    }
    payload = {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "candidate_minus_resident": comparison,
        "active_cells": active,
        "opponent_mean_margin_deltas": opponent_deltas,
        "telemetry": telemetry,
        "inactive_identity": inactive,
        "timing_integrity": timing,
        "historical_resident_identity": reference_check,
        "integrity_checks": integrity,
    }

    if phase == "mechanism":
        checks = {
            "integrity": all(integrity.values()),
            "repaid_breadth": telemetry["repaid_cells"] >= 20,
            "offer_breadth": telemetry["offers"] >= 50,
            "selection_breadth": telemetry["selections"] >= 10,
            "active_mean_margin": active["mean_margin_delta"] is not None
            and active["mean_margin_delta"] >= -5.0,
            "active_trimmed_margin": active["trimmed_10pct_mean_margin_delta"]
            is not None
            and active["trimmed_10pct_mean_margin_delta"] >= -2.0,
            "active_own_score": active["mean_own_score_delta"] is not None
            and active["mean_own_score_delta"] >= -5.0,
            "active_lower_tail": active["worst_5pct_mean_margin_delta"] is not None
            and active["worst_5pct_mean_margin_delta"] >= -30.0,
        }
        passed = all(checks.values())
        return {
            **payload,
            "mechanism_checks": checks,
            "passed": passed,
            "decision": (
                "open frozen fresh discovery"
                if passed
                else "close terminal-value-rate orchard task"
            ),
        }

    margin_deltas = [pair["margin_delta"] for pair in pairs]
    positive_families = sum(value > 0 for value in opponent_deltas.values())
    worst_family = min(opponent_deltas.values())
    active_counts = active["improved_tied_regressed"]
    confirmation = phase == "confirmation"
    checks = {
        "integrity": all(integrity.values()),
        "overall_mean_margin": comparison["mean_margin_delta"] >= 0.5,
        "overall_trimmed_margin": trimmed_mean(margin_deltas, 0.10) >= 0,
        "active_mean_margin": active["mean_margin_delta"] is not None
        and active["mean_margin_delta"] >= (5.0 if confirmation else 8.0),
        "active_own_score": active["mean_own_score_delta"] is not None
        and active["mean_own_score_delta"] >= (3.0 if confirmation else 5.0),
        "active_sign": active_counts["improved"] > active_counts["regressed"],
        "opponent_breadth": positive_families >= 3,
        "worst_opponent": worst_family >= -3.0,
        "adaptive_gold": opponent_deltas["gold_adaptive"] >= 0,
        "active_worst_case": active["minimum_margin_delta"] is not None
        and active["minimum_margin_delta"] >= -25,
        "active_tenth_percentile": active["tenth_percentile_margin_delta"]
        is not None
        and active["tenth_percentile_margin_delta"] >= -10,
    }
    passed = all(checks.values())
    return {
        **payload,
        "trimmed_10pct_mean_margin_delta": trimmed_mean(margin_deltas, 0.10),
        "positive_opponent_families": positive_families,
        "worst_opponent_mean_margin_delta": worst_family,
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for source and arena-transfer audits"
            if phase == "confirmation" and passed
            else "close terminal-value-rate orchard task"
        ),
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
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

