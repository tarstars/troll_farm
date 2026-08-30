//! The exact strategy subset referenced by `rust/src/rl_full.rs`.

use crate::game::state::GameState;

#[path = "../../../rust/src/strategies/champion_exact.rs"]
pub mod champion_exact;
#[path = "../../../rust/src/strategies/compact_gold.rs"]
pub mod compact_gold;
#[path = "../../../rust/src/strategies/gold_elite.rs"]
pub mod gold_elite;
#[path = "../../../rust/src/strategies/legend_field_proxy.rs"]
pub mod legend_field_proxy;
#[path = "../../../rust/src/strategies/mybot.rs"]
pub mod mybot;
#[path = "../../../rust/src/strategies/norxondor_native.rs"]
pub mod norxondor_native;
#[path = "../../../rust/src/strategies/norxondor_research.rs"]
pub mod norxondor_research;
#[path = "../../../rust/src/strategies/script_boss.rs"]
pub mod script_boss;
#[path = "../../../rust/src/strategies/silver_boss.rs"]
pub mod silver_boss;

pub trait Strategy: Send {
    fn name(&self) -> &str;
    fn decide(&self, game: &GameState, player: usize) -> Vec<String>;
}
