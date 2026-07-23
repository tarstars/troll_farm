//! Evaluate exact D40 and the frozen D49 chopper-first reservation order.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroOpponentMode, MacroTerminal, MACRO_ACTION_PLANES, MACRO_CELLS,
};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Policy {
    D40,
    ChopperFirst,
}

impl Policy {
    fn parse(value: &str) -> Self {
        match value {
            "d40" => Self::D40,
            "chopper_first" => Self::ChopperFirst,
            _ => panic!("D49 policy must be d40 or chopper_first"),
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::D40 => "d40",
            Self::ChopperFirst => "chopper_first",
        }
    }
}

struct Row {
    task: Task,
    terminal: MacroTerminal,
    action_planes: [u32; MACRO_ACTION_PLANES],
    order_eligible: u32,
    order_promotions: u32,
    order_integrity_failures: u32,
    reward_identity_error: f32,
}

fn designated_chopper(env: &CompleteMacroEnv) -> Option<i32> {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .max_by_key(|unit| (unit.chop, unit.id))
        .map(|unit| unit.id)
}

fn play(task: Task, policy: Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut order_eligible = 0u32;
    let mut order_promotions = 0u32;
    let mut order_integrity_failures = 0u32;
    let mut terminal = MacroTerminal::default();
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D49 decision loop on {task:?}");
        if policy == Policy::ChopperFirst {
            let status = env.promote_max_chop_remaining_free_unit();
            order_eligible += u32::from(status.is_some());
            order_promotions += u32::from(status == Some(true));
            if status == Some(true)
                && (env.current_unit_id().is_none()
                    || env.current_unit_id() != designated_chopper(&env))
            {
                order_integrity_failures += 1;
            }
        }
        let observation = env.candidate_observation();
        let order = exact_prior_order(
            &observation.features,
            &observation.actions,
            observation.branch as u8,
        );
        let action = observation.actions[order[0]] as usize;
        assert_eq!(
            action, observation.actions[observation.teacher_index] as usize,
            "D49 exact-prior mismatch"
        );
        assert!(
            env.legal_actions().contains(&action),
            "D49 chose illegal action"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D49 zero-time loop on {task:?}");
    }
    let reward_identity_error = (100.0 * terminal.margin_return
        - (terminal.own_score - terminal.opponent_score) as f32)
        .abs();
    Row {
        task,
        terminal,
        action_planes,
        order_eligible,
        order_promotions,
        order_integrity_failures,
        reward_identity_error,
    }
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        6,
        "usage: d49_chopper_first START_SEED MAPS OUTPUT THREADS POLICY"
    );
    let start_seed = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    let policy = Policy::parse(&args[5]);
    assert!(maps > 0 && threads > 0);
    let tasks: Vec<_> = (start_seed..start_seed + maps as i64)
        .flat_map(|map_seed| {
            (0..2).flat_map(move |seat| {
                (0..MacroOpponentMode::ALL.len()).map(move |opponent| Task {
                    map_seed,
                    seat,
                    opponent,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(tasks.len())));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = tasks.get(index).copied() else {
                    break;
                };
                rows.lock().expect("D49 row lock").push(play(task, policy));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D49 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D49 row owner")
        .into_inner()
        .expect("D49 row lock");
    rows.sort_by_key(|row| row.task);

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D49 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank\tdeposit_prediction_failures\torder_eligible\torder_promotions\torder_integrity_failures\treward_identity_error").expect("write D49 header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.6}\t{:.6}\t{:.6}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.9}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            policy.label(),
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
            terminal.deposit_prediction_failures,
            row.order_eligible,
            row.order_promotions,
            row.order_integrity_failures,
            row.reward_identity_error,
        )
        .expect("write D49 row");
    }
    writer.flush().expect("flush D49 output");
    eprintln!(
        "saved {} {} rows in {:.3}s to {}",
        rows.len(),
        policy.label(),
        started.elapsed().as_secs_f64(),
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn d40_mode_matches_teacher_actions() {
        for opponent in [0, 1, 4, 7] {
            let mut env =
                CompleteMacroEnv::new(9_778_000, 0, MacroOpponentMode::from_index(opponent));
            for _ in 0..160 {
                let observation = env.candidate_observation();
                let expected = observation.actions[observation.teacher_index] as usize;
                let order = exact_prior_order(
                    &observation.features,
                    &observation.actions,
                    observation.branch as u8,
                );
                assert_eq!(observation.actions[order[0]] as usize, expected);
                if env.step(expected).done {
                    break;
                }
            }
        }
    }

    #[test]
    fn promotion_makes_designated_chopper_current() {
        let mut promotions = 0;
        for opponent in 0..MacroOpponentMode::ALL.len() {
            let mut env =
                CompleteMacroEnv::new(9_778_001, 1, MacroOpponentMode::from_index(opponent));
            for _ in 0..800 {
                let status = env.promote_max_chop_remaining_free_unit();
                if status == Some(true) {
                    promotions += 1;
                    assert_eq!(env.current_unit_id(), designated_chopper(&env));
                }
                let observation = env.candidate_observation();
                let action = observation.actions[observation.teacher_index] as usize;
                if env.step(action).done {
                    break;
                }
            }
        }
        assert!(promotions > 0);
    }
}
