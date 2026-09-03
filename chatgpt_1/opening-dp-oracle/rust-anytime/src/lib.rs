pub mod model;
pub mod search;

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use crate::model::{
        global_assignment_problem, infeasible_problem, plant_investment_problem, two_stage_problem,
        OpeningAction, IRON, LEMON,
    };
    use crate::search::{replay_actions, SearchLimits, StopReason};

    #[test]
    fn training_cost_uses_referee_formula() {
        let problem = two_stage_problem();
        // target-chop2 = (2, 2, 1, 2), with two existing trolls.
        assert_eq!(problem.training_cost(2, 3), [6, 6, 3, 6]);
    }

    #[test]
    fn joint_assignment_beats_independent_greedy() {
        let problem = global_assignment_problem();
        problem.validate().unwrap();
        let greedy = problem.greedy_incumbent(10_000).unwrap();
        assert_eq!(greedy.state.now, 9);

        let result = problem.hybrid_solve(SearchLimits::proof());
        assert!(result.plan.is_some());
        assert!(result.proven_optimal);
        assert_eq!(result.completion_time(&problem), Some(6));
        assert_eq!(result.optimality_gap(&problem), Some(0));
        assert!(result.stats.pruned_by_dominance > 0);

        let plan = result.plan.unwrap();
        let replayed = replay_actions(&problem, &plan.actions).unwrap();
        assert_eq!(replayed, plan.state);
        assert!(problem.goal_count() <= replayed.workers.len());

        let mut lemon_by_worker_1 = false;
        let mut iron_by_worker_0 = false;
        for action in plan.actions {
            if let OpeningAction::Fetch {
                worker, resource, ..
            } = action
            {
                lemon_by_worker_1 |= worker == 1 && usize::from(resource) == LEMON;
                iron_by_worker_0 |= worker == 0 && usize::from(resource) == IRON;
            }
        }
        assert!(lemon_by_worker_1);
        assert!(iron_by_worker_0);
    }

    #[test]
    fn planting_can_be_part_of_the_optimal_sequence() {
        let problem = plant_investment_problem();
        problem.validate().unwrap();
        let greedy = problem.greedy_incumbent(10_000).unwrap();
        assert_eq!(greedy.state.now, 13);

        let result = problem.hybrid_solve(SearchLimits::proof());
        assert!(result.proven_optimal);
        assert_eq!(result.completion_time(&problem), Some(10));
        let plan = result.plan.unwrap();
        assert!(
            plan.actions
                .iter()
                .any(|action| matches!(action, OpeningAction::Plant { .. }))
        );
        assert_eq!(replay_actions(&problem, &plan.actions).unwrap(), plan.state);
    }

    #[test]
    fn immediate_timeout_returns_the_valid_greedy_incumbent() {
        let problem = global_assignment_problem();
        let mut limits = SearchLimits::online(Duration::ZERO);
        limits.beam_width = 0;
        let result = problem.hybrid_solve(limits);
        assert_eq!(result.stop_reason, StopReason::TimeBudget);
        assert!(!result.proven_optimal);
        assert_eq!(result.completion_time(&problem), Some(9));
        let plan = result.plan.unwrap();
        assert_eq!(replay_actions(&problem, &plan.actions).unwrap(), plan.state);
    }

    #[test]
    fn state_cap_uses_bounded_beam_without_losing_the_incumbent() {
        let problem = global_assignment_problem();
        let limits = SearchLimits {
            wall_time: Some(Duration::from_secs(1)),
            max_expansions: usize::MAX,
            max_states: 4,
            deadline_check_interval: 1,
            beam_width: 2,
            max_beam_rounds: 64,
        };
        let result = problem.hybrid_solve(limits);
        assert!(result.used_beam_fallback);
        assert!(result.plan.is_some());
        assert!(result.completion_time(&problem).unwrap() <= 9);
        let plan = result.plan.unwrap();
        assert_eq!(replay_actions(&problem, &plan.actions).unwrap(), plan.state);
    }

    #[test]
    fn infeasible_model_is_reported_without_false_proof() {
        let problem = infeasible_problem();
        let result = problem.hybrid_solve(SearchLimits::proof());
        assert!(result.plan.is_none());
        assert!(!result.proven_optimal);
        assert_eq!(result.stop_reason, StopReason::Infeasible);
    }

    #[test]
    #[ignore = "release benchmark and parity check"]
    fn larger_two_stage_case_is_19() {
        let problem = two_stage_problem();
        let result = problem.hybrid_solve(SearchLimits::proof());
        assert!(result.proven_optimal);
        assert_eq!(result.completion_time(&problem), Some(19));
    }
}
