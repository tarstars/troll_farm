from __future__ import annotations

import json
from pathlib import Path

from cgauto.make_agent_initial_dataset import records


def test_records_filter_sort_and_render_relative_seat(tmp_path: Path) -> None:
    game = {
        "gameId": 9,
        "frames": [
            {
                "view": " 0\n" + json.dumps(
                    {
                        "global": {"inputmodule": "3 1\n0.1"},
                        "frame": {
                            "diff": "10 W 00001111;20 W 12011111",
                            "inputmodule": "1 2 3 4 5 6\n6 5 4 3 2 1",
                        },
                    }
                )
            }
        ],
    }
    (tmp_path / "9.json").write_text(json.dumps(game))
    analysis = {
        "occurrences": [
            {"agent_id": 2, "game_id": 9, "seat": 1},
            {"agent_id": 3, "game_id": 10, "seat": 0},
        ]
    }

    rendered = records(analysis, 2, tmp_path)

    assert len(rendered) == 1
    assert rendered[0].startswith("SEED 9\n3 1\n1.0\n")
    assert "6 5 4 3 2 1\n1 2 3 4 5 6\n" in rendered[0]
