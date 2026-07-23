from __future__ import annotations

import csv
from pathlib import Path

import pytest

from cgauto.robust_option_repeat_audit import audit


FIELDS = [
    "seed",
    "seat",
    "model",
    "option",
    "active",
    "control_margin",
    "option_margin",
    "delta",
    "first_train",
    "elapsed_us",
]


def write_grid(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def row(model: str, option: str, control: int, margin: int) -> dict:
    return {
        "seed": 0,
        "seat": 0,
        "model": model,
        "option": option,
        "active": int(option != "control"),
        "control_margin": control,
        "option_margin": margin,
        "delta": margin - control,
        "first_train": "TRAIN 1 1 0 1" if option != "control" else "TRAIN 1 2 0 2",
        "elapsed_us": 1,
    }


def test_audit_separates_exact_and_process_sensitive_models(tmp_path: Path) -> None:
    reference = tmp_path / "reference.tsv"
    repeat = tmp_path / "repeat.tsv"
    reference_rows = [
        row("stable", "control", 10, 10),
        row("stable", "candidate", 10, 15),
        row("changing", "control", 20, 20),
        row("changing", "candidate", 20, 25),
    ]
    repeat_rows = [dict(source) for source in reference_rows]
    repeat_rows[-2].update(control_margin=30, option_margin=30)
    repeat_rows[-1].update(control_margin=30, option_margin=25, delta=-5)
    write_grid(reference, reference_rows)
    write_grid(repeat, repeat_rows)

    result = audit(reference, repeat)

    assert result["classification"]["terminal_exact_models"] == ["stable"]
    assert result["classification"]["process_sensitive_models"] == ["changing"]
    assert result["by_model"]["changing"]["terminal_exact_count"] == 0
    assert result["by_model"]["changing"]["delta_strict_sign_flip_count"] == 1
    assert result["overall"]["action_exact_count"] == 4
    assert result["selector_repeatability"]["strict_expanded"]["decision_changed_count"] == 1


def test_audit_allows_repeat_to_be_a_complete_subset(tmp_path: Path) -> None:
    reference = tmp_path / "reference.tsv"
    repeat = tmp_path / "repeat.tsv"
    overlap = [row("stable", "control", 10, 10), row("stable", "candidate", 10, 15)]
    extra = dict(row("stable", "control", 4, 4), seed=1)
    extra_candidate = dict(row("stable", "candidate", 4, 5), seed=1)
    write_grid(reference, overlap + [extra, extra_candidate])
    write_grid(repeat, overlap)

    result = audit(reference, repeat)

    assert result["reference_rows_total"] == 4
    assert result["overlap_rows"] == 2
    assert result["overlap_cells"] == 1


def test_audit_rejects_repeat_only_rows(tmp_path: Path) -> None:
    reference = tmp_path / "reference.tsv"
    repeat = tmp_path / "repeat.tsv"
    write_grid(reference, [row("stable", "control", 10, 10)])
    write_grid(repeat, [dict(row("stable", "control", 10, 10), seed=9)])

    with pytest.raises(ValueError, match="absent from reference"):
        audit(reference, repeat)
