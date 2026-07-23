from __future__ import annotations

from cgauto.analyze_d41d_one_deviation import behavioral_rows_equal, delta_stats


def test_delta_stats_has_paired_rates_and_normal_interval() -> None:
    rows = [{"margin_delta": value} for value in (-1, 0, 2, 3)]
    result = delta_stats(rows)
    assert result["samples"] == 4
    assert result["mean"] == 1.0
    assert result["positive_rate"] == 0.5
    assert result["tie_rate"] == 0.25
    assert result["negative_rate"] == 0.25
    assert result["normal_95_low"] < result["mean"] < result["normal_95_high"]


def test_aa_comparison_ignores_only_elapsed_time() -> None:
    left = [{"sample_id": 1, "margin_delta": 3, "elapsed_us": 10}]
    right = [{"sample_id": 1, "margin_delta": 3, "elapsed_us": 20}]
    assert behavioral_rows_equal(left, right)
    right[0]["margin_delta"] = 4
    assert not behavioral_rows_equal(left, right)
