#!/usr/bin/env python3
"""Join exact selected-first action memory into D153 conditional groups."""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path

import numpy as np

from cgauto import build_d149a_joint_two_stage_dataset as d149
from cgauto import build_d153a_conditional_value_dataset as d153
from cgauto import run_d148a_priority_joint_teacher as d148_runner


def feature_hash(values: np.ndarray) -> str:
    array = np.asarray(values, dtype="<f4")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def selected_first_actions(
    candidate_path: Path = d153.CANDIDATES,
    target_path: Path = d149.TARGETS,
) -> dict[tuple[int, int, str], dict]:
    targets = d149.load_targets(target_path)
    result = {}
    for key, rows in d149.iter_candidate_groups(candidate_path):
        if str(rows[0]["stage"]) != "first":
            continue
        task = key[:3]
        target = targets.get(task)
        if target is None:
            raise RuntimeError("D155 first group lacks a trajectory target")
        boundary = int(key[3])
        slot = int(target["first_slot"])
        if boundary != int(target["first_boundary"]):
            raise RuntimeError("D155 first boundary drift")
        if int(rows[0]["chosen_slot"]) != slot:
            raise RuntimeError("D155 candidate/target selected first slot drift")
        selected = [row for row in rows if int(row["candidate_slot"]) == slot]
        if len(selected) != 1:
            raise RuntimeError("D155 selected first action multiplicity drift")
        row = selected[0]
        action = np.asarray(
            [float(row[field]) for field in d148_runner.ACTION_FIELDS],
            dtype=np.float32,
        )
        state = np.asarray(
            [float(row[field]) for field in d148_runner.STATE_FIELDS],
            dtype=np.float32,
        )
        if not np.isfinite(action).all() or not np.isfinite(state).all():
            raise RuntimeError("D155 selected first features are nonfinite")
        if task in result:
            raise RuntimeError("D155 duplicate selected first task")
        result[task] = {
            "first_boundary": boundary,
            "first_slot": slot,
            "first_action_features": action,
            "first_state_features": state,
            "first_action_feature_sha256": feature_hash(action),
        }
    if set(result) != set(targets):
        raise RuntimeError(
            f"D155 selected first task set drift: first={len(result)} targets={len(targets)}"
        )
    return result


def memory_examples(
    candidate_path: Path = d153.CANDIDATES,
    label_path: Path = d153.LABELS,
    branch_path: Path = d153.BRANCHES,
    target_path: Path = d149.TARGETS,
) -> tuple[list[dict], dict]:
    examples, structural = d153.conditional_examples(
        candidate_path, label_path, branch_path
    )
    first = selected_first_actions(candidate_path, target_path)
    hashes = Counter()
    slots = Counter()
    for row in examples:
        memory = first.get(row["task"])
        if memory is None:
            raise RuntimeError("D155 conditional task lacks first-action memory")
        row.update(memory)
        hashes[memory["first_action_feature_sha256"]] += 1
        slots[int(memory["first_slot"])] += 1
    summary = {
        **structural,
        "first_action_groups": len(first),
        "nonzero_first_slots": sum(int(row["first_slot"] != 0) for row in first.values()),
        "unique_first_action_feature_hashes": len(hashes),
        "repeated_first_action_feature_groups": sum(
            count for count in hashes.values() if count > 1
        ),
        "first_slot_counts": dict(sorted(slots.items())),
    }
    return examples, summary


def padded_dataset(examples: list[dict]) -> dict:
    result = d153.padded_dataset(examples)
    first_actions = np.asarray(
        [row["first_action_features"] for row in examples], dtype=np.float32
    )
    first_states = np.asarray(
        [row["first_state_features"] for row in examples], dtype=np.float32
    )
    first_slots = np.asarray(
        [row["first_slot"] for row in examples], dtype=np.int64
    )
    if first_actions.shape != (len(examples), 379) or first_states.shape != (
        len(examples),
        64,
    ):
        raise RuntimeError("D155 padded first-memory shape drift")
    if not np.isfinite(first_actions).all() or not np.isfinite(first_states).all():
        raise RuntimeError("D155 padded first memory is nonfinite")
    result.update(
        {
            "first_action_features": first_actions,
            "first_state_features": first_states,
            "first_slots": first_slots,
        }
    )
    result["summary"] = {
        **result["summary"],
        "first_action_groups": len(first_actions),
        "nonzero_first_slots": int((first_slots != 0).sum()),
        "unique_first_action_feature_rows": len(
            {feature_hash(row) for row in first_actions}
        ),
    }
    return result


def main() -> int:
    examples, structural = memory_examples()
    padded = padded_dataset(examples)
    print({"structural": structural, "padded": padded["summary"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
