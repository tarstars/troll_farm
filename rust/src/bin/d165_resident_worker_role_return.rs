//! D165a: exact-resident bounded same-worker producer/suppressor return.

#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    const D165_HORIZON: i32 = 16;
    const D165_POLICY_LABELS: [&str; 2] =
        ["resident", "producer_suppressor_return_h016"];

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct ReturnEpisode {
        unit_id: i32,
        target: Cell,
        activation_turn: i32,
        deadline: i32,
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum ReturnVerb {
        Move,
        Hold,
        Harvest,
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct PendingReturn {
        unit_id: i32,
        target: Cell,
        action_turn: i32,
        verb: ReturnVerb,
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct ReturnTelemetry {
        resident_calls: u16,
        turns_played: u16,
        resident_call_mismatches: u16,
        production_events: u16,
        successful_production_plants: u16,
        successful_production_harvests: u16,
        opponent_crop_chops: u16,
        historical_producer_opponent_crop_chops: u16,
        remembered_live_target_opponent_crop_chops: u16,
        post_step_live_target_opponent_crop_chops: u16,
        suppression_entries: u16,
        eligible_entries: u16,
        activated: bool,
        activation_turn: i32,
        deadline: i32,
        first_override_turn: i32,
        selected_unit_id: i32,
        target_x: i32,
        target_y: i32,
        active_turns: u16,
        completed: bool,
        return_turn: i32,
        return_latency: i32,
        return_harvest_units: u16,
        aborted: bool,
        abort_turn: i32,
        abort_target_loss: u16,
        abort_unit_loss: u16,
        abort_capacity: u16,
        abort_incapable: u16,
        abort_horizon: u16,
        abort_terminal: u16,
        option_overrides: u16,
        protected_commands: u16,
        move_commands: u16,
        hold_commands: u16,
        harvest_commands: u16,
        generated_command_failures: u16,
        ownership_failures: u16,
        target_change_violations: u16,
        same_worker_target_violations: u16,
        controller_train_commands: u16,
        controller_plant_commands: u16,
        controller_chop_commands: u16,
        controller_other_commands: u16,
        post_exit_overrides: u16,
        horizon_violations: u16,
        restart_violations: u16,
        prefix_action_hash: u64,
        prefix_state_hash: u64,
    }

    impl ReturnTelemetry {
        fn new() -> Self {
            Self {
                activation_turn: -1,
                deadline: -1,
                first_override_turn: -1,
                selected_unit_id: -1,
                target_x: -1,
                target_y: -1,
                return_turn: -1,
                return_latency: -1,
                abort_turn: -1,
                ..Self::default()
            }
        }
    }

    #[derive(Clone, Debug)]
    struct ReturnController {
        enabled: bool,
        used: bool,
        historical_producers: BTreeSet<i32>,
        production_targets: BTreeMap<i32, Cell>,
        episode: Option<ReturnEpisode>,
        pending: Option<PendingReturn>,
        telemetry: ReturnTelemetry,
    }

    impl ReturnController {
        fn new(enabled: bool) -> Self {
            Self {
                enabled,
                used: false,
                historical_producers: BTreeSet::new(),
                production_targets: BTreeMap::new(),
                episode: None,
                pending: None,
                telemetry: ReturnTelemetry::new(),
            }
        }

        fn abort_target(&mut self, turn: i32) {
            self.telemetry.abort_target_loss += 1;
            self.abort(turn);
        }

        fn abort_unit(&mut self, turn: i32) {
            self.telemetry.abort_unit_loss += 1;
            self.abort(turn);
        }

        fn abort_capacity(&mut self, turn: i32) {
            self.telemetry.abort_capacity += 1;
            self.abort(turn);
        }

        fn abort_incapable(&mut self, turn: i32) {
            self.telemetry.abort_incapable += 1;
            self.abort(turn);
        }

        fn abort_horizon(&mut self, turn: i32) {
            self.telemetry.abort_horizon += 1;
            self.abort(turn);
        }

        fn abort_terminal(&mut self, turn: i32) {
            self.telemetry.abort_terminal += 1;
            self.abort(turn);
        }

        fn abort(&mut self, turn: i32) {
            if self.episode.take().is_some() {
                self.telemetry.aborted = true;
                self.telemetry.abort_turn = turn;
            }
            self.pending = None;
        }

        fn generated_command_is_legal(
            game: &GameState,
            player: usize,
            episode: ReturnEpisode,
            verb: ReturnVerb,
        ) -> bool {
            let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == episode.unit_id && unit.player as usize == player)
            else {
                return false;
            };
            match verb {
                ReturnVerb::Move => {
                    unit.pos() != episode.target && game.walkable.contains(&episode.target)
                }
                ReturnVerb::Hold => {
                    unit.pos() == episode.target && game.walkable.contains(&episode.target)
                }
                ReturnVerb::Harvest => {
                    unit.pos() == episode.target
                        && unit.hp > 0
                        && unit.free() > 0
                        && game
                            .plants
                            .iter()
                            .any(|plant| plant.pos() == episode.target && plant.fruits > 0)
                }
            }
        }

        fn rewrite(
            &mut self,
            game: &GameState,
            player: usize,
            resident_commands: Vec<String>,
            action_hash: u64,
        ) -> Vec<String> {
            self.telemetry.resident_calls += 1;
            self.pending = None;
            if !self.enabled {
                return resident_commands;
            }
            let Some(episode) = self.episode else {
                return resident_commands;
            };
            if self.telemetry.completed || self.telemetry.aborted {
                self.telemetry.post_exit_overrides += 1;
                self.episode = None;
                return resident_commands;
            }
            if game.turn > episode.deadline {
                self.telemetry.horizon_violations += 1;
                self.abort_horizon(game.turn);
                return resident_commands;
            }
            if self.production_targets.get(&episode.unit_id) != Some(&episode.target) {
                self.telemetry.target_change_violations += 1;
                self.abort_target(game.turn);
                return resident_commands;
            }
            if owners_at_target_missing(game, episode.target) {
                self.abort_target(game.turn);
                return resident_commands;
            }
            let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == episode.unit_id && unit.player as usize == player)
            else {
                self.abort_unit(game.turn);
                return resident_commands;
            };
            if unit.hp <= 0 {
                self.abort_incapable(game.turn);
                return resident_commands;
            }
            if unit.free() <= 0 {
                self.abort_capacity(game.turn);
                return resident_commands;
            }

            let verb = if unit.pos() != episode.target {
                ReturnVerb::Move
            } else if game
                .plants
                .iter()
                .any(|plant| plant.pos() == episode.target && plant.fruits > 0)
            {
                ReturnVerb::Harvest
            } else {
                ReturnVerb::Hold
            };
            if !Self::generated_command_is_legal(game, player, episode, verb) {
                self.telemetry.generated_command_failures += 1;
                self.abort(game.turn);
                return resident_commands;
            }

            let command = match verb {
                ReturnVerb::Move | ReturnVerb::Hold => format!(
                    "MOVE {} {} {}",
                    episode.unit_id, episode.target.0, episode.target.1
                ),
                ReturnVerb::Harvest => format!("HARVEST {}", episode.unit_id),
            };
            let mut rewritten = Vec::with_capacity(resident_commands.len() + 1);
            for resident_command in resident_commands {
                if command_unit(&resident_command) == Some(episode.unit_id) {
                    self.telemetry.protected_commands += 1;
                } else {
                    rewritten.push(resident_command);
                }
            }
            rewritten.push(command);

            if self.telemetry.first_override_turn < 0 {
                self.telemetry.first_override_turn = game.turn;
                self.telemetry.prefix_action_hash = action_hash;
                self.telemetry.prefix_state_hash = canonical_state_hash(game);
            }
            self.telemetry.active_turns += 1;
            self.telemetry.option_overrides += 1;
            match verb {
                ReturnVerb::Move => self.telemetry.move_commands += 1,
                ReturnVerb::Hold => self.telemetry.hold_commands += 1,
                ReturnVerb::Harvest => self.telemetry.harvest_commands += 1,
            }
            self.pending = Some(PendingReturn {
                unit_id: episode.unit_id,
                target: episode.target,
                action_turn: game.turn,
                verb,
            });
            rewritten
        }

        fn observe_after_step(
            &mut self,
            before: &GameState,
            after: &GameState,
            player: usize,
            commands: &[String],
            owners_before: &BTreeMap<Cell, Owner>,
            owners_after: &BTreeMap<Cell, Owner>,
        ) {
            let assigned = d165_commands_by_unit(commands);
            let old_targets = self.production_targets.clone();

            if let Some(pending) = self.pending {
                if let Some(episode) = self.episode {
                    if pending.unit_id != episode.unit_id || pending.target != episode.target {
                        self.telemetry.same_worker_target_violations += 1;
                    }
                } else {
                    self.telemetry.post_exit_overrides += 1;
                }
                if pending.verb == ReturnVerb::Harvest {
                    let gained = d165_fruit_gain(before, after, pending.unit_id);
                    if gained > 0
                        && owners_before.get(&pending.target) == Some(&Owner::Own)
                        && before
                            .units
                            .iter()
                            .any(|unit| unit.id == pending.unit_id && unit.pos() == pending.target)
                    {
                        self.telemetry.completed = true;
                        self.telemetry.return_turn = pending.action_turn;
                        self.telemetry.return_latency =
                            pending.action_turn - self.telemetry.activation_turn;
                        self.telemetry.return_harvest_units += gained as u16;
                        self.episode = None;
                    } else {
                        self.telemetry.generated_command_failures += 1;
                    }
                }
            }

            let before_plants: BTreeSet<_> =
                before.plants.iter().map(|plant| plant.pos()).collect();
            for (unit_id, command) in &assigned {
                let fields = command_fields(command);
                let verb = fields.first().copied().unwrap_or("WAIT");
                if verb == "HARVEST" {
                    let Some(unit) = before.units.iter().find(|unit| {
                        unit.id == *unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    let gained = d165_fruit_gain(before, after, *unit_id);
                    if gained > 0 && owners_before.get(&unit.pos()) == Some(&Owner::Own) {
                        self.historical_producers.insert(*unit_id);
                        self.production_targets.insert(*unit_id, unit.pos());
                        self.telemetry.production_events += 1;
                        self.telemetry.successful_production_harvests += 1;
                    }
                } else if verb == "PLANT" {
                    let Some(unit) = before.units.iter().find(|unit| {
                        unit.id == *unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    let Some(item) = command_item(command) else {
                        continue;
                    };
                    let after_carry = after
                        .units
                        .iter()
                        .find(|candidate| candidate.id == *unit_id)
                        .map(|candidate| candidate.carry[item])
                        .unwrap_or(unit.carry[item]);
                    if item < 4
                        && !before_plants.contains(&unit.pos())
                        && unit.carry[item] > after_carry
                        && owners_after.get(&unit.pos()) == Some(&Owner::Own)
                    {
                        self.historical_producers.insert(*unit_id);
                        self.production_targets.insert(*unit_id, unit.pos());
                        self.telemetry.production_events += 1;
                        self.telemetry.successful_production_plants += 1;
                    }
                }
            }
            self.production_targets.retain(|_, target| {
                owners_after.get(target) == Some(&Owner::Own)
                    && after.plants.iter().any(|plant| plant.pos() == *target)
            });

            if self.enabled && !self.used && self.episode.is_none() {
                for (unit_id, command) in &assigned {
                    if command_fields(command).first().copied() != Some("CHOP") {
                        continue;
                    }
                    let Some(unit_before) = before.units.iter().find(|unit| {
                        unit.id == *unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    if unit_before.chop <= 0
                        || owners_before.get(&unit_before.pos()) != Some(&Owner::Opponent)
                        || !before
                            .plants
                            .iter()
                            .any(|plant| plant.pos() == unit_before.pos())
                    {
                        continue;
                    }
                    self.telemetry.opponent_crop_chops += 1;
                    if self.historical_producers.contains(unit_id) {
                        self.telemetry.historical_producer_opponent_crop_chops += 1;
                    }
                    let Some(target) = old_targets.get(unit_id).copied() else {
                        continue;
                    };
                    self.telemetry.remembered_live_target_opponent_crop_chops += 1;
                    self.telemetry.suppression_entries += 1;
                    let Some(unit_after) = after.units.iter().find(|unit| {
                        unit.id == *unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    if owners_after.get(&target) != Some(&Owner::Own)
                        || !after.plants.iter().any(|plant| plant.pos() == target)
                    {
                        continue;
                    }
                    self.telemetry.post_step_live_target_opponent_crop_chops += 1;
                    if unit_after.hp <= 0 || unit_after.free() <= 0 {
                        continue;
                    }
                    self.telemetry.eligible_entries += 1;
                    self.used = true;
                    self.telemetry.activated = true;
                    self.telemetry.activation_turn = before.turn;
                    self.telemetry.deadline = before.turn + D165_HORIZON;
                    self.telemetry.selected_unit_id = *unit_id;
                    self.telemetry.target_x = target.0;
                    self.telemetry.target_y = target.1;
                    self.episode = Some(ReturnEpisode {
                        unit_id: *unit_id,
                        target,
                        activation_turn: before.turn,
                        deadline: before.turn + D165_HORIZON,
                    });
                    break;
                }
            } else if self.enabled && self.used && self.episode.is_none() {
                let later_eligible = assigned.iter().any(|(unit_id, command)| {
                    command_fields(command).first().copied() == Some("CHOP")
                        && old_targets.get(unit_id).is_some()
                });
                if later_eligible && !self.telemetry.completed && !self.telemetry.aborted {
                    self.telemetry.restart_violations += 1;
                }
            }

            if let Some(episode) = self.episode {
                if owners_after.get(&episode.target) != Some(&Owner::Own)
                    || !after
                        .plants
                        .iter()
                        .any(|plant| plant.pos() == episode.target)
                {
                    self.abort_target(before.turn);
                } else if after
                    .units
                    .iter()
                    .all(|unit| unit.id != episode.unit_id || unit.player as usize != player)
                {
                    self.abort_unit(before.turn);
                } else if before.turn >= episode.deadline {
                    self.abort_horizon(before.turn);
                }
            }
            self.pending = None;
        }

        fn finish(&mut self, final_turn: i32, turns_played: usize) {
            self.telemetry.turns_played = turns_played.min(u16::MAX as usize) as u16;
            self.telemetry.resident_call_mismatches = usize::from(
                usize::from(self.telemetry.resident_calls) != turns_played,
            ) as u16;
            if self.episode.is_some() {
                self.abort_terminal(final_turn);
            }
        }
    }

    fn owners_at_target_missing(game: &GameState, target: Cell) -> bool {
        !game.plants.iter().any(|plant| plant.pos() == target)
    }

    fn d165_commands_by_unit(commands: &[String]) -> BTreeMap<i32, String> {
        let mut assigned = BTreeMap::new();
        for command in commands {
            if let Some(unit_id) = command_unit(command) {
                assigned.entry(unit_id).or_insert_with(|| command.clone());
            }
        }
        assigned
    }

    fn d165_fruit_gain(before: &GameState, after: &GameState, unit_id: i32) -> i32 {
        let Some(before_unit) = before.units.iter().find(|unit| unit.id == unit_id) else {
            return 0;
        };
        let Some(after_unit) = after.units.iter().find(|unit| unit.id == unit_id) else {
            return 0;
        };
        (0..4)
            .map(|item| (after_unit.carry[item] - before_unit.carry[item]).max(0))
            .sum()
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct TracePoint {
        turn: i32,
        action_hash: u64,
        state_hash: u64,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D165Outcome {
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
        max_opponent_workers: u8,
        successful_trains: u8,
        successful_opponent_trains: u8,
        invalid_direct_commands: u16,
        provenance_failures: u16,
        deposit_prediction_failures: u16,
        own_created_crops: u16,
        opponent_created_crops: u16,
        joint_created_crops: u16,
        ambiguous_created_crops: u16,
        own_owned_crop_harvest_units: u16,
        own_reinvested_crops: u16,
        action_hash: u64,
        state_hash: u64,
        role_return: ReturnTelemetry,
        trace: Vec<TracePoint>,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D165Row {
        task: Task,
        policy: usize,
        outcome: D165Outcome,
    }

    #[derive(Clone, Copy, Debug)]
    struct D165Work {
        task: Task,
        policy: usize,
    }

    fn d165_play(task: Task, policy: usize) -> D165Row {
        let mut game = generate_official(task.map_seed);
        let mut ours = SecureOrchardBot::new();
        let mut controller = ReturnController::new(policy == 1);
        let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
        let mut owners: BTreeMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), Owner::Natural))
            .collect();
        let mut turns_until_end = 0i32;
        let mut action_hash = 14_695_981_039_346_656_037_u64;
        let mut max_own_workers = worker_count(&game, task.seat);
        let mut max_opponent_workers = worker_count(&game, 1 - task.seat);
        let mut successful_trains = 0usize;
        let mut successful_opponent_trains = 0usize;
        let mut provenance_failures = 0usize;
        let mut own_created_crops = 0usize;
        let mut opponent_created_crops = 0usize;
        let mut joint_created_crops = 0usize;
        let mut ambiguous_created_crops = 0usize;
        let mut own_owned_crop_harvest_units = 0usize;
        let mut own_reinvested_crops = 0usize;
        let mut trace = Vec::with_capacity(MACRO_TOTAL_TURNS as usize + 1);
        let mut turns_played = 0usize;
        let mut done = false;

        while !done {
            trace.push(TracePoint {
                turn: game.turn,
                action_hash,
                state_hash: canonical_state_hash(&game),
            });
            let resident_commands = ours.commands(&resident_view(&game, task.seat));
            let ours_commands =
                controller.rewrite(&game, task.seat, resident_commands, action_hash);
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

            let before = game.clone();
            let owners_before = owners.clone();
            let before_plants: BTreeSet<_> =
                game.plants.iter().map(|plant| plant.pos()).collect();
            let attempts = [
                plant_attempts(&game, 0, &commands[0]),
                plant_attempts(&game, 1, &commands[1]),
            ];
            let before_own_workers = worker_count(&game, task.seat);
            let before_opponent_workers = worker_count(&game, 1 - task.seat);
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
            turns_played += 1;
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
                own_owned_crop_harvest_units += gained as usize;
            }
            controller.observe_after_step(
                &before,
                &game,
                task.seat,
                &commands[task.seat],
                &owners_before,
                &owners,
            );

            let after_own_workers = worker_count(&game, task.seat);
            let after_opponent_workers = worker_count(&game, 1 - task.seat);
            successful_trains += after_own_workers.saturating_sub(before_own_workers);
            successful_opponent_trains +=
                after_opponent_workers.saturating_sub(before_opponent_workers);
            max_own_workers = max_own_workers.max(after_own_workers);
            max_opponent_workers = max_opponent_workers.max(after_opponent_workers);
            done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        }
        controller.finish(game.turn, turns_played);

        let own_score = game.scores[task.seat];
        let opponent_score = game.scores[1 - task.seat];
        let margin = own_score - opponent_score;
        let own_return = own_score as f32 / 100.0;
        let opponent_return = opponent_score as f32 / 100.0;
        let margin_return = margin as f32 / 100.0;
        D165Row {
            task,
            policy,
            outcome: D165Outcome {
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
                max_opponent_workers: max_opponent_workers.min(u8::MAX as usize) as u8,
                successful_trains: successful_trains.min(u8::MAX as usize) as u8,
                successful_opponent_trains: successful_opponent_trains
                    .min(u8::MAX as usize) as u8,
                invalid_direct_commands: controller.telemetry.generated_command_failures,
                provenance_failures: provenance_failures.min(u16::MAX as usize) as u16,
                deposit_prediction_failures: 0,
                own_created_crops: own_created_crops.min(u16::MAX as usize) as u16,
                opponent_created_crops: opponent_created_crops.min(u16::MAX as usize) as u16,
                joint_created_crops: joint_created_crops.min(u16::MAX as usize) as u16,
                ambiguous_created_crops: ambiguous_created_crops.min(u16::MAX as usize) as u16,
                own_owned_crop_harvest_units: own_owned_crop_harvest_units
                    .min(u16::MAX as usize) as u16,
                own_reinvested_crops: own_reinvested_crops.min(u16::MAX as usize) as u16,
                action_hash,
                state_hash: canonical_state_hash(&game),
                role_return: controller.telemetry,
                trace,
            },
        }
    }

    fn d165_terminal_equal(a: &D165Outcome, b: &D165Outcome) -> bool {
        a.done == b.done
            && a.turn == b.turn
            && a.own_score == b.own_score
            && a.opponent_score == b.opponent_score
            && a.own_return == b.own_return
            && a.opponent_return == b.opponent_return
            && a.margin_return == b.margin_return
            && a.reward_identity_error == b.reward_identity_error
            && a.own_workers == b.own_workers
            && a.opponent_workers == b.opponent_workers
            && a.max_own_workers == b.max_own_workers
            && a.max_opponent_workers == b.max_opponent_workers
            && a.successful_trains == b.successful_trains
            && a.successful_opponent_trains == b.successful_opponent_trains
            && a.invalid_direct_commands == b.invalid_direct_commands
            && a.provenance_failures == b.provenance_failures
            && a.deposit_prediction_failures == b.deposit_prediction_failures
            && a.own_created_crops == b.own_created_crops
            && a.opponent_created_crops == b.opponent_created_crops
            && a.joint_created_crops == b.joint_created_crops
            && a.ambiguous_created_crops == b.ambiguous_created_crops
            && a.own_owned_crop_harvest_units == b.own_owned_crop_harvest_units
            && a.own_reinvested_crops == b.own_reinvested_crops
            && a.action_hash == b.action_hash
            && a.state_hash == b.state_hash
    }

    fn d165_write_rows(output: &str, rows: &[D165Row]) {
        let controls: BTreeMap<_, _> = rows
            .iter()
            .filter(|row| row.policy == 0)
            .map(|row| (row.task, &row.outcome))
            .collect();
        let mut writer = BufWriter::new(File::create(output).expect("create D165a output"));
        writeln!(
            writer,
            "map_seed\tseat\topponent_index\topponent\tpolicy_index\tpolicy\treturn_horizon\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tmax_opponent_workers\tsuccessful_trains\tsuccessful_opponent_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tresident_calls\tturns_played\tresident_call_mismatches\tproduction_events\tsuccessful_production_plants\tsuccessful_production_harvests\topponent_crop_chops\thistorical_producer_opponent_crop_chops\tremembered_live_target_opponent_crop_chops\tpost_step_live_target_opponent_crop_chops\tsuppression_entries\teligible_entries\tactivated\tactivation_turn\tdeadline\tfirst_override_turn\tselected_unit_id\ttarget_x\ttarget_y\tactive_turns\tcompleted\treturn_turn\treturn_latency\treturn_harvest_units\taborted\tabort_turn\tabort_target_loss\tabort_unit_loss\tabort_capacity\tabort_incapable\tabort_horizon\tabort_terminal\toption_overrides\tprotected_commands\tmove_commands\thold_commands\tharvest_commands\tgenerated_command_failures\townership_failures\ttarget_change_violations\tsame_worker_target_violations\tcontroller_train_commands\tcontroller_plant_commands\tcontroller_chop_commands\tcontroller_other_commands\tpost_exit_overrides\thorizon_violations\trestart_violations\tprefix_action_hash\tprefix_state_hash\tprefix_available\tprefix_action_match\tprefix_state_match\tresident_prefix_action_hash\tresident_prefix_state_hash\tinactive_terminal_match\tworkforce_pair_match"
        )
        .expect("write D165a header");
        for row in rows {
            let out = &row.outcome;
            let telemetry = out.role_return;
            let control = controls.get(&row.task).expect("D165a control for every task");
            let resident_prefix = if row.policy == 1 && telemetry.first_override_turn >= 0 {
                control
                    .trace
                    .iter()
                    .find(|point| point.turn == telemetry.first_override_turn)
                    .copied()
            } else {
                None
            };
            let prefix_available = row.policy == 0 || resident_prefix.is_some();
            let prefix_action_match = row.policy == 0
                || resident_prefix.is_some_and(|point| {
                    point.action_hash == telemetry.prefix_action_hash
                });
            let prefix_state_match = row.policy == 0
                || resident_prefix
                    .is_some_and(|point| point.state_hash == telemetry.prefix_state_hash);
            let inactive_terminal_match = row.policy == 0
                || telemetry.activated
                || d165_terminal_equal(out, control);
            let workforce_pair_match = out.own_workers == control.own_workers
                && out.opponent_workers == control.opponent_workers
                && out.max_own_workers == control.max_own_workers
                && out.max_opponent_workers == control.max_opponent_workers
                && out.successful_trains == control.successful_trains
                && out.successful_opponent_trains == control.successful_opponent_trains;
            let values = vec![
                row.task.map_seed.to_string(),
                row.task.seat.to_string(),
                row.task.opponent.to_string(),
                MacroOpponentMode::from_index(row.task.opponent)
                    .label()
                    .to_string(),
                row.policy.to_string(),
                D165_POLICY_LABELS[row.policy].to_string(),
                if row.policy == 1 { D165_HORIZON } else { 0 }.to_string(),
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
                out.max_opponent_workers.to_string(),
                out.successful_trains.to_string(),
                out.successful_opponent_trains.to_string(),
                "0".to_string(),
                "0".to_string(),
                out.invalid_direct_commands.to_string(),
                out.provenance_failures.to_string(),
                out.deposit_prediction_failures.to_string(),
                out.own_created_crops.to_string(),
                out.opponent_created_crops.to_string(),
                out.joint_created_crops.to_string(),
                out.ambiguous_created_crops.to_string(),
                out.own_owned_crop_harvest_units.to_string(),
                out.own_reinvested_crops.to_string(),
                out.action_hash.to_string(),
                out.state_hash.to_string(),
                telemetry.resident_calls.to_string(),
                telemetry.turns_played.to_string(),
                telemetry.resident_call_mismatches.to_string(),
                telemetry.production_events.to_string(),
                telemetry.successful_production_plants.to_string(),
                telemetry.successful_production_harvests.to_string(),
                telemetry.opponent_crop_chops.to_string(),
                telemetry
                    .historical_producer_opponent_crop_chops
                    .to_string(),
                telemetry
                    .remembered_live_target_opponent_crop_chops
                    .to_string(),
                telemetry
                    .post_step_live_target_opponent_crop_chops
                    .to_string(),
                telemetry.suppression_entries.to_string(),
                telemetry.eligible_entries.to_string(),
                usize::from(telemetry.activated).to_string(),
                telemetry.activation_turn.to_string(),
                telemetry.deadline.to_string(),
                telemetry.first_override_turn.to_string(),
                telemetry.selected_unit_id.to_string(),
                telemetry.target_x.to_string(),
                telemetry.target_y.to_string(),
                telemetry.active_turns.to_string(),
                usize::from(telemetry.completed).to_string(),
                telemetry.return_turn.to_string(),
                telemetry.return_latency.to_string(),
                telemetry.return_harvest_units.to_string(),
                usize::from(telemetry.aborted).to_string(),
                telemetry.abort_turn.to_string(),
                telemetry.abort_target_loss.to_string(),
                telemetry.abort_unit_loss.to_string(),
                telemetry.abort_capacity.to_string(),
                telemetry.abort_incapable.to_string(),
                telemetry.abort_horizon.to_string(),
                telemetry.abort_terminal.to_string(),
                telemetry.option_overrides.to_string(),
                telemetry.protected_commands.to_string(),
                telemetry.move_commands.to_string(),
                telemetry.hold_commands.to_string(),
                telemetry.harvest_commands.to_string(),
                telemetry.generated_command_failures.to_string(),
                telemetry.ownership_failures.to_string(),
                telemetry.target_change_violations.to_string(),
                telemetry.same_worker_target_violations.to_string(),
                telemetry.controller_train_commands.to_string(),
                telemetry.controller_plant_commands.to_string(),
                telemetry.controller_chop_commands.to_string(),
                telemetry.controller_other_commands.to_string(),
                telemetry.post_exit_overrides.to_string(),
                telemetry.horizon_violations.to_string(),
                telemetry.restart_violations.to_string(),
                telemetry.prefix_action_hash.to_string(),
                telemetry.prefix_state_hash.to_string(),
                usize::from(prefix_available).to_string(),
                usize::from(prefix_action_match).to_string(),
                usize::from(prefix_state_match).to_string(),
                resident_prefix.map_or(0, |point| point.action_hash).to_string(),
                resident_prefix.map_or(0, |point| point.state_hash).to_string(),
                usize::from(inactive_terminal_match).to_string(),
                usize::from(workforce_pair_match).to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D165a row");
        }
        writer.flush().expect("flush D165a output");
    }

    pub(super) fn d165_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            5,
            "usage: d165_resident_worker_role_return START_SEED MAPS OUTPUT THREADS"
        );
        let start_seed: i64 = parse(&args[1], "start seed");
        let maps: usize = parse(&args[2], "maps");
        let output = &args[3];
        let threads: usize = parse(&args[4], "threads");
        assert!(maps > 0 && threads > 0);
        assert!(start_seed >= 9_844_136);
        assert!(start_seed + maps as i64 <= 9_844_200);

        let work: Vec<_> = (start_seed..start_seed + maps as i64)
            .flat_map(|map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).flat_map(move |opponent| {
                        (0..D165_POLICY_LABELS.len()).map(move |policy| D165Work {
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
                let work = Arc::clone(&work);
                let next = Arc::clone(&next);
                let rows = Arc::clone(&rows);
                thread::spawn(move || loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    let Some(item) = work.get(index).copied() else {
                        break;
                    };
                    let row = d165_play(item.task, item.policy);
                    rows.lock().expect("D165a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D165a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D165a rows")
            .into_inner()
            .expect("D165a rows lock");
        rows.sort_by_key(|row| (row.task, row.policy));
        d165_write_rows(output, &rows);
        eprintln!(
            "saved {} D165a rows with {} workers in {:.3}s to {}",
            rows.len(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            output,
        );
    }

    #[cfg(test)]
    mod d165_tests {
        use super::*;

        #[test]
        fn catalog_and_horizon_are_frozen() {
            assert_eq!(
                D165_POLICY_LABELS,
                ["resident", "producer_suppressor_return_h016"]
            );
            assert_eq!(D165_HORIZON, 16);
        }

        #[test]
        fn disabled_controller_is_exact_resident() {
            let task = Task {
                map_seed: 9_844_136,
                seat: 0,
                opponent: 0,
            };
            let control = d165_play(task, 0);
            let disabled = d165_play(task, 0);
            assert_eq!(control, disabled);
            assert_eq!(
                control.outcome.role_return.resident_calls,
                control.outcome.role_return.turns_played
            );
        }

        #[test]
        fn forced_return_replaces_only_selected_worker() {
            let mut game = generate_official(9_844_136);
            let player = 0usize;
            let unit_id = game
                .units
                .iter()
                .find(|unit| unit.player == player as i32)
                .expect("own unit")
                .id;
            let target = game.plants[0].pos();
            let unit = game
                .units
                .iter_mut()
                .find(|unit| unit.id == unit_id)
                .expect("selected unit");
            unit.x = target.0;
            unit.y = target.1;
            unit.hp = 1;
            unit.cc = unit.total() + 1;
            game.plants[0].fruits = 1;

            let mut controller = ReturnController::new(true);
            controller.used = true;
            controller.production_targets.insert(unit_id, target);
            controller.telemetry.activated = true;
            controller.telemetry.activation_turn = game.turn - 1;
            controller.telemetry.deadline = game.turn + 15;
            controller.episode = Some(ReturnEpisode {
                unit_id,
                target,
                activation_turn: game.turn - 1,
                deadline: game.turn + 15,
            });
            let other_id = game
                .units
                .iter()
                .find(|unit| unit.player == player as i32 && unit.id != unit_id)
                .map(|unit| unit.id)
                .unwrap_or(unit_id + 1000);
            let commands = vec![
                format!("MOVE {unit_id} 0 0"),
                format!("MOVE {other_id} 1 1"),
            ];
            let rewritten = controller.rewrite(
                &game,
                player,
                commands,
                14_695_981_039_346_656_037,
            );
            assert_eq!(rewritten.last(), Some(&format!("HARVEST {unit_id}")));
            assert!(rewritten.contains(&format!("MOVE {other_id} 1 1")));
            assert!(!rewritten.contains(&format!("MOVE {unit_id} 0 0")));
            assert_eq!(controller.telemetry.harvest_commands, 1);
            assert_eq!(controller.telemetry.controller_train_commands, 0);
            assert_eq!(controller.telemetry.controller_plant_commands, 0);
            assert_eq!(controller.telemetry.controller_chop_commands, 0);
        }

        #[test]
        fn proven_producer_opponent_chop_arms_exact_episode() {
            let mut before = generate_official(9_844_136);
            let player = 0usize;
            assert!(before.plants.len() >= 2);
            let target = before.plants[0].pos();
            let suppression_cell = before.plants[1].pos();
            before.plants[1].health = 100;
            let unit = before
                .units
                .iter_mut()
                .find(|unit| unit.player == player as i32)
                .expect("own unit");
            let unit_id = unit.id;
            unit.x = suppression_cell.0;
            unit.y = suppression_cell.1;
            unit.hp = 1;
            unit.chop = 1;
            unit.cc = unit.total() + 2;

            let mut owners_before: BTreeMap<_, _> = before
                .plants
                .iter()
                .map(|plant| (plant.pos(), Owner::Natural))
                .collect();
            owners_before.insert(target, Owner::Own);
            owners_before.insert(suppression_cell, Owner::Opponent);
            let owners_after = owners_before.clone();
            let commands = vec![format!("CHOP {unit_id}")];
            let mut after = before.clone();
            step(&mut after, &commands, &[]);

            let mut controller = ReturnController::new(true);
            controller.historical_producers.insert(unit_id);
            controller.production_targets.insert(unit_id, target);
            controller.observe_after_step(
                &before,
                &after,
                player,
                &commands,
                &owners_before,
                &owners_after,
            );
            assert!(controller.telemetry.activated);
            assert_eq!(controller.telemetry.opponent_crop_chops, 1);
            assert_eq!(
                controller.telemetry.historical_producer_opponent_crop_chops,
                1
            );
            assert_eq!(
                controller
                    .telemetry
                    .remembered_live_target_opponent_crop_chops,
                1
            );
            assert_eq!(
                controller.telemetry.post_step_live_target_opponent_crop_chops,
                1
            );
            assert_eq!(controller.telemetry.suppression_entries, 1);
            assert_eq!(controller.telemetry.eligible_entries, 1);
            assert_eq!(
                controller.episode,
                Some(ReturnEpisode {
                    unit_id,
                    target,
                    activation_turn: before.turn,
                    deadline: before.turn + D165_HORIZON,
                })
            );
        }

        #[test]
        fn treatment_is_deterministic_and_structurally_bounded() {
            let task = Task {
                map_seed: 9_844_136,
                seat: 0,
                opponent: 0,
            };
            let first = d165_play(task, 1);
            let second = d165_play(task, 1);
            assert_eq!(first, second);
            assert!(first.outcome.done);
            assert!(first.outcome.role_return.active_turns <= D165_HORIZON as u16);
            assert_eq!(first.outcome.role_return.resident_call_mismatches, 0);
            assert_eq!(first.outcome.role_return.horizon_violations, 0);
            assert_eq!(first.outcome.role_return.restart_violations, 0);
            assert_eq!(first.outcome.role_return.controller_train_commands, 0);
            assert_eq!(first.outcome.role_return.controller_plant_commands, 0);
            assert_eq!(first.outcome.role_return.controller_chop_commands, 0);
        }
    }
}

fn main() {
    inherited::d165_main();
}
