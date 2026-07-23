import numpy as np
import torch

from cgauto.train_d117a_factorized_q6_ranker_state_gate import (
    factorized_dataset,
    fit_policy_gates,
    model_fit_gates,
    train_factorized_model,
)


def arm(boundary, slot, own, opponent, state):
    row = {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "boundary_index": str(boundary),
        "slot": str(slot),
        "own_score": str(own),
        "opponent_score": str(opponent),
    }
    row.update({f"state_{index:03}": str(value) for index, value in enumerate(state)})
    return row


def test_factorized_dataset_separates_rank_and_act_targets():
    task = (1, 0, "resident")
    roots = [(task, 0), (task, 1)]
    first_state = np.arange(64, dtype=np.float32) / 64.0
    second_state = first_state[::-1].copy()
    arms = [
        arm(0, 1, 12, 10, first_state),
        arm(0, 2, 11, 10, first_state),
        arm(1, 1, 9, 10, second_state),
        arm(1, 2, 10, 10, second_state),
    ]
    x = np.zeros((4, 379), dtype=np.float64)
    x[:, 0] = 1.0
    data = {
        "arms": arms,
        "x": x,
        "y": np.asarray([2.0, 1.0, -1.0, 0.0]),
        "root_keys": [roots[0], roots[0], roots[1], roots[1]],
        "baseline_by_task": {
            task: {"own_score": "10", "opponent_score": "10"}
        },
        "arms_by_root": {roots[0]: arms[:2], roots[1]: arms[2:]},
    }
    dataset = factorized_dataset(data)
    assert dataset["rank_targets"].tolist() == [0, 1]
    assert dataset["act_targets"].tolist() == [True, False]
    assert np.array_equal(dataset["state_features"][0].numpy(), first_state)
    assert dataset["summary"]["target_act_roots"] == 1


def test_factorized_training_is_deterministic_and_finite():
    generator = np.random.Generator(np.random.PCG64(117))
    actions = generator.normal(size=(8, 3, 379)).astype(np.float32)
    actions[:, :, 0] = 1.0
    states = generator.normal(size=(8, 64)).astype(np.float32)
    dataset = {
        "action_features": torch.from_numpy(actions),
        "valid": torch.ones((8, 3), dtype=torch.bool),
        "state_features": torch.from_numpy(states),
        "rank_targets": torch.tensor([0, 1, 2, 0, 1, 2, 0, 1]),
        "act_targets": torch.tensor([True, False] * 4),
    }
    first, first_summary = train_factorized_model(
        dataset, 11701, epochs=2, root_batch_size=4, threads=1
    )
    second, second_summary = train_factorized_model(
        dataset, 11701, epochs=2, root_batch_size=4, threads=1
    )
    assert first_summary["model_hash"] == second_summary["model_hash"]
    assert first_summary["parameters"] == 6_626
    assert np.isfinite(first_summary["final_rank_cross_entropy"])
    assert np.isfinite(first_summary["final_gate_binary_cross_entropy"])
    assert all(
        torch.equal(first.state_dict()[name], second.state_dict()[name])
        for name in first.state_dict()
    )


def test_prospective_fit_gates_accept_structurally_useful_model():
    summary = {
        "train_rank_top1_accuracy": 0.3,
        "train_rank_top1_accuracy_on_act_roots": 0.25,
        "train_gate_balanced_accuracy": 0.7,
        "train_gate_act_recall": 0.65,
        "train_gate_wait_recall": 0.75,
    }
    metrics = {
        "mean_margin_delta": 3.0,
        "strict_improvement_rate": 0.3,
        "fold_mean_margin_delta": {"0": 2.0, "1": 4.0},
        "worst_family": -2.0,
        "positive_families": 7,
        "intervention_rate": 0.5,
        "crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.92,
    }
    assert all(model_fit_gates(summary).values())
    assert all(fit_policy_gates(metrics).values())
