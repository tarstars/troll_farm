#!/usr/bin/env python3
"""Boundary tests for referee.py — the rules the recorded matches cannot exercise, because the
reference bot only ever prints valid commands.  Standard library only.

    python3 -m unittest cleanroom/package/harness/test_referee.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import referee  # noqa: E402


def small_game(rows, inv=(9, 9, 9, 9, 9, 0)):
    """A game from a hand-drawn map; trolls 0 and 1 start on their shacks."""
    shacks = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in "01":
                shacks[int(ch)] = (x, y)
    spec = {"map_id": "test", "width": len(rows[0]), "height": len(rows), "rows": rows,
            "inventories": [list(inv), list(inv)], "trees": [],
            "trolls": [{"id": p, "player": p, "x": shacks[p][0], "y": shacks[p][1],
                        "ms": 1, "cc": 1, "hp": 1, "chop": 1} for p in (0, 1)]}
    return referee.Game(spec)


ROWS = ["0.....", "......", ".....1"]


def parsed(game, seat0="", seat1=""):
    return [referee.parse(seat0, game, 0), referee.parse(seat1, game, 1)]


class Items(unittest.TestCase):
    def test_numeric_item_codes_are_accepted(self):
        game = small_game(ROWS)
        out = referee.parse("PICK 0 1", game, 0)
        self.assertEqual(out["PICK"], [(0, "LEMON")])

    def test_lowercase_verbs_are_accepted(self):
        game = small_game(ROWS)
        out = referee.parse("move 0 1 0", game, 0)
        self.assertEqual(out["MOVE"], {0: (1, 0)})

    def test_plant_iron_or_wood_is_refused_without_harm(self):
        game = small_game(ROWS)
        game.units[0]["x"], game.units[0]["y"] = 1, 0
        game.units[0]["carry"][referee.IRON] = 1
        out = referee.parse("PLANT 0 IRON;PLANT 0 5", game, 0)
        self.assertEqual(out["PLANT"], [])
        game.apply_turn(parsed(game))          # must not crash
        self.assertEqual(game.trees, [])

    def test_unknown_item_name_is_fatal(self):
        game = small_game(ROWS)
        with self.assertRaises(referee.Illegal):
            referee.parse("PICK 0 GOLD", game, 0)

    def test_unknown_verb_is_fatal(self):
        game = small_game(ROWS)
        with self.assertRaises(referee.Illegal):
            referee.parse("FLY 0", game, 0)


class Training(unittest.TestCase):
    def moved_off(self, game):
        game.units[0]["x"], game.units[0]["y"] = 1, 0

    def test_out_of_range_talents_are_refused_without_harm(self):
        game = small_game(ROWS)
        self.moved_off(game)
        for bundle in ("TRAIN 0 1 0 1", "TRAIN 1 1 4 1", "TRAIN 1 1 0 21", "TRAIN 99 1 0 1",
                       "TRAIN 1 1001 0 1", "TRAIN 1 -1 0 1"):
            before = list(game.inventories[0])
            game.apply_turn(parsed(game, bundle))
            self.assertEqual(len(game.units), 2, bundle)
            self.assertEqual(game.inventories[0], before, bundle)

    def test_boundary_talents_are_legal(self):
        game = small_game(ROWS, inv=(500, 500, 500, 500, 500, 0))
        self.moved_off(game)
        game.apply_turn(parsed(game, "TRAIN 1 0 3 20"))
        self.assertEqual(len(game.units), 3)

    def test_at_most_one_train_succeeds_per_turn(self):
        game = small_game(ROWS, inv=(50, 50, 50, 50, 50, 0))
        self.moved_off(game)
        game.apply_turn(parsed(game, "TRAIN 1 1 0 1;TRAIN 1 1 0 1"))
        self.assertEqual(len(game.units), 3)           # the second is blocked by the first's troll

    def test_a_later_train_can_succeed_if_earlier_ones_are_refused(self):
        game = small_game(ROWS, inv=(50, 50, 50, 50, 50, 0))
        self.moved_off(game)
        game.apply_turn(parsed(game, "TRAIN 0 1 0 1;TRAIN 1 1 0 1"))
        self.assertEqual(len(game.units), 3)

    def test_shack_stays_occupied_until_the_new_troll_moves(self):
        game = small_game(ROWS, inv=(50, 50, 50, 50, 50, 0))
        self.moved_off(game)
        game.apply_turn(parsed(game, "TRAIN 1 1 0 1"))
        self.assertEqual(len(game.units), 3)
        game.apply_turn(parsed(game, "TRAIN 1 1 0 1"))  # new troll still on the shack
        self.assertEqual(len(game.units), 3)
        game.apply_turn(parsed(game, "MOVE 2 0 1;TRAIN 1 1 0 1"))  # it moves first (MOVE before TRAIN)
        self.assertEqual(len(game.units), 4)

    def test_troll_on_the_shack_on_turn_1_blocks_training(self):
        game = small_game(ROWS, inv=(50, 50, 50, 50, 50, 0))
        game.apply_turn(parsed(game, "TRAIN 1 1 0 1"))
        self.assertEqual(len(game.units), 2)

    def test_iron_is_waived_on_a_map_without_iron(self):
        game = small_game(ROWS, inv=(9, 9, 9, 9, 0, 0))
        self.moved_off(game)
        game.apply_turn(parsed(game, "TRAIN 1 1 0 2"))
        self.assertEqual(len(game.units), 3)

    def test_a_drop_this_turn_does_not_pay_for_a_train_this_turn(self):
        game = small_game(ROWS, inv=(0, 9, 9, 9, 9, 0))
        self.moved_off(game)
        game.units[0]["carry"][0] = 1                     # carrying a plum, next to the shack
        game.units[0]["cc"] = 2
        game.apply_turn(parsed(game, "DROP 0;TRAIN 1 1 0 1"))
        self.assertEqual(len(game.units), 2)
        self.assertEqual(game.inventories[0][0], 1)       # the plum was banked, after the train check


class Trees(unittest.TestCase):
    def test_a_seed_planted_this_turn_cannot_be_chopped_this_turn(self):
        game = small_game(ROWS)
        game.units[0]["x"], game.units[0]["y"] = 2, 1
        game.units[1]["x"], game.units[1]["y"] = 2, 1
        game.units[0]["carry"][3] = 1                     # a banana
        game.units[1]["chop"] = 3
        game.apply_turn(parsed(game, "PLANT 0 BANANA", "CHOP 1"))
        self.assertEqual(len(game.trees), 1)
        self.assertEqual((game.trees[0]["size"], game.trees[0]["health"]), (1, 3))

    def test_last_fruit_duplicates_and_last_wood_duplicates(self):
        game = small_game(ROWS)
        game.trees.append({"type": "BANANA", "x": 2, "y": 1, "size": 1, "health": 1, "fruits": 1, "cooldown": 5})
        for u in game.units:
            u["x"], u["y"] = 2, 1
        game.apply_turn(parsed(game, "HARVEST 0", "HARVEST 1"))
        self.assertEqual([u["carry"][3] for u in game.units], [1, 1])
        game.trees[0]["fruits"] = 0
        for u in game.units:
            u["carry"] = [0] * 6                          # room for the wood
        game.apply_turn(parsed(game, "CHOP 0", "CHOP 1"))
        self.assertEqual(game.trees, [])
        self.assertEqual([u["carry"][referee.WOOD] for u in game.units], [1, 1])


class Timing(unittest.TestCase):
    def test_third_strike_loses(self):
        self.assertEqual(referee.STRIKES_TO_LOSE, 3)


if __name__ == "__main__":
    unittest.main()
