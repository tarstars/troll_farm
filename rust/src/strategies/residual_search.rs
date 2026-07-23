//! Conservative residual forward search over a strong policy.
//!
//! GoldElite emits the control command. We enumerate a bounded set of one-unit
//! deviations, screen them with short exact-engine rollouts, then re-score a
//! few finalists against two continuation models. A deviation is used only if
//! it beats the control in every long scenario by `RS_MIN_GAIN`. Search is
//! phase-gated and failed options are not retried, bounding horizon mistakes.

use std::cell::RefCell;
use std::collections::{BTreeSet, HashMap};

use super::gold_elite::GoldElite;
use super::sched_bot::SchedBot;
use super::Strategy;
use crate::game::engine::{bfs_distances, has_stalled, step, training_cost, BANANA, IRON, WOOD};
use crate::game::state::{Cell, GameState, Unit};

const DEFAULT_SHORT_HORIZON: usize = 4;
const DEFAULT_LONG_HORIZON: usize = 16;
const DEFAULT_FINALISTS: usize = 4;
const DEFAULT_MAX_CANDIDATES: usize = 14;
// A one-point leaf gain is too fragile: small horizon artifacts survive both
// continuation models. Five was frozen before the final holdout.
const DEFAULT_MIN_GAIN: f64 = 5.0;
const DEFAULT_COMMIT_TURNS: usize = 8;
const DEFAULT_START_TURN: usize = 80;
const TOTAL_TURNS: i32 = 300;

#[derive(Clone, Copy)]
struct Commitment {
    target: Cell,
    expires: i32,
}

pub struct ResidualSearchBot {
    baseline: GoldElite,
    commitments: RefCell<HashMap<i32, Commitment>>,
    failed_targets: RefCell<BTreeSet<(i32, Cell)>>,
}

impl ResidualSearchBot {
    pub fn new() -> Self {
        Self {
            baseline: GoldElite::new(),
            commitments: RefCell::new(HashMap::new()),
            failed_targets: RefCell::new(BTreeSet::new()),
        }
    }
}

fn envi(name: &str, default: usize) -> usize {
    std::env::var(name)
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(default)
}

fn envf(name: &str, default: f64) -> f64 {
    std::env::var(name)
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(default)
}

fn enabled() -> bool {
    std::env::var("RS_ENABLE")
        .ok()
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(1)
        != 0
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn command_unit_id(command: &str) -> Option<i32> {
    let mut fields = command.split_whitespace();
    match fields.next()? {
        "MOVE" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK" => {
            fields.next()?.parse().ok()
        }
        _ => None,
    }
}

fn move_target(command: &str) -> Option<(i32, Cell)> {
    let fields: Vec<_> = command.split_whitespace().collect();
    if fields.len() != 4 || fields[0] != "MOVE" {
        return None;
    }
    Some((
        fields[1].parse().ok()?,
        (fields[2].parse().ok()?, fields[3].parse().ok()?),
    ))
}

fn changed_move_targets(candidate: &[String], baseline: &[String]) -> Vec<(i32, Cell)> {
    candidate
        .iter()
        .filter_map(|command| move_target(command))
        .filter(|(unit_id, target)| {
            baseline
                .iter()
                .filter_map(|command| move_target(command))
                .find_map(|(control_id, control_target)| {
                    (control_id == *unit_id).then_some(control_target)
                })
                != Some(*target)
        })
        .collect()
}

fn replace_unit_command(commands: &[String], unit_id: i32, replacement: &str) -> Vec<String> {
    let mut result = commands.to_vec();
    if let Some(index) = result
        .iter()
        .position(|command| command_unit_id(command) == Some(unit_id))
    {
        result[index] = replacement.to_owned();
    } else {
        result.push(replacement.to_owned());
    }
    result
}

fn carried_value(unit: &Unit) -> i32 {
    unit.carry[..WOOD].iter().sum::<i32>() + 4 * unit.carry[WOOD]
}

fn state_value(game: &GameState, player: usize) -> f64 {
    let opponent = 1 - player;
    let carry = |side: usize| {
        game.units
            .iter()
            .filter(|unit| unit.player as usize == side)
            .map(carried_value)
            .sum::<i32>()
    };
    (game.scores[player] - game.scores[opponent]) as f64
        + 0.75 * (carry(player) - carry(opponent)) as f64
}

#[derive(Clone, Copy)]
enum OpponentModel {
    Elite,
    Scheduler,
}

fn rollout_value(
    root: &GameState,
    player: usize,
    root_commands: &[String],
    baseline_commands: &[String],
    horizon: usize,
    model: OpponentModel,
    commit_turns: usize,
) -> f64 {
    let mut game = root.clone();
    let our_continuation = GoldElite::new();
    let elite_opponent = GoldElite::new();
    let scheduler_opponent = SchedBot::new();
    let mut commitments: Vec<_> = changed_move_targets(root_commands, baseline_commands)
        .into_iter()
        .map(|(unit_id, target)| (unit_id, target, commit_turns))
        .collect();
    let mut turns_until_end = 0;
    let remaining_turns = (TOTAL_TURNS - root.turn + 1).max(0) as usize;
    for depth in 0..horizon.min(remaining_turns) {
        let mut ours = if depth == 0 {
            root_commands.to_vec()
        } else {
            our_continuation.decide(&game, player)
        };
        // Evaluate the policy that will actually execute. An accepted target is
        // held across decisions, but a direct baseline action still completes
        // work immediately and clears the commitment.
        if depth > 0 {
            commitments.retain(|(unit_id, target, duration)| {
                if depth > *duration {
                    return false;
                }
                let Some(unit) = game
                    .units
                    .iter()
                    .find(|unit| unit.id == *unit_id && unit.player as usize == player)
                else {
                    return false;
                };
                let continuation = ours
                    .iter()
                    .find(|command| command_unit_id(command) == Some(*unit_id));
                let continuation_is_move =
                    continuation.is_some_and(|command| command.starts_with("MOVE "));
                let reached = unit.pos() == *target
                    || (*target == game.shacks[player] && manhattan(unit.pos(), *target) <= 1);
                if reached || !continuation_is_move {
                    return false;
                }
                let replacement = format!("MOVE {} {} {}", unit_id, target.0, target.1);
                ours = replace_unit_command(&ours, *unit_id, &replacement);
                true
            });
        }
        let opponent = match model {
            OpponentModel::Elite => elite_opponent.decide(&game, 1 - player),
            OpponentModel::Scheduler => scheduler_opponent.decide(&game, 1 - player),
        };
        if player == 0 {
            step(&mut game, &ours, &opponent);
        } else {
            step(&mut game, &opponent, &ours);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    state_value(&game, player)
}

fn push_unique(alternatives: &mut Vec<String>, seen: &mut BTreeSet<String>, command: String) {
    if seen.insert(command.clone()) {
        alternatives.push(command);
    }
}

fn unit_alternatives(
    game: &GameState,
    player: usize,
    unit: &Unit,
    baseline_command: &str,
) -> Vec<String> {
    let mut alternatives = Vec::new();
    let mut seen = BTreeSet::new();
    let id = unit.id;
    let shack = game.shacks[player];
    let opponent_shack = game.shacks[1 - player];
    let distances = bfs_distances(&game.walkable, &[unit.pos()]);
    // A residual layer may choose a different target, but it may not replace a
    // baseline action already completing work on the current cell. This prevents
    // the short horizon from interrupting CHOP/HARVEST/PLANT/PICK/DROP sequences.
    if !baseline_command.starts_with("MOVE ") {
        return alternatives;
    }
    let reachable = |cell: Cell| distances.get(&cell).copied();

    // Pure choppers search only within GoldElite's economic safety envelope.
    // In particular, the two most-mature local bananas are permanent seed
    // sources; the unconstrained prototype chopped them for a false leaf gain.
    if unit.chop > 0 && unit.hp == 0 {
        let liquidation = 300 - game.turn + 1 <= 34;
        let mut farm_bananas: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.plant_type == "BANANA" && manhattan(plant.pos(), shack) <= 3)
            .collect();
        farm_bananas.sort_by_key(|plant| {
            (
                -plant.size,
                -plant.fruits,
                manhattan(plant.pos(), shack),
                plant.pos(),
            )
        });
        let protected: BTreeSet<Cell> = if liquidation {
            BTreeSet::new()
        } else {
            farm_bananas
                .into_iter()
                .take(2)
                .map(|plant| plant.pos())
                .collect()
        };
        let safe_tree = |plant: &&crate::game::state::Plant| {
            let farm_banana = plant.plant_type == "BANANA" && manhattan(plant.pos(), shack) <= 3;
            let threshold = if liquidation {
                1
            } else if farm_banana {
                2
            } else {
                2
            };
            !protected.contains(&plant.pos())
                && plant.size >= threshold
                && (liquidation
                    || (manhattan(plant.pos(), shack) <= manhattan(plant.pos(), opponent_shack)
                        && manhattan(plant.pos(), shack) <= 10))
                && reachable(plant.pos()).is_some()
        };
        let mut by_completion: Vec<_> = game
            .plants
            .iter()
            .filter(safe_tree)
            .filter_map(|plant| {
                let distance = reachable(plant.pos())?;
                let travel = (distance + unit.ms - 1) / unit.ms.max(1);
                let chops = (plant.health + unit.chop - 1) / unit.chop.max(1);
                Some((travel + chops, plant.pos()))
            })
            .collect();
        by_completion.sort();
        for (_, target) in by_completion.into_iter().take(2) {
            push_unique(
                &mut alternatives,
                &mut seen,
                format!("MOVE {id} {} {}", target.0, target.1),
            );
        }
        if let Some(target) = game
            .plants
            .iter()
            .filter(safe_tree)
            .max_by_key(|plant| {
                (
                    plant.size,
                    -reachable(plant.pos()).unwrap_or(i32::MAX),
                    plant.pos(),
                )
            })
            .map(|plant| plant.pos())
        {
            push_unique(
                &mut alternatives,
                &mut seen,
                format!("MOVE {id} {} {}", target.0, target.1),
            );
        }
        if unit.total() > 0 {
            push_unique(
                &mut alternatives,
                &mut seen,
                format!("MOVE {id} {} {}", shack.0, shack.1),
            );
        }
        return alternatives;
    }

    // Funder/printer units keep their role. Search may choose another funding
    // fruit, seed source, planting cell, mine, or bank route, but cannot become
    // an opportunistic chopper.
    if unit.carry[BANANA] > 0 {
        let mut cells: Vec<_> = game
            .walkable
            .iter()
            .filter(|cell| manhattan(**cell, shack) <= 3)
            .filter(|cell| !game.plants.iter().any(|plant| plant.pos() == **cell))
            .filter_map(|cell| Some((reachable(*cell)?, *cell)))
            .collect();
        cells.sort();
        for (_, target) in cells.into_iter().take(3) {
            push_unique(
                &mut alternatives,
                &mut seen,
                format!("MOVE {id} {} {}", target.0, target.1),
            );
        }
        return alternatives;
    }
    if unit.total() > 0 && unit.free() == 0 {
        push_unique(
            &mut alternatives,
            &mut seen,
            format!("MOVE {id} {} {}", shack.0, shack.1),
        );
        return alternatives;
    }

    let my_units = game
        .units
        .iter()
        .filter(|other| other.player as usize == player)
        .count() as i32;
    let has_chopper = game
        .units
        .iter()
        .any(|other| other.player as usize == player && other.chop > 0 && other.hp == 0);
    if !has_chopper {
        let cost = training_cost(my_units, (2, 2, 0, 2));
        let needed = [
            game.inventories[player][0] < cost[0],
            game.inventories[player][1] < cost[1],
            game.inventories[player][2] < cost[2],
        ];
        let mut funding: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.fruits > 0)
            .filter(|plant| {
                let index = match plant.plant_type.as_str() {
                    "PLUM" => 0,
                    "LEMON" => 1,
                    "APPLE" => 2,
                    _ => 3,
                };
                index < 3 && needed[index]
            })
            .filter_map(|plant| Some((reachable(plant.pos())?, plant.pos())))
            .collect();
        funding.sort();
        for (_, target) in funding.into_iter().take(3) {
            push_unique(
                &mut alternatives,
                &mut seen,
                format!("MOVE {id} {} {}", target.0, target.1),
            );
        }
        if game.inventories[player][IRON] < cost[IRON] {
            if let Some(iron) = game
                .iron
                .iter()
                .min_by_key(|cell| (manhattan(unit.pos(), **cell), **cell))
            {
                push_unique(
                    &mut alternatives,
                    &mut seen,
                    format!("MOVE {id} {} {}", iron.0, iron.1),
                );
            }
        }
        return alternatives;
    }

    let mut seeds: Vec<_> = game
        .plants
        .iter()
        .filter(|plant| {
            plant.fruits > 0
                && (plant.plant_type == "BANANA"
                    || (plant.plant_type == "APPLE"
                        && game
                            .water
                            .iter()
                            .any(|water| manhattan(*water, plant.pos()) == 1)))
        })
        .filter_map(|plant| Some((reachable(plant.pos())?, plant.pos())))
        .collect();
    seeds.sort();
    for (_, target) in seeds.into_iter().take(3) {
        push_unique(
            &mut alternatives,
            &mut seen,
            format!("MOVE {id} {} {}", target.0, target.1),
        );
    }
    if game.inventories[player][BANANA] > 0 {
        push_unique(
            &mut alternatives,
            &mut seen,
            format!("MOVE {id} {} {}", shack.0, shack.1),
        );
    }
    alternatives
}

fn candidates(
    game: &GameState,
    player: usize,
    baseline: &[String],
    maximum: usize,
) -> Vec<Vec<String>> {
    let mut result = vec![baseline.to_vec()];
    let mut seen = BTreeSet::new();
    seen.insert(baseline.join(";"));
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    for unit in units {
        let baseline_command = baseline
            .iter()
            .find(|command| command_unit_id(command) == Some(unit.id))
            .map(String::as_str)
            .unwrap_or("WAIT");
        for alternative in unit_alternatives(game, player, unit, baseline_command) {
            let joint = replace_unit_command(baseline, unit.id, &alternative);
            if seen.insert(joint.join(";")) {
                result.push(joint);
                if result.len() >= maximum {
                    return result;
                }
            }
        }
    }
    result
}

/// Reuse the bounded, role-preserving movement library with another exact
/// baseline. The first row is always the unmodified baseline, and direct work
/// commands are never replaced.
pub fn movement_candidates(
    game: &GameState,
    player: usize,
    baseline: &[String],
    maximum: usize,
) -> Vec<Vec<String>> {
    candidates(game, player, baseline, maximum)
}

fn robust_choice(deltas: &[[f64; 2]], minimum_gain: f64) -> usize {
    let mut best = 0usize;
    // A candidate tied at exactly (minimum_gain, minimum_gain) does not justify
    // an override; one model or the mean must exceed that conservative floor.
    let mut best_key = (minimum_gain, minimum_gain);
    for (index, delta) in deltas.iter().enumerate().skip(1) {
        let robust = delta[0].min(delta[1]);
        let mean = 0.5 * (delta[0] + delta[1]);
        if robust >= minimum_gain && (robust, mean) > best_key {
            best = index;
            best_key = (robust, mean);
        }
    }
    best
}

impl Strategy for ResidualSearchBot {
    fn name(&self) -> &str {
        "residual"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let baseline = self.baseline.decide(game, player);
        if game.turn == 1 {
            self.commitments.borrow_mut().clear();
            self.failed_targets.borrow_mut().clear();
        }
        if !enabled() {
            return baseline;
        }
        // The finite-horizon leaf value is suitable for tactical corrections,
        // not for the fragile training/farm bootstrap. Let GoldElite own that
        // strategic phase completely.
        let start_turn = envi("RS_START_TURN", DEFAULT_START_TURN) as i32;
        let economy_ready = game
            .units
            .iter()
            .any(|unit| unit.player as usize == player && unit.chop >= 2);
        if game.turn < start_turn || !economy_ready {
            return baseline;
        }
        // Honor an accepted target long enough to reach it. A direct baseline
        // action (CHOP/HARVEST/etc.) always wins and clears the commitment, so
        // search cannot interrupt work once the unit arrives on a useful cell.
        let mut committed = baseline.clone();
        let mut has_active_commitment = false;
        let mut ended_commitment = false;
        let mut newly_failed = Vec::new();
        self.commitments.borrow_mut().retain(|unit_id, commitment| {
            let Some(unit) = game.units.iter().find(|unit| unit.id == *unit_id) else {
                return false;
            };
            let baseline_command = baseline
                .iter()
                .find(|command| command_unit_id(command) == Some(*unit_id));
            let baseline_is_move =
                baseline_command.is_some_and(|command| command.starts_with("MOVE "));
            let reached = unit.pos() == commitment.target
                || (commitment.target == game.shacks[player]
                    && manhattan(unit.pos(), commitment.target) <= 1);
            if !baseline_is_move {
                ended_commitment = true;
                return false;
            }
            if game.turn > commitment.expires || reached {
                // The option did not produce the direct baseline action it was
                // meant to unlock. Never pay for the same false positive twice.
                newly_failed.push((*unit_id, commitment.target));
                ended_commitment = true;
                return false;
            }
            let replacement = format!(
                "MOVE {} {} {}",
                unit_id, commitment.target.0, commitment.target.1
            );
            committed = replace_unit_command(&committed, *unit_id, &replacement);
            has_active_commitment = true;
            true
        });
        self.failed_targets.borrow_mut().extend(newly_failed);
        if has_active_commitment {
            return committed;
        }
        if ended_commitment {
            return baseline;
        }
        let short_horizon = envi("RS_SHORT_H", DEFAULT_SHORT_HORIZON).max(1);
        let long_horizon = envi("RS_LONG_H", DEFAULT_LONG_HORIZON).max(short_horizon);
        let finalists = envi("RS_FINALISTS", DEFAULT_FINALISTS).max(1);
        let maximum = envi("RS_MAX_CANDIDATES", DEFAULT_MAX_CANDIDATES).max(1);
        let minimum_gain = envf("RS_MIN_GAIN", DEFAULT_MIN_GAIN);
        let commit_turns = envi("RS_COMMIT", DEFAULT_COMMIT_TURNS);
        let mut all = candidates(game, player, &baseline, maximum);
        let failed_targets = self.failed_targets.borrow();
        all.retain(|commands| {
            commands == &baseline
                || changed_move_targets(commands, &baseline)
                    .iter()
                    .all(|target| !failed_targets.contains(target))
        });
        drop(failed_targets);
        if all.len() == 1 {
            return baseline;
        }

        let mut screened: Vec<(f64, usize)> = all
            .iter()
            .enumerate()
            .map(|(index, commands)| {
                (
                    rollout_value(
                        game,
                        player,
                        commands,
                        &baseline,
                        short_horizon,
                        OpponentModel::Elite,
                        commit_turns,
                    ),
                    index,
                )
            })
            .collect();
        screened.sort_by(|left, right| {
            right
                .0
                .total_cmp(&left.0)
                .then_with(|| left.1.cmp(&right.1))
        });
        let mut finalist_indices: Vec<usize> = screened
            .iter()
            .take(finalists)
            .map(|(_, index)| *index)
            .collect();
        if !finalist_indices.contains(&0) {
            finalist_indices.push(0);
        }
        finalist_indices.sort_unstable();
        finalist_indices.dedup();

        let baseline_values = [
            rollout_value(
                game,
                player,
                &baseline,
                &baseline,
                long_horizon,
                OpponentModel::Elite,
                commit_turns,
            ),
            rollout_value(
                game,
                player,
                &baseline,
                &baseline,
                long_horizon,
                OpponentModel::Scheduler,
                commit_turns,
            ),
        ];
        let mut deltas = vec![[f64::NEG_INFINITY; 2]; finalist_indices.len()];
        for (slot, &index) in finalist_indices.iter().enumerate() {
            if index == 0 {
                deltas[slot] = [0.0, 0.0];
                continue;
            }
            deltas[slot][0] = rollout_value(
                game,
                player,
                &all[index],
                &baseline,
                long_horizon,
                OpponentModel::Elite,
                commit_turns,
            ) - baseline_values[0];
            // The final rule is conjunctive. Once Elite rejects a candidate,
            // its Scheduler value cannot make it eligible, so avoid that exact
            // rollout without changing the selected command.
            if deltas[slot][0] >= minimum_gain {
                deltas[slot][1] = rollout_value(
                    game,
                    player,
                    &all[index],
                    &baseline,
                    long_horizon,
                    OpponentModel::Scheduler,
                    commit_turns,
                ) - baseline_values[1];
            }
        }
        let chosen_slot = robust_choice(&deltas, minimum_gain);
        let chosen_index = finalist_indices[chosen_slot];
        if chosen_index != 0 && std::env::var("RS_TRACE").is_ok() {
            eprintln!(
                "@RS turn={} player={} models={:+.2}/{:+.2} baseline={:?} chosen={:?}",
                game.turn,
                player,
                deltas[chosen_slot][0],
                deltas[chosen_slot][1],
                baseline,
                all[chosen_index],
            );
        }
        if chosen_index != 0 {
            for (unit_id, target) in changed_move_targets(&all[chosen_index], &baseline) {
                self.commitments.borrow_mut().insert(
                    unit_id,
                    Commitment {
                        target,
                        expires: game.turn + commit_turns as i32,
                    },
                );
            }
        }
        all[chosen_index].clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::mapgen::generate_bronze;

    #[test]
    fn command_replacement_preserves_training_and_other_units() {
        let commands = vec![
            "MOVE 0 1 2".to_owned(),
            "CHOP 2".to_owned(),
            "TRAIN 2 2 0 2".to_owned(),
        ];

        let result = replace_unit_command(&commands, 0, "HARVEST 0");

        assert_eq!(result[0], "HARVEST 0");
        assert_eq!(result[1], "CHOP 2");
        assert_eq!(result[2], "TRAIN 2 2 0 2");
    }

    #[test]
    fn move_target_ignores_non_move_commands() {
        assert_eq!(move_target("MOVE 7 12 3"), Some((7, (12, 3))));
        assert_eq!(move_target("CHOP 7"), None);
    }

    #[test]
    fn candidates_keep_exact_baseline_first_and_are_unique() {
        let game = generate_bronze(7);
        let baseline = GoldElite::new().decide(&game, 0);

        let result = candidates(&game, 0, &baseline, 14);
        let unique: BTreeSet<_> = result.iter().map(|row| row.join(";")).collect();

        assert_eq!(result[0], baseline);
        assert_eq!(result.len(), unique.len());
        assert!(result.len() <= 14);
    }

    #[test]
    fn robust_choice_rejects_a_candidate_that_loses_one_model() {
        let deltas = [[0.0, 0.0], [9.0, -0.1], [2.0, 3.0]];

        assert_eq!(robust_choice(&deltas, 1.0), 2);
        assert_eq!(robust_choice(&deltas, 4.0), 0);
    }
}
