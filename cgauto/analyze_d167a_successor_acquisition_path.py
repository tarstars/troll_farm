#!/usr/bin/env python3
"""D167a orchestrator: local+field acquisition-path class distributions and gates."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d167a-successor-acquisition-path"
PROTOCOL = BASE / "d167a-successor-acquisition-path-protocol-2026-07-27.md"
LOCK = BASE / "d167a-successor-acquisition-path-lock.json"
RUST_RUNNER = ROOT / "rust" / "src" / "bin" / "d167a_successor_acquisition_path.rs"
FIELD_EXTRACTOR = ROOT / "cgauto" / "extract_d167a_field_acquisition_classes.py"
SELF = Path(__file__)

LOCAL_SUMMARY_A = ARTIFACT_BASE / "d167a-local-summary-jobs1-9844136-9844199.tsv"
LOCAL_SUMMARY_B = ARTIFACT_BASE / "d167a-local-summary-jobs20-9844136-9844199.tsv"
LOCAL_EVENTS_A = ARTIFACT_BASE / "d167a-local-events-jobs1-9844136-9844199.tsv"
LOCAL_EVENTS_B = ARTIFACT_BASE / "d167a-local-events-jobs20-9844136-9844199.tsv"
FIELD_A = ARTIFACT_BASE / "d167a-field-acquisition-classes-jobs1.jsonl"
FIELD_B = ARTIFACT_BASE / "d167a-field-acquisition-classes-jobs20.jsonl"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
D166_LOCAL = (
    ROOT
    / "artifacts/experiments/d166a-producer-job-successor-affordance"
    / "d166a-local-affordances-jobs20-9844136-9844199.tsv"
)
D166_FIELD = (
    ROOT
    / "artifacts/experiments/d166a-producer-job-successor-affordance"
    / "d166a-field-return-classes-jobs20.jsonl"
)
OUTPUT = BASE / "d167a-successor-acquisition-path-result.json"

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
CLASSES = ("BANK_SEED", "FIELD_FRUIT", "OPPONENT_DERIVED", "OTHER_MIXED")

D166_SHARED_COLUMNS = (
    "map_seed", "seat", "opponent_index", "opponent", "policy", "done", "turn",
    "own_score", "opponent_score", "margin", "own_return", "opponent_return",
    "margin_return", "reward_identity_error", "own_workers", "opponent_workers",
    "max_own_workers", "successful_trains", "completed_jobs", "invalidated_jobs",
    "invalid_direct_commands", "provenance_failures", "deposit_prediction_failures",
    "own_created_crops", "opponent_created_crops", "joint_created_crops",
    "ambiguous_created_crops", "own_owned_crop_harvest_units", "own_reinvested_crops",
    "action_hash", "state_hash", "resident_calls", "turns_played",
    "resident_call_mismatches", "production_events", "successful_production_plants",
    "successful_production_harvests", "opponent_crop_chops",
    "historical_producer_opponent_crop_chops", "entry_captured", "entry_turn",
    "selected_unit_id", "prior_verb", "prior_turn", "prior_x", "prior_y",
    "prior_generation_birth_turn", "prior_target_live", "worker_ms", "worker_cc",
    "worker_hp", "worker_chop", "worker_free", "worker_carry_plum",
    "worker_carry_lemon", "worker_carry_apple", "worker_carry_banana",
    "worker_carry_iron", "worker_carry_wood", "own_live_crops", "own_ripe_crops",
    "h_ripe_available", "h_ripe_x", "h_ripe_y", "h_ripe_distance", "h_ripe_fruits",
    "h_ripe_cooldown", "h_live_available", "h_live_x", "h_live_y", "h_live_distance",
    "h_live_fruits", "h_live_cooldown", "p_carry_available", "legal_empty_cells",
    "p_empty_x", "p_empty_y", "p_empty_distance", "natural_return",
    "natural_return_turn", "natural_return_latency", "natural_return_verb",
    "natural_return_x", "natural_return_y", "natural_return_generation_birth_turn",
    "natural_return_reuses_prior_cell", "natural_return_reuses_prior_generation",
    "natural_return_within16", "natural_return_within32", "entry_worker_failures",
    "history_failures", "entry_restarts", "controller_commands",
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
    if lock.get("schema") != "troll-farm-d167a-successor-acquisition-path-lock-v1":
        raise ValueError("unknown D167a lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"D167a frozen input differs: {relative}")
    return lock


def read_tsv(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def local_integrity(local_a: list[dict], local_b: list[dict]) -> dict:
    d161_rows = {
        (row["map_seed"], row["seat"], row["opponent"]): row
        for row in read_tsv(D161)
        if row["policy"] == "resident"
    }
    d166_rows = {
        (row["map_seed"], row["seat"], row["opponent"]): row for row in read_tsv(D166_LOCAL)
    }
    mismatches_d161 = []
    mismatches_d166 = []
    for row in local_b:
        key = (row["map_seed"], row["seat"], row["opponent"])
        d161_row = d161_rows.get(key)
        if d161_row is None:
            mismatches_d161.append({"task": key, "reason": "missing_in_d161"})
        else:
            for field in D166_SHARED_COLUMNS:
                if field not in d161_row:
                    continue
                if row[field] != d161_row[field]:
                    mismatches_d161.append(
                        {"task": key, "field": field, "d167a": row[field], "d161": d161_row[field]}
                    )
                    break
        d166_row = d166_rows.get(key)
        if d166_row is None:
            mismatches_d166.append({"task": key, "reason": "missing_in_d166"})
        else:
            for field in D166_SHARED_COLUMNS:
                if row[field] != d166_row[field]:
                    mismatches_d166.append(
                        {"task": key, "field": field, "d167a": row[field], "d166a": d166_row[field]}
                    )
                    break

    entries = [row for row in local_b if row["entry_captured"] == "1"]
    returns = [row for row in entries if row["natural_return"] == "1"]
    plant_returns = [row for row in returns if row["natural_return_verb"] == "PLANT"]

    return {
        "rows_exact_1024": len(local_a) == len(local_b) == 1024,
        "bytes_identical_summary": LOCAL_SUMMARY_A.read_bytes() == LOCAL_SUMMARY_B.read_bytes(),
        "bytes_identical_events": LOCAL_EVENTS_A.read_bytes() == LOCAL_EVENTS_B.read_bytes(),
        "reproduces_d161_on_shared_columns": not mismatches_d161,
        "reproduces_d166a_on_shared_columns": not mismatches_d166,
        "entries_exact_237": len(entries) == 237,
        "natural_returns_exact_135": len(returns) == 135,
        "all_returns_are_plant": len(plant_returns) == len(returns),
        "ledger_integrity_ok_for_all_returns": all(
            row["ledger_integrity_ok"] == "1" for row in returns
        ),
        "zero_reward_or_ownership_failures": all(
            float(row["reward_identity_error"]) <= 1e-6 for row in local_b
        )
        and sum(int(row["provenance_failures"]) for row in local_b) == 0
        and sum(int(row["ambiguous_created_crops"]) for row in local_b) == 0
        and sum(int(row["entry_worker_failures"]) for row in local_b) == 0
        and sum(int(row["history_failures"]) for row in local_b) == 0
        and sum(int(row["entry_restarts"]) for row in local_b) == 0,
        "zero_controller_commands": sum(int(row["controller_commands"]) for row in local_b) == 0,
        "zero_ledger_ambiguous_partial_spends": sum(
            int(row["ledger_ambiguous_partial_spends"]) for row in local_b
        )
        == 0,
        "zero_ledger_carry_mismatches": sum(
            int(row["ledger_carry_mismatches"]) for row in local_b
        )
        == 0,
        "zero_entry_carry_nonzero": sum(
            int(row["ledger_entry_carry_nonzero"]) for row in local_b
        )
        == 0,
        "mismatch_examples_d161": mismatches_d161[:10],
        "mismatch_examples_d166a": mismatches_d166[:10],
    }, entries, returns


def field_integrity(field_a: list[dict], field_b: list[dict]) -> dict:
    d166_field_rows = read_jsonl(D166_FIELD)
    d166_plant_cycles = {
        (row["actor_id"], row["game_id"])
        for row in d166_field_rows
        if row["has_cycle"] and row["return_verb"] == "PLANT" and row["cohort"] in ("rank_1_5", "rank_6_20")
    }
    d167a_cycles = {(row["actor_id"], row["game_id"]) for row in field_b}
    top5 = [row for row in field_b if row["cohort"] == "rank_1_5"]
    rank620 = [row for row in field_b if row["cohort"] == "rank_6_20"]
    return {
        "rows_exact_49": len(field_a) == len(field_b) == 49,
        "bytes_identical": FIELD_A.read_bytes() == FIELD_B.read_bytes(),
        "top5_exact_21": len(top5) == 21,
        "rank6_20_exact_28": len(rank620) == 28,
        "cycle_selection_matches_d166a": d166_plant_cycles == d167a_cycles,
        "ledger_integrity_ok_for_all": all(row["ledger_integrity_ok"] for row in field_b),
        "zero_ambiguous_partial_spends": sum(
            row["ledger_ambiguous_partial_spends"] for row in field_b
        )
        == 0,
    }, top5, rank620


def verb_return_summary(rows: list[dict], population: int, agent_field: str) -> dict:
    counts = Counter(row["acquisition_class"] for row in rows)
    per_class = {}
    for cls in CLASSES:
        selected = [row for row in rows if row["acquisition_class"] == cls]
        per_class[cls] = {
            "count": len(selected),
            "rate": ratio(len(selected), population),
            "agents": sorted({row[agent_field] for row in selected}),
            "agent_count": len({row[agent_field] for row in selected}),
            "seats": sorted({row["seat"] for row in selected}),
        }
    return {"population": population, "counts": dict(counts), "per_class": per_class}


def evaluate_field_gate(field_summary: dict) -> dict:
    result = {}
    for cls in CLASSES:
        stats = field_summary["per_class"][cls]
        gates = {
            "top5_rate_at_least_60pct": stats["rate"] >= 0.60,
            "at_least_4_of_5_top5_agents": stats["agent_count"] >= 4,
            "both_seats": stats["seats"] == [0, 1],
        }
        result[cls] = {"gates": gates, "pass": all(gates.values()), "stats": stats}
    return result


def evaluate_local_gate(local_returns_by_class: dict, total_returns: int) -> dict:
    result = {}
    for cls in CLASSES:
        count = local_returns_by_class.get(cls, 0)
        result[cls] = {
            "count": count,
            "rate": ratio(count, total_returns),
            "pass": count >= 90,
        }
    return result


def determinism_block(
    local_summary_wall: tuple[float | None, float | None],
    local_events_identical: bool,
    field_wall: tuple[float | None, float | None],
) -> dict:
    return {
        "local_summary_jobs1_sha256": sha256(LOCAL_SUMMARY_A),
        "local_summary_jobs20_sha256": sha256(LOCAL_SUMMARY_B),
        "local_summary_byte_identical": LOCAL_SUMMARY_A.read_bytes() == LOCAL_SUMMARY_B.read_bytes(),
        "local_events_jobs1_sha256": sha256(LOCAL_EVENTS_A),
        "local_events_jobs20_sha256": sha256(LOCAL_EVENTS_B),
        "local_events_byte_identical": local_events_identical,
        "local_jobs1_wall_seconds": local_summary_wall[0],
        "local_jobs20_wall_seconds": local_summary_wall[1],
        "field_jobs1_sha256": sha256(FIELD_A),
        "field_jobs20_sha256": sha256(FIELD_B),
        "field_byte_identical": FIELD_A.read_bytes() == FIELD_B.read_bytes(),
        "field_jobs1_wall_seconds": field_wall[0],
        "field_jobs20_wall_seconds": field_wall[1],
    }


def analyze(
    local_a: list[dict],
    local_b: list[dict],
    field_a: list[dict],
    field_b: list[dict],
    lock: dict,
    *,
    local_jobs1_wall: float | None,
    local_jobs20_wall: float | None,
    field_jobs1_wall: float | None,
    field_jobs20_wall: float | None,
) -> dict:
    local_integrity_result, entries, returns = local_integrity(local_a, local_b)
    field_integrity_result, top5, rank620 = field_integrity(field_a, field_b)
    integrity_pass = all(
        value for value in local_integrity_result.values() if isinstance(value, bool)
    ) and all(
        value for value in field_integrity_result.values() if isinstance(value, bool)
    )

    local_class_counts = Counter(row["acquisition_class"] for row in returns)
    local_gate = evaluate_local_gate(local_class_counts, len(returns))
    top5_summary = verb_return_summary(top5, len(top5), "actor")
    rank620_summary = verb_return_summary(rank620, len(rank620), "actor")
    field_gate = evaluate_field_gate(top5_summary)

    frozen_eligible = [
        cls for cls in CLASSES if field_gate[cls]["pass"] and local_gate[cls]["pass"]
    ]
    if frozen_eligible:
        verdict = (
            f"frozen_eligible_class={frozen_eligible[0]}"
            if len(frozen_eligible) == 1
            else f"frozen_eligible_classes={'+'.join(frozen_eligible)}"
        )
        decision_sentence = (
            f"{frozen_eligible[0]} is FROZEN-ELIGIBLE: it passes both the field gate "
            "(>=60% of top-5 PLANT returns, >=4/5 top agents, both seats) and the local gate "
            "(>=90/135 natural PLANT returns)."
        )
    else:
        verdict = "no_class_frozen_eligible"
        decision_sentence = (
            "No class passes both gates: close hand-written successor controllers; the "
            "successor branch proceeds only as trajectory-valued semantic actions with short "
            "resident-backed rollouts."
        )

    single_persistent_job_rate_local = ratio(
        sum(row["single_persistent_job"] == "1" for row in returns), len(returns)
    )
    single_persistent_job_rate_field_top5 = ratio(
        sum(row["single_persistent_job"] for row in top5), len(top5)
    )

    return {
        "schema": "troll-farm-d167a-successor-acquisition-path-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "input_hashes": {
            "protocol": sha256(PROTOCOL),
            "lock": sha256(LOCK),
            "rust_runner": sha256(RUST_RUNNER),
            "field_extractor": sha256(FIELD_EXTRACTOR),
            "analyzer": sha256(SELF),
            "local_summary_jobs20": sha256(LOCAL_SUMMARY_B),
            "local_events_jobs20": sha256(LOCAL_EVENTS_B),
            "field_jobs20": sha256(FIELD_B),
            "d161_reference": sha256(D161),
            "d166a_local_reference": sha256(D166_LOCAL),
            "d166a_field_reference": sha256(D166_FIELD),
        },
        "row_counts": {
            "local_tasks": len(local_b),
            "local_entries": len(entries),
            "local_natural_returns": len(returns),
            "field_rows": len(field_b),
            "field_top5": len(top5),
            "field_rank6_20": len(rank620),
        },
        "integrity": {
            "local": local_integrity_result,
            "field": field_integrity_result,
        },
        "integrity_pass": integrity_pass,
        "determinism": determinism_block(
            (local_jobs1_wall, local_jobs20_wall),
            LOCAL_EVENTS_A.read_bytes() == LOCAL_EVENTS_B.read_bytes(),
            (field_jobs1_wall, field_jobs20_wall),
        ),
        "local": {
            "returns": len(returns),
            "class_counts": dict(local_class_counts),
            "class_rates": {
                cls: ratio(local_class_counts.get(cls, 0), len(returns)) for cls in CLASSES
            },
            "species_distribution": dict(
                Counter(row["species_planted"] for row in returns)
            ),
            "single_persistent_job_rate": single_persistent_job_rate_local,
            "median_path_length_turns": sorted(
                int(row["path_length_turns"]) for row in returns
            )[len(returns) // 2]
            if returns
            else None,
            "gate": local_gate,
        },
        "field": {
            "top5": top5_summary,
            "rank_6_20": rank620_summary,
            "top5_single_persistent_job_rate": single_persistent_job_rate_field_top5,
            "acquisition_predates_suppression_count": sum(
                row["acquisition_predates_suppression"] for row in field_b
            ),
            "acquisition_predates_suppression_rate": ratio(
                sum(row["acquisition_predates_suppression"] for row in field_b), len(field_b)
            ),
            "gate": field_gate,
        },
        "decision": {
            "verdict": verdict,
            "decision_sentence": decision_sentence,
            "frozen_eligible_classes": frozen_eligible,
            "construct_candidate": False,
            "arena_or_submission": False,
            "yt": False,
            "reserved_maps_opened": False,
        },
    }


def run(
    output: Path = OUTPUT,
    *,
    local_jobs1_wall: float | None = None,
    local_jobs20_wall: float | None = None,
    field_jobs1_wall: float | None = None,
    field_jobs20_wall: float | None = None,
) -> dict:
    lock = verify_lock()
    local_a = read_tsv(LOCAL_SUMMARY_A)
    local_b = read_tsv(LOCAL_SUMMARY_B)
    field_a = read_jsonl(FIELD_A)
    field_b = read_jsonl(FIELD_B)
    result = analyze(
        local_a,
        local_b,
        field_a,
        field_b,
        lock,
        local_jobs1_wall=local_jobs1_wall,
        local_jobs20_wall=local_jobs20_wall,
        field_jobs1_wall=field_jobs1_wall,
        field_jobs20_wall=field_jobs20_wall,
    )
    atomic_write(output, result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--local-jobs1-wall", type=float)
    parser.add_argument("--local-jobs20-wall", type=float)
    parser.add_argument("--field-jobs1-wall", type=float)
    parser.add_argument("--field-jobs20-wall", type=float)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    result = run(
        args.output,
        local_jobs1_wall=args.local_jobs1_wall,
        local_jobs20_wall=args.local_jobs20_wall,
        field_jobs1_wall=args.field_jobs1_wall,
        field_jobs20_wall=args.field_jobs20_wall,
    )
    print(
        json.dumps(
            {
                "integrity_pass": result["integrity_pass"],
                "row_counts": result["row_counts"],
                "determinism": result["determinism"],
                "local_gate": result["local"]["gate"],
                "field_gate": result["field"]["gate"],
                "decision": result["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
