from cgauto.portfolio_prospective_gate import (
    branch_summary,
    evaluate_gate,
    high_branch_equivalence,
    same_outcome_protocol,
)


def game_row(seed, policy, opponent, margin):
    return {
        "seed": seed,
        "policy": policy,
        "opponent": opponent,
        "delta_vs_live_margin": margin,
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


def test_branch_summary_balances_opponents_and_removes_largest_seed() -> None:
    rows = [
        game_row(1, "portfolio", "a", 2),
        game_row(1, "portfolio", "b", 4),
        game_row(2, "portfolio", "a", 7),
        game_row(2, "portfolio", "b", 9),
    ]

    result = branch_summary(rows, {1, 2})

    assert result["mean"] == 5.5
    assert result["mean_without_largest"] == 3


def test_high_branch_equivalence_detects_changed_result() -> None:
    live = game_row(1, "live", "race", 0)
    exact = game_row(1, "portfolio", "race", 0)
    changed = game_row(2, "portfolio", "race", 1)
    live_two = game_row(2, "live", "race", 0)

    result = high_branch_equivalence([live, exact, live_two, changed], {1, 2})

    assert result["cells"] == 2
    assert result["exact_cells"] == 1
    assert result["passed"] is False


def test_gate_requires_every_research_rule_before_promotion() -> None:
    low = {
        "mean": 2,
        "trimmed_5pct_mean": 1,
        "mean_without_largest": 1,
        "wins": 7,
        "losses": 3,
        "ci95_normal": [0.2, 3.8],
        "worst_decile_mean": 0,
    }
    equivalence = {"passed": True}
    opponents = {name: {"mean": 0.1} for name in ("a", "b")}

    result = evaluate_gate(low, equivalence, opponents)

    assert result["research_passed"] is True
    assert result["promotion_ready"] is True
    assert result["decision"] == "promotion_ready_pending_healthy_arena_control"


def test_worker_count_is_not_an_outcome_protocol_field() -> None:
    first = {"seed_start": 10_000, "candidate_sha256": "abc", "jobs": 8}
    second = {"seed_start": 10_000, "candidate_sha256": "abc", "jobs": 16}

    assert same_outcome_protocol(first, second) is True
    second["seed_start"] = 20_000
    assert same_outcome_protocol(first, second) is False
