from cgauto.correct_d88b_support_count import correct


def fixture():
    return {
        "schema": "d88b-yaichi-task-state-v1",
        "rows_hash": "rows",
        "decision": "reject_literal_task_imitation",
        "counts": {"validation": 16},
        "integrity": {"validation": {"pass": True}},
        "mechanism": {
            "validation": {
                "renewable_games": 10,
                "bank_bootstrap_before_maintenance_games": 10,
                "complete_ordered_phase_games": 10,
            }
        },
        "mechanism_gates": {
            "supported_starter_plants_at_least_0.80": True,
            "own_crop_same_worker_replant_at_least_0.80": True,
            "trained_chop_drop_at_least_0.95": True,
            "trained_farm_in_at_most_one_game": True,
            "current_same_qualitative_direction": True,
        },
    }


def test_conservative_support_correction_passes_only_all_ten():
    result = correct(fixture(), input_hash="input")
    assert result["decision"] == "pass_write_blueprint_open_d89"
    assert all(result["corrected_gates"].values())
    payload = fixture()
    payload["mechanism"]["validation"]["complete_ordered_phase_games"] = 9
    assert correct(payload)["decision"] == "reject_or_repair_under_corrected_support"


def test_support_count_must_be_exactly_known_ten():
    payload = fixture()
    payload["mechanism"]["validation"]["renewable_games"] = 12
    try:
        correct(payload)
    except ValueError as error:
        assert "exactly ten" in str(error)
    else:
        raise AssertionError("bad support count accepted")
