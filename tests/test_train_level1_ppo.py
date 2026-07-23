from __future__ import annotations

from types import SimpleNamespace

import torch
import pytest

from cgauto.rl_level1_env import ACTION_SIZE
from cgauto.rl_level5_env import Level5CropFirstRepeatedPressureReacquire180VecEnv
from cgauto.train_level1_ppo import (
    SpatialActorCritic,
    evaluate,
    legal_teacher_auxiliary_loss,
    level5_env_class,
    level5_mechanism_gate,
    load_model_weights_npz,
    resolve_device,
    save_model_weights_npz,
    validate_evaluation_baseline,
)


def test_model_shapes_parameter_budget_and_masking() -> None:
    torch.manual_seed(1)
    model = SpatialActorCritic()
    observations = torch.zeros((3, 104, 11, 22), dtype=torch.uint8)
    observations[:, 0] = 255
    masks = torch.zeros((3, 13, 11, 22), dtype=torch.uint8)
    legal = torch.tensor([0, 123, ACTION_SIZE - 1])
    masks.view(3, -1)[torch.arange(3), legal] = 1
    actions, logprob, entropy, values = model.action_and_value(observations, masks)
    assert torch.equal(actions, legal)
    assert logprob.shape == (3,)
    assert entropy.shape == (3,)
    assert values.shape == (3,)
    assert sum(parameter.numel() for parameter in model.parameters()) < 40_000


def test_device_resolution_is_explicit() -> None:
    assert resolve_device("cpu") == torch.device("cpu")
    if not torch.cuda.is_available():
        with pytest.raises(SystemExit, match="available CUDA device"):
            resolve_device("cuda")


def test_model_weight_npz_roundtrip_is_torch_version_neutral(tmp_path) -> None:
    torch.manual_seed(19)
    source = SpatialActorCritic()
    path = tmp_path / "weights.npz"
    save_model_weights_npz(source, path)

    torch.manual_seed(23)
    restored = SpatialActorCritic()
    load_model_weights_npz(restored, path)

    for name, tensor in source.state_dict().items():
        assert torch.equal(restored.state_dict()[name], tensor)


def test_teacher_auxiliary_skips_illegal_off_teacher_labels() -> None:
    logits = torch.tensor([[2.0, 0.0, -1.0], [0.0, 1.0, 2.0]])
    legal = torch.tensor([[True, False, False], [True, False, True]])
    masked = logits.masked_fill(~legal, torch.finfo(logits.dtype).min)
    teacher_actions = torch.tensor([1, 2])
    loss, accuracy, teacher_legal = legal_teacher_auxiliary_loss(
        masked, legal, teacher_actions
    )
    assert torch.isfinite(loss)
    assert accuracy.item() == 1.0
    assert teacher_legal.tolist() == [False, True]


def test_evaluate_collects_the_exact_seed_interval() -> None:
    torch.manual_seed(2)
    result = evaluate(
        SpatialActorCritic(), seed_base=20_000, episodes=7, num_envs=3
    )
    assert [row["seed"] for row in result.rows] == list(range(20_000, 20_007))


def test_evaluate_level2_collects_recipe_groups() -> None:
    torch.manual_seed(3)
    result = evaluate(
        SpatialActorCritic(),
        seed_base=21_000,
        episodes=17,
        num_envs=3,
        curriculum_level=2,
        max_turns=20,
    )
    assert [row["seed"] for row in result.rows] == list(range(21_000, 21_017))
    assert result.by_recipe is not None
    assert sum(bucket["episodes"] for bucket in result.by_recipe.values()) == 17
    assert all("initial_total_deficit" in row for row in result.rows)


def test_evaluate_level3_collects_renewable_milestones() -> None:
    torch.manual_seed(4)
    result = evaluate(
        SpatialActorCritic(),
        seed_base=22_000,
        episodes=7,
        num_envs=3,
        curriculum_level=3,
        max_turns=20,
    )
    assert [row["seed"] for row in result.rows] == list(range(22_000, 22_007))
    assert result.target == [2, 2, 0, 2]
    assert result.required_score_gain == 12
    assert result.created_crop_rate is not None
    assert result.renewable_harvest_rate is not None
    assert all("training_turn" in row for row in result.rows)
    assert all("score_gain" in row for row in result.rows)


def test_level5_d11_selection_and_destruction_telemetry() -> None:
    assert (
        level5_env_class(
            "crop-first-funded-trio-repeated-pressure-reacquire-180"
        )
        is Level5CropFirstRepeatedPressureReacquire180VecEnv
    )
    with pytest.raises(ValueError, match="unsupported Level-5 opponent mode"):
        level5_env_class("missing-mode")

    torch.manual_seed(5)
    result = evaluate(
        SpatialActorCritic(),
        seed_base=23_000,
        episodes=7,
        num_envs=3,
        curriculum_level=5,
        max_turns=240,
        level5_opponent_mode=(
            "crop-first-funded-trio-repeated-pressure-reacquire-180"
        ),
    )
    assert result.opponent_crop_destruction_rate is not None
    assert result.opponent_crop_destruction_at_least_two_rate is not None
    assert result.opponent_crop_destruction_at_least_three_rate is not None
    assert result.max_opponent_crop_destructions is not None
    assert result.max_opponent_crop_destructions <= 3


def test_level5_mechanism_gate_covers_repeated_pressure() -> None:
    metrics = {
        "opponent_training_rate": 0.98,
        "opponent_third_worker_training_rate": 0.85,
        "trained_with_funding_receipt_rate": 1.0,
        "third_trained_with_fresh_funding_receipt_rate": 1.0,
        "opponent_second_worker_productive_rate": 0.98,
        "opponent_third_worker_productive_rate": 0.80,
        "opponent_crop_creation_rate": 0.95,
        "opponent_renewable_harvest_rate": 0.80,
        "opponent_crop_destruction_rate": 0.95,
        "opponent_crop_destruction_at_least_two_rate": 0.85,
        "opponent_crop_destruction_at_least_three_rate": 0.70,
        "max_opponent_workers": 3,
        "max_opponent_crop_destructions": 3,
    }
    assert level5_mechanism_gate(SimpleNamespace(**metrics))
    metrics["opponent_crop_destruction_at_least_three_rate"] = 0.69
    assert not level5_mechanism_gate(SimpleNamespace(**metrics))


def test_baseline_must_match_the_exact_evaluation_interval() -> None:
    validate_evaluation_baseline(
        {
            "exact_seed_interval": True,
            "seed_base": 30_000,
            "seed_stop_exclusive": 30_007,
            "episodes": 7,
        },
        label="teacher",
        seed_base=30_000,
        episodes=7,
    )
    with pytest.raises(SystemExit, match="exact learned-evaluation seed interval"):
        validate_evaluation_baseline(
            {
                "exact_seed_interval": True,
                "seed_base": 30_000,
                "seed_stop_exclusive": 30_008,
                "episodes": 7,
            },
            label="teacher",
            seed_base=30_000,
            episodes=7,
        )
