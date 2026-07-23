import torch

from cgauto.rl_q6_proposal_env import Q6_ACTIONS, Q6_ACTION_FEATURES, Q6_STATE_FEATURES
from cgauto.train_d108a_recurrent_q6_ppo import HIDDEN, RecurrentProposalActorCritic


def test_d108_model_respects_dynamic_mask_and_shapes():
    torch.manual_seed(10801)
    model = RecurrentProposalActorCritic()
    batch = 3
    state = torch.randn(batch, Q6_STATE_FEATURES)
    proposals = torch.randn(batch, Q6_ACTIONS, Q6_ACTION_FEATURES)
    masks = torch.zeros(batch, Q6_ACTIONS, dtype=torch.uint8)
    masks[:, 0] = 1
    masks[0, 4] = 1
    masks[1, 9] = 1
    hidden = torch.zeros(batch, HIDDEN)
    action, logprob, entropy, value, next_hidden, logits = model.action_and_value(
        state, proposals, masks, hidden, deterministic=True
    )
    assert action.tolist()[2] == 0
    assert all(masks[index, selected] for index, selected in enumerate(action))
    assert logprob.shape == entropy.shape == value.shape == (batch,)
    assert next_hidden.shape == (batch, HIDDEN)
    assert logits.shape == (batch, Q6_ACTIONS)
    assert torch.isfinite(logprob).all()
    assert torch.isfinite(value).all()


def test_d108_sequence_statistics_are_finite():
    model = RecurrentProposalActorCritic()
    steps, batch = 2, 2
    state = torch.randn(steps, batch, Q6_STATE_FEATURES)
    proposals = torch.randn(steps, batch, Q6_ACTIONS, Q6_ACTION_FEATURES)
    masks = torch.zeros(steps, batch, Q6_ACTIONS, dtype=torch.uint8)
    masks[..., 0] = 1
    actions = torch.zeros(steps, batch, dtype=torch.long)
    dones = torch.zeros(steps, batch)
    values = model.sequence_statistics(
        state, proposals, masks, actions, dones, torch.zeros(batch, HIDDEN)
    )
    assert all(value.shape == (steps, batch) for value in values)
    assert all(torch.isfinite(value).all() for value in values)
