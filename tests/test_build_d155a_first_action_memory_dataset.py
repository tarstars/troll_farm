import csv

from cgauto import analyze_d148a_priority_joint_teacher as d148_analysis
from cgauto import analyze_d152a_conditional_second_value as d152
from cgauto import build_d155a_first_action_memory_dataset as d155
from cgauto import run_d148a_priority_joint_teacher as d148
from cgauto import run_d151a_conditional_second_counterfactual as d151
from tests.test_build_d149a_joint_two_stage_dataset import target
from tests.test_build_d153a_conditional_value_dataset import branch, candidate, label, write_rows


def test_selected_first_action_is_joined_exactly_into_second_group(tmp_path):
    candidates = tmp_path / "candidates.tsv"
    labels = tmp_path / "labels.tsv"
    branches = tmp_path / "branches.tsv"
    targets = tmp_path / "targets.tsv"
    first_rows = []
    for slot in (0, 1, 2):
        row = candidate(slot)
        row.update(
            {
                "boundary": "0",
                "stage": "first",
                "chosen_slot": "1",
                "chosen": str(int(slot == 1)),
            }
        )
        row[d148.ACTION_FIELDS[0]] = str(float(slot + 10))
        first_rows.append(row)
    second_rows = [candidate(slot) for slot in (0, 1, 2)]
    write_rows(candidates, d148.CANDIDATE_FIELDS, first_rows + second_rows)
    values = {0: 0, 1: -5, 2: 15}
    write_rows(
        labels,
        d152.LABEL_FIELDS,
        [label(slot, value) for slot, value in values.items()],
    )
    write_rows(
        branches,
        d151.OUTPUT_FIELDS,
        [branch(slot, value) for slot, value in values.items()],
    )
    with targets.open("w", newline="") as sink:
        writer = csv.DictWriter(
            sink,
            fieldnames=d148_analysis.TARGET_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(target(1))

    examples, summary = d155.memory_examples(
        candidates, labels, branches, targets
    )
    assert summary["first_action_groups"] == 1
    assert summary["nonzero_first_slots"] == 1
    assert examples[0]["first_slot"] == 1
    assert examples[0]["first_action_features"][0] == 11.0
    padded = d155.padded_dataset(examples)
    assert padded["first_action_features"].shape == (1, 379)
    assert padded["first_slots"].tolist() == [1]
