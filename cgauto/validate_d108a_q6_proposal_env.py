#!/usr/bin/env python3
"""Validate D108's q6 vector environment against locked D107 zero traces."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cgauto.rl_q6_proposal_env import OPPONENTS, Q6ProposalVecEnv


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
D107_ROWS = BASE / "d107a-q6-controller-population-a-9829000-9829007.tsv"
D107_SUPPORT = BASE / "d107a-q6-zero-support-audit-9829000-9829007.tsv"
D107_BASELINES = BASE / "d107a-q6-controller-baselines-a-9829000-9829007.tsv"
OUTPUT = BASE / "d108a-q6-proposal-environment-parity.json"
MAP_START = 9_829_000
MAPS = 8
TASKS = MAPS * 2 * len(OPPONENTS)
NUM_ENVS = 20


def read_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def update_digest(
    digest: hashlib._Hash,
    task_index: int,
    state: np.ndarray,
    actions: np.ndarray,
    mask: np.ndarray,
) -> None:
    digest.update(task_index.to_bytes(8, "little"))
    digest.update(np.ascontiguousarray(state).tobytes())
    digest.update(np.ascontiguousarray(actions).tobytes())
    digest.update(np.ascontiguousarray(mask).tobytes())


def run_once() -> dict:
    d107_zero = {
        key(row): row for row in read_table(D107_ROWS) if row["policy"] == "zero_control"
    }
    d107_support = {key(row): row for row in read_table(D107_SUPPORT)}
    baselines = {key(row): row for row in read_table(D107_BASELINES)}
    if len(d107_zero) != TASKS or len(d107_support) != TASKS or len(baselines) != TASKS:
        raise RuntimeError("D108 parity source cardinality mismatch")

    eligible = np.zeros(TASKS, dtype=np.int64)
    unique_sum = np.zeros(TASKS, dtype=np.int64)
    unique_min = np.full(TASKS, np.iinfo(np.int64).max, dtype=np.int64)
    unique_max = np.zeros(TASKS, dtype=np.int64)
    returns = np.zeros(NUM_ENVS, dtype=np.float64)
    completed: dict[int, dict] = {}
    feature_digest = hashlib.sha256()
    steps = 0
    started = time.perf_counter()
    with Q6ProposalVecEnv(NUM_ENVS, MAP_START, map_pool=MAPS) as env:
        for _ in range(256):
            for slot, task_index in enumerate(env.task_indices):
                task_index = int(task_index)
                if task_index >= TASKS:
                    continue
                update_digest(
                    feature_digest,
                    task_index,
                    env.state_features[slot],
                    env.action_features[slot],
                    env.masks[slot],
                )
                noncontrol = int(env.masks[slot].sum()) - 1
                if noncontrol > 0:
                    eligible[task_index] += 1
                    unique_sum[task_index] += noncontrol
                    unique_min[task_index] = min(unique_min[task_index], noncontrol)
                    unique_max[task_index] = max(unique_max[task_index], noncontrol)
            _, _, _, rewards, info = env.step(np.zeros(NUM_ENVS, dtype=np.int32))
            returns += rewards
            steps += NUM_ENVS
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                task_index = terminal["task_index"]
                if task_index < TASKS:
                    if task_index in completed:
                        raise RuntimeError(f"duplicate D108 parity task {task_index}")
                    terminal = dict(terminal)
                    terminal["paired_return"] = float(returns[slot])
                    completed[task_index] = terminal
                returns[slot] = 0.0
            if len(completed) == TASKS:
                break
        else:
            raise RuntimeError("D108 parity decision guard")
    elapsed = time.perf_counter() - started

    comparisons = []
    for task_index in range(TASKS):
        terminal = completed[task_index]
        task = (terminal["map_seed"], terminal["seat"], terminal["opponent"])
        zero = d107_zero[task]
        support = d107_support[task]
        baseline = baselines[task]
        minimum = 0 if eligible[task_index] == 0 else int(unique_min[task_index])
        exact_fields = {
            "own_score": int(baseline["own_score"]),
            "opponent_score": int(baseline["opponent_score"]),
            "own_workers": int(baseline["own_workers"]),
            "successful_trains": int(baseline["successful_trains"]),
            "own_created_crops": int(baseline["own_created_crops"]),
            "invalid_direct_commands": int(baseline["invalid_direct_commands"]),
            "provenance_failures": int(baseline["provenance_failures"]),
            "deposit_prediction_failures": int(baseline["deposit_prediction_failures"]),
            "invalidated_jobs": int(baseline["invalidated_jobs"]),
            "action_hash": int(baseline["action_hash"]),
            "state_hash": int(baseline["state_hash"]),
        }
        terminal_exact = all(terminal[field] == value for field, value in exact_fields.items())
        support_exact = (
            terminal["boundary_decisions"] == int(zero["eligible_batches"])
            == int(eligible[task_index])
            and int(unique_sum[task_index])
            == int(zero["unique_proposals"]) - int(zero["eligible_batches"])
            and minimum == int(support["minimum_unique_proposals"]) - int(eligible[task_index] > 0)
            and int(unique_max[task_index])
            == max(0, int(zero["maximum_unique_proposals"]) - int(eligible[task_index] > 0))
        )
        reward_exact = (
            terminal["margin_delta"] == 0
            and abs(terminal["paired_return"]) < 1.0e-7
            and terminal["intervention_batches"] == 0
            and terminal["joint_batches"] == 0
            and terminal["noncontrol_assignments"] == 0
        )
        comparisons.append(
            {
                "task_index": task_index,
                "task": task,
                "terminal_exact": terminal_exact,
                "support_exact": support_exact,
                "reward_exact": reward_exact,
                "eligible_boundaries": int(eligible[task_index]),
                "unique_noncontrol_sum": int(unique_sum[task_index]),
                "minimum_unique_noncontrol": minimum,
                "maximum_unique_noncontrol": int(unique_max[task_index]),
            }
        )
    return {
        "tasks": len(completed),
        "steps": steps,
        "elapsed_seconds": elapsed,
        "steps_per_second": steps / elapsed,
        "feature_stream_sha256": feature_digest.hexdigest(),
        "terminal_exact": all(row["terminal_exact"] for row in comparisons),
        "support_exact": all(row["support_exact"] for row in comparisons),
        "reward_exact": all(row["reward_exact"] for row in comparisons),
        "eligible_tasks": sum(row["eligible_boundaries"] > 0 for row in comparisons),
        "eligible_boundaries": sum(row["eligible_boundaries"] for row in comparisons),
        "minimum_unique_noncontrol": min(
            row["minimum_unique_noncontrol"]
            for row in comparisons
            if row["eligible_boundaries"] > 0
        ),
        "comparisons": comparisons,
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    os.environ.setdefault("RAYON_NUM_THREADS", "20")
    first = run_once()
    second = run_once()
    repeat_exact = (
        first["feature_stream_sha256"] == second["feature_stream_sha256"]
        and first["comparisons"] == second["comparisons"]
    )
    gates = {
        "complete_128_tasks": first["tasks"] == TASKS and second["tasks"] == TASKS,
        "terminal_exact_d107_d40": first["terminal_exact"] and second["terminal_exact"],
        "proposal_support_exact_d107": first["support_exact"] and second["support_exact"],
        "paired_reward_exact_zero": first["reward_exact"] and second["reward_exact"],
        "repeat_feature_and_comparison_exact": repeat_exact,
        "eligible_cardinality_exact": first["eligible_tasks"] == 119
        and first["eligible_boundaries"] == 647,
        "minimum_unique_noncontrol_exact": first["minimum_unique_noncontrol"] == 6,
    }
    result = {
        "schema": "troll-farm-d108a-q6-proposal-environment-parity-v1",
        "scope": "consumed D107 panel; environment parity only",
        "config": {
            "map_start": MAP_START,
            "maps": MAPS,
            "tasks": TASKS,
            "num_envs": NUM_ENVS,
            "threads": 20,
        },
        "first": {key: value for key, value in first.items() if key != "comparisons"},
        "second": {key: value for key, value in second.items() if key != "comparisons"},
        "repeat_exact": repeat_exact,
        "gates": gates,
        "pass": all(gates.values()),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
