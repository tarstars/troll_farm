//! Single-game tracer: play botA(p0) vs botB(p1) on one seed and report where
//! player 0 spends its turns -- verb histogram, idle troll-turns (WAIT or
//! move-to-own-cell), and the opening. Reveals execution waste the aggregate
//! diag averages hide. Usage: cargo run --release --bin trace -- [A] [B] [seed]
use std::collections::BTreeMap;
use troll_farm::game::engine::{has_stalled, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::roster;

fn verb(cmd: &str) -> &str {
    cmd.split_whitespace().next().unwrap_or("?")
}

/// ASCII map at the current state: terrain + shacks + trees (lowercase) + trolls
/// (digits = player). Reveals chokepoints/pockets that wedge trolls.
fn render_map(g: &troll_farm::game::state::GameState) {
    println!(
        "--- map @ turn 250 (shack0={:?} shack1={:?}) ---",
        g.shacks[0], g.shacks[1]
    );
    for y in 0..g.height {
        let mut row = String::new();
        for x in 0..g.width {
            let c = (x, y);
            let ch = if let Some(u) = g.units.iter().find(|u| (u.x, u.y) == c) {
                std::char::from_digit(u.player as u32, 10).unwrap()
            } else if g.shacks[0] == c {
                'S'
            } else if g.shacks[1] == c {
                's'
            } else if let Some(p) = g.plants.iter().find(|p| (p.x, p.y) == c) {
                p.plant_type.chars().next().unwrap().to_ascii_lowercase()
            } else if g.iron.contains(&c) {
                '+'
            } else if g.water.contains(&c) {
                '~'
            } else if g.walkable.contains(&c) {
                '.'
            } else {
                '#'
            };
            row.push(ch);
        }
        println!("  {}", row);
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let na = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let nb = args.get(2).cloned().unwrap_or_else(|| "gatherer".into());
    let seed: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(0);
    // which player to inspect (0 = botA, 1 = botB); default 0
    let who: usize = args.get(4).and_then(|s| s.parse().ok()).unwrap_or(0);

    let bots = roster();
    let a = &*bots[bots.iter().position(|x| x.name() == na).expect("bad A")];
    let b = &*bots[bots.iter().position(|x| x.name() == nb).expect("bad B")];

    let mut g = generate_bronze(seed);
    let mut hist: BTreeMap<String, i64> = BTreeMap::new();
    let mut idle_turns: i64 = 0; // troll-turns spent on WAIT or move-to-self
    let mut troll_turns: i64 = 0; // total troll-turns (sum of troll count each turn)
    let mut phase_wait = [0i64; 3]; // WAIT counts in early/mid/late thirds
    let mut turns_until_end = 0;

    let wi = who as i32;
    for t in 0..300 {
        let c0 = a.decide(&g, 0);
        let c1 = b.decide(&g, 1);
        let cw = if who == 0 { &c0 } else { &c1 };

        let nw = g.units.iter().filter(|u| u.player == wi).count() as i64;
        troll_turns += nw;
        for cmd in cw {
            *hist.entry(verb(cmd).to_string()).or_insert(0) += 1;
            let parts: Vec<&str> = cmd.split_whitespace().collect();
            if parts[0] == "WAIT" {
                idle_turns += 1;
            } else if parts[0] == "MOVE" && parts.len() >= 4 {
                if let Ok(id) = parts[1].parse::<i32>() {
                    let (x, y): (i32, i32) = (
                        parts[2].parse().unwrap_or(-1),
                        parts[3].parse().unwrap_or(-1),
                    );
                    if let Some(u) = g.units.iter().find(|u| u.id == id) {
                        if (u.x, u.y) == (x, y) {
                            idle_turns += 1;
                        }
                    }
                }
            }
        }
        // trolls that got NO command at all are also idle
        let commanded: std::collections::HashSet<i32> = cw
            .iter()
            .filter_map(|c| c.split_whitespace().nth(1).and_then(|s| s.parse().ok()))
            .collect();
        idle_turns += g
            .units
            .iter()
            .filter(|u| u.player == wi && !commanded.contains(&u.id))
            .count() as i64;

        if t == 250 {
            render_map(&g);
        }

        let phase = if t < 100 {
            0
        } else if t < 200 {
            1
        } else {
            2
        };
        phase_wait[phase] += cw.iter().filter(|c| c.starts_with("WAIT")).count() as i64;

        if t < 12 || (t >= 200 && t < 212) || t >= 288 {
            println!(
                "t{:<3} s{:<3} n{} | {}",
                t + 1,
                g.scores[who],
                nw,
                cw.join("; ")
            );
        }
        step(&mut g, &c0, &c1);
        if has_stalled(&g, &mut turns_until_end) {
            println!("t{:<3} GAME END: referee stall rule", t + 2);
            break;
        }
    }
    println!(
        "WAITs by phase: early(1-100)={} mid(101-200)={} late(201-300)={}",
        phase_wait[0], phase_wait[1], phase_wait[2]
    );

    let traced = if who == 0 { &na } else { &nb };
    println!("\n--- {} (p{}) over seed {} ---", traced, who, seed);
    println!(
        "final: score {} ({} fruit + {} wood*4), trolls {}",
        g.scores[who],
        g.inventories[who][0..4].iter().sum::<i32>(),
        4 * g.inventories[who][WOOD],
        g.units.iter().filter(|u| u.player == wi).count()
    );
    println!("verb histogram: {:?}", hist);
    println!(
        "idle troll-turns: {}/{} ({:.0}%)",
        idle_turns,
        troll_turns,
        100.0 * idle_turns as f64 / troll_turns.max(1) as f64
    );
}
