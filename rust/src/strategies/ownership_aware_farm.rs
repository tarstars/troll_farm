//! Research-only private farm with race-conditioned opponent-loop denial.

use std::cell::RefCell;
use std::cmp::Ordering;
use std::collections::HashSet;

use super::gold_elite::{GoldEconomyConfig, GoldElite};
use super::Strategy;
use crate::game::engine::bfs_distances;
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
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct OwnershipTelemetry {
    pub opponent_crops_seen: usize,
    pub active_opponent_crops: usize,
    pub activation_turns: usize,
    pub first_activation_turn: Option<i32>,
    pub base_command_mismatches: usize,
}

#[derive(Clone, Copy)]
struct CycleValue {
    cell: Cell,
    own_wood: i32,
    denied_wood: i32,
    turns: i32,
}

impl CycleValue {
    fn margin_wood(self) -> i32 {
        self.own_wood + self.denied_wood
    }

    fn rate_cmp(self, other: Self) -> Ordering {
        (self.margin_wood() * other.turns)
            .cmp(&(other.margin_wood() * self.turns))
            .then_with(|| other.cell.cmp(&self.cell))
    }
}

pub struct OwnershipAwareFarm {
    inner: GoldElite,
    shadow: GoldElite,
    history: RefCell<History>,
    base_command_mismatches: RefCell<usize>,
}

impl OwnershipAwareFarm {
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

    pub fn telemetry(&self) -> OwnershipTelemetry {
        let history = self.history.borrow();
        OwnershipTelemetry {
            opponent_crops_seen: history.opponent_crops_seen,
            active_opponent_crops: history.opponent_crops.len(),
            activation_turns: history.activation_turns,
            first_activation_turn: history.first_activation_turn,
            base_command_mismatches: *self.base_command_mismatches.borrow(),
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
        let mut attempts = Vec::new();
        for command in commands {
            let mut fields = command.split_whitespace();
            if fields.next() != Some("PLANT") {
                continue;
            }
            let Some(id) = fields.next().and_then(|value| value.parse::<i32>().ok()) else {
                continue;
            };
            if let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
            {
                attempts.push(unit.pos());
            }
        }
        self.history
            .borrow_mut()
            .own_plant_attempts
            .extend(attempts);
    }

    fn ceil_div(value: i32, divisor: i32) -> i32 {
        (value + divisor.max(1) - 1) / divisor.max(1)
    }

    fn home_distance(game: &GameState, player: usize, cell: Cell) -> Option<i32> {
        let distances = bfs_distances(&game.walkable, &[cell]);
        let shack = game.shacks[player];
        [(0, 1), (1, 0), (0, -1), (-1, 0)]
            .into_iter()
            .map(|(dx, dy)| (shack.0 + dx, shack.1 + dy))
            .filter(|drop| game.walkable.contains(drop))
            .filter_map(|drop| distances.get(&drop).copied())
            .min()
    }

    fn cycle_value(
        game: &GameState,
        player: usize,
        unit: &Unit,
        plant: &Plant,
        denial: bool,
    ) -> Option<CycleValue> {
        let distance = bfs_distances(&game.walkable, &[unit.pos()]);
        let travel = Self::ceil_div(*distance.get(&plant.pos())?, unit.ms);
        let chop_turns = Self::ceil_div(plant.health, unit.chop);
        let home = Self::ceil_div(Self::home_distance(game, player, plant.pos())?, unit.ms);
        let turns = travel + chop_turns + home + 1;
        if turns > TOTAL_TURNS - game.turn + 1 {
            return None;
        }
        let own_wood = plant.size.min(unit.free()).max(0);
        if own_wood == 0 {
            return None;
        }
        let our_completion = travel + chop_turns;
        let denied_wood = if denial {
            game.units
                .iter()
                .filter(|enemy| {
                    enemy.player as usize != player && enemy.chop > 0 && enemy.free() > 0
                })
                .filter_map(|enemy| {
                    let enemy_distance = bfs_distances(&game.walkable, &[enemy.pos()]);
                    let travel = Self::ceil_div(*enemy_distance.get(&plant.pos())?, enemy.ms);
                    let completion = travel + Self::ceil_div(plant.health, enemy.chop);
                    Some((completion, enemy.id, enemy.free()))
                })
                .min_by_key(|(completion, id, _)| (*completion, *id))
                .filter(|(completion, _, _)| our_completion < *completion)
                .map_or(0, |(_, _, free)| plant.size.min(free).max(0))
        } else {
            0
        };
        Some(CycleValue {
            cell: plant.pos(),
            own_wood,
            denied_wood,
            turns,
        })
    }

    fn base_tree_target<'a>(game: &'a GameState, unit: &Unit, command: &str) -> Option<&'a Plant> {
        let fields: Vec<_> = command.split_whitespace().collect();
        let cell = match fields.as_slice() {
            ["CHOP", id] if id.parse::<i32>().ok() == Some(unit.id) => unit.pos(),
            ["MOVE", id, x, y]
                if id.parse::<i32>().ok() == Some(unit.id)
                    && x.parse::<i32>().is_ok()
                    && y.parse::<i32>().is_ok() =>
            {
                (x.parse().ok()?, y.parse().ok()?)
            }
            _ => return None,
        };
        game.plants.iter().find(|plant| plant.pos() == cell)
    }

    fn override_chopper(&self, game: &GameState, player: usize, commands: &mut [String]) -> bool {
        let opponent_crops = self.history.borrow().opponent_crops.clone();
        if opponent_crops.is_empty() {
            return false;
        }
        for command in commands {
            let Some(id) = command
                .split_whitespace()
                .nth(1)
                .and_then(|value| value.parse::<i32>().ok())
            else {
                continue;
            };
            let Some(unit) = game.units.iter().find(|unit| {
                unit.id == id
                    && unit.player as usize == player
                    && unit.chop >= 2
                    && unit.hp == 0
                    && unit.free() > 0
            }) else {
                continue;
            };
            let Some(base_plant) = Self::base_tree_target(game, unit, command) else {
                continue;
            };
            let Some(base) = Self::cycle_value(game, player, unit, base_plant, false) else {
                continue;
            };
            let best = game
                .plants
                .iter()
                .filter(|plant| plant.size >= 2 && opponent_crops.contains(&plant.pos()))
                .filter_map(|plant| Self::cycle_value(game, player, unit, plant, true))
                .max_by(|left, right| left.rate_cmp(*right));
            let Some(best) = best.filter(|candidate| candidate.rate_cmp(base).is_gt()) else {
                continue;
            };
            if best.cell == base.cell {
                continue;
            }
            *command = if unit.pos() == best.cell {
                format!("CHOP {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, best.cell.0, best.cell.1)
            };
            return true;
        }
        false
    }
}

impl Strategy for OwnershipAwareFarm {
    fn name(&self) -> &str {
        "ownership_aware_farm"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        self.reconcile_provenance(game);
        let mut commands = self.inner.decide(game, player);
        if commands != self.shadow.decide(game, player) {
            *self.base_command_mismatches.borrow_mut() += 1;
        }
        if self.override_chopper(game, player, &mut commands) {
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
    use crate::game::state::{from_ascii, Plant};

    fn banana(cell: Cell) -> Plant {
        Plant {
            plant_type: "BANANA".to_string(),
            x: cell.0,
            y: cell.1,
            size: 2,
            health: 4,
            fruits: 0,
            cooldown: 2,
        }
    }

    #[test]
    fn initial_natural_tree_is_not_opponent_crop() {
        let mut game = from_ascii(&["0...1", "....."]);
        game.plants.push(banana((2, 1)));
        let bot = OwnershipAwareFarm::new();
        bot.reconcile_provenance(&game);
        assert!(bot.history.borrow().opponent_crops.is_empty());
    }

    #[test]
    fn newly_appeared_tree_is_opponent_crop() {
        let mut game = from_ascii(&["0...1", "....."]);
        let bot = OwnershipAwareFarm::new();
        bot.reconcile_provenance(&game);
        game.turn = 2;
        game.plants.push(banana((2, 1)));
        bot.reconcile_provenance(&game);
        assert_eq!(bot.history.borrow().opponent_crops, HashSet::from([(2, 1)]));
    }

    #[test]
    fn rate_comparison_prefers_margin_per_cycle() {
        let fast = CycleValue {
            cell: (1, 1),
            own_wood: 2,
            denied_wood: 0,
            turns: 4,
        };
        let denial = CycleValue {
            cell: (2, 1),
            own_wood: 2,
            denied_wood: 2,
            turns: 6,
        };
        assert!(denial.rate_cmp(fast).is_gt());
    }
}
