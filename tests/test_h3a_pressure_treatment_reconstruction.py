from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chatgpt_1 import h3a_pressure_treatment_reconstruction as h3a


def test_frozen_hashes_and_three_way_exact_reconstruction():
    result = h3a.analyze(compile_sources=False)
    assert result["verdict"] == "TREATMENT_REPRODUCIBLE"
    assert all(result["equality"].values())
    assert result["inputs"]["fallback_sha256"] == h3a.FALLBACK_SHA256
    assert result["inputs"]["treatment_sha256"] == h3a.TREATMENT_SHA256
    assert result["edit_count"] == 7
    assert result["panel_authorized"] is False


def test_direct_and_inverse_are_stable_and_exact():
    fallback = h3a.FALLBACK.read_text()
    treatment = h3a.TREATMENT.read_text()
    direct = h3a.apply_edits(fallback)
    inverse = h3a.remove_edits(treatment)
    assert direct == treatment
    assert inverse == fallback
    assert h3a.apply_edits(fallback) == direct
    assert h3a.remove_edits(treatment) == inverse


def test_every_edit_has_unique_forward_and_reverse_anchor():
    current = h3a.FALLBACK.read_text()
    for edit in h3a.EDITS:
        assert current.count(edit.before) == 1, edit.name
        current = h3a.replace_once(current, edit.before, edit.after, edit.name)
    assert current == h3a.TREATMENT.read_text()

    for edit in reversed(h3a.EDITS):
        assert current.count(edit.after) == 1, edit.name
        current = h3a.replace_once(
            current, edit.after, edit.before, f"inverse:{edit.name}"
        )
    assert current == h3a.FALLBACK.read_text()


def test_archived_generator_is_independent_exact_path():
    assert h3a.archived_generator_output() == h3a.TREATMENT.read_text()


@pytest.mark.parametrize(
    "distance,speed,expected",
    [
        (1, 1, 20.0),
        (6, 1, 20.0),
        (12, 2, 20.0),
        (13, 2, 10.0),
        (7, 1, 10.0),
    ],
)
def test_eta_boundary(distance, speed, expected):
    observed = h3a.dual_value_score(
        10.0,
        tracked_opponent_crop=True,
        tree_target=True,
        reachable_distance_cells=distance,
        movement_speed=speed,
    )
    assert observed == expected


def test_provenance_and_target_eligibility():
    assert h3a.dual_value_score(
        10.0,
        tracked_opponent_crop=False,
        tree_target=True,
        reachable_distance_cells=1,
        movement_speed=1,
    ) == 10.0
    assert h3a.dual_value_score(
        10.0,
        tracked_opponent_crop=True,
        tree_target=False,
        reachable_distance_cells=1,
        movement_speed=1,
    ) == 10.0
    assert h3a.dual_value_score(
        10.0,
        tracked_opponent_crop=True,
        tree_target=True,
        reachable_distance_cells=None,
        movement_speed=1,
    ) == 10.0


def test_semantic_classification_excludes_unrelated_changes():
    result = h3a.analyze(compile_sources=False)
    classification = result["classification"]
    assert classification["provenance"]
    assert classification["original_tree_target_eligibility"]
    assert classification["original_eta_threshold_6"]
    assert classification["score_operation_candidate_plus_equal_candidate"]
    for key in (
        "new_multiplier",
        "new_eta",
        "new_target",
        "new_commitment",
        "harvest_rewrite",
        "scheduler_change",
        "unrelated_bytes",
    ):
        assert classification[key] is False


def test_machine_result_is_deterministic_without_compile():
    first = h3a.analyze(compile_sources=False)
    second = h3a.analyze(compile_sources=False)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_exact_artifacts_compile():
    if shutil.which("rustc") is None:
        pytest.skip("rustc is unavailable in this runtime")
    result = h3a.analyze(compile_sources=True)
    assert len(result["compilation"]) == 2
    assert {row["source"] for row in result["compilation"]} == {
        str(h3a.FALLBACK.relative_to(ROOT)),
        str(h3a.TREATMENT.relative_to(ROOT)),
    }
    assert all(row["output_bytes"] > 0 for row in result["compilation"])
