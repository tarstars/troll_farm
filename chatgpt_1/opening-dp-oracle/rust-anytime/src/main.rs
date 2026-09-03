use std::time::Duration;

use opening_dp_anytime::model::{
    global_assignment_problem, plant_investment_problem, two_stage_problem, OpeningProblem,
};
use opening_dp_anytime::search::{replay_actions, SearchLimits};

fn print_result(name: &str, problem: &OpeningProblem, limits: SearchLimits, show_plan: bool) {
    let greedy = problem.greedy_incumbent(10_000);
    let greedy_turn = greedy.as_ref().map(|plan| plan.state.now);
    let result = problem.hybrid_solve(limits);
    let turn = result.completion_time(problem);
    let gap = result.optimality_gap(problem);
    println!(
        "case={name} greedy={greedy_turn:?} result={turn:?} lower={:?} gap={gap:?} proven={} stop={:?} beam={} elapsed_ms={:.3} astar_expanded={} astar_generated={} astar_nodes={} astar_peak_queue={} dominance_pruned={} bound_pruned={} beam_expanded={} beam_generated={} beam_peak_width={}",
        result.lower_bound_at_stop,
        result.proven_optimal,
        result.stop_reason,
        result.used_beam_fallback,
        result.stats.elapsed.as_secs_f64() * 1_000.0,
        result.stats.astar_expanded,
        result.stats.astar_generated,
        result.stats.astar_nodes,
        result.stats.astar_peak_queue,
        result.stats.pruned_by_dominance,
        result.stats.pruned_by_bound,
        result.stats.beam_expanded,
        result.stats.beam_generated,
        result.stats.beam_peak_width,
    );

    if let Some(plan) = result.plan {
        let replayed = replay_actions(problem, &plan.actions).expect("returned plan must replay");
        assert_eq!(replayed, plan.state);
        if show_plan {
            for action in plan.actions {
                println!("  {}", action.describe(problem));
            }
        }
    }
}

fn run_small() {
    print_result(
        "joint-assignment",
        &global_assignment_problem(),
        SearchLimits::proof(),
        true,
    );
    print_result(
        "plant-investment",
        &plant_investment_problem(),
        SearchLimits::proof(),
        true,
    );
}

fn run_bench() {
    print_result(
        "two-stage-proof",
        &two_stage_problem(),
        SearchLimits::proof(),
        false,
    );
}

fn run_online() {
    let problem = two_stage_problem();
    for millis in [0_u64, 1, 5, 10, 25, 50, 100, 250, 750] {
        let mut limits = SearchLimits::online(Duration::from_millis(millis));
        limits.max_states = 100_000;
        limits.beam_width = 2_048;
        print_result(&format!("online-{millis}ms"), &problem, limits, false);
    }
}

fn main() {
    match std::env::args().nth(1).as_deref() {
        None | Some("small") => run_small(),
        Some("bench") => run_bench(),
        Some("online") => run_online(),
        Some(other) => {
            eprintln!("unknown command {other:?}; use small, bench or online");
            std::process::exit(2);
        }
    }
}
