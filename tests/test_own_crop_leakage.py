from cgauto.own_crop_leakage import analyze, geometry_class, invert_record


def crop(geometry: str, leaked: int, own: int = 1) -> dict:
    distances = {
        "resident_favored": (1, 5),
        "contested": (3, 3),
        "opponent_favored": (5, 1),
    }
    resident, opponent = distances[geometry]
    return {
        "cell": [1, 1],
        "type": "BANANA",
        "birth_turn": 10,
        "death_turn": 20,
        "survived_to_end": False,
        "resident_eta_at_birth": 1,
        "opponent_eta_at_birth": 2,
        "resident_shack_distance": resident,
        "opponent_shack_distance": opponent,
        "geometry": geometry,
        "resident_chop_turns": [19],
        "resident_harvest_turns": [],
        "opponent_chop_turns": [20] if leaked else [],
        "opponent_harvest_turns": [],
        "resident_wood_collected": own,
        "opponent_wood_collected": leaked,
        "resident_fruit_harvested": 0,
        "opponent_fruit_harvested": 0,
    }


def test_leaky_fixture_passes_frozen_gates() -> None:
    rows = []
    for index in range(131):
        catastrophic = index < 25
        records = [crop("contested", 2) for _ in range(5)]
        rows.append(
            {
                "game_id": 1000 + index,
                "opponent": "field",
                "margin": -150 if catastrophic else 10,
                "catastrophic": catastrophic,
                "quality": {
                    "decoded_turns": 300,
                    "trajectory_turns": 300,
                    "unknown_diff_updates": 0,
                },
                "resident_crops": len(records),
                "records": records,
            }
        )
    report = analyze(rows, [])
    assert report["passed"] is True
    assert all(report["gates"].values())


def test_geometry_and_role_inversion() -> None:
    assert geometry_class(2, 6) == "resident_favored"
    assert geometry_class(4, 4) == "contested"
    assert geometry_class(8, 3) == "opponent_favored"
    record = invert_record(
        {
            "cell": [2, 3],
            "type": "PLUM",
            "birth_turn": 5,
            "death_turn": 10,
            "our_eta_at_birth": 7,
            "opponent_eta_at_birth": 2,
            "our_shack_distance": 8,
            "opponent_shack_distance": 1,
            "our_chop_turns": [9],
            "our_harvest_turns": [],
            "opponent_chop_turns": [10],
            "opponent_harvest_turns": [],
            "our_wood_collected": 2,
            "opponent_wood_collected": 1,
            "our_fruit_harvested": 3,
            "opponent_fruit_harvested": 4,
        }
    )
    assert record["geometry"] == "resident_favored"
    assert record["opponent_wood_collected"] == 2
    assert record["resident_wood_collected"] == 1

