from cgauto.portfolio_motion_followup import (
    branch_summary,
    evaluate_followup,
    null_adjusted_difference,
    seed_results,
)


def row(seed: int, policy: str, repetition: int, margin: float) -> dict:
    return {
        "seed": seed,
        "policy": policy,
        "repetition": repetition,
        "paired_margin": margin,
    }


def repeated(seed: int, policy: str, margin: float) -> list[dict]:
    return [row(seed, policy, repetition, margin) for repetition in range(5)]


def test_seed_results_average_repetitions_before_policy_delta() -> None:
    rows = repeated(1, "live", 2) + repeated(1, "portfolio", 5)

    result = seed_results(rows)

    assert result[0]["live_mean_margin"] == 2
    assert result[0]["portfolio_mean_margin"] == 5
    assert result[0]["delta_vs_live_margin"] == 3


def test_branch_summary_removes_largest_seed() -> None:
    results = [
        {"seed": 1, "delta_vs_live_margin": 2},
        {"seed": 2, "delta_vs_live_margin": 8},
    ]

    summary = branch_summary(results, {1, 2})

    assert summary["mean"] == 5
    assert summary["mean_without_largest"] == 2


def test_null_adjusted_difference_uses_both_branch_uncertainties() -> None:
    low = {"mean": 3, "standard_deviation": 2, "n": 4}
    high = {"mean": 1, "standard_deviation": 3, "n": 9}

    adjusted = null_adjusted_difference(low, high)

    assert adjusted["mean_difference"] == 2
    assert adjusted["standard_error"] == 2**0.5


def test_evaluation_distinguishes_directional_from_strong_support() -> None:
    low = {
        "mean": 2,
        "trimmed_5pct_mean": 1,
        "mean_without_largest": 1,
        "wins": 8,
        "losses": 2,
    }
    high = {"mean": 0}
    adjusted = {"ci95_normal": [-0.1, 4.1]}

    result = evaluate_followup(low, high, adjusted)

    assert result["directional_support"] is True
    assert result["strong_support"] is False
    assert result["decision"] == "directional_stochastic_support"
