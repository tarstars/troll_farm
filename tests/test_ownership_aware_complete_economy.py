from cgauto.ownership_aware_complete_economy import analyze, PROFILES


OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    aware = profile == "ownership_aware"
    farm = profile == "lean_m2c2h0k2"
    score = 180 if aware else 100 if not farm else 170
    opponent_score = 80 if aware else 100 if not farm else 120
    wood = 30 if aware else 10 if not farm else 28
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "own_score": score,
        "opponent_score": opponent_score,
        "margin": score - opponent_score,
        "own_inventory_wood": wood,
        "opponent_inventory_wood": 10,
        "workers": 2,
        "terminal_turn": 301,
        "own_successful_plants": 10,
        "opponent_successful_plants": 10,
        "ambiguous_births": 0,
        "total_chop_wood": 20,
        "assigned_chop_wood": 20,
        "own_from_natural": 2,
        "own_from_ours": 8,
        "own_from_opponent": 2,
        "own_from_unknown": 0,
        "opponent_from_natural": 2,
        "opponent_from_ours": 0,
        "opponent_from_opponent": 6,
        "opponent_from_unknown": 0,
        "opponent_crops_seen": 10 if aware else 0,
        "active_opponent_crops": 2 if aware else 0,
        "activation_turns": 3 if aware else 0,
        "first_activation_turn": 40 if aware else -1,
        "base_command_mismatches": 0,
    }


def test_strong_complete_discovery_panel_passes() -> None:
    rows = [
        row(seed, seat, opponent, profile)
        for seed in range(1660, 1720)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for profile in PROFILES
    ]
    payload = analyze(rows, "discovery")
    assert payload["passed"]
    assert payload["nonnegative_opponents"] == 8
    assert payload["profiles"]["ownership_aware"]["activated_cells"] == 960
    diagnostic = payload["activation_diagnostic"]["overall"]
    assert diagnostic["activation_rate"] == 1
    assert diagnostic["mean_margin_delta_vs_farm_when_active"] == 50
    assert diagnostic["inactive_cells_exactly_equal_farm"]
