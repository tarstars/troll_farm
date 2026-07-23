from cgauto.portfolio_geometry_prospective_gate import (
    evaluate_gate,
    low_branch_equivalence,
)


def game_row(seed: int, policy: str, margin: float) -> dict:
    return {
        "seed": seed,
        "policy": policy,
        "opponent": "race",
        "seat_margins": [margin, margin],
        "paired_margin": margin,
        "seat_wood_edges": [0, 0],
        "paired_wood_edge": 0,
        "policy_scores": [margin, margin],
        "opponent_scores": [0, 0],
        "policy_wood": [0, 0],
        "opponent_wood": [0, 0],
        "policy_command_counts": {"WAIT": 2},
        "opponent_command_counts": {"WAIT": 2},
        "terminal_turns": [10, 10],
    }


def test_low_branch_equivalence_compares_geometry_reference() -> None:
    exact = game_row(1, "portfolio", 2)
    geometry = game_row(1, "geometry", 2)

    result = low_branch_equivalence([exact, geometry], {1})

    assert result["cells"] == 1
    assert result["exact_cells"] == 1
    assert result["passed"] is True


def test_gate_requires_both_branch_equivalences() -> None:
    low = {
        "mean": 2,
        "trimmed_5pct_mean": 1,
        "mean_without_largest": 1,
        "wins": 2,
        "losses": 0,
        "ci95_normal": [0.1, 3.9],
        "worst_decile_mean": 0,
    }
    opponents = {"race": {"mean": 1}}

    passed = evaluate_gate(low, {"passed": True}, {"passed": True}, opponents)
    failed = evaluate_gate(low, {"passed": True}, {"passed": False}, opponents)

    assert passed["promotion_ready"] is True
    assert failed["research_passed"] is False
    assert failed["decision"] == "reject"
