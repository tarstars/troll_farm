import csv

from cgauto import analyze_d152a_conditional_second_value as d152
from cgauto import build_d153a_conditional_value_dataset as d153
from cgauto import run_d148a_priority_joint_teacher as d148
from cgauto import run_d151a_conditional_second_counterfactual as d151


def candidate(slot: int) -> dict:
    row = {
        "scenario": "0",
        "map_seed": "9844136",
        "seat": "0",
        "opponent": "resident",
        "source_replica": "17",
        "boundary": "1",
        "stage": "second",
        "chosen_slot": "2",
        "candidate_slot": str(slot),
        "chosen": str(int(slot == 2)),
        "legal_candidates": "3",
    }
    row.update({field: "0.0" for field in d148.STATE_FIELDS})
    row.update({field: "0.0" for field in d148.ACTION_FIELDS})
    row[d148.ACTION_FIELDS[0]] = str(float(slot))
    return row


def label(slot: int, value: int) -> dict:
    row = {field: "0" for field in d152.LABEL_FIELDS}
    row.update(
        {
            "map_seed": "9844136",
            "seat": "0",
            "opponent": "resident",
            "eight_map_fold": "0",
            "target_active": "1",
            "first_boundary": "0",
            "first_slot": "1",
            "second_boundary": "1",
            "candidate_slot": str(slot),
            "terminal_margin": str(10 + value),
            "control_margin": "10",
            "conditional_value": str(value),
            "positive_value": str(int(value > 0)),
        }
    )
    return row


def branch(slot: int, value: int) -> dict:
    row = {field: "0" for field in d151.OUTPUT_FIELDS}
    row.update(
        {
            "map_seed": "9844136",
            "seat": "0",
            "opponent": "resident",
            "first_boundary": "0",
            "first_slot": "1",
            "second_boundary": "1",
            "second_slot": str(slot),
            "margin": str(10 + value),
            "own_score": str(20 + value),
            "opponent_score": "10",
            "own_workers": str(2 + int(slot == 2)),
            "own_created_crops": "1",
        }
    )
    return row


def write_rows(path, fields, rows):
    with path.open("w", newline="") as sink:
        writer = csv.DictWriter(
            sink, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def test_exact_group_join_retains_control_value_and_terminal_safety(tmp_path):
    candidates = tmp_path / "candidates.tsv"
    labels = tmp_path / "labels.tsv"
    branches = tmp_path / "branches.tsv"
    values = {0: 0, 1: -5, 2: 15}
    write_rows(candidates, d148.CANDIDATE_FIELDS, [candidate(slot) for slot in values])
    write_rows(labels, d152.LABEL_FIELDS, [label(slot, value) for slot, value in values.items()])
    write_rows(branches, d151.OUTPUT_FIELDS, [branch(slot, value) for slot, value in values.items()])

    examples, summary = d153.conditional_examples(candidates, labels, branches)
    assert summary["groups"] == 1
    assert summary["actions"] == 3
    assert examples[0]["candidate_slots"].tolist() == [0, 1, 2]
    assert examples[0]["target_values"].tolist() == [0.0, -5.0, 15.0]
    padded = d153.padded_dataset(examples)
    assert padded["action_features"].shape == (1, 3, 379)
    assert padded["target_values"][0, 0] == 0.0
    assert padded["terminal_own_workers"][0, 2] == 3
