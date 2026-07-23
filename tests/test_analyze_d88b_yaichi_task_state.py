from collections import deque

from cgauto.analyze_d88b_yaichi_task_state import (
    consume_tokens,
    extract_msg_payload,
    normalize_state,
    parse_msg_payload,
)


def test_frozen_state_normalization():
    assert normalize_state("MINE") == "MINE"
    assert normalize_state("HARVEST") == "HARVEST"
    assert normalize_state("DROP") == "DROP"
    assert normalize_state("DO_CHOP") == "DO_CHOP"
    assert normalize_state("PLANT") == "PLANT"
    assert normalize_state("PICK_SHACK->2,3") == "PICK_SHACK"
    assert normalize_state("GO_PLANT->2,3") == "GO_PLANT"
    assert normalize_state("RETURN->2,3") == "RETURN"
    assert normalize_state("CHOP->2,3 to(1,3)") == "CHOP_TRAVEL"
    assert normalize_state("H(2,3) T4->1,3") == "HARVEST_TRAVEL"
    assert normalize_state("M(2,3)->1,3") == "MINE_TRAVEL"
    assert normalize_state("GET_SEED_TREE->2,3 to(1,3)") == "GET_SEED_TREE"
    assert normalize_state("ATTACK->2,3 to(1,3)") == "ATTACK"
    assert normalize_state("FUTURE_ALIAS") == "UNKNOWN"


def test_message_extraction_and_exact_segment_split():
    payload, count = extract_msg_payload(
        "MOVE 1 2 3;MSG 1:H(4,5)->2,3 | 7:DO_CHOP"
    )
    assert count == 1
    parsed = parse_msg_payload(payload)
    assert parsed == {
        "segments": {1: "H(4,5)->2,3", 7: "DO_CHOP"},
        "malformed": [],
        "duplicates": [],
    }


def test_message_parser_retains_malformed_and_duplicates():
    parsed = parse_msg_payload("1:MINE | broken | 1:DROP")
    assert parsed["segments"] == {1: "MINE"}
    assert parsed["malformed"] == ["broken"]
    assert parsed["duplicates"] == [1]


def test_fifo_token_disposition_and_underflow():
    first = {"id": 1, "disposition": "carried", "disposition_turn": None}
    second = {"id": 2, "disposition": "carried", "disposition_turn": None}
    pool = deque((first, second))
    consumed, underflow = consume_tokens(pool, 3, "planted", 17)
    assert [token["id"] for token in consumed] == [1, 2]
    assert underflow == 1
    assert all(token["disposition"] == "planted" for token in consumed)
    assert all(token["disposition_turn"] == 17 for token in consumed)
