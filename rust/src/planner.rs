#![allow(dead_code, unused)]
//! Pure planner logic mirrored from the CG submission (src/main.rs, v0.7.5), with
//! the stdin/stdout I/O stripped, exposed as a lib module so the local tournament
//! can rank our REAL bot against the other strategies. Keep in sync with main.rs.

use std::collections::{HashMap, HashSet, VecDeque};

// ── constants ───────────────────────────────────────────────────────────────

const VERSION: &str = "0.9.0";
const TOTAL_TURNS: i32 = 300;
// PURE HARVESTER mode. The real arena Boss 4 (config/level2/Boss.cs) is a 2-troll
// SUSTAINABLE FARMER that never chops -- it out-harvests a scorch-earth chopper over
// 300 turns (we lost 89-222 while chopping). Against a replanter, denial is self-
// defeating: it starves our own renewable fruit economy for a one-time wood payout.
// So NO_CHOP disables all chopping/mining/chopper-training -- the bot becomes a
// many-harvester farmer (BFS + ripeness routing) that out-farms the boss's 2 gatherers.
const NO_CHOP: bool = true;
// Flip to true for a SIM-FIDELITY validation run: echoes the full per-turn state
// to stderr (captured in the replay) so we can replay a real game through the sim
// and compare turn-by-turn. Off by default (no effect on play or stdout parity).
const DEBUG: bool = false;

// Item indices: PLUM=0, LEMON=1, APPLE=2, BANANA=3, IRON=4, WOOD=5
const PLUM: usize = 0;
const LEMON: usize = 1;
const APPLE: usize = 2;
const BANANA: usize = 3;
const IRON: usize = 4;
const WOOD: usize = 5;

fn item_index(name: &str) -> usize {
    match name {
        "PLUM" => PLUM,
        "LEMON" => LEMON,
        "APPLE" => APPLE,
        "BANANA" => BANANA,
        "IRON" => IRON,
        "WOOD" => WOOD,
        _ => panic!("unknown item: {}", name),
    }
}

// Base growth cooldown per tree type
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

const MAX_SIZE: i32 = 4;
const MAX_FRUITS: i32 = 3;
const WOOD_POINTS: f64 = 4.0;
const INF: f64 = f64::INFINITY;
const RIPEN_HORIZON: i32 = 120;
const RAMP_DELAY_CAP: i32 = 8;

// ── PARAMS ──────────────────────────────────────────────────────────────────

struct Params {
    topup_radius: i32,
    max_trolls: usize,
    iron_target: i32,
    min_turns_left_to_train: i32,
    opening_turns: i32,
    opening_max_trolls: usize,
    opening_spec: (i32, i32, i32, i32),
    opening_chopper_specs: &'static [(i32, i32, i32, i32)],
    plant_enabled: bool,
    max_orchard: usize,
}

const PARAMS: Params = Params {
    topup_radius: 4,
    max_trolls: 5,
    iron_target: 18,
    min_turns_left_to_train: 25,
    opening_turns: 30,
    opening_max_trolls: 3,
    opening_spec: (1, 1, 1, 0),
    opening_chopper_specs: &[
        (2, 2, 1, 2),
        (2, 2, 0, 2),
        (2, 1, 0, 2),
        (1, 2, 0, 2),
        (1, 1, 0, 2),
    ],
    plant_enabled: true,
    max_orchard: 3,
};

// GATHERER_SPECS / CHOPPER_SPECS
const GATHERER_SPECS: [(i32, i32, i32, i32); 3] = [(1, 1, 1, 0), (1, 2, 1, 0), (2, 2, 2, 0)];
const CHOPPER_SPECS: [(i32, i32, i32, i32); 3] = [(1, 3, 0, 2), (2, 4, 0, 3), (2, 4, 0, 4)];

// ── data structures ─────────────────────────────────────────────────────────

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
    pub tree_type: String, // "PLUM","LEMON","APPLE","BANANA"
    pub x: i32,
    pub y: i32,
    pub size: i32,
    pub health: i32,
    pub fruits: i32,
    pub cooldown: i32,
}

impl Tree {
    fn pos(&self) -> Cell {
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

// ── geometry helpers ─────────────────────────────────────────────────────────

const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];

fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
    let (x, y) = cell;
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
}

fn is_adjacent(a: Cell, b: Cell) -> bool {
    (a.0 - b.0).abs() + (a.1 - b.1).abs() == 1
}

// ── BFS ─────────────────────────────────────────────────────────────────────

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

// ── plant simulation ─────────────────────────────────────────────────────────

fn predict_fruits(
    plant_type: &str,
    mut size: i32,
    mut fruits: i32,
    mut cooldown: i32,
    ticks: i32,
) -> i32 {
    let base = plant_cooldown(plant_type);
    for _ in 0..ticks {
        if cooldown > 0 {
            cooldown -= 1;
        }
        if cooldown == 0 {
            if size < MAX_SIZE {
                size += 1;
                cooldown = base;
            } else if fruits < MAX_FRUITS {
                fruits += 1;
                cooldown = base;
            }
        }
    }
    fruits
}

fn ticks_until_ripe(tree: &Tree, min_offset: i32) -> Option<i32> {
    for offset in min_offset..=RIPEN_HORIZON {
        if predict_fruits(
            &tree.tree_type,
            tree.size,
            tree.fruits,
            tree.cooldown,
            offset,
        ) > 0
        {
            return Some(offset);
        }
    }
    None
}

// ── training cost ────────────────────────────────────────────────────────────

fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0i32; 6];
    cost[PLUM] = n + ms * ms;
    cost[LEMON] = n + cc * cc;
    cost[APPLE] = n + hp * hp;
    cost[IRON] = n + chop * chop;
    cost
}

// ── Rates ────────────────────────────────────────────────────────────────────

struct Rates {
    fruit_supply: [f64; 4],
    mean_dist: f64,
    mean_tree_size: f64,
    mean_tree_health: f64,
    iron_dist: f64,
}

fn effective_cooldown(state: &State, tree: &Tree) -> i32 {
    let mut cd = plant_cooldown(&tree.tree_type);
    let (tx, ty) = tree.pos();
    let near_water = state
        .water_cells
        .iter()
        .any(|&(wx, wy)| (tx - wx).abs() + (ty - wy).abs() == 1);
    if near_water {
        cd -= water_boost(&tree.tree_type);
    }
    cd.max(1)
}

fn estimate_rates(state: &State) -> Rates {
    let shack_adj: Vec<Cell> = ortho_neighbors(state.my_shack)
        .iter()
        .filter(|n| state.walkable.contains(n))
        .copied()
        .collect();
    let dist = bfs_distances(&state.walkable, &shack_adj);

    let mut supply = [0.0f64; 4];
    let mut dsum = 0.0f64;
    let mut size_sum = 0.0f64;
    let mut health_sum = 0.0f64;
    let mut n = 0usize;

    for t in &state.trees {
        if !dist.contains_key(&t.pos()) {
            continue;
        }
        // fruit tree check: PLUM/LEMON/APPLE/BANANA all have water_boost
        let idx = item_index(&t.tree_type);
        if idx < 4 {
            supply[idx] += 1.0 / effective_cooldown(state, t) as f64;
        }
        dsum += dist[&t.pos()] as f64;
        size_sum += t.size.max(1) as f64;
        health_sum += t.health.max(1) as f64;
        n += 1;
    }

    let mean_dist = if n > 0 { dsum / n as f64 } else { 4.0 };
    let mean_size = if n > 0 { size_sum / n as f64 } else { 1.0 };
    let mean_health = if n > 0 { health_sum / n as f64 } else { 6.0 };

    let iron_dist = if state.iron_cells.is_empty() {
        INF
    } else {
        let mut best = INF;
        for &ic in &state.iron_cells {
            for nb in ortho_neighbors(ic) {
                if let Some(&d) = dist.get(&nb) {
                    if (d as f64) < best {
                        best = d as f64;
                    }
                }
            }
        }
        best
    };

    Rates {
        fruit_supply: supply,
        mean_dist,
        mean_tree_size: mean_size,
        mean_tree_health: mean_health,
        iron_dist,
    }
}

fn has_iron(rates: &Rates) -> bool {
    rates.iron_dist != INF
}

// ── rate functions ───────────────────────────────────────────────────────────

fn gatherer_rate(rates: &Rates, stats: (i32, i32, i32, i32)) -> f64 {
    let (ms, cc, _hp, _chop) = stats;
    let cycle = 2.0 * rates.mean_dist / (ms.max(1) as f64) + 1.0;
    cc as f64 / cycle
}

fn chopper_wood_rate(rates: &Rates, stats: (i32, i32, i32, i32)) -> f64 {
    let (ms, cc, _hp, chop) = stats;
    if chop <= 0 {
        return 0.0;
    }
    // Python: fell = max(1.0, -(-mean_tree_health // chop))
    // Python floor division: -(-h // c) is ceil(h/c) for positive values
    let fell = (rates.mean_tree_health / chop as f64).ceil().max(1.0);
    let travel = 2.0 * rates.mean_dist / (ms.max(1) as f64);
    let wood_per_trip = (cc as f64).min(rates.mean_tree_size);
    wood_per_trip / (fell + travel + 1.0)
}

fn chopper_iron_rate(rates: &Rates, stats: (i32, i32, i32, i32)) -> f64 {
    let (ms, cc, _hp, chop) = stats;
    if chop <= 0 || !has_iron(rates) {
        return 0.0;
    }
    let travel = 2.0 * rates.iron_dist / (ms.max(1) as f64);
    let iron_per_trip = (cc as f64).min(chop as f64);
    iron_per_trip / (travel + 1.0)
}

// ── role ─────────────────────────────────────────────────────────────────────

const ROLE_CHOP: u8 = 0;
const ROLE_GATH: u8 = 1;

fn role_of(stats: (i32, i32, i32, i32)) -> u8 {
    if stats.3 >= 2 {
        ROLE_CHOP
    } else {
        ROLE_GATH
    }
}

// ── project ──────────────────────────────────────────────────────────────────

fn project(state: &State, policy: &[(i32, i32, i32, i32)], rates: &Rates) -> f64 {
    let mut banked: [f64; 6] = [
        state.my_inventory[0] as f64,
        state.my_inventory[1] as f64,
        state.my_inventory[2] as f64,
        state.my_inventory[3] as f64,
        state.my_inventory[4] as f64,
        state.my_inventory[5] as f64,
    ];
    // roster: (role, stats)
    let mut roster: Vec<(u8, (i32, i32, i32, i32))> = state
        .my_trolls
        .iter()
        .map(|t| (role_of(t.stats()), t.stats()))
        .collect();
    // pending: (ready_at, role, stats)
    let mut pending: Vec<(i32, u8, (i32, i32, i32, i32))> = Vec::new();
    let mut bi = 0usize;
    let ramp = ((rates.mean_dist as i32) + 1).min(RAMP_DELAY_CAP);

    // pay indices: iron index included only if has_iron
    let pay: &[usize] = if has_iron(rates) {
        &[0, 1, 2, 4]
    } else {
        &[0, 1, 2]
    };

    for t in state.turn..=TOTAL_TURNS {
        // mature pending trolls
        let matured: Vec<_> = pending.iter().filter(|p| p.0 <= t).cloned().collect();
        for m in &matured {
            roster.push((m.1, m.2));
        }
        pending.retain(|p| p.0 > t);

        let n_now = (roster.len() + pending.len()) as i32;

        let mut need = [0.0f64; 6];
        if bi < policy.len() {
            let cost = training_cost(n_now, policy[bi]);
            for i in 0..6 {
                need[i] = (cost[i] as f64 - banked[i]).max(0.0);
            }
        }
        // suppress iron need if no choppers
        let has_choppers = roster.iter().any(|(r, _)| *r == ROLE_CHOP)
            || pending.iter().any(|(_, r, _)| *r == ROLE_CHOP);
        if need[IRON] > 0.0 && !has_choppers {
            need = [0.0; 6];
        }

        // gatherers: allocate supply to needed types first, then highest supply
        let mut remaining: f64 = roster
            .iter()
            .filter(|(r, _)| *r == ROLE_GATH)
            .map(|(_, s)| gatherer_rate(rates, *s))
            .sum();

        // sort fruit indices by (-need[j], -supply[j])
        let mut fruit_order: [usize; 4] = [0, 1, 2, 3];
        fruit_order.sort_by(|&a, &b| {
            let ka = (-need[a], -rates.fruit_supply[a]);
            let kb = (-need[b], -rates.fruit_supply[b]);
            ka.partial_cmp(&kb).unwrap()
        });
        for i in fruit_order {
            if remaining <= 0.0 {
                break;
            }
            let take = remaining.min(rates.fruit_supply[i]);
            banked[i] += take;
            remaining -= take;
        }

        // choppers
        for &(r, s) in &roster {
            if r != ROLE_CHOP {
                continue;
            }
            if need[IRON] > 0.0 {
                banked[IRON] += chopper_iron_rate(rates, s);
            } else {
                banked[WOOD] += chopper_wood_rate(rates, s);
            }
        }

        // investment
        if bi < policy.len() {
            let spec = policy[bi];
            let cost = training_cost(n_now, spec);
            if pay.iter().all(|&i| banked[i] >= cost[i] as f64) {
                for &i in pay {
                    banked[i] -= cost[i] as f64;
                }
                pending.push((t + ramp, role_of(spec), spec));
                bi += 1;
            }
        }
    }

    banked[0] + banked[1] + banked[2] + banked[3] + WOOD_POINTS * banked[WOOD]
}

// ── candidate policies ───────────────────────────────────────────────────────

fn candidate_policies() -> Vec<Vec<(i32, i32, i32, i32)>> {
    let mut cands: Vec<Vec<(i32, i32, i32, i32)>> = Vec::new();
    cands.push(vec![]);
    for &g in &GATHERER_SPECS {
        cands.push(vec![g]);
        cands.push(vec![g, g]);
    }
    if !NO_CHOP {
        for &c in &CHOPPER_SPECS {
            cands.push(vec![c]);
            for &g in &GATHERER_SPECS {
                cands.push(vec![c, g]);
                cands.push(vec![c, g, g]);
            }
        }
    }
    cands
}

// ── Plan ─────────────────────────────────────────────────────────────────────

struct Plan {
    train: Option<(i32, i32, i32, i32)>,
    gather_types: Vec<usize>,
}

fn plan_from_policy(state: &State, policy: &[(i32, i32, i32, i32)]) -> Plan {
    let n = state.my_trolls.len() as i32;
    let league3 = !state.iron_cells.is_empty();
    let pay: &[usize] = if league3 { &[0, 1, 2, 4] } else { &[0, 1, 2] };
    if policy.is_empty() {
        return Plan {
            train: None,
            gather_types: vec![],
        };
    }
    let first = policy[0];
    let cost = training_cost(n, first);
    let affordable = pay.iter().all(|&i| state.my_inventory[i] >= cost[i]);

    // gather_types: fruit indices where we're short, sorted by (inventory[i] - cost[i]) ascending
    let mut gather_types: Vec<usize> = (0..4)
        .filter(|&i| state.my_inventory[i] < cost[i])
        .collect();
    gather_types.sort_by_key(|&i| state.my_inventory[i] - cost[i]);

    Plan {
        train: if affordable { Some(first) } else { None },
        gather_types,
    }
}

fn search_policy(state: &State) -> Plan {
    let rates = estimate_rates(state);
    let mut best_score: Option<f64> = None;
    let mut best_pol: Vec<(i32, i32, i32, i32)> = vec![];
    for pol in candidate_policies() {
        let s = project(state, &pol, &rates);
        if best_score.is_none() || s > best_score.unwrap() {
            best_score = Some(s);
            best_pol = pol;
        }
    }
    plan_from_policy(state, &best_pol)
}

// ── best_tree ────────────────────────────────────────────────────────────────

fn best_tree<'a>(
    state: &'a State,
    reserved: &HashSet<Cell>,
    dist_t: &HashMap<Cell, i32>,
    return_dist: &HashMap<Cell, i32>,
    gather_types: &[usize],
) -> Option<&'a Tree> {
    let mut best: Option<&Tree> = None;
    let mut best_key: Option<(i32, i32, i32, i32)> = None;

    for tree in &state.trees {
        let pos = tree.pos();
        if reserved.contains(&pos) {
            continue;
        }
        if !dist_t.contains_key(&pos) || !return_dist.contains_key(&pos) {
            continue;
        }
        let walk = dist_t[&pos];
        let ripe = match ticks_until_ripe(tree, walk) {
            Some(r) => r,
            None => continue,
        };
        let ti = item_index(&tree.tree_type);
        let short = if gather_types.contains(&ti) {
            0i32
        } else {
            1i32
        };
        let wait = ripe - walk;
        let key = (short, wait, ripe + return_dist[&pos], walk);
        if best_key.is_none() || key < best_key.unwrap() {
            best_key = Some(key);
            best = Some(tree);
        }
    }
    best
}

// ── gather_command ────────────────────────────────────────────────────────────

fn bank_command(troll: &Troll, state: &State) -> String {
    if is_adjacent(troll.pos(), state.my_shack) {
        format!("DROP {}", troll.id)
    } else {
        format!(
            "MOVE {} {} {}",
            troll.id, state.my_shack.0, state.my_shack.1
        )
    }
}

fn gather_command(
    state: &State,
    troll: &Troll,
    reserved: &HashSet<Cell>,
    dist_t: &HashMap<Cell, i32>,
    return_dist: &HashMap<Cell, i32>,
    gather_types: &[usize],
    topup_radius: i32,
) -> (String, Option<Cell>) {
    // 1. Opportunistic harvest
    if troll.free_capacity() > 0 {
        for tree in &state.trees {
            if tree.pos() == troll.pos() && tree.fruits > 0 {
                return (format!("HARVEST {}", troll.id), Some(tree.pos()));
            }
        }
    }

    let target = best_tree(state, reserved, dist_t, return_dist, gather_types);

    // 2. Carrying: bank unless worthwhile top-up nearby
    if troll.total_carried() > 0 {
        if troll.free_capacity() == 0
            || target.is_none()
            || *dist_t.get(&target.unwrap().pos()).unwrap_or(&(1 << 30)) > topup_radius
        {
            return (bank_command(troll, state), None);
        }
    }

    // 3. Head for target
    match target {
        None => ("WAIT".to_string(), None),
        Some(t) => {
            if t.pos() == troll.pos() {
                ("WAIT".to_string(), None)
            } else {
                (format!("MOVE {} {} {}", troll.id, t.x, t.y), Some(t.pos()))
            }
        }
    }
}

// ── chop_command ──────────────────────────────────────────────────────────────

// Experiment knob: read an i32 from env with a default (planner.rs only, for
// sweeping; winners get baked into a const and mirrored to main.rs).
fn envi(name: &str, default: i32) -> i32 {
    std::env::var(name)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

fn best_chop_target<'a>(
    state: &'a State,
    reserved: &HashSet<Cell>,
    dist_t: &HashMap<Cell, i32>,
) -> Option<&'a Tree> {
    let mut best: Option<&Tree> = None;
    let mut best_key: Option<(i32, i32, i32)> = None;
    let (ox, oy) = state.opp_shack;
    let w = envi("DENIAL_W", 1); // weight on enemy-distance (denial dominance)
    let fb = envi("FRUIT_DENIAL", 6); // bonus for chopping fruited enemy trees
    for tree in &state.trees {
        let pos = tree.pos();
        if reserved.contains(&pos) || !dist_t.contains_key(&pos) {
            continue;
        }
        let d_enemy = (tree.x - ox).abs() + (tree.y - oy).abs();
        // Denial-dominant but trek-aware: weight on enemy-distance keeps denial
        // (chopping the foe's nearby trees to starve their fruit) decisive when that
        // tree is reasonably close, yet our own travel distance (dist_t) can still
        // tip us to a closer tree rather than trekking the whole map diagonal for one
        // far tree -- which tanked chop throughput on far-apart-shack maps. Measured
        // best of {pure denial, denial+reach, this} across the whole field.
        let key = (
            w * d_enemy + dist_t[&pos] - fb * tree.fruits,
            d_enemy,
            -tree.size,
        );
        if best_key.is_none() || key < best_key.unwrap() {
            best_key = Some(key);
            best = Some(tree);
        }
    }
    best
}

fn chop_command(
    state: &State,
    troll: &Troll,
    reserved: &HashSet<Cell>,
    dist_t: &HashMap<Cell, i32>,
    mining_useful: bool,
) -> (String, Option<Cell>) {
    // Mine iron ONLY when it's still the binding constraint for a troll we can afford
    // (computed in decide as `mining_useful`). Iron never scores -- it only pays a
    // troll's chop^2+n training cost -- so mining for a train we can't afford the
    // FRUIT for, or won't make at all, just burns endgame turns (observed: 20 iron
    // banked unused). Otherwise the chopper falls through to chopping a tree (4 pts).
    if mining_useful && troll.free_capacity() > 0 {
        for &ic in &state.iron_cells {
            if is_adjacent(troll.pos(), ic) {
                return (format!("MINE {}", troll.id), None);
            }
        }
    }

    let target = best_chop_target(state, reserved, dist_t);

    // Carry home when full or no target
    if troll.total_carried() > 0 && (troll.free_capacity() == 0 || target.is_none()) {
        if is_adjacent(troll.pos(), state.my_shack) {
            return (format!("DROP {}", troll.id), None);
        }
        return (
            format!(
                "MOVE {} {} {}",
                troll.id, state.my_shack.0, state.my_shack.1
            ),
            None,
        );
    }

    // Standing on a tree -> chop it
    for tree in &state.trees {
        if tree.pos() == troll.pos() {
            return (format!("CHOP {}", troll.id), Some(tree.pos()));
        }
    }

    match target {
        None => (
            format!(
                "MOVE {} {} {}",
                troll.id, state.opp_shack.0, state.opp_shack.1
            ),
            None,
        ),
        Some(t) => (format!("MOVE {} {} {}", troll.id, t.x, t.y), Some(t.pos())),
    }
}

// ── decide ────────────────────────────────────────────────────────────────────

pub fn decide(state: &State) -> Vec<String> {
    let shack_adj: Vec<Cell> = ortho_neighbors(state.my_shack)
        .iter()
        .filter(|n| state.walkable.contains(n))
        .copied()
        .collect();
    let return_dist = bfs_distances(&state.walkable, &shack_adj);

    let plan = search_policy(state);

    let mut commands_by_id: HashMap<i32, String> = HashMap::new();
    let mut used_ids: HashSet<i32> = HashSet::new();
    let mut reserved: HashSet<Cell> = HashSet::new();

    // Choppers first. Dedicated chopper = chop_power>=2; if none yet, bootstrap
    // the wood/iron economy with our best chop>=1 troll (mine iron + chop to fund
    // a real chopper). Reverts to gathering once a real chopper exists.
    let mut my_trolls_sorted = state.my_trolls.clone();
    my_trolls_sorted.sort_by_key(|t| t.id);

    let has_real_chopper = my_trolls_sorted.iter().any(|t| t.chop_power >= 2);
    // Bootstrap the wood/iron economy with our chop-1 starter (mine iron + chop) until
    // we own a real chopper. NOTE: do NOT "optimize" this away when a chopper is already
    // affordable -- making the starter gather instead skips its early IRON MINING, which
    // strands us at 2 trolls (iron-short of the 3rd) and REGRESSED the arena 3 -> 48
    // (v0.8.2). The starter's early trek doubles as mining/denial; keep it.
    let mut bootstrap_id: Option<i32> = None;
    if !NO_CHOP && !has_real_chopper && !state.iron_cells.is_empty() {
        bootstrap_id = my_trolls_sorted
            .iter()
            .filter(|t| t.chop_power >= 1)
            .max_by_key(|t| (t.chop_power, t.carry_capacity, -t.id))
            .map(|t| t.id);
    }

    // Is mining iron still worthwhile this turn? Only if iron is the binding
    // constraint for a troll we'd actually train -- i.e. we can already afford the
    // FRUIT (plum/lemon/apple) but are short on iron. Mining for a fruit-starved or
    // unplanned train wastes endgame turns (iron never scores); see chop_command.
    let n_now = my_trolls_sorted.len() as i32;
    let afford_fruit = |spec: (i32, i32, i32, i32)| -> bool {
        let c = training_cost(n_now, spec);
        c[PLUM] <= state.my_inventory[PLUM]
            && c[LEMON] <= state.my_inventory[LEMON]
            && c[APPLE] <= state.my_inventory[APPLE]
    };
    let next_spec: Option<(i32, i32, i32, i32)> = if !NO_CHOP
        && !has_real_chopper
        && !state.iron_cells.is_empty()
        && my_trolls_sorted.len() < (envi("OPEN_MAX", 3) as usize)
        && state.turn <= envi("OPEN_TURNS", 30)
    {
        // Opening: strongest chopper whose fruit we can already cover (iron via mining).
        PARAMS
            .opening_chopper_specs
            .iter()
            .copied()
            .find(|s| afford_fruit(*s))
    } else {
        plan.train
    };
    let mining_useful = match next_spec {
        Some(spec) => {
            afford_fruit(spec) && state.my_inventory[IRON] < training_cost(n_now, spec)[IRON]
        }
        None => false,
    };

    for troll in &my_trolls_sorted {
        if troll.chop_power >= 2 || Some(troll.id) == bootstrap_id {
            let dist_t = bfs_distances(&state.walkable, &[troll.pos()]);
            let (cmd, res) = chop_command(state, troll, &reserved, &dist_t, mining_useful);
            if let Some(pos) = res {
                reserved.insert(pos);
            }
            commands_by_id.insert(troll.id, cmd);
            used_ids.insert(troll.id);
        }
    }

    // Orchard planting (gated on plan.plant which is always None in v0.7.1)
    // plan.plant is always None (planting_commands is only called when plan.plant is Some)
    // So this block never executes — matching Python behavior where plan.plant == None

    // Gathering for remaining trolls
    for troll in &my_trolls_sorted {
        if used_ids.contains(&troll.id) {
            continue;
        }
        let dist_t = bfs_distances(&state.walkable, &[troll.pos()]);
        let (cmd, res) = gather_command(
            state,
            troll,
            &reserved,
            &dist_t,
            &return_dist,
            &plan.gather_types,
            PARAMS.topup_radius,
        );
        if let Some(pos) = res {
            reserved.insert(pos);
        }
        commands_by_id.insert(troll.id, cmd);
    }

    // Spread banking trolls across shack-adjacent DROP cells, preferring cells NOT
    // already held by a teammate that will stay put this turn. An idle troll sitting
    // on a drop cell otherwise blocks a banker forever, so its load never gets
    // delivered -- we lost a 127-135 game to exactly this (a chopper froze one step
    // from the shack carrying wood because a fruitless gatherer camped the cell).
    let (sx, sy) = state.my_shack;
    let mut bankers: Vec<i32> = commands_by_id
        .iter()
        .filter(|(tid, cmd)| cmd.as_str() == format!("MOVE {} {} {}", tid, sx, sy).as_str())
        .map(|(tid, _)| *tid)
        .collect();
    bankers.sort();
    if !bankers.is_empty() {
        let banker_set: HashSet<i32> = bankers.iter().copied().collect();
        // A troll "stays put" unless its command is a MOVE to a cell other than its own.
        let stays_put = |id: i32, pos: Cell| -> bool {
            match commands_by_id.get(&id) {
                Some(cmd) => {
                    let p: Vec<&str> = cmd.split_whitespace().collect();
                    if p.first() == Some(&"MOVE") && p.len() >= 4 {
                        let tx = p[2].parse::<i32>().unwrap_or(pos.0);
                        let ty = p[3].parse::<i32>().unwrap_or(pos.1);
                        (tx, ty) == pos
                    } else {
                        true
                    }
                }
                None => true,
            }
        };
        let blocked: HashSet<Cell> = state
            .my_trolls
            .iter()
            .filter(|u| !banker_set.contains(&u.id) && stays_put(u.id, u.pos()))
            .map(|u| u.pos())
            .collect();
        // Assign each banker its NEAREST reachable free drop cell (BFS from the
        // banker's own position). The old fixed-order pick could hand a banker a
        // shack-adjacent cell reachable only THROUGH a teammate camping the near
        // approach, wedging it one step short of the shack for the rest of the game
        // (undelivered cargo = lost points; a dead scorched-earth endgame made this
        // permanent). Nearest-reachable routes it to a cell it can actually reach.
        let mut used: HashSet<Cell> = HashSet::new();
        for &tid in &bankers {
            let from = state
                .my_trolls
                .iter()
                .find(|u| u.id == tid)
                .map(|u| u.pos())
                .unwrap_or(state.my_shack);
            let d = bfs_distances(&state.walkable, &[from]);
            let cell = shack_adj
                .iter()
                .filter(|c| !blocked.contains(c) && !used.contains(c))
                .min_by_key(|c| *d.get(*c).unwrap_or(&(1 << 30)))
                .copied()
                .unwrap_or(state.my_shack);
            used.insert(cell);
            commands_by_id.insert(tid, format!("MOVE {} {} {}", tid, cell.0, cell.1));
        }
    }

    // Movement deconfliction is intentionally NOT done here: we emit each troll's
    // FINAL target and let the referee resolve same-cell contention (highest id
    // wins, the rest wait one turn then retry). Predicting and pre-resolving
    // collisions ourselves wedged whole clusters in tight terrain pockets -- e.g.
    // 3 trolls boxed by water/iron next to the shack thrashed for ~290 turns,
    // scoring 19 instead of 112. Letting the referee disperse them fixed those
    // collapses and improved margin across the whole field (measured).

    let mut commands: Vec<String> = Vec::new();
    if state.turn == 1 {
        commands.push(format!("MSG v{}", VERSION));
    }
    let mut sorted_ids: Vec<i32> = commands_by_id.keys().copied().collect();
    sorted_ids.sort();
    for tid in sorted_ids {
        commands.push(commands_by_id[&tid].clone());
    }

    // Opening tempo floor: build a CHOPPER first (wood is the dominant economy),
    // then top up with cheap gatherers. forced_policy is never set in the real bot.
    let mut train_spec = plan.train;
    let n = state.my_trolls.len();
    if state.turn <= envi("OPEN_TURNS", 30) && n < (envi("OPEN_MAX", 3) as usize) {
        let pay: &[usize] = if !state.iron_cells.is_empty() {
            &[0, 1, 2, 4]
        } else {
            &[0, 1, 2]
        };
        let affordable = |spec: (i32, i32, i32, i32)| {
            let cost = training_cost(n as i32, spec);
            pay.iter().all(|&i| state.my_inventory[i] >= cost[i])
        };
        let have_chopper = state.my_trolls.iter().any(|t| t.chop_power >= 2);
        let mut chosen: Option<(i32, i32, i32, i32)> = None;
        if !NO_CHOP && !have_chopper && !state.iron_cells.is_empty() {
            for &spec in PARAMS.opening_chopper_specs {
                if affordable(spec) {
                    chosen = Some(spec);
                    break;
                }
            }
        }
        if chosen.is_none() && affordable(PARAMS.opening_spec) {
            chosen = Some(PARAMS.opening_spec);
        }
        if let Some(spec) = chosen {
            train_spec = Some(spec);
        }
    }

    if let Some(spec) = train_spec {
        if TOTAL_TURNS - state.turn > PARAMS.min_turns_left_to_train
            && !state.my_trolls.iter().any(|t| t.pos() == state.my_shack)
            && n < (envi("MAX_TROLLS", 5) as usize)
        {
            commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
    }

    if commands.is_empty() {
        commands.push("WAIT".to_string());
    }
    commands
}
