from __future__ import annotations

from cgauto.d11_recipe_fallback_analysis import analyze, validate


def controls() -> list[dict]:
    rows = []
    for seat in range(2):
        rows.append(
            {
                "seed": 0,
                "seat": seat,
                "opponent": "fixture",
                "recipe": 6,
                "margin": 0,
                "workers": 2,
            }
        )
        rows.append(
            {
                "seed": 0,
                "seat": seat,
                "opponent": "fixture",
                "recipe": 7,
                "margin": 10 if seat == 0 else -10,
                "workers": 2 if seat == 0 else 1,
            }
        )
    return rows


def fallback_rows() -> list[dict]:
    rows = []
    for deadline, margin in ((40, 6), (60, 7)):
        for seat in range(2):
            rows.append(
                {
                    "seed": 0,
                    "seat": seat,
                    "opponent": "fixture",
                    "recipe": 7,
                    "fallback_turn": deadline,
                    "margin": margin,
                    "workers": 2,
                    "trained_ms": 2,
                    "trained_cc": 2,
                    "trained_hp": 0,
                    "trained_chop": 2,
                }
            )
    return rows


def test_deadline_tie_window_prefers_earlier_rule(tmp_path):
    fallback_path = tmp_path / "fallback.tsv"
    control_path = tmp_path / "control.tsv"
    fallback_path.write_text("fixture\n")
    control_path.write_text("fixture\n")

    result = analyze(
        fallback_rows(), controls(), fallback_path, control_path
    )

    assert result["selection"]["eligible_deadlines"] == [40, 60]
    assert result["selection"]["selected_deadline"] == 40
    assert result["per_deadline"]["40"]["fallback_activation_rate"] == 1


def test_fallback_validation_requires_all_deadline_cells():
    rows = fallback_rows()
    rows.pop()

    try:
        validate(rows, controls())
    except ValueError as error:
        assert "incomplete fallback sweep" in str(error)
    else:
        raise AssertionError("missing fallback row was accepted")
