//! Research-only renewable farm with physically separated denial capacity.

use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

use super::gold_elite::GoldElite;
use super::prefruit_interruption::{PreFruitInterruption, TargetPlan};
use super::Strategy;
use crate::game::state::{Cell, GameState, Plant, Unit};

const DENIAL_START_TURN: i32 = 100;

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
    capacity_ready_turns: usize,
    capacity_separation_violations: usize,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct CapacitySeparatedTelemetry {
    pub opponent_crops_seen: usize,
    pub active_opponent_crops: usize,
    pub activation_turns: usize,
    pub first_activation_turn: Option<i32>,
    pub base_command_mismatches: usize,
    pub selected_targets: usize,
    pub targets_disappeared_before_fruit: usize,
    pub targets_fruited_after_selection: usize,
    pub capacity_ready_turns: usize,
    pub capacity_separation_violations: usize,
}

pub struct CapacitySeparatedDenial {
    inner: GoldElite,
    shadow: GoldElite,
    history: RefCell<History>,
    base_command_mismatches: RefCell<usize>,
}

impl CapacitySeparatedDenial {
    pub fn new() -> Self {
        Self {
            inner: GoldElite::adaptive(),
            shadow: GoldElite::adaptive(),
            history: RefCell::new(History::default()),
            base_command_mismatches: RefCell::new(0),
        }
    }

    pub fn telemetry(&self) -> CapacitySeparatedTelemetry {
        let history = self.history.borrow();
        CapacitySeparatedTelemetry {
            opponent_crops_seen: history.opponent_crops_seen,
            active_opponent_crops: history.opponent_crops.len(),
            activation_turns: history.activation_turns,
            first_activation_turn: history.first_activation_turn,
            base_command_mismatches: *self.base_command_mismatches.borrow(),
            selected_targets: history.selected_targets,
            targets_disappeared_before_fruit: history.targets_disappeared_before_fruit,
            targets_fruited_after_selection: history.targets_fruited_after_selection,
            capacity_ready_turns: history.capacity_ready_turns,
            capacity_separation_violations: history.capacity_separation_violations,
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

    fn pure_choppers<'a>(game: &'a GameState, player: usize) -> Vec<&'a Unit> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player && unit.chop >= 2 && unit.hp == 0)
            .collect();
        units.sort_by_key(|unit| unit.id);
        units
    }

    fn capacity_ready(game: &GameState, player: usize) -> bool {
        game.turn >= DENIAL_START_TURN && Self::pure_choppers(game, player).len() >= 2
    }

    fn target_for(
        game: &GameState,
        player: usize,
        unit: &Unit,
        opponent_crops: &HashSet<Cell>,
        committed: Option<Cell>,
    ) -> Option<TargetPlan> {
        committed
            .and_then(|cell| {
                PreFruitInterruption::target_plan(game, player, unit, cell, opponent_crops)
            })
            .or_else(|| {
                opponent_crops
                    .iter()
                    .filter_map(|cell| {
                        PreFruitInterruption::target_plan(game, player, unit, *cell, opponent_crops)
                    })
                    .min_by_key(|plan| (plan.first_fruit_turn, plan.kill_turn, plan.cell))
            })
    }

    fn override_denial_chopper(
        &self,
        game: &GameState,
        player: usize,
        commands: &mut [String],
    ) -> bool {
        if game.turn < DENIAL_START_TURN {
            return false;
        }
        let pure = Self::pure_choppers(game, player);
        if pure.len() < 2 {
            return false;
        }
        let protected_id = pure.first().expect("two pure choppers").id;
        let denial = *pure.last().expect("two pure choppers");
        if denial.id == protected_id {
            self.history.borrow_mut().capacity_separation_violations += 1;
            return false;
        }
        if denial.total() != 0 {
            return false;
        }

        let (opponent_crops, committed) = {
            let history = self.history.borrow();
            (
                history.opponent_crops.clone(),
                history.commitments.get(&denial.id).copied(),
            )
        };
        let Some(plan) = Self::target_for(game, player, denial, &opponent_crops, committed) else {
            self.history.borrow_mut().commitments.remove(&denial.id);
            return false;
        };
        let replacement = if denial.pos() == plan.cell {
            format!("CHOP {}", denial.id)
        } else {
            format!("MOVE {} {} {}", denial.id, plan.cell.0, plan.cell.1)
        };
        let Some(index) = commands
            .iter()
            .position(|command| PreFruitInterruption::command_unit_id(command) == Some(denial.id))
        else {
            return false;
        };
        if commands[index] == replacement {
            return false;
        }
        if PreFruitInterruption::command_unit_id(&commands[index]) == Some(protected_id) {
            self.history.borrow_mut().capacity_separation_violations += 1;
            return false;
        }
        commands[index] = replacement;
        let mut history = self.history.borrow_mut();
        history.commitments.insert(denial.id, plan.cell);
        if history.tracked_targets.insert(plan.cell) {
            history.selected_targets += 1;
        }
        true
    }
}

impl Strategy for CapacitySeparatedDenial {
    fn name(&self) -> &str {
        "capacity_separated_denial"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        self.reconcile_provenance(game);
        let mut commands = self.inner.decide(game, player);
        if commands != self.shadow.decide(game, player) {
            *self.base_command_mismatches.borrow_mut() += 1;
        }
        if Self::capacity_ready(game, player) {
            self.history.borrow_mut().capacity_ready_turns += 1;
        }
        if self.override_denial_chopper(game, player, &mut commands) {
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
    use crate::game::state::{from_ascii, Unit};

    fn banana(cell: Cell) -> Plant {
        Plant {
            plant_type: "BANANA".to_string(),
            x: cell.0,
            y: cell.1,
            size: 4,
            health: 2,
            fruits: 0,
            cooldown: 2,
        }
    }

    fn make_pure(unit: &mut Unit) {
        unit.ms = 2;
        unit.cc = 2;
        unit.hp = 0;
        unit.chop = 2;
    }

    fn two_chopper_game() -> GameState {
        let mut game = from_ascii(&["0....1", "......"]);
        make_pure(&mut game.units[0]);
        game.units[1].x = 2;
        game.units[1].y = 0;
        game.units.push(Unit {
            id: 2,
            player: 0,
            x: 0,
            y: 0,
            ms: 2,
            cc: 2,
            hp: 0,
            chop: 2,
            carry: [0; 6],
        });
        game
    }

    fn attributed_crop(bot: &CapacitySeparatedDenial, game: &mut GameState, turn: i32) {
        bot.reconcile_provenance(game);
        game.turn = turn;
        game.plants.push(banana((1, 0)));
        bot.reconcile_provenance(game);
    }

    #[test]
    fn before_build_boundary_is_exactly_inactive() {
        let mut game = two_chopper_game();
        let bot = CapacitySeparatedDenial::new();
        attributed_crop(&bot, &mut game, 99);
        let mut commands = vec!["MOVE 0 4 1".to_string(), "MOVE 2 3 1".to_string()];
        let original = commands.clone();
        assert!(!bot.override_denial_chopper(&game, 0, &mut commands));
        assert_eq!(commands, original);
    }

    #[test]
    fn one_chopper_is_never_diverted() {
        let mut game = two_chopper_game();
        game.units.retain(|unit| unit.id != 2);
        let bot = CapacitySeparatedDenial::new();
        attributed_crop(&bot, &mut game, 100);
        let mut commands = vec!["MOVE 0 4 1".to_string()];
        assert!(!bot.override_denial_chopper(&game, 0, &mut commands));
        assert_eq!(commands, ["MOVE 0 4 1"]);
    }

    #[test]
    fn second_chopper_activates_while_first_command_is_preserved() {
        let mut game = two_chopper_game();
        let bot = CapacitySeparatedDenial::new();
        attributed_crop(&bot, &mut game, 100);
        let mut commands = vec![
            "MOVE 0 4 1".to_string(),
            "MOVE 2 3 1".to_string(),
            "TRAIN 1 1 1 1".to_string(),
        ];
        assert!(bot.override_denial_chopper(&game, 0, &mut commands));
        assert_eq!(commands, ["MOVE 0 4 1", "MOVE 2 1 0", "TRAIN 1 1 1 1"]);
        assert_eq!(bot.history.borrow().capacity_separation_violations, 0);
    }

    #[test]
    fn carrying_second_chopper_keeps_base_command() {
        let mut game = two_chopper_game();
        game.units
            .iter_mut()
            .find(|unit| unit.id == 2)
            .unwrap()
            .carry[5] = 1;
        let bot = CapacitySeparatedDenial::new();
        attributed_crop(&bot, &mut game, 100);
        let mut commands = vec!["MOVE 0 4 1".to_string(), "DROP 2".to_string()];
        let original = commands.clone();
        assert!(!bot.override_denial_chopper(&game, 0, &mut commands));
        assert_eq!(commands, original);
    }
}
