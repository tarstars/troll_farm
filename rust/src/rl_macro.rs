//! Complete asynchronous persistent-job environment for D37.
//!
//! The learned side owns every command.  A policy chooses a persistent TRAIN
//! goal and one role/target for each currently free worker; deterministic
//! executors advance the exact official referee until the next job boundary.

use std::collections::{BTreeMap, BTreeSet};

use rayon::prelude::*;

use crate::game::engine::{bfs_distances, has_stalled, step, training_cost, IRON, WOOD};
use crate::game::official_mapgen::generate_official;
use crate::game::state::{Cell, GameState, Unit};
use crate::resident_policy::bot::moisan::SecureOrchardBot;
use crate::resident_policy::bot::Bot as ResidentBot;
use crate::resident_policy::game::{
    GameState as ResidentState, Plant as ResidentPlant, PlantKind, Stats as ResidentStats,
    Unit as ResidentUnit,
};
use crate::strategies::compact_gold::CompactGold;
use crate::strategies::gold_elite::GoldElite;
use crate::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use crate::strategies::mybot::MyBot;
use crate::strategies::norxondor_native::NorxondorNative;
use crate::strategies::script_boss::ScriptBoss;
use crate::strategies::silver_boss::SilverBoss;
use crate::strategies::Strategy;

pub const MACRO_HEIGHT: usize = 11;
pub const MACRO_WIDTH: usize = 22;
pub const MACRO_CELLS: usize = MACRO_HEIGHT * MACRO_WIDTH;
pub const MACRO_ACTION_PLANES: usize = 9;
pub const MACRO_ACTION_SIZE: usize = MACRO_ACTION_PLANES * MACRO_CELLS;
pub const MACRO_TOTAL_TURNS: i32 = 300;
pub const MACRO_MAX_WORKERS: usize = 3;
pub const MACRO_MAX_CANDIDATES: usize = 768;
pub const MACRO_CANDIDATE_FEATURES: usize = 44;
pub const D42_SHARED_CONTEXT_FEATURES: usize = 46;
pub const D42_JOB_CONTEXT_FEATURES: usize = 16;
pub const D42_COMBINED_FEATURES: usize =
    100 + D42_SHARED_CONTEXT_FEATURES + 3 * D42_JOB_CONTEXT_FEATURES;

const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];
const TRAIN_RESOURCE_SLOTS: [usize; 4] = [0, 1, 2, IRON];

#[inline]
pub fn macro_spatial(cell: Cell) -> usize {
    cell.1 as usize * MACRO_WIDTH + cell.0 as usize
}

#[inline]
pub fn macro_action(plane: usize, cell: Cell) -> usize {
    plane * MACRO_CELLS + macro_spatial(cell)
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn ceil_div(value: i32, divisor: i32) -> i32 {
    if divisor <= 0 {
        10_000
    } else {
        (value + divisor - 1) / divisor
    }
}

fn d42_distance(game: &GameState, sources: &[Cell], target: Cell) -> i32 {
    bfs_distances(&game.walkable, sources)
        .get(&target)
        .copied()
        .unwrap_or(50)
        .clamp(0, 50)
}

fn adjacent_to_water(game: &GameState, target: Cell) -> bool {
    game.water
        .iter()
        .any(|water| manhattan(*water, target) == 1)
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

fn worker_count(game: &GameState, player: usize) -> usize {
    own_units(game, player).len()
}

fn shack_doors(game: &GameState, player: usize) -> Vec<Cell> {
    let (x, y) = game.shacks[player];
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        .into_iter()
        .filter(|target| game.walkable.contains(target))
        .collect()
}

fn nearest_door(game: &GameState, player: usize, from: Cell) -> Option<(Cell, i32)> {
    let distances = bfs_distances(&game.walkable, &[from]);
    shack_doors(game, player)
        .into_iter()
        .filter_map(|target| Some((target, *distances.get(&target)?)))
        .min_by_key(|(target, distance)| (*distance, *target))
}

fn player_favored_plant_cell_avoiding(
    game: &GameState,
    player: usize,
    from: Cell,
    reserved: &BTreeSet<Cell>,
) -> Option<Cell> {
    let from_distance = bfs_distances(&game.walkable, &[from]);
    let own_distance = bfs_distances(&game.walkable, &shack_doors(game, player));
    let other_distance = bfs_distances(&game.walkable, &shack_doors(game, 1 - player));
    game.walkable
        .iter()
        .filter(|target| manhattan(**target, game.shacks[player]) <= 4)
        .filter(|target| !game.plants.iter().any(|plant| plant.pos() == **target))
        .filter(|target| !game.units.iter().any(|unit| unit.pos() == **target))
        .filter(|target| !reserved.contains(*target))
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

fn player_favored_plant_cell(game: &GameState, player: usize, from: Cell) -> Option<Cell> {
    player_favored_plant_cell_avoiding(game, player, from, &BTreeSet::new())
}

fn fruit_index(name: &str) -> Option<usize> {
    FRUIT_NAMES.iter().position(|known| *known == name)
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

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum PlantOwner {
    Natural,
    Own,
    Opponent,
    Ambiguous,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MacroOpponentMode {
    Resident,
    GoldAdaptive,
    CompactGold,
    NorxondorThree,
    LegendBalanced,
    MyBot,
    ScriptBoss,
    SilverBoss,
}

impl MacroOpponentMode {
    pub const ALL: [Self; 8] = [
        Self::Resident,
        Self::GoldAdaptive,
        Self::CompactGold,
        Self::NorxondorThree,
        Self::LegendBalanced,
        Self::MyBot,
        Self::ScriptBoss,
        Self::SilverBoss,
    ];

    pub fn from_index(index: usize) -> Self {
        Self::ALL[index % Self::ALL.len()]
    }

    pub fn id(self) -> u8 {
        Self::ALL.iter().position(|mode| *mode == self).unwrap() as u8
    }

    pub fn label(self) -> &'static str {
        match self {
            Self::Resident => "resident",
            Self::GoldAdaptive => "gold_adaptive",
            Self::CompactGold => "compact_gold",
            Self::NorxondorThree => "norx_native_three",
            Self::LegendBalanced => "legend_balanced",
            Self::MyBot => "mybot",
            Self::ScriptBoss => "script_boss",
            Self::SilverBoss => "silver_boss",
        }
    }
}

#[derive(Clone)]
enum MacroOpponent {
    Resident(SecureOrchardBot),
    GoldAdaptive(GoldElite),
    CompactGold(CompactGold),
    NorxondorThree(NorxondorNative),
    LegendBalanced(LegendFieldProxyV2),
    MyBot(MyBot),
    ScriptBoss(ScriptBoss),
    SilverBoss(SilverBoss),
}

impl MacroOpponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => Self::Resident(SecureOrchardBot::new()),
            MacroOpponentMode::GoldAdaptive => Self::GoldAdaptive(GoldElite::adaptive()),
            MacroOpponentMode::CompactGold => Self::CompactGold(CompactGold::new()),
            MacroOpponentMode::NorxondorThree => Self::NorxondorThree(NorxondorNative::new(true)),
            MacroOpponentMode::LegendBalanced => {
                Self::LegendBalanced(LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }))
            }
            MacroOpponentMode::MyBot => Self::MyBot(MyBot::new()),
            MacroOpponentMode::ScriptBoss => Self::ScriptBoss(ScriptBoss::new()),
            MacroOpponentMode::SilverBoss => Self::SilverBoss(SilverBoss::new()),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&resident_view(game, player)),
            Self::GoldAdaptive(strategy) => strategy.decide(game, player),
            Self::CompactGold(strategy) => strategy.decide(game, player),
            Self::NorxondorThree(strategy) => strategy.decide(game, player),
            Self::LegendBalanced(strategy) => strategy.decide(game, player),
            Self::MyBot(strategy) => strategy.decide(game, player),
            Self::ScriptBoss(strategy) => strategy.decide(game, player),
            Self::SilverBoss(strategy) => strategy.decide(game, player),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub enum MacroJobKind {
    IdleOneTurn,
    Bank,
    FellBank,
    HarvestBank,
    Renew,
    MineBank,
}

impl MacroJobKind {
    pub fn label(self) -> &'static str {
        match self {
            Self::IdleOneTurn => "idle_one_turn",
            Self::Bank => "bank",
            Self::FellBank => "fell_bank",
            Self::HarvestBank => "harvest_bank",
            Self::Renew => "renew",
            Self::MineBank => "mine_bank",
        }
    }

    pub fn action_plane(self) -> usize {
        match self {
            Self::IdleOneTurn => 3,
            Self::Bank => 4,
            Self::FellBank => 5,
            Self::HarvestBank => 6,
            Self::Renew => 7,
            Self::MineBank => 8,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MacroTrainGoal {
    None,
    Producer,
    Chopper,
}

impl MacroTrainGoal {
    pub fn spec(self) -> Option<(i32, i32, i32, i32)> {
        match self {
            Self::None => None,
            Self::Producer => Some((2, 2, 1, 1)),
            Self::Chopper => Some((2, 2, 0, 2)),
        }
    }

    pub fn action_plane(self) -> usize {
        match self {
            Self::None => 0,
            Self::Producer => 1,
            Self::Chopper => 2,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum MacroDecisionStage {
    Train,
    Worker,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum MacroSelectionBranch {
    Train = 0,
    Deficit = 1,
    Evacuation = 2,
    Rate = 3,
}

#[derive(Clone, Debug)]
pub struct MacroCandidateObservation {
    pub actions: Vec<i32>,
    pub features: Vec<[f32; MACRO_CANDIDATE_FEATURES]>,
    pub teacher_index: usize,
    pub branch: MacroSelectionBranch,
}

/// Outcome-blind preview of the next same-turn worker after one macro assignment.
///
/// The preview is intentionally limited to the next worker observation. Its temporary opponent
/// controller is never advanced because the method returns `None` unless another worker remains in
/// the current assignment batch.
#[derive(Clone, Debug)]
pub struct MacroPairBranchPreview {
    pub observation: MacroCandidateObservation,
    pub shared_context: [f32; D42_SHARED_CONTEXT_FEATURES],
    pub state_hash: u64,
    pub worker_id: i32,
    pub worker_ordinal: usize,
    pub turn: i32,
    pub live_own_crops: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MacroJobSpec {
    pub kind: MacroJobKind,
    pub unit_id: i32,
    pub target: Option<Cell>,
    pub plant_cell: Option<Cell>,
    pub fruit_kind: Option<usize>,
    pub owner: Option<PlantOwner>,
    pub predicted_eta: i32,
    pub predicted_reward: i32,
    pub predicted_deposit: [i32; 6],
}

impl MacroJobSpec {
    fn action_cell(&self, game: &GameState, seat: usize, unit: &Unit) -> Cell {
        match self.kind {
            MacroJobKind::IdleOneTurn => unit.pos(),
            MacroJobKind::Bank => game.shacks[seat],
            MacroJobKind::FellBank
            | MacroJobKind::HarvestBank
            | MacroJobKind::Renew
            | MacroJobKind::MineBank => self.target.expect("targeted macro job"),
        }
    }

    pub fn action(&self, game: &GameState, seat: usize, unit: &Unit) -> usize {
        macro_action(self.kind.action_plane(), self.action_cell(game, seat, unit))
    }

    fn acquisition_target(&self) -> Option<Cell> {
        match self.kind {
            MacroJobKind::FellBank
            | MacroJobKind::HarvestBank
            | MacroJobKind::Renew
            | MacroJobKind::MineBank => self.target,
            MacroJobKind::IdleOneTurn | MacroJobKind::Bank => None,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum JobPhase {
    Idle,
    Acquire,
    Plant,
    Ripen,
    Bank,
}

#[derive(Clone, Debug)]
struct ActiveJob {
    spec: MacroJobSpec,
    phase: JobPhase,
    initial_carry: [i32; 6],
    bank_seed_source: bool,
    bank_seed_source_lease: bool,
    plant_issued: bool,
    idle_issued: bool,
    age: u16,
}

enum JobCommand {
    Command(String),
    Complete,
    Invalid,
}

impl ActiveJob {
    fn new(spec: MacroJobSpec, game: &GameState) -> Self {
        let unit = game
            .units
            .iter()
            .find(|unit| unit.id == spec.unit_id)
            .expect("macro root unit");
        let phase = match spec.kind {
            MacroJobKind::IdleOneTurn => JobPhase::Idle,
            MacroJobKind::Bank => JobPhase::Bank,
            _ => JobPhase::Acquire,
        };
        Self {
            spec,
            phase,
            initial_carry: unit.carry,
            bank_seed_source: false,
            bank_seed_source_lease: false,
            plant_issued: false,
            idle_issued: false,
            age: 0,
        }
    }

    fn new_bank_seed_source(
        unit_id: i32,
        fruit_kind: usize,
        plant_cell: Cell,
        lease_to_surplus: bool,
        game: &GameState,
    ) -> Self {
        let unit = game
            .units
            .iter()
            .find(|unit| unit.id == unit_id)
            .expect("seed-source unit");
        Self {
            spec: MacroJobSpec {
                kind: MacroJobKind::Renew,
                unit_id,
                target: None,
                plant_cell: Some(plant_cell),
                fruit_kind: Some(fruit_kind),
                owner: None,
                predicted_eta: 0,
                predicted_reward: 0,
                predicted_deposit: {
                    let mut deposit = [0; 6];
                    if lease_to_surplus {
                        deposit[fruit_kind] = 2;
                    }
                    deposit
                },
            },
            phase: JobPhase::Acquire,
            initial_carry: unit.carry,
            bank_seed_source: true,
            bank_seed_source_lease: lease_to_surplus,
            plant_issued: false,
            idle_issued: false,
            age: 0,
        }
    }

    fn acquired(&self, unit: &Unit) -> bool {
        match self.spec.kind {
            MacroJobKind::FellBank => unit.carry[WOOD] > self.initial_carry[WOOD],
            MacroJobKind::HarvestBank | MacroJobKind::Renew => {
                let kind = self.spec.fruit_kind.expect("fruit job kind");
                unit.carry[kind] > self.initial_carry[kind]
            }
            MacroJobKind::MineBank => unit.carry[IRON] > self.initial_carry[IRON],
            MacroJobKind::Bank => true,
            MacroJobKind::IdleOneTurn => false,
        }
    }

    fn bank_command(&self, game: &GameState, player: usize, unit: &Unit) -> JobCommand {
        if unit.total() == 0 {
            return JobCommand::Complete;
        }
        let Some((door, _)) = nearest_door(game, player, unit.pos()) else {
            return JobCommand::Invalid;
        };
        JobCommand::Command(if unit.pos() == door {
            format!("DROP {}", unit.id)
        } else {
            format!("MOVE {} {} {}", unit.id, door.0, door.1)
        })
    }

    fn command(&mut self, game: &GameState, player: usize) -> JobCommand {
        let Some(unit) = game.units.iter().find(|unit| unit.id == self.spec.unit_id) else {
            return JobCommand::Invalid;
        };
        if self.phase == JobPhase::Idle {
            if self.idle_issued {
                return JobCommand::Complete;
            }
            self.idle_issued = true;
            return JobCommand::Command("WAIT".to_string());
        }
        if self.phase == JobPhase::Acquire && self.acquired(unit) {
            self.phase = if self.spec.kind == MacroJobKind::Renew {
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
                    self.phase = if self.bank_seed_source_lease {
                        JobPhase::Ripen
                    } else {
                        JobPhase::Bank
                    };
                } else {
                    return JobCommand::Invalid;
                }
            } else if game.plants.iter().any(|plant| plant.pos() == target) {
                return JobCommand::Invalid;
            } else if unit.carry[kind] <= 0 {
                return JobCommand::Invalid;
            } else if unit.pos() == target {
                self.plant_issued = true;
                return JobCommand::Command(format!("PLANT {} {}", unit.id, FRUIT_NAMES[kind]));
            } else {
                return JobCommand::Command(format!("MOVE {} {} {}", unit.id, target.0, target.1));
            }
        }
        if self.phase == JobPhase::Ripen {
            let target = self.spec.plant_cell.expect("source-lease plant cell");
            let kind = self.spec.fruit_kind.expect("source-lease fruit kind");
            if unit.carry[kind] - self.initial_carry[kind] >= 2 {
                self.phase = JobPhase::Bank;
            } else {
                let Some(plant) = game.plants.iter().find(|plant| {
                    plant.pos() == target
                        && plant.health > 0
                        && plant.plant_type == FRUIT_NAMES[kind]
                }) else {
                    return JobCommand::Invalid;
                };
                if unit.pos() != target {
                    return JobCommand::Command(format!(
                        "MOVE {} {} {}",
                        unit.id, target.0, target.1
                    ));
                }
                if plant.fruits > 0 && unit.hp > 0 && unit.free() > 0 {
                    return JobCommand::Command(format!("HARVEST {}", unit.id));
                }
                return JobCommand::Command("WAIT".to_string());
            }
        }
        if self.phase == JobPhase::Bank {
            return self.bank_command(game, player, unit);
        }

        if self.bank_seed_source {
            let kind = self.spec.fruit_kind.expect("seed-source fruit kind");
            let Some((door, _)) = nearest_door(game, player, unit.pos()) else {
                return JobCommand::Invalid;
            };
            if unit.pos() != door {
                return JobCommand::Command(format!("MOVE {} {} {}", unit.id, door.0, door.1));
            }
            if unit.free() <= 0 || game.inventories[player][kind] <= 0 {
                return JobCommand::Invalid;
            }
            return JobCommand::Command(format!("PICK {} {}", unit.id, FRUIT_NAMES[kind]));
        }

        let target = self.spec.target.expect("acquisition target");
        if unit.pos() != target {
            if !bfs_distances(&game.walkable, &[unit.pos()]).contains_key(&target) {
                return JobCommand::Invalid;
            }
            return JobCommand::Command(format!("MOVE {} {} {}", unit.id, target.0, target.1));
        }
        match self.spec.kind {
            MacroJobKind::FellBank => {
                let valid = game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == target && plant.health > 0);
                if valid && unit.chop > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("CHOP {}", unit.id))
                } else {
                    JobCommand::Invalid
                }
            }
            MacroJobKind::HarvestBank | MacroJobKind::Renew => {
                let valid = game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == target && plant.health > 0 && plant.fruits > 0);
                if valid && unit.hp > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("HARVEST {}", unit.id))
                } else {
                    JobCommand::Invalid
                }
            }
            MacroJobKind::MineBank => {
                let adjacent = game.iron.iter().any(|ore| manhattan(*ore, unit.pos()) == 1);
                if adjacent && unit.chop > 0 && unit.free() > 0 {
                    JobCommand::Command(format!("MINE {}", unit.id))
                } else {
                    JobCommand::Invalid
                }
            }
            MacroJobKind::IdleOneTurn | MacroJobKind::Bank => unreachable!(),
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

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

fn apply_with_provenance(
    game: &mut GameState,
    seat: usize,
    ours: &[String],
    theirs: &[String],
    owners: &mut BTreeMap<Cell, PlantOwner>,
) -> (usize, usize, usize, usize) {
    let before: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    let our_attempts = plant_attempts(game, seat, ours);
    let their_attempts = plant_attempts(game, 1 - seat, theirs);
    apply_commands(game, seat, ours, theirs);
    let after: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    owners.retain(|cell, _| after.contains(cell));
    let mut failures = 0;
    let mut own_plants = 0;
    let mut opponent_plants = 0;
    let mut ambiguous_plants = 0;
    for cell in after.difference(&before) {
        let owner = match (our_attempts.contains(cell), their_attempts.contains(cell)) {
            (true, false) => Some(PlantOwner::Own),
            (false, true) => Some(PlantOwner::Opponent),
            (true, true) => Some(PlantOwner::Ambiguous),
            (false, false) => None,
        };
        if let Some(owner) = owner {
            owners.insert(*cell, owner);
            match owner {
                PlantOwner::Own => own_plants += 1,
                PlantOwner::Opponent => opponent_plants += 1,
                PlantOwner::Ambiguous => ambiguous_plants += 1,
                PlantOwner::Natural => unreachable!(),
            }
        } else {
            failures += 1;
        }
    }
    let failures = failures
        + owners
            .keys()
            .copied()
            .collect::<BTreeSet<_>>()
            .symmetric_difference(&after)
            .count();
    (failures, own_plants, opponent_plants, ambiguous_plants)
}

fn direct_command_is_valid(game: &GameState, player: usize, command: &str) -> bool {
    let parts: Vec<_> = command.split_whitespace().collect();
    let Some(verb) = parts.first().copied() else {
        return false;
    };
    if verb == "WAIT" {
        return parts.len() == 1;
    }
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
        "PICK" => {
            let Some(kind) = parts.get(2).and_then(|name| fruit_index(name)) else {
                return false;
            };
            parts.len() == 3
                && unit.free() > 0
                && game.inventories[player][kind] > 0
                && manhattan(unit.pos(), game.shacks[player]) <= 1
        }
        _ => false,
    }
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct MacroTerminal {
    pub own_reward: f32,
    pub opponent_reward: f32,
    pub margin_reward: f32,
    pub done: bool,
    pub turn: u16,
    pub own_return: f32,
    pub opponent_return: f32,
    pub margin_return: f32,
    pub own_score: i32,
    pub opponent_score: i32,
    pub own_workers: u8,
    pub opponent_workers: u8,
    pub successful_trains: u8,
    pub completed_jobs: u16,
    pub invalidated_jobs: u16,
    pub invalid_direct_commands: u16,
    pub provenance_failures: u16,
    pub deposit_prediction_failures: u16,
    pub selected_decisions: u32,
    pub selected_jobs: u16,
    pub selected_nonidle_jobs: u16,
    pub selected_renew_jobs: u16,
    pub own_created_crops: u16,
    pub opponent_created_crops: u16,
    pub ambiguous_created_crops: u16,
    pub own_owned_crop_harvest_units: u16,
    pub own_reinvested_crops: u16,
    pub action_hash: u64,
    pub state_hash: u64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct MacroSeedSourceOutcome {
    pub terminal: MacroTerminal,
    pub fruit_kind: usize,
    pub target: Cell,
    pub start_turn: i32,
    pub end_turn: i32,
    pub pick_commands: u16,
    pub plant_commands: u16,
    pub harvest_commands: u16,
    pub drop_commands: u16,
    pub wait_commands: u16,
}

#[derive(Clone)]
pub struct CompleteMacroEnv {
    pub state: GameState,
    pub map_seed: i64,
    pub seat: usize,
    pub opponent_mode: MacroOpponentMode,
    opponent: MacroOpponent,
    owners: BTreeMap<Cell, PlantOwner>,
    active: BTreeMap<i32, ActiveJob>,
    train_goal: MacroTrainGoal,
    stage: MacroDecisionStage,
    free_ids: Vec<i32>,
    free_index: usize,
    candidate_jobs: Vec<MacroJobSpec>,
    stall_counter: i32,
    previous_scores: [i32; 2],
    returns: [f32; 2],
    margin_return: f32,
    done: bool,
    successful_trains: u8,
    completed_jobs: u16,
    invalidated_jobs: u16,
    invalid_direct_commands: u16,
    provenance_failures: u16,
    deposit_prediction_failures: u16,
    selected_decisions: u32,
    selected_jobs: u16,
    selected_nonidle_jobs: u16,
    selected_renew_jobs: u16,
    own_created_crops: u16,
    opponent_created_crops: u16,
    ambiguous_created_crops: u16,
    own_owned_crop_harvest_units: u16,
    own_reinvested_crops: u16,
    explicit_source_creations: [u16; 4],
    seed_source_pick_commands: u16,
    seed_source_plant_commands: u16,
    seed_source_harvest_commands: u16,
    seed_source_drop_commands: u16,
    seed_source_wait_commands: u16,
    action_hash: u64,
}

impl CompleteMacroEnv {
    pub fn new(map_seed: i64, seat: usize, opponent_mode: MacroOpponentMode) -> Self {
        assert!(seat < 2);
        let state = generate_official(map_seed);
        let owners = state
            .plants
            .iter()
            .map(|plant| (plant.pos(), PlantOwner::Natural))
            .collect();
        let previous_scores = [state.scores[seat], state.scores[1 - seat]];
        let mut env = Self {
            state,
            map_seed,
            seat,
            opponent_mode,
            opponent: MacroOpponent::new(opponent_mode),
            owners,
            active: BTreeMap::new(),
            train_goal: MacroTrainGoal::None,
            stage: MacroDecisionStage::Train,
            free_ids: Vec::new(),
            free_index: 0,
            candidate_jobs: Vec::new(),
            stall_counter: 0,
            previous_scores,
            returns: [0.0; 2],
            margin_return: 0.0,
            done: false,
            successful_trains: 0,
            completed_jobs: 0,
            invalidated_jobs: 0,
            invalid_direct_commands: 0,
            provenance_failures: 0,
            deposit_prediction_failures: 0,
            selected_decisions: 0,
            selected_jobs: 0,
            selected_nonidle_jobs: 0,
            selected_renew_jobs: 0,
            own_created_crops: 0,
            opponent_created_crops: 0,
            ambiguous_created_crops: 0,
            own_owned_crop_harvest_units: 0,
            own_reinvested_crops: 0,
            explicit_source_creations: [0; 4],
            seed_source_pick_commands: 0,
            seed_source_plant_commands: 0,
            seed_source_harvest_commands: 0,
            seed_source_drop_commands: 0,
            seed_source_wait_commands: 0,
            action_hash: 0xcbf29ce484222325,
        };
        env.refresh_free_ids();
        env
    }

    pub fn stage(&self) -> MacroDecisionStage {
        self.stage
    }

    pub fn train_goal(&self) -> MacroTrainGoal {
        self.train_goal
    }

    pub fn owners(&self) -> &BTreeMap<Cell, PlantOwner> {
        &self.owners
    }

    pub fn active_jobs(&self) -> Vec<MacroJobSpec> {
        self.active.values().map(|job| job.spec.clone()).collect()
    }

    pub fn explicit_source_creations(&self) -> [u16; 4] {
        self.explicit_source_creations
    }

    pub fn opening_source_in_flight(&self) -> bool {
        self.active.values().any(|job| job.bank_seed_source)
    }

    fn opening_source_target_for_unit(&self, fruit_kind: usize, unit_id: i32) -> Option<Cell> {
        if self.done
            || fruit_kind >= FRUIT_NAMES.len()
            || self.state.inventories[self.seat][fruit_kind] <= 0
            || self.opening_source_in_flight()
        {
            return None;
        }
        let unit = self.state.units.iter().find(|unit| {
            unit.id == unit_id && unit.player as usize == self.seat && unit.total() == 0
        })?;
        let reserved: BTreeSet<_> = self
            .active
            .values()
            .filter_map(|job| job.spec.plant_cell)
            .collect();
        player_favored_plant_cell_avoiding(&self.state, self.seat, unit.pos(), &reserved)
    }

    /// Whether a D71 explicit source can be assigned to the first free worker.
    ///
    /// This query and the corresponding worker-stage step are inert unless an experimental
    /// opening-portfolio wrapper calls them.
    pub fn opening_bank_seed_source_available(&self, fruit_kind: usize) -> bool {
        let unit_id = match self.stage {
            MacroDecisionStage::Train => self.free_ids.first().copied(),
            MacroDecisionStage::Worker => self.current_unit_id(),
        };
        unit_id.is_some_and(|id| {
            self.opening_source_target_for_unit(fruit_kind, id)
                .is_some()
        })
    }

    /// Assign one explicit deposited-seed source job to the current free worker.
    ///
    /// The caller must already have selected the no-TRAIN action for this batch. Remaining free
    /// workers can then receive ordinary jobs, while existing jobs continue concurrently.
    pub fn step_opening_bank_seed_source_current(
        &mut self,
        fruit_kind: usize,
    ) -> Option<MacroTerminal> {
        if self.stage != MacroDecisionStage::Worker {
            return None;
        }
        let unit_id = self.current_unit_id()?;
        let target = self.opening_source_target_for_unit(fruit_kind, unit_id)?;
        self.active.insert(
            unit_id,
            ActiveJob::new_bank_seed_source(unit_id, fruit_kind, target, false, &self.state),
        );
        self.selected_decisions = self.selected_decisions.saturating_add(1);
        self.selected_jobs = self.selected_jobs.saturating_add(1);
        self.selected_nonidle_jobs = self.selected_nonidle_jobs.saturating_add(1);
        self.selected_renew_jobs = self.selected_renew_jobs.saturating_add(1);
        let action = MACRO_ACTION_PLANES * MACRO_CELLS + fruit_kind;
        self.action_hash ^= action as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        self.action_hash ^= self.state.turn as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        self.free_index += 1;
        Some(if self.free_index < self.free_ids.len() {
            self.refresh_candidate_jobs();
            self.terminal([0.0; 2], 0.0)
        } else {
            self.advance_until_boundary()
        })
    }

    /// Execute one explicitly requested deposited-seed source transaction.
    ///
    /// This method is inert unless an experiment calls it at a one-worker Train boundary. Normal
    /// D40/D61 paths never invoke it and retain their exact action space and behavior.
    pub fn install_bank_seed_source(
        &mut self,
        fruit_kind: usize,
    ) -> Option<MacroSeedSourceOutcome> {
        self.install_bank_seed_source_mode(fruit_kind, false)
    }

    /// Execute a deposited-seed source lease through two harvested and deposited fruits.
    ///
    /// Spending one seed and depositing two fruits creates the first unit of net bill progress.
    /// Like the shorter D65 transaction, this path is inert unless an experiment calls it.
    pub fn install_bank_seed_source_surplus_lease(
        &mut self,
        fruit_kind: usize,
    ) -> Option<MacroSeedSourceOutcome> {
        self.install_bank_seed_source_mode(fruit_kind, true)
    }

    /// Execute the surplus lease at an explicitly audited empty, reachable target cell.
    ///
    /// Normal controllers never call this method; it exists only for source-cell feasibility
    /// experiments and retains every transaction rule of the deterministic lease.
    pub fn install_bank_seed_source_surplus_lease_at(
        &mut self,
        fruit_kind: usize,
        target: Cell,
    ) -> Option<MacroSeedSourceOutcome> {
        let unit_id = self.bank_seed_source_unit(fruit_kind)?;
        let unit = self.state.units.iter().find(|unit| unit.id == unit_id)?;
        if !self.state.walkable.contains(&target)
            || self.state.plants.iter().any(|plant| plant.pos() == target)
            || self.state.units.iter().any(|unit| unit.pos() == target)
            || !bfs_distances(&self.state.walkable, &[unit.pos()]).contains_key(&target)
        {
            return None;
        }
        Some(self.start_bank_seed_source(unit_id, fruit_kind, target, true))
    }

    fn bank_seed_source_unit(&self, fruit_kind: usize) -> Option<i32> {
        if self.done
            || self.stage != MacroDecisionStage::Train
            || worker_count(&self.state, self.seat) != 1
            || self.train_goal != MacroTrainGoal::Producer
            || fruit_kind >= FRUIT_NAMES.len()
            || self.state.inventories[self.seat][fruit_kind] <= 0
            || !self.active.is_empty()
        {
            return None;
        }
        let unit_id = *self.free_ids.first()?;
        let unit = self.state.units.iter().find(|unit| unit.id == unit_id)?;
        (unit.total() == 0).then_some(unit_id)
    }

    fn install_bank_seed_source_mode(
        &mut self,
        fruit_kind: usize,
        lease_to_surplus: bool,
    ) -> Option<MacroSeedSourceOutcome> {
        let unit_id = self.bank_seed_source_unit(fruit_kind)?;
        let unit = self.state.units.iter().find(|unit| unit.id == unit_id)?;
        let target = player_favored_plant_cell(&self.state, self.seat, unit.pos())?;
        Some(self.start_bank_seed_source(unit_id, fruit_kind, target, lease_to_surplus))
    }

    fn start_bank_seed_source(
        &mut self,
        unit_id: i32,
        fruit_kind: usize,
        target: Cell,
        lease_to_surplus: bool,
    ) -> MacroSeedSourceOutcome {
        let start_turn = self.state.turn;
        let picks_before = self.seed_source_pick_commands;
        let plants_before = self.seed_source_plant_commands;
        let harvests_before = self.seed_source_harvest_commands;
        let drops_before = self.seed_source_drop_commands;
        let waits_before = self.seed_source_wait_commands;
        self.active.insert(
            unit_id,
            ActiveJob::new_bank_seed_source(
                unit_id,
                fruit_kind,
                target,
                lease_to_surplus,
                &self.state,
            ),
        );
        self.selected_decisions = self.selected_decisions.saturating_add(1);
        self.selected_jobs = self.selected_jobs.saturating_add(1);
        self.selected_nonidle_jobs = self.selected_nonidle_jobs.saturating_add(1);
        self.selected_renew_jobs = self.selected_renew_jobs.saturating_add(1);
        let action = macro_action(MacroJobKind::Renew.action_plane(), target);
        self.action_hash ^= action as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        self.action_hash ^= self.state.turn as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        let terminal = self.advance_until_boundary();
        MacroSeedSourceOutcome {
            terminal,
            fruit_kind,
            target,
            start_turn,
            end_turn: self.state.turn,
            pick_commands: self.seed_source_pick_commands - picks_before,
            plant_commands: self.seed_source_plant_commands - plants_before,
            harvest_commands: self.seed_source_harvest_commands - harvests_before,
            drop_commands: self.seed_source_drop_commands - drops_before,
            wait_commands: self.seed_source_wait_commands - waits_before,
        }
    }

    pub fn current_unit_id(&self) -> Option<i32> {
        (self.stage == MacroDecisionStage::Worker)
            .then(|| self.free_ids.get(self.free_index).copied())
            .flatten()
    }

    /// Promote the maximum-chop worker to the front of the unassigned free-worker suffix.
    ///
    /// Returns `None` outside an eligible post-funding worker batch, `Some(false)` when that
    /// worker is already first, and `Some(true)` when the suffix was stably reordered. All other
    /// free workers retain their relative order.
    pub fn promote_max_chop_remaining_free_unit(&mut self) -> Option<bool> {
        if self.stage != MacroDecisionStage::Worker
            || worker_count(&self.state, self.seat) < MACRO_MAX_WORKERS
            || self.free_index >= self.free_ids.len()
        {
            return None;
        }
        let designated = own_units(&self.state, self.seat)
            .into_iter()
            .max_by_key(|unit| (unit.chop, unit.id))?
            .id;
        let relative = self.free_ids[self.free_index..]
            .iter()
            .position(|id| *id == designated)?;
        if relative == 0 {
            return Some(false);
        }
        let absolute = self.free_index + relative;
        let unit_id = self.free_ids.remove(absolute);
        self.free_ids.insert(self.free_index, unit_id);
        Some(true)
    }

    /// Frozen outcome-blind shared context for D42 continuation selection.
    pub fn d42_shared_context(&self) -> [f32; D42_SHARED_CONTEXT_FEATURES] {
        let unit_id = self.current_unit_id().expect("D42 context worker stage");
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| unit.id == unit_id)
            .expect("D42 current worker");
        let opponent = 1 - self.seat;
        let mut result = [0.0f32; D42_SHARED_CONTEXT_FEATURES];
        for item in 0..6 {
            result[item] = self.state.inventories[self.seat][item] as f32 / 20.0;
            result[6 + item] = self.state.inventories[opponent][item] as f32 / 20.0;
        }
        result[12] = worker_count(&self.state, opponent) as f32 / 3.0;
        result[13] = self.active.len() as f32 / 3.0;
        result[14] = unit.ms as f32 / 4.0;
        result[15] = unit.cc as f32 / 4.0;
        result[16] = unit.hp as f32 / 4.0;
        result[17] = unit.chop as f32 / 4.0;
        for item in 0..6 {
            result[18 + item] = unit.carry[item] as f32 / 10.0;
        }
        result[24] = unit.free() as f32 / 10.0;
        let mut active_kinds = [0usize; 6];
        let mut active_deposits = [0i32; 6];
        for active in self.active.values() {
            active_kinds[active.spec.kind as usize] += 1;
            for (total, deposit) in active_deposits
                .iter_mut()
                .zip(active.spec.predicted_deposit)
            {
                *total = total.saturating_add(deposit);
            }
        }
        for kind in 0..6 {
            result[25 + kind] = active_kinds[kind] as f32 / 3.0;
        }
        for item in 0..6 {
            result[31 + item] = active_deposits[item] as f32 / 20.0;
        }
        let mut owner_counts = [0usize; 4];
        let mut owner_fruits = [0i32; 4];
        for plant in &self.state.plants {
            let owner = *self.owners.get(&plant.pos()).expect("D42 plant provenance");
            let index = match owner {
                PlantOwner::Natural => 0,
                PlantOwner::Own => 1,
                PlantOwner::Opponent => 2,
                PlantOwner::Ambiguous => 3,
            };
            owner_counts[index] += 1;
            owner_fruits[index] = owner_fruits[index].saturating_add(plant.fruits);
        }
        for owner in 0..4 {
            result[37 + owner] = owner_counts[owner] as f32 / 20.0;
        }
        result[41] = owner_fruits[1] as f32 / 40.0;
        result[42] = owner_fruits[2] as f32 / 40.0;
        result[43] = self.state.water.len() as f32 / MACRO_CELLS as f32;
        result[44] = self.state.walkable.len() as f32 / MACRO_CELLS as f32;
        let opponent_sources: Vec<_> = self
            .state
            .units
            .iter()
            .filter(|other| other.player as usize == opponent)
            .map(Unit::pos)
            .collect();
        result[45] = d42_distance(&self.state, &opponent_sources, unit.pos()) as f32 / 50.0;
        assert!(result.iter().all(|value| value.is_finite()));
        result
    }

    /// Preview exactly one worker assignment and expose the following same-turn worker context.
    ///
    /// This supports collision-safe pair allocation without rolling the game, opponent, or terminal
    /// value forward. The real environment is unchanged.
    pub fn pair_branch_preview(&self, selected_action: usize) -> Option<MacroPairBranchPreview> {
        if self.stage != MacroDecisionStage::Worker
            || self.free_index + 1 >= self.free_ids.len()
            || !self.legal_actions().contains(&selected_action)
        {
            return None;
        }
        let start_turn = self.state.turn;
        let mut branch = Self {
            state: self.state.clone(),
            map_seed: self.map_seed,
            seat: self.seat,
            opponent_mode: self.opponent_mode,
            opponent: MacroOpponent::new(self.opponent_mode),
            owners: self.owners.clone(),
            active: self.active.clone(),
            train_goal: self.train_goal,
            stage: self.stage,
            free_ids: self.free_ids.clone(),
            free_index: self.free_index,
            candidate_jobs: self.candidate_jobs.clone(),
            stall_counter: self.stall_counter,
            previous_scores: self.previous_scores,
            returns: self.returns,
            margin_return: self.margin_return,
            done: self.done,
            successful_trains: self.successful_trains,
            completed_jobs: self.completed_jobs,
            invalidated_jobs: self.invalidated_jobs,
            invalid_direct_commands: self.invalid_direct_commands,
            provenance_failures: self.provenance_failures,
            deposit_prediction_failures: self.deposit_prediction_failures,
            selected_decisions: self.selected_decisions,
            selected_jobs: self.selected_jobs,
            selected_nonidle_jobs: self.selected_nonidle_jobs,
            selected_renew_jobs: self.selected_renew_jobs,
            own_created_crops: self.own_created_crops,
            opponent_created_crops: self.opponent_created_crops,
            ambiguous_created_crops: self.ambiguous_created_crops,
            own_owned_crop_harvest_units: self.own_owned_crop_harvest_units,
            own_reinvested_crops: self.own_reinvested_crops,
            explicit_source_creations: self.explicit_source_creations,
            seed_source_pick_commands: self.seed_source_pick_commands,
            seed_source_plant_commands: self.seed_source_plant_commands,
            seed_source_harvest_commands: self.seed_source_harvest_commands,
            seed_source_drop_commands: self.seed_source_drop_commands,
            seed_source_wait_commands: self.seed_source_wait_commands,
            action_hash: self.action_hash,
        };
        let terminal = branch.step(selected_action);
        assert!(!terminal.done, "pair preview unexpectedly terminated");
        assert_eq!(
            branch.state.turn, start_turn,
            "pair preview advanced game turn"
        );
        assert_eq!(
            branch.stage,
            MacroDecisionStage::Worker,
            "pair preview did not expose second worker"
        );
        let worker_id = branch
            .current_unit_id()
            .expect("pair preview second worker");
        let mut unit_ids: Vec<_> = branch
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize == branch.seat)
            .map(|unit| unit.id)
            .collect();
        unit_ids.sort_unstable();
        let worker_ordinal = unit_ids
            .iter()
            .position(|id| *id == worker_id)
            .expect("pair preview worker ordinal");
        let live_own_crops = branch
            .state
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter(|plant| branch.owners.get(&plant.pos()) == Some(&PlantOwner::Own))
            .count();
        Some(MacroPairBranchPreview {
            observation: branch.candidate_observation(),
            shared_context: branch.d42_shared_context(),
            state_hash: branch.state_hash(),
            worker_id,
            worker_ordinal,
            turn: branch.state.turn,
            live_own_crops,
        })
    }

    /// Frozen outcome-blind action-target context for one D42 candidate job.
    pub fn d42_job_context(&self, action: i32) -> [f32; D42_JOB_CONTEXT_FEATURES] {
        let unit_id = self.current_unit_id().expect("D42 context worker stage");
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| unit.id == unit_id)
            .expect("D42 current worker");
        let job = self
            .candidate_jobs
            .iter()
            .find(|job| job.action(&self.state, self.seat, unit) == action as usize)
            .expect("D42 candidate action");
        let target = job.action_cell(&self.state, self.seat, unit);
        let opponent = 1 - self.seat;
        let opponent_sources: Vec<_> = self
            .state
            .units
            .iter()
            .filter(|other| other.player as usize == opponent)
            .map(Unit::pos)
            .collect();
        let own_shack = [self.state.shacks[self.seat]];
        let opponent_shack = [self.state.shacks[opponent]];
        let mut result = [0.0f32; D42_JOB_CONTEXT_FEATURES];
        result[0] = target.0 as f32 / (MACRO_WIDTH - 1) as f32;
        result[1] = target.1 as f32 / (MACRO_HEIGHT - 1) as f32;
        result[2] = d42_distance(&self.state, &[unit.pos()], target) as f32 / 50.0;
        result[3] = d42_distance(&self.state, &own_shack, target) as f32 / 50.0;
        result[4] = d42_distance(&self.state, &opponent_shack, target) as f32 / 50.0;
        let opponent_distance = d42_distance(&self.state, &opponent_sources, target);
        result[5] = opponent_distance as f32 / 50.0;
        if let Some(plant) = self.state.plants.iter().find(|plant| plant.pos() == target) {
            result[6] = plant.health as f32 / 20.0;
            result[7] = plant.size as f32 / 10.0;
            result[8] = plant.fruits as f32 / 20.0;
            result[9] = plant.cooldown as f32 / 20.0;
        }
        result[10] = f32::from(adjacent_to_water(&self.state, target));
        result[11] = f32::from(
            self.state
                .units
                .iter()
                .any(|other| other.player as usize == self.seat && other.pos() == target),
        );
        result[12] = f32::from(
            self.state
                .units
                .iter()
                .any(|other| other.player as usize == opponent && other.pos() == target),
        );
        result[13] = f32::from(opponent_distance <= 2);
        if let Some(plant_cell) = job.plant_cell {
            let own_distance = d42_distance(&self.state, &own_shack, plant_cell);
            let opponent_distance = d42_distance(&self.state, &opponent_shack, plant_cell);
            result[14] = (opponent_distance - own_distance) as f32 / 50.0;
            result[15] = f32::from(adjacent_to_water(&self.state, plant_cell));
        }
        assert!(result.iter().all(|value| value.is_finite()));
        result
    }

    fn refresh_free_ids(&mut self) {
        self.free_ids = own_units(&self.state, self.seat)
            .into_iter()
            .map(|unit| unit.id)
            .filter(|id| !self.active.contains_key(id))
            .collect();
        self.free_index = 0;
        self.candidate_jobs.clear();
        self.stage = MacroDecisionStage::Train;
    }

    fn refresh_candidate_jobs(&mut self) {
        self.candidate_jobs = self.jobs_for_current_unit();
    }

    fn reserved_targets(&self) -> (BTreeSet<Cell>, BTreeSet<Cell>) {
        let acquisitions = self
            .active
            .values()
            .filter_map(|job| job.spec.acquisition_target())
            .collect();
        let plant_cells = self
            .active
            .values()
            .filter_map(|job| job.spec.plant_cell)
            .collect();
        (acquisitions, plant_cells)
    }

    pub fn jobs_for_current_unit(&self) -> Vec<MacroJobSpec> {
        let Some(id) = self.current_unit_id() else {
            return Vec::new();
        };
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| unit.id == id)
            .expect("free macro unit");
        let (reserved_targets, reserved_plant_cells) = self.reserved_targets();
        let from_unit = bfs_distances(&self.state.walkable, &[unit.pos()]);
        let bank_distances =
            bfs_distances(&self.state.walkable, &shack_doors(&self.state, self.seat));
        let mut jobs = vec![MacroJobSpec {
            kind: MacroJobKind::IdleOneTurn,
            unit_id: id,
            target: None,
            plant_cell: None,
            fruit_kind: None,
            owner: None,
            predicted_eta: 1,
            predicted_reward: 0,
            predicted_deposit: [0; 6],
        }];
        if unit.total() > 0 {
            if let Some((_, distance)) = nearest_door(&self.state, self.seat, unit.pos()) {
                jobs.push(MacroJobSpec {
                    kind: MacroJobKind::Bank,
                    unit_id: id,
                    target: None,
                    plant_cell: None,
                    fruit_kind: None,
                    owner: None,
                    predicted_eta: ceil_div(distance, unit.ms) + 1,
                    predicted_reward: unit.carry[..4].iter().sum::<i32>() + 4 * unit.carry[WOOD],
                    predicted_deposit: unit.carry,
                });
            }
        }
        if unit.chop > 0 && unit.free() > 0 {
            for plant in self.state.plants.iter().filter(|plant| plant.health > 0) {
                let target = plant.pos();
                if reserved_targets.contains(&target) {
                    continue;
                }
                let Some(travel) = from_unit.get(&target).copied() else {
                    continue;
                };
                let Some(bank_distance) = bank_distances.get(&target).copied() else {
                    continue;
                };
                let reward = 4 * plant.size.min(unit.free());
                let mut predicted_deposit = unit.carry;
                predicted_deposit[WOOD] += plant.size.min(unit.free());
                jobs.push(MacroJobSpec {
                    kind: MacroJobKind::FellBank,
                    unit_id: id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: None,
                    owner: self.owners.get(&target).copied(),
                    predicted_eta: ceil_div(travel, unit.ms)
                        + ceil_div(plant.health, unit.chop)
                        + ceil_div(bank_distance, unit.ms)
                        + 1,
                    predicted_reward: reward,
                    predicted_deposit,
                });
            }
        }
        if unit.hp > 0 && unit.free() > 0 {
            for plant in self
                .state
                .plants
                .iter()
                .filter(|plant| plant.health > 0 && plant.fruits > 0)
            {
                let target = plant.pos();
                if reserved_targets.contains(&target) {
                    continue;
                }
                let Some(kind) = fruit_index(&plant.plant_type) else {
                    continue;
                };
                let Some(travel) = from_unit.get(&target).copied() else {
                    continue;
                };
                let Some(bank_distance) = bank_distances.get(&target).copied() else {
                    continue;
                };
                let reward = plant.fruits.min(unit.hp).min(unit.free());
                let mut harvest_deposit = unit.carry;
                harvest_deposit[kind] += reward;
                let common = MacroJobSpec {
                    kind: MacroJobKind::HarvestBank,
                    unit_id: id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: Some(kind),
                    owner: self.owners.get(&target).copied(),
                    predicted_eta: ceil_div(travel, unit.ms)
                        + 1
                        + ceil_div(bank_distance, unit.ms)
                        + 1,
                    predicted_reward: reward,
                    predicted_deposit: harvest_deposit,
                };
                jobs.push(common);
                if let Some(plant_cell) = player_favored_plant_cell(&self.state, self.seat, target)
                {
                    if !reserved_plant_cells.contains(&plant_cell) {
                        let travel_to_plant = bfs_distances(&self.state.walkable, &[target])
                            .get(&plant_cell)
                            .copied()
                            .unwrap_or(10_000);
                        let plant_to_bank =
                            bank_distances.get(&plant_cell).copied().unwrap_or(10_000);
                        let mut renew_deposit = harvest_deposit;
                        renew_deposit[kind] = (renew_deposit[kind] - 1).max(0);
                        jobs.push(MacroJobSpec {
                            kind: MacroJobKind::Renew,
                            unit_id: id,
                            target: Some(target),
                            plant_cell: Some(plant_cell),
                            fruit_kind: Some(kind),
                            owner: self.owners.get(&target).copied(),
                            predicted_eta: ceil_div(travel, unit.ms)
                                + 1
                                + ceil_div(travel_to_plant, unit.ms)
                                + 1
                                + ceil_div(plant_to_bank, unit.ms)
                                + 1,
                            predicted_reward: reward + 16,
                            predicted_deposit: renew_deposit,
                        });
                    }
                }
            }
        }
        if unit.chop > 0 && unit.free() > 0 {
            let mut mine_cells = BTreeSet::new();
            for ore in &self.state.iron {
                let (x, y) = *ore;
                for target in [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)] {
                    if self.state.walkable.contains(&target)
                        && from_unit.contains_key(&target)
                        && !reserved_targets.contains(&target)
                    {
                        mine_cells.insert(target);
                    }
                }
            }
            for target in mine_cells {
                let Some(bank_distance) = bank_distances.get(&target).copied() else {
                    continue;
                };
                let amount = unit.chop.min(unit.free());
                let mut predicted_deposit = unit.carry;
                predicted_deposit[IRON] += amount;
                jobs.push(MacroJobSpec {
                    kind: MacroJobKind::MineBank,
                    unit_id: id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: None,
                    owner: None,
                    predicted_eta: ceil_div(from_unit[&target], unit.ms)
                        + 1
                        + ceil_div(bank_distance, unit.ms)
                        + 1,
                    predicted_reward: 1,
                    predicted_deposit,
                });
            }
        }
        jobs.retain(|job| self.state.turn + job.predicted_eta <= MACRO_TOTAL_TURNS + 1);
        jobs.sort_by_key(|job| {
            (
                job.kind,
                job.target,
                job.plant_cell,
                job.fruit_kind,
                job.predicted_eta,
            )
        });
        jobs.dedup_by_key(|job| (job.kind, job.target, job.plant_cell, job.fruit_kind));
        jobs
    }

    pub fn legal_actions(&self) -> Vec<usize> {
        if self.done {
            return Vec::new();
        }
        match self.stage {
            MacroDecisionStage::Train => {
                let shack = self.state.shacks[self.seat];
                let mut actions = vec![macro_action(0, shack)];
                if worker_count(&self.state, self.seat) < MACRO_MAX_WORKERS
                    && self.state.turn <= MACRO_TOTAL_TURNS - 30
                {
                    actions.push(macro_action(1, shack));
                    actions.push(macro_action(2, shack));
                }
                actions
            }
            MacroDecisionStage::Worker => {
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == self.current_unit_id())
                    .expect("current macro worker");
                self.candidate_jobs
                    .iter()
                    .map(|job| job.action(&self.state, self.seat, unit))
                    .collect()
            }
        }
    }

    fn train_action(&self, goal: MacroTrainGoal) -> usize {
        macro_action(goal.action_plane(), self.state.shacks[self.seat])
    }

    fn affordable_train(&self, goal: MacroTrainGoal) -> bool {
        let Some(spec) = goal.spec() else {
            return false;
        };
        let count = worker_count(&self.state, self.seat);
        if count >= MACRO_MAX_WORKERS || self.state.turn > MACRO_TOTAL_TURNS - 30 {
            return false;
        }
        let cost = training_cost(count as i32, spec);
        let inventory = self.state.inventories[self.seat];
        inventory[0] >= cost[0]
            && inventory[1] >= cost[1]
            && inventory[2] >= cost[2]
            && (self.state.iron.is_empty() || inventory[IRON] >= cost[IRON])
            && !self.state.units.iter().any(|unit| {
                unit.player as usize == self.seat && unit.pos() == self.state.shacks[self.seat]
            })
    }

    fn train_deficit(&self) -> [i32; 6] {
        let Some(spec) = self.train_goal.spec() else {
            return [0; 6];
        };
        let count = worker_count(&self.state, self.seat);
        if count >= MACRO_MAX_WORKERS || self.state.turn > MACRO_TOTAL_TURNS - 30 {
            return [0; 6];
        }
        let mut cost = training_cost(count as i32, spec);
        if self.state.iron.is_empty() {
            cost[IRON] = 0;
        }
        let mut covered = self.state.inventories[self.seat];
        for job in self.active.values() {
            for (available, deposit) in covered.iter_mut().zip(job.spec.predicted_deposit) {
                *available = available.saturating_add(deposit);
            }
        }
        let mut deficit = [0; 6];
        for index in 0..deficit.len() {
            deficit[index] = (cost[index] - covered[index]).max(0);
        }
        deficit
    }

    fn deficit_reduction(job: &MacroJobSpec, deficit: [i32; 6]) -> i32 {
        deficit
            .into_iter()
            .zip(job.predicted_deposit)
            .map(|(needed, deposit)| needed.min(deposit))
            .sum()
    }

    fn train_command(goal: MacroTrainGoal) -> String {
        let (ms, cc, hp, chop) = goal.spec().expect("nonempty train goal");
        format!("TRAIN {ms} {cc} {hp} {chop}")
    }

    fn terminal(&self, rewards: [f32; 2], margin_reward: f32) -> MacroTerminal {
        MacroTerminal {
            own_reward: rewards[0],
            opponent_reward: rewards[1],
            margin_reward,
            done: self.done,
            turn: self.state.turn.clamp(0, u16::MAX as i32) as u16,
            own_return: self.returns[0],
            opponent_return: self.returns[1],
            margin_return: self.margin_return,
            own_score: self.state.scores[self.seat],
            opponent_score: self.state.scores[1 - self.seat],
            own_workers: worker_count(&self.state, self.seat).min(u8::MAX as usize) as u8,
            opponent_workers: worker_count(&self.state, 1 - self.seat).min(u8::MAX as usize) as u8,
            successful_trains: self.successful_trains,
            completed_jobs: self.completed_jobs,
            invalidated_jobs: self.invalidated_jobs,
            invalid_direct_commands: self.invalid_direct_commands,
            provenance_failures: self.provenance_failures,
            deposit_prediction_failures: self.deposit_prediction_failures,
            selected_decisions: self.selected_decisions,
            selected_jobs: self.selected_jobs,
            selected_nonidle_jobs: self.selected_nonidle_jobs,
            selected_renew_jobs: self.selected_renew_jobs,
            own_created_crops: self.own_created_crops,
            opponent_created_crops: self.opponent_created_crops,
            ambiguous_created_crops: self.ambiguous_created_crops,
            own_owned_crop_harvest_units: self.own_owned_crop_harvest_units,
            own_reinvested_crops: self.own_reinvested_crops,
            action_hash: self.action_hash,
            state_hash: self.state_hash(),
        }
    }

    pub fn state_hash(&self) -> u64 {
        fn mix(hash: &mut u64, value: i64) {
            for byte in value.to_le_bytes() {
                *hash ^= u64::from(byte);
                *hash = hash.wrapping_mul(0x100000001b3);
            }
        }

        let mut hash = 0xcbf29ce484222325;
        for value in [
            self.state.width,
            self.state.height,
            self.state.turn,
            self.state.next_id,
            self.state.scores[0],
            self.state.scores[1],
        ] {
            mix(&mut hash, i64::from(value));
        }
        for cell in self.state.shacks {
            mix(&mut hash, i64::from(cell.0));
            mix(&mut hash, i64::from(cell.1));
        }
        for inventory in self.state.inventories {
            for value in inventory {
                mix(&mut hash, i64::from(value));
            }
        }
        let mut units: Vec<_> = self.state.units.iter().collect();
        units.sort_by_key(|unit| unit.id);
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
                mix(&mut hash, i64::from(value));
            }
            for value in unit.carry {
                mix(&mut hash, i64::from(value));
            }
        }
        let mut plants: Vec<_> = self.state.plants.iter().collect();
        plants.sort_by_key(|plant| (plant.pos(), &plant.plant_type));
        for plant in plants {
            for byte in plant.plant_type.as_bytes() {
                hash ^= u64::from(*byte);
                hash = hash.wrapping_mul(0x100000001b3);
            }
            for value in [
                plant.x,
                plant.y,
                plant.size,
                plant.health,
                plant.fruits,
                plant.cooldown,
            ] {
                mix(&mut hash, i64::from(value));
            }
        }
        for cells in [&self.state.walkable, &self.state.iron, &self.state.water] {
            let mut ordered: Vec<_> = cells.iter().copied().collect();
            ordered.sort_unstable();
            mix(&mut hash, ordered.len() as i64);
            for cell in ordered {
                mix(&mut hash, i64::from(cell.0));
                mix(&mut hash, i64::from(cell.1));
            }
        }
        for (cell, owner) in &self.owners {
            mix(&mut hash, i64::from(cell.0));
            mix(&mut hash, i64::from(cell.1));
            mix(&mut hash, *owner as i64);
        }
        hash
    }

    fn advance_until_boundary(&mut self) -> MacroTerminal {
        let start_scores = [
            self.state.scores[self.seat],
            self.state.scores[1 - self.seat],
        ];
        loop {
            let active_before_commands = self.active.clone();
            let ids: Vec<_> = self.active.keys().copied().collect();
            let mut commands = Vec::new();
            let mut finished = Vec::new();
            for id in ids {
                let result = {
                    let job = self.active.get_mut(&id).expect("active macro job");
                    job.command(&self.state, self.seat)
                };
                match result {
                    JobCommand::Command(command) => commands.push((id, command)),
                    JobCommand::Complete => finished.push((id, true)),
                    JobCommand::Invalid => finished.push((id, false)),
                }
            }
            if !finished.is_empty() {
                for (id, job) in active_before_commands {
                    if !finished.iter().any(|(finished_id, _)| *finished_id == id) {
                        self.active.insert(id, job);
                    }
                }
                for (id, complete) in finished {
                    self.active.remove(&id);
                    if complete {
                        self.completed_jobs = self.completed_jobs.saturating_add(1);
                    } else {
                        self.invalidated_jobs = self.invalidated_jobs.saturating_add(1);
                    }
                }
                self.refresh_free_ids();
                let end_scores = [
                    self.state.scores[self.seat],
                    self.state.scores[1 - self.seat],
                ];
                let rewards = [
                    (end_scores[0] - start_scores[0]) as f32 / 100.0,
                    (end_scores[1] - start_scores[1]) as f32 / 100.0,
                ];
                return self.terminal(rewards, rewards[0] - rewards[1]);
            }

            commands.sort_by_key(|(id, _)| *id);
            for (id, command) in &commands {
                if self.active.get(id).is_some_and(|job| job.bank_seed_source) {
                    self.seed_source_pick_commands = self
                        .seed_source_pick_commands
                        .saturating_add(u16::from(command.starts_with("PICK ")));
                    self.seed_source_plant_commands = self
                        .seed_source_plant_commands
                        .saturating_add(u16::from(command.starts_with("PLANT ")));
                    if self
                        .active
                        .get(id)
                        .is_some_and(|job| job.bank_seed_source_lease)
                    {
                        self.seed_source_harvest_commands = self
                            .seed_source_harvest_commands
                            .saturating_add(u16::from(command.starts_with("HARVEST ")));
                        self.seed_source_drop_commands = self
                            .seed_source_drop_commands
                            .saturating_add(u16::from(command.starts_with("DROP ")));
                        self.seed_source_wait_commands = self
                            .seed_source_wait_commands
                            .saturating_add(u16::from(command == "WAIT"));
                    }
                }
                if command.starts_with("DROP ") {
                    let actual_deposit = self
                        .state
                        .units
                        .iter()
                        .find(|unit| unit.id == *id)
                        .expect("depositing macro unit")
                        .carry;
                    let predicted_deposit = self
                        .active
                        .get(id)
                        .expect("depositing macro job")
                        .spec
                        .predicted_deposit;
                    if TRAIN_RESOURCE_SLOTS
                        .iter()
                        .any(|index| actual_deposit[*index] != predicted_deposit[*index])
                    {
                        self.deposit_prediction_failures =
                            self.deposit_prediction_failures.saturating_add(1);
                    }
                }
            }
            let mut ours: Vec<_> = commands
                .iter()
                .map(|(_, command)| command.clone())
                .collect();
            let own_crop_harvests: Vec<_> = commands
                .iter()
                .filter(|(_, command)| command.starts_with("HARVEST "))
                .filter_map(|(id, _)| {
                    let unit = self.state.units.iter().find(|unit| unit.id == *id)?;
                    (self.owners.get(&unit.pos()) == Some(&PlantOwner::Own))
                        .then_some((*id, unit.carry))
                })
                .collect();
            let explicit_source_plants: Vec<_> = commands
                .iter()
                .filter(|(_, command)| command.starts_with("PLANT "))
                .filter_map(|(id, _)| {
                    let job = self.active.get(id)?;
                    job.bank_seed_source
                        .then_some((job.spec.plant_cell?, job.spec.fruit_kind?))
                })
                .collect();
            for (_, command) in &commands {
                if !direct_command_is_valid(&self.state, self.seat, command) {
                    self.invalid_direct_commands = self.invalid_direct_commands.saturating_add(1);
                }
            }
            let before_workers = worker_count(&self.state, self.seat);
            let training = self.affordable_train(self.train_goal);
            if training {
                ours.insert(0, Self::train_command(self.train_goal));
            }
            let theirs = self.opponent.commands(&self.state, 1 - self.seat);
            let had_renewable_receipt = self.own_owned_crop_harvest_units > 0;
            let (failures, own_plants, opponent_plants, ambiguous_plants) =
                apply_with_provenance(&mut self.state, self.seat, &ours, &theirs, &mut self.owners);
            if had_renewable_receipt {
                self.own_reinvested_crops =
                    self.own_reinvested_crops.saturating_add(own_plants as u16);
            }
            for (id, before_carry) in own_crop_harvests {
                let Some(unit) = self.state.units.iter().find(|unit| unit.id == id) else {
                    continue;
                };
                let gained = (0..4)
                    .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                    .sum::<i32>();
                self.own_owned_crop_harvest_units = self
                    .own_owned_crop_harvest_units
                    .saturating_add(gained.clamp(0, u16::MAX as i32) as u16);
            }
            for (cell, kind) in explicit_source_plants {
                let created =
                    self.owners.get(&cell) == Some(&PlantOwner::Own)
                        && self.state.plants.iter().any(|plant| {
                            plant.pos() == cell && plant.plant_type == FRUIT_NAMES[kind]
                        });
                self.explicit_source_creations[kind] =
                    self.explicit_source_creations[kind].saturating_add(u16::from(created));
            }
            self.provenance_failures = self.provenance_failures.saturating_add(failures as u16);
            self.own_created_crops = self.own_created_crops.saturating_add(own_plants as u16);
            self.opponent_created_crops = self
                .opponent_created_crops
                .saturating_add(opponent_plants as u16);
            self.ambiguous_created_crops = self
                .ambiguous_created_crops
                .saturating_add(ambiguous_plants as u16);
            for job in self.active.values_mut() {
                job.age = job.age.saturating_add(1);
            }
            let scores = [
                self.state.scores[self.seat],
                self.state.scores[1 - self.seat],
            ];
            let turn_rewards = [
                (scores[0] - self.previous_scores[0]) as f32 / 100.0,
                (scores[1] - self.previous_scores[1]) as f32 / 100.0,
            ];
            self.returns[0] += turn_rewards[0];
            self.returns[1] += turn_rewards[1];
            self.margin_return += turn_rewards[0] - turn_rewards[1];
            self.previous_scores = scores;
            self.done = self.state.turn > MACRO_TOTAL_TURNS
                || has_stalled(&self.state, &mut self.stall_counter);
            if self.done {
                self.returns = [scores[0] as f32 / 100.0, scores[1] as f32 / 100.0];
                self.margin_return = (scores[0] - scores[1]) as f32 / 100.0;
                let rewards = [
                    (scores[0] - start_scores[0]) as f32 / 100.0,
                    (scores[1] - start_scores[1]) as f32 / 100.0,
                ];
                return self.terminal(rewards, rewards[0] - rewards[1]);
            }
            let after_workers = worker_count(&self.state, self.seat);
            if training && after_workers > before_workers {
                self.successful_trains = self.successful_trains.saturating_add(1);
                self.train_goal = MacroTrainGoal::None;
                self.refresh_free_ids();
                let rewards = [
                    (scores[0] - start_scores[0]) as f32 / 100.0,
                    (scores[1] - start_scores[1]) as f32 / 100.0,
                ];
                return self.terminal(rewards, rewards[0] - rewards[1]);
            }
        }
    }

    pub fn step(&mut self, selected_action: usize) -> MacroTerminal {
        if self.done {
            return self.terminal([0.0; 2], 0.0);
        }
        assert!(
            self.legal_actions().contains(&selected_action),
            "illegal D37 macro action {selected_action} at {:?}",
            self.stage
        );
        self.selected_decisions = self.selected_decisions.saturating_add(1);
        self.action_hash ^= selected_action as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        self.action_hash ^= self.state.turn as u64;
        self.action_hash = self.action_hash.wrapping_mul(0x100000001b3);
        match self.stage {
            MacroDecisionStage::Train => {
                self.train_goal = if selected_action == self.train_action(MacroTrainGoal::None) {
                    MacroTrainGoal::None
                } else if selected_action == self.train_action(MacroTrainGoal::Producer) {
                    MacroTrainGoal::Producer
                } else {
                    MacroTrainGoal::Chopper
                };
                self.stage = MacroDecisionStage::Worker;
                self.free_index = 0;
                if self.free_ids.is_empty() {
                    self.advance_until_boundary()
                } else {
                    self.refresh_candidate_jobs();
                    self.terminal([0.0; 2], 0.0)
                }
            }
            MacroDecisionStage::Worker => {
                let unit_id = self.current_unit_id().expect("worker decision id");
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| unit.id == unit_id)
                    .expect("worker decision unit");
                let spec = self
                    .candidate_jobs
                    .iter()
                    .find(|job| job.action(&self.state, self.seat, unit) == selected_action)
                    .expect("masked macro action has job")
                    .clone();
                self.selected_jobs = self.selected_jobs.saturating_add(1);
                if spec.kind != MacroJobKind::IdleOneTurn {
                    self.selected_nonidle_jobs = self.selected_nonidle_jobs.saturating_add(1);
                }
                if spec.kind == MacroJobKind::Renew {
                    self.selected_renew_jobs = self.selected_renew_jobs.saturating_add(1);
                }
                self.active
                    .insert(unit_id, ActiveJob::new(spec, &self.state));
                self.free_index += 1;
                if self.free_index < self.free_ids.len() {
                    self.refresh_candidate_jobs();
                    self.terminal([0.0; 2], 0.0)
                } else {
                    self.advance_until_boundary()
                }
            }
        }
    }

    fn heuristic_train_action(&self) -> usize {
        let workers = worker_count(&self.state, self.seat);
        if self.state.turn > MACRO_TOTAL_TURNS - 30 {
            self.train_action(MacroTrainGoal::None)
        } else if workers < 2 {
            self.train_action(MacroTrainGoal::Producer)
        } else if workers < MACRO_MAX_WORKERS {
            self.train_action(MacroTrainGoal::Chopper)
        } else {
            self.train_action(MacroTrainGoal::None)
        }
    }

    fn rate_value(job: &MacroJobSpec) -> i32 {
        let owner_bonus = match job.owner {
            Some(PlantOwner::Opponent) => 20_000,
            Some(PlantOwner::Ambiguous) => 10_000,
            _ => 0,
        };
        let renew_bonus = if job.kind == MacroJobKind::Renew {
            15_000
        } else {
            0
        };
        let bank_bonus = if job.kind == MacroJobKind::Bank {
            8_000
        } else {
            0
        };
        1_000 * job.predicted_reward / job.predicted_eta.max(1)
            + owner_bonus
            + renew_bonus
            + bank_bonus
    }

    fn rate_worker_action(&self) -> usize {
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| Some(unit.id) == self.current_unit_id())
            .expect("heuristic macro unit");
        let best = self
            .candidate_jobs
            .iter()
            .min_by_key(|job| {
                let value = Self::rate_value(job);
                (-value, job.predicted_eta, job.kind, job.target)
            })
            .expect("idle macro action exists");
        best.action(&self.state, self.seat, unit)
    }

    fn idle_worker_action(&self) -> usize {
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| Some(unit.id) == self.current_unit_id())
            .expect("idle macro unit");
        self.candidate_jobs
            .iter()
            .find(|job| job.kind == MacroJobKind::IdleOneTurn)
            .expect("idle macro action exists")
            .action(&self.state, self.seat, unit)
    }

    fn action_for_current_unit(&self, job: &MacroJobSpec) -> usize {
        let unit = self
            .state
            .units
            .iter()
            .find(|unit| Some(unit.id) == self.current_unit_id())
            .expect("current macro unit");
        job.action(&self.state, self.seat, unit)
    }

    fn best_deficit_job(&self, deficit: [i32; 6]) -> Option<&MacroJobSpec> {
        self.candidate_jobs
            .iter()
            .filter_map(|job| {
                let reduction = Self::deficit_reduction(job, deficit);
                (reduction > 0).then_some((job, reduction))
            })
            .min_by_key(|(job, reduction)| {
                (
                    -*reduction,
                    job.predicted_eta,
                    usize::from(job.kind != MacroJobKind::Bank),
                    job.kind,
                    job.target,
                    job.plant_cell,
                    job.fruit_kind,
                )
            })
            .map(|(job, _)| job)
    }

    pub fn work_conserving_branch(&self) -> MacroSelectionBranch {
        match self.stage {
            MacroDecisionStage::Train => MacroSelectionBranch::Train,
            MacroDecisionStage::Worker => {
                let workers = worker_count(&self.state, self.seat);
                if workers >= MACRO_MAX_WORKERS
                    || self.train_goal == MacroTrainGoal::None
                    || self.affordable_train(self.train_goal)
                {
                    return MacroSelectionBranch::Rate;
                }
                let deficit = self.train_deficit();
                if self.best_deficit_job(deficit).is_some() {
                    return MacroSelectionBranch::Deficit;
                }
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == self.current_unit_id())
                    .expect("branch macro unit");
                if unit.pos() == self.state.shacks[self.seat] {
                    MacroSelectionBranch::Evacuation
                } else {
                    MacroSelectionBranch::Rate
                }
            }
        }
    }

    pub fn candidate_observation(&self) -> MacroCandidateObservation {
        let actions = self.legal_actions();
        assert!(
            !actions.is_empty(),
            "terminal macro state has no observation"
        );
        assert!(
            actions.len() <= MACRO_MAX_CANDIDATES,
            "macro candidate overflow: {} > {}",
            actions.len(),
            MACRO_MAX_CANDIDATES
        );
        assert_eq!(
            actions.len(),
            actions.iter().copied().collect::<BTreeSet<_>>().len(),
            "macro observation action IDs must be unique"
        );
        let teacher_action = self.work_conserving_deficit_heuristic_action();
        let teacher_index = actions
            .iter()
            .position(|action| *action == teacher_action)
            .expect("D40 teacher action must be legal");
        let branch = self.work_conserving_branch();
        let workers = worker_count(&self.state, self.seat);
        let deficit = self.train_deficit();
        let affordable = self.affordable_train(self.train_goal);
        let current_on_shack = self
            .current_unit_id()
            .and_then(|id| self.state.units.iter().find(|unit| unit.id == id))
            .is_some_and(|unit| unit.pos() == self.state.shacks[self.seat]);
        let any_positive_deficit = self.best_deficit_job(deficit).is_some();
        let mut features = Vec::with_capacity(actions.len());
        for &action in &actions {
            let mut row = [0.0f32; MACRO_CANDIDATE_FEATURES];
            row[0] = 1.0;
            row[1] = self.state.turn as f32 / MACRO_TOTAL_TURNS as f32;
            row[2] = workers as f32 / MACRO_MAX_WORKERS as f32;
            row[3] = self.state.scores[self.seat] as f32 / 400.0;
            row[4] = self.state.scores[1 - self.seat] as f32 / 400.0;
            row[5] = f32::from(self.stage == MacroDecisionStage::Train);
            row[6] = f32::from(self.stage == MacroDecisionStage::Worker);
            row[7 + self.train_goal.action_plane()] = 1.0;
            row[10 + branch as usize] = 1.0;
            row[14] = f32::from(affordable);
            row[15] = f32::from(current_on_shack);
            row[16] = f32::from(any_positive_deficit);

            let job = if self.stage == MacroDecisionStage::Train {
                let goal = if action == self.train_action(MacroTrainGoal::None) {
                    MacroTrainGoal::None
                } else if action == self.train_action(MacroTrainGoal::Producer) {
                    MacroTrainGoal::Producer
                } else {
                    MacroTrainGoal::Chopper
                };
                row[17 + goal.action_plane()] = 1.0;
                None
            } else {
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == self.current_unit_id())
                    .expect("feature macro unit");
                Some(
                    self.candidate_jobs
                        .iter()
                        .find(|job| job.action(&self.state, self.seat, unit) == action)
                        .expect("feature action has macro job"),
                )
            };
            if let Some(job) = job {
                row[20 + job.kind as usize] = 1.0;
                row[26] = job.predicted_eta as f32 / MACRO_TOTAL_TURNS as f32;
                row[27] = job.predicted_reward as f32 / 40.0;
                row[28] = Self::deficit_reduction(job, deficit) as f32 / 20.0;
                row[29] = Self::rate_value(job) as f32 / 50_000.0;
                if let Some(owner) = job.owner {
                    row[30 + owner as usize] = 1.0;
                }
                for (feature, item) in TRAIN_RESOURCE_SLOTS.into_iter().enumerate() {
                    row[34 + feature] = job.predicted_deposit[item] as f32 / 10.0;
                }
                row[43] = job
                    .plant_cell
                    .map(|cell| macro_spatial(cell) as f32 / (MACRO_CELLS - 1) as f32)
                    .unwrap_or(-1.0);
            } else {
                row[43] = -1.0;
            }
            for (feature, item) in TRAIN_RESOURCE_SLOTS.into_iter().enumerate() {
                row[38 + feature] = deficit[item] as f32 / 10.0;
            }
            row[42] = action as f32 / (MACRO_ACTION_SIZE - 1) as f32;
            features.push(row);
        }
        MacroCandidateObservation {
            actions: actions.into_iter().map(|action| action as i32).collect(),
            features,
            teacher_index,
            branch,
        }
    }

    pub fn heuristic_action(&self) -> usize {
        match self.stage {
            MacroDecisionStage::Train => self.heuristic_train_action(),
            MacroDecisionStage::Worker => self.rate_worker_action(),
        }
    }

    pub fn deficit_heuristic_action(&self) -> usize {
        match self.stage {
            MacroDecisionStage::Train => self.heuristic_train_action(),
            MacroDecisionStage::Worker => {
                let workers = worker_count(&self.state, self.seat);
                if workers >= MACRO_MAX_WORKERS
                    || self.train_goal == MacroTrainGoal::None
                    || self.affordable_train(self.train_goal)
                {
                    return self.rate_worker_action();
                }
                let deficit = self.train_deficit();
                let Some(best) = self.best_deficit_job(deficit) else {
                    return self.idle_worker_action();
                };
                self.action_for_current_unit(best)
            }
        }
    }

    pub fn evacuation_deficit_heuristic_action(&self) -> usize {
        match self.stage {
            MacroDecisionStage::Train => self.heuristic_train_action(),
            MacroDecisionStage::Worker => {
                let workers = worker_count(&self.state, self.seat);
                if workers >= MACRO_MAX_WORKERS || self.train_goal == MacroTrainGoal::None {
                    return self.rate_worker_action();
                }
                if self.affordable_train(self.train_goal) {
                    return self.rate_worker_action();
                }
                let deficit = self.train_deficit();
                if let Some(best) = self.best_deficit_job(deficit) {
                    return self.action_for_current_unit(best);
                }
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == self.current_unit_id())
                    .expect("evacuation macro unit");
                if unit.pos() != self.state.shacks[self.seat] {
                    return self.idle_worker_action();
                }
                let Some(best) = self
                    .candidate_jobs
                    .iter()
                    .filter(|job| job.kind != MacroJobKind::IdleOneTurn)
                    .min_by_key(|job| {
                        (
                            job.predicted_eta,
                            job.kind,
                            job.target,
                            job.plant_cell,
                            job.fruit_kind,
                        )
                    })
                else {
                    return self.idle_worker_action();
                };
                self.action_for_current_unit(best)
            }
        }
    }

    pub fn work_conserving_deficit_heuristic_action(&self) -> usize {
        match self.stage {
            MacroDecisionStage::Train => self.heuristic_train_action(),
            MacroDecisionStage::Worker => {
                let workers = worker_count(&self.state, self.seat);
                if workers >= MACRO_MAX_WORKERS || self.train_goal == MacroTrainGoal::None {
                    return self.rate_worker_action();
                }
                if self.affordable_train(self.train_goal) {
                    return self.rate_worker_action();
                }
                let deficit = self.train_deficit();
                if let Some(best) = self.best_deficit_job(deficit) {
                    return self.action_for_current_unit(best);
                }
                let unit = self
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == self.current_unit_id())
                    .expect("work-conserving macro unit");
                if unit.pos() != self.state.shacks[self.seat] {
                    return self.rate_worker_action();
                }
                let Some(best) = self
                    .candidate_jobs
                    .iter()
                    .filter(|job| job.kind != MacroJobKind::IdleOneTurn)
                    .min_by_key(|job| {
                        (
                            job.predicted_eta,
                            job.kind,
                            job.target,
                            job.plant_cell,
                            job.fruit_kind,
                        )
                    })
                else {
                    return self.idle_worker_action();
                };
                self.action_for_current_unit(best)
            }
        }
    }

    pub fn run_heuristic(&mut self) -> MacroTerminal {
        let mut terminal = self.terminal([0.0; 2], 0.0);
        let mut decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(decisions < 5_000, "macro heuristic decision loop");
            terminal = self.step(self.heuristic_action());
        }
        terminal
    }

    pub fn run_deficit_heuristic(&mut self) -> MacroTerminal {
        let mut terminal = self.terminal([0.0; 2], 0.0);
        let mut decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(decisions < 5_000, "macro deficit heuristic decision loop");
            terminal = self.step(self.deficit_heuristic_action());
        }
        terminal
    }

    pub fn run_evacuation_deficit_heuristic(&mut self) -> MacroTerminal {
        let mut terminal = self.terminal([0.0; 2], 0.0);
        let mut decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(
                decisions < 5_000,
                "macro evacuation-deficit heuristic decision loop"
            );
            terminal = self.step(self.evacuation_deficit_heuristic_action());
        }
        terminal
    }

    pub fn run_work_conserving_deficit_heuristic(&mut self) -> MacroTerminal {
        let mut terminal = self.terminal([0.0; 2], 0.0);
        let mut decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(
                decisions < 5_000,
                "macro work-conserving deficit heuristic decision loop"
            );
            terminal = self.step(self.work_conserving_deficit_heuristic_action());
        }
        terminal
    }
}

struct MacroBatchSlot {
    task_index: u64,
    env: CompleteMacroEnv,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct MacroBatchTerminal {
    pub done: u8,
    pub seat: u8,
    pub opponent: u8,
    pub own_workers: u8,
    pub map_seed: i64,
    pub task_index: u64,
    pub own_score: i32,
    pub opponent_score: i32,
    pub successful_trains: u8,
    pub _padding: u8,
    pub own_created_crops: u16,
    pub invalid_direct_commands: u16,
    pub provenance_failures: u16,
    pub deposit_prediction_failures: u16,
    pub invalidated_jobs: u16,
    pub action_hash: u64,
    pub state_hash: u64,
}

pub struct CompleteMacroBatch {
    slots: Vec<MacroBatchSlot>,
    seed_base: i64,
    next_task_index: u64,
}

impl CompleteMacroBatch {
    pub fn new(num_envs: usize, seed_base: i64) -> Self {
        assert!(num_envs > 0);
        let slots = (0..num_envs)
            .map(|task_index| Self::make_slot(seed_base, task_index as u64))
            .collect();
        Self {
            slots,
            seed_base,
            next_task_index: num_envs as u64,
        }
    }

    fn task(seed_base: i64, task_index: u64) -> (i64, usize, usize) {
        let per_map = 2 * MacroOpponentMode::ALL.len() as u64;
        let within_map = task_index % per_map;
        let map_seed = seed_base + (task_index / per_map) as i64;
        let seat = (within_map / MacroOpponentMode::ALL.len() as u64) as usize;
        let opponent = (within_map % MacroOpponentMode::ALL.len() as u64) as usize;
        (map_seed, seat, opponent)
    }

    fn make_slot(seed_base: i64, task_index: u64) -> MacroBatchSlot {
        let (map_seed, seat, opponent) = Self::task(seed_base, task_index);
        MacroBatchSlot {
            task_index,
            env: CompleteMacroEnv::new(map_seed, seat, MacroOpponentMode::from_index(opponent)),
        }
    }

    pub fn len(&self) -> usize {
        self.slots.len()
    }

    pub fn observe(
        &mut self,
        actions: &mut [i32],
        features: &mut [f32],
        counts: &mut [u16],
        teacher_indices: &mut [u16],
        branches: &mut [u8],
        prior_ranks: &mut [u16],
    ) {
        assert_eq!(actions.len(), self.len() * MACRO_MAX_CANDIDATES);
        assert_eq!(
            features.len(),
            self.len() * MACRO_MAX_CANDIDATES * MACRO_CANDIDATE_FEATURES
        );
        assert_eq!(counts.len(), self.len());
        assert_eq!(teacher_indices.len(), self.len());
        assert_eq!(branches.len(), self.len());
        assert_eq!(prior_ranks.len(), self.len() * MACRO_MAX_CANDIDATES);
        actions.fill(-1);
        features.fill(0.0);
        prior_ranks.fill(u16::MAX);
        self.slots
            .par_iter_mut()
            .zip(actions.par_chunks_mut(MACRO_MAX_CANDIDATES))
            .zip(features.par_chunks_mut(MACRO_MAX_CANDIDATES * MACRO_CANDIDATE_FEATURES))
            .zip(prior_ranks.par_chunks_mut(MACRO_MAX_CANDIDATES))
            .zip(counts.par_iter_mut())
            .zip(teacher_indices.par_iter_mut())
            .zip(branches.par_iter_mut())
            .for_each(
                |(
                    (((((slot, action_chunk), feature_chunk), rank_chunk), count), teacher),
                    branch,
                )| {
                    let observation = slot.env.candidate_observation();
                    *count = observation.actions.len() as u16;
                    *teacher = observation.teacher_index as u16;
                    *branch = observation.branch as u8;
                    action_chunk[..observation.actions.len()].copy_from_slice(&observation.actions);
                    let order = crate::d41b_prior_kernel::exact_prior_order(
                        &observation.features,
                        &observation.actions,
                        observation.branch as u8,
                    );
                    assert_eq!(order[0], observation.teacher_index);
                    for (rank, candidate) in order.into_iter().enumerate() {
                        rank_chunk[candidate] = rank as u16;
                    }
                    for (candidate, row) in observation.features.iter().enumerate() {
                        let base = candidate * MACRO_CANDIDATE_FEATURES;
                        feature_chunk[base..base + MACRO_CANDIDATE_FEATURES].copy_from_slice(row);
                    }
                },
            );
    }

    pub fn step(
        &mut self,
        selected_actions: &[i32],
        rewards: &mut [f32],
        terminals: &mut [MacroBatchTerminal],
    ) {
        assert_eq!(selected_actions.len(), self.len());
        assert_eq!(rewards.len(), self.len());
        assert_eq!(terminals.len(), self.len());
        for terminal in terminals.iter_mut() {
            *terminal = MacroBatchTerminal::default();
        }
        let results: Vec<_> = self
            .slots
            .par_iter_mut()
            .zip(selected_actions.par_iter())
            .map(|(slot, action)| slot.env.step(*action as usize))
            .collect();
        for (index, result) in results.into_iter().enumerate() {
            let slot = &mut self.slots[index];
            rewards[index] = result.margin_reward;
            if result.done {
                terminals[index] = MacroBatchTerminal {
                    done: 1,
                    seat: slot.env.seat as u8,
                    opponent: slot.env.opponent_mode.id(),
                    own_workers: result.own_workers,
                    map_seed: slot.env.map_seed,
                    task_index: slot.task_index,
                    own_score: result.own_score,
                    opponent_score: result.opponent_score,
                    successful_trains: result.successful_trains,
                    _padding: 0,
                    own_created_crops: result.own_created_crops,
                    invalid_direct_commands: result.invalid_direct_commands,
                    provenance_failures: result.provenance_failures,
                    deposit_prediction_failures: result.deposit_prediction_failures,
                    invalidated_jobs: result.invalidated_jobs,
                    action_hash: result.action_hash,
                    state_hash: result.state_hash,
                };
                let task_index = self.next_task_index;
                self.next_task_index += 1;
                self.slots[index] = Self::make_slot(self.seed_base, task_index);
            }
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_macro_max_candidates() -> usize {
    MACRO_MAX_CANDIDATES
}

#[no_mangle]
pub extern "C" fn tf_macro_candidate_features() -> usize {
    MACRO_CANDIDATE_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_macro_terminal_size() -> usize {
    std::mem::size_of::<MacroBatchTerminal>()
}

#[no_mangle]
pub extern "C" fn tf_macro_create(num_envs: usize, seed_base: i64) -> *mut CompleteMacroBatch {
    if num_envs == 0 || seed_base == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(CompleteMacroBatch::new(num_envs, seed_base)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_macro_destroy(handle: *mut CompleteMacroBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_macro_observe(
    handle: *mut CompleteMacroBatch,
    actions: *mut i32,
    features: *mut f32,
    counts: *mut u16,
    teacher_indices: *mut u16,
    branches: *mut u8,
    prior_ranks: *mut u16,
) -> i32 {
    if handle.is_null()
        || actions.is_null()
        || features.is_null()
        || counts.is_null()
        || teacher_indices.is_null()
        || branches.is_null()
        || prior_ranks.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let action_slice = std::slice::from_raw_parts_mut(actions, batch.len() * MACRO_MAX_CANDIDATES);
    let feature_slice = std::slice::from_raw_parts_mut(
        features,
        batch.len() * MACRO_MAX_CANDIDATES * MACRO_CANDIDATE_FEATURES,
    );
    let count_slice = std::slice::from_raw_parts_mut(counts, batch.len());
    let teacher_slice = std::slice::from_raw_parts_mut(teacher_indices, batch.len());
    let branch_slice = std::slice::from_raw_parts_mut(branches, batch.len());
    let rank_slice =
        std::slice::from_raw_parts_mut(prior_ranks, batch.len() * MACRO_MAX_CANDIDATES);
    batch.observe(
        action_slice,
        feature_slice,
        count_slice,
        teacher_slice,
        branch_slice,
        rank_slice,
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_macro_step(
    handle: *mut CompleteMacroBatch,
    selected_actions: *const i32,
    actions: *mut i32,
    features: *mut f32,
    counts: *mut u16,
    teacher_indices: *mut u16,
    branches: *mut u8,
    prior_ranks: *mut u16,
    rewards: *mut f32,
    terminals: *mut MacroBatchTerminal,
) -> i32 {
    if handle.is_null()
        || selected_actions.is_null()
        || actions.is_null()
        || features.is_null()
        || counts.is_null()
        || teacher_indices.is_null()
        || branches.is_null()
        || prior_ranks.is_null()
        || rewards.is_null()
        || terminals.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let selected_slice = std::slice::from_raw_parts(selected_actions, batch.len());
    let reward_slice = std::slice::from_raw_parts_mut(rewards, batch.len());
    let terminal_slice = std::slice::from_raw_parts_mut(terminals, batch.len());
    batch.step(selected_slice, reward_slice, terminal_slice);
    tf_macro_observe(
        handle,
        actions,
        features,
        counts,
        teacher_indices,
        branches,
        prior_ranks,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn initial_macro_stage_has_global_and_worker_actions() {
        let mut env = CompleteMacroEnv::new(9_600_000, 0, MacroOpponentMode::Resident);
        let train = env.legal_actions();
        assert_eq!(train.len(), 3);
        assert_eq!(env.stage(), MacroDecisionStage::Train);
        let result = env.step(env.train_action(MacroTrainGoal::Producer));
        assert!(!result.done);
        assert_eq!(env.stage(), MacroDecisionStage::Worker);
        let jobs = env.jobs_for_current_unit();
        assert!(!jobs.is_empty());
        assert!(jobs.iter().any(|job| job.kind == MacroJobKind::IdleOneTurn));
        let actions = env.legal_actions();
        assert_eq!(
            actions.len(),
            actions.iter().copied().collect::<BTreeSet<_>>().len()
        );
    }

    #[test]
    fn idle_is_a_complete_one_turn_job_without_fallback() {
        let mut env = CompleteMacroEnv::new(9_600_001, 1, MacroOpponentMode::CompactGold);
        let turn = env.state.turn;
        let no_train = env.train_action(MacroTrainGoal::None);
        env.step(no_train);
        let unit = env
            .state
            .units
            .iter()
            .find(|unit| Some(unit.id) == env.current_unit_id())
            .unwrap();
        let idle = macro_action(MacroJobKind::IdleOneTurn.action_plane(), unit.pos());
        let result = env.step(idle);
        assert!(!result.done);
        assert_eq!(env.state.turn, turn + 1);
        assert_eq!(env.completed_jobs, 1);
        assert_eq!(env.stage(), MacroDecisionStage::Train);
    }

    #[test]
    fn heuristic_is_deterministic_legal_and_telescoping() {
        for seed in 9_600_000..9_600_003 {
            let mut left = CompleteMacroEnv::new(seed, 0, MacroOpponentMode::SilverBoss);
            let mut right = CompleteMacroEnv::new(seed, 0, MacroOpponentMode::SilverBoss);
            let a = left.run_heuristic();
            let b = right.run_heuristic();
            assert_eq!(a, b, "seed {seed}");
            assert_eq!(a.invalid_direct_commands, 0, "seed {seed}");
            assert_eq!(a.provenance_failures, 0, "seed {seed}");
            assert!(a.own_workers <= MACRO_MAX_WORKERS as u8, "seed {seed}");
            assert!((100.0 * a.own_return - a.own_score as f32).abs() < 1e-4);
            assert!((100.0 * a.opponent_return - a.opponent_score as f32).abs() < 1e-4);
            assert!(
                (100.0 * a.margin_return - (a.own_score - a.opponent_score) as f32).abs() < 1e-4
            );
        }
    }

    #[test]
    fn cloned_opponents_continue_byte_exactly_in_every_family() {
        for (index, mode) in MacroOpponentMode::ALL.into_iter().enumerate() {
            let mut original = CompleteMacroEnv::new(9_843_000, index % 2, mode);
            for _ in 0..40 {
                let action = original.work_conserving_deficit_heuristic_action();
                assert!(!original.step(action).done);
            }
            let mut snapshot = original.clone();
            assert_eq!(
                original.run_work_conserving_deficit_heuristic(),
                snapshot.run_work_conserving_deficit_heuristic(),
                "clone continuation for {}",
                mode.label()
            );
        }
    }

    #[test]
    fn renew_prediction_spends_the_harvested_seed() {
        let mut paired_jobs = 0usize;
        for seed in 9_630_000..9_630_016 {
            for seat in 0..2 {
                let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
                env.step(env.train_action(MacroTrainGoal::Producer));
                let jobs = env.jobs_for_current_unit();
                for renew in jobs.iter().filter(|job| job.kind == MacroJobKind::Renew) {
                    let harvest = jobs
                        .iter()
                        .find(|job| {
                            job.kind == MacroJobKind::HarvestBank
                                && job.target == renew.target
                                && job.fruit_kind == renew.fruit_kind
                        })
                        .expect("renew has paired harvest-bank job");
                    let kind = renew.fruit_kind.expect("renew fruit kind");
                    assert_eq!(
                        harvest.predicted_deposit[kind] - 1,
                        renew.predicted_deposit[kind]
                    );
                    for other in 0..6 {
                        if other != kind {
                            assert_eq!(
                                harvest.predicted_deposit[other],
                                renew.predicted_deposit[other]
                            );
                        }
                    }
                    paired_jobs += 1;
                }
            }
        }
        assert!(paired_jobs > 0, "fresh D38 panel has paired renewable jobs");
    }

    #[test]
    fn deficit_teacher_prefers_banking_the_missing_seed() {
        for seed in 9_630_000..9_630_016 {
            for seat in 0..2 {
                let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
                env.step(env.train_action(MacroTrainGoal::Producer));
                let Some(kind) = env
                    .candidate_jobs
                    .iter()
                    .filter(|job| job.kind == MacroJobKind::Renew)
                    .filter_map(|job| job.fruit_kind)
                    .find(|kind| *kind < 3)
                else {
                    continue;
                };
                let mut inventory = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
                if env.state.iron.is_empty() {
                    inventory[IRON] = 0;
                }
                inventory[kind] -= 1;
                env.state.inventories[seat] = inventory;
                let selected = env.deficit_heuristic_action();
                let unit = env
                    .state
                    .units
                    .iter()
                    .find(|unit| Some(unit.id) == env.current_unit_id())
                    .unwrap();
                let job = env
                    .candidate_jobs
                    .iter()
                    .find(|job| job.action(&env.state, seat, unit) == selected)
                    .unwrap();
                assert_eq!(job.kind, MacroJobKind::HarvestBank);
                assert_eq!(job.fruit_kind, Some(kind));
                return;
            }
        }
        panic!("fresh D38 panel has no renewable training fruit");
    }

    #[test]
    fn deficit_heuristic_is_deterministic_clean_and_telescoping() {
        for seed in 9_630_000..9_630_002 {
            let seat = (seed as usize) % 2;
            let mut left = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let mut right = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let a = left.run_deficit_heuristic();
            let b = right.run_deficit_heuristic();
            assert_eq!(a, b, "seed {seed}");
            assert_eq!(a.invalid_direct_commands, 0, "seed {seed}");
            assert_eq!(a.provenance_failures, 0, "seed {seed}");
            assert_eq!(a.deposit_prediction_failures, 0, "seed {seed}");
            assert!(a.own_workers <= MACRO_MAX_WORKERS as u8, "seed {seed}");
            assert!((100.0 * a.own_return - a.own_score as f32).abs() < 1e-4);
            assert!((100.0 * a.opponent_return - a.opponent_score as f32).abs() < 1e-4);
            assert!(
                (100.0 * a.margin_return - (a.own_score - a.opponent_score) as f32).abs() < 1e-4
            );
        }
    }

    #[test]
    fn evacuation_teacher_clears_a_funded_spawn_and_trains() {
        for seed in 9_650_000..9_650_016 {
            let seat = 0usize;
            let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
            let cost = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
            let inventory = env.state.inventories[seat];
            if TRAIN_RESOURCE_SLOTS
                .iter()
                .any(|index| inventory[*index] < cost[*index])
            {
                continue;
            }
            env.step(env.train_action(MacroTrainGoal::Producer));
            let unit = env
                .state
                .units
                .iter()
                .find(|unit| Some(unit.id) == env.current_unit_id())
                .unwrap();
            assert_eq!(unit.pos(), env.state.shacks[seat]);
            let selected = env.evacuation_deficit_heuristic_action();
            let job = env
                .candidate_jobs
                .iter()
                .find(|job| job.action(&env.state, seat, unit) == selected)
                .unwrap();
            assert_ne!(job.kind, MacroJobKind::IdleOneTurn);
            let boundary = env.step(selected);
            assert_eq!(boundary.successful_trains, 1);
            assert_eq!(boundary.own_workers, 2);
            return;
        }
        panic!("fresh D39 panel has no initially funded producer");
    }

    #[test]
    fn deficit_ablation_idles_on_the_same_funded_spawn() {
        for seed in 9_650_000..9_650_016 {
            let seat = 0usize;
            let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
            let cost = training_cost(1, MacroTrainGoal::Producer.spec().unwrap());
            let inventory = env.state.inventories[seat];
            if TRAIN_RESOURCE_SLOTS
                .iter()
                .any(|index| inventory[*index] < cost[*index])
            {
                continue;
            }
            env.step(env.train_action(MacroTrainGoal::Producer));
            let selected = env.deficit_heuristic_action();
            let unit = env
                .state
                .units
                .iter()
                .find(|unit| Some(unit.id) == env.current_unit_id())
                .unwrap();
            let job = env
                .candidate_jobs
                .iter()
                .find(|job| job.action(&env.state, seat, unit) == selected)
                .unwrap();
            assert_eq!(job.kind, MacroJobKind::IdleOneTurn);
            return;
        }
        panic!("fresh D39 panel has no initially funded producer");
    }

    #[test]
    fn evacuation_teacher_is_deterministic_clean_and_telescoping() {
        for seed in 9_650_000..9_650_002 {
            let seat = (seed as usize) % 2;
            let mut left = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let mut right = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let a = left.run_evacuation_deficit_heuristic();
            let b = right.run_evacuation_deficit_heuristic();
            assert_eq!(a, b, "seed {seed}");
            assert_eq!(a.invalid_direct_commands, 0, "seed {seed}");
            assert_eq!(a.provenance_failures, 0, "seed {seed}");
            assert_eq!(a.deposit_prediction_failures, 0, "seed {seed}");
            assert!(a.own_workers <= MACRO_MAX_WORKERS as u8, "seed {seed}");
            assert!((100.0 * a.own_return - a.own_score as f32).abs() < 1e-4);
            assert!((100.0 * a.opponent_return - a.opponent_score as f32).abs() < 1e-4);
            assert!(
                (100.0 * a.margin_return - (a.own_score - a.opponent_score) as f32).abs() < 1e-4
            );
        }
    }

    #[test]
    fn work_conserving_teacher_replaces_a_nonblocking_deficit_idle() {
        for seed in 9_670_000..9_670_016 {
            let seat = 0usize;
            let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
            let mut terminal = MacroTerminal::default();
            for _ in 0..2_000 {
                if terminal.done {
                    break;
                }
                if env.stage() == MacroDecisionStage::Worker
                    && env.train_goal() != MacroTrainGoal::None
                {
                    let unit = env
                        .state
                        .units
                        .iter()
                        .find(|unit| Some(unit.id) == env.current_unit_id())
                        .unwrap();
                    if unit.pos() != env.state.shacks[seat] {
                        let ablation = env.evacuation_deficit_heuristic_action();
                        let ablation_job = env
                            .candidate_jobs
                            .iter()
                            .find(|job| job.action(&env.state, seat, unit) == ablation)
                            .unwrap();
                        if ablation_job.kind == MacroJobKind::IdleOneTurn {
                            let selected = env.work_conserving_deficit_heuristic_action();
                            let selected_job = env
                                .candidate_jobs
                                .iter()
                                .find(|job| job.action(&env.state, seat, unit) == selected)
                                .unwrap();
                            assert_ne!(selected_job.kind, MacroJobKind::IdleOneTurn);
                            return;
                        }
                    }
                }
                terminal = env.step(env.evacuation_deficit_heuristic_action());
            }
        }
        panic!("fresh D40 panel has no nonblocking deficit idle");
    }

    #[test]
    fn work_conserving_teacher_is_deterministic_clean_and_telescoping() {
        for seed in 9_670_000..9_670_002 {
            let seat = (seed as usize) % 2;
            let mut left = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let mut right = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::SilverBoss);
            let a = left.run_work_conserving_deficit_heuristic();
            let b = right.run_work_conserving_deficit_heuristic();
            assert_eq!(a, b, "seed {seed}");
            assert_eq!(a.invalid_direct_commands, 0, "seed {seed}");
            assert_eq!(a.provenance_failures, 0, "seed {seed}");
            assert_eq!(a.deposit_prediction_failures, 0, "seed {seed}");
            assert!(a.own_workers <= MACRO_MAX_WORKERS as u8, "seed {seed}");
            assert!((100.0 * a.own_return - a.own_score as f32).abs() < 1e-4);
            assert!((100.0 * a.opponent_return - a.opponent_score as f32).abs() < 1e-4);
            assert!(
                (100.0 * a.margin_return - (a.own_score - a.opponent_score) as f32).abs() < 1e-4
            );
        }
    }

    #[test]
    fn d41_candidate_features_are_deterministic_finite_and_teacher_legal() {
        let mut left = CompleteMacroEnv::new(9_710_000, 0, MacroOpponentMode::GoldAdaptive);
        let mut right = CompleteMacroEnv::new(9_710_000, 0, MacroOpponentMode::GoldAdaptive);
        let mut terminal = MacroTerminal::default();
        let mut decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(decisions < 5_000);
            let a = left.candidate_observation();
            let b = right.candidate_observation();
            assert_eq!(a.actions, b.actions);
            assert_eq!(a.features, b.features);
            assert_eq!(a.teacher_index, b.teacher_index);
            assert_eq!(a.branch, b.branch);
            assert!(a.actions.len() <= MACRO_MAX_CANDIDATES);
            assert!(a.teacher_index < a.actions.len());
            assert!(a.features.iter().flatten().all(|value| value.is_finite()));
            assert_eq!(
                crate::d41b_prior_kernel::exact_prior_order(
                    &a.features,
                    &a.actions,
                    a.branch as u8,
                )[0],
                a.teacher_index,
            );
            let action = a.actions[a.teacher_index] as usize;
            assert_eq!(action, left.work_conserving_deficit_heuristic_action());
            terminal = left.step(action);
            assert_eq!(terminal, right.step(action));
        }
    }

    #[test]
    fn d42_context_features_are_exact_finite_and_compact() {
        assert_eq!(D42_SHARED_CONTEXT_FEATURES, 46);
        assert_eq!(D42_JOB_CONTEXT_FEATURES, 16);
        assert_eq!(D42_COMBINED_FEATURES, 194);
        let mut left = CompleteMacroEnv::new(9_773_000, 0, MacroOpponentMode::GoldAdaptive);
        let mut right = CompleteMacroEnv::new(9_773_000, 0, MacroOpponentMode::GoldAdaptive);
        let mut terminal = MacroTerminal::default();
        let mut checked = 0usize;
        for _ in 0..5_000 {
            if terminal.done {
                break;
            }
            let a = left.candidate_observation();
            let b = right.candidate_observation();
            assert_eq!(a.actions, b.actions);
            if left.stage() == MacroDecisionStage::Worker && a.actions.len() >= 2 {
                let shared_a = left.d42_shared_context();
                let shared_b = right.d42_shared_context();
                assert_eq!(shared_a, shared_b);
                assert!(shared_a.iter().all(|value| value.is_finite()));
                let order = crate::d41b_prior_kernel::exact_prior_order(
                    &a.features,
                    &a.actions,
                    a.branch as u8,
                );
                for index in order.into_iter().take(2) {
                    let context_a = left.d42_job_context(a.actions[index]);
                    let context_b = right.d42_job_context(b.actions[index]);
                    assert_eq!(context_a, context_b);
                    assert!(context_a.iter().all(|value| value.is_finite()));
                    assert!((0.0..=1.0).contains(&context_a[0]));
                    assert!((0.0..=1.0).contains(&context_a[1]));
                }
                checked += 1;
            }
            let action = a.actions[a.teacher_index] as usize;
            terminal = left.step(action);
            assert_eq!(terminal, right.step(action));
        }
        assert!(checked > 10);
    }

    #[test]
    fn d41_batch_reproduces_direct_teacher_episode_exactly() {
        let seed = 9_711_000;
        let mut batch = CompleteMacroBatch::new(1, seed);
        let mut direct = CompleteMacroEnv::new(seed, 0, MacroOpponentMode::Resident);
        let mut actions = vec![-1; MACRO_MAX_CANDIDATES];
        let mut features = vec![0.0; MACRO_MAX_CANDIDATES * MACRO_CANDIDATE_FEATURES];
        let mut counts = vec![0u16; 1];
        let mut teacher_indices = vec![0u16; 1];
        let mut branches = vec![0u8; 1];
        let mut prior_ranks = vec![u16::MAX; MACRO_MAX_CANDIDATES];
        let mut rewards = vec![0.0f32; 1];
        let mut terminals = vec![MacroBatchTerminal::default(); 1];
        for _ in 0..5_000 {
            batch.observe(
                &mut actions,
                &mut features,
                &mut counts,
                &mut teacher_indices,
                &mut branches,
                &mut prior_ranks,
            );
            assert_eq!(prior_ranks[teacher_indices[0] as usize], 0);
            let selected = actions[teacher_indices[0] as usize];
            assert_eq!(
                selected as usize,
                direct.work_conserving_deficit_heuristic_action()
            );
            let direct_terminal = direct.step(selected as usize);
            batch.step(&[selected], &mut rewards, &mut terminals);
            assert!((rewards[0] - direct_terminal.margin_reward).abs() < 1e-6);
            if direct_terminal.done {
                let terminal = terminals[0];
                assert_eq!(terminal.done, 1);
                assert_eq!(terminal.map_seed, seed);
                assert_eq!(terminal.task_index, 0);
                assert_eq!(terminal.own_score, direct_terminal.own_score);
                assert_eq!(terminal.opponent_score, direct_terminal.opponent_score);
                assert_eq!(terminal.own_workers, direct_terminal.own_workers);
                assert_eq!(terminal.action_hash, direct_terminal.action_hash);
                assert_eq!(terminal.state_hash, direct_terminal.state_hash);
                return;
            }
            assert_eq!(terminals[0].done, 0);
        }
        panic!("D41 batch teacher episode did not terminate");
    }

    #[test]
    fn random_boundary_scheduler_does_not_livelock() {
        fn splitmix64(state: &mut u64) -> u64 {
            *state = state.wrapping_add(0x9e3779b97f4a7c15);
            let mut value = *state;
            value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
            value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
            value ^ (value >> 31)
        }

        let seed = 9_630_006i64;
        let seat = 1usize;
        let opponent = 1usize;
        let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::from_index(opponent));
        let mut random_state = seed as u64
            ^ (seat as u64).wrapping_mul(0xd6e8feb86659fd93)
            ^ (opponent as u64).wrapping_mul(0xa0761d6478bd642f)
            ^ 0x4433375f72616e64;
        let mut terminal = MacroTerminal::default();
        let mut decisions = 0usize;
        let mut last_turn = env.state.turn;
        let mut stagnant_decisions = 0usize;
        while !terminal.done {
            decisions += 1;
            assert!(decisions <= 5_000);
            let legal = env.legal_actions();
            let action = legal[splitmix64(&mut random_state) as usize % legal.len()];
            terminal = env.step(action);
            if env.state.turn == last_turn {
                stagnant_decisions += 1;
            } else {
                last_turn = env.state.turn;
                stagnant_decisions = 0;
            }
            assert!(stagnant_decisions <= 16, "turn {last_turn}");
        }
        assert_eq!(terminal.turn, MACRO_TOTAL_TURNS as u16 + 1);
    }

    #[test]
    fn explicit_bank_seed_source_is_transactional_and_returns_to_boundary() {
        let mut env = CompleteMacroEnv::new(9_830_002, 0, MacroOpponentMode::Resident);
        let train = env.candidate_observation();
        env.step(train.actions[train.teacher_index] as usize);
        let worker = env.candidate_observation();
        env.step(worker.actions[worker.teacher_index] as usize);
        assert_eq!(env.stage(), MacroDecisionStage::Train);
        assert_eq!(env.train_goal(), MacroTrainGoal::Producer);
        let crops_before = env.own_created_crops;
        let plum_before = env.state.inventories[env.seat][0];

        let outcome = env
            .install_bank_seed_source(0)
            .expect("eligible deposited PLUM source");

        assert!(!outcome.terminal.done);
        assert_eq!(outcome.fruit_kind, 0);
        assert_eq!(outcome.pick_commands, 1);
        assert_eq!(outcome.plant_commands, 1);
        assert!(outcome.end_turn > outcome.start_turn);
        assert_eq!(env.stage(), MacroDecisionStage::Train);
        assert_eq!(env.train_goal(), MacroTrainGoal::Producer);
        assert_eq!(env.state.inventories[env.seat][0], plum_before - 1);
        assert_eq!(env.own_created_crops, crops_before + 1);
        assert_eq!(outcome.terminal.invalid_direct_commands, 0);
        assert_eq!(outcome.terminal.provenance_failures, 0);
    }

    #[test]
    fn explicit_bank_seed_source_surplus_lease_fails_cleanly_if_root_is_lost() {
        let mut env = CompleteMacroEnv::new(9_830_002, 0, MacroOpponentMode::Resident);
        let train = env.candidate_observation();
        env.step(train.actions[train.teacher_index] as usize);
        let worker = env.candidate_observation();
        env.step(worker.actions[worker.teacher_index] as usize);
        let plum_before = env.state.inventories[env.seat][0];

        let outcome = env
            .install_bank_seed_source_surplus_lease(0)
            .expect("eligible deposited PLUM surplus lease");

        assert_eq!(outcome.pick_commands, 1);
        assert_eq!(outcome.plant_commands, 1);
        assert_eq!(outcome.harvest_commands, 1);
        assert_eq!(outcome.drop_commands, 0);
        assert_eq!(env.state.inventories[env.seat][0], plum_before - 1);
        assert_eq!(outcome.terminal.invalidated_jobs, 1);
        assert_eq!(outcome.terminal.invalid_direct_commands, 0);
        assert_eq!(outcome.terminal.provenance_failures, 0);
        assert_eq!(outcome.terminal.deposit_prediction_failures, 0);
        assert_eq!(env.stage(), MacroDecisionStage::Train);
    }

    #[test]
    fn provenance_stays_complete_across_heuristic_episode() {
        let mut env = CompleteMacroEnv::new(9_600_007, 1, MacroOpponentMode::GoldAdaptive);
        let result = env.run_heuristic();
        assert!(result.done);
        assert_eq!(result.provenance_failures, 0);
        let live: BTreeSet<_> = env.state.plants.iter().map(|plant| plant.pos()).collect();
        assert_eq!(live, env.owners.keys().copied().collect());
    }
}
