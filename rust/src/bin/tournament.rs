//! Local round-robin tournament: every strategy plays every other on the same
//! maps from both sides, and we print a leaderboard. This is our own trustworthy
//! ladder for ranking strategies (and, later, tuned/learned ones) -- fast enough
//! to run thousands of games because both the sim and the bots are in Rust.
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

fn main() {
    let seeds: u64 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(100);
    let bots = roster();
    let n = bots.len();
    let mut wins = vec![0i64; n];
    let mut games = vec![0i64; n];
    let mut margin = vec![0i64; n];
    // h2h[i][j] = games i won against j (summed over both seatings).
    let mut h2h = vec![vec![0i64; n]; n];

    let t0 = std::time::Instant::now();
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue; // (self-play could be added; skip for the ladder)
            }
            for s in 0..seeds {
                let (si, sj) = play(&*bots[i], &*bots[j], s);
                games[i] += 1;
                games[j] += 1;
                margin[i] += (si - sj) as i64;
                margin[j] += (sj - si) as i64;
                if si > sj {
                    wins[i] += 1;
                    h2h[i][j] += 1;
                } else if sj > si {
                    wins[j] += 1;
                    h2h[j][i] += 1;
                }
            }
        }
    }
    let total_games: i64 = games.iter().sum::<i64>() / 2;
    let elapsed = t0.elapsed();

    let mut order: Vec<usize> = (0..n).collect();
    order.sort_by(|&a, &b| (wins[b], margin[b]).cmp(&(wins[a], margin[a])));

    println!(
        "=== Local leaderboard | {} strategies | {} seeds/pairing both sides | {} games in {:.2}s ===",
        n, seeds, total_games, elapsed.as_secs_f64()
    );
    println!(
        "{:<4}{:<12}{:>7}{:>7}{:>9}{:>12}",
        "#", "strategy", "wins", "games", "winrate", "avg_margin"
    );
    for (rank, &i) in order.iter().enumerate() {
        let wr = 100.0 * wins[i] as f64 / games[i] as f64;
        let am = margin[i] as f64 / games[i] as f64;
        println!(
            "{:<4}{:<12}{:>7}{:>7}{:>8.0}%{:>12.1}",
            rank + 1,
            bots[i].name(),
            wins[i],
            games[i],
            wr,
            am
        );
    }

    // Head-to-head matrix: cell = row's win% over column (out of 2*seeds direct
    // games). This is the honest pairwise signal -- aggregate winrate is diluted
    // by how each bot fares against the weakest field members.
    let pair_games = (2 * seeds) as f64;
    println!("\nHead-to-head win% (row vs column):");
    print!("{:<12}", "");
    for &j in &order {
        print!("{:>9.6}", bots[j].name());
    }
    println!();
    for &i in &order {
        print!("{:<12}", bots[i].name());
        for &j in &order {
            if i == j {
                print!("{:>9}", "-");
            } else {
                print!("{:>8.0}%", 100.0 * h2h[i][j] as f64 / pair_games);
            }
        }
        println!();
    }
}
