from cgauto import run_orchard_ab_night_cycle as cycle


def test_sequence_is_four_complete_cycles_and_ends_safe() -> None:
    assert cycle.SEQUENCE == ["no-orchard", "orchard"] * 4
    assert cycle.SEQUENCE.count("no-orchard") == 4
    assert cycle.SEQUENCE.count("orchard") == 4
    assert cycle.SEQUENCE[-1] == "orchard"


def test_checkpoint_scrub_replaces_opponent_names() -> None:
    payload = {"rows": [{"opponent": "PersonalName"}], "unexpected_rows": []}
    assert cycle.scrub_checkpoint(payload)["rows"][0]["opponent"] == "PLAYER_OPPONENT"
