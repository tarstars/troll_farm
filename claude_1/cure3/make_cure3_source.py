#!/usr/bin/env python3
"""Generate the ONE source of task `20260826-candidate-3-keep-your-goal` from the champion.

Packet of record: `claude_1/cure3/g0-candidate-3-2026-08-26-r6.md` — r5 as amended by r6 C1-C5,
returned **ACCEPT-WITH-EDIT** by codex_1 at `20260826T122017Z`, the edit applied as C5. There is
no r7 (owner bound `121330Z`).

Base: `readable/door1-champion.rs` at `origin/main` — 2,210 lines, sha256 `ad1ae4ef…`. Every line
anchor in the packet was written against that blob; this script refuses any other base.

Three arms come from this one file and ONE flag line (`build_arms3.py`):

  instrument  KEEP=true  NARRATE=true   the G-1 read; can never be champion
  candidate   KEEP=true  NARRATE=false  the score block, and the ladder if the panel passes
  ruleoff     KEEP=false NARRATE=true   the containment reference (§9.1)

Every edit is an ANCHORED replacement that must match exactly once; if the base moves, this
script stops rather than producing a plausible file.

## Construction notes the G-1 report must carry (they are NOT in the packet)

Each is a place where the packet's letter has no referent in the base, found while implementing
it. Each is implemented in the way that keeps the packet's intent, and each is named here rather
than absorbed silently.

F4 — **`Shack` has no `impossible` test.** §3.4 says the goal cell for `Target::Shack` is
`view.shacks[0]`. That cell is **never** in `view.walkable`: `parse_static_map` (`:328-355`)
inserts only `'.'` cells, and the shack is `'0'`. The literal test therefore fires for every
`Shack` goal on the turn after it is recorded, releasing a goal that is perfectly live. The
neighbour form (`ortho_neighbors(shacks[0]) ∩ walkable` reachable) is no better: the `Shack`
candidate is emitted **only** when no such cell is reachable (`bank_candidates`, `:590-623`), so
that test also fires exactly when the goal is live. `Shack` is therefore implemented with **no**
`impossible` test — it ends on `done` (`total_carried() == 0`) or `dead`, both of which are
reachable and bounded.

F5 — **§5.3's `xj` fallback clause is unreachable.** "if the unrestricted maximisation has no pair
either, `xj=0` and the turn is in `xn=`" cannot happen: `L|g ⊆ L`, so the restricted product is a
subset of the unrestricted product, and a restricted pair existing implies an unrestricted pair
exists. `xj` is emitted 0 there and `xn` counts contests only.

F6 — **`k=1` is widened from "valid but not live" to "holds a valid goal whose emitted command
does not carry it".** §5.1's three values do not cover a live-restricted unit whose command
`resolve_move_conflicts` rewrote into something no candidate proposed; that unit keeps a valid
goal, so `k=0` is wrong, and `k=2` claims the command carried the goal when it did not.

F7 — **`rt` is producer-independent.** §3.3's `rt` row is worded against "the unit's producer this
turn", but §1(a) runs every release test **before any candidate is built**, so no producer is
known yet. Implemented as the row's own predicate (`plant.kind != kind`, `:714`) evaluated against
the goal's **own** kind — the kind of the plant at `c` when the goal was recorded, carried in
`kept_kinds`. This fires exactly when the tree at `c` was replaced by one of another kind.

F8 — **`last_carried` and `last_inventory` are not implemented.** §3 lists them in the one-turn
snapshot, but none of the four predicates as written reads either: `done` reads the *current*
`free_capacity()`/`total_carried()`, and `gone` for `Cell(c)` reads the current `carried_fruit`.
Carrying two unread fields would be exactly the inert check this programme has paid for.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASE = REPO / "readable" / "door1-champion.rs"
BASE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"
OUT = HERE / "cure3-keep-v6.rs"


class GenError(Exception):
    """Fail closed: a generator that guesses produces a file nobody can review."""


def replace_once(text: str, old: str, new: str, what: str) -> str:
    n = text.count(old)
    if n != 1:
        raise GenError(f"anchor {what!r} occurs {n} times, expected exactly 1")
    return text.replace(old, new, 1)


# --------------------------------------------------------------------------- A. the flag block
FLAGS_OLD = "        impl MoisanBot {\n"
FLAGS_NEW = '''        impl MoisanBot {
            // ---------------------------------------------------------------- Candidate 3
            // Task 20260826-candidate-3-keep-your-goal. Packet of record:
            // claude_1/cure3/g0-candidate-3-2026-08-26-r6.md (r5 as amended by r6 C1-C5),
            // ACCEPT-WITH-EDIT by codex_1 20260826T122017Z; the owner's bound forbids an r7.
            //
            // R5, in four steps run inside `commands()` and nowhere else:
            //   (a) release  -- four world predicates, order dead / gone / impossible / done
            //   (b) restrict -- L|g, order preserved; never adds a candidate, never scores
            //   (c) decide   -- the champion's `select` over the restricted lists; a turn the
            //                   restriction makes undecidable releases the YOUNGER goal
            //   (d) record   -- goalless units only, exact string match against the pre-
            //                   restriction list L
            //
            // No margin and no constant of any kind appears in the rule.
            //
            // `build_arms3.py` rewrites exactly the line below to make the three arms, and
            // nothing else differs between them.
            const KEEP_RULE_ENABLED: bool = true; const NARRATE_V6_ENABLED: bool = true;
            // Ruled at G-0 and NOT a knob: a Tree goal is done on CHOP *or* HARVEST at the cell
            // with the carry full (r5 F1, ruled `true` by codex_1 20260826T122017Z).
            const DONE_ON_HARVEST: bool = true;
            // `ERASE_WHEN_NOT_LIVE` is ruled FALSE (coordinator Ruling 2) and is therefore not a
            // constant here: a valid goal that no candidate carries this turn is preserved and
            // unrestricting, and the `true` arm is code nothing would ever execute.
'''

# --------------------------------------------------------------------------- B. KeepMeta
META_OLD = "        struct MoisanBot;\n"
META_NEW = '''        // The v6 per-turn census. Every field here is a REQUIRED field on the wire; the
        // decoder `claude_1/narrate6/narrate6.py` asserts at import that no field of the grammar
        // is without a consumer and no consumed field is off the grammar (r6 C3).
        #[derive(Clone, Debug, Default)]
        struct KeepMeta {
            kp: u32,
            kq: u32,
            kl: u32,
            kr: u32,
            rd: u32,
            rg: u32,
            ri: u32,
            rx: u32,
            rf: u32,
            rt: u32,
            ro: u32,
            nl: u32,
            nl_producer: u32,
            nl_door: u32,
            nl_admissibility: u32,
            nl_other: u32,
            ka: u32,
            kc: u32,
            xc: u32,
            xw: u32,
            xn: u32,
            xp: u32,
            xg: u32,
            xd: u32,
            xj: u32,
        }
        struct MoisanBot;
'''

# --------------------------------------------------------------------------- C. bot state
STATE_OLD = "            regeneration_commitments: BTreeMap<i32, PlantKind>,\n            opponent_eta_penalty: i32,\n        }\n"
STATE_NEW = '''            regeneration_commitments: BTreeMap<i32, PlantKind>,
            opponent_eta_penalty: i32,
            // Candidate 3. One remembered goal per own troll, its birth turn, and the kind of
            // the plant that stood at a Tree goal when it was recorded (the `rt` release, F7).
            // The one-turn snapshot is the emitted command line and the cell the unit stood on
            // when it emitted it -- `CHOP`/`HARVEST` carry no cell of their own (`:893`, `:707`).
            kept_goals: BTreeMap<i32, Target>,
            kept_since: BTreeMap<i32, i32>,
            kept_kinds: BTreeMap<i32, PlantKind>,
            last_command: BTreeMap<i32, String>,
            last_cell: BTreeMap<i32, Cell>,
        }
'''

INIT_OLD = "                    regeneration_commitments: BTreeMap::new(),\n                    opponent_eta_penalty: 0,\n                }\n"
INIT_NEW = '''                    regeneration_commitments: BTreeMap::new(),
                    opponent_eta_penalty: 0,
                    kept_goals: BTreeMap::new(),
                    kept_since: BTreeMap::new(),
                    kept_kinds: BTreeMap::new(),
                    last_command: BTreeMap::new(),
                    last_cell: BTreeMap::new(),
                }
'''


# ------------------------------------------------------- E. the resolver, instrumented only
# The v4/v5 branch alphabet, carried into v6 unchanged: P primary . L lateral/improving detour .
# R regressive detour . W forced WAIT . N no MOVE this turn. `H` (Candidate 1's hold) and
# `S`/`X` (Candidate 2's exchange) have no writer in a Candidate 3 arm and are off this arm's
# grammar. Everything added below is a READ: `granted`, `waiting_cells`, `d_cur` and `d_detour`
# are never consulted by a branch that assigns a command, so the instrumented resolver returns
# the champion's commands on every input.
RESOLVER_OLD = """            fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                Self::resolve_move_conflicts_with_priority(view, commands, &BTreeSet::new());
            }
            fn resolve_move_conflicts_with_priority(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
            ) {
                Self::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    commands,
                    priority_ids,
                    &BTreeSet::new(),
                );
            }
"""
RESOLVER_NEW = """            fn resolve_move_conflicts(
                view: &GameState,
                commands: &mut [String],
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                Self::resolve_move_conflicts_with_priority(
                    view,
                    commands,
                    &BTreeSet::new(),
                    branch,
                    w_collisions,
                );
            }
            fn resolve_move_conflicts_with_priority(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                Self::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    commands,
                    priority_ids,
                    &BTreeSet::new(),
                    branch,
                    w_collisions,
                );
            }
"""

RESOLVER_BODY_OLD = """            fn resolve_move_conflicts_with_priority_and_forbidden(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
            ) {
                let command_by_id: BTreeMap<i32, usize> = commands"""
RESOLVER_BODY_NEW = """            fn resolve_move_conflicts_with_priority_and_forbidden(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
                branch: &mut BTreeMap<i32, char>,
                w_collisions: &mut u32,
            ) {
                let mut granted: BTreeSet<Cell> = BTreeSet::new();
                let mut waiting_cells: BTreeSet<Cell> = BTreeSet::new();
                let command_by_id: BTreeMap<i32, usize> = commands"""

# the two WAIT-writing sites and the two MOVE-writing sites, each tagged with its branch code
W_SELF_OLD = """                for (_, index, current, _, landing) in &projections {
                    if landing == current {
                        commands[*index] = "WAIT".to_string();
                    }
                }"""
W_SELF_NEW = """                for (id, index, current, _, landing) in &projections {
                    if landing == current {
                        commands[*index] = "WAIT".to_string();
                        // A self-targeting MOVE resolved to WAIT is W. Its cell is reserved
                        // already: the unit is not in `moving_ids`.
                        branch.insert(*id, 'W');
                    }
                }"""

PRIMARY_OLD = """                    if !landing_forbidden && !reserved.contains(&landing) {
                        reserved.insert(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                        continue;
                    }"""
PRIMARY_NEW = """                    if !landing_forbidden && !reserved.contains(&landing) {
                        reserved.insert(landing);
                        granted.insert(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                        branch.insert(id, 'P');
                        continue;
                    }"""

DETOUR_OLD = """                    commands[index] = if let Some(cell) = detour {
                        reserved.insert(cell);
                        format!("MOVE {} {} {}", id, cell.0, cell.1)
                    } else {
                        "WAIT".to_string()
                    };
                }
            }"""
DETOUR_NEW = """                    // `d_cur` uses the detour key's OWN fallback, or L and R would be decided
                    // by comparing two different metrics.
                    let d_cur = toward_goal
                        .get(&unit.cell)
                        .copied()
                        .unwrap_or_else(|| manhattan(unit.cell, target));
                    commands[index] = if let Some(cell) = detour {
                        let d_detour = toward_goal
                            .get(&cell)
                            .copied()
                            .unwrap_or_else(|| manhattan(cell, target));
                        reserved.insert(cell);
                        granted.insert(cell);
                        branch.insert(id, if d_detour <= d_cur { 'L' } else { 'R' });
                        format!("MOVE {} {} {}", id, cell.0, cell.1)
                    } else {
                        waiting_cells.insert(unit.cell);
                        branch.insert(id, 'W');
                        "WAIT".to_string()
                    };
                }
                *w_collisions = waiting_cells
                    .iter()
                    .filter(|cell| granted.contains(cell))
                    .count() as u32;
            }"""


# --------------------------------------------------------------- F. the rule and the narrator
RULE_ANCHOR = "        impl Bot for YamoBot {\n"
RULE_BLOCK = '''        // ------------------------------------------------------------ Candidate 3 helpers
        impl MoisanBot {
            // The champion's two-unit joint maximisation (`select`, `:952-972`) lifted verbatim,
            // so the restricted decision and the unrestricted reference `xj` compares it against
            // are literally the same code. The only addition is that the winning sum comes back.
            fn best_pair(
                a_list: &[Candidate],
                b_list: &[Candidate],
                inventory: &[i32; 6],
            ) -> Option<(String, String, f64)> {
                let mut best_score = f64::NEG_INFINITY;
                let mut best = None;
                for a in a_list {
                    for b in b_list {
                        if !Self::compatible(a.target, b.target)
                            || !Self::stock_compatible(a, b, inventory)
                        {
                            continue;
                        }
                        let score = a.score + b.score;
                        if score > best_score {
                            best_score = score;
                            best = Some((a.command.clone(), b.command.clone(), score));
                        }
                    }
                }
                best
            }
            fn best_score(list: &[Candidate]) -> Option<f64> {
                list.iter().map(|candidate| candidate.score).max_by(f64::total_cmp)
            }
            // Basis points given up, floored toward zero and saturating at 999_999: a saturated
            // value is decode-visible and reads as "at least 100x", never as a measurement.
            fn give_up_bps(free: f64, kept: f64) -> u32 {
                if !(kept > 0.0) || !(free > kept) {
                    return 0;
                }
                let raw = (10_000.0 * (free - kept) / kept).floor();
                if !raw.is_finite() || raw >= 999_999.0 {
                    return 999_999;
                }
                if raw <= 0.0 {
                    0
                } else {
                    raw as u32
                }
            }
            // Ids are parsed exactly as `remember_selected_regeneration` (`:1702-1715`) parses
            // them, so the two recording steps cannot disagree about whose command is whose.
            fn command_for_unit(commands: &[String], id: i32) -> Option<String> {
                commands
                    .iter()
                    .find(|command| {
                        let fields: Vec<&str> = command.split_whitespace().collect();
                        fields.len() >= 2 && fields[1].parse::<i32>().map_or(false, |v| v == id)
                    })
                    .cloned()
            }
            // The exact-match rule of R5(d)/§6, used for BOTH the recording and the narrator's
            // `chosen` column so the two cannot disagree: exactly one match, or several agreeing
            // on the target, gives that target; differing targets or no match give `None`.
            fn matched_target(list: &[Candidate], command: &str) -> Option<Target> {
                let targets: Vec<Target> = list
                    .iter()
                    .filter(|candidate| candidate.command == command)
                    .map(|candidate| candidate.target)
                    .collect();
                let first = targets.first().copied()?;
                if targets.iter().any(|target| *target != first) {
                    return None;
                }
                Some(first)
            }
        }
        // ------------------------------------------------------------------- Candidate 3, R5
        impl YamoBot {
            // ---- R5(a) release ---------------------------------------------------------------
            // Runs immediately after `reconcile_regeneration_commitments` and BEFORE any candidate
            // is built, so a kept goal restricts ZERO turns after its invalidating event becomes
            // observable. Order is fixed -- dead, gone, impossible, done -- and the first to fire
            // wins, so the census sums exactly and no turn is double-counted.
            fn release_kept_goals(&mut self, view: &GameState, meta: &mut KeepMeta) {
                let held: Vec<i32> = self.kept_goals.keys().copied().collect();
                for id in held {
                    let Some(goal) = self.kept_goals.get(&id).copied() else {
                        continue;
                    };
                    let alive = view
                        .units
                        .iter()
                        .find(|unit| unit.player == 0 && unit.id == id);
                    let Some(unit) = alive else {
                        self.forget_goal(id);
                        meta.rx += 1;
                        meta.kr += 1;
                        continue;
                    };
                    if let Some(cause) = self.gone_cause(view, unit, goal) {
                        match cause {
                            'f' => meta.rf += 1,
                            't' => meta.rt += 1,
                            'o' => meta.ro += 1,
                            // r6 C1: the Bank cause has NO sub-count. It is asserted structurally
                            // unreachable and `rf + rt + ro == rg` is the falsifier for that
                            // assertion -- strictly better than an always-zero `rw=`, which would
                            // read as a passing check.
                            _ => {}
                        }
                        self.forget_goal(id);
                        meta.rg += 1;
                        meta.kr += 1;
                        continue;
                    }
                    if Self::goal_impossible(view, unit, goal) {
                        self.forget_goal(id);
                        meta.ri += 1;
                        meta.kr += 1;
                        continue;
                    }
                    if self.goal_done(view, unit, goal) {
                        self.forget_goal(id);
                        meta.rd += 1;
                        meta.kr += 1;
                    }
                }
            }
            fn forget_goal(&mut self, id: i32) {
                self.kept_goals.remove(&id);
                self.kept_since.remove(&id);
                self.kept_kinds.remove(&id);
            }
            fn gone_cause(&self, view: &GameState, unit: &Unit, goal: Target) -> Option<char> {
                match goal {
                    Target::Tree(cell) => match view.plant_at(cell) {
                        None => Some('f'),
                        Some(index) => {
                            let plant = &view.plants[index];
                            if plant.health <= 0 {
                                Some('f')
                            } else if self
                                .kept_kinds
                                .get(&unit.id)
                                .map_or(false, |kind| *kind != plant.kind)
                            {
                                // F7: §3.3's `rt` row is worded against "the unit's producer this
                                // turn", but no producer has run yet at release time. The row's own
                                // predicate (`plant.kind != kind`, `:714`) is evaluated against the
                                // goal's OWN kind instead -- the kind that stood at `c` when the
                                // goal was recorded.
                                Some('t')
                            } else {
                                None
                            }
                        }
                    },
                    // F3/C1: no accepts or fullness predicate exists anywhere on the DROP path
                    // (`:596-611`), so the walkable test is the whole cause -- and it is
                    // structurally unreachable, bank cells being
                    // `ortho_neighbors(shacks[0]) INTERSECT walkable` by construction (`:592-594`).
                    Target::Bank(cell) => {
                        if view.walkable.contains(&cell) {
                            None
                        } else {
                            Some('b')
                        }
                    }
                    Target::Cell(cell) => {
                        let taken = view.plant_at(cell).is_some()
                            && !self
                                .last_command
                                .get(&unit.id)
                                .map_or(false, |command| command.starts_with("PLANT "));
                        let no_fruit = Self::carried_fruit(unit).is_none()
                            && !self.regeneration_commitments.contains_key(&unit.id);
                        if !view.walkable.contains(&cell) || taken || no_fruit {
                            Some('o')
                        } else {
                            None
                        }
                    }
                    Target::Shack | Target::None => None,
                }
            }
            fn goal_impossible(view: &GameState, unit: &Unit, goal: Target) -> bool {
                // F4: `Shack` gets NO impossible test. §3.4 names `shacks[0]` as its goal cell,
                // but that cell is never in `view.walkable` (`parse_static_map`, `:328-355`, adds
                // only `.` cells and the shack is `0`), so the literal test would release every
                // `Shack` goal one turn after it is recorded; and the neighbour form fires exactly
                // when the goal is live, since the `Shack` candidate is emitted ONLY when no bank
                // cell is reachable (`:590-623`). `Shack` ends on `done` or `dead`, both reachable.
                let cell = match goal {
                    Target::Tree(cell) | Target::Bank(cell) | Target::Cell(cell) => cell,
                    Target::Shack | Target::None => return false,
                };
                // The champion's own BFS walks `view.walkable`, a static map-derived set that
                // never removes an occupied cell, so a standing teammate is never an
                // impossibility -- it is the exchange rule's business, exactly as the charter says.
                !bfs_distances(&view.walkable, &[unit.cell]).contains_key(&cell)
            }
            fn goal_done(&self, view: &GameState, unit: &Unit, goal: Target) -> bool {
                let last = match self.last_command.get(&unit.id) {
                    Some(command) => command.as_str(),
                    None => "",
                };
                let at = self.last_cell.get(&unit.id).copied();
                match goal {
                    // The capacity middle. NOT the first chop: a single swing is progress toward
                    // the goal, and releasing on it is the champion's re-pick, which is the loop's
                    // mechanism. Done is "the goal has yielded everything this troll can take".
                    Target::Tree(cell) => {
                        let worked = last == format!("CHOP {}", unit.id)
                            || (MoisanBot::DONE_ON_HARVEST
                                && last == format!("HARVEST {}", unit.id));
                        worked && at == Some(cell) && unit.free_capacity() <= 0
                    }
                    Target::Bank(cell) => last == format!("DROP {}", unit.id) && at == Some(cell),
                    Target::Cell(cell) => {
                        view.plant_at(cell).is_some()
                            && last.starts_with(&format!("PLANT {} ", unit.id))
                    }
                    Target::Shack => unit.total_carried() == 0,
                    Target::None => true,
                }
            }
'''

RULE_BLOCK += '''            // ---- R5(b) restrict and R5(c) decide ---------------------------------------------
            // Returns the commands and the ids that were live-restricted on the FIRST pass -- the
            // set `k=2` is read against. `L|g` is a subset of `L`, so the rule can never cause a
            // command the champion did not offer this turn.
            fn select_keeping(
                &mut self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                inventory: &[i32; 6],
                door_cleared: &BTreeSet<i32>,
                meta: &mut KeepMeta,
            ) -> (Vec<String>, BTreeSet<i32>) {
                let mut first_pass = true;
                let mut restricted: BTreeSet<i32> = BTreeSet::new();
                loop {
                    let mut live: BTreeSet<i32> = BTreeSet::new();
                    let mut effective: BTreeMap<i32, Vec<Candidate>> = BTreeMap::new();
                    for (id, list) in by_id {
                        let kept: Vec<Candidate> = match self.kept_goals.get(id) {
                            // Order preserved: `L|g` is a filter of `L`, never a re-sort.
                            Some(goal) => list
                                .iter()
                                .filter(|candidate| candidate.target == *goal)
                                .cloned()
                                .collect(),
                            None => Vec::new(),
                        };
                        if kept.is_empty() {
                            // Not live. The goal is NOT erased: `ERASE_WHEN_NOT_LIVE` is false.
                            effective.insert(*id, list.clone());
                        } else {
                            live.insert(*id);
                            effective.insert(*id, kept);
                        }
                    }
                    if first_pass {
                        self.census_entry(view, by_id, &effective, &live, door_cleared, meta);
                        restricted = live.clone();
                        first_pass = false;
                    }
                    // R5(c) first sentence, and the containment theorem: with nothing
                    // live-restricted the champion's `select` runs UNMODIFIED and no step below
                    // executes.
                    if live.is_empty() {
                        return (MoisanBot::select(by_id.clone(), inventory), restricted);
                    }
                    let ids: Vec<i32> = effective.keys().copied().collect();
                    if ids.len() == 1 {
                        // §4.1. `max_by` returns the LAST maximal element, so ties are decided by
                        // list order exactly as in the champion. No contest is possible here.
                        let best = effective[&ids[0]]
                            .iter()
                            .max_by(|a, b| a.score.total_cmp(&b.score))
                            .expect("a live-restricted list is non-empty by construction");
                        return (vec![best.command.clone()], restricted);
                    }
                    if ids.len() == 2 {
                        let (a, b) = (ids[0], ids[1]);
                        let both = live.contains(&a) && live.contains(&b);
                        if let Some((first, second, sum)) =
                            MoisanBot::best_pair(&effective[&a], &effective[&b], inventory)
                        {
                            if both {
                                // §5.3. `xj` is r3's `rho` turned from a threshold into a price
                                // tag: what the joint decision gave up against the unrestricted
                                // maximisation of the SAME turn. F5: the `None` arm is unreachable
                                // -- `L|g` is a subset of `L`, so a restricted pair existing
                                // implies an unrestricted pair exists. It is not a measurement.
                                meta.xj = match MoisanBot::best_pair(&by_id[&a], &by_id[&b], inventory)
                                {
                                    Some((_, _, free)) => MoisanBot::give_up_bps(free, sum),
                                    None => 0,
                                };
                            }
                            return (vec![first, second], restricted);
                        }
                        if both {
                            // §4.3, the contest. The YOUNGER goal is released -- never both, never
                            // to a score, and the elder is untouched. At most one release per
                            // troll per turn, so this terminates.
                            let younger = self.younger_of(a, b);
                            self.forget_goal(younger);
                            meta.xc += 1;
                            meta.kr += 1;
                            continue;
                        }
                        // §4.2(b). One restricted, no joint pair, and no second goal to release,
                        // so the decision is phased -- and THE KEPT TROLL IS NEVER THE ONE THAT
                        // WAITS. The partner's forced `wait()` is the rule's real cost, counted
                        // `xw` and bounded by one turn: the partner holds no goal to carry.
                        let keeper = if live.contains(&a) { a } else { b };
                        let partner = if keeper == a { b } else { a };
                        let chosen = effective[&keeper]
                            .iter()
                            .max_by(|x, y| x.score.total_cmp(&y.score))
                            .expect("a live-restricted list is non-empty by construction")
                            .clone();
                        let mut partner_list = effective[&partner].clone();
                        partner_list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let taken = partner_list.into_iter().find(|candidate| {
                            MoisanBot::compatible(candidate.target, chosen.target)
                                && MoisanBot::stock_compatible(&chosen, candidate, inventory)
                        });
                        let partner_command = match taken {
                            Some(candidate) => candidate.command,
                            None => {
                                // Counted only when the partner's FULL list held something other
                                // than a `WAIT`, so champion-native waits and the door-clearance
                                // `wait()` are never charged to the rule.
                                if by_id[&partner]
                                    .iter()
                                    .any(|candidate| candidate.command != "WAIT")
                                {
                                    meta.xw += 1;
                                }
                                MoisanBot::wait().command
                            }
                        };
                        meta.xp += 1;
                        let commands = if keeper == a {
                            vec![chosen.command, partner_command]
                        } else {
                            vec![partner_command, chosen.command]
                        };
                        return (commands, restricted);
                    }
                    // §4.4, the `>= 3` path, two phases. Phase 2 cannot un-assign phase 1.
                    let mut used_targets: Vec<Target> = Vec::new();
                    let mut used_stock = [0; 6];
                    let mut assigned: BTreeMap<i32, String> = BTreeMap::new();
                    let mut phase1: Vec<i32> = live.iter().copied().collect();
                    phase1.sort_by_key(|id| {
                        (self.kept_since.get(id).copied().unwrap_or(i32::MAX), *id)
                    });
                    let mut collided: Vec<i32> = Vec::new();
                    for id in phase1 {
                        let mut list = effective[&id].clone();
                        list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let pick = list.into_iter().find(|candidate| {
                            used_targets
                                .iter()
                                .all(|target| MoisanBot::compatible(candidate.target, *target))
                                && MoisanBot::picked_item(&candidate.command)
                                    .map(|item| used_stock[item] < inventory[item])
                                    .unwrap_or(true)
                        });
                        match pick {
                            Some(candidate) => {
                                used_targets.push(candidate.target);
                                if let Some(item) = MoisanBot::picked_item(&candidate.command) {
                                    used_stock[item] += 1;
                                }
                                assigned.insert(id, candidate.command);
                            }
                            None => {
                                collided.push(id);
                                meta.xc += 1;
                                meta.xg += 1;
                                meta.kr += 1;
                            }
                        }
                    }
                    for id in &collided {
                        self.forget_goal(*id);
                    }
                    // Phase 2 IS the champion's greedy loop -- ascending id, full lists, the same
                    // accumulated sets -- run against what phase 1 already took.
                    let mut commands: Vec<String> = Vec::new();
                    for id in &ids {
                        if let Some(command) = assigned.get(id) {
                            commands.push(command.clone());
                            continue;
                        }
                        let mut list = by_id[id].clone();
                        list.sort_by(|x, y| y.score.total_cmp(&x.score));
                        let pick = list.into_iter().find(|candidate| {
                            used_targets
                                .iter()
                                .all(|target| MoisanBot::compatible(candidate.target, *target))
                                && MoisanBot::picked_item(&candidate.command)
                                    .map(|item| used_stock[item] < inventory[item])
                                    .unwrap_or(true)
                        });
                        let chosen = match pick {
                            Some(candidate) => candidate,
                            None => {
                                if by_id[id]
                                    .iter()
                                    .any(|candidate| candidate.command != "WAIT")
                                {
                                    meta.xw += 1;
                                }
                                MoisanBot::wait()
                            }
                        };
                        used_targets.push(chosen.target);
                        if let Some(item) = MoisanBot::picked_item(&chosen.command) {
                            used_stock[item] += 1;
                        }
                        commands.push(chosen.command);
                    }
                    return (commands, restricted);
                }
            }
            fn younger_of(&self, a: i32, b: i32) -> i32 {
                let key = |id: i32| (self.kept_since.get(&id).copied().unwrap_or(i32::MIN), id);
                if key(a) > key(b) {
                    a
                } else {
                    b
                }
            }
'''

RULE_BLOCK += '''            // ---- the census, taken on the FIRST pass -----------------------------------------
            // A unit whose goal is released as contested was live-restricted when it entered, so
            // it stays in `kq`; `kp == kq + kl` is exact.
            fn census_entry(
                &self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                effective: &BTreeMap<i32, Vec<Candidate>>,
                live: &BTreeSet<i32>,
                door_cleared: &BTreeSet<i32>,
                meta: &mut KeepMeta,
            ) {
                for (id, goal) in &self.kept_goals {
                    if !by_id.contains_key(id) {
                        continue;
                    }
                    meta.kp += 1;
                    let age = view.turn - self.kept_since.get(id).copied().unwrap_or(view.turn);
                    if age > 0 {
                        meta.ka = meta.ka.max(age as u32);
                    }
                    if live.contains(id) {
                        meta.kq += 1;
                        // §5.3 `xd`: the per-troll price tag. Units whose kept score is not
                        // positive are excluded and counted in `kq` only.
                        meta.xd = meta.xd.max(MoisanBot::give_up_bps(
                            MoisanBot::best_score(&by_id[id]).unwrap_or(0.0),
                            MoisanBot::best_score(&effective[id]).unwrap_or(0.0),
                        ));
                    } else {
                        meta.kl += 1;
                        meta.nl += 1;
                        match self.not_live_cause(view, *id, *goal, &by_id[id], door_cleared) {
                            'p' => meta.nl_producer += 1,
                            'd' => meta.nl_door += 1,
                            'a' => meta.nl_admissibility += 1,
                            _ => meta.nl_other += 1,
                        }
                    }
                }
            }
            // The four not-live causes of §2, in a fixed priority order, each read off what the
            // turn actually produced rather than re-derived from which branch ran. A non-zero
            // `nl_other` is a FINDING for the packet under §9.10, not a decode error: the causes
            // are a claim about the base and `nl_other` is how that claim is falsified.
            fn not_live_cause(
                &self,
                view: &GameState,
                id: i32,
                goal: Target,
                list: &[Candidate],
                door_cleared: &BTreeSet<i32>,
            ) -> char {
                // Case 3. `force_unique_door_clear` REPLACES a unit's whole list, and R5(b) runs
                // after it, so door clearance is never outvoted by a kept goal.
                if door_cleared.contains(&id) {
                    return 'd';
                }
                // Case 1, the residual walk-back's own counter. The producer chosen this turn
                // routes a carrying unit to bank candidates only (`:1936-1939`, `:1779-1782`), so
                // no Tree or Cell goal can be offered at all.
                if !list.is_empty()
                    && list
                        .iter()
                        .all(|candidate| matches!(candidate.target, Target::Bank(_) | Target::Shack))
                {
                    return 'p';
                }
                // Case 4. The goal's tree is alive AND reachable -- `gone` and `impossible` both
                // ran first and did not fire -- yet no candidate carries it. `chop_candidates`
                // filters on health, reachability and endgame admissibility only (`:859-882`), and
                // the first two are excluded here, so admissibility is the only cause left.
                if let Target::Tree(cell) = goal {
                    if let Some(index) = view.plant_at(cell) {
                        if view.plants[index].health > 0 {
                            return 'a';
                        }
                    }
                }
                'o'
            }
            // `kc`: turns the rule holds a troll on a tree it is already chopping -- where it is
            // inert, since the champion scores that same CHOP at the top of its own list.
            fn chop_holds(&self, commands: &[String]) -> u32 {
                self.kept_goals
                    .iter()
                    .filter(|(id, goal)| {
                        matches!(goal, Target::Tree(_))
                            && MoisanBot::command_for_unit(commands, **id)
                                .map_or(false, |command| command == format!("CHOP {}", id))
                    })
                    .count() as u32
            }
            // ---- R5(d) record, and the one-turn snapshot the release tests read next turn -----
            // Only units that entered the selector WITHOUT a valid kept goal -- including a unit
            // whose goal was released as contested this turn -- take one. Erasure on ambiguity is
            // the safe direction: a missing kept goal costs one turn of preference, a wrong one is
            // a preference for something the troll is not doing.
            fn record_kept_goals(
                &mut self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                commands: &[String],
            ) {
                for (id, list) in by_id {
                    let Some(unit) = view
                        .units
                        .iter()
                        .find(|unit| unit.player == 0 && unit.id == *id)
                    else {
                        continue;
                    };
                    // The snapshot and the recording read the SAME final emitted line, so `done`
                    // and the record can never disagree about what the unit did.
                    let emitted = MoisanBot::command_for_unit(commands, *id);
                    match &emitted {
                        Some(command) => {
                            self.last_command.insert(*id, command.clone());
                            self.last_cell.insert(*id, unit.cell);
                        }
                        None => {
                            self.last_command.remove(id);
                            self.last_cell.remove(id);
                        }
                    }
                    if self.kept_goals.contains_key(id) {
                        continue;
                    }
                    let Some(command) = emitted else {
                        continue;
                    };
                    let Some(target) = MoisanBot::matched_target(list, &command) else {
                        continue;
                    };
                    if target == Target::None {
                        continue;
                    }
                    self.kept_goals.insert(*id, target);
                    self.kept_since.insert(*id, view.turn);
                    if let Target::Tree(cell) = target {
                        if let Some(index) = view.plant_at(cell) {
                            self.kept_kinds.insert(*id, view.plants[index].kind);
                        }
                    }
                }
                let alive: BTreeSet<i32> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                self.last_command.retain(|id, _| alive.contains(id));
                self.last_cell.retain(|id, _| alive.contains(id));
            }
            // ---- the v6 wire -----------------------------------------------------------------
            // Reads only. Nothing here decides anything. v6 is v5's payload with `m=` deleted --
            // there is no margin constant to disambiguate a wire with, which is itself the
            // version's signature -- plus the three-valued `k=` and the keep census.
            fn narrate_target(target: Target) -> String {
                match target {
                    Target::None => "NONE".to_string(),
                    Target::Shack => "SHACK".to_string(),
                    Target::Bank(cell) => format!("BANK({},{})", cell.0, cell.1),
                    Target::Cell(cell) => format!("CELL({},{})", cell.0, cell.1),
                    Target::Tree(cell) => format!("TREE({},{})", cell.0, cell.1),
                }
            }
            // `k=2` restricted AND the emitted command carried the kept goal; `k=1` the unit holds
            // a valid kept goal whose emitted command does not carry it -- the not-live case, and
            // (F6) the case where `resolve_move_conflicts` rewrote a restricted command into
            // something no candidate proposed; `k=0` no valid kept goal, including a goal released
            // as contested this turn, which is why `xc` and `k` are read together and never apart.
            fn keep_code(
                &self,
                id: i32,
                goal_lists: &BTreeMap<i32, Vec<Candidate>>,
                restricted: &BTreeSet<i32>,
                commands: &[String],
            ) -> char {
                let Some(goal) = self.kept_goals.get(&id) else {
                    return '0';
                };
                if restricted.contains(&id) {
                    if let Some(command) = MoisanBot::command_for_unit(commands, id) {
                        let carried = goal_lists
                            .get(&id)
                            .map_or(false, |list| {
                                list.iter().any(|candidate| {
                                    candidate.command == command && candidate.target == *goal
                                })
                            });
                        if carried {
                            return '2';
                        }
                    }
                }
                '1'
            }
            fn narrate_message(
                &self,
                view: &GameState,
                by_id: &BTreeMap<i32, Vec<Candidate>>,
                restricted: &BTreeSet<i32>,
                commands: &[String],
                branch: &BTreeMap<i32, char>,
                meta: &KeepMeta,
                w_collisions: u32,
                banner: Option<&str>,
            ) -> String {
                // Every live own unit exactly once, ids ascending, roster taken from the VIEW.
                let mut ids: Vec<i32> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.id)
                    .collect();
                ids.sort();
                let mut tokens: Vec<String> = vec![format!("NARRATE v6 t={}", view.turn)];
                for id in ids {
                    let chosen = MoisanBot::command_for_unit(commands, id)
                        .and_then(|command| {
                            by_id
                                .get(&id)
                                .and_then(|list| MoisanBot::matched_target(list, &command))
                        })
                        .unwrap_or(Target::None);
                    let want = match by_id.get(&id) {
                        Some(list) => match list
                            .iter()
                            .max_by(|a, b| a.score.total_cmp(&b.score))
                        {
                            Some(candidate) => Self::narrate_target(candidate.target),
                            None => "ABSENT".to_string(),
                        },
                        None => "ABSENT".to_string(),
                    };
                    let code = branch.get(&id).copied().unwrap_or('N');
                    // `b=` is v4's `blocked_turns`, kept in the shape for the decoder's benefit
                    // and identically 0: Candidate 1's hold was its only writer and it is retired.
                    tokens.push(format!(
                        "u{}={}/{}/r={}/b=0/k={}",
                        id,
                        Self::narrate_target(chosen),
                        want,
                        code,
                        self.keep_code(id, by_id, restricted, commands)
                    ));
                }
                // `pz=1`, `sp=0` and the four exchange counters have no writer in a Candidate 3
                // arm: R5 adds no holder and there is no exchange rule here. They are carried with
                // v5's meanings unchanged (r6 C4) and a violation is a defect in R5.
                tokens.push("pz=1".to_string());
                tokens.push("sp=0".to_string());
                tokens.push(format!("wc={}", w_collisions));
                tokens.push("sw=0".to_string());
                tokens.push("so=0".to_string());
                tokens.push("sn=0".to_string());
                tokens.push("sf=0".to_string());
                tokens.push(format!("kp={}", meta.kp));
                tokens.push(format!("kq={}", meta.kq));
                tokens.push(format!("kl={}", meta.kl));
                tokens.push(format!("kr={}", meta.kr));
                tokens.push(format!("rd={}", meta.rd));
                tokens.push(format!("rg={}", meta.rg));
                tokens.push(format!("ri={}", meta.ri));
                tokens.push(format!("rx={}", meta.rx));
                tokens.push(format!("rf={}", meta.rf));
                tokens.push(format!("rt={}", meta.rt));
                tokens.push(format!("ro={}", meta.ro));
                tokens.push(format!("nl={}", meta.nl));
                tokens.push(format!("nl_producer={}", meta.nl_producer));
                tokens.push(format!("nl_door={}", meta.nl_door));
                tokens.push(format!("nl_admissibility={}", meta.nl_admissibility));
                tokens.push(format!("nl_other={}", meta.nl_other));
                tokens.push(format!("ka={}", meta.ka));
                tokens.push(format!("kc={}", meta.kc));
                tokens.push(format!("xc={}", meta.xc));
                tokens.push(format!("xw={}", meta.xw));
                tokens.push(format!("xn={}", meta.xn));
                tokens.push(format!("xp={}", meta.xp));
                tokens.push(format!("xg={}", meta.xg));
                tokens.push(format!("xd={}", meta.xd));
                tokens.push(format!("xj={}", meta.xj));
                let body = tokens.join(" ");
                match banner {
                    Some(text) => format!("MSG {} {}", text, body),
                    None => format!("MSG {}", body),
                }
            }
        }
'''


# ------------------------------------------------------------------ G. commands(), rewired
RELEASE_OLD = """            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_regeneration_commitments(view);
"""
RELEASE_NEW = """            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.reconcile_regeneration_commitments(view);
                let mut keep_meta = KeepMeta::default();
                // R5(a). Before any candidate is built, so a kept goal restricts zero turns after
                // its invalidating event becomes observable.
                if MoisanBot::KEEP_RULE_ENABLED {
                    self.release_kept_goals(view, &mut keep_meta);
                }
"""

BANNER_OLD = """                let mut out = Vec::new();
                if !self.announced {
                    self.announced = true;
                    out.push(format!("MSG {}", self.announcement));
                }
"""
BANNER_NEW = """                let mut out = Vec::new();
                let narrate_banner = if !self.announced {
                    self.announced = true;
                    if !MoisanBot::NARRATE_V6_ENABLED {
                        out.push(format!("MSG {}", self.announcement));
                    }
                    Some(self.announcement)
                } else {
                    None
                };
"""

TAIL_OLD = """                if self.door_unblocking {
                    self.force_unique_door_clear(view, &mut by_id);
                }
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                MoisanBot::resolve_move_conflicts(view, &mut selected);
                self.remember_selected_regeneration(&selected);
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                out
            }"""
TAIL_NEW = """                // Which units the door clearance REPLACED the list of, read off the bytes rather
                // than re-derived: `nl_door` is a claim about this call and nothing else.
                let mut door_cleared: BTreeSet<i32> = BTreeSet::new();
                if self.door_unblocking {
                    let before: BTreeMap<i32, Vec<String>> = by_id
                        .iter()
                        .map(|(id, list)| {
                            (*id, list.iter().map(|c| c.command.clone()).collect())
                        })
                        .collect();
                    self.force_unique_door_clear(view, &mut by_id);
                    for (id, list) in &by_id {
                        let after: Vec<String> =
                            list.iter().map(|c| c.command.clone()).collect();
                        if before.get(id) != Some(&after) {
                            door_cleared.insert(*id);
                        }
                    }
                }
                // R5(b) and (c) run AFTER `force_unique_door_clear` -- so door clearance cannot be
                // outvoted by a kept goal -- and BEFORE `select`, because the preference is only
                // correct inside the maximisation.
                let mut restricted: BTreeSet<i32> = BTreeSet::new();
                let mut selected = if MoisanBot::KEEP_RULE_ENABLED {
                    let (commands, live) = self.select_keeping(
                        view,
                        &by_id,
                        &view.inventories[0],
                        &door_cleared,
                        &mut keep_meta,
                    );
                    restricted = live;
                    commands
                } else {
                    MoisanBot::select(by_id.clone(), &view.inventories[0])
                };
                let mut narrate_branch: BTreeMap<i32, char> = BTreeMap::new();
                let mut w_collisions = 0;
                MoisanBot::resolve_move_conflicts(
                    view,
                    &mut selected,
                    &mut narrate_branch,
                    &mut w_collisions,
                );
                if keep_meta.xc > 0 {
                    keep_meta.xn = 1;
                }
                if MoisanBot::KEEP_RULE_ENABLED {
                    keep_meta.kc = self.chop_holds(&selected);
                }
                let narration = if MoisanBot::NARRATE_V6_ENABLED {
                    Some(self.narrate_message(
                        view,
                        &by_id,
                        &restricted,
                        &selected,
                        &narrate_branch,
                        &keep_meta,
                        w_collisions,
                        narrate_banner,
                    ))
                } else {
                    None
                };
                // R5(d) LAST, and against the final emitted line -- never against `select`'s
                // output, which `resolve_move_conflicts` may have rewritten.
                if MoisanBot::KEEP_RULE_ENABLED {
                    self.record_kept_goals(view, &by_id, &selected);
                }
                self.remember_selected_regeneration(&selected);
                out.extend(selected);
                // The empty-check runs on the GAMEPLAY tokens alone, so the payload can never
                // suppress the base's WAIT.
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                if let Some(payload) = narration {
                    // Exactly one MSG per turn, FIRST in the list.
                    out.insert(0, payload);
                }
                out
            }"""


def main() -> int:
    base = BASE.read_text()
    sha = hashlib.sha256(base.encode()).hexdigest()
    if sha != BASE_SHA:
        raise GenError(f"base {BASE} is {sha}, expected {BASE_SHA} — refuse to guess")
    text = base
    text = replace_once(text, FLAGS_OLD, FLAGS_NEW, "flag block")
    text = replace_once(text, META_OLD, META_NEW, "KeepMeta")
    text = replace_once(text, STATE_OLD, STATE_NEW, "bot state")
    text = replace_once(text, INIT_OLD, INIT_NEW, "constructor")
    text = replace_once(text, RESOLVER_OLD, RESOLVER_NEW, "resolver entry point")
    text = replace_once(text, RESOLVER_BODY_OLD, RESOLVER_BODY_NEW, "resolver body")
    text = replace_once(text, W_SELF_OLD, W_SELF_NEW, "self-target WAIT")
    text = replace_once(text, PRIMARY_OLD, PRIMARY_NEW, "primary grant")
    text = replace_once(text, DETOUR_OLD, DETOUR_NEW, "detour")
    text = replace_once(text, RULE_ANCHOR, RULE_BLOCK + RULE_ANCHOR, "rule block")
    text = replace_once(text, RELEASE_OLD, RELEASE_NEW, "release call")
    text = replace_once(text, BANNER_OLD, BANNER_NEW, "banner")
    text = replace_once(text, TAIL_OLD, TAIL_NEW, "commands tail")
    OUT.write_text(text)
    out_sha = hashlib.sha256(text.encode()).hexdigest()
    print(f"  base   {BASE.relative_to(REPO)}  sha256 {sha[:16]}  {len(base.splitlines())} lines")
    print(f"  source {OUT.relative_to(REPO)}  sha256 {out_sha[:16]}  {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
