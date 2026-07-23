"""Tests for generic paired live-variant aggregation."""

from cgauto.live_variant_study import aggregate


def test_aggregate_reports_candidate_direction_and_command_deltas() -> None:
    rows = [
        {
            "candidate_paired_margin": 4,
            "candidate_wood_delta": 2,
            "command_delta": {"CHOP": 3},
        },
        {
            "candidate_paired_margin": -2,
            "candidate_wood_delta": 0,
            "command_delta": {"CHOP": -1, "WAIT": 2},
        },
    ]

    result = aggregate(rows)

    assert result["candidate_mean_paired_margin"] == 1
    assert result["candidate_mean_wood_delta"] == 1
    assert result["candidate_wins_ties_losses"] == {"wins": 1, "ties": 0, "losses": 1}
    assert result["mean_command_delta"] == {"CHOP": 1, "WAIT": 1}
