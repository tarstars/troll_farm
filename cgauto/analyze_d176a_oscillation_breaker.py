#!/usr/bin/env python3
"""Analyze D176a's oscillation-breaker-successor fresh panel against its frozen gates.

See
`data/analysis/live-agent-6553250/d176a-oscillation-breaker-successor-protocol-2026-07-29.md`.

Two input families, both produced by `rust/src/bin/d176a_oscillation_breaker_panel.rs`:

1. The paired outcome TSV (128 fresh maps x 8 opponent families x 2 seats = 2,048 tasks),
   at 1 and 20 threads, for integrity (determinism, command purity) and the value gates
   (paired margin deltas) -- same statistical methodology as
   `analyze_d171a_oscillation_breaker.py` (map-clustered 95% CI).
2. Full per-turn trajectory NDJSON for both arms (CONTROL always; CANDIDATE only for tasks
   where a divergence occurred -- an inactive task is byte-identical to CONTROL by
   construction, so decoding it a second time would only reproduce CONTROL's own counts),
   bridged into `cgauto.waste_sweep.build_decoded_game` so all six standing waste detectors
   run over both arms for the detector-displacement mechanism sub-gate (reusing D174a's own
   NDJSON->DecodedGame bridge verbatim), AND used to recompute the run-length mechanism
   sub-gates (run_5_9/run_ge10/run_max/ever_streak_ge3) directly from raw positions.

   NOTE on why run-length is recomputed here rather than read from the TSV: the panel
   binary's own `RunTracker` (D171a's, reused verbatim for exact comparability) only
   buckets a streak into run_5_9/run_ge10 when a *non-reversal* turn closes it -- a streak
   still active at the moment a game ends (44% of this panel's 2,048 tasks stall before
   turn 300, and even full-length games can end mid-oscillation) is silently dropped
   entirely, undercounting exactly the kind of long-running episode this experiment cares
   about most. Discovered while root-causing the mechanism-gate failures below (a 69-turn
   CONTROL streak, task 9857002/opp0/seat0, that the TSV reported as zero oscillation
   because the 143-turn game ended while the streak was still open). This is a measurement
   correctness fix to the panel/analyzer tooling, not a change to the fix under test or to
   any gate threshold: the same corrected algorithm (identical predicate, identical
   run_5_9/run_ge10 bucket boundaries, with one added `close()` call per unit at the end of
   each game to flush a still-open streak) is applied identically to both arms. D171a's own
   historical numbers likely share this same gap; not restated here, out of scope.

Mechanism gates (anchored to the H13 reference bot measurement, not chosen freely):
  - Games containing a >=10-turn same-two-cell run: candidate rate <= 6.0% (yamo's measured
    2.9% is the ceiling; our own measured rate is ~18.2% on real ladder games -- reported
    here as descriptive context, not itself gated, since this panel is a different corpus).
  - Worst-case run length (candidate) <= 20 turns.
  - No displacement: candidate run_5_9 total must not exceed control's by more than 10%.
  - No de-novo oscillation: tasks with zero control oscillation (both buckets empty)
    acquiring a candidate run_ge10 must be <= 1% of all tasks.
  - No waste-sweep detector worsens by more than 10%.

Value gates (retained from the family that killed D171a/D173/D174): overall paired mean
>= 0.0 with clustered-by-map 95% CI lower bound >= -0.5; activated-subset mean >= +0.5
(preregistered floor, lowered from D171a's +1.0 before any result was seen); worst opponent
family >= -1.0; catastrophes <= control; negative-margin mass <= 1.05x control.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.waste_sweep import DETECTORS, DecodedGame, build_decoded_game  # noqa: E402

ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d176a-oscillation-breaker-successor"
PANEL_JOBS20 = ARTIFACT_BASE / "d176a-jobs20-9857000-9857127.tsv"
PANEL_JOBS1 = ARTIFACT_BASE / "d176a-jobs1-9857000-9857127.tsv"
TRAJ_CONTROL = ARTIFACT_BASE / "d176a-trajectories-control-9857000-9857127.ndjson"
TRAJ_CANDIDATE = ARTIFACT_BASE / "d176a-trajectories-candidate-9857000-9857127.ndjson"
OUTPUT = ROOT / "data" / "analysis" / "live-agent-6553250" / "d176a-oscillation-breaker-successor-result.json"

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
START_SEED = 9_857_000
MAP_COUNT = 128
INT_FIELDS = (
    "map_seed", "seat", "opponent_index",
    "control_done", "control_turn", "control_own_score", "control_opponent_score",
    "control_margin", "control_own_workers_final",
    "control_run_5_9", "control_run_ge10", "control_run_max", "control_ever_streak_ge3",
    "candidate_done", "candidate_turn", "candidate_own_score", "candidate_opponent_score",
    "candidate_margin", "candidate_own_workers_final",
    "candidate_run_5_9", "candidate_run_ge10", "candidate_run_max",
    "activated", "purity_violation",
)

# Mechanism gate frozen thresholds (protocol section "Mechanism gates").
GE10_TASK_RATE_MAX_PCT = 6.0
YAMO_REFERENCE_GE10_RATE_PCT = 2.9
CONTROL_REFERENCE_GE10_RATE_PCT = 18.2  # H13 real-ladder-corpus reference (descriptive only)
WORST_CASE_RUN_MAX_TURNS = 20
RUN_5_9_DISPLACEMENT_MAX_PCT = 10.0
DE_NOVO_MAX_PCT = 1.0
DETECTOR_WORSEN_MAX_PCT = 10.0

# Value gate frozen thresholds.
OVERALL_MEAN_MIN = 0.0
OVERALL_CI_LOWER_MIN = -0.5
ACTIVATED_MEAN_MIN = 0.5
WORST_FAMILY_MIN = -1.0
NEGATIVE_MASS_RATIO_MAX = 1.05


# ---------------------------------------------------------------------------
# TSV (integrity / mechanism run-length / value gates)
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


def sha256_of(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrity(rows: list[dict]) -> dict:
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
    purity_rows = [row for row in rows if row["purity_violation"] == 1]
    all_done = all(row["control_done"] == 1 and row["candidate_done"] == 1 for row in rows)

    jobs1_hash = sha256_of(PANEL_JOBS1)
    jobs20_hash = sha256_of(PANEL_JOBS20)

    checks = {
        "row_count_exact": len(rows) == EXPECTED_ROWS,
        "task_matrix_exact": task_keys == expected_keys,
        "all_games_done": all_done,
        "inactive_episodes_byte_exact": {
            "inactive_tasks": len(inactive_rows),
            "mismatches": len(inactive_mismatches),
            "mismatch_examples": [
                {"map_seed": row["map_seed"], "seat": row["seat"], "opponent": OPPONENTS[row["opponent_index"]]}
                for row in inactive_mismatches[:10]
            ],
            "pass": not inactive_mismatches,
        },
        "command_purity": {
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
            "pass": not purity_rows,
        },
        "one_vs_twenty_thread_byte_identical": {
            "jobs1_sha256": jobs1_hash,
            "jobs20_sha256": jobs20_hash,
            "pass": jobs1_hash is not None and jobs20_hash is not None and jobs1_hash == jobs20_hash,
        },
    }
    checks["pass"] = (
        checks["row_count_exact"]
        and checks["task_matrix_exact"]
        and checks["all_games_done"]
        and checks["inactive_episodes_byte_exact"]["pass"]
        and checks["command_purity"]["pass"]
        and checks["one_vs_twenty_thread_byte_identical"]["pass"]
    )
    return checks


def run_length_mechanism(rows: list[dict], run_stats: dict[tuple[int, int, int], dict]) -> dict:
    """`run_stats[key]` = {"control": {...}, "candidate": {...}} per-task corrected
    run_5_9/run_ge10/run_max/ever_streak_ge3, from `detector_displacement`'s single decode
    pass over the trajectory NDJSON (see module docstring for why this replaces the TSV's
    own run_* columns)."""
    total_tasks = len(rows)
    control_ge10_tasks = 0
    candidate_ge10_tasks = 0
    control_run_5_9_total = 0
    candidate_run_5_9_total = 0
    control_run_max = 0
    candidate_run_max = 0
    de_novo_tasks = []
    missing = []

    for row in rows:
        key = (row["map_seed"], row["seat"], row["opponent_index"])
        stats = run_stats.get(key)
        if stats is None:
            missing.append(list(key))
            continue
        control = stats["control"]
        candidate = stats["candidate"]
        control_ge10_tasks += control["run_ge10"] > 0
        candidate_ge10_tasks += candidate["run_ge10"] > 0
        control_run_5_9_total += control["run_5_9"]
        candidate_run_5_9_total += candidate["run_5_9"]
        control_run_max = max(control_run_max, control["run_max"])
        candidate_run_max = max(candidate_run_max, candidate["run_max"])
        if control["run_5_9"] == 0 and control["run_ge10"] == 0 and candidate["run_ge10"] > 0:
            de_novo_tasks.append({
                "map_seed": row["map_seed"], "seat": row["seat"], "opponent": row["opponent"],
                "candidate_run_ge10": candidate["run_ge10"], "candidate_run_max": candidate["run_max"],
            })

    control_ge10_rate_pct = 100.0 * control_ge10_tasks / total_tasks if total_tasks else None
    candidate_ge10_rate_pct = 100.0 * candidate_ge10_tasks / total_tasks if total_tasks else None
    displacement_pct = (
        100.0 * (candidate_run_5_9_total - control_run_5_9_total) / control_run_5_9_total
        if control_run_5_9_total
        else (0.0 if candidate_run_5_9_total == 0 else None)
    )
    de_novo_pct = 100.0 * len(de_novo_tasks) / total_tasks if total_tasks else None

    gate_ge10_rate = candidate_ge10_rate_pct is not None and candidate_ge10_rate_pct <= GE10_TASK_RATE_MAX_PCT
    gate_worst_case = candidate_run_max <= WORST_CASE_RUN_MAX_TURNS
    gate_displacement = displacement_pct is not None and displacement_pct <= RUN_5_9_DISPLACEMENT_MAX_PCT
    gate_de_novo = de_novo_pct is not None and de_novo_pct <= DE_NOVO_MAX_PCT

    return {
        "total_tasks": total_tasks,
        "missing_run_stats": missing,
        "ge10_task_rate": {
            "control_tasks": control_ge10_tasks,
            "control_rate_pct": control_ge10_rate_pct,
            "candidate_tasks": candidate_ge10_tasks,
            "candidate_rate_pct": candidate_ge10_rate_pct,
            "gate_max_pct": GE10_TASK_RATE_MAX_PCT,
            "yamo_reference_pct": YAMO_REFERENCE_GE10_RATE_PCT,
            "control_reference_pct_h13_real_corpus": CONTROL_REFERENCE_GE10_RATE_PCT,
            "pass": gate_ge10_rate,
        },
        "worst_case_run_length": {
            "control_run_max": control_run_max,
            "candidate_run_max": candidate_run_max,
            "gate_max_turns": WORST_CASE_RUN_MAX_TURNS,
            "yamo_reference_turns": 6,
            "control_reference_turns_h13_real_corpus": 133,
            "pass": gate_worst_case,
        },
        "run_5_9_displacement": {
            "control_total": control_run_5_9_total,
            "candidate_total": candidate_run_5_9_total,
            "displacement_pct": displacement_pct,
            "gate_max_pct": RUN_5_9_DISPLACEMENT_MAX_PCT,
            "pass": gate_displacement,
        },
        "de_novo_oscillation": {
            "tasks": len(de_novo_tasks),
            "pct": de_novo_pct,
            "gate_max_pct": DE_NOVO_MAX_PCT,
            "examples": de_novo_tasks[:10],
            "pass": gate_de_novo,
        },
        "gates": {
            "ge10_task_rate_le_6pct": gate_ge10_rate,
            "worst_case_run_le_20": gate_worst_case,
            "run_5_9_displacement_le_10pct": gate_displacement,
            "de_novo_le_1pct": gate_de_novo,
        },
        "pass": gate_ge10_rate and gate_worst_case and gate_displacement and gate_de_novo and not missing,
    }


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
        "overall_mean_ge_0": overall_mean >= OVERALL_MEAN_MIN,
        "overall_ci_lower_ge_neg_0_5": ci is not None and ci[0] >= OVERALL_CI_LOWER_MIN,
        "activated_subset_mean_ge_0_5": bool(activated) and activated_mean >= ACTIVATED_MEAN_MIN,
        "worst_family_ge_neg_1_0": worst_family[1] is not None and worst_family[1] >= WORST_FAMILY_MIN,
        "catastrophes_not_above_control": candidate_catastrophes <= control_catastrophes,
        "negative_margin_mass_le_1_05x_control": (
            negative_mass_ratio is None or negative_mass_ratio <= NEGATIVE_MASS_RATIO_MAX
        ),
    }
    return {
        "overall_mean_margin_delta": overall_mean,
        "map_clustered_95pct_ci": ci,
        "activated_tasks": len(activated),
        "activated_subset_mean_margin_delta": activated_mean,
        "activated_subset_floor": ACTIVATED_MEAN_MIN,
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


# ---------------------------------------------------------------------------
# NDJSON -> DecodedGame bridge (identical schema/convention to D174a's own bridge)
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


def _close_tracker(tracker: dict, totals: dict) -> None:
    if tracker["streak"] >= 10:
        totals["run_ge10"] += 1
    elif tracker["streak"] >= 5:
        totals["run_5_9"] += 1
    totals["run_max"] = max(totals["run_max"], tracker["streak"])
    tracker["streak"] = 0


def run_length_stats(game: DecodedGame) -> dict:
    """D171a's own `RunTracker` (position-only B3.2/B3.4 predicate: `positions[k]==
    positions[k-2] and positions[k]!=positions[k-1]`), reimplemented in Python directly
    from decoded per-turn positions, PLUS a correctness fix over the original Rust
    version: an explicit final close of every unit's tracker after the last observed
    state, so a streak still active when the game ends is still bucketed (see module
    docstring)."""
    trackers: dict[int, dict] = {}
    totals = {"run_5_9": 0, "run_ge10": 0, "run_max": 0}
    ever_streak_ge3 = False
    for state in game.states:
        own = [unit for unit in state["units"] if unit["player"] == game.me]
        for unit in own:
            cell = (unit["x"], unit["y"])
            tracker = trackers.setdefault(unit["id"], {"one_ago": None, "two_ago": None, "streak": 0})
            is_reversal = tracker["two_ago"] == cell and tracker["one_ago"] != cell
            if is_reversal:
                tracker["streak"] += 1
                if tracker["streak"] >= 3:
                    ever_streak_ge3 = True
            else:
                _close_tracker(tracker, totals)
            tracker["two_ago"] = tracker["one_ago"]
            tracker["one_ago"] = cell
    for tracker in trackers.values():
        _close_tracker(tracker, totals)  # flush any still-open streak at game end
    totals["ever_streak_ge3"] = ever_streak_ge3
    return totals


def count_one_game(record: dict) -> tuple[tuple[int, int, int], dict[str, int], dict[str, int], dict]:
    game = decode_record(record)
    detector_totals = {}
    detector_turns = {}
    for name, detector in DETECTORS.items():
        episodes = detector(game)
        detector_totals[name] = len(episodes)
        detector_turns[name] = sum(episode["duration"] for episode in episodes)
    key = (record["seed"], record["seat"], record["opp"])
    return key, detector_totals, detector_turns, run_length_stats(game)


def iter_ndjson(path: Path):
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _count_many(records: list[dict], jobs: int) -> dict[tuple[int, int, int], tuple[dict, dict, dict]]:
    result: dict[tuple[int, int, int], tuple[dict, dict, dict]] = {}
    if jobs <= 1:
        for record in records:
            key, totals, turns, run_stats = count_one_game(record)
            result[key] = (totals, turns, run_stats)
        return result
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for key, totals, turns, run_stats in pool.map(count_one_game, records, chunksize=8):
            result[key] = (totals, turns, run_stats)
    return result


def detector_displacement(rows: list[dict], jobs: int) -> tuple[dict, dict[tuple[int, int, int], dict]]:
    """Returns (detector_report, run_stats_by_key) -- one decode pass over both arms'
    trajectory NDJSON serves both the waste-sweep detector-displacement gate and the
    run-length mechanism gates (see module docstring)."""
    control_records = list(iter_ndjson(TRAJ_CONTROL))
    candidate_records = list(iter_ndjson(TRAJ_CANDIDATE))
    control_counts = _count_many(control_records, jobs)
    candidate_counts = _count_many(candidate_records, jobs)

    missing_control = []
    missing_candidate_for_active = []
    control_detector_totals: dict[str, int] = defaultdict(int)
    candidate_detector_totals: dict[str, int] = defaultdict(int)
    control_detector_turns: dict[str, int] = defaultdict(int)
    candidate_detector_turns: dict[str, int] = defaultdict(int)
    tasks_covered = 0
    run_stats_by_key: dict[tuple[int, int, int], dict] = {}

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
        else:
            candidate_side = control_side  # byte-identical trajectory; reuse control's counts
        tasks_covered += 1
        control_totals, control_turns, control_run_stats = control_side
        candidate_totals, candidate_turns, candidate_run_stats = candidate_side
        run_stats_by_key[key] = {"control": control_run_stats, "candidate": candidate_run_stats}
        for name in DETECTORS:
            control_detector_totals[name] += control_totals[name]
            candidate_detector_totals[name] += candidate_totals[name]
            control_detector_turns[name] += control_turns[name]
            candidate_detector_turns[name] += candidate_turns[name]

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

    gate_detectors = all(detector_gate_pass.values())
    report = {
        "tasks_covered": tasks_covered,
        "missing_control": missing_control,
        "missing_candidate_for_active": missing_candidate_for_active,
        "waste_sweep_detectors": detector_report,
        "gate_no_detector_worsens_gt_10pct": gate_detectors,
        "pass": gate_detectors,
    }
    return report, run_stats_by_key


def mechanism(rows: list[dict], jobs: int) -> dict:
    detectors, run_stats_by_key = detector_displacement(rows, jobs)
    run_length = run_length_mechanism(rows, run_stats_by_key)
    return {
        "run_length": run_length,
        "detector_displacement": detectors,
        "gates": {
            **run_length["gates"],
            "no_detector_worsens_gt_10pct": detectors["gate_no_detector_worsens_gt_10pct"],
        },
        "pass": run_length["pass"] and detectors["pass"],
    }


def verdict(integrity_result: dict, mechanism_result: dict, value_result: dict) -> dict:
    if not integrity_result["pass"]:
        return {"verdict": "BLOCKED", "reason": "integrity gate failure; mechanism/value not authoritative"}
    if not mechanism_result["pass"]:
        return {"verdict": "CLOSED-AT-MECHANISM", "reason": "one or more mechanism gates failed"}
    if not value_result["pass"]:
        return {"verdict": "CLOSED-AT-VALUE", "reason": "one or more value gates failed"}
    return {"verdict": "QUALIFIED", "reason": "all mechanism and value gates pass"}


def analyze(rows: list[dict], jobs: int) -> dict:
    integrity_result = integrity(rows)
    mechanism_result = mechanism(rows, jobs)
    value_result = value(rows)
    verdict_result = verdict(integrity_result, mechanism_result, value_result)
    return {
        "schema": "troll-farm-d176a-oscillation-breaker-successor-panel-v1",
        "panel": {
            "path": str(PANEL_JOBS20.relative_to(ROOT)),
            "rows": len(rows),
            "seeds": f"{START_SEED}-{START_SEED + MAP_COUNT - 1}",
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
    result = analyze(rows, args.jobs)
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
