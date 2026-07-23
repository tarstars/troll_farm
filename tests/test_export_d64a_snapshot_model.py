"""Tests for the frozen D64a field-snapshot model exporter."""

from __future__ import annotations

import numpy as np

from cgauto.export_d64a_snapshot_model import fit_snapshot_model, nearest_rank


def test_nearest_rank_uses_frozen_ceiling_definition() -> None:
    values = np.asarray([4.0, 1.0, 3.0, 2.0])
    assert nearest_rank(values, 0.5) == 2.0
    assert nearest_rank(values, 0.95) == 4.0


def test_export_reproduces_d63b_snapshot_model() -> None:
    report = fit_snapshot_model()

    assert report["fit"]["feature_count"] == 44
    assert report["fit"]["converged"]
    assert all(report["fit"]["parity"].values())
    assert report["fit"]["metrics"]["validation"]["roc_auc"] > 0.99
    assert report["threshold"] == 0.5
    assert report["support_reference"]["rows"] == 76
    assert len({feature["name"] for feature in report["features"]}) == 44

