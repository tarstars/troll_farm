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
use crate::game::engine::{training_cost, IRON, PLUM, LEMON, APPLE};
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
const CHOPPER_SPEC: (i32, i32, i32, i32) = (2, 2, 1, 2);
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
        // Mine iron only while we still lack a chopper and its fruit is (nearly) covered.
        let need_iron = have_iron
            && want_chopper
            && inv[IRON] < training_cost(n, chop_spec)[IRON]
            && afford_fruit(inv, &training_cost(n, chop_spec));

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

            // Full -> home; harvester seeds the plum orchard at base, else drops.
            if u.free() == 0 {
                mem.remove(&u.id);
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
                let dw = envi("MYBOT_DW", 3);
                let wt = envi("MYBOT_WT", 0);
                iron_cell
                    .or_else(|| {
                        game.plants
                            .iter()
                            .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                            .min_by_key(|p| (d[&p.pos()] + dw * manh(p.pos(), opp) - wt * p.size, -p.size))
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
                // HARV=1 (default): nearest ripe fruit for max throughput. HARV=0:
                // scarce-resource-first (funds training, but slower fruit).
                if envi("MYBOT_HARV", 1) == 1 {
                    sticky.or_else(|| nearest_ripe(None))
                } else {
                    sticky.or_else(|| nearest_ripe(Some(need_ty))).or_else(|| nearest_ripe(None))
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
