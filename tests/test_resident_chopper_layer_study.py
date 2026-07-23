from cgauto.resident_chopper_layer_study import analyze, OPPONENTS, PROFILES


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    hybrid = profile == "resident_chopper_hybrid"
    farm = profile == "lean_m2c2h0k2"
    own_score = 180 if hybrid else 170 if farm else 100
    opponent_score = 80 if hybrid else 160 if farm else 100
    opponent_plants = 10 if hybrid else 25 if farm else 8
    opponent_crop_wood = 5 if hybrid else 30 if farm else 4
    copied = 4 if hybrid else 0
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "own_score": own_score,
        "opponent_score": opponent_score,
        "margin": own_score - opponent_score,
        "own_inventory_wood": 30 if hybrid else 28 if farm else 10,
        "opponent_inventory_wood": 10,
        "workers": 2,
        "terminal_turn": 301,
        "own_successful_plants": 10,
        "opponent_successful_plants": opponent_plants,
        "ambiguous_births": 0,
        "total_chop_wood": 20,
        "assigned_chop_wood": 20,
        "own_from_natural": 2,
        "own_from_ours": 8,
        "own_from_opponent": 2,
        "own_from_unknown": 0,
        "opponent_from_natural": 2,
        "opponent_from_ours": 0,
        "opponent_from_opponent": opponent_crop_wood,
        "opponent_from_unknown": 0,
        "opponent_crops_seen": 0,
        "active_opponent_crops": 0,
        "activation_turns": copied,
        "first_activation_turn": 30 if hybrid else -1,
        "base_command_mismatches": 0,
        "copied_move": copied,
        "copied_chop": 0,
        "copied_drop": 0,
        "copied_mine": 0,
        "copied_pick": 0,
        "copied_harvest": 0,
        "copied_plant": 0,
    }


def test_strong_hybrid_discovery_passes() -> None:
    rows = [
        row(seed, seat, opponent, profile)
        for seed in range(1780, 1840)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for profile in PROFILES
    ]
    payload = analyze(rows, "discovery")
    assert payload["passed"]
    assert payload["adaptive_gold"]["mean_opponent_successful_plants_delta_vs_farm"] == -15
    assert payload["adaptive_gold"]["mean_opponent_self_crop_wood_delta_vs_farm"] == -25
    assert payload["hybrid_telemetry"]["activated_cells"] == 960
