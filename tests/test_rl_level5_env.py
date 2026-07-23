from dataclasses import fields

import numpy as np

from cgauto.rl_level1_env import ACTION_SIZE, OBS_SIZE
from cgauto.rl_level4_env import Level4VecEnv
from cgauto.rl_level5_env import (
    Level5CropFirstRepeatedPressure180VecEnv,
    Level5CropFirstRepeatedPressureReacquire180VecEnv,
    Level5CropFirstSustainedTrio180VecEnv,
    Level5FundedPairVecEnv,
    Level5FundedTrioVecEnv,
    Level5ForagerVecEnv,
    Level5PlanterVecEnv,
    Level5RecoveryVecEnv,
    Level5ReaperVecEnv,
    Level5StepInfo,
    Level5SustainedTrio180VecEnv,
    Level5SustainedTrioVecEnv,
    Level5VecEnv,
    run_policy,
)


def test_level5_shapes_recipe_and_terminal_telemetry() -> None:
    with Level5VecEnv(8, 0) as env:
        assert env.obs.size == 8 * OBS_SIZE
        assert env.masks.size == 8 * ACTION_SIZE
        terminal_seen = False
        for _ in range(500):
            actions = env.teacher_actions()
            _, _, _, info = env.step(actions)
            if np.any(info.dones):
                terminal_seen = True
                done = info.dones.astype(bool)
                assert np.all(info.opponent_workers[done] >= 1)
                assert np.all((0 <= info.recipe_ids[done]) & (info.recipe_ids[done] < 8))
                break
        assert terminal_seen


def test_level5_batches_are_byte_deterministic() -> None:
    with Level5VecEnv(6, 77) as left, Level5VecEnv(6, 77) as right:
        for _ in range(120):
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            left_obs, left_masks, left_rewards, left_info = left.step(left_actions)
            right_obs, right_masks, right_rewards, right_info = right.step(right_actions)
            np.testing.assert_array_equal(left_obs, right_obs)
            np.testing.assert_array_equal(left_masks, right_masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )


def test_active_opponent_diverges_from_waiting_control() -> None:
    with Level4VecEnv(4, 20) as waiting, Level5VecEnv(4, 20) as active:
        for _ in range(8):
            waiting.step(waiting.teacher_actions())
            active.step(active.teacher_actions())
        opponent_position_channel = 9
        assert np.any(
            waiting.obs[:, opponent_position_channel]
            != active.obs[:, opponent_position_channel]
        )


def test_level5_control_summary_records_material_opponent() -> None:
    result = run_policy("teacher", episodes=20, num_envs=10, seed_base=0)
    assert result["curriculum_level"] == 5
    assert result["exact_seed_interval"] is True
    assert result["episodes"] == 20
    assert result["material_opponent_episodes"] > 0
    assert len(result["episodes_detail"]) == 20


def test_natural_forager_is_deterministic_and_never_trains() -> None:
    with Level5ForagerVecEnv(8, 500) as left, Level5ForagerVecEnv(8, 500) as right:
        terminal_workers = []
        for _ in range(500):
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            _, _, left_rewards, left_info = left.step(left_actions)
            _, _, right_rewards, right_info = right.step(right_actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            np.testing.assert_array_equal(
                left_info.opponent_workers, right_info.opponent_workers
            )
            terminal_workers.extend(left_info.opponent_workers[left_info.dones.astype(bool)])
            if terminal_workers:
                break
        assert terminal_workers
        assert set(terminal_workers) == {1}


def test_natural_forager_summary_selects_explicit_policy() -> None:
    result = run_policy(
        "teacher",
        episodes=20,
        num_envs=10,
        seed_base=500,
        opponent_mode="natural-forager",
    )
    assert result["opponent_policy"] == "deterministic-no-growth-natural-forager"
    assert result["opponent_multiworker_rate"] == 0.0


def test_dynamic_crop_recovery_is_deterministic_and_teacher_legal() -> None:
    with Level5RecoveryVecEnv(8, 1_000) as left, Level5RecoveryVecEnv(
        8, 1_000
    ) as right:
        terminal_seen = False
        for _ in range(500):
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            flat_masks = left.masks.reshape(8, ACTION_SIZE)
            assert np.all(flat_masks[np.arange(8), left_actions] == 1)
            _, _, left_rewards, left_info = left.step(left_actions)
            _, _, right_rewards, right_info = right.step(right_actions)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            terminal_seen |= bool(np.any(left_info.dones))
            if terminal_seen:
                break
        assert terminal_seen


def test_dynamic_crop_recovery_summary_selects_explicit_policy() -> None:
    result = run_policy(
        "teacher",
        episodes=20,
        num_envs=10,
        seed_base=1_000,
        opponent_mode="complete-recovery",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-rhea-faststate-baseline-dynamic-crop-recovery"
    )
    assert result["illegal_selected_actions"] == 0


def test_natural_planter_is_deterministic_renewable_and_never_trains() -> None:
    with Level5PlanterVecEnv(8, 0) as left, Level5PlanterVecEnv(8, 0) as right:
        terminal_crops = []
        terminal_harvests = []
        for _ in range(500):
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            _, _, left_rewards, left_info = left.step(left_actions)
            _, _, right_rewards, right_info = right.step(right_actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            assert np.all(left_info.opponent_workers[done] == 1)
            terminal_crops.extend(left_info.opponent_created_crops[done])
            terminal_harvests.extend(left_info.opponent_renewable_harvests[done])
            if terminal_crops and terminal_harvests and max(terminal_harvests) > 0:
                break
        assert terminal_crops
        assert max(terminal_crops) > 0
        assert max(terminal_harvests) > 0


def test_natural_planter_summary_records_explicit_activation() -> None:
    result = run_policy(
        "teacher",
        episodes=20,
        num_envs=10,
        seed_base=0,
        opponent_mode="natural-planter",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-one-worker-natural-regenerative-planter"
    )
    assert result["opponent_multiworker_rate"] == 0.0
    assert result["opponent_crop_creation_rate"] > 0.0
    assert result["opponent_renewable_harvest_rate"] > 0.0


def test_one_shot_reaper_is_deterministic_and_destroys_at_most_once() -> None:
    with Level5ReaperVecEnv(8, 0) as left, Level5ReaperVecEnv(8, 0) as right:
        terminal_destructions = []
        for _ in range(500):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            assert np.all(left_info.opponent_workers[done] == 1)
            assert np.all(left_info.opponent_crop_destructions[done] <= 1)
            terminal_destructions.extend(left_info.opponent_crop_destructions[done])
            if terminal_destructions and max(terminal_destructions) > 0:
                break
        assert terminal_destructions
        assert max(terminal_destructions) == 1


def test_one_shot_reaper_summary_records_explicit_activation() -> None:
    result = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="one-shot-reaper",
    )
    assert result["opponent_policy"] == "deterministic-one-worker-one-shot-crop-reaper"
    assert result["opponent_multiworker_rate"] == 0.0
    assert result["opponent_crop_destruction_rate"] > 0.0
    assert result["mean_opponent_crop_destructions"] <= 1.0


def test_funded_pair_is_deterministic_funded_and_capped_at_two() -> None:
    with Level5FundedPairVecEnv(8, 0) as left, Level5FundedPairVecEnv(
        8, 0
    ) as right:
        trained = []
        productive = []
        for _ in range(500):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            assert np.all(left_info.opponent_workers[done] <= 2)
            trained_done = done & (left_info.opponent_training_turns > 0)
            assert np.all(left_info.opponent_funding_deposits[trained_done] > 0)
            trained.extend(left_info.opponent_training_turns[done])
            productive.extend(left_info.opponent_second_worker_productive_actions[done])
            if trained and productive and max(trained) > 0 and max(productive) > 0:
                break
        assert trained and max(trained) > 0
        assert productive and max(productive) > 0


def test_funded_pair_summary_records_training_and_productivity() -> None:
    result = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="funded-pair",
    )
    assert result["opponent_policy"] == "deterministic-naturally-funded-two-worker-pair"
    assert result["opponent_training_rate"] > 0.0
    assert result["trained_with_funding_receipt_rate"] == 1.0
    assert result["opponent_second_worker_productive_rate"] > 0.0
    assert result["max_opponent_workers"] == 2


def test_funded_trio_is_deterministic_and_requires_two_funding_epochs() -> None:
    with Level5FundedTrioVecEnv(8, 0) as left, Level5FundedTrioVecEnv(
        8, 0
    ) as right:
        third_training = []
        third_productive = []
        for _ in range(500):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            assert np.all(left_info.opponent_workers[done] <= 3)
            third_done = done & (left_info.opponent_third_worker_training_turns > 0)
            assert np.all(left_info.opponent_workers[third_done] == 3)
            assert np.all(left_info.opponent_funded_training_events[third_done] == 2)
            third_training.extend(left_info.opponent_third_worker_training_turns[done])
            third_productive.extend(
                left_info.opponent_third_worker_productive_actions[done]
            )
            if (
                third_training
                and third_productive
                and max(third_training) > 0
                and max(third_productive) > 0
            ):
                break
        assert third_training and max(third_training) > 0
        assert third_productive and max(third_productive) > 0


def test_funded_trio_summary_records_scale_and_feeder_productivity() -> None:
    result = run_policy(
        "teacher",
        episodes=100,
        num_envs=10,
        seed_base=0,
        opponent_mode="funded-trio",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-two-epoch-funded-three-worker-economy"
    )
    assert result["opponent_third_worker_training_rate"] > 0.0
    assert result["third_trained_with_fresh_funding_receipt_rate"] == 1.0
    assert result["opponent_third_worker_productive_rate"] > 0.0
    assert result["max_opponent_workers"] == 3


def test_sustained_trio_is_deterministic_and_cannot_finish_before_turn_120() -> None:
    with Level5SustainedTrioVecEnv(8, 0) as left, Level5SustainedTrioVecEnv(
        8, 0
    ) as right:
        terminal_turns = []
        for _ in range(600):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            terminal_turns.extend(left_info.turns[done])
            if terminal_turns:
                break
        assert terminal_turns
        assert min(terminal_turns) >= 120


def test_sustained_trio_summary_records_fixed_minimum_turn() -> None:
    result = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="funded-trio-sustained",
    )
    assert result["success_rate"] == 1.0
    assert result["median_success_turn"] >= 120
    assert min(row["turns"] for row in result["episodes_detail"]) >= 120
    assert result["max_opponent_workers"] == 3


def test_sustained_trio_180_is_deterministic_and_cannot_finish_early() -> None:
    with Level5SustainedTrio180VecEnv(8, 0) as left, Level5SustainedTrio180VecEnv(
        8, 0
    ) as right:
        terminal_turns = []
        for _ in range(600):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            terminal_turns.extend(left_info.turns[done])
            if terminal_turns:
                break
        assert terminal_turns
        assert min(terminal_turns) >= 180


def test_sustained_trio_180_summary_preserves_turn_120_mode() -> None:
    result_180 = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="funded-trio-sustained-180",
    )
    result_120 = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="funded-trio-sustained",
    )
    assert result_180["success_rate"] == 1.0
    assert result_180["median_success_turn"] >= 180
    assert min(row["turns"] for row in result_180["episodes_detail"]) >= 180
    assert result_180["max_opponent_workers"] == 3
    assert result_120["median_success_turn"] >= 120
    assert result_120["median_success_turn"] < 180


def test_crop_first_trio_180_batches_are_byte_deterministic() -> None:
    with Level5CropFirstSustainedTrio180VecEnv(
        8, 0
    ) as left, Level5CropFirstSustainedTrio180VecEnv(8, 0) as right:
        terminal_turns = []
        for _ in range(600):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            terminal_turns.extend(left_info.turns[done])
            if terminal_turns:
                break
        assert terminal_turns
        assert min(terminal_turns) >= 180


def test_crop_first_trio_summary_records_supply_before_scale() -> None:
    result = run_policy(
        "teacher",
        episodes=50,
        num_envs=10,
        seed_base=0,
        opponent_mode="crop-first-funded-trio-sustained-180",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-crop-first-funded-three-worker-economy-sustained-turn-180"
    )
    assert result["success_rate"] == 1.0
    assert result["median_success_turn"] >= 180
    trained = [
        row
        for row in result["episodes_detail"]
        if row["opponent_third_worker_training_turn"] > 0
    ]
    assert trained
    assert all(row["opponent_created_crops"] > 0 for row in trained)
    assert all(row["opponent_funded_training_events"] == 2 for row in trained)
    assert result["max_opponent_workers"] == 3


def test_repeated_pressure_batches_are_deterministic_and_bounded_at_three() -> None:
    with Level5CropFirstRepeatedPressure180VecEnv(
        8, 0
    ) as left, Level5CropFirstRepeatedPressure180VecEnv(8, 0) as right:
        terminal_destructions = []
        for _ in range(600):
            actions = left.teacher_actions()
            np.testing.assert_array_equal(actions, right.teacher_actions())
            _, _, left_rewards, left_info = left.step(actions)
            _, _, right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(left_info, field.name), getattr(right_info, field.name)
                )
            done = left_info.dones.astype(bool)
            assert np.all(left_info.opponent_crop_destructions[done] <= 3)
            terminal_destructions.extend(
                left_info.opponent_crop_destructions[done]
            )
            if terminal_destructions:
                break
        assert terminal_destructions
        assert max(terminal_destructions) == 3


def test_repeated_pressure_summary_records_recurrent_activation() -> None:
    result = run_policy(
        "teacher",
        episodes=100,
        num_envs=10,
        seed_base=0,
        opponent_mode="crop-first-funded-trio-repeated-pressure-180",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-crop-first-funded-three-worker-economy-"
        "repeated-pressure-3-sustained-turn-180"
    )
    assert result["median_success_turn"] >= 180
    assert result["opponent_crop_destruction_at_least_two_rate"] > 0.0
    assert result["opponent_crop_destruction_at_least_three_rate"] > 0.0
    assert result["max_opponent_crop_destructions"] == 3
    trained = [
        row
        for row in result["episodes_detail"]
        if row["opponent_third_worker_training_turn"] > 0
    ]
    assert trained
    assert all(row["opponent_created_crops"] > 0 for row in trained)
    assert all(row["opponent_funded_training_events"] == 2 for row in trained)
    assert result["max_opponent_workers"] == 3


def test_reacquisition_mode_preserves_external_action_task_parity() -> None:
    with Level5CropFirstRepeatedPressure180VecEnv(
        8, 0
    ) as d10, Level5CropFirstRepeatedPressureReacquire180VecEnv(8, 0) as d11:
        divergent_labels = False
        for _ in range(600):
            np.testing.assert_array_equal(d10.obs, d11.obs)
            np.testing.assert_array_equal(d10.masks, d11.masks)
            actions = d10.teacher_actions()
            divergent_labels |= bool(
                np.any(actions != d11.teacher_actions())
            )
            d10_obs, d10_masks, d10_rewards, d10_info = d10.step(actions)
            d11_obs, d11_masks, d11_rewards, d11_info = d11.step(actions)
            np.testing.assert_array_equal(d10_obs, d11_obs)
            np.testing.assert_array_equal(d10_masks, d11_masks)
            np.testing.assert_array_equal(d10_rewards, d11_rewards)
            for field in fields(Level5StepInfo):
                np.testing.assert_array_equal(
                    getattr(d10_info, field.name), getattr(d11_info, field.name)
                )
            if divergent_labels and np.any(d10_info.dones):
                break
        assert divergent_labels


def test_reacquisition_expert_summary_is_feasible_active_and_bounded() -> None:
    result = run_policy(
        "teacher",
        episodes=100,
        num_envs=10,
        seed_base=0,
        opponent_mode="crop-first-funded-trio-repeated-pressure-reacquire-180",
    )
    assert (
        result["opponent_policy"]
        == "deterministic-crop-first-funded-three-worker-economy-"
        "repeated-pressure-3-seed-reacquisition-expert-turn-180"
    )
    assert result["success_rate"] >= 0.95
    assert result["illegal_selected_actions"] == 0
    assert result["median_success_turn"] >= 180
    assert result["opponent_crop_destruction_at_least_two_rate"] > 0.0
    assert result["opponent_crop_destruction_at_least_three_rate"] > 0.0
    assert result["max_opponent_crop_destructions"] == 3
    assert result["max_opponent_workers"] == 3
