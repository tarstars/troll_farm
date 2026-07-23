from __future__ import annotations

from cgauto.norxondor_research_rollout_study import summary


def test_summary_preserves_outcome_counts() -> None:
    result = summary([-2, 0, 3, 5])

    assert result["mean"] == 1.5
    assert result["wins"] == 2
    assert result["ties"] == 1
    assert result["losses"] == 1
