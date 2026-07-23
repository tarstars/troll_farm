from cgauto import run_d148a_priority_joint_teacher as d148
from cgauto.run_d144a_two_intervention_mc_pilot import episode_spec


def test_priority_source_replicas_are_unique_stable_and_sorted():
    replicas = d148.priority_source_replicas(3, 16, 64)
    assert replicas == d148.priority_source_replicas(3, 16, 64)
    assert len(replicas) == len(set(replicas)) == 64
    assert all(d148.SOURCE_FIRST_REPLICA <= value <= d148.SOURCE_LAST_REPLICA for value in replicas)
    keys = []
    for replica in replicas:
        spec = episode_spec(replica * 16 + 3, 16, 16)
        keys.append(
            (*d148.schedule_class_key(int(spec["first"]), int(spec["second"])), replica)
        )
    assert keys == sorted(keys)


def test_runtime_spec_maps_control_and_priority_ordinals():
    control = d148.runtime_spec(7, 16, 64)
    assert control == {
        "scenario": 7,
        "search_ordinal": 0,
        "source_replica": 0,
        "mode": "control",
        "first": -1,
        "second": -1,
        "source_task_index": 7,
    }
    first = d148.runtime_spec(16 + 7, 16, 64)
    assert first["source_replica"] == d148.priority_source_replicas(7, 16, 64)[0]
    assert first["mode"] == "double"
    assert first["source_task_index"] == int(first["source_replica"]) * 16 + 7


def test_schedule_class_key_has_frozen_d146_order():
    assert d148.schedule_class_key(0, 1) < d148.schedule_class_key(0, 3)
    assert d148.schedule_class_key(0, 3) < d148.schedule_class_key(2, 3)
    assert d148.schedule_class_key(2, 3) < d148.schedule_class_key(2, 5)


def test_select_manifest_uses_only_executed_pairs_and_stable_outcome_tie():
    control = {
        "scenario": 0,
        "mode": "control",
        "margin": 10,
        "own_score": 20,
        "opponent_score": 10,
    }
    base = {
        "scenario": 0,
        "mode": "double",
        "intervention_batches": 2,
        "map_seed": 1,
        "seat": 0,
        "opponent": "resident",
        "search_ordinal": 1,
        "source_replica": 17,
        "scheduled_first_boundary": 0,
        "scheduled_second_boundary": 1,
        "first_selected_boundary": 0,
        "first_selected_slot": 2,
        "second_selected_boundary": 1,
        "second_selected_slot": 3,
        "selection_hash": 4,
        "margin": 12,
        "own_score": 22,
        "opponent_score": 10,
    }
    better = {**base, "source_replica": 18, "margin": 13, "own_score": 23}
    incomplete = {**better, "source_replica": 19, "intervention_batches": 1, "margin": 99}
    manifest = d148.select_manifest([control, base, better, incomplete], 1)
    assert len(manifest) == 1
    assert manifest[0]["source_replica"] == 18
    assert manifest[0]["sequence_gain_over_control"] == 3
