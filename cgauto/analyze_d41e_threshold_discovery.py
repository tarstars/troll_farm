#!/usr/bin/env python3
"""Audit the simple D41e branch/gap rule on consumed D41d labels."""

from __future__ import annotations

import collections
import csv
import json
import math
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
ROWS = ANALYSIS / "d41d-one-deviation-results-9760000-9760031.tsv"
D41D_ANALYSIS = ANALYSIS / "d41d-one-deviation-analysis-2026-07-21.json"
OUTPUT = ANALYSIS / "d41e-threshold-discovery-2026-07-21.json"
EXPECTED_ROWS_SHA256 = "be1181bbcdb4e5188f19f80377e111803d4a261ad90a4c469928869516559f53"
EXPECTED_D41D_SHA256 = "f4ccbc56a4a013932e1cec1657131a8c4a451a4d55656c5be29a2564e688a24c"

# These constants are a retrospective discovery rule. They become immutable only
# if a later prospective protocol names the resulting artifact by hash.
EVACUATION_GAP_MIN = 0.020
EVACUATION_GAP_MAX = 0.030
RATE_GAP_MIN = 0.280
RATE_GAP_MAX = 0.340
MIDDLE_START = 100
LATE_START = 200
MAP_FOLDS = 8


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        row["map_seed"] = int(row["map_seed"])
        row["turn"] = int(row["turn"])
        row["margin_delta"] = int(row["margin_delta"])
        row["residual_gap"] = float(row["residual_gap"])
    return rows


def select(row: dict) -> bool:
    gap = row["residual_gap"]
    if row["branch"] == "evacuation":
        return EVACUATION_GAP_MIN <= gap <= EVACUATION_GAP_MAX
    if row["branch"] == "rate":
        outside_middle = row["turn"] < MIDDLE_START or row["turn"] >= LATE_START
        return outside_middle and RATE_GAP_MIN <= gap <= RATE_GAP_MAX
    return False


def stats(rows: list[dict]) -> dict:
    values = np.asarray([row["margin_delta"] for row in rows], dtype=np.float64)
    if not len(values):
        return {"samples": 0}
    standard_error = float(values.std(ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0
    mean = float(values.mean())
    return {
        "samples": len(values),
        "mean": mean,
        "standard_error": standard_error,
        "normal_95_low": mean - 1.96 * standard_error,
        "normal_95_high": mean + 1.96 * standard_error,
        "minimum": float(values.min()),
        "median": float(np.median(values)),
        "maximum": float(values.max()),
        "positive_rate": float(np.mean(values > 0)),
        "tie_rate": float(np.mean(values == 0)),
        "negative_rate": float(np.mean(values < 0)),
    }


def grouped(rows: list[dict], field: str) -> dict:
    buckets: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        buckets[str(row[field])].append(row)
    return {key: stats(bucket) for key, bucket in sorted(buckets.items())}


def analyze(rows: list[dict]) -> dict:
    selected = [row for row in rows if select(row)]
    seed_base = min(row["map_seed"] for row in rows)
    folds = {
        str(fold): stats(
            [row for row in selected if (row["map_seed"] - seed_base) % MAP_FOLDS == fold]
        )
        for fold in range(MAP_FOLDS)
    }
    overall = stats(selected)
    by_branch = grouped(selected, "branch")
    by_opponent = grouped(selected, "opponent")
    cohort_counts = collections.Counter(row["cohort"] for row in selected)
    gates = {
        "at_least_128_samples": overall["samples"] >= 128,
        "mean_at_least_8": overall["mean"] >= 8,
        "normal_95_low_above_5": overall["normal_95_low"] > 5,
        "positive_rate_at_least_65pct": overall["positive_rate"] >= 0.65,
        "both_branches_mean_at_least_8": len(by_branch) == 2
        and min(bucket["mean"] for bucket in by_branch.values()) >= 8,
        "all_eight_map_folds_positive": len(folds) == MAP_FOLDS
        and min(bucket["mean"] for bucket in folds.values()) > 0,
        "all_eight_opponents_positive": len(by_opponent) == 8
        and min(bucket["mean"] for bucket in by_opponent.values()) > 0,
        "control_contamination_at_most_10pct": cohort_counts["hash_control"]
        / len(selected)
        <= 0.10,
    }
    return {
        "rule": {
            "evacuation_gap_inclusive": [EVACUATION_GAP_MIN, EVACUATION_GAP_MAX],
            "rate_gap_inclusive": [RATE_GAP_MIN, RATE_GAP_MAX],
            "rate_turn_condition": f"turn < {MIDDLE_START} or turn >= {LATE_START}",
            "fallback": "exact D40 rank zero",
            "proposal": "exact D40 prior rank one",
        },
        "selected_samples": len(selected),
        "cohort_counts": dict(sorted(cohort_counts.items())),
        "overall": overall,
        "by_branch": by_branch,
        "by_phase": grouped(selected, "phase"),
        "by_opponent": by_opponent,
        "map_folds": folds,
        "gates": gates,
        "pass": all(gates.values()),
    }


def main() -> None:
    for required in (ROWS, D41D_ANALYSIS):
        if not required.exists():
            raise SystemExit(f"missing D41e discovery prerequisite: {required}")
    if sha256(ROWS) != EXPECTED_ROWS_SHA256:
        raise SystemExit("D41d continuation rows changed before D41e discovery audit")
    if sha256(D41D_ANALYSIS) != EXPECTED_D41D_SHA256:
        raise SystemExit("D41d analysis changed before D41e discovery audit")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D41e discovery artifact")
    report = {
        "scope": (
            "retrospective D41d discovery only; no fresh outcomes, policy qualification, "
            "candidate, TestSession, submission, or Arena authorization"
        ),
        "rows": str(ROWS),
        "rows_sha256": sha256(ROWS),
        "d41d_analysis": str(D41D_ANALYSIS),
        "d41d_analysis_sha256": sha256(D41D_ANALYSIS),
        "analysis": analyze(read_rows(ROWS)),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
