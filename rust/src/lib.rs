// Self-referential alias so code copied verbatim from `src/bin/*.rs` modules
// (which depend on this package's own lib crate externally, as
// `troll_farm::...`) keeps compiling unmodified when reused from inside the
// lib crate itself (D170a's `rl_d170a_option_policy_env.rs`).
extern crate self as troll_farm;

pub mod botmain;
pub mod d41b_prior_kernel;
pub mod etudes;
pub mod game;
pub mod planner;
#[path = "bin/yamo_orchard_live.rs"]
pub mod resident_policy;
pub mod rl_batch_option;
pub mod rl_d170a_option_policy_env;
pub mod rl_level1;
pub mod rl_level3;
pub mod rl_full;
pub mod rl_macro;
pub mod rl_opening_portfolio;
pub mod rl_q6_proposal;
pub mod rl_resident_residual;
pub mod strategies;
