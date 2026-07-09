//! Pluggable bot strategies for the local tournament. Each strategy maps a full
//! GameState + which player it controls to that player's commands for the turn.
use crate::game::state::GameState;

pub mod balanced;
pub mod boss4;
pub mod boss5;
pub mod boss_real;
pub mod boss_v3;
pub mod chopper;
pub mod gatherer;
pub mod gold_elite;
pub mod harvester;
pub mod mybot;
pub mod orchard;
pub mod planner_strategy;
pub mod printer_bot;
pub mod rhea_bot;
pub mod sched_bot;
pub mod script_boss;
pub mod search_bot;
pub mod silver_boss;

pub trait Strategy {
    fn name(&self) -> &str;
    fn decide(&self, game: &GameState, player: usize) -> Vec<String>;
}

pub fn dist(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// DROP if adjacent to the shack, else MOVE toward it.
pub fn bank(id: i32, pos: (i32, i32), shack: (i32, i32)) -> String {
    if dist(pos, shack) == 1 {
        format!("DROP {}", id)
    } else {
        format!("MOVE {} {} {}", id, shack.0, shack.1)
    }
}

/// Nearest plant position (optionally fruited-only, skipping `reserved`).
pub fn nearest_plant(
    game: &GameState,
    from: (i32, i32),
    fruited_only: bool,
    reserved: &std::collections::HashSet<(i32, i32)>,
) -> Option<(i32, i32)> {
    let mut best: Option<(i32, (i32, i32))> = None;
    for p in &game.plants {
        if fruited_only && p.fruits <= 0 {
            continue;
        }
        if reserved.contains(&p.pos()) {
            continue;
        }
        let d = dist(from, p.pos());
        if best.is_none() || d < best.unwrap().0 {
            best = Some((d, p.pos()));
        }
    }
    best.map(|(_, c)| c)
}

/// All strategies entered in the tournament.
pub fn roster() -> Vec<Box<dyn Strategy>> {
    vec![
        Box::new(planner_strategy::Planner),
        Box::new(gatherer::Gatherer),
        Box::new(orchard::Orchard),
        Box::new(boss4::Boss4),
        Box::new(boss5::Boss5::new()),
        Box::new(boss_real::BossReal::new()),
        Box::new(chopper::Chopper),
        Box::new(harvester::Harvester),
        Box::new(balanced::Balanced),
        Box::new(search_bot::SearchBot),
        Box::new(silver_boss::SilverBoss::new()),
        Box::new(script_boss::ScriptBoss::new()),
        Box::new(boss_v3::BossV3::new()),
        Box::new(printer_bot::PrinterBot::new()),
        Box::new(gold_elite::GoldElite::new()),
        Box::new(gold_elite::GoldElite::hybrid()),
        Box::new(gold_elite::GoldElite::accumulate()),
        Box::new(gold_elite::GoldElite::adaptive()),
        Box::new(sched_bot::SchedBot::new()),
        Box::new(rhea_bot::RheaBot::new()),
        Box::new(mybot::MyBot::new()),
    ]
}
