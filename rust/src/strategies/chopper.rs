//! Wood-economy strategy: build a chopper (bootstrap with the chop-1 starter),
//! mine iron + fell trees for 4-pt wood; spare trolls harvest fruit.
use std::collections::HashSet;

use super::{bank, dist, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::GameState;

pub struct Chopper;

impl Strategy for Chopper {
    fn name(&self) -> &str {
        "chopper"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let shack = game.shacks[player];
        let mut mine: Vec<&crate::game::state::Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        mine.sort_by_key(|u| u.id);
        let inv = &game.inventories[player];
        let n = mine.len() as i32;
        let have_chopper = mine.iter().any(|u| u.chop >= 2);
        let mut cmds = Vec::new();
        let mut reserved: HashSet<(i32, i32)> = HashSet::new();

        for u in &mine {
            let acts_as_chopper = u.chop >= 2 || (!have_chopper && u.chop >= 1);
            if acts_as_chopper {
                if u.free() > 0 && game.iron.iter().any(|&c| dist(u.pos(), c) == 1) {
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
                        cmds.push(format!("MOVE {} {} {}", u.id, tp.0, tp.1));
                    }
                    None if u.total() > 0 => cmds.push(bank(u.id, u.pos(), shack)),
                    None => {}
                }
            }
        }

        if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            let specs: &[(i32, i32, i32, i32)] = if !have_chopper {
                &[(1, 2, 0, 2), (1, 1, 0, 2), (1, 1, 1, 0)]
            } else {
                &[(1, 1, 1, 0)]
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
