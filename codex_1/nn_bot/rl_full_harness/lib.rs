//! Focused build root for the full-game environment.
//!
//! The repository crate still has a compile-time include of the archived
//! `d105a-q6-expert-population.tsv` in an unrelated closed experiment.  This
//! harness imports the production modules used by `rl_full` and nothing else,
//! so the environment remains buildable and testable when that bulk archive
//! is not mounted.  All imported source paths are the production files.

extern crate self as troll_farm;

#[path = "../../../rust/src/game/mod.rs"]
pub mod game;
#[path = "../../../rust/src/bin/yamo_orchard_live.rs"]
pub mod resident_policy;
#[path = "strategies.rs"]
pub mod strategies;
#[path = "../../../rust/src/rl_full.rs"]
pub mod rl_full;
