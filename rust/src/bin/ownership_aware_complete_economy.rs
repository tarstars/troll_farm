//! Fresh closed-loop panel for race-conditioned ownership-aware farm denial.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeSet, HashMap, HashSet, VecDeque};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{
    has_stalled, step, training_cost, APPLE, BANANA, IRON, LEMON, PLUM, WOOD,
};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::strategies::capacity_separated_denial::{
    CapacitySeparatedDenial, CapacitySeparatedTelemetry,
};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::ownership_aware_farm::{OwnershipAwareFarm, OwnershipTelemetry};
use troll_farm::strategies::prefruit_interruption::{PreFruitInterruption, PreFruitTelemetry};
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const FRUIT_NAMES: [&str; 4] = ["plum", "lemon", "apple", "banana"];
const ORIGIN_NAMES: [&str; 4] = ["natural", "ours", "opponent", "unknown"];
const OPPONENTS: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Origin {
    Natural = 0,
    Ours = 1,
    Opponent = 2,
    Unknown = 3,
}

#[derive(Clone, Copy, Default)]
struct Attribution {
    wood: [[i32; 4]; 2],
    fruit: [[[i32; 4]; 4]; 2],
    successful_plants: [usize; 2],
    successful_plants_by_kind: [[usize; 4]; 2],
    plant_commands_by_kind: [[usize; 4]; 2],
    ambiguous_births: usize,
}

impl Attribution {
    fn add_wood(&mut self, collector: usize, origin: Origin, amount: i32) {
        self.wood[collector][origin as usize] += amount;
    }

    fn add_fruit(&mut self, collector: usize, origin: Origin, kind: usize, amount: i32) {
        self.fruit[collector][origin as usize][kind] += amount;
    }

    fn total_wood(&self) -> i32 {
        self.wood.iter().flatten().sum()
    }

    fn assigned_wood(&self) -> i32 {
        self.total_wood() - self.wood[0][3] - self.wood[1][3]
    }

    fn total_fruit(&self) -> i32 {
        self.fruit.iter().flatten().flatten().sum()
    }

    fn assigned_fruit(&self) -> i32 {
        self.total_fruit()
            - self.fruit[0][Origin::Unknown as usize].iter().sum::<i32>()
            - self.fruit[1][Origin::Unknown as usize].iter().sum::<i32>()
    }
}

fn fruit_index(name: &str) -> Option<usize> {
    match name {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}

fn top_farm() -> GoldElite {
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

fn opponent(model: usize) -> Box<dyn Strategy> {
    match model {
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

enum Policy {
    Resident(SecureOrchardBot),
    TaskMarketOrchard(TaskMarketOrchardResident),
    FreshHarvestRegeneration(FreshHarvestRegenerationResident),
    BananaSeedFactory(BananaSeedFactoryResident),
    Farm(GoldElite),
    Ownership(OwnershipAwareFarm),
    ResidentChopper(ResidentChopperHybrid),
    PreFruit(PreFruitInterruption),
    CapacitySeparated(CapacitySeparatedDenial),
    LineageCollapse(LineageCollapseResident),
}

#[derive(Clone, Copy, Default)]
struct PanelTelemetry {
    opponent_crops_seen: usize,
    active_opponent_crops: usize,
    activation_turns: usize,
    first_activation_turn: Option<i32>,
    base_command_mismatches: usize,
    selected_targets: usize,
    targets_disappeared_before_fruit: usize,
    targets_fruited_after_selection: usize,
    capacity_ready_turns: usize,
    capacity_separation_violations: usize,
    copied_verbs: [usize; 7],
    entry_state_violations: usize,
    forbidden_post_entry_commands: usize,
    post_entry_commands: usize,
    lineage_recovery_turns: usize,
    entry_banked_banana: i32,
    entry_carried_banana: i32,
    entry_crop_banana_fruits: i32,
    entry_opponent_banana_crops: usize,
    entry_own_score: i32,
    entry_opponent_score: i32,
    entry_margin: i32,
    orchard_activation_turn: Option<i32>,
    orchard_seed_repaid_turn: Option<i32>,
    orchard_market_turns: usize,
    orchard_offers: usize,
    orchard_selections: usize,
    orchard_harvest_selections: usize,
    orchard_first_selection_turn: Option<i32>,
    orchard_forced_setup_actions: usize,
    orchard_premarket_mismatches: usize,
    fresh_harvest_commitments: usize,
    fresh_harvest_first_turn: Option<i32>,
    fresh_harvest_successful_plants: usize,
    fresh_harvest_precommit_mismatches: usize,
    fresh_harvest_shadow_divergence_turns: usize,
    banana_factory_active: usize,
    banana_factory_activation_turn: Option<i32>,
    banana_factory_selector_decided: usize,
    banana_factory_selector_selected: usize,
    banana_factory_initial_budget: i32,
    banana_factory_bootstrap_attempts: usize,
    banana_factory_bootstrap_successes: usize,
    banana_factory_reserve_promotions: usize,
    banana_factory_reserve_losses: usize,
    banana_factory_harvest_selections: usize,
    banana_factory_harvest_successes: usize,
    banana_factory_bank_harvest_selections: usize,
    banana_factory_bank_harvest_successes: usize,
    banana_factory_conversion_harvest_selections: usize,
    banana_factory_conversion_harvest_successes: usize,
    banana_factory_opponent_crop_policy_selections: usize,
    banana_factory_trained_opponent_crop_selections: usize,
    banana_factory_renewable_plant_attempts: usize,
    banana_factory_renewable_plant_successes: usize,
    banana_factory_trained_role_rewrites: usize,
    banana_factory_trained_forbidden_commands: usize,
    banana_factory_tracked_live_crops: usize,
    banana_factory_worker_three_bridge_funding_turns: usize,
    banana_factory_worker_three_bridge_fruit_harvest_selections: [usize; 3],
    banana_factory_worker_three_bridge_fruit_harvest_successes: [usize; 3],
    banana_factory_worker_three_bridge_iron_mine_selections: usize,
    banana_factory_worker_three_bridge_iron_mine_successes: usize,
    banana_factory_worker_three_bridge_train_attempts: usize,
    banana_factory_worker_three_bridge_train_successes: usize,
    banana_factory_worker_three_bridge_trained_turn: Option<i32>,
    banana_factory_worker_three_bridge_forbidden_commands: usize,
    banana_factory_worker_three_bridge_post_training_commands: usize,
    banana_factory_preactivation_mismatches: usize,
    banana_factory_shadow_divergence_turns: usize,
    banana_factory_initial_plants: i32,
    banana_factory_initial_ripe_plants: i32,
    banana_factory_initial_fruits: i32,
    banana_factory_initial_banana_plants: i32,
    banana_factory_initial_banana_fruits: i32,
    banana_factory_initial_shack_distance: i32,
    banana_factory_activation_own_score: i32,
    banana_factory_activation_opponent_score: i32,
    banana_factory_activation_own_banked_fruit: i32,
    banana_factory_activation_opponent_banked_fruit: i32,
    banana_factory_activation_opponent_banana: i32,
    banana_factory_activation_opponent_iron: i32,
    banana_factory_activation_opponent_wood: i32,
    banana_factory_activation_opponent_workers: i32,
    banana_factory_activation_opponent_ms_sum: i32,
    banana_factory_activation_opponent_cc_sum: i32,
    banana_factory_activation_opponent_hp_sum: i32,
    banana_factory_activation_opponent_chop_sum: i32,
    banana_factory_activation_opponent_ms_max: i32,
    banana_factory_activation_opponent_cc_max: i32,
    banana_factory_activation_opponent_hp_max: i32,
    banana_factory_activation_opponent_chop_max: i32,
    banana_factory_activation_plants: i32,
    banana_factory_activation_ripe_plants: i32,
    banana_factory_activation_fruits: i32,
    banana_factory_activation_banana_plants: i32,
    banana_factory_activation_banana_fruits: i32,
    banana_factory_activation_opponent_carried_fruit: i32,
    banana_factory_activation_opponent_carried_wood: i32,
    banana_factory_activation_opponent_crops_seen: i32,
}

impl From<OwnershipTelemetry> for PanelTelemetry {
    fn from(value: OwnershipTelemetry) -> Self {
        Self {
            opponent_crops_seen: value.opponent_crops_seen,
            active_opponent_crops: value.active_opponent_crops,
            activation_turns: value.activation_turns,
            first_activation_turn: value.first_activation_turn,
            base_command_mismatches: value.base_command_mismatches,
            selected_targets: 0,
            targets_disappeared_before_fruit: 0,
            targets_fruited_after_selection: 0,
            capacity_ready_turns: 0,
            capacity_separation_violations: 0,
            copied_verbs: [0; 7],
            ..Self::default()
        }
    }
}

struct TaskMarketOrchardResident {
    candidate: SecureOrchardBot,
    shadow: SecureOrchardBot,
    premarket_mismatches: usize,
}

struct FreshHarvestRegenerationResident {
    candidate: SecureOrchardBot,
    shadow: SecureOrchardBot,
    precommit_mismatches: usize,
    shadow_divergence_turns: usize,
}

struct BananaSeedFactoryResident {
    candidate: SecureOrchardBot,
    shadow: SecureOrchardBot,
    preactivation_mismatches: usize,
    shadow_divergence_turns: usize,
    initial_snapshot: Option<FactoryInitialSnapshot>,
    activation_snapshot: Option<FactoryActivationSnapshot>,
}

#[derive(Clone, Copy, Default)]
struct FactoryInitialSnapshot {
    plants: i32,
    ripe_plants: i32,
    fruits: i32,
    banana_plants: i32,
    banana_fruits: i32,
    shack_distance: i32,
}

#[derive(Clone, Copy, Default)]
struct FactoryActivationSnapshot {
    own_score: i32,
    opponent_score: i32,
    own_banked_fruit: i32,
    opponent_banked_fruit: i32,
    opponent_banana: i32,
    opponent_iron: i32,
    opponent_wood: i32,
    opponent_workers: i32,
    opponent_ms_sum: i32,
    opponent_cc_sum: i32,
    opponent_hp_sum: i32,
    opponent_chop_sum: i32,
    opponent_ms_max: i32,
    opponent_cc_max: i32,
    opponent_hp_max: i32,
    opponent_chop_max: i32,
    plants: i32,
    ripe_plants: i32,
    fruits: i32,
    banana_plants: i32,
    banana_fruits: i32,
    opponent_carried_fruit: i32,
    opponent_carried_wood: i32,
    opponent_crops_seen: i32,
}

impl BananaSeedFactoryResident {
    fn new(candidate: SecureOrchardBot) -> Self {
        Self {
            candidate,
            shadow: SecureOrchardBot::new(),
            preactivation_mismatches: 0,
            shadow_divergence_turns: 0,
            initial_snapshot: None,
            activation_snapshot: None,
        }
    }

    fn shack_distance(game: &GameState) -> i32 {
        let starts: Vec<_> = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            .into_iter()
            .map(|delta| (game.shacks[0].0 + delta.0, game.shacks[0].1 + delta.1))
            .filter(|cell| game.walkable.contains(cell))
            .collect();
        let goals: HashSet<_> = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            .into_iter()
            .map(|delta| (game.shacks[1].0 + delta.0, game.shacks[1].1 + delta.1))
            .filter(|cell| game.walkable.contains(cell))
            .collect();
        let mut distance = HashMap::new();
        let mut queue = VecDeque::new();
        for cell in starts {
            distance.insert(cell, 0);
            queue.push_back(cell);
        }
        while let Some((x, y)) = queue.pop_front() {
            if goals.contains(&(x, y)) {
                return distance[&(x, y)];
            }
            let next_distance = distance[&(x, y)] + 1;
            for next in [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)] {
                if game.walkable.contains(&next) && !distance.contains_key(&next) {
                    distance.insert(next, next_distance);
                    queue.push_back(next);
                }
            }
        }
        -1
    }

    fn initial_snapshot(game: &GameState) -> FactoryInitialSnapshot {
        FactoryInitialSnapshot {
            plants: game.plants.len() as i32,
            ripe_plants: game.plants.iter().filter(|plant| plant.fruits > 0).count() as i32,
            fruits: game.plants.iter().map(|plant| plant.fruits).sum(),
            banana_plants: game
                .plants
                .iter()
                .filter(|plant| plant.plant_type == "BANANA")
                .count() as i32,
            banana_fruits: game
                .plants
                .iter()
                .filter(|plant| plant.plant_type == "BANANA")
                .map(|plant| plant.fruits)
                .sum(),
            shack_distance: Self::shack_distance(game),
        }
    }

    fn activation_snapshot(game: &GameState, player: usize) -> FactoryActivationSnapshot {
        let opponent = 1 - player;
        let opponent_units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == opponent)
            .collect();
        FactoryActivationSnapshot {
            own_score: game.scores[player],
            opponent_score: game.scores[opponent],
            own_banked_fruit: game.inventories[player][..4].iter().sum(),
            opponent_banked_fruit: game.inventories[opponent][..4].iter().sum(),
            opponent_banana: game.inventories[opponent][BANANA],
            opponent_iron: game.inventories[opponent][4],
            opponent_wood: game.inventories[opponent][WOOD],
            opponent_workers: opponent_units.len() as i32,
            opponent_ms_sum: opponent_units.iter().map(|unit| unit.ms).sum(),
            opponent_cc_sum: opponent_units.iter().map(|unit| unit.cc).sum(),
            opponent_hp_sum: opponent_units.iter().map(|unit| unit.hp).sum(),
            opponent_chop_sum: opponent_units.iter().map(|unit| unit.chop).sum(),
            opponent_ms_max: opponent_units.iter().map(|unit| unit.ms).max().unwrap_or(0),
            opponent_cc_max: opponent_units.iter().map(|unit| unit.cc).max().unwrap_or(0),
            opponent_hp_max: opponent_units.iter().map(|unit| unit.hp).max().unwrap_or(0),
            opponent_chop_max: opponent_units
                .iter()
                .map(|unit| unit.chop)
                .max()
                .unwrap_or(0),
            plants: game.plants.len() as i32,
            ripe_plants: game.plants.iter().filter(|plant| plant.fruits > 0).count() as i32,
            fruits: game.plants.iter().map(|plant| plant.fruits).sum(),
            banana_plants: game
                .plants
                .iter()
                .filter(|plant| plant.plant_type == "BANANA")
                .count() as i32,
            banana_fruits: game
                .plants
                .iter()
                .filter(|plant| plant.plant_type == "BANANA")
                .map(|plant| plant.fruits)
                .sum(),
            opponent_carried_fruit: opponent_units
                .iter()
                .map(|unit| unit.carry[..4].iter().sum::<i32>())
                .sum(),
            opponent_carried_wood: opponent_units.iter().map(|unit| unit.carry[WOOD]).sum(),
            opponent_crops_seen: 0,
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.preactivation_mismatches = 0;
            self.shadow_divergence_turns = 0;
            self.initial_snapshot = Some(Self::initial_snapshot(game));
            self.activation_snapshot = None;
        }
        let activating = self.activation_snapshot.is_none()
            && self
                .candidate
                .banana_seed_factory_telemetry()
                .activation_turn
                .is_none()
            && game
                .units
                .iter()
                .filter(|unit| unit.player as usize == player)
                .count()
                >= 2;
        if activating {
            self.activation_snapshot = Some(Self::activation_snapshot(game, player));
        }
        let view = yamo_view(game, player);
        let candidate = self.candidate.commands(&view);
        let shadow = self.shadow.commands(&view);
        if candidate != shadow {
            if self
                .candidate
                .banana_seed_factory_telemetry()
                .activation_turn
                .is_none()
            {
                self.preactivation_mismatches += 1;
            } else {
                self.shadow_divergence_turns += 1;
            }
        }
        if activating {
            if let Some(snapshot) = &mut self.activation_snapshot {
                snapshot.opponent_crops_seen = self
                    .candidate
                    .banana_seed_factory_telemetry()
                    .opponent_crops_seen as i32;
            }
        }
        candidate
    }

    fn telemetry(&self) -> PanelTelemetry {
        let telemetry = self.candidate.banana_seed_factory_telemetry();
        let initial = self.initial_snapshot.unwrap_or_default();
        let activation = self.activation_snapshot.unwrap_or_default();
        PanelTelemetry {
            banana_factory_active: usize::from(telemetry.active),
            banana_factory_activation_turn: telemetry.activation_turn,
            banana_factory_selector_decided: usize::from(telemetry.selector_decided),
            banana_factory_selector_selected: usize::from(telemetry.selector_selected),
            banana_factory_initial_budget: telemetry.initial_budget,
            banana_factory_bootstrap_attempts: telemetry.bootstrap_attempts,
            banana_factory_bootstrap_successes: telemetry.bootstrap_successes,
            banana_factory_reserve_promotions: telemetry.reserve_promotions,
            banana_factory_reserve_losses: telemetry.reserve_losses,
            banana_factory_harvest_selections: telemetry.own_crop_harvest_selections,
            banana_factory_harvest_successes: telemetry.own_crop_harvest_successes,
            banana_factory_bank_harvest_selections: telemetry.bank_source_harvest_selections,
            banana_factory_bank_harvest_successes: telemetry.bank_source_harvest_successes,
            banana_factory_conversion_harvest_selections: telemetry
                .conversion_source_harvest_selections,
            banana_factory_conversion_harvest_successes: telemetry
                .conversion_source_harvest_successes,
            banana_factory_opponent_crop_policy_selections: telemetry
                .opponent_crop_policy_selections,
            banana_factory_trained_opponent_crop_selections: telemetry
                .trained_opponent_crop_selections,
            banana_factory_renewable_plant_attempts: telemetry.renewable_plant_attempts,
            banana_factory_renewable_plant_successes: telemetry.renewable_plant_successes,
            banana_factory_trained_role_rewrites: telemetry.trained_role_rewrites,
            banana_factory_trained_forbidden_commands: telemetry.trained_forbidden_commands,
            banana_factory_tracked_live_crops: telemetry.tracked_live_crops,
            banana_factory_worker_three_bridge_funding_turns: telemetry
                .worker_three_bridge_funding_turns,
            banana_factory_worker_three_bridge_fruit_harvest_selections: telemetry
                .worker_three_bridge_fruit_harvest_selections,
            banana_factory_worker_three_bridge_fruit_harvest_successes: telemetry
                .worker_three_bridge_fruit_harvest_successes,
            banana_factory_worker_three_bridge_iron_mine_selections: telemetry
                .worker_three_bridge_iron_mine_selections,
            banana_factory_worker_three_bridge_iron_mine_successes: telemetry
                .worker_three_bridge_iron_mine_successes,
            banana_factory_worker_three_bridge_train_attempts: telemetry
                .worker_three_bridge_train_attempts,
            banana_factory_worker_three_bridge_train_successes: telemetry
                .worker_three_bridge_train_successes,
            banana_factory_worker_three_bridge_trained_turn: telemetry
                .worker_three_bridge_trained_turn,
            banana_factory_worker_three_bridge_forbidden_commands: telemetry
                .worker_three_bridge_forbidden_commands,
            banana_factory_worker_three_bridge_post_training_commands: telemetry
                .worker_three_bridge_post_training_commands,
            banana_factory_preactivation_mismatches: self.preactivation_mismatches,
            banana_factory_shadow_divergence_turns: self.shadow_divergence_turns,
            banana_factory_initial_plants: initial.plants,
            banana_factory_initial_ripe_plants: initial.ripe_plants,
            banana_factory_initial_fruits: initial.fruits,
            banana_factory_initial_banana_plants: initial.banana_plants,
            banana_factory_initial_banana_fruits: initial.banana_fruits,
            banana_factory_initial_shack_distance: initial.shack_distance,
            banana_factory_activation_own_score: activation.own_score,
            banana_factory_activation_opponent_score: activation.opponent_score,
            banana_factory_activation_own_banked_fruit: activation.own_banked_fruit,
            banana_factory_activation_opponent_banked_fruit: activation.opponent_banked_fruit,
            banana_factory_activation_opponent_banana: activation.opponent_banana,
            banana_factory_activation_opponent_iron: activation.opponent_iron,
            banana_factory_activation_opponent_wood: activation.opponent_wood,
            banana_factory_activation_opponent_workers: activation.opponent_workers,
            banana_factory_activation_opponent_ms_sum: activation.opponent_ms_sum,
            banana_factory_activation_opponent_cc_sum: activation.opponent_cc_sum,
            banana_factory_activation_opponent_hp_sum: activation.opponent_hp_sum,
            banana_factory_activation_opponent_chop_sum: activation.opponent_chop_sum,
            banana_factory_activation_opponent_ms_max: activation.opponent_ms_max,
            banana_factory_activation_opponent_cc_max: activation.opponent_cc_max,
            banana_factory_activation_opponent_hp_max: activation.opponent_hp_max,
            banana_factory_activation_opponent_chop_max: activation.opponent_chop_max,
            banana_factory_activation_plants: activation.plants,
            banana_factory_activation_ripe_plants: activation.ripe_plants,
            banana_factory_activation_fruits: activation.fruits,
            banana_factory_activation_banana_plants: activation.banana_plants,
            banana_factory_activation_banana_fruits: activation.banana_fruits,
            banana_factory_activation_opponent_carried_fruit: activation.opponent_carried_fruit,
            banana_factory_activation_opponent_carried_wood: activation.opponent_carried_wood,
            banana_factory_activation_opponent_crops_seen: activation.opponent_crops_seen,
            ..PanelTelemetry::default()
        }
    }
}

impl FreshHarvestRegenerationResident {
    fn new() -> Self {
        Self {
            candidate: SecureOrchardBot::fresh_harvest_regeneration(),
            shadow: SecureOrchardBot::new(),
            precommit_mismatches: 0,
            shadow_divergence_turns: 0,
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.precommit_mismatches = 0;
            self.shadow_divergence_turns = 0;
        }
        let view = yamo_view(game, player);
        let candidate = self.candidate.commands(&view);
        let shadow = self.shadow.commands(&view);
        let telemetry = self.candidate.fresh_harvest_regeneration_telemetry();
        if candidate != shadow {
            if telemetry.commitments == 0 {
                self.precommit_mismatches += 1;
            } else {
                self.shadow_divergence_turns += 1;
            }
        }
        candidate
    }

    fn telemetry(&self) -> PanelTelemetry {
        let telemetry = self.candidate.fresh_harvest_regeneration_telemetry();
        PanelTelemetry {
            fresh_harvest_commitments: telemetry.commitments,
            fresh_harvest_first_turn: telemetry.first_commitment_turn,
            fresh_harvest_successful_plants: telemetry.successful_plants,
            fresh_harvest_precommit_mismatches: self.precommit_mismatches,
            fresh_harvest_shadow_divergence_turns: self.shadow_divergence_turns,
            ..PanelTelemetry::default()
        }
    }
}

impl TaskMarketOrchardResident {
    fn new() -> Self {
        Self {
            candidate: SecureOrchardBot::task_market(),
            shadow: SecureOrchardBot::new(),
            premarket_mismatches: 0,
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.premarket_mismatches = 0;
        }
        let view = yamo_view(game, player);
        let candidate = self.candidate.commands(&view);
        let shadow = self.shadow.commands(&view);
        if self.candidate.task_market_telemetry().market_turns == 0 && candidate != shadow {
            self.premarket_mismatches += 1;
        }
        candidate
    }

    fn telemetry(&self) -> PanelTelemetry {
        let telemetry = self.candidate.task_market_telemetry();
        PanelTelemetry {
            base_command_mismatches: self.premarket_mismatches,
            orchard_activation_turn: telemetry.activation_turn,
            orchard_seed_repaid_turn: telemetry.seed_repaid_turn,
            orchard_market_turns: telemetry.market_turns,
            orchard_offers: telemetry.offers,
            orchard_selections: telemetry.selections,
            orchard_harvest_selections: telemetry.harvest_selections,
            orchard_first_selection_turn: telemetry.first_selection_turn,
            orchard_forced_setup_actions: telemetry.forced_setup_actions,
            orchard_premarket_mismatches: self.premarket_mismatches,
            ..PanelTelemetry::default()
        }
    }
}

impl From<PreFruitTelemetry> for PanelTelemetry {
    fn from(value: PreFruitTelemetry) -> Self {
        Self {
            opponent_crops_seen: value.opponent_crops_seen,
            active_opponent_crops: value.active_opponent_crops,
            activation_turns: value.activation_turns,
            first_activation_turn: value.first_activation_turn,
            base_command_mismatches: value.base_command_mismatches,
            selected_targets: value.selected_targets,
            targets_disappeared_before_fruit: value.targets_disappeared_before_fruit,
            targets_fruited_after_selection: value.targets_fruited_after_selection,
            capacity_ready_turns: 0,
            capacity_separation_violations: 0,
            copied_verbs: [0; 7],
            ..Self::default()
        }
    }
}

impl From<CapacitySeparatedTelemetry> for PanelTelemetry {
    fn from(value: CapacitySeparatedTelemetry) -> Self {
        Self {
            opponent_crops_seen: value.opponent_crops_seen,
            active_opponent_crops: value.active_opponent_crops,
            activation_turns: value.activation_turns,
            first_activation_turn: value.first_activation_turn,
            base_command_mismatches: value.base_command_mismatches,
            selected_targets: value.selected_targets,
            targets_disappeared_before_fruit: value.targets_disappeared_before_fruit,
            targets_fruited_after_selection: value.targets_fruited_after_selection,
            capacity_ready_turns: value.capacity_ready_turns,
            capacity_separation_violations: value.capacity_separation_violations,
            copied_verbs: [0; 7],
            ..Self::default()
        }
    }
}

#[derive(Default)]
struct CollapseHistory {
    initialized: bool,
    previous_plants: HashSet<Cell>,
    own_plant_attempts: HashSet<Cell>,
    opponent_crops: HashSet<Cell>,
    opponent_banana_crops_seen: usize,
    active: bool,
    activation_turns: usize,
    first_activation_turn: Option<i32>,
    base_command_mismatches: usize,
    selected_targets: usize,
    emitted_verbs: [usize; 7],
    entry_state_violations: usize,
    forbidden_post_entry_commands: usize,
    post_entry_commands: usize,
    lineage_recovery_turns: usize,
    entry_banked_banana: i32,
    entry_carried_banana: i32,
    entry_crop_banana_fruits: i32,
    entry_opponent_banana_crops: usize,
    entry_own_score: i32,
    entry_opponent_score: i32,
    entry_margin: i32,
}

struct LineageCollapseResident {
    resident: SecureOrchardBot,
    shadow: SecureOrchardBot,
    history: CollapseHistory,
}

impl LineageCollapseResident {
    fn new() -> Self {
        Self {
            resident: SecureOrchardBot::new(),
            shadow: SecureOrchardBot::new(),
            history: CollapseHistory::default(),
        }
    }

    fn bfs(walkable: &HashSet<Cell>, source: Cell) -> HashMap<Cell, i32> {
        let mut distance = HashMap::new();
        let mut queue = VecDeque::new();
        distance.insert(source, 0);
        queue.push_back(source);
        while let Some((x, y)) = queue.pop_front() {
            let next_distance = distance[&(x, y)] + 1;
            for next in [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)] {
                if walkable.contains(&next) && !distance.contains_key(&next) {
                    distance.insert(next, next_distance);
                    queue.push_back(next);
                }
            }
        }
        distance
    }

    fn verb_index(command: &str) -> Option<usize> {
        ResidentChopperHybrid::verb_index(command)
    }

    fn remember_plant_attempts(
        history: &mut CollapseHistory,
        game: &GameState,
        player: usize,
        commands: &[String],
    ) {
        history
            .own_plant_attempts
            .extend(commands.iter().filter_map(|command| {
                let mut fields = command.split_whitespace();
                if fields.next()? != "PLANT" {
                    return None;
                }
                let id = fields.next()?.parse::<i32>().ok()?;
                game.units
                    .iter()
                    .find(|unit| unit.id == id && unit.player as usize == player)
                    .map(|unit| unit.pos())
            }));
    }

    fn reconcile_provenance(&mut self, game: &GameState) {
        if game.turn == 1 {
            self.history = CollapseHistory::default();
        }
        let current: HashSet<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .map(|plant| plant.pos())
            .collect();
        if self.history.initialized {
            let appeared: Vec<_> = current
                .difference(&self.history.previous_plants)
                .copied()
                .collect();
            for cell in appeared {
                if self.history.own_plant_attempts.contains(&cell) {
                    continue;
                }
                if self.history.opponent_crops.insert(cell)
                    && game
                        .plants
                        .iter()
                        .any(|plant| plant.pos() == cell && plant.plant_type == "BANANA")
                {
                    self.history.opponent_banana_crops_seen += 1;
                }
            }
            self.history
                .opponent_crops
                .retain(|cell| current.contains(cell));
        } else {
            self.history.initialized = true;
        }
        self.history.previous_plants = current;
        self.history.own_plant_attempts.clear();
    }

    fn opponent_banana_stock(&self, game: &GameState, player: usize) -> (i32, i32, i32, usize) {
        let opponent = 1 - player;
        let banked = game.inventories[opponent][BANANA];
        let carried = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == opponent)
            .map(|unit| unit.carry[BANANA])
            .sum();
        let mut crop_fruits = 0;
        let mut crops = 0;
        for plant in game.plants.iter().filter(|plant| {
            plant.plant_type == "BANANA" && self.history.opponent_crops.contains(&plant.pos())
        }) {
            crops += 1;
            crop_fruits += plant.fruits;
        }
        (banked, carried, crop_fruits, crops)
    }

    fn enter_if_eligible(&mut self, game: &GameState, player: usize) {
        let stock = self.opponent_banana_stock(game, player);
        if self.history.active {
            if stock.0 + stock.1 + stock.2 > 0 || stock.3 > 0 {
                self.history.lineage_recovery_turns += 1;
            }
            return;
        }
        let eligible =
            game.turn > 100 && self.history.opponent_banana_crops_seen > 0 && stock == (0, 0, 0, 0);
        if !eligible {
            return;
        }
        self.history.active = true;
        self.history.first_activation_turn = Some(game.turn);
        self.history.entry_banked_banana = stock.0;
        self.history.entry_carried_banana = stock.1;
        self.history.entry_crop_banana_fruits = stock.2;
        self.history.entry_opponent_banana_crops = stock.3;
        self.history.entry_own_score = game.scores[player];
        self.history.entry_opponent_score = game.scores[1 - player];
        self.history.entry_margin = game.scores[player] - game.scores[1 - player];
        if game.turn <= 100 || self.history.opponent_banana_crops_seen == 0 || stock != (0, 0, 0, 0)
        {
            self.history.entry_state_violations += 1;
        }
    }

    fn bank_command(
        game: &GameState,
        unit: &troll_farm::game::state::Unit,
        player: usize,
    ) -> String {
        let shack = game.shacks[player];
        if (unit.x - shack.0).abs() + (unit.y - shack.1).abs() == 1 {
            return format!("DROP {}", unit.id);
        }
        let distance = Self::bfs(&game.walkable, unit.pos());
        let door = [
            (shack.0, shack.1 + 1),
            (shack.0 + 1, shack.1),
            (shack.0, shack.1 - 1),
            (shack.0 - 1, shack.1),
        ]
        .into_iter()
        .filter(|cell| game.walkable.contains(cell))
        .min_by_key(|cell| (distance.get(cell).copied().unwrap_or(i32::MAX), *cell))
        .unwrap_or(unit.pos());
        format!("MOVE {} {} {}", unit.id, door.0, door.1)
    }

    fn liquidation_commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let mut assigned = HashSet::new();
        let mut first_target = None;
        let mut commands = Vec::new();
        for unit in units {
            let command = if unit.total() > 0 {
                Self::bank_command(game, unit, player)
            } else {
                let distance = Self::bfs(&game.walkable, unit.pos());
                let fresh = game
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0 && !assigned.contains(&plant.pos()))
                    .filter_map(|plant| {
                        distance
                            .get(&plant.pos())
                            .copied()
                            .map(|cells| (plant, cells))
                    })
                    .min_by_key(|(plant, cells)| {
                        (
                            usize::from(plant.plant_type != "BANANA"),
                            usize::from(plant.fruits == 0),
                            plant.health,
                            *cells,
                            plant.pos(),
                        )
                    })
                    .map(|(plant, _)| plant.pos());
                let target = fresh.or(first_target);
                let Some(target) = target else {
                    commands.push("WAIT".to_string());
                    continue;
                };
                if fresh.is_some() {
                    assigned.insert(target);
                    first_target.get_or_insert(target);
                }
                self.history.selected_targets += 1;
                if unit.pos() == target {
                    format!("CHOP {}", unit.id)
                } else {
                    format!("MOVE {} {} {}", unit.id, target.0, target.1)
                }
            };
            commands.push(command);
        }
        for command in &commands {
            let Some(verb) = Self::verb_index(command) else {
                continue;
            };
            self.history.emitted_verbs[verb] += 1;
            self.history.post_entry_commands += 1;
            if matches!(verb, 3..=6) {
                self.history.forbidden_post_entry_commands += 1;
            }
        }
        commands
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        self.reconcile_provenance(game);
        let base = self.resident.commands(&yamo_view(game, player));
        if base != self.shadow.commands(&yamo_view(game, player)) {
            self.history.base_command_mismatches += 1;
        }
        self.enter_if_eligible(game, player);
        if self.history.active {
            self.history.activation_turns += 1;
            return self.liquidation_commands(game, player);
        }
        Self::remember_plant_attempts(&mut self.history, game, player, &base);
        base
    }

    fn telemetry(&self) -> PanelTelemetry {
        let entered = self.history.first_activation_turn.is_some();
        PanelTelemetry {
            opponent_crops_seen: self.history.opponent_banana_crops_seen,
            active_opponent_crops: self.history.opponent_crops.len(),
            activation_turns: self.history.activation_turns,
            first_activation_turn: self.history.first_activation_turn,
            base_command_mismatches: self.history.base_command_mismatches,
            selected_targets: self.history.selected_targets,
            copied_verbs: self.history.emitted_verbs,
            entry_state_violations: self.history.entry_state_violations,
            forbidden_post_entry_commands: self.history.forbidden_post_entry_commands,
            post_entry_commands: self.history.post_entry_commands,
            lineage_recovery_turns: self.history.lineage_recovery_turns,
            entry_banked_banana: if entered {
                self.history.entry_banked_banana
            } else {
                -1
            },
            entry_carried_banana: if entered {
                self.history.entry_carried_banana
            } else {
                -1
            },
            entry_crop_banana_fruits: if entered {
                self.history.entry_crop_banana_fruits
            } else {
                -1
            },
            entry_opponent_banana_crops: if entered {
                self.history.entry_opponent_banana_crops
            } else {
                usize::MAX
            },
            entry_own_score: if entered {
                self.history.entry_own_score
            } else {
                -1
            },
            entry_opponent_score: if entered {
                self.history.entry_opponent_score
            } else {
                -1
            },
            entry_margin: if entered {
                self.history.entry_margin
            } else {
                i32::MIN
            },
            ..PanelTelemetry::default()
        }
    }
}

#[derive(Default)]
struct HybridHistory {
    substitution_turns: usize,
    first_substitution_turn: Option<i32>,
    base_command_mismatches: usize,
    copied_verbs: [usize; 7],
}

struct ResidentChopperHybrid {
    farm: GoldElite,
    farm_shadow: GoldElite,
    resident: SecureOrchardBot,
    history: HybridHistory,
}

impl ResidentChopperHybrid {
    fn new() -> Self {
        Self {
            farm: top_farm(),
            farm_shadow: top_farm(),
            resident: SecureOrchardBot::new(),
            history: HybridHistory::default(),
        }
    }

    fn unit_id(command: &str) -> Option<i32> {
        let mut fields = command.split_whitespace();
        match fields.next()? {
            "MOVE" | "HARVEST" | "DROP" | "CHOP" | "MINE" | "PLANT" | "PICK" => {
                fields.next()?.parse().ok()
            }
            _ => None,
        }
    }

    fn verb_index(command: &str) -> Option<usize> {
        match command.split_whitespace().next()? {
            "MOVE" => Some(0),
            "CHOP" => Some(1),
            "DROP" => Some(2),
            "MINE" => Some(3),
            "PICK" => Some(4),
            "HARVEST" => Some(5),
            "PLANT" => Some(6),
            _ => None,
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.history = HybridHistory::default();
        }
        let mut commands = self.farm.decide(game, player);
        if commands != self.farm_shadow.decide(game, player) {
            self.history.base_command_mismatches += 1;
        }
        let resident = self.resident.commands(&yamo_view(game, player));
        let chopper_ids: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player && unit.chop >= 2 && unit.hp == 0)
            .map(|unit| unit.id)
            .collect();
        let mut substituted = false;
        for id in chopper_ids {
            let Some(resident_command) = resident
                .iter()
                .find(|command| Self::unit_id(command) == Some(id))
                .cloned()
            else {
                continue;
            };
            let Some(index) = commands
                .iter()
                .position(|command| Self::unit_id(command) == Some(id))
            else {
                commands.push(resident_command);
                substituted = true;
                let verb = Self::verb_index(commands.last().expect("pushed command"))
                    .expect("resident unit command verb");
                self.history.copied_verbs[verb] += 1;
                continue;
            };
            if commands[index] == resident_command {
                continue;
            }
            let verb = Self::verb_index(&resident_command).expect("resident unit command verb");
            commands[index] = resident_command;
            self.history.copied_verbs[verb] += 1;
            substituted = true;
        }
        if substituted {
            self.history.substitution_turns += 1;
            self.history
                .first_substitution_turn
                .get_or_insert(game.turn);
        }
        commands
    }

    fn telemetry(&self) -> PanelTelemetry {
        PanelTelemetry {
            activation_turns: self.history.substitution_turns,
            first_activation_turn: self.history.first_substitution_turn,
            base_command_mismatches: self.history.base_command_mismatches,
            copied_verbs: self.history.copied_verbs,
            ..PanelTelemetry::default()
        }
    }
}

impl Policy {
    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::TaskMarketOrchard(bot) => bot.commands(game, player),
            Self::FreshHarvestRegeneration(bot) => bot.commands(game, player),
            Self::BananaSeedFactory(bot) => bot.commands(game, player),
            Self::Farm(bot) => bot.decide(game, player),
            Self::Ownership(bot) => bot.decide(game, player),
            Self::ResidentChopper(bot) => bot.commands(game, player),
            Self::PreFruit(bot) => bot.decide(game, player),
            Self::CapacitySeparated(bot) => bot.decide(game, player),
            Self::LineageCollapse(bot) => bot.commands(game, player),
        }
    }

    fn telemetry(&self) -> PanelTelemetry {
        match self {
            Self::TaskMarketOrchard(bot) => bot.telemetry(),
            Self::FreshHarvestRegeneration(bot) => bot.telemetry(),
            Self::BananaSeedFactory(bot) => bot.telemetry(),
            Self::Ownership(bot) => bot.telemetry().into(),
            Self::ResidentChopper(bot) => bot.telemetry(),
            Self::PreFruit(bot) => bot.telemetry().into(),
            Self::CapacitySeparated(bot) => bot.telemetry().into(),
            Self::LineageCollapse(bot) => bot.telemetry(),
            _ => PanelTelemetry::default(),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Profile {
    Resident,
    Farm,
    Ownership,
    ResidentChopper,
    PreFruit,
    AdaptiveFarm,
    CapacitySeparated,
    LineageCollapse,
    SpeciesSeparated,
    TaskMarketOrchard,
    FreshHarvestRegeneration,
    BananaSeedFactory,
    BananaSeedFactorySourceSeparated,
    BananaSeedFactoryActivationSelector,
    BananaSeedFactoryDualValueE6,
    BananaSeedFactoryTrainedDualValueE6,
    BananaSeedFactoryWorkerThreeBridge,
}

impl Profile {
    fn label(self) -> &'static str {
        match self {
            Self::Resident => "resident",
            Self::Farm => "lean_m2c2h0k2",
            Self::Ownership => "ownership_aware",
            Self::ResidentChopper => "resident_chopper_hybrid",
            Self::PreFruit => "prefruit_interruption",
            Self::AdaptiveFarm => "adaptive_density",
            Self::CapacitySeparated => "capacity_separated_denial",
            Self::LineageCollapse => "lineage_collapse_liquidation",
            Self::SpeciesSeparated => "species_separated_plum",
            Self::TaskMarketOrchard => "task_market_orchard",
            Self::FreshHarvestRegeneration => "fresh_harvest_regeneration",
            Self::BananaSeedFactory => "banana_seed_factory",
            Self::BananaSeedFactorySourceSeparated => "banana_seed_factory_source_separated",
            Self::BananaSeedFactoryActivationSelector => "banana_seed_factory_activation_selector",
            Self::BananaSeedFactoryDualValueE6 => "banana_seed_factory_dual_value_e6",
            Self::BananaSeedFactoryTrainedDualValueE6 => {
                "banana_seed_factory_trained_dual_value_e6"
            }
            Self::BananaSeedFactoryWorkerThreeBridge => "banana_seed_factory_worker_three_bridge",
        }
    }

    fn policy(self) -> Policy {
        match self {
            Self::Resident => Policy::Resident(SecureOrchardBot::new()),
            Self::Farm => Policy::Farm(top_farm()),
            Self::Ownership => Policy::Ownership(OwnershipAwareFarm::new()),
            Self::ResidentChopper => Policy::ResidentChopper(ResidentChopperHybrid::new()),
            Self::PreFruit => Policy::PreFruit(PreFruitInterruption::new()),
            Self::AdaptiveFarm => Policy::Farm(GoldElite::adaptive()),
            Self::CapacitySeparated => Policy::CapacitySeparated(CapacitySeparatedDenial::new()),
            Self::LineageCollapse => Policy::LineageCollapse(LineageCollapseResident::new()),
            Self::SpeciesSeparated => Policy::Farm(GoldElite::adaptive_plum()),
            Self::TaskMarketOrchard => Policy::TaskMarketOrchard(TaskMarketOrchardResident::new()),
            Self::FreshHarvestRegeneration => {
                Policy::FreshHarvestRegeneration(FreshHarvestRegenerationResident::new())
            }
            Self::BananaSeedFactory => Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                SecureOrchardBot::banana_seed_factory(),
            )),
            Self::BananaSeedFactorySourceSeparated => {
                Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                    SecureOrchardBot::banana_seed_factory_source_separated(),
                ))
            }
            Self::BananaSeedFactoryActivationSelector => {
                Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                    SecureOrchardBot::banana_seed_factory_activation_selector(),
                ))
            }
            Self::BananaSeedFactoryDualValueE6 => {
                Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                    SecureOrchardBot::banana_seed_factory_dual_value_e6(),
                ))
            }
            Self::BananaSeedFactoryTrainedDualValueE6 => {
                Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                    SecureOrchardBot::banana_seed_factory_trained_dual_value_e6(),
                ))
            }
            Self::BananaSeedFactoryWorkerThreeBridge => {
                Policy::BananaSeedFactory(BananaSeedFactoryResident::new(
                    SecureOrchardBot::banana_seed_factory_worker_three_bridge(),
                ))
            }
        }
    }
}

#[derive(Clone, Copy)]
enum Experiment {
    Ownership,
    ResidentChopper,
    PreFruit,
    CapacitySeparated,
    LineageCollapse,
    SpeciesSeparated,
    TaskMarketOrchard,
    FreshHarvestRegeneration,
    BananaSeedFactory,
    BananaFactoryLineageAblation,
    BananaFactoryActivationSelector,
    BananaFactoryDualValueAblation,
    BananaFactoryWorkerThreeBridge,
}

impl Experiment {
    fn parse(value: &str) -> Self {
        match value {
            "ownership" => Self::Ownership,
            "resident_chopper" => Self::ResidentChopper,
            "prefruit" => Self::PreFruit,
            "capacity_separated" => Self::CapacitySeparated,
            "lineage_collapse" => Self::LineageCollapse,
            "species_separated" => Self::SpeciesSeparated,
            "task_market_orchard" => Self::TaskMarketOrchard,
            "fresh_harvest_regeneration" => Self::FreshHarvestRegeneration,
            "banana_seed_factory" => Self::BananaSeedFactory,
            "banana_factory_lineage_ablation" => Self::BananaFactoryLineageAblation,
            "banana_factory_activation_selector" => Self::BananaFactoryActivationSelector,
            "banana_factory_dual_value_ablation" => Self::BananaFactoryDualValueAblation,
            "banana_factory_worker_three_bridge" => Self::BananaFactoryWorkerThreeBridge,
            _ => panic!("unknown experiment {value}"),
        }
    }

    fn profiles(self) -> Vec<Profile> {
        match self {
            Self::Ownership => vec![Profile::Resident, Profile::Farm, Profile::Ownership],
            Self::ResidentChopper => {
                vec![Profile::Resident, Profile::Farm, Profile::ResidentChopper]
            }
            Self::PreFruit => vec![Profile::Resident, Profile::Farm, Profile::PreFruit],
            Self::CapacitySeparated => vec![
                Profile::Resident,
                Profile::AdaptiveFarm,
                Profile::CapacitySeparated,
            ],
            Self::LineageCollapse => vec![
                Profile::Resident,
                Profile::AdaptiveFarm,
                Profile::LineageCollapse,
            ],
            Self::SpeciesSeparated => vec![
                Profile::Resident,
                Profile::AdaptiveFarm,
                Profile::SpeciesSeparated,
            ],
            Self::TaskMarketOrchard => {
                vec![Profile::Resident, Profile::TaskMarketOrchard]
            }
            Self::FreshHarvestRegeneration => {
                vec![Profile::Resident, Profile::FreshHarvestRegeneration]
            }
            Self::BananaSeedFactory => {
                vec![Profile::Resident, Profile::BananaSeedFactory]
            }
            Self::BananaFactoryLineageAblation => vec![
                Profile::Resident,
                Profile::BananaSeedFactory,
                Profile::BananaSeedFactorySourceSeparated,
            ],
            Self::BananaFactoryActivationSelector => vec![
                Profile::Resident,
                Profile::BananaSeedFactoryActivationSelector,
            ],
            Self::BananaFactoryDualValueAblation => vec![
                Profile::Resident,
                Profile::BananaSeedFactory,
                Profile::BananaSeedFactoryDualValueE6,
                Profile::BananaSeedFactoryTrainedDualValueE6,
            ],
            Self::BananaFactoryWorkerThreeBridge => vec![
                Profile::Resident,
                Profile::BananaSeedFactory,
                Profile::BananaSeedFactoryWorkerThreeBridge,
            ],
        }
    }
}

fn command_unit_ids(commands: &[String], action: &str) -> HashSet<i32> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            if fields.next()? != action {
                return None;
            }
            fields.next()?.parse().ok()
        })
        .collect()
}

fn plant_command_kinds(commands: &[String]) -> [usize; 4] {
    let mut counts = [0; 4];
    for command in commands {
        let mut fields = command.split_whitespace();
        if fields.next() != Some("PLANT") {
            continue;
        }
        let _unit_id = fields.next();
        if let Some(kind) = fields.next().and_then(fruit_index) {
            counts[kind] += 1;
        }
    }
    counts
}

fn plant_attempts(game: &GameState, player: usize, commands: &[String]) -> HashSet<Cell> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            if fields.next()? != "PLANT" {
                return None;
            }
            let id: i32 = fields.next()?.parse().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(|unit| unit.pos())
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

#[derive(Clone, Copy)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    own_inventory_wood: i32,
    opponent_inventory_wood: i32,
    workers: usize,
    terminal_turn: i32,
    terminal_plants: usize,
    terminal_banana_plants: usize,
    terminal_plants_by_kind: [usize; 4],
    action_hash: u64,
    terminal_state_hash: u64,
    attribution: Attribution,
    telemetry: PanelTelemetry,
    worker_three_audit: WorkerThreeAudit,
}

#[derive(Clone, Copy, Debug)]
struct WorkerThreeAudit {
    two_worker_turns: usize,
    shack_occupied_turns: usize,
    balanced_affordable_turns: usize,
    balanced_carried_affordable_turns: usize,
    balanced_spawn_legal_turns: usize,
    balanced_first_affordable_turn: Option<i32>,
    balanced_first_spawn_legal_turn: Option<i32>,
    balanced_last_spawn_legal_turn: Option<i32>,
    balanced_longest_spawn_legal_run: usize,
    balanced_current_spawn_legal_run: usize,
    balanced_min_total_deficit: i32,
    balanced_best_deficit_turn: Option<i32>,
    balanced_best_deficit: [i32; 4],
    balanced_resource_deficit_turns: [usize; 4],
    poststock_affordable_turns: usize,
    fruit_materializable_turns: usize,
    first_fruit_materializable_turn: Option<i32>,
    longest_fruit_materializable_run: usize,
    current_fruit_materializable_run: usize,
    poststock_min_total_deficit: i32,
    poststock_best_deficit_turn: Option<i32>,
    poststock_best_deficit: [i32; 4],
    maximum_poststock_available: [i32; 4],
    cheap_affordable_turns: usize,
    cheap_spawn_legal_turns: usize,
    cheap_first_spawn_legal_turn: Option<i32>,
    terminal_inventory: [i32; 6],
    terminal_carried: [i32; 6],
}

impl Default for WorkerThreeAudit {
    fn default() -> Self {
        Self {
            two_worker_turns: 0,
            shack_occupied_turns: 0,
            balanced_affordable_turns: 0,
            balanced_carried_affordable_turns: 0,
            balanced_spawn_legal_turns: 0,
            balanced_first_affordable_turn: None,
            balanced_first_spawn_legal_turn: None,
            balanced_last_spawn_legal_turn: None,
            balanced_longest_spawn_legal_run: 0,
            balanced_current_spawn_legal_run: 0,
            balanced_min_total_deficit: i32::MAX,
            balanced_best_deficit_turn: None,
            balanced_best_deficit: [0; 4],
            balanced_resource_deficit_turns: [0; 4],
            poststock_affordable_turns: 0,
            fruit_materializable_turns: 0,
            first_fruit_materializable_turn: None,
            longest_fruit_materializable_run: 0,
            current_fruit_materializable_run: 0,
            poststock_min_total_deficit: i32::MAX,
            poststock_best_deficit_turn: None,
            poststock_best_deficit: [0; 4],
            maximum_poststock_available: [0; 4],
            cheap_affordable_turns: 0,
            cheap_spawn_legal_turns: 0,
            cheap_first_spawn_legal_turn: None,
            terminal_inventory: [0; 6],
            terminal_carried: [0; 6],
        }
    }
}

impl WorkerThreeAudit {
    const BALANCED_SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2);
    const CHEAP_SPEC: (i32, i32, i32, i32) = (1, 1, 0, 1);
    const BILL_ITEMS: [usize; 4] = [PLUM, LEMON, APPLE, IRON];

    fn affordability(
        game: &GameState,
        seat: usize,
        spec: (i32, i32, i32, i32),
        include_carried: bool,
    ) -> (bool, [i32; 4]) {
        let cost = training_cost(2, spec);
        let mut deficits = [0; 4];
        for (slot, item) in Self::BILL_ITEMS.into_iter().enumerate() {
            if item == IRON && game.iron.is_empty() {
                continue;
            }
            let carried = if include_carried {
                game.units
                    .iter()
                    .filter(|unit| unit.player as usize == seat)
                    .map(|unit| unit.carry[item])
                    .sum()
            } else {
                0
            };
            deficits[slot] = (cost[item] - game.inventories[seat][item] - carried).max(0);
        }
        (deficits.iter().all(|deficit| *deficit == 0), deficits)
    }

    fn poststock_deficit(
        game: &GameState,
        seat: usize,
        spec: (i32, i32, i32, i32),
    ) -> ([i32; 4], [i32; 4]) {
        let cost = training_cost(2, spec);
        let mut available = [0; 4];
        let mut deficits = [0; 4];
        for (slot, item) in Self::BILL_ITEMS.into_iter().enumerate() {
            available[slot] = game.inventories[seat][item]
                + game
                    .units
                    .iter()
                    .filter(|unit| unit.player as usize == seat)
                    .map(|unit| unit.carry[item])
                    .sum::<i32>();
            if item != IRON {
                let species = match item {
                    PLUM => "PLUM",
                    LEMON => "LEMON",
                    APPLE => "APPLE",
                    _ => unreachable!(),
                };
                available[slot] += game
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0 && plant.plant_type == species)
                    .map(|plant| plant.fruits)
                    .sum::<i32>();
            } else if game.iron.is_empty() {
                available[slot] = cost[item];
            }
            deficits[slot] = (cost[item] - available[slot]).max(0);
        }
        (available, deficits)
    }

    fn observe(&mut self, game: &GameState, seat: usize) {
        let own_workers = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count();
        if own_workers != 2 {
            self.balanced_current_spawn_legal_run = 0;
            return;
        }
        self.two_worker_turns += 1;
        let shack_occupied = game
            .units
            .iter()
            .any(|unit| unit.pos() == game.shacks[seat]);
        if shack_occupied {
            self.shack_occupied_turns += 1;
        }
        let (balanced_affordable, balanced_deficit) =
            Self::affordability(game, seat, Self::BALANCED_SPEC, false);
        let (balanced_carried_affordable, _) =
            Self::affordability(game, seat, Self::BALANCED_SPEC, true);
        if balanced_affordable {
            self.balanced_affordable_turns += 1;
            self.balanced_first_affordable_turn.get_or_insert(game.turn);
        }
        if balanced_carried_affordable {
            self.balanced_carried_affordable_turns += 1;
        }
        for (slot, deficit) in balanced_deficit.into_iter().enumerate() {
            if deficit > 0 {
                self.balanced_resource_deficit_turns[slot] += 1;
            }
        }
        let total_deficit: i32 = balanced_deficit.iter().sum();
        if total_deficit < self.balanced_min_total_deficit {
            self.balanced_min_total_deficit = total_deficit;
            self.balanced_best_deficit_turn = Some(game.turn);
            self.balanced_best_deficit = balanced_deficit;
        }
        let horizon_open = TOTAL_TURNS - game.turn > 20;
        let balanced_spawn_legal = balanced_affordable && !shack_occupied && horizon_open;
        if balanced_spawn_legal {
            self.balanced_spawn_legal_turns += 1;
            self.balanced_first_spawn_legal_turn
                .get_or_insert(game.turn);
            self.balanced_last_spawn_legal_turn = Some(game.turn);
            self.balanced_current_spawn_legal_run += 1;
            self.balanced_longest_spawn_legal_run = self
                .balanced_longest_spawn_legal_run
                .max(self.balanced_current_spawn_legal_run);
        } else {
            self.balanced_current_spawn_legal_run = 0;
        }

        let (poststock_available, poststock_deficit) =
            Self::poststock_deficit(game, seat, Self::BALANCED_SPEC);
        for slot in 0..4 {
            self.maximum_poststock_available[slot] =
                self.maximum_poststock_available[slot].max(poststock_available[slot]);
        }
        if poststock_deficit.iter().all(|deficit| *deficit == 0) {
            self.poststock_affordable_turns += 1;
        }
        let fruit_materializable =
            horizon_open && poststock_deficit[..3].iter().all(|deficit| *deficit == 0);
        if fruit_materializable {
            self.fruit_materializable_turns += 1;
            self.first_fruit_materializable_turn
                .get_or_insert(game.turn);
            self.current_fruit_materializable_run += 1;
            self.longest_fruit_materializable_run = self
                .longest_fruit_materializable_run
                .max(self.current_fruit_materializable_run);
        } else {
            self.current_fruit_materializable_run = 0;
        }
        let poststock_total_deficit: i32 = poststock_deficit.iter().sum();
        if poststock_total_deficit < self.poststock_min_total_deficit {
            self.poststock_min_total_deficit = poststock_total_deficit;
            self.poststock_best_deficit_turn = Some(game.turn);
            self.poststock_best_deficit = poststock_deficit;
        }

        let (cheap_affordable, _) = Self::affordability(game, seat, Self::CHEAP_SPEC, false);
        if cheap_affordable {
            self.cheap_affordable_turns += 1;
        }
        let cheap_spawn_legal = cheap_affordable && !shack_occupied && horizon_open;
        if cheap_spawn_legal {
            self.cheap_spawn_legal_turns += 1;
            self.cheap_first_spawn_legal_turn.get_or_insert(game.turn);
        }
    }

    fn finish(&mut self, game: &GameState, seat: usize) {
        self.terminal_inventory = game.inventories[seat];
        for unit in game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
        {
            for item in 0..6 {
                self.terminal_carried[item] += unit.carry[item];
            }
        }
        if self.balanced_min_total_deficit == i32::MAX {
            self.balanced_min_total_deficit = -1;
        }
        if self.poststock_min_total_deficit == i32::MAX {
            self.poststock_min_total_deficit = -1;
        }
    }
}

fn play(initial: &GameState, seat: usize, model: usize, profile: Profile) -> Outcome {
    let mut game = initial.clone();
    let mut ours = profile.policy();
    let theirs = opponent(model);
    let mut provenance: HashMap<Cell, Origin> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Origin::Natural))
        .collect();
    let mut attribution = Attribution::default();
    let mut action_hash = 14_695_981_039_346_656_037_u64;
    let mut turns_until_end = 0;
    let mut worker_three_audit = WorkerThreeAudit::default();
    while game.turn <= TOTAL_TURNS {
        worker_three_audit.observe(&game, seat);
        let ours_commands = ours.commands(&game, seat);
        let theirs_commands = theirs.decide(&game, 1 - seat);
        let commands = if seat == 0 {
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
        for absolute_player in 0..2 {
            let relative = usize::from(absolute_player != seat);
            let counts = plant_command_kinds(&commands[absolute_player]);
            for (kind, count) in counts.into_iter().enumerate() {
                attribution.plant_commands_by_kind[relative][kind] += count;
            }
        }
        let before_plants: HashSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        let attempts = [
            plant_attempts(&game, 0, &commands[0]),
            plant_attempts(&game, 1, &commands[1]),
        ];
        let chop_ids = [
            command_unit_ids(&commands[0], "CHOP"),
            command_unit_ids(&commands[1], "CHOP"),
        ];
        let harvest_ids = [
            command_unit_ids(&commands[0], "HARVEST"),
            command_unit_ids(&commands[1], "HARVEST"),
        ];
        let before_units: HashMap<_, _> = game
            .units
            .iter()
            .map(|unit| (unit.id, (unit.player as usize, unit.pos(), unit.carry)))
            .collect();

        step(&mut game, &commands[0], &commands[1]);

        let after_units: HashMap<_, _> = game
            .units
            .iter()
            .map(|unit| (unit.id, unit.carry))
            .collect();
        for player in 0..2 {
            for id in &chop_ids[player] {
                let Some((actual_player, cell, before_carry)) = before_units.get(id) else {
                    continue;
                };
                let Some(after_carry) = after_units.get(id) else {
                    continue;
                };
                let gained = after_carry[WOOD] - before_carry[WOOD];
                if gained <= 0 || *actual_player != player {
                    continue;
                }
                attribution.add_wood(
                    usize::from(player != seat),
                    provenance.get(cell).copied().unwrap_or(Origin::Unknown),
                    gained,
                );
            }
            for id in &harvest_ids[player] {
                let Some((actual_player, cell, before_carry)) = before_units.get(id) else {
                    continue;
                };
                let Some(after_carry) = after_units.get(id) else {
                    continue;
                };
                if *actual_player != player {
                    continue;
                }
                let origin = provenance.get(cell).copied().unwrap_or(Origin::Unknown);
                for kind in 0..4 {
                    let gained = after_carry[kind] - before_carry[kind];
                    if gained > 0 {
                        attribution.add_fruit(usize::from(player != seat), origin, kind, gained);
                    }
                }
            }
        }
        let after_plants: HashSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        provenance.retain(|cell, _| after_plants.contains(cell));
        for cell in after_plants.difference(&before_plants) {
            let claimants: Vec<_> = (0..2)
                .filter(|player| attempts[*player].contains(cell))
                .collect();
            let origin = match claimants.as_slice() {
                [player] => {
                    let relative = usize::from(*player != seat);
                    attribution.successful_plants[relative] += 1;
                    if let Some(kind) = game
                        .plants
                        .iter()
                        .find(|plant| plant.pos() == *cell)
                        .and_then(|plant| fruit_index(&plant.plant_type))
                    {
                        attribution.successful_plants_by_kind[relative][kind] += 1;
                    }
                    if relative == 0 {
                        Origin::Ours
                    } else {
                        Origin::Opponent
                    }
                }
                _ => {
                    attribution.ambiguous_births += 1;
                    Origin::Unknown
                }
            };
            provenance.insert(*cell, origin);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    worker_three_audit.finish(&game, seat);
    let mut terminal_plants_by_kind = [0; 4];
    for plant in game.plants.iter().filter(|plant| plant.health > 0) {
        if let Some(kind) = fruit_index(&plant.plant_type) {
            terminal_plants_by_kind[kind] += 1;
        }
    }
    Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        own_inventory_wood: game.inventories[seat][WOOD],
        opponent_inventory_wood: game.inventories[1 - seat][WOOD],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        terminal_turn: game.turn,
        terminal_plants: game.plants.iter().filter(|plant| plant.health > 0).count(),
        terminal_banana_plants: game
            .plants
            .iter()
            .filter(|plant| plant.health > 0 && plant.plant_type == "BANANA")
            .count(),
        terminal_plants_by_kind,
        action_hash,
        terminal_state_hash: canonical_state_hash(&game),
        attribution,
        telemetry: ours.telemetry(),
        worker_three_audit,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    model: usize,
}

struct Row {
    task: Task,
    profile: Profile,
    outcome: Outcome,
}

fn run_task(task: Task, experiment: Experiment) -> Vec<Row> {
    let initial = generate_bronze(task.seed);
    experiment
        .profiles()
        .into_iter()
        .map(|profile| Row {
            task,
            profile,
            outcome: play(&initial, task.seat, task.model, profile),
        })
        .collect()
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(60);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "ownership-aware-complete-economy.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(20)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(1660);
    let experiment = Experiment::parse(args.get(5).map_or("ownership", String::as_str));
    let model_selector = args.get(6).map_or("all", String::as_str);
    let models: Vec<_> = if model_selector == "all" {
        (0..OPPONENTS.len()).collect()
    } else {
        vec![OPPONENTS
            .iter()
            .position(|name| *name == model_selector)
            .unwrap_or_else(|| panic!("unknown opponent {model_selector}"))]
    };
    let mut task_rows = Vec::new();
    for seed in seed_start..seed_start + seeds {
        for &model in &models {
            for seat in 0..2 {
                task_rows.push(Task { seed, seat, model });
            }
        }
    }
    let tasks = Arc::new(task_rows);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.extend(run_task(tasks[index], experiment));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("ownership panel worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.model,
            row.task.seat,
            row.profile.label(),
        )
    });
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    let mut header = "seed\tseat\topponent\tprofile\town_score\topponent_score\tmargin\town_inventory_wood\topponent_inventory_wood\tworkers\tterminal_turn\town_successful_plants\topponent_successful_plants\tambiguous_births\ttotal_chop_wood\tassigned_chop_wood\town_from_natural\town_from_ours\town_from_opponent\town_from_unknown\topponent_from_natural\topponent_from_ours\topponent_from_opponent\topponent_from_unknown\topponent_crops_seen\tactive_opponent_crops\tactivation_turns\tfirst_activation_turn\tbase_command_mismatches\tselected_targets\ttargets_disappeared_before_fruit\ttargets_fruited_after_selection\tcapacity_ready_turns\tcapacity_separation_violations\tcopied_move\tcopied_chop\tcopied_drop\tcopied_mine\tcopied_pick\tcopied_harvest\tcopied_plant\tentry_state_violations\tforbidden_post_entry_commands\tpost_entry_commands\tlineage_recovery_turns\tentry_banked_banana\tentry_carried_banana\tentry_crop_banana_fruits\tentry_opponent_banana_crops\tentry_own_score\tentry_opponent_score\tentry_margin\tterminal_plants\tterminal_banana_plants\torchard_activation_turn\torchard_seed_repaid_turn\torchard_market_turns\torchard_offers\torchard_selections\torchard_harvest_selections\torchard_first_selection_turn\torchard_forced_setup_actions\torchard_premarket_mismatches\tfresh_harvest_commitments\tfresh_harvest_first_turn\tfresh_harvest_successful_plants\tfresh_harvest_precommit_mismatches\tfresh_harvest_shadow_divergence_turns\tbanana_factory_active\tbanana_factory_activation_turn\tbanana_factory_selector_decided\tbanana_factory_selector_selected\tbanana_factory_initial_budget\tbanana_factory_bootstrap_attempts\tbanana_factory_bootstrap_successes\tbanana_factory_reserve_promotions\tbanana_factory_reserve_losses\tbanana_factory_harvest_selections\tbanana_factory_harvest_successes\tbanana_factory_bank_harvest_selections\tbanana_factory_bank_harvest_successes\tbanana_factory_conversion_harvest_selections\tbanana_factory_conversion_harvest_successes\tbanana_factory_renewable_plant_attempts\tbanana_factory_renewable_plant_successes\tbanana_factory_trained_role_rewrites\tbanana_factory_trained_forbidden_commands\tbanana_factory_tracked_live_crops\tbanana_factory_preactivation_mismatches\tbanana_factory_shadow_divergence_turns\taction_hash\tterminal_state_hash"
        .split('\t')
        .map(str::to_string)
        .collect::<Vec<_>>();
    header.extend(
        [
            "banana_factory_opponent_crop_policy_selections",
            "banana_factory_trained_opponent_crop_selections",
            "banana_factory_worker_three_bridge_funding_turns",
            "banana_factory_worker_three_bridge_plum_harvest_selections",
            "banana_factory_worker_three_bridge_lemon_harvest_selections",
            "banana_factory_worker_three_bridge_apple_harvest_selections",
            "banana_factory_worker_three_bridge_plum_harvest_successes",
            "banana_factory_worker_three_bridge_lemon_harvest_successes",
            "banana_factory_worker_three_bridge_apple_harvest_successes",
            "banana_factory_worker_three_bridge_iron_mine_selections",
            "banana_factory_worker_three_bridge_iron_mine_successes",
            "banana_factory_worker_three_bridge_train_attempts",
            "banana_factory_worker_three_bridge_train_successes",
            "banana_factory_worker_three_bridge_trained_turn",
            "banana_factory_worker_three_bridge_forbidden_commands",
            "banana_factory_worker_three_bridge_post_training_commands",
            "banana_factory_initial_plants",
            "banana_factory_initial_ripe_plants",
            "banana_factory_initial_fruits",
            "banana_factory_initial_banana_plants",
            "banana_factory_initial_banana_fruits",
            "banana_factory_initial_shack_distance",
            "banana_factory_activation_own_score",
            "banana_factory_activation_opponent_score",
            "banana_factory_activation_own_banked_fruit",
            "banana_factory_activation_opponent_banked_fruit",
            "banana_factory_activation_opponent_banana",
            "banana_factory_activation_opponent_iron",
            "banana_factory_activation_opponent_wood",
            "banana_factory_activation_opponent_workers",
            "banana_factory_activation_opponent_ms_sum",
            "banana_factory_activation_opponent_cc_sum",
            "banana_factory_activation_opponent_hp_sum",
            "banana_factory_activation_opponent_chop_sum",
            "banana_factory_activation_opponent_ms_max",
            "banana_factory_activation_opponent_cc_max",
            "banana_factory_activation_opponent_hp_max",
            "banana_factory_activation_opponent_chop_max",
            "banana_factory_activation_plants",
            "banana_factory_activation_ripe_plants",
            "banana_factory_activation_fruits",
            "banana_factory_activation_banana_plants",
            "banana_factory_activation_banana_fruits",
            "banana_factory_activation_opponent_carried_fruit",
            "banana_factory_activation_opponent_carried_wood",
            "banana_factory_activation_opponent_crops_seen",
            "worker3_two_worker_turns",
            "worker3_shack_occupied_turns",
            "worker3_balanced_affordable_turns",
            "worker3_balanced_carried_affordable_turns",
            "worker3_balanced_spawn_legal_turns",
            "worker3_balanced_first_affordable_turn",
            "worker3_balanced_first_spawn_legal_turn",
            "worker3_balanced_last_spawn_legal_turn",
            "worker3_balanced_longest_spawn_legal_run",
            "worker3_balanced_min_total_deficit",
            "worker3_balanced_best_deficit_turn",
            "worker3_balanced_best_deficit_plum",
            "worker3_balanced_best_deficit_lemon",
            "worker3_balanced_best_deficit_apple",
            "worker3_balanced_best_deficit_iron",
            "worker3_balanced_plum_deficit_turns",
            "worker3_balanced_lemon_deficit_turns",
            "worker3_balanced_apple_deficit_turns",
            "worker3_balanced_iron_deficit_turns",
            "worker3_poststock_affordable_turns",
            "worker3_fruit_materializable_turns",
            "worker3_first_fruit_materializable_turn",
            "worker3_longest_fruit_materializable_run",
            "worker3_poststock_min_total_deficit",
            "worker3_poststock_best_deficit_turn",
            "worker3_poststock_best_deficit_plum",
            "worker3_poststock_best_deficit_lemon",
            "worker3_poststock_best_deficit_apple",
            "worker3_poststock_best_deficit_iron",
            "worker3_max_poststock_plum",
            "worker3_max_poststock_lemon",
            "worker3_max_poststock_apple",
            "worker3_max_poststock_iron",
            "worker3_cheap_affordable_turns",
            "worker3_cheap_spawn_legal_turns",
            "worker3_cheap_first_spawn_legal_turn",
            "worker3_terminal_bank_plum",
            "worker3_terminal_bank_lemon",
            "worker3_terminal_bank_apple",
            "worker3_terminal_bank_banana",
            "worker3_terminal_bank_iron",
            "worker3_terminal_bank_wood",
            "worker3_terminal_carry_plum",
            "worker3_terminal_carry_lemon",
            "worker3_terminal_carry_apple",
            "worker3_terminal_carry_banana",
            "worker3_terminal_carry_iron",
            "worker3_terminal_carry_wood",
        ]
        .into_iter()
        .map(str::to_string),
    );
    for collector in ["own", "opponent"] {
        for kind in FRUIT_NAMES {
            header.push(format!("{collector}_plant_commands_{kind}"));
        }
    }
    for collector in ["own", "opponent"] {
        for kind in FRUIT_NAMES {
            header.push(format!("{collector}_successful_plants_{kind}"));
        }
    }
    for kind in FRUIT_NAMES {
        header.push(format!("terminal_plants_{kind}"));
    }
    header.extend([
        "total_harvested_fruit".to_string(),
        "assigned_harvested_fruit".to_string(),
    ]);
    for collector in ["own", "opponent"] {
        for origin in ORIGIN_NAMES {
            for kind in FRUIT_NAMES {
                header.push(format!("{collector}_fruit_from_{origin}_{kind}"));
            }
        }
    }
    writeln!(writer, "{}", header.join("\t")).expect("write header");
    for row in rows {
        let out = row.outcome;
        let wood = out.attribution.wood;
        let mut fields = vec![
            row.task.seed.to_string(),
            row.task.seat.to_string(),
            OPPONENTS[row.task.model].to_string(),
            row.profile.label().to_string(),
            out.own_score.to_string(),
            out.opponent_score.to_string(),
            (out.own_score - out.opponent_score).to_string(),
            out.own_inventory_wood.to_string(),
            out.opponent_inventory_wood.to_string(),
            out.workers.to_string(),
            out.terminal_turn.to_string(),
            out.attribution.successful_plants[0].to_string(),
            out.attribution.successful_plants[1].to_string(),
            out.attribution.ambiguous_births.to_string(),
            out.attribution.total_wood().to_string(),
            out.attribution.assigned_wood().to_string(),
            wood[0][0].to_string(),
            wood[0][1].to_string(),
            wood[0][2].to_string(),
            wood[0][3].to_string(),
            wood[1][0].to_string(),
            wood[1][1].to_string(),
            wood[1][2].to_string(),
            wood[1][3].to_string(),
            out.telemetry.opponent_crops_seen.to_string(),
            out.telemetry.active_opponent_crops.to_string(),
            out.telemetry.activation_turns.to_string(),
            out.telemetry
                .first_activation_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry.base_command_mismatches.to_string(),
            out.telemetry.selected_targets.to_string(),
            out.telemetry.targets_disappeared_before_fruit.to_string(),
            out.telemetry.targets_fruited_after_selection.to_string(),
            out.telemetry.capacity_ready_turns.to_string(),
            out.telemetry.capacity_separation_violations.to_string(),
            out.telemetry.copied_verbs[0].to_string(),
            out.telemetry.copied_verbs[1].to_string(),
            out.telemetry.copied_verbs[2].to_string(),
            out.telemetry.copied_verbs[3].to_string(),
            out.telemetry.copied_verbs[4].to_string(),
            out.telemetry.copied_verbs[5].to_string(),
            out.telemetry.copied_verbs[6].to_string(),
            out.telemetry.entry_state_violations.to_string(),
            out.telemetry.forbidden_post_entry_commands.to_string(),
            out.telemetry.post_entry_commands.to_string(),
            out.telemetry.lineage_recovery_turns.to_string(),
            out.telemetry.entry_banked_banana.to_string(),
            out.telemetry.entry_carried_banana.to_string(),
            out.telemetry.entry_crop_banana_fruits.to_string(),
            out.telemetry.entry_opponent_banana_crops.to_string(),
            out.telemetry.entry_own_score.to_string(),
            out.telemetry.entry_opponent_score.to_string(),
            out.telemetry.entry_margin.to_string(),
            out.terminal_plants.to_string(),
            out.terminal_banana_plants.to_string(),
            out.telemetry
                .orchard_activation_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry
                .orchard_seed_repaid_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry.orchard_market_turns.to_string(),
            out.telemetry.orchard_offers.to_string(),
            out.telemetry.orchard_selections.to_string(),
            out.telemetry.orchard_harvest_selections.to_string(),
            out.telemetry
                .orchard_first_selection_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry.orchard_forced_setup_actions.to_string(),
            out.telemetry.orchard_premarket_mismatches.to_string(),
            out.telemetry.fresh_harvest_commitments.to_string(),
            out.telemetry
                .fresh_harvest_first_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry.fresh_harvest_successful_plants.to_string(),
            out.telemetry.fresh_harvest_precommit_mismatches.to_string(),
            out.telemetry
                .fresh_harvest_shadow_divergence_turns
                .to_string(),
            out.telemetry.banana_factory_active.to_string(),
            out.telemetry
                .banana_factory_activation_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry.banana_factory_selector_decided.to_string(),
            out.telemetry.banana_factory_selector_selected.to_string(),
            out.telemetry.banana_factory_initial_budget.to_string(),
            out.telemetry.banana_factory_bootstrap_attempts.to_string(),
            out.telemetry.banana_factory_bootstrap_successes.to_string(),
            out.telemetry.banana_factory_reserve_promotions.to_string(),
            out.telemetry.banana_factory_reserve_losses.to_string(),
            out.telemetry.banana_factory_harvest_selections.to_string(),
            out.telemetry.banana_factory_harvest_successes.to_string(),
            out.telemetry
                .banana_factory_bank_harvest_selections
                .to_string(),
            out.telemetry
                .banana_factory_bank_harvest_successes
                .to_string(),
            out.telemetry
                .banana_factory_conversion_harvest_selections
                .to_string(),
            out.telemetry
                .banana_factory_conversion_harvest_successes
                .to_string(),
            out.telemetry
                .banana_factory_renewable_plant_attempts
                .to_string(),
            out.telemetry
                .banana_factory_renewable_plant_successes
                .to_string(),
            out.telemetry
                .banana_factory_trained_role_rewrites
                .to_string(),
            out.telemetry
                .banana_factory_trained_forbidden_commands
                .to_string(),
            out.telemetry.banana_factory_tracked_live_crops.to_string(),
            out.telemetry
                .banana_factory_preactivation_mismatches
                .to_string(),
            out.telemetry
                .banana_factory_shadow_divergence_turns
                .to_string(),
            out.action_hash.to_string(),
            out.terminal_state_hash.to_string(),
        ];
        fields.extend([
            out.telemetry
                .banana_factory_opponent_crop_policy_selections
                .to_string(),
            out.telemetry
                .banana_factory_trained_opponent_crop_selections
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_funding_turns
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_selections[0]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_selections[1]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_selections[2]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_successes[0]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_successes[1]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_fruit_harvest_successes[2]
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_iron_mine_selections
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_iron_mine_successes
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_train_attempts
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_train_successes
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_trained_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_forbidden_commands
                .to_string(),
            out.telemetry
                .banana_factory_worker_three_bridge_post_training_commands
                .to_string(),
            out.telemetry.banana_factory_initial_plants.to_string(),
            out.telemetry.banana_factory_initial_ripe_plants.to_string(),
            out.telemetry.banana_factory_initial_fruits.to_string(),
            out.telemetry
                .banana_factory_initial_banana_plants
                .to_string(),
            out.telemetry
                .banana_factory_initial_banana_fruits
                .to_string(),
            out.telemetry
                .banana_factory_initial_shack_distance
                .to_string(),
            out.telemetry
                .banana_factory_activation_own_score
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_score
                .to_string(),
            out.telemetry
                .banana_factory_activation_own_banked_fruit
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_banked_fruit
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_banana
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_iron
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_wood
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_workers
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_ms_sum
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_cc_sum
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_hp_sum
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_chop_sum
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_ms_max
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_cc_max
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_hp_max
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_chop_max
                .to_string(),
            out.telemetry.banana_factory_activation_plants.to_string(),
            out.telemetry
                .banana_factory_activation_ripe_plants
                .to_string(),
            out.telemetry.banana_factory_activation_fruits.to_string(),
            out.telemetry
                .banana_factory_activation_banana_plants
                .to_string(),
            out.telemetry
                .banana_factory_activation_banana_fruits
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_carried_fruit
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_carried_wood
                .to_string(),
            out.telemetry
                .banana_factory_activation_opponent_crops_seen
                .to_string(),
            out.worker_three_audit.two_worker_turns.to_string(),
            out.worker_three_audit.shack_occupied_turns.to_string(),
            out.worker_three_audit.balanced_affordable_turns.to_string(),
            out.worker_three_audit
                .balanced_carried_affordable_turns
                .to_string(),
            out.worker_three_audit
                .balanced_spawn_legal_turns
                .to_string(),
            out.worker_three_audit
                .balanced_first_affordable_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit
                .balanced_first_spawn_legal_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit
                .balanced_last_spawn_legal_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit
                .balanced_longest_spawn_legal_run
                .to_string(),
            out.worker_three_audit
                .balanced_min_total_deficit
                .to_string(),
            out.worker_three_audit
                .balanced_best_deficit_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit.balanced_best_deficit[0].to_string(),
            out.worker_three_audit.balanced_best_deficit[1].to_string(),
            out.worker_three_audit.balanced_best_deficit[2].to_string(),
            out.worker_three_audit.balanced_best_deficit[3].to_string(),
            out.worker_three_audit.balanced_resource_deficit_turns[0].to_string(),
            out.worker_three_audit.balanced_resource_deficit_turns[1].to_string(),
            out.worker_three_audit.balanced_resource_deficit_turns[2].to_string(),
            out.worker_three_audit.balanced_resource_deficit_turns[3].to_string(),
            out.worker_three_audit
                .poststock_affordable_turns
                .to_string(),
            out.worker_three_audit
                .fruit_materializable_turns
                .to_string(),
            out.worker_three_audit
                .first_fruit_materializable_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit
                .longest_fruit_materializable_run
                .to_string(),
            out.worker_three_audit
                .poststock_min_total_deficit
                .to_string(),
            out.worker_three_audit
                .poststock_best_deficit_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit.poststock_best_deficit[0].to_string(),
            out.worker_three_audit.poststock_best_deficit[1].to_string(),
            out.worker_three_audit.poststock_best_deficit[2].to_string(),
            out.worker_three_audit.poststock_best_deficit[3].to_string(),
            out.worker_three_audit.maximum_poststock_available[0].to_string(),
            out.worker_three_audit.maximum_poststock_available[1].to_string(),
            out.worker_three_audit.maximum_poststock_available[2].to_string(),
            out.worker_three_audit.maximum_poststock_available[3].to_string(),
            out.worker_three_audit.cheap_affordable_turns.to_string(),
            out.worker_three_audit.cheap_spawn_legal_turns.to_string(),
            out.worker_three_audit
                .cheap_first_spawn_legal_turn
                .map_or(-1, |turn| turn)
                .to_string(),
            out.worker_three_audit.terminal_inventory[PLUM].to_string(),
            out.worker_three_audit.terminal_inventory[LEMON].to_string(),
            out.worker_three_audit.terminal_inventory[APPLE].to_string(),
            out.worker_three_audit.terminal_inventory[BANANA].to_string(),
            out.worker_three_audit.terminal_inventory[IRON].to_string(),
            out.worker_three_audit.terminal_inventory[WOOD].to_string(),
            out.worker_three_audit.terminal_carried[PLUM].to_string(),
            out.worker_three_audit.terminal_carried[LEMON].to_string(),
            out.worker_three_audit.terminal_carried[APPLE].to_string(),
            out.worker_three_audit.terminal_carried[BANANA].to_string(),
            out.worker_three_audit.terminal_carried[IRON].to_string(),
            out.worker_three_audit.terminal_carried[WOOD].to_string(),
        ]);
        for collector in 0..2 {
            for kind in 0..4 {
                fields.push(out.attribution.plant_commands_by_kind[collector][kind].to_string());
            }
        }
        for collector in 0..2 {
            for kind in 0..4 {
                fields.push(out.attribution.successful_plants_by_kind[collector][kind].to_string());
            }
        }
        for count in out.terminal_plants_by_kind {
            fields.push(count.to_string());
        }
        fields.push(out.attribution.total_fruit().to_string());
        fields.push(out.attribution.assigned_fruit().to_string());
        for collector in 0..2 {
            for origin in 0..4 {
                for kind in 0..4 {
                    fields.push(out.attribution.fruit[collector][origin][kind].to_string());
                }
            }
        }
        writeln!(writer, "{}", fields.join("\t")).expect("write row");
    }
    eprintln!(
        "saved {} scenarios x {} profiles to {}",
        tasks.len(),
        experiment.profiles().len(),
        output
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_common_cell_contains_all_profiles() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::Ownership,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "lean_m2c2h0k2", "ownership_aware"]
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn resident_chopper_cell_contains_three_profiles() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::ResidentChopper,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "lean_m2c2h0k2", "resident_chopper_hybrid"]
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn prefruit_cell_contains_three_profiles() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::PreFruit,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "lean_m2c2h0k2", "prefruit_interruption"]
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn capacity_separated_cell_contains_three_profiles() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::CapacitySeparated,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "adaptive_density", "capacity_separated_denial"]
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn lineage_collapse_cell_contains_three_profiles_and_clean_shadow() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::LineageCollapse,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            [
                "resident",
                "adaptive_density",
                "lineage_collapse_liquidation"
            ]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::LineageCollapse)
            .expect("candidate row");
        assert_eq!(candidate.outcome.telemetry.base_command_mismatches, 0);
        assert_eq!(candidate.outcome.telemetry.entry_state_violations, 0);
        assert_eq!(candidate.outcome.telemetry.forbidden_post_entry_commands, 0);
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn explicit_banana_kind_is_command_identical_to_adaptive_control() {
        let mut game = generate_bronze(0);
        let control = GoldElite::adaptive();
        let explicit = GoldElite::adaptive_farm_kind(BANANA);
        let opponent = GoldElite::new();
        let mut turns_until_end = 0;
        while game.turn <= TOTAL_TURNS {
            let control_commands = control.decide(&game, 0);
            assert_eq!(control_commands, explicit.decide(&game, 0));
            let opponent_commands = opponent.decide(&game, 1);
            step(&mut game, &control_commands, &opponent_commands);
            if has_stalled(&game, &mut turns_until_end) {
                break;
            }
        }
    }

    #[test]
    fn task_market_cell_contains_control_and_clean_candidate_prefix() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::TaskMarketOrchard,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "task_market_orchard"]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::TaskMarketOrchard)
            .expect("task-market candidate");
        assert_eq!(candidate.outcome.telemetry.orchard_premarket_mismatches, 0);
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn fresh_harvest_cell_contains_control_and_candidate() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::FreshHarvestRegeneration,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "fresh_harvest_regeneration"]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::FreshHarvestRegeneration)
            .expect("fresh-harvest candidate");
        assert_eq!(
            candidate
                .outcome
                .telemetry
                .fresh_harvest_precommit_mismatches,
            0
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn banana_seed_factory_cell_contains_control_and_candidate() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::BananaSeedFactory,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "banana_seed_factory"]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::BananaSeedFactory)
            .expect("banana seed-factory candidate");
        assert_eq!(
            candidate
                .outcome
                .telemetry
                .banana_factory_preactivation_mismatches,
            0
        );
        assert_eq!(
            candidate
                .outcome
                .telemetry
                .banana_factory_trained_forbidden_commands,
            0
        );
        let audit = candidate.outcome.worker_three_audit;
        assert!(audit.two_worker_turns > 0);
        assert!(audit.balanced_spawn_legal_turns <= audit.balanced_affordable_turns);
        assert!(audit.cheap_spawn_legal_turns <= audit.cheap_affordable_turns);
        assert!(audit.balanced_min_total_deficit >= 0);
        assert!(audit.fruit_materializable_turns <= audit.two_worker_turns);
        assert!(audit.poststock_min_total_deficit >= 0);
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn banana_factory_lineage_ablation_contains_both_factory_grammars() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::BananaFactoryLineageAblation,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            [
                "resident",
                "banana_seed_factory",
                "banana_seed_factory_source_separated"
            ]
        );
        let separated = rows
            .iter()
            .find(|row| row.profile == Profile::BananaSeedFactorySourceSeparated)
            .expect("source-separated candidate");
        assert_eq!(
            separated
                .outcome
                .telemetry
                .banana_factory_preactivation_mismatches,
            0
        );
        assert_eq!(
            separated
                .outcome
                .telemetry
                .banana_factory_trained_forbidden_commands,
            0
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn banana_factory_activation_selector_records_one_clean_decision() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::BananaFactoryActivationSelector,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "banana_seed_factory_activation_selector"]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::BananaSeedFactoryActivationSelector)
            .expect("activation-selector candidate");
        assert_eq!(
            candidate.outcome.telemetry.banana_factory_selector_decided,
            1
        );
        assert_eq!(
            candidate
                .outcome
                .telemetry
                .banana_factory_preactivation_mismatches,
            0
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn banana_factory_dual_value_ablation_contains_full_and_targeted_factories() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::BananaFactoryDualValueAblation,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            [
                "resident",
                "banana_seed_factory",
                "banana_seed_factory_dual_value_e6",
                "banana_seed_factory_trained_dual_value_e6"
            ]
        );
        let targeted = rows
            .iter()
            .find(|row| row.profile == Profile::BananaSeedFactoryDualValueE6)
            .expect("dual-value factory");
        assert_eq!(
            targeted
                .outcome
                .telemetry
                .banana_factory_preactivation_mismatches,
            0
        );
        assert_eq!(
            targeted
                .outcome
                .telemetry
                .banana_factory_trained_forbidden_commands,
            0
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn banana_factory_worker_three_bridge_contains_exact_factory_control() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::BananaFactoryWorkerThreeBridge,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            [
                "resident",
                "banana_seed_factory",
                "banana_seed_factory_worker_three_bridge"
            ]
        );
        let bridge = rows
            .iter()
            .find(|row| row.profile == Profile::BananaSeedFactoryWorkerThreeBridge)
            .expect("worker-three bridge");
        assert_eq!(
            bridge
                .outcome
                .telemetry
                .banana_factory_preactivation_mismatches,
            0
        );
        assert_eq!(
            bridge
                .outcome
                .telemetry
                .banana_factory_worker_three_bridge_forbidden_commands,
            0
        );
        assert!(rows.iter().all(|row| row.outcome.terminal_turn > 1));
    }

    #[test]
    fn species_separated_cell_plants_only_plum() {
        let rows = run_task(
            Task {
                seed: 0,
                seat: 0,
                model: 1,
            },
            Experiment::SpeciesSeparated,
        );
        assert_eq!(
            rows.iter()
                .map(|row| row.profile.label())
                .collect::<Vec<_>>(),
            ["resident", "adaptive_density", "species_separated_plum"]
        );
        let candidate = rows
            .iter()
            .find(|row| row.profile == Profile::SpeciesSeparated)
            .expect("species candidate");
        assert!(candidate.outcome.attribution.plant_commands_by_kind[0][0] > 0);
        assert_eq!(
            candidate.outcome.attribution.plant_commands_by_kind[0][1..],
            [0, 0, 0]
        );
        assert!(candidate.outcome.attribution.successful_plants_by_kind[0][0] > 0);
        assert_eq!(
            candidate.outcome.attribution.successful_plants_by_kind[0][1..],
            [0, 0, 0]
        );
    }
}
