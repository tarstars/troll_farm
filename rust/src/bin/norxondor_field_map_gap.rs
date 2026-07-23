//! Run resident and exact-three-worker policies on the five consumed Stage 2A field maps.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::cell::RefCell;
use std::collections::BTreeSet;
use std::fs::File;
use std::io::{BufReader, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use troll_farm::game::engine::{has_stalled, step, WOOD};
use troll_farm::game::state::{GameState, Plant as EnginePlant, Unit as EngineUnit};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_research::NorxondorThreeWorkerSilver;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::protocol::{read_line, read_static_map, read_turn};
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const MODELS: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];
const POLICIES: [&str; 2] = ["resident", "norx_three_worker_silver"];
const ACTIONS: [&str; 8] = [
    "TRAIN", "MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "DROP", "MINE",
];

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

fn yamo_view(game: &GameState) -> YamoState {
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: game.shacks,
        inventories: game.inventories,
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: unit.player as usize,
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
        scores: game.scores,
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn engine_state(view: YamoState) -> GameState {
    GameState {
        width: view.width,
        height: view.height,
        walkable: view.walkable.into_iter().collect(),
        shacks: view.shacks,
        inventories: view.inventories,
        units: view
            .units
            .into_iter()
            .map(|unit| EngineUnit {
                id: unit.id,
                player: unit.player as i32,
                x: unit.cell.0,
                y: unit.cell.1,
                ms: unit.stats.movement_speed,
                cc: unit.stats.carry_capacity,
                hp: unit.stats.harvest_power,
                chop: unit.stats.chop_power,
                carry: unit.carry,
            })
            .collect(),
        plants: view
            .plants
            .into_iter()
            .map(|plant| EnginePlant {
                plant_type: plant.kind.as_str().to_string(),
                x: plant.cell.0,
                y: plant.cell.1,
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: view.scores,
        turn: view.turn,
        next_id: view.next_id,
        iron: view.iron.into_iter().collect(),
        water: view.water.into_iter().collect(),
    }
}

fn read_dataset(path: &str) -> Vec<(u64, GameState)> {
    let file = File::open(path).expect("open exact field map dataset");
    let mut reader = BufReader::new(file);
    let mut maps = Vec::new();
    while let Some(line) = read_line(&mut reader) {
        if line.is_empty() {
            continue;
        }
        let mut fields = line.split_whitespace();
        assert_eq!(fields.next(), Some("SEED"));
        let game_id = fields.next().unwrap().parse::<u64>().unwrap();
        let map = read_static_map(&mut reader).expect("static map");
        let view = read_turn(&mut reader, &map, 1).expect("turn-one state");
        maps.push((game_id, engine_state(view)));
    }
    maps
}

struct ResidentAdapter {
    bot: RefCell<SecureOrchardBot>,
}

impl ResidentAdapter {
    fn new() -> Self {
        Self {
            bot: RefCell::new(SecureOrchardBot::new()),
        }
    }
}

impl Strategy for ResidentAdapter {
    fn name(&self) -> &str {
        "resident"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        assert_eq!(player, 0);
        self.bot.borrow_mut().commands(&yamo_view(game))
    }
}

fn policy(index: usize) -> Box<dyn Strategy> {
    match index {
        0 => Box::new(ResidentAdapter::new()),
        1 => Box::new(NorxondorThreeWorkerSilver::new()),
        _ => unreachable!(),
    }
}

#[derive(Clone, Copy)]
struct Task {
    map: usize,
    policy: usize,
    model: usize,
}

struct Row {
    task: Task,
    game_id: u64,
    terminal_turn: i32,
    score: i32,
    opponent_score: i32,
    wood: i32,
    opponent_wood: i32,
    workers: usize,
    opponent_workers: usize,
    second_worker_turn: i32,
    third_worker_turn: i32,
    action_counts: [i32; 8],
}

fn count_actions(commands: &[String], counts: &mut [i32; 8]) {
    for command in commands {
        let Some(verb) = command.split_whitespace().next() else {
            continue;
        };
        if let Some(index) = ACTIONS.iter().position(|candidate| *candidate == verb) {
            counts[index] += 1;
        }
    }
}

fn play(task: Task, game_id: u64, initial: &GameState) -> Row {
    let mut game = initial.clone();
    let candidate = policy(task.policy);
    let opposing = opponent(task.model);
    let mut turns_until_end = 0;
    let mut second_worker_turn = 0;
    let mut third_worker_turn = 0;
    let mut action_counts = [0; 8];
    for _ in 0..300 {
        let ours = candidate.decide(&game, 0);
        let theirs = opposing.decide(&game, 1);
        count_actions(&ours, &mut action_counts);
        step(&mut game, &ours, &theirs);
        let workers = game.units.iter().filter(|unit| unit.player == 0).count();
        if workers >= 2 && second_worker_turn == 0 {
            second_worker_turn = game.turn - 1;
        }
        if workers >= 3 && third_worker_turn == 0 {
            third_worker_turn = game.turn - 1;
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    Row {
        task,
        game_id,
        terminal_turn: game.turn - 1,
        score: game.scores[0],
        opponent_score: game.scores[1],
        wood: game.inventories[0][WOOD],
        opponent_wood: game.inventories[1][WOOD],
        workers: game.units.iter().filter(|unit| unit.player == 0).count(),
        opponent_workers: game.units.iter().filter(|unit| unit.player == 1).count(),
        second_worker_turn,
        third_worker_turn,
        action_counts,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let input = args.get(1).expect("map dataset path");
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "norxondor-field-map-gap.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(18)
        .max(1);
    let maps = Arc::new(read_dataset(input));
    assert_eq!(maps.len(), 5, "frozen Stage 2A map count");
    let tasks: Vec<_> = (0..maps.len())
        .flat_map(|map| {
            (0..POLICIES.len()).flat_map(move |policy| {
                (0..MODELS.len()).map(move |model| Task { map, policy, model })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads.min(tasks.len()))
            .map(|_| {
                let maps = Arc::clone(&maps);
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        let task = tasks[index];
                        let (game_id, initial) = &maps[task.map];
                        local.push(play(task, *game_id, initial));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("field-map worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.game_id, row.task.policy, row.task.model));
    assert_eq!(rows.len(), 80);
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    write!(writer, "game_id\tpolicy\tmodel\tterminal_turn\tscore\topponent_score\tmargin\twood\topponent_wood\tworkers\topponent_workers\tsecond_worker_turn\tthird_worker_turn").unwrap();
    for action in ACTIONS {
        write!(writer, "\t{}_commands", action.to_ascii_lowercase()).unwrap();
    }
    writeln!(writer).unwrap();
    for row in rows {
        write!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.game_id,
            POLICIES[row.task.policy],
            MODELS[row.task.model],
            row.terminal_turn,
            row.score,
            row.opponent_score,
            row.score - row.opponent_score,
            row.wood,
            row.opponent_wood,
            row.workers,
            row.opponent_workers,
            row.second_worker_turn,
            row.third_worker_turn,
        )
        .unwrap();
        for count in row.action_counts {
            write!(writer, "\t{count}").unwrap();
        }
        writeln!(writer).unwrap();
    }
    writer.flush().unwrap();
    eprintln!("saved 80 exact-field-map cells to {output}");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_catalogs_are_unique() {
        assert_eq!(MODELS.iter().collect::<BTreeSet<_>>().len(), 8);
        assert_eq!(POLICIES.iter().collect::<BTreeSet<_>>().len(), 2);
    }
}
