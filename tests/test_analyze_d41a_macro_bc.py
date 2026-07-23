from __future__ import annotations

import numpy as np

from cgauto.analyze_d41a_macro_bc import CELLS, exact_prior_index, exact_prior_order


def row(
    *,
    kind: int = 0,
    eta: int = 0,
    reduction: int = 0,
    rate: int = 0,
    plant: int | None = None,
    turn: int = 0,
    workers: int = 1,
) -> np.ndarray:
    value = np.zeros(44, dtype=np.float32)
    value[1] = turn / 300
    value[2] = workers / 3
    value[20 + kind] = 1
    value[26] = eta / 300
    value[28] = reduction / 20
    value[29] = rate / 50_000
    value[43] = -1 if plant is None else plant / (CELLS - 1)
    return value


def test_exact_prior_train_goal_follows_workforce_and_deadline() -> None:
    actions = np.array([0, CELLS, 2 * CELLS], dtype=np.int32)
    features = np.stack([row(workers=1)] * 3)
    assert exact_prior_index(features, actions, 0) == 1
    features = np.stack([row(workers=2)] * 3)
    assert exact_prior_index(features, actions, 0) == 2
    features = np.stack([row(workers=2, turn=271)] * 3)
    assert exact_prior_index(features, actions, 0) == 0


def test_exact_prior_deficit_uses_reduction_eta_then_bank() -> None:
    features = np.stack(
        [
            row(kind=2, eta=2, reduction=3),
            row(kind=1, eta=2, reduction=3),
            row(kind=3, eta=1, reduction=2),
        ]
    )
    actions = np.array([5 * CELLS + 3, 4 * CELLS, 6 * CELLS + 2])
    assert exact_prior_index(features, actions, 1) == 1


def test_exact_prior_evacuation_excludes_idle_and_uses_rust_cell_order() -> None:
    # Cell (1, 1) has row-major index 23, while (2, 0) has index 2. Rust's
    # tuple ordering selects (1, 1), proving the decoder is not sorting spatial IDs.
    features = np.stack(
        [row(kind=0, eta=0), row(kind=2, eta=3), row(kind=2, eta=3)]
    )
    actions = np.array([3 * CELLS, 5 * CELLS + 23, 5 * CELLS + 2])
    assert exact_prior_index(features, actions, 2) == 1


def test_exact_prior_rate_uses_value_eta_then_kind() -> None:
    features = np.stack(
        [
            row(kind=4, eta=4, rate=30_000),
            row(kind=2, eta=3, rate=30_000),
            row(kind=1, eta=1, rate=29_999),
        ]
    )
    actions = np.array([7 * CELLS + 4, 5 * CELLS + 5, 4 * CELLS])
    assert exact_prior_index(features, actions, 3) == 1
    assert sorted(exact_prior_order(features, actions, 3)) == [0, 1, 2]
