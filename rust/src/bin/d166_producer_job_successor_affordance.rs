//! D166a: read-only producer-job successor affordance audit.

#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum ProductionVerb {
        Plant,
        Harvest,
    }

    impl ProductionVerb {
        fn label(self) -> &'static str {
            match self {
                Self::Plant => "PLANT",
                Self::Harvest => "HARVEST",
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct ProductionRecord {
        verb: ProductionVerb,
        target: Cell,
        generation_birth_turn: i32,
        turn: i32,
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct SuccessfulProduction {
        unit_id: i32,
        record: ProductionRecord,
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct SuccessorAudit {
        entry_captured: bool,
        entry_turn: i32,
        selected_unit_id: i32,
        prior_verb: i8,
        prior_turn: i32,
        prior_x: i32,
        prior_y: i32,
        prior_generation_birth_turn: i32,
        prior_target_live: bool,
        worker_ms: i32,
        worker_cc: i32,
        worker_hp: i32,
        worker_chop: i32,
        worker_free: i32,
        worker_carry_plum: i32,
        worker_carry_lemon: i32,
        worker_carry_apple: i32,
        worker_carry_banana: i32,
        worker_carry_iron: i32,
        worker_carry_wood: i32,
        own_live_crops: u16,
        own_ripe_crops: u16,
        h_ripe_available: bool,
        h_ripe_x: i32,
        h_ripe_y: i32,
        h_ripe_distance: i32,
        h_ripe_fruits: i32,
        h_ripe_cooldown: i32,
        h_live_available: bool,
        h_live_x: i32,
        h_live_y: i32,
        h_live_distance: i32,
        h_live_fruits: i32,
        h_live_cooldown: i32,
        p_carry_available: bool,
        legal_empty_cells: u16,
        p_empty_x: i32,
        p_empty_y: i32,
        p_empty_distance: i32,
        natural_return: bool,
        natural_return_turn: i32,
        natural_return_latency: i32,
        natural_return_verb: i8,
        natural_return_x: i32,
        natural_return_y: i32,
        natural_return_generation_birth_turn: i32,
        natural_return_reuses_prior_cell: bool,
        natural_return_reuses_prior_generation: bool,
        entry_worker_failures: u16,
        history_failures: u16,
    }

    impl SuccessorAudit {
        fn new() -> Self {
            Self {
                entry_turn: -1,
                selected_unit_id: -1,
                prior_verb: -1,
                prior_turn: -1,
                prior_x: -1,
                prior_y: -1,
                prior_generation_birth_turn: -1,
                h_ripe_x: -1,
                h_ripe_y: -1,
                h_ripe_distance: -1,
                h_ripe_fruits: -1,
                h_ripe_cooldown: -1,
                h_live_x: -1,
                h_live_y: -1,
                h_live_distance: -1,
                h_live_fruits: -1,
                h_live_cooldown: -1,
                p_empty_x: -1,
                p_empty_y: -1,
                p_empty_distance: -1,
                natural_return_turn: -1,
                natural_return_latency: -1,
                natural_return_verb: -1,
                natural_return_x: -1,
                natural_return_y: -1,
                natural_return_generation_birth_turn: -1,
                ..Self::default()
            }
        }
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct AuditTelemetry {
        resident_calls: u16,
        turns_played: u16,
        resident_call_mismatches: u16,
        production_events: u16,
        successful_production_plants: u16,
        successful_production_harvests: u16,
        opponent_crop_chops: u16,
        historical_producer_opponent_crop_chops: u16,
        entry_restarts: u16,
        controller_commands: u16,
        successor: SuccessorAudit,
    }

    fn d166_commands_by_unit(commands: &[String]) -> BTreeMap<i32, String> {
        let mut assigned = BTreeMap::new();
        for command in commands {
            if let Some(unit_id) = command_unit(command) {
                assigned.entry(unit_id).or_insert_with(|| command.clone());
            }
        }
        assigned
    }

    fn d166_fruit_gain(before: &GameState, after: &GameState, unit_id: i32) -> i32 {
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

    fn d166_successful_production(
        before: &GameState,
        after: &GameState,
        player: usize,
        commands: &[String],
        owners_before: &BTreeMap<Cell, Owner>,
        owners_after: &BTreeMap<Cell, Owner>,
        birth_turns: &BTreeMap<Cell, i32>,
    ) -> Vec<SuccessfulProduction> {
        let before_plants: BTreeSet<_> =
            before.plants.iter().map(|plant| plant.pos()).collect();
        let mut result = Vec::new();
        for (unit_id, command) in d166_commands_by_unit(commands) {
            let fields = command_fields(&command);
            match fields.first().copied().unwrap_or("WAIT") {
                "HARVEST" => {
                    let Some(unit) = before.units.iter().find(|unit| {
                        unit.id == unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    if d166_fruit_gain(before, after, unit_id) > 0
                        && owners_before.get(&unit.pos()) == Some(&Owner::Own)
                    {
                        result.push(SuccessfulProduction {
                            unit_id,
                            record: ProductionRecord {
                                verb: ProductionVerb::Harvest,
                                target: unit.pos(),
                                generation_birth_turn: birth_turns
                                    .get(&unit.pos())
                                    .copied()
                                    .unwrap_or(-1),
                                turn: before.turn,
                            },
                        });
                    }
                }
                "PLANT" => {
                    let Some(unit) = before.units.iter().find(|unit| {
                        unit.id == unit_id && unit.player as usize == player
                    }) else {
                        continue;
                    };
                    let Some(item) = command_item(&command) else {
                        continue;
                    };
                    let after_carry = after
                        .units
                        .iter()
                        .find(|candidate| candidate.id == unit_id)
                        .map(|candidate| candidate.carry[item])
                        .unwrap_or(unit.carry[item]);
                    if item < 4
                        && !before_plants.contains(&unit.pos())
                        && unit.carry[item] > after_carry
                        && owners_after.get(&unit.pos()) == Some(&Owner::Own)
                    {
                        result.push(SuccessfulProduction {
                            unit_id,
                            record: ProductionRecord {
                                verb: ProductionVerb::Plant,
                                target: unit.pos(),
                                generation_birth_turn: before.turn,
                                turn: before.turn,
                            },
                        });
                    }
                }
                _ => {}
            }
        }
        result.sort_by_key(|event| event.unit_id);
        result
    }

    fn d166_capture_successor(
        game: &GameState,
        player: usize,
        owners: &BTreeMap<Cell, Owner>,
        birth_turns: &BTreeMap<Cell, i32>,
        prior: ProductionRecord,
        unit_id: i32,
        entry_turn: i32,
    ) -> SuccessorAudit {
        let mut result = SuccessorAudit::new();
        result.entry_captured = true;
        result.entry_turn = entry_turn;
        result.selected_unit_id = unit_id;
        result.prior_verb = match prior.verb {
            ProductionVerb::Plant => 1,
            ProductionVerb::Harvest => 2,
        };
        result.prior_turn = prior.turn;
        result.prior_x = prior.target.0;
        result.prior_y = prior.target.1;
        result.prior_generation_birth_turn = prior.generation_birth_turn;
        result.prior_target_live = owners.get(&prior.target) == Some(&Owner::Own)
            && game.plants.iter().any(|plant| plant.pos() == prior.target)
            && birth_turns.get(&prior.target) == Some(&prior.generation_birth_turn);

        let Some(unit) = game
            .units
            .iter()
            .find(|unit| unit.id == unit_id && unit.player as usize == player)
        else {
            result.entry_worker_failures += 1;
            return result;
        };
        result.worker_ms = unit.ms;
        result.worker_cc = unit.cc;
        result.worker_hp = unit.hp;
        result.worker_chop = unit.chop;
        result.worker_free = unit.free();
        result.worker_carry_plum = unit.carry[PLUM];
        result.worker_carry_lemon = unit.carry[LEMON];
        result.worker_carry_apple = unit.carry[APPLE];
        result.worker_carry_banana = unit.carry[3];
        result.worker_carry_iron = unit.carry[IRON];
        result.worker_carry_wood = unit.carry[5];

        let mut own_plants: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| owners.get(&plant.pos()) == Some(&Owner::Own))
            .collect();
        own_plants.sort_by_key(|plant| {
            (
                manhattan(unit.pos(), plant.pos()),
                plant.x,
                plant.y,
                plant.plant_type.as_str(),
            )
        });
        let ripe: Vec<_> = own_plants
            .iter()
            .copied()
            .filter(|plant| plant.fruits > 0)
            .collect();
        result.own_live_crops = own_plants.len().min(u16::MAX as usize) as u16;
        result.own_ripe_crops = ripe.len().min(u16::MAX as usize) as u16;
        if let Some(plant) = ripe.first() {
            result.h_ripe_x = plant.x;
            result.h_ripe_y = plant.y;
            result.h_ripe_distance = manhattan(unit.pos(), plant.pos());
            result.h_ripe_fruits = plant.fruits;
            result.h_ripe_cooldown = plant.cooldown;
            result.h_ripe_available = unit.hp > 0 && unit.free() > 0;
        }
        if let Some(plant) = own_plants.first() {
            result.h_live_x = plant.x;
            result.h_live_y = plant.y;
            result.h_live_distance = manhattan(unit.pos(), plant.pos());
            result.h_live_fruits = plant.fruits;
            result.h_live_cooldown = plant.cooldown;
            result.h_live_available = unit.hp > 0 && unit.free() > 0;
        }

        let plant_cells: BTreeSet<_> =
            game.plants.iter().map(|plant| plant.pos()).collect();
        let distances = bfs_distances(&game.walkable, &[unit.pos()]);
        let mut empty: Vec<_> = game
            .walkable
            .iter()
            .copied()
            .filter(|cell| !plant_cells.contains(cell))
            .filter_map(|cell| distances.get(&cell).copied().map(|distance| (distance, cell)))
            .collect();
        empty.sort_unstable();
        result.legal_empty_cells = empty.len().min(u16::MAX as usize) as u16;
        if let Some((distance, cell)) = empty.first().copied() {
            result.p_empty_x = cell.0;
            result.p_empty_y = cell.1;
            result.p_empty_distance = distance;
        }
        result.p_carry_available =
            unit.carry[..4].iter().sum::<i32>() > 0 && !empty.is_empty();
        result
    }

    fn d166_note_natural_return(
        audit: &mut SuccessorAudit,
        event: SuccessfulProduction,
    ) {
        if !audit.entry_captured
            || audit.natural_return
            || event.unit_id != audit.selected_unit_id
            || event.record.turn <= audit.entry_turn
        {
            return;
        }
        audit.natural_return = true;
        audit.natural_return_turn = event.record.turn;
        audit.natural_return_latency = event.record.turn - audit.entry_turn;
        audit.natural_return_verb = match event.record.verb {
            ProductionVerb::Plant => 1,
            ProductionVerb::Harvest => 2,
        };
        audit.natural_return_x = event.record.target.0;
        audit.natural_return_y = event.record.target.1;
        audit.natural_return_generation_birth_turn = event.record.generation_birth_turn;
        audit.natural_return_reuses_prior_cell =
            event.record.target == (audit.prior_x, audit.prior_y);
        audit.natural_return_reuses_prior_generation =
            audit.natural_return_reuses_prior_cell
                && event.record.generation_birth_turn == audit.prior_generation_birth_turn;
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D166Outcome {
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
        audit: AuditTelemetry,
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D166Row {
        task: Task,
        outcome: D166Outcome,
    }

    fn d166_play(task: Task) -> D166Row {
        let mut game = generate_official(task.map_seed);
        let mut ours = SecureOrchardBot::new();
        let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
        let mut owners: BTreeMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), Owner::Natural))
            .collect();
        let mut birth_turns: BTreeMap<_, _> =
            game.plants.iter().map(|plant| (plant.pos(), 0)).collect();
        let mut history: BTreeMap<i32, ProductionRecord> = BTreeMap::new();
        let mut telemetry = AuditTelemetry {
            successor: SuccessorAudit::new(),
            ..AuditTelemetry::default()
        };
        let mut turns_until_end = 0i32;
        let mut action_hash = 14_695_981_039_346_656_037_u64;
        let mut max_own_workers = worker_count(&game, task.seat);
        let mut successful_trains = 0usize;
        let mut provenance_failures = 0usize;
        let mut own_created_crops = 0usize;
        let mut opponent_created_crops = 0usize;
        let mut joint_created_crops = 0usize;
        let mut ambiguous_created_crops = 0usize;
        let mut own_owned_crop_harvest_units = 0usize;
        let mut own_reinvested_crops = 0usize;
        let mut turns_played = 0usize;
        let mut done = false;

        while !done {
            let ours_commands = ours.commands(&resident_view(&game, task.seat));
            telemetry.resident_calls += 1;
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
            let history_before = history.clone();
            let before_plants: BTreeSet<_> =
                before.plants.iter().map(|plant| plant.pos()).collect();
            let attempts = [
                plant_attempts(&before, 0, &commands[0]),
                plant_attempts(&before, 1, &commands[1]),
            ];
            let before_workers = worker_count(&before, task.seat);
            let harvest_ids = command_unit_ids(&commands[task.seat], "HARVEST");
            let own_crop_harvests: Vec<_> = harvest_ids
                .into_iter()
                .filter_map(|id| {
                    let unit = before
                        .units
                        .iter()
                        .find(|unit| unit.id == id && unit.player as usize == task.seat)?;
                    (owners_before.get(&unit.pos()) == Some(&Owner::Own))
                        .then_some((id, unit.carry))
                })
                .collect();
            let had_renewable_receipt = own_owned_crop_harvest_units > 0;

            step(&mut game, &commands[0], &commands[1]);
            turns_played += 1;
            let (failures, own_plants, opponent_plants, joint_plants, ambiguous_plants) =
                update_provenance(
                    &game,
                    &before_plants,
                    &attempts,
                    &mut owners,
                    task.seat,
                );
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
                own_owned_crop_harvest_units += (0..4)
                    .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                    .sum::<i32>() as usize;
            }

            let after_cells: BTreeSet<_> =
                game.plants.iter().map(|plant| plant.pos()).collect();
            birth_turns.retain(|cell, _| after_cells.contains(cell));
            for cell in after_cells.difference(&before_plants) {
                birth_turns.insert(*cell, before.turn);
            }
            let production = d166_successful_production(
                &before,
                &game,
                task.seat,
                &commands[task.seat],
                &owners_before,
                &owners,
                &birth_turns,
            );

            for (unit_id, command) in d166_commands_by_unit(&commands[task.seat]) {
                if command_fields(&command).first().copied() != Some("CHOP") {
                    continue;
                }
                let Some(unit) = before.units.iter().find(|unit| {
                    unit.id == unit_id && unit.player as usize == task.seat
                }) else {
                    continue;
                };
                if unit.chop <= 0
                    || owners_before.get(&unit.pos()) != Some(&Owner::Opponent)
                    || !before
                        .plants
                        .iter()
                        .any(|plant| plant.pos() == unit.pos())
                {
                    continue;
                }
                telemetry.opponent_crop_chops += 1;
                let Some(prior) = history_before.get(&unit_id).copied() else {
                    continue;
                };
                telemetry.historical_producer_opponent_crop_chops += 1;
                if !telemetry.successor.entry_captured {
                    telemetry.successor = d166_capture_successor(
                        &game,
                        task.seat,
                        &owners,
                        &birth_turns,
                        prior,
                        unit_id,
                        before.turn,
                    );
                }
            }

            for event in production {
                telemetry.production_events += 1;
                match event.record.verb {
                    ProductionVerb::Plant => telemetry.successful_production_plants += 1,
                    ProductionVerb::Harvest => telemetry.successful_production_harvests += 1,
                }
                d166_note_natural_return(&mut telemetry.successor, event);
                history.insert(event.unit_id, event.record);
            }

            let after_workers = worker_count(&game, task.seat);
            successful_trains += after_workers.saturating_sub(before_workers);
            max_own_workers = max_own_workers.max(after_workers);
            done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        }
        telemetry.turns_played = turns_played.min(u16::MAX as usize) as u16;
        telemetry.resident_call_mismatches =
            u16::from(usize::from(telemetry.resident_calls) != turns_played);

        let own_score = game.scores[task.seat];
        let opponent_score = game.scores[1 - task.seat];
        let margin = own_score - opponent_score;
        let own_return = own_score as f32 / 100.0;
        let opponent_return = opponent_score as f32 / 100.0;
        let margin_return = margin as f32 / 100.0;
        D166Row {
            task,
            outcome: D166Outcome {
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
                invalid_direct_commands: 0,
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
                audit: telemetry,
            },
        }
    }

    fn d166_verb_label(code: i8) -> &'static str {
        match code {
            1 => ProductionVerb::Plant.label(),
            2 => ProductionVerb::Harvest.label(),
            _ => "NONE",
        }
    }

    fn d166_write_rows(output: &str, rows: &[D166Row]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D166a output"));
        writeln!(
            writer,
            "map_seed\tseat\topponent_index\topponent\tpolicy\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tresident_calls\tturns_played\tresident_call_mismatches\tproduction_events\tsuccessful_production_plants\tsuccessful_production_harvests\topponent_crop_chops\thistorical_producer_opponent_crop_chops\tentry_captured\tentry_turn\tselected_unit_id\tprior_verb\tprior_turn\tprior_x\tprior_y\tprior_generation_birth_turn\tprior_target_live\tworker_ms\tworker_cc\tworker_hp\tworker_chop\tworker_free\tworker_carry_plum\tworker_carry_lemon\tworker_carry_apple\tworker_carry_banana\tworker_carry_iron\tworker_carry_wood\town_live_crops\town_ripe_crops\th_ripe_available\th_ripe_x\th_ripe_y\th_ripe_distance\th_ripe_fruits\th_ripe_cooldown\th_live_available\th_live_x\th_live_y\th_live_distance\th_live_fruits\th_live_cooldown\tp_carry_available\tlegal_empty_cells\tp_empty_x\tp_empty_y\tp_empty_distance\tnatural_return\tnatural_return_turn\tnatural_return_latency\tnatural_return_verb\tnatural_return_x\tnatural_return_y\tnatural_return_generation_birth_turn\tnatural_return_reuses_prior_cell\tnatural_return_reuses_prior_generation\tnatural_return_within16\tnatural_return_within32\tentry_worker_failures\thistory_failures\tentry_restarts\tcontroller_commands"
        )
        .expect("write D166a header");
        for row in rows {
            let out = row.outcome;
            let telemetry = out.audit;
            let audit = telemetry.successor;
            let values = vec![
                row.task.map_seed.to_string(),
                row.task.seat.to_string(),
                row.task.opponent.to_string(),
                MacroOpponentMode::from_index(row.task.opponent)
                    .label()
                    .to_string(),
                "resident".to_string(),
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
                telemetry.historical_producer_opponent_crop_chops.to_string(),
                usize::from(audit.entry_captured).to_string(),
                audit.entry_turn.to_string(),
                audit.selected_unit_id.to_string(),
                d166_verb_label(audit.prior_verb).to_string(),
                audit.prior_turn.to_string(),
                audit.prior_x.to_string(),
                audit.prior_y.to_string(),
                audit.prior_generation_birth_turn.to_string(),
                usize::from(audit.prior_target_live).to_string(),
                audit.worker_ms.to_string(),
                audit.worker_cc.to_string(),
                audit.worker_hp.to_string(),
                audit.worker_chop.to_string(),
                audit.worker_free.to_string(),
                audit.worker_carry_plum.to_string(),
                audit.worker_carry_lemon.to_string(),
                audit.worker_carry_apple.to_string(),
                audit.worker_carry_banana.to_string(),
                audit.worker_carry_iron.to_string(),
                audit.worker_carry_wood.to_string(),
                audit.own_live_crops.to_string(),
                audit.own_ripe_crops.to_string(),
                usize::from(audit.h_ripe_available).to_string(),
                audit.h_ripe_x.to_string(),
                audit.h_ripe_y.to_string(),
                audit.h_ripe_distance.to_string(),
                audit.h_ripe_fruits.to_string(),
                audit.h_ripe_cooldown.to_string(),
                usize::from(audit.h_live_available).to_string(),
                audit.h_live_x.to_string(),
                audit.h_live_y.to_string(),
                audit.h_live_distance.to_string(),
                audit.h_live_fruits.to_string(),
                audit.h_live_cooldown.to_string(),
                usize::from(audit.p_carry_available).to_string(),
                audit.legal_empty_cells.to_string(),
                audit.p_empty_x.to_string(),
                audit.p_empty_y.to_string(),
                audit.p_empty_distance.to_string(),
                usize::from(audit.natural_return).to_string(),
                audit.natural_return_turn.to_string(),
                audit.natural_return_latency.to_string(),
                d166_verb_label(audit.natural_return_verb).to_string(),
                audit.natural_return_x.to_string(),
                audit.natural_return_y.to_string(),
                audit.natural_return_generation_birth_turn.to_string(),
                usize::from(audit.natural_return_reuses_prior_cell).to_string(),
                usize::from(audit.natural_return_reuses_prior_generation).to_string(),
                usize::from(
                    audit.natural_return
                        && audit.natural_return_latency > 0
                        && audit.natural_return_latency <= 16,
                )
                .to_string(),
                usize::from(
                    audit.natural_return
                        && audit.natural_return_latency > 0
                        && audit.natural_return_latency <= 32,
                )
                .to_string(),
                audit.entry_worker_failures.to_string(),
                audit.history_failures.to_string(),
                telemetry.entry_restarts.to_string(),
                telemetry.controller_commands.to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D166a row");
        }
        writer.flush().expect("flush D166a output");
    }

    pub(super) fn d166_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            5,
            "usage: d166_producer_job_successor_affordance START_SEED MAPS OUTPUT THREADS"
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
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Task {
                        map_seed,
                        seat,
                        opponent,
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
                    let Some(task) = work.get(index).copied() else {
                        break;
                    };
                    let row = d166_play(task);
                    rows.lock().expect("D166a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D166a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D166a rows")
            .into_inner()
            .expect("D166a rows lock");
        rows.sort_by_key(|row| row.task);
        d166_write_rows(output, &rows);
        eprintln!(
            "saved {} D166a rows with {} workers in {:.3}s to {}",
            rows.len(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            output,
        );
    }

    #[cfg(test)]
    mod d166_tests {
        use super::*;

        #[test]
        fn ripe_and_plant_affordances_are_state_exact() {
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
            unit.hp = 1;
            unit.cc = unit.total() + 2;
            unit.carry[PLUM] = 1;
            game.plants[0].fruits = 1;
            let mut owners: BTreeMap<_, _> = game
                .plants
                .iter()
                .map(|plant| (plant.pos(), Owner::Natural))
                .collect();
            owners.insert(target, Owner::Own);
            let prior = ProductionRecord {
                verb: ProductionVerb::Plant,
                target,
                generation_birth_turn: 0,
                turn: 10,
            };
            let birth_turns: BTreeMap<_, _> =
                game.plants.iter().map(|plant| (plant.pos(), 0)).collect();
            let audit = d166_capture_successor(
                &game,
                player,
                &owners,
                &birth_turns,
                prior,
                unit_id,
                game.turn,
            );
            assert!(audit.entry_captured);
            assert!(audit.prior_target_live);
            assert!(audit.h_ripe_available);
            assert!(audit.h_live_available);
            assert!(audit.p_carry_available);
            assert!(audit.legal_empty_cells > 0);
        }

        #[test]
        fn exact_resident_audit_is_deterministic_and_read_only() {
            let task = Task {
                map_seed: 9_844_136,
                seat: 0,
                opponent: 0,
            };
            let first = d166_play(task);
            let second = d166_play(task);
            assert_eq!(first, second);
            assert!(first.outcome.done);
            assert_eq!(first.outcome.audit.controller_commands, 0);
            assert_eq!(first.outcome.audit.resident_call_mismatches, 0);
            assert_eq!(first.outcome.provenance_failures, 0);
            assert_eq!(first.outcome.ambiguous_created_crops, 0);
        }
    }
}

fn main() {
    inherited::d166_main();
}
