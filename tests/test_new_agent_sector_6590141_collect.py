from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chatgpt_1.new_agent_sector_6590141_collect import initial_sector
from cgauto.e7_type_to_cut_audit import focus_geometry
from sim.mapgen import generate_bronze


def parser_map(game) -> dict:
    rows = []
    for y in range(game.height):
        chars = []
        for x in range(game.width):
            cell = (x, y)
            if cell == game.shacks[0]:
                char = "0"
            elif cell == game.shacks[1]:
                char = "1"
            elif cell in game.iron:
                char = "+"
            elif cell in game.water:
                char = "~"
            elif cell in game.walkable:
                char = "."
            else:
                char = "#"
            chars.append(char)
        rows.append("".join(chars))
    return {
        "w": game.width,
        "h": game.height,
        "rows": rows,
        "trees0": [
            {
                "type": plant.type,
                "x": plant.x,
                "y": plant.y,
                "size": plant.size,
                "fruits": plant.fruits,
                "health": plant.health,
                "stage": plant.size + plant.fruits,
            }
            for plant in game.plants
        ],
    }


class NewAgentSectorCollectorTests(unittest.TestCase):
    def test_live_geometry_matches_original_e7_for_all_roots_and_seats(self) -> None:
        selected = []
        for seed in range(60):
            game = generate_bronze(seed)
            map_data = parser_map(game)
            for seat in (0, 1):
                original = focus_geometry(game, seat)
                live = initial_sector(map_data, seat)
                self.assertEqual(
                    live["lemon_distance_sum"],
                    original["distance_sums"]["LEMON"],
                )
                self.assertEqual(
                    live["plum_distance_sum"],
                    original["distance_sums"]["PLUM"],
                )
                self.assertEqual(
                    live["parent_default_species"],
                    original["chosen_species"],
                )
                expected = (
                    original["chosen_species"] == "LEMON"
                    and original["distance_sums"]["PLUM"]
                    - original["distance_sums"]["LEMON"]
                    <= 8
                )
                self.assertEqual(live["frozen_sector_selected"], expected)
                self.assertEqual(
                    live["candidate_species"],
                    "PLUM" if expected else original["chosen_species"],
                )
            if initial_sector(map_data, 0)["frozen_sector_selected"]:
                selected.append(seed)
        self.assertEqual(
            selected,
            [17, 18, 20, 25, 27, 29, 32, 35, 45, 50, 52, 56, 57],
        )


if __name__ == "__main__":
    unittest.main()
