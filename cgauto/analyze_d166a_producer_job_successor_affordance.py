#!/usr/bin/env python3
"""Validate and analyze D166 field return classes and local successor affordances."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
ARTIFACT_BASE = (
    ROOT
    / "artifacts"
    / "experiments"
    / "d166a-producer-job-successor-affordance"
)
PROTOCOL = (
    BASE / "d166a-producer-job-successor-affordance-audit-protocol-2026-07-23.md"
)
LOCK = BASE / "d166a-producer-job-successor-affordance-audit-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
FIELD_A = ARTIFACT_BASE / "d166a-field-return-classes-jobs1.jsonl"
FIELD_B = ARTIFACT_BASE / "d166a-field-return-classes-jobs20.jsonl"
LOCAL_A = ARTIFACT_BASE / "d166a-local-affordances-jobs1-9844136-9844199.tsv"
LOCAL_B = ARTIFACT_BASE / "d166a-local-affordances-jobs20-9844136-9844199.tsv"
FIELD_EXTRACTOR = ROOT / "cgauto" / "extract_d166a_field_return_classes.py"
LOCAL_RUNNER = (
    ROOT / "rust" / "src" / "bin" / "d166_producer_job_successor_affordance.rs"
)
OUTPUT = BASE / "d166a-producer-job-successor-affordance-audit-result.json"

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
COHORTS = ("rank_1_5", "rank_6_20", "resident")
EXPECTED_COHORT_ROWS = {"rank_1_5": 50, "rank_6_20": 150, "resident": 192}
EXPECTED_CYCLES = {"rank_1_5": 36, "rank_6_20": 41, "resident": 21}

LOCAL_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "opponent",
    "policy",
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "max_own_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "joint_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
    "resident_calls",
    "turns_played",
    "resident_call_mismatches",
    "production_events",
    "successful_production_plants",
    "successful_production_harvests",
    "opponent_crop_chops",
    "historical_producer_opponent_crop_chops",
    "entry_captured",
    "entry_turn",
    "selected_unit_id",
    "prior_verb",
    "prior_turn",
    "prior_x",
    "prior_y",
    "prior_generation_birth_turn",
    "prior_target_live",
    "worker_ms",
    "worker_cc",
    "worker_hp",
    "worker_chop",
    "worker_free",
    "worker_carry_plum",
    "worker_carry_lemon",
    "worker_carry_apple",
    "worker_carry_banana",
    "worker_carry_iron",
    "worker_carry_wood",
    "own_live_crops",
    "own_ripe_crops",
    "h_ripe_available",
    "h_ripe_x",
    "h_ripe_y",
    "h_ripe_distance",
    "h_ripe_fruits",
    "h_ripe_cooldown",
    "h_live_available",
    "h_live_x",
    "h_live_y",
    "h_live_distance",
    "h_live_fruits",
    "h_live_cooldown",
    "p_carry_available",
    "legal_empty_cells",
    "p_empty_x",
    "p_empty_y",
    "p_empty_distance",
    "natural_return",
    "natural_return_turn",
    "natural_return_latency",
    "natural_return_verb",
    "natural_return_x",
    "natural_return_y",
    "natural_return_generation_birth_turn",
    "natural_return_reuses_prior_cell",
    "natural_return_reuses_prior_generation",
    "natural_return_within16",
    "natural_return_within32",
    "entry_worker_failures",
    "history_failures",
    "entry_restarts",
    "controller_commands",
)
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
STRING_FIELDS = ("opponent", "policy", "prior_verb", "natural_return_verb")
INT_FIELDS = tuple(
    field
    for field in LOCAL_FIELDS
    if field not in FLOAT_FIELDS and field not in STRING_FIELDS
)
D161_PARITY_FIELDS = (
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "max_own_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "joint_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d166a-producer-job-successor-affordance-lock-v1":
        raise ValueError("unknown D166 lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"D166 frozen input differs: {relative}")
    return lock


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def read_local(path: Path) -> tuple[list[dict], tuple[str, ...]]:
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


def read_d161() -> dict[tuple[int, int, str], dict]:
    with D161.open(newline="") as source:
        rows = [
            row
            for row in csv.DictReader(source, delimiter="\t")
            if row["policy"] == "resident"
        ]
    return {
        (int(row["map_seed"]), int(row["seat"]), row["opponent"]): row
        for row in rows
    }


def median(values: Iterable[int | float]) -> float | None:
    selected = list(values)
    return statistics.median(selected) if selected else None


def ratio(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator if denominator else 0.0


def field_verb_summary(rows: list[dict], verb: str) -> dict:
    by_cohort = {}
    for cohort in COHORTS:
        cycles = [row for row in rows if row["cohort"] == cohort and row["has_cycle"]]
        selected = [row for row in cycles if row["return_verb"] == verb]
        by_cohort[cohort] = {
            "returns": len(selected),
            "cycles": len(cycles),
            "rate": ratio(len(selected), len(cycles)),
            "agents": len({row["actor_id"] for row in selected}),
            "seats": sorted({row["seat"] for row in selected}),
            "median_suppression_duration": median(
                row["suppression_duration"] for row in selected
            ),
        }
    top = by_cohort["rank_1_5"]
    reference = by_cohort["rank_6_20"]
    gates = {
        "top5_rate_at_least_60pct": top["rate"] >= 0.60,
        "rank6_20_rate_at_least_50pct": reference["rate"] >= 0.50,
        "at_least_four_top5_agents": top["agents"] >= 4,
        "both_top5_seats": top["seats"] == [0, 1],
        "top5_median_duration_at_most_32": (
            top["median_suppression_duration"] is not None
            and top["median_suppression_duration"] <= 32
        ),
    }
    return {"verb": verb, "cohorts": by_cohort, "gates": gates, "pass": all(gates.values())}


def affordance_summary(entries: list[dict], field: str, distance: str) -> dict:
    selected = [row for row in entries if row[field] == 1]
    distances = [row[distance] for row in selected if row[distance] >= 0]
    families = sorted({row["opponent"] for row in selected})
    seats = sorted({row["seat"] for row in selected})
    return {
        "tasks": len(selected),
        "entry_rate": ratio(len(selected), len(entries)),
        "seats": seats,
        "families": families,
        "family_count": len(families),
        "median_distance": median(distances),
        "distance_at_most_16": sum(value <= 16 for value in distances),
        "distance_at_most_16_rate": ratio(
            sum(value <= 16 for value in distances), len(distances)
        ),
        "by_family": {
            opponent: sum(
                row[field] == 1 for row in entries if row["opponent"] == opponent
            )
            for opponent in OPPONENTS
        },
        "by_seat": {
            str(seat): sum(
                row[field] == 1 for row in entries if row["seat"] == seat
            )
            for seat in (0, 1)
        },
    }


def natural_summary(entries: list[dict]) -> dict:
    returned = [row for row in entries if row["natural_return"] == 1]
    return {
        "any_return_tasks": len(returned),
        "any_return_rate": ratio(len(returned), len(entries)),
        "within16_tasks": sum(row["natural_return_within16"] for row in entries),
        "within16_rate": ratio(
            sum(row["natural_return_within16"] for row in entries), len(entries)
        ),
        "within32_tasks": sum(row["natural_return_within32"] for row in entries),
        "within32_rate": ratio(
            sum(row["natural_return_within32"] for row in entries), len(entries)
        ),
        "median_latency": median(row["natural_return_latency"] for row in returned),
        "verbs": dict(Counter(row["natural_return_verb"] for row in returned)),
        "reuses_prior_cell": sum(
            row["natural_return_reuses_prior_cell"] for row in returned
        ),
        "reuses_prior_generation": sum(
            row["natural_return_reuses_prior_generation"] for row in returned
        ),
        "seats": sorted({row["seat"] for row in returned}),
        "families": sorted({row["opponent"] for row in returned}),
    }


def analyze(
    field_a: list[dict],
    field_b: list[dict],
    local_a: list[dict],
    local_fields_a: tuple[str, ...],
    local_b: list[dict],
    local_fields_b: tuple[str, ...],
    lock: dict,
    *,
    field_jobs1_wall: float | None = None,
    field_jobs20_wall: float | None = None,
    local_jobs1_wall: float | None = None,
    local_jobs20_wall: float | None = None,
) -> dict:
    field_rows = field_b
    local_rows = local_b
    field_counts = Counter(row["cohort"] for row in field_rows)
    cycle_counts = Counter(row["cohort"] for row in field_rows if row["has_cycle"])
    d161 = read_d161()
    parity_mismatches = []
    for row in local_rows:
        key = (row["map_seed"], row["seat"], row["opponent"])
        reference = d161.get(key)
        if reference is None:
            parity_mismatches.append({"task": key, "field": "missing"})
            continue
        for field in D161_PARITY_FIELDS:
            actual = (
                f"{row[field]:.9f}"
                if field in FLOAT_FIELDS
                else str(row[field])
            )
            if actual != reference[field]:
                parity_mismatches.append(
                    {
                        "task": key,
                        "field": field,
                        "expected": reference[field],
                        "actual": actual,
                    }
                )
                break

    local_keys = {
        (row["map_seed"], row["seat"], row["opponent"]) for row in local_rows
    }
    expected_local_keys = {
        (seed, seat, opponent)
        for seed in range(9_844_136, 9_844_200)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    integrity = {
        "field_rows_exact": len(field_a) == len(field_b) == 392,
        "field_unique_exact": (
            len({(row["actor_id"], row["game_id"]) for row in field_a}) == 392
            and len({(row["actor_id"], row["game_id"]) for row in field_b}) == 392
        ),
        "field_bytes_identical": FIELD_A.read_bytes() == FIELD_B.read_bytes(),
        "field_cohorts_reproduce_d164": dict(field_counts) == EXPECTED_COHORT_ROWS,
        "field_cycles_reproduce_d164": dict(cycle_counts) == EXPECTED_CYCLES,
        "field_state_and_birth_integrity": all(
            row["decoded_turns"] == row["trajectory_turns"]
            and row["unknown_diff_updates"] == 0
            and row["unknown_births"] == 0
            and row["ambiguous_births"] == 0
            for row in field_rows
        ),
        "local_schema_exact": local_fields_a == LOCAL_FIELDS
        and local_fields_b == LOCAL_FIELDS,
        "local_rows_exact": len(local_a) == len(local_b) == 1024,
        "local_unique_matrix_exact": (
            len(
                {
                    (row["map_seed"], row["seat"], row["opponent"])
                    for row in local_a
                }
            )
            == 1024
            and len(local_keys) == 1024
            and local_keys == expected_local_keys
        ),
        "local_bytes_identical": LOCAL_A.read_bytes() == LOCAL_B.read_bytes(),
        "local_resident_reproduces_d161": not parity_mismatches,
        "local_d165_support_counts_reproduce": (
            sum(row["production_events"] > 0 for row in local_rows) == 1024
            and sum(row["opponent_crop_chops"] > 0 for row in local_rows) == 932
            and sum(row["historical_producer_opponent_crop_chops"] > 0 for row in local_rows)
            == 237
            and sum(
                row["historical_producer_opponent_crop_chops"] for row in local_rows
            )
            == 1976
        ),
        "local_reward_and_ownership_integrity": all(
            row["done"] == 1
            and row["reward_identity_error"] <= 1e-6
            and row["provenance_failures"] == 0
            and row["ambiguous_created_crops"] == 0
            and row["entry_worker_failures"] == 0
            and row["history_failures"] == 0
            and row["entry_restarts"] == 0
            for row in local_rows
        ),
        "local_read_only_exact": all(
            row["controller_commands"] == 0
            and row["resident_calls"] == row["turns_played"]
            and row["resident_call_mismatches"] == 0
            for row in local_rows
        ),
    }
    integrity_pass = all(integrity.values())

    cycles = [row for row in field_rows if row["has_cycle"]]
    verb_summaries = {
        verb: field_verb_summary(field_rows, verb)
        for verb in ("PLANT", "HARVEST")
    }
    passing_verbs = [
        verb for verb, summary in verb_summaries.items() if summary["pass"]
    ]
    selected_verb = passing_verbs[0] if len(passing_verbs) == 1 else None
    field_generation = {
        cohort: {
            "cycles": sum(
                row["cohort"] == cohort and row["has_cycle"] for row in field_rows
            ),
            "prior_generation_live_at_suppression": sum(
                row["cohort"] == cohort
                and row["has_cycle"]
                and row["prior_generation_live_at_suppression"]
                for row in field_rows
            ),
            "return_generation_live_at_suppression": sum(
                row["cohort"] == cohort
                and row["has_cycle"]
                and row["return_generation_live_at_suppression"]
                for row in field_rows
            ),
            "return_reuses_prior_generation": sum(
                row["cohort"] == cohort
                and row["has_cycle"]
                and row["return_reuses_prior_generation"]
                for row in field_rows
            ),
            "return_reuses_prior_cell": sum(
                row["cohort"] == cohort
                and row["has_cycle"]
                and row["return_reuses_prior_cell"]
                for row in field_rows
            ),
        }
        for cohort in COHORTS
    }

    entries = [row for row in local_rows if row["entry_captured"] == 1]
    local_affordances = {
        "H-ripe": affordance_summary(entries, "h_ripe_available", "h_ripe_distance"),
        "H-live_diagnostic": affordance_summary(
            entries, "h_live_available", "h_live_distance"
        ),
        "P-carry": affordance_summary(
            entries, "p_carry_available", "p_empty_distance"
        ),
    }
    mapped = {"HARVEST": "H-ripe", "PLANT": "P-carry"}
    local_transport = {}
    for verb, affordance in mapped.items():
        summary = local_affordances[affordance]
        field_nonzero_cohorts = sum(
            verb_summaries[verb]["cohorts"][cohort]["returns"] > 0
            for cohort in COHORTS
        )
        gates = {
            "at_least_64_tasks": summary["tasks"] >= 64,
            "both_seats": summary["seats"] == [0, 1],
            "at_least_six_families": summary["family_count"] >= 6,
            "at_least_half_distance_at_most_16": (
                summary["distance_at_most_16_rate"] >= 0.50
                if summary["tasks"]
                else False
            ),
            "exact_worker_and_target_integrity": integrity[
                "local_reward_and_ownership_integrity"
            ],
            "nonzero_in_two_field_cohorts": field_nonzero_cohorts >= 2,
        }
        local_transport[verb] = {
            "mapped_affordance": affordance,
            "summary": summary,
            "field_nonzero_cohorts": field_nonzero_cohorts,
            "gates": gates,
            "pass": all(gates.values()),
        }

    field_dominance_pass = selected_verb is not None
    selected_transport_pass = (
        local_transport[selected_verb]["pass"] if selected_verb else False
    )
    overall_pass = integrity_pass and field_dominance_pass and selected_transport_pass
    if not integrity_pass:
        verdict = "invalid_integrity_repair_before_interpretation"
        next_experiment = "repair D166 without interpreting support"
    elif not field_dominance_pass:
        verdict = "close_single_return_verb_and_use_state_conditioned_job_value"
        next_experiment = (
            "freeze trajectory-conditioned semantic successor evaluation over KEEP, acquire-and-"
            "PLANT, and current-own-crop HARVEST jobs; preserve exact resident fallback and do "
            "not force one verb"
        )
    elif not selected_transport_pass:
        verdict = "close_field_dominant_successor_for_local_transport"
        next_experiment = (
            "change representation rather than selecting the locally more common affordance"
        )
    else:
        verdict = "freeze_one_d167_causal_successor_option"
        next_experiment = (
            f"freeze exact-resident one-episode {selected_verb} successor on consumed maps"
        )

    return {
        "schema": "troll-farm-d166a-producer-job-successor-affordance-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "input_hashes": {
            "protocol": sha256(PROTOCOL),
            "lock": sha256(LOCK),
            "field_extractor": sha256(FIELD_EXTRACTOR),
            "local_runner": sha256(LOCAL_RUNNER),
            "field_rows": sha256(FIELD_B),
            "local_rows": sha256(LOCAL_B),
            "d161": sha256(D161),
        },
        "runs": {
            "field_jobs1": {"rows": len(field_a), "wall_seconds": field_jobs1_wall},
            "field_jobs20": {"rows": len(field_b), "wall_seconds": field_jobs20_wall},
            "field_speedup": (
                field_jobs1_wall / field_jobs20_wall
                if field_jobs1_wall and field_jobs20_wall
                else None
            ),
            "local_jobs1": {"rows": len(local_a), "wall_seconds": local_jobs1_wall},
            "local_jobs20": {"rows": len(local_b), "wall_seconds": local_jobs20_wall},
            "local_speedup": (
                local_jobs1_wall / local_jobs20_wall
                if local_jobs1_wall and local_jobs20_wall
                else None
            ),
        },
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "parity_mismatches": parity_mismatches[:20],
        "field": {
            "cycles": len(cycles),
            "return_verbs": dict(Counter(row["return_verb"] for row in cycles)),
            "prior_to_return_cross_tab": {
                f"{prior}->{returned}": count
                for (prior, returned), count in sorted(
                    Counter(
                        (row["prior_verb"], row["return_verb"]) for row in cycles
                    ).items()
                )
            },
            "verb_summaries": verb_summaries,
            "generation_continuity": field_generation,
            "selected_verb": selected_verb,
            "dominance_pass": field_dominance_pass,
        },
        "local": {
            "entries": len(entries),
            "entry_rate": ratio(len(entries), len(local_rows)),
            "entry_seats": dict(Counter(row["seat"] for row in entries)),
            "entry_families": dict(Counter(row["opponent"] for row in entries)),
            "prior_verbs": dict(Counter(row["prior_verb"] for row in entries)),
            "worker_hp": dict(Counter(row["worker_hp"] for row in entries)),
            "worker_full_at_entry": sum(row["worker_free"] <= 0 for row in entries),
            "prior_target_live": sum(row["prior_target_live"] for row in entries),
            "affordances": local_affordances,
            "natural_continuation": natural_summary(entries),
            "transport_by_field_verb": local_transport,
        },
        "decision": {
            "verdict": verdict,
            "overall_pass": overall_pass,
            "next_experiment": next_experiment,
            "construct_candidate": False,
            "arena_or_submission": False,
            "yt": False,
            "reserved_maps_opened": False,
        },
    }


def run(
    output: Path = OUTPUT,
    *,
    field_jobs1_wall: float | None = None,
    field_jobs20_wall: float | None = None,
    local_jobs1_wall: float | None = None,
    local_jobs20_wall: float | None = None,
) -> dict:
    lock = verify_lock()
    field_a = read_jsonl(FIELD_A)
    field_b = read_jsonl(FIELD_B)
    local_a, local_fields_a = read_local(LOCAL_A)
    local_b, local_fields_b = read_local(LOCAL_B)
    result = analyze(
        field_a,
        field_b,
        local_a,
        local_fields_a,
        local_b,
        local_fields_b,
        lock,
        field_jobs1_wall=field_jobs1_wall,
        field_jobs20_wall=field_jobs20_wall,
        local_jobs1_wall=local_jobs1_wall,
        local_jobs20_wall=local_jobs20_wall,
    )
    atomic_write(output, result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--field-jobs1-wall", type=float)
    parser.add_argument("--field-jobs20-wall", type=float)
    parser.add_argument("--local-jobs1-wall", type=float)
    parser.add_argument("--local-jobs20-wall", type=float)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    result = run(
        args.output,
        field_jobs1_wall=args.field_jobs1_wall,
        field_jobs20_wall=args.field_jobs20_wall,
        local_jobs1_wall=args.local_jobs1_wall,
        local_jobs20_wall=args.local_jobs20_wall,
    )
    print(
        json.dumps(
            {
                "integrity_pass": result["integrity_pass"],
                "field": result["field"],
                "local": result["local"],
                "decision": result["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
