#!/usr/bin/env python3
"""Validate the frozen D61 renewable-safe batch-option population."""

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
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-protocol-2026-07-21.md"
)
AMENDMENT = ANALYSIS / "d61a-safe-balanced-anchor-amendment-2026-07-21.md"
POPULATION = ANALYSIS / "d61a-renewable-safe-batch-option-population.tsv"
RUN_A = (
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-corrected-a-9801000-9801007.tsv"
)
RUN_B = (
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-corrected-b-9801000-9801007.tsv"
)
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d61_batch_option_population.rs"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d61a_batch_option_population.py"
OUTPUT = ANALYSIS / "d61a-renewable-safe-batch-option-population-result.json"

EXPECTED_PROTOCOL_SHA256 = (
    "e8abefc987d3887f91af970aa44c2026927d9de1a86fa4b284aa19a3529580d2"
)
EXPECTED_AMENDMENT_SHA256 = (
    "3f03e6c7ec1bc527fdc5c914b925e4d66d21da5097ae18ad1117ad229a01413d"
)
EXPECTED_POPULATION_SHA256 = (
    "e7021ac2ef7e99a7f89dbe700473674f451c186e837d51046712036443790f5f"
)
EXPECTED_ENV_SOURCE_SHA256 = (
    "c53388b444ae010a6a298b6ccc32be63badf20bfe4f8b8aa78b38767108d5360"
)
EXPECTED_PRIOR_SOURCE_SHA256 = (
    "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
)
EXPECTED_RUNNER_SOURCE_SHA256 = (
    "fecc96da988436176e3ee35802deaef9ec5c4cdee0e6c9929422b28516a06ba5"
)
EXPECTED_GENERATOR_SOURCE_SHA256 = (
    "2dc776f972a3e239b7e201baf953378fa3e0529154ccdc2f8dc002f76f17b094"
)

MAP_START = 9_801_000
MAP_STOP = 9_801_008
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
CONTROL = "d40_control"
ANCHOR = "safe_balanced"
CONSTANTS = (ANCHOR, "safe_harvest", "safe_renew", "safe_fell")
LINEAR = tuple(f"linear_{index:02d}" for index in range(64))
CANDIDATES = (*CONSTANTS, *LINEAR)
ALL_POLICIES = (CONTROL, *CANDIDATES)
TASKS = (MAP_STOP - MAP_START) * 2 * len(OPPONENTS)
MODE_FIELDS = (
    "balanced_batches",
    "harvest_batches",
    "renew_batches",
    "fell_batches",
)
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
    "terminal_live_own_plants",
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


def mean(values: list[int] | list[float] | list[bool]) -> float:
    return float(statistics.mean(values))


def expected_kind(policy: str) -> str:
    if policy == CONTROL:
        return "control"
    if policy.startswith("safe_"):
        return policy.removeprefix("safe_")
    return "linear"


def validate_grid(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    if not fields or len(rows) != len(ALL_POLICIES) * TASKS:
        raise RuntimeError("D61 matrix schema or size mismatch")
    labels = Counter(row["policy"] for row in rows)
    if set(labels) != set(ALL_POLICIES) or any(
        count != TASKS for count in labels.values()
    ):
        raise RuntimeError("D61 policy coverage mismatch")
    tasks = expected_tasks()
    result: dict[str, dict[tuple[int, int, str], dict[str, str]]] = {}
    for policy in ALL_POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        keys = [task_key(row) for row in selected]
        if len(set(keys)) != len(keys) or set(keys) != tasks:
            raise RuntimeError(f"D61 task grid mismatch for {policy}")
        if any(row["kind"] != expected_kind(policy) for row in selected):
            raise RuntimeError(f"D61 kind mismatch for {policy}")
        result[policy] = {task_key(row): row for row in selected}
    return result


def row_integrity_failures(row: dict[str, str]) -> int:
    batches = int(row["option_batches"])
    mode_batches = sum(int(row[field]) for field in MODE_FIELDS)
    switches = int(row["mode_switches"])
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
        + int(mode_batches != batches)
        + int(int(row["feature_evaluations"]) != batches)
        + int(int(row["locked_batches"]) > batches)
        + int(switches > max(batches - 1, 0))
        + int(int(row["semantic_overrides"]) > int(row["selected_decisions"]))
        + int(int(row["semantic_eligible"]) > int(row["selected_decisions"]))
        + int(int(row["option_hash"]) == 0)
    )
    if row["policy"] == CONTROL:
        failures += (
            int(row["locked_batches"])
            + int(row["harvest_batches"])
            + int(row["renew_batches"])
            + int(row["fell_batches"])
            + int(row["mode_switches"])
            + int(row["safe_fell_rejections"])
            + int(row["semantic_eligible"])
            + int(row["semantic_overrides"])
            + int(int(row["balanced_batches"]) != batches)
        )
    return failures


def summarize_policy(
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
    mode_totals = {
        field.removesuffix("_batches"): sum(int(row[field]) for row in ordered)
        for field in MODE_FIELDS
    }
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
        "option_batches": sum(int(row["option_batches"]) for row in ordered),
        "locked_batches": sum(int(row["locked_batches"]) for row in ordered),
        "mode_batch_totals": mode_totals,
        "distinct_executed_modes": sum(value > 0 for value in mode_totals.values()),
        "tasks_with_mode_switch": sum(int(row["mode_switches"]) > 0 for row in ordered),
        "task_mode_switch_rate": mean(
            [int(row["mode_switches"]) > 0 for row in ordered]
        ),
        "mode_switches": sum(int(row["mode_switches"]) for row in ordered),
        "safe_fell_rejections": sum(
            int(row["safe_fell_rejections"]) for row in ordered
        ),
        "semantic_eligible": sum(int(row["semantic_eligible"]) for row in ordered),
        "semantic_overrides": sum(int(row["semantic_overrides"]) for row in ordered),
    }


def oracle_metrics(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]]
) -> dict:
    control = by_policy[CONTROL]
    selections: Counter[str] = Counter()
    strict_selections: Counter[str] = Counter()
    margin_deltas: list[int] = []
    own_deltas: list[int] = []
    opponent_deltas: list[int] = []
    family_deltas: dict[str, list[int]] = defaultdict(list)
    workers_three: list[bool] = []
    crops: list[bool] = []
    details = []
    for key in sorted(expected_tasks()):
        alternatives = [by_policy[policy][key] for policy in CANDIDATES]
        selected = min(
            alternatives,
            key=lambda row: (
                -int(row["margin"]),
                -int(row["own_score"]),
                int(row["opponent_score"]),
                row["policy"],
            ),
        )
        baseline = control[key]
        margin_delta = int(selected["margin"]) - int(baseline["margin"])
        own_delta = int(selected["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(selected["opponent_score"]) - int(
            baseline["opponent_score"]
        )
        selections[selected["policy"]] += 1
        if margin_delta > 0:
            strict_selections[selected["policy"]] += 1
        margin_deltas.append(margin_delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        family_deltas[key[2]].append(margin_delta)
        workers_three.append(int(selected["own_workers"]) >= 3)
        crops.append(int(selected["own_created_crops"]) > 0)
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "policy": selected["policy"],
                "margin_delta": margin_delta,
                "own_score_delta": own_delta,
                "opponent_score_delta": opponent_delta,
            }
        )
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    linear_strict = {
        policy: count
        for policy, count in strict_selections.items()
        if policy.startswith("linear_")
    }
    strict_total = sum(strict_selections.values())
    linear_total = sum(linear_strict.values())
    return {
        "tasks": len(details),
        "paired_mean_margin_delta": mean(margin_deltas),
        "paired_mean_own_score_delta": mean(own_deltas),
        "paired_mean_opponent_score_delta": mean(opponent_deltas),
        "strict_margin_improvements": sum(value > 0 for value in margin_deltas),
        "strict_margin_improvement_rate": mean(
            [value > 0 for value in margin_deltas]
        ),
        "ties": sum(value == 0 for value in margin_deltas),
        "selected_policy_counts": dict(sorted(selections.items())),
        "strict_selection_counts": dict(sorted(strict_selections.items())),
        "linear_policies_with_at_least_two_strict_selections": sum(
            count >= 2 for count in linear_strict.values()
        ),
        "linear_strict_selection_share": linear_total / strict_total
        if strict_total
        else 0.0,
        "opponent_family_mean_margin_deltas": family_means,
        "worst_opponent_family_mean_margin_delta": min(family_means.values()),
        "worker_three_rate": mean(workers_three),
        "crop_rate": mean(crops),
        "details": details,
    }


def gate_report(summaries: dict[str, dict], oracle: dict) -> tuple[dict, dict]:
    active = [
        policy
        for policy in CANDIDATES
        if summaries[policy]["changed_action_hash_rate"] >= 0.10
    ]
    override_totals = {
        mode: summaries[f"safe_{mode}"]["semantic_overrides"]
        for mode in ("harvest", "renew", "fell")
    }
    linear_three_modes = [
        policy
        for policy in LINEAR
        if summaries[policy]["distinct_executed_modes"] >= 3
    ]
    linear_switching = [
        policy
        for policy in LINEAR
        if summaries[policy]["task_mode_switch_rate"] >= 0.25
    ]
    candidate_means = [summaries[policy]["mean_margin"] for policy in CANDIDATES]
    surface = {
        "active_candidate_policies": active,
        "active_candidate_policy_count": len(active),
        "constant_semantic_override_totals": override_totals,
        "linear_policies_with_at_least_three_modes": linear_three_modes,
        "linear_policies_with_switches_in_at_least_25pct_tasks": linear_switching,
        "candidate_mean_margin_minimum": min(candidate_means),
        "candidate_mean_margin_maximum": max(candidate_means),
        "candidate_mean_margin_range": max(candidate_means) - min(candidate_means),
    }
    gates = {
        "all_69_policies_crop_in_all_tasks": all(
            summaries[policy]["crop_rate"] == 1.0 for policy in ALL_POLICIES
        ),
        "at_least_56_active_candidate_policies": len(active) >= 56,
        "all_semantic_modes_have_at_least_1000_overrides": all(
            count >= 1_000 for count in override_totals.values()
        ),
        "at_least_48_linear_policies_use_three_modes": len(linear_three_modes) >= 48,
        "at_least_48_linear_policies_switch_in_25pct_tasks": len(linear_switching)
        >= 48,
        "candidate_mean_margin_range_at_least_25": surface[
            "candidate_mean_margin_range"
        ]
        >= 25,
        "oracle_mean_margin_gain_at_least_30": oracle[
            "paired_mean_margin_delta"
        ]
        >= 30,
        "oracle_strictly_improves_at_least_60pct": oracle[
            "strict_margin_improvement_rate"
        ]
        >= 0.60,
        "all_opponent_oracle_gains_at_least_10": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 10,
        "at_least_12_linear_policies_have_two_strict_selections": oracle[
            "linear_policies_with_at_least_two_strict_selections"
        ]
        >= 12,
        "linear_policies_are_half_of_strict_oracle_selections": oracle[
            "linear_strict_selection_share"
        ]
        >= 0.50,
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
        "oracle_crop_rate_exactly_100pct": oracle["crop_rate"] == 1.0,
    }
    return surface, {name: bool(value) for name, value in gates.items()}


class D61AnalysisTests(unittest.TestCase):
    def test_policy_catalog_is_complete(self) -> None:
        self.assertEqual(len(ALL_POLICIES), 69)
        self.assertEqual(len(set(ALL_POLICIES)), 69)
        self.assertEqual(len(LINEAR), 64)

    def test_policy_kinds(self) -> None:
        self.assertEqual(expected_kind(CONTROL), "control")
        self.assertEqual(expected_kind("safe_fell"), "fell")
        self.assertEqual(expected_kind("linear_17"), "linear")


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (AMENDMENT, EXPECTED_AMENDMENT_SHA256),
        (POPULATION, EXPECTED_POPULATION_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
        (GENERATOR_SOURCE, EXPECTED_GENERATOR_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D61 prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D61 repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D61 result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D61 repeat matrices are not byte-identical")
    if fields_a != fields_b:
        raise RuntimeError("D61 repeat schemas differ")
    by_policy = validate_grid(rows_a, fields_a)

    parity_failures = []
    for key in sorted(expected_tasks()):
        control = by_policy[CONTROL][key]
        anchor = by_policy[ANCHOR][key]
        for field in PARITY_FIELDS:
            if control[field] != anchor[field]:
                parity_failures.append((key, field, control[field], anchor[field]))
    if parity_failures:
        raise RuntimeError(f"D61 anchor parity failure: {parity_failures[:3]}")

    integrity_failures = sum(row_integrity_failures(row) for row in rows_a)
    if integrity_failures:
        raise RuntimeError(f"D61 integrity failures: {integrity_failures}")

    control = by_policy[CONTROL]
    summaries = {
        policy: summarize_policy(by_policy[policy], control)
        for policy in ALL_POLICIES
    }
    oracle = oracle_metrics(by_policy)
    surface, substantive_gates = gate_report(summaries, oracle)
    gates = {
        "complete_byte_identical_69x128_repeats": True,
        "safe_balanced_exact_direct_d40_parity": not parity_failures,
        "zero_integrity_failures": integrity_failures == 0,
        **substantive_gates,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    best_fixed = max(
        CANDIDATES,
        key=lambda policy: (summaries[policy]["mean_margin"], policy),
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "amendment": str(AMENDMENT),
            "amendment_sha256": sha256(AMENDMENT),
            "population": str(POPULATION),
            "population_sha256": sha256(POPULATION),
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
        },
        "audit": {
            "policies": len(ALL_POLICIES),
            "tasks_per_policy": TASKS,
            "rows": len(rows_a),
            "repeat_byte_identical": True,
            "anchor_parity_failures": len(parity_failures),
            "integrity_failures": integrity_failures,
        },
        "summaries": summaries,
        "surface": surface,
        "best_fixed_policy_descriptive_only": {
            "policy": best_fixed,
            **summaries[best_fixed],
        },
        "oracle": oracle,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": (
            "crop-safe random-function-class upper bound only; no policy selection, "
            "PPO, candidate, TestSession, submission, or Arena action"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {**report["audit"], "gates": gates, "pass": report["pass"]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
