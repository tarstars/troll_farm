//! D82a provenance-specific semantic response rollout upper bound.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroOpponentMode, MacroSelectionBranch,
    MacroTerminal, MACRO_ACTION_PLANES, MACRO_CELLS,
};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Arm {
    Control,
    Fell,
    Harvest,
    Renew,
}

impl Arm {
    const ALL: [Self; 4] = [Self::Control, Self::Fell, Self::Harvest, Self::Renew];

    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Fell => "fell",
            Self::Harvest => "harvest",
            Self::Renew => "renew",
        }
    }

    fn plane(self) -> Option<usize> {
        match self {
            Self::Control => None,
            Self::Fell => Some(5),
            Self::Harvest => Some(6),
            Self::Renew => Some(7),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug)]
struct Work {
    arm: Arm,
    task: Task,
}

#[derive(Clone, Copy, Debug)]
struct RootStats {
    root_seen: u32,
    root_turn: i32,
    root_state_hash: u64,
    root_candidate_count: u32,
    arm_available: u32,
    arm_prior_rank: i32,
    arm_action_plane: i32,
    interventions: u32,
    nonfinite_feature_failures: u32,
    illegal_selection_failures: u32,
    fallback_mismatch_failures: u32,
}

impl Default for RootStats {
    fn default() -> Self {
        Self {
            root_seen: 0,
            root_turn: -1,
            root_state_hash: 0,
            root_candidate_count: 0,
            arm_available: 0,
            arm_prior_rank: -1,
            arm_action_plane: -1,
            interventions: 0,
            nonfinite_feature_failures: 0,
            illegal_selection_failures: 0,
            fallback_mismatch_failures: 0,
        }
    }
}

struct Row {
    arm: Arm,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    max_own_workers: u8,
    root: RootStats,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn threatened_own_crop(action: i32, features: &[f32; 44], context: &[f32; 16]) -> bool {
    matches!(action as usize / MACRO_CELLS, 5..=7) && features[31] > 0.5 && context[13] > 0.5
}

fn arm_action(
    env: &CompleteMacroEnv,
    observation: &MacroCandidateObservation,
    arm: Arm,
    stats: &mut RootStats,
) -> usize {
    let teacher = observation.actions[observation.teacher_index] as usize;
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    stats.fallback_mismatch_failures +=
        u32::from(observation.actions[order[0]] as usize != teacher);
    if stats.root_seen > 0 || observation.branch != MacroSelectionBranch::Rate {
        return teacher;
    }

    let mut responses: [Option<(usize, usize)>; 3] = [None; 3];
    for (rank, &candidate) in order.iter().enumerate() {
        let action = observation.actions[candidate];
        let plane = action as usize / MACRO_CELLS;
        if !(5..=7).contains(&plane)
            || observation.features[candidate][31] <= 0.5
            || action as usize == teacher
            || responses[plane - 5].is_some()
        {
            continue;
        }
        let context = env.d42_job_context(action);
        stats.nonfinite_feature_failures += u32::from(
            observation.features[candidate]
                .iter()
                .chain(context.iter())
                .any(|value| !value.is_finite()),
        );
        if threatened_own_crop(action, &observation.features[candidate], &context) {
            responses[plane - 5] = Some((rank, action as usize));
        }
    }
    if responses.iter().all(Option::is_none) {
        return teacher;
    }

    stats.root_seen = 1;
    stats.root_turn = env.state.turn;
    stats.root_state_hash = env.state_hash();
    stats.root_candidate_count = observation.actions.len() as u32;
    if arm == Arm::Control {
        stats.arm_available = 1;
        stats.arm_prior_rank = 0;
        stats.arm_action_plane = (teacher / MACRO_CELLS) as i32;
        return teacher;
    }
    let response = responses[arm.plane().expect("semantic arm") - 5];
    let Some((rank, action)) = response else {
        return teacher;
    };
    stats.arm_available = 1;
    stats.arm_prior_rank = rank as i32;
    stats.arm_action_plane = (action / MACRO_CELLS) as i32;
    stats.interventions = 1;
    action
}

fn play(work: Work) -> Row {
    let mut env = CompleteMacroEnv::new(
        work.task.map_seed,
        work.task.seat,
        MacroOpponentMode::from_index(work.task.opponent),
    );
    let mut terminal = MacroTerminal::default();
    let mut root = RootStats::default();
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut max_own_workers = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == work.task.seat)
        .count() as u8;
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D82a decision loop on {:?}", work.task);
        let observation = env.candidate_observation();
        let mut action = arm_action(&env, &observation, work.arm, &mut root);
        if !env.legal_actions().contains(&action) {
            root.illegal_selection_failures += 1;
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
        assert!(stagnant <= 16, "D82a zero-time loop on {:?}", work.task);
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
        arm: work.arm,
        task: work.task,
        terminal,
        reward_identity_error,
        max_own_workers,
        root,
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d82_threatened_own_crop_rollout START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);

    let work: Vec<_> = Arm::ALL
        .into_iter()
        .flat_map(|arm| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
                        arm,
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
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index).copied() else {
                    break;
                };
                let row = play(item);
                rows.lock().expect("D82a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D82a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D82a row owner")
        .into_inner()
        .expect("D82a row lock");
    rows.sort_by_key(|row| {
        (
            row.arm.label(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D82a output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tarm\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\troot_seen\troot_turn\troot_state_hash\troot_candidate_count\tarm_available\tarm_prior_rank\tarm_action_plane\tinterventions\tnonfinite_feature_failures\tillegal_selection_failures\tfallback_mismatch_failures\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D82a header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.arm.label(),
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
            row.root.root_seen,
            row.root.root_turn,
            row.root.root_state_hash,
            row.root.root_candidate_count,
            row.root.arm_available,
            row.root.arm_prior_rank,
            row.root.arm_action_plane,
            row.root.interventions,
            row.root.nonfinite_feature_failures,
            row.root.illegal_selection_failures,
            row.root.fallback_mismatch_failures,
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
        .expect("write D82a row");
    }
    writer.flush().expect("flush D82a output");
    eprintln!(
        "saved {} D82a rows in {:.3}s",
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn threat_requires_own_provenance_crop_plane_and_proximity() {
        let mut features = [0.0; 44];
        let mut context = [0.0; 16];
        features[31] = 1.0;
        context[13] = 1.0;
        assert!(threatened_own_crop(
            (6 * MACRO_CELLS) as i32,
            &features,
            &context
        ));
        features[31] = 0.0;
        assert!(!threatened_own_crop(
            (6 * MACRO_CELLS) as i32,
            &features,
            &context
        ));
    }

    #[test]
    fn semantic_arms_share_root_and_obey_one_decision_budget() {
        let rows: Vec<_> = Arm::ALL
            .into_iter()
            .map(|arm| {
                play(Work {
                    arm,
                    task: Task {
                        map_seed: 9_914_000,
                        seat: 0,
                        opponent: 4,
                    },
                })
            })
            .collect();
        assert!(rows.iter().all(|row| row.root.interventions <= 1));
        assert!(rows
            .iter()
            .all(|row| row.root.nonfinite_feature_failures == 0));
        let control = &rows[0].root;
        for row in &rows[1..] {
            assert_eq!(row.root.root_seen, control.root_seen);
            assert_eq!(row.root.root_turn, control.root_turn);
            assert_eq!(row.root.root_state_hash, control.root_state_hash);
            assert_eq!(row.root.root_candidate_count, control.root_candidate_count);
        }
    }
}
