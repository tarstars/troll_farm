from cgauto.analyze_d122a_d119_crop_failure_trace import (
    observable_state,
    safe_alternatives,
    task_id,
)


def test_task_id_is_stable():
    assert task_id((9843700, 1, "resident")) == "9843700:1:resident"


def test_observable_state_uses_only_frozen_state_columns():
    row = {f"state_{index:03}": str(index / 10.0) for index in range(64)}
    state = observable_state(row)
    assert state["state_039_has_own_live_crop"] == 3.9
    assert state["state_058_live_own_crops"] == 5.8
    assert len(state) == 25


def test_forced_control_crop_failure_has_no_action_alternatives():
    result = safe_alternatives(
        {},
        {"choice": None},
        {},
        {},
    )
    assert result == {
        "applicable": False,
        "reason": "forced_control_crop_failure_without_intervention",
        "proposal_count": 0,
        "unsafe_proposals": 0,
        "safe_proposals": 0,
        "top_safe_by_model": [],
        "best_safe_by_exact_margin": None,
    }
