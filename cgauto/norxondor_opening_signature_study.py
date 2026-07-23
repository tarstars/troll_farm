#!/usr/bin/env python3
"""Test whether observable opponent training signatures arrive before worker three."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto.norxondor_portfolio_upper_bound import RESIDENT, THREE_WORKER
from cgauto.norxondor_research_rollout_study import atomic_write, summary


INTEGER_FIELDS = (
    "seed",
    "seat",
    "margin",
    "candidate_second_worker_turn",
    "candidate_third_worker_turn",
    "opponent_second_worker_turn",
    "opponent_second_ms",
    "opponent_second_cc",
    "opponent_second_hp",
    "opponent_second_chop",
)


def read_instrumented_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                if field not in row:
                    raise ValueError(f"instrumented field {field!r} is absent")
                row[field] = int(row[field])
            rows.append(row)
    return rows


def turn_band(turn: int) -> str:
    if turn <= 4:
        return "00-04"
    if turn <= 15:
        return "05-15"
    if turn <= 30:
        return "16-30"
    if turn <= 60:
        return "31-60"
    return "61+"


def signature(row: dict, include_turn: bool = True) -> tuple:
    observed = row["opponent_second_worker_turn"]
    commitment = row["candidate_third_worker_turn"]
    if observed < 0 or commitment < 0 or observed >= commitment:
        return ("unobserved",)
    stats = (
        row["opponent_second_ms"],
        row["opponent_second_cc"],
        row["opponent_second_hp"],
        row["opponent_second_chop"],
    )
    return (turn_band(observed), *stats) if include_turn else stats


def cross_validated_safe_selector(
    rows: list[dict], labels: dict[str, str], include_turn: bool, minimum_support: int = 3
) -> dict:
    predictions = []
    for fold in range(5):
        train = [row for row in rows if row["seed"] % 5 != fold]
        held = [row for row in rows if row["seed"] % 5 == fold]
        counts: dict[tuple, Counter] = defaultdict(Counter)
        for row in train:
            counts[signature(row, include_turn)][labels[row["opponent"]]] += 1
        safe = {
            token
            for token, token_counts in counts.items()
            if token != ("unobserved",)
            and token_counts[THREE_WORKER] >= minimum_support
            and token_counts[RESIDENT] == 0
        }
        for row in held:
            predicted = THREE_WORKER if signature(row, include_turn) in safe else RESIDENT
            predictions.append((row, predicted))

    actual_alternative = sum(labels[row["opponent"]] == THREE_WORKER for row, _ in predictions)
    actual_resident = len(predictions) - actual_alternative
    selected_alternative = sum(predicted == THREE_WORKER for _, predicted in predictions)
    true_alternative = sum(
        predicted == THREE_WORKER and labels[row["opponent"]] == THREE_WORKER
        for row, predicted in predictions
    )
    false_alternative = selected_alternative - true_alternative
    correct = sum(predicted == labels[row["opponent"]] for row, predicted in predictions)
    return {
        "predictions": predictions,
        "rows": len(predictions),
        "accuracy": correct / len(predictions),
        "alternative_recall": true_alternative / actual_alternative,
        "alternative_precision": (
            true_alternative / selected_alternative if selected_alternative else 1.0
        ),
        "false_alternative_rate_on_resident": false_alternative / actual_resident,
        "selected_alternative": selected_alternative,
        "true_alternative": true_alternative,
        "false_alternative": false_alternative,
    }


def analyze(rows: list[dict], labels: dict[str, str]) -> dict:
    relevant = [row for row in rows if row["candidate"] == THREE_WORKER]
    resident_rows = [row for row in rows if row["candidate"] == RESIDENT]
    alternative = {
        (row["opponent"], row["seed"], row["seat"]): row for row in relevant
    }
    resident = {
        (row["opponent"], row["seed"], row["seat"]): row for row in resident_rows
    }
    if not relevant or alternative.keys() != resident.keys():
        raise ValueError("resident and three-worker instrumented grids must be complete and paired")
    if set(labels) != {row["opponent"] for row in relevant}:
        raise ValueError("portfolio mapping does not cover the rollout opponents")

    timing = {}
    for opponent in sorted(labels):
        selected = [row for row in relevant if row["opponent"] == opponent]
        before = sum(
            row["opponent_second_worker_turn"] >= 0
            and row["opponent_second_worker_turn"] < row["candidate_third_worker_turn"]
            for row in selected
        )
        timing[opponent] = {
            "portfolio_branch": labels[opponent],
            "rows": len(selected),
            "signature_before_commitment": before,
            "coverage": before / len(selected),
            "median_opponent_observation_turn": statistics.median(
                row["opponent_second_worker_turn"] for row in selected
            ),
            "median_third_worker_turn": statistics.median(
                row["candidate_third_worker_turn"] for row in selected
            ),
            "observed_specs": {
                "/".join(map(str, token)): count
                for token, count in sorted(
                    Counter(
                        (
                            row["opponent_second_ms"],
                            row["opponent_second_cc"],
                            row["opponent_second_hp"],
                            row["opponent_second_chop"],
                        )
                        for row in selected
                    ).items()
                )
            },
        }

    selectors = {}
    for name, include_turn in (("spec_only", False), ("turn_band_and_spec", True)):
        result = cross_validated_safe_selector(relevant, labels, include_turn)
        deltas = []
        by_opponent: dict[str, list[int]] = defaultdict(list)
        for row, predicted in result.pop("predictions"):
            key = (row["opponent"], row["seed"], row["seat"])
            chosen = alternative[key] if predicted == THREE_WORKER else resident[key]
            delta = chosen["margin"] - resident[key]["margin"]
            deltas.append(delta)
            by_opponent[row["opponent"]].append(delta)
        opponent_deltas = {
            opponent: statistics.mean(values)
            for opponent, values in sorted(by_opponent.items())
        }
        result.update(
            {
                "paired_margin_delta_vs_resident": summary(deltas),
                "opponent_mean_margin_deltas": opponent_deltas,
                "worst_opponent_mean_delta": min(opponent_deltas.values()),
            }
        )
        selectors[name] = result

    selected = selectors["turn_band_and_spec"]
    alternative_timing = [
        row
        for row in relevant
        if labels[row["opponent"]] == THREE_WORKER
    ]
    alternative_timing_coverage = sum(
        row["opponent_second_worker_turn"] >= 0
        and row["opponent_second_worker_turn"] < row["candidate_third_worker_turn"]
        for row in alternative_timing
    ) / len(alternative_timing)
    gate = (
        alternative_timing_coverage >= 0.95
        and selected["paired_margin_delta_vs_resident"]["mean"] > 0
        and selected["false_alternative_rate_on_resident"] <= 0.05
        and selected["worst_opponent_mean_delta"] >= -5
    )
    return {
        "schema": 1,
        "scope": (
            "generated-map exact-engine timing and observable-signature study; opponent names "
            "are used only as training labels, and fivefold predictions use first successful "
            "opponent TRAIN stats visible strictly before the third-worker commitment"
        ),
        "rows": len(relevant),
        "seeds": len({row["seed"] for row in relevant}),
        "portfolio_labels": labels,
        "timing_by_opponent": timing,
        "alternative_signature_timing_coverage": alternative_timing_coverage,
        "safe_selectors": selectors,
        "research_gate": {
            "requirements": [
                "at least 95% of alternative-label signatures visible before worker three",
                "positive cross-validated paired margin delta versus resident",
                "false alternative rate on resident labels at most 5%",
                "worst opponent mean margin delta at least -5",
            ],
            "passed": gate,
        },
        "decision": {
            "build_delayed_common_prefix_prototype": gate,
            "build_online_selector": False,
            "build_submission_candidate": False,
            "reason": (
                "A signature can authorize only the research common-prefix experiment. The "
                "standalone resident and Silver-based three-worker policy diverge before the "
                "classification point, so their label-aware portfolio gain is not directly "
                "deployable."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--portfolio", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    portfolio = json.loads(args.portfolio.read_text())
    payload = analyze(read_instrumented_rows(args.input), portfolio["frozen_selector"])
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "rows": payload["rows"],
        "alternative_timing_coverage": payload[
            "alternative_signature_timing_coverage"
        ],
        "selectors": {
            name: {
                "accuracy": report["accuracy"],
                "alternative_recall": report["alternative_recall"],
                "alternative_precision": report["alternative_precision"],
                "false_alternative_rate": report["false_alternative_rate_on_resident"],
                "margin_gain": report["paired_margin_delta_vs_resident"]["mean"],
                "worst_opponent": report["worst_opponent_mean_delta"],
            }
            for name, report in payload["safe_selectors"].items()
        },
        "gate": payload["research_gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
