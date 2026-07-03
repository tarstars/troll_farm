//! Copy-cheap game state + O(1) pathing for rollout search (RHEA/MCTS).
//!
//! Two pillars:
//! 1. `NavTable` — the walkable set never changes during a game, so all-pairs
//!    BFS distances and next-step tables are precomputed ONCE (per game), and
//!    every rollout move becomes a table lookup instead of a BFS.
//! 2. `FastState` — fixed-size arrays, `Copy`; cloning is a ~2 KB memcpy vs the
//!    HashMap-heavy `GameState`. `step_fast` ports the referee rules from
//!    `engine.rs` (move conflicts per player, harvest rounds, chop + wood
//!    distribution, plant/pick/train/drop/mine, plant ticking).
use super::state::{Cell, GameState};

pub const MAXW: usize = 22;
pub const MAXH: usize = 11;
pub const MAXC: usize = MAXW * MAXH; // 242
pub const MAXP: usize = 72;
pub const MAXU: usize = 12;

#[inline]
pub fn cid(x: i8, y: i8, w: i8) -> usize {
    y as usize * w as usize + x as usize
}

/// Static per-map navigation: all-pairs dist + next-step (O(1) rollout moves).
pub struct NavTable {
    pub w: i8,
    pub h: i8,
    pub walk: [bool; MAXC],
    pub dist: Vec<u8>,      // dist[from * MAXC + to], 255 = unreachable
    pub next: Vec<u8>,      // next[from * MAXC + to] = cell id of first step
    pub park: [u8; MAXC],   // for unreachable targets: reachable cell minimizing manhattan
}

impl NavTable {
    pub fn build(g: &GameState) -> Box<NavTable> {
        let w = g.width as i8;
        let h = g.height as i8;
        let mut nav = Box::new(NavTable {
            w,
            h,
            walk: [false; MAXC],
            dist: vec![255u8; MAXC * MAXC],
            next: vec![255u8; MAXC * MAXC],
            park: [255u8; MAXC],
        });
        for &(x, y) in &g.walkable {
            nav.walk[cid(x as i8, y as i8, w)] = true;
        }
        // BFS from every cell (walkable sources + shack cells: units can stand there)
        let mut sources: Vec<usize> = (0..(w as usize * h as usize)).filter(|&c| nav.walk[c]).collect();
        for &s in &[g.shacks[0], g.shacks[1]] {
            sources.push(cid(s.0 as i8, s.1 as i8, w));
        }
        let mut q = std::collections::VecDeque::new();
        for &src in &sources {
            let base = src * MAXC;
            nav.dist[base + src] = 0;
            nav.next[base + src] = src as u8;
            q.clear();
            q.push_back(src);
            while let Some(c) = q.pop_front() {
                let d = nav.dist[base + c];
                let (cx, cy) = ((c % w as usize) as i8, (c / w as usize) as i8);
                for (dx, dy) in [(0i8, 1i8), (1, 0), (0, -1), (-1, 0)] {
                    let (nx, ny) = (cx + dx, cy + dy);
                    if nx < 0 || ny < 0 || nx >= w || ny >= h {
                        continue;
                    }
                    let n = cid(nx, ny, w);
                    if !nav.walk[n] || nav.dist[base + n] != 255 {
                        continue;
                    }
                    nav.dist[base + n] = d + 1;
                    // first step from src toward n: inherit, or n itself if c==src
                    nav.next[base + n] = if c == src { n as u8 } else { nav.next[base + c] };
                    q.push_back(n);
                }
            }
        }
        // park targets for unwalkable cells (e.g. shacks as MOVE targets):
        // reachable cell minimizing manhattan to the target (referee rule).
        for t in 0..(w as usize * h as usize) {
            if nav.walk[t] {
                nav.park[t] = t as u8;
                continue;
            }
            let (tx, ty) = ((t % w as usize) as i8, (t / w as usize) as i8);
            let mut best = 255usize;
            let mut bestd = i32::MAX;
            for c in 0..(w as usize * h as usize) {
                if !nav.walk[c] {
                    continue;
                }
                let (cx, cy) = ((c % w as usize) as i8, (c / w as usize) as i8);
                let md = ((cx - tx).abs() + (cy - ty).abs()) as i32;
                if md < bestd {
                    bestd = md;
                    best = c;
                }
            }
            nav.park[t] = best as u8;
        }
        nav
    }

    #[inline]
    pub fn d(&self, from: usize, to: usize) -> u8 {
        self.dist[from * MAXC + to]
    }
}

#[derive(Clone, Copy)]
pub struct FastState {
    pub w: i8,
    pub h: i8,
    pub turn: i16,
    pub next_id: i16,
    pub shack: [(i8, i8); 2],
    pub inv: [[i16; 6]; 2],
    pub n_plants: u8,
    pub p_type: [u8; MAXP], // 0..3 = PLUM,LEMON,APPLE,BANANA
    pub p_x: [i8; MAXP],
    pub p_y: [i8; MAXP],
    pub p_size: [i8; MAXP],
    pub p_health: [i8; MAXP],
    pub p_fruits: [i8; MAXP],
    pub p_cd: [i8; MAXP],
    pub p_wet: [bool; MAXP], // water-adjacent (cooldown boost)
    pub n_units: u8,
    pub u_id: [i16; MAXU],
    pub u_pl: [u8; MAXU],
    pub u_x: [i8; MAXU],
    pub u_y: [i8; MAXU],
    pub u_ms: [i8; MAXU],
    pub u_cc: [i8; MAXU],
    pub u_hp: [i8; MAXU],
    pub u_chop: [i8; MAXU],
    pub u_carry: [[i8; 6]; MAXU],
    pub iron_adj: [bool; MAXC], // cells adjacent to iron (MINE legality)
    pub water_adj: [bool; MAXC],
    pub has_iron: bool,
}

pub const CD_BASE: [i8; 4] = [8, 8, 9, 6];
pub const CD_BOOST: [i8; 4] = [5, 5, 7, 2];
pub const HP_BASE: [i8; 4] = [4, 4, 8, 2];
pub const HP_SLOPE: [i8; 4] = [2, 2, 3, 1];

pub fn type_idx(t: &str) -> u8 {
    match t {
        "PLUM" => 0,
        "LEMON" => 1,
        "APPLE" => 2,
        _ => 3,
    }
}

impl FastState {
    pub fn from_game(g: &GameState) -> FastState {
        let w = g.width as i8;
        let h = g.height as i8;
        let mut s = FastState {
            w,
            h,
            turn: g.turn as i16,
            next_id: g.next_id as i16,
            shack: [
                (g.shacks[0].0 as i8, g.shacks[0].1 as i8),
                (g.shacks[1].0 as i8, g.shacks[1].1 as i8),
            ],
            inv: [[0; 6]; 2],
            n_plants: 0,
            p_type: [0; MAXP],
            p_x: [0; MAXP],
            p_y: [0; MAXP],
            p_size: [0; MAXP],
            p_health: [0; MAXP],
            p_fruits: [0; MAXP],
            p_cd: [0; MAXP],
            p_wet: [false; MAXP],
            n_units: 0,
            u_id: [0; MAXU],
            u_pl: [0; MAXU],
            u_x: [0; MAXU],
            u_y: [0; MAXU],
            u_ms: [0; MAXU],
            u_cc: [0; MAXU],
            u_hp: [0; MAXU],
            u_chop: [0; MAXU],
            u_carry: [[0; 6]; MAXU],
            iron_adj: [false; MAXC],
            water_adj: [false; MAXC],
            has_iron: !g.iron.is_empty(),
        };
        for p in 0..2 {
            for i in 0..6 {
                s.inv[p][i] = g.inventories[p][i] as i16;
            }
        }
        let wet = |c: Cell| g.water.iter().any(|&(wx, wy)| (c.0 - wx).abs() + (c.1 - wy).abs() == 1);
        for pl in &g.plants {
            let i = s.n_plants as usize;
            if i >= MAXP {
                break;
            }
            s.p_type[i] = type_idx(&pl.plant_type);
            s.p_x[i] = pl.x as i8;
            s.p_y[i] = pl.y as i8;
            s.p_size[i] = pl.size as i8;
            s.p_health[i] = pl.health as i8;
            s.p_fruits[i] = pl.fruits as i8;
            s.p_cd[i] = pl.cooldown as i8;
            s.p_wet[i] = wet(pl.pos());
            s.n_plants += 1;
        }
        for u in &g.units {
            let i = s.n_units as usize;
            if i >= MAXU {
                break;
            }
            s.u_id[i] = u.id as i16;
            s.u_pl[i] = u.player as u8;
            s.u_x[i] = u.x as i8;
            s.u_y[i] = u.y as i8;
            s.u_ms[i] = u.ms as i8;
            s.u_cc[i] = u.cc as i8;
            s.u_hp[i] = u.hp as i8;
            s.u_chop[i] = u.chop as i8;
            for k in 0..6 {
                s.u_carry[i][k] = u.carry[k] as i8;
            }
            s.n_units += 1;
        }
        for &(ix, iy) in &g.iron {
            for (dx, dy) in [(0i32, 1i32), (1, 0), (0, -1), (-1, 0)] {
                let (nx, ny) = (ix + dx, iy + dy);
                if nx >= 0 && ny >= 0 && nx < g.width && ny < g.height {
                    s.iron_adj[cid(nx as i8, ny as i8, w)] = true;
                }
            }
        }
        for &(wx, wy) in &g.water {
            for (dx, dy) in [(0i32, 1i32), (1, 0), (0, -1), (-1, 0)] {
                let (nx, ny) = (wx + dx, wy + dy);
                if nx >= 0 && ny >= 0 && nx < g.width && ny < g.height {
                    s.water_adj[cid(nx as i8, ny as i8, w)] = true;
                }
            }
        }
        s
    }

    #[inline]
    pub fn plant_at(&self, x: i8, y: i8) -> Option<usize> {
        (0..self.n_plants as usize).find(|&i| self.p_x[i] == x && self.p_y[i] == y)
    }

    #[inline]
    pub fn free(&self, ui: usize) -> i8 {
        self.u_cc[ui] - self.u_carry[ui].iter().sum::<i8>()
    }

    pub fn score(&self, p: usize) -> i32 {
        (self.inv[p][0] + self.inv[p][1] + self.inv[p][2] + self.inv[p][3]) as i32
            + 4 * self.inv[p][5] as i32
    }
}

/// One unit's action for a turn (macro-free, referee-level).
#[derive(Clone, Copy, PartialEq, Debug)]
pub enum FAct {
    Idle,
    Move(u8), // target cell id (may be unwalkable -> park rule)
    Harvest,
    Chop,
    Drop,
    Mine,
    Plant(u8),          // fruit type
    Pick(u8),           // fruit type
}

/// Per-player turn command set: one action per unit slot + optional train.
#[derive(Clone, Copy)]
pub struct FCmds {
    pub acts: [FAct; MAXU],
    pub train: Option<(i8, i8, i8, i8)>,
}

impl Default for FCmds {
    fn default() -> Self {
        FCmds { acts: [FAct::Idle; MAXU], train: None }
    }
}

pub fn training_cost_fast(n: i16, t: (i8, i8, i8, i8)) -> [i16; 6] {
    let mut c = [0i16; 6];
    c[0] = n + (t.0 as i16) * (t.0 as i16);
    c[1] = n + (t.1 as i16) * (t.1 as i16);
    c[2] = n + (t.2 as i16) * (t.2 as i16);
    c[4] = n + (t.3 as i16) * (t.3 as i16);
    c
}

/// Full referee turn: moves -> harvest -> plant -> chop -> pick -> train -> drop
/// -> mine -> tick plants. Mirrors engine.rs::step semantics.
pub fn step_fast(s: &mut FastState, nav: &NavTable, cmds: &[FCmds; 2]) {
    let w = s.w;
    // ── moves (per-player conflict resolution, highest id first) ─────────────
    for pl in 0..2u8 {
        // desired target cell per unit (after speed-limited pathing)
        let mut want: [Option<usize>; MAXU] = [None; MAXU];
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] != pl {
                continue;
            }
            if let FAct::Move(tgt) = cmds[pl as usize].acts[ui] {
                let from = cid(s.u_x[ui], s.u_y[ui], w);
                let mut to = tgt as usize;
                if !nav.walk[to] {
                    to = nav.park[to] as usize; // park rule for unwalkable targets
                }
                let d = nav.d(from, to);
                if d == 255 {
                    continue;
                }
                let ms = s.u_ms[ui] as u8;
                let mut cell = from;
                // walk up to ms steps along the shortest path
                for _ in 0..ms.min(d) {
                    cell = nav.next[cell * MAXC + to] as usize;
                }
                if cell != from {
                    want[ui] = Some(cell);
                }
            }
        }
        // conflict resolution: occupied set = this player's unit cells
        let mut occ: [bool; MAXC] = [false; MAXC];
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] == pl {
                occ[cid(s.u_x[ui], s.u_y[ui], w)] = true;
            }
        }
        // iterate: move units whose target is free, highest id first; repeat
        let mut order: Vec<usize> = (0..s.n_units as usize)
            .filter(|&ui| s.u_pl[ui] == pl && want[ui].is_some())
            .collect();
        order.sort_by_key(|&ui| -(s.u_id[ui] as i32));
        let mut progress = true;
        let mut force = false;
        while progress {
            progress = false;
            for &ui in &order {
                let Some(t) = want[ui] else { continue };
                let cur = cid(s.u_x[ui], s.u_y[ui], w);
                // count contenders
                let contested = order
                    .iter()
                    .filter(|&&o| want[o] == Some(t))
                    .count()
                    > 1;
                if (!contested || force) && !occ[t] {
                    occ[cur] = false;
                    occ[t] = true;
                    s.u_x[ui] = (t % w as usize) as i8;
                    s.u_y[ui] = (t / w as usize) as i8;
                    want[ui] = None;
                    progress = true;
                    force = false;
                }
            }
            if progress {
                continue;
            }
            // swaps: A->B while B->A (2-cycles only; longer cycles are rare)
            for &a in &order {
                let Some(ta) = want[a] else { continue };
                for &b in &order {
                    if a == b {
                        continue;
                    }
                    let Some(tb) = want[b] else { continue };
                    let ca = cid(s.u_x[a], s.u_y[a], w);
                    let cb = cid(s.u_x[b], s.u_y[b], w);
                    if ta == cb && tb == ca {
                        s.u_x[a] = (ta % w as usize) as i8;
                        s.u_y[a] = (ta / w as usize) as i8;
                        s.u_x[b] = (tb % w as usize) as i8;
                        s.u_y[b] = (tb / w as usize) as i8;
                        want[a] = None;
                        want[b] = None;
                        progress = true;
                    }
                }
            }
            if !progress && !force && order.iter().any(|&ui| want[ui].is_some()) {
                force = true;
                progress = true;
            }
        }
    }

    // ── harvest (rounds; last-fruit duplication across both players) ─────────
    for round in 1..=3i8 {
        // collect harvesters per plant this round
        for pi in 0..s.n_plants as usize {
            if s.p_fruits[pi] <= 0 {
                continue;
            }
            let (px, py) = (s.p_x[pi], s.p_y[pi]);
            let ty = s.p_type[pi] as usize;
            let mut took = 0i8;
            for ui in 0..s.n_units as usize {
                let pl = s.u_pl[ui] as usize;
                if cmds[pl].acts[ui] != FAct::Harvest {
                    continue;
                }
                if s.u_x[ui] != px || s.u_y[ui] != py {
                    continue;
                }
                if s.u_hp[ui] >= round && s.free(ui) > 0 {
                    s.u_carry[ui][ty] += 1;
                    took += 1;
                }
            }
            // decrement once per taker but not below 0 (duplication quirk)
            s.p_fruits[pi] = (s.p_fruits[pi] - took).max(0);
        }
    }

    // ── plant ────────────────────────────────────────────────────────────────
    for pl in 0..2usize {
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] as usize != pl {
                continue;
            }
            if let FAct::Plant(ty) = cmds[pl].acts[ui] {
                let (x, y) = (s.u_x[ui], s.u_y[ui]);
                let c = cid(x, y, w);
                if !nav.walk[c] || s.plant_at(x, y).is_some() {
                    continue;
                }
                if s.u_carry[ui][ty as usize] <= 0 || s.n_plants as usize >= MAXP {
                    continue;
                }
                s.u_carry[ui][ty as usize] -= 1;
                let i = s.n_plants as usize;
                s.p_type[i] = ty;
                s.p_x[i] = x;
                s.p_y[i] = y;
                s.p_size[i] = 0;
                s.p_health[i] = HP_BASE[ty as usize];
                s.p_fruits[i] = 0;
                s.p_cd[i] = 0;
                s.p_wet[i] = s.water_adj[c];
                s.n_plants += 1;
            }
        }
    }

    // ── chop ────────────────────────────────────────────────────────────────
    let mut dead: [bool; MAXP] = [false; MAXP];
    for pi in 0..s.n_plants as usize {
        let (px, py) = (s.p_x[pi], s.p_y[pi]);
        // damage
        let mut choppers: [usize; 4] = [usize::MAX; 4];
        let mut nch = 0usize;
        for ui in 0..s.n_units as usize {
            let pl = s.u_pl[ui] as usize;
            if cmds[pl].acts[ui] != FAct::Chop || s.u_chop[ui] == 0 {
                continue;
            }
            if s.u_x[ui] != px || s.u_y[ui] != py {
                continue;
            }
            s.p_health[pi] -= s.u_chop[ui];
            if nch < 4 {
                choppers[nch] = ui;
                nch += 1;
            }
        }
        if nch > 0 && s.p_health[pi] <= 0 {
            // wood distribution round-robin among choppers with free capacity
            let mut remaining = s.p_size[pi];
            let mut i = 0;
            while i < s.p_size[pi] && remaining > 0 {
                for k in 0..nch {
                    let ui = choppers[k];
                    if s.free(ui) > 0 && remaining > 0 {
                        s.u_carry[ui][5] += 1;
                        remaining -= 1;
                    }
                }
                i += 1;
            }
            dead[pi] = true;
        }
    }
    // remove dead plants (swap-remove keeping order-insensitive)
    let mut pi = 0usize;
    while pi < s.n_plants as usize {
        if dead[pi] {
            let last = s.n_plants as usize - 1;
            s.p_type[pi] = s.p_type[last];
            s.p_x[pi] = s.p_x[last];
            s.p_y[pi] = s.p_y[last];
            s.p_size[pi] = s.p_size[last];
            s.p_health[pi] = s.p_health[last];
            s.p_fruits[pi] = s.p_fruits[last];
            s.p_cd[pi] = s.p_cd[last];
            s.p_wet[pi] = s.p_wet[last];
            dead[pi] = dead[last];
            dead[last] = false;
            s.n_plants -= 1;
        } else {
            pi += 1;
        }
    }

    // ── pick ────────────────────────────────────────────────────────────────
    for pl in 0..2usize {
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] as usize != pl {
                continue;
            }
            if let FAct::Pick(ty) = cmds[pl].acts[ui] {
                let sh = s.shack[pl];
                if (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() > 1 {
                    continue;
                }
                if s.free(ui) <= 0 || s.inv[pl][ty as usize] <= 0 {
                    continue;
                }
                s.inv[pl][ty as usize] -= 1;
                s.u_carry[ui][ty as usize] += 1;
            }
        }
    }

    // ── train ───────────────────────────────────────────────────────────────
    for pl in 0..2usize {
        if let Some(t) = cmds[pl].train {
            let n = (0..s.n_units as usize).filter(|&ui| s.u_pl[ui] as usize == pl).count() as i16;
            let cost = training_cost_fast(n, t);
            let payable = (0..6).all(|i| {
                if i == 4 && !s.has_iron {
                    true
                } else {
                    s.inv[pl][i] >= cost[i]
                }
            });
            let sh = s.shack[pl];
            let occupied = (0..s.n_units as usize).any(|ui| s.u_x[ui] == sh.0 && s.u_y[ui] == sh.1);
            if payable && !occupied && (s.n_units as usize) < MAXU {
                for i in 0..6 {
                    if i == 4 && !s.has_iron {
                        continue;
                    }
                    s.inv[pl][i] -= cost[i];
                }
                let i = s.n_units as usize;
                s.u_id[i] = s.next_id;
                s.next_id += 1;
                s.u_pl[i] = pl as u8;
                s.u_x[i] = sh.0;
                s.u_y[i] = sh.1;
                s.u_ms[i] = t.0;
                s.u_cc[i] = t.1;
                s.u_hp[i] = t.2;
                s.u_chop[i] = t.3;
                s.u_carry[i] = [0; 6];
                s.n_units += 1;
            }
        }
    }

    // ── drop ────────────────────────────────────────────────────────────────
    for pl in 0..2usize {
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] as usize != pl || cmds[pl].acts[ui] != FAct::Drop {
                continue;
            }
            let sh = s.shack[pl];
            if (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() > 1 {
                continue;
            }
            for i in 0..6 {
                s.inv[pl][i] += s.u_carry[ui][i] as i16;
                s.u_carry[ui][i] = 0;
            }
        }
    }

    // ── mine ────────────────────────────────────────────────────────────────
    for pl in 0..2usize {
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] as usize != pl || cmds[pl].acts[ui] != FAct::Mine {
                continue;
            }
            if s.u_chop[ui] == 0 || s.free(ui) <= 0 {
                continue;
            }
            if !s.iron_adj[cid(s.u_x[ui], s.u_y[ui], w)] {
                continue;
            }
            let amount = s.u_chop[ui].min(s.free(ui));
            s.u_carry[ui][4] += amount;
        }
    }

    // ── tick plants ─────────────────────────────────────────────────────────
    for pi in 0..s.n_plants as usize {
        if s.p_cd[pi] > 0 {
            s.p_cd[pi] -= 1;
        }
        if s.p_cd[pi] == 0 && s.p_health[pi] > 0 {
            let ty = s.p_type[pi] as usize;
            let cd = if s.p_wet[pi] {
                CD_BASE[ty] - CD_BOOST[ty]
            } else {
                CD_BASE[ty]
            };
            if s.p_size[pi] < 4 {
                s.p_size[pi] += 1;
                s.p_health[pi] += HP_SLOPE[ty];
                s.p_cd[pi] = cd;
            } else if s.p_fruits[pi] < 3 {
                s.p_fruits[pi] += 1;
                s.p_cd[pi] = cd;
            }
        }
    }
    s.turn += 1;
}
