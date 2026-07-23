"""Pure tests for exact historical-stream preseed gate helpers."""

from cgauto.preseed_historical_stream_gate import aggregate, first_action_divergence


def test_first_action_divergence_ignores_message_only_drift() -> None:
    baseline = ["MSG base;MOVE 0 1 2", "WAIT"]
    candidate = ["MSG candidate;MOVE 0 1 2", "PICK 0 APPLE"]

    assert first_action_divergence(baseline, candidate) == 2


def test_aggregate_separates_loss_and_win_activation() -> None:
    rows = [
        {
            "won": False,
            "baseline_matches_recorded": True,
            "first_divergence": 110,
            "first_divergence_is_eligible": True,
            "candidate_stderr": "",
        },
        {
            "won": True,
            "baseline_matches_recorded": False,
            "first_divergence": None,
            "first_divergence_is_eligible": False,
            "candidate_stderr": "",
        },
    ]

    result = aggregate(rows)

    assert result["candidate_activated_games"] == 1
    assert result["activated_close_losses"] == 1
    assert result["inactive_command_identical_games"] == 1
    assert result["baseline_exact_reproductions"] == 1
    assert result["rejected_nonreproducing_streams"] == 1
    assert result["admissible_candidate_activated_games"] == 1
    assert result["admissible_activated_close_losses"] == 1
    assert result["admissible_inactive_command_identical_games"] == 0
