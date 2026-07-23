import json

import pytest

from cgauto.analyze_d106a_q6_fresh_map_readout import OUTPUT
from cgauto.select_d106a_q6_precision import LOCK, build_lock


def test_d106a_q6_precision_lock_is_outcome_blind_and_reproducible():
    lock = json.loads(LOCK.read_text())
    assert lock == build_lock()
    assert lock["selection_pass"] is True
    assert lock["selected_bits"] == 6
    assert lock["outcomes_read"] is False
    assert lock["consumed_d105a_q6_proposals_inspected"] is False
    assert all(lock["selection_gates"].values())
    assert lock["q4_support"]["experts_noncontrol_in_at_least_25pct_roots"] == 48
    assert lock["q6_support"]["experts_noncontrol_in_at_least_25pct_roots"] == 50
    similarity = lock["q6_vs_q4_similarity"]
    assert similarity["mean_q4_union_recall"] == pytest.approx(0.8584810132982283)
    assert similarity["minimum_q4_union_recall"] == pytest.approx(
        0.5714285714285714
    )
    assert similarity["mean_q4_q6_union_jaccard"] == pytest.approx(
        0.784744960272247
    )


def test_d106a_fresh_q6_headroom_replicates():
    report = json.loads(OUTPUT.read_text())
    assert report["integrity_pass"] is True
    assert report["selection_pass"] is True
    assert report["headroom_pass"] is True
    assert all(report["integrity_gates"].values())
    assert all(report["headroom_gates"].values())
    oracle = report["fresh_union_oracle"]
    assert oracle["mean_margin_delta_all_tasks"] == pytest.approx(32.046875)
    assert oracle["strict_root_improvements"] == 216
    assert oracle["worst_family_mean_margin_delta"] == pytest.approx(17.8125)
    assert oracle["mean_own_score_delta_all_tasks"] == pytest.approx(17.34765625)
    assert oracle["mean_opponent_score_delta_all_tasks"] == pytest.approx(-14.69921875)
    assert oracle["mean_incremental_margin_vs_best_single_rooted"] == pytest.approx(
        12.017391304347827
    )
    assert oracle["joint_strictly_beats_best_single_roots"] == 145
    assert oracle["crop_rate"] == 1.0
    assert oracle["worker_three_rate"] == oracle["baseline_worker_three_rate"]


def test_d106a_offline_ridge_closes_on_held_calibration_failure():
    report = json.loads(OUTPUT.read_text())
    assert report["readout_opened"] is True
    assert report["readout_pass"] is False
    assert report["pass"] is False
    assert report["decision"] == "close_d106a_offline_ridge_keep_q6_action_basis"
    failed = {name for name, passed in report["readout_gates"].items() if not passed}
    assert failed == {
        "activation_between_15_and_80pct",
        "activated_positive_at_least_55pct",
        "every_family_at_least_minus3",
        "at_least_six_positive_families",
        "capture_at_least_15pct_oracle",
    }
    validation = report["readout_summaries"]["combined"]["validation"]
    assert validation["activation_rate"] == pytest.approx(0.8727272727272727)
    assert validation["mean_realized_margin_delta_all_tasks"] == pytest.approx(2.5546875)
    assert validation["activated_positive_rate"] == pytest.approx(0.5416666666666666)
    assert validation["strict_root_improvement_rate"] == pytest.approx(
        0.4727272727272727
    )
    assert validation["worst_family_mean_margin_delta"] == pytest.approx(-11.375)
    assert validation["positive_families"] == 5
    assert validation["oracle_value_capture"] == pytest.approx(0.08436532507739938)
    assert validation["crop_rate"] == 1.0
    assert validation["worker_three_rate"] == validation["baseline_worker_three_rate"]
