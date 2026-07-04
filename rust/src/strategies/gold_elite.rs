//! GOLD-ELITE — a STRONG sparring bot that replicates the decoded Gold elite
//! (GoodDevel, PonyPonyCodeCode; see task handoff). The point: printerbot banks
//! only ~21 wood and LOSES to a weak fruit bot, so "beat printerbot" is a
//! meaningless objective — every bot crushes a weak opponent, so the sim scores
//! 220+ while the arena plateaus at ~170. This bot instead banks ~40 WOOD vs a
//! weak opponent, so the local sim finally discriminates like the Gold arena.
//!
//! Decoded profile it replicates:
//!  - EXACTLY 2 trolls: the (1,1,1,1) starter + ONE trained (2,2,0,2) perma-chop.
//!  - Harvest-first opening: the starter harvests fruit (and mines iron) to fund
//!    the chopper, trained ~t20-77.
//!  - Then SUSTAINED local chopping: the chopper fells own-half trees near base,
//!    banking every time it fills (cc2), ~100% utilisation, no denial treks.
//!  - Banana printer: the starter continuously re-seeds BANANA near base (PICK a
//!    banked banana / harvest a native banana tree -> PLANT), so the chopper
//!    always has a ripe local tree. Banked fruit stays ~0 — everything funnels
//!    into WOOD (banks ~40-65 wood = 160-260 pts, final score 230-320).
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, BANANA, IRON};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;

pub struct GoldElite {
    mem: RefCell<HashMap<i32, Cell>>, // last target cell per troll (sticky)
}

impl GoldElite {
    pub fn new() -> Self {
        GoldElite { mem: RefCell::new(HashMap::new()) }
    }
}

fn envi(name: &str, d: i32) -> i32 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(d)
}
fn env_spec(name: &str, d: (i32, i32, i32, i32)) -> (i32, i32, i32, i32) {
    if let Ok(s) = std::env::var(name) {
        let p: Vec<i32> = s.split(',').filter_map(|x| x.trim().parse().ok()).collect();
        if p.len() == 4 {
            return (p[0], p[1], p[2], p[3]);
        }
    }
    d
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

fn fruit_ty(t: &str) -> Option<usize> {
    match t {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}

impl Strategy for GoldElite {
    fn name(&self) -> &str {
        "goldelite"
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

        // ── training: exactly ONE chopper, then stop at GE_MAX trolls ───────────
        let spec = env_spec("GE_SPEC", (2, 2, 0, 2));
        let max_trolls = envi("GE_MAX", 2);
        let want_chopper = n < max_trolls && !my.iter().any(|u| u.chop >= 2);
        let cost = training_cost(n, spec);
        let train_now = want_chopper && afford(inv, &cost, have_iron);
        // iron-gated: fruit is ready but we still lack the iron for the chopper.
        let need_iron =
            have_iron && want_chopper && inv[IRON] < cost[IRON] && afford_fruit(inv, &cost);
        // which fruit types still block the chopper (funding targets)
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];

        // ── farm config ─────────────────────────────────────────────────────────
        let farm_r = envi("GE_FARM_R", 3);
        let farm_cap = envi("GE_FARM_MAX", 12) as usize;
        let fell_size = envi("GE_FELL_SIZE", 2);
        let chop_r = envi("GE_CHOP_R", 99); // max manh(tree, shack) the chopper roams
        let liq_t = envi("GE_LIQ_T", 34); // last turns: fell anything reachable
        let starter_chop = envi("GE_STARTER_CHOP", 1) == 1;
        let liquidation = turns_rem <= liq_t;
        let base_trees = game.plants.iter().filter(|p| manh(p.pos(), shack) <= farm_r).count();

        // own-half + reachable + not reserved fellable trees, with fell time
        let own_half = |p: &crate::game::state::Plant| {
            liquidation || manh(p.pos(), shack) <= manh(p.pos(), opp)
        };
        let within_roam =
            |p: &crate::game::state::Plant| liquidation || manh(p.pos(), shack) <= chop_r;

        let mut mem = self.mem.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();

        // nearest walkable drop cell -> DROP if adjacent else MOVE toward it
        let bank_cmd = |u: &Unit, d: &HashMap<Cell, i32>| -> String {
            if manh(u.pos(), shack) == 1 {
                format!("DROP {}", u.id)
            } else {
                let drop_cell = ortho(shack)
                    .into_iter()
                    .filter(|c| game.walkable.contains(c))
                    .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                    .unwrap_or(shack);
                format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1)
            }
        };
        let park_cmd = |u: &Unit, d: &HashMap<Cell, i32>| -> String {
            let park = ortho(shack)
                .into_iter()
                .filter(|c| game.walkable.contains(c))
                .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                .unwrap_or(shack);
            format!("MOVE {} {} {}", u.id, park.0, park.1)
        };

        for u in &my {
            let d = bfs(&game.walkable, u.pos());
            let is_chopper = u.chop >= 2;

            // endgame banking (bank a carried load in time to score it)
            if u.total() > 0 {
                let d_home = ortho(shack)
                    .iter()
                    .filter(|c| game.walkable.contains(*c))
                    .filter_map(|c| d.get(c))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let eta = (d_home + u.ms - 1) / u.ms.max(1) + 1;
                if turns_rem <= eta + 1 {
                    cmd_by_id.insert(u.id, bank_cmd(u, &d));
                    continue;
                }
            }

            // nearest fellable tree (size>=fell_size, own-half, in roam range)
            let nearest_fell = |free_needed: bool| -> Option<Cell> {
                if free_needed && u.free() == 0 {
                    return None;
                }
                game.plants
                    .iter()
                    .filter(|p| p.size >= if liquidation { 1 } else { fell_size })
                    .filter(|p| own_half(p) && within_roam(p))
                    .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                    .min_by_key(|p| {
                        // prefer close + fast-to-fell (banana health 4 << apple health 20)
                        let steps = (d[&p.pos()] + u.ms - 1) / u.ms.max(1);
                        let chop_t = (p.health + u.chop.max(1) - 1) / u.chop.max(1);
                        steps + chop_t
                    })
                    .map(|p| p.pos())
            };

            // ── CHOPPER: perma-fell local trees, bank when full ─────────────────
            if is_chopper {
                if u.free() == 0 {
                    cmd_by_id.insert(u.id, bank_cmd(u, &d));
                    continue;
                }
                // standing on a fellable tree -> chop
                if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                    if u.chop > 0 && p.size >= if liquidation { 1 } else { fell_size } {
                        cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                        reserved.insert(u.pos());
                        continue;
                    }
                }
                if let Some(tc) = nearest_fell(false) {
                    reserved.insert(tc);
                    mem.insert(u.id, tc);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                    continue;
                }
                // nothing to fell: bank a partial load, else idle near base
                cmd_by_id.insert(u.id, if u.total() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) });
                continue;
            }

            // ── STARTER (1,1,1,1): funder early, banana printer after ───────────
            // free base cell to plant on (prefer water-adjacent: banana cd 6->4)
            let free_base = |water: bool| -> Option<Cell> {
                game.walkable
                    .iter()
                    .filter(|c| manh(**c, shack) <= farm_r && d.contains_key(*c))
                    .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                    .filter(|c| !water || game.water.iter().any(|w| manh(*w, **c) == 1))
                    .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                    .filter(|c| !reserved.contains(*c))
                    .min_by_key(|c| d[*c])
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
            if u.free() == 0 {
                cmd_by_id.insert(u.id, bank_cmd(u, &d));
                continue;
            }

            // 3) standing on a ripe fruit tree we want -> harvest
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if p.fruits > 0 && u.hp > 0 && u.free() > 0 {
                    let ty = fruit_ty(&p.plant_type);
                    let want = if want_chopper {
                        ty.map_or(false, |t| t < 3 && need_fund[t])
                    } else {
                        // post-funding: only harvest seeds we replant (banana/water apple)
                        p.plant_type == "BANANA"
                            || (p.plant_type == "APPLE"
                                && game.water.iter().any(|w| manh(*w, p.pos()) == 1))
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
                if need_iron && u.chop > 0 {
                    if game.iron.iter().any(|ic| manh(u.pos(), *ic) == 1) {
                        cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                        continue;
                    }
                    if let Some(c) = game
                        .iron
                        .iter()
                        .flat_map(|ic| ortho(*ic))
                        .filter(|c| d.contains_key(c) && !reserved.contains(c))
                        .min_by_key(|c| d[c])
                    {
                        reserved.insert(c);
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                        continue;
                    }
                }
                // nearest ripe deficit fruit
                let target = game
                    .plants
                    .iter()
                    .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                    .filter(|p| fruit_ty(&p.plant_type).map_or(false, |t| t < 3 && need_fund[t]))
                    .min_by_key(|p| d[&p.pos()])
                    .map(|p| p.pos());
                if let Some(tc) = target {
                    reserved.insert(tc);
                    mem.insert(u.id, tc);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                    continue;
                }
                // no deficit fruit reachable — fall through to the printer so the
                // troll never stalls (it pre-seeds the banana farm meanwhile).
            }

            // 5) BANANA PRINTER: keep the farm stocked with bananas
            if base_trees < farm_cap {
                // pick a banked banana at the shack (fastest seed cycle)
                if manh(u.pos(), shack) == 1 && inv[BANANA] > 0 && u.free() > 0 {
                    cmd_by_id.insert(u.id, format!("PICK {} BANANA", u.id));
                    continue;
                }
                if inv[BANANA] > 0 {
                    // go to a shack-adjacent cell to PICK
                    cmd_by_id.insert(u.id, park_cmd(u, &d));
                    continue;
                }
                // no banked seeds: harvest a native banana (or water-apple) tree
                let seed_tree = game
                    .plants
                    .iter()
                    .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                    .filter(|p| {
                        p.plant_type == "BANANA"
                            || (p.plant_type == "APPLE"
                                && game.water.iter().any(|w| manh(*w, p.pos()) == 1))
                    })
                    .min_by_key(|p| d[&p.pos()])
                    .map(|p| p.pos());
                if let Some(tc) = seed_tree {
                    reserved.insert(tc);
                    mem.insert(u.id, tc);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                    continue;
                }
            }

            // 6) farm full / no seeds: help chop (chop1), else park at base
            if starter_chop && u.chop > 0 {
                if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
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
            cmd_by_id.insert(u.id, if u.total() > 0 { bank_cmd(u, &d) } else { park_cmd(u, &d) });
        }

        let mut actions: Vec<String> = Vec::new();
        let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
        ids.sort();
        for id in ids {
            actions.push(cmd_by_id[&id].clone());
        }

        if train_now
            && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT
            && !my.iter().any(|u| u.pos() == shack)
        {
            actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }

        if actions.is_empty() {
            actions.push("WAIT".into());
        }
        actions
    }
}
