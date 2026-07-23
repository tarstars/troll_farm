//! D79a consumed-map population preflight for a D40-anchored spatial job scorer.

use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroOpponentMode, MacroSelectionBranch,
    MacroTerminal, D42_JOB_CONTEXT_FEATURES, D42_SHARED_CONTEXT_FEATURES, MACRO_ACTION_PLANES,
    MACRO_CANDIDATE_FEATURES, MACRO_CELLS,
};

const HIDDEN: usize = 8;
const JOB_FEATURES: usize = MACRO_CANDIDATE_FEATURES + D42_JOB_CONTEXT_FEATURES;
const PARAMETERS: usize = HIDDEN * D42_SHARED_CONTEXT_FEATURES
    + HIDDEN
    + HIDDEN * JOB_FEATURES
    + HIDDEN
    + HIDDEN
    + D42_JOB_CONTEXT_FEATURES
    + 1;

const WS_START: usize = 0;
const BS_START: usize = WS_START + HIDDEN * D42_SHARED_CONTEXT_FEATURES;
const WJ_START: usize = BS_START + HIDDEN;
const BJ_START: usize = WJ_START + HIDDEN * JOB_FEATURES;
const V_START: usize = BJ_START + HIDDEN;
const Q_START: usize = V_START + HIDDEN;
const B_INDEX: usize = Q_START + D42_JOB_CONTEXT_FEATURES;

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    theta: [f32; PARAMETERS],
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Work {
    policy: usize,
    task: Task,
}

#[derive(Clone, Copy, Debug, Default)]
struct SpatialStats {
    rate_decisions: u32,
    overrides: u32,
    selected_rank_sum: u64,
    selected_rank_max: u32,
    near_opponent_targets: u32,
    nonfinite_feature_failures: u32,
    illegal_selection_failures: u32,
}

struct Row {
    policy: usize,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    max_own_workers: u8,
    spatial: SpatialStats,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D79a population"));
    let mut lines = source.lines();
    let expected = std::iter::once("policy".to_string())
        .chain((0..PARAMETERS).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D79a population header").unwrap(),
        expected
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D79a population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARAMETERS + 1);
        let mut theta = [0.0f32; PARAMETERS];
        for (target, value) in theta.iter_mut().zip(&fields[1..]) {
            *target = parse(value, "D79a parameter");
            assert!(target.is_finite());
        }
        policies.push(Policy {
            label: fields[0].to_string(),
            theta,
        });
    }
    assert_eq!(
        policies.len(),
        33,
        "D79a requires zero plus 32 random policies"
    );
    assert_eq!(policies[0].label, "zero");
    assert!(policies[0].theta.iter().all(|value| *value == 0.0));
    policies
}

fn shared_tower(
    shared: &[f32; D42_SHARED_CONTEXT_FEATURES],
    theta: &[f32; PARAMETERS],
) -> [f32; HIDDEN] {
    let mut output = [0.0f32; HIDDEN];
    for hidden in 0..HIDDEN {
        let start = WS_START + hidden * D42_SHARED_CONTEXT_FEATURES;
        let affine = theta[BS_START + hidden]
            + theta[start..start + D42_SHARED_CONTEXT_FEATURES]
                .iter()
                .zip(shared)
                .map(|(weight, feature)| weight * feature)
                .sum::<f32>();
        output[hidden] = affine.tanh();
    }
    output
}

fn residual(
    shared_hidden: &[f32; HIDDEN],
    candidate: &[f32; MACRO_CANDIDATE_FEATURES],
    context: &[f32; D42_JOB_CONTEXT_FEATURES],
    theta: &[f32; PARAMETERS],
) -> f32 {
    let mut job_hidden = [0.0f32; HIDDEN];
    for hidden in 0..HIDDEN {
        let start = WJ_START + hidden * JOB_FEATURES;
        let candidate_value = theta[start..start + MACRO_CANDIDATE_FEATURES]
            .iter()
            .zip(candidate)
            .map(|(weight, feature)| weight * feature)
            .sum::<f32>();
        let context_start = start + MACRO_CANDIDATE_FEATURES;
        let context_value = theta[context_start..context_start + D42_JOB_CONTEXT_FEATURES]
            .iter()
            .zip(context)
            .map(|(weight, feature)| weight * feature)
            .sum::<f32>();
        job_hidden[hidden] = (theta[BJ_START + hidden] + candidate_value + context_value).tanh();
    }
    theta[B_INDEX]
        + theta[V_START..V_START + HIDDEN]
            .iter()
            .zip(shared_hidden.iter().zip(job_hidden))
            .map(|(weight, (shared, job))| weight * shared * job)
            .sum::<f32>()
        + theta[Q_START..Q_START + D42_JOB_CONTEXT_FEATURES]
            .iter()
            .zip(context)
            .map(|(weight, feature)| weight * feature)
            .sum::<f32>()
}

fn spatial_action(
    env: &CompleteMacroEnv,
    observation: &MacroCandidateObservation,
    theta: &[f32; PARAMETERS],
    stats: &mut SpatialStats,
) -> usize {
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    if observation.branch != MacroSelectionBranch::Rate {
        return observation.actions[order[0]] as usize;
    }
    stats.rate_decisions += 1;
    let shared = env.d42_shared_context();
    stats.nonfinite_feature_failures +=
        u32::from(shared.iter().any(|feature| !feature.is_finite()));
    let shared_hidden = shared_tower(&shared, theta);
    stats.nonfinite_feature_failures +=
        u32::from(shared_hidden.iter().any(|feature| !feature.is_finite()));

    let denominator = order.len().saturating_sub(1).max(1) as f32;
    let mut best_candidate = order[0];
    let mut best_rank = 0usize;
    let mut best_score = f32::NEG_INFINITY;
    let mut best_near = false;
    for (rank, &candidate) in order.iter().enumerate() {
        let context = env.d42_job_context(observation.actions[candidate]);
        let finite = observation.features[candidate]
            .iter()
            .chain(context.iter())
            .all(|feature| feature.is_finite());
        if !finite {
            stats.nonfinite_feature_failures += 1;
            continue;
        }
        let score = -(rank as f32) / denominator
            + residual(
                &shared_hidden,
                &observation.features[candidate],
                &context,
                theta,
            );
        if !score.is_finite() {
            stats.nonfinite_feature_failures += 1;
            continue;
        }
        let action = observation.actions[candidate];
        let best_action = observation.actions[best_candidate];
        if score.total_cmp(&best_score).is_gt()
            || (score.total_cmp(&best_score).is_eq() && (rank, action) < (best_rank, best_action))
        {
            best_candidate = candidate;
            best_rank = rank;
            best_score = score;
            best_near = action as usize / MACRO_CELLS >= 4 && context[13] > 0.5;
        }
    }
    stats.overrides += u32::from(best_rank > 0);
    stats.selected_rank_sum += best_rank as u64;
    stats.selected_rank_max = stats.selected_rank_max.max(best_rank as u32);
    stats.near_opponent_targets += u32::from(best_near);
    observation.actions[best_candidate] as usize
}

fn play(task: Task, policy_index: usize, policy: &Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut terminal = MacroTerminal::default();
    let mut spatial = SpatialStats::default();
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut max_own_workers = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == task.seat)
        .count() as u8;
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D79a decision loop on {task:?}");
        let observation = env.candidate_observation();
        let mut action = spatial_action(&env, &observation, &policy.theta, &mut spatial);
        if !env.legal_actions().contains(&action) {
            spatial.illegal_selection_failures += 1;
            action = observation.actions[observation.teacher_index] as usize;
        }
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        max_own_workers = max_own_workers.max(terminal.own_workers);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D79a zero-time loop on {task:?}");
    }
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Row {
        policy: policy_index,
        task,
        terminal,
        reward_identity_error,
        max_own_workers,
        spatial,
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        6,
        "usage: d79_spatial_job_population POPULATION START_SEED MAPS OUTPUT THREADS"
    );
    let policies = Arc::new(read_policies(&args[1]));
    let start_seed = parse(&args[2], "start seed");
    let maps: usize = parse(&args[3], "maps");
    let output = &args[4];
    let threads: usize = parse(&args[5], "threads");
    assert!(maps > 0 && threads > 0);
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
                        policy,
                        task: Task {
                            map_seed,
                            seat,
                            opponent,
                        },
                    })
                })
            })
        })
        .collect();
    let work = Arc::new(work);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let policies = Arc::clone(&policies);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index) else {
                    break;
                };
                let row = play(item.task, item.policy, &policies[item.policy]);
                rows.lock().expect("D79a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D79a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D79a row owner")
        .into_inner()
        .expect("D79a row lock");
    rows.sort_by_key(|row| {
        (
            policies[row.policy].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D79a output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\trate_decisions\trate_overrides\tselected_prior_rank_sum\tselected_prior_rank_max\tnear_opponent_targets\tnonfinite_feature_failures\tillegal_selection_failures\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D79a header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            policies[row.policy].label,
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            row.reward_identity_error,
            terminal.own_workers,
            terminal.opponent_workers,
            row.max_own_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            row.spatial.rate_decisions,
            row.spatial.overrides,
            row.spatial.selected_rank_sum,
            row.spatial.selected_rank_max,
            row.spatial.near_opponent_targets,
            row.spatial.nonfinite_feature_failures,
            row.spatial.illegal_selection_failures,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
        )
        .expect("write D79a row");
    }
    writer.flush().expect("flush D79a output");
    eprintln!(
        "saved {} policies x {} maps x 16 tasks = {} rows in {:.3}s",
        policies.len(),
        maps,
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_parameter_layout_has_889_values() {
        assert_eq!(PARAMETERS, 889);
        assert_eq!((WS_START, BS_START, WJ_START, BJ_START), (0, 368, 376, 856));
        assert_eq!((V_START, Q_START, B_INDEX), (864, 872, 888));
    }

    #[test]
    fn zero_parameters_preserve_exact_d40_actions() {
        let theta = [0.0; PARAMETERS];
        for opponent in [0, 1, 4, 7] {
            let mut env =
                CompleteMacroEnv::new(9_670_000, 0, MacroOpponentMode::from_index(opponent));
            let mut stats = SpatialStats::default();
            for _ in 0..120 {
                let observation = env.candidate_observation();
                let selected = spatial_action(&env, &observation, &theta, &mut stats);
                assert_eq!(
                    selected,
                    observation.actions[observation.teacher_index] as usize
                );
                if env.step(selected).done {
                    break;
                }
            }
            assert_eq!(stats.overrides, 0);
            assert_eq!(stats.nonfinite_feature_failures, 0);
        }
    }

    #[test]
    fn spatial_scorer_is_finite_on_legal_rate_candidates() {
        let theta = [0.01; PARAMETERS];
        let mut env = CompleteMacroEnv::new(9_670_001, 1, MacroOpponentMode::GoldAdaptive);
        let mut checked = 0usize;
        for _ in 0..160 {
            let observation = env.candidate_observation();
            let mut stats = SpatialStats::default();
            let action = spatial_action(&env, &observation, &theta, &mut stats);
            assert!(env.legal_actions().contains(&action));
            assert_eq!(stats.nonfinite_feature_failures, 0);
            checked += usize::from(observation.branch == MacroSelectionBranch::Rate);
            if env.step(action).done {
                break;
            }
        }
        assert!(checked > 0);
    }
}
