from cgauto.analyze_d160a_resident_capital_windows import (
    game_spec_report,
    max_consecutive,
    training_cost,
)


def _state(turn: int, inventory: list[int], occupied: bool = False) -> dict:
    return {
        "resolved_turn": turn - 1,
        "inventories": [inventory, [0] * 6],
        "units": [
            {
                "id": 0,
                "player": 0,
                "x": 3 if occupied else 2,
                "y": 3 if occupied else 2,
                "carry": [0] * 6,
            },
            {
                "id": 2,
                "player": 0,
                "x": 4,
                "y": 4,
                "carry": [0, 0, 0, 0, 0, 0],
            },
            {
                "id": 1,
                "player": 1,
                "x": 9,
                "y": 9,
                "carry": [0] * 6,
            },
        ],
    }


def test_training_cost_matches_n_two_and_iron_guard() -> None:
    assert training_cost((2, 2, 0, 2), True) == [6, 6, 2, 0, 6, 0]
    assert training_cost((2, 2, 1, 2), True) == [6, 6, 3, 0, 6, 0]
    assert training_cost((2, 3, 0, 2), False) == [6, 11, 2, 0, 0, 0]


def test_max_consecutive_deduplicates_and_splits_windows() -> None:
    assert max_consecutive([]) == 0
    assert max_consecutive([8, 7, 7, 10, 11, 12]) == 3


def test_game_report_separates_stock_from_shack_execution() -> None:
    states = [
        _state(99, [6, 6, 2, 0, 6, 0], occupied=True),
        _state(100, [6, 6, 2, 0, 6, 0]),
        _state(101, [6, 6, 2, 0, 6, 0]),
        _state(102, [5, 6, 2, 0, 6, 0]),
    ]
    report = game_spec_report(
        states,
        seat=0,
        shack=(3, 3),
        has_iron=True,
        spec=(2, 2, 0, 2),
    )
    assert report["stock_affordable_turns"] == [99, 100, 101]
    assert report["executable_turns"] == [100, 101]
    assert report["gate_maximum_consecutive"] == 2
    assert report["closest_state"]["total_deficit"] == 0


def test_game_report_counts_own_carry_as_liquid_only() -> None:
    state = _state(75, [5, 6, 2, 0, 6, 0])
    state["units"][0]["carry"][0] = 1
    report = game_spec_report(
        [state], seat=0, shack=(3, 3), has_iron=True, spec=(2, 2, 0, 2)
    )
    assert report["stock_affordable_turns"] == []
    assert report["liquid_affordable_turns"] == [75]
    assert report["executable_turns"] == []
    assert report["closest_state"]["limiting_resources"] == ["PLUM"]
