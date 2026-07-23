import numpy as np
import torch

from cgauto.train_d119a_long_fit_soft_value_q6 import EPOCHS, train_long_model


def test_d119_changes_only_horizon_and_remains_deterministic():
    assert EPOCHS == 80
    generator = np.random.Generator(np.random.PCG64(119))
    actions = generator.normal(size=(8, 3, 379)).astype(np.float32)
    actions[:, :, 0] = 1.0
    states = generator.normal(size=(8, 64)).astype(np.float32)
    values = torch.tensor([[3.0, 2.0, 1.0], [1.0, 3.0, 2.0]] * 4)
    dataset = {
        "action_features": torch.from_numpy(actions),
        "valid": torch.ones((8, 3), dtype=torch.bool),
        "state_features": torch.from_numpy(states),
        "soft_rank_targets": torch.softmax(values / 10.0, dim=1),
        "proposal_values": values,
        "act_targets": torch.tensor([True, False] * 4),
    }
    first, first_summary = train_long_model(dataset, 11901, epochs=2)
    second, second_summary = train_long_model(dataset, 11901, epochs=2)
    assert first_summary["model_hash"] == second_summary["model_hash"]
    assert all(
        torch.equal(first.state_dict()[name], second.state_dict()[name])
        for name in first.state_dict()
    )
