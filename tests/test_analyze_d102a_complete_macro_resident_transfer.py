import pytest

from cgauto.analyze_d102a_complete_macro_resident_transfer import (
    BASE,
    analyze,
    read_rows,
)


RUN_A = BASE / "d102a-complete-macro-resident-transfer-a-jobs1-9824100-9824131.tsv"
RUN_B = BASE / "d102a-complete-macro-resident-transfer-b-jobs20-9824100-9824131.tsv"


def test_frozen_d102a_verdict_and_key_effects():
    assert RUN_A.read_bytes() == RUN_B.read_bytes()
    report = analyze(read_rows(RUN_A), read_rows(RUN_B), repeat_identical=True)

    assert report["integrity_pass"] is True
    assert report["mechanism_pass"] is True
    assert report["value_pass"] is False
    assert report["pass"] is False
    assert report["decision"] == "retain_d40_as_role_transition_teacher_do_not_package"

    assert report["paired"]["mean_margin_delta"] == pytest.approx(-48.396484375)
    assert report["paired"]["mean_own_score_delta"] == pytest.approx(17.546875)
    assert report["paired"]["mean_opponent_score_delta"] == pytest.approx(65.943359375)
    assert report["summaries"]["d40"]["own_crop_harvest_rate"] == pytest.approx(
        0.904296875
    )
    assert report["summaries"]["resident"]["own_crop_harvest_rate"] == pytest.approx(
        0.09765625
    )


def test_frozen_d102a_reproduces_joint_birth_accounting():
    report = analyze(read_rows(RUN_A), read_rows(RUN_B), repeat_identical=True)

    assert report["gates"]["integrity"][
        "zero_provenance_and_ambiguous_birth_failures"
    ] is True
    assert report["summaries"]["d40"]["mean_joint_created_crops"] == 0
    assert report["summaries"]["resident"]["mean_joint_created_crops"] == pytest.approx(
        4 / 512
    )
