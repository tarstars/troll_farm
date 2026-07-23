from cgauto.analyze_d133b_q6_support_semantics import (
    calibration_minimum,
    exact_mechanics_without_support_gate,
    support_summary,
)


def test_support_summary_counts_zero_boundary_as_unsupported_not_invalid(tmp_path):
    path = tmp_path / "baselines.tsv"
    path.write_text("map_seed\tboundary_count\n1\t2\n1\t0\n")
    summary = support_summary(path)
    assert summary["tasks"] == 2
    assert summary["supported_tasks"] == 1
    assert summary["support_rate"] == 0.5


def test_repair_removes_only_support_percentage_gate():
    mechanics = {
        "gates": {
            "complete_unique_arm_grid": True,
            "supported_tasks_at_least_90pct": False,
            "zero_mechanical_failures": True,
        },
        "details": {"supported_tasks": 217},
    }
    repaired = exact_mechanics_without_support_gate(mechanics)
    assert repaired["pass"]
    assert not repaired["descriptive_support_gate"]
    mechanics["gates"]["zero_mechanical_failures"] = False
    assert not exact_mechanics_without_support_gate(mechanics)["pass"]


def test_calibration_minimum_keeps_finite_inactive_ceiling():
    assert calibration_minimum(768) == 646
    assert calibration_minimum(1024) == 861
