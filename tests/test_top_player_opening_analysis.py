from cgauto.top_player_opening_analysis import (
    analyze_players,
    assigned_unit_commands,
    best_threshold,
    opening_features,
    summarize_training_events,
    training_cost,
)


def unit(unit_id, player, x, *, carry=None, stats=(1, 1, 1, 1)):
    return {
        "id": unit_id,
        "player": player,
        "x": x,
        "y": 0,
        "ms": stats[0],
        "cc": stats[1],
        "hp": stats[2],
        "chop": stats[3],
        "carry": list(carry or [0] * 6),
    }


def plant(x, *, kind="PLUM", health=6, fruits=1):
    return {
        "type": kind,
        "x": x,
        "y": 0,
        "stage": 4 + fruits,
        "size": 4,
        "fruits": fruits,
        "cooldown": 1,
        "health": health,
        "cooldown_effective": 8,
    }


def state(turn, inventory0, units, plants=None):
    return {
        "resolved_turn": turn,
        "inventories": [list(inventory0), [8, 8, 8, 8, 8, 0]],
        "units": units,
        "plants": list(plants or []),
    }


def test_training_cost_uses_worker_count_and_four_resource_stats() -> None:
    assert training_cost(2, (2, 3, 1, 2)) == [6, 11, 3, 0, 6, 0]


def test_wait_keeps_its_positional_worker_slot() -> None:
    units = [unit(2, 0, 0), unit(7, 0, 1)]

    assigned = assigned_unit_commands(["WAIT", "CHOP 7"], units)

    assert assigned == {2: "WAIT", 7: "CHOP 7"}


def test_opening_features_are_seat_relative_and_include_affordability() -> None:
    decoded_map = {"rows": ["0...1"]}
    initial = state(
        0,
        [8, 8, 8, 3, 8, 0],
        [unit(0, 0, 1), unit(1, 1, 3)],
        [plant(1), plant(3, kind="BANANA", fruits=3)],
    )

    features = opening_features(decoded_map, initial, 0)

    assert features["initial_plum"] == 8
    assert features["tree_total"] == 2
    assert features["fruit_total"] == 4
    assert features["own_private_tree_count"] == 1
    assert features["opponent_private_tree_count"] == 1
    assert features["own_nearest_tree_distance"] == 0
    assert features["affords_2_2_0_2"] is True


def test_training_event_and_new_worker_output_are_joined() -> None:
    starter0 = unit(0, 0, 1)
    starter1 = unit(1, 1, 3)
    trained_empty = unit(2, 0, 1, stats=(1, 1, 0, 1))
    trained_wood = unit(2, 0, 1, carry=[0, 0, 0, 0, 0, 1], stats=(1, 1, 0, 1))
    states = [
        state(0, [3, 3, 1, 0, 3, 0], [starter0, starter1], [plant(1)]),
        state(
            1,
            [1, 1, 0, 0, 1, 0],
            [starter0, starter1, trained_empty],
            [plant(1)],
        ),
        state(
            2,
            [1, 1, 0, 0, 1, 0],
            [starter0, starter1, trained_wood],
            [],
        ),
        state(
            3,
            [1, 1, 0, 0, 1, 1],
            [starter0, starter1, trained_empty],
            [],
        ),
    ]
    trajectory = [
        {"commands0": "WAIT;TRAIN 1 1 0 1", "commands1": "WAIT"},
        {"commands0": "WAIT;CHOP 2", "commands1": "WAIT"},
        {"commands0": "WAIT;DROP 2", "commands1": "WAIT"},
    ]

    result = analyze_players(states, trajectory)[0]

    event = result["training_events"][0]
    assert event["turn"] == 1
    assert event["new_unit_id"] == 2
    assert event["cost_vector"] == [2, 2, 1, 0, 2, 0]
    assert event["starting_bank_funded"] is True
    assert event["max_affordable_spec"] == [1, 1, 0, 1]
    assert event["matches_max_affordable_spec"] is True
    assert event["deficit_trajectory"] == [{"turn": 1, "deficit": {}}]
    assert event["bank_score_delta_after"]["100"] is None
    trained = next(worker for worker in result["workers"] if worker["unit_id"] == 2)
    assert trained["chop_on_tree_turns"] == 1
    assert trained["dropped"] == {"WOOD": 1}
    assert trained["direct_banked_value"] == 4
    assert trained["direct_payback_turn"] is None


def test_training_summary_attributes_funding_by_worker_ordinal() -> None:
    event = {
        "ordinal": 2,
        "turn": 20,
        "funding_window_start_turn": 5,
        "spec": [2, 2, 0, 2],
        "role": "wood specialist",
        "matches_max_affordable_spec": True,
        "max_affordable_stat_slack": [0, 0, 0, 0],
        "cost": {"PLUM": 6, "LEMON": 6, "APPLE": 2, "IRON": 6},
        "deficit_at_window_start": {"PLUM": 4, "LEMON": 3},
        "funding_contributors": [
            {
                "ordinal": 0,
                "commands": {"HARVEST": 4, "DROP": 2},
                "dropped": {"PLUM": 2, "LEMON": 1},
                "material_gained": {"PLUM": 3, "LEMON": 1},
            }
        ],
        "n_before": 2,
        "starting_bank_funded": False,
        "delay_after_affordable": 1,
        "whole_bank_recovery_turn": 30,
        "whole_bank_recovery_delay": 10,
        "bank_score_delta_after": {
            "0": -12,
            "10": 0,
            "25": 8,
            "50": None,
            "100": None,
        },
        "wood_delta_after": {"10": 0, "25": 2, "50": None, "100": None},
    }

    summary = summarize_training_events([{"training_events": [event]}])["2"]

    assert summary["mean_funding_window_turns"] == 15
    assert summary["funding_by_worker_ordinal"]["0"]["dropped_per_event"] == {
        "PLUM": 2,
        "LEMON": 1,
    }
    assert summary["funding_by_worker_ordinal"]["1"]["active_in_window_rate"] == 0
    assert summary["bank_score_delta_after"]["50"]["n"] == 0


def test_threshold_is_descriptive_of_multiworker_condition() -> None:
    rows = [
        {"opening": {"initial_iron": value}, "successful_train_count": int(value >= 5) * 2}
        for value in range(1, 9)
    ]

    threshold = best_threshold(rows, "initial_iron")

    assert threshold is not None
    assert threshold["threshold"] == 4.5
    assert threshold["multiworker_direction"] == "above"
    assert threshold["balanced_accuracy_in_sample"] == 1.0
