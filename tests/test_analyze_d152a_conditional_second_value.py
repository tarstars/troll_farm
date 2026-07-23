from cgauto import analyze_d152a_conditional_second_value as d152


def branch(slot, margin, own=None, opponent=10):
    own = margin + opponent if own is None else own
    return {
        "map_seed": "9844136",
        "seat": "0",
        "opponent": "resident",
        "second_slot": str(slot),
        "selected_second_slot": "2",
        "margin": str(margin),
        "own_score": str(own),
        "opponent_score": str(opponent),
        "own_created_crops": "1",
        "own_workers": "3",
        "first_boundary": "0",
        "first_slot": "1",
        "second_boundary": "1",
    }


def test_interpret_task_uses_control_and_soft_near_ties():
    rows = [branch(0, 10), branch(1, 20), branch(2, 18), branch(3, 19)]
    target = {
        "target_active": "1",
        "sequence_margin": "18",
        "one_use_margin": "12",
    }
    summary, labels = d152.interpret_task(rows, target)
    assert summary["gain"] == 10
    assert summary["oracle_slot"] == 1
    assert summary["original_within_five"]
    assert summary["nonselected_near_tie"]
    assert summary["positive_noncontrol_actions"] == 3
    assert sum(row["near_optimal"] for row in labels) == 3


def test_action_key_has_stable_lower_slot_tie_break():
    assert d152.action_key(branch(1, 20)) > d152.action_key(branch(2, 20))
