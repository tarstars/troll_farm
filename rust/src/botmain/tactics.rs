//! Tactics layer (L1, R4): everything decided BEFORE any troll is looked at — the
//! turn-1 adaptive chopper spec, train gating, farm geometry/phase, and the seed
//! reserve. `Plan` is the explicit L1→L2 interface consumed by jobs::assign_all.
//! Bodies moved VERBATIM from decide_elite; equality enforced by the harness.
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Meta {
    Tempo,
    Scale,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Phase {
    Tempo,
    Hoard,
    Factory,
}

/// Scale meta: hoard (no felling, bank the wallet) until T_SWITCH, then the factory.
// Swept down per gatekeeper verdict #4 — hoarding until t=140 cedes the shared map to
// deforesting opponents (opp wood 60.1 vs our 23.2 avg, boss avg score delta -169.0): 100 =
// the design spec's sweep floor (docs/superpowers/specs/2026-07-07-last-mile-and-basin-jump-
// design.md, "Risks": T_SWITCH sweeps down to 120/100 if Hoard loses the early race
// unrecoverably). Note: SCALE_MIN_TURN stays [10, 40, 110] unchanged — slot 2 (the ladder's
// only chop-capable hand) now has its min-turn gate (110) ABOVE T_SWITCH (100), so it becomes
// eligible only after Factory has already begun. This is intentional: `ladder_funding`
// (planner.rs; renamed from `scale_funding` in v1.35.0-thand) keeps the funding bands elevated
// through a grace window scoped to `want_feeder`, not `phase == Phase::Hoard` alone, so the
// ladder's tail still gets funded priority even though it crosses the Hoard->Factory boundary —
// and, as of v1.35.0, the same grace window now also serves Tempo's own pending 3rd hand.
pub const T_SWITCH: i32 = 100;

pub fn phase_for(meta: Meta, turn: i32) -> Phase {
    match meta {
        Meta::Tempo => Phase::Tempo,
        Meta::Scale => {
            if turn < T_SWITCH {
                Phase::Hoard
            } else {
                Phase::Factory
            }
        }
    }
}

thread_local! {
    // v1.7.0: the chopper spec chosen ONCE at turn 1 from the starting draw.
    static GE_CHOSEN_SPEC: RefCell<Option<(i32, i32, i32, i32)>> = RefCell::new(None);
}

/// Turn-1 reset of the committed spec.
pub fn reset() {
    GE_CHOSEN_SPEC.with(|c| *c.borrow_mut() = None);
}

pub struct Plan {
    pub shack: Cell,
    /// MAP distances from the shack (BFS) — farm membership and chopper roam use THIS,
    /// not manhattan (user-found bug vs biz1: manhattan ignores water, so the starter
    /// planted "nearby" cells that were a long walk around a lake).
    pub farm_d: std::collections::HashMap<Cell, i32>,
    pub opp: Cell,
    pub have_iron: bool,
    pub turns_rem: i32,
    pub n: i32,
    pub farm_now: usize,
    pub nchop: i32,
    pub spec: (i32, i32, i32, i32),
    pub want_chopper: bool,
    pub want_feeder: bool,
    pub train_spec: (i32, i32, i32, i32),
    pub cost: [i32; 6],
    pub train_now: bool,
    pub need_iron: bool,
    pub need_fund: [bool; 3],
    pub farm_r: i32,
    pub farm_cap: usize,
    pub fell_size: i32,
    pub farm_fell: i32,
    pub chop_r: i32,
    pub starter_chop: bool,
    pub liquidation: bool,
    pub base_trees: usize,
    pub seed_cells: HashSet<Cell>,
    pub phase: Phase,
    /// v1.53.0-pressurefarm (Task 1 Step 3): the live ownership-pressure verdict, computed
    /// ONCE per turn below (never recomputed in planner.rs's per-troll hot loop). Under
    /// `PressureState::Green` this is always the all-zero/empty default and every
    /// pressure-gated behavior in planner.rs is a proven no-op (see
    /// tests/pressurefarm.rs::pressure_green_is_noop).
    pub pressure: ownership::Pressure,
    /// v1.54.0-frontdoor: the chosen "front door" cell when the shack straddles a
    /// detected chokepoint (see `compute_door`); `None` on every normal map — a proven
    /// no-op (tests/frontdoor.rs::frontdoor_open_map_noop).
    pub door: Option<Cell>,
    /// BFS distances from `door` (`Some` iff `door` is `Some`). `farm_eligible` uses
    /// THIS instead of `farm_d` at the farm/plant-membership sites exactly when a
    /// chokepoint override is active; every OTHER use of `farm_d` (banking-adjacency,
    /// chop-roam) is untouched.
    pub door_d: Option<HashMap<Cell, i32>>,
}

// ── FRONT-DOOR FARM PLACEMENT (v1.54.0-frontdoor) ───────────────────────────────────────
// `farm_d` above is a BFS SEEDED AT THE SHACK CELL: the shack is impassable to trolls (they
// can never stand on / re-enter it), but the BFS still treats it as a zero-cost hub, so
// cells on OPPOSITE sides of a shack that straddles a chokepoint (lake + boulders, e.g. the
// Sasso map) both read farm_d<=2 even when they are 20+ REAL walking steps apart — one
// connected component, a DISTANCE bug, not a connectivity one (user replay 895493013,
// confirmed: farm_d(14,4)=1 but real dist (12,4)->(14,4)=24). The farm/plant-membership
// filter then wrongly admits cells on BOTH sides, so the gatherer shuttles the full detour
// every trip (263/300 turns in transit, measured).
//
// Fix: `compute_door` detects the straddle (chokepoint-gated) and, ONLY then, picks a
// single "front door" — the shack's walkable neighbor farthest (true BFS distance) from
// the OPPONENT shack among candidates VIABLE enough to host a farm. `farm_eligible` then
// resolves farm/plant membership through the door's BFS instead of the shack-hub `farm_d`.
// On every normal (non-chokepoint) map `compute_door` returns `(None, None)` and
// `farm_eligible` reduces to exactly today's `farm_d.get(pos) <= r` — a proven no-op (see
// tests/frontdoor.rs::frontdoor_open_map_noop). `farm_d` keeps ALL its other uses
// (banking-adjacency `farm_d==1` in planner.rs's plant_cell chooser, chop-roam `chop_r`)
// untouched — only the farm/plant-membership sites route through `farm_eligible`.
pub const MIN_FARM_CELLS: usize = 4; // a candidate door must host at least this many walkable cells within GE_FARM_R to be VIABLE
pub const CHOKE_THRESHOLD: i32 = 8; // max true pairwise distance between door candidates before we call it a chokepoint (open maps: ~4 via the small detour around the shack; Sasso: 24)

/// Chokepoint-gated front-door selection. Returns `(None, None)` on every normal map:
/// fewer than 2 walkable shack-neighbors (nothing to straddle), every candidate mutually
/// close (`<= CHOKE_THRESHOLD`), or no candidate is VIABLE (>= `MIN_FARM_CELLS` walkable
/// cells within `GE_FARM_R`). Otherwise picks the viable candidate maximizing true BFS
/// distance from `state.opp_shack` (farthest-from-enemy — the enemy must travel farther to
/// raid our crops), tie-broken lexicographically on the cell.
///
/// Determinism: `candidates` is an explicit sorted `Vec` (never a HashSet iterated for
/// order); the viable list is explicitly sorted on `(-opp_dist, door_cell)` before picking
/// index 0 — the result depends only on map geometry, never on HashSet/HashMap internal
/// iteration order (see tests/frontdoor.rs::frontdoor_determinism_hashset_reorder).
pub fn compute_door(state: &State) -> (Option<Cell>, Option<HashMap<Cell, i32>>) {
    let shack = state.my_shack;
    let mut candidates: Vec<Cell> = ortho_neighbors(shack)
        .into_iter()
        .filter(|c| state.walkable.contains(c))
        .collect();
    candidates.sort();
    if candidates.len() < 2 {
        return (None, None); // nothing to straddle
    }

    let dds: Vec<(Cell, HashMap<Cell, i32>)> = candidates
        .iter()
        .map(|&c| (c, bfs_distances(&state.walkable, &[c])))
        .collect();

    let mut max_pair = 0;
    for i in 0..dds.len() {
        for j in (i + 1)..dds.len() {
            let dist = dds[i].1.get(&dds[j].0).copied().unwrap_or(i32::MAX / 2);
            max_pair = max_pair.max(dist);
        }
    }
    if max_pair <= CHOKE_THRESHOLD {
        return (None, None); // open map: no-op
    }

    let opp_d = bfs_distances(&state.walkable, &[state.opp_shack]);
    let mut viable: Vec<(Cell, i32)> = Vec::new();
    for (door, dd) in &dds {
        let count = state
            .walkable
            .iter()
            .filter(|c| dd.get(c).map_or(false, |&d| d <= GE_FARM_R))
            .count();
        if count >= MIN_FARM_CELLS {
            viable.push((*door, opp_d.get(door).copied().unwrap_or(0)));
        }
    }
    if viable.is_empty() {
        return (None, None); // no side can host a farm: fall back to plain farm_d
    }
    viable.sort_by_key(|&(door, od)| (-od, door));
    let chosen = viable[0].0;
    let chosen_d = dds.into_iter().find(|(c, _)| *c == chosen).map(|(_, d)| d);
    (Some(chosen), chosen_d)
}

/// Farm/plant-cell eligibility at radius `r`: `farm_d <= r` on every normal map (byte-
/// identical to the pre-frontdoor test); `door_d <= r` when a chokepoint override is
/// active. The only call sites this replaces are farm/plant-membership tests (tactics.rs
/// farm_now/base_trees below, planner.rs's plant_cell chooser) — NOT `farm_d==1` banking-
/// adjacency or `chop_r` roam, which keep consulting `farm_d` directly.
pub fn farm_eligible(
    farm_d: &HashMap<Cell, i32>,
    door_d: &Option<HashMap<Cell, i32>>,
    pos: Cell,
    r: i32,
) -> bool {
    match door_d {
        Some(dd) => dd.get(&pos).map_or(false, |&d| d <= r),
        None => farm_d.get(&pos).map_or(false, |&d| d <= r),
    }
}

fn plan_impl(state: &State, my: &[Troll], meta: Meta) -> Plan {
    let farm_d = bfs_distances(&state.walkable, &[state.my_shack]);
    let (door, door_d) = compute_door(state);
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
    let turns_rem = TOTAL_TURNS - state.turn + 1;

    let n = my.len() as i32;

    // ── training: ONE chopper, EARLY, spec ADAPTED to the starting draw (v1.7.0) ──
    // Denial > production (proven 2026-07-05): the chopper must train at turn 1 so we win
    // the shared-tree race. cc=3 captures 3 wood/tree but its lemon cost (n+9=10) only fits
    // a rich starting draw; cc=2 (lemon n+4=5) trains at t1 on nearly any draw. So pick the
    // RICHEST chopper the turn-1 inventory can train IMMEDIATELY — cc=3 when the draw affords
    // it (production), else cc=2 (denial) — NEVER delay waiting to afford cc=3.
    let spec = GE_CHOSEN_SPEC.with(|c| {
        let mut c = c.borrow_mut();
        if c.is_none() {
            // v1.9.0 (data-driven vs 32 real Boss-5 games): pick EACH axis independently to
            // level 3 iff the turn-1 draw's binding resource already affords it — ms<-plum,
            // cc<-lemon, chop<-iron (each level-3 costs n+9). This (a) FIXES the v1.7.0 bug
            // where a plum/iron shortfall wrongly locked cc2 on a lemon-rich map (cc3 vs cc2
            // differ ONLY in lemon), and (b) adopts Boss 5's ms=3/chop=3 flexibility (faster
            // travel + faster felling = the sustained-throughput lever it beats us on). An axis
            // upgrades only when its resource is ALREADY >= n+9, so it never delays training
            // beyond the cc2 baseline (the upgrade is "free"). hp=0 (can't harvest, cheap).
            // ms/cc/chop upgrade to 3 when their resource is free (>=n+9), else 2. (v1.14.0's cc1
            // tier on lemon-poor maps was WORSE: 0/5 wood 40 — cc1 throughput too low even with
            // the tight farm's cheap banking. A late cc2 beats an early cc1.)
            let lvl = |res: usize| if inv[res] >= n + 9 { 3 } else { 2 };
            *c = Some((lvl(PLUM), lvl(LEMON), 0, lvl(IRON)));
        }
        c.unwrap()
    });
    let farm_now = state
        .trees
        .iter()
        .filter(|p| farm_eligible(&farm_d, &door_d, p.pos(), GE_FARM_R))
        .count();
    // v1.11.0: troll 2 = the CHOPPER (early, adaptive spec). troll 3 = a FEEDER (late): a cheap
    // hp>0/chop=0 harvester. Because decide_elite routes any chop<2 troll through the STARTER
    // (printer) branch, the feeder auto-plants bananas — a 2nd pair of hands keeping the farm
    // DENSE so the single chopper never travels/idles (travel is ~2.5x the felling = the real
    // Boss-5 throughput gap). This is the runninglvlan structure (starter+feeder+chopper) and
    // AVOIDS the 2-chopper starvation (validated: a 2nd chopper starves the 1-feeder farm).
    let nchop = my.iter().filter(|u| u.chop_power >= 2).count() as i32;
    // B2 (Scale ladder): under Meta::Scale, replace the adaptive chopper-training logic with a
    // FIXED HAND ladder — want_chopper forced false (the early adaptive t1 chopper is REPLACED
    // by the ladder itself: its final slot trains a real chopper `(2,2,0,2)` once n reaches 3
    // hands, gated at t>=110; Hoard banks the wallet with hands only before that). Troll count n
    // selects the next hand's spec/turn-gate from
    // SCALE_LADDER/SCALE_MIN_TURN, mapped onto the SAME Plan fields the Tempo path uses
    // (want_feeder/train_spec/cost/train_now/need_iron/need_fund) so planner.rs needs no new
    // fields — it already reads want_feeder to drive funding/printer work. The Tempo branch
    // below is BYTE-IDENTICAL to the pre-B2 code (equality-critical: GE_META stays Tempo live).
    let (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund) = if meta
        == Meta::Scale
    {
        const SCALE_LADDER: [(i32, i32, i32, i32); 3] = [(1, 1, 1, 0), (1, 1, 1, 0), (2, 2, 0, 2)];
        const SCALE_MIN_TURN: [i32; 3] = [10, 40, 110];
        let slot = ((n - 1).max(0) as usize).min(2);
        let want_hand = n < 4 && state.turn >= SCALE_MIN_TURN[slot];
        let want_chopper = false;
        let want_feeder = want_hand;
        let train_spec = SCALE_LADDER[slot];
        let cost = training_cost(n, train_spec);
        let train_now = want_hand && mb_afford(inv, &cost, have_iron);
        // B2.1 gatekeeper fix: accumulate iron EARLY (all of Hoard), not only once slot 2 is
        // reached at t>=110 — 7 = the slot-2 chopper's iron cost (n=3 + chop^2=4). Iron income
        // is otherwise zero (nothing mines it) and the map's starting stock rarely reaches 7 by
        // t110, so the wallet must be pre-filled during Hoard or the ladder's only chop-capable
        // hand never trains (wood=0 the entire game, confirmed 12/12 in the gatekeeper report).
        let need_iron = have_iron && inv[IRON] < 7;
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];
        (
            want_chopper,
            want_feeder,
            train_spec,
            cost,
            train_now,
            need_iron,
            need_fund,
        )
    } else {
        let want_chopper = nchop == 0 && (state.turn >= GE_CHOP_DELAY || farm_now >= GE_CHOP_FARM);
        let want_feeder = nchop >= 1
            && n < GE_MAX_TROLLS
            && state.turn >= GE_FEEDER_T
            && farm_now >= GE_FEEDER_FARM;
        let train_spec = if want_chopper { spec } else { GE_FEEDER_SPEC };
        let cost = training_cost(n, train_spec);
        let train_now = (want_chopper || want_feeder) && mb_afford(inv, &cost, have_iron);
        let want_chopper = want_chopper; // (kept: need_iron/need_fund below key off the pending hand)
                                         // iron-gated: fruit is ready but we still lack the iron for the PENDING HAND — the
                                         // chopper OR the feeder. T-hand.1 (gatekeeper v1.35.0 verdict, fix a): this used to be
                                         // want_chopper-only, so iron mining stopped FOREVER the instant the chopper trained,
                                         // permanently starving any later pending hand of its flat cost[IRON]=n training cost
                                         // (every spec carries it) on every iron-bearing map — 12/12 sampled by the gatekeeper.
        let need_iron = have_iron
            && (want_chopper || want_feeder)
            && inv[IRON] < cost[IRON]
            && afford_fruit_only(inv, &cost);
        // which fruit types still block the pending hand (funding targets)
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];
        (
            want_chopper,
            want_feeder,
            train_spec,
            cost,
            train_now,
            need_iron,
            need_fund,
        )
    };

    // ── farm config ─────────────────────────────────────────────────────────
    // v1.18.0: TURN-1 ADAPTIVE ECONOMY (committed via the draw-chosen spec, no mid-game switch).
    // High-draw map (spec chose cc>=3): economy B = BIG farm + size-3 fells (cc3 captures 3, chop3
    // fells size-3 in 2 chops; the cc3 banks-every-3 offsets the bigger farm's longer trips) — the
    // Boss-5 throughput economy. Low-draw map (cc2): economy A = the TIGHT farm (short bank trips,
    // fast size-2 maturation) that beats Boss 5 ~40%. Best of both, per the felling mechanics.
    let phase = phase_for(meta, state.turn);
    let econ_b = false; // econ B (big-farm size-3) arena-validated WORSE (135 vs 120) — the big farm cannot sustain size-3 maturation; pure tight-farm (A) is best
    let farm_r = if econ_b { 3 } else { GE_FARM_R };
    // B3 (Factory): once the Scale meta reaches Factory (post-T_SWITCH), the hoard-built wallet
    // funds a bigger farm — 20 slots instead of 12 — so the plant-and-fell loop has room to grow
    // with the trained hand ladder. Hoard/Tempo are unchanged (econ_b is a permanent `false`, so
    // they fall through to GE_FARM_MAX=12).
    let farm_cap = if phase == Phase::Factory {
        20
    } else if econ_b {
        20
    } else {
        GE_FARM_MAX
    };
    let fell_size = GE_FELL_SIZE; // NATIVE/contested trees: always size-2 = DENIAL
    let farm_fell = if econ_b { 3 } else { 2 }; // OUR farm bananas: size-3 in econ B, size-2 in A
    let chop_r = if econ_b { 10 } else { GE_CHOP_R }; // econ B roams a bigger farm; A stays tight
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state
        .trees
        .iter()
        .filter(|p| farm_eligible(&farm_d, &door_d, p.pos(), farm_r))
        .count();

    // ── SEED SUSTAINABILITY (arena deforestation fix) ───────────────────────
    // Trees only fruit at MAX_SIZE(4); felling farm bananas at size 2 means they
    // NEVER fruit, so the seed supply drains -> the farm dies -> our half
    // deforests -> both trolls park (the decoded arena stall). Fix: keep the K
    // most-mature farm bananas as a permanent seed reserve the chopper won't
    // fell — they ripen, fruit, and the starter harvests their fruit for seeds.
    let mut seed_cells: HashSet<Cell> = HashSet::new();
    if GE_SEED_RESERVE > 0 && !liquidation {
        let mut fb: Vec<&Tree> = state
            .trees
            .iter()
            .filter(|p| {
                p.tree_type == "BANANA" && farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r)
            })
            .collect();
        fb.sort_by_key(|p| (-p.size, -p.fruits, manhattan(p.pos(), shack), p.pos()));
        for p in fb.into_iter().take(GE_SEED_RESERVE) {
            seed_cells.insert(p.pos());
        }
    }

    let provisional = Plan {
        shack,
        farm_d,
        opp,
        have_iron,
        turns_rem,
        n,
        farm_now,
        nchop,
        spec,
        want_chopper,
        want_feeder,
        train_spec,
        cost,
        train_now,
        need_iron,
        need_fund,
        farm_r,
        farm_cap,
        fell_size,
        farm_fell,
        chop_r,
        starter_chop,
        liquidation,
        base_trees,
        seed_cells,
        phase,
        pressure: ownership::Pressure::default(),
        door,
        door_d,
    };

    // ── PRESSURE GOVERNOR (v1.53.0-pressurefarm, Task 1 Step 2) ─────────────
    // ownership::assess only reads provisional.farm_d/farm_r/seed_cells (all already final
    // above) — the placeholder `pressure` field on `provisional` is never read by it, so
    // computing against the provisional Plan and overlaying the real pressure (plus its one
    // derived override, farm_cap) afterward is equality-safe. Computed exactly ONCE per
    // turn here — never inside planner.rs's per-troll candidates() hot loop.
    let pressure = ownership::assess(state, &provisional);
    // Task 2 Step 1 (dynamic farm cap): Orange+ pressure suppresses further expansion, but
    // NEVER below a small survival floor — a farm already at/under the floor keeps planting
    // regardless (the `.min` only ever shrinks the CEILING, it can't force liquidation). This
    // keeps Green/Yellow byte-identical (provisional.farm_cap is returned unchanged) and
    // avoids the "always smaller farm" static-control trap: the clamp only engages when
    // pressure is actually observed.
    //
    // Code review C2 (2026-07-09): re-gated from `>= Yellow` to `>= Orange`. Yellow only
    // requires `own_half_exposed > 0` (created_exposed == 0) — a signal that lights up from
    // static map geometry (any own-half tree we can't PROVE decisively ours) and is
    // near-permanent from ~turn 5 on real maps, independent of any real threat to farm value
    // WE created. Gating the clamp there collapsed farm_cap 12->4 for essentially the whole
    // game — exactly the "always smaller farm" nerf the paragraph above warns against, and a
    // throughput crater (dense-farm-never-idle is this bot's whole economic thesis). Orange
    // requires `created_exposed > 0` — a created/local farm tree the ownership model itself
    // marks not-safely-ours — which IS threat-discriminating (it needs the opponent's ETA to
    // actually contest a tree WE planted), matching this feature's own design intent (see
    // docs/pressure-aware-farm.md Task 0 Step 3, "Yellow: … pause expansion ONLY IF
    // created/local value exists") and data/analysis/map-value-ownership/report.md's
    // recommended trigger.
    //
    // Factory latent note (M1): under Phase::Factory the champion raises farm_cap to 20
    // (see the `phase == Phase::Factory` branch above); this clamp would override that down
    // to GE_PRESSURE_FARM_FLOOR if Orange+ pressure ever fires during Factory. Dormant today
    // (GE_META=Tempo, Factory unreachable) — flagged, not handled; no logic added here.
    let farm_cap = if pressure.state >= ownership::PressureState::Orange {
        provisional.farm_cap.min(GE_PRESSURE_FARM_FLOOR)
    } else {
        provisional.farm_cap
    };

    Plan {
        farm_cap,
        pressure,
        ..provisional
    }
}

pub fn plan(state: &State, my: &[Troll]) -> Plan {
    plan_impl(state, my, super::GE_META)
}

/// Test-only seam: drive `plan_impl` under an explicit `Meta` instead of the compile-time
/// `GE_META` const. Plain `pub` (not `cfg(test)`) because integration tests in `rust/tests/`
/// compile as a separate crate and can't see `cfg(test)` items; this is dead code in the arena
/// build, which the crate's `#![allow(dead_code, unused)]` already tolerates, and the bundler
/// carries it harmlessly (submission size gate is on the minified bytes, not source LOC).
pub fn plan_with_meta(state: &State, my: &[Troll], meta: Meta) -> Plan {
    plan_impl(state, my, meta)
}
