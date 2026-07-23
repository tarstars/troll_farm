import math

from cgauto.analyze_d131a_d130_all_seed_transfer import pearson


def test_pearson_reports_direction_and_degenerate_null():
    assert math.isclose(pearson([1, 2, 3], [2, 4, 6]), 1.0)
    assert math.isclose(pearson([1, 2, 3], [6, 4, 2]), -1.0)
    assert pearson([1, 1, 1], [1, 2, 3]) is None
