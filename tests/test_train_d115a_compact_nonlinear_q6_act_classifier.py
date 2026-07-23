import numpy as np

from cgauto.train_d115a_compact_nonlinear_q6_act_classifier import (
    FEATURES,
    CompactActClassifier,
    admission,
    canonical_model_hash,
    class_balanced_root_weights,
    parameter_count,
    train_model,
)


def test_root_and_class_balancing_splits_global_mass_equally():
    targets = np.asarray([2.0, -1.0, -3.0, 4.0, 0.0], dtype=np.float64)
    roots = [("a",), ("a",), ("a",), ("b",), ("c",)]
    weights, summary = class_balanced_root_weights(roots, targets)
    positive = targets > 0.0
    assert np.isclose(weights[positive].sum(), 0.5)
    assert np.isclose(weights[~positive].sum(), 0.5)
    assert summary["positive_arms"] == 2
    assert summary["roots"] == 3


def test_compact_model_has_frozen_size_and_training_is_reproducible():
    generator = np.random.Generator(np.random.PCG64(115))
    x = generator.normal(size=(12, FEATURES)).astype(np.float64)
    x[:, 0] = 1.0
    y = np.asarray([1.0, -1.0] * 6)
    roots = [(index // 3,) for index in range(len(y))]
    first, first_summary = train_model(
        x, y, roots, 11501, epochs=2, batch_size=4, threads=1
    )
    second, second_summary = train_model(
        x, y, roots, 11501, epochs=2, batch_size=4, threads=1
    )
    assert parameter_count(CompactActClassifier()) == 6_097
    assert canonical_model_hash(first) == canonical_model_hash(second)
    assert first_summary["model_hash"] == second_summary["model_hash"]
    assert np.isfinite(first_summary["final_full_weighted_loss"])


def test_validation_admission_accepts_frozen_robust_sparse_controller():
    metrics = {
        "mean_margin_delta": 3.0,
        "strict_improvement_rate": 0.4,
        "fold_mean_margin_delta": {"0": 2.0, "1": 4.0},
        "worst_family": -2.0,
        "positive_families": 6,
        "mean_own_score_delta": 1.0,
        "mean_opponent_score_delta": -2.0,
        "intervention_rate": 0.5,
        "crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.92,
    }
    assert all(admission(metrics).values())
