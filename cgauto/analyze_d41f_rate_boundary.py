#!/usr/bin/env python3
"""Analyze the frozen D41f early/late rate-boundary continuation study."""

from __future__ import annotations

import json
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d41d_one_deviation import (
    behavioral_rows_equal,
    grouped,
    read_rows,
    summarize,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41f-rate-boundary-one-deviation-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d41f-rate-boundary-manifest-2026-07-21.json"
ROWS = ANALYSIS / "d41f-rate-boundary-results-9772000-9772031.tsv"
AA_A = ANALYSIS / "d41f-rate-boundary-aa-a-96.tsv"
AA_B = ANALYSIS / "d41f-rate-boundary-aa-b-96.tsv"
OUTPUT = ANALYSIS / "d41f-rate-boundary-analysis-2026-07-21.json"
BIN_LOWERS = {
    "gap_100_200": 100,
    "gap_200_240": 200,
    "gap_240_260": 240,
    "gap_260_280": 260,
    "gap_280_300": 280,
    "gap_300_320": 300,
    "gap_320_340": 320,
}
THRESHOLDS = (100, 200, 240, 260, 280)


def individual_gate(summary: dict) -> dict:
    margin = summary["margin_delta"]
    gates = {
        "at_least_128_rows": margin["samples"] >= 128,
        "mean_at_least_5": margin["mean"] >= 5,
        "positive_rate_at_least_55pct": margin["positive_rate"] >= 0.55,
        "normal_95_low_above_zero": margin["normal_95_low"] > 0,
    }
    return {"gates": gates, "pass": all(gates.values())}


def threshold_gate(rows: list[dict], integrity: bool) -> dict:
    overall = summarize(rows)
    phases = grouped(rows, ("phase",))
    opponents = grouped(rows, ("opponent",))
    margin = overall["margin_delta"]
    opponent_means = [bucket["margin_delta"]["mean"] for bucket in opponents.values()]
    early = phases.get("early", {"margin_delta": {"mean": float("-inf")}})
    late = phases.get("late", {"margin_delta": {"mean": float("-inf")}})
    gates = {
        "at_least_384_rows": margin["samples"] >= 384,
        "mean_at_least_8": margin["mean"] >= 8,
        "normal_95_low_above_4": margin["normal_95_low"] > 4,
        "positive_rate_at_least_60pct": margin["positive_rate"] >= 0.60,
        "early_mean_at_least_8": early["margin_delta"]["mean"] >= 8,
        "late_mean_at_least_4": late["margin_delta"]["mean"] >= 4,
        "opponent_breadth": len(opponent_means) == 8
        and sum(value > 0 for value in opponent_means) >= 6
        and min(opponent_means) >= -10,
        "integrity_and_replay": integrity,
    }
    return {
        "summary": overall,
        "by_phase": phases,
        "by_opponent": opponents,
        "gates": gates,
        "pass": all(gates.values()),
    }


def analyze(rows: list[dict], aa_a: list[dict], aa_b: list[dict]) -> dict:
    aa_exact = behavioral_rows_equal(aa_a, aa_b)
    subset_exact = behavioral_rows_equal(rows[: len(aa_a)], aa_a)
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
    worker_cap_failures = sum(
        row["baseline_own_workers"] > 3 or row["treatment_own_workers"] > 3
        for row in rows
    )
    integrity = aa_exact and subset_exact and integrity_failures == 0 and worker_cap_failures == 0
    bin_rows = {
        bin_name: [row for row in rows if row["cohort"] == bin_name]
        for bin_name in BIN_LOWERS
    }
    by_bin = {bin_name: summarize(bucket) for bin_name, bucket in bin_rows.items()}
    individual = {
        bin_name: individual_gate(by_bin[bin_name]) for bin_name in BIN_LOWERS
    }
    thresholds = {}
    for threshold in THRESHOLDS:
        pooled = [row for row in rows if BIN_LOWERS[row["cohort"]] >= threshold]
        thresholds[str(threshold)] = threshold_gate(pooled, integrity)
    new_useful_bins = [
        bin_name
        for bin_name, lower in BIN_LOWERS.items()
        if lower < 280 and individual[bin_name]["pass"]
    ]
    qualifying = [
        threshold
        for threshold in THRESHOLDS
        if thresholds[str(threshold)]["pass"]
    ]
    selected = min(qualifying) if qualifying and new_useful_bins else None
    return {
        "samples": len(rows),
        "aa_behavioral_exact": aa_exact,
        "full_subset_behavioral_exact": subset_exact,
        "integrity_failures": integrity_failures,
        "worker_cap_failures": worker_cap_failures,
        "integrity_and_replay": integrity,
        "by_bin": by_bin,
        "by_bin_phase": grouped(rows, ("cohort", "phase")),
        "by_phase": grouped(rows, ("phase",)),
        "by_opponent": grouped(rows, ("opponent",)),
        "individual_bin_gates": individual,
        "new_useful_bins": new_useful_bins,
        "threshold_gates": thresholds,
        "selected_lower_threshold": selected,
        "pass": selected is not None,
    }


def main() -> None:
    for required in (PROTOCOL, MANIFEST, ROWS, AA_A, AA_B):
        if not required.exists():
            raise SystemExit(f"missing D41f artifact: {required}")
    manifest = json.loads(MANIFEST.read_text())
    rows = read_rows(ROWS)
    aa_a = read_rows(AA_A)
    aa_b = read_rows(AA_B)
    if len(rows) != manifest["samples"]:
        raise SystemExit("D41f manifest/result row mismatch")
    analysis = analyze(rows, aa_a, aa_b)
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "manifest": str(MANIFEST),
        "manifest_sha256": sha256(MANIFEST),
        "rows": str(ROWS),
        "rows_sha256": sha256(ROWS),
        "aa_a_sha256": sha256(AA_A),
        "aa_b_sha256": sha256(AA_B),
        "analysis": analysis,
        "scope": "D41f local one-deviation discovery only; no complete-policy or platform action",
    }
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D41f analysis")
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass": analysis["pass"],
                "new_useful_bins": analysis["new_useful_bins"],
                "selected_lower_threshold": analysis["selected_lower_threshold"],
                "individual_bin_gates": analysis["individual_bin_gates"],
                "threshold_gates": analysis["threshold_gates"],
                "integrity_and_replay": analysis["integrity_and_replay"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
