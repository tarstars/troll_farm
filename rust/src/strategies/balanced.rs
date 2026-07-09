//! Balanced strategy (models the real ladder winners: Boss 4 / Rysiu22). Runs BOTH
//! economies at once via roles: a DEDICATED chopper mines iron then fells trees for
//! 4-pt wood every turn, while the other trolls harvest fruit; expand toward a
//! powerful (cc-4) chopper. This is the competent opponent the ladder needs --
//! gathering-only and naive-chopping both lose to it, matching the arena.
use std::collections::HashSet;

use super::{bank, dist, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::{GameState, Unit};

const IRON: usize = 4;

pub struct Balanced;

impl Strategy for Balanced {
    fn name(&self) -> &str {
        "balanced"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let shack = game.shacks[player];
        let mut mine: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        mine.sort_by_key(|u| u.id);
        let inv = &game.inventories[player];
        let n = mine.len() as i32;
        let have_real_chopper = mine.iter().any(|u| u.chop >= 2);
        // Dedicate ONE chopper to wood: the strongest chop troll (or, before we own
        // a real one, the chop-1 starter to bootstrap iron). Everyone else harvests.
        let chopper_id: Option<i32> = mine
            .iter()
            .filter(|u| u.chop >= if have_real_chopper { 2 } else { 1 })
            .max_by_key(|u| (u.chop, u.cc, -u.id))
            .map(|u| u.id);

        let mut cmds = Vec::new();
        let mut reserved: HashSet<(i32, i32)> = HashSet::new();
        for u in &mine {
            if Some(u.id) == chopper_id {
                // mine iron until we have a stockpile, then fell trees for wood
                if u.free() > 0
                    && inv[IRON] < 18
                    && game.iron.iter().any(|&c| dist(u.pos(), c) == 1)
                {
                    cmds.push(format!("MINE {}", u.id));
                    continue;
                }
                if u.total() >= u.cc {
                    cmds.push(bank(u.id, u.pos(), shack));
                    continue;
                }
                if game.plants.iter().any(|p| p.pos() == u.pos()) {
                    cmds.push(format!("CHOP {}", u.id));
                    continue;
                }
                match nearest_plant(game, u.pos(), false, &reserved) {
                    Some(tp) => {
                        reserved.insert(tp);
                        cmds.push(format!("MOVE {} {} {}", u.id, tp.0, tp.1));
                    }
                    None if u.total() > 0 => cmds.push(bank(u.id, u.pos(), shack)),
                    None => {}
                }
            } else {
                // harvester
                if u.free() > 0
                    && game
                        .plants
                        .iter()
                        .any(|p| p.pos() == u.pos() && p.fruits > 0)
                {
                    cmds.push(format!("HARVEST {}", u.id));
                    continue;
                }
                if u.total() >= u.cc {
                    cmds.push(bank(u.id, u.pos(), shack));
                    continue;
                }
                match nearest_plant(game, u.pos(), true, &reserved) {
                    Some(tp) => {
                        reserved.insert(tp);
                        cmds.push(if u.pos() == tp {
                            format!("HARVEST {}", u.id)
                        } else {
                            format!("MOVE {} {} {}", u.id, tp.0, tp.1)
                        });
                    }
                    None if u.total() > 0 => cmds.push(bank(u.id, u.pos(), shack)),
                    None => {}
                }
            }
        }

        // Expand: a powerful chopper first if we don't own one, then strong
        // balanced trolls, then affordable fallbacks (all chop-capable).
        if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            let specs: &[(i32, i32, i32, i32)] = if !have_real_chopper {
                &[(2, 4, 2, 2), (1, 2, 0, 2), (2, 2, 2, 2), (1, 1, 1, 1)]
            } else {
                &[(2, 2, 2, 2), (1, 2, 1, 1), (1, 1, 1, 1)]
            };
            for &spec in specs {
                let cost = training_cost(n, spec);
                if pay.iter().all(|&i| inv[i] >= cost[i]) {
                    cmds.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
                    break;
                }
            }
        }
        cmds
    }
}
