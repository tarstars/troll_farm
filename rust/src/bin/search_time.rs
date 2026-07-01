//! Per-turn wall-clock profiler for the search bot, to judge the real 50ms/turn
//! CodinGame budget. Plays `search` vs `boss4` over a few seeds, timing every
//! individual `search.decide()` call, and reports avg / median / p95 / max (µs)
//! plus how many turns would blow a 50ms budget.
//!
//! Usage: search_time [seeds]
use std::time::Instant;
use troll_farm::game::engine::step;
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::roster;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seeds: u64 = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(5);

    let bots = roster();
    let search = bots.iter().find(|b| b.name() == "search").unwrap().as_ref();
    let boss = bots.iter().find(|b| b.name() == "boss4").unwrap().as_ref();

    let mut times_us: Vec<f64> = Vec::new();
    for s in 0..seeds {
        let mut g = generate_bronze(s);
        for _ in 0..300 {
            let t0 = Instant::now();
            let c0 = search.decide(&g, 0);
            times_us.push(t0.elapsed().as_secs_f64() * 1e6);
            let c1 = boss.decide(&g, 1);
            step(&mut g, &c0, &c1);
        }
    }

    times_us.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let n = times_us.len();
    let avg = times_us.iter().sum::<f64>() / n as f64;
    let median = times_us[n / 2];
    let p95 = times_us[(n as f64 * 0.95) as usize];
    let max = times_us[n - 1];
    let over_50ms = times_us.iter().filter(|&&t| t > 50_000.0).count();
    let over_45ms = times_us.iter().filter(|&&t| t > 45_000.0).count();

    println!("search.decide() over {} turns ({} seeds):", n, seeds);
    println!("  avg    {:>8.0} µs  ({:.2} ms)", avg, avg / 1000.0);
    println!("  median {:>8.0} µs  ({:.2} ms)", median, median / 1000.0);
    println!("  p95    {:>8.0} µs  ({:.2} ms)", p95, p95 / 1000.0);
    println!("  max    {:>8.0} µs  ({:.2} ms)", max, max / 1000.0);
    println!("  turns > 50ms: {}/{}   > 45ms: {}/{}", over_50ms, n, over_45ms, n);
}
