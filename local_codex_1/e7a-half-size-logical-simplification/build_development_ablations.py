#!/usr/bin/env python3
"""Build readable oversized attribution arms from the exact E7a source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.slim_live_source import _item_span, _remove_item, _replace_item  # noqa: E402
from build_integrated_half import (  # noqa: E402
    BOT_IMPL,
    TWO_WORKER_MOVE_GUARD,
    YAMO_IMPL,
    YAMO_STRUCT,
    lexical_identifiers,
)


BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
ORCHARD_ITEMS = (
    "enum OrchardPhase",
    "struct OrchardGeometry",
    "struct OrchardCycle",
    "pub struct SecureOrchardBot",
    "impl SecureOrchardBot",
    "impl Bot for SecureOrchardBot",
)
ORPHANED_DERIVES = (
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    "#[derive(Clone,Debug)]"
    "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def item_text(source: str, marker: str) -> str:
    start, end = _item_span(source, marker)
    return source[start:end]


def orchard_only(source: str) -> tuple[str, dict]:
    if sha256_bytes(source.encode()) != BASELINE_SHA256:
        raise ValueError("input is not the exact E7a source")
    result = source
    removals = []
    for marker in ORCHARD_ITEMS:
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    if result.count(ORPHANED_DERIVES) != 1:
        raise ValueError("unexpected orchard derive sequence")
    result = result.replace(ORPHANED_DERIVES, "", 1)
    yamo_impl = "impl YamoBot{"
    if result.count(yamo_impl) != 1:
        raise ValueError("unexpected YamoBot implementation count")
    result = result.replace(
        yamo_impl,
        yamo_impl
        + "pub fn new()->Self{"
        + "Self::tuned_carry_regeneration_transit_idle_harvest()}",
        1,
    )
    replacements = (
        ("use crate::bot::moisan::SecureOrchardBot;", "use crate::bot::moisan::YamoBot;"),
        (
            "let mut bot=SecureOrchardBot::new();",
            "let mut bot=YamoBot::new();",
        ),
    )
    for old, new in replacements:
        if result.count(old) != 1:
            raise ValueError(f"expected one {old!r}")
        result = result.replace(old, new, 1)
    manifest = {
        "schema": "troll-farm-e7a-development-ablation/1",
        "arm": "ORCHARD_REMOVED_CORE_EXACT",
        "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        "baseline_sha256": BASELINE_SHA256,
        "candidate_bytes": len(result.encode()),
        "candidate_sha256": sha256_bytes(result.encode()),
        "logical_change": "remove SecureOrchardBot and run the otherwise exact inner YamoBot",
        "removed_items": removals,
        "identifier_renaming": False,
        "minification": False,
    }
    return result, manifest


def focused_yamo_exact_moisan(
    source: str,
    *,
    yamo_impl: str = YAMO_IMPL,
    arm: str = "FOCUSED_YAMO_EXACT_MOISAN",
    logical_change: str = (
        "remove orchard and general opening/Yamo orchestration while retaining exact "
        "Moisan chop forecast, selector, target model, movement, and banking"
    ),
) -> tuple[str, dict]:
    """Remove the orchard and specialize Yamo while retaining exact Moisan economics."""

    if sha256_bytes(source.encode()) != BASELINE_SHA256:
        raise ValueError("input is not the exact E7a source")
    result = source
    removals = []
    for marker in ORCHARD_ITEMS:
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    for marker in (
        "pub struct YamoOpeningPolicy",
        "impl YamoOpeningPolicy",
        "struct OpeningObjective",
    ):
        before = len(result.encode())
        result = _remove_item(result, marker)
        removals.append({"marker": marker, "bytes": before - len(result.encode())})
    if result.count(ORPHANED_DERIVES) != 1:
        raise ValueError("unexpected orchard derive sequence")
    result = result.replace(ORPHANED_DERIVES, "", 1)
    duplicate_yamo_derive = (
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
    )
    if result.count(duplicate_yamo_derive) != 1:
        raise ValueError("unexpected opening-policy derive sequence")
    result = result.replace(
        duplicate_yamo_derive,
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]",
        1,
    )

    exact_select_impl = yamo_impl.replace(
        "let mut candidate_groups = Vec::new();",
        "let mut candidates_by_id = BTreeMap::new();",
    ).replace(
        "candidate_groups.push(candidates);",
        "candidates_by_id.insert(unit.id, candidates);",
    ).replace(
        "candidate_groups, &view.inventories[0]",
        "candidates_by_id, &view.inventories[0]",
    )
    exact_select_bot = BOT_IMPL.replace(
        "let mut candidate_groups = Vec::new();",
        "let mut candidates_by_id = BTreeMap::new();",
    ).replace(
        "candidate_groups.push(candidates);",
        "candidates_by_id.insert(unit.id, candidates);",
    ).replace(
        "candidate_groups, &view.inventories[0]",
        "candidates_by_id, &view.inventories[0]",
    )
    replacements = (
        ("pub struct YamoBot", YAMO_STRUCT),
        ("impl YamoBot", exact_select_impl),
        ("impl Bot for YamoBot", exact_select_bot),
    )
    for marker, replacement in replacements:
        before = len(result.encode())
        result = _replace_item(result, marker, replacement)
        removals.append(
            {
                "marker": marker,
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(replacement.encode()),
            }
        )
    before = len(result.encode())
    result = _remove_item(result, "pub fn item_index(self)")
    removals.append(
        {"marker": "pub fn item_index(self)", "bytes": before - len(result.encode())}
    )
    fragments = (
        (
            "effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,",
            "effective_cooldown,item_index,training_cost,tree_health,TOTAL_TURNS,",
        ),
        (
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,};",
            "Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,WOOD,};",
        ),
        ("use crate::bot::moisan::SecureOrchardBot;", "use crate::bot::moisan::YamoBot;"),
        ("let mut bot=SecureOrchardBot::new();", "let mut bot=YamoBot::new();"),
    )
    for old, new in fragments:
        if result.count(old) != 1:
            raise ValueError(f"expected one {old!r}")
        result = result.replace(old, new, 1)
    manifest = {
        "schema": "troll-farm-e7a-development-ablation/1",
        "arm": arm,
        "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        "baseline_sha256": BASELINE_SHA256,
        "candidate_bytes": len(result.encode()),
        "candidate_sha256": sha256_bytes(result.encode()),
        "logical_change": logical_change,
        "removed_or_replaced_items": removals,
        "identifier_renaming": False,
        "minification": False,
    }
    return result, manifest


def focused_yamo_partial_wood(source: str) -> tuple[str, dict]:
    """Let partial wood carriers keep chopping until full, adjacent, or late."""

    old_wood = """                if unit.carry[WOOD] > 0 {
                    return MoisanBot::bank_candidates(view, unit);
                }
"""
    new_wood = """                if unit.carry[WOOD] > 0
                    && (unit.free_capacity() == 0
                        || ortho_neighbors(view.shacks[0]).contains(&unit.cell)
                        || view.turn > 250)
                {
                    return MoisanBot::bank_candidates(view, unit);
                }
"""
    if YAMO_IMPL.count(old_wood) != 1:
        raise ValueError("unexpected partial-wood banking block")
    if YAMO_IMPL.count("if unit.total_carried() > 0 {") != 1:
        raise ValueError("unexpected mixed-cargo banking block")
    implementation = YAMO_IMPL.replace(old_wood, new_wood, 1).replace(
        "if unit.total_carried() > 0 {",
        "if unit.total_carried() > unit.carry[WOOD] {",
        1,
    )
    return focused_yamo_exact_moisan(
        source,
        yamo_impl=implementation,
        arm="FOCUSED_YAMO_PARTIAL_WOOD_EXACT_MOISAN",
        logical_change=(
            "retain the focused Yamo and exact Moisan core, but bank partial wood only "
            "when full, adjacent to home, or after turn 250"
        ),
    )


def focused_yamo_all_training_profiles(source: str) -> tuple[str, dict]:
    """Restore the full 27-profile opening search without the general policy layer."""

    old_choices = """                let choices = [
                    (2, 2, 2),
                    (2, 2, 3),
                    (1, 2, 1),
                    (3, 2, 2),
                    (2, 3, 2),
                    (1, 2, 2),
                    (2, 1, 2),
                ];
"""
    new_choices = """                let mut choices = Vec::new();
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            choices.push((movement_speed, carry_capacity, chop_power));
                        }
                    }
                }
"""
    if YAMO_IMPL.count(old_choices) != 1:
        raise ValueError("unexpected reduced training-profile block")
    implementation = YAMO_IMPL.replace(old_choices, new_choices, 1)
    return focused_yamo_exact_moisan(
        source,
        yamo_impl=implementation,
        arm="FOCUSED_YAMO_ALL_TRAINING_PROFILES_EXACT_MOISAN",
        logical_change=(
            "retain the focused Yamo and exact Moisan core while restoring the complete "
            "27-profile opening search"
        ),
    )


def focused_yamo_stable_move_guard(source: str) -> tuple[str, dict]:
    """Replace the general priority router with the two-worker liveness guard."""

    result, manifest = focused_yamo_exact_moisan(source)
    changes = manifest["removed_or_replaced_items"]
    before = len(result.encode())
    result = _replace_item(
        result,
        "fn resolve_move_conflicts(",
        TWO_WORKER_MOVE_GUARD,
    )
    changes.append(
        {
            "marker": "fn resolve_move_conflicts(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(TWO_WORKER_MOVE_GUARD.encode()),
        }
    )
    for marker in (
        "fn resolve_move_conflicts_with_priority(",
        "fn resolve_move_conflicts_with_priority_and_forbidden(",
    ):
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_STABLE_MOVE_GUARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain focused Yamo and exact Moisan economics, but replace the general "
                "priority movement router with the readable two-worker liveness guard"
            ),
        }
    )
    return result, manifest


def focused_yamo_fixed_carrying_chopper(source: str) -> tuple[str, dict]:
    """Replace the expensive opening search with the modal carrying chopper."""

    result, manifest = focused_yamo_exact_moisan(source)
    replacement = r"""fn choose_second_troll(_view: &GameState) -> Stats {
                Stats {
                    movement_speed: 2,
                    carry_capacity: 2,
                    harvest_power: 0,
                    chop_power: 2,
                }
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn choose_second_troll(", replacement)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn choose_second_troll(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(replacement.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_FIXED_CARRYING_CHOPPER",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain focused Yamo and exact Moisan behavior while replacing the map-wide "
                "opening-profile search with a fixed movement-2 carry-2 chop-2 worker"
            ),
            "evidence_boundary": "development arm; size eligibility does not imply qualification",
        }
    )
    return result, manifest


def focused_yamo_no_forced_current_chop(source: str) -> tuple[str, dict]:
    """Remove the simplified scheduler's unconditional current-tree commitment."""

    forced = """                if let Some(mut current) = chops
                    .iter()
                    .find(|candidate| candidate.command == format!("CHOP {}", unit.id))
                    .cloned()
                {
                    current.score = 10_000.0;
                    out.push(current);
                    return out;
                }
"""
    if YAMO_IMPL.count(forced) != 1:
        raise ValueError("unexpected forced-current-chop block")
    implementation = YAMO_IMPL.replace(forced, "", 1)
    return focused_yamo_exact_moisan(
        source,
        yamo_impl=implementation,
        arm="FOCUSED_YAMO_NO_FORCED_CURRENT_CHOP",
        logical_change=(
            "retain focused Yamo and exact Moisan behavior but remove the unconditional "
            "10,000-point commitment to whichever tree a worker currently occupies"
        ),
    )


def focused_yamo_exact_endgame_threshold(source: str) -> tuple[str, dict]:
    """Use the parent's score-aware endgame boundary after removing forced chops."""

    result, manifest = focused_yamo_no_forced_current_chop(source)
    replacements = (
        (
            "if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2) {",
            "if !Self::endgame(view) {",
        ),
        (
            "if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2 {",
            "if Self::endgame(view) {",
        ),
        (
            "fn endgame_candidates(",
            "fn endgame(view: &GameState) -> bool {\n"
            "                view.turn > 250 || (view.plants.len() <= 4\n"
            "                    && score(&view.inventories[0]) < score(&view.inventories[1]))\n"
            "            }\n\n"
            "            fn endgame_candidates(",
        ),
        (
            "effective_cooldown,item_index,training_cost,tree_health,TOTAL_TURNS,",
            "effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,",
        ),
    )
    for old, new in replacements:
        if result.count(old) != 1:
            raise ValueError(f"expected one endgame-threshold fragment {old!r}")
        result = result.replace(old, new, 1)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_EXACT_ENDGAME_THRESHOLD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "remove forced current-tree commitment and use the parent's score-aware "
                "endgame boundary: after turn 250, or at four trees while behind"
            ),
        }
    )
    return result, manifest


def focused_yamo_exact_opening(source: str) -> tuple[str, dict]:
    """Restore the exact tuned opening while retaining the focused late scheduler."""

    result, manifest = focused_yamo_no_forced_current_chop(source)
    policy = item_text(source, "pub struct YamoOpeningPolicy") + item_text(
        source, "impl YamoOpeningPolicy"
    )
    objective = (
        "#[derive(Clone,Copy,Debug,Eq,PartialEq)]"
        + item_text(source, "struct OpeningObjective")
    )
    yamo_struct = r"""pub struct YamoBot {
            type_to_cut: Option<PlantKind>,
            desired_second: Option<OpeningObjective>,
            opening_initialized: bool,
            opening_abandoned: bool,
            opening_policy: YamoOpeningPolicy,
        }"""
    focused = YAMO_IMPL.replace(
        """                if let Some(mut current) = chops
                    .iter()
                    .find(|candidate| candidate.command == format!("CHOP {}", unit.id))
                    .cloned()
                {
                    current.score = 10_000.0;
                    out.push(current);
                    return out;
                }
""",
        "",
        1,
    )
    opening_methods = "".join(
        item_text(source, marker)
        for marker in (
            "fn ensure_opening",
            "fn collection_eta",
            "fn opening_objective",
            "fn opening_key",
            "fn opening_options",
            "fn choose_second_troll",
            "fn training_affordable",
            "fn strongest_affordable",
            "fn enforce_training_deadline",
            "fn fallback_second_troll",
        )
    )
    yamo_impl = (
        "impl YamoBot{pub fn new()->Self{Self{type_to_cut:None,desired_second:None,"
        "opening_initialized:false,opening_abandoned:false,"
        "opening_policy:YamoOpeningPolicy::TUNED_CARRY,}}"
        + opening_methods
        + item_text(focused, "fn fruit_kind")
        + item_text(focused, "fn endgame_candidates")
        + "}"
    )
    bot_impl = BOT_IMPL.replace(
        """                if view.turn >= 35
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
""",
        """                self.enforce_training_deadline(view);
                let desired = self.desired_second
                    .map(|objective| objective.stats)
                    .unwrap_or_else(Self::fallback_second_troll);
                let train_now = !self.opening_abandoned
                    && MoisanBot::can_train(view, desired);
""",
        1,
    ).replace(
        "let early = units.len() < 2 && !train_now;",
        "let early = !self.opening_abandoned && units.len() < 2 && !train_now;",
        1,
    ).replace(
        "let mut candidate_groups = Vec::new();",
        "let mut candidates_by_id = BTreeMap::new();",
    ).replace(
        "candidate_groups.push(candidates);",
        "candidates_by_id.insert(unit.id, candidates);",
    ).replace(
        "candidate_groups, &view.inventories[0]",
        "candidates_by_id, &view.inventories[0]",
    )
    insertion = policy + objective
    if result.count("pub struct YamoBot") != 1:
        raise ValueError("unexpected focused Yamo struct count")
    result = result.replace("pub struct YamoBot", insertion + "pub struct YamoBot", 1)
    result = _replace_item(result, "pub struct YamoBot", yamo_struct)
    result = _replace_item(result, "impl YamoBot", yamo_impl)
    result = _replace_item(result, "impl Bot for YamoBot", bot_impl)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_EXACT_OPENING",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "remove forced current-tree commitment and restore the exact tuned-carry "
                "opening objective, 27-profile search, and turn-35 affordable fallback"
            ),
            "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        }
    )
    return result, manifest


def focused_yamo_affordable_deadline(source: str) -> tuple[str, dict]:
    """At turn 35 train the strongest affordable profile instead of fixed 1/1/0/1."""

    result, manifest = focused_yamo_no_forced_current_chop(source)
    helper = r"""fn strongest_affordable(view: &GameState) -> Option<Stats> {
                let mut best = None;
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            if MoisanBot::can_train(view, stats)
                                && best.map_or(true, |old: Stats| {
                                    (movement_speed + carry_capacity + chop_power,
                                        chop_power, carry_capacity, movement_speed)
                                        > (old.movement_speed + old.carry_capacity
                                            + old.chop_power, old.chop_power,
                                            old.carry_capacity, old.movement_speed)
                                })
                            {
                                best = Some(stats);
                            }
                        }
                    }
                }
                best
            }

            """
    if result.count("fn fruit_kind(") != 1:
        raise ValueError("unexpected focused fruit-kind marker")
    result = result.replace("fn fruit_kind(", helper + "fn fruit_kind(", 1)
    old_deadline = """                if view.turn >= 35
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
"""
    new_deadline = """                if view.turn >= 35
                    && self.desired_second
                        .is_some_and(|stats| !MoisanBot::can_train(view, stats))
                {
                    if let Some(affordable) = Self::strongest_affordable(view) {
                        self.desired_second = Some(affordable);
                    }
                }
"""
    if result.count(old_deadline) != 1:
        raise ValueError("unexpected fixed deadline fallback")
    result = result.replace(old_deadline, new_deadline, 1)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_AFFORDABLE_DEADLINE",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "remove forced current-tree commitment and replace the fixed turn-35 "
                "1/1/0/1 fallback with a full strongest-affordable profile search"
            ),
        }
    )
    return result, manifest


def focused_yamo_specialized_exact_initial(source: str) -> tuple[str, dict]:
    """Specialize the exact tuned opening decision into one readable method."""

    result, manifest = focused_yamo_no_forced_current_chop(source)
    chooser = r"""fn choose_second_troll(view: &GameState) -> Stats {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let collection_eta = |item, kind: Option<PlantKind>, missing: i32| {
                    if missing <= 0 {
                        return 0;
                    }
                    if item == IRON {
                        return view.iron
                            .iter()
                            .flat_map(|iron| ortho_neighbors(*iron))
                            .filter_map(|cell| distance.get(&cell).copied())
                            .min()
                            .map_or(10_000, |travel| missing * (2 * travel + 2));
                    }
                    view.plants
                        .iter()
                        .filter(|plant| Some(plant.kind) == kind && plant.health > 0)
                        .filter_map(|plant| {
                            let travel = distance.get(&plant.cell).copied()?;
                            let wait = (MoisanBot::ticks_until_fruit(view, plant)
                                - travel).max(0);
                            Some(missing * (2 * travel + 2) + wait)
                        })
                        .min()
                        .unwrap_or(10_000)
                };
                let mut options = Vec::new();
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            let cost = training_cost(1, stats.tuple());
                            let mut eta = collection_eta(
                                PLUM,
                                Some(PlantKind::Plum),
                                (cost[PLUM] - view.inventories[0][PLUM]).max(0),
                            ) + collection_eta(
                                LEMON,
                                Some(PlantKind::Lemon),
                                (cost[LEMON] - view.inventories[0][LEMON]).max(0),
                            );
                            if !view.iron.is_empty() {
                                eta += collection_eta(
                                    IRON,
                                    None,
                                    (cost[IRON] - view.inventories[0][IRON]).max(0),
                                );
                            }
                            options.push((stats, eta));
                        }
                    }
                }
                let key = |(stats, eta): &(Stats, i32)| {
                    (stats.movement_speed + stats.carry_capacity + stats.chop_power,
                        -*eta, stats.chop_power, stats.carry_capacity, stats.movement_speed)
                };
                let baseline = options
                    .iter()
                    .filter(|(_, eta)| *eta <= 15)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(options[0]);
                if baseline.0.carry_capacity >= 2 {
                    return baseline.0;
                }
                let allowed_eta = (baseline.1 + 15).min(34);
                options
                    .iter()
                    .filter(|(stats, eta)| stats.carry_capacity >= 2 && *eta <= allowed_eta)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(baseline)
                    .0
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn choose_second_troll(", chooser)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn choose_second_troll(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(chooser.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_SPECIALIZED_EXACT_INITIAL",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "remove forced current-tree commitment and specialize the exact tuned-carry "
                "initial objective into one policy-free method"
            ),
        }
    )
    return result, manifest


def focused_yamo_empty_priority_router(source: str) -> tuple[str, dict]:
    """Specialize the exact movement router for its always-empty priority sets."""

    result, manifest = focused_yamo_specialized_exact_initial(source)
    router = item_text(source, "fn resolve_move_conflicts_with_priority_and_forbidden(")
    transforms = (
        (
            "fn resolve_move_conflicts_with_priority_and_forbidden(view:&GameState,"
            "commands:&mut[String],priority_ids:&BTreeSet<i32>,"
            "forbidden_for_non_priority:&BTreeSet<Cell>,)",
            "fn resolve_move_conflicts(view:&GameState,commands:&mut[String])",
        ),
        (
            "movers.sort_by(|a,b|{let a_priority=priority_ids.contains(&a.0);"
            "let b_priority=priority_ids.contains(&b.0);b_priority.cmp(&a_priority)"
            ".then_with(||b.0.cmp(&a.0))});",
            "movers.sort_by(|a,b|b.0.cmp(&a.0));",
        ),
        (
            "let landing_forbidden=!priority_ids.contains(&id)&&"
            "forbidden_for_non_priority.contains(&landing);"
            "if!landing_forbidden&&!reserved.contains(&landing)",
            "if!reserved.contains(&landing)",
        ),
        (
            ".filter(|cell|{priority_ids.contains(&id)||"
            "!forbidden_for_non_priority.contains(cell)})",
            "",
        ),
    )
    for old, new in transforms:
        if router.count(old) != 1:
            raise ValueError(f"unexpected exact-router fragment {old!r}")
        router = router.replace(old, new, 1)
    if "priority_ids" in router or "forbidden_for_non_priority" in router:
        raise ValueError("priority configuration survived specialized router")
    changes = manifest["removed_or_replaced_items"]
    before = len(result.encode())
    result = _replace_item(result, "fn resolve_move_conflicts(", router)
    changes.append(
        {
            "marker": "fn resolve_move_conflicts(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(router.encode()),
        }
    )
    for marker in (
        "fn resolve_move_conflicts_with_priority(",
        "fn resolve_move_conflicts_with_priority_and_forbidden(",
    ):
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_EMPTY_PRIORITY_ROUTER",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the specialized exact initial selector and exact empty-priority "
                "movement semantics while deleting unused priority/forbidden routing"
            ),
        }
    )
    return result, manifest


def focused_yamo_two_worker_live_state(source: str) -> tuple[str, dict]:
    """Delete unreachable N-worker selection and unused mirrored protocol state."""

    result, manifest = focused_yamo_empty_priority_router(source)
    selector = item_text(source, "fn select(")
    fallback = (
        "let mut used_targets=Vec::new();let mut used_stock=[0;6];"
        "let mut commands=Vec::new();for id in ids{let mut candidates="
        "candidates_by_id[&id].clone();candidates.sort_by(|a,b|b.score.total_cmp(&a.score));"
        "let best=candidates.into_iter().find(|candidate|{used_targets.iter().all(|target|"
        "Self::compatible(candidate.target,*target))&&Self::picked_item(&candidate.command)"
        ".map(|item|used_stock[item]<inventory[item]).unwrap_or(true)}).unwrap_or_else"
        "(Self::wait);used_targets.push(best.target);if let Some(item)=Self::picked_item"
        "(&best.command){used_stock[item]+=1;}commands.push(best.command);}commands"
    )
    if selector.count(fallback) != 1:
        raise ValueError("unexpected general N-worker selector fallback")
    selector = selector.replace(fallback, "Vec::new()", 1)
    changes = manifest["removed_or_replaced_items"]
    before = len(result.encode())
    result = _replace_item(result, "fn select(", selector)
    changes.append(
        {
            "marker": "fn select(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(selector.encode()),
        }
    )
    if result.count("Self::carrying_any(unit)") != 1:
        raise ValueError("unexpected carrying helper call")
    result = result.replace("Self::carrying_any(unit)", "unit.total_carried()>0", 1)
    for marker in ("fn carry_total(", "fn carrying_any("):
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})
    redundant_early = (
        "if item==APPLE&&cost[item]<=view.inventories[0][item]{continue;}"
        "if item!=APPLE&&cost[item]<=view.inventories[0][item]{continue;}"
    )
    simple_early = "if cost[item]<=view.inventories[0][item]{continue;}"
    if result.count(redundant_early) != 1:
        raise ValueError("unexpected duplicated early-resource affordability check")
    result = result.replace(redundant_early, simple_early, 1)
    changes.append(
        {
            "marker": "duplicated early-resource affordability check",
            "bytes": len(redundant_early.encode()) - len(simple_early.encode()),
        }
    )
    score_mirror = "scores:[score(&inventories[0]),score(&inventories[1])],"
    if result.count(score_mirror) != 1 or result.count("use super::rules::score;") != 1:
        raise ValueError("unexpected protocol score mirror")
    result = result.replace(score_mirror, "scores:[0;2],", 1)
    result = result.replace("use super::rules::score;", "", 1)
    for marker in ("pub const WOOD_POINTS", "pub fn score("):
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})
    changes.append(
        {
            "marker": "unused protocol score computation",
            "bytes": len(score_mirror.encode()) - len("scores:[0;2],".encode()) + 24,
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_TWO_WORKER_LIVE_STATE",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain specialized exact opening/movement behavior while deleting the "
                "unreachable N-worker selector fallback, redundant carry/affordability "
                "wrappers, and an unused protocol score computation"
            ),
        }
    )
    return result, manifest


def focused_yamo_live_trait_pruning(source: str) -> tuple[str, dict]:
    """Remove unused trait scaffolding and the impossible doorless-shack fallback."""

    result, manifest = focused_yamo_two_worker_live_state(source)
    changes = manifest["removed_or_replaced_items"]
    derive_fragments = (
        (
            "#[derive(Clone,Copy,Debug,Eq,PartialEq,Ord,PartialOrd,Hash)]"
            "pub enum PlantKind",
            "#[derive(Clone,Copy,PartialEq)]pub enum PlantKind",
        ),
        (
            "#[derive(Clone,Copy,Debug,Eq,PartialEq)]pub struct Stats",
            "#[derive(Clone,Copy)]pub struct Stats",
        ),
        ("#[derive(Clone,Debug,Eq,PartialEq)]pub struct Unit", "pub struct Unit"),
        ("#[derive(Clone,Debug,Eq,PartialEq)]pub struct Plant", "pub struct Plant"),
        (
            "#[derive(Clone,Debug,Eq,PartialEq)]pub struct GameState",
            "pub struct GameState",
        ),
        ("#[derive(Clone,Debug)]pub struct StaticMap", "pub struct StaticMap"),
        (
            "#[derive(Clone,Copy,Debug,Eq,PartialEq,Ord,PartialOrd)]enum Target",
            "#[derive(Clone,Copy,PartialEq)]enum Target",
        ),
        ("#[derive(Clone,Debug)]struct Candidate", "struct Candidate"),
        (
            "#[derive(Clone,Copy,Debug,Eq,PartialEq)]pub struct YamoBot",
            "pub struct YamoBot",
        ),
        ("#[derive(Clone,Copy)]struct PredictedTree", "struct PredictedTree"),
    )
    for old, new in derive_fragments:
        if result.count(old) != 1:
            raise ValueError(f"unexpected unused-derive fragment {old!r}")
        result = result.replace(old, new, 1)
        changes.append({"marker": old, "bytes": len(old.encode()) - len(new.encode())})
    doorless_fallback = (
        "if out.is_empty(){out.push(Candidate{command:format!(\"MOVE {} {} {}\","
        "unit.id,view.shacks[0].0,view.shacks[0].1),score:7_000.0,"
        "target:Target::Shack,});}"
    )
    if result.count(doorless_fallback) != 1 or result.count("Target::Shack") != 1:
        raise ValueError("unexpected doorless-shack fallback")
    if result.count("None,Shack,Bank") != 1:
        raise ValueError("unexpected Target::Shack variant")
    result = result.replace(doorless_fallback, "", 1).replace(
        "None,Shack,Bank", "None,Bank", 1
    )
    changes.append(
        {
            "marker": "doorless-shack banking fallback and Target::Shack",
            "bytes": len(doorless_fallback.encode()) + len("Shack,".encode()),
        }
    )
    if result.count("pub type Stock=[i32;ITEM_COUNT];") != 1:
        raise ValueError("unexpected Stock item-count alias")
    result = result.replace("pub type Stock=[i32;ITEM_COUNT];", "pub type Stock=[i32;6];", 1)
    before = len(result.encode())
    result = _remove_item(result, "pub const ITEM_COUNT")
    changes.append(
        {
            "marker": "pub const ITEM_COUNT and its sole Stock alias",
            "bytes": before - len(result.encode()) + 8,
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_LIVE_TRAIT_PRUNING",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the specialized exact two-worker behavior while deleting unused "
                "Clone/Debug/Eq/Ord/Hash implementations, an unused item-count constant, "
                "and the unreachable no-door shack fallback"
            ),
            "evidence_boundary": (
                "development arm; size eligibility does not imply value qualification"
            ),
        }
    )
    return result, manifest


def focused_yamo_precomputed_opening_eta(source: str) -> tuple[str, dict]:
    """Precompute the exact three resource ETA curves before profile enumeration."""

    result, manifest = focused_yamo_live_trait_pruning(source)
    chooser = r"""fn choose_second_troll(view: &GameState) -> Stats {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let resource_eta = |item: usize, kind: Option<PlantKind>| {
                    let mut values = [0; 3];
                    for level in 1_i32..=3 {
                        let missing = (1 + level * level - view.inventories[0][item]).max(0);
                        if missing == 0 {
                            continue;
                        }
                        values[(level - 1) as usize] = if item == IRON {
                            view.iron
                                .iter()
                                .flat_map(|iron| ortho_neighbors(*iron))
                                .filter_map(|cell| distance.get(&cell).copied())
                                .min()
                                .map_or(10_000, |travel| missing * (2 * travel + 2))
                        } else {
                            view.plants
                                .iter()
                                .filter(|plant| Some(plant.kind) == kind && plant.health > 0)
                                .filter_map(|plant| {
                                    let travel = distance.get(&plant.cell).copied()?;
                                    let wait = (MoisanBot::ticks_until_fruit(view, plant)
                                        - travel).max(0);
                                    Some(missing * (2 * travel + 2) + wait)
                                })
                                .min()
                                .unwrap_or(10_000)
                        };
                    }
                    values
                };
                let plum_eta = resource_eta(PLUM, Some(PlantKind::Plum));
                let lemon_eta = resource_eta(LEMON, Some(PlantKind::Lemon));
                let iron_eta = if view.iron.is_empty() {
                    [0; 3]
                } else {
                    resource_eta(IRON, None)
                };
                let mut options = Vec::new();
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            let eta = plum_eta[(movement_speed - 1) as usize]
                                + lemon_eta[(carry_capacity - 1) as usize]
                                + iron_eta[(chop_power - 1) as usize];
                            options.push((stats, eta));
                        }
                    }
                }
                let key = |(stats, eta): &(Stats, i32)| {
                    (stats.movement_speed + stats.carry_capacity + stats.chop_power,
                        -*eta, stats.chop_power, stats.carry_capacity, stats.movement_speed)
                };
                let baseline = options
                    .iter()
                    .filter(|(_, eta)| *eta <= 15)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(options[0]);
                if baseline.0.carry_capacity >= 2 {
                    return baseline.0;
                }
                let allowed_eta = (baseline.1 + 15).min(34);
                options
                    .iter()
                    .filter(|(stats, eta)| stats.carry_capacity >= 2 && *eta <= allowed_eta)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(baseline)
                    .0
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn choose_second_troll(", chooser)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn choose_second_troll(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(chooser.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_PRECOMPUTED_OPENING_ETA",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain exact tuned opening decisions but compute each level's plum, lemon, "
                "and iron ETA once before enumerating the 27 worker profiles"
            ),
            "evidence_boundary": (
                "development arm; size eligibility does not imply value qualification"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_wait_fallback(source: str) -> tuple[str, dict]:
    """Make the two-worker pair selector total by allowing one carrier to wait."""

    result, manifest = focused_yamo_live_trait_pruning(source)
    bank = item_text(result, "fn bank_candidates(")
    if bank.count("}).collect();out") != 1:
        raise ValueError("unexpected exact bank-candidate tail")
    replacement = bank.replace(
        "}).collect();out",
        "}).collect();out.push(Self::wait());out",
        1,
    )
    before = len(result.encode())
    result = _replace_item(result, "fn bank_candidates(", replacement)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn bank_candidates(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(replacement.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_WAIT_FALLBACK",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the size-qualified specialized bot and make single-door two-carrier "
                "selection total by offering WAIT beside every bank route"
            ),
            "evidence_boundary": (
                "development arm; size eligibility does not imply value qualification"
            ),
        }
    )
    return result, manifest


def focused_yamo_compact_opening_eta(source: str) -> tuple[str, dict]:
    """Express the exact 27-profile opening choice without general policy scaffolding."""

    result, manifest = focused_yamo_bank_wait_fallback(source)
    chooser = r"""fn choose_second_troll(view: &GameState) -> Stats {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let collection_eta = |level: i32, item: usize, kind: Option<PlantKind>| {
                    let missing = (1 + level * level - view.inventories[0][item]).max(0);
                    if missing == 0 {
                        return 0;
                    }
                    if let Some(kind) = kind {
                        return view.plants.iter()
                            .filter(|plant| plant.kind == kind && plant.health > 0)
                            .filter_map(|plant| {
                                let travel = distance.get(&plant.cell).copied()?;
                                let wait = (MoisanBot::ticks_until_fruit(view, plant) - travel)
                                    .max(0);
                                Some(missing * (2 * travel + 2) + wait)
                            })
                            .min()
                            .unwrap_or(10_000);
                    }
                    view.iron.iter()
                        .flat_map(|iron| ortho_neighbors(*iron))
                        .filter_map(|cell| distance.get(&cell).copied())
                        .min()
                        .map_or(10_000, |travel| missing * (2 * travel + 2))
                };
                let mut options = Vec::new();
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            let eta = collection_eta(
                                movement_speed, PLUM, Some(PlantKind::Plum),
                            ) + collection_eta(
                                carry_capacity, LEMON, Some(PlantKind::Lemon),
                            ) + if view.iron.is_empty() {
                                0
                            } else {
                                collection_eta(chop_power, IRON, None)
                            };
                            options.push((stats, eta));
                        }
                    }
                }
                let key = |(stats, eta): &(Stats, i32)| {
                    (stats.movement_speed + stats.carry_capacity + stats.chop_power,
                        -*eta, stats.chop_power, stats.carry_capacity, stats.movement_speed)
                };
                let baseline = options.iter()
                    .filter(|(_, eta)| *eta <= 15)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(options[0]);
                if baseline.0.carry_capacity >= 2 {
                    return baseline.0;
                }
                let allowed_eta = (baseline.1 + 15).min(34);
                options.iter()
                    .filter(|(stats, eta)| stats.carry_capacity >= 2 && *eta <= allowed_eta)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(baseline)
                    .0
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn choose_second_troll(", chooser)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn choose_second_troll(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(chooser.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_COMPACT_OPENING_ETA",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "preserve the exact 27-profile opening choice while deriving each resource "
                "bill directly from the corresponding worker stat"
            ),
            "evidence_boundary": "development refactor; requires exact behavioral parity",
        }
    )
    return result, manifest


def focused_yamo_compact_orchard(source: str) -> tuple[str, dict]:
    """Restore the active orchard sector with a small stateful override."""

    result, manifest = focused_yamo_compact_opening_eta(source)
    old_fields = """            desired_second: Option<Stats>,
        }"""
    new_fields = """            desired_second: Option<Stats>,
            orchard_mother: Option<Cell>,
        }"""
    if result.count(old_fields) != 1:
        raise ValueError("unexpected focused Yamo fields")
    result = result.replace(old_fields, new_fields, 1)
    old_constructor = "Self { type_to_cut: None, desired_second: None }"
    new_constructor = (
        "Self { type_to_cut: None, desired_second: None, "
        "orchard_mother: None }"
    )
    if result.count(old_constructor) != 1:
        raise ValueError("unexpected focused Yamo constructor")
    result = result.replace(old_constructor, new_constructor, 1)
    opening_tail = """                if self.desired_second.is_none() {
                    self.desired_second = Some(Self::choose_second_troll(view));
                }
"""
    orchard_initialization = """                if view.turn == 1 {
                    self.orchard_mother = Self::select_orchard_mother(view);
                }
"""
    if result.count(opening_tail) != 1:
        raise ValueError("unexpected focused opening tail")
    result = result.replace(opening_tail, opening_tail + orchard_initialization, 1)
    methods = r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                if doors.len() < 2 {
                    return None;
                }
                if view.plants.iter().any(|plant| doors.contains(&plant.cell)) {
                    return None;
                }
                let enemy_distance = bfs_distances(
                    &view.walkable,
                    &ortho_neighbors(view.shacks[1]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .collect::<Vec<Cell>>(),
                );
                doors
                    .into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter().any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance.get(door).copied().unwrap_or(10_000) >= 11)
                    .min_by_key(|door| {
                        (-enemy_distance.get(door).copied().unwrap_or(10_000), *door)
                    })
            }

            fn orchard_command(&mut self, view: &GameState) -> Option<String> {
                let mother = self.orchard_mother?;
                if view.units.iter().filter(|unit| unit.player == 0).count() < 2 {
                    return None;
                }
                let starter = view.units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .min_by_key(|unit| unit.id)?;
                if starter.cell != mother {
                    return Some(format!(
                        "MOVE {} {} {}", starter.id, mother.0, mother.1,
                    ));
                }
                if let Some(tree) = view.plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple && plant.health > 0)
                {
                    return Some(if starter.total_carried() > 0 {
                        format!("DROP {}", starter.id)
                    } else if tree.fruits > 0 && starter.free_capacity() > 0 {
                        format!("HARVEST {}", starter.id)
                    } else {
                        "WAIT".to_string()
                    });
                }
                Some(if starter.carry[APPLE] > 0 {
                    format!("PLANT {} APPLE", starter.id)
                } else if starter.total_carried() > 0 {
                    format!("DROP {}", starter.id)
                } else {
                    format!("PICK {} APPLE", starter.id)
                })
            }

            """
    if result.count("fn fruit_kind(") != 1:
        raise ValueError("unexpected fruit-kind insertion point")
    result = result.replace("fn fruit_kind(", methods + "fn fruit_kind(", 1)
    candidate_loop = """                for unit in units {
                    let mut candidates = if view.turn > 250 || !early {
"""
    reserved_starter = """                let orchard_mother = self.orchard_mother;
                let orchard_active = orchard_mother.is_some() && units.len() >= 2;
                for (unit_index, unit) in units.into_iter().enumerate() {
                    let mut candidates = if orchard_active && unit_index == 0
                    {
                        vec![MoisanBot::wait()]
                    } else if view.turn > 250 || !early {
"""
    if result.count(candidate_loop) != 1:
        raise ValueError("unexpected candidate-loop insertion point")
    result = result.replace(candidate_loop, reserved_starter, 1)
    candidate_tail = """                    } else {
                        MoisanBot::early_candidates(view, unit, desired)
                    };
"""
    protection = """                    if orchard_active {
                        if let Some(mother) = orchard_mother {
                            candidates.retain(|candidate| !matches!(candidate.target,
                                Target::Tree(cell) | Target::Bank(cell) | Target::Cell(cell)
                                if cell == mother));
                        }
                    }
"""
    if result.count(candidate_tail) != 1:
        raise ValueError("unexpected candidate-protection insertion point")
    result = result.replace(candidate_tail, candidate_tail + protection, 1)
    resolve = "MoisanBot::resolve_move_conflicts(view, &mut selected);"
    override_command = """if let Some(command) = self.orchard_command(view) {
                    if !selected.is_empty() {
                        selected[0] = command;
                    }
                }
                """
    if result.count(resolve) != 1:
        raise ValueError("unexpected movement-resolution insertion point")
    result = result.replace(resolve, override_command + resolve, 1)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_COMPACT_ORCHARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the size-qualified bank-wait core and restore a compact stateful "
                "apple orchard only in the exact six-map geometry sector"
            ),
            "evidence_boundary": "oversized attribution arm; cannot qualify for Arena",
        }
    )
    return result, manifest


def focused_yamo_direct_chop_forecast(source: str) -> tuple[str, dict]:
    """Price current health/size directly instead of simulating future tree growth."""

    result, manifest = focused_yamo_compact_orchard(source)
    changes = []
    chop_candidates = item_text(result, "fn chop_candidates(")
    prediction = (
        "let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{continue;};"
        "if predicted.size<=0||predicted.health<=0{continue;}"
    )
    direct_health = (
        "if plant.size<=0||plant.health<=0{continue;}"
        "let chop_turns=Self::ceil_div(plant.health,unit.stats.chop_power);"
    )
    outcome = (
        "let Some((chop_turns,final_size))="
        "Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{continue;};"
    )
    if chop_candidates.count(prediction) != 1 or chop_candidates.count(outcome) != 1:
        raise ValueError("unexpected chop forecast call sites")
    chop_candidates = chop_candidates.replace(prediction, direct_health, 1)
    chop_candidates = chop_candidates.replace(outcome, "let final_size=plant.size;", 1)
    before = len(result.encode())
    result = _replace_item(result, "fn chop_candidates(", chop_candidates)
    changes.append(
        {
            "marker": "fn chop_candidates(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(chop_candidates.encode()),
        }
    )
    for marker in (
        "fn predicted_opp_chop(",
        "struct PredictedTree",
        "fn predict_tree(",
        "fn chop_outcome(",
    ):
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})
    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_DIRECT_CHOP_FORECAST",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "delete opponent/growth forecasting and price chop time from the tree's "
                "observed health and size"
            ),
            "evidence_boundary": "oversized consumed-panel ablation; cannot qualify",
        }
    )
    return result, manifest


def focused_yamo_runtime_state_pruning(source: str) -> tuple[str, dict]:
    """Delete parsed state never read by the compact policy and reachable-target routing."""

    result, manifest = focused_yamo_direct_chop_forecast(source)
    replacements = (
        ("pub width:i32,pub height:i32,", "", 2),
        ("pub scores:[i32;2],", "", 1),
        ("pub next_id:i32,", "", 1),
        ("let width=parts.next()?.parse().ok()?;", "let _width:i32=parts.next()?.parse().ok()?;", 1),
        ("Some(parse_static_map(width,height,&rows))", "Some(parse_static_map(&rows))", 1),
        (
            "pub fn parse_static_map(width:i32,height:i32,rows:&[String])->StaticMap",
            "pub fn parse_static_map(rows:&[String])->StaticMap",
            1,
        ),
        ("StaticMap{width,height,walkable,shacks,iron,water,}",
         "StaticMap{walkable,shacks,iron,water,}", 1),
        ("let mut next_id=0;", "", 1),
        ("next_id=next_id.max(values[0]+1);", "", 1),
        (
            "Some(GameState{width:map.width,height:map.height,walkable:map.walkable.clone(),"
            "shacks:map.shacks,inventories,units,plants,scores:[0;2],turn,next_id,"
            "iron:map.iron.clone(),water:map.water.clone(),})",
            "Some(GameState{walkable:map.walkable.clone(),shacks:map.shacks,inventories,"
            "units,plants,turn,iron:map.iron.clone(),water:map.water.clone(),})",
            1,
        ),
    )
    removed = 0
    for old, new, expected in replacements:
        if result.count(old) != expected:
            raise ValueError(f"unexpected unused-state fragment: {old!r}")
        removed += expected * (len(old.encode()) - len(new.encode()))
        result = result.replace(old, new, expected)
    reachable_router = r"""pub fn next_cell(
                walkable: &BTreeSet<Cell>,
                current: Cell,
                target: Cell,
                speed: i32,
            ) -> Cell {
                let from_current = bfs_distances(walkable, &[current]);
                let to_target = bfs_distances(walkable, &[target]);
                from_current.iter()
                    .filter(|(cell, distance)| {
                        **distance <= speed && to_target.contains_key(*cell)
                    })
                    .map(|(cell, _)| *cell)
                    .min_by_key(|cell| (to_target[cell], *cell))
                    .unwrap_or(current)
            }"""
    before = len(result.encode())
    result = _replace_item(result, "pub fn next_cell(", reachable_router)
    manifest["removed_or_replaced_items"].extend(
        [
            {"marker": "unused parsed GameState/StaticMap fields", "bytes": removed},
            {
                "marker": "pub fn next_cell(",
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(reachable_router.encode()),
            },
        ]
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_RUNTIME_STATE_PRUNING",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "discard dimensions, scores and next-id state never read by the policy, and "
                "route only among reachable policy targets"
            ),
            "evidence_boundary": "development refactor; requires behavioral parity",
        }
    )
    return result, manifest


def focused_yamo_collapsed_targets(source: str) -> tuple[str, dict]:
    """Collapse target provenance that is used only as a same-cell mutex."""

    result, manifest = focused_yamo_direct_chop_forecast(source)
    target = "enum Target{None,Cell(Cell),}"
    before = len(result.encode())
    result = _replace_item(result, "enum Target", target)
    target_saving = before - len(result.encode())
    result = result.replace("Target::Bank(", "Target::Cell(")
    result = result.replace("Target::Tree(", "Target::Cell(")
    compatible = (
        "fn compatible(a:Target,b:Target)->bool{"
        "a==Target::None||b==Target::None||a!=b}"
    )
    before = len(result.encode())
    result = _replace_item(result, "fn compatible(", compatible)
    compatible_saving = before - len(result.encode())
    repeated_target_pattern = (
        "Target::Cell(cell) | Target::Cell(cell) | Target::Cell(cell)"
    )
    if result.count(repeated_target_pattern) != 1:
        raise ValueError("unexpected orchard target protection")
    result = result.replace(repeated_target_pattern, "Target::Cell(cell)", 1)
    manifest["removed_or_replaced_items"].extend(
        [
            {
                "marker": "enum Target",
                "net_removed_bytes": target_saving,
                "replacement_bytes": len(target.encode()),
            },
            {
                "marker": "fn compatible(",
                "net_removed_bytes": compatible_saving,
                "replacement_bytes": len(compatible.encode()),
            },
        ]
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_COLLAPSED_TARGETS",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "represent every non-idle assignment target by cell because target kind "
                "never affects scoring or compatibility"
            ),
            "evidence_boundary": "semantic refactor; requires behavioral parity",
        }
    )
    return result, manifest


def focused_yamo_wait_on_conflict(source: str) -> tuple[str, dict]:
    """Delete collision detour search and wait when two chosen moves land together."""

    result, manifest = focused_yamo_collapsed_targets(source)
    resolver = r"""fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                let mut moves: Vec<(i32, usize, Cell, Cell)> = commands.iter()
                    .enumerate()
                    .filter_map(|(index, command)| {
                        let (id, target) = Self::move_command(command)?;
                        let unit = view.unit(id)?;
                        Some((id, index, unit.cell, next_cell(
                            &view.walkable, unit.cell, target, unit.stats.movement_speed,
                        )))
                    })
                    .collect();
                let moving_ids: BTreeSet<i32> = moves.iter()
                    .filter(|(_, _, current, landing)| current != landing)
                    .map(|(id, _, _, _)| *id)
                    .collect();
                let mut reserved: BTreeSet<Cell> = view.units.iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                moves.sort_by(|a, b| b.0.cmp(&a.0));
                for (id, index, current, landing) in moves {
                    if landing == current || !reserved.insert(landing) {
                        commands[index] = "WAIT".to_string();
                    } else {
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                    }
                }
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn resolve_move_conflicts(", resolver)
    manifest["removed_or_replaced_items"].append(
        {
            "marker": "fn resolve_move_conflicts(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(resolver.encode()),
        }
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_WAIT_ON_CONFLICT",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "remove one-step collision detour planning and make conflicting chosen "
                "moves wait in deterministic worker order"
            ),
            "evidence_boundary": "development liveness ablation; cannot qualify alone",
        }
    )
    return result, manifest


def focused_yamo_structural_specialization(source: str) -> tuple[str, dict]:
    """Delete protocol and policy generality impossible in the two-worker controller."""

    result, manifest = focused_yamo_wait_on_conflict(source)
    changes = []

    def replace_item(marker: str, replacement: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _replace_item(result, marker, replacement)
        changes.append(
            {
                "marker": marker,
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(replacement.encode()),
            }
        )

    def remove_item(marker: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})

    # The deployed policy only ever asks for harvest level zero.  Keep parsing the
    # referee's fourteen unit fields, but do not retain or propagate the unused value.
    replace_item(
        "pub struct Stats",
        "pub struct Stats{pub movement_speed:i32,pub carry_capacity:i32,"
        "pub chop_power:i32,}",
    )
    remove_item("impl Stats")
    before_zero_harvest_plumbing = len(result.encode())
    for old, new, expected in (
        ("harvest_power:values[6],", "", 1),
        ("harvest_power: 0,", "", 2),
        ("desired.harvest_power,", "0,", 1),
    ):
        if result.count(old) != expected:
            raise ValueError(f"unexpected zero-harvest fragment: {old!r}")
        result = result.replace(old, new, expected)
    changes.append(
        {
            "marker": "zero-harvest parser and TRAIN plumbing",
            "bytes": before_zero_harvest_plumbing - len(result.encode()),
        }
    )

    # Before worker two exists, n is exactly one and the zero-harvest APPLE bill is
    # already covered by the official starting inventory.  Price only live deficits.
    remove_item("pub fn training_cost(")
    replace_item(
        "fn can_train(",
        r"""fn can_train(view: &GameState, stats: Stats) -> bool {
                if view.units.iter().filter(|unit| unit.player == 0).count() >= 2
                    || TOTAL_TURNS - view.turn <= 20
                {
                    return false;
                }
                let inventory = &view.inventories[0];
                inventory[PLUM] >= 1 + stats.movement_speed * stats.movement_speed
                    && inventory[LEMON] >= 1 + stats.carry_capacity * stats.carry_capacity
                    && (view.iron.is_empty()
                        || inventory[IRON] >= 1 + stats.chop_power * stats.chop_power)
            }""",
    )
    replace_item(
        "fn early_candidates(",
        r"""fn early_candidates(
                view: &GameState,
                unit: &Unit,
                desired: Stats,
            ) -> Vec<Candidate> {
                let mut out = vec![Self::wait()];
                if unit.total_carried() > 0 || unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let needs = [
                    (PLUM, 1 + desired.movement_speed * desired.movement_speed),
                    (LEMON, 1 + desired.carry_capacity * desired.carry_capacity),
                    (IRON, 1 + desired.chop_power * desired.chop_power),
                ];
                for (item, required) in needs {
                    if required <= view.inventories[0][item] {
                        continue;
                    }
                    if item == IRON {
                        out.extend(Self::iron_candidates(view, unit, 6_100.0));
                    } else {
                        let kind = if item == PLUM {
                            PlantKind::Plum
                        } else {
                            PlantKind::Lemon
                        };
                        out.extend(Self::fruit_candidates(view, unit, kind, 6_000.0));
                    }
                }
                if out.len() == 1 {
                    out.extend(Self::chop_candidates(view, unit, None));
                }
                out
            }""",
    )

    # The former loop is an exact arithmetic progression: the current cooldown, then
    # one effective cooldown for every remaining growth step through size four.
    replace_item(
        "fn ticks_until_fruit(",
        r"""fn ticks_until_fruit(view: &GameState, plant: &Plant) -> i32 {
                if plant.fruits > 0 {
                    return 0;
                }
                let near_water = view.water.iter().any(|water| {
                    is_adjacent(*water, plant.cell)
                });
                let reset = match plant.kind {
                    PlantKind::Plum | PlantKind::Lemon => if near_water { 3 } else { 8 },
                    PlantKind::Apple => if near_water { 2 } else { 9 },
                    PlantKind::Banana => if near_water { 4 } else { 6 },
                };
                plant.cooldown.max(1)
                    + reset * (4 - plant.size).max(0)
            }""",
    )
    remove_item("pub fn effective_cooldown(")
    remove_item("pub fn plant_cooldown(")
    remove_item("pub fn water_boost(")
    replace_item(
        "pub fn tree_health(",
        r"""pub fn tree_health(kind: PlantKind, size: i32) -> i32 {
            match kind {
                PlantKind::Plum | PlantKind::Lemon => 4 + 2 * size,
                PlantKind::Apple => 8 + 3 * size,
                PlantKind::Banana => 2 + size,
            }
        }""",
    )
    remove_item("pub fn tree_health_params(")

    # The three-way selector is algebraically identical to one near-tie comparison.
    replace_item(
        "fn focus_type(",
        r"""fn focus_type(view: &GameState) -> PlantKind {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let sum = |kind| view.plants.iter()
                    .filter(|plant| plant.kind == kind)
                    .map(|plant| distance.get(&plant.cell).copied().unwrap_or(10_000))
                    .sum::<i32>();
                if sum(PlantKind::Plum) - sum(PlantKind::Lemon) <= 8 {
                    PlantKind::Plum
                } else {
                    PlantKind::Lemon
                }
            }""",
    )

    for old in ("effective_cooldown,", "training_cost,", "item_index,"):
        if result.count(old) != 1:
            raise ValueError(f"unexpected removed rules import: {old!r}")
        result = result.replace(old, "", 1)
    old_rules_import = "PlantKind,Stock,APPLE,IRON,LEMON,PLUM,WOOD"
    if result.count(old_rules_import) != 1:
        raise ValueError("unexpected rules type import")
    result = result.replace(
        old_rules_import, "PlantKind", 1
    )
    remove_item("pub fn item_index(")
    replace_item(
        "fn picked_item(",
        "fn picked_item(command:&str)->Option<usize>{"
        "let item=command.strip_prefix(\"PICK \")?.split_whitespace().nth(1)?;"
        "match item{\"PLUM\"=>Some(PLUM),\"LEMON\"=>Some(LEMON),"
        "\"APPLE\"=>Some(APPLE),\"BANANA\"=>Some(BANANA),"
        "\"IRON\"=>Some(IRON),\"WOOD\"=>Some(WOOD),_=>None}}",
    )
    replace_item(
        "pub fn parse(",
        "pub fn parse(value:&str)->Option<PlantKind>{match value{"
        "\"PLUM\"=>Some(PlantKind::Plum),\"LEMON\"=>Some(PlantKind::Lemon),"
        "\"APPLE\"=>Some(PlantKind::Apple),\"BANANA\"=>Some(PlantKind::Banana),"
        "_=>None}}",
    )

    # All generated chop targets are reachable from a worker that originated at the
    # home component, so return distance is present.  Remove duplicate feasibility work.
    chop = item_text(result, "fn chop_candidates(")
    chop_replacements = (
        ("if plant.size<=0||plant.health<=0{continue;}",
         "if plant.size<=0{continue;}"),
        (
            "let return_turns=to_shack.get(&plant.cell).map(|d|Self::ceil_div(*d,"
            "unit.stats.movement_speed)).unwrap_or_else(||{Self::ceil_div(manhattan("
            "plant.cell,view.shacks[0]),unit.stats.movement_speed,)});",
            "let return_turns=Self::ceil_div(to_shack[&plant.cell],"
            "unit.stats.movement_speed);",
        ),
        ("let final_size=plant.size;", ""),
        (
            "let turns=(travel_turns+chop_turns+return_turns+1).max(1);",
            "let turns=travel_turns+chop_turns+return_turns+1;",
        ),
        ("let wood=final_size.min(unit.free_capacity());",
         "let wood=plant.size.min(unit.free_capacity());"),
        ("if wood<=0{continue;}", ""),
    )
    for old, new in chop_replacements:
        if chop.count(old) != 1:
            raise ValueError(f"unexpected direct-chop fragment: {old!r}")
        chop = chop.replace(old, new, 1)
    replace_item("fn chop_candidates(", chop)

    # Target provenance is only an optional same-cell mutex in this controller.
    replace_item("enum Target", "type Target=Option<Cell>;")
    target_derive = "#[derive(Clone,Copy,PartialEq)]type Target=Option<Cell>;"
    if result.count(target_derive) != 1:
        raise ValueError("unexpected target derive after optional-target specialization")
    result = result.replace(target_derive, "type Target=Option<Cell>;", 1)
    before_optional_target_sites = len(result.encode())
    result = result.replace("Target::None", "None")
    result = result.replace("Target::Cell(", "Some(")
    changes.append(
        {
            "marker": "optional-cell target use sites",
            "bytes": before_optional_target_sites - len(result.encode()),
        }
    )
    replace_item(
        "fn compatible(",
        "fn compatible(a:Target,b:Target)->bool{a.is_none()||b.is_none()||a!=b}",
    )

    # Vec membership is sufficient for two movers and preserves the same id priority.
    resolver = r"""fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                let mut moves: Vec<(i32, usize, Cell, Cell)> = commands.iter()
                    .enumerate()
                    .filter_map(|(index, command)| {
                        let (id, target) = Self::move_command(command)?;
                        let unit = view.units.iter().find(|unit| unit.id == id)?;
                        Some((id, index, unit.cell, next_cell(
                            &view.walkable, unit.cell, target, unit.stats.movement_speed,
                        )))
                    })
                    .collect();
                let moving_ids: Vec<i32> = moves.iter()
                    .filter(|(_, _, current, landing)| current != landing)
                    .map(|(id, _, _, _)| *id)
                    .collect();
                let mut reserved: Vec<Cell> = view.units.iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                moves.sort_by(|a, b| b.0.cmp(&a.0));
                for (id, index, current, landing) in moves {
                    if landing == current || reserved.contains(&landing) {
                        commands[index] = "WAIT".to_string();
                    } else {
                        reserved.push(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                    }
                }
            }"""
    replace_item("fn resolve_move_conflicts(", resolver)
    remove_item("pub fn unit(")
    old_import = "use std::collections::{BTreeMap,BTreeSet};"
    if result.count(old_import) != 1:
        raise ValueError("unexpected compact-bot collections import")
    result = result.replace(old_import, "use std::collections::BTreeMap;", 1)

    # Dimensions, synthetic scores, and next-id were retained compatibility fields only.
    # The parser still validates every input token and consumes every protocol line.
    before_unused_state = len(result.encode())
    for old, new, expected in (
        ("pub width:i32,pub height:i32,", "", 2),
        ("pub scores:[i32;2],", "", 1),
        ("pub next_id:i32,", "", 1),
        ("let width=parts.next()?.parse().ok()?;",
         "let _width:i32=parts.next()?.parse().ok()?;", 1),
        ("Some(parse_static_map(width,height,&rows))",
         "Some(parse_static_map(&rows))", 1),
        ("pub fn parse_static_map(width:i32,height:i32,rows:&[String])->StaticMap",
         "pub fn parse_static_map(rows:&[String])->StaticMap", 1),
        ("StaticMap{width,height,walkable,shacks,iron,water,}",
         "StaticMap{walkable,shacks,iron,water,}", 1),
        ("let mut next_id=0;", "", 1),
        ("next_id=next_id.max(values[0]+1);", "", 1),
        (
            "Some(GameState{width:map.width,height:map.height,walkable:map.walkable.clone(),"
            "shacks:map.shacks,inventories,units,plants,scores:[0;2],turn,next_id,"
            "iron:map.iron.clone(),water:map.water.clone(),})",
            "Some(GameState{walkable:map.walkable.clone(),shacks:map.shacks,inventories,"
            "units,plants,turn,iron:map.iron.clone(),water:map.water.clone(),})",
            1,
        ),
    ):
        if result.count(old) != expected:
            raise ValueError(f"unexpected unused-state fragment: {old!r}")
        result = result.replace(old, new, expected)
    changes.append(
        {
            "marker": "unused parsed GameState and StaticMap fields",
            "bytes": before_unused_state - len(result.encode()),
        }
    )

    replace_item(
        "pub fn next_cell(",
        r"""pub fn next_cell(
                walkable: &BTreeSet<Cell>,
                current: Cell,
                target: Cell,
                speed: i32,
            ) -> Cell {
                let from_current = bfs_distances(walkable, &[current]);
                let to_target = bfs_distances(walkable, &[target]);
                from_current.iter()
                    .filter(|(cell, distance)| {
                        **distance <= speed && to_target.contains_key(*cell)
                    })
                    .map(|(cell, _)| *cell)
                    .min_by_key(|cell| (to_target[cell], *cell))
                    .unwrap_or(current)
            }""",
    )

    # Protocol delivery always starts at turn one, so initialize all three immutable
    # opening decisions together instead of probing two Option fields every turn.
    replace_item(
        "fn ensure_opening(",
        r"""fn ensure_opening(&mut self, view: &GameState) {
                if view.turn == 1 {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                    self.desired_second = Some(Self::choose_second_troll(view));
                    self.orchard_mother = Self::select_orchard_mother(view);
                }
            }""",
    )

    # Orchard command generation is called only when a mother and both workers exist.
    replace_item(
        "fn orchard_command(",
        r"""fn orchard_command(&self, view: &GameState) -> String {
                let mother = self.orchard_mother.unwrap();
                let starter = view.units.iter()
                    .filter(|unit| unit.player == 0)
                    .min_by_key(|unit| unit.id).unwrap();
                if starter.cell != mother {
                    return format!("MOVE {} {} {}", starter.id, mother.0, mother.1);
                }
                if let Some(tree) = view.plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple && plant.health > 0)
                {
                    return if starter.total_carried() > 0 {
                        format!("DROP {}", starter.id)
                    } else if tree.fruits > 0 && starter.free_capacity() > 0 {
                        format!("HARVEST {}", starter.id)
                    } else {
                        "WAIT".to_string()
                    };
                }
                if starter.carry[APPLE] > 0 {
                    format!("PLANT {} APPLE", starter.id)
                } else if starter.total_carried() > 0 {
                    format!("DROP {}", starter.id)
                } else {
                    format!("PICK {} APPLE", starter.id)
                }
            }""",
    )
    old_override = """if let Some(command) = self.orchard_command(view) {
                    if !selected.is_empty() {
                        selected[0] = command;
                    }
                }
                """
    new_override = """if orchard_active {
                    selected[0] = self.orchard_command(view);
                }
                """
    if result.count(old_override) != 1:
        raise ValueError("unexpected orchard command override")
    result = result.replace(old_override, new_override, 1)

    # Every door was already proved empty before this iterator, and official map doors
    # share one connected component, so the second empty check/fallback is redundant.
    replace_item(
        "fn select_orchard_mother(",
        r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 2
                    || view.plants.iter().any(|plant| doors.contains(&plant.cell))
                {
                    return None;
                }
                let enemy_doors: Vec<Cell> = ortho_neighbors(view.shacks[1]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                let enemy_distance = bfs_distances(&view.walkable, &enemy_doors);
                doors.into_iter()
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance[door] >= 11)
                    .min_by_key(|door| (-enemy_distance[door], *door))
            }""",
    )

    replace_item(
        "fn fruit_kind(",
        r"""fn fruit_kind(stock: &[i32; 6], bank: bool) -> Option<PlantKind> {
                let items = if bank {
                    [BANANA, PLUM, LEMON, APPLE]
                } else {
                    [PLUM, LEMON, APPLE, BANANA]
                };
                items.into_iter()
                    .find(|item| stock[*item] > 0)
                    .map(|item| match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => PlantKind::Banana,
                    })
            }""",
    )

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_STRUCTURAL_SPECIALIZATION",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "specialize protocol state, training bill, growth timing, target mutex, "
                "collision storage and orchard preconditions to the exact two-worker policy"
            ),
            "evidence_boundary": (
                "size candidate; requires exact consumed-panel parity before qualification"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy(source: str) -> tuple[str, dict]:
    """Prioritize the front carrier when both workers share a bank door."""

    result, manifest = focused_yamo_structural_specialization(source)
    changes = []
    old_priority = (
        "7_000.0-Self::ceil_div(dist[&cell],unit.stats.movement_speed)as f64"
    )
    new_priority = "7_000.0-dist[&cell]as f64"
    if result.count(old_priority) != 1:
        raise ValueError("unexpected speed-normalized bank priority")
    before = len(result.encode())
    result = result.replace(old_priority, new_priority, 1)
    changes.append(
        {
            "marker": "bank lane priority",
            "net_removed_bytes": before - len(result.encode()),
            "logical_change": (
                "order same-door carriers by remaining cells so the rear worker cannot "
                "pin the front worker in WAIT"
            ),
        }
    )
    live_size_check = "if plant.size<=0{continue;}"
    if result.count(live_size_check) != 1:
        raise ValueError("unexpected live-tree size check")
    before = len(result.encode())
    result = result.replace(live_size_check, "", 1)
    changes.append(
        {
            "marker": "impossible live-tree size-zero branch",
            "bytes": before - len(result.encode()),
            "logical_change": "protocol plant rows always have size at least one",
        }
    )
    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "replace speed-priority bank contention with a front-to-back wood convoy"
            ),
            "evidence_boundary": (
                "distinct size candidate after terminal rejection; requires a new lock and "
                "new untouched validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_spare_door_orchard(source: str) -> tuple[str, dict]:
    """Allow mixed-door orchards only when a third home door remains available."""

    result, manifest = focused_yamo_bank_convoy(source)
    orchard_mother = r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 2 || doors.len() == 2
                    && view.plants.iter().any(|plant| doors.contains(&plant.cell))
                {
                    return None;
                }
                let enemy_distance = bfs_distances(
                    &view.walkable,
                    &ortho_neighbors(view.shacks[1]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .collect::<Vec<Cell>>(),
                );
                doors.into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance[door] >= 11)
                    .min_by_key(|door| (-enemy_distance[door], *door))
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn select_orchard_mother(", orchard_mother)
    change = {
        "marker": "fn select_orchard_mother(",
        "net_removed_bytes": before - len(result.encode()),
        "replacement_bytes": len(orchard_mother.encode()),
        "logical_change": (
            "preserve all-empty two-door orchards, but require a spare third door when a "
            "natural tree already occupies another home door"
        ),
    }
    manifest["removed_or_replaced_items"].append(change)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_SPARE_DOOR_ORCHARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "prevent same-door convoy deadlock and admit mixed-door orchards only with "
                "a third home door available"
            ),
            "evidence_boundary": (
                "distinct size candidate after terminal rejection; requires a new lock and "
                "new untouched validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_spare_door_safe_select(
    source: str,
) -> tuple[str, dict]:
    """Emit one action per worker when a reserved orchard cell empties a candidate set."""

    result, manifest = focused_yamo_bank_convoy_spare_door_orchard(source)
    changes = []

    selector = item_text(result, "fn select(")
    empty_pair = "}Vec::new()}"
    wait_pair = "}vec![\"WAIT\".to_string();2]}"
    if selector.count(empty_pair) != 1:
        raise ValueError("unexpected empty two-worker selector fallback")
    before = len(result.encode())
    selector = selector.replace(empty_pair, wait_pair, 1)
    result = _replace_item(result, "fn select(", selector)
    changes.append(
        {
            "marker": "empty two-worker selector fallback",
            "net_removed_bytes": before - len(result.encode()),
            "logical_change": (
                "emit an explicit WAIT for each worker when reserved-cell filtering "
                "leaves no compatible pair"
            ),
        }
    )

    redundant_health = "plant.kind == PlantKind::Apple && plant.health > 0"
    live_apple = "plant.kind == PlantKind::Apple"
    if result.count(redundant_health) != 1:
        raise ValueError("unexpected orchard live-tree health predicate")
    before = len(result.encode())
    result = result.replace(redundant_health, live_apple, 1)
    changes.append(
        {
            "marker": "redundant orchard live-tree health predicate",
            "bytes": before - len(result.encode()),
            "logical_change": "protocol plant rows contain only live trees",
        }
    )

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_SPARE_DOOR_SAFE_SELECT",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the bank-convoy and spare-door orchard while making the "
                "two-worker selector total after reserved-cell filtering"
            ),
            "evidence_boundary": (
                "distinct liveness repair; requires a new lock and new untouched "
                "validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_spare_door_period2_guard(
    source: str,
) -> tuple[str, dict]:
    """Stop a third A-B-A landing before collision reservations are finalized."""

    result, manifest = focused_yamo_bank_convoy_spare_door_safe_select(source)
    changes = []

    old_struct = item_text(result, "pub struct YamoBot")
    new_struct = old_struct.replace(
        "orchard_mother: Option<Cell>,",
        "orchard_mother: Option<Cell>,\n"
        "            move_history: [Option<(i32, Cell, Cell)>; 4],",
        1,
    )
    if new_struct == old_struct:
        raise ValueError("unexpected compact YamoBot fields")
    before = len(result.encode())
    result = _replace_item(result, "pub struct YamoBot", new_struct)
    changes.append(
        {
            "marker": "pub struct YamoBot",
            "net_removed_bytes": before - len(result.encode()),
            "logical_change": "remember two consecutive landing cells for each live unit id",
        }
    )

    old_constructor = (
        "Self { type_to_cut: None, desired_second: None, orchard_mother: None }"
    )
    new_constructor = (
        "Self { type_to_cut: None, desired_second: None, orchard_mother: None, "
        "move_history: [None; 4] }"
    )
    if result.count(old_constructor) != 1:
        raise ValueError("unexpected compact YamoBot constructor")
    result = result.replace(old_constructor, new_constructor, 1)

    resolver = r"""fn resolve_move_conflicts(
                view: &GameState,
                commands: &mut [String],
                move_history: &mut [Option<(i32, Cell, Cell)>; 4],
            ) {
                let mut moves: Vec<(i32, usize, Cell, Cell)> = commands.iter()
                    .enumerate()
                    .filter_map(|(index, command)| {
                        let (id, target) = Self::move_command(command)?;
                        let unit = view.units.iter().find(|unit| unit.id == id)?;
                        Some((id, index, unit.cell, next_cell(
                            &view.walkable, unit.cell, target, unit.stats.movement_speed,
                        )))
                    })
                    .collect();
                moves.retain(|(id, index, _, landing)| {
                    let history = &mut move_history[*id as usize];
                    let previous = (*history).filter(|row| row.0 + 1 == view.turn);
                    if previous.is_some_and(|row| row.1 == *landing && row.2 != *landing) {
                        commands[*index] = "WAIT".to_string();
                        *history = None;
                        false
                    } else {
                        *history = Some((
                            view.turn,
                            previous.map_or(*landing, |row| row.2),
                            *landing,
                        ));
                        true
                    }
                });
                let moving_ids: Vec<i32> = moves.iter()
                    .filter(|(_, _, current, landing)| current != landing)
                    .map(|(id, _, _, _)| *id)
                    .collect();
                let mut reserved: Vec<Cell> = view.units.iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                moves.sort_by(|a, b| b.0.cmp(&a.0));
                for (id, index, current, landing) in moves {
                    if landing == current || reserved.contains(&landing) {
                        commands[index] = "WAIT".to_string();
                    } else {
                        reserved.push(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                    }
                }
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn resolve_move_conflicts(", resolver)
    changes.append(
        {
            "marker": "fn resolve_move_conflicts(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(resolver.encode()),
            "logical_change": (
                "turn the third consecutive A-B-A landing into WAIT before reserving "
                "the remaining worker's landing"
            ),
        }
    )

    old_call = "MoisanBot::resolve_move_conflicts(view, &mut selected);"
    new_call = (
        "MoisanBot::resolve_move_conflicts("
        "view, &mut selected, &mut self.move_history);"
    )
    if result.count(old_call) != 1:
        raise ValueError("unexpected compact movement resolver call")
    result = result.replace(old_call, new_call, 1)

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_SPARE_DOOR_PERIOD2_GUARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the safe two-worker selector and break any third consecutive "
                "A-B-A landing before collision resolution"
            ),
            "evidence_boundary": (
                "live-counterexample liveness repair; over-ceiling output is diagnostic "
                "until paired with a declared logical simplification"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_spare_door_slot_period2(
    source: str,
) -> tuple[str, dict]:
    """Break A-B-A landings with two stable action-slot history records."""

    result, manifest = focused_yamo_bank_convoy_spare_door_safe_select(source)
    changes = []

    old_struct = item_text(result, "pub struct YamoBot")
    new_struct = old_struct.replace(
        "orchard_mother: Option<Cell>,",
        "orchard_mother: Option<Cell>,\n"
        "            move_history: [(i32, Cell, Cell); 2],",
        1,
    )
    if new_struct == old_struct:
        raise ValueError("unexpected compact YamoBot fields")
    before = len(result.encode())
    result = _replace_item(result, "pub struct YamoBot", new_struct)
    changes.append(
        {
            "marker": "pub struct YamoBot",
            "net_removed_bytes": before - len(result.encode()),
            "logical_change": "remember the last two consecutive landings in each worker slot",
        }
    )

    old_constructor = (
        "Self { type_to_cut: None, desired_second: None, orchard_mother: None }"
    )
    new_constructor = (
        "Self { type_to_cut: None, desired_second: None, orchard_mother: None, "
        "move_history: [(0, (0, 0), (0, 0)); 2] }"
    )
    if result.count(old_constructor) != 1:
        raise ValueError("unexpected compact YamoBot constructor")
    result = result.replace(old_constructor, new_constructor, 1)

    resolver = item_text(result, "fn resolve_move_conflicts(")
    old_signature = "fn resolve_move_conflicts(view: &GameState, commands: &mut [String])"
    new_signature = (
        "fn resolve_move_conflicts(view: &GameState, commands: &mut [String], "
        "move_history: &mut [(i32, Cell, Cell); 2])"
    )
    if resolver.count(old_signature) != 1:
        raise ValueError("unexpected compact movement resolver signature")
    resolver = resolver.replace(old_signature, new_signature, 1)
    collection_tail = "                    .collect();\n"
    if resolver.count(collection_tail) != 3:
        raise ValueError("unexpected movement resolver collection structure")
    guard = r"""                moves.retain(|(_, index, _, landing)| {
                    let (turn, two_back, previous) = move_history[*index];
                    if turn + 1 == view.turn
                        && two_back == *landing && previous != *landing
                    {
                        commands[*index] = "WAIT".to_string();
                        move_history[*index] = (view.turn, *landing, *landing);
                        false
                    } else {
                        move_history[*index] = (
                            view.turn,
                            if turn + 1 == view.turn { previous } else { *landing },
                            *landing,
                        );
                        true
                    }
                });
"""
    resolver = resolver.replace(collection_tail, collection_tail + guard, 1)
    before = len(result.encode())
    result = _replace_item(result, "fn resolve_move_conflicts(", resolver)
    changes.append(
        {
            "marker": "fn resolve_move_conflicts(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(resolver.encode()),
            "logical_change": "turn the third consecutive A-B-A landing into WAIT",
        }
    )

    old_call = "MoisanBot::resolve_move_conflicts(view, &mut selected);"
    new_call = (
        "MoisanBot::resolve_move_conflicts("
        "view, &mut selected, &mut self.move_history);"
    )
    if result.count(old_call) != 1:
        raise ValueError("unexpected compact movement resolver call")
    result = result.replace(old_call, new_call, 1)

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_SPARE_DOOR_SLOT_PERIOD2",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain exact opening and terminal economics while breaking a third "
                "A-B-A landing in either stable worker action slot"
            ),
            "evidence_boundary": (
                "live-counterexample liveness repair; over-ceiling output is diagnostic "
                "until paired with a declared logical simplification"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_period2_lean_safe(
    source: str,
) -> tuple[str, dict]:
    """Fund the slot liveness guard by removing narrow policy generality."""

    result, manifest = focused_yamo_bank_convoy_spare_door_slot_period2(source)
    changes = []

    orchard_mother = r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 2 || doors.len() == 2
                    && view.plants.iter().any(|plant| doors.contains(&plant.cell))
                {
                    return None;
                }
                doors.into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| manhattan(*door, view.shacks[1]) >= 11)
                    .min_by_key(|door| (-manhattan(*door, view.shacks[1]), *door))
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn select_orchard_mother(", orchard_mother)
    changes.append(
        {
            "marker": "fn select_orchard_mother(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(orchard_mother.encode()),
            "logical_change": (
                "retain the enemy-distance floor but use conservative Manhattan distance "
                "instead of a second BFS"
            ),
        }
    )

    old_evacuation = r"""                    if train_now
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
                                target: Some(cell),
                            });
                        }
                    }
"""
    new_evacuation = r"""                    if train_now && unit.cell == view.shacks[0] {
                        let cell = ortho_neighbors(view.shacks[0]).into_iter()
                            .find(|cell| view.walkable.contains(cell)).unwrap();
                        candidates.push(Candidate {
                            command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                            score: 19_000.0,
                            target: Some(cell),
                        });
                    }
"""
    if result.count(old_evacuation) != 1:
        raise ValueError("unexpected conditional training evacuation block")
    before = len(result.encode())
    result = result.replace(old_evacuation, new_evacuation, 1)
    changes.append(
        {
            "marker": "conditional training evacuation block",
            "bytes": before - len(result.encode()),
            "logical_change": (
                "official shacks always have a walkable door, so always add the same-turn "
                "evacuation move when a funded worker is trained"
            ),
        }
    )

    fruit_kind = r"""fn fruit_kind(stock: &[i32; 6]) -> Option<PlantKind> {
                [BANANA, PLUM, LEMON, APPLE].into_iter()
                    .find(|item| stock[*item] > 0)
                    .map(|item| match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => PlantKind::Banana,
                    })
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn fruit_kind(", fruit_kind)
    for old, new, expected in (
        ("Self::fruit_kind(&unit.carry, false)", "Self::fruit_kind(&unit.carry)", 1),
        ("Self::fruit_kind(&view.inventories[0], true)",
         "Self::fruit_kind(&view.inventories[0])", 1),
    ):
        if result.count(old) != expected:
            raise ValueError(f"unexpected terminal fruit-priority call: {old!r}")
        result = result.replace(old, new, expected)
    changes.append(
        {
            "marker": "fn fruit_kind(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(fruit_kind.encode()),
            "logical_change": "use one banana-first terminal conversion priority",
        }
    )

    for old, new in (
        (
            "if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2)",
            "if view.turn <= 250",
        ),
        (
            "if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2",
            "if view.turn > 250",
        ),
    ):
        if result.count(old) != 1:
            raise ValueError(f"unexpected preterminal conversion condition: {old!r}")
        before = len(result.encode())
        result = result.replace(old, new, 1)
        changes.append(
            {
                "marker": old,
                "bytes": before - len(result.encode()),
                "logical_change": "bank fruit before turn 251 and convert only in the terminal phase",
            }
        )

    occupied_conversion_door = r"""                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
"""
    if result.count(occupied_conversion_door) != 1:
        raise ValueError("unexpected terminal occupied-door prefilter")
    before = len(result.encode())
    result = result.replace(occupied_conversion_door, "", 1)
    changes.append(
        {
            "marker": "terminal occupied-door prefilter",
            "bytes": before - len(result.encode()),
            "logical_change": (
                "delete the redundant prospective occupancy scan; the shared landing "
                "resolver already makes an occupied conversion door wait"
            ),
        }
    )

    redundant_live_health = "if plant.health<=0||!from_unit.contains_key(&plant.cell)"
    reachable_live_tree = "if !from_unit.contains_key(&plant.cell)"
    if result.count(redundant_live_health) != 1:
        raise ValueError("unexpected live-tree chop predicate")
    before = len(result.encode())
    result = result.replace(redundant_live_health, reachable_live_tree, 1)
    changes.append(
        {
            "marker": "redundant live-tree chop health predicate",
            "bytes": before - len(result.encode()),
            "logical_change": "protocol plant rows contain only live trees",
        }
    )

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_PERIOD2_LEAN_SAFE",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "combine the slot period-2 guard with conservative orchard geometry, "
                "unconditional funded-shack evacuation, and one terminal conversion mode"
            ),
            "evidence_boundary": (
                "size-eligible development successor; requires consumed semantic and "
                "value gates before any fresh lock"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_period2_lean_coordination(
    source: str,
) -> tuple[str, dict]:
    """Fund the slot guard by deleting redundant two-worker coordination layers."""

    result, manifest = focused_yamo_bank_convoy_spare_door_slot_period2(source)
    changes = []

    selector = item_text(result, "fn select(")
    stock_guard = "||!Self::stock_compatible(a,b,inventory)"
    if selector.count(stock_guard) != 1:
        raise ValueError("unexpected simultaneous-PICK stock guard")
    before = len(result.encode())
    selector = selector.replace(stock_guard, "", 1)
    result = _replace_item(result, "fn select(", selector)
    stock_guard_bytes = before - len(result.encode())
    for marker in ("fn picked_item(", "fn stock_compatible("):
        item_before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": item_before - len(result.encode())})
    changes.append(
        {
            "marker": "simultaneous-PICK stock guard",
            "bytes": stock_guard_bytes,
            "logical_change": (
                "delete speculative same-item stock reservation; the two workers already "
                "reserve distinct action cells and failed excess PICK is a legal no-op"
            ),
        }
    )

    old_evacuation = r"""                    if train_now
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
                                target: Some(cell),
                            });
                        }
                    }
"""
    new_evacuation = r"""                    if train_now && unit.cell == view.shacks[0] {
                        let cell = ortho_neighbors(view.shacks[0]).into_iter()
                            .find(|cell| view.walkable.contains(cell)).unwrap();
                        candidates.push(Candidate {
                            command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                            score: 19_000.0,
                            target: Some(cell),
                        });
                    }
"""
    if result.count(old_evacuation) != 1:
        raise ValueError("unexpected conditional training evacuation block")
    before = len(result.encode())
    result = result.replace(old_evacuation, new_evacuation, 1)
    changes.append(
        {
            "marker": "conditional training evacuation block",
            "bytes": before - len(result.encode()),
            "logical_change": (
                "official shacks always have a walkable door, so always add the same-turn "
                "evacuation move when a funded worker is trained"
            ),
        }
    )

    occupied_conversion_door = r"""                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
"""
    if result.count(occupied_conversion_door) != 1:
        raise ValueError("unexpected terminal occupied-door prefilter")
    before = len(result.encode())
    result = result.replace(occupied_conversion_door, "", 1)
    changes.append(
        {
            "marker": "terminal occupied-door prefilter",
            "bytes": before - len(result.encode()),
            "logical_change": (
                "delete the redundant prospective occupancy scan; the shared landing "
                "resolver already makes an occupied conversion door wait"
            ),
        }
    )

    redundant_live_health = "if plant.health<=0||!from_unit.contains_key(&plant.cell)"
    reachable_live_tree = "if !from_unit.contains_key(&plant.cell)"
    if result.count(redundant_live_health) != 1:
        raise ValueError("unexpected live-tree chop predicate")
    before = len(result.encode())
    result = result.replace(redundant_live_health, reachable_live_tree, 1)
    changes.append(
        {
            "marker": "redundant live-tree chop health predicate",
            "bytes": before - len(result.encode()),
            "logical_change": "protocol plant rows contain only live trees",
        }
    )

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_PERIOD2_LEAN_COORDINATION",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain exact opening, orchard, and conversion economics while replacing "
                "redundant stock, evacuation, and occupancy coordination with the shared "
                "two-worker landing guard"
            ),
            "evidence_boundary": (
                "size-eligible development successor; requires consumed semantic and "
                "value gates before any fresh lock"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_period2_simple_clock(
    source: str,
) -> tuple[str, dict]:
    """Pair the period-2 guard with travel-only opening and terminal conversion."""

    result, manifest = focused_yamo_bank_convoy_spare_door_period2_guard(source)
    changes = []

    fruit_candidates = item_text(result, "fn fruit_candidates(")
    old_fruit_wait = (
        "let wait=(Self::ticks_until_fruit(view,plant)-travel).max(0);"
        "out.push(Candidate{command:format!(\"MOVE {} {} {}\",unit.id,plant.cell.0,"
        "plant.cell.1),score:base_score-(travel+wait)as f64,target:Some(plant.cell),});"
    )
    new_fruit_wait = (
        "out.push(Candidate{command:format!(\"MOVE {} {} {}\",unit.id,plant.cell.0,"
        "plant.cell.1),score:base_score-travel as f64,target:Some(plant.cell),});"
    )
    if fruit_candidates.count(old_fruit_wait) != 1:
        raise ValueError("unexpected opening fruit wait forecast")
    before = len(result.encode())
    fruit_candidates = fruit_candidates.replace(old_fruit_wait, new_fruit_wait, 1)
    result = _replace_item(result, "fn fruit_candidates(", fruit_candidates)
    changes.append(
        {
            "marker": "opening fruit target growth wait",
            "bytes": before - len(result.encode()),
            "logical_change": "rank bill-fruit sources by reachable travel rather than growth forecast",
        }
    )

    chooser = item_text(result, "fn choose_second_troll(")
    old_eta_wait = (
        "let wait = (MoisanBot::ticks_until_fruit(view, plant) - travel)\n"
        "                                    .max(0);\n"
        "                                Some(missing * (2 * travel + 2) + wait)"
    )
    new_eta_wait = "Some(missing * (2 * travel + 2))"
    if chooser.count(old_eta_wait) != 1:
        raise ValueError("unexpected worker-profile growth wait forecast")
    before = len(result.encode())
    chooser = chooser.replace(old_eta_wait, new_eta_wait, 1)
    result = _replace_item(result, "fn choose_second_troll(", chooser)
    changes.append(
        {
            "marker": "worker-profile growth wait forecast",
            "bytes": before - len(result.encode()),
            "logical_change": "price each bill resource by collection travel only",
        }
    )

    before = len(result.encode())
    result = _remove_item(result, "fn ticks_until_fruit(")
    changes.append(
        {
            "marker": "fn ticks_until_fruit(",
            "bytes": before - len(result.encode()),
            "logical_change": "delete the now-unused species/water growth-clock predictor",
        }
    )

    fruit_kind = r"""fn fruit_kind(stock: &[i32; 6]) -> Option<PlantKind> {
                [BANANA, PLUM, LEMON, APPLE].into_iter()
                    .find(|item| stock[*item] > 0)
                    .map(|item| match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => PlantKind::Banana,
                    })
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn fruit_kind(", fruit_kind)
    for old, new, expected in (
        ("Self::fruit_kind(&unit.carry, false)", "Self::fruit_kind(&unit.carry)", 1),
        ("Self::fruit_kind(&view.inventories[0], true)",
         "Self::fruit_kind(&view.inventories[0])", 1),
    ):
        if result.count(old) != expected:
            raise ValueError(f"unexpected terminal fruit-priority call: {old!r}")
        result = result.replace(old, new, expected)
    changes.append(
        {
            "marker": "fn fruit_kind(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(fruit_kind.encode()),
            "logical_change": "use one banana-first terminal conversion priority",
        }
    )

    for old, new in (
        (
            "if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2)",
            "if view.turn <= 250",
        ),
        (
            "if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2",
            "if view.turn > 250",
        ),
    ):
        if result.count(old) != 1:
            raise ValueError(f"unexpected preterminal conversion condition: {old!r}")
        before = len(result.encode())
        result = result.replace(old, new, 1)
        changes.append(
            {
                "marker": old,
                "bytes": before - len(result.encode()),
                "logical_change": "bank fruit before turn 251 and convert only in the terminal phase",
            }
        )

    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_PERIOD2_SIMPLE_CLOCK",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "combine a total two-worker period-2 guard with travel-only opening "
                "pricing and one terminal fruit-conversion mode"
            ),
            "evidence_boundary": (
                "size-eligible development successor; requires consumed semantic and "
                "value gates before any fresh lock"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_safe_orchard(source: str) -> tuple[str, dict]:
    """Open any eligible mother door, but disable seeding when APPLE is exhausted."""

    result, manifest = focused_yamo_bank_convoy(source)
    changes = []
    orchard_command = r"""fn orchard_command(&mut self, view: &GameState) -> String {
                let mother = self.orchard_mother.unwrap();
                let starter = view.units.iter()
                    .filter(|unit| unit.player == 0)
                    .min_by_key(|unit| unit.id).unwrap();
                if starter.cell != mother {
                    return format!("MOVE {} {} {}", starter.id, mother.0, mother.1);
                }
                let tree = view.plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple);
                if starter.total_carried() > 0 {
                    return if tree.is_none() && starter.carry[APPLE] > 0 {
                        format!("PLANT {} APPLE", starter.id)
                    } else {
                        format!("DROP {}", starter.id)
                    };
                }
                match tree {
                    Some(tree) if tree.fruits > 0 => format!("HARVEST {}", starter.id),
                    Some(_) => "WAIT".to_string(),
                    None if view.inventories[0][APPLE] > 0 => {
                        format!("PICK {} APPLE", starter.id)
                    }
                    None => {
                        self.orchard_mother = None;
                        "WAIT".to_string()
                    }
                }
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn orchard_command(", orchard_command)
    changes.append(
        {
            "marker": "fn orchard_command(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(orchard_command.encode()),
            "logical_change": (
                "collapse duplicate orchard cargo branches and stop an exhausted seed loop"
            ),
        }
    )
    orchard_mother = r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 3 {
                    return None;
                }
                let enemy_distance = bfs_distances(
                    &view.walkable,
                    &ortho_neighbors(view.shacks[1]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .collect::<Vec<Cell>>(),
                );
                doors.into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance[door] >= 11)
                    .min_by_key(|door| (-enemy_distance[door], *door))
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn select_orchard_mother(", orchard_mother)
    changes.append(
        {
            "marker": "fn select_orchard_mother(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(orchard_mother.encode()),
            "logical_change": (
                "allow an empty eligible mother when a different home door has a natural tree"
            ),
        }
    )
    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_SAFE_ORCHARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "prevent same-door convoy deadlock and restore mixed-door orchard geometry "
                "with fail-closed APPLE exhaustion"
            ),
            "evidence_boundary": (
                "distinct size candidate after terminal rejection; requires a new lock and "
                "new untouched validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_door_harvest(source: str) -> tuple[str, dict]:
    """Let the front wood carrier clear a bank lane and preserve a ripe door tree."""

    result, manifest = focused_yamo_structural_specialization(source)
    changes = []
    old_bank_priority = (
        "7_000.0-Self::ceil_div(dist[&cell],unit.stats.movement_speed)as f64"
    )
    new_bank_priority = "7_000.0-dist[&cell]as f64"
    if result.count(old_bank_priority) != 1:
        raise ValueError("unexpected speed-normalized bank priority")
    before = len(result.encode())
    result = result.replace(old_bank_priority, new_bank_priority, 1)
    changes.append(
        {
            "marker": "bank lane priority",
            "net_removed_bytes": before - len(result.encode()),
            "logical_change": (
                "order same-door wood carriers by remaining cells rather than travel turns, "
                "so a faster rear worker cannot pin the front worker in WAIT"
            ),
        }
    )
    live_size_check = "if plant.size<=0{continue;}"
    if result.count(live_size_check) != 1:
        raise ValueError("unexpected live-tree size check")
    before = len(result.encode())
    result = result.replace(live_size_check, "", 1)
    changes.append(
        {
            "marker": "impossible live-tree size-zero branch",
            "bytes": before - len(result.encode()),
            "logical_change": "protocol plant rows always have size at least one",
        }
    )

    endgame = r"""fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                focus: Option<PlantKind>,
            ) -> Vec<Candidate> {
                let bank = || MoisanBot::bank_candidates(view, unit);
                if unit.carry[WOOD] > 0 {
                    return bank();
                }
                let turns_left = TOTAL_TURNS - view.turn + 1;
                let conversion = view.turn > 250
                    || view.turn >= 100 && view.plants.len() <= 2;
                if let Some(kind) = Self::fruit_kind(&unit.carry, false) {
                    if !conversion {
                        return bank();
                    }
                    let distance = bfs_distances(&view.walkable, &[unit.cell]);
                    let target = ortho_neighbors(view.shacks[0]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| view.plant_at(*cell).is_none())
                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
                        .min_by_key(|cell| (distance[cell], *cell));
                    let Some(cell) = target else {
                        return bank();
                    };
                    let travel = MoisanBot::ceil_div(
                        distance[&cell], unit.stats.movement_speed
                    );
                    if travel + MoisanBot::ceil_div(
                        tree_health(kind, 1), unit.stats.chop_power
                    ) + 3 > turns_left {
                        return bank();
                    }
                    return Self::single_candidate(if unit.cell == cell {
                            format!("PLANT {} {}", unit.id, kind.as_str())
                        } else {
                            format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                        }, Some(cell));
                }
                if unit.total_carried() > 0 {
                    return bank();
                }
                if is_adjacent(unit.cell, view.shacks[0]) {
                    if let Some(plant) = view.plant_at(unit.cell)
                        .map(|index| &view.plants[index])
                        .filter(|plant| plant.fruits > 0)
                    {
                        return Self::single_candidate(
                            format!("HARVEST {}", unit.id), Some(plant.cell)
                        );
                    }
                }
                if conversion && is_adjacent(unit.cell, view.shacks[0])
                    && view.plant_at(unit.cell).is_none()
                {
                    if let Some(kind) = Self::fruit_kind(&view.inventories[0], true) {
                        if MoisanBot::ceil_div(
                            tree_health(kind, 1), unit.stats.chop_power
                        ) + 3 <= turns_left
                        {
                            return Self::single_candidate(
                                format!("PICK {} {}", unit.id, kind.as_str()),
                                Some(unit.cell),
                            );
                        }
                    }
                }
                let mut out = vec![MoisanBot::wait()];
                out.extend(MoisanBot::chop_candidates(view, unit, focus));
                out
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn endgame_candidates(", endgame)
    changes.append(
        {
            "marker": "fn endgame_candidates(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(endgame.encode()),
            "logical_change": (
                "factor one conversion boundary, remove scores from single-command paths, "
                "and harvest a ripe natural tree while empty on a home door"
            ),
        }
    )
    single_candidate = r"""fn single_candidate(
                command: String,
                target: Target,
            ) -> Vec<Candidate> {
                vec![Candidate { command, score: 0.0, target }]
            }

            """
    insertion = "fn endgame_candidates("
    if result.count(insertion) != 1:
        raise ValueError("unexpected endgame insertion point")
    before = len(result.encode())
    result = result.replace(insertion, single_candidate + insertion, 1)
    changes.append(
        {
            "marker": "single-command candidate construction",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(single_candidate.encode()),
            "logical_change": "factor three unconditional single-command returns",
        }
    )
    fruit_kind = r"""fn fruit_kind(stock: &[i32; 6], bank: bool) -> Option<PlantKind> {
                let order = if bank {
                    [BANANA, PLUM, LEMON, APPLE]
                } else {
                    [PLUM, LEMON, APPLE, BANANA]
                };
                let item = order.into_iter().find(|item| stock[*item] > 0)?;
                Some([
                    PlantKind::Plum,
                    PlantKind::Lemon,
                    PlantKind::Apple,
                    PlantKind::Banana,
                ][item])
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn fruit_kind(", fruit_kind)
    changes.append(
        {
            "marker": "fn fruit_kind(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(fruit_kind.encode()),
            "logical_change": "replace a four-way item match with the protocol's index table",
        }
    )
    orchard_command = r"""fn orchard_command(&self, view: &GameState) -> String {
                let mother = self.orchard_mother.unwrap();
                let starter = view.units.iter()
                    .filter(|unit| unit.player == 0)
                    .min_by_key(|unit| unit.id).unwrap();
                if starter.cell != mother {
                    return format!("MOVE {} {} {}", starter.id, mother.0, mother.1);
                }
                let tree = view.plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple);
                if starter.total_carried() > 0 {
                    return if tree.is_none() && starter.carry[APPLE] > 0 {
                        format!("PLANT {} APPLE", starter.id)
                    } else {
                        format!("DROP {}", starter.id)
                    };
                }
                match tree {
                    Some(tree) if tree.fruits > 0 => {
                        format!("HARVEST {}", starter.id)
                    }
                    Some(_) => "WAIT".to_string(),
                    None => format!("PICK {} APPLE", starter.id),
                }
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn orchard_command(", orchard_command)
    changes.append(
        {
            "marker": "fn orchard_command(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(orchard_command.encode()),
            "logical_change": (
                "collapse duplicated tree/no-tree cargo branches into one orchard state split"
            ),
        }
    )
    orchard_mother = r"""fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 2 {
                    return None;
                }
                let enemy_distance = bfs_distances(
                    &view.walkable,
                    &ortho_neighbors(view.shacks[1]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .collect::<Vec<Cell>>(),
                );
                doors.into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance[door] >= 11)
                    .min_by_key(|door| (-enemy_distance[door], *door))
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn select_orchard_mother(", orchard_mother)
    changes.append(
        {
            "marker": "fn select_orchard_mother(",
            "net_removed_bytes": before - len(result.encode()),
            "replacement_bytes": len(orchard_mother.encode()),
            "logical_change": (
                "allow an empty eligible mother when a different home door has a natural tree"
            ),
        }
    )
    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_DOOR_HARVEST",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "replace speed-priority bank contention with a front-to-back convoy and "
                "retain productive natural door-tree harvesting in the simplified endgame"
            ),
            "evidence_boundary": (
                "distinct size candidate after terminal rejection; requires a new lock and "
                "new untouched validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_bank_convoy_door_harvest_no_orchard(
    source: str,
) -> tuple[str, dict]:
    """Delete the sparse orchard override after restoring natural door harvesting."""

    result, manifest = focused_yamo_bank_convoy_door_harvest(source)
    changes = []

    def replace_item(marker: str, replacement: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _replace_item(result, marker, replacement)
        changes.append(
            {
                "marker": marker,
                "net_removed_bytes": before - len(result.encode()),
                "replacement_bytes": len(replacement.encode()),
            }
        )

    def remove_item(marker: str) -> None:
        nonlocal result
        before = len(result.encode())
        result = _remove_item(result, marker)
        changes.append({"marker": marker, "bytes": before - len(result.encode())})

    replace_item(
        "pub struct YamoBot",
        r"""pub struct YamoBot {
            type_to_cut: Option<PlantKind>,
            desired_second: Option<Stats>,
        }""",
    )
    constructor = "Self { type_to_cut: None, desired_second: None, orchard_mother: None }"
    if result.count(constructor) != 1:
        raise ValueError("unexpected orchard-bearing Yamo constructor")
    result = result.replace(
        constructor, "Self { type_to_cut: None, desired_second: None }", 1
    )
    replace_item(
        "fn ensure_opening(",
        r"""fn ensure_opening(&mut self, view: &GameState) {
                if view.turn == 1 {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                    self.desired_second = Some(Self::choose_second_troll(view));
                }
            }""",
    )
    remove_item("fn select_orchard_mother(")
    remove_item("fn orchard_command(")

    old_loop = """                let orchard_mother = self.orchard_mother;
                let orchard_active = orchard_mother.is_some() && units.len() >= 2;
                for (unit_index, unit) in units.into_iter().enumerate() {
                    let mut candidates = if orchard_active && unit_index == 0
                    {
                        vec![MoisanBot::wait()]
                    } else if view.turn > 250 || !early {
"""
    new_loop = """                for unit in units {
                    let mut candidates = if view.turn > 250 || !early {
"""
    if result.count(old_loop) != 1:
        raise ValueError("unexpected orchard-bearing candidate loop")
    result = result.replace(old_loop, new_loop, 1)
    protection = """                    if orchard_active {
                        if let Some(mother) = orchard_mother {
                            candidates.retain(|candidate| !matches!(candidate.target,
                                Some(cell)
                                if cell == mother));
                        }
                    }
"""
    if result.count(protection) != 1:
        raise ValueError("unexpected orchard target protection")
    result = result.replace(protection, "", 1)
    override = """                let mut selected = MoisanBot::select(
                    candidates_by_id, &view.inventories[0]
                );
                if orchard_active {
                    selected[0] = self.orchard_command(view);
                }
"""
    plain_selection = """                let mut selected = MoisanBot::select(
                    candidates_by_id, &view.inventories[0]
                );
"""
    if result.count(override) != 1:
        raise ValueError("unexpected orchard command override")
    result = result.replace(override, plain_selection, 1)
    changes.append(
        {
            "marker": "orchard field, activation, reservation and command override",
            "logical_change": (
                "delete the six-map starter reservation while retaining ordinary natural "
                "door-tree harvesting and endgame fruit-to-wood conversion"
            ),
        }
    )
    manifest["removed_or_replaced_items"].extend(changes)
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_BANK_CONVOY_DOOR_HARVEST_NO_ORCHARD",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "delete the sparse secure-orchard override, preserve natural door-tree "
                "harvesting, and prevent same-door wood convoy deadlock"
            ),
            "evidence_boundary": (
                "distinct size candidate after terminal rejection; requires a new lock and "
                "new untouched validation block"
            ),
        }
    )
    return result, manifest


def focused_yamo_compact_endgame(source: str) -> tuple[str, dict]:
    """Factor the retained fruit-to-wood conversion path without changing its gates."""

    result, manifest = focused_yamo_wait_on_conflict(source)
    fruit_kind = r"""fn fruit_kind(stock: &[i32; 6], bank: bool) -> Option<PlantKind> {
                let items = if bank {
                    [BANANA, PLUM, LEMON, APPLE]
                } else {
                    [PLUM, LEMON, APPLE, BANANA]
                };
                items.into_iter()
                    .find(|item| stock[*item] > 0)
                    .map(|item| match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => PlantKind::Banana,
                    })
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn fruit_kind(", fruit_kind)
    fruit_saving = before - len(result.encode())
    endgame = r"""fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                focus: Option<PlantKind>,
            ) -> Vec<Candidate> {
                if unit.carry[WOOD] > 0 {
                    return MoisanBot::bank_candidates(view, unit);
                }
                let turns_left = TOTAL_TURNS - view.turn + 1;
                let conversion_turns = |kind, travel| {
                    travel + MoisanBot::ceil_div(
                        tree_health(kind, 1), unit.stats.chop_power,
                    ) + 3
                };
                if let Some(kind) = Self::fruit_kind(&unit.carry, false) {
                    if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2) {
                        return MoisanBot::bank_candidates(view, unit);
                    }
                    let distance = bfs_distances(&view.walkable, &[unit.cell]);
                    let target = ortho_neighbors(view.shacks[0]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| view.plant_at(*cell).is_none())
                        .filter(|cell| distance.contains_key(cell))
                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
                        .min_by_key(|cell| (distance[cell], *cell));
                    let Some(cell) = target else {
                        return MoisanBot::bank_candidates(view, unit);
                    };
                    let travel = MoisanBot::ceil_div(
                        distance[&cell], unit.stats.movement_speed,
                    );
                    if conversion_turns(kind, travel) > turns_left {
                        return MoisanBot::bank_candidates(view, unit);
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
                    return MoisanBot::bank_candidates(view, unit);
                }
                let mut candidates = vec![MoisanBot::wait()];
                if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2 {
                    if let Some(kind) = Self::fruit_kind(&view.inventories[0], true) {
                        if is_adjacent(unit.cell, view.shacks[0])
                            && view.plant_at(unit.cell).is_none()
                            && conversion_turns(kind, 0) <= turns_left
                        {
                            candidates.push(Candidate {
                                command: format!("PICK {} {}", unit.id, kind.as_str()),
                                score: 8_000.0,
                                target: Target::Cell(unit.cell),
                            });
                        }
                    }
                }
                candidates.extend(MoisanBot::chop_candidates(view, unit, focus));
                candidates
            }"""
    before = len(result.encode())
    result = _replace_item(result, "fn endgame_candidates(", endgame)
    endgame_saving = before - len(result.encode())
    manifest["removed_or_replaced_items"].extend(
        [
            {
                "marker": "fn fruit_kind(",
                "net_removed_bytes": fruit_saving,
                "replacement_bytes": len(fruit_kind.encode()),
            },
            {
                "marker": "fn endgame_candidates(",
                "net_removed_bytes": endgame_saving,
                "replacement_bytes": len(endgame.encode()),
            },
        ]
    )
    manifest.update(
        {
            "arm": "FOCUSED_YAMO_COMPACT_ENDGAME",
            "candidate_bytes": len(result.encode()),
            "candidate_sha256": sha256_bytes(result.encode()),
            "logical_change": (
                "retain the same fruit banking and late fruit-to-wood gates while sharing "
                "conversion-time calculation and direct fruit selection"
            ),
            "evidence_boundary": "semantic refactor; requires behavioral parity",
        }
    )
    return result, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--arm",
        choices=(
            "orchard-only",
            "focused-yamo-exact-moisan",
            "focused-yamo-partial-wood",
            "focused-yamo-all-training-profiles",
            "focused-yamo-stable-move-guard",
            "focused-yamo-fixed-carrying-chopper",
            "focused-yamo-no-forced-current-chop",
            "focused-yamo-exact-endgame-threshold",
            "focused-yamo-exact-opening",
            "focused-yamo-affordable-deadline",
            "focused-yamo-specialized-exact-initial",
            "focused-yamo-empty-priority-router",
            "focused-yamo-two-worker-live-state",
            "focused-yamo-live-trait-pruning",
            "focused-yamo-precomputed-opening-eta",
            "focused-yamo-bank-wait-fallback",
            "focused-yamo-compact-opening-eta",
            "focused-yamo-compact-orchard",
            "focused-yamo-direct-chop-forecast",
            "focused-yamo-runtime-state-pruning",
            "focused-yamo-collapsed-targets",
            "focused-yamo-wait-on-conflict",
            "focused-yamo-structural-specialization",
            "focused-yamo-bank-convoy",
            "focused-yamo-bank-convoy-spare-door-orchard",
            "focused-yamo-bank-convoy-spare-door-safe-select",
            "focused-yamo-bank-convoy-spare-door-period2-guard",
            "focused-yamo-bank-convoy-spare-door-slot-period2",
            "focused-yamo-bank-convoy-period2-lean-safe",
            "focused-yamo-bank-convoy-period2-lean-coordination",
            "focused-yamo-bank-convoy-period2-simple-clock",
            "focused-yamo-bank-convoy-safe-orchard",
            "focused-yamo-bank-convoy-door-harvest",
            "focused-yamo-bank-convoy-door-harvest-no-orchard",
            "focused-yamo-compact-endgame",
        ),
        default="orchard-only",
    )
    args = parser.parse_args()
    builders = {
        "orchard-only": orchard_only,
        "focused-yamo-exact-moisan": focused_yamo_exact_moisan,
        "focused-yamo-partial-wood": focused_yamo_partial_wood,
        "focused-yamo-all-training-profiles": focused_yamo_all_training_profiles,
        "focused-yamo-stable-move-guard": focused_yamo_stable_move_guard,
        "focused-yamo-fixed-carrying-chopper": focused_yamo_fixed_carrying_chopper,
        "focused-yamo-no-forced-current-chop": focused_yamo_no_forced_current_chop,
        "focused-yamo-exact-endgame-threshold": focused_yamo_exact_endgame_threshold,
        "focused-yamo-exact-opening": focused_yamo_exact_opening,
        "focused-yamo-affordable-deadline": focused_yamo_affordable_deadline,
        "focused-yamo-specialized-exact-initial": focused_yamo_specialized_exact_initial,
        "focused-yamo-empty-priority-router": focused_yamo_empty_priority_router,
        "focused-yamo-two-worker-live-state": focused_yamo_two_worker_live_state,
        "focused-yamo-live-trait-pruning": focused_yamo_live_trait_pruning,
        "focused-yamo-precomputed-opening-eta": focused_yamo_precomputed_opening_eta,
        "focused-yamo-bank-wait-fallback": focused_yamo_bank_wait_fallback,
        "focused-yamo-compact-opening-eta": focused_yamo_compact_opening_eta,
        "focused-yamo-compact-orchard": focused_yamo_compact_orchard,
        "focused-yamo-direct-chop-forecast": focused_yamo_direct_chop_forecast,
        "focused-yamo-runtime-state-pruning": focused_yamo_runtime_state_pruning,
        "focused-yamo-collapsed-targets": focused_yamo_collapsed_targets,
        "focused-yamo-wait-on-conflict": focused_yamo_wait_on_conflict,
        "focused-yamo-structural-specialization": focused_yamo_structural_specialization,
        "focused-yamo-bank-convoy": focused_yamo_bank_convoy,
        "focused-yamo-bank-convoy-spare-door-orchard": (
            focused_yamo_bank_convoy_spare_door_orchard
        ),
        "focused-yamo-bank-convoy-spare-door-safe-select": (
            focused_yamo_bank_convoy_spare_door_safe_select
        ),
        "focused-yamo-bank-convoy-spare-door-period2-guard": (
            focused_yamo_bank_convoy_spare_door_period2_guard
        ),
        "focused-yamo-bank-convoy-spare-door-slot-period2": (
            focused_yamo_bank_convoy_spare_door_slot_period2
        ),
        "focused-yamo-bank-convoy-period2-lean-safe": (
            focused_yamo_bank_convoy_period2_lean_safe
        ),
        "focused-yamo-bank-convoy-period2-lean-coordination": (
            focused_yamo_bank_convoy_period2_lean_coordination
        ),
        "focused-yamo-bank-convoy-period2-simple-clock": (
            focused_yamo_bank_convoy_period2_simple_clock
        ),
        "focused-yamo-bank-convoy-safe-orchard": (
            focused_yamo_bank_convoy_safe_orchard
        ),
        "focused-yamo-bank-convoy-door-harvest": (
            focused_yamo_bank_convoy_door_harvest
        ),
        "focused-yamo-bank-convoy-door-harvest-no-orchard": (
            focused_yamo_bank_convoy_door_harvest_no_orchard
        ),
        "focused-yamo-compact-endgame": focused_yamo_compact_endgame,
    }
    baseline = args.source.read_text()
    candidate, manifest = builders[args.arm](baseline)
    baseline_identifiers = lexical_identifiers(baseline)
    candidate_identifiers = lexical_identifiers(candidate)
    manifest["lexical_identifier_audit"] = {
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
        "removed_identifiers_are_consequence_of_declared_items": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
