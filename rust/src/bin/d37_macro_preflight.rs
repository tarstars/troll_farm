//! Deterministic D37/D38 complete-macro preflight runner.

use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

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
    Heuristic,
    Deficit,
    Evacuation,
    WorkConserving,
    Random,
}

impl Policy {
    fn parse(value: &str) -> Self {
        match value {
            "heuristic" => Self::Heuristic,
            "deficit" => Self::Deficit,
            "evacuation" => Self::Evacuation,
            "work_conserving" => Self::WorkConserving,
            "random" => Self::Random,
            _ => {
                panic!("policy must be heuristic, deficit, evacuation, work_conserving, or random")
            }
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Heuristic => "heuristic",
            Self::Deficit => "deficit",
            Self::Evacuation => "evacuation",
            Self::WorkConserving => "work_conserving",
            Self::Random => "random",
        }
    }
}

struct Row {
    task: Task,
    terminal: MacroTerminal,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9e3779b97f4a7c15);
    let mut value = *state;
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
    value ^ (value >> 31)
}

fn play(task: Task, policy: Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut random_state = task.map_seed as u64
        ^ (task.seat as u64).wrapping_mul(0xd6e8feb86659fd93)
        ^ (task.opponent as u64).wrapping_mul(0xa0761d6478bd642f)
        ^ 0x4433375f72616e64;
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut terminal = MacroTerminal::default();
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant_decisions = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(
            decisions <= 5_000,
            "D37 decision loop on {:?} under {}",
            task,
            policy.label()
        );
        let action = match policy {
            Policy::Heuristic => env.heuristic_action(),
            Policy::Deficit => env.deficit_heuristic_action(),
            Policy::Evacuation => env.evacuation_deficit_heuristic_action(),
            Policy::WorkConserving => env.work_conserving_deficit_heuristic_action(),
            Policy::Random => {
                let legal = env.legal_actions();
                legal[splitmix64(&mut random_state) as usize % legal.len()]
            }
        };
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        if env.state.turn == last_turn {
            stagnant_decisions += 1;
        } else {
            last_turn = env.state.turn;
            stagnant_decisions = 0;
        }
        assert!(
            stagnant_decisions <= 16,
            "D37 zero-time decision loop on {:?} under {} at turn {}: stage {:?}, goal {:?}, current {:?}, active {:?}, legal {}",
            task,
            policy.label(),
            last_turn,
            env.stage(),
            env.train_goal(),
            env.current_unit_id(),
            env.active_jobs(),
            env.legal_actions().len(),
        );
    }
    Row {
        task,
        terminal,
        action_planes,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let start_seed = args
        .get(1)
        .map_or(9_600_000, |value| value.parse::<i64>().expect("start seed"));
    let map_count = args
        .get(2)
        .map_or(16, |value| value.parse::<usize>().expect("map count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d37-macro-preflight.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(24, |value| value.parse::<usize>().expect("threads"));
    let policy = Policy::parse(args.get(5).map_or("heuristic", String::as_str));
    assert!(map_count > 0 && threads > 0);

    let tasks: Vec<_> = (start_seed..start_seed + map_count as i64)
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
                rows.lock().expect("row lock").push(play(task, policy));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D37 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D37 rows")
        .into_inner()
        .expect("D37 rows lock");
    rows.sort_by_key(|row| row.task);

    let mut writer = BufWriter::new(File::create(&output).expect("create D37 output"));
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank\tdeposit_prediction_failures").expect("write D37 header");
    for row in &rows {
        let terminal = row.terminal;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.6}\t{:.6}\t{:.6}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
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
        )
        .expect("write D37 row");
    }
    writer.flush().expect("flush D37 output");
    eprintln!(
        "saved {} {} rows in {:.3}s to {}",
        rows.len(),
        policy.label(),
        started.elapsed().as_secs_f64(),
        output
    );
}
