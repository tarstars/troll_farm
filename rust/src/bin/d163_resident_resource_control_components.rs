//! D163a: factorial resource-control components over an always-warm resident.

#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    const D163_HORIZON: i32 = 32;
    const FRUIT: u8 = 1;
    const IRON_ROUTE: u8 = 2;
    const PROTECTION: u8 = 4;

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct ResourceConfig {
        mask: u8,
        start: i32,
    }

    #[derive(Clone, Debug)]
    struct ResourcePolicySpec {
        label: String,
        controller: Option<ResourceConfig>,
    }

    fn mask_label(mask: u8) -> &'static str {
        match mask {
            1 => "fruit",
            2 => "iron",
            3 => "fruit_iron",
            4 => "protection",
            5 => "fruit_protection",
            6 => "iron_protection",
            7 => "fruit_iron_protection",
            _ => panic!("invalid D163 mask {mask}"),
        }
    }

    fn d163_policy_catalog() -> Vec<ResourcePolicySpec> {
        let mut policies = vec![ResourcePolicySpec {
            label: "resident".to_string(),
            controller: None,
        }];
        for start in MARKS {
            for mask in 1..=7 {
                policies.push(ResourcePolicySpec {
                    label: format!("{}_t{start:03}_h032", mask_label(mask)),
                    controller: Some(ResourceConfig { mask, start }),
                });
            }
        }
        policies
    }

    fn shadow_reserve(game: &GameState) -> [i32; 6] {
        [3, 3, 2, 0, if game.iron.is_empty() { 0 } else { 3 }, 0]
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum ResourceReason {
        FruitBank,
        IronBank,
        FruitRoute,
        IronRoute,
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct ResourceTelemetry {
        activated: bool,
        activation_turn: i32,
        deadline: i32,
        active_turns: u16,
        aborted: bool,
        option_overrides: u16,
        fruit_overrides: u16,
        iron_overrides: u16,
        protected_commands: u16,
        move_commands: u16,
        bank_commands: u16,
        fruit_bank_commands: u16,
        iron_bank_commands: u16,
        harvest_commands: u16,
        mine_commands: u16,
        resident_train_commands: u16,
        controller_train_commands: u16,
        suppressed_train_commands: u16,
        initial_bank_deficit: i32,
        closest_bank_deficit: i32,
        option_command_failures: u16,
        workforce_exit_events: u16,
        horizon_violations: u16,
        restart_violations: u16,
    }

    #[derive(Clone, Debug)]
    struct ResourceController {
        config: Option<ResourceConfig>,
        telemetry: ResourceTelemetry,
    }

    impl ResourceController {
        fn new(config: Option<ResourceConfig>) -> Self {
            Self {
                config,
                telemetry: ResourceTelemetry {
                    activation_turn: -1,
                    deadline: -1,
                    initial_bank_deficit: -1,
                    closest_bank_deficit: -1,
                    ..ResourceTelemetry::default()
                },
            }
        }

        fn enabled(config: ResourceConfig, component: u8) -> bool {
            config.mask & component != 0
        }

        fn active(&self) -> bool {
            self.telemetry.activated && !self.telemetry.aborted
        }

        fn carried_resource_worker<'a>(
            game: &'a GameState,
            player: usize,
            target: &[i32; 6],
            config: ResourceConfig,
        ) -> Option<(&'a Unit, ResourceReason)> {
            own_units(game, player)
                .into_iter()
                .filter_map(|unit| {
                    let fruit_progress = if Self::enabled(config, FRUIT) {
                        [PLUM, LEMON, APPLE]
                            .into_iter()
                            .map(|item| {
                                unit.carry[item]
                                    .min((target[item] - game.inventories[player][item]).max(0))
                            })
                            .sum()
                    } else {
                        0
                    };
                    let iron_progress = if Self::enabled(config, IRON_ROUTE) {
                        unit.carry[IRON].min((target[IRON] - game.inventories[player][IRON]).max(0))
                    } else {
                        0
                    };
                    let total = fruit_progress + iron_progress;
                    if total <= 0 {
                        return None;
                    }
                    let reason = if fruit_progress >= iron_progress {
                        ResourceReason::FruitBank
                    } else {
                        ResourceReason::IronBank
                    };
                    Some((total, fruit_progress, iron_progress, -unit.id, unit, reason))
                })
                .max_by_key(|entry| (entry.0, entry.1, entry.2, entry.3))
                .map(|entry| (entry.4, entry.5))
        }

        fn acquisition_command(
            game: &GameState,
            player: usize,
            target: &[i32; 6],
            config: ResourceConfig,
        ) -> Option<(i32, String, ResourceReason)> {
            if let Some((unit, reason)) =
                Self::carried_resource_worker(game, player, target, config)
            {
                return Some((
                    unit.id,
                    CapitalOption::bank_command(game, player, unit),
                    reason,
                ));
            }
            let deficits = liquid_deficits(game, player, target);
            let mut resources = Vec::new();
            if Self::enabled(config, FRUIT) {
                resources.extend([PLUM, LEMON, APPLE]);
            }
            if Self::enabled(config, IRON_ROUTE) {
                resources.push(IRON);
            }
            resources.sort_by_key(|item| (-deficits[*item], *item));
            for item in resources {
                if deficits[item] <= 0 {
                    continue;
                }
                if item == IRON {
                    if let Some((id, command)) = CapitalOption::mine_command(game, player) {
                        return Some((id, command, ResourceReason::IronRoute));
                    }
                } else if let Some((id, command)) = CapitalOption::fruit_command(game, player, item)
                {
                    return Some((id, command, ResourceReason::FruitRoute));
                }
            }
            None
        }

        fn rewrite(
            &mut self,
            game: &GameState,
            player: usize,
            resident_commands: Vec<String>,
        ) -> Vec<String> {
            let Some(config) = self.config else {
                return resident_commands;
            };
            self.telemetry.resident_train_commands += resident_commands
                .iter()
                .filter(|command| command_fields(command).first() == Some(&"TRAIN"))
                .count()
                .min(u16::MAX as usize)
                as u16;
            let workers = worker_count(game, player);
            if game.turn == config.start {
                if self.telemetry.activated {
                    self.telemetry.restart_violations += 1;
                } else if workers == 2 {
                    let target = shadow_reserve(game);
                    let deficit = bank_deficit(game, player, &target);
                    self.telemetry.activated = true;
                    self.telemetry.activation_turn = game.turn;
                    self.telemetry.deadline = config.start + D163_HORIZON;
                    self.telemetry.initial_bank_deficit = deficit;
                    self.telemetry.closest_bank_deficit = deficit;
                }
            }
            if !self.active() {
                return resident_commands;
            }
            if workers != 2 {
                self.telemetry.workforce_exit_events += 1;
                self.telemetry.aborted = true;
                return resident_commands;
            }
            if game.turn >= self.telemetry.deadline {
                self.telemetry.aborted = true;
                return resident_commands;
            }
            self.telemetry.active_turns += 1;
            if i32::from(self.telemetry.active_turns) > D163_HORIZON {
                self.telemetry.horizon_violations += 1;
            }
            let target = shadow_reserve(game);
            self.telemetry.closest_bank_deficit = self
                .telemetry
                .closest_bank_deficit
                .min(bank_deficit(game, player, &target));
            let acquisition = Self::acquisition_command(game, player, &target, config);
            let selected_id = acquisition.as_ref().map(|(id, _, _)| *id);
            let mut rewritten = Vec::new();
            for command in resident_commands {
                if command_unit(&command).is_some_and(|id| Some(id) == selected_id) {
                    continue;
                }
                let protected = Self::enabled(config, PROTECTION)
                    && command_item(&command).is_some_and(|item| {
                        item < 6 && game.inventories[player][item] < target[item]
                    });
                if protected {
                    if command_fields(&command).first() == Some(&"TRAIN") {
                        self.telemetry.suppressed_train_commands += 1;
                    }
                    self.telemetry.protected_commands += 1;
                    continue;
                }
                rewritten.push(command);
            }
            if let Some((_, command, reason)) = acquisition {
                if !CapitalOption::generated_command_is_legal(game, player, &command) {
                    self.telemetry.option_command_failures += 1;
                } else {
                    self.telemetry.option_overrides += 1;
                    match reason {
                        ResourceReason::FruitBank => {
                            self.telemetry.fruit_overrides += 1;
                            self.telemetry.fruit_bank_commands += 1;
                        }
                        ResourceReason::IronBank => {
                            self.telemetry.iron_overrides += 1;
                            self.telemetry.iron_bank_commands += 1;
                        }
                        ResourceReason::FruitRoute => self.telemetry.fruit_overrides += 1,
                        ResourceReason::IronRoute => self.telemetry.iron_overrides += 1,
                    }
                    match command_fields(&command).first().copied().unwrap_or("WAIT") {
                        "MOVE" => self.telemetry.move_commands += 1,
                        "DROP" => self.telemetry.bank_commands += 1,
                        "HARVEST" => self.telemetry.harvest_commands += 1,
                        "MINE" => self.telemetry.mine_commands += 1,
                        "TRAIN" => self.telemetry.controller_train_commands += 1,
                        _ => self.telemetry.option_command_failures += 1,
                    }
                    rewritten.push(command);
                }
            }
            rewritten
        }
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D163Outcome {
        done: bool,
        turn: u16,
        own_score: i32,
        opponent_score: i32,
        own_return: f32,
        opponent_return: f32,
        margin_return: f32,
        reward_identity_error: f32,
        own_workers: u8,
        opponent_workers: u8,
        max_own_workers: u8,
        successful_trains: u8,
        provenance_failures: u16,
        own_created_crops: u16,
        opponent_created_crops: u16,
        joint_created_crops: u16,
        ambiguous_created_crops: u16,
        own_owned_crop_harvest_units: u16,
        own_reinvested_crops: u16,
        action_hash: u64,
        state_hash: u64,
        prefix_captured: [bool; 3],
        prefix_action_hash: [u64; 3],
        prefix_state_hash: [u64; 3],
        resource: ResourceTelemetry,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D163Row {
        task: Task,
        policy: usize,
        outcome: D163Outcome,
    }

    fn d163_play(task: Task, policy: usize, spec: &ResourcePolicySpec) -> D163Row {
        let mut game = generate_official(task.map_seed);
        let mut ours = SecureOrchardBot::new();
        let mut controller = ResourceController::new(spec.controller);
        let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
        let mut owners: BTreeMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), Owner::Natural))
            .collect();
        let mut turns_until_end = 0i32;
        let mut action_hash = 14_695_981_039_346_656_037_u64;
        let mut prefix_captured = [false; 3];
        let mut prefix_action_hash = [0; 3];
        let mut prefix_state_hash = [0; 3];
        let mut max_own_workers = worker_count(&game, task.seat);
        let mut successful_trains = 0usize;
        let mut provenance_failures = 0usize;
        let mut own_created_crops = 0usize;
        let mut opponent_created_crops = 0usize;
        let mut joint_created_crops = 0usize;
        let mut ambiguous_created_crops = 0usize;
        let mut own_owned_crop_harvest_units = 0usize;
        let mut own_reinvested_crops = 0usize;
        let mut done = false;

        while !done {
            for (index, mark) in MARKS.iter().enumerate() {
                if game.turn == *mark {
                    prefix_captured[index] = true;
                    prefix_action_hash[index] = action_hash;
                    prefix_state_hash[index] = canonical_state_hash(&game);
                }
            }
            let resident_commands = ours.commands(&resident_view(&game, task.seat));
            let ours_commands = controller.rewrite(&game, task.seat, resident_commands);
            let theirs_commands = theirs.commands(&game, 1 - task.seat);
            let commands = if task.seat == 0 {
                [ours_commands, theirs_commands]
            } else {
                [theirs_commands, ours_commands]
            };
            for (player, player_commands) in commands.iter().enumerate() {
                action_hash = fnv1a(action_hash, &[player as u8]);
                for command in player_commands {
                    action_hash = fnv1a(action_hash, command.as_bytes());
                    action_hash = fnv1a(action_hash, &[0]);
                }
                action_hash = fnv1a(action_hash, &[255]);
            }

            let before_plants: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
            let attempts = [
                plant_attempts(&game, 0, &commands[0]),
                plant_attempts(&game, 1, &commands[1]),
            ];
            let before_workers = worker_count(&game, task.seat);
            let harvest_ids = command_unit_ids(&commands[task.seat], "HARVEST");
            let own_crop_harvests: Vec<_> = harvest_ids
                .into_iter()
                .filter_map(|id| {
                    let unit = game
                        .units
                        .iter()
                        .find(|unit| unit.id == id && unit.player as usize == task.seat)?;
                    (owners.get(&unit.pos()) == Some(&Owner::Own)).then_some((id, unit.carry))
                })
                .collect();
            let had_renewable_receipt = own_owned_crop_harvest_units > 0;

            step(&mut game, &commands[0], &commands[1]);

            let (failures, own_plants, opponent_plants, joint_plants, ambiguous_plants) =
                update_provenance(&game, &before_plants, &attempts, &mut owners, task.seat);
            provenance_failures += failures;
            own_created_crops += own_plants;
            opponent_created_crops += opponent_plants;
            joint_created_crops += joint_plants;
            ambiguous_created_crops += ambiguous_plants;
            if had_renewable_receipt {
                own_reinvested_crops += own_plants;
            }
            for (id, before_carry) in own_crop_harvests {
                let Some(unit) = game.units.iter().find(|unit| unit.id == id) else {
                    continue;
                };
                let gained = (0..4)
                    .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                    .sum::<i32>();
                own_owned_crop_harvest_units += gained.max(0) as usize;
            }
            let after_workers = worker_count(&game, task.seat);
            successful_trains += after_workers.saturating_sub(before_workers);
            max_own_workers = max_own_workers.max(after_workers);
            done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        }

        let own_score = game.scores[task.seat];
        let opponent_score = game.scores[1 - task.seat];
        let margin = own_score - opponent_score;
        let own_return = own_score as f32 / 100.0;
        let opponent_return = opponent_score as f32 / 100.0;
        let margin_return = margin as f32 / 100.0;
        D163Row {
            task,
            policy,
            outcome: D163Outcome {
                done,
                turn: game.turn.clamp(0, u16::MAX as i32) as u16,
                own_score,
                opponent_score,
                own_return,
                opponent_return,
                margin_return,
                reward_identity_error: (margin_return - (own_return - opponent_return)).abs(),
                own_workers: worker_count(&game, task.seat).min(u8::MAX as usize) as u8,
                opponent_workers: worker_count(&game, 1 - task.seat).min(u8::MAX as usize) as u8,
                max_own_workers: max_own_workers.min(u8::MAX as usize) as u8,
                successful_trains: successful_trains.min(u8::MAX as usize) as u8,
                provenance_failures: provenance_failures.min(u16::MAX as usize) as u16,
                own_created_crops: own_created_crops.min(u16::MAX as usize) as u16,
                opponent_created_crops: opponent_created_crops.min(u16::MAX as usize) as u16,
                joint_created_crops: joint_created_crops.min(u16::MAX as usize) as u16,
                ambiguous_created_crops: ambiguous_created_crops.min(u16::MAX as usize) as u16,
                own_owned_crop_harvest_units: own_owned_crop_harvest_units.min(u16::MAX as usize)
                    as u16,
                own_reinvested_crops: own_reinvested_crops.min(u16::MAX as usize) as u16,
                action_hash,
                state_hash: canonical_state_hash(&game),
                prefix_captured,
                prefix_action_hash,
                prefix_state_hash,
                resource: controller.telemetry,
            },
        }
    }

    fn d163_write_rows(output: &str, rows: &[D163Row], policies: &[ResourcePolicySpec]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D163a output"));
        writeln!(writer, "map_seed\tseat\topponent_index\topponent\tpolicy_index\tpolicy\tcomponent_mask\tfruit_routing\tiron_routing\tprotection\toption_start\toption_horizon\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tprefix72_captured\tprefix72_action_hash\tprefix72_state_hash\tprefix104_captured\tprefix104_action_hash\tprefix104_state_hash\tprefix136_captured\tprefix136_action_hash\tprefix136_state_hash\tactivated\tactivation_turn\tdeadline\tactive_turns\taborted\toption_overrides\tfruit_overrides\tiron_overrides\tprotected_commands\tmove_commands\tbank_commands\tfruit_bank_commands\tiron_bank_commands\tharvest_commands\tmine_commands\tresident_train_commands\tcontroller_train_commands\tsuppressed_train_commands\tinitial_bank_deficit\tclosest_bank_deficit\toption_command_failures\tworkforce_exit_events\thorizon_violations\trestart_violations").expect("write D163a header");
        for row in rows {
            let out = row.outcome;
            let telemetry = out.resource;
            let config = policies[row.policy].controller;
            let mask = config.map_or(0, |value| value.mask);
            let start = config.map_or(-1, |value| value.start);
            let values = vec![
                row.task.map_seed.to_string(),
                row.task.seat.to_string(),
                row.task.opponent.to_string(),
                MacroOpponentMode::from_index(row.task.opponent)
                    .label()
                    .to_string(),
                row.policy.to_string(),
                policies[row.policy].label.clone(),
                mask.to_string(),
                usize::from(mask & FRUIT != 0).to_string(),
                usize::from(mask & IRON_ROUTE != 0).to_string(),
                usize::from(mask & PROTECTION != 0).to_string(),
                start.to_string(),
                if config.is_some() {
                    D163_HORIZON.to_string()
                } else {
                    "0".to_string()
                },
                usize::from(out.done).to_string(),
                out.turn.to_string(),
                out.own_score.to_string(),
                out.opponent_score.to_string(),
                (out.own_score - out.opponent_score).to_string(),
                format!("{:.9}", out.own_return),
                format!("{:.9}", out.opponent_return),
                format!("{:.9}", out.margin_return),
                format!("{:.9}", out.reward_identity_error),
                out.own_workers.to_string(),
                out.opponent_workers.to_string(),
                out.max_own_workers.to_string(),
                out.successful_trains.to_string(),
                "0".to_string(),
                "0".to_string(),
                telemetry.option_command_failures.to_string(),
                out.provenance_failures.to_string(),
                "0".to_string(),
                out.own_created_crops.to_string(),
                out.opponent_created_crops.to_string(),
                out.joint_created_crops.to_string(),
                out.ambiguous_created_crops.to_string(),
                out.own_owned_crop_harvest_units.to_string(),
                out.own_reinvested_crops.to_string(),
                out.action_hash.to_string(),
                out.state_hash.to_string(),
                usize::from(out.prefix_captured[0]).to_string(),
                out.prefix_action_hash[0].to_string(),
                out.prefix_state_hash[0].to_string(),
                usize::from(out.prefix_captured[1]).to_string(),
                out.prefix_action_hash[1].to_string(),
                out.prefix_state_hash[1].to_string(),
                usize::from(out.prefix_captured[2]).to_string(),
                out.prefix_action_hash[2].to_string(),
                out.prefix_state_hash[2].to_string(),
                usize::from(telemetry.activated).to_string(),
                telemetry.activation_turn.to_string(),
                telemetry.deadline.to_string(),
                telemetry.active_turns.to_string(),
                usize::from(telemetry.aborted).to_string(),
                telemetry.option_overrides.to_string(),
                telemetry.fruit_overrides.to_string(),
                telemetry.iron_overrides.to_string(),
                telemetry.protected_commands.to_string(),
                telemetry.move_commands.to_string(),
                telemetry.bank_commands.to_string(),
                telemetry.fruit_bank_commands.to_string(),
                telemetry.iron_bank_commands.to_string(),
                telemetry.harvest_commands.to_string(),
                telemetry.mine_commands.to_string(),
                telemetry.resident_train_commands.to_string(),
                telemetry.controller_train_commands.to_string(),
                telemetry.suppressed_train_commands.to_string(),
                telemetry.initial_bank_deficit.to_string(),
                telemetry.closest_bank_deficit.to_string(),
                telemetry.option_command_failures.to_string(),
                telemetry.workforce_exit_events.to_string(),
                telemetry.horizon_violations.to_string(),
                telemetry.restart_violations.to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D163a row");
        }
        writer.flush().expect("flush D163a output");
    }

    #[derive(Clone, Copy, Debug)]
    struct D163Work {
        task: Task,
        policy: usize,
    }

    pub(super) fn d163_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            5,
            "usage: d163_resident_resource_control_components START_SEED MAPS OUTPUT THREADS"
        );
        let start_seed: i64 = parse(&args[1], "start seed");
        let maps: usize = parse(&args[2], "maps");
        let output = &args[3];
        let threads: usize = parse(&args[4], "threads");
        assert!(maps > 0 && threads > 0);
        assert!(start_seed + maps as i64 <= 9_844_200 || start_seed >= 9_844_216);

        let policies = Arc::new(d163_policy_catalog());
        let policy_count = policies.len();
        let work: Vec<_> = (start_seed..start_seed + maps as i64)
            .flat_map(|map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).flat_map(move |opponent| {
                        (0..policy_count).map(move |policy| D163Work {
                            task: Task {
                                map_seed,
                                seat,
                                opponent,
                            },
                            policy,
                        })
                    })
                })
            })
            .collect();
        let work = Arc::new(work);
        let next = Arc::new(AtomicUsize::new(0));
        let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
        let started = Instant::now();
        let handles: Vec<_> = (0..threads.min(work.len()))
            .map(|_| {
                let policies = Arc::clone(&policies);
                let work = Arc::clone(&work);
                let next = Arc::clone(&next);
                let rows = Arc::clone(&rows);
                thread::spawn(move || loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    let Some(item) = work.get(index).copied() else {
                        break;
                    };
                    let row = d163_play(item.task, item.policy, &policies[item.policy]);
                    rows.lock().expect("D163a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D163a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D163a rows")
            .into_inner()
            .expect("D163a rows lock");
        rows.sort_by_key(|row| (row.task, row.policy));
        d163_write_rows(output, &rows, &policies);
        eprintln!(
            "saved {} D163a rows with {} workers in {:.3}s to {}",
            rows.len(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            output,
        );
    }

    #[cfg(test)]
    mod d163_tests {
        use super::*;

        #[test]
        fn catalog_is_control_plus_full_nonempty_factorial_at_three_marks() {
            let catalog = d163_policy_catalog();
            assert_eq!(catalog.len(), 22);
            assert_eq!(catalog[0].label, "resident");
            assert_eq!(catalog[1].label, "fruit_t072_h032");
            assert_eq!(catalog[7].label, "fruit_iron_protection_t072_h032");
            assert_eq!(catalog[21].label, "fruit_iron_protection_t136_h032");
        }

        #[test]
        fn shadow_reserve_is_frozen_and_drops_iron_only_without_ore() {
            let mut game = generate_official(9_844_144);
            assert_eq!(shadow_reserve(&game), [3, 3, 2, 0, 3, 0]);
            game.iron.clear();
            assert_eq!(shadow_reserve(&game), [3, 3, 2, 0, 0, 0]);
        }

        #[test]
        fn disabled_controller_is_exact_resident() {
            let task = Task {
                map_seed: 9_844_144,
                seat: 0,
                opponent: 0,
            };
            let resident = ResourcePolicySpec {
                label: "resident".to_string(),
                controller: None,
            };
            let disabled = ResourcePolicySpec {
                label: "disabled".to_string(),
                controller: Some(ResourceConfig {
                    mask: FRUIT | IRON_ROUTE | PROTECTION,
                    start: 400,
                }),
            };
            let first = d163_play(task, 0, &resident);
            let second = d163_play(task, 1, &disabled);
            assert_eq!(first.outcome.own_score, second.outcome.own_score);
            assert_eq!(first.outcome.opponent_score, second.outcome.opponent_score);
            assert_eq!(first.outcome.action_hash, second.outcome.action_hash);
            assert_eq!(first.outcome.state_hash, second.outcome.state_hash);
        }

        #[test]
        fn component_purity_and_no_controller_train_are_structural() {
            let task = Task {
                map_seed: 9_844_144,
                seat: 0,
                opponent: 0,
            };
            for (mask, forbidden) in [
                (FRUIT, (true, true)),
                (IRON_ROUTE, (true, true)),
                (PROTECTION, (true, true)),
            ] {
                let spec = ResourcePolicySpec {
                    label: "test".to_string(),
                    controller: Some(ResourceConfig { mask, start: 72 }),
                };
                let row = d163_play(task, 1, &spec);
                assert!(row.outcome.resource.active_turns <= D163_HORIZON as u16);
                assert_eq!(row.outcome.resource.controller_train_commands, 0);
                assert_eq!(row.outcome.resource.suppressed_train_commands, 0);
                assert_eq!(row.outcome.resource.option_command_failures, 0);
                if mask & FRUIT == 0 && forbidden.0 {
                    assert_eq!(row.outcome.resource.fruit_overrides, 0);
                }
                if mask & IRON_ROUTE == 0 && forbidden.1 {
                    assert_eq!(row.outcome.resource.iron_overrides, 0);
                }
                if mask & PROTECTION == 0 {
                    assert_eq!(row.outcome.resource.protected_commands, 0);
                }
            }
        }
    }
}

fn main() {
    inherited::d163_main();
}
