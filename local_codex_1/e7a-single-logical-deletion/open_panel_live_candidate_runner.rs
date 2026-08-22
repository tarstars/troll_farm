//! Continued-referee open panel for the exact E7a baseline and half-size candidate.
//!
//! The launcher supplies visibility-only module renderings of both standalone sources.
//! Maps are confined to the already-consumed A2-0b calibration range.

mod baseline {
    include!(env!("E7A_HALF_BASELINE_MODULE"));
}
mod candidate {
    include!(env!("E7A_HALF_CANDIDATE_MODULE"));
}

#[path = "../../rust/src/d171a_control_resident_snapshot.rs"]
mod control_resident;

use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::a2_referee_parity::{self, LegalityReport};
use troll_farm::game::engine::has_stalled;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::Strategy;

const OPEN_START: i64 = 9_854_000;
const OPEN_END: i64 = 9_854_128;
const OPPONENTS: usize = 6;

enum Opponent {
    Resident(control_resident::bot::moisan::SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(index: usize) -> Self {
        match MacroOpponentMode::from_index(index) {
            MacroOpponentMode::Resident => {
                Self::Resident(control_resident::bot::moisan::SecureOrchardBot::new())
            }
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => {
                Self::Local(Box::new(NorxondorNative::new(true)))
            }
            MacroOpponentMode::LegendBalanced => Self::Local(Box::new(
                LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }),
            )),
            MacroOpponentMode::MyBot => Self::Local(Box::new(MyBot::new())),
            _ => unreachable!("runner intentionally freezes the first six families"),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => control_resident::bot::Bot::commands(
                bot,
                &control_view(game, player),
            ),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn control_view(game: &GameState, player: usize) -> control_resident::game::GameState {
    let opponent = 1 - player;
    control_resident::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game.units.iter().map(|unit| control_resident::game::Unit {
            id: unit.id,
            player: usize::from(unit.player as usize != player),
            cell: unit.pos(),
            stats: control_resident::game::Stats {
                movement_speed: unit.ms,
                carry_capacity: unit.cc,
                harvest_power: unit.hp,
                chop_power: unit.chop,
            },
            carry: unit.carry,
        }).collect(),
        plants: game.plants.iter().map(|plant| control_resident::game::Plant {
            kind: control_resident::game::PlantKind::parse(&plant.plant_type)
                .expect("known plant type"),
            cell: plant.pos(),
            size: plant.size,
            health: plant.health,
            fruits: plant.fruits,
            cooldown: plant.cooldown,
        }).collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

fn baseline_view(game: &GameState, player: usize) -> baseline::game::GameState {
    let opponent = 1 - player;
    baseline::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game.units.iter().map(|unit| baseline::game::types::Unit {
            id: unit.id,
            player: usize::from(unit.player as usize != player),
            cell: unit.pos(),
            stats: baseline::game::types::Stats {
                movement_speed: unit.ms,
                carry_capacity: unit.cc,
                harvest_power: unit.hp,
                chop_power: unit.chop,
            },
            carry: unit.carry,
        }).collect(),
        plants: game.plants.iter().map(|plant| baseline::game::types::Plant {
            kind: baseline::game::types::PlantKind::parse(&plant.plant_type)
                .expect("known plant type"),
            cell: plant.pos(),
            size: plant.size,
            health: plant.health,
            fruits: plant.fruits,
            cooldown: plant.cooldown,
        }).collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

fn candidate_view(game: &GameState, player: usize) -> candidate::game::GameState {
    let opponent = 1 - player;
    candidate::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game.units.iter().map(|unit| candidate::game::types::Unit {
            id: unit.id,
            player: usize::from(unit.player as usize != player),
            cell: unit.pos(),
            stats: candidate::game::types::Stats {
                movement_speed: unit.ms,
                carry_capacity: unit.cc,
                harvest_power: unit.hp,
                chop_power: unit.chop,
            },
            carry: unit.carry,
        }).collect(),
        plants: game.plants.iter().map(|plant| candidate::game::types::Plant {
            kind: candidate::game::types::PlantKind::parse(&plant.plant_type)
                .expect("known plant type"),
            cell: plant.pos(),
            size: plant.size,
            health: plant.health,
            fruits: plant.fruits,
            cooldown: plant.cooldown,
        }).collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Arm {
    Baseline,
    Candidate,
}

enum Policy {
    Baseline(baseline::bot::moisan::SecureOrchardBot),
    Candidate(candidate::bot::moisan::SecureOrchardBot),
}

impl Policy {
    fn new(arm: Arm) -> Self {
        match arm {
            Arm::Baseline => Self::Baseline(
                baseline::bot::moisan::SecureOrchardBot::new()
            ),
            Arm::Candidate => Self::Candidate(candidate::bot::moisan::SecureOrchardBot::new()),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Baseline(bot) => baseline::bot::Bot::commands(
                bot,
                &baseline_view(game, player),
            ),
            Self::Candidate(bot) => candidate::bot::Bot::commands(
                bot,
                &candidate_view(game, player),
            ),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct SideResult {
    score: i32,
    opponent_score: i32,
    final_wood: i32,
    opponent_final_wood: i32,
    turn: i32,
    first_train_turn: Option<i32>,
    final_workers: usize,
    longest_period2: usize,
    latency: Vec<u64>,
    legality: LegalityReport,
}

fn longest_period2(positions: &BTreeMap<i32, Vec<Cell>>) -> usize {
    positions.values().map(|cells| {
        let mut current = 0;
        let mut longest = 0;
        for index in 2..cells.len() {
            if cells[index] == cells[index - 2] && cells[index] != cells[index - 1] {
                current = if current == 0 { 3 } else { current + 1 };
                longest = longest.max(current);
            } else {
                current = 0;
            }
        }
        longest
    }).max().unwrap_or(0)
}

fn play(arm: Arm, task: Task) -> SideResult {
    let mut referee = a2_referee_parity::generate_official(task.map_seed);
    let mut policy = Policy::new(arm);
    let mut opponent = Opponent::new(task.opponent);
    let mut turns_until_end = 0;
    let mut first_train_turn = None;
    let mut positions: BTreeMap<i32, Vec<Cell>> = BTreeMap::new();
    let mut latency = Vec::new();
    for unit in referee.game.units.iter().filter(|unit| unit.player as usize == task.seat) {
        positions.entry(unit.id).or_default().push(unit.pos());
    }

    loop {
        let turn = referee.game.turn;
        let opponent_seat = 1 - task.seat;
        let started = Instant::now();
        let ours = policy.commands(&referee.game, task.seat);
        latency.push(started.elapsed().as_nanos().min(u128::from(u64::MAX)) as u64);
        let theirs = opponent.commands(&referee.game, opponent_seat);
        let commands = if task.seat == 0 { [ours, theirs] } else { [theirs, ours] };
        a2_referee_parity::step(&mut referee, &commands[0], &commands[1]);

        let workers = referee.game.units.iter()
            .filter(|unit| unit.player as usize == task.seat)
            .count();
        if workers >= 2 && first_train_turn.is_none() {
            first_train_turn = Some(turn);
        }
        for unit in referee.game.units.iter().filter(|unit| unit.player as usize == task.seat) {
            positions.entry(unit.id).or_default().push(unit.pos());
        }
        if referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&referee.game, &mut turns_until_end)
        {
            break;
        }
    }

    SideResult {
        score: referee.game.scores[task.seat],
        opponent_score: referee.game.scores[1 - task.seat],
        final_wood: referee.game.inventories[task.seat][5],
        opponent_final_wood: referee.game.inventories[1 - task.seat][5],
        turn: referee.game.turn,
        first_train_turn,
        final_workers: referee.game.units.iter()
            .filter(|unit| unit.player as usize == task.seat)
            .count(),
        longest_period2: longest_period2(&positions),
        latency,
        legality: referee.legality,
    }
}

struct Row {
    task: Task,
    baseline: SideResult,
    candidate: SideResult,
}

fn percentile95(samples: &mut [u64]) -> u64 {
    samples.sort_unstable();
    samples[((samples.len() * 95).saturating_sub(1)) / 100]
}

fn optional(value: Option<i32>) -> String {
    value.map(|number| number.to_string()).unwrap_or_default()
}

fn write_rows(path: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(path).expect("create panel TSV"));
    writeln!(writer, "map_seed\tseat\topponent\tbaseline_score\tbaseline_opponent_score\tbaseline_margin\tcandidate_score\tcandidate_opponent_score\tcandidate_margin\tdelta\tbaseline_wood\tcandidate_wood\tbaseline_opponent_wood\tcandidate_opponent_wood\tbaseline_turn\tcandidate_turn\tbaseline_train_turn\tcandidate_train_turn\tbaseline_workers\tcandidate_workers\tbaseline_period2\tcandidate_period2\tbaseline_issues\tcandidate_issues\tbaseline_critical\tcandidate_critical\tbaseline_unclassified\tcandidate_unclassified").expect("header");
    let mut baseline_latency = Vec::new();
    let mut candidate_latency = Vec::new();
    for row in rows {
        let baseline_margin = row.baseline.score - row.baseline.opponent_score;
        let candidate_margin = row.candidate.score - row.candidate.opponent_score;
        baseline_latency.extend_from_slice(&row.baseline.latency);
        candidate_latency.extend_from_slice(&row.candidate.latency);
        writeln!(writer, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.baseline.score,
            row.baseline.opponent_score,
            baseline_margin,
            row.candidate.score,
            row.candidate.opponent_score,
            candidate_margin,
            candidate_margin - baseline_margin,
            row.baseline.final_wood,
            row.candidate.final_wood,
            row.baseline.opponent_final_wood,
            row.candidate.opponent_final_wood,
            row.baseline.turn,
            row.candidate.turn,
            optional(row.baseline.first_train_turn),
            optional(row.candidate.first_train_turn),
            row.baseline.final_workers,
            row.candidate.final_workers,
            row.baseline.longest_period2,
            row.candidate.longest_period2,
            row.baseline.legality.issue_count(),
            row.candidate.legality.issue_count(),
            row.baseline.legality.critical_issue_count(),
            row.candidate.legality.critical_issue_count(),
            row.baseline.legality.unclassified_issue_count(),
            row.candidate.legality.unclassified_issue_count(),
        ).expect("row");
    }
    let baseline_max = baseline_latency.iter().copied().max().unwrap_or(0);
    let candidate_max = candidate_latency.iter().copied().max().unwrap_or(0);
    let baseline_count = baseline_latency.len();
    let candidate_count = candidate_latency.len();
    let baseline_p95 = percentile95(&mut baseline_latency);
    let candidate_p95 = percentile95(&mut candidate_latency);
    writeln!(writer, "#latency\tbaseline\t{}\t{}\t{}", baseline_count, baseline_p95, baseline_max).expect("baseline latency");
    writeln!(writer, "#latency\tcandidate\t{}\t{}\t{}", candidate_count, candidate_p95, candidate_max).expect("candidate latency");
}

fn parse<T: std::str::FromStr>(text: &str, label: &str) -> T {
    text.parse().unwrap_or_else(|_| panic!("invalid {label}: {text}"))
}

fn main() {
    let arguments: Vec<String> = std::env::args().collect();
    assert!(arguments.len() == 5, "usage: runner START MAPS OUTPUT THREADS");
    let start: i64 = parse(&arguments[1], "start");
    let maps: i64 = parse(&arguments[2], "maps");
    let output = &arguments[3];
    let threads: usize = parse(&arguments[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(start >= OPEN_START && start + maps <= OPEN_END);

    let tasks: Vec<Task> = (start..start + maps).flat_map(|map_seed| {
        (0..2).flat_map(move |seat| {
            (0..OPPONENTS).map(move |opponent| Task { map_seed, seat, opponent })
        })
    }).collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(tasks.len())));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(tasks.len())).map(|_| {
        let tasks = Arc::clone(&tasks);
        let next = Arc::clone(&next);
        let rows = Arc::clone(&rows);
        thread::spawn(move || loop {
            let index = next.fetch_add(1, Ordering::Relaxed);
            let Some(task) = tasks.get(index).copied() else { break };
            rows.lock().expect("rows lock").push(Row {
                task,
                baseline: play(Arm::Baseline, task),
                candidate: play(Arm::Candidate, task),
            });
        })
    }).collect();
    for handle in handles {
        handle.join().expect("panel worker");
    }
    let mut rows = Arc::try_unwrap(rows).ok().expect("sole rows")
        .into_inner().expect("rows mutex");
    rows.sort_by_key(|row| row.task);
    write_rows(output, &rows);
    eprintln!("saved {} paired tasks in {:.3}s", rows.len(), started.elapsed().as_secs_f64());
}
