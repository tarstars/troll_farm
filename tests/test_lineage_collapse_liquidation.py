from __future__ import annotations

from cgauto.lineage_collapse_liquidation import analyze, OPPONENTS, PROFILES


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    candidate = profile == "lineage_collapse_liquidation"
    resident = profile == "resident"
    own_score = 105 if candidate else 100 if resident else 80
    opponent_score = 90 if candidate else 100 if resident else 120
    result = {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "own_score": own_score,
        "opponent_score": opponent_score,
        "margin": own_score - opponent_score,
        "own_inventory_wood": 25 if candidate else 20,
        "opponent_inventory_wood": 20 if candidate else 25,
        "workers": 2,
        "terminal_turn": 301,
        "terminal_plants": 0 if candidate else 5,
        "terminal_banana_plants": 0 if candidate else 1,
        "own_successful_plants": 10,
        "opponent_successful_plants": 10 if candidate else 12,
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
        "opponent_crops_seen": 2 if candidate else 0,
        "active_opponent_crops": 0,
        "activation_turns": 191 if candidate else 0,
        "first_activation_turn": 110 if candidate else -1,
        "base_command_mismatches": 0,
        "selected_targets": 10 if candidate else 0,
        "targets_disappeared_before_fruit": 0,
        "targets_fruited_after_selection": 0,
        "capacity_ready_turns": 0,
        "capacity_separation_violations": 0,
        "entry_state_violations": 0,
        "forbidden_post_entry_commands": 0,
        "post_entry_commands": 300 if candidate else 0,
        "lineage_recovery_turns": 0,
        "entry_banked_banana": 0 if candidate else -1,
        "entry_carried_banana": 0 if candidate else -1,
        "entry_crop_banana_fruits": 0 if candidate else -1,
        "entry_opponent_banana_crops": 0 if candidate else -1,
        "entry_own_score": 40 if candidate else -1,
        "entry_opponent_score": 30 if candidate else -1,
        "entry_margin": 10 if candidate else -1,
        "copied_move": 150 if candidate else 0,
        "copied_chop": 100 if candidate else 0,
        "copied_drop": 50 if candidate else 0,
        "copied_mine": 0,
        "copied_pick": 0,
        "copied_harvest": 0,
        "copied_plant": 0,
    }
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


def test_integrity_panel_passes() -> None:
    payload = analyze(panel(0, {"gold_adaptive"}), "integrity", repeat_exact=True)
    assert payload["passed"]
    assert payload["inactive_identity"]["passed"]


def test_strong_discovery_panel_passes() -> None:
    payload = analyze(panel(2140, OPPONENTS), "discovery")
    assert payload["passed"]
    assert payload["positive_opponents"] == 8
    assert payload["trimmed_10pct_mean_margin_delta"] == 15


def test_forbidden_command_fails_integrity() -> None:
    rows = panel(0, {"gold_adaptive"})
    candidate = next(
        item for item in rows if item["profile"] == "lineage_collapse_liquidation"
    )
    candidate["forbidden_post_entry_commands"] = 1
    candidate["copied_plant"] = 1
    payload = analyze(rows, "integrity", repeat_exact=True)
    assert not payload["passed"]
    assert not payload["integrity_checks"]["no_forbidden_post_entry_commands"]
