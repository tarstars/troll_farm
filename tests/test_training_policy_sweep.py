"""Tests for consolidated training-policy sweep statistics."""

import pytest

from cgauto.summarize_training_sweep import row_stats


def test_row_stats_decomposes_wood_and_nonwood_score() -> None:
    rows = [
        {"candidate_paired_margin": 4, "candidate_wood_delta": 1},
        {"candidate_paired_margin": 0, "candidate_wood_delta": 0},
        {"candidate_paired_margin": -2, "candidate_wood_delta": -0.5},
    ]

    result = row_stats(rows)

    assert result["seeds"] == 3
    assert result["mean_margin"] == pytest.approx(2 / 3)
    assert result["median_margin"] == 0
    assert result["mean_wood_delta"] == pytest.approx(1 / 6)
    assert result["mean_nonwood_score_delta"] == 0
    assert result["wins_ties_losses"] == {"wins": 1, "ties": 1, "losses": 1}
    assert result["active_seeds"] == 2
    assert result["minimum_margin"] == -2
    assert result["maximum_margin"] == 4


def test_row_stats_trims_five_percent_from_each_tail() -> None:
    rows = [
        {"candidate_paired_margin": margin, "candidate_wood_delta": 0}
        for margin in [-100, *([1] * 18), 100]
    ]

    result = row_stats(rows)

    assert result["trimmed_5pct_mean_margin"] == 1


def test_row_stats_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="empty"):
        row_stats([])
