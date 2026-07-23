//! Research-only farm that interrupts attributed rival crops before first fruit.

use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

use super::gold_elite::{GoldEconomyConfig, GoldElite};
use super::Strategy;
use crate::game::engine::{
    bfs_distances, plant_cooldown, tree_health_params, water_boost, MAX_FRUITS, MAX_SIZE,
};
use crate::game::state::{Cell, GameState, Plant, Unit};

const TOTAL_TURNS: i32 = 300;

#[derive(Default)]
struct History {
    initialized: bool,
    previous_plants: HashSet<Cell>,
    own_plant_attempts: HashSet<Cell>,
    opponent_crops: HashSet<Cell>,
    opponent_crops_seen: usize,
    activation_turns: usize,
    first_activation_turn: Option<i32>,
    commitments: HashMap<i32, Cell>,
    tracked_targets: HashSet<Cell>,
    selected_targets: usize,
    targets_disappeared_before_fruit: usize,
    targets_fruited_after_selection: usize,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct PreFruitTelemetry {
    pub opponent_crops_seen: usize,
    pub active_opponent_crops: usize,
    pub activation_turns: usize,
    pub first_activation_turn: Option<i32>,
    pub base_command_mismatches: usize,
    pub selected_targets: usize,
    pub targets_disappeared_before_fruit: usize,
    pub targets_fruited_after_selection: usize,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct TargetPlan {
    pub(crate) cell: Cell,
    pub(crate) first_fruit_turn: i32,
    pub(crate) kill_turn: i32,
}

pub struct PreFruitInterruption {
    inner: GoldElite,
    shadow: GoldElite,
    history: RefCell<History>,
    base_command_mismatches: RefCell<usize>,
}

impl PreFruitInterruption {
    fn farm() -> GoldElite {
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

    pub fn new() -> Self {
        Self {
            inner: Self::farm(),
            shadow: Self::farm(),
            history: RefCell::new(History::default()),
            base_command_mismatches: RefCell::new(0),
        }
    }

    pub fn telemetry(&self) -> PreFruitTelemetry {
        let history = self.history.borrow();
        PreFruitTelemetry {
            opponent_crops_seen: history.opponent_crops_seen,
            active_opponent_crops: history.opponent_crops.len(),
            activation_turns: history.activation_turns,
            first_activation_turn: history.first_activation_turn,
            base_command_mismatches: *self.base_command_mismatches.borrow(),
            selected_targets: history.selected_targets,
            targets_disappeared_before_fruit: history.targets_disappeared_before_fruit,
            targets_fruited_after_selection: history.targets_fruited_after_selection,
        }
    }

    fn reconcile_provenance(&self, game: &GameState) {
        let current: HashSet<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .map(Plant::pos)
            .collect();
        let mut history = self.history.borrow_mut();
        if game.turn == 1 {
            *history = History::default();
            *self.base_command_mismatches.borrow_mut() = 0;
        }

        let tracked: Vec<_> = history.tracked_targets.iter().copied().collect();
        for cell in tracked {
            match game.plants.iter().find(|plant| plant.pos() == cell) {
                None => {
                    history.targets_disappeared_before_fruit += 1;
                    history.tracked_targets.remove(&cell);
                    history.commitments.retain(|_, target| *target != cell);
                }
                Some(plant) if plant.fruits > 0 => {
                    history.targets_fruited_after_selection += 1;
                    history.tracked_targets.remove(&cell);
                    history.commitments.retain(|_, target| *target != cell);
                }
                Some(_) => {}
            }
        }

        if history.initialized {
            let appeared: Vec<_> = current
                .difference(&history.previous_plants)
                .copied()
                .collect();
            for cell in appeared {
                if !history.own_plant_attempts.contains(&cell)
                    && history.opponent_crops.insert(cell)
                {
                    history.opponent_crops_seen += 1;
                }
            }
            history.opponent_crops.retain(|cell| current.contains(cell));
        } else {
            history.initialized = true;
        }
        history.previous_plants = current;
        history.own_plant_attempts.clear();
    }

    fn remember_plant_attempts(&self, game: &GameState, player: usize, commands: &[String]) {
        let attempts = commands.iter().filter_map(|command| {
            let mut fields = command.split_whitespace();
            if fields.next()? != "PLANT" {
                return None;
            }
            let id = fields.next()?.parse::<i32>().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(Unit::pos)
        });
        self.history
            .borrow_mut()
            .own_plant_attempts
            .extend(attempts);
    }

    fn ceil_div(value: i32, divisor: i32) -> i32 {
        (value + divisor.max(1) - 1) / divisor.max(1)
    }

    fn effective_cooldown(game: &GameState, plant: &Plant) -> i32 {
        let near_water = game
            .water
            .iter()
            .any(|water| (water.0 - plant.x).abs() + (water.1 - plant.y).abs() == 1);
        plant_cooldown(&plant.plant_type)
            - if near_water {
                water_boost(&plant.plant_type)
            } else {
                0
            }
    }

    fn tick_crop(game: &GameState, plant: &mut Plant) {
        if plant.cooldown > 0 {
            plant.cooldown -= 1;
        }
        if plant.cooldown != 0 || plant.health <= 0 {
            return;
        }
        if plant.size < MAX_SIZE {
            plant.size += 1;
            plant.health += tree_health_params(&plant.plant_type).1;
            plant.cooldown = Self::effective_cooldown(game, plant);
        } else if plant.fruits < MAX_FRUITS {
            plant.fruits += 1;
            plant.cooldown = Self::effective_cooldown(game, plant);
        }
    }

    fn first_fruit_turn(game: &GameState, plant: &Plant) -> Option<i32> {
        if plant.fruits > 0 || plant.health <= 0 {
            return None;
        }
        let mut simulated = plant.clone();
        let turns_left = TOTAL_TURNS - game.turn + 1;
        for turn in 1..=turns_left {
            Self::tick_crop(game, &mut simulated);
            if simulated.fruits > 0 {
                return Some(turn);
            }
        }
        None
    }

    fn kill_before_first_fruit(game: &GameState, unit: &Unit, plant: &Plant) -> Option<TargetPlan> {
        if plant.fruits > 0 || plant.health <= 0 || unit.chop <= 0 {
            return None;
        }
        let first_fruit_turn = Self::first_fruit_turn(game, plant)?;
        let distances = bfs_distances(&game.walkable, &[unit.pos()]);
        let travel_turns = Self::ceil_div(*distances.get(&plant.pos())?, unit.ms);
        let mut simulated = plant.clone();
        for turn in 1..=first_fruit_turn {
            if turn > travel_turns {
                simulated.health = (simulated.health - unit.chop).max(0);
                if simulated.health == 0 {
                    return Some(TargetPlan {
                        cell: plant.pos(),
                        first_fruit_turn,
                        kill_turn: turn,
                    });
                }
            }
            Self::tick_crop(game, &mut simulated);
            if simulated.fruits > 0 {
                return None;
            }
        }
        None
    }

    fn opponent_can_arrive_by_first_fruit(
        game: &GameState,
        player: usize,
        plant: &Plant,
        first_fruit_turn: i32,
    ) -> bool {
        game.units
            .iter()
            .filter(|unit| unit.player as usize != player && unit.hp > 0)
            .any(|unit| {
                let distances = bfs_distances(&game.walkable, &[unit.pos()]);
                distances
                    .get(&plant.pos())
                    .is_some_and(|distance| Self::ceil_div(*distance, unit.ms) <= first_fruit_turn)
            })
    }

    pub(crate) fn target_plan(
        game: &GameState,
        player: usize,
        unit: &Unit,
        cell: Cell,
        opponent_crops: &HashSet<Cell>,
    ) -> Option<TargetPlan> {
        if !opponent_crops.contains(&cell) {
            return None;
        }
        let plant = game
            .plants
            .iter()
            .find(|plant| plant.pos() == cell && plant.fruits == 0)?;
        let plan = Self::kill_before_first_fruit(game, unit, plant)?;
        Self::opponent_can_arrive_by_first_fruit(game, player, plant, plan.first_fruit_turn)
            .then_some(plan)
    }

    pub(crate) fn command_unit_id(command: &str) -> Option<i32> {
        let mut fields = command.split_whitespace();
        match fields.next()? {
            "MOVE" | "HARVEST" | "DROP" | "CHOP" | "MINE" | "PLANT" | "PICK" => {
                fields.next()?.parse().ok()
            }
            _ => None,
        }
    }

    fn override_choppers(&self, game: &GameState, player: usize, commands: &mut [String]) -> bool {
        let (opponent_crops, commitments) = {
            let history = self.history.borrow();
            (history.opponent_crops.clone(), history.commitments.clone())
        };
        if opponent_crops.is_empty() {
            return false;
        }

        let mut activated = false;
        let mut reserved = HashSet::new();
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| {
                unit.player as usize == player
                    && unit.chop >= 2
                    && unit.hp == 0
                    && unit.total() == 0
            })
            .collect();
        units.sort_by_key(|unit| unit.id);

        for unit in units {
            let committed = commitments
                .get(&unit.id)
                .and_then(|cell| Self::target_plan(game, player, unit, *cell, &opponent_crops));
            let plan = committed.or_else(|| {
                opponent_crops
                    .iter()
                    .filter(|cell| !reserved.contains(*cell))
                    .filter_map(|cell| {
                        Self::target_plan(game, player, unit, *cell, &opponent_crops)
                    })
                    .min_by_key(|plan| (plan.first_fruit_turn, plan.kill_turn, plan.cell))
            });
            let Some(plan) = plan else {
                self.history.borrow_mut().commitments.remove(&unit.id);
                continue;
            };
            reserved.insert(plan.cell);
            let replacement = if unit.pos() == plan.cell {
                format!("CHOP {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, plan.cell.0, plan.cell.1)
            };
            let Some(index) = commands
                .iter()
                .position(|command| Self::command_unit_id(command) == Some(unit.id))
            else {
                continue;
            };
            if commands[index] == replacement {
                continue;
            }
            commands[index] = replacement;
            let mut history = self.history.borrow_mut();
            history.commitments.insert(unit.id, plan.cell);
            if history.tracked_targets.insert(plan.cell) {
                history.selected_targets += 1;
            }
            activated = true;
        }
        activated
    }
}

impl Strategy for PreFruitInterruption {
    fn name(&self) -> &str {
        "prefruit_interruption"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        self.reconcile_provenance(game);
        let mut commands = self.inner.decide(game, player);
        if commands != self.shadow.decide(game, player) {
            *self.base_command_mismatches.borrow_mut() += 1;
        }
        if self.override_choppers(game, player, &mut commands) {
            let mut history = self.history.borrow_mut();
            history.activation_turns += 1;
            history.first_activation_turn.get_or_insert(game.turn);
        }
        self.remember_plant_attempts(game, player, &commands);
        commands
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::state::from_ascii;

    fn banana(cell: Cell, size: i32, health: i32, fruits: i32, cooldown: i32) -> Plant {
        Plant {
            plant_type: "BANANA".to_string(),
            x: cell.0,
            y: cell.1,
            size,
            health,
            fruits,
            cooldown,
        }
    }

    fn pure_chopper(game: &mut GameState, player: usize) {
        let unit = game
            .units
            .iter_mut()
            .find(|unit| unit.player as usize == player)
            .expect("player unit");
        unit.ms = 2;
        unit.cc = 2;
        unit.hp = 0;
        unit.chop = 2;
    }

    #[test]
    fn newly_appeared_tree_is_attributed_to_opponent() {
        let mut game = from_ascii(&["0...1", "....."]);
        let bot = PreFruitInterruption::new();
        bot.reconcile_provenance(&game);
        game.turn = 2;
        game.plants.push(banana((2, 1), 1, 3, 0, 4));
        bot.reconcile_provenance(&game);
        assert_eq!(bot.history.borrow().opponent_crops, HashSet::from([(2, 1)]));
    }

    #[test]
    fn same_turn_kill_beats_first_fruit_tick() {
        let mut game = from_ascii(&["0...1", "....."]);
        pure_chopper(&mut game, 0);
        let unit = &game.units[0];
        let crop = banana(unit.pos(), 4, 2, 0, 1);
        let plan = PreFruitInterruption::kill_before_first_fruit(&game, unit, &crop)
            .expect("kill precedes tick");
        assert_eq!(plan.first_fruit_turn, 1);
        assert_eq!(plan.kill_turn, 1);
    }

    #[test]
    fn insufficient_health_damage_loses_to_first_fruit_tick() {
        let mut game = from_ascii(&["0...1", "....."]);
        pure_chopper(&mut game, 0);
        let unit = &game.units[0];
        let crop = banana(unit.pos(), 4, 3, 0, 1);
        assert!(PreFruitInterruption::kill_before_first_fruit(&game, unit, &crop).is_none());
    }

    #[test]
    fn travel_consumes_action_turns_before_chopping() {
        let mut game = from_ascii(&["0....1", "......"]);
        pure_chopper(&mut game, 0);
        game.units[0].ms = 1;
        let crop = banana((2, 0), 4, 2, 0, 2);
        assert!(
            PreFruitInterruption::kill_before_first_fruit(&game, &game.units[0], &crop).is_none()
        );
    }

    #[test]
    fn feasible_ready_crop_replaces_only_chopper_command() {
        let mut game = from_ascii(&["0....1", "......"]);
        pure_chopper(&mut game, 0);
        game.units[1].x = 2;
        game.units[1].y = 0;
        let bot = PreFruitInterruption::new();
        bot.reconcile_provenance(&game);
        game.turn = 2;
        game.plants.push(banana((1, 0), 4, 2, 0, 2));
        bot.reconcile_provenance(&game);
        let mut commands = vec!["MOVE 0 3 1".to_string(), "TRAIN 1 1 1 1".to_string()];
        assert!(bot.override_choppers(&game, 0, &mut commands));
        assert_eq!(commands, ["MOVE 0 1 0", "TRAIN 1 1 1 1"]);
        assert_eq!(bot.history.borrow().selected_targets, 1);
    }

    #[test]
    fn crop_that_already_fruited_is_never_selected() {
        let mut game = from_ascii(&["0....1", "......"]);
        pure_chopper(&mut game, 0);
        game.plants.push(banana((1, 0), 4, 2, 1, 2));
        let opponent_crops = HashSet::from([(1, 0)]);
        assert!(PreFruitInterruption::target_plan(
            &game,
            0,
            &game.units[0],
            (1, 0),
            &opponent_crops,
        )
        .is_none());
    }
}
