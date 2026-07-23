#!/usr/bin/env python3
"""Build D153's grouped conditional-second value-learning dataset."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path

import numpy as np

from cgauto import analyze_d151a_conditional_second_corpus as d151
from cgauto import analyze_d152a_conditional_second_value as d152
from cgauto import build_d149a_joint_two_stage_dataset as d149
from cgauto import run_d148a_priority_joint_teacher as d148_runner
from cgauto import run_d151a_conditional_second_counterfactual as d151_runner


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
CANDIDATES = d149.CANDIDATES
LABELS = d152.LABELS
BRANCHES = (
    BASE
    / "yt"
    / "d151a-conditional-second-counterfactual-corpus"
    / "d151a-branches-a-9844136-9844199.tsv"
)


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def action_key(row: dict, slot_field: str) -> tuple[int, int, str, int]:
    return (*task_key(row), int(row[slot_field]))


def load_labels(path: Path = LABELS) -> dict[tuple[int, int, str, int], dict]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(d152.LABEL_FIELDS):
            raise RuntimeError("D153 label schema drift")
        rows = list(reader)
    by_action = {action_key(row, "candidate_slot"): row for row in rows}
    if len(by_action) != len(rows):
        raise RuntimeError("D153 duplicate value label")
    return by_action


def load_branches(path: Path = BRANCHES) -> dict[tuple[int, int, str, int], dict]:
    rows, fields = d151.read_table(path)
    if fields != list(d151_runner.OUTPUT_FIELDS):
        raise RuntimeError("D153 branch schema drift")
    by_action = {action_key(row, "second_slot"): row for row in rows}
    if len(by_action) != len(rows):
        raise RuntimeError("D153 duplicate branch terminal")
    return by_action


def conditional_examples(
    candidate_path: Path = CANDIDATES,
    label_path: Path = LABELS,
    branch_path: Path = BRANCHES,
) -> tuple[list[dict], dict]:
    labels = load_labels(label_path)
    branches = load_branches(branch_path)
    examples = []
    seen_actions = set()
    widths = Counter()
    active = 0
    for key, rows in d149.iter_candidate_groups(candidate_path):
        if str(rows[0]["stage"]) != "second":
            continue
        task = key[:3]
        boundary = int(key[3])
        slots = np.asarray([int(row["candidate_slot"]) for row in rows], dtype=np.int64)
        if list(slots) != sorted(set(slots)) or int(slots[0]) != 0:
            raise RuntimeError("D153 candidate slots are not stable with control first")
        state_rows = np.asarray(
            [[float(row[field]) for field in d148_runner.STATE_FIELDS] for row in rows],
            dtype=np.float32,
        )
        if not np.array_equal(state_rows, np.repeat(state_rows[:1], len(rows), axis=0)):
            raise RuntimeError("D153 conditional group state drift")
        action_features = np.asarray(
            [[float(row[field]) for field in d148_runner.ACTION_FIELDS] for row in rows],
            dtype=np.float32,
        )
        group_labels = []
        group_branches = []
        for slot in slots:
            joined_key = (*task, int(slot))
            label = labels.get(joined_key)
            branch = branches.get(joined_key)
            if label is None or branch is None:
                raise RuntimeError(f"D153 missing joined action: {joined_key!r}")
            if int(label["second_boundary"]) != boundary or int(
                branch["second_boundary"]
            ) != boundary:
                raise RuntimeError("D153 joined second boundary drift")
            if int(label["terminal_margin"]) != int(branch["margin"]):
                raise RuntimeError("D153 label/branch terminal margin drift")
            if int(label["conditional_value"]) != int(branch["margin"]) - int(
                label["control_margin"]
            ):
                raise RuntimeError("D153 conditional value arithmetic drift")
            group_labels.append(label)
            group_branches.append(branch)
            seen_actions.add(joined_key)
        controls = [row for row in group_labels if int(row["candidate_slot"]) == 0]
        if len(controls) != 1 or int(controls[0]["conditional_value"]) != 0:
            raise RuntimeError("D153 group control is not exact zero")
        fold_values = {int(row["eight_map_fold"]) for row in group_labels}
        active_values = {int(row["target_active"]) for row in group_labels}
        if len(fold_values) != 1 or len(active_values) != 1:
            raise RuntimeError("D153 group metadata drift")
        target_active = bool(active_values.pop())
        active += int(target_active)
        widths[len(rows)] += 1
        examples.append(
            {
                "task": task,
                "opponent": task[2],
                "fold": fold_values.pop(),
                "boundary": boundary,
                "target_active": target_active,
                "state_features": state_rows[0],
                "action_features": action_features,
                "candidate_slots": slots,
                "target_values": np.asarray(
                    [int(row["conditional_value"]) for row in group_labels],
                    dtype=np.float32,
                ),
                "terminal_margins": np.asarray(
                    [int(row["margin"]) for row in group_branches], dtype=np.int32
                ),
                "terminal_own_scores": np.asarray(
                    [int(row["own_score"]) for row in group_branches], dtype=np.int32
                ),
                "terminal_opponent_scores": np.asarray(
                    [int(row["opponent_score"]) for row in group_branches],
                    dtype=np.int32,
                ),
                "terminal_own_workers": np.asarray(
                    [int(row["own_workers"]) for row in group_branches], dtype=np.int16
                ),
                "terminal_own_created_crops": np.asarray(
                    [int(row["own_created_crops"]) for row in group_branches],
                    dtype=np.int16,
                ),
            }
        )
    if seen_actions != set(labels) or seen_actions != set(branches):
        raise RuntimeError(
            "D153 candidate/value/terminal action sets differ: "
            f"seen={len(seen_actions)} labels={len(labels)} branches={len(branches)}"
        )
    tasks = [row["task"] for row in examples]
    if len(set(tasks)) != len(tasks):
        raise RuntimeError("D153 duplicate conditional task")
    summary = {
        "groups": len(examples),
        "actions": len(seen_actions),
        "noncontrol_actions": len(seen_actions) - len(examples),
        "active_groups": active,
        "inactive_groups": len(examples) - active,
        "minimum_legal_actions": min(widths) if widths else 0,
        "maximum_legal_actions": max(widths) if widths else 0,
        "mean_legal_actions": (
            sum(width * count for width, count in widths.items()) / len(examples)
            if examples
            else 0.0
        ),
        "legal_action_width_counts": dict(sorted(widths.items())),
        "fold_group_counts": dict(
            sorted(Counter(int(row["fold"]) for row in examples).items())
        ),
        "opponent_group_counts": dict(
            sorted(Counter(row["opponent"] for row in examples).items())
        ),
    }
    return examples, summary


def padded_dataset(examples: list[dict]) -> dict:
    if not examples:
        raise ValueError("D153 cannot pad an empty dataset")
    groups = len(examples)
    width = max(len(row["candidate_slots"]) for row in examples)
    actions = np.zeros(
        (groups, width, len(d148_runner.ACTION_FIELDS)), dtype=np.float32
    )
    states = np.zeros((groups, len(d148_runner.STATE_FIELDS)), dtype=np.float32)
    valid = np.zeros((groups, width), dtype=np.bool_)
    slots = np.full((groups, width), -1, dtype=np.int64)
    values = np.zeros((groups, width), dtype=np.float32)
    margins = np.zeros((groups, width), dtype=np.int32)
    own_scores = np.zeros((groups, width), dtype=np.int32)
    opponent_scores = np.zeros((groups, width), dtype=np.int32)
    workers = np.zeros((groups, width), dtype=np.int16)
    crops = np.zeros((groups, width), dtype=np.int16)
    folds = np.zeros(groups, dtype=np.int64)
    active = np.zeros(groups, dtype=np.bool_)
    for index, row in enumerate(examples):
        count = len(row["candidate_slots"])
        actions[index, :count] = row["action_features"]
        states[index] = row["state_features"]
        valid[index, :count] = True
        slots[index, :count] = row["candidate_slots"]
        values[index, :count] = row["target_values"]
        margins[index, :count] = row["terminal_margins"]
        own_scores[index, :count] = row["terminal_own_scores"]
        opponent_scores[index, :count] = row["terminal_opponent_scores"]
        workers[index, :count] = row["terminal_own_workers"]
        crops[index, :count] = row["terminal_own_created_crops"]
        folds[index] = int(row["fold"])
        active[index] = bool(row["target_active"])
    if not np.isfinite(actions).all() or not np.isfinite(states).all():
        raise RuntimeError("D153 padded features are nonfinite")
    if not np.all(slots[:, 0] == 0) or not np.all(values[:, 0] == 0):
        raise RuntimeError("D153 padded controls are not exact slot-zero/value-zero")
    return {
        "action_features": actions,
        "state_features": states,
        "valid": valid,
        "candidate_slots": slots,
        "target_values": values,
        "terminal_margins": margins,
        "terminal_own_scores": own_scores,
        "terminal_opponent_scores": opponent_scores,
        "terminal_own_workers": workers,
        "terminal_own_created_crops": crops,
        "folds": folds,
        "target_active": active,
        "tasks": [row["task"] for row in examples],
        "opponents": [row["opponent"] for row in examples],
        "summary": {
            "groups": groups,
            "actions": int(valid.sum()),
            "noncontrol_actions": int(valid.sum()) - groups,
            "maximum_legal_actions": width,
            "mean_legal_actions": float(valid.sum(axis=1).mean()),
        },
    }


def main() -> int:
    examples, structural = conditional_examples()
    padded = padded_dataset(examples)
    print({"structural": structural, "padded": padded["summary"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
