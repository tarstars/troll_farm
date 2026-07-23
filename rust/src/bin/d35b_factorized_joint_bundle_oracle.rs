//! Hindsight oracle for centralized, factorized persistent worker bundles.
//!
//! A clonable productive farm creates exact official-map roots.  At each root
//! the runner enumerates collision-safe unit jobs plus one optional train goal,
//! executes the whole bundle to completion, and returns to the warmed farm.

#[path = "yamo_orchard_live.rs"]
mod yamo;

#[path = "d35c_provenance_competitive_bundle_oracle_impl.rs"]
pub(crate) mod d35c_extension;

pub use yamo::{bot, game};

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{bfs_distances, has_stalled, step, training_cost, IRON, WOOD};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState, Unit as EngineUnit};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const CHECKPOINTS: [i32; 2] = [50, 100];
const MAX_TARGETS_PER_KIND: usize = 2;
const MAX_BASE_BUNDLES: usize = 96;
const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

fn productive_farm() -> GoldElite {
    GoldElite::configured(GoldEconomyConfig {
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
    })
}

enum Opponent {
    Resident(SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn opponent(index: usize) -> Opponent {
    match index {
        0 => Opponent::Resident(SecureOrchardBot::new()),
        1 => Opponent::Local(Box::new(GoldElite::adaptive())),
        2 => Opponent::Local(Box::new(CompactGold::new())),
        3 => Opponent::Local(Box::new(NorxondorNative::new(true))),
        4 => Opponent::Local(Box::new(LegendFieldProxyV2::configured(
            LegendFieldProxyV2Config {
                producer_spec: (2, 2, 1, 1),
                chopper_spec: (2, 2, 0, 2),
                late_chop: true,
            },
        ))),
        5 => Opponent::Local(Box::new(MyBot::new())),
        6 => Opponent::Local(Box::new(ScriptBoss::new())),
        7 => Opponent::Local(Box::new(SilverBoss::new())),
        _ => unreachable!(),
    }
}

const OPPONENTS: [&str; 8] = [
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
];

fn yamo_view(game: &GameState, player: usize) -> YamoState {
    let other = 1 - player;
    YamoState {
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
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
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

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

fn own_units(game: &GameState, player: usize) -> Vec<&EngineUnit> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    units
}

fn worker_count(game: &GameState, player: usize) -> usize {
    own_units(game, player).len()
}

fn ceil_div(value: i32, divisor: i32) -> i32 {
    if divisor <= 0 {
        10_000
    } else {
        (value + divisor - 1) / divisor
    }
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn shack_doors(game: &GameState, player: usize) -> Vec<Cell> {
    let (x, y) = game.shacks[player];
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        .into_iter()
        .filter(|target| game.walkable.contains(target))
        .collect()
}

fn nearest_door(game: &GameState, player: usize, from: Cell) -> Option<(Cell, i32)> {
    let distance = bfs_distances(&game.walkable, &[from]);
    shack_doors(game, player)
        .into_iter()
        .filter_map(|target| Some((target, *distance.get(&target)?)))
        .min_by_key(|(target, cells)| (*cells, *target))
}

fn replace_unit_action(
    game: &GameState,
    player: usize,
    commands: &mut Vec<String>,
    unit_id: i32,
    replacement: String,
) -> bool {
    let ids: Vec<_> = own_units(game, player)
        .into_iter()
        .map(|unit| unit.id)
        .collect();
    let mut slot = 0usize;
    for command in commands.iter_mut() {
        if command.starts_with("MSG ") || command.starts_with("TRAIN ") {
            continue;
        }
        if ids.get(slot).copied() == Some(unit_id) {
            let changed = *command != replacement;
            *command = replacement;
            return changed;
        }
        slot += 1;
    }
    commands.push(replacement);
    true
}

/// Validate the exact command emitted by the bundle executor against the
/// pre-turn state.  Dynamic simultaneous conflicts with the opponent are job
/// invalidations, not malformed direct commands, and are deliberately handled
/// after the referee step.
fn direct_command_is_valid(game: &GameState, player: usize, command: &str) -> bool {
    let parts: Vec<_> = command.split_whitespace().collect();
    let Some(verb) = parts.first().copied() else {
        return false;
    };
    let Some(unit_id) = parts.get(1).and_then(|value| value.parse::<i32>().ok()) else {
        return false;
    };
    let Some(unit) = game
        .units
        .iter()
        .find(|unit| unit.id == unit_id && unit.player as usize == player)
    else {
        return false;
    };
    match verb {
        "MOVE" => {
            if parts.len() != 4 {
                return false;
            }
            let Some(x) = parts[2].parse::<i32>().ok() else {
                return false;
            };
            let Some(y) = parts[3].parse::<i32>().ok() else {
                return false;
            };
            let target = (x, y);
            game.walkable.contains(&target)
                && bfs_distances(&game.walkable, &[unit.pos()]).contains_key(&target)
        }
        "HARVEST" => {
            parts.len() == 2
                && unit.hp > 0
                && unit.free() > 0
                && game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == unit.pos() && plant.health > 0 && plant.fruits > 0)
        }
        "PLANT" => {
            let Some(kind) = parts.get(2).and_then(|name| fruit_index(name)) else {
                return false;
            };
            parts.len() == 3
                && unit.carry[kind] > 0
                && game.walkable.contains(&unit.pos())
                && !game.plants.iter().any(|plant| plant.pos() == unit.pos())
        }
        "CHOP" => {
            parts.len() == 2
                && unit.chop > 0
                && unit.free() > 0
                && game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == unit.pos() && plant.health > 0)
        }
        "MINE" => {
            parts.len() == 2
                && unit.chop > 0
                && unit.free() > 0
                && game.iron.iter().any(|ore| manhattan(*ore, unit.pos()) == 1)
        }
        "DROP" => {
            parts.len() == 2 && unit.total() > 0 && manhattan(unit.pos(), game.shacks[player]) <= 1
        }
        _ => false,
    }
}

fn fruit_index(name: &str) -> Option<usize> {
    FRUIT_NAMES.iter().position(|known| *known == name)
}

fn player_favored_plant_cell(game: &GameState, player: usize, from: Cell) -> Option<Cell> {
    let from_distance = bfs_distances(&game.walkable, &[from]);
    let own_distance = bfs_distances(&game.walkable, &shack_doors(game, player));
    let other_distance = bfs_distances(&game.walkable, &shack_doors(game, 1 - player));
    game.walkable
        .iter()
        .filter(|target| manhattan(**target, game.shacks[player]) <= 4)
        .filter(|target| !game.plants.iter().any(|plant| plant.pos() == **target))
        .filter(|target| !game.units.iter().any(|unit| unit.pos() == **target))
        .filter(|target| from_distance.contains_key(*target))
        .filter(|target| {
            own_distance.get(*target).copied().unwrap_or(10_000)
                < other_distance.get(*target).copied().unwrap_or(10_000)
        })
        .min_by_key(|target| {
            let wet = game
                .water
                .iter()
                .any(|water| manhattan(*water, **target) == 1);
            (from_distance[*target], usize::from(!wet), **target)
        })
        .copied()
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum JobKind {
    Keep,
    Bank,
    FellBank,
    HarvestBank,
    Renew,
    MineBank,
}

impl JobKind {
    fn label(self) -> &'static str {
        match self {
            Self::Keep => "keep",
            Self::Bank => "bank",
            Self::FellBank => "fell_bank",
            Self::HarvestBank => "harvest_bank",
            Self::Renew => "renew",
            Self::MineBank => "mine_bank",
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct JobSpec {
    kind: JobKind,
    unit_id: i32,
    target: Option<Cell>,
    plant_cell: Option<Cell>,
    fruit_kind: Option<usize>,
    predicted_eta: i32,
    predicted_reward: i32,
}

impl JobSpec {
    fn key(&self) -> String {
        format!(
            "{}:{}:{}:{}:{}",
            self.kind.label(),
            self.unit_id,
            self.target.map_or_else(
                || "-".to_string(),
                |value| format!("{},{}", value.0, value.1)
            ),
            self.plant_cell.map_or_else(
                || "-".to_string(),
                |value| format!("{},{}", value.0, value.1)
            ),
            self.fruit_kind
                .map_or_else(|| "-".to_string(), |value| value.to_string()),
        )
    }

    fn acquisition_target(&self) -> Option<Cell> {
        match self.kind {
            JobKind::FellBank | JobKind::HarvestBank | JobKind::Renew | JobKind::MineBank => {
                self.target
            }
            JobKind::Keep | JobKind::Bank => None,
        }
    }
}

fn jobs_for_unit(game: &GameState, player: usize, unit: &EngineUnit) -> Vec<JobSpec> {
    let from_unit = bfs_distances(&game.walkable, &[unit.pos()]);
    let mut jobs = vec![JobSpec {
        kind: JobKind::Keep,
        unit_id: unit.id,
        target: None,
        plant_cell: None,
        fruit_kind: None,
        predicted_eta: 0,
        predicted_reward: 0,
    }];
    if unit.total() > 0 {
        if let Some((_, distance)) = nearest_door(game, player, unit.pos()) {
            jobs.push(JobSpec {
                kind: JobKind::Bank,
                unit_id: unit.id,
                target: None,
                plant_cell: None,
                fruit_kind: None,
                predicted_eta: ceil_div(distance, unit.ms) + 1,
                predicted_reward: unit.carry[..4].iter().sum::<i32>() + 4 * unit.carry[WOOD],
            });
        }
    }
    if unit.chop > 0 && unit.free() > 0 {
        let mut fell: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let chop = ceil_div(plant.health, unit.chop);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = 4 * plant.size.min(unit.free());
                Some((travel + chop + bank, -reward, plant.pos(), reward))
            })
            .collect();
        fell.sort_unstable();
        jobs.extend(
            fell.into_iter()
                .take(MAX_TARGETS_PER_KIND)
                .map(|(eta, _, target, reward)| JobSpec {
                    kind: JobKind::FellBank,
                    unit_id: unit.id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: None,
                    predicted_eta: eta,
                    predicted_reward: reward,
                }),
        );
    }
    if unit.hp > 0 && unit.free() > 0 {
        let mut harvest: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0 && plant.fruits > 0)
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = plant.fruits.min(unit.hp).min(unit.free());
                Some((
                    travel + 1 + bank,
                    -reward,
                    plant.pos(),
                    reward,
                    fruit_index(&plant.plant_type)?,
                ))
            })
            .collect();
        harvest.sort_unstable();
        jobs.extend(harvest.iter().take(MAX_TARGETS_PER_KIND).map(
            |(eta, _, target, reward, kind)| JobSpec {
                kind: JobKind::HarvestBank,
                unit_id: unit.id,
                target: Some(*target),
                plant_cell: None,
                fruit_kind: Some(*kind),
                predicted_eta: *eta,
                predicted_reward: *reward,
            },
        ));
        jobs.extend(harvest.into_iter().take(MAX_TARGETS_PER_KIND).filter_map(
            |(harvest_eta, _, target, reward, kind)| {
                let plant_cell = player_favored_plant_cell(game, player, target)?;
                let travel_to_plant = bfs_distances(&game.walkable, &[target])
                    .get(&plant_cell)
                    .copied()?;
                let (_, bank_distance) = nearest_door(game, player, plant_cell)?;
                Some(JobSpec {
                    kind: JobKind::Renew,
                    unit_id: unit.id,
                    target: Some(target),
                    plant_cell: Some(plant_cell),
                    fruit_kind: Some(kind),
                    predicted_eta: harvest_eta
                        + ceil_div(travel_to_plant, unit.ms)
                        + 1
                        + ceil_div(bank_distance, unit.ms)
                        + 1,
                    predicted_reward: reward + 16,
                })
            },
        ));
    }
    if unit.chop > 0 && unit.free() > 0 {
        let mut mine: Vec<_> = game
            .iron
            .iter()
            .flat_map(|ore| {
                let (x, y) = *ore;
                [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
            })
            .filter(|target| game.walkable.contains(target) && from_unit.contains_key(target))
            .filter_map(|target| {
                let travel = ceil_div(from_unit[&target], unit.ms);
                let (_, bank_distance) = nearest_door(game, player, target)?;
                Some((travel + 1 + ceil_div(bank_distance, unit.ms) + 1, target))
            })
            .collect();
        mine.sort_unstable();
        mine.dedup();
        jobs.extend(
            mine.into_iter()
                .take(MAX_TARGETS_PER_KIND)
                .map(|(eta, target)| JobSpec {
                    kind: JobKind::MineBank,
                    unit_id: unit.id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: None,
                    predicted_eta: eta,
                    predicted_reward: 1,
                }),
        );
    }
    jobs.retain(|job| game.turn + job.predicted_eta <= TOTAL_TURNS);
    jobs.sort_by_key(|job| {
        (
            job.kind,
            job.predicted_eta,
            -job.predicted_reward,
            job.target,
            job.plant_cell,
        )
    });
    jobs.dedup_by_key(|job| (job.kind, job.target, job.plant_cell, job.fruit_kind));
    jobs
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum TrainGoal {
    None,
    Producer,
    Chopper,
}

impl TrainGoal {
    fn label(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Producer => "producer_2211",
            Self::Chopper => "chopper_2202",
        }
    }

    fn spec(self) -> Option<(i32, i32, i32, i32)> {
        match self {
            Self::None => None,
            Self::Producer => Some((2, 2, 1, 1)),
            Self::Chopper => Some((2, 2, 0, 2)),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct JointPlan {
    jobs: Vec<JobSpec>,
    train_goal: TrainGoal,
    key: String,
    rate_score: i32,
    predicted_eta: i32,
    predicted_reward: i32,
}

fn jobs_collide(left: &JobSpec, right: &JobSpec) -> bool {
    (left.acquisition_target().is_some() && left.acquisition_target() == right.acquisition_target())
        || (left.plant_cell.is_some() && left.plant_cell == right.plant_cell)
}

fn joint_plans(game: &GameState, player: usize) -> Vec<JointPlan> {
    let units = own_units(game, player);
    if units.len() != 2 {
        return Vec::new();
    }
    let first = jobs_for_unit(game, player, units[0]);
    let second = jobs_for_unit(game, player, units[1]);
    let mut bases = Vec::new();
    for left in &first {
        for right in &second {
            if jobs_collide(left, right) {
                continue;
            }
            let jobs = vec![left.clone(), right.clone()];
            let predicted_reward: i32 = jobs.iter().map(|job| job.predicted_reward).sum();
            let predicted_eta = jobs.iter().map(|job| job.predicted_eta).max().unwrap_or(0);
            let rate_score: i32 = jobs
                .iter()
                .map(|job| 1000 * job.predicted_reward / job.predicted_eta.max(1))
                .sum();
            let key = jobs.iter().map(JobSpec::key).collect::<Vec<_>>().join("+");
            bases.push((rate_score, predicted_eta, predicted_reward, key, jobs));
        }
    }
    bases.sort_by(|left, right| (-left.0, left.1, &left.3).cmp(&(-right.0, right.1, &right.3)));
    bases.dedup_by(|left, right| left.3 == right.3);
    bases.truncate(MAX_BASE_BUNDLES);

    // Roots are deliberately restricted to exactly two workers, so every
    // factorized unit bundle is crossed with the same three global choices.
    let goals = [TrainGoal::None, TrainGoal::Producer, TrainGoal::Chopper];
    let mut plans = Vec::new();
    for (rate_score, predicted_eta, predicted_reward, key, jobs) in bases {
        for goal in goals {
            if jobs.iter().all(|job| job.kind == JobKind::Keep) && goal == TrainGoal::None {
                continue;
            }
            plans.push(JointPlan {
                jobs: jobs.clone(),
                train_goal: goal,
                key: format!("{}|train={}", key, goal.label()),
                rate_score,
                predicted_eta,
                predicted_reward,
            });
        }
    }
    plans
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum JobPhase {
    Acquire,
    Plant,
    Bank,
}

struct ActiveJob {
    spec: JobSpec,
    phase: JobPhase,
    initial_carry: [i32; 6],
    plant_issued: bool,
}

enum JobCommand {
    Command(String),
    Complete,
    Invalid(&'static str),
}

impl ActiveJob {
    fn new(spec: JobSpec, game: &GameState) -> Self {
        let unit = game
            .units
            .iter()
            .find(|unit| unit.id == spec.unit_id)
            .expect("root job unit");
        let phase = match spec.kind {
            JobKind::Bank => JobPhase::Bank,
            JobKind::Keep => unreachable!(),
            _ => JobPhase::Acquire,
        };
        Self {
            spec,
            phase,
            initial_carry: unit.carry,
            plant_issued: false,
        }
    }

    fn acquired(&self, unit: &EngineUnit) -> bool {
        match self.spec.kind {
            JobKind::FellBank => unit.carry[WOOD] > self.initial_carry[WOOD],
            JobKind::HarvestBank | JobKind::Renew => {
                let kind = self.spec.fruit_kind.expect("fruit job kind");
                unit.carry[kind] > self.initial_carry[kind]
            }
            JobKind::MineBank => unit.carry[IRON] > self.initial_carry[IRON],
            JobKind::Bank => true,
            JobKind::Keep => false,
        }
    }

    fn bank_command(&self, game: &GameState, player: usize, unit: &EngineUnit) -> JobCommand {
        if unit.total() == 0 {
            return JobCommand::Complete;
        }
        let Some((door, _)) = nearest_door(game, player, unit.pos()) else {
            return JobCommand::Invalid("bank_unreachable");
        };
        JobCommand::Command(if unit.pos() == door {
            format!("DROP {}", unit.id)
        } else {
            format!("MOVE {} {} {}", unit.id, door.0, door.1)
        })
    }

    fn command(&mut self, game: &GameState, player: usize) -> JobCommand {
        let Some(unit) = game.units.iter().find(|unit| unit.id == self.spec.unit_id) else {
            return JobCommand::Invalid("unit_missing");
        };
        if self.phase == JobPhase::Acquire && self.acquired(unit) {
            self.phase = if self.spec.kind == JobKind::Renew {
                JobPhase::Plant
            } else {
                JobPhase::Bank
            };
        }
        if self.phase == JobPhase::Plant {
            let target = self.spec.plant_cell.expect("renew plant cell");
            let kind = self.spec.fruit_kind.expect("renew fruit kind");
            if self.plant_issued {
                if game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == target && plant.plant_type == FRUIT_NAMES[kind])
                {
                    self.phase = JobPhase::Bank;
                } else {
                    return JobCommand::Invalid("plant_failed");
                }
            } else if game.plants.iter().any(|plant| plant.pos() == target) {
                return JobCommand::Invalid("plant_cell_occupied");
            } else if unit.carry[kind] <= 0 {
                return JobCommand::Invalid("seed_missing");
            } else if unit.pos() == target {
                self.plant_issued = true;
                return JobCommand::Command(format!("PLANT {} {}", unit.id, FRUIT_NAMES[kind]));
            } else {
                return JobCommand::Command(format!("MOVE {} {} {}", unit.id, target.0, target.1));
            }
        }
        if self.phase == JobPhase::Bank {
            return self.bank_command(game, player, unit);
        }

        let target = self.spec.target.expect("acquisition target");
        if unit.pos() != target {
            if !bfs_distances(&game.walkable, &[unit.pos()]).contains_key(&target) {
                return JobCommand::Invalid("target_unreachable");
            }
            return JobCommand::Command(format!("MOVE {} {} {}", unit.id, target.0, target.1));
        }
        match self.spec.kind {
            JobKind::FellBank => {
                let valid = game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == target && plant.health > 0);
                if valid && unit.chop > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("CHOP {}", unit.id))
                } else {
                    JobCommand::Invalid("fell_target_invalid")
                }
            }
            JobKind::HarvestBank | JobKind::Renew => {
                let valid = game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == target && plant.health > 0 && plant.fruits > 0);
                if valid && unit.hp > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("HARVEST {}", unit.id))
                } else {
                    JobCommand::Invalid("fruit_target_invalid")
                }
            }
            JobKind::MineBank => {
                let adjacent_iron = game.iron.iter().any(|ore| manhattan(*ore, unit.pos()) == 1);
                if adjacent_iron && unit.chop > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("MINE {}", unit.id))
                } else {
                    JobCommand::Invalid("mine_target_invalid")
                }
            }
            JobKind::Keep | JobKind::Bank => unreachable!(),
        }
    }
}

fn affordable_train(game: &GameState, player: usize, goal: TrainGoal) -> bool {
    let Some(spec) = goal.spec() else {
        return false;
    };
    let n = worker_count(game, player) as i32;
    if n >= 3 || game.turn > TOTAL_TURNS - 30 {
        return false;
    }
    let cost = training_cost(n, spec);
    let inventory = game.inventories[player];
    inventory[0] >= cost[0]
        && inventory[1] >= cost[1]
        && inventory[2] >= cost[2]
        && (game.iron.is_empty() || inventory[IRON] >= cost[IRON])
        && !game
            .units
            .iter()
            .any(|unit| unit.player as usize == player && unit.pos() == game.shacks[player])
}

fn train_command(goal: TrainGoal) -> String {
    let (ms, cc, hp, chop) = goal.spec().expect("nonempty train goal");
    format!("TRAIN {ms} {cc} {hp} {chop}")
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    own_wood: i32,
    opponent_wood: i32,
    own_workers: usize,
    opponent_workers: usize,
    terminal_turn: i32,
}

impl Outcome {
    fn from_game(game: &GameState, player: usize) -> Self {
        Self {
            own_score: game.scores[player],
            opponent_score: game.scores[1 - player],
            own_wood: game.inventories[player][WOOD],
            opponent_wood: game.inventories[1 - player][WOOD],
            own_workers: worker_count(game, player),
            opponent_workers: worker_count(game, 1 - player),
            terminal_turn: game.turn,
        }
    }

    fn margin(self) -> i32 {
        self.own_score - self.opponent_score
    }
}

#[derive(Clone)]
struct Root {
    checkpoint: i32,
    game: GameState,
    farm: GoldElite,
    opponent_history: Vec<GameState>,
    stall_counter: i32,
    plans: Vec<JointPlan>,
    has_renew: bool,
    has_fell: bool,
    has_mine: bool,
    has_train_goal: bool,
}

struct Simulation {
    outcome: Outcome,
    statuses: String,
    overridden_actions: usize,
    invalid_direct_commands: usize,
    train_success: bool,
    max_own_workers: usize,
    bundle_end_turn: i32,
}

fn warmed_opponent(root: &Root, index: usize, player: usize) -> Opponent {
    let mut policy = opponent(index);
    for historical in &root.opponent_history {
        let _ = policy.commands(historical, 1 - player);
    }
    policy
}

fn simulate(root: &Root, player: usize, model: usize, plan: Option<&JointPlan>) -> Simulation {
    let mut game = root.game.clone();
    let farm = root.farm.clone();
    let mut opponent = warmed_opponent(root, model, player);
    let mut stall_counter = root.stall_counter;
    let mut active = BTreeMap::new();
    let mut status = BTreeMap::new();
    let mut train_pending = TrainGoal::None;
    if let Some(plan) = plan {
        train_pending = plan.train_goal;
        for spec in &plan.jobs {
            if spec.kind == JobKind::Keep {
                status.insert(spec.unit_id, "keep");
            } else {
                active.insert(spec.unit_id, ActiveJob::new(spec.clone(), &game));
                status.insert(spec.unit_id, "active");
            }
        }
    }
    let mut overridden_actions = 0usize;
    let mut invalid_direct_commands = 0usize;
    let initial_workers = worker_count(&game, player);
    let mut train_success = false;
    let mut max_own_workers = initial_workers;
    let mut bundle_end_turn = if plan.is_none() { root.game.turn } else { -1 };

    while game.turn <= TOTAL_TURNS {
        let mut ours = farm.decide(&game, player);
        let ids: Vec<_> = active.keys().copied().collect();
        let mut job_invalidated = false;
        for id in ids {
            let result = active
                .get_mut(&id)
                .expect("active job")
                .command(&game, player);
            match result {
                JobCommand::Command(command) => {
                    if !direct_command_is_valid(&game, player, &command) {
                        invalid_direct_commands += 1;
                        active.remove(&id);
                        status.insert(id, "direct_command_invalid");
                        job_invalidated = true;
                        continue;
                    }
                    overridden_actions +=
                        usize::from(replace_unit_action(&game, player, &mut ours, id, command));
                }
                JobCommand::Complete => {
                    active.remove(&id);
                    status.insert(id, "completed");
                }
                JobCommand::Invalid(reason) => {
                    active.remove(&id);
                    status.insert(id, reason);
                    job_invalidated = true;
                }
            }
        }

        if job_invalidated {
            train_pending = TrainGoal::None;
        }
        let mut train_issued = false;
        if train_pending != TrainGoal::None && affordable_train(&game, player, train_pending) {
            ours.retain(|command| !command.starts_with("TRAIN "));
            ours.push(train_command(train_pending));
            train_issued = true;
        } else if active.is_empty() && train_pending != TrainGoal::None {
            train_pending = TrainGoal::None;
        }
        if active.is_empty() && train_pending == TrainGoal::None && bundle_end_turn < 0 {
            bundle_end_turn = game.turn;
        }

        let theirs = opponent.commands(&game, 1 - player);
        apply_commands(&mut game, player, &ours, &theirs);
        max_own_workers = max_own_workers.max(worker_count(&game, player));
        if train_issued && worker_count(&game, player) > initial_workers {
            train_success = true;
            train_pending = TrainGoal::None;
            if active.is_empty() && bundle_end_turn < 0 {
                bundle_end_turn = game.turn;
            }
        }
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    if bundle_end_turn < 0 {
        bundle_end_turn = game.turn;
    }
    let statuses = status
        .iter()
        .map(|(id, value)| format!("{id}:{value}"))
        .collect::<Vec<_>>()
        .join(",");
    Simulation {
        outcome: Outcome::from_game(&game, player),
        statuses,
        overridden_actions,
        invalid_direct_commands,
        train_success,
        max_own_workers,
        bundle_end_turn,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: i64,
    seat: usize,
    opponent_index: usize,
}

fn resident_reference(task: Task) -> Outcome {
    let mut game = generate_official(task.seed);
    let mut resident = SecureOrchardBot::new();
    let mut opponent = opponent(task.opponent_index);
    let mut stall_counter = 0;
    while game.turn <= TOTAL_TURNS {
        let ours = resident.commands(&yamo_view(&game, task.seat));
        let theirs = opponent.commands(&game, 1 - task.seat);
        apply_commands(&mut game, task.seat, &ours, &theirs);
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    Outcome::from_game(&game, task.seat)
}

fn capture_roots(task: Task) -> (Vec<Root>, Outcome) {
    let mut game = generate_official(task.seed);
    let farm = productive_farm();
    let mut opponent = opponent(task.opponent_index);
    let mut stall_counter = 0;
    let mut opponent_history = Vec::new();
    let mut captured = [false; CHECKPOINTS.len()];
    let mut roots = Vec::new();
    while game.turn <= TOTAL_TURNS {
        let farm_before = farm.clone();
        let ours = farm.decide(&game, task.seat);
        for (index, checkpoint) in CHECKPOINTS.iter().copied().enumerate() {
            if !captured[index] && game.turn >= checkpoint && worker_count(&game, task.seat) == 2 {
                captured[index] = true;
                let plans = joint_plans(&game, task.seat);
                let has_renew = plans
                    .iter()
                    .any(|plan| plan.jobs.iter().any(|job| job.kind == JobKind::Renew));
                let has_fell = plans
                    .iter()
                    .any(|plan| plan.jobs.iter().any(|job| job.kind == JobKind::FellBank));
                let has_mine = plans
                    .iter()
                    .any(|plan| plan.jobs.iter().any(|job| job.kind == JobKind::MineBank));
                let has_train_goal = plans.iter().any(|plan| plan.train_goal != TrainGoal::None);
                roots.push(Root {
                    checkpoint,
                    game: game.clone(),
                    farm: farm_before.clone(),
                    opponent_history: opponent_history.clone(),
                    stall_counter,
                    plans,
                    has_renew,
                    has_fell,
                    has_mine,
                    has_train_goal,
                });
            }
        }
        let theirs = opponent.commands(&game, 1 - task.seat);
        opponent_history.push(game.clone());
        apply_commands(&mut game, task.seat, &ours, &theirs);
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    (roots, Outcome::from_game(&game, task.seat))
}

struct Row {
    task: Task,
    checkpoint: i32,
    root_turn: i32,
    option: usize,
    plan: Option<JointPlan>,
    simulation: Simulation,
    control: Outcome,
    baseline: Outcome,
    resident: Outcome,
    root_plan_count: usize,
    has_renew: bool,
    has_fell: bool,
    has_mine: bool,
    has_train_goal: bool,
}

struct ScenarioManifest {
    task: Task,
    baseline: Outcome,
    resident: Outcome,
    roots: Vec<(i32, i32)>,
}

fn scenario_manifest(task: Task) -> ScenarioManifest {
    let resident = resident_reference(task);
    let (roots, baseline) = capture_roots(task);
    ScenarioManifest {
        task,
        baseline,
        resident,
        roots: roots
            .iter()
            .map(|root| (root.checkpoint, root.game.turn))
            .collect(),
    }
}

fn write_scenario_manifest(tasks: Arc<Vec<Task>>, output: &str, threads: usize) {
    let next = Arc::new(AtomicUsize::new(0));
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            thread::spawn(move || {
                let mut manifests = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    manifests.push(scenario_manifest(tasks[index]));
                }
                manifests
            })
        })
        .collect();
    let mut manifests: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D35b manifest worker"))
        .collect();
    manifests.sort_by_key(|entry| (entry.task.seed, entry.task.seat, entry.task.opponent_index));
    let path = format!("{output}.scenarios.tsv");
    let mut writer = BufWriter::new(File::create(&path).expect("create D35b manifest"));
    writeln!(writer, "seed\tseat\topponent\troot_count\tcaptured_checkpoints\troot_turns\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_workers\tfarm_opponent_workers\tfarm_terminal_turn\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn").expect("write D35b manifest header");
    for entry in &manifests {
        let checkpoints = entry
            .roots
            .iter()
            .map(|(checkpoint, _)| checkpoint.to_string())
            .collect::<Vec<_>>()
            .join(",");
        let root_turns = entry
            .roots
            .iter()
            .map(|(_, turn)| turn.to_string())
            .collect::<Vec<_>>()
            .join(",");
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            entry.task.seed,
            entry.task.seat,
            OPPONENTS[entry.task.opponent_index],
            entry.roots.len(),
            checkpoints,
            root_turns,
            entry.baseline.own_score,
            entry.baseline.opponent_score,
            entry.baseline.margin(),
            entry.baseline.own_workers,
            entry.baseline.opponent_workers,
            entry.baseline.terminal_turn,
            entry.resident.own_score,
            entry.resident.opponent_score,
            entry.resident.margin(),
            entry.resident.own_workers,
            entry.resident.opponent_workers,
            entry.resident.terminal_turn,
        )
        .expect("write D35b manifest row");
    }
    writer.flush().expect("flush D35b manifest");
    eprintln!("saved {} scenario rows to {path}", manifests.len());
}

fn play_task(task: Task) -> Vec<Row> {
    let resident = resident_reference(task);
    let (roots, baseline) = capture_roots(task);
    let mut rows = Vec::new();
    for root in roots {
        let control_simulation = simulate(&root, task.seat, task.opponent_index, None);
        let control = control_simulation.outcome;
        rows.push(Row {
            task,
            checkpoint: root.checkpoint,
            root_turn: root.game.turn,
            option: 0,
            plan: None,
            simulation: control_simulation,
            control,
            baseline,
            resident,
            root_plan_count: root.plans.len(),
            has_renew: root.has_renew,
            has_fell: root.has_fell,
            has_mine: root.has_mine,
            has_train_goal: root.has_train_goal,
        });
        for (index, plan) in root.plans.iter().cloned().enumerate() {
            rows.push(Row {
                task,
                checkpoint: root.checkpoint,
                root_turn: root.game.turn,
                option: index + 1,
                plan: Some(plan.clone()),
                simulation: simulate(&root, task.seat, task.opponent_index, Some(&plan)),
                control,
                baseline,
                resident,
                root_plan_count: root.plans.len(),
                has_renew: root.has_renew,
                has_fell: root.has_fell,
                has_mine: root.has_mine,
                has_train_goal: root.has_train_goal,
            });
        }
    }
    rows
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args.get(1).map_or(9_200_000, |value| {
        value.parse::<i64>().expect("signed seed start")
    });
    let seed_count = args
        .get(2)
        .map_or(1, |value| value.parse::<usize>().expect("seed count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d35b-factorized-joint-bundle-oracle.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(24, |value| value.parse::<usize>().expect("thread count"))
        .clamp(1, 64);
    let manifest_only = args.get(5).map_or(false, |value| value == "manifest-only");
    assert!(seed_count > 0);

    let tasks: Vec<_> = (0..seed_count)
        .flat_map(|offset| {
            (0..2).flat_map(move |seat| {
                (0..OPPONENTS.len()).map(move |opponent_index| Task {
                    seed: seed_start + offset as i64,
                    seat,
                    opponent_index,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    if manifest_only {
        write_scenario_manifest(Arc::clone(&tasks), &output, threads);
        return;
    }
    let next = Arc::new(AtomicUsize::new(0));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            thread::spawn(move || {
                let mut rows = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    rows.extend(play_task(tasks[index]));
                }
                rows
            })
        })
        .collect();
    let mut rows: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D35b worker thread"))
        .collect();
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.seat,
            row.task.opponent_index,
            row.checkpoint,
            row.option,
        )
    });

    let mut writer = BufWriter::new(File::create(&output).expect("create D35b output"));
    writeln!(writer, "seed\tseat\topponent\tcheckpoint\troot_turn\toption\tplan_key\trole_tuple\ttrain_goal\tpredicted_eta\tpredicted_reward\trate_score\tstatuses\toverridden_actions\tinvalid_direct_commands\ttrain_success\tmax_own_workers\tbundle_end_turn\troot_plan_count\thas_renew\thas_fell\thas_mine\thas_train_goal\town_score\topponent_score\tmargin\town_wood\topponent_wood\town_workers\topponent_workers\tterminal_turn\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_wood\tfarm_opponent_wood\tfarm_terminal_turn\tmargin_delta_farm\town_score_delta_farm\topponent_score_delta_farm\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tmargin_delta_resident\town_score_delta_resident\topponent_score_delta_resident\tcontrol_identity_match").expect("write D35b header");
    for row in &rows {
        let (key, roles, train, eta, reward, rate) = row.plan.as_ref().map_or(
            (
                "control".to_string(),
                "control".to_string(),
                "none".to_string(),
                0,
                0,
                0,
            ),
            |plan| {
                (
                    plan.key.clone(),
                    plan.jobs
                        .iter()
                        .map(|job| job.kind.label())
                        .collect::<Vec<_>>()
                        .join("+"),
                    plan.train_goal.label().to_string(),
                    plan.predicted_eta,
                    plan.predicted_reward,
                    plan.rate_score,
                )
            },
        );
        let terminal = row.simulation.outcome;
        let fields = vec![
            row.task.seed.to_string(),
            row.task.seat.to_string(),
            OPPONENTS[row.task.opponent_index].to_string(),
            row.checkpoint.to_string(),
            row.root_turn.to_string(),
            row.option.to_string(),
            key,
            roles,
            train,
            eta.to_string(),
            reward.to_string(),
            rate.to_string(),
            row.simulation.statuses.clone(),
            row.simulation.overridden_actions.to_string(),
            row.simulation.invalid_direct_commands.to_string(),
            usize::from(row.simulation.train_success).to_string(),
            row.simulation.max_own_workers.to_string(),
            row.simulation.bundle_end_turn.to_string(),
            row.root_plan_count.to_string(),
            usize::from(row.has_renew).to_string(),
            usize::from(row.has_fell).to_string(),
            usize::from(row.has_mine).to_string(),
            usize::from(row.has_train_goal).to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            terminal.margin().to_string(),
            terminal.own_wood.to_string(),
            terminal.opponent_wood.to_string(),
            terminal.own_workers.to_string(),
            terminal.opponent_workers.to_string(),
            terminal.terminal_turn.to_string(),
            row.control.own_score.to_string(),
            row.control.opponent_score.to_string(),
            row.control.margin().to_string(),
            row.control.own_wood.to_string(),
            row.control.opponent_wood.to_string(),
            row.control.terminal_turn.to_string(),
            (terminal.margin() - row.control.margin()).to_string(),
            (terminal.own_score - row.control.own_score).to_string(),
            (terminal.opponent_score - row.control.opponent_score).to_string(),
            row.resident.own_score.to_string(),
            row.resident.opponent_score.to_string(),
            row.resident.margin().to_string(),
            row.resident.own_wood.to_string(),
            row.resident.opponent_wood.to_string(),
            (terminal.margin() - row.resident.margin()).to_string(),
            (terminal.own_score - row.resident.own_score).to_string(),
            (terminal.opponent_score - row.resident.opponent_score).to_string(),
            usize::from(row.control == row.baseline).to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D35b row");
    }
    writer.flush().expect("flush D35b output");
    write_scenario_manifest(Arc::clone(&tasks), &output, threads);
    eprintln!(
        "saved {} rows from {} tasks in {:.3}s to {output}",
        rows.len(),
        tasks.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn official_root_jobs_and_joint_plans_are_deterministic() {
        let mut game = generate_official(9_200_000);
        let farm = productive_farm();
        let opponent = CompactGold::new();
        let mut stall_counter = 0;
        while game.turn < 50 {
            let ours = farm.decide(&game, 0);
            let theirs = opponent.decide(&game, 1);
            step(&mut game, &ours, &theirs);
            assert!(!has_stalled(&game, &mut stall_counter));
        }
        assert_eq!(worker_count(&game, 0), 2);
        let first = joint_plans(&game, 0);
        let second = joint_plans(&game, 0);
        assert_eq!(first, second);
        assert!(!first.is_empty());
        assert!(first.len() <= MAX_BASE_BUNDLES * 3);
    }

    #[test]
    fn collisions_reject_shared_acquisition_or_plant_cells() {
        let base = JobSpec {
            kind: JobKind::Renew,
            unit_id: 1,
            target: Some((2, 2)),
            plant_cell: Some((3, 3)),
            fruit_kind: Some(3),
            predicted_eta: 5,
            predicted_reward: 16,
        };
        let mut other = base.clone();
        other.unit_id = 2;
        assert!(jobs_collide(&base, &other));
        other.target = Some((4, 4));
        assert!(jobs_collide(&base, &other));
        other.plant_cell = Some((5, 5));
        assert!(!jobs_collide(&base, &other));
    }

    #[test]
    fn control_branches_reproduce_uninterrupted_farm() {
        let rows = play_task(Task {
            seed: 9_200_000,
            seat: 0,
            opponent_index: 2,
        });
        assert!(!rows.is_empty());
        assert!(rows.iter().all(|row| row.control == row.baseline));
        assert!(rows
            .iter()
            .all(|row| row.simulation.invalid_direct_commands == 0));
        assert!(rows.iter().all(|row| row.simulation.max_own_workers <= 3));
        assert!(rows.iter().filter(|row| row.option == 0).all(|row| {
            row.simulation.overridden_actions == 0 && !row.simulation.train_success
        }));
    }

    #[test]
    fn train_goals_are_fixed_and_distinct() {
        assert_eq!(TrainGoal::Producer.spec(), Some((2, 2, 1, 1)));
        assert_eq!(TrainGoal::Chopper.spec(), Some((2, 2, 0, 2)));
        assert_eq!(TrainGoal::None.spec(), None);
    }
}
