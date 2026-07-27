//! D168a: bounded BANK_SEED successor option (ARM_A post-return, ARM_B pre-carry)
//! over the exact resident. See
//! `data/analysis/live-agent-6553250/d168a-bank-seed-successor-option-protocol-2026-07-27.md`.

#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    // ── copied byte-for-byte from d166_producer_job_successor_affordance.rs via
    // d167a_successor_acquisition_path.rs — reproduces D166/D167's frozen
    // production-history bookkeeping exactly. Do not edit; D168a's integrity gate
    // requires this to reproduce D166/D167's own 1,024/237/135 counts on CONTROL. ──

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum ProductionVerb {
        Plant,
        Harvest,
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
        let before_plants: BTreeSet<_> = before.plants.iter().map(|plant| plant.pos()).collect();
        let mut result = Vec::new();
        for (unit_id, command) in d166_commands_by_unit(commands) {
            let fields = command_fields(&command);
            match fields.first().copied().unwrap_or("WAIT") {
                "HARVEST" => {
                    let Some(unit) = before
                        .units
                        .iter()
                        .find(|unit| unit.id == unit_id && unit.player as usize == player)
                    else {
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
                    let Some(unit) = before
                        .units
                        .iter()
                        .find(|unit| unit.id == unit_id && unit.player as usize == player)
                    else {
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

    /// Same entry predicate as D166/D167: the first turn (ascending unit_id among
    /// ties) a historical producer issues CHOP against a live Opponent-owned
    /// plant it currently stands on. Returns (unit_id, cell). Pure / read-only.
    fn d168a_entry_candidate(
        game: &GameState,
        player: usize,
        owners: &BTreeMap<Cell, Owner>,
        history: &BTreeMap<i32, ProductionRecord>,
        commands_for_player: &[String],
    ) -> Option<(i32, Cell)> {
        for (unit_id, command) in d166_commands_by_unit(commands_for_player) {
            if command_fields(&command).first().copied() != Some("CHOP") {
                continue;
            }
            let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == unit_id && unit.player as usize == player)
            else {
                continue;
            };
            if unit.chop <= 0
                || owners.get(&unit.pos()) != Some(&Owner::Opponent)
                || !game.plants.iter().any(|plant| plant.pos() == unit.pos())
            {
                continue;
            }
            if !history.contains_key(&unit_id) {
                continue;
            }
            return Some((unit_id, unit.pos()));
        }
        None
    }

    /// Same nearest-legal-empty-cell BFS already frozen in D166/D167's own
    /// `p_empty` computation, reused unchanged as "the resident's own
    /// legal-plant-cell preference" proxy.
    fn nearest_empty_cell(game: &GameState, from: Cell) -> Option<Cell> {
        let plant_cells: BTreeSet<Cell> = game.plants.iter().map(|plant| plant.pos()).collect();
        let distances = bfs_distances(&game.walkable, &[from]);
        game.walkable
            .iter()
            .copied()
            .filter(|cell| !plant_cells.contains(cell))
            .filter_map(|cell| distances.get(&cell).copied().map(|distance| (distance, cell)))
            .min()
            .map(|(_, cell)| cell)
    }

    fn near_shack(game: &GameState, player: usize, unit: &Unit) -> bool {
        manhattan(unit.pos(), game.shacks[player]) == 1
    }

    fn bank_fruit_total(game: &GameState, player: usize) -> i32 {
        (0..4).map(|idx| game.inventories[player][idx]).sum()
    }

    const BANANA: usize = 3;

    /// Lower value = higher priority when deposited counts tie.
    fn species_priority(idx: usize) -> i32 {
        match idx {
            BANANA => 0,
            i if i == APPLE => 1,
            i if i == PLUM => 2,
            i if i == LEMON => 3,
            _ => 4,
        }
    }

    /// Most abundant deposited fruit species; ties broken BANANA>APPLE>PLUM>LEMON.
    fn choose_species(deposited: &[i32; 6]) -> Option<usize> {
        (0..4)
            .filter(|&idx| deposited[idx] > 0)
            .max_by_key(|&idx| (deposited[idx], -species_priority(idx)))
    }

    // ── D168a policies and bounded option state machine ─────────────────────────

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    pub(super) enum Policy {
        Control,
        ArmA,
        ArmB,
    }

    impl Policy {
        pub(super) const ALL: [Self; 3] = [Self::Control, Self::ArmA, Self::ArmB];

        fn label(self) -> &'static str {
            match self {
                Self::Control => "control",
                Self::ArmA => "arm_a_post_return",
                Self::ArmB => "arm_b_pre_carry",
            }
        }

        fn horizon(self) -> i32 {
            match self {
                Self::Control => 0,
                Self::ArmA => 24,
                Self::ArmB => 32,
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum AbortReason {
        None,
        EmptyBankAtPick,
        NoLegalCell,
        Horizon,
        ChopJobInvalidated,
        WorkerMissing,
    }

    impl AbortReason {
        fn label(self) -> &'static str {
            match self {
                Self::None => "NONE",
                Self::EmptyBankAtPick => "EMPTY_BANK_AT_PICK",
                Self::NoLegalCell => "NO_LEGAL_CELL",
                Self::Horizon => "HORIZON",
                Self::ChopJobInvalidated => "CHOP_JOB_INVALIDATED",
                Self::WorkerMissing => "WORKER_MISSING",
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Phase {
        AcquireSeed,
        ReturnToChop,
        SeekPlantCell,
    }

    fn phase_for(policy: Policy, unit: &Unit, chop_commands: u16) -> Phase {
        if unit.total() == 0 {
            Phase::AcquireSeed
        } else if policy == Policy::ArmB && chop_commands == 0 {
            Phase::ReturnToChop
        } else {
            Phase::SeekPlantCell
        }
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D168aOptionTelemetry {
        gate_bank_ok: bool,
        gate_carry_ok: bool,
        activated: bool,
        activation_turn: i32,
        deadline: i32,
        committed: bool,
        committed_turn: i32,
        aborted: bool,
        abort_reason: AbortReason,
        species_picked: i32,
        species_planted: i32,
        plant_cell_x: i32,
        plant_cell_y: i32,
        chop_cell_x: i32,
        chop_cell_y: i32,
        move_commands: u16,
        pick_commands: u16,
        chop_commands: u16,
        plant_commands: u16,
        hold_commands: u16,
        pick_attempts: u16,
        pick_successes: u16,
        plant_attempts: u16,
        plant_successes: u16,
        chop_attempts: u16,
        chop_successes: u16,
        vocabulary_violations: u16,
        active_turns: u16,
    }

    impl D168aOptionTelemetry {
        fn new() -> Self {
            Self {
                gate_bank_ok: false,
                gate_carry_ok: false,
                activated: false,
                activation_turn: -1,
                deadline: -1,
                committed: false,
                committed_turn: -1,
                aborted: false,
                abort_reason: AbortReason::None,
                species_picked: -1,
                species_planted: -1,
                plant_cell_x: -1,
                plant_cell_y: -1,
                chop_cell_x: -1,
                chop_cell_y: -1,
                move_commands: 0,
                pick_commands: 0,
                chop_commands: 0,
                plant_commands: 0,
                hold_commands: 0,
                pick_attempts: 0,
                pick_successes: 0,
                plant_attempts: 0,
                plant_successes: 0,
                chop_attempts: 0,
                chop_successes: 0,
                vocabulary_violations: 0,
                active_turns: 0,
            }
        }

        fn active(&self) -> bool {
            self.activated && !self.committed && !self.aborted
        }
    }

    fn is_allowed_verb(policy: Policy, verb: &str) -> bool {
        match policy {
            Policy::Control => false,
            Policy::ArmA => matches!(verb, "MOVE" | "PICK" | "PLANT"),
            Policy::ArmB => matches!(verb, "MOVE" | "PICK" | "PLANT" | "CHOP"),
        }
    }

    /// Compute this turn's armed-worker override, or None for a deliberate hold.
    /// May instead set `telemetry.aborted`; callers must not apply any command
    /// (including hold) when that fires this same call.
    fn armed_command(
        policy: Policy,
        game: &GameState,
        player: usize,
        unit: &Unit,
        telemetry: &mut D168aOptionTelemetry,
    ) -> Option<String> {
        if game.turn >= telemetry.deadline {
            telemetry.aborted = true;
            telemetry.abort_reason = AbortReason::Horizon;
            return None;
        }
        match phase_for(policy, unit, telemetry.chop_commands) {
            Phase::AcquireSeed => {
                if !near_shack(game, player, unit) {
                    telemetry.move_commands += 1;
                    let shack = game.shacks[player];
                    Some(format!("MOVE {} {} {}", unit.id, shack.0, shack.1))
                } else {
                    match choose_species(&game.inventories[player]) {
                        None => {
                            telemetry.aborted = true;
                            telemetry.abort_reason = AbortReason::EmptyBankAtPick;
                            None
                        }
                        Some(idx) => {
                            telemetry.pick_commands += 1;
                            telemetry.pick_attempts += 1;
                            Some(format!("PICK {} {}", unit.id, ITEM_NAMES[idx]))
                        }
                    }
                }
            }
            Phase::ReturnToChop => {
                let cell = (telemetry.chop_cell_x, telemetry.chop_cell_y);
                if !game.plants.iter().any(|plant| plant.pos() == cell) {
                    telemetry.aborted = true;
                    telemetry.abort_reason = AbortReason::ChopJobInvalidated;
                    None
                } else if unit.pos() != cell {
                    telemetry.move_commands += 1;
                    Some(format!("MOVE {} {} {}", unit.id, cell.0, cell.1))
                } else {
                    telemetry.chop_commands += 1;
                    telemetry.chop_attempts += 1;
                    Some(format!("CHOP {}", unit.id))
                }
            }
            Phase::SeekPlantCell => match nearest_empty_cell(game, unit.pos()) {
                None => {
                    telemetry.aborted = true;
                    telemetry.abort_reason = AbortReason::NoLegalCell;
                    None
                }
                Some(cell) => {
                    if unit.pos() != cell {
                        telemetry.move_commands += 1;
                        Some(format!("MOVE {} {} {}", unit.id, cell.0, cell.1))
                    } else {
                        match (0..4).find(|&item| unit.carry[item] > 0) {
                            None => {
                                telemetry.hold_commands += 1;
                                None
                            }
                            Some(item) => {
                                telemetry.plant_commands += 1;
                                telemetry.plant_attempts += 1;
                                Some(format!("PLANT {} {}", unit.id, ITEM_NAMES[item]))
                            }
                        }
                    }
                }
            },
        }
    }

    fn remove_unit_command(commands: &mut Vec<String>, unit_id: i32) {
        commands.retain(|command| command_unit(command) != Some(unit_id));
    }

    fn replace_unit_command(commands: &mut Vec<String>, unit_id: i32, new_command: String) {
        remove_unit_command(commands, unit_id);
        commands.push(new_command);
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum IssuedVerb {
        None,
        Move,
        Pick(usize),
        Chop,
        Plant(usize),
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D168aOutcome {
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
        entry_captured: bool,
        entry_turn: i32,
        entry_unit_id: i32,
        generic_return_captured: bool,
        generic_return_turn: i32,
        generic_return_verb: i8,
        purity_violations: u16,
        option: D168aOptionTelemetry,
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D168aRow {
        task: Task,
        policy: Policy,
        outcome: D168aOutcome,
    }

    fn d168a_play(task: Task, policy: Policy) -> D168aRow {
        let mut game = generate_official(task.map_seed);
        let mut ours = SecureOrchardBot::new();
        let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
        let mut owners: BTreeMap<Cell, Owner> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), Owner::Natural))
            .collect();
        let mut birth_turns: BTreeMap<Cell, i32> =
            game.plants.iter().map(|plant| (plant.pos(), 0)).collect();
        let mut history: BTreeMap<i32, ProductionRecord> = BTreeMap::new();

        let mut entry_captured = false;
        let mut entry_turn: i32 = -1;
        let mut entry_unit_id: i32 = -1;

        let mut generic_return_captured = false;
        let mut generic_return_turn: i32 = -1;
        let mut generic_return_verb: i8 = -1;

        let mut telemetry = D168aOptionTelemetry::new();

        let mut action_hash = 14_695_981_039_346_656_037_u64;
        let mut turns_until_end = 0i32;
        let mut max_own_workers = worker_count(&game, task.seat);
        let mut successful_trains = 0usize;
        let mut provenance_failures = 0usize;
        let mut own_created_crops = 0usize;
        let mut opponent_created_crops = 0usize;
        let mut joint_created_crops = 0usize;
        let mut ambiguous_created_crops = 0usize;
        let mut own_owned_crop_harvest_units = 0usize;
        let mut own_reinvested_crops = 0usize;
        let mut purity_violations = 0usize;
        let mut done = false;

        while !done {
            let current_turn = game.turn;
            let resident_commands = ours.commands(&resident_view(&game, task.seat));
            let theirs_commands = theirs.commands(&game, 1 - task.seat);
            let mut seat_commands = resident_commands.clone();

            // ── entry-candidate detection: identical for all 3 policies, pre-step ──
            if !entry_captured {
                if let Some((unit_id, cell)) =
                    d168a_entry_candidate(&game, task.seat, &owners, &history, &resident_commands)
                {
                    entry_captured = true;
                    entry_turn = current_turn;
                    entry_unit_id = unit_id;
                    if policy == Policy::ArmB {
                        if let Some(unit) = game
                            .units
                            .iter()
                            .find(|unit| unit.id == unit_id && unit.player as usize == task.seat)
                        {
                            telemetry.gate_carry_ok = unit.total() == 0;
                            telemetry.gate_bank_ok = bank_fruit_total(&game, task.seat) > 0;
                            if telemetry.gate_carry_ok && telemetry.gate_bank_ok {
                                telemetry.activated = true;
                                telemetry.activation_turn = current_turn;
                                telemetry.deadline = current_turn + Policy::ArmB.horizon();
                                telemetry.chop_cell_x = cell.0;
                                telemetry.chop_cell_y = cell.1;
                            }
                        }
                    }
                }
            }

            // ── apply the armed-worker override, if active ──────────────────────
            let mut issued = IssuedVerb::None;
            let mut armed_pos_before: Option<Cell> = None;
            if policy != Policy::Control && telemetry.active() {
                let armed_unit = game
                    .units
                    .iter()
                    .find(|unit| unit.id == entry_unit_id && unit.player as usize == task.seat)
                    .cloned();
                match armed_unit {
                    None => {
                        telemetry.aborted = true;
                        telemetry.abort_reason = AbortReason::WorkerMissing;
                    }
                    Some(unit) => {
                        armed_pos_before = Some(unit.pos());
                        match armed_command(policy, &game, task.seat, &unit, &mut telemetry) {
                            Some(command) => {
                                let verb = command_fields(&command).first().copied().unwrap_or("");
                                if !is_allowed_verb(policy, verb) {
                                    telemetry.vocabulary_violations += 1;
                                } else {
                                    issued = match verb {
                                        "MOVE" => IssuedVerb::Move,
                                        "PICK" => IssuedVerb::Pick(
                                            command_item(&command).unwrap_or(usize::MAX),
                                        ),
                                        "CHOP" => IssuedVerb::Chop,
                                        "PLANT" => IssuedVerb::Plant(
                                            command_item(&command).unwrap_or(usize::MAX),
                                        ),
                                        _ => IssuedVerb::None,
                                    };
                                    replace_unit_command(&mut seat_commands, entry_unit_id, command);
                                    telemetry.active_turns += 1;
                                }
                            }
                            None => {
                                if !telemetry.aborted {
                                    remove_unit_command(&mut seat_commands, entry_unit_id);
                                    telemetry.hold_commands += 1;
                                    telemetry.active_turns += 1;
                                }
                            }
                        }
                    }
                }
            }

            // Controller-command purity: every unit other than the currently
            // armed one must carry exactly the resident's own command, every
            // turn, regardless of policy or activation state.
            {
                let mut resident_others: Vec<&String> = resident_commands
                    .iter()
                    .filter(|command| command_unit(command) != Some(entry_unit_id))
                    .collect();
                let mut seat_others: Vec<&String> = seat_commands
                    .iter()
                    .filter(|command| command_unit(command) != Some(entry_unit_id))
                    .collect();
                resident_others.sort();
                seat_others.sort();
                if resident_others != seat_others {
                    purity_violations += 1;
                }
            }

            let commands = if task.seat == 0 {
                [seat_commands, theirs_commands]
            } else {
                [theirs_commands, seat_commands]
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
            let before_plants: BTreeSet<_> = before.plants.iter().map(|plant| plant.pos()).collect();
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
                    (owners_before.get(&unit.pos()) == Some(&Owner::Own)).then_some((id, unit.carry))
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
                own_owned_crop_harvest_units += (0..4)
                    .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                    .sum::<i32>() as usize;
            }

            let after_cells: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
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
            for event in &production {
                if entry_captured
                    && !generic_return_captured
                    && event.unit_id == entry_unit_id
                    && event.record.turn > entry_turn
                {
                    generic_return_captured = true;
                    generic_return_turn = event.record.turn;
                    generic_return_verb = match event.record.verb {
                        ProductionVerb::Plant => 1,
                        ProductionVerb::Harvest => 2,
                    };
                }
            }
            for event in production {
                history.insert(event.unit_id, event.record);
            }

            // ── ARM_A activation: post-step ("P→S transition completion") ───────
            if policy == Policy::ArmA
                && entry_captured
                && entry_turn == current_turn
                && !telemetry.activated
            {
                telemetry.gate_bank_ok = bank_fruit_total(&game, task.seat) > 0;
                // gate_carry_ok is an ARM_B-only concept; left at its neutral default here.
                if telemetry.gate_bank_ok {
                    telemetry.activated = true;
                    telemetry.activation_turn = entry_turn;
                    telemetry.deadline = entry_turn + Policy::ArmA.horizon();
                }
            }

            // ── transaction verification for this turn's issued override ────────
            if let Some(pos_before) = armed_pos_before {
                let before_carry_of = |item: usize| -> i32 {
                    before
                        .units
                        .iter()
                        .find(|unit| unit.id == entry_unit_id)
                        .map(|unit| unit.carry[item])
                        .unwrap_or(0)
                };
                let after_carry_of = |item: usize| -> i32 {
                    game.units
                        .iter()
                        .find(|unit| unit.id == entry_unit_id)
                        .map(|unit| unit.carry[item])
                        .unwrap_or(0)
                };
                match issued {
                    IssuedVerb::Pick(item) if item < 4 => {
                        if after_carry_of(item) > before_carry_of(item) {
                            telemetry.pick_successes += 1;
                            telemetry.species_picked = item as i32;
                        }
                    }
                    IssuedVerb::Plant(item) if item < 4 => {
                        let planted_now = !before_plants.contains(&pos_before)
                            && owners.get(&pos_before) == Some(&Owner::Own)
                            && game.plants.iter().any(|plant| plant.pos() == pos_before);
                        if after_carry_of(item) < before_carry_of(item) && planted_now {
                            telemetry.plant_successes += 1;
                            telemetry.committed = true;
                            telemetry.committed_turn = before.turn;
                            telemetry.species_planted = item as i32;
                            telemetry.plant_cell_x = pos_before.0;
                            telemetry.plant_cell_y = pos_before.1;
                        }
                    }
                    IssuedVerb::Chop => {
                        let still_there = before.plants.iter().any(|plant| plant.pos() == pos_before);
                        let destroyed_or_damaged = !game
                            .plants
                            .iter()
                            .any(|plant| plant.pos() == pos_before && plant.health >= i32::MAX);
                        if still_there && destroyed_or_damaged {
                            telemetry.chop_successes += 1;
                        }
                    }
                    _ => {}
                }
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
        D168aRow {
            task,
            policy,
            outcome: D168aOutcome {
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
                invalid_direct_commands: telemetry.vocabulary_violations,
                provenance_failures: provenance_failures.min(u16::MAX as usize) as u16,
                deposit_prediction_failures: 0,
                own_created_crops: own_created_crops.min(u16::MAX as usize) as u16,
                opponent_created_crops: opponent_created_crops.min(u16::MAX as usize) as u16,
                joint_created_crops: joint_created_crops.min(u16::MAX as usize) as u16,
                ambiguous_created_crops: ambiguous_created_crops.min(u16::MAX as usize) as u16,
                own_owned_crop_harvest_units: own_owned_crop_harvest_units.min(u16::MAX as usize)
                    as u16,
                own_reinvested_crops: own_reinvested_crops.min(u16::MAX as usize) as u16,
                action_hash,
                state_hash: canonical_state_hash(&game),
                entry_captured,
                entry_turn,
                entry_unit_id,
                generic_return_captured,
                generic_return_turn,
                generic_return_verb,
                purity_violations: purity_violations.min(u16::MAX as usize) as u16,
                option: telemetry,
            },
        }
    }

    fn opt_i32(value: i32) -> String {
        value.to_string()
    }

    fn species_name(idx: i32) -> &'static str {
        match idx {
            0 => "PLUM",
            1 => "LEMON",
            2 => "APPLE",
            3 => "BANANA",
            _ => "NONE",
        }
    }

    fn d168a_write_rows(output: &str, rows: &[D168aRow]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D168a output"));
        writeln!(
            writer,
            "map_seed\tseat\topponent_index\topponent\tpolicy_index\tpolicy\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tentry_captured\tentry_turn\tentry_unit_id\tgeneric_return_captured\tgeneric_return_turn\tgeneric_return_verb\tpurity_violations\tgate_bank_ok\tgate_carry_ok\tactivated\tactivation_turn\tdeadline\tcommitted\tcommitted_turn\taborted\tabort_reason\tspecies_picked\tspecies_planted\tplant_cell_x\tplant_cell_y\tchop_cell_x\tchop_cell_y\tmove_commands\tpick_commands\tchop_commands\tplant_commands\thold_commands\tpick_attempts\tpick_successes\tplant_attempts\tplant_successes\tchop_attempts\tchop_successes\tvocabulary_violations\tactive_turns"
        )
        .expect("write D168a header");
        for row in rows {
            let out = &row.outcome;
            let option = out.option;
            let values = vec![
                row.task.map_seed.to_string(),
                row.task.seat.to_string(),
                row.task.opponent.to_string(),
                MacroOpponentMode::from_index(row.task.opponent).label().to_string(),
                Policy::ALL.iter().position(|policy| *policy == row.policy).unwrap().to_string(),
                row.policy.label().to_string(),
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
                usize::from(out.entry_captured).to_string(),
                opt_i32(out.entry_turn),
                opt_i32(out.entry_unit_id),
                usize::from(out.generic_return_captured).to_string(),
                opt_i32(out.generic_return_turn),
                out.generic_return_verb.to_string(),
                out.purity_violations.to_string(),
                usize::from(option.gate_bank_ok).to_string(),
                usize::from(option.gate_carry_ok).to_string(),
                usize::from(option.activated).to_string(),
                opt_i32(option.activation_turn),
                opt_i32(option.deadline),
                usize::from(option.committed).to_string(),
                opt_i32(option.committed_turn),
                usize::from(option.aborted).to_string(),
                option.abort_reason.label().to_string(),
                species_name(option.species_picked).to_string(),
                species_name(option.species_planted).to_string(),
                opt_i32(option.plant_cell_x),
                opt_i32(option.plant_cell_y),
                opt_i32(option.chop_cell_x),
                opt_i32(option.chop_cell_y),
                option.move_commands.to_string(),
                option.pick_commands.to_string(),
                option.chop_commands.to_string(),
                option.plant_commands.to_string(),
                option.hold_commands.to_string(),
                option.pick_attempts.to_string(),
                option.pick_successes.to_string(),
                option.plant_attempts.to_string(),
                option.plant_successes.to_string(),
                option.chop_attempts.to_string(),
                option.chop_successes.to_string(),
                option.vocabulary_violations.to_string(),
                option.active_turns.to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D168a row");
        }
        writer.flush().expect("flush D168a output");
    }

    #[derive(Clone, Copy, Debug)]
    struct D168aWork {
        task: Task,
        policy: Policy,
    }

    pub(super) fn d168a_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            5,
            "usage: d168a_bank_seed_successor_option START_SEED MAPS OUTPUT THREADS"
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
                        Policy::ALL.iter().map(move |policy| D168aWork {
                            task: Task {
                                map_seed,
                                seat,
                                opponent,
                            },
                            policy: *policy,
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
                    let row = d168a_play(item.task, item.policy);
                    rows.lock().expect("D168a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D168a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D168a rows")
            .into_inner()
            .expect("D168a rows lock");
        rows.sort_by_key(|row| {
            (
                row.task,
                Policy::ALL.iter().position(|policy| *policy == row.policy).unwrap(),
            )
        });
        d168a_write_rows(output, &rows);
        eprintln!(
            "saved {} D168a rows with {} workers in {:.3}s to {}",
            rows.len(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            output,
        );
    }

    #[cfg(test)]
    mod d168a_tests {
        use super::*;

        const TASK0: Task = Task {
            map_seed: 9_844_136,
            seat: 0,
            opponent: 0,
        };

        #[test]
        fn species_tie_break_prefers_banana_then_apple_then_plum_then_lemon() {
            assert_eq!(choose_species(&[1, 1, 1, 1, 0, 0]), Some(BANANA));
            assert_eq!(choose_species(&[1, 1, 1, 0, 0, 0]), Some(APPLE));
            assert_eq!(choose_species(&[1, 1, 0, 0, 0, 0]), Some(PLUM));
            assert_eq!(choose_species(&[0, 1, 0, 0, 0, 0]), Some(LEMON));
            assert_eq!(choose_species(&[0, 0, 0, 0, 5, 5]), None);
        }

        #[test]
        fn species_tie_break_prefers_larger_count_over_priority() {
            // LEMON has lowest priority but a strictly larger deposited count wins.
            assert_eq!(choose_species(&[0, 3, 0, 1, 0, 0]), Some(LEMON));
        }

        #[test]
        fn nearest_empty_cell_excludes_plant_cells_and_breaks_ties_by_xy() {
            let game = generate_official(9_844_136);
            let start = game.units[0].pos();
            let cell = nearest_empty_cell(&game, start);
            assert!(cell.is_some());
            let plant_cells: BTreeSet<Cell> = game.plants.iter().map(|plant| plant.pos()).collect();
            assert!(!plant_cells.contains(&cell.unwrap()));
        }

        #[test]
        fn control_is_deterministic_and_never_overrides() {
            let first = d168a_play(TASK0, Policy::Control);
            let second = d168a_play(TASK0, Policy::Control);
            assert_eq!(first, second);
            assert!(first.outcome.done);
            assert_eq!(first.outcome.option.activated, false);
            assert_eq!(first.outcome.option.active_turns, 0);
            assert_eq!(first.outcome.invalid_direct_commands, 0);
            assert_eq!(first.outcome.provenance_failures, 0);
            assert_eq!(first.outcome.ambiguous_created_crops, 0);
        }

        #[test]
        fn arm_a_and_arm_b_are_deterministic() {
            for policy in [Policy::ArmA, Policy::ArmB] {
                let first = d168a_play(TASK0, policy);
                let second = d168a_play(TASK0, policy);
                assert_eq!(first, second, "policy {:?} not deterministic", policy);
                assert!(first.outcome.done);
                assert_eq!(first.outcome.option.vocabulary_violations, 0);
            }
        }

        #[test]
        fn entry_event_is_identical_across_all_three_policies() {
            let control = d168a_play(TASK0, Policy::Control);
            let arm_a = d168a_play(TASK0, Policy::ArmA);
            let arm_b = d168a_play(TASK0, Policy::ArmB);
            assert_eq!(control.outcome.entry_captured, arm_a.outcome.entry_captured);
            assert_eq!(control.outcome.entry_captured, arm_b.outcome.entry_captured);
            if control.outcome.entry_captured {
                assert_eq!(control.outcome.entry_turn, arm_a.outcome.entry_turn);
                assert_eq!(control.outcome.entry_turn, arm_b.outcome.entry_turn);
                assert_eq!(control.outcome.entry_unit_id, arm_a.outcome.entry_unit_id);
                assert_eq!(control.outcome.entry_unit_id, arm_b.outcome.entry_unit_id);
            }
        }

        /// The game-relevant projection of an outcome: everything that must be
        /// byte-identical across policies when an arm never overrides anything.
        /// Excludes `option.gate_bank_ok`/`gate_carry_ok`, which are legitimate
        /// per-arm diagnostic reads (why the gate did or didn't fire) computed
        /// even on inactive tasks, and are not part of the simulated game state.
        #[derive(Debug, PartialEq)]
        struct GameRelevant {
            done: bool,
            turn: u16,
            own_score: i32,
            opponent_score: i32,
            own_return: f32,
            opponent_return: f32,
            margin_return: f32,
            own_workers: u8,
            opponent_workers: u8,
            max_own_workers: u8,
            successful_trains: u8,
            invalid_direct_commands: u16,
            provenance_failures: u16,
            own_created_crops: u16,
            opponent_created_crops: u16,
            joint_created_crops: u16,
            ambiguous_created_crops: u16,
            own_owned_crop_harvest_units: u16,
            action_hash: u64,
            state_hash: u64,
            entry_captured: bool,
            entry_turn: i32,
            entry_unit_id: i32,
        }

        fn game_relevant(outcome: &D168aOutcome) -> GameRelevant {
            GameRelevant {
                done: outcome.done,
                turn: outcome.turn,
                own_score: outcome.own_score,
                opponent_score: outcome.opponent_score,
                own_return: outcome.own_return,
                opponent_return: outcome.opponent_return,
                margin_return: outcome.margin_return,
                own_workers: outcome.own_workers,
                opponent_workers: outcome.opponent_workers,
                max_own_workers: outcome.max_own_workers,
                successful_trains: outcome.successful_trains,
                invalid_direct_commands: outcome.invalid_direct_commands,
                provenance_failures: outcome.provenance_failures,
                own_created_crops: outcome.own_created_crops,
                opponent_created_crops: outcome.opponent_created_crops,
                joint_created_crops: outcome.joint_created_crops,
                ambiguous_created_crops: outcome.ambiguous_created_crops,
                own_owned_crop_harvest_units: outcome.own_owned_crop_harvest_units,
                action_hash: outcome.action_hash,
                state_hash: outcome.state_hash,
                entry_captured: outcome.entry_captured,
                entry_turn: outcome.entry_turn,
                entry_unit_id: outcome.entry_unit_id,
            }
        }

        #[test]
        fn inactive_arm_is_byte_exact_vs_control() {
            // Scan a small span of tasks; whenever an arm's gate never fires,
            // its game-relevant outcome (scores/hashes/workforce/crops/entry
            // event) must equal control's exactly.
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        let control = d168a_play(task, Policy::Control);
                        for policy in [Policy::ArmA, Policy::ArmB] {
                            let arm = d168a_play(task, policy);
                            if !arm.outcome.option.activated {
                                assert_eq!(
                                    game_relevant(&control.outcome),
                                    game_relevant(&arm.outcome),
                                    "task {:?} policy {:?} inactive but not byte-exact",
                                    task, policy
                                );
                            }
                        }
                    }
                }
            }
        }

        #[test]
        fn armed_option_never_exceeds_its_horizon_and_commits_at_most_once() {
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        for policy in [Policy::ArmA, Policy::ArmB] {
                            let row = d168a_play(task, policy);
                            let option = row.outcome.option;
                            if option.activated {
                                assert!(
                                    i32::from(option.active_turns) <= policy.horizon() + 1,
                                    "task {:?} policy {:?} exceeded horizon",
                                    task,
                                    policy
                                );
                                assert!(!(option.committed && option.aborted));
                                assert_eq!(option.plant_successes <= 1, true);
                            }
                        }
                    }
                }
            }
        }

        #[test]
        fn controller_command_purity_holds_every_turn() {
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        for policy in Policy::ALL {
                            let row = d168a_play(task, policy);
                            assert_eq!(
                                row.outcome.purity_violations, 0,
                                "task {:?} policy {:?} had a non-armed-unit command deviation",
                                task, policy
                            );
                        }
                    }
                }
            }
        }
    }
}

fn main() {
    inherited::d168a_main();
}
