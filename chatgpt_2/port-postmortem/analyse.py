#!/usr/bin/env python3
"""Read-only post-mortem of the norxondor behavioural port.

The script compares:
* 218 recorded games of the real norxondor_gorgonax bot from the committed profile;
* two independent 160-game packages of the real champion lineage;
* the 400-game closed-loop v2 port-vs-champion loss read;
* the public 616-game time series for the real norxondor bot.

It changes no policy and performs no platform action.
"""
from __future__ import annotations

import collections
import gzip
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from local_claude_1.reconstructions.fits.reconstruct import (  # noqa: E402
    Reconstructor,
    build_game,
    parse_frame0,
)

PROFILE = ROOT / "local_claude_1/reconstructions/profiles/norxondor_gorgonax.json"
PUBLIC_STATS = ROOT / "local_claude_1/reconstructions/sources/all-legend-players-eulerschezahl-stats-2026-05-25.json"
PORT_LOSS = ROOT / "codex_1/norxondor-port/loss-read-v2.json"
OUTPUT_DIR = ROOT / "chatgpt_2/port-postmortem/results"
ENDPOINTS = (0, 50, 100, 150, 200, 250, 300)
RATING_BINS = ((-1e9, 20.0, "<20"), (20.0, 22.0, "20-22"), (22.0, 24.0, "22-24"),
               (24.0, 26.0, "24-26"), (26.0, 28.0, "26-28"), (28.0, 1e9, ">=28"))

PACKAGES = (
    ("champion-41234663", ROOT / "local_claude_1/ladder-queue/games-41234663/games-agent6693889-submission41234663.jsonl.gz", 6693889),
    ("champion-41236823", ROOT / "local_claude_1/ladder-queue/games-41236823/games-agent6696368-submission41236823.jsonl.gz", 6696368),
)


class ReplayReconstructor(Reconstructor):
    def __init__(self, replay: dict[str, Any]) -> None:
        self.game_id = int(replay["gameId"])
        self.replay = replay
        self.frames = replay["frames"]
        width, height, rows, units, plants, inventories = parse_frame0(self.frames[0])
        self.map = {"w": width, "h": height, "rows": rows}
        self.game = build_game(width, height, rows, units, plants, inventories)
        self.unit_by_eid = {}
        self.plant_by_eid = {}
        by_id = {unit.id: unit for unit in self.game.units}
        for entity_id, unit in units.items():
            self.unit_by_eid[entity_id] = by_id[unit["id"]]
        by_pos = {plant.pos: plant for plant in self.game.plants}
        for entity_id, plant in plants.items():
            self.plant_by_eid[entity_id] = by_pos[(plant["x"], plant["y"])]
        self.mismatch = collections.Counter()
        self.examples = {}
        self.agents = {agent["index"]: agent for agent in replay["agents"]}
        self.n_turns = (len(self.frames) - 1) // 2


def bank_score(inventory: list[int]) -> float:
    return float(sum(inventory[:4]) + 4 * inventory[5])


def gameplay_verb(command: str) -> str:
    fields = command.split()
    return fields[0].upper() if fields else ""


def load_package(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def analyse_champion_game(replay: dict[str, Any], agent_id: int, cohort: str) -> dict[str, Any]:
    seats = [int(agent["index"]) for agent in replay["agents"] if int(agent["agentId"]) == agent_id]
    if len(seats) != 1:
        raise ValueError(f"game {replay['gameId']}: target seat count {len(seats)}")
    seat = seats[0]
    opponent = next(agent for agent in replay["agents"] if int(agent["index"]) != seat)
    reconstructor = ReplayReconstructor(replay)
    states = reconstructor.run(keep_states=True)
    n_turns = reconstructor.n_turns
    train_turns: list[int] = []
    plants = harvests = chops = 0
    for turn in range(1, n_turns + 1):
        for command in reconstructor.commands(turn)[seat]:
            verb = gameplay_verb(command)
            if verb == "TRAIN":
                train_turns.append(turn)
            elif verb == "PLANT":
                plants += 1
            elif verb == "HARVEST":
                harvests += 1
            elif verb == "CHOP":
                chops += 1
    trajectory = {}
    for endpoint in ENDPOINTS:
        index = min(endpoint, n_turns)
        state = states[index]
        own_inv = list(state["inv"][seat])
        opp_inv = list(state["inv"][1 - seat])
        trajectory[str(endpoint)] = {
            "source_turn": index,
            "score": bank_score(own_inv),
            "opp_score": bank_score(opp_inv),
            "fruit": float(sum(own_inv[:4])),
            "wood": int(own_inv[5]),
            "roster": sum(1 for unit in state["units"] if int(unit["player"]) == seat),
        }
    final_score = float(replay["scores"][seat])
    final_opp = float(replay["scores"][1 - seat])
    reconstructed_final = trajectory["300"]["score"]
    return {
        "cohort": cohort,
        "game_id": int(replay["gameId"]),
        "seat": seat,
        "opp_id": int(opponent["agentId"]),
        "opp_name": str(opponent.get("codingamer", {}).get("pseudo", opponent["agentId"])),
        "opp_arena": float(opponent["score"]),
        "own_arena": float(next(agent for agent in replay["agents"] if int(agent["index"]) == seat)["score"]),
        "score": final_score,
        "opp_score": final_opp,
        "margin": final_score - final_opp,
        "win": 1.0 if final_score > final_opp else 0.5 if final_score == final_opp else 0.0,
        "turns": n_turns,
        "train_turns": train_turns,
        "trolls": trajectory["300"]["roster"],
        "plants": plants,
        "harvests": harvests,
        "chops": chops,
        "fruit_pts": trajectory["300"]["fruit"],
        "wood": trajectory["300"]["wood"],
        "wood_pts": 4 * trajectory["300"]["wood"],
        "trajectory": trajectory,
        "reconstruction_mismatches": dict(reconstructor.mismatch),
        "final_score_error": reconstructed_final - final_score,
    }


def summary(records: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "n": len(records),
        "opp_arena": statistics.fmean(row["opp_arena"] for row in records),
        "score": statistics.fmean(row["score"] for row in records),
        "opp_score": statistics.fmean(row["opp_score"] for row in records),
        "margin": statistics.fmean(row["margin"] for row in records),
        "win_rate": statistics.fmean(row["win"] for row in records),
        "trolls": statistics.fmean(row["trolls"] for row in records),
        "plants": statistics.fmean(row["plants"] for row in records),
        "harvests": statistics.fmean(row["harvests"] for row in records),
        "chops": statistics.fmean(row["chops"] for row in records),
        "fruit_pts": statistics.fmean(row["fruit_pts"] for row in records),
        "wood_pts": statistics.fmean(row["wood_pts"] for row in records),
    }


def rating_bin(value: float) -> str:
    for lower, upper, label in RATING_BINS:
        if lower <= value < upper:
            return label
    raise AssertionError(value)


def binned(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for _, _, label in RATING_BINS:
        group = [row for row in records if rating_bin(row["opp_arena"]) == label]
        if group:
            item = summary(group)
            item["bin"] = label
            rows.append(item)
    return rows


def fixed_strata(norx: list[dict[str, Any]], champion: list[dict[str, Any]]) -> list[tuple[str, int]]:
    strata = []
    for _, _, label in RATING_BINS:
        for seat in (0, 1):
            left = sum(1 for row in norx if rating_bin(row["opp_arena"]) == label and row["seat"] == seat)
            right = sum(1 for row in champion if rating_bin(row["opp_arena"]) == label and row["seat"] == seat)
            if left >= 3 and right >= 3:
                strata.append((label, seat))
    return strata


def standardized_difference(
    norx: list[dict[str, Any]], champion: list[dict[str, Any]], field: str,
    strata: list[tuple[str, int]], weights: dict[tuple[str, int], float],
) -> float | None:
    value = 0.0
    for key in strata:
        label, seat = key
        left = [row[field] for row in norx if rating_bin(row["opp_arena"]) == label and row["seat"] == seat]
        right = [row[field] for row in champion if rating_bin(row["opp_arena"]) == label and row["seat"] == seat]
        if not left or not right:
            return None
        value += weights[key] * (statistics.fmean(left) - statistics.fmean(right))
    return value


def bootstrap_standardized(
    norx: list[dict[str, Any]], champion: list[dict[str, Any]], field: str,
    strata: list[tuple[str, int]], weights: dict[tuple[str, int], float], seed: int,
    draws: int = 5000,
) -> list[float]:
    rng = random.Random(seed)
    values = []
    for _ in range(draws):
        left = [norx[rng.randrange(len(norx))] for _ in norx]
        right = [champion[rng.randrange(len(champion))] for _ in champion]
        value = standardized_difference(left, right, field, strata, weights)
        if value is not None:
            values.append(value)
    values.sort()
    return [values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]]


def exact_opponent_match(norx: list[dict[str, Any]], champion: list[dict[str, Any]], field: str) -> dict[str, Any]:
    left: dict[int, list[float]] = collections.defaultdict(list)
    right: dict[int, list[float]] = collections.defaultdict(list)
    for row in norx:
        left[row["opp_id"]].append(row[field])
    for row in champion:
        right[row["opp_id"]].append(row[field])
    common = [key for key in left.keys() & right.keys() if len(left[key]) >= 2 and len(right[key]) >= 2]
    weighted = []
    for key in common:
        delta = statistics.fmean(left[key]) - statistics.fmean(right[key])
        weighted.extend([delta] * min(len(left[key]), len(right[key])))
    return {
        "opponents": len(common),
        "matched_weight": len(weighted),
        "difference": statistics.fmean(weighted) if weighted else None,
        "opponent_ids": sorted(common),
    }


def public_curve(player: dict[str, Any], key: str, endpoints: Iterable[int]) -> dict[str, dict[str, float]]:
    source = {int(turn): float(value) for turn, value in player[key]}
    result = {}
    for endpoint in endpoints:
        available = [turn for turn in source if turn <= endpoint]
        turn = max(available) if available else min(source)
        result[str(endpoint)] = {"source_turn": turn, "value": source[turn]}
    return result


def cumulative_port_curve(port_loss: dict[str, Any]) -> dict[str, dict[str, float]]:
    result = {"0": {"score": 0.0, "wood_pts": 0.0, "fruit_current": 0.0}}
    cumulative_wood = 0.0
    endpoints = (50, 100, 150, 200, 250, 300)
    for endpoint, phase in zip(endpoints, port_loss["summary"]["score_by_50_turn_phase"]):
        cumulative_wood += float(phase["policy"]["wood_score_banked_mean"])
        score = float(phase["policy"]["bank_score_after_phase_mean"])
        result[str(endpoint)] = {
            "score": score,
            "wood_pts": cumulative_wood,
            "fruit_current": score - cumulative_wood,
            "champion_score": float(phase["champion"]["bank_score_after_phase_mean"]),
            "policy_minus_champion": float(phase["policy_minus_champion_score"]),
        }
    return result


def phase_command_counts(profile: dict[str, Any], lo: int, hi: int) -> dict[str, float]:
    out = collections.Counter()
    for label, values in profile["verbs_by_bucket_per_game"].items():
        start, end = (int(value) for value in label.split("-"))
        if start >= lo and end <= hi:
            out.update(values)
    return dict(out)


def main() -> int:
    profile = json.loads(PROFILE.read_text())
    public = json.loads(PUBLIC_STATS.read_text())
    port_loss = json.loads(PORT_LOSS.read_text())

    norx_records = []
    for row in profile["games"]:
        norx_records.append({
            "cohort": "real-norxondor-profile",
            "game_id": int(row["gameId"]),
            "seat": int(row["seat"]),
            "opp_id": int(row["opp_id"]),
            "opp_name": str(row["opp"]),
            "opp_arena": float(row["opp_arena"]),
            "score": float(row["score"]),
            "opp_score": float(row["opp_score"]),
            "margin": float(row["score"] - row["opp_score"]),
            "win": float(row["win"]),
            "turns": int(row["turns"]),
            "train_turns": list(row["train_turns"]),
            "trolls": int(row["trolls"]),
            "plants": int(row["plants"]),
            "harvests": int(row["harvests"]),
            "chops": int(row["chops"]),
            "fruit_pts": float(row["fruit_pts"]),
            "wood": int(row["wood"]),
            "wood_pts": float(row["wood_pts"]),
        })

    champion_records = []
    package_summaries = {}
    mismatch_totals = collections.Counter()
    final_score_errors = []
    for cohort, path, agent_id in PACKAGES:
        records = [analyse_champion_game(replay, agent_id, cohort) for replay in load_package(path)]
        champion_records.extend(records)
        package_summaries[cohort] = summary(records)
        for row in records:
            mismatch_totals.update(row["reconstruction_mismatches"])
            final_score_errors.append(row["final_score_error"])

    strata = fixed_strata(norx_records, champion_records)
    norx_counts = {
        key: sum(1 for row in norx_records if rating_bin(row["opp_arena"]) == key[0] and row["seat"] == key[1])
        for key in strata
    }
    total_weight = sum(norx_counts.values())
    weights = {key: count / total_weight for key, count in norx_counts.items()}
    adjusted = {}
    for index, field in enumerate(("score", "margin", "opp_score"), 1):
        estimate = standardized_difference(norx_records, champion_records, field, strata, weights)
        adjusted[field] = {
            "estimate": estimate,
            "bootstrap_95": bootstrap_standardized(norx_records, champion_records, field, strata, weights, 100 + index),
        }

    exact_match = {
        field: exact_opponent_match(norx_records, champion_records, field)
        for field in ("score", "margin", "opp_score")
    }

    real_player = public["norxondor_gorgonax"]
    yamo_player = public["yamo"]
    curve_endpoints = (0, 50, 100, 150, 200, 250, 300)
    real_score_curve = public_curve(real_player, "scores-chart", ()) if False else None
    real_scores = public_curve(real_player, "scores-chart", ()) if False else {}
    real_score_source = {int(t): float(v) for t, v in real_player["scores-chart"]["Score"]}
    real_opp_source = {int(t): float(v) for t, v in real_player["scores-chart"]["Opponent Score"]}
    yamo_score_source = {int(t): float(v) for t, v in yamo_player["scores-chart"]["Score"]}
    real_wood_source = {int(t): float(v) for t, v in real_player["inventory-chart"]["WOOD"]}
    real_plants_sources = [
        {int(t): float(v) for t, v in curve}
        for curve in real_player["plants-chart"].values()
    ]

    def nearest(source: dict[int, float], endpoint: int) -> tuple[int, float]:
        turn = max(t for t in source if t <= endpoint)
        return turn, source[turn]

    port_curve = cumulative_port_curve(port_loss)
    trajectory = []
    for endpoint in curve_endpoints:
        rt, real_score = nearest(real_score_source, endpoint)
        _, real_opp = nearest(real_opp_source, endpoint)
        _, yamo_score = nearest(yamo_score_source, endpoint)
        _, real_wood = nearest(real_wood_source, endpoint)
        real_plants = sum(nearest(source, endpoint)[1] for source in real_plants_sources)
        port = port_curve.get(str(endpoint), {})
        champion_endpoint = statistics.fmean(
            row["trajectory"][str(endpoint)]["score"] for row in champion_records
        )
        trajectory.append({
            "requested_turn": endpoint,
            "public_source_turn": rt,
            "real_norx_score": real_score,
            "real_norx_opp_score": real_opp,
            "public_yamo_score": yamo_score,
            "real_norx_minus_yamo": real_score - yamo_score,
            "real_norx_wood_pts": 4 * real_wood,
            "real_norx_fruit_current": real_score - 4 * real_wood,
            "real_norx_cumulative_plants": real_plants,
            "port_score": port.get("score"),
            "port_wood_pts": port.get("wood_pts"),
            "port_fruit_current": port.get("fruit_current"),
            "port_minus_paired_champion": port.get("policy_minus_champion"),
            "real_norx_minus_port": real_score - port["score"] if "score" in port else None,
            "champion_package_score": champion_endpoint,
        })

    real_train_turns = {}
    for nth in range(1, 6):
        turns = [row["train_turns"][nth - 1] for row in norx_records if len(row["train_turns"]) >= nth]
        if turns:
            real_train_turns[f"train_{nth}"] = {
                "n": len(turns), "mean": statistics.fmean(turns), "median": statistics.median(turns),
                "p25": sorted(turns)[round((len(turns) - 1) * .25)],
                "p75": sorted(turns)[round((len(turns) - 1) * .75)],
            }
    champion_train_turns = {}
    for nth in range(1, 4):
        turns = [row["train_turns"][nth - 1] for row in champion_records if len(row["train_turns"]) >= nth]
        if turns:
            champion_train_turns[f"train_{nth}"] = {
                "n": len(turns), "mean": statistics.fmean(turns), "median": statistics.median(turns),
            }

    port_phase_plants = [float(row["policy_trees_planted_mean"]) for row in port_loss["summary"]["board_and_policy_trees_by_50_turn_phase"]]
    port_cumulative_plants = []
    running = 0.0
    for value in port_phase_plants:
        running += value
        port_cumulative_plants.append(running)

    result = {
        "schema_version": 1,
        "task": "20260905-port-postmortem",
        "verdict": "PORT_SPECIFIC_HYBRID_FAILURE",
        "raw": {
            "real_norxondor": summary(norx_records),
            "champion_combined": summary(champion_records),
            "champion_packages": package_summaries,
        },
        "opponent_strength": {
            "real_norxondor_bins": binned(norx_records),
            "champion_bins": binned(champion_records),
            "common_strata": [
                {"rating_bin": key[0], "seat": key[1], "norx_n": norx_counts[key],
                 "champion_n": sum(1 for row in champion_records if rating_bin(row["opp_arena"]) == key[0] and row["seat"] == key[1]),
                 "weight": weights[key]}
                for key in strata
            ],
            "standardized_to_real_norxondor_rating_and_seat_mix": adjusted,
            "exact_opponent_id_sensitivity": exact_match,
            "limitation": "The cohorts use different maps, draws, dates and opponent submissions; rating/seat and exact-ID adjustment do not make this a causal head-to-head.",
        },
        "trajectory": trajectory,
        "roster": {
            "real_norxondor_profile": real_train_turns,
            "champion_packages": champion_train_turns,
            "port_v2_third_train_median_reported": 74,
            "port_v2_switch_median_reported": 144,
            "port_v3_validity_duel_margin_reported": -59.62,
        },
        "throughput": {
            "real_norxondor_commands_101_150_per_game": phase_command_counts(profile, 101, 150),
            "real_norxondor_commands_151_200_per_game": phase_command_counts(profile, 151, 200),
            "port_commands_100_150_per_game": {
                key: value / 400 for key, value in port_loss["summary"]["activity"]["policy"]["windows"]["100-150"]["counts"].items()
            },
            "port_commands_151_200_per_game": {
                key: value / 400 for key, value in port_loss["summary"]["activity"]["policy"]["windows"]["151-200"]["counts"].items()
            },
            "real_norxondor_total_plants_profile": profile["planting"]["plant_commands_per_game"],
            "real_norxondor_total_harvested_profile": profile["harvesting"]["fruits_harvested_per_game"],
            "port_cumulative_plants_at_50_turn_endpoints": dict(zip((50, 100, 150, 200, 250, 300), port_cumulative_plants)),
            "port_total_fruit_items_banked": sum(float(row["policy"]["fruit_items_banked_mean"]) for row in port_loss["summary"]["score_by_50_turn_phase"]),
        },
        "reconstruction_validation": {
            "champion_games": len(champion_records),
            "mismatches": dict(mismatch_totals),
            "max_abs_final_score_error": max(abs(value) for value in final_score_errors),
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (OUTPUT_DIR / "summary.txt").write_text(
        "PORT_SPECIFIC_HYBRID_FAILURE\n"
        f"real norx raw margin {result['raw']['real_norxondor']['margin']:.2f}\n"
        f"champion raw margin {result['raw']['champion_combined']['margin']:.2f}\n"
        f"rating-seat adjusted margin gap {adjusted['margin']['estimate']:.2f} {adjusted['margin']['bootstrap_95']}\n"
        f"rating-seat adjusted own-score gap {adjusted['score']['estimate']:.2f} {adjusted['score']['bootstrap_95']}\n"
        f"exact-opponent margin sensitivity {exact_match['margin']}\n"
        f"champion reconstruction mismatches {dict(mismatch_totals)}\n"
    )
    print((OUTPUT_DIR / "summary.txt").read_text(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
