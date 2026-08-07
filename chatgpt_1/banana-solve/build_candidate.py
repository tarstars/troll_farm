#!/usr/bin/env python3
"""Build the owner-directed conservative Banana R2 candidate.

The stable parent and Claude's insertion seam remain byte-for-byte inputs.  This
builder applies a small, asserted source-to-source correction layer to the readable
BananaBot block, then reuses the existing fail-closed compaction/insertion builder.
Every replacement is exact and must occur once; drift aborts the build.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CLAUDE = REPO / "claude_1" / "banana-restoration-r2"
BASE_BLOCKS = CLAUDE / "banana_blocks"
PATCHED = HERE / "generated" / "banana_blocks"
OUT = HERE / "candidate-banana-r2.min.rs"
MANIFEST = HERE / "candidate-banana-r2-manifest.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = replace_once(
        text,
        "    banana_lost_banking: bool,\n}",
        "    banana_lost_banking: bool,\n"
        "    // Exact identity of the one diagonal mother founded by this wrapper.\n"
        "    // Never recomputed from arbitrary live bananas: an opponent plant cannot\n"
        "    // migrate the claim or ownership response.\n"
        "    banana_mother: Option<Cell>,\n} ",
        "mother field",
    )
    # Normalize the deliberately distinctive closing marker above.
    text = text.replace("\n} \n\nimpl BananaBot", "\n}\n\nimpl BananaBot", 1)
    text = replace_once(
        text,
        "            banana_lost_banking: false,\n        }",
        "            banana_lost_banking: false,\n"
        "            banana_mother: None,\n        }",
        "mother init",
    )

    old_mother = '''    /// The single protected mother (C3): the minimal diagonal ring cell
    /// holding a live banana. Deterministic; None while diag(tent) is empty.
    fn banana_mother_cell(view: &GameState) -> Option<Cell> {
        let tent = view.shacks[0];
        Self::banana_ring(view)
            .into_iter()
            .filter(|cell| !is_adjacent(*cell, tent))
            .filter(|cell| Self::banana_live(view, *cell).is_some())
            .min()
    }
'''
    new_mother = '''    /// The single protected mother, latched at our own founding decision.
    /// A natural/opponent banana is never adopted merely because it is the minimum
    /// diagonal cell.  The claim lapses when the exact latched plant is gone.
    fn banana_mother_cell(&self, view: &GameState) -> Option<Cell> {
        self.banana_mother
            .filter(|cell| Self::banana_live(view, *cell).is_some())
    }
'''
    text = replace_once(text, old_mother, new_mother, "latched mother helper")
    text = text.replace("Self::banana_mother_cell(view)", "self.banana_mother_cell(view)")

    old_safety = '''        if is_adjacent(cell, tent) {
            // Orthogonal wood slots keep the cheap instant margins: they
            // are meant to be cut within one cycle.
            return Self::banana_opponent_eta(view, cell, false) > resident_eta
                && Self::banana_opponent_eta(view, cell, true) > 2;
        }
        // F-C1 founding-horizon margin (rev. 2026-08-06, round-6 ruling 4):
        // the diagonal mother is a long-horizon asset — the old instant
        // margins (`> eta_res`, `> 2`) certified only the planting turn,
        // and every opponent harvester one fruit-cycle away farmed the
        // standing mother forever (diagnosis-r6 family (c), m023/m050:
        // eta_opp_h 0-5 at plant time). Margins, minimal compatible with
        // the committed I-10a machinery:
        //   harvesters: eta_opp_h > CD(c) + ceil(health(2)/chop) — one
        //     uncontested growth cycle plus the sapling's own conversion
        //     time. Not the full first-fruit horizon (4*CD): a harvester
        //     that closes in later flips I-7 while the mother is still
        //     unripe (first fruit >= 4*CD out), where the
        //     CONVERSION_RACE_ORACLE is feasible and the I-10a response
        //     converts the asset to wood — the recoverable-loss case whose
        //     normative witness is R-4 (founding executes at
        //     eta_opp_h = 11 > 10 and the t11 flip converts). The
        //     witnessed farmable foundings (eta_opp_h 0-5) are refused;
        //   choppers: the same margin — a chopper needs a growth cycle's
        //     head start to beat the resident's own convert response to a
        //     mid-growth sapling, and the committed t1 lifecycle witness
        //     (static chopper-capable opponent at eta 13) binds the
        //     chopper margin below 13 exactly as R-4 binds the harvester
        //     margin below 11.
        let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
        let margin = effective_cooldown(PlantKind::Banana, near_water)
            + MoisanBot::ceil_div(tree_health(PlantKind::Banana, 2), worker.stats.chop_power.max(1));
        Self::banana_opponent_eta(view, cell, false) > margin
            && Self::banana_opponent_eta(view, cell, true) > margin
'''
    new_safety = '''        let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
        let cooldown = effective_cooldown(PlantKind::Banana, near_water);
        let eta_h = Self::banana_opponent_eta(view, cell, false);
        let eta_x = Self::banana_opponent_eta(view, cell, true);
        if is_adjacent(cell, tent) {
            // Consumable wood trees are felled at size two, before fruit exists.
            // Still require enough uncontested time to grow and bank the cut;
            // this removes the opponent-chop-at-plant defect without pretending
            // an orthogonal tree is a renewable mother.
            let service = resident_eta + cooldown + 3;
            return eta_x > service;
        }
        // A renewable diagonal mother is founded only when its first fruit is
        // private under the current positions.  Four cooldown periods is the
        // exact conservative fresh-plant-to-first-fruit horizon (creation tick
        // included); ties are unsafe because cross-player co-location and
        // last-fruit duplication are legal.
        let first_fruit = resident_eta + 4 * cooldown + 2;
        eta_h > first_fruit && eta_x > first_fruit
'''
    text = replace_once(text, old_safety, new_safety, "plant safety")

    activation_helper = '''
    /// Conservative activation gate.  Banana play starts only on an open,
    /// multi-door ring where one private diagonal mother and one consumable
    /// orthogonal wood slot can be founded without interfering with the newly
    /// trained economy.  Risky maps remain byte-identical to the stable parent.
    fn banana_activation_safe(view: &GameState, worker: &Unit) -> bool {
        let tent = view.shacks[0];
        let doors: Vec<Cell> = ortho_neighbors(tent)
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .collect();
        if doors.len() < 3 {
            return false;
        }
        if view.units.iter().any(|unit| {
            unit.player == 0 && unit.id != worker.id && unit.total_carried() > 0
        }) {
            return false;
        }
        // Start from a clean plot; otherwise provenance and the single-mother
        // invariant are not observable.
        if Self::banana_ring(view)
            .into_iter()
            .any(|cell| Self::banana_live(view, cell).is_some())
        {
            return false;
        }
        let mut safe_diag = false;
        let mut safe_orth = false;
        for cell in Self::banana_ring(view) {
            if !Self::banana_vacant_ok(view, worker, cell, false) {
                continue;
            }
            if is_adjacent(cell, tent) {
                safe_orth = true;
                continue;
            }
            // The resident/claim cell must not be an articulation barrier for
            // any peer's route to every bank door.
            let mut walk = view.walkable.clone();
            walk.remove(&cell);
            let route_safe = view.units.iter().filter(|unit| {
                unit.player == 0 && unit.id != worker.id
            }).all(|unit| {
                let dist = bfs_distances(&walk, &[unit.cell]);
                doors.iter().any(|door| dist.contains_key(door))
            });
            if route_safe {
                safe_diag = true;
            }
        }
        safe_diag && safe_orth
    }

'''
    marker = "    /// Banking candidates (I-19/I-20/I-21, B7):"
    text = replace_once(text, marker, activation_helper + marker, "activation helper")

    old_activation = '''                // Checkpoint (family precedent: the orchard's on-door
                // checkpoint): the starter stands on the ring, and a seed
                // source exists (carried, banked, or a live ring banana).
                let seedable = starter.carry[BANANA] > 0
                    || view.inventories[0][BANANA] > 0
                    || Self::banana_ring(view)
                        .into_iter()
                        .any(|cell| Self::banana_live(view, cell).is_some());
                if on_ring && seedable {
'''
    new_activation = '''                // Checkpoint: the starter is on the ring, a seed exists,
                // and the complete bounded plot passes the conservative safety gate.
                let seedable = starter.carry[BANANA] > 0
                    || view.inventories[0][BANANA] > 0;
                if on_ring && seedable && Self::banana_activation_safe(view, starter) {
'''
    text = replace_once(text, old_activation, new_activation, "activation gate")

    # Yield the resident completely whenever a peer is already committed to
    # banking wood.  This is an observable, immediate owner-contract priority;
    # no resident reservation or priority re-resolution is written that turn.
    action_marker = '''    fn banana_action(&mut self, view: &GameState, worker: &Unit) -> Option<String> {
        // F-B3'''
    action_replacement = '''    fn banana_action(&mut self, view: &GameState, worker: &Unit) -> Option<String> {
        if view.units.iter().any(|unit| {
            unit.player == 0
                && unit.id != worker.id
                && unit.carry[crate::game::types::WOOD] > 0
        }) {
            self.banana_last_move = false;
            self.banana_last_cell = Some(worker.cell);
            return None;
        }
        // F-B3'''
    text = replace_once(text, action_marker, action_replacement, "peer carrier yield")

    # Latch the exact diagonal cell at the moment our PLANT command is selected.
    plant_latch_marker = '''        if chosen.3.starts_with("PICK ") {
            self.banana_bootstrap_used = true;
        }
'''
    plant_latch = '''        if chosen.3.starts_with("PICK ") {
            self.banana_bootstrap_used = true;
        }
        if chosen.3.starts_with("PLANT ")
            && !is_adjacent(chosen.2, view.shacks[0])
        {
            self.banana_mother = Some(chosen.2);
        }
'''
    text = replace_once(text, plant_latch_marker, plant_latch, "mother latch")

    # Replace the global/rest-of-game banana PICK veto with the one observable
    # bootstrap reservation.  Once our single bootstrap PICK has occurred, the
    # inner economy is never globally suppressed.
    old_veto = '''            let steals_seed = (active || lost)
                && commands[slot].starts_with("PICK ")
                && commands[slot].ends_with(" BANANA");
'''
    new_veto = '''            let steals_seed = active
                && !self.banana_bootstrap_used
                && commands[slot].starts_with("PICK ")
                && commands[slot].ends_with(" BANANA");
'''
    text = replace_once(text, old_veto, new_veto, "bounded seed veto")
    return text


def main() -> int:
    PATCHED.mkdir(parents=True, exist_ok=True)
    for path in BASE_BLOCKS.glob("block-i*.rs"):
        target = PATCHED / path.name
        if path.name == "block-i1.rs":
            target.write_text(patch_i1(path.read_text()))
        else:
            shutil.copyfile(path, target)

    spec = importlib.util.spec_from_file_location(
        "banana_base_builder", CLAUDE / "build_banana_candidate.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.BLOCKS = PATCHED
    module.OUT = OUT
    module.MANIFEST = MANIFEST
    result = module.main()
    manifest = json.loads(MANIFEST.read_text())
    manifest["owner_directed_patch"] = {
        "base_block_sha": "347356a3347ba9b01667b071017e8ad1599b975e",
        "patched_block": str(PATCHED / "block-i1.rs"),
        "policy": "safe-private-mother-v1",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
