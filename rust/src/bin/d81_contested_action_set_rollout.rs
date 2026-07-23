//! D81a exact one-boundary rollout action-set audit over D40.

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
    Rank1,
    Rank2,
    Rank3,
}

impl Arm {
    const ALL: [Self; 4] = [Self::Control, Self::Rank1, Self::Rank2, Self::Rank3];

    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Rank1 => "rank_1",
            Self::Rank2 => "rank_2",
            Self::Rank3 => "rank_3",
        }
    }

    fn rank(self) -> usize {
        match self {
            Self::Control => 0,
            Self::Rank1 => 1,
            Self::Rank2 => 2,
            Self::Rank3 => 3,
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
    arm_rank: i32,
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
            arm_rank: -1,
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

fn contested_crop(action: i32, context: &[f32; 16]) -> bool {
    matches!(action as usize / MACRO_CELLS, 5..=7) && context[13] > 0.5
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
    if stats.root_seen > 0 || observation.branch != MacroSelectionBranch::Rate || order.len() < 2 {
        return teacher;
    }

    let anchor_context = env.d42_job_context(observation.actions[order[0]]);
    stats.nonfinite_feature_failures += u32::from(
        observation.features[order[0]]
            .iter()
            .chain(anchor_context.iter())
            .any(|value| !value.is_finite()),
    );
    if contested_crop(observation.actions[order[0]], &anchor_context) {
        return teacher;
    }

    let mut contested = [None; 4];
    for (rank, &candidate) in order.iter().enumerate().skip(1).take(3) {
        let context = env.d42_job_context(observation.actions[candidate]);
        stats.nonfinite_feature_failures += u32::from(
            observation.features[candidate]
                .iter()
                .chain(context.iter())
                .any(|value| !value.is_finite()),
        );
        let action = observation.actions[candidate];
        if contested_crop(action, &context) {
            contested[rank] = Some(action as usize);
        }
    }
    if contested.iter().all(Option::is_none) {
        return teacher;
    }

    stats.root_seen = 1;
    stats.root_turn = env.state.turn;
    stats.root_state_hash = env.state_hash();
    stats.root_candidate_count = observation.actions.len() as u32;
    stats.arm_rank = arm.rank() as i32;
    if arm == Arm::Control {
        stats.arm_available = 1;
        stats.arm_action_plane = (teacher / MACRO_CELLS) as i32;
        return teacher;
    }
    let Some(action) = contested[arm.rank()] else {
        return teacher;
    };
    stats.arm_available = 1;
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
        assert!(decisions <= 5_000, "D81a decision loop on {:?}", work.task);
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
        assert!(stagnant <= 16, "D81a zero-time loop on {:?}", work.task);
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
        "usage: d81_contested_action_set_rollout START_SEED MAPS OUTPUT THREADS"
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
                rows.lock().expect("D81a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D81a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D81a row owner")
        .into_inner()
        .expect("D81a row lock");
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
        .expect("create D81a output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tarm\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\troot_seen\troot_turn\troot_state_hash\troot_candidate_count\tarm_available\tarm_rank\tarm_action_plane\tinterventions\tnonfinite_feature_failures\tillegal_selection_failures\tfallback_mismatch_failures\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D81a header");
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
            row.root.arm_rank,
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
        .expect("write D81a row");
    }
    writer.flush().expect("flush D81a output");
    eprintln!(
        "saved {} D81a rows in {:.3}s",
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn contested_crop_requires_expected_plane_and_proximity() {
        let mut context = [0.0; 16];
        context[13] = 1.0;
        for plane in 5..=7 {
            assert!(contested_crop((plane * MACRO_CELLS) as i32, &context));
        }
        assert!(!contested_crop((4 * MACRO_CELLS) as i32, &context));
        assert!(!contested_crop((8 * MACRO_CELLS) as i32, &context));
    }

    #[test]
    fn all_arms_share_root_and_obey_one_decision_budget() {
        let rows: Vec<_> = Arm::ALL
            .into_iter()
            .map(|arm| {
                play(Work {
                    arm,
                    task: Task {
                        map_seed: 9_912_000,
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
        assert!(rows
            .iter()
            .all(|row| row.root.illegal_selection_failures == 0));
        assert!(rows
            .iter()
            .all(|row| row.root.fallback_mismatch_failures == 0));
        let control = &rows[0].root;
        for row in &rows[1..] {
            assert_eq!(row.root.root_seen, control.root_seen);
            assert_eq!(row.root.root_turn, control.root_turn);
            assert_eq!(row.root.root_state_hash, control.root_state_hash);
            assert_eq!(row.root.root_candidate_count, control.root_candidate_count);
        }
    }
}
