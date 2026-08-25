#!/usr/bin/env python3
"""Unit tests for the C-7 command-stream pairing -- ON THE CASE THE CORPUS NEVER PRODUCED.

`c7_poison_control.py --panel` found ZERO turns granting two or more exchanges, on either arm,
over 34 fixtures and 240 panel games, even with the predicate gutted. So the run cannot show that
the pairing survives ambiguity: there was no ambiguity to survive. These tests fabricate the turn
the corpus withheld and check the two pairings against each other on it, so the claim is
"tested at the function level, never observed in the corpus" and not "tested by the run".

    python3 claude_1/cure2/test_c7_pairing.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from c7_poison_control import counters, exchange_pairs   # noqa: E402


class TestExchangePairs(unittest.TestCase):
    def test_single_exchange_is_forced_and_both_pairings_agree(self):
        cells = {0: (5, 2), 2: (4, 2)}
        dest = {0: (4, 2), 2: (5, 2)}
        branch = {0: "S", 2: "X"}
        pairs, incidental = exchange_pairs(cells, dest, branch)
        self.assertEqual(pairs, [(0, 2)])
        self.assertEqual(incidental, [])

    def test_two_exchanges_on_one_turn(self):
        """The wire would report movers [0,4] and displaced [2,6] and could not say which went
        with which; the commands say it exactly."""
        cells = {0: (5, 2), 2: (4, 2), 4: (9, 7), 6: (9, 8)}
        dest = {0: (4, 2), 2: (5, 2), 4: (9, 8), 6: (9, 7)}
        branch = {0: "S", 2: "X", 4: "S", 6: "X"}
        pairs, incidental = exchange_pairs(cells, dest, branch)
        self.assertEqual(sorted(pairs), [(0, 2), (4, 6)])
        self.assertEqual(incidental, [])
        # The wire pairing, faced with 2 S and 2 X, has four candidate matchings and no way to
        # choose: {0-2,4-6} (the truth), {0-6,4-2}, and either alone. It reports AMBIGUOUS.
        self.assertEqual(len(branch), 4)

    def test_the_wrong_matching_is_the_one_that_would_be_guessed(self):
        """Ascending-order zip -- the natural guess -- picks the WRONG pairs here, which is why
        the published control refuses to guess and this one reads the commands instead."""
        cells = {0: (5, 2), 2: (9, 8), 4: (9, 7), 6: (4, 2)}
        dest = {0: (4, 2), 6: (5, 2), 4: (9, 8), 2: (9, 7)}
        branch = {0: "S", 6: "X", 4: "S", 2: "X"}
        pairs, _ = exchange_pairs(cells, dest, branch)
        self.assertEqual(sorted(pairs), [(0, 6), (2, 4)])
        movers, displaced = sorted([0, 4]), sorted([2, 6])
        guessed = sorted(tuple(sorted(p)) for p in zip(movers, displaced))
        self.assertEqual(guessed, [(0, 2), (4, 6)])
        self.assertNotEqual(guessed, sorted(pairs))

    def test_incidental_exchange_is_not_the_rule(self):
        """Two planners crossing on their own is a mutual position exchange with no S/X codes.
        It is reported, not counted as a rule exchange -- otherwise C-5/C-6 would count swaps the
        predicate never granted."""
        cells = {0: (5, 2), 2: (4, 2)}
        dest = {0: (4, 2), 2: (5, 2)}
        branch = {0: "P", 2: "P"}
        pairs, incidental = exchange_pairs(cells, dest, branch)
        self.assertEqual(pairs, [])
        self.assertEqual(len(incidental), 1)

    def test_a_lone_mover_into_a_vacated_cell_is_not_a_pair(self):
        cells = {0: (5, 2), 2: (4, 2)}
        dest = {0: (4, 2), 2: (3, 2)}
        branch = {0: "S", 2: "X"}
        self.assertEqual(exchange_pairs(cells, dest, branch)[0], [])


class TestCounters(unittest.TestCase):
    def test_c6_fires_on_consecutive_turns_and_c5_within_six(self):
        events = [{"game": "g", "turn": 3, "pair": (0, 2)},
                  {"game": "g", "turn": 4, "pair": (0, 2)},
                  {"game": "g", "turn": 20, "pair": (0, 2)}]
        c5, c6, pairs = counters(events)
        self.assertEqual(len(c6), 1)
        self.assertEqual(len(c5), 1)
        self.assertEqual(pairs, {"g:0-2": [3, 4, 20]})

    def test_a_multi_exchange_turn_contributes_every_pair(self):
        """The point of the whole exercise: two exchanges on turn 4 are two counted fires, not
        one ambiguous turn."""
        events = [{"game": "g", "turn": 3, "pair": (0, 2)},
                  {"game": "g", "turn": 3, "pair": (4, 6)},
                  {"game": "g", "turn": 4, "pair": (0, 2)},
                  {"game": "g", "turn": 4, "pair": (4, 6)}]
        c5, c6, _ = counters(events)
        self.assertEqual(len(c6), 2)
        self.assertEqual(len(c5), 2)

    def test_different_games_never_pair_across(self):
        events = [{"game": "a", "turn": 3, "pair": (0, 2)},
                  {"game": "b", "turn": 4, "pair": (0, 2)}]
        c5, c6, _ = counters(events)
        self.assertEqual((len(c5), len(c6)), (0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
