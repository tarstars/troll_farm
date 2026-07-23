from cgauto.complete_economy_representation_study import analyze


def row(seed: int, seat: int, opponent: str, genome: str, delta: int) -> dict:
    parameters = {
        "max_trolls": 3,
        "choppers": 2,
        "stagger": 20,
        "spec1_ms": 2,
        "spec1_cc": 2,
        "spec1_hp": 0,
        "spec1_chop": 2,
        "spec2_ms": 2,
        "spec2_cc": 2,
        "spec2_hp": 0,
        "spec2_chop": 2,
        "planters": 0,
        "hold_until": 0,
        "farm_cap": 12,
        "co_fell": 0,
        "adaptive": 0,
    }
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "genome": genome,
        **parameters,
        "margin_delta": delta,
        "score_delta": max(delta, 0),
        "opponent_score_delta": min(-delta, 0),
        "wood_delta": 1 if delta > 0 else 0,
        "opponent_wood_delta": min(-delta, 0),
        "candidate_workers": 3,
        "candidate_successful_trains": 2,
        "candidate_successful_plants": 5,
        "candidate_harvest": 5,
        "candidate_chop": 50,
        "divergence_turns": 10,
        "resident_identity_mismatches": 0,
        "resident_terminal_turn": 120,
        "candidate_terminal_turn": 130,
    }


def grid(genomes: int, seed_start: int, delta: int) -> list[dict]:
    return [
        row(seed, seat, f"opponent-{model}", f"genome-{index:02}", delta)
        for index in range(genomes)
        for seed in range(seed_start, seed_start + 30)
        for model in range(8)
        for seat in range(2)
    ]


def test_discovery_selects_at_most_three_eligible_genomes() -> None:
    report = analyze(grid(31, 0, 3), "discovery")
    assert report["integrity"]["resident_identity"] is True
    assert len(report["eligible_genomes"]) == 31
    assert report["selected_genomes"] == ["genome-00", "genome-01", "genome-02"]
    assert report["open_confirmation"] is True


def test_discovery_rejects_neutral_catalog() -> None:
    report = analyze(grid(31, 0, 0), "discovery")
    assert report["selected_genomes"] == []
    assert report["open_confirmation"] is False


def test_confirmation_passes_positive_selected_genome() -> None:
    report = analyze(grid(1, 30, 3), "confirmation")
    assert report["representation_gate_passed"] is True
    assert report["selected_genomes"] == ["genome-00"]
