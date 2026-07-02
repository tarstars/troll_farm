#![allow(dead_code, unused)]
// CodinGame Spring Challenge 2026 - Troll Farm bot (Rust port of Python v0.7.1)
// Single-file submission. stdlib only.

use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};

// ── constants ───────────────────────────────────────────────────────────────

const VERSION: &str = "1.0.8-woodprinter";
const TOTAL_TURNS: i32 = 300;
// NO_CHOP is LEGACY: it only gates the old economic-planner bot (`decide_old`, now
// dead code). The live bot is the v0.9.2 `decide` (big-chopper strategy). Real Boss 4
// wins on WOOD (a cc4 chopper fells trees for 4 wood = 16pts; ~184 of its 283 pts were
// wood), so we now train big choppers and chop the nearest tree (fruit grabbed as bonus).
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
    opening_chopper_specs: &[(2, 2, 1, 2), (2, 2, 0, 2), (2, 1, 0, 2), (1, 2, 0, 2), (1, 1, 0, 2)],
    plant_enabled: true,
    max_orchard: 3,
};

// GATHERER_SPECS / CHOPPER_SPECS
const GATHERER_SPECS: [(i32, i32, i32, i32); 3] = [
    (1, 1, 1, 0),
    (1, 2, 1, 0),
    (2, 2, 2, 0),
];
const CHOPPER_SPECS: [(i32, i32, i32, i32); 3] = [
    (1, 3, 0, 2),
    (2, 4, 0, 3),
    (2, 4, 0, 4),
];

// ── data structures ─────────────────────────────────────────────────────────

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
    tree_type: String, // "PLUM","LEMON","APPLE","BANANA"
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

fn predict_fruits(plant_type: &str, mut size: i32, mut fruits: i32, mut cooldown: i32, ticks: i32) -> i32 {
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
        if predict_fruits(&tree.tree_type, tree.size, tree.fruits, tree.cooldown, offset) > 0 {
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
    let near_water = state.water_cells.iter().any(|&(wx, wy)| {
        (tx - wx).abs() + (ty - wy).abs() == 1
    });
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
    if stats.3 >= 2 { ROLE_CHOP } else { ROLE_GATH }
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
    let mut roster: Vec<(u8, (i32, i32, i32, i32))> = state.my_trolls
        .iter()
        .map(|t| (role_of(t.stats()), t.stats()))
        .collect();
    // pending: (ready_at, role, stats)
    let mut pending: Vec<(i32, u8, (i32, i32, i32, i32))> = Vec::new();
    let mut bi = 0usize;
    let ramp = ((rates.mean_dist as i32) + 1).min(RAMP_DELAY_CAP);

    // pay indices: iron index included only if has_iron
    let pay: &[usize] = if has_iron(rates) { &[0, 1, 2, 4] } else { &[0, 1, 2] };

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
        let mut remaining: f64 = roster.iter()
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
        return Plan { train: None, gather_types: vec![] };
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
        let short = if gather_types.contains(&ti) { 0i32 } else { 1i32 };
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
        format!("MOVE {} {} {}", troll.id, state.my_shack.0, state.my_shack.1)
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

fn best_chop_target<'a>(
    state: &'a State,
    reserved: &HashSet<Cell>,
    dist_t: &HashMap<Cell, i32>,
) -> Option<&'a Tree> {
    let mut best: Option<&Tree> = None;
    let mut best_key: Option<(i32, i32, i32)> = None;
    let (ox, oy) = state.opp_shack;
    for tree in &state.trees {
        let pos = tree.pos();
        if reserved.contains(&pos) || !dist_t.contains_key(&pos) {
            continue;
        }
        let d_enemy = (tree.x - ox).abs() + (tree.y - oy).abs();
        // Denial-dominant but trek-aware: 1x weight on enemy-distance keeps denial
        // (chopping the foe's nearby trees to starve their fruit) present, yet our own
        // travel distance (dist_t) keeps chop throughput high (trekking the map diagonal
        // for a far tree tanked throughput on far-apart-shack maps). The -6*fruits term
        // is FRUIT-DENIAL: preferentially fell the foe's FRUITED trees, destroying its
        // harvest (1pt each) while banking wood. Swept vs boss4 (v0.8.5): W=1,FB=6 gives
        // 76.8% / +9.9 margin, up from W=2,FB=0's 73.7% -- best win-rate*margin balance.
        let key = (1 * d_enemy + dist_t[&pos] - 6 * tree.fruits, d_enemy, -tree.size);
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
            format!("MOVE {} {} {}", troll.id, state.my_shack.0, state.my_shack.1),
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
            format!("MOVE {} {} {}", troll.id, state.opp_shack.0, state.opp_shack.1),
            None,
        ),
        Some(t) => (format!("MOVE {} {} {}", troll.id, t.x, t.y), Some(t.pos())),
    }
}

// ── decide ────────────────────────────────────────────────────────────────────

// ── VERSATILE POWER-TROLL strategy (v0.9.x) ──────────────────────────────────
// The real Boss 4 trains versatile power-trolls (ms1,cc2,hp3,chop3) that harvest
// fast AND chop, and it INVESTS its resources; it scores ~250. Our old bots trained
// weak (1,1,1,0) gatherers and hoarded apple/iron, scoring ~86. This strategy:
//   - saves toward and trains the STRONGEST affordable power-troll (mine iron for it);
//   - each troll HARVESTs the fruited tree it targets (primary income), and CHOPs a
//     tree only when no fruit is reachable (wood is 4pt/unit -- a fallback, not scorch);
//   - banks when full; spreads over shack drop cells.
// WOOD dominates scoring (4pt/unit; a cc4 chopper fells a tree for up to 4 wood = 16
// pts). The real Boss 4 wins with a (2,4,2,2) powerhouse chopper (184 of its 283 pts
// were wood). So we train big CHOPPERS (high cc + chop, some hp to grab fruit too),
// strongest affordable first, and each troll chops the nearest tree (harvesting its
// fruit first when present). Trees regrow, so chopping is sustainable, not scorch.
// One STRONG chopper (wood engine, like the boss's (2,4,2,2)); cc>=3 only, so we don't
// settle for a weak cc2 chopper -- we save until a real one is affordable.
const CHOPPER_BUILD: [(i32, i32, i32, i32); 4] =
    [(2, 4, 2, 2), (2, 4, 0, 3), (1, 3, 1, 2), (1, 3, 0, 2)];
// HARVESTERS: hp-focused, cc2, no chop (so they never fell trees -> map is preserved).
const HARVEST_SPECS: [(i32, i32, i32, i32); 5] =
    [(2, 2, 3, 0), (1, 2, 3, 0), (1, 2, 2, 0), (1, 2, 1, 0), (1, 1, 1, 0)];
const MAX_POWER_TROLLS: usize = 6;

fn afford_cost(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM]
        && inv[LEMON] >= cost[LEMON]
        && inv[APPLE] >= cost[APPLE]
        && inv[IRON] >= cost[IRON]
}
fn afford_fruit_only(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}

// ── WOOD-RACE bot (v1.0) — beats the Silver Boss ~68% in the local sim ─────────
// Mirror of strategies::mybot (validated in the referee-faithful Rust sim). Strategy:
//   * GREEDY expansion to ~4 trolls (train the cheapest affordable troll each turn),
//     jumping the queue to build TWO fast (ms2,cc2,chop2) choppers as soon as afford-
//     able; the rest are speed harvesters. Mine iron to fund the choppers' chop cost.
//   * Choppers fell the best tree (close + big) with a DENIAL bias toward the foe's
//     shack -- felling starves the opponent's fruit while banking 4pt-each wood.
//   * Harvesters grab the NEAREST ripe fruit (max throughput) and seed a tiny base
//     plum orchard; everyone banks when full.
// The boss is a similar wood/denial bot; our edge is faster (ms2) choppers that win
// the race to contested trees + higher fruit throughput (nearest-ripe harvesting).
// Cheap pure chopper (ms1, cc2, hp0, chop2): swept best vs silver_boss at 87% (vs the
// old ms2 (2,2,1,2) at 81%). cc2 = 2 wood/fell is essential; dropping ms+hp saves plum
// +apple for a stronger economy while still winning the denial race (DW=3) + woodfarm.
// hp0 (was hp1): saves n+1 APPLE per chopper; the only loss is a rarely-reachable
// fruit-harvest fallback. Confirmed on BOTH boss models at 1000 seeds (2026-07-02):
// scriptboss 59.8→60.9% (margin +14.7→+18.2), silverboss 77.5→78.4% (+24.1→+26.9).
const MB_CHOPPER: (i32, i32, i32, i32) = (2, 2, 0, 2);
const MB_NCHOPPERS: i32 = 2;
// chop1 harvesters (+n+1 iron each): every fruit troll can also FELL the base
// farm's young bananas (the "mower"). Blueprint from arena replays: 250-pt bots
// sustain 0.30 wood/turn vs our 0.07; fellers must live AT the farm, and the
// denial choppers can't. Both-model win at 1000 seeds: scriptboss 63.0->64.3%
// (margin +25.8->+31.6), silverboss 85.1->87.5% (+51.4->+54.1); wood 90->105.
const MB_HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const MB_MAX_TROLLS: usize = 4;
const MB_MAX_ORCHARD: usize = 2;
const MB_MIN_TURNS_LEFT: i32 = 20;
// Denial-heavy chopper targeting (swept 2026-07-01 in the faithful sim): DW=3, WT=0
// lifts the bot from 67.6% -> 78.0% vs silver_boss. Our cheap fast choppers win the
// race to the BOSS's trees and starve its wood+fruit; biasing hard toward the enemy
// shack (and dropping the tree-size preference) is decisively better than balanced.
const MB_DENIAL_W: i32 = 3;
const MB_SIZE_W: i32 = 0;

thread_local! {
    // Sticky per-harvester target memory (reset at turn 1). Persists across turns
    // within a single game process.
    static MB_MEM: std::cell::RefCell<HashMap<i32, Cell>> = std::cell::RefCell::new(HashMap::new());
}

fn mb_afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}

fn decide(state: &State) -> Vec<String> {
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();

    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    let n = my.len() as i32;

    // ── training plan: greedy expansion, jump the queue for the choppers ──────
    let chop_spec = MB_CHOPPER;
    let n_choppers = my.iter().filter(|t| t.chop_power >= 2).count() as i32;
    let want_chopper = n_choppers < MB_NCHOPPERS;
    let train_now: Option<(i32, i32, i32, i32)> =
        if want_chopper && mb_afford(inv, &training_cost(n, chop_spec), have_iron) {
            Some(chop_spec)
        } else {
            MB_HARVESTERS.iter().copied().find(|&s| mb_afford(inv, &training_cost(n, s), have_iron))
        };
    let need_iron = have_iron
        && want_chopper
        && inv[IRON] < training_cost(n, chop_spec)[IRON]
        && afford_fruit_only(inv, &training_cost(n, chop_spec));

    // Roles: chop>=2 are choppers; if none yet, the best chop>=1 starter bootstraps.
    let has_real_chopper = my.iter().any(|t| t.chop_power >= 2);
    let bootstrap_id: Option<i32> = if has_real_chopper {
        None
    } else {
        my.iter()
            .filter(|t| t.chop_power >= 1)
            .max_by_key(|t| (t.carry_capacity, -t.id))
            .map(|t| t.id)
    };
    let is_chopper = |t: &Troll| -> bool { t.chop_power >= 2 || Some(t.id) == bootstrap_id };

    let orchard: usize = state
        .trees
        .iter()
        .filter(|p| p.tree_type == "PLUM" && manhattan(p.pos(), shack) <= 3)
        .count();

    MB_MEM.with(|mem_cell| {
        if state.turn == 1 {
            mem_cell.borrow_mut().clear();
        }
        let mut mem = mem_cell.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
        let mut commands: Vec<String> = Vec::new();
        if state.turn == 1 {
            commands.push(format!("MSG v{}", VERSION));
        }

        for t in &my {
            let is_chop = is_chopper(t);
            let d = bfs_distances(&state.walkable, &[t.pos()]);

            // ── ENDGAME BANKING: carried items score ZERO unless DROPped at the shack
            // by the final turn. When the remaining turns barely cover the walk home +
            // the DROP, abandon everything and bank. Without this, every troll strands
            // up to cc-1 items at t=300 (a chopper's stranded wood = 4 pts each).
            if t.total_carried() > 0 {
                let turns_rem = TOTAL_TURNS - state.turn + 1; // incl. this turn
                let d_home = ortho_neighbors(shack)
                    .iter()
                    .filter(|c| state.walkable.contains(*c))
                    .filter_map(|c| d.get(c))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let ms = t.movement_speed.max(1);
                let eta = (d_home + ms - 1) / ms + 1; // walk turns + the DROP turn
                if turns_rem <= eta + 1 {
                    if is_adjacent(t.pos(), shack) {
                        cmd_by_id.insert(t.id, format!("DROP {}", t.id));
                    } else {
                        let drop_cell = ortho_neighbors(shack)
                            .into_iter()
                            .filter(|c| state.walkable.contains(c))
                            .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                            .unwrap_or(shack);
                        cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, drop_cell.0, drop_cell.1));
                    }
                    continue;
                }
            }

            // ── WOOD PRINTER: the engine top-Silver bots run (decoded from an arena
            // loss to aRi, 275 pts = 67 wood): keep (re)planting BANANA near base —
            // cd 6 (fastest growth), health 2+s (3 chops at chop2) — and fell the young
            // trees for 2 wood (8 pts) each, forever. Unlike the passive woodfarm
            // (plants only surplus CARRIED fruit), this PICKs banana back out of the
            // inventory to keep the loop fed. +13 avg score, boss win rates held.
            {
                let base_trees_now =
                    state.trees.iter().filter(|p| manhattan(p.pos(), shack) <= 3).count();
                if !is_chop && state.turn >= 20 && state.turn <= 280 && base_trees_now < 6
                    // the plum ORCHARD outranks the banana printer
                    && !(t.carry[PLUM] > 0 && orchard < MB_MAX_ORCHARD)
                {
                    if t.carry[BANANA] > 0 {
                        let free_base = |water: bool| {
                            state
                                .walkable
                                .iter()
                                .filter(|c| manhattan(**c, shack) <= 3 && d.contains_key(*c))
                                .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                                .filter(|c| {
                                    !water
                                        || state
                                            .water_cells
                                            .iter()
                                            .any(|w| manhattan(*w, **c) == 1)
                                })
                                .filter(|c| !my.iter().any(|o| o.id != t.id && o.pos() == **c))
                                .min_by_key(|c| d[*c])
                                .copied()
                        };
                        if let Some(tc) = free_base(true).or_else(|| free_base(false)) {
                            if t.pos() == tc {
                                cmd_by_id.insert(t.id, format!("PLANT {} BANANA", t.id));
                            } else {
                                cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, tc.0, tc.1));
                            }
                            continue;
                        }
                    } else if is_adjacent(t.pos(), shack)
                        && t.free_capacity() > 0
                        && state.my_inventory[BANANA] > 0
                    {
                        cmd_by_id.insert(t.id, format!("PICK {} BANANA", t.id));
                        continue;
                    }
                }
            }

            // Full -> home; harvester seeds the base plum orchard, then does FRUIT->WOOD
            // conversion (plant surplus fruit -- prefer BANANA, which has no training
            // value -- near base in a mid-game window so it grows and the chopper fells
            // it for wood: 1pt fruit -> up to 4*size pts). Else drops.
            if t.free_capacity() == 0 {
                mem.remove(&t.id);
                // Place orchard plums DELIBERATELY on a water-adjacent base cell (plum
                // cooldown 8 -> 3 beside water = ~2.7x fruit rate) instead of planting
                // wherever the returning harvester happens to stand. Both-model win:
                // scriptboss 60.5->62.5%, silverboss 78.2->81.2% (1000 seeds, same-seed).
                if !is_chop && t.carry[PLUM] > 0 && orchard < MB_MAX_ORCHARD {
                    let spot = state
                        .walkable
                        .iter()
                        .filter(|c| manhattan(**c, shack) <= 3 && d.contains_key(*c))
                        .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                        .filter(|c| state.water_cells.iter().any(|w| manhattan(*w, **c) == 1))
                        .filter(|c| !my.iter().any(|o| o.id != t.id && o.pos() == **c))
                        .min_by_key(|c| d[*c]);
                    if let Some(&tc) = spot {
                        if t.pos() == tc {
                            cmd_by_id.insert(t.id, format!("PLANT {} PLUM", t.id));
                        } else {
                            cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, tc.0, tc.1));
                        }
                        continue;
                    }
                    // no water-adjacent base cell -> fall through to the old behavior
                }
                if is_adjacent(t.pos(), shack) {
                    let on_tree = state.trees.iter().any(|p| p.pos() == t.pos());
                    let base_trees = state.trees.iter().filter(|p| manhattan(p.pos(), shack) <= 3).count();
                    let plum_orchard = orchard < MB_MAX_ORCHARD && t.carry[PLUM] > 0;
                    // WOODFARM re-validated 2026-07-02 ALONE (v1.0.4's flop was the coupled
                    // cheap ms1 chopper, not the farm): scriptboss +0.9pp/+2.9 margin,
                    // silverboss +3.2pp/+10.8 margin. Surplus fruit (BANANA first — no
                    // training value) becomes 4pt wood via the chopper.
                    let woodfarm = state.turn >= 20 && state.turn <= 280 && base_trees < 6;
                    if !is_chop && !on_tree && state.walkable.contains(&t.pos()) && (plum_orchard || woodfarm) {
                        let ty = if plum_orchard {
                            "PLUM"
                        } else if t.carry[BANANA] > 0 {
                            "BANANA"
                        } else {
                            match (0..4).filter(|&i| t.carry[i] > 0).max_by_key(|&i| t.carry[i]) {
                                Some(0) => "PLUM",
                                Some(1) => "LEMON",
                                Some(2) => "APPLE",
                                _ => "BANANA",
                            }
                        };
                        cmd_by_id.insert(t.id, format!("PLANT {} {}", t.id, ty));
                    } else {
                        cmd_by_id.insert(t.id, format!("DROP {}", t.id));
                    }
                } else {
                    // Head to the NEAREST walkable shack-adjacent DROP cell (not the shack
                    // center). A full troll standing ON the shack cell (e.g. the starter
                    // after mining turn-1 iron on maps with iron beside the shack) would
                    // otherwise MOVE to its own cell forever and wedge the whole game.
                    let drop_cell = ortho_neighbors(shack)
                        .into_iter()
                        .filter(|c| state.walkable.contains(c))
                        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, drop_cell.0, drop_cell.1));
                }
                continue;
            }

            // On a tree: chopper fells it; harvester grabs the fruit. The MOWER
            // (chop1+hp2 harvester) also fells fruitless base-farm trees at size>=2
            // (banana health 2+s = 4 chops at chop1; size<4 never bears fruit).
            let is_tender = t.chop_power == 1 && t.harvest_power >= 2;
            if let Some(p) = state.trees.iter().find(|p| p.pos() == t.pos()) {
                if is_chop && t.chop_power > 0 {
                    cmd_by_id.insert(t.id, format!("CHOP {}", t.id));
                    reserved.insert(t.pos());
                    continue;
                }
                if is_tender && manhattan(p.pos(), shack) <= 3 && p.size >= 2 && p.fruits == 0 {
                    cmd_by_id.insert(t.id, format!("CHOP {}", t.id));
                    reserved.insert(t.pos());
                    continue;
                }
                if p.fruits > 0 && t.harvest_power > 0 && t.free_capacity() > 0 {
                    cmd_by_id.insert(t.id, format!("HARVEST {}", t.id));
                    reserved.insert(t.pos());
                    continue;
                }
            }

            // Chopper mines iron when saving and adjacent to it.
            if need_iron && is_chop && t.chop_power > 0
                && state.iron_cells.iter().any(|ic| is_adjacent(t.pos(), *ic))
            {
                cmd_by_id.insert(t.id, format!("MINE {}", t.id));
                continue;
            }

            let go: Option<Cell> = if is_chop {
                let iron_cell = if need_iron {
                    state
                        .iron_cells
                        .iter()
                        .flat_map(|ic| ortho_neighbors(*ic))
                        .filter(|c| d.contains_key(c) && !reserved.contains(c))
                        .min_by_key(|c| d[c])
                } else {
                    None
                };
                iron_cell
                    .or_else(|| {
                        state
                            .trees
                            .iter()
                            .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                            .min_by_key(|p| {
                                (d[&p.pos()] + MB_DENIAL_W * manhattan(p.pos(), opp) - MB_SIZE_W * p.size, -p.size)
                            })
                            .map(|p| p.pos())
                    })
                    .or_else(|| {
                        if t.harvest_power > 0 {
                            state
                                .trees
                                .iter()
                                .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                                .min_by_key(|p| d[&p.pos()])
                                .map(|p| p.pos())
                        } else {
                            None
                        }
                    })
            } else {
                let sticky = mem.get(&t.id).copied().filter(|&c| {
                    state.trees.iter().any(|p| p.pos() == c && p.fruits > 0) && !reserved.contains(&c)
                });
                // When NOTHING is ripe, don't idle at base: pre-position at the tree
                // whose first fruit lands soonest relative to our arrival (minimize
                // max(travel, time-to-ripe)). Validated growth mechanics only.
                let anticipate = || -> Option<Cell> {
                    state
                        .trees
                        .iter()
                        .filter(|p| !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                        .filter_map(|p| {
                            let mut cd = plant_cooldown(&p.tree_type);
                            if state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1) {
                                cd -= water_boost(&p.tree_type);
                            }
                            let cd = cd.max(1);
                            let steps = if p.size < 4 { 4 - p.size + 1 } else { 1 };
                            let ttr = p.cooldown + (steps - 1) * cd;
                            let ms = t.movement_speed.max(1);
                            let arrive = (d[&p.pos()] + ms - 1) / ms;
                            if ttr <= 40 {
                                Some((arrive.max(ttr), d[&p.pos()], p.pos()))
                            } else {
                                None
                            }
                        })
                        .min()
                        .map(|(_, _, c)| c)
                };
                // Scarcity among equal-distance ripe trees: prefer the type our
                // inventory is shortest on (banana penalized — it can't fund training).
                // Zero travel cost; nudges fruit COMPOSITION toward what training needs.
                let nearest_ripe_scarce = || -> Option<Cell> {
                    let dmin = state
                        .trees
                        .iter()
                        .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                        .map(|p| d[&p.pos()])
                        .min()?;
                    state
                        .trees
                        .iter()
                        .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                        .filter(|p| d[&p.pos()] <= dmin)
                        .min_by_key(|p| {
                            let ti = match p.tree_type.as_str() {
                                "PLUM" => PLUM,
                                "LEMON" => LEMON,
                                "APPLE" => APPLE,
                                _ => BANANA,
                            };
                            let scarcity = if ti == BANANA {
                                state.my_inventory[BANANA] + 6
                            } else {
                                state.my_inventory[ti]
                            };
                            (scarcity, d[&p.pos()])
                        })
                        .map(|p| p.pos())
                };
                // Mower first: head for a fellable (size>=2, fruitless) base-farm tree.
                let tender_target = if is_tender {
                    state
                        .trees
                        .iter()
                        .filter(|p| manhattan(p.pos(), shack) <= 3 && p.size >= 2 && p.fruits == 0)
                        .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                        .min_by_key(|p| d[&p.pos()])
                        .map(|p| p.pos())
                } else {
                    None
                };
                tender_target
                    .or(sticky)
                    .or_else(nearest_ripe_scarce)
                    .or_else(anticipate)
            };

            match go {
                Some(c) => {
                    reserved.insert(c);
                    if !is_chop {
                        mem.insert(t.id, c);
                    }
                    cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, c.0, c.1));
                }
                None => {
                    cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, shack.0, shack.1));
                }
            }
        }

        let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
        ids.sort();
        for id in ids {
            commands.push(cmd_by_id[&id].clone());
        }

        if let Some(spec) = train_now {
            if (n as usize) < MB_MAX_TROLLS
                && TOTAL_TURNS - state.turn > MB_MIN_TURNS_LEFT
                && !my.iter().any(|t| t.pos() == shack)
            {
                commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }

        if commands.is_empty() {
            commands.push("WAIT".to_string());
        }
        commands
    })
}

fn decide_v097(state: &State) -> Vec<String> {
    let shack = state.my_shack;
    let shack_adj: Vec<Cell> = ortho_neighbors(shack)
        .iter()
        .filter(|n| state.walkable.contains(n))
        .copied()
        .collect();

    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    let n = my.len() as i32;

    // Composition (mirrors the boss): starter + 1 harvester for early income, then
    // SAVE for ONE strong (2,4,2,2)-class chopper (cc>=3, chop>=2 -- the wood engine
    // that wins games; the boss's cc4 chopper made 156 of its pts). Only after we own
    // that do we add more harvesters. While saving, if no strong chopper is affordable
    // we simply don't train (accumulate lemon+iron) rather than waste resources on weak
    // trolls -- that dilution is why we kept losing the wood race.
    let have_strong = my.iter().any(|t| t.chop_power >= 2 && t.carry_capacity >= 3);
    let build_list: &[(i32, i32, i32, i32)] = if have_strong {
        &HARVEST_SPECS
    } else if n < 2 {
        &HARVEST_SPECS
    } else {
        &CHOPPER_BUILD
    };
    let trainable: Option<(i32, i32, i32, i32)> = build_list
        .iter()
        .copied()
        .find(|&s| afford_cost(&state.my_inventory, &training_cost(n, s)));
    let iron_goal: Option<(i32, i32, i32, i32)> = build_list
        .iter()
        .copied()
        .find(|&s| afford_fruit_only(&state.my_inventory, &training_cost(n, s)));
    let need_iron = match iron_goal {
        Some(s) => state.my_inventory[IRON] < training_cost(n, s)[IRON],
        None => false,
    };

    let mut commands: Vec<String> = Vec::new();
    if state.turn == 1 {
        commands.push(format!("MSG v{}", VERSION));
    }

    let mut reserved: HashSet<Cell> = HashSet::new();
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();

    // MIXED roles: exactly ONE dedicated chopper (the strongest chop>=2 troll) fells
    // trees for wood; everyone else HARVESTS fruit and never chops. This sustains the
    // tree population (chopping with every troll scorched the map -- the game ends at
    // 0 trees and we lost 58-168), while still banking the high-value wood the boss
    // wins on. Fruit-grabbing on a tree is allowed for all (free points).
    let chopper_id: Option<i32> = my
        .iter()
        .filter(|t| t.chop_power >= 2)
        .max_by_key(|t| (t.chop_power, t.carry_capacity, -t.id))
        .map(|t| t.id);

    for troll in &my {
        let is_chopper = Some(troll.id) == chopper_id;
        // 1. Full -> bank.
        if troll.free_capacity() == 0 {
            cmd_by_id.insert(troll.id, bank_command(troll, state));
            continue;
        }
        // 2. On a tree: the dedicated chopper FELLS it (wood is the win condition -- if
        //    it harvested the regrowing fruit instead it would never fell the tree and
        //    make 0 wood, which is exactly why we kept losing). Harvesters take the fruit.
        if let Some(tree) = state.trees.iter().find(|t| t.pos() == troll.pos()) {
            if is_chopper && troll.chop_power > 0 {
                cmd_by_id.insert(troll.id, format!("CHOP {}", troll.id));
                reserved.insert(tree.pos());
                continue;
            }
            if tree.fruits > 0 && troll.harvest_power > 0 {
                cmd_by_id.insert(troll.id, format!("HARVEST {}", troll.id));
                reserved.insert(tree.pos());
                continue;
            }
        }
        // 3. Mine iron if we're saving for a train and adjacent to iron.
        if need_iron && troll.chop_power > 0 {
            if state.iron_cells.iter().any(|ic| is_adjacent(troll.pos(), *ic)) {
                cmd_by_id.insert(troll.id, format!("MINE {}", troll.id));
                continue;
            }
        }
        // 4. Head for the nearest reachable FRUITED tree (harvest income). If none,
        //    fall back to the nearest reachable tree to CHOP (wood), or to iron if we
        //    need it, else bank what we carry.
        let dist = bfs_distances(&state.walkable, &[troll.pos()]);
        let nearest = |fruited: bool| -> Option<(i32, Cell)> {
            state
                .trees
                .iter()
                .filter(|t| !fruited || t.fruits > 0)
                .filter(|t| !reserved.contains(&t.pos()))
                .filter_map(|t| dist.get(&t.pos()).map(|&d| (d, t.pos())))
                .min()
        };
        // The dedicated chopper heads for the NEAREST tree (any) to fell it. Harvesters
        // head for the nearest FRUITED tree, PREFERRING the training resource we're
        // shortest on (plum/lemon/apple) -- otherwise we starve a resource (usually
        // APPLE, needed for harvestPower) and can't train past 2 trolls. Fall back to
        // any fruited tree, then any tree (never chop -> trees live).
        let need_idx = (0..3usize).min_by_key(|&i| state.my_inventory[i]).unwrap();
        let need_ty = ["PLUM", "LEMON", "APPLE"][need_idx];
        let nearest_typed = |ty: &str| -> Option<(i32, Cell)> {
            state
                .trees
                .iter()
                .filter(|t| t.fruits > 0 && t.tree_type == ty && !reserved.contains(&t.pos()))
                .filter_map(|t| dist.get(&t.pos()).map(|&d| (d, t.pos())))
                .min()
        };
        let target = if is_chopper {
            nearest(false)
        } else {
            nearest_typed(need_ty)
                .or_else(|| nearest(true))
                .or_else(|| nearest(false))
        };
        // If we need iron and there's a reachable iron cell, a chopper may go mine.
        let iron_target: Option<(i32, Cell)> = if need_iron && troll.chop_power > 0 {
            state
                .iron_cells
                .iter()
                .flat_map(|ic| ortho_neighbors(*ic))
                .filter(|c| state.walkable.contains(c))
                .filter_map(|c| dist.get(&c).map(|&d| (d, c)))
                .min()
        } else {
            None
        };

        // When we're saving for the chopper and short on iron, a chop-capable troll
        // PRIORITIZES mining (go straight to iron) -- otherwise the lone miner stays
        // harvesting and we stall 1 iron short of the big chopper, hoarding fruit
        // (observed: 105-109 loss, iron 5 vs the 6 needed). Iron need self-limits (once
        // banked enough, need_iron flips off and we return to fruit).
        let go: Option<Cell> = match (target, iron_target) {
            (_, Some((_, ci))) => Some(ci),
            (Some((_, c)), None) => Some(c),
            (None, None) => None,
        };
        match go {
            Some(c) => {
                reserved.insert(c);
                cmd_by_id.insert(troll.id, format!("MOVE {} {} {}", troll.id, c.0, c.1));
            }
            None => {
                if troll.total_carried() > 0 {
                    cmd_by_id.insert(troll.id, bank_command(troll, state));
                } else {
                    cmd_by_id.insert(troll.id, format!("WAIT"));
                }
            }
        }
    }

    // Spread bankers over free shack-adjacent drop cells (reuse the wedge-free logic:
    // nearest reachable free cell per banker).
    let (sx, sy) = shack;
    let mut bankers: Vec<i32> = cmd_by_id
        .iter()
        .filter(|(tid, cmd)| cmd.as_str() == format!("MOVE {} {} {}", tid, sx, sy).as_str())
        .map(|(tid, _)| *tid)
        .collect();
    bankers.sort();
    if !bankers.is_empty() {
        let banker_set: HashSet<i32> = bankers.iter().copied().collect();
        let blocked: HashSet<Cell> = my
            .iter()
            .filter(|u| !banker_set.contains(&u.id))
            .map(|u| u.pos())
            .collect();
        let mut used: HashSet<Cell> = HashSet::new();
        for &tid in &bankers {
            let from = my.iter().find(|u| u.id == tid).map(|u| u.pos()).unwrap_or(shack);
            let d = bfs_distances(&state.walkable, &[from]);
            let cell = shack_adj
                .iter()
                .filter(|c| !blocked.contains(c) && !used.contains(c))
                .min_by_key(|c| *d.get(*c).unwrap_or(&(1 << 30)))
                .copied()
                .unwrap_or(shack);
            used.insert(cell);
            cmd_by_id.insert(tid, format!("MOVE {} {} {}", tid, cell.0, cell.1));
        }
    }

    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        commands.push(cmd_by_id[&id].clone());
    }

    // Train the strongest affordable power-troll -- invest, don't hoard. Requires a
    // free shack (a troll spawns on it) and enough turns left to pay off.
    if let Some(spec) = trainable {
        if (n as usize) < MAX_POWER_TROLLS
            && TOTAL_TURNS - state.turn > PARAMS.min_turns_left_to_train
            && !my.iter().any(|t| t.pos() == shack)
        {
            commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
    }

    if commands.is_empty() {
        commands.push("WAIT".to_string());
    }
    commands
}

fn decide_old(state: &State) -> Vec<String> {
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
        && my_trolls_sorted.len() < PARAMS.opening_max_trolls
        && state.turn <= PARAMS.opening_turns
    {
        // Opening: strongest chopper whose fruit we can already cover (iron via mining).
        PARAMS.opening_chopper_specs.iter().copied().find(|s| afford_fruit(*s))
    } else {
        plan.train
    };
    let mining_useful = match next_spec {
        Some(spec) => afford_fruit(spec) && state.my_inventory[IRON] < training_cost(n_now, spec)[IRON],
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
    // collapses and improved margin across the whole field (measured, v0.8.0).

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
    if state.turn <= PARAMS.opening_turns && n < PARAMS.opening_max_trolls {
        let pay: &[usize] = if !state.iron_cells.is_empty() { &[0, 1, 2, 4] } else { &[0, 1, 2] };
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
            && n < PARAMS.max_trolls
        {
            commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
    }

    if commands.is_empty() {
        commands.push("WAIT".to_string());
    }
    commands
}

// ── I/O parsing ───────────────────────────────────────────────────────────────

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
                _ => {} // '#' and others are rocks
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
        // id player x y ms cc hp chop carry[6]
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

// ── main ──────────────────────────────────────────────────────────────────────

/// Echo per-turn state to stderr for sim validation (gated by DEBUG). At turn 1
/// it logs the map + full initial trees/trolls (to reconstruct the start); every
/// turn it logs a compact digest (both inventories + all troll positions) so a
/// captured game can be replayed through the sim and compared turn-by-turn.
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

    // Compact per-turn SUMMARY (printed LAST so it's the console line that survives
    // truncation): both scores, tree count, and OPPONENT troll stats -- so we can read
    // the real Boss 4's composition (fruit vs wood) and troll build from one screenshot.
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

    // Read header: width height
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
                let cmds = decide(&state);
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}
