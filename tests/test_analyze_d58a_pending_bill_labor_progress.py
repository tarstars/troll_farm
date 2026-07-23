from cgauto.analyze_d58a_pending_bill_labor_progress import ACTIONS, summarize


def diagnostic_row(**overrides):
    row = {
        "final_workers": "2",
        "pending3_turns": "2",
        "pending3_worker_turns": "4",
        "pending3_progress_turns": "1",
        "pending3_equal_turns": "1",
        "pending3_regress_turns": "0",
        "pending3_reduced_units": "2",
        "pending3_increased_units": "0",
    }
    for action in ACTIONS:
        row[f"pending3_action_{action}"] = "0"
        row[f"pending3_{action}_observed_turns"] = "0"
        row[f"pending3_{action}_progress_turns"] = "0"
        row[f"pending3_{action}_regress_turns"] = "0"
    row["pending3_action_move"] = "2"
    row["pending3_action_harvest"] = "2"
    row["pending3_move_observed_turns"] = "2"
    row["pending3_move_progress_turns"] = "1"
    for resource in ("plum", "lemon", "apple", "iron"):
        row[f"pending3_initial_deficit_{resource}"] = "4"
        row[f"pending3_minimum_deficit_{resource}"] = "2"
        row[f"pending3_last_deficit_{resource}"] = "3"
    for fruit in ("plum", "lemon", "apple", "banana"):
        row[f"successful_plants_{fruit}"] = "1"
        row[f"harvested_{fruit}"] = "2"
    row.update(overrides)
    return row


def test_summary_preserves_worker_turn_shares_and_signed_progress():
    summary = summarize([diagnostic_row()])
    assert summary["pending_worker_turns"] == 4
    assert summary["actions"]["move"]["share"] == 0.5
    assert summary["actions"]["harvest"]["share"] == 0.5
    assert summary["progress"]["net_units"] == 2
    assert summary["progress"]["net_units_per_worker_turn"] == 0.5
    assert summary["per_action_next_state"]["move"]["progress_rate"] == 0.5
    assert summary["deficit"]["lemon"]["initial_to_minimum_mean"] == 2
    assert summary["deficit"]["lemon"]["initial_to_last_mean"] == 1
