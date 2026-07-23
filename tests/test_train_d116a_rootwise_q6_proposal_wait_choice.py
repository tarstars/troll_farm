import numpy as np
import torch

from cgauto.train_d116a_rootwise_q6_proposal_wait_choice import (
    root_choice_dataset,
    train_choice_model,
)


def arm(boundary, slot, own, opponent):
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "boundary_index": str(boundary),
        "slot": str(slot),
        "own_score": str(own),
        "opponent_score": str(opponent),
    }


def test_root_choice_dataset_targets_exact_best_arm_or_wait():
    task = (1, 0, "resident")
    roots = [(task, 0), (task, 1)]
    arms = [
        arm(0, 1, 12, 10),
        arm(0, 2, 11, 10),
        arm(1, 1, 9, 10),
        arm(1, 2, 10, 10),
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
        "arms_by_root": {
            roots[0]: arms[:2],
            roots[1]: arms[2:],
        },
    }
    dataset = root_choice_dataset(data)
    assert dataset["targets"].tolist() == [1, 0]
    assert dataset["valid"].sum().item() == 4
    assert dataset["summary"]["target_act_roots"] == 1
    assert dataset["summary"]["target_wait_roots"] == 1


def test_rootwise_training_is_deterministic_and_finite():
    generator = np.random.Generator(np.random.PCG64(116))
    features = generator.normal(size=(8, 3, 379)).astype(np.float32)
    features[:, :, 0] = 1.0
    dataset = {
        "features": torch.from_numpy(features),
        "valid": torch.ones((8, 3), dtype=torch.bool),
        "targets": torch.tensor([0, 1, 2, 3, 0, 1, 2, 3]),
    }
    first, first_summary = train_choice_model(
        dataset, 11601, epochs=2, root_batch_size=4, threads=1
    )
    second, second_summary = train_choice_model(
        dataset, 11601, epochs=2, root_batch_size=4, threads=1
    )
    assert first_summary["model_hash"] == second_summary["model_hash"]
    assert np.isfinite(first_summary["final_full_root_cross_entropy"])
    assert all(
        torch.equal(first.state_dict()[name], second.state_dict()[name])
        for name in first.state_dict()
    )
