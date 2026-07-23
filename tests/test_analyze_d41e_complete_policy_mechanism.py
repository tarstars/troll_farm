from cgauto.analyze_d41e_complete_policy_mechanism import analyze


def row(task, margin, overrides, branch, phase):
    return {
        "task_index": task,
        "margin": margin,
        "overrides": overrides,
        "branch_overrides": {
            "train": 0,
            "deficit": 0,
            "evacuation": int(branch in {"evacuation", "both"}),
            "rate": int(branch in {"rate", "both"}),
        },
        "phase_overrides": {
            "early": int(phase in {"early", "both"}),
            "middle": 0,
            "late": int(phase in {"late", "both"}),
        },
    }


def test_analysis_separates_coverage_from_repeat_interaction():
    baseline = [row(index, 0, 0, "rate", "early") for index in range(6)]
    candidate = [
        row(0, 0, 0, "rate", "early"),
        row(1, 10, 1, "rate", "early"),
        row(2, 8, 1, "rate", "late"),
        row(3, -2, 1, "evacuation", "early"),
        row(4, 22, 2, "rate", "both"),
        row(5, 36, 3, "rate", "both"),
    ]
    report = analyze(candidate, baseline)
    assert report["changed_episodes"] == 5
    assert report["groups"]["branch_pattern|rate"]["mean"] == 19.0
    assert report["groups"]["branch_pattern|evacuation"]["mean"] == -2.0
    assert report["diagnosis"]["evacuation_is_not_prospectively_positive"]
    assert report["diagnosis"]["multi_override_means_nondecreasing"]
