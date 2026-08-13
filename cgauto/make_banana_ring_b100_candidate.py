#!/usr/bin/env python3
"""Build the owner-corrected bounded banana-ring + b100/e6 candidate.

The byte-sacred resident source is only read.  Every source transformation is
fail-closed and the generated research/compact artifacts carry hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


SOURCE_REL = Path("rust/src/bin/yamo_orchard_live.rs")
CONTROL_REL = Path("cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs")
SOURCE_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
CONTROL_SHA256 = "6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19"


class BuildError(RuntimeError):
    pass


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify(path: Path, expected: str, label: str) -> bytes:
    if not path.is_file():
        raise BuildError(f"{label} missing: {path}")
    payload = path.read_bytes()
    actual = digest(payload)
    if actual != expected:
        raise BuildError(f"{label} hash drift: expected {expected}, got {actual}")
    return payload


def replace_once(source: str, before: str, after: str, label: str) -> str:
    count = source.count(before)
    if count != 1:
        raise BuildError(f"{label}: expected one anchor, found {count}")
    return source.replace(before, after, 1)


def prepend_item(source: str, marker: str, statement: str) -> str:
    if source.count(marker) != 1:
        raise BuildError(f"expected one item marker {marker!r}, found {source.count(marker)}")
    start = source.index(marker)
    opening = source.index("{", start)
    return source[: opening + 1] + statement + source[opening + 1 :]


RING_HELPERS = r'''
            fn banana_ring_frontdoor(view: &GameState) -> Option<Cell> {
                let mut gates = Self::banana_factory_home_doors(view, 0);
                gates.sort_unstable();
                if gates.len() < 2 {
                    return None;
                }
                let gate_distances: Vec<(Cell, BTreeMap<Cell, i32>)> = gates
                    .iter()
                    .map(|gate| (*gate, bfs_distances(&view.walkable, &[*gate])))
                    .collect();
                let mut max_pair = 0;
                for left in 0..gate_distances.len() {
                    for right in (left + 1)..gate_distances.len() {
                        max_pair = max_pair.max(
                            gate_distances[left]
                                .1
                                .get(&gate_distances[right].0)
                                .copied()
                                .unwrap_or(i32::MAX / 2),
                        );
                    }
                }
                if max_pair <= 8 {
                    return None;
                }
                let from_enemy = bfs_distances(&view.walkable, &[view.shacks[1]]);
                let mut viable: Vec<(Cell, i32)> = gate_distances
                    .iter()
                    .filter(|(_, distances)| {
                        view.walkable
                            .iter()
                            .filter(|cell| distances.get(cell).is_some_and(|steps| *steps <= 2))
                            .count()
                            >= 4
                    })
                    .map(|(gate, _)| (*gate, from_enemy.get(gate).copied().unwrap_or(0)))
                    .collect();
                viable.sort_by_key(|(gate, enemy_distance)| (-*enemy_distance, *gate));
                viable.first().map(|(gate, _)| *gate)
            }
            fn banana_ring_cells(&self, view: &GameState) -> &[Cell] {
                self.banana_ring_cells_cache.get_or_init(|| {
                    let home_doors = Self::banana_factory_home_doors(view, 0);
                    let from_home = bfs_distances(&view.walkable, &home_doors);
                    let frontdoor = Self::banana_ring_frontdoor(view);
                    let from_frontdoor = frontdoor
                        .map(|gate| bfs_distances(&view.walkable, &[gate]));
                    let shack = view.shacks[0];
                    let mut cells = Vec::new();
                    for dy in -1..=1 {
                        for dx in -1..=1 {
                            if dx == 0 && dy == 0 {
                                continue;
                            }
                            let cell = (shack.0 + dx, shack.1 + dy);
                            if !view.walkable.contains(&cell) || !from_home.contains_key(&cell) {
                                continue;
                            }
                            if from_frontdoor
                                .as_ref()
                                .is_some_and(|distances| {
                                    !distances.get(&cell).is_some_and(|steps| *steps <= 2)
                                })
                            {
                                continue;
                            }
                            cells.push(cell);
                        }
                    }
                    cells.sort_unstable();
                    cells
                }).as_slice()
            }
            fn banana_ring_is_diagonal(view: &GameState, cell: Cell) -> bool {
                (cell.0 - view.shacks[0].0).abs() == 1
                    && (cell.1 - view.shacks[0].1).abs() == 1
            }
            fn banana_ring_goal(&self, view: &GameState) -> usize {
                (self.banana_factory_initial_budget.unwrap_or(0).max(0) as usize)
                    .min(self.banana_ring_cells(view).len())
            }
            fn banana_ring_release_mothers(&self, view: &GameState) -> bool {
                if TOTAL_TURNS - view.turn <= 34 {
                    return true;
                }
                let from_home = self.banana_ring_home_distances_cache.get_or_init(|| {
                    bfs_distances(&view.walkable, &[view.shacks[0]])
                });
                view.units.iter().any(|unit| {
                    unit.player == 1
                        && from_home
                            .get(&unit.cell)
                            .is_some_and(|distance| *distance <= 4)
                })
            }
            fn banana_ring_plant_cell(&self, view: &GameState, unit: &Unit) -> Option<Cell> {
                let ring = self.banana_ring_cells(view);
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let has_live_mother = view.plants.iter().any(|plant| {
                    plant.health > 0
                        && plant.kind == PlantKind::Banana
                        && ring.contains(&plant.cell)
                        && Self::banana_ring_is_diagonal(view, plant.cell)
                });
                ring.iter().copied()
                    .filter(|cell| view.plant_at(*cell).is_none())
                    .filter(|cell| distance.contains_key(cell))
                    .filter(|cell| {
                        !view
                            .units
                            .iter()
                            .any(|other| other.id != unit.id && other.cell == *cell)
                    })
                    .min_by_key(|cell| {
                        (
                            if !has_live_mother && Self::banana_ring_is_diagonal(view, *cell) {
                                0
                            } else {
                                1
                            },
                            distance[cell],
                            *cell,
                        )
                    })
            }
            fn banana_ring_harvest_target(
                &self,
                view: &GameState,
                unit: &Unit,
            ) -> Option<(Cell, bool)> {
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                view.plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0
                            && plant.kind == PlantKind::Banana
                            && plant.fruits > 0
                            && ring.contains(&plant.cell)
                            && Self::banana_ring_is_diagonal(view, plant.cell)
                            && distance.contains_key(&plant.cell)
                    })
                    .min_by_key(|plant| (distance[&plant.cell], plant.cell))
                    .map(|plant| {
                        (
                            plant.cell,
                            self.banana_factory_owned_crops
                                .get(&plant.cell)
                                .copied()
                                .unwrap_or(false),
                        )
                    })
            }
            fn banana_ring_bank_command(view: &GameState, unit: &Unit) -> Option<String> {
                YamoBot::bank_candidates(view, unit)
                    .into_iter()
                    .max_by(|left, right| left.score.total_cmp(&right.score))
                    .map(|candidate| candidate.command)
            }
            fn banana_ring_issue_harvest(
                &mut self,
                view: &GameState,
                starter: &Unit,
                target: Cell,
                bank_source: bool,
            ) -> String {
                if starter.cell != target {
                    return format!("MOVE {} {} {}", starter.id, target.0, target.1);
                }
                self.banana_factory_harvest_selections += 1;
                if bank_source {
                    self.banana_factory_bank_harvest_selections += 1;
                } else {
                    self.banana_factory_conversion_harvest_selections += 1;
                }
                self.banana_factory_pending_harvest =
                    Some((view.turn, starter.carry[BANANA], bank_source));
                format!("HARVEST {}", starter.id)
            }
            fn banana_ring_starter_command(
                &mut self,
                view: &GameState,
                starter: &Unit,
            ) -> Option<String> {
                if starter.total_carried() > starter.carry[BANANA] {
                    return Self::banana_ring_bank_command(view, starter);
                }
                let goal = self.banana_ring_goal(view);
                let target = self
                    .banana_factory_plant_target
                    .filter(|cell| {
                        self.banana_ring_cells(view).contains(cell)
                            && view.plant_at(*cell).is_none()
                            && !view
                                .units
                                .iter()
                                .any(|other| other.id != starter.id && other.cell == *cell)
                    })
                    .or_else(|| self.banana_ring_plant_cell(view, starter));
                if starter.carry[BANANA] > 0 {
                    let Some(target) = target else {
                        self.banana_factory_plant_target = None;
                        return Self::banana_ring_bank_command(view, starter);
                    };
                    self.banana_factory_plant_target = Some(target);
                    let source = if self.banana_factory_seed_from_harvest
                        || self.banana_factory_bootstrap_successes >= goal
                    {
                        BananaFactoryPlantSource::RenewableHarvest
                    } else {
                        BananaFactoryPlantSource::BankBootstrap
                    };
                    if starter.cell != target {
                        return Some(format!("MOVE {} {} {}", starter.id, target.0, target.1));
                    }
                    match source {
                        BananaFactoryPlantSource::BankBootstrap => {
                            self.banana_factory_bootstrap_attempts += 1;
                        }
                        BananaFactoryPlantSource::RenewableHarvest => {
                            self.banana_factory_renewable_plant_attempts += 1;
                        }
                    }
                    self.banana_factory_pending_plant =
                        Some((view.turn, target, source, starter.carry[BANANA]));
                    return Some(format!("PLANT {} BANANA", starter.id));
                }
                if starter.free_capacity() <= 0 {
                    return Self::banana_ring_bank_command(view, starter);
                }
                let harvest = self.banana_ring_harvest_target(view, starter);
                if let Some((cell, bank_source)) = harvest.filter(|(cell, _)| {
                    manhattan(starter.cell, *cell) <= 1
                }) {
                    return Some(self.banana_ring_issue_harvest(
                        view,
                        starter,
                        cell,
                        bank_source,
                    ));
                }
                if self.banana_factory_bootstrap_successes < goal {
                    if let Some(target) = target {
                        let distance = bfs_distances(&view.walkable, &[starter.cell]);
                        let movement_turns = distance
                            .get(&target)
                            .map(|steps| MoisanBot::ceil_div(*steps, starter.stats.movement_speed));
                        if view.inventories[0][BANANA] > 0
                            && movement_turns.is_some_and(|turns| turns <= 2)
                        {
                            return Self::banana_factory_bank_command(view, starter);
                        }
                    }
                }
                harvest.map(|(cell, bank_source)| {
                    self.banana_ring_issue_harvest(view, starter, cell, bank_source)
                })
            }
            fn banana_ring_promote_reserve(&mut self, view: &GameState) {
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                let selected = view
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.health > 0
                            && plant.kind == PlantKind::Banana
                            && ring.contains(&plant.cell)
                            && Self::banana_ring_is_diagonal(view, plant.cell)
                    })
                    .map(|plant| plant.cell)
                    .min();
                if self.banana_factory_reserve != selected {
                    if self.banana_factory_reserve.is_some() {
                        self.banana_factory_reserve_losses += 1;
                    }
                    if selected.is_some() {
                        self.banana_factory_reserve_promotions += 1;
                    }
                    self.banana_factory_reserve = selected;
                }
            }
            fn banana_ring_wood_command(&mut self, view: &GameState, unit: &Unit) -> String {
                let mut candidates = if unit.total_carried() > 0 {
                    YamoBot::bank_candidates(view, unit)
                } else {
                    YamoBot::yamo_chop_candidates(
                        view,
                        unit,
                        self.inner.type_to_cut,
                        self.banana_factory_reserve,
                        self.inner.opponent_eta_penalty,
                    )
                };
                let ring: BTreeSet<Cell> = self.banana_ring_cells(view).iter().copied().collect();
                if !self.banana_ring_release_mothers(view) {
                    candidates.retain(|candidate| {
                        !matches!(
                            candidate.target,
                            Target::Tree(cell)
                                if ring.contains(&cell)
                                    && Self::banana_ring_is_diagonal(view, cell)
                        )
                    });
                }
                self.inner
                    .apply_opponent_crop_priority(view, unit, &mut candidates);
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let urgent = self.inner.crop_priority_active(view).then(|| {
                    candidates
                        .iter()
                        .filter(|candidate| {
                            let Target::Tree(cell) = candidate.target else {
                                return false;
                            };
                            self.inner.opponent_crops.contains(&cell)
                                && distance.get(&cell).is_some_and(|steps| {
                                    MoisanBot::ceil_div(*steps, unit.stats.movement_speed)
                                        <= self.inner.opponent_crop_eta_limit
                                })
                        })
                        .max_by(|left, right| left.score.total_cmp(&right.score))
                        .cloned()
                }).flatten();
                if let Some(selected) = urgent {
                    self.banana_factory_trained_opponent_crop_selections += 1;
                    return selected.command;
                }
                let orthogonal = candidates
                    .iter()
                    .filter(|candidate| {
                        let Target::Tree(cell) = candidate.target else {
                            return false;
                        };
                        ring.contains(&cell)
                            && !Self::banana_ring_is_diagonal(view, cell)
                            && view.plant_at(cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0
                                    && plant.kind == PlantKind::Banana
                                    && plant.size >= 2
                            })
                    })
                    .max_by(|left, right| left.score.total_cmp(&right.score))
                    .cloned();
                orthogonal
                    .or_else(|| {
                        candidates
                            .into_iter()
                            .max_by(|left, right| left.score.total_cmp(&right.score))
                    })
                    .map(|candidate| candidate.command)
                    .unwrap_or_else(|| "WAIT".to_string())
            }
            fn banana_ring_commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_banana_factory(view);
                if !self.banana_factory_active {
                    self.banana_factory_active = true;
                    self.banana_factory_activation_turn = Some(view.turn);
                }
                self.inner.external_idle_unit = None;
                self.inner.external_orchard_task = None;
                self.inner.external_protected_tree = self.banana_factory_reserve;
                self.inner.regeneration_commitments.clear();
                let mut commands = self.inner.commands(view);
                let mut unit_ids: Vec<_> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                unit_ids.sort_unstable();
                let Some(starter_id) = self.starter_id else {
                    return commands;
                };
                if let Some(starter) = view.unit(starter_id) {
                    if let Some(command) = self.banana_ring_starter_command(view, starter) {
                        Self::replace_action(&mut commands, &unit_ids, starter_id, command);
                    }
                }
                if !self.banana_ring_release_mothers(view) {
                    if let Some(starter) = view.unit(starter_id) {
                        let protected_mother = self.banana_ring_cells(view).contains(&starter.cell)
                            && Self::banana_ring_is_diagonal(view, starter.cell)
                            && view.plant_at(starter.cell).is_some_and(|index| {
                                let plant = &view.plants[index];
                                plant.health > 0 && plant.kind == PlantKind::Banana
                            });
                        if protected_mother {
                            if let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, starter_id) {
                                if commands[slot]
                                    .split_whitespace()
                                    .next()
                                    .is_some_and(|verb| verb == "CHOP")
                                {
                                    commands[slot] = "WAIT".to_string();
                                }
                            }
                        }
                    }
                }
                for unit in view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.id != starter_id)
                {
                    if let Some(slot) = Self::unit_action_slot(&commands, &unit_ids, unit.id) {
                        commands[slot] = self.banana_ring_wood_command(view, unit);
                        self.banana_factory_trained_role_rewrites += 1;
                    }
                }
                self.inner.regeneration_commitments.clear();
                self.inner.own_plant_attempts.clear();
                let priority = BTreeSet::from([starter_id]);
                let forbidden: BTreeSet<Cell> = if self.banana_ring_release_mothers(view) {
                    BTreeSet::new()
                } else {
                    self.banana_ring_cells(view)
                        .iter()
                        .copied()
                        .filter(|cell| Self::banana_ring_is_diagonal(view, *cell))
                        .collect()
                };
                MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    &mut commands,
                    &priority,
                    &forbidden,
                );
                self.inner.remember_own_plant_attempts(view, &commands);
                commands
            }
'''


RING_TESTS = r'''
        #[cfg(test)]
        mod banana_ring_tests {
            use super::*;
            fn banana_ring_fixture() -> GameState {
                let mut view = GameState::empty(7, 7);
                view.shacks = [(3, 3), (6, 6)];
                view.walkable = (0..7)
                    .flat_map(|y| (0..7).map(move |x| (x, y)))
                    .filter(|cell| *cell != (3, 3) && *cell != (6, 6))
                    .collect();
                view.units.push(Unit {
                    id: 7,
                    player: 0,
                    cell: (2, 3),
                    stats: Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        harvest_power: 1,
                        chop_power: 1,
                    },
                    carry: [0; 6],
                });
                view.units.push(Unit {
                    id: 8,
                    player: 0,
                    cell: (3, 2),
                    stats: Stats {
                        movement_speed: 2,
                        carry_capacity: 2,
                        harvest_power: 0,
                        chop_power: 2,
                    },
                    carry: [0; 6],
                });
                view
            }
            fn banana_ring_tree(cell: Cell, size: i32, fruits: i32) -> Plant {
                Plant {
                    kind: PlantKind::Banana,
                    cell,
                    size,
                    health: 2 + size,
                    fruits,
                    cooldown: 1,
                }
            }
            #[test]
            fn banana_ring_plant_target_never_leaves_ring() {
                let view = banana_ring_fixture();
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let target = bot.banana_ring_plant_cell(&view, view.unit(7).unwrap()).unwrap();
                assert!(bot.banana_ring_cells(&view).contains(&target));
                assert_eq!((target.0 - 3).abs().max((target.1 - 3).abs()), 1);
            }
            #[test]
            fn banana_ring_goal_caps_large_bank_at_capacity() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 24;
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                assert_eq!(bot.banana_ring_goal(&view), 8);
            }
            #[test]
            fn banana_ring_full_banks_surplus_and_never_picks() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 24;
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                for cell in bot.banana_ring_cells(&view).iter().copied() {
                    view.plants.push(banana_ring_tree(cell, 2, 0));
                }
                view.units[0].carry[BANANA] = 1;
                let mut bot = bot;
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap()).unwrap();
                assert!(command.starts_with("DROP ") || command.starts_with("MOVE "));
                assert!(!command.starts_with("PICK "));
                assert!(!command.contains("PLANT"));
            }
            #[test]
            fn banana_ring_pick_requires_target_within_two_move_turns() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 3;
                view.units[0].cell = (0, 0);
                let ring_bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                for cell in ring_bot.banana_ring_cells(&view).iter().copied() {
                    if cell != (4, 4) {
                        view.plants.push(banana_ring_tree(cell, 2, 0));
                    }
                }
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap());
                assert!(!command.is_some_and(|command| command.starts_with("PICK ")));
            }
            #[test]
            fn banana_ring_near_mother_harvest_beats_pick() {
                let mut view = banana_ring_fixture();
                view.inventories[0][BANANA] = 3;
                view.plants.push(banana_ring_tree((2, 2), 4, 1));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                let command = bot.banana_ring_starter_command(&view, view.unit(7).unwrap()).unwrap();
                assert_eq!(command, "MOVE 7 2 2");
            }
            #[test]
            fn banana_ring_harvests_diagonal_not_orthogonal() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((2, 2), 4, 1));
                view.plants.push(banana_ring_tree((3, 2), 4, 3));
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(
                    bot.banana_ring_harvest_target(&view, view.unit(7).unwrap()).map(|pair| pair.0),
                    Some((2, 2))
                );
            }
            #[test]
            fn banana_ring_chops_size_two_orthogonal() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((3, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "CHOP 8");
            }
            #[test]
            fn banana_ring_keeps_diagonal_before_release() {
                let mut view = banana_ring_fixture();
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "WAIT");
            }
            #[test]
            fn banana_ring_releases_diagonal_in_endgame() {
                let mut view = banana_ring_fixture();
                view.turn = 270;
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(bot.banana_ring_wood_command(&view, view.unit(8).unwrap()), "CHOP 8");
            }
            #[test]
            fn banana_ring_releases_diagonal_under_local_raid() {
                let mut view = banana_ring_fixture();
                view.units[1].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                view.units.push(Unit {
                    id: 9,
                    player: 1,
                    cell: (4, 3),
                    stats: Stats { movement_speed: 1, carry_capacity: 1, harvest_power: 0, chop_power: 1 },
                    carry: [0; 6],
                });
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                assert_eq!(bot.banana_ring_wood_command(&view, view.unit(8).unwrap()), "CHOP 8");
            }
            #[test]
            fn banana_ring_frontdoor_excludes_far_side() {
                let mut view = GameState::empty(11, 7);
                view.shacks = [(5, 2), (10, 2)];
                for x in 0..=4 {
                    for y in 0..=6 {
                        view.walkable.insert((x, y));
                    }
                }
                for x in 6..=10 {
                    for y in 0..=6 {
                        view.walkable.insert((x, y));
                    }
                }
                view.walkable.insert((5, 6));
                view.walkable.remove(&(10, 2));
                let bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let ring = bot.banana_ring_cells(&view);
                assert!(ring.iter().all(|cell| cell.0 < 5));
                assert!(ring.contains(&(4, 2)));
            }
            #[test]
            fn banana_ring_eta6_opponent_crop_beats_orthogonal_cut() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((3, 2), 2, 0));
                view.plants.push(Plant {
                    kind: PlantKind::Plum,
                    cell: (0, 2),
                    size: 4,
                    health: 12,
                    fruits: 0,
                    cooldown: 1,
                });
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.inner.opponent_crops_seen = 1;
                bot.inner.opponent_crops.insert((0, 2));
                let command = bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                assert_eq!(command, "MOVE 8 0 2");
            }
            #[test]
            fn banana_ring_own_plant_is_not_opponent_provenance() {
                let mut view = banana_ring_fixture();
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.inner.reconcile_opponent_crops(&view);
                view.units[0].cell = (2, 3);
                bot.inner
                    .remember_own_plant_attempts(&view, &["PLANT 7 BANANA".to_string()]);
                view.turn += 1;
                view.plants.push(banana_ring_tree((2, 3), 1, 0));
                bot.inner.reconcile_opponent_crops(&view);
                assert!(!bot.inner.opponent_crops.contains(&(2, 3)));
                assert_eq!(bot.inner.opponent_crops_seen, 0);
            }
            #[test]
            fn banana_ring_clears_harvest_seed_after_observed_drop() {
                let view = banana_ring_fixture();
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                bot.initialize(&view);
                bot.banana_factory_seed_from_harvest = true;
                bot.reconcile_banana_factory(&view);
                assert!(!bot.banana_factory_seed_from_harvest);
            }
            #[test]
            fn banana_ring_wrapper_regenerates_worker_command() {
                let mut view = banana_ring_fixture();
                view.plants.push(banana_ring_tree((4, 3), 2, 0));
                let mut expected_bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                expected_bot.initialize(&view);
                let expected = expected_bot.banana_ring_wood_command(&view, view.unit(8).unwrap());
                let mut wrapped = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let commands = wrapped.commands(&view);
                let unit_ids = vec![7, 8];
                let slot = SecureOrchardBot::unit_action_slot(&commands, &unit_ids, 8).unwrap();
                assert_eq!(commands[slot], expected);
            }
            #[test]
            fn banana_ring_starter_never_chops_unripe_mother_before_release() {
                let mut view = banana_ring_fixture();
                view.units[0].cell = (2, 2);
                view.plants.push(banana_ring_tree((2, 2), 2, 0));
                let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();
                let commands = bot.commands(&view);
                let slot = SecureOrchardBot::unit_action_slot(&commands, &[7, 8], 7).unwrap();
                assert_ne!(commands[slot], "CHOP 7");
            }
        }
'''


def inject(source: str) -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from cgauto.slim_live_source import _item_span
    finally:
        sys.path.pop(0)

    source = replace_once(
        source,
        "            banana_factory_enabled: bool,\n",
        "            banana_factory_enabled: bool,\n            banana_factory_ring: bool,\n            banana_ring_cells_cache: std::cell::OnceCell<Vec<Cell>>,\n            banana_ring_home_distances_cache: std::cell::OnceCell<BTreeMap<Cell, i32>>,\n",
        "ring field",
    )
    source = replace_once(
        source,
        "                    banana_factory_enabled: false,\n",
        "                    banana_factory_enabled: false,\n                    banana_factory_ring: false,\n                    banana_ring_cells_cache: std::cell::OnceCell::new(),\n                    banana_ring_home_distances_cache: std::cell::OnceCell::new(),\n",
        "ring field initialization",
    )
    constructor_anchor = "            pub fn banana_seed_factory_source_separated() -> Self {"
    constructor = '''            pub fn banana_ring_opponent_crop_b100_e6() -> Self {
                let mut bot = Self::banana_seed_factory();
                bot.banana_factory_ring = true;
                bot.inner.opponent_crop_bonus = 100;
                bot.inner.opponent_crop_eta_limit = 6;
                bot.inner.opponent_crop_start_turn = 1;
                bot.inner.opponent_crop_min_seen = 1;
                bot
            }
'''
    source = replace_once(source, constructor_anchor, constructor + constructor_anchor, "constructor")
    helper_anchor = "            fn banana_factory_plant_cell(\n"
    source = replace_once(source, helper_anchor, RING_HELPERS + helper_anchor, "ring helpers")
    for marker, statement in (
        ("fn banana_factory_plant_cell(", "\n                if self.banana_factory_ring { return self.banana_ring_plant_cell(view, unit); }"),
        ("fn banana_factory_promote_reserve(", "\n                if self.banana_factory_ring { self.banana_ring_promote_reserve(view); return; }"),
        ("fn banana_factory_harvest_target(", "\n                if self.banana_factory_ring { return self.banana_ring_harvest_target(view, unit); }"),
        ("fn banana_factory_starter_command(", "\n                if self.banana_factory_ring { return self.banana_ring_starter_command(view, starter); }"),
        ("fn banana_factory_wood_command(", "\n                if self.banana_factory_ring { return self.banana_ring_wood_command(view, unit); }"),
        ("fn banana_factory_commands(", "\n                if self.banana_factory_ring { return self.banana_ring_commands(view); }"),
    ):
        source = prepend_item(source, marker, statement)

    start, end = _item_span(source, "fn reconcile_banana_factory(")
    reconcile_tail = '''
                if self.banana_factory_ring
                    && self.banana_factory_pending_harvest.is_none()
                    && self.banana_factory_pending_plant.is_none()
                    && self
                        .starter_id
                        .and_then(|id| view.unit(id))
                        .is_some_and(|starter| starter.carry[BANANA] == 0)
                {
                    self.banana_factory_seed_from_harvest = false;
                }
'''
    source = source[: end - 1].rstrip() + "\n" + reconcile_tail.lstrip("\n") + source[end - 1 :]
    source = replace_once(
        source,
        "    let mut bot = SecureOrchardBot::new();",
        "    let mut bot = SecureOrchardBot::banana_ring_opponent_crop_b100_e6();",
        "main activation",
    )
    tests_anchor = "        }\n        impl Bot for SecureOrchardBot {"
    source = replace_once(source, tests_anchor, "        }\n" + RING_TESTS + "        impl Bot for SecureOrchardBot {", "ring tests")
    return source


def compact(repo: Path, source: str) -> str:
    sys.path.insert(0, str(repo))
    try:
        from cgauto.compact_rust_source import compact as compact_rust
        return compact_rust(source)
    finally:
        sys.path.pop(0)


def build(repo: Path, output_dir: Path) -> dict:
    repo = repo.resolve()
    source_path = repo / SOURCE_REL
    source_payload = verify(source_path, SOURCE_SHA256, "byte-sacred source")
    verify(repo / CONTROL_REL, CONTROL_SHA256, "fallback control")
    research = inject(source_payload.decode())
    if source_path.read_bytes() != source_payload:
        raise BuildError("byte-sacred source changed during generation")
    compacted = compact(repo, research)
    output_dir.mkdir(parents=True, exist_ok=True)
    research_path = output_dir / "banana-ring-b100-e6.research.rs"
    compact_path = output_dir / "banana-ring-b100-e6.compact.rs"
    research_path.write_text(research)
    compact_path.write_text(compacted)
    for path in (research_path, compact_path):
        path.with_name(path.name + ".sha256").write_text(f"{digest(path.read_bytes())}  {path.name}\n")
    manifest = {
        "schema": "troll-farm-banana-ring-b100-e6-research-build-v1",
        "status": "research_only_not_submission_ready",
        "inputs": {
            "source": str(SOURCE_REL),
            "source_sha256": SOURCE_SHA256,
            "control": str(CONTROL_REL),
            "control_sha256": CONTROL_SHA256,
        },
        "intervention": {
            "constructor": "banana_ring_opponent_crop_b100_e6",
            "banana_ring": True,
            "opponent_crop_bonus": 100,
            "opponent_crop_eta_limit": 6,
        },
        "outputs": {
            "research": {
                "path": str(research_path),
                "sha256": digest(research_path.read_bytes()),
                "bytes": research_path.stat().st_size,
            },
            "compact": {
                "path": str(compact_path),
                "sha256": digest(compact_path.read_bytes()),
                "bytes": compact_path.stat().st_size,
            },
        },
    }
    manifest_path = output_dir / "banana-ring-b100-e6.build.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.repo, args.output_dir), indent=2))
    except (BuildError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
