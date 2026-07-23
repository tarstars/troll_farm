//! Forced 300-turn, both-seat process safety screen for the frozen D11 live source.

use std::collections::BTreeSet;
use std::io::{BufRead, BufReader, Read, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};

use troll_farm::game::engine::step;
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;

struct Bot {
    child: Child,
    input: Option<ChildStdin>,
    output: BufReader<ChildStdout>,
}

impl Bot {
    fn spawn(path: &str) -> Self {
        let mut child = Command::new(path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap_or_else(|error| panic!("cannot spawn {path}: {error}"));
        Self {
            input: Some(child.stdin.take().expect("child stdin")),
            output: BufReader::new(child.stdout.take().expect("child stdout")),
            child,
        }
    }

    fn send(&mut self, text: &str) {
        let input = self.input.as_mut().expect("open stdin");
        input.write_all(text.as_bytes()).expect("write input");
        input.flush().expect("flush input");
    }

    fn receive(&mut self) -> Option<String> {
        let mut line = String::new();
        (self.output.read_line(&mut line).ok()? != 0)
            .then(|| line.trim_end_matches(['\n', '\r']).to_string())
    }

    fn finish(mut self) -> (i32, String) {
        drop(self.input.take());
        let status = self.child.wait().expect("wait child");
        let mut stderr = String::new();
        self.child
            .stderr
            .take()
            .expect("stderr")
            .read_to_string(&mut stderr)
            .expect("read stderr");
        (status.code().unwrap_or(-1), stderr)
    }
}

fn grid(game: &GameState, seat: usize) -> String {
    let rows: Vec<String> = (0..game.height)
        .map(|y| {
            (0..game.width)
                .map(|x| {
                    let cell = (x, y);
                    if cell == game.shacks[seat] {
                        '0'
                    } else if cell == game.shacks[1 - seat] {
                        '1'
                    } else if game.iron.contains(&cell) {
                        '+'
                    } else if game.water.contains(&cell) {
                        '~'
                    } else if game.walkable.contains(&cell) {
                        '.'
                    } else {
                        '#'
                    }
                })
                .collect()
        })
        .collect();
    format!("{} {}\n{}\n", game.width, game.height, rows.join("\n"))
}

fn turn_block(game: &GameState, seat: usize) -> String {
    let mut text = String::new();
    for player in [seat, 1 - seat] {
        let inv = game.inventories[player];
        text.push_str(&format!(
            "{} {} {} {} {} {}\n",
            inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]
        ));
    }
    text.push_str(&format!("{}\n", game.plants.len()));
    for plant in &game.plants {
        text.push_str(&format!(
            "{} {} {} {} {} {} {}\n",
            plant.plant_type,
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown
        ));
    }
    text.push_str(&format!("{}\n", game.units.len()));
    for unit in &game.units {
        let player = usize::from(unit.player as usize != seat);
        text.push_str(&format!(
            "{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n",
            unit.id,
            player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
            unit.carry[0],
            unit.carry[1],
            unit.carry[2],
            unit.carry[3],
            unit.carry[4],
            unit.carry[5]
        ));
    }
    text
}

fn validate(line: &str, game: &GameState, seat: usize) -> Result<(), String> {
    if line.is_empty() {
        return Err("empty command line".to_string());
    }
    let own_ids: BTreeSet<i32> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .map(|unit| unit.id)
        .collect();
    let mut action_count = 0usize;
    let mut explicit_ids = BTreeSet::new();
    let mut trains = 0usize;
    for command in line.split(';') {
        let fields: Vec<&str> = command.split_whitespace().collect();
        let Some(verb) = fields.first().copied() else {
            return Err("empty command".to_string());
        };
        match verb {
            "TRAIN" => {
                trains += 1;
                if fields != ["TRAIN", "2", "2", "0", "2"] {
                    return Err(format!("invalid TRAIN {command:?}"));
                }
            }
            "WAIT" => {
                if fields.len() != 1 {
                    return Err(format!("invalid WAIT {command:?}"));
                }
                action_count += 1;
            }
            "MOVE" => {
                if fields.len() != 4
                    || fields[2].parse::<i32>().is_err()
                    || fields[3].parse::<i32>().is_err()
                {
                    return Err(format!("invalid MOVE {command:?}"));
                }
                let id: i32 = fields[1]
                    .parse()
                    .map_err(|_| format!("invalid id {command:?}"))?;
                if !own_ids.contains(&id) || !explicit_ids.insert(id) {
                    return Err(format!("invalid/duplicate unit id {command:?}"));
                }
                action_count += 1;
            }
            "HARVEST" | "CHOP" | "DROP" | "MINE" => {
                if fields.len() != 2 {
                    return Err(format!("invalid action {command:?}"));
                }
                let id: i32 = fields[1]
                    .parse()
                    .map_err(|_| format!("invalid id {command:?}"))?;
                if !own_ids.contains(&id) || !explicit_ids.insert(id) {
                    return Err(format!("invalid/duplicate unit id {command:?}"));
                }
                action_count += 1;
            }
            "PLANT" | "PICK" => {
                if fields.len() != 3 || !["PLUM", "LEMON", "APPLE", "BANANA"].contains(&fields[2]) {
                    return Err(format!("invalid fruit action {command:?}"));
                }
                let id: i32 = fields[1]
                    .parse()
                    .map_err(|_| format!("invalid id {command:?}"))?;
                if !own_ids.contains(&id) || !explicit_ids.insert(id) {
                    return Err(format!("invalid/duplicate unit id {command:?}"));
                }
                action_count += 1;
            }
            _ => return Err(format!("unknown command {command:?}")),
        }
    }
    if trains > 1 || action_count != own_ids.len() {
        return Err(format!(
            "trains={trains}, actions={action_count}, own_units={}",
            own_ids.len()
        ));
    }
    Ok(())
}

fn fail(seed: u64, seat: usize, turn: usize, message: impl AsRef<str>) -> ! {
    eprintln!(
        "D11 live safety failure seed={seed} seat={seat} turn={turn}: {}",
        message.as_ref()
    );
    std::process::exit(1);
}

fn play(binary: &str, seed: u64, seat: usize) -> (usize, usize) {
    let mut game = generate_bronze(seed);
    let mut bot = Bot::spawn(binary);
    bot.send(&grid(&game, seat));
    let mut lines = 0usize;
    let mut maximum_workers = 0usize;
    for turn in 1..=300usize {
        maximum_workers = maximum_workers.max(
            game.units
                .iter()
                .filter(|unit| unit.player as usize == seat)
                .count(),
        );
        bot.send(&turn_block(&game, seat));
        let line = bot
            .receive()
            .unwrap_or_else(|| fail(seed, seat, turn, "child EOF"));
        validate(&line, &game, seat).unwrap_or_else(|error| fail(seed, seat, turn, error));
        let commands: Vec<String> = line.split(';').map(str::to_string).collect();
        let waiting = vec!["WAIT".to_string()];
        if seat == 0 {
            step(&mut game, &commands, &waiting);
        } else {
            step(&mut game, &waiting, &commands);
        }
        lines += 1;
    }
    let (code, stderr) = bot.finish();
    if code != 0 || !stderr.is_empty() {
        fail(seed, seat, 300, format!("exit={code}, stderr={stderr:?}"));
    }
    (lines, maximum_workers)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: d11_live_safety <live-binary>");
        std::process::exit(2);
    }
    let mut games = 0usize;
    let mut lines = 0usize;
    let mut minimum_lines = usize::MAX;
    let mut maximum_workers = 0usize;
    for seed in 0..16u64 {
        for seat in 0..2usize {
            let (game_lines, workers) = play(&args[1], seed, seat);
            games += 1;
            lines += game_lines;
            minimum_lines = minimum_lines.min(game_lines);
            maximum_workers = maximum_workers.max(workers);
        }
    }
    println!(
        "{{\"pass\":true,\"games\":{},\"total_lines\":{},\"minimum_lines_per_game\":{},\"maximum_own_workers\":{},\"stderr_failures\":0,\"syntax_failures\":0}}",
        games, lines, minimum_lines, maximum_workers
    );
}
