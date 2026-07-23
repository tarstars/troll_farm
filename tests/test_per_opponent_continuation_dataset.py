from cgauto.per_opponent_continuation_dataset import (
    exact_agent_metadata,
    selection_hash,
)


def test_metadata_selection_is_hash_ordered_and_result_blind() -> None:
    agent_id = 123
    battles = [
        {
            "gameId": game_id,
            "done": True,
            "players": [
                {"playerAgentId": agent_id, "position": 0, "nickname": "target"},
                {"playerAgentId": 999, "position": 1, "nickname": "other"},
            ],
            "irrelevant_result": 1000 - game_id,
        }
        for game_id in range(10, 20)
    ]
    rows = exact_agent_metadata(battles, agent_id, {13})
    assert {row["game_id"] for row in rows} == set(range(10, 20)) - {13}
    assert rows == sorted(rows, key=lambda row: (row["selection_hash"], row["game_id"]))
    assert all("irrelevant_result" not in row for row in rows)


def test_selection_hash_is_agent_conditioned_and_stable() -> None:
    assert selection_hash(1, 2) == selection_hash(1, 2)
    assert selection_hash(1, 2) != selection_hash(2, 2)

