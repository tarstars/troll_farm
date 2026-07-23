#!/usr/bin/env python3
"""Analyze paired local rollouts of Norxondor ladder/continuation prototypes."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics


CONTROLS = {
    "norx_compact": "compact_gold",
    "norx_cooperative_silver": "silver_boss",
    "norx_funded_silver": "silver_boss",
    "norx_silver": "silver_boss",
    "norx_resident_challenge": "resident",
    "norx_signature_portfolio": "resident",
    "norx_soft_cooperative_silver": "silver_boss",
    "norx_soft_resident_challenge": "resident",
    "norx_three_worker_silver": "silver_boss",
    "norx_three_worker_resident_challenge": "resident",
    "norx_native_three": "resident",
    "norx_native_full": "resident",
}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def read_rows(path: Path) -> list[dict]:
    integer_fields = (
        "seed",
        "seat",
        "margin",
        "score",
        "opponent_score",
        "wood",
        "workers",
        "train_attempts",
        "turn",
    )
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in integer_fields:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def summary(values) -> dict:
    values = list(values)
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
    }


def analyze(rows: list[dict]) -> dict:
    candidates = sorted({row["candidate"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    keys = [(row["opponent"], row["seed"], row["seat"]) for row in rows]
    expected = len(opponents) * len({row["seed"] for row in rows}) * 2
    for candidate in candidates:
        selected = [row for row in rows if row["candidate"] == candidate]
        if len(selected) != expected or len(
            {(row["opponent"], row["seed"], row["seat"]) for row in selected}
        ) != expected:
            raise ValueError(f"incomplete or duplicate grid for {candidate}")
    lookup = {
        (row["candidate"], row["opponent"], row["seed"], row["seat"]): row
        for row in rows
    }
    active_controls = {
        candidate: control
        for candidate, control in CONTROLS.items()
        if candidate in candidates and control in candidates
    }
    reports = {}
    for candidate in candidates:
        selected = [row for row in rows if row["candidate"] == candidate]
        report = {
            "margin": summary(row["margin"] for row in selected),
            "score": summary(row["score"] for row in selected),
            "wood": summary(row["wood"] for row in selected),
            "workers": summary(row["workers"] for row in selected),
            "worker_distribution": dict(
                sorted(Counter(row["workers"] for row in selected).items())
            ),
            "successful_trains": summary(row["workers"] - 1 for row in selected),
            "train_attempts": summary(row["train_attempts"] for row in selected),
            "by_opponent": {},
        }
        for opponent in opponents:
            cell = [row for row in selected if row["opponent"] == opponent]
            report["by_opponent"][opponent] = {
                "margin": summary(row["margin"] for row in cell),
                "score": summary(row["score"] for row in cell),
                "workers": summary(row["workers"] for row in cell),
            }
        if candidate in active_controls:
            control = active_controls[candidate]
            deltas = []
            score_deltas = []
            by_opponent = defaultdict(list)
            for row in selected:
                baseline = lookup[
                    (control, row["opponent"], row["seed"], row["seat"])
                ]
                delta = row["margin"] - baseline["margin"]
                deltas.append(delta)
                score_deltas.append(row["score"] - baseline["score"])
                by_opponent[row["opponent"]].append(delta)
            opponent_means = {
                opponent: statistics.mean(values)
                for opponent, values in sorted(by_opponent.items())
            }
            report["control"] = control
            report["delta_vs_control_margin"] = summary(deltas)
            report["delta_vs_control_score"] = summary(score_deltas)
            report["opponent_mean_margin_deltas"] = opponent_means
            report["nonnegative_opponent_deltas"] = sum(
                value >= 0 for value in opponent_means.values()
            )
            report["worst_opponent_mean_delta"] = min(opponent_means.values())
        reports[candidate] = report

    prototype_passes = []
    for candidate in active_controls:
        report = reports[candidate]
        if (
            report["workers"]["mean"] >= 2.5
            and report["delta_vs_control_score"]["mean"] >= 0
            and report["delta_vs_control_margin"]["mean"] >= 0
            and report["nonnegative_opponent_deltas"] >= 5
            and report["worst_opponent_mean_delta"] >= -5
        ):
            prototype_passes.append(candidate)
    return {
        "schema": 1,
        "scope": (
            "deterministic exact-engine Bronze map rollouts with seats swapped for every "
            "candidate/opponent/seed cell; replay-derived workforce ladder joined to two existing "
            "continuations and paired against each continuation control; discovery evidence only, "
            "not official-map, sealed-holdout, or arena evidence"
        ),
        "rows": len(rows),
        "seeds": len({row["seed"] for row in rows}),
        "opponents": opponents,
        "candidates": reports,
        "research_gate": {
            "requirements": [
                "mean final workforce at least 2.5",
                "nonnegative paired score and margin delta versus the same continuation",
                "nonnegative mean margin delta against at least five of eight opponents",
                "worst opponent mean margin delta at least -5",
            ],
            "passing_prototypes": prototype_passes,
            "passed": bool(prototype_passes),
        },
        "decision": {
            "build_integrated_controller": bool(prototype_passes),
            "selected_prototype": prototype_passes[0] if prototype_passes else None,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(read_rows(args.input))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "rows": payload["rows"],
        "seeds": payload["seeds"],
        "candidates": {
            name: {
                "margin": row["margin"]["mean"],
                "score": row["score"]["mean"],
                "workers": row["workers"]["mean"],
                "worker_distribution": row["worker_distribution"],
                "delta_margin": row.get("delta_vs_control_margin", {}).get("mean"),
                "delta_score": row.get("delta_vs_control_score", {}).get("mean"),
                "opponent_deltas": row.get("opponent_mean_margin_deltas"),
            }
            for name, row in payload["candidates"].items()
        },
        "gate": payload["research_gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
