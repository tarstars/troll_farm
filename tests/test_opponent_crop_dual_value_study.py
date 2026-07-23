from cgauto.opponent_crop_dual_value_study import analyze, DUAL, FLAT, EXPECTED_OPPONENTS


def row(seed: int, seat: int, opponent: str, profile: str) -> dict:
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "margin_delta": 0,
        "candidate_margin": 10,
        "candidate_score": 20,
        "candidate_opponent_score": 10,
        "score_delta": 0,
        "opponent_score_delta": 0,
        "candidate_wood": 3,
        "candidate_opponent_wood": 2,
        "wood_delta": 0,
        "opponent_wood_delta": 0,
        "divergence_turns": 1,
    }


def test_exact_neutral_panel_passes_safety_gate() -> None:
    rows = [
        row(seed, seat, opponent, profile)
        for seed in range(1600, 1660)
        for seat in (0, 1)
        for opponent in EXPECTED_OPPONENTS
        for profile in (DUAL, FLAT)
    ]
    payload = analyze(rows)
    assert payload["gate_passed"]
    assert payload["scenarios_per_profile"] == 960
    assert payload["opponents_above_floor"] == 8
    assert payload["dual_minus_flat"]["equal"] == 960
