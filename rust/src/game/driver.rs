//! Shared black-box game driver: spawns bot BINARIES and speaks the CG stdin/stdout
//! protocol over simulated games (real `engine::step`, real `generate_bronze` maps).
//! Consumers: bin/equality.rs (exactness assertions), bin/playmatch.rs (scored matches).
//! Extracted verbatim from bin/equality.rs on 2026-07-11 (see that file's doc comment
//! for the protocol description). One deliberate change: `Bot::send` is fallible so a
//! crashed bot can be FLAGGED instead of panicking (equality call sites `.unwrap()`).

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdout, Command, Stdio};

use crate::game::engine::{recompute_scores, step, WOOD};
use crate::game::mapgen::generate_bronze;
use crate::game::state::GameState;

pub struct Bot {
    pub child: Child,
}

impl Bot {
    pub fn spawn(path: &str) -> Bot {
        let child = Command::new(path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .unwrap_or_else(|e| panic!("cannot spawn bot {path}: {e}"));
        Bot { child }
    }
    pub fn send(&mut self, s: &str) -> std::io::Result<()> {
        let stdin = self.child.stdin.as_mut().unwrap();
        stdin.write_all(s.as_bytes())?;
        stdin.flush()
    }
}

impl Drop for Bot {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

pub fn grid_rows(g: &GameState, seat: usize) -> Vec<String> {
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

pub fn turn_block(g: &GameState, seat: usize) -> String {
    let mut s = String::new();
    let me = &g.inventories[seat];
    let op = &g.inventories[1 - seat];
    s.push_str(&format!(
        "{} {} {} {} {} {}\n",
        me[0], me[1], me[2], me[3], me[4], me[5]
    ));
    s.push_str(&format!(
        "{} {} {} {} {} {}\n",
        op[0], op[1], op[2], op[3], op[4], op[5]
    ));
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
            u.id,
            rel,
            u.x,
            u.y,
            u.ms,
            u.cc,
            u.hp,
            u.chop,
            u.carry[0],
            u.carry[1],
            u.carry[2],
            u.carry[3],
            u.carry[4],
            u.carry[5]
        ));
    }
    s
}

/// Read one command line from a bot; None = crash/EOF.
pub fn read_cmds(reader: &mut BufReader<ChildStdout>) -> Option<String> {
    let mut line = String::new();
    if reader.read_line(&mut line).unwrap_or(0) == 0 {
        None
    } else {
        Some(line.trim_end().to_string())
    }
}

/// Play one game: `bot_path` in `seat`; opponent = another binary (deterministic by the
/// same fixes) or the scripted "WAIT" bot. A lib strategy is NOT used: roster strategies
/// carry their own per-process HashSet nondeterminism, which would break equality even for
/// a deterministic bot. Returns the bot's per-turn command lines (empty line marks a read
/// failure). (Equality semantics — verbatim from the pre-extraction equality.rs at cec35bf,
/// with the four internal `send` calls suffixed `.unwrap()`.)
pub fn play(bot_path: &str, opp_path: &str, seed: u64, seat: usize, max_turns: i32) -> Vec<String> {
    let mut g = generate_bronze(seed);
    let mut bot = Bot::spawn(bot_path);
    let rows = grid_rows(&g, seat);
    bot.send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n"))).unwrap();
    let mut reader = BufReader::new(bot.child.stdout.take().unwrap());

    let mut opp = if opp_path == "WAIT" {
        None
    } else {
        Some(Bot::spawn(opp_path))
    };
    let mut opp_reader = opp.as_mut().map(|o| {
        let rows = grid_rows(&g, 1 - seat);
        o.send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n"))).unwrap();
        BufReader::new(o.child.stdout.take().unwrap())
    });

    let mut lines = Vec::new();
    for _ in 0..max_turns {
        bot.send(&turn_block(&g, seat)).unwrap();
        let Some(line) = read_cmds(&mut reader) else {
            lines.push(String::new());
            break;
        };
        let bot_cmds: Vec<String> = line.split(';').map(|s| s.to_string()).collect();
        let opp_cmds: Vec<String> = match (&mut opp, &mut opp_reader) {
            (Some(o), Some(r)) => {
                o.send(&turn_block(&g, 1 - seat)).unwrap();
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

pub struct MatchResult {
    pub turns: i32,
    pub scores: [i32; 2],
    pub fruit: [i32; 2],
    pub wood: [i32; 2],
    pub crashed: [bool; 2],
}

struct Side {
    bot: Option<Bot>,
    reader: Option<BufReader<ChildStdout>>,
    crashed: bool,
}

/// One scored match on `generate_bronze(seed)`: bot0 = player 0, bot1 = player 1.
/// "WAIT" = scripted do-nothing side. A side that crashes (send/read failure) plays
/// WAIT for the remainder and is FLAGGED. Early end when no plants remain (mirrors the
/// referee, same rule as `play`).
pub fn play_match(bot0_path: &str, bot1_path: &str, seed: u64, max_turns: i32) -> MatchResult {
    let mut g = generate_bronze(seed);
    let mut sides: Vec<Side> = Vec::new();
    for (i, path) in [bot0_path, bot1_path].iter().enumerate() {
        if *path == "WAIT" {
            sides.push(Side { bot: None, reader: None, crashed: false });
        } else {
            let mut b = Bot::spawn(path);
            let rows = grid_rows(&g, i);
            let header_ok = b
                .send(&format!("{} {}\n{}\n", g.width, g.height, rows.join("\n")))
                .is_ok();
            let reader = BufReader::new(b.child.stdout.take().unwrap());
            sides.push(Side { bot: Some(b), reader: Some(reader), crashed: !header_ok });
        }
    }
    let mut turns = 0;
    for _ in 0..max_turns {
        let mut cmds: [Vec<String>; 2] = [vec!["WAIT".to_string()], vec!["WAIT".to_string()]];
        for i in 0..2 {
            let blk = turn_block(&g, i);
            let side = &mut sides[i];
            if side.crashed || side.bot.is_none() {
                continue;
            }
            if side.bot.as_mut().unwrap().send(&blk).is_err() {
                side.crashed = true;
                continue;
            }
            match read_cmds(side.reader.as_mut().unwrap()) {
                Some(l) => cmds[i] = l.split(';').map(|s| s.to_string()).collect(),
                None => side.crashed = true,
            }
        }
        step(&mut g, &cmds[0], &cmds[1]);
        turns += 1;
        if g.plants.is_empty() {
            break;
        }
    }
    recompute_scores(&mut g);
    let fruit = |p: usize| {
        let inv = &g.inventories[p];
        inv[0] + inv[1] + inv[2] + inv[3]
    };
    MatchResult {
        turns,
        scores: [g.scores[0], g.scores[1]],
        fruit: [fruit(0), fruit(1)],
        wood: [g.inventories[0][WOOD], g.inventories[1][WOOD]],
        crashed: [sides[0].crashed, sides[1].crashed],
    }
}
