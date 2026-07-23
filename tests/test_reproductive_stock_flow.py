from __future__ import annotations

from cgauto.reproductive_stock_flow import (
    analyze,
    CHECKPOINTS,
    CHECKPOINT_FIELDS,
    FRUIT_FIELDS,
    KINDS,
    ORIGINS,
    PHASES,
    PROFILES,
    WOOD_FIELDS,
)


def row(seed: int, seat: int, profile: str) -> dict:
    resident = profile == "resident"
    result = {
        "seed": seed,
        "seat": seat,
        "profile": profile,
        "own_score": 20,
        "opponent_score": 10,
        "margin": 10,
        "own_inventory_wood": 2,
        "opponent_inventory_wood": 1,
        "terminal_turn": 301,
        "own_successful_plants": 5,
        "opponent_successful_plants": 5,
        "own_early_successful_plants": 1,
        "opponent_early_successful_plants": 1,
        "ambiguous_births": 0,
        "total_chop_wood": 10,
        "assigned_chop_wood": 10,
        "post100_exposure_turns": 100,
        "zero_immediate_seed_turns": 20 if resident else 0,
        "zero_owned_seed_turns": 20 if resident else 0,
        "lineage_absent_turns": 10 if resident else 0,
        "low_redundancy_turns": 20 if resident else 0,
        "max_zero_owned_streak": 5 if resident else 0,
        "minimum_immediate_seeds": 0 if resident else 2,
        "minimum_owned_seed_stock": 0 if resident else 2,
    }
    result.update({field: 1 for field in WOOD_FIELDS})
    result.update({field: 0 for field in FRUIT_FIELDS})
    result["own_fruit_from_natural_plum"] = 1
    for collector in ("own", "opponent"):
        for index, (label, _, _) in enumerate(PHASES):
            result[f"{collector}_successful_plants_{label}"] = 1
    for checkpoint in CHECKPOINTS:
        for field in CHECKPOINT_FIELDS:
            result[f"t{checkpoint}_{field}"] = 0
        result[f"t{checkpoint}_recorded"] = 1
        result[f"t{checkpoint}_opponent_successful_plants"] = min(5, checkpoint // 50)
    return result


def panel() -> list[dict]:
    return [
        row(seed, seat, profile)
        for seed in range(30)
        for seat in (0, 1)
        for profile in PROFILES
    ]


def test_material_resident_bottlenecks_are_detected() -> None:
    payload = analyze(panel(), repeat_exact=True)
    assert all(payload["integrity_checks"].values())
    assert payload["material_seed_depletion_boundary"]
    assert payload["material_lineage_absence_boundary"]
    assert payload["profiles"]["resident"]["flow_rates"]["zero_owned_seed"] == 0.2


def test_repeat_identity_is_integrity_gated() -> None:
    payload = analyze(panel(), repeat_exact=False)
    assert not payload["integrity_checks"]["repeat_run_identity"]
    assert not payload["material_seed_depletion_boundary"]


def test_schema_covers_all_provenance_dimensions() -> None:
    assert len(FRUIT_FIELDS) == 64
    assert len(WOOD_FIELDS) == 8
    assert set(ORIGINS) == {"natural", "ours", "opponent", "unknown"}
    assert set(KINDS) == {"plum", "lemon", "apple", "banana"}
