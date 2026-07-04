#![allow(dead_code, unused)]
use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};
const VERSION: &str = "1.4.1-nostarve";
const TOTAL_TURNS: i32 = 300;
const DEBUG: bool = false;
const PLUM: usize = 0;
const LEMON: usize = 1;
const APPLE: usize = 2;
const BANANA: usize = 3;
const IRON: usize = 4;
const WOOD: usize = 5;
fn plant_cooldown(t: &str) -> i32 {
    match t {
        "PLUM" => 8,
        "LEMON" => 8,
        "APPLE" => 9,
        "BANANA" => 6,
        _ => panic!("unknown plant: {}", t),
    }
}
fn water_boost(t: &str) -> i32 {
    match t {
        "PLUM" => 5,
        "LEMON" => 5,
        "APPLE" => 7,
        "BANANA" => 2,
        _ => panic!("unknown plant for water_boost: {}", t),
    }
}
type Cell = (i32, i32);
#[derive(Clone)]
struct Troll {
    id: i32,
    x: i32,
    y: i32,
    movement_speed: i32,
    carry_capacity: i32,
    harvest_power: i32,
    chop_power: i32,
    carry: [i32; 6],
}
impl Troll {
    fn pos(&self) -> Cell {
        (self.x, self.y)
    }
    fn total_carried(&self) -> i32 {
        self.carry.iter().sum()
    }
    fn free_capacity(&self) -> i32 {
        self.carry_capacity - self.total_carried()
    }
    fn stats(&self) -> (i32, i32, i32, i32) {
        (self.movement_speed, self.carry_capacity, self.harvest_power, self.chop_power)
    }
}
#[derive(Clone)]
struct Tree {
    tree_type: String,
    x: i32,
    y: i32,
    size: i32,
    health: i32,
    fruits: i32,
    cooldown: i32,
}
impl Tree {
    fn pos(&self) -> Cell {
        (self.x, self.y)
    }
}
struct State {
    walkable: HashSet<Cell>,
    my_shack: Cell,
    opp_shack: Cell,
    my_inventory: [i32; 6],
    opp_inventory: [i32; 6],
    trees: Vec<Tree>,
    my_trolls: Vec<Troll>,
    opp_trolls: Vec<Troll>,
    turn: i32,
    iron_cells: HashSet<Cell>,
    water_cells: HashSet<Cell>,
}
const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];
fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
    let (x, y) = cell;
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
}
fn is_adjacent(a: Cell, b: Cell) -> bool {
    (a.0 - b.0).abs() + (a.1 - b.1).abs() == 1
}
fn bfs_distances(walkable: &HashSet<Cell>, sources: &[Cell]) -> HashMap<Cell, i32> {
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
fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}
fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0i32; 6];
    cost[PLUM] = n + ms * ms;
    cost[LEMON] = n + cc * cc;
    cost[APPLE] = n + hp * hp;
    cost[IRON] = n + chop * chop;
    cost
}
fn afford_fruit_only(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}
const MB_CHOPPER: (i32, i32, i32, i32) = (2, 2, 0, 2);
const MB_NCHOPPERS: i32 = 2;
const MB_HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const MB_MAX_TROLLS: usize = 4;
const MB_MAX_ORCHARD: usize = 2;
const MB_MIN_TURNS_LEFT: i32 = 20;
const MB_DENIAL_W: i32 = 3;
const MB_SIZE_W: i32 = 0;
thread_local! {
    static MB_MEM: std::cell::RefCell<HashMap<i32, Cell>> = std::cell::RefCell::new(HashMap::new());
    static SB_PICKED: std::cell::RefCell<HashMap<i32, i32>> = std::cell::RefCell::new(HashMap::new());
}
fn mb_afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}
#[derive(Clone, Debug)]
enum SchedTask {
    Bank,
    Fell(Cell),
    Harvest(Cell),
    Mine(Cell),
    Print(Cell, usize),
    Orchard(Cell),
    PickSeed(usize),
}
fn decide_sched(state: &State) -> Vec<String> {
    if state.turn == 1 {
        SB_PICKED.with(|m| m.borrow_mut().clear());
    }
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
    let turns_rem = TOTAL_TURNS - state.turn + 1;
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    let n = my.len() as i32;
    let want_chopper = (my.iter().filter(|t| t.chop_power >= 2).count() as i32) < MB_NCHOPPERS;
    let train_now: Option<(i32, i32, i32, i32)> =
        if want_chopper && mb_afford(inv, &training_cost(n, MB_CHOPPER), have_iron) {
            Some(MB_CHOPPER)
        } else {
            MB_HARVESTERS.iter().copied().find(|&sp| mb_afford(inv, &training_cost(n, sp), have_iron))
        };
    let need_iron = have_iron
        && want_chopper
        && inv[IRON] < training_cost(n, MB_CHOPPER)[IRON]
        && afford_fruit_only(inv, &training_cost(n, MB_CHOPPER));
    let has_real_chopper = my.iter().any(|t| t.chop_power >= 2);
    let bootstrap_id: Option<i32> = if has_real_chopper {
        None
    } else {
        my.iter()
            .filter(|t| t.chop_power >= 1)
            .max_by_key(|t| (t.carry_capacity, -t.id))
            .map(|t| t.id)
    };
    let base_r = 3;
    let wf_cap = 10usize;
    let fell_base = 0.8f64;
    let print_v = 9.0f64;
    let orch_v = 10.0f64;
    let mine_v = 3.0f64;
    let base_trees = state.trees.iter().filter(|p| manhattan(p.pos(), shack) <= base_r).count();
    let next_cost = training_cost(n, MB_HARVESTERS[MB_HARVESTERS.len() - 1]);
    let need_fruit: [bool; 3] = [
        inv[0] < next_cost[0],
        inv[1] < next_cost[1],
        inv[2] < next_cost[2],
    ];
    let window = state.turn >= 20 && state.turn <= 280;
    let mut cands: Vec<(f64, usize, SchedTask)> = Vec::new();
    let mut dists: Vec<HashMap<Cell, i32>> = Vec::new();
    for (ti, t) in my.iter().enumerate() {
        let d = bfs_distances(&state.walkable, &[t.pos()]);
        let d_home = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .filter_map(|c| d.get(c))
            .min()
            .copied()
            .unwrap_or(1 << 20);
        let ms = t.movement_speed.max(1);
        let steps = |dist: i32| -> f64 { ((dist + ms - 1) / ms).max(0) as f64 };
        let carried: i32 = t
            .carry
            .iter()
            .enumerate()
            .map(|(i, c)| if i == WOOD { 4 * c } else { *c })
            .sum();
        if carried > 0 {
            let tt = steps(d_home) + 1.0;
            let endgame = (turns_rem as f64) <= tt + 2.0;
            if endgame {
                cands.push((1000.0 * carried as f64 / tt, ti, SchedTask::Bank));
            } else if t.free_capacity() == 0 {
                cands.push((carried as f64 / tt, ti, SchedTask::Bank));
            }
        }
        let is_chop_role = t.chop_power >= 2 || Some(t.id) == bootstrap_id;
        for p in &state.trees {
            let pos = p.pos();
            let dd = match d.get(&pos) {
                Some(&x) => x,
                None => continue,
            };
            let need_free = turns_rem <= 80;
            let my_score: i32 = state.my_inventory[0] + state.my_inventory[1]
                + state.my_inventory[2] + state.my_inventory[3] + 4 * state.my_inventory[5];
            let opp_score: i32 = state.opp_inventory[0] + state.opp_inventory[1]
                + state.opp_inventory[2] + state.opp_inventory[3] + 4 * state.opp_inventory[5];
            let clearing = false && turns_rem <= 60 && my_score - opp_score >= 40;
            let liquidation = turns_rem <= 280;
            if is_chop_role && t.chop_power > 0 && (!need_free || t.free_capacity() > 0) {
                let chop_t = ((p.health + t.chop_power - 1) / t.chop_power) as f64;
                let tt = steps(dd) + chop_t + 0.5 * steps(manhattan(pos, shack)) + 1.0;
                if turns_rem as f64 > tt {
                    let lemon_bonus = 0;
                    let rate = if liquidation {
                        (p.size.min(t.free_capacity()) * 4) as f64 / tt
                    } else if clearing {
                        2.0 - (dd + 3 * manhattan(pos, shack)) as f64 * 0.005
                    } else {
                        fell_base
                            - (dd + 3 * manhattan(pos, opp) - lemon_bonus) as f64 * 0.005
                    };
                    cands.push((rate, ti, SchedTask::Fell(pos)));
                }
            }
            if p.fruits > 0 && t.harvest_power > 0 && t.free_capacity() > 0 {
                let tt = steps(dd) + 1.0 + 0.5 * steps(manhattan(pos, shack));
                if turns_rem as f64 > tt {
                    let take = p.fruits.min(t.harvest_power).min(t.free_capacity()) as f64;
                    let ty = match p.tree_type.as_str() {
                        "PLUM" => 0,
                        "LEMON" => 1,
                        "APPLE" => 2,
                        _ => 3,
                    };
                    let mut rate = take / tt;
                    if ty < 3 && need_fruit[ty] {
                        rate *= 2.0;
                    }
                    cands.push((rate, ti, SchedTask::Harvest(pos)));
                }
            }
        }
        if !is_chop_role && t.chop_power > 0 && (state.my_inventory[BANANA] >= 1 || turns_rem <= 280) {
            for p in &state.trees {
                let pos = p.pos();
                let dd = match d.get(&pos) {
                    Some(&x) => x,
                    None => continue,
                };
                if manhattan(pos, shack) > 4 || p.size < 2 || p.fruits > 0 {
                    continue;
                }
                let chop_t = ((p.health + t.chop_power - 1) / t.chop_power) as f64;
                let wood = (p.size.min(t.free_capacity()) * 4) as f64 - 1.0;
                let tt = steps(dd) + chop_t + 0.5 * steps(manhattan(pos, shack)) + 1.0;
                if t.free_capacity() > 0 && (turns_rem as f64) > tt {
                    cands.push((wood / tt, ti, SchedTask::Fell(pos)));
                }
            }
        }
        if need_iron && t.chop_power > 0 && t.free_capacity() > 0 {
            if let Some(c) = state
                .iron_cells
                .iter()
                .flat_map(|ic| ortho_neighbors(*ic))
                .filter(|c| d.contains_key(c))
                .min_by_key(|c| d[c])
            {
                let tt = steps(d[&c]) + 1.0;
                cands.push((mine_v / tt, ti, SchedTask::Mine(c)));
            }
        }
        let orchard_n = state
            .trees
            .iter()
            .filter(|p| p.tree_type == "PLUM" && manhattan(p.pos(), shack) <= base_r)
            .count();
        if !is_chop_role && t.carry[PLUM] > 0 && orchard_n < MB_MAX_ORCHARD {
            let spot = state
                .walkable
                .iter()
                .filter(|c| manhattan(**c, shack) <= base_r && d.contains_key(*c))
                .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                .filter(|c| state.water_cells.iter().any(|w| manhattan(*w, **c) == 1))
                .filter(|c| !my.iter().any(|o| o.id != t.id && o.pos() == **c))
                .min_by_key(|c| d[*c])
                .copied();
            if let Some(sp) = spot {
                let tt = steps(d.get(&sp).copied().unwrap_or(1 << 20)) + 1.0;
                cands.push((orch_v / tt, ti, SchedTask::Orchard(sp)));
            }
        }
        if window && base_trees < wf_cap && !is_chop_role {
            let free_base = |water: bool| {
                state
                    .walkable
                    .iter()
                    .filter(|c| manhattan(**c, shack) <= base_r && d.contains_key(*c))
                    .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                    .filter(|c| {
                        !water || state.water_cells.iter().any(|w| manhattan(*w, **c) == 1)
                    })
                    .filter(|c| !my.iter().any(|o| o.id != t.id && o.pos() == **c))
                    .min_by_key(|c| d[*c])
                    .copied()
            };
            if let Some(sp) = free_base(true).or_else(|| free_base(false)) {
                let wet = state.water_cells.iter().any(|w| manhattan(*w, sp) == 1);
                let species: usize = if wet {
                    if inv[APPLE] >= 8 || t.carry[APPLE] > 0 {
                        APPLE
                    } else if inv[PLUM] >= 8 || t.carry[PLUM] > 0 {
                        PLUM
                    } else {
                        BANANA
                    }
                } else {
                    BANANA
                };
                if t.carry[species] > 0 {
                    let tt = steps(d.get(&sp).copied().unwrap_or(1 << 20)) + 1.0;
                    cands.push((print_v / tt, ti, SchedTask::Print(sp, species)));
                } else if manhattan(t.pos(), shack) == 1
                    && t.free_capacity() > 0
                    && inv[species] > 0
                    && !my.iter().any(|o| {
                        o.id != t.id && (o.carry[BANANA] > 0 || o.carry[species] > 0)
                    })
                    && SB_PICKED.with(|m| {
                        m.borrow().get(&t.id).map_or(true, |&t0| state.turn - t0 > 12)
                    })
                {
                    cands.push((print_v / 2.0, ti, SchedTask::PickSeed(species)));
                }
            }
        }
        dists.push(d);
    }
    cands.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
    let mut assigned: HashMap<usize, SchedTask> = HashMap::new();
    let mut taken: HashSet<Cell> = HashSet::new();
    for (_, ti, task) in cands {
        if assigned.contains_key(&ti) {
            continue;
        }
        let cell = match &task {
            SchedTask::Fell(c)
            | SchedTask::Harvest(c)
            | SchedTask::Mine(c)
            | SchedTask::Print(c, _)
            | SchedTask::Orchard(c) => Some(*c),
            _ => None,
        };
        if let Some(c) = cell {
            if taken.contains(&c) {
                continue;
            }
            taken.insert(c);
        }
        assigned.insert(ti, task);
    }
    SB_PICKED.with(|m| {
        let mut m = m.borrow_mut();
        for (ti, task) in &assigned {
            if matches!(task, SchedTask::PickSeed(_)) {
                m.insert(my[*ti].id, state.turn);
            }
        }
    });
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    for (ti, t) in my.iter().enumerate() {
        let d = &dists[ti];
        let go_move = |c: Cell| format!("MOVE {} {} {}", t.id, c.0, c.1);
        let drop_cell = || {
            ortho_neighbors(shack)
                .into_iter()
                .filter(|c| state.walkable.contains(c))
                .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                .unwrap_or(shack)
        };
        let cmd = match assigned.get(&ti) {
            Some(SchedTask::Bank) => {
                if is_adjacent(t.pos(), shack) {
                    format!("DROP {}", t.id)
                } else {
                    go_move(drop_cell())
                }
            }
            Some(SchedTask::Fell(c)) => {
                if t.pos() == *c {
                    format!("CHOP {}", t.id)
                } else {
                    go_move(*c)
                }
            }
            Some(SchedTask::Harvest(c)) => {
                if t.pos() == *c {
                    format!("HARVEST {}", t.id)
                } else {
                    go_move(*c)
                }
            }
            Some(SchedTask::Mine(c)) => {
                if t.pos() == *c {
                    format!("MINE {}", t.id)
                } else {
                    go_move(*c)
                }
            }
            Some(SchedTask::Print(c, sp)) => {
                if t.pos() == *c {
                    format!("PLANT {} {}", t.id, ["PLUM", "LEMON", "APPLE", "BANANA"][*sp])
                } else {
                    go_move(*c)
                }
            }
            Some(SchedTask::Orchard(c)) => {
                if t.pos() == *c {
                    format!("PLANT {} PLUM", t.id)
                } else {
                    go_move(*c)
                }
            }
            Some(SchedTask::PickSeed(sp)) => {
                format!("PICK {} {}", t.id, ["PLUM", "LEMON", "APPLE", "BANANA"][*sp])
            }
            None => {
                let anticipate = state
                    .trees
                    .iter()
                    .filter(|p| d.contains_key(&p.pos()))
                    .filter(|p| !taken.contains(&p.pos()))
                    .filter(|p| !my.iter().any(|o| o.id != t.id && o.pos() == p.pos()))
                    .filter_map(|p| {
                        let mut cd = plant_cooldown(&p.tree_type);
                        if state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1) {
                            cd -= water_boost(&p.tree_type);
                        }
                        let cd = cd.max(1);
                        let steps_needed = if p.size < 4 { 4 - p.size + 1 } else { 1 };
                        let ttr = p.cooldown + (steps_needed - 1) * cd;
                        let ms = t.movement_speed.max(1);
                        let arrive = (d[&p.pos()] + ms - 1) / ms;
                        if ttr <= 40 {
                            Some((arrive.max(ttr), d[&p.pos()], p.pos()))
                        } else {
                            None
                        }
                    })
                    .min()
                    .map(|(_, _, c)| c);
                match anticipate {
                    Some(c) => go_move(c),
                    None => {
                        let park = ortho_neighbors(shack)
                            .into_iter()
                            .filter(|c| state.walkable.contains(c))
                            .min_by_key(|c| {
                                let wet = state
                                    .water_cells
                                    .iter()
                                    .any(|w| manhattan(*w, *c) == 1);
                                (wet as i32, d.get(c).copied().unwrap_or(1 << 30))
                            })
                            .unwrap_or(shack);
                        go_move(park)
                    }
                }
            }
        };
        cmd_by_id.insert(t.id, cmd);
    }
    let mut actions: Vec<String> = Vec::new();
    if state.turn == 1 {
        actions.push(format!("MSG v{}", VERSION));
    }
    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        actions.push(cmd_by_id[&id].clone());
    }
    if let Some(spec) = train_now {
        if (n as usize) < MB_MAX_TROLLS
            && TOTAL_TURNS - state.turn > MB_MIN_TURNS_LEFT
            && !my.iter().any(|t| t.pos() == shack)
        {
            actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
    }
    if actions.is_empty() {
        actions.push("WAIT".to_string());
    }
    actions
}
use std::cell::RefCell;
use std::time::Instant;
pub const MAXW: usize = 22;
pub const MAXH: usize = 11;
pub const MAXC: usize = MAXW * MAXH;
pub const MAXP: usize = 72;
pub const MAXU: usize = 12;
#[inline]
pub fn cid(x: i8, y: i8, w: i8) -> usize {
    y as usize * w as usize + x as usize
}
fn derive_dims(st: &State) -> (i32, i32) {
    let mut mx = 0i32;
    let mut my = 0i32;
    {
        let mut upd = |c: Cell| {
            if c.0 > mx {
                mx = c.0;
            }
            if c.1 > my {
                my = c.1;
            }
        };
        for &c in &st.walkable {
            upd(c);
        }
        for &c in &st.iron_cells {
            upd(c);
        }
        for &c in &st.water_cells {
            upd(c);
        }
        upd(st.my_shack);
        upd(st.opp_shack);
        for t in &st.trees {
            upd((t.x, t.y));
        }
        for u in st.my_trolls.iter().chain(st.opp_trolls.iter()) {
            upd((u.x, u.y));
        }
    }
    (mx + 1, my + 1)
}
pub struct NavTable {
    pub w: i8,
    pub h: i8,
    pub walk: [bool; MAXC],
    pub dist: Vec<u8>,
    pub next: Vec<u8>,
    pub park: [u8; MAXC],
}
impl NavTable {
    fn build_from_state(st: &State) -> Box<NavTable> {
        let (wi, hi) = derive_dims(st);
        let w = wi as i8;
        let h = hi as i8;
        let mut nav = Box::new(NavTable {
            w,
            h,
            walk: [false; MAXC],
            dist: vec![255u8; MAXC * MAXC],
            next: vec![255u8; MAXC * MAXC],
            park: [255u8; MAXC],
        });
        for &(x, y) in &st.walkable {
            nav.walk[cid(x as i8, y as i8, w)] = true;
        }
        let mut sources: Vec<usize> = (0..(w as usize * h as usize)).filter(|&c| nav.walk[c]).collect();
        for &s in &[st.my_shack, st.opp_shack] {
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
                    nav.next[base + n] = if c == src { n as u8 } else { nav.next[base + c] };
                    q.push_back(n);
                }
            }
        }
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
    pub p_type: [u8; MAXP],
    pub p_x: [i8; MAXP],
    pub p_y: [i8; MAXP],
    pub p_size: [i8; MAXP],
    pub p_health: [i8; MAXP],
    pub p_fruits: [i8; MAXP],
    pub p_cd: [i8; MAXP],
    pub p_wet: [bool; MAXP],
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
    pub iron_adj: [bool; MAXC],
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
    fn from_state(st: &State) -> FastState {
        let (wi, hi) = derive_dims(st);
        let w = wi as i8;
        let h = hi as i8;
        let next_id = st
            .my_trolls
            .iter()
            .chain(st.opp_trolls.iter())
            .map(|u| u.id)
            .max()
            .unwrap_or(-1)
            + 1;
        let mut s = FastState {
            w,
            h,
            turn: st.turn as i16,
            next_id: next_id as i16,
            shack: [
                (st.my_shack.0 as i8, st.my_shack.1 as i8),
                (st.opp_shack.0 as i8, st.opp_shack.1 as i8),
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
            has_iron: !st.iron_cells.is_empty(),
        };
        for i in 0..6 {
            s.inv[0][i] = st.my_inventory[i] as i16;
            s.inv[1][i] = st.opp_inventory[i] as i16;
        }
        let wet = |c: Cell| st.water_cells.iter().any(|&(wx, wy)| (c.0 - wx).abs() + (c.1 - wy).abs() == 1);
        for pl in &st.trees {
            let i = s.n_plants as usize;
            if i >= MAXP {
                break;
            }
            s.p_type[i] = type_idx(&pl.tree_type);
            s.p_x[i] = pl.x as i8;
            s.p_y[i] = pl.y as i8;
            s.p_size[i] = pl.size as i8;
            s.p_health[i] = pl.health as i8;
            s.p_fruits[i] = pl.fruits as i8;
            s.p_cd[i] = pl.cooldown as i8;
            s.p_wet[i] = wet(pl.pos());
            s.n_plants += 1;
        }
        let mut merged: Vec<(u8, &Troll)> = st
            .my_trolls
            .iter()
            .map(|u| (0u8, u))
            .chain(st.opp_trolls.iter().map(|u| (1u8, u)))
            .collect();
        merged.sort_by_key(|&(_, u)| u.id);
        for (pl, u) in merged {
            let i = s.n_units as usize;
            if i >= MAXU {
                break;
            }
            s.u_id[i] = u.id as i16;
            s.u_pl[i] = pl;
            s.u_x[i] = u.x as i8;
            s.u_y[i] = u.y as i8;
            s.u_ms[i] = u.movement_speed as i8;
            s.u_cc[i] = u.carry_capacity as i8;
            s.u_hp[i] = u.harvest_power as i8;
            s.u_chop[i] = u.chop_power as i8;
            for k in 0..6 {
                s.u_carry[i][k] = u.carry[k] as i8;
            }
            s.n_units += 1;
        }
        for &(ix, iy) in &st.iron_cells {
            for (dx, dy) in [(0i32, 1i32), (1, 0), (0, -1), (-1, 0)] {
                let (nx, ny) = (ix + dx, iy + dy);
                if nx >= 0 && ny >= 0 && nx < wi && ny < hi {
                    s.iron_adj[cid(nx as i8, ny as i8, w)] = true;
                }
            }
        }
        for &(wx, wy) in &st.water_cells {
            for (dx, dy) in [(0i32, 1i32), (1, 0), (0, -1), (-1, 0)] {
                let (nx, ny) = (wx + dx, wy + dy);
                if nx >= 0 && ny >= 0 && nx < wi && ny < hi {
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
#[derive(Clone, Copy, PartialEq, Debug)]
pub enum FAct {
    Idle,
    Move(u8),
    Harvest,
    Chop,
    Drop,
    Mine,
    Plant(u8),
    Pick(u8),
}
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
pub fn step_fast(s: &mut FastState, nav: &NavTable, cmds: &[FCmds; 2]) {
    let w = s.w;
    for pl in 0..2u8 {
        let mut want: [Option<usize>; MAXU] = [None; MAXU];
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] != pl {
                continue;
            }
            if let FAct::Move(tgt) = cmds[pl as usize].acts[ui] {
                let from = cid(s.u_x[ui], s.u_y[ui], w);
                let mut to = tgt as usize;
                if !nav.walk[to] {
                    to = nav.park[to] as usize;
                }
                let d = nav.d(from, to);
                if d == 255 {
                    continue;
                }
                let ms = s.u_ms[ui] as u8;
                let mut cell = from;
                for _ in 0..ms.min(d) {
                    cell = nav.next[cell * MAXC + to] as usize;
                }
                if cell != from {
                    want[ui] = Some(cell);
                }
            }
        }
        let mut occ: [bool; MAXC] = [false; MAXC];
        for ui in 0..s.n_units as usize {
            if s.u_pl[ui] == pl {
                occ[cid(s.u_x[ui], s.u_y[ui], w)] = true;
            }
        }
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
    for round in 1..=3i8 {
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
            s.p_fruits[pi] = (s.p_fruits[pi] - took).max(0);
        }
    }
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
    let mut dead: [bool; MAXP] = [false; MAXP];
    for pi in 0..s.n_plants as usize {
        let (px, py) = (s.p_x[pi], s.p_y[pi]);
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
const H: usize = 40;
const PLAN_LEN: usize = 3;
#[derive(Clone, Copy, PartialEq)]
enum Task {
    Auto,
    GoTree(u8),
    GoBank,
    GoMine,
    PlantHere(u8),
}
#[derive(Clone, Copy)]
struct RheaPlan {
    tasks: [[Task; PLAN_LEN]; MAXU],
}
impl Default for RheaPlan {
    fn default() -> Self {
        RheaPlan { tasks: [[Task::Auto; PLAN_LEN]; MAXU] }
    }
}
thread_local! {
    static RH_NAV: RefCell<Option<Box<NavTable>>> = RefCell::new(None);
    static RH_BEST: RefCell<RheaPlan> = RefCell::new(RheaPlan::default());
    static RH_RNG: RefCell<u64> = RefCell::new(0x9E3779B97F4A7C15);
    static RH_LASTPOS: RefCell<HashMap<i32, (i8, i8, u8)>> = RefCell::new(HashMap::new());
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
const FB: f64 = 0.654;
const PRINT_V: f64 = 8.36;
const ORCH_V: f64 = 10.0;
const NEED_W: f64 = 1.0;
const RETW: f64 = 0.592;
const LIQ_T: i32 = 189;
const WF_MAX: i32 = 13;
const MOW_R: i32 = 4;
const CROP_RES: i16 = 8;
const LATE_FREE: i32 = 82;
const BASE_R: i32 = 3;
const ORCH_N: usize = 2;
fn policy_act(s: &FastState, nav: &NavTable, pl: usize, ui: usize, turns_rem: i32, reserved: &mut [bool; MAXC]) -> FAct {
    let w = s.w;
    let me = cid(s.u_x[ui], s.u_y[ui], w);
    let free = s.free(ui);
    let carried: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
    let sh = s.shack[pl];
    let osh = s.shack[1 - pl];
    let shc = cid(sh.0, sh.1, w);
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
    if carried > 0 {
        let eta = (dropd as i32 + s.u_ms[ui] as i32 - 1) / s.u_ms[ui].max(1) as i32 + 1;
        if turns_rem <= eta + 1 {
            return if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) };
        }
    }
    let ms = s.u_ms[ui].max(1) as i32;
    let steps = |dist: i32| -> f64 { ((dist + ms - 1) / ms).max(0) as f64 };
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
    let liquidation = turns_rem <= LIQ_T;
    let fell_needs_free = turns_rem <= LATE_FREE;
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
    if carried > 0 && free == 0 && dropc != usize::MAX {
        let t = steps(dropd as i32) + 1.0;
        consider!(
            carried as f64 / t,
            if adj_shack { FAct::Drop } else { FAct::Move(dropc as u8) },
            usize::MAX
        );
    }
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
        if is_chop_role && s.u_chop[ui] > 0 && (!fell_needs_free || free > 0) {
            let chop_t = ((s.p_health[pi] as i32 + s.u_chop[ui] as i32 - 1) / s.u_chop[ui] as i32) as f64;
            let t = steps(d as i32) + chop_t + 0.5 * steps(man_home) + 1.0;
            if turns_rem as f64 > t {
                let rate = if liquidation {
                    (s.p_size[pi].min(free) as i32 * 4) as f64 / t
                } else {
                    let man_opp = ((px - osh.0).abs() + (py - osh.1).abs()) as i32;
                    FB - (d as i32 + 3 * man_opp) as f64 * 0.005
                };
                consider!(rate, if me == pc { FAct::Chop } else { FAct::Move(pc as u8) }, pc);
            }
        }
        if mow_ok && free > 0 && man_home <= MOW_R && s.p_size[pi] >= 2 && s.p_fruits[pi] == 0 {
            let chop_t = ((s.p_health[pi] as i32 + s.u_chop[ui] as i32 - 1) / s.u_chop[ui] as i32) as f64;
            let t = steps(d as i32) + chop_t + 0.5 * steps(man_home) + 1.0;
            if turns_rem as f64 > t {
                let wood = (s.p_size[pi].min(free) as i32 * 4) as f64 - 1.0;
                consider!(wood / t, if me == pc { FAct::Chop } else { FAct::Move(pc as u8) }, pc);
            }
        }
        if s.p_fruits[pi] > 0 && s.u_hp[ui] > 0 && free > 0 {
            let t = steps(d as i32) + 1.0 + RETW * steps(man_home);
            if turns_rem as f64 > t {
                let mut rate = s.p_fruits[pi].min(s.u_hp[ui]).min(free) as f64 / t;
                let ty = s.p_type[pi] as usize;
                if ty < 3 && s.inv[pl][ty] < n_own + 1 {
                    rate *= 1.0 + NEED_W;
                }
                consider!(rate, if me == pc { FAct::Harvest } else { FAct::Move(pc as u8) }, pc);
            }
        }
    }
    let window = s.turn >= 20 && s.turn <= 230;
    let want_orch = !is_chop_role && s.u_carry[ui][0] > 0 && orchard_n < ORCH_N;
    let want_print = !is_chop_role && window && base_trees < WF_MAX;
    if want_orch || want_print {
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
        let mut print_key = (2i32, i32::MAX);
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
        if orch_c != usize::MAX {
            let t = steps(orch_d) + 1.0;
            consider!(
                ORCH_V / t,
                if me == orch_c { FAct::Plant(0) } else { FAct::Move(orch_c as u8) },
                orch_c
            );
        }
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
fn task_act(s: &FastState, nav: &NavTable, pl: usize, ui: usize, task: Task, root_plants: &[(i8, i8); 72], n_root_plants: usize) -> Option<FAct> {
    let w = s.w;
    match task {
        Task::Auto => None,
        Task::GoBank => {
            let carried: i32 = (0..6).map(|k| s.u_carry[ui][k] as i32).sum();
            if carried == 0 {
                return None;
            }
            let sh = s.shack[pl];
            if (s.u_x[ui] - sh.0).abs() + (s.u_y[ui] - sh.1).abs() <= 1 {
                Some(FAct::Drop)
            } else {
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
            let Some(pi) = s.plant_at(tx, ty) else { return None };
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
                return None;
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
fn rollout(root: &FastState, nav: &NavTable, plan: &RheaPlan, me: usize) -> f64 {
    let mut s = *root;
    let mut root_plants = [(0i8, 0i8); 72];
    let nrp = root.n_plants as usize;
    for i in 0..nrp {
        root_plants[i] = (root.p_x[i], root.p_y[i]);
    }
    let mut cursor = [0usize; MAXU];
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
        for pl in 0..2usize {
            let n = (0..s.n_units as usize).filter(|&ui| s.u_pl[ui] as usize == pl).count() as i16;
            if n >= 4 || turns_rem <= 20 {
                continue;
            }
            let n_chop = (0..s.n_units as usize)
                .filter(|&ui| s.u_pl[ui] as usize == pl && s.u_chop[ui] >= 2)
                .count();
            let afford = |t: (i8, i8, i8, i8)| -> bool {
                let c = training_cost_fast(n, t);
                (0..6).all(|i| (i == 4 && !s.has_iron) || s.inv[pl][i] >= c[i])
            };
            let spec = if n_chop < 2 && afford((2, 2, 0, 2)) {
                Some((2, 2, 0, 2))
            } else {
                [(2i8, 2i8, 2i8, 0i8), (1, 2, 2, 0), (1, 1, 1, 0)]
                    .into_iter()
                    .find(|&t| afford(t))
            };
            cmds[pl].train = spec;
        }
        step_fast(&mut s, nav, &cmds);
    }
    let mut carried = [0f64; 2];
    for ui in 0..s.n_units as usize {
        let v: i32 = (0..6).map(|k| if k == 5 { 4 * s.u_carry[ui][k] as i32 } else { s.u_carry[ui][k] as i32 }).sum();
        carried[s.u_pl[ui] as usize] += v as f64;
    }
    let mut trolls = [0f64; 2];
    for ui in 0..s.n_units as usize {
        trolls[s.u_pl[ui] as usize] += 1.0;
    }
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
fn decide_rhea(state: &State) -> Vec<String> {
    let t0 = Instant::now();
    let (wi, hi) = derive_dims(state);
    if wi as usize > MAXW || hi as usize > MAXH || state.my_trolls.len() + state.opp_trolls.len() > MAXU {
        return decide_sched(state);
    }
    let stale = RH_NAV.with(|n| match n.borrow().as_ref() {
        Some(nav) => nav.w as i32 != wi || nav.h as i32 != hi,
        None => true,
    });
    if state.turn == 1 || stale {
        RH_NAV.with(|n| *n.borrow_mut() = Some(NavTable::build_from_state(state)));
        RH_BEST.with(|b| *b.borrow_mut() = RheaPlan::default());
    }
    RH_NAV.with(|n| {
        let navb = n.borrow();
        rhea_decide(state, navb.as_ref().unwrap(), t0)
    })
}
fn rhea_decide(state: &State, nav: &NavTable, t0: Instant) -> Vec<String> {
    let root = FastState::from_state(state);
    let me = 0usize;
    let budget_ms: u128 = if state.turn == 1 { 550 } else { 28 };
    let nrp = (root.n_plants as usize).min(72);
    let my_units: Vec<usize> = (0..root.n_units as usize).filter(|&ui| root.u_pl[ui] as usize == me).collect();
    let mut best = RH_BEST.with(|b| *b.borrow());
    let mut best_v = rollout(&root, nav, &best, me);
    let policy_only = RheaPlan::default();
    let pv = rollout(&root, nav, &policy_only, me);
    if pv > best_v {
        best = policy_only;
        best_v = pv;
    }
    let mut evals = 2u32;
    while t0.elapsed().as_millis() < budget_ms {
        let mut cand = best;
        if my_units.is_empty() {
            break;
        }
        let ui = my_units[(rh_rand() as usize) % my_units.len()];
        for _ in 0..1 + (rh_rand() % 2) {
            let slot = (rh_rand() as usize) % PLAN_LEN;
            let roll = rh_rand() % 100;
            cand.tasks[ui][slot] = if roll < 45 && nrp > 0 {
                Task::GoTree((rh_rand() as usize % nrp) as u8)
            } else if roll < 60 {
                Task::GoBank
            } else if roll < 70 {
                Task::PlantHere(3)
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
    RH_BEST.with(|b| *b.borrow_mut() = best);
    let _ = evals;
    let turns_rem = 300 - root.turn as i32 + 1;
    let mut root_plants = [(0i8, 0i8); 72];
    for i in 0..nrp {
        root_plants[i] = (root.p_x[i], root.p_y[i]);
    }
    let mut reserved = [false; MAXC];
    let mut out: Vec<String> = Vec::new();
    if state.turn == 1 {
        out.push(format!("MSG v{}", VERSION));
    }
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
        {
            let id32 = root.u_id[ui] as i32;
            let cur = (root.u_x[ui], root.u_y[ui]);
            let mut streak = 0u8;
            RH_LASTPOS.with(|m| {
                let mut m = m.borrow_mut();
                let entry = m.entry(id32).or_insert((cur.0, cur.1, 0));
                let stuck = entry.0 == cur.0 && entry.1 == cur.1;
                if stuck && matches!(act, FAct::Move(_)) {
                    entry.2 = entry.2.saturating_add(1);
                } else {
                    entry.2 = 0;
                }
                *entry = (cur.0, cur.1, entry.2);
                streak = entry.2;
            });
            if streak >= 2 {
                if let FAct::Move(tgt) = act {
                    if tgt as usize != cid(cur.0, cur.1, root.w) {
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
                                root.u_pl[o] as usize == me && root.u_x[o] == nx && root.u_y[o] == ny
                            });
                            if !occupied {
                                cands.push(c as u8);
                            }
                        }
                        if !cands.is_empty() {
                            let pick = cands[(rh_rand() as usize) % cands.len()];
                            act = FAct::Move(pick);
                            RH_LASTPOS.with(|m| {
                                if let Some(e) = m.borrow_mut().get_mut(&id32) {
                                    e.2 = 0;
                                }
                            });
                        }
                    }
                }
            }
        }
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
    let n = my_units.len() as i32;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
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
        let sh = state.my_shack;
        if (n as usize) < 4
            && 300 - state.turn > 20
            && !state.my_trolls.iter().chain(state.opp_trolls.iter()).any(|u| u.pos() == sh)
        {
            out.push(format!("TRAIN {} {} {} {}", t.0, t.1, t.2, t.3));
        }
    }
    if out.is_empty() {
        out.push("WAIT".into());
    }
    out
}
const GE_SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2);
const GE_MAX_TROLLS: i32 = 2;
const GE_FARM_R: i32 = 3;
const GE_FARM_MAX: usize = 12;
const GE_FELL_SIZE: i32 = 2;
const GE_CHOP_R: i32 = 99;
const GE_LIQ_T: i32 = 34;
const GE_STARTER_CHOP: bool = true;
const GE_MIN_TURNS_LEFT: i32 = 20;
thread_local! {
    static GE_MEM: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
    static GE_LASTPOS: RefCell<HashMap<i32, (i32, i32, u8)>> = RefCell::new(HashMap::new());
}
fn ge_fruit_ty(t: &str) -> Option<usize> {
    match t {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}
fn decide_elite(state: &State) -> Vec<String> {
    if state.turn == 1 {
        GE_MEM.with(|m| m.borrow_mut().clear());
        GE_LASTPOS.with(|m| m.borrow_mut().clear());
    }
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
    let turns_rem = TOTAL_TURNS - state.turn + 1;
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    let n = my.len() as i32;
    let spec = GE_SPEC;
    let want_chopper = n < GE_MAX_TROLLS && !my.iter().any(|u| u.chop_power >= 2);
    let cost = training_cost(n, spec);
    let train_now = want_chopper && mb_afford(inv, &cost, have_iron);
    let need_iron =
        have_iron && want_chopper && inv[IRON] < cost[IRON] && afford_fruit_only(inv, &cost);
    let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];
    let farm_r = GE_FARM_R;
    let farm_cap = GE_FARM_MAX;
    let fell_size = GE_FELL_SIZE;
    let chop_r = GE_CHOP_R;
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state.trees.iter().filter(|p| manhattan(p.pos(), shack) <= farm_r).count();
    let own_half = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), opp);
    let within_roam = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= chop_r;
    let mut reserved: HashSet<Cell> = HashSet::new();
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let bank_cmd = |u: &Troll, d: &HashMap<Cell, i32>| -> String {
        if manhattan(u.pos(), shack) == 1 {
            format!("DROP {}", u.id)
        } else {
            let drop_cell = ortho_neighbors(shack)
                .into_iter()
                .filter(|c| state.walkable.contains(c))
                .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                .unwrap_or(shack);
            format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1)
        }
    };
    let park_cmd = |u: &Troll, d: &HashMap<Cell, i32>| -> String {
        let park = ortho_neighbors(shack)
            .into_iter()
            .filter(|c| state.walkable.contains(c))
            .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
            .unwrap_or(shack);
        format!("MOVE {} {} {}", u.id, park.0, park.1)
    };
    for u in &my {
        let d = bfs_distances(&state.walkable, &[u.pos()]);
        let is_chopper = u.chop_power >= 2;
        if u.total_carried() > 0 {
            let d_home = ortho_neighbors(shack)
                .iter()
                .filter(|c| state.walkable.contains(*c))
                .filter_map(|c| d.get(c))
                .min()
                .copied()
                .unwrap_or(i32::MAX / 2);
            let eta = (d_home + u.movement_speed - 1) / u.movement_speed.max(1) + 1;
            if turns_rem <= eta + 1 {
                cmd_by_id.insert(u.id, bank_cmd(u, &d));
                continue;
            }
        }
        let nearest_fell = |free_needed: bool| -> Option<Cell> {
            if free_needed && u.free_capacity() == 0 {
                return None;
            }
            state
                .trees
                .iter()
                .filter(|p| p.size >= if liquidation { 1 } else { fell_size })
                .filter(|p| own_half(p) && within_roam(p))
                .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                .min_by_key(|p| {
                    let steps = (d[&p.pos()] + u.movement_speed - 1) / u.movement_speed.max(1);
                    let chop_t = (p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1);
                    steps + chop_t
                })
                .map(|p| p.pos())
        };
        if is_chopper {
            if u.free_capacity() == 0 {
                cmd_by_id.insert(u.id, bank_cmd(u, &d));
                continue;
            }
            if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
                if u.chop_power > 0 && p.size >= if liquidation { 1 } else { fell_size } {
                    cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
            }
            if let Some(tc) = nearest_fell(false) {
                reserved.insert(tc);
                GE_MEM.with(|m| {
                    m.borrow_mut().insert(u.id, tc);
                });
                cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                continue;
            }
            if let Some(tc) = state
                .trees
                .iter()
                .filter(|p| p.size >= 1)
                .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                .min_by_key(|p| {
                    let steps = (d[&p.pos()] + u.movement_speed - 1) / u.movement_speed.max(1);
                    let chop_t = (p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1);
                    steps + chop_t
                })
                .map(|p| p.pos())
            {
                if u.pos() == tc {
                    cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                } else {
                    reserved.insert(tc);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                }
                continue;
            }
            cmd_by_id.insert(
                u.id,
                if u.total_carried() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) },
            );
            continue;
        }
        let free_base = |water: bool| -> Option<Cell> {
            state
                .walkable
                .iter()
                .filter(|c| manhattan(**c, shack) <= farm_r && d.contains_key(*c))
                .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                .filter(|c| !water || state.water_cells.iter().any(|w| manhattan(*w, **c) == 1))
                .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                .filter(|c| !reserved.contains(*c))
                .min_by_key(|c| d[*c])
                .copied()
        };
        if u.carry[BANANA] > 0 && base_trees < farm_cap {
            if let Some(tc) = free_base(true).or_else(|| free_base(false)) {
                reserved.insert(tc);
                if u.pos() == tc {
                    cmd_by_id.insert(u.id, format!("PLANT {} BANANA", u.id));
                } else {
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                }
                continue;
            }
        }
        if u.free_capacity() == 0 {
            cmd_by_id.insert(u.id, bank_cmd(u, &d));
            continue;
        }
        if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
            if p.fruits > 0 && u.harvest_power > 0 && u.free_capacity() > 0 {
                let ty = ge_fruit_ty(&p.tree_type);
                let want = if want_chopper {
                    ty.map_or(false, |t| t < 3 && need_fund[t])
                } else {
                    p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1))
                };
                if want {
                    cmd_by_id.insert(u.id, format!("HARVEST {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
            }
        }
        if want_chopper {
            if need_iron && u.chop_power > 0 {
                if state.iron_cells.iter().any(|ic| manhattan(u.pos(), *ic) == 1) {
                    cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                    continue;
                }
                if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c) && !reserved.contains(c))
                    .min_by_key(|c| d[c])
                {
                    reserved.insert(c);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                    continue;
                }
            }
            let target = state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                .filter(|p| ge_fruit_ty(&p.tree_type).map_or(false, |t| t < 3 && need_fund[t]))
                .min_by_key(|p| d[&p.pos()])
                .map(|p| p.pos());
            if let Some(tc) = target {
                reserved.insert(tc);
                GE_MEM.with(|m| {
                    m.borrow_mut().insert(u.id, tc);
                });
                cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                continue;
            }
        }
        if base_trees < farm_cap {
            if manhattan(u.pos(), shack) == 1 && inv[BANANA] > 0 && u.free_capacity() > 0 {
                cmd_by_id.insert(u.id, format!("PICK {} BANANA", u.id));
                continue;
            }
            if inv[BANANA] > 0 {
                cmd_by_id.insert(u.id, park_cmd(u, &d));
                continue;
            }
            let seed_tree = state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                .filter(|p| {
                    p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1))
                })
                .min_by_key(|p| d[&p.pos()])
                .map(|p| p.pos());
            if let Some(tc) = seed_tree {
                reserved.insert(tc);
                GE_MEM.with(|m| {
                    m.borrow_mut().insert(u.id, tc);
                });
                cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                continue;
            }
        }
        if starter_chop && u.chop_power > 0 {
            if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
                if p.size >= if liquidation { 1 } else { fell_size } {
                    cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
            }
            if let Some(tc) = nearest_fell(true) {
                reserved.insert(tc);
                cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                continue;
            }
        }
        cmd_by_id.insert(
            u.id,
            if u.total_carried() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) },
        );
    }
    GE_LASTPOS.with(|cell| {
        let mut m = cell.borrow_mut();
        for t in &my {
            let cur = t.pos();
            let is_move = cmd_by_id.get(&t.id).map_or(false, |c| c.starts_with("MOVE "));
            let entry = m.entry(t.id).or_insert((cur.0, cur.1, 0u8));
            let stuck = entry.0 == cur.0 && entry.1 == cur.1;
            entry.2 = if stuck && is_move { entry.2.saturating_add(1) } else { 0 };
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
                            if state.walkable.contains(&nb)
                                && !my.iter().any(|o| o.pos() == nb)
                            {
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
    let mut actions: Vec<String> = Vec::new();
    if state.turn == 1 {
        actions.push(format!("MSG v{}", VERSION));
    }
    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        actions.push(cmd_by_id[&id].clone());
    }
    if train_now
        && TOTAL_TURNS - state.turn > GE_MIN_TURNS_LEFT
        && !my.iter().any(|u| u.pos() == shack)
    {
        actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
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
                '.' => { walkable.insert(cell); }
                '+' => { iron.insert(cell); }
                '~' => { water.insert(cell); }
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
    let my_inventory: Vec<i32> = inv0_line.split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let inv1_line = read_line(reader)?;
    let opp_inventory: Vec<i32> = inv1_line.split_whitespace()
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
        let f: Vec<i32> = line.split_whitespace()
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
    let my_inv: [i32; 6] = [my_inventory[0], my_inventory[1], my_inventory[2],
                            my_inventory[3], my_inventory[4], my_inventory[5]];
    let opp_inv: [i32; 6] = [opp_inventory[0], opp_inventory[1], opp_inventory[2],
                             opp_inventory[3], opp_inventory[4], opp_inventory[5]];
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
                    u.id, pl, u.x, u.y, u.movement_speed, u.carry_capacity,
                    u.harvest_power, u.chop_power, u.carry[0], u.carry[1],
                    u.carry[2], u.carry[3], u.carry[4], u.carry[5]
                );
            }
        }
    }
    let join = |a: &[i32; 6]| a.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",");
    let mut us = String::new();
    for u in &state.my_trolls {
        us.push_str(&format!("{},0,{},{};", u.id, u.x, u.y));
    }
    for u in &state.opp_trolls {
        us.push_str(&format!("{},1,{},{};", u.id, u.x, u.y));
    }
    eprintln!("@TFD {} {} {} {}", state.turn, join(&state.my_inventory), join(&state.opp_inventory), us);
    let score = |inv: &[i32; 6]| inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5];
    let opp_builds: Vec<String> = state
        .opp_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    let my_builds: Vec<String> = state
        .my_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    eprintln!(
        "@TFSUM t={} me={} opp={} trees={} myinv=[{}] oppinv=[{}] mybuilds={} oppbuilds={}",
        state.turn, score(&state.my_inventory), score(&state.opp_inventory), state.trees.len(),
        join(&state.my_inventory), join(&state.opp_inventory),
        my_builds.join(","), opp_builds.join(",")
    );
}
fn main() {
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
        match parse_turn(&mut reader, &walkable, my_shack, opp_shack, turn, &iron_cells, &water_cells) {
            None => break,
            Some(state) => {
                debug_log(&state, &grid_lines, width, height);
                let cmds = decide_elite(&state);
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}
