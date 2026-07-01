use std::collections::HashSet;
use super::state::{Cell, GameState, Plant, Unit};
use super::engine::{bfs_distances, tick_plants, plant_cooldown, tree_health, MAX_SIZE, MAX_FRUITS, IRON};

// Match the real Bronze arena: 20x10 grids, sparse trees (~5 pairs = ~10 trees,
// density ~0.05/cell). The old 16x8 with 1-3 pairs/type (~16 trees, ~0.13/cell)
// was 3x too tree-dense, which structurally over-rewarded sustained fruit
// harvesting (renewable) over one-shot chopping (destructive) -- biasing the
// local ladder against every chop strategy. See docs/mechanics.md.
const WIDTH: i32 = 20;
const HEIGHT: i32 = 10;

const FRUITS: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

// Density knobs (env, for Silver-fidelity calibration; the real arena is far denser
// than the old sparse Bronze maps). TREE_LO/TREE_HI = pairs-per-fruit-type range;
// WATER_PAIRS / IRON_PAIRS = terrain pairs. Defaults reproduce the old sparse map.
fn envi(name: &str, default: i32) -> i32 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default)
}

// ── SplitMix64 PRNG ──────────────────────────────────────────────────────────

struct Rng(u64);

impl Rng {
    fn new(seed: u64) -> Self {
        Rng(seed)
    }

    fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15u64);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9u64);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111ebu64);
        z ^ (z >> 31)
    }

    /// Random integer in [0, n)
    fn randrange(&mut self, n: i32) -> i32 {
        (self.next_u64() % n as u64) as i32
    }

    /// Random integer in [lo, hi] inclusive
    fn randint(&mut self, lo: i32, hi: i32) -> i32 {
        lo + self.randrange(hi - lo + 1)
    }

    /// Shuffle a slice in place (Fisher-Yates)
    fn shuffle<T>(&mut self, v: &mut Vec<T>) {
        let n = v.len();
        for i in (1..n).rev() {
            let j = self.randrange((i + 1) as i32) as usize;
            v.swap(i, j);
        }
    }

    /// Pick a random element from a non-empty slice
    fn choice<T: Clone>(&mut self, v: &[T]) -> T {
        let i = self.randrange(v.len() as i32) as usize;
        v[i].clone()
    }
}

// ── helpers ───────────────────────────────────────────────────────────────────

fn mirror(cell: Cell) -> Cell {
    (WIDTH - 1 - cell.0, HEIGHT - 1 - cell.1)
}

/// Check that all walkable cells are reachable from shack-adjacent walkable cells.
fn all_reachable(walkable: &HashSet<Cell>, shack: Cell) -> bool {
    let sources: Vec<Cell> = [
        (shack.0, shack.1 + 1),
        (shack.0 + 1, shack.1),
        (shack.0, shack.1 - 1),
        (shack.0 - 1, shack.1),
    ]
    .iter()
    .filter(|n| walkable.contains(n))
    .copied()
    .collect();

    if sources.is_empty() {
        return walkable.is_empty();
    }

    let dist = bfs_distances(walkable, &sources);
    walkable.iter().all(|c| dist.contains_key(c))
}

// ── generate (Bronze-like base map) ─────────────────────────────────────────

/// Generate a valid symmetric Bronze map.
/// The Rust RNG differs from Python's random module so maps will differ,
/// but structural properties are identical.
pub fn generate_bronze(seed: u64) -> GameState {
    let mut rnd = Rng::new(seed);

    // ── step 1: pick shacks (mirror-symmetric) ──────────────────────────────
    let (s0, s1) = loop {
        let x = rnd.randrange(WIDTH / 2);
        let y = rnd.randrange(HEIGHT);
        let s0: Cell = (x, y);
        let s1 = mirror(s0);
        if s0 == s1 {
            continue;
        }
        // Build initial walkable (all cells except shacks)
        let mut w: HashSet<Cell> = (0..WIDTH).flat_map(|x| (0..HEIGHT).map(move |y| (x, y))).collect();
        w.remove(&s0);
        w.remove(&s1);
        if all_reachable(&w, s0) {
            break (s0, s1);
        }
    };

    let mut walkable: HashSet<Cell> = (0..WIDTH)
        .flat_map(|x| (0..HEIGHT).map(move |y| (x, y)))
        .collect();
    walkable.remove(&s0);
    walkable.remove(&s1);

    // ── step 2: plant fruit trees ────────────────────────────────────────────
    let inv_fruits: Vec<i32> = (0..4).map(|_| rnd.randint(2, 10)).collect();
    let inv0: [i32; 6] = [inv_fruits[0], inv_fruits[1], inv_fruits[2], inv_fruits[3], 0, 0];
    let inv1 = inv0;

    let mut plants: Vec<Plant> = Vec::new();
    let mut used: HashSet<Cell> = HashSet::new();
    used.insert(s0);
    used.insert(s1);

    let (tree_lo, tree_hi) = (envi("TREE_LO", 1), envi("TREE_HI", 2));
    for &ftype in &FRUITS {
        let count = rnd.randint(tree_lo, tree_hi);
        for _ in 0..count {
            // Sort before the seeded RNG picks: HashSet iteration order is randomized
            // per process, so without this the SAME seed produces DIFFERENT maps on
            // every run -- making every tournament/diag measurement irreproducible.
            let mut free: Vec<Cell> = walkable.iter().filter(|c| !used.contains(*c)).copied().collect();
            free.sort_unstable();
            if free.is_empty() {
                break;
            }
            let cell = rnd.choice(&free);
            let mc = mirror(cell);
            if mc == cell || used.contains(&mc) || !walkable.contains(&mc) {
                continue;
            }
            used.insert(cell);
            used.insert(mc);

            let base = plant_cooldown(ftype);
            let ticks = rnd.randint(1, base * (MAX_SIZE + MAX_FRUITS));

            // Age the pair identically
            // Start at size 0 / base health; tick_plants ages each pair, growing
            // size and bumping health by the type's slope, so they finish at the
            // real `health = base + slope*size`.
            let h0 = tree_health(ftype, 0);
            let pair: Vec<Plant> = vec![
                Plant { plant_type: ftype.to_string(), x: cell.0, y: cell.1, size: 0, health: h0, fruits: 0, cooldown: 0 },
                Plant { plant_type: ftype.to_string(), x: mc.0, y: mc.1, size: 0, health: h0, fruits: 0, cooldown: 0 },
            ];
            // Simulate tick_plants on these two plants alone (no water adjustment)
            // using a temporary minimal game state
            let tmp_walkable: HashSet<Cell> = walkable.iter().copied().collect();
            let mut tmp = GameState {
                width: WIDTH,
                height: HEIGHT,
                walkable: tmp_walkable,
                shacks: [s0, s1],
                inventories: [inv0, inv1],
                units: Vec::new(),
                plants: pair,
                scores: [0, 0],
                turn: 1,
                next_id: 0,
                iron: HashSet::new(),
                water: HashSet::new(),
            };
            for _ in 0..ticks {
                tick_plants(&mut tmp);
            }
            plants.extend(tmp.plants);
        }
    }

    // ── step 3: ensure at least one fruit is available ───────────────────────
    // If no plant has fruits, force-ripen the first one
    if plants.iter().all(|p| p.fruits == 0) && !plants.is_empty() {
        let tmp_walkable: HashSet<Cell> = walkable.iter().copied().collect();
        let mut tmp = GameState {
            width: WIDTH,
            height: HEIGHT,
            walkable: tmp_walkable,
            shacks: [s0, s1],
            inventories: [inv0, inv1],
            units: Vec::new(),
            plants: plants.clone(),
            scores: [0, 0],
            turn: 1,
            next_id: 0,
            iron: HashSet::new(),
            water: HashSet::new(),
        };
        for _ in 0..200 {
            tick_plants(&mut tmp);
            if tmp.plants.iter().any(|p| p.fruits > 0) {
                break;
            }
        }
        plants = tmp.plants;
    }

    // ── step 4: add iron/water cells (Bronze additions) ─────────────────────
    let mut rnd2 = Rng::new(seed.wrapping_mul(2654435761) % (1u64 << 32));

    let mut iron: HashSet<Cell> = HashSet::new();
    let mut water: HashSet<Cell> = HashSet::new();

    let blocked: HashSet<Cell> = {
        let mut b = HashSet::new();
        b.insert(s0);
        b.insert(s1);
        for p in &plants {
            b.insert(p.pos());
        }
        b
    };

    let mut candidates: Vec<Cell> = walkable.iter().filter(|c| !blocked.contains(*c)).copied().collect();
    candidates.sort_unstable(); // determinism: fix HashSet order before the seeded shuffle
    rnd2.shuffle(&mut candidates);

    // Place 2 pairs of iron cells
    let mut placed = 0;
    let mut ci = 0;
    while placed < envi("IRON_PAIRS", 2) as usize && ci < candidates.len() {
        let c = candidates[ci];
        ci += 1;
        let m = mirror(c);
        if c == m || !walkable.contains(&c) || !walkable.contains(&m) {
            continue;
        }
        if iron.contains(&c) || iron.contains(&m) || water.contains(&c) || water.contains(&m) {
            continue;
        }
        let trial: HashSet<Cell> = walkable.iter().filter(|x| **x != c && **x != m).copied().collect();
        if !all_reachable(&trial, s0) {
            continue;
        }
        walkable = trial;
        iron.insert(c);
        iron.insert(m);
        placed += 1;
    }

    // Place 3 pairs of water cells
    let mut placed = 0;
    while placed < envi("WATER_PAIRS", 3) as usize && ci < candidates.len() {
        let c = candidates[ci];
        ci += 1;
        let m = mirror(c);
        if c == m || !walkable.contains(&c) || !walkable.contains(&m) {
            continue;
        }
        if iron.contains(&c) || iron.contains(&m) || water.contains(&c) || water.contains(&m) {
            continue;
        }
        let trial: HashSet<Cell> = walkable.iter().filter(|x| **x != c && **x != m).copied().collect();
        if !all_reachable(&trial, s0) {
            continue;
        }
        walkable = trial;
        water.insert(c);
        water.insert(m);
        placed += 1;
    }

    // ── step 5: starting iron inventory ──────────────────────────────────────
    let iron_start = rnd2.randint(2, 10);
    let mut inv0_final = inv0;
    let mut inv1_final = inv1;
    inv0_final[IRON] = iron_start;
    inv1_final[IRON] = iron_start;

    // ── step 6: create units with chop=1 (Bronze) ───────────────────────────
    let units = vec![
        Unit { id: 0, player: 0, x: s0.0, y: s0.1, ms: 1, cc: 1, hp: 1, chop: 1, carry: [0; 6] },
        Unit { id: 1, player: 1, x: s1.0, y: s1.1, ms: 1, cc: 1, hp: 1, chop: 1, carry: [0; 6] },
    ];

    GameState {
        width: WIDTH,
        height: HEIGHT,
        walkable,
        shacks: [s0, s1],
        inventories: [inv0_final, inv1_final],
        units,
        plants,
        scores: [0, 0],
        turn: 1,
        next_id: 2,
        iron,
        water,
    }
}
