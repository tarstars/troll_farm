#!/usr/bin/env python3
"""Generate the PLANT-aware start-game optimizer candidate from the champion of record.

The generator is fail-closed: it pins all three bases, applies the same token edits to the
instrumented arm and readable source, compiles both, compacts the arm, recompiles the exact
submission, writes a readable diff and records the action vocabulary and parameter file.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "cgauto"))
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import compact_rust_source as crs  # noqa: E402
import build_arms3 as ba  # noqa: E402

ARM_BASE = REPO / "local_claude_1" / "denial-ablation" / "champion-denial-off-v6-instrument.rs"
ARM_BASE_SHA = "321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f"
READABLE_BASE = REPO / "readable" / "denial-off-champion.rs"
READABLE_BASE_SHA = "4ce3d1e85e8962d84c0ecb1a071de46e844d24f7dbe5a31bd6ca0579db552143"
RESIDENT = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
RESIDENT_SHA = "0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c"

TYPES_TEMPLATE = HERE / "types.rs.in"
OPTIMIZER_TEMPLATE = HERE / "optimizer.rs.in"
PARAMETERS = HERE / "parameters.json"
ACTION_MANIFEST = HERE / "action-manifest.json"

ARM = HERE / "champion-start-game-optimizer-v6-instrument.rs"
READABLE = HERE / "start-game-optimizer-readable.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-start-game-optimizer-v6-instrument.rs"
DIFF = REPO / "readable" / "diffs" / "start-game-optimizer.diff"
REPORT = REPO / "readable" / "reports" / "candidate-start-game-optimizer-v6-instrument.round-trip.json"
RESULTS = HERE / "results"
BUILD = RESULTS / "build.json"


class BuildError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def token_stream(text: str) -> str:
    return crs.compact(text)


def replace_once(text: str, anchor: str, replacement: str, name: str) -> str:
    count = text.count(anchor)
    require(count == 1, f"{name}: anchor occurs {count} times, expected 1")
    return text.replace(anchor, replacement, 1)


def insert_before(text: str, anchor: str, insertion: str, name: str) -> str:
    return replace_once(text, anchor, insertion + anchor, name)


def insert_after(text: str, anchor: str, insertion: str, name: str) -> str:
    return replace_once(text, anchor, anchor + insertion, name)


def rust_literal(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        text = repr(value)
        return text if "." in text or "e" in text.lower() else text + ".0"
    return str(value)


def render_types() -> str:
    p = json.loads(PARAMETERS.read_text())
    mapping = {
        "__HORIZON__": p["horizon"],
        "__MAX_PLANTS__": p["max_plants"],
        "__MAX_PLANT_DISTANCE__": p["max_plant_distance"],
        "__MAX_CANDIDATE_CELLS__": p["max_candidate_cells"],
        "__MAX_PLAN_DEPTH__": p["max_plan_depth"],
        "__MAX_PLAN_STATES__": p["max_plan_states"],
        "__ACTIVATION_POINTS__": p["activation_points"],
        "__OPPORTUNITY_POINTS_PER_TURN__": p["opportunity_points_per_turn"],
        "__RAID_BEFORE_100__": p["raid_before_100_per_tree_turn"],
        "__RAID_AFTER_100__": p["raid_after_100_per_tree_turn"],
        "__RAID_DISTANCE_FACTOR__": p["raid_distance_factor"],
        "__ENABLE_THIRD__": p["enable_third"],
        "__THIRD_LATEST__": p["third_latest"],
        "__THIRD_MIN_ORCHARD_CELLS__": p["third_min_orchard_cells"],
        "__THIRD_MIN_NET__": p["third_min_net"],
    }
    text = TYPES_TEMPLATE.read_text()
    for marker, value in mapping.items():
        require(text.count(marker) == 1, f"parameter marker {marker} missing or repeated")
        text = text.replace(marker, rust_literal(value))
    require("__" not in text, "unexpanded parameter marker remains in types template")
    return text


FIELDS = (
    "            // Start-game optimizer state. Targets are in-flight PICK->PLANT macros;\n"
    "            // cells are trees observed after a successful PLANT.\n"
    "            optimizer_targets: BTreeMap<i32, (PlantKind, Cell)>,\n"
    "            optimizer_cells: BTreeSet<Cell>,\n"
    "            optimizer_handed_back: bool,\n"
    "            optimizer_searches: u32,\n"
    "            optimizer_plant_offers: u32,\n"
    "            optimizer_third_offers: u32,\n"
)

INIT = (
    "                    optimizer_targets: BTreeMap::new(),\n"
    "                    optimizer_cells: BTreeSet::new(),\n"
    "                    optimizer_handed_back: false,\n"
    "                    optimizer_searches: 0,\n"
    "                    optimizer_plant_offers: 0,\n"
    "                    optimizer_third_offers: 0,\n"
)

JOINT_HELPER = r'''            // Joint candidate choice for every own troll. The previous champion searched a
            // pair exactly and degraded to an id-order greedy pass for three or more trolls.
            // The bounded recursion preserves the exact pair behaviour and supports an optional
            // optimizer-created third troll without duplicate targets or overdrawn PICK stock.
            const OPTIMIZER_JOINT_LIMIT: usize = 400_000;
            fn optimizer_select_joint<'a>(
                lists: &[&'a Vec<Candidate>],
                inventory: &[i32; 6],
                chosen: &mut Vec<&'a Candidate>,
                sum: f64,
                best_score: &mut f64,
                best_set: &mut Option<Vec<String>>,
            ) {
                let depth = chosen.len();
                if depth == lists.len() {
                    if sum > *best_score {
                        *best_score = sum;
                        *best_set = Some(chosen.iter().map(|candidate| candidate.command.clone()).collect());
                    }
                    return;
                }
                for candidate in lists[depth] {
                    if !chosen
                        .iter()
                        .all(|earlier| Self::compatible(earlier.target, candidate.target))
                    {
                        continue;
                    }
                    if let Some(item) = Self::picked_item(&candidate.command) {
                        let already = chosen
                            .iter()
                            .filter(|earlier| Self::picked_item(&earlier.command) == Some(item))
                            .count() as i32;
                        if inventory[item] <= already {
                            continue;
                        }
                    }
                    chosen.push(candidate);
                    Self::optimizer_select_joint(
                        lists,
                        inventory,
                        chosen,
                        sum + candidate.score,
                        best_score,
                        best_set,
                    );
                    chosen.pop();
                }
            }
'''

PAIR_BLOCK = r'''                if ids.len() == 2 {
                    let mut best_score = f64::NEG_INFINITY;
                    let mut best_pair = None;
                    for a in &candidates_by_id[&ids[0]] {
                        for b in &candidates_by_id[&ids[1]] {
                            if !Self::compatible(a.target, b.target)
                                || !Self::stock_compatible(a, b, inventory)
                            {
                                continue;
                            }
                            let score = a.score + b.score;
                            if score > best_score {
                                best_score = score;
                                best_pair = Some((a.command.clone(), b.command.clone()));
                            }
                        }
                    }
                    if let Some((a, b)) = best_pair {
                        return vec![a, b];
                    }
                }
'''

JOINT_BLOCK = r'''                let lists: Vec<&Vec<Candidate>> =
                    ids.iter().map(|id| &candidates_by_id[id]).collect();
                let combinations = lists
                    .iter()
                    .fold(1usize, |count, list| count.saturating_mul(list.len()));
                if combinations <= Self::OPTIMIZER_JOINT_LIMIT {
                    let mut best_score = f64::NEG_INFINITY;
                    let mut best_set = None;
                    let mut chosen = Vec::new();
                    Self::optimizer_select_joint(
                        &lists,
                        inventory,
                        &mut chosen,
                        0.0,
                        &mut best_score,
                        &mut best_set,
                    );
                    if let Some(commands) = best_set {
                        return commands;
                    }
                }
'''


def transform(text: str, label: str) -> str:
    types = render_types()
    optimizer = OPTIMIZER_TEMPLATE.read_text()

    text = insert_before(text, "        pub struct YamoBot {\n", types, f"{label}: optimizer types")
    text = insert_after(
        text,
        "            regeneration_commitments: BTreeMap<i32, PlantKind>,\n",
        FIELDS,
        f"{label}: optimizer fields",
    )
    text = insert_after(
        text,
        "                    regeneration_commitments: BTreeMap::new(),\n",
        INIT,
        f"{label}: optimizer initialization",
    )
    text = insert_before(
        text,
        "            fn endgame(view: &GameState) -> bool {\n",
        optimizer + "\n",
        f"{label}: optimizer implementation",
    )
    text = insert_before(
        text,
        "            fn move_command(command: &str) -> Option<(i32, Cell)> {\n",
        JOINT_HELPER,
        f"{label}: joint selector helper",
    )
    text = replace_once(text, PAIR_BLOCK, JOINT_BLOCK, f"{label}: joint selector")

    text = insert_after(
        text,
        "                self.reconcile_regeneration_commitments(view);\n",
        "                self.optimizer_reconcile(view);\n",
        f"{label}: live optimizer reconciliation",
    )

    train_anchor = (
        "                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);\n"
    )
    train_text = (
        train_anchor
        + "                let optimizer_train = if train_now { None } else { self.optimizer_train_choice(view) };\n"
        + "                let any_train = train_now || optimizer_train.is_some();\n"
        + "                let train_stats = optimizer_train.unwrap_or(desired);\n"
    )
    text = replace_once(text, train_anchor, train_text, f"{label}: optimizer train choice")

    old_train = r'''                if train_now {
                    out.push(format!(
                        "TRAIN {} {} {} {}",
                        desired.movement_speed,
                        desired.carry_capacity,
                        desired.harvest_power,
                        desired.chop_power
                    ));
                }
'''
    new_train = r'''                if any_train {
                    out.push(format!(
                        "TRAIN {} {} {} {}",
                        train_stats.movement_speed,
                        train_stats.carry_capacity,
                        train_stats.harvest_power,
                        train_stats.chop_power
                    ));
                }
'''
    text = replace_once(text, old_train, new_train, f"{label}: emit selected train")
    text = replace_once(
        text,
        "                let early = !self.opening_abandoned && my_units.len() < 2 && !train_now;\n",
        "                let early = !self.opening_abandoned && my_units.len() < 2 && !any_train;\n",
        f"{label}: early mode respects any train",
    )
    text = replace_once(
        text,
        "                    if self.persistent_regeneration && train_now {\n",
        "                    if self.persistent_regeneration && any_train {\n",
        f"{label}: no pick during any train",
    )
    text = replace_once(
        text,
        "                    if train_now\n                        && unit.cell == view.shacks[0]\n",
        "                    if any_train\n                        && unit.cell == view.shacks[0]\n",
        f"{label}: vacate shack for any train",
    )

    hook_anchor = "                    by_id.insert(unit.id, candidates);\n"
    hook = (
        "                    self.optimizer_filter_young_orchard(view, &mut candidates);\n"
        "                    let optimizer_was_committed = self.optimizer_targets.contains_key(&unit.id);\n"
        "                    if let Some(optimizer) = self.optimizer_candidates(view, unit, any_train) {\n"
        "                        if optimizer_was_committed {\n"
        "                            candidates = optimizer;\n"
        "                        } else {\n"
        "                            candidates.extend(optimizer);\n"
        "                        }\n"
        "                    }\n"
    )
    text = insert_before(text, hook_anchor, hook, f"{label}: optimizer candidate hook")
    return text


def compile_check(text: str, crate: str) -> None:
    ba.compile_check(text, crate)


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    arm_base = ARM_BASE.read_text()
    readable_base = READABLE_BASE.read_text()
    resident = RESIDENT.read_text()
    require(sha(arm_base) == ARM_BASE_SHA, f"arm base hash changed: {sha(arm_base)}")
    require(sha(readable_base) == READABLE_BASE_SHA, f"readable base hash changed: {sha(readable_base)}")
    require(sha(resident) == RESIDENT_SHA, f"resident hash changed: {sha(resident)}")
    require(token_stream(arm_base) == token_stream(resident), "arm base != resident token stream")

    manifest = json.loads(ACTION_MANIFEST.read_text())
    require(manifest.get("finite_ledger") is True, "action manifest must declare finite ledger")
    require("PLANT" in manifest.get("searched_irreversible_choices", {}), "PLANT absent from manifest")

    arm = transform(arm_base, "arm")
    readable = transform(readable_base, "readable")
    # The diagnostics arm and owner-readable source intentionally carry different
    # non-feature tokens. Both receive the same anchored edit and compile independently;
    # only compact(arm) is the submission identity.

    compile_check(arm, "start_game_optimizer_arm")
    compile_check(readable, "start_game_optimizer_readable")
    ARM.write_text(arm)
    READABLE.write_text(readable)
    (HERE / f"{ARM.name}.sha256").write_text(f"{sha(arm)}  {ARM.name}\n")
    (HERE / f"{READABLE.name}.sha256").write_text(f"{sha(readable)}  {READABLE.name}\n")

    compacted = crs.compact(arm)
    if not compacted.endswith("\n"):
        compacted += "\n"
    require(token_stream(compacted) == token_stream(arm), "compacted token stream differs")
    compile_check(compacted, "start_game_optimizer_submission")
    SUBMISSION.write_text(compacted)
    (SUBMISSION.parent / f"{SUBMISSION.name}.sha256").write_text(
        f"{sha(compacted)}  {SUBMISSION.name}\n"
    )

    diff_lines = list(
        difflib.unified_diff(
            readable_base.splitlines(keepends=True),
            readable.splitlines(keepends=True),
            fromfile="readable/denial-off-champion.rs",
            tofile="readable/denial-off-champion.rs (start-game optimizer)",
            n=3,
        )
    )
    DIFF.parent.mkdir(parents=True, exist_ok=True)
    DIFF.write_text("".join(diff_lines))
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    utf16_units = len(compacted.encode("utf-16-le")) // 2
    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "20260904-start-game-optimizer-build",
        "candidate": "champion plus parameterised PLANT-aware bounded opening optimizer",
        "base": {
            "arm": str(ARM_BASE.relative_to(REPO)),
            "arm_sha256": ARM_BASE_SHA,
            "readable": str(READABLE_BASE.relative_to(REPO)),
            "readable_sha256": READABLE_BASE_SHA,
            "resident": str(RESIDENT.relative_to(REPO)),
            "resident_sha256": RESIDENT_SHA,
        },
        "arm": {"path": str(ARM.relative_to(REPO)), "sha256": sha(arm), "lines": len(arm.splitlines())},
        "readable": {"path": str(READABLE.relative_to(REPO)), "sha256": sha(readable)},
        "submission": {
            "path": str(SUBMISSION.relative_to(REPO)),
            "sha256": sha(compacted),
            "bytes": len(compacted.encode()),
            "utf16_units": utf16_units,
            "under_100000_utf16": utf16_units < 100_000,
        },
        "diff": str(DIFF.relative_to(REPO)),
        "action_manifest": str(ACTION_MANIFEST.relative_to(REPO)),
        "parameters": str(PARAMETERS.relative_to(REPO)),
        "round_trip_exact": True,
        "arm_readable_same_token_stream": token_stream(arm) == token_stream(readable),
        "compiles": True,
        "control": str(RESIDENT.relative_to(REPO)),
        "control_sha256": RESIDENT_SHA,
        "provisional_orchard_parameters": True,
        "third_training_enabled": json.loads(PARAMETERS.read_text())["enable_third"],
        "verdict": "BUILD_VALIDITY_READY",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    BUILD.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
