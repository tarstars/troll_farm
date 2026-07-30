#!/usr/bin/env python3
"""M3: audit resident seat asymmetry with same-opponent matched controls."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import RESIDENT_AGENT_ID, is_clean  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
PROJECT = Path("/home/tarstars/prj/troll_farm")
DEFAULT_GAMES = PROJECT / "data/processed/games.jsonl"
DEFAULT_OUTPUT = REPO / "local_codex_1/m3-seat-asymmetry"
EXPECTED_GAMES_HASH = (
    "12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d"
)
EXPECTED_COUNTS = {
    "records": 9082,
    "clean_games": 9018,
    "resident_games": 241,
    "exact_opponents": 72,
    "seat_0_games": 126,
    "seat_1_games": 115,
}
EXPECTED_GAME_ID_RANGE = [891153730, 897326497]
PRIMARY_BAND = 1.0
SENSITIVITY_BANDS = (0.5, 1.5)
BOOTSTRAP_REPS = 20_000
NULL_REPS = 50_000
SEED = 20_260_730
MIN_SUPPORTED_TARGETS = 30
MIN_EXACT_IDENTITIES = 15
MIN_HALF_TARGETS = 15
MIN_RAW_PER_SEAT = 100


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("empty percentile input")
    position = (len(sorted_values) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def resident_row(game: dict) -> dict | None:
    players = game["players"]
    if int(players[0]["agentId"]) == RESIDENT_AGENT_ID:
        seat = 0
    elif int(players[1]["agentId"]) == RESIDENT_AGENT_ID:
        seat = 1
    else:
        return None
    resident = players[seat]
    opponent = players[1 - seat]
    margin = float(game["scores"][seat]) - float(game["scores"][1 - seat])
    win = 1.0 if margin > 0 else 0.5 if margin == 0 else 0.0
    mine = game["per_player"][str(seat)]
    theirs = game["per_player"][str(1 - seat)]
    return {
        "record_index": int(game["_m3_record_index"]),
        "game_id": int(game["gameId"]),
        "seat": seat,
        "resident_score": float(resident["arenaScore"]),
        "opponent_score": float(opponent["arenaScore"]),
        "opponent_id": int(opponent["agentId"]),
        "opponent_pseudo": str(opponent["name"]),
        "map_width": int(game["map"]["w"]),
        "map_height": int(game["map"]["h"]),
        "initial_trees": len(game["map"]["trees0"]),
        "margin": margin,
        "win": win,
        "resident_final_score": float(game["scores"][seat]),
        "opponent_final_score": float(game["scores"][1 - seat]),
        "resident_final_fruit": float(sum(mine["final_inv"][:4])),
        "resident_final_wood_points": float(4 * mine["final_inv"][5]),
        "opponent_final_fruit": float(sum(theirs["final_inv"][:4])),
        "opponent_final_wood_points": float(4 * theirs["final_inv"][5]),
        "turns": int(game["n_turns"]),
    }


def load_source(games_path: Path) -> tuple[list[dict], dict]:
    observed_hash = sha256_file(games_path)
    if observed_hash != EXPECTED_GAMES_HASH:
        raise ValueError(
            f"source hash mismatch: expected {EXPECTED_GAMES_HASH}, observed {observed_hash}"
        )
    games = []
    with games_path.open() as handle:
        for record_index, line in enumerate(handle, 1):
            game = json.loads(line)
            game["_m3_record_index"] = record_index
            games.append(game)
    clean = [game for game in games if is_clean(game)]
    rows = [row for game in clean if (row := resident_row(game)) is not None]
    counts = {
        "records": len(games),
        "clean_games": len(clean),
        "resident_games": len(rows),
        "exact_opponents": len({row["opponent_id"] for row in rows}),
        "seat_0_games": sum(row["seat"] == 0 for row in rows),
        "seat_1_games": sum(row["seat"] == 1 for row in rows),
    }
    checks = {
        key: counts[key] == expected for key, expected in EXPECTED_COUNTS.items()
    }
    if not all(checks.values()):
        raise ValueError(f"source count mismatch: {counts}")
    game_id_range = [min(game["gameId"] for game in games), max(game["gameId"] for game in games)]
    if game_id_range != EXPECTED_GAME_ID_RANGE:
        raise ValueError(f"game-id range mismatch: {game_id_range}")
    source = {
        "path": str(games_path),
        "expected_hash": EXPECTED_GAMES_HASH,
        "observed_hash": observed_hash,
        "hash_check": True,
        "counts": counts,
        "count_checks": checks,
        "game_id_range": game_id_range,
        "game_id_range_check": True,
    }
    return rows, source


def is_match(
    target: dict,
    control: dict,
    *,
    target_seat: int,
    identity_mode: str,
    opponent_score_band: float,
) -> bool:
    if identity_mode not in {"exact", "pseudo"}:
        raise ValueError(f"unknown identity mode: {identity_mode}")
    identity_matches = (
        control["opponent_id"] == target["opponent_id"]
        if identity_mode == "exact"
        else control["opponent_pseudo"] == target["opponent_pseudo"]
    )
    return (
        target["seat"] == target_seat
        and control["seat"] == 1 - target_seat
        and identity_matches
        and control["map_width"] == target["map_width"]
        and control["map_height"] == target["map_height"]
        and abs(control["opponent_score"] - target["opponent_score"])
        <= opponent_score_band
        and abs(control["resident_score"] - target["resident_score"]) <= 0.25
        and abs(control["initial_trees"] - target["initial_trees"]) <= 4
    )


def matched_targets(
    rows: list[dict],
    *,
    target_seat: int,
    identity_mode: str = "exact",
    opponent_score_band: float = PRIMARY_BAND,
) -> tuple[list[dict], list[dict]]:
    supported = []
    unsupported = []
    targets = sorted(
        (row for row in rows if row["seat"] == target_seat),
        key=lambda row: (row["game_id"], row["record_index"]),
    )
    for target in targets:
        controls = [
            control
            for control in rows
            if is_match(
                target,
                control,
                target_seat=target_seat,
                identity_mode=identity_mode,
                opponent_score_band=opponent_score_band,
            )
        ]
        controls.sort(key=lambda row: (row["game_id"], row["record_index"]))
        if not controls:
            unsupported.append(
                {
                    "game_id": target["game_id"],
                    "opponent_id": target["opponent_id"],
                    "opponent_pseudo": target["opponent_pseudo"],
                }
            )
            continue
        expected_margin = statistics.mean(control["margin"] for control in controls)
        expected_win = statistics.mean(control["win"] for control in controls)
        supported.append(
            {
                "game_id": target["game_id"],
                "record_index": target["record_index"],
                "target_seat": target_seat,
                "opponent_id": target["opponent_id"],
                "opponent_pseudo": target["opponent_pseudo"],
                "control_count": len(controls),
                "control_game_ids": [control["game_id"] for control in controls],
                "target_margin": target["margin"],
                "expected_margin": expected_margin,
                "margin_residual": target["margin"] - expected_margin,
                "target_win": target["win"],
                "expected_win": expected_win,
                "win_residual": target["win"] - expected_win,
            }
        )
    return supported, unsupported


def cluster_values(matched: list[dict], field: str) -> dict[int, list[float]]:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in matched:
        clusters[int(row["opponent_id"])].append(float(row[field]))
    return dict(sorted(clusters.items()))


def cluster_bootstrap_ci(
    matched: list[dict],
    *,
    field: str,
    reps: int,
    seed: int,
) -> tuple[float, float]:
    clusters = cluster_values(matched, field)
    if not clusters:
        raise ValueError("no clusters")
    keys = list(clusters)
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        sampled = [rng.choice(keys) for _index in keys]
        values = [value for key in sampled for value in clusters[key]]
        estimates.append(statistics.mean(values))
    estimates.sort()
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def cluster_sign_flip_p(
    matched: list[dict],
    *,
    field: str,
    reps: int,
    seed: int,
) -> float:
    clusters = cluster_values(matched, field)
    if not clusters:
        raise ValueError("no clusters")
    sums = [sum(values) for values in clusters.values()]
    total_n = sum(len(values) for values in clusters.values())
    observed = abs(sum(sums) / total_n)
    rng = random.Random(seed)
    exceedances = 0
    for _ in range(reps):
        estimate = abs(
            sum(value if rng.getrandbits(1) else -value for value in sums) / total_n
        )
        exceedances += estimate >= observed
    return (1 + exceedances) / (reps + 1)


def raw_summary(rows: list[dict]) -> dict:
    result = {}
    for seat in (0, 1):
        subset = [row for row in rows if row["seat"] == seat]
        result[str(seat)] = {
            "games": len(subset),
            "mean_margin": statistics.mean(row["margin"] for row in subset),
            "mean_win": statistics.mean(row["win"] for row in subset),
            "mean_resident_final_score": statistics.mean(
                row["resident_final_score"] for row in subset
            ),
            "mean_opponent_final_score": statistics.mean(
                row["opponent_final_score"] for row in subset
            ),
            "mean_resident_final_fruit": statistics.mean(
                row["resident_final_fruit"] for row in subset
            ),
            "mean_resident_final_wood_points": statistics.mean(
                row["resident_final_wood_points"] for row in subset
            ),
            "mean_turns": statistics.mean(row["turns"] for row in subset),
        }
    result["seat_1_minus_seat_0"] = {
        field: result["1"][field] - result["0"][field]
        for field in (
            "mean_margin",
            "mean_win",
            "mean_resident_final_score",
            "mean_opponent_final_score",
            "mean_resident_final_fruit",
            "mean_resident_final_wood_points",
            "mean_turns",
        )
    }
    return result


def fixed_effect_sensitivity(rows: list[dict]) -> dict:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["opponent_id"]].append(row)
    contrasts = []
    for opponent_id, subset in sorted(grouped.items()):
        seat_0 = [row for row in subset if row["seat"] == 0]
        seat_1 = [row for row in subset if row["seat"] == 1]
        if not seat_0 or not seat_1:
            continue
        contrasts.append(
            {
                "opponent_id": opponent_id,
                "pseudo": sorted({row["opponent_pseudo"] for row in subset})[0],
                "seat_0_games": len(seat_0),
                "seat_1_games": len(seat_1),
                "margin_difference": statistics.mean(row["margin"] for row in seat_1)
                - statistics.mean(row["margin"] for row in seat_0),
                "win_difference": statistics.mean(row["win"] for row in seat_1)
                - statistics.mean(row["win"] for row in seat_0),
            }
        )
    weights = [row["seat_0_games"] + row["seat_1_games"] for row in contrasts]
    return {
        "identities": len(contrasts),
        "identity_equal_margin_difference": statistics.mean(
            row["margin_difference"] for row in contrasts
        ),
        "identity_equal_win_difference": statistics.mean(
            row["win_difference"] for row in contrasts
        ),
        "game_weighted_margin_difference": sum(
            row["margin_difference"] * weight
            for row, weight in zip(contrasts, weights)
        )
        / sum(weights),
        "game_weighted_win_difference": sum(
            row["win_difference"] * weight
            for row, weight in zip(contrasts, weights)
        )
        / sum(weights),
        "contrasts": contrasts,
    }


def same_sign(value: float | None, reference: float) -> bool:
    if value is None or value == 0 or reference == 0:
        return False
    return (value > 0) == (reference > 0)


def leave_one_cluster_out(matched: list[dict]) -> list[dict]:
    rows = []
    for opponent_id in sorted({row["opponent_id"] for row in matched}):
        kept = [row for row in matched if row["opponent_id"] != opponent_id]
        rows.append(
            {
                "omitted_opponent_id": opponent_id,
                "targets_remaining": len(kept),
                "margin_difference": statistics.mean(
                    row["margin_residual"] for row in kept
                ),
                "win_difference": statistics.mean(row["win_residual"] for row in kept),
            }
        )
    return rows


def build_result(
    rows: list[dict],
    source: dict,
    *,
    bootstrap_reps: int,
    null_reps: int,
    seed: int,
) -> dict:
    primary_rows, primary_unsupported = matched_targets(
        rows,
        target_seat=1,
        identity_mode="exact",
        opponent_score_band=PRIMARY_BAND,
    )
    reverse_rows, reverse_unsupported = matched_targets(
        rows,
        target_seat=0,
        identity_mode="exact",
        opponent_score_band=PRIMARY_BAND,
    )
    pseudo_rows, pseudo_unsupported = matched_targets(
        rows,
        target_seat=1,
        identity_mode="pseudo",
        opponent_score_band=PRIMARY_BAND,
    )
    band_rows = {
        str(band): matched_targets(
            rows,
            target_seat=1,
            identity_mode="exact",
            opponent_score_band=band,
        )[0]
        for band in SENSITIVITY_BANDS
    }
    ordered = sorted(
        primary_rows, key=lambda row: (row["game_id"], row["record_index"])
    )
    midpoint = len(ordered) // 2
    halves = {"early": ordered[:midpoint], "late": ordered[midpoint:]}
    primary_margin = statistics.mean(row["margin_residual"] for row in primary_rows)
    primary_win = statistics.mean(row["win_residual"] for row in primary_rows)
    ci = cluster_bootstrap_ci(
        primary_rows,
        field="margin_residual",
        reps=bootstrap_reps,
        seed=seed,
    )
    null_p = cluster_sign_flip_p(
        primary_rows,
        field="margin_residual",
        reps=null_reps,
        seed=seed + 1,
    )
    reverse_margin = -statistics.mean(
        row["margin_residual"] for row in reverse_rows
    )
    reverse_win = -statistics.mean(row["win_residual"] for row in reverse_rows)
    pseudo_margin = statistics.mean(row["margin_residual"] for row in pseudo_rows)
    pseudo_win = statistics.mean(row["win_residual"] for row in pseudo_rows)
    band_summaries = {
        band: {
            "targets": len(subset),
            "identities": len({row["opponent_id"] for row in subset}),
            "margin_difference": statistics.mean(
                row["margin_residual"] for row in subset
            ),
            "win_difference": statistics.mean(row["win_residual"] for row in subset),
        }
        for band, subset in band_rows.items()
    }
    half_summaries = {
        label: {
            "targets": len(subset),
            "identities": len({row["opponent_id"] for row in subset}),
            "margin_difference": statistics.mean(
                row["margin_residual"] for row in subset
            ),
            "win_difference": statistics.mean(row["win_residual"] for row in subset),
        }
        for label, subset in halves.items()
    }
    leave_one_out = leave_one_cluster_out(primary_rows)
    raw = raw_summary(rows)
    support_gates = {
        "at_least_30_supported_targets": len(primary_rows) >= MIN_SUPPORTED_TARGETS,
        "at_least_15_exact_identities": len(
            {row["opponent_id"] for row in primary_rows}
        )
        >= MIN_EXACT_IDENTITIES,
        "at_least_15_targets_each_half": all(
            len(subset) >= MIN_HALF_TARGETS for subset in halves.values()
        ),
        "at_least_100_raw_games_each_seat": all(
            sum(row["seat"] == seat for row in rows) >= MIN_RAW_PER_SEAT
            for seat in (0, 1)
        ),
    }
    support = all(support_gates.values())
    actionability_gates = {
        "primary_support": support,
        "absolute_margin_difference_at_least_20": abs(primary_margin) >= 20,
        "ci_excludes_zero": ci[0] > 0 or ci[1] < 0,
        "two_sided_p_at_most_0_05": null_p <= 0.05,
        "win_difference_same_sign_and_at_least_0_10": same_sign(
            primary_win, primary_margin
        )
        and abs(primary_win) >= 0.10,
        "reverse_orientation_same_sign": same_sign(reverse_margin, primary_margin),
        "pseudo_lineage_same_sign": same_sign(pseudo_margin, primary_margin),
        "both_score_bands_same_sign": all(
            same_sign(summary["margin_difference"], primary_margin)
            for summary in band_summaries.values()
        ),
        "both_time_halves_same_sign": all(
            same_sign(summary["margin_difference"], primary_margin)
            for summary in half_summaries.values()
        ),
        "leave_one_exact_opponent_out_same_sign": all(
            same_sign(row["margin_difference"], primary_margin)
            for row in leave_one_out
        ),
    }
    actionable = all(actionability_gates.values())
    verdict = (
        "UNIDENTIFIABLE"
        if not support
        else "ACTIONABLE_SEAT_ASYMMETRY"
        if actionable
        else "NO_ACTIONABLE_SEAT_ASYMMETRY"
    )
    direction = "SEAT_1_WORSE" if primary_margin < 0 else "SEAT_0_WORSE"
    return {
        "verdict": verdict,
        "direction": direction,
        "actionable": actionable,
        "source": source,
        "protocol": {
            "primary_orientation": "seat_1_minus_seat_0",
            "identity_mode": "exact_agent_id",
            "opponent_score_band": PRIMARY_BAND,
            "resident_score_band": 0.25,
            "initial_tree_band": 4,
            "bootstrap_reps": bootstrap_reps,
            "null_reps": null_reps,
            "seed": seed,
        },
        "raw": raw,
        "primary": {
            "supported_targets": len(primary_rows),
            "unsupported_targets": len(primary_unsupported),
            "exact_identities": len({row["opponent_id"] for row in primary_rows}),
            "control_count_min": min(row["control_count"] for row in primary_rows),
            "control_count_median": statistics.median(
                row["control_count"] for row in primary_rows
            ),
            "control_count_max": max(row["control_count"] for row in primary_rows),
            "margin_difference": primary_margin,
            "margin_ci95": list(ci),
            "two_sided_randomization_p": null_p,
            "win_difference": primary_win,
            "targets": primary_rows,
            "unsupported": primary_unsupported,
        },
        "sensitivities": {
            "reverse_orientation": {
                "supported_targets": len(reverse_rows),
                "unsupported_targets": len(reverse_unsupported),
                "exact_identities": len(
                    {row["opponent_id"] for row in reverse_rows}
                ),
                "margin_difference": reverse_margin,
                "win_difference": reverse_win,
            },
            "pseudo_lineage": {
                "supported_targets": len(pseudo_rows),
                "unsupported_targets": len(pseudo_unsupported),
                "pseudos": len({row["opponent_pseudo"] for row in pseudo_rows}),
                "margin_difference": pseudo_margin,
                "win_difference": pseudo_win,
            },
            "opponent_score_bands": band_summaries,
            "chronological_halves": half_summaries,
            "fixed_effect": fixed_effect_sensitivity(rows),
        },
        "support_gates": support_gates,
        "actionability_gates": actionability_gates,
        "failed_actionability_gates": [
            key for key, passed in actionability_gates.items() if not passed
        ],
        "leave_one_exact_opponent_out": leave_one_out,
    }


def cluster_table(result: dict) -> list[dict]:
    targets = result["primary"]["targets"]
    leave_one = {
        row["omitted_opponent_id"]: row
        for row in result["leave_one_exact_opponent_out"]
    }
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in targets:
        grouped[row["opponent_id"]].append(row)
    table = []
    for opponent_id, subset in sorted(grouped.items()):
        table.append(
            {
                "opponent_id": opponent_id,
                "pseudo": sorted({row["opponent_pseudo"] for row in subset})[0],
                "supported_seat_1_targets": len(subset),
                "control_count_min": min(row["control_count"] for row in subset),
                "control_count_max": max(row["control_count"] for row in subset),
                "mean_margin_residual": statistics.mean(
                    row["margin_residual"] for row in subset
                ),
                "mean_win_residual": statistics.mean(
                    row["win_residual"] for row in subset
                ),
                "leave_one_out_margin": leave_one[opponent_id]["margin_difference"],
            }
        )
    return table


def report_text(result: dict) -> str:
    primary = result["primary"]
    raw = result["raw"]["seat_1_minus_seat_0"]
    sensitivities = result["sensitivities"]
    gates = result["actionability_gates"]
    failed = ", ".join(key for key, passed in gates.items() if not passed) or "none"
    return f"""# M3 — resident seat asymmetry

- Verdict: **{result['verdict']}**
- Direction of primary point estimate: **{result['direction']}**
- Raw seat-1 minus seat-0 margin: {raw['mean_margin']:.3f}
- Matched seat-1 minus seat-0 margin: {primary['margin_difference']:.3f}
- Cluster-bootstrap 95% CI: [{primary['margin_ci95'][0]:.3f}, {primary['margin_ci95'][1]:.3f}]
- Two-sided matched randomization p: {primary['two_sided_randomization_p']:.6f}
- Matched win difference: {primary['win_difference']:.3f}
- Support: {primary['supported_targets']} seat-1 targets / {primary['exact_identities']} exact identities

## Frozen sensitivities

- Reverse orientation: {sensitivities['reverse_orientation']['margin_difference']:.3f}
- Same-pseudo lineage: {sensitivities['pseudo_lineage']['margin_difference']:.3f}
- Score band ±0.5: {sensitivities['opponent_score_bands']['0.5']['margin_difference']:.3f}
- Score band ±1.5: {sensitivities['opponent_score_bands']['1.5']['margin_difference']:.3f}
- Early / late: {sensitivities['chronological_halves']['early']['margin_difference']:.3f} / {sensitivities['chronological_halves']['late']['margin_difference']:.3f}
- Exact-identity fixed-effect, identity equal: {sensitivities['fixed_effect']['identity_equal_margin_difference']:.3f}

## Failed actionability gates

{failed}

An actionable result could open only a read-only replay/mechanism audit. This result does
not authorize a seat branch, resident change, simulation, or Arena action.
"""


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.json").write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n"
    )
    (output_dir / "report.md").write_text(report_text(result))
    table = cluster_table(result)
    fields = [
        "opponent_id",
        "pseudo",
        "supported_seat_1_targets",
        "control_count_min",
        "control_count_max",
        "mean_margin_residual",
        "mean_win_residual",
        "leave_one_out_margin",
    ]
    with (output_dir / "clusters.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)


def synthetic_rows() -> list[dict]:
    rows = []
    game_id = 1
    for opponent_id, pseudo, offset in (
        (10, "alpha", 0.0),
        (11, "beta", 5.0),
        (12, "gamma", -5.0),
    ):
        for seat, margins in ((0, [10.0, 20.0]), (1, [-20.0, -10.0])):
            for margin in margins:
                rows.append(
                    {
                        "record_index": game_id,
                        "game_id": game_id,
                        "seat": seat,
                        "resident_score": 22.0,
                        "opponent_score": 23.0,
                        "opponent_id": opponent_id,
                        "opponent_pseudo": pseudo,
                        "map_width": 12,
                        "map_height": 12,
                        "initial_trees": 20,
                        "margin": margin + offset,
                        "win": 1.0 if margin + offset > 0 else 0.0,
                        "resident_final_score": 100.0,
                        "opponent_final_score": 100.0 - margin - offset,
                        "resident_final_fruit": 10.0,
                        "resident_final_wood_points": 80.0,
                        "opponent_final_fruit": 10.0,
                        "opponent_final_wood_points": 80.0,
                        "turns": 200,
                    }
                )
                game_id += 1
    return rows


def self_test() -> None:
    rows = synthetic_rows()
    supported, unsupported = matched_targets(rows, target_seat=1)
    assert len(supported) == 6 and not unsupported
    assert statistics.mean(row["margin_residual"] for row in supported) == -30.0
    reverse, _ = matched_targets(rows, target_seat=0)
    reverse_oriented = -statistics.mean(row["margin_residual"] for row in reverse)
    assert reverse_oriented == -30.0
    changed = [dict(row) for row in rows]
    changed[-1]["map_width"] = 99
    supported_changed, unsupported_changed = matched_targets(changed, target_seat=1)
    assert len(supported_changed) == 5 and len(unsupported_changed) == 1
    ci_one = cluster_bootstrap_ci(
        supported, field="margin_residual", reps=200, seed=7
    )
    ci_two = cluster_bootstrap_ci(
        supported, field="margin_residual", reps=200, seed=7
    )
    assert ci_one == ci_two == (-30.0, -30.0)
    p_one = cluster_sign_flip_p(
        supported, field="margin_residual", reps=200, seed=8
    )
    p_two = cluster_sign_flip_p(
        supported, field="margin_residual", reps=200, seed=8
    )
    assert p_one == p_two and 0 < p_one <= 1
    assert same_sign(-1.0, -2.0) and not same_sign(1.0, -2.0)
    print("self-test: ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    parser.add_argument("--null-reps", type=int, default=NULL_REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    rows, source = load_source(args.games)
    result = build_result(
        rows,
        source,
        bootstrap_reps=args.bootstrap_reps,
        null_reps=args.null_reps,
        seed=args.seed,
    )
    write_outputs(result, args.output_dir)
    print(
        f"{result['verdict']}: "
        f"margin={result['primary']['margin_difference']:.3f}, "
        f"targets={result['primary']['supported_targets']}, "
        f"identities={result['primary']['exact_identities']}"
    )
    return 2 if result["verdict"] == "UNIDENTIFIABLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
