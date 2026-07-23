from __future__ import annotations

from cgauto.capacity_separated_reproductive_denial import (
    analyze,
    OPPONENTS,
    PROFILES,
)


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    candidate = profile == "capacity_separated_denial"
    base = profile == "adaptive_density"
    own_score = 180 if candidate else 170 if base else 100
    opponent_score = 80 if candidate else 150 if base else 100
    own_wood = 30 if candidate else 28 if base else 10
    opponent_plants = 10 if candidate else 30 if base else 20
    opponent_self_wood = 5 if candidate else 30 if base else 10
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
        "workers": 4 if candidate or base else 2,
        "terminal_turn": 301,
        "own_successful_plants": 20 if candidate or base else 10,
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
        "first_activation_turn": 110 if candidate else -1,
        "base_command_mismatches": 0,
        "selected_targets": 1 if candidate else 0,
        "targets_disappeared_before_fruit": 1 if candidate else 0,
        "targets_fruited_after_selection": 0,
        "capacity_ready_turns": 100 if candidate else 0,
        "capacity_separation_violations": 0,
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


def test_strong_discovery_panel_passes() -> None:
    payload = analyze(panel(2020), "discovery")
    assert payload["passed"]
    assert payload["nonnegative_opponents"] == 8
    assert payload["profiles"]["capacity_separated_denial"][
        "activated_without_capacity_cells"
    ] == 0


def test_capacity_violation_fails_integrity() -> None:
    rows = [
        row(seed, seat, opponent, profile)
        for seed in range(30)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for profile in PROFILES
    ]
    assert analyze(rows, "integrity", repeat_exact=True)["passed"]
    candidate = next(
        item for item in rows if item["profile"] == "capacity_separated_denial"
    )
    candidate["capacity_separation_violations"] = 1
    payload = analyze(rows, "integrity", repeat_exact=True)
    assert not payload["passed"]
    assert not payload["integrity_checks"][
        "zero_capacity_separation_violations"
    ]

