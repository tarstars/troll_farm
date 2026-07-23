from cgauto.surplus_workforce_study import affordability, summarize


def test_affordability_reports_per_resource_deficits() -> None:
    result = affordability([2, 3, 1, 99, 0, 0], (1, 1, 0, 1))

    assert result["cost"] == [3, 3, 2, 3]
    assert result["deficits"] == [1, 0, 1, 3]
    assert result["total_deficit"] == 5
    assert result["affordable"] is False


def test_summary_uses_each_sides_best_observed_state() -> None:
    def observation(turn: int, deficit: int) -> dict:
        return {
            "turn": turn,
            "specs": {
                name: {
                    "cost": [3, 3, 2, 3],
                    "inventory": [0, 0, 0, 0],
                    "deficits": [deficit, 0, 0, 0],
                    "total_deficit": deficit,
                    "affordable": deficit == 0,
                }
                for name in (
                    "minimal_wood_1101",
                    "fast_wood_2101",
                    "carry_wood_1201",
                    "live_wood_2202",
                    "minimal_hybrid_1111",
                )
            },
        }

    rows = [
        {
            "seed": 1,
            "seat": 0,
            "first_two_worker_turn": 10,
            "observations": [observation(10, 3), observation(11, 0)],
        },
        {
            "seed": 1,
            "seat": 1,
            "first_two_worker_turn": None,
            "observations": [],
        },
    ]

    result = summarize(rows)

    assert result["sides_reaching_two_workers"] == 1
    assert result["by_spec"]["minimal_wood_1101"]["sides_with_affordable_window"] == 1
    assert result["by_spec"]["minimal_wood_1101"]["minimum_total_deficit"] == 0
