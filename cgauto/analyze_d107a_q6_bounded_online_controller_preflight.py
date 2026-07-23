#!/usr/bin/env python3
"""Analyze D107a's frozen bounded whole-game q6 controller preflight."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cgauto import make_d107a_q6_proposal_controller_population as generator


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d107a-q6-bounded-online-controller-preflight-protocol-2026-07-22.md"
AMENDMENT = BASE / "d107a-minimum-support-measurement-amendment-2026-07-22.md"
GENERATOR = ROOT / "cgauto" / "make_d107a_q6_proposal_controller_population.py"
RUNNER = ROOT / "rust" / "src" / "bin" / "d107_q6_proposal_controller_population.rs"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
POPULATION = BASE / "d107a-q6-proposal-controller-population.tsv"
ROWS_A = BASE / "d107a-q6-controller-population-a-9829000-9829007.tsv"
ROWS_B = BASE / "d107a-q6-controller-population-b-9829000-9829007.tsv"
BASELINES_A = BASE / "d107a-q6-controller-baselines-a-9829000-9829007.tsv"
BASELINES_B = BASE / "d107a-q6-controller-baselines-b-9829000-9829007.tsv"
SUPPORT_ROWS = BASE / "d107a-q6-zero-support-audit-9829000-9829007.tsv"
SUPPORT_BASELINES = BASE / "d107a-q6-zero-support-baselines-9829000-9829007.tsv"
OUTPUT = BASE / "d107a-q6-bounded-online-controller-preflight-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "ddf4c814dbb309e9280eba110e9a88937f4f0614280ae4b6a8cb558b6c8427b0",
    AMENDMENT: "b4be5b5d8481a60cfafc785ab9273861dab42555e4c9bf584c6b0c532ebce5b4",
    GENERATOR: "ec2d216e307c8999895d7ea5c8ac0a013bfe8c237018638c37473018a873db0f",
    RUNNER: "2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514",
    EXPERTS: "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    POPULATION: "aae1a417cce5ba76b47e461f51a5859c98891df1fba13baa4dce7d8791779d94",
    ROWS_A: "115d820e9f79efb80d794211a4e1a1aea740bfdf8656dbf6322c6f78601d26dd",
    ROWS_B: "115d820e9f79efb80d794211a4e1a1aea740bfdf8656dbf6322c6f78601d26dd",
    BASELINES_A: "513a5f47b386993d34a6e4005891043b8eac2b9f2711515c994c34e64d3cee7c",
    BASELINES_B: "513a5f47b386993d34a6e4005891043b8eac2b9f2711515c994c34e64d3cee7c",
    SUPPORT_ROWS: "06d53fd74fb6d602d02874e6d9ddab0b99e663051e6de855cff02247ef21ba69",
    SUPPORT_BASELINES: "513a5f47b386993d34a6e4005891043b8eac2b9f2711515c994c34e64d3cee7c",
}
ORIGINAL_RUNNER_HASH = "b15214ee87ca925cb43b565f31815f169d6e18c4105abbb4d776a3cc687e860a"
MAP_START = 9_829_000
MAP_STOP = 9_829_008
TASKS = 128
POLICIES = 129
OPPONENTS = (
    "resident",
    "compact_gold",
    "gold_adaptive",
    "silver_boss",
    "legend_balanced",
    "norx_native_three",
    "script_boss",
    "mybot",
)
TASK_FIELDS = ("map_seed", "seat", "opponent")
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
JOB_FIELDS = ("concrete_fell", "concrete_harvest", "concrete_renew", "concrete_mine")
OWNER_FIELDS = ("owner_natural", "owner_own", "owner_opponent", "owner_ambiguous")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def expected_policies() -> set[str]:
    return {"zero_control"} | {
        f"{kind}_{index:02d}"
        for kind in ("one", "four")
        for index in range(64)
    }


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def gate(value, threshold: str, passed: bool) -> dict:
    return {"value": value, "threshold": threshold, "pass": bool(passed)}


def counter_violations(rows: list[dict[str, str]]) -> list[str]:
    violations = []
    for row in rows:
        label = f"{row['policy']}:{row['map_seed']}:{row['seat']}:{row['opponent']}"
        eligible = int(row["eligible_batches"])
        interventions = int(row["intervention_batches"])
        joint = int(row["joint_batches"])
        first = int(row["single_first_batches"])
        second = int(row["single_second_batches"])
        nonkeep = int(row["nonkeep_assignments"])
        proposals = int(row["proposal_occurrences"])
        unique = int(row["unique_proposals"])
        supporters = int(row["supporter_occurrences"])
        budget = int(row["budget"])
        jobs = sum(int(row[field]) for field in JOB_FIELDS)
        owners = sum(int(row[field]) for field in OWNER_FIELDS)
        valid = (
            interventions <= budget
            and joint + first + second == interventions
            and nonkeep == 2 * joint + first + second
            and jobs == nonkeep
            and owners <= nonkeep
            and proposals == 64 * eligible
            and supporters == proposals
            and unique >= eligible
            and (row["kind"] != "zero" or interventions == 0)
        )
        if not valid:
            violations.append(label)
    return violations


def choose_oracle(
    baseline: dict[str, str], rows: list[dict[str, str]]
) -> tuple[str, dict[str, str]]:
    candidates = [("control", baseline)] + [(row["policy"], row) for row in rows]
    return min(candidates, key=lambda item: (-int(item[1]["margin"]), item[0]))


def analyze() -> dict:
    actual_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES}
    hash_integrity = all(sha256(path) == expected for path, expected in EXPECTED_HASHES.items())
    generated = generator.population()
    generator.validate(generated)
    population_reconstructs = POPULATION.read_text() == generator.render(generated)

    rows_a, row_header = read_table(ROWS_A)
    rows_b, row_header_b = read_table(ROWS_B)
    baselines_a, baseline_header = read_table(BASELINES_A)
    baselines_b, baseline_header_b = read_table(BASELINES_B)
    support_rows, support_header = read_table(SUPPORT_ROWS)
    support_baselines, support_baseline_header = read_table(SUPPORT_BASELINES)

    tasks = expected_tasks()
    policies = expected_policies()
    grid_a = Counter((row["policy"], task_key(row)) for row in rows_a)
    complete_grid = (
        len(rows_a) == POLICIES * TASKS
        and len(rows_b) == POLICIES * TASKS
        and len(baselines_a) == TASKS
        and len(baselines_b) == TASKS
        and set(grid_a) == {(policy, task) for policy in policies for task in tasks}
        and all(count == 1 for count in grid_a.values())
        and {task_key(row) for row in baselines_a} == tasks
        and row_header == row_header_b
        and baseline_header == baseline_header_b
    )
    row_byte_identity = ROWS_A.read_bytes() == ROWS_B.read_bytes()
    baseline_byte_identity = BASELINES_A.read_bytes() == BASELINES_B.read_bytes()

    baseline_by_task = {task_key(row): row for row in baselines_a}
    zero_rows = [row for row in rows_a if row["policy"] == "zero_control"]
    baseline_value_fields = baseline_header[3:]
    zero_exact = len(zero_rows) == TASKS and all(
        all(row[field] == baseline_by_task[task_key(row)][field] for field in baseline_value_fields)
        for row in zero_rows
    )

    support_by_task = {task_key(row): row for row in support_rows}
    original_zero_by_task = {task_key(row): row for row in zero_rows}
    shared_support_fields = [field for field in row_header if field != "minimum_unique_proposals"]
    support_exact = (
        len(support_rows) == TASKS
        and set(support_by_task) == tasks
        and support_baseline_header == baseline_header
        and SUPPORT_BASELINES.read_bytes() == BASELINES_A.read_bytes()
        and set(row_header).issubset(set(support_header))
        and all(
            all(support_by_task[task][field] == original_zero_by_task[task][field]
                for field in shared_support_fields)
            for task in tasks
        )
    )

    finite = all(
        all(math.isfinite(float(row[field])) for field in FLOAT_FIELDS) for row in rows_a
    )
    maximum_reward_error = max(abs(float(row["reward_identity_error"])) for row in rows_a)
    mechanics_failures = sum(
        int(row[field])
        for row in rows_a
        for field in ("invalid_direct_commands", "provenance_failures", "deposit_prediction_failures")
    )
    violations = counter_violations(rows_a)
    baseline_crop_rate = rate(
        sum(int(row["own_created_crops"]) > 0 for row in baselines_a), len(baselines_a)
    )
    baseline_worker_rate = rate(sum(int(row["own_workers"]) >= 3 for row in baselines_a), len(baselines_a))
    kind_rows = {kind: [row for row in rows_a if row["kind"] == kind] for kind in ("one", "four")}
    crop_rates = {
        kind: rate(sum(int(row["own_created_crops"]) > 0 for row in values), len(values))
        for kind, values in kind_rows.items()
    }
    worker_rates = {
        kind: rate(sum(int(row["own_workers"]) >= 3 for row in values), len(values))
        for kind, values in kind_rows.items()
    }
    safety = (
        baseline_crop_rate == 1.0
        and all(value == 1.0 for value in crop_rates.values())
        and all(value >= baseline_worker_rate - 0.05 for value in worker_rates.values())
    )
    integrity_gates = {
        "source_hashes_and_population": gate(
            hash_integrity and population_reconstructs, "all immutable hashes and exact generator reconstruction", hash_integrity and population_reconstructs
        ),
        "complete_repeated_grid": gate(
            {"rows": len(rows_a), "baselines": len(baselines_a), "row_bytes_equal": row_byte_identity,
             "baseline_bytes_equal": baseline_byte_identity},
            "16,512 rows, 128 baselines, complete grids, byte-identical repeats",
            complete_grid and row_byte_identity and baseline_byte_identity,
        ),
        "zero_exact_d40": gate(zero_exact, "all 128 terminal/action fields exact", zero_exact),
        "finite_safe_mechanics": gate(
            {"finite": finite, "maximum_reward_identity_error": maximum_reward_error,
             "mechanics_failures": mechanics_failures},
            "finite; reward error <=1e-5; zero mechanical failures",
            finite and maximum_reward_error <= 1e-5 and mechanics_failures == 0,
        ),
        "counter_reconciliation": gate(len(violations), "zero violations", not violations),
        "minimum_support_amendment": gate(support_exact, "128 rows and all shared fields/baselines exact", support_exact),
        "crop_and_worker_safety": gate(
            {"baseline_crop_rate": baseline_crop_rate, "one_crop_rate": crop_rates["one"],
             "four_crop_rate": crop_rates["four"], "baseline_worker3_rate": baseline_worker_rate,
             "one_worker3_rate": worker_rates["one"], "four_worker3_rate": worker_rates["four"]},
            "100% crops and worker3 no more than 5pp below D40",
            safety,
        ),
    }
    integrity_pass = all(item["pass"] for item in integrity_gates.values())

    eligible_zero = [row for row in support_rows if int(row["eligible_batches"]) > 0]
    eligible_tasks = len(eligible_zero)
    total_boundaries = sum(int(row["eligible_batches"]) for row in support_rows)
    total_unique_noncontrol = sum(
        int(row["unique_proposals"]) - int(row["eligible_batches"]) for row in support_rows
    )
    mean_unique_noncontrol = rate(total_unique_noncontrol, total_boundaries)
    minimum_unique_noncontrol = min(
        (int(row["minimum_unique_proposals"]) - 1 for row in eligible_zero), default=0
    )
    mean_expert_occurrences = rate(
        sum(int(row["proposal_occurrences"]) for row in support_rows), total_boundaries
    )

    four_by_policy = defaultdict(list)
    one_by_policy = defaultdict(list)
    for row in kind_rows["four"]:
        four_by_policy[row["policy"]].append(row)
    for row in kind_rows["one"]:
        one_by_policy[row["policy"]].append(row)
    medium_controllers = 0
    active_controllers = 0
    repeated_controllers = 0
    more_than_one_pairs = 0
    for index in range(64):
        four = four_by_policy[f"four_{index:02d}"]
        one = one_by_policy[f"one_{index:02d}"]
        active_tasks = sum(int(row["intervention_batches"]) > 0 for row in four)
        repeated_tasks = sum(int(row["intervention_batches"]) >= 2 for row in four)
        active_controllers += active_tasks > 0
        medium_controllers += 0.10 <= active_tasks / TASKS <= 0.90
        repeated_controllers += repeated_tasks / TASKS >= 0.10
        more_than_one_pairs += sum(int(row["intervention_batches"]) for row in four) > sum(
            int(row["intervention_batches"]) for row in one
        )
    selected_four = [row for row in kind_rows["four"] if int(row["intervention_batches"]) > 0]
    selected_jobs = {field for field in JOB_FIELDS if sum(int(row[field]) for row in selected_four) > 0}
    selected_owners = {
        field for field in OWNER_FIELDS[:3] if sum(int(row[field]) for row in selected_four) > 0
    }
    selected_seats = {int(row["seat"]) for row in selected_four}
    selected_opponents = {row["opponent"] for row in selected_four}
    joint_count = sum(int(row["joint_batches"]) for row in selected_four)
    breadth = (
        joint_count > 0
        and len(selected_jobs) == 4
        and len(selected_owners) == 3
        and selected_seats == {0, 1}
        and selected_opponents == set(OPPONENTS)
    )
    activity_gates = {
        "eligible_tasks": gate(eligible_tasks, ">=110/128", eligible_tasks >= 110),
        "proposal_support": gate(
            {"eligible_boundaries": total_boundaries, "mean_unique_noncontrol": mean_unique_noncontrol,
             "minimum_unique_noncontrol": minimum_unique_noncontrol,
             "mean_expert_occurrences": mean_expert_occurrences},
            "mean>=14, min>=6, expert mean=64",
            mean_unique_noncontrol >= 14 and minimum_unique_noncontrol >= 6
            and mean_expert_occurrences == 64,
        ),
        "controller_activity": gate(
            {"medium": medium_controllers, "ever_active": active_controllers},
            ">=32 medium and >=48 ever active",
            medium_controllers >= 32 and active_controllers >= 48,
        ),
        "repeated_activity": gate(repeated_controllers, ">=24 controllers", repeated_controllers >= 24),
        "matched_budget_separation": gate(more_than_one_pairs, ">=24 pairs", more_than_one_pairs >= 24),
        "selection_breadth": gate(
            {"joint_batches": joint_count, "jobs": sorted(selected_jobs), "owners": sorted(selected_owners),
             "seats": sorted(selected_seats), "opponents": sorted(selected_opponents)},
            "joint, 4 jobs, 3 provenance, 2 seats, 8 opponents",
            breadth,
        ),
    }
    activity_pass = integrity_pass and all(item["pass"] for item in activity_gates.values())

    result = {
        "experiment": "D107a",
        "original_runner_hash": ORIGINAL_RUNNER_HASH,
        "hashes": actual_hashes,
        "output_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (ROWS_A, ROWS_B, BASELINES_A, BASELINES_B, SUPPORT_ROWS, SUPPORT_BASELINES)
        },
        "integrity": {"pass": integrity_pass, "gates": integrity_gates, "violations": violations[:20]},
        "activity": {"pass": activity_pass, "gates": activity_gates},
        "headroom": {"opened": False},
    }
    if not activity_pass:
        result["decision"] = "repair_integrity" if not integrity_pass else "close_d107a_activity"
        return result

    rows_by_kind_task = {
        kind: defaultdict(list) for kind in ("one", "four")
    }
    for kind in ("one", "four"):
        for row in kind_rows[kind]:
            rows_by_kind_task[kind][task_key(row)].append(row)
    oracle = {kind: {} for kind in ("one", "four")}
    for kind in ("one", "four"):
        for task in sorted(tasks):
            oracle[kind][task] = choose_oracle(
                baseline_by_task[task], rows_by_kind_task[kind][task]
            )
    four_deltas = []
    one_deltas = []
    repeated_deltas = []
    own_deltas = []
    opponent_deltas = []
    family_deltas = defaultdict(list)
    winners = []
    for task in sorted(tasks):
        baseline = baseline_by_task[task]
        one_label, one_row = oracle["one"][task]
        four_label, four_row = oracle["four"][task]
        one_delta = int(one_row["margin"]) - int(baseline["margin"])
        four_delta = int(four_row["margin"]) - int(baseline["margin"])
        one_deltas.append(one_delta)
        four_deltas.append(four_delta)
        repeated_deltas.append(int(four_row["margin"]) - int(one_row["margin"]))
        own_deltas.append(int(four_row["own_score"]) - int(baseline["own_score"]))
        opponent_deltas.append(int(four_row["opponent_score"]) - int(baseline["opponent_score"]))
        family_deltas[task[2]].append(four_delta)
        if four_label != "control":
            winners.append(four_row)
    family_means = {family: mean(values) for family, values in sorted(family_deltas.items())}
    oracle_crop_rate = rate(sum(int(row["own_created_crops"]) > 0 for row in winners), len(winners)) if winners else 1.0
    # Control winners also create crops and reach workers according to their baseline rows.
    chosen_four_rows = [oracle["four"][task][1] for task in sorted(tasks)]
    oracle_crop_rate = rate(sum(int(row["own_created_crops"]) > 0 for row in chosen_four_rows), TASKS)
    oracle_worker_rate = rate(sum(int(row["own_workers"]) >= 3 for row in chosen_four_rows), TASKS)
    winner_policies = {row["policy"] for row in winners}
    winner_seats = {int(row["seat"]) for row in winners}
    winner_opponents = {row["opponent"] for row in winners}
    winner_jobs = {field for field in JOB_FIELDS if sum(int(row[field]) for row in winners) > 0}
    winner_owners = {field for field in OWNER_FIELDS if sum(int(row[field]) for row in winners) > 0}
    winner_joint = sum(int(row["joint_batches"]) for row in winners)
    winner_breadth = (
        len(winner_policies) >= 16 and winner_seats == {0, 1}
        and winner_opponents == set(OPPONENTS) and winner_joint > 0
        and len(winner_jobs) >= 3 and len(winner_owners) >= 2
    )
    headroom_gates = {
        "four_oracle_gain": gate(
            {"mean": mean(four_deltas), "strict_rate": rate(sum(value > 0 for value in four_deltas), TASKS)},
            "mean>=20 and strict>=70%",
            mean(four_deltas) >= 20 and rate(sum(value > 0 for value in four_deltas), TASKS) >= 0.70,
        ),
        "family_floor": gate(family_means, "every family>=8", min(family_means.values()) >= 8),
        "score_decomposition": gate(
            {"own_delta": mean(own_deltas), "opponent_delta": mean(opponent_deltas)},
            "own>=0 and opponent<=0", mean(own_deltas) >= 0 and mean(opponent_deltas) <= 0,
        ),
        "repeated_increment": gate(
            {"mean": mean(repeated_deltas), "strict_rate": rate(sum(value > 0 for value in repeated_deltas), TASKS)},
            "mean>=3 and strict>=20%",
            mean(repeated_deltas) >= 3 and rate(sum(value > 0 for value in repeated_deltas), TASKS) >= 0.20,
        ),
        "oracle_safety": gate(
            {"crop_rate": oracle_crop_rate, "worker3_rate": oracle_worker_rate},
            "100% crops and worker3 within 5pp of D40",
            oracle_crop_rate == 1.0 and oracle_worker_rate >= baseline_worker_rate - 0.05,
        ),
        "winner_breadth": gate(
            {"controllers": len(winner_policies), "seats": sorted(winner_seats),
             "opponents": sorted(winner_opponents), "joint_batches": winner_joint,
             "jobs": sorted(winner_jobs), "owners": sorted(winner_owners)},
            ">=16 controllers, 2 seats, 8 opponents, joint, >=3 jobs, >=2 provenance",
            winner_breadth,
        ),
    }
    headroom_pass = all(item["pass"] for item in headroom_gates.values())
    result["headroom"] = {
        "opened": True,
        "pass": headroom_pass,
        "gates": headroom_gates,
        "one_oracle_mean_gain": mean(one_deltas),
    }
    result["decision"] = "open_d108a_recurrent_masked_controller" if headroom_pass else "close_d107a_headroom"
    return result


def main() -> int:
    result = analyze()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
