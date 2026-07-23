from cgauto import run_d149a_joint_two_stage_selection as d149


def passing_counts():
    return {
        "groups": 100,
        "rank_groups": 40,
        "rank_correct": 8,
        "rank_chance_sum": 2.5,
        "first_rank_groups": 20,
        "first_rank_correct": 4,
        "first_rank_chance_sum": 1.25,
        "second_rank_groups": 20,
        "second_rank_correct": 4,
        "second_rank_chance_sum": 1.25,
        "act_groups": 40,
        "act_correct": 24,
        "wait_groups": 60,
        "wait_correct": 36,
        "first_joint_correct": 3,
        "second_joint_correct": 3,
        "active_tasks": 20,
        "both_actions_exact_tasks": 2,
        "full_logged_exact_active_tasks": 1,
        "inactive_tasks": 30,
        "inactive_no_false_act_tasks": 10,
    }


def test_metric_view_derives_stage_gate_and_task_rates():
    metrics = d149.metric_view(passing_counts())
    assert metrics["rank_accuracy"] == 0.2
    assert metrics["rank_lift"] == 3.2
    assert metrics["first_rank_accuracy"] == 0.2
    assert metrics["gate_balanced_accuracy"] == 0.6
    assert metrics["both_actions_exact_rate"] == 0.1
    assert metrics["inactive_no_false_act_rate"] == 1 / 3


def test_held_gates_accept_frozen_thresholds_and_preserve_fold_floor():
    metrics = d149.metric_view(passing_counts())
    folds = [{"metrics": metrics} for _ in range(8)]
    assert all(d149.held_gates(metrics, folds).values())
    folds[3] = {"metrics": {**metrics, "gate_balanced_accuracy": 0.49}}
    gates = d149.held_gates(metrics, folds)
    assert not gates["every_fold_gate_balanced_at_least_50pct"]


def test_merge_counts_is_additive():
    one = passing_counts()
    merged = d149.merge_counts([one, one])
    assert merged["groups"] == 200
    assert merged["rank_chance_sum"] == 5.0
