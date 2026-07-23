#![allow(dead_code, unused_imports)]

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

#[path = "../norxondor_three_worker_live_bot.rs"]
mod norxondor_three_worker_live_bot;

use game::protocol::{read_static_map, read_turn};
use norxondor_three_worker_live_bot::NorxondorThreeWorkerBot;
use std::io::{self, Write};

fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());
    let Some(map) = read_static_map(&mut reader) else {
        return;
    };
    let mut bot = NorxondorThreeWorkerBot::new();
    let mut turn = 1;
    while let Some(view) = read_turn(&mut reader, &map, turn) {
        let commands = bot.commands(&view);
        writeln!(out, "{}", commands.join(";")).expect("write command line");
        out.flush().expect("flush command line");
        turn += 1;
    }
}
