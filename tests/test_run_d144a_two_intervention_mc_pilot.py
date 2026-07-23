import numpy as np
import pytest

from cgauto.run_d144a_two_intervention_mc_pilot import (
    MAX_SCHEDULE,
    TASKS_PER_MAP,
    episode_spec,
    expected_task,
    selected_action,
    splitmix64,
    trailing_schedule,
    update_selection_hash,
)
from cgauto.rl_macro_env import OPPONENTS


def test_splitmix_and_trailing_schedule_are_stable_and_bounded():
    values = [splitmix64(index) for index in range(32)]
    assert values == [splitmix64(index) for index in range(32)]
    assert len(set(values)) == len(values)
    assert trailing_schedule(0) == MAX_SCHEDULE
    assert trailing_schedule(1) == 0
    assert trailing_schedule(2) == 1
    assert trailing_schedule(8) == 3
    assert trailing_schedule(1 << 20) == MAX_SCHEDULE


def test_episode_spec_assigns_control_single_and_double_replicas():
    pool_tasks = 16
    assert episode_spec(0, pool_tasks, 2)["mode"] == "control"
    assert episode_spec(pool_tasks, pool_tasks, 2)["mode"] == "single"
    assert episode_spec(2 * pool_tasks, pool_tasks, 2)["mode"] == "single"
    spec = episode_spec(3 * pool_tasks + 7, pool_tasks, 2)
    assert spec["mode"] == "double"
    assert spec["replica"] == 3
    assert spec["scenario"] == 7
    assert 0 <= spec["first"] <= MAX_SCHEDULE
    assert spec["first"] < spec["second"] <= 2 * MAX_SCHEDULE + 1


def test_selected_action_obeys_schedule_mask_and_intervention_cap():
    pool_tasks = 16
    single_replicas = 1
    mask = np.zeros(65, dtype=np.uint8)
    mask[[0, 4, 11, 63]] = 1

    control_task = 3
    for boundary in range(16):
        assert (
            selected_action(
                control_task,
                boundary,
                0,
                mask,
                pool_tasks,
                single_replicas,
            )
            == 0
        )

    single_task = pool_tasks + 3
    single = episode_spec(single_task, pool_tasks, single_replicas)
    action = selected_action(
        single_task,
        single["first"],
        0,
        mask,
        pool_tasks,
        single_replicas,
    )
    assert action in {4, 11, 63}
    assert selected_action(
        single_task,
        single["second"],
        1,
        mask,
        pool_tasks,
        single_replicas,
    ) == 0

    double_task = 2 * pool_tasks + 3
    double = episode_spec(double_task, pool_tasks, single_replicas)
    first = selected_action(
        double_task,
        double["first"],
        0,
        mask,
        pool_tasks,
        single_replicas,
    )
    second = selected_action(
        double_task,
        double["second"],
        1,
        mask,
        pool_tasks,
        single_replicas,
    )
    assert first in {4, 11, 63}
    assert second in {4, 11, 63}
    assert selected_action(
        double_task,
        double["second"] + 1,
        2,
        mask,
        pool_tasks,
        single_replicas,
    ) == 0

    control_only = np.zeros(65, dtype=np.uint8)
    control_only[0] = 1
    assert selected_action(
        double_task,
        double["first"],
        0,
        control_only,
        pool_tasks,
        single_replicas,
    ) == 0


def test_expected_task_matches_map_seat_and_opponent_ordering():
    start = 9_829_000
    assert expected_task(start, 0) == (start, 0, OPPONENTS[0])
    assert expected_task(start, len(OPPONENTS)) == (start, 1, OPPONENTS[0])
    assert expected_task(start, TASKS_PER_MAP) == (start + 1, 0, OPPONENTS[0])


def test_selection_hash_is_stable_and_order_sensitive():
    first = update_selection_hash(0, 2, 7)
    assert first == update_selection_hash(0, 2, 7)
    assert first != update_selection_hash(0, 3, 7)
    assert update_selection_hash(first, 5, 9) != update_selection_hash(
        update_selection_hash(0, 5, 9), 2, 7
    )


@pytest.mark.parametrize(
    ("task_index", "pool_tasks", "single_replicas"),
    [(-1, 16, 1), (0, 0, 1), (0, 16, -1)],
)
def test_episode_spec_rejects_invalid_inputs(task_index, pool_tasks, single_replicas):
    with pytest.raises(ValueError):
        episode_spec(task_index, pool_tasks, single_replicas)
