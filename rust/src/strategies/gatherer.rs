//! Fruit-economy strategy: expand to strong balanced trolls, harvest aggressively
//! with distinct tree targets, never chop. (Port of sim/boss.py gatherer_boss.)
use std::collections::HashSet;

use super::{bank, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::GameState;

const SPECS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 2), (1, 2, 2, 0), (1, 1, 1, 0)];

pub struct Gatherer;

impl Strategy for Gatherer {
    fn name(&self) -> &str {
        "gatherer"
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
        let mut cmds = Vec::new();
        let mut reserved: HashSet<(i32, i32)> = HashSet::new();

        for u in &mine {
            let on_fruit = game
                .plants
                .iter()
                .any(|p| p.pos() == u.pos() && p.fruits > 0);
            if on_fruit && u.total() < u.cc {
                cmds.push(format!("HARVEST {}", u.id));
                continue;
            }
            let any_fruit = game.plants.iter().any(|p| p.fruits > 0);
            if u.total() >= u.cc || (u.total() > 0 && !any_fruit) {
                cmds.push(bank(u.id, u.pos(), shack));
                continue;
            }
            if let Some(tpos) = nearest_plant(game, u.pos(), true, &reserved) {
                reserved.insert(tpos);
                cmds.push(if u.pos() == tpos {
                    format!("HARVEST {}", u.id)
                } else {
                    format!("MOVE {} {} {}", u.id, tpos.0, tpos.1)
                });
            } else if u.total() > 0 {
                cmds.push(bank(u.id, u.pos(), shack));
            }
        }

        if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            for spec in SPECS {
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
