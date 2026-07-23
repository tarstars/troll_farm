#!/usr/bin/env python3
"""Validate and summarize the frozen D52b TRAIN transaction diagnostic."""

from __future__ import annotations

from collections import defaultdict
import csv
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d52a_hybrid_job_market import MODELS


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d52b-train-transaction-diagnostic-protocol-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
D52A = ANALYSIS / "d52a-hybrid-job-market-a-phase21-local.tsv"
RUN = ANALYSIS / "d52b-train-transaction-diagnostic-phase21-local.tsv"
OUTPUT = ANALYSIS / "d52b-train-transaction-diagnostic-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "d7fd21f6fa3a3107792d82079d5f88dcd757d1c8862611c784b2614ddd81ad7e",
    RUNNER: "6df3732778f97663e830a84b407c92694477576fdd4c46196d9ba54bc01a622e",
    STRATEGY: "d13dea27b559e531d7fc53dc316768d2cb30e91e1064dd46f46c2e05fb645b78",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    D52A: "47686b28222e92793414c7d50cb437c3e7d779f7f4f8b8bdf85a0ec0c2c66bae",
}

TARGETS = (2, 3, 4)
KINDS = (
    "attempts",
    "successes",
    "fail_shack_only",
    "fail_budget_only",
    "fail_both",
    "fail_other",
)
TELEMETRY_FIELDS = tuple(
    f"train{target}_{kind}" for target in TARGETS for kind in KINDS
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def target_summary(values: dict[str, int]) -> dict:
    attempts = values["attempts"]
    successes = values["successes"]
    failures = attempts - successes
    shack = values["fail_shack_only"] + values["fail_both"]
    budget = values["fail_budget_only"] + values["fail_both"]
    explained_union = failures - values["fail_other"]
    return {
        **values,
        "failures": failures,
        "success_rate": successes / attempts if attempts else None,
        "shack_inclusive": shack,
        "shack_inclusive_failure_rate": shack / failures if failures else None,
        "budget_inclusive": budget,
        "budget_inclusive_failure_rate": budget / failures if failures else None,
        "explained_union": explained_union,
        "explained_union_failure_rate": explained_union / failures if failures else None,
        "unexplained_failure_rate": values["fail_other"] / failures
        if failures
        else None,
    }


def partition_exact(values: dict[str, int]) -> bool:
    return values["attempts"] == values["successes"] + sum(
        values[kind]
        for kind in (
            "fail_shack_only",
            "fail_budget_only",
            "fail_both",
            "fail_other",
        )
    )


def repair_decision(pooled: dict) -> str:
    if not pooled["failures"]:
        return "no failed worker-three/four TRAIN attempts; do not infer a repair"
    if pooled["unexplained_failure_rate"] > 0.20:
        return "freeze a turn-level trace before scheduler repair"
    shack = pooled["shack_inclusive_failure_rate"] >= 0.80
    budget = pooled["budget_inclusive_failure_rate"] >= 0.80
    if shack and budget:
        return "require atomic spawn evacuation and exact bill reservation"
    if shack:
        return "require atomic spawn evacuation"
    if budget:
        return "require exact bill reservation through higher-priority actions"
    if pooled["explained_union_failure_rate"] >= 0.80:
        return "require atomic spawn evacuation and exact bill reservation"
    return "freeze a turn-level trace before scheduler repair"


def main() -> None:
    if "PLACEHOLDER" in EXPECTED_SHA256[RUNNER]:
        raise SystemExit("D52b analyzer runner hash was not frozen")
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D52b prerequisite missing or changed: {path}")
    if not RUN.exists():
        raise SystemExit("missing D52b diagnostic matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D52b result")

    baseline = read_rows(D52A)
    diagnostic = read_rows(RUN)
    if len(baseline) != 1_280 or len(diagnostic) != 1_280:
        raise ValueError("D52b matrices are not exact 160 x 8")
    identities = {(row["game_id"], row["model"]) for row in diagnostic}
    if len(identities) != 1_280 or {row["model"] for row in diagnostic} != set(MODELS):
        raise ValueError("D52b diagnostic identities are incomplete or duplicated")
    baseline_by_identity = {
        (row["game_id"], row["model"]): row for row in baseline
    }
    common_mismatches = []
    for row in diagnostic:
        old = baseline_by_identity.get((row["game_id"], row["model"]))
        if old is None or any(row.get(field) != value for field, value in old.items()):
            common_mismatches.append((row["game_id"], row["model"]))

    by_target = {
        target: {kind: 0 for kind in KINDS}
        for target in TARGETS
    }
    by_model_target = {
        model: {
            target: {kind: 0 for kind in KINDS}
            for target in TARGETS
        }
        for model in MODELS
    }
    row_partition_failures = []
    for row in diagnostic:
        for target in TARGETS:
            values = {
                kind: int(row[f"train{target}_{kind}"])
                for kind in KINDS
            }
            if not partition_exact(values):
                row_partition_failures.append(
                    (row["game_id"], row["model"], target)
                )
            for kind, value in values.items():
                by_target[target][kind] += value
                by_model_target[row["model"]][target][kind] += value

    pooled_values = {
        kind: by_target[3][kind] + by_target[4][kind]
        for kind in KINDS
    }
    pooled = target_summary(pooled_values)
    integrity = {
        "exact_160_by_8_grid": len(identities) == 1_280,
        "all_preexisting_fields_match_d52a": not common_mismatches,
        "all_attempt_partitions_exact": not row_partition_failures
        and all(partition_exact(values) for values in by_target.values()),
    }
    report = {
        "schema": 1,
        "scope": (
            "TRAIN transaction telemetry only on consumed maps; all score, coverage, cohort, "
            "opponent, support, candidate-value, and platform fields ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d52a_sha256": sha256(D52A),
            "diagnostic_sha256": sha256(RUN),
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "runner_sha256": sha256(RUNNER),
            "strategy_sha256": sha256(STRATEGY),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "integrity": {
            **integrity,
            "common_field_mismatches": len(common_mismatches),
            "row_partition_failures": len(row_partition_failures),
        },
        "by_target": {
            str(target): target_summary(values)
            for target, values in by_target.items()
        },
        "by_model_target": {
            model: {
                str(target): target_summary(values)
                for target, values in targets.items()
            }
            for model, targets in by_model_target.items()
        },
        "pooled_worker_three_four": pooled,
        "pass": all(integrity.values()),
        "decision": repair_decision(pooled)
        if all(integrity.values())
        else "diagnostic integrity failed; do not infer a scheduler repair",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
