import csv

from cgauto import analyze_d148a_priority_joint_teacher as d148
from cgauto import run_d148a_priority_joint_teacher as runner


def feature_row(slot: int, chosen: int) -> dict[str, str]:
    row = {
        "scenario": "0",
        "map_seed": "9844136",
        "seat": "0",
        "opponent": "resident",
        "source_replica": "17",
        "boundary": "0",
        "stage": "first",
        "chosen_slot": "1",
        "candidate_slot": str(slot),
        "chosen": str(chosen),
        "legal_candidates": "2",
    }
    row.update({field: "0.000000000" for field in runner.STATE_FIELDS})
    row.update({field: "0.000000000" for field in runner.ACTION_FIELDS})
    if slot:
        row[runner.ACTION_FIELDS[0]] = "1.000000000"
    return row


def test_validate_candidate_group_accepts_exact_group():
    assert not d148.validate_candidate_group([feature_row(0, 0), feature_row(1, 1)])


def test_validate_candidate_group_rejects_nonzero_control():
    rows = [feature_row(0, 0), feature_row(1, 1)]
    rows[0][runner.ACTION_FIELDS[3]] = "1.0"
    failures = d148.validate_candidate_group(rows)
    assert failures["control_action_nonzero"] == 1


def test_iter_arm_blocks_streams_contiguous_seed_blocks(tmp_path):
    path = tmp_path / "arms.tsv"
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=("map_seed", "seat", "opponent"),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(
            [
                {"map_seed": 9844136, "seat": 0, "opponent": "resident"},
                {"map_seed": 9844143, "seat": 1, "opponent": "resident"},
                {"map_seed": 9844144, "seat": 0, "opponent": "resident"},
            ]
        )
    blocks = list(d148.iter_arm_blocks(path))
    assert [block for block, _, _ in blocks] == [0, 1]
    assert [len(rows) for _, rows, _ in blocks] == [2, 1]


def test_transfer_analysis_applies_strict_pair_selection():
    controls = {}
    one = {}
    pairs = {}
    for seed, seat, opponent in sorted(d148.expected_tasks()):
        key = (seed, seat, opponent)
        controls[key] = {
            "own_score": "10",
            "opponent_score": "10",
            "own_workers": "3",
            "own_created_crops": "1",
        }
        one[key] = {
            "own_score": "11",
            "opponent_score": "10",
            "own_workers": "3",
            "own_created_crops": "1",
            "boundary_index": "0",
            "slot": "1",
        }
        pairs[key] = {
            "own_score": "14",
            "opponent_score": "10",
            "own_workers": "3",
            "own_created_crops": "1",
            "source_replica": "17",
            "first_selected_boundary": "0",
            "first_selected_slot": "1",
            "second_selected_boundary": "1",
            "second_selected_slot": "2",
            "selection_hash": "3",
        }
    result, targets = d148.transfer_analysis(controls, one, pairs)
    assert result["pass"]
    assert result["aggregate"]["mean_increment_beyond_one_use"] == 3.0
    assert len(targets) == 1024
    assert all(row["target_active"] == 1 for row in targets)
