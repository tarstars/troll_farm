from __future__ import annotations

from cgauto.norxondor_workforce_ladder_study import (
    evaluate_ladder,
    infer_ladder,
    proposed_spec,
)


def occurrence(game_id: int, specs: list[tuple[int, int, int, int]]) -> dict:
    return {
        "game_id": game_id,
        "training_events": [
            {"n_before": ordinal, "spec": list(spec)}
            for ordinal, spec in enumerate(specs, 1)
        ],
    }


def decision(
    game_id: int,
    turn: int,
    n: int,
    inventory: list[int],
    actual: tuple[int, int, int, int] | None,
) -> dict:
    return {
        "game_id": game_id,
        "turn": turn,
        "n": n,
        "inventory": inventory,
        "has_iron": True,
        "actual": actual,
    }


def test_infer_ladder_excludes_held_games() -> None:
    occurrences = [
        occurrence(1, [(2, 2, 1, 1), (2, 3, 1, 2)]),
        occurrence(2, [(3, 3, 2, 2), (4, 5, 2, 2)]),
    ]

    ladder = infer_ladder(occurrences, {1})

    assert ladder[1] == {"base": (2, 2, 1, 1), "cap": (2, 2, 1, 1)}
    assert ladder[2] == {"base": (2, 3, 1, 2), "cap": (2, 3, 1, 2)}


def test_proposed_spec_waits_for_base_then_clamps_max_affordable() -> None:
    ladder = {1: {"base": (2, 2, 1, 1), "cap": (3, 3, 2, 2)}}
    waiting = decision(1, 1, 1, [4, 5, 2, 0, 2, 0], None)
    funded = decision(1, 2, 1, [20, 10, 10, 0, 17, 0], (3, 3, 2, 2))

    assert proposed_spec(waiting, ladder) is None
    assert proposed_spec(funded, ladder) == (3, 3, 2, 2)


def test_evaluate_ladder_counts_exact_trigger_specs_and_sequences() -> None:
    ladder = {1: {"base": (2, 2, 1, 1), "cap": (3, 3, 2, 2)}}
    rows = [
        decision(1, 1, 1, [4, 4, 1, 0, 1, 0], None),
        decision(1, 2, 1, [5, 5, 2, 0, 2, 0], (2, 2, 1, 1)),
        decision(2, 1, 1, [4, 4, 1, 0, 1, 0], None),
    ]

    metrics = evaluate_ladder(rows, ladder)

    assert metrics["trigger_exact"] == 3
    assert metrics["exact_specs"] == 1
    assert metrics["false_positive_events"] == 0
    assert metrics["missed_events"] == 0
    assert metrics["sequence_exact_games"] == 2
