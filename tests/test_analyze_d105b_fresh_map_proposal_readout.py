import json

import pytest

from cgauto.analyze_d105b_fresh_map_proposal_readout import OUTPUT


@pytest.fixture(scope="module")
def report():
    return json.loads(OUTPUT.read_text())


def test_d105b_stops_before_outcomes_on_frozen_support_failure(report):
    assert report["integrity_pass"] is True
    assert report["support_pass"] is False
    assert report["terminal_value_opened"] is False
    assert report["readout_fit_opened"] is False
    assert report["pass"] is False
    assert report["decision"] == "close_d105b_q4_fresh_map_readout_before_outcomes"
    assert all(report["integrity_gates"].values())
    assert report["failed_support_gates"] == [
        "at_least_48_experts_active_on_25pct_roots"
    ]


def test_d105b_q4_union_is_broad_but_has_only_47_active_experts(report):
    support = report["support"]
    assert support["roots"] == 233
    assert support["selected_arms"] == 4_264
    assert support["mean_unique_noncontrol_proposals_per_root"] == pytest.approx(
        17.300429184549355
    )
    assert support["minimum_unique_noncontrol_proposals_per_root"] == 8
    assert support["roots_with_joint"] == 233
    assert support["experts_noncontrol_in_at_least_25pct_roots"] == 47
    assert set(support["job_kinds"]) == {"fell", "harvest", "mine", "renew"}
    assert {"natural", "own", "opponent"}.issubset(
        support["provenance_classes"]
    )
    assert support["reversed_role_order_present"] is True
    assert report["activity_boundary"]["experts_at_or_above_floor"] == 47
    assert report["active_root_floor"] == 59
