#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

mod live_features {
    include!("../d29b_live_features.rs");
}

mod critic {
    include!("../../../data/analysis/live-agent-6553250/d29b-option-critic-rust-kernel-only-2026-07-20.rs");

    pub fn predict(
        grid: &[i16; super::live_features::GRID_COUNT],
        scalars: &[f32; super::live_features::SCALAR_COUNT],
    ) -> (f32, f32) {
        let mut row = Vec::with_capacity(2 * grid.len() + 4 * scalars.len());
        for value in grid {
            row.extend_from_slice(&value.to_le_bytes());
        }
        for value in scalars {
            row.extend_from_slice(&value.to_le_bytes());
        }
        Critic::new().forward(&row)
    }
}

use game::protocol::{read_static_map, read_turn};
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
            let scalars = history.scalars().expect("complete D29c history");
            let grid = live_features::spatial(&view);
            let (normalized, raw) = critic::predict(&grid, &scalars);
            let workers = view.units.iter().filter(|unit| unit.player == 0).count();
            println!(
                "{{\"turn\":75,\"workers\":{},\"finite\":{},\"normalized_prediction\":{:.9},\"raw_prediction\":{:.9},\"switch\":{},\"grid_hash\":{}}}",
                workers,
                normalized.is_finite() && raw.is_finite() && scalars.iter().all(|value| value.is_finite()),
                normalized,
                raw,
                usize::from(workers == 2 && raw > 4.0),
                live_features::spatial_hash(&grid),
            );
            return;
        }
        turn += 1;
    }
}
