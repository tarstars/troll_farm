import torch

from cgauto.train_d134a_block_transfer_selected_soft_value_q6 import (
    aggregate_policy_metrics,
    held_policy_gates,
    merge_soft_datasets,
    selection_key,
)
from cgauto import analyze_d133b_q6_support_semantics as d133b


def _dataset(root, proposals):
    valid = torch.ones((1, proposals), dtype=torch.bool)
    values = torch.arange(proposals, dtype=torch.float32)[None, :]
    return {
        "action_features": torch.ones((1, proposals, 379)),
        "valid": valid,
        "state_features": torch.ones((1, 64)),
        "act_targets": torch.tensor([True]),
        "proposal_values": values,
        "soft_rank_targets": torch.softmax(values / 10.0, dim=1),
        "root_order": [root],
    }


def test_merge_soft_datasets_pads_proposals_without_target_mass_loss():
    merged = merge_soft_datasets(
        [_dataset(((1, 0, "resident"), 0), 2), _dataset(((2, 0, "resident"), 0), 3)]
    )
    assert merged["action_features"].shape == (2, 3, 379)
    assert merged["valid"].tolist() == [[True, True, False], [True, True, True]]
    assert torch.isneginf(merged["proposal_values"][0, 2])
    assert torch.allclose(merged["soft_rank_targets"].sum(1), torch.ones(2))


def _metrics(mean):
    family = {
        "resident": mean,
        "compact_gold": mean,
        "gold_adaptive": mean,
        "silver_boss": mean,
        "legend_balanced": mean,
        "norx_native_three": mean,
        "script_boss": mean,
        "mybot": mean,
    }
    return {
        "tasks": 256,
        "mean_margin_delta": mean,
        "strict_improvement_rate": 0.5,
        "mean_own_score_delta": 1.0,
        "mean_opponent_score_delta": -1.0,
        "family_mean_margin_delta": family,
        "positive_families": 8,
        "worst_family": mean,
        "intervention_rate": 0.8,
        "crop_rate": 1.0,
        "control_crop_rate": 1.0,
        "worker_three_rate": 0.9,
        "control_worker_three_rate": 0.9,
        "positive_score_ties": 0,
    }


def test_held_metrics_pool_equal_blocks_and_require_each_nonnegative():
    pooled = aggregate_policy_metrics([_metrics(value) for value in (1.0, 2.0, 3.0, 4.0)])
    assert pooled["tasks"] == 1024
    assert pooled["mean_margin_delta"] == 2.5
    assert held_policy_gates(pooled)["every_block_nonnegative"]
    bad = aggregate_policy_metrics([_metrics(value) for value in (-1.0, 4.0, 4.0, 4.0)])
    assert not held_policy_gates(bad)["every_block_nonnegative"]


def test_selection_key_prefers_worst_block_before_pooled_mean():
    safer = {
        "seed": 1,
        "held_policy_metrics": {
            **aggregate_policy_metrics([_metrics(2.0)] * 4),
            "block_mean_margin_delta": {"0": 1.0, "1": 2.0, "2": 2.0, "3": 3.0},
        },
    }
    volatile = {
        "seed": 2,
        "held_policy_metrics": {
            **aggregate_policy_metrics([_metrics(5.0)] * 4),
            "block_mean_margin_delta": {"0": 0.5, "1": 6.0, "2": 6.0, "3": 7.5},
        },
    }
    assert selection_key(safer) > selection_key(volatile)


def test_d134_inherits_only_the_frozen_d133b_support_repair():
    mechanics = {
        "gates": {
            "supported_tasks_at_least_90pct": False,
            "reward_identity_below_1e_4": True,
        },
        "details": {},
    }
    assert d133b.exact_mechanics_without_support_gate(mechanics)["pass"]
    mechanics["gates"]["reward_identity_below_1e_4"] = False
    assert not d133b.exact_mechanics_without_support_gate(mechanics)["pass"]
