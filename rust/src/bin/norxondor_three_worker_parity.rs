//! Exhaustive complete-match command parity for the standalone three-worker policy port.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

#[path = "../norxondor_three_worker_live_bot.rs"]
mod norxondor_three_worker_live_bot;

use norxondor_three_worker_live_bot::NorxondorThreeWorkerBot;
use std::collections::BTreeSet;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;
use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_research::NorxondorThreeWorkerSilver;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::game::{GameState as LiveState, Plant, PlantKind, Stats, Unit};

const OPPONENT_NAMES: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    opponent: usize,
    seat: usize,
}

struct Row {
    task: Task,
    turns: i32,
    decisions: usize,
    elapsed_ns: u128,
    p95_ns: u128,
    max_ns: u128,
    score: i32,
    opponent_score: i32,
    workers: usize,
}

fn opponent(index: usize) -> Box<dyn Strategy> {
    match index {
        0 => Box::new(CompactGold::new()),
        1 => Box::new(GoldElite::adaptive()),
        2 => Box::new(GoldElite::new()),
        3 => Box::new(MyBot::new()),
        4 => Box::new(PrinterBot::new()),
        5 => Box::new(SchedBot::new()),
        6 => Box::new(ScriptBoss::new()),
        7 => Box::new(SilverBoss::new()),
        _ => unreachable!(),
    }
}

fn live_view(game: &troll_farm::game::state::GameState, player: usize) -> LiveState {
    let other = 1 - player;
    LiveState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: [game.shacks[player], game.shacks[other]],
        inventories: [game.inventories[player], game.inventories[other]],
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: Stats {
                    movement_speed: unit.ms,
                    carry_capacity: unit.cc,
                    harvest_power: unit.hp,
                    chop_power: unit.chop,
                },
                carry: unit.carry,
            })
            .collect(),
        plants: game
            .plants
            .iter()
            .map(|plant| Plant {
                kind: PlantKind::parse(&plant.plant_type).expect("known plant kind"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: [game.scores[player], game.scores[other]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn play(task: Task) -> Result<Row, String> {
    let mut game = generate_bronze(task.seed);
    let reference = NorxondorThreeWorkerSilver::new();
    let opposing = opponent(task.opponent);
    let mut live = NorxondorThreeWorkerBot::new();
    let mut turns_until_end = 0;
    let mut elapsed_ns = 0;
    let mut max_ns = 0;
    let mut latencies = Vec::new();
    let mut decisions = 0;

    for _ in 0..300 {
        let view = live_view(&game, task.seat);
        let started = Instant::now();
        let actual = live.commands(&view);
        let duration = started.elapsed().as_nanos();
        elapsed_ns += duration;
        max_ns = max_ns.max(duration);
        latencies.push(duration);
        decisions += 1;
        let expected = reference.decide(&game, task.seat);
        if actual != expected {
            return Err(format!(
                "seed={} opponent={} seat={} turn={} expected={:?} actual={:?}",
                task.seed, OPPONENT_NAMES[task.opponent], task.seat, game.turn, expected, actual
            ));
        }
        let other = opposing.decide(&game, 1 - task.seat);
        if task.seat == 0 {
            step(&mut game, &actual, &other);
        } else {
            step(&mut game, &other, &actual);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }

    latencies.sort_unstable();
    let p95_index = (latencies.len() * 95).div_ceil(100).saturating_sub(1);
    Ok(Row {
        task,
        turns: game.turn - 1,
        decisions,
        elapsed_ns,
        p95_ns: latencies[p95_index],
        max_ns,
        score: game.scores[task.seat],
        opponent_score: game.scores[1 - task.seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == task.seat)
            .count(),
    })
}

fn arg_value<T: std::str::FromStr>(name: &str, default: T) -> T {
    let args: Vec<String> = std::env::args().collect();
    args.windows(2)
        .find(|pair| pair[0] == name)
        .and_then(|pair| pair[1].parse().ok())
        .unwrap_or(default)
}

fn main() {
    let start_seed: u64 = arg_value("--start-seed", 0);
    let end_seed: u64 = arg_value("--end-seed", 29);
    let workers: usize = arg_value("--workers", 18).max(1);
    let args: Vec<String> = std::env::args().collect();
    let output = args
        .windows(2)
        .find(|pair| pair[0] == "--output")
        .map(|pair| pair[1].clone())
        .unwrap_or_else(|| "../data/analysis/norxondor-three-worker-parity.tsv".to_string());
    assert!(start_seed <= end_seed);

    let mut tasks = Vec::new();
    for seed in start_seed..=end_seed {
        for opponent in 0..OPPONENT_NAMES.len() {
            for seat in 0..2 {
                tasks.push(Task {
                    seed,
                    opponent,
                    seat,
                });
            }
        }
    }
    let tasks = Arc::new(tasks);
    let cursor = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::new()));
    let failures = Arc::new(Mutex::new(Vec::new()));
    let mut handles = Vec::new();
    for _ in 0..workers.min(tasks.len()) {
        let tasks = Arc::clone(&tasks);
        let cursor = Arc::clone(&cursor);
        let rows = Arc::clone(&rows);
        let failures = Arc::clone(&failures);
        handles.push(thread::spawn(move || loop {
            let index = cursor.fetch_add(1, Ordering::Relaxed);
            if index >= tasks.len() {
                break;
            }
            match play(tasks[index]) {
                Ok(row) => rows.lock().unwrap().push(row),
                Err(error) => failures.lock().unwrap().push(error),
            }
        }));
    }
    for handle in handles {
        handle.join().expect("parity worker panicked");
    }
    let failures = failures.lock().unwrap();
    if !failures.is_empty() {
        for failure in failures.iter().take(20) {
            eprintln!("MISMATCH {failure}");
        }
        panic!("{} parity matches failed", failures.len());
    }
    drop(failures);

    let mut rows = rows.lock().unwrap();
    rows.sort_by_key(|row| (row.task.seed, row.task.opponent, row.task.seat));
    assert_eq!(rows.len(), tasks.len());
    let file = File::create(&output).expect("create parity TSV");
    let mut out = BufWriter::new(file);
    writeln!(
        out,
        "seed\topponent\tseat\tturns\tdecisions\telapsed_ns\tp95_ns\tmax_ns\tscore\topponent_score\tworkers"
    )
    .unwrap();
    for row in rows.iter() {
        writeln!(
            out,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.seed,
            OPPONENT_NAMES[row.task.opponent],
            row.task.seat,
            row.turns,
            row.decisions,
            row.elapsed_ns,
            row.p95_ns,
            row.max_ns,
            row.score,
            row.opponent_score,
            row.workers
        )
        .unwrap();
    }
    out.flush().unwrap();
    eprintln!(
        "parity: {} complete matches, zero mismatch -> {}",
        rows.len(),
        output
    );
}
