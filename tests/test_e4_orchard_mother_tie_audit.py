from __future__ import annotations

import pytest

from cgauto.e4_orchard_mother_tie_audit import (
    adjudicate,
    ALTERNATE_SUFFIX,
    CONTROL_SUFFIX,
    geometry_for,
    LIVE_SHA256,
    LIVE_SOURCE,
    mechanism_summary,
    metric_summary,
    OPPONENT_NAMES,
    SENTINEL_SEEDS,
    sha256_path,
    structural_census,
    TIED_SEEDS,
    transform_source,
    validate_commands,
)
from sim.mapgen import generate_bronze


def test_exact_live_transform_changes_one_suffix_only():
    source = LIVE_SOURCE.read_bytes()
    assert sha256_path(LIVE_SOURCE) == LIVE_SHA256
    assert source.count(CONTROL_SUFFIX.encode()) == 1
    assert source.count(ALTERNATE_SUFFIX.encode()) == 0

    alternate = transform_source(source)

    assert alternate.count(CONTROL_SUFFIX.encode()) == 0
    assert alternate.count(ALTERNATE_SUFFIX.encode()) == 1
    assert (
        alternate.replace(ALTERNATE_SUFFIX.encode(), CONTROL_SUFFIX.encode(), 1)
        == source
    )


@pytest.mark.parametrize("seat", [0, 1])
def test_known_tied_seed_reproduces_two_equal_best_mothers(seat):
    geometry = geometry_for(generate_bronze(TIED_SEEDS[0]), seat)

    assert geometry["eligible"]
    assert geometry["best_tie_size"] == 2
    assert geometry["control_mother"] != geometry["alternate_mother"]
    tied_distances = {
        item["enemy_door_distance"]
        for item in geometry["mothers"]
        if item["cell"] in geometry["best_tie"]
    }
    assert tied_distances == {geometry["best_distance"]}


@pytest.mark.parametrize("seat", [0, 1])
def test_known_sentinel_has_one_best_mother(seat):
    geometry = geometry_for(generate_bronze(SENTINEL_SEEDS[0]), seat)

    assert geometry["eligible"]
    assert geometry["best_tie_size"] == 1
    assert geometry["control_mother"] == geometry["alternate_mother"]


def test_structural_census_reproduces_frozen_registry():
    census = structural_census()

    assert census["eligible_seed_count_by_seat"] == {"0": 57, "1": 57}
    assert census["tied_seeds_by_seat"] == {
        "0": list(TIED_SEEDS),
        "1": list(TIED_SEEDS),
    }
    assert census["eligible_side_best_tie_size_counts"] == {"1": 94, "2": 20}
    assert all(census["integrity"].values())


def test_command_validation_is_strict():
    validate_commands(
        [
            "WAIT",
            "MOVE 1 2 3",
            "TRAIN 1 2 3 4",
            "HARVEST 1",
            "PLANT 1 APPLE",
        ]
    )
    with pytest.raises(ValueError, match="malformed command"):
        validate_commands(["MOVE 1 2"])
    with pytest.raises(ValueError, match="malformed integer"):
        validate_commands(["CHOP unit"])


def test_mechanism_requires_seed_seat_and_family_breadth():
    records = []
    for seed in TIED_SEEDS:
        for opponent in OPPONENT_NAMES:
            records.append(
                {
                    "seed": seed,
                    "opponent": opponent,
                    "policy_action_diverged_by_seat": [
                        seed in TIED_SEEDS[:6] and opponent in OPPONENT_NAMES[:4],
                        seed in TIED_SEEDS[:6] and opponent in OPPONENT_NAMES[:4],
                    ],
                }
            )

    result = mechanism_summary(records)

    assert result["status"] == "ACTIVE_TIE"
    assert result["divergent_seed_count"] == 6
    assert result["divergent_family_count"] == 4
    assert all(result["gates"].values())


def test_weighted_metric_prices_only_ten_of_one_thousand_maps():
    records = [
        {
            "seed": seed,
            "opponent": opponent,
            "delta_paired_margin": 2.0,
        }
        for seed in TIED_SEEDS
        for opponent in OPPONENT_NAMES
    ]

    summary = metric_summary(records, "delta_paired_margin")

    assert summary["tied_cell_mean"] == 2.0
    assert summary["seed_balanced_tied_mean"] == 2.0
    assert summary["exact_1000_map_weighted_mean"] == 0.02


def test_adjudication_precedence_and_material_gate():
    positive = {name: 1.0 for name in OPPONENT_NAMES}
    four_positive = {
        name: (1.0 if index < 4 else 0.0)
        for index, name in enumerate(OPPONENT_NAMES)
    }
    one_bad = dict(positive)
    one_bad[OPPONENT_NAMES[0]] = -1.01

    assert adjudicate("TIE_INERT", 2.0, [1.0, 1.0], positive)[0] == "TIE_INERT"
    assert (
        adjudicate("ACTIVE_TIE", 0.0, [1.0, 1.0], positive)[0]
        == "KEEP_LEXICOGRAPHIC"
    )
    assert (
        adjudicate("ACTIVE_TIE", 2.0, [-0.01, 1.0], positive)[0]
        == "KEEP_LEXICOGRAPHIC"
    )
    assert (
        adjudicate("ACTIVE_TIE", 2.0, [1.0, 1.0], one_bad)[0]
        == "KEEP_LEXICOGRAPHIC"
    )
    assert (
        adjudicate("ACTIVE_TIE", 0.99, [1.0, 1.0], positive)[0]
        == "TIE_RESIDUAL_NONMATERIAL"
    )
    assert (
        adjudicate("ACTIVE_TIE", 1.0, [0.0, 1.0], four_positive)[0]
        == "TIE_RESIDUAL_MATERIAL_LOCAL"
    )
