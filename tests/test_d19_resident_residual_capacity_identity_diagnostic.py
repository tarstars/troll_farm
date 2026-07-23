from __future__ import annotations

import numpy as np
import torch

from cgauto.d18_resident_residual_spatial_distillation import geometry_matrix
from cgauto.d19_resident_residual_capacity_identity_diagnostic import (
    LargeGeometryMlp,
    LargeSpatialScorer,
    opponent_matrix,
    parallel_geometry_matrix,
    parameter_count,
)
from cgauto.rl_resident_residual_env import OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH


def observations() -> np.ndarray:
    result = np.zeros((2, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8)
    result[:, 0, :4, :6] = 255
    result[:, 1, :4, :6] = 255
    result[0, 6, 1, 1] = 255
    result[1, 6, 2, 3] = 255
    result[:, 4, 0, 0] = 255
    result[:, 5, 3, 5] = 255
    return result


def test_parallel_geometry_is_identical_to_serial() -> None:
    source = observations()
    assert np.array_equal(
        parallel_geometry_matrix(source, workers=2), geometry_matrix(source)
    )


def test_research_models_have_frozen_capacity() -> None:
    assert parameter_count(LargeGeometryMlp(177)) == 33_153
    assert parameter_count(LargeGeometryMlp(183)) == 33_921
    assert parameter_count(LargeSpatialScorer(oracle=False)) == 22_301
    assert parameter_count(LargeSpatialScorer(oracle=True)) == 22_685


def test_oracle_identity_is_the_only_extra_spatial_input() -> None:
    obs = torch.from_numpy(observations())
    opponents = torch.eye(6)[:2]
    assert LargeSpatialScorer(oracle=False)(obs, opponents).shape == (2, 13)
    assert LargeSpatialScorer(oracle=True)(obs, opponents).shape == (2, 13)
    rows = [{"opponent": "resident"}, {"opponent": "mybot"}]
    encoded = opponent_matrix(rows)
    assert encoded.shape == (2, 6)
    assert encoded.sum(axis=1).tolist() == [1.0, 1.0]
    assert encoded[0, 0] == 1
    assert encoded[1, 5] == 1
