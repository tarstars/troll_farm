#!/usr/bin/env python3
"""Validate the frozen D97 target-aware joint concrete-job continuations."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d97a-d40-joint-concrete-job-continuation-protocol-2026-07-21.md"
LOCK = ANALYSIS / "d97a-d40-joint-concrete-job-manifest-lock-2026-07-21.md"
MANIFEST = ANALYSIS / "d97a-d40-joint-concrete-job-manifest-9820000-9820015.tsv"
ARMS_A = ANALYSIS / "d97a-d40-joint-concrete-job-arms-a-9820000-9820015.tsv"
ARMS_B = ANALYSIS / "d97a-d40-joint-concrete-job-arms-b-9820000-9820015.tsv"
BASELINES_A = ANALYSIS / "d97a-d40-joint-concrete-job-baselines-a-9820000-9820015.tsv"
BASELINES_B = ANALYSIS / "d97a-d40-joint-concrete-job-baselines-b-9820000-9820015.tsv"
GENERATOR_SOURCE = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_manifest.rs"
EVALUATOR_SOURCE = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_continuations.rs"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
OUTPUT = ANALYSIS / "d97a-d40-joint-concrete-job-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "157a18d39ba49bf7a7b76080a0f16e8df3c622d93d6f98a22127f779ee5dd0e3",
    LOCK: "e9d7907d1a9d3c5aa114fb705423ae09f83071fab3bd424fa153c2b9ff301903",
    MANIFEST: "ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e",
    GENERATOR_SOURCE: "f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23",
    EVALUATOR_SOURCE: "e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4",
    ENV_SOURCE: "19d54cc89051c43a4a002c595b52a6403075581125d31e4fb152f6fb3cb70ede",
    PRIOR_SOURCE: "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62",
}

MAP_START = 9_820_000
MAP_STOP = 9_820_016
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
TASKS = (MAP_STOP - MAP_START) * 2 * len(OPPONENTS)
EXPECTED_ROOTS = 240
EXPECTED_ARMS = 12_483
EXPECTED_KINDS = {
    "control": 240,
    "single_first": 1_741,
    "single_second": 1_160,
    "joint": 9_342,
}
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


def manifest_support(rows: list[dict[str, str]]) -> tuple[dict, dict[str, dict[str, str]]]:
    if len(rows) != EXPECTED_ARMS:
        raise RuntimeError(f"D97 manifest arm count mismatch: {len(rows)}")
    by_arm = {row["arm_id"]: row for row in rows}
    if len(by_arm) != len(rows):
        raise RuntimeError("D97 duplicate manifest arm id")
    by_root = defaultdict(list)
    for row in rows:
        by_root[row["root_id"]].append(row)
    if len(by_root) != EXPECTED_ROOTS:
        raise RuntimeError("D97 manifest root count mismatch")
    kinds = Counter(row["arm_kind"] for row in rows)
    controls = {
        root: sum(row["arm_kind"] == "control" for row in root_rows)
        for root, root_rows in by_root.items()
    }
    root_tasks = {}
    opponent_roots = Counter()
    seat_roots = Counter()
    fell_and_renewable = 0
    mine_roots = 0
    owners_by_seat = Counter()
    final_own_fells = 0
    for root, root_rows in by_root.items():
        tasks = {task_key(row) for row in root_rows}
        if len(tasks) != 1:
            raise RuntimeError(f"D97 root crosses tasks: {root}")
        key = tasks.pop()
        if key in root_tasks:
            raise RuntimeError(f"D97 multiple roots in one task: {key}")
        root_tasks[key] = root
        opponent_roots[key[2]] += 1
        seat_roots[str(key[1])] += 1
        classes = {
            value
            for row in root_rows
            for value in (row["first_class"], row["second_class"])
        }
        fell = any(value.startswith("fell:") for value in classes)
        renewable = any(
            value.startswith("harvest:") or value.startswith("renew:")
            for value in classes
        )
        fell_and_renewable += fell and renewable
        mine_roots += "mine" in classes
        for row in root_rows:
            for prefix in ("first", "second"):
                owner = row[f"{prefix}_owner"]
                if owner != "none":
                    owners_by_seat[(row["seat"], owner)] += 1
                final_own_fells += (
                    row[f"{prefix}_class"] != "keep"
                    and row[f"{prefix}_job_kind"] == "fell"
                    and owner == "own"
                    and int(row["live_own_crops"]) <= 1
                )
    observed_owners = {owner for _, owner in owners_by_seat}
    owners_both_seats = all(
        owners_by_seat[(seat, owner)] > 0
        for owner in observed_owners
        for seat in ("0", "1")
    )
    support = {
        "roots": len(by_root),
        "arms": len(rows),
        "arm_kind_counts": dict(sorted(kinds.items())),
        "single_arms": kinds["single_first"] + kinds["single_second"],
        "joint_arms": kinds["joint"],
        "bad_control_counts": sum(value != 1 for value in controls.values()),
        "opponent_root_counts": dict(sorted(opponent_roots.items())),
        "minimum_opponent_roots": min(opponent_roots.values()),
        "seat_root_counts": dict(sorted(seat_roots.items())),
        "roots_with_fell_and_renewable": fell_and_renewable,
        "fell_and_renewable_root_rate": fell_and_renewable / len(by_root),
        "roots_with_mine": mine_roots,
        "mine_root_rate": mine_roots / len(by_root),
        "observed_provenance_classes": sorted(observed_owners),
        "observed_provenance_in_both_seats": owners_both_seats,
        "final_own_crop_fell_catalog_entries": final_own_fells,
        "root_task_count": len(root_tasks),
    }
    return support, by_arm


def validate_outputs(
    manifest_by_arm: dict[str, dict[str, str]],
    arms: list[dict[str, str]],
    arm_fields: list[str],
    baselines: list[dict[str, str]],
    baseline_fields: list[str],
) -> tuple[dict, dict, dict]:
    if len(arms) != EXPECTED_ARMS or len(baselines) != TASKS:
        raise RuntimeError("D97 output matrix size mismatch")
    if not set(TERMINAL_FIELDS).issubset(arm_fields) or not set(TERMINAL_FIELDS).issubset(
        baseline_fields
    ):
        raise RuntimeError("D97 terminal schema mismatch")
    baseline_by_task = {task_key(row): row for row in baselines}
    if len(baseline_by_task) != TASKS or set(baseline_by_task) != expected_tasks():
        raise RuntimeError("D97 baseline task coverage mismatch")
    arm_by_id = {row["arm_id"]: row for row in arms}
    if len(arm_by_id) != EXPECTED_ARMS or set(arm_by_id) != set(manifest_by_arm):
        raise RuntimeError("D97 arm identity coverage mismatch")
    mirror_fields = (
        "map_seed",
        "seat",
        "opponent",
        "root_id",
        "arm_kind",
        "arm_id",
        "first_label",
        "first_class",
        "first_action",
        "second_label",
        "second_class",
        "second_action",
    )
    mirror_failures = []
    for arm_id, row in arm_by_id.items():
        manifest = manifest_by_arm[arm_id]
        for field in mirror_fields:
            if row[field] != manifest[field]:
                mirror_failures.append((arm_id, field, row[field], manifest[field]))
    integrity = Counter()
    for row in [*baselines, *arms]:
        floats = [float(row[field]) for field in FLOAT_FIELDS]
        if any(not math.isfinite(value) for value in floats):
            integrity["nonfinite_terminal"] += 1
        if float(row["reward_identity_error"]) > 1.0e-4:
            integrity["reward_identity"] += 1
        if int(row["margin"]) != int(row["own_score"]) - int(row["opponent_score"]):
            integrity["margin_identity"] += 1
        if sum(int(row[field]) for field in ACTION_PLANES) != int(row["selected_decisions"]):
            integrity["action_plane_accounting"] += 1
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        ):
            if int(row[field]):
                integrity[field] += 1
        if int(row["own_workers"]) > 3:
            integrity["worker_cap"] += 1
    controls = [row for row in arms if row["arm_kind"] == "control"]
    control_failures = []
    for row in controls:
        baseline = baseline_by_task[task_key(row)]
        for field in TERMINAL_FIELDS:
            if row[field] != baseline[field]:
                control_failures.append((row["arm_id"], field, row[field], baseline[field]))
    return (
        {
            "mirror_failures": len(mirror_failures),
            "integrity_failure_counts": dict(sorted(integrity.items())),
            "control_parity_failures": len(control_failures),
        },
        arm_by_id,
        baseline_by_task,
    )


def nonteacher_actions(row: dict[str, str]) -> int:
    return {"control": 0, "single_first": 1, "single_second": 1, "joint": 2}[
        row["arm_kind"]
    ]


def select(rows: list[dict[str, str]]) -> dict[str, str]:
    return min(
        rows,
        key=lambda row: (
            -int(row["margin"]),
            -int(row["own_score"]),
            int(row["opponent_score"]),
            nonteacher_actions(row),
            row["arm_id"],
        ),
    )


def oracle_metrics(
    manifest_by_arm: dict[str, dict[str, str]],
    arms: list[dict[str, str]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict]]:
    by_task = defaultdict(list)
    for row in arms:
        by_task[task_key(row)].append(row)
    margin_deltas = []
    own_deltas = []
    opponent_deltas = []
    family_deltas = defaultdict(list)
    selected_workers_three = []
    selected_crops = []
    baseline_workers_three = []
    single_margin_deltas = []
    strict_root_improvements = 0
    incremental_root_deltas = []
    joint_beats_single = 0
    role_tuples = Counter()
    selected_jobs = set()
    selected_owners = set()
    selected_opponents = set()
    selected_role_pairs = set()
    selected_kind_counts = Counter()
    details = []
    for key in sorted(expected_tasks()):
        baseline = baselines[key]
        baseline_workers_three.append(int(baseline["own_workers"]) >= 3)
        task_rows = by_task.get(key, [])
        if task_rows:
            control = next(row for row in task_rows if row["arm_kind"] == "control")
            single = select([row for row in task_rows if row["arm_kind"] != "joint"])
            joint = select(
                [row for row in task_rows if row["arm_kind"] in ("control", "joint")]
            )
            assert all(control[field] == baseline[field] for field in TERMINAL_FIELDS)
            delta = int(joint["margin"]) - int(baseline["margin"])
            strict_root_improvements += delta > 0
            incremental = int(joint["margin"]) - int(single["margin"])
            incremental_root_deltas.append(incremental)
            beats_single = int(joint["margin"]) > int(single["margin"])
            joint_beats_single += beats_single
            if joint["arm_kind"] == "joint":
                manifest = manifest_by_arm[joint["arm_id"]]
                pair = (joint["first_class"], joint["second_class"])
                role_tuples[" / ".join(pair)] += 1
                selected_role_pairs.add(pair)
                selected_jobs.update(
                    (manifest["first_job_kind"], manifest["second_job_kind"])
                )
                selected_owners.update(
                    owner
                    for owner in (manifest["first_owner"], manifest["second_owner"])
                    if owner != "none"
                )
                selected_opponents.add(key[2])
        else:
            joint = baseline
            single = baseline
            delta = 0
            incremental = None
            beats_single = False
        single_delta = int(single["margin"]) - int(baseline["margin"])
        own_delta = int(joint["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(joint["opponent_score"]) - int(baseline["opponent_score"])
        margin_deltas.append(delta)
        single_margin_deltas.append(single_delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        family_deltas[key[2]].append(delta)
        selected_workers_three.append(int(joint["own_workers"]) >= 3)
        selected_crops.append(int(joint["own_created_crops"]) > 0)
        selected_kind_counts[joint.get("arm_kind", "no_root_d40")] += 1
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "root": bool(task_rows),
                "selected_arm": joint.get("arm_id", "no_root_d40"),
                "selected_kind": joint.get("arm_kind", "no_root_d40"),
                "margin_delta_vs_d40": delta,
                "incremental_margin_vs_best_single": incremental,
                "strictly_beats_best_single": beats_single,
            }
        )
    family_means = {opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS}
    reversed_order_present = any(
        left != right and (right, left) in selected_role_pairs
        for left, right in selected_role_pairs
    )
    metrics = {
        "tasks": TASKS,
        "eligible_roots": len(by_task),
        "paired_mean_margin_delta_vs_d40_all_tasks": mean(margin_deltas),
        "best_single_mean_margin_delta_vs_d40_all_tasks": mean(
            single_margin_deltas
        ),
        "best_single_strict_improvements": sum(
            value > 0 for value in single_margin_deltas
        ),
        "paired_mean_own_score_delta_vs_d40_all_tasks": mean(own_deltas),
        "paired_mean_opponent_score_delta_vs_d40_all_tasks": mean(opponent_deltas),
        "strict_root_improvements": strict_root_improvements,
        "strict_root_improvement_rate": strict_root_improvements / len(by_task),
        "opponent_family_mean_margin_deltas_all_tasks": family_means,
        "worst_opponent_family_mean_margin_delta": min(family_means.values()),
        "baseline_worker_three_rate": mean(baseline_workers_three),
        "oracle_worker_three_rate": mean(selected_workers_three),
        "oracle_crop_rate": mean(selected_crops),
        "mean_incremental_margin_vs_best_single_eligible_roots": mean(
            incremental_root_deltas
        ),
        "joint_strictly_beats_best_single_roots": joint_beats_single,
        "joint_strictly_beats_best_single_rate": joint_beats_single / len(by_task),
        "joint_vs_best_single_improvements": sum(
            value > 0 for value in incremental_root_deltas
        ),
        "joint_vs_best_single_ties": sum(
            value == 0 for value in incremental_root_deltas
        ),
        "joint_vs_best_single_regressions": sum(
            value < 0 for value in incremental_root_deltas
        ),
        "selected_kind_counts": dict(sorted(selected_kind_counts.items())),
        "selected_joint_role_tuple_counts": dict(sorted(role_tuples.items())),
        "joint_role_tuples_with_at_least_ten_wins": sum(
            count >= 10 for count in role_tuples.values()
        ),
        "selected_joint_job_kinds": sorted(selected_jobs),
        "selected_joint_provenance_classes": sorted(selected_owners),
        "selected_joint_opponent_families": sorted(selected_opponents),
        "selected_joint_reversed_role_order_present": reversed_order_present,
    }
    return metrics, details


def main() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D97 prerequisite missing or changed: {path}")
    for path in (ARMS_A, ARMS_B, BASELINES_A, BASELINES_B):
        if not path.exists():
            raise SystemExit("missing D97 repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D97 result")
    if ARMS_A.read_bytes() != ARMS_B.read_bytes():
        raise RuntimeError("D97 arm repeats are not byte-identical")
    if BASELINES_A.read_bytes() != BASELINES_B.read_bytes():
        raise RuntimeError("D97 baseline repeats are not byte-identical")

    manifest, manifest_fields = read_table(MANIFEST)
    support, manifest_by_arm = manifest_support(manifest)
    arms, arm_fields = read_table(ARMS_A)
    baselines, baseline_fields = read_table(BASELINES_A)
    audit, arm_by_id, baseline_by_task = validate_outputs(
        manifest_by_arm, arms, arm_fields, baselines, baseline_fields
    )
    oracle, details = oracle_metrics(manifest_by_arm, arms, baseline_by_task)
    support_gates = {
        "at_least_220_roots": support["roots"] >= 220,
        "exactly_one_control_per_root": support["bad_control_counts"] == 0,
        "at_least_5000_joint_arms": support["joint_arms"] >= 5_000,
        "at_least_1000_single_arms": support["single_arms"] >= 1_000,
        "at_least_24_roots_each_opponent": support["minimum_opponent_roots"] >= 24,
        "both_seats_have_roots": all(
            support["seat_root_counts"].get(str(seat), 0) > 0 for seat in range(2)
        ),
        "fell_and_renewable_in_at_least_90pct_roots": support[
            "fell_and_renewable_root_rate"
        ]
        >= 0.90,
        "mine_in_at_least_50pct_roots": support["mine_root_rate"] >= 0.50,
        "observed_provenance_in_both_seats": support[
            "observed_provenance_in_both_seats"
        ],
    }
    value_gates = {
        "joint_oracle_mean_margin_gain_at_least_15": oracle[
            "paired_mean_margin_delta_vs_d40_all_tasks"
        ]
        >= 15,
        "joint_oracle_strictly_improves_at_least_55pct_roots": oracle[
            "strict_root_improvement_rate"
        ]
        >= 0.55,
        "all_opponent_family_mean_gains_at_least_3": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 3,
        "joint_oracle_mean_own_score_nonnegative": oracle[
            "paired_mean_own_score_delta_vs_d40_all_tasks"
        ]
        >= 0,
        "joint_oracle_mean_opponent_score_nonpositive": oracle[
            "paired_mean_opponent_score_delta_vs_d40_all_tasks"
        ]
        <= 0,
        "joint_oracle_crop_rate_exactly_100pct": oracle["oracle_crop_rate"] == 1.0,
        "joint_oracle_worker_three_within_5pct_d40": oracle[
            "oracle_worker_three_rate"
        ]
        >= oracle["baseline_worker_three_rate"] - 0.05,
        "joint_oracle_at_least_5_above_best_single": oracle[
            "mean_incremental_margin_vs_best_single_eligible_roots"
        ]
        >= 5,
        "joint_strictly_beats_single_in_at_least_25pct_roots": oracle[
            "joint_strictly_beats_best_single_rate"
        ]
        >= 0.25,
        "two_role_tuples_have_at_least_ten_joint_wins": oracle[
            "joint_role_tuples_with_at_least_ten_wins"
        ]
        >= 2,
        "selected_joint_winner_breadth": len(oracle["selected_joint_job_kinds"]) >= 3
        and len(oracle["selected_joint_provenance_classes"]) >= 2
        and oracle["selected_joint_reversed_role_order_present"]
        and len(oracle["selected_joint_opponent_families"]) == len(OPPONENTS),
    }
    gates = {
        "byte_identical_arm_and_baseline_repeats": True,
        "exact_manifest_output_mirror": audit["mirror_failures"] == 0,
        "zero_integrity_failures": not audit["integrity_failure_counts"],
        "exact_control_d40_parity": audit["control_parity_failures"] == 0,
        "zero_final_own_crop_fell_catalog_entries": support[
            "final_own_crop_fell_catalog_entries"
        ]
        == 0,
        **support_gates,
        **value_gates,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "lock": str(LOCK),
            "lock_sha256": sha256(LOCK),
            "manifest": str(MANIFEST),
            "manifest_sha256": sha256(MANIFEST),
            "arms_a_sha256": sha256(ARMS_A),
            "arms_b_sha256": sha256(ARMS_B),
            "baselines_a_sha256": sha256(BASELINES_A),
            "baselines_b_sha256": sha256(BASELINES_B),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
            "evaluator_source_sha256": sha256(EVALUATOR_SOURCE),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "analyzer_source_sha256": sha256(Path(__file__)),
        },
        "audit": {
            "manifest_fields": len(manifest_fields),
            "arm_output_fields": len(arm_fields),
            "baseline_output_fields": len(baseline_fields),
            "arms": len(arm_by_id),
            "baselines": len(baseline_by_task),
            "repeat_byte_identical": True,
            **audit,
        },
        "support": support,
        "oracle": oracle,
        "oracle_details": details,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": (
            "one-batch local concrete-assignment upper bound only; no selector, learner, "
            "candidate, TestSession, submission, Arena action, or resident replacement"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "audit": report["audit"],
                "support": support,
                "oracle": oracle,
                "gates": gates,
                "pass": report["pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
