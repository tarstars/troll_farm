from __future__ import annotations

import numpy as np

from cgauto.rl_resident_residual_env import (
    ACTION_SIZE,
    OBS_SIZE,
    OPPONENTS,
)


def test_residual_shapes_and_panel_are_frozen():
    assert OBS_SIZE == 137 * 11 * 22
    assert ACTION_SIZE == 13 * 11 * 22
    assert OPPONENTS == (
        "resident",
        "gold_adaptive",
        "compact_gold",
        "norx_native_three",
        "legend_balanced",
        "mybot",
    )
    assert np.dtype(np.uint8).itemsize == 1
