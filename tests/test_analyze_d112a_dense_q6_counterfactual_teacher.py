from collections import defaultdict

from cgauto.analyze_d112a_dense_q6_counterfactual_teacher import teacher_analysis


def control():
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "boundary_count": "3",
        "own_score": "100",
        "opponent_score": "100",
        "own_created_crops": "1",
        "own_workers": "3",
    }


def arm(boundary, slot, gain):
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "boundary_index": str(boundary),
        "slot": str(slot),
        "kind": "1",
        "own_score": str(100 + gain),
        "opponent_score": "100",
        "own_created_crops": "1",
        "own_workers": "3",
    }


def test_backward_teacher_values_wait_against_best_later_opportunity():
    task = (1, 0, "resident")
    rows = [
        arm(0, 1, 5),
        arm(0, 2, 1),
        arm(1, 1, 10),
        arm(1, 2, -2),
        arm(2, 1, 3),
    ]
    by_root = defaultdict(list)
    for row in rows:
        by_root[(task, int(row["boundary_index"]))].append(row)

    result, labels = teacher_analysis(rows, {task: control()}, by_root)
    keyed = {(row["boundary_index"], row["slot"]): row for row in labels}

    assert keyed[(2, 1)]["wait_margin_value"] == 0
    assert keyed[(2, 1)]["act_advantage"] == 3
    assert keyed[(1, 1)]["wait_margin_value"] == 3
    assert keyed[(1, 1)]["act_advantage"] == 7
    assert keyed[(0, 1)]["wait_margin_value"] == 10
    assert keyed[(0, 1)]["act_advantage"] == -5
    assert keyed[(0, 1)]["act_now_optimal"] == 0
    assert result["backward_dp"]["act_now_roots"] == 2
    assert result["oracle"]["mean_margin_gain"] == 10
    assert result["oracle"]["first_boundary_oracle_mean_gain"] == 5
    assert result["oracle"]["later_boundary_increment"] == 5
    assert sum(row["task_oracle_arm"] for row in labels) == 1
