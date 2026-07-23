//! PRINTER BOT — the top-Silver field archetype, decoded from arena replays
//! (aRi 275, tossy 256, QuickFix 248, Simulatorb 204; see silver-experiment-log
//! 2026-07-02): a small roster (~3 trolls) of chop-capable GENERALISTS that camp
//! their base half, continuously (re)plant BANANA (cd 6, health 2+size => 3 chops
//! at chop2) and fell the young trees for min(size,cc) wood — a self-sustaining
//! ~8 pts/cycle wood printer — harvesting ripe fruit between fells. No cross-map
//! denial treks. This is the architecture A/B partner for mybot: if it wins both
//! the head-to-head AND the boss matchups, it becomes the new main.
use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, BANANA, IRON, PLUM};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;

pub struct PrinterBot {
    mem: RefCell<HashMap<i32, Cell>>,
}

impl PrinterBot {
    pub fn new() -> Self {
        PrinterBot {
            mem: RefCell::new(HashMap::new()),
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

impl Strategy for PrinterBot {
    fn name(&self) -> &str {
        "printerbot"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.mem.borrow_mut().clear();
        }
        let shack = game.shacks[player];
        let inv = &game.inventories[player];
        let have_iron = !game.iron.is_empty();

        let mut my: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        my.sort_by_key(|u| u.id);
        let n = my.len() as i32;

        // Two hybrid generalists on top of the starter (aRi's observed build:
        // (2,2,2,1) early — chop1 is iron-cheap — then (2,2,0,2)). If the first
        // hybrid still isn't affordable by t40 (weak start), settle for a cheap
        // harvester so the roster never stalls at 1 troll.
        let spec1 = env_spec("PB_SPEC1", (2, 2, 2, 1));
        let spec2 = env_spec("PB_SPEC2", (2, 2, 0, 2));
        let max_trolls = envi("PB_MAX", 3);
        let want = if n == 1 {
            Some(spec1)
        } else if n == 2 {
            Some(spec2)
        } else {
            None
        };
        let train_now = want
            .filter(|_| (n as usize) < max_trolls as usize)
            .filter(|s| afford(inv, &training_cost(n, *s), have_iron))
            .or_else(|| {
                (n == 1
                    && game.turn > envi("PB_FALLBACK_T", 40)
                    && afford(inv, &training_cost(n, (1, 1, 1, 0)), have_iron))
                .then_some((1, 1, 1, 0))
            });
        let need_iron = have_iron
            && want.map_or(false, |s| {
                inv[IRON] < training_cost(n, s)[IRON] && afford_fruit(inv, &training_cost(n, s))
            });

        let farm_r = envi("PB_FARM_R", 3);
        let farm_cap = envi("PB_FARM_MAX", 6) as usize;
        let base_trees = game
            .plants
            .iter()
            .filter(|p| manh(p.pos(), shack) <= farm_r)
            .count();

        let mut mem = self.mem.borrow_mut();
        let mut reserved: HashSet<Cell> = HashSet::new();
        let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
        let mut actions: Vec<String> = Vec::new();

        for u in &my {
            let d = bfs(&game.walkable, u.pos());

            // Endgame banking (same rule as mybot).
            if u.total() > 0 {
                let turns_rem = TOTAL_TURNS - game.turn + 1;
                let d_home = ortho(shack)
                    .iter()
                    .filter(|c| game.walkable.contains(*c))
                    .filter_map(|c| d.get(c))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let eta = (d_home + u.ms - 1) / u.ms + 1;
                if turns_rem <= eta + 1 {
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
            }

            // Print: carrying banana in the window -> plant it on a base cell.
            let window = game.turn >= envi("PB_WF_START", 5) && game.turn <= envi("PB_WF_END", 285);
            if window && base_trees < farm_cap && u.carry[BANANA] > 0 {
                let free_base = |water: bool| {
                    game.walkable
                        .iter()
                        .filter(|c| manh(**c, shack) <= farm_r && d.contains_key(*c))
                        .filter(|c| !game.plants.iter().any(|p| p.pos() == **c))
                        .filter(|c| !water || game.water.iter().any(|w| manh(*w, **c) == 1))
                        .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
                        .min_by_key(|c| (d[*c], **c))
                        .copied()
                };
                if let Some(tc) = free_base(true).or_else(|| free_base(false)) {
                    if u.pos() == tc {
                        cmd_by_id.insert(u.id, format!("PLANT {} BANANA", u.id));
                    } else {
                        cmd_by_id.insert(u.id, format!("MOVE {} {} {}", u.id, tc.0, tc.1));
                    }
                    continue;
                }
            }

            // Full -> bank.
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

            // On a tree: fell ready farm trees / harvest ripe fruit.
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                let ready_farm =
                    manh(p.pos(), shack) <= farm_r && p.size >= envi("PB_FELL_SIZE", 2);
                if u.chop > 0 && (ready_farm || p.fruits == 0 && p.size >= 2) {
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

            // Mine iron when it's the binding constraint.
            if need_iron && u.chop > 0 && game.iron.iter().any(|ic| manh(u.pos(), *ic) == 1) {
                cmd_by_id.insert(u.id, format!("MINE {}", u.id));
                continue;
            }

            // Targets, in order: ready farm tree to fell -> nearest ripe fruit ->
            // pick banana seed at shack -> iron -> idle at base.
            let ready_farm_target = (u.chop > 0)
                .then(|| {
                    game.plants
                        .iter()
                        .filter(|p| {
                            manh(p.pos(), shack) <= farm_r && p.size >= envi("PB_FELL_SIZE", 2)
                        })
                        .filter(|p| d.contains_key(&p.pos()) && !reserved.contains(&p.pos()))
                        .min_by_key(|p| (d[&p.pos()], p.pos()))
                        .map(|p| p.pos())
                })
                .flatten();
            let sticky = mem.get(&u.id).copied().filter(|&c| {
                game.plants.iter().any(|p| p.pos() == c && p.fruits > 0) && !reserved.contains(&c)
            });
            let nearest_ripe = || {
                game.plants
                    .iter()
                    .filter(|p| {
                        p.fruits > 0 && !reserved.contains(&p.pos()) && d.contains_key(&p.pos())
                    })
                    .min_by_key(|p| (d[&p.pos()], p.pos()))
                    .map(|p| p.pos())
            };
            let iron_target = need_iron
                .then(|| {
                    game.iron
                        .iter()
                        .flat_map(|ic| ortho(*ic))
                        .filter(|c| d.contains_key(c) && !reserved.contains(c))
                        .min_by_key(|c| (d[c], *c))
                })
                .flatten();

            // PICK a banana seed when at the shack with print capacity.
            if window
                && base_trees < farm_cap
                && manh(u.pos(), shack) == 1
                && u.free() > 0
                && inv[BANANA] > 0
                && ready_farm_target.is_none()
                && sticky.is_none()
            {
                cmd_by_id.insert(u.id, format!("PICK {} BANANA", u.id));
                continue;
            }

            let go = ready_farm_target
                .or(sticky)
                .or_else(nearest_ripe)
                .or(iron_target);
            match go {
                Some(c) => {
                    reserved.insert(c);
                    mem.insert(u.id, c);
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
            if TOTAL_TURNS - game.turn > MIN_TURNS_LEFT && !my.iter().any(|u| u.pos() == shack) {
                actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }

        if actions.is_empty() {
            actions.push("WAIT".into());
        }
        actions
    }
}
