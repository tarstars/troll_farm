from copy import deepcopy

from cgauto.analyze_d52a_hybrid_job_market import (
    CONFIGS,
    MODELS,
    activation_gates,
    mechanism_signature,
)


def passing_counts():
    return {
        label: {
            "cells": 160,
            "worker_two": 144,
            "worker_three": 112,
            "worker_four": 24 if config["max_workers"] == 4 else 0,
            "successful_crop": 152,
        }
        for label, config in CONFIGS.items()
    }


def test_frozen_catalog_has_eight_unique_crossed_configs():
    assert len(MODELS) == 8
    assert len(set(MODELS)) == 8
    assert len({tuple(sorted(config.items())) for config in CONFIGS.values()}) == 8
    assert {config["max_workers"] for config in CONFIGS.values()} == {3, 4}
    assert {config["post_producers"] for config in CONFIGS.values()} == {1, 2}


def test_activation_gates_accept_all_exact_boundaries():
    counts = passing_counts()
    gates = activation_gates(
        repeat_exact=True,
        complete_grid=True,
        opening_mismatches=0,
        cap_violations=0,
        counts=counts,
        changed_cells=640,
    )
    assert all(gates.values())


def test_activation_gates_reject_per_config_and_aggregate_shortfalls():
    counts = passing_counts()
    label = MODELS[0]
    counts[label]["worker_three"] = 87
    gates = activation_gates(
        repeat_exact=True,
        complete_grid=True,
        opening_mismatches=0,
        cap_violations=0,
        counts=counts,
        changed_cells=640,
    )
    assert not gates["each_config_worker_three_at_least_55_percent"]

    counts = passing_counts()
    for values in counts.values():
        values["worker_three"] = 111
    gates = activation_gates(
        repeat_exact=True,
        complete_grid=True,
        opening_mismatches=0,
        cap_violations=0,
        counts=counts,
        changed_cells=640,
    )
    assert not gates["aggregate_worker_three_at_least_70_percent"]


def test_mechanism_signature_excludes_label_score_and_d51_telemetry():
    row = {"terminal_turn": 300}
    for prefix in ("t50", "t100", "final"):
        for feature in (
            "score",
            "fruit",
            "wood",
            "workers",
            "plants",
            "harvested_fruit",
            "chops",
            "dropped_items",
        ):
            row[f"{prefix}_{feature}"] = 1
    altered = deepcopy(row)
    altered.update(
        {
            "model": "different",
            "t50_score": 99,
            "third_worker_turn": "88",
            "switch_turn": "0",
        }
    )
    assert mechanism_signature(row) == mechanism_signature(altered)
    altered["final_workers"] = 2
    assert mechanism_signature(row) != mechanism_signature(altered)
