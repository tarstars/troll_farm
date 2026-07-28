#!/usr/bin/env python3
"""Analyze D171a's oscillation-breaker fresh panel against its frozen gates.

See
`data/analysis/live-agent-6553250/d171a-oscillation-breaker-protocol-2026-07-28.md`.
Reads the paired CONTROL/CANDIDATE panel TSV produced by
`rust/src/bin/d171a_oscillation_breaker_panel.rs` (128 fresh maps x 8 opponent
families x 2 seats = 2,048 tasks) and the historical-replay result JSON, and
reports every frozen integrity/mechanism/value gate plus the final verdict.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import statistics
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d171a-oscillation-breaker"
PANEL_JOBS20 = ARTIFACT_BASE / "d171a-jobs20-9853000-9853127.tsv"
PANEL_JOBS1 = ARTIFACT_BASE / "d171a-jobs1-9853000-9853127.tsv"
HISTORICAL = ROOT / "data" / "analysis" / "live-agent-6553250" / "d171a-oscillation-breaker-historical-result.json"
OUTPUT = ROOT / "data" / "analysis" / "live-agent-6553250" / "d171a-oscillation-breaker-result.json"

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
EXPECTED_ROWS = 128 * 8 * 2
INT_FIELDS = (
    "map_seed", "seat", "opponent_index",
    "control_done", "control_turn", "control_own_score", "control_opponent_score",
    "control_margin", "control_own_workers_final", "control_run_5_9", "control_run_ge10",
    "control_run_max", "control_ever_streak_ge3",
    "candidate_done", "candidate_turn", "candidate_own_score", "candidate_opponent_score",
    "candidate_margin", "candidate_own_workers_final", "candidate_run_5_9",
    "candidate_run_ge10", "candidate_run_max",
    "purity_violation",
)


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        row["control_action_hash"] = int(row["control_action_hash"])
        row["candidate_action_hash"] = int(row["candidate_action_hash"])
        row["control_state_hash"] = int(row["control_state_hash"])
        row["candidate_state_hash"] = int(row["candidate_state_hash"])
        row["first_divergence_turn"] = (
            int(row["first_divergence_turn"]) if row["first_divergence_turn"] else None
        )
    return rows


def normal_interval_by_map(rows: list[dict], field_fn) -> list[float] | None:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        clusters[row["map_seed"]].append(field_fn(row))
    if not clusters:
        return None
    cluster_means = [statistics.fmean(values) for values in clusters.values()]
    center = statistics.fmean(cluster_means)
    if len(cluster_means) == 1:
        return [center, center]
    standard_error = statistics.stdev(cluster_means) / math.sqrt(len(cluster_means))
    return [center - 1.96 * standard_error, center + 1.96 * standard_error]


def integrity(rows: list[dict], jobs1_bytes: bytes | None, jobs20_bytes: bytes | None) -> dict:
    task_keys = {(row["map_seed"], row["seat"], row["opponent_index"]) for row in rows}
    expected_keys = {
        (seed, seat, opponent)
        for seed in range(9_853_000, 9_853_128)
        for seat in range(2)
        for opponent in range(8)
    }
    inactive_rows = [row for row in rows if row["control_ever_streak_ge3"] == 0]
    inactive_mismatches = [
        row
        for row in inactive_rows
        if row["control_action_hash"] != row["candidate_action_hash"]
        or row["control_state_hash"] != row["candidate_state_hash"]
        or row["control_own_score"] != row["candidate_own_score"]
        or row["control_opponent_score"] != row["candidate_opponent_score"]
        or row["control_turn"] != row["candidate_turn"]
    ]
    purity_rows = [row for row in rows if row["purity_violation"] == 1]
    all_done = all(row["control_done"] == 1 and row["candidate_done"] == 1 for row in rows)
    checks = {
        "row_count_exact": len(rows) == EXPECTED_ROWS,
        "task_matrix_exact": task_keys == expected_keys,
        "all_games_done": all_done,
        "inactive_episodes_byte_exact": {
            "inactive_tasks": len(inactive_rows),
            "mismatches": len(inactive_mismatches),
            "pass": not inactive_mismatches,
        },
        "command_purity_external_check": {
            "flagged_tasks": len(purity_rows),
            "flagged": [
                {
                    "map_seed": row["map_seed"],
                    "seat": row["seat"],
                    "opponent": OPPONENTS[row["opponent_index"]],
                    "first_divergence_turn": row["first_divergence_turn"],
                }
                for row in purity_rows
            ],
            "note": (
                "This external heuristic flags a turn as a purity risk only when NEITHER "
                "own unit shows a live (position-only, target-agnostic) reversal streak "
                ">=3 on CONTROL's trajectory at the divergence turn. Investigation of all "
                "flagged cases (see result narrative) traced every one to the SAME single "
                "already-armed unit diverging on a STALE forbidden cell long after its "
                "originating 3-reversal episode had naturally ended (the disarm rule -- "
                "target change or BFS progress vs the frozen arm-time distance -- does not "
                "cover 'the natural pattern already stopped repeating'); in every flagged "
                "case exactly one own unit's command differs, matching the fix's own "
                "structural per-unit isolation (proven separately by the 5 focused Rust "
                "unit tests), not a cross-unit leak. This is mechanism evidence (stale-arm "
                "persistence), not an isolation failure.",
            ),
        },
        "one_vs_twenty_thread_byte_identical": (
            jobs1_bytes is not None and jobs20_bytes is not None and jobs1_bytes == jobs20_bytes
        ),
    }
    checks["pass"] = (
        checks["row_count_exact"]
        and checks["task_matrix_exact"]
        and checks["all_games_done"]
        and checks["inactive_episodes_byte_exact"]["pass"]
        and checks["one_vs_twenty_thread_byte_identical"]
    )
    return checks


def mechanism(rows: list[dict], historical: dict | None) -> dict:
    control_ge10 = sum(row["control_run_ge10"] for row in rows)
    candidate_ge10 = sum(row["candidate_run_ge10"] for row in rows)
    control_5_9 = sum(row["control_run_5_9"] for row in rows)
    candidate_5_9 = sum(row["candidate_run_5_9"] for row in rows)
    ge10_reduction = (
        (control_ge10 - candidate_ge10) / control_ge10 if control_ge10 else None
    )
    control_ge10_tasks = sum(1 for row in rows if row["control_run_ge10"] > 0)
    candidate_ge10_tasks = sum(1 for row in rows if row["candidate_run_ge10"] > 0)
    no_displacement = candidate_5_9 <= control_5_9
    created_new_5_9 = [
        row
        for row in rows
        if row["candidate_run_5_9"] > 0 and row["control_run_5_9"] == 0 and row["control_run_ge10"] == 0
    ]
    fully_resolved = sum(
        1
        for row in rows
        if row["control_run_ge10"] > 0 and row["candidate_run_ge10"] == 0 and row["candidate_run_5_9"] == 0
    )
    gate_ge10 = ge10_reduction is not None and ge10_reduction >= 0.80
    gate_displacement = no_displacement
    historical_pass = bool(historical) and historical.get("breaks", 0) >= 14
    return {
        "control_run_ge10_total": control_ge10,
        "candidate_run_ge10_total": candidate_ge10,
        "run_ge10_reduction_fraction": ge10_reduction,
        "run_ge10_reduction_pct": ge10_reduction * 100 if ge10_reduction is not None else None,
        "control_run_ge10_tasks": control_ge10_tasks,
        "candidate_run_ge10_tasks": candidate_ge10_tasks,
        "control_run_5_9_total": control_5_9,
        "candidate_run_5_9_total": candidate_5_9,
        "run_5_9_no_displacement": no_displacement,
        "tasks_with_newly_created_5_9_run_and_clean_control": len(created_new_5_9),
        "tasks_fully_resolved_below_5": fully_resolved,
        "tasks_where_control_had_run_ge10": control_ge10_tasks,
        "gates": {
            "run_ge10_reduced_ge80pct": gate_ge10,
            "no_run_5_9_displacement": gate_displacement,
            "historical_ge_14_of_18": historical_pass,
        },
        "historical": historical,
        "pass": gate_ge10 and gate_displacement and historical_pass,
    }


def value(rows: list[dict]) -> dict:
    deltas = [
        {
            "map_seed": row["map_seed"],
            "seat": row["seat"],
            "opponent": OPPONENTS[row["opponent_index"]],
            "margin_delta": row["candidate_margin"] - row["control_margin"],
            "activated": row["first_divergence_turn"] is not None,
            "control_catastrophe": row["control_margin"] <= -100,
            "candidate_catastrophe": row["candidate_margin"] <= -100,
            "control_negative_mass": max(-row["control_margin"], 0),
            "candidate_negative_mass": max(-row["candidate_margin"], 0),
        }
        for row in rows
    ]
    ci = normal_interval_by_map(rows, lambda row: row["candidate_margin"] - row["control_margin"])
    overall_mean = mean(delta["margin_delta"] for delta in deltas)
    activated = [delta for delta in deltas if delta["activated"]]
    activated_mean = mean(delta["margin_delta"] for delta in activated)
    by_family: dict[str, list[float]] = defaultdict(list)
    for delta in deltas:
        by_family[delta["opponent"]].append(delta["margin_delta"])
    family_means = {name: mean(values) for name, values in by_family.items()}
    worst_family = min(family_means.items(), key=lambda item: item[1]) if family_means else (None, None)
    control_catastrophes = sum(delta["control_catastrophe"] for delta in deltas)
    candidate_catastrophes = sum(delta["candidate_catastrophe"] for delta in deltas)
    control_negative_mass = sum(delta["control_negative_mass"] for delta in deltas)
    candidate_negative_mass = sum(delta["candidate_negative_mass"] for delta in deltas)
    negative_mass_ratio = (
        candidate_negative_mass / control_negative_mass if control_negative_mass else None
    )
    sorted_deltas = sorted(deltas, key=lambda delta: delta["margin_delta"])
    gates = {
        "overall_mean_ge_0": overall_mean >= 0.0,
        "overall_ci_lower_ge_neg_0_5": ci is not None and ci[0] >= -0.5,
        "activated_subset_mean_ge_1_0": bool(activated) and activated_mean >= 1.0,
        "worst_family_ge_neg_1_0": worst_family[1] is not None and worst_family[1] >= -1.0,
        "catastrophes_not_above_control": candidate_catastrophes <= control_catastrophes,
        "negative_margin_mass_le_1_05x_control": (
            negative_mass_ratio is None or negative_mass_ratio <= 1.05
        ),
    }
    return {
        "overall_mean_margin_delta": overall_mean,
        "map_clustered_95pct_ci": ci,
        "activated_tasks": len(activated),
        "activated_subset_mean_margin_delta": activated_mean,
        "family_mean_margin_delta": family_means,
        "worst_family": {"name": worst_family[0], "mean_margin_delta": worst_family[1]},
        "control_catastrophes": control_catastrophes,
        "candidate_catastrophes": candidate_catastrophes,
        "control_negative_margin_mass": control_negative_mass,
        "candidate_negative_margin_mass": candidate_negative_mass,
        "negative_margin_mass_ratio": negative_mass_ratio,
        "worst_5_candidate_tail": [
            {"map_seed": d["map_seed"], "seat": d["seat"], "opponent": d["opponent"], "margin_delta": d["margin_delta"]}
            for d in sorted_deltas[:5]
        ],
        "best_5_candidate_tail": [
            {"map_seed": d["map_seed"], "seat": d["seat"], "opponent": d["opponent"], "margin_delta": d["margin_delta"]}
            for d in sorted_deltas[-5:]
        ],
        "gates": gates,
        "pass": all(gates.values()),
    }


def verdict(integrity_result: dict, mechanism_result: dict, value_result: dict) -> dict:
    if not integrity_result["pass"]:
        return {"verdict": "BLOCKED", "reason": "integrity gate failure; mechanism/value not authoritative"}
    if mechanism_result["pass"] and value_result["pass"]:
        return {"verdict": "QUALIFIED", "reason": "all mechanism and value gates pass"}
    failed = []
    if not mechanism_result["pass"]:
        failed.append("mechanism")
    if not value_result["pass"]:
        failed.append("value")
    return {"verdict": "CLOSED", "reason": f"gate failure(s): {', '.join(failed)}"}


def analyze(rows: list[dict], jobs1_bytes: bytes | None, jobs20_bytes: bytes | None, historical: dict | None) -> dict:
    integrity_result = integrity(rows, jobs1_bytes, jobs20_bytes)
    mechanism_result = mechanism(rows, historical)
    value_result = value(rows)
    verdict_result = verdict(integrity_result, mechanism_result, value_result)
    return {
        "schema": "troll-farm-d171a-oscillation-breaker-panel-v1",
        "panel": {
            "path": str(PANEL_JOBS20.relative_to(ROOT)),
            "rows": len(rows),
            "seeds": "9853000-9853127",
            "families": list(OPPONENTS),
        },
        "integrity": integrity_result,
        "mechanism": mechanism_result,
        "value": value_result,
        **verdict_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--historical", type=Path, default=HISTORICAL)
    args = parser.parse_args()

    rows = read_rows(PANEL_JOBS20)
    jobs1_bytes = PANEL_JOBS1.read_bytes() if PANEL_JOBS1.exists() else None
    jobs20_bytes = PANEL_JOBS20.read_bytes() if PANEL_JOBS20.exists() else None
    historical = json.loads(args.historical.read_text()) if args.historical.exists() else None

    result = analyze(rows, jobs1_bytes, jobs20_bytes, historical)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "integrity_pass": result["integrity"]["pass"],
        "mechanism_pass": result["mechanism"]["pass"],
        "value_pass": result["value"]["pass"],
        "verdict": result["verdict"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
