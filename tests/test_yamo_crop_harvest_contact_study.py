from cgauto.yamo_crop_harvest_contact_study import analyze


def row(seed: int, seat: int, opponent: str, delta: int) -> dict:
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "harvest_b100_margin_delta": delta,
        "harvest_b100_score_delta": max(delta, 0),
        "harvest_b100_opponent_score_delta": min(-delta, 0),
        "harvest_b100_wood_delta": 0,
        "harvest_b100_opponent_wood_delta": min(-delta, 0),
        "harvest_b100_divergence_turns": 1,
        "harvest_b100_first_divergence_turn": 50,
        "harvest_rewrites": 1,
        "b100_resident_margin_delta": 1,
        "b100_resident_score_delta": 1,
        "b100_resident_opponent_score_delta": 0,
        "b100_resident_wood_delta": 0,
        "b100_resident_opponent_wood_delta": 0,
        "harvest_resident_margin_delta": delta + 1,
        "harvest_resident_score_delta": max(delta, 0) + 1,
        "harvest_resident_opponent_score_delta": min(-delta, 0),
        "harvest_resident_wood_delta": 0,
        "harvest_resident_opponent_wood_delta": min(-delta, 0),
    }


def grid(delta: int) -> list[dict]:
    return [
        row(seed, seat, f"opponent-{model}", delta)
        for seed in range(1300, 1360)
        for model in range(8)
        for seat in range(2)
    ]


def test_analyze_passes_distributed_positive_grid() -> None:
    report = analyze(grid(1))
    assert report["rows"] == 960
    assert report["activation"]["cells"] == 960
    assert report["activation"]["harvest_rewrites"] == 960
    assert report["nonnegative_opponents"] == 8
    assert report["gate_passed"] is True


def test_analyze_rejects_neutral_grid() -> None:
    report = analyze(grid(0))
    assert report["harvest_minus_b100"]["margin_delta"]["mean"] == 0
    assert report["gate_passed"] is False
