from cgauto.farm_first_option_study import (
    attach_replicate_live_deltas,
    farmer_spec,
    funding_deficit,
    geometry_label,
    handoff_reason,
    parse_command,
    stage_target,
    summarise_supply,
)


def test_farmer_spec_reproduces_the_replay_derived_integer_rule() -> None:
    assert farmer_spec([2, 2, 2, 0, 2, 0]) == (1, 1, 1, 1)
    assert farmer_spec([5, 10, 5, 0, 2, 0]) == (2, 3, 2, 1)
    assert farmer_spec([10, 10, 10, 0, 2, 0]) == (2, 3, 2, 1)


def test_later_funding_targets_use_the_fixed_wood_worker_and_deadlines() -> None:
    first = stage_target(2, [0] * 6)
    second = stage_target(3, [0] * 6)

    assert first["stats"] == [2, 2, 0, 2]
    assert first["cost"] == [6, 6, 2, 0, 6, 0]
    assert first["deadline"] == 100
    assert second["cost"] == [7, 7, 3, 0, 7, 0]
    assert second["deadline"] == 180
    assert stage_target(4, [0] * 6) is None


def test_funding_deficit_is_reported_per_resource() -> None:
    assert funding_deficit([5, 2, 9, 0, 3, 8], [6, 6, 2, 0, 6, 0]) == [
        1,
        4,
        0,
        0,
        3,
        0,
    ]


def test_parse_command_preserves_train_specs_and_plant_kind() -> None:
    assert parse_command("TRAIN 2 2 0 2")["stats"] == [2, 2, 0, 2]
    assert parse_command("PLANT 17 banana") == {
        "verb": "PLANT",
        "raw": "PLANT 17 banana",
        "unit_id": 17,
        "kind": "BANANA",
    }


def test_supply_summary_orients_capture_to_the_candidate_seat() -> None:
    episodes = [
        {
            "kind": "LEMON",
            "geometry": "candidate_favored",
            "joint_plant": False,
            "removed_turn": 80,
            "harvested_fruit": [2, 5],
            "chop_hits": [1, 0],
            "wood_captured": [3, 0],
        },
        {
            "kind": "BANANA",
            "geometry": "contested",
            "joint_plant": True,
            "removed_turn": None,
            "harvested_fruit": [0, 1],
            "chop_hits": [0, 1],
            "wood_captured": [0, 2],
        },
    ]

    summary = summarise_supply(episodes, candidate_seat=1)

    assert summary["candidate_harvested_fruit"] == 6
    assert summary["opponent_harvested_fruit"] == 2
    assert summary["candidate_wood_captured"] == 2
    assert summary["opponent_wood_captured"] == 3
    assert summary["opponent_touched_trees"] == 1
    assert summary["joint_plants"] == 1


def test_replicate_controls_are_joined_without_overwriting_each_other() -> None:
    rows = [
        {
            "seed": 4,
            "replicate": 0,
            "policy": "live",
            "opponent": "race",
            "paired_margin": 10,
            "paired_wood_edge": 3,
        },
        {
            "seed": 4,
            "replicate": 1,
            "policy": "live",
            "opponent": "race",
            "paired_margin": 20,
            "paired_wood_edge": 5,
        },
        {
            "seed": 4,
            "replicate": 0,
            "policy": "farmfirst",
            "opponent": "race",
            "paired_margin": 16,
            "paired_wood_edge": 1,
        },
        {
            "seed": 4,
            "replicate": 1,
            "policy": "farmfirst",
            "opponent": "race",
            "paired_margin": 18,
            "paired_wood_edge": 8,
        },
    ]

    attach_replicate_live_deltas(rows)

    assert rows[2]["delta_vs_live_margin"] == 6
    assert rows[2]["delta_vs_live_wood"] == -2
    assert rows[3]["delta_vs_live_margin"] == -2
    assert rows[3]["delta_vs_live_wood"] == 3


def test_geometry_and_handoff_categories_are_explicit() -> None:
    assert geometry_label(3, 8) == "candidate_favored"
    assert geometry_label(8, 3) == "opponent_favored"
    assert geometry_label(4, 5) == "contested"
    assert handoff_reason(3, 300) == "scaled"
    assert handoff_reason(2, 300) == "second_chopper_timeout"
    assert handoff_reason(1, 80) == "terminal_before_first_deadline"
