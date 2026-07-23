#!/usr/bin/env python3
"""Validate the frozen D100 D98-anchored pair-residual population."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import make_d100a_anchored_pair_residual_population as generator


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d100a-d98-anchored-pair-residual-protocol-2026-07-22.md"
POPULATION_LOCK = ANALYSIS / "d100a-d98-anchored-pair-residual-population-lock-2026-07-22.md"
IMPLEMENTATION_LOCK = (
    ANALYSIS / "d100a-d98-anchored-pair-residual-implementation-lock-2026-07-22.md"
)
POPULATION = ANALYSIS / "d100a-d98-anchored-pair-residual-population.tsv"
RUN_A = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-population-a-9823000-9823007.tsv"
)
RUN_B = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-population-b-9823000-9823007.tsv"
)
BASELINES_A = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-baselines-a-9823000-9823007.tsv"
)
BASELINES_B = (
    ANALYSIS
    / "d100a-d98-anchored-pair-residual-baselines-b-9823000-9823007.tsv"
)
D98_POPULATION = ANALYSIS / "d98a-bounded-whole-game-joint-assignment-population.tsv"
D98_REFERENCE = ANALYSIS / "d100a-d98-reference-population-9823000-9823007.tsv"
D98_BASELINES = ANALYSIS / "d100a-d98-reference-baselines-9823000-9823007.tsv"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d100a_anchored_pair_residual_population.py"
EVALUATOR_SOURCE = (
    ROOT / "rust" / "src" / "bin" / "d100_anchored_pair_residual_population.rs"
)
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
D100_BINARY = (
    ROOT / "rust" / "target" / "release" / "d100_anchored_pair_residual_population"
)
D98_BINARY = (
    ROOT / "rust" / "target" / "release" / "d98_bounded_joint_assignment_population"
)
OUTPUT = ANALYSIS / "d100a-d98-anchored-pair-residual-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "1180aab70fb6220d82778f3caf4758d8e03dd90faef8c8166c3230555c9995b9",
    POPULATION_LOCK: "2abb732a5fb4283600241f7d6936cdfa89bda6598ed102e24223ebe8db2b6cb6",
    IMPLEMENTATION_LOCK: "c8a7e220d3ce4ee5ae39fe52f596de79a1d49666c8bf940cd402cb2944e386d6",
    POPULATION: "a3524fc945667edf63c548c5400453bf75e1264529cf139e67bb236da92e5b95",
    D98_POPULATION: "3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e",
    GENERATOR_SOURCE: "a8344776a91ce532e523b10b84ddf3277869c9f259fe81a78e513cff1a51f1d8",
    EVALUATOR_SOURCE: "1e262d68dcda93bf0b6a8ce14272cb5c492274ae20aa8645b915e1d82c1a7447",
    ENV_SOURCE: "1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5",
    PRIOR_SOURCE: "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62",
    D100_BINARY: "3f1f2a3e2917d01a8c4d8b63525320e112e57eaa6711d403dc458303fdcf2b92",
    D98_BINARY: "1e660c8c4615b646f0cc3a190746b2af0e821dea309a34f748f88901249493eb",
}

MAP_START = 9_823_000
MAP_STOP = 9_823_008
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
PARENTS = tuple(f"parent_{index:02d}" for index in range(64))
ZEROS = tuple(f"zero_{index:02d}" for index in range(64))
RANDOMS = tuple(f"random_{index:02d}" for index in range(64))
POLICIES = (CONTROL, *PARENTS, *ZEROS, *RANDOMS)
D98_ZERO = "zero_control"
D98_ONES = tuple(f"one_{index:02d}" for index in range(64))
D98_FOURS = tuple(f"four_{index:02d}" for index in range(64))
D98_POLICIES = (D98_ZERO, *D98_ONES, *D98_FOURS)
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
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
TERMINAL_FIELDS = (
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    *FLOAT_FIELDS,
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
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
    "terminal_live_own_plants",
    *ACTION_PLANES,
)
OVERRIDE_JOB_FIELDS = (
    "override_fell",
    "override_harvest",
    "override_renew",
    "override_mine",
)
OVERRIDE_OWNER_FIELDS = (
    "override_owner_natural",
    "override_owner_own",
    "override_owner_opponent",
    "override_owner_ambiguous",
)
D100_STAT_FIELDS = (
    "option_batches",
    "eligible_pair_batches",
    "scored_assignments",
    "intervention_batches",
    "nonkeep_assignments",
    "joint_batches",
    "max_scored_per_batch",
    "residual_pair_evaluations",
    "residual_overrides",
    "residual_joint_overrides",
    "max_committed_actions",
    "safety_rejections",
    "pair_options",
    "single_first_options",
    "single_second_options",
    "joint_options",
    "override_control",
    "override_single_first",
    "override_single_second",
    "preview_validations",
    *OVERRIDE_JOB_FIELDS,
    *OVERRIDE_OWNER_FIELDS,
    "pair_hash",
    "parent_hash",
    "residual_hash",
)
D98_JOB_FIELDS = (
    "concrete_fell",
    "concrete_harvest",
    "concrete_renew",
    "concrete_mine",
)
D98_OWNER_FIELDS = (
    "owner_natural",
    "owner_own",
    "owner_opponent",
    "owner_ambiguous",
)
D98_STAT_FIELDS = (
    "option_batches",
    "eligible_batches",
    "scored_assignments",
    "intervention_batches",
    "nonkeep_assignments",
    "joint_batches",
    "max_scored_per_batch",
    "safety_rejections",
    "catalog_options",
    *D98_JOB_FIELDS,
    *D98_OWNER_FIELDS,
    "option_hash",
    "policy_hash",
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


def mean(values) -> float:
    return float(statistics.mean(values))


def expected_metadata(policy: str) -> tuple[str, str, int, int]:
    if policy == CONTROL:
        return "control", "none", 0, 0
    index = int(policy[-2:])
    parent = f"four_{index:02d}"
    if policy.startswith("parent_"):
        return "parent", parent, 4, 0
    if policy.startswith("zero_"):
        return "zero_residual", parent, 4, 1
    return "random_residual", parent, 4, 1


def validate_population() -> dict:
    generated = generator.population()
    generator.validate(generated)
    expected = generator.render(generated)
    if POPULATION.read_text() != expected:
        raise RuntimeError("D100 population does not reconstruct from D98 plus PCG64 seed 10001")
    rows, fields = read_table(POPULATION)
    parent_fields = [field for field in fields if field.startswith("parent_")][1:]
    residual_fields = [field for field in fields if field.startswith("residual_")][1:]
    by_policy = {row["policy"]: row for row in rows}
    if len(rows) != 193 or len(by_policy) != 193 or set(by_policy) != set(POLICIES):
        raise RuntimeError("D100 population labels or row count mismatch")
    if len(parent_fields) != 153 or len(residual_fields) != 342:
        raise RuntimeError("D100 population feature shape mismatch")
    triplet_failures = 0
    zero_residual_failures = 0
    for index in range(64):
        parent = by_policy[PARENTS[index]]
        zero = by_policy[ZEROS[index]]
        random = by_policy[RANDOMS[index]]
        triplet_failures += any(
            not (parent[field] == zero[field] == random[field]) for field in parent_fields
        )
        zero_residual_failures += any(
            parent[field] != "0.00000000" or zero[field] != "0.00000000"
            for field in residual_fields
        )
    return {
        "policies": len(rows),
        "parent_features": len(parent_fields),
        "residual_features": len(residual_fields),
        "parent_triplet_failures": triplet_failures,
        "parent_or_zero_nonzero_residual_failures": zero_residual_failures,
        "reconstructs_from_d98_and_pcg64_seed_10001": True,
    }


def validate_baselines(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[tuple[int, int, str], dict[str, str]]:
    required = {"map_seed", "seat", "opponent", *TERMINAL_FIELDS}
    if not required.issubset(fields):
        raise RuntimeError(f"D100 baseline fields missing: {sorted(required - set(fields))}")
    by_task = {task_key(row): row for row in rows}
    if len(rows) != TASKS or len(by_task) != TASKS or set(by_task) != expected_tasks():
        raise RuntimeError("D100 baseline coverage mismatch")
    expected_order = sorted(
        rows,
        key=lambda row: (
            int(row["map_seed"]),
            int(row["seat"]),
            OPPONENTS.index(row["opponent"]),
        ),
    )
    if rows != expected_order:
        raise RuntimeError("D100 baselines are not in deterministic order")
    return by_task


def validate_d100_grid(
    rows: list[dict[str, str]], fields: list[str]
) -> tuple[dict[str, dict[tuple[int, int, str], dict[str, str]]], dict]:
    required = {
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "kind",
        "parent",
        "parent_budget",
        "residual_budget",
        *TERMINAL_FIELDS,
        *D100_STAT_FIELDS,
    }
    if not required.issubset(fields):
        raise RuntimeError(f"D100 matrix fields missing: {sorted(required - set(fields))}")
    if len(rows) != len(POLICIES) * TASKS:
        raise RuntimeError(f"D100 matrix size mismatch: {len(rows)}")
    counts = Counter(row["policy"] for row in rows)
    if set(counts) != set(POLICIES) or any(count != TASKS for count in counts.values()):
        raise RuntimeError("D100 policy coverage mismatch")
    tasks = expected_tasks()
    by_policy = {}
    metadata_failures = 0
    parent_hash_variations = 0
    residual_hash_variations = 0
    zero_parameter_hashes = 0
    zero_pair_hash_rows = 0
    for policy in POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        keyed = {task_key(row): row for row in selected}
        if len(keyed) != TASKS or set(keyed) != tasks:
            raise RuntimeError(f"D100 task coverage mismatch for {policy}")
        kind, parent, parent_budget, residual_budget = expected_metadata(policy)
        metadata_failures += sum(
            row["kind"] != kind
            or row["parent"] != parent
            or int(row["parent_budget"]) != parent_budget
            or int(row["residual_budget"]) != residual_budget
            for row in selected
        )
        parent_hashes = {row["parent_hash"] for row in selected}
        residual_hashes = {row["residual_hash"] for row in selected}
        parent_hash_variations += len(parent_hashes) != 1
        residual_hash_variations += len(residual_hashes) != 1
        zero_parameter_hashes += "0" in parent_hashes or "0" in residual_hashes
        zero_pair_hash_rows += sum(row["pair_hash"] == "0" for row in selected)
        by_policy[policy] = keyed
    triplet_parent_hash_failures = 0
    triplet_zero_residual_hash_failures = 0
    random_hash_matches_zero = 0
    for parent, zero, random in zip(PARENTS, ZEROS, RANDOMS):
        parent_hash = next(iter({row["parent_hash"] for row in by_policy[parent].values()}))
        zero_parent_hash = next(iter({row["parent_hash"] for row in by_policy[zero].values()}))
        random_parent_hash = next(iter({row["parent_hash"] for row in by_policy[random].values()}))
        triplet_parent_hash_failures += len({parent_hash, zero_parent_hash, random_parent_hash}) != 1
        parent_residual = next(
            iter({row["residual_hash"] for row in by_policy[parent].values()})
        )
        zero_residual = next(iter({row["residual_hash"] for row in by_policy[zero].values()}))
        random_residual = next(
            iter({row["residual_hash"] for row in by_policy[random].values()})
        )
        triplet_zero_residual_hash_failures += parent_residual != zero_residual
        random_hash_matches_zero += random_residual == zero_residual
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
        raise RuntimeError("D100 rows are not in deterministic order")
    return by_policy, {
        "metadata_failures": metadata_failures,
        "parent_hash_variations": parent_hash_variations,
        "residual_hash_variations": residual_hash_variations,
        "zero_parameter_hashes": zero_parameter_hashes,
        "zero_pair_hash_rows": zero_pair_hash_rows,
        "triplet_parent_hash_failures": triplet_parent_hash_failures,
        "triplet_zero_residual_hash_failures": triplet_zero_residual_hash_failures,
        "random_residual_hash_matches_zero": random_hash_matches_zero,
    }


def validate_d98_grid(
    rows: list[dict[str, str]], fields: list[str]
) -> tuple[dict[str, dict[tuple[int, int, str], dict[str, str]]], dict]:
    required = {
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "kind",
        "budget",
        *TERMINAL_FIELDS,
        *D98_STAT_FIELDS,
    }
    if not required.issubset(fields) or len(rows) != len(D98_POLICIES) * TASKS:
        raise RuntimeError("D98 reference schema or size mismatch")
    counts = Counter(row["policy"] for row in rows)
    if set(counts) != set(D98_POLICIES) or any(count != TASKS for count in counts.values()):
        raise RuntimeError("D98 reference policy coverage mismatch")
    by_policy = {}
    metadata_failures = 0
    hash_variations = 0
    zero_hashes = 0
    for policy in D98_POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        keyed = {task_key(row): row for row in selected}
        if len(keyed) != TASKS or set(keyed) != expected_tasks():
            raise RuntimeError(f"D98 reference task coverage mismatch for {policy}")
        kind = "zero" if policy == D98_ZERO else policy.split("_", 1)[0]
        budget = 1 if policy.startswith("one_") else 4
        metadata_failures += sum(
            row["kind"] != kind or int(row["budget"]) != budget for row in selected
        )
        hashes = {row["policy_hash"] for row in selected}
        hash_variations += len(hashes) != 1
        zero_hashes += hashes == {"0"}
        by_policy[policy] = keyed
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
        raise RuntimeError("D98 reference rows are not in deterministic order")
    return by_policy, {
        "metadata_failures": metadata_failures,
        "policy_hash_variations": hash_variations,
        "zero_policy_hashes": zero_hashes,
    }


def terminal_failures(row: dict[str, str]) -> list[str]:
    failures = []
    if any(not math.isfinite(float(row[field])) for field in FLOAT_FIELDS):
        failures.append("nonfinite_terminal")
    if float(row["reward_identity_error"]) > 1.0e-4:
        failures.append("reward_identity")
    if int(row["margin"]) != int(row["own_score"]) - int(row["opponent_score"]):
        failures.append("margin_identity")
    if sum(int(row[field]) for field in ACTION_PLANES) != int(row["selected_decisions"]):
        failures.append("action_plane_accounting")
    if int(row["own_workers"]) > 3:
        failures.append("worker_cap")
    for field in ("invalid_direct_commands", "provenance_failures", "deposit_prediction_failures"):
        if int(row[field]):
            failures.append(field)
    if int(row["action_hash"]) == 0:
        failures.append("zero_action_hash")
    if int(row["state_hash"]) == 0:
        failures.append("zero_state_hash")
    return failures


def d100_failures(row: dict[str, str]) -> list[str]:
    failures = terminal_failures(row)
    option_batches = int(row["option_batches"])
    eligible = int(row["eligible_pair_batches"])
    scored = int(row["scored_assignments"])
    interventions = int(row["intervention_batches"])
    nonkeep = int(row["nonkeep_assignments"])
    joint = int(row["joint_batches"])
    evaluations = int(row["residual_pair_evaluations"])
    overrides = int(row["residual_overrides"])
    residual_joint = int(row["residual_joint_overrides"])
    pair_options = int(row["pair_options"])
    single_first_options = int(row["single_first_options"])
    single_second_options = int(row["single_second_options"])
    joint_options = int(row["joint_options"])
    override_control = int(row["override_control"])
    override_first = int(row["override_single_first"])
    override_second = int(row["override_single_second"])
    jobs = sum(int(row[field]) for field in OVERRIDE_JOB_FIELDS)
    owners = sum(int(row[field]) for field in OVERRIDE_OWNER_FIELDS)
    mine = int(row["override_mine"])
    if eligible != evaluations or eligible > option_batches:
        failures.append("pair_evaluation_accounting")
    if scored < 2 * evaluations or scored > 2 * option_batches:
        failures.append("scored_assignment_accounting")
    if int(row["preview_validations"]) != evaluations:
        failures.append("preview_validation_accounting")
    if int(row["max_committed_actions"]) != (2 if evaluations else 0):
        failures.append("committed_action_accounting")
    if int(row["max_scored_per_batch"]) > 2:
        failures.append("scoring_cap")
    if interventions > int(row["parent_budget"]):
        failures.append("parent_intervention_budget")
    if overrides > int(row["residual_budget"]) or overrides > evaluations:
        failures.append("residual_override_budget")
    if nonkeep != interventions + joint or joint > interventions:
        failures.append("nonkeep_joint_accounting")
    if pair_options != evaluations + single_first_options + single_second_options + joint_options:
        failures.append("pair_catalog_accounting")
    if override_control + override_first + override_second + residual_joint != overrides:
        failures.append("override_type_accounting")
    expected_jobs = override_first + override_second + 2 * residual_joint
    if jobs != expected_jobs:
        failures.append("override_job_accounting")
    if owners != jobs - mine:
        failures.append("override_owner_accounting")
    if any(int(row[field]) == 0 for field in ("pair_hash", "parent_hash", "residual_hash")):
        failures.append("zero_d100_hash")
    residual_fields = (
        "eligible_pair_batches",
        "residual_pair_evaluations",
        "residual_overrides",
        "residual_joint_overrides",
        "pair_options",
        "single_first_options",
        "single_second_options",
        "joint_options",
        "override_control",
        "override_single_first",
        "override_single_second",
        "preview_validations",
        *OVERRIDE_JOB_FIELDS,
        *OVERRIDE_OWNER_FIELDS,
    )
    if row["policy"] not in RANDOMS and any(int(row[field]) for field in residual_fields):
        failures.append("inactive_residual_nonzero")
    if row["policy"] == CONTROL and any(
        int(row[field])
        for field in (
            "scored_assignments",
            "intervention_batches",
            "nonkeep_assignments",
            "joint_batches",
            "max_scored_per_batch",
            "max_committed_actions",
        )
    ):
        failures.append("d40_control_intervention")
    return failures


def d98_failures(row: dict[str, str]) -> list[str]:
    failures = terminal_failures(row)
    eligible = int(row["eligible_batches"])
    scored = int(row["scored_assignments"])
    interventions = int(row["intervention_batches"])
    nonkeep = int(row["nonkeep_assignments"])
    joint = int(row["joint_batches"])
    jobs = sum(int(row[field]) for field in D98_JOB_FIELDS)
    owners = sum(int(row[field]) for field in D98_OWNER_FIELDS)
    mine = int(row["concrete_mine"])
    if eligible > int(row["option_batches"]) or not (eligible <= scored <= 2 * eligible):
        failures.append("d98_scoring_accounting")
    if interventions > int(row["budget"]) or int(row["max_scored_per_batch"]) > 2:
        failures.append("d98_budget_or_scoring_cap")
    if nonkeep != interventions + joint or joint > interventions:
        failures.append("d98_nonkeep_joint_accounting")
    if jobs != nonkeep or owners != nonkeep - mine:
        failures.append("d98_job_owner_accounting")
    if int(row["catalog_options"]) < scored:
        failures.append("d98_catalog_accounting")
    if int(row["option_hash"]) == 0 or int(row["policy_hash"]) == 0:
        failures.append("d98_zero_hash")
    if row["policy"] == D98_ZERO and (interventions or nonkeep or joint):
        failures.append("d98_zero_control_intervention")
    return failures


def parity_failures(
    left: dict[tuple[int, int, str], dict[str, str]],
    right: dict[tuple[int, int, str], dict[str, str]],
    fields: tuple[str, ...],
) -> list[tuple[str, tuple[int, int, str], str]]:
    return [
        ("parity", key, field)
        for key in sorted(expected_tasks())
        for field in fields
        if left[key][field] != right[key][field]
    ]


def summarize_policy(
    rows: dict[tuple[int, int, str], dict[str, str]],
    parent: dict[tuple[int, int, str], dict[str, str]] | None = None,
) -> dict:
    ordered = [rows[key] for key in sorted(rows)]
    result = {
        "tasks": len(ordered),
        "mean_margin": mean(int(row["margin"]) for row in ordered),
        "worker_three_rate": mean(int(row["own_workers"]) >= 3 for row in ordered),
        "crop_rate": mean(int(row["own_created_crops"]) > 0 for row in ordered),
        "mean_intervention_batches": mean(
            int(row["intervention_batches"]) for row in ordered
        ),
        "mean_residual_overrides": mean(int(row["residual_overrides"]) for row in ordered),
        "override_task_rate": mean(int(row["residual_overrides"]) > 0 for row in ordered),
        "joint_override_task_rate": mean(
            int(row["residual_joint_overrides"]) > 0 for row in ordered
        ),
        "override_job_totals": {
            field.removeprefix("override_"): sum(int(row[field]) for row in ordered)
            for field in OVERRIDE_JOB_FIELDS
        },
        "override_provenance_totals": {
            field.removeprefix("override_owner_"): sum(int(row[field]) for row in ordered)
            for field in OVERRIDE_OWNER_FIELDS
        },
    }
    result["distinct_override_job_kinds"] = sum(
        value > 0 for value in result["override_job_totals"].values()
    )
    result["distinct_override_provenance_classes"] = sum(
        value > 0 for value in result["override_provenance_totals"].values()
    )
    if parent is not None:
        result.update(
            {
                "parent_mean_margin": mean(int(parent[key]["margin"]) for key in sorted(parent)),
                "paired_mean_margin_delta_vs_parent": mean(
                    int(rows[key]["margin"]) - int(parent[key]["margin"])
                    for key in sorted(rows)
                ),
                "changed_action_hash_tasks_vs_parent": sum(
                    rows[key]["action_hash"] != parent[key]["action_hash"]
                    for key in sorted(rows)
                ),
                "changed_action_hash_rate_vs_parent": mean(
                    rows[key]["action_hash"] != parent[key]["action_hash"]
                    for key in sorted(rows)
                ),
                "parent_worker_three_rate": mean(
                    int(parent[key]["own_workers"]) >= 3 for key in sorted(parent)
                ),
            }
        )
        result["worker_three_rate_delta_vs_parent"] = (
            result["worker_three_rate"] - result["parent_worker_three_rate"]
        )
    return result


def baseline_candidate(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    result.update(
        {
            "policy": CONTROL,
            "intervention_batches": "0",
            "residual_overrides": "0",
            "residual_joint_overrides": "0",
            **{field: "0" for field in OVERRIDE_JOB_FIELDS},
            **{field: "0" for field in OVERRIDE_OWNER_FIELDS},
        }
    )
    return result


def select(rows: list[dict[str, str]]) -> dict[str, str]:
    return min(
        rows,
        key=lambda row: (
            -int(row["margin"]),
            -int(row["own_score"]),
            int(row["opponent_score"]),
            int(row["intervention_batches"]),
            int(row["residual_overrides"]),
            row["policy"],
        ),
    )


def oracle_metrics(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict]]:
    parent_selections = Counter()
    superset_selections = Counter()
    strict_random_winners = Counter()
    parent_margins = []
    superset_margins = []
    superset_deltas = []
    own_deltas = []
    opponent_deltas = []
    family_deltas = defaultdict(list)
    workers = []
    crops = []
    strict_random_tasks = 0
    selected_random_rows = 0
    selected_override_rows = 0
    selected_joint_override_rows = 0
    selected_jobs = set()
    selected_owners = set()
    selected_seats = set()
    selected_opponents = set()
    details = []
    for key in sorted(expected_tasks()):
        baseline = baselines[key]
        base = baseline_candidate(baseline)
        parent = select([base, *[by_policy[policy][key] for policy in PARENTS]])
        superset = select(
            [
                base,
                *[by_policy[policy][key] for policy in PARENTS],
                *[by_policy[policy][key] for policy in RANDOMS],
            ]
        )
        parent_selections[parent["policy"]] += 1
        superset_selections[superset["policy"]] += 1
        parent_margins.append(int(parent["margin"]))
        superset_margins.append(int(superset["margin"]))
        delta = int(superset["margin"]) - int(baseline["margin"])
        superset_deltas.append(delta)
        own_deltas.append(int(superset["own_score"]) - int(baseline["own_score"]))
        opponent_deltas.append(
            int(superset["opponent_score"]) - int(baseline["opponent_score"])
        )
        family_deltas[key[2]].append(delta)
        workers.append(int(superset["own_workers"]) >= 3)
        crops.append(int(superset["own_created_crops"]) > 0)
        strict = (
            superset["policy"] in RANDOMS
            and int(superset["margin"]) > int(parent["margin"])
        )
        strict_random_tasks += strict
        if strict:
            strict_random_winners[superset["policy"]] += 1
        if superset["policy"] in RANDOMS:
            selected_random_rows += 1
            selected_override_rows += int(superset["residual_overrides"]) > 0
            selected_joint_override_rows += int(superset["residual_joint_overrides"]) > 0
            selected_jobs.update(
                field.removeprefix("override_")
                for field in OVERRIDE_JOB_FIELDS
                if int(superset[field]) > 0
            )
            selected_owners.update(
                field.removeprefix("override_owner_")
                for field in OVERRIDE_OWNER_FIELDS
                if int(superset[field]) > 0
            )
            selected_seats.add(key[1])
            selected_opponents.add(key[2])
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "d40_margin": int(baseline["margin"]),
                "parent_policy": parent["policy"],
                "parent_margin": int(parent["margin"]),
                "superset_policy": superset["policy"],
                "superset_margin": int(superset["margin"]),
                "strict_random_improvement": strict,
            }
        )
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    metrics = {
        "tasks": TASKS,
        "d40_mean_margin": mean(int(row["margin"]) for row in baselines.values()),
        "parent_oracle_mean_margin": mean(parent_margins),
        "strict_superset_oracle_mean_margin": mean(superset_margins),
        "strict_superset_minus_parent_oracle_mean_margin": mean(superset_margins)
        - mean(parent_margins),
        "strict_superset_paired_mean_margin_delta_vs_d40": mean(superset_deltas),
        "strict_superset_paired_mean_own_score_delta_vs_d40": mean(own_deltas),
        "strict_superset_paired_mean_opponent_score_delta_vs_d40": mean(opponent_deltas),
        "strict_superset_opponent_family_mean_margin_deltas_vs_d40": family_means,
        "strict_superset_worst_opponent_family_mean_margin_delta_vs_d40": min(
            family_means.values()
        ),
        "strict_superset_worker_three_rate": mean(workers),
        "strict_superset_crop_rate": mean(crops),
        "strict_random_improvement_tasks": strict_random_tasks,
        "parent_oracle_selected_policy_counts": dict(sorted(parent_selections.items())),
        "strict_superset_selected_policy_counts": dict(sorted(superset_selections.items())),
        "strict_random_winner_counts": dict(sorted(strict_random_winners.items())),
        "random_policies_with_at_least_two_strict_wins": sum(
            strict_random_winners[policy] >= 2 for policy in RANDOMS
        ),
        "selected_random_rows": selected_random_rows,
        "selected_random_rows_with_override": selected_override_rows,
        "selected_random_rows_with_joint_override": selected_joint_override_rows,
        "selected_random_override_job_kinds": sorted(selected_jobs),
        "selected_random_override_provenance_classes": sorted(selected_owners),
        "selected_random_seats": sorted(selected_seats),
        "selected_random_opponent_families": sorted(selected_opponents),
    }
    return metrics, details


def main() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D100 prerequisite missing or changed: {path}")
    required_outputs = (RUN_A, RUN_B, BASELINES_A, BASELINES_B, D98_REFERENCE, D98_BASELINES)
    for path in required_outputs:
        if not path.exists():
            raise SystemExit(f"missing D100 artifact: {path}")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D100 result")
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D100 population repeats are not byte-identical")
    if BASELINES_A.read_bytes() != BASELINES_B.read_bytes():
        raise RuntimeError("D100 baseline repeats are not byte-identical")
    if BASELINES_A.read_bytes() != D98_BASELINES.read_bytes():
        raise RuntimeError("D100 and frozen D98 baselines differ")

    population_audit = validate_population()
    rows, fields = read_table(RUN_A)
    repeat_rows, repeat_fields = read_table(RUN_B)
    baselines, baseline_fields = read_table(BASELINES_A)
    repeat_baselines, repeat_baseline_fields = read_table(BASELINES_B)
    d98_rows, d98_fields = read_table(D98_REFERENCE)
    d98_baselines, d98_baseline_fields = read_table(D98_BASELINES)
    if rows != repeat_rows or fields != repeat_fields:
        raise RuntimeError("D100 parsed policy repeats differ")
    if baselines != repeat_baselines or baseline_fields != repeat_baseline_fields:
        raise RuntimeError("D100 parsed baseline repeats differ")
    if baselines != d98_baselines or baseline_fields != d98_baseline_fields:
        raise RuntimeError("D100 and frozen D98 parsed baselines differ")

    baseline_by_task = validate_baselines(baselines, baseline_fields)
    by_policy, grid_audit = validate_d100_grid(rows, fields)
    d98_by_policy, d98_grid_audit = validate_d98_grid(d98_rows, d98_fields)

    integrity = Counter()
    d98_integrity = Counter()
    for row in baselines:
        integrity.update(terminal_failures(row))
    for row in rows:
        integrity.update(d100_failures(row))
    for row in d98_rows:
        d98_integrity.update(d98_failures(row))

    d40_parity = parity_failures(by_policy[CONTROL], baseline_by_task, TERMINAL_FIELDS)
    d98_d40_parity = parity_failures(
        d98_by_policy[D98_ZERO], baseline_by_task, TERMINAL_FIELDS
    )
    parent_reference_parity = []
    zero_parent_parity = []
    for index in range(64):
        parent_reference_parity.extend(
            parity_failures(
                by_policy[PARENTS[index]],
                d98_by_policy[D98_FOURS[index]],
                TERMINAL_FIELDS,
            )
        )
        zero_parent_parity.extend(
            parity_failures(
                by_policy[ZEROS[index]],
                by_policy[PARENTS[index]],
                (*TERMINAL_FIELDS, *D100_STAT_FIELDS),
            )
        )

    summaries = {
        CONTROL: summarize_policy(by_policy[CONTROL]),
        **{policy: summarize_policy(by_policy[policy]) for policy in PARENTS},
        **{policy: summarize_policy(by_policy[policy]) for policy in ZEROS},
        **{
            random: summarize_policy(by_policy[random], by_policy[parent])
            for random, parent in zip(RANDOMS, PARENTS)
        },
    }
    retained_worker_three = [
        policy
        for policy in RANDOMS
        if summaries[policy]["worker_three_rate_delta_vs_parent"] >= -0.10
    ]
    action_active = [
        policy
        for policy in RANDOMS
        if summaries[policy]["changed_action_hash_rate_vs_parent"] >= 0.25
    ]
    override_active = [
        policy for policy in RANDOMS if summaries[policy]["override_task_rate"] >= 0.25
    ]
    joint_active = [
        policy
        for policy in RANDOMS
        if summaries[policy]["joint_override_task_rate"] >= 0.10
    ]
    broad = [
        policy
        for policy in RANDOMS
        if summaries[policy]["distinct_override_job_kinds"] >= 3
        and summaries[policy]["distinct_override_provenance_classes"] >= 2
    ]
    fixed_deltas = [
        summaries[policy]["paired_mean_margin_delta_vs_parent"] for policy in RANDOMS
    ]
    surface = {
        "random_policies_retaining_parent_worker_three": retained_worker_three,
        "random_policies_retaining_parent_worker_three_count": len(retained_worker_three),
        "random_policies_changing_quarter_actions": action_active,
        "random_policies_changing_quarter_actions_count": len(action_active),
        "random_policies_overriding_quarter_tasks": override_active,
        "random_policies_overriding_quarter_tasks_count": len(override_active),
        "random_policies_joint_overriding_tenth_tasks": joint_active,
        "random_policies_joint_overriding_tenth_tasks_count": len(joint_active),
        "broad_random_policies": broad,
        "broad_random_policy_count": len(broad),
        "random_fixed_paired_mean_delta_vs_parent_minimum": min(fixed_deltas),
        "random_fixed_paired_mean_delta_vs_parent_maximum": max(fixed_deltas),
        "random_fixed_paired_mean_delta_vs_parent_range": max(fixed_deltas)
        - min(fixed_deltas),
    }
    oracle, oracle_details = oracle_metrics(by_policy, baseline_by_task)

    construction_audit = {
        "illegal_macro_action_failures": 0,
        "nonfinite_feature_failures": 0,
        "reservation_or_target_collision_failures": 0,
        "final_live_own_crop_fell_failures": 0,
        "pair_preview_runtime_assertion_failures": 0,
        "catalog_runtime_assertion_failures": 0,
        "basis": (
            "both hashed evaluator runs completed; legal-action, finite-feature, pair-preview, "
            "catalog, reservation, and final-own-crop guards are runtime assertions or "
            "construction invariants"
        ),
    }
    audit = {
        "population": population_audit,
        "d100_output_fields": len(fields),
        "d98_reference_output_fields": len(d98_fields),
        "baseline_output_fields": len(baseline_fields),
        "policies": len(POLICIES),
        "tasks_per_policy": TASKS,
        "d100_rows": len(rows),
        "d98_reference_rows": len(d98_rows),
        "baseline_rows": len(baselines),
        "repeat_byte_identical": True,
        "d100_grid": grid_audit,
        "d98_reference_grid": d98_grid_audit,
        "d40_control_parity_failures": len(d40_parity),
        "d98_d40_control_parity_failures": len(d98_d40_parity),
        "parent_reference_terminal_parity_failures": len(parent_reference_parity),
        "zero_parent_behavioral_parity_failures": len(zero_parent_parity),
        "integrity_failure_counts": dict(sorted(integrity.items())),
        "d98_reference_integrity_failure_counts": dict(sorted(d98_integrity.items())),
        "construction_audit": construction_audit,
    }

    grid_hash_clean = all(value == 0 for value in grid_audit.values())
    integrity_gates = {
        "complete_byte_identical_193x128_d100_repeats": True,
        "byte_identical_d100_and_frozen_d98_baselines": True,
        "d100_d40_control_exact_parity": not d40_parity,
        "d98_reference_d40_control_exact_parity": not d98_d40_parity,
        "all_64_parents_exact_d98_terminal_parity": not parent_reference_parity,
        "all_64_zero_residuals_exact_parent_behavioral_parity": not zero_parent_parity,
        "population_reconstructs_from_d98_and_pcg64_seed_10001": population_audit[
            "reconstructs_from_d98_and_pcg64_seed_10001"
        ]
        and population_audit["parent_triplet_failures"] == 0
        and population_audit["parent_or_zero_nonzero_residual_failures"] == 0,
        "all_metadata_and_parameter_hashes_stable_nonzero_and_matched": grid_hash_clean,
        "zero_d100_mechanics_integrity_failures": not integrity,
        "zero_d98_reference_integrity_failures": not d98_integrity,
        "zero_runtime_construction_failures": all(
            value == 0 for key, value in construction_audit.items() if key != "basis"
        ),
    }
    activity_gates = {
        "every_policy_crops_in_every_task": all(
            summaries[policy]["crop_rate"] == 1.0 for policy in POLICIES
        ),
        "at_least_56_randoms_retain_parent_worker_three": len(retained_worker_three) >= 56,
        "at_least_56_randoms_change_quarter_actions": len(action_active) >= 56,
        "at_least_48_randoms_override_quarter_tasks": len(override_active) >= 48,
        "at_least_32_randoms_joint_override_tenth_tasks": len(joint_active) >= 32,
        "at_least_48_randoms_span_three_jobs_two_provenances": len(broad) >= 48,
        "random_fixed_paired_delta_range_at_least_20": surface[
            "random_fixed_paired_mean_delta_vs_parent_range"
        ]
        >= 20,
    }
    headroom_gates = {
        "strict_superset_at_least_5_above_parent_oracle": oracle[
            "strict_superset_minus_parent_oracle_mean_margin"
        ]
        >= 5,
        "random_strictly_improves_parent_oracle_in_at_least_24_tasks": oracle[
            "strict_random_improvement_tasks"
        ]
        >= 24,
        "at_least_12_randoms_have_two_strict_wins": oracle[
            "random_policies_with_at_least_two_strict_wins"
        ]
        >= 12,
        "strict_superset_gain_vs_d40_at_least_55": oracle[
            "strict_superset_paired_mean_margin_delta_vs_d40"
        ]
        >= 55,
        "all_strict_superset_opponent_family_gains_at_least_15": oracle[
            "strict_superset_worst_opponent_family_mean_margin_delta_vs_d40"
        ]
        >= 15,
        "strict_superset_mean_own_score_delta_nonnegative": oracle[
            "strict_superset_paired_mean_own_score_delta_vs_d40"
        ]
        >= 0,
        "strict_superset_mean_opponent_score_delta_nonpositive": oracle[
            "strict_superset_paired_mean_opponent_score_delta_vs_d40"
        ]
        <= 0,
        "strict_superset_worker_three_rate_at_least_85pct": oracle[
            "strict_superset_worker_three_rate"
        ]
        >= 0.85,
        "strict_superset_crop_rate_exactly_100pct": oracle[
            "strict_superset_crop_rate"
        ]
        == 1.0,
        "selected_random_rows_override_in_at_least_24_tasks": oracle[
            "selected_random_rows_with_override"
        ]
        >= 24,
        "selected_random_rows_joint_override_in_at_least_16_tasks": oracle[
            "selected_random_rows_with_joint_override"
        ]
        >= 16,
        "selected_random_rows_span_all_jobs_two_provenances_both_seats_all_families": len(
            oracle["selected_random_override_job_kinds"]
        )
        == 4
        and len(oracle["selected_random_override_provenance_classes"]) >= 2
        and len(oracle["selected_random_seats"]) == 2
        and len(oracle["selected_random_opponent_families"]) == len(OPPONENTS),
    }
    integrity_gates = {name: bool(value) for name, value in integrity_gates.items()}
    activity_gates = {name: bool(value) for name, value in activity_gates.items()}
    headroom_gates = {name: bool(value) for name, value in headroom_gates.items()}
    gates = {**integrity_gates, **activity_gates, **headroom_gates}
    if not all(integrity_gates.values()):
        decision = "quarantine_value_and_repair_only_integrity_defects"
    elif not all(activity_gates.values()):
        decision = "close_anchored_pair_residual_initialization_on_consumed_maps"
    elif not all(headroom_gates.values()):
        decision = "close_pair_residuals_on_d98_surface_and_switch_representation"
    else:
        decision = "open_short_anchored_residual_mechanics_and_learning_signal_preflight"

    best_fixed = max(
        RANDOMS,
        key=lambda policy: (summaries[policy]["paired_mean_margin_delta_vs_parent"], policy),
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "population_lock_sha256": sha256(POPULATION_LOCK),
            "implementation_lock_sha256": sha256(IMPLEMENTATION_LOCK),
            "population_sha256": sha256(POPULATION),
            "run_a_sha256": sha256(RUN_A),
            "run_b_sha256": sha256(RUN_B),
            "baselines_a_sha256": sha256(BASELINES_A),
            "baselines_b_sha256": sha256(BASELINES_B),
            "d98_reference_sha256": sha256(D98_REFERENCE),
            "d98_baselines_sha256": sha256(D98_BASELINES),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
            "evaluator_source_sha256": sha256(EVALUATOR_SOURCE),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "d100_binary_sha256": sha256(D100_BINARY),
            "d98_reference_binary_sha256": sha256(D98_BINARY),
            "analyzer_source_sha256": sha256(Path(__file__)),
        },
        "audit": audit,
        "surface": surface,
        "policy_summaries": summaries,
        "best_fixed_random_policy_descriptive_only": {
            "policy": best_fixed,
            **summaries[best_fixed],
        },
        "oracle": oracle,
        "oracle_details": oracle_details,
        "integrity_gates": integrity_gates,
        "activity_gates": activity_gates,
        "headroom_gates": headroom_gates,
        "gates": gates,
        "pass": all(gates.values()),
        "decision": decision,
        "scope": (
            "consumed-map D98-anchored pair-residual function-class upper bound only; fixed "
            "random policies and hindsight choices are unselectable, with no candidate, "
            "TestSession, submission, Arena action, or resident replacement"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "audit": audit,
                "surface": surface,
                "oracle": oracle,
                "integrity_gates": integrity_gates,
                "activity_gates": activity_gates,
                "headroom_gates": headroom_gates,
                "pass": report["pass"],
                "decision": decision,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
