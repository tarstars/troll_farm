from __future__ import annotations

from cgauto.norxondor_partial_rollout_selector_study import aggregate


def test_partial_aggregates_use_conservative_order_statistics() -> None:
    values = [-4, 2, 8, 10]
    assert aggregate(values, "minimum") == -4
    assert aggregate(values, "lower_quartile") == -4
    assert aggregate(values, "median") == 5
    assert aggregate(values, "mean") == 4
