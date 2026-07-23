#!/usr/bin/env python3
"""Generate deterministic capped two-intervention q6 Monte-Carlo episodes."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import time

import numpy as np

from cgauto.rl_macro_env import OPPONENTS
from cgauto.rl_q6_proposal_env import Q6ProposalVecEnv


MASK64 = (1 << 64) - 1
OPPONENTS_PER_SEAT = len(OPPONENTS)
TASKS_PER_MAP = 2 * OPPONENTS_PER_SEAT
MAX_SCHEDULE = 7

FIELDS = (
    "task_index",
    "scenario",
    "replica",
    "mode",
    "scheduled_first_boundary",
    "scheduled_second_boundary",
    "observed_boundaries",
    "first_selected_boundary",
    "first_selected_slot",
    "second_selected_boundary",
    "second_selected_slot",
    "selection_hash",
    "map_seed",
    "seat",
    "opponent",
    "own_score",
    "opponent_score",
    "margin",
    "baseline_own_score",
    "baseline_opponent_score",
    "baseline_margin",
    "margin_delta",
    "own_workers",
    "successful_trains",
    "intervention_batches",
    "boundary_decisions",
    "joint_batches",
    "noncontrol_assignments",
    "own_created_crops",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "invalidated_jobs",
    "action_hash",
    "state_hash",
)


def splitmix64(value: int) -> int:
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def trailing_schedule(value: int) -> int:
    if value == 0:
        return MAX_SCHEDULE
    return min((value & -value).bit_length() - 1, MAX_SCHEDULE)


def episode_spec(
    task_index: int,
    pool_tasks: int,
    single_replicas: int,
) -> dict:
    if task_index < 0 or pool_tasks <= 0 or single_replicas < 0:
        raise ValueError("invalid D144 episode coordinates")
    replica, scenario = divmod(task_index, pool_tasks)
    if replica == 0:
        mode = "control"
    elif replica <= single_replicas:
        mode = "single"
    else:
        mode = "double"
    first_bits = splitmix64(task_index ^ 0xD144A001)
    gap_bits = splitmix64(task_index ^ 0xD144A002)
    first = trailing_schedule(first_bits)
    gap = 1 + trailing_schedule(gap_bits)
    return {
        "replica": replica,
        "scenario": scenario,
        "mode": mode,
        "first": first,
        "second": first + gap,
    }


def selected_action(
    task_index: int,
    boundary: int,
    interventions: int,
    mask: np.ndarray,
    pool_tasks: int,
    single_replicas: int,
) -> int:
    live = np.flatnonzero(mask[1:]) + 1
    if len(live) == 0:
        return 0
    spec = episode_spec(task_index, pool_tasks, single_replicas)
    if spec["mode"] == "control" or interventions >= 2:
        return 0
    target = spec["first"] if interventions == 0 else spec["second"]
    if boundary != target:
        return 0
    if spec["mode"] == "single" and interventions == 1:
        return 0
    bits = splitmix64(
        task_index
        ^ (boundary * 0x9E3779B1)
        ^ (interventions * 0x85EBCA77)
        ^ 0xD144A003
    )
    return int(live[bits % len(live)])


def expected_task(start_seed: int, scenario: int) -> tuple[int, int, str]:
    map_offset, within = divmod(scenario, TASKS_PER_MAP)
    seat, opponent = divmod(within, OPPONENTS_PER_SEAT)
    return start_seed + map_offset, seat, OPPONENTS[opponent]


def update_selection_hash(current: int, boundary: int, action: int) -> int:
    payload = current.to_bytes(8, "little")
    payload += int(boundary).to_bytes(2, "little")
    payload += int(action).to_bytes(2, "little")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def generate(
    start_seed: int,
    maps: int,
    replicas: int,
    single_replicas: int,
    output: Path,
) -> dict:
    if start_seed == 0 or maps <= 0 or replicas < 3:
        raise ValueError("D144 requires nonzero seeds, maps, and at least three replicas")
    if not 0 < single_replicas < replicas - 1:
        raise ValueError("D144 single replicas must leave control and double modes")
    if output.exists():
        raise FileExistsError(output)
    pool_tasks = maps * TASKS_PER_MAP
    target_episodes = pool_tasks * replicas
    num_envs = pool_tasks
    boundaries = np.zeros(num_envs, dtype=np.int32)
    interventions = np.zeros(num_envs, dtype=np.int8)
    first_boundary = np.full(num_envs, -1, dtype=np.int32)
    first_slot = np.full(num_envs, -1, dtype=np.int32)
    second_boundary = np.full(num_envs, -1, dtype=np.int32)
    second_slot = np.full(num_envs, -1, dtype=np.int32)
    selection_hash = np.zeros(num_envs, dtype=np.uint64)
    rows = []
    steps = 0
    started = time.perf_counter()
    with Q6ProposalVecEnv(num_envs, start_seed, map_pool=maps) as env:
        while len(rows) < target_episodes:
            task_before = env.task_indices.copy()
            actions = np.zeros(num_envs, dtype=np.int32)
            decision = env.masks.sum(axis=1) > 1
            for slot in np.flatnonzero(decision):
                task_index = int(task_before[slot])
                if task_index >= target_episodes:
                    continue
                action = selected_action(
                    task_index,
                    int(boundaries[slot]),
                    int(interventions[slot]),
                    env.masks[slot],
                    pool_tasks,
                    single_replicas,
                )
                actions[slot] = action
                if action > 0:
                    if interventions[slot] == 0:
                        first_boundary[slot] = boundaries[slot]
                        first_slot[slot] = action
                    elif interventions[slot] == 1:
                        second_boundary[slot] = boundaries[slot]
                        second_slot[slot] = action
                    else:
                        raise RuntimeError("D144 exceeded two local interventions")
                    interventions[slot] += 1
                    selection_hash[slot] = update_selection_hash(
                        int(selection_hash[slot]), int(boundaries[slot]), action
                    )
                boundaries[slot] += 1
            _, _, _, _, info = env.step(actions)
            steps += 1
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                task_index = int(task_before[slot])
                if terminal["task_index"] != task_index:
                    raise RuntimeError("D144 task index drift")
                if terminal["intervention_batches"] != int(interventions[slot]):
                    raise RuntimeError("D144 intervention counter drift")
                if task_index < target_episodes:
                    spec = episode_spec(task_index, pool_tasks, single_replicas)
                    expected = expected_task(start_seed, spec["scenario"])
                    actual = (
                        terminal["map_seed"],
                        terminal["seat"],
                        terminal["opponent"],
                    )
                    if actual != expected:
                        raise RuntimeError(
                            f"D144 scenario mapping drift: {actual!r} != {expected!r}"
                        )
                    rows.append(
                        {
                            "task_index": task_index,
                            "scenario": spec["scenario"],
                            "replica": spec["replica"],
                            "mode": spec["mode"],
                            "scheduled_first_boundary": spec["first"],
                            "scheduled_second_boundary": spec["second"],
                            "observed_boundaries": int(boundaries[slot]),
                            "first_selected_boundary": int(first_boundary[slot]),
                            "first_selected_slot": int(first_slot[slot]),
                            "second_selected_boundary": int(second_boundary[slot]),
                            "second_selected_slot": int(second_slot[slot]),
                            "selection_hash": int(selection_hash[slot]),
                            **terminal,
                        }
                    )
                boundaries[slot] = 0
                interventions[slot] = 0
                first_boundary[slot] = -1
                first_slot[slot] = -1
                second_boundary[slot] = -1
                second_slot[slot] = -1
                selection_hash[slot] = 0
    rows.sort(key=lambda row: int(row["task_index"]))
    if [int(row["task_index"]) for row in rows] != list(range(target_episodes)):
        raise RuntimeError("D144 episode matrix is incomplete")
    if any(int(row["intervention_batches"]) > 2 for row in rows):
        raise RuntimeError("D144 terminal exceeded its intervention cap")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    elapsed = time.perf_counter() - started
    return {
        "path": str(output),
        "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "start_seed": start_seed,
        "maps": maps,
        "pool_tasks": pool_tasks,
        "replicas": replicas,
        "single_replicas": single_replicas,
        "episodes": len(rows),
        "steps": steps,
        "elapsed_seconds": elapsed,
        "episodes_per_second": len(rows) / elapsed,
        "zero_intervention": sum(
            int(row["intervention_batches"]) == 0 for row in rows
        ),
        "one_intervention": sum(
            int(row["intervention_batches"]) == 1 for row in rows
        ),
        "two_interventions": sum(
            int(row["intervention_batches"]) == 2 for row in rows
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("start_seed", type=int)
    parser.add_argument("maps", type=int)
    parser.add_argument("replicas", type=int)
    parser.add_argument("single_replicas", type=int)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = generate(
        args.start_seed,
        args.maps,
        args.replicas,
        args.single_replicas,
        args.output,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
