from cgauto.analyze_d127a_d126_tail_attribution import (
    SWEEP_OFFSETS,
    loss_attribution,
    loss_group_summary,
)


def test_sweep_is_frozen_from_minus_point_one_through_point_five():
    assert len(SWEEP_OFFSETS) == 13
    assert SWEEP_OFFSETS[0] == -0.10
    assert SWEEP_OFFSETS[-1] == 0.50


def test_loss_attribution_separates_ranking_timing_and_abstention():
    assert loss_attribution(1, 2, 3) is None
    assert loss_attribution(-1, 2, 0) == "proposal_ranking_error"
    assert loss_attribution(-1, -2, 3) == "act_wait_timing_error"
    assert loss_attribution(-1, -2, -3) == "should_abstain_to_control"


def test_loss_group_summary_aggregates_negative_margin():
    rows = [
        {"opponent": "a", "chosen": {"margin_delta": -2}},
        {"opponent": "a", "chosen": {"margin_delta": -4}},
        {"opponent": "b", "chosen": {"margin_delta": -1}},
    ]
    summary = loss_group_summary(rows, "opponent")
    assert summary["a"] == {
        "tasks": 2,
        "total_margin_delta": -6,
        "mean_margin_delta": -3,
        "minimum_margin_delta": -4,
    }
