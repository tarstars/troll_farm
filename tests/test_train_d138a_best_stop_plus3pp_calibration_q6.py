from cgauto.train_d138a_best_stop_plus3pp_calibration_q6 import boosted_target


def test_boosted_target_adds_frozen_three_percentage_points():
    assert boosted_target(768, 513) == 536
    assert boosted_target(1024, 700) == 731
