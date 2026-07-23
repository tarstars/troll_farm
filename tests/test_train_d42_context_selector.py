import numpy as np

from cgauto.train_d42_context_selector import (
    FEATURES,
    SCALARS,
    canonical_hash,
    discovery_metrics,
)


def test_d42_compact_model_has_frozen_size():
    assert FEATURES == 194
    assert SCALARS == 1570


def test_d42_discovery_gates_context_coverage_and_precision():
    size = 800
    data = {
        "margin_delta": np.full(size, 20.0),
        "residual_gap": np.linspace(0.21, 0.33, size),
        "phase": np.arange(size) % 2,
        "fold": np.arange(size) % 8,
        "opponent": np.arange(size) % 8,
    }
    scores = -np.arange(size, dtype=np.float32)
    report = discovery_metrics(data, scores, -399.0)
    assert report["selected_rows"] == 400
    assert report["below_0280"] >= 160
    assert report["pass"]


def test_d42_canonical_hash_excludes_only_elapsed(tmp_path):
    left = tmp_path / "left.tsv"
    right = tmp_path / "right.tsv"
    left.write_text("a\telapsed_us\tb\n1\t10\t2\n")
    right.write_text("a\telapsed_us\tb\n1\t99\t2\n")
    assert canonical_hash(left) == canonical_hash(right)
