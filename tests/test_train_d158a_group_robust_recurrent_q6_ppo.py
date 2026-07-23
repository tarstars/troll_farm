import numpy as np

from cgauto.rl_macro_env import OPPONENTS
from cgauto.train_d158a_group_robust_recurrent_q6_ppo import (
    FROZEN,
    OBJECTIVES,
    VARIANT_ORDER,
    family_weights,
    objective_return,
    output_paths,
    update_family_ema,
)


def terminal(margin=20, own_delta=10, opponent="resident"):
    return {
        "margin_delta": margin,
        "own_score": 100 + own_delta,
        "baseline_own_score": 100,
        "opponent": opponent,
    }


def test_d158_frozen_ranges_and_geometry_exclude_reserved_maps():
    assert VARIANT_ORDER == tuple(OBJECTIVES)
    assert FROZEN["total_transitions"] == 64_800
    assert FROZEN["num_envs"] * FROZEN["rollout_steps"] == 1_200
    assert FROZEN["total_transitions"] // 1_200 == 54
    ranges = (
        range(FROZEN["train_seed_base"], FROZEN["train_seed_base"] + FROZEN["train_map_pool"]),
        range(
            FROZEN["evaluation_seed_base"],
            FROZEN["evaluation_seed_base"] + FROZEN["evaluation_maps"],
        ),
        range(
            FROZEN["confirmation_seed_base"],
            FROZEN["confirmation_seed_base"] + FROZEN["confirmation_maps"],
        ),
    )
    assert not any(seed in range(9_844_200, 9_844_216) for values in ranges for seed in values)
    assert not (set(ranges[0]) & set(ranges[1]))
    assert not (set(ranges[1]) & set(ranges[2]))


def test_d158_objective_ablation_is_exact():
    weights = np.ones(len(OPPONENTS))
    assert objective_return(terminal(margin=60), "pooled_margin", weights) == 0.6
    assert objective_return(terminal(margin=60), "capped_margin", weights) == 0.4
    assert objective_return(terminal(margin=60, own_delta=-20), "own_protected", weights) == 0.3
    assert objective_return(terminal(margin=-60), "capped_margin", weights) == -0.6


def test_d158_group_dro_upweights_weak_families_and_normalizes():
    ema = np.arange(len(OPPONENTS), dtype=np.float64) * 10.0
    initialized = np.ones(len(OPPONENTS), dtype=np.bool_)
    weights = family_weights(ema, initialized)
    assert abs(weights.mean() - 1.0) < 1e-12
    assert np.all(weights > 0)
    assert weights[0] > weights[-1]
    row = terminal(opponent=OPPONENTS[0])
    assert objective_return(row, "group_dro_own", weights) > objective_return(
        row, "own_protected", np.ones_like(weights)
    )


def test_d158_group_ema_updates_only_observed_families():
    ema = np.zeros(len(OPPONENTS), dtype=np.float64)
    initialized = np.zeros(len(OPPONENTS), dtype=np.bool_)
    update_family_ema(
        ema,
        initialized,
        [
            {"opponent": OPPONENTS[0], "margin_delta": -10},
            {"opponent": OPPONENTS[0], "margin_delta": 10},
        ],
    )
    assert initialized[0]
    assert ema[0] == 0
    assert not initialized[1:].any()
    assert np.array_equal(family_weights(ema, initialized), np.ones(len(OPPONENTS)))


def test_d158_output_paths_are_variant_separated():
    paths = [output_paths(variant) for variant in VARIANT_ORDER]
    for key in paths[0]:
        assert len({str(item[key]) for item in paths}) == len(paths)

