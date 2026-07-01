//! Focused head-to-head benchmark: strategy A vs strategy B over N seeds, both
//! seatings, on the same bronze maps. Prints win rate + avg margin and (optionally)
//! the losing seeds so we can diagnose the maps we drop. Much faster than the full
//! round-robin when we only care about one matchup (planner vs boss4).
//!
//! Usage: bench [A] [B] [seeds] [--losses]
//!   A, B   strategy names (default: planner boss4)
//!   seeds  number of map seeds (default 300); each played from BOTH sides
//!   --losses  print the seed list where A lost / drew as A-seat and B-seat
use troll_farm::game::engine::step;
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::{roster, Strategy};

fn play(p0: &dyn Strategy, p1: &dyn Strategy, seed: u64) -> (i32, i32) {
    let mut g = generate_bronze(seed);
    for _ in 0..300 {
        let c0 = p0.decide(&g, 0);
        let c1 = p1.decide(&g, 1);
        step(&mut g, &c0, &c1);
    }
    (g.scores[0], g.scores[1])
}

fn find<'a>(bots: &'a [Box<dyn Strategy>], name: &str) -> &'a dyn Strategy {
    bots.iter()
        .find(|b| b.name() == name)
        .unwrap_or_else(|| panic!("no strategy named {name}"))
        .as_ref()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let a_name = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let b_name = args.get(2).cloned().unwrap_or_else(|| "boss4".into());
    let seeds: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(300);
    let show_losses = args.iter().any(|a| a == "--losses");

    let bots = roster();
    let a = find(&bots, &a_name);
    let b = find(&bots, &b_name);

    let mut a_wins = 0i64;
    let mut b_wins = 0i64;
    let mut draws = 0i64;
    let mut margin = 0i64; // sum of (A - B) over all games
    let mut games = 0i64;
    let mut loss_seeds: Vec<(u64, char, i32, i32)> = Vec::new(); // seed, seat, a_score, b_score

    let t0 = std::time::Instant::now();
    for s in 0..seeds {
        // A as player 0
        let (sa, sb) = play(a, b, s);
        games += 1;
        margin += (sa - sb) as i64;
        if sa > sb {
            a_wins += 1;
        } else if sb > sa {
            b_wins += 1;
            loss_seeds.push((s, '0', sa, sb));
        } else {
            draws += 1;
            loss_seeds.push((s, '0', sa, sb));
        }
        // A as player 1
        let (sb2, sa2) = play(b, a, s);
        games += 1;
        margin += (sa2 - sb2) as i64;
        if sa2 > sb2 {
            a_wins += 1;
        } else if sb2 > sa2 {
            b_wins += 1;
            loss_seeds.push((s, '1', sa2, sb2));
        } else {
            draws += 1;
            loss_seeds.push((s, '1', sa2, sb2));
        }
    }

    let wr = 100.0 * a_wins as f64 / games as f64;
    let am = margin as f64 / games as f64;
    println!(
        "{} vs {} | {} games ({} seeds x2 seats) in {:.2}s",
        a_name, b_name, games, seeds, t0.elapsed().as_secs_f64()
    );
    println!(
        "{}: {} wins ({:.1}%)  |  {}: {} wins  |  draws: {}  |  avg margin (A-B): {:+.1}",
        a_name, a_wins, wr, b_name, b_wins, draws, am
    );

    if show_losses {
        println!("\n{} non-wins ({} seeds, seat = A's player index):", a_name, loss_seeds.len());
        for (s, seat, asc, bsc) in &loss_seeds {
            println!("  seed {:>4} seat {}  A={:>3} B={:>3}  (margin {:+})", s, seat, asc, bsc, asc - bsc);
        }
    }
}
