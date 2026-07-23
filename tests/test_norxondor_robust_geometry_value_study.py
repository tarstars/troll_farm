from __future__ import annotations

from cgauto.norxondor_robust_geometry_value_study import (
    group_rows,
    lower_quartile_positive,
)


def test_lower_quartile_requires_second_worst_positive() -> None:
    group = [{"margin_delta": value} for value in [-2, 1, 2, 3, 4, 5, 6, 7]]
    assert lower_quartile_positive(group)
    group[1]["margin_delta"] = 0
    assert not lower_quartile_positive(group)


def test_group_rows_requires_all_eight_opponents() -> None:
    rows = [
        {"seed": 1, "seat": 0, "actual_opponent": f"opponent-{index}"}
        for index in range(8)
    ]
    assert len(group_rows(rows)) == 1
