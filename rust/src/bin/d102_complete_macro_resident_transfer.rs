//! D102a: exact D40 complete-macro controller versus the current embedded resident.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::resident_policy::bot::moisan::SecureOrchardBot;
use troll_farm::resident_policy::bot::Bot as ResidentBot;
use troll_farm::resident_policy::game::{
    GameState as ResidentState, Plant as ResidentPlant, PlantKind, Stats as ResidentStats,
    Unit as ResidentUnit,
};
use troll_farm::rl_macro::{CompleteMacroEnv, MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Policy {
    D40,
    Resident,
}

impl Policy {
    fn label(self) -> &'static str {
        match self {
            Self::D40 => "d40",
            Self::Resident => "resident",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Owner {
    Natural,
    Own,
    Opponent,
    Joint,
    Ambiguous,
}

#[derive(Clone, Copy, Debug, PartialEq)]
struct Outcome {
    done: bool,
    turn: u16,
    own_score: i32,
    opponent_score: i32,
    own_return: f32,
    opponent_return: f32,
    margin_return: f32,
    reward_identity_error: f32,
    own_workers: u8,
    opponent_workers: u8,
    max_own_workers: u8,
    successful_trains: u8,
    completed_jobs: u16,
    invalidated_jobs: u16,
    invalid_direct_commands: u16,
    provenance_failures: u16,
    deposit_prediction_failures: u16,
    own_created_crops: u16,
    opponent_created_crops: u16,
    joint_created_crops: u16,
    ambiguous_created_crops: u16,
    own_owned_crop_harvest_units: u16,
    own_reinvested_crops: u16,
    action_hash: u64,
    state_hash: u64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
struct Row {
    task: Task,
    policy: Policy,
    outcome: Outcome,
}

enum Opponent {
    Resident(SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => Self::Resident(SecureOrchardBot::new()),
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => Self::Local(Box::new(NorxondorNative::new(true))),
            MacroOpponentMode::LegendBalanced => Self::Local(Box::new(
                LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }),
            )),
            MacroOpponentMode::MyBot => Self::Local(Box::new(MyBot::new())),
            MacroOpponentMode::ScriptBoss => Self::Local(Box::new(ScriptBoss::new())),
            MacroOpponentMode::SilverBoss => Self::Local(Box::new(SilverBoss::new())),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&resident_view(game, player)),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn resident_view(game: &GameState, player: usize) -> ResidentState {
    let opponent = 1 - player;
    ResidentState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| ResidentUnit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: ResidentStats {
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
            .map(|plant| ResidentPlant {
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
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

fn worker_count(game: &GameState, player: usize) -> usize {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count()
}

fn plant_attempts(game: &GameState, player: usize, commands: &[String]) -> BTreeSet<Cell> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            (fields.next()? == "PLANT").then_some(())?;
            let id = fields.next()?.parse::<i32>().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(|unit| unit.pos())
        })
        .collect()
}

fn command_unit_ids(commands: &[String], verb: &str) -> Vec<i32> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            (fields.next()? == verb).then_some(())?;
            fields.next()?.parse::<i32>().ok()
        })
        .collect()
}

fn fnv1a(mut hash: u64, bytes: &[u8]) -> u64 {
    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(1_099_511_628_211);
    }
    hash
}

fn hash_i32(hash: u64, value: i32) -> u64 {
    fnv1a(hash, &value.to_le_bytes())
}

fn canonical_state_hash(game: &GameState) -> u64 {
    let mut hash = 14_695_981_039_346_656_037_u64;
    for value in [game.width, game.height, game.turn, game.next_id] {
        hash = hash_i32(hash, value);
    }
    for cell in game.shacks {
        hash = hash_i32(hash, cell.0);
        hash = hash_i32(hash, cell.1);
    }
    for inventory in game.inventories {
        for value in inventory {
            hash = hash_i32(hash, value);
        }
    }
    for value in game.scores {
        hash = hash_i32(hash, value);
    }
    for cells in [&game.walkable, &game.iron, &game.water] {
        let mut cells: Vec<_> = cells.iter().copied().collect();
        cells.sort_unstable();
        hash = hash_i32(hash, cells.len() as i32);
        for cell in cells {
            hash = hash_i32(hash, cell.0);
            hash = hash_i32(hash, cell.1);
        }
    }
    let mut units: Vec<_> = game.units.iter().collect();
    units.sort_by_key(|unit| unit.id);
    hash = hash_i32(hash, units.len() as i32);
    for unit in units {
        for value in [
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ] {
            hash = hash_i32(hash, value);
        }
        for value in unit.carry {
            hash = hash_i32(hash, value);
        }
    }
    let mut plants: Vec<_> = game.plants.iter().collect();
    plants.sort_by_key(|plant| (plant.x, plant.y, plant.plant_type.as_str()));
    hash = hash_i32(hash, plants.len() as i32);
    for plant in plants {
        hash = fnv1a(hash, plant.plant_type.as_bytes());
        hash = fnv1a(hash, &[0]);
        for value in [
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ] {
            hash = hash_i32(hash, value);
        }
    }
    hash
}

fn play_d40(task: Task) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let terminal = env.run_work_conserving_deficit_heuristic();
    let margin = terminal.own_score - terminal.opponent_score;
    Row {
        task,
        policy: Policy::D40,
        outcome: Outcome {
            done: terminal.done,
            turn: terminal.turn,
            own_score: terminal.own_score,
            opponent_score: terminal.opponent_score,
            own_return: terminal.own_return,
            opponent_return: terminal.opponent_return,
            margin_return: terminal.margin_return,
            reward_identity_error: (terminal.margin_return - margin as f32 / 100.0).abs(),
            own_workers: terminal.own_workers,
            opponent_workers: terminal.opponent_workers,
            max_own_workers: terminal.own_workers,
            successful_trains: terminal.successful_trains,
            completed_jobs: terminal.completed_jobs,
            invalidated_jobs: terminal.invalidated_jobs,
            invalid_direct_commands: terminal.invalid_direct_commands,
            provenance_failures: terminal.provenance_failures,
            deposit_prediction_failures: terminal.deposit_prediction_failures,
            own_created_crops: terminal.own_created_crops,
            opponent_created_crops: terminal.opponent_created_crops,
            joint_created_crops: 0,
            ambiguous_created_crops: terminal.ambiguous_created_crops,
            own_owned_crop_harvest_units: terminal.own_owned_crop_harvest_units,
            own_reinvested_crops: terminal.own_reinvested_crops,
            action_hash: terminal.action_hash,
            state_hash: terminal.state_hash,
        },
    }
}

fn update_provenance(
    game: &GameState,
    before_plants: &BTreeSet<Cell>,
    attempts: &[BTreeSet<Cell>; 2],
    owners: &mut BTreeMap<Cell, Owner>,
    seat: usize,
) -> (usize, usize, usize, usize, usize) {
    let after_plants: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    owners.retain(|cell, _| after_plants.contains(cell));
    let mut failures = 0usize;
    let mut own = 0usize;
    let mut opponent = 0usize;
    let mut joint = 0usize;
    let ambiguous = 0usize;
    for cell in after_plants.difference(before_plants) {
        let claimants: Vec<_> = (0..2)
            .filter(|player| attempts[*player].contains(cell))
            .collect();
        let owner = match claimants.as_slice() {
            [player] if *player == seat => {
                own += 1;
                Owner::Own
            }
            [player] if *player == 1 - seat => {
                opponent += 1;
                Owner::Opponent
            }
            [_, _] => {
                // The exact engine merges same-kind simultaneous PLANT intents and charges both
                // planters. A surviving two-claimant birth therefore has known joint provenance.
                joint += 1;
                Owner::Joint
            }
            _ => {
                failures += 1;
                Owner::Ambiguous
            }
        };
        owners.insert(*cell, owner);
    }
    failures += owners
        .keys()
        .copied()
        .collect::<BTreeSet<_>>()
        .symmetric_difference(&after_plants)
        .count();
    (failures, own, opponent, joint, ambiguous)
}

fn play_resident(task: Task) -> Row {
    let mut game = generate_official(task.map_seed);
    let mut ours = SecureOrchardBot::new();
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Owner::Natural))
        .collect();
    let mut turns_until_end = 0i32;
    let mut action_hash = 14_695_981_039_346_656_037_u64;
    let mut max_own_workers = worker_count(&game, task.seat);
    let mut successful_trains = 0usize;
    let mut provenance_failures = 0usize;
    let mut own_created_crops = 0usize;
    let mut opponent_created_crops = 0usize;
    let mut joint_created_crops = 0usize;
    let mut ambiguous_created_crops = 0usize;
    let mut own_owned_crop_harvest_units = 0usize;
    let mut own_reinvested_crops = 0usize;
    let mut done = false;

    while !done {
        let ours_commands = ours.commands(&resident_view(&game, task.seat));
        let theirs_commands = theirs.commands(&game, 1 - task.seat);
        let commands = if task.seat == 0 {
            [ours_commands, theirs_commands]
        } else {
            [theirs_commands, ours_commands]
        };
        for (player, player_commands) in commands.iter().enumerate() {
            action_hash = fnv1a(action_hash, &[player as u8]);
            for command in player_commands {
                action_hash = fnv1a(action_hash, command.as_bytes());
                action_hash = fnv1a(action_hash, &[0]);
            }
            action_hash = fnv1a(action_hash, &[255]);
        }

        let before_plants: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        let attempts = [
            plant_attempts(&game, 0, &commands[0]),
            plant_attempts(&game, 1, &commands[1]),
        ];
        let before_workers = worker_count(&game, task.seat);
        let harvest_ids = command_unit_ids(&commands[task.seat], "HARVEST");
        let own_crop_harvests: Vec<_> = harvest_ids
            .into_iter()
            .filter_map(|id| {
                let unit = game
                    .units
                    .iter()
                    .find(|unit| unit.id == id && unit.player as usize == task.seat)?;
                (owners.get(&unit.pos()) == Some(&Owner::Own)).then_some((id, unit.carry))
            })
            .collect();
        let had_renewable_receipt = own_owned_crop_harvest_units > 0;

        step(&mut game, &commands[0], &commands[1]);

        let (failures, own_plants, opponent_plants, joint_plants, ambiguous_plants) =
            update_provenance(&game, &before_plants, &attempts, &mut owners, task.seat);
        provenance_failures += failures;
        own_created_crops += own_plants;
        opponent_created_crops += opponent_plants;
        joint_created_crops += joint_plants;
        ambiguous_created_crops += ambiguous_plants;
        if had_renewable_receipt {
            own_reinvested_crops += own_plants;
        }
        for (id, before_carry) in own_crop_harvests {
            let Some(unit) = game.units.iter().find(|unit| unit.id == id) else {
                continue;
            };
            let gained = (0..4)
                .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                .sum::<i32>();
            own_owned_crop_harvest_units += gained.max(0) as usize;
        }
        let after_workers = worker_count(&game, task.seat);
        successful_trains += after_workers.saturating_sub(before_workers);
        max_own_workers = max_own_workers.max(after_workers);
        done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
    }

    let own_score = game.scores[task.seat];
    let opponent_score = game.scores[1 - task.seat];
    let margin = own_score - opponent_score;
    let own_return = own_score as f32 / 100.0;
    let opponent_return = opponent_score as f32 / 100.0;
    let margin_return = margin as f32 / 100.0;
    Row {
        task,
        policy: Policy::Resident,
        outcome: Outcome {
            done,
            turn: game.turn.clamp(0, u16::MAX as i32) as u16,
            own_score,
            opponent_score,
            own_return,
            opponent_return,
            margin_return,
            reward_identity_error: (margin_return - (own_return - opponent_return)).abs(),
            own_workers: worker_count(&game, task.seat).min(u8::MAX as usize) as u8,
            opponent_workers: worker_count(&game, 1 - task.seat).min(u8::MAX as usize) as u8,
            max_own_workers: max_own_workers.min(u8::MAX as usize) as u8,
            successful_trains: successful_trains.min(u8::MAX as usize) as u8,
            completed_jobs: 0,
            invalidated_jobs: 0,
            invalid_direct_commands: 0,
            provenance_failures: provenance_failures.min(u16::MAX as usize) as u16,
            deposit_prediction_failures: 0,
            own_created_crops: own_created_crops.min(u16::MAX as usize) as u16,
            opponent_created_crops: opponent_created_crops.min(u16::MAX as usize) as u16,
            joint_created_crops: joint_created_crops.min(u16::MAX as usize) as u16,
            ambiguous_created_crops: ambiguous_created_crops.min(u16::MAX as usize) as u16,
            own_owned_crop_harvest_units: own_owned_crop_harvest_units.min(u16::MAX as usize)
                as u16,
            own_reinvested_crops: own_reinvested_crops.min(u16::MAX as usize) as u16,
            action_hash,
            state_hash: canonical_state_hash(&game),
        },
    }
}

fn play(task: Task) -> [Row; 2] {
    [play_d40(task), play_resident(task)]
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create D102a output"));
    writeln!(writer, "map_seed\tseat\topponent_index\topponent\tpolicy\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash").expect("write D102a header");
    for row in rows {
        let out = row.outcome;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.9}\t{:.9}\t{:.9}\t{:.9}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.policy.label(),
            usize::from(out.done),
            out.turn,
            out.own_score,
            out.opponent_score,
            out.own_score - out.opponent_score,
            out.own_return,
            out.opponent_return,
            out.margin_return,
            out.reward_identity_error,
            out.own_workers,
            out.opponent_workers,
            out.max_own_workers,
            out.successful_trains,
            out.completed_jobs,
            out.invalidated_jobs,
            out.invalid_direct_commands,
            out.provenance_failures,
            out.deposit_prediction_failures,
            out.own_created_crops,
            out.opponent_created_crops,
            out.joint_created_crops,
            out.ambiguous_created_crops,
            out.own_owned_crop_harvest_units,
            out.own_reinvested_crops,
            out.action_hash,
            out.state_hash,
        )
        .expect("write D102a row");
    }
    writer.flush().expect("flush D102a output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let start_seed = args
        .get(1)
        .map_or(9_824_100, |value| value.parse::<i64>().expect("start seed"));
    let map_count = args
        .get(2)
        .map_or(32, |value| value.parse::<usize>().expect("map count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d102a-complete-macro-resident-transfer.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(20, |value| value.parse::<usize>().expect("threads"));
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
    let rows = Arc::new(Mutex::new(Vec::with_capacity(tasks.len() * 2)));
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
                rows.lock().expect("D102a row lock").extend(play(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D102a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D102a rows")
        .into_inner()
        .expect("D102a rows lock");
    rows.sort_by_key(|row| (row.task, row.policy));
    write_rows(&output, &rows);
    eprintln!(
        "saved {} D102a rows with {} workers in {:.3}s to {}",
        rows.len(),
        threads.min(tasks.len()),
        started.elapsed().as_secs_f64(),
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn smoke_task() -> Task {
        Task {
            map_seed: 9_824_000,
            seat: 0,
            opponent: 0,
        }
    }

    #[test]
    fn both_paths_are_deterministic_terminal_and_clean() {
        let task = smoke_task();
        let first = play(task);
        let second = play(task);
        assert_eq!(first, second);
        for row in first {
            assert!(row.outcome.done);
            assert!(row.outcome.turn <= 301);
            assert_eq!(row.outcome.provenance_failures, 0);
            assert_eq!(row.outcome.ambiguous_created_crops, 0);
            assert!(row.outcome.reward_identity_error <= 1e-6);
        }
        assert_eq!(first[0].policy, Policy::D40);
        assert_eq!(first[1].policy, Policy::Resident);
    }

    #[test]
    fn opponent_index_labels_are_frozen() {
        let labels: Vec<_> = (0..MacroOpponentMode::ALL.len())
            .map(|index| MacroOpponentMode::from_index(index).label())
            .collect();
        assert_eq!(
            labels,
            vec![
                "resident",
                "gold_adaptive",
                "compact_gold",
                "norx_native_three",
                "legend_balanced",
                "mybot",
                "script_boss",
                "silver_boss",
            ]
        );
    }

    #[test]
    fn simultaneous_resident_births_have_known_joint_provenance() {
        for seat in 0..2 {
            let row = play_resident(Task {
                map_seed: 9_824_115,
                seat,
                opponent: 0,
            });
            assert_eq!(row.outcome.provenance_failures, 0);
            assert_eq!(row.outcome.ambiguous_created_crops, 0);
            assert_eq!(row.outcome.joint_created_crops, 2);
        }
    }
}
