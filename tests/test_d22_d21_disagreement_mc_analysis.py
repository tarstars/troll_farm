from __future__ import annotations

from cgauto.d22_d21_disagreement_mc_analysis import classify


def classify_case(**updates):
    values = {
        "readiness_pass": True,
        "mean_advantage": 1.0,
        "positive_rate": 0.4,
        "gain_at_least_10_rate": 0.25,
        "nonnegative_opponent_means": 5,
        "gain_opponent_coverage": 6,
        "gain_recipe_coverage": 8,
        "new_catastrophe_rate": 0.0,
    }
    values.update(updates)
    return classify(**values)


def test_frozen_classifications_are_mutually_prioritized():
    assert classify_case() == "compounding_distribution_failure"
    assert (
        classify_case(mean_advantage=-0.1, gain_at_least_10_rate=0.1)
        == "direct_proposal_harm"
    )
    assert (
        classify_case(positive_rate=0.1, nonnegative_opponent_means=3)
        == "mixed_sparse_opportunity"
    )
    assert (
        classify_case(
            positive_rate=0.1,
            gain_at_least_10_rate=0.05,
            nonnegative_opponent_means=3,
        )
        == "mixed_unsafe"
    )


def test_readiness_failure_preempts_policy_classification():
    assert classify_case(readiness_pass=False) == "invalid_readiness"
