from cgauto import analyze_d162a_resident_native_capital_option as d162


def row(seed: int, opponent: str, policy: str, margin: int, crops: int = 1, workers: int = 2) -> dict:
    return {
        "map_seed": seed,
        "seat": 0,
        "opponent": opponent,
        "policy": policy,
        "own_score": 100 + margin,
        "opponent_score": 100,
        "own_created_crops": crops,
        "max_own_workers": workers,
    }


def test_catalog_is_frozen_control_plus_twelve_options() -> None:
    policies = d162.catalog()
    assert len(policies) == 13
    assert policies[0]["label"] == "resident"
    assert policies[1]["label"] == "minimal_1101_t072_h032"
    assert policies[-1]["label"] == "balanced_2202_t136_h064"


def test_envelope_prefers_resident_on_tie_and_rejects_crop_extinction() -> None:
    indexed = {}
    for key in d162.expected_tasks():
        resident = row(key[0], key[2], "resident", 0)
        resident["seat"] = key[1]
        indexed[(*key, "resident")] = resident
        for policy in d162.catalog()[1:]:
            candidate = row(key[0], key[2], policy["label"], 0)
            candidate["seat"] = key[1]
            indexed[(*key, policy["label"])] = candidate
    first_key = sorted(d162.expected_tasks())[0]
    harmful = indexed[(*first_key, d162.catalog()[1]["label"])]
    harmful["own_score"] = 200
    harmful["own_created_crops"] = 0

    selected, summary = d162.select_envelope(indexed)

    assert selected[first_key]["policy"] == "resident"
    assert set(item["policy"] for item in selected.values()) == {"resident"}
    assert summary["ineligible_crop_rows"] == 1


def test_capacity_envelope_has_no_strict_regressions_by_construction() -> None:
    indexed = {}
    winning_policy = d162.catalog()[1]["label"]
    for key in d162.expected_tasks():
        resident = row(key[0], key[2], "resident", 0)
        resident["seat"] = key[1]
        indexed[(*key, "resident")] = resident
        for policy in d162.catalog()[1:]:
            gain = 10 if policy["label"] == winning_policy else -20
            candidate = row(
                key[0], key[2], policy["label"], gain, workers=3 if gain > 0 else 2
            )
            candidate["seat"] = key[1]
            indexed[(*key, policy["label"])] = candidate

    result = d162.capacity_metrics(indexed)

    assert result["delta"]["strict_regression_tasks"] == 0
    assert result["delta"]["mean_margin_delta"] == 10
    assert result["selected_worker_three_rate"] == 1


def test_frozen_d162_result_closes_one_lane_scaling_but_retains_value_signal() -> None:
    result = d162.analyze(d162.RUN_A, d162.RUN_B)

    assert result["integrity"]["pass"] is True
    assert result["resident_parity"]["pass"] is True
    assert result["mechanism"]["pass"] is False
    assert result["capacity"]["pass"] is False
    assert result["decision"] == "close_exact_one_lane_reserve_interface_on_mechanics"
    assert result["capacity"]["delta"]["mean_margin_delta"] == 12.65625
    assert result["capacity"]["positive_families"] == 8
    assert result["capacity"]["selected_worker_three_rate"] == 1 / 128
