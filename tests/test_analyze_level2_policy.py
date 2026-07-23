from __future__ import annotations

import numpy as np

from cgauto.analyze_level2_policy import needed_work_kind


def test_needed_work_kind_distinguishes_recipe_deficit() -> None:
    observation = np.zeros((104, 11, 22), dtype=np.uint8)
    mask = np.zeros((13, 11, 22), dtype=np.uint8)
    observation[7, 2, 3] = 255
    observation[38, 2, 3] = 255
    mask[1, 2, 3] = 1
    assert needed_work_kind(observation, mask) is None
    observation[95, :, :] = 80
    assert needed_work_kind(observation, mask) == "HARVEST"


def test_needed_work_kind_detects_iron_and_ignores_banana() -> None:
    observation = np.zeros((104, 11, 22), dtype=np.uint8)
    mask = np.zeros((13, 11, 22), dtype=np.uint8)
    observation[7, 4, 5] = 255
    observation[50, 4, 5] = 255
    observation[97, :, :] = 100
    mask[1, 4, 5] = 1
    mask[4, 4, 5] = 1
    assert needed_work_kind(observation, mask) == "MINE"
