//! Head-to-head diagnostic harness. Plays two named strategies over N seeds from
//! BOTH sides and reports per-bot averages: final score, troll count, and score
//! composition (fruit vs 4x wood). This is the lens for understanding WHY a bot
//! wins/loses (e.g. the 2-troll ceiling, or whether it scores on wood or fruit).
//!
//! Usage: `cargo run --release --bin diag -- <botA> <botB> [seeds]`
//!        defaults: planner gatherer 100
use troll_farm::game::engine::{step, recompute_scores, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::{roster, Strategy};

#[derive(Default, Clone)]
struct Stat {
    games: i64,
    wins: i64,
    score: i64,
    trolls: i64,
    wood: i64,   // units of wood banked (each worth 4 pts)
    fruit: i64,  // banked PLUM+LEMON+APPLE+BANANA (1 pt each)
}

impl Stat {
    fn add_player(&mut self, g: &GameState, p: usize, won: bool) {
        self.games += 1;
        self.wins += won as i64;
        self.score += g.scores[p] as i64;
        self.trolls += g.units.iter().filter(|u| u.player as usize == p).count() as i64;
        self.wood += g.inventories[p][WOOD] as i64;
        self.fruit += g.inventories[p][0..4].iter().sum::<i32>() as i64;
    }
    fn line(&self, name: &str) -> String {
        let n = self.games.max(1) as f64;
        format!(
            "{:<12}{:>8.1}{:>9.2}{:>10.1}{:>10.1}{:>9.0}%",
            name,
            self.score as f64 / n,
            self.trolls as f64 / n,
            self.fruit as f64 / n,
            4.0 * self.wood as f64 / n,
            100.0 * self.wins as f64 / n,
        )
    }
}

fn play(a: &dyn Strategy, b: &dyn Strategy, seed: u64) -> GameState {
    let mut g = generate_bronze(seed);
    for _ in 0..300 {
        let c0 = a.decide(&g, 0);
        let c1 = b.decide(&g, 1);
        step(&mut g, &c0, &c1);
        // Real referee: game ends when no plants remain.
        if g.plants.is_empty() {
            break;
        }
    }
    recompute_scores(&mut g);
    g
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let name_a = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let name_b = args.get(2).cloned().unwrap_or_else(|| "gatherer".into());
    let seeds: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(100);

    let bots = roster();
    let ia = bots.iter().position(|x| x.name() == name_a).expect("unknown botA");
    let ib = bots.iter().position(|x| x.name() == name_b).expect("unknown botB");
    let (a, b) = (&*bots[ia], &*bots[ib]);

    let mut sa = Stat::default();
    let mut sb = Stat::default();
    let mut losses: Vec<(u64, char, i32, i32)> = Vec::new(); // (seed, side, a_score, b_score)
    for s in 0..seeds {
        // a as p0, b as p1
        let g = play(a, b, s);
        sa.add_player(&g, 0, g.scores[0] > g.scores[1]);
        sb.add_player(&g, 1, g.scores[1] > g.scores[0]);
        if g.scores[0] <= g.scores[1] {
            losses.push((s, '0', g.scores[0], g.scores[1]));
        }
        // swap seats on the same map
        let g = play(b, a, s);
        sb.add_player(&g, 0, g.scores[0] > g.scores[1]);
        sa.add_player(&g, 1, g.scores[1] > g.scores[0]);
        if g.scores[1] <= g.scores[0] {
            losses.push((s, '1', g.scores[1], g.scores[0]));
        }
    }

    println!("=== diag: {} vs {} | {} seeds x2 sides = {} games each ===",
             name_a, name_b, seeds, sa.games);
    println!("{:<12}{:>8}{:>9}{:>10}{:>10}{:>10}",
             "bot", "score", "trolls", "fruit", "wood*4", "winrate");
    println!("{}", sa.line(&name_a));
    println!("{}", sb.line(&name_b));

    if std::env::var("SHOW_LOSSES").is_ok() {
        losses.sort_by_key(|l| l.2 - l.3); // worst (most negative) margin first
        println!("\n{} losses/ties ({}): seed(side) a_score-b_score [margin]", name_a, losses.len());
        for (seed, side, a, b) in losses.iter().take(14) {
            println!("  seed {:>3}(p{}) {:>3}-{:<3} [{:+}]", seed, side, a, b, a - b);
        }
    }
}
