"""Tests for deterministic agent selection in the replay collector."""

import pytest

from data.scripts.collect import parse_args, selected_players


def user(agent_id: int, pseudo: str, league: int) -> dict:
    return {
        "agentId": agent_id,
        "pseudo": pseudo,
        "league": {"divisionIndex": league},
        "codingamer": {"userId": agent_id + 1000},
    }


def test_default_selection_keeps_pseudo_and_top_cohorts() -> None:
    selected, ours, legend, gold = selected_players(
        [user(10, "tass", 4), user(20, "legend", 5), user(30, "gold", 4)]
    )

    assert (ours, legend, gold) == (1, 1, 2)
    assert selected[10]["group"] == "ours"
    assert selected[20]["group"] == "legend_top"
    assert selected[30]["group"] == "gold_top"


def test_explicit_agent_only_does_not_require_leaderboard_membership() -> None:
    selected, ours, legend, gold = selected_players(
        [user(20, "legend", 5)], agent_id=6551038, agent_only=True
    )

    assert (ours, legend, gold) == (1, 0, 0)
    assert selected == {
        6551038: {
            "pseudo": "agent-6551038",
            "agentId": 6551038,
            "userId": None,
            "group": "ours",
            "leagueIndex": None,
            "league": None,
            "globalRank": None,
            "score": None,
        }
    }


def test_agent_only_requires_an_explicit_id() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--agent-only"])

