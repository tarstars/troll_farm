#!/usr/bin/env python3
"""Analyze D174a's opportunistic-mining fresh panel against its frozen gates.

See
`data/analysis/live-agent-6553250/d174a-opportunistic-mining-protocol-2026-07-28.md`.

Two input families, both produced by `rust/src/bin/d174a_opportunistic_mining_panel.rs`:

1. The paired outcome TSV (128 fresh maps x 8 opponent families x 2 seats = 2,048 tasks),
   at 1 and 20 threads, for the integrity (determinism, inactive-episode byte-exactness)
   and value gates (paired margin deltas) -- same statistical methodology as
   `analyze_d173b_harvest_before_chop.py`/`analyze_d171a_oscillation_breaker.py`
   (map-clustered 95% CI).
2. Full per-turn trajectory NDJSON for both arms (CONTROL always; CANDIDATE only for
   tasks where a divergence occurred -- an inactive task is byte-identical to CONTROL by
   construction, so decoding it a second time would only reproduce CONTROL's own counts),
   bridged into `cgauto.waste_sweep.build_decoded_game` so all six standing waste
   detectors, plus B3.9's `cgauto.iron_acquisition_audit` mining/reachability
   measurements, run over both arms for the mechanism gate.

Both D174a deltas (the opportunistic-mining post-selection rewrite, and the one-clause
TRAIN-gate repair in `MoisanBot::can_train`) are stateless and freshly recomputed every
turn, so "activated" is exactly "own commands ever diverge between control and
candidate" -- if neither delta ever fires, the two trajectories are byte-identical for
the whole game by induction.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.iron_acquisition_audit import (  # noqa: E402
    iron_reachability_episodes,
    iron_source_geometry,
    mining_behavior_for_game,
    own_states_by_turn,
)
from cgauto.waste_sweep import DETECTORS, DecodedGame, build_decoded_game  # noqa: E402

ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d174a-opportunistic-mining"
PANEL_JOBS20 = ARTIFACT_BASE / "d174a-jobs20-9855000-9855127.tsv"
PANEL_JOBS1 = ARTIFACT_BASE / "d174a-jobs1-9855000-9855127.tsv"
TRAJ_CONTROL = ARTIFACT_BASE / "d174a-trajectories-control-9855000-9855127.ndjson"
TRAJ_CANDIDATE = ARTIFACT_BASE / "d174a-trajectories-candidate-9855000-9855127.ndjson"
OUTPUT = ROOT / "data" / "analysis" / "live-agent-6553250" / "d174a-opportunistic-mining-result.json"

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
START_SEED = 9_855_000
MAP_COUNT = 128
INT_FIELDS = (
    "map_seed", "seat", "opponent_index",
    "control_done", "control_turn", "control_own_score", "control_opponent_score",
    "control_margin", "control_own_workers_final",
    "candidate_done", "candidate_turn", "candidate_own_score", "candidate_opponent_score",
    "candidate_margin", "candidate_own_workers_final",
    "activated",
)

# Mechanism gate frozen thresholds (protocol section "Mechanism gates").
IRON_PER_GAME_MIN = 4.0
UNMINED_REACHABLE_REDUCTION_MIN_PCT = 50.0
WORKER3_TRAIN_RATE_MIN_PCT = 25.0
DETECTOR_WORSEN_MAX_PCT = 10.0


# ---------------------------------------------------------------------------
# TSV (value / integrity gates) -- same methodology as D173b
# ---------------------------------------------------------------------------


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        for field in (
            "control_action_hash", "control_own_action_hash", "control_state_hash",
            "candidate_action_hash", "candidate_own_action_hash", "candidate_state_hash",
        ):
            row[field] = int(row[field])
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
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in range(8)
    }
    inactive_rows = [row for row in rows if row["activated"] == 0]
    inactive_mismatches = [
        row
        for row in inactive_rows
        if row["control_action_hash"] != row["candidate_action_hash"]
        or row["control_state_hash"] != row["candidate_state_hash"]
        or row["control_own_score"] != row["candidate_own_score"]
        or row["control_opponent_score"] != row["candidate_opponent_score"]
        or row["control_turn"] != row["candidate_turn"]
        or row["control_own_workers_final"] != row["candidate_own_workers_final"]
    ]
    all_done = all(row["control_done"] == 1 and row["candidate_done"] == 1 for row in rows)
    checks = {
        "row_count_exact": len(rows) == EXPECTED_ROWS,
        "task_matrix_exact": task_keys == expected_keys,
        "all_games_done": all_done,
        "inactive_episodes_byte_exact": {
            "inactive_tasks": len(inactive_rows),
            "activated_tasks": len(rows) - len(inactive_rows),
            "mismatches": len(inactive_mismatches),
            "pass": not inactive_mismatches,
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


def value(rows: list[dict]) -> dict:
    deltas = [
        {
            "map_seed": row["map_seed"],
            "seat": row["seat"],
            "opponent": OPPONENTS[row["opponent_index"]],
            "margin_delta": row["candidate_margin"] - row["control_margin"],
            "activated": row["activated"] == 1,
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
        "overall_mean_ge_1_0": overall_mean >= 1.0,
        "overall_ci_lower_ge_0_0": ci is not None and ci[0] >= 0.0,
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


def worker3_train_rate(rows: list[dict]) -> dict:
    """Workforce is monotonic non-decreasing in this engine (TRAIN is the only unit-
    creation effect; there is no unit-removal/death mechanic), so `own_workers_final >= 3`
    is exactly equivalent to 'a 3rd-or-later worker was trained at some point in the
    game' -- computed directly from the TSV, no trajectory decode needed."""

    control_hits = sum(1 for row in rows if row["control_own_workers_final"] >= 3)
    candidate_hits = sum(1 for row in rows if row["candidate_own_workers_final"] >= 3)
    total = len(rows)
    control_pct = 100.0 * control_hits / total if total else None
    candidate_pct = 100.0 * candidate_hits / total if total else None
    return {
        "tasks": total,
        "control_worker3plus_tasks": control_hits,
        "control_pct": control_pct,
        "candidate_worker3plus_tasks": candidate_hits,
        "candidate_pct": candidate_pct,
        "gate_min_pct": WORKER3_TRAIN_RATE_MIN_PCT,
        "counterfactual_prediction_pct": 84.4,
        "shortfall_vs_counterfactual_pct": (
            84.4 - candidate_pct if candidate_pct is not None else None
        ),
        "pass": candidate_pct is not None and candidate_pct >= WORKER3_TRAIN_RATE_MIN_PCT,
    }


# ---------------------------------------------------------------------------
# NDJSON -> DecodedGame bridge (identical schema/convention to D173b's own bridge)
# ---------------------------------------------------------------------------


def _expand_unit(arr: list) -> dict:
    return {
        "id": arr[0], "player": arr[1], "x": arr[2], "y": arr[3],
        "ms": arr[4], "cc": arr[5], "hp": arr[6], "chop": arr[7],
        "carry": arr[8:14],
    }


def _expand_plant(arr: list) -> dict:
    return {
        "x": arr[0], "y": arr[1], "type": arr[2], "size": arr[3],
        "health": arr[4], "fruits": arr[5], "cooldown": arr[6],
    }


def _expand_state(raw: dict) -> dict:
    return {
        "units": [_expand_unit(u) for u in raw["u"]],
        "plants": [_expand_plant(p) for p in raw["p"]],
        "inventories": raw["b"],
    }


def game_id_for(seed: int, seat: int, opponent: int, arm: str) -> int:
    base = (seed - START_SEED) * 16 + seat * 8 + opponent
    return base if arm == "control" else base + 10_000_000


def decode_record(record: dict) -> DecodedGame:
    states = [_expand_state(s) for s in record["states"]]
    trajectory = [
        {
            "commands0": ";".join(record["c0"][index]),
            "commands1": ";".join(record["c1"][index]),
        }
        for index in range(len(record["c0"]))
    ]
    me = record["seat"]
    opponent = 1 - me
    scores = record["scores"]
    margin = scores[me] - scores[opponent]
    ranks = [0, 0]
    if margin > 0:
        ranks[me], ranks[opponent] = 0, 1
    elif margin < 0:
        ranks[me], ranks[opponent] = 1, 0
    return build_decoded_game(
        game_id=game_id_for(record["seed"], record["seat"], record["opp"], record["arm"]),
        me=me,
        map_rows=record["map_rows"],
        states=states,
        trajectory=trajectory,
        scores=scores,
        ranks=ranks,
        opponent_name=record["opp_name"],
    )


@dataclass
class GameMechanismCounts:
    total_iron_mined: int
    unmined_reachable_workforce2plus: int
    reachable_workforce2plus_total: int
    detector_totals: dict[str, int]
    detector_turns: dict[str, int]


def _unmined_reachable_workforce2plus(game: DecodedGame) -> tuple[int, int]:
    behavior = mining_behavior_for_game(game)
    successful_turns_by_unit: dict[int, set[int]] = defaultdict(set)
    for event in behavior["mine_events"]:
        if event["success"]:
            successful_turns_by_unit[event["unit_id"]].add(event["turn"])

    sources = iron_source_geometry(game)
    own_by_turn = own_states_by_turn(game)
    episodes = iron_reachability_episodes(game, sources, own_by_turn)["strict"]
    workforce2plus = [episode for episode in episodes if episode["workforce_at_start"] >= 2]

    unmined = 0
    for episode in workforce2plus:
        turns_mined = successful_turns_by_unit.get(episode["unit_id"], set())
        hit = any(
            episode["start_turn"] <= turn <= episode["end_turn"] for turn in turns_mined
        )
        if not hit:
            unmined += 1
    return unmined, len(workforce2plus)


def count_one_game(record: dict) -> tuple[tuple[int, int, int], GameMechanismCounts]:
    game = decode_record(record)
    behavior = mining_behavior_for_game(game)
    unmined, reachable_total = _unmined_reachable_workforce2plus(game)
    detector_totals = {}
    detector_turns = {}
    for name, detector in DETECTORS.items():
        episodes = detector(game)
        detector_totals[name] = len(episodes)
        detector_turns[name] = sum(episode["duration"] for episode in episodes)
    key = (record["seed"], record["seat"], record["opp"])
    return key, GameMechanismCounts(
        total_iron_mined=behavior["total_iron_mined"],
        unmined_reachable_workforce2plus=unmined,
        reachable_workforce2plus_total=reachable_total,
        detector_totals=detector_totals,
        detector_turns=detector_turns,
    )


def iter_ndjson(path: Path):
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _count_many(records: list[dict], jobs: int) -> dict[tuple[int, int, int], GameMechanismCounts]:
    result: dict[tuple[int, int, int], GameMechanismCounts] = {}
    if jobs <= 1:
        for record in records:
            key, counts = count_one_game(record)
            result[key] = counts
        return result
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for key, counts in pool.map(count_one_game, records, chunksize=8):
            result[key] = counts
    return result


def mechanism(rows: list[dict], jobs: int) -> dict:
    control_records = list(iter_ndjson(TRAJ_CONTROL))
    candidate_records = list(iter_ndjson(TRAJ_CANDIDATE))
    control_counts = _count_many(control_records, jobs)
    candidate_counts = _count_many(candidate_records, jobs)

    missing_control = []
    missing_candidate_for_active = []
    control_iron_total = 0
    candidate_iron_total = 0
    control_unmined = 0
    candidate_unmined = 0
    control_reachable_total = 0
    candidate_reachable_total = 0
    control_detector_totals: dict[str, int] = defaultdict(int)
    candidate_detector_totals: dict[str, int] = defaultdict(int)
    control_detector_turns: dict[str, int] = defaultdict(int)
    candidate_detector_turns: dict[str, int] = defaultdict(int)
    activated_tasks_covered = 0

    for row in rows:
        key = (row["map_seed"], row["seat"], row["opponent_index"])
        control_side = control_counts.get(key)
        if control_side is None:
            missing_control.append(list(key))
            continue
        activated = row["activated"] == 1
        if activated:
            candidate_side = candidate_counts.get(key)
            if candidate_side is None:
                missing_candidate_for_active.append(list(key))
                continue
            activated_tasks_covered += 1
        else:
            candidate_side = control_side  # byte-identical trajectory; reuse control's counts

        control_iron_total += control_side.total_iron_mined
        candidate_iron_total += candidate_side.total_iron_mined
        control_unmined += control_side.unmined_reachable_workforce2plus
        candidate_unmined += candidate_side.unmined_reachable_workforce2plus
        control_reachable_total += control_side.reachable_workforce2plus_total
        candidate_reachable_total += candidate_side.reachable_workforce2plus_total
        for name in DETECTORS:
            control_detector_totals[name] += control_side.detector_totals[name]
            candidate_detector_totals[name] += candidate_side.detector_totals[name]
            control_detector_turns[name] += control_side.detector_turns[name]
            candidate_detector_turns[name] += candidate_side.detector_turns[name]

    tasks_covered = len(rows) - len(missing_control) - len(missing_candidate_for_active)
    control_iron_per_game = control_iron_total / tasks_covered if tasks_covered else None
    candidate_iron_per_game = candidate_iron_total / tasks_covered if tasks_covered else None

    unmined_reduction = (
        (control_unmined - candidate_unmined) / control_unmined if control_unmined else None
    )

    def worsen_pct(control_value: int, candidate_value: int) -> float | None:
        if control_value == 0:
            return None
        return 100.0 * (candidate_value - control_value) / control_value

    detector_report = {}
    detector_gate_pass = {}
    for name in DETECTORS:
        c = control_detector_totals[name]
        d = candidate_detector_totals[name]
        pct = worsen_pct(c, d)
        gate_pass = (pct is not None and pct <= DETECTOR_WORSEN_MAX_PCT) or (
            pct is None and d <= c
        )
        detector_gate_pass[name] = gate_pass
        detector_report[name] = {
            "control_episodes": c,
            "candidate_episodes": d,
            "worsen_pct": pct,
            "control_flagged_turns": control_detector_turns[name],
            "candidate_flagged_turns": candidate_detector_turns[name],
            "gate_le_10pct_worse": gate_pass,
        }

    gate_iron = candidate_iron_per_game is not None and candidate_iron_per_game >= IRON_PER_GAME_MIN
    gate_unmined = (
        unmined_reduction is not None and unmined_reduction * 100.0 >= UNMINED_REACHABLE_REDUCTION_MIN_PCT
    )
    gate_detectors = all(detector_gate_pass.values())

    worker3 = worker3_train_rate(rows)

    return {
        "tasks_covered": tasks_covered,
        "missing_control": missing_control,
        "missing_candidate_for_active": missing_candidate_for_active,
        "activated_tasks_covered": activated_tasks_covered,
        "iron_per_game": {
            "control_total": control_iron_total,
            "control_mean": control_iron_per_game,
            "candidate_total": candidate_iron_total,
            "candidate_mean": candidate_iron_per_game,
            "gate_min": IRON_PER_GAME_MIN,
            "b39_reference_control": 0.68,
            "b39_reference_top5": 13.02,
            "pass": gate_iron,
        },
        "unmined_reachable_workforce2plus": {
            "control_episodes": control_unmined,
            "control_reachable_total": control_reachable_total,
            "candidate_episodes": candidate_unmined,
            "candidate_reachable_total": candidate_reachable_total,
            "reduction_fraction": unmined_reduction,
            "reduction_pct": unmined_reduction * 100.0 if unmined_reduction is not None else None,
            "gate_min_reduction_pct": UNMINED_REACHABLE_REDUCTION_MIN_PCT,
            "pass": gate_unmined,
        },
        "worker3_train_rate": worker3,
        "waste_sweep_detectors": detector_report,
        "gates": {
            "iron_per_game_ge_4_0": gate_iron,
            "unmined_reachable_reduced_ge_50pct": gate_unmined,
            "worker3_train_rate_ge_25pct": worker3["pass"],
            "no_detector_worsens_gt_10pct": gate_detectors,
        },
        "pass": gate_iron and gate_unmined and worker3["pass"] and gate_detectors,
    }


def verdict(integrity_result: dict, mechanism_result: dict, value_result: dict) -> dict:
    if not integrity_result["pass"]:
        return {"verdict": "BLOCKED", "reason": "integrity gate failure; mechanism/value not authoritative"}
    if mechanism_result["pass"] and value_result["pass"]:
        return {"verdict": "QUALIFIED", "reason": "all mechanism and value gates pass"}
    if not mechanism_result["pass"]:
        return {"verdict": "CLOSED-AT-MECHANISM", "reason": "one or more mechanism gates failed"}
    return {"verdict": "CLOSED-AT-VALUE", "reason": "mechanism passed but one or more value gates failed"}


def analyze(rows: list[dict], jobs1_bytes: bytes | None, jobs20_bytes: bytes | None, jobs: int) -> dict:
    integrity_result = integrity(rows, jobs1_bytes, jobs20_bytes)
    mechanism_result = mechanism(rows, jobs)
    value_result = value(rows)
    verdict_result = verdict(integrity_result, mechanism_result, value_result)
    return {
        "schema": "troll-farm-d174a-opportunistic-mining-panel-v1",
        "panel": {
            "path": str(PANEL_JOBS20.relative_to(ROOT)),
            "rows": len(rows),
            "seeds": "9855000-9855127",
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
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()

    rows = read_rows(PANEL_JOBS20)
    jobs1_bytes = PANEL_JOBS1.read_bytes() if PANEL_JOBS1.exists() else None
    jobs20_bytes = PANEL_JOBS20.read_bytes() if PANEL_JOBS20.exists() else None

    result = analyze(rows, jobs1_bytes, jobs20_bytes, args.jobs)
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
