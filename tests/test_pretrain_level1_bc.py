import torch

from cgauto.pretrain_level1_bc import masked_cross_entropy
from cgauto.train_level1_ppo import SpatialActorCritic


def test_masked_cross_entropy_accepts_only_legal_teacher_label() -> None:
    model = SpatialActorCritic()
    observations = torch.zeros((2, 104, 11, 22), dtype=torch.uint8)
    observations[:, 0] = 255
    masks = torch.zeros((2, 13, 11, 22), dtype=torch.uint8)
    masks.view(2, -1)[0, 5] = 1
    masks.view(2, -1)[1, 17] = 1
    labels = torch.tensor([5, 17])
    loss, accuracy = masked_cross_entropy(model, observations, masks, labels)
    assert torch.isfinite(loss)
    assert accuracy.item() == 1.0
