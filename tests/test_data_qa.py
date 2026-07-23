"""Focused tests for replay-QA score classification."""

from data.scripts.qa import score_status


def test_score_status_exact() -> None:
    status, derived = score_status([9, 17], [[1, 0, 0, 0, 0, 2], [1, 0, 0, 0, 0, 4]])

    assert status == "exact"
    assert derived == [9, 17]


def test_score_status_accepts_official_crash_penalty() -> None:
    status, derived = score_status([-2, 17], [[1, 0, 0, 0, 0, 2], [1, 0, 0, 0, 0, 4]])

    assert status == "penalty"
    assert derived == [9, 17]


def test_score_status_rejects_non_penalty_drift() -> None:
    status, derived = score_status([8, 17], [[1, 0, 0, 0, 0, 2], [1, 0, 0, 0, 0, 4]])

    assert status == "unexpected"
    assert derived == [9, 17]
