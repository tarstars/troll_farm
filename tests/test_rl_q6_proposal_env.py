import numpy as np

from cgauto.rl_q6_proposal_env import (
    Q6_ACTIONS,
    Q6_ACTION_FEATURES,
    Q6_EXPERTS,
    Q6_EXPERT_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
    load_experts,
)


def test_q6_expert_loader_has_exact_shape_and_integer_coefficients():
    experts = load_experts()
    assert experts.shape == (Q6_EXPERTS, Q6_EXPERT_FEATURES)
    assert experts.dtype == np.float32
    np.testing.assert_array_equal(experts, np.round(experts))


def test_q6_vector_action_zero_has_exact_paired_return():
    with Q6ProposalVecEnv(2, 9_829_000, map_pool=1) as env:
        assert env.state_features.shape == (2, Q6_STATE_FEATURES)
        assert env.action_features.shape == (2, Q6_ACTIONS, Q6_ACTION_FEATURES)
        completed = []
        returns = np.zeros(2, dtype=np.float64)
        for _ in range(32):
            _, _, _, rewards, info = env.step(np.zeros(2, dtype=np.int32))
            returns += rewards
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                assert terminal["margin_delta"] == 0
                assert abs(returns[slot]) < 1e-7
                assert terminal["intervention_batches"] == 0
                assert terminal["invalid_direct_commands"] == 0
                completed.append(terminal)
                returns[slot] = 0.0
            if len(completed) >= 2:
                break
        assert len(completed) >= 2
