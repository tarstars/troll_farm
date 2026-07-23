mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    #[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
    pub(super) enum Continuation {
        Farm,
        Cold,
        Paused,
        Shadow,
    }

    impl Continuation {
        pub(super) fn label(self) -> &'static str {
            match self {
                Self::Farm => "farm",
                Self::Cold => "cold",
                Self::Paused => "paused",
                Self::Shadow => "shadow",
            }
        }

        fn parse(label: &str) -> Self {
            match label {
                "farm" => Self::Farm,
                "cold" => Self::Cold,
                "paused" => Self::Paused,
                "shadow" => Self::Shadow,
                _ => panic!("unknown D28 option: {label}"),
            }
        }
    }

    #[derive(Clone)]
    pub(super) struct Selection {
        pub(super) resident: bool,
        pub(super) continuations: Vec<Continuation>,
    }

    pub(super) fn parse_selection(value: &str) -> Selection {
        let labels: BTreeSet<_> = value.split(',').filter(|label| !label.is_empty()).collect();
        assert!(!labels.is_empty(), "D28 options must not be empty");
        Selection {
            resident: labels.contains("resident"),
            continuations: labels
                .iter()
                .filter(|label| **label != "resident")
                .map(|label| Continuation::parse(label))
                .collect(),
        }
    }

    #[derive(Clone)]
    struct HandoffState {
        game: GameState,
        farm_prefix_hash: u64,
    }

    #[derive(Clone)]
    struct D28Branch {
        result: BranchResult,
        handoff: Option<HandoffState>,
        shadow_turns: usize,
    }

    fn handoff_branch(
        prefix: &Prefix,
        seat: usize,
        opponent_index: usize,
        continuation: Continuation,
    ) -> D28Branch {
        let mut game = prefix.root.clone();
        let farm = OwnershipAwareFarm::new();
        let opponent = warmed_opponent(prefix, seat, opponent_index);
        let mut retained_resident =
            matches!(continuation, Continuation::Paused | Continuation::Shadow)
                .then(|| warmed_resident(prefix, seat));
        let mut stall_counter = prefix.stall_counter;
        let mut max_workers = worker_count(&game, seat);
        let mut farm_turns = 0;
        let mut restart_turns = 0;
        let mut shadow_turns = 0;
        let mut farm_train = 0;
        let mut farm_plant = 0;
        let mut restart_train = 0;
        let mut restart_plant = 0;
        let mut hash = FNV_OFFSET;
        let mut ended = !prefix.reached_cut;

        if prefix.reached_cut {
            while game.turn < 150 && game.turn <= 300 {
                if continuation == Continuation::Shadow {
                    let _ = retained_resident
                        .as_mut()
                        .expect("shadow resident")
                        .commands(&yamo_view(&game, seat));
                    shadow_turns += 1;
                }
                let ours = farm.decide(&game, seat);
                let theirs = opponent.decide(&game, 1 - seat);
                farm_turns += 1;
                farm_train += count_kind(&ours, "TRAIN");
                farm_plant += count_kind(&ours, "PLANT");
                trace_commands(&mut hash, &ours);
                apply_commands(&mut game, seat, &ours, &theirs);
                max_workers = max_workers.max(worker_count(&game, seat));
                if has_stalled(&game, &mut stall_counter) {
                    ended = true;
                    break;
                }
            }
        }
        let handoff = prefix.reached_cut.then(|| HandoffState {
            game: game.clone(),
            farm_prefix_hash: hash,
        });

        if !ended && game.turn <= 300 {
            match continuation {
                Continuation::Farm => {
                    while game.turn <= 300 {
                        let ours = farm.decide(&game, seat);
                        let theirs = opponent.decide(&game, 1 - seat);
                        farm_turns += 1;
                        farm_train += count_kind(&ours, "TRAIN");
                        farm_plant += count_kind(&ours, "PLANT");
                        trace_commands(&mut hash, &ours);
                        apply_commands(&mut game, seat, &ours, &theirs);
                        max_workers = max_workers.max(worker_count(&game, seat));
                        if has_stalled(&game, &mut stall_counter) {
                            break;
                        }
                    }
                }
                Continuation::Cold | Continuation::Paused | Continuation::Shadow => {
                    let mut resident = match continuation {
                        Continuation::Cold => SecureOrchardBot::new(),
                        Continuation::Paused | Continuation::Shadow => retained_resident
                            .take()
                            .expect("retained resident continuation"),
                        Continuation::Farm => unreachable!(),
                    };
                    while game.turn <= 300 {
                        let ours = resident.commands(&yamo_view(&game, seat));
                        let theirs = opponent.decide(&game, 1 - seat);
                        restart_turns += 1;
                        restart_train += count_kind(&ours, "TRAIN");
                        restart_plant += count_kind(&ours, "PLANT");
                        trace_commands(&mut hash, &ours);
                        apply_commands(&mut game, seat, &ours, &theirs);
                        max_workers = max_workers.max(worker_count(&game, seat));
                        if has_stalled(&game, &mut stall_counter) {
                            break;
                        }
                    }
                }
            }
        }

        D28Branch {
            result: finish(
                continuation.label().to_string(),
                if continuation == Continuation::Farm {
                    -1
                } else {
                    150
                },
                &game,
                seat,
                max_workers,
                farm_turns,
                restart_turns,
                farm_train,
                farm_plant,
                restart_train,
                restart_plant,
                hash,
            ),
            handoff,
            shadow_turns,
        }
    }

    struct D28Scenario {
        task: Task,
        reached_cut: bool,
        root: GameState,
        branches: Vec<D28Branch>,
    }

    fn run_d28_task(task: Task, selection: &Selection) -> D28Scenario {
        let prefix = resident_prefix(task.seed, task.seat, task.opponent_index);
        let mut branches = Vec::with_capacity(selection.continuations.len() + 1);
        if selection.resident {
            branches.push(D28Branch {
                result: control(&prefix, task.seat, task.opponent_index),
                handoff: None,
                shadow_turns: 0,
            });
        }
        for &continuation in &selection.continuations {
            branches.push(handoff_branch(
                &prefix,
                task.seat,
                task.opponent_index,
                continuation,
            ));
        }
        D28Scenario {
            task,
            reached_cut: prefix.reached_cut,
            root: prefix.root,
            branches,
        }
    }

    pub fn run_d28() {
        let args: Vec<String> = std::env::args().collect();
        let seed_start = args
            .get(1)
            .map_or(0, |value| value.parse::<u64>().expect("numeric seed start"));
        let seed_count = args.get(2).map_or(5, |value| {
            value.parse::<usize>().expect("numeric seed count")
        });
        let output = args
            .get(3)
            .cloned()
            .unwrap_or_else(|| "d28-handoff-state.tsv".to_string());
        let threads = args
            .get(4)
            .map_or(16, |value| {
                value.parse::<usize>().expect("numeric thread count")
            })
            .clamp(1, 64);
        let selection = Arc::new(parse_selection(
            args.get(5)
                .map_or("resident,farm,cold,paused,shadow", String::as_str),
        ));
        assert!(seed_count > 0, "seed count must be positive");

        let tasks: Vec<_> = (seed_start..seed_start + seed_count as u64)
            .flat_map(|seed| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent_index| Task {
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
                let selection = Arc::clone(&selection);
                thread::spawn(move || {
                    let mut rows = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        rows.push(run_d28_task(tasks[index], &selection));
                    }
                    rows
                })
            })
            .collect();
        let mut scenarios: Vec<_> = handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("D28 worker"))
            .collect();
        scenarios.sort_by_key(|row| (row.task.seed, row.task.seat, row.task.opponent_index));

        let mut writer = BufWriter::new(File::create(&output).expect("create D28 output"));
        writeln!(
            writer,
            "seed\tseat\topponent\treached_cut\toption\texit_turn\troot_turn\troot_my_score\troot_opponent_score\troot_my_wood\troot_opponent_wood\troot_my_workers\troot_opponent_workers\troot_plants\thandoff_turn\thandoff_my_score\thandoff_opponent_score\thandoff_my_wood\thandoff_opponent_wood\thandoff_my_workers\thandoff_opponent_workers\thandoff_plants\tfarm_prefix_hash\tshadow_turns\tfinal_turn\tmargin\tmy_score\topponent_score\tmy_wood\topponent_wood\tmy_workers\topponent_workers\tmax_my_workers\tfarm_turns\trestart_turns\tfarm_train_commands\tfarm_plant_commands\trestart_train_commands\trestart_plant_commands\tcommand_hash"
        )
        .expect("write D28 header");
        let mut row_count = 0;
        for scenario in scenarios {
            let task = scenario.task;
            for branch in scenario.branches {
                let result = branch.result;
                let handoff = branch.handoff;
                let (
                    handoff_turn,
                    handoff_my_score,
                    handoff_opponent_score,
                    handoff_my_wood,
                    handoff_opponent_wood,
                    handoff_my_workers,
                    handoff_opponent_workers,
                    handoff_plants,
                ) = handoff
                    .as_ref()
                    .map_or((-1, -1, -1, -1, -1, -1, -1, -1), |state| {
                        (
                            state.game.turn,
                            state.game.scores[task.seat],
                            state.game.scores[1 - task.seat],
                            state.game.inventories[task.seat][5],
                            state.game.inventories[1 - task.seat][5],
                            worker_count(&state.game, task.seat) as i32,
                            worker_count(&state.game, 1 - task.seat) as i32,
                            state.game.plants.len() as i32,
                        )
                    });
                writeln!(
                    writer,
                    "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                    task.seed,
                    task.seat,
                    OPPONENTS[task.opponent_index].0,
                    usize::from(scenario.reached_cut),
                    result.label,
                    result.exit_turn,
                    scenario.root.turn,
                    scenario.root.scores[task.seat],
                    scenario.root.scores[1 - task.seat],
                    scenario.root.inventories[task.seat][5],
                    scenario.root.inventories[1 - task.seat][5],
                    worker_count(&scenario.root, task.seat),
                    worker_count(&scenario.root, 1 - task.seat),
                    scenario.root.plants.len(),
                    handoff_turn,
                    handoff_my_score,
                    handoff_opponent_score,
                    handoff_my_wood,
                    handoff_opponent_wood,
                    handoff_my_workers,
                    handoff_opponent_workers,
                    handoff_plants,
                    handoff.as_ref().map_or(0, |state| state.farm_prefix_hash),
                    branch.shadow_turns,
                    result.final_turn,
                    result.margin,
                    result.my_score,
                    result.opponent_score,
                    result.my_wood,
                    result.opponent_wood,
                    result.my_workers,
                    result.opponent_workers,
                    result.max_my_workers,
                    result.farm_turns,
                    result.restart_turns,
                    result.farm_train_commands,
                    result.farm_plant_commands,
                    result.restart_train_commands,
                    result.restart_plant_commands,
                    result.command_hash,
                )
                .expect("write D28 row");
                row_count += 1;
            }
        }
        writer.flush().expect("flush D28 output");
        eprintln!(
            "saved {row_count} rows from {} scenarios in {:.3}s to {output}",
            tasks.len(),
            started.elapsed().as_secs_f64(),
        );
    }
}

pub use base::{bot, game};

fn main() {
    base::run_d28();
}

#[cfg(test)]
mod tests {
    use super::base::Continuation;

    #[test]
    fn continuation_labels_are_unique() {
        let labels = [
            Continuation::Farm.label(),
            Continuation::Cold.label(),
            Continuation::Paused.label(),
            Continuation::Shadow.label(),
        ];
        let unique: std::collections::BTreeSet<_> = labels.into_iter().collect();
        assert_eq!(unique.len(), labels.len());
    }

    #[test]
    fn confirmation_selection_is_narrow() {
        let selected = super::base::parse_selection("resident,paused");
        assert!(selected.resident);
        assert_eq!(selected.continuations, vec![Continuation::Paused]);
    }
}
