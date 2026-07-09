//! Weak baseline: harvest the nearest fruit, bank, and train cheap gatherers up
//! to 2 trolls. A deliberately simple entry to sanity-check the tournament ranks
//! strategies sensibly (it should sit near the bottom).
use std::collections::HashSet;

use super::{bank, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::GameState;

pub struct Harvester;

impl Strategy for Harvester {
    fn name(&self) -> &str {
        "harvester"
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

        if n < 2 && !mine.iter().any(|u| u.pos() == shack) {
            let spec = (1, 1, 1, 0);
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            let cost = training_cost(n, spec);
            if pay.iter().all(|&i| inv[i] >= cost[i]) {
                cmds.push("TRAIN 1 1 1 0".to_string());
            }
        }
        cmds
    }
}
