from __future__ import annotations

import numpy as np

from cgauto import train_d142a_shared_ranker_dual_gate_selection as d142
from cgauto import train_d142b_tie_stable_dual_gate_selection as d142b


def _tasks() -> list[tuple[int, int, str]]:
    return [(10, 0, "a"), (11, 0, "a"), (12, 0, "a"), (13, 0, "a")]


def test_tie_stable_boundary_hits_exact_count_across_numeric_tie() -> None:
    tasks = _tasks()
    roots = [
        (tasks[0], 0),
        (tasks[0], 1),
        (tasks[1], 0),
        (tasks[2], 0),
        (tasks[3], 0),
    ]
    values = np.asarray([2.0, 1.0, 1.0, 1.0, 0.0], dtype=np.float32)
    calibration = d142b.tie_stable_count_boundary(tasks, roots, values, 2)
    gates = d142b.binary_gate_by_root(roots, values, calibration)
    active = {
        task
        for task in tasks
        if any(gates[root] > d142b.POLICY_OFFSET for root in roots if root[0] == task)
    }
    assert calibration["numeric_boundary_tied"] is True
    assert calibration["achieved_active_tasks"] == 2
    assert len(active) == 2
    assert tasks[0] in active


def test_priority_only_affects_logits_equal_to_cutoff() -> None:
    tasks = _tasks()
    roots = [(task, 0) for task in tasks]
    values = np.asarray([3.0, 2.0, 1.0, 0.0], dtype=np.float32)
    calibration = d142b.tie_stable_count_boundary(tasks, roots, values, 2)
    gates = d142b.binary_gate_by_root(roots, values, calibration)
    assert calibration["numeric_boundary_tied"] is False
    assert gates[roots[0]] == 1.0
    assert gates[roots[1]] == 1.0
    assert gates[roots[2]] == 0.0
    assert gates[roots[3]] == 0.0


def test_task_priority_is_stable_and_key_sensitive() -> None:
    task = (9_844_000, 0, "resident")
    assert d142b.stable_task_priority(task) == d142b.stable_task_priority(task)
    assert d142b.stable_task_priority(task) != d142b.stable_task_priority(
        (9_844_000, 1, "resident")
    )


def test_d142b_retains_d142_architecture_and_component_matrix() -> None:
    assert d142b.BLOCKS == d142.BLOCKS == 8
    assert d142b.WORKERS == d142.WORKERS == 4
    assert d142.PARAMETERS == 7_475
    assert len(d142.expected_component_hashes()) == 32
