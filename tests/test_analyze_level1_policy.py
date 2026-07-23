import numpy as np

from cgauto.analyze_level1_policy import move_kind


def test_move_kind_prioritizes_current_home_and_species() -> None:
    observation = np.zeros((104, 11, 22), dtype=np.uint8)
    observation[7, 2, 3] = 255
    observation[38, 2, 3] = 255
    assert move_kind(observation, 2, 3) == "WAIT_CURRENT"
    observation[7, 2, 3] = 0
    observation[5, 2, 3] = 255
    assert move_kind(observation, 2, 3) == "HOME"
    observation[5, 2, 3] = 0
    assert move_kind(observation, 2, 3) == "LEMON"
