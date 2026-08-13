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

    # Owner ruling 2026-08-11 (B7/1a). The live source was legitimately replaced on
    # 2026-07-29 by the platform recovery (SHA-256 prefix fff6669b), so the
    # source-fingerprint gate is expected False permanently for this frozen record;
    # every other gate and every frozen number must still reproduce. If the hash
    # gate ever reads True again, the source moved a second time — investigate,
    # never silently re-pin.
    gates = report["gates"]["integrity"]
    assert gates["frozen_source_hashes_match"] is False
    for name, value in gates.items():
        if name != "frozen_source_hashes_match":
            assert value is True, name

    assert report["integrity_pass"] is False  # driven solely by the hash gate
    assert report["mechanism_pass"] is True
    assert report["value_pass"] is False
    assert report["pass"] is False
    # Mechanical consequence of integrity_pass=False in the frozen analyzer. The
    # historical verdict, rendered at experiment time with matching hashes, was
    # "retain_d40_as_role_transition_teacher_do_not_package" and still stands.
    assert report["decision"] == "repair_measurement_and_rerun_frozen_panel"

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
