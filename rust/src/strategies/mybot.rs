//! Faithful model of the real arena "Boss 4" (the Silver->Gold gate). Verified
//! from real games: a MIXED bot, ~3-4 trolls, that WINS ON WOOD. Its engine is one
//! dominant (movementSpeed 2, carryCapacity 4, harvestPower 2, chopPower 2) chopper
//! that fells trees for up to 4 wood = 16 pts (WOOD=4pt, fruit=1pt). It also runs
//! harvesters, PLANTs a small base PLUM orchard early (plum funds movementSpeed:
//! every troll costs n+ms^2 plum), and MINEs iron (chopPower costs iron: n+chop^2).
//! It scores ~150-283 by map, dominating on wood while denying the foe's fruit by
//! felling trees. (The old `boss_real` -- a weak 2-troll pure farmer -- was WRONG.)
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{plant_cooldown, training_cost, water_boost, IRON, PLUM, LEMON, APPLE};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;
const MAX_TROLLS: usize = 4;
const MAX_ORCHARD: usize = 2; // base plum orchard size

// The real Boss 4: a MIXED bot that wins on wood. We expand GREEDILY (train the
// cheapest affordable troll every turn, like a gatherer) toward ~4 trolls, jumping the
// queue to build TWO cheap choppers as soon as affordable. Result: high fruit (2 self-
// funding harvesters) AND high wood + denial (2 choppers felling trees, starving the
// foe's fruit) -- a balanced ~138pt bot that beats pure harvesters decisively.
// WINNING config (beats silverboss ~68% over 500 games). vs the boss we use FAST
// (ms2) choppers that win the race to contested trees, and harvesters that grab the
// NEAREST ripe fruit for max throughput (greedy expansion already funds training, so
// we don't need scarce-resource-first harvesting).
// hp0 (was hp1): saves n+1 APPLE per chopper; the only loss is a rarely-reachable
// fruit-harvest fallback. Confirmed on BOTH boss models at 1000 seeds (2026-07-02):
// scriptboss 59.8→60.9% (margin +14.7→+18.2), silverboss 77.5→78.4% (+24.1→+26.9).
const CHOPPER_SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2);
const N_CHOPPERS: i32 = 2;
const HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const HARVESTER: (i32, i32, i32, i32) = (1, 2, 2, 0);

pub struct MyBot {
    mem: RefCell<HashMap<i32, Cell>>, // sticky per-harvester targets; reset at turn 1
}

impl MyBot {
    pub fn new() -> Self {
        MyBot { mem: RefCell::new(HashMap::new()) }
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
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}
fn afford_fruit(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}

impl Strategy for MyBot {
    fn name(&self) -> &str {
        "mybot"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.mem.borrow_mut().clear();
        }
        let shack = game.shacks[player];
        let inv = &game.inventories[player];
        let have_iron = !game.iron.is_empty();

        let mut my: Vec<&Unit> = game.units.iter().filter(|u| u.player as usize == player).collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        // IN-GAME ADAPTATION (MB_ADAPT_ECON) — TESTED, WORSE (77%->65%); default OFF.
        // Idea: when behind on troll count past the opening, switch choppers to local
        // felling (dw=0) to recover the ramp. It backfires because "fewer trolls than the
        // boss" is our NORMAL winning state (we win via denial with fewer trolls), so the
        // trigger fires on maps we'd win and kills the denial edge. Kept as a documented
        // dead-end so it isn't retried. DW=3 denial is load-bearing; do not gate it on this.
        let opp_n = game.units.iter().filter(|u| u.player as usize != player).count() as i32;
        let econ_mode = envi("MB_ADAPT_ECON", 0) == 1
            && game.turn > envi("MB_ECON_TURN", 25)
            && opp_n > n;

        // ── training plan ────────────────────────────────────────────────────
        // Greedy expansion: build the one chopper as soon as affordable (jumping the
        // queue), else the cheapest affordable harvester -- so the economy keeps growing
        // toward ~4 trolls while we wait for the chopper's resources.
        let chop_spec = env_spec("MYBOT_CHOP", CHOPPER_SPEC);
        // Map-adaptive chopper count: when the shacks are far apart, denial-felling
        // wastes travel, so lean on local harvesting (fewer choppers); when close and
        // contested, field more choppers to win the wood/denial race.
        let nchop = if envi("MYBOT_ADAPT", 0) == 1 {
            let sd = manh(shack, game.shacks[1 - player]);
            if sd <= envi("MYBOT_SDLO", 9) { 3 } else if sd >= envi("MYBOT_SDHI", 18) { 1 } else { 2 }
        } else {
            envi("MYBOT_NCHOP", N_CHOPPERS)
        };
        // MB_CHOP_MIN_N: build cheap GATHERERS first (fast fruit+iron economy), and
        // only start wanting a chopper once we have this many trolls -- delaying wood
        // for a stronger early economy (user hypothesis: gather early, chop late).
        let want_chopper = (my.iter().filter(|u| u.chop >= 2).count() as i32) < nchop
            && n >= envi("MB_CHOP_MIN_N", 1);
        let train_now: Option<(i32, i32, i32, i32)> = if want_chopper
            && afford(inv, &training_cost(n, chop_spec), have_iron)
        {
            Some(chop_spec)
        } else {
            HARVESTERS.iter().copied().find(|&s| afford(inv, &training_cost(n, s), have_iron))
        };
        // Mine iron whenever it's the binding constraint for the NEXT troll we'd train
        // (chopper if wanted, else cheapest harvester whose fruit we can already cover).
        // Old code only mined for the chopper, so after building it we stopped mining and
        // got IRON-GATED at 2-3 trolls on low-iron maps (a systematic both-seat blowout).
        // MB_MINE_ALL=0 restores the old chopper-only behavior for A/B.
        let need_iron = if envi("MB_MINE_ALL", 0) == 1 {
            let next = if want_chopper {
                Some(chop_spec)
            } else {
                HARVESTERS.iter().copied().find(|&s| afford_fruit(inv, &training_cost(n, s)))
            };
            have_iron
                && (n as usize) < envi("MYBOT_MAX", MAX_TROLLS as i32) as usize
                && match next {
                    Some(s) => {
                        afford_fruit(inv, &training_cost(n, s))
                            && inv[IRON] < training_cost(n, s)[IRON]
                    }
                    None => false,
                }
        } else {
            have_iron
                && want_chopper
                && inv[IRON] < training_cost(n, chop_spec)[IRON]
                && afford_fruit(inv, &training_cost(n, chop_spec))
        };

        // Roles: every chop>=2 troll is a chopper (fells wood). If none exists yet, the
        // starter (chop>=1, best cc) bootstraps the wood/iron economy.
        let has_real_chopper = my.iter().any(|u| u.chop >= 2);
        let bootstrap_id: Option<i32> = if has_real_chopper {
            None
        } else {
            my.iter().filter(|u| u.chop >= 1).max_by_key(|u| (u.cc, -u.id)).map(|u| u.id)
        };
        let is_chopper = |u: &Unit| -> bool { u.chop >= 2 || Some(u.id) == bootstrap_id };

        let orchard: usize = game
            .plants
            .iter()
            .filter(|p| p.plant_type == "PLUM" && manh(p.pos(), shack) <= 3)
            .count();

        // scarce training resource drives harvester targeting (plum/lemon/apple)
        let need_idx = (0..3usize).min_by_key(|&i| inv[i]).unwrap();
        let need_ty = ["PLUM", "LEMON", "APPLE"][need_idx];

        // DEFICIT CHASE (MB_DEFICIT) — TESTED, NET-NEGATIVE; default OFF (dead-end).
        // Root cause it targeted is real (e.g. seed 1: plum trees in far corners ->
        // nearest-ripe never banks PLUM -> stuck at 2 trolls with 78 useless fruit,
        // every troll costs n+ms^2 plum). But the cure loses more than it converts:
        // loose trigger -3.6pp script / -1.6pp silver; tight starved-only trigger
        // (below) still -1.2pp script / +0.4pp silver (1000 seeds, same-seed A/B).
        // Chasing a far-off type bleeds exactly the throughput the wood race needs.
        let deficit_ty: Option<&str> = if envi("MB_DEFICIT", 0) == 1
            && train_now.is_none()
            && (n as usize) < envi("MYBOT_MAX", MAX_TROLLS as i32) as usize
            && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT
        {
            // Fire only on the STARVATION signature: one type near zero while another
            // is rich. A loose trigger (any shortfall vs next cost) fires transiently
            // after every train and bleeds throughput everywhere: -3.6pp scriptboss /
            // -1.6pp silverboss at 1000 seeds. Starved-only targets the stuck maps.
            let cost_min = training_cost(n, HARVESTERS[HARVESTERS.len() - 1]);
            let rich = (0..3usize).map(|i| inv[i]).max().unwrap() >= envi("MB_DEF_HI", 10);
            (0..3usize)
                .filter(|&i| rich && inv[i] <= envi("MB_DEF_LOW", 1) && inv[i] < cost_min[i])
                .max_by_key(|&i| cost_min[i] - inv[i])
                .map(|i| ["PLUM", "LEMON", "APPLE"][i])
        } else {
            None
        };

        let mut mem = self.mem.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
        let mut actions: Vec<String> = Vec::new();
        if game.turn == 1 {
            actions.push("MSG Eat your vegetables!".into());
        }

        for u in &my {
            let is_chopper = is_chopper(u);
            let d = bfs(&game.walkable, u.pos());

            // ── ENDGAME BANKING (MB_ENDBANK, default on): carried items score ZERO
            // unless DROPped at the shack by the final turn. When the remaining turns
            // barely cover the walk home + the DROP, abandon whatever we're doing and
            // bank. Without this, every troll strands up to cc-1 items at t=300 (a
            // chopper's stranded wood = 4 pts each) — pure lost points in close games.
            if envi("MB_ENDBANK", 1) == 1 && u.total() > 0 {
                let turns_rem = TOTAL_TURNS - game.turn + 1; // incl. this turn
                let d_home = ortho(shack)
                    .iter()
                    .filter(|c| game.walkable.contains(*c))
                    .filter_map(|c| d.get(c))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let eta = (d_home + u.ms - 1) / u.ms + 1; // walk turns + the DROP turn
                if turns_rem <= eta + 1 {
                    if manh(u.pos(), shack) == 1 {
                        cmd_by_id.insert(u.id, format!("DROP {}", u.id));
                    } else {
                        let drop_cell = ortho(shack)
                            .into_iter()
                            .filter(|c| game.walkable.contains(c))
                            .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                            .unwrap_or(shack);
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1));
                    }
                    continue;
                }
            }

            // Full -> home; harvester seeds the plum orchard at base, else drops.
            if u.free() == 0 {
                mem.remove(&u.id);
                // MB_H2O: place orchard plums DELIBERATELY on a water-adjacent base cell
                // (plum cooldown 8 -> 3 beside water = ~2.7x fruit rate) instead of
                // planting wherever the returning harvester happens to stand.
                if envi("MB_H2O", 1) == 1
                    && !is_chopper
                    && u.carry[PLUM] > 0
                    && orchard < envi("MB_ORCHARD", MAX_ORCHARD as i32) as usize
                {
                    let spot = game
                        .walkable
                        .iter()
                        .filter(|c| manh(**c, shack) <= 3 && d.contains_key(*c))
                        .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                        .filter(|c| game.water.iter().any(|w| manh(*w, **c) == 1))
                        .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                        .min_by_key(|c| d[*c]);
                    if let Some(&tc) = spot {
                        if u.pos() == tc {
                            cmd_by_id.insert(u.id, format!("PLANT {} PLUM", u.id));
                        } else {
                            cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                        }
                        continue;
                    }
                    // no water-adjacent base cell -> fall through to the old behavior
                }
                if manh(u.pos(), shack) == 1 {
                    let on_tree = game.plants.iter().any(|p| p.pos() == u.pos());
                    let base_trees = game.plants.iter().filter(|p| manh(p.pos(), shack) <= 3).count();
                    let plum_orchard =
                        orchard < envi("MB_ORCHARD", MAX_ORCHARD as i32) as usize && u.carry[PLUM] > 0;
                    // FRUIT->WOOD conversion (MB_WOODFARM): plant a seed on this empty base
                    // cell so it grows and the chopper later fells it for wood (1pt fruit ->
                    // up to 4*size pts). Prefer BANANA -- it can't fund training, so it's
                    // pure surplus. Only in a mid-game window so the tree has time to grow.
                    let woodfarm = envi("MB_WOODFARM", 0) == 1
                        && game.turn >= envi("MB_WF_START", 20)
                        && game.turn <= envi("MB_WF_END", 280)
                        && base_trees < envi("MB_WF_MAX", 6) as usize;
                    if !is_chopper && !on_tree && game.walkable.contains(&u.pos())
                        && (plum_orchard || woodfarm)
                    {
                        let ty = if plum_orchard {
                            "PLUM"
                        } else if u.carry[3] > 0 {
                            "BANANA"
                        } else {
                            match (0..4).filter(|&i| u.carry[i] > 0).max_by_key(|&i| u.carry[i]) {
                                Some(0) => "PLUM",
                                Some(1) => "LEMON",
                                Some(2) => "APPLE",
                                _ => "BANANA",
                            }
                        };
                        cmd_by_id.insert(u.id, format!("PLANT {} {}", u.id, ty));
                    } else {
                        cmd_by_id.insert(u.id, format!("DROP {}", u.id));
                    }
                } else {
                    // Head to the NEAREST walkable shack-adjacent DROP cell (not the shack
                    // center). Critical: a full troll standing ON the shack cell (e.g. the
                    // starter after mining turn-1 iron) would otherwise MOVE to its own cell
                    // forever and wedge the whole game (100% idle, stuck at 1 troll).
                    let drop_cell = ortho(shack)
                        .into_iter()
                        .filter(|c| game.walkable.contains(c))
                        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1));
                }
                continue;
            }

            // On a tree: chopper fells it (wood engine); harvester grabs the fruit.
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if is_chopper && u.chop > 0 {
                    cmd_by_id.insert(u.id, format!("CHOP {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
                if p.fruits > 0 && u.hp > 0 && u.free() > 0 {
                    cmd_by_id.insert(u.id, format!("HARVEST {}", u.id));
                    reserved.insert(u.pos());
                    continue;
                }
            }

            // Chopper mines iron when saving and adjacent to it.
            if need_iron && is_chopper && u.chop > 0
                && game.iron.iter().any(|ic| manh(u.pos(), *ic) == 1)
            {
                cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                continue;
            }

            let go: Option<Cell> = if is_chopper {
                // need iron? go to nearest reachable iron-adjacent cell first.
                let iron_cell = if need_iron {
                    game.iron
                        .iter()
                        .flat_map(|ic| ortho(*ic))
                        .filter(|c| d.contains_key(c) && !reserved.contains(c))
                        .min_by_key(|c| d[c])
                } else {
                    None
                };
                // Fell the best tree: close + big, with DENIAL weight toward the foe's
                // shack. Fall back to nearest ripe fruit so an idle chopper still banks
                // points (late game, when few trees remain).
                let opp = game.shacks[1 - player];
                // Economy mode: chop the NEAREST tree (no denial trek) to recover the ramp.
                let dw = if econ_mode { 0 } else { envi("MYBOT_DW", 3) };
                let wt = envi("MYBOT_WT", 0);
                // MB_FELLT: also charge the fell TIME (ceil(health/chop) turns a fell
                // actually costs — an APPLE s4 is 10 turns at chop2, a BANANA s4 just 3).
                let ft = envi("MB_FELLT", 0);
                // MB_LEMONW: extra denial pull toward LEMON trees — carry capacity costs
                // lemon (n+cc^2), so any chopper-heavy foe is lemon-gated (the real Boss 4
                // saves to lemon 18 for its (2,4,2,2); felling its lemons delays the spike).
                let lw = envi("MB_LEMONW", 0);
                iron_cell
                    .or_else(|| {
                        game.plants
                            .iter()
                            .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                            .min_by_key(|p| {
                                let fell = (p.health + u.chop.max(1) - 1) / u.chop.max(1);
                                let lemon = (p.plant_type == "LEMON") as i32;
                                (d[&p.pos()] + dw * manh(p.pos(), opp) - wt * p.size + ft * fell
                                    - lw * lemon, -p.size)
                            })
                            .map(|p| p.pos())
                    })
                    .or_else(|| {
                        if u.hp > 0 {
                            game.plants
                                .iter()
                                .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                                .min_by_key(|p| d[&p.pos()])
                                .map(|p| p.pos())
                        } else {
                            None
                        }
                    })
            } else {
                let sticky = mem.get(&u.id).copied().filter(|&c| {
                    game.plants.iter().any(|p| p.pos() == c && p.fruits > 0) && !reserved.contains(&c)
                });
                let nearest_ripe = |ty: Option<&str>| -> Option<Cell> {
                    game.plants
                        .iter()
                        .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                        .filter(|p| ty.map_or(true, |t| p.plant_type == t))
                        .min_by_key(|p| d[&p.pos()])
                        .map(|p| p.pos())
                };
                // When NOTHING is ripe, don't idle at base: pre-position at the tree
                // whose first fruit lands soonest relative to our arrival (minimize
                // max(travel, time-to-ripe)). Uses only validated growth mechanics
                // (cooldown + water boost), no boss assumptions. MB_RIPE=0 disables.
                let anticipate = || -> Option<Cell> {
                    if envi("MB_RIPE", 1) == 0 {
                        return None;
                    }
                    game.plants
                        .iter()
                        .filter(|p| !reserved.contains(&p.pos()) && d.contains_key(&p.pos()))
                        .filter_map(|p| {
                            let mut cd = plant_cooldown(&p.plant_type);
                            if game.water.iter().any(|w| manh(*w, p.pos()) == 1) {
                                cd -= water_boost(&p.plant_type);
                            }
                            let cd = cd.max(1);
                            let steps = if p.size < 4 { 4 - p.size + 1 } else { 1 };
                            let ttr = p.cooldown + (steps - 1) * cd;
                            let arrive = (d[&p.pos()] + u.ms - 1) / u.ms.max(1);
                            (ttr <= 40).then(|| (arrive.max(ttr), d[&p.pos()], p.pos()))
                        })
                        .min()
                        .map(|(_, _, c)| c)
                };
                // HARV=1 (default): nearest ripe fruit for max throughput (but chase a
                // training-blocking deficit type first — see deficit_ty above). HARV=0:
                // scarce-resource-first (funds training, but slower fruit).
                if envi("MYBOT_HARV", 1) == 1 {
                    sticky
                        .or_else(|| deficit_ty.and_then(|t| nearest_ripe(Some(t))))
                        .or_else(|| nearest_ripe(None))
                        .or_else(anticipate)
                } else {
                    sticky
                        .or_else(|| nearest_ripe(Some(need_ty)))
                        .or_else(|| nearest_ripe(None))
                        .or_else(anticipate)
                }
            };

            match go {
                Some(c) => {
                    reserved.insert(c);
                    if !is_chopper {
                        mem.insert(u.id, c);
                    }
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                }
                None => {
                    // nothing to do: bank carry or idle at base
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, shack.0, shack.1));
                }
            }
        }

        let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
        ids.sort();
        for id in ids {
            actions.push(cmd_by_id[&id].clone());
        }

        if let Some(spec) = train_now {
            if (n as usize) < envi("MYBOT_MAX", MAX_TROLLS as i32) as usize
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
