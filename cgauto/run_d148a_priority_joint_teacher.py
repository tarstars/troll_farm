#!/usr/bin/env python3
"""Collect a compact two-pass, 64-priority joint q6 trajectory teacher."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from functools import lru_cache
import hashlib
from pathlib import Path
import time

import numpy as np

from cgauto.collect_d147a_selected_trajectory_features import (
    ACTION_FIELDS,
    STATE_FIELDS,
    TERMINAL_FIELDS,
    decision_stage,
    feature,
)
from cgauto.rl_q6_proposal_env import Q6ProposalVecEnv
from cgauto.run_d144a_two_intervention_mc_pilot import (
    TASKS_PER_MAP,
    episode_spec,
    expected_task,
    selected_action,
    update_selection_hash,
)


SOURCE_FIRST_REPLICA = 17
SOURCE_LAST_REPLICA = 127
DEFAULT_SEARCH_BUDGET = 64

POPULATION_FIELDS = (
    "task_index",
    "scenario",
    "search_ordinal",
    "source_replica",
    "mode",
    "scheduled_first_boundary",
    "scheduled_second_boundary",
    "observed_boundaries",
    "first_selected_boundary",
    "first_selected_slot",
    "second_selected_boundary",
    "second_selected_slot",
    "selection_hash",
) + TERMINAL_FIELDS
MANIFEST_FIELDS = (
    "scenario",
    "map_seed",
    "seat",
    "opponent",
    "search_ordinal",
    "source_replica",
    "scheduled_first_boundary",
    "scheduled_second_boundary",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "second_slot",
    "selection_hash",
    "control_margin",
    "sequence_margin",
    "sequence_gain_over_control",
)
CANDIDATE_FIELDS = (
    "scenario",
    "map_seed",
    "seat",
    "opponent",
    "source_replica",
    "boundary",
    "stage",
    "chosen_slot",
    "candidate_slot",
    "chosen",
    "legal_candidates",
) + STATE_FIELDS + ACTION_FIELDS
REPLAY_FIELDS = MANIFEST_FIELDS + TERMINAL_FIELDS


def schedule_class_key(first: int, second: int) -> tuple[int, int, int]:
    gap = second - first
    if first == 0 and gap == 1:
        schedule_class = 0
    elif first == 0:
        schedule_class = 1
    elif gap == 1:
        schedule_class = 2
    else:
        schedule_class = 3
    return schedule_class, first, gap


@lru_cache(maxsize=None)
def priority_source_replicas(
    scenario: int, pool_tasks: int, budget: int = DEFAULT_SEARCH_BUDGET
) -> tuple[int, ...]:
    if not 0 <= scenario < pool_tasks:
        raise ValueError("D148 scenario is outside its pool")
    available = SOURCE_LAST_REPLICA - SOURCE_FIRST_REPLICA + 1
    if not 1 <= budget <= available:
        raise ValueError("D148 search budget is outside source population")
    ranked = []
    for replica in range(SOURCE_FIRST_REPLICA, SOURCE_LAST_REPLICA + 1):
        spec = episode_spec(replica * pool_tasks + scenario, pool_tasks, 16)
        ranked.append(
            (
                schedule_class_key(int(spec["first"]), int(spec["second"])),
                replica,
            )
        )
    ranked.sort(key=lambda item: (*item[0], item[1]))
    return tuple(replica for _, replica in ranked[:budget])


def runtime_spec(
    task_index: int, pool_tasks: int, budget: int
) -> dict[str, int | str]:
    ordinal, scenario = divmod(task_index, pool_tasks)
    if ordinal == 0:
        return {
            "scenario": scenario,
            "search_ordinal": ordinal,
            "source_replica": 0,
            "mode": "control",
            "first": -1,
            "second": -1,
            "source_task_index": scenario,
        }
    replicas = priority_source_replicas(scenario, pool_tasks, budget)
    if ordinal > len(replicas):
        raise ValueError("D148 runtime ordinal exceeds search budget")
    replica = replicas[ordinal - 1]
    source_task_index = replica * pool_tasks + scenario
    source = episode_spec(source_task_index, pool_tasks, 16)
    return {
        "scenario": scenario,
        "search_ordinal": ordinal,
        "source_replica": replica,
        "mode": "double",
        "first": int(source["first"]),
        "second": int(source["second"]),
        "source_task_index": source_task_index,
    }


def write_table(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outcome_key(row: dict, control: dict) -> tuple[int, int, int, int]:
    return (
        int(row["margin"]) - int(control["margin"]),
        int(row["own_score"]) - int(control["own_score"]),
        -(int(row["opponent_score"]) - int(control["opponent_score"])),
        -int(row["source_replica"]),
    )


def collect_population(
    start_seed: int, maps: int, budget: int
) -> tuple[list[dict], float, int]:
    pool_tasks = maps * TASKS_PER_MAP
    target_episodes = pool_tasks * (budget + 1)
    boundaries = np.zeros(pool_tasks, dtype=np.int32)
    interventions = np.zeros(pool_tasks, dtype=np.int8)
    first_boundary = np.full(pool_tasks, -1, dtype=np.int32)
    first_slot = np.full(pool_tasks, -1, dtype=np.int32)
    second_boundary = np.full(pool_tasks, -1, dtype=np.int32)
    second_slot = np.full(pool_tasks, -1, dtype=np.int32)
    selection_hash = np.zeros(pool_tasks, dtype=np.uint64)
    rows = []
    steps = 0
    started = time.perf_counter()
    with Q6ProposalVecEnv(pool_tasks, start_seed, map_pool=maps) as env:
        while len(rows) < target_episodes:
            task_before = env.task_indices.copy()
            actions = np.zeros(pool_tasks, dtype=np.int32)
            decisions = env.masks.sum(axis=1) > 1
            for slot in np.flatnonzero(decisions):
                task_index = int(task_before[slot])
                if task_index >= target_episodes:
                    continue
                spec = runtime_spec(task_index, pool_tasks, budget)
                action = 0
                if spec["mode"] == "double":
                    action = selected_action(
                        int(spec["source_task_index"]),
                        int(boundaries[slot]),
                        int(interventions[slot]),
                        env.masks[slot],
                        pool_tasks,
                        16,
                    )
                actions[slot] = action
                if action:
                    if interventions[slot] == 0:
                        first_boundary[slot] = boundaries[slot]
                        first_slot[slot] = action
                    elif interventions[slot] == 1:
                        second_boundary[slot] = boundaries[slot]
                        second_slot[slot] = action
                    else:
                        raise RuntimeError("D148 exceeded two interventions")
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
                if task_index < target_episodes:
                    spec = runtime_spec(task_index, pool_tasks, budget)
                    expected = expected_task(start_seed, int(spec["scenario"]))
                    actual = (
                        terminal["map_seed"],
                        terminal["seat"],
                        terminal["opponent"],
                    )
                    if actual != expected:
                        raise RuntimeError("D148 population scenario mapping drift")
                    if terminal["intervention_batches"] != int(interventions[slot]):
                        raise RuntimeError("D148 population intervention count drift")
                    rows.append(
                        {
                            "task_index": task_index,
                            "scenario": int(spec["scenario"]),
                            "search_ordinal": int(spec["search_ordinal"]),
                            "source_replica": int(spec["source_replica"]),
                            "mode": str(spec["mode"]),
                            "scheduled_first_boundary": int(spec["first"]),
                            "scheduled_second_boundary": int(spec["second"]),
                            "observed_boundaries": int(boundaries[slot]),
                            "first_selected_boundary": int(first_boundary[slot]),
                            "first_selected_slot": int(first_slot[slot]),
                            "second_selected_boundary": int(second_boundary[slot]),
                            "second_selected_slot": int(second_slot[slot]),
                            "selection_hash": int(selection_hash[slot]),
                            **{field: terminal[field] for field in TERMINAL_FIELDS},
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
        raise RuntimeError("D148 population matrix incomplete")
    return rows, time.perf_counter() - started, steps


def select_manifest(rows: list[dict], pool_tasks: int) -> list[dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[int(row["scenario"])].append(row)
    manifest = []
    for scenario in range(pool_tasks):
        scenario_rows = grouped[scenario]
        controls = [row for row in scenario_rows if row["mode"] == "control"]
        doubles = [
            row
            for row in scenario_rows
            if row["mode"] == "double" and int(row["intervention_batches"]) == 2
        ]
        if len(controls) != 1:
            raise RuntimeError("D148 control multiplicity drift")
        if not doubles:
            continue
        control = controls[0]
        selected = max(doubles, key=lambda row: outcome_key(row, control))
        manifest.append(
            {
                "scenario": scenario,
                "map_seed": int(selected["map_seed"]),
                "seat": int(selected["seat"]),
                "opponent": str(selected["opponent"]),
                "search_ordinal": int(selected["search_ordinal"]),
                "source_replica": int(selected["source_replica"]),
                "scheduled_first_boundary": int(selected["scheduled_first_boundary"]),
                "scheduled_second_boundary": int(selected["scheduled_second_boundary"]),
                "first_boundary": int(selected["first_selected_boundary"]),
                "first_slot": int(selected["first_selected_slot"]),
                "second_boundary": int(selected["second_selected_boundary"]),
                "second_slot": int(selected["second_selected_slot"]),
                "selection_hash": int(selected["selection_hash"]),
                "control_margin": int(control["margin"]),
                "sequence_margin": int(selected["margin"]),
                "sequence_gain_over_control": int(selected["margin"])
                - int(control["margin"]),
            }
        )
    return manifest


def replay_manifest(
    start_seed: int,
    maps: int,
    manifest: list[dict],
    population: list[dict],
) -> tuple[list[dict], list[dict], float, int]:
    pool_tasks = maps * TASKS_PER_MAP
    selected_by_scenario = {int(row["scenario"]): row for row in manifest}
    population_by_key = {
        (int(row["scenario"]), int(row["source_replica"])): row
        for row in population
    }
    boundaries = np.zeros(pool_tasks, dtype=np.int32)
    completed = set()
    candidates = []
    replays = []
    steps = 0
    started = time.perf_counter()
    with Q6ProposalVecEnv(pool_tasks, start_seed, map_pool=maps) as env:
        while len(completed) < pool_tasks:
            task_before = env.task_indices.copy()
            actions = np.zeros(pool_tasks, dtype=np.int32)
            decisions = env.masks.sum(axis=1) > 1
            for slot in np.flatnonzero(decisions):
                scenario = int(task_before[slot])
                if scenario >= pool_tasks:
                    continue
                selected = selected_by_scenario.get(scenario)
                if selected is None:
                    boundaries[slot] += 1
                    continue
                boundary = int(boundaries[slot])
                first = int(selected["first_boundary"])
                second = int(selected["second_boundary"])
                stage = decision_stage(boundary, first, second)
                action = 0
                if boundary == first:
                    action = int(selected["first_slot"])
                elif boundary == second:
                    action = int(selected["second_slot"])
                if stage is not None:
                    if env.masks[slot, action] != 1:
                        raise RuntimeError("D148 replay selected a masked action")
                    legal = np.flatnonzero(env.masks[slot])
                    state = [feature(value) for value in env.state_features[slot]]
                    for candidate in legal:
                        candidate = int(candidate)
                        candidates.append(
                            {
                                "scenario": scenario,
                                "map_seed": int(selected["map_seed"]),
                                "seat": int(selected["seat"]),
                                "opponent": str(selected["opponent"]),
                                "source_replica": int(selected["source_replica"]),
                                "boundary": boundary,
                                "stage": stage,
                                "chosen_slot": action,
                                "candidate_slot": candidate,
                                "chosen": int(candidate == action),
                                "legal_candidates": len(legal),
                                **dict(zip(STATE_FIELDS, state)),
                                **dict(
                                    zip(
                                        ACTION_FIELDS,
                                        [
                                            feature(value)
                                            for value in env.action_features[
                                                slot, candidate
                                            ]
                                        ],
                                    )
                                ),
                            }
                        )
                actions[slot] = action
                boundaries[slot] += 1
            _, _, _, _, info = env.step(actions)
            steps += 1
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                scenario = int(task_before[slot])
                if scenario < pool_tasks:
                    if scenario in completed:
                        raise RuntimeError("D148 duplicate replay terminal")
                    completed.add(scenario)
                    selected = selected_by_scenario.get(scenario)
                    if selected is not None:
                        reference = population_by_key[
                            (scenario, int(selected["source_replica"]))
                        ]
                        errors = {
                            field: (str(terminal[field]), str(reference[field]))
                            for field in TERMINAL_FIELDS
                            if str(terminal[field]) != str(reference[field])
                        }
                        if errors:
                            raise RuntimeError(
                                f"D148 selected replay terminal mismatch: {errors!r}"
                            )
                        replays.append(
                            {
                                **selected,
                                **{field: terminal[field] for field in TERMINAL_FIELDS},
                            }
                        )
                boundaries[slot] = 0
    candidates.sort(
        key=lambda row: (
            int(row["scenario"]),
            int(row["boundary"]),
            int(row["candidate_slot"]),
        )
    )
    replays.sort(key=lambda row: int(row["scenario"]))
    if len(replays) != len(manifest):
        raise RuntimeError("D148 selected replay matrix incomplete")
    return candidates, replays, time.perf_counter() - started, steps


def collect(
    start_seed: int,
    maps: int,
    budget: int,
    population_output: Path,
    manifest_output: Path,
    candidate_output: Path,
    replay_output: Path,
) -> dict:
    if start_seed == 0 or maps <= 0:
        raise ValueError("D148 requires nonzero seeds and maps")
    for path in (
        population_output,
        manifest_output,
        candidate_output,
        replay_output,
    ):
        if path.exists():
            raise FileExistsError(path)
    population, population_seconds, population_steps = collect_population(
        start_seed, maps, budget
    )
    pool_tasks = maps * TASKS_PER_MAP
    manifest = select_manifest(population, pool_tasks)
    candidates, replays, replay_seconds, replay_steps = replay_manifest(
        start_seed, maps, manifest, population
    )
    write_table(population_output, POPULATION_FIELDS, population)
    write_table(manifest_output, MANIFEST_FIELDS, manifest)
    write_table(candidate_output, CANDIDATE_FIELDS, candidates)
    write_table(replay_output, REPLAY_FIELDS, replays)
    artifacts = {}
    for label, path, rows in (
        ("population", population_output, population),
        ("manifest", manifest_output, manifest),
        ("candidates", candidate_output, candidates),
        ("replays", replay_output, replays),
    ):
        artifacts[label] = {
            "path": str(path),
            "rows": len(rows),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    return {
        "start_seed": start_seed,
        "maps": maps,
        "pool_tasks": pool_tasks,
        "search_budget": budget,
        "population_seconds": population_seconds,
        "population_steps": population_steps,
        "episodes_per_second": len(population) / population_seconds,
        "replay_seconds": replay_seconds,
        "replay_steps": replay_steps,
        "supported_tasks": len(manifest),
        "positive_over_control": sum(
            int(row["sequence_gain_over_control"]) > 0 for row in manifest
        ),
        "artifacts": artifacts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("start_seed", type=int)
    parser.add_argument("maps", type=int)
    parser.add_argument("search_budget", type=int)
    parser.add_argument("population_output", type=Path)
    parser.add_argument("manifest_output", type=Path)
    parser.add_argument("candidate_output", type=Path)
    parser.add_argument("replay_output", type=Path)
    args = parser.parse_args()
    print(
        collect(
            args.start_seed,
            args.maps,
            args.search_budget,
            args.population_output,
            args.manifest_output,
            args.candidate_output,
            args.replay_output,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
