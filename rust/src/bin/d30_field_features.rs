#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

mod live_features {
    include!("../d29b_live_features.rs");
}

use game::protocol::{read_static_map, read_turn};
use std::fmt::Write as _;
use std::io;

fn main() {
    let stdin = io::stdin();
    let mut reader = io::BufReader::new(stdin.lock());
    let Some(map) = read_static_map(&mut reader) else {
        return;
    };
    let mut history = live_features::History::new();
    let mut turn = 1;
    while let Some(view) = read_turn(&mut reader, &map, turn) {
        history.observe(&view);
        if turn == 75 {
            let scalars = history.scalars().expect("complete D30 history");
            let grid = live_features::spatial(&view);
            let workers = view.units.iter().filter(|unit| unit.player == 0).count();
            let mut output = String::with_capacity(32_768);
            write!(
                output,
                "{{\"turn\":75,\"workers\":{},\"grid_hash\":{},\"scalars\":[",
                workers,
                live_features::spatial_hash(&grid),
            )
            .unwrap();
            for (index, value) in scalars.iter().enumerate() {
                if index != 0 {
                    output.push(',');
                }
                write!(output, "{}", value).unwrap();
            }
            output.push_str("],\"grid\":[");
            for (index, value) in grid.iter().enumerate() {
                if index != 0 {
                    output.push(',');
                }
                write!(output, "{}", value).unwrap();
            }
            output.push_str("]}");
            println!("{output}");
            return;
        }
        turn += 1;
    }
}
