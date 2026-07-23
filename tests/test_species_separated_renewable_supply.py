from __future__ import annotations

from cgauto.species_separated_renewable_supply import analyze, OPPONENTS, PROFILES


KINDS = ("plum", "lemon", "apple", "banana")
ORIGINS = ("natural", "ours", "opponent", "unknown")


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    candidate = profile == "species_separated_plum"
    banana = profile == "adaptive_density"
    own_score = 130 if candidate else 150 if banana else 100
    opponent_score = 110 if candidate else 150 if banana else 100
    result = {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "own_score": own_score,
        "opponent_score": opponent_score,
        "margin": own_score - opponent_score,
        "own_inventory_wood": 30,
        "opponent_inventory_wood": 20,
        "workers": 4 if candidate or banana else 2,
        "terminal_turn": 301,
        "terminal_plants": 4,
        "terminal_banana_plants": 0 if candidate else 2,
        "own_successful_plants": 10,
        "opponent_successful_plants": 20 if candidate else 30 if banana else 15,
        "ambiguous_births": 0,
        "total_chop_wood": 20,
        "assigned_chop_wood": 20,
        "own_from_natural": 5,
        "own_from_ours": 5,
        "own_from_opponent": 0,
        "own_from_unknown": 0,
        "opponent_from_natural": 5,
        "opponent_from_ours": 0,
        "opponent_from_opponent": 5,
        "opponent_from_unknown": 0,
        "opponent_crops_seen": 0,
        "active_opponent_crops": 0,
        "activation_turns": 0,
        "first_activation_turn": -1,
        "base_command_mismatches": 0,
        "selected_targets": 0,
        "targets_disappeared_before_fruit": 0,
        "targets_fruited_after_selection": 0,
        "capacity_ready_turns": 0,
        "capacity_separation_violations": 0,
        "entry_state_violations": 0,
        "forbidden_post_entry_commands": 0,
        "post_entry_commands": 0,
        "lineage_recovery_turns": 0,
        "entry_banked_banana": 0,
        "entry_carried_banana": 0,
        "entry_crop_banana_fruits": 0,
        "entry_opponent_banana_crops": 0,
        "entry_own_score": 0,
        "entry_opponent_score": 0,
        "entry_margin": 0,
        "total_harvested_fruit": 10,
        "assigned_harvested_fruit": 10,
    }
    result.update(
        {
            f"copied_{verb}": 0
            for verb in ("move", "chop", "drop", "mine", "pick", "harvest", "plant")
        }
    )
    for collector in ("own", "opponent"):
        for kind in KINDS:
            result[f"{collector}_plant_commands_{kind}"] = int(
                collector == "own" and kind == ("plum" if candidate else "banana")
            ) * 10
            result[f"{collector}_successful_plants_{kind}"] = int(
                collector == "own" and kind == ("plum" if candidate else "banana")
            ) * 10
    for kind in KINDS:
        result[f"terminal_plants_{kind}"] = int(kind == ("plum" if candidate else "banana")) * 4
    for collector in ("own", "opponent"):
        for origin in ORIGINS:
            for kind in KINDS:
                result[f"{collector}_fruit_from_{origin}_{kind}"] = 0
    result["own_fruit_from_natural_plum"] = 5
    result["opponent_fruit_from_natural_banana"] = 5
    if candidate:
        result["opponent_fruit_from_ours_plum"] = 1
    return result


def panel(start: int, opponents: set[str]) -> list[dict]:
    count = 30 if start == 0 else 60
    return [
        row(seed, seat, opponent, profile)
        for seed in range(start, start + count)
        for seat in (0, 1)
        for opponent in opponents
        for profile in PROFILES
    ]


def test_mechanism_panel_passes() -> None:
    rows = panel(0, {"gold_adaptive"})
    payload = analyze(rows, "mechanism", repeat_exact=True, reference=rows)
    assert payload["passed"]
    assert payload["profiles"]["species_separated_plum"][
        "successful_plants_by_kind"
    ]["own"]["plum"] == 600


def test_strong_discovery_panel_passes() -> None:
    payload = analyze(panel(2260, OPPONENTS), "discovery")
    assert payload["passed"]
    assert payload["positive_opponents"] == 8


def test_banana_candidate_birth_fails_integrity() -> None:
    rows = panel(0, {"gold_adaptive"})
    candidate = next(item for item in rows if item["profile"] == "species_separated_plum")
    candidate["own_successful_plants_banana"] = 1
    payload = analyze(rows, "mechanism", repeat_exact=True, reference=rows)
    assert not payload["passed"]
    assert not payload["integrity_checks"]["candidate_zero_banana_crop_births"]
