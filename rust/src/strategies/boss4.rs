//! Model of the Bronze arena BOSS (Boss 4), reconstructed from a real replay
//! (docs/plays/game_v074_boss4_loss.html). Its actual turn-1..2 output was
//! `TRAIN 3 2 1 2` then `TRAIN 2 2 1 2` (fast choppers bought immediately from the
//! starting hand), a powerful `TRAIN 2 4 2 2` ~turn 100, plus PICK/PLANT to keep its
//! fruit topped up. It played BALANCED: 64 CHOP + 62 HARVEST with ~4 versatile
//! trolls that both fell trees (denial/wood) and gather fruit. We must rank ABOVE
//! this bot to promote out of Bronze, so it's our key sparring partner.
use std::collections::HashSet;

use super::{bank, dist, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::{GameState, Unit};

pub struct Boss4;

impl Strategy for Boss4 {
    fn name(&self) -> &str {
        "boss4"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let shack = game.shacks[player];
        let opp_shack = game.shacks[1 - player];
        let inv = &game.inventories[player];
        let mut mine: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        mine.sort_by_key(|u| u.id);
        let n = mine.len() as i32;

        let mut cmds = Vec::new();
        let mut reserved: HashSet<(i32, i32)> = HashSet::new();
        for u in &mine {
            if u.total() >= u.cc {
                cmds.push(bank(u.id, u.pos(), shack));
                continue;
            }
            // On a tree: chop it if we can (wood + denial), else harvest its fruit.
            if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
                if u.chop > 0 && u.free() > 0 {
                    cmds.push(format!("CHOP {}", u.id));
                    continue;
                }
                if u.free() > 0 && p.fruits > 0 {
                    cmds.push(format!("HARVEST {}", u.id));
                    continue;
                }
            }
            // Choppers head for the enemy-nearest tree (denial); if none, they gather
            // like everyone else (Boss 4's choppers are versatile harvesters too).
            if u.chop >= 2 {
                if let Some(p) = game
                    .plants
                    .iter()
                    .filter(|p| !reserved.contains(&p.pos()))
                    .min_by_key(|p| (dist(p.pos(), opp_shack), dist(u.pos(), p.pos())))
                {
                    reserved.insert(p.pos());
                    cmds.push(format!("MOVE {} {} {}", u.id, p.x, p.y));
                    continue;
                }
            }
            match nearest_plant(game, u.pos(), true, &reserved) {
                Some(tp) => {
                    reserved.insert(tp);
                    cmds.push(format!("MOVE {} {} {}", u.id, tp.0, tp.1));
                }
                None if u.total() > 0 => cmds.push(bank(u.id, u.pos(), shack)),
                None => {}
            }
        }

        // Expand to 4, fast choppers first (Boss buys them turn 1-2 from starting PLUM),
        // then a powerful cc-4 chopper, then cheaper fallbacks.
        if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            let specs: &[(i32, i32, i32, i32)] =
                &[(2, 2, 1, 2), (2, 4, 2, 2), (1, 2, 1, 2), (1, 1, 1, 0)];
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
