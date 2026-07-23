from cgauto.make_d42_context_manifest import gap_bin, select_rows


def row(task, ordinal, cohort="gap_200_240", phase="early", opponent="resident"):
    return {
        "cohort": cohort,
        "phase": phase,
        "opponent": opponent,
        "map_seed": 9_773_000 + task // 16,
        "task_index": task,
        "seat": (task % 16) // 8,
        "opponent_index": task % 8,
        "decision_ordinal": ordinal,
    }


def test_d42_gap_bins_have_frozen_boundary_semantics():
    assert gap_bin(0.199999) is None
    assert gap_bin(0.200) == "gap_200_240"
    assert gap_bin(0.239999) == "gap_200_240"
    assert gap_bin(0.240) == "gap_240_260"
    assert gap_bin(0.280) == "gap_280_300"
    assert gap_bin(0.340) == "gap_320_340"
    assert gap_bin(0.340001) is None


def test_d42_selection_keeps_one_state_per_task_and_twenty_four_per_stratum():
    rows = []
    for task in range(40):
        rows.extend((row(task, 10), row(task, 20)))
    selected = select_rows(rows)
    assert len(selected) == 24
    assert len({item["task_index"] for item in selected}) == 24
    assert len({item["sample_id"] for item in selected}) == 24
    assert all(item["control_hash"] for item in selected)
