#!/usr/bin/env python3
"""Run the hybrid trial-first + A*/DP prototype on deterministic examples."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from oracle import astar_dp, replay_actions
from reduced_opening import (
    global_assignment_problem,
    greedy_incumbent,
    plant_investment_problem,
    two_stage_problem,
)


def solve(name: str, problem, budget: int | None) -> None:
    greedy = greedy_incumbent(problem)
    result = astar_dp(problem, incumbent=greedy, max_expansions=budget)
    replayed = replay_actions(problem, result.actions)
    assert result.goal_state is None or replayed == result.goal_state

    print(f"\n=== {name} ===")
    print(
        json.dumps(
            {
                "greedy_completion_turn": None
                if greedy is None
                else problem.elapsed(greedy.state),
                "best_completion_turn": result.completion_time,
                "proven_optimal": result.proven_optimal,
                "lower_bound_at_stop": result.lower_bound_at_stop,
                "optimality_gap": result.optimality_gap,
                "stop_reason": result.stop_reason,
                "stats": asdict(result.stats),
            },
            indent=2,
            sort_keys=True,
        )
    )
    for action in result.actions:
        print(f"  {action}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        choices=("all", "assignment", "plant", "two-stage"),
        default="all",
    )
    parser.add_argument(
        "--max-expansions",
        type=int,
        default=None,
        help="turn exact A* into an anytime bounded search",
    )
    args = parser.parse_args()

    cases = []
    if args.case in ("all", "assignment"):
        cases.append(("global worker assignment", global_assignment_problem()))
    if args.case in ("all", "plant"):
        cases.append(("plant now versus distant harvest", plant_investment_problem()))
    if args.case == "two-stage":
        cases.append(("larger two-stage opening", two_stage_problem()))

    for name, problem in cases:
        solve(name, problem, args.max_expansions)


if __name__ == "__main__":
    main()
