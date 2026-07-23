//! Focused head-to-head benchmark: strategy A vs strategy B over N seeds, both
//! seatings, on the same bronze maps. Prints win rate + avg margin and (optionally)
//! the losing seeds so we can diagnose the maps we drop.
//!
//! PARALLEL: the seed loop is embarrassingly parallel, so we split seeds across all
//! CPU cores (std::thread::scope). Each thread builds its OWN strategy instances
//! (strategies hold RefCell target-memory, which is !Sync -- never shared).
//!
//! Usage: bench [A] [B] [seeds] [--losses]
use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::{roster, Strategy};

fn play(p0: &dyn Strategy, p1: &dyn Strategy, seed: u64) -> (i32, i32) {
    let mut g = generate_bronze(seed);
    let mut turns_until_end = 0;
    for _ in 0..300 {
        let c0 = p0.decide(&g, 0);
        let c1 = p1.decide(&g, 1);
        step(&mut g, &c0, &c1);
        if has_stalled(&g, &mut turns_until_end) {
            break;
        }
    }
    (g.scores[0], g.scores[1])
}

fn find<'a>(bots: &'a [Box<dyn Strategy>], name: &str) -> &'a dyn Strategy {
    bots.iter()
        .find(|b| b.name() == name)
        .unwrap_or_else(|| panic!("no strategy named {name}"))
        .as_ref()
}

#[derive(Default)]
struct Acc {
    a_wins: i64,
    b_wins: i64,
    draws: i64,
    margin: i64,
    games: i64,
    losses: Vec<(u64, char, i32, i32)>, // seed, seat, a_score, b_score
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let a_name = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let b_name = args.get(2).cloned().unwrap_or_else(|| "boss4".into());
    let seeds: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(300);
    let show_losses = args.iter().any(|a| a == "--losses");

    let nthreads = std::thread::available_parallelism()
        .map(|n| n.get() as u64)
        .unwrap_or(4)
        .clamp(1, seeds.max(1));
    let chunk = (seeds + nthreads - 1) / nthreads;

    let t0 = std::time::Instant::now();
    let parts: Vec<Acc> = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..nthreads)
            .map(|t| {
                let a_name = a_name.clone();
                let b_name = b_name.clone();
                scope.spawn(move || {
                    let bots = roster();
                    let a = find(&bots, &a_name);
                    let b = find(&bots, &b_name);
                    let lo = t * chunk;
                    let hi = ((t + 1) * chunk).min(seeds);
                    let mut acc = Acc::default();
                    for s in lo..hi {
                        // A as player 0
                        let (sa, sb) = play(a, b, s);
                        acc.games += 1;
                        acc.margin += (sa - sb) as i64;
                        if sa > sb {
                            acc.a_wins += 1;
                        } else if sb > sa {
                            acc.b_wins += 1;
                            acc.losses.push((s, '0', sa, sb));
                        } else {
                            acc.draws += 1;
                            acc.losses.push((s, '0', sa, sb));
                        }
                        // A as player 1
                        let (sb2, sa2) = play(b, a, s);
                        acc.games += 1;
                        acc.margin += (sa2 - sb2) as i64;
                        if sa2 > sb2 {
                            acc.a_wins += 1;
                        } else if sb2 > sa2 {
                            acc.b_wins += 1;
                            acc.losses.push((s, '1', sa2, sb2));
                        } else {
                            acc.draws += 1;
                            acc.losses.push((s, '1', sa2, sb2));
                        }
                    }
                    acc
                })
            })
            .collect();
        handles.into_iter().map(|h| h.join().unwrap()).collect()
    });

    let mut tot = Acc::default();
    for p in parts {
        tot.a_wins += p.a_wins;
        tot.b_wins += p.b_wins;
        tot.draws += p.draws;
        tot.margin += p.margin;
        tot.games += p.games;
        tot.losses.extend(p.losses);
    }
    tot.losses.sort();

    let wr = 100.0 * tot.a_wins as f64 / tot.games as f64;
    let am = tot.margin as f64 / tot.games as f64;
    println!(
        "{} vs {} | {} games ({} seeds x2 seats, {} threads) in {:.2}s",
        a_name,
        b_name,
        tot.games,
        seeds,
        nthreads,
        t0.elapsed().as_secs_f64()
    );
    println!(
        "{}: {} wins ({:.1}%)  |  {}: {} wins  |  draws: {}  |  avg margin (A-B): {:+.1}",
        a_name, tot.a_wins, wr, b_name, tot.b_wins, tot.draws, am
    );

    if show_losses {
        println!(
            "\n{} non-wins ({} seeds, seat = A's player index):",
            a_name,
            tot.losses.len()
        );
        for (s, seat, asc, bsc) in &tot.losses {
            println!(
                "  seed {:>4} seat {}  A={:>3} B={:>3}  (margin {:+})",
                s,
                seat,
                asc,
                bsc,
                asc - bsc
            );
        }
    }
}
