from cgauto import analyze_d150a_population_value_support as d150


def population(first_boundary, first_slot, second_boundary, second_slot, margin):
    return {
        "mode": "double",
        "intervention_batches": "2",
        "first_selected_boundary": str(first_boundary),
        "first_selected_slot": str(first_slot),
        "second_selected_boundary": str(second_boundary),
        "second_selected_slot": str(second_slot),
        "margin": str(margin),
    }


def candidates(stage, boundary, chosen):
    return [
        {
            "stage": stage,
            "boundary": str(boundary),
            "candidate_slot": str(slot),
            "chosen_slot": str(chosen),
        }
        for slot in (0, 1, 2, 3)
    ]


def test_first_join_aggregates_downstream_returns_by_first_action():
    rows = [
        population(0, 1, 1, 2, 10),
        population(0, 1, 2, 3, 15),
        population(0, 2, 1, 1, 14),
        population(1, 3, 2, 1, 99),
    ]
    manifest = {"first_boundary": "0", "first_slot": "1"}
    result = d150.group_support(
        (1, 0, "resident", 0), candidates("first", 0, 1), manifest, rows, True
    )
    assert result["joined_episodes"] == 3
    assert result["observed_actions"] == 2
    assert result["observed_slot_max_margin"] == {"1": 15, "2": 14}
    assert result["nonselected_near_tie"]


def test_second_join_requires_exact_first_path():
    rows = [
        population(0, 1, 1, 2, 10),
        population(0, 1, 1, 3, 12),
        population(0, 2, 1, 1, 99),
        population(0, 1, 2, 1, 98),
    ]
    manifest = {"first_boundary": "0", "first_slot": "1"}
    joined, field = d150.join_population_rows(
        "second", 1, manifest, rows
    )
    assert field == "second_selected_slot"
    assert [row["margin"] for row in joined] == ["10", "12"]
