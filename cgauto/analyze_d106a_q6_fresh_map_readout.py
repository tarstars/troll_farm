#!/usr/bin/env python3
"""Analyze D106a's fresh q6 proposal headroom and held ridge readout."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.analyze_d97a_joint_concrete_jobs import (  # noqa: E402
    ACTION_PLANES,
    FLOAT_FIELDS,
    OPPONENTS,
    TERMINAL_FIELDS,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d106a-q6-fresh-map-proposal-readout-protocol-2026-07-22.md"
SELECTOR = ROOT / "cgauto" / "select_d106a_q6_precision.py"
UNION_BUILDER = ROOT / "cgauto" / "make_d105b_proposal_union_manifest.py"
ADAPTER = ROOT / "cgauto" / "d105b_d104_cardinality_adapter.py"
MANIFEST_RUNNER = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_manifest.rs"
PROPOSAL_RUNNER = ROOT / "rust" / "src" / "bin" / "d104_d98_expert_proposal_coverage.rs"
CONTINUATION_RUNNER = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_continuations.rs"
POPULATION = BASE / "d105a-q6-expert-population.tsv"
MANIFEST = BASE / "d106a-full-d97-manifest-9827000-9827015.tsv"
PROPOSALS = BASE / "d106a-q6-proposals-9827000-9827015.tsv"
UNION = BASE / "d106a-q6-union-manifest-9827000-9827015.tsv"
UNION_LOCK = BASE / "d106a-q6-proposal-union-lock.json"
SELECTION_LOCK = BASE / "d106a-q6-precision-selection-lock.json"
ARMS_A = BASE / "d106a-q6-union-arms-a-9827000-9827015.tsv"
ARMS_B = BASE / "d106a-q6-union-arms-b-9827000-9827015.tsv"
BASELINES_A = BASE / "d106a-q6-baselines-a-9827000-9827015.tsv"
BASELINES_B = BASE / "d106a-q6-baselines-b-9827000-9827015.tsv"
OUTPUT = BASE / "d106a-q6-fresh-map-proposal-readout-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "809b2204e67214001e61d10d8e8edd3124b68e7256110daede489f6430b0418d",
    SELECTOR: "62dddaffdeaab9907ef9ee85e6b0de4778eeda844806afb0ee9e4e3ab2266983",
    UNION_BUILDER: "e2872dcaadd8826210ee2e902daf7dec4e5522f2910fcf4117fb7699e9bf8a96",
    ADAPTER: "6f5c8e062e7449ed30f5701c1a9b73609fe250a4f3102ccce5ac8427f3866546",
    MANIFEST_RUNNER: "f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23",
    PROPOSAL_RUNNER: "c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393",
    CONTINUATION_RUNNER: "e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4",
    POPULATION: "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    SELECTION_LOCK: "1de217f124a2c61e19adf67592862f8098cbee8ac957992125113d7eb8a2cc5a",
    ARMS_A: "e495b102be6ccc842c202137b43d8ca3464d0c47e7c7cd3e26cc411374b90d89",
    ARMS_B: "e495b102be6ccc842c202137b43d8ca3464d0c47e7c7cd3e26cc411374b90d89",
    BASELINES_A: "553bae921756dac11a884f62fb7f61db08ffa4e20928ca69c9b88a931e28619a",
    BASELINES_B: "553bae921756dac11a884f62fb7f61db08ffa4e20928ca69c9b88a931e28619a",
}
MAP_START = 9_827_000
MAP_SPLIT = 9_827_008
MAP_STOP = 9_827_016
TASKS = (MAP_STOP - MAP_START) * 2 * len(OPPONENTS)
JOB_CATEGORIES = ("keep", "fell", "harvest", "renew", "mine")
OWNER_CATEGORIES = ("none", "natural", "own", "opponent", "ambiguous")
ARM_KINDS = ("control", "single_first", "single_second", "joint")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def expected_tasks() -> list[tuple[int, int, str]]:
    return [
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in OPPONENTS
    ]


def nonteacher_actions(row: dict[str, str]) -> int:
    return {"control": 0, "single_first": 1, "single_second": 1, "joint": 2}[
        row["arm_kind"]
    ]


def best(rows: list[dict[str, str]]) -> dict[str, str]:
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


def validate_terminal(
    manifest: list[dict[str, str]],
    arms: list[dict[str, str]],
    arm_fields: list[str],
    baselines: list[dict[str, str]],
    baseline_fields: list[str],
) -> tuple[dict, dict[str, dict[str, str]], dict[tuple[int, int, str], dict[str, str]]]:
    manifest_by_arm = {row["arm_id"]: row for row in manifest}
    arm_by_id = {row["arm_id"]: row for row in arms}
    baseline_by_task = {task_key(row): row for row in baselines}
    expected = set(expected_tasks())
    failures = Counter()
    if len(manifest_by_arm) != len(manifest):
        failures["duplicate_manifest_arm"] += len(manifest) - len(manifest_by_arm)
    if len(arm_by_id) != len(arms):
        failures["duplicate_terminal_arm"] += len(arms) - len(arm_by_id)
    if set(arm_by_id) != set(manifest_by_arm):
        failures["arm_identity_coverage"] += len(set(arm_by_id) ^ set(manifest_by_arm))
    if len(baseline_by_task) != TASKS or set(baseline_by_task) != expected:
        failures["baseline_task_coverage"] += 1
    if not set(TERMINAL_FIELDS).issubset(arm_fields):
        failures["arm_terminal_schema"] += 1
    if not set(TERMINAL_FIELDS).issubset(baseline_fields):
        failures["baseline_terminal_schema"] += 1
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
    for arm_id, row in arm_by_id.items():
        source = manifest_by_arm.get(arm_id)
        if source is None:
            continue
        for field in mirror_fields:
            failures[f"mirror_{field}"] += row[field] != source[field]
    for row in [*baselines, *arms]:
        try:
            floats = [float(row[field]) for field in FLOAT_FIELDS]
            failures["nonfinite_terminal"] += any(
                not math.isfinite(value) for value in floats
            )
            failures["reward_identity"] += float(row["reward_identity_error"]) > 1e-4
            failures["margin_identity"] += int(row["margin"]) != int(
                row["own_score"]
            ) - int(row["opponent_score"])
            failures["action_plane_accounting"] += sum(
                int(row[field]) for field in ACTION_PLANES
            ) != int(row["selected_decisions"])
            failures["worker_cap"] += int(row["own_workers"]) > 3
            failures["crop_creation"] += int(row["own_created_crops"]) <= 0
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            ):
                failures[field] += int(row[field])
        except (KeyError, TypeError, ValueError):
            failures["terminal_parse"] += 1
    controls = [row for row in arms if row["arm_kind"] == "control"]
    roots = {row["root_id"] for row in manifest}
    failures["control_count"] += abs(len(controls) - len(roots))
    for row in controls:
        baseline = baseline_by_task.get(task_key(row))
        if baseline is None:
            failures["control_task_missing"] += 1
            continue
        for field in TERMINAL_FIELDS:
            failures["control_parity"] += row[field] != baseline[field]
    failure_counts = {key: int(value) for key, value in sorted(failures.items()) if value}
    return (
        {
            "manifest_arms": len(manifest),
            "terminal_arms": len(arms),
            "baselines": len(baselines),
            "roots": len(roots),
            "failure_counts": failure_counts,
        },
        arm_by_id,
        baseline_by_task,
    )


def reversed_order_present(pairs: set[tuple[str, str]]) -> bool:
    return any(left != right and (right, left) in pairs for left, right in pairs)


def headroom(
    manifest_by_arm: dict[str, dict[str, str]],
    arms: list[dict[str, str]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict]]:
    by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        by_task[task_key(row)].append(row)
    margin_deltas = []
    own_deltas = []
    opponent_deltas = []
    family = defaultdict(list)
    crops = []
    workers = []
    baseline_workers = []
    rooted_deltas = []
    incremental = []
    joint_beats = 0
    jobs = set()
    owners = set()
    seats = set()
    opponents = set()
    pairs = set()
    selected_kinds = Counter()
    details = []
    for key in expected_tasks():
        baseline = baselines[key]
        baseline_workers.append(int(baseline["own_workers"]) >= 3)
        task_rows = by_task.get(key, [])
        if task_rows:
            chosen = best(task_rows)
            single = best([row for row in task_rows if row["arm_kind"] != "joint"])
            delta = int(chosen["margin"]) - int(baseline["margin"])
            rooted_deltas.append(delta)
            inc = int(chosen["margin"]) - int(single["margin"])
            incremental.append(inc)
            joint_beats += chosen["arm_kind"] == "joint" and inc > 0
            if chosen["arm_kind"] != "control":
                source = manifest_by_arm[chosen["arm_id"]]
                seats.add(key[1])
                opponents.add(key[2])
                pair = (chosen["first_class"], chosen["second_class"])
                pairs.add(pair)
                for prefix in ("first", "second"):
                    if chosen[f"{prefix}_class"] == "keep":
                        continue
                    jobs.add(source[f"{prefix}_job_kind"])
                    owner = source[f"{prefix}_owner"]
                    if owner != "none":
                        owners.add(owner)
        else:
            chosen = baseline
            delta = 0
            inc = None
        own_delta = int(chosen["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(chosen["opponent_score"]) - int(
            baseline["opponent_score"]
        )
        margin_deltas.append(delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        family[key[2]].append(delta)
        crops.append(int(chosen["own_created_crops"]) > 0)
        workers.append(int(chosen["own_workers"]) >= 3)
        selected_kinds[chosen.get("arm_kind", "no_root_d40")] += 1
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "selected_arm": chosen.get("arm_id", "no_root_d40"),
                "selected_kind": chosen.get("arm_kind", "no_root_d40"),
                "margin_delta": delta,
                "incremental_vs_best_single": inc,
            }
        )
    family_means = {name: float(np.mean(family[name])) for name in OPPONENTS}
    result = {
        "tasks": TASKS,
        "roots": len(rooted_deltas),
        "mean_margin_delta_all_tasks": float(np.mean(margin_deltas)),
        "mean_own_score_delta_all_tasks": float(np.mean(own_deltas)),
        "mean_opponent_score_delta_all_tasks": float(np.mean(opponent_deltas)),
        "strict_root_improvements": int(np.sum(np.asarray(rooted_deltas) > 0)),
        "strict_root_improvement_rate": float(np.mean(np.asarray(rooted_deltas) > 0)),
        "family_mean_margin_deltas": family_means,
        "worst_family_mean_margin_delta": min(family_means.values()),
        "crop_rate": float(np.mean(crops)),
        "worker_three_rate": float(np.mean(workers)),
        "baseline_worker_three_rate": float(np.mean(baseline_workers)),
        "mean_incremental_margin_vs_best_single_rooted": float(np.mean(incremental)),
        "joint_strictly_beats_best_single_roots": joint_beats,
        "joint_strictly_beats_best_single_rate": joint_beats / len(rooted_deltas),
        "selected_kind_counts": dict(sorted(selected_kinds.items())),
        "selected_job_kinds": sorted(jobs),
        "selected_provenance_classes": sorted(owners),
        "selected_seats": sorted(seats),
        "selected_opponents": sorted(opponents),
        "selected_reversed_role_order_present": reversed_order_present(pairs),
    }
    return result, details


def proposal_supporters() -> dict[tuple[str, str], set[int]]:
    rows, _ = read_table(PROPOSALS)
    result: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row in rows:
        result[(row["root_id"], row["arm_id"])].add(int(row["expert_index"]))
    return result


def one_hot(value: str, categories: tuple[str, ...]) -> list[float]:
    if value not in categories:
        raise RuntimeError(f"D106a unknown category {value!r}")
    return [float(value == category) for category in categories]


def semantic_vector(row: dict[str, str], supporters: set[int]) -> np.ndarray:
    values: list[float] = [float(row["arm_kind"] != "control")]
    values.extend(one_hot(row["arm_kind"], ARM_KINDS))
    for prefix in ("first", "second"):
        job = "keep" if row[f"{prefix}_class"] == "keep" else row[f"{prefix}_job_kind"]
        values.extend(one_hot(job, JOB_CATEGORIES))
    for prefix in ("first", "second"):
        owner = "none" if row[f"{prefix}_class"] == "keep" else row[f"{prefix}_owner"]
        values.extend(one_hot(owner, OWNER_CATEGORIES))
    values.extend(
        [
            int(row["first_prior_rank"]) / max(1, int(row["root_candidate_count"])),
            int(row["second_prior_rank"]) / max(1, int(row["second_candidate_count"])),
        ]
    )
    for prefix in ("first", "second"):
        target = int(row[f"{prefix}_target"])
        present = target >= 0
        values.extend(
            [
                float(present),
                (target // 22) / 10.0 if present else 0.0,
                (target % 22) / 21.0 if present else 0.0,
            ]
        )
    for prefix in ("first", "second"):
        for fruit in ("plum", "lemon", "apple", "iron"):
            values.append(int(row[f"{prefix}_deposit_{fruit}"]) / 10.0)
    values.extend(
        [
            nonteacher_actions(row) / 2.0,
            int(row["second_candidate_count"]) / 100.0,
            int(row["second_catalog_size"]) / 16.0,
            len(supporters) / 64.0,
        ]
    )
    if len(values) != 45:
        raise RuntimeError(f"D106a semantic feature count {len(values)} != 45")
    return np.asarray(values, dtype=np.float64)


def context_vector(row: dict[str, str]) -> np.ndarray:
    return np.asarray(
        [
            int(row["turn"]) / 300.0,
            int(row["decision_ordinal"]) / 200.0,
            int(row["live_own_crops"]) / 20.0,
            int(row["root_candidate_count"]) / 100.0,
            int(row["first_catalog_size"]) / 16.0,
            int(row["first_worker_ordinal"]) / 2.0,
        ],
        dtype=np.float64,
    )


def raw_feature(row: dict[str, str], supporters: set[int]) -> np.ndarray:
    semantic = semantic_vector(row, supporters)
    endorsements = np.zeros(64, dtype=np.float64)
    endorsements[list(supporters)] = 1.0
    interactions = np.outer(context_vector(row), semantic).reshape(-1)
    result = np.concatenate((semantic, endorsements, interactions))
    if result.shape != (379,) or not np.isfinite(result).all():
        raise RuntimeError("D106a proposal feature ABI failure")
    return result


def feature_dataset(
    manifest: list[dict[str, str]],
    arm_by_id: dict[str, dict[str, str]],
) -> tuple[list[dict], dict[str, np.ndarray]]:
    supporters = proposal_supporters()
    by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        by_root[row["root_id"]].append(row)
    controls = {
        root_id: next(row for row in rows if row["arm_kind"] == "control")
        for root_id, rows in by_root.items()
    }
    control_features = {
        root_id: raw_feature(
            control, supporters.get((root_id, control["arm_id"]), set())
        )
        for root_id, control in controls.items()
    }
    dataset = []
    for root_id in sorted(by_root, key=int):
        control = controls[root_id]
        control_terminal = arm_by_id[control["arm_id"]]
        partition = "discovery" if int(control["map_seed"]) < MAP_SPLIT else "validation"
        for row in sorted(by_root[root_id], key=lambda item: item["arm_id"]):
            if row["arm_kind"] == "control":
                continue
            vector = raw_feature(
                row, supporters.get((root_id, row["arm_id"]), set())
            ) - control_features[root_id]
            terminal = arm_by_id[row["arm_id"]]
            dataset.append(
                {
                    "root_id": root_id,
                    "task": task_key(row),
                    "partition": partition,
                    "arm_id": row["arm_id"],
                    "manifest": row,
                    "features": vector,
                    "margin_delta": int(terminal["margin"])
                    - int(control_terminal["margin"]),
                }
            )
    return dataset, control_features


def fit_ridge(rows: list[dict], columns: np.ndarray) -> dict:
    x = np.stack([row["features"][columns] for row in rows])
    y = np.clip(
        np.asarray([row["margin_delta"] for row in rows], dtype=np.float64),
        -100.0,
        100.0,
    )
    counts = Counter(row["root_id"] for row in rows)
    raw_weights = np.asarray([1.0 / counts[row["root_id"]] for row in rows])
    weights = raw_weights * (len(rows) / raw_weights.sum())
    scale = np.sqrt(np.mean(x * x, axis=0))
    scale = np.where(scale == 0.0, 1.0, scale)
    standardized = x / scale
    gram = standardized.T @ (weights[:, None] * standardized)
    target = standardized.T @ (weights * y)
    coefficients = np.linalg.solve(
        gram + 100.0 * np.eye(gram.shape[0], dtype=np.float64), target
    )
    return {
        "columns": columns,
        "scale": scale,
        "coefficients": coefficients,
        "training_rows": len(rows),
        "training_roots": len(counts),
        "target_clip": 100.0,
        "alpha": 100.0,
        "maximum_root_weight_error": max(
            abs(sum(weights[index] for index, row in enumerate(rows) if row["root_id"] == root_id)
                - len(rows) / len(counts))
            for root_id in counts
        ),
    }


def predict(model: dict, row: dict) -> float:
    vector = row["features"][model["columns"]]
    return float((vector / model["scale"]) @ model["coefficients"])


def readout_summary(
    rows: list[dict],
    model: dict,
    manifest_by_arm: dict[str, dict[str, str]],
    arm_by_id: dict[str, dict[str, str]],
    baselines: dict[tuple[int, int, str], dict[str, str]],
    oracle_details: list[dict],
    partition: str,
) -> tuple[dict, list[dict]]:
    partition_rows = [row for row in rows if row["partition"] == partition]
    by_root: dict[str, list[dict]] = defaultdict(list)
    for row in partition_rows:
        row = dict(row)
        row["prediction"] = predict(model, row)
        by_root[row["root_id"]].append(row)
    selected_by_task = {}
    activations = []
    for root_id, candidates in by_root.items():
        candidates.sort(key=lambda row: row["arm_id"])
        chosen = max(candidates, key=lambda row: row["prediction"])
        task = chosen["task"]
        if chosen["prediction"] > 0:
            selected_by_task[task] = chosen
            activations.append(chosen)
        else:
            selected_by_task[task] = None
    start = MAP_START if partition == "discovery" else MAP_SPLIT
    stop = MAP_SPLIT if partition == "discovery" else MAP_STOP
    tasks = [
        (seed, seat, opponent)
        for seed in range(start, stop)
        for seat in range(2)
        for opponent in OPPONENTS
    ]
    deltas = []
    family = defaultdict(list)
    crops = []
    workers = []
    baseline_workers = []
    rooted_deltas = []
    active_deltas = []
    details = []
    jobs = set()
    owners = set()
    seats = set()
    opponents = set()
    pairs = set()
    joint = 0
    for key in tasks:
        baseline = baselines[key]
        baseline_workers.append(int(baseline["own_workers"]) >= 3)
        selected = selected_by_task.get(key)
        if selected is None:
            terminal = baseline
            arm_id = "control_or_no_root"
            kind = "control"
            delta = 0
        else:
            arm_id = selected["arm_id"]
            terminal = arm_by_id[arm_id]
            source = manifest_by_arm[arm_id]
            kind = source["arm_kind"]
            delta = int(terminal["margin"]) - int(baseline["margin"])
            active_deltas.append(delta)
            joint += kind == "joint"
            seats.add(key[1])
            opponents.add(key[2])
            pairs.add((source["first_class"], source["second_class"]))
            for prefix in ("first", "second"):
                if source[f"{prefix}_class"] == "keep":
                    continue
                jobs.add(source[f"{prefix}_job_kind"])
                owner = source[f"{prefix}_owner"]
                if owner != "none":
                    owners.add(owner)
        if key in selected_by_task:
            rooted_deltas.append(delta)
        deltas.append(delta)
        family[key[2]].append(delta)
        crops.append(int(terminal["own_created_crops"]) > 0)
        workers.append(int(terminal["own_workers"]) >= 3)
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "selected_arm": arm_id,
                "selected_kind": kind,
                "margin_delta": delta,
            }
        )
    oracle_by_task = {
        (row["map_seed"], row["seat"], row["opponent"]): row
        for row in oracle_details
        if start <= row["map_seed"] < stop
    }
    oracle_mean = float(
        np.mean([oracle_by_task[key]["margin_delta"] for key in tasks])
    )
    family_means = {name: float(np.mean(family[name])) for name in OPPONENTS}
    rooted_count = len(by_root)
    activation_count = len(activations)
    summary = {
        "partition": partition,
        "tasks": len(tasks),
        "roots": rooted_count,
        "activation_roots": activation_count,
        "activation_rate": activation_count / rooted_count,
        "mean_realized_margin_delta_all_tasks": float(np.mean(deltas)),
        "strict_root_improvement_rate": float(np.mean(np.asarray(rooted_deltas) > 0)),
        "activated_positive_rate": float(np.mean(np.asarray(active_deltas) > 0))
        if active_deltas
        else None,
        "activated_negative_rate": float(np.mean(np.asarray(active_deltas) < 0))
        if active_deltas
        else None,
        "family_mean_margin_deltas": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family_mean_margin_delta": min(family_means.values()),
        "oracle_mean_margin_delta_all_tasks": oracle_mean,
        "oracle_value_capture": float(np.mean(deltas)) / oracle_mean
        if oracle_mean > 0
        else None,
        "crop_rate": float(np.mean(crops)),
        "worker_three_rate": float(np.mean(workers)),
        "baseline_worker_three_rate": float(np.mean(baseline_workers)),
        "joint_activation_rate": joint / rooted_count,
        "selected_job_kinds": sorted(jobs),
        "selected_provenance_classes": sorted(owners),
        "selected_seats": sorted(seats),
        "selected_opponents": sorted(opponents),
        "selected_reversed_role_order_present": reversed_order_present(pairs),
    }
    return summary, details


def serializable_model(model: dict) -> dict:
    return {
        "columns": model["columns"].tolist(),
        "scale": model["scale"].tolist(),
        "coefficients": model["coefficients"].tolist(),
        "training_rows": model["training_rows"],
        "training_roots": model["training_roots"],
        "target_clip": model["target_clip"],
        "alpha": model["alpha"],
        "maximum_root_weight_error": model["maximum_root_weight_error"],
    }


def main() -> int:
    source_hashes = {
        str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES
    }
    hashes_pass = all(
        source_hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in EXPECTED_HASHES.items()
    )
    if not hashes_pass:
        raise RuntimeError("D106a immutable hash mismatch")
    selection_lock = json.loads(SELECTION_LOCK.read_text())
    if not selection_lock["selection_pass"] or selection_lock["selected_bits"] != 6:
        raise RuntimeError("D106a q6 was not outcome-blindly selected")

    manifest, _ = read_table(UNION)
    arms_a, arm_fields = read_table(ARMS_A)
    arms_b, _ = read_table(ARMS_B)
    baselines_a, baseline_fields = read_table(BASELINES_A)
    baselines_b, _ = read_table(BASELINES_B)
    terminal_audit, arm_by_id, baseline_by_task = validate_terminal(
        manifest, arms_a, arm_fields, baselines_a, baseline_fields
    )
    repeat_identical = ARMS_A.read_bytes() == ARMS_B.read_bytes() and BASELINES_A.read_bytes() == BASELINES_B.read_bytes()
    manifest_by_arm = {row["arm_id"]: row for row in manifest}
    integrity_gates = {
        "immutable_hashes_match": hashes_pass,
        "selection_lock_outcome_blind": selection_lock["outcomes_read"] is False,
        "selection_lock_predates_terminal_outputs": SELECTION_LOCK.stat().st_mtime_ns
        < min(ARMS_A.stat().st_mtime_ns, ARMS_B.stat().st_mtime_ns),
        "terminal_repeats_byte_identical": repeat_identical,
        "terminal_grid_and_mechanics": not terminal_audit["failure_counts"],
        "union_hash_matches_lock": sha256(UNION)
        == selection_lock["union_manifest_sha256"]["q6"],
        "proposal_hash_matches_lock": sha256(PROPOSALS)
        == selection_lock["proposal_sha256"]["q6"],
    }
    integrity_pass = all(integrity_gates.values())
    if not integrity_pass:
        report = {
            "protocol": "D106a q6 fresh-map proposal readout",
            "integrity_pass": False,
            "selection_pass": True,
            "headroom_opened": False,
            "readout_opened": False,
            "pass": False,
            "decision": "quarantine_d106a_measurement_repair_only",
            "integrity_gates": integrity_gates,
            "terminal_audit": terminal_audit,
            "source_hashes": source_hashes,
        }
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0

    oracle, oracle_details = headroom(manifest_by_arm, arms_a, baseline_by_task)
    headroom_gates = {
        "mean_gain_at_least_25": oracle["mean_margin_delta_all_tasks"] >= 25,
        "strict_root_improvement_at_least_85pct": oracle[
            "strict_root_improvement_rate"
        ]
        >= 0.85,
        "every_family_gain_at_least_12": oracle["worst_family_mean_margin_delta"]
        >= 12,
        "own_nonnegative_opponent_nonpositive": oracle[
            "mean_own_score_delta_all_tasks"
        ]
        >= 0
        and oracle["mean_opponent_score_delta_all_tasks"] <= 0,
        "crop_exact_and_worker_three_preserved": oracle["crop_rate"] == 1.0
        and oracle["worker_three_rate"] >= oracle["baseline_worker_three_rate"] - 0.05,
        "increment_over_best_single_at_least_2": oracle[
            "mean_incremental_margin_vs_best_single_rooted"
        ]
        >= 2,
        "joint_beats_single_at_least_30pct_roots": oracle[
            "joint_strictly_beats_best_single_rate"
        ]
        >= 0.30,
        "winner_breadth": len(oracle["selected_job_kinds"]) >= 3
        and len(oracle["selected_provenance_classes"]) >= 2
        and oracle["selected_seats"] == [0, 1]
        and set(oracle["selected_opponents"]) == set(OPPONENTS)
        and oracle["selected_reversed_role_order_present"],
    }
    headroom_pass = all(headroom_gates.values())
    report = {
        "protocol": "D106a q6 fresh-map proposal readout",
        "integrity_pass": integrity_pass,
        "selection_pass": True,
        "headroom_opened": True,
        "headroom_pass": headroom_pass,
        "integrity_gates": integrity_gates,
        "terminal_audit": terminal_audit,
        "headroom_gates": headroom_gates,
        "fresh_union_oracle": oracle,
        "oracle_details": oracle_details,
        "selection": selection_lock,
        "source_hashes": source_hashes,
    }
    if not headroom_pass:
        report.update(
            {
                "readout_opened": False,
                "pass": False,
                "decision": "close_d106a_q6_after_fresh_headroom_failure",
            }
        )
    else:
        dataset, _ = feature_dataset(manifest, arm_by_id)
        discovery = [row for row in dataset if row["partition"] == "discovery"]
        combined_columns = np.arange(379)
        semantic_columns = np.concatenate((np.arange(45), np.arange(109, 379)))
        endorsement_columns = np.arange(45, 109)
        models = {
            "combined": fit_ridge(discovery, combined_columns),
            "semantic_only": fit_ridge(discovery, semantic_columns),
            "endorsement_only": fit_ridge(discovery, endorsement_columns),
        }
        summaries = {}
        selected_details = {}
        for name, model in models.items():
            summaries[name] = {}
            selected_details[name] = {}
            for partition in ("discovery", "validation"):
                summary, details = readout_summary(
                    dataset,
                    model,
                    manifest_by_arm,
                    arm_by_id,
                    baseline_by_task,
                    oracle_details,
                    partition,
                )
                summaries[name][partition] = summary
                selected_details[name][partition] = details
        validation = summaries["combined"]["validation"]
        readout_gates = {
            "activation_between_15_and_80pct": 0.15
            <= validation["activation_rate"]
            <= 0.80,
            "selected_semantic_breadth": len(validation["selected_job_kinds"]) >= 3
            and len(validation["selected_provenance_classes"]) >= 2
            and validation["selected_seats"] == [0, 1]
            and set(validation["selected_opponents"]) == set(OPPONENTS)
            and validation["joint_activation_rate"] >= 0.10,
            "mean_realized_gain_at_least_2": validation[
                "mean_realized_margin_delta_all_tasks"
            ]
            >= 2,
            "strict_root_improvement_at_least_20pct": validation[
                "strict_root_improvement_rate"
            ]
            >= 0.20,
            "activated_positive_at_least_55pct": validation[
                "activated_positive_rate"
            ]
            is not None
            and validation["activated_positive_rate"] >= 0.55,
            "every_family_at_least_minus3": validation[
                "worst_family_mean_margin_delta"
            ]
            >= -3,
            "at_least_six_positive_families": validation["positive_families"] >= 6,
            "capture_at_least_15pct_oracle": validation["oracle_value_capture"]
            >= 0.15,
            "crop_exact_and_worker_three_preserved": validation["crop_rate"] == 1.0
            and validation["worker_three_rate"]
            >= validation["baseline_worker_three_rate"] - 0.05,
        }
        readout_pass = all(readout_gates.values())
        report.update(
            {
                "readout_opened": True,
                "readout_pass": readout_pass,
                "readout_gates": readout_gates,
                "feature_abi": {
                    "semantic_features": 45,
                    "endorsement_features": 64,
                    "context_semantic_interactions": 270,
                    "total_features": 379,
                    "opponent_identity_included": False,
                    "map_seed_included": False,
                    "seat_label_included": False,
                },
                "readout_models": {
                    name: serializable_model(model) for name, model in models.items()
                },
                "readout_summaries": summaries,
                "readout_selected_details": selected_details,
                "pass": readout_pass,
                "decision": (
                    "open_d106b_bounded_complete_online_proposal_controller"
                    if readout_pass
                    else "close_d106a_offline_ridge_keep_q6_action_basis"
                ),
            }
        )
    report["provenance"] = {
        "protocol_sha256": sha256(PROTOCOL),
        "selection_lock_sha256": sha256(SELECTION_LOCK),
        "analyzer_sha256": sha256(Path(__file__)),
        "arms_sha256": sha256(ARMS_A),
        "baselines_sha256": sha256(BASELINES_A),
    }
    report["scope"] = (
        "fresh q6 one-assignment continuation and discovery-only held readout; no complete learned "
        "policy, candidate, or platform action"
    )
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "integrity_pass": integrity_pass,
                "headroom_pass": headroom_pass,
                "fresh_union_oracle": oracle,
                "readout_opened": report["readout_opened"],
                "readout_pass": report.get("readout_pass"),
                "validation": report.get("readout_summaries", {})
                .get("combined", {})
                .get("validation"),
                "failed_readout_gates": [
                    name
                    for name, passed in report.get("readout_gates", {}).items()
                    if not passed
                ],
                "decision": report["decision"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
