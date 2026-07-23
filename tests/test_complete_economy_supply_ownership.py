from cgauto.complete_economy_supply_ownership import analyze, PROFILES


def row(seed: int, seat: int, profile: str) -> dict:
    farm = profile == "lean_m2c2h0k2"
    return {
        "seed": seed,
        "seat": seat,
        "profile": profile,
        "own_score": 20,
        "opponent_score": 10,
        "margin": 10,
        "own_inventory_wood": 2,
        "opponent_inventory_wood": 1,
        "terminal_turn": 301,
        "own_successful_plants": 2 if farm else 1,
        "opponent_successful_plants": 1,
        "ambiguous_births": 0,
        "total_chop_wood": 20 if farm else 10,
        "assigned_chop_wood": 20 if farm else 10,
        "own_from_natural": 4,
        "own_from_ours": 5 if farm else 2,
        "own_from_opponent": 1,
        "own_from_unknown": 0,
        "opponent_from_natural": 2,
        "opponent_from_ours": 6 if farm else 1,
        "opponent_from_opponent": 2,
        "opponent_from_unknown": 0,
    }


def test_direct_capture_panel_selects_private_supply_branch() -> None:
    rows = [
        row(seed, seat, profile)
        for seed in range(30)
        for seat in (0, 1)
        for profile in PROFILES
    ]
    payload = analyze(rows)
    assert payload["direct_supply_capture"]
    assert payload["farm_minus_resident"]["our_crop_share_of_increase"] >= 0.5
