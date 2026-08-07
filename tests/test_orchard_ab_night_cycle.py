from cgauto import run_orchard_ab_night_cycle as cycle


def test_sequence_is_four_complete_cycles_and_ends_safe() -> None:
    assert cycle.SEQUENCE == ["no-orchard", "orchard"] * 4
    assert cycle.SEQUENCE.count("no-orchard") == 4
    assert cycle.SEQUENCE.count("orchard") == 4
    assert cycle.SEQUENCE[-1] == "orchard"


def test_checkpoint_scrub_replaces_opponent_names() -> None:
    payload = {"rows": [{"opponent": "PersonalName"}], "unexpected_rows": []}
    assert cycle.scrub_checkpoint(payload)["rows"][0]["opponent"] == "PLAYER_OPPONENT"


def test_source_recovery_uses_controller_session_file(monkeypatch) -> None:
    commands = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, *, check=True):
        commands.append(command)
        return Result()

    monkeypatch.setattr(cycle, "run", fake_run)
    cycle.recover_source("a" * 64)
    assert commands[0][-2:] == ["--session-file", str(cycle.api_submit_once.SESSION_FILE)]
