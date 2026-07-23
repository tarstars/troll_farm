from cgauto import analyze_d151a_conditional_second_corpus as d151
from cgauto import run_d144a_two_intervention_mc_pilot as d144


def test_row_errors_accepts_control_second_fallback():
    plan = {
        "slots": (0, 2),
        "scenario": "0",
        "source_replica": "7",
        "first_boundary": "0",
        "first_slot": "3",
        "second_boundary": "1",
        "selected_second_slot": "2",
        "target_active": "1",
    }
    selection = d144.update_selection_hash(0, 0, 3)
    row = {
        "branch_ordinal": "0",
        "second_slot": "0",
        "scenario": "0",
        "source_replica": "7",
        "first_boundary": "0",
        "first_slot": "3",
        "second_boundary": "1",
        "selected_second_slot": "2",
        "target_active": "1",
        "selection_hash": str(selection),
        "own_score": "20",
        "opponent_score": "10",
        "margin": "10",
        "baseline_own_score": "15",
        "baseline_opponent_score": "10",
        "baseline_margin": "5",
        "margin_delta": "5",
        "intervention_batches": "1",
    }
    assert not any(d151.row_errors(row, plan).values())
