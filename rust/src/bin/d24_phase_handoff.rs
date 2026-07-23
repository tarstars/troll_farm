//! Exact common-state screen of complete midgame policy handoffs.
//!
//! A promoted SecureOrchard resident creates the prefix against one fixed local
//! opponent.  At a fixed turn, terminal continuations fork from the same engine
//! state: the warmed resident control and cold-start, whole-side macro options.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone resident refers to its modules through `crate::`.  Re-exporting
// them here preserves those paths when it is compiled as a nested module.
pub use yamo::{bot, game};

use std::collections::BTreeSet;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_research::NorxondorThreeWorkerSilver;
use troll_farm::strategies::ownership_aware_farm::OwnershipAwareFarm;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

type Factory = fn() -> Box<dyn Strategy>;

fn fixed_gold2() -> Box<dyn Strategy> {
    Box::new(GoldElite::configured(GoldEconomyConfig {
        max_trolls: 2,
        choppers: 1,
        stagger: 0,
        spec1: (2, 2, 0, 2),
        spec2: (2, 2, 0, 2),
        planters: 0,
        hold_until: 0,
        farm_cap: 12,
        co_fell: false,
        adaptive: false,
    }))
}

fn compact() -> Box<dyn Strategy> {
    Box::new(CompactGold::new())
}

fn adaptive() -> Box<dyn Strategy> {
    Box::new(GoldElite::adaptive())
}

fn mybot() -> Box<dyn Strategy> {
    Box::new(MyBot::new())
}

fn printer() -> Box<dyn Strategy> {
    Box::new(PrinterBot::new())
}

fn scheduler() -> Box<dyn Strategy> {
    Box::new(SchedBot::new())
}

fn script() -> Box<dyn Strategy> {
    Box::new(ScriptBoss::new())
}

fn silver() -> Box<dyn Strategy> {
    Box::new(SilverBoss::new())
}

const OPPONENTS: [(&str, Factory); 8] = [
    ("compact_gold", compact),
    ("gold_adaptive", adaptive),
    ("gold_elite", fixed_gold2),
    ("mybot", mybot),
    ("printer_bot", printer),
    ("sched_bot", scheduler),
    ("script_boss", script),
    ("silver_boss", silver),
];

fn private2() -> Box<dyn Strategy> {
    fixed_gold2()
}

fn ownership2() -> Box<dyn Strategy> {
    Box::new(OwnershipAwareFarm::new())
}

fn hybrid3() -> Box<dyn Strategy> {
    Box::new(GoldElite::hybrid())
}

fn accumulate4() -> Box<dyn Strategy> {
    // Explicit configuration avoids the environment knobs in `GoldElite::accumulate`.
    Box::new(GoldElite::configured(GoldEconomyConfig {
        max_trolls: 4,
        choppers: 2,
        stagger: 30,
        spec1: (2, 2, 0, 2),
        spec2: (2, 2, 0, 2),
        planters: 1,
        hold_until: 0,
        farm_cap: 18,
        co_fell: false,
        adaptive: false,
    }))
}

fn norx3() -> Box<dyn Strategy> {
    Box::new(NorxondorThreeWorkerSilver::new())
}

const OPTIONS: [(&str, Factory); 5] = [
    ("private2", private2),
    ("ownership2", ownership2),
    ("hybrid3", hybrid3),
    ("accumulate4", accumulate4),
    ("norx3", norx3),
];

fn yamo_view(game: &GameState, player: usize) -> YamoState {
    let opponent = 1 - player;
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
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
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

fn worker_count(game: &GameState, player: usize) -> usize {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count()
}

#[derive(Clone)]
struct Prefix {
    states: Vec<GameState>,
    root: GameState,
    stall_counter: i32,
    reached_cut: bool,
}

fn resident_prefix(seed: u64, seat: usize, opponent_index: usize, decision_turn: i32) -> Prefix {
    let mut game = generate_bronze(seed);
    let mut resident = SecureOrchardBot::new();
    let opponent = OPPONENTS[opponent_index].1();
    let mut states = Vec::new();
    let mut stall_counter = 0;
    let mut ended = false;
    while game.turn < decision_turn && game.turn <= 300 {
        states.push(game.clone());
        let ours = resident.commands(&yamo_view(&game, seat));
        let theirs = opponent.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        if has_stalled(&game, &mut stall_counter) {
            ended = true;
            break;
        }
    }
    Prefix {
        states,
        reached_cut: !ended && game.turn == decision_turn,
        root: game,
        stall_counter,
    }
}

fn warmed_resident(prefix: &Prefix, seat: usize) -> SecureOrchardBot {
    let mut resident = SecureOrchardBot::new();
    for state in &prefix.states {
        let _ = resident.commands(&yamo_view(state, seat));
    }
    resident
}

fn warmed_opponent(prefix: &Prefix, seat: usize, opponent_index: usize) -> Box<dyn Strategy> {
    let opponent = OPPONENTS[opponent_index].1();
    for state in &prefix.states {
        let _ = opponent.decide(state, 1 - seat);
    }
    opponent
}

const FNV_OFFSET: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

fn trace_commands(hash: &mut u64, commands: &[String]) {
    for command in commands {
        for byte in command.as_bytes().iter().copied().chain([0xff]) {
            *hash ^= u64::from(byte);
            *hash = hash.wrapping_mul(FNV_PRIME);
        }
    }
    *hash ^= 0xfe;
    *hash = hash.wrapping_mul(FNV_PRIME);
}

#[derive(Clone, Copy)]
enum Branch {
    Resident,
    Option(usize),
}

impl Branch {
    fn label(self) -> &'static str {
        match self {
            Self::Resident => "resident",
            Self::Option(index) => OPTIONS[index].0,
        }
    }
}

#[derive(Clone)]
struct BranchResult {
    label: &'static str,
    final_turn: i32,
    margin: i32,
    my_score: i32,
    opponent_score: i32,
    my_wood: i32,
    opponent_wood: i32,
    my_workers: usize,
    opponent_workers: usize,
    max_my_workers: usize,
    third_worker_turn: i32,
    train_commands: usize,
    plant_commands: usize,
    command_hash: u64,
}

fn count_kind(commands: &[String], kind: &str) -> usize {
    commands
        .iter()
        .filter(|command| command.split_whitespace().next() == Some(kind))
        .count()
}

fn branch_result(
    prefix: &Prefix,
    seat: usize,
    opponent_index: usize,
    branch: Branch,
) -> BranchResult {
    let mut game = prefix.root.clone();
    let mut resident = matches!(branch, Branch::Resident).then(|| warmed_resident(prefix, seat));
    let option = match branch {
        Branch::Resident => None,
        Branch::Option(index) => Some(OPTIONS[index].1()),
    };
    let opponent = warmed_opponent(prefix, seat, opponent_index);
    let mut stall_counter = prefix.stall_counter;
    let mut max_my_workers = worker_count(&game, seat);
    let mut third_worker_turn = if max_my_workers >= 3 { game.turn } else { -1 };
    let mut train_commands = 0;
    let mut plant_commands = 0;
    let mut command_hash = FNV_OFFSET;

    if prefix.reached_cut {
        while game.turn <= 300 {
            let ours = if let Some(resident) = resident.as_mut() {
                resident.commands(&yamo_view(&game, seat))
            } else {
                option.as_ref().expect("option branch").decide(&game, seat)
            };
            let theirs = opponent.decide(&game, 1 - seat);
            train_commands += count_kind(&ours, "TRAIN");
            plant_commands += count_kind(&ours, "PLANT");
            trace_commands(&mut command_hash, &ours);
            apply_commands(&mut game, seat, &ours, &theirs);
            let workers = worker_count(&game, seat);
            max_my_workers = max_my_workers.max(workers);
            if third_worker_turn < 0 && workers >= 3 {
                third_worker_turn = game.turn;
            }
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
    }

    BranchResult {
        label: branch.label(),
        final_turn: game.turn,
        margin: game.scores[seat] - game.scores[1 - seat],
        my_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        my_wood: game.inventories[seat][5],
        opponent_wood: game.inventories[1 - seat][5],
        my_workers: worker_count(&game, seat),
        opponent_workers: worker_count(&game, 1 - seat),
        max_my_workers,
        third_worker_turn,
        train_commands,
        plant_commands,
        command_hash,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    decision_turn: i32,
    opponent_index: usize,
}

struct Scenario {
    task: Task,
    reached_cut: bool,
    root: GameState,
    branches: Vec<BranchResult>,
}

fn run_task(task: Task, selected_options: &[usize]) -> Scenario {
    let prefix = resident_prefix(
        task.seed,
        task.seat,
        task.opponent_index,
        task.decision_turn,
    );
    let mut branches = Vec::with_capacity(selected_options.len() + 1);
    branches.push(branch_result(
        &prefix,
        task.seat,
        task.opponent_index,
        Branch::Resident,
    ));
    for &option in selected_options {
        branches.push(branch_result(
            &prefix,
            task.seat,
            task.opponent_index,
            Branch::Option(option),
        ));
    }
    Scenario {
        task,
        reached_cut: prefix.reached_cut,
        root: prefix.root,
        branches,
    }
}

fn parse_turns(value: &str) -> Vec<i32> {
    let mut turns: Vec<_> = value
        .split(',')
        .map(|part| part.parse::<i32>().expect("numeric decision turn"))
        .collect();
    turns.sort_unstable();
    turns.dedup();
    assert!(
        !turns.is_empty() && turns.iter().all(|turn| (2..=300).contains(turn)),
        "decision turns must be unique values from 2 through 300"
    );
    turns
}

fn parse_options(value: &str) -> Vec<usize> {
    let requested: Vec<_> = value.split(',').filter(|name| !name.is_empty()).collect();
    assert!(!requested.is_empty(), "at least one option is required");
    let mut indexes = Vec::new();
    for name in requested {
        let index = OPTIONS
            .iter()
            .position(|(label, _)| *label == name)
            .unwrap_or_else(|| panic!("unknown option {name}"));
        if !indexes.contains(&index) {
            indexes.push(index);
        }
    }
    indexes
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args
        .get(1)
        .map_or(0, |value| value.parse::<u64>().expect("numeric seed start"));
    let seed_count = args.get(2).map_or(5, |value| {
        value.parse::<usize>().expect("numeric seed count")
    });
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d24-phase-handoff.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(16, |value| {
            value.parse::<usize>().expect("numeric thread count")
        })
        .clamp(1, 64);
    let turns = parse_turns(args.get(5).map_or("75,100,125,150", String::as_str));
    let selected_options = Arc::new(parse_options(args.get(6).map_or(
        "private2,ownership2,hybrid3,accumulate4,norx3",
        String::as_str,
    )));
    assert!(seed_count > 0, "seed count must be positive");

    let tasks: Vec<_> = (seed_start..seed_start + seed_count as u64)
        .flat_map(|seed| {
            turns.iter().copied().flat_map(move |decision_turn| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent_index| Task {
                        seed,
                        seat,
                        decision_turn,
                        opponent_index,
                    })
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let selected_options = Arc::clone(&selected_options);
            thread::spawn(move || {
                let mut rows = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    rows.push(run_task(tasks[index], &selected_options));
                }
                rows
            })
        })
        .collect();
    let mut scenarios: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D24 worker thread"))
        .collect();
    scenarios.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.decision_turn,
            row.task.seat,
            row.task.opponent_index,
        )
    });

    let file = File::create(&output).expect("create D24 output");
    let mut writer = BufWriter::new(file);
    writeln!(
        writer,
        "seed\tseat\tdecision_turn\topponent\treached_cut\toption\troot_turn\troot_my_score\troot_opponent_score\troot_my_wood\troot_opponent_wood\troot_my_workers\troot_opponent_workers\troot_plants\tfinal_turn\tmargin\tmy_score\topponent_score\tmy_wood\topponent_wood\tmy_workers\topponent_workers\tmax_my_workers\tthird_worker_turn\ttrain_commands\tplant_commands\tcommand_hash"
    )
    .expect("write D24 header");
    let mut row_count = 0usize;
    for scenario in scenarios {
        let task = scenario.task;
        for branch in scenario.branches {
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                task.seed,
                task.seat,
                task.decision_turn,
                OPPONENTS[task.opponent_index].0,
                usize::from(scenario.reached_cut),
                branch.label,
                scenario.root.turn,
                scenario.root.scores[task.seat],
                scenario.root.scores[1 - task.seat],
                scenario.root.inventories[task.seat][5],
                scenario.root.inventories[1 - task.seat][5],
                worker_count(&scenario.root, task.seat),
                worker_count(&scenario.root, 1 - task.seat),
                scenario.root.plants.len(),
                branch.final_turn,
                branch.margin,
                branch.my_score,
                branch.opponent_score,
                branch.my_wood,
                branch.opponent_wood,
                branch.my_workers,
                branch.opponent_workers,
                branch.max_my_workers,
                branch.third_worker_turn,
                branch.train_commands,
                branch.plant_commands,
                branch.command_hash,
            )
            .expect("write D24 row");
            row_count += 1;
        }
    }
    writer.flush().expect("flush D24 output");
    eprintln!(
        "saved {row_count} rows from {} scenarios in {:.3}s to {output}",
        tasks.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn option_names_are_unique_and_complete() {
        let names: BTreeSet<_> = OPTIONS.iter().map(|(name, _)| *name).collect();
        assert_eq!(names.len(), OPTIONS.len());
        assert_eq!(
            parse_options("private2,ownership2,hybrid3,accumulate4,norx3").len(),
            OPTIONS.len()
        );
    }

    #[test]
    fn command_hash_is_order_sensitive_and_repeatable() {
        let commands = vec!["MOVE 0 1 2".to_string(), "CHOP 1".to_string()];
        let mut first = FNV_OFFSET;
        let mut second = FNV_OFFSET;
        trace_commands(&mut first, &commands);
        trace_commands(&mut second, &commands);
        assert_eq!(first, second);
        let mut reversed = FNV_OFFSET;
        trace_commands(
            &mut reversed,
            &commands.into_iter().rev().collect::<Vec<_>>(),
        );
        assert_ne!(first, reversed);
    }
}
