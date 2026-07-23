import math

from cgauto.analyze_d136a_d135_all_pair_transfer import pearson


def test_pearson_reads_held_and_d126_fields():
    rows = [
        {
            "held_selection": {"mean_margin_delta": value},
            "d126_metrics": {"mean_margin_delta": 2.0 * value},
        }
        for value in (1.0, 2.0, 4.0, 8.0)
    ]
    assert math.isclose(
        pearson(rows, "mean_margin_delta", "mean_margin_delta"), 1.0
    )
