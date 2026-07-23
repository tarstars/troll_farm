import math

from cgauto.analyze_d34_official_architecture_census import (
    CONTROLLERS,
    INTEGER_FIELDS,
    OPPONENTS,
    analyze,
    pareto_frontier,
    pearson,
    robust_summary,
    validate_grid,
)


def make_row(seed: int, seat: int, opponent: str, controller: str) -> dict:
    row = {field: 0 for field in INTEGER_FIELDS}
    row.update(
        {
            "seed": seed,
            "seat": seat,
            "opponent": opponent,
            "controller": controller,
            "width": 16,
            "height": 8,
            "initial_plants": 16,
            "final_turn": 200,
            "my_score": 100,
            "opponent_score": 100,
            "my_inv5": 25,
            "opponent_inv5": 25,
            "my_workers": 2,
            "opponent_workers": 2,
            "max_my_workers": 2,
            "max_opponent_workers": 2,
        }
    )
    if controller == "private2":
        row.update({"margin": 30, "my_score": 130, "my_inv5": 32})
    return row


def complete_rows(seed_count: int = 2) -> list[dict]:
    return [
        make_row(seed, seat, opponent, controller)
        for seed in range(100, 100 + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for controller in CONTROLLERS
    ]


def test_robust_summary_uses_normal_interval_and_sign_counts() -> None:
    result = robust_summary([-1, 0, 2])
    assert result["n"] == 3
    assert result["mean"] == 1 / 3
    assert (result["wins"], result["ties"], result["losses"]) == (1, 1, 1)
    assert result["ci95_normal"][0] < result["mean"] < result["ci95_normal"][1]


def test_complete_grid_and_frozen_promotion_gate() -> None:
    report = analyze(complete_rows(), seed_start=100, seed_count=2)
    assert report["integrity"]["complete"]
    assert report["development_passers"] == ["private2"]
    assert report["controllers"]["private2"]["passes_all_promotion_gates"]
    assert report["confirmation_authorized"]


def test_grid_reports_ambiguous_plant_attribution_without_double_credit() -> None:
    rows = complete_rows(seed_count=1)
    rows[0]["ambiguous_plants"] = 1
    integrity, _ = validate_grid(rows, seed_start=100, seed_count=1)
    assert integrity["complete"]
    assert integrity["ambiguous_plants"] == 1
    assert integrity["ambiguous_plants_reported_separately"]


def test_pareto_frontier_maximizes_own_and_minimizes_opponent_score() -> None:
    def point(own: float, opponent: float) -> dict:
        return {
            "paired_vs_resident": {
                "own_score": {"mean": own},
                "opponent_score": {"mean": opponent},
            }
        }

    analyses = {
        "resident": point(0, 0),
        "productive": point(30, 20),
        "dominated": point(20, 25),
        "suppressive": point(-5, -10),
    }
    assert pareto_frontier(analyses) == ["productive", "resident", "suppressive"]


def test_pearson_handles_linear_and_constant_inputs() -> None:
    assert math.isclose(pearson([1, 2, 3], [2, 4, 6]), 1)
    assert pearson([1, 1, 1], [2, 4, 6]) is None
