"""Tests for the sole D75b horizon repair."""

from cgauto.analyze_d75b_two_batch_option_sequences import strict_horizon_failures


def test_repaired_horizon_excludes_turn_299_and_later() -> None:
    rows = [{"turn": str(turn)} for turn in (0, 298, 299, 300)]
    assert strict_horizon_failures(rows) == 2
