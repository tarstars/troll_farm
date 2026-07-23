"""Pure tests for common-seed replay fingerprints."""

from cgauto.analyze_testsession_common_seed_aa import stdout_stream, stream_sha256


def test_stdout_stream_is_player_specific_and_ordered() -> None:
    frames = [
        {"agentId": 1, "stdout": "WAIT\n"},
        {"agentId": 0, "stdout": "MOVE 0 1 1\n"},
        {"agentId": 0, "stderr": "ignored"},
        {"agentId": 1, "stdout": "MOVE 1 2 2\n"},
        {"agentId": 0, "stdout": "WAIT\n"},
    ]

    assert stdout_stream(frames, 0) == ["MOVE 0 1 1\n", "WAIT\n"]
    assert stdout_stream(frames, 1) == ["WAIT\n", "MOVE 1 2 2\n"]
    assert stream_sha256(stdout_stream(frames, 0)) == stream_sha256(
        ["MOVE 0 1 1\n", "WAIT\n"]
    )
