//! Measure release-mode residual-search decision latency and override frequency.
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::residual_search::ResidualSearchBot;
use troll_farm::strategies::Strategy;

fn main() {
    let seeds: u64 = std::env::args()
        .nth(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(3);
    let mut samples = Vec::new();
    let mut overrides = 0usize;
    let mut turns = 0usize;
    let mut over_budget_by_game = Vec::new();
    for seed in 0..seeds {
        let mut game = generate_bronze(seed);
        let candidate = ResidualSearchBot::new();
        let control = GoldElite::new();
        let opponent = GoldElite::new();
        let mut turns_until_end = 0;
        let mut game_over_budget = 0usize;
        for _ in 0..300 {
            let baseline = control.decide(&game, 0);
            let started = Instant::now();
            let commands = candidate.decide(&game, 0);
            let elapsed = started.elapsed().as_micros() as u64;
            game_over_budget += (elapsed > 50_000) as usize;
            samples.push(elapsed);
            overrides += (commands != baseline) as usize;
            turns += 1;
            let opposition = opponent.decide(&game, 1);
            step(&mut game, &commands, &opposition);
            if has_stalled(&game, &mut turns_until_end) {
                break;
            }
        }
        over_budget_by_game.push(game_over_budget);
    }
    samples.sort_unstable();
    let percentile = |fraction: f64| -> u64 {
        let index = ((samples.len() - 1) as f64 * fraction).round() as usize;
        samples[index]
    };
    let mean = samples.iter().sum::<u64>() as f64 / samples.len() as f64;
    let over_budget = samples.iter().filter(|sample| **sample > 50_000).count();
    println!(
        "residual search: {seeds} games, {turns} turns, {overrides} overrides ({:.1}%)",
        100.0 * overrides as f64 / turns as f64
    );
    println!(
        "decision latency: mean {:.2} ms, p50 {:.2} ms, p95 {:.2} ms, p99 {:.2} ms, max {:.2} ms",
        mean / 1000.0,
        percentile(0.50) as f64 / 1000.0,
        percentile(0.95) as f64 / 1000.0,
        percentile(0.99) as f64 / 1000.0,
        samples[samples.len() - 1] as f64 / 1000.0,
    );
    println!(
        "over 50 ms: {over_budget}/{turns} ({:.2}%), max in one game {}, games with >=3: {}",
        100.0 * over_budget as f64 / turns as f64,
        over_budget_by_game.iter().copied().max().unwrap_or(0),
        over_budget_by_game
            .iter()
            .filter(|count| **count >= 3)
            .count(),
    );
}
