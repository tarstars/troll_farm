from cgauto.train_d109a_long_recurrent_q6_ppo import FROZEN


def test_d109_changes_only_duration_diversity_and_vector_geometry():
    assert FROZEN["model_seed"] == 10_801
    assert FROZEN["num_envs"] == 60
    assert FROZEN["rollout_steps"] == 20
    assert FROZEN["total_transitions"] == 64_800
    assert FROZEN["total_transitions"] // (
        FROZEN["num_envs"] * FROZEN["rollout_steps"]
    ) == 54
    assert FROZEN["train_map_pool"] == 128
    assert FROZEN["evaluation_maps"] == 32
    for key in (
        "learning_rate",
        "adam_epsilon",
        "gamma",
        "gae_lambda",
        "clip_coef",
        "entropy_coef",
        "value_coef",
        "max_grad_norm",
        "target_kl",
    ):
        assert key in FROZEN
