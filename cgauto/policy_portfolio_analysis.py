#!/usr/bin/env python3
"""Cross-validate a map-conditioned policy stump and a maximin policy mixture."""

from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.offline_policy_league import robust_summary  # noqa: E402


def seed_policy_outcomes(payload: dict) -> dict[int, dict[str, float]]:
    grouped = {}
    for row in payload["rows"]:
        grouped.setdefault((row["seed"], row["policy"]), []).append(
            row["delta_vs_live_margin"]
        )
    outcomes = {}
    for (seed, policy), values in grouped.items():
        outcomes.setdefault(seed, {})[policy] = statistics.mean(values)
    return outcomes


def choose_leaf_policy(seeds, outcomes, policies) -> tuple[str, float]:
    means = {
        policy: statistics.mean(outcomes[seed][policy] for seed in seeds)
        for policy in policies
    }
    policy = max(policies, key=lambda name: (means[name], name == "live", name))
    return policy, means[policy]


def fit_decision_stump(
    train_seeds: list[int], features: dict[int, dict], outcomes: dict, policies: list[str]
) -> tuple[dict, list[dict]]:
    min_leaf = max(3, len(train_seeds) // 5)
    candidates = []
    feature_names = sorted(next(iter(features.values())))
    for feature in feature_names:
        values = sorted({features[seed][feature] for seed in train_seeds})
        thresholds = [(left + right) / 2 for left, right in zip(values, values[1:])]
        for threshold in thresholds:
            left = [seed for seed in train_seeds if features[seed][feature] <= threshold]
            right = [seed for seed in train_seeds if features[seed][feature] > threshold]
            if min(len(left), len(right)) < min_leaf:
                continue
            left_policy, left_mean = choose_leaf_policy(left, outcomes, policies)
            right_policy, right_mean = choose_leaf_policy(right, outcomes, policies)
            selected = [
                outcomes[seed][left_policy if seed in left else right_policy]
                for seed in train_seeds
            ]
            candidates.append(
                {
                    "feature": feature,
                    "threshold": threshold,
                    "left_policy": left_policy,
                    "right_policy": right_policy,
                    "left_n": len(left),
                    "right_n": len(right),
                    "left_train_mean": left_mean,
                    "right_train_mean": right_mean,
                    "train_mean_delta": statistics.mean(selected),
                    "train_worst_decile_mean": robust_summary(selected)[
                        "worst_decile_mean"
                    ],
                }
            )
    candidates.sort(
        key=lambda row: (
            row["train_mean_delta"],
            row["train_worst_decile_mean"],
            row["feature"],
            -row["threshold"],
        ),
        reverse=True,
    )
    if not candidates:
        policy, mean = choose_leaf_policy(train_seeds, outcomes, policies)
        return {
            "feature": None,
            "threshold": None,
            "left_policy": policy,
            "right_policy": policy,
            "left_n": len(train_seeds),
            "right_n": 0,
            "train_mean_delta": mean,
        }, []
    return candidates[0], candidates[:10]


def stump_policy(stump: dict, feature_row: dict) -> str:
    if stump["feature"] is None:
        return stump["left_policy"]
    if feature_row[stump["feature"]] <= stump["threshold"]:
        return stump["left_policy"]
    return stump["right_policy"]


def evaluate_selector(seeds, stump, features, outcomes) -> dict:
    rows = []
    for seed in seeds:
        policy = stump_policy(stump, features[seed])
        rows.append(
            {
                "seed": seed,
                "policy": policy,
                "delta_vs_live_margin": outcomes[seed][policy],
            }
        )
    return {
        "summary": robust_summary(row["delta_vs_live_margin"] for row in rows),
        "policy_counts": dict(sorted(Counter(row["policy"] for row in rows).items())),
        "rows": rows,
    }


def selector_vs_policy_summary(selector: dict, outcomes: dict, policy: str) -> dict:
    """Keep the comparison paired by map seed instead of comparing two means."""

    return robust_summary(
        row["delta_vs_live_margin"] - outcomes[row["seed"]][policy]
        for row in selector["rows"]
    )


def split_payoff_matrix(payload, seeds, policies, opponents) -> dict[str, dict[str, float]]:
    seed_set = set(seeds)
    grouped = {}
    for row in payload["rows"]:
        if row["seed"] in seed_set:
            grouped.setdefault((row["policy"], row["opponent"]), []).append(
                row["delta_vs_live_margin"]
            )
    return {
        policy: {
            opponent: statistics.mean(grouped[(policy, opponent)])
            for opponent in opponents
        }
        for policy in policies
    }


def simplex_weights(count: int, units: int):
    if count == 1:
        yield (units,)
        return
    for first in range(units + 1):
        for rest in simplex_weights(count - 1, units - first):
            yield (first,) + rest


def evaluate_mixture(weights: dict[str, float], matrix: dict, opponents) -> dict:
    opponent_payoffs = {
        opponent: sum(
            weights[policy] * matrix[policy][opponent] for policy in weights
        )
        for opponent in opponents
    }
    return {
        "weights": weights,
        "opponent_expected_deltas": opponent_payoffs,
        "worst_opponent_delta": min(opponent_payoffs.values()),
        "mean_opponent_delta": statistics.mean(opponent_payoffs.values()),
    }


def fit_maximin_mixture(matrix, policies, opponents, step: float) -> dict:
    units = round(1 / step)
    if not math.isclose(units * step, 1.0):
        raise ValueError("mixture step must divide one exactly")
    best = None
    for integer_weights in simplex_weights(len(policies), units):
        weights = {
            policy: weight / units
            for policy, weight in zip(policies, integer_weights)
        }
        result = evaluate_mixture(weights, matrix, opponents)
        key = (
            result["worst_opponent_delta"],
            result["mean_opponent_delta"],
            weights.get("live", 0.0),
        )
        if best is None or key > best[0]:
            best = (key, result)
    assert best is not None
    return best[1]


def oracle_summary(seeds, outcomes, policies) -> dict:
    values = []
    counts = Counter()
    for seed in seeds:
        policy = max(policies, key=lambda name: (outcomes[seed][name], name))
        counts[policy] += 1
        values.append(outcomes[seed][policy])
    return {"summary": robust_summary(values), "policy_counts": dict(sorted(counts.items()))}


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/offline-policy-league-2026-07-16.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/policy-portfolio-analysis-2026-07-16.json",
    )
    parser.add_argument("--mixture-step", type=float, default=0.05)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    policies = sorted(payload["policies"])
    opponents = sorted(payload["opponents"])
    outcomes = seed_policy_outcomes(payload)
    features = {
        int(seed): feature_row for seed, feature_row in payload["map_features"].items()
    }
    seeds = sorted(outcomes)
    train_seeds = [seed for seed in seeds if seed % 2 == 0]
    test_seeds = [seed for seed in seeds if seed % 2 == 1]
    if not train_seeds or not test_seeds:
        raise SystemExit("need at least one even and one odd seed")

    pure = {}
    for policy in policies:
        pure[policy] = {
            "train": robust_summary(outcomes[seed][policy] for seed in train_seeds),
            "test": robust_summary(outcomes[seed][policy] for seed in test_seeds),
        }
    train_best_global = max(
        policies,
        key=lambda policy: (
            pure[policy]["train"]["mean"],
            policy == "live",
            policy,
        ),
    )
    stump, top_candidates = fit_decision_stump(
        train_seeds, features, outcomes, policies
    )
    selector_train = evaluate_selector(train_seeds, stump, features, outcomes)
    selector_test = evaluate_selector(test_seeds, stump, features, outcomes)
    selector_vs_global_train = selector_vs_policy_summary(
        selector_train, outcomes, train_best_global
    )
    selector_vs_global_test = selector_vs_policy_summary(
        selector_test, outcomes, train_best_global
    )

    train_matrix = split_payoff_matrix(
        payload, train_seeds, policies, opponents
    )
    test_matrix = split_payoff_matrix(payload, test_seeds, policies, opponents)
    mixture_train = fit_maximin_mixture(
        train_matrix, policies, opponents, args.mixture_step
    )
    mixture_test = evaluate_mixture(
        mixture_train["weights"], test_matrix, opponents
    )

    result = {
        "schema": 1,
        "scope": "even-seed training; odd-seed untouched test; turn-1 features only",
        "source": str(args.input),
        "split": {"train_seeds": train_seeds, "test_seeds": test_seeds},
        "pure_policy_delta_vs_live": pure,
        "training_selected_global_policy": train_best_global,
        "stump": stump,
        "top_training_stumps": top_candidates,
        "selector_train": selector_train,
        "selector_test": selector_test,
        "selector_vs_training_selected_global": {
            "policy": train_best_global,
            "train": selector_vs_global_train,
            "test": selector_vs_global_test,
        },
        "selector_gate": {
            "beats_live_on_test": selector_test["summary"]["mean"] > 0,
            "trimmed_mean_beats_live_on_test": (
                selector_test["summary"]["trimmed_5pct_mean"] > 0
            ),
            "paired_mean_beats_training_selected_global_on_test": (
                selector_vs_global_test["mean"] > 0
            ),
            "paired_trimmed_mean_beats_training_selected_global_on_test": (
                selector_vs_global_test["trimmed_5pct_mean"] > 0
            ),
            "passed": (
                selector_test["summary"]["mean"] > 0
                and selector_test["summary"]["trimmed_5pct_mean"] > 0
                and selector_vs_global_test["mean"] > 0
                and selector_vs_global_test["trimmed_5pct_mean"] > 0
            ),
            "promotion_ready": (
                selector_test["summary"]["ci95_normal"][0] > 0
                and selector_test["summary"]["worst_decile_mean"] >= 0
            ),
        },
        "oracle_upper_bound": {
            "train": oracle_summary(train_seeds, outcomes, policies),
            "test": oracle_summary(test_seeds, outcomes, policies),
        },
        "maximin": {
            "step": args.mixture_step,
            "train_matrix": train_matrix,
            "test_matrix": test_matrix,
            "selected_on_train": mixture_train,
            "evaluation_on_test": mixture_test,
            "test_worst_opponent_improves_live": mixture_test[
                "worst_opponent_delta"
            ]
            > 0,
        },
    }
    save(args.output, result)
    print(json.dumps({
        "stump": stump,
        "selector_gate": result["selector_gate"],
        "selector_test": selector_test["summary"],
        "maximin_train": mixture_train,
        "maximin_test": mixture_test,
    }, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
