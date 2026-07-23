import numpy as np

from cgauto.collect_d147a_selected_trajectory_features import (
    chosen_action,
    decision_stage,
    feature,
)


def test_decision_stage_covers_wait_first_wait_second_and_stop():
    assert decision_stage(0, 1, 3) == "wait_before_first"
    assert decision_stage(1, 1, 3) == "first"
    assert decision_stage(2, 1, 3) == "wait_before_second"
    assert decision_stage(3, 1, 3) == "second"
    assert decision_stage(4, 1, 3) is None


def test_chosen_action_uses_manifest_only_at_selected_boundaries():
    row = {
        "first_boundary": "1",
        "first_slot": "7",
        "second_boundary": "3",
        "second_slot": "9",
    }
    assert [chosen_action(index, row) for index in range(5)] == [0, 7, 0, 9, 0]


def test_feature_has_stable_float32_format():
    assert feature(np.float32(0.1)) == "0.100000001"
    assert feature(np.float32(-1.0)) == "-1.000000000"
