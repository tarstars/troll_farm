#!/usr/bin/env python3
"""Replay selected first actions and branch every legal conditional second action."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from cgauto import run_d144a_two_intervention_mc_pilot as d144
from cgauto.rl_q6_proposal_env import (
    Q6_ACTION_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
)


PLAN_FIELDS = (
    "scenario",
    "map_seed",
    "seat",
    "opponent",
    "source_replica",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "selected_second_slot",
    "target_active",
    "legal_second_slots",
    "second_feature_sha256",
)
TERMINAL_FIELDS = d144.FIELDS[12:]
OUTPUT_FIELDS = (
    "scenario",
    "branch_ordinal",
    "source_replica",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "second_slot",
    "selected_second_slot",
    "target_active",
    "selection_hash",
) + TERMINAL_FIELDS


def feature(value) -> str:
    return f"{float(value):.9f}"


def conditional_feature_hash(
    state: list[str], actions: list[tuple[int, list[str]]]
) -> str:
    if len(state) != Q6_STATE_FEATURES:
        raise ValueError("D151 state feature width drift")
    if any(len(values) != Q6_ACTION_FEATURES for _, values in actions):
        raise ValueError("D151 action feature width drift")
    slots = [slot for slot, _ in actions]
    if slots != sorted(set(slots)) or not slots or slots[0] != 0:
        raise ValueError("D151 legal slot ordering drift")
    digest = hashlib.sha256()
    for token in ["d151-conditional-feature-v1", *state]:
        digest.update(str(token).encode("ascii"))
        digest.update(b"\0")
    for slot, values in actions:
        digest.update(str(slot).encode("ascii"))
        digest.update(b"\0")
        for value in values:
            digest.update(str(value).encode("ascii"))
            digest.update(b"\0")
    return digest.hexdigest()


def parse_slots(value: str) -> tuple[int, ...]:
    slots = tuple(int(item) for item in value.split(",") if item)
    if slots != tuple(sorted(set(slots))) or not slots or slots[0] != 0:
        raise RuntimeError("D151 plan legal slots are invalid")
    return slots


def load_plan(path: Path, start_seed: int, maps: int) -> dict:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(PLAN_FIELDS):
            raise RuntimeError("D151 plan schema drift")
        rows = [
            row
            for row in reader
            if start_seed <= int(row["map_seed"]) < start_seed + maps
        ]
    by_task = {
        (int(row["map_seed"]), int(row["seat"]), str(row["opponent"])): {
            **row,
            "slots": parse_slots(row["legal_second_slots"]),
        }
        for row in rows
    }
    if len(by_task) != len(rows):
        raise RuntimeError("D151 duplicate plan task")
    return by_task


def env_feature_hash(env: Q6ProposalVecEnv, slot: int, legal: tuple[int, ...]) -> str:
    state = [feature(value) for value in env.state_features[slot]]
    actions = [
        (
            action,
            [feature(value) for value in env.action_features[slot, action]],
        )
        for action in legal
    ]
    return conditional_feature_hash(state, actions)


def write_rows(path: Path, rows: list[dict]) -> None:
    if path.exists():
        raise FileExistsError(path)
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def collect(start_seed: int, maps: int, plan_path: Path, output: Path) -> dict:
    if start_seed == 0 or maps <= 0:
        raise ValueError("D151 requires nonzero seeds and maps")
    plan = load_plan(plan_path, start_seed, maps)
    pool_tasks = maps * d144.TASKS_PER_MAP
    branches = max((len(row["slots"]) for row in plan.values()), default=0)
    if not branches:
        raise RuntimeError("D151 shard has no planned branches")
    target_episodes = pool_tasks * branches
    boundaries = np.zeros(pool_tasks, dtype=np.int32)
    completed = 0
    verified = set()
    rows = []
    steps = 0
    started = time.perf_counter()
    with Q6ProposalVecEnv(pool_tasks, start_seed, map_pool=maps) as env:
        while completed < target_episodes:
            task_before = env.task_indices.copy()
            actions = np.zeros(pool_tasks, dtype=np.int32)
            decisions = env.masks.sum(axis=1) > 1
            for env_slot in np.flatnonzero(decisions):
                task_index = int(task_before[env_slot])
                if task_index >= target_episodes:
                    continue
                branch, scenario = divmod(task_index, pool_tasks)
                task = d144.expected_task(start_seed, scenario)
                spec = plan.get(task)
                if spec is not None and branch < len(spec["slots"]):
                    boundary = int(boundaries[env_slot])
                    action = 0
                    if boundary == int(spec["first_boundary"]):
                        action = int(spec["first_slot"])
                    elif boundary == int(spec["second_boundary"]):
                        legal = spec["slots"]
                        actual_legal = tuple(int(value) for value in np.flatnonzero(env.masks[env_slot]))
                        if actual_legal != legal:
                            raise RuntimeError(
                                f"D151 conditional legal slots drift: {task!r}"
                            )
                        if task not in verified:
                            actual_hash = env_feature_hash(env, env_slot, legal)
                            if actual_hash != spec["second_feature_sha256"]:
                                raise RuntimeError(
                                    f"D151 conditional feature hash drift: {task!r}"
                                )
                            verified.add(task)
                        action = int(legal[branch])
                    if env.masks[env_slot, action] != 1:
                        raise RuntimeError(
                            f"D151 selected masked action: {task!r}:{boundary}:{action}"
                        )
                    actions[env_slot] = action
                boundaries[env_slot] += 1
            _, _, _, _, info = env.step(actions)
            steps += 1
            for env_slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                task_index = int(task_before[env_slot])
                if task_index < target_episodes:
                    completed += 1
                    branch, scenario = divmod(task_index, pool_tasks)
                    task = d144.expected_task(start_seed, scenario)
                    spec = plan.get(task)
                    if spec is not None and branch < len(spec["slots"]):
                        second_slot = int(spec["slots"][branch])
                        expected_interventions = 1 + int(second_slot != 0)
                        actual_task = (
                            int(terminal["map_seed"]),
                            int(terminal["seat"]),
                            str(terminal["opponent"]),
                        )
                        if actual_task != task:
                            raise RuntimeError("D151 terminal task mapping drift")
                        if int(terminal["intervention_batches"]) != expected_interventions:
                            raise RuntimeError("D151 terminal intervention-count drift")
                        selection_hash = d144.update_selection_hash(
                            0,
                            int(spec["first_boundary"]),
                            int(spec["first_slot"]),
                        )
                        if second_slot:
                            selection_hash = d144.update_selection_hash(
                                selection_hash,
                                int(spec["second_boundary"]),
                                second_slot,
                            )
                        rows.append(
                            {
                                "scenario": int(spec["scenario"]),
                                "map_seed": task[0],
                                "seat": task[1],
                                "opponent": task[2],
                                "branch_ordinal": branch,
                                "source_replica": int(spec["source_replica"]),
                                "first_boundary": int(spec["first_boundary"]),
                                "first_slot": int(spec["first_slot"]),
                                "second_boundary": int(spec["second_boundary"]),
                                "second_slot": second_slot,
                                "selected_second_slot": int(
                                    spec["selected_second_slot"]
                                ),
                                "target_active": int(spec["target_active"]),
                                "selection_hash": selection_hash,
                                **{
                                    field: terminal[field]
                                    for field in TERMINAL_FIELDS
                                },
                            }
                        )
                boundaries[env_slot] = 0
    rows.sort(
        key=lambda row: (
            int(row["scenario"]),
            int(row["branch_ordinal"]),
        )
    )
    expected_rows = sum(len(row["slots"]) for row in plan.values())
    if len(rows) != expected_rows or len(verified) != len(plan):
        raise RuntimeError("D151 branch or feature-verification matrix incomplete")
    write_rows(output, rows)
    elapsed = time.perf_counter() - started
    return {
        "start_seed": start_seed,
        "maps": maps,
        "pool_tasks": pool_tasks,
        "planned_tasks": len(plan),
        "maximum_branches": branches,
        "simulated_episodes": target_episodes,
        "rows": len(rows),
        "feature_hashes_verified": len(verified),
        "steps": steps,
        "elapsed_seconds": elapsed,
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("start_seed", type=int)
    parser.add_argument("maps", type=int)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(collect(args.start_seed, args.maps, args.plan, args.output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
