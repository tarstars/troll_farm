from cgauto.analyze_d87a_fresh_harvest_regeneration import (
    lower_empirical_quantile,
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
