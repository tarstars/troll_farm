import numpy as np

from cgauto import analyze_d156a_hierarchical_semantic_value_policy as d156


def semantic_action() -> np.ndarray:
    action = np.zeros(379, dtype=np.float32)
    action[0] = 1.0
    action[1] = -1.0
    action[3] = 1.0
    action[5] = -1.0
    action[8] = 1.0
    action[10] = -1.0
    action[14] = 1.0
    action[15] = -1.0
    action[17] = 1.0
    action[20] = -1.0
    action[23] = 1.0
    action[25] = 0.3
    action[26] = 0.8
    return action


def state() -> np.ndarray:
    result = np.zeros(64, dtype=np.float32)
    result[2] = 1.0
    result[56] = 0.5
    result[58] = 0.1
    result[62] = 1.0
    return result


def test_semantic_decoder_and_state_regime_are_stable():
    decoded = d156.decode_action(semantic_action())
    assert decoded["jobs"] == (2, 3, 4)
    assert decoded["job_owner"] == (2, 3, 4, 2, 3)
    assert (decoded["rank_one"], decoded["rank_two"]) == (1, 3)
    regime = d156.state_regime(state())
    assert regime == {
        "phase": 1,
        "workers": 3,
        "crop_bucket": 1,
        "previous_kind": 2,
    }


def test_hierarchical_posterior_shrinks_to_parent_and_reports_support():
    mean, deviation, count = d156.posterior([16.0, 160.0, 2400.0], 2.0)
    assert mean == 6.0
    assert count == 16
    assert deviation > 0.0
    unseen = d156.posterior(None, mean)
    assert unseen == (mean, 0.0, 0)


def test_variant_score_uses_fine_support_and_lcb_is_conservative():
    action_keys = d156.keys(state(), semantic_action())
    stats = {
        name: {}
        for name in (
            "jobs",
            "job_owner",
            "job_owner_phase",
            "job_owner_phase_rank",
            "job_owner_regime",
        )
    }
    stats["job_owner"][action_keys["job_owner"]] = [16.0, 160.0, 2400.0]
    stats["job_owner_phase"][action_keys["job_owner_phase"]] = [
        16.0,
        192.0,
        3200.0,
    ]
    mean, support = d156.score_action("job_owner_phase", stats, action_keys)
    lower, lower_support = d156.score_action(
        "job_owner_phase_lcb", stats, action_keys
    )
    assert support == lower_support == 16
    assert lower < mean
