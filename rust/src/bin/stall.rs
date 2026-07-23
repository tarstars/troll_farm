//! Starvation/stall harness. Plays goldelite(p0) vs an opponent and measures the
//! DEFORESTATION failure mode observed in the arena: our trolls parking at base
//! because our reachable region has no fellable tree left (seed supply died).
//!
//! Per game it reports, for player 0:
//!   - idle troll-turns: a troll that issues WAIT or MOVE-to-its-own-cell (parked)
//!   - starved turns: turns where p0 has >0 trolls but ZERO reachable size>=1 plant
//!   - our-plants@end and game length (early end = full deforestation)
//! Usage: cargo run --release --bin stall -- [opp] [seeds]
use std::collections::{HashMap, HashSet, VecDeque};
use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::strategies::roster;

fn bfs(walkable: &HashSet<Cell>, src: Cell) -> HashMap<Cell, i32> {
    let mut dist = HashMap::new();
    let mut q = VecDeque::new();
    dist.insert(src, 0);
    q.push_back(src);
    while let Some((x, y)) = q.pop_front() {
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let n = (x + dx, y + dy);
            if walkable.contains(&n) && !dist.contains_key(&n) {
                dist.insert(n, 0);
                q.push_back(n);
            }
        }
    }
    dist
}

fn reachable_tree(g: &GameState, p: usize) -> bool {
    // union of BFS from each p-troll; is any size>=1 plant reachable?
    let mut reach: HashSet<Cell> = HashSet::new();
    for u in g.units.iter().filter(|u| u.player as usize == p) {
        for c in bfs(&g.walkable, (u.x, u.y)).keys() {
            reach.insert(*c);
        }
    }
    g.plants
        .iter()
        .any(|pl| pl.size >= 1 && reach.contains(&(pl.x, pl.y)))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let opp = args.get(1).cloned().unwrap_or_else(|| "scriptboss".into());
    let seeds: u64 = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(60);

    let bots = roster();
    let a = &*bots[bots.iter().position(|x| x.name() == "goldelite").unwrap()];
    let b = &*bots[bots.iter().position(|x| x.name() == opp).expect("bad opp")];

    let (mut wins, mut wood_sum, mut len_sum, mut idle_sum, mut starve_sum, mut endplants) =
        (0i64, 0i64, 0i64, 0i64, 0i64, 0i64);
    let (mut games, mut starved_games) = (0i64, 0i64);
    for s in 0..seeds {
        let mut g = generate_bronze(s);
        let mut turns_until_end = 0;
        let (mut idle, mut starve, mut turns) = (0i64, 0i64, 0i64);
        for _ in 0..300 {
            let c0 = a.decide(&g, 0);
            // idle proxy: WAIT or MOVE to a troll's own current cell
            for cmd in &c0 {
                let t: Vec<&str> = cmd.split_whitespace().collect();
                if t.first() == Some(&"WAIT") {
                    idle += 1;
                } else if t.first() == Some(&"MOVE") && t.len() >= 4 {
                    if let (Ok(id), Ok(x), Ok(y)) = (
                        t[1].parse::<i32>(),
                        t[2].parse::<i32>(),
                        t[3].parse::<i32>(),
                    ) {
                        if let Some(u) = g.units.iter().find(|u| u.id == id) {
                            if u.x == x && u.y == y {
                                idle += 1;
                            }
                        }
                    }
                }
            }
            if g.units.iter().any(|u| u.player == 0) && !reachable_tree(&g, 0) {
                starve += 1;
            }
            let c1 = b.decide(&g, 1);
            step(&mut g, &c0, &c1);
            turns += 1;
            if has_stalled(&g, &mut turns_until_end) {
                break;
            }
        }
        troll_farm::game::engine::recompute_scores(&mut g);
        games += 1;
        wins += (g.scores[0] > g.scores[1]) as i64;
        wood_sum += g.inventories[0][troll_farm::game::engine::WOOD] as i64;
        len_sum += turns;
        idle_sum += idle;
        starve_sum += starve;
        endplants += g.plants.iter().filter(|p| p.size >= 1).count() as i64;
        if starve > 20 {
            starved_games += 1;
        }
    }
    let n = games as f64;
    println!("goldelite vs {} | {} games", opp, games);
    println!("  winrate     {:>6.0}%", 100.0 * wins as f64 / n);
    println!("  wood(banked){:>7.1}", wood_sum as f64 / n);
    println!("  game_len    {:>7.1} turns", len_sum as f64 / n);
    println!("  idle t-turns{:>7.1}/game", idle_sum as f64 / n);
    println!(
        "  STARVED turns{:>6.1}/game  (turns w/ no reachable tree)",
        starve_sum as f64 / n
    );
    println!(
        "  starved games{:>6} / {}  (>20 starved turns)",
        starved_games, games
    );
    println!("  our plants@end{:>5.1}", endplants as f64 / n);
}
