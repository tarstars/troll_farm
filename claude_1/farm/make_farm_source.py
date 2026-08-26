#!/usr/bin/env python3
"""Generate the banana farm candidate's ONE source — task `20260826-banana-farm-candidate`.

Board row F-2. Packet of record: `claude_1/farm/g0-farm-2026-08-26.md`, round 2 as amended by
codex_1's round-2 W1 edit; ACCEPT-WITH-EDIT 20:45Z, the edit applied 20:57Z, the build authorised
by local_claude_1's policy `20260826T212149Z` at 21:21Z. The dialect is **v8**
(`claude_1/narrate8/narrate8.py`), not v7 — v7 is Candidate 3b's.

**What this file builds on, and why not the bare champion.** The farm arm has to carry v6's whole
diagnostic line (packet §8: "v8 = v6 plus one farm group, placed first"). v6's emitter is
`claude_1/cure3/cure3-keep-v6.rs`, which is the champion plus Candidate 3's keep rule *behind a
flag*. This generator imports that generator, rebuilds its text, verifies it against the recorded
sha, and then applies its own anchored replacements. `KEEP_RULE_ENABLED` is **false on every farm
arm** (packet §7, row W3): the farm supplies its own stickiness and Candidate 3's absolute keep is
closed and dead. So the farm arms are, in play, the champion plus the farm and nothing else.

Three arms come from this one file and ONE flag line (`build_arms_farm.py`):

  instrument  FARM=true  NARRATE=true    the panel read (v8 on the wire)
  candidate   FARM=true  NARRATE=false   the score block, and the ladder slot 3 on a pass
  farmoff     FARM=false NARRATE=true    the containment reference (gate C1)

    python3 claude_1/farm/make_farm_source.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import make_cure3_source as P  # noqa: E402

# The v6 emitter as this generator was written against. Regenerate with
# `python3 claude_1/cure3/make_cure3_source.py` and compare; a drift stops the build.
PARENT_SHA = "01b61444a109c1d190fba5b0a103c861c6f9e772596e97cf9042b9b2c516b3b3"
OUT = HERE / "farm-v8.rs"

GenError = P.GenError
replace_once = P.replace_once

# ------------------------------------------------------------------ 0. WOOD into the bot module
# W1 reads the wood slot of a troll's carry and the bot module never needed it before.
IMPORT_OLD = """        use crate::game::types::{
            Cell, GameState, Plant, PlantKind, Stats, Unit, APPLE, BANANA, IRON, LEMON, PLUM,
        };
"""
IMPORT_NEW = """        use crate::game::types::{
            Cell, GameState, Plant, PlantKind, Stats, Unit, APPLE, BANANA, IRON, LEMON, PLUM, WOOD,
        };
"""

# ------------------------------------------------------------------------- 1. the flag line
FLAG_OLD = ("            const KEEP_RULE_ENABLED: bool = true;"
            " const NARRATE_V6_ENABLED: bool = true;\n")
FLAG_NEW = '''            // ------------------------------------------------------- the banana farm (F-2)
            // Task 20260826-banana-farm-candidate; packet claude_1/farm/g0-farm-2026-08-26.md.
            // `build_arms_farm.py` rewrites exactly the line below to make the three arms and
            // checks that exactly one line differs, so "one source and a compile-time flag" stays
            // a property of the bytes. KEEP is false on every arm (packet §7 row W3): Candidate 3
            // is closed, and the farm carries its own stickiness.
            const KEEP_RULE_ENABLED: bool = false; const NARRATE_V6_ENABLED: bool = true; const FARM_ENABLED: bool = true;
            // The latch of packet §4.2, measured and NOT knobs: no other value was tried after the
            // 580-seat replay run, and §4 pre-commits to not re-tuning them on any later corpus.
            const FARM_WINDOW: i32 = 60;        // w — the window, inclusive [T-w+1, T]
            const FARM_OWN_FLOOR: u32 = 6;      // F — our own ring work before the ring is judged
            const FARM_EVIDENCE: u32 = 12;      // N — total events in the window
            const FARM_RATIO: u32 = 2;          // R — fe > R * fw, R = 2.0 on integers
            const FARM_PERSIST: i32 = 15;       // M — consecutive qualifying turns
            // Denial: the hard deadline of §2.1 (departure D3), the round cap and K of §5.
            const FARM_DENY_DEADLINE: i32 = 120;
            const FARM_ROUND_CAP: i32 = 40;
            const FARM_K: u32 = 2;
            // Build resolutions, recorded here because they are choices this file had to make and
            // the packet does not fix them (they travel to the reviewer in the handoff):
            //   * a denial chop is valued as the wood it takes PLUS this premium, in the
            //     champion's own scoring units (1000 * value / turns), so denial competes with
            //     ordinary chopping instead of overriding it;
            //   * a banana seed is worth 4 wood — one seed grown on a plot to size 4 and felled is
            //     4 wood = 16 points (contract §1) — and the farm's horizon constants are the
            //     referee's own growth arithmetic, not tuning: 24 turns to size 4, 6 chop hits.
            //   * BR-4: a farm candidate's divisor is the TROLL'S OCCUPANCY -- the turns the
            //     troll itself spends -- and never the wall clock, because a tree grows while
            //     the troll works elsewhere. This is the champion's own convention
            //     (`chop_candidates` divides by travel + chop + return, all occupancy); the
            //     first smoke read of this build charged the 24-turn growth to the troll, which
            //     scored every plant at ~125 against ordinary chops at ~200 and left the farm
            //     inert: 1 accepted farm plant across 34 fixtures. Corrected before the panel.
            const FARM_DENY_PREMIUM: f64 = 1.0;
            const FARM_SEED_WOOD: f64 = 4.0;
'''

# ------------------------------------------------------------------------ 2. the bot's state
STATE_OLD = "            last_cell: BTreeMap<i32, Cell>,\n        }\n"
STATE_NEW = '''            last_cell: BTreeMap<i32, Cell>,
            // --- the banana farm. Every field here is written by the farm code and by nothing
            // else, and every one of them is identically its initial value on a FARM=false arm.
            farm_state: u8,                     // 0 TRAIN . 1 DENY . 2 FARM . 3 WOOD (fs)
            farm_aim: Option<PlantKind>,        // §3, sticky for the whole of DENY
            farm_aim_base: i32,                 // the aim count when the round opened (§5)
            farm_round_open: i32,
            farm_flat_rounds: u32,              // consecutive non-falling rounds (§5)
            farm_deny_reason: Option<char>,     // fd — written once, at the turn DENY ends
            farm_plants: u32,                   // fp — accepted farm plants
            farm_harvests: u32,                 // fh — accepted mother harvests
            farm_latch: i32,                    // fl — the turn the latch fired, 0 until it does
            farm_fe: u32,                       // fe — enemy chop hits on our ring, cumulative
            farm_fw: u32,                       // fw — our own ring work events, cumulative
            farm_fe_win: Option<u32>,           // fE — the window pair, FROZEN at the latch turn
            farm_fw_win: Option<u32>,           // fW
            farm_events: Vec<(i32, u32, u32)>,  // (turn, enemy hits, own work) inside the window
            farm_hold: i32,                     // consecutive turns the latch condition has held
            // What the referee had done by the previous turn, so this turn can read what changed.
            farm_prev_ring: BTreeMap<Cell, (i32, i32, i32)>,   // ring cell -> (size, health, fruits)
            farm_prev_enemy: Vec<Cell>,
            // id -> (command, cell, chop power, was this command a farm offer?)
            farm_prev_cmd: BTreeMap<i32, (String, Cell, i32, bool)>,
            // W3: the ring cell a troll is working, held until the cell's job is done or it dies.
            farm_jobs: BTreeMap<i32, Cell>,
            // Trolls carrying a banana the FARM asked for, and that the farm therefore owes the
            // ring (BR-8).
            farm_seeded: BTreeSet<i32>,
            farm_offer: BTreeMap<i32, Vec<(String, Cell)>>,    // this turn's farm offers, by unit
        }
'''

INIT_OLD = "                    last_cell: BTreeMap::new(),\n                }\n"
INIT_NEW = '''                    last_cell: BTreeMap::new(),
                    farm_state: 0,
                    farm_aim: None,
                    farm_aim_base: 0,
                    farm_round_open: 0,
                    farm_flat_rounds: 0,
                    farm_deny_reason: None,
                    farm_plants: 0,
                    farm_harvests: 0,
                    farm_latch: 0,
                    farm_fe: 0,
                    farm_fw: 0,
                    farm_fe_win: None,
                    farm_fw_win: None,
                    farm_events: Vec::new(),
                    farm_hold: 0,
                    farm_prev_ring: BTreeMap::new(),
                    farm_prev_enemy: Vec::new(),
                    farm_prev_cmd: BTreeMap::new(),
                    farm_jobs: BTreeMap::new(),
                    farm_seeded: BTreeSet::new(),
                    farm_offer: BTreeMap::new(),
                }
'''

# ------------------------------------------------------------------------ 3. the farm itself
FARM_ANCHOR = "        impl YamoBot {\n            pub fn with_opening_policy"
FARM_BLOCK = '''        impl YamoBot {
            // ======================================================== the banana farm (F-2)
            // Packet claude_1/farm/g0-farm-2026-08-26.md. Four states, three one-way edges:
            //     TRAIN --e1--> DENY --e2--> FARM --e3--> WOOD
            // e1 fires when our second troll exists (the owner's standing rule of 2026-08-10:
            // no banana action of any kind before the second troll is trained), e2 on the first
            // of the five ordered reasons of §2.1, e3 is the latch of §4.2. Nothing returns.

            /// The eight ring cells of our own hut that lie on the board. This is the ring the
            /// latch counts on, and it is deliberately the set `claude_1/farm/ring_pressure.py`
            /// counted when the rule was calibrated: in-bounds neighbours of the hut, walkable or
            /// not — a tree stands only on a walkable cell anyway, and dropping the others here
            /// would move the definition away from the one the numbers came from.
            fn farm_ring_cells(view: &GameState) -> BTreeSet<Cell> {
                let (hx, hy) = view.shacks[0];
                let mut out = BTreeSet::new();
                for dx in -1..=1 {
                    for dy in -1..=1 {
                        if dx == 0 && dy == 0 {
                            continue;
                        }
                        let cell = (hx + dx, hy + dy);
                        if cell.0 >= 0 && cell.0 < view.width && cell.1 >= 0 && cell.1 < view.height
                        {
                            out.insert(cell);
                        }
                    }
                }
                out
            }

            /// The plots: the walkable orthogonal ring cells. **The single-door exclusion of
            /// §2.4**: where exactly one orthogonal cell is walkable it is the shack's only door
            /// and is never planted, so the farm has no plots at all on such a seat (gate R1).
            fn farm_plots(view: &GameState) -> Vec<Cell> {
                let open: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                if open.len() <= 1 {
                    return Vec::new();
                }
                open
            }

            /// The mothers: the walkable diagonal ring cells, farthest from the enemy hut first
            /// ("do not create fruit the opponent can harvest before us", owner 2026-08-02). A
            /// diagonal the enemy cannot reach at all sorts first, which is the same preference
            /// taken to its limit.
            fn farm_mothers(view: &GameState) -> Vec<Cell> {
                let (hx, hy) = view.shacks[0];
                let from_enemy = bfs_distances(&view.walkable, &[view.shacks[1]]);
                let mut out: Vec<Cell> = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                    .into_iter()
                    .map(|(dx, dy)| (hx + dx, hy + dy))
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                out.sort_by_key(|cell| {
                    (
                        std::cmp::Reverse(from_enemy.get(cell).copied().unwrap_or(i32::MAX)),
                        *cell,
                    )
                });
                out
            }

            fn farm_doors(view: &GameState) -> Vec<Cell> {
                ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect()
            }

            fn farm_enemy_half(view: &GameState, cell: Cell) -> bool {
                manhattan(cell, view.shacks[1]) <= manhattan(cell, view.shacks[0])
            }

            fn farm_aim_trees(view: &GameState, aim: PlantKind) -> Vec<Cell> {
                view.plants
                    .iter()
                    .filter(|plant| {
                        plant.kind == aim
                            && plant.health > 0
                            && Self::farm_enemy_half(view, plant.cell)
                    })
                    .map(|plant| plant.cell)
                    .collect()
            }

            /// §3. Aim = the species that funds the enemy's next troll, resolved by cost
            /// shortfall, then by the smaller standing count. Bananas and wood are never a
            /// training cost, so they are never an aim. Called at most once per denial round.
            fn farm_select_aim(&mut self, view: &GameState) {
                let cost = training_cost(3, Self::fallback_second_troll().tuple());
                let mut best: Option<(PlantKind, i32, i32)> = None;
                for (index, kind) in [
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                ] {
                    let need = (cost[index] - view.inventories[1][index]).max(0);
                    let standing = Self::farm_aim_trees(view, kind).len() as i32;
                    let better = match best {
                        None => true,
                        Some((_, best_need, best_standing)) => {
                            need > best_need || (need == best_need && standing < best_standing)
                        }
                    };
                    if better {
                        best = Some((kind, need, standing));
                    }
                }
                if let Some((kind, _, standing)) = best {
                    self.farm_aim = Some(kind);
                    self.farm_aim_base = standing;
                    self.farm_round_open = view.turn;
                    self.farm_flat_rounds = 0;
                }
            }

            /// §2.1's five reasons, in their fixed order, first match wins and the rest are not
            /// evaluated. The round bookkeeping of §5 rides inside reason `b`: a round can only
            /// ever close on the 40-turn cap here, because "no aim tree alive" and "none
            /// reachable" are themselves reasons `a` and `d` and are tested first.
            fn farm_deny_exit(&mut self, view: &GameState) -> Option<char> {
                if view.turn >= MoisanBot::FARM_DENY_DEADLINE {
                    return Some('t');
                }
                if view.units.iter().filter(|unit| unit.player == 1).count() >= 3 {
                    return Some('c');
                }
                let Some(aim) = self.farm_aim else {
                    return Some('a');
                };
                let alive = Self::farm_aim_trees(view, aim);
                if alive.is_empty() {
                    return Some('a');
                }
                let mut sources: Vec<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.cell)
                    .collect();
                sources.sort();
                let reach = bfs_distances(&view.walkable, &sources);
                if !alive.iter().any(|cell| reach.contains_key(cell)) {
                    return Some('d');
                }
                if view.turn - self.farm_round_open >= MoisanBot::FARM_ROUND_CAP {
                    let count = alive.len() as i32;
                    if count >= self.farm_aim_base {
                        self.farm_flat_rounds += 1;
                    } else {
                        self.farm_flat_rounds = 0;
                    }
                    self.farm_aim_base = count;
                    self.farm_round_open = view.turn;
                    if self.farm_flat_rounds >= MoisanBot::FARM_K {
                        return Some('b');
                    }
                }
                None
            }

            /// The window pair of §4.5: the inclusive range [T-w+1, T], counted per event.
            fn farm_window(&self) -> (u32, u32) {
                let mut fe = 0;
                let mut fw = 0;
                for (_, enemy, own) in &self.farm_events {
                    fe += *enemy;
                    fw += *own;
                }
                (fe, fw)
            }

            /// e3 — the latch of §4.2, evaluated once per turn and only in FARM. Five parts: a
            /// full window, our own work floor F, the evidence floor N, the ratio R, and M
            /// consecutive qualifying turns. One-way: `farm_latch` is written once and the window
            /// pair is frozen with it.
            fn farm_latch_test(&mut self, view: &GameState) {
                if self.farm_latch != 0 {
                    return;
                }
                let (fe, fw) = self.farm_window();
                let holds = view.turn >= MoisanBot::FARM_WINDOW
                    && fw >= MoisanBot::FARM_OWN_FLOOR
                    && fe + fw >= MoisanBot::FARM_EVIDENCE
                    && fe > MoisanBot::FARM_RATIO * fw;
                if holds {
                    self.farm_hold += 1;
                } else {
                    self.farm_hold = 0;
                }
                if self.farm_hold >= MoisanBot::FARM_PERSIST {
                    self.farm_latch = view.turn;
                    self.farm_fe_win = Some(fe);
                    self.farm_fw_win = Some(fw);
                    self.farm_state = 3;
                }
            }

            /// Read what the referee accepted since our last turn off the view, and count it onto
            /// the ring. §4.5(3): one enemy hit per (turn, ring cell) where the cell's plant lost
            /// health and an enemy troll stood on it — whatever the size of the loss. §4.5(4): a
            /// loss with no enemy troll on the cell is not attributable and is not counted.
            fn farm_observe(&mut self, view: &GameState) {
                let ring = Self::farm_ring_cells(view);
                let mut own_events: u32 = 0;
                let mut enemy_events: u32 = 0;
                let mut our_damage: BTreeMap<Cell, i32> = BTreeMap::new();
                let mother_cells: BTreeSet<Cell> = Self::farm_mothers(view).into_iter().collect();
                let prev_cmd = self.farm_prev_cmd.clone();
                for (_, (command, cell, power, farm_offered)) in &prev_cmd {
                    if !ring.contains(cell) {
                        continue;
                    }
                    let before = self.farm_prev_ring.get(cell).copied();
                    let now = view.plant_at(*cell).map(|index| {
                        let plant = &view.plants[index];
                        (plant.size, plant.health, plant.fruits)
                    });
                    if command.starts_with("CHOP ") {
                        *our_damage.entry(*cell).or_insert(0) += *power;
                        let accepted = match (before, now) {
                            (Some(b), Some(n)) => n.1 < b.1 || n.0 < b.0,
                            (Some(_), None) => true,
                            _ => false,
                        };
                        if accepted {
                            own_events += 1;
                        }
                    } else if command.starts_with("HARVEST ") {
                        let accepted = match (before, now) {
                            (Some(b), Some(n)) => n.2 < b.2,
                            _ => false,
                        };
                        if accepted {
                            own_events += 1;
                            if mother_cells.contains(cell) {
                                self.farm_harvests += 1;
                            }
                        }
                    } else if command.starts_with("PLANT ") {
                        // `fp` claims **accepted FARM plants**, so it counts only a PLANT the
                        // farm itself offered. Build resolution BR-2, made because the first
                        // smoke read showed `fp=2` on a fixture whose state never left TRAIN:
                        // the champion's own regeneration plants land on ring cells too, and a
                        // cell-attributed counter reported them as farm plants — that is, it
                        // reported the owner's standing rule broken when it was not.
                        if *farm_offered && before.is_none() && now.is_some() {
                            self.farm_plants += 1;
                        }
                    }
                }
                let prev_ring = self.farm_prev_ring.clone();
                for (cell, before) in &prev_ring {
                    let now = view.plant_at(*cell).map(|index| {
                        let plant = &view.plants[index];
                        (plant.size, plant.health, plant.fruits)
                    });
                    // A tree that GREW had its health recomputed by the referee, so no loss is
                    // readable on such a turn: the cell is skipped rather than guessed at.
                    let loss = match now {
                        Some((size, health, _)) => {
                            if size > before.0 {
                                0
                            } else {
                                (before.1 - health).max(0)
                            }
                        }
                        None => before.1,
                    };
                    let ours = our_damage.get(cell).copied().unwrap_or(0);
                    if loss > ours && self.farm_prev_enemy.iter().any(|other| other == cell) {
                        enemy_events += 1;
                    }
                }
                // A troll that no longer carries a banana no longer owes the ring one.
                let holders: BTreeSet<i32> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && unit.carry[BANANA] > 0)
                    .map(|unit| unit.id)
                    .collect();
                self.farm_seeded.retain(|id| holders.contains(id));
                self.farm_fe += enemy_events;
                self.farm_fw += own_events;
                self.farm_events.push((view.turn, enemy_events, own_events));
                let floor = view.turn - MoisanBot::FARM_WINDOW + 1;
                self.farm_events.retain(|(turn, _, _)| *turn >= floor);
            }

            /// The state transitions, run once per turn at the top of `commands()`, before any
            /// candidate is built.
            fn farm_step(&mut self, view: &GameState) {
                if self.farm_state == 0 {
                    // e1: the owner's standing rule made structural — no banana action of any
                    // kind before the second troll exists.
                    if view.units.iter().filter(|unit| unit.player == 0).count() >= 2 {
                        self.farm_state = 1;
                        self.farm_select_aim(view);
                    }
                }
                if self.farm_state == 1 {
                    if let Some(reason) = self.farm_deny_exit(view) {
                        self.farm_deny_reason = Some(reason);
                        self.farm_state = 2;
                    }
                }
                if self.farm_state == 2 {
                    self.farm_latch_test(view);
                }
            }

            /// The farm's offers for one troll: (candidate, the ring cell the candidate is a job
            /// on). They are proposed into the champion's pool and compete there; they never
            /// override it. Scores are in the champion's own units — 1000 * value / turns — so
            /// that competing means what it says.
            fn farm_offers(&self, view: &GameState, unit: &Unit) -> Vec<(Candidate, Cell)> {
                let mut out: Vec<(Candidate, Cell)> = Vec::new();
                if self.farm_state != 1 && self.farm_state != 2 {
                    return out;
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let speed = unit.stats.movement_speed.max(1);
                // Mothers in both DENY and FARM (owner decision 3: during denial the ring is
                // planted with mothers and nothing else); plots only once denial is over.
                let mothers = Self::farm_mothers(view);
                // Build resolution BR-3, from the first smoke read: seeds are scarce (the shack
                // starts with at most one banana) and §2.2 leaves the ORDER of the jobs open. A
                // seed spent on a plot is felled for 4 wood and the farm is over; a seed spent on
                // a mother is the only way the farm ever reproduces. So while **no mother is
                // standing**, mothers come first; once one does, §2.2's routing takes over and an
                // empty plot is filled first.
                let mother_standing = mothers.iter().any(|cell| {
                    view.plant_at(*cell).map_or(false, |index| {
                        view.plants[index].kind == PlantKind::Banana
                            && view.plants[index].health > 0
                    })
                });
                let mut empty_job: Option<Cell> = None;
                let mut jobs: Vec<(Cell, bool)> = Vec::new();
                if mother_standing && self.farm_state == 2 {
                    for cell in Self::farm_plots(view) {
                        jobs.push((cell, true));
                    }
                }
                for cell in &mothers {
                    jobs.push((*cell, false));
                }
                if !mother_standing && self.farm_state == 2 {
                    for cell in Self::farm_plots(view) {
                        jobs.push((cell, true));
                    }
                }
                // W2/W4: a cell another troll is already working is not offered to this one.
                let taken: BTreeSet<Cell> = self
                    .farm_jobs
                    .iter()
                    .filter(|(id, _)| **id != unit.id)
                    .map(|(_, cell)| *cell)
                    .collect();
                // W3: a job, once taken, is held until the cell's job is done or the cell dies.
                if let Some(held) = self.farm_jobs.get(&unit.id) {
                    if jobs.iter().any(|(cell, _)| cell == held) {
                        jobs.retain(|(cell, _)| cell == held);
                    }
                }
                for (cell, is_plot) in jobs {
                    if taken.contains(&cell) || !from_unit.contains_key(&cell) {
                        continue;
                    }
                    let travel = MoisanBot::ceil_div(from_unit[&cell], speed);
                    match view.plant_at(cell) {
                        None => {
                            if empty_job.is_none() {
                                empty_job = Some(cell);
                            }
                            if unit.carry[BANANA] > 0 {
                                // BR-4: the divisor is the troll's OCCUPANCY, not the wall clock.
                                let turns = (travel + 1).max(1);
                                let command = if unit.cell == cell {
                                    format!("PLANT {} {}", unit.id, PlantKind::Banana.as_str())
                                } else {
                                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                };
                                out.push((
                                    Candidate {
                                        command,
                                        score: 1000.0 * MoisanBot::FARM_SEED_WOOD
                                            / turns as f64,
                                        target: Target::Cell(cell),
                                    },
                                    cell,
                                ));
                            }
                        }
                        Some(index) => {
                            let plant = view.plants[index].clone();
                            if plant.kind != PlantKind::Banana || plant.health <= 0 {
                                continue;
                            }
                            if is_plot {
                                // A plot banana is felled at full size and never before: 4 wood
                                // from one seed is the whole of the farm's income.
                                if plant.size >= 4
                                    && unit.stats.chop_power > 0
                                    && unit.free_capacity() > 0
                                {
                                    let hits =
                                        MoisanBot::ceil_div(plant.health, unit.stats.chop_power);
                                    let turns = (travel + hits + 1).max(1);
                                    let command = if unit.cell == cell {
                                        format!("CHOP {}", unit.id)
                                    } else {
                                        format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                    };
                                    out.push((
                                        Candidate {
                                            command,
                                            score: 1000.0 * MoisanBot::FARM_SEED_WOOD
                                                / turns as f64,
                                            target: Target::Tree(cell),
                                        },
                                        cell,
                                    ));
                                }
                            } else if plant.fruits > 0
                                && unit.stats.harvest_power > 0
                                && unit.free_capacity() > 0
                            {
                                // A mother is harvested and NEVER chopped. Her fruit is the next
                                // plot's seed, so it is valued at the seed's horizon.
                                let turns = (travel + 1).max(1);
                                let command = if unit.cell == cell {
                                    format!("HARVEST {}", unit.id)
                                } else {
                                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                };
                                out.push((
                                    Candidate {
                                        command,
                                        score: 1000.0 * MoisanBot::FARM_SEED_WOOD / turns as f64,
                                        target: Target::Tree(cell),
                                    },
                                    cell,
                                ));
                            }
                        }
                    }
                }
                // A seed out of the shack, when the ring has an empty cell to fill and this
                // troll carries no banana. PICK needs the troll adjacent to the shack, which
                // every plot is by construction. The first smoke read showed this offer doing
                // harm without the guard below it: it put a banana in a troll's carry that the
                // FARM had asked for and the CHAMPION then spent — planted outside the ring on
                // m007 seat 1 (detector D-5). The offer is kept, because without it the farm
                // never gets its first seed and never reproduces, and the seed is guarded by
                // `farm_seed_filter` (BR-8) instead.
                if let Some(job) = empty_job {
                    if unit.carry[BANANA] == 0
                        && view.inventories[0][BANANA] > 0
                        && unit.free_capacity() > 0
                    {
                        let doors = Self::farm_doors(view);
                        if is_adjacent(unit.cell, view.shacks[0]) {
                            out.push((
                                Candidate {
                                    command: format!(
                                        "PICK {} {}",
                                        unit.id,
                                        PlantKind::Banana.as_str()
                                    ),
                                    score: 1000.0 * MoisanBot::FARM_SEED_WOOD,
                                    target: Target::Cell(unit.cell),
                                },
                                job,
                            ));
                        } else if let Some(door) = doors
                            .into_iter()
                            .filter(|cell| from_unit.contains_key(cell))
                            .min_by_key(|cell| (from_unit[cell], *cell))
                        {
                            let travel = MoisanBot::ceil_div(from_unit[&door], speed);
                            let turns = (travel + 1).max(1);
                            out.push((
                                Candidate {
                                    command: format!("MOVE {} {} {}", unit.id, door.0, door.1),
                                    score: 1000.0 * MoisanBot::FARM_SEED_WOOD / turns as f64,
                                    target: Target::Cell(door),
                                },
                                job,
                            ));
                        }
                    }
                }
                // Denial: chop the aim, and only the aim, on the enemy's half. The wood is ours
                // at 4 points a unit, so this is income and not sacrifice (contract §1).
                if self.farm_state == 1 {
                    if let Some(aim) = self.farm_aim {
                        if unit.stats.chop_power > 0 && unit.free_capacity() > 0 {
                            for cell in Self::farm_aim_trees(view, aim) {
                                let Some(index) = view.plant_at(cell) else {
                                    continue;
                                };
                                if !from_unit.contains_key(&cell) {
                                    continue;
                                }
                                let plant = view.plants[index].clone();
                                let travel = MoisanBot::ceil_div(from_unit[&cell], speed);
                                let hits =
                                    MoisanBot::ceil_div(plant.health, unit.stats.chop_power);
                                let turns = (travel + hits + 1).max(1);
                                let value = plant.size as f64 + MoisanBot::FARM_DENY_PREMIUM;
                                let command = if unit.cell == cell {
                                    format!("CHOP {}", unit.id)
                                } else {
                                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                                };
                                out.push((
                                    Candidate {
                                        command,
                                        score: 1000.0 * value / turns as f64,
                                        target: Target::Tree(cell),
                                    },
                                    cell,
                                ));
                            }
                        }
                    }
                }
                out
            }

            /// **BR-8, the seed guard** — W1's shape applied to a banana the farm asked for.
            /// The farm has no authority over what the champion does with a carried fruit, and
            /// the first smoke read showed the champion planting the farm's seed outside the ring
            /// (m007 seat 1, detector D-5). So a troll that took a banana on a FARM offer has its
            /// candidate list filtered down to the farm's own offers until the banana leaves its
            /// carry. If the farm has no offer for it this turn — the ring filled up while it
            /// walked — the list is left alone, which is the side that never strands a troll.
            fn farm_seed_filter(
                &self,
                unit: &Unit,
                offers: &BTreeSet<String>,
                candidates: &mut Vec<Candidate>,
            ) {
                if offers.is_empty()
                    || unit.carry[BANANA] <= 0
                    || !self.farm_seeded.contains(&unit.id)
                {
                    return;
                }
                candidates.retain(|candidate| offers.contains(&candidate.command));
                if candidates.is_empty() {
                    candidates.push(MoisanBot::wait());
                }
            }

            /// A mother is harvested and NEVER chopped (§2.2). The farm does not chop one --
            /// and until this filter it did not stop the CHAMPION chopping one either: on m007
            /// seat 0 of the first smoke read the champion's ordinary chop candidate felled the
            /// mother the farm had just planted on the diagonal, three times over (detector D-8,
            /// `diag_mother_chop`). Build resolution BR-6: while the farm is running, every
            /// candidate AIMED AT a living banana on a mother cell is removed from every troll's
            /// list unless the farm itself offered it this turn -- the same shape of filter as W1.
            ///
            /// **Removing only the `CHOP` was not enough, and the second smoke read said so.** A
            /// troll standing next to the mother had its CHOP removed and its next-best candidate
            /// was a MOVE onto the same mother, whose CHOP was then removed again: an A->B->A
            /// shuttle of 6 flips on m007 seats 0 and 1 and m003 seat 1 (detector D-1). The
            /// approach MOVE carries the same `Target::Tree(cell)` as the chop it exists to
            /// serve, so the target is what the guard reads, and the farm's own offers -- which
            /// are how a mother is harvested -- are exempted by their command string.
            fn farm_mother_guard(
                &self,
                view: &GameState,
                offers: &BTreeSet<String>,
                candidates: &mut Vec<Candidate>,
            ) {
                if self.farm_state != 1 && self.farm_state != 2 {
                    return;
                }
                let mothers: BTreeSet<Cell> = Self::farm_mothers(view)
                    .into_iter()
                    .filter(|cell| {
                        view.plant_at(*cell).map_or(false, |index| {
                            view.plants[index].kind == PlantKind::Banana
                                && view.plants[index].health > 0
                        })
                    })
                    .collect();
                if mothers.is_empty() {
                    return;
                }
                candidates.retain(|candidate| match candidate.target {
                    Target::Tree(cell) => {
                        !mothers.contains(&cell) || offers.contains(&candidate.command)
                    }
                    _ => true,
                });
                if candidates.is_empty() {
                    candidates.push(MoisanBot::wait());
                }
            }

            /// **W1, as codex_1's round-2 edit requires it**: a filter over the wood carrier's
            /// WHOLE candidate list, applied before pair selection, not the omission of farm
            /// candidates. Every candidate that is neither a DROP nor a MOVE whose accepted next
            /// cell strictly reduces shortest-path distance to a legal shack drop cell is
            /// removed, whatever its source and whatever the troll was targeting when the wood
            /// entered its carry. Build resolution of the empty case, in the direction that never
            /// diverts a carrier: WAIT.
            fn farm_wood_filter(view: &GameState, unit: &Unit, candidates: &mut Vec<Candidate>) {
                if unit.carry[WOOD] <= 0 {
                    return;
                }
                // Build resolution BR-7, in the two stages the two smoke reads between them
                // forced. **Stage 1 measures against every door**, so the distance function does
                // not move under the carrier's feet. **Stage 2 runs only if stage 1 admits
                // nothing**, and measures against the doors our OTHER troll is not standing on:
                // a drop cell occupied by our own troll is not a legal drop cell for this one --
                // `compatible` rejects the pair that names it -- so a carrier whose only
                // shortening step is the occupied one is otherwise stranded.
                //
                // Both stages exist because each cured what the other caused. With stage 2 alone
                // the door set changed as the other troll moved, the distance function moved with
                // it, and a full wood carrier shuttled (7,2)<->(6,2) for 9 turns without ever
                // dropping on m007 seat 1 (I-19/I-20/I-21). With stage 1 alone, troll 0 held 2
                // wood at (0,2) on m005 seat 0 while troll 2 sat on the one shortening door
                // (1,2), and the carrier WAITed for 137 turns (P4).
                let all_doors = Self::farm_doors(view);
                if all_doors.is_empty() {
                    return;
                }
                let free_doors: Vec<Cell> = all_doors
                    .iter()
                    .copied()
                    .filter(|cell| {
                        !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        })
                    })
                    .collect();
                let drop = format!("DROP {}", unit.id);
                let speed = unit.stats.movement_speed.max(1);
                let admissible = |doors: &Vec<Cell>, candidate: &Candidate| -> bool {
                    if candidate.command == drop {
                        return true;
                    }
                    if doors.is_empty() {
                        return false;
                    }
                    let to_doors = bfs_distances(&view.walkable, doors);
                    let Some(here) = to_doors.get(&unit.cell).copied() else {
                        return false;
                    };
                    let Some((_, target)) = MoisanBot::move_command(&candidate.command) else {
                        return false;
                    };
                    let next = next_cell(&view.walkable, unit.cell, target, speed);
                    match to_doors.get(&next) {
                        Some(distance) => *distance < here,
                        None => false,
                    }
                };
                let stage1: Vec<Candidate> = candidates
                    .iter()
                    .filter(|candidate| admissible(&all_doors, candidate))
                    .cloned()
                    .collect();
                let kept = if stage1.is_empty() {
                    candidates
                        .iter()
                        .filter(|candidate| admissible(&free_doors, candidate))
                        .cloned()
                        .collect()
                } else {
                    stage1
                };
                *candidates = kept;
                if candidates.is_empty() {
                    candidates.push(MoisanBot::wait());
                }
            }

            /// End of turn: remember what the ring looked like and what we told the referee, so
            /// the next turn can read the difference. The job map is updated from the EMITTED
            /// commands, never from what was merely offered.
            fn farm_snapshot(&mut self, view: &GameState, selected: &[String]) {
                let ring = Self::farm_ring_cells(view);
                self.farm_prev_ring = ring
                    .iter()
                    .filter_map(|cell| {
                        view.plant_at(*cell).map(|index| {
                            let plant = &view.plants[index];
                            (*cell, (plant.size, plant.health, plant.fruits))
                        })
                    })
                    .collect();
                self.farm_prev_enemy = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 1)
                    .map(|unit| unit.cell)
                    .collect();
                self.farm_prev_cmd = BTreeMap::new();
                for unit in view.units.iter().filter(|unit| unit.player == 0) {
                    let Some(command) = MoisanBot::command_for_unit(selected, unit.id) else {
                        self.farm_jobs.remove(&unit.id);
                        continue;
                    };
                    let job = self
                        .farm_offer
                        .get(&unit.id)
                        .and_then(|offers| {
                            offers
                                .iter()
                                .find(|(offered, _)| *offered == command)
                                .map(|(_, cell)| *cell)
                        });
                    self.farm_prev_cmd.insert(
                        unit.id,
                        (command.clone(), unit.cell, unit.stats.chop_power, job.is_some()),
                    );
                    if job.is_some() && command.starts_with("PICK ") {
                        self.farm_seeded.insert(unit.id);
                    }
                    match job {
                        Some(cell) => {
                            self.farm_jobs.insert(unit.id, cell);
                        }
                        None => {
                            self.farm_jobs.remove(&unit.id);
                        }
                    }
                }
                self.farm_offer = BTreeMap::new();
            }

'''

# ------------------------------------------------------- 4. the turn: observe, then transition
STEP_OLD = """                self.reconcile_regeneration_commitments(view);
                let mut keep_meta = KeepMeta::default();
"""
STEP_NEW = """                self.reconcile_regeneration_commitments(view);
                // The farm reads the referee's accepted effects for the turn and then takes its
                // one state decision, both before any candidate is built (packet §2.1, §4.5(5)).
                if MoisanBot::FARM_ENABLED {
                    self.farm_observe(view);
                    self.farm_step(view);
                }
                let mut keep_meta = KeepMeta::default();
"""

# ------------------------------------------------- 5. the offers and the W1 filter, per unit
OFFER_OLD = "                    by_id.insert(unit.id, candidates);\n"
OFFER_NEW = """                    if MoisanBot::FARM_ENABLED {
                        let offers = self.farm_offers(view, unit);
                        let offer_commands: BTreeSet<String> = offers
                            .iter()
                            .map(|(candidate, _)| candidate.command.clone())
                            .collect();
                        self.farm_offer.insert(
                            unit.id,
                            offers
                                .iter()
                                .map(|(candidate, cell)| (candidate.command.clone(), *cell))
                                .collect(),
                        );
                        candidates.extend(offers.into_iter().map(|(candidate, _)| candidate));
                        self.farm_seed_filter(unit, &offer_commands, &mut candidates);
                        // The mother guard before W1, so a carrier is still filtered last.
                        self.farm_mother_guard(view, &offer_commands, &mut candidates);
                        // W1 LAST, over the whole list: a carrier is filtered after every source
                        // has proposed, so no source can divert it.
                        Self::farm_wood_filter(view, unit, &mut candidates);
                    }
                    by_id.insert(unit.id, candidates);
"""

# --------------------------------------------------------------- 6. the wire: v6 becomes v8
WIRE_OLD = ('                let mut tokens: Vec<String> = '
            'vec![format!("NARRATE v6 t={}", view.turn)];\n')
WIRE_NEW = '''                let mut tokens: Vec<String> =
                    vec![format!("NARRATE v8 t={}", view.turn)];
                // §8: the nine farm tokens, FIRST — before every unit and every v6 token — so
                // that a truncated tail still brings the farm readout home. `fd`, `fE` and `fW`
                // carry the sentinel `-`, which means "not yet determined" and never zero.
                tokens.push(format!("fs={}", self.farm_state));
                tokens.push(format!("fp={}", self.farm_plants));
                tokens.push(format!("fh={}", self.farm_harvests));
                tokens.push(format!("fl={}", self.farm_latch));
                tokens.push(format!(
                    "fd={}",
                    match self.farm_deny_reason {
                        Some(reason) => reason.to_string(),
                        None => "-".to_string(),
                    }
                ));
                tokens.push(format!("fe={}", self.farm_fe));
                tokens.push(format!("fw={}", self.farm_fw));
                tokens.push(format!(
                    "fE={}",
                    match self.farm_fe_win {
                        Some(value) => value.to_string(),
                        None => "-".to_string(),
                    }
                ));
                tokens.push(format!(
                    "fW={}",
                    match self.farm_fw_win {
                        Some(value) => value.to_string(),
                        None => "-".to_string(),
                    }
                ));
'''

# ------------------------------------------------------------------ 7. the end-of-turn snapshot
SNAP_OLD = "                self.remember_selected_regeneration(&selected);\n"
SNAP_NEW = """                if MoisanBot::FARM_ENABLED {
                    self.farm_snapshot(view, &selected);
                }
                self.remember_selected_regeneration(&selected);
"""


def build_text(parent: str) -> str:
    text = parent
    text = replace_once(text, IMPORT_OLD, IMPORT_NEW, "types import")
    text = replace_once(text, FLAG_OLD, FLAG_NEW, "flag line")
    text = replace_once(text, STATE_OLD, STATE_NEW, "bot state")
    text = replace_once(text, INIT_OLD, INIT_NEW, "constructor")
    text = replace_once(text, FARM_ANCHOR, FARM_BLOCK + "            pub fn with_opening_policy",
                        "farm block")
    text = replace_once(text, STEP_OLD, STEP_NEW, "turn step")
    text = replace_once(text, OFFER_OLD, OFFER_NEW, "offers and W1")
    text = replace_once(text, WIRE_OLD, WIRE_NEW, "wire")
    text = replace_once(text, SNAP_OLD, SNAP_NEW, "snapshot")
    return text


def load_parent() -> str:
    parent = P.build_text(P.load_base())
    got = hashlib.sha256(parent.encode()).hexdigest()
    if got != PARENT_SHA:
        raise GenError(f"parent source is {got}, expected {PARENT_SHA} — refuse to guess")
    return parent


def main() -> int:
    parent = load_parent()
    text = build_text(parent)
    OUT.write_text(text)
    out_sha = hashlib.sha256(text.encode()).hexdigest()
    print(f"  parent claude_1/cure3/cure3-keep-v6.rs  sha256 {PARENT_SHA[:16]}  "
          f"{len(parent.splitlines())} lines")
    print(f"  source {OUT.relative_to(REPO)}  sha256 {out_sha[:16]}  {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
