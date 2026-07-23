#!/usr/bin/env python3
"""Audit Level-3/4 deterministic actions by role and teacher opportunity."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import numpy as np
import torch

from cgauto.rl_level1_env import OBS_HEIGHT, OBS_WIDTH
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, LEVEL2_TARGETS
from cgauto.rl_level3_env import LEVEL3_SCORE_GAIN, LEVEL3_TARGET, Level3VecEnv
from cgauto.rl_level4_env import Level4VecEnv
from cgauto.rl_level5_env import Level5CropFirstRepeatedPressureReacquire180VecEnv
from cgauto.train_level1_ppo import SpatialActorCritic, sha256


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
CELLS = OBS_HEIGHT * OBS_WIDTH
POST_TRAIN_CHANNEL = 94
FARMER_CHANNEL = 95
CHOPPER_CHANNEL = 96
CROP_EXISTS_CHANNEL = 92
BANANA_PLANT_CHANNEL = 50
BANANA_FRUIT_CHANNEL = 53
OWN_BANANA_INVENTORY_CHANNEL = 59
ACTIVE_CARRY_CHANNELS = slice(68, 74)


def selected_cell(observation: np.ndarray) -> tuple[int, int]:
    cells = np.argwhere(observation[7] != 0)
    if len(cells) != 1:
        raise ValueError(f"expected one selected-unit cell, found {len(cells)}")
    return tuple(int(value) for value in cells[0])


def is_move_current(observation: np.ndarray, action: int) -> bool:
    if action // CELLS != 0:
        return False
    y, x = selected_cell(observation)
    return action % CELLS == y * OBS_WIDTH + x


def role_name(observation: np.ndarray) -> str | None:
    if observation[POST_TRAIN_CHANNEL, 0, 0] != 255:
        return None
    farmer = observation[FARMER_CHANNEL, 0, 0] == 255
    chopper = observation[CHOPPER_CHANNEL, 0, 0] == 255
    if farmer == chopper:
        raise ValueError("post-training observation must identify exactly one active role")
    return "farmer" if farmer else "chopper"


def is_justified_unripe_crop_wait(observation: np.ndarray, action: int) -> bool:
    """The one wait explicitly exempted by the frozen Level-3 protocol."""

    if role_name(observation) != "farmer" or not is_move_current(observation, action):
        return False
    if not observation[CROP_EXISTS_CHANNEL, 0, 0]:
        return False
    y, x = selected_cell(observation)
    return bool(
        observation[BANANA_PLANT_CHANNEL, y, x]
        and not observation[BANANA_FRUIT_CHANNEL, y, x]
    )


def is_empty_seed_recovery_opportunity(observation: np.ndarray) -> bool:
    """Whether D11's active farmer must reacquire a real banana source."""

    return bool(
        role_name(observation) == "farmer"
        and observation[CROP_EXISTS_CHANNEL, 0, 0] == 0
        and observation[OWN_BANANA_INVENTORY_CHANNEL, 0, 0] == 0
        and np.all(observation[ACTIVE_CARRY_CHANNELS, 0, 0] == 0)
    )


def new_role_counters() -> dict[str, collections.Counter]:
    return {
        "farmer": collections.Counter(),
        "chopper": collections.Counter(),
    }


def record_decision(
    counters: collections.Counter,
    observation: np.ndarray,
    selected_action: int,
    teacher_action: int,
) -> None:
    selected_plane = selected_action // CELLS
    teacher_plane = teacher_action // CELLS
    selected_name = ACTION_NAMES[selected_plane]
    teacher_name = ACTION_NAMES[teacher_plane]
    counters["DECISIONS"] += 1
    counters[f"CHOSE_{selected_name}"] += 1
    counters[f"TEACHER_{teacher_name}"] += 1

    teacher_wait = is_move_current(observation, teacher_action)
    if not teacher_wait:
        counters["PRODUCTIVE_OPPORTUNITIES"] += 1
        counters[f"OPPORTUNITY_{teacher_name}"] += 1
        if selected_plane == teacher_plane:
            counters["PRODUCTIVE_VERB_CHOICES"] += 1
        if selected_action == teacher_action:
            counters["EXACT_PRODUCTIVE_CHOICES"] += 1

    if is_move_current(observation, selected_action):
        counters["SELECTED_CURRENT_WAITS"] += 1
        if is_justified_unripe_crop_wait(observation, selected_action):
            counters["JUSTIFIED_UNRIPE_CROP_WAITS"] += 1
        else:
            counters["UNJUSTIFIED_CURRENT_WAITS"] += 1

    if is_empty_seed_recovery_opportunity(observation):
        counters["EMPTY_SEED_RECOVERY_OPPORTUNITIES"] += 1
        if selected_plane == teacher_plane:
            counters["EMPTY_SEED_RECOVERY_VERB_CHOICES"] += 1
        if selected_action == teacher_action:
            counters["EMPTY_SEED_RECOVERY_EXACT_CHOICES"] += 1


def summarize_role(counter: collections.Counter) -> dict:
    opportunities = counter["PRODUCTIVE_OPPORTUNITIES"]
    exact = counter["EXACT_PRODUCTIVE_CHOICES"]
    verbs = counter["PRODUCTIVE_VERB_CHOICES"]
    recovery_opportunities = counter["EMPTY_SEED_RECOVERY_OPPORTUNITIES"]
    recovery_exact = counter["EMPTY_SEED_RECOVERY_EXACT_CHOICES"]
    recovery_verbs = counter["EMPTY_SEED_RECOVERY_VERB_CHOICES"]
    return {
        "decisions": counter["DECISIONS"],
        "productive_opportunities": opportunities,
        "exact_productive_choices": exact,
        "exact_productive_choice_rate": exact / opportunities if opportunities else None,
        "productive_verb_choices": verbs,
        "productive_verb_choice_rate": verbs / opportunities if opportunities else None,
        "selected_current_waits": counter["SELECTED_CURRENT_WAITS"],
        "justified_unripe_crop_waits": counter["JUSTIFIED_UNRIPE_CROP_WAITS"],
        "unjustified_current_waits": counter["UNJUSTIFIED_CURRENT_WAITS"],
        "empty_seed_recovery_opportunities": recovery_opportunities,
        "empty_seed_recovery_exact_choices": recovery_exact,
        "empty_seed_recovery_exact_choice_rate": (
            recovery_exact / recovery_opportunities
            if recovery_opportunities
            else None
        ),
        "empty_seed_recovery_verb_choices": recovery_verbs,
        "empty_seed_recovery_verb_choice_rate": (
            recovery_verbs / recovery_opportunities
            if recovery_opportunities
            else None
        ),
        "counts": dict(counter),
    }


def recipe_recovery_gate(by_recipe: dict | None, minimum_rate: float | None) -> bool:
    """Check exact recovery choices in every recipe with recovery opportunities."""
    if by_recipe is None or minimum_rate is None:
        return True
    summaries = [
        bucket["roles"]["farmer"]
        for bucket in by_recipe.values()
        if bucket["roles"]["farmer"]["empty_seed_recovery_opportunities"] > 0
    ]
    return all(
        summary["empty_seed_recovery_exact_choice_rate"] is not None
        and summary["empty_seed_recovery_exact_choice_rate"] >= minimum_rate
        for summary in summaries
    )


def d11_action_gate_thresholds() -> dict[str, float | int | None]:
    """Return the exact action gates frozen in the D11 learning protocol."""
    return {
        "minimum_role_rate": 0.55,
        "minimum_farmer_rate": 0.55,
        "minimum_chopper_rate": 0.90,
        "minimum_recipe_role_rate": None,
        "maximum_unjustified_waits": 3_000,
        "minimum_empty_seed_recovery_rate": 0.30,
        "minimum_empty_seed_recovery_verb_rate": 0.99,
        "minimum_recipe_empty_seed_recovery_rate": 0.10,
    }


def audit(
    checkpoint: Path,
    *,
    seed_base: int,
    episodes: int,
    num_envs: int,
    threads: int,
    max_turns: int = 240,
    curriculum_level: int = 3,
    gate_profile: str | None = None,
    minimum_role_rate: float | None = None,
    minimum_farmer_rate: float | None = None,
    minimum_chopper_rate: float | None = None,
    minimum_recipe_role_rate: float | None = None,
    maximum_unjustified_waits: int | None = None,
    minimum_empty_seed_recovery_rate: float | None = None,
    minimum_empty_seed_recovery_verb_rate: float | None = None,
    minimum_recipe_empty_seed_recovery_rate: float | None = None,
) -> dict:
    if curriculum_level not in (3, 4, 5):
        raise ValueError("action audit supports Curriculum Level 3, 4, or 5")
    if gate_profile not in (None, "d11"):
        raise ValueError(f"unknown action gate profile: {gate_profile}")
    if gate_profile == "d11":
        if curriculum_level != 5:
            raise ValueError("the d11 action gate profile requires Curriculum Level 5")
        explicit_thresholds = (
            minimum_role_rate,
            minimum_farmer_rate,
            minimum_chopper_rate,
            minimum_recipe_role_rate,
            maximum_unjustified_waits,
            minimum_empty_seed_recovery_rate,
            minimum_empty_seed_recovery_verb_rate,
            minimum_recipe_empty_seed_recovery_rate,
        )
        if any(value is not None for value in explicit_thresholds):
            raise ValueError("the d11 profile cannot be combined with explicit thresholds")
        thresholds = d11_action_gate_thresholds()
        minimum_role_rate = float(thresholds["minimum_role_rate"])
        minimum_farmer_rate = float(thresholds["minimum_farmer_rate"])
        minimum_chopper_rate = float(thresholds["minimum_chopper_rate"])
        minimum_recipe_role_rate = None
        maximum_unjustified_waits = int(thresholds["maximum_unjustified_waits"])
        minimum_empty_seed_recovery_rate = float(
            thresholds["minimum_empty_seed_recovery_rate"]
        )
        minimum_empty_seed_recovery_verb_rate = float(
            thresholds["minimum_empty_seed_recovery_verb_rate"]
        )
        minimum_recipe_empty_seed_recovery_rate = float(
            thresholds["minimum_recipe_empty_seed_recovery_rate"]
        )
    else:
        if minimum_role_rate is None:
            minimum_role_rate = 0.60 if curriculum_level == 3 else 0.55
        if minimum_farmer_rate is None:
            minimum_farmer_rate = minimum_role_rate
        if minimum_chopper_rate is None:
            minimum_chopper_rate = minimum_role_rate
        if minimum_recipe_role_rate is None and curriculum_level in (4, 5):
            minimum_recipe_role_rate = 0.35
        if maximum_unjustified_waits is None:
            maximum_unjustified_waits = (
                20_000 if curriculum_level == 3 else 30_000
            )
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(min(4, threads))
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"])
    model.eval()
    target_stop = seed_base + episodes
    slot_counters = [new_role_counters() for _ in range(num_envs)]
    totals = new_role_counters()
    recipe_totals = (
        [new_role_counters() for _ in LEVEL2_TARGETS]
        if curriculum_level in (4, 5)
        else None
    )
    completed: dict[int, dict] = {}

    env_class = {
        3: Level3VecEnv,
        4: Level4VecEnv,
        5: Level5CropFirstRepeatedPressureReacquire180VecEnv,
    }[curriculum_level]
    with env_class(num_envs, seed_base, max_turns=max_turns) as env:
        while len(completed) < episodes:
            observations = env.obs.copy()
            teacher_actions = env.teacher_actions().astype(np.int64)
            with torch.inference_mode():
                actions, _, _, _ = model.action_and_value(
                    torch.from_numpy(env.obs),
                    torch.from_numpy(env.masks),
                    deterministic=True,
                )
            actions_np = actions.numpy()
            for index, selected_action in enumerate(actions_np):
                role = role_name(observations[index])
                if role is not None:
                    record_decision(
                        slot_counters[index][role],
                        observations[index],
                        int(selected_action),
                        int(teacher_actions[index]),
                    )
            _, _, _, info = env.step(actions_np.astype(np.int32, copy=False))
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if seed_base <= seed < target_stop:
                    role_summaries = {
                        role: summarize_role(slot_counters[index][role])
                        for role in ("farmer", "chopper")
                    }
                    completed[seed] = {
                        "seed": seed,
                        "success": bool(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "height": int(info.heights[index]),
                        "initial_total_deficit": int(
                            info.initial_total_deficits[index]
                        ),
                        "training_turn": int(info.training_turns[index]),
                        "score_gain": int(info.score_gains[index]),
                        "renewable_harvests": int(info.renewable_harvests[index]),
                        "created_crop": bool(info.created_crops[index]),
                        "roles": role_summaries,
                    }
                    if curriculum_level in (4, 5):
                        recipe_id = int(info.recipe_ids[index])
                        completed[seed].update(
                            {
                                "recipe_id": recipe_id,
                                "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                                "target": [
                                    int(value) for value in info.targets[index]
                                ],
                            }
                        )
                    for role in ("farmer", "chopper"):
                        totals[role].update(slot_counters[index][role])
                        if recipe_totals is not None:
                            recipe_totals[recipe_id][role].update(
                                slot_counters[index][role]
                            )
                slot_counters[index] = new_role_counters()

    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    successful = [row for row in rows if row["success"]]
    nontrivial = [row for row in rows if row["initial_total_deficit"] > 0]
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        successes = sum(row["success"] for row in bucket)
        by_height[str(height)] = {
            "episodes": len(bucket),
            "successes": successes,
            "success_rate": successes / len(bucket),
        }
    role_summary = {
        role: summarize_role(totals[role]) for role in ("farmer", "chopper")
    }
    by_recipe = None
    if recipe_totals is not None:
        by_recipe = {}
        for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
            bucket = [row for row in rows if row["recipe_id"] == recipe_id]
            successes = sum(row["success"] for row in bucket)
            by_recipe[str(recipe_id)] = {
                "name": name,
                "target": list(LEVEL2_TARGETS[recipe_id]),
                "episodes": len(bucket),
                "successes": successes,
                "success_rate": successes / len(bucket) if bucket else None,
                "roles": {
                    role: summarize_role(recipe_totals[recipe_id][role])
                    for role in ("farmer", "chopper")
                },
            }
    unjustified_waits = sum(
        role_summary[role]["unjustified_current_waits"]
        for role in ("farmer", "chopper")
    )
    minimum_rates = {
        "farmer": minimum_farmer_rate,
        "chopper": minimum_chopper_rate,
    }
    action_gate = (
        all(
            role_summary[role]["exact_productive_choice_rate"] is not None
            and role_summary[role]["exact_productive_choice_rate"]
            >= minimum_rates[role]
            for role in ("farmer", "chopper")
        )
        and (
            by_recipe is None
            or minimum_recipe_role_rate is None
            or all(
                bucket["roles"][role]["exact_productive_choice_rate"] is not None
                and bucket["roles"][role]["exact_productive_choice_rate"]
                >= minimum_recipe_role_rate
                for bucket in by_recipe.values()
                if bucket["episodes"]
                for role in ("farmer", "chopper")
            )
        )
        and unjustified_waits <= maximum_unjustified_waits
        and (
            curriculum_level != 5
            or minimum_empty_seed_recovery_rate is None
            or (
                role_summary["farmer"]["empty_seed_recovery_exact_choice_rate"]
                is not None
                and role_summary["farmer"]["empty_seed_recovery_exact_choice_rate"]
                >= minimum_empty_seed_recovery_rate
            )
        )
        and (
            curriculum_level != 5
            or minimum_empty_seed_recovery_verb_rate is None
            or (
                role_summary["farmer"]["empty_seed_recovery_verb_choice_rate"]
                is not None
                and role_summary["farmer"]["empty_seed_recovery_verb_choice_rate"]
                >= minimum_empty_seed_recovery_verb_rate
            )
        )
        and (
            curriculum_level != 5
            or recipe_recovery_gate(
                by_recipe, minimum_recipe_empty_seed_recovery_rate
            )
        )
    )
    return {
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256(checkpoint),
        "curriculum_level": curriculum_level,
        "gate_profile": gate_profile,
        "target": list(LEVEL3_TARGET) if curriculum_level == 3 else None,
        "recipe_catalog": (
            [list(target) for target in LEVEL2_TARGETS]
            if curriculum_level in (4, 5)
            else None
        ),
        "required_score_gain": LEVEL3_SCORE_GAIN,
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
        "nontrivial_episodes": len(nontrivial),
        "nontrivial_successes": sum(row["success"] for row in nontrivial),
        "nontrivial_success_rate": (
            sum(row["success"] for row in nontrivial) / len(nontrivial)
            if nontrivial
            else None
        ),
        "created_crop_rate": sum(row["created_crop"] for row in rows) / len(rows),
        "renewable_harvest_rate": sum(
            row["renewable_harvests"] > 0 for row in rows
        )
        / len(rows),
        "median_training_turn": float(
            np.median([row["training_turn"] for row in rows if row["training_turn"]])
        ),
        "median_score_gain": float(np.median([row["score_gain"] for row in rows])),
        "by_height": by_height,
        "by_recipe": by_recipe,
        "roles": role_summary,
        "unjustified_current_waits": unjustified_waits,
        "action_gate": action_gate,
        "action_gate_definition": {
            "productive_opportunity": (
                "a post-training role decision whose deterministic teacher command is not "
                "MOVE to the selected unit's current cell"
            ),
            "productive_choice": "the learned action exactly equals that teacher command",
            "wait_exemption": (
                "farmer MOVE-current while standing on the tracked unripe BANANA crop"
            ),
            "minimum_exact_productive_rate_per_role": minimum_role_rate,
            "minimum_exact_productive_rate_by_role": minimum_rates,
            "minimum_exact_productive_rate_per_recipe_role": (
                minimum_recipe_role_rate
            ),
            "maximum_unjustified_current_waits": maximum_unjustified_waits,
            "empty_seed_recovery_opportunity": (
                "post-training farmer with no crop, no carried inventory, and no home banana"
            ),
            "minimum_empty_seed_recovery_exact_choice_rate": (
                minimum_empty_seed_recovery_rate
            ),
            "minimum_empty_seed_recovery_verb_choice_rate": (
                minimum_empty_seed_recovery_verb_rate
            ),
            "minimum_empty_seed_recovery_exact_choice_rate_per_nonempty_recipe": (
                minimum_recipe_empty_seed_recovery_rate
            ),
        },
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--seed-base", type=int, default=2_011_000)
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--max-turns", type=int, default=240)
    parser.add_argument("--curriculum-level", type=int, choices=(3, 4, 5), default=3)
    parser.add_argument("--gate-profile", choices=("d11",))
    parser.add_argument("--minimum-role-rate", type=float)
    parser.add_argument("--minimum-farmer-rate", type=float)
    parser.add_argument("--minimum-chopper-rate", type=float)
    parser.add_argument("--minimum-recipe-role-rate", type=float)
    parser.add_argument("--maximum-unjustified-waits", type=int)
    parser.add_argument("--minimum-empty-seed-recovery-rate", type=float)
    parser.add_argument("--minimum-empty-seed-recovery-verb-rate", type=float)
    parser.add_argument("--minimum-recipe-empty-seed-recovery-rate", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(
        args.checkpoint,
        seed_base=args.seed_base,
        episodes=args.episodes,
        num_envs=args.num_envs,
        threads=args.threads,
        max_turns=args.max_turns,
        curriculum_level=args.curriculum_level,
        gate_profile=args.gate_profile,
        minimum_role_rate=args.minimum_role_rate,
        minimum_farmer_rate=args.minimum_farmer_rate,
        minimum_chopper_rate=args.minimum_chopper_rate,
        minimum_recipe_role_rate=args.minimum_recipe_role_rate,
        maximum_unjustified_waits=args.maximum_unjustified_waits,
        minimum_empty_seed_recovery_rate=args.minimum_empty_seed_recovery_rate,
        minimum_empty_seed_recovery_verb_rate=(
            args.minimum_empty_seed_recovery_verb_rate
        ),
        minimum_recipe_empty_seed_recovery_rate=(
            args.minimum_recipe_empty_seed_recovery_rate
        ),
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "episodes_detail"},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
