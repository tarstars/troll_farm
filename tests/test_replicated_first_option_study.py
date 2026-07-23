from __future__ import annotations

import csv
from pathlib import Path

import pytest

from cgauto.replicated_first_option_study import study


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


def write_grid(path: Path, candidate_deltas: dict[str, int], *, train: str = "TRAIN 1 1 0 1") -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        for model, delta in candidate_deltas.items():
            writer.writerow(
                {
                    "seed": 0,
                    "seat": 0,
                    "model": model,
                    "option": "control",
                    "active": 0,
                    "control_margin": 0,
                    "option_margin": 0,
                    "delta": 0,
                    "first_train": "TRAIN 1 2 0 2",
                    "elapsed_us": 1,
                }
            )
            writer.writerow(
                {
                    "seed": 0,
                    "seat": 0,
                    "model": model,
                    "option": "candidate",
                    "active": 1,
                    "control_margin": 0,
                    "option_margin": delta,
                    "delta": delta,
                    "first_train": train,
                    "elapsed_us": 1,
                }
            )


def test_robust_rule_selects_repeat_stable_positive_option(tmp_path: Path) -> None:
    paths = [tmp_path / f"run-{index}.tsv" for index in range(3)]
    for path in paths:
        write_grid(path, {"a": 5, "b": 3})

    result = study(paths)

    robust = result["rules"]["model_lcb90_minimax"]
    assert robust["full_information"]["selected_cell_count"] == 1
    assert robust["leave_one_repetition_out"]["total_selected_cells"] == 3
    assert robust["leave_one_repetition_out"]["worst_held_model_mean"] > 0


def test_pooled_signal_cannot_pass_model_robust_rule(tmp_path: Path) -> None:
    paths = [tmp_path / f"run-{index}.tsv" for index in range(3)]
    for path in paths:
        write_grid(path, {"large_gain": 100, "consistent_loss": -20})

    result = study(paths)

    assert result["rules"]["model_lcb90_minimax"]["full_information"]["selected_cell_count"] == 0
    assert result["rules"]["pooled_lcb90_floor30_diagnostic"]["full_information"]["selected_cell_count"] == 1
    assert result["discovery_gate"]["passed"] is False


def test_study_rejects_action_changes_across_processes(tmp_path: Path) -> None:
    first = tmp_path / "first.tsv"
    second = tmp_path / "second.tsv"
    write_grid(first, {"a": 5})
    write_grid(second, {"a": 5}, train="TRAIN 2 1 0 1")

    with pytest.raises(ValueError, match="opening action changed"):
        study([first, second])
