#!/usr/bin/env python3
"""M2: audit exact-opponent loss anomalies using resident-only matched controls."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    is_clean,
    load_leaderboard,
)


REPO = Path(__file__).resolve().parent.parent
PROJECT = Path("/home/tarstars/prj/troll_farm")
DEFAULT_GAMES = PROJECT / "data/processed/games.jsonl"
DEFAULT_LEADERBOARD = (
    PROJECT / "data/raw/snapshots/20260730T021701Z-d61p-wide/leaderboard.json"
)
DEFAULT_OUTPUT = REPO / "local_codex_1/m2-opponent-specific-losses"
EXPECTED_GAMES_HASH = (
    "12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d"
)
EXPECTED_LEADERBOARD_HASH = (
    "7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815"
)
EXPECTED_COUNTS = {
    "records": 9082,
    "clean_games": 9018,
    "resident_games": 241,
    "exact_opponents": 72,
}
PRIMARY_BAND = 1.0
SENSITIVITY_BANDS = (0.5, 1.5)
MIN_GAMES = 5
MIN_PER_SEAT = 2
MIN_CONTROLS = 10
BOOTSTRAP_REPS = 20_000
NULL_REPS = 50_000
SEED = 20_260_730


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


def bootstrap_ci(
    values: list[float],
    reps: int,
    seed: int,
) -> tuple[float, float]:
    if not values:
        raise ValueError("empty bootstrap input")
    rng = random.Random(seed)
    estimates = []
    for _ in range(reps):
        estimates.append(
            statistics.mean(rng.choice(values) for _index in range(len(values)))
        )
    estimates.sort()
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def holm_adjust(raw: dict[int, float]) -> dict[int, float]:
    ordered = sorted(raw.items(), key=lambda item: (item[1], item[0]))
    adjusted = {}
    running = 0.0
    family = len(ordered)
    for index, (agent_id, value) in enumerate(ordered):
        candidate = min(1.0, value * (family - index))
        running = max(running, candidate)
        adjusted[agent_id] = running
    return adjusted


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
        "record_index": int(game["_m2_record_index"]),
        "game_id": int(game["gameId"]),
        "seat": seat,
        "resident_score": float(resident["arenaScore"]),
        "opponent_score": float(opponent["arenaScore"]),
        "opponent_id": int(opponent["agentId"]),
        "opponent_pseudo": opponent["name"],
        "map_width": int(game["map"]["w"]),
        "map_height": int(game["map"]["h"]),
        "initial_trees": len(game["map"]["trees0"]),
        "margin": margin,
        "win": win,
        "resident_final_score": float(game["scores"][seat]),
        "opponent_final_score": float(game["scores"][1 - seat]),
        "resident_final_fruit": sum(mine["final_inv"][:4]),
        "resident_final_wood_points": 4 * mine["final_inv"][5],
        "opponent_final_fruit": sum(theirs["final_inv"][:4]),
        "opponent_final_wood_points": 4 * theirs["final_inv"][5],
    }


def load_sources(games_path: Path, leaderboard_path: Path) -> tuple[list[dict], dict, dict]:
    observed_hashes = {
        "games": sha256_file(games_path),
        "leaderboard": sha256_file(leaderboard_path),
    }
    checks = {
        "games": observed_hashes["games"] == EXPECTED_GAMES_HASH,
        "leaderboard": observed_hashes["leaderboard"] == EXPECTED_LEADERBOARD_HASH,
    }
    if not all(checks.values()):
        raise ValueError(f"source hash mismatch: {checks}")
    games = []
    with games_path.open() as handle:
        for record_index, line in enumerate(handle, 1):
            game = json.loads(line)
            game["_m2_record_index"] = record_index
            games.append(game)
    clean = [game for game in games if is_clean(game)]
    resident = [row for game in clean if (row := resident_row(game)) is not None]
    leaderboard = load_leaderboard(leaderboard_path)
    counts = {
        "records": len(games),
        "clean_games": len(clean),
        "resident_games": len(resident),
        "exact_opponents": len({row["opponent_id"] for row in resident}),
    }
    count_checks = {
        key: counts[key] == expected for key, expected in EXPECTED_COUNTS.items()
    }
    if not all(count_checks.values()):
        raise ValueError(f"source count mismatch: {counts}")
    source = {
        "paths": {"games": str(games_path), "leaderboard": str(leaderboard_path)},
        "expected_hashes": {
            "games": EXPECTED_GAMES_HASH,
            "leaderboard": EXPECTED_LEADERBOARD_HASH,
        },
        "observed_hashes": observed_hashes,
        "hash_checks": checks,
        "counts": counts,
        "count_checks": count_checks,
    }
    return resident, leaderboard, source


def is_match(
    target: dict,
    control: dict,
    target_ids: set[int],
    target_pseudos: set[str],
    opponent_score_band: float,
) -> bool:
    return (
        control["opponent_id"] not in target_ids
        and control["opponent_pseudo"] not in target_pseudos
        and control["seat"] == target["seat"]
        and control["map_width"] == target["map_width"]
        and control["map_height"] == target["map_height"]
        and abs(control["opponent_score"] - target["opponent_score"])
        <= opponent_score_band
        and abs(control["resident_score"] - target["resident_score"]) <= 0.25
        and abs(control["initial_trees"] - target["initial_trees"]) <= 4
    )


def make_control_pools(
    target_rows: list[dict],
    all_rows: list[dict],
    opponent_score_band: float,
) -> list[list[dict]]:
    target_ids = {row["opponent_id"] for row in target_rows}
    target_pseudos = {row["opponent_pseudo"] for row in target_rows}
    return [
        [
            control
            for control in all_rows
            if is_match(
                target,
                control,
                target_ids,
                target_pseudos,
                opponent_score_band,
            )
        ]
        for target in target_rows
    ]


def residual_vectors(
    target_rows: list[dict],
    pools: list[list[dict]],
) -> tuple[list[float], list[float]]:
    margin = [
        target["margin"] - statistics.mean(control["margin"] for control in pool)
        for target, pool in zip(target_rows, pools)
    ]
    wins = [
        target["win"] - statistics.mean(control["win"] for control in pool)
        for target, pool in zip(target_rows, pools)
    ]
    return margin, wins


def matched_null_p(
    observed: float,
    pools: list[list[dict]],
    reps: int,
    seed: int,
) -> float:
    rng = random.Random(seed)
    expected = [statistics.mean(row["margin"] for row in pool) for pool in pools]
    at_or_below = 0
    for _ in range(reps):
        null_value = statistics.mean(
            rng.choice(pool)["margin"] - center
            for pool, center in zip(pools, expected)
        )
        at_or_below += null_value <= observed
    return (1 + at_or_below) / (reps + 1)


def split_means(
    target_rows: list[dict],
    residuals: list[float],
) -> dict:
    by_seat = {}
    for seat in (0, 1):
        values = [
            residual
            for row, residual in zip(target_rows, residuals)
            if row["seat"] == seat
        ]
        by_seat[str(seat)] = {
            "n": len(values),
            "mean_margin_residual": statistics.mean(values) if values else None,
        }
    ordered = sorted(
        zip(target_rows, residuals),
        key=lambda item: (item[0]["game_id"], item[0]["record_index"]),
    )
    midpoint = len(ordered) // 2
    halves = {"early": ordered[:midpoint], "late": ordered[midpoint:]}
    chronological = {
        name: {
            "n": len(rows),
            "mean_margin_residual": (
                statistics.mean(residual for _row, residual in rows) if rows else None
            ),
        }
        for name, rows in halves.items()
    }
    return {"seat": by_seat, "chronological": chronological}


def sensitivity(
    target_rows: list[dict],
    all_rows: list[dict],
    band: float,
) -> dict:
    pools = make_control_pools(target_rows, all_rows, band)
    counts = [len(pool) for pool in pools]
    identified = bool(counts) and min(counts) >= MIN_CONTROLS
    result = {
        "opponent_score_band": band,
        "identified": identified,
        "control_count_min": min(counts) if counts else None,
        "control_count_median": statistics.median(counts) if counts else None,
        "control_count_max": max(counts) if counts else None,
    }
    if identified:
        margins, wins = residual_vectors(target_rows, pools)
        result.update(
            {
                "mean_margin_residual": statistics.mean(margins),
                "mean_win_residual": statistics.mean(wins),
            }
        )
    return result


def summarize_raw(rows: list[dict]) -> dict:
    return {
        "games": len(rows),
        "seat_counts": dict(sorted(Counter(row["seat"] for row in rows).items())),
        "wins": sum(row["win"] == 1 for row in rows),
        "ties": sum(row["win"] == 0.5 for row in rows),
        "win_rate_with_half_ties": statistics.mean(row["win"] for row in rows),
        "mean_margin": statistics.mean(row["margin"] for row in rows),
        "mean_resident_score": statistics.mean(row["resident_score"] for row in rows),
        "mean_opponent_score": statistics.mean(row["opponent_score"] for row in rows),
        "first_game_id": min(row["game_id"] for row in rows),
        "last_game_id": max(row["game_id"] for row in rows),
    }


def basic_gates(
    rows: list[dict],
    agent_id: int,
    leaderboard: dict[int, dict],
) -> dict:
    seats = Counter(row["seat"] for row in rows)
    complete = all(
        row[field] is not None
        for row in rows
        for field in (
            "resident_score",
            "opponent_score",
            "map_width",
            "map_height",
            "initial_trees",
        )
    )
    return {
        "at_least_five_games": len(rows) >= MIN_GAMES,
        "at_least_two_each_seat": seats[0] >= MIN_PER_SEAT
        and seats[1] >= MIN_PER_SEAT,
        "active_exact_agent": agent_id in leaderboard,
        "complete_matching_fields": complete,
    }


def evaluate_exact_opponents(
    resident_rows: list[dict],
    leaderboard: dict[int, dict],
    bootstrap_reps: int,
    null_reps: int,
    seed: int,
) -> list[dict]:
    by_opponent: dict[int, list[dict]] = defaultdict(list)
    for row in resident_rows:
        by_opponent[row["opponent_id"]].append(row)
    results = []
    raw_p = {}
    for agent_id, rows in sorted(by_opponent.items()):
        rows.sort(key=lambda row: (row["game_id"], row["record_index"]))
        pseudo = Counter(row["opponent_pseudo"] for row in rows).most_common(1)[0][0]
        gates = basic_gates(rows, agent_id, leaderboard)
        result = {
            "agent_id": agent_id,
            "pseudo": pseudo,
            "current": (
                {
                    "rank": leaderboard[agent_id]["rank"],
                    "score": leaderboard[agent_id]["score"],
                }
                if agent_id in leaderboard
                else None
            ),
            "raw": summarize_raw(rows),
            "eligibility_gates": gates,
            "eligible_before_controls": all(gates.values()),
        }
        if result["eligible_before_controls"]:
            pools = make_control_pools(rows, resident_rows, PRIMARY_BAND)
            counts = [len(pool) for pool in pools]
            control_gate = min(counts) >= MIN_CONTROLS
            gates["at_least_ten_controls_each_game"] = control_gate
            result["primary_control_counts"] = {
                "min": min(counts),
                "median": statistics.median(counts),
                "max": max(counts),
                "per_game": counts,
            }
            if control_gate:
                margin_residuals, win_residuals = residual_vectors(rows, pools)
                ci_low, ci_high = bootstrap_ci(
                    margin_residuals, bootstrap_reps, seed + agent_id
                )
                p_value = matched_null_p(
                    statistics.mean(margin_residuals),
                    pools,
                    null_reps,
                    seed + 1_000_000 + agent_id,
                )
                raw_p[agent_id] = p_value
                split = split_means(rows, margin_residuals)
                leave_one_out = [
                    statistics.mean(
                        value
                        for other_index, value in enumerate(margin_residuals)
                        if other_index != index
                    )
                    for index in range(len(margin_residuals))
                ]
                result["primary"] = {
                    "mean_margin_residual": statistics.mean(margin_residuals),
                    "margin_residual_ci95": [ci_low, ci_high],
                    "mean_win_residual": statistics.mean(win_residuals),
                    "raw_one_sided_p": p_value,
                    "per_game_margin_residuals": margin_residuals,
                    "per_game_win_residuals": win_residuals,
                    "splits": split,
                    "leave_one_game_out": {
                        "min": min(leave_one_out),
                        "max": max(leave_one_out),
                        "all_negative": all(value < 0 for value in leave_one_out),
                    },
                    "sensitivities": {
                        str(band): sensitivity(rows, resident_rows, band)
                        for band in SENSITIVITY_BANDS
                    },
                }
        gates.setdefault("at_least_ten_controls_each_game", False)
        result["primary_eligible"] = all(gates.values())
        results.append(result)

    adjusted = holm_adjust(raw_p)
    for result in results:
        primary = result.get("primary")
        if primary is None:
            result["actionability_gates"] = {
                "primary_eligible": False,
                "margin_residual_at_most_minus_20": False,
                "ci_upper_below_zero": False,
                "holm_p_at_most_0_05": False,
                "win_residual_at_most_minus_0_15": False,
                "both_seats_negative": False,
                "both_time_halves_negative": False,
                "both_band_sensitivities_identified_negative": False,
                "leave_one_out_all_negative": False,
                "active_exact_agent": result["eligibility_gates"]["active_exact_agent"],
            }
            result["actionable"] = False
            continue
        agent_id = result["agent_id"]
        primary["holm_adjusted_p"] = adjusted[agent_id]
        seats = primary["splits"]["seat"]
        halves = primary["splits"]["chronological"]
        sensitivity_rows = list(primary["sensitivities"].values())
        actionability = {
            "primary_eligible": result["primary_eligible"],
            "margin_residual_at_most_minus_20": primary["mean_margin_residual"]
            <= -20,
            "ci_upper_below_zero": primary["margin_residual_ci95"][1] < 0,
            "holm_p_at_most_0_05": primary["holm_adjusted_p"] <= 0.05,
            "win_residual_at_most_minus_0_15": primary["mean_win_residual"]
            <= -0.15,
            "both_seats_negative": all(
                row["n"] >= MIN_PER_SEAT
                and row["mean_margin_residual"] is not None
                and row["mean_margin_residual"] < 0
                for row in seats.values()
            ),
            "both_time_halves_negative": all(
                row["n"] >= MIN_PER_SEAT
                and row["mean_margin_residual"] is not None
                and row["mean_margin_residual"] < 0
                for row in halves.values()
            ),
            "both_band_sensitivities_identified_negative": all(
                row["identified"] and row["mean_margin_residual"] < 0
                for row in sensitivity_rows
            ),
            "leave_one_out_all_negative": primary["leave_one_game_out"][
                "all_negative"
            ],
            "active_exact_agent": result["eligibility_gates"]["active_exact_agent"],
        }
        result["actionability_gates"] = actionability
        result["actionable"] = all(actionability.values())
    return results


def pseudo_sensitivities(resident_rows: list[dict]) -> list[dict]:
    by_pseudo: dict[str, list[dict]] = defaultdict(list)
    for row in resident_rows:
        by_pseudo[row["opponent_pseudo"]].append(row)
    results = []
    for pseudo, rows in sorted(by_pseudo.items()):
        seats = Counter(row["seat"] for row in rows)
        if len(rows) < MIN_GAMES or min(seats[0], seats[1]) < MIN_PER_SEAT:
            continue
        pools = make_control_pools(rows, resident_rows, PRIMARY_BAND)
        counts = [len(pool) for pool in pools]
        identified = min(counts) >= MIN_CONTROLS
        result = {
            "pseudo": pseudo,
            "exact_agent_ids": sorted({row["opponent_id"] for row in rows}),
            "games": len(rows),
            "seat_counts": dict(sorted(seats.items())),
            "identified": identified,
            "control_count_min": min(counts),
        }
        if identified:
            margins, wins = residual_vectors(rows, pools)
            result["mean_margin_residual"] = statistics.mean(margins)
            result["mean_win_residual"] = statistics.mean(wins)
        results.append(result)
    return results


def overall_verdict(results: list[dict]) -> tuple[str, list[dict]]:
    actionable = sorted(
        [row for row in results if row["actionable"]],
        key=lambda row: (
            row["primary"]["holm_adjusted_p"],
            row["primary"]["mean_margin_residual"],
            row["agent_id"],
        ),
    )
    if actionable:
        return "ACTIONABLE_MATCHUP_ANOMALY", actionable
    if any(row["primary_eligible"] for row in results):
        return "NO_ACTIONABLE_MATCHUP", []
    return "UNIDENTIFIABLE", []


def write_csv(path: Path, results: list[dict]) -> None:
    fields = (
        "agent_id",
        "pseudo",
        "games",
        "seat0",
        "seat1",
        "active",
        "current_rank",
        "current_score",
        "primary_eligible",
        "control_min",
        "raw_mean_margin",
        "raw_win_rate",
        "mean_margin_residual",
        "ci_low",
        "ci_high",
        "mean_win_residual",
        "raw_p",
        "holm_p",
        "actionable",
        "failed_actionability_gates",
    )
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(results, key=lambda item: item["agent_id"]):
            primary = row.get("primary") or {}
            current = row.get("current") or {}
            ci = primary.get("margin_residual_ci95") or [None, None]
            writer.writerow(
                {
                    "agent_id": row["agent_id"],
                    "pseudo": row["pseudo"],
                    "games": row["raw"]["games"],
                    "seat0": row["raw"]["seat_counts"].get(0, 0),
                    "seat1": row["raw"]["seat_counts"].get(1, 0),
                    "active": row["eligibility_gates"]["active_exact_agent"],
                    "current_rank": current.get("rank"),
                    "current_score": current.get("score"),
                    "primary_eligible": row["primary_eligible"],
                    "control_min": (row.get("primary_control_counts") or {}).get(
                        "min"
                    ),
                    "raw_mean_margin": row["raw"]["mean_margin"],
                    "raw_win_rate": row["raw"]["win_rate_with_half_ties"],
                    "mean_margin_residual": primary.get("mean_margin_residual"),
                    "ci_low": ci[0],
                    "ci_high": ci[1],
                    "mean_win_residual": primary.get("mean_win_residual"),
                    "raw_p": primary.get("raw_one_sided_p"),
                    "holm_p": primary.get("holm_adjusted_p"),
                    "actionable": row["actionable"],
                    "failed_actionability_gates": ",".join(
                        key
                        for key, passed in row["actionability_gates"].items()
                        if not passed
                    ),
                }
            )


def render_report(result: dict) -> str:
    lines = [
        "# M2 — opponent-specific systematic losses",
        "",
        f"- Verdict: **{result['verdict']}**",
        f"- Resident games: {result['source']['counts']['resident_games']}",
        f"- Exact opponents: {result['source']['counts']['exact_opponents']}",
        f"- Primary-eligible opponents: {result['primary_eligible_count']}",
        f"- Actionable opponents: {len(result['actionable'])}",
        "",
        "## Primary-eligible exact opponents",
        "",
        "| agentId | pseudo | n | residual | 95% CI | win residual | Holm p | actionable |",
        "|---:|---|---:|---:|---|---:|---:|---|",
    ]
    for row in result["opponents"]:
        if not row["primary_eligible"]:
            continue
        primary = row["primary"]
        lines.append(
            f"| {row['agent_id']} | {row['pseudo']} | {row['raw']['games']} | "
            f"{primary['mean_margin_residual']:.3f} | "
            f"[{primary['margin_residual_ci95'][0]:.3f},"
            f"{primary['margin_residual_ci95'][1]:.3f}] | "
            f"{primary['mean_win_residual']:.3f} | "
            f"{primary['holm_adjusted_p']:.6f} | {row['actionable']} |"
        )
    lines.extend(
        [
            "",
            "## Decision boundary",
            "",
            (
                "Only an exact active identity passing all ten frozen actionability gates "
                "can open a replay-mechanism follow-up. No result here authorizes an "
                "opponent-name policy branch, resident change, simulation, or Arena action."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def self_test() -> None:
    target = {
        "opponent_id": 1,
        "opponent_pseudo": "target",
        "seat": 0,
        "map_width": 16,
        "map_height": 8,
        "opponent_score": 22.0,
        "resident_score": 21.5,
        "initial_trees": 20,
    }
    control = {
        "opponent_id": 2,
        "opponent_pseudo": "control",
        "seat": 0,
        "map_width": 16,
        "map_height": 8,
        "opponent_score": 22.5,
        "resident_score": 21.6,
        "initial_trees": 23,
    }
    assert is_match(target, control, {1}, {"target"}, 1.0)
    assert not is_match(target, {**control, "opponent_pseudo": "target"}, {1}, {"target"}, 1.0)
    assert not is_match(target, {**control, "seat": 1}, {1}, {"target"}, 1.0)
    assert holm_adjust({1: 0.01, 2: 0.04, 3: 0.20}) == {
        1: 0.03,
        2: 0.08,
        3: 0.2,
    }
    low, high = bootstrap_ci([-30.0, -20.0, -10.0], 1000, 7)
    assert low <= -20 <= high
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--leaderboard", type=Path, default=DEFAULT_LEADERBOARD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    parser.add_argument("--null-reps", type=int, default=NULL_REPS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    resident_rows, leaderboard, source = load_sources(
        args.games, args.leaderboard
    )
    opponents = evaluate_exact_opponents(
        resident_rows,
        leaderboard,
        args.bootstrap_reps,
        args.null_reps,
        args.seed,
    )
    verdict, actionable = overall_verdict(opponents)
    result = {
        "schema": 1,
        "protocol": "docs/m2-opponent-specific-losses-protocol-2026-07-30.md",
        "verdict": verdict,
        "resident_agent_id": RESIDENT_AGENT_ID,
        "source": source,
        "parameters": {
            "primary_opponent_score_band": PRIMARY_BAND,
            "sensitivity_bands": list(SENSITIVITY_BANDS),
            "min_games": MIN_GAMES,
            "min_per_seat": MIN_PER_SEAT,
            "min_controls_per_game": MIN_CONTROLS,
            "bootstrap_reps": args.bootstrap_reps,
            "null_reps": args.null_reps,
            "seed": args.seed,
        },
        "primary_eligible_count": sum(row["primary_eligible"] for row in opponents),
        "actionable": [
            {
                "agent_id": row["agent_id"],
                "pseudo": row["pseudo"],
                "mean_margin_residual": row["primary"]["mean_margin_residual"],
                "holm_adjusted_p": row["primary"]["holm_adjusted_p"],
            }
            for row in actionable
        ],
        "opponents": opponents,
        "pseudo_sensitivities": pseudo_sensitivities(resident_rows),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    table_path = args.output_dir / "opponents.csv"
    report_path = args.output_dir / "report.md"
    result_path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    write_csv(table_path, opponents)
    report_path.write_text(render_report(result))
    print(
        json.dumps(
            {
                "verdict": verdict,
                "primary_eligible_count": result["primary_eligible_count"],
                "actionable": result["actionable"],
                "output": str(result_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
