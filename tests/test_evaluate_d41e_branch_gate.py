from cgauto.evaluate_d41e_branch_gate import (
    BRANCHES,
    candidate_replicas_equal,
    distribution,
    paired_report,
    rule_select,
)


def terminal(task, margin, own=100, opponent=90, overrides=0, family="resident"):
    return {
        "task_index": task,
        "map_seed": 9_770_000 + task,
        "seat": 0,
        "opponent": family,
        "margin": margin,
        "own_score": own,
        "opponent_score": opponent,
        "overrides": overrides,
    }


def test_rule_boundaries_and_branch_isolation():
    evacuation = BRANCHES.index("evacuation")
    rate = BRANCHES.index("rate")
    assert rule_select(evacuation, 150, 0.020)
    assert rule_select(evacuation, 150, 0.030)
    assert not rule_select(evacuation, 150, 0.03001)
    assert rule_select(rate, 99, 0.280)
    assert not rule_select(rate, 100, 0.300)
    assert not rule_select(rate, 199, 0.300)
    assert rule_select(rate, 200, 0.340)
    assert not rule_select(BRANCHES.index("train"), 20, 0.3)
    assert not rule_select(BRANCHES.index("deficit"), 20, 0.3)


def test_distribution_and_paired_report_are_task_aligned():
    values = distribution([-2, 0, 4, 10])
    assert values["mean"] == 3.0
    assert values["positive_rate"] == 0.5
    baseline = [terminal(0, 10), terminal(1, -20, family="gold_adaptive")]
    candidate = [
        terminal(0, 16, own=105, opponent=89, overrides=1),
        terminal(1, -17, own=101, opponent=88, overrides=0, family="gold_adaptive"),
    ]
    report = paired_report(candidate, baseline)
    assert report["margin_delta"]["mean"] == 4.5
    assert report["own_score_delta"]["mean"] == 3.0
    assert report["changed_episode_margin_delta"]["mean"] == 6.0


def test_candidate_replica_equality_uses_decisions_and_rows():
    base = {
        "summary": {"decision_hash_sha256": "a"},
        "episodes_detail": [terminal(0, 10)],
    }
    assert candidate_replicas_equal(base, base)
    changed = {
        "summary": {"decision_hash_sha256": "b"},
        "episodes_detail": [terminal(0, 10)],
    }
    assert not candidate_replicas_equal(base, changed)
