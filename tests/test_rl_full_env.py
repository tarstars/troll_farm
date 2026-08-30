from __future__ import annotations

import copy
import ctypes
import json
import os
from pathlib import Path

import numpy as np
import pytest

from cgauto.rl_full_env import (
    ACTION_SIZE,
    DEFAULT_LIBRARY,
    OPPONENTS,
    PLAN_SIZE,
    PHASE_PLAN,
    PHASE_TROLL,
    FullVecEnv,
    RandomFrozenOpponent,
    random_legal_actions,
    replay_and_verify,
    verify_terminal_parity,
    verify_transition_parity,
)


TEST_LIBRARY = Path(os.environ.get("TF_FULL_TEST_LIBRARY", DEFAULT_LIBRARY))
pytestmark = pytest.mark.skipif(
    not TEST_LIBRARY.exists(), reason="release Rust full-environment library missing"
)


def _env(
    num_envs: int,
    seed: int,
    weights: dict[str, float] | None = None,
    *,
    frozen: RandomFrozenOpponent | None = None,
) -> FullVecEnv:
    return FullVecEnv(
        num_envs,
        seed,
        opponent_weights=weights,
        frozen_opponent=frozen,
        library=TEST_LIBRARY,
    )


def _append_empty_turn(record: dict) -> dict:
    """Append a mechanically valid transition after a supplied terminal state."""

    from cgauto.rl_full_env import canonical_state_hash
    from sim.engine import step
    from sim.state import GameState, SimPlant, SimUnit

    amended = copy.deepcopy(record)
    rows = amended["map"]["rows"]
    walkable: set[tuple[int, int]] = set()
    iron: set[tuple[int, int]] = set()
    water: set[tuple[int, int]] = set()
    shacks: list[tuple[int, int] | None] = [None, None]
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell == ".":
                walkable.add((x, y))
            elif cell == "+":
                iron.add((x, y))
            elif cell == "~":
                water.add((x, y))
            elif cell in ("0", "1"):
                shacks[int(cell)] = (x, y)
    state = amended["turns"][-1]["state"]
    game = GameState(
        len(rows[0]),
        len(rows),
        walkable,
        shacks,
        [list(values) for values in state["inventories"]],
        [
            SimUnit(
                unit["id"], unit["player"], unit["x"], unit["y"], unit["ms"],
                unit["cc"], unit["hp"], unit["chop"], list(unit["carry"])
            )
            for unit in state["units"]
        ],
        [
            SimPlant(
                plant["type"], plant["x"], plant["y"], plant["size"],
                plant["health"], plant["fruits"], plant["cooldown"]
            )
            for plant in state["plants"]
        ],
        list(state["scores"]),
        state["turn"],
        state["next_id"],
        iron,
        water,
    )
    turn = game.turn
    step(game, [], [])
    next_state = {
        "turn": game.turn,
        "next_id": game.next_id,
        "inventories": game.inventories,
        "scores": game.scores,
        "units": [
            {
                "id": unit.id, "player": unit.player, "x": unit.x, "y": unit.y,
                "ms": unit.ms, "cc": unit.cc, "hp": unit.hp, "chop": unit.chop,
                "carry": unit.carry,
            }
            for unit in sorted(game.units, key=lambda item: item.id)
        ],
        "plants": [
            {
                "type": plant.type, "x": plant.x, "y": plant.y, "size": plant.size,
                "health": plant.health, "fruits": plant.fruits, "cooldown": plant.cooldown,
            }
            for plant in sorted(game.plants, key=lambda item: (item.x, item.y, item.type))
        ],
    }
    amended["turns"].append(
        {
            "turn": turn,
            "commands0": [],
            "commands1": [],
            "state": next_state,
            "state_hash": canonical_state_hash(game),
        }
    )
    return amended


def test_shapes_phase_masks_and_atomic_invalid_action() -> None:
    with _env(4, 100, {"script_boss": 1.0}) as env:
        assert env.obs.shape == (4, 104, 11, 22)
        assert env.masks.shape == (4, 13, 11, 22)
        assert env.plan_masks.shape == (4, PLAN_SIZE)
        assert np.all(env.phase == PHASE_PLAN)
        assert np.all(env.plan_masks[:, 0] == 1)
        assert not env.masks.any()

        before = env.obs.copy()
        with pytest.raises(RuntimeError, match="-4"):
            env.step(np.full(4, PLAN_SIZE, dtype=np.int32))
        np.testing.assert_array_equal(env.obs, before)
        assert np.all(env.phase == PHASE_PLAN)

        rewards, info = env.step(np.zeros(4, dtype=np.int32))
        np.testing.assert_array_equal(rewards, np.zeros(4, dtype=np.float32))
        assert not info.turn_completed.any()
        assert np.all(env.phase == PHASE_TROLL)
        flat = env.masks.reshape(4, ACTION_SIZE)
        assert flat.any(axis=1).all()


def test_identical_batches_are_deterministic() -> None:
    rng = np.random.default_rng(51)
    weights = {name: 1.0 for name in OPPONENTS if name != "python_frozen"}
    with _env(4, 777, weights) as left, _env(4, 777, weights) as right:
        for _ in range(24):
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left.plan_masks, right.plan_masks)
            actions = random_legal_actions(left, rng)
            left_rewards, left_info = left.step(actions)
            right_rewards, right_info = right.step(actions)
            np.testing.assert_array_equal(left_rewards, right_rewards)
            np.testing.assert_array_equal(left_info.turn_completed, right_info.turn_completed)
            np.testing.assert_array_equal(left_info.dones, right_info.dones)


def test_python_frozen_opponent_returns_one_reward_row_per_learner_call() -> None:
    rng = np.random.default_rng(61)
    frozen = RandomFrozenOpponent(62)
    with _env(6, 800, {"python_frozen": 1.0}, frozen=frozen) as env:
        rewards, info = env.step(random_legal_actions(env, rng))
        np.testing.assert_array_equal(rewards, np.zeros(6, dtype=np.float32))
        assert not info.turn_completed.any()
        rewards, info = env.step(random_legal_actions(env, rng))
        assert rewards.shape == (6,)
        assert np.all(info.turn_completed == 1)


def test_ten_thousand_random_masked_learner_actions_are_accepted() -> None:
    rng = np.random.default_rng(65)
    frozen = RandomFrozenOpponent(66)
    accepted = 0
    with _env(20, 850, {"python_frozen": 1.0}, frozen=frozen) as env:
        while accepted < 10_000:
            actions = random_legal_actions(env, rng)
            plan_slots = env.phase == PHASE_PLAN
            troll_slots = env.phase == PHASE_TROLL
            assert np.all(
                env.plan_masks[np.flatnonzero(plan_slots), actions[plan_slots]] == 1
            )
            flat = env.masks.reshape(20, ACTION_SIZE)
            assert np.all(flat[np.flatnonzero(troll_slots), actions[troll_slots]] == 1)
            env.step(actions)
            accepted += int(plan_slots.sum() + troll_slots.sum())
    assert accepted >= 10_000


def test_both_seats_all_verbs_codec_mask_and_strict_context() -> None:
    lib = ctypes.CDLL(str(TEST_LIBRARY))
    void = ctypes.c_void_p
    lib.tf_full_obs_from_state.argtypes = [
        void, ctypes.c_size_t, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_int32, ctypes.c_uint8, void, void, void,
    ]
    lib.tf_full_obs_from_state.restype = ctypes.c_int32
    lib.tf_full_encode_command.argtypes = [
        void, ctypes.c_size_t, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
    ]
    lib.tf_full_encode_command.restype = ctypes.c_int32
    lib.tf_full_decode_action.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_int32, void, ctypes.c_size_t,
    ]
    lib.tf_full_decode_action.restype = ctypes.c_int32

    rows = ["0.+.1", ".....", "....."]
    commands = [
        "MOVE {id} 2 1", "HARVEST {id}", "CHOP {id}", "DROP {id}",
        "MINE {id}",
        *[f"PLANT {{id}} {kind}" for kind in ("PLUM", "LEMON", "APPLE", "BANANA")],
        *[f"PICK {{id}} {kind}" for kind in ("PLUM", "LEMON", "APPLE", "BANANA")],
    ]
    for seat in (0, 1):
        active_id = seat
        active_x = 1 if seat == 0 else 3
        active_y = 0
        for plane, template in enumerate(commands):
            units = [
                {
                    "id": 0, "player": 0, "x": 1, "y": 0, "ms": 1,
                    "cc": 5, "hp": 1, "chop": 1, "carry": [0] * 6,
                },
                {
                    "id": 1, "player": 1, "x": 3, "y": 0, "ms": 1,
                    "cc": 5, "hp": 1, "chop": 1, "carry": [0] * 6,
                },
            ]
            plants: list[dict] = []
            if plane in (1, 2):
                plants.append(
                    {
                        "type": "PLUM", "x": active_x, "y": active_y,
                        "size": 1, "health": 6, "fruits": 1, "cooldown": 8,
                    }
                )
            if plane == 3:
                units[seat]["carry"][5] = 1
            if 5 <= plane <= 8:
                units[seat]["carry"][plane - 5] = 1
            state = {
                "w": 5,
                "h": 3,
                "rows": rows,
                "turn": 17,
                "inv": [[5, 5, 5, 5, 5, 0], [5, 5, 5, 5, 5, 0]],
                "units": units,
                "plants": plants,
                "staged_actions": [],
            }
            payload = json.dumps(state, separators=(",", ":")).encode()
            obs = np.empty(104 * 11 * 22, dtype=np.uint8)
            mask = np.empty(ACTION_SIZE, dtype=np.uint8)
            plan_mask = np.empty(PLAN_SIZE, dtype=np.uint8)
            status = lib.tf_full_obs_from_state(
                ctypes.c_char_p(payload), len(payload), seat, active_id, PHASE_TROLL,
                0, 0, ctypes.c_void_p(obs.ctypes.data), ctypes.c_void_p(mask.ctypes.data),
                ctypes.c_void_p(plan_mask.ctypes.data),
            )
            assert status == 0
            if plane == 0:
                relative = (2, 1)
            elif seat == 0:
                relative = (active_x, active_y)
            else:
                relative = (4 - active_x, 2 - active_y)
            expected = plane * 242 + relative[1] * 22 + relative[0]
            assert mask[expected] == 1

            command = template.format(id=active_id).encode()
            encoded = lib.tf_full_encode_command(
                ctypes.c_char_p(command), len(command), active_id, seat, 5, 3,
                active_x, active_y,
            )
            assert encoded == expected
            output = ctypes.create_string_buffer(96)
            written = lib.tf_full_decode_action(
                expected, active_id, seat, 5, 3, output, len(output)
            )
            assert written == len(command)
            assert output.value == command

    invalid = {
        "w": 5, "h": 3, "rows": rows, "turn": 1,
        "inv": [[0] * 6, [0] * 6],
        "units": [
            {"id": 0, "player": 0, "x": 1, "y": 0, "ms": 1, "cc": 1,
             "hp": 1, "chop": 1, "carry": [0] * 6},
            {"id": 1, "player": 1, "x": 3, "y": 0, "ms": 1, "cc": 1,
             "hp": 1, "chop": 1, "carry": [0] * 6},
        ],
        "plants": [], "staged_actions": [],
    }
    payload = json.dumps(invalid).encode()
    obs = np.empty(104 * 11 * 22, dtype=np.uint8)
    assert lib.tf_full_obs_from_state(
        ctypes.c_char_p(payload), len(payload), 0, 0, PHASE_PLAN, 0, 0,
        ctypes.c_void_p(obs.ctypes.data), None, None,
    ) == -2


def test_completed_replay_matches_python_simulator_each_turn() -> None:
    rng = np.random.default_rng(71)
    with _env(1, 900, {"script_boss": 1.0}) as env:
        for _ in range(2_000):
            _, info = env.step(random_legal_actions(env, rng))
            if info.dones[0]:
                replay = env.take_replay(0)
                assert replay is not None
                assert [unit["chop"] for unit in replay["initial_state"]["units"]] == [1, 1]
                assert replay_and_verify(replay) == int(info.state_hash[0])

                truncated = copy.deepcopy(replay)
                truncated["turns"] = truncated["turns"][:-1]
                verify_transition_parity(truncated)
                with pytest.raises(AssertionError, match="nonterminal|no turns"):
                    verify_terminal_parity(truncated)

                appended = _append_empty_turn(replay)
                verify_transition_parity(appended)
                with pytest.raises(AssertionError, match="after an earlier terminal"):
                    verify_terminal_parity(appended)

                wrong_counter = copy.deepcopy(replay)
                wrong_counter["terminal_stall_counter"] += 1
                with pytest.raises(AssertionError, match="counter mismatch"):
                    verify_terminal_parity(wrong_counter)

                wrong_reason = copy.deepcopy(replay)
                wrong_reason["terminal_reason"] = "mutated"
                with pytest.raises(AssertionError, match="reason mismatch"):
                    verify_terminal_parity(wrong_reason)

                wrong_initial = copy.deepcopy(replay)
                wrong_initial["initial_state"]["units"][0]["chop"] = 0
                with pytest.raises(AssertionError, match="chop-1 starters"):
                    verify_transition_parity(wrong_initial)
                break
        else:
            pytest.fail("full-game episode did not terminate")


def test_two_hundred_no_train_self_play_replays_match_python_simulator() -> None:
    class NoTrainFrozen(RandomFrozenOpponent):
        def __call__(self, *args: np.ndarray) -> np.ndarray:
            actions = super().__call__(*args)
            phases = args[3]
            actions[phases == PHASE_PLAN] = 0
            return actions

    rng = np.random.default_rng(81)
    completed = 0
    with _env(
        20,
        1_100,
        {"python_frozen": 1.0},
        frozen=NoTrainFrozen(82),
    ) as env:
        while completed < 200:
            actions = random_legal_actions(env, rng)
            actions[env.phase == PHASE_PLAN] = 0
            _, info = env.step(actions)
            for slot in np.flatnonzero(info.dones):
                assert info.illegal_commands[slot] == 0
                replay = env.take_replay(int(slot))
                assert replay is not None
                assert replay_and_verify(replay) == int(info.state_hash[slot])
                completed += 1
    assert completed == 200
