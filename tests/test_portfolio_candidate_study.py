from cgauto.portfolio_candidate_study import (
    compare_branch_row,
    merge_with_live,
    seed_balanced_split,
)


def row(margin: float) -> dict:
    return {
        "seat_margins": [margin, margin],
        "paired_margin": margin,
        "seat_wood_edges": [1, 1],
        "paired_wood_edge": 1,
        "policy_scores": [2, 2],
        "opponent_scores": [1, 1],
        "policy_wood": [1, 1],
        "opponent_wood": [0, 0],
        "policy_command_counts": {"CHOP": 2},
        "opponent_command_counts": {"WAIT": 2},
        "terminal_turns": [10, 10],
    }


def test_branch_comparison_reports_only_changed_fields() -> None:
    candidate = row(1)
    expected = row(1)
    expected["policy_scores"] = [3, 3]

    assert compare_branch_row(candidate, expected) == ["policy_scores"]


def test_merge_attaches_candidate_delta_to_live_control() -> None:
    live = {**row(2), "seed": 1, "policy": "live", "opponent": "race"}
    candidate = {**row(5), "seed": 1, "policy": "portfolio", "opponent": "race"}
    control = {"rows": [live]}

    merged = merge_with_live(control, [candidate])

    portfolio = next(item for item in merged if item["policy"] == "portfolio")
    assert portfolio["delta_vs_live_margin"] == 3
    assert portfolio["delta_vs_live_wood"] == 0


def test_seed_balanced_split_averages_opponents_before_seeds() -> None:
    rows = [
        {"seed": 0, "delta_vs_live_margin": 2},
        {"seed": 0, "delta_vs_live_margin": 4},
        {"seed": 1, "delta_vs_live_margin": 6},
        {"seed": 1, "delta_vs_live_margin": 8},
    ]

    result = seed_balanced_split(rows)

    assert result["train_even_seeds"]["mean"] == 3
    assert result["test_odd_seeds"]["mean"] == 7
