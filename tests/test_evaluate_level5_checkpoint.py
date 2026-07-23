from cgauto.evaluate_level5_checkpoint import d11_final_functional_gate


def passing_payload() -> dict:
    return {
        "success_rate": 0.90,
        "nontrivial_success_rate": 0.88,
        "recipe_success_floor": 0.82,
        "height_success_floor": 0.85,
        "created_crop_rate": 0.90,
        "renewable_harvest_rate": 0.95,
        "paired_teacher_median_turn_delta": 30.0,
    }


def test_d11_final_functional_gate_uses_inclusive_frozen_floors() -> None:
    assert d11_final_functional_gate(passing_payload())


def test_d11_final_functional_gate_rejects_each_missed_floor() -> None:
    payload = passing_payload()
    for key in payload:
        failed = payload.copy()
        if key == "paired_teacher_median_turn_delta":
            failed[key] += 0.01
        else:
            failed[key] -= 0.01
        assert not d11_final_functional_gate(failed), key
