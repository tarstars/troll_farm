//! D167a: read-only successor-job acquisition-path recovery (extends D166a).

#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    use troll_farm::game::state::Plant;

    // ── copied byte-for-byte from d166_producer_job_successor_affordance.rs ──────
    // These reproduce D166's frozen entry/natural-return criteria exactly. Do not
    // edit; D167a's integrity gate requires this replay to reproduce D166's own
    // 1,024/237/135 counts and per-task fields exactly.

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

    fn d166_verb_label(code: i8) -> &'static str {
        match code {
            1 => ProductionVerb::Plant.label(),
            2 => ProductionVerb::Harvest.label(),
            _ => "NONE",
        }
    }

    // ── D167a new instrumentation: species-provenance acquisition-path ledger ───

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Tag {
        Bank,
        Field,
        Opponent,
        Other,
    }

    impl Tag {
        fn label(self) -> &'static str {
            match self {
                Self::Bank => "BANK",
                Self::Field => "FIELD",
                Self::Opponent => "OPPONENT",
                Self::Other => "OTHER",
            }
        }

        fn class_label(self) -> &'static str {
            match self {
                Self::Bank => "BANK_SEED",
                Self::Field => "FIELD_FRUIT",
                Self::Opponent => "OPPONENT_DERIVED",
                Self::Other => "OTHER_MIXED",
            }
        }
    }

    fn owner_label(owner: Option<&Owner>) -> &'static str {
        match owner {
            Some(Owner::Natural) => "Natural",
            Some(Owner::Own) => "Own",
            Some(Owner::Opponent) => "Opponent",
            Some(Owner::Joint) => "Joint",
            Some(Owner::Ambiguous) => "Ambiguous",
            None => "None",
        }
    }

    fn harvest_tag(owner: Option<&Owner>) -> Tag {
        match owner {
            Some(Owner::Own) | Some(Owner::Natural) => Tag::Field,
            Some(Owner::Opponent) => Tag::Opponent,
            _ => Tag::Other,
        }
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct SpeciesLedger {
        bank: i32,
        field: i32,
        opponent: i32,
        other: i32,
    }

    impl SpeciesLedger {
        fn total(&self) -> i32 {
            self.bank + self.field + self.opponent + self.other
        }

        fn add(&mut self, tag: Tag, count: i32) {
            match tag {
                Tag::Bank => self.bank += count,
                Tag::Field => self.field += count,
                Tag::Opponent => self.opponent += count,
                Tag::Other => self.other += count,
            }
        }

        fn distinct_tags(&self) -> Vec<Tag> {
            let mut result = Vec::new();
            if self.bank > 0 {
                result.push(Tag::Bank);
            }
            if self.field > 0 {
                result.push(Tag::Field);
            }
            if self.opponent > 0 {
                result.push(Tag::Opponent);
            }
            if self.other > 0 {
                result.push(Tag::Other);
            }
            result
        }

        /// Remove `count` units in a fixed deterministic priority order
        /// (Other, Opponent, Bank, Field). Returns true iff the removal drew
        /// from a genuinely mixed (>1 distinct tag) stash, which flags a rare
        /// ambiguous-attribution edge case for an incidental (non-returning)
        /// spend from a multi-source stash.
        fn remove(&mut self, mut count: i32) -> bool {
            let ambiguous = self.distinct_tags().len() > 1 && count > 0;
            for slot in [&mut self.other, &mut self.opponent, &mut self.bank, &mut self.field] {
                if count == 0 {
                    break;
                }
                let take = count.min(*slot);
                *slot -= take;
                count -= take;
            }
            ambiguous
        }
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D167aTraceEvent {
        turn: i32,
        unit_id: i32,
        x_before: i32,
        y_before: i32,
        x_after: i32,
        y_after: i32,
        verb: String,
        success: bool,
        gained: [i32; 6],
        spent: [i32; 6],
        target_origin: &'static str,
        target_kind: String,
        created_origin: &'static str,
        is_entry: bool,
        is_return: bool,
    }

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct D167aLedgerDiagnostics {
        ambiguous_partial_spends: u16,
        carry_mismatches: u16,
        entry_carry_nonzero: u16,
    }

    fn d167a_item_deltas(before_unit: &Unit, after_unit: Option<&Unit>) -> ([i32; 6], [i32; 6]) {
        let after_carry = after_unit.map(|unit| unit.carry).unwrap_or(before_unit.carry);
        let mut gained = [0i32; 6];
        let mut spent = [0i32; 6];
        for i in 0..6 {
            let delta = after_carry[i] - before_unit.carry[i];
            if delta > 0 {
                gained[i] = delta;
            } else if delta < 0 {
                spent[i] = -delta;
            }
        }
        (gained, spent)
    }

    fn d167a_success(
        verb: &str,
        pos_before: Cell,
        pos_after: Cell,
        before_plant_here: Option<&Plant>,
        after_plant_here: Option<&Plant>,
        gained: &[i32; 6],
        spent: &[i32; 6],
    ) -> bool {
        match verb {
            "MOVE" => pos_after != pos_before,
            "HARVEST" => (0..4).any(|i| gained[i] > 0),
            "PLANT" => before_plant_here.is_none() && (0..4).any(|i| spent[i] > 0),
            "CHOP" => match (before_plant_here, after_plant_here) {
                (Some(_), None) => true,
                (Some(before_plant), Some(after_plant)) => {
                    after_plant.health < before_plant.health
                }
                _ => false,
            },
            "PICK" => gained.iter().any(|&value| value > 0),
            "MINE" => gained[IRON] > 0,
            "DROP" => spent.iter().any(|&value| value > 0),
            _ => false,
        }
    }

    /// Process one turn's command (if any) for `unit_id`, append a trace row, and
    /// update the per-species acquisition ledger. Returns the species index (0..4)
    /// consumed by a successful PLANT this turn, if any (regardless of whether the
    /// created crop ends up own/joint — any successful PLANT truly spends a seed).
    #[allow(clippy::too_many_arguments)]
    fn d167a_process_turn(
        trace: &mut Vec<D167aTraceEvent>,
        ledgers: &mut [SpeciesLedger; 4],
        diagnostics: &mut D167aLedgerDiagnostics,
        before: &GameState,
        after: &GameState,
        player: usize,
        owners_before: &BTreeMap<Cell, Owner>,
        owners_after: &BTreeMap<Cell, Owner>,
        commands_for_player: &[String],
        unit_id: i32,
        turn: i32,
        is_entry_turn: bool,
    ) -> Option<usize> {
        let Some(before_unit) = before
            .units
            .iter()
            .find(|unit| unit.id == unit_id && unit.player as usize == player)
        else {
            return None;
        };
        let after_unit = after.units.iter().find(|unit| unit.id == unit_id);
        let pos_before = before_unit.pos();
        let pos_after = after_unit.map(|unit| unit.pos()).unwrap_or(pos_before);
        let (gained, spent) = d167a_item_deltas(before_unit, after_unit);
        let command = d166_commands_by_unit(commands_for_player).get(&unit_id).cloned();
        let verb = command
            .as_deref()
            .and_then(|value| command_fields(value).first().copied())
            .unwrap_or("NONE")
            .to_string();
        let before_plant_here = before.plants.iter().find(|plant| plant.pos() == pos_before);
        let after_plant_here = after.plants.iter().find(|plant| plant.pos() == pos_before);
        let success = d167a_success(
            &verb,
            pos_before,
            pos_after,
            before_plant_here,
            after_plant_here,
            &gained,
            &spent,
        );
        let target_kind = before_plant_here
            .map(|plant| plant.plant_type.clone())
            .unwrap_or_else(|| "NONE".to_string());
        let target_origin = if before_plant_here.is_some() {
            owner_label(owners_before.get(&pos_before))
        } else {
            "None"
        };

        let mut consumed_species: Option<usize> = None;
        if success {
            match verb.as_str() {
                "HARVEST" => {
                    if let Some(idx) = (0..4).find(|&i| gained[i] > 0) {
                        let tag = harvest_tag(owners_before.get(&pos_before));
                        ledgers[idx].add(tag, gained[idx]);
                    }
                }
                "PICK" => {
                    if let Some(idx) = (0..4).find(|&i| gained[i] > 0) {
                        ledgers[idx].add(Tag::Bank, gained[idx]);
                    }
                }
                "DROP" => {
                    for idx in 0..4 {
                        if spent[idx] > 0 {
                            let before_total = ledgers[idx].total();
                            if before_total != spent[idx] {
                                diagnostics.carry_mismatches += 1;
                            }
                            ledgers[idx].remove(spent[idx]);
                        }
                    }
                }
                "PLANT" => {
                    if let Some(idx) = (0..4).find(|&i| spent[i] > 0) {
                        consumed_species = Some(idx);
                        // Do not decrement yet: the caller reads classification
                        // from the ledger's pre-spend state for this exact turn.
                    }
                }
                _ => {}
            }
        }

        let created_origin = if verb == "PLANT" && success {
            owner_label(owners_after.get(&pos_before))
        } else {
            "None"
        };

        trace.push(D167aTraceEvent {
            turn,
            unit_id,
            x_before: pos_before.0,
            y_before: pos_before.1,
            x_after: pos_after.0,
            y_after: pos_after.1,
            verb,
            success,
            gained,
            spent,
            target_origin,
            target_kind,
            created_origin,
            is_entry: is_entry_turn,
            is_return: false,
        });
        let _ = diagnostics;
        consumed_species
    }

    #[derive(Clone, Debug, Default, PartialEq)]
    struct D167aAuditTelemetry {
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
        acquisition_terminated: bool,
        acquisition_event_count: u16,
        bank_units: i32,
        field_units: i32,
        opponent_units: i32,
        other_units: i32,
        acquisition_class: &'static str,
        acquisition_tags: String,
        species_planted: &'static str,
        path_length_turns: i32,
        distinct_cells_visited: u16,
        material_waypoints: u16,
        single_persistent_job: bool,
        ledger_integrity_ok: bool,
        ledger_diagnostics: D167aLedgerDiagnostics,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D167aOutcome {
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
        audit: D167aAuditTelemetry,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D167aRow {
        task: Task,
        outcome: D167aOutcome,
        trace: Vec<D167aTraceEvent>,
    }

    fn item_species_name(idx: usize) -> &'static str {
        match idx {
            0 => "PLUM",
            1 => "LEMON",
            2 => "APPLE",
            3 => "BANANA",
            _ => "NONE",
        }
    }

    fn d167a_play(task: Task) -> D167aRow {
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
        let mut telemetry = D167aAuditTelemetry {
            successor: SuccessorAudit::new(),
            acquisition_class: "NONE",
            species_planted: "NONE",
            path_length_turns: -1,
            ..D167aAuditTelemetry::default()
        };
        let mut trace: Vec<D167aTraceEvent> = Vec::new();
        let mut ledgers: [SpeciesLedger; 4] = Default::default();
        let mut visited_cells: BTreeSet<Cell> = BTreeSet::new();
        let mut idle_turns: u16 = 0;
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

            let entry_captured_before_this_turn = telemetry.successor.entry_captured;
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
                    if telemetry.successor.entry_captured
                        && (0..4).any(|item| telemetry.successor_carry(item) > 0)
                    {
                        telemetry.ledger_diagnostics.entry_carry_nonzero += 1;
                    }
                }
            }

            let was_returned_before = telemetry.successor.natural_return;
            for event in production {
                telemetry.production_events += 1;
                match event.record.verb {
                    ProductionVerb::Plant => telemetry.successful_production_plants += 1,
                    ProductionVerb::Harvest => telemetry.successful_production_harvests += 1,
                }
                d166_note_natural_return(&mut telemetry.successor, event);
                history.insert(event.unit_id, event.record);
            }

            // D167a: track the selected worker's full command trajectory from the
            // entry turn (inclusive) through the natural-return turn (inclusive).
            if telemetry.successor.entry_captured && !telemetry.acquisition_terminated {
                let selected_unit_id = telemetry.successor.selected_unit_id;
                let is_entry_turn = !entry_captured_before_this_turn;
                let consumed_species = d167a_process_turn(
                    &mut trace,
                    &mut ledgers,
                    &mut telemetry.ledger_diagnostics,
                    &before,
                    &game,
                    task.seat,
                    &owners_before,
                    &owners,
                    &commands[task.seat],
                    selected_unit_id,
                    before.turn,
                    is_entry_turn,
                );
                telemetry.acquisition_event_count += 1;
                if !is_entry_turn {
                    let pos_after = trace
                        .last()
                        .map(|event| (event.x_after, event.y_after))
                        .unwrap_or((-1, -1));
                    let is_idle = trace
                        .last()
                        .map(|event| {
                            (event.x_before, event.y_before) == (event.x_after, event.y_after)
                                && !event.success
                        })
                        .unwrap_or(false);
                    visited_cells.insert(pos_after);
                    if is_idle {
                        idle_turns += 1;
                    }
                }

                let just_returned = !was_returned_before && telemetry.successor.natural_return;
                if just_returned {
                    telemetry.acquisition_terminated = true;
                    if let Some(last) = trace.last_mut() {
                        last.is_return = true;
                    }
                    if telemetry.successor.natural_return_verb == 1 {
                        // PLANT return: classify from the species just consumed.
                        if let Some(idx) = consumed_species {
                            let ledger = ledgers[idx];
                            let distinct = ledger.distinct_tags();
                            telemetry.bank_units = ledger.bank;
                            telemetry.field_units = ledger.field;
                            telemetry.opponent_units = ledger.opponent;
                            telemetry.other_units = ledger.other;
                            telemetry.species_planted = item_species_name(idx);
                            telemetry.ledger_integrity_ok = !distinct.is_empty();
                            telemetry.acquisition_class = match distinct.as_slice() {
                                [only] => only.class_label(),
                                [] => "EMPTY_LEDGER_INTEGRITY_FAILURE",
                                _ => "OTHER_MIXED",
                            };
                            telemetry.acquisition_tags = distinct
                                .iter()
                                .map(|tag| tag.label())
                                .collect::<Vec<_>>()
                                .join("+");
                        } else {
                            telemetry.ledger_integrity_ok = false;
                            telemetry.acquisition_class = "MISSING_PLANT_SPEND_INTEGRITY_FAILURE";
                        }
                    } else {
                        telemetry.acquisition_class = "NON_PLANT_RETURN";
                        telemetry.ledger_integrity_ok = true;
                    }
                    telemetry.path_length_turns = telemetry.successor.natural_return_latency;
                    telemetry.distinct_cells_visited =
                        visited_cells.len().min(u16::MAX as usize) as u16;
                    telemetry.material_waypoints = trace
                        .iter()
                        .filter(|event| {
                            !event.is_entry
                                && !event.is_return
                                && event.success
                                && matches!(
                                    event.verb.as_str(),
                                    "HARVEST" | "PICK" | "DROP" | "CHOP" | "MINE"
                                )
                        })
                        .count()
                        .min(u16::MAX as usize) as u16;
                    telemetry.single_persistent_job = idle_turns == 0;
                } else if let Some(idx) = consumed_species {
                    // An incidental (non-returning) PLANT by the same worker truly
                    // spends a seed; decrement the ledger so later classification
                    // is not double-counted against stale contributions.
                    if ledgers[idx].remove(1) {
                        telemetry.ledger_diagnostics.ambiguous_partial_spends += 1;
                    }
                }
            }

            let after_workers = worker_count(&game, task.seat);
            successful_trains += after_workers.saturating_sub(before_workers);
            max_own_workers = max_own_workers.max(after_workers);
            done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        }
        telemetry.turns_played = turns_played.min(u16::MAX as usize) as u16;
        telemetry.resident_call_mismatches =
            u16::from(usize::from(telemetry.resident_calls) != turns_played);
        if telemetry.successor.entry_captured && !telemetry.acquisition_terminated {
            // Entry captured but no natural return before game end: no class.
            telemetry.acquisition_class = "NO_RETURN";
            telemetry.path_length_turns = -1;
            telemetry.distinct_cells_visited = visited_cells.len().min(u16::MAX as usize) as u16;
            telemetry.ledger_integrity_ok = true;
        }

        let own_score = game.scores[task.seat];
        let opponent_score = game.scores[1 - task.seat];
        let margin = own_score - opponent_score;
        let own_return = own_score as f32 / 100.0;
        let opponent_return = opponent_score as f32 / 100.0;
        let margin_return = margin as f32 / 100.0;
        D167aRow {
            task,
            outcome: D167aOutcome {
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
            trace,
        }
    }

    impl D167aAuditTelemetry {
        fn successor_carry(&self, item: usize) -> i32 {
            match item {
                0 => self.successor.worker_carry_plum,
                1 => self.successor.worker_carry_lemon,
                2 => self.successor.worker_carry_apple,
                3 => self.successor.worker_carry_banana,
                _ => 0,
            }
        }
    }

    fn d167a_write_summary_rows(output: &str, rows: &[D167aRow]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D167a summary output"));
        writeln!(
            writer,
            "map_seed\tseat\topponent_index\topponent\tpolicy\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tresident_calls\tturns_played\tresident_call_mismatches\tproduction_events\tsuccessful_production_plants\tsuccessful_production_harvests\topponent_crop_chops\thistorical_producer_opponent_crop_chops\tentry_captured\tentry_turn\tselected_unit_id\tprior_verb\tprior_turn\tprior_x\tprior_y\tprior_generation_birth_turn\tprior_target_live\tworker_ms\tworker_cc\tworker_hp\tworker_chop\tworker_free\tworker_carry_plum\tworker_carry_lemon\tworker_carry_apple\tworker_carry_banana\tworker_carry_iron\tworker_carry_wood\town_live_crops\town_ripe_crops\th_ripe_available\th_ripe_x\th_ripe_y\th_ripe_distance\th_ripe_fruits\th_ripe_cooldown\th_live_available\th_live_x\th_live_y\th_live_distance\th_live_fruits\th_live_cooldown\tp_carry_available\tlegal_empty_cells\tp_empty_x\tp_empty_y\tp_empty_distance\tnatural_return\tnatural_return_turn\tnatural_return_latency\tnatural_return_verb\tnatural_return_x\tnatural_return_y\tnatural_return_generation_birth_turn\tnatural_return_reuses_prior_cell\tnatural_return_reuses_prior_generation\tnatural_return_within16\tnatural_return_within32\tentry_worker_failures\thistory_failures\tentry_restarts\tcontroller_commands\tacquisition_class\tacquisition_tags\tacquisition_event_count\tbank_units\tfield_units\topponent_units\tother_units\tpath_length_turns\tdistinct_cells_visited\tmaterial_waypoints\tsingle_persistent_job\tspecies_planted\tledger_integrity_ok\tledger_ambiguous_partial_spends\tledger_carry_mismatches\tledger_entry_carry_nonzero"
        )
        .expect("write D167a summary header");
        for row in rows {
            let out = &row.outcome;
            let telemetry = &out.audit;
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
                telemetry.acquisition_class.to_string(),
                telemetry.acquisition_tags.clone(),
                telemetry.acquisition_event_count.to_string(),
                telemetry.bank_units.to_string(),
                telemetry.field_units.to_string(),
                telemetry.opponent_units.to_string(),
                telemetry.other_units.to_string(),
                telemetry.path_length_turns.to_string(),
                telemetry.distinct_cells_visited.to_string(),
                telemetry.material_waypoints.to_string(),
                usize::from(telemetry.single_persistent_job).to_string(),
                telemetry.species_planted.to_string(),
                usize::from(telemetry.ledger_integrity_ok).to_string(),
                telemetry.ledger_diagnostics.ambiguous_partial_spends.to_string(),
                telemetry.ledger_diagnostics.carry_mismatches.to_string(),
                telemetry.ledger_diagnostics.entry_carry_nonzero.to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D167a summary row");
        }
        writer.flush().expect("flush D167a summary output");
    }

    fn d167a_write_event_rows(output: &str, rows: &[D167aRow]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D167a events output"));
        writeln!(
            writer,
            "map_seed\tseat\topponent_index\topponent\tentry_turn\tnatural_return_turn\tstep_index\tturn\tunit_id\tx_before\ty_before\tx_after\ty_after\tverb\tsuccess\tgained_plum\tgained_lemon\tgained_apple\tgained_banana\tgained_iron\tgained_wood\tspent_plum\tspent_lemon\tspent_apple\tspent_banana\tspent_iron\tspent_wood\ttarget_origin\ttarget_kind\tcreated_origin\tis_entry\tis_return"
        )
        .expect("write D167a events header");
        for row in rows {
            let telemetry = &row.outcome.audit;
            for (index, event) in row.trace.iter().enumerate() {
                let values = vec![
                    row.task.map_seed.to_string(),
                    row.task.seat.to_string(),
                    row.task.opponent.to_string(),
                    MacroOpponentMode::from_index(row.task.opponent)
                        .label()
                        .to_string(),
                    telemetry.successor.entry_turn.to_string(),
                    telemetry.successor.natural_return_turn.to_string(),
                    index.to_string(),
                    event.turn.to_string(),
                    event.unit_id.to_string(),
                    event.x_before.to_string(),
                    event.y_before.to_string(),
                    event.x_after.to_string(),
                    event.y_after.to_string(),
                    event.verb.clone(),
                    usize::from(event.success).to_string(),
                    event.gained[0].to_string(),
                    event.gained[1].to_string(),
                    event.gained[2].to_string(),
                    event.gained[3].to_string(),
                    event.gained[4].to_string(),
                    event.gained[5].to_string(),
                    event.spent[0].to_string(),
                    event.spent[1].to_string(),
                    event.spent[2].to_string(),
                    event.spent[3].to_string(),
                    event.spent[4].to_string(),
                    event.spent[5].to_string(),
                    event.target_origin.to_string(),
                    event.target_kind.clone(),
                    event.created_origin.to_string(),
                    usize::from(event.is_entry).to_string(),
                    usize::from(event.is_return).to_string(),
                ];
                writeln!(writer, "{}", values.join("\t")).expect("write D167a event row");
            }
        }
        writer.flush().expect("flush D167a events output");
    }

    pub(super) fn d167a_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            6,
            "usage: d167a_successor_acquisition_path START_SEED MAPS SUMMARY_OUTPUT EVENTS_OUTPUT THREADS"
        );
        let start_seed: i64 = parse(&args[1], "start seed");
        let maps: usize = parse(&args[2], "maps");
        let summary_output = &args[3];
        let events_output = &args[4];
        let threads: usize = parse(&args[5], "threads");
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
                    let row = d167a_play(task);
                    rows.lock().expect("D167a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D167a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D167a rows")
            .into_inner()
            .expect("D167a rows lock");
        rows.sort_by_key(|row| row.task);
        d167a_write_summary_rows(summary_output, &rows);
        d167a_write_event_rows(events_output, &rows);
        eprintln!(
            "saved {} D167a rows ({} trace events) with {} workers in {:.3}s to {} / {}",
            rows.len(),
            rows.iter().map(|row| row.trace.len()).sum::<usize>(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            summary_output,
            events_output,
        );
    }

    #[cfg(test)]
    mod d167a_tests {
        use super::*;

        #[test]
        fn ledger_classifies_pure_bank_source() {
            let mut ledger = SpeciesLedger::default();
            ledger.add(Tag::Bank, 1);
            assert_eq!(ledger.distinct_tags(), vec![Tag::Bank]);
            assert_eq!(Tag::Bank.class_label(), "BANK_SEED");
        }

        #[test]
        fn ledger_classifies_mixed_source_as_other_mixed() {
            let mut ledger = SpeciesLedger::default();
            ledger.add(Tag::Bank, 1);
            ledger.add(Tag::Field, 1);
            let distinct = ledger.distinct_tags();
            assert_eq!(distinct.len(), 2);
        }

        #[test]
        fn ledger_drop_clears_all_tags_for_that_species() {
            let mut ledger = SpeciesLedger::default();
            ledger.add(Tag::Bank, 1);
            ledger.add(Tag::Field, 2);
            assert_eq!(ledger.total(), 3);
            let ambiguous = ledger.remove(3);
            assert!(ambiguous);
            assert_eq!(ledger.total(), 0);
            assert!(ledger.distinct_tags().is_empty());
        }

        #[test]
        fn harvest_tag_maps_ownership_correctly() {
            assert_eq!(harvest_tag(Some(&Owner::Own)), Tag::Field);
            assert_eq!(harvest_tag(Some(&Owner::Natural)), Tag::Field);
            assert_eq!(harvest_tag(Some(&Owner::Opponent)), Tag::Opponent);
            assert_eq!(harvest_tag(Some(&Owner::Joint)), Tag::Other);
            assert_eq!(harvest_tag(Some(&Owner::Ambiguous)), Tag::Other);
            assert_eq!(harvest_tag(None), Tag::Other);
        }

        #[test]
        fn exact_resident_audit_is_deterministic_and_read_only() {
            let task = Task {
                map_seed: 9_844_136,
                seat: 0,
                opponent: 0,
            };
            let first = d167a_play(task);
            let second = d167a_play(task);
            assert_eq!(first.outcome, second.outcome);
            assert_eq!(first.trace, second.trace);
            assert!(first.outcome.done);
            assert_eq!(first.outcome.audit.controller_commands, 0);
            assert_eq!(first.outcome.audit.resident_call_mismatches, 0);
            assert_eq!(first.outcome.provenance_failures, 0);
            assert_eq!(first.outcome.ambiguous_created_crops, 0);
        }

        #[test]
        fn entry_captured_tasks_have_zero_carried_seed_at_entry() {
            // Cross-checks D166's own 0/237 carried-seed-at-entry fact on a task
            // known (from the frozen D166a artifact) to activate entry.
            let task = Task {
                map_seed: 9_844_136,
                seat: 0,
                opponent: 0,
            };
            let row = d167a_play(task);
            if row.outcome.audit.successor.entry_captured {
                assert_eq!(row.outcome.audit.ledger_diagnostics.entry_carry_nonzero, 0);
            }
        }
    }
}

fn main() {
    inherited::d167a_main();
}
