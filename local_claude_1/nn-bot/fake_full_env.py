#!/usr/bin/env python3
"""A stand-in for the full-game environment, so the Phase-3 trainer can be run and
tested before the Rust library exists.

Plain words: the real environment (`cgauto/rl_full_env.py`, built by another agent) plays real
games of Troll Farm inside our Rust engine and hands the trainer a picture of the board plus the
list of commands that are allowed. That library is not finished yet. This file is a *fake* with
the same shape: it hands out pictures of the right size, allow-lists of the right size, and it
walks through the same sequence of little decisions (the "mini-steps") in the same order, paying
the reward in the same place. Nothing here plays a real game — every number is made up. It exists
only so that `train_ppo_full.py` can be exercised end to end, and so the tests can check the
trainer's arithmetic without a compiled library.

The surface copied from `local_claude_1/nn-bot/ENV-API.md` (signed 2026-08-29, on branch
`origin/agent/codex_1`):

* attributes ``obs`` ``u8[n,104,11,22]``, ``masks`` ``u8[n,13,11,22]``, ``plan_masks`` ``u8[n,400]``
  (400 since amendment (8) of the card), ``phase`` ``i32[n]``, ``seat_view`` ``i32[n]``,
  ``active_troll`` ``i32[n]``;
* phases ``0 PLAN`` -> ``1 TROLL`` once per own troll in ascending id order -> the turn executes;
* ``2 EXTERNAL_WAIT`` never reaches the caller: ``step()`` drives a Python-frozen opponent itself;
* the reward is paid **once, on the mini-step that executes the turn**; the earlier mini-steps of
  that turn carry reward 0 (the amendment on card `20260829-nn-bot-way-b.md`, "The mini-steps");
* ``step(actions)`` returns exactly ``(rewards, info)`` -- card amendment (9). ``rewards`` is
  ``f32[n]``; ``info`` is the frozen ``FullStepInfo`` record with exactly the terminal arrays of
  ``tf_full_step`` plus ``turn_completed``, no variable-length transition batch;
* completed slots auto-reset and the returned observation already belongs to the new episode;
* terminal fields are zero for unfinished slots;
* at the plan phase planes 59-71 show the STANDING target -- the previous turn's plan, kept until
  a TRAIN buys it -- and after the plan decision the newly selected one (amendment 8).

Deliberate deviations, all fake-only and marked here:

1. ``maps_path`` may be ``None`` or missing; the fake then invents map indices. The real
   environment refuses a missing map file. This is what lets the tests run with no data files.
2. The staged troll commands and the per-cell observation planes are not consistent with any real
   board. The shapes, the dtypes, the phase order, the reward placement, the step contract and the
   thirteen broadcast planes the plan head reads (43-48, 57-58, 59-71) are real.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

OBS_CHANNELS = 104
OBS_HEIGHT = 11
OBS_WIDTH = 22
ACTION_PLANES = 13
OBS_SIZE = OBS_CHANNELS * OBS_HEIGHT * OBS_WIDTH          # 25168
ACTION_SIZE = ACTION_PLANES * OBS_HEIGHT * OBS_WIDTH      # 3146
PLAN_SIZE = 400          # amendment (8): speed 1-4 x carry 1-5 x harvest 0-3 x chop 0-4
MAX_RECORDED_TRAINS = 4

PHASE_PLAN = 0
PHASE_TROLL = 1
PHASE_EXTERNAL_WAIT = 2

#: The seven training opponents, in the fixed order of ENV-API.md's weight vector.
OPPONENT_IDS = (
    "secure_orchard",
    "norxondor_native",
    "legend_field_proxy_v2",
    "gold_elite_adaptive",
    "script_boss",
    "mybot_boss4",
    "python_frozen",
)
PYTHON_FROZEN_ID = 6

#: The four real board sizes, as `(height, width)`.
BOARD_SIZES = ((11, 22), (10, 20), (9, 18), (8, 16))

#: The scales of the current-target planes 60-63 and of the cost/deficit planes 64-71 after
#: amendment (8).
PLAN_ATTRIBUTE_SCALES = (4.0, 5.0, 3.0, 4.0)
PLAN_COST_SCALE = 48.0

#: The generation id of the plan vocabulary; `plan_version()` reports it and the trainer refuses
#: an environment whose id is not the one it was built against.
PLAN_VOCAB_VERSION = "v400-2026-08-29"


def quantize(value: float, scale: float) -> int:
    """`round(255 * v / scale)`, clipped -- the quantization every plane uses."""

    return int(max(0, min(255, round(255.0 * value / scale))))


try:  # pragma: no cover - the real wrapper owns the record once codex_1 lands it
    from cgauto.rl_full_env import FullStepInfo
except ImportError:

    @dataclass(frozen=True)
    class FullStepInfo:
        """The named record `step()` returns beside the rewards (card amendment (9)).

        Exactly the terminal arrays of `tf_full_step`, all numpy arrays of length `num_envs`, in
        the order the card lists them. `cgauto/rl_full_env.py` will own this class; until it
        exists the fake defines it, and the import above picks up the real one the moment it
        lands, so the two cannot drift.
        """

        dones: np.ndarray              # u8[n]
        wins: np.ndarray               # u8[n]
        episode_turns: np.ndarray      # u16[n]
        episode_returns: np.ndarray    # f32[n]
        episode_seeds: np.ndarray      # u64[n]
        map_indices: np.ndarray        # u32[n]
        opponent_ids: np.ndarray       # u8[n]
        score_own: np.ndarray          # i32[n]
        score_opp: np.ndarray          # i32[n]
        trained_specs: np.ndarray      # i8[n,4,4]
        trained_turns: np.ndarray      # u16[n,4]
        trained_count: np.ndarray      # u8[n]
        trained_overflow: np.ndarray   # u8[n]
        illegal_commands: np.ndarray   # u16[n]
        action_hash: np.ndarray        # u64[n]
        state_hash: np.ndarray         # u64[n]
        turn_completed: np.ndarray     # u8[n]


def plan_talents(index: int) -> tuple[int, int, int, int]:
    """The talent set behind a flat plan index, amendment (8)'s 400-entry vocabulary.

    The index is `(((speed-1)*5 + (carry-1))*4 + harvest)*5 + chop`; index 0 decodes to
    `(1, 1, 0, 0)` and is repurposed as "train nothing".
    """

    chop = index % 5
    harvest = (index // 5) % 4
    carry = ((index // 20) % 5) + 1
    speed = (index // 100) + 1
    return speed, carry, harvest, chop


def plan_is_legal(index: int) -> bool:
    """The plan mask's one rule (amendment 8, second completion): every index in range is legal.

    Entry 0 is "train nothing". Neither `harvest > carry` nor `harvest 0 and chop 0` masks -- both
    were delineate's habits, not the game's rules -- and affordability never masks. The only thing
    the environment still masks is the global unit cap, which leaves entry 0 alone.
    """

    return 0 <= index < PLAN_SIZE


LEGAL_PLANS = np.arange(PLAN_SIZE, dtype=np.int64)


class FakeFullVecEnv:
    """A batched fake with FullVecEnv's surface. See the module docstring."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        maps_path: Path | str | None = None,
        opponent_weights: dict[str, float] | None = None,
        *,
        wood_shaping: float = 0.5,
        end_wood: float = 3.5,
        frozen_opponent=None,
        library: Path | str | None = None,
        min_turns: int = 20,
        max_turns: int = 60,
        max_trolls: int = 3,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if not 0 < min_turns <= max_turns:
            raise ValueError("turn bounds must satisfy 0 < min_turns <= max_turns")
        self.num_envs = int(num_envs)
        self.seed_base = int(seed_base)
        self.wood_shaping = float(wood_shaping)
        self.end_wood = float(end_wood)
        self.frozen_opponent = frozen_opponent
        self.library_path = None if library is None else Path(library)
        self.min_turns = int(min_turns)
        self.max_turns = int(max_turns)
        self.max_trolls = max(1, min(3, int(max_trolls)))

        self.maps_path = None if maps_path is None else Path(maps_path)
        self.map_count = 1000
        if self.maps_path is not None and self.maps_path.exists():
            with self.maps_path.open() as handle:
                self.map_count = max(1, sum(1 for line in handle if line.strip()))

        weights = dict(opponent_weights or {"secure_orchard": 1.0})
        vector = np.array(
            [float(weights.get(name, 0.0)) for name in OPPONENT_IDS], dtype=np.float64
        )
        if not np.isfinite(vector).all() or (vector < 0).any():
            raise ValueError("opponent weights must be finite and non-negative")
        if vector.sum() <= 0:
            raise ValueError("at least one opponent weight must be positive")
        self.opponent_weights = vector / vector.sum()

        self.obs = np.zeros(
            (self.num_envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.masks = np.zeros(
            (self.num_envs, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.plan_masks = np.zeros((self.num_envs, PLAN_SIZE), dtype=np.uint8)
        self.phase = np.zeros(self.num_envs, dtype=np.int32)
        self.seat_view = np.zeros(self.num_envs, dtype=np.int32)
        self.active_troll = np.full(self.num_envs, -1, dtype=np.int32)
        self.rewards = np.zeros(self.num_envs, dtype=np.float32)
        self.turn_completed = np.zeros(self.num_envs, dtype=np.uint8)
        self.reward_credit_count = np.zeros(self.num_envs, dtype=np.uint8)

        self._dones = np.zeros(self.num_envs, dtype=np.uint8)
        self._wins = np.zeros(self.num_envs, dtype=np.uint8)
        self._episode_turns = np.zeros(self.num_envs, dtype=np.uint16)
        self._episode_returns = np.zeros(self.num_envs, dtype=np.float32)
        self._episode_seeds = np.zeros(self.num_envs, dtype=np.uint64)
        self._map_indices = np.zeros(self.num_envs, dtype=np.uint32)
        self._opponent_ids = np.zeros(self.num_envs, dtype=np.uint8)
        self._score_own = np.zeros(self.num_envs, dtype=np.int32)
        self._score_opp = np.zeros(self.num_envs, dtype=np.int32)
        self._trained_specs = np.zeros(
            (self.num_envs, MAX_RECORDED_TRAINS, 4), dtype=np.int8
        )
        self._trained_turns = np.zeros(
            (self.num_envs, MAX_RECORDED_TRAINS), dtype=np.uint16
        )
        self._trained_count = np.zeros(self.num_envs, dtype=np.uint8)
        self._trained_overflow = np.zeros(self.num_envs, dtype=np.uint8)
        self._illegal_commands = np.zeros(self.num_envs, dtype=np.uint16)
        self._action_hash = np.zeros(self.num_envs, dtype=np.uint64)
        self._state_hash = np.zeros(self.num_envs, dtype=np.uint64)

        self._next_seed = self.seed_base + self.num_envs
        self._slots: list[dict] = []
        self._closed = False
        for slot in range(self.num_envs):
            self._slots.append(self._new_episode(self.seed_base + slot))
        self._write_views()

    # ------------------------------------------------------------------ episodes

    def _new_episode(self, seed: int) -> dict:
        rng = np.random.default_rng(seed)
        height, width = BOARD_SIZES[int(rng.integers(len(BOARD_SIZES)))]
        return {
            "seed": int(seed),
            "rng": rng,
            "height": height,
            "width": width,
            "map_index": int(rng.integers(self.map_count)),
            # Four maps in five have iron; the rest waive the iron cost entirely.
            "has_iron": bool(rng.random() < 0.8),
            "seat": int(rng.integers(2)),
            "opponent": int(rng.choice(len(OPPONENT_IDS), p=self.opponent_weights)),
            "turn": 0,
            "total_turns": int(rng.integers(self.min_turns, self.max_turns + 1)),
            # plum, lemon, apple, banana, iron, wood -- the referee's 2..10 opening draw
            "bank": [int(rng.integers(2, 11)) for _ in range(5)] + [0],
            # The standing target starts at zero and returns to zero when a TRAIN succeeds.
            "standing_target": 0,
            "trolls": 1,
            "troll_index": 0,
            "phase": PHASE_PLAN,
            "plan": 0,
            "score_own": 0,
            "score_opp": 0,
            "wood_own": 0,
            "wood_opp": 0,
            "episode_return": 0.0,
            "trains": [],
            "commands": [],
        }

    def _troll_ids(self, state: dict) -> list[int]:
        return list(range(state["trolls"]))

    # ------------------------------------------------------------------ views

    def _write_views(self) -> None:
        for slot, state in enumerate(self._slots):
            self._write_slot(slot, state)

    @staticmethod
    def _write_target_planes(obs: np.ndarray, state: dict, index: int) -> None:
        """Planes 59-71: the train target, its four costs and its four deficits.

        `cost_i = own troll count + talent_i^2` for plum/lemon/apple/iron and
        `deficit_i = max(cost_i - own bank_i, 0)`, quantized at S=48 (amendment 8). Index 0 --
        "train nothing" -- zeroes all thirteen planes.
        """

        obs[59:72, :, :] = 0
        if index == 0:
            return
        talents = plan_talents(index)
        obs[59, :, :] = 255
        for offset, (value, scale) in enumerate(zip(talents, PLAN_ATTRIBUTE_SCALES)):
            obs[60 + offset, :, :] = quantize(value, scale)
        banks = (state["bank"][0], state["bank"][1], state["bank"][2], state["bank"][4])
        for offset, (talent, bank) in enumerate(zip(talents, banks)):
            # Iron is the fourth resource, and an iron-free map waives it.
            if offset == 3 and not state["has_iron"]:
                continue
            cost = state["trolls"] + talent * talent
            obs[64 + offset, :, :] = quantize(cost, PLAN_COST_SCALE)
            obs[68 + offset, :, :] = quantize(max(cost - bank, 0), PLAN_COST_SCALE)

    def _write_slot(self, slot: int, state: dict) -> None:
        height, width = state["height"], state["width"]
        rng = state["rng"]
        obs = self.obs[slot]
        obs[:] = 0
        obs[0, :height, :width] = 255                      # plane 0: the valid-cell mask
        obs[1:4, :height, :width] = rng.integers(
            0, 256, size=(3, height, width), dtype=np.uint8
        )
        obs[5:16, :height, :width] = rng.integers(
            0, 256, size=(11, height, width), dtype=np.uint8
        )
        # Plane 4 is the iron cell, and the scorer waives the iron cost when it is empty.
        if state["has_iron"]:
            obs[4, height // 2, width // 2] = 255
        obs[42, :, :] = min(255, state["turn"] * 255 // max(1, state["total_turns"]))
        obs[55, :, :] = min(255, state["score_own"])
        obs[56, :, :] = min(255, state["score_opp"])
        # The broadcast planes the plan head reads back (OBS-PLANES.md, amendment 8's scales).
        for offset, amount in enumerate(state["bank"][:5]):
            obs[43 + offset, :, :] = quantize(amount, 64.0)
        obs[48, :, :] = quantize(state["bank"][5], 128.0)
        obs[57, :, :] = quantize(state["trolls"], 12.0)
        obs[58, :, :] = quantize(state["trolls"], 12.0)
        # Target memory (amendment 8, "Target memory"): at the plan phase the planes show the
        # STANDING target -- the previous turn's plan, kept until it is trained -- and after the
        # plan decision they show the newly selected one.
        shown = (
            state["standing_target"]
            if state["phase"] == PHASE_PLAN
            else state["plan"]
        )
        self._write_target_planes(obs, state, shown)

        self.masks[slot] = 0
        self.plan_masks[slot] = 0
        self.phase[slot] = state["phase"]
        self.seat_view[slot] = state["seat"]

        if state["phase"] == PHASE_PLAN:
            self.active_troll[slot] = -1
            # One rule: entry 0 is always legal and so is every other entry -- unless the global
            # unit cap is reached, and then only entry 0 is.
            self.plan_masks[slot, 0] = 1
            if state["trolls"] < self.max_trolls:
                self.plan_masks[slot, :] = 1
            return

        troll = self._troll_ids(state)[state["troll_index"]]
        self.active_troll[slot] = troll
        obs[99, :, :] = 0
        troll_y = int(rng.integers(height))
        troll_x = int(rng.integers(width))
        obs[99, troll_y, troll_x] = 255                    # plane 99: the active troll
        # MOVE (plane 0) is legal on the troll's own cell and on a random reachable subset.
        self.masks[slot, 0, troll_y, troll_x] = 1
        reach = rng.integers(0, 2, size=(height, width), dtype=np.uint8)
        self.masks[slot, 0, :height, :width] |= reach
        # The other verbs live only on the troll's own cell, as ENV-API.md requires.
        verbs = rng.integers(0, 2, size=ACTION_PLANES - 1, dtype=np.uint8)
        self.masks[slot, 1:, troll_y, troll_x] = verbs
        state["troll_cell"] = (troll_y, troll_x)

    # ------------------------------------------------------------------ stepping

    def _current_mask(self, slot: int) -> np.ndarray:
        if self.phase[slot] == PHASE_PLAN:
            return self.plan_masks[slot]
        return self.masks[slot].reshape(-1)

    def step(self, actions: np.ndarray):
        """One mini-step for every slot. See the module docstring for the return contract."""

        if self._closed:
            raise RuntimeError("step() on a closed environment")
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(
                f"expected actions shape {(self.num_envs,)}, got {actions.shape}"
            )
        # Batch-atomic validation, the real library's status -4.
        for slot in range(self.num_envs):
            index = int(actions[slot])
            mask = self._current_mask(slot)
            if not 0 <= index < mask.shape[0] or mask[index] == 0:
                raise RuntimeError(
                    f"action {index} is outside the mask in slot {slot} "
                    f"(phase {int(self.phase[slot])})"
                )

        self.rewards[:] = 0.0
        self.turn_completed[:] = 0
        self.reward_credit_count[:] = 0
        self._zero_terminals()

        for slot in range(self.num_envs):
            self._advance(slot, int(actions[slot]))

        info = FullStepInfo(
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
            turn_completed=self.turn_completed.copy(),
        )
        return self.rewards.copy(), info

    def _zero_terminals(self) -> None:
        for array in (
            self._dones,
            self._wins,
            self._episode_turns,
            self._episode_returns,
            self._episode_seeds,
            self._map_indices,
            self._opponent_ids,
            self._score_own,
            self._score_opp,
            self._trained_turns,
            self._trained_count,
            self._trained_overflow,
            self._illegal_commands,
            self._action_hash,
            self._state_hash,
        ):
            array[...] = 0
        self._trained_specs[...] = 0

    def _advance(self, slot: int, action: int) -> None:
        state = self._slots[slot]
        state["commands"].append(action)

        if state["phase"] == PHASE_PLAN:
            state["plan"] = action
            state["phase"] = PHASE_TROLL
            state["troll_index"] = 0
            self._write_slot(slot, state)
            return

        state["troll_index"] += 1
        if state["troll_index"] < state["trolls"]:
            self._write_slot(slot, state)
            return

        self._execute_turn(slot, state)

    def _execute_turn(self, slot: int, state: dict) -> None:
        rng = state["rng"]
        # The opponent decides. A python_frozen opponent is driven here, inside step(), so the
        # learner never sees phase 2 EXTERNAL_WAIT -- ENV-API.md's FullVecEnv contract.
        if state["opponent"] == PYTHON_FROZEN_ID and self.frozen_opponent is not None:
            self._drive_frozen_opponent(slot, state)

        for slot_index in range(5):
            state["bank"][slot_index] = min(
                60, state["bank"][slot_index] + int(rng.integers(0, 3))
            )
        wood_own = int(rng.integers(0, 3))
        wood_opp = int(rng.integers(0, 3))
        state["wood_own"] += wood_own
        state["wood_opp"] += wood_opp
        state["bank"][5] += wood_own
        state["score_own"] += int(rng.integers(0, 4)) + wood_own
        state["score_opp"] += int(rng.integers(0, 4)) + wood_opp
        trained = (
            state["plan"] != 0 and len(state["trains"]) < 8 and rng.random() < 0.05
        )
        if trained:
            state["trains"].append((plan_talents(state["plan"]), state["turn"] + 1))
            state["trolls"] = min(self.max_trolls, state["trolls"] + 1)
        # The plan the trolls keep collecting towards: cleared once it has been bought.
        state["standing_target"] = 0 if trained else state["plan"]

        reward = self.wood_shaping * wood_own
        state["turn"] += 1
        done = state["turn"] >= state["total_turns"]
        if done:
            reward += float(
                (state["score_own"] + self.end_wood * state["wood_own"])
                - (state["score_opp"] + self.end_wood * state["wood_opp"])
            )
        state["episode_return"] += reward

        # The reward is paid once, here, on the mini-step that executes the turn.
        self.rewards[slot] = np.float32(reward)
        self.turn_completed[slot] = 1
        self.reward_credit_count[slot] = 1 + state["trolls"]

        if not done:
            state["phase"] = PHASE_PLAN
            state["troll_index"] = 0
            self._write_slot(slot, state)
            return

        self._finish(slot, state)

    def _drive_frozen_opponent(self, slot: int, state: dict) -> None:
        """Ask the frozen self-play opponent for its own PLAN and TROLL decisions.

        NOT MATCHED TO THE REAL INTERFACE. ENV-API.md fixes the C calls
        (`tf_full_opponent_observe` / `tf_full_opponent_step`) but leaves the Python callable's
        signature open ("frozen_opponent: Callable | None"). The fake calls it as
        ``frozen_opponent(obs, masks, plan_masks, phase, active_troll, seat_view, needs_action)``
        and expects ``int32[n]`` back, with ``-1`` in every slot that is not waiting. If the real
        wrapper settles on another shape, only `train_ppo_full.FrozenOpponent.__call__` changes.
        """

        rng = state["rng"]
        for mini in range(1 + state["trolls"]):
            obs = np.zeros(
                (self.num_envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
            )
            masks = np.zeros(
                (self.num_envs, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
            )
            plan_masks = np.zeros((self.num_envs, PLAN_SIZE), dtype=np.uint8)
            phase = np.full(self.num_envs, -1, dtype=np.int32)
            active = np.full(self.num_envs, -1, dtype=np.int32)
            seat = np.full(self.num_envs, -1, dtype=np.int32)
            needs = np.zeros(self.num_envs, dtype=np.uint8)

            obs[slot, 0, : state["height"], : state["width"]] = 255
            needs[slot] = 1
            seat[slot] = 1 - state["seat"]
            if mini == 0:
                phase[slot] = PHASE_PLAN
                plan_masks[slot, 0] = 1
                plan_masks[slot, LEGAL_PLANS[rng.integers(len(LEGAL_PLANS))]] = 1
            else:
                phase[slot] = PHASE_TROLL
                active[slot] = mini - 1
                masks[slot, 0, 0, 0] = 1

            reply = self.frozen_opponent(
                obs, masks, plan_masks, phase, active, seat, needs
            )
            reply = np.ascontiguousarray(reply, dtype=np.int32)
            if reply.shape != (self.num_envs,):
                raise RuntimeError(
                    "the frozen opponent must return one action per slot, got "
                    f"shape {reply.shape}"
                )

    def _finish(self, slot: int, state: dict) -> None:
        self._dones[slot] = 1
        self._wins[slot] = 1 if state["score_own"] > state["score_opp"] else 0
        self._episode_turns[slot] = state["turn"]
        self._episode_returns[slot] = np.float32(state["episode_return"])
        self._episode_seeds[slot] = np.uint64(state["seed"])
        self._map_indices[slot] = np.uint32(state["map_index"])
        self._opponent_ids[slot] = np.uint8(state["opponent"])
        self._score_own[slot] = np.int32(state["score_own"])
        self._score_opp[slot] = np.int32(state["score_opp"])
        for index, (spec, turn) in enumerate(state["trains"][:MAX_RECORDED_TRAINS]):
            self._trained_specs[slot, index] = np.array(spec, dtype=np.int8)
            self._trained_turns[slot, index] = np.uint16(turn)
        self._trained_count[slot] = np.uint8(min(255, len(state["trains"])))
        self._trained_overflow[slot] = np.uint8(
            max(0, len(state["trains"]) - MAX_RECORDED_TRAINS)
        )
        self._illegal_commands[slot] = 0
        digest = hashlib.sha256(
            json.dumps(state["commands"]).encode()
        ).digest()
        self._action_hash[slot] = np.frombuffer(digest[:8], dtype=np.uint64)[0]
        self._state_hash[slot] = np.frombuffer(digest[8:16], dtype=np.uint64)[0]

        seed = self._next_seed
        self._next_seed += 1
        self._slots[slot] = self._new_episode(seed)
        self._write_slot(slot, self._slots[slot])

    # ------------------------------------------------------------------ lifecycle

    @staticmethod
    def plan_version() -> str:
        """The generation id of the plan vocabulary this environment speaks (amendment 8)."""

        return PLAN_VOCAB_VERSION

    def observe(self):
        return self.obs, self.masks, self.plan_masks, self.phase, self.seat_view, self.active_troll

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> "FakeFullVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def random_legal_actions(env: FakeFullVecEnv, rng: np.random.Generator) -> np.ndarray:
    """One uniformly drawn legal action per slot, for the phase each slot is in."""

    out = np.empty(env.num_envs, dtype=np.int32)
    for slot in range(env.num_envs):
        mask = env._current_mask(slot)
        legal = np.flatnonzero(mask)
        if not len(legal):
            raise RuntimeError(f"empty action mask in slot {slot}")
        out[slot] = legal[rng.integers(len(legal))]
    return out
