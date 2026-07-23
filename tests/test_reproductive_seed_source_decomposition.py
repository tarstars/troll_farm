from __future__ import annotations

from cgauto.reproductive_seed_source_decomposition import (
    analyze,
    FRUIT_FIELDS,
    KINDS,
    ORIGINS,
    PROFILES,
    WOOD_FIELDS,
)


def row(seed: int, seat: int, profile: str) -> dict:
    farm = profile == "lean_m2c2h0k2"
    result = {
        "seed": seed,
        "seat": seat,
        "profile": profile,
        "own_score": 20,
        "opponent_score": 10,
        "margin": -47.93333333333333 if farm else 0,
        "own_inventory_wood": 2,
        "opponent_inventory_wood": 1,
        "terminal_turn": 301,
        "own_successful_plants": 1,
        "opponent_successful_plants": 3 if farm else 1,
        "own_early_successful_plants": 1,
        "opponent_early_successful_plants": 2 if farm else 1,
        "ambiguous_births": 0,
        "total_chop_wood": 10,
        "assigned_chop_wood": 10,
    }
    result.update({field: 1 for field in WOOD_FIELDS})
    result.update({field: 0 for field in FRUIT_FIELDS})
    for phase in ("fruit", "early_fruit"):
        result[f"opponent_{phase}_from_natural_plum"] = 2 if farm else 1
    result["opponent_fruit_from_opponent_banana"] = 5 if farm else 1
    return result


def test_upstream_seed_source_gate_detects_early_natural_uplift() -> None:
    rows = [
        row(seed, seat, profile)
        for seed in range(30)
        for seat in (0, 1)
        for profile in PROFILES
    ]
    payload = analyze(rows)
    assert payload["material_upstream_natural_seed_mechanism"]
    assert payload["farm_minus_resident"]["natural_early_fruit_per_game"] == 1
    assert payload["farm_minus_resident"]["dominant_added_fruit_origin"] == "opponent"


def test_field_names_cover_every_phase_collector_origin_and_kind() -> None:
    assert len(FRUIT_FIELDS) == 64
    assert len(WOOD_FIELDS) == 8
    assert set(ORIGINS) == {"natural", "ours", "opponent", "unknown"}
    assert set(KINDS) == {"plum", "lemon", "apple", "banana"}
