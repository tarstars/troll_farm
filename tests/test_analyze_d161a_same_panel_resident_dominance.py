from cgauto import analyze_d161a_same_panel_resident_dominance as d161


def outcome(seed: int, opponent: str, own: int, other: int) -> dict:
    return {
        "map_seed": seed,
        "seat": 0,
        "opponent": opponent,
        "own_score": own,
        "opponent_score": other,
    }


def test_choose_best_one_uses_strict_improvement_and_deterministic_tie_break() -> None:
    control = {**outcome(d161.START_SEED, "resident", 10, 10), "margin": "0"}
    tied = {
        **outcome(d161.START_SEED, "resident", 12, 12),
        "margin": "0",
        "own_workers": "3",
        "own_created_crops": "1",
        "boundary_index": "0",
        "slot": "1",
    }
    improved = {
        **outcome(d161.START_SEED, "resident", 12, 11),
        "margin": "1",
        "own_workers": "3",
        "own_created_crops": "1",
        "boundary_index": "1",
        "slot": "2",
    }
    control.update({"own_workers": "2", "own_created_crops": "1"})

    assert d161.choose_best_one(control, [tied])["boundary_index"] == "-1"
    assert d161.choose_best_one(control, [tied, improved])["boundary_index"] == "1"


def test_resident_dominance_gates_accept_uniformly_strong_safe_envelope() -> None:
    resident = {}
    candidate = {}
    for seed in range(d161.START_SEED, d161.START_SEED + d161.MAP_COUNT):
        for opponent in d161.OPPONENTS:
            key = (seed, 0, opponent)
            resident[key] = outcome(seed, opponent, 100, 100)
            candidate[key] = outcome(seed, opponent, 110, 100)

    metrics = d161.comparison_metrics(resident, candidate)
    gates = d161.value_gates(metrics)

    assert metrics["delta"]["mean_margin_delta"] == 10
    assert metrics["positive_families"] == 8
    assert gates["pass"] is True


def test_resident_dominance_gates_reject_tail_damage() -> None:
    resident = {}
    candidate = {}
    for seed in range(d161.START_SEED, d161.START_SEED + d161.MAP_COUNT):
        for opponent in d161.OPPONENTS:
            key = (seed, 0, opponent)
            resident[key] = outcome(seed, opponent, 100, 100)
            candidate[key] = outcome(seed, opponent, 110, 100)
    damaged = (d161.START_SEED, 0, d161.OPPONENTS[0])
    candidate[damaged] = outcome(d161.START_SEED, d161.OPPONENTS[0], 0, 101)

    gates = d161.value_gates(d161.comparison_metrics(resident, candidate))

    assert gates["gates"]["catastrophe_count_not_above_resident"] is False
    assert gates["gates"]["negative_margin_mass_not_above_resident"] is False
    assert gates["pass"] is False
