#!/usr/bin/env python3
"""Validate and analyze the frozen D103a opponent-growth phase decomposition."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d103a-d40-opponent-growth-phase-decomposition-protocol-2026-07-22.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "d103_opponent_growth_phase_decomposition.rs"
D102 = BASE / "d102a-complete-macro-resident-transfer-a-jobs1-9824100-9824131.tsv"
D95 = BASE / "d95a-rank-one-concurrent-scaler-result-j1.json"
RAW_GAMES = ROOT / "data" / "raw" / "games"

START_SEED = 9_824_100
MAP_COUNT = 32
POLICIES = ("d40", "resident")
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

FROZEN_SHA256 = {
    PROTOCOL: "b9d308b1a2ea68450905edfbf03eece2c45e4644def3bb787607086b91559110",
    RUNNER: "fb3003fc2dde0f1932925d1b6cf25528371925461c46b655c8072a24c4e6dca0",
    D102: "0120c834a88ec178f923dd741a129bf13fdb5d842cad55f54ec765be793046f4",
}

STRING_FIELDS = {"opponent", "policy"}
CUMULATIVE_FIELDS = (
    "cumulative_successful_trains",
    "cumulative_completed_jobs",
    "cumulative_invalidated_jobs",
    "cumulative_invalid_direct_commands",
    "cumulative_provenance_failures",
    "cumulative_deposit_prediction_failures",
    "cumulative_own_created_crops",
    "cumulative_opponent_created_crops",
    "cumulative_joint_created_crops",
    "cumulative_ambiguous_created_crops",
    "cumulative_own_crop_harvest_units",
    "cumulative_own_reinvested_crops",
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


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def percentile_nearest(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[round(fraction * (len(ordered) - 1))]


def normal_interval_by_map(rows: list[dict], field: str) -> dict:
    by_map: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        by_map[row["map_seed"]].append(float(row[field]))
    map_means = [mean(values) for _, values in sorted(by_map.items())]
    center = mean(map_means)
    sd = statistics.stdev(map_means) if len(map_means) > 1 else 0.0
    radius = 1.96 * sd / math.sqrt(len(map_means)) if map_means else 0.0
    return {
        "maps": len(map_means),
        "mean": center,
        "lower": center - radius,
        "upper": center + radius,
        "map_mean_sd": sd,
    }


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in row:
            if field not in STRING_FIELDS:
                row[field] = int(row[field])
    return rows


def read_d102(path: Path) -> dict[tuple[int, int, str, str], dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    int_fields = {
        "map_seed",
        "seat",
        "done",
        "turn",
        "own_score",
        "opponent_score",
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
    }
    for row in rows:
        for field in int_fields:
            row[field] = int(row[field])
    return {
        (row["map_seed"], row["seat"], row["opponent"], row["policy"]): row
        for row in rows
    }


def episode_key(row: dict) -> tuple[int, int, str, str]:
    return row["map_seed"], row["seat"], row["opponent"], row["policy"]


def task_key(row: dict) -> tuple[int, int, str]:
    return row["map_seed"], row["seat"], row["opponent"]


def expected_episode_keys() -> set[tuple[int, int, str, str]]:
    return {
        (seed, seat, opponent, policy)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
        for policy in POLICIES
    }


def group_episodes(rows: list[dict]) -> dict[tuple[int, int, str, str], list[dict]]:
    grouped: dict[tuple[int, int, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[episode_key(row)].append(row)
    for episode in grouped.values():
        episode.sort(key=lambda row: row["interval_index"])
    return dict(grouped)


def continuity_errors(episodes: dict) -> dict:
    bad_indices = 0
    bad_turns = 0
    bad_state_links = 0
    bad_done = 0
    bad_stock = 0
    bad_cumulative = 0
    link_fields = (
        ("end_turn", "start_turn"),
        ("end_own_workers", "start_own_workers"),
        ("end_opponent_workers", "start_opponent_workers"),
        ("end_own_score", "start_own_score"),
        ("end_opponent_score", "start_opponent_score"),
        ("end_live_own_crops", "start_live_own_crops"),
        ("end_live_opponent_crops", "start_live_opponent_crops"),
        ("end_live_joint_crops", "start_live_joint_crops"),
        ("end_live_ambiguous_crops", "start_live_ambiguous_crops"),
    )
    for rows in episodes.values():
        if [row["interval_index"] for row in rows] != list(range(len(rows))):
            bad_indices += 1
        if any(row["end_turn"] <= row["start_turn"] for row in rows):
            bad_turns += 1
        if sum(row["done"] for row in rows) != 1 or rows[-1]["done"] != 1:
            bad_done += 1
        for left, right in zip(rows, rows[1:]):
            if any(left[end] != right[start] for end, start in link_fields):
                bad_state_links += 1
                break
        for row in rows:
            if (
                row["start_live_own_crops"] + row["own_crop_births"]
                != row["end_live_own_crops"] + row["own_crop_removals"]
                or row["start_live_opponent_crops"] + row["opponent_crop_births"]
                != row["end_live_opponent_crops"] + row["opponent_crop_removals"]
            ):
                bad_stock += 1
        for before, after in zip(rows, rows[1:]):
            if any(after[field] < before[field] for field in CUMULATIVE_FIELDS):
                bad_cumulative += 1
                break
    return {
        "bad_interval_indices": bad_indices,
        "bad_turn_progression": bad_turns,
        "bad_state_links": bad_state_links,
        "bad_terminal_markers": bad_done,
        "bad_crop_stock_flow_rows": bad_stock,
        "bad_cumulative_episodes": bad_cumulative,
    }


def d102_parity(episodes: dict, reference: dict) -> dict:
    mapping = {
        "done": "done",
        "end_turn": "turn",
        "end_own_score": "own_score",
        "end_opponent_score": "opponent_score",
        "end_own_workers": "own_workers",
        "end_opponent_workers": "opponent_workers",
        "cumulative_successful_trains": "successful_trains",
        "cumulative_completed_jobs": "completed_jobs",
        "cumulative_invalidated_jobs": "invalidated_jobs",
        "cumulative_invalid_direct_commands": "invalid_direct_commands",
        "cumulative_provenance_failures": "provenance_failures",
        "cumulative_deposit_prediction_failures": "deposit_prediction_failures",
        "cumulative_own_created_crops": "own_created_crops",
        "cumulative_opponent_created_crops": "opponent_created_crops",
        "cumulative_joint_created_crops": "joint_created_crops",
        "cumulative_ambiguous_created_crops": "ambiguous_created_crops",
        "cumulative_own_crop_harvest_units": "own_owned_crop_harvest_units",
        "cumulative_own_reinvested_crops": "own_reinvested_crops",
        "action_hash": "action_hash",
        "state_hash": "state_hash",
    }
    field_mismatches = defaultdict(int)
    missing = 0
    for key, rows in episodes.items():
        expected = reference.get(key)
        if expected is None:
            missing += 1
            continue
        final = rows[-1]
        for actual_field, expected_field in mapping.items():
            if final[actual_field] != expected[expected_field]:
                field_mismatches[actual_field] += 1
        if final["end_own_workers"] != expected["max_own_workers"]:
            field_mismatches["max_own_workers"] += 1
    return {
        "episodes": len(episodes),
        "missing_reference_episodes": missing,
        "field_mismatches": dict(sorted(field_mismatches.items())),
        "pass": missing == 0 and not field_mismatches and len(episodes) == len(reference),
    }


def endpoint(rows: list[dict], turn: int, mode: str = "nearest") -> dict:
    if mode == "earlier":
        eligible = [row for row in rows if row["end_turn"] <= turn]
        return eligible[-1] if eligible else rows[0]
    if mode == "later":
        eligible = [row for row in rows if row["end_turn"] >= turn]
        return eligible[0] if eligible else rows[-1]
    assert mode == "nearest"
    return min(rows, key=lambda row: (abs(row["end_turn"] - turn), row["end_turn"] > turn))


def decompose_task(d40: list[dict], resident: list[dict], common_mode: str) -> dict:
    d_terminal = d40[-1]
    r_terminal = resident[-1]
    common = endpoint(d40, r_terminal["end_turn"], common_mode)
    r_common = endpoint(resident, common["end_turn"], "nearest")
    scale = next((row for row in d40 if row["end_own_workers"] >= 3), None)
    scaled_in_common = scale is not None and scale["end_turn"] < common["end_turn"]

    def components(field: str) -> tuple[int, int, int, int]:
        if not scaled_in_common:
            pre = common[field] - r_common[field]
            post = 0
        else:
            assert scale is not None
            r_scale = endpoint(resident, scale["end_turn"], "nearest")
            pre = scale[field] - r_scale[field]
            post = (common[field] - scale[field]) - (r_common[field] - r_scale[field])
        # The nearest D40 common boundary can precede the resident terminal.
        # Include that signed resident tail in the terminal-duration component so
        # the frozen three-part decomposition remains exactly additive.
        boundary_alignment = r_common[field] - r_terminal[field]
        extension = d_terminal[field] - common[field] + boundary_alignment
        return pre, post, extension, boundary_alignment

    score = components("end_opponent_score")
    births = components("cumulative_opponent_created_crops")
    assert sum(score[:3]) == d_terminal["end_opponent_score"] - r_terminal["end_opponent_score"]
    assert sum(births[:3]) == (
        d_terminal["cumulative_opponent_created_crops"]
        - r_terminal["cumulative_opponent_created_crops"]
    )

    own_births_pre = common["cumulative_own_created_crops"]
    own_harvest_pre = common["cumulative_own_crop_harvest_units"]
    own_reinvest_pre = common["cumulative_own_reinvested_crops"]
    if scaled_in_common:
        assert scale is not None
        own_births_pre = scale["cumulative_own_created_crops"]
        own_harvest_pre = scale["cumulative_own_crop_harvest_units"]
        own_reinvest_pre = scale["cumulative_own_reinvested_crops"]

    return {
        "map_seed": d_terminal["map_seed"],
        "seat": d_terminal["seat"],
        "opponent": d_terminal["opponent"],
        "resident_terminal_turn": r_terminal["end_turn"],
        "d40_terminal_turn": d_terminal["end_turn"],
        "common_turn": common["end_turn"],
        "common_boundary_distance": abs(common["end_turn"] - r_terminal["end_turn"]),
        "scale_turn": scale["end_turn"] if scale is not None else None,
        "scaled": scale is not None,
        "scaled_in_common_horizon": scaled_in_common,
        "opponent_score_excess": sum(score[:3]),
        "pre_scale_opponent_score_excess": score[0],
        "post_scale_common_opponent_score_excess": score[1],
        "extension_opponent_score_excess": score[2],
        "opponent_score_common_boundary_alignment": score[3],
        "opponent_crop_birth_excess": sum(births[:3]),
        "pre_scale_opponent_crop_birth_excess": births[0],
        "post_scale_common_opponent_crop_birth_excess": births[1],
        "extension_opponent_crop_birth_excess": births[2],
        "opponent_crop_birth_common_boundary_alignment": births[3],
        "d40_common_live_opponent_crops": common["end_live_opponent_crops"],
        "d40_terminal_live_opponent_crops": d_terminal["end_live_opponent_crops"],
        "d40_pre_own_crop_births": own_births_pre,
        "d40_post_common_own_crop_births": common["cumulative_own_created_crops"] - own_births_pre,
        "d40_extension_own_crop_births": d_terminal["cumulative_own_created_crops"]
        - common["cumulative_own_created_crops"],
        "d40_pre_own_crop_harvest_units": own_harvest_pre,
        "d40_post_common_own_crop_harvest_units": common[
            "cumulative_own_crop_harvest_units"
        ]
        - own_harvest_pre,
        "d40_extension_own_crop_harvest_units": d_terminal[
            "cumulative_own_crop_harvest_units"
        ]
        - common["cumulative_own_crop_harvest_units"],
        "d40_pre_own_reinvested_crops": own_reinvest_pre,
        "d40_post_common_own_reinvested_crops": common[
            "cumulative_own_reinvested_crops"
        ]
        - own_reinvest_pre,
        "d40_extension_own_reinvested_crops": d_terminal[
            "cumulative_own_reinvested_crops"
        ]
        - common["cumulative_own_reinvested_crops"],
    }


def summarize_decomposition(rows: list[dict]) -> dict:
    component_fields = (
        "pre_scale_opponent_score_excess",
        "post_scale_common_opponent_score_excess",
        "extension_opponent_score_excess",
    )
    total = mean(row["opponent_score_excess"] for row in rows)
    component_means = {field: mean(row[field] for row in rows) for field in component_fields}
    component_shares = {
        field: ratio(value, total) for field, value in component_means.items()
    }
    eligible = [
        field
        for field in component_fields
        if component_means[field] >= 20.0
        and component_shares[field] is not None
        and component_shares[field] >= 0.50
    ]
    label = {
        "pre_scale_opponent_score_excess": "pre_scale",
        "post_scale_common_opponent_score_excess": "post_scale_common_horizon",
        "extension_opponent_score_excess": "extension",
    }
    return {
        "tasks": len(rows),
        "mean_opponent_score_excess": total,
        "component_means": component_means,
        "component_shares_of_total": component_shares,
        "component_map_clustered_intervals": {
            field: normal_interval_by_map(rows, field) for field in component_fields
        },
        "primary_boundary_from_value_only": label[eligible[0]] if eligible else "mixed",
        "mean_opponent_crop_birth_excess": mean(
            row["opponent_crop_birth_excess"] for row in rows
        ),
        "opponent_crop_birth_component_means": {
            phase: mean(row[field] for row in rows)
            for phase, field in {
                "pre_scale": "pre_scale_opponent_crop_birth_excess",
                "post_scale_common_horizon": "post_scale_common_opponent_crop_birth_excess",
                "extension": "extension_opponent_crop_birth_excess",
            }.items()
        },
        "common_boundary_alignment_means": {
            "opponent_score": mean(
                row["opponent_score_common_boundary_alignment"] for row in rows
            ),
            "opponent_crop_births": mean(
                row["opponent_crop_birth_common_boundary_alignment"] for row in rows
            ),
        },
        "scaled_rate": mean(row["scaled"] for row in rows),
        "scaled_in_common_horizon_rate": mean(
            row["scaled_in_common_horizon"] for row in rows
        ),
        "mean_scale_turn_scaled": mean(
            row["scale_turn"] for row in rows if row["scale_turn"] is not None
        ),
        "boundary_resolution": {
            "mean_absolute_turn_distance": mean(
                row["common_boundary_distance"] for row in rows
            ),
            "p95_absolute_turn_distance": percentile_nearest(
                (row["common_boundary_distance"] for row in rows), 0.95
            ),
            "maximum_absolute_turn_distance": max(
                row["common_boundary_distance"] for row in rows
            ),
        },
        "by_seat": {
            str(seat): {
                field: mean(row[field] for row in rows if row["seat"] == seat)
                for field in ("opponent_score_excess", *component_fields)
            }
            for seat in range(2)
        },
        "by_opponent": {
            opponent: {
                field: mean(row[field] for row in rows if row["opponent"] == opponent)
                for field in ("opponent_score_excess", *component_fields)
            }
            for opponent in OPPONENTS
        },
        "own_production_phase_means": {
            field: mean(row[field] for row in rows)
            for field in (
                "d40_pre_own_crop_births",
                "d40_post_common_own_crop_births",
                "d40_extension_own_crop_births",
                "d40_pre_own_crop_harvest_units",
                "d40_post_common_own_crop_harvest_units",
                "d40_extension_own_crop_harvest_units",
                "d40_pre_own_reinvested_crops",
                "d40_post_common_own_reinvested_crops",
                "d40_extension_own_reinvested_crops",
            )
        },
        "mean_live_opponent_crops": {
            "d40_common": mean(row["d40_common_live_opponent_crops"] for row in rows),
            "d40_terminal": mean(row["d40_terminal_live_opponent_crops"] for row in rows),
        },
    }


def removal_summary(episodes: dict) -> dict:
    totals = {
        "d40_pre_scale": [0, 0],
        "d40_post_scale": [0, 0],
        "resident": [0, 0],
    }
    for key, rows in episodes.items():
        policy = key[-1]
        for row in rows:
            if policy == "resident":
                group = "resident"
            elif row["start_own_workers"] < 3:
                group = "d40_pre_scale"
            else:
                group = "d40_post_scale"
            totals[group][0] += row["opponent_crop_births"]
            totals[group][1] += row["opponent_crop_removals"]
    return {
        group: {
            "opponent_crop_births": values[0],
            "opponent_crop_removals": values[1],
            "removal_per_birth": ratio(values[1], values[0]),
        }
        for group, values in totals.items()
    }


def message_preflight() -> dict:
    payload = json.loads(D95.read_text())
    game_ids = sorted(
        int(row["game_id"])
        for row in payload["rows"]
        if row["agent"] == "delineate"
    )
    pattern = re.compile(r"(?:^|[;\n])MSG(?: |$)", re.IGNORECASE)

    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)

    counts = {}
    for game_id in game_ids:
        raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        counts[str(game_id)] = sum(bool(pattern.search(value)) for value in strings(raw))
    return {
        "agent_id": 6_479_768,
        "agent": "delineate",
        "games": len(game_ids),
        "game_ids": game_ids,
        "message_counts": counts,
        "all_games_have_zero_msg_commands": len(game_ids) == 10
        and all(count == 0 for count in counts.values()),
    }


def analyze(rows_a: list[dict], rows_b: list[dict], repeat_identical: bool) -> dict:
    episodes_a = group_episodes(rows_a)
    episodes_b = group_episodes(rows_b)
    expected = expected_episode_keys()
    continuity_a = continuity_errors(episodes_a)
    continuity_b = continuity_errors(episodes_b)
    parity = d102_parity(episodes_a, read_d102(D102))
    source_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in FROZEN_SHA256}
    hashes_match = all(
        source_hashes[str(path.relative_to(ROOT))] == expected_hash
        for path, expected_hash in FROZEN_SHA256.items()
    )
    message = message_preflight()

    decompositions = {}
    for mode in ("nearest", "earlier", "later"):
        task_rows = []
        for seed in range(START_SEED, START_SEED + MAP_COUNT):
            for seat in range(2):
                for opponent in OPPONENTS:
                    task_rows.append(
                        decompose_task(
                            episodes_a[(seed, seat, opponent, "d40")],
                            episodes_a[(seed, seat, opponent, "resident")],
                            mode,
                        )
                    )
        decompositions[mode] = {
            "summary": summarize_decomposition(task_rows),
            "rows": task_rows,
        }

    resolution = decompositions["nearest"]["summary"]["boundary_resolution"]
    integrity_gates = {
        "run_a_exact_episode_grid": set(episodes_a) == expected,
        "run_b_exact_episode_grid": set(episodes_b) == expected,
        "one_and_twenty_worker_runs_byte_identical": repeat_identical,
        "run_a_interval_integrity": all(value == 0 for value in continuity_a.values()),
        "run_b_interval_integrity": all(value == 0 for value in continuity_b.values()),
        "final_rows_reproduce_d102": parity["pass"],
        "frozen_source_hashes_match": hashes_match,
        "zero_final_provenance_and_ambiguous_failures": all(
            rows[-1]["cumulative_provenance_failures"] == 0
            and rows[-1]["cumulative_ambiguous_created_crops"] == 0
            for rows in episodes_a.values()
        ),
        "d40_zero_invalid_commands_and_deposit_failures": all(
            rows[-1]["cumulative_invalid_direct_commands"] == 0
            and rows[-1]["cumulative_deposit_prediction_failures"] == 0
            for key, rows in episodes_a.items()
            if key[-1] == "d40"
        ),
        "d40_direct_api_parity_assertion_present": (
            "assert_eq!(terminal, direct_terminal" in RUNNER.read_text()
        ),
        "boundary_resolution_mean_at_most_5": resolution[
            "mean_absolute_turn_distance"
        ]
        <= 5.0,
        "boundary_resolution_p95_at_most_15": resolution[
            "p95_absolute_turn_distance"
        ]
        <= 15.0,
    }
    integrity_pass = all(integrity_gates.values())
    value_boundary = decompositions["nearest"]["summary"][
        "primary_boundary_from_value_only"
    ]
    primary_boundary = value_boundary if integrity_pass else "unresolved_integrity"
    decision = {
        "pre_scale": "learn_joint_establishment_bill_production_and_early_denial",
        "post_scale_common_horizon": "test_bounded_worker_three_opponent_lineage_allocator",
        "extension": "test_terminal_liquidation_and_stop_producing_controller",
        "mixed": "require_complete_closed_loop_opponent_aware_policy_improvement",
        "unresolved_integrity": "repair_measurement_only",
    }[primary_boundary]

    return {
        "protocol": "D103a D40 opponent-growth phase decomposition",
        "integrity_pass": integrity_pass,
        "primary_boundary": primary_boundary,
        "decision": decision,
        "integrity": {
            "run_a_rows": len(rows_a),
            "run_b_rows": len(rows_b),
            "run_a_episodes": len(episodes_a),
            "run_b_episodes": len(episodes_b),
            "repeat_byte_identical": repeat_identical,
            "run_a_continuity": continuity_a,
            "run_b_continuity": continuity_b,
            "d102_parity": parity,
            "source_hashes": source_hashes,
        },
        "integrity_gates": integrity_gates,
        "message_preflight": message,
        "decomposition": {
            mode: value["summary"] for mode, value in decompositions.items()
        },
        "task_rows": decompositions["nearest"]["rows"],
        "opponent_crop_removal": removal_summary(episodes_a),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-a",
        type=Path,
        default=BASE
        / "d103a-d40-opponent-growth-phase-decomposition-a-jobs1-9824100-9824131.tsv",
    )
    parser.add_argument(
        "--run-b",
        type=Path,
        default=BASE
        / "d103a-d40-opponent-growth-phase-decomposition-b-jobs20-9824100-9824131.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "d103a-d40-opponent-growth-phase-decomposition-result.json",
    )
    parser.add_argument("--jobs1-seconds", type=float, required=True)
    parser.add_argument("--jobs20-seconds", type=float, required=True)
    args = parser.parse_args()
    report = analyze(
        read_rows(args.run_a),
        read_rows(args.run_b),
        repeat_identical=sha256(args.run_a) == sha256(args.run_b),
    )
    report["provenance"] = {
        "run_a": {"path": str(args.run_a), "sha256": sha256(args.run_a)},
        "run_b": {"path": str(args.run_b), "sha256": sha256(args.run_b)},
        "protocol": {"path": str(PROTOCOL), "sha256": sha256(PROTOCOL)},
        "runner": {"path": str(RUNNER), "sha256": sha256(RUNNER)},
        "analyzer": {"path": str(Path(__file__)), "sha256": sha256(Path(__file__))},
        "execution_seconds": {
            "jobs_1": args.jobs1_seconds,
            "jobs_20": args.jobs20_seconds,
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    nearest = report["decomposition"]["nearest"]
    print(
        json.dumps(
            {
                "integrity_pass": report["integrity_pass"],
                "primary_boundary": report["primary_boundary"],
                "decision": report["decision"],
                "mean_opponent_score_excess": nearest["mean_opponent_score_excess"],
                "component_means": nearest["component_means"],
                "boundary_resolution": nearest["boundary_resolution"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
