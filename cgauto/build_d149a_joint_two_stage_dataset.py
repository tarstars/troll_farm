#!/usr/bin/env python3
"""Build on-policy structural examples from a D148 joint trajectory corpus."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path

import numpy as np

from cgauto import analyze_d148a_priority_joint_teacher as d148
from cgauto import run_d148a_priority_joint_teacher as runner
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
CANDIDATES = (
    BASE
    / "yt"
    / "d148a-priority-joint-teacher-corpus"
    / "d148a-candidates-9844136-9844199.tsv"
)
TARGETS = BASE / "d148a-joint-trajectory-targets-9844136-9844199.tsv"


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def load_targets(path: Path = TARGETS) -> dict[tuple[int, int, str], dict[str, str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(d148.TARGET_FIELDS):
            raise RuntimeError("D149 target schema drift")
        rows = list(reader)
    by_task = {task_key(row): row for row in rows}
    if len(by_task) != len(rows):
        raise RuntimeError("D149 duplicate target task")
    return by_task


def iter_candidate_groups(path: Path = CANDIDATES):
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(runner.CANDIDATE_FIELDS):
            raise RuntimeError("D149 candidate schema drift")
        key = None
        rows = []
        seen = set()
        for row in reader:
            next_key = (*task_key(row), int(row["boundary"]))
            if key is None:
                key = next_key
            if next_key != key:
                if next_key in seen:
                    raise RuntimeError("D149 candidate group is noncontiguous")
                seen.add(key)
                yield key, rows
                key = next_key
                rows = []
            rows.append(row)
        if rows:
            yield key, rows


def structural_examples(
    candidate_path: Path = CANDIDATES,
    target_path: Path = TARGETS,
) -> tuple[list[dict], dict]:
    targets = load_targets(target_path)
    examples = []
    raw_stages = Counter()
    included_stages = Counter()
    groups_by_target = Counter()
    for key, rows in iter_candidate_groups(candidate_path):
        target_key = key[:3]
        target = targets.get(target_key)
        if target is None:
            raise RuntimeError(f"D149 candidate lacks trajectory target: {target_key!r}")
        first = rows[0]
        stage = str(first["stage"])
        boundary = int(first["boundary"])
        active = bool(int(target["target_active"]))
        raw_stages[stage] += 1
        groups_by_target[target_key] += 1

        # A rejected pair remains on-policy only until and including its proposed
        # first action. Its post-action second state must not train the controller.
        if not active and boundary > int(target["first_boundary"]):
            continue
        state_rows = np.asarray(
            [
                [float(row[field]) for field in runner.STATE_FIELDS]
                for row in rows
            ],
            dtype=np.float32,
        )
        if not np.array_equal(state_rows, np.repeat(state_rows[:1], len(rows), axis=0)):
            raise RuntimeError("D149 group state drift")
        noncontrol = [row for row in rows if int(row["candidate_slot"]) > 0]
        if not noncontrol:
            raise RuntimeError("D149 decision group lacks noncontrol proposals")
        action_features = np.asarray(
            [
                [float(row[field]) for field in runner.ACTION_FIELDS]
                for row in noncontrol
            ],
            dtype=np.float32,
        )
        slots = np.asarray(
            [int(row["candidate_slot"]) for row in noncontrol], dtype=np.int64
        )
        gate_target = active and stage in {"first", "second"}
        rank_target = -1
        if gate_target:
            chosen_slot = int(first["chosen_slot"])
            matches = np.flatnonzero(slots == chosen_slot)
            if len(matches) != 1:
                raise RuntimeError("D149 chosen noncontrol proposal is missing")
            rank_target = int(matches[0])
        examples.append(
            {
                "task": target_key,
                "fold": int(target["eight_map_fold"]),
                "boundary": boundary,
                "stage": stage,
                "active_trajectory": active,
                "state_features": state_rows[0],
                "action_features": action_features,
                "candidate_slots": slots,
                "gate_target": gate_target,
                "rank_target": rank_target,
            }
        )
        included_stages[stage] += 1
    missing = set(targets) - set(groups_by_target)
    if missing:
        raise RuntimeError(f"D149 targets lack candidate groups: {len(missing)}")
    active_tasks = sum(int(row["target_active"]) for row in targets.values())
    active_examples = [row for row in examples if row["active_trajectory"]]
    if sum(row["gate_target"] for row in active_examples) != 2 * active_tasks:
        raise RuntimeError("D149 active first/second target count drift")
    summary = {
        "target_tasks": len(targets),
        "active_tasks": active_tasks,
        "inactive_tasks": len(targets) - active_tasks,
        "raw_groups": sum(raw_stages.values()),
        "included_groups": len(examples),
        "excluded_off_policy_groups": sum(raw_stages.values()) - len(examples),
        "gate_act_groups": sum(row["gate_target"] for row in examples),
        "gate_wait_groups": sum(not row["gate_target"] for row in examples),
        "rank_groups": sum(row["rank_target"] >= 0 for row in examples),
        "raw_stage_counts": dict(sorted(raw_stages.items())),
        "included_stage_counts": dict(sorted(included_stages.items())),
        "fold_task_counts": dict(
            sorted(Counter(int(row["eight_map_fold"]) for row in targets.values()).items())
        ),
    }
    return examples, summary


def padded_dataset(examples: list[dict]) -> dict:
    if not examples:
        raise ValueError("D149 cannot pad an empty dataset")
    proposals = max(len(row["candidate_slots"]) for row in examples)
    count = len(examples)
    actions = np.zeros((count, proposals, len(runner.ACTION_FIELDS)), dtype=np.float32)
    valid = np.zeros((count, proposals), dtype=np.bool_)
    slots = np.zeros((count, proposals), dtype=np.int64)
    states = np.zeros((count, len(runner.STATE_FIELDS)), dtype=np.float32)
    rank_targets = np.full(count, -1, dtype=np.int64)
    gate_targets = np.zeros(count, dtype=np.bool_)
    folds = np.zeros(count, dtype=np.int64)
    for index, row in enumerate(examples):
        width = len(row["candidate_slots"])
        actions[index, :width] = row["action_features"]
        valid[index, :width] = True
        slots[index, :width] = row["candidate_slots"]
        states[index] = row["state_features"]
        rank_targets[index] = int(row["rank_target"])
        gate_targets[index] = bool(row["gate_target"])
        folds[index] = int(row["fold"])
    if not np.isfinite(actions).all() or not np.isfinite(states).all():
        raise RuntimeError("D149 padded features are nonfinite")
    return {
        "action_features": actions,
        "valid": valid,
        "candidate_slots": slots,
        "state_features": states,
        "rank_targets": rank_targets,
        "gate_targets": gate_targets,
        "folds": folds,
        "tasks": [row["task"] for row in examples],
        "stages": [row["stage"] for row in examples],
        "summary": {
            "groups": count,
            "maximum_noncontrol_proposals": proposals,
            "mean_noncontrol_proposals": float(valid.sum(axis=1).mean()),
            "act_groups": int(gate_targets.sum()),
            "wait_groups": int((~gate_targets).sum()),
            "rank_groups": int((rank_targets >= 0).sum()),
        },
    }


def main() -> int:
    examples, summary = structural_examples()
    padded = padded_dataset(examples)
    print({"structural": summary, "padded": padded["summary"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
