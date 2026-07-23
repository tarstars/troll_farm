from __future__ import annotations

import numpy as np
import torch

from cgauto.d18_resident_residual_spatial_distillation import (
    GeometryMlp,
    TinySpatialScorer,
    geometry_feature_names,
    geometry_feature_row,
    parameter_count,
)
from cgauto.rl_resident_residual_env import (
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
)


def observation() -> np.ndarray:
    obs = np.zeros((OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8)
    obs[0, :5, :7] = 255
    obs[1, :5, :7] = 255
    obs[4, 0, 0] = 255
    obs[5, 4, 6] = 255
    obs[6, 2, 3] = 255
    obs[7, 2, 3] = 255
    obs[8, 2, 5] = 255
    obs[2, 3, 3] = 255
    obs[3, 1, 4] = 255
    obs[31, 2, 4] = 255
    obs[34, 2, 4] = 255
    return obs


def test_geometry_features_include_exact_path_distances() -> None:
    values = dict(
        zip(geometry_feature_names(), geometry_feature_row(observation()), strict=True)
    )
    assert values["plum_plant_minimum_distance"] == 1 / 32
    assert values["ripe_plum_minimum_distance"] == 1 / 32
    assert values["opponent_worker_minimum_distance"] == 2 / 32
    assert values["other_own_worker_reachable_count"] == 0
    assert values["iron_access_minimum_distance"] == 0


def test_spatial_and_geometry_models_fit_source_budget() -> None:
    spatial = TinySpatialScorer()
    geometry = GeometryMlp(116 + len(geometry_feature_names()))
    assert parameter_count(spatial) == 5_401
    assert parameter_count(geometry) == 4_585
    assert parameter_count(spatial) < 10_000
    assert parameter_count(geometry) < 10_000


def test_spatial_model_emits_one_score_per_action_plane() -> None:
    model = TinySpatialScorer()
    inputs = torch.from_numpy(observation()[None])
    output = model(inputs)
    assert output.shape == (1, 13)
    assert torch.isfinite(output).all()
