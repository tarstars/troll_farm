from cgauto.analyze_d145a_two_intervention_population_decomposition import (
    FIRST_DOUBLE_REPLICA,
    population_view,
    selected_trajectory_decomposition,
)


def _control():
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "own_score": "10",
        "opponent_score": "10",
        "own_created_crops": "1",
        "own_workers": "3",
    }


def test_population_view_filters_double_replicas():
    control = _control()
    arms = [{**control, "own_score": "12", "slot": "1"}]
    rows = [
        {
            **control,
            "mode": "double",
            "intervention_batches": "2",
            "own_score": str(score),
            "replica": str(replica),
        }
        for replica, score in ((FIRST_DOUBLE_REPLICA, 14), (FIRST_DOUBLE_REPLICA + 1, 20))
    ]
    result = population_view(rows, arms, {(1, 0, "resident"): control}, {FIRST_DOUBLE_REPLICA})
    assert result["replica_count"] == 1
    assert result["episode_rows"] == 1
    assert result["summary"]["mean_increment_beyond_one_use"] == 2


def test_selected_decomposition_attributes_lift_to_same_first():
    control = _control()
    arm = {
        **control,
        "own_score": "14",
        "boundary_index": "2",
        "slot": "3",
        "kind": "1",
    }
    double = {
        **control,
        "mode": "double",
        "intervention_batches": "2",
        "own_score": "20",
        "replica": "17",
        "first_selected_boundary": "2",
        "second_selected_boundary": "5",
        "first_selected_slot": "3",
        "second_selected_slot": "4",
        "selection_hash": "99",
    }
    summary, selected = selected_trajectory_decomposition(
        [double], [arm], {(1, 0, "resident"): control}
    )
    assert len(selected) == 1
    assert selected[0]["sequence_increment_over_one"] == 6
    assert selected[0]["second_lift_over_same_first"] == 6
    assert summary["first_matches_one_use_oracle_rate"] == 1.0
