from cgauto.opponent_crop_harvest_contact_diagnostic import active_crop, summarize


def opportunity(
    *,
    empty: bool = True,
    wood: int = 0,
    later: bool = True,
    later_fruit: int = 2,
    kind: str = "BANANA",
) -> dict:
    return {
        "collectable_fruit": 1,
        "would_empty_crop": empty,
        "immediate_wood_from_actual_chop": wood,
        "later_opponent_harvested": later,
        "later_opponent_fruit": later_fruit if later else 0,
        "type": kind,
    }


def test_active_crop_resolves_generations_and_death_turn() -> None:
    records = [
        {"cell": [3, 4], "birth_turn": 5, "death_turn": 8},
        {"cell": [3, 4], "birth_turn": 10, "death_turn": None},
    ]
    assert active_crop(records, (3, 4), 4) is None
    assert active_crop(records, (3, 4), 8) == records[0]
    assert active_crop(records, (3, 4), 9) is None
    assert active_crop(records, (3, 4), 12) == records[1]


def test_summarize_passes_only_distributed_material_signature() -> None:
    rows = []
    for index in range(40):
        items = [
            opportunity(
                empty=offset == 0,
                wood=0 if index < 30 else 1,
                later=index < 20,
            )
            for offset in range(2)
        ]
        rows.append(
            {
                "opponent": f"opponent-{index % 12}",
                "seat": index % 2,
                "catastrophic": index < 13,
                "opportunities": items,
            }
        )
    report = summarize(rows)
    assert report["opportunities"] == 80
    assert report["opportunity_games"] == 40
    assert report["opportunity_opponents"] == 12
    assert report["collectable_fruit"] == 80
    assert report["full_depletions"] == 40
    assert report["zero_immediate_wood"] == 60
    assert report["later_opponent_harvested_crops"] == 40
    assert report["later_opponent_fruit"] == 80
    assert report["catastrophic_opportunities"] == 26
    assert report["gate_passed"] is True


def test_summarize_rejects_inert_diagnostic() -> None:
    report = summarize([])
    assert report["opportunities"] == 0
    assert report["gate_passed"] is False
