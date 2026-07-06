//! R1 EQUALITY HARNESS (docs/refactor-goal.md): prove the refactored bot behaves EXACTLY
//! like the frozen v1.20.0 baseline. Drives two compiled BOT BINARIES through the CG
//! stdin/stdout protocol over the same simulated games and asserts identical per-turn
//! command lines. Black-box: covers parsing + decision + formatting, i.e. the whole
//! artifact. Referee-fidelity of listing order is NOT required — both bots see the same
//! serializer, so any self-consistent order is a valid equality probe.
//!
//! The bot's protocol (mirrored from main.rs): header `width height` + `height` grid rows
//! ('0' my shack, '1' opp shack, '.' walkable, '+' iron, '~' water, '#' rock); per turn:
//! my inventory (6 ints), opp inventory (6 ints), tree count + `TYPE x y size health
//! fruits cooldown` each, troll count + `id player x y ms cc hp chop carry0..5` each
//! (player 0 = the bot). Output: one `;`-joined line of commands per turn.
//!
//! Usage: equality <botA> <botB> <seeds> [max_turns=300]
//!   Plays every seed with the bot in BOTH seats (opponent = roster "goldelite", falling
//!   back to "silverboss"). Reports the first divergence (seed/seat/turn + both lines) and
//!   a summary. Exit code 0 iff all games identical.

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdout, Command, Stdio};
use troll_farm::game::engine::step;
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;

struct Bot {
    child: Child,
}

impl Bot {
    fn spawn(path: &str) -> Bot {
        let child = Command::new(path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .unwrap_or_else(|e| panic!("cannot spawn bot {path}: {e}"));
        Bot { child }
    }
    fn send(&mut self, s: &str) {
        let stdin = self.child.stdin.as_mut().unwrap();
        stdin.write_all(s.as_bytes()).unwrap();
        stdin.flush().unwrap();
    }
}

impl Drop for Bot {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn grid_rows(g: &GameState, seat: usize) -> Vec<String> {
    (0..g.height)
        .map(|y| {
            (0..g.width)
                .map(|x| {
                    let c = (x, y);
                    if c == g.shacks[seat] {
                        '0'
                    } else if c == g.shacks[1 - seat] {
                        '1'
                    } else if g.iron.contains(&c) {
                        '+'
                    } else if g.water.contains(&c) {
                        '~'
                    } else if g.walkable.contains(&c) {
                        '.'
                    } else {
                        '#'
                    }
                })
                .collect()
        })
        .collect()
}

fn turn_block(g: &GameState, seat: usize) -> String {
    let mut s = String::new();
    let me = &g.inventories[seat];
    let op = &g.inventories[1 - seat];
    s.push_str(&format!("{} {} {} {} {} {}\n", me[0], me[1], me[2], me[3], me[4], me[5]));
    s.push_str(&format!("{} {} {} {} {} {}\n", op[0], op[1], op[2], op[3], op[4], op[5]));
    s.push_str(&format!("{}\n", g.plants.len()));
    for p in &g.plants {
        s.push_str(&format!(
            "{} {} {} {} {} {} {}\n",
            p.plant_type, p.x, p.y, p.size, p.health, p.fruits, p.cooldown
        ));
    }
    s.push_str(&format!("{}\n", g.units.len()));
    for u in &g.units {
        let rel = if u.player as usize == seat { 0 } else { 1 };
        s.push_str(&format!(
            "{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n",
            u.id, rel, u.x, u.y, u.ms, u.cc, u.hp, u.chop,
            u.carry[0], u.carry[1], u.carry[2], u.carry[3], u.carry[4], u.carry[5]
        ));
    }
    s
}

/// Read one command line from a bot; None = crash/EOF.
fn read_cmds(reader: &mut BufReader<ChildStdout>) -> Option<String> {
    let mut line = String::new();
    if reader.read_line(&mut line).unwrap_or(0) == 0 {
        None
    } else {
        Some(line.trim_end().to_string())
    }
}

/// Play one game: `bot_path` in `seat`; the opponent is either another bot binary
/// (`opp_path` = path, deterministic by the same fixes) or the scripted "WAIT" bot.
/// A lib strategy is NOT used: roster strategies carry their own per-process HashSet
/// nondeterminism, which would break equality even for a deterministic bot.
/// Returns the bot's per-turn command lines (empty line marks a read failure / crash).
fn play(bot_path: &str, opp_path: &str, seed: u64, seat: usize, max_turns: i32) -> Vec<String> {
    let mut g = generate_bronze(seed);
    let mut bot = Bot::spawn(bot_path);
    let rows = grid_rows(&g, seat);
    bot.send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n")));
    let mut reader = BufReader::new(bot.child.stdout.take().unwrap());

    let mut opp = if opp_path == "WAIT" { None } else { Some(Bot::spawn(opp_path)) };
    let mut opp_reader = opp.as_mut().map(|o| {
        let rows = grid_rows(&g, 1 - seat);
        o.send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n")));
        BufReader::new(o.child.stdout.take().unwrap())
    });

    let mut lines = Vec::new();
    for _ in 0..max_turns {
        bot.send(&turn_block(&g, seat));
        let Some(line) = read_cmds(&mut reader) else {
            lines.push(String::new());
            break;
        };
        let bot_cmds: Vec<String> = line.split(';').map(|s| s.to_string()).collect();
        let opp_cmds: Vec<String> = match (&mut opp, &mut opp_reader) {
            (Some(o), Some(r)) => {
                o.send(&turn_block(&g, 1 - seat));
                match read_cmds(r) {
                    Some(l) => l.split(';').map(|s| s.to_string()).collect(),
                    None => vec!["WAIT".to_string()],
                }
            }
            _ => vec!["WAIT".to_string()],
        };
        if seat == 0 {
            step(&mut g, &bot_cmds, &opp_cmds);
        } else {
            step(&mut g, &opp_cmds, &bot_cmds);
        }
        lines.push(line);
        if g.plants.is_empty() {
            break; // real referee ends the game with no plants
        }
    }
    lines
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 4 {
        eprintln!("usage: equality <botA> <botB> <seeds> [max_turns=300] [opp=WAIT|<path>]");
        std::process::exit(2);
    }
    let (bot_a, bot_b) = (&args[1], &args[2]);
    let seeds: u64 = args[3].parse().unwrap();
    let max_turns: i32 = args.get(4).map(|s| s.parse().unwrap()).unwrap_or(300);
    let opp = args.get(5).cloned().unwrap_or_else(|| "WAIT".to_string());

    let mut games = 0u64;
    let mut divergent = 0u64;
    for seed in 0..seeds {
        for seat in 0..2usize {
            let la = play(bot_a, &opp, seed, seat, max_turns);
            let lb = play(bot_b, &opp, seed, seat, max_turns);
            games += 1;
            if la != lb {
                divergent += 1;
                let t = la
                    .iter()
                    .zip(lb.iter())
                    .position(|(a, b)| a != b)
                    .unwrap_or_else(|| la.len().min(lb.len()));
                eprintln!("DIVERGE seed={seed} seat={seat} turn={} ({} vs {} turns)", t + 1, la.len(), lb.len());
                eprintln!("  A: {}", la.get(t).map(String::as_str).unwrap_or("<none>"));
                eprintln!("  B: {}", lb.get(t).map(String::as_str).unwrap_or("<none>"));
                if divergent >= 5 {
                    eprintln!("(stopping after 5 divergences)");
                    println!("NOT EQUAL: {divergent}+ of {games} games diverged");
                    std::process::exit(1);
                }
            }
        }
        if (seed + 1) % 50 == 0 {
            eprintln!("  … {} seeds done ({} games), divergent so far: {}", seed + 1, games, divergent);
        }
    }
    if divergent == 0 {
        println!("EQUAL: {games} games ({seeds} seeds x 2 seats), all command streams identical");
    } else {
        println!("NOT EQUAL: {divergent} of {games} games diverged");
        std::process::exit(1);
    }
}
