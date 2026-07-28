#!/usr/bin/env python3
"""Analyze D173b's harvest-before-chop fresh panel against its frozen gates.

See
`data/analysis/live-agent-6553250/d173b-harvest-before-chop-protocol-2026-07-28.md`.

Two input families, both produced by `rust/src/bin/d173b_harvest_before_chop_panel.rs`:

1. The paired outcome TSV (128 fresh maps x 8 opponent families x 2 seats = 2,048 tasks),
   at 1 and 20 threads, for the integrity (determinism, inactive-episode byte-exactness)
   and value gates (paired margin deltas) -- same statistical methodology as
   `analyze_d171a_oscillation_breaker.py` (map-clustered 95% CI).
2. Full per-turn trajectory NDJSON for both arms (CONTROL always; CANDIDATE only for
   tasks where a divergence occurred -- an inactive task is byte-identical to CONTROL by
   construction, so decoding it a second time would only reproduce CONTROL's own counts),
   bridged into `cgauto.waste_sweep.build_decoded_game` (the function's own docstring
   sanctions exactly this reuse: "used ... directly by unit tests with small synthetic
   maps/states/trajectories") so all six standing waste detectors run unmodified over both
   arms for the mechanism gate.

Because this fix (unlike D171a's oscillation breaker) is a stateless, freshly-recomputed-
every-turn candidate with no cross-turn memory, "activated" is exactly "own commands ever
diverge between control and candidate" -- if the trigger never fires, the two trajectories
are byte-identical for the whole game by induction (identical own commands -> identical
opponent inputs, since the opponent is deterministic in the current state -> identical next
state, every turn).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
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

from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_opening_analysis import assigned_unit_commands  # noqa: E402
from cgauto.waste_sweep import DETECTORS, DecodedGame, build_decoded_game  # noqa: E402

ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d173b-harvest-before-chop"
PANEL_JOBS20 = ARTIFACT_BASE / "d173b-jobs20-9854000-9854127.tsv"
PANEL_JOBS1 = ARTIFACT_BASE / "d173b-jobs1-9854000-9854127.tsv"
TRAJ_CONTROL = ARTIFACT_BASE / "d173b-trajectories-control-9854000-9854127.ndjson"
TRAJ_CANDIDATE = ARTIFACT_BASE / "d173b-trajectories-candidate-9854000-9854127.ndjson"
OUTPUT = ROOT / "data" / "analysis" / "live-agent-6553250" / "d173b-harvest-before-chop-result.json"

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
START_SEED = 9_854_000
MAP_COUNT = 128
INT_FIELDS = (
    "map_seed", "seat", "opponent_index",
    "control_done", "control_turn", "control_own_score", "control_opponent_score",
    "control_margin", "control_own_workers_final",
    "candidate_done", "candidate_turn", "candidate_own_score", "candidate_opponent_score",
    "candidate_margin", "candidate_own_workers_final",
    "activated",
)

# Mechanism gate: the subclass restriction from the frozen protocol -- an episode's
# dominant own worker was CHOPping the exact fruited cell for >= 50% of the episode's own
# turns (mirrors the B3.5 diagnosis's `chop_or_mine_shadows_harvest` sub-classification
# rule, "dominant verb CHOP/MINE, same-cell fraction >= 50%"), and the cell itself sits at
# shack (BFS door) distance <= 2 -- exactly the fix's own trigger bound, computed here from
# `DecodedGame.own_distance`, which is already the same BFS-from-own-doors table the fix's
# own Rust helper independently recomputes at runtime.
CHOP_SHADOW_VERB_FRACTION = 0.5
CHOP_SHADOW_SHACK_DISTANCE = 2


# ---------------------------------------------------------------------------
# TSV (value / integrity gates) -- same methodology as D171a
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


# ---------------------------------------------------------------------------
# NDJSON -> DecodedGame bridge
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


def is_chop_shadow_shack2(game: DecodedGame, episode: dict) -> bool:
    """Restrict a `harvest_slack` episode to the fix's own scoped sub-class: the cell
    sits at own-door BFS distance <= 2, and the dominant own worker was issuing `CHOP`
    from that exact cell for >= 50% of the episode's own turns (the B3.5 sub-
    classification rule, restricted to this fix's shack-distance bound)."""

    cell = tuple(episode["cell"])
    shack_distance = game.own_distance.get(cell)
    if shack_distance is None or shack_distance > CHOP_SHADOW_SHACK_DISTANCE:
        return False
    chop_turns = 0
    total_turns = 0
    for turn in range(episode["start_turn"], episode["end_turn"] + 1):
        if turn > game.turns:
            break
        before_units = {
            unit["id"]: unit for unit in game.states[turn - 1]["units"] if unit["player"] == game.me
        }
        commands = action_commands(game.trajectory[turn - 1].get(f"commands{game.me}"))
        assigned = assigned_unit_commands(commands, list(before_units.values()))
        total_turns += 1
        on_cell_chop = any(
            (unit["x"], unit["y"]) == cell
            and assigned.get(unit_id, "WAIT").split()[0].upper() == "CHOP"
            for unit_id, unit in before_units.items()
        )
        if on_cell_chop:
            chop_turns += 1
    return total_turns > 0 and (chop_turns / total_turns) >= CHOP_SHADOW_VERB_FRACTION


@dataclass
class GameDetectorCounts:
    harvest_slack_subclass: int
    harvest_slack_total: int
    other_totals: dict[str, int]
    other_turns: dict[str, int]


OTHER_DETECTORS = tuple(name for name in DETECTORS if name != "harvest_slack")


def count_one_game(record: dict) -> tuple[tuple[int, int, int], GameDetectorCounts]:
    game = decode_record(record)
    harvest_slack_episodes = DETECTORS["harvest_slack"](game)
    subclass = sum(1 for episode in harvest_slack_episodes if is_chop_shadow_shack2(game, episode))
    other_totals = {}
    other_turns = {}
    for name in OTHER_DETECTORS:
        episodes = DETECTORS[name](game)
        other_totals[name] = len(episodes)
        other_turns[name] = sum(episode["duration"] for episode in episodes)
    key = (record["seed"], record["seat"], record["opp"])
    return key, GameDetectorCounts(
        harvest_slack_subclass=subclass,
        harvest_slack_total=len(harvest_slack_episodes),
        other_totals=other_totals,
        other_turns=other_turns,
    )


def iter_ndjson(path: Path):
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def mechanism(rows: list[dict]) -> dict:
    control_counts: dict[tuple[int, int, int], GameDetectorCounts] = {}
    candidate_counts: dict[tuple[int, int, int], GameDetectorCounts] = {}

    for record in iter_ndjson(TRAJ_CONTROL):
        key, counts = count_one_game(record)
        control_counts[key] = counts
    for record in iter_ndjson(TRAJ_CANDIDATE):
        key, counts = count_one_game(record)
        candidate_counts[key] = counts

    missing_control = []
    missing_candidate_for_active = []
    control_subclass_total = 0
    candidate_subclass_total = 0
    control_harvest_slack_total = 0
    candidate_harvest_slack_total = 0
    control_other_totals: dict[str, int] = defaultdict(int)
    candidate_other_totals: dict[str, int] = defaultdict(int)
    control_other_turns: dict[str, int] = defaultdict(int)
    candidate_other_turns: dict[str, int] = defaultdict(int)
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

        control_subclass_total += control_side.harvest_slack_subclass
        candidate_subclass_total += candidate_side.harvest_slack_subclass
        control_harvest_slack_total += control_side.harvest_slack_total
        candidate_harvest_slack_total += candidate_side.harvest_slack_total
        for name in OTHER_DETECTORS:
            control_other_totals[name] += control_side.other_totals[name]
            candidate_other_totals[name] += candidate_side.other_totals[name]
            control_other_turns[name] += control_side.other_turns[name]
            candidate_other_turns[name] += candidate_side.other_turns[name]

    subclass_reduction = (
        (control_subclass_total - candidate_subclass_total) / control_subclass_total
        if control_subclass_total
        else None
    )
    gate_subclass = subclass_reduction is not None and subclass_reduction >= 0.70
    gate_total_not_increased = candidate_harvest_slack_total <= control_harvest_slack_total
    no_displacement = {
        name: candidate_other_totals[name] <= control_other_totals[name] for name in OTHER_DETECTORS
    }
    no_displacement_turns = {
        name: candidate_other_turns[name] <= control_other_turns[name] for name in OTHER_DETECTORS
    }
    gate_no_displacement = all(no_displacement.values())

    return {
        "tasks_covered": len(rows) - len(missing_control) - len(missing_candidate_for_active),
        "missing_control": missing_control,
        "missing_candidate_for_active": missing_candidate_for_active,
        "activated_tasks_covered": activated_tasks_covered,
        "harvest_slack": {
            "subclass_chop_shadow_shack2": {
                "control": control_subclass_total,
                "candidate": candidate_subclass_total,
                "reduction_fraction": subclass_reduction,
                "reduction_pct": subclass_reduction * 100 if subclass_reduction is not None else None,
            },
            "total_all_subclasses": {
                "control": control_harvest_slack_total,
                "candidate": candidate_harvest_slack_total,
                "not_increased": gate_total_not_increased,
            },
        },
        "other_five_detectors": {
            name: {
                "control_episodes": control_other_totals[name],
                "candidate_episodes": candidate_other_totals[name],
                "control_flagged_turns": control_other_turns[name],
                "candidate_flagged_turns": candidate_other_turns[name],
                "episodes_not_worsened": no_displacement[name],
                "flagged_turns_not_worsened": no_displacement_turns[name],
            }
            for name in OTHER_DETECTORS
        },
        "gates": {
            "subclass_reduced_ge_70pct": gate_subclass,
            "harvest_slack_total_not_increased": gate_total_not_increased,
            "other_five_no_displacement": gate_no_displacement,
        },
        "pass": gate_subclass and gate_total_not_increased and gate_no_displacement,
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


def analyze(rows: list[dict], jobs1_bytes: bytes | None, jobs20_bytes: bytes | None) -> dict:
    integrity_result = integrity(rows, jobs1_bytes, jobs20_bytes)
    mechanism_result = mechanism(rows)
    value_result = value(rows)
    verdict_result = verdict(integrity_result, mechanism_result, value_result)
    return {
        "schema": "troll-farm-d173b-harvest-before-chop-panel-v1",
        "panel": {
            "path": str(PANEL_JOBS20.relative_to(ROOT)),
            "rows": len(rows),
            "seeds": "9854000-9854127",
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
    args = parser.parse_args()

    rows = read_rows(PANEL_JOBS20)
    jobs1_bytes = PANEL_JOBS1.read_bytes() if PANEL_JOBS1.exists() else None
    jobs20_bytes = PANEL_JOBS20.read_bytes() if PANEL_JOBS20.exists() else None

    result = analyze(rows, jobs1_bytes, jobs20_bytes)
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
