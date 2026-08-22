from cgauto.rating_system_dynamics import (
    BattleObservation,
    Epoch,
    GameAgent,
    GameSummary,
    complete_epoch,
    cross_validate_linear,
    metrics,
    parse_time,
)


def test_complete_epoch_requires_both_boundaries_in_one_source_list() -> None:
    epochs = [
        Epoch(7, 20.0, (1, 2)),
        Epoch(7, 21.0, (3, 4)),
        Epoch(7, 22.0, (5, 6)),
    ]
    complete = BattleObservation(
        "s", 7, "2026-01-01T00:00:00Z", "a", frozenset(range(1, 7))
    )
    clipped = BattleObservation(
        "s", 7, "2026-01-01T00:00:00Z", "b", frozenset((3, 4, 5))
    )
    assert complete_epoch(1, epochs, [complete])
    assert not complete_epoch(1, epochs, [clipped])
    assert not complete_epoch(0, epochs, [complete])


def test_leave_agent_out_linear_fit_does_not_leak_held_agent() -> None:
    rows = [
        {"agent_id": agent, "score_delta": 0.25 * net, "net_wins": net}
        for agent in range(8)
        for net in (-2, -1, 1, 2)
    ]
    result = cross_validate_linear(rows, ("net_wins",))
    assert result["validation"]["mae"] < 1e-8
    assert abs(result["coefficients"][1] - 0.25) < 1e-8


def test_metrics_preserve_signed_bias_and_zero_baseline() -> None:
    result = metrics([1.0, -1.0], [1.5, -0.5])
    assert result["mae"] == 0.5
    assert result["bias"] == 0.5
    assert result["zero_change_baseline_mae"] == 1.0


def test_numeric_millisecond_timestamp_matches_iso() -> None:
    assert parse_time(1767225600000) == parse_time("2026-01-01T00:00:00Z")


def test_complete_epoch_rejects_an_unindexed_game_inside_bracket() -> None:
    epochs = [
        Epoch(7, 20.0, (1,)),
        Epoch(7, 21.0, (3,)),
        Epoch(7, 22.0, (5,)),
    ]
    observation = BattleObservation(
        "s",
        7,
        "2026-01-01T00:00:00Z",
        "a",
        frozenset((1, 3, 4, 5)),
        (5, 4, 3, 1),
    )
    agent = GameAgent(7, 21.0, 0, 1.0, (20.0,))
    games = {
        1: GameSummary(1, "1", {7: agent}),
        3: GameSummary(3, "3", {7: agent}),
        5: GameSummary(5, "5", {7: agent}),
    }
    assert not complete_epoch(1, epochs, [observation], games)
