#!/usr/bin/env python3
"""Validate the frozen D96 factorized per-worker option population."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import make_d96a_factorized_worker_population as generator


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = (
    ANALYSIS
    / "d96a-factorized-worker-option-population-protocol-2026-07-21.md"
)
D61_POPULATION = ANALYSIS / "d61a-renewable-safe-batch-option-population.tsv"
D96_POPULATION = ANALYSIS / "d96a-factorized-worker-option-population.tsv"
D61_REFERENCE = (
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-corrected-a-9801000-9801007.tsv"
)
D61_REFERENCE_REPEAT = (
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-corrected-b-9801000-9801007.tsv"
)
RUN_A = (
    ANALYSIS
    / "d96a-factorized-worker-option-population-a-9801000-9801007.tsv"
)
RUN_B = (
    ANALYSIS
    / "d96a-factorized-worker-option-population-b-9801000-9801007.tsv"
)
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = (
    ROOT / "rust" / "src" / "bin" / "d96_factorized_worker_option_population.rs"
)
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d96a_factorized_worker_population.py"
OUTPUT = ANALYSIS / "d96a-factorized-worker-option-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "49a1469e58bee8519197e82b88b6c34a9416e89fa56563172b82faed743dd5c7",
    D61_POPULATION: "e7021ac2ef7e99a7f89dbe700473674f451c186e837d51046712036443790f5f",
    D96_POPULATION: "3fbe912c30bae723f6d5f27d323b2a7befac2c9758f75928a62c31e27144a900",
    D61_REFERENCE: "957f9d332cf0b1c15d1027b0a01250321f427eacb00da86a7d618f6da071e485",
    D61_REFERENCE_REPEAT: "957f9d332cf0b1c15d1027b0a01250321f427eacb00da86a7d618f6da071e485",
    ENV_SOURCE: "19d54cc89051c43a4a002c595b52a6403075581125d31e4fb152f6fb3cb70ede",
    PRIOR_SOURCE: "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62",
    RUNNER_SOURCE: "6e3b3c0ff75f9d4118e1243323e76467855882d1439fa99d890da14a4c296291",
    GENERATOR_SOURCE: "51c5a9c518d84e8bf685623590d696dd0aab33c2a661139f9d5276f9c762b459",
}

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
CONSTANTS = ("safe_balanced", "safe_harvest", "safe_renew", "safe_fell")
LINEAR = tuple(f"linear_{index:02d}" for index in range(64))
GLOBAL_OPTIONS = (*CONSTANTS, *LINEAR)
GLOBAL_POLICIES = (CONTROL, *GLOBAL_OPTIONS)
FACTOR_ZERO = tuple(f"factor_zero_{index:02d}" for index in range(64))
FACTOR_RANDOM = tuple(f"factor_random_{index:02d}" for index in range(64))
ALL_POLICIES = (*GLOBAL_POLICIES, *FACTOR_ZERO, *FACTOR_RANDOM)
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
ORDINAL_MODE_FIELDS = {
    ordinal: tuple(
        f"o{ordinal}_{mode}" for mode in ("balanced", "harvest", "renew", "fell")
    )
    for ordinal in range(3)
}
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
IDENTITY_FIELDS = {"map_seed", "seat", "opponent", "policy", "kind", "base_policy"}


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


def expected_kind(policy: str) -> str:
    if policy == CONTROL:
        return "control"
    if policy.startswith("safe_"):
        return policy.removeprefix("safe_")
    if policy.startswith("linear_"):
        return "linear"
    if policy.startswith("factor_zero_"):
        return "factor_zero"
    if policy.startswith("factor_random_"):
        return "factor_random"
    raise ValueError(f"unknown D96 policy: {policy}")


def expected_base(policy: str) -> str:
    if policy.startswith("factor_zero_"):
        return "linear_" + policy.removeprefix("factor_zero_")
    if policy.startswith("factor_random_"):
        return "linear_" + policy.removeprefix("factor_random_")
    return policy


def mean(values) -> float:
    return float(statistics.mean(values))


def validate_grid(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    expected_fields = {
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "kind",
        "base_policy",
        "margin",
        "own_score",
        "opponent_score",
        "own_workers",
        "own_created_crops",
        "action_hash",
        "worker_feature_evaluations",
        "worker_mode_switches",
        "multi_rate_batches",
        "mixed_rate_batches",
        "worker_option_hash",
        *MODE_FIELDS,
        *ACTION_PLANES,
        *(field for names in ORDINAL_MODE_FIELDS.values() for field in names),
    }
    if not expected_fields.issubset(fields):
        raise RuntimeError(f"D96 matrix missing fields: {sorted(expected_fields - set(fields))}")
    if len(rows) != len(ALL_POLICIES) * TASKS:
        raise RuntimeError(f"D96 matrix size mismatch: {len(rows)}")
    labels = Counter(row["policy"] for row in rows)
    if set(labels) != set(ALL_POLICIES) or any(count != TASKS for count in labels.values()):
        raise RuntimeError("D96 policy coverage mismatch")
    tasks = expected_tasks()
    result = {}
    for policy in ALL_POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        keys = [task_key(row) for row in selected]
        if len(set(keys)) != TASKS or set(keys) != tasks:
            raise RuntimeError(f"D96 task coverage mismatch for {policy}")
        if any(row["kind"] != expected_kind(policy) for row in selected):
            raise RuntimeError(f"D96 kind mismatch for {policy}")
        if any(row["base_policy"] != expected_base(policy) for row in selected):
            raise RuntimeError(f"D96 base mismatch for {policy}")
        result[policy] = {task_key(row): row for row in selected}
    expected_order = sorted(
        rows,
        key=lambda row: (
            row["policy"],
            int(row["map_seed"]),
            int(row["seat"]),
            OPPONENTS.index(row["opponent"]),
        ),
    )
    if rows != expected_order:
        raise RuntimeError("D96 rows are not in frozen deterministic order")
    return result


def validate_population() -> None:
    expected = generator.render(generator.population(D61_POPULATION))
    if D96_POPULATION.read_text() != expected:
        raise RuntimeError("D96 population does not reconstruct from the frozen generator")


def global_reference_failures(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]],
) -> list[tuple[str, tuple[int, int, str], str, str, str]]:
    rows, fields = read_table(D61_REFERENCE)
    reference = {(row["policy"], task_key(row)): row for row in rows}
    failures = []
    for policy in GLOBAL_POLICIES:
        for key in sorted(expected_tasks()):
            actual = by_policy[policy][key]
            expected = reference[(policy, key)]
            for field in fields:
                if actual[field] != expected[field]:
                    failures.append((policy, key, field, actual[field], expected[field]))
                    if len(failures) >= 20:
                        return failures
    return failures


def zero_parent_failures(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]],
    fields: list[str],
) -> list[tuple[str, tuple[int, int, str], str, str, str]]:
    parity_fields = [field for field in fields if field not in IDENTITY_FIELDS]
    failures = []
    for index, policy in enumerate(FACTOR_ZERO):
        parent = LINEAR[index]
        for key in sorted(expected_tasks()):
            actual = by_policy[policy][key]
            expected = by_policy[parent][key]
            for field in parity_fields:
                if actual[field] != expected[field]:
                    failures.append((policy, key, field, actual[field], expected[field]))
                    if len(failures) >= 20:
                        return failures
    return failures


def row_integrity_failures(row: dict[str, str]) -> list[str]:
    failures = []
    ints = {field: int(value) for field, value in row.items() if field not in FLOAT_FIELDS and field not in IDENTITY_FIELDS}
    floats = {field: float(row[field]) for field in FLOAT_FIELDS}
    if any(not math.isfinite(value) for value in floats.values()):
        failures.append("nonfinite_terminal_float")
    if ints["invalid_direct_commands"]:
        failures.append("invalid_direct_command")
    if ints["provenance_failures"]:
        failures.append("provenance_failure")
    if ints["deposit_prediction_failures"]:
        failures.append("deposit_prediction_failure")
    if ints["own_workers"] > 3:
        failures.append("worker_cap")
    if floats["reward_identity_error"] > 1.0e-4:
        failures.append("reward_identity")
    if ints["margin"] != ints["own_score"] - ints["opponent_score"]:
        failures.append("margin_identity")
    if sum(ints[field] for field in ACTION_PLANES) != ints["selected_decisions"]:
        failures.append("action_plane_accounting")
    if sum(ints[field] for field in MODE_FIELDS) != ints["option_batches"]:
        failures.append("batch_mode_accounting")
    if ints["feature_evaluations"] != ints["option_batches"]:
        failures.append("global_feature_accounting")
    if ints["locked_batches"] > ints["option_batches"]:
        failures.append("locked_batch_accounting")
    if ints["mode_switches"] > max(ints["option_batches"] - 1, 0):
        failures.append("global_switch_accounting")
    if ints["semantic_eligible"] > ints["selected_decisions"]:
        failures.append("semantic_eligible_accounting")
    if ints["semantic_overrides"] > ints["selected_decisions"]:
        failures.append("semantic_override_accounting")
    if ints["option_hash"] == 0 or ints["worker_option_hash"] == 0:
        failures.append("zero_option_hash")
    ordinal_total = sum(
        ints[field] for names in ORDINAL_MODE_FIELDS.values() for field in names
    )
    if ordinal_total != ints["worker_feature_evaluations"]:
        failures.append("worker_feature_accounting")
    if ints["mixed_rate_batches"] > ints["multi_rate_batches"]:
        failures.append("mixed_batch_accounting")
    if ints["multi_rate_batches"] > ints["option_batches"]:
        failures.append("multi_batch_accounting")
    if ints["worker_mode_switches"] > ints["worker_feature_evaluations"]:
        failures.append("worker_switch_accounting")
    if row["policy"] in (CONTROL, "safe_balanced"):
        if ordinal_total or ints["worker_feature_evaluations"] or ints["worker_mode_switches"]:
            failures.append("exact_anchor_worker_accounting")
    return failures


def summarize_policy(
    rows: dict[tuple[int, int, str], dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
    zero: dict[tuple[int, int, str], dict[str, str]] | None = None,
) -> dict:
    ordered = [rows[key] for key in sorted(rows)]
    margins = [int(row["margin"]) for row in ordered]
    modes = {
        mode: sum(
            int(row[f"o{ordinal}_{mode}"])
            for row in ordered
            for ordinal in range(3)
        )
        for mode in ("balanced", "harvest", "renew", "fell")
    }
    ordinal_modes = {
        str(ordinal): {
            mode: sum(int(row[f"o{ordinal}_{mode}"]) for row in ordered)
            for mode in ("balanced", "harvest", "renew", "fell")
        }
        for ordinal in range(3)
    }
    result = {
        "tasks": len(ordered),
        "mean_margin": mean(margins),
        "mean_own_score": mean([int(row["own_score"]) for row in ordered]),
        "mean_opponent_score": mean([int(row["opponent_score"]) for row in ordered]),
        "paired_mean_margin_delta_vs_d40": mean(
            [int(row["margin"]) - int(control[task_key(row)]["margin"]) for row in ordered]
        ),
        "worker_three_rate": mean([int(row["own_workers"]) >= 3 for row in ordered]),
        "crop_rate": mean([int(row["own_created_crops"]) > 0 for row in ordered]),
        "tasks_with_mixed_rate_batch": sum(int(row["mixed_rate_batches"]) > 0 for row in ordered),
        "mixed_rate_task_rate": mean([int(row["mixed_rate_batches"]) > 0 for row in ordered]),
        "mode_totals": modes,
        "distinct_modes": sum(value > 0 for value in modes.values()),
        "ordinal_mode_totals": ordinal_modes,
        "ordinal_zero_distinct_modes": sum(value > 0 for value in ordinal_modes["0"].values()),
        "ordinal_one_distinct_modes": sum(value > 0 for value in ordinal_modes["1"].values()),
        "worker_feature_evaluations": sum(int(row["worker_feature_evaluations"]) for row in ordered),
        "worker_mode_switches": sum(int(row["worker_mode_switches"]) for row in ordered),
        "multi_rate_batches": sum(int(row["multi_rate_batches"]) for row in ordered),
        "mixed_rate_batches": sum(int(row["mixed_rate_batches"]) for row in ordered),
    }
    if zero is not None:
        changed = sum(
            row["action_hash"] != zero[task_key(row)]["action_hash"] for row in ordered
        )
        result["changed_action_hash_tasks_vs_zero"] = changed
        result["changed_action_hash_rate_vs_zero"] = changed / len(ordered)
    return result


def select(rows: list[dict[str, str]]) -> dict[str, str]:
    return min(
        rows,
        key=lambda row: (
            -int(row["margin"]),
            -int(row["own_score"]),
            int(row["opponent_score"]),
            row["policy"],
        ),
    )


def oracle_metrics(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]]
) -> tuple[dict, dict]:
    control = by_policy[CONTROL]
    global_selections = Counter()
    factor_selections = Counter()
    factor_strict = Counter()
    factor_margin_deltas = []
    factor_own_deltas = []
    factor_opponent_deltas = []
    factor_family_deltas = defaultdict(list)
    factor_workers_three = []
    factor_crops = []
    global_margins = []
    factor_margins = []
    factor_beats_global = []
    details = []
    for key in sorted(expected_tasks()):
        baseline = control[key]
        global_row = select([by_policy[policy][key] for policy in GLOBAL_OPTIONS])
        factor_row = select([baseline, *[by_policy[policy][key] for policy in FACTOR_RANDOM]])
        margin_delta = int(factor_row["margin"]) - int(baseline["margin"])
        own_delta = int(factor_row["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(factor_row["opponent_score"]) - int(baseline["opponent_score"])
        global_selections[global_row["policy"]] += 1
        factor_selections[factor_row["policy"]] += 1
        if factor_row["policy"] != CONTROL and margin_delta > 0:
            factor_strict[factor_row["policy"]] += 1
        factor_margin_deltas.append(margin_delta)
        factor_own_deltas.append(own_delta)
        factor_opponent_deltas.append(opponent_delta)
        factor_family_deltas[key[2]].append(margin_delta)
        factor_workers_three.append(int(factor_row["own_workers"]) >= 3)
        factor_crops.append(int(factor_row["own_created_crops"]) > 0)
        global_margins.append(int(global_row["margin"]))
        factor_margins.append(int(factor_row["margin"]))
        beats = int(factor_row["margin"]) > int(global_row["margin"])
        factor_beats_global.append(beats)
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "d40_margin": int(baseline["margin"]),
                "global_policy": global_row["policy"],
                "global_margin": int(global_row["margin"]),
                "factor_policy": factor_row["policy"],
                "factor_margin": int(factor_row["margin"]),
                "factor_margin_delta_vs_d40": margin_delta,
                "factor_strictly_beats_global_margin": beats,
            }
        )
    family_means = {
        opponent: mean(factor_family_deltas[opponent]) for opponent in OPPONENTS
    }
    metrics = {
        "tasks": TASKS,
        "global_oracle_mean_margin": mean(global_margins),
        "factor_oracle_mean_margin": mean(factor_margins),
        "factor_minus_global_mean_margin": mean(factor_margins) - mean(global_margins),
        "factor_paired_mean_margin_delta_vs_d40": mean(factor_margin_deltas),
        "factor_paired_mean_own_score_delta_vs_d40": mean(factor_own_deltas),
        "factor_paired_mean_opponent_score_delta_vs_d40": mean(factor_opponent_deltas),
        "factor_strict_margin_improvements_vs_d40": sum(value > 0 for value in factor_margin_deltas),
        "factor_strict_margin_improvement_rate_vs_d40": mean([value > 0 for value in factor_margin_deltas]),
        "factor_opponent_family_mean_margin_deltas_vs_d40": family_means,
        "factor_worst_opponent_family_mean_margin_delta_vs_d40": min(family_means.values()),
        "factor_worker_three_rate": mean(factor_workers_three),
        "factor_crop_rate": mean(factor_crops),
        "factor_strictly_beats_global_margin_tasks": sum(factor_beats_global),
        "global_selected_policy_counts": dict(sorted(global_selections.items())),
        "factor_selected_policy_counts": dict(sorted(factor_selections.items())),
        "factor_strict_winner_counts": dict(sorted(factor_strict.items())),
        "random_factor_policies_with_two_strict_wins": sum(
            factor_strict[policy] >= 2 for policy in FACTOR_RANDOM
        ),
    }
    return metrics, {"tasks": details}


def main() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D96 prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D96 repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D96 result")
    validate_population()
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D96 repeat matrices are not byte-identical")

    rows, fields = read_table(RUN_A)
    repeat_rows, repeat_fields = read_table(RUN_B)
    if fields != repeat_fields or rows != repeat_rows:
        raise RuntimeError("D96 repeat schemas or parsed matrices differ")
    by_policy = validate_grid(rows, fields)
    reference_failures = global_reference_failures(by_policy)
    zero_failures = zero_parent_failures(by_policy, fields)
    integrity = Counter()
    for row in rows:
        integrity.update(row_integrity_failures(row))

    control = by_policy[CONTROL]
    summaries = {
        policy: summarize_policy(
            by_policy[policy],
            control,
            by_policy[FACTOR_ZERO[index]],
        )
        for index, policy in enumerate(FACTOR_RANDOM)
    }
    d40_worker_three = mean(
        [int(row["own_workers"]) >= 3 for row in control.values()]
    )
    retained_worker_three = [
        policy
        for policy in FACTOR_RANDOM
        if summaries[policy]["worker_three_rate"] >= d40_worker_three - 0.10
    ]
    active = [
        policy
        for policy in FACTOR_RANDOM
        if summaries[policy]["changed_action_hash_rate_vs_zero"] >= 0.10
    ]
    three_modes = [
        policy for policy in FACTOR_RANDOM if summaries[policy]["distinct_modes"] >= 3
    ]
    mixed = [
        policy
        for policy in FACTOR_RANDOM
        if summaries[policy]["mixed_rate_task_rate"] >= 0.25
    ]
    two_ordinals = [
        policy
        for policy in FACTOR_RANDOM
        if summaries[policy]["ordinal_zero_distinct_modes"] >= 2
        and summaries[policy]["ordinal_one_distinct_modes"] >= 2
    ]
    fixed_means = [summaries[policy]["mean_margin"] for policy in FACTOR_RANDOM]
    surface = {
        "d40_worker_three_rate": d40_worker_three,
        "random_policies_retaining_worker_three": retained_worker_three,
        "random_policies_retaining_worker_three_count": len(retained_worker_three),
        "active_random_policies": active,
        "active_random_policy_count": len(active),
        "random_policies_with_at_least_three_modes": three_modes,
        "random_policies_with_at_least_three_modes_count": len(three_modes),
        "random_policies_mixed_in_at_least_25pct_tasks": mixed,
        "random_policies_mixed_in_at_least_25pct_tasks_count": len(mixed),
        "random_policies_using_two_modes_for_ordinals_zero_and_one": two_ordinals,
        "random_policies_using_two_modes_for_ordinals_zero_and_one_count": len(two_ordinals),
        "random_fixed_mean_margin_minimum": min(fixed_means),
        "random_fixed_mean_margin_maximum": max(fixed_means),
        "random_fixed_mean_margin_range": max(fixed_means) - min(fixed_means),
    }
    oracle, oracle_details = oracle_metrics(by_policy)
    gates = {
        "complete_byte_identical_197x128_repeats": True,
        "all_69_global_policies_reproduce_d61": not reference_failures,
        "all_64_zero_residuals_reproduce_parent": not zero_failures,
        "population_reconstructs_exactly": True,
        "zero_integrity_failures": not integrity,
        "all_random_policies_crop_in_all_tasks": all(
            summaries[policy]["crop_rate"] == 1.0 for policy in FACTOR_RANDOM
        ),
        "at_least_48_random_policies_retain_worker_three": len(retained_worker_three) >= 48,
        "at_least_56_random_policies_change_10pct_actions": len(active) >= 56,
        "at_least_48_random_policies_request_three_modes": len(three_modes) >= 48,
        "at_least_48_random_policies_mix_25pct_tasks": len(mixed) >= 48,
        "at_least_48_random_policies_use_two_modes_for_ordinals_zero_and_one": len(two_ordinals) >= 48,
        "random_fixed_mean_margin_range_at_least_25": surface["random_fixed_mean_margin_range"] >= 25,
        "factor_oracle_mean_margin_gain_at_least_50": oracle["factor_paired_mean_margin_delta_vs_d40"] >= 50,
        "factor_oracle_strictly_improves_at_least_85pct": oracle["factor_strict_margin_improvement_rate_vs_d40"] >= 0.85,
        "all_factor_oracle_opponent_gains_at_least_15": oracle["factor_worst_opponent_family_mean_margin_delta_vs_d40"] >= 15,
        "factor_oracle_mean_own_score_nonnegative": oracle["factor_paired_mean_own_score_delta_vs_d40"] >= 0,
        "factor_oracle_mean_opponent_score_nonpositive": oracle["factor_paired_mean_opponent_score_delta_vs_d40"] <= 0,
        "factor_oracle_worker_three_rate_at_least_85pct": oracle["factor_worker_three_rate"] >= 0.85,
        "factor_oracle_crop_rate_exactly_100pct": oracle["factor_crop_rate"] == 1.0,
        "factor_oracle_at_least_5_above_global": oracle["factor_minus_global_mean_margin"] >= 5,
        "factor_strictly_beats_global_in_at_least_24_tasks": oracle["factor_strictly_beats_global_margin_tasks"] >= 24,
        "at_least_12_random_factor_policies_have_two_strict_wins": oracle["random_factor_policies_with_two_strict_wins"] >= 12,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    best_fixed = max(FACTOR_RANDOM, key=lambda policy: (summaries[policy]["mean_margin"], policy))
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "d61_population": str(D61_POPULATION),
            "d61_population_sha256": sha256(D61_POPULATION),
            "d96_population": str(D96_POPULATION),
            "d96_population_sha256": sha256(D96_POPULATION),
            "d61_reference": str(D61_REFERENCE),
            "d61_reference_sha256": sha256(D61_REFERENCE),
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
            "analyzer_source_sha256": sha256(Path(__file__)),
        },
        "audit": {
            "policies": len(ALL_POLICIES),
            "global_policies": len(GLOBAL_POLICIES),
            "zero_factor_policies": len(FACTOR_ZERO),
            "random_factor_policies": len(FACTOR_RANDOM),
            "tasks_per_policy": TASKS,
            "rows": len(rows),
            "repeat_byte_identical": True,
            "global_reference_failures": len(reference_failures),
            "zero_parent_failures": len(zero_failures),
            "integrity_failure_counts": dict(sorted(integrity.items())),
        },
        "surface": surface,
        "random_policy_summaries": summaries,
        "best_fixed_random_policy_descriptive_only": {
            "policy": best_fixed,
            **summaries[best_fixed],
        },
        "oracle": oracle,
        "oracle_details": oracle_details,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": (
            "consumed-map factorized-function-class upper bound only; no random policy "
            "selection, learner, candidate, TestSession, submission, or Arena action"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**report["audit"], "surface": surface, "oracle": oracle, "gates": gates, "pass": report["pass"]}, sort_keys=True))


if __name__ == "__main__":
    main()
