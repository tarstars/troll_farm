from __future__ import annotations

from cgauto.analyze_d41c_residual_gaps import distribution


def test_distribution_reports_exact_order_statistics() -> None:
    result = distribution([1.0, 2.0, 3.0])
    assert result["count"] == 3
    assert result["minimum"] == 1.0
    assert result["median"] == 2.0
    assert result["maximum"] == 3.0


def test_distribution_handles_empty_input() -> None:
    assert distribution([]) == {"count": 0}
