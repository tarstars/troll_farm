mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    mod live_features {
        include!("../d29b_live_features.rs");
    }

    mod exact_farm {
        include!("../d29b_exact_farm.rs");
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

    use exact_farm::ExactFarm;

    struct Controller {
        resident: SecureOrchardBot,
        history: live_features::History,
        farm: ExactFarm,
        switched: bool,
        prediction: Option<(f32, f32)>,
    }

    impl Controller {
        fn new() -> Self {
            Self {
                resident: SecureOrchardBot::new(),
                history: live_features::History::new(),
                farm: ExactFarm::new(),
                switched: false,
                prediction: None,
            }
        }

        fn commands(&mut self, view: &YamoState) -> Vec<String> {
            self.history.observe(view);
            if view.turn == 75 && view.units.iter().filter(|unit| unit.player == 0).count() == 2 {
                let scalars = self.history.scalars().expect("complete D29b history");
                let grid = live_features::spatial(view);
                let prediction = critic::predict(&grid, &scalars);
                self.switched = prediction.1 > 4.0;
                self.prediction = Some(prediction);
            }
            if self.switched {
                self.farm.commands(view)
            } else {
                self.resident.commands(view)
            }
        }
    }

    #[derive(Clone, Copy)]
    struct IntegratedTask {
        seed: u64,
        seat: usize,
        opponent_index: usize,
    }

    struct IntegratedResult {
        task: IntegratedTask,
        reached_cut: bool,
        normalized: f32,
        raw: f32,
        switched: bool,
        turns: usize,
        commands: usize,
        final_turn: i32,
        margin: i32,
        my_score: i32,
        opponent_score: i32,
        command_hash: u64,
        selection_ns: u128,
        mismatch: Option<String>,
    }

    fn integrated_parity(task: IntegratedTask) -> IntegratedResult {
        let mut game = generate_bronze(task.seed);
        let mut controller = Controller::new();
        let mut resident = SecureOrchardBot::new();
        let original_farm = OwnershipAwareFarm::new();
        let opponent = OPPONENTS[task.opponent_index].1();
        let mut reached_cut = false;
        let mut stall_counter = 0;
        let mut turns = 0;
        let mut commands = 0;
        let mut command_hash = FNV_OFFSET;
        let mut selection_ns = 0;
        let mut mismatch = None;
        while game.turn <= 300 {
            let view = yamo_view(&game, task.seat);
            let selection_started = (game.turn == 75).then(Instant::now);
            let actual = controller.commands(&view);
            if let Some(started) = selection_started {
                selection_ns = started.elapsed().as_nanos();
            }
            if game.turn == 75 {
                reached_cut = true;
            }
            let expected = if controller.switched {
                original_farm.decide(&game, task.seat)
            } else {
                resident.commands(&view)
            };
            if actual != expected {
                mismatch = Some(format!(
                    "turn={} switched={} expected={:?} actual={:?}",
                    game.turn, controller.switched, expected, actual
                ));
                break;
            }
            turns += 1;
            commands += actual.len();
            if game.turn >= 75 {
                trace_commands(&mut command_hash, &actual);
            }
            let theirs = opponent.decide(&game, 1 - task.seat);
            apply_commands(&mut game, task.seat, &actual, &theirs);
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
        let (normalized, raw) = controller.prediction.unwrap_or((f32::NAN, f32::NAN));
        IntegratedResult {
            task,
            reached_cut,
            normalized,
            raw,
            switched: controller.switched,
            turns,
            commands,
            final_turn: game.turn,
            margin: game.scores[task.seat] - game.scores[1 - task.seat],
            my_score: game.scores[task.seat],
            opponent_score: game.scores[1 - task.seat],
            command_hash,
            selection_ns,
            mismatch,
        }
    }

    fn write_protocol_fixture(
        seed: u64,
        seat: usize,
        opponent_index: usize,
        input_path: &str,
        expected_path: &str,
    ) {
        let mut game = generate_bronze(seed);
        let mut controller = Controller::new();
        let opponent = OPPONENTS[opponent_index].1();
        let mut input = BufWriter::new(File::create(input_path).unwrap());
        let mut expected = BufWriter::new(File::create(expected_path).unwrap());
        writeln!(input, "{} {}", game.width, game.height).unwrap();
        for y in 0..game.height {
            let row: String = (0..game.width)
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
                .collect();
            writeln!(input, "{row}").unwrap();
        }
        let mut stall_counter = 0;
        while game.turn <= 300 {
            for player in [seat, 1 - seat] {
                writeln!(
                    input,
                    "{}",
                    game.inventories[player]
                        .iter()
                        .map(i32::to_string)
                        .collect::<Vec<_>>()
                        .join(" ")
                )
                .unwrap();
            }
            writeln!(input, "{}", game.plants.len()).unwrap();
            for plant in &game.plants {
                writeln!(
                    input,
                    "{} {} {} {} {} {} {}",
                    plant.plant_type,
                    plant.x,
                    plant.y,
                    plant.size,
                    plant.health,
                    plant.fruits,
                    plant.cooldown
                )
                .unwrap();
            }
            writeln!(input, "{}", game.units.len()).unwrap();
            for unit in &game.units {
                let player = usize::from(unit.player as usize != seat);
                writeln!(
                    input,
                    "{} {} {} {} {} {} {} {} {}",
                    unit.id,
                    player,
                    unit.x,
                    unit.y,
                    unit.ms,
                    unit.cc,
                    unit.hp,
                    unit.chop,
                    unit.carry
                        .iter()
                        .map(i32::to_string)
                        .collect::<Vec<_>>()
                        .join(" ")
                )
                .unwrap();
            }
            let ours = controller.commands(&yamo_view(&game, seat));
            writeln!(expected, "{}", ours.join(";")).unwrap();
            let theirs = opponent.decide(&game, 1 - seat);
            apply_commands(&mut game, seat, &ours, &theirs);
            if has_stalled(&game, &mut stall_counter) {
                break;
            }
        }
        input.flush().unwrap();
        expected.flush().unwrap();
        eprintln!(
            "fixture seed={seed} seat={seat} opponent={} switched={} prediction={:?}",
            OPPONENTS[opponent_index].0, controller.switched, controller.prediction
        );
    }

    pub fn run_integrated() {
        let args: Vec<String> = std::env::args().collect();
        if args.get(1).map(String::as_str) == Some("fixture") {
            write_protocol_fixture(
                args[2].parse().unwrap(),
                args[3].parse().unwrap(),
                args[4].parse().unwrap(),
                &args[5],
                &args[6],
            );
            return;
        }
        let seed_start = args.get(1).map_or(0, |value| value.parse().unwrap());
        let seed_count = args.get(2).map_or(5, |value| value.parse().unwrap());
        let output = args
            .get(3)
            .cloned()
            .unwrap_or_else(|| "d29b-integrated-parity.tsv".to_string());
        let threads = args
            .get(4)
            .map_or(16, |value| value.parse::<usize>().unwrap())
            .clamp(1, 64);
        let tasks: Vec<_> = (seed_start..seed_start + seed_count)
            .flat_map(|seed| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent_index| IntegratedTask {
                        seed,
                        seat,
                        opponent_index,
                    })
                })
            })
            .collect();
        let tasks = Arc::new(tasks);
        let next = Arc::new(AtomicUsize::new(0));
        let started = Instant::now();
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                thread::spawn(move || {
                    let mut rows = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        rows.push(integrated_parity(tasks[index]));
                    }
                    rows
                })
            })
            .collect();
        let mut rows: Vec<_> = handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("integrated parity worker"))
            .collect();
        rows.sort_by_key(|row| (row.task.seed, row.task.seat, row.task.opponent_index));
        let mut writer = BufWriter::new(File::create(&output).unwrap());
        writeln!(
            writer,
            "seed\tseat\topponent\treached_cut\tnormalized_prediction\traw_prediction\tswitched\tturns\tcommands\tfinal_turn\tmargin\tmy_score\topponent_score\tcommand_hash\tselection_ns\tmismatch"
        )
        .unwrap();
        let mut mismatch_count = 0usize;
        let mut switch_count = 0usize;
        let mut command_count = 0usize;
        for row in &rows {
            mismatch_count += usize::from(row.mismatch.is_some());
            switch_count += usize::from(row.switched);
            command_count += row.commands;
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{:.9}\t{:.9}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                row.task.seed,
                row.task.seat,
                OPPONENTS[row.task.opponent_index].0,
                usize::from(row.reached_cut),
                row.normalized,
                row.raw,
                usize::from(row.switched),
                row.turns,
                row.commands,
                row.final_turn,
                row.margin,
                row.my_score,
                row.opponent_score,
                row.command_hash,
                row.selection_ns,
                row.mismatch.as_deref().unwrap_or("")
            )
            .unwrap();
        }
        writer.flush().unwrap();
        eprintln!(
            "saved {} scenarios / {} commands / {} switches with {} mismatches in {:.3}s to {}",
            rows.len(),
            command_count,
            switch_count,
            mismatch_count,
            started.elapsed().as_secs_f64(),
            output
        );
        assert_eq!(mismatch_count, 0, "integrated command mismatch");
    }
}

pub use base::{bot, game};

fn main() {
    base::run_integrated();
}
