#![allow(dead_code, unused)]
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};
const VERSION: &str = "1.51.1-fruitstand";
mod state {
use std::collections::{HashMap, HashSet, VecDeque};
pub const TOTAL_TURNS: i32 = 300;
pub const PLUM: usize = 0;
pub const LEMON: usize = 1;
pub const APPLE: usize = 2;
pub const BANANA: usize = 3;
pub const IRON: usize = 4;
pub const WOOD: usize = 5;
pub fn plant_cooldown(t: &str) -> i32 {
    match t {
        "PLUM" => 8,
        "LEMON" => 8,
        "APPLE" => 9,
        "BANANA" => 6,
        _ => panic!("unknown plant: {}", t),
    }
}
pub fn water_boost(t: &str) -> i32 {
    match t {
        "PLUM" => 5,
        "LEMON" => 5,
        "APPLE" => 7,
        "BANANA" => 2,
        _ => panic!("unknown plant for water_boost: {}", t),
    }
}
pub type Cell = (i32, i32);
#[derive(Clone)]
pub struct Troll {
    pub id: i32,
    pub x: i32,
    pub y: i32,
    pub movement_speed: i32,
    pub carry_capacity: i32,
    pub harvest_power: i32,
    pub chop_power: i32,
    pub carry: [i32; 6],
}
impl Troll {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
    pub fn total_carried(&self) -> i32 {
        self.carry.iter().sum()
    }
    pub fn free_capacity(&self) -> i32 {
        self.carry_capacity - self.total_carried()
    }
    pub fn stats(&self) -> (i32, i32, i32, i32) {
        (
            self.movement_speed,
            self.carry_capacity,
            self.harvest_power,
            self.chop_power,
        )
    }
}
#[derive(Clone)]
pub struct Tree {
    pub tree_type: String,
    pub x: i32,
    pub y: i32,
    pub size: i32,
    pub health: i32,
    pub fruits: i32,
    pub cooldown: i32,
}
impl Tree {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
}
pub struct State {
    pub walkable: HashSet<Cell>,
    pub my_shack: Cell,
    pub opp_shack: Cell,
    pub my_inventory: [i32; 6],
    pub opp_inventory: [i32; 6],
    pub trees: Vec<Tree>,
    pub my_trolls: Vec<Troll>,
    pub opp_trolls: Vec<Troll>,
    pub turn: i32,
    pub iron_cells: HashSet<Cell>,
    pub water_cells: HashSet<Cell>,
}
pub const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];
pub fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
    let (x, y) = cell;
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
}
pub fn is_adjacent(a: Cell, b: Cell) -> bool {
    (a.0 - b.0).abs() + (a.1 - b.1).abs() == 1
}
pub fn bfs_distances(walkable: &HashSet<Cell>, sources: &[Cell]) -> HashMap<Cell, i32> {
    let mut dist: HashMap<Cell, i32> = HashMap::new();
    let mut queue: VecDeque<Cell> = VecDeque::new();
    for &cell in sources {
        if !dist.contains_key(&cell) {
            dist.insert(cell, 0);
            queue.push_back(cell);
        }
    }
    while let Some((x, y)) = queue.pop_front() {
        let d = dist[&(x, y)];
        for &(dx, dy) in &NEIGHBORS {
            let n = (x + dx, y + dy);
            if walkable.contains(&n) && !dist.contains_key(&n) {
                dist.insert(n, d + 1);
                queue.push_back(n);
            }
        }
    }
    dist
}
pub fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}
pub fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0i32; 6];
    cost[PLUM] = n + ms * ms;
    cost[LEMON] = n + cc * cc;
    cost[APPLE] = n + hp * hp;
    cost[IRON] = n + chop * chop;
    cost
}
pub fn afford_fruit_only(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}
pub fn mb_afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}
pub fn ge_fruit_ty(t: &str) -> Option<usize> {
    match t {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}
pub fn tie_salt(state: &State) -> u64 {
    let (sx, sy) = state.my_shack;
    let (ox, oy) = state.opp_shack;
    let mut h = 0x9E37_79B9_7F4A_7C15u64;
    for v in [
        sx as u64,
        sy as u64,
        ox as u64,
        oy as u64,
        state.walkable.len() as u64,
        state.water_cells.len() as u64,
        state.iron_cells.len() as u64,
    ] {
        h ^= v.wrapping_mul(0x0000_0100_0000_01B3);
        h = h.rotate_left(23).wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    }
    h
}
pub fn tie_mix(c: Cell, salt: u64) -> u64 {
    let mut h = salt
        ^ (c.0 as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (c.1 as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F);
    h ^= h >> 33;
    h = h.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    h ^= h >> 29;
    h
}
}
pub use state::*;
pub mod motion {
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};
thread_local! {
    static GE_LASTPOS: RefCell<HashMap<i32, (i32, i32, u8)>> = RefCell::new(HashMap::new());
}
pub fn reset() {
    GE_LASTPOS.with(|m| m.borrow_mut().clear());
}
pub fn pick_camp_cell(
    state: &State,
    shack: Cell,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
) -> Cell {
    let free = ortho_neighbors(shack)
        .into_iter()
        .filter(|c| state.walkable.contains(c) && !claimed.contains(c))
        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30));
    let cell = free
        .or_else(|| {
            ortho_neighbors(shack)
                .into_iter()
                .filter(|c| state.walkable.contains(c))
                .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
        })
        .unwrap_or(shack);
    claimed.insert(cell);
    cell
}
pub fn bank_cmd(
    state: &State,
    shack: Cell,
    u: &Troll,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
) -> String {
    if manhattan(u.pos(), shack) == 1 {
        format!("DROP {}", u.id)
    } else {
        let c = pick_camp_cell(state, shack, d, claimed);
        format!("MOVE {} {} {}", u.id, c.0, c.1)
    }
}
pub fn park_cmd(
    state: &State,
    shack: Cell,
    u: &Troll,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
    idle: bool,
) -> String {
    if idle {
        let camp_cells = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .count();
        if camp_cells <= 2 {
            let ring2 = state
                .walkable
                .iter()
                .filter(|c| manhattan(**c, shack) == 2 && !claimed.contains(*c))
                .filter_map(|c| d.get(c).map(|&dist| (*c, dist)))
                .min_by_key(|(c, dist)| (*dist, *c));
            if let Some((c, _)) = ring2 {
                claimed.insert(c);
                return format!("MOVE {} {} {}", u.id, c.0, c.1);
            }
        }
    }
    let c = pick_camp_cell(state, shack, d, claimed);
    format!("MOVE {} {} {}", u.id, c.0, c.1)
}
pub fn watchdog(state: &State, my: &[Troll], cmd_by_id: &mut HashMap<i32, String>) {
    GE_LASTPOS.with(|cell| {
        let mut m = cell.borrow_mut();
        for t in my {
            let cur = t.pos();
            let is_move = cmd_by_id
                .get(&t.id)
                .map_or(false, |c| c.starts_with("MOVE "));
            let entry = m.entry(t.id).or_insert((cur.0, cur.1, 0u8));
            let stuck = entry.0 == cur.0 && entry.1 == cur.1;
            entry.2 = if stuck && is_move {
                entry.2.saturating_add(1)
            } else {
                0
            };
            entry.0 = cur.0;
            entry.1 = cur.1;
            let streak = entry.2;
            if streak >= 2 && is_move {
                let tgt = cmd_by_id.get(&t.id).and_then(|c| {
                    let p: Vec<&str> = c.split_whitespace().collect();
                    if p.len() == 4 {
                        Some((p[2].parse::<i32>().ok()?, p[3].parse::<i32>().ok()?))
                    } else {
                        None
                    }
                });
                if let Some((tx, ty)) = tgt {
                    if (tx, ty) != cur {
                        let mut cands: Vec<Cell> = Vec::new();
                        for nb in ortho_neighbors(cur) {
                            if state.walkable.contains(&nb) && !my.iter().any(|o| o.pos() == nb) {
                                cands.push(nb);
                            }
                        }
                        if !cands.is_empty() {
                            let pick = cands[(rh_rand() as usize) % cands.len()];
                            cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, pick.0, pick.1));
                            entry.2 = 0;
                        }
                    }
                }
            }
        }
    });
}
pub fn solve_moves(state: &State, my: &[Troll], intents: &[(i32, Cell)]) -> HashMap<i32, Cell> {
    let moving: HashSet<i32> = intents.iter().map(|(id, _)| *id).collect();
    let stationary: HashSet<Cell> = my
        .iter()
        .filter(|t| !moving.contains(&t.id))
        .map(|t| t.pos())
        .collect();
    let mut intents: Vec<(i32, Cell)> = intents.to_vec();
    intents.sort();
    let mut ids: Vec<i32> = Vec::new();
    let mut cands: Vec<Vec<(Cell, i32)>> = Vec::new();
    for (id, goal) in &intents {
        let t = match my.iter().find(|t| t.id == *id) {
            Some(t) => t,
            None => continue,
        };
        let dg = bfs_distances(&state.walkable, &[*goal]);
        let dp = bfs_distances(&state.walkable, &[t.pos()]);
        let here = match dg.get(&t.pos()) {
            Some(&d) => d,
            None => {
                ids.push(*id);
                cands.push(vec![(t.pos(), 0)]);
                continue;
            }
        };
        let mut cs: Vec<(Cell, i32)> = state
            .walkable
            .iter()
            .filter(|c| {
                dp.get(*c)
                    .map_or(false, |&d| d > 0 && d <= t.movement_speed)
            })
            .filter(|c| !stationary.contains(*c))
            .filter_map(|c| dg.get(c).map(|&d| (*c, here - d)))
            .filter(|(_, pr)| *pr >= 0)
            .collect();
        cs.push((t.pos(), 0));
        cs.sort_by_key(|(c, pr)| (-pr, *c));
        cs.truncate(8);
        ids.push(*id);
        cands.push(cs);
    }
    let n = ids.len();
    let mut best: Option<(i32, Vec<Cell>)> = None;
    let mut pick = vec![0usize; n];
    loop {
        let landing: Vec<Cell> = (0..n).map(|i| cands[i][pick[i]].0).collect();
        let distinct = {
            let mut s: Vec<Cell> = landing.clone();
            s.sort();
            s.windows(2).all(|w| w[0] != w[1])
        };
        if distinct {
            let total: i32 = (0..n).map(|i| cands[i][pick[i]].1).sum();
            let better = match &best {
                None => true,
                Some((bt, bl)) => total > *bt || (total == *bt && landing < *bl),
            };
            if better {
                best = Some((total, landing));
            }
        }
        let mut i = 0;
        loop {
            if i == n {
                break;
            }
            pick[i] += 1;
            if pick[i] < cands[i].len() {
                break;
            }
            pick[i] = 0;
            i += 1;
        }
        if i == n {
            break;
        }
        if n == 0 {
            break;
        }
    }
    let mut out = HashMap::new();
    if let Some((_, landing)) = best {
        for (i, id) in ids.iter().enumerate() {
            out.insert(*id, landing[i]);
        }
    }
    out
}
}
pub mod planner {
use super::tactics::{Phase, Plan};
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};
thread_local! {
    static LAST_TGT: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
    static FLAPS: RefCell<u32> = RefCell::new(0);
}
pub fn reset() {
    LAST_TGT.with(|m| m.borrow_mut().clear());
    FLAPS.with(|f| *f.borrow_mut() = 0);
}
pub fn flaps() -> u32 {
    FLAPS.with(|f| *f.borrow())
}
const K: usize = 8;
const BAND: i64 = 100_000;
const STICKY: i64 = 6;
const DENY_W: i64 = 0;
const RACE_SHARE_PEN: i64 = 2;
#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Bank,
    Park,
    ChopHere,
    MoveTo,
    PlantHere,
    Harvest,
    Mine,
    Pick,
}
#[derive(Clone, Debug)]
struct Cand {
    kind: Kind,
    target: Option<Cell>,
    value: i64,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ClaimClass {
    Cell,
    Fruit,
    Wood,
}
#[derive(Clone, Copy, Debug)]
struct ClaimInfo {
    class: ClaimClass,
    cell: Cell,
    steps: i64,
}
#[derive(Clone, Debug)]
struct Assignments {
    ids: Vec<i32>,
    cands: Vec<Vec<Cand>>,
    picks: Vec<usize>,
}
impl Assignments {
    fn idx(&self, id: i32) -> Option<usize> {
        self.ids.binary_search(&id).ok()
    }
    fn selected(&self, id: i32) -> Option<&Cand> {
        let i = self.idx(id)?;
        self.cands.get(i)?.get(self.picks[i])
    }
    fn selected_value(&self, id: i32) -> Option<i64> {
        self.selected(id).map(|c| c.value)
    }
}
fn eta(d: &HashMap<Cell, i32>, c: Cell, ms: i32) -> i64 {
    let dist = d.get(&c).copied().unwrap_or(1 << 20);
    ((dist + ms - 1) / ms.max(1)) as i64
}
fn value_band(value: i64) -> i64 {
    (value + BAND - 1) / BAND
}
fn claim_info(state: &State, c: &Cand, steps: i64) -> Option<ClaimInfo> {
    let cell = c.target?;
    let class = match c.kind {
        Kind::ChopHere => ClaimClass::Wood,
        Kind::Harvest => ClaimClass::Fruit,
        Kind::MoveTo => {
            let targets_tree = state.trees.iter().any(|p| p.pos() == cell);
            if targets_tree {
                match value_band(c.value) {
                    70 | 40 | 30 => ClaimClass::Wood,
                    63 | 62 | 58 | 52 | 44 | 38 => ClaimClass::Fruit,
                    _ => ClaimClass::Cell,
                }
            } else {
                ClaimClass::Cell
            }
        }
        Kind::Bank | Kind::Park | Kind::PlantHere | Kind::Mine | Kind::Pick => ClaimClass::Cell,
    };
    Some(ClaimInfo { class, cell, steps })
}
fn claims_conflict(a: ClaimInfo, b: ClaimInfo) -> bool {
    if a.cell != b.cell {
        return false;
    }
    match (a.class, b.class) {
        (ClaimClass::Fruit, ClaimClass::Wood) => a.steps == 0 || a.steps >= b.steps,
        (ClaimClass::Wood, ClaimClass::Fruit) => b.steps == 0 || b.steps >= a.steps,
        _ => true,
    }
}
#[allow(clippy::too_many_lines)]
fn candidates(state: &State, plan: &Plan, my: &[Troll], u: &Troll, salt: u64) -> Vec<Cand> {
    let shack = plan.shack;
    let inv = &state.my_inventory;
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed;
    let is_chopper = u.chop_power >= 2;
    let mut out: Vec<Cand> = Vec::new();
    let hoard = plan.phase == Phase::Hoard;
    let enemy_d: Option<HashMap<Cell, i32>> = if hoard {
        Some(bfs_distances(
            &state.walkable,
            &state.opp_trolls.iter().map(|e| e.pos()).collect::<Vec<_>>(),
        ))
    } else {
        None
    };
    let threatened = |pc: Cell| -> bool {
        enemy_d
            .as_ref()
            .map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
    };
    let fell_ok = |p: &Tree| -> bool {
        if plan.seed_cells.contains(&p.pos()) {
            return false;
        }
        if plan.liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA"
            && plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.farm_r);
        p.size
            >= if farm_banana {
                plan.farm_fell
            } else {
                plan.fell_size
            }
    };
    let occupied_by_ripe_harvester = |p: &Tree| -> bool {
        p.fruits > 0
            && my.iter().any(|o| {
                o.id != u.id && o.pos() == p.pos() && o.harvest_power > 0 && o.free_capacity() > 0
            })
    };
    let own_half =
        |p: &Tree| plan.liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), plan.opp);
    let within_roam = |p: &Tree| {
        plan.liquidation
            || plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.chop_r)
    };
    let race = |pc: Cell, our_eta: i64| -> Option<i64> {
        let occupant = state
            .opp_trolls
            .iter()
            .find(|e| e.pos() == pc && e.chop_power > 0);
        match occupant {
            None => Some(0),
            Some(e) => {
                let h = state
                    .trees
                    .iter()
                    .find(|p| p.pos() == pc)
                    .map(|p| p.health)
                    .unwrap_or(0) as i64;
                let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
                if their_turns <= our_eta {
                    None
                } else {
                    Some(RACE_SHARE_PEN)
                }
            }
        }
    };
    let plant_cell: Option<Cell> = if plan.base_trees < plan.farm_cap {
        state
            .walkable
            .iter()
            .filter(|c| {
                plan.farm_d.get(*c).map_or(false, |&fd| fd <= plan.farm_r) && d.contains_key(*c)
            })
            .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
            .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
            .min_by_key(|c| {
                let wet = state.water_cells.iter().any(|w| manhattan(*w, **c) == 1);
                let bank_adj = plan.farm_d.get(*c).copied() == Some(1);
                let (cx, cy) = **c;
                let diag = (cx - plan.shack.0).abs() == 1 && (cy - plan.shack.1).abs() == 1;
                let geo = (if bank_adj { 3 } else { 0 }) + (if diag { -1 } else { 0 });
                (d[*c] + if wet { 0 } else { 2 } + geo, tie_mix(**c, salt))
            })
            .copied()
    } else {
        None
    };
    if u.total_carried() > 0 {
        let d_home = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .filter_map(|c| d.get(c))
            .min()
            .copied()
            .unwrap_or(i32::MAX / 2);
        let e = ((d_home + ms - 1) / ms.max(1) + 1) as i64;
        if (plan.turns_rem as i64) <= e + 1 {
            out.push(Cand {
                kind: Kind::Bank,
                target: None,
                value: 95 * BAND - e,
            });
        }
    }
    if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plant_cell.is_some()) {
        out.push(Cand {
            kind: Kind::Bank,
            target: None,
            value: 80 * BAND,
        });
    }
    if is_chopper {
        for p in state
            .trees
            .iter()
            .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
        {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if occupied_by_ripe_harvester(p) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue;
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue,
                Some(pen) => pen,
            };
            let deny_pen = DENY_W * (manhattan(pc, plan.opp) as i64 / 2);
            if pc == u.pos() {
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 72 * BAND - chop_t - race_pen - deny_pen,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen,
                });
            }
        }
        for p in state.trees.iter().filter(|p| p.size >= 1) {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if occupied_by_ripe_harvester(p) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue;
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue,
                Some(pen) => pen,
            };
            if pc == u.pos() {
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 31 * BAND - chop_t - race_pen,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 30 * BAND - (steps + chop_t) - race_pen,
                });
            }
        }
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
            target: None,
            value: 10 * BAND,
        });
    } else {
        if u.carry[BANANA] > 0 {
            if let Some(tc) = plant_cell {
                let kind = if u.pos() == tc {
                    Kind::PlantHere
                } else {
                    Kind::MoveTo
                };
                out.push(Cand {
                    kind,
                    target: Some(tc),
                    value: 88 * BAND - eta(&d, tc, ms),
                });
            }
        }
        if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
            if p.fruits > 0 && u.harvest_power > 0 && u.free_capacity() > 0 {
                let ty = ge_fruit_ty(&p.tree_type);
                let funding = plan.want_chopper || plan.want_feeder;
                let want = (funding && ty.map_or(false, |t| t < 3 && plan.need_fund[t]))
                    || (!plan.want_chopper
                        && (p.tree_type == "BANANA"
                            || (p.tree_type == "APPLE"
                                && state
                                    .water_cells
                                    .iter()
                                    .any(|w| manhattan(*w, p.pos()) == 1))))
                    || plan.phase == Phase::Hoard;
                if want {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(u.pos()),
                        value: 75 * BAND,
                    });
                }
            }
        }
        if plan.phase == Phase::Hoard {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 62 * BAND - eta(&d, pc, ms),
                });
            }
        }
        if plan.want_chopper || plan.want_feeder {
            let (fund_hi, fund_lo) = if plan.want_chopper {
                (60, 58)
            } else {
                (45, 44)
            };
            let ladder_funding = plan.want_feeder;
            if plan.need_iron && u.chop_power > 0 {
                if state
                    .iron_cells
                    .iter()
                    .any(|ic| manhattan(u.pos(), *ic) == 1)
                {
                    let v = if ladder_funding { 65 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::Mine,
                        target: Some(u.pos()),
                        value: v * BAND,
                    });
                } else if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| (d[c], tie_mix(*c, salt)))
                {
                    let v = if ladder_funding { 64 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(c),
                        value: v * BAND - eta(&d, c, ms),
                    });
                }
            }
            let fruit_band = if ladder_funding { 63 } else { fund_lo };
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && ge_fruit_ty(&p.tree_type).map_or(false, |t| t < 3 && plan.need_fund[t])
            }) {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: fruit_band * BAND - eta(&d, pc, ms),
                });
            }
        }
        if plan.base_trees < plan.farm_cap {
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && (p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state
                                .water_cells
                                .iter()
                                .any(|w| manhattan(*w, p.pos()) == 1)))
            }) {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 52 * BAND - eta(&d, pc, ms),
                });
            }
            if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
                if manhattan(u.pos(), shack) == 1 {
                    out.push(Cand {
                        kind: Kind::Pick,
                        target: Some(shack),
                        value: 50 * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::Park,
                        target: Some(shack),
                        value: 50 * BAND - 1,
                    });
                }
            }
        }
        if plan.starter_chop && u.chop_power > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
            {
                if u.free_capacity() == 0 {
                    break;
                }
                let pc = p.pos();
                if !d.contains_key(&pc) {
                    continue;
                }
                if occupied_by_ripe_harvester(p) {
                    continue;
                }
                if hoard && !threatened(pc) {
                    continue;
                }
                let steps = eta(&d, pc, ms);
                let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                let race_pen = match race(pc, steps) {
                    None => continue,
                    Some(pen) => pen,
                };
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::ChopHere,
                        target: Some(pc),
                        value: 42 * BAND - chop_t - race_pen,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 40 * BAND - (steps + chop_t) - race_pen,
                    });
                }
            }
            if u.free_capacity() > 0 {
                for p in state.trees.iter().filter(|p| p.size >= 1) {
                    let pc = p.pos();
                    if !d.contains_key(&pc) {
                        continue;
                    }
                    if occupied_by_ripe_harvester(p) {
                        continue;
                    }
                    if hoard && !threatened(pc) {
                        continue;
                    }
                    let steps = eta(&d, pc, ms);
                    let chop_t =
                        ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                    let race_pen = match race(pc, steps) {
                        None => continue,
                        Some(pen) => pen,
                    };
                    if pc == u.pos() {
                        out.push(Cand {
                            kind: Kind::ChopHere,
                            target: Some(pc),
                            value: 31 * BAND - chop_t - race_pen,
                        });
                    } else {
                        out.push(Cand {
                            kind: Kind::MoveTo,
                            target: Some(pc),
                            value: 30 * BAND - (steps + chop_t) - race_pen,
                        });
                    }
                }
            }
        }
        if u.harvest_power > 0 && u.free_capacity() > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                let steps = eta(&d, pc, ms);
                if race(pc, steps).is_none() {
                    continue;
                }
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(pc),
                        value: 38 * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 38 * BAND - steps,
                    });
                }
            }
        }
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
            target: None,
            value: 10 * BAND,
        });
    }
    let last = LAST_TGT.with(|m| m.borrow().get(&u.id).copied());
    if let Some(lt) = last {
        for c in out.iter_mut() {
            if c.target == Some(lt) {
                c.value += STICKY;
            }
        }
    }
    out.sort_by_key(|c| (-c.value, c.target));
    out.truncate(K);
    out
}
fn select_assignments(state: &State, plan: &Plan, my: &[Troll]) -> Assignments {
    let salt = tie_salt(state);
    let mut ids: Vec<i32> = my.iter().map(|t| t.id).collect();
    ids.sort();
    let trolls: Vec<&Troll> = ids
        .iter()
        .map(|id| my.iter().find(|t| t.id == *id).unwrap())
        .collect();
    let cands: Vec<Vec<Cand>> = trolls
        .iter()
        .map(|t| candidates(state, plan, my, t, salt))
        .collect();
    let claim_infos: Vec<Vec<Option<ClaimInfo>>> = trolls
        .iter()
        .zip(cands.iter())
        .map(|(t, cs)| {
            let d = bfs_distances(&state.walkable, &[t.pos()]);
            cs.iter()
                .map(|c| {
                    let steps = c.target.map_or(0, |tc| eta(&d, tc, t.movement_speed));
                    claim_info(state, c, steps)
                })
                .collect()
        })
        .collect();
    let n = ids.len();
    let mut best: Option<(i64, Vec<usize>)> = None;
    let mut pick = vec![0usize; n];
    if n > 0 {
        loop {
            let mut ok = true;
            for i in 0..n {
                for j in 0..i {
                    if let (Some(a), Some(b)) = (claim_infos[i][pick[i]], claim_infos[j][pick[j]]) {
                        if claims_conflict(a, b) {
                            ok = false;
                            break;
                        }
                    }
                }
                if !ok {
                    break;
                }
            }
            if ok {
                let total: i64 = (0..n).map(|i| cands[i][pick[i]].value).sum();
                let better = match &best {
                    None => true,
                    Some((bt, bp)) => total > *bt || (total == *bt && pick < *bp),
                };
                if better {
                    best = Some((total, pick.clone()));
                }
            }
            let mut i = 0;
            loop {
                if i == n {
                    break;
                }
                pick[i] += 1;
                if pick[i] < cands[i].len() {
                    break;
                }
                pick[i] = 0;
                i += 1;
            }
            if i == n {
                break;
            }
        }
    }
    Assignments {
        ids,
        cands,
        picks: best.map(|(_, picks)| picks).unwrap_or_default(),
    }
}
fn render_assignments(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &Assignments,
    update_last_target: bool,
) -> HashMap<i32, String> {
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let mut claimed_drop: HashSet<Cell> = HashSet::new();
    if !assignments.picks.is_empty() {
        for (i, id) in assignments.ids.iter().enumerate() {
            let u = my.iter().find(|t| t.id == *id).unwrap();
            let d = bfs_distances(&state.walkable, &[u.pos()]);
            let c = &assignments.cands[i][assignments.picks[i]];
            if update_last_target {
                if let (Kind::MoveTo, Some(tc)) = (&c.kind, c.target) {
                    LAST_TGT.with(|m| {
                        let mut m = m.borrow_mut();
                        if let Some(prev) = m.get(id) {
                            if *prev != tc && u.pos() != *prev {
                                FLAPS.with(|f| *f.borrow_mut() += 1);
                            }
                        }
                        m.insert(*id, tc);
                    });
                } else {
                    LAST_TGT.with(|m| m.borrow_mut().remove(id));
                }
            }
            let cmd = match (&c.kind, c.target) {
                (Kind::Bank, _) => motion::bank_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                (Kind::Park, park_target) => motion::park_cmd(
                    state,
                    plan.shack,
                    u,
                    &d,
                    &mut claimed_drop,
                    park_target.is_none(),
                ),
                (Kind::ChopHere, _) => format!("CHOP {}", u.id),
                (Kind::PlantHere, _) => format!("PLANT {} BANANA", u.id),
                (Kind::Harvest, _) => format!("HARVEST {}", u.id),
                (Kind::Mine, _) => format!("MINE {}", u.id),
                (Kind::Pick, _) => format!("PICK {} BANANA", u.id),
                (Kind::MoveTo, Some(tc)) => format!("MOVE {} {} {}", u.id, tc.0, tc.1),
                (Kind::MoveTo, None) => format!("MOVE {} {} {}", u.id, plan.shack.0, plan.shack.1),
            };
            cmd_by_id.insert(*id, cmd);
        }
    }
    cmd_by_id
}
fn move_intents(cmd_by_id: &HashMap<i32, String>) -> Vec<(i32, Cell)> {
    let mut intents: Vec<(i32, Cell)> = cmd_by_id
        .iter()
        .filter_map(|(id, c)| {
            let p: Vec<&str> = c.split_whitespace().collect();
            if p.len() == 4 && p[0] == "MOVE" {
                Some((*id, (p[2].parse().ok()?, p[3].parse().ok()?)))
            } else {
                None
            }
        })
        .collect();
    intents.sort();
    intents
}
fn pin_landing(my: &[Troll], cmd_by_id: &mut HashMap<i32, String>, landing: HashMap<i32, Cell>) {
    for (id, cell) in landing {
        let cur = my.iter().find(|t| t.id == id).map(|t| t.pos());
        if cur != Some(cell) {
            cmd_by_id.insert(id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
}
fn best_progress_without_stationary(
    state: &State,
    mover: &Troll,
    goal: Cell,
    stationary: &HashSet<Cell>,
) -> Option<i32> {
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let mut best = 0;
    for c in &state.walkable {
        if stationary.contains(c) {
            continue;
        }
        let Some(&from_here) = dp.get(c) else {
            continue;
        };
        if from_here == 0 || from_here > mover.movement_speed {
            continue;
        }
        let Some(&to_goal) = dg.get(c) else {
            continue;
        };
        let progress = here - to_goal;
        if progress >= 0 {
            best = best.max(progress);
        }
    }
    Some(best)
}
fn blocker_landing_progress(
    state: &State,
    mover: &Troll,
    goal: Cell,
    blocker_cell: Cell,
) -> Option<i32> {
    if !state.walkable.contains(&blocker_cell) {
        return None;
    }
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let from_here = *dp.get(&blocker_cell)?;
    if from_here == 0 || from_here > mover.movement_speed {
        return None;
    }
    let progress = here - *dg.get(&blocker_cell)?;
    (progress > 0).then_some(progress)
}
fn candidate_conflicts(
    assignments: &Assignments,
    blocker_idx: usize,
    target: Option<Cell>,
) -> bool {
    let Some(target) = target else {
        return false;
    };
    assignments.ids.iter().enumerate().any(|(i, _)| {
        i != blocker_idx && assignments.cands[i][assignments.picks[i]].target == Some(target)
    })
}
fn candidate_can_move_for_yield(plan: &Plan, u: &Troll, cand: &Cand) -> bool {
    match cand.kind {
        Kind::MoveTo | Kind::Park => true,
        Kind::Bank => manhattan(u.pos(), plan.shack) != 1,
        Kind::ChopHere | Kind::PlantHere | Kind::Harvest | Kind::Mine | Kind::Pick => false,
    }
}
fn reselect_blocker_for_yield(
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    blocker_id: i32,
) -> bool {
    let Some(blocker_idx) = assignments.idx(blocker_id) else {
        return false;
    };
    let Some(u) = my.iter().find(|t| t.id == blocker_id) else {
        return false;
    };
    let old_pick = assignments.picks[blocker_idx];
    let old_target = assignments.cands[blocker_idx][old_pick].target;
    for new_pick in 0..assignments.cands[blocker_idx].len() {
        if new_pick == old_pick {
            continue;
        }
        let cand = &assignments.cands[blocker_idx][new_pick];
        if old_target.is_some() && cand.target == old_target {
            continue;
        }
        if candidate_conflicts(assignments, blocker_idx, cand.target) {
            continue;
        }
        if !candidate_can_move_for_yield(plan, u, cand) {
            continue;
        }
        assignments.picks[blocker_idx] = new_pick;
        return true;
    }
    false
}
fn yield_pass(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    intents: &[(i32, Cell)],
    landing: &HashMap<i32, Cell>,
) -> bool {
    #[derive(Clone)]
    struct YieldCandidate {
        mover_id: i32,
        blocker_id: i32,
        mover_value: i64,
        blocker_value: i64,
    }
    let moving: HashSet<i32> = intents.iter().map(|(id, _)| *id).collect();
    let stationary_cells: HashSet<Cell> = my
        .iter()
        .filter(|t| !moving.contains(&t.id))
        .map(|t| t.pos())
        .collect();
    let stationary: Vec<&Troll> = my.iter().filter(|t| !moving.contains(&t.id)).collect();
    let mut pairs: Vec<YieldCandidate> = Vec::new();
    for (mover_id, goal) in intents {
        let Some(mover) = my.iter().find(|t| t.id == *mover_id) else {
            continue;
        };
        if landing.get(mover_id) != Some(&mover.pos()) {
            continue;
        }
        let Some(mover_value) = assignments.selected_value(*mover_id) else {
            continue;
        };
        let Some(normal_best) =
            best_progress_without_stationary(state, mover, *goal, &stationary_cells)
        else {
            continue;
        };
        if normal_best > 0 {
            continue;
        }
        for blocker in &stationary {
            let Some(blocker_value) = assignments.selected_value(blocker.id) else {
                continue;
            };
            if mover_value <= blocker_value {
                continue;
            }
            let Some(blocked_progress) =
                blocker_landing_progress(state, mover, *goal, blocker.pos())
            else {
                continue;
            };
            if blocked_progress > normal_best {
                pairs.push(YieldCandidate {
                    mover_id: *mover_id,
                    blocker_id: blocker.id,
                    mover_value,
                    blocker_value,
                });
            }
        }
    }
    pairs.sort_by_key(|p| (-p.mover_value, p.blocker_value, p.mover_id, p.blocker_id));
    for p in pairs {
        let mut trial = assignments.clone();
        if reselect_blocker_for_yield(plan, my, &mut trial, p.blocker_id) {
            *assignments = trial;
            if DEBUG {
                eprintln!(
                    "@TFYIELD t={} blocker={} mover={}",
                    state.turn, p.blocker_id, p.mover_id
                );
            }
            return true;
        }
    }
    false
}
pub fn assign(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let assignments = select_assignments(state, plan, my);
    render_assignments(state, plan, my, &assignments, true)
}
pub fn assign_resolved(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let mut assignments = select_assignments(state, plan, my);
    let initial_cmds = render_assignments(state, plan, my, &assignments, false);
    let initial_intents = move_intents(&initial_cmds);
    let initial_landing = motion::solve_moves(state, my, &initial_intents);
    let yielded = yield_pass(
        state,
        plan,
        my,
        &mut assignments,
        &initial_intents,
        &initial_landing,
    );
    let mut cmd_by_id = render_assignments(state, plan, my, &assignments, true);
    let landing = if yielded {
        let intents = move_intents(&cmd_by_id);
        motion::solve_moves(state, my, &intents)
    } else {
        initial_landing
    };
    pin_landing(my, &mut cmd_by_id, landing);
    cmd_by_id
}
}
pub mod tactics {
use super::*;
use std::cell::RefCell;
use std::collections::HashSet;
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
    static GE_CHOSEN_SPEC: RefCell<Option<(i32, i32, i32, i32)>> = RefCell::new(None);
}
pub fn reset() {
    GE_CHOSEN_SPEC.with(|c| *c.borrow_mut() = None);
}
pub struct Plan {
    pub shack: Cell,
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
fn plan_impl(state: &State, my: &[Troll], meta: Meta) -> Plan {
    let farm_d = bfs_distances(&state.walkable, &[state.my_shack]);
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
    let turns_rem = TOTAL_TURNS - state.turn + 1;
    let n = my.len() as i32;
    let spec = GE_CHOSEN_SPEC.with(|c| {
        let mut c = c.borrow_mut();
        if c.is_none() {
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
    let nchop = my.iter().filter(|u| u.chop_power >= 2).count() as i32;
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
        let want_chopper = want_chopper;
        let need_iron = have_iron
            && (want_chopper || want_feeder)
            && inv[IRON] < cost[IRON]
            && afford_fruit_only(inv, &cost);
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
    let phase = phase_for(meta, state.turn);
    let econ_b = false;
    let farm_r = if econ_b { 3 } else { GE_FARM_R };
    let farm_cap = if phase == Phase::Factory {
        20
    } else if econ_b {
        20
    } else {
        GE_FARM_MAX
    };
    let fell_size = GE_FELL_SIZE;
    let farm_fell = if econ_b { 3 } else { 2 };
    let chop_r = if econ_b { 10 } else { GE_CHOP_R };
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state
        .trees
        .iter()
        .filter(|p| farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r))
        .count();
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
    Plan {
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
    }
}
pub fn plan(state: &State, my: &[Troll]) -> Plan {
    plan_impl(state, my, super::GE_META)
}
pub fn plan_with_meta(state: &State, my: &[Troll], meta: Meta) -> Plan {
    plan_impl(state, my, meta)
}
}
const DEBUG: bool = true;
const MB_CHOPPER: (i32, i32, i32, i32) = (2, 3, 0, 3);
const MB_NCHOPPERS: i32 = 1;
const MB_HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const MB_MAX_TROLLS: usize = 4;
const MB_MAX_ORCHARD: usize = 2;
const MB_MIN_TURNS_LEFT: i32 = 20;
const MB_DENIAL_W: i32 = 0;
const MB_SIZE_W: i32 = 0;
thread_local! {
    static RH_RNG: RefCell<u64> = RefCell::new(0x9E3779B97F4A7C15);
}
fn rh_rand() -> u64 {
    RH_RNG.with(|rng| {
        let mut r = rng.borrow_mut();
        *r ^= *r << 13;
        *r ^= *r >> 7;
        *r ^= *r << 17;
        *r
    })
}
const GE_META: tactics::Meta = tactics::Meta::Tempo;
const GE_SPEC: (i32, i32, i32, i32) = (2, 3, 0, 2);
const GE_MAX_TROLLS: i32 = 2;
const GE_FEEDER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 0);
const GE_FEEDER_T: i32 = 45;
const GE_FEEDER_FARM: usize = 0;
const GE_CHOP_DELAY: i32 = 0;
const GE_CHOP_FARM: usize = 3;
const GE_FARM_R: i32 = 2;
const GE_FARM_MAX: usize = 12;
const GE_FELL_SIZE: i32 = 2;
const GE_CHOP_R: i32 = 5;
const GE_LIQ_T: i32 = 34;
const GE_STARTER_CHOP: bool = true;
const GE_MIN_TURNS_LEFT: i32 = 20;
const GE_SEED_RESERVE: usize = 2;
const GE_FARM_FELL: i32 = 3;
fn decide_elite(state: &State) -> Vec<String> {
    if state.turn == 1 {
        motion::reset();
        tactics::reset();
        planner::reset();
    }
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    let plan = tactics::plan(state, &my);
    let mut cmd_by_id = planner::assign_resolved(state, &plan, &my);
    if DEBUG && state.turn % 5 == 0 {
        eprintln!(
            "@TFFARM t={} farm={} seeds={} n={} flaps={} phase={:?}",
            state.turn,
            plan.farm_now,
            state.my_inventory[BANANA],
            my.len(),
            planner::flaps(),
            plan.phase
        );
    }
    motion::watchdog(state, &my, &mut cmd_by_id);
    let mut actions: Vec<String> = Vec::new();
    if state.turn == 1 {
        actions.push(format!("MSG v{}", VERSION));
    }
    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        actions.push(cmd_by_id[&id].clone());
    }
    if plan.train_now
        && TOTAL_TURNS - state.turn > GE_MIN_TURNS_LEFT
        && !my.iter().any(|u| u.pos() == plan.shack)
    {
        actions.push(format!(
            "TRAIN {} {} {} {}",
            plan.train_spec.0, plan.train_spec.1, plan.train_spec.2, plan.train_spec.3
        ));
    }
    if actions.is_empty() {
        actions.push("WAIT".into());
    }
    actions
}
fn parse_grid(grid_lines: &[String]) -> (HashSet<Cell>, Cell, Cell, HashSet<Cell>, HashSet<Cell>) {
    let mut walkable = HashSet::new();
    let mut iron = HashSet::new();
    let mut water = HashSet::new();
    let mut my_shack = (0i32, 0i32);
    let mut opp_shack = (0i32, 0i32);
    for (y, line) in grid_lines.iter().enumerate() {
        for (x, ch) in line.chars().enumerate() {
            let cell = (x as i32, y as i32);
            match ch {
                '0' => my_shack = cell,
                '1' => opp_shack = cell,
                '.' => {
                    walkable.insert(cell);
                }
                '+' => {
                    iron.insert(cell);
                }
                '~' => {
                    water.insert(cell);
                }
                _ => {}
            }
        }
    }
    (walkable, my_shack, opp_shack, iron, water)
}
fn read_line(reader: &mut impl BufRead) -> Option<String> {
    let mut s = String::new();
    match reader.read_line(&mut s) {
        Ok(0) => None,
        Ok(_) => Some(s.trim_end_matches('\n').trim_end_matches('\r').to_string()),
        Err(_) => None,
    }
}
fn parse_turn(
    reader: &mut impl BufRead,
    walkable: &HashSet<Cell>,
    my_shack: Cell,
    opp_shack: Cell,
    turn: i32,
    iron_cells: &HashSet<Cell>,
    water_cells: &HashSet<Cell>,
) -> Option<State> {
    let inv0_line = read_line(reader)?;
    let my_inventory: Vec<i32> = inv0_line
        .split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let inv1_line = read_line(reader)?;
    let opp_inventory: Vec<i32> = inv1_line
        .split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let tree_count_line = read_line(reader)?;
    let tree_count: usize = tree_count_line.trim().parse().unwrap();
    let mut trees = Vec::with_capacity(tree_count);
    for _ in 0..tree_count {
        let line = read_line(reader)?;
        let parts: Vec<&str> = line.split_whitespace().collect();
        trees.push(Tree {
            tree_type: parts[0].to_string(),
            x: parts[1].parse().unwrap(),
            y: parts[2].parse().unwrap(),
            size: parts[3].parse().unwrap(),
            health: parts[4].parse().unwrap(),
            fruits: parts[5].parse().unwrap(),
            cooldown: parts[6].parse().unwrap(),
        });
    }
    let troll_count_line = read_line(reader)?;
    let troll_count: usize = troll_count_line.trim().parse().unwrap();
    let mut my_trolls = Vec::new();
    let mut opp_trolls = Vec::new();
    for _ in 0..troll_count {
        let line = read_line(reader)?;
        let f: Vec<i32> = line
            .split_whitespace()
            .map(|v| v.parse().unwrap())
            .collect();
        let troll = Troll {
            id: f[0],
            x: f[2],
            y: f[3],
            movement_speed: f[4],
            carry_capacity: f[5],
            harvest_power: f[6],
            chop_power: f[7],
            carry: [f[8], f[9], f[10], f[11], f[12], f[13]],
        };
        if f[1] == 0 {
            my_trolls.push(troll);
        } else {
            opp_trolls.push(troll);
        }
    }
    let my_inv: [i32; 6] = [
        my_inventory[0],
        my_inventory[1],
        my_inventory[2],
        my_inventory[3],
        my_inventory[4],
        my_inventory[5],
    ];
    let opp_inv: [i32; 6] = [
        opp_inventory[0],
        opp_inventory[1],
        opp_inventory[2],
        opp_inventory[3],
        opp_inventory[4],
        opp_inventory[5],
    ];
    Some(State {
        walkable: walkable.clone(),
        my_shack,
        opp_shack,
        my_inventory: my_inv,
        opp_inventory: opp_inv,
        trees,
        my_trolls,
        opp_trolls,
        turn,
        iron_cells: iron_cells.clone(),
        water_cells: water_cells.clone(),
    })
}
fn debug_log(state: &State, grid: &[String], width: i32, height: i32) {
    if !DEBUG {
        return;
    }
    if state.turn == 1 {
        eprintln!("@TFMAP {} {}", width, height);
        for l in grid {
            eprintln!("@TFMAP {}", l.trim_end());
        }
        for t in &state.trees {
            eprintln!(
                "@TFI P {} {} {} {} {} {} {}",
                t.tree_type, t.x, t.y, t.size, t.health, t.fruits, t.cooldown
            );
        }
        for (pl, list) in [(0, &state.my_trolls), (1, &state.opp_trolls)] {
            for u in list {
                eprintln!(
                    "@TFI U {} {} {} {} {} {} {} {} {} {} {} {} {} {}",
                    u.id,
                    pl,
                    u.x,
                    u.y,
                    u.movement_speed,
                    u.carry_capacity,
                    u.harvest_power,
                    u.chop_power,
                    u.carry[0],
                    u.carry[1],
                    u.carry[2],
                    u.carry[3],
                    u.carry[4],
                    u.carry[5]
                );
            }
        }
    }
    let join = |a: &[i32; 6]| {
        a.iter()
            .map(|v| v.to_string())
            .collect::<Vec<_>>()
            .join(",")
    };
    let mut us = String::new();
    for u in &state.my_trolls {
        us.push_str(&format!("{},0,{},{};", u.id, u.x, u.y));
    }
    for u in &state.opp_trolls {
        us.push_str(&format!("{},1,{},{};", u.id, u.x, u.y));
    }
    eprintln!(
        "@TFD {} {} {} {}",
        state.turn,
        join(&state.my_inventory),
        join(&state.opp_inventory),
        us
    );
    let score = |inv: &[i32; 6]| inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5];
    let opp_builds: Vec<String> = state
        .opp_trolls
        .iter()
        .map(|u| {
            format!(
                "{}:{}.{}.{}.{}",
                u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power
            )
        })
        .collect();
    let my_builds: Vec<String> = state
        .my_trolls
        .iter()
        .map(|u| {
            format!(
                "{}:{}.{}.{}.{}",
                u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power
            )
        })
        .collect();
    eprintln!(
        "@TFSUM t={} me={} opp={} trees={} myinv=[{}] oppinv=[{}] mybuilds={} oppbuilds={}",
        state.turn,
        score(&state.my_inventory),
        score(&state.opp_inventory),
        state.trees.len(),
        join(&state.my_inventory),
        join(&state.opp_inventory),
        my_builds.join(","),
        opp_builds.join(",")
    );
}
pub fn run() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());
    let header = match read_line(&mut reader) {
        Some(s) => s,
        None => return,
    };
    let mut hw = header.split_whitespace();
    let width: i32 = hw.next().unwrap().parse().unwrap();
    let height: i32 = hw.next().unwrap().parse().unwrap();
    let mut grid_lines = Vec::with_capacity(height as usize);
    for _ in 0..height {
        match read_line(&mut reader) {
            Some(line) => grid_lines.push(line),
            None => return,
        }
    }
    let (walkable, my_shack, opp_shack, iron_cells, water_cells) = parse_grid(&grid_lines);
    let mut turn = 0i32;
    loop {
        turn += 1;
        match parse_turn(
            &mut reader,
            &walkable,
            my_shack,
            opp_shack,
            turn,
            &iron_cells,
            &water_cells,
        ) {
            None => break,
            Some(state) => {
                debug_log(&state, &grid_lines, width, height);
                let cmds = decide_elite(&state);
                if DEBUG {
                    let pos: Vec<String> = state
                        .my_trolls
                        .iter()
                        .map(|t| format!("{}@{},{}", t.id, t.x, t.y))
                        .collect();
                    let moves: Vec<String> = cmds
                        .iter()
                        .filter(|c| c.starts_with("MOVE "))
                        .cloned()
                        .collect();
                    eprintln!(
                        "@TFMOVE t={} pos=[{}] moves=[{}]",
                        state.turn,
                        pos.join(" "),
                        moves.join(" ")
                    );
                }
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}
fn main() {
    run();
}
