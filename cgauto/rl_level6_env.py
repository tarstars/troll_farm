#!/usr/bin/env python3
"""Full-length competitive environment and frozen-policy evaluator for D21."""

from __future__ import annotations

import argparse
from collections import defaultdict
import ctypes
import json
from pathlib import Path
import sys
import time

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level1_env import ACTION_SIZE, random_legal_actions
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, level2_recipe
from cgauto.rl_level5_env import Level5VecEnv


LEVEL6_OPPONENT_NAMES = (
    "complete_baseline",
    "renewable_planter",
    "one_shot_reaper",
    "funded_pair",
    "sustained_funded_trio",
    "crop_first_repeated_pressure_reacquire",
)
LEVEL6_OPPONENT_XOR = 0x4C366F70706F6E65
MASK64 = (1 << 64) - 1


def level6_opponent(seed: int) -> tuple[int, str]:
    """Mirror the frozen independent Rust opponent assignment."""

    value = (int(seed) ^ LEVEL6_OPPONENT_XOR) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    opponent_id = value % len(LEVEL6_OPPONENT_NAMES)
    return opponent_id, LEVEL6_OPPONENT_NAMES[opponent_id]


class Level6VecEnv(Level5VecEnv):
    """Two-worker actor versus a deterministic mixed strategic curriculum."""

    ffi_prefix = "tf_level6"

    def _configure_abi(self) -> None:
        super()._configure_abi()
        self._current_metadata = self._lib.tf_level6_current_metadata
        self._current_metadata.argtypes = [ctypes.c_void_p] * 4
        self._current_metadata.restype = ctypes.c_int32

    def current_metadata(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return exact live turn, sequential phase, and seed for every vector slot."""

        turns = np.empty(self.num_envs, dtype=np.uint16)
        phases = np.empty(self.num_envs, dtype=np.uint8)
        seeds = np.empty(self.num_envs, dtype=np.uint64)
        status = self._current_metadata(
            self._handle,
            self._ptr(turns),
            self._ptr(phases),
            self._ptr(seeds),
        )
        if status != 0:
            raise RuntimeError(f"tf_level6_current_metadata failed with {status}")
        return turns, phases, seeds


def _summary(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": float(np.mean(values)) if values else None,
        "median": float(np.median(values)) if values else None,
        "minimum": float(np.min(values)) if values else None,
        "maximum": float(np.max(values)) if values else None,
    }


def _bucket(rows: list[dict]) -> dict:
    margins = [row["margin"] for row in rows]
    return {
        "episodes": len(rows),
        "wins": sum(value > 0 for value in margins),
        "ties": sum(value == 0 for value in margins),
        "losses": sum(value < 0 for value in margins),
        "win_rate": sum(value > 0 for value in margins) / len(rows) if rows else None,
        "margin": _summary(margins),
        "own_score": _summary([row["own_score"] for row in rows]),
        "opponent_score": _summary([row["opponent_score"] for row in rows]),
        "training_completion_rate": (
            sum(row["training_completed"] for row in rows) / len(rows) if rows else None
        ),
        "crop_creation_rate": (
            sum(row["created_crop"] for row in rows) / len(rows) if rows else None
        ),
        "renewable_harvest_rate": (
            sum(row["renewable_harvests"] > 0 for row in rows) / len(rows)
            if rows
            else None
        ),
    }


def aggregate(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    by_recipe: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
        by_recipe[str(row["recipe_id"])].append(row)
    return {
        **_bucket(rows),
        "terminal_turn_min": min(row["turn"] for row in rows),
        "terminal_turn_max": max(row["turn"] for row in rows),
        "maximum_return_margin_error": max(
            row["return_margin_error"] for row in rows
        ),
        "minimum_opponent_episodes": min(len(value) for value in by_opponent.values()),
        "minimum_recipe_episodes": min(len(value) for value in by_recipe.values()),
        "by_opponent": {
            name: _bucket(by_opponent[name]) for name in LEVEL6_OPPONENT_NAMES
        },
        "by_recipe": {
            str(recipe_id): {
                "name": LEVEL2_RECIPE_NAMES[recipe_id],
                **_bucket(by_recipe[str(recipe_id)]),
            }
            for recipe_id in range(len(LEVEL2_RECIPE_NAMES))
        },
    }


def run_policy(
    policy: str,
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    max_turns: int = 300,
    random_seed: int = 2101,
    checkpoint: Path | None = None,
    threads: int = 14,
) -> dict:
    if policy not in ("teacher", "random", "actor"):
        raise ValueError(f"unsupported policy {policy}")
    if episodes <= 0 or num_envs <= 0:
        raise ValueError("episodes and num_envs must be positive")
    model = None
    device = None
    checkpoint_sha256 = None
    if policy == "actor":
        if checkpoint is None or not checkpoint.exists():
            raise FileNotFoundError("actor policy requires an existing checkpoint")
        import torch

        from cgauto.train_level1_ppo import SpatialActorCritic, sha256

        torch.set_num_threads(threads)
        torch.set_num_interop_threads(min(4, threads))
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        model = SpatialActorCritic()
        model.load_state_dict(saved["model"])
        model.eval()
        device = next(model.parameters()).device
        checkpoint_sha256 = sha256(checkpoint)

    rng = np.random.default_rng(random_seed)
    stop = seed_base + episodes
    completed: dict[int, dict] = {}
    transitions = 0
    illegal_selected_actions = 0
    started = time.perf_counter()
    with Level6VecEnv(num_envs, seed_base, max_turns=max_turns) as env:
        while len(completed) < episodes:
            if policy == "teacher":
                actions = env.teacher_actions()
            elif policy == "random":
                actions = random_legal_actions(env.masks, rng)
            else:
                import torch

                assert model is not None and device is not None
                with torch.inference_mode():
                    selected, _, _, _ = model.action_and_value(
                        torch.from_numpy(env.obs).to(device),
                        torch.from_numpy(env.masks).to(device),
                        deterministic=True,
                    )
                actions = selected.cpu().numpy().astype(np.int32, copy=False)
            legal = env.masks.reshape(num_envs, ACTION_SIZE)
            illegal_selected_actions += int(
                np.count_nonzero(legal[np.arange(num_envs), actions] == 0)
            )
            _, _, _, info = env.step(actions)
            transitions += num_envs
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if not seed_base <= seed < stop:
                    continue
                recipe_id = int(info.recipe_ids[index])
                expected_recipe, expected_target = level2_recipe(seed)
                target = tuple(int(value) for value in info.targets[index])
                if (recipe_id, target) != (expected_recipe, expected_target):
                    raise RuntimeError(f"terminal recipe mismatch for seed {seed}")
                opponent_id, opponent = level6_opponent(seed)
                own_score = int(info.score_gains[index])
                opponent_score = int(info.opponent_scores[index])
                margin = own_score - opponent_score
                episode_return = float(info.returns[index])
                completed[seed] = {
                    "seed": seed,
                    "opponent_id": opponent_id,
                    "opponent": opponent,
                    "recipe_id": recipe_id,
                    "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                    "target": list(target),
                    "height": int(info.heights[index]),
                    "turn": int(info.turns[index]),
                    "return": episode_return,
                    "own_score": own_score,
                    "opponent_score": opponent_score,
                    "margin": margin,
                    "return_margin_error": abs(episode_return * 100.0 - margin),
                    "win": margin > 0,
                    "training_turn": int(info.training_turns[index]),
                    "training_completed": int(info.training_turns[index]) > 0,
                    "created_crop": bool(info.created_crops[index]),
                    "renewable_harvests": int(info.renewable_harvests[index]),
                    "opponent_workers": int(info.opponent_workers[index]),
                    "opponent_created_crops": int(info.opponent_created_crops[index]),
                    "opponent_renewable_harvests": int(
                        info.opponent_renewable_harvests[index]
                    ),
                    "opponent_crop_destructions": int(
                        info.opponent_crop_destructions[index]
                    ),
                }
    elapsed = time.perf_counter() - started
    rows = [completed[seed] for seed in range(seed_base, stop)]
    return {
        "schema": 1,
        "scope": "D21 full-length competitive preflight; score_gain ABI field carries own terminal score",
        "policy": policy,
        "seed_base": seed_base,
        "seed_stop_exclusive": stop,
        "episodes": episodes,
        "num_envs": num_envs,
        "max_turns": max_turns,
        "random_seed": random_seed if policy == "random" else None,
        "checkpoint": str(checkpoint) if checkpoint else None,
        "checkpoint_sha256": checkpoint_sha256,
        "threads": threads if policy == "actor" else None,
        "transitions": transitions,
        "elapsed_seconds": elapsed,
        "transitions_per_second": transitions / elapsed,
        "illegal_selected_actions": illegal_selected_actions,
        "aggregate": aggregate(rows),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=("teacher", "random", "actor"), required=True)
    parser.add_argument("--episodes", type=int, default=480)
    parser.add_argument("--num-envs", type=int, default=80)
    parser.add_argument("--seed-base", type=int, default=8_000_000)
    parser.add_argument("--max-turns", type=int, default=300)
    parser.add_argument("--random-seed", type=int, default=2101)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run_policy(
        args.policy,
        episodes=args.episodes,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        max_turns=args.max_turns,
        random_seed=args.random_seed,
        checkpoint=args.checkpoint,
        threads=args.threads,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in payload.items() if key != "rows"}, indent=2))
    print(f"saved {args.output}")


if __name__ == "__main__":
    main()
