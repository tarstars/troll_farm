#!/usr/bin/env python3
"""Analyze D148's fresh-map 64-priority joint trajectory corpus."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import gc
import json
import math
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto import analyze_d133b_q6_support_semantics as d133b
from cgauto import run_d148a_priority_joint_teacher as runner
from cgauto import yt_d133_q6_teacher_corpus as d133
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d148a-priority-joint-teacher-corpus-protocol-2026-07-22.md"
OUTPUT = BASE / "d148a-priority-joint-teacher-corpus-result.json"
TARGETS = BASE / "d148a-joint-trajectory-targets-9844136-9844199.tsv"

TRANSFER_TERMINAL_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "own_created_crops",
)
CONTROL_PARITY_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "successful_trains",
    "own_created_crops",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "action_hash",
    "state_hash",
)
TARGET_FIELDS = (
    "map_seed",
    "seat",
    "opponent",
    "eight_map_fold",
    "source_replica",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "second_slot",
    "selection_hash",
    "control_margin",
    "one_use_boundary",
    "one_use_slot",
    "one_use_margin",
    "sequence_margin",
    "sequence_gain_over_control",
    "increment_beyond_one_use",
    "target_active",
)


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def margin(row: dict) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(yt_d148.START_SEED, yt_d148.START_SEED + yt_d148.MAPS)
        for seat in range(2)
        for opponent in d112.OPPONENTS
    }


def iter_arm_blocks(path: Path):
    """Yield the merged exact-arm table one contiguous 8-map block at a time."""

    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = list(reader.fieldnames or ())
        current = None
        rows = []
        for row in reader:
            block = (int(row["map_seed"]) - yt_d148.START_SEED) // yt_d148.MAPS_PER_SHARD
            if not 0 <= block < yt_d148.SHARDS:
                raise RuntimeError("D148 exact arm outside training panel")
            if current is None:
                current = block
            if block < current:
                raise RuntimeError("D148 exact arms are not seed ordered")
            if block != current:
                yield current, rows, fields
                if block != current + 1:
                    raise RuntimeError("D148 exact arm block gap")
                current = block
                rows = []
            rows.append(row)
        if current is not None:
            yield current, rows, fields


def analyze_exact(
    arms_path: Path,
    baselines_path: Path,
    metadata_by_shard: dict[str, dict],
) -> tuple[dict, dict, dict]:
    baselines, _ = read_table(baselines_path)
    baseline_by_task = {task(row): row for row in baselines}
    if len(baseline_by_task) != len(baselines):
        raise RuntimeError("D148 duplicate exact baseline task")
    blocks = []
    best_one_by_task = {}
    seen_blocks = []
    for block, arms, fields in iter_arm_blocks(arms_path):
        seen_blocks.append(block)
        start = yt_d148.START_SEED + block * yt_d148.MAPS_PER_SHARD
        block_baselines = [
            row
            for row in baselines
            if start <= int(row["map_seed"]) < start + yt_d148.MAPS_PER_SHARD
        ]
        d113.START_SEED = start
        d113.MAPS = yt_d148.MAPS_PER_SHARD
        elapsed = float(metadata_by_shard[f"exact-{block:02d}"]["elapsed_seconds"])
        inherited, block_controls, arms_by_root = d113.zero_aware_mechanics(
            arms, block_baselines, fields, elapsed, {"pass": True}
        )
        mechanics = d133b.exact_mechanics_without_support_gate(inherited)
        if mechanics["pass"]:
            teacher, labels = d113.teacher_analysis(arms, block_controls, arms_by_root)
            labels = [{"block_id": block, **row} for row in labels]
            label_path = yt_d148.LOCAL_OUTPUT / f"exact-block-{block:02d}-labels.tsv"
            d112.write_labels(label_path, labels)
            label_artifact = {
                "path": str(label_path),
                "rows": len(labels),
                "bytes": label_path.stat().st_size,
                "sha256": yt_d148.sha256(label_path),
            }
        else:
            teacher = {"signal_pass": False, "safety_pass": False}
            label_artifact = {"path": None, "rows": 0, "bytes": 0, "sha256": None}
        arms_by_task = defaultdict(list)
        for row in arms:
            arms_by_task[task(row)].append(row)
        for key, control in block_controls.items():
            candidates = arms_by_task.get(key, [])
            best = max(candidates, key=lambda row: d112.tie_key(row, control)) if candidates else control
            if margin(best) <= margin(control):
                best = control
            best_one_by_task[key] = {
                **{field: str(best[field]) for field in TRANSFER_TERMINAL_FIELDS},
                "boundary_index": str(best.get("boundary_index", -1)),
                "slot": str(best.get("slot", 0)),
            }
        blocks.append(
            {
                "block": block,
                "start_seed": start,
                "maps": yt_d148.MAPS_PER_SHARD,
                "mechanics": mechanics,
                "teacher": teacher,
                "labels": label_artifact,
            }
        )
        del arms, arms_by_root, arms_by_task, block_controls
        gc.collect()
    mechanics_pass = (
        seen_blocks == list(range(yt_d148.SHARDS))
        and len(baseline_by_task) == 1024
        and len(best_one_by_task) == 1024
        and all(block["mechanics"]["pass"] for block in blocks)
    )
    aggregate_teacher = (
        d133.combine_teachers([block["teacher"] for block in blocks])
        if mechanics_pass
        else {"signal_pass": False, "safety_pass": False}
    )
    summary = {
        "blocks": blocks,
        "baselines": len(baselines),
        "best_one_tasks": len(best_one_by_task),
        "mechanics_pass": mechanics_pass,
        "teacher": aggregate_teacher,
        "pass": mechanics_pass
        and aggregate_teacher["signal_pass"]
        and aggregate_teacher["safety_pass"],
    }
    return summary, baseline_by_task, best_one_by_task


def validate_population(
    rows: list[dict[str, str]],
    fields: list[str],
    baseline_by_task: dict,
) -> tuple[dict, dict, dict]:
    grouped = defaultdict(list)
    indexed = Counter()
    failures = Counter()
    semantic_errors = 0
    starts = {
        yt_d148.START_SEED + index * yt_d148.MAPS_PER_SHARD
        for index in range(yt_d148.SHARDS)
    }
    for row in rows:
        key = task(row)
        grouped[key].append(row)
        scenario = int(row["scenario"])
        shard_start = int(row["map_seed"]) - scenario // runner.TASKS_PER_MAP
        indexed[(shard_start, int(row["task_index"]))] += 1
        for field in d112.FAILURE_FIELDS:
            failures[field] += int(row[field])
        try:
            spec = runner.runtime_spec(
                int(row["task_index"]),
                yt_d148.MAPS_PER_SHARD * runner.TASKS_PER_MAP,
                yt_d148.SEARCH_BUDGET,
            )
            expected = runner.expected_task(shard_start, scenario)
            interventions = int(row["intervention_batches"])
            valid = (
                shard_start in starts
                and scenario == int(spec["scenario"])
                and int(row["search_ordinal"]) == int(spec["search_ordinal"])
                and int(row["source_replica"]) == int(spec["source_replica"])
                and row["mode"] == spec["mode"]
                and int(row["scheduled_first_boundary"]) == int(spec["first"])
                and int(row["scheduled_second_boundary"]) == int(spec["second"])
                and key == expected
                and int(row["margin"]) == margin(row)
                and int(row["baseline_margin"])
                == int(row["baseline_own_score"]) - int(row["baseline_opponent_score"])
                and int(row["margin_delta"])
                == int(row["margin"]) - int(row["baseline_margin"])
                and 0 <= interventions <= (0 if row["mode"] == "control" else 2)
            )
            expected_hash = 0
            if interventions >= 1:
                valid = valid and (
                    int(row["first_selected_boundary"]) == int(spec["first"])
                    and int(row["first_selected_slot"]) > 0
                )
                expected_hash = runner.update_selection_hash(
                    expected_hash,
                    int(row["first_selected_boundary"]),
                    int(row["first_selected_slot"]),
                )
            else:
                valid = valid and int(row["first_selected_boundary"]) == -1
            if interventions == 2:
                valid = valid and (
                    int(row["second_selected_boundary"]) == int(spec["second"])
                    and int(row["second_selected_slot"]) > 0
                )
                expected_hash = runner.update_selection_hash(
                    expected_hash,
                    int(row["second_selected_boundary"]),
                    int(row["second_selected_slot"]),
                )
            else:
                valid = valid and int(row["second_selected_boundary"]) == -1
            valid = valid and int(row["selection_hash"]) == expected_hash
        except (KeyError, TypeError, ValueError):
            valid = False
        semantic_errors += int(not valid)

    controls = {}
    best_pair = {}
    group_errors = 0
    control_parity_errors = 0
    for key, task_rows in grouped.items():
        ordinals = Counter(int(row["search_ordinal"]) for row in task_rows)
        control = [row for row in task_rows if row["mode"] == "control"]
        doubles = [row for row in task_rows if row["mode"] == "double"]
        if (
            len(task_rows) != 65
            or ordinals != Counter(range(65))
            or len(control) != 1
            or len(doubles) != 64
        ):
            group_errors += 1
            continue
        controls[key] = control[0]
        exact = baseline_by_task.get(key)
        if exact is None or any(
            str(control[0][field]) != str(exact[field]) for field in CONTROL_PARITY_FIELDS
        ):
            control_parity_errors += 1
        pairs = [row for row in doubles if int(row["intervention_batches"]) == 2]
        if pairs:
            best_pair[key] = max(
                pairs, key=lambda row: runner.outcome_key(row, control[0])
            )
    expected = expected_tasks()
    summary = {
        "rows": len(rows),
        "schema_exact": fields == list(runner.POPULATION_FIELDS),
        "tasks": len(grouped),
        "unique_shard_task_indices": len(indexed),
        "duplicate_shard_task_indices": sum(value != 1 for value in indexed.values()),
        "group_errors": group_errors,
        "semantic_errors": semantic_errors,
        "control_parity_errors": control_parity_errors,
        "mechanical_failures": dict(sorted(failures.items())),
        "tasks_with_executed_pair": len(best_pair),
    }
    summary["pass"] = (
        summary["schema_exact"]
        and len(rows) == 66_560
        and set(grouped) == expected
        and len(indexed) == 66_560
        and not summary["duplicate_shard_task_indices"]
        and not group_errors
        and not semantic_errors
        and not control_parity_errors
        and not any(failures.values())
    )
    return summary, controls, best_pair


def validate_manifest_and_replays(
    manifest: list[dict[str, str]],
    manifest_fields: list[str],
    replays: list[dict[str, str]],
    replay_fields: list[str],
    best_pair: dict,
) -> tuple[dict, dict]:
    manifest_by_task = {task(row): row for row in manifest}
    replay_by_task = {task(row): row for row in replays}
    failures = Counter()
    if len(manifest_by_task) != len(manifest):
        failures["duplicate_manifest_task"] += 1
    if len(replay_by_task) != len(replays):
        failures["duplicate_replay_task"] += 1
    for key, reference in best_pair.items():
        selected = manifest_by_task.get(key)
        replay = replay_by_task.get(key)
        if selected is None:
            failures["missing_manifest"] += 1
            continue
        compare = {
            "scenario": reference["scenario"],
            "map_seed": reference["map_seed"],
            "seat": reference["seat"],
            "opponent": reference["opponent"],
            "search_ordinal": reference["search_ordinal"],
            "source_replica": reference["source_replica"],
            "scheduled_first_boundary": reference["scheduled_first_boundary"],
            "scheduled_second_boundary": reference["scheduled_second_boundary"],
            "first_boundary": reference["first_selected_boundary"],
            "first_slot": reference["first_selected_slot"],
            "second_boundary": reference["second_selected_boundary"],
            "second_slot": reference["second_selected_slot"],
            "selection_hash": reference["selection_hash"],
            "control_margin": reference["baseline_margin"],
            "sequence_margin": reference["margin"],
            "sequence_gain_over_control": reference["margin_delta"],
        }
        if any(str(selected[field]) != str(value) for field, value in compare.items()):
            failures["manifest_best_pair_mismatch"] += 1
        if replay is None:
            failures["missing_replay"] += 1
        elif any(
            replay[field] != reference[field] for field in runner.TERMINAL_FIELDS
        ):
            failures["replay_terminal_mismatch"] += 1
    if set(manifest_by_task) != set(best_pair):
        failures["manifest_task_set"] += 1
    if set(replay_by_task) != set(best_pair):
        failures["replay_task_set"] += 1
    summary = {
        "manifest_rows": len(manifest),
        "replay_rows": len(replays),
        "manifest_schema_exact": manifest_fields == list(runner.MANIFEST_FIELDS),
        "replay_schema_exact": replay_fields == list(runner.REPLAY_FIELDS),
        "failures": dict(sorted(failures.items())),
    }
    summary["pass"] = (
        summary["manifest_schema_exact"]
        and summary["replay_schema_exact"]
        and not failures
    )
    return summary, manifest_by_task


def validate_candidate_group(group: list[dict[str, str]]) -> Counter:
    failures = Counter()
    first = group[0]
    legal = int(first["legal_candidates"])
    slots = [int(row["candidate_slot"]) for row in group]
    chosen = [row for row in group if int(row["chosen"]) == 1]
    if len(group) != legal:
        failures["legal_count"] += 1
    if len(slots) != len(set(slots)):
        failures["duplicate_candidate"] += 1
    if 0 not in slots:
        failures["missing_control"] += 1
    if int(first["chosen_slot"]) not in slots:
        failures["missing_chosen"] += 1
    if len(chosen) != 1:
        failures["chosen_count"] += 1
    else:
        selected = chosen[0]
        slot = int(selected["candidate_slot"])
        if slot != int(selected["chosen_slot"]):
            failures["chosen_slot_mismatch"] += 1
        if selected["stage"].startswith("wait_") and slot != 0:
            failures["wait_noncontrol"] += 1
        if selected["stage"] in {"first", "second"} and slot == 0:
            failures["selected_control"] += 1
        if slot and not any(float(selected[field]) != 0.0 for field in runner.ACTION_FIELDS):
            failures["selected_action_all_zero"] += 1
    state = tuple(first[field] for field in runner.STATE_FIELDS)
    metadata_fields = tuple(
        field
        for field in runner.CANDIDATE_FIELDS[:11]
        if field not in {"candidate_slot", "chosen"}
    )
    metadata = tuple(first[field] for field in metadata_fields)
    if any(tuple(row[field] for field in runner.STATE_FIELDS) != state for row in group):
        failures["state_inconsistent"] += 1
    if any(
        tuple(row[field] for field in metadata_fields) != metadata
        for row in group
    ):
        failures["metadata_inconsistent"] += 1
    controls = [row for row in group if int(row["candidate_slot"]) == 0]
    if len(controls) != 1 or any(
        float(row[field]) != 0.0
        for row in controls
        for field in runner.ACTION_FIELDS
    ):
        failures["control_action_nonzero"] += 1
    return failures


def analyze_candidates(path: Path, manifest_by_task: dict) -> dict:
    feature_fields = runner.STATE_FIELDS + runner.ACTION_FIELDS
    failures = Counter()
    stages = Counter()
    groups = 0
    rows = 0
    nonfinite = 0
    seen_groups = set()
    current_key = None
    current = []

    def finish() -> None:
        nonlocal groups, current
        if not current:
            return
        groups += 1
        failures.update(validate_candidate_group(current))
        chosen = [row for row in current if int(row["chosen"]) == 1]
        if len(chosen) == 1:
            stages[chosen[0]["stage"]] += 1
        current = []

    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = list(reader.fieldnames or ())
        for row in reader:
            rows += 1
            key = (*task(row), int(row["boundary"]))
            if current_key is None:
                current_key = key
            if key != current_key:
                finish()
                if key in seen_groups:
                    failures["noncontiguous_group"] += 1
                seen_groups.add(current_key)
                current_key = key
            for field in feature_fields:
                try:
                    nonfinite += int(not math.isfinite(float(row[field])))
                except (KeyError, TypeError, ValueError):
                    failures["feature_parse"] += 1
            current.append(row)
        finish()
        if current_key is not None:
            seen_groups.add(current_key)
    expected_groups = sum(int(row["second_boundary"]) + 1 for row in manifest_by_task.values())
    summary = {
        "rows": rows,
        "columns": len(fields),
        "feature_columns": len(feature_fields),
        "schema_exact": fields == list(runner.CANDIDATE_FIELDS),
        "groups": groups,
        "expected_groups": expected_groups,
        "stage_counts": dict(sorted(stages.items())),
        "nonfinite_values": nonfinite,
        "failures": dict(sorted(failures.items())),
    }
    summary["pass"] = (
        summary["schema_exact"]
        and len(feature_fields) == 443
        and groups == expected_groups
        and stages["first"] == len(manifest_by_task)
        and stages["second"] == len(manifest_by_task)
        and not nonfinite
        and not failures
    )
    return summary


def transfer_analysis(
    controls: dict,
    best_one: dict,
    best_pair: dict,
) -> tuple[dict, list[dict]]:
    enriched = []
    targets = []
    for key in sorted(expected_tasks()):
        control = controls[key]
        one = best_one[key]
        pair = best_pair.get(key)
        one_margin = margin(one)
        pair_margin = margin(pair) if pair is not None else one_margin
        selected_pair = pair is not None and pair_margin > one_margin
        combined = pair if selected_pair else one
        increment = margin(combined) - one_margin
        enriched.append(
            {
                "task": key,
                "opponent": key[2],
                "block": (key[0] - yt_d148.START_SEED) // 16,
                "increment": increment,
                "strict": increment > 0,
                "own_increment": int(combined["own_score"]) - int(one["own_score"]),
                "opponent_increment": int(combined["opponent_score"])
                - int(one["opponent_score"]),
                "new_crop_failure": int(one["own_created_crops"]) > 0
                and int(combined["own_created_crops"]) == 0,
                "one_worker_three": int(one["own_workers"]) >= 3,
                "combined_worker_three": int(combined["own_workers"]) >= 3,
            }
        )
        if pair is not None:
            targets.append(
                {
                    "map_seed": key[0],
                    "seat": key[1],
                    "opponent": key[2],
                    "eight_map_fold": (key[0] - yt_d148.START_SEED)
                    // yt_d148.MAPS_PER_SHARD,
                    "source_replica": int(pair["source_replica"]),
                    "first_boundary": int(pair["first_selected_boundary"]),
                    "first_slot": int(pair["first_selected_slot"]),
                    "second_boundary": int(pair["second_selected_boundary"]),
                    "second_slot": int(pair["second_selected_slot"]),
                    "selection_hash": int(pair["selection_hash"]),
                    "control_margin": margin(control),
                    "one_use_boundary": int(one["boundary_index"]),
                    "one_use_slot": int(one["slot"]),
                    "one_use_margin": one_margin,
                    "sequence_margin": pair_margin,
                    "sequence_gain_over_control": pair_margin - margin(control),
                    "increment_beyond_one_use": pair_margin - one_margin,
                    "target_active": int(selected_pair),
                }
            )

    def view(items: list[dict]) -> dict:
        return {
            "tasks": len(items),
            "mean_increment_beyond_one_use": d112.mean(row["increment"] for row in items),
            "strict_increment_tasks": sum(row["strict"] for row in items),
            "strict_increment_rate": d112.mean(row["strict"] for row in items),
            "mean_own_score_increment": d112.mean(row["own_increment"] for row in items),
            "mean_opponent_score_increment": d112.mean(
                row["opponent_increment"] for row in items
            ),
            "new_crop_failures": sum(row["new_crop_failure"] for row in items),
            "one_use_worker_three_rate": d112.mean(row["one_worker_three"] for row in items),
            "combined_worker_three_rate": d112.mean(
                row["combined_worker_three"] for row in items
            ),
        }

    aggregate = view(enriched)
    family = {
        opponent: d112.mean(
            row["increment"] for row in enriched if row["opponent"] == opponent
        )
        for opponent in d112.OPPONENTS
    }
    aggregate["family_mean_increment"] = family
    aggregate["positive_families"] = sum(value > 0 for value in family.values())
    aggregate["worst_family_increment"] = min(family.values())
    blocks = {
        str(block): view([row for row in enriched if row["block"] == block])
        for block in range(4)
    }
    gates = {
        "mean_increment_at_least_2_5": aggregate["mean_increment_beyond_one_use"] >= 2.5,
        "strict_increment_at_least_20pct": aggregate["strict_increment_rate"] >= 0.20,
        "at_least_six_positive_families": aggregate["positive_families"] >= 6,
        "worst_family_nonnegative": aggregate["worst_family_increment"] >= 0.0,
        "no_new_crop_failures": aggregate["new_crop_failures"] == 0,
        "worker_three_within_5pp": aggregate["combined_worker_three_rate"]
        >= aggregate["one_use_worker_three_rate"] - 0.05,
        "all_four_blocks_positive_mean": all(
            block["mean_increment_beyond_one_use"] > 0 for block in blocks.values()
        ),
        "at_least_three_blocks_strict_15pct": sum(
            block["strict_increment_rate"] >= 0.15 for block in blocks.values()
        )
        >= 3,
    }
    return {
        "aggregate": aggregate,
        "blocks": blocks,
        "gates": gates,
        "pass": all(gates.values()),
    }, targets


def write_targets(rows: list[dict]) -> dict:
    if TARGETS.exists():
        raise FileExistsError(TARGETS)
    with TARGETS.open("x", newline="") as target_file:
        writer = csv.DictWriter(
            target_file, fieldnames=TARGET_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return {
        "path": str(TARGETS),
        "rows": len(rows),
        "active_rows": sum(int(row["target_active"]) for row in rows),
        "bytes": TARGETS.stat().st_size,
        "sha256": yt_d148.sha256(TARGETS),
    }


def main() -> int:
    lock = yt_d148.verify_lock()
    download = json.loads(yt_d148.DOWNLOAD_RECORD.read_text())
    if download["operation"]["state"] != "completed":
        raise RuntimeError("D148 download is not from a completed operation")
    for summary in download["outputs"].values():
        path = Path(summary["path"])
        if yt_d148.sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D148 downloaded artifact changed: {path}")
    metadata = download["mapper_metadata"]
    metadata_by_shard = {item["shard_id"]: item for item in metadata}
    specs = yt_d148.build_specs()
    infrastructure_gates = {
        "operation_completed": download["operation"]["state"] == "completed",
        "exactly_16_metadata_rows": len(metadata) == 16,
        "exact_prescribed_shards": set(metadata_by_shard)
        == {str(spec["shard_id"]) for spec in specs},
        "all_shards_used_16_threads": all(int(item["threads"]) == 16 for item in metadata),
        "joint_shards_within_2700_seconds": all(
            float(item["elapsed_seconds"]) <= yt_d148.JOINT_MAX_ACTIVE_SECONDS
            for item in metadata
            if item["kind"] == "joint"
        ),
        "exact_shards_within_1200_seconds": all(
            float(item["elapsed_seconds"]) <= yt_d148.EXACT_MAX_ACTIVE_SECONDS
            for item in metadata
            if item["kind"] == "exact"
        ),
    }
    outputs = download["outputs"]
    exact, baseline_by_task, best_one = analyze_exact(
        Path(outputs["arms"]["path"]),
        Path(outputs["baselines"]["path"]),
        metadata_by_shard,
    )
    population_rows, population_fields = read_table(Path(outputs["population"]["path"]))
    population, controls, best_pair = validate_population(
        population_rows, population_fields, baseline_by_task
    )
    manifest_rows, manifest_fields = read_table(Path(outputs["manifest"]["path"]))
    replay_rows, replay_fields = read_table(Path(outputs["replays"]["path"]))
    selected, manifest_by_task = validate_manifest_and_replays(
        manifest_rows, manifest_fields, replay_rows, replay_fields, best_pair
    )
    candidates = analyze_candidates(Path(outputs["candidates"]["path"]), manifest_by_task)
    mechanics_pass = exact["pass"] and population["pass"] and selected["pass"] and candidates["pass"]
    if mechanics_pass:
        transfer, target_rows = transfer_analysis(controls, best_one, best_pair)
        targets = write_targets(target_rows)
    else:
        transfer = {"pass": False, "not_interpreted": "D148 mechanics failure"}
        targets = {"path": None, "rows": 0, "active_rows": 0, "sha256": None}
    full_pass = all(infrastructure_gates.values()) and mechanics_pass and transfer["pass"]
    result = {
        "schema": "troll-farm-d148a-priority-joint-teacher-corpus-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": download["operation"],
        "panel": {
            "training_start_seed": yt_d148.START_SEED,
            "training_maps": yt_d148.MAPS,
            "training_tasks": 1024,
            "reserved_validation_start_seed": yt_d148.VALIDATION_START_SEED,
            "reserved_validation_maps": yt_d148.VALIDATION_MAPS,
        },
        "infrastructure": {
            "gates": infrastructure_gates,
            "pass": all(infrastructure_gates.values()),
            "metadata": metadata,
        },
        "exact_one_use": exact,
        "population": population,
        "selected_replays": selected,
        "candidates": candidates,
        "mechanics_pass": mechanics_pass,
        "transfer": transfer,
        "targets": targets,
        "full_pass": full_pass,
        "decision": (
            "open_d149_grouped_joint_two_stage_policy_fit"
            if full_pass
            else "close_nontransferring_d148_population"
            if mechanics_pass and not transfer["pass"]
            else "repair_d148_infrastructure_or_mechanics_only"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
