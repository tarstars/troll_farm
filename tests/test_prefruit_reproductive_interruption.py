from __future__ import annotations

from cgauto.prefruit_reproductive_interruption import analyze, OPPONENTS, PROFILES


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    candidate = profile == "prefruit_interruption"
    farm = profile == "lean_m2c2h0k2"
    own_score = 180 if candidate else 170 if farm else 100
    opponent_score = 80 if candidate else 150 if farm else 100
    own_wood = 30 if candidate else 28 if farm else 10
    opponent_plants = 10 if candidate else 30 if farm else 20
    opponent_self_wood = 5 if candidate else 30 if farm else 10
    result = {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "own_score": own_score,
        "opponent_score": opponent_score,
        "margin": own_score - opponent_score,
        "own_inventory_wood": own_wood,
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
        "opponent_from_opponent": opponent_self_wood,
        "opponent_from_unknown": 0,
        "opponent_crops_seen": 10 if candidate else 0,
        "active_opponent_crops": 2 if candidate else 0,
        "activation_turns": 3 if candidate else 0,
        "first_activation_turn": 40 if candidate else -1,
        "base_command_mismatches": 0,
        "selected_targets": 1 if candidate else 0,
        "targets_disappeared_before_fruit": 1 if candidate else 0,
        "targets_fruited_after_selection": 0,
    }
    result.update(
        {
            f"copied_{verb}": 0
            for verb in ("move", "chop", "drop", "mine", "pick", "harvest", "plant")
        }
    )
    return result


def panel(start: int) -> list[dict]:
    return [
        row(seed, seat, opponent, profile)
        for seed in range(start, start + 60)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for profile in PROFILES
    ]


def test_strong_complete_discovery_panel_passes() -> None:
    payload = analyze(panel(1900), "discovery")
    assert payload["passed"]
    assert payload["nonnegative_opponents"] == 8
    assert payload["profiles"]["prefruit_interruption"]["activated_cells"] == 960
    assert payload["adaptive_gold"]["prefruit_minus_farm"][
        "mean_opponent_successful_plants_delta"
    ] == -20


def test_reproductive_mechanism_is_mandatory() -> None:
    rows = panel(1900)
    for item in rows:
        if item["profile"] == "prefruit_interruption":
            item["opponent_successful_plants"] = 30
    payload = analyze(rows, "discovery")
    assert not payload["passed"]
    assert not payload["gate_checks"]["adaptive_opponent_plant_suppression"]


def test_integrity_requires_repeat_identity() -> None:
    rows = [
        row(seed, seat, opponent, profile)
        for seed in range(30)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for profile in PROFILES
    ]
    assert analyze(rows, "integrity", repeat_exact=True)["passed"]
    assert not analyze(rows, "integrity", repeat_exact=False)["passed"]

