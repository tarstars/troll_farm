import math
import unittest

import orchard_kinetics as ok


class OrchardKineticsTests(unittest.TestCase):
    def test_water_milestones(self) -> None:
        expected = {
            "PLUM": (9, 12),
            "LEMON": (9, 12),
            "APPLE": (6, 8),
            "BANANA": (12, 16),
        }
        for kind, pair in expected.items():
            m = ok.milestones(kind, True)
            self.assertEqual((m.full_size_end_offset, m.first_fruit_end_offset), pair)

    def test_inland_milestones(self) -> None:
        expected = {
            "PLUM": (24, 32),
            "LEMON": (24, 32),
            "APPLE": (27, 36),
            "BANANA": (18, 24),
        }
        for kind, pair in expected.items():
            m = ok.milestones(kind, False)
            self.assertEqual((m.full_size_end_offset, m.first_fruit_end_offset), pair)

    def test_mature_health_and_fell_turns(self) -> None:
        expected = {
            "PLUM": (12, (12, 6, 4, 3)),
            "LEMON": (12, (12, 6, 4, 3)),
            "APPLE": (20, (20, 10, 7, 5)),
            "BANANA": (6, (6, 3, 2, 2)),
        }
        for kind, (health, turns) in expected.items():
            self.assertEqual(ok.tree_health(kind, 4), health)
            self.assertEqual(tuple(ok.mature_fell_turns(kind, p) for p in range(1, 5)), turns)

    def test_plant_turn_tick_makes_size_one(self) -> None:
        for kind in ok.SPECIES:
            state = ok.plant_turn_end_state(kind, True)
            self.assertEqual(state.size, 1)
            self.assertEqual(state.health, ok.tree_health(kind, 1))

    def test_growth_preserves_chop_damage(self) -> None:
        state = ok.plant_turn_end_state("PLUM", True)
        damaged, wood = ok.chop(state, 1)
        self.assertEqual(wood, 0)
        self.assertIsNotNone(damaged)
        assert damaged is not None
        # Advance until the next growth event: health is 7, not reset to untouched size-2 health 8.
        for _ in range(3):
            damaged = ok.tick(damaged, True)
        self.assertEqual(damaged.size, 2)
        self.assertEqual(damaged.health, 7)

    def test_chop_returns_tree_size_as_conservative_wood(self) -> None:
        state = ok.state_at_end_offset("BANANA", True, 12)
        self.assertEqual(state.size, 4)
        for _ in range(2):
            state, wood = ok.chop(state, 3)
            if state is None:
                break
        self.assertIsNone(state)
        self.assertEqual(wood, 4)

    def test_cohort_standing_points(self) -> None:
        # Three water-side apples planted on turns 0, 4 and 8, observed after turn 10:
        # ages 10, 6, 2 -> sizes 4, 4, 2 -> 10 wood -> 40 points.
        self.assertEqual(ok.cohort_standing_points("APPLE", True, [0, 4, 8], 10), 40)

    def test_survival_probability_is_piecewise_and_monotone(self) -> None:
        p_early = ok.survival_probability(0, 50)
        p_late = ok.survival_probability(100, 150)
        self.assertGreater(p_early, p_late)
        self.assertAlmostEqual(p_early, (1.0 - 0.0019) ** 50)
        self.assertAlmostEqual(p_late, (1.0 - 0.008) ** 50)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            ok.effective_cooldown("PEAR", True)
        with self.assertRaises(ValueError):
            ok.mature_fell_turns("PLUM", 0)
        with self.assertRaises(ValueError):
            ok.survival_probability(10, 9)


if __name__ == "__main__":
    unittest.main()
