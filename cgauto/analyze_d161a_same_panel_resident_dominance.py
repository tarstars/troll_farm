#!/usr/bin/env python3
"""Audit D148's hindsight q6 envelope against the exact resident on one panel."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Iterable, Mapping

from cgauto import analyze_d102a_complete_macro_resident_transfer as d102
from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d148a_priority_joint_teacher as d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d161a-same-panel-resident-dominance-protocol-2026-07-23.md"
LOCK = BASE / "d161a-same-panel-resident-dominance-lock.json"
D148_DOWNLOAD = BASE / "d148a-priority-joint-teacher-corpus-download.json"
D148B_RESULT = BASE / "d148b-priority-joint-support-semantics-result.json"
D148_TARGETS = BASE / "d148a-joint-trajectory-targets-9844136-9844199.tsv"
RUN_A = BASE / "d161a-resident-d40-panel-jobs1-9844136-9844199.tsv"
RUN_B = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
OUTPUT = BASE / "d161a-same-panel-resident-dominance-result.json"

START_SEED = 9_844_136
MAP_COUNT = 64
RESERVED_START_SEED = 9_844_200
RESERVED_MAP_COUNT = 16
POLICIES = ("d40", "resident")
OPPONENTS = tuple(d112.OPPONENTS)
YT_ROOT = "//home/delivery_ml/research/tarstars/troll_farm"

D40_PARITY_INT_FIELDS = (
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
)
D40_PARITY_FLOAT_FIELDS = ("own_return", "opponent_return", "margin_return")
MECHANICAL_FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def task_key(row: Mapping[str, object]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def margin(row: Mapping[str, object]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "path": str(LOCK.relative_to(ROOT)),
        "sha256": sha256(LOCK),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def verify_d148_download(download: dict) -> dict:
    artifacts = {}
    for name, declared in download["outputs"].items():
        path = Path(declared["path"])
        actual = sha256(path) if path.exists() else None
        artifacts[name] = {
            "path": str(path),
            "declared_sha256": declared["sha256"],
            "actual_sha256": actual,
            "pass": actual == declared["sha256"],
        }
    operation_paths = download["operation"].get("paths", {})
    canonical_paths = bool(operation_paths) and all(
        str(path) == YT_ROOT or str(path).startswith(f"{YT_ROOT}/")
        for path in operation_paths.values()
    )
    gates = {
        "completed_operation": download["operation"].get("state") == "completed",
        "all_downloaded_artifacts_match_declared_hashes": all(
            item["pass"] for item in artifacts.values()
        ),
        "operation_uses_canonical_yt_root": canonical_paths,
    }
    return {"artifacts": artifacts, "gates": gates, "pass": all(gates.values())}


def arm_tie_key(row: Mapping[str, object], control: Mapping[str, object]) -> tuple[int, int, int, int]:
    """Mirror D112's deterministic best-arm ordering without retaining wide rows."""

    return (
        margin(row) - margin(control),
        int(row["own_score"]) - int(control["own_score"]),
        -(int(row["opponent_score"]) - int(control["opponent_score"])),
        -int(row["slot"]),
    )


def choose_best_one(
    control: Mapping[str, object], candidates: Iterable[Mapping[str, object]]
) -> dict[str, str]:
    candidates = list(candidates)
    best = max(candidates, key=lambda row: arm_tie_key(row, control)) if candidates else control
    if margin(best) <= margin(control):
        best = control
    return {
        **{field: str(best[field]) for field in d148.TRANSFER_TERMINAL_FIELDS},
        "boundary_index": str(best.get("boundary_index", -1)),
        "slot": str(best.get("slot", 0)),
    }


def stream_best_one(
    arms_path: Path, baseline_by_task: Mapping[tuple[int, int, str], Mapping[str, object]]
) -> tuple[dict, dict[tuple[int, int, str], dict[str, str]]]:
    """Reconstruct all best one-use terminal rows while keeping the 503 MB table streaming."""

    best_arm: dict[tuple[int, int, str], dict[str, str]] = {}
    best_key: dict[tuple[int, int, str], tuple[int, int, int, int]] = {}
    rows = 0
    malformed_margins = 0
    unexpected_tasks = 0
    with arms_path.open(newline="") as source:
        reader = csv.reader(source, delimiter="\t")
        fields = next(reader)
        index = {field: position for position, field in enumerate(fields)}
        required = {
            "map_seed",
            "seat",
            "opponent",
            "boundary_index",
            "slot",
            *d148.TRANSFER_TERMINAL_FIELDS,
        }
        missing_fields = sorted(required - set(index))
        if missing_fields:
            raise RuntimeError(f"D148 arms missing fields: {missing_fields}")
        wanted = tuple(required)
        for values in reader:
            rows += 1
            row = {field: values[index[field]] for field in wanted}
            key = task_key(row)
            control = baseline_by_task.get(key)
            if control is None:
                unexpected_tasks += 1
                continue
            malformed_margins += int(int(row["margin"]) != margin(row))
            tie = arm_tie_key(row, control)
            if key not in best_key or tie > best_key[key]:
                best_key[key] = tie
                best_arm[key] = row

    best_one = {
        key: choose_best_one(control, [best_arm[key]] if key in best_arm else [])
        for key, control in baseline_by_task.items()
    }
    gains = [margin(best_one[key]) - margin(control) for key, control in baseline_by_task.items()]
    expected_arm_tasks = {
        key for key, control in baseline_by_task.items() if int(control["boundary_count"]) > 0
    }
    arm_task_set_exact = set(best_arm) == expected_arm_tasks
    summary = {
        "rows": rows,
        "tasks_with_arms": len(best_arm),
        "tasks_with_positive_boundary_count": len(expected_arm_tasks),
        "arm_task_set_matches_positive_boundary_tasks": arm_task_set_exact,
        "best_one_tasks": len(best_one),
        "unexpected_tasks": unexpected_tasks,
        "malformed_margins": malformed_margins,
        "strict_improvement_tasks_vs_d40": sum(value > 0 for value in gains),
        "strict_improvement_rate_vs_d40": mean(value > 0 for value in gains),
        "mean_margin_gain_vs_d40": mean(gains),
    }
    summary["pass"] = (
        rows == 88_469
        and len(baseline_by_task) == len(best_one) == 1_024
        and arm_task_set_exact
        and not unexpected_tasks
        and not malformed_margins
    )
    return summary, best_one


def normalized_rows(rows: Iterable[Mapping[str, object]], fields: Iterable[str]) -> list[tuple[str, ...]]:
    fields = tuple(fields)
    return [tuple(str(row[field]) for field in fields) for row in rows]


def reconstruct_d148(download: dict) -> tuple[dict, dict, dict, dict]:
    outputs = download["outputs"]
    baselines, baseline_fields = d148.read_table(Path(outputs["baselines"]["path"]))
    baseline_by_task = {task_key(row): row for row in baselines}
    duplicate_baselines = len(baseline_by_task) != len(baselines)
    best_summary, best_one = stream_best_one(
        Path(outputs["arms"]["path"]), baseline_by_task
    )

    population_rows, population_fields = d148.read_table(Path(outputs["population"]["path"]))
    population, controls, best_pair = d148.validate_population(
        population_rows, population_fields, baseline_by_task
    )
    manifest_rows, manifest_fields = d148.read_table(Path(outputs["manifest"]["path"]))
    replay_rows, replay_fields = d148.read_table(Path(outputs["replays"]["path"]))
    selected, manifest_by_task = d148.validate_manifest_and_replays(
        manifest_rows, manifest_fields, replay_rows, replay_fields, best_pair
    )
    transfer, expected_target_rows = d148.transfer_analysis(controls, best_one, best_pair)
    target_rows, target_fields = d148.read_table(D148_TARGETS)
    targets_exact = (
        target_fields == list(d148.TARGET_FIELDS)
        and normalized_rows(target_rows, d148.TARGET_FIELDS)
        == normalized_rows(expected_target_rows, d148.TARGET_FIELDS)
    )
    frozen_d148b = json.loads(D148B_RESULT.read_text())
    transfer_exact = transfer == frozen_d148b["transfer"]
    target_hash_exact = sha256(D148_TARGETS) == frozen_d148b["targets"]["sha256"]

    combined = {}
    for key in sorted(expected_tasks()):
        one = best_one[key]
        pair = best_pair.get(key)
        combined[key] = pair if pair is not None and margin(pair) > margin(one) else one

    gates = {
        "baseline_schema_contains_required_fields": set(D40_PARITY_INT_FIELDS)
        | set(D40_PARITY_FLOAT_FIELDS)
        <= set(baseline_fields),
        "exactly_1024_unique_baselines": (
            len(baselines) == 1_024
            and not duplicate_baselines
            and set(baseline_by_task) == expected_tasks()
        ),
        "best_one_stream_reconstruction_passed": best_summary["pass"],
        "population_validation_passed": population["pass"],
        "manifest_and_replay_validation_passed": selected["pass"],
        "manifest_indexes_every_selected_pair": set(manifest_by_task) == set(best_pair),
        "target_rows_reproduced_exactly": targets_exact,
        "target_hash_matches_frozen_d148b": target_hash_exact,
        "transfer_aggregates_match_frozen_d148b": transfer_exact,
        "combined_envelope_has_all_tasks": set(combined) == expected_tasks(),
    }
    summary = {
        "gates": gates,
        "pass": all(gates.values()),
        "best_one": best_summary,
        "population": population,
        "selected_replays": selected,
        "target_rows": len(target_rows),
        "active_target_rows": sum(int(row["target_active"]) for row in target_rows),
        "transfer": transfer,
    }
    return summary, baseline_by_task, best_one, combined


def validate_runner_rows(rows: list[dict]) -> tuple[dict, dict]:
    expected = {
        (seed, seat, opponent, policy)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
        for policy in POLICIES
    }
    keys = [(*task_key(row), row["policy"]) for row in rows]
    indexed = {(*task_key(row), row["policy"]): row for row in rows}
    failures = {
        field: sum(int(row[field]) for row in rows) for field in MECHANICAL_FAILURE_FIELDS
    }
    margin_errors = sum(row["margin"] != margin(row) for row in rows)
    reward_errors = sum(
        max(
            abs(row["own_return"] - row["own_score"] / 100.0),
            abs(row["opponent_return"] - row["opponent_score"] / 100.0),
            abs(row["margin_return"] - row["margin"] / 100.0),
            abs(row["reward_identity_error"]),
        )
        > 1e-6
        for row in rows
    )
    summary = {
        "rows": len(rows),
        "expected_rows": len(expected),
        "unique_keys": len(indexed),
        "duplicate_rows": len(keys) - len(set(keys)),
        "missing_rows": len(expected - set(keys)),
        "unexpected_rows": len(set(keys) - expected),
        "unfinished_rows": sum(not row["done"] for row in rows),
        "margin_identity_errors": margin_errors,
        "reward_identity_errors": reward_errors,
        "mechanical_failures": failures,
    }
    summary["pass"] = (
        len(rows) == len(expected)
        and set(keys) == expected
        and len(keys) == len(set(keys))
        and not summary["unfinished_rows"]
        and not margin_errors
        and not reward_errors
        and not any(failures.values())
    )
    return summary, indexed


def d40_parity(
    runner_index: Mapping[tuple[int, int, str, str], Mapping[str, object]],
    baseline_by_task: Mapping[tuple[int, int, str], Mapping[str, object]],
) -> dict:
    mismatches = Counter()
    samples = []
    for key in sorted(expected_tasks()):
        row = runner_index.get((*key, "d40"))
        baseline = baseline_by_task.get(key)
        if row is None or baseline is None:
            mismatches["missing_task"] += 1
            continue
        for field in D40_PARITY_INT_FIELDS:
            if int(row[field]) != int(baseline[field]):
                mismatches[field] += 1
                if len(samples) < 10:
                    samples.append(
                        {"task": key, "field": field, "runner": row[field], "d148": baseline[field]}
                    )
        for field in D40_PARITY_FLOAT_FIELDS:
            if not math.isclose(
                float(row[field]), float(baseline[field]), rel_tol=0.0, abs_tol=1e-7
            ):
                mismatches[field] += 1
                if len(samples) < 10:
                    samples.append(
                        {"task": key, "field": field, "runner": row[field], "d148": baseline[field]}
                    )
    return {
        "tasks": len(expected_tasks()),
        "integer_fields": list(D40_PARITY_INT_FIELDS),
        "float_fields": list(D40_PARITY_FLOAT_FIELDS),
        "float_absolute_tolerance": 1e-7,
        "mismatches": dict(sorted(mismatches.items())),
        "samples": samples,
        "pass": not mismatches,
    }


def outcome_summary(rows: Iterable[Mapping[str, object]]) -> dict:
    rows = list(rows)
    margins = [margin(row) for row in rows]
    return {
        "tasks": len(rows),
        "mean_own_score": mean(int(row["own_score"]) for row in rows),
        "mean_opponent_score": mean(int(row["opponent_score"]) for row in rows),
        "mean_margin": mean(margins),
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def comparison_metrics(
    resident: Mapping[tuple[int, int, str], Mapping[str, object]],
    candidate: Mapping[tuple[int, int, str], Mapping[str, object]],
) -> dict:
    if set(resident) != set(candidate):
        raise ValueError("resident and candidate task sets differ")
    rows = []
    family = defaultdict(list)
    maps = defaultdict(list)
    blocks = defaultdict(list)
    for key in sorted(resident):
        resident_row = resident[key]
        candidate_row = candidate[key]
        row = {
            "task": key,
            "margin_delta": margin(candidate_row) - margin(resident_row),
            "own_score_delta": int(candidate_row["own_score"]) - int(resident_row["own_score"]),
            "opponent_score_delta": int(candidate_row["opponent_score"])
            - int(resident_row["opponent_score"]),
        }
        rows.append(row)
        family[key[2]].append(row)
        maps[key[0]].append(row)
        blocks[(key[0] - START_SEED) // 16].append(row)

    margin_deltas = [row["margin_delta"] for row in rows]
    map_means = [mean(row["margin_delta"] for row in group) for _, group in sorted(maps.items())]
    map_sd = statistics.stdev(map_means) if len(map_means) > 1 else 0.0
    half_width = 1.96 * map_sd / math.sqrt(len(map_means)) if map_means else math.inf

    def grouped_view(group: list[dict]) -> dict:
        return {
            "tasks": len(group),
            "mean_margin_delta": mean(row["margin_delta"] for row in group),
            "mean_own_score_delta": mean(row["own_score_delta"] for row in group),
            "mean_opponent_score_delta": mean(row["opponent_score_delta"] for row in group),
            "strict_improvement_rate": mean(row["margin_delta"] > 0 for row in group),
            "tie_rate": mean(row["margin_delta"] == 0 for row in group),
            "strict_regression_rate": mean(row["margin_delta"] < 0 for row in group),
        }

    aggregate = grouped_view(rows)
    aggregate.update(
        {
            "median_margin_delta": statistics.median(margin_deltas),
            "strict_improvement_tasks": sum(value > 0 for value in margin_deltas),
            "tie_tasks": sum(value == 0 for value in margin_deltas),
            "strict_regression_tasks": sum(value < 0 for value in margin_deltas),
            "map_clustered_normal_95pct_interval": [
                mean(map_means) - half_width,
                mean(map_means) + half_width,
            ],
            "map_mean_delta_sd": map_sd,
        }
    )
    families = {
        opponent: grouped_view(family[opponent]) for opponent in OPPONENTS
    }
    block_views = {
        str(block): grouped_view(blocks[block]) for block in range(4)
    }
    family_means = [view["mean_margin_delta"] for view in families.values()]
    return {
        "resident": outcome_summary(resident.values()),
        "candidate": outcome_summary(candidate.values()),
        "delta": aggregate,
        "families": families,
        "blocks": block_views,
        "positive_families": sum(value > 0 for value in family_means),
        "worst_family_mean_margin_delta": min(family_means),
    }


def value_gates(metrics: Mapping[str, object]) -> dict:
    delta = metrics["delta"]
    candidate = metrics["candidate"]
    resident = metrics["resident"]
    gates = {
        "mean_margin_delta_at_least_5": delta["mean_margin_delta"] >= 5.0,
        "map_clustered_95pct_lower_bound_above_zero": delta[
            "map_clustered_normal_95pct_interval"
        ][0]
        > 0.0,
        "strict_improvement_rate_at_least_55pct": delta["strict_improvement_rate"] >= 0.55,
        "strict_regression_rate_at_most_35pct": delta["strict_regression_rate"] <= 0.35,
        "at_least_six_positive_families": metrics["positive_families"] >= 6,
        "worst_family_at_least_minus_5": metrics["worst_family_mean_margin_delta"] >= -5.0,
        "all_four_blocks_positive": all(
            block["mean_margin_delta"] > 0.0 for block in metrics["blocks"].values()
        ),
        "own_nonnegative_or_opponent_nonpositive": (
            delta["mean_own_score_delta"] >= 0.0
            or delta["mean_opponent_score_delta"] <= 0.0
        ),
        "catastrophe_count_not_above_resident": candidate["catastrophe_count"]
        <= resident["catastrophe_count"],
        "negative_margin_mass_not_above_resident": candidate["negative_margin_mass"]
        <= resident["negative_margin_mass"],
    }
    return {"gates": gates, "pass": all(gates.values())}


def analyze(run_a: Path, run_b: Path) -> dict:
    lock = verify_lock()
    download = json.loads(D148_DOWNLOAD.read_text())
    download_integrity = verify_d148_download(download)
    d148_reconstruction, baselines, best_one, combined = reconstruct_d148(download)

    repeated_exact = run_a.read_bytes() == run_b.read_bytes()
    rows_a = d102.read_rows(run_a)
    rows_b = d102.read_rows(run_b)
    grid_a, index_a = validate_runner_rows(rows_a)
    grid_b, _ = validate_runner_rows(rows_b)
    parity = d40_parity(index_a, baselines)
    resident = {key[:3]: row for key, row in index_a.items() if key[3] == "resident"}
    d40 = {key[:3]: row for key, row in index_a.items() if key[3] == "d40"}

    comparisons = {
        "d40": comparison_metrics(resident, d40),
        "best_one_use": comparison_metrics(resident, best_one),
        "combined_priority_joint": comparison_metrics(resident, combined),
    }
    value = {
        "best_one_use": value_gates(comparisons["best_one_use"]),
        "combined_priority_joint": value_gates(comparisons["combined_priority_joint"]),
    }
    d148_gain = mean(
        margin(combined[key]) - margin(d40[key]) for key in sorted(expected_tasks())
    )
    expected_gain = (
        d148_reconstruction["best_one"]["mean_margin_gain_vs_d40"]
        + d148_reconstruction["transfer"]["aggregate"]["mean_increment_beyond_one_use"]
    )
    cross_checks = {
        "combined_mean_gain_over_d40": d148_gain,
        "best_one_plus_joint_increment": expected_gain,
        "gain_decomposition_error": abs(d148_gain - expected_gain),
        "gain_decomposition_exact": math.isclose(
            d148_gain, expected_gain, rel_tol=0.0, abs_tol=1e-12
        ),
    }

    integrity_gates = {
        "frozen_lock_matches": lock["pass"],
        "d148_download_and_canonical_yt_root_match": download_integrity["pass"],
        "d148_envelope_reconstructed_exactly": d148_reconstruction["pass"],
        "jobs1_and_jobs20_byte_identical": repeated_exact,
        "jobs1_grid_and_mechanics_pass": grid_a["pass"],
        "jobs20_grid_and_mechanics_pass": grid_b["pass"],
        "d102_d40_matches_d148_baseline": parity["pass"],
        "combined_gain_decomposes_exactly": cross_checks["gain_decomposition_exact"],
        "reserved_maps_excluded": START_SEED + MAP_COUNT == RESERVED_START_SEED,
    }
    integrity_pass = all(integrity_gates.values())
    combined_pass = integrity_pass and value["combined_priority_joint"]["pass"]
    decision = (
        "repair_d161_measurement_before_interpretation"
        if not integrity_pass
        else "open_resident_relative_q6_learning_preflight"
        if combined_pass
        else "close_d40_q6_substrate_and_build_native_resident_control_representation"
    )
    return {
        "schema": "troll-farm-d161a-same-panel-resident-dominance-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "canonical_yt_root": YT_ROOT,
        "panel": {
            "start_seed": START_SEED,
            "maps": MAP_COUNT,
            "tasks": len(expected_tasks()),
            "reserved_start_seed": RESERVED_START_SEED,
            "reserved_maps": RESERVED_MAP_COUNT,
            "platform_requests": 0,
            "yt_requests": 0,
        },
        "lock": lock,
        "inputs": {
            "run_jobs1": {"path": str(run_a), "sha256": sha256(run_a)},
            "run_jobs20": {"path": str(run_b), "sha256": sha256(run_b)},
            "d148_download": {
                "path": str(D148_DOWNLOAD.relative_to(ROOT)),
                "sha256": sha256(D148_DOWNLOAD),
            },
            "download_integrity": download_integrity,
        },
        "d148_reconstruction": d148_reconstruction,
        "runner_validation": {"jobs1": grid_a, "jobs20": grid_b},
        "d40_parity": parity,
        "cross_checks": cross_checks,
        "integrity": {"gates": integrity_gates, "pass": integrity_pass},
        "comparisons": comparisons,
        "value": value,
        "pass": combined_pass,
        "decision": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", type=Path, default=RUN_A)
    parser.add_argument("--run-b", type=Path, default=RUN_B)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = analyze(args.run_a, args.run_b)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
