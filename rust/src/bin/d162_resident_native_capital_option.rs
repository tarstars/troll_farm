//! D162a: bounded third-worker capital options over an always-warm exact resident.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{
    bfs_distances, has_stalled, step, training_cost, APPLE, IRON, LEMON, PLUM,
};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState, Unit};
use troll_farm::resident_policy::bot::moisan::SecureOrchardBot;
use troll_farm::resident_policy::bot::Bot as ResidentBot;
use troll_farm::resident_policy::game::{
    GameState as ResidentState, Plant as ResidentPlant, PlantKind, Stats as ResidentStats,
    Unit as ResidentUnit,
};
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const MARKS: [i32; 3] = [72, 104, 136];
const ITEM_NAMES: [&str; 6] = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"];

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct OptionConfig {
    stats: (i32, i32, i32, i32),
    start: i32,
    horizon: i32,
}

#[derive(Clone, Debug)]
struct PolicySpec {
    label: String,
    option: Option<OptionConfig>,
}

fn policy_catalog() -> Vec<PolicySpec> {
    let mut policies = vec![PolicySpec {
        label: "resident".to_string(),
        option: None,
    }];
    for (name, stats) in [("minimal_1101", (1, 1, 0, 1)), ("balanced_2202", (2, 2, 0, 2))] {
        for start in MARKS {
            for horizon in [32, 64] {
                policies.push(PolicySpec {
                    label: format!("{name}_t{start:03}_h{horizon:03}"),
                    option: Some(OptionConfig {
                        stats,
                        start,
                        horizon,
                    }),
                });
            }
        }
    }
    policies
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Owner {
    Natural,
    Own,
    Opponent,
    Joint,
    Ambiguous,
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
struct OptionTelemetry {
    activated: bool,
    activation_turn: i32,
    deadline: i32,
    active_turns: u16,
    committed: bool,
    aborted: bool,
    option_overrides: u16,
    protected_commands: u16,
    move_commands: u16,
    bank_commands: u16,
    harvest_commands: u16,
    mine_commands: u16,
    train_attempts: u16,
    train_successes: u16,
    trained_turn: i32,
    initial_bank_deficit: i32,
    closest_bank_deficit: i32,
    option_command_failures: u16,
    affordability_violations: u16,
    transaction_failures: u16,
    worker_cap_violations: u16,
    horizon_violations: u16,
    restart_violations: u16,
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
    prefix_captured: [bool; 3],
    prefix_action_hash: [u64; 3],
    prefix_state_hash: [u64; 3],
    option: OptionTelemetry,
}

#[derive(Clone, Debug, PartialEq)]
struct Row {
    task: Task,
    policy: usize,
    outcome: Outcome,
}

#[derive(Clone, Copy, Debug)]
struct Work {
    task: Task,
    policy: usize,
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

fn own_units(game: &GameState, player: usize) -> Vec<&Unit> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    units
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn home_doors(game: &GameState, player: usize) -> Vec<Cell> {
    let shack = game.shacks[player];
    let mut doors: Vec<_> = game
        .walkable
        .iter()
        .copied()
        .filter(|cell| manhattan(*cell, shack) == 1)
        .collect();
    doors.sort_unstable();
    doors
}

fn command_fields(command: &str) -> Vec<&str> {
    command.split_whitespace().collect()
}

fn command_unit(command: &str) -> Option<i32> {
    let fields = command_fields(command);
    match fields.first().copied()? {
        "MOVE" | "HARVEST" | "PLANT" | "CHOP" | "PICK" | "DROP" | "MINE" => {
            fields.get(1)?.parse().ok()
        }
        _ => None,
    }
}

fn command_item(command: &str) -> Option<usize> {
    let fields = command_fields(command);
    if !matches!(fields.first().copied(), Some("PICK" | "PLANT")) {
        return None;
    }
    ITEM_NAMES.iter().position(|name| Some(name) == fields.get(2))
}

fn bill(game: &GameState, config: OptionConfig) -> [i32; 6] {
    let mut cost = training_cost(2, config.stats);
    if game.iron.is_empty() {
        cost[IRON] = 0;
    }
    cost
}

fn bank_deficit(game: &GameState, player: usize, cost: &[i32; 6]) -> i32 {
    (0..6)
        .map(|item| (cost[item] - game.inventories[player][item]).max(0))
        .sum()
}

fn liquid_deficits(game: &GameState, player: usize, cost: &[i32; 6]) -> [i32; 6] {
    let mut liquid = game.inventories[player];
    for unit in own_units(game, player) {
        for item in 0..6 {
            liquid[item] += unit.carry[item];
        }
    }
    let mut deficits = [0; 6];
    for item in 0..6 {
        deficits[item] = (cost[item] - liquid[item]).max(0);
    }
    deficits
}

fn affordable(game: &GameState, player: usize, cost: &[i32; 6]) -> bool {
    (0..6).all(|item| game.inventories[player][item] >= cost[item])
}

#[derive(Clone, Debug)]
struct CapitalOption {
    config: Option<OptionConfig>,
    telemetry: OptionTelemetry,
}

impl CapitalOption {
    fn new(config: Option<OptionConfig>) -> Self {
        Self {
            config,
            telemetry: OptionTelemetry {
                activation_turn: -1,
                deadline: -1,
                trained_turn: -1,
                initial_bank_deficit: -1,
                closest_bank_deficit: -1,
                ..OptionTelemetry::default()
            },
        }
    }

    fn active(&self) -> bool {
        self.telemetry.activated && !self.telemetry.committed && !self.telemetry.aborted
    }

    fn bank_command(game: &GameState, player: usize, unit: &Unit) -> String {
        if manhattan(unit.pos(), game.shacks[player]) == 1 {
            format!("DROP {}", unit.id)
        } else {
            format!("MOVE {} {} {}", unit.id, game.shacks[player].0, game.shacks[player].1)
        }
    }

    fn carried_bill_worker<'a>(
        game: &'a GameState,
        player: usize,
        cost: &[i32; 6],
    ) -> Option<&'a Unit> {
        own_units(game, player).into_iter().max_by_key(|unit| {
            let progress: i32 = (0..6)
                .map(|item| {
                    unit.carry[item]
                        .min((cost[item] - game.inventories[player][item]).max(0))
                })
                .sum();
            (progress > 0, progress, -unit.id)
        }).filter(|unit| {
            (0..6).any(|item| {
                unit.carry[item] > 0 && game.inventories[player][item] < cost[item]
            })
        })
    }

    fn fruit_command(
        game: &GameState,
        player: usize,
        item: usize,
    ) -> Option<(i32, String)> {
        let doors = home_doors(game, player);
        if doors.is_empty() {
            return None;
        }
        let from_home = bfs_distances(&game.walkable, &doors);
        let mut choices = Vec::new();
        for unit in own_units(game, player) {
            if unit.hp <= 0 || unit.free() <= 0 {
                continue;
            }
            let from_unit = bfs_distances(&game.walkable, &[unit.pos()]);
            for plant in &game.plants {
                if plant.health <= 0
                    || plant.fruits <= 0
                    || plant.plant_type != ITEM_NAMES[item]
                {
                    continue;
                }
                let (Some(distance), Some(home)) =
                    (from_unit.get(&plant.pos()), from_home.get(&plant.pos()))
                else {
                    continue;
                };
                choices.push((*distance + *home, *distance, unit.id, plant.pos()));
            }
        }
        let (_, _, id, target) = choices.into_iter().min()?;
        let unit = game.units.iter().find(|unit| unit.id == id)?;
        let command = if unit.pos() == target {
            format!("HARVEST {id}")
        } else {
            format!("MOVE {id} {} {}", target.0, target.1)
        };
        Some((id, command))
    }

    fn mine_command(game: &GameState, player: usize) -> Option<(i32, String)> {
        let doors = home_doors(game, player);
        if doors.is_empty() {
            return None;
        }
        let from_home = bfs_distances(&game.walkable, &doors);
        let mut targets: Vec<_> = game
            .walkable
            .iter()
            .copied()
            .filter(|cell| game.iron.iter().any(|ore| manhattan(*cell, *ore) == 1))
            .collect();
        targets.sort_unstable();
        let mut choices = Vec::new();
        for unit in own_units(game, player) {
            if unit.chop <= 0 || unit.free() <= 0 {
                continue;
            }
            let from_unit = bfs_distances(&game.walkable, &[unit.pos()]);
            for target in &targets {
                let (Some(distance), Some(home)) = (from_unit.get(target), from_home.get(target))
                else {
                    continue;
                };
                choices.push((*distance + *home, *distance, unit.id, *target));
            }
        }
        let (_, _, id, target) = choices.into_iter().min()?;
        let unit = game.units.iter().find(|unit| unit.id == id)?;
        let command = if unit.pos() == target {
            format!("MINE {id}")
        } else {
            format!("MOVE {id} {} {}", target.0, target.1)
        };
        Some((id, command))
    }

    fn acquisition_command(
        &self,
        game: &GameState,
        player: usize,
        cost: &[i32; 6],
    ) -> Option<(i32, String)> {
        if let Some(unit) = Self::carried_bill_worker(game, player, cost) {
            return Some((unit.id, Self::bank_command(game, player, unit)));
        }
        let deficits = liquid_deficits(game, player, cost);
        let mut resources = vec![PLUM, LEMON, APPLE, IRON];
        resources.sort_by_key(|item| (-deficits[*item], *item));
        for item in resources {
            if deficits[item] <= 0 {
                continue;
            }
            let command = if item == IRON {
                Self::mine_command(game, player)
            } else {
                Self::fruit_command(game, player, item)
            };
            if command.is_some() {
                return command;
            }
        }
        None
    }

    fn generated_command_is_legal(game: &GameState, player: usize, command: &str) -> bool {
        let fields = command_fields(command);
        match fields.first().copied().unwrap_or("WAIT") {
            "MOVE" => command_unit(command).is_some_and(|id| {
                game.units
                    .iter()
                    .any(|unit| unit.id == id && unit.player as usize == player)
                    && fields.get(2).and_then(|value| value.parse::<i32>().ok()).is_some()
                    && fields.get(3).and_then(|value| value.parse::<i32>().ok()).is_some()
            }),
            "DROP" => command_unit(command).is_some_and(|id| {
                game.units.iter().any(|unit| {
                    unit.id == id
                        && unit.player as usize == player
                        && unit.total() > 0
                        && manhattan(unit.pos(), game.shacks[player]) == 1
                })
            }),
            "HARVEST" => command_unit(command).is_some_and(|id| {
                game.units.iter().any(|unit| {
                    unit.id == id
                        && unit.player as usize == player
                        && unit.hp > 0
                        && unit.free() > 0
                        && game.plants.iter().any(|plant| {
                            plant.pos() == unit.pos() && plant.health > 0 && plant.fruits > 0
                        })
                })
            }),
            "MINE" => command_unit(command).is_some_and(|id| {
                game.units.iter().any(|unit| {
                    unit.id == id
                        && unit.player as usize == player
                        && unit.chop > 0
                        && unit.free() > 0
                        && game.iron.iter().any(|ore| manhattan(unit.pos(), *ore) == 1)
                })
            }),
            "TRAIN" => true,
            _ => false,
        }
    }

    fn rewrite(
        &mut self,
        game: &GameState,
        player: usize,
        resident_commands: Vec<String>,
    ) -> Vec<String> {
        let Some(config) = self.config else {
            return resident_commands;
        };
        let workers = worker_count(game, player);
        if game.turn == config.start {
            if self.telemetry.activated {
                self.telemetry.restart_violations += 1;
            } else if workers == 2 {
                let cost = bill(game, config);
                let deficit = bank_deficit(game, player, &cost);
                self.telemetry.activated = true;
                self.telemetry.activation_turn = game.turn;
                self.telemetry.deadline = config.start + config.horizon;
                self.telemetry.initial_bank_deficit = deficit;
                self.telemetry.closest_bank_deficit = deficit;
            }
        }
        if !self.active() {
            return resident_commands;
        }
        if workers > 2 {
            self.telemetry.committed = true;
            return resident_commands;
        }
        if game.turn >= self.telemetry.deadline {
            self.telemetry.aborted = true;
            return resident_commands;
        }
        self.telemetry.active_turns += 1;
        if i32::from(self.telemetry.active_turns) > config.horizon {
            self.telemetry.horizon_violations += 1;
        }
        let cost = bill(game, config);
        self.telemetry.closest_bank_deficit = self
            .telemetry
            .closest_bank_deficit
            .min(bank_deficit(game, player, &cost));

        let train_now = affordable(game, player, &cost)
            && !game
                .units
                .iter()
                .any(|unit| unit.pos() == game.shacks[player]);
        let acquisition = (!train_now).then(|| self.acquisition_command(game, player, &cost)).flatten();
        let selected_id = acquisition.as_ref().map(|(id, _)| *id);
        let mut rewritten = Vec::new();
        for command in resident_commands {
            if command_unit(&command).is_some_and(|id| Some(id) == selected_id) {
                continue;
            }
            let fields = command_fields(&command);
            let verb = fields.first().copied().unwrap_or("WAIT");
            let protected = command_item(&command).is_some_and(|item| {
                item < 6 && game.inventories[player][item] < cost[item]
            });
            let unsafe_train_command = train_now
                && (verb == "PICK"
                    || (verb == "MOVE"
                        && fields.get(2).and_then(|value| value.parse::<i32>().ok())
                            == Some(game.shacks[player].0)
                        && fields.get(3).and_then(|value| value.parse::<i32>().ok())
                            == Some(game.shacks[player].1)));
            if protected || unsafe_train_command {
                self.telemetry.protected_commands += 1;
                continue;
            }
            rewritten.push(command);
        }

        if let Some((_, command)) = acquisition {
            if !Self::generated_command_is_legal(game, player, &command) {
                self.telemetry.option_command_failures += 1;
            } else {
                self.telemetry.option_overrides += 1;
                match command_fields(&command).first().copied().unwrap_or("WAIT") {
                    "MOVE" => self.telemetry.move_commands += 1,
                    "DROP" => self.telemetry.bank_commands += 1,
                    "HARVEST" => self.telemetry.harvest_commands += 1,
                    "MINE" => self.telemetry.mine_commands += 1,
                    _ => self.telemetry.option_command_failures += 1,
                }
                rewritten.push(command);
            }
        }
        if train_now {
            if !affordable(game, player, &cost) {
                self.telemetry.affordability_violations += 1;
            }
            rewritten.push(format!(
                "TRAIN {} {} {} {}",
                config.stats.0, config.stats.1, config.stats.2, config.stats.3
            ));
            self.telemetry.train_attempts += 1;
        }
        rewritten
    }

    fn after_step(&mut self, game: &GameState, player: usize, before_workers: usize) {
        let Some(config) = self.config else {
            return;
        };
        let after_workers = worker_count(game, player);
        if after_workers > 3 {
            self.telemetry.worker_cap_violations += 1;
        }
        if self.telemetry.train_attempts > self.telemetry.train_successes
            && self.active()
            && game.turn - 1 >= config.start
            && before_workers == 2
        {
            if after_workers == 3 {
                self.telemetry.train_successes += 1;
                self.telemetry.trained_turn = game.turn - 1;
                self.telemetry.committed = true;
            } else {
                self.telemetry.transaction_failures += 1;
            }
        }
    }
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

fn play(task: Task, policy: usize, spec: &PolicySpec) -> Row {
    let mut game = generate_official(task.map_seed);
    let mut ours = SecureOrchardBot::new();
    let mut option = CapitalOption::new(spec.option);
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Owner::Natural))
        .collect();
    let mut turns_until_end = 0i32;
    let mut action_hash = 14_695_981_039_346_656_037_u64;
    let mut prefix_captured = [false; 3];
    let mut prefix_action_hash = [0; 3];
    let mut prefix_state_hash = [0; 3];
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
        for (index, mark) in MARKS.iter().enumerate() {
            if game.turn == *mark {
                prefix_captured[index] = true;
                prefix_action_hash[index] = action_hash;
                prefix_state_hash[index] = canonical_state_hash(&game);
            }
        }
        let resident_commands = ours.commands(&resident_view(&game, task.seat));
        let ours_commands = option.rewrite(&game, task.seat, resident_commands);
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
        option.after_step(&game, task.seat, before_workers);

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
        policy,
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
            invalid_direct_commands: option.telemetry.option_command_failures,
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
            prefix_captured,
            prefix_action_hash,
            prefix_state_hash,
            option: option.telemetry,
        },
    }
}

fn write_rows(output: &str, rows: &[Row], policies: &[PolicySpec]) {
    let mut writer = BufWriter::new(File::create(output).expect("create D162a output"));
    writeln!(writer, "map_seed\tseat\topponent_index\topponent\tpolicy_index\tpolicy\toption_ms\toption_cc\toption_hp\toption_chop\toption_start\toption_horizon\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tprefix72_captured\tprefix72_action_hash\tprefix72_state_hash\tprefix104_captured\tprefix104_action_hash\tprefix104_state_hash\tprefix136_captured\tprefix136_action_hash\tprefix136_state_hash\tactivated\tactivation_turn\tdeadline\tactive_turns\tcommitted\taborted\toption_overrides\tprotected_commands\tmove_commands\tbank_commands\tharvest_commands\tmine_commands\ttrain_attempts\ttrain_successes\ttrained_turn\tinitial_bank_deficit\tclosest_bank_deficit\toption_command_failures\taffordability_violations\ttransaction_failures\tworker_cap_violations\thorizon_violations\trestart_violations").expect("write D162a header");
    for row in rows {
        let out = row.outcome;
        let telemetry = out.option;
        let option = policies[row.policy].option;
        let stats = option.map_or((-1, -1, -1, -1), |value| value.stats);
        let start = option.map_or(-1, |value| value.start);
        let horizon = option.map_or(0, |value| value.horizon);
        let values = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            row.task.opponent.to_string(),
            MacroOpponentMode::from_index(row.task.opponent).label().to_string(),
            row.policy.to_string(),
            policies[row.policy].label.clone(),
            stats.0.to_string(),
            stats.1.to_string(),
            stats.2.to_string(),
            stats.3.to_string(),
            start.to_string(),
            horizon.to_string(),
            usize::from(out.done).to_string(),
            out.turn.to_string(),
            out.own_score.to_string(),
            out.opponent_score.to_string(),
            (out.own_score - out.opponent_score).to_string(),
            format!("{:.9}", out.own_return),
            format!("{:.9}", out.opponent_return),
            format!("{:.9}", out.margin_return),
            format!("{:.9}", out.reward_identity_error),
            out.own_workers.to_string(),
            out.opponent_workers.to_string(),
            out.max_own_workers.to_string(),
            out.successful_trains.to_string(),
            "0".to_string(),
            "0".to_string(),
            out.invalid_direct_commands.to_string(),
            out.provenance_failures.to_string(),
            out.deposit_prediction_failures.to_string(),
            out.own_created_crops.to_string(),
            out.opponent_created_crops.to_string(),
            out.joint_created_crops.to_string(),
            out.ambiguous_created_crops.to_string(),
            out.own_owned_crop_harvest_units.to_string(),
            out.own_reinvested_crops.to_string(),
            out.action_hash.to_string(),
            out.state_hash.to_string(),
            usize::from(out.prefix_captured[0]).to_string(),
            out.prefix_action_hash[0].to_string(),
            out.prefix_state_hash[0].to_string(),
            usize::from(out.prefix_captured[1]).to_string(),
            out.prefix_action_hash[1].to_string(),
            out.prefix_state_hash[1].to_string(),
            usize::from(out.prefix_captured[2]).to_string(),
            out.prefix_action_hash[2].to_string(),
            out.prefix_state_hash[2].to_string(),
            usize::from(telemetry.activated).to_string(),
            telemetry.activation_turn.to_string(),
            telemetry.deadline.to_string(),
            telemetry.active_turns.to_string(),
            usize::from(telemetry.committed).to_string(),
            usize::from(telemetry.aborted).to_string(),
            telemetry.option_overrides.to_string(),
            telemetry.protected_commands.to_string(),
            telemetry.move_commands.to_string(),
            telemetry.bank_commands.to_string(),
            telemetry.harvest_commands.to_string(),
            telemetry.mine_commands.to_string(),
            telemetry.train_attempts.to_string(),
            telemetry.train_successes.to_string(),
            telemetry.trained_turn.to_string(),
            telemetry.initial_bank_deficit.to_string(),
            telemetry.closest_bank_deficit.to_string(),
            telemetry.option_command_failures.to_string(),
            telemetry.affordability_violations.to_string(),
            telemetry.transaction_failures.to_string(),
            telemetry.worker_cap_violations.to_string(),
            telemetry.horizon_violations.to_string(),
            telemetry.restart_violations.to_string(),
        ];
        writeln!(writer, "{}", values.join("\t")).expect("write D162a row");
    }
    writer.flush().expect("flush D162a output");
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
        5,
        "usage: d162_resident_native_capital_option START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(start_seed + maps as i64 <= 9_844_200 || start_seed >= 9_844_216);

    let policies = Arc::new(policy_catalog());
    let policy_count = policies.len();
    let work: Vec<_> = (start_seed..start_seed + maps as i64)
        .flat_map(|map_seed| {
            (0..2).flat_map(move |seat| {
                (0..MacroOpponentMode::ALL.len()).flat_map(move |opponent| {
                    (0..policy_count).map(move |policy| Work {
                        task: Task {
                            map_seed,
                            seat,
                            opponent,
                        },
                        policy,
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
            let policies = Arc::clone(&policies);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(item) = work.get(index).copied() else {
                    break;
                };
                let row = play(item.task, item.policy, &policies[item.policy]);
                rows.lock().expect("D162a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D162a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D162a rows")
        .into_inner()
        .expect("D162a rows lock");
    rows.sort_by_key(|row| (row.task, row.policy));
    write_rows(output, &rows, &policies);
    eprintln!(
        "saved {} D162a rows with {} workers in {:.3}s to {}",
        rows.len(),
        threads.min(work.len()),
        started.elapsed().as_secs_f64(),
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_catalog_has_control_and_twelve_options() {
        let catalog = policy_catalog();
        assert_eq!(catalog.len(), 13);
        assert_eq!(catalog[0].label, "resident");
        assert!(catalog[0].option.is_none());
        assert_eq!(catalog[1].label, "minimal_1101_t072_h032");
        assert_eq!(catalog[12].label, "balanced_2202_t136_h064");
    }

    #[test]
    fn referee_exact_third_worker_bills_are_frozen() {
        let mut game = generate_official(9_844_136);
        let minimal = OptionConfig {
            stats: (1, 1, 0, 1),
            start: 72,
            horizon: 32,
        };
        let balanced = OptionConfig {
            stats: (2, 2, 0, 2),
            start: 72,
            horizon: 32,
        };
        assert_eq!(bill(&game, minimal), [3, 3, 2, 0, 3, 0]);
        assert_eq!(bill(&game, balanced), [6, 6, 2, 0, 6, 0]);
        game.iron.clear();
        assert_eq!(bill(&game, minimal), [3, 3, 2, 0, 0, 0]);
    }

    #[test]
    fn disabled_option_is_exact_resident_control() {
        let task = Task {
            map_seed: 9_844_136,
            seat: 0,
            opponent: 0,
        };
        let control = PolicySpec {
            label: "resident".to_string(),
            option: None,
        };
        let disabled = PolicySpec {
            label: "disabled".to_string(),
            option: Some(OptionConfig {
                stats: (1, 1, 0, 1),
                start: 400,
                horizon: 32,
            }),
        };
        assert_eq!(play(task, 0, &control).outcome, play(task, 1, &disabled).outcome);
    }

    #[test]
    fn bounded_option_is_deterministic_and_never_exceeds_three_workers() {
        let task = Task {
            map_seed: 9_844_136,
            seat: 0,
            opponent: 0,
        };
        let spec = &policy_catalog()[1];
        let first = play(task, 1, spec);
        let second = play(task, 1, spec);
        assert_eq!(first, second);
        assert!(first.outcome.done);
        assert!(first.outcome.option.active_turns <= 32);
        assert!(first.outcome.max_own_workers <= 3);
        assert_eq!(first.outcome.option.option_command_failures, 0);
        assert_eq!(first.outcome.option.affordability_violations, 0);
        assert_eq!(first.outcome.option.transaction_failures, 0);
    }
}
