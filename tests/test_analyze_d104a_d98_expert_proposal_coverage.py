import pytest

from cgauto.analyze_d104a_d98_expert_proposal_coverage import (
    PROPOSALS_A,
    PROPOSALS_B,
    analyze,
    read_table,
)


@pytest.fixture(scope="module")
def report():
    assert PROPOSALS_A.read_bytes() == PROPOSALS_B.read_bytes()
    rows_a, _ = read_table(PROPOSALS_A)
    rows_b, _ = read_table(PROPOSALS_B)
    return analyze(rows_a, rows_b, repeat_identical=True)


def test_frozen_d104a_full_pass_and_proposal_support(report):
    assert report["integrity_pass"] is True
    assert report["support_pass"] is True
    assert report["value_pass"] is True
    assert report["pass"] is True
    assert report["decision"] == (
        "open_d104b_online_recurrent_opponent_aware_proposal_controller"
    )
    assert all(report["integrity_gates"].values())
    assert all(report["support_gates"].values())
    assert all(report["value_gates"].values())

    audit = report["proposal_audit"]
    assert audit["rows_a"] == audit["rows_b"] == 15_360
    assert audit["supported_rate"] == 1.0
    assert audit["exact_arm_matches"] == 15_360
    assert audit["failure_counts"] == {}

    support = report["proposal_support"]
    assert support["mean_unique_supported_noncontrol_proposals_per_root"] == pytest.approx(
        16.641666666666666
    )
    assert support["minimum_unique_supported_noncontrol_proposals"] == 7
    assert support["root_rate_with_supported_joint"] == 1.0
    assert support["experts_noncontrol_in_at_least_25pct_roots"] == 50


def test_frozen_d104a_retains_joint_value_beyond_best_single(report):
    oracle = report["proposal_oracle"]
    assert oracle["mean_margin_delta_vs_d40_all_tasks"] == pytest.approx(31.859375)
    assert oracle["capture_of_d97_joint_oracle"] == pytest.approx(0.8645325418698325)
    assert oracle["mean_own_score_delta_vs_d40_all_tasks"] == pytest.approx(21.03515625)
    assert oracle["mean_opponent_score_delta_vs_d40_all_tasks"] == pytest.approx(-10.82421875)
    assert oracle["strict_root_improvements"] == 223
    assert oracle["mean_incremental_margin_vs_full_best_single_rooted"] == pytest.approx(
        3.8833333333333333
    )
    assert oracle["joint_selected_roots"] == 148
    assert oracle["joint_strictly_beats_full_best_single_roots"] == 107
    assert oracle["worst_opponent_family_mean_margin_delta"] == pytest.approx(18.75)
    assert oracle["proposal_oracle_crop_rate"] == 1.0
    assert oracle["proposal_oracle_worker_three_rate"] == oracle[
        "baseline_worker_three_rate"
    ]

