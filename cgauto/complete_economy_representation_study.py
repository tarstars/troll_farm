#!/usr/bin/env python3
"""Apply the frozen complete-economy representation smoke gates."""

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


CONFIG_FIELDS = (
    "max_trolls",
    "choppers",
    "stagger",
    "spec1_ms",
    "spec1_cc",
    "spec1_hp",
    "spec1_chop",
    "spec2_ms",
    "spec2_cc",
    "spec2_hp",
    "spec2_chop",
    "planters",
    "hold_until",
    "farm_cap",
    "co_fell",
    "adaptive",
)

INTEGER_FIELDS = (
    "seed",
    "seat",
    *CONFIG_FIELDS,
    "resident_margin",
    "candidate_margin",
    "margin_delta",
    "resident_score",
    "candidate_score",
    "score_delta",
    "resident_opponent_score",
    "candidate_opponent_score",
    "opponent_score_delta",
    "resident_wood",
    "candidate_wood",
    "wood_delta",
    "resident_opponent_wood",
    "candidate_opponent_wood",
    "opponent_wood_delta",
    "resident_workers",
    "candidate_workers",
    "resident_terminal_turn",
    "candidate_terminal_turn",
    "resident_successful_trains",
    "candidate_successful_trains",
    "resident_successful_plants",
    "candidate_successful_plants",
    "resident_harvest",
    "candidate_harvest",
    "resident_chop",
    "candidate_chop",
    "resident_drop",
    "candidate_drop",
    "resident_pick",
    "candidate_pick",
    "resident_mine",
    "candidate_mine",
    "divergence_turns",
    "resident_identity_mismatches",
)

DISCOVERY_GATE = {
    "minimum_mean_margin_delta": 0,
    "strictly_positive_trimmed_cell_margin": True,
    "strictly_positive_seed_mean_margin": True,
    "strictly_positive_trimmed_seed_margin": True,
    "minimum_favorable_to_unfavorable_ratio": 1.0,
    "minimum_nonnegative_opponents": 6,
    "minimum_worst_opponent_mean_margin": -10,
    "minimum_mean_score_delta": 0,
    "minimum_mean_wood_delta": 0,
    "minimum_changed_cells": 80,
    "minimum_train_cells": 80,
    "minimum_plant_cells": 80,
}

CONFIRMATION_GATE = {
    **DISCOVERY_GATE,
    "minimum_mean_margin_delta": 2,
    "minimum_seed_mean_margin_delta": 2,
    "minimum_worst_opponent_mean_margin": -5,
}


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def trimmed_mean(values: list[float], fraction: float = 0.05) -> float:
    if not values:
        raise ValueError("cannot trim an empty sample")
    ordered = sorted(values)
    trim = math.floor(fraction * len(ordered))
    kept = ordered[trim : len(ordered) - trim] if trim else ordered
    return statistics.mean(kept)


def distribution(values: list[float]) -> dict:
    if not values:
        raise ValueError("cannot summarize an empty sample")
    ordered = sorted(values)
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "trimmed_5pct_mean": trimmed_mean(values),
        "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0,
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def summarize_genome(rows: list[dict], phase: str) -> dict:
    config_values = {tuple(row[field] for field in CONFIG_FIELDS) for row in rows}
    if len(config_values) != 1:
        raise ValueError("genome configuration changes within its grid")
    config_value = next(iter(config_values))
    parameters = dict(zip(CONFIG_FIELDS, config_value, strict=True))

    cell_margin = distribution([row["margin_delta"] for row in rows])
    by_seed: dict[int, list[int]] = defaultdict(list)
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row["margin_delta"])
        by_opponent[row["opponent"]].append(row)
    seed_margin = distribution(
        [statistics.mean(by_seed[seed]) for seed in sorted(by_seed)]
    )
    opponent_reports = {
        opponent: {
            "cells": len(group),
            "mean_margin_delta": mean(group, "margin_delta"),
            "mean_score_delta": mean(group, "score_delta"),
            "mean_wood_delta": mean(group, "wood_delta"),
            "changed_cells": sum(row["divergence_turns"] > 0 for row in group),
        }
        for opponent, group in sorted(by_opponent.items())
    }
    opponent_margins = [
        report["mean_margin_delta"] for report in opponent_reports.values()
    ]
    nonnegative_opponents = sum(value >= 0 for value in opponent_margins)
    worst_opponent = min(opponent_margins)
    favorable_ratio = (
        cell_margin["positive"] / cell_margin["negative"]
        if cell_margin["negative"]
        else math.inf
    )
    changed_cells = sum(row["divergence_turns"] > 0 for row in rows)
    train_cells = sum(row["candidate_successful_trains"] > 0 for row in rows)
    plant_cells = sum(row["candidate_successful_plants"] > 0 for row in rows)
    gate = CONFIRMATION_GATE if phase == "confirmation" else DISCOVERY_GATE
    checks = {
        "mean_margin_delta": cell_margin["mean"]
        >= gate["minimum_mean_margin_delta"]
        and (phase == "confirmation" or cell_margin["mean"] > 0),
        "trimmed_cell_margin": cell_margin["trimmed_5pct_mean"] > 0,
        "seed_mean_margin": seed_margin["mean"]
        >= gate.get("minimum_seed_mean_margin_delta", 0)
        and (phase == "confirmation" or seed_margin["mean"] > 0),
        "trimmed_seed_margin": seed_margin["trimmed_5pct_mean"] > 0,
        "favorable_to_unfavorable": favorable_ratio
        >= gate["minimum_favorable_to_unfavorable_ratio"],
        "nonnegative_opponents": nonnegative_opponents
        >= gate["minimum_nonnegative_opponents"],
        "worst_opponent": worst_opponent
        >= gate["minimum_worst_opponent_mean_margin"],
        "mean_score_delta": mean(rows, "score_delta")
        >= gate["minimum_mean_score_delta"],
        "mean_wood_delta": mean(rows, "wood_delta")
        >= gate["minimum_mean_wood_delta"],
        "changed_cells": changed_cells >= gate["minimum_changed_cells"],
        "train_cells": train_cells >= gate["minimum_train_cells"],
        "plant_cells": plant_cells >= gate["minimum_plant_cells"],
    }
    return {
        "parameters": parameters,
        "cells": len(rows),
        "seeds": len(by_seed),
        "cell_margin_delta": cell_margin,
        "seed_mean_margin_delta": seed_margin,
        "mean_score_delta": mean(rows, "score_delta"),
        "mean_opponent_score_delta": mean(rows, "opponent_score_delta"),
        "mean_wood_delta": mean(rows, "wood_delta"),
        "mean_opponent_wood_delta": mean(rows, "opponent_wood_delta"),
        "mean_candidate_workers": mean(rows, "candidate_workers"),
        "mean_successful_trains": mean(rows, "candidate_successful_trains"),
        "mean_successful_plants": mean(rows, "candidate_successful_plants"),
        "mean_harvest_commands": mean(rows, "candidate_harvest"),
        "mean_chop_commands": mean(rows, "candidate_chop"),
        "changed_cells": changed_cells,
        "train_cells": train_cells,
        "plant_cells": plant_cells,
        "favorable_to_unfavorable_ratio": favorable_ratio,
        "nonnegative_opponents": nonnegative_opponents,
        "worst_opponent_mean_margin": worst_opponent,
        "opponents": opponent_reports,
        "gate_checks": checks,
        "gate_passed": all(checks.values()),
    }


def selection_key(label: str, report: dict) -> tuple:
    return (
        -report["nonnegative_opponents"],
        -report["worst_opponent_mean_margin"],
        -report["seed_mean_margin_delta"]["trimmed_5pct_mean"],
        -report["seed_mean_margin_delta"]["mean"],
        label,
    )


def analyze(rows: list[dict], phase: str) -> dict:
    if not rows:
        raise ValueError("complete-economy study has no rows")
    identities = {
        (row["seed"], row["seat"], row["opponent"], row["genome"])
        for row in rows
    }
    if len(identities) != len(rows):
        raise ValueError("duplicate genome scenario rows")
    if any(row["resident_identity_mismatches"] != 0 for row in rows):
        raise ValueError("resident grammar is not command-identical")
    if any(
        not 1 <= row["resident_terminal_turn"] <= 301
        or not 1 <= row["candidate_terminal_turn"] <= 301
        for row in rows
    ):
        raise ValueError("game did not terminate inside the corrected horizon")

    grouped: dict[str, list[dict]] = defaultdict(list)
    grids: dict[str, set[tuple[int, int, str]]] = defaultdict(set)
    for row in rows:
        grouped[row["genome"]].append(row)
        grids[row["genome"]].add((row["seed"], row["seat"], row["opponent"]))
    expected_grid = next(iter(grids.values()))
    incomplete = [label for label, grid in grids.items() if grid != expected_grid]
    if incomplete:
        raise ValueError(f"genomes have different scenario grids: {sorted(incomplete)}")
    seed_values = sorted({row["seed"] for row in rows})
    opponent_values = sorted({row["opponent"] for row in rows})
    expected_cells = len(seed_values) * 2 * len(opponent_values)
    if len(expected_grid) != expected_cells:
        raise ValueError("scenario grid is incomplete")
    if len(seed_values) != 30 or len(opponent_values) != 8:
        raise ValueError("frozen smoke requires 30 seeds and eight opponents")
    if phase == "discovery" and len(grouped) != 31:
        raise ValueError("discovery requires the exact 31-genome catalog")
    if phase == "confirmation" and not 1 <= len(grouped) <= 3:
        raise ValueError("confirmation requires one to three selected genomes")

    reports = {
        label: summarize_genome(group, phase)
        for label, group in sorted(grouped.items())
    }
    eligible = [label for label, report in reports.items() if report["gate_passed"]]
    ranking = sorted(eligible, key=lambda label: selection_key(label, reports[label]))
    selected = ranking[:3] if phase == "discovery" else ranking
    integrity = {
        "resident_identity": True,
        "unique_rows": True,
        "complete_equal_grids": True,
        "terminal_horizon": True,
        "catalog_size": len(grouped),
        "cells_per_genome": len(expected_grid),
    }
    return {
        "schema": 1,
        "phase": phase,
        "scope": (
            "closed-loop terminal outcome representation smoke on consumed seeds; "
            "never candidate-qualification evidence"
        ),
        "seed_range": [min(seed_values), max(seed_values)],
        "seeds": seed_values,
        "opponents": opponent_values,
        "genomes": len(grouped),
        "rows": len(rows),
        "integrity": integrity,
        "gate": CONFIRMATION_GATE if phase == "confirmation" else DISCOVERY_GATE,
        "eligible_genomes": ranking,
        "selected_genomes": selected,
        "representation_gate_passed": phase == "confirmation" and bool(selected),
        "open_confirmation": phase == "discovery" and bool(selected),
        "reports": reports,
        "decision": (
            "run unchanged selections on consumed seeds 30--59"
            if phase == "discovery" and selected
            else "close the farm-economy grammar without opening confirmation"
            if phase == "discovery"
            else "representation is expressive; opponent-coverage iteration required next"
            if selected
            else "close the farm-economy grammar without retuning"
        ),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("discovery", "confirmation"), required=True)
    args = parser.parse_args()
    payload = analyze(read_rows(args.input), args.phase)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps({key: payload[key] for key in (
        "phase", "seed_range", "genomes", "rows", "eligible_genomes",
        "selected_genomes", "representation_gate_passed", "open_confirmation", "decision"
    )}, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
