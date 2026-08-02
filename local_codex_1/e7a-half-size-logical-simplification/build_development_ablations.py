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
    }
    candidate, manifest = builders[args.arm](args.source.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
