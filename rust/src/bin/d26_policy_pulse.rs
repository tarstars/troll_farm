/// Common-state screen of a bounded ownership-farm production pulse.

#[path = "yamo_orchard_live.rs"]
mod yamo;

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

fn compact() -> Box<dyn Strategy> {
    Box::new(CompactGold::new())
}

fn adaptive() -> Box<dyn Strategy> {
    Box::new(GoldElite::adaptive())
}

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

fn resident_prefix(seed: u64, seat: usize, opponent_index: usize) -> Prefix {
    let mut game = generate_bronze(seed);
    let mut resident = SecureOrchardBot::new();
    let opponent = OPPONENTS[opponent_index].1();
    let mut states = Vec::new();
    let mut stall_counter = 0;
    let mut ended = false;
    while game.turn < 75 && game.turn <= 300 {
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
        reached_cut: !ended && game.turn == 75,
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

fn count_kind(commands: &[String], kind: &str) -> usize {
    commands
        .iter()
        .filter(|command| command.split_whitespace().next() == Some(kind))
        .count()
}

#[derive(Clone)]
struct BranchResult {
    label: String,
    exit_turn: i32,
    final_turn: i32,
    margin: i32,
    my_score: i32,
    opponent_score: i32,
    my_wood: i32,
    opponent_wood: i32,
    my_workers: usize,
    opponent_workers: usize,
    max_my_workers: usize,
    farm_turns: usize,
    restart_turns: usize,
    farm_train_commands: usize,
    farm_plant_commands: usize,
    restart_train_commands: usize,
    restart_plant_commands: usize,
    command_hash: u64,
}

fn finish(
    label: String,
    exit_turn: i32,
    game: &GameState,
    seat: usize,
    max_my_workers: usize,
    farm_turns: usize,
    restart_turns: usize,
    farm_train_commands: usize,
    farm_plant_commands: usize,
    restart_train_commands: usize,
    restart_plant_commands: usize,
    command_hash: u64,
) -> BranchResult {
    BranchResult {
        label,
        exit_turn,
        final_turn: game.turn,
        margin: game.scores[seat] - game.scores[1 - seat],
        my_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        my_wood: game.inventories[seat][5],
        opponent_wood: game.inventories[1 - seat][5],
        my_workers: worker_count(game, seat),
        opponent_workers: worker_count(game, 1 - seat),
        max_my_workers,
        farm_turns,
        restart_turns,
        farm_train_commands,
        farm_plant_commands,
        restart_train_commands,
        restart_plant_commands,
        command_hash,
    }
}

fn control(prefix: &Prefix, seat: usize, opponent_index: usize) -> BranchResult {
    let mut game = prefix.root.clone();
    let mut resident = warmed_resident(prefix, seat);
    let opponent = warmed_opponent(prefix, seat, opponent_index);
    let mut stall_counter = prefix.stall_counter;
    let mut max_workers = worker_count(&game, seat);
    let mut turns = 0;
    let mut train = 0;
    let mut plant = 0;
    let mut hash = FNV_OFFSET;
    if prefix.reached_cut {
        while game.turn <= 300 {
            let ours = resident.commands(&yamo_view(&game, seat));
            let theirs = opponent.decide(&game, 1 - seat);
            turns += 1;
            train += count_kind(&ours, "TRAIN");
            plant += count_kind(&ours, "PLANT");
            trace_commands(&mut hash, &ours);
            apply_commands(&mut game, seat, &ours, &theirs);
            max_workers = max_workers.max(worker_count(&game, seat));
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
    }
    finish(
        "resident".to_string(),
        -1,
        &game,
        seat,
        max_workers,
        0,
        turns,
        0,
        0,
        train,
        plant,
        hash,
    )
}

fn pulse(prefix: &Prefix, seat: usize, opponent_index: usize, exit_turn: i32) -> BranchResult {
    let mut game = prefix.root.clone();
    let farm = OwnershipAwareFarm::new();
    let opponent = warmed_opponent(prefix, seat, opponent_index);
    let mut stall_counter = prefix.stall_counter;
    let mut max_workers = worker_count(&game, seat);
    let mut farm_turns = 0;
    let mut restart_turns = 0;
    let mut farm_train = 0;
    let mut farm_plant = 0;
    let mut restart_train = 0;
    let mut restart_plant = 0;
    let mut hash = FNV_OFFSET;
    let mut ended = !prefix.reached_cut;
    if prefix.reached_cut {
        while game.turn < exit_turn && game.turn <= 300 {
            let ours = farm.decide(&game, seat);
            let theirs = opponent.decide(&game, 1 - seat);
            farm_turns += 1;
            farm_train += count_kind(&ours, "TRAIN");
            farm_plant += count_kind(&ours, "PLANT");
            trace_commands(&mut hash, &ours);
            apply_commands(&mut game, seat, &ours, &theirs);
            max_workers = max_workers.max(worker_count(&game, seat));
            if has_stalled(&game, &mut stall_counter) {
                ended = true;
                break;
            }
        }
    }
    if !ended && game.turn <= 300 {
        let mut resident = SecureOrchardBot::new();
        while game.turn <= 300 {
            let ours = resident.commands(&yamo_view(&game, seat));
            let theirs = opponent.decide(&game, 1 - seat);
            restart_turns += 1;
            restart_train += count_kind(&ours, "TRAIN");
            restart_plant += count_kind(&ours, "PLANT");
            trace_commands(&mut hash, &ours);
            apply_commands(&mut game, seat, &ours, &theirs);
            max_workers = max_workers.max(worker_count(&game, seat));
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
    }
    finish(
        format!("pulse{exit_turn}"),
        exit_turn,
        &game,
        seat,
        max_workers,
        farm_turns,
        restart_turns,
        farm_train,
        farm_plant,
        restart_train,
        restart_plant,
        hash,
    )
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    opponent_index: usize,
}

struct Scenario {
    task: Task,
    reached_cut: bool,
    root: GameState,
    branches: Vec<BranchResult>,
}

fn run_task(task: Task, exits: &[i32]) -> Scenario {
    let prefix = resident_prefix(task.seed, task.seat, task.opponent_index);
    let mut branches = Vec::with_capacity(exits.len() + 1);
    branches.push(control(&prefix, task.seat, task.opponent_index));
    for &exit in exits {
        branches.push(pulse(&prefix, task.seat, task.opponent_index, exit));
    }
    Scenario {
        task,
        reached_cut: prefix.reached_cut,
        root: prefix.root,
        branches,
    }
}

fn parse_exits(value: &str) -> Vec<i32> {
    let mut exits: Vec<_> = value
        .split(',')
        .map(|part| part.parse::<i32>().expect("numeric pulse exit"))
        .collect();
    exits.sort_unstable();
    exits.dedup();
    assert!(
        !exits.is_empty() && exits.iter().all(|turn| (76..=300).contains(turn)),
        "pulse exits must be unique values from 76 through 300"
    );
    exits
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
        .unwrap_or_else(|| "d26-policy-pulse.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(16, |value| {
            value.parse::<usize>().expect("numeric thread count")
        })
        .clamp(1, 64);
    let exits = Arc::new(parse_exits(
        args.get(5).map_or("100,125,150", String::as_str),
    ));
    assert!(seed_count > 0, "seed count must be positive");

    let tasks: Vec<_> = (seed_start..seed_start + seed_count as u64)
        .flat_map(|seed| {
            (0..2).flat_map(move |seat| {
                (0..OPPONENTS.len()).map(move |opponent_index| Task {
                    seed,
                    seat,
                    opponent_index,
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
            let exits = Arc::clone(&exits);
            let next = Arc::clone(&next);
            thread::spawn(move || {
                let mut rows = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    rows.push(run_task(tasks[index], &exits));
                }
                rows
            })
        })
        .collect();
    let mut scenarios: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D26 worker"))
        .collect();
    scenarios.sort_by_key(|row| (row.task.seed, row.task.seat, row.task.opponent_index));

    let mut writer = BufWriter::new(File::create(&output).expect("create D26 output"));
    writeln!(
        writer,
        "seed\tseat\topponent\treached_cut\toption\texit_turn\troot_turn\troot_my_score\troot_opponent_score\troot_my_wood\troot_opponent_wood\troot_my_workers\troot_opponent_workers\troot_plants\tfinal_turn\tmargin\tmy_score\topponent_score\tmy_wood\topponent_wood\tmy_workers\topponent_workers\tmax_my_workers\tfarm_turns\trestart_turns\tfarm_train_commands\tfarm_plant_commands\trestart_train_commands\trestart_plant_commands\tcommand_hash"
    )
    .expect("write D26 header");
    let mut row_count = 0;
    for scenario in scenarios {
        let task = scenario.task;
        for branch in scenario.branches {
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                task.seed,
                task.seat,
                OPPONENTS[task.opponent_index].0,
                usize::from(scenario.reached_cut),
                branch.label,
                branch.exit_turn,
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
                branch.farm_turns,
                branch.restart_turns,
                branch.farm_train_commands,
                branch.farm_plant_commands,
                branch.restart_train_commands,
                branch.restart_plant_commands,
                branch.command_hash,
            )
            .expect("write D26 row");
            row_count += 1;
        }
    }
    writer.flush().expect("flush D26 output");
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
    fn exits_are_sorted_and_unique() {
        assert_eq!(parse_exits("150,100,125,100"), vec![100, 125, 150]);
    }

    #[test]
    fn trace_hash_is_repeatable() {
        let commands = vec!["MOVE 0 1 2".to_string(), "CHOP 1".to_string()];
        let mut first = FNV_OFFSET;
        let mut second = FNV_OFFSET;
        trace_commands(&mut first, &commands);
        trace_commands(&mut second, &commands);
        assert_eq!(first, second);
    }
}
