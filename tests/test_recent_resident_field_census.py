from cgauto.recent_resident_field_census import (
    event_amount,
    inventory_after,
    rule_report,
    score,
    summarize_crop_records,
    successful_events,
)


def test_successful_events_keep_turns_amounts_and_ignore_failures() -> None:
    frames = [
        {"keyframe": True, "view": " 0\n{}"},
        {
            "keyframe": True,
            "view": " 1\n{}",
            "summary": "\n".join(
                (
                    "$0: trained a troll",
                    "$1: troll 1 planted a BANANA",
                    "$1: [failed] troll 1 planted a PLUM",
                )
            ),
        },
        {
            "keyframe": True,
            "view": " 2\n{}",
            "summary": "$1: troll 1 harvested 3 BANANA\n$0: troll 0 damaged a tree",
        },
    ]
    events = successful_events(frames)
    assert events[0] == [
        {"turn": 1, "kind": "TRAIN", "amount": 1},
        {"turn": 2, "kind": "CHOP", "amount": 1},
    ]
    assert event_amount(events[1], "PLANT", 1) == 1
    assert event_amount(events[1], "HARVEST", 1) == 0
    assert event_amount(events[1], "HARVEST", 2) == 3


def test_successful_events_accepts_both_referee_chop_success_forms() -> None:
    frames = [
        {"keyframe": True, "view": " 0\n{}"},
        {
            "keyframe": True,
            "view": " 1\n{}",
            "summary": "\n".join(
                (
                    "$0: troll 0 damaged a tree",
                    "$1: troll 7 collected 4 WOOD",
                    "$1: [failed] troll 7 collected 4 WOOD",
                )
            ),
        },
    ]
    events = successful_events(frames)
    assert events[0] == [{"turn": 1, "kind": "CHOP", "amount": 1}]
    assert events[1] == [{"turn": 1, "kind": "CHOP", "amount": 1}]


def test_inventory_after_and_score_follow_replay_turn_convention() -> None:
    turns = [
        {"inv0": [1, 1, 1, 1, 0, 0], "inv1": [0] * 6},
        {"inv0": [2, 1, 1, 1, 0, 3], "inv1": [0] * 6},
    ]
    final = ([2, 2, 1, 1, 0, 4], [0] * 6)
    assert inventory_after(turns, final, 0, 1) == [2, 1, 1, 1, 0, 3]
    assert inventory_after(turns, final, 0, 2) == [2, 2, 1, 1, 0, 4]
    assert inventory_after(turns, final, 0, 3) is None
    assert score(final[0]) == 22


def _risk_row(margin: int, opponent: str, workers: int, plants: int) -> dict:
    side = {
        "score": 20,
        "wood": 5,
        "workers": 2,
        "successful_plants": 1,
        "harvested_fruit": 0,
    }
    opponent_side = {
        "score": 40,
        "wood": 10,
        "workers": workers,
        "successful_plants": plants,
        "harvested_fruit": 8,
    }
    return {
        "margin": margin,
        "opponent": opponent,
        "timeline": {"75": {"my": side, "opponent": opponent_side}},
        "final": {"opponent": {"wood": 30}},
    }


def test_rule_report_measures_tail_precision_recall_and_breadth() -> None:
    rows = [
        _risk_row(-150, "a", 3, 10),
        _risk_row(-120, "b", 4, 12),
        _risk_row(-20, "c", 3, 9),
        _risk_row(10, "d", 2, 20),
    ]
    conditions = [
        {
            "feature": "t75:opponent_workers",
            "operator": ">=",
            "threshold": 3,
            "label": "workers",
        },
        {
            "feature": "t75:opponent_plants",
            "operator": ">=",
            "threshold": 8,
            "label": "plants",
        },
    ]
    report = rule_report(rows, conditions)
    assert report["selected"] == 3
    assert report["catastrophic"] == 2
    assert report["precision"] == 2 / 3
    assert report["recall"] == 1
    assert report["opponents"] == 3


def test_crop_summary_distinguishes_reachable_contact_and_compounding() -> None:
    records = [
        {
            "type": "BANANA",
            "our_eta_at_birth": 8,
            "first_our_contact_turn": 30,
            "first_opponent_harvest_turn": 35,
            "our_chop_turns": [30],
            "our_harvest_turns": [],
            "our_wood_collected": 2,
            "our_fruit_harvested": 0,
            "opponent_wood_collected": 0,
            "opponent_fruit_harvested": 1,
        },
        {
            "type": "LEMON",
            "our_eta_at_birth": 12,
            "first_our_contact_turn": None,
            "first_opponent_harvest_turn": 40,
            "our_chop_turns": [],
            "our_harvest_turns": [],
            "our_wood_collected": 0,
            "our_fruit_harvested": 0,
            "opponent_wood_collected": 4,
            "opponent_fruit_harvested": 3,
        },
    ]
    summary = summarize_crop_records(records)
    assert summary["crops"] == 2
    assert summary["our_interception_rate"] == 0.5
    assert summary["reachable_within_20_at_birth"] == 2
    assert summary["reachable_20_contacted"] == 1
    assert summary["opponent_harvested_before_our_contact"] == 1
    assert summary["opponent_wood_collected"] == 4
