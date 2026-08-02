#!/usr/bin/env python3
"""Build the first half-size E7a controller by replacing named live subsystems.

The input must be the exact immutable E7a submission.  This builder does not rename any
identifier and does not run a minifier.  It removes the secure-orchard wrapper and replaces
the general Yamo orchestration, tree forecast, selector, and movement router with readable,
focused two-worker logic while retaining the protocol parser and exact E7a focus rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import _remove_item, _replace_item  # noqa: E402


BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
BASELINE_BYTES = 62_820
TARGET_BYTES = 31_410


YAMO_STRUCT = """pub struct YamoBot {
            announced: bool,
            type_to_cut: Option<PlantKind>,
            desired_second: Option<Stats>,
        }"""


YAMO_IMPL = r"""impl YamoBot {
            pub fn new() -> Self {
                Self { announced: false, type_to_cut: None, desired_second: None }
            }

            fn ensure_opening(&mut self, view: &GameState) {
                if self.type_to_cut.is_none() {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                }
                if self.desired_second.is_none() {
                    self.desired_second = Some(Self::choose_second_troll(view));
                }
            }

            fn choose_second_troll(view: &GameState) -> Stats {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let choices = [
                    (2, 2, 2),
                    (2, 2, 3),
                    (2, 2, 1),
                    (3, 2, 2),
                    (2, 3, 2),
                    (1, 2, 2),
                    (2, 1, 2),
                ];
                choices
                    .into_iter()
                    .map(|(movement_speed, carry_capacity, chop_power)| Stats {
                        movement_speed,
                        carry_capacity,
                        harvest_power: 0,
                        chop_power,
                    })
                    .max_by_key(|stats| {
                        let cost = training_cost(1, stats.tuple());
                        let eta = [PLUM, LEMON, IRON]
                            .into_iter()
                            .filter(|item| *item != IRON || !view.iron.is_empty())
                            .map(|item| {
                                let missing = (cost[item] - view.inventories[0][item]).max(0);
                                let travel = if item == IRON {
                                    view.iron.iter()
                                        .flat_map(|cell| ortho_neighbors(*cell))
                                        .filter_map(|cell| distance.get(&cell))
                                        .copied()
                                        .min()
                                } else {
                                    let kind = if item == PLUM {
                                        PlantKind::Plum
                                    } else {
                                        PlantKind::Lemon
                                    };
                                    view.plants.iter()
                                        .filter(|plant| plant.kind == kind && plant.health > 0)
                                        .filter_map(|plant| distance.get(&plant.cell))
                                        .copied()
                                        .min()
                                }.unwrap_or(10_000);
                                missing * (2 * travel + 2)
                            })
                            .sum::<i32>();
                        (
                            eta <= 15,
                            if eta <= 15 {
                                stats.movement_speed
                                    + stats.carry_capacity
                                    + stats.chop_power
                            } else {
                                -eta
                            },
                            -eta,
                            stats.chop_power,
                            stats.carry_capacity,
                            stats.movement_speed,
                        )
                    })
                    .unwrap()
            }

            fn fixed_bank_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let door = if starts.contains(&unit.cell) {
                    Some(unit.cell)
                } else {
                    let mut reachable: Vec<Cell> = starts
                        .into_iter()
                        .filter(|cell| distance.contains_key(cell))
                        .collect();
                    reachable.sort();
                    let slot = view.units.iter().filter(|other| {
                        other.player == 0 && other.id < unit.id
                    }).count();
                    (!reachable.is_empty()).then(|| reachable[slot % reachable.len()])
                };
                let Some(door) = door else { return vec![MoisanBot::wait()] };
                vec![Candidate {
                    command: if unit.cell == door {
                        format!("DROP {}", unit.id)
                    } else {
                        format!("MOVE {} {} {}", unit.id, door.0, door.1)
                    },
                    score: if unit.cell == door { 21_000.0 } else { 20_000.0 },
                    target: Target::Bank(door),
                }, MoisanBot::wait()]
            }

            fn carried_fruit(unit: &Unit) -> Option<PlantKind> {
                [
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                    (BANANA, PlantKind::Banana),
                ]
                .into_iter()
                .find(|(item, _)| unit.carry[*item] > 0)
                .map(|(_, kind)| kind)
            }

            fn bank_fruit(view: &GameState) -> Option<PlantKind> {
                [
                    (BANANA, PlantKind::Banana),
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                ]
                .into_iter()
                .find(|(item, _)| view.inventories[0][*item] > 0)
                .map(|(_, kind)| kind)
            }

            fn conversion_chop_turns(
                kind: PlantKind,
                chop_power: i32,
            ) -> i32 {
                MoisanBot::ceil_div(tree_health(kind, 1), chop_power)
            }

            fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                focus: Option<PlantKind>,
            ) -> Vec<Candidate> {
                if unit.carry[WOOD] > 0 {
                    return Self::fixed_bank_candidates(view, unit);
                }
                let turns_left = TOTAL_TURNS - view.turn + 1;
                if let Some(kind) = Self::carried_fruit(unit) {
                    if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2) {
                        return Self::fixed_bank_candidates(view, unit);
                    }
                    let distance = bfs_distances(&view.walkable, &[unit.cell]);
                    let target = ortho_neighbors(view.shacks[0])
                        .into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| view.plant_at(*cell).is_none())
                        .filter(|cell| distance.contains_key(cell))
                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
                        .min_by_key(|cell| (distance[cell], *cell));
                    let Some(cell) = target else {
                        return Self::fixed_bank_candidates(view, unit);
                    };
                    let travel = MoisanBot::ceil_div(
                        distance[&cell], unit.stats.movement_speed
                    );
                    if travel + Self::conversion_chop_turns(
                        kind, unit.stats.chop_power
                    ) + 3 > turns_left {
                        return Self::fixed_bank_candidates(view, unit);
                    }
                    return vec![Candidate {
                        command: if unit.cell == cell {
                            format!("PLANT {} {}", unit.id, kind.as_str())
                        } else {
                            format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                        },
                        score: 9_000.0 - travel as f64,
                        target: Target::Cell(cell),
                    }];
                }
                if unit.total_carried() > 0 {
                    return Self::fixed_bank_candidates(view, unit);
                }
                let mut out = vec![MoisanBot::wait()];
                let chops = MoisanBot::chop_candidates(view, unit, focus);
                if let Some(mut current) = chops
                    .iter()
                    .find(|candidate| candidate.command == format!("CHOP {}", unit.id))
                    .cloned()
                {
                    current.score = 10_000.0;
                    out.push(current);
                    return out;
                }
                if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2 {
                    if let Some(kind) = Self::bank_fruit(view) {
                    if is_adjacent(unit.cell, view.shacks[0])
                        && view.plant_at(unit.cell).is_none()
                        && Self::conversion_chop_turns(
                            kind, unit.stats.chop_power
                        ) + 3 <= turns_left
                    {
                        out.push(Candidate {
                            command: format!("PICK {} {}", unit.id, kind.as_str()),
                            score: 8_000.0,
                            target: Target::Cell(unit.cell),
                        });
                    }
                    }
                }
                out.extend(chops);
                out
            }

            fn ordinary_candidates(
                view: &GameState,
                unit: &Unit,
                early: bool,
                desired: Stats,
                focus: PlantKind,
            ) -> Vec<Candidate> {
                if early {
                    return MoisanBot::early_candidates(view, unit, desired);
                }
                Self::endgame_candidates(view, unit, Some(focus))
            }
        }"""


BOT_IMPL = r"""impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.ensure_opening(view);
                if view.turn >= 35
                    && self.desired_second
                        .is_some_and(|stats| !MoisanBot::can_train(view, stats))
                {
                    self.desired_second = Some(Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        harvest_power: 0,
                        chop_power: 1,
                    });
                }
                let desired = self.desired_second.unwrap();
                let train_now = MoisanBot::can_train(view, desired);
                let mut output = Vec::new();
                if !self.announced {
                    self.announced = true;
                    output.push("MSG e7a-half-size-logical".to_string());
                }
                if train_now {
                    output.push(format!(
                        "TRAIN {} {} {} {}",
                        desired.movement_speed,
                        desired.carry_capacity,
                        desired.harvest_power,
                        desired.chop_power
                    ));
                }
                let mut units: Vec<&Unit> = view.units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .collect();
                units.sort_by_key(|unit| unit.id);
                let early = units.len() < 2 && !train_now;
                let mut candidates_by_id = BTreeMap::new();
                for unit in units {
                    let mut candidates = if view.turn > 250 {
                        Self::endgame_candidates(view, unit, self.type_to_cut)
                    } else {
                        Self::ordinary_candidates(
                            view,
                            unit,
                            early,
                            desired,
                            self.type_to_cut.unwrap(),
                        )
                    };
                    if train_now
                        && unit.cell == view.shacks[0]
                        && !candidates.iter().any(|row| row.command.starts_with("MOVE "))
                    {
                        if let Some(cell) = ortho_neighbors(view.shacks[0])
                            .into_iter()
                            .find(|cell| view.walkable.contains(cell))
                        {
                            candidates.push(Candidate {
                                command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                                score: 19_000.0,
                                target: Target::Cell(cell),
                            });
                        }
                    }
                    candidates_by_id.insert(unit.id, candidates);
                }
                let mut selected = MoisanBot::select(
                    candidates_by_id, &view.inventories[0]
                );
                MoisanBot::resolve_move_conflicts(view, &mut selected);
                output.extend(selected);
                if output.is_empty() { output.push("WAIT".to_string()); }
                output
            }
        }"""


DIRECT_CHOP_CANDIDATES = r"""fn chop_candidates(
                view: &GameState,
                unit: &Unit,
                type_to_cut: Option<PlantKind>,
            ) -> Vec<Candidate> {
                let mut out = Vec::new();
                if unit.stats.chop_power <= 0 || unit.free_capacity() <= 0 {
                    return out;
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let to_shack = bfs_distances(&view.walkable, &doors);
                let few_opponents = view.units.iter().filter(|row| row.player == 1).count() <= 2;
                for plant in &view.plants {
                    if plant.health <= 0 || !from_unit.contains_key(&plant.cell) {
                        continue;
                    }
                    let travel = Self::ceil_div(
                        from_unit[&plant.cell], unit.stats.movement_speed
                    );
                    let chop = Self::ceil_div(plant.health, unit.stats.chop_power);
                    let home = to_shack
                        .get(&plant.cell)
                        .map(|distance| Self::ceil_div(*distance, unit.stats.movement_speed))
                        .unwrap_or_else(|| Self::ceil_div(
                            manhattan(plant.cell, view.shacks[0]),
                            unit.stats.movement_speed,
                        ));
                    let turns = (travel + chop + home + 1).max(1);
                    if turns > TOTAL_TURNS - view.turn + 1 {
                        continue;
                    }
                    let wood = plant.size.max(1).min(unit.free_capacity());
                    let mut score = 1_000.0 * wood as f64 / turns as f64;
                    if Some(plant.kind) == type_to_cut && few_opponents {
                        score += 900.0 / (1 + manhattan(plant.cell, view.shacks[1])) as f64;
                    }
                    out.push(Candidate {
                        command: if unit.cell == plant.cell {
                            format!("CHOP {}", unit.id)
                        } else {
                            format!("MOVE {} {} {}", unit.id, plant.cell.0, plant.cell.1)
                        },
                        score,
                        target: Target::Tree(plant.cell),
                    });
                }
                out
            }"""


TWO_WORKER_SELECT = r"""fn select(
                candidates_by_id: BTreeMap<i32, Vec<Candidate>>,
                inventory: &[i32; 6],
            ) -> Vec<String> {
                let ids: Vec<i32> = candidates_by_id.keys().copied().collect();
                if ids.is_empty() {
                    return Vec::new();
                }
                if ids.len() == 1 {
                    return candidates_by_id[&ids[0]]
                        .iter()
                        .max_by(|a, b| a.score.total_cmp(&b.score))
                        .map(|row| vec![row.command.clone()])
                        .unwrap_or_default();
                }
                let mut best: Option<(f64, String, String)> = None;
                for a in &candidates_by_id[&ids[0]] {
                    for b in &candidates_by_id[&ids[1]] {
                        if !Self::compatible(a.target, b.target)
                            || !Self::stock_compatible(a, b, inventory)
                        {
                            continue;
                        }
                        let score = a.score + b.score;
                        if best.as_ref().map(|row| score > row.0).unwrap_or(true) {
                            best = Some((score, a.command.clone(), b.command.clone()));
                        }
                    }
                }
                best.map(|row| vec![row.1, row.2]).unwrap_or_default()
            }"""


TWO_WORKER_MOVE_GUARD = r"""fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                let mut own: Vec<&Unit> = view.units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .collect();
                own.sort_by_key(|unit| unit.id);
                let mut reserved: BTreeSet<Cell> = view.units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.cell)
                    .collect();
                let mut order: Vec<usize> = (0..commands.len()).collect();
                order.sort_by_key(|index| {
                    own.get(*index).map(|unit| unit.total_carried() == 0).unwrap_or(true)
                });
                let mut forced = BTreeSet::new();
                for index in order {
                    if forced.contains(&index) { continue; }
                    let Some((id, target)) = Self::move_command(&commands[index]) else {
                        continue;
                    };
                    let Some(unit) = view.unit(id) else { continue };
                    let landing = next_cell(
                        &view.walkable,
                        unit.cell,
                        target,
                        unit.stats.movement_speed,
                    );
                    if landing == unit.cell {
                        commands[index] = "WAIT".to_string();
                        continue;
                    }
                    if unit.total_carried() > 0 && reserved.contains(&landing) {
                        let blocker = own.iter().find(|other| other.cell == landing);
                        if let Some(blocker) = blocker.filter(|other| other.total_carried() == 0) {
                            let egress = ortho_neighbors(blocker.cell)
                                .into_iter()
                                .filter(|cell| view.walkable.contains(cell))
                                .filter(|cell| !own.iter().any(|other| {
                                    other.id != blocker.id && other.cell == *cell
                                }))
                                .min_by_key(|cell| (manhattan(*cell, view.shacks[0]), *cell))
                                .or_else(|| {
                                    is_adjacent(blocker.cell, unit.cell).then_some(unit.cell)
                                });
                            if let (Some(egress), Some(blocker_index)) = (
                                egress,
                                own.iter().position(|other| other.id == blocker.id),
                            ) {
                                commands[blocker_index] = format!(
                                    "MOVE {} {} {}", blocker.id, egress.0, egress.1
                                );
                                forced.insert(blocker_index);
                                reserved.remove(&landing);
                                reserved.insert(egress);
                            }
                        }
                    }
                    commands[index] = if !reserved.contains(&landing) {
                        reserved.insert(landing);
                        format!("MOVE {} {} {}", id, landing.0, landing.1)
                    } else {
                        "WAIT".to_string()
                    };
                }
            }"""


ORCHARD_ITEMS = (
    "enum OrchardPhase",
    "struct OrchardGeometry",
    "struct OrchardCycle",
    "pub struct SecureOrchardBot",
    "impl SecureOrchardBot",
    "impl Bot for SecureOrchardBot",
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def lexical_identifiers(text: str) -> set[str]:
    return set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text))


def build(source: str) -> tuple[str, dict]:
    if len(source.encode()) != BASELINE_BYTES or digest(source) != BASELINE_SHA256:
        raise ValueError("input is not the exact E7a baseline")
    result = source
    gross_removed = []

    def remove(marker: str, block: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _remove_item(result, marker)
        gross_removed.append(
            {"block": block, "marker": marker, "gross_removed_bytes": before - len(result.encode())}
        )

    def replace(marker: str, replacement: str, block: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _replace_item(result, marker, replacement)
        gross_removed.append(
            {
                "block": block,
                "marker": marker,
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(replacement.encode()),
            }
        )

    for marker in ORCHARD_ITEMS:
        remove(marker, "secure_orchard_removed")
    remove("pub struct YamoOpeningPolicy", "general_opening_policy_removed")
    remove("impl YamoOpeningPolicy", "general_opening_policy_removed")
    remove("struct OpeningObjective", "general_opening_policy_removed")
    orphaned_orchard_derives = (
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
        "#[derive(Clone,Debug)]"
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    )
    if result.count(orphaned_orchard_derives) != 1:
        raise ValueError("expected one orphaned orchard derive sequence")
    result = result.replace(orphaned_orchard_derives, "", 1)
    gross_removed.append(
        {
            "block": "secure_orchard_removed",
            "marker": "three derives belonging to removed orchard types",
            "gross_removed_bytes": len(orphaned_orchard_derives.encode()),
        }
    )
    duplicate_yamo_derive = (
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    )
    if result.count(duplicate_yamo_derive) != 1:
        raise ValueError("expected removed opening policy to leave one duplicate derive")
    result = result.replace(
        duplicate_yamo_derive,
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]",
        1,
    )
    gross_removed.append(
        {
            "block": "general_opening_policy_removed",
            "marker": "derive belonging to removed opening policy",
            "gross_removed_bytes": len("#[derive(Clone,Copy,Debug,Eq,PartialEq)]".encode()),
        }
    )
    replace("pub struct YamoBot", YAMO_STRUCT, "focused_state_replacement")
    replace("impl YamoBot", YAMO_IMPL, "focused_two_worker_orchestration")
    replace("impl Bot for YamoBot", BOT_IMPL, "focused_two_worker_orchestration")
    remove(
        "#[derive(Clone,Copy)]struct PredictedTree",
        "full_tree_growth_forecast_removed",
    )
    remove("fn predicted_opp_chop(", "full_tree_growth_forecast_removed")
    remove("fn predict_tree(", "full_tree_growth_forecast_removed")
    remove("fn chop_outcome(", "full_tree_growth_forecast_removed")
    replace(
        "fn chop_candidates(",
        DIRECT_CHOP_CANDIDATES,
        "direct_harvest_cycle_replacement",
    )
    replace("fn select(", TWO_WORKER_SELECT, "two_worker_selector_replacement")
    replace(
        "fn resolve_move_conflicts(",
        TWO_WORKER_MOVE_GUARD,
        "two_worker_collision_guard_replacement",
    )
    remove(
        "fn resolve_move_conflicts_with_priority(",
        "general_priority_router_removed",
    )
    remove(
        "fn resolve_move_conflicts_with_priority_and_forbidden(",
        "general_priority_router_removed",
    )
    if result.count("Self::carrying_any(unit)") != 1:
        raise ValueError("expected one redundant carrying-any call")
    result = result.replace("Self::carrying_any(unit)", "unit.total_carried() > 0", 1)
    remove("fn carry_total(", "redundant_carry_helpers_removed")
    remove("fn carrying_any(", "redundant_carry_helpers_removed")
    remove("pub fn item_index(self)", "orphaned_plant_kind_api_removed")
    remove("pub fn plant_cooldown(", "orphaned_growth_rules_removed")
    remove("pub fn water_boost(", "orphaned_growth_rules_removed")
    remove("pub fn effective_cooldown(", "orphaned_growth_rules_removed")
    replace(
        "fn ticks_until_fruit(",
        "fn ticks_until_fruit(_view:&GameState,plant:&Plant)->i32{"
        "if plant.fruits>0{0}else{plant.cooldown.max(0)}}",
        "direct_fruit_readiness_replacement",
    )

    replacements = (
        (
            "effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,",
            "item_index,training_cost,tree_health,TOTAL_TURNS,",
        ),
        (
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,};",
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,WOOD,};",
        ),
        ("use crate::bot::moisan::SecureOrchardBot;", "use crate::bot::moisan::YamoBot;"),
        ("let mut bot=SecureOrchardBot::new();", "let mut bot=YamoBot::new();"),
    )
    for old, new in replacements:
        if result.count(old) != 1:
            raise ValueError(f"expected one main fragment {old!r}")
        result = result.replace(old, new, 1)
    baseline_identifiers = lexical_identifiers(source)
    candidate_identifiers = lexical_identifiers(result)
    manifest = {
        "schema": "troll-farm-e7a-integrated-half-builder-v1",
        "baseline": {"bytes": BASELINE_BYTES, "sha256": BASELINE_SHA256},
        "candidate": {
            "bytes": len(result.encode()),
            "sha256": digest(result),
            "target_bytes": TARGET_BYTES,
            "within_target": len(result.encode()) <= TARGET_BYTES,
        },
        "non_obfuscation": {
            "whole_source_minifier_run": False,
            "identifier_renaming_run": False,
            "encoding_or_compression": False,
            "construction": "unique named item removal/replacement only",
            "lexical_identifier_audit": {
                "baseline_unique": len(baseline_identifiers),
                "candidate_unique": len(candidate_identifiers),
                "preserved_unique": len(baseline_identifiers & candidate_identifiers),
                "removed_with_declared_blocks": sorted(
                    baseline_identifiers - candidate_identifiers
                ),
                "added_by_readable_replacements": sorted(
                    candidate_identifiers - baseline_identifiers
                ),
                "renaming_mapping": None,
            },
        },
        "logical_changes": gross_removed,
        "preserved_exact_items": [
            "protocol input parser and GameState data layout",
            "MoisanBot::focus_type E7a threshold",
            "MoisanBot::can_train legality check",
            "fruit and iron target enumeration",
        ],
        "replacement_behaviors": [
            "seven-profile worker-two bill selection with turn-35 cheap fallback",
            "direct harvest-cycle valuation without future-growth simulation",
            "two-worker stock/target-compatible pair selection",
            "two-worker occupied-cell and landing reservation guard",
            "bounded shack-door endgame fruit-to-wood conversion",
        ],
    }
    return result, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    candidate, manifest = build(args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest["candidate"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
