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
}

impl RheaBot {
    pub fn new() -> Self {
        RheaBot { nav: RefCell::new(None), best: RefCell::new(Plan::default()), rng: RefCell::new(0x9E3779B97F4A7C15) }
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

/// Baseline per-troll policy on FastState (market-lite): full->bank,
/// on-fruit->harvest, chopper->fell by yield-nearest, else harvest-nearest,
/// endgame banking. Used for the opponent and for Task::Auto trolls.
fn policy_act(s: &FastState, nav: &NavTable, pl: usize, ui: usize, turns_rem: i32, reserved: &mut [bool; MAXC]) -> FAct {
    let w = s.w;
    let me = cid(s.u_x[ui], s.u_y[ui], w);
    let free = s.free(ui);
    let carried: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
    let sh = s.shack[pl];
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
    // endgame banking
    if carried > 0 {
        let eta = (dropd as i32 + s.u_ms[ui] as i32 - 1) / s.u_ms[ui].max(1) as i32 + 1;
        if turns_rem <= eta + 1 {
            return if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) };
        }
    }
    if free == 0 {
        return if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) };
    }
    // on a plant?
    if let Some(pi) = s.plant_at(s.u_x[ui], s.u_y[ui]) {
        if s.u_chop[ui] >= 2 {
            return FAct::Chop;
        }
        if s.p_fruits[pi] > 0 && s.u_hp[ui] > 0 {
            return FAct::Harvest;
        }
    }
    // choose a target
    let is_chopper = s.u_chop[ui] >= 2;
    let mut best_c = usize::MAX;
    let mut best_v = -1e18f64;
    for pi in 0..s.n_plants as usize {
        let pc = cid(s.p_x[pi], s.p_y[pi], w);
        if reserved[pc] {
            continue;
        }
        let d = nav.d(me, pc);
        if d == 255 {
            continue;
        }
        let steps = (d as i32 + s.u_ms[ui] as i32 - 1) / s.u_ms[ui].max(1) as i32;
        let v = if is_chopper {
            let chop_t = (s.p_health[pi] as i32 + s.u_chop[ui] as i32 - 1) / s.u_chop[ui] as i32;
            let wood = (s.p_size[pi].min(free) as i32 * 4) as f64;
            wood / (steps as f64 + chop_t as f64 + 1.0)
        } else if s.p_fruits[pi] > 0 && s.u_hp[ui] > 0 {
            let take = s.p_fruits[pi].min(s.u_hp[ui]).min(free) as f64;
            take / (steps as f64 + 1.0)
        } else {
            continue;
        };
        if v > best_v {
            best_v = v;
            best_c = pc;
        }
    }
    if best_c != usize::MAX {
        reserved[best_c] = true;
        return FAct::Move(best_c as u8);
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
        crate::game::fast::step_fast(&mut s, nav, &cmds);
    }
    // eval: banked diff + fraction of carried value + tiny asset term
    let mut carried = [0f64; 2];
    for ui in 0..s.n_units as usize {
        let v: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
        carried[s.u_pl[ui] as usize] += v as f64;
    }
    (s.score(me) - s.score(1 - me)) as f64 + 0.5 * (carried[me] - carried[1 - me])
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
        }
        let navb = self.nav.borrow();
        let nav = navb.as_ref().unwrap();
        let root = FastState::from_game(game);
        let me = player;
        let budget_ms = envi("RH_MS", 30) as u128;
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
                } else if roll < 70 {
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
            let act = act.unwrap_or_else(|| policy_act(&root, nav, me, ui, turns_rem, &mut reserved));
            let id = root.u_id[ui];
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
        let spec = if n_chop < 2 && afford(cost((2, 2, 0, 2))) {
            Some((2, 2, 0, 2))
        } else {
            [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)]
                .into_iter()
                .find(|&t| afford(cost(t)))
        };
        if let Some(t) = spec {
            let sh = game.shacks[me];
            if (n as usize) < 4 && 300 - game.turn > 20 && !game.units.iter().any(|u| u.pos() == sh) {
                out.push(format!("TRAIN {} {} {} {}", t.0, t.1, t.2, t.3));
            }
        }
        if out.is_empty() {
            out.push("WAIT".into());
        }
        out
    }
}
