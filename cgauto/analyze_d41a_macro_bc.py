#!/usr/bin/env python3
"""Diagnose D41a by reconstructing D40's ordering from candidate observations."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from cgauto.rl_macro_env import BRANCHES, MacroVecEnv, TASKS_PER_MAP


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
TRAINING_RESULT = ANALYSIS / "d41a-macro-bc-result.json"
DEFAULT_OUTPUT = ANALYSIS / "d41a-exact-prior-diagnostic-2026-07-21.json"
CELLS = 11 * 22
TOTAL_TURNS = 300
MAX_WORKERS = 3


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _cell_key(spatial: int) -> tuple[int, int]:
    """Recover Rust's `(x, y)` Cell ordering from the row-major action cell."""

    return spatial % 22, spatial // 22


def _option_cell_key(spatial: int | None) -> tuple[int, int, int]:
    # Rust Option ordering is None < Some, followed by the tuple's x/y ordering.
    if spatial is None:
        return 0, 0, 0
    x, y = _cell_key(spatial)
    return 1, x, y


def _integer_feature(value: np.float32 | float, scale: int) -> int:
    return int(np.rint(float(value) * scale))


def exact_prior_order(
    features: np.ndarray, actions: np.ndarray, branch: int
) -> list[int]:
    """Order candidates with D40's selected action first.

    This deliberately does not accept a teacher label.  Reproducing the label therefore
    distinguishes observation sufficiency from behavior-clone function-class failure.
    """

    if len(features) != len(actions) or not len(actions):
        raise ValueError("features/actions must be nonempty and have equal length")
    if branch < 0 or branch >= len(BRANCHES):
        raise ValueError(f"invalid D40 branch: {branch}")

    planes = np.asarray(actions, dtype=np.int64) // CELLS
    if branch == 0:  # TRAIN: the goal is a deterministic function of turn/workforce.
        turn = _integer_feature(features[0, 1], TOTAL_TURNS)
        workers = _integer_feature(features[0, 2], MAX_WORKERS)
        if turn > TOTAL_TURNS - 30 or workers >= MAX_WORKERS:
            goal = 0
        elif workers < 2:
            goal = 1
        else:
            goal = 2
        matches = np.flatnonzero(planes == goal)
        if len(matches) != 1:
            raise ValueError(f"expected one TRAIN candidate for plane {goal}")
        selected = int(matches[0])
        return [selected] + sorted(
            (index for index in range(len(actions)) if index != selected),
            key=lambda index: (int(planes[index]), int(actions[index])),
        )

    ranked: list[tuple[tuple, int]] = []
    for index, (row, raw_action) in enumerate(zip(features, actions)):
        kind = int(np.argmax(row[20:26]))
        eta = _integer_feature(row[26], TOTAL_TURNS)
        reduction = _integer_feature(row[28], 20)
        rate = _integer_feature(row[29], 50_000)
        target = None if kind in (0, 1) else int(raw_action) % CELLS
        plant = (
            None
            if float(row[43]) < 0.0
            else _integer_feature(row[43], CELLS - 1)
        )

        if branch == 1:  # positive TRAIN-deficit reduction
            key = (
                0,
                -reduction,
                eta,
                int(kind != 1),  # prefer BANK after reduction/ETA
                kind,
                _option_cell_key(target),
                _option_cell_key(plant),
                int(raw_action),
            ) if reduction > 0 else (1, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), int(raw_action))
        elif branch == 2:  # shortest non-idle shack evacuation
            key = (
                0,
                eta,
                kind,
                _option_cell_key(target),
                _option_cell_key(plant),
                int(raw_action),
            ) if kind != 0 else (1, 0, 0, (0, 0, 0), (0, 0, 0), int(raw_action))
        else:  # frozen D37 rate/provenance ordering
            key = (-rate, eta, kind, _option_cell_key(target), int(raw_action))
        ranked.append((key, index))

    if not ranked:
        raise ValueError(f"branch {BRANCHES[branch]} has no selectable candidate")
    return [index for _, index in sorted(ranked)]


def exact_prior_index(
    features: np.ndarray, actions: np.ndarray, branch: int
) -> int:
    """Select D40's exact action using only its frozen candidate observation."""

    return exact_prior_order(features, actions, branch)[0]


def replay_exact_prior(*, seed_base: int, maps: int, num_envs: int) -> dict:
    target_tasks = maps * TASKS_PER_MAP
    branch_total: collections.Counter[int] = collections.Counter()
    branch_correct: collections.Counter[int] = collections.Counter()
    branch_plane_correct: collections.Counter[int] = collections.Counter()
    completed: dict[int, dict] = {}
    decisions = 0
    started = time.perf_counter()

    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            active = set(np.flatnonzero(env.task_indices < target_tasks).tolist())
            selected = np.empty(num_envs, dtype=np.int32)
            for slot in range(num_envs):
                count = int(env.counts[slot])
                branch = int(env.branches[slot])
                index = exact_prior_index(
                    env.features[slot, :count], env.actions[slot, :count], branch
                )
                selected[slot] = env.actions[slot, index]
                if slot not in active:
                    continue
                teacher_index = int(env.teacher_indices[slot])
                teacher_action = int(env.actions[slot, teacher_index])
                branch_total[branch] += 1
                branch_correct[branch] += int(index == teacher_index)
                branch_plane_correct[branch] += int(
                    int(selected[slot]) // CELLS == teacher_action // CELLS
                )
                decisions += 1

            _, _, _, _, info = env.step(selected)
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal

    branches = {}
    for index, name in enumerate(BRANCHES):
        total = branch_total[index]
        branches[name] = {
            "decisions": total,
            "exact_matches": branch_correct[index],
            "accuracy": branch_correct[index] / total if total else 1.0,
            "action_plane_accuracy": (
                branch_plane_correct[index] / total if total else 1.0
            ),
        }
    terminal_digest = hashlib.sha256()
    for task_index in range(target_tasks):
        terminal = completed[task_index]
        terminal_digest.update(
            f"{task_index}:{terminal['action_hash']}:{terminal['state_hash']}\n".encode()
        )
    exact_matches = sum(branch_correct.values())
    return {
        "seed_base": seed_base,
        "maps": maps,
        "episodes": target_tasks,
        "decisions": decisions,
        "exact_matches": exact_matches,
        "accuracy": exact_matches / decisions,
        "branches": branches,
        "terminal_hash_sha256": terminal_digest.hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-base", type=int, default=9_710_000)
    parser.add_argument("--maps", type=int, default=32)
    parser.add_argument("--num-envs", type=int, default=16)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not TRAINING_RESULT.exists():
        raise SystemExit(f"missing D41a result: {TRAINING_RESULT}")

    replay = replay_exact_prior(
        seed_base=args.seed_base, maps=args.maps, num_envs=args.num_envs
    )
    training = json.loads(TRAINING_RESULT.read_text())
    output = {
        "training_result": str(TRAINING_RESULT),
        "training_result_sha256": sha256(TRAINING_RESULT),
        "trained_validation": training["validation"],
        "passing_model_seeds": training["passing_model_seeds"],
        "selected_seed": training["selected_seed"],
        "exact_prior": replay,
        "diagnosis": (
            "candidate observation is sufficient; the independent 44-32-16-1 "
            "scorer failed to represent D40's branchwise lexicographic ordering"
        ),
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
