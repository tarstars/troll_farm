#!/usr/bin/env python3
"""Validate and analyze D104a's frozen D98 expert-proposal coverage audit."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import struct
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.analyze_d97a_joint_concrete_jobs import (
    ACTION_PLANES,
    OPPONENTS,
    TASKS,
    TERMINAL_FIELDS,
    expected_tasks,
    manifest_support,
    mean,
    nonteacher_actions,
    oracle_metrics,
    read_table,
    select,
    task_key,
    validate_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d104a-d98-expert-proposal-coverage-protocol-2026-07-22.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "d104_d98_expert_proposal_coverage.rs"
PROPOSALS_A = BASE / "d104a-d98-expert-proposals-a-jobs1.tsv"
PROPOSALS_B = BASE / "d104a-d98-expert-proposals-b-jobs20.tsv"
D98_POPULATION = BASE / "d98a-bounded-whole-game-joint-assignment-population.tsv"
D98_RUNNER = ROOT / "rust" / "src" / "bin" / "d98_bounded_joint_assignment_population.rs"
D97_GENERATOR = ROOT / "rust" / "src" / "bin" / "d97_joint_concrete_manifest.rs"
D97_MANIFEST = BASE / "d97a-d40-joint-concrete-job-manifest-9820000-9820015.tsv"
D97_ARMS = BASE / "d97a-d40-joint-concrete-job-arms-a-9820000-9820015.tsv"
D97_ARMS_B = BASE / "d97a-d40-joint-concrete-job-arms-b-9820000-9820015.tsv"
D97_BASELINES = BASE / "d97a-d40-joint-concrete-job-baselines-a-9820000-9820015.tsv"
D97_BASELINES_B = BASE / "d97a-d40-joint-concrete-job-baselines-b-9820000-9820015.tsv"
OUTPUT = BASE / "d104a-d98-expert-proposal-coverage-result.json"

EXPECTED_HASHES = {
    PROTOCOL: "c6d0cfdb2220711325bd94ea02dd93eeab183d177e2d901f0f18f500b3dbd24b",
    RUNNER: "c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393",
    D98_POPULATION: "3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e",
    D98_RUNNER: "49a2c204ec1df3aaf79facdcd39e44cd250458535494a8cf4b6b8de1ff077dfd",
    D97_GENERATOR: "f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23",
    D97_MANIFEST: "ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e",
    D97_ARMS: "c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33",
    D97_BASELINES: "8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6",
}

EXPECTED_ROOTS = 240
EXPECTED_EXPERTS = 64
EXPECTED_PROPOSALS = EXPECTED_ROOTS * EXPECTED_EXPERTS
PROPOSAL_MIRROR_FIELDS = (
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
    "second_state_hash",
    "second_observation_hash",
    "second_catalog_hash",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fnv_mix(hash_value: int, value: int) -> int:
    for byte in value.to_bytes(8, "little", signed=False):
        hash_value ^= byte
        hash_value = (hash_value * 0x100000001B3) & ((1 << 64) - 1)
    return hash_value


def expert_hash(values: list[str]) -> int:
    result = 0xCBF29CE484222325
    for value in values:
        bits = struct.unpack("<I", struct.pack("<f", float(value)))[0]
        result = fnv_mix(result, bits)
    return result


def read_experts(path: Path) -> dict[str, dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    experts = {}
    for row in rows:
        if row["kind"] != "four":
            continue
        parameters = [row[f"param_{index:03}"] for index in range(153)]
        experts[row["policy"]] = {
            "budget": int(row["budget"]),
            "hash": expert_hash(parameters),
        }
    if sorted(experts) != [f"four_{index:02}" for index in range(EXPECTED_EXPERTS)]:
        raise RuntimeError("D104 D98 expert population mismatch")
    return experts


def proposal_key(row: dict[str, str]) -> tuple[int, int]:
    return int(row["root_id"]), int(row["expert_index"])


def root_manifest_rows(manifest: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    roots = {}
    for row in manifest:
        root_id = int(row["root_id"])
        if root_id in roots:
            for field in (
                "map_seed",
                "seat",
                "opponent_index",
                "opponent",
                "decision_ordinal",
                "turn",
                "root_state_hash",
            ):
                if roots[root_id][field] != row[field]:
                    raise RuntimeError(f"D104 inconsistent manifest root {root_id} field {field}")
        else:
            roots[root_id] = row
    if len(roots) != EXPECTED_ROOTS:
        raise RuntimeError("D104 manifest root count mismatch")
    return roots


def validate_proposals(
    proposals: list[dict[str, str]],
    proposals_b: list[dict[str, str]],
    roots: dict[int, dict[str, str]],
    manifest_by_arm: dict[str, dict[str, str]],
    experts: dict[str, dict],
    repeat_identical: bool,
) -> tuple[dict, dict[int, list[dict[str, str]]]]:
    counts = Counter()
    if len(proposals) != EXPECTED_PROPOSALS:
        counts["run_a_row_count"] += abs(len(proposals) - EXPECTED_PROPOSALS) or 1
    if len(proposals_b) != EXPECTED_PROPOSALS:
        counts["run_b_row_count"] += abs(len(proposals_b) - EXPECTED_PROPOSALS) or 1
    if not repeat_identical:
        counts["repeat_byte_mismatch"] += 1

    by_key = {proposal_key(row): row for row in proposals}
    if len(by_key) != len(proposals):
        counts["duplicate_proposal_keys"] += len(proposals) - len(by_key)
    expected_keys = {
        (root_id, expert_index)
        for root_id in roots
        for expert_index in range(EXPECTED_EXPERTS)
    }
    counts["missing_grid_rows"] += len(expected_keys - set(by_key))
    counts["extra_grid_rows"] += len(set(by_key) - expected_keys)

    by_root = defaultdict(list)
    global_hashes = defaultdict(set)
    matched = 0
    supported = 0
    for row in proposals:
        root_id = int(row["root_id"])
        by_root[root_id].append(row)
        global_hashes[root_id].add(row["global_feature_hash"])
        root = roots.get(root_id)
        if root is None:
            counts["unknown_root"] += 1
            continue
        for proposal_field, manifest_field in (
            ("map_seed", "map_seed"),
            ("seat", "seat"),
            ("opponent_index", "opponent_index"),
            ("opponent", "opponent"),
            ("decision_ordinal", "decision_ordinal"),
            ("turn", "turn"),
            ("root_state_hash", "root_state_hash"),
        ):
            if row[proposal_field] != root[manifest_field]:
                counts[f"root_mirror_{proposal_field}"] += 1

        expert_index = int(row["expert_index"])
        expected_label = f"four_{expert_index:02}"
        if row["expert"] != expected_label:
            counts["expert_label"] += 1
        expected_expert = experts.get(row["expert"])
        if expected_expert is None or int(row["expert_hash"]) != expected_expert["hash"]:
            counts["expert_hash"] += 1

        paired = int(row["paired_boundary"]) == 1
        if paired:
            supported += 1
            arm = manifest_by_arm.get(row["arm_id"])
            if arm is None:
                counts["supported_arm_missing"] += 1
                continue
            arm_matches = True
            for field in PROPOSAL_MIRROR_FIELDS:
                if row[field] != arm[field]:
                    counts[f"arm_mirror_{field}"] += 1
                    arm_matches = False
            expected_nonkeep = {
                "control": 0,
                "single_first": 1,
                "single_second": 1,
                "joint": 2,
            }.get(row["arm_kind"])
            if expected_nonkeep is None or int(row["nonkeep_actions"]) != expected_nonkeep:
                counts["nonkeep_accounting"] += 1
                arm_matches = False
            matched += arm_matches
        else:
            if row["arm_kind"] != "unsupported" or row["arm_id"]:
                counts["unsupported_not_explicit"] += 1
            if any(
                row[field]
                for field in (
                    "second_label",
                    "second_class",
                    "second_action",
                    "second_teacher",
                    "second_state_hash",
                    "second_observation_hash",
                    "second_catalog_hash",
                )
            ):
                counts["unsupported_synthesized_second"] += 1

    counts["root_global_hash_multiplicity"] += sum(
        len(values) != 1 for values in global_hashes.values()
    )
    return (
        {
            "rows_a": len(proposals),
            "rows_b": len(proposals_b),
            "roots": len(by_root),
            "repeat_byte_identical": repeat_identical,
            "supported_rows": supported,
            "supported_rate": supported / len(proposals),
            "exact_arm_matches": matched,
            "failure_counts": {key: value for key, value in sorted(counts.items()) if value},
        },
        dict(by_root),
    )


def reversed_order_present(pairs: set[tuple[str, str]]) -> bool:
    return any(left != right and (right, left) in pairs for left, right in pairs)


def proposal_support(
    by_root: dict[int, list[dict[str, str]]],
    manifest_by_arm: dict[str, dict[str, str]],
) -> dict:
    unique_counts = []
    roots_with_three = 0
    roots_with_joint = 0
    expert_noncontrol_roots = Counter()
    jobs = set()
    owners = set()
    seats = set()
    opponents = set()
    pairs = set()
    kind_counts = Counter()
    for root_id, rows in by_root.items():
        supported = [
            row
            for row in rows
            if int(row["paired_boundary"]) == 1 and row["arm_id"] in manifest_by_arm
        ]
        unique = {
            row["arm_id"]: row
            for row in supported
            if row["arm_kind"] != "control"
        }
        unique_counts.append(len(unique))
        roots_with_three += len(unique) >= 3
        roots_with_joint += any(row["arm_kind"] == "joint" for row in unique.values())
        for expert in {row["expert"] for row in supported if row["arm_kind"] != "control"}:
            expert_noncontrol_roots[expert] += 1
        for row in unique.values():
            kind_counts[row["arm_kind"]] += 1
            arm = manifest_by_arm[row["arm_id"]]
            seats.add(int(row["seat"]))
            opponents.add(row["opponent"])
            classes = (row["first_class"], row["second_class"])
            pairs.add(classes)
            for prefix in ("first", "second"):
                if row[f"{prefix}_class"] == "keep":
                    continue
                jobs.add(arm[f"{prefix}_job_kind"])
                owner = arm[f"{prefix}_owner"]
                if owner != "none":
                    owners.add(owner)
    return {
        "mean_unique_supported_noncontrol_proposals_per_root": mean(unique_counts),
        "minimum_unique_supported_noncontrol_proposals": min(unique_counts),
        "maximum_unique_supported_noncontrol_proposals": max(unique_counts),
        "roots_with_at_least_three_unique_noncontrol": roots_with_three,
        "root_rate_with_at_least_three_unique_noncontrol": roots_with_three / EXPECTED_ROOTS,
        "roots_with_supported_joint": roots_with_joint,
        "root_rate_with_supported_joint": roots_with_joint / EXPECTED_ROOTS,
        "experts_noncontrol_in_at_least_25pct_roots": sum(
            expert_noncontrol_roots[f"four_{index:02}"] >= 0.25 * EXPECTED_ROOTS
            for index in range(EXPECTED_EXPERTS)
        ),
        "expert_noncontrol_root_counts": dict(sorted(expert_noncontrol_roots.items())),
        "unique_proposal_kind_occurrences": dict(sorted(kind_counts.items())),
        "proposal_job_kinds": sorted(jobs),
        "proposal_provenance_classes": sorted(owners),
        "proposal_seats": sorted(seats),
        "proposal_opponent_families": sorted(opponents),
        "proposal_reversed_role_order_present": reversed_order_present(pairs),
    }


def proposal_oracle(
    by_root: dict[int, list[dict[str, str]]],
    roots: dict[int, dict[str, str]],
    manifest_by_arm: dict[str, dict[str, str]],
    arm_by_id: dict[str, dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict]]:
    arms_by_task = defaultdict(list)
    for arm in arm_by_id.values():
        arms_by_task[task_key(arm)].append(arm)
    root_by_task = {
        (int(row["map_seed"]), int(row["seat"]), row["opponent"]): root_id
        for root_id, row in roots.items()
    }
    margin_deltas = []
    own_deltas = []
    opponent_deltas = []
    family_deltas = defaultdict(list)
    worker_three = []
    baseline_worker_three = []
    crops = []
    strict_root = 0
    incremental = []
    joint_selected = 0
    joint_beats_single = 0
    selected_jobs = set()
    selected_owners = set()
    selected_pairs = set()
    selected_seats = set()
    selected_opponents = set()
    selected_kinds = Counter()
    details = []
    for key in sorted(expected_tasks()):
        baseline = baseline_by_task[key]
        baseline_worker_three.append(int(baseline["own_workers"]) >= 3)
        root_id = root_by_task.get(key)
        if root_id is None:
            chosen = baseline
            single = baseline
            delta = 0
            incremental_delta = None
        else:
            task_arms = arms_by_task[key]
            control = next(row for row in task_arms if row["arm_kind"] == "control")
            candidate_ids = {
                row["arm_id"]
                for row in by_root[root_id]
                if int(row["paired_boundary"]) == 1
                and row["arm_id"] in arm_by_id
            }
            candidate_ids.add(control["arm_id"])
            chosen = select([arm_by_id[arm_id] for arm_id in candidate_ids])
            single = select([row for row in task_arms if row["arm_kind"] != "joint"])
            delta = int(chosen["margin"]) - int(baseline["margin"])
            strict_root += delta > 0
            incremental_delta = int(chosen["margin"]) - int(single["margin"])
            incremental.append(incremental_delta)
            joint_selected += chosen["arm_kind"] == "joint"
            joint_beats_single += chosen["arm_kind"] == "joint" and incremental_delta > 0
            if chosen["arm_kind"] != "control":
                manifest = manifest_by_arm[chosen["arm_id"]]
                selected_seats.add(key[1])
                selected_opponents.add(key[2])
                pair = (chosen["first_class"], chosen["second_class"])
                selected_pairs.add(pair)
                for prefix in ("first", "second"):
                    if chosen[f"{prefix}_class"] == "keep":
                        continue
                    selected_jobs.add(manifest[f"{prefix}_job_kind"])
                    owner = manifest[f"{prefix}_owner"]
                    if owner != "none":
                        selected_owners.add(owner)
        own_delta = int(chosen["own_score"]) - int(baseline["own_score"])
        opponent_delta = int(chosen["opponent_score"]) - int(baseline["opponent_score"])
        margin_deltas.append(delta)
        own_deltas.append(own_delta)
        opponent_deltas.append(opponent_delta)
        family_deltas[key[2]].append(delta)
        worker_three.append(int(chosen["own_workers"]) >= 3)
        crops.append(int(chosen["own_created_crops"]) > 0)
        selected_kind = chosen.get("arm_kind", "no_root_d40")
        selected_kinds[selected_kind] += 1
        details.append(
            {
                "map_seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "root_id": root_id,
                "selected_arm": chosen.get("arm_id", "no_root_d40"),
                "selected_kind": selected_kind,
                "margin_delta_vs_d40": delta,
                "incremental_margin_vs_full_best_single": incremental_delta,
            }
        )
    family_means = {name: mean(family_deltas[name]) for name in OPPONENTS}
    return (
        {
            "tasks": TASKS,
            "roots": EXPECTED_ROOTS,
            "mean_margin_delta_vs_d40_all_tasks": mean(margin_deltas),
            "mean_own_score_delta_vs_d40_all_tasks": mean(own_deltas),
            "mean_opponent_score_delta_vs_d40_all_tasks": mean(opponent_deltas),
            "strict_root_improvements": strict_root,
            "strict_root_improvement_rate": strict_root / EXPECTED_ROOTS,
            "opponent_family_mean_margin_deltas_all_tasks": family_means,
            "worst_opponent_family_mean_margin_delta": min(family_means.values()),
            "baseline_worker_three_rate": mean(baseline_worker_three),
            "proposal_oracle_worker_three_rate": mean(worker_three),
            "proposal_oracle_crop_rate": mean(crops),
            "mean_incremental_margin_vs_full_best_single_rooted": mean(incremental),
            "joint_selected_roots": joint_selected,
            "joint_selected_root_rate": joint_selected / EXPECTED_ROOTS,
            "joint_strictly_beats_full_best_single_roots": joint_beats_single,
            "joint_strictly_beats_full_best_single_rate": joint_beats_single / EXPECTED_ROOTS,
            "selected_kind_counts": dict(sorted(selected_kinds.items())),
            "selected_job_kinds": sorted(selected_jobs),
            "selected_provenance_classes": sorted(selected_owners),
            "selected_seats": sorted(selected_seats),
            "selected_opponent_families": sorted(selected_opponents),
            "selected_reversed_role_order_present": reversed_order_present(selected_pairs),
        },
        details,
    )


def analyze(
    proposals_a: list[dict[str, str]],
    proposals_b: list[dict[str, str]],
    repeat_identical: bool,
) -> dict:
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES}
    hashes_match = all(hashes[str(path.relative_to(ROOT))] == expected for path, expected in EXPECTED_HASHES.items())
    experts = read_experts(D98_POPULATION)
    manifest, manifest_fields = read_table(D97_MANIFEST)
    d97_support, manifest_by_arm = manifest_support(manifest)
    roots = root_manifest_rows(manifest)
    arms, arm_fields = read_table(D97_ARMS)
    baselines, baseline_fields = read_table(D97_BASELINES)
    d97_audit, arm_by_id, baseline_by_task = validate_outputs(
        manifest_by_arm, arms, arm_fields, baselines, baseline_fields
    )
    d97_oracle, _ = oracle_metrics(manifest_by_arm, arms, baseline_by_task)
    proposal_audit, by_root = validate_proposals(
        proposals_a,
        proposals_b,
        roots,
        manifest_by_arm,
        experts,
        repeat_identical,
    )
    support = proposal_support(by_root, manifest_by_arm)
    oracle, details = proposal_oracle(
        by_root, roots, manifest_by_arm, arm_by_id, baseline_by_task
    )
    oracle["capture_of_d97_joint_oracle"] = (
        oracle["mean_margin_delta_vs_d40_all_tasks"]
        / d97_oracle["paired_mean_margin_delta_vs_d40_all_tasks"]
    )

    d97_reproduced = (
        abs(d97_oracle["paired_mean_margin_delta_vs_d40_all_tasks"] - 36.8515625) < 1e-12
        and abs(
            d97_oracle["mean_incremental_margin_vs_best_single_eligible_roots"]
            - 9.208333333333334
        )
        < 1e-12
    )
    integrity_gates = {
        "frozen_source_and_input_hashes_match": hashes_match,
        "proposal_runs_byte_identical": repeat_identical,
        "exact_15360_row_grid": proposal_audit["rows_a"] == EXPECTED_PROPOSALS
        and proposal_audit["rows_b"] == EXPECTED_PROPOSALS
        and proposal_audit["roots"] == EXPECTED_ROOTS,
        "zero_proposal_reconstruction_failures": not proposal_audit["failure_counts"],
        "every_supported_proposal_exactly_matches_d97_arm": proposal_audit[
            "exact_arm_matches"
        ]
        == proposal_audit["supported_rows"],
        "d97_repeats_remain_byte_identical": D97_ARMS.read_bytes() == D97_ARMS_B.read_bytes()
        and D97_BASELINES.read_bytes() == D97_BASELINES_B.read_bytes(),
        "d97_terminal_integrity_remains_exact": not d97_audit["integrity_failure_counts"]
        and d97_audit["mirror_failures"] == 0
        and d97_audit["control_parity_failures"] == 0,
        "published_d97_oracles_reproduced": d97_reproduced,
    }
    support_gates = {
        "supported_proposal_rate_at_least_95pct": proposal_audit["supported_rate"] >= 0.95,
        "mean_unique_noncontrol_proposals_at_least_6": support[
            "mean_unique_supported_noncontrol_proposals_per_root"
        ]
        >= 6,
        "at_least_90pct_roots_have_3_noncontrol_proposals": support[
            "root_rate_with_at_least_three_unique_noncontrol"
        ]
        >= 0.90,
        "at_least_80pct_roots_have_joint_proposal": support[
            "root_rate_with_supported_joint"
        ]
        >= 0.80,
        "proposal_union_has_frozen_breadth": set(support["proposal_job_kinds"])
        == {"fell", "harvest", "mine", "renew"}
        and {"natural", "own", "opponent"}.issubset(
            support["proposal_provenance_classes"]
        )
        and support["proposal_seats"] == [0, 1]
        and set(support["proposal_opponent_families"]) == set(OPPONENTS)
        and support["proposal_reversed_role_order_present"],
        "at_least_48_experts_noncontrol_in_25pct_roots": support[
            "experts_noncontrol_in_at_least_25pct_roots"
        ]
        >= 48,
    }
    value_gates = {
        "proposal_oracle_gain_at_least_25": oracle[
            "mean_margin_delta_vs_d40_all_tasks"
        ]
        >= 25,
        "capture_at_least_65pct_d97_joint_oracle": oracle[
            "capture_of_d97_joint_oracle"
        ]
        >= 0.65,
        "strictly_improves_at_least_75pct_roots": oracle[
            "strict_root_improvement_rate"
        ]
        >= 0.75,
        "every_opponent_family_gain_at_least_10": oracle[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= 10,
        "own_nonnegative_opponent_nonpositive": oracle[
            "mean_own_score_delta_vs_d40_all_tasks"
        ]
        >= 0
        and oracle["mean_opponent_score_delta_vs_d40_all_tasks"] <= 0,
        "crop_exact_and_worker_three_preserved": oracle["proposal_oracle_crop_rate"] == 1.0
        and oracle["proposal_oracle_worker_three_rate"]
        >= oracle["baseline_worker_three_rate"] - 0.05,
        "gain_at_least_3_beyond_full_best_single": oracle[
            "mean_incremental_margin_vs_full_best_single_rooted"
        ]
        >= 3,
        "joint_selected_in_at_least_40pct_roots": oracle["joint_selected_root_rate"]
        >= 0.40,
        "joint_beats_full_single_in_at_least_20pct_roots": oracle[
            "joint_strictly_beats_full_best_single_rate"
        ]
        >= 0.20,
        "selected_proposal_breadth": len(oracle["selected_job_kinds"]) >= 3
        and len(oracle["selected_provenance_classes"]) >= 2
        and oracle["selected_reversed_role_order_present"]
        and oracle["selected_seats"] == [0, 1]
        and set(oracle["selected_opponent_families"]) == set(OPPONENTS),
    }
    integrity_pass = all(integrity_gates.values())
    support_pass = integrity_pass and all(support_gates.values())
    value_pass = integrity_pass and all(value_gates.values())
    passed = integrity_pass and support_pass and value_pass
    if not integrity_pass:
        decision = "repair_measurement_only"
    elif not support_pass:
        decision = "close_d98_bank_as_action_library"
    elif not value_pass:
        decision = "close_expert_mixture_value_not_exposed"
    else:
        decision = "open_d104b_online_recurrent_opponent_aware_proposal_controller"
    return {
        "protocol": "D104a D98 expert-proposal coverage",
        "integrity_pass": integrity_pass,
        "support_pass": support_pass,
        "value_pass": value_pass,
        "pass": passed,
        "decision": decision,
        "integrity_gates": integrity_gates,
        "support_gates": support_gates,
        "value_gates": value_gates,
        "source_hashes": hashes,
        "proposal_audit": proposal_audit,
        "d97_audit": d97_audit,
        "d97_support": d97_support,
        "d97_oracle": d97_oracle,
        "proposal_support": support,
        "proposal_oracle": oracle,
        "oracle_details": details,
        "scope": (
            "retrospective proposal-library audit only; no expert/arm selection, fitting, new "
            "terminal outcome, candidate, platform action, or resident mutation"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", type=Path, default=PROPOSALS_A)
    parser.add_argument("--run-b", type=Path, default=PROPOSALS_B)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--jobs1-seconds", type=float, required=True)
    parser.add_argument("--jobs20-seconds", type=float, required=True)
    args = parser.parse_args()
    rows_a, _ = read_table(args.run_a)
    rows_b, _ = read_table(args.run_b)
    report = analyze(rows_a, rows_b, sha256(args.run_a) == sha256(args.run_b))
    report["provenance"] = {
        "run_a": {"path": str(args.run_a), "sha256": sha256(args.run_a)},
        "run_b": {"path": str(args.run_b), "sha256": sha256(args.run_b)},
        "protocol": {"path": str(PROTOCOL), "sha256": sha256(PROTOCOL)},
        "runner": {"path": str(RUNNER), "sha256": sha256(RUNNER)},
        "analyzer": {"path": str(Path(__file__)), "sha256": sha256(Path(__file__))},
        "execution_seconds": {
            "jobs_1": args.jobs1_seconds,
            "jobs_20": args.jobs20_seconds,
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "integrity_pass": report["integrity_pass"],
                "support_pass": report["support_pass"],
                "value_pass": report["value_pass"],
                "pass": report["pass"],
                "decision": report["decision"],
                "support": report["proposal_support"],
                "oracle": report["proposal_oracle"],
                "failed_support_gates": [
                    name for name, value in report["support_gates"].items() if not value
                ],
                "failed_value_gates": [
                    name for name, value in report["value_gates"].items() if not value
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
