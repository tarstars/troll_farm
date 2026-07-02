//! SCHEDULER BOT (v0) — the architecture rebuild toward Gold (HANDOFF §7.2).
//! Instead of mybot's fixed per-troll roles and if-else priorities, every turn we
//! enumerate (troll, task) pairs, score each by MARGINAL RATE (points / turns,
//! with a denial uplift for enemy-side fells), and assign greedily best-first.
//! Tasks: BANK carried load, FELL a tree, HARVEST a ripe tree, MINE iron,
//! PRINT (pick+plant banana at base). Training reuses mybot's proven greedy plan.
//! Target (arena-decoded): elite Silver sustains 0.30 wood/turn vs our 0.07.
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, BANANA, IRON, PLUM};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;
const MAX_TROLLS: usize = 4;
const CHOPPER_SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2);
const N_CHOPPERS: i32 = 2;
const HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];

pub struct SchedBot {
    mem: RefCell<HashMap<i32, Cell>>, // last target cell per troll (sticky hysteresis)
}

impl SchedBot {
    pub fn new() -> Self {
        SchedBot { mem: RefCell::new(HashMap::new()) }
    }
}

fn envf(name: &str, d: f64) -> f64 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(d)
}
fn envi(name: &str, d: i32) -> i32 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(d)
}

fn manh(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}
fn ortho(c: Cell) -> [Cell; 4] {
    [(c.0, c.1 + 1), (c.0 + 1, c.1), (c.0, c.1 - 1), (c.0 - 1, c.1)]
}

fn bfs(walkable: &HashSet<Cell>, src: Cell) -> HashMap<Cell, i32> {
    let mut dist = HashMap::new();
    let mut q = VecDeque::new();
    dist.insert(src, 0);
    q.push_back(src);
    while let Some((x, y)) = q.pop_front() {
        let d = dist[&(x, y)];
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let n = (x + dx, y + dy);
            if walkable.contains(&n) && !dist.contains_key(&n) {
                dist.insert(n, d + 1);
                q.push_back(n);
            }
        }
    }
    dist
}

fn afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[0] >= cost[0] && inv[1] >= cost[1] && inv[2] >= cost[2] && iron_ok
}
fn afford_fruit(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[0] >= cost[0] && inv[1] >= cost[1] && inv[2] >= cost[2]
}

#[derive(Clone, Debug)]
enum Task {
    Bank,
    Fell(Cell),
    Harvest(Cell),
    Mine(Cell),   // iron-adjacent cell to stand on
    Print(Cell),  // base cell to plant a carried banana on
    PickSeed,     // pick a banana at the shack
}

impl Strategy for SchedBot {
    fn name(&self) -> &str {
        "schedbot"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.mem.borrow_mut().clear();
        }
        let shack = game.shacks[player];
        let opp = game.shacks[1 - player];
        let inv = &game.inventories[player];
        let have_iron = !game.iron.is_empty();
        let turns_rem = TOTAL_TURNS - game.turn + 1;

        let mut my: Vec<&Unit> = game.units.iter().filter(|u| u.player as usize == player).collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        // ── training: mybot's proven greedy plan, verbatim ──────────────────
        let want_chopper = (my.iter().filter(|u| u.chop >= 2).count() as i32) < N_CHOPPERS;
        let train_now: Option<(i32, i32, i32, i32)> = if want_chopper
            && afford(inv, &training_cost(n, CHOPPER_SPEC), have_iron)
        {
            Some(CHOPPER_SPEC)
        } else {
            HARVESTERS.iter().copied().find(|&s| afford(inv, &training_cost(n, s), have_iron))
        };
        let need_iron = have_iron
            && want_chopper
            && inv[IRON] < training_cost(n, CHOPPER_SPEC)[IRON]
            && afford_fruit(inv, &training_cost(n, CHOPPER_SPEC));

        let has_real_chopper = my.iter().any(|u| u.chop >= 2);
        let bootstrap_id: Option<i32> = if has_real_chopper {
            None
        } else {
            my.iter().filter(|u| u.chop >= 1).max_by_key(|u| (u.cc, -u.id)).map(|u| u.id)
        };

        // knobs (v0 defaults hand-set; sweep later)
        let den_w = envf("SB_DEN", 12.0); // denial uplift (pts-equivalent) at the foe's shack
        let print_v = envf("SB_PRINT", 6.0); // future value of one planted banana
        let base_r = envi("SB_BASE_R", 3);
        let wf_cap = envi("SB_WF_MAX", 6) as usize;
        let span = (game.width + game.height) as f64;

        let base_trees = game.plants.iter().filter(|p| manh(p.pos(), shack) <= base_r).count();
        let window = game.turn >= 20 && game.turn <= 280;

        // per-troll BFS + candidate scoring
        let mut cands: Vec<(f64, usize, Task)> = Vec::new(); // (rate, troll_idx, task)
        let mut dists: Vec<HashMap<Cell, i32>> = Vec::new();
        for (ti, u) in my.iter().enumerate() {
            let d = bfs(&game.walkable, u.pos());
            let d_home = ortho(shack)
                .iter()
                .filter(|c| game.walkable.contains(*c))
                .filter_map(|c| d.get(c))
                .min()
                .copied()
                .unwrap_or(1 << 20);
            let steps = |dist: i32| -> f64 { ((dist + u.ms - 1) / u.ms.max(1)).max(0) as f64 };
            let carried: i32 = u.carry.iter().enumerate().map(|(i, c)| if i == 5 { 4 * c } else { *c }).sum();

            // BANK: carried points become real when dropped.
            if carried > 0 {
                let t = steps(d_home) + 1.0;
                // endgame override: if the clock barely covers banking, it dominates.
                let urgency = if (turns_rem as f64) <= t + 2.0 { 1000.0 } else { 1.0 };
                cands.push((urgency * carried as f64 / t, ti, Task::Bank));
            }

            let is_chop_role = u.chop >= 2 || Some(u.id) == bootstrap_id;

            for p in &game.plants {
                let pos = p.pos();
                let Some(&dd) = d.get(&pos) else { continue };
                // FELL: wood now + denial uplift; costs travel + chop turns (+ bank later, half-charged)
                if is_chop_role && u.chop > 0 {
                    let chop_t = ((p.health + u.chop - 1) / u.chop) as f64;
                    let wood = p.size.min(u.free()) as f64 * 4.0;
                    let den = den_w * (1.0 - manh(pos, opp) as f64 / span);
                    let t = steps(dd) + chop_t + 0.5 * steps(manh(pos, shack)) + 1.0;
                    if turns_rem as f64 > t {
                        cands.push(((wood + den) / t, ti, Task::Fell(pos)));
                    }
                }
                // HARVEST ripe fruit
                if p.fruits > 0 && u.hp > 0 && u.free() > 0 {
                    let take = p.fruits.min(u.hp).min(u.free()) as f64;
                    let t = steps(dd) + 1.0 + 0.5 * steps(manh(pos, shack));
                    if turns_rem as f64 > t {
                        cands.push((take / t, ti, Task::Harvest(pos)));
                    }
                }
            }

            // MINE when iron-gated for the chopper plan
            if need_iron && u.chop > 0 {
                if let Some(c) = game
                    .iron
                    .iter()
                    .flat_map(|ic| ortho(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| d[c])
                {
                    let t = steps(d[&c]) + 1.0;
                    cands.push((envf("SB_MINE_V", 3.0) / t, ti, Task::Mine(c)));
                }
            }

            // PRINT: plant carried banana at base (value = future wood/fruit)
            if window && base_trees < wf_cap && !is_chop_role {
                if u.carry[BANANA] > 0 {
                    let spot = game
                        .walkable
                        .iter()
                        .filter(|c| manh(**c, shack) <= base_r && d.contains_key(*c))
                        .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                        .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                        .min_by_key(|c| {
                            let water = game.water.iter().any(|w| manh(*w, **c) == 1);
                            (!water as i32, d[*c])
                        })
                        .copied();
                    if let Some(sp) = spot {
                        let t = steps(d.get(&sp).copied().unwrap_or(1 << 20)) + 1.0;
                        cands.push((print_v / t, ti, Task::Print(sp)));
                    }
                } else if manh(u.pos(), shack) == 1 && u.free() > 0 && inv[BANANA] > 0 {
                    cands.push((print_v / 2.0, ti, Task::PickSeed));
                }
            }
            dists.push(d);
        }

        // sticky hysteresis: boost the rate of whatever each troll targeted last
        // turn (rates are recomputed from scratch, so near-ties flip targets and
        // trolls oscillate — mybot's sticky memory existed for exactly this).
        let stick = 1.0 + envf("SB_STICK", 0.0);
        {
            let mem = self.mem.borrow();
            for c in cands.iter_mut() {
                let cell = match &c.2 {
                    Task::Fell(x) | Task::Harvest(x) | Task::Mine(x) | Task::Print(x) => Some(*x),
                    _ => None,
                };
                if let (Some(cell), Some(&prev)) = (cell, mem.get(&(my[c.1].id))) {
                    if prev == cell {
                        c.0 *= stick;
                    }
                }
            }
        }
        // greedy joint assignment: best rate first; one task per troll, one troll per target
        cands.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
        let mut assigned: HashMap<usize, Task> = HashMap::new();
        let mut taken: HashSet<Cell> = HashSet::new();
        for (_, ti, task) in cands {
            if assigned.contains_key(&ti) {
                continue;
            }
            let cell = match &task {
                Task::Fell(c) | Task::Harvest(c) | Task::Mine(c) | Task::Print(c) => Some(*c),
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

        {
            let mut mem = self.mem.borrow_mut();
            for (ti, task) in &assigned {
                let cell = match task {
                    Task::Fell(x) | Task::Harvest(x) | Task::Mine(x) | Task::Print(x) => Some(*x),
                    _ => None,
                };
                match cell {
                    Some(c) => {
                        mem.insert(my[*ti].id, c);
                    }
                    None => {
                        mem.remove(&my[*ti].id);
                    }
                }
            }
        }

        // emit commands
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
        for (ti, u) in my.iter().enumerate() {
            let d = &dists[ti];
            let go_move = |c: Cell| format!("MOVE {} {} {}", u.id, c.0, c.1);
            let cmd = match assigned.get(&ti) {
                Some(Task::Bank) => {
                    if manh(u.pos(), shack) == 1 {
                        format!("DROP {}", u.id)
                    } else {
                        let drop_cell = ortho(shack)
                            .into_iter()
                            .filter(|c| game.walkable.contains(c))
                            .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                            .unwrap_or(shack);
                        go_move(drop_cell)
                    }
                }
                Some(Task::Fell(c)) => {
                    if u.pos() == *c {
                        format!("CHOP {}", u.id)
                    } else {
                        go_move(*c)
                    }
                }
                Some(Task::Harvest(c)) => {
                    if u.pos() == *c {
                        format!("HARVEST {}", u.id)
                    } else {
                        go_move(*c)
                    }
                }
                Some(Task::Mine(c)) => {
                    if u.pos() == *c {
                        format!("MINE {}", u.id)
                    } else {
                        go_move(*c)
                    }
                }
                Some(Task::Print(c)) => {
                    if u.pos() == *c {
                        format!("PLANT {} BANANA", u.id)
                    } else {
                        go_move(*c)
                    }
                }
                Some(Task::PickSeed) => format!("PICK {} BANANA", u.id),
                None => {
                    // idle: park near base (never on the shack cell)
                    let drop_cell = ortho(shack)
                        .into_iter()
                        .filter(|c| game.walkable.contains(c))
                        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    go_move(drop_cell)
                }
            };
            cmd_by_id.insert(u.id, cmd);
        }

        let mut actions: Vec<String> = Vec::new();
        let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
        ids.sort();
        for id in ids {
            actions.push(cmd_by_id[&id].clone());
        }
        if let Some(spec) = train_now {
            if (n as usize) < envi("SB_MAX", MAX_TROLLS as i32) as usize
                && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT
                && !my.iter().any(|u| u.pos() == shack)
            {
                actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }
        if actions.is_empty() {
            actions.push("WAIT".into());
        }
        actions
    }
}
