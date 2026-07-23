import pytest

from cgauto.analyze_d103a_opponent_growth_phase_decomposition import (
    BASE,
    analyze,
    read_rows,
)


RUN_A = BASE / "d103a-d40-opponent-growth-phase-decomposition-a-jobs1-9824100-9824131.tsv"
RUN_B = BASE / "d103a-d40-opponent-growth-phase-decomposition-b-jobs20-9824100-9824131.tsv"


@pytest.fixture(scope="module")
def report():
    assert RUN_A.read_bytes() == RUN_B.read_bytes()
    return analyze(read_rows(RUN_A), read_rows(RUN_B), repeat_identical=True)


def test_frozen_d103a_integrity_and_mixed_boundary_verdict(report):
    assert report["integrity_pass"] is True
    assert all(report["integrity_gates"].values())
    assert report["primary_boundary"] == "mixed"
    assert report["decision"] == "require_complete_closed_loop_opponent_aware_policy_improvement"

    nearest = report["decomposition"]["nearest"]
    assert nearest["mean_opponent_score_excess"] == pytest.approx(65.943359375)
    assert nearest["component_means"] == pytest.approx(
        {
            "pre_scale_opponent_score_excess": 9.48046875,
            "post_scale_common_opponent_score_excess": 25.71484375,
            "extension_opponent_score_excess": 30.748046875,
        }
    )
    assert nearest["component_shares_of_total"] == pytest.approx(
        {
            "pre_scale_opponent_score_excess": 0.14376684536326748,
            "post_scale_common_opponent_score_excess": 0.3899534993928265,
            "extension_opponent_score_excess": 0.4662796552439061,
        }
    )
    assert report["decomposition"]["earlier"]["primary_boundary_from_value_only"] == "mixed"
    assert report["decomposition"]["later"]["primary_boundary_from_value_only"] == "mixed"


def test_frozen_d103a_terminal_alignment_is_exact_and_messages_are_absent(report):
    component_fields = (
        "pre_scale_opponent_score_excess",
        "post_scale_common_opponent_score_excess",
        "extension_opponent_score_excess",
    )
    assert all(
        row["opponent_score_excess"] == sum(row[field] for field in component_fields)
        for row in report["task_rows"]
    )

    outlier = next(
        row
        for row in report["task_rows"]
        if row["map_seed"] == 9_824_101
        and row["seat"] == 1
        and row["opponent"] == "resident"
    )
    assert outlier["common_boundary_distance"] == 145
    assert outlier["opponent_score_common_boundary_alignment"] == -39
    assert report["decomposition"]["nearest"]["common_boundary_alignment_means"][
        "opponent_score"
    ] == pytest.approx(-0.224609375)

    assert report["message_preflight"]["games"] == 10
    assert report["message_preflight"]["all_games_have_zero_msg_commands"] is True

