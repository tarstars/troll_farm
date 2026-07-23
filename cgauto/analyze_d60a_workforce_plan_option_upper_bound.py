#!/usr/bin/env python3
"""Validate and summarize the frozen D60 workforce-plan option upper bound."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = (
    ANALYSIS / "d60a-workforce-plan-option-upper-bound-protocol-2026-07-21.md"
)
RUN_A = (
    ANALYSIS
    / "d60a-workforce-plan-option-upper-bound-a-9800000-9800015.tsv"
)
RUN_B = (
    ANALYSIS
    / "d60a-workforce-plan-option-upper-bound-b-9800000-9800015.tsv"
)
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d60_plan_option_upper_bound.rs"
OUTPUT = ANALYSIS / "d60a-workforce-plan-option-upper-bound-result.json"

EXPECTED_PROTOCOL_SHA256 = (
    "5e204108ca6fef181aa16e5b8479895815564eac75c517853c34fb18e83497b9"
)
EXPECTED_ENV_SOURCE_SHA256 = (
    "c53388b444ae010a6a298b6ccc32be63badf20bfe4f8b8aa78b38767108d5360"
)
EXPECTED_PRIOR_SOURCE_SHA256 = (
    "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
)
EXPECTED_RUNNER_SOURCE_SHA256 = (
    "b6031b1f809b95cdc4a69597b908a8efefcb7504750ca165dd3cd3834ec86dad"
)

MAP_START = 9_800_000
MAP_STOP = 9_800_016
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
MODES = ("balanced", "harvest", "renew", "fell")
CONTROL = "d40_control"
ANCHOR = "pre3_balanced__post3_balanced"
PLAN_LABELS = tuple(
    f"pre3_{pre3}__post3_{post3}" for pre3 in MODES for post3 in MODES
)
ALL_LABELS = (CONTROL, *PLAN_LABELS)
TASKS = (MAP_STOP - MAP_START) * 2 * len(OPPONENTS)
ACTION_PLANES = (
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
PARITY_FIELDS = (
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "selected_decisions",
    "selected_jobs",
    "selected_nonidle_jobs",
    "selected_renew_jobs",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "action_hash",
    "state_hash",
    "pre3_rate",
    "pre3_eligible",
    "pre3_overrides",
    "post3_rate",
    "post3_eligible",
    "post3_overrides",
    *ACTION_PLANES,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def mean(values: list[int] | list[float]) -> float:
    return float(statistics.mean(values))


def modes_from_label(label: str) -> tuple[str, str]:
    if label == CONTROL:
        return "balanced", "balanced"
    left, right = label.split("__")
    return left.removeprefix("pre3_"), right.removeprefix("post3_")


def validate_grid(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    if not fields or len(rows) != len(ALL_LABELS) * TASKS:
        raise RuntimeError("D60 matrix schema or size mismatch")
    labels = Counter(row["plan"] for row in rows)
    if set(labels) != set(ALL_LABELS) or any(count != TASKS for count in labels.values()):
        raise RuntimeError("D60 plan coverage mismatch")
    result: dict[str, dict[tuple[int, int, str], dict[str, str]]] = {}
    tasks = expected_tasks()
    for label in ALL_LABELS:
        selected = [row for row in rows if row["plan"] == label]
        keys = [task_key(row) for row in selected]
        if len(set(keys)) != len(keys) or set(keys) != tasks:
            raise RuntimeError(f"D60 task grid mismatch for {label}")
        pre3, post3 = modes_from_label(label)
        if any(
            row["pre3_mode"] != pre3 or row["post3_mode"] != post3
            for row in selected
        ):
            raise RuntimeError(f"D60 mode-label mismatch for {label}")
        result[label] = {task_key(row): row for row in selected}
    return result


def row_integrity_failures(row: dict[str, str]) -> int:
    failures = (
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(int(row["own_workers"]) > 3)
        + int(float(row["reward_identity_error"]) > 1.0e-4)
        + int(int(row["margin"]) != int(row["own_score"]) - int(row["opponent_score"]))
        + int(
            sum(int(row[field]) for field in ACTION_PLANES)
            != int(row["selected_decisions"])
        )
    )
    for phase in ("pre3", "post3"):
        rate = int(row[f"{phase}_rate"])
        eligible = int(row[f"{phase}_eligible"])
        overrides = int(row[f"{phase}_overrides"])
        failures += int(eligible > rate) + int(overrides > eligible)
        if row[f"{phase}_mode"] == "balanced":
            failures += eligible + overrides
    if row["plan"] == CONTROL:
        failures += int(row["pre3_eligible"]) + int(row["pre3_overrides"])
        failures += int(row["post3_eligible"]) + int(row["post3_overrides"])
    return failures


def summarize_plan(
    rows: dict[tuple[int, int, str], dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    ordered = [rows[key] for key in sorted(rows)]
    margin_deltas = [
        int(row["margin"]) - int(control[task_key(row)]["margin"])
        for row in ordered
    ]
    own_deltas = [
        int(row["own_score"]) - int(control[task_key(row)]["own_score"])
        for row in ordered
    ]
    opponent_deltas = [
        int(row["opponent_score"])
        - int(control[task_key(row)]["opponent_score"])
        for row in ordered
    ]
    changed = sum(
        row["action_hash"] != control[task_key(row)]["action_hash"] for row in ordered
    )
    return {
        "tasks": len(ordered),
        "mean_margin": mean([int(row["margin"]) for row in ordered]),
        "mean_own_score": mean([int(row["own_score"]) for row in ordered]),
        "mean_opponent_score": mean(
            [int(row["opponent_score"]) for row in ordered]
        ),
        "paired_mean_margin_delta": mean(margin_deltas),
        "paired_mean_own_score_delta": mean(own_deltas),
        "paired_mean_opponent_score_delta": mean(opponent_deltas),
        "strict_margin_improvements": sum(value > 0 for value in margin_deltas),
        "strict_margin_regressions": sum(value < 0 for value in margin_deltas),
        "changed_action_hash_tasks": changed,
        "changed_action_hash_rate": changed / len(ordered),
        "worker_two_rate": mean([int(row["own_workers"]) >= 2 for row in ordered]),
        "worker_three_rate": mean(
            [int(row["own_workers"]) >= 3 for row in ordered]
        ),
        "crop_rate": mean(
            [int(row["own_created_crops"]) > 0 for row in ordered]
        ),
        "pre3_rate_decisions": sum(int(row["pre3_rate"]) for row in ordered),
        "pre3_eligible_decisions": sum(
            int(row["pre3_eligible"]) for row in ordered
        ),
        "pre3_overrides": sum(int(row["pre3_overrides"]) for row in ordered),
        "post3_rate_decisions": sum(int(row["post3_rate"]) for row in ordered),
        "post3_eligible_decisions": sum(
            int(row["post3_eligible"]) for row in ordered
        ),
        "post3_overrides": sum(int(row["post3_overrides"]) for row in ordered),
    }


def oracle_metrics(
    by_plan: dict[str, dict[tuple[int, int, str], dict[str, str]]]
) -> dict:
    control = by_plan[CONTROL]
    selections: Counter[str] = Counter()
    strict_gain_selections: Counter[str] = Counter()
    margin_deltas: list[int] = []
    own_deltas: list[int] = []
    opponent_deltas: list[int] = []
    family_deltas: dict[str, list[int]] = defaultdict(list)
    worker_three: list[bool] = []
    crops: list[bool] = []
    rows: list[dict] = []
    for key in sorted(expected_tasks()):
        alternatives = [by_plan[label][key] for label in PLAN_LABELS]
        selected = min(
            alternatives,
            key=lambda row: (
                -int(row["margin"]),
                -int(row["own_score"]),
                int(row["opponent_score"]),
                row["plan"],
            ),
        )
        baseline = control[key]
        margin_delta = int(selected["margin"]) - int(baseline["margin"])
        own_delta = int(selected["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(selected["opponent_score"]) - int(
            baseline["opponent_score"]
        )
        selections[selected["plan"]] += 1
        if selected["plan"] != ANCHOR and margin_delta > 0:
            strict_gain_selections[selected["plan"]] += 1
        margin_deltas.append(margin_delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        family_deltas[key[2]].append(margin_delta)
        worker_three.append(int(selected["own_workers"]) >= 3)
        crops.append(int(selected["own_created_crops"]) > 0)
        rows.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "plan": selected["plan"],
                "margin_delta": margin_delta,
                "own_score_delta": own_delta,
                "opponent_score_delta": opponent_delta,
            }
        )
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    return {
        "tasks": len(rows),
        "paired_mean_margin_delta": mean(margin_deltas),
        "paired_mean_own_score_delta": mean(own_deltas),
        "paired_mean_opponent_score_delta": mean(opponent_deltas),
        "strict_margin_improvements": sum(value > 0 for value in margin_deltas),
        "strict_margin_improvement_rate": mean(
            [value > 0 for value in margin_deltas]
        ),
        "ties": sum(value == 0 for value in margin_deltas),
        "selected_plan_counts": dict(sorted(selections.items())),
        "strict_gain_selection_counts": dict(
            sorted(strict_gain_selections.items())
        ),
        "nonanchor_plans_with_at_least_four_strict_gains": sum(
            count >= 4 for count in strict_gain_selections.values()
        ),
        "opponent_family_mean_margin_deltas": family_means,
        "worst_opponent_family_mean_margin_delta": min(family_means.values()),
        "worker_three_rate": mean(worker_three),
        "crop_rate": mean(crops),
        "details": rows,
    }


def gate_report(summaries: dict[str, dict], oracle: dict) -> tuple[dict, dict]:
    nonanchors = [label for label in PLAN_LABELS if label != ANCHOR]
    active = [
        label
        for label in nonanchors
        if summaries[label]["changed_action_hash_rate"] >= 0.10
    ]
    semantic_overrides = {}
    for mode in MODES[1:]:
        semantic_overrides[mode] = {
            "pre3": sum(
                summaries[label]["pre3_overrides"]
                for label in PLAN_LABELS
                if modes_from_label(label)[0] == mode
            ),
            "post3": sum(
                summaries[label]["post3_overrides"]
                for label in PLAN_LABELS
                if modes_from_label(label)[1] == mode
            ),
        }
    plan_means = [summaries[label]["mean_margin"] for label in nonanchors]
    surface = {
        "active_nonanchor_plans": active,
        "active_nonanchor_plan_count": len(active),
        "semantic_overrides": semantic_overrides,
        "nonanchor_mean_margin_minimum": min(plan_means),
        "nonanchor_mean_margin_maximum": max(plan_means),
        "nonanchor_mean_margin_range": max(plan_means) - min(plan_means),
    }
    gates = {
        "at_least_12_active_nonanchor_plans": len(active) >= 12,
        "all_semantic_modes_override_in_both_phases": all(
            counts[phase] > 0
            for counts in semantic_overrides.values()
            for phase in ("pre3", "post3")
        ),
        "nonanchor_mean_margin_range_at_least_25": surface[
            "nonanchor_mean_margin_range"
        ]
        >= 25,
        "oracle_mean_margin_gain_at_least_20": oracle[
            "paired_mean_margin_delta"
        ]
        >= 20,
        "oracle_strictly_improves_at_least_30pct": oracle[
            "strict_margin_improvement_rate"
        ]
        >= 0.30,
        "all_opponent_oracle_gains_at_least_8": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 8,
        "at_least_four_nonanchor_plans_have_four_strict_gains": oracle[
            "nonanchor_plans_with_at_least_four_strict_gains"
        ]
        >= 4,
        "oracle_mean_own_score_nonnegative": oracle[
            "paired_mean_own_score_delta"
        ]
        >= 0,
        "oracle_mean_opponent_score_nonpositive": oracle[
            "paired_mean_opponent_score_delta"
        ]
        <= 0,
        "oracle_worker_three_rate_at_least_85pct": oracle["worker_three_rate"]
        >= 0.85,
        "oracle_crop_rate_at_least_95pct": oracle["crop_rate"] >= 0.95,
    }
    return surface, {name: bool(value) for name, value in gates.items()}


class D60AnalysisTests(unittest.TestCase):
    def test_modes_round_trip(self) -> None:
        for pre3 in MODES:
            for post3 in MODES:
                label = f"pre3_{pre3}__post3_{post3}"
                self.assertEqual(modes_from_label(label), (pre3, post3))
        self.assertEqual(modes_from_label(CONTROL), ("balanced", "balanced"))

    def test_plan_catalog_is_complete(self) -> None:
        self.assertEqual(len(PLAN_LABELS), 16)
        self.assertEqual(len(set(PLAN_LABELS)), 16)
        self.assertIn(ANCHOR, PLAN_LABELS)


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D60 prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D60 repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D60 result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D60 repeat matrices are not byte-identical")
    if fields_a != fields_b:
        raise RuntimeError("D60 repeat schemas differ")
    by_plan = validate_grid(rows_a, fields_a)

    parity_failures = []
    for key in sorted(expected_tasks()):
        control = by_plan[CONTROL][key]
        anchor = by_plan[ANCHOR][key]
        for field in PARITY_FIELDS:
            if control[field] != anchor[field]:
                parity_failures.append((key, field, control[field], anchor[field]))
    if parity_failures:
        raise RuntimeError(f"D60 anchor parity failure: {parity_failures[:3]}")

    integrity_failures = sum(row_integrity_failures(row) for row in rows_a)
    if integrity_failures:
        raise RuntimeError(f"D60 integrity failures: {integrity_failures}")

    control = by_plan[CONTROL]
    summaries = {
        label: summarize_plan(by_plan[label], control) for label in ALL_LABELS
    }
    oracle = oracle_metrics(by_plan)
    surface, substantive_gates = gate_report(summaries, oracle)
    gates = {
        "complete_byte_identical_17x256_repeats": True,
        "balanced_anchor_exact_direct_d40_parity": not parity_failures,
        "zero_integrity_failures": integrity_failures == 0,
        **substantive_gates,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    best_fixed = max(
        PLAN_LABELS,
        key=lambda label: (summaries[label]["mean_margin"], label),
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
        },
        "audit": {
            "plans": len(ALL_LABELS),
            "tasks_per_plan": TASKS,
            "rows": len(rows_a),
            "repeat_byte_identical": True,
            "anchor_parity_failures": len(parity_failures),
            "integrity_failures": integrity_failures,
        },
        "summaries": summaries,
        "surface": surface,
        "best_fixed_plan_descriptive_only": {
            "plan": best_fixed,
            **summaries[best_fixed],
        },
        "oracle": oracle,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": (
            "representation upper bound only; no plan selection, candidate, "
            "TestSession, submission, or Arena action"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**report["audit"], "gates": gates, "pass": report["pass"]}, sort_keys=True))


if __name__ == "__main__":
    main()
