pub mod game {
    include!("model.rs");
}

pub mod bot {
    use super::game::GameState;
    pub trait Bot {
        fn commands(&mut self, view: &GameState) -> Vec<String>;
    }

    pub mod moisan {
        use super::Bot;
        use crate::candidate::game::nav::{bfs_distances, is_adjacent, manhattan, next_cell, ortho_neighbors};
        use crate::candidate::game::rules::{effective_cooldown, training_cost, tree_health, TOTAL_TURNS};
        use crate::candidate::game::types::{Cell, GameState, Plant, PlantKind, Stats, Unit, APPLE, BANANA, IRON, LEMON, PLUM, WOOD};
        use std::collections::{BTreeMap, BTreeSet};

        include!("config.rs");
        include!("movement.rs");
        include!("economy.rs");
        pub type SecureOrchardBot = R1faBot;

        #[cfg(test)]
        mod tests {
            use super::*;
            include!("tests.rs");
        }
    }
}
