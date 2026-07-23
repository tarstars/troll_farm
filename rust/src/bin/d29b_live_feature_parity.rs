mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    mod live_features {
        include!("../d29b_live_features.rs");
    }

    fn feature_row(seed: u64, seat: usize, opponent_index: usize) -> String {
        let mut game = generate_bronze(seed);
        let mut resident = SecureOrchardBot::new();
        let opponent = OPPONENTS[opponent_index].1();
        let mut history = live_features::History::new();
        let mut stall_counter = 0;
        let mut reached = true;
        loop {
            let view = yamo_view(&game, seat);
            history.observe(&view);
            if game.turn == 75 {
                let scalars = history.scalars().expect("complete D29b history");
                let grid = live_features::spatial(&view);
                return format!(
                    "{}\t{}\t{}\t{}\t{}\t{}\t{}",
                    seed,
                    seat,
                    OPPONENTS[opponent_index].0,
                    usize::from(reached),
                    scalars
                        .iter()
                        .map(f32::to_string)
                        .collect::<Vec<_>>()
                        .join(","),
                    live_features::spatial_hash(&grid),
                    grid.iter()
                        .map(i16::to_string)
                        .collect::<Vec<_>>()
                        .join(","),
                );
            }
            if game.turn > 300 {
                reached = false;
                panic!("D29b feature parity did not reach turn 75");
            }
            let ours = resident.commands(&view);
            let theirs = opponent.decide(&game, 1 - seat);
            apply_commands(&mut game, seat, &ours, &theirs);
            if has_stalled(&game, &mut stall_counter) {
                reached = false;
                panic!("D29b feature parity stalled before turn 75");
            }
        }
    }

    pub fn run() {
        let args: Vec<String> = std::env::args().collect();
        let seed_start = args.get(1).map_or(0, |value| value.parse().unwrap());
        let seed_count = args.get(2).map_or(5, |value| value.parse().unwrap());
        let output = args
            .get(3)
            .cloned()
            .unwrap_or_else(|| "d29b-live-features.tsv".to_string());
        let mut rows = Vec::new();
        for seed in seed_start..seed_start + seed_count {
            for seat in 0..2 {
                for opponent in 0..OPPONENTS.len() {
                    rows.push(feature_row(seed, seat, opponent));
                }
            }
        }
        let mut writer = BufWriter::new(File::create(output).unwrap());
        writeln!(
            writer,
            "seed\tseat\topponent\treached_cut\tscalars\tgrid_hash\tgrid"
        )
        .unwrap();
        for row in rows {
            writeln!(writer, "{row}").unwrap();
        }
    }
}

pub use base::{bot, game};

fn main() {
    base::run();
}
