#!/usr/bin/env python3
"""Audit Level-2 deterministic actions by recipe and needed work opportunity."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import numpy as np
import torch

from cgauto.rl_level1_env import OBS_HEIGHT, OBS_WIDTH
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, LEVEL2_TARGETS, Level2VecEnv
from cgauto.train_level1_ppo import SpatialActorCritic


ACTION_NAMES = (
    "MOVE",
    "HARVEST",
    "CHOP",
    "DROP",
    "MINE",
    "PLANT_PLUM",
    "PLANT_LEMON",
    "PLANT_APPLE",
    "PLANT_BANANA",
    "PICK_PLUM",
    "PICK_LEMON",
    "PICK_APPLE",
    "PICK_BANANA",
)
PLANT_CHANNELS = (("PLUM", 32), ("LEMON", 38), ("APPLE", 44), ("BANANA", 50))
DEFICIT_CHANNELS = {"PLUM": 94, "LEMON": 95, "APPLE": 96, "IRON": 97}
CELLS = OBS_HEIGHT * OBS_WIDTH


def move_kind(observation: np.ndarray, y: int, x: int) -> str:
    if observation[7, y, x]:
        return "WAIT_CURRENT"
    if observation[5, y, x]:
        return "HOME"
    for name, channel in PLANT_CHANNELS:
        if observation[channel, y, x]:
            return name
    if observation[3, y, x] or not observation[1, y, x]:
        return "IRON_SOURCE"
    return "OTHER"


def needed_work_kind(observation: np.ndarray, mask: np.ndarray) -> str | None:
    """Return the currently legal productive verb needed by the requested recipe."""

    if mask[1].any():
        selected = np.argwhere(observation[7] != 0)
        if len(selected) == 1:
            y, x = (int(value) for value in selected[0])
            for name, channel in PLANT_CHANNELS[:3]:
                if observation[channel, y, x] and observation[
                    DEFICIT_CHANNELS[name], 0, 0
                ]:
                    return "HARVEST"
    if mask[4].any() and observation[DEFICIT_CHANNELS["IRON"], 0, 0]:
        return "MINE"
    return None


def audit(
    checkpoint: Path,
    *,
    seed_base: int,
    episodes: int,
    num_envs: int,
    threads: int,
    max_turns: int = 240,
) -> dict:
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(min(4, threads))
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"])
    model.eval()
    target_stop = seed_base + episodes
    slot_actions = [collections.Counter() for _ in range(num_envs)]
    slot_moves = [collections.Counter() for _ in range(num_envs)]
    slot_opportunities = [collections.Counter() for _ in range(num_envs)]
    completed: dict[int, dict] = {}
    action_totals = collections.Counter()
    move_targets = collections.Counter()
    opportunities = collections.Counter()

    with Level2VecEnv(
        num_envs, seed_base, max_turns=max_turns
    ) as env:
        while len(completed) < episodes:
            observations = env.obs.copy()
            masks = env.masks.copy()
            with torch.inference_mode():
                actions, _, _, _ = model.action_and_value(
                    torch.from_numpy(env.obs),
                    torch.from_numpy(env.masks),
                    deterministic=True,
                )
            actions_np = actions.numpy()
            for index, selected in enumerate(actions_np):
                plane = int(selected) // CELLS
                cell = int(selected) % CELLS
                y, x = divmod(cell, OBS_WIDTH)
                name = ACTION_NAMES[plane]
                slot_actions[index][name] += 1
                work_kind = needed_work_kind(observations[index], masks[index])
                if work_kind is not None:
                    slot_opportunities[index]["NEEDED_WORK_LEGAL"] += 1
                    slot_opportunities[index][f"NEEDED_{work_kind}_LEGAL"] += 1
                    slot_opportunities[index][f"NEEDED_WORK_CHOSE_{name}"] += 1
                    if name == work_kind:
                        slot_opportunities[index]["NEEDED_WORK_CHOSE_PRODUCTIVE"] += 1
                        slot_opportunities[index][
                            f"NEEDED_{work_kind}_CHOSE_{work_kind}"
                        ] += 1
                if masks[index, 3].any():
                    slot_opportunities[index]["DROP_LEGAL"] += 1
                    slot_opportunities[index][f"DROP_LEGAL_CHOSE_{name}"] += 1
                if plane == 0:
                    target_kind = move_kind(observations[index], y, x)
                    slot_moves[index][target_kind] += 1
                    slot_actions[index][f"MOVE_{target_kind}"] += 1
            _, _, _, info = env.step(actions_np.astype(np.int32, copy=False))
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if seed_base <= seed < target_stop:
                    recipe_id = int(info.recipe_ids[index])
                    completed[seed] = {
                        "seed": seed,
                        "success": bool(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "height": int(info.heights[index]),
                        "recipe_id": recipe_id,
                        "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                        "target": [int(value) for value in info.targets[index]],
                        "initial_total_deficit": int(
                            info.initial_total_deficits[index]
                        ),
                        "actions": dict(slot_actions[index]),
                        "opportunities": dict(slot_opportunities[index]),
                    }
                    action_totals.update(
                        {
                            key: count
                            for key, count in slot_actions[index].items()
                            if not key.startswith("MOVE_")
                        }
                    )
                    move_targets.update(slot_moves[index])
                    opportunities.update(slot_opportunities[index])
                slot_actions[index] = collections.Counter()
                slot_moves[index] = collections.Counter()
                slot_opportunities[index] = collections.Counter()

    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    by_recipe = {}
    for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
        bucket = [row for row in rows if row["recipe_id"] == recipe_id]
        successes = sum(row["success"] for row in bucket)
        needed = sum(
            row["opportunities"].get("NEEDED_WORK_LEGAL", 0) for row in bucket
        )
        productive = sum(
            row["opportunities"].get("NEEDED_WORK_CHOSE_PRODUCTIVE", 0)
            for row in bucket
        )
        by_recipe[str(recipe_id)] = {
            "name": name,
            "target": list(LEVEL2_TARGETS[recipe_id]),
            "episodes": len(bucket),
            "successes": successes,
            "success_rate": successes / len(bucket),
            "needed_work_opportunities": needed,
            "productive_choices": productive,
            "productive_choice_rate": productive / needed if needed else None,
            "move_current_waits": sum(
                row["actions"].get("MOVE_WAIT_CURRENT", 0) for row in bucket
            ),
        }
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        successes = sum(row["success"] for row in bucket)
        by_height[str(height)] = {
            "episodes": len(bucket),
            "successes": successes,
            "success_rate": successes / len(bucket),
        }
    nontrivial = [row for row in rows if row["initial_total_deficit"] > 0]
    successful = [row for row in rows if row["success"]]
    needed = opportunities["NEEDED_WORK_LEGAL"]
    productive = opportunities["NEEDED_WORK_CHOSE_PRODUCTIVE"]
    return {
        "checkpoint": str(checkpoint),
        "curriculum_level": 2,
        "seed_base": seed_base,
        "seed_stop_exclusive": target_stop,
        "exact_seed_interval": True,
        "episodes": episodes,
        "successes": len(successful),
        "success_rate": len(successful) / len(rows),
        "median_success_turn": (
            float(np.median([row["turns"] for row in successful]))
            if successful
            else None
        ),
        "by_recipe": by_recipe,
        "by_height": by_height,
        "nontrivial_episodes": len(nontrivial),
        "nontrivial_successes": sum(row["success"] for row in nontrivial),
        "nontrivial_success_rate": sum(row["success"] for row in nontrivial)
        / len(nontrivial),
        "action_totals": dict(action_totals),
        "move_targets": dict(move_targets),
        "work_opportunities": dict(opportunities),
        "needed_productive_choice_rate": productive / needed if needed else None,
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--seed-base", type=int, default=2_005_000)
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--max-turns", type=int, default=240)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(
        args.checkpoint,
        seed_base=args.seed_base,
        episodes=args.episodes,
        num_envs=args.num_envs,
        threads=args.threads,
        max_turns=args.max_turns,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    summary = {key: value for key, value in result.items() if key != "episodes_detail"}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
