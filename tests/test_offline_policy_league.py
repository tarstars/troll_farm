import copy

from cgauto.idle_harvest_study import fixed_fixture
from cgauto.offline_policy_league import (
    attach_live_deltas,
    map_features,
    resolve_seeds,
    robust_summary,
)


def test_robust_summary_reports_tail_and_trimmed_statistics() -> None:
    values = list(range(20))

    result = robust_summary(values)

    assert result["n"] == 20
    assert result["mean"] == 9.5
    assert result["median"] == 9.5
    assert result["trimmed_5pct_mean"] == 9.5
    assert result["worst_decile_mean"] == 0.5
    assert (result["wins"], result["ties"], result["losses"]) == (19, 1, 0)


def test_attach_live_deltas_uses_same_seed_and_opponent() -> None:
    rows = [
        {
            "seed": 7,
            "policy": "live",
            "opponent": "race",
            "paired_margin": 3,
            "paired_wood_edge": 2,
        },
        {
            "seed": 7,
            "policy": "stack",
            "opponent": "race",
            "paired_margin": 8,
            "paired_wood_edge": 1,
        },
    ]

    attach_live_deltas(rows)

    assert rows[0]["delta_vs_live_margin"] == 0
    assert rows[1]["delta_vs_live_margin"] == 5
    assert rows[1]["delta_vs_live_wood"] == -1


def test_map_features_are_seat_invariant() -> None:
    game = fixed_fixture()
    mirrored_seat_labels = copy.deepcopy(game)
    mirrored_seat_labels.shacks.reverse()

    assert map_features(game) == map_features(mirrored_seat_labels)


def test_resolve_seeds_supports_a_sparse_registry() -> None:
    assert resolve_seeds(10, 3, None) == [10, 11, 12]
    assert resolve_seeds(0, 99, "4, 23,32,43,44") == [4, 23, 32, 43, 44]
