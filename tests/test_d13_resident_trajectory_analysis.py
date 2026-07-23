from __future__ import annotations

from cgauto.d13_resident_trajectory_analysis import (
    FROZEN_OPPONENTS,
    FROZEN_SEEDS,
    analyze,
)


def fixture() -> tuple[list[dict], list[dict]]:
    games = []
    decisions = []
    for seed in FROZEN_SEEDS:
        for seat in range(2):
            for opponent in FROZEN_OPPONENTS:
                games.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "opponent": opponent,
                        "policy": "resident",
                        "margin": 5,
                        "wood_edge": 1,
                        "terminal_turn": 100,
                        "workers": 2,
                    }
                )
                for turn in range(1, 5):
                    decisions.append(
                        {
                            "seed": seed,
                            "seat": seat,
                            "opponent": opponent,
                            "policy": "resident",
                            "turn": turn,
                            "unit_id": seat,
                            "ordinal": 0,
                            "worker_count": 2,
                            "ms": 1,
                            "cc": 1,
                            "hp": 1,
                            "chop": 1,
                            "free": 1,
                            **{f"carry{i}": 0 for i in range(6)},
                            **{f"inv{i}": 1 for i in range(6)},
                            "local_plant_type": "-",
                            "local_plant_fruits": -1,
                            "near_home": 0,
                            "near_iron": 0,
                            "resident_command": "MOVE 0 2 2",
                            "resident_verb": "MOVE",
                            "actor_command": "MOVE 0 2 2",
                            "actor_verb": "MOVE",
                            "resident_target_x": 2,
                            "resident_target_y": 2,
                            "previous_verb": "-" if turn == 1 else "MOVE",
                            "previous_target_x": -1 if turn == 1 else 2,
                            "previous_target_y": -1 if turn == 1 else 2,
                            "exact_persistent": int(turn > 1),
                            "verb_persistent": int(turn > 1),
                            "target_persistent": int(turn > 1),
                            "intent_age": turn,
                            "other_verb": "MOVE",
                            "paired_target_collision": 0,
                            "poi_move_targets": 9,
                            "local_productive_actions": 0,
                            "residual_options": 9,
                            "resident_directly_decodable": 1,
                            "state_fingerprint": f"{seed:02x}{seat}{turn}{opponent}",
                            "terminal_margin": 5,
                            "terminal_wood_edge": 1,
                            "terminal_turn": 100,
                        }
                    )
    return games, decisions


def test_selects_spatial_interface_with_both_intent_features(tmp_path):
    games, decisions = fixture()
    games_path = tmp_path / "games.tsv"
    decisions_path = tmp_path / "decisions.tsv"
    games_path.write_text("fixture\n")
    decisions_path.write_text("fixture\n")
    result = analyze(games, decisions, games_path, decisions_path)

    selected = result["interface_selection"]
    assert selected["selected"] == "spatial_keep_plus_action"
    assert selected["include_previous_resident_intent"] is True
    assert selected["include_other_worker_intent"] is True
    assert selected["retain_point_of_interest_moves_due_to_sparse_local_actions"] is True


def test_large_action_mask_selects_binary_fallback(tmp_path):
    games, decisions = fixture()
    for row in decisions:
        row["residual_options"] = 80
    games_path = tmp_path / "games.tsv"
    decisions_path = tmp_path / "decisions.tsv"
    games_path.write_text("fixture\n")
    decisions_path.write_text("fixture\n")
    result = analyze(games, decisions, games_path, decisions_path)

    assert (
        result["interface_selection"]["selected"]
        == "binary_keep_or_generated_alternative"
    )
