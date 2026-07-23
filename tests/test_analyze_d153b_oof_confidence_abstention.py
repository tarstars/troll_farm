import numpy as np

from cgauto import analyze_d153b_oof_confidence_abstention as d153b
from tests.test_run_d153a_conditional_value_selection import passing_counts
from cgauto import run_d153a_conditional_value_selection as d153a


def test_threshold_selection_abstains_and_preserves_stable_zero_tie():
    scores = np.asarray(
        [[0.0, 0.0, -1.0], [0.0, 4.0, 6.0], [0.0, 8.0, 7.0]],
        dtype=np.float64,
    )
    valid = np.ones_like(scores, dtype=np.bool_)
    assert d153b.selected_actions(scores, valid, 0.0).tolist() == [0, 2, 1]
    assert d153b.selected_actions(scores, valid, 5.0).tolist() == [0, 2, 1]
    assert d153b.selected_actions(scores, valid, 7.0).tolist() == [0, 0, 1]


def test_diagnostic_gates_require_nontrivial_high_precision_support():
    metrics = d153a.metric_view(passing_counts())
    folds = {str(index): 10.0 for index in range(8)}
    assert all(d153b.diagnostic_gates(metrics, folds).values())
    weak = {**metrics, "selected_control_rate": 0.95}
    gates = d153b.diagnostic_gates(weak, folds)
    assert not gates["noncontrol_selection_rate_at_least_10pct"]
