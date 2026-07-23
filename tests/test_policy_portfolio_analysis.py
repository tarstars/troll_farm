from cgauto.policy_portfolio_analysis import (
    evaluate_selector,
    fit_decision_stump,
    fit_maximin_mixture,
    selector_vs_policy_summary,
    simplex_weights,
)


def test_simplex_weights_sum_to_units() -> None:
    weights = list(simplex_weights(3, 4))

    assert len(weights) == 15
    assert all(sum(row) == 4 for row in weights)


def test_stump_recovers_two_policy_feature_split() -> None:
    seeds = list(range(10))
    features = {seed: {"trees": seed} for seed in seeds}
    outcomes = {
        seed: {
            "left": 5 if seed <= 4 else -5,
            "live": 0,
            "right": -5 if seed <= 4 else 5,
        }
        for seed in seeds
    }

    stump, _ = fit_decision_stump(
        seeds, features, outcomes, ["left", "live", "right"]
    )

    assert stump["feature"] == "trees"
    assert stump["threshold"] == 4.5
    assert stump["left_policy"] == "left"
    assert stump["right_policy"] == "right"
    assert stump["train_mean_delta"] == 5


def test_maximin_mix_balances_complementary_policies() -> None:
    matrix = {
        "a": {"x": 2, "y": -2},
        "b": {"x": -2, "y": 2},
    }

    result = fit_maximin_mixture(matrix, ["a", "b"], ["x", "y"], 0.5)

    assert result["weights"] == {"a": 0.5, "b": 0.5}
    assert result["worst_opponent_delta"] == 0


def test_maximin_tie_defaults_to_live_control() -> None:
    matrix = {
        "candidate": {"x": 0, "y": 0},
        "live": {"x": 0, "y": 0},
    }

    result = fit_maximin_mixture(
        matrix, ["candidate", "live"], ["x", "y"], 0.5
    )

    assert result["weights"] == {"candidate": 0.0, "live": 1.0}


def test_selector_comparison_remains_paired_by_seed() -> None:
    seeds = [0, 1]
    features = {0: {"fruit": 0}, 1: {"fruit": 1}}
    outcomes = {
        0: {"candidate": 12, "global": 10},
        1: {"candidate": 102, "global": 100},
    }
    stump = {
        "feature": None,
        "threshold": None,
        "left_policy": "candidate",
        "right_policy": "candidate",
    }

    selector = evaluate_selector(seeds, stump, features, outcomes)
    comparison = selector_vs_policy_summary(selector, outcomes, "global")

    assert comparison["mean"] == 2
    assert comparison["minimum"] == 2
    assert comparison["maximum"] == 2
