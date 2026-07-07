//! Tactics layer (L1, R4): everything decided BEFORE any troll is looked at — the
//! turn-1 adaptive chopper spec, train gating, farm geometry/phase, and the seed
//! reserve. `Plan` is the explicit L1→L2 interface consumed by jobs::assign_all.
//! Bodies moved VERBATIM from decide_elite; equality enforced by the harness.
use super::*;
use std::cell::RefCell;
use std::collections::HashSet;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Meta { Tempo, Scale }

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Phase { Tempo, Hoard, Factory }

/// Scale meta: hoard (no felling, bank the wallet) until T_SWITCH, then the factory.
pub const T_SWITCH: i32 = 140;

pub fn phase_for(meta: Meta, turn: i32) -> Phase {
    match meta {
        Meta::Tempo => Phase::Tempo,
        Meta::Scale => {
            if turn < T_SWITCH { Phase::Hoard } else { Phase::Factory }
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
}

pub fn plan(state: &State, my: &[Troll]) -> Plan {
    let farm_d = bfs_distances(&state.walkable, &[state.my_shack]);
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
        .filter(|p| farm_d.get(&p.pos()).map_or(false, |&d| d <= GE_FARM_R))
        .count();
    // v1.11.0: troll 2 = the CHOPPER (early, adaptive spec). troll 3 = a FEEDER (late): a cheap
    // hp>0/chop=0 harvester. Because decide_elite routes any chop<2 troll through the STARTER
    // (printer) branch, the feeder auto-plants bananas — a 2nd pair of hands keeping the farm
    // DENSE so the single chopper never travels/idles (travel is ~2.5x the felling = the real
    // Boss-5 throughput gap). This is the runninglvlan structure (starter+feeder+chopper) and
    // AVOIDS the 2-chopper starvation (validated: a 2nd chopper starves the 1-feeder farm).
    let nchop = my.iter().filter(|u| u.chop_power >= 2).count() as i32;
    let want_chopper =
        nchop == 0 && (state.turn >= GE_CHOP_DELAY || farm_now >= GE_CHOP_FARM);
    let want_feeder = nchop >= 1
        && n < GE_MAX_TROLLS
        && state.turn >= GE_FEEDER_T
        && farm_now >= GE_FEEDER_FARM;
    let train_spec = if want_chopper { spec } else { GE_FEEDER_SPEC };
    let cost = training_cost(n, train_spec);
    let train_now = (want_chopper || want_feeder) && mb_afford(inv, &cost, have_iron);
    let want_chopper = want_chopper; // (kept: need_iron/need_fund below key off the chopper train)
    // iron-gated: fruit is ready but we still lack the iron for the chopper.
    let need_iron =
        have_iron && want_chopper && inv[IRON] < cost[IRON] && afford_fruit_only(inv, &cost);
    // which fruit types still block the chopper (funding targets)
    let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];

    // ── farm config ─────────────────────────────────────────────────────────
    // v1.18.0: TURN-1 ADAPTIVE ECONOMY (committed via the draw-chosen spec, no mid-game switch).
    // High-draw map (spec chose cc>=3): economy B = BIG farm + size-3 fells (cc3 captures 3, chop3
    // fells size-3 in 2 chops; the cc3 banks-every-3 offsets the bigger farm's longer trips) — the
    // Boss-5 throughput economy. Low-draw map (cc2): economy A = the TIGHT farm (short bank trips,
    // fast size-2 maturation) that beats Boss 5 ~40%. Best of both, per the felling mechanics.
    let econ_b = false; // econ B (big-farm size-3) arena-validated WORSE (135 vs 120) — the big farm cannot sustain size-3 maturation; pure tight-farm (A) is best
    let farm_r = if econ_b { 3 } else { GE_FARM_R };
    let farm_cap = if econ_b { 20 } else { GE_FARM_MAX };
    let fell_size = GE_FELL_SIZE; // NATIVE/contested trees: always size-2 = DENIAL
    let farm_fell = if econ_b { 3 } else { 2 }; // OUR farm bananas: size-3 in econ B, size-2 in A
    let chop_r = if econ_b { 10 } else { GE_CHOP_R }; // econ B roams a bigger farm; A stays tight
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state.trees.iter().filter(|p| farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r)).count();

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
            .filter(|p| p.tree_type == "BANANA" && farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r))
            .collect();
        fb.sort_by_key(|p| (-p.size, -p.fruits, manhattan(p.pos(), shack), p.pos()));
        for p in fb.into_iter().take(GE_SEED_RESERVE) {
            seed_cells.insert(p.pos());
        }
    }

    let phase = phase_for(super::GE_META, state.turn);
    Plan {
        shack, farm_d, opp, have_iron, turns_rem, n, farm_now, nchop, spec, want_chopper,
        want_feeder, train_spec, cost, train_now, need_iron, need_fund, farm_r, farm_cap,
        fell_size, farm_fell, chop_r, starter_chop, liquidation, base_trees, seed_cells,
        phase,
    }
}
