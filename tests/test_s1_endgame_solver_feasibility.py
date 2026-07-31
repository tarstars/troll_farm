from __future__ import annotations

import copy
from itertools import product

from cgauto.s1_endgame_solver_feasibility import (
    endpoint_options,
    movement_outcome_summary,
    resolve_player_positions,
    root_group_summary,
    structural_classification,
)
from sim.engine import apply_moves
from sim.state import GameState, SimUnit


def _game(units):
    width, height = 5, 4
    shacks = [(0, 3), (4, 0)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    return GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0] * 6, [0] * 6],
        units=units,
        plants=[],
        scores=[0, 0],
        turn=251,
        next_id=max(unit.id for unit in units) + 1,
    )


def _unit(unit_id, player, x, y, speed=1):
    return SimUnit(
        unit_id,
        player,
        x,
        y,
        speed,
        1,
        1,
        1,
        [0] * 6,
    )


def _engine_positions(game, player, targets):
    cloned = copy.deepcopy(game)
    units = sorted(
        (unit for unit in cloned.units if unit.player == player),
        key=lambda unit: unit.id,
    )
    intents = {
        unit.id: target
        for unit, target in zip(units, targets, strict=True)
        if target != unit.pos
    }
    apply_moves(cloned, intents)
    return tuple(
        (unit.id, unit.x, unit.y)
        for unit in sorted(
            (unit for unit in cloned.units if unit.player == player),
            key=lambda unit: unit.id,
        )
    )


def test_endpoint_options_are_exact_direct_speed_ball():
    game = _game([_unit(1, 0, 2, 2, speed=2), _unit(2, 1, 4, 1)])

    options = endpoint_options(game, game.units[0])

    assert game.units[0].pos in options
    assert (2, 0) in options
    assert (4, 2) in options
    assert (0, 2) in options
    assert all(
        abs(x - 2) + abs(y - 2) <= 2 for x, y in options
    )


def test_position_resolver_matches_engine_for_all_small_vectors():
    game = _game(
        [
            _unit(1, 0, 1, 1),
            _unit(2, 0, 2, 1),
            _unit(3, 1, 4, 1),
        ]
    )
    units = sorted(
        (unit for unit in game.units if unit.player == 0),
        key=lambda unit: unit.id,
    )
    choices = [endpoint_options(game, unit) for unit in units]

    for targets in product(*choices):
        assert resolve_player_positions(units, targets) == _engine_positions(
            game, 0, targets
        )


def test_position_resolver_handles_swap_and_contested_destination():
    units = [_unit(1, 0, 1, 1), _unit(2, 0, 2, 1)]

    assert resolve_player_positions(units, ((2, 1), (1, 1))) == (
        (1, 2, 1),
        (2, 1, 1),
    )
    assert resolve_player_positions(units, ((1, 2), (1, 2))) == (
        (1, 1, 1),
        (2, 1, 2),
    )


def test_movement_summary_deduplicates_post_collision_positions():
    game = _game(
        [
            _unit(1, 0, 1, 1),
            _unit(2, 0, 2, 1),
            _unit(3, 1, 4, 1),
        ]
    )

    summary = movement_outcome_summary(game, 0)

    assert summary["movement_intent_vectors"] > 0
    assert (
        summary["distinct_position_outcomes"]
        <= summary["movement_intent_vectors"]
    )
    assert summary["endpoint_option_counts"] == [
        len(endpoint_options(game, unit))
        for unit in sorted(game.units[:2], key=lambda unit: unit.id)
    ]


def test_root_group_summary_preserves_reach_and_branch_extremes():
    rows = [
        {
            "turn": 251,
            "opponent": "motion",
            "joint_movement_only_state_outcomes": 100,
            "own_movement_outcomes": 10,
            "opponent_movement_outcomes": 10,
            "unit_counts": [2, 2],
        },
        {
            "turn": 251,
            "opponent": "taskplan",
            "joint_movement_only_state_outcomes": 10_000,
            "own_movement_outcomes": 100,
            "opponent_movement_outcomes": 100,
            "unit_counts": [2, 3],
        },
    ]

    summary = root_group_summary(rows, 251)

    assert summary["root_count"] == 2
    assert summary["joint_movement_outcomes"]["minimum"] == 100
    assert summary["joint_movement_outcomes"]["maximum"] == 10_000
    assert summary["joint_movement_outcomes"]["above_4096"] == 1
    assert summary["family_root_counts"]["motion"] == 1


def test_classification_keeps_full_and_restricted_objects_separate():
    result = structural_classification()

    assert result["verdict"] == "FULL_EXACT_INFEASIBLE"
    assert result["objects"]["full_simultaneous_game"][
        "distinct_from_closed_candidate_interfaces"
    ]
    assert not result["objects"]["known_policy_continuation"][
        "bot_session_forkable"
    ]
    assert not result["objects"]["resident_candidate_restriction"]["novel"]
