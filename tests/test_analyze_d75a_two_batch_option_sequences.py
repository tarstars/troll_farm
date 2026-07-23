"""Tests for D75 two-batch sequence analysis helpers."""

from __future__ import annotations

from cgauto.analyze_d75a_two_batch_option_sequences import choose_best


def row(margin: int, own: int, opponent: int) -> dict[str, str]:
    return {"margin": str(margin), "own_score": str(own), "opponent_score": str(opponent)}


def test_choose_best_prefers_prefix_on_exact_outcome_tie() -> None:
    rows = {index: row(0, 10, 10) for index in range(16)}
    rows[1] = row(5, 15, 10)
    rows[4] = row(5, 15, 10)
    assert choose_best(rows, tuple(range(16))) == 4


def test_choose_best_uses_outcome_then_sequence_index() -> None:
    rows = {index: row(0, 10, 10) for index in range(16)}
    rows[4] = row(5, 14, 9)
    rows[8] = row(5, 15, 10)
    assert choose_best(rows, (0, 4, 8, 12)) == 8
