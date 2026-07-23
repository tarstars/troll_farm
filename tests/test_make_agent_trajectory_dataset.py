from __future__ import annotations

from cgauto.make_agent_trajectory_dataset import relative_map, render_state


def test_relative_map_swaps_only_player_shacks() -> None:
    map_data = {"rows": ["0.+", "~1."]}
    assert relative_map(map_data, 0) == ["0.+", "~1."]
    assert relative_map(map_data, 1) == ["1.+", "~0."]


def test_render_state_uses_relative_players_and_inventory_order() -> None:
    state = {
        "inventories": [[1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1]],
        "plants": [],
        "units": [
            {
                "id": 7,
                "player": 1,
                "x": 3,
                "y": 4,
                "ms": 2,
                "cc": 3,
                "hp": 0,
                "chop": 2,
                "carry": [0, 0, 0, 0, 0, 1],
            }
        ],
    }

    rendered = render_state(state, 1)

    assert rendered.startswith("6 5 4 3 2 1\n1 2 3 4 5 6\n0\n1\n")
    assert "7 0 3 4 2 3 0 2 0 0 0 0 0 1\n" in rendered
