import json

import pytest

from cgauto.analyze_d104a_d98_expert_proposal_coverage import (
    D97_MANIFEST,
    D98_POPULATION,
    PROPOSALS_A,
    read_experts,
    read_table,
)
from cgauto.analyze_d104b_compact_expert_library import (
    LOCK,
    OUTPUT,
    lock_payload,
    population_rows,
    select_compact_library,
)
from cgauto.analyze_d97a_joint_concrete_jobs import manifest_support


@pytest.fixture(scope="module")
def frozen_selection():
    proposals, _ = read_table(PROPOSALS_A)
    manifest, _ = read_table(D97_MANIFEST)
    _, manifest_by_arm = manifest_support(manifest)
    return select_compact_library(
        proposals,
        manifest_by_arm,
        population_rows(D98_POPULATION),
        read_experts(D98_POPULATION),
    )


def test_frozen_d104b_outcome_blind_selection_is_deterministic(frozen_selection):
    assert frozen_selection["selected_experts"] == [
        "four_11",
        "four_12",
        "four_50",
        "four_40",
        "four_21",
        "four_48",
        "four_53",
    ]
    assert frozen_selection["selected_count"] == 7
    assert frozen_selection["coefficient_payload_bytes"] == 12_303
    assert frozen_selection["selection_pass"] is True
    support = frozen_selection["support"]
    assert support["mean_unique_supported_noncontrol_proposals_per_root"] == pytest.approx(
        6.641666666666667
    )
    assert support["minimum_unique_supported_noncontrol_proposals"] == 5
    assert support["root_rate_with_supported_joint"] == 1.0

    lock = json.loads(LOCK.read_text())
    assert lock == lock_payload(frozen_selection)
    assert lock["outcomes_read_during_selection"] is False


def test_frozen_d104b_is_an_honest_value_failure():
    report = json.loads(OUTPUT.read_text())
    assert report["integrity_pass"] is True
    assert report["selection_pass"] is True
    assert report["value_opened"] is True
    assert report["value_pass"] is False
    assert report["pass"] is False
    assert report["decision"] == "close_coverage_only_compact_expert_library"
    assert all(report["integrity_gates"].values())

    failed = {name for name, passed in report["value_gates"].items() if not passed}
    assert failed == {
        "retain_at_least_80pct_d104a_union_gain",
        "gain_at_least_2_beyond_full_best_single",
        "selected_proposal_breadth",
    }
    oracle = report["compact_oracle"]
    assert oracle["mean_margin_delta_vs_d40_all_tasks"] == pytest.approx(25.34765625)
    assert oracle["retained_fraction_of_d104a_union_gain"] == pytest.approx(
        0.7956105934281511
    )
    assert oracle["mean_incremental_margin_vs_full_best_single_rooted"] == pytest.approx(
        -3.0625
    )
    assert oracle["capture_of_d97_joint_oracle"] == pytest.approx(0.6878312486750053)
    assert oracle["strict_root_improvements"] == 203
    assert oracle["joint_selected_roots"] == 189
    assert oracle["joint_strictly_beats_full_best_single_roots"] == 81
    assert oracle["worst_opponent_family_mean_margin_delta"] == pytest.approx(15.15625)
    assert oracle["proposal_oracle_crop_rate"] == 1.0
    assert oracle["proposal_oracle_worker_three_rate"] == oracle[
        "baseline_worker_three_rate"
    ]
