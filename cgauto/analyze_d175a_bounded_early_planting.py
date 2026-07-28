#!/usr/bin/env python3
"""Analyze D175a's bounded-early-planting fresh panel against its frozen gates.

See
`data/analysis/live-agent-6553250/d175a-bounded-early-planting-protocol-2026-07-29.md`.

Two input families, both produced by `rust/src/bin/d175a_bounded_early_planting_panel.rs`:

1. The paired outcome TSV (256 fresh maps x 8 opponent families x 2 seats = 4,096 tasks),
   at 1 and 20 threads, for the integrity (determinism, inactive-episode byte-exactness)
   and value/safety gates (paired margin/own/opponent-score deltas) -- same statistical
   methodology as `analyze_d174a_opportunistic_mining.py`/`analyze_d173b_harvest_before_
   chop.py` (map-clustered 95% CI).
2. Full per-turn trajectory NDJSON for both arms (CONTROL always; CANDIDATE only for
   tasks where a divergence occurred -- an inactive task is byte-identical to CONTROL by
   construction), bridged into `cgauto.waste_sweep.build_decoded_game` so all six standing
   waste detectors run over both arms for the mechanism-gate displacement check, plus a
   from-scratch own-crop generation-lineage tracker (median first-plant turn, own-reap
   rate, peak concurrent own crops) built directly against the panel's own raw per-turn
   schema, mirroring `cgauto/planting_gate_diagnostic.py`'s `classify_peer_game`/
   `Generation`/`peak_concurrency` reference implementation and
   `cgauto/analyze_d101a_production_suppression.py`'s reap-rate definition so the
   candidate/control numbers here are directly comparable to B4.4's field figures
   (resident 0.93% own-reap, median first-plant turn 191.5).

The D175a fix (`YamoBot::bounded_early_plant_candidate`, a scored candidate injected into
the ordinary mid-game branch of `commands()`) is stateless and recomputed fresh every turn,
so "activated" is exactly "own commands ever diverge between control and candidate" -- if
the fix never fires, the two trajectories are byte-identical for the whole game by
induction.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
from dataclasses import dataclass, field
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

ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d175a-bounded-early-planting"
PANEL_JOBS20 = ARTIFACT_BASE / "d175a-panel-jobs20.tsv"
PANEL_JOBS1 = ARTIFACT_BASE / "d175a-panel-jobs1.tsv"
TRAJ_CONTROL = ARTIFACT_BASE / "d175a-control-trajectory.ndjson"
TRAJ_CANDIDATE = ARTIFACT_BASE / "d175a-candidate-trajectory.ndjson"
OUTPUT = ROOT / "data" / "analysis" / "live-agent-6553250" / "d175a-bounded-early-planting-result.json"

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
EXPECTED_ROWS = 256 * 8 * 2
START_SEED = 9_856_000
MAP_COUNT = 256
INT_FIELDS = (
    "map_seed", "seat", "opponent_index",
    "control_done", "control_turn", "control_own_score", "control_opponent_score",
    "control_margin", "control_own_workers_final",
    "candidate_done", "candidate_turn", "candidate_own_score", "candidate_opponent_score",
    "candidate_margin", "candidate_own_workers_final",
    "activated",
)

# Mechanism gate frozen thresholds (protocol section "Mechanism gates (frozen)").
FIRST_PLANT_TURN_MAX = 60.0
FIRST_PLANT_TURN_CONTROL_REFERENCE = 191.5
OWN_REAP_RATE_MIN_PCT = 5.0
OWN_REAP_RATE_CONTROL_REFERENCE_PCT = 0.93
PEAK_CONCURRENT_OWN_CROPS_MAX = 8.0
PEER_PEAK_CONCURRENCY_REFERENCE = 5.5  # B4.4/B4.5 field median
DETECTOR_WORSEN_MAX_PCT = 10.0

# Safety gate (protocol section "Value and safety gates (frozen)").
SAFETY_RATIO_MAX = 0.40

# Value gates (protocol section "Value and safety gates (frozen)").
VALUE_OVERALL_MEAN_MIN = 1.0
VALUE_ACTIVATED_MEAN_MIN = 1.0
VALUE_WORST_FAMILY_MIN = -1.0
VALUE_NEGATIVE_MASS_MAX_RATIO = 1.05


# ---------------------------------------------------------------------------
# TSV (integrity / value / safety gates)
# ---------------------------------------------------------------------------


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field_name in INT_FIELDS:
            row[field_name] = int(row[field_name])
        for field_name in (
            "control_action_hash", "control_own_action_hash", "control_state_hash",
            "candidate_action_hash", "candidate_own_action_hash", "candidate_state_hash",
        ):
            row[field_name] = int(row[field_name])
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
            "own_delta": row["candidate_own_score"] - row["control_own_score"],
            "opponent_delta": row["candidate_opponent_score"] - row["control_opponent_score"],
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
        "overall_mean_ge_1_0": overall_mean >= VALUE_OVERALL_MEAN_MIN,
        "overall_ci_lower_ge_0_0": ci is not None and ci[0] >= 0.0,
        "activated_subset_mean_ge_1_0": bool(activated) and activated_mean >= VALUE_ACTIVATED_MEAN_MIN,
        "worst_family_ge_neg_1_0": worst_family[1] is not None and worst_family[1] >= VALUE_WORST_FAMILY_MIN,
        "catastrophes_not_above_control": candidate_catastrophes <= control_catastrophes,
        "negative_margin_mass_le_1_05x_control": (
            negative_mass_ratio is None or negative_mass_ratio <= VALUE_NEGATIVE_MASS_MAX_RATIO
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
        "_deltas": deltas,  # consumed by safety(); stripped before writing output
    }


def safety(deltas: list[dict]) -> dict:
    """D89/D91's frozen competitive-efficiency ratio: selected (activated-subset) mean
    Delta-opponent-score <= 0.40 x selected mean Delta-own-score. Delta_own and
    Delta_opponent are computed per paired episode (candidate - control, same map/seat/
    opponent), each reported explicitly, not just the ratio -- per the task brief.
    Also reports the all-tasks (not just activated) pooled version for context; given the
    activation rate here is 99.8%, the two are expected to be nearly identical."""

    def summarize(subset: list[dict]) -> dict:
        own = mean(d["own_delta"] for d in subset)
        opponent = mean(d["opponent_delta"] for d in subset)
        ratio = (opponent / own) if own not in (0, 0.0) else None
        return {
            "n": len(subset),
            "mean_own_delta": own,
            "mean_opponent_delta": opponent,
            "ratio_opponent_over_own": ratio,
        }

    activated = [d for d in deltas if d["activated"]]
    activated_summary = summarize(activated)
    overall_summary = summarize(deltas)
    ratio = activated_summary["ratio_opponent_over_own"]
    own = activated_summary["mean_own_delta"]
    opponent = activated_summary["mean_opponent_delta"]
    # The ratio's premise (Delta_opponent <= 0.40x Delta_own) assumes Delta_own > 0 --
    # it is asking how much of a genuine OWN gain leaks to the opponent. If Delta_own <=
    # 0, a literal `ratio <= 0.40` can pass by sign flip alone (a negative ratio is always
    # <= 0.40) while substantively describing something *worse* than the gate was built to
    # catch: no own gain to justify any leak, and if Delta_opponent > 0 on top of that, the
    # candidate is strictly dominated (own down, opponent up) -- reported as an explicit
    # gate failure, not a misleading pass, regardless of the raw ratio's sign.
    if own is None:
        gate_pass = False
        classification = "own_delta_undefined"
    elif own <= 0:
        gate_pass = False
        classification = (
            "own_delta_nonpositive_dominated_by_opponent"
            if opponent > 0
            else "own_delta_nonpositive_no_genuine_gain_to_bound"
        )
    else:
        gate_pass = ratio is not None and ratio <= SAFETY_RATIO_MAX
        classification = "ratio_evaluated_normally"
    return {
        "definition": (
            "Delta_own_i = candidate_own_score_i - control_own_score_i; "
            "Delta_opponent_i = candidate_opponent_score_i - control_opponent_score_i; "
            "computed per paired episode (same map_seed/seat/opponent between arms), "
            "then meaned. Primary gate uses the ACTIVATED subset (D89/D91's own 'selected' "
            "convention); overall (all 4,096 tasks) reported for context. The ratio "
            "Delta_opponent/Delta_own only has its intended meaning (how much of a "
            "genuine own gain leaks to the opponent) when Delta_own > 0; when Delta_own "
            "<= 0 the gate is reported as FAILED outright rather than accepting a "
            "sign-flip pass, and classified explicitly."
        ),
        "activated_subset": activated_summary,
        "overall_all_tasks": overall_summary,
        "gate_max_ratio": SAFETY_RATIO_MAX,
        "d89_reference_ratio_FAILED": 0.511,
        "d91_reference_ratio_PASSED": 0.337,
        "classification": classification,
        "pass": gate_pass,
    }


# ---------------------------------------------------------------------------
# NDJSON -> DecodedGame bridge (identical schema/convention to D174a/D173b's own bridge)
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


def iter_ndjson(path: Path):
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


# ---------------------------------------------------------------------------
# Generation-lineage tracker (first-plant turn, own-reap rate, peak concurrency) --
# ported directly from `cgauto/planting_gate_diagnostic.py`'s own `Generation`/
# `classify_peer_game`/`peak_concurrency` reference implementation (B4.5's field study,
# itself independently cross-validated against B4.4's D101a-reused own-reap-rate figures
# -- both land in the same range for the same cohorts), adapted to this panel's own
# already-expanded per-turn schema (`DecodedGame.states`/`.trajectory`, built above)
# instead of a from-disk CG-replay decode. Own-reap rate is a POOLED, generation-level
# rate (own generations ever harvested by the owner at least once, divided by all own
# generations) -- not a per-game average -- matching B4.4/B4.5's own convention exactly
# (their field numbers, e.g. resident 0.93%, are pooled the same way).
# ---------------------------------------------------------------------------


@dataclass
class Generation:
    cell: tuple
    kind: str
    plant_turn: int
    end_turn: int | None = None
    ever_harvested_by_owner: bool = False
    self_chopped: bool = False
    opponent_chopped: bool = False


def own_generations(game: DecodedGame) -> list[Generation]:
    me = game.me
    open_generations: dict[tuple, Generation] = {}
    all_generations: list[Generation] = []
    for turn in range(1, len(game.states)):
        before = game.states[turn - 1]
        row = game.trajectory[turn - 1]
        before_units_by_id = {u["id"]: u for u in before["units"]}
        before_plants_by_cell = {(p["x"], p["y"]): p for p in before["plants"]}
        for player in (0, 1):
            commands = [c for c in row.get(f"commands{player}", "").split(";") if c]
            for command in commands:
                fields = command.split()
                if len(fields) < 2:
                    continue
                verb = fields[0].upper()
                try:
                    unit_id = int(fields[1])
                except ValueError:
                    continue
                unit = before_units_by_id.get(unit_id)
                if unit is None or unit["player"] != player:
                    continue
                cell = (unit["x"], unit["y"])
                if verb == "HARVEST":
                    plant = before_plants_by_cell.get(cell)
                    if player == me and plant is not None:
                        gen = open_generations.get(cell)
                        if gen is not None:
                            gen.ever_harvested_by_owner = True
                elif verb == "PLANT" and len(fields) >= 3 and player == me:
                    item = fields[2].upper()
                    gen = Generation(cell=cell, kind=item, plant_turn=turn)
                    open_generations[cell] = gen
                    all_generations.append(gen)
                elif verb == "CHOP":
                    plant = before_plants_by_cell.get(cell)
                    if plant is None:
                        continue
                    gen = open_generations.get(cell)
                    if gen is None:
                        continue
                    if player == me:
                        gen.self_chopped = True
                    else:
                        gen.opponent_chopped = True
        after = game.states[turn]
        after_plants_by_cell = {(p["x"], p["y"]): p for p in after["plants"]}
        for cell, gen in list(open_generations.items()):
            still_alive = (
                cell in after_plants_by_cell and after_plants_by_cell[cell]["type"] == gen.kind
            )
            if not still_alive:
                gen.end_turn = turn
                del open_generations[cell]
    for gen in open_generations.values():
        gen.end_turn = len(game.states) - 1
    return all_generations


def peak_concurrency(generations: list[Generation], total_turns: int) -> int:
    if not generations:
        return 0
    delta = [0] * (total_turns + 2)
    for gen in generations:
        start = gen.plant_turn
        end = gen.end_turn if gen.end_turn is not None else total_turns
        end = max(end, start)
        delta[start] += 1
        delta[min(end + 1, total_turns + 1)] -= 1
    running = 0
    peak = 0
    for value in delta:
        running += value
        peak = max(peak, running)
    return peak


def first_plant_turn(generations: list[Generation]) -> int | None:
    turns = [gen.plant_turn for gen in generations]
    return min(turns) if turns else None


@dataclass
class GameMechanismCounts:
    n_generations: int
    n_ever_harvested: int
    peak_concurrent: int
    first_plant_turn: int | None
    detector_totals: dict[str, int]
    detector_turns: dict[str, int]


def count_one_game(record: dict) -> tuple[tuple[int, int, int], GameMechanismCounts]:
    game = decode_record(record)
    gens = own_generations(game)
    detector_totals = {}
    detector_turns = {}
    for name, detector in DETECTORS.items():
        episodes = detector(game)
        detector_totals[name] = len(episodes)
        detector_turns[name] = sum(episode["duration"] for episode in episodes)
    key = (record["seed"], record["seat"], record["opp"])
    return key, GameMechanismCounts(
        n_generations=len(gens),
        n_ever_harvested=sum(1 for g in gens if g.ever_harvested_by_owner),
        peak_concurrent=peak_concurrency(gens, game.turns),
        first_plant_turn=first_plant_turn(gens),
        detector_totals=detector_totals,
        detector_turns=detector_turns,
    )


def iter_ndjson_records(path: Path):
    return list(iter_ndjson(path))


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
    control_records = iter_ndjson_records(TRAJ_CONTROL)
    candidate_records = iter_ndjson_records(TRAJ_CANDIDATE)
    control_counts = _count_many(control_records, jobs)
    candidate_counts = _count_many(candidate_records, jobs)

    missing_control: list[list[int]] = []
    missing_candidate_for_active: list[list[int]] = []
    control_first_plant_turns: list[int] = []
    candidate_first_plant_turns: list[int] = []
    control_generations = 0
    candidate_generations = 0
    control_harvested = 0
    candidate_harvested = 0
    control_peaks: list[int] = []
    candidate_peaks: list[int] = []
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

        if control_side.first_plant_turn is not None:
            control_first_plant_turns.append(control_side.first_plant_turn)
        if candidate_side.first_plant_turn is not None:
            candidate_first_plant_turns.append(candidate_side.first_plant_turn)
        control_generations += control_side.n_generations
        candidate_generations += candidate_side.n_generations
        control_harvested += control_side.n_ever_harvested
        candidate_harvested += candidate_side.n_ever_harvested
        control_peaks.append(control_side.peak_concurrent)
        candidate_peaks.append(candidate_side.peak_concurrent)
        for name in DETECTORS:
            control_detector_totals[name] += control_side.detector_totals[name]
            candidate_detector_totals[name] += candidate_side.detector_totals[name]
            control_detector_turns[name] += control_side.detector_turns[name]
            candidate_detector_turns[name] += candidate_side.detector_turns[name]

    tasks_covered = len(rows) - len(missing_control) - len(missing_candidate_for_active)

    def median_or_none(values: list[int]) -> float | None:
        return statistics.median(values) if values else None

    control_median_first_plant = median_or_none(control_first_plant_turns)
    candidate_median_first_plant = median_or_none(candidate_first_plant_turns)
    control_reap_rate_pct = (
        100.0 * control_harvested / control_generations if control_generations else None
    )
    candidate_reap_rate_pct = (
        100.0 * candidate_harvested / candidate_generations if candidate_generations else None
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

    gate_first_plant = (
        candidate_median_first_plant is not None
        and candidate_median_first_plant <= FIRST_PLANT_TURN_MAX
    )
    gate_reap = (
        candidate_reap_rate_pct is not None and candidate_reap_rate_pct >= OWN_REAP_RATE_MIN_PCT
    )
    candidate_mean_peak = mean(candidate_peaks)
    candidate_median_peak = median_or_none(candidate_peaks)
    gate_peak = candidate_mean_peak <= PEAK_CONCURRENT_OWN_CROPS_MAX
    gate_detectors = all(detector_gate_pass.values())

    return {
        "tasks_covered": tasks_covered,
        "missing_control": missing_control,
        "missing_candidate_for_active": missing_candidate_for_active,
        "activated_tasks_covered": activated_tasks_covered,
        "first_plant_turn": {
            "control_n_games_ever_planted": len(control_first_plant_turns),
            "control_median": control_median_first_plant,
            "control_mean": mean(control_first_plant_turns) if control_first_plant_turns else None,
            "control_reference_b44_b45": FIRST_PLANT_TURN_CONTROL_REFERENCE,
            "candidate_n_games_ever_planted": len(candidate_first_plant_turns),
            "candidate_median": candidate_median_first_plant,
            "candidate_mean": (
                mean(candidate_first_plant_turns) if candidate_first_plant_turns else None
            ),
            "gate_max_median": FIRST_PLANT_TURN_MAX,
            "pass": gate_first_plant,
        },
        "own_reap_rate": {
            "control_generations": control_generations,
            "control_ever_harvested": control_harvested,
            "control_rate_pct": control_reap_rate_pct,
            "control_reference_b44": OWN_REAP_RATE_CONTROL_REFERENCE_PCT,
            "candidate_generations": candidate_generations,
            "candidate_ever_harvested": candidate_harvested,
            "candidate_rate_pct": candidate_reap_rate_pct,
            "gate_min_pct": OWN_REAP_RATE_MIN_PCT,
            "pass": gate_reap,
        },
        "peak_concurrent_own_crops": {
            "control_mean": mean(control_peaks),
            "control_median": median_or_none(control_peaks),
            "control_max": max(control_peaks) if control_peaks else None,
            "candidate_mean": candidate_mean_peak,
            "candidate_median": candidate_median_peak,
            "candidate_max": max(candidate_peaks) if candidate_peaks else None,
            "peer_field_reference_b45": PEER_PEAK_CONCURRENCY_REFERENCE,
            "gate_max_mean": PEAK_CONCURRENT_OWN_CROPS_MAX,
            "pass": gate_peak,
        },
        "waste_sweep_detectors": detector_report,
        "gates": {
            "median_first_plant_turn_le_60": gate_first_plant,
            "own_reap_rate_ge_5pct": gate_reap,
            "peak_concurrent_own_crops_le_8": gate_peak,
            "no_detector_worsens_gt_10pct": gate_detectors,
        },
        "pass": gate_first_plant and gate_reap and gate_peak and gate_detectors,
    }


def verdict(integrity_result: dict, mechanism_result: dict, safety_result: dict, value_result: dict) -> dict:
    if not integrity_result["pass"]:
        return {"verdict": "BLOCKED", "reason": "integrity gate failure; mechanism/safety/value not authoritative"}
    if not mechanism_result["pass"]:
        return {"verdict": "CLOSED-AT-MECHANISM", "reason": "one or more mechanism gates failed"}
    if not safety_result["pass"]:
        return {
            "verdict": "CLOSED-AT-SAFETY",
            "reason": (
                "mechanism passed but the competitive-efficiency safety ratio "
                "(Delta-opponent <= 0.40x Delta-own) failed"
            ),
        }
    if not value_result["pass"]:
        return {"verdict": "CLOSED-AT-VALUE", "reason": "mechanism and safety passed but one or more value gates failed"}
    return {"verdict": "QUALIFIED", "reason": "all mechanism, safety, and value gates pass"}


def analyze(rows: list[dict], jobs1_bytes: bytes | None, jobs20_bytes: bytes | None, jobs: int) -> dict:
    integrity_result = integrity(rows, jobs1_bytes, jobs20_bytes)
    mechanism_result = mechanism(rows, jobs)
    value_result = value(rows)
    safety_result = safety(value_result.pop("_deltas"))
    verdict_result = verdict(integrity_result, mechanism_result, safety_result, value_result)
    return {
        "schema": "troll-farm-d175a-bounded-early-planting-panel-v1",
        "panel": {
            "path": str(PANEL_JOBS20.relative_to(ROOT)),
            "rows": len(rows),
            "seeds": "9856000-9856255",
            "families": list(OPPONENTS),
        },
        "integrity": integrity_result,
        "mechanism": mechanism_result,
        "safety": safety_result,
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
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({
        "integrity_pass": result["integrity"]["pass"],
        "mechanism_pass": result["mechanism"]["pass"],
        "safety_pass": result["safety"]["pass"],
        "value_pass": result["value"]["pass"],
        "verdict": result["verdict"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
