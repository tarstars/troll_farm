#!/usr/bin/env python3
"""NumPy/ctypes wrapper for the real-map full-game Rust environment."""

from __future__ import annotations

import argparse
import ctypes
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
DEFAULT_MAPS = ROOT / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl"

OBS_CHANNELS = 104
OBS_HEIGHT = 11
OBS_WIDTH = 22
OBS_SIZE = OBS_CHANNELS * OBS_HEIGHT * OBS_WIDTH
ACTION_PLANES = 13
ACTION_SIZE = ACTION_PLANES * OBS_HEIGHT * OBS_WIDTH
PLAN_SIZE = 144
MAX_RECORDED_TRAINS = 4

PHASE_PLAN = 0
PHASE_TROLL = 1
PHASE_EXTERNAL_WAIT = 2

OPPONENTS = (
    "secure_orchard",
    "norxondor_native",
    "legend_field_proxy_v2",
    "gold_elite_adaptive",
    "script_boss",
    "mybot_boss4",
    "python_frozen",
)

FrozenOpponent = Callable[
    [np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    np.ndarray,
]


@dataclass(frozen=True)
class TransitionBatch:
    """Learner mini-steps credited with a completed turn's scalar reward."""

    obs: np.ndarray
    masks: np.ndarray
    plan_masks: np.ndarray
    phases: np.ndarray
    seat_view: np.ndarray
    active_troll: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    slots: np.ndarray


@dataclass(frozen=True)
class FullStepInfo:
    """Copied full-turn and terminal metadata from one vector step."""

    turn_completed: np.ndarray
    reward_credit_count: np.ndarray
    dones: np.ndarray
    wins: np.ndarray
    episode_turns: np.ndarray
    episode_returns: np.ndarray
    episode_seeds: np.ndarray
    map_indices: np.ndarray
    opponent_ids: np.ndarray
    score_own: np.ndarray
    score_opp: np.ndarray
    trained_specs: np.ndarray
    trained_turns: np.ndarray
    trained_count: np.ndarray
    trained_overflow: np.ndarray
    illegal_commands: np.ndarray
    action_hash: np.ndarray
    state_hash: np.ndarray


@dataclass
class _PendingTransition:
    obs: np.ndarray
    masks: np.ndarray
    plan_masks: np.ndarray
    phase: int
    seat_view: int
    active_troll: int
    action: int


class FullVecEnv:
    """Batched auto-reset full-game environment with learner mini-step credit."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        maps_path: Path | str = DEFAULT_MAPS,
        opponent_weights: Mapping[str, float] | None = None,
        *,
        wood_shaping: float = 0.5,
        end_wood: float = 3.5,
        frozen_opponent: FrozenOpponent | None = None,
        library: Path | str = DEFAULT_LIBRARY,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if not 0 <= seed_base <= np.iinfo(np.uint64).max:
            raise ValueError("seed_base must fit uint64")
        self.num_envs = int(num_envs)
        self.seed_base = int(seed_base)
        self.maps_path = Path(maps_path).resolve()
        if not self.maps_path.is_file():
            raise FileNotFoundError(self.maps_path)
        if opponent_weights is None:
            opponent_weights = {name: 1.0 for name in OPPONENTS[:-1]}
        unknown = sorted(set(opponent_weights) - set(OPPONENTS))
        if unknown:
            raise ValueError(f"unknown opponent weights: {unknown}")
        weights = np.array(
            [float(opponent_weights.get(name, 0.0)) for name in OPPONENTS],
            dtype=np.float32,
        )
        if not np.all(np.isfinite(weights)) or np.any(weights < 0) or not np.any(weights > 0):
            raise ValueError("opponent weights must be finite, non-negative, and nonempty")
        if weights[-1] > 0 and frozen_opponent is None:
            raise ValueError("python_frozen has positive weight but no frozen_opponent callback")
        if not np.isfinite(wood_shaping) or wood_shaping < 0:
            raise ValueError("wood_shaping must be finite and non-negative")
        if not np.isfinite(end_wood) or end_wood < 0:
            raise ValueError("end_wood must be finite and non-negative")

        self._weights = weights
        self._frozen_opponent = frozen_opponent
        self.library_path = Path(library).resolve()
        if not self.library_path.is_file():
            raise FileNotFoundError(
                f"missing {self.library_path}; run "
                "cargo build --manifest-path rust/Cargo.toml --release --lib"
            )
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        if self._lib.tf_full_obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python observation-size mismatch")
        if self._lib.tf_full_action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python action-size mismatch")
        if self._lib.tf_full_plan_size() != PLAN_SIZE:
            raise RuntimeError("Rust/Python plan-size mismatch")
        self._handle = self._lib.tf_full_create(
            self.num_envs,
            ctypes.c_uint64(self.seed_base),
            str(self.maps_path).encode(),
            self._ptr(self._weights),
            ctypes.c_float(wood_shaping),
            ctypes.c_float(end_wood),
        )
        if not self._handle:
            raise RuntimeError("Rust full environment allocation failed")

        self.obs = np.empty(
            (self.num_envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.masks = np.empty(
            (self.num_envs, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.plan_masks = np.empty((self.num_envs, PLAN_SIZE), dtype=np.uint8)
        self.phase = np.empty(self.num_envs, dtype=np.int32)
        self.seat_view = np.empty(self.num_envs, dtype=np.int32)
        self.active_troll = np.empty(self.num_envs, dtype=np.int32)

        self.rewards = np.empty(self.num_envs, dtype=np.float32)
        self._turn_completed = np.empty(self.num_envs, dtype=np.uint8)
        self._reward_credit_count = np.empty(self.num_envs, dtype=np.uint8)
        self._dones = np.empty(self.num_envs, dtype=np.uint8)
        self._wins = np.empty(self.num_envs, dtype=np.uint8)
        self._episode_turns = np.empty(self.num_envs, dtype=np.uint16)
        self._episode_returns = np.empty(self.num_envs, dtype=np.float32)
        self._episode_seeds = np.empty(self.num_envs, dtype=np.uint64)
        self._map_indices = np.empty(self.num_envs, dtype=np.uint32)
        self._opponent_ids = np.empty(self.num_envs, dtype=np.uint8)
        self._score_own = np.empty(self.num_envs, dtype=np.int32)
        self._score_opp = np.empty(self.num_envs, dtype=np.int32)
        self._trained_specs = np.empty(
            (self.num_envs, MAX_RECORDED_TRAINS, 4), dtype=np.int8
        )
        self._trained_turns = np.empty(
            (self.num_envs, MAX_RECORDED_TRAINS), dtype=np.uint16
        )
        self._trained_count = np.empty(self.num_envs, dtype=np.uint8)
        self._trained_overflow = np.empty(self.num_envs, dtype=np.uint8)
        self._illegal_commands = np.empty(self.num_envs, dtype=np.uint16)
        self._action_hash = np.empty(self.num_envs, dtype=np.uint64)
        self._state_hash = np.empty(self.num_envs, dtype=np.uint64)

        self._opp_obs = np.empty_like(self.obs)
        self._opp_masks = np.empty_like(self.masks)
        self._opp_plan_masks = np.empty_like(self.plan_masks)
        self._opp_phase = np.empty_like(self.phase)
        self._opp_seat = np.empty_like(self.seat_view)
        self._opp_active = np.empty_like(self.active_troll)
        self._opp_needs = np.empty(self.num_envs, dtype=np.uint8)
        self._pending: list[list[_PendingTransition]] = [
            [] for _ in range(self.num_envs)
        ]
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._lib.tf_full_obs_size.restype = ctypes.c_size_t
        self._lib.tf_full_action_size.restype = ctypes.c_size_t
        self._lib.tf_full_plan_size.restype = ctypes.c_size_t
        self._lib.tf_full_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_char_p,
            void,
            ctypes.c_float,
            ctypes.c_float,
        ]
        self._lib.tf_full_create.restype = void
        self._lib.tf_full_destroy.argtypes = [void]
        self._lib.tf_full_destroy.restype = None
        self._lib.tf_full_observe.argtypes = [void] * 7
        self._lib.tf_full_observe.restype = ctypes.c_int32
        self._lib.tf_full_step.argtypes = [void] * 27
        self._lib.tf_full_step.restype = ctypes.c_int32
        self._lib.tf_full_opponent_step.argtypes = [void] * 27
        self._lib.tf_full_opponent_step.restype = ctypes.c_int32
        self._lib.tf_full_opponent_observe.argtypes = [void] * 8
        self._lib.tf_full_opponent_observe.restype = ctypes.c_int32
        self._lib.tf_full_take_replay.argtypes = [
            void,
            ctypes.c_size_t,
            void,
            ctypes.c_size_t,
        ]
        self._lib.tf_full_take_replay.restype = ctypes.c_int64

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def observe(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        status = self._lib.tf_full_observe(
            self._handle,
            self._ptr(self.obs),
            self._ptr(self.masks),
            self._ptr(self.plan_masks),
            self._ptr(self.phase),
            self._ptr(self.seat_view),
            self._ptr(self.active_troll),
        )
        if status != self.num_envs:
            raise RuntimeError(f"tf_full_observe failed with {status}")
        return (
            self.obs,
            self.masks,
            self.plan_masks,
            self.phase,
            self.seat_view,
            self.active_troll,
        )

    def _step_args(self, actions: np.ndarray) -> tuple[ctypes.c_void_p, ...]:
        return (
            self._handle,
            self._ptr(actions),
            self._ptr(self.obs),
            self._ptr(self.masks),
            self._ptr(self.plan_masks),
            self._ptr(self.phase),
            self._ptr(self.seat_view),
            self._ptr(self.active_troll),
            self._ptr(self.rewards),
            self._ptr(self._turn_completed),
            self._ptr(self._reward_credit_count),
            self._ptr(self._dones),
            self._ptr(self._wins),
            self._ptr(self._episode_turns),
            self._ptr(self._episode_returns),
            self._ptr(self._episode_seeds),
            self._ptr(self._map_indices),
            self._ptr(self._opponent_ids),
            self._ptr(self._score_own),
            self._ptr(self._score_opp),
            self._ptr(self._trained_specs),
            self._ptr(self._trained_turns),
            self._ptr(self._trained_count),
            self._ptr(self._trained_overflow),
            self._ptr(self._illegal_commands),
            self._ptr(self._action_hash),
            self._ptr(self._state_hash),
        )

    def _capture_pending(self, actions: np.ndarray) -> list[_PendingTransition | None]:
        captured: list[_PendingTransition | None] = []
        for slot in range(self.num_envs):
            if self.phase[slot] not in (PHASE_PLAN, PHASE_TROLL):
                captured.append(None)
                continue
            captured.append(
                _PendingTransition(
                    obs=self.obs[slot].copy(),
                    masks=self.masks[slot].copy(),
                    plan_masks=self.plan_masks[slot].copy(),
                    phase=int(self.phase[slot]),
                    seat_view=int(self.seat_view[slot]),
                    active_troll=int(self.active_troll[slot]),
                    action=int(actions[slot]),
                )
            )
        return captured

    def _commit_pending(self, captured: list[_PendingTransition | None]) -> None:
        for slot, transition in enumerate(captured):
            if transition is not None:
                self._pending[slot].append(transition)

    def _snapshot_outputs(self) -> dict[str, np.ndarray]:
        return {
            name: getattr(self, name).copy()
            for name in (
                "rewards",
                "_turn_completed",
                "_reward_credit_count",
                "_dones",
                "_wins",
                "_episode_turns",
                "_episode_returns",
                "_episode_seeds",
                "_map_indices",
                "_opponent_ids",
                "_score_own",
                "_score_opp",
                "_trained_specs",
                "_trained_turns",
                "_trained_count",
                "_trained_overflow",
                "_illegal_commands",
                "_action_hash",
                "_state_hash",
            )
        }

    def _merge_completed_outputs(self, merged: dict[str, np.ndarray]) -> None:
        completed = self._turn_completed.astype(bool)
        for name, values in merged.items():
            values[completed] = getattr(self, name)[completed]

    def _restore_outputs(self, merged: dict[str, np.ndarray]) -> None:
        for name, values in merged.items():
            getattr(self, name)[:] = values

    def _drive_external(self, merged: dict[str, np.ndarray]) -> None:
        if self._frozen_opponent is None:
            return
        for _ in range(64):
            status = self._lib.tf_full_opponent_observe(
                self._handle,
                self._ptr(self._opp_obs),
                self._ptr(self._opp_masks),
                self._ptr(self._opp_plan_masks),
                self._ptr(self._opp_phase),
                self._ptr(self._opp_seat),
                self._ptr(self._opp_active),
                self._ptr(self._opp_needs),
            )
            if status != self.num_envs:
                raise RuntimeError(f"tf_full_opponent_observe failed with {status}")
            needed = self._opp_needs.astype(bool)
            if not np.any(needed):
                return
            proposed = np.ascontiguousarray(
                self._frozen_opponent(
                    self._opp_obs,
                    self._opp_masks,
                    self._opp_plan_masks,
                    self._opp_phase,
                    self._opp_seat,
                    self._opp_active,
                ),
                dtype=np.int32,
            )
            if proposed.shape != (self.num_envs,):
                raise ValueError(
                    f"frozen opponent returned {proposed.shape}, expected {(self.num_envs,)}"
                )
            actions = np.full(self.num_envs, -1, dtype=np.int32)
            actions[needed] = proposed[needed]
            status = self._lib.tf_full_opponent_step(*self._step_args(actions))
            if status != self.num_envs:
                raise RuntimeError(f"tf_full_opponent_step failed with {status}")
            self._merge_completed_outputs(merged)
        raise RuntimeError("frozen opponent exceeded 64 mini-steps in one turn")

    def _transitions_for_completed(self) -> TransitionBatch:
        rows: list[tuple[int, _PendingTransition, float]] = []
        for slot in np.flatnonzero(self._turn_completed):
            pending = self._pending[int(slot)]
            expected = int(self._reward_credit_count[slot])
            if len(pending) != expected:
                raise RuntimeError(
                    f"slot {slot}: Rust credits {expected} mini-steps, Python buffered {len(pending)}"
                )
            rows.extend((int(slot), row, float(self.rewards[slot])) for row in pending)
            pending.clear()
        if not rows:
            return TransitionBatch(
                obs=np.empty((0, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8),
                masks=np.empty((0, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8),
                plan_masks=np.empty((0, PLAN_SIZE), dtype=np.uint8),
                phases=np.empty(0, dtype=np.int32),
                seat_view=np.empty(0, dtype=np.int32),
                active_troll=np.empty(0, dtype=np.int32),
                actions=np.empty(0, dtype=np.int32),
                rewards=np.empty(0, dtype=np.float32),
                slots=np.empty(0, dtype=np.int32),
            )
        return TransitionBatch(
            obs=np.stack([row.obs for _, row, _ in rows]),
            masks=np.stack([row.masks for _, row, _ in rows]),
            plan_masks=np.stack([row.plan_masks for _, row, _ in rows]),
            phases=np.array([row.phase for _, row, _ in rows], dtype=np.int32),
            seat_view=np.array([row.seat_view for _, row, _ in rows], dtype=np.int32),
            active_troll=np.array([row.active_troll for _, row, _ in rows], dtype=np.int32),
            actions=np.array([row.action for _, row, _ in rows], dtype=np.int32),
            rewards=np.array([reward for _, _, reward in rows], dtype=np.float32),
            slots=np.array([slot for slot, _, _ in rows], dtype=np.int32),
        )

    def _info(self) -> FullStepInfo:
        return FullStepInfo(
            turn_completed=self._turn_completed.copy(),
            reward_credit_count=self._reward_credit_count.copy(),
            dones=self._dones.copy(),
            wins=self._wins.copy(),
            episode_turns=self._episode_turns.copy(),
            episode_returns=self._episode_returns.copy(),
            episode_seeds=self._episode_seeds.copy(),
            map_indices=self._map_indices.copy(),
            opponent_ids=self._opponent_ids.copy(),
            score_own=self._score_own.copy(),
            score_opp=self._score_opp.copy(),
            trained_specs=self._trained_specs.copy(),
            trained_turns=self._trained_turns.copy(),
            trained_count=self._trained_count.copy(),
            trained_overflow=self._trained_overflow.copy(),
            illegal_commands=self._illegal_commands.copy(),
            action_hash=self._action_hash.copy(),
            state_hash=self._state_hash.copy(),
        )

    def step(self, actions: np.ndarray) -> tuple[TransitionBatch, FullStepInfo]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        waiting = self.phase == PHASE_EXTERNAL_WAIT
        if np.any(actions[waiting] != -1):
            raise ValueError("EXTERNAL_WAIT slots require action -1")
        captured = self._capture_pending(actions)
        status = self._lib.tf_full_step(*self._step_args(actions))
        if status != self.num_envs:
            raise RuntimeError(f"tf_full_step failed with {status}")
        self._commit_pending(captured)
        merged = self._snapshot_outputs()
        if np.any(self.phase == PHASE_EXTERNAL_WAIT):
            self._drive_external(merged)
            self._restore_outputs(merged)
        transitions = self._transitions_for_completed()
        return transitions, self._info()

    def take_replay(self, slot: int) -> dict | None:
        if not 0 <= slot < self.num_envs:
            raise IndexError(slot)
        needed = self._lib.tf_full_take_replay(self._handle, slot, None, 0)
        if needed < 0:
            raise RuntimeError(f"tf_full_take_replay size failed with {needed}")
        if needed == 0:
            return None
        output = np.empty(needed, dtype=np.uint8)
        written = self._lib.tf_full_take_replay(
            self._handle, slot, self._ptr(output), output.size
        )
        if written != needed:
            raise RuntimeError(f"tf_full_take_replay wrote {written}, expected {needed}")
        return json.loads(output.tobytes())

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_full_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "FullVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def random_legal_actions(env: FullVecEnv, rng: np.random.Generator) -> np.ndarray:
    """Uniformly sample the active head, using -1 for external-wait slots."""

    actions = np.full(env.num_envs, -1, dtype=np.int32)
    spatial = env.masks.reshape(env.num_envs, ACTION_SIZE)
    for slot in range(env.num_envs):
        if env.phase[slot] == PHASE_PLAN:
            legal = np.flatnonzero(env.plan_masks[slot])
        elif env.phase[slot] == PHASE_TROLL:
            legal = np.flatnonzero(spatial[slot])
        elif env.phase[slot] == PHASE_EXTERNAL_WAIT:
            continue
        else:
            raise RuntimeError(f"unknown phase {env.phase[slot]} in slot {slot}")
        if not len(legal):
            raise RuntimeError(f"empty legal mask in slot {slot}")
        actions[slot] = int(legal[rng.integers(len(legal))])
    return actions


class RandomFrozenOpponent:
    """Seeded legal-action sampler used only for environment tests and smoke runs."""

    def __init__(self, seed: int) -> None:
        self.rng = np.random.default_rng(seed)

    def __call__(
        self,
        _obs: np.ndarray,
        masks: np.ndarray,
        plan_masks: np.ndarray,
        phases: np.ndarray,
        _seat_view: np.ndarray,
        _active_troll: np.ndarray,
    ) -> np.ndarray:
        actions = np.full(len(phases), -1, dtype=np.int32)
        flat_masks = masks.reshape(len(phases), ACTION_SIZE)
        for slot, phase in enumerate(phases):
            if phase == PHASE_PLAN:
                legal = np.flatnonzero(plan_masks[slot])
            elif phase == PHASE_TROLL:
                legal = np.flatnonzero(flat_masks[slot])
            else:
                continue
            actions[slot] = int(legal[self.rng.integers(len(legal))])
        return actions


def canonical_state_hash(game: object) -> int:
    """Match ``rl_full.rs::state_hash`` for an in-memory Python simulator state."""

    mask64 = (1 << 64) - 1
    value = 0xCBF29CE484222325

    def mix_i64(number: int) -> None:
        nonlocal value
        for byte in int(number).to_bytes(8, "little", signed=True):
            value ^= byte
            value = (value * 0x100000001B3) & mask64

    for number in (
        game.width,
        game.height,
        game.turn,
        game.next_id,
        game.scores[0],
        game.scores[1],
    ):
        mix_i64(number)
    for x, y in game.shacks:
        mix_i64(x)
        mix_i64(y)
    for inventory in game.inventories:
        for number in inventory:
            mix_i64(number)
    for unit in sorted(game.units, key=lambda item: item.id):
        for number in (
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
            *unit.carry,
        ):
            mix_i64(number)
    for plant in sorted(game.plants, key=lambda item: (item.x, item.y, item.type)):
        for byte in plant.type.encode():
            value ^= byte
            value = (value * 0x100000001B3) & mask64
        for number in (
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ):
            mix_i64(number)
    for cells in (game.walkable, game.iron, game.water):
        ordered = sorted(cells)
        mix_i64(len(ordered))
        for x, y in ordered:
            mix_i64(x)
            mix_i64(y)
    return value


def replay_and_verify(record: Mapping[str, object]) -> int:
    """Replay a Rust episode in ``sim.engine`` and verify every recorded hash."""

    from sim.engine import recompute_scores, step
    from sim.state import GameState, SimPlant, SimUnit

    map_record = record["map"]
    rows = map_record["rows"]
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
    if shacks[0] is None or shacks[1] is None:
        raise AssertionError("replay map is missing a player shack")
    units = [
        SimUnit(player, player, *shacks[player], 1, 1, 1, 0, [0] * 6)
        for player in (0, 1)
    ]
    plants = [
        SimPlant(
            plant["type"],
            plant["x"],
            plant["y"],
            plant["size"],
            plant["health"],
            plant["fruits"],
            plant.get("cooldown", plant.get("cur_cd")),
        )
        for plant in map_record["trees0"]
    ]
    game = GameState(
        len(rows[0]),
        len(rows),
        walkable,
        shacks,
        [list(row) for row in record["initial_inventories"]],
        units,
        plants,
        [0, 0],
        1,
        2,
        iron,
        water,
    )
    recompute_scores(game)
    for replay_turn in record["turns"]:
        if replay_turn["turn"] != game.turn:
            raise AssertionError(
                f"replay turn {replay_turn['turn']} does not match simulator turn {game.turn}"
            )
        step(game, replay_turn["commands0"], replay_turn["commands1"])
        actual_state = {
            "turn": game.turn,
            "next_id": game.next_id,
            "inventories": game.inventories,
            "scores": game.scores,
            "units": [
                {
                    "id": unit.id,
                    "player": unit.player,
                    "x": unit.x,
                    "y": unit.y,
                    "ms": unit.ms,
                    "cc": unit.cc,
                    "hp": unit.hp,
                    "chop": unit.chop,
                    "carry": unit.carry,
                }
                for unit in sorted(game.units, key=lambda item: item.id)
            ],
            "plants": [
                {
                    "type": plant.type,
                    "x": plant.x,
                    "y": plant.y,
                    "size": plant.size,
                    "health": plant.health,
                    "fruits": plant.fruits,
                    "cooldown": plant.cooldown,
                }
                for plant in sorted(
                    game.plants, key=lambda item: (item.x, item.y, item.type)
                )
            ],
        }
        expected_state = replay_turn.get("state")
        if expected_state is not None and actual_state != expected_state:
            differing = [
                name
                for name in actual_state
                if actual_state[name] != expected_state[name]
            ]
            raise AssertionError(
                f"state mismatch after turn {replay_turn['turn']} in {differing}: "
                f"python={actual_state}, rust={expected_state}"
            )
        actual = canonical_state_hash(game)
        expected = replay_turn["state_hash"]
        if actual != expected:
            raise AssertionError(
                f"state hash mismatch after turn {replay_turn['turn']}: "
                f"python={actual:#018x}, rust={expected:#018x}"
            )
    terminal = record["terminal_state_hash"]
    actual = canonical_state_hash(game)
    if actual != terminal:
        raise AssertionError(
            f"terminal hash mismatch: python={actual:#018x}, rust={terminal:#018x}"
        )
    return actual


def run_random_smoke(
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    maps_path: Path = DEFAULT_MAPS,
    random_seed: int = 0,
    opponent_weights: Mapping[str, float] | None = None,
    verify_replays: bool = False,
    library: Path | str = DEFAULT_LIBRARY,
) -> dict:
    rng = np.random.default_rng(random_seed)
    frozen = RandomFrozenOpponent(random_seed + 1)
    completed: dict[int, dict] = {}
    mini_steps = 0
    turn_steps = 0
    replay_parity = 0
    started = time.perf_counter()
    with FullVecEnv(
        num_envs,
        seed_base,
        maps_path,
        (
            {name: 1.0 for name in OPPONENTS}
            if opponent_weights is None
            else opponent_weights
        ),
        frozen_opponent=frozen,
        library=library,
    ) as env:
        while len(completed) < episodes:
            actions = random_legal_actions(env, rng)
            transitions, info = env.step(actions)
            mini_steps += len(transitions.actions)
            turn_steps += int(info.turn_completed.sum())
            for slot in np.flatnonzero(info.dones):
                seed = int(info.episode_seeds[slot])
                replay = env.take_replay(int(slot))
                if seed_base <= seed < seed_base + episodes:
                    if verify_replays:
                        if replay is None:
                            raise AssertionError(f"seed {seed} completed without a replay")
                        replay_and_verify(replay)
                        replay_parity += 1
                    completed[seed] = {
                        "seed": seed,
                        "turns": int(info.episode_turns[slot]),
                        "win": bool(info.wins[slot]),
                        "score_own": int(info.score_own[slot]),
                        "score_opp": int(info.score_opp[slot]),
                        "illegal_commands": int(info.illegal_commands[slot]),
                        "action_hash": int(info.action_hash[slot]),
                        "state_hash": int(info.state_hash[slot]),
                    }
    elapsed = time.perf_counter() - started
    rows = [completed[seed] for seed in range(seed_base, seed_base + episodes)]
    return {
        "episodes": episodes,
        "num_envs": num_envs,
        "seed_base": seed_base,
        "elapsed_seconds": elapsed,
        "mini_steps": mini_steps,
        "turn_steps": turn_steps,
        "turn_steps_per_second": turn_steps / elapsed,
        "illegal_commands": sum(row["illegal_commands"] for row in rows),
        "replay_parity": replay_parity,
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=16)
    parser.add_argument("--num-envs", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=1_000_000)
    parser.add_argument("--maps", type=Path, default=DEFAULT_MAPS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--self-play", action="store_true")
    parser.add_argument("--verify-replays", action="store_true")
    args = parser.parse_args()
    result = run_random_smoke(
        episodes=args.episodes,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        maps_path=args.maps,
        opponent_weights=(
            {"python_frozen": 1.0} if args.self_play else None
        ),
        verify_replays=args.verify_replays,
        library=args.library,
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
