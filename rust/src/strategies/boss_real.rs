//! FAITHFUL port of the real arena boss (config/level2/Boss.cs from the referee
//! repo eulerscheZahl/Troll-Farm) -- this is the actual "Boss 4" that gates Silver.
//! It is a SUSTAINABLE FARMER, not a chopper:
//!   - fields exactly 2 cheap gatherers (TRAIN 1 1 1 0), never more;
//!   - NEVER chops or mines -- pure fruit harvesting (Manhattan routing);
//!   - among fruited trees it keeps the FARTHER ones past the closest (a quirky
//!     tie-break in the original), with a sticky per-worker target;
//!   - when a full worker reaches a base-adjacent cell with no tree, it PLANTs its
//!     carried fruit there (seeding a small base orchard), else DROPs.
//! Because it preserves + replants trees, it out-farms a scorch-earth chopper over
//! 300 turns. Our old `boss4` model (a chopper) was the wrong opponent entirely.
use std::cell::RefCell;
use std::collections::HashMap;

use super::Strategy;
use crate::game::state::{GameState, Plant, Unit};

pub struct BossReal {
    // Sticky per-worker target memory (mirrors the boss's `targetTrees` dict).
    // Cleared at turn 1 so it resets between games (the sim reuses one instance).
    targets: RefCell<HashMap<i32, (i32, i32)>>,
}

impl BossReal {
    pub fn new() -> Self {
        BossReal { targets: RefCell::new(HashMap::new()) }
    }
}

fn manh(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

impl Strategy for BossReal {
    fn name(&self) -> &str {
        "bossreal"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let base = game.shacks[player];
        let mut mine: Vec<&Unit> =
            game.units.iter().filter(|u| u.player as usize == player).collect();
        mine.sort_by_key(|u| u.id);

        if game.turn == 1 {
            self.targets.borrow_mut().clear();
        }
        let mut targets = self.targets.borrow_mut();

        let mut actions: Vec<String> = vec!["MSG Eat your vegetables!".into()];
        for w in &mine {
            // Full -> head home; at base plant a seed on an empty base-adjacent cell,
            // else drop. (The original's hasPlanted flag is never set, so it plants
            // whenever the cell is tree-free.)
            if w.total() >= w.cc {
                targets.remove(&w.id);
                if manh(w.pos(), base) == 1 {
                    let on_tree = game.plants.iter().any(|p| p.pos() == w.pos());
                    if !on_tree {
                        if let Some(idx) = (0..4).find(|&i| w.carry[i] == 1) {
                            let ty = ["PLUM", "LEMON", "APPLE", "BANANA"][idx];
                            actions.push(format!("PLANT {} {}", w.id, ty));
                        } else {
                            actions.push(format!("DROP {}", w.id));
                        }
                    } else {
                        actions.push(format!("DROP {}", w.id));
                    }
                } else {
                    actions.push(format!("MOVE {} {} {}", w.id, base.0, base.1));
                }
                continue;
            }

            // Not full -> harvest the nearest-of-the-farther fruited tree (Manhattan).
            let mut cands: Vec<&Plant> = game.plants.iter().filter(|p| p.fruits > 0).collect();
            if cands.is_empty() {
                continue;
            }
            cands.sort_by_key(|c| manh(w.pos(), c.pos()));
            let closest = manh(w.pos(), cands[0].pos());
            if cands.iter().any(|c| manh(w.pos(), c.pos()) > closest) {
                cands.retain(|c| manh(w.pos(), c.pos()) > closest);
            }
            let mut target = cands[0].pos();
            // Sticky: keep the remembered target if it still has fruit.
            if let Some(&(tx, ty)) = targets.get(&w.id) {
                if game.plants.iter().any(|p| p.pos() == (tx, ty) && p.fruits > 0) {
                    target = (tx, ty);
                }
            }
            targets.insert(w.id, target);
            if manh(w.pos(), target) == 0 {
                actions.push(format!("HARVEST {}", w.id));
            } else {
                actions.push(format!("MOVE {} {} {}", w.id, target.0, target.1));
            }
        }

        if mine.len() < 2 {
            actions.push("TRAIN 1 1 1 0".into());
        }
        actions
    }
}
