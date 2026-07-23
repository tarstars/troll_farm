from cgauto.analyze_d56a_deficit_scaled_lemon_source import (
    CONFIGS,
    MODELS,
    lemon_mechanism_gates,
    lemon_mechanism_summary,
)


def test_frozen_v6_catalog_crosses_eight_configs_without_pruning():
    assert len(MODELS) == 8
    assert len(set(MODELS)) == 8
    assert all(label.startswith("legend_v6_") for label in MODELS)
    assert {config["first_name"] for config in CONFIGS.values()} == {
        "hp2",
        "balanced",
    }
    assert {config["max_workers"] for config in CONFIGS.values()} == {3, 4}
    assert {config["post_producers"] for config in CONFIGS.values()} == {1, 2}


def test_lemon_mechanism_summary_preserves_signed_deltas():
    summary = lemon_mechanism_summary([(2, 5), (4, 4), (7, 6)])
    assert summary["cells"] == 3
    assert summary["increased_cells"] == 1
    assert summary["equal_cells"] == 1
    assert summary["decreased_cells"] == 1
    assert summary["total_delta"] == 2
    assert summary["mean_delta"] == 2 / 3


def test_lemon_mechanism_gates_use_frozen_inclusive_boundaries():
    passing = {
        "cells": 732,
        "increased_cells": 183,
        "mean_delta": 1.0,
    }
    assert all(lemon_mechanism_gates(passing).values())
    for field, value in (
        ("cells", 731),
        ("increased_cells", 182),
        ("mean_delta", 0.999),
    ):
        failing = {**passing, field: value}
        assert not all(lemon_mechanism_gates(failing).values())
