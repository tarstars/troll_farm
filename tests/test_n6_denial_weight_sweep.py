import pytest

from cgauto.n6_denial_weight_sweep import (
    CONFIRMATION_MAPS,
    CONFIRMATION_START,
    DEVELOPMENT_MAPS,
    DEVELOPMENT_START,
    FAMILIES,
    SEATS,
    TARGET_LINE,
    analyze_confirmation_rows,
    analyze_development_rows,
    choose_development_arm,
    materialize_source,
    module_compatible_source,
)


def synthetic_rows(low_margin=2, high_margin=-1, low_directional=True):
    rows = []
    for seed in range(DEVELOPMENT_START, DEVELOPMENT_START + DEVELOPMENT_MAPS):
        for seat in range(SEATS):
            for family in range(FAMILIES):
                for arm, margin in (
                    ("control", 0),
                    ("low", low_margin),
                    ("high", high_margin),
                ):
                    rows.append(
                        {
                            "map_seed": str(seed),
                            "seat": str(seat),
                            "opponent_index": str(family),
                            "arm": arm,
                            "margin": str(margin),
                            "own_score": str(100 + margin),
                            "opponent_score": "100",
                            "done": "1",
                            "critical_issues": "0",
                            "unclassified_issues": "0",
                            "legality_issues": "0",
                            "command_diverged": "1",
                            "first_divergence_common_state": "1",
                            "first_both_focus": "1",
                            "first_directional_comparable": "1",
                            "first_directional": str(
                                int(arm == "low" and low_directional)
                            ),
                            "opponent_command_mismatch": "0",
                            "legality_reason_counts": "",
                        }
                    )
    return rows


def synthetic_confirmation_rows():
    rows = []
    for seed in range(CONFIRMATION_START, CONFIRMATION_START + CONFIRMATION_MAPS):
        for seat in range(SEATS):
            for family in range(FAMILIES):
                for arm in ("control", "high"):
                    rows.append(
                        {
                            "map_seed": str(seed),
                            "seat": str(seat),
                            "opponent_index": str(family),
                            "opponent": str(family),
                            "arm": arm,
                            "margin": "0",
                            "own_score": "100",
                            "opponent_score": "100",
                            "done": "1",
                            "critical_issues": "0",
                            "unclassified_issues": "0",
                            "legality_issues": "0",
                            "legality_reason_counts": "",
                            "command_diverged": str(int(arm == "high")),
                            "first_divergence_common_state": "1",
                            "first_both_focus": "0",
                            "first_directional_comparable": str(int(arm == "high")),
                            "first_directional": str(int(arm == "high")),
                            "opponent_command_mismatch": "0",
                        }
                    )
    return rows


def test_materializer_changes_only_exact_scalar():
    source = f"before\n{TARGET_LINE}\nafter\n"
    assert materialize_source(source, 900) == source
    assert materialize_source(source, 450) == source.replace("900.0", "450.0")
    assert materialize_source(source, 1800) == source.replace("900.0", "1800.0")


@pytest.mark.parametrize("source", ["nothing", f"{TARGET_LINE}\n{TARGET_LINE}"])
def test_materializer_fails_closed_on_missing_or_duplicate_anchor(source):
    with pytest.raises(ValueError):
            materialize_source(source, 450)


def test_module_normalization_removes_only_crate_allow():
    source = "#![allow(dead_code, unused_imports)]\nbody\n"
    assert module_compatible_source(source) == "body\n"


def test_development_selects_only_arm_passing_every_gate():
    result = analyze_development_rows(synthetic_rows())
    assert result["source_integrity"]
    assert result["selected_arm"] == "low"
    assert result["arms"]["low"]["eligible"]
    assert not result["arms"]["high"]["eligible"]


def test_directional_failure_closes_development():
    result = analyze_development_rows(synthetic_rows(low_directional=False))
    assert result["verdict"] == "CLOSED_AT_DEVELOPMENT"
    assert result["selected_arm"] is None


def test_directional_denominator_uses_orderable_focus_transitions():
    rows = synthetic_rows()
    for row in rows:
        if row["arm"] == "low":
            row["first_both_focus"] = "0"
            row["first_directional_comparable"] = "1"
            row["first_directional"] = "1"
    result = analyze_development_rows(rows)
    low = result["arms"]["low"]
    assert low["common_state_directionally_comparable_divergences"] == 512
    assert low["eligible"]


def test_opponent_command_mismatch_fails_integrity():
    rows = synthetic_rows()
    next(row for row in rows if row["arm"] == "low")[
        "opponent_command_mismatch"
    ] = "1"
    result = analyze_development_rows(rows)
    assert not result["arms"]["low"]["gates"]["issue_and_terminal_integrity"]


def test_incomplete_matrix_is_unidentifiable():
    result = analyze_development_rows(synthetic_rows()[:-1])
    assert result["verdict"] == "UNIDENTIFIABLE"
    assert not result["source_integrity"]


def test_tie_selection_prefers_smaller_absolute_perturbation():
    summaries = [
        {"arm": "high", "weight": 1800, "eligible": True, "paired_mean_margin_delta": 3},
        {"arm": "low", "weight": 450, "eligible": True, "paired_mean_margin_delta": 3},
    ]
    assert choose_development_arm(summaries) == "low"


def test_confirmation_ratio_gates_are_exact_when_control_baseline_is_zero():
    rows = synthetic_confirmation_rows()
    result = analyze_confirmation_rows(rows, "high", bootstrap_reps=2)
    assert result["gates"]["noncritical_issues_le_1_10x"]
    assert result["gates"]["negative_mass_le_1_05x"]
    assert result["gates"]["own_score_delta_ge_minus_5"]

    first_high = next(row for row in rows if row["arm"] == "high")
    first_high["legality_issues"] = "1"
    first_high["margin"] = "-1"
    first_high["own_score"] = "99"
    result = analyze_confirmation_rows(rows, "high", bootstrap_reps=2)
    assert not result["gates"]["noncritical_issues_le_1_10x"]
    assert not result["gates"]["negative_mass_le_1_05x"]
