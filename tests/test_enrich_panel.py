"""Pure tests for controlled-panel replay enrichment."""

import pytest

from cgauto.enrich_panel import enrich_row, needs_enrichment


def replay() -> dict:
    return {
        "scores": [20.0, 10.0],
        "frames": [
            {"keyframe": True},
            {"agentId": 0, "stdout": "MSG baseline;HARVEST 0"},
            {
                "agentId": 1,
                "stdout": "WAIT",
                "keyframe": True,
                "view": 'x {"inputmodule":"0 0 1 0 0 5\\n0 0 0 0 0 2"}',
            },
        ],
    }


def test_enrich_row_adds_corrected_turn_and_command_trace() -> None:
    row = {
        "game_id": 1,
        "scores": [20.0, 10.0],
        "inventories": [[0, 0, 1, 0, 0, 5], [0, 0, 0, 0, 0, 2]],
        "turns": 2,
    }

    enriched = enrich_row(row, replay())

    assert enriched["turns"] == 1
    assert enriched["commands"]["harvest_turns"] == [1]
    assert enriched["commands"]["announcements"] == ["baseline"]


def test_enrich_row_rejects_a_score_mismatch() -> None:
    row = {"game_id": 1, "scores": [19.0, 10.0]}

    with pytest.raises(RuntimeError, match="saved scores"):
        enrich_row(row, replay())


def test_trace_without_agent_identity_requires_replay_enrichment() -> None:
    row = {
        "commands": {},
        "workforce": {"source": "referee_summary", "training_turns": [[], []]},
        "trace": {"agents": []},
    }

    assert needs_enrichment(row) is True
    row["trace"]["agents"] = [{"index": 1, "agent_id": 42}]
    assert needs_enrichment(row) is False
