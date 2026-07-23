from __future__ import annotations

from cgauto import analyze_d165a_resident_worker_role_return as d165


def test_frozen_catalog_and_matrix_are_exact() -> None:
    assert d165.POLICIES == (
        "resident",
        "producer_suppressor_return_h016",
    )
    assert d165.HORIZON == 16
    assert len(d165.expected_tasks()) == 1_024
    assert min(task[0] for task in d165.expected_tasks()) == 9_844_136
    assert max(task[0] for task in d165.expected_tasks()) == 9_844_199


def test_cluster_interval_and_percentiles_are_deterministic() -> None:
    rows = [
        {"map_seed": 1, "margin_delta": 1.0},
        {"map_seed": 1, "margin_delta": 3.0},
        {"map_seed": 2, "margin_delta": 5.0},
        {"map_seed": 2, "margin_delta": 7.0},
    ]
    interval = d165.normal_interval_by_map(rows, "margin_delta")
    assert interval is not None
    assert interval[0] < 4.0 < interval[1]
    assert d165.percentile([0, 10, 20], 0.10) == 2.0
    assert d165.percentile([], 0.10) is None


def test_frozen_output_has_clean_integrity_and_fails_support(tmp_path) -> None:
    result = d165.run(tmp_path / "d165-result.json")
    assert result["integrity_pass"]
    assert result["mechanism"]["activated_tasks"] == 0
    assert not result["mechanism"]["pass"]
    assert (
        result["decision"]["verdict"]
        == "close_exact_live_target_return_grammar_at_support_gate"
    )
    assert (
        result["support_diagnosis"]["opponent_crop_chop"]["events"]
        == 44_049
    )
    assert (
        result["support_diagnosis"][
            "opponent_crop_chop_by_historical_producer"
        ]["tasks"]
        == 237
    )
    assert (
        result["support_diagnosis"][
            "opponent_crop_chop_with_remembered_live_target"
        ]["events"]
        == 0
    )
