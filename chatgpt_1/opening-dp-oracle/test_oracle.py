from __future__ import annotations

import unittest

from oracle import astar_dp, replay_actions
from reduced_opening import (
    APPLE,
    IRON,
    LEMON,
    PLUM,
    OpeningProblem,
    SourceState,
    WorkerSpec,
    global_assignment_problem,
    greedy_incumbent,
    plant_investment_problem,
)


class OpeningOracleTests(unittest.TestCase):
    def test_training_cost_uses_referee_formula(self) -> None:
        spec = WorkerSpec("x", movement=2, capacity=3, harvest=1, chop=2)
        self.assertEqual(
            OpeningProblem.training_cost(2, spec),
            (2 + 2**2, 2 + 3**2, 2 + 1**2, 2 + 2**2),
        )

    def test_joint_assignment_beats_independent_greedy(self) -> None:
        problem = global_assignment_problem()
        greedy = greedy_incumbent(problem)
        self.assertIsNotNone(greedy)
        assert greedy is not None
        self.assertEqual(problem.elapsed(greedy.state), 9)

        result = astar_dp(problem, incumbent=greedy)
        self.assertTrue(result.found)
        self.assertTrue(result.proven_optimal)
        self.assertEqual(result.completion_time, 6)
        self.assertEqual(result.optimality_gap, 0.0)
        self.assertGreater(result.stats.pruned_by_dominance, 0)

        replayed = replay_actions(problem, result.actions)
        self.assertTrue(problem.is_goal(replayed))
        self.assertEqual(replayed, result.goal_state)

        fetched = {
            (action.resource, action.worker)
            for action in result.actions
            if action.kind == "FETCH"
        }
        self.assertIn((LEMON, 1), fetched)
        self.assertIn((IRON, 0), fetched)

    def test_planting_can_be_part_of_the_optimal_sequence(self) -> None:
        problem = plant_investment_problem()
        greedy = greedy_incumbent(problem)
        self.assertIsNotNone(greedy)
        assert greedy is not None
        self.assertEqual(problem.elapsed(greedy.state), 13)

        result = astar_dp(problem, incumbent=greedy)
        self.assertTrue(result.proven_optimal)
        self.assertEqual(result.completion_time, 10)
        self.assertTrue(any(action.kind == "PLANT" for action in result.actions))
        self.assertEqual(replay_actions(problem, result.actions), result.goal_state)

    def test_budgeted_search_returns_a_live_optimality_gap(self) -> None:
        problem = global_assignment_problem()
        greedy = greedy_incumbent(problem)
        assert greedy is not None

        result = astar_dp(problem, incumbent=greedy, max_expansions=0)
        self.assertTrue(result.found)
        self.assertFalse(result.proven_optimal)
        self.assertEqual(result.completion_time, 9)
        self.assertEqual(result.stop_reason, "expansion budget exhausted")
        self.assertIsNotNone(result.lower_bound_at_stop)
        self.assertIsNotNone(result.optimality_gap)
        assert result.lower_bound_at_stop is not None
        assert result.optimality_gap is not None
        self.assertLessEqual(result.lower_bound_at_stop, 6)
        self.assertGreater(result.optimality_gap, 0)

    def test_infeasible_model_is_reported_without_a_false_proof(self) -> None:
        worker = WorkerSpec("starter", 1, 1, 1, 0)
        target = WorkerSpec("target", 1, 1, 0, 0)
        problem = OpeningProblem(
            initial_bank_value=(2, 0, 1, 1),
            initial_workers_value=(worker,),
            initial_sources_value=(
                SourceState("plum", PLUM, distance=1, stock=3),
                SourceState("apple", APPLE, distance=1, stock=3),
            ),
            training_stages=((target,),),
            max_turn=20,
        )
        result = astar_dp(problem)
        self.assertFalse(result.found)
        self.assertFalse(result.proven_optimal)
        self.assertIsNone(result.completion_time)


if __name__ == "__main__":
    unittest.main(verbosity=2)
