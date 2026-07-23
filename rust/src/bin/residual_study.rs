//! Paired residual-search study against one frozen opponent.
//!
//! For every seed, control and candidate use clones of the same initial map and
//! play both seats. The independent value is the seat-averaged candidate margin
//! minus the seat-averaged GoldElite margin.
use std::cmp::Ordering;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::residual_search::ResidualSearchBot;
use troll_farm::strategies::{roster, Strategy};

fn opponent(name: &str) -> Box<dyn Strategy> {
    roster()
        .into_iter()
        .find(|strategy| strategy.name() == name)
        .unwrap_or_else(|| panic!("unknown opponent {name}"))
}

fn play(mut game: GameState, p0: &dyn Strategy, p1: &dyn Strategy) -> (i32, i32) {
    let mut turns_until_end = 0;
    for _ in 0..300 {
        let c0 = p0.decide(&game, 0);
        let c1 = p1.decide(&game, 1);
        step(&mut game, &c0, &c1);
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    (game.scores[0], game.scores[1])
}

fn paired_delta(seed: u64, opponent_name: &str) -> f64 {
    let initial = generate_bronze(seed);
    let control = GoldElite::new();
    let opposing = opponent(opponent_name);
    let (control_0, opponent_1) = play(initial.clone(), &control, opposing.as_ref());
    let opposing = opponent(opponent_name);
    let control = GoldElite::new();
    let (opponent_0, control_1) = play(initial.clone(), opposing.as_ref(), &control);
    let control_margin = 0.5 * ((control_0 - opponent_1) + (control_1 - opponent_0)) as f64;

    let candidate = ResidualSearchBot::new();
    let opposing = opponent(opponent_name);
    let (candidate_0, opponent_1) = play(initial.clone(), &candidate, opposing.as_ref());
    let opposing = opponent(opponent_name);
    let candidate = ResidualSearchBot::new();
    let (opponent_0, candidate_1) = play(initial, opposing.as_ref(), &candidate);
    let candidate_margin = 0.5 * ((candidate_0 - opponent_1) + (candidate_1 - opponent_0)) as f64;
    candidate_margin - control_margin
}

fn mean(values: &[f64]) -> f64 {
    values.iter().sum::<f64>() / values.len() as f64
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let opponent_name = args.get(1).map(String::as_str).unwrap_or("goldelite");
    let seeds: u64 = args
        .get(2)
        .and_then(|value| value.parse().ok())
        .unwrap_or(40);
    let start: u64 = args
        .get(3)
        .and_then(|value| value.parse().ok())
        .unwrap_or(0);
    let threads = std::thread::available_parallelism()
        .map(|count| count.get() as u64)
        .unwrap_or(4)
        .clamp(1, seeds.max(1));
    let chunk = (seeds + threads - 1) / threads;
    let started = std::time::Instant::now();
    let mut results: Vec<(u64, f64)> = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|thread| {
                scope.spawn(move || {
                    let lo = start + thread * chunk;
                    let hi = (lo + chunk).min(start + seeds);
                    (lo..hi)
                        .map(|seed| (seed, paired_delta(seed, opponent_name)))
                        .collect::<Vec<_>>()
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().unwrap())
            .collect()
    });
    results.sort_by(|left, right| left.1.partial_cmp(&right.1).unwrap_or(Ordering::Equal));
    let values: Vec<f64> = results.iter().map(|(_, value)| *value).collect();
    let trim = (0.05 * values.len() as f64).floor() as usize;
    let trimmed = if trim == 0 {
        &values[..]
    } else {
        &values[trim..values.len() - trim]
    };
    let worst_n = ((0.10 * values.len() as f64).ceil() as usize).max(1);
    let without_largest = if values.len() > 1 {
        mean(&values[..values.len() - 1])
    } else {
        values[0]
    };
    println!(
        "residual paired vs {opponent_name}: seeds {start}..{} ({seeds}), {threads} threads, {:.2}s",
        start + seeds - 1,
        started.elapsed().as_secs_f64()
    );
    println!(
        "delta mean {:+.3}, trimmed5 {:+.3}, without-max {:+.3}, worst10 {:+.3}",
        mean(&values),
        mean(trimmed),
        without_largest,
        mean(&values[..worst_n]),
    );
    println!(
        "W/T/L {}/{}/{}, min {:+.1}, median {:+.1}, max {:+.1}",
        values.iter().filter(|value| **value > 0.0).count(),
        values.iter().filter(|value| **value == 0.0).count(),
        values.iter().filter(|value| **value < 0.0).count(),
        values[0],
        values[values.len() / 2],
        values[values.len() - 1],
    );
    let regressions: Vec<_> = results
        .iter()
        .filter(|(_, value)| *value < 0.0)
        .map(|(seed, value)| format!("{seed}:{value:+.1}"))
        .collect();
    if !regressions.is_empty() {
        println!("negative seeds: {}", regressions.join(", "));
    }
}
