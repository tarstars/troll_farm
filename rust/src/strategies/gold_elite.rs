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
    // per-instance config (defaults read from env in new(); the hybrid()
    // constructor bakes the 3-troll denial build so it can be A/B'd in-process).
    max_trolls: i32,
    choppers: i32,               // how many chop>=2 trolls to train
    stagger: i32,                // earliest turn to train chopper #2+
    spec1: (i32, i32, i32, i32), // spec for chopper #1
    spec2: (i32, i32, i32, i32), // spec for chopper #2+
    planters: i32,               // extra CHEAP (1,1,1,1) planter trolls to boost farm supply
    hold_until: i32,             // choppers PLANT (don't fell) before this turn — accumulate phase
    farm_cap: usize,             // max standing farm trees (override GE_FARM_MAX)
    co_fell: bool,               // let multiple choppers pile on one tree (full-capture size-4)
    adaptive: bool, // pick economy by map density at turn 1 (dense=supply, sparse=lean)
    dense0: RefCell<i32>, // initial tree count (-1 = unset), for the adaptive decision
}

impl GoldElite {
    pub fn new() -> Self {
        GoldElite {
            mem: RefCell::new(HashMap::new()),
            max_trolls: envi("GE_MAX", 2),
            choppers: envi("GE_CHOPPERS", 1),
            stagger: envi("GE_STAGGER", 0),
            spec1: env_spec("GE_SPEC", (2, 2, 0, 2)),
            spec2: env_spec("GE_SPEC2", (2, 2, 0, 2)),
            planters: envi("GE_PLANTERS", 0),
            hold_until: envi("GE_HOLD_UNTIL", 0),
            farm_cap: envi("GE_FARM_MAX", 12) as usize,
            co_fell: false,
            adaptive: false,
            dense0: RefCell::new(-1),
        }
    }
    /// The 3-troll build decoded from kurigen: a staggered 2nd chopper that adds
    /// throughput AND denies the opponent's trees once our farm is drained.
    pub fn hybrid() -> Self {
        GoldElite {
            mem: RefCell::new(HashMap::new()),
            max_trolls: 3,
            choppers: 2,
            stagger: 60,
            spec1: (2, 2, 0, 2),
            spec2: (2, 2, 2, 2), // harvest-capable -> self-planting flex unit
            planters: 0,
            hold_until: 0,
            farm_cap: 12,
            co_fell: false,
            adaptive: false,
            dense0: RefCell::new(-1),
        }
    }
    /// The 180-WOOD Legend economy decoded from Tchoubidouwa123: build a big farm +
    /// multiple trolls early, bank ~0 wood (HOLD — all trolls plant), accumulate a
    /// huge mature forest, then MASS-HARVEST it late with high-capacity choppers.
    pub fn accumulate() -> Self {
        // DEDICATED GE_ACC_* env so the default goldelite baseline stays clean in sweeps
        GoldElite {
            mem: RefCell::new(HashMap::new()),
            max_trolls: envi("GE_ACC_MAX", 4),
            choppers: envi("GE_ACC_CHOP", 2),
            stagger: envi("GE_ACC_STAG", 30),
            spec1: env_spec("GE_ACC_SPEC1", (2, 2, 0, 2)),
            spec2: env_spec("GE_ACC_SPEC2", (2, 2, 0, 2)),
            planters: envi("GE_ACC_PLANT", 1), // +1 cheap (1,1,1,1) planter feeds the 2 choppers
            hold_until: envi("GE_ACC_HOLD", 0), // steady-state: planters keep the farm big enough
            farm_cap: envi("GE_ACC_CAP", 18) as usize,
            co_fell: false,
            adaptive: false,
            dense0: RefCell::new(-1),
        }
    }
    /// MAP-ADAPTIVE: on DENSE maps run the cheap-planter + hold supply economy
    /// (beats v1.4.5 53%); on SPARSE maps run the lean 2-troll v1.4.5 build.
    pub fn adaptive() -> Self {
        GoldElite {
            mem: RefCell::new(HashMap::new()),
            max_trolls: 4,
            choppers: 2,
            stagger: 30,
            spec1: (2, 2, 0, 2),
            spec2: (2, 2, 0, 2),
            planters: 1,
            hold_until: 100,
            farm_cap: 24,
            co_fell: false,
            adaptive: true,
            dense0: RefCell::new(-1),
        }
    }
}

fn envi(name: &str, d: i32) -> i32 {
    std::env::var(name)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(d)
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
    [
        (c.0, c.1 + 1),
        (c.0 + 1, c.1),
        (c.0, c.1 - 1),
        (c.0 - 1, c.1),
    ]
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
        if self.adaptive {
            return "goldelite_ad";
        }
        if self.planters > 0 || self.hold_until > 0 {
            return "goldelite_acc";
        }
        if self.choppers > 1 {
            "goldelite3"
        } else {
            "goldelite"
        }
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

        let mut my: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        // ── MAP-ADAPTIVE: choose the economy by initial tree density (turn 1) ───
        if self.adaptive && game.turn == 1 {
            *self.dense0.borrow_mut() = game.plants.len() as i32;
        }
        // dense map (>=12 trees) -> cheap-planter + hold supply economy (beats v1.4.5
        // on dense); sparse -> lean 2-troll v1.4.5 build (multi-troll starves on sparse).
        let (e_max, e_chop, e_plant, e_hold, e_cap): (i32, i32, i32, i32, usize) = if self.adaptive
        {
            if *self.dense0.borrow() >= 12 {
                (4, 2, 1, 100, 24)
            } else {
                (2, 1, 0, 0, 12)
            }
        } else {
            (
                self.max_trolls,
                self.choppers,
                self.planters,
                self.hold_until,
                self.farm_cap,
            )
        };

        // ── training: `choppers` choppers, staggered, then stop at max_trolls ────
        let spec = self.spec1; // chopper #1 spec
        let max_trolls = e_max;
        let want_choppers = e_chop;
        let n_choppers = my.iter().filter(|u| u.chop >= 2).count() as i32;
        // chopper #2+ waits until the economy is established (self.stagger)
        let stagger_ok = n_choppers == 0 || game.turn >= self.stagger;
        // extra CHEAP (1,1,1,1) planters boost farm SUPPLY so >1 chopper stays fed;
        // train them FIRST (cheap ~6 res), then the choppers.
        let n_planters_extra = (my.iter().filter(|u| u.chop < 2).count() as i32 - 1).max(0);
        let want_planter = n < max_trolls && n_planters_extra < e_plant;
        let want_chopper =
            !want_planter && n < max_trolls && n_choppers < want_choppers && stagger_ok;
        // planter=(1,1,1,1); chopper #1 uses spec; later choppers use spec2
        let train_spec = if want_planter {
            (1, 1, 1, 1)
        } else if n_choppers == 0 {
            spec
        } else {
            self.spec2
        };
        let want_train = want_planter || want_chopper;
        let cost = training_cost(n, train_spec);
        let train_now = want_train && afford(inv, &cost, have_iron);
        // iron-gated: fruit is ready but we still lack the iron for the next unit.
        let need_iron =
            have_iron && want_train && inv[IRON] < cost[IRON] && afford_fruit(inv, &cost);
        // which fruit types still block the next unit (funding targets)
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];

        // ── farm config ─────────────────────────────────────────────────────────
        let farm_r = envi("GE_FARM_R", 3);
        let farm_cap = e_cap;
        // ACCUMULATE PHASE: before hold_until, choppers PLANT instead of fell, so the
        // farm grows into a big mature forest that gets mass-harvested afterwards.
        let holding = game.turn < e_hold;
        let co_fell = self.co_fell; // allow >1 chopper on the same tree (full-capture)
        let fell_size = envi("GE_FELL_SIZE", 2);
        let chop_r = envi("GE_CHOP_R", 10); // max manh(tree, shack) the chopper roams
        let liq_t = envi("GE_LIQ_T", 34); // last turns: fell anything reachable
        let starter_chop = envi("GE_STARTER_CHOP", 1) == 1;
        let liquidation = turns_rem <= liq_t;
        let base_trees = game
            .plants
            .iter()
            .filter(|p| manh(p.pos(), shack) <= farm_r)
            .count();

        // ── SEED SUSTAINABILITY (arena deforestation fix) ───────────────────────
        // Trees only fruit at MAX_SIZE (4); felling farm bananas at size 2 means
        // they NEVER fruit, so the seed supply only drains -> the farm dies -> our
        // half deforests -> both trolls park (the decoded arena stall). Fix: keep
        // the K most-mature farm bananas as a permanent seed reserve the chopper
        // won't fell. They ripen, fruit, and the starter harvests their fruit for
        // seeds — a self-sustaining loop. GE_SEED_RESERVE=0 disables.
        let seed_reserve_k = envi("GE_SEED_RESERVE", 2) as usize;
        let farm_fell = envi("GE_FARM_FELL", 2); // fell threshold for NON-reserved farm bananas
        let mut seed_cells: HashSet<Cell> = HashSet::new();
        if seed_reserve_k > 0 && !liquidation {
            let mut fb: Vec<&crate::game::state::Plant> = game
                .plants
                .iter()
                .filter(|p| p.plant_type == "BANANA" && manh(p.pos(), shack) <= farm_r)
                .collect();
            // most mature first: size desc, fruits desc, then nearest shack (stable)
            fb.sort_by_key(|p| (-p.size, -p.fruits, manh(p.pos(), shack), p.pos()));
            for p in fb.into_iter().take(seed_reserve_k) {
                seed_cells.insert(p.pos());
            }
        }
        // is a plant currently fellable by the chopper (per-plant threshold)?
        let fell_ok = |p: &crate::game::state::Plant| -> bool {
            if seed_cells.contains(&p.pos()) {
                return false; // protected seed source
            }
            if liquidation {
                return p.size >= 1;
            }
            let farm_banana = p.plant_type == "BANANA" && manh(p.pos(), shack) <= farm_r;
            p.size >= if farm_banana { farm_fell } else { fell_size }
        };

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
            // A harvest-capable chopper (hp>0, e.g. the 2,2,2,2 hybrid) routes
            // through the flexible printer/chopper branch: it PLANTS bananas when
            // the farm is low (raising supply — the real bottleneck) and helps
            // CHOP when the farm is full. Pure choppers (hp==0) chop only.
            // During the accumulate/hold phase, choppers route through the flexible
            // planter branch (build the forest) instead of felling it.
            let is_chopper = u.chop >= 2 && u.hp == 0 && !holding;

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
                    .filter(|p| fell_ok(p))
                    .filter(|p| own_half(p) && within_roam(p))
                    .filter(|p| {
                        d.contains_key(&p.pos()) && (co_fell || !reserved.contains(&p.pos()))
                    })
                    .min_by_key(|p| {
                        let steps = (d[&p.pos()] + u.ms - 1) / u.ms.max(1);
                        let chop_t = (p.health + u.chop.max(1) - 1) / u.chop.max(1);
                        // harvest (co_fell): BIGGEST tree first so choppers converge and
                        // co-fell it (full-capture size-4); else prefer close+fast-to-fell.
                        if co_fell {
                            (-p.size, steps)
                        } else {
                            (0, steps + chop_t)
                        }
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
                    if u.chop > 0 && fell_ok(p) {
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
                // ANTI-STARVATION: farm empty -> fell nearest reachable tree (size>=1)
                // anywhere instead of idling (arena shutdown floor fix). GE_NOIDLE=0 off.
                if envi("GE_NOIDLE", 1) == 1 {
                    if let Some(tc) = game
                        .plants
                        .iter()
                        .filter(|p| {
                            p.size >= 1 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos())
                        })
                        .min_by_key(|p| {
                            let steps = (d[&p.pos()] + u.ms - 1) / u.ms.max(1);
                            let chop_t = (p.health + u.chop.max(1) - 1) / u.chop.max(1);
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
                // nothing to fell: bank a partial load, else idle near base
                cmd_by_id.insert(
                    u.id,
                    if u.total() > 0 {
                        bank_cmd(u, &d)
                    } else {
                        park_cmd(u, &d)
                    },
                );
                continue;
            }

            // ── STARTER (1,1,1,1): funder early, banana printer after ───────────
            // free base cell to plant on (prefer water-adjacent: banana cd 6->4)
            // Plant at the NEAREST free base cell, with water-adjacency only a mild
            // tiebreak (GE_WATER_W cells' worth), not a hard first pass. Water bananas
            // grow faster (cd 6->4) but trekking to water is the printer's biggest
            // travel sink — and travel is the arena's confirmed cost. Nearest-first
            // cuts the shack<->farm round-trip.
            let water_w = envi("GE_WATER_W", 2);
            let free_base = |_water: bool| -> Option<Cell> {
                game.walkable
                    .iter()
                    .filter(|c| manh(**c, shack) <= farm_r && d.contains_key(*c))
                    .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                    .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                    .filter(|c| !reserved.contains(*c))
                    .min_by_key(|c| {
                        let wet = game.water.iter().any(|w| manh(*w, **c) == 1);
                        d[*c] + if wet { 0 } else { water_w }
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
            if u.free() == 0 {
                cmd_by_id.insert(u.id, bank_cmd(u, &d));
                continue;
            }

            // 3) standing on a ripe fruit tree we want -> harvest
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if p.fruits > 0 && u.hp > 0 && u.free() > 0 {
                    let ty = fruit_ty(&p.plant_type);
                    let want = if want_train {
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

            // 4) FUNDING PHASE: mine iron / harvest deficit fruit for the next unit
            if want_train {
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
                    .filter(|p| {
                        p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos())
                    })
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
                    .filter(|p| {
                        p.fruits > 0 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos())
                    })
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
            //    (suppressed during the accumulate/hold phase — build, don't fell)
            if starter_chop && u.chop > 0 && !holding {
                if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
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
                // anti-starvation for the starter too: fell the nearest reachable
                // size>=1 tree anywhere (with free capacity) rather than parking idle.
                if envi("GE_NOIDLE", 1) == 1 && u.free() > 0 {
                    if let Some(tc) = game
                        .plants
                        .iter()
                        .filter(|p| {
                            p.size >= 1 && d.contains_key(&p.pos()) && !reserved.contains(&p.pos())
                        })
                        .min_by_key(|p| {
                            let steps = (d[&p.pos()] + u.ms - 1) / u.ms.max(1);
                            let chop_t = (p.health + u.chop.max(1) - 1) / u.chop.max(1);
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
                if u.total() > 0 {
                    bank_cmd(u, &d)
                } else {
                    park_cmd(u, &d)
                },
            );
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
            actions.push(format!(
                "TRAIN {} {} {} {}",
                train_spec.0, train_spec.1, train_spec.2, train_spec.3
            ));
        }

        if actions.is_empty() {
            actions.push("WAIT".into());
        }
        actions
    }
}
