from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import run_d153a_conditional_value_selection as d153


def passing_counts():
    families = {name: 10 for name in d112.OPPONENTS}
    return {
        "groups": 80,
        "selected_value_sum": 800,
        "oracle_value_sum": 2400,
        "oracle_regret_sum": 1600,
        "strict_positive_selections": 40,
        "harmful_negative_selections": 8,
        "within_ten_of_oracle": 20,
        "selected_control": 32,
        "new_crop_failures": 0,
        "control_worker_three": 72,
        "selected_worker_three": 70,
        "sign_positive_actions": 100,
        "sign_positive_correct": 70,
        "sign_nonpositive_actions": 100,
        "sign_nonpositive_correct": 70,
        "family_value_sum": {name: 100 for name in d112.OPPONENTS},
        "family_groups": families,
    }


def test_metric_view_derives_exact_value_and_safety_rates():
    metrics = d153.metric_view(passing_counts())
    assert metrics["mean_selected_value"] == 10.0
    assert metrics["oracle_value_capture"] == 1 / 3
    assert metrics["mean_oracle_regret"] == 20.0
    assert metrics["sign_balanced_accuracy"] == 0.7
    assert metrics["worst_family_mean_value"] == 10.0


def test_held_gates_preserve_fold_and_family_floors():
    metrics = d153.metric_view(passing_counts())
    folds = [{"metrics": metrics} for _ in range(8)]
    assert all(d153.held_gates(metrics, folds).values())
    folds[2] = {"metrics": {**metrics, "mean_selected_value": -0.01}}
    assert not d153.held_gates(metrics, folds)["every_fold_mean_nonnegative"]


def test_merge_counts_adds_scalar_and_family_counts():
    one = passing_counts()
    merged = d153.merge_counts([one, one])
    assert merged["groups"] == 160
    assert merged["family_value_sum"]["resident"] == 200
    assert merged["family_groups"]["resident"] == 20
