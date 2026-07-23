#!/usr/bin/env python3
"""Analyze exact one-intervention resident residual continuation labels."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d11_recipe_catalog_analysis import summary  # noqa: E402

START = 360_000
STOP = 360_240
STRING_FIELDS = {
    "opponent",
    "local_plant_type",
    "resident_command",
    "resident_verb",
    "previous_command",
    "previous_verb",
    "other_command",
    "other_verb",
    "alternative_command",
    "alternative_verb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field, value in list(row.items()):
            if field not in STRING_FIELDS:
                row[field] = int(value)
    return rows


def validate(rows: list[dict]) -> None:
    scenarios = Counter(row["scenario"] for row in rows)
    if len(rows) != 2_400 or set(scenarios) != set(range(START, STOP)):
        raise ValueError(
            f"incomplete MC density block: rows={len(rows)}, scenarios={len(scenarios)}"
        )
    if any(count != 10 for count in scenarios.values()):
        raise ValueError("every scenario must contribute exactly ten labels")
    slots = defaultdict(set)
    for row in rows:
        slots[row["scenario"]].add(row["sample_slot"])
        if row["candidate_count"] < 10:
            raise ValueError("scenario has fewer than ten candidate events")
        if row["alternative_plane"] == 0:
            raise ValueError("teacher row contains KEEP instead of an alternative")
    if any(values != set(range(10)) for values in slots.values()):
        raise ValueError("sample slots must be 0--9 in every scenario")


def group_stats(rows: list[dict], key) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[str(key(row))].append(row)
    return {
        label: {
            "labels": len(bucket),
            "positive": sum(row["margin_advantage"] > 0 for row in bucket),
            "positive_rate": statistics.mean(
                row["margin_advantage"] > 0 for row in bucket
            ),
            "at_least_plus2": sum(row["margin_advantage"] >= 2 for row in bucket),
            "mean_margin_advantage": statistics.mean(
                row["margin_advantage"] for row in bucket
            ),
            "mean_wood_advantage": statistics.mean(
                row["wood_advantage"] for row in bucket
            ),
        }
        for label, bucket in sorted(groups.items())
    }


def turn_quartile(turn: int) -> str:
    if turn <= 75:
        return "01-075"
    if turn <= 150:
        return "076-150"
    if turn <= 225:
        return "151-225"
    return "226-301"


def analyze(rows: list[dict], input_path: Path) -> dict:
    validate(rows)
    positive = [row for row in rows if row["margin_advantage"] > 0]
    negative = [row for row in rows if row["margin_advantage"] < 0]
    ties = [row for row in rows if row["margin_advantage"] == 0]
    plus2 = [row for row in rows if row["margin_advantage"] >= 2]
    positive_maps = {row["map_seed"] for row in positive}
    positive_opponents = {row["opponent"] for row in positive}
    positive_roles = {row["ordinal"] for row in positive}
    positive_planes = {row["alternative_plane"] for row in positive}
    per_map_positive = Counter(row["map_seed"] for row in positive)
    maximum_map_share = (
        max(per_map_positive.values()) / len(positive) if positive else None
    )
    gates = {
        "complete_2400_labels": len(rows) == 2_400,
        "clone_fidelity_240_of_240": True,
        "at_least_48_positive_labels": len(positive) >= 48,
        "at_least_24_labels_plus2": len(plus2) >= 24,
        "positive_on_at_least_8_maps": len(positive_maps) >= 8,
        "positive_against_at_least_4_opponents": len(positive_opponents) >= 4,
        "positive_in_both_resident_roles": {0, 1}.issubset(positive_roles),
        "at_least_2_positive_action_planes": len(positive_planes) >= 2,
        "maximum_positive_map_share_at_most_30_percent": (
            maximum_map_share is not None and maximum_map_share <= 0.30
        ),
    }
    eligible = all(gates.values())
    return {
        "schema": 1,
        "scope": (
            "D16 exact one-intervention Monte Carlo teacher density audit on "
            "development scenarios; no runtime search, candidate, or Arena authorization"
        ),
        "source": {
            "rows": str(input_path),
            "rows_sha256": sha256(input_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "scenario_start": START,
            "scenario_stop_exclusive": STOP,
            "scenarios": 240,
            "maps": 20,
            "samples_per_scenario": 10,
            "labels": len(rows),
            "complete": True,
            "clone_fidelity": (
                "runner aborts before output on any mismatch; complete output proves 240/240"
            ),
        },
        "overall": {
            "margin_advantage": summary(row["margin_advantage"] for row in rows),
            "wood_advantage": summary(row["wood_advantage"] for row in rows),
            "positive_labels": len(positive),
            "positive_rate": len(positive) / len(rows),
            "tie_labels": len(ties),
            "tie_rate": len(ties) / len(rows),
            "negative_labels": len(negative),
            "negative_rate": len(negative) / len(rows),
            "labels_at_least_plus2": len(plus2),
            "positive_maps": len(positive_maps),
            "positive_opponents": len(positive_opponents),
            "positive_roles": sorted(positive_roles),
            "positive_action_planes": sorted(positive_planes),
            "maximum_positive_map_share": maximum_map_share,
            "new_catastrophes": sum(row["new_catastrophe"] for row in rows),
            "continuation_elapsed_us": summary(row["elapsed_us"] for row in rows),
        },
        "slices": {
            "map": group_stats(rows, lambda row: row["map_seed"]),
            "opponent": group_stats(rows, lambda row: row["opponent"]),
            "seat": group_stats(rows, lambda row: row["seat"]),
            "role": group_stats(rows, lambda row: row["ordinal"]),
            "resident_verb": group_stats(rows, lambda row: row["resident_verb"]),
            "alternative_verb": group_stats(
                rows, lambda row: row["alternative_verb"]
            ),
            "alternative_plane": group_stats(
                rows, lambda row: row["alternative_plane"]
            ),
            "turn_quartile": group_stats(
                rows, lambda row: turn_quartile(row["turn"])
            ),
            "worker_spec": group_stats(
                rows,
                lambda row: f"{row['ms']}/{row['cc']}/{row['hp']}/{row['chop']}",
            ),
        },
        "density_gate": {
            "gates": gates,
            "eligible_for_larger_distillation_corpus": eligible,
            "authorization": (
                "larger frozen train/validation label corpus only; no policy, "
                "candidate, submission, or Arena activity"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rows", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(read_rows(args.rows), args.rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "design": result["design"],
        "overall": result["overall"],
        "density_gate": result["density_gate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

