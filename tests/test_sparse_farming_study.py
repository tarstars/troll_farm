"""Unit tests for sparse-farming paired-study arithmetic."""

from cgauto.sparse_farming_study import aggregate, candidate_margins


def test_candidate_margins_follow_candidate_across_seat_swap() -> None:
    baseline_seat0 = {"scores": [10, 15]}
    candidate_seat0 = {"scores": [21, 18]}

    assert candidate_margins(baseline_seat0, candidate_seat0) == [5, 3]


def test_aggregate_separates_activated_and_inactive_seeds() -> None:
    rows = [
        {"activated": True, "candidate_paired_margin": 4, "candidate_wood_delta": 2},
        {"activated": True, "candidate_paired_margin": -2, "candidate_wood_delta": -1},
        {"activated": False, "candidate_paired_margin": 0, "candidate_wood_delta": 0},
    ]

    result = aggregate(rows)

    assert result["activated"]["seeds"] == 2
    assert result["activated"]["candidate_mean_paired_margin"] == 1
    assert result["activated"]["candidate_mean_wood_delta"] == 0.5
    assert result["activated"]["candidate_wins_ties_losses"] == {
        "wins": 1,
        "ties": 0,
        "losses": 1,
    }
    assert result["inactive"]["candidate_wins_ties_losses"]["ties"] == 1
