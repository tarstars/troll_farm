//! Jobs layer (L2, R3c): per-troll decision cascade — who funds, mines, harvests,
//! plants, fells, banks, parks. Consumes the tactical Plan; produces one command per
//! troll (id → command). Bodies moved VERBATIM from decide_elite (plan fields re-bound
//! as same-named locals); equality enforced by the harness. This is the layer where the
//! future policy experiments (farm-supply invariant, dynamic starter role) live.
use super::tactics::Plan;
use super::*;
use std::collections::{HashMap, HashSet};

thread_local! {
    // GoldElite::mem — last sticky target cell per troll. Write-only (never read);
    // kept for a faithful 1:1 port. Reset at turn 1.
    static GE_MEM: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
}

/// Turn-1 reset of the sticky-target memory.
pub fn reset() {
    GE_MEM.with(|m| m.borrow_mut().clear());
}

pub fn assign_all(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let shack = plan.shack;
    let opp = plan.opp;
    let turns_rem = plan.turns_rem;
    let want_chopper = plan.want_chopper;
    let cost = plan.cost;
    let need_iron = plan.need_iron;
    let need_fund = plan.need_fund;
    let farm_r = plan.farm_r;
    let farm_cap = plan.farm_cap;
    let fell_size = plan.fell_size;
    let farm_fell = plan.farm_fell;
    let chop_r = plan.chop_r;
    let starter_chop = plan.starter_chop;
    let liquidation = plan.liquidation;
    let base_trees = plan.base_trees;
    let seed_cells = &plan.seed_cells;
    let inv = &state.my_inventory;
    // is a tree currently fellable by the chopper (per-tree threshold)?
    let fell_ok = |p: &Tree| -> bool {
        if seed_cells.contains(&p.pos()) {
            return false; // protected seed source
        }
        if liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA" && manhattan(p.pos(), shack) <= farm_r;
        p.size >= if farm_banana { farm_fell } else { fell_size }
    };

    // own-half + reachable + not reserved fellable trees, with fell time
    let own_half = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), opp);
    let within_roam = |p: &Tree| liquidation || manhattan(p.pos(), shack) <= chop_r;
    let mut reserved: HashSet<Cell> = HashSet::new();
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    // v1.20.0 MOTION: trolls heading to the camp (bank/park) claim DISTINCT shack-adjacent cells
    // so they don't converge on one cell and block each other (the #1 near-camp move-waste).
    let mut claimed_drop: HashSet<Cell> = HashSet::new();

    // bank/park via motion:: camp-cell claiming (R3b); thin wrappers keep call sites short.
    let bank_cmd = |u: &Troll, d: &HashMap<Cell, i32>, claimed: &mut HashSet<Cell>| -> String {
        motion::bank_cmd(state, shack, u, d, claimed)
    };
    let park_cmd = |u: &Troll, d: &HashMap<Cell, i32>, claimed: &mut HashSet<Cell>| -> String {
        motion::park_cmd(state, shack, u, d, claimed)
    };

    for u in my {
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
                cmd_by_id.insert(u.id, bank_cmd(u, &d, &mut claimed_drop));
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
                cmd_by_id.insert(u.id, bank_cmd(u, &d, &mut claimed_drop));
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
                if u.total_carried() > 0 { bank_cmd(u, &d, &mut claimed_drop) } else { park_cmd(u, &d, &mut claimed_drop) },
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
                    // (…, **c): total-order tiebreak — HashSet iteration order is random per
                    // process; equal-scored ties must not depend on it (R1 determinism).
                    (d[*c] + if wet { 0 } else { 2 }, **c)
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
            cmd_by_id.insert(u.id, bank_cmd(u, &d, &mut claimed_drop));
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
                    .min_by_key(|c| (d[c], *c)) // cell tiebreak: HashSet order is per-process random
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
                cmd_by_id.insert(u.id, park_cmd(u, &d, &mut claimed_drop));
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
            if u.total_carried() > 0 { bank_cmd(u, &d, &mut claimed_drop) } else { park_cmd(u, &d, &mut claimed_drop) },
        );
    }

    cmd_by_id
}
