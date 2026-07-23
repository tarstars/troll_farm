from cgauto.opponent_crop_dual_value_field_activation import (
    analyze,
    instrument_dual_value_probe,
    parse_probe_events,
)


def test_dual_probe_instrumentation_is_fail_closed() -> None:
    anchor = (
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
    )
    result = instrument_dual_value_probe(f"before{anchor}after")
    assert "@DUAL_SELECT" in result
    assert result.count("MoisanBot::select") == 1


def test_parse_dual_probe_score() -> None:
    events = parse_probe_events(
        "@DUAL_SELECT t=42 cell=3,-2 score=120.000000000 "
        "base=60.000000000 command=MOVE 7 3 -2\n"
    )
    assert events == [
        {
            "turn": 42,
            "cell": [3, -2],
            "doubled_score": 120.0,
            "inferred_resident_score": 60.0,
            "score_is_exactly_doubled": True,
            "command": "MOVE 7 3 -2",
            "unit_id": 7,
        }
    ]


def test_frozen_mechanism_gate_passes_sufficient_explained_rows() -> None:
    rows = []
    for index in range(131):
        activated = index < 55
        catastrophic = index < 12
        rows.append(
            {
                "game_id": index,
                "opponent": f"opponent-{index % 3}",
                "margin": -100 if catastrophic else 1,
                "unknown_diff_updates": 0,
                "resident_full_stream_exact": True,
                "candidate_first_divergence_turn": 40 if activated else None,
                "admissible_first_divergence": activated,
                "first_divergence_explanation": {"explained": True}
                if activated
                else None,
                "opponent_crops": 3,
                "opponent_crop_wood": 8,
            }
        )
    payload = analyze(rows, [], True)
    assert payload["prospective_gate_passed"]
    assert payload["catastrophic_activated_games"] == 12
