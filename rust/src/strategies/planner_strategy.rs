//! Tournament wrapper around our REAL submission's planner (src/planner.rs — the
//! v0.7.5 CG bot logic). Builds a planner::State view for `player` from the shared
//! GameState and delegates to planner::decide, so the local ladder can rank our
//! actual arena bot (rank ~152) against the hand-coded strategies.
use super::Strategy;
use crate::game::state::{GameState, Plant, Unit};
use crate::planner::{self, State as PState, Tree as PTree, Troll as PTroll};

pub struct Planner;

fn to_troll(u: &Unit) -> PTroll {
    PTroll {
        id: u.id,
        x: u.x,
        y: u.y,
        movement_speed: u.ms,
        carry_capacity: u.cc,
        harvest_power: u.hp,
        chop_power: u.chop,
        carry: u.carry,
    }
}

fn to_tree(p: &Plant) -> PTree {
    PTree {
        tree_type: p.plant_type.clone(),
        x: p.x,
        y: p.y,
        size: p.size,
        health: p.health,
        fruits: p.fruits,
        cooldown: p.cooldown,
    }
}

impl Strategy for Planner {
    fn name(&self) -> &str {
        "planner"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let opp = 1 - player;
        let st = PState {
            walkable: game.walkable.clone(),
            my_shack: game.shacks[player],
            opp_shack: game.shacks[opp],
            my_inventory: game.inventories[player],
            opp_inventory: game.inventories[opp],
            trees: game.plants.iter().map(to_tree).collect(),
            my_trolls: game
                .units
                .iter()
                .filter(|u| u.player as usize == player)
                .map(to_troll)
                .collect(),
            opp_trolls: game
                .units
                .iter()
                .filter(|u| u.player as usize == opp)
                .map(to_troll)
                .collect(),
            turn: game.turn,
            iron_cells: game.iron.clone(),
            water_cells: game.water.clone(),
        };
        planner::decide(&st)
    }
}
