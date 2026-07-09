//! Strong arena-realistic opponent: a GATHERER that plants a banana ORCHARD near
//! its shack for sustained high fruit income, then fields up to 4 fast harvesters.
//! This models the kind of bot that actually beats us around rank 152 (a 3-troll
//! gatherer + orchard + ~185 harvests, 0 chop). It is the real stress test for the
//! planner's denial: to beat it the planner must chop the orchard, not just out-farm.
use std::collections::HashSet;

use super::{bank, dist, nearest_plant, Strategy};
use crate::game::engine::training_cost;
use crate::game::state::{GameState, Unit};

const BANANA: usize = 3;

pub struct Orchard;

/// The orchard footprint: the `k` nearest walkable cells to the shack (excluding
/// the shack itself), deterministically ordered by (distance, cell).
fn orchard_cells(game: &GameState, shack: (i32, i32), k: usize) -> Vec<(i32, i32)> {
    let mut cells: Vec<(i32, i32)> = game
        .walkable
        .iter()
        .copied()
        .filter(|&c| c != shack)
        .collect();
    cells.sort_by_key(|&c| (dist(shack, c), c.0, c.1));
    cells.truncate(k);
    cells
}

impl Strategy for Orchard {
    fn name(&self) -> &str {
        "orchard"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let shack = game.shacks[player];
        let inv = &game.inventories[player];
        let mut mine: Vec<&Unit> = game
            .units
            .iter()
            .filter(|u| u.player as usize == player)
            .collect();
        mine.sort_by_key(|u| u.id);
        let n = mine.len() as i32;

        // Orchard footprint and which of its cells still need a tree planted.
        let footprint = orchard_cells(game, shack, 4);
        let empty_orchard: Vec<(i32, i32)> = footprint
            .iter()
            .copied()
            .filter(|c| !game.plants.iter().any(|p| p.pos() == *c))
            .collect();
        // Dedicate ONE spare troll (highest id) as the planter -- but only once we
        // can afford to: 3+ trolls so 2+ keep harvesting, and a banana surplus (keep
        // some banked for score). Planting is a long-horizon investment, never a
        // turn-1 move. Below that bar, everyone harvests (so a 1-troll start grows
        // its fleet first, instead of starving on plant cycles).
        let need_orchard = !empty_orchard.is_empty() && inv[BANANA] >= 4 && n >= 3;
        let planter_id = if need_orchard {
            mine.last().map(|u| u.id)
        } else {
            None
        };

        let mut cmds = Vec::new();
        let mut reserved: HashSet<(i32, i32)> = HashSet::new();
        for u in &mine {
            if Some(u.id) == planter_id {
                // Planter: pick a banana seed at the shack, carry it to the nearest
                // empty orchard cell, plant it.
                if u.carry[BANANA] > 0 {
                    if empty_orchard.contains(&u.pos()) {
                        cmds.push(format!("PLANT {} BANANA", u.id));
                    } else {
                        let tgt = empty_orchard
                            .iter()
                            .copied()
                            .min_by_key(|c| dist(u.pos(), *c))
                            .unwrap();
                        cmds.push(format!("MOVE {} {} {}", u.id, tgt.0, tgt.1));
                    }
                    continue;
                }
                if u.total() > 0 {
                    // carrying harvested fruit, not a seed -> bank it first
                    cmds.push(bank(u.id, u.pos(), shack));
                    continue;
                }
                if dist(u.pos(), shack) == 1 {
                    cmds.push(format!("PICK {} BANANA", u.id));
                } else {
                    cmds.push(format!("MOVE {} {} {}", u.id, shack.0, shack.1));
                }
                continue;
            }
            // Harvester
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

        // Expand to 4 fast harvesters; cheapest affordable spec wins (iron-aware pay).
        if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
            let pay: &[usize] = if !game.iron.is_empty() {
                &[0, 1, 2, 4]
            } else {
                &[0, 1, 2]
            };
            for &spec in [(2, 2, 2, 0), (1, 2, 1, 0), (1, 1, 1, 0)].iter() {
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
