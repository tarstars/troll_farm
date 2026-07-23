from __future__ import annotations

from cgauto.make_d41d_one_deviation_manifest import identity, phase, select_cohorts


def state(index: int, gap: float) -> dict:
    return {
        "map_seed": 9_760_000 + index,
        "task_index": index,
        "seat": 0,
        "opponent_index": 0,
        "opponent": "resident",
        "decision_ordinal": index,
        "turn": 50,
        "branch_index": 3,
        "branch": "rate",
        "phase": "early",
        "candidate_count": 3,
        "teacher_action": 1,
        "alternative_action": 2,
        "residual_gap": gap,
    }


def test_phase_boundaries_are_frozen() -> None:
    assert phase(99) == "early"
    assert phase(100) == "middle"
    assert phase(199) == "middle"
    assert phase(200) == "late"


def test_cohorts_are_disjoint_and_top_selects_largest_gaps() -> None:
    selected = select_cohorts([state(index, float(index)) for index in range(20)])
    top = [row for row in selected if row["cohort"] == "residual_top"]
    control = [row for row in selected if row["cohort"] == "hash_control"]
    assert len(top) == 8
    assert len(control) == 4
    assert {row["residual_gap"] for row in top} == set(map(float, range(12, 20)))
    assert {identity(row) for row in top}.isdisjoint({identity(row) for row in control})
    assert len({row["sample_id"] for row in selected}) == len(selected)
