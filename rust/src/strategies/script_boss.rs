//! The REAL arena Boss 4, scripted from a full-game DEBUG dump (cgauto/
//! last_console.txt, real Silver game vs v0.9.8): NOT the greedy-expansion
//! `silver_boss` model. The real script observed turn-by-turn:
//!   t1   PICK LEMON + try TRAIN (1,1,1,2)  (train lands t2)
//!   t2-5 starter walks a shack-adjacent cell and PLANTs a base LEMON orchard
//!   t2+  starter MINEs iron until the big chopper's iron is covered, then
//!        both trolls shuttle-harvest, hoarding LEMON toward 18
//!   ~t150 TRAIN (2,4,2,2)  (all savings spent: 6 plum / 18 lemon / 6 apple / 6 iron)
//!   t150+ the cc4 chopper CHOPs every single turn (fells for 4 wood = 16 pts,
//!        raiding trees all the way to the foe's shack); wood was 0 before ~t190.
//!   NO further training ever (banked 23 lemon unspent by t300). 3 trolls total.
//! So the real boss = slow 2-troll opening, one mid-game power spike, then a
//! relentless late wood engine. The `silver_boss` model (4 trolls, 2 cheap fast
//! choppers, early wood pressure) has a different SHAPE; tuning past ~78% vs it
//! overfits (v1.0.4: 90.5% sim / 33% real). This script is the second sparring
//! partner: robust changes must hold up vs BOTH models.
//!
//! Measured from the same dump (max/avg BFS-ish manhattan from own shack over
//! 300 turns): starter 5/2.0, util troll 15/4.7, cc4 chopper 16/9.1. So the
//! boss's HARVEST economy is LOCAL: the starter never leaves radius 5; the util
//! troll prefers local trees and only ranges out when nothing ripe is near.
//! Modelling that locality is what brings the anchor win rates in line.
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, IRON, LEMON};
use crate::game::state::{Cell, GameState, Unit};

const UTIL_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 2);
const BIG_SPEC: (i32, i32, i32, i32) = (2, 4, 2, 2);
const MAX_ORCHARD: usize = 2; // base LEMON orchard (funds the cc4's lemon 18)
const LOCAL_R: i32 = 5; // observed harvest radius around the boss shack

#[derive(Clone)]
pub struct ScriptBoss {
    mem: RefCell<HashMap<i32, Cell>>, // sticky per-harvester targets; reset at turn 1
}

impl ScriptBoss {
    pub fn new() -> Self {
        ScriptBoss {
            mem: RefCell::new(HashMap::new()),
        }
    }
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

impl Strategy for ScriptBoss {
    fn name(&self) -> &str {
        "scriptboss"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.mem.borrow_mut().clear();
        }
        let shack = game.shacks[player];
        let opp = game.shacks[1 - player];
        let inv = &game.inventories[player];
        let have_iron = !game.iron.is_empty();

        let mut my: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        let big_alive = my.iter().any(|u| u.cc >= 4 && u.chop >= 2);
        let big_cost = training_cost(2, BIG_SPEC); // trained as the 3rd troll (n=2)

        // ── the fixed build order: (1,1,1,2) as 2nd troll, (2,4,2,2) as 3rd, then stop
        let train_now: Option<(i32, i32, i32, i32)> = if n == 1 {
            afford(inv, &training_cost(n, UTIL_SPEC), have_iron).then_some(UTIL_SPEC)
        } else if n == 2 && !big_alive {
            afford(inv, &training_cost(n, BIG_SPEC), have_iron).then_some(BIG_SPEC)
        } else {
            None
        };

        // While saving for the big chopper: starter mines until its iron is banked,
        // harvesters hoard the scarcest missing cost resource (in practice LEMON 18).
        let saving = !big_alive && n >= 1;
        let need_iron = saving && have_iron && inv[IRON] < big_cost[IRON];
        let need_ty: Option<&str> = if saving {
            let deficit = |i: usize| (big_cost[i] - inv[i]).max(0);
            let idx = (0..3usize).max_by_key(|&i| deficit(i)).unwrap();
            (deficit(idx) > 0).then(|| ["PLUM", "LEMON", "APPLE"][idx])
        } else {
            None
        };

        let starter_id = my.first().map(|u| u.id);
        let orchard: usize = game
            .plants
            .iter()
            .filter(|p| p.plant_type == "LEMON" && manh(p.pos(), shack) <= 3)
            .count();

        let mut mem = self.mem.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
        let mut actions: Vec<String> = Vec::new();

        for u in &my {
            let is_big = u.cc >= 4 && u.chop >= 2;
            let is_starter = Some(u.id) == starter_id && !is_big;
            let d = bfs(&game.walkable, u.pos());
            let planting = is_starter && orchard < MAX_ORCHARD && game.turn <= 60;

            // ── base LEMON orchard: pick a lemon, walk to a free base cell, plant it
            if planting && u.carry[LEMON] > 0 {
                let on_plant = game.plants.iter().any(|p| p.pos() == u.pos());
                if !on_plant && game.walkable.contains(&u.pos()) && manh(u.pos(), shack) <= 2 {
                    cmd_by_id.insert(u.id, format!("PLANT {} LEMON", u.id));
                    continue;
                }
                if let Some(c) = game
                    .walkable
                    .iter()
                    .filter(|c| {
                        manh(**c, shack) <= 2 && !game.plants.iter().any(|p| p.pos() == **c)
                    })
                    .filter(|c| d.contains_key(*c))
                    .min_by_key(|c| (d[*c], **c))
                {
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                    continue;
                }
            }
            if planting && manh(u.pos(), shack) == 1 && inv[LEMON] > 0 && u.free() > 0 {
                cmd_by_id.insert(u.id, format!("PICK {} LEMON", u.id));
                continue;
            }

            // Full -> bank at the shack.
            if u.free() == 0 {
                mem.remove(&u.id);
                if manh(u.pos(), shack) == 1 {
                    cmd_by_id.insert(u.id, format!("DROP {}", u.id));
                } else {
                    let drop_cell = ortho(shack)
                        .into_iter()
                        .filter(|c| game.walkable.contains(c))
                        .min_by_key(|c| (d.get(c).copied().unwrap_or(1 << 30), *c))
                        .unwrap_or(shack);
                    cmd_by_id.insert(
                        u.id,
                        format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1),
                    );
                }
                continue;
            }

            // On a tree: the big chopper fells it; anyone else grabs ripe fruit.
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if is_big {
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

            // Starter mines the big chopper's iron while saving.
            if need_iron && is_starter && u.chop > 0 {
                if game.iron.iter().any(|ic| manh(u.pos(), *ic) == 1) {
                    cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                    continue;
                }
                if let Some(c) = game
                    .iron
                    .iter()
                    .flat_map(|ic| ortho(*ic))
                    .filter(|c| d.contains_key(c) && !reserved.contains(c))
                    .min_by_key(|c| (d[c], *c))
                {
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                    continue;
                }
            }

            let go: Option<Cell> = if is_big {
                // The observed cc4 engine: fell big trees, biased toward the FOE's
                // side (it raided trees beside our shack); same metric family as the
                // rest of the codebase.
                game.plants
                    .iter()
                    .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                    .min_by_key(|p| {
                        (
                            d[&p.pos()] + manh(p.pos(), opp) - 3 * p.size,
                            -p.size,
                            p.pos(),
                        )
                    })
                    .map(|p| p.pos())
                    .or_else(|| {
                        game.plants
                            .iter()
                            .filter(|p| {
                                p.fruits > 0
                                    && !reserved.contains(&p.pos())
                                    && d.contains_key(&p.pos())
                            })
                            .min_by_key(|p| (d[&p.pos()], p.pos()))
                            .map(|p| p.pos())
                    })
            } else {
                let sticky = mem.get(&u.id).copied().filter(|&c| {
                    game.plants.iter().any(|p| p.pos() == c && p.fruits > 0)
                        && !reserved.contains(&c)
                });
                let nearest_ripe = |ty: Option<&str>, local_only: bool| -> Option<Cell> {
                    game.plants
                        .iter()
                        .filter(|p| {
                            p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos())
                        })
                        .filter(|p| !local_only || manh(p.pos(), shack) <= LOCAL_R)
                        .filter(|p| ty.map_or(true, |t| p.plant_type == t))
                        .min_by_key(|p| (d[&p.pos()], p.pos()))
                        .map(|p| p.pos())
                };
                // Locality (observed): the starter farms ONLY its base patch; the util
                // troll prefers local trees and ranges out only when none are ripe.
                if is_starter {
                    sticky
                        .or_else(|| nearest_ripe(need_ty, true))
                        .or_else(|| nearest_ripe(None, true))
                } else {
                    sticky
                        .or_else(|| nearest_ripe(need_ty, true))
                        .or_else(|| nearest_ripe(None, true))
                        .or_else(|| nearest_ripe(need_ty, false))
                        .or_else(|| nearest_ripe(None, false))
                }
            };

            match go {
                Some(c) => {
                    reserved.insert(c);
                    if !is_big {
                        mem.insert(u.id, c);
                    }
                    cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, c.0, c.1));
                }
                None => {
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
            if !my.iter().any(|u| u.pos() == shack) {
                actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }

        if actions.is_empty() {
            actions.push("WAIT".into());
        }
        actions
    }
}
