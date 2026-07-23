import json

import pytest

from cgauto.analyze_d105a_low_bit_full_expert_bank import (
    LOCK,
    OUTPUT,
    select_width,
)


@pytest.fixture(scope="module")
def selection():
    selected, rows = select_width()
    assert rows is not None
    return selected


def test_frozen_d105a_selects_four_bits_without_outcomes(selection):
    assert selection["selection_pass"] is True
    assert selection["selected_bits"] == 4
    assert selection["evaluated_bits"] == [4]
    assert selection["higher_width_fidelity_inspected"] is False
    assert selection["outcomes_read_during_selection"] is False
    assert selection == json.loads(LOCK.read_text())

    candidate = selection["selected_fidelity"]
    assert candidate["pass"] is True
    assert all(candidate["gates"].values())
    similarity = candidate["similarity"]
    assert similarity["exact_arm_matches"] == 13_489
    assert similarity["exact_arm_match_rate"] == pytest.approx(0.8781901041666667)
    assert similarity["mean_exact_noncontrol_union_recall"] == pytest.approx(
        0.9061683215005114
    )
    assert similarity["minimum_exact_noncontrol_union_recall"] == pytest.approx(
        0.6923076923076923
    )
    assert similarity["mean_noncontrol_union_jaccard"] == pytest.approx(
        0.7883342084004157
    )
    support = candidate["support"]
    assert support["mean_unique_supported_noncontrol_proposals_per_root"] == pytest.approx(
        17.595833333333335
    )
    assert support["minimum_unique_supported_noncontrol_proposals"] == 8
    assert support["root_rate_with_supported_joint"] == 1.0
    assert support["experts_noncontrol_in_at_least_25pct_roots"] == 48
    assert candidate["population_audit"]["base85_payload_bytes"] == 6_120


def test_frozen_d105a_value_pass_preserves_joint_coordination():
    report = json.loads(OUTPUT.read_text())
    assert report["integrity_pass"] is True
    assert report["selection_pass"] is True
    assert report["value_pass"] is True
    assert report["pass"] is True
    assert report["decision"] == (
        "open_d105b_fresh_map_recurrent_proposal_controller_preflight"
    )
    assert all(report["integrity_gates"].values())
    assert all(report["value_gates"].values())

    oracle = report["quantized_oracle"]
    assert oracle["mean_margin_delta_vs_d40_all_tasks"] == pytest.approx(32.4453125)
    assert oracle["retained_fraction_of_d104a_union_gain"] == pytest.approx(
        1.0183913683178027
    )
    assert oracle["capture_of_d97_joint_oracle"] == pytest.approx(0.880432478270087)
    assert oracle["mean_own_score_delta_vs_d40_all_tasks"] == pytest.approx(21.41015625)
    assert oracle["mean_opponent_score_delta_vs_d40_all_tasks"] == pytest.approx(
        -11.03515625
    )
    assert oracle["strict_root_improvements"] == 225
    assert oracle["mean_incremental_margin_vs_full_best_single_rooted"] == pytest.approx(
        4.508333333333334
    )
    assert oracle["joint_selected_roots"] == 155
    assert oracle["joint_strictly_beats_full_best_single_roots"] == 112
    assert oracle["worst_opponent_family_mean_margin_delta"] == pytest.approx(18.875)
    assert oracle["proposal_oracle_crop_rate"] == 1.0
    assert oracle["proposal_oracle_worker_three_rate"] == oracle[
        "baseline_worker_three_rate"
    ]
