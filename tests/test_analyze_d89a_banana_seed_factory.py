from cgauto.analyze_d89a_banana_seed_factory import (
    cohort_summary,
    lower_empirical_quantile,
    negative_margin_mass,
    normal_ci,
)


def test_lower_empirical_quantile_uses_frozen_lower_order_statistic() -> None:
    assert lower_empirical_quantile(range(10), 0.10) == 0
    assert lower_empirical_quantile(range(11), 0.10) == 1


def test_normal_ci_is_degenerate_for_single_value() -> None:
    assert normal_ci([3.5]) == [3.5, 3.5]


def test_normal_ci_contains_sample_mean() -> None:
    interval = normal_ci([0.0, 1.0, 2.0, 3.0])
    assert interval is not None
    assert interval[0] < 1.5 < interval[1]


def synthetic_pair(delta: int, resident_margin: int = -10) -> dict:
    return {
        "initial_budget": 5,
        "bootstrap_attempts": 5,
        "bootstrap_successes": 5,
        "harvest_successes": 3,
        "renewable_plant_successes": 2,
        "resident": {"margin": resident_margin},
        "candidate": {"margin": resident_margin + delta},
        "delta": {
            "margin": delta,
            "score": delta + 1,
            "opponent_score": 1,
            "wood": 2,
            "owned_chop_wood": 3,
            "plants": 4,
            "own_crop_harvest": 5,
        },
    }


def test_cohort_summary_retains_value_and_mechanism_counts() -> None:
    summary = cohort_summary([synthetic_pair(4), synthetic_pair(-2)])
    assert summary["n"] == 2
    assert summary["bootstrap_successes"] == 10
    assert summary["renewable_plant_successes"] == 4
    assert summary["mean_margin_delta"] == 1
    assert summary["improved"] == 1
    assert summary["regressed"] == 1


def test_negative_margin_mass_counts_each_loss_once() -> None:
    pairs = [synthetic_pair(4, -10), synthetic_pair(-2, 3)]
    assert negative_margin_mass(pairs, "resident") == 10
    assert negative_margin_mass(pairs, "candidate") == 6
