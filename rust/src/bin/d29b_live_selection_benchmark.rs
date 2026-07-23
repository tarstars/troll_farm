mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    mod live_features {
        include!("../d29b_live_features.rs");
    }

    mod critic {
        include!("../../../data/analysis/live-agent-6553250/d29b-option-critic-rust-kernel-only-2026-07-20.rs");

        pub fn predict(
            grid: &[i16; super::live_features::GRID_COUNT],
            scalars: &[f32; super::live_features::SCALAR_COUNT],
        ) -> f32 {
            let mut row = Vec::with_capacity(2 * grid.len() + 4 * scalars.len());
            for value in grid {
                row.extend_from_slice(&value.to_le_bytes());
            }
            for value in scalars {
                row.extend_from_slice(&value.to_le_bytes());
            }
            Critic::new().forward(&row).1
        }
    }

    fn sample(
        seed: u64,
        seat: usize,
        opponent_index: usize,
    ) -> (live_features::History, YamoState) {
        let mut game = generate_bronze(seed);
        let mut resident = SecureOrchardBot::new();
        let opponent = OPPONENTS[opponent_index].1();
        let mut history = live_features::History::new();
        let mut stall_counter = 0;
        while game.turn < 75 {
            let view = yamo_view(&game, seat);
            history.observe(&view);
            let ours = resident.commands(&view);
            let theirs = opponent.decide(&game, 1 - seat);
            apply_commands(&mut game, seat, &ours, &theirs);
            assert!(!has_stalled(&game, &mut stall_counter));
        }
        (history, yamo_view(&game, seat))
    }

    fn selection(history: &mut live_features::History, view: &YamoState) -> f32 {
        history.observe(view);
        let scalars = history.scalars().unwrap();
        let grid = live_features::spatial(view);
        critic::predict(&grid, &scalars)
    }

    pub fn benchmark() {
        let args: Vec<String> = std::env::args().collect();
        let seed_start = args.get(1).map_or(53600, |value| value.parse().unwrap());
        let seed_count = args.get(2).map_or(20, |value| value.parse().unwrap());
        let iterations = args.get(3).map_or(1000, |value| value.parse().unwrap());
        let mut samples: Vec<_> = (seed_start..seed_start + seed_count)
            .flat_map(|seed| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent| sample(seed, seat, opponent))
                })
            })
            .collect();
        let mut checksum = 0u64;
        let sample_count = samples.len();
        for index in 0..16 {
            let (history, view) = &mut samples[index % sample_count];
            checksum ^= u64::from(selection(history, view).to_bits());
        }
        let mut durations = Vec::with_capacity(iterations);
        for index in 0..iterations {
            let (history, view) = &mut samples[index % sample_count];
            let started = Instant::now();
            let raw = selection(history, view);
            durations.push(started.elapsed().as_nanos() as u64);
            checksum = checksum.wrapping_add(u64::from(raw.to_bits()));
        }
        durations.sort_unstable();
        let median = durations[durations.len() / 2];
        let p95 = durations[((durations.len() * 95 + 99) / 100).saturating_sub(1)];
        let maximum = *durations.last().unwrap();
        println!(
            "{{\"samples\":{},\"iterations\":{},\"warmup\":16,\"median_ns\":{},\"p95_ns\":{},\"maximum_ns\":{},\"checksum\":{}}}",
            samples.len(), iterations, median, p95, maximum, checksum
        );
    }
}

pub use base::{bot, game};

fn main() {
    base::benchmark();
}
