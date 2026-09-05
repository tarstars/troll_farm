#!/usr/bin/env python3
"""Opponent-strength controls for the norxondor port post-mortem.

There is almost no direct rating overlap between the real norxondor games and the
current champion packages.  This script therefore reports the lack of support,
a small common-support stress slice, name-matched opponents, and a transparent
corpus-calibrated normalization instead of fabricating a reweighted estimate.
"""
from __future__ import annotations

import collections
import gzip
import json
import math
import random
import re
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "chatgpt_2/port-postmortem/results"
PROFILE = ROOT / "local_claude_1/reconstructions/profiles/norxondor_gorgonax.json"
CORPUS = ROOT / "data/processed/games.jsonl"
NORX_PLATFORM_RATING = 29.66
PACKAGES = (
    (ROOT / "local_claude_1/ladder-queue/games-41234663/games-agent6693889-submission41234663.jsonl.gz", 6693889),
    (ROOT / "local_claude_1/ladder-queue/games-41236823/games-agent6696368-submission41236823.jsonl.gz", 6696368),
)
BINS = ((-math.inf, 18, "<18"), (18, 20, "18-20"), (20, 22, "20-22"),
        (22, 24, "22-24"), (24, 26, "24-26"), (26, 28, "26-28"),
        (28, math.inf, ">=28"))


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def load_gzip(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def real_records() -> list[dict[str, Any]]:
    profile = json.loads(PROFILE.read_text())
    return [{
        "game_id": int(row["gameId"]),
        "seat": int(row["seat"]),
        "score": float(row["score"]),
        "opp_score": float(row["opp_score"]),
        "margin": float(row["score"] - row["opp_score"]),
        "opp_arena": float(row["opp_arena"]),
        "own_arena": NORX_PLATFORM_RATING,
        "opp_name": str(row["opp"]),
        "opp_id": int(row["opp_id"]),
    } for row in profile["games"]]


def champion_records() -> list[dict[str, Any]]:
    out = []
    for path, agent_id in PACKAGES:
        for replay in load_gzip(path):
            seats = [int(agent["index"]) for agent in replay["agents"] if int(agent["agentId"]) == agent_id]
            if len(seats) != 1:
                raise ValueError((replay["gameId"], agent_id, seats))
            seat = seats[0]
            own = next(agent for agent in replay["agents"] if int(agent["index"]) == seat)
            opp = next(agent for agent in replay["agents"] if int(agent["index"]) != seat)
            own_score = float(replay["scores"][seat])
            opp_score = float(replay["scores"][1 - seat])
            out.append({
                "game_id": int(replay["gameId"]),
                "seat": seat,
                "score": own_score,
                "opp_score": opp_score,
                "margin": own_score - opp_score,
                "opp_arena": float(opp["score"]),
                "own_arena": float(own["score"]),
                "opp_name": str(opp.get("codingamer", {}).get("pseudo", opp["agentId"])),
                "opp_id": int(opp["agentId"]),
            })
    return out


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [matrix[i][:] + [vector[i]] for i in range(n)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("singular normal equations")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[column])]
    return [augmented[i][-1] for i in range(n)]


def ols(features: list[list[float]], outcomes: list[float]) -> list[float]:
    width = len(features[0])
    xtx = [[0.0] * width for _ in range(width)]
    xty = [0.0] * width
    for row, outcome in zip(features, outcomes):
        for i in range(width):
            xty[i] += row[i] * outcome
            for j in range(width):
                xtx[i][j] += row[i] * row[j]
    return solve(xtx, xty)


def load_corpus() -> list[dict[str, float]]:
    rows = []
    with CORPUS.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            game = json.loads(line)
            if len(game.get("players", [])) != 2 or len(game.get("scores", [])) != 2:
                continue
            try:
                r0 = float(game["players"][0]["arenaScore"])
                r1 = float(game["players"][1]["arenaScore"])
                s0 = float(game["scores"][0])
                s1 = float(game["scores"][1])
            except (KeyError, TypeError, ValueError):
                continue
            if not all(math.isfinite(value) for value in (r0, r1, s0, s1)) or min(s0, s1) < 0:
                continue
            rows.append({"r0": r0, "r1": r1, "s0": s0, "s1": s1})
    return rows


def fit_calibration(rows: list[dict[str, float]]) -> dict[str, Any]:
    margin_x = [[1.0, row["r0"] - row["r1"]] for row in rows]
    margin_y = [row["s0"] - row["s1"] for row in rows]
    margin_intercept, margin_per_rating = ols(margin_x, margin_y)

    score_x = []
    score_y = []
    for row in rows:
        score_x.append([1.0, row["r0"], row["r1"], 0.0])
        score_y.append(row["s0"])
        score_x.append([1.0, row["r1"], row["r0"], 1.0])
        score_y.append(row["s1"])
    score_coefficients = ols(score_x, score_y)
    return {
        "games": len(rows),
        "margin_intercept": margin_intercept,
        "margin_points_per_rating_difference": margin_per_rating,
        "score_coefficients": {
            "intercept": score_coefficients[0],
            "own_rating": score_coefficients[1],
            "opponent_rating": score_coefficients[2],
            "seat_1": score_coefficients[3],
        },
    }


def mean(records: list[dict[str, Any]], field: str) -> float:
    return statistics.fmean(float(row[field]) for row in records)


def quantile(values: list[float], probability: float) -> float:
    values = sorted(values)
    return values[round((len(values) - 1) * probability)]


def bootstrap_difference(
    left: list[dict[str, Any]], right: list[dict[str, Any]], function,
    *, seed: int, draws: int = 5000,
) -> list[float]:
    rng = random.Random(seed)
    values = []
    for _ in range(draws):
        lsample = [left[rng.randrange(len(left))] for _ in left]
        rsample = [right[rng.randrange(len(right))] for _ in right]
        values.append(function(lsample) - function(rsample))
    values.sort()
    return [values[int(draws * .025)], values[int(draws * .975) - 1]]


def summarize(records: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "n": len(records),
        "opponent_rating_mean": mean(records, "opp_arena"),
        "own_rating_mean": mean(records, "own_arena"),
        "score_mean": mean(records, "score"),
        "opponent_score_mean": mean(records, "opp_score"),
        "margin_mean": mean(records, "margin"),
    }


def bin_counts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for lower, upper, label in BINS:
        group = [row for row in records if lower <= row["opp_arena"] < upper]
        if group:
            item = summarize(group)
            item["bin"] = label
            result.append(item)
    return result


def name_match(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    lgroups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    rgroups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in left:
        lgroups[normalize_name(row["opp_name"])].append(row)
    for row in right:
        rgroups[normalize_name(row["opp_name"])].append(row)
    details = []
    weighted_margin = []
    weighted_score = []
    for key in sorted(lgroups.keys() & rgroups.keys()):
        if not key:
            continue
        lg, rg = lgroups[key], rgroups[key]
        weight = min(len(lg), len(rg))
        detail = {
            "name": lg[0]["opp_name"],
            "norx_n": len(lg),
            "champion_n": len(rg),
            "norx_opponent_rating": mean(lg, "opp_arena"),
            "champion_opponent_rating": mean(rg, "opp_arena"),
            "margin_difference": mean(lg, "margin") - mean(rg, "margin"),
            "score_difference": mean(lg, "score") - mean(rg, "score"),
            "weight": weight,
        }
        details.append(detail)
        weighted_margin.extend([detail["margin_difference"]] * weight)
        weighted_score.extend([detail["score_difference"]] * weight)
    return {
        "opponents": len(details),
        "matched_weight": len(weighted_margin),
        "margin_difference": statistics.fmean(weighted_margin) if weighted_margin else None,
        "score_difference": statistics.fmean(weighted_score) if weighted_score else None,
        "details": details,
    }


def main() -> int:
    norx = real_records()
    champion = champion_records()
    corpus = load_corpus()
    calibration = fit_calibration(corpus)
    anchor = (mean(norx, "opp_arena") + mean(champion, "opp_arena")) / 2
    margin_slope = calibration["margin_points_per_rating_difference"]
    score_opp_slope = calibration["score_coefficients"]["opponent_rating"]

    def adjusted_margin(records):
        return statistics.fmean(row["margin"] + margin_slope * (row["opp_arena"] - anchor) for row in records)

    def adjusted_score(records):
        return statistics.fmean(row["score"] + score_opp_slope * (anchor - row["opp_arena"]) for row in records)

    raw_margin_interval = bootstrap_difference(norx, champion, lambda rows: mean(rows, "margin"), seed=51)
    raw_score_interval = bootstrap_difference(norx, champion, lambda rows: mean(rows, "score"), seed=52)
    adjusted_margin_interval = bootstrap_difference(norx, champion, adjusted_margin, seed=53)
    adjusted_score_interval = bootstrap_difference(norx, champion, adjusted_score, seed=54)

    weak_norx = [row for row in norx if row["opp_arena"] < 22]
    weak_champion = [row for row in champion if row["opp_arena"] < 22]
    weak = {
        "definition": "opponent rating below 22; this is the only broad slice with more than a handful of observations in both cohorts",
        "norxondor": summarize(weak_norx),
        "champion": summarize(weak_champion),
        "margin_difference": mean(weak_norx, "margin") - mean(weak_champion, "margin"),
        "margin_bootstrap_95": bootstrap_difference(weak_norx, weak_champion, lambda rows: mean(rows, "margin"), seed=55),
        "score_difference": mean(weak_norx, "score") - mean(weak_champion, "score"),
        "score_bootstrap_95": bootstrap_difference(weak_norx, weak_champion, lambda rows: mean(rows, "score"), seed=56),
        "warning": "The real-bot side has only nine games and still faced opponents roughly three rating points stronger, so this is a stress check, not the primary estimate.",
    }

    output = {
        "schema_version": 1,
        "task": "20260905-port-postmortem",
        "support_diagnostic": {
            "norxondor_bins": bin_counts(norx),
            "champion_bins": bin_counts(champion),
            "direct_reweighting_valid": False,
            "reason": "Only four of 320 champion games faced an opponent rated 20 or above, while 209 of 218 norxondor games did. No stable common-support reweighting exists.",
        },
        "raw": {
            "norxondor": summarize(norx),
            "champion": summarize(champion),
            "margin_difference": mean(norx, "margin") - mean(champion, "margin"),
            "margin_bootstrap_95": raw_margin_interval,
            "score_difference": mean(norx, "score") - mean(champion, "score"),
            "score_bootstrap_95": raw_score_interval,
        },
        "platform_control": {
            "norxondor_rating": NORX_PLATFORM_RATING,
            "champion_rating_mean_in_packages": mean(champion, "own_arena"),
            "rating_gap": NORX_PLATFORM_RATING - mean(champion, "own_arena"),
            "interpretation": "The arena rating is the only directly observed opponent-strength-adjusted measure spanning both non-overlapping fields; it has no interval in the stored data.",
        },
        "corpus_calibration": {
            **calibration,
            "anchor_opponent_rating": anchor,
            "norxondor_adjusted_margin": adjusted_margin(norx),
            "champion_adjusted_margin": adjusted_margin(champion),
            "adjusted_margin_difference": adjusted_margin(norx) - adjusted_margin(champion),
            "adjusted_margin_bootstrap_95_conditional_on_calibration": adjusted_margin_interval,
            "norxondor_adjusted_score": adjusted_score(norx),
            "champion_adjusted_score": adjusted_score(champion),
            "adjusted_score_difference": adjusted_score(norx) - adjusted_score(champion),
            "adjusted_score_bootstrap_95_conditional_on_calibration": adjusted_score_interval,
            "warning": "This transports both cohorts to the midpoint opponent rating using a common slope estimated from the 1,302-game local corpus. It is an extrapolating sensitivity analysis, not a paired causal estimate.",
        },
        "weak_common_support": weak,
        "opponent_name_match": name_match(norx, champion),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "calibration.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print("GLOBAL_CORPUS_GAMES", len(corpus))
    print("MARGIN_POINTS_PER_RATING", margin_slope)
    print("RAW_MARGIN_DIFF", output["raw"]["margin_difference"], raw_margin_interval)
    print("ADJUSTED_MARGIN_DIFF", output["corpus_calibration"]["adjusted_margin_difference"], adjusted_margin_interval)
    print("RAW_SCORE_DIFF", output["raw"]["score_difference"], raw_score_interval)
    print("ADJUSTED_SCORE_DIFF", output["corpus_calibration"]["adjusted_score_difference"], adjusted_score_interval)
    print("WEAK_SUPPORT_MARGIN_DIFF", weak["margin_difference"], weak["margin_bootstrap_95"])
    print("NAME_MATCH", json.dumps(output["opponent_name_match"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
