from collections import defaultdict

from cgauto.analyze_d113a_control_aware_dense_q6_teacher import teacher_analysis


def baseline(seed, boundaries):
    return {
        "map_seed": str(seed),
        "seat": "0",
        "opponent": "resident",
        "boundary_count": str(boundaries),
        "own_score": "100",
        "opponent_score": "100",
        "own_created_crops": "1",
        "own_workers": "3",
    }


def test_zero_boundary_task_is_forced_control_in_oracle_and_has_no_labels():
    supported = (1, 0, "resident")
    unsupported = (2, 0, "resident")
    row = {
        "map_seed": "1",
        "seat": "0",
        "opponent": "resident",
        "boundary_index": "0",
        "slot": "1",
        "kind": "1",
        "own_score": "120",
        "opponent_score": "100",
        "own_created_crops": "1",
        "own_workers": "3",
    }
    roots = defaultdict(list)
    roots[(supported, 0)].append(row)
    result, labels = teacher_analysis(
        [row],
        {
            supported: baseline(1, 1),
            unsupported: baseline(2, 0),
        },
        roots,
    )
    assert result["oracle"]["tasks"] == 2
    assert result["oracle"]["supported_tasks"] == 1
    assert result["oracle"]["mean_margin_gain"] == 10
    assert result["oracle"]["strict_improvement_rate"] == 0.5
    assert result["oracle"]["crop_rate"] == 1.0
    assert len(labels) == 1
    assert labels[0]["task_oracle_arm"] == 1
