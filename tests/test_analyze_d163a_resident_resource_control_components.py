import json

from cgauto import analyze_d163a_resident_resource_control_components as d163


def synthetic_index() -> dict:
    indexed = {}
    for key in d163.expected_tasks():
        for start in d163.MARKS:
            for mask in range(8):
                fruit = int(bool(mask & d163.COMPONENTS["fruit"]))
                iron = int(bool(mask & d163.COMPONENTS["iron"]))
                protection = int(bool(mask & d163.COMPONENTS["protection"]))
                margin = (
                    3 * fruit
                    - 2 * iron
                    + 5 * protection
                    + 4 * fruit * iron
                )
                label = d163.label_for(start, mask)
                row = {
                    "map_seed": key[0],
                    "seat": key[1],
                    "opponent": key[2],
                    "policy": label,
                    "own_score": 100 + margin,
                    "opponent_score": 100,
                    "own_created_crops": 1,
                    "successful_trains": 0,
                    "own_workers": 2,
                    "max_own_workers": 2,
                }
                if mask == 0:
                    indexed.setdefault((*key, "resident"), row)
                else:
                    indexed[(*key, label)] = row
    return indexed


def test_catalog_is_shared_control_plus_twenty_one_factorial_arms() -> None:
    policies = d163.catalog()
    assert len(policies) == 22
    assert policies[0]["label"] == "resident"
    assert policies[1]["label"] == "fruit_t072_h032"
    assert policies[7]["label"] == "fruit_iron_protection_t072_h032"
    assert policies[-1]["label"] == "fruit_iron_protection_t136_h032"


def test_factorial_main_effects_recover_additive_and_interaction_average() -> None:
    results = d163.factorial_components(
        synthetic_index(),
        {"fruit": 1.0, "iron": 1.0, "protection": 1.0},
    )
    assert results["fruit"]["paired_observations"] == 1536
    assert results["fruit"]["mean_margin_effect"] == 5
    assert results["iron"]["mean_margin_effect"] == 0
    assert results["protection"]["mean_margin_effect"] == 5


def test_interaction_contrasts_recover_fruit_iron_term() -> None:
    interactions = d163.interaction_effects(synthetic_index())
    assert (
        interactions["two_way"]["fruit_x_iron"]["mean_margin_interaction"]
        == 4
    )
    assert (
        interactions["two_way"]["fruit_x_protection"][
            "mean_margin_interaction"
        ]
        == 0
    )
    assert interactions["three_way"]["mean_margin_interaction"] == 0


def test_fixed_arm_gate_is_resident_relative_without_oracle_selection() -> None:
    arms = d163.fixed_arm_metrics(synthetic_index())
    assert arms["protection_t072_h032"]["mean_margin_delta"] == 5
    assert arms["protection_t072_h032"]["pass"] is True
    assert arms["iron_t072_h032"]["mean_margin_delta"] == -2
    assert arms["iron_t072_h032"]["pass"] is False


def test_frozen_d163_result_closes_fixed_shadow_reserve_grammar() -> None:
    result = json.loads(d163.OUTPUT.read_text())

    assert result["integrity"]["pass"] is True
    assert result["mechanism"]["pass"] is True
    assert result["passing_components"] == []
    assert result["passing_fixed_arms"] == []
    assert result["components"]["fruit"]["mean_margin_effect"] == -1.982421875
    assert result["components"]["iron"]["mean_margin_effect"] == -3.5514322916666665
    assert result["components"]["protection"]["mean_margin_effect"] == -0.029296875
    assert (
        result["decision"]
        == "close_fixed_shadow_reserve_grammar_no_causal_component"
    )
