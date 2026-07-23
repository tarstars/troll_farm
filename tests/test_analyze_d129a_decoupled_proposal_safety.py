import numpy as np

from cgauto.analyze_d129a_decoupled_proposal_safety import (
    COMPOSITIONS,
    SPECIFICITY_TARGETS,
    safety_threshold,
    select_root_row,
)


def row(slot):
    return {
        "map_seed": "1",
        "seat": "0",
        "opponent": "x",
        "boundary_index": "0",
        "slot": str(slot),
    }


def test_frozen_matrix_has_sixty_cells():
    assert COMPOSITIONS == ("winner_veto", "filter_rank", "safety_rerank")
    assert SPECIFICITY_TARGETS == (0.70, 0.80, 0.90, 0.95, 0.98)
    assert 4 * len(COMPOSITIONS) * len(SPECIFICITY_TARGETS) == 60


def test_safety_threshold_rejects_at_least_target_nonpositive_arms():
    logits = np.asarray([-3.0, -2.0, -1.0, 4.0], dtype=np.float32)
    values = np.asarray([-1.0, 0.0, -2.0, 5.0], dtype=np.float32)
    threshold, calibration = safety_threshold(logits, values, 0.50)
    assert threshold == -2.0
    assert calibration["nonpositive_recall"] == 2 / 3
    assert calibration["positive_recall"] == 1.0


def test_compositions_separate_veto_filter_and_rerank():
    rows = [row(0), row(1)]
    rank = {((1, 0, "x"), 0, 0): 2.0, ((1, 0, "x"), 0, 1): 1.0}
    safety = {((1, 0, "x"), 0, 0): -1.0, ((1, 0, "x"), 0, 1): 1.0}
    assert select_root_row(rows, rank, safety, 0.0, "winner_veto") is None
    assert select_root_row(rows, rank, safety, 0.0, "filter_rank") is rows[1]
    assert select_root_row(rows, rank, safety, 0.0, "safety_rerank") is rows[1]

    safety[((1, 0, "x"), 0, 0)] = 0.5
    assert select_root_row(rows, rank, safety, 0.0, "filter_rank") is rows[0]
    assert select_root_row(rows, rank, safety, 0.0, "safety_rerank") is rows[1]
