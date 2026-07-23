//! Exact full-game environment for a resident-aware residual policy.
//!
//! The stable resident proposes one joint command per referee turn.  The
//! learned policy sees those intents and sequentially chooses KEEP or one
//! executable local action for each resident unit.  Stage A deliberately
//! masks all alternative MOVE targets, preserving the resident's routing.

use std::collections::BTreeMap;

use crate::game::engine::{has_stalled, step, WOOD};
use crate::game::mapgen::generate_bronze;
use crate::game::state::{GameState, Unit};
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
use crate::strategies::Strategy;

pub const RESIDUAL_OBS_CHANNELS: usize = 137;
pub const RESIDUAL_OBS_HEIGHT: usize = 11;
pub const RESIDUAL_OBS_WIDTH: usize = 22;
pub const RESIDUAL_OBS_CELLS: usize = RESIDUAL_OBS_HEIGHT * RESIDUAL_OBS_WIDTH;
pub const RESIDUAL_OBS_SIZE: usize = RESIDUAL_OBS_CHANNELS * RESIDUAL_OBS_CELLS;
pub const RESIDUAL_ACTION_PLANES: usize = 13;
pub const RESIDUAL_ACTION_SIZE: usize = RESIDUAL_ACTION_PLANES * RESIDUAL_OBS_CELLS;

const ITEM_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

#[inline]
fn spatial(x: i32, y: i32) -> usize {
    y as usize * RESIDUAL_OBS_WIDTH + x as usize
}

#[inline]
fn action(plane: usize, x: i32, y: i32) -> usize {
    plane * RESIDUAL_OBS_CELLS + spatial(x, y)
}

#[inline]
fn quant(value: f32, scale: f32) -> u8 {
    if scale <= 0.0 {
        return 0;
    }
    (255.0 * value / scale).round().clamp(0.0, 255.0) as u8
}

#[inline]
fn quant_signed(value: f32, magnitude: f32) -> u8 {
    quant(
        value.clamp(-magnitude, magnitude) + magnitude,
        2.0 * magnitude,
    )
}

fn verb(command: &str) -> &str {
    command.split_whitespace().next().unwrap_or("WAIT")
}

fn item_index(value: &str) -> Option<usize> {
    ITEM_NAMES.iter().position(|name| *name == value)
}

fn per_unit_actions(commands: &[String], own_ids: &[i32]) -> BTreeMap<i32, String> {
    let mut actions = BTreeMap::new();
    let mut waits = 0usize;
    for command in commands {
        let fields: Vec<_> = command.split_whitespace().collect();
        match fields.first().copied() {
            Some("WAIT") => waits += 1,
            Some("MOVE" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK") => {
                if let Some(id) = fields.get(1).and_then(|value| value.parse::<i32>().ok()) {
                    actions.insert(id, command.clone());
                }
            }
            _ => {}
        }
    }
    for &id in own_ids {
        if waits == 0 {
            break;
        }
        if let std::collections::btree_map::Entry::Vacant(entry) = actions.entry(id) {
            entry.insert("WAIT".to_string());
            waits -= 1;
        }
    }
    actions
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

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ResidualOpponentMode {
    Resident,
    GoldAdaptive,
    CompactGold,
    NorxondorThree,
    LegendBalanced,
    MyBot,
}

impl ResidualOpponentMode {
    const ALL: [Self; 6] = [
        Self::Resident,
        Self::GoldAdaptive,
        Self::CompactGold,
        Self::NorxondorThree,
        Self::LegendBalanced,
        Self::MyBot,
    ];

    fn from_index(index: usize) -> Self {
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
        }
    }
}

#[derive(Clone)]
enum OpponentPolicy {
    Resident(SecureOrchardBot),
    GoldAdaptive(GoldElite),
    CompactGold(CompactGold),
    NorxondorThree(NorxondorNative),
    LegendBalanced(LegendFieldProxyV2),
    MyBot(MyBot),
}

impl OpponentPolicy {
    fn new(mode: ResidualOpponentMode) -> Self {
        match mode {
            ResidualOpponentMode::Resident => Self::Resident(SecureOrchardBot::new()),
            ResidualOpponentMode::GoldAdaptive => Self::GoldAdaptive(GoldElite::adaptive()),
            ResidualOpponentMode::CompactGold => Self::CompactGold(CompactGold::new()),
            ResidualOpponentMode::NorxondorThree => {
                Self::NorxondorThree(NorxondorNative::new(true))
            }
            ResidualOpponentMode::LegendBalanced => {
                Self::LegendBalanced(LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }))
            }
            ResidualOpponentMode::MyBot => Self::MyBot(MyBot::new()),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&resident_view(game, player)),
            Self::GoldAdaptive(bot) => bot.decide(game, player),
            Self::CompactGold(bot) => bot.decide(game, player),
            Self::NorxondorThree(bot) => bot.decide(game, player),
            Self::LegendBalanced(bot) => bot.decide(game, player),
            Self::MyBot(bot) => bot.decide(game, player),
        }
    }
}

#[derive(Clone, Debug)]
struct Intent {
    command: String,
    age: u16,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ResidentResidualTerminal {
    pub reward: f32,
    pub done: bool,
    pub turns: u16,
    pub episode_return: f32,
    pub scenario_seed: u64,
    pub map_seed: u64,
    pub seat: u8,
    pub opponent: u8,
    pub margin: i32,
    pub wood_edge: i32,
    pub workers: u8,
    pub opponent_workers: u8,
    pub overrides: u16,
    pub residual_attempts: u16,
    pub rejected_actions: u16,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ResidentResidualProbe {
    pub scenario_seed: u64,
    pub map_seed: u64,
    pub seat: u8,
    pub opponent: u8,
    pub turn: u16,
    pub unit_id: i32,
    pub ordinal: u8,
    pub worker_count: u8,
    pub x: i32,
    pub y: i32,
    pub ms: i32,
    pub cc: i32,
    pub hp: i32,
    pub chop: i32,
    pub free: i32,
    pub carry: [i32; 6],
    pub inventory: [i32; 6],
    pub score: i32,
    pub opponent_score: i32,
    pub wood_edge: i32,
    pub plants: u16,
    pub local_plant_type: String,
    pub local_plant_health: i32,
    pub local_plant_fruits: i32,
    pub near_home: bool,
    pub near_iron: bool,
    pub resident_command: String,
    pub resident_plane: i8,
    pub previous_command: String,
    pub previous_plane: i8,
    pub other_command: String,
    pub other_plane: i8,
    pub intent_age: u16,
    pub legal_actions: u8,
}

#[derive(Clone)]
pub struct ResidentResidualEnv {
    pub state: GameState,
    scenario_seed: u64,
    map_seed: u64,
    seat: usize,
    opponent_mode: ResidualOpponentMode,
    opponent: OpponentPolicy,
    resident: SecureOrchardBot,
    max_turns: u16,
    stall_counter: i32,
    unit_ids: Vec<i32>,
    resident_commands: Vec<String>,
    base_actions: BTreeMap<i32, String>,
    actual_actions: BTreeMap<i32, String>,
    non_unit_commands: Vec<String>,
    current_intent_ages: BTreeMap<i32, u16>,
    previous_intents: BTreeMap<i32, Intent>,
    decision_phase: usize,
    previous_margin: i32,
    episode_return: f32,
    overrides: u16,
    residual_attempts: u16,
    rejected_actions: u16,
}

impl ResidentResidualEnv {
    pub fn new(scenario_seed: u64, max_turns: u16) -> Self {
        let map_seed = scenario_seed / 12;
        let seat = ((scenario_seed / 6) % 2) as usize;
        let opponent_mode = ResidualOpponentMode::from_index(scenario_seed as usize % 6);
        let state = generate_bronze(map_seed);
        let initial_margin = state.scores[seat] - state.scores[1 - seat];
        let mut env = Self {
            state,
            scenario_seed,
            map_seed,
            seat,
            opponent_mode,
            opponent: OpponentPolicy::new(opponent_mode),
            resident: SecureOrchardBot::new(),
            max_turns,
            stall_counter: 0,
            unit_ids: Vec::new(),
            resident_commands: Vec::new(),
            base_actions: BTreeMap::new(),
            actual_actions: BTreeMap::new(),
            non_unit_commands: Vec::new(),
            current_intent_ages: BTreeMap::new(),
            previous_intents: BTreeMap::new(),
            decision_phase: 0,
            previous_margin: initial_margin,
            episode_return: 0.0,
            overrides: 0,
            residual_attempts: 0,
            rejected_actions: 0,
        };
        env.prepare_turn();
        env
    }

    pub fn seat(&self) -> usize {
        self.seat
    }

    pub fn opponent_mode(&self) -> ResidualOpponentMode {
        self.opponent_mode
    }

    fn own_units(&self) -> Vec<&Unit> {
        let mut units: Vec<_> = self
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize == self.seat)
            .collect();
        units.sort_by_key(|unit| unit.id);
        units
    }

    fn active_unit(&self) -> &Unit {
        let id = self.unit_ids[self.decision_phase];
        self.state
            .units
            .iter()
            .find(|unit| unit.id == id)
            .expect("active resident unit")
    }

    fn prepare_turn(&mut self) {
        self.resident_commands = self
            .resident
            .commands(&resident_view(&self.state, self.seat));
        self.unit_ids = self.own_units().iter().map(|unit| unit.id).collect();
        self.base_actions = per_unit_actions(&self.resident_commands, &self.unit_ids);
        for &id in &self.unit_ids {
            self.base_actions
                .entry(id)
                .or_insert_with(|| "WAIT".to_string());
        }
        self.actual_actions = self.base_actions.clone();
        self.non_unit_commands = self
            .resident_commands
            .iter()
            .filter(|command| matches!(verb(command), "TRAIN" | "MSG"))
            .cloned()
            .collect();
        self.current_intent_ages.clear();
        for (&id, command) in &self.base_actions {
            let age = self
                .previous_intents
                .get(&id)
                .filter(|previous| previous.command == *command)
                .map_or(1, |previous| previous.age.saturating_add(1));
            self.current_intent_ages.insert(id, age);
        }
        self.decision_phase = 0;
    }

    fn near_home(&self, unit: &Unit) -> bool {
        (unit.x - self.state.shacks[self.seat].0).abs()
            + (unit.y - self.state.shacks[self.seat].1).abs()
            <= 1
    }

    fn near_iron(&self, unit: &Unit) -> bool {
        [
            (unit.x, unit.y + 1),
            (unit.x + 1, unit.y),
            (unit.x, unit.y - 1),
            (unit.x - 1, unit.y),
        ]
        .into_iter()
        .any(|cell| self.state.iron.contains(&cell))
    }

    fn local_legal(&self, unit: &Unit, plane: usize) -> bool {
        let plant = self
            .state
            .plants
            .iter()
            .find(|plant| plant.pos() == unit.pos());
        match plane {
            1 => plant.is_some_and(|plant| plant.fruits > 0) && unit.hp > 0 && unit.free() > 0,
            2 => plant.is_some() && unit.chop > 0,
            3 => self.near_home(unit) && unit.total() > 0,
            4 => self.near_iron(unit) && unit.chop > 0 && unit.free() > 0,
            5..=8 => {
                let item = plane - 5;
                self.state.walkable.contains(&unit.pos()) && plant.is_none() && unit.carry[item] > 0
            }
            9..=12 => {
                let item = plane - 9;
                self.near_home(unit)
                    && unit.free() > 0
                    && self.state.inventories[self.seat][item] > 0
            }
            _ => false,
        }
    }

    fn local_action_count(&self, unit: &Unit) -> usize {
        (1..RESIDUAL_ACTION_PLANES)
            .filter(|&plane| self.local_legal(unit, plane))
            .count()
    }

    pub fn keep_action(&self) -> usize {
        let unit = self.active_unit();
        action(0, unit.x, unit.y)
    }

    pub fn legal_actions(&self) -> Vec<usize> {
        let active = self.active_unit();
        let mut actions = vec![self.keep_action()];
        for plane in 1..RESIDUAL_ACTION_PLANES {
            if actions.len() < 7 && self.local_legal(active, plane) {
                actions.push(action(plane, active.x, active.y));
            }
        }
        actions
    }

    pub fn command_for_action(&self, selected_action: usize) -> String {
        self.selected_command(selected_action)
    }

    pub fn probe(&self) -> ResidentResidualProbe {
        let active = self.active_unit();
        let resident_command = self
            .base_actions
            .get(&active.id)
            .cloned()
            .unwrap_or_else(|| "WAIT".to_string());
        let previous_command = self
            .previous_intents
            .get(&active.id)
            .map_or("WAIT", |intent| intent.command.as_str())
            .to_string();
        let other = self
            .own_units()
            .into_iter()
            .find(|unit| unit.id != active.id);
        let other_command = other
            .and_then(|unit| self.base_actions.get(&unit.id))
            .map_or("WAIT", String::as_str)
            .to_string();
        let plane = |command: &str, current: (i32, i32)| {
            Self::command_plane_target(command, current).map_or(-1, |(plane, _)| plane as i8)
        };
        let local_plant = self
            .state
            .plants
            .iter()
            .find(|plant| plant.pos() == active.pos());
        ResidentResidualProbe {
            scenario_seed: self.scenario_seed,
            map_seed: self.map_seed,
            seat: self.seat as u8,
            opponent: self.opponent_mode.id(),
            turn: self.state.turn.clamp(0, u16::MAX as i32) as u16,
            unit_id: active.id,
            ordinal: self.decision_phase.min(u8::MAX as usize) as u8,
            worker_count: self.unit_ids.len().min(u8::MAX as usize) as u8,
            x: active.x,
            y: active.y,
            ms: active.ms,
            cc: active.cc,
            hp: active.hp,
            chop: active.chop,
            free: active.free(),
            carry: active.carry,
            inventory: self.state.inventories[self.seat],
            score: self.state.scores[self.seat],
            opponent_score: self.state.scores[1 - self.seat],
            wood_edge: self.state.inventories[self.seat][WOOD]
                - self.state.inventories[1 - self.seat][WOOD],
            plants: self.state.plants.len().min(u16::MAX as usize) as u16,
            local_plant_type: local_plant
                .map_or("-", |plant| plant.plant_type.as_str())
                .to_string(),
            local_plant_health: local_plant.map_or(-1, |plant| plant.health),
            local_plant_fruits: local_plant.map_or(-1, |plant| plant.fruits),
            near_home: self.near_home(active),
            near_iron: self.near_iron(active),
            resident_plane: plane(&resident_command, active.pos()),
            resident_command,
            previous_plane: plane(&previous_command, active.pos()),
            previous_command,
            other_plane: other.map_or(-1, |unit| plane(&other_command, unit.pos())),
            other_command,
            intent_age: *self.current_intent_ages.get(&active.id).unwrap_or(&1),
            legal_actions: self.legal_actions().len() as u8,
        }
    }

    pub fn finish_with_keep(&mut self) -> ResidentResidualTerminal {
        loop {
            let terminal = self.step(self.keep_action());
            if terminal.done {
                return terminal;
            }
        }
    }

    fn selected_command(&self, selected_action: usize) -> String {
        let unit = self.active_unit();
        let keep = self
            .base_actions
            .get(&unit.id)
            .cloned()
            .unwrap_or_else(|| "WAIT".to_string());
        if selected_action >= RESIDUAL_ACTION_SIZE || selected_action == self.keep_action() {
            return keep;
        }
        let plane = selected_action / RESIDUAL_OBS_CELLS;
        let cell = selected_action % RESIDUAL_OBS_CELLS;
        if cell != spatial(unit.x, unit.y) || !self.local_legal(unit, plane) {
            return keep;
        }
        match plane {
            1 => format!("HARVEST {}", unit.id),
            2 => format!("CHOP {}", unit.id),
            3 => format!("DROP {}", unit.id),
            4 => format!("MINE {}", unit.id),
            5..=8 => format!("PLANT {} {}", unit.id, ITEM_NAMES[plane - 5]),
            9..=12 => format!("PICK {} {}", unit.id, ITEM_NAMES[plane - 9]),
            _ => keep,
        }
    }

    fn command_plane_target(command: &str, current: (i32, i32)) -> Option<(usize, (i32, i32))> {
        let fields: Vec<_> = command.split_whitespace().collect();
        match fields.first().copied().unwrap_or("WAIT") {
            "WAIT" => Some((0, current)),
            "MOVE" => Some((
                0,
                (
                    fields.get(2)?.parse::<i32>().ok()?,
                    fields.get(3)?.parse::<i32>().ok()?,
                ),
            )),
            "HARVEST" => Some((1, current)),
            "CHOP" => Some((2, current)),
            "DROP" => Some((3, current)),
            "MINE" => Some((4, current)),
            "PLANT" => Some((5 + item_index(fields.get(2)?)?, current)),
            "PICK" => Some((9 + item_index(fields.get(2)?)?, current)),
            _ => None,
        }
    }

    fn fill_broadcast(&self, obs: &mut [u8], channel: usize, value: u8) {
        let base = channel * RESIDUAL_OBS_CELLS;
        for y in 0..self.state.height {
            for x in 0..self.state.width {
                obs[base + spatial(x, y)] = value;
            }
        }
    }

    fn encode_intent(&self, obs: &mut [u8], offset: usize, command: &str, unit: &Unit) {
        let Some((plane, target)) = Self::command_plane_target(command, unit.pos()) else {
            return;
        };
        if target.0 >= 0
            && target.1 >= 0
            && target.0 < self.state.width
            && target.1 < self.state.height
        {
            obs[(offset + plane) * RESIDUAL_OBS_CELLS + spatial(target.0, target.1)] = 255;
        }
    }

    pub fn observe(&self, obs: &mut [u8], mask: &mut [u8]) {
        assert_eq!(obs.len(), RESIDUAL_OBS_SIZE);
        assert_eq!(mask.len(), RESIDUAL_ACTION_SIZE);
        obs.fill(0);
        mask.fill(0);
        let active = self.active_unit();

        for y in 0..self.state.height {
            for x in 0..self.state.width {
                let cell = (x, y);
                let sc = spatial(x, y);
                obs[sc] = 255;
                obs[RESIDUAL_OBS_CELLS + sc] = if self.state.walkable.contains(&cell) {
                    255
                } else {
                    0
                };
                obs[2 * RESIDUAL_OBS_CELLS + sc] = if self.state.iron.contains(&cell) {
                    255
                } else {
                    0
                };
                obs[3 * RESIDUAL_OBS_CELLS + sc] = if self.state.water.contains(&cell) {
                    255
                } else {
                    0
                };
            }
        }
        obs[4 * RESIDUAL_OBS_CELLS
            + spatial(
                self.state.shacks[self.seat].0,
                self.state.shacks[self.seat].1,
            )] = 255;
        obs[5 * RESIDUAL_OBS_CELLS
            + spatial(
                self.state.shacks[1 - self.seat].0,
                self.state.shacks[1 - self.seat].1,
            )] = 255;
        obs[6 * RESIDUAL_OBS_CELLS + spatial(active.x, active.y)] = 255;

        for unit in &self.state.units {
            let own = unit.player as usize == self.seat;
            let sc = spatial(unit.x, unit.y);
            obs[(if own { 7 } else { 8 }) * RESIDUAL_OBS_CELLS + sc] = 255;
            let stats_base = if own { 9 } else { 14 };
            for (offset, (value, scale)) in [
                (unit.ms, 3.0),
                (unit.cc, 4.0),
                (unit.hp, 3.0),
                (unit.chop, 4.0),
                (unit.free(), 4.0),
            ]
            .into_iter()
            .enumerate()
            {
                obs[(stats_base + offset) * RESIDUAL_OBS_CELLS + sc] = quant(value as f32, scale);
            }
            let carry_base = if own { 19 } else { 25 };
            for item in 0..6 {
                obs[(carry_base + item) * RESIDUAL_OBS_CELLS + sc] =
                    quant(unit.carry[item] as f32, 4.0);
            }
        }

        for plant in &self.state.plants {
            let item = item_index(&plant.plant_type).expect("known plant item");
            let sc = spatial(plant.x, plant.y);
            let base = 31 + 6 * item;
            obs[base * RESIDUAL_OBS_CELLS + sc] = 255;
            obs[(base + 1) * RESIDUAL_OBS_CELLS + sc] = quant(plant.size as f32, 4.0);
            obs[(base + 2) * RESIDUAL_OBS_CELLS + sc] = quant(plant.health as f32, 24.0);
            obs[(base + 3) * RESIDUAL_OBS_CELLS + sc] = quant(plant.fruits as f32, 3.0);
            obs[(base + 4) * RESIDUAL_OBS_CELLS + sc] = quant(plant.cooldown as f32, 10.0);
            let wet = [
                (plant.x, plant.y + 1),
                (plant.x + 1, plant.y),
                (plant.x, plant.y - 1),
                (plant.x - 1, plant.y),
            ]
            .into_iter()
            .any(|cell| self.state.water.contains(&cell));
            obs[(base + 5) * RESIDUAL_OBS_CELLS + sc] = if wet { 255 } else { 0 };
        }

        for item in 0..6 {
            self.fill_broadcast(
                obs,
                55 + item,
                quant(self.state.inventories[self.seat][item] as f32, 30.0),
            );
            self.fill_broadcast(
                obs,
                61 + item,
                quant(self.state.inventories[1 - self.seat][item] as f32, 30.0),
            );
            self.fill_broadcast(obs, 67 + item, quant(active.carry[item] as f32, 4.0));
        }
        for (channel, value, scale) in [
            (73, active.ms, 3.0),
            (74, active.cc, 4.0),
            (75, active.hp, 3.0),
            (76, active.chop, 4.0),
            (77, active.free(), 4.0),
        ] {
            self.fill_broadcast(obs, channel, quant(value as f32, scale));
        }
        self.fill_broadcast(
            obs,
            78,
            quant(self.state.turn as f32, self.max_turns as f32),
        );
        self.fill_broadcast(
            obs,
            79,
            quant(
                (i32::from(self.max_turns) - self.state.turn).max(0) as f32,
                self.max_turns as f32,
            ),
        );
        self.fill_broadcast(obs, 80, quant(self.state.scores[self.seat] as f32, 500.0));
        self.fill_broadcast(
            obs,
            81,
            quant(self.state.scores[1 - self.seat] as f32, 500.0),
        );
        self.fill_broadcast(
            obs,
            82,
            quant_signed(
                (self.state.scores[self.seat] - self.state.scores[1 - self.seat]) as f32,
                400.0,
            ),
        );
        self.fill_broadcast(obs, 83, quant(self.unit_ids.len() as f32, 6.0));
        let opponent_workers = self
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize != self.seat)
            .count();
        self.fill_broadcast(obs, 84, quant(opponent_workers as f32, 6.0));
        self.fill_broadcast(obs, 85, if self.decision_phase == 0 { 255 } else { 0 });
        self.fill_broadcast(obs, 86, if self.decision_phase > 0 { 255 } else { 0 });
        self.fill_broadcast(obs, 87, if self.near_home(active) { 255 } else { 0 });
        self.fill_broadcast(obs, 88, if self.near_iron(active) { 255 } else { 0 });
        self.fill_broadcast(
            obs,
            89,
            if self
                .state
                .plants
                .iter()
                .any(|plant| plant.pos() == active.pos())
            {
                255
            } else {
                0
            },
        );
        self.fill_broadcast(obs, 90, quant(self.local_action_count(active) as f32, 6.0));
        self.fill_broadcast(
            obs,
            91,
            quant(
                f32::from(*self.current_intent_ages.get(&active.id).unwrap_or(&1)),
                16.0,
            ),
        );
        self.fill_broadcast(obs, 92, quant(self.state.plants.len() as f32, 64.0));
        self.fill_broadcast(
            obs,
            93,
            quant(self.state.inventories[self.seat][WOOD] as f32, 100.0),
        );
        self.fill_broadcast(
            obs,
            94,
            quant(self.state.inventories[1 - self.seat][WOOD] as f32, 100.0),
        );
        self.fill_broadcast(
            obs,
            95,
            quant_signed(
                (self.state.inventories[self.seat][WOOD]
                    - self.state.inventories[1 - self.seat][WOOD]) as f32,
                100.0,
            ),
        );
        self.fill_broadcast(obs, 96, quant(self.decision_phase as f32, 5.0));

        let base = self
            .base_actions
            .get(&active.id)
            .map_or("WAIT", String::as_str);
        self.encode_intent(obs, 98, base, active);
        if let Some(other) = self
            .own_units()
            .into_iter()
            .find(|unit| unit.id != active.id)
        {
            let command = self
                .base_actions
                .get(&other.id)
                .map_or("WAIT", String::as_str);
            self.encode_intent(obs, 111, command, other);
        }
        if let Some(previous) = self.previous_intents.get(&active.id) {
            self.encode_intent(obs, 124, &previous.command, active);
        }

        mask[self.keep_action()] = 1;
        let mut alternatives = 0usize;
        for plane in 1..RESIDUAL_ACTION_PLANES {
            if alternatives < 6 && self.local_legal(active, plane) {
                mask[action(plane, active.x, active.y)] = 1;
                alternatives += 1;
            }
        }
    }

    fn terminal(&self, reward: f32, done: bool) -> ResidentResidualTerminal {
        let workers = self
            .state
            .units
            .iter()
            .filter(|unit| unit.player as usize == self.seat)
            .count();
        ResidentResidualTerminal {
            reward,
            done,
            turns: self.state.turn.clamp(0, u16::MAX as i32) as u16,
            episode_return: self.episode_return,
            scenario_seed: self.scenario_seed,
            map_seed: self.map_seed,
            seat: self.seat as u8,
            opponent: self.opponent_mode.id(),
            margin: self.state.scores[self.seat] - self.state.scores[1 - self.seat],
            wood_edge: self.state.inventories[self.seat][WOOD]
                - self.state.inventories[1 - self.seat][WOOD],
            workers: workers.min(u8::MAX as usize) as u8,
            opponent_workers: (self.state.units.len() - workers).min(u8::MAX as usize) as u8,
            overrides: self.overrides,
            residual_attempts: self.residual_attempts,
            rejected_actions: self.rejected_actions,
        }
    }

    pub fn step(&mut self, selected_action: usize) -> ResidentResidualTerminal {
        let unit_id = self.unit_ids[self.decision_phase];
        let unit = self.active_unit();
        let keep_action = self.keep_action();
        let selected_plane = selected_action / RESIDUAL_OBS_CELLS;
        let selected_cell = selected_action % RESIDUAL_OBS_CELLS;
        let selected_valid = selected_action == keep_action
            || (selected_action < RESIDUAL_ACTION_SIZE
                && selected_cell == spatial(unit.x, unit.y)
                && self.local_legal(unit, selected_plane));
        if selected_action != keep_action {
            self.residual_attempts = self.residual_attempts.saturating_add(1);
        }
        if !selected_valid {
            self.rejected_actions = self.rejected_actions.saturating_add(1);
        }
        let selected = self.selected_command(selected_action);
        let base = self.base_actions.get(&unit_id).expect("base action");
        if selected != *base {
            self.overrides = self.overrides.saturating_add(1);
        }
        self.actual_actions.insert(unit_id, selected);
        if self.decision_phase + 1 < self.unit_ids.len() {
            self.decision_phase += 1;
            return self.terminal(0.0, false);
        }

        let mut ours = self.non_unit_commands.clone();
        ours.extend(
            self.unit_ids
                .iter()
                .map(|id| self.actual_actions.get(id).expect("actual action").clone()),
        );
        let theirs = self.opponent.commands(&self.state, 1 - self.seat);
        for (&id, command) in &self.base_actions {
            self.previous_intents.insert(
                id,
                Intent {
                    command: command.clone(),
                    age: *self.current_intent_ages.get(&id).unwrap_or(&1),
                },
            );
        }
        if self.seat == 0 {
            step(&mut self.state, &ours, &theirs);
        } else {
            step(&mut self.state, &theirs, &ours);
        }
        let margin = self.state.scores[self.seat] - self.state.scores[1 - self.seat];
        let reward = (margin - self.previous_margin) as f32 / 100.0;
        self.previous_margin = margin;
        self.episode_return += reward;
        let done = self.state.turn > i32::from(self.max_turns)
            || has_stalled(&self.state, &mut self.stall_counter);
        if !done {
            self.prepare_turn();
        }
        self.terminal(reward, done)
    }
}

pub struct ResidentResidualBatch {
    envs: Vec<ResidentResidualEnv>,
    next_seed: u64,
    max_turns: u16,
}

impl ResidentResidualBatch {
    pub fn new(num_envs: usize, seed_base: u64, max_turns: u16) -> Self {
        assert!(num_envs > 0);
        Self {
            envs: (0..num_envs)
                .map(|offset| ResidentResidualEnv::new(seed_base + offset as u64, max_turns))
                .collect(),
            next_seed: seed_base + num_envs as u64,
            max_turns,
        }
    }

    fn len(&self) -> usize {
        self.envs.len()
    }

    fn reset_slot(&mut self, index: usize) {
        let seed = self.next_seed;
        self.next_seed += 1;
        self.envs[index] = ResidentResidualEnv::new(seed, self.max_turns);
    }

    fn observe(&self, obs: &mut [u8], masks: &mut [u8]) {
        for (index, env) in self.envs.iter().enumerate() {
            env.observe(
                &mut obs[index * RESIDUAL_OBS_SIZE..(index + 1) * RESIDUAL_OBS_SIZE],
                &mut masks[index * RESIDUAL_ACTION_SIZE..(index + 1) * RESIDUAL_ACTION_SIZE],
            );
        }
    }

    fn keep_actions(&self, actions: &mut [i32]) {
        for (output, env) in actions.iter_mut().zip(&self.envs) {
            *output = env.keep_action() as i32;
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_resident_residual_obs_size() -> usize {
    RESIDUAL_OBS_SIZE
}

#[no_mangle]
pub extern "C" fn tf_resident_residual_action_size() -> usize {
    RESIDUAL_ACTION_SIZE
}

#[no_mangle]
pub extern "C" fn tf_resident_residual_create(
    num_envs: usize,
    seed_base: u64,
    max_turns: u16,
) -> *mut ResidentResidualBatch {
    if num_envs == 0 || max_turns == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(ResidentResidualBatch::new(
        num_envs, seed_base, max_turns,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_resident_residual_destroy(handle: *mut ResidentResidualBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_resident_residual_observe(
    handle: *mut ResidentResidualBatch,
    obs: *mut u8,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || obs.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.observe(
        std::slice::from_raw_parts_mut(obs, batch.len() * RESIDUAL_OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, batch.len() * RESIDUAL_ACTION_SIZE),
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_resident_residual_keep_actions(
    handle: *mut ResidentResidualBatch,
    actions: *mut i32,
) -> i32 {
    if handle.is_null() || actions.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.keep_actions(std::slice::from_raw_parts_mut(actions, batch.len()));
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_resident_residual_step(
    handle: *mut ResidentResidualBatch,
    actions: *const i32,
    obs: *mut u8,
    masks: *mut u8,
    rewards: *mut f32,
    dones: *mut u8,
    turns: *mut u16,
    returns: *mut f32,
    scenario_seeds: *mut u64,
    map_seeds: *mut u64,
    seats: *mut u8,
    opponents: *mut u8,
    margins: *mut i32,
    wood_edges: *mut i32,
    workers: *mut u8,
    opponent_workers: *mut u8,
    overrides: *mut u16,
    residual_attempts: *mut u16,
    rejected_actions: *mut u16,
) -> i32 {
    if handle.is_null()
        || actions.is_null()
        || obs.is_null()
        || masks.is_null()
        || rewards.is_null()
        || dones.is_null()
        || turns.is_null()
        || returns.is_null()
        || scenario_seeds.is_null()
        || map_seeds.is_null()
        || seats.is_null()
        || opponents.is_null()
        || margins.is_null()
        || wood_edges.is_null()
        || workers.is_null()
        || opponent_workers.is_null()
        || overrides.is_null()
        || residual_attempts.is_null()
        || rejected_actions.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let n = batch.len();
    let actions = std::slice::from_raw_parts(actions, n);
    let rewards = std::slice::from_raw_parts_mut(rewards, n);
    let dones = std::slice::from_raw_parts_mut(dones, n);
    let turns = std::slice::from_raw_parts_mut(turns, n);
    let returns = std::slice::from_raw_parts_mut(returns, n);
    let scenario_seeds = std::slice::from_raw_parts_mut(scenario_seeds, n);
    let map_seeds = std::slice::from_raw_parts_mut(map_seeds, n);
    let seats = std::slice::from_raw_parts_mut(seats, n);
    let opponents = std::slice::from_raw_parts_mut(opponents, n);
    let margins = std::slice::from_raw_parts_mut(margins, n);
    let wood_edges = std::slice::from_raw_parts_mut(wood_edges, n);
    let workers = std::slice::from_raw_parts_mut(workers, n);
    let opponent_workers = std::slice::from_raw_parts_mut(opponent_workers, n);
    let overrides = std::slice::from_raw_parts_mut(overrides, n);
    let residual_attempts = std::slice::from_raw_parts_mut(residual_attempts, n);
    let rejected_actions = std::slice::from_raw_parts_mut(rejected_actions, n);

    for index in 0..n {
        let terminal = batch.envs[index].step(actions[index].max(0) as usize);
        rewards[index] = terminal.reward;
        dones[index] = terminal.done as u8;
        turns[index] = if terminal.done { terminal.turns } else { 0 };
        returns[index] = if terminal.done {
            terminal.episode_return
        } else {
            0.0
        };
        scenario_seeds[index] = if terminal.done {
            terminal.scenario_seed
        } else {
            0
        };
        map_seeds[index] = if terminal.done { terminal.map_seed } else { 0 };
        seats[index] = if terminal.done { terminal.seat } else { 0 };
        opponents[index] = if terminal.done { terminal.opponent } else { 0 };
        margins[index] = if terminal.done { terminal.margin } else { 0 };
        wood_edges[index] = if terminal.done { terminal.wood_edge } else { 0 };
        workers[index] = if terminal.done { terminal.workers } else { 0 };
        opponent_workers[index] = if terminal.done {
            terminal.opponent_workers
        } else {
            0
        };
        overrides[index] = if terminal.done { terminal.overrides } else { 0 };
        residual_attempts[index] = if terminal.done {
            terminal.residual_attempts
        } else {
            0
        };
        rejected_actions[index] = if terminal.done {
            terminal.rejected_actions
        } else {
            0
        };
        if terminal.done {
            batch.reset_slot(index);
        }
    }
    batch.observe(
        std::slice::from_raw_parts_mut(obs, n * RESIDUAL_OBS_SIZE),
        std::slice::from_raw_parts_mut(masks, n * RESIDUAL_ACTION_SIZE),
    );
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn direct_resident(scenario_seed: u64, max_turns: u16) -> (i32, i32, i32, usize, usize) {
        let map_seed = scenario_seed / 12;
        let seat = ((scenario_seed / 6) % 2) as usize;
        let mode = ResidualOpponentMode::from_index(scenario_seed as usize % 6);
        let mut game = generate_bronze(map_seed);
        let mut resident = SecureOrchardBot::new();
        let mut opponent = OpponentPolicy::new(mode);
        let mut stall_counter = 0;
        while game.turn <= i32::from(max_turns) {
            let ours = resident.commands(&resident_view(&game, seat));
            let theirs = opponent.commands(&game, 1 - seat);
            if seat == 0 {
                step(&mut game, &ours, &theirs);
            } else {
                step(&mut game, &theirs, &ours);
            }
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
        let workers = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count();
        (
            game.scores[seat] - game.scores[1 - seat],
            game.inventories[seat][WOOD] - game.inventories[1 - seat][WOOD],
            game.turn,
            workers,
            game.units.len() - workers,
        )
    }

    fn residual_keep(scenario_seed: u64, max_turns: u16) -> ResidentResidualTerminal {
        let mut env = ResidentResidualEnv::new(scenario_seed, max_turns);
        loop {
            let terminal = env.step(env.keep_action());
            if terminal.done {
                return terminal;
            }
        }
    }

    #[test]
    fn keep_is_always_legal_and_local_mask_is_bounded() {
        let env = ResidentResidualEnv::new(0, 300);
        let mut obs = vec![0u8; RESIDUAL_OBS_SIZE];
        let mut mask = vec![0u8; RESIDUAL_ACTION_SIZE];
        env.observe(&mut obs, &mut mask);
        assert_eq!(mask[env.keep_action()], 1);
        assert!((1..=7).contains(&mask.iter().filter(|&&legal| legal != 0).count()));
        assert_eq!(obs.len(), 137 * 11 * 22);
    }

    #[test]
    fn deterministic_keep_matches_direct_resident_panel() {
        for scenario_seed in 0..24 {
            let direct = direct_resident(scenario_seed, 300);
            let residual = residual_keep(scenario_seed, 300);
            assert_eq!(
                (
                    residual.margin,
                    residual.wood_edge,
                    i32::from(residual.turns)
                ),
                (direct.0, direct.1, direct.2),
                "scenario {scenario_seed} against {} seat {}",
                ResidualOpponentMode::from_index(scenario_seed as usize % 6).label(),
                (scenario_seed / 6) % 2,
            );
            assert_eq!(
                (
                    usize::from(residual.workers),
                    usize::from(residual.opponent_workers)
                ),
                (direct.3, direct.4)
            );
            assert_eq!(residual.overrides, 0);
            assert_eq!(residual.residual_attempts, 0);
            assert_eq!(residual.rejected_actions, 0);
            assert!((residual.episode_return - residual.margin as f32 / 100.0).abs() < 1e-5);
        }
    }
}
