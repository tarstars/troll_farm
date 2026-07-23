from __future__ import annotations

from cgauto import analyze_d166a_producer_job_successor_affordance as d166
from cgauto import extract_d166a_field_return_classes as extract


def test_first_cycle_preserves_exact_source_events() -> None:
    events = [
        {
            "ordinal": 0,
            "turn": 1,
            "verb": "PLANT",
            "created_origin": "actor",
            "target_origin": None,
        },
        {
            "ordinal": 0,
            "turn": 2,
            "verb": "HARVEST",
            "created_origin": None,
            "target_origin": "actor",
        },
        {
            "ordinal": 0,
            "turn": 3,
            "verb": "CHOP",
            "created_origin": None,
            "target_origin": "opponent",
        },
        {
            "ordinal": 0,
            "turn": 4,
            "verb": "PLANT",
            "created_origin": "actor",
            "target_origin": None,
        },
    ]
    cycle = extract.first_cycle(events)
    assert cycle is not None
    assert [event["turn"] for event in cycle] == [1, 3, 4]
    assert [extract.role(event) for event in cycle] == ["P", "S", "P"]


def test_frozen_field_and_local_products_close_single_verb(tmp_path) -> None:
    result = d166.run(tmp_path / "d166-result.json")
    assert result["integrity_pass"]
    assert result["field"]["verb_summaries"]["PLANT"]["cohorts"]["rank_1_5"][
        "returns"
    ] == 21
    assert result["field"]["verb_summaries"]["HARVEST"]["cohorts"]["rank_1_5"][
        "returns"
    ] == 15
    assert not result["field"]["dominance_pass"]
    assert result["local"]["entries"] == 237
    assert result["local"]["affordances"]["H-ripe"]["tasks"] == 2
    assert result["local"]["affordances"]["P-carry"]["tasks"] == 0
    assert result["local"]["natural_continuation"]["any_return_tasks"] == 135
    assert result["local"]["natural_continuation"]["verbs"] == {"PLANT": 135}
    assert (
        result["decision"]["verdict"]
        == "close_single_return_verb_and_use_state_conditioned_job_value"
    )
