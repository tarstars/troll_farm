#!/usr/bin/env python3
"""Replay D145 winners and collect complete legal q6 candidate features."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import time

import numpy as np

from cgauto.rl_q6_proposal_env import (
    Q6_ACTION_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
)
from cgauto.run_d144a_two_intervention_mc_pilot import TASKS_PER_MAP, expected_task


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
MANIFEST = BASE / "d145a-selected-two-intervention-trajectories.tsv"
REFERENCE = (
    BASE
    / "yt"
    / "d144a-two-intervention-mc-pilot"
    / "d144a-mc-a-9844128-9844135.tsv"
)
START_SEED = 9_844_128
MAPS = 8
TASKS = MAPS * TASKS_PER_MAP

TASK_FIELDS = ("map_seed", "seat", "opponent")
TERMINAL_FIELDS = (
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
STATE_FIELDS = tuple(f"state_{index:03d}" for index in range(Q6_STATE_FEATURES))
ACTION_FIELDS = tuple(f"action_{index:03d}" for index in range(Q6_ACTION_FEATURES))
CANDIDATE_FIELDS = (
    "scenario",
    "map_seed",
    "seat",
    "opponent",
    "reference_task_index",
    "replica",
    "boundary",
    "stage",
    "chosen_slot",
    "candidate_slot",
    "chosen",
    "legal_candidates",
) + STATE_FIELDS + ACTION_FIELDS
REPLAY_FIELDS = (
    "scenario",
    "reference_task_index",
    "replica",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "second_slot",
) + TERMINAL_FIELDS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def decision_stage(boundary: int, first: int, second: int) -> str | None:
    if boundary < first:
        return "wait_before_first"
    if boundary == first:
        return "first"
    if boundary < second:
        return "wait_before_second"
    if boundary == second:
        return "second"
    return None


def chosen_action(boundary: int, row: dict[str, str]) -> int:
    if boundary == int(row["first_boundary"]):
        return int(row["first_slot"])
    if boundary == int(row["second_boundary"]):
        return int(row["second_slot"])
    return 0


def feature(value: np.float32) -> str:
    return f"{float(value):.9f}"


def load_inputs() -> tuple[dict, dict]:
    manifest, fields = read_table(MANIFEST)
    expected_manifest_fields = {
        "map_seed",
        "seat",
        "opponent",
        "replica",
        "first_boundary",
        "second_boundary",
        "first_slot",
        "second_slot",
        "selection_hash",
    }
    if not expected_manifest_fields <= set(fields) or len(manifest) != 57:
        raise RuntimeError("D147 selected manifest schema/count drift")
    manifest_by_task = {task_key(row): row for row in manifest}
    if len(manifest_by_task) != len(manifest):
        raise RuntimeError("D147 selected manifest has duplicate tasks")
    reference, _ = read_table(REFERENCE)
    reference_by_key = {
        (task_key(row), int(row["replica"])): row for row in reference
    }
    selected_reference = {}
    for task, row in manifest_by_task.items():
        key = task, int(row["replica"])
        reference_row = reference_by_key.get(key)
        if reference_row is None:
            raise RuntimeError(f"D147 reference trajectory missing: {key!r}")
        if (
            int(reference_row["first_selected_boundary"])
            != int(row["first_boundary"])
            or int(reference_row["second_selected_boundary"])
            != int(row["second_boundary"])
            or int(reference_row["first_selected_slot"]) != int(row["first_slot"])
            or int(reference_row["second_selected_slot"]) != int(row["second_slot"])
            or int(reference_row["selection_hash"]) != int(row["selection_hash"])
        ):
            raise RuntimeError(f"D147 manifest/reference action drift: {key!r}")
        selected_reference[task] = reference_row
    return manifest_by_task, selected_reference


def write_table(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def collect(candidate_output: Path, replay_output: Path) -> dict:
    manifest_by_task, reference_by_task = load_inputs()
    candidates = []
    replays = []
    boundaries = np.zeros(TASKS, dtype=np.int32)
    completed = set()
    started = time.perf_counter()
    steps = 0
    with Q6ProposalVecEnv(TASKS, START_SEED, map_pool=MAPS) as env:
        while len(completed) < TASKS:
            task_before = env.task_indices.copy()
            actions = np.zeros(TASKS, dtype=np.int32)
            decisions = env.masks.sum(axis=1) > 1
            for slot in np.flatnonzero(decisions):
                task_index = int(task_before[slot])
                if task_index >= TASKS:
                    continue
                task = expected_task(START_SEED, task_index)
                manifest = manifest_by_task.get(task)
                boundary = int(boundaries[slot])
                if manifest is not None:
                    first = int(manifest["first_boundary"])
                    second = int(manifest["second_boundary"])
                    stage = decision_stage(boundary, first, second)
                    action = chosen_action(boundary, manifest)
                    if stage is not None:
                        if env.masks[slot, action] != 1:
                            raise RuntimeError(
                                f"D147 selected masked action: {task!r}:{boundary}:{action}"
                            )
                        legal = np.flatnonzero(env.masks[slot])
                        state = [feature(value) for value in env.state_features[slot]]
                        for candidate in legal:
                            candidate = int(candidate)
                            action_features = [
                                feature(value)
                                for value in env.action_features[slot, candidate]
                            ]
                            candidates.append(
                                {
                                    "scenario": task_index,
                                    "map_seed": task[0],
                                    "seat": task[1],
                                    "opponent": task[2],
                                    "reference_task_index": int(
                                        reference_by_task[task]["task_index"]
                                    ),
                                    "replica": int(manifest["replica"]),
                                    "boundary": boundary,
                                    "stage": stage,
                                    "chosen_slot": action,
                                    "candidate_slot": candidate,
                                    "chosen": int(candidate == action),
                                    "legal_candidates": len(legal),
                                    **dict(zip(STATE_FIELDS, state)),
                                    **dict(zip(ACTION_FIELDS, action_features)),
                                }
                            )
                    actions[slot] = action
                boundaries[slot] += 1
            _, _, _, _, info = env.step(actions)
            steps += 1
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                task_index = int(task_before[slot])
                if task_index < TASKS:
                    if task_index in completed:
                        raise RuntimeError("D147 duplicate initial task terminal")
                    completed.add(task_index)
                    task = expected_task(START_SEED, task_index)
                    manifest = manifest_by_task.get(task)
                    if manifest is not None:
                        reference = reference_by_task[task]
                        errors = {
                            field: (str(terminal[field]), str(reference[field]))
                            for field in TERMINAL_FIELDS
                            if str(terminal[field]) != str(reference[field])
                        }
                        if errors:
                            raise RuntimeError(
                                f"D147 terminal parity failed for {task!r}: {errors!r}"
                            )
                        replays.append(
                            {
                                "scenario": task_index,
                                "reference_task_index": int(reference["task_index"]),
                                "replica": int(manifest["replica"]),
                                "first_boundary": int(manifest["first_boundary"]),
                                "first_slot": int(manifest["first_slot"]),
                                "second_boundary": int(manifest["second_boundary"]),
                                "second_slot": int(manifest["second_slot"]),
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
    if len(replays) != len(manifest_by_task):
        raise RuntimeError("D147 selected replay matrix incomplete")
    chosen_rows = [row for row in candidates if int(row["chosen"]) == 1]
    expected_chosen = sum(
        int(row["second_boundary"]) + 1 for row in manifest_by_task.values()
    )
    if len(chosen_rows) != expected_chosen:
        raise RuntimeError("D147 chosen decision count drift")
    if sum(row["stage"] == "first" for row in chosen_rows) != len(manifest_by_task):
        raise RuntimeError("D147 first-decision count drift")
    if sum(row["stage"] == "second" for row in chosen_rows) != len(manifest_by_task):
        raise RuntimeError("D147 second-decision count drift")
    write_table(candidate_output, CANDIDATE_FIELDS, candidates)
    write_table(replay_output, REPLAY_FIELDS, replays)
    elapsed = time.perf_counter() - started
    return {
        "candidate_path": str(candidate_output),
        "candidate_rows": len(candidates),
        "candidate_bytes": candidate_output.stat().st_size,
        "candidate_sha256": sha256(candidate_output),
        "replay_path": str(replay_output),
        "replay_rows": len(replays),
        "replay_bytes": replay_output.stat().st_size,
        "replay_sha256": sha256(replay_output),
        "chosen_decisions": len(chosen_rows),
        "first_decisions": sum(row["stage"] == "first" for row in chosen_rows),
        "second_decisions": sum(row["stage"] == "second" for row in chosen_rows),
        "steps": steps,
        "elapsed_seconds": elapsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_output", type=Path)
    parser.add_argument("replay_output", type=Path)
    args = parser.parse_args()
    print(collect(args.candidate_output, args.replay_output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
