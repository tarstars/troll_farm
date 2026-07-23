#!/usr/bin/env python3
"""Analyze the frozen D41d paired one-deviation continuation study."""

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
PROTOCOL = ANALYSIS / "d41d-residual-ranked-one-deviation-protocol-2026-07-21.md"
MANIFEST_SUMMARY = ANALYSIS / "d41d-one-deviation-manifest-2026-07-21.json"
ROWS = ANALYSIS / "d41d-one-deviation-results-9760000-9760031.tsv"
AA_A = ANALYSIS / "d41d-one-deviation-aa-a-64.tsv"
AA_B = ANALYSIS / "d41d-one-deviation-aa-b-64.tsv"
OUTPUT = ANALYSIS / "d41d-one-deviation-analysis-2026-07-21.json"
INTEGER_FIELDS = (
    "sample_id",
    "map_seed",
    "task_index",
    "seat",
    "opponent_index",
    "decision_ordinal",
    "turn",
    "branch_index",
    "candidate_count",
    "teacher_action",
    "alternative_action",
    "baseline_own_score",
    "baseline_opponent_score",
    "baseline_margin",
    "baseline_own_workers",
    "baseline_opponent_workers",
    "baseline_own_created_crops",
    "baseline_successful_trains",
    "baseline_invalidated_jobs",
    "baseline_invalid_direct_commands",
    "baseline_provenance_failures",
    "baseline_deposit_prediction_failures",
    "baseline_action_hash",
    "baseline_state_hash",
    "treatment_own_score",
    "treatment_opponent_score",
    "treatment_margin",
    "treatment_own_workers",
    "treatment_opponent_workers",
    "treatment_own_created_crops",
    "treatment_successful_trains",
    "treatment_invalidated_jobs",
    "treatment_invalid_direct_commands",
    "treatment_provenance_failures",
    "treatment_deposit_prediction_failures",
    "treatment_action_hash",
    "treatment_state_hash",
    "own_score_delta",
    "opponent_score_delta",
    "margin_delta",
    "elapsed_us",
)


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in INTEGER_FIELDS:
            row[field] = int(row[field])
        row["residual_gap"] = float(row["residual_gap"])
    return rows


def delta_stats(rows: list[dict], field: str = "margin_delta") -> dict:
    values = np.asarray([row[field] for row in rows], dtype=np.float64)
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
        "p10": float(np.quantile(values, 0.10)),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "p75": float(np.quantile(values, 0.75)),
        "p90": float(np.quantile(values, 0.90)),
        "maximum": float(values.max()),
        "positive_rate": float(np.mean(values > 0)),
        "tie_rate": float(np.mean(values == 0)),
        "negative_rate": float(np.mean(values < 0)),
    }


def summarize(rows: list[dict]) -> dict:
    baseline_catastrophes = sum(row["baseline_margin"] <= -100 for row in rows)
    treatment_catastrophes = sum(row["treatment_margin"] <= -100 for row in rows)
    return {
        "samples": len(rows),
        "margin_delta": delta_stats(rows, "margin_delta"),
        "own_score_delta": delta_stats(rows, "own_score_delta"),
        "opponent_score_delta": delta_stats(rows, "opponent_score_delta"),
        "worker_two_lost": sum(
            row["baseline_own_workers"] >= 2 and row["treatment_own_workers"] < 2
            for row in rows
        ),
        "worker_two_gained": sum(
            row["baseline_own_workers"] < 2 and row["treatment_own_workers"] >= 2
            for row in rows
        ),
        "worker_three_lost": sum(
            row["baseline_own_workers"] >= 3 and row["treatment_own_workers"] < 3
            for row in rows
        ),
        "worker_three_gained": sum(
            row["baseline_own_workers"] < 3 and row["treatment_own_workers"] >= 3
            for row in rows
        ),
        "crop_lost": sum(
            row["baseline_own_created_crops"] > 0
            and row["treatment_own_created_crops"] == 0
            for row in rows
        ),
        "crop_gained": sum(
            row["baseline_own_created_crops"] == 0
            and row["treatment_own_created_crops"] > 0
            for row in rows
        ),
        "baseline_catastrophes": baseline_catastrophes,
        "treatment_catastrophes": treatment_catastrophes,
        "catastrophe_delta": treatment_catastrophes - baseline_catastrophes,
    }


def grouped(rows: list[dict], fields: tuple[str, ...]) -> dict:
    buckets: dict[tuple, list[dict]] = collections.defaultdict(list)
    for row in rows:
        buckets[tuple(row[field] for field in fields)].append(row)
    return {
        "|".join(map(str, key)): summarize(bucket)
        for key, bucket in sorted(buckets.items())
    }


def behavioral_rows_equal(left: list[dict], right: list[dict]) -> bool:
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        keys = set(a) | set(b)
        if any(key != "elapsed_us" and a.get(key) != b.get(key) for key in keys):
            return False
    return True


def main() -> None:
    for required in (PROTOCOL, MANIFEST_SUMMARY, ROWS, AA_A, AA_B):
        if not required.exists():
            raise SystemExit(f"missing D41d artifact: {required}")
    manifest = json.loads(MANIFEST_SUMMARY.read_text())
    rows = read_rows(ROWS)
    aa_a = read_rows(AA_A)
    aa_b = read_rows(AA_B)
    if len(rows) != manifest["samples"] or len({row["sample_id"] for row in rows}) != len(rows):
        raise SystemExit("D41d result/manifest row mismatch")
    aa_exact = behavioral_rows_equal(aa_a, aa_b)
    full_subset_exact = behavioral_rows_equal(rows[: len(aa_a)], aa_a)
    integrity_failures = sum(
        row[field]
        for row in rows
        for field in (
            "baseline_invalid_direct_commands",
            "baseline_provenance_failures",
            "baseline_deposit_prediction_failures",
            "treatment_invalid_direct_commands",
            "treatment_provenance_failures",
            "treatment_deposit_prediction_failures",
        )
    )
    workforce_cap_failures = sum(
        row["baseline_own_workers"] > 3 or row["treatment_own_workers"] > 3
        for row in rows
    )
    by_cohort_rows = {
        cohort: [row for row in rows if row["cohort"] == cohort]
        for cohort in ("residual_top", "hash_control")
    }
    by_cohort = {cohort: summarize(bucket) for cohort, bucket in by_cohort_rows.items()}
    top = by_cohort["residual_top"]["margin_delta"]
    control = by_cohort["hash_control"]["margin_delta"]
    top_opponents = grouped(by_cohort_rows["residual_top"], ("opponent",))
    opponent_means = [bucket["margin_delta"]["mean"] for bucket in top_opponents.values()]
    overall_gates = {
        "at_least_256_top_samples": top["samples"] >= 256,
        "top_mean_at_least_3": top["mean"] >= 3,
        "top_normal_95_low_above_zero": top["normal_95_low"] > 0,
        "top_positive_rate_at_least_55pct": top["positive_rate"] >= 0.55,
        "top_advantage_over_control_at_least_3": top["mean"] - control["mean"] >= 3,
        "at_least_four_nonnegative_opponents": sum(value >= 0 for value in opponent_means) >= 4,
        "no_opponent_below_minus_15": min(opponent_means) >= -15,
        "integrity_and_replay": integrity_failures == 0
        and workforce_cap_failures == 0
        and aa_exact
        and full_subset_exact,
    }
    top_branches = grouped(by_cohort_rows["residual_top"], ("branch",))
    branch_gates = {}
    for branch, bucket in top_branches.items():
        stats = bucket["margin_delta"]
        gates = {
            "at_least_64_samples": stats["samples"] >= 64,
            "mean_at_least_5": stats["mean"] >= 5,
            "positive_rate_at_least_55pct": stats["positive_rate"] >= 0.55,
            "normal_95_low_above_zero": stats["normal_95_low"] > 0,
        }
        branch_gates[branch] = {"gates": gates, "pass": all(gates.values())}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "manifest_summary": str(MANIFEST_SUMMARY),
        "manifest_summary_sha256": sha256(MANIFEST_SUMMARY),
        "rows": str(ROWS),
        "rows_sha256": sha256(ROWS),
        "aa_a_sha256": sha256(AA_A),
        "aa_b_sha256": sha256(AA_B),
        "samples": len(rows),
        "aa_behavioral_exact": aa_exact,
        "full_subset_behavioral_exact": full_subset_exact,
        "integrity_failures": integrity_failures,
        "workforce_cap_failures": workforce_cap_failures,
        "by_cohort": by_cohort,
        "by_cohort_branch": grouped(rows, ("cohort", "branch")),
        "by_cohort_phase": grouped(rows, ("cohort", "phase")),
        "by_cohort_opponent": grouped(rows, ("cohort", "opponent")),
        "residual_top_branch": top_branches,
        "overall_gates": overall_gates,
        "overall_pass": all(overall_gates.values()),
        "branch_gates": branch_gates,
        "passing_branches": [
            branch for branch, result in branch_gates.items() if result["pass"]
        ],
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "overall_pass": report["overall_pass"],
                "overall_gates": overall_gates,
                "passing_branches": report["passing_branches"],
                "branch_gates": branch_gates,
                "by_cohort": by_cohort,
                "residual_top_branch": top_branches,
                "aa_behavioral_exact": aa_exact,
                "full_subset_behavioral_exact": full_subset_exact,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
