#!/usr/bin/env python3
"""Validate and classify the frozen D22 one-action Monte Carlo diagnostic."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d22_d21_disagreement_mc import (  # noqa: E402
    BASELINE_SHA256,
    EPISODES,
    PROPOSAL_SHA256,
    SEED_BASE,
    SEED_STOP,
    TURN_BANDS,
)
from cgauto.rl_level6_env import LEVEL6_OPPONENT_NAMES  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_tree(value: object) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(child) for child in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(child) for child in value)
    return True


def summary(values: list[float]) -> dict:
    array = np.asarray(values, dtype=np.float64)
    if not len(array):
        return {"n": 0}
    ordered = np.sort(array)
    worst_count = max(1, len(array) // 10)
    quantiles = np.quantile(array, [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95])
    return {
        "n": len(array),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
        "positive_rate": float(np.mean(array > 0)),
        "zero_rate": float(np.mean(array == 0)),
        "negative_rate": float(np.mean(array < 0)),
        "gain_at_least_10_rate": float(np.mean(array >= 10)),
        "loss_at_most_minus_10_rate": float(np.mean(array <= -10)),
        "worst_decile_mean": float(ordered[:worst_count].mean()),
        "quantiles": {
            "q05": float(quantiles[0]),
            "q10": float(quantiles[1]),
            "q25": float(quantiles[2]),
            "q50": float(quantiles[3]),
            "q75": float(quantiles[4]),
            "q90": float(quantiles[5]),
            "q95": float(quantiles[6]),
        },
    }


def grouped_summary(rows: list[dict], field: str) -> dict:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row["advantage"])
    return {key: summary(values) for key, values in sorted(groups.items())}


def classify(
    *,
    readiness_pass: bool,
    mean_advantage: float,
    positive_rate: float,
    gain_at_least_10_rate: float,
    nonnegative_opponent_means: int,
    gain_opponent_coverage: int,
    gain_recipe_coverage: int,
    new_catastrophe_rate: float,
) -> str:
    if not readiness_pass:
        return "invalid_readiness"
    if (
        mean_advantage > 0
        and nonnegative_opponent_means >= 4
        and positive_rate >= 0.30
        and new_catastrophe_rate <= 0.01
    ):
        return "compounding_distribution_failure"
    if mean_advantage <= 0 and gain_at_least_10_rate < 0.20:
        return "direct_proposal_harm"
    if (
        gain_at_least_10_rate >= 0.20
        and gain_opponent_coverage >= 5
        and gain_recipe_coverage >= 6
        and new_catastrophe_rate <= 0.02
    ):
        return "mixed_sparse_opportunity"
    return "mixed_unsafe"


def validate_terminal_rows(rows: list[dict], label: str) -> None:
    if [row.get("seed") for row in rows] != list(range(SEED_BASE, SEED_STOP)):
        raise ValueError(f"{label} seed coverage mismatch")


def analyze(payload: dict) -> dict:
    config = payload.get("config", {})
    if (
        config.get("seed_base") != SEED_BASE
        or config.get("seed_stop_exclusive") != SEED_STOP
        or config.get("episodes") != EPISODES
        or config.get("num_envs") != EPISODES
        or config.get("max_turns") != 300
        or config.get("turn_bands") != [list(band) for band in TURN_BANDS]
        or config.get("baseline_checkpoint_sha256") != BASELINE_SHA256
        or config.get("proposal_checkpoint_sha256") != PROPOSAL_SHA256
    ):
        raise ValueError("D22 frozen configuration mismatch")
    discovery = payload["discovery"]
    repeat = payload["baseline_repeat"]
    validate_terminal_rows(discovery["terminal_rows"], "discovery baseline")
    validate_terminal_rows(repeat["terminal_rows"], "repeat baseline")
    arms = sorted(payload["arms"], key=lambda arm: arm["label"])
    if [arm["label"] for arm in arms] != [f"band_{band}" for band in range(4)]:
        raise ValueError("D22 arm set mismatch")
    for arm in arms:
        validate_terminal_rows(arm["terminal_rows"], arm["label"])

    events = discovery["selected_events"]
    outcomes = [row for arm in arms for row in arm["outcomes"]]
    event_keys = [(row["seed"], row["band"]) for row in events]
    outcome_keys = [(row["seed"], row["band"]) for row in outcomes]
    if len(set(event_keys)) != len(event_keys) or sorted(event_keys) != sorted(outcome_keys):
        raise ValueError("D22 event/outcome identity mismatch")
    selected_by_band = Counter(row["band"] for row in events)
    opponent_coverage = Counter(row["opponent"] for row in outcomes)
    recipe_coverage = Counter(str(row["recipe_id"]) for row in outcomes)

    baseline_exact = discovery["terminal_rows"] == repeat["terminal_rows"]
    all_terminal_legal_finite = (
        finite_tree(payload)
        and repeat["illegal_actions"] == 0
        and not repeat["violations"]
        and all(arm["illegal_actions"] == 0 and not arm["violations"] for arm in arms)
        and all(
            row["turn"] == 300 and row["return_margin_error"] <= 1e-4
            for row in discovery["terminal_rows"] + repeat["terminal_rows"]
        )
        and all(
            row["turn"] == 300 and row["return_margin_error"] <= 1e-4
            for arm in arms
            for row in arm["terminal_rows"]
        )
    )
    readiness_gates = {
        "all_d11_runs_exact_legal_and_identical": (
            baseline_exact
            and discovery["baseline_illegal_actions"] == 0
            and repeat["illegal_actions"] == 0
        ),
        "proposal_legal_on_every_shared_state": discovery["proposal_illegal_actions"]
        == 0,
        "at_least_480_events_and_80_per_band": (
            len(events) >= 480
            and all(selected_by_band[band] >= 80 for band in range(4))
        ),
        "opponent_and_recipe_coverage": (
            set(opponent_coverage) == set(LEVEL6_OPPONENT_NAMES)
            and min(opponent_coverage.values()) >= 40
            and set(recipe_coverage) == {str(recipe) for recipe in range(8)}
            and min(recipe_coverage.values()) >= 25
        ),
        "counterfactual_replays_legal_finite_turn300_and_exact_return": (
            all_terminal_legal_finite
        ),
    }
    readiness_pass = all(readiness_gates.values())

    advantages = [row["advantage"] for row in outcomes]
    overall = summary(advantages)
    by_band = grouped_summary(outcomes, "band")
    by_opponent = grouped_summary(outcomes, "opponent")
    by_recipe = grouped_summary(outcomes, "recipe_id")
    by_transition = grouped_summary(
        [
            {**row, "transition": f"{row['baseline_plane']}->{row['proposal_plane']}"}
            for row in outcomes
        ],
        "transition",
    )
    gain_rows = [row for row in outcomes if row["advantage"] >= 10]
    new_catastrophe_rate = sum(row["new_catastrophe"] for row in outcomes) / len(
        outcomes
    )
    nonnegative_opponent_means = sum(
        bucket["mean"] >= 0 for bucket in by_opponent.values()
    )
    classification = classify(
        readiness_pass=readiness_pass,
        mean_advantage=overall["mean"],
        positive_rate=overall["positive_rate"],
        gain_at_least_10_rate=overall["gain_at_least_10_rate"],
        nonnegative_opponent_means=nonnegative_opponent_means,
        gain_opponent_coverage=len({row["opponent"] for row in gain_rows}),
        gain_recipe_coverage=len({row["recipe_id"] for row in gain_rows}),
        new_catastrophe_rate=new_catastrophe_rate,
    )
    authorizations = {
        "invalid_readiness": "repair instrumentation only; draw no policy conclusion",
        "compounding_distribution_failure": (
            "design a separately frozen sparse commitment/residual study only"
        ),
        "direct_proposal_harm": "close the D21 action proposal",
        "mixed_sparse_opportunity": (
            "design a separately frozen confidence-gated distillation readiness study only"
        ),
        "mixed_unsafe": "close the D21 action proposal; no residual or distillation follows",
    }
    return {
        "schema": 1,
        "scope": (
            "D22 frozen one-action Monte Carlo diagnostic; no candidate, holdout, "
            "submission, or Arena authorization"
        ),
        "readiness_gates": readiness_gates,
        "readiness_pass": readiness_pass,
        "coverage": {
            "inspected_shared_states": discovery["inspected_states"],
            "raw_disagreements_by_band": discovery["raw_disagreements_by_band"],
            "selected_events": len(events),
            "selected_by_band": {str(key): value for key, value in selected_by_band.items()},
            "by_opponent": dict(opponent_coverage),
            "by_recipe": dict(recipe_coverage),
        },
        "metrics": {
            "overall_advantage": overall,
            "new_catastrophes": sum(row["new_catastrophe"] for row in outcomes),
            "new_catastrophe_rate": new_catastrophe_rate,
            "mean_own_score_delta": float(
                np.mean(
                    [row["alternative_own_score"] - row["baseline_own_score"] for row in outcomes]
                )
            ),
            "mean_opponent_score_delta": float(
                np.mean(
                    [
                        row["alternative_opponent_score"]
                        - row["baseline_opponent_score"]
                        for row in outcomes
                    ]
                )
            ),
            "nonnegative_opponent_means": nonnegative_opponent_means,
            "gain_at_least_10_opponent_coverage": len(
                {row["opponent"] for row in gain_rows}
            ),
            "gain_at_least_10_recipe_coverage": len(
                {row["recipe_id"] for row in gain_rows}
            ),
            "by_band": by_band,
            "by_opponent": by_opponent,
            "by_recipe": by_recipe,
            "by_action_plane_transition": by_transition,
        },
        "classification": classification,
        "authorization": authorizations[classification],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--protocol", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    result = analyze(payload)
    result["source"] = {
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "analyzer": str(Path(__file__).relative_to(REPO)),
        "analyzer_sha256": sha256(Path(__file__)),
    }
    if args.protocol is not None:
        result["source"]["protocol"] = str(args.protocol)
        result["source"]["protocol_sha256"] = sha256(args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "readiness_pass": result["readiness_pass"],
                "failed_readiness_gates": [
                    name
                    for name, passed in result["readiness_gates"].items()
                    if not passed
                ],
                "classification": result["classification"],
                "authorization": result["authorization"],
                "coverage": result["coverage"],
                "overall": result["metrics"]["overall_advantage"],
                "new_catastrophe_rate": result["metrics"]["new_catastrophe_rate"],
                "by_band": result["metrics"]["by_band"],
                "by_opponent": result["metrics"]["by_opponent"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
