from cgauto.analyze_d146a_two_intervention_schedule_priority import (
    priority_sample,
    schedule_class,
    schedule_priority,
)


def _row(replica, first, second):
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "mode": "double",
        "replica": str(replica),
        "scheduled_first_boundary": str(first),
        "scheduled_second_boundary": str(second),
    }


def test_schedule_classes_and_priority_are_outcome_blind():
    rows = [_row(17, 2, 4), _row(18, 0, 3), _row(19, 2, 3), _row(20, 0, 1)]
    assert [schedule_class(row) for row in rows] == [
        "later_delayed",
        "early_delayed",
        "later_immediate",
        "early_immediate",
    ]
    assert [row["replica"] for row in sorted(rows, key=schedule_priority)] == [
        "20",
        "18",
        "19",
        "17",
    ]


def test_priority_sample_takes_fixed_budget_per_task(monkeypatch):
    rows = [_row(17 + index, index % 2, index % 2 + 1) for index in range(4)]
    monkeypatch.setattr(
        "cgauto.analyze_d146a_two_intervention_schedule_priority.d145.DOUBLE_REPLICAS",
        4,
    )
    selected = priority_sample(rows, 2)
    assert len(selected) == 2
    assert all(schedule_class(row) == "early_immediate" for row in selected)
