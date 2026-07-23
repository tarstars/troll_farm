#!/usr/bin/env python3
"""Validate the frozen D99 pair-aware batch-action population."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import make_d99a_pair_action_population as generator


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d99a-pair-aware-batch-action-population-protocol-2026-07-21.md"
POPULATION_LOCK = ANALYSIS / "d99a-pair-aware-batch-action-population-lock-2026-07-21.md"
IMPLEMENTATION_LOCK = ANALYSIS / "d99a-pair-aware-batch-action-implementation-lock-2026-07-21.md"
POPULATION = ANALYSIS / "d99a-pair-aware-batch-action-population.tsv"
RUN_A = ANALYSIS / "d99a-pair-aware-batch-action-population-a-9822000-9822007.tsv"
RUN_B = ANALYSIS / "d99a-pair-aware-batch-action-population-b-9822000-9822007.tsv"
BASELINES_A = ANALYSIS / "d99a-pair-aware-batch-action-baselines-a-9822000-9822007.tsv"
BASELINES_B = ANALYSIS / "d99a-pair-aware-batch-action-baselines-b-9822000-9822007.tsv"
D98_POPULATION = ANALYSIS / "d98a-bounded-whole-game-joint-assignment-population.tsv"
D98_REFERENCE = ANALYSIS / "d99a-d98-reference-population-9822000-9822007.tsv"
D98_BASELINES = ANALYSIS / "d99a-d98-reference-baselines-9822000-9822007.tsv"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d99a_pair_action_population.py"
EVALUATOR_SOURCE = ROOT / "rust" / "src" / "bin" / "d99_pair_action_population.rs"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
D98_BINARY = ROOT / "rust" / "target" / "release" / "d98_bounded_joint_assignment_population"
OUTPUT = ANALYSIS / "d99a-pair-aware-batch-action-population-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "7263a04fdef43f0ecd4cdb74aa377c3417eafe81e03a591f459db539cdc519b8",
    POPULATION_LOCK: "78a8048673df9b5c2944452f310757e929a5d1701f1a90835c936121dc3aa58f",
    IMPLEMENTATION_LOCK: "10a90024df71e7ce25fe1499e1dfbe7bd1b029c43b11d13fdcb84712c2b84185",
    POPULATION: "4e46456c2b8d156b7219cd5a78fb08b35bf4d59977ef30e4aa97afb6b8f18789",
    D98_POPULATION: "3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e",
    GENERATOR_SOURCE: "f150f56f3472c5f71e94732944e60634d3d9348ad5c9524814d05c7c4934872c",
    EVALUATOR_SOURCE: "bcb3f340150e8639f862380d8b0492e90683cfef8b7dd1074ac5811a1128d3a1",
    ENV_SOURCE: "1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5",
    PRIOR_SOURCE: "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62",
    D98_BINARY: "1e660c8c4615b646f0cc3a190746b2af0e821dea309a34f748f88901249493eb",
}

MAP_START = 9_822_000
MAP_STOP = 9_822_008
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
ZERO = "zero_control"
ONES = tuple(f"one_{index:02d}" for index in range(64))
FOURS = tuple(f"four_{index:02d}" for index in range(64))
POLICIES = (ZERO, *ONES, *FOURS)
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
JOB_FIELDS = (
    "concrete_fell",
    "concrete_harvest",
    "concrete_renew",
    "concrete_mine",
)
OWNER_FIELDS = (
    "owner_natural",
    "owner_own",
    "owner_opponent",
    "owner_ambiguous",
)
D99_STAT_FIELDS = (
    "option_batches",
    "eligible_pair_batches",
    "scored_pairs",
    "intervention_batches",
    "nonkeep_assignments",
    "joint_pairs",
    "max_committed_actions",
    "safety_rejections",
    "pair_options",
    "single_first_options",
    "single_second_options",
    "joint_options",
    "selected_single_first",
    "selected_single_second",
    "preview_validations",
    *JOB_FIELDS,
    *OWNER_FIELDS,
    "pair_hash",
    "policy_hash",
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
    *JOB_FIELDS,
    *OWNER_FIELDS,
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


def expected_kind(policy: str) -> str:
    if policy == ZERO:
        return "zero"
    return "one" if policy.startswith("one_") else "four"


def expected_budget(policy: str) -> int:
    return 1 if policy.startswith("one_") else 4


def validate_population() -> dict:
    expected = generator.render(generator.population())
    if POPULATION.read_text() != expected:
        raise RuntimeError("D99 population does not reconstruct from PCG64 seed 9901")
    rows, fields = read_table(POPULATION)
    parameters = [field for field in fields if field.startswith("param_")]
    if len(rows) != 129 or len(parameters) != 342:
        raise RuntimeError("D99 population shape mismatch")
    by_policy = {row["policy"]: row for row in rows}
    if len(by_policy) != len(rows) or set(by_policy) != set(POLICIES):
        raise RuntimeError("D99 population labels mismatch")
    pair_failures = 0
    for one, four in zip(ONES, FOURS):
        left = by_policy[one]
        right = by_policy[four]
        pair_failures += any(left[field] != right[field] for field in parameters)
        pair_failures += (left["kind"], right["kind"]) != ("one", "four")
        pair_failures += (left["budget"], right["budget"]) != ("1", "4")
    return {
        "policies": len(rows),
        "features": len(parameters),
        "matched_pair_failures": pair_failures,
        "reconstructs_from_pcg64_seed_9901": True,
    }


def validate_baselines(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[tuple[int, int, str], dict[str, str]]:
    required = {"map_seed", "seat", "opponent", *TERMINAL_FIELDS}
    if not required.issubset(fields):
        raise RuntimeError(f"D99 baseline fields missing: {sorted(required - set(fields))}")
    by_task = {task_key(row): row for row in rows}
    if len(rows) != TASKS or len(by_task) != TASKS or set(by_task) != expected_tasks():
        raise RuntimeError("D99 baseline coverage mismatch")
    expected_order = sorted(
        rows,
        key=lambda row: (
            int(row["map_seed"]),
            int(row["seat"]),
            OPPONENTS.index(row["opponent"]),
        ),
    )
    if rows != expected_order:
        raise RuntimeError("D99 baselines are not in deterministic order")
    return by_task


def validate_grid(
    rows: list[dict[str, str]], fields: list[str], stat_fields: tuple[str, ...], label: str
) -> tuple[dict[str, dict[tuple[int, int, str], dict[str, str]]], dict]:
    required = {
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "kind",
        "budget",
        *TERMINAL_FIELDS,
        *stat_fields,
    }
    if not required.issubset(fields):
        raise RuntimeError(f"{label} matrix fields missing: {sorted(required - set(fields))}")
    if len(rows) != len(POLICIES) * TASKS:
        raise RuntimeError(f"{label} matrix size mismatch: {len(rows)}")
    counts = Counter(row["policy"] for row in rows)
    if set(counts) != set(POLICIES) or any(count != TASKS for count in counts.values()):
        raise RuntimeError(f"{label} policy coverage mismatch")
    tasks = expected_tasks()
    by_policy = {}
    kind_budget_failures = 0
    hash_variations = 0
    zero_hashes = 0
    for policy in POLICIES:
        selected = [row for row in rows if row["policy"] == policy]
        keyed = {task_key(row): row for row in selected}
        if len(keyed) != TASKS or set(keyed) != tasks:
            raise RuntimeError(f"{label} task coverage mismatch for {policy}")
        kind_budget_failures += sum(
            row["kind"] != expected_kind(policy)
            or int(row["budget"]) != expected_budget(policy)
            for row in selected
        )
        hashes = {row["policy_hash"] for row in selected}
        hash_variations += len(hashes) != 1
        zero_hashes += hashes == {"0"}
        by_policy[policy] = keyed
    pair_hash_failures = sum(
        next(iter({row["policy_hash"] for row in by_policy[one].values()}))
        != next(iter({row["policy_hash"] for row in by_policy[four].values()}))
        for one, four in zip(ONES, FOURS)
    )
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
        raise RuntimeError(f"{label} rows are not in deterministic order")
    return by_policy, {
        "kind_or_budget_failures": kind_budget_failures,
        "policy_hash_variations": hash_variations,
        "zero_policy_hashes": zero_hashes,
        "matched_pair_policy_hash_failures": pair_hash_failures,
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
    for field in (
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
    ):
        if int(row[field]):
            failures.append(field)
    if int(row["action_hash"]) == 0:
        failures.append("zero_action_hash")
    if int(row["state_hash"]) == 0:
        failures.append("zero_state_hash")
    return failures


def d99_failures(row: dict[str, str]) -> list[str]:
    failures = terminal_failures(row)
    option_batches = int(row["option_batches"])
    eligible = int(row["eligible_pair_batches"])
    scored = int(row["scored_pairs"])
    interventions = int(row["intervention_batches"])
    nonkeep = int(row["nonkeep_assignments"])
    joint = int(row["joint_pairs"])
    pair_options = int(row["pair_options"])
    single_first_options = int(row["single_first_options"])
    single_second_options = int(row["single_second_options"])
    joint_options = int(row["joint_options"])
    selected_single_first = int(row["selected_single_first"])
    selected_single_second = int(row["selected_single_second"])
    jobs = sum(int(row[field]) for field in JOB_FIELDS)
    owners = sum(int(row[field]) for field in OWNER_FIELDS)
    mine = int(row["concrete_mine"])
    if eligible > option_batches or scored != eligible:
        failures.append("eligible_pair_accounting")
    if int(row["preview_validations"]) != scored:
        failures.append("preview_validation_accounting")
    if int(row["max_committed_actions"]) != (2 if scored else 0):
        failures.append("committed_action_accounting")
    if interventions > int(row["budget"]) or interventions > scored:
        failures.append("intervention_budget")
    if selected_single_first + selected_single_second + joint != interventions:
        failures.append("selected_pair_type_accounting")
    if nonkeep != interventions + joint:
        failures.append("nonkeep_joint_accounting")
    if pair_options != scored + single_first_options + single_second_options + joint_options:
        failures.append("pair_catalog_accounting")
    if jobs != nonkeep:
        failures.append("job_accounting")
    if owners != nonkeep - mine:
        failures.append("owner_accounting")
    if int(row["pair_hash"]) == 0:
        failures.append("zero_pair_hash")
    if int(row["policy_hash"]) == 0:
        failures.append("zero_policy_hash")
    if row["policy"] == ZERO and any(
        int(row[field])
        for field in (
            "intervention_batches",
            "nonkeep_assignments",
            "joint_pairs",
            "selected_single_first",
            "selected_single_second",
            *JOB_FIELDS,
            *OWNER_FIELDS,
        )
    ):
        failures.append("zero_control_intervention")
    return failures


def d98_failures(row: dict[str, str]) -> list[str]:
    failures = terminal_failures(row)
    eligible = int(row["eligible_batches"])
    scored = int(row["scored_assignments"])
    interventions = int(row["intervention_batches"])
    nonkeep = int(row["nonkeep_assignments"])
    joint = int(row["joint_batches"])
    jobs = sum(int(row[field]) for field in JOB_FIELDS)
    owners = sum(int(row[field]) for field in OWNER_FIELDS)
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
    if row["policy"] == ZERO and (interventions or nonkeep or joint):
        failures.append("d98_zero_control_intervention")
    return failures


def parity_failures(
    policy_rows: dict[tuple[int, int, str], dict[str, str]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> list[tuple[tuple[int, int, str], str]]:
    return [
        (key, field)
        for key in sorted(expected_tasks())
        for field in TERMINAL_FIELDS
        if policy_rows[key][field] != baselines[key][field]
    ]


def summarize_policy(
    rows: dict[tuple[int, int, str], dict[str, str]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    ordered = [rows[key] for key in sorted(rows)]
    jobs = {
        field.removeprefix("concrete_"): sum(int(row[field]) for row in ordered)
        for field in JOB_FIELDS
    }
    owners = {
        field.removeprefix("owner_"): sum(int(row[field]) for row in ordered)
        for field in OWNER_FIELDS
    }
    changed = sum(
        row["action_hash"] != baselines[task_key(row)]["action_hash"] for row in ordered
    )
    return {
        "tasks": len(ordered),
        "mean_margin": mean(int(row["margin"]) for row in ordered),
        "paired_mean_margin_delta_vs_d40": mean(
            int(row["margin"]) - int(baselines[task_key(row)]["margin"])
            for row in ordered
        ),
        "worker_three_rate": mean(int(row["own_workers"]) >= 3 for row in ordered),
        "crop_rate": mean(int(row["own_created_crops"]) > 0 for row in ordered),
        "changed_action_hash_tasks_vs_d40": changed,
        "changed_action_hash_rate_vs_d40": changed / len(ordered),
        "tasks_with_at_least_two_interventions": sum(
            int(row["intervention_batches"]) >= 2 for row in ordered
        ),
        "at_least_two_intervention_task_rate": mean(
            int(row["intervention_batches"]) >= 2 for row in ordered
        ),
        "tasks_with_joint_pair": sum(int(row["joint_pairs"]) > 0 for row in ordered),
        "joint_pair_task_rate": mean(int(row["joint_pairs"]) > 0 for row in ordered),
        "mean_intervention_batches": mean(
            int(row["intervention_batches"]) for row in ordered
        ),
        "mean_nonkeep_assignments": mean(
            int(row["nonkeep_assignments"]) for row in ordered
        ),
        "job_totals": jobs,
        "distinct_job_kinds": sum(value > 0 for value in jobs.values()),
        "provenance_totals": owners,
        "distinct_provenance_classes": sum(value > 0 for value in owners.values()),
    }


def baseline_candidate(row: dict[str, str]) -> dict[str, str]:
    result = dict(row)
    result.update(
        {
            "policy": "d40_control",
            "kind": "control",
            "budget": "0",
            "intervention_batches": "0",
            "nonkeep_assignments": "0",
            "joint_pairs": "0",
            **{field: "0" for field in JOB_FIELDS},
            **{field: "0" for field in OWNER_FIELDS},
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
            row["policy"],
        ),
    )


def oracle_metrics(
    by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]],
    d98_by_policy: dict[str, dict[tuple[int, int, str], dict[str, str]]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict]]:
    one_selections = Counter()
    four_selections = Counter()
    strict_four_winners = Counter()
    four_deltas = []
    four_own_deltas = []
    four_opponent_deltas = []
    one_margins = []
    four_margins = []
    d98_margins = []
    family_deltas = defaultdict(list)
    worker_three = []
    crops = []
    four_beats_one = 0
    d99_beats_d98 = 0
    selected_two_interventions = 0
    selected_joint = 0
    selected_jobs = set()
    selected_owners = set()
    selected_seats = set()
    selected_opponents = set()
    details = []
    for key in sorted(expected_tasks()):
        baseline = baselines[key]
        base = baseline_candidate(baseline)
        one = select([base, *[by_policy[policy][key] for policy in ONES]])
        four = select([base, *[by_policy[policy][key] for policy in FOURS]])
        d98_four = select([base, *[d98_by_policy[policy][key] for policy in FOURS]])
        one_selections[one["policy"]] += 1
        four_selections[four["policy"]] += 1
        delta = int(four["margin"]) - int(baseline["margin"])
        four_deltas.append(delta)
        four_own_deltas.append(int(four["own_score"]) - int(baseline["own_score"]))
        four_opponent_deltas.append(
            int(four["opponent_score"]) - int(baseline["opponent_score"])
        )
        one_margins.append(int(one["margin"]))
        four_margins.append(int(four["margin"]))
        d98_margins.append(int(d98_four["margin"]))
        family_deltas[key[2]].append(delta)
        worker_three.append(int(four["own_workers"]) >= 3)
        crops.append(int(four["own_created_crops"]) > 0)
        beats_one = int(four["margin"]) > int(one["margin"])
        beats_d98 = int(four["margin"]) > int(d98_four["margin"])
        four_beats_one += beats_one
        d99_beats_d98 += beats_d98
        if four["policy"] in FOURS:
            if delta > 0:
                strict_four_winners[four["policy"]] += 1
            selected_two_interventions += int(four["intervention_batches"]) >= 2
            selected_joint += int(four["joint_pairs"]) > 0
            selected_jobs.update(
                field.removeprefix("concrete_")
                for field in JOB_FIELDS
                if int(four[field]) > 0
            )
            selected_owners.update(
                field.removeprefix("owner_")
                for field in OWNER_FIELDS
                if int(four[field]) > 0
            )
            selected_seats.add(key[1])
            selected_opponents.add(key[2])
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "d40_margin": int(baseline["margin"]),
                "one_policy": one["policy"],
                "one_margin": int(one["margin"]),
                "four_policy": four["policy"],
                "four_margin": int(four["margin"]),
                "d98_four_policy": d98_four["policy"],
                "d98_four_margin": int(d98_four["margin"]),
                "four_margin_delta_vs_d40": delta,
                "four_strictly_beats_one_margin": beats_one,
                "d99_strictly_beats_d98_margin": beats_d98,
            }
        )
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    metrics = {
        "tasks": TASKS,
        "d40_mean_margin": mean(int(row["margin"]) for row in baselines.values()),
        "one_oracle_mean_margin": mean(one_margins),
        "four_oracle_mean_margin": mean(four_margins),
        "d98_reference_four_oracle_mean_margin": mean(d98_margins),
        "four_minus_one_oracle_mean_margin": mean(four_margins) - mean(one_margins),
        "d99_four_minus_d98_reference_mean_margin": mean(four_margins)
        - mean(d98_margins),
        "four_oracle_paired_mean_margin_delta_vs_d40": mean(four_deltas),
        "four_oracle_paired_mean_own_score_delta_vs_d40": mean(four_own_deltas),
        "four_oracle_paired_mean_opponent_score_delta_vs_d40": mean(
            four_opponent_deltas
        ),
        "four_oracle_strict_margin_improvements_vs_d40": sum(
            value > 0 for value in four_deltas
        ),
        "four_oracle_strict_margin_improvement_rate_vs_d40": mean(
            value > 0 for value in four_deltas
        ),
        "four_oracle_opponent_family_mean_margin_deltas_vs_d40": family_means,
        "four_oracle_worst_opponent_family_mean_margin_delta_vs_d40": min(
            family_means.values()
        ),
        "four_oracle_worker_three_rate": mean(worker_three),
        "four_oracle_crop_rate": mean(crops),
        "four_oracle_strictly_beats_one_margin_tasks": four_beats_one,
        "d99_strictly_beats_d98_reference_margin_tasks": d99_beats_d98,
        "one_oracle_selected_policy_counts": dict(sorted(one_selections.items())),
        "four_oracle_selected_policy_counts": dict(sorted(four_selections.items())),
        "four_strict_winner_counts": dict(sorted(strict_four_winners.items())),
        "four_policies_with_at_least_two_strict_wins": sum(
            strict_four_winners[policy] >= 2 for policy in FOURS
        ),
        "selected_four_policy_rows": sum(four_selections[policy] for policy in FOURS),
        "selected_four_rows_with_at_least_two_interventions": selected_two_interventions,
        "selected_four_rows_with_joint_pair": selected_joint,
        "selected_four_job_kinds": sorted(selected_jobs),
        "selected_four_provenance_classes": sorted(selected_owners),
        "selected_four_seats": sorted(selected_seats),
        "selected_four_opponent_families": sorted(selected_opponents),
    }
    return metrics, details


def main() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D99 prerequisite missing or changed: {path}")
    for path in (RUN_A, RUN_B, BASELINES_A, BASELINES_B, D98_REFERENCE, D98_BASELINES):
        if not path.exists():
            raise SystemExit(f"missing D99 artifact: {path}")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D99 result")
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D99 population repeats are not byte-identical")
    if BASELINES_A.read_bytes() != BASELINES_B.read_bytes():
        raise RuntimeError("D99 baseline repeats are not byte-identical")
    if BASELINES_A.read_bytes() != D98_BASELINES.read_bytes():
        raise RuntimeError("D99 and pre-change D98 baselines differ")

    population_audit = validate_population()
    rows, fields = read_table(RUN_A)
    repeat_rows, repeat_fields = read_table(RUN_B)
    baselines, baseline_fields = read_table(BASELINES_A)
    repeat_baselines, repeat_baseline_fields = read_table(BASELINES_B)
    d98_rows, d98_fields = read_table(D98_REFERENCE)
    d98_baselines, d98_baseline_fields = read_table(D98_BASELINES)
    if rows != repeat_rows or fields != repeat_fields:
        raise RuntimeError("D99 parsed policy repeats differ")
    if baselines != repeat_baselines or baseline_fields != repeat_baseline_fields:
        raise RuntimeError("D99 parsed baseline repeats differ")
    if baselines != d98_baselines or baseline_fields != d98_baseline_fields:
        raise RuntimeError("D99 and D98 parsed baselines differ")

    baseline_by_task = validate_baselines(baselines, baseline_fields)
    by_policy, grid_audit = validate_grid(rows, fields, D99_STAT_FIELDS, "D99")
    d98_by_policy, d98_grid_audit = validate_grid(
        d98_rows, d98_fields, D98_STAT_FIELDS, "D98 reference"
    )

    integrity = Counter()
    d98_integrity = Counter()
    for row in baselines:
        integrity.update(terminal_failures(row))
    for row in rows:
        integrity.update(d99_failures(row))
    for row in d98_rows:
        d98_integrity.update(d98_failures(row))
    zero_parity = parity_failures(by_policy[ZERO], baseline_by_task)
    d98_zero_parity = parity_failures(d98_by_policy[ZERO], baseline_by_task)

    summaries = {
        policy: summarize_policy(by_policy[policy], baseline_by_task) for policy in POLICIES
    }
    d40_worker_three = mean(
        int(row["own_workers"]) >= 3 for row in baseline_by_task.values()
    )
    retained_worker_three = [
        policy
        for policy in FOURS
        if summaries[policy]["worker_three_rate"] >= d40_worker_three - 0.10
    ]
    active_pairs = [
        f"pair_{index:02d}"
        for index, (one, four) in enumerate(zip(ONES, FOURS))
        if min(
            summaries[one]["changed_action_hash_rate_vs_d40"],
            summaries[four]["changed_action_hash_rate_vs_d40"],
        )
        >= 0.50
    ]
    broad_four = [
        policy
        for policy in FOURS
        if summaries[policy]["distinct_job_kinds"] >= 3
        and summaries[policy]["distinct_provenance_classes"] >= 2
    ]
    repeated_four = [
        policy
        for policy in FOURS
        if summaries[policy]["at_least_two_intervention_task_rate"] >= 0.25
    ]
    joint_four = [
        policy
        for policy in FOURS
        if summaries[policy]["joint_pair_task_rate"] >= 0.25
    ]
    four_means = [summaries[policy]["mean_margin"] for policy in FOURS]
    surface = {
        "d40_worker_three_rate": d40_worker_three,
        "four_policies_retaining_worker_three": retained_worker_three,
        "four_policies_retaining_worker_three_count": len(retained_worker_three),
        "active_matched_pairs_conservative_both_budgets": active_pairs,
        "active_matched_pair_count": len(active_pairs),
        "broad_four_policies": broad_four,
        "broad_four_policy_count": len(broad_four),
        "repeated_four_policies": repeated_four,
        "repeated_four_policy_count": len(repeated_four),
        "joint_four_policies": joint_four,
        "joint_four_policy_count": len(joint_four),
        "four_fixed_mean_margin_minimum": min(four_means),
        "four_fixed_mean_margin_maximum": max(four_means),
        "four_fixed_mean_margin_range": max(four_means) - min(four_means),
    }
    oracle, oracle_details = oracle_metrics(by_policy, d98_by_policy, baseline_by_task)

    construction_audit = {
        "illegal_macro_action_failures": 0,
        "nonfinite_feature_failures": 0,
        "reservation_or_target_collision_failures": 0,
        "final_live_own_crop_fell_failures": 0,
        "pair_preview_runtime_assertion_failures": 0,
        "catalog_runtime_assertion_failures": 0,
        "basis": (
            "both frozen evaluator runs completed; legal-action, finite-feature, pair-preview, "
            "catalog, reservation, and final-own-crop guards are runtime assertions or "
            "construction invariants in the hashed evaluator/environment"
        ),
    }
    audit = {
        "population": population_audit,
        "d99_output_fields": len(fields),
        "d98_reference_output_fields": len(d98_fields),
        "baseline_output_fields": len(baseline_fields),
        "policies": len(POLICIES),
        "tasks_per_policy": TASKS,
        "d99_rows": len(rows),
        "d98_reference_rows": len(d98_rows),
        "baseline_rows": len(baselines),
        "repeat_byte_identical": True,
        "d99_grid": grid_audit,
        "d98_reference_grid": d98_grid_audit,
        "zero_control_parity_failures": len(zero_parity),
        "d98_zero_control_parity_failures": len(d98_zero_parity),
        "integrity_failure_counts": dict(sorted(integrity.items())),
        "d98_reference_integrity_failure_counts": dict(sorted(d98_integrity.items())),
        "construction_audit": construction_audit,
    }

    integrity_gates = {
        "complete_byte_identical_129x128_d99_repeats": True,
        "byte_identical_d99_and_prechange_d98_baselines": True,
        "d99_zero_control_exact_d40_parity": not zero_parity,
        "d98_reference_zero_control_exact_d40_parity": not d98_zero_parity,
        "population_reconstructs_from_pcg64_seed_9901": population_audit[
            "reconstructs_from_pcg64_seed_9901"
        ],
        "all_one_four_weights_and_budgets_match": population_audit[
            "matched_pair_failures"
        ]
        == 0
        and grid_audit["matched_pair_policy_hash_failures"] == 0
        and grid_audit["kind_or_budget_failures"] == 0,
        "all_d99_policy_hashes_stable_and_nonzero": grid_audit[
            "policy_hash_variations"
        ]
        == 0
        and grid_audit["zero_policy_hashes"] == 0,
        "zero_d99_mechanics_integrity_failures": not integrity,
        "zero_d98_reference_integrity_failures": not d98_integrity,
        "zero_runtime_construction_failures": all(
            value == 0 for key, value in construction_audit.items() if key != "basis"
        ),
    }
    activity_gates = {
        "every_policy_crops_in_every_task": all(
            summaries[policy]["crop_rate"] == 1.0 for policy in POLICIES
        ),
        "at_least_56_four_policies_retain_worker_three": len(retained_worker_three) >= 56,
        "at_least_56_matched_pairs_change_half_actions": len(active_pairs) >= 56,
        "at_least_48_four_policies_use_three_jobs_two_provenances": len(broad_four)
        >= 48,
        "at_least_48_four_policies_repeat_in_quarter_tasks": len(repeated_four) >= 48,
        "at_least_48_four_policies_joint_in_quarter_tasks": len(joint_four) >= 48,
        "four_fixed_mean_margin_range_at_least_25": surface[
            "four_fixed_mean_margin_range"
        ]
        >= 25,
    }
    headroom_gates = {
        "four_oracle_mean_margin_gain_at_least_50": oracle[
            "four_oracle_paired_mean_margin_delta_vs_d40"
        ]
        >= 50,
        "four_oracle_strictly_improves_at_least_85pct": oracle[
            "four_oracle_strict_margin_improvement_rate_vs_d40"
        ]
        >= 0.85,
        "all_four_oracle_opponent_gains_at_least_15": oracle[
            "four_oracle_worst_opponent_family_mean_margin_delta_vs_d40"
        ]
        >= 15,
        "four_oracle_mean_own_score_nonnegative": oracle[
            "four_oracle_paired_mean_own_score_delta_vs_d40"
        ]
        >= 0,
        "four_oracle_mean_opponent_score_nonpositive": oracle[
            "four_oracle_paired_mean_opponent_score_delta_vs_d40"
        ]
        <= 0,
        "four_oracle_worker_three_rate_at_least_85pct": oracle[
            "four_oracle_worker_three_rate"
        ]
        >= 0.85,
        "four_oracle_crop_rate_exactly_100pct": oracle["four_oracle_crop_rate"] == 1.0,
        "four_oracle_at_least_10_above_one_oracle": oracle[
            "four_minus_one_oracle_mean_margin"
        ]
        >= 10,
        "four_strictly_beats_one_oracle_in_at_least_32_tasks": oracle[
            "four_oracle_strictly_beats_one_margin_tasks"
        ]
        >= 32,
        "at_least_12_four_policies_have_two_strict_wins": oracle[
            "four_policies_with_at_least_two_strict_wins"
        ]
        >= 12,
        "selected_four_rows_repeat_in_at_least_24_tasks": oracle[
            "selected_four_rows_with_at_least_two_interventions"
        ]
        >= 24,
        "selected_four_rows_joint_in_at_least_32_tasks": oracle[
            "selected_four_rows_with_joint_pair"
        ]
        >= 32,
        "selected_four_rows_span_all_jobs_two_provenances_both_seats_all_families": len(
            oracle["selected_four_job_kinds"]
        )
        == 4
        and len(oracle["selected_four_provenance_classes"]) >= 2
        and len(oracle["selected_four_seats"]) == 2
        and len(oracle["selected_four_opponent_families"]) == len(OPPONENTS),
        "d99_four_oracle_at_least_5_above_d98_reference": oracle[
            "d99_four_minus_d98_reference_mean_margin"
        ]
        >= 5,
    }
    integrity_gates = {name: bool(value) for name, value in integrity_gates.items()}
    activity_gates = {name: bool(value) for name, value in activity_gates.items()}
    headroom_gates = {name: bool(value) for name, value in headroom_gates.items()}
    gates = {**integrity_gates, **activity_gates, **headroom_gates}
    if not all(integrity_gates.values()):
        decision = "quarantine_value_and_repair_only_integrity_defects"
    elif not all(activity_gates.values()):
        decision = "close_random_pair_initialization_on_consumed_maps"
    elif not all(headroom_gates.values()):
        decision = "close_pair_aware_whole_game_use_without_learning"
    else:
        decision = "open_short_pair_action_mechanics_and_learning_signal_preflight_at_exact_d40"

    best_fixed = max(FOURS, key=lambda policy: (summaries[policy]["mean_margin"], policy))
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
            "d98_reference_binary_sha256": sha256(D98_BINARY),
            "analyzer_source_sha256": sha256(Path(__file__)),
        },
        "audit": audit,
        "surface": surface,
        "policy_summaries": summaries,
        "best_fixed_four_policy_descriptive_only": {
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
            "consumed-map pair-action function-class upper bound with a frozen D98 architecture "
            "reference only; fixed random policies and hindsight choices are unselectable, with "
            "no candidate, TestSession, submission, Arena action, or resident replacement"
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
