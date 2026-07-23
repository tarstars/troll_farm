from copy import deepcopy

from cgauto import analyze_d147a_selected_trajectory_feature_replay as d147a
from cgauto import collect_d147a_selected_trajectory_features as collector


def candidate(slot: int, chosen: int) -> dict[str, str]:
    row = {
        "scenario": "2",
        "map_seed": "9844128",
        "seat": "0",
        "opponent": "compact_gold",
        "reference_task_index": "8194",
        "replica": "64",
        "boundary": "0",
        "stage": "first",
        "chosen_slot": "1",
        "candidate_slot": str(slot),
        "chosen": str(chosen),
        "legal_candidates": "2",
    }
    row.update({field: "0.000000000" for field in collector.STATE_FIELDS})
    row.update({field: "0.000000000" for field in collector.ACTION_FIELDS})
    if slot:
        row[collector.ACTION_FIELDS[0]] = "1.000000000"
    return row


def test_candidate_integrity_accepts_exact_legal_group():
    result = d147a.candidate_integrity(
        [candidate(0, 0), candidate(1, 1)], list(collector.CANDIDATE_FIELDS)
    )
    assert result["pass"]
    assert result["decision_groups"] == 1
    assert result["stage_counts"] == {"first": 1}
    assert result["feature_columns"] == 443


def test_candidate_integrity_rejects_state_drift_and_nonfinite_value():
    rows = [candidate(0, 0), candidate(1, 1)]
    rows[1] = deepcopy(rows[1])
    rows[1][collector.STATE_FIELDS[0]] = "nan"
    result = d147a.candidate_integrity(rows, list(collector.CANDIDATE_FIELDS))
    assert not result["pass"]
    assert result["nonfinite_values"] == 1
    assert result["group_failures"]["state_inconsistent"] == 1


def test_candidate_integrity_rejects_nonzero_control_features():
    rows = [candidate(0, 0), candidate(1, 1)]
    rows[0][collector.ACTION_FIELDS[-1]] = "0.25"
    result = d147a.candidate_integrity(rows, list(collector.CANDIDATE_FIELDS))
    assert not result["pass"]
    assert result["group_failures"]["control_action_nonzero"] == 1
