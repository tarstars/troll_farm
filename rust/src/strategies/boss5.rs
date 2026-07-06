//! BOSS 5 model — the Gold→Legend boss, reconstructed from real arena games
//! (see docs/BOSS5-FINDINGS.md). Banks ~84 wood with a lean 2-troll economy:
//!   • Troll 1 (starter 1,1,1,1): BANANA printer — plant near base (big farm),
//!     harvest fruit for seeds, MINE iron to fund the chopper.
//!   • Troll 2 (2,3,0,2, cc=3): trained at TURN 1 from the starting inventory;
//!     perma-chops, felling ready trees (prefers size 3 → cc=3 captures 3 wood),
//!     and ROAMS CROSS-MAP into the opponent's half to deny their trees.
//! This is a MODEL for offline analysis, not a byte-exact replica (we only have
//! aggregate stats: 37 fells = {1:7, 2:13, 3:17}, ~36 bananas planted, denies on
//! the opponent half). Env knobs B5_* let us tune it. Prints "MSG :]".
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, BANANA, IRON};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;

pub struct Boss5 {
    mem: RefCell<HashMap<i32, Cell>>,
}
impl Boss5 {
    pub fn new() -> Self {
        Boss5 { mem: RefCell::new(HashMap::new()) }
    }
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

impl Strategy for Boss5 {
    fn name(&self) -> &str {
        "boss5"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.mem.borrow_mut().clear();
        }
        let shack = game.shacks[player];
        let opp_shack = game.shacks[1 - player];
        let inv = &game.inventories[player];
        let have_iron = !game.iron.is_empty();

        let mut my: Vec<&Unit> = game.units.iter().filter(|u| u.player as usize == player).collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        // ── train the ONE cc=3 chopper as early as affordable (turn 1 on a normal draw) ──
        let spec = (2, envi("B5_CC", 3), 0, 2);
        let train_now = ((n as usize) < 2)
            && !my.iter().any(|u| u.chop >= 2)
            && afford(inv, &training_cost(n, spec), have_iron);

        let farm_r = envi("B5_FARM_R", 3);
        let farm_cap = envi("B5_FARM_MAX", 18) as usize;
        let base_trees = game.plants.iter().filter(|p| manh(p.pos(), shack) <= farm_r).count();
        // is a fruit type needed to fund the (not-yet-trained) chopper?
        let cost = training_cost(n, spec);
        let need_iron = have_iron && (n as usize) < 2 && inv[IRON] < cost[IRON];

        let mut mem = self.mem.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();

        for u in &my {
            let d = bfs(&game.walkable, u.pos());
            let is_chopper = u.chop >= 2;

            // endgame banking: carry home before t=300
            if u.total() > 0 {
                let turns_rem = TOTAL_TURNS - game.turn + 1;
                let d_home = ortho(shack).iter().filter_map(|c| d.get(c)).min().copied().unwrap_or(1 << 29);
                let eta = (d_home + u.ms - 1) / u.ms.max(1) + 1;
                if turns_rem <= eta + 1 {
                    bank(&mut cmd_by_id, u, shack, &d, &game.walkable);
                    continue;
                }
            }

            if is_chopper {
                // ── CHOPPER: fell + CROSS-MAP DENIAL ──────────────────────────
                // on a fellable tree now?
                if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                    if p.size >= envi("B5_FELL_SIZE", 2) {
                        cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                        reserved.insert(u.pos());
                        continue;
                    }
                }
                if u.free() == 0 {
                    bank(&mut cmd_by_id, u, shack, &d, &game.walkable);
                    continue;
                }
                // target: nearest ready tree, but BIAS toward the opponent's half
                // (denial). Cost = bfs dist − denial_bonus if the tree is past mid-map
                // toward the opponent, so it prefers stealing their trees.
                let midx = (shack.0 + opp_shack.0) / 2;
                let toward_opp = |c: Cell| -> bool {
                    if opp_shack.0 >= shack.0 { c.0 >= midx } else { c.0 <= midx }
                };
                let bonus = envi("B5_DENY_BONUS", 6);
                let tgt = game
                    .plants
                    .iter()
                    .filter(|p| p.size >= envi("B5_FELL_SIZE", 2))
                    .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                    .min_by_key(|p| d[&p.pos()] - if toward_opp(p.pos()) { bonus } else { 0 })
                    .map(|p| p.pos());
                match tgt {
                    Some(c) => {
                        reserved.insert(c);
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                    }
                    None => {
                        // nothing to fell — walk toward the opponent base to deny.
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, opp_shack.0, opp_shack.1));
                    }
                }
                continue;
            }

            // ── STARTER: banana printer + harvest + mine iron ────────────────
            if u.free() == 0 {
                bank(&mut cmd_by_id, u, shack, &d, &game.walkable);
                continue;
            }
            // plant a carried banana on a free base cell
            if base_trees < farm_cap && u.carry[BANANA] > 0 {
                let tc = game
                    .walkable
                    .iter()
                    .filter(|c| manh(**c, shack) <= farm_r && d.contains_key(*c))
                    .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                    .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                    .min_by_key(|c| d[*c])
                    .copied();
                if let Some(tc) = tc {
                    if u.pos() == tc {
                        cmd_by_id.insert(u.id, format!("PLANT {} BANANA", u.id));
                    } else {
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                    }
                    continue;
                }
            }
            // on a ripe tree -> harvest a seed
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if p.fruits > 0 && u.hp > 0 && u.free() > 0 {
                    cmd_by_id.insert(u.id, format!("HARVEST {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
            }
            // at shack with a banked banana seed & room to print -> PICK it
            if base_trees < farm_cap && manh(u.pos(), shack) == 1 && u.free() > 0 && inv[BANANA] > 0 {
                cmd_by_id.insert(u.id, format!("PICK {} BANANA", u.id));
                continue;
            }
            // mine iron when it's the binding fund constraint
            if need_iron && game.iron.iter().any(|ic| manh(u.pos(), *ic) == 1) {
                cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                continue;
            }
            // else move to a target: ripe fruit -> iron -> shack
            let nearest_ripe = game
                .plants
                .iter()
                .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                .min_by_key(|p| d[&p.pos()])
                .map(|p| p.pos());
            let iron_target = if need_iron {
                game.iron
                    .iter()
                    .flat_map(|ic| ortho(*ic))
                    .filter(|c| d.contains_key(c) && !reserved.contains(c))
                    .min_by_key(|c| d[c])
            } else {
                None
            };
            let go = nearest_ripe.or(iron_target);
            match go {
                Some(c) => {
                    reserved.insert(c);
                    mem.insert(u.id, c);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                }
                None => {
                    let sc = ortho(shack)
                        .into_iter()
                        .filter(|c| game.walkable.contains(c))
                        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, sc.0, sc.1));
                }
            }
        }

        let mut actions: Vec<String> = vec!["MSG :]".into()];
        let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
        ids.sort();
        for id in ids {
            actions.push(cmd_by_id[&id].clone());
        }
        if train_now && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT && !my.iter().any(|u| u.pos() == shack) {
            actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
        actions
    }
}

/// bank whatever the unit carries: DROP if shack-adjacent, else move to the
/// nearest shack-adjacent walkable cell.
fn bank(
    cmd_by_id: &mut HashMap<i32, String>,
    u: &Unit,
    shack: Cell,
    d: &HashMap<Cell, i32>,
    walkable: &HashSet<Cell>,
) {
    if manh(u.pos(), shack) == 1 {
        cmd_by_id.insert(u.id, format!("DROP {}", u.id));
    } else {
        let drop_cell = ortho(shack)
            .into_iter()
            .filter(|c| walkable.contains(c))
            .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
            .unwrap_or(shack);
        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1));
    }
}
