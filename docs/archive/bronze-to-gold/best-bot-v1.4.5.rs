// ============================================================================
//  Troll Farm — BEST BOT (readable single-file edition)   v1.4.5-seedreserve
//  CodinGame Spring Challenge 2026 · 2-player · ~300 turns · 50 ms/turn
// ----------------------------------------------------------------------------
//  This is the arena submission cgauto/submissions/v1.4.5-seedreserve.rs with
//  all DEAD code removed, so ONLY the live decision path remains:
//
//      fn main()  ->  read game state each turn  ->  fn decide_elite(&State)
//
//  decide_elite implements the "gold-elite" strategy: keep exactly TWO trolls
//  (a (1,1,1,1) starter + one trained (2,2,0,2) chopper), run a banana-"printer"
//  farm next to the base, and perma-fell it for WOOD (worth 4x a fruit).
//
//  The companion PDF (docs/best-bot-v1.4.5.pdf) explains (A) the Rust syntax
//  for C++/Go/Python readers, (B) the strategy & why, (C) this code block-by-block.
//
//  Removed from the submission (NOT part of the live path): decide_sched, the
//  RHEA rollout search + "fast engine" (NavTable / FastState / step_fast),
//  decide_rhea, and the evolution structs. Kept alongside decide_elite: the two
//  small helpers the live path still calls -- mb_afford (training affordability)
//  and rh_rand (the watchdog's RNG).
//
//  Compiles standalone:   rustc --edition 2021 -O best-bot-v1.4.5.rs
// ============================================================================

// crate_name override: `rustc best-bot-v1.4.5.rs` would otherwise reject the dots
// in the filename (illegal in a rustc-derived crate name). No effect on behaviour.
#![crate_name = "bestbot"]
#![allow(dead_code, unused)]

use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};
use std::cell::RefCell;

// ── constants ────────────────────────────────────────────────────────────────
const VERSION: &str = "1.4.5-seedreserve";
const TOTAL_TURNS: i32 = 300;
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

fn afford_fruit_only(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}

// ── training affordability (called by decide_elite's training gate) ──────────
fn mb_afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}

// ── xorshift RNG (used by decide_elite's anti-stall watchdog for a sidestep) ──
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

const GE_SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2); // the one trained chopper
const GE_MAX_TROLLS: i32 = 2; // stop training at 2 trolls
const GE_FARM_R: i32 = 3; // banana-farm radius around base
const GE_FARM_MAX: usize = 12; // farm cap (max base trees)
const GE_FELL_SIZE: i32 = 2; // min tree size to fell (pre-liquidation)
const GE_CHOP_R: i32 = 10; // max manh(tree, shack) the chopper roams
const GE_LIQ_T: i32 = 34; // turns_rem <= this: fell anything reachable
const GE_STARTER_CHOP: bool = true; // let a chop-capable starter help fell
const GE_MIN_TURNS_LEFT: i32 = 20; // no training inside the last 20 turns
const GE_SEED_RESERVE: usize = 2; // protect K most-mature farm bananas as seed sources
const GE_FARM_FELL: i32 = 2; // fell threshold for NON-reserved farm bananas

thread_local! {
    // GoldElite::mem — last sticky target cell per troll. In the lib this field
    // is write-only (never read), so it has no behavioural effect; kept for a
    // faithful 1:1 port. Reset at turn 1.
    static GE_MEM: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
    // anti-stall watchdog (NEW safety net, mirrors decide_rhea/RH_LASTPOS):
    // troll id -> (x, y, same-pos streak while MOVEing). Reset at turn 1.
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

/// v1.4.0 live decider: the gold-elite pure-production strategy. The standalone
/// bot is always player 0 (my_trolls). A 1:1 port of GoldElite::decide with an
/// added turn-1 MSG and an anti-stall watchdog (below).
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

    // ── training: exactly ONE chopper, then stop at GE_MAX_TROLLS trolls ─────
    let spec = GE_SPEC;
    let want_chopper = n < GE_MAX_TROLLS && !my.iter().any(|u| u.chop_power >= 2);
    let cost = training_cost(n, spec);
    let train_now = want_chopper && mb_afford(inv, &cost, have_iron);
    // iron-gated: fruit is ready but we still lack the iron for the chopper.
    let need_iron =
        have_iron && want_chopper && inv[IRON] < cost[IRON] && afford_fruit_only(inv, &cost);
    // which fruit types still block the chopper (funding targets)
    let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];

    // ── farm config ─────────────────────────────────────────────────────────
    let farm_r = GE_FARM_R;
    let farm_cap = GE_FARM_MAX;
    let fell_size = GE_FELL_SIZE;
    let chop_r = GE_CHOP_R; // max manh(tree, shack) the chopper roams
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state.trees.iter().filter(|p| manhattan(p.pos(), shack) <= farm_r).count();

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
            .filter(|p| p.tree_type == "BANANA" && manhattan(p.pos(), shack) <= farm_r)
            .collect();
        fb.sort_by_key(|p| (-p.size, -p.fruits, manhattan(p.pos(), shack), p.pos()));
        for p in fb.into_iter().take(GE_SEED_RESERVE) {
            seed_cells.insert(p.pos());
        }
    }
    // is a tree currently fellable by the chopper (per-tree threshold)?
    let fell_ok = |p: &Tree| -> bool {
        if seed_cells.contains(&p.pos()) {
            return false; // protected seed source
        }
        if liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA" && manhattan(p.pos(), shack) <= farm_r;
        p.size >= if farm_banana { GE_FARM_FELL } else { fell_size }
    };

    // own-half + reachable + not reserved fellable trees, with fell time
    let own_half = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), opp);
    let within_roam = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= chop_r;

    let mut reserved: HashSet<Cell> = HashSet::new();
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();

    // nearest walkable drop cell -> DROP if adjacent else MOVE toward it
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

        // endgame banking (bank a carried load in time to score it)
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

        // nearest fellable tree (size>=fell_size, own-half, in roam range)
        let nearest_fell = |free_needed: bool| -> Option<Cell> {
            if free_needed && u.free_capacity() == 0 {
                return None;
            }
            state
                .trees
                .iter()
                .filter(|p| fell_ok(p))
                .filter(|p| own_half(p) && within_roam(p))
                .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                .min_by_key(|p| {
                    // prefer close + fast-to-fell (banana health 4 << apple health 20)
                    let steps = (d[&p.pos()] + u.movement_speed - 1) / u.movement_speed.max(1);
                    let chop_t = (p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1);
                    steps + chop_t
                })
                .map(|p| p.pos())
        };

        // ── CHOPPER: perma-fell local trees, bank when full ─────────────────
        if is_chopper {
            if u.free_capacity() == 0 {
                cmd_by_id.insert(u.id, bank_cmd(u, &d));
                continue;
            }
            // standing on a fellable tree -> chop
            if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
                if u.chop_power > 0 && fell_ok(p) {
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
            // ANTI-STARVATION (arena floor fix for the win-rate goal): the local farm
            // is empty -> instead of idling (shutdown games: 5 plants, chopper wandered,
            // wood 22), fell the nearest reachable tree ANYWHERE of size>=1 (1 wood
            // beats 0). Converts shutdown-LOSSES into competitive games. Neutral in
            // sim (no banana-poor maps there); arena is the judge.
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
            // nothing at all to fell: bank a partial load, else idle near base
            cmd_by_id.insert(
                u.id,
                if u.total_carried() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) },
            );
            continue;
        }

        // ── STARTER (1,1,1,0): funder early, banana printer after ───────────
        // free base cell to plant on (prefer water-adjacent: banana cd 6->4)
        // Plant at the NEAREST free base cell; water-adjacency is a mild tiebreak
        // (2 cells' worth), not a hard first pass — trekking to water is the
        // printer's biggest travel sink and travel is the arena's confirmed cost.
        let free_base = |_water: bool| -> Option<Cell> {
            state
                .walkable
                .iter()
                .filter(|c| manhattan(**c, shack) <= farm_r && d.contains_key(*c))
                .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
                .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                .filter(|c| !reserved.contains(*c))
                .min_by_key(|c| {
                    let wet = state.water_cells.iter().any(|w| manhattan(*w, **c) == 1);
                    d[*c] + if wet { 0 } else { 2 }
                })
                .copied()
        };

        // 1) carrying a banana + base room -> plant it near base (BEFORE the
        //    full->bank check, since cc1 + carried banana reads as "full").
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

        // 2) full -> bank
        if u.free_capacity() == 0 {
            cmd_by_id.insert(u.id, bank_cmd(u, &d));
            continue;
        }

        // 3) standing on a ripe fruit tree we want -> harvest
        if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
            if p.fruits > 0 && u.harvest_power > 0 && u.free_capacity() > 0 {
                let ty = ge_fruit_ty(&p.tree_type);
                let want = if want_chopper {
                    ty.map_or(false, |t| t < 3 && need_fund[t])
                } else {
                    // post-funding: only harvest seeds we replant (banana/water apple)
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

        // 4) FUNDING PHASE: mine iron / harvest deficit fruit for the chopper
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
            // nearest ripe deficit fruit
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
            // no deficit fruit reachable — fall through to the printer so the
            // troll never stalls (it pre-seeds the banana farm meanwhile).
        }

        // 5) BANANA PRINTER: keep the farm stocked with bananas
        if base_trees < farm_cap {
            // pick a banked banana at the shack (fastest seed cycle)
            if manhattan(u.pos(), shack) == 1 && inv[BANANA] > 0 && u.free_capacity() > 0 {
                cmd_by_id.insert(u.id, format!("PICK {} BANANA", u.id));
                continue;
            }
            if inv[BANANA] > 0 {
                // go to a shack-adjacent cell to PICK
                cmd_by_id.insert(u.id, park_cmd(u, &d));
                continue;
            }
            // no banked seeds: harvest a native banana (or water-apple) tree
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

        // 6) farm full / no seeds: help chop (chop1), else park at base
        if starter_chop && u.chop_power > 0 {
            if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
                if fell_ok(p) {
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
            // anti-starvation for the starter too: fell the nearest reachable size>=1
            // tree anywhere (with free capacity) rather than parking idle (+4pp vs
            // production bots, the real Gold field).
            if u.free_capacity() > 0 {
                if let Some(tc) = state
                    .trees
                    .iter()
                    .filter(|p| p.size >= 1 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
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
            }
        }
        cmd_by_id.insert(
            u.id,
            if u.total_carried() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) },
        );
    }

    // ── ANTI-STALL WATCHDOG (NEW; mirrors decide_rhea/RH_LASTPOS) ────────────
    // If a troll issued a MOVE but hasn't moved for 2+ consecutive turns, it is
    // self-blocked — sidestep to a free orthogonally-adjacent walkable cell.
    // This is the #1 arena loss cause (self-block stalls).
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
                // parse the MOVE target; only sidestep if it isn't the cur cell
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
                let cmds = decide_elite(&state);
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}
