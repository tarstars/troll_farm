from __future__ import annotations

import copy

import numpy as np
import torch

from cgauto.d17_resident_residual_precision_distillation import (
    LinearScorer,
    MlpScorer,
    feature_names,
    feature_row,
    parameter_count,
    score,
)


def example_row() -> dict:
    row = {
        "turn": 123,
        "ordinal": 1,
        "worker_count": 2,
        "ms": 2,
        "cc": 3,
        "hp": 1,
        "chop": 2,
        "free": 2,
        "state_score": 77,
        "state_opponent_score": 81,
        "state_margin": -4,
        "state_wood_edge": 9,
        "plants": 19,
        "local_plant_health": 12,
        "local_plant_fruits": 2,
        "near_home": 0,
        "near_iron": 1,
        "intent_age": 3,
        "legal_actions": 4,
        "local_plant_type": "APPLE",
        "resident_verb": "MOVE",
        "resident_plane": 0,
        "resident_command": "MOVE 4 7 8",
        "previous_verb": "HARVEST",
        "previous_plane": 1,
        "other_verb": "CHOP",
        "other_plane": 2,
        "alternative_plane": 11,
        "alternative_command": "PICK 4 APPLE",
    }
    row.update({f"carry{item}": item % 3 for item in range(6)})
    row.update({f"inv{item}": 2 * item + 1 for item in range(6)})
    return row


def test_feature_schema_is_fixed_and_excludes_identity_and_outcomes() -> None:
    names = feature_names()
    assert len(names) == len(set(names))
    original = feature_row(example_row())
    assert len(original) == len(names)

    changed = copy.deepcopy(example_row())
    changed.update(
        {
            "scenario": 999999,
            "map_seed": 88888,
            "opponent": "invented",
            "x": 21,
            "y": 10,
            "candidate_index": 12345,
            "baseline_margin": -500,
            "alternative_margin": 500,
            "margin_advantage": 1000,
            "elapsed_us": 999999,
        }
    )
    assert feature_row(changed) == original


def test_compact_scorers_fit_the_payload_gate_and_score_rows() -> None:
    inputs = len(feature_names())
    features = np.asarray([feature_row(example_row())], dtype=np.float32)
    for family, model in (
        ("binary_linear", LinearScorer(inputs)),
        ("binary_mlp", MlpScorer(inputs)),
        ("value_mlp", MlpScorer(inputs)),
    ):
        values = score(model, family, features)
        assert values.shape == (1,)
        assert np.isfinite(values).all()
        assert parameter_count(model) < 3_500
    assert sum(parameter_count(MlpScorer(inputs)) for _ in range(3)) < 10_000


def test_identical_resident_action_is_explicitly_visible() -> None:
    row = example_row()
    row["resident_plane"] = 11
    row["resident_command"] = row["alternative_command"]
    values = dict(zip(feature_names(), feature_row(row), strict=True))
    assert values["same_as_resident_plane"] == 1.0
    assert values["same_as_resident_command"] == 1.0
