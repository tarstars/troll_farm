from __future__ import annotations

from cgauto.agent_opening_plan_audit import audit, parse_train


def test_parse_train_and_audit_alignment() -> None:
    assert parse_train("TRAIN 2 3 0 2") == (2, 3, 0, 2)
    analysis = {
        "occurrences": [
            {
                "agent_id": 7,
                "game_id": 10,
                "training_events": [
                    {
                        "turn": 8,
                        "spec": [2, 3, 0, 2],
                        "max_affordable_spec": [2, 3, 2, 2],
                        "first_affordable_turn": 8,
                        "delay_after_affordable": 0,
                    }
                ],
            }
        ]
    }

    result = audit(analysis, 7, {10: (2, 2, 0, 2)}, "test")

    assert result["planned_spec_exact"] == 0
    assert result["mean_talent_l1"] == 1
    assert result["actual_max_affordable_hp0"] == 1
    assert result["trained_on_first_chosen_spec_affordability"] == 1
