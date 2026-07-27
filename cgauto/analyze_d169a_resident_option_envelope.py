#!/usr/bin/env python3
"""Validate and analyze D169a's resident-native option-interface envelope gate.

Computes the unified crop-safe hindsight envelope over the exact resident
(CONTROL), OPT_RETURN (D168a's ARM_A BANK_SEED successor return), and
OPT_FRUIT/OPT_IRON/OPT_PROTECT (D163's three resource-control components,
each singly enabled, at three fixed starts plus an observable-trigger TRIG
start), and evaluates it against the frozen B2.1 gate thresholds. See
`data/analysis/live-agent-6553250/d169a-resident-option-interface-envelope-protocol-2026-07-27.md`.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d169a-resident-option-envelope"
PROTOCOL = BASE / "d169a-resident-option-interface-envelope-protocol-2026-07-27.md"
LOCK = BASE / "d169a-resident-option-interface-envelope-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
RUN_A = ARTIFACT_BASE / "d169a-jobs1-9844136-9844199.tsv"
RUN_B = ARTIFACT_BASE / "d169a-jobs20-9844136-9844199.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "d169a_resident_option_envelope.rs"
BUILD_SCRIPT = ROOT / "rust" / "build.rs"
OUTPUT = BASE / "d169a-resident-option-interface-envelope-result.json"

START_SEED = 9_844_136
MAP_COUNT = 64
RESERVED_START_SEED = 9_844_200
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

CONTROL = "control"
RETURN_ARM = "opt_return"
RESOURCE_COMPONENTS = ("fruit", "iron", "protect")
FIXED_STARTS = (72, 104, 136)
ARM_LABELS = (
    "opt_return",
    "opt_fruit_t072", "opt_fruit_t104", "opt_fruit_t136", "opt_fruit_trig",
    "opt_iron_t072", "opt_iron_t104", "opt_iron_t136", "opt_iron_trig",
    "opt_protect_t072", "opt_protect_t104", "opt_protect_t136", "opt_protect_trig",
)
POLICIES = (CONTROL, *ARM_LABELS)
assert len(POLICIES) == 14
TRIG_AND_RETURN_ARMS = (
    "opt_return", "opt_fruit_trig", "opt_iron_trig", "opt_protect_trig",
)

EXPECTED_FIELDS = (
    "map_seed", "seat", "opponent_index", "opponent", "policy_index", "policy",
    "arm_family", "component", "start_kind", "fixed_start", "configured_start",
    "done", "turn", "own_score", "opponent_score", "margin", "own_return",
    "opponent_return", "margin_return", "reward_identity_error", "own_workers",
    "opponent_workers", "max_own_workers", "successful_trains",
    "provenance_failures", "own_created_crops", "opponent_created_crops",
    "joint_created_crops", "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "own_reinvested_crops", "action_hash", "state_hash", "entry_captured",
    "entry_turn", "entry_unit_id", "generic_return_captured", "generic_return_turn",
    "generic_return_verb", "opp_worker_trigger_turn", "purity_violations",
    "invalid_direct_commands", "activated", "activation_turn", "deadline",
    "committed", "committed_turn", "aborted", "abort_reason", "active_turns",
    "return_gate_bank_ok", "return_species_picked", "return_species_planted",
    "return_plant_cell_x", "return_plant_cell_y", "return_move_commands",
    "return_pick_commands", "return_plant_commands", "return_hold_commands",
    "return_pick_attempts", "return_pick_successes", "return_plant_attempts",
    "return_plant_successes", "return_vocabulary_violations", "resource_mask",
    "resource_option_overrides", "resource_fruit_overrides", "resource_iron_overrides",
    "resource_protected_commands", "resource_move_commands", "resource_bank_commands",
    "resource_fruit_bank_commands", "resource_iron_bank_commands",
    "resource_harvest_commands", "resource_mine_commands",
    "resource_resident_train_commands", "resource_controller_train_commands",
    "resource_suppressed_train_commands", "resource_initial_bank_deficit",
    "resource_closest_bank_deficit", "resource_option_command_failures",
    "resource_workforce_exit_events", "resource_horizon_violations",
    "resource_restart_violations",
)
STRING_FIELDS = (
    "opponent", "policy", "arm_family", "component", "start_kind", "abort_reason",
    "return_species_picked", "return_species_planted",
)
FLOAT_FIELDS = ("own_return", "opponent_return", "margin_return", "reward_identity_error")
INT_FIELDS = tuple(
    field for field in EXPECTED_FIELDS if field not in FLOAT_FIELDS and field not in STRING_FIELDS
)
FAILURE_FIELDS = (
    "provenance_failures",
    "ambiguous_created_crops",
    "purity_violations",
    "invalid_direct_commands",
    "return_vocabulary_violations",
    "resource_option_command_failures",
    "resource_controller_train_commands",
    "resource_suppressed_train_commands",
)
D161_PARITY_FIELDS = (
    "done", "turn", "own_score", "opponent_score", "margin", "own_return",
    "opponent_return", "margin_return", "reward_identity_error", "own_workers",
    "opponent_workers", "max_own_workers", "successful_trains",
    "own_created_crops", "opponent_created_crops", "joint_created_crops",
    "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "own_reinvested_crops", "action_hash", "state_hash",
)
GAME_RELEVANT_FIELDS = (
    "done", "turn", "own_score", "opponent_score", "own_return", "opponent_return",
    "margin_return", "own_workers", "opponent_workers", "max_own_workers",
    "successful_trains", "own_created_crops", "opponent_created_crops",
    "joint_created_crops", "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "action_hash", "state_hash",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            json.dump(value, target, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def ratio(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator if denominator else 0.0


def read_rows(path: Path) -> tuple[list[dict], tuple[str, ...]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = tuple(reader.fieldnames or ())
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows, fields


def task(row: Mapping[str, object]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def row_key(row: Mapping[str, object]) -> tuple[int, int, str, str]:
    return (*task(row), str(row["policy"]))


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def outcome_margin(row: Mapping[str, object]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def normal_interval_by_map(rows: Iterable[Mapping[str, object]], field: str) -> list[float] | None:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        clusters[int(row["map_seed"])].append(float(row[field]))
    if not clusters:
        return None
    cluster_means = [statistics.fmean(values) for values in clusters.values()]
    center = statistics.fmean(cluster_means)
    if len(cluster_means) == 1:
        return [center, center]
    standard_error = statistics.stdev(cluster_means) / math.sqrt(len(cluster_means))
    return [center - 1.96 * standard_error, center + 1.96 * standard_error]


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d169a-resident-option-interface-envelope-lock-v1":
        raise ValueError("unknown D169a lock schema")
    mismatches = {}
    for relative, expected in lock["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {"lock": lock, "mismatches": mismatches, "pass": not mismatches}


def read_d161_resident() -> dict[tuple[int, int, str], dict]:
    with D161.open(newline="") as source:
        rows = [row for row in csv.DictReader(source, delimiter="\t") if row["policy"] == "resident"]
    return {(int(row["map_seed"]), int(row["seat"]), row["opponent"]): row for row in rows}


def d161_parity(control_rows: list[dict]) -> dict:
    reference = read_d161_resident()
    mismatches = []
    for row in control_rows:
        ref = reference.get(task(row))
        if ref is None:
            mismatches.append({"task": task(row), "field": "missing"})
            continue
        for field in D161_PARITY_FIELDS:
            actual = row[field]
            expected = ref[field]
            if field in FLOAT_FIELDS:
                if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=1e-7):
                    mismatches.append({"task": task(row), "field": field, "expected": expected, "actual": actual})
                    break
            elif str(actual) != str(expected):
                mismatches.append({"task": task(row), "field": field, "expected": expected, "actual": actual})
                break
    return {
        "tasks": len(control_rows),
        "mismatches": mismatches[:20],
        "mismatch_count": len(mismatches),
        "pass": not mismatches and len(control_rows) == len(reference),
    }


def resource_workforce_parity(indexed: dict[tuple, dict]) -> dict:
    """D163's own frozen invariant, reused here: the resource-control
    components never issue or suppress TRAIN (D163a: 'workforce counts
    remain exactly paired', a workforce-independent comparison), so every
    OPT_FRUIT/OPT_IRON/OPT_PROTECT row must have *our own* workforce counts
    exactly paired with CONTROL for that same task, active or not. This is
    deliberately restricted to our own seat: the independently-reacting
    opponent bot legitimately trains at different turns against a perturbed
    trajectory (confirmed empirically: opponent_workers diverges on 97/12288
    rows, own_workers/max_own_workers/successful_trains never do), and nothing
    in D163/D169a's protocol claims opponent-side workforce independence."""
    fields = ("own_workers", "max_own_workers", "successful_trains")
    resource_arms = tuple(arm for arm in ARM_LABELS if arm != RETURN_ARM)
    mismatches = []
    checked = 0
    for key in sorted(expected_tasks()):
        control = indexed[(*key, CONTROL)]
        for arm in resource_arms:
            row = indexed[(*key, arm)]
            checked += 1
            for field in fields:
                if control[field] != row[field]:
                    mismatches.append(
                        {"task": key, "policy": arm, "field": field, "control": control[field], "arm": row[field]}
                    )
                    break
    return {"rows_checked": checked, "mismatches": mismatches[:20], "mismatch_count": len(mismatches), "pass": not mismatches}


def inactive_task_parity(indexed: dict[tuple, dict]) -> dict:
    mismatches = []
    checked = 0
    for key in sorted(expected_tasks()):
        control = indexed[(*key, CONTROL)]
        for arm in ARM_LABELS:
            arm_row = indexed[(*key, arm)]
            if arm_row["activated"]:
                continue
            checked += 1
            for field in GAME_RELEVANT_FIELDS:
                if control[field] != arm_row[field]:
                    mismatches.append(
                        {"task": key, "policy": arm, "field": field, "control": control[field], "arm": arm_row[field]}
                    )
                    break
    return {"tasks_checked": checked, "mismatches": mismatches[:20], "mismatch_count": len(mismatches), "pass": not mismatches}


def tail_summary(rows: Iterable[Mapping[str, object]]) -> dict:
    margins = [outcome_margin(row) for row in rows]
    return {
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def coverage_gate(indexed: dict[tuple, dict]) -> dict:
    covered = 0
    for key in sorted(expected_tasks()):
        if any(indexed[(*key, arm)]["activated"] for arm in ARM_LABELS):
            covered += 1
    total = len(expected_tasks())
    rate = ratio(covered, total)
    return {
        "tasks_with_at_least_one_armable_option_state": covered,
        "tasks": total,
        "rate": rate,
        "pass": rate >= 0.60,
    }


def per_arm_activation(indexed: dict[tuple, dict]) -> dict:
    summary = {}
    for arm in ARM_LABELS:
        rows = [indexed[(*key, arm)] for key in sorted(expected_tasks())]
        active = [row for row in rows if row["activated"]]
        deltas = [outcome_margin(row) - outcome_margin(indexed[(*task(row), CONTROL)]) for row in active]
        summary[arm] = {
            "activated_tasks": len(active),
            "activation_rate": ratio(len(active), len(rows)),
            "committed_tasks": sum(row["committed"] for row in rows),
            "aborted_tasks": sum(row["aborted"] for row in rows),
            "mean_paired_margin_active": mean(deltas),
            "strict_improve_active": sum(value > 0 for value in deltas),
            "strict_regress_active": sum(value < 0 for value in deltas),
        }
    return summary


def select_envelope(indexed: dict[tuple, dict], arms: tuple[str, ...]) -> tuple[dict, dict]:
    """D169a's frozen envelope rule: crop-safety filter first (candidate's
    own_created_crops >= CONTROL's, the D122 relative rule stated verbatim in
    the protocol), then per-task envelope = max paired margin over
    {CONTROL} union eligible arms. Ties prefer CONTROL, then earlier catalog
    order (D162a's own established convention for this identical envelope
    shape; not restated in D169a's protocol because it is inherited by
    reference to D162)."""
    selected = {}
    selection_counts = Counter()
    ineligible_crop_rows = 0
    for key in sorted(expected_tasks()):
        control = indexed[(*key, CONTROL)]
        best = control
        for arm in arms:
            candidate = indexed[(*key, arm)]
            crop_safe = candidate["own_created_crops"] >= control["own_created_crops"]
            if not crop_safe:
                ineligible_crop_rows += 1
                continue
            if outcome_margin(candidate) > outcome_margin(best):
                best = candidate
        selected[key] = best
        selection_counts[best["policy"]] += 1
    return selected, {
        "selection_counts": dict(sorted(selection_counts.items())),
        "ineligible_crop_rows": ineligible_crop_rows,
    }


def envelope_metrics(indexed: dict[tuple, dict], arms: tuple[str, ...]) -> dict:
    selected, selection = select_envelope(indexed, arms)
    controls = {key: indexed[(*key, CONTROL)] for key in expected_tasks()}
    deltas = []
    by_map = defaultdict(list)
    by_family = defaultdict(list)
    for key in sorted(expected_tasks()):
        control = controls[key]
        candidate = selected[key]
        row = {
            "map_seed": key[0],
            "margin": outcome_margin(candidate) - outcome_margin(control),
            "own": candidate["own_score"] - control["own_score"],
            "opponent": candidate["opponent_score"] - control["opponent_score"],
        }
        deltas.append(row)
        by_map[key[0]].append(row)
        by_family[key[2]].append(row)

    ci = normal_interval_by_map(deltas, "margin")
    family_means = {opponent: mean(row["margin"] for row in by_family[opponent]) for opponent in OPPONENTS}
    control_tail = tail_summary(controls.values())
    selected_tail = tail_summary(selected.values())

    return {
        "arms_in_envelope": list(arms),
        "tasks": len(deltas),
        "selection": selection,
        "mean_margin": mean(row["margin"] for row in deltas),
        "median_margin": statistics.median(row["margin"] for row in deltas),
        "map_clustered_normal_95pct_ci": ci,
        "mean_own_score_delta": mean(row["own"] for row in deltas),
        "mean_opponent_score_delta": mean(row["opponent"] for row in deltas),
        "strict_improvement_tasks": sum(row["margin"] > 0 for row in deltas),
        "strict_improvement_rate": mean(row["margin"] > 0 for row in deltas),
        "tie_tasks": sum(row["margin"] == 0 for row in deltas),
        "strict_regression_tasks": sum(row["margin"] < 0 for row in deltas),
        "family_mean_margin": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family_mean_margin": min(family_means.values()),
        "control_tail": control_tail,
        "selected_tail": selected_tail,
        "catastrophes_not_above_control": selected_tail["catastrophe_count"] <= control_tail["catastrophe_count"],
        "negative_margin_mass_not_above_control": selected_tail["negative_margin_mass"] <= control_tail["negative_margin_mass"],
    }


def value_verdict(envelope: dict, coverage: dict) -> dict:
    mean_margin = envelope["mean_margin"]
    ci = envelope["map_clustered_normal_95pct_ci"]
    ci_lower = ci[0] if ci else None
    gates = {
        "mean_envelope_at_least_10_0": mean_margin >= 10.0,
        "ci_lower_bound_at_least_5_0": ci_lower is not None and ci_lower >= 5.0,
        "at_least_30pct_improved": envelope["strict_improvement_rate"] >= 0.30,
        "no_negative_family_mean": envelope["worst_family_mean_margin"] >= 0.0,
        "catastrophes_not_above_control": envelope["catastrophes_not_above_control"],
        "negative_margin_mass_not_above_control": envelope["negative_margin_mass_not_above_control"],
    }
    non_mean_gates = {name: value for name, value in gates.items() if name != "mean_envelope_at_least_10_0"}
    all_non_mean_pass = all(non_mean_gates.values())

    if not coverage["pass"]:
        verdict = "KILL"
        reason = "coverage gate failed (< 60% of tasks have >= 1 armable option state); representation too narrow, independent of value"
    elif mean_margin < 5.0:
        verdict = "KILL"
        reason = f"mean envelope {mean_margin:.3f} < +5.0"
    elif mean_margin >= 10.0 and all_non_mean_pass:
        verdict = "PASS"
        reason = "mean envelope >= +10.0 and all non-mean gates pass"
    elif mean_margin >= 10.0 and not all_non_mean_pass:
        verdict = "BORDERLINE"
        failed = [name for name, value in non_mean_gates.items() if not value]
        reason = f"mean envelope >= +10.0 but non-mean gate(s) missed: {failed}"
    else:
        verdict = "BORDERLINE"
        reason = f"+5.0 <= mean envelope {mean_margin:.3f} < +10.0"

    return {
        "gates": gates,
        "all_non_mean_gates_pass": all_non_mean_pass,
        "verdict": verdict,
        "reason": reason,
    }


def analyze(rows_a: list[dict], fields_a: tuple, rows_b: list[dict], fields_b: tuple, lock_result: dict,
            *, jobs1_wall_seconds: float | None = None, jobs20_wall_seconds: float | None = None) -> dict:
    expected = expected_tasks()
    expected_keys = {(*key, policy) for key in expected for policy in POLICIES}
    rows = rows_b
    indexed = {row_key(row): row for row in rows}
    control_rows = [row for row in rows if row["policy"] == CONTROL]

    parity = d161_parity(control_rows)
    inactive_parity = inactive_task_parity(indexed)
    workforce_parity = resource_workforce_parity(indexed)
    coverage = coverage_gate(indexed)

    integrity = {
        "schema_exact": fields_a == EXPECTED_FIELDS and fields_b == EXPECTED_FIELDS,
        "row_count_exact": len(rows_a) == 14336 and len(rows_b) == 14336,
        "unique_rows_exact": (
            len({row_key(row) for row in rows_a}) == len(rows_a)
            and len({row_key(row) for row in rows_b}) == len(rows_b)
        ),
        "task_policy_matrix_exact": (
            {row_key(row) for row in rows_a} == expected_keys
            and {row_key(row) for row in rows_b} == expected_keys
        ),
        "jobs1_and_jobs20_byte_identical": RUN_A.read_bytes() == RUN_B.read_bytes(),
        "reserved_maps_excluded": START_SEED + MAP_COUNT <= RESERVED_START_SEED,
        "control_reproduces_d161": parity["pass"],
        "inactive_tasks_byte_exact_vs_control": inactive_parity["pass"],
        "resource_arms_workforce_paired_with_control": workforce_parity["pass"],
        "all_games_done": all(row["done"] == 1 for row in rows),
        "reward_identity_exact": all(row["reward_identity_error"] <= 1e-6 for row in rows),
        "zero_failure_telemetry": all(row[field] == 0 for row in rows for field in FAILURE_FIELDS),
        "zero_ambiguous_crops": all(row["ambiguous_created_crops"] == 0 for row in rows),
        "control_never_activates": all(row["activated"] == 0 for row in control_rows),
        "no_task_exceeds_workforce_cap": all(row["max_own_workers"] <= 3 for row in rows),
        "own_le_max_own_workers": all(row["own_workers"] <= row["max_own_workers"] for row in rows),
        "no_double_commit_and_abort": all(not (row["committed"] and row["aborted"]) for row in rows),
        "frozen_modules_unmodified": lock_result["pass"],
    }
    integrity_pass = all(integrity.values())

    activation = per_arm_activation(indexed) if integrity_pass else None
    full_envelope = envelope_metrics(indexed, ARM_LABELS) if integrity_pass else None
    trig_return_envelope = envelope_metrics(indexed, TRIG_AND_RETURN_ARMS) if integrity_pass else None
    verdict = value_verdict(full_envelope, coverage) if integrity_pass else {
        "verdict": "BLOCKED",
        "reason": "integrity gate failure; value numbers not interpreted",
        "gates": {},
        "all_non_mean_gates_pass": False,
    }

    return {
        "schema": "troll-farm-d169a-resident-option-interface-envelope-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock_result,
        "input_hashes": {
            "protocol": sha256(PROTOCOL),
            "lock": sha256(LOCK),
            "runner": sha256(RUNNER),
            "build_script": sha256(BUILD_SCRIPT),
            "d161_resident_panel": sha256(D161),
            "jobs1": sha256(RUN_A),
            "jobs20": sha256(RUN_B),
        },
        "runs": {
            "jobs1": {"path": str(RUN_A.relative_to(ROOT)), "rows": len(rows_a), "wall_seconds": jobs1_wall_seconds},
            "jobs20": {"path": str(RUN_B.relative_to(ROOT)), "rows": len(rows_b), "wall_seconds": jobs20_wall_seconds},
            "speedup": (jobs1_wall_seconds / jobs20_wall_seconds if jobs1_wall_seconds and jobs20_wall_seconds else None),
        },
        "policies": list(POLICIES),
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "d161_parity": parity,
        "inactive_task_parity": inactive_parity,
        "resource_workforce_parity": workforce_parity,
        "coverage": coverage,
        "activation": activation,
        "envelope": full_envelope,
        "trig_and_return_envelope_diagnostic": trig_return_envelope,
        "value_verdict": verdict,
        "verdict": verdict["verdict"],
    }


def run(output: Path = OUTPUT, *, jobs1_wall_seconds: float | None = None, jobs20_wall_seconds: float | None = None) -> dict:
    lock_result = verify_lock()
    rows_a, fields_a = read_rows(RUN_A)
    rows_b, fields_b = read_rows(RUN_B)
    result = analyze(rows_a, fields_a, rows_b, fields_b, lock_result,
                      jobs1_wall_seconds=jobs1_wall_seconds, jobs20_wall_seconds=jobs20_wall_seconds)
    atomic_write(output, result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--jobs1-wall-seconds", type=float)
    parser.add_argument("--jobs20-wall-seconds", type=float)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    result = run(args.output, jobs1_wall_seconds=args.jobs1_wall_seconds, jobs20_wall_seconds=args.jobs20_wall_seconds)
    print(json.dumps({
        "integrity_pass": result["integrity_pass"],
        "coverage": result["coverage"],
        "mean_envelope": result["envelope"]["mean_margin"] if result["envelope"] else None,
        "verdict": result["verdict"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
