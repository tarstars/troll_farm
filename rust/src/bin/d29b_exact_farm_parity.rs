mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    mod exact_farm {
        include!("../d29b_exact_farm.rs");
    }

    use exact_farm::ExactFarm;

    #[derive(Clone, Copy)]
    struct FarmTask {
        seed: u64,
        seat: usize,
        opponent_index: usize,
    }

    struct FarmParity {
        task: FarmTask,
        reached_cut: bool,
        turns: usize,
        commands: usize,
        final_turn: i32,
        margin: i32,
        command_hash: u64,
        mismatch: Option<String>,
    }

    fn farm_parity(task: FarmTask) -> FarmParity {
        let prefix = resident_prefix(task.seed, task.seat, task.opponent_index);
        let mut game = prefix.root.clone();
        let original = OwnershipAwareFarm::new();
        let compact = ExactFarm::new();
        let opponent = warmed_opponent(&prefix, task.seat, task.opponent_index);
        let mut stall_counter = prefix.stall_counter;
        let mut turns = 0;
        let mut commands = 0;
        let mut command_hash = FNV_OFFSET;
        let mut mismatch = None;
        if prefix.reached_cut {
            while game.turn <= 300 {
                let expected = original.decide(&game, task.seat);
                let actual = compact.commands(&yamo_view(&game, task.seat));
                if expected != actual {
                    mismatch = Some(format!(
                        "turn={} expected={:?} actual={:?}",
                        game.turn, expected, actual
                    ));
                    break;
                }
                turns += 1;
                commands += expected.len();
                trace_commands(&mut command_hash, &expected);
                let theirs = opponent.decide(&game, 1 - task.seat);
                apply_commands(&mut game, task.seat, &expected, &theirs);
                if has_stalled(&game, &mut stall_counter) {
                    break;
                }
            }
        }
        FarmParity {
            task,
            reached_cut: prefix.reached_cut,
            turns,
            commands,
            final_turn: game.turn,
            margin: game.scores[task.seat] - game.scores[1 - task.seat],
            command_hash,
            mismatch,
        }
    }

    pub fn run_parity() {
        let args: Vec<String> = std::env::args().collect();
        let seed_start = args.get(1).map_or(0, |value| value.parse().unwrap());
        let seed_count = args.get(2).map_or(5, |value| value.parse().unwrap());
        let output = args
            .get(3)
            .cloned()
            .unwrap_or_else(|| "d29b-exact-farm-parity.tsv".to_string());
        let threads = args
            .get(4)
            .map_or(16, |value| value.parse::<usize>().unwrap())
            .clamp(1, 64);
        let tasks: Vec<_> = (seed_start..seed_start + seed_count)
            .flat_map(|seed| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent_index| FarmTask {
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
                        rows.push(farm_parity(tasks[index]));
                    }
                    rows
                })
            })
            .collect();
        let mut rows: Vec<_> = handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("farm parity worker"))
            .collect();
        rows.sort_by_key(|row| (row.task.seed, row.task.seat, row.task.opponent_index));
        let mut writer = BufWriter::new(File::create(&output).unwrap());
        writeln!(
            writer,
            "seed\tseat\topponent\treached_cut\tturns\tcommands\tfinal_turn\tmargin\tcommand_hash\tmismatch"
        )
        .unwrap();
        let mut mismatch_count = 0usize;
        let mut command_count = 0usize;
        for row in &rows {
            mismatch_count += usize::from(row.mismatch.is_some());
            command_count += row.commands;
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                row.task.seed,
                row.task.seat,
                OPPONENTS[row.task.opponent_index].0,
                usize::from(row.reached_cut),
                row.turns,
                row.commands,
                row.final_turn,
                row.margin,
                row.command_hash,
                row.mismatch.as_deref().unwrap_or("")
            )
            .unwrap();
        }
        writer.flush().unwrap();
        eprintln!(
            "saved {} scenarios / {} commands with {} mismatches in {:.3}s to {}",
            rows.len(),
            command_count,
            mismatch_count,
            started.elapsed().as_secs_f64(),
            output
        );
        assert_eq!(mismatch_count, 0, "exact-farm command mismatch");
    }
}

pub use base::{bot, game};

fn main() {
    base::run_parity();
}
