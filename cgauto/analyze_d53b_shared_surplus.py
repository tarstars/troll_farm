#!/usr/bin/env python3
"""Validate the frozen D53b shared-surplus oversubscription diagnostic."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.analyze_d52b_train_transaction import KINDS, TARGETS, partition_exact
from cgauto.analyze_d53a_atomic_train_reservation import MODELS


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d53b-shared-surplus-oversubscription-diagnostic-protocol-2026-07-21.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "field_continuation_audit.rs"
STRATEGY = ROOT / "rust" / "src" / "strategies" / "legend_field_proxy.rs"
OBSERVED = ANALYSIS / "field-continuation-phase21-candidate-160-observed.json"
MAPS = ANALYSIS / "field-continuation-phase21-candidate-160.maps"
D53A = ANALYSIS / "d53a-atomic-train-a-phase21-local.tsv"
RUN = ANALYSIS / "d53b-shared-surplus-diagnostic-phase21-local.tsv"
OUTPUT = ANALYSIS / "d53b-shared-surplus-diagnostic-result.json"

EXPECTED_SHA256 = {
    PROTOCOL: "50ed0f24c79698188059aea5c734c6d5f6fa0cf6f486080fae0b18d326737e90",
    RUNNER: "6f5cda853088b756a02e1c6c17ec5029e6a217e845512b219d10a5f70c0b1df0",
    STRATEGY: "cf5cdb1df23033f88f465a8213d47b4291137c916d539f8861ba040f4363062a",
    OBSERVED: "c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc",
    MAPS: "d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0",
    D53A: "d378288dd24b992a027583ae6270fbff358311f34b8da666a5241880347c021b",
}

NEW_FIELDS = (
    "failed_currency_picks",
    "fail_with_multiple_currency_picks",
    "fail_with_oversubscribed_resource",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def oversubscription_gates(
    *,
    common_mismatches: int,
    partition_failures: int,
    budget_failures: int,
    failed_currency_picks: int,
    multi_pick_failures: int,
    oversubscribed_failures: int,
) -> dict[str, bool]:
    return {
        "all_preexisting_fields_match_d53a": common_mismatches == 0,
        "all_attempt_partitions_exact": partition_failures == 0,
        "binding_budget_failures_are_present": budget_failures > 0,
        "every_binding_budget_failure_has_multiple_currency_picks": (
            multi_pick_failures == budget_failures
            and failed_currency_picks >= 2 * budget_failures
        ),
        "every_binding_budget_failure_oversubscribes_a_resource": (
            oversubscribed_failures == budget_failures
        ),
    }


def main() -> None:
    for path, expected in EXPECTED_SHA256.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D53b prerequisite missing or changed: {path}")
    if not RUN.exists():
        raise SystemExit("missing D53b diagnostic matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D53b result")

    baseline = read_rows(D53A)
    diagnostic = read_rows(RUN)
    if len(baseline) != 1_280 or len(diagnostic) != 1_280:
        raise ValueError("D53b matrices are not exact 160 x 8")
    identities = {(row["game_id"], row["model"]) for row in diagnostic}
    if len(identities) != 1_280 or {row["model"] for row in diagnostic} != set(MODELS):
        raise ValueError("D53b diagnostic identities are incomplete or duplicated")
    baseline_by_identity = {
        (row["game_id"], row["model"]): row for row in baseline
    }
    common_mismatches = 0
    partition_failures = 0
    by_target = {
        str(target): {
            **{kind: 0 for kind in KINDS},
            **{field: 0 for field in NEW_FIELDS},
        }
        for target in TARGETS
    }
    for row in diagnostic:
        old = baseline_by_identity.get((row["game_id"], row["model"]))
        common_mismatches += old is None or any(
            row.get(field) != value for field, value in old.items()
        )
        for target in TARGETS:
            existing = {
                kind: int(row[f"train{target}_{kind}"])
                for kind in KINDS
            }
            partition_failures += not partition_exact(existing)
            for kind, value in existing.items():
                by_target[str(target)][kind] += value
            for field in NEW_FIELDS:
                by_target[str(target)][field] += int(
                    row[f"train{target}_{field}"]
                )

    binding = (by_target["3"], by_target["4"])
    budget_failures = sum(
        values["fail_budget_only"] + values["fail_both"] for values in binding
    )
    failed_currency_picks = sum(
        values["failed_currency_picks"] for values in binding
    )
    multi_pick_failures = sum(
        values["fail_with_multiple_currency_picks"] for values in binding
    )
    oversubscribed_failures = sum(
        values["fail_with_oversubscribed_resource"] for values in binding
    )
    gates = oversubscription_gates(
        common_mismatches=common_mismatches,
        partition_failures=partition_failures,
        budget_failures=budget_failures,
        failed_currency_picks=failed_currency_picks,
        multi_pick_failures=multi_pick_failures,
        oversubscribed_failures=oversubscribed_failures,
    )
    report = {
        "schema": 1,
        "scope": (
            "shared-surplus transaction telemetry only on consumed maps; score, support, distance, "
            "cohort, opponent, candidate-value, and platform fields ignored"
        ),
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d53a_sha256": sha256(D53A),
            "diagnostic_sha256": sha256(RUN),
            "observed_sha256": sha256(OBSERVED),
            "maps_sha256": sha256(MAPS),
            "runner_sha256": sha256(RUNNER),
            "strategy_sha256": sha256(STRATEGY),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "integrity": {
            "exact_160_by_8_grid": len(identities) == 1_280,
            "common_field_mismatches": common_mismatches,
            "attempt_partition_failures": partition_failures,
        },
        "by_target": by_target,
        "binding_worker_three_four": {
            "budget_failures": budget_failures,
            "failed_currency_picks": failed_currency_picks,
            "failures_with_multiple_currency_picks": multi_pick_failures,
            "failures_with_oversubscribed_resource": oversubscribed_failures,
        },
        "gates": gates,
        "pass": all(gates.values()),
        "decision": (
            "authorize D54 shared per-turn PICK-surplus ledger as the sole treatment"
            if all(gates.values())
            else "freeze a turn-level command/state trace before changing allocation"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
