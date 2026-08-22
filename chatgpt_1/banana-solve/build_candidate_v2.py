#!/usr/bin/env python3
"""Second owner-directed Banana R2 build: private-but-usable founding plus
proactive harvester/chopper conversion.

This layers exact asserted edits over build_candidate.py without modifying any
Claude-owned artifact.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "build_candidate.py"

spec = importlib.util.spec_from_file_location("banana_owner_base", BASE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
base_patch = mod.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)

    # A dry first fruit is about four cooldown periods away, but the resident
    # can deliberately convert a threatened young mother long before that.
    # Two periods of uncontested lead time is enough to make that response
    # executable while still allowing the canonical far-opponent lifecycle.
    text = replace_once(
        text,
        '''        let first_fruit = resident_eta + 4 * cooldown + 2;
        eta_h > first_fruit && eta_x > first_fruit
''',
        '''        let response_lead = 2 * cooldown;
        eta_h > response_lead && eta_x > response_lead
''',
        "founding response lead",
    )

    eta_helper_marker = '''    /// Growth-only forward simulation of a live plant over `turns` growth
'''
    chop_helper = '''    /// Earliest conservative opponent chop-out deadline, in turns from S_t.
    /// Same-player choppers cannot share the tree cell, so powers are never
    /// summed: each possible chopper is simulated alone and the earliest legal
    /// single-unit schedule wins.
    fn banana_opponent_chop_deadline(view: &GameState, cell: Cell) -> i32 {
        let Some(plant) = Self::banana_live(view, cell) else {
            return 10_000;
        };
        let dist = bfs_distances(&view.walkable, &[cell]);
        view.units
            .iter()
            .filter(|unit| unit.player == 1 && unit.stats.chop_power > 0)
            .filter_map(|unit| {
                let eta = dist
                    .get(&unit.cell)
                    .map(|d| MoisanBot::ceil_div(*d, unit.stats.movement_speed))?;
                let arrival = Self::banana_predict_growth(view, plant, eta);
                let (turns, _wood) = MoisanBot::chop_outcome(
                    view,
                    plant,
                    arrival,
                    unit.stats.chop_power,
                )?;
                Some(eta + turns - 1)
            })
            .min()
            .unwrap_or(10_000)
    }

'''
    text = replace_once(text, eta_helper_marker, chop_helper + eta_helper_marker,
                        "opponent chop deadline helper")

    old_race_header = '''            let eta_opp = Self::banana_opponent_eta(view, mother, false);
            let banking_drop_now = worker.carry[crate::game::types::WOOD] > 0
                && is_adjacent(worker.cell, view.shacks[0]);
            if resident_eta >= eta_opp && !banking_drop_now {
                let plant = Self::banana_live(view, mother);
                let fruits_ready = plant.map(|p| p.fruits > 0).unwrap_or(false);
'''
    new_race_header = '''            let eta_opp = Self::banana_opponent_eta(view, mother, false);
            let chop_deadline = Self::banana_opponent_chop_deadline(view, mother);
            let plant = Self::banana_live(view, mother);
            let conversion = worker.stats.chop_power.checked_sub(0).and_then(|_| {
                let p = plant?;
                if worker.stats.chop_power <= 0 || resident_eta >= 10_000 {
                    return None;
                }
                let arrival = Self::banana_predict_growth(view, p, resident_eta);
                let (turns, _wood) = MoisanBot::chop_outcome(
                    view, p, arrival, worker.stats.chop_power
                )?;
                Some(resident_eta + turns - 1)
            });
            let harvest_deadline = plant
                .map(|p| eta_opp.max(MoisanBot::ticks_until_fruit(view, p)))
                .unwrap_or(10_000);
            let loss_deadline = harvest_deadline.min(chop_deadline);
            // Do not wait for a geometric ownership tie.  Begin the response
            // while a still-feasible conversion has only a three-turn reserve;
            // this prevents the late-farm and chopper-spectator families.
            let threatened = conversion
                .map(|completion| loss_deadline <= completion + 3)
                .unwrap_or(true);
            let banking_drop_now = worker.carry[crate::game::types::WOOD] > 0
                && is_adjacent(worker.cell, view.shacks[0]);
            if (resident_eta >= eta_opp || threatened) && !banking_drop_now {
                let fruits_ready = plant.map(|p| p.fruits > 0).unwrap_or(false);
'''
    text = replace_once(text, old_race_header, new_race_header,
                        "proactive race header")

    # A co-located opponent can receive the same last fruit; do not call that
    # value secured.
    text = replace_once(
        text,
        '''                if fruits_ready
                    && worker.cell == mother
                    && worker.stats.harvest_power > 0
                    && worker.free_capacity() > 0
''',
        '''                if fruits_ready
                    && worker.cell == mother
                    && eta_opp > 0
                    && worker.stats.harvest_power > 0
                    && worker.free_capacity() > 0
''',
        "duplication-safe harvest",
    )

    old_feasible = '''                let feasible = worker.stats.chop_power > 0
                    && resident_eta < 10_000
                    && plant
                        .and_then(|p| {
                            let arrival =
                                Self::banana_predict_growth(view, p, resident_eta);
                            let (chop_turns, _wood) = MoisanBot::chop_outcome(
                                view,
                                p,
                                arrival,
                                worker.stats.chop_power,
                            )?;
                            let ripe = MoisanBot::ticks_until_fruit(view, p);
                            Some(resident_eta + chop_turns - 1 < eta_opp.max(ripe))
                        })
                        .unwrap_or(false);
'''
    new_feasible = '''                let feasible = conversion
                    .map(|completion| completion < loss_deadline)
                    .unwrap_or(false);
'''
    text = replace_once(text, old_feasible, new_feasible,
                        "combined harvest/chop feasibility")
    return text


mod.patch_i1 = patch_i1
raise SystemExit(mod.main())
