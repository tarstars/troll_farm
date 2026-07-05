//! RHEA — rolling-horizon evolutionary search over task plans (the user's
//! "trajectory pool" design): keep a pool of per-troll task plans, mutate,
//! evaluate by forward-simulating H turns with the exact fast engine
//! (game/fast.rs, O(1) pathing), keep the best, act on its first move.
//! Time-boxed anytime loop (~35 ms/turn; 500 ms on turn 1).
use std::cell::RefCell;
use std::time::Instant;

use super::Strategy;
use crate::game::fast::{cid, FAct, FCmds, FastState, NavTable, MAXC, MAXU};
use crate::game::state::GameState;

const H: usize = 40; // rollout horizon (turns)
const PLAN_LEN: usize = 3; // tasks per troll in a plan

#[derive(Clone, Copy, PartialEq)]
enum Task {
    Auto,          // follow the baseline policy
    GoTree(u8),    // plant list index at ROOT (chop or harvest depending on troll)
    GoBank,
    GoMine,
    PlantHere(u8), // fruit type: walk to base free cell and plant
}

#[derive(Clone, Copy)]
struct Plan {
    tasks: [[Task; PLAN_LEN]; MAXU],
}

impl Default for Plan {
    fn default() -> Self {
        Plan { tasks: [[Task::Auto; PLAN_LEN]; MAXU] }
    }
}

pub struct RheaBot {
    nav: RefCell<Option<Box<NavTable>>>,
    best: RefCell<Plan>,
    rng: RefCell<u64>,
    // anti-stall watchdog: troll id -> (x, y, same-pos streak while MOVEing)
    lastpos: RefCell<std::collections::HashMap<i32, (i8, i8, u8)>>,
}

impl RheaBot {
    pub fn new() -> Self {
        RheaBot {
            nav: RefCell::new(None),
            best: RefCell::new(Plan::default()),
            rng: RefCell::new(0x9E3779B97F4A7C15),
            lastpos: RefCell::new(std::collections::HashMap::new()),
        }
    }
    fn rand(&self) -> u64 {
        let mut r = self.rng.borrow_mut();
        *r ^= *r << 13;
        *r ^= *r >> 7;
        *r ^= *r << 17;
        *r
    }
}

fn envi(name: &str, d: i64) -> i64 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(d)
}
fn envf(name: &str, d: f64) -> f64 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(d)
}

// Evolved schedbot constants (Monte-Carlo searched; see sched_bot.rs) baked
// into the baseline policy — no env reads in the hot path.
const FB: f64 = 0.654; // fell-vs-bank anchor rate (SB_FB)
const PRINT_V: f64 = 8.36; // future value of one planted base seed (SB_PRINT)
const ORCH_V: f64 = 10.0; // value of a plum-orchard slot (SB_ORCH_V)
const RETW: f64 = 0.592; // harvest return-leg weight (SB_RETW)
const LIQ_T: i32 = 189; // turns_rem <= this -> liquidation fells (SB_LIQ_T)
const WF_MAX: i32 = 13; // base-tree cap for the printer (SB_WF_MAX)
const MOW_R: i32 = 4; // mow radius around own shack (SB_MOW_R)
const CROP_RES: i16 = 8; // plum/apple bank reserve before planting them (SB_CROP_RES)
const BASE_R: i32 = 3; // base radius for print/orchard/census (SB_BASE_R)
const ORCH_N: usize = 2; // max plum trees near base (SB_ORCH_N)

// ── wood-economy tuning (this bot's rewrite) ─────────────────────────────────
// The 2-troll wood economy is the champion (starter printer/funder + ONE cc2
// perma-chopper). More trolls dilute; the eval's troll term drove 4-troll fruit
// play that banks ~4x less wood than goldelite. Cap at 2.
const MAX_TROLLS: usize = 2;
// A REAL chopper (chop>=2) fells at WOOD THROUGHPUT (points/turn), which
// dominates fruit-harvest rates (~1.9) so it commits to banking wood instead of
// idling/harvesting. DENIAL_W biases the fell target toward CONTESTED (near-opp)
// trees. The game is a scorched-earth RACE for a shared, finite tree pool —
// grabbing the opponent's easy trees first wins (sim: 40%->67% vs goldelite). The
// bias is additive+bounded (max DENIAL_W/2), so `wood/t` still penalizes distance:
// it prefers contested trees but never treks blindly to a far one.
const DENIAL_W: f64 = 8.0;
// Additive priority for FUNDING the chopper (gather its training fruit + iron).
// Large so it dominates the rate market until the cc2 chopper is affordable —
// the old market never mined iron, so the chopper was never trained.
const FUND_RATE: f64 = 50.0;

/// Baseline per-troll policy on FastState — a port of the FULL evolved
/// schedbot cascade (sched_bot.rs), expressed as a per-troll rate market:
/// every candidate task gets a marginal rate (points/turn) and the troll takes
/// the argmax (deterministic tie-break: first candidate in schedbot's order).
/// Tasks: BANK (full-load rate + endgame override), FELL (FB denial metric
/// until the liquidation flip at turns_rem<=LIQ_T, then pure yield; LATE_FREE
/// capacity gate), MOW (chop-capable non-chopper on own-base fruitless trees),
/// HARVEST (deficit-weighted by the next troll's (1,1,1,0) cost), ORCHARD
/// (carried plum -> water base cell) and PRINT (pick+plant crops at base;
/// species follows the spot). Used for the opponent model and for Task::Auto
/// trolls in rollouts and at emit time.
fn policy_act(s: &FastState, nav: &NavTable, pl: usize, ui: usize, turns_rem: i32, reserved: &mut [bool; MAXC]) -> FAct {
    // tunable knobs (env-overridable for sweeps; cheap under policy-only play)
    let denial_w = envf("RH_DENIAL", DENIAL_W);
    let farm_cap = envi("RH_FARM", WF_MAX as i64) as i32;
    let w = s.w;
    let me = cid(s.u_x[ui], s.u_y[ui], w);
    let free = s.free(ui);
    let carried: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
    let sh = s.shack[pl];
    let osh = s.shack[1 - pl];
    let shc = cid(sh.0, sh.1, w);
    // nearest walkable drop cell
    let mut dropc = usize::MAX;
    let mut dropd = 255u8;
    for (dx, dy) in [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)] {
        let (nx, ny) = (sh.0 + dx, sh.1 + dy);
        if nx < 0 || ny < 0 || nx >= s.w || ny >= s.h {
            continue;
        }
        let c = cid(nx, ny, w);
        if nav.walk[c] && nav.d(me, c) < dropd {
            dropd = nav.d(me, c);
            dropc = c;
        }
    }
    let adj_shack = (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() <= 1;
    // endgame banking (hard rule = schedbot's 1000x endgame bank rate)
    if carried > 0 {
        let eta = (dropd as i32 + s.u_ms[ui] as i32 - 1) / s.u_ms[ui].max(1) as i32 + 1;
        if turns_rem <= eta + 1 {
            return if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) };
        }
    }
    let ms = s.u_ms[ui].max(1) as i32;
    let steps = |dist: i32| -> f64 { ((dist + ms - 1) / ms).max(0) as f64 };

    // roster facts: own count + chop role (real chopper, or the bootstrap
    // starter — max (cc, -id) among chop>=1 — while no chop>=2 troll exists)
    let mut n_own = 0i16;
    let mut has_real = false;
    for oi in 0..s.n_units as usize {
        if s.u_pl[oi] as usize != pl {
            continue;
        }
        n_own += 1;
        if s.u_chop[oi] >= 2 {
            has_real = true;
        }
    }
    let mut boot = usize::MAX;
    if !has_real {
        for oi in 0..s.n_units as usize {
            if s.u_pl[oi] as usize != pl || s.u_chop[oi] < 1 {
                continue;
            }
            if boot == usize::MAX
                || (s.u_cc[oi], -(s.u_id[oi] as i32)) > (s.u_cc[boot], -(s.u_id[boot] as i32))
            {
                boot = oi;
            }
        }
    }
    let is_chop_role = s.u_chop[ui] >= 2 || boot == ui;
    // FUNDING choppers: gather each cc2 chopper's training cost (plum/lemon + iron)
    // until we have `n_chop_target`. training_cost_fast -> [plum,lemon,apple,_,iron,_].
    let n_real_chop = (0..s.n_units as usize)
        .filter(|&oi| s.u_pl[oi] as usize == pl && s.u_chop[oi] >= 2)
        .count();
    let max_trolls = envi("RH_MAXT", MAX_TROLLS as i64) as usize;
    let n_chop_target = envi("RH_NCHOP", 1) as usize;
    let want_chopper =
        n_real_chop < n_chop_target && (n_own as usize) < max_trolls && s.u_chop[ui] < 2;
    let chop_cost = crate::game::fast::training_cost_fast(n_own, (2, 2, 0, 2));
    let liquidation = turns_rem <= LIQ_T;
    // mow sustainability gate: a banked replacement seed (or liquidation)
    let mow_ok = !is_chop_role && s.u_chop[ui] > 0 && (s.inv[pl][3] >= 1 || liquidation);

    let mut best_v = -1e18f64;
    let mut best_act = FAct::Idle;
    let mut best_cell = usize::MAX;
    macro_rules! consider {
        ($v:expr, $a:expr, $c:expr) => {{
            let v: f64 = $v;
            if v > best_v {
                best_v = v;
                best_act = $a;
                best_cell = $c;
            }
        }};
    }

    // BANK when full: rate carried/t — competes in the market (a seed-carrying
    // printer must be allowed to outrank banking, else cc1 pick->drop livelock)
    if carried > 0 && free == 0 && dropc != usize::MAX {
        let t = steps(dropd as i32) + 1.0;
        consider!(
            carried as f64 / t,
            if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) },
            usize::MAX
        );
    }

    // FUND (boot starter): MINE iron for the chopper when iron still blocks it.
    // Without this the market never affords the cc2 chopper on iron maps.
    if want_chopper && s.has_iron && s.inv[pl][4] < chop_cost[4] && s.u_chop[ui] > 0 && free > 0 {
        if s.iron_adj[me] {
            consider!(FUND_RATE, FAct::Mine, usize::MAX);
        } else {
            let mut bc = usize::MAX;
            let mut bd = 255u8;
            for c in 0..(w as usize * s.h as usize) {
                if s.iron_adj[c] && nav.walk[c] && !reserved[c] {
                    let dd = nav.d(me, c);
                    if dd < bd {
                        bd = dd;
                        bc = c;
                    }
                }
            }
            if bc != usize::MAX {
                consider!(FUND_RATE - bd as f64 * 0.01, FAct::Move(bc as u8), bc);
            }
        }
    }

    // plants: FELL / MOW / HARVEST (+ base census for printer & orchard)
    let mut base_trees = 0i32;
    let mut orchard_n = 0usize;
    for pi in 0..s.n_plants as usize {
        let (px, py) = (s.p_x[pi], s.p_y[pi]);
        let man_home = ((px - sh.0).abs() + (py - sh.1).abs()) as i32;
        if man_home <= BASE_R {
            base_trees += 1;
            if s.p_type[pi] == 0 {
                orchard_n += 1;
            }
        }
        let pc = cid(px, py, w);
        if reserved[pc] {
            continue;
        }
        let d = nav.d(me, pc);
        if d == 255 {
            continue;
        }
        // FELL (chop role). REQUIRE free>0: felling while full collects no wood and
        // just wastes the turn — the old `!fell_needs_free` let a FULL funder trek to
        // a tree (rate 0.65) instead of banking (rate 0.25), stalling the opening.
        let man_opp = ((px - osh.0).abs() + (py - osh.1).abs()) as i32;
        if is_chop_role && s.u_chop[ui] > 0 && free > 0 {
            let chop_t = ((s.p_health[pi] as i32 + s.u_chop[ui] as i32 - 1) / s.u_chop[ui] as i32) as f64;
            let t = steps(d as i32) + chop_t + 0.5 * steps(man_home) + 1.0;
            if turns_rem as f64 > t {
                let rate = if s.u_chop[ui] >= 2 || liquidation {
                    // REAL chopper (or endgame): wood points per turn (travel- AND
                    // chop-time-aware via t) + a bounded denial bias toward contested
                    // trees. (An earlier travel-BLIND quick-fell bonus lifted goldelite
                    // but was exploited by scriptboss/schedbot 86%->38% — dropped.)
                    let wood = (s.p_size[pi].min(free) as i32 * 4) as f64;
                    wood / t + denial_w / (1.0 + man_opp as f64)
                } else {
                    // bootstrap starter (chop=1, no real chopper yet): fell only as a
                    // low-priority fallback so it FUNDS (harvest/mine) the chopper first.
                    FB - (d as i32 + 3 * man_opp) as f64 * 0.005
                };
                consider!(rate, if me == pc { FAct::Chop } else { FAct::Move(pc as u8) }, pc);
            }
        }
        // MOW: own-base fruitless size>=2 trees at pure yield (-1 seed cost)
        if mow_ok && free > 0 && man_home <= MOW_R && s.p_size[pi] >= 2 && s.p_fruits[pi] == 0 {
            let chop_t = ((s.p_health[pi] as i32 + s.u_chop[ui] as i32 - 1) / s.u_chop[ui] as i32) as f64;
            let t = steps(d as i32) + chop_t + 0.5 * steps(man_home) + 1.0;
            if turns_rem as f64 > t {
                let wood = (s.p_size[pi].min(free) as i32 * 4) as f64 - 1.0;
                consider!(wood / t, if me == pc { FAct::Chop } else { FAct::Move(pc as u8) }, pc);
            }
        }
        // HARVEST: one-turn take / (travel + RETW*return). Only worth it when it
        // FEEDS the economy: funding fruit (buys the chopper) or a BANANA seed (feeds
        // the printer). Harvesting random plum/lemon post-funding banks 1 pt while the
        // same turn spent printing/chopping is worth ~4 — goldelite avoids it (13 fruit
        // vs our old 35). Liquidation grabs anything.
        if s.p_fruits[pi] > 0 && s.u_hp[ui] > 0 && free > 0 {
            let ty = s.p_type[pi] as usize;
            let funding = want_chopper && ty < 3 && s.inv[pl][ty] < chop_cost[ty];
            let seed = ty == 3; // banana -> printer seed
            if funding || seed || liquidation {
                let t = steps(d as i32) + 1.0 + RETW * steps(man_home);
                if turns_rem as f64 > t {
                    let mut rate = s.p_fruits[pi].min(s.u_hp[ui]).min(free) as f64 / t;
                    if funding {
                        rate += FUND_RATE; // top priority: buy the chopper first
                    }
                    consider!(rate, if me == pc { FAct::Harvest } else { FAct::Move(pc as u8) }, pc);
                }
            }
        }
    }

    // ORCHARD + PRINT: base-spot scan (only when eligible; fixed 7x7 diamond)
    let window = s.turn >= 20 && s.turn <= 230;
    let want_orch = !is_chop_role && s.u_carry[ui][0] > 0 && orchard_n < ORCH_N;
    let want_print = !is_chop_role && window && base_trees < farm_cap;
    if want_orch || want_print {
        // spot blockers: existing plants + other own trolls
        let mut occ = [false; MAXC];
        for pi in 0..s.n_plants as usize {
            occ[cid(s.p_x[pi], s.p_y[pi], w)] = true;
        }
        for oi in 0..s.n_units as usize {
            if oi != ui && s.u_pl[oi] as usize == pl {
                occ[cid(s.u_x[oi], s.u_y[oi], w)] = true;
            }
        }
        let mut print_c = usize::MAX;
        let mut print_key = (2i32, i32::MAX); // (!water_adj, dist)
        let mut orch_c = usize::MAX;
        let mut orch_d = i32::MAX;
        for dy in -(BASE_R as i8)..=(BASE_R as i8) {
            for dx in -(BASE_R as i8)..=(BASE_R as i8) {
                if (dx.abs() + dy.abs()) as i32 > BASE_R {
                    continue;
                }
                let (x, y) = (sh.0 + dx, sh.1 + dy);
                if x < 0 || y < 0 || x >= s.w || y >= s.h {
                    continue;
                }
                let c = cid(x, y, w);
                if !nav.walk[c] || occ[c] || reserved[c] {
                    continue;
                }
                let dd = nav.d(me, c);
                if dd == 255 {
                    continue;
                }
                if want_print {
                    let k = (!s.water_adj[c] as i32, dd as i32);
                    if k < print_key {
                        print_key = k;
                        print_c = c;
                    }
                }
                if want_orch && s.water_adj[c] && (dd as i32) < orch_d {
                    orch_d = dd as i32;
                    orch_c = c;
                }
            }
        }
        // ORCHARD: carried PLUM -> water base cell; ORCH_V/t outranks the
        // printer's PRINT_V/t, so plum-carriers build the orchard first.
        if orch_c != usize::MAX {
            let t = steps(orch_d) + 1.0;
            consider!(
                ORCH_V / t,
                if me == orch_c { FAct::Plant(0) } else { FAct::Move(orch_c as u8) },
                orch_c
            );
        }
        // PRINT: species follows the spot (wet: apple/plum above a bank
        // reserve, else banana; dry: banana).
        if want_print && print_c != usize::MAX {
            let species: usize = if s.water_adj[print_c] {
                if s.inv[pl][2] >= CROP_RES || s.u_carry[ui][2] > 0 {
                    2
                } else if s.inv[pl][0] >= CROP_RES || s.u_carry[ui][0] > 0 {
                    0
                } else {
                    3
                }
            } else {
                3
            };
            if s.u_carry[ui][species] > 0 {
                let t = steps(print_key.1) + 1.0;
                consider!(
                    PRINT_V / t,
                    if me == print_c { FAct::Plant(species as u8) } else { FAct::Move(print_c as u8) },
                    print_c
                );
            } else if adj_shack && free > 0 && s.inv[pl][species] > 0 && carried == 0 {
                // anti-livelock (rollout-simple, replaces the 12-turn PICK
                // cooldown): only pick on a completely empty carry, and never
                // while another own troll already ferries a seed.
                let ferrying = (0..s.n_units as usize).any(|oi| {
                    oi != ui
                        && s.u_pl[oi] as usize == pl
                        && (s.u_carry[oi][3] > 0 || s.u_carry[oi][species] > 0)
                });
                if !ferrying {
                    consider!(PRINT_V / 2.0, FAct::Pick(species as u8), usize::MAX);
                }
            }
        }
    }

    if best_v > -1e17 {
        if best_cell != usize::MAX {
            reserved[best_cell] = true;
        }
        return best_act;
    }
    if carried > 0 {
        return if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) };
    }
    FAct::Move(if dropc != usize::MAX { dropc as u8 } else { shc as u8 })
}

/// Decode one troll's plan-task into an action given the current rolled state.
/// Returns None when the task is complete (advance to the next task).
fn task_act(s: &FastState, nav: &NavTable, pl: usize, ui: usize, task: Task, root_plants: &[(i8, i8); 72], n_root_plants: usize) -> Option<FAct> {
    let w = s.w;
    match task {
        Task::Auto => None, // handled by caller (policy)
        Task::GoBank => {
            let carried: i32 = (0..6).map(|k| s.u_carry[ui][k] as i32).sum();
            if carried == 0 {
                return None;
            }
            let sh = s.shack[pl];
            if (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() <= 1 {
                Some(FAct::Drop)
            } else {
                // nearest drop cell
                let me = cid(s.u_x[ui], s.u_y[ui], w);
                let mut bc = usize::MAX;
                let mut bd = 255u8;
                for (dx, dy) in [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)] {
                    let (nx, ny) = (sh.0 + dx, sh.1 + dy);
                    if nx < 0 || ny < 0 || nx >= s.w || ny >= s.h {
                        continue;
                    }
                    let c = cid(nx, ny, w);
                    if nav.walk[c] && nav.d(me, c) < bd {
                        bd = nav.d(me, c);
                        bc = c;
                    }
                }
                if bc == usize::MAX { None } else { Some(FAct::Move(bc as u8)) }
            }
        }
        Task::GoMine => {
            if s.free(ui) <= 0 || s.u_chop[ui] == 0 {
                return None;
            }
            let me = cid(s.u_x[ui], s.u_y[ui], w);
            if s.iron_adj[me] {
                return Some(FAct::Mine);
            }
            let mut bc = usize::MAX;
            let mut bd = 255u8;
            for c in 0..(s.w as usize * s.h as usize) {
                if s.iron_adj[c] && nav.walk[c] && nav.d(me, c) < bd {
                    bd = nav.d(me, c);
                    bc = c;
                }
            }
            if bc == usize::MAX { None } else { Some(FAct::Move(bc as u8)) }
        }
        Task::GoTree(k) => {
            if k as usize >= n_root_plants {
                return None;
            }
            let (tx, ty) = root_plants[k as usize];
            let Some(pi) = s.plant_at(tx, ty) else { return None }; // tree gone -> next task
            if s.u_x[ui] == tx && s.u_y[ui] == ty {
                if s.u_chop[ui] > 0 && (s.p_fruits[pi] == 0 || s.u_chop[ui] >= 2) {
                    return Some(FAct::Chop);
                }
                if s.p_fruits[pi] > 0 && s.u_hp[ui] > 0 && s.free(ui) > 0 {
                    return Some(FAct::Harvest);
                }
                return None;
            }
            if s.free(ui) == 0 {
                return None; // full: let policy bank
            }
            Some(FAct::Move(cid(tx, ty, w) as u8))
        }
        Task::PlantHere(ty) => {
            if s.u_carry[ui][ty as usize] == 0 {
                return None;
            }
            let me = cid(s.u_x[ui], s.u_y[ui], w);
            let sh = s.shack[pl];
            let near = (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() <= 3;
            if near && nav.walk[me] && s.plant_at(s.u_x[ui], s.u_y[ui]).is_none() {
                return Some(FAct::Plant(ty));
            }
            // walk to a free base cell (prefer water-adjacent)
            let mut bc = usize::MAX;
            let mut key = (2i32, 255i32);
            for c in 0..(s.w as usize * s.h as usize) {
                if !nav.walk[c] {
                    continue;
                }
                let (x, y) = ((c % s.w as usize) as i8, (c / s.w as usize) as i8);
                if (x - sh.0).abs() + (y - sh.1).abs() > 3 || s.plant_at(x, y).is_some() {
                    continue;
                }
                let k2 = (!s.water_adj[c] as i32, nav.d(me, c) as i32);
                if k2 < key {
                    key = k2;
                    bc = c;
                }
            }
            if bc == usize::MAX { None } else { Some(FAct::Move(bc as u8)) }
        }
    }
}

/// Roll the plan forward H turns; opponent plays the baseline policy.
fn rollout(root: &FastState, nav: &NavTable, plan: &Plan, me: usize) -> f64 {
    let mut s = *root;
    // snapshot root plant positions for GoTree indices
    let mut root_plants = [(0i8, 0i8); 72];
    let nrp = root.n_plants as usize;
    for i in 0..nrp {
        root_plants[i] = (root.p_x[i], root.p_y[i]);
    }
    let mut cursor = [0usize; MAXU]; // per-troll task index
    for step_i in 0..H {
        let turns_rem = 300 - s.turn as i32 + 1;
        if turns_rem <= 0 || s.n_plants == 0 {
            break;
        }
        let mut cmds = [FCmds::default(), FCmds::default()];
        for pl in 0..2usize {
            let mut reserved = [false; MAXC];
            for ui in 0..s.n_units as usize {
                if s.u_pl[ui] as usize != pl {
                    continue;
                }
                let act = if pl == me && step_i < H {
                    // advance through the troll's plan
                    let mut a = None;
                    while cursor[ui] < PLAN_LEN {
                        let t = plan.tasks[ui][cursor[ui]];
                        if t == Task::Auto {
                            break;
                        }
                        match task_act(&s, nav, pl, ui, t, &root_plants, nrp) {
                            Some(x) => {
                                a = Some(x);
                                break;
                            }
                            None => cursor[ui] += 1,
                        }
                    }
                    a.unwrap_or_else(|| policy_act(&s, nav, pl, ui, turns_rem, &mut reserved))
                } else {
                    policy_act(&s, nav, pl, ui, turns_rem, &mut reserved)
                };
                cmds[pl].acts[ui] = act;
            }
        }
        // training (both sides): greedy chopper-first, then harvester ladder
        for pl in 0..2usize {
            let n = (0..s.n_units as usize).filter(|&ui| s.u_pl[ui] as usize == pl).count() as i16;
            if n as usize >= MAX_TROLLS || turns_rem <= 20 {
                continue;
            }
            let n_chop = (0..s.n_units as usize)
                .filter(|&ui| s.u_pl[ui] as usize == pl && s.u_chop[ui] >= 2)
                .count();
            let afford = |t: (i8, i8, i8, i8)| -> bool {
                let c = crate::game::fast::training_cost_fast(n, t);
                (0..6).all(|i| (i == 4 && !s.has_iron) || s.inv[pl][i] >= c[i])
            };
            let spec = if n_chop < 1 {
                // SAVE for the cc2 chopper — WAIT rather than waste the slot on a
                // cheap body (which delays the chopper and inflates its n-scaled cost).
                afford((2, 2, 0, 2)).then_some((2, 2, 0, 2))
            } else {
                [(2i8, 2i8, 2i8, 0i8), (1, 2, 2, 0), (1, 1, 1, 0)]
                    .into_iter()
                    .find(|&t| afford(t))
            };
            cmds[pl].train = spec;
        }
        crate::game::fast::step_fast(&mut s, nav, &cmds);
    }
    // eval: banked diff + fraction of carried value + tiny asset term
    let mut carried = [0f64; 2];
    for ui in 0..s.n_units as usize {
        let v: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
        carried[s.u_pl[ui] as usize] += v as f64;
    }
    // asset terms: a troll's future output and standing base trees have value
    // beyond the horizon; without these, in-rollout training/planting read as
    // pure losses and plans learn to avoid growth.
    let mut trolls = [0f64; 2];
    for ui in 0..s.n_units as usize {
        trolls[s.u_pl[ui] as usize] += 1.0;
    }
    // CAPPED tree-asset term: uncapped it made planting near-free in eval
    // (arena decode: 68 PLANTs, 30 chops, 54-point game — plant mania).
    let mut base_trees = [0f64; 2];
    for pi in 0..s.n_plants as usize {
        for p in 0..2usize {
            let sh = s.shack[p];
            if (s.p_x[pi] - sh.0).abs() + (s.p_y[pi] - sh.1).abs() <= 3 {
                base_trees[p] += (s.p_size[pi] as f64).max(1.0);
            }
        }
    }
    base_trees[0] = base_trees[0].min(12.0);
    base_trees[1] = base_trees[1].min(12.0);
    (s.score(me) - s.score(1 - me)) as f64
        + 0.5 * (carried[me] - carried[1 - me])
        + 12.0 * (trolls[me] - trolls[1 - me])
        + 1.5 * (base_trees[me] - base_trees[1 - me])
}

impl Strategy for RheaBot {
    fn name(&self) -> &str {
        "rhea"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        // (re)build nav at game start
        if game.turn == 1 || self.nav.borrow().is_none() {
            *self.nav.borrow_mut() = Some(NavTable::build(game));
            *self.best.borrow_mut() = Plan::default();
            self.lastpos.borrow_mut().clear();
        }
        let navb = self.nav.borrow();
        let nav = navb.as_ref().unwrap();
        let root = FastState::from_game(game);
        let me = player;
        // Search budget. DEFAULT 0 = pure policy: the evolutionary plan search over
        // this (now strong) baseline consistently REGRESSED it — the short H=40 rollout
        // eval rewards carried value / tree assets, so mutations that skip training or
        // grab quick fruit look good but lose the long wood game (e.g. 42%->25% vs
        // goldelite, trolls 2.0->1.8). Set RH_MS>0 to re-enable the search for study.
        let budget_ms = envi("RH_MS", 0) as u128;
        let t0 = Instant::now();

        let nrp = (root.n_plants as usize).min(72);
        let my_units: Vec<usize> = (0..root.n_units as usize).filter(|&ui| root.u_pl[ui] as usize == me).collect();

        // seed pool: carried-over best (shifted) + policy-only
        let mut best = *self.best.borrow();
        let mut best_v = rollout(&root, nav, &best, me);
        let policy_only = Plan::default();
        let pv = rollout(&root, nav, &policy_only, me);
        if pv > best_v {
            best = policy_only;
            best_v = pv;
        }
        let mut evals = 2u32;
        while t0.elapsed().as_millis() < budget_ms {
            // mutate: pick a troll, rewrite 1-2 tasks randomly
            let mut cand = best;
            if my_units.is_empty() {
                break;
            }
            let ui = my_units[(self.rand() as usize) % my_units.len()];
            for _ in 0..1 + (self.rand() % 2) {
                let slot = (self.rand() as usize) % PLAN_LEN;
                let roll = self.rand() % 100;
                cand.tasks[ui][slot] = if roll < 45 && nrp > 0 {
                    Task::GoTree((self.rand() as usize % nrp) as u8)
                } else if roll < 60 {
                    Task::GoBank
                } else if roll < 65 {
                    Task::PlantHere(3) // banana
                } else if roll < 78 {
                    Task::GoMine
                } else {
                    Task::Auto
                };
            }
            let v = rollout(&root, nav, &cand, me);
            evals += 1;
            if v > best_v {
                best_v = v;
                best = cand;
            }
        }
        *self.best.borrow_mut() = best;
        let _ = evals;

        // emit the first move of the best plan (same decode as the rollout's turn 0)
        let turns_rem = 300 - root.turn as i32 + 1;
        let mut root_plants = [(0i8, 0i8); 72];
        for i in 0..nrp {
            root_plants[i] = (root.p_x[i], root.p_y[i]);
        }
        let mut reserved = [false; MAXC];
        let mut out: Vec<String> = Vec::new();
        for &ui in &my_units {
            let mut act = None;
            let mut k = 0usize;
            while k < PLAN_LEN {
                let t = best.tasks[ui][k];
                if t == Task::Auto {
                    break;
                }
                match task_act(&root, nav, me, ui, t, &root_plants, nrp) {
                    Some(x) => {
                        act = Some(x);
                        break;
                    }
                    None => k += 1,
                }
            }
            let mut act = act.unwrap_or_else(|| policy_act(&root, nav, me, ui, turns_rem, &mut reserved));
            let id = root.u_id[ui];
            // ANTI-STALL WATCHDOG (arena decode: 99 failed MOVEs/game, trolls stuck
            // 20-248 turns behind OWN units — 8/17 losses). If we issued MOVEs but
            // the troll hasn't moved for 2+ turns, sidestep to a free adjacent cell.
            {
                let mut lp = self.lastpos.borrow_mut();
                let cur = (root.u_x[ui], root.u_y[ui]);
                let entry = lp.entry(id as i32).or_insert((cur.0, cur.1, 0));
                let stuck = entry.0 == cur.0 && entry.1 == cur.1;
                let was_moving = matches!(act, FAct::Move(_));
                if stuck && was_moving {
                    entry.2 = entry.2.saturating_add(1);
                } else {
                    entry.2 = 0;
                }
                *entry = (cur.0, cur.1, entry.2);
                if entry.2 >= 2 {
                    if let FAct::Move(tgt) = act {
                        if tgt as usize != cid(cur.0, cur.1, root.w) {
                            // pick a free adjacent walkable cell not under an own troll
                            let mut cands: Vec<u8> = Vec::new();
                            for (dx, dy) in [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)] {
                                let (nx, ny) = (cur.0 + dx, cur.1 + dy);
                                if nx < 0 || ny < 0 || nx >= root.w || ny >= root.h {
                                    continue;
                                }
                                let c = cid(nx, ny, root.w);
                                if !nav.walk[c] {
                                    continue;
                                }
                                let occupied = (0..root.n_units as usize).any(|o| {
                                    root.u_pl[o] as usize == me
                                        && root.u_x[o] == nx
                                        && root.u_y[o] == ny
                                });
                                if !occupied {
                                    cands.push(c as u8);
                                }
                            }
                            if !cands.is_empty() {
                                let pick = cands[(self.rand() as usize) % cands.len()];
                                act = FAct::Move(pick);
                                entry.2 = 0;
                            }
                        }
                    }
                }
            }
            let s = match act {
                FAct::Idle => format!("MOVE {} {} {}", id, root.shack[me].0, root.shack[me].1),
                FAct::Move(c) => {
                    let (x, y) = ((c as usize % root.w as usize), (c as usize / root.w as usize));
                    format!("MOVE {} {} {}", id, x, y)
                }
                FAct::Harvest => format!("HARVEST {}", id),
                FAct::Chop => format!("CHOP {}", id),
                FAct::Drop => format!("DROP {}", id),
                FAct::Mine => format!("MINE {}", id),
                FAct::Plant(ty) => format!("PLANT {} {}", id, ["PLUM", "LEMON", "APPLE", "BANANA"][ty as usize]),
                FAct::Pick(ty) => format!("PICK {} {}", id, ["PLUM", "LEMON", "APPLE", "BANANA"][ty as usize]),
            };
            out.push(s);
        }
        // training: reuse the greedy plan (chopper first, then harvester ladder)
        let n = my_units.len() as i32;
        let inv = &game.inventories[me];
        let have_iron = !game.iron.is_empty();
        let afford = |c: [i32; 6]| -> bool {
            inv[0] >= c[0] && inv[1] >= c[1] && inv[2] >= c[2] && (!have_iron || inv[4] >= c[4])
        };
        let cost = |t: (i32, i32, i32, i32)| -> [i32; 6] {
            [n + t.0 * t.0, n + t.1 * t.1, n + t.2 * t.2, 0, n + t.3 * t.3, 0]
        };
        let n_chop = my_units.iter().filter(|&&ui| root.u_chop[ui] >= 2).count();
        let max_trolls = envi("RH_MAXT", MAX_TROLLS as i64) as usize;
        let n_chop_target = envi("RH_NCHOP", 1) as usize;
        // SAVE for cc2 chopper(s) — never spend the slot on a cheap body (that both
        // delays the chopper and inflates its n-scaled cost). The single biggest fix:
        // the old fallback trained a (1,1,1,0) at t2 so a real chopper was NEVER built
        // (all felling was the cc1 starter, 1 wood/fell).
        let spec = if n_chop < n_chop_target {
            afford(cost((2, 2, 0, 2))).then_some((2, 2, 0, 2))
        } else {
            [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)]
                .into_iter()
                .find(|&t| afford(cost(t)))
        };
        if let Some(t) = spec {
            let sh = game.shacks[me];
            if (n as usize) < max_trolls && 300 - game.turn > 20 && !game.units.iter().any(|u| u.pos() == sh) {
                out.push(format!("TRAIN {} {} {} {}", t.0, t.1, t.2, t.3));
            }
        }
        if out.is_empty() {
            out.push("WAIT".into());
        }
        out
    }
}
