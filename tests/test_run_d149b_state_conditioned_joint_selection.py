from cgauto import run_d149a_joint_two_stage_selection as d149a
from cgauto import run_d149b_state_conditioned_joint_selection as d149b


def test_d149b_reuses_exact_d149a_metric_gates():
    counts = __import__(
        "tests.test_run_d149a_joint_two_stage_selection",
        fromlist=["passing_counts"],
    ).passing_counts()
    metrics = d149a.metric_view(counts)
    folds = [{"metrics": metrics} for _ in range(8)]
    assert all(d149a.held_gates(metrics, folds).values())
    assert d149b.trainer.PARAMETERS == 7_810
