from __future__ import annotations

import pytest

from cgauto.e7_type_to_cut_audit import (
    adjudicate,
    command_target_cell,
    first_divergence,
    FLIP_FROM,
    FLIP_TO,
    focus_geometry,
    hindsight_summary,
    LIVE_SHA256,
    LIVE_SOURCE,
    mechanism_summary,
    OPPONENT_NAMES,
    SEEDS,
    sha256_path,
    transform_source,
)
from sim.mapgen import generate_bronze


def test_exact_live_transform_is_unique_and_reversible():
    source = LIVE_SOURCE.read_bytes()
    assert sha256_path(LIVE_SOURCE) == LIVE_SHA256
    assert source.count(FLIP_FROM.encode()) == 1
    assert source.count(FLIP_TO.encode()) == 0

    flipped = transform_source(source)

    assert flipped.count(FLIP_FROM.encode()) == 0
    assert flipped.count(FLIP_TO.encode()) == 1
    assert flipped.replace(FLIP_TO.encode(), FLIP_FROM.encode(), 1) == source


def test_geometry_reproduces_binary_symmetric_choice_on_frozen_panel():
    choices = []
    for seed in SEEDS:
        game = generate_bronze(seed)
        seats = [focus_geometry(game, seat) for seat in (0, 1)]
        assert seats[0]["chosen_species"] == seats[1]["chosen_species"]
        assert seats[0]["chosen_species"] in {"LEMON", "PLUM"}
        choices.append(seats[0]["chosen_species"])

    assert choices.count("LEMON") + choices.count("PLUM") == 60
    assert set(choices) == {"LEMON", "PLUM"}


def _match(policy_commands, opponent_commands):
    return {
        "policy_trace": [
            {
                "turn": turn,
                "commands": commands,
                "by_unit": {1: commands[0]},
            }
            for turn, commands in enumerate(policy_commands, 1)
        ],
        "opponent_trace": [
            {
                "turn": turn,
                "commands": commands,
                "by_unit": {2: commands[0]},
            }
            for turn, commands in enumerate(opponent_commands, 1)
        ],
    }


def test_first_divergence_has_exact_prefix_and_target_species():
    control = _match(
        [["WAIT"], ["MOVE 1 4 5"]],
        [["WAIT"], ["MOVE 2 7 7"]],
    )
    flip = _match(
        [["WAIT"], ["MOVE 1 6 5"]],
        [["WAIT"], ["MOVE 2 7 7"]],
    )

    result = first_divergence(
        control,
        flip,
        {(4, 5): "LEMON", (6, 5): "PLUM"},
    )

    assert result["turn"] == 2
    assert result["common_prefix_turns"] == 1
    changed = result["changed_unit_commands"][0]
    assert changed["control_initial_target_species"] == "LEMON"
    assert changed["flip_initial_target_species"] == "PLUM"
    assert command_target_cell("CHOP 1") is None


def test_first_divergence_rejects_opponent_leading_policy():
    control = _match([["WAIT"]], [["WAIT"]])
    flip = _match([["WAIT"]], [["MOVE 2 7 7"]])
    with pytest.raises(RuntimeError, match="opponent diverged before"):
        first_divergence(control, flip)


def test_mechanism_gate_requires_cell_seat_and_family_breadth():
    rows = []
    for index in range(36):
        rows.append(
            {
                "seed": index,
                "opponent": OPPONENT_NAMES[index % 4],
                "activated": index < 30,
                "seat_activated": [index < 30, index < 30],
            }
        )

    result = mechanism_summary(rows)

    assert result["status"] == "ACTIVE_FOCUS"
    assert result["activated_cell_count"] == 30
    assert result["seat_game_counts"] == [30, 30]
    assert result["active_family_count"] == 4


def _oracle_rows(delta_for):
    rows = []
    for seed in SEEDS:
        for opponent in OPPONENT_NAMES:
            delta = delta_for(seed, opponent)
            rows.append(
                {
                    "seed": seed,
                    "opponent": opponent,
                    "control_species": "LEMON",
                    "delta_paired_margin": delta,
                    "delta_seat_margins": [delta, delta],
                }
            )
    return rows


def test_hindsight_chooses_once_per_seed_not_per_opponent():
    def delta_for(seed, opponent):
        if seed != 0:
            return 0
        if opponent == OPPONENT_NAMES[0]:
            return -300
        return 50

    summary, rows = hindsight_summary(_oracle_rows(delta_for))

    assert rows[0]["seed"] == 0
    assert rows[0]["flip_delta_mean"] < 0
    assert rows[0]["selected_policy"] == "CONTROL"
    assert rows[0]["selected_gain"] == 0
    assert summary["preferred_flip_seed_count"] == 0


def test_hindsight_material_gate_and_adjudication_precedence():
    rows = _oracle_rows(
        lambda seed, opponent: 6 if seed < 12 else 0
    )
    hindsight, _ = hindsight_summary(rows)
    positive = {name: 1.0 for name in OPPONENT_NAMES}

    assert hindsight["material"]
    assert hindsight["seed_balanced_gain"] == pytest.approx(1.2)
    assert hindsight["preferred_flip_seed_count"] == 12
    assert (
        adjudicate("FOCUS_INERT", 2, [1, 1], positive, True)[0]
        == "FOCUS_INERT"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 0, [0, 0], positive, False)[0]
        == "KEEP_TYPE_TO_CUT"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 0, [0, 0], positive, True)[0]
        == "HINDSIGHT_RESIDUAL_ONLY"
    )
    assert (
        adjudicate("ACTIVE_FOCUS", 1, [0, 0], positive, False)[0]
        == "FLIP_MATERIAL_LOCAL"
    )
