import csv

from cgauto import analyze_d148a_priority_joint_teacher as d148
from cgauto import build_d149a_joint_two_stage_dataset as d149
from cgauto import run_d148a_priority_joint_teacher as runner


def target(active: int) -> dict:
    row = {field: "0" for field in d148.TARGET_FIELDS}
    row.update(
        {
            "map_seed": "9844136",
            "seat": "0",
            "opponent": "resident",
            "eight_map_fold": "0",
            "first_boundary": "0",
            "first_slot": "1",
            "second_boundary": "1",
            "second_slot": "2",
            "target_active": str(active),
        }
    )
    return row


def candidate(boundary: int, stage: str, slot: int, chosen_slot: int) -> dict:
    row = {
        "scenario": "0",
        "map_seed": "9844136",
        "seat": "0",
        "opponent": "resident",
        "source_replica": "17",
        "boundary": str(boundary),
        "stage": stage,
        "chosen_slot": str(chosen_slot),
        "candidate_slot": str(slot),
        "chosen": str(int(slot == chosen_slot)),
        "legal_candidates": "3",
    }
    row.update({field: "0.0" for field in runner.STATE_FIELDS})
    row.update({field: "0.0" for field in runner.ACTION_FIELDS})
    if slot:
        row[runner.ACTION_FIELDS[0]] = str(float(slot))
    return row


def write_fixture(tmp_path, active: int):
    targets = tmp_path / "targets.tsv"
    with targets.open("w", newline="") as sink:
        writer = csv.DictWriter(
            sink, fieldnames=d148.TARGET_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerow(target(active))
    candidates = tmp_path / "candidates.tsv"
    rows = []
    for boundary, stage, chosen in ((0, "first", 1), (1, "second", 2)):
        rows.extend(candidate(boundary, stage, slot, chosen) for slot in (0, 1, 2))
    with candidates.open("w", newline="") as sink:
        writer = csv.DictWriter(
            sink,
            fieldnames=runner.CANDIDATE_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return candidates, targets


def test_active_trajectory_keeps_both_ranked_actions(tmp_path):
    candidates, targets = write_fixture(tmp_path, 1)
    examples, summary = d149.structural_examples(candidates, targets)
    assert len(examples) == 2
    assert [row["rank_target"] for row in examples] == [0, 1]
    assert summary["gate_act_groups"] == 2
    padded = d149.padded_dataset(examples)
    assert padded["action_features"].shape == (2, 2, 379)


def test_inactive_trajectory_excludes_post_rejection_state(tmp_path):
    candidates, targets = write_fixture(tmp_path, 0)
    examples, summary = d149.structural_examples(candidates, targets)
    assert len(examples) == 1
    assert examples[0]["gate_target"] is False
    assert examples[0]["rank_target"] == -1
    assert summary["excluded_off_policy_groups"] == 1
