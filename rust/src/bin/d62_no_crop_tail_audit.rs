//! Classify the zero-crop tail of D62's deterministic balanced path.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::time::Instant;

use rayon::prelude::*;

use troll_farm::rl_batch_option::{BatchOptionEnv, BatchOptionMode};
use troll_farm::rl_macro::{MacroOpponentMode, MacroTerminal};

#[derive(Debug)]
struct Row {
    task_index: usize,
    map_seed: i64,
    seat: usize,
    opponent: MacroOpponentMode,
    initial_inventory: [i32; 6],
    initial_plants: usize,
    batches: u32,
    terminal_live_plants: usize,
    terminal: MacroTerminal,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn task(seed_base: i64, task_index: usize) -> (i64, usize, usize) {
    let per_map = 2 * MacroOpponentMode::ALL.len();
    let within_map = task_index % per_map;
    let map_seed = seed_base + (task_index / per_map) as i64;
    let seat = within_map / MacroOpponentMode::ALL.len();
    let opponent = within_map % MacroOpponentMode::ALL.len();
    (map_seed, seat, opponent)
}

fn play(seed_base: i64, task_index: usize) -> Row {
    let (map_seed, seat, opponent_index) = task(seed_base, task_index);
    let opponent = MacroOpponentMode::from_index(opponent_index);
    let mut env = BatchOptionEnv::new(map_seed, seat, opponent);
    let initial_inventory = env.macro_env.state.inventories[seat];
    let initial_plants = env.macro_env.state.plants.len();
    let mut batches = 0u32;
    let terminal = loop {
        batches = batches.saturating_add(1);
        let result = env.step(BatchOptionMode::Balanced as usize);
        if result.done {
            break result;
        }
        assert!(batches < 1_000, "D62 tail-audit batch loop");
    };
    Row {
        task_index,
        map_seed,
        seat,
        opponent,
        initial_inventory,
        initial_plants,
        batches,
        terminal_live_plants: env.macro_env.state.plants.len(),
        terminal,
    }
}

fn main() {
    let arguments: Vec<_> = std::env::args().collect();
    assert_eq!(
        arguments.len(),
        5,
        "usage: d62_no_crop_tail_audit SEED_BASE TASKS OUTPUT THREADS"
    );
    let seed_base: i64 = parse(&arguments[1], "seed base");
    let tasks: usize = parse(&arguments[2], "tasks");
    let output = &arguments[3];
    let threads: usize = parse(&arguments[4], "threads");
    assert!(seed_base != 0 && tasks > 0 && threads > 0);

    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("build D62 tail-audit pool");
    let started = Instant::now();
    let mut rows: Vec<_> = pool.install(|| {
        (0..tasks)
            .into_par_iter()
            .map(|task_index| play(seed_base, task_index))
            .collect()
    });
    rows.sort_by_key(|row| row.task_index);

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D62 tail-audit output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "task_index\tmap_seed\tseat\topponent\tturn\tend_reason\town_score\topponent_score\town_workers\topponent_workers\tsuccessful_trains\town_created_crops\topponent_created_crops\tselected_renew_jobs\tinitial_plants\tterminal_live_plants\tinitial_plum\tinitial_lemon\tinitial_apple\tinitial_banana\tinitial_iron\tinitial_wood\tinitial_seed_available\tbatches\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\taction_hash\tstate_hash").expect("write D62 tail-audit header");
    for row in &rows {
        let terminal = row.terminal;
        let end_reason = if terminal.turn > 300 {
            "turn_limit"
        } else {
            "plant_stock_stall"
        };
        let initial_seed_available = row.initial_inventory[..4].iter().any(|value| *value > 0);
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task_index,
            row.map_seed,
            row.seat,
            row.opponent.label(),
            terminal.turn,
            end_reason,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.selected_renew_jobs,
            row.initial_plants,
            row.terminal_live_plants,
            row.initial_inventory[0],
            row.initial_inventory[1],
            row.initial_inventory[2],
            row.initial_inventory[3],
            row.initial_inventory[4],
            row.initial_inventory[5],
            u8::from(initial_seed_available),
            row.batches,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.action_hash,
            terminal.state_hash,
        )
        .expect("write D62 tail-audit row");
    }
    writer.flush().expect("flush D62 tail-audit output");
    let crop_zero = rows
        .iter()
        .filter(|row| row.terminal.own_created_crops == 0)
        .count();
    eprintln!(
        "saved {} D62 balanced tasks with {} zero-crop rows in {:.3}s",
        rows.len(),
        crop_zero,
        started.elapsed().as_secs_f64(),
    );
}
