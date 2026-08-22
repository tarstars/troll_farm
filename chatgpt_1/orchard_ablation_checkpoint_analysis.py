#!/usr/bin/env python3
"""Compare fresh orchard and no-orchard Arena checkpoints without raw replay access.

This analysis deliberately uses the fresh exact-E7a restore as the orchard arm. The older
rank-11 E7a deployment is retained as historical context only because resubmitting the exact
same bytes changed the ladder placement materially.

Inputs contain compact per-game outcomes and exact opponent agent identities. Outputs are
observational: Arena queues are not paired or randomized. No platform call or mutation occurs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NO_ORCHARD = (
    ROOT
    / "data/analysis/live-agent-6553250"
    / "no-orchard-ablation-terminal-checkpoint-20260803T154310Z.json"
)
DEFAULT_ORCHARD = (
    ROOT
    / "data/analysis/live-agent-6553250"
    / "e7a-restore-collected-games-checkpoint-20260803T175757Z.json"
)
DEFAULT_JSON = ROOT / "chatgpt_1/orchard-ablation-opponent-standardized-2026-08-03.json"
DEFAULT_MD = ROOT / "chatgpt_1/orchard-ablation-opponent-standardized-2026-08-03.md"


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * probability
    lo = math.floor(position)
    hi = math.ceil(position)
    if lo == hi:
        return values[lo]
    fraction = position - lo
    return values[lo] * (1 - fraction) + values[hi] * fraction


def load(path: Path, expected_agent: int, expected_submission: int) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if payload.get("agent_id") != expected_agent:
        raise ValueError(f"{path}: agent mismatch")
    if payload.get("submission_id") != expected_submission:
        raise ValueError(f"{path}: submission mismatch")
    if not payload.get("identity_clean"):
        raise ValueError(f"{path}: identity not clean")
    rows = payload.get("rows") or []
    if len(rows) != payload.get("matching_finished"):
        raise ValueError(f"{path}: row count mismatch")
    if payload.get("fetch_failures"):
        raise ValueError(f"{path}: fetch failures present")
    return payload


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    margins = [float(row["margin"]) for row in rows]
    own = [float(row["our_score"]) for row in rows]
    opp = [float(row["opponent_score"]) for row in rows]
    return {
        "games": len(rows),
        "wins": sum(value > 0 for value in margins),
        "ties": sum(value == 0 for value in margins),
        "losses": sum(value < 0 for value in margins),
        "win_rate": sum(value > 0 for value in margins) / len(rows),
        "nonloss_rate": sum(value >= 0 for value in margins) / len(rows),
        "mean_our_score": mean(own),
        "mean_opponent_score": mean(opp),
        "mean_margin": mean(margins),
        "median_margin": statistics.median(margins),
        "margin_q10": quantile(margins, 0.10),
        "margin_q25": quantile(margins, 0.25),
        "margin_q75": quantile(margins, 0.75),
        "margin_q90": quantile(margins, 0.90),
        "catastrophes": sum(value <= -100 for value in margins),
        "catastrophe_rate": sum(value <= -100 for value in margins) / len(rows),
        "negative_margin_mass": sum(-value for value in margins if value < 0),
        "distinct_opponents": len({int(row["opponent_agent_id"]) for row in rows}),
    }


def groups(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    result: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[int(row["opponent_agent_id"])].append(row)
    return dict(result)


def row_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    margins = [float(row["margin"]) for row in rows]
    return {
        "games": float(len(rows)),
        "win_rate": sum(value > 0 for value in margins) / len(rows),
        "nonloss_rate": sum(value >= 0 for value in margins) / len(rows),
        "our_score": statistics.mean(float(row["our_score"]) for row in rows),
        "opponent_score": statistics.mean(float(row["opponent_score"]) for row in rows),
        "margin": statistics.mean(margins),
        "catastrophe_rate": sum(value <= -100 for value in margins) / len(rows),
    }


def weighted(values: list[tuple[float, float]]) -> float | None:
    denominator = sum(weight for _value, weight in values)
    if denominator == 0:
        return None
    return sum(value * weight for value, weight in values) / denominator


def standardized(
    orchard: dict[int, list[dict[str, Any]]],
    no_orchard: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    common = sorted(set(orchard) & set(no_orchard))
    rows = []
    for opponent_id in common:
        left = row_metrics(orchard[opponent_id])
        right = row_metrics(no_orchard[opponent_id])
        name = orchard[opponent_id][0].get("opponent") or no_orchard[opponent_id][0].get("opponent")
        differences = {
            key: left[key] - right[key]
            for key in (
                "win_rate",
                "nonloss_rate",
                "our_score",
                "opponent_score",
                "margin",
                "catastrophe_rate",
            )
        }
        rows.append(
            {
                "opponent_agent_id": opponent_id,
                "opponent": name,
                "orchard": left,
                "no_orchard": right,
                "orchard_minus_no_orchard": differences,
                "minimum_support_weight": min(left["games"], right["games"]),
                "pooled_support_weight": left["games"] + right["games"],
            }
        )

    metrics = (
        "win_rate",
        "nonloss_rate",
        "our_score",
        "opponent_score",
        "margin",
        "catastrophe_rate",
    )
    schemes = {}
    for scheme, weight_field in (
        ("equal_opponent", None),
        ("minimum_count", "minimum_support_weight"),
        ("pooled_count", "pooled_support_weight"),
    ):
        schemes[scheme] = {}
        for metric in metrics:
            pairs = [
                (
                    float(row["orchard_minus_no_orchard"][metric]),
                    1.0 if weight_field is None else float(row[weight_field]),
                )
                for row in rows
            ]
            schemes[scheme][metric] = weighted(pairs)

    return {
        "common_opponents": len(common),
        "orchard_games_on_common_opponents": sum(len(orchard[key]) for key in common),
        "no_orchard_games_on_common_opponents": sum(len(no_orchard[key]) for key in common),
        "opponent_id_jaccard": len(common) / len(set(orchard) | set(no_orchard)),
        "standardized_differences": schemes,
        "per_opponent": rows,
    }


def bootstrap_opponents(
    rows: list[dict[str, Any]], repetitions: int, seed: int
) -> dict[str, Any]:
    if not rows:
        return {}
    rng = random.Random(seed)
    metrics = ("win_rate", "our_score", "opponent_score", "margin", "catastrophe_rate")
    draws = {metric: [] for metric in metrics}
    for _ in range(repetitions):
        sample = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        for metric in metrics:
            draws[metric].append(
                statistics.mean(
                    float(row["orchard_minus_no_orchard"][metric]) for row in sample
                )
            )
    result = {}
    for metric, values in draws.items():
        values.sort()
        result[metric] = {
            "lower_95": values[int(0.025 * repetitions)],
            "median": values[repetitions // 2],
            "upper_95": values[min(repetitions - 1, int(0.975 * repetitions))],
            "probability_le_zero": sum(value <= 0 for value in values) / repetitions,
        }
    return {"repetitions": repetitions, "seed": seed, "equal_opponent": result}


def build_report(
    orchard_payload: dict[str, Any],
    no_orchard_payload: dict[str, Any],
    repetitions: int,
) -> dict[str, Any]:
    orchard_rows = orchard_payload["rows"]
    no_orchard_rows = no_orchard_payload["rows"]
    orchard_groups = groups(orchard_rows)
    no_orchard_groups = groups(no_orchard_rows)
    standard = standardized(orchard_groups, no_orchard_groups)
    standard["opponent_cluster_bootstrap"] = bootstrap_opponents(
        standard["per_opponent"], repetitions, 2026080301
    )
    orchard_summary = summarize(orchard_rows)
    no_orchard_summary = summarize(no_orchard_rows)
    raw_difference = {
        key: orchard_summary[key] - no_orchard_summary[key]
        for key in (
            "win_rate",
            "nonloss_rate",
            "mean_our_score",
            "mean_opponent_score",
            "mean_margin",
            "catastrophe_rate",
            "negative_margin_mass",
        )
    }
    return {
        "schema": "troll-farm-orchard-ablation-checkpoint-analysis/1",
        "identity": {
            "orchard": {
                "agent_id": orchard_payload["agent_id"],
                "submission_id": orchard_payload["submission_id"],
                "score": orchard_payload["arena"]["score"],
                "rank": orchard_payload["arena"]["rank"],
                "field_size": orchard_payload["arena"]["total"],
            },
            "no_orchard": {
                "agent_id": no_orchard_payload["agent_id"],
                "submission_id": no_orchard_payload["submission_id"],
                "score": no_orchard_payload["arena"]["score"],
                "rank": no_orchard_payload["arena"]["rank"],
                "field_size": no_orchard_payload["arena"]["total"],
            },
        },
        "fresh_ladder_difference": {
            "orchard_minus_no_orchard_score": orchard_payload["arena"]["score"]
            - no_orchard_payload["arena"]["score"],
            "orchard_rank_minus_no_orchard_rank": orchard_payload["arena"]["rank"]
            - no_orchard_payload["arena"]["rank"],
        },
        "raw": {
            "orchard": orchard_summary,
            "no_orchard": no_orchard_summary,
            "orchard_minus_no_orchard": raw_difference,
        },
        "opponent_standardized": standard,
        "historical_context": {
            "old_orchard_score": 25.3,
            "old_orchard_rank": 12,
            "warning": (
                "the old and freshly restored orchard agents use the same exact E7a source but "
                "differ by 1.74 ladder score and 20 rank places; old rank 12 is not a clean source control"
            ),
        },
        "causal_boundary": {
            "randomized": False,
            "paired_maps": False,
            "paired_opponents": False,
            "rating_formula_reconstructed": False,
            "allowed_claim": "observational source comparison after opponent standardization",
            "forbidden_claim": "rank 12 to rank 34 is the orchard treatment effect",
        },
    }


def render(report: dict[str, Any]) -> str:
    orchard = report["identity"]["orchard"]
    no = report["identity"]["no_orchard"]
    raw = report["raw"]
    standardized_rows = report["opponent_standardized"]["standardized_differences"]
    bootstrap = report["opponent_standardized"]["opponent_cluster_bootstrap"]["equal_opponent"]
    lines = [
        "# Orchard ablation: fresh-queue opponent-standardized comparison",
        "",
        "## Identity and headline correction",
        "",
        f"- orchard: `{orchard['agent_id']}` / `{orchard['submission_id']}`, "
        f"score {orchard['score']}, rank {orchard['rank']}/{orchard['field_size']};",
        f"- no orchard: `{no['agent_id']}` / `{no['submission_id']}`, "
        f"score {no['score']}, rank {no['rank']}/{no['field_size']};",
        f"- fresh difference: {report['fresh_ladder_difference']['orchard_minus_no_orchard_score']:+.2f} "
        "score and two rank places in favor of orchard.",
        "",
        "The earlier rank-12 orchard row is not a clean control: the exact same source's fresh restore "
        "landed at rank 32. The apparent rank-12 to rank-34 drop therefore mixes source, reset, "
        "matchmaking and queue effects.",
        "",
        "## Raw outcomes",
        "",
        "| metric | orchard | no orchard | orchard - no orchard |",
        "|---|---:|---:|---:|",
    ]
    for label, key in (
        ("games", "games"),
        ("win rate", "win_rate"),
        ("mean own score", "mean_our_score"),
        ("mean opponent score", "mean_opponent_score"),
        ("mean margin", "mean_margin"),
        ("catastrophe rate", "catastrophe_rate"),
        ("negative-margin mass", "negative_margin_mass"),
    ):
        left = raw["orchard"][key]
        right = raw["no_orchard"][key]
        delta = left - right
        lines.append(f"| {label} | {left:.4f} | {right:.4f} | {delta:+.4f} |")
    lines += [
        "",
        "Raw outcomes favor no-orchard on wins and tails. They do not explain the ladder score, "
        "which is not a direct transform of terminal margin and is sensitive to opponent mixture.",
        "",
        "## Common-opponent standardization",
        "",
        f"Common exact opponents: {report['opponent_standardized']['common_opponents']}; "
        f"opponent-set Jaccard {report['opponent_standardized']['opponent_id_jaccard']:.3f}.",
        "",
        "| weighting | win-rate diff | own-score diff | opponent-score diff | margin diff | catastrophe-rate diff |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scheme, values in standardized_rows.items():
        lines.append(
            f"| {scheme} | {values['win_rate']:+.4f} | {values['our_score']:+.3f} | "
            f"{values['opponent_score']:+.3f} | {values['margin']:+.3f} | "
            f"{values['catastrophe_rate']:+.4f} |"
        )
    lines += [
        "",
        "Equal-opponent cluster bootstrap (orchard minus no-orchard):",
        "",
        "| metric | lower 95% | median | upper 95% | P(diff <= 0) |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric, values in bootstrap.items():
        lines.append(
            f"| {metric} | {values['lower_95']:+.4f} | {values['median']:+.4f} | "
            f"{values['upper_95']:+.4f} | {values['probability_le_zero']:.4f} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This is an observational comparison. It can show whether opponent composition explains the "
        "raw result, but it cannot identify orchard value on identical map/opponent/seat states. "
        "A replay-level mechanism join and paired local continuation are required for that.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-orchard", type=Path, default=DEFAULT_NO_ORCHARD)
    parser.add_argument("--orchard", type=Path, default=DEFAULT_ORCHARD)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--bootstrap", type=int, default=100_000)
    args = parser.parse_args()
    no_orchard = load(args.no_orchard, 6592097, 41085842)
    orchard = load(args.orchard, 6592131, 41086057)
    report = build_report(orchard, no_orchard, args.bootstrap)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(render(report) + "\n")
    print(
        "fresh orchard minus no-orchard:",
        report["fresh_ladder_difference"],
        "common opponents:",
        report["opponent_standardized"]["common_opponents"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
