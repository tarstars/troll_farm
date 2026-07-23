from cgauto.analyze_d33_official_mapgen_parity import (
    canonical_comparison,
    live_plant_order,
    parse_turn_one,
    structural_invariants,
)


def sample(plants: list[str]) -> str:
    rows = [
        "8 4",
        "0.......",
        "........",
        "........",
        ".......1",
        "2 2 2 2 2 0",
        "2 2 2 2 2 0",
        str(len(plants)),
        *plants,
        "2",
        "0 0 0 0 1 1 1 1 0 0 0 0 0 0",
        "1 1 7 3 1 1 1 1 0 0 0 0 0 0",
    ]
    return "\n".join(rows) + "\n"


def ordered_plants() -> list[str]:
    return [
        "PLUM 1 1 1 6 0 2",
        "PLUM 6 2 1 6 0 2",
        "LEMON 2 1 2 8 0 3",
        "LEMON 5 2 2 8 0 3",
        "APPLE 3 1 3 17 0 4",
        "APPLE 4 2 3 17 0 4",
        "BANANA 1 2 4 6 1 2",
        "BANANA 6 1 4 6 1 2",
    ]


def test_parser_and_live_order_accept_type_grouped_mirror_pairs():
    parsed = parse_turn_one(sample(ordered_plants()))
    assert live_plant_order(parsed)


def test_canonical_comparison_accepts_replay_only_reordering():
    generated = sample(ordered_plants())
    replay_order = [ordered_plants()[index] for index in (4, 0, 6, 2, 5, 1, 7, 3)]
    result = canonical_comparison(sample(replay_order), generated)
    assert result["pass"]
    assert result["plant_multiset_exact"]


def test_canonical_comparison_rejects_plant_state_change():
    expected = sample(ordered_plants())
    changed = ordered_plants()
    changed[0] = changed[0].replace(" 6 0 2", " 5 0 2")
    result = canonical_comparison(expected, sample(changed))
    assert not result["pass"]
    assert not result["plant_multiset_exact"]


def test_structural_invariants_reject_nonofficial_height():
    result = structural_invariants(sample(ordered_plants()))
    assert not result["pass"]
    assert not result["dimensions"]
