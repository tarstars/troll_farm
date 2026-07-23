from __future__ import annotations

from cgauto.opponent_crop_field_prefix_replication import (
    block_report,
    build_manifest,
    stable_prefix,
)


def battle(game_id: int, agent: int = 6559583, submission: int = 41009991) -> dict:
    return {
        "gameId": game_id,
        "done": True,
        "players": [{"playerAgentId": agent, "submissionId": submission}],
    }


def test_manifest_takes_exactly_the_82_games_after_the_recent_block() -> None:
    recent = list(range(1000, 1080))
    older = list(range(900, 982))
    result = build_manifest(
        [battle(game_id) for game_id in recent + older], recent
    )
    assert result["discovery"]["game_ids"] == older[:40]
    assert result["replication"]["game_ids"] == older[40:]


def test_stable_prefix_requires_ten_more_exact_turns_or_game_end() -> None:
    row = {
        "candidate_first_divergence_turn": 20,
        "admissible_first_divergence": True,
        "turns": 100,
        "resident_first_mismatch_turn": 31,
    }
    assert stable_prefix(row)
    row["resident_first_mismatch_turn"] = 30
    assert not stable_prefix(row)
    row.update(turns=25, resident_first_mismatch_turn=None)
    assert stable_prefix(row)


def test_block_gate_keeps_full_stream_exactness_descriptive() -> None:
    rows = []
    for index in range(24):
        rows.append(
            {
                "candidate_first_divergence_turn": 10,
                "admissible_first_divergence": True,
                "turns": 100,
                "resident_first_mismatch_turn": 50,
                "resident_full_stream_exact": False,
                "first_divergence_explanation": {"explained": True},
                "unknown_diff_updates": 0,
                "opponent": f"opponent-{index % 8}",
                "margin": 0,
            }
        )
    result = block_report("discovery", rows, [], 24, 24)
    assert result["resident_full_stream_exact"] == 0
    assert result["prospective_gate_passed"]
