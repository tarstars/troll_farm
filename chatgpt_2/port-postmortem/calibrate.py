#!/usr/bin/env python3
"""Opponent-strength controls for the norxondor port post-mortem.

The target and champion fields scarcely overlap. Report that fact, then use
three transparent sensitivities: the platform ratings themselves, the small
shared weak-opponent slice, and a common opponent-rating slope estimated within
other committed behaviour profiles with a bot-and-seat fixed effect.
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
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "chatgpt_2/port-postmortem/results"
PROFILE_DIR = ROOT / "local_claude_1/reconstructions/profiles"
TARGET_PROFILE = PROFILE_DIR / "norxondor_gorgonax.json"
NORX_PLATFORM_RATING = 29.66
CALIBRATION_PROFILES = ("Bubaptik", "MSz", "delineate", "tass")
PACKAGES = (
    (
        "champion-41234663",
        ROOT
        / "local_claude_1/ladder-queue/games-41234663"
        / "games-agent6693889-submission41234663.jsonl.gz",
        6693889,
    ),
    (
        "champion-41236823",
        ROOT
        / "local_claude_1/ladder-queue/games-41236823"
        / "games-agent6696368-submission41236823.jsonl.gz",
        6696368,
    ),
)
BINS = (
    (-math.inf, 18, "<18"),
    (18, 20, "18-20"),
    (20, 22, "20-22"),
    (22, 24, "22-24"),
    (24, 26, "24-26"),
    (26, 28, "26-28"),
    (28, math.inf, ">=28"),
)


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def load_gzip(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def profile_records(
    path: Path,
    group: str,
    own_arena: float | None = None,
) -> list[dict[str, Any]]:
    profile = json.loads(path.read_text())
    out = []
    for row in profile["games"]:
        try:
            opponent_rating = float(row["opp_arena"])
            score = float(row["score"])
            opponent_score = float(row["opp_score"])
        except (KeyError, TypeError, ValueError):
            continue
        if not all(
            math.isfinite(value)
            for value in (opponent_rating, score, opponent_score)
        ):
            continue
        out.append(
            {
                "group": group,
                "game_id": int(row["gameId"]),
                "seat": int(row["seat"]),
                "score": score,
                "opp_score": opponent_score,
                "margin": score - opponent_score,
                "opp_arena": opponent_rating,
                "own_arena": own_arena,
                "opp_name": str(row["opp"]),
                "opp_id": int(row["opp_id"]),
            }
        )
    return out


def champion_records() -> list[dict[str, Any]]:
    out = []
    for group, path, agent_id in PACKAGES:
        for replay in load_gzip(path):
            seats = [
                int(agent["index"])
                for agent in replay["agents"]
                if int(agent["agentId"]) == agent_id
            ]
            if len(seats) != 1:
                raise ValueError((replay["gameId"], agent_id, seats))
            seat = seats[0]
            own = next(
                agent for agent in replay["agents"] if int(agent["index"]) == seat
            )
            opponent = next(
                agent for agent in replay["agents"] if int(agent["index"]) != seat
            )
            score = float(replay["scores"][seat])
            opponent_score = float(replay["scores"][1 - seat])
            out.append(
                {
                    "group": group,
                    "game_id": int(replay["gameId"]),
                    "seat": seat,
                    "score": score,
                    "opp_score": opponent_score,
                    "margin": score - opponent_score,
                    "opp_arena": float(opponent["score"]),
                    "own_arena": float(own["score"]),
                    "opp_name": str(
                        opponent.get("codingamer", {}).get(
                            "pseudo", opponent["agentId"]
                        )
                    ),
                    "opp_id": int(opponent["agentId"]),
                }
            )
    return out


def mean(records: list[dict[str, Any]], field: str) -> float:
    return statistics.fmean(float(row[field]) for row in records)


def summarize(records: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "n": len(records),
        "opponent_rating_mean": mean(records, "opp_arena"),
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


def bootstrap_difference(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    statistic: Callable[[list[dict[str, Any]]], float],
    *,
    seed: int,
    draws: int = 5000,
) -> list[float]:
    rng = random.Random(seed)
    values = []
    for _ in range(draws):
        lsample = [left[rng.randrange(len(left))] for _ in left]
        rsample = [right[rng.randrange(len(right))] for _ in right]
        values.append(statistic(lsample) - statistic(rsample))
    values.sort()
    return [values[int(draws * 0.025)], values[int(draws * 0.975) - 1]]


def fixed_effect_slope(
    records: list[dict[str, Any]],
    field: str,
) -> dict[str, Any]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = collections.defaultdict(
        list
    )
    for row in records:
        groups[(row["group"], int(row["seat"]))].append(row)
    numerator = denominator = 0.0
    usable = {}
    for key, rows in groups.items():
        if len(rows) < 3:
            continue
        xbar = mean(rows, "opp_arena")
        ybar = mean(rows, field)
        local_denominator = sum(
            (row["opp_arena"] - xbar) ** 2 for row in rows
        )
        if local_denominator <= 0:
            continue
        numerator += sum(
            (row["opp_arena"] - xbar) * (row[field] - ybar)
            for row in rows
        )
        denominator += local_denominator
        usable[f"{key[0]}:seat{key[1]}"] = len(rows)
    if denominator <= 0:
        raise ValueError("no within-group opponent-rating variation")
    return {
        "slope": numerator / denominator,
        "groups": usable,
        "observations": sum(usable.values()),
    }


def bootstrap_slope(
    records: list[dict[str, Any]],
    field: str,
    seed: int,
    draws: int = 3000,
) -> list[float]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = collections.defaultdict(
        list
    )
    for row in records:
        grouped[(row["group"], int(row["seat"]))].append(row)
    rng = random.Random(seed)
    values = []
    for _ in range(draws):
        sample = []
        for rows in grouped.values():
            sample.extend(rows[rng.randrange(len(rows))] for _ in rows)
        values.append(fixed_effect_slope(sample, field)["slope"])
    values.sort()
    return [values[int(draws * 0.025)], values[int(draws * 0.975) - 1]]


def name_match(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
) -> dict[str, Any]:
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
        item = {
            "name": lg[0]["opp_name"],
            "norxondor_n": len(lg),
            "champion_n": len(rg),
            "norxondor_opponent_rating": mean(lg, "opp_arena"),
            "champion_opponent_rating": mean(rg, "opp_arena"),
            "margin_difference": mean(lg, "margin") - mean(rg, "margin"),
            "score_difference": mean(lg, "score") - mean(rg, "score"),
            "weight": weight,
        }
        details.append(item)
        weighted_margin.extend([item["margin_difference"]] * weight)
        weighted_score.extend([item["score_difference"]] * weight)
    return {
        "opponents": len(details),
        "matched_weight": len(weighted_margin),
        "margin_difference": (
            statistics.fmean(weighted_margin) if weighted_margin else None
        ),
        "score_difference": (
            statistics.fmean(weighted_score) if weighted_score else None
        ),
        "details": details,
    }


def main() -> int:
    norxondor = profile_records(
        TARGET_PROFILE, "norxondor", NORX_PLATFORM_RATING
    )
    champion = champion_records()

    calibration_records = []
    for name in CALIBRATION_PROFILES:
        calibration_records.extend(
            profile_records(PROFILE_DIR / f"{name}.json", name)
        )
    calibration_records.extend(champion)
    margin_fit = fixed_effect_slope(calibration_records, "margin")
    score_fit = fixed_effect_slope(calibration_records, "score")
    margin_slope = margin_fit["slope"]
    score_slope = score_fit["slope"]
    anchor = (
        mean(norxondor, "opp_arena") + mean(champion, "opp_arena")
    ) / 2

    def adjusted(field: str, slope: float):
        return lambda rows: statistics.fmean(
            row[field] + slope * (anchor - row["opp_arena"])
            for row in rows
        )

    raw_margin = mean(norxondor, "margin") - mean(champion, "margin")
    raw_score = mean(norxondor, "score") - mean(champion, "score")
    adjusted_margin = adjusted("margin", margin_slope)
    adjusted_score = adjusted("score", score_slope)

    weak_norxondor = [row for row in norxondor if row["opp_arena"] < 22]
    weak_champion = [row for row in champion if row["opp_arena"] < 22]

    output = {
        "schema_version": 1,
        "task": "20260905-port-postmortem",
        "support_diagnostic": {
            "norxondor_bins": bin_counts(norxondor),
            "champion_bins": bin_counts(champion),
            "direct_reweighting_valid": False,
            "reason": (
                "Only four of 320 champion games faced an opponent rated 20 or "
                "above, while 209 of 218 norxondor games did. A nonparametric "
                "reweighting would be almost entirely extrapolation."
            ),
        },
        "raw": {
            "norxondor": summarize(norxondor),
            "champion": summarize(champion),
            "margin_difference": raw_margin,
            "margin_bootstrap_95": bootstrap_difference(
                norxondor,
                champion,
                lambda rows: mean(rows, "margin"),
                seed=51,
            ),
            "score_difference": raw_score,
            "score_bootstrap_95": bootstrap_difference(
                norxondor,
                champion,
                lambda rows: mean(rows, "score"),
                seed=52,
            ),
        },
        "platform_control": {
            "norxondor_rating": NORX_PLATFORM_RATING,
            "champion_rating_mean_in_packages": statistics.fmean(
                row["own_arena"] for row in champion
            ),
            "rating_gap": NORX_PLATFORM_RATING
            - statistics.fmean(row["own_arena"] for row in champion),
            "interpretation": (
                "Arena rating is the only directly observed opponent-strength-"
                "adjusted measure spanning the two non-overlapping matchmaking "
                "fields; the stored records provide no uncertainty interval for it."
            ),
        },
        "profile_fixed_effect_calibration": {
            "profiles": list(CALIBRATION_PROFILES)
            + [name for name, _, _ in PACKAGES],
            "anchor_opponent_rating": anchor,
            "margin_opponent_rating_slope": margin_fit,
            "margin_slope_bootstrap_95": bootstrap_slope(
                calibration_records, "margin", seed=61
            ),
            "score_opponent_rating_slope": score_fit,
            "score_slope_bootstrap_95": bootstrap_slope(
                calibration_records, "score", seed=62
            ),
            "norxondor_adjusted_margin": adjusted_margin(norxondor),
            "champion_adjusted_margin": adjusted_margin(champion),
            "adjusted_margin_difference": adjusted_margin(norxondor)
            - adjusted_margin(champion),
            "adjusted_margin_bootstrap_95_conditional_on_slope": (
                bootstrap_difference(
                    norxondor,
                    champion,
                    adjusted_margin,
                    seed=53,
                )
            ),
            "norxondor_adjusted_score": adjusted_score(norxondor),
            "champion_adjusted_score": adjusted_score(champion),
            "adjusted_score_difference": adjusted_score(norxondor)
            - adjusted_score(champion),
            "adjusted_score_bootstrap_95_conditional_on_slope": (
                bootstrap_difference(
                    norxondor,
                    champion,
                    adjusted_score,
                    seed=54,
                )
            ),
            "warning": (
                "This uses a common within-bot, within-seat slope from four other "
                "committed profiles plus the champion packages. Transporting the "
                "champion from rating-17.5 opponents to the 21.5 midpoint remains "
                "extrapolation, so this is a sensitivity analysis, not a paired "
                "causal estimate."
            ),
        },
        "weak_common_support": {
            "definition": "opponent rating below 22",
            "norxondor": summarize(weak_norxondor),
            "champion": summarize(weak_champion),
            "margin_difference": mean(weak_norxondor, "margin")
            - mean(weak_champion, "margin"),
            "margin_bootstrap_95": bootstrap_difference(
                weak_norxondor,
                weak_champion,
                lambda rows: mean(rows, "margin"),
                seed=55,
            ),
            "score_difference": mean(weak_norxondor, "score")
            - mean(weak_champion, "score"),
            "score_bootstrap_95": bootstrap_difference(
                weak_norxondor,
                weak_champion,
                lambda rows: mean(rows, "score"),
                seed=56,
            ),
            "warning": (
                "The real-bot side has only nine games and still faced opponents "
                "roughly three rating points stronger. This is a stress check, not "
                "the primary estimate."
            ),
        },
        "opponent_name_match": name_match(norxondor, champion),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "calibration.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n"
    )
    print("CALIBRATION_OBSERVATIONS", margin_fit["observations"])
    print(
        "MARGIN_OPPONENT_SLOPE",
        margin_slope,
        output["profile_fixed_effect_calibration"][
            "margin_slope_bootstrap_95"
        ],
    )
    print(
        "RAW_MARGIN_DIFFERENCE",
        raw_margin,
        output["raw"]["margin_bootstrap_95"],
    )
    print(
        "ADJUSTED_MARGIN_DIFFERENCE",
        output["profile_fixed_effect_calibration"][
            "adjusted_margin_difference"
        ],
        output["profile_fixed_effect_calibration"][
            "adjusted_margin_bootstrap_95_conditional_on_slope"
        ],
    )
    print(
        "RAW_SCORE_DIFFERENCE",
        raw_score,
        output["raw"]["score_bootstrap_95"],
    )
    print(
        "ADJUSTED_SCORE_DIFFERENCE",
        output["profile_fixed_effect_calibration"][
            "adjusted_score_difference"
        ],
        output["profile_fixed_effect_calibration"][
            "adjusted_score_bootstrap_95_conditional_on_slope"
        ],
    )
    print("WEAK_SUPPORT", json.dumps(output["weak_common_support"], sort_keys=True))
    print("NAME_MATCH", json.dumps(output["opponent_name_match"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
