#!/usr/bin/env python3
"""Analyze the frozen prospective D64a late-capitalization matrix."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d64a-field-gated-late-capitalization-protocol-2026-07-21.md"
MODEL = ANALYSIS / "d64a-field-snapshot-model-2026-07-21.json"
RUNNER = REPO / "rust/src/bin/d64_field_gated_capitalization.rs"
GENERATED_MODEL = REPO / "rust/src/d64a_snapshot_model_generated.rs"
START_SEED = 9_830_000
MAPS = 16
POLICIES = (
    "d40_control",
    "never_late_scale",
    "field_snapshot_gate",
    "inverse_snapshot_gate",
)
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
ACTION_FIELDS = (
    "train_none",
    "train_producer",
    "train_chopper",
    "idle",
    "bank",
    "fell_bank",
    "harvest_bank",
    "renew",
    "mine_bank",
)
DECISION_SHARED_FIELDS = (
    "eligible",
    "decision_turn",
    "decision_state_hash",
    "model_logit",
    "model_probability",
    "rms_z",
    "within_support",
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "finite_feature_failures",
    "model_parity_failures",
)


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return (int(row["map_seed"]), int(row["seat"]), row["opponent"])


def mean(values: list[float | int | bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def read_matrix(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        fields = reader.fieldnames or []
    return rows, fields


def expected_task_keys() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAPS)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }


def index_rows(rows: list[dict[str, str]]) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    indexed = {policy: {} for policy in POLICIES}
    for row in rows:
        policy = row["policy"]
        if policy not in indexed:
            raise ValueError(f"unexpected D64 policy {policy}")
        key = task_key(row)
        if key in indexed[policy]:
            raise ValueError(f"duplicate D64 row {policy} {key}")
        indexed[policy][key] = row
    expected = expected_task_keys()
    for policy in POLICIES:
        if set(indexed[policy]) != expected:
            raise ValueError(f"incomplete D64 task grid for {policy}")
    return indexed


def numeric(row: dict[str, str], field: str) -> float:
    return float(row[field])


def summarize(rows: list[dict[str, str]]) -> dict:
    return {
        "tasks": len(rows),
        "mean_own_score": mean([int(row["own_score"]) for row in rows]),
        "mean_opponent_score": mean([int(row["opponent_score"]) for row in rows]),
        "mean_margin": mean([int(row["margin"]) for row in rows]),
        "catastrophic_losses": sum(int(row["margin"]) <= -100 for row in rows),
        "worker_three_rate": mean([int(row["own_workers"]) >= 3 for row in rows]),
        "crop_rate": mean([int(row["own_created_crops"]) > 0 for row in rows]),
        "mean_overrides": mean([int(row["overrides"]) for row in rows]),
    }


def paired_delta(
    left: dict[tuple[int, int, str], dict[str, str]],
    right: dict[tuple[int, int, str], dict[str, str]],
    keys: list[tuple[int, int, str]],
) -> dict:
    fields = ("own_score", "opponent_score", "margin")
    result = {
        f"mean_{field}_delta": mean(
            [int(left[key][field]) - int(right[key][field]) for key in keys]
        )
        for field in fields
    }
    result.update(
        {
            "tasks": len(keys),
            "strict_margin_improvements": sum(
                int(left[key]["margin"]) > int(right[key]["margin"]) for key in keys
            ),
            "strict_margin_regressions": sum(
                int(left[key]["margin"]) < int(right[key]["margin"]) for key in keys
            ),
            "changed_action_hashes": sum(
                left[key]["action_hash"] != right[key]["action_hash"] for key in keys
            ),
            "catastrophic_delta": sum(
                int(left[key]["margin"]) <= -100 for key in keys
            )
            - sum(int(right[key]["margin"]) <= -100 for key in keys),
        }
    )
    return result


def oracle_report(indexed: dict[str, dict], eligible: list[tuple[int, int, str]]) -> dict:
    control = indexed["d40_control"]
    suppress = indexed["never_late_scale"]
    field = indexed["field_snapshot_gate"]
    selections = Counter()
    gains = []
    strict = 0
    agreements = 0
    for key in eligible:
        scale = control[key]
        no_scale = suppress[key]
        scale_key = (
            int(scale["margin"]),
            int(scale["own_score"]),
            -int(scale["opponent_score"]),
            1,
        )
        suppress_key = (
            int(no_scale["margin"]),
            int(no_scale["own_score"]),
            -int(no_scale["opponent_score"]),
            0,
        )
        selected_policy, selected = (
            ("d40_control", scale)
            if scale_key >= suppress_key
            else ("never_late_scale", no_scale)
        )
        selections[selected_policy] += 1
        gain = int(selected["margin"]) - int(scale["margin"])
        gains.append(gain)
        strict += int(gain > 0)
        expected_action = "scale" if selected_policy == "d40_control" else "suppress"
        agreements += int(field[key]["latched_action"] == expected_action)
    return {
        "tasks": len(eligible),
        "selection_counts": dict(sorted(selections.items())),
        "mean_margin_gain_vs_d40": mean(gains),
        "strict_margin_improvements": strict,
        "strict_improvement_rate": strict / len(eligible) if eligible else 0.0,
        "field_selector_agreements": agreements,
        "field_selector_agreement_rate": agreements / len(eligible) if eligible else 0.0,
    }


def validate_integrity(
    rows: list[dict[str, str]], fields: list[str], indexed: dict[str, dict]
) -> tuple[dict, list[tuple[int, int, str]]]:
    expected_rows = len(POLICIES) * MAPS * 2 * len(OPPONENTS)
    required = {
        "map_seed",
        "split",
        "seat",
        "opponent",
        "policy",
        "margin",
        "eligible",
        "latched_action",
        *ACTION_FIELDS,
        *DECISION_SHARED_FIELDS,
        *FAILURE_FIELDS,
    }
    if not required.issubset(fields):
        raise ValueError(f"D64 header missing {sorted(required - set(fields))}")
    keys = sorted(expected_task_keys())
    eligible = [key for key in keys if indexed["d40_control"][key]["eligible"] == "1"]
    shared_mismatches = 0
    ineligible_terminal_mismatches = 0
    latch_mismatches = 0
    for key in keys:
        task_rows = [indexed[policy][key] for policy in POLICIES]
        for field in DECISION_SHARED_FIELDS:
            shared_mismatches += int(len({row[field] for row in task_rows}) != 1)
        if task_rows[0]["eligible"] == "0":
            comparable = [
                {name: value for name, value in row.items() if name != "policy"}
                for row in task_rows
            ]
            ineligible_terminal_mismatches += int(
                any(row != comparable[0] for row in comparable[1:])
            )
        else:
            probability = float(task_rows[0]["model_probability"])
            expected = {
                "d40_control": "scale",
                "never_late_scale": "suppress",
                "field_snapshot_gate": "scale" if probability >= 0.5 else "suppress",
                "inverse_snapshot_gate": "suppress" if probability >= 0.5 else "scale",
            }
            latch_mismatches += sum(
                indexed[policy][key]["latched_action"] != expected[policy]
                for policy in POLICIES
            )
    failure_total = sum(
        int(row[field]) for row in rows for field in FAILURE_FIELDS
    )
    action_accounting_failures = sum(
        sum(int(row[field]) for field in ACTION_FIELDS) != int(row["selected_decisions"])
        for row in rows
    )
    nonfinite_model_values = sum(
        not all(
            math.isfinite(float(row[field]))
            for field in ("model_logit", "model_probability", "rms_z")
        )
        for row in rows
        if row["eligible"] == "1"
    )
    reward_identity_failures = sum(
        float(row["reward_identity_error"]) >= 1e-4 for row in rows
    )
    worker_cap_failures = sum(
        int(row["max_workers"]) > 3 or int(row["own_workers"]) > 3 for row in rows
    )
    split_failures = sum(
        row["split"]
        != ("development" if int(row["map_seed"]) < START_SEED + 8 else "validation")
        for row in rows
    )
    return (
        {
            "rows": len(rows),
            "expected_rows": expected_rows,
            "complete_grid": len(rows) == expected_rows,
            "shared_decision_mismatches": shared_mismatches,
            "ineligible_terminal_mismatches": ineligible_terminal_mismatches,
            "latch_mismatches": latch_mismatches,
            "mechanical_failure_total": failure_total,
            "action_accounting_failures": action_accounting_failures,
            "nonfinite_model_values": nonfinite_model_values,
            "reward_identity_failures": reward_identity_failures,
            "worker_cap_failures": worker_cap_failures,
            "split_failures": split_failures,
        },
        eligible,
    )


def build_report(
    matrix_a: Path,
    matrix_b: Path,
    rows: list[dict[str, str]],
    fields: list[str],
) -> dict:
    indexed = index_rows(rows)
    integrity, eligible = validate_integrity(rows, fields, indexed)
    repeat_identical = matrix_a.read_bytes() == matrix_b.read_bytes()
    integrity["repeat_byte_identical"] = repeat_identical
    keys = sorted(expected_task_keys())
    development = [key for key in keys if key[0] < START_SEED + 8]
    validation = [key for key in keys if key[0] >= START_SEED + 8]
    eligible_development = [key for key in eligible if key in set(development)]
    eligible_validation = [key for key in eligible if key in set(validation)]
    field = indexed["field_snapshot_gate"]
    control = indexed["d40_control"]
    inverse = indexed["inverse_snapshot_gate"]
    never = indexed["never_late_scale"]
    field_actions = Counter(field[key]["latched_action"] for key in eligible)
    field_actions_by_block = {
        "development": Counter(field[key]["latched_action"] for key in eligible_development),
        "validation": Counter(field[key]["latched_action"] for key in eligible_validation),
    }
    support = {
        "eligible_tasks": len(eligible),
        "eligible_development": len(eligible_development),
        "eligible_validation": len(eligible_validation),
        "field_actions": dict(sorted(field_actions.items())),
        "field_actions_by_block": {
            block: dict(sorted(counts.items()))
            for block, counts in field_actions_by_block.items()
        },
        "within_field_radius": sum(field[key]["within_support"] == "1" for key in eligible),
        "within_field_radius_rate": mean(
            [field[key]["within_support"] == "1" for key in eligible]
        ),
        "rms_z": {
            "minimum": min((float(field[key]["rms_z"]) for key in eligible), default=None),
            "median": (
                sorted(float(field[key]["rms_z"]) for key in eligible)[len(eligible) // 2]
                if eligible
                else None
            ),
            "maximum": max((float(field[key]["rms_z"]) for key in eligible), default=None),
        },
    }
    comparisons = {
        "field_vs_d40": {
            "all": paired_delta(field, control, keys),
            "eligible": paired_delta(field, control, eligible),
            "eligible_development": paired_delta(field, control, eligible_development),
            "eligible_validation": paired_delta(field, control, eligible_validation),
            "by_opponent": {
                opponent: paired_delta(
                    field, control, [key for key in keys if key[2] == opponent]
                )
                for opponent in OPPONENTS
            },
        },
        "field_vs_never": {
            "eligible": paired_delta(field, never, eligible),
        },
        "field_vs_inverse": {
            "eligible": paired_delta(field, inverse, eligible),
        },
        "never_vs_d40": {
            "eligible": paired_delta(never, control, eligible),
        },
    }
    oracle = oracle_report(indexed, eligible)
    field_gain = comparisons["field_vs_d40"]["eligible"]["mean_margin_delta"]
    oracle_gain = oracle["mean_margin_gain_vs_d40"]
    oracle["field_captured_gain_fraction"] = (
        field_gain / oracle_gain if oracle_gain > 0 else 0.0
    )
    summaries = {
        policy: {
            "all": summarize(list(indexed[policy].values())),
            "eligible": summarize([indexed[policy][key] for key in eligible]),
        }
        for policy in POLICIES
    }

    integrity_checks = {
        "repeat_matrix_byte_identical": repeat_identical,
        "complete_4x256_grid": integrity["complete_grid"],
        "shared_decision_metadata_exact": integrity["shared_decision_mismatches"] == 0,
        "ineligible_tasks_terminally_identical": integrity[
            "ineligible_terminal_mismatches"
        ]
        == 0,
        "latched_actions_match_frozen_rules": integrity["latch_mismatches"] == 0,
        "zero_mechanical_failures": integrity["mechanical_failure_total"] == 0,
        "zero_action_accounting_failures": integrity["action_accounting_failures"] == 0,
        "finite_model_values": integrity["nonfinite_model_values"] == 0,
        "reward_identity_below_1e_4": integrity["reward_identity_failures"] == 0,
        "worker_cap_respected": integrity["worker_cap_failures"] == 0,
        "split_exact": integrity["split_failures"] == 0,
    }
    field_all = summaries["field_snapshot_gate"]["all"]
    safety_checks = {
        "field_crop_rate_exactly_1": field_all["crop_rate"] == 1.0,
        "field_worker_two_rate_exactly_1": all(
            int(field[key]["own_workers"]) >= 2 for key in keys
        ),
        "field_never_exceeds_three_workers": all(
            int(field[key]["max_workers"]) <= 3 for key in keys
        ),
    }
    activity_checks = {
        "eligible_at_least_32_and_12_per_block": len(eligible) >= 32
        and len(eligible_development) >= 12
        and len(eligible_validation) >= 12,
        "both_actions_at_least_8_overall_3_per_block": min(
            field_actions.get("scale", 0), field_actions.get("suppress", 0)
        )
        >= 8
        and all(
            min(counts.get("scale", 0), counts.get("suppress", 0)) >= 3
            for counts in field_actions_by_block.values()
        ),
        "changes_at_least_8_vs_each_pure_arm": comparisons["field_vs_d40"][
            "eligible"
        ]["changed_action_hashes"]
        >= 8
        and comparisons["field_vs_never"]["eligible"]["changed_action_hashes"] >= 8,
        "at_least_half_within_field_radius": support["within_field_radius_rate"] >= 0.5,
    }
    headroom_checks = {
        "oracle_gain_at_least_5": oracle_gain >= 5.0,
        "oracle_strict_improvement_rate_at_least_20pct": oracle[
            "strict_improvement_rate"
        ]
        >= 0.20,
    }
    field_vs_control_all = comparisons["field_vs_d40"]["all"]
    field_vs_control_eligible = comparisons["field_vs_d40"]["eligible"]
    value_checks = {
        "eligible_field_gain_at_least_2": field_gain >= 2.0,
        "captures_at_least_25pct_oracle_gain": oracle[
            "field_captured_gain_fraction"
        ]
        >= 0.25,
        "beats_inverse_by_at_least_2": comparisons["field_vs_inverse"]["eligible"][
            "mean_margin_delta"
        ]
        >= 2.0,
        "eligible_validation_delta_nonnegative": comparisons["field_vs_d40"][
            "eligible_validation"
        ]["mean_margin_delta"]
        >= 0.0,
        "all_task_margin_nonnegative": field_vs_control_all["mean_margin_delta"] >= 0.0,
        "all_task_own_delta_at_least_minus_2": field_vs_control_all[
            "mean_own_score_delta"
        ]
        >= -2.0,
        "all_task_opponent_delta_at_most_2": field_vs_control_all[
            "mean_opponent_score_delta"
        ]
        <= 2.0,
        "worst_opponent_margin_delta_at_least_minus_5": min(
            report["mean_margin_delta"]
            for report in comparisons["field_vs_d40"]["by_opponent"].values()
        )
        >= -5.0,
        "catastrophes_do_not_increase_all_or_validation": field_vs_control_all[
            "catastrophic_delta"
        ]
        <= 0
        and comparisons["field_vs_d40"]["eligible_validation"][
            "catastrophic_delta"
        ]
        <= 0,
    }
    if not all(integrity_checks.values()) or not all(safety_checks.values()):
        status = "invalid"
        next_experiment = "repair_violated_invariant_only"
    elif not all(activity_checks.values()):
        status = "insufficient"
        next_experiment = "field_like_role_conditioned_or_recurrent_representation"
    elif all(headroom_checks.values()) and all(value_checks.values()):
        status = "pass"
        next_experiment = "submission_capable_capitalization_integration"
    elif all(headroom_checks.values()):
        status = "fail"
        next_experiment = "narrow_capitalization_boundary_monte_carlo_value_target"
    else:
        status = "fail"
        next_experiment = "close_late_scale_vs_suppress_on_d40"
    return {
        "schema": "troll-farm-d64a-field-gated-late-capitalization-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "fresh-seed exact local causal intervention; no platform or candidate claim",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "snapshot_model": sha256_file(MODEL),
            "runner": sha256_file(RUNNER),
            "generated_rust_model": sha256_file(GENERATED_MODEL),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": integrity,
        "support": support,
        "summaries": summaries,
        "comparisons": comparisons,
        "oracle": oracle,
        "gates": {
            "integrity": integrity_checks,
            "safety": safety_checks,
            "support_activity": activity_checks,
            "action_headroom": headroom_checks,
            "selector_value": value_checks,
            "status": status,
        },
        "decision": {
            "next_experiment": next_experiment,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(matrix_a: Path, matrix_b: Path, output: Path) -> dict:
    if matrix_a.read_bytes() != matrix_b.read_bytes():
        raise ValueError("D64 repeated matrices are not byte-identical")
    rows, fields = read_matrix(matrix_a)
    report = build_report(matrix_a, matrix_b, rows, fields)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix_a", type=Path)
    parser.add_argument("matrix_b", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.matrix_a, args.matrix_b, args.output)
    print(
        json.dumps(
            {
                "status": report["gates"]["status"],
                "eligible": report["support"]["eligible_tasks"],
                "field_actions": report["support"]["field_actions"],
                "oracle_gain": report["oracle"]["mean_margin_gain_vs_d40"],
                "field_gain": report["comparisons"]["field_vs_d40"]["eligible"][
                    "mean_margin_delta"
                ],
                "next": report["decision"]["next_experiment"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

