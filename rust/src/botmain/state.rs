//! State layer (R3a): game-state types, item indices, and pure helpers shared by
//! every decider. Extracted VERBATIM from botmain.rs (only visibility added);
//! behavior equality is enforced by the black-box harness (src/bin/equality.rs).
use std::collections::{HashMap, HashSet, VecDeque};

pub const TOTAL_TURNS: i32 = 300;

// Item indices: PLUM=0, LEMON=1, APPLE=2, BANANA=3, IRON=4, WOOD=5
pub const PLUM: usize = 0;
pub const LEMON: usize = 1;
pub const APPLE: usize = 2;
pub const BANANA: usize = 3;
pub const IRON: usize = 4;
pub const WOOD: usize = 5;

// Base growth cooldown per tree type
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
    pub tree_type: String, // "PLUM","LEMON","APPLE","BANANA"
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

// ── geometry helpers ─────────────────────────────────────────────────────────

pub const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];

pub fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
    let (x, y) = cell;
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
}

pub fn is_adjacent(a: Cell, b: Cell) -> bool {
    (a.0 - b.0).abs() + (a.1 - b.1).abs() == 1
}

// ── BFS ─────────────────────────────────────────────────────────────────────

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

// ── training cost ────────────────────────────────────────────────────────────

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

// ── R5.0: deterministic tie-break "spread" ──────────────────────────────────
// v1.20.0's HashSet iteration accidentally gave RANDOM-PER-GAME tie-breaking, which
// spread plant spots around the shack; the R1 lexicographic determinization clustered
// them (measured ~-0.5 arena vs same-hour baseline). These helpers restore the spread
// deterministically: a per-game salt from immutable map facts (STABLE WITHIN a game so
// tied targets never flap turn-to-turn) mixed with the cell -> a pseudo-random rank.

/// per-game-stable salt from immutable map facts (varies across maps/seats).
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

/// mix a cell with the salt -> deterministic pseudo-random tie-break rank.
pub fn tie_mix(c: Cell, salt: u64) -> u64 {
    let mut h = salt
        ^ (c.0 as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (c.1 as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F);
    h ^= h >> 33;
    h = h.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    h ^= h >> 29;
    h
}
