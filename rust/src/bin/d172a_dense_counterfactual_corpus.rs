//! D172a: dense counterfactual-credit option policy — exact, zero-noise
//! per-decision counterfactual labels at every armable state under the
//! exact resident, a small linear/MLP function class fitted on them, and a
//! closed-loop, budget-1, tau-thresholded runtime. See
//! `data/analysis/live-agent-6553250/d172a-dense-counterfactual-option-policy-protocol-2026-07-28.md`
//! and `...-lock.json`.
//!
//! `mod inherited` below is composed from two frozen, hash-verified sources,
//! copied byte-for-byte (never edited) exactly as this codebase's own D169a/
//! D170a files each independently compose the same retained logic:
//!   1. `rust/src/bin/d169a_resident_option_envelope.rs` (lines 9-1284 as of
//!      its own frozen hash) — the D163 resource-controller component
//!      mechanism, the D166/D167/D168a return-option + entry-detection
//!      logic, the D169a `Component`/`StartSpec`/`ArmKind`/`arm_catalog`
//!      composition types, `D169aOutcome`/`D169aRow`, and `d169a_play`
//!      itself (the exact per-(task,arm) full-game counterfactual
//!      simulation — D172a's label source, unmodified).
//!   2. `rust/src/rl_d170a_option_policy_env.rs` (lines 802-923 as of its
//!      own frozen hash) — the `D170A_*` field-count constants,
//!      `decision_arm_index`, `opponent_units`, `owner_slot`,
//!      `owner_counts`, and `state_family` (the 64-field observable state
//!      family — D172a's feature source, unmodified).
//! Below the "D172a-specific" banner is new code (not a copy of any frozen
//! module): `affordance` is a de-methodized, otherwise byte-identical
//! adaptation of `D170aEnv::affordance` (same body; `&self` state threaded
//! through as explicit parameters instead of struct fields — cross-checked
//! in Phase 0 against the live `tf_d170a_*` FFI on sample tasks). Everything
//! else is a new composition layer: `scan_task` reproduces D169a's own
//! per-decision arming timing exactly (pre-step, same-iteration checks for
//! the workers==2 gate, the three fixed marks, and the trig arms' own
//! `opp_worker_trigger_turn == current_turn` equality; a genuine post-step
//! sticky `return_pending` flag for OPT_RETURN only, matching D169a's own
//! post-step activation check byte-for-byte -- Phase 0's byte-exact
//! cross-check against d169a_play caught and corrected an earlier draft
//! that copied D170b's own next-turn sticky-flag pattern for the trig arms
//! too, which is specific to that file's own architecture and is one turn
//! later than D169a's native timing) over a control-only (never-invoke)
//! trajectory, recording every candidate's full 81-field input at the
//! moment it is offered;
//! `label_task` (Phase 0/1) joins those candidates against `d169a_play`'s
//! own per-arm outcome for the exact counterfactual label, asserting 1:1
//! agreement between "offered" and `d169a_play`'s own `activated` telemetry
//! for all 13 arms on every task; `eval_task` (Phase 3/4) drives a fitted
//! linear/MLP model closed-loop (true argmax over each turn's simultaneously
//! -offered group, invoke iff > tau, budget-1), reusing `d169a_play` again
//! for the chosen arm's real outcome when a decision fires. Neither
//! `scan_task` nor `eval_task` ever edits the retained decision logic above
//! the banner; they only call it.
#[allow(dead_code)]
mod inherited {
    include!(concat!(
        env!("OUT_DIR"),
        "/d162_resident_native_capital_option.in.rs"
    ));

    // ══════════════════════════════════════════════════════════════════════
    // copied from d163_resident_resource_control_components.rs (the
    // FRUIT/IRON_ROUTE/PROTECTION component mechanism only — its own
    // catalog/play/write/main/tests are not reused; D169a builds its own
    // catalog and orchestrates when each component's `ResourceConfig.start`
    // is chosen). Reproduces D163's frozen resource-control component
    // decision logic byte-for-byte. Do not edit the retained logic.
    // ══════════════════════════════════════════════════════════════════════

    const D163_HORIZON: i32 = 32;
    const FRUIT: u8 = 1;
    const IRON_ROUTE: u8 = 2;
    const PROTECTION: u8 = 4;

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    struct ResourceConfig {
        mask: u8,
        start: i32,
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
                .min(u16::MAX as usize) as u16;
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

    // ══════════════════════════════════════════════════════════════════════
    // copied (trimmed to the ARM_A "post-return" subset only — ARM_B
    // "pre-carry" is out of scope for D169a's OPT_RETURN) from
    // d168a_bank_seed_successor_option.rs, which itself copied its
    // production-history/entry-detection bookkeeping byte-for-byte from
    // d166_producer_job_successor_affordance.rs via
    // d167a_successor_acquisition_path.rs. Reproduces D166/D167/D168a's
    // frozen entry-detection and D168a's ARM_A decision logic exactly
    // (types renamed with a D168a prefix only where the bare name would
    // collide with this file's own top-level catalog types; the ArmB-only
    // branches — Phase::ReturnToChop, ChopJobInvalidated, chop telemetry,
    // the `policy` dispatch parameter — are omitted because D169a's
    // OPT_RETURN reuses ARM_A only, per protocol: "the D168 ARM_A BANK_SEED
    // successor return, byte-identical semantics ... aborts: empty bank, no
    // legal cell, horizon" names exactly ARM_A's abort set). Do not edit the
    // retained logic.
    // ══════════════════════════════════════════════════════════════════════

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

    /// Same entry predicate as D166/D167/D168a: the first turn (ascending
    /// unit_id among ties) a historical producer issues CHOP against a live
    /// Opponent-owned plant it currently stands on. Returns (unit_id, cell).
    /// Pure / read-only.
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

    const OPT_RETURN_HORIZON: i32 = 24;

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum D168aAbortReason {
        None,
        EmptyBankAtPick,
        NoLegalCell,
        Horizon,
        WorkerMissing,
    }

    impl D168aAbortReason {
        fn label(self) -> &'static str {
            match self {
                Self::None => "NONE",
                Self::EmptyBankAtPick => "EMPTY_BANK_AT_PICK",
                Self::NoLegalCell => "NO_LEGAL_CELL",
                Self::Horizon => "HORIZON",
                Self::WorkerMissing => "WORKER_MISSING",
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum D168aPhase {
        AcquireSeed,
        SeekPlantCell,
    }

    fn phase_for(unit: &Unit) -> D168aPhase {
        if unit.total() == 0 {
            D168aPhase::AcquireSeed
        } else {
            D168aPhase::SeekPlantCell
        }
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D168aOptionTelemetry {
        gate_bank_ok: bool,
        activated: bool,
        activation_turn: i32,
        deadline: i32,
        committed: bool,
        committed_turn: i32,
        aborted: bool,
        abort_reason: D168aAbortReason,
        species_picked: i32,
        species_planted: i32,
        plant_cell_x: i32,
        plant_cell_y: i32,
        move_commands: u16,
        pick_commands: u16,
        plant_commands: u16,
        hold_commands: u16,
        pick_attempts: u16,
        pick_successes: u16,
        plant_attempts: u16,
        plant_successes: u16,
        vocabulary_violations: u16,
        active_turns: u16,
    }

    impl D168aOptionTelemetry {
        fn new() -> Self {
            Self {
                gate_bank_ok: false,
                activated: false,
                activation_turn: -1,
                deadline: -1,
                committed: false,
                committed_turn: -1,
                aborted: false,
                abort_reason: D168aAbortReason::None,
                species_picked: -1,
                species_planted: -1,
                plant_cell_x: -1,
                plant_cell_y: -1,
                move_commands: 0,
                pick_commands: 0,
                plant_commands: 0,
                hold_commands: 0,
                pick_attempts: 0,
                pick_successes: 0,
                plant_attempts: 0,
                plant_successes: 0,
                vocabulary_violations: 0,
                active_turns: 0,
            }
        }

        fn active(&self) -> bool {
            self.activated && !self.committed && !self.aborted
        }
    }

    fn is_allowed_verb(verb: &str) -> bool {
        matches!(verb, "MOVE" | "PICK" | "PLANT")
    }

    /// Compute this turn's armed-worker override, or None for a deliberate
    /// hold. May instead set `telemetry.aborted`; callers must not apply any
    /// command (including hold) when that fires this same call.
    fn armed_command(
        game: &GameState,
        player: usize,
        unit: &Unit,
        telemetry: &mut D168aOptionTelemetry,
    ) -> Option<String> {
        if game.turn >= telemetry.deadline {
            telemetry.aborted = true;
            telemetry.abort_reason = D168aAbortReason::Horizon;
            return None;
        }
        match phase_for(unit) {
            D168aPhase::AcquireSeed => {
                if !near_shack(game, player, unit) {
                    telemetry.move_commands += 1;
                    let shack = game.shacks[player];
                    Some(format!("MOVE {} {} {}", unit.id, shack.0, shack.1))
                } else {
                    match choose_species(&game.inventories[player]) {
                        None => {
                            telemetry.aborted = true;
                            telemetry.abort_reason = D168aAbortReason::EmptyBankAtPick;
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
            D168aPhase::SeekPlantCell => match nearest_empty_cell(game, unit.pos()) {
                None => {
                    telemetry.aborted = true;
                    telemetry.abort_reason = D168aAbortReason::NoLegalCell;
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
    enum D168aIssuedVerb {
        None,
        Move,
        Pick(usize),
        Plant(usize),
    }

    // ══════════════════════════════════════════════════════════════════════
    // D169a-specific: unified 14-policy catalog, per-task play loop, and
    // TSV output. New code (not a copy of any frozen module) — this is the
    // composition layer that decides *when* each reused mechanism runs and
    // resolves the TRIG start dynamically; it never edits the retained
    // decision logic above.
    // ══════════════════════════════════════════════════════════════════════

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum Component {
        Fruit,
        Iron,
        Protect,
    }

    impl Component {
        const ALL: [Self; 3] = [Self::Fruit, Self::Iron, Self::Protect];

        fn label(self) -> &'static str {
            match self {
                Self::Fruit => "fruit",
                Self::Iron => "iron",
                Self::Protect => "protect",
            }
        }

        fn mask(self) -> u8 {
            match self {
                Self::Fruit => FRUIT,
                Self::Iron => IRON_ROUTE,
                Self::Protect => PROTECTION,
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum StartSpec {
        Fixed(i32),
        Trig,
    }

    impl StartSpec {
        fn label(self) -> String {
            match self {
                Self::Fixed(turn) => format!("t{turn:03}"),
                Self::Trig => "trig".to_string(),
            }
        }
    }

    #[derive(Clone, Copy, Debug, Eq, PartialEq)]
    enum ArmKind {
        Control,
        Return,
        Resource(Component, StartSpec),
    }

    impl ArmKind {
        fn label(self) -> String {
            match self {
                Self::Control => "control".to_string(),
                Self::Return => "opt_return".to_string(),
                Self::Resource(component, start) => {
                    format!("opt_{}_{}", component.label(), start.label())
                }
            }
        }

        fn arm_family(self) -> &'static str {
            match self {
                Self::Control => "control",
                Self::Return => "return",
                Self::Resource(..) => "resource",
            }
        }

        fn component_label(self) -> &'static str {
            match self {
                Self::Resource(component, _) => component.label(),
                _ => "none",
            }
        }

        fn start_kind_label(self) -> &'static str {
            match self {
                Self::Resource(_, StartSpec::Fixed(_)) => "fixed",
                Self::Resource(_, StartSpec::Trig) => "trig",
                _ => "none",
            }
        }

        fn fixed_start(self) -> i32 {
            match self {
                Self::Resource(_, StartSpec::Fixed(turn)) => turn,
                _ => -1,
            }
        }
    }

    fn arm_catalog() -> Vec<ArmKind> {
        let mut arms = vec![ArmKind::Control, ArmKind::Return];
        for component in Component::ALL {
            for mark in MARKS {
                arms.push(ArmKind::Resource(component, StartSpec::Fixed(mark)));
            }
            arms.push(ArmKind::Resource(component, StartSpec::Trig));
        }
        arms
    }

    #[derive(Clone, Copy, Debug, PartialEq)]
    struct D169aOutcome {
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
        entry_captured: bool,
        entry_turn: i32,
        entry_unit_id: i32,
        generic_return_captured: bool,
        generic_return_turn: i32,
        generic_return_verb: i8,
        opp_worker_trigger_turn: i32,
        purity_violations: u16,
        invalid_direct_commands: u16,
        activated: bool,
        activation_turn: i32,
        deadline: i32,
        committed: bool,
        committed_turn: i32,
        aborted: bool,
        abort_reason: &'static str,
        active_turns: u16,
        configured_start: i32,
        resource_mask: u8,
        return_option: D168aOptionTelemetry,
        resource: ResourceTelemetry,
    }

    #[derive(Clone, Debug, PartialEq)]
    struct D169aRow {
        task: Task,
        arm_index: usize,
        arm: ArmKind,
        outcome: D169aOutcome,
    }

    fn d169a_play(task: Task, arm_index: usize, arm: ArmKind) -> D169aRow {
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
        let mut opp_worker_trigger_turn: i32 = -1;

        let mut return_telemetry = D168aOptionTelemetry::new();

        let mask = match arm {
            ArmKind::Resource(component, _) => component.mask(),
            _ => 0,
        };
        let mut resource_controller = ResourceController::new(match arm {
            ArmKind::Resource(_, StartSpec::Fixed(start)) => Some(ResourceConfig { mask, start }),
            _ => None,
        });
        let mut configured_start: i32 = arm.fixed_start();

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

            // ── diagnostic: first turn observed opponent worker count
            // reaches >= 3 (the B3.1 early-warning trigger); computed for
            // every task and every arm identically, independent of whether
            // this row's own arm uses it. ──
            if opp_worker_trigger_turn < 0 && worker_count(&game, 1 - task.seat) >= 3 {
                opp_worker_trigger_turn = current_turn;
            }

            // ── entry-candidate detection: identical for every arm,
            // pre-step, reused unchanged from D166/D167/D168a. ──
            if !entry_captured {
                if let Some((unit_id, _cell)) =
                    d168a_entry_candidate(&game, task.seat, &owners, &history, &resident_commands)
                {
                    entry_captured = true;
                    entry_turn = current_turn;
                    entry_unit_id = unit_id;
                }
            }

            // ── resource-controller path (OPT_FRUIT/OPT_IRON/OPT_PROTECT
            // only). The TRIG variant supplies D163's own unmodified
            // `ResourceConfig.start` dynamically, at the exact turn the
            // observable trigger first fires, so the reused `rewrite()`
            // activation check (`game.turn == config.start`) behaves
            // exactly as it would for a fixed mark discovered in advance. ──
            if let ArmKind::Resource(_, StartSpec::Trig) = arm {
                if resource_controller.config.is_none() && opp_worker_trigger_turn == current_turn {
                    resource_controller.config = Some(ResourceConfig { mask, start: current_turn });
                    configured_start = current_turn;
                }
            }
            if matches!(arm, ArmKind::Resource(..)) {
                seat_commands = resource_controller.rewrite(&game, task.seat, seat_commands);
            }
            let resource_live_this_turn = resource_controller.active();

            // ── return-option path (OPT_RETURN only; D168a ARM_A verbatim) ──
            let return_live_this_turn = arm == ArmKind::Return && return_telemetry.active();
            let mut issued = D168aIssuedVerb::None;
            let mut armed_pos_before: Option<Cell> = None;
            if return_live_this_turn {
                let armed_unit = game
                    .units
                    .iter()
                    .find(|unit| unit.id == entry_unit_id && unit.player as usize == task.seat)
                    .cloned();
                match armed_unit {
                    None => {
                        return_telemetry.aborted = true;
                        return_telemetry.abort_reason = D168aAbortReason::WorkerMissing;
                    }
                    Some(unit) => {
                        armed_pos_before = Some(unit.pos());
                        match armed_command(&game, task.seat, &unit, &mut return_telemetry) {
                            Some(command) => {
                                let verb = command_fields(&command).first().copied().unwrap_or("");
                                if !is_allowed_verb(verb) {
                                    return_telemetry.vocabulary_violations += 1;
                                } else {
                                    issued = match verb {
                                        "MOVE" => D168aIssuedVerb::Move,
                                        "PICK" => D168aIssuedVerb::Pick(
                                            command_item(&command).unwrap_or(usize::MAX),
                                        ),
                                        "PLANT" => D168aIssuedVerb::Plant(
                                            command_item(&command).unwrap_or(usize::MAX),
                                        ),
                                        _ => D168aIssuedVerb::None,
                                    };
                                    replace_unit_command(&mut seat_commands, entry_unit_id, command);
                                    return_telemetry.active_turns += 1;
                                }
                            }
                            None => {
                                if !return_telemetry.aborted {
                                    remove_unit_command(&mut seat_commands, entry_unit_id);
                                    return_telemetry.hold_commands += 1;
                                    return_telemetry.active_turns += 1;
                                }
                            }
                        }
                    }
                }
            }

            // ── controller-command purity: generalizes D168a's own "every
            // unit other than the armed one carries the resident's own
            // command" check to also permit D163's own frozen
            // protection-suppression mechanism (a pure removal, never a
            // substitution, of a *different* unit's command). At most one
            // unit total may *deviate* per turn — its command replaced,
            // newly issued (resident left it silent), or removed (a
            // deliberate hold) — and only while that arm is live this turn;
            // any *number* of pure removals (never a replacement or a new
            // command) is legal for the protection-capable resource arm. ──
            {
                let resident_map: BTreeMap<i32, &str> = resident_commands
                    .iter()
                    .filter_map(|command| command_unit(command).map(|id| (id, command.as_str())))
                    .collect();
                let seat_map: BTreeMap<i32, &str> = seat_commands
                    .iter()
                    .filter_map(|command| command_unit(command).map(|id| (id, command.as_str())))
                    .collect();
                let all_ids: BTreeSet<i32> =
                    resident_map.keys().chain(seat_map.keys()).copied().collect();
                let mut changed_or_added = 0usize;
                let mut removed = 0usize;
                for id in all_ids {
                    match (resident_map.get(&id), seat_map.get(&id)) {
                        (Some(resident_command), Some(seat_command))
                            if resident_command != seat_command =>
                        {
                            changed_or_added += 1;
                        }
                        (Some(_), None) => removed += 1,
                        (None, Some(_)) => changed_or_added += 1,
                        _ => {}
                    }
                }
                let acquisition_capable = return_live_this_turn
                    || matches!(arm, ArmKind::Resource(Component::Fruit | Component::Iron, _));
                let protection_capable =
                    matches!(arm, ArmKind::Resource(Component::Protect, _)) && resource_live_this_turn;
                let arm_live = return_live_this_turn || resource_live_this_turn;
                let violation = if protection_capable {
                    changed_or_added > 0
                } else if arm_live && acquisition_capable {
                    changed_or_added + removed > 1
                } else {
                    changed_or_added + removed > 0
                };
                if violation {
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

            // ── OPT_RETURN activation: post-step ("P→S transition
            // completion"), byte-identical to D168a's ARM_A. ──
            if arm == ArmKind::Return
                && entry_captured
                && entry_turn == current_turn
                && !return_telemetry.activated
            {
                return_telemetry.gate_bank_ok = bank_fruit_total(&game, task.seat) > 0;
                if return_telemetry.gate_bank_ok {
                    return_telemetry.activated = true;
                    return_telemetry.activation_turn = entry_turn;
                    return_telemetry.deadline = entry_turn + OPT_RETURN_HORIZON;
                }
            }

            // ── transaction verification for this turn's issued override ──
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
                    D168aIssuedVerb::Pick(item) if item < 4 => {
                        if after_carry_of(item) > before_carry_of(item) {
                            return_telemetry.pick_successes += 1;
                            return_telemetry.species_picked = item as i32;
                        }
                    }
                    D168aIssuedVerb::Plant(item) if item < 4 => {
                        let planted_now = !before_plants.contains(&pos_before)
                            && owners.get(&pos_before) == Some(&Owner::Own)
                            && game.plants.iter().any(|plant| plant.pos() == pos_before);
                        if after_carry_of(item) < before_carry_of(item) && planted_now {
                            return_telemetry.plant_successes += 1;
                            return_telemetry.committed = true;
                            return_telemetry.committed_turn = before.turn;
                            return_telemetry.species_planted = item as i32;
                            return_telemetry.plant_cell_x = pos_before.0;
                            return_telemetry.plant_cell_y = pos_before.1;
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

        let (activated, activation_turn, deadline, committed, committed_turn, aborted, abort_reason, active_turns) =
            match arm {
                ArmKind::Control => (false, -1, -1, false, -1, false, "NONE", 0u16),
                ArmKind::Return => (
                    return_telemetry.activated,
                    return_telemetry.activation_turn,
                    return_telemetry.deadline,
                    return_telemetry.committed,
                    return_telemetry.committed_turn,
                    return_telemetry.aborted,
                    return_telemetry.abort_reason.label(),
                    return_telemetry.active_turns,
                ),
                ArmKind::Resource(..) => {
                    let reason = if resource_controller.telemetry.workforce_exit_events > 0 {
                        "WORKFORCE_EXIT"
                    } else if resource_controller.telemetry.aborted {
                        "HORIZON"
                    } else {
                        "NONE"
                    };
                    (
                        resource_controller.telemetry.activated,
                        resource_controller.telemetry.activation_turn,
                        resource_controller.telemetry.deadline,
                        false,
                        -1,
                        resource_controller.telemetry.aborted,
                        reason,
                        resource_controller.telemetry.active_turns,
                    )
                }
            };
        let invalid_direct_commands = match arm {
            ArmKind::Return => return_telemetry.vocabulary_violations,
            ArmKind::Resource(..) => resource_controller.telemetry.option_command_failures,
            ArmKind::Control => 0,
        };

        D169aRow {
            task,
            arm_index,
            arm,
            outcome: D169aOutcome {
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
                entry_captured,
                entry_turn,
                entry_unit_id,
                generic_return_captured,
                generic_return_turn,
                generic_return_verb,
                opp_worker_trigger_turn,
                purity_violations: purity_violations.min(u16::MAX as usize) as u16,
                invalid_direct_commands,
                activated,
                activation_turn,
                deadline,
                committed,
                committed_turn,
                aborted,
                abort_reason,
                active_turns,
                configured_start,
                resource_mask: mask,
                return_option: return_telemetry,
                resource: resource_controller.telemetry,
            },
        }
    }
    pub(super) const D170A_STATE_FEATURES: usize = 64;
    /// Decision block appended after the state family: 0 turn/300;
    /// 1 observed_opponent_worker_count/6; 2..15 armable-option one-hot (13
    /// dims, arm_catalog()[1..14] order); 15 affordance_primary;
    /// 16 affordance_secondary. Only populated while a decision is pending
    /// (all-zero otherwise).
    pub(super) const D170A_DECISION_FEATURES: usize = 17;
    pub(super) const D170A_INPUT_FEATURES: usize = D170A_STATE_FEATURES + D170A_DECISION_FEATURES;
    /// KEEP = 0, INVOKE = 1.
    pub(super) const D170A_ACTIONS: usize = 2;
    /// arm_catalog().len() - 1 (excludes Control, which is never a choice).
    pub(super) const D170A_ARMS: usize = 13;

    fn decision_arm_index(arm: ArmKind) -> usize {
        arm_catalog()
            .iter()
            .position(|candidate| *candidate == arm)
            .expect("D170a known arm")
            - 1
    }

    fn opponent_units<'a>(game: &'a GameState, player: usize) -> Vec<&'a Unit> {
        game.units
            .iter()
            .filter(|unit| unit.player as usize != player)
            .collect()
    }

    fn owner_slot(owner: Owner) -> usize {
        match owner {
            Owner::Natural => 0,
            Owner::Own => 1,
            Owner::Opponent => 2,
            Owner::Joint => 3,
            Owner::Ambiguous => 4,
        }
    }

    fn owner_counts(game: &GameState, owners: &BTreeMap<Cell, Owner>) -> ([f32; 5], [f32; 5]) {
        let mut plants = [0f32; 5];
        let mut fruits = [0f32; 5];
        for plant in game.plants.iter().filter(|plant| plant.health > 0) {
            let owner = owners.get(&plant.pos()).copied().unwrap_or(Owner::Natural);
            let slot = owner_slot(owner);
            plants[slot] += 1.0;
            fruits[slot] += plant.fruits as f32;
        }
        (plants, fruits)
    }

    /// The 64-field observable state family; see `D170A_STATE_FEATURES` doc
    /// for the exact field list. `opponent identity is never an input` —
    /// every field is a symmetric function of the observable game state.
    #[allow(clippy::too_many_arguments)]
    fn state_family(
        game: &GameState,
        player: usize,
        owners: &BTreeMap<Cell, Owner>,
        max_own_workers_so_far: usize,
        own_created_crops_so_far: usize,
        opponent_created_crops_so_far: usize,
        own_reinvested_crops_so_far: usize,
        provenance_failures_so_far: usize,
        opp_worker_trigger_turn: i32,
        entry_captured: bool,
        decisions_seen_so_far: usize,
        budget_remaining: bool,
    ) -> [f32; D170A_STATE_FEATURES] {
        let opponent = 1 - player;
        let own = own_units(game, player);
        let opp = opponent_units(game, player);
        let (plant_counts, fruit_counts) = owner_counts(game, owners);
        let mut f = [0f32; D170A_STATE_FEATURES];
        f[0] = 1.0;
        f[1] = game.turn as f32 / MACRO_TOTAL_TURNS as f32;
        f[2] = own.len() as f32 / 3.0;
        f[3] = opp.len() as f32 / 3.0;
        f[4] = game.scores[player] as f32 / 400.0;
        f[5] = game.scores[opponent] as f32 / 400.0;
        f[6] = (game.scores[player] - game.scores[opponent]) as f32 / 400.0;
        for item in 0..6 {
            f[7 + item] = game.inventories[player][item] as f32 / 20.0;
            f[13 + item] = game.inventories[opponent][item] as f32 / 20.0;
            f[19 + item] = own.iter().map(|unit| unit.carry[item]).sum::<i32>() as f32 / 20.0;
            f[25 + item] = opp.iter().map(|unit| unit.carry[item]).sum::<i32>() as f32 / 20.0;
        }
        for slot in 0..5 {
            f[31 + slot] = plant_counts[slot] / 20.0;
            f[36 + slot] = fruit_counts[slot] / 40.0;
        }
        f[41] = f32::from(plant_counts[owner_slot(Owner::Own)] > 0.0);
        f[42] = f32::from(plant_counts[owner_slot(Owner::Opponent)] > 0.0);
        let total_cells = (game.width * game.height).max(1) as f32;
        f[43] = game.water.len() as f32 / total_cells;
        f[44] = game.walkable.len() as f32 / total_cells;
        f[45] = own.iter().map(|unit| unit.hp).sum::<i32>() as f32 / 12.0;
        f[46] = own.iter().map(|unit| unit.chop).sum::<i32>() as f32 / 12.0;
        f[47] = own.iter().map(|unit| unit.ms).sum::<i32>() as f32 / 9.0;
        f[48] = own.iter().map(|unit| unit.cc).sum::<i32>() as f32 / 12.0;
        f[49] = (MACRO_TOTAL_TURNS - game.turn).max(0) as f32 / MACRO_TOTAL_TURNS as f32;
        f[50] = max_own_workers_so_far as f32 / 3.0;
        f[51] = own_created_crops_so_far as f32 / 20.0;
        f[52] = opponent_created_crops_so_far as f32 / 20.0;
        f[53] = own_reinvested_crops_so_far as f32 / 20.0;
        f[54] = provenance_failures_so_far as f32 / 10.0;
        f[55] = f32::from(opp_worker_trigger_turn >= 0);
        f[56] = if opp_worker_trigger_turn >= 0 {
            opp_worker_trigger_turn as f32 / MACRO_TOTAL_TURNS as f32
        } else {
            0.0
        };
        f[57] = f32::from(entry_captured);
        f[58] = bank_fruit_total(game, player) as f32 / 20.0;
        let deficit = bank_deficit(game, player, &shadow_reserve(game));
        f[59] = (deficit as f32 / 20.0).clamp(-1.0, 1.0);
        f[60] = own.iter().map(|unit| unit.free()).sum::<i32>() as f32 / 12.0;
        f[61] = opp.iter().map(|unit| unit.free()).sum::<i32>() as f32 / 12.0;
        f[62] = decisions_seen_so_far as f32 / 10.0;
        f[63] = f32::from(budget_remaining);
        assert!(f.iter().all(|value| value.is_finite()));
        f
    }

    // ══════════════════════════════════════════════════════════════════════
    // D172a-specific: dense counterfactual-credit corpus generator + policy
    // runtime. New code (not a copy of any frozen module) — composes the
    // retained decision logic above (copied byte-for-byte from D169a) and
    // the D170 feature builder (copied byte-for-byte from
    // rl_d170a_option_policy_env.rs) exactly as D169a's own `d169a_play` and
    // D170a's own `D170aEnv` each independently compose the same retained
    // logic. Never edits the retained logic above this banner.
    // ══════════════════════════════════════════════════════════════════════

    /// De-methodized, otherwise byte-identical adaptation of
    /// `D170aEnv::affordance` (rust/src/rl_d170a_option_policy_env.rs,
    /// lines 1217-1246 as of its own frozen hash) — identical match arms and
    /// arithmetic; `&self` state (`self.game`, `self.task.seat`,
    /// `self.entry_unit_id`) threaded through as explicit parameters
    /// instead of struct fields, since D172a has no persistent env struct.
    /// Cross-validated in Phase 0 against direct output from that file's
    /// own `tf_d170a_*` FFI on sample tasks.
    fn affordance(game: &GameState, player: usize, entry_unit_id: i32, arm: ArmKind) -> (f32, f32) {
        match arm {
            ArmKind::Return => {
                let primary = bank_fruit_total(game, player) as f32 / 20.0;
                let near = game
                    .units
                    .iter()
                    .find(|unit| unit.id == entry_unit_id && unit.player as usize == player)
                    .is_some_and(|unit| near_shack(game, player, unit));
                (primary, f32::from(near))
            }
            ArmKind::Resource(component, _) => {
                let target = shadow_reserve(game);
                let deficit = bank_deficit(game, player, &target);
                let primary = (deficit as f32 / 20.0).clamp(-1.0, 1.0);
                let config = ResourceConfig {
                    mask: component.mask(),
                    start: game.turn,
                };
                let carried =
                    ResourceController::carried_resource_worker(game, player, &target, config)
                        .is_some();
                (primary, f32::from(carried))
            }
            ArmKind::Control => (0.0, 0.0),
        }
    }

    /// One armable candidate discovered by the control-trajectory scan: the
    /// arm, the turn it becomes armable, and its full 81-field input vector
    /// (64-field state family + 17-field decision block), byte-identical in
    /// construction to D170a's own `observe_input`.
    #[derive(Clone, Copy, Debug)]
    pub(super) struct D172aCandidate {
        pub(super) arm: ArmKind,
        pub(super) turn: i32,
        pub(super) input: [f32; D170A_INPUT_FEATURES],
    }

    /// Outcome of the control-only (never-invoke) scan of one task: every
    /// candidate ever offered, in chronological (turn, then component/mark
    /// arrival) order, plus the resulting control score pair.
    pub(super) struct D172aScan {
        pub(super) candidates: Vec<D172aCandidate>,
        pub(super) control_own_score: i32,
        pub(super) control_opponent_score: i32,
    }

    /// Walks the exact resident's own trajectory once — no option ever
    /// engages, so this is control-identical by construction (the same
    /// property D170a's own all-KEEP walk relies on, proven byte-exact vs
    /// control by its `all_keep_is_byte_exact_vs_control` test) —
    /// reproducing D169a's own per-decision arming timing exactly: the
    /// workers==2 gate, the three fixed marks, the trig arms' pre-step
    /// same-turn `opp_worker_trigger_turn == current_turn` equality, and a
    /// genuine post-step sticky `return_pending` flag for OPT_RETURN only
    /// (byte-identical to D169a's own post-step activation check — NOT the
    /// D170b Delta-1 next-turn pattern, which is specific to that file's
    /// own strictly-sequential offer-one-at-a-time architecture and is one
    /// turn later than D169a's native trig timing; see the file-level doc
    /// comment). Records every candidate's full input vector at the moment
    /// it is offered — state as
    /// of the START of that turn, before any option ever runs — using
    /// `state_family` + `affordance` (both from the D170 feature builder
    /// above, never re-derived by hand).
    fn scan_task(task: Task) -> D172aScan {
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
        let mut opp_worker_trigger_turn: i32 = -1;
        let mut return_pending = false;
        let mut last_scanned_turn = i32::MIN;

        let mut max_own_workers = worker_count(&game, task.seat);
        let mut own_created_crops = 0usize;
        let mut opponent_created_crops = 0usize;
        let mut own_reinvested_crops = 0usize;
        let mut own_owned_crop_harvest_units = 0usize;
        let mut provenance_failures = 0usize;
        let mut decisions_seen = 0usize;
        let mut turns_until_end = 0i32;
        let mut done = false;

        let mut candidates = Vec::new();

        while !done {
            let current_turn = game.turn;

            // ── exact-resident-only turn body: no option ever engages.
            // Pre-step bookkeeping ordered exactly as D169a's own
            // `d169a_play` (opp_worker_trigger_turn update, then entry-
            // detection, both using this turn's about-to-be-issued
            // `resident_commands`) -- both can newly become true in THIS
            // exact iteration, before any candidate is offered this turn,
            // matching D169a's own trig-arm activation check
            // (`opp_worker_trigger_turn == current_turn`, evaluated the
            // SAME iteration it is set: d169a_resident_option_envelope.rs
            // lines 903-904 then 925-926) byte-for-byte. ──
            let resident_commands = ours.commands(&resident_view(&game, task.seat));
            let theirs_commands = theirs.commands(&game, 1 - task.seat);
            let seat_commands = resident_commands.clone();

            if opp_worker_trigger_turn < 0 && worker_count(&game, 1 - task.seat) >= 3 {
                opp_worker_trigger_turn = current_turn;
            }
            if !entry_captured {
                if let Some((unit_id, _cell)) =
                    d168a_entry_candidate(&game, task.seat, &owners, &history, &resident_commands)
                {
                    entry_captured = true;
                    entry_turn = current_turn;
                    entry_unit_id = unit_id;
                }
            }

            // ── candidate scan for this turn (idempotent per turn). Fixed
            // marks and the trig gate are checked exactly as D169a's own
            // `ResourceController::rewrite`/trig-config-assignment
            // (workers==2 gate; `opp_worker_trigger_turn == current_turn`
            // direct equality, same-turn, NOT a next-turn sticky flag --
            // unlike D170a/b's OPT_RETURN, D169a's own trig arm has no
            // post-step latch to reproduce; its activation check runs
            // pre-step, same iteration it is set. Phase 0's byte-exact
            // cross-check against d169a_play's own `activated`/
            // `activation_turn` caught the D170b-Delta-1-pattern version of
            // this (offering trig one turn late) as a real mismatch --
            // fixed here, see the phase-0 result doc). OPT_RETURN keeps its
            // genuine post-step sticky `return_pending` flag (D169a's own
            // Return activation is itself a post-step check at
            // `entry_turn`, so the earliest a real decision can be offered
            // is the following turn -- confirmed by the `!matches!(arm,
            // ArmKind::Return)` carve-out in `label_task`'s turn-equality
            // assertion below). ──
            if last_scanned_turn != current_turn {
                last_scanned_turn = current_turn;
                let mut this_turn: Vec<ArmKind> = Vec::new();
                if return_pending {
                    this_turn.push(ArmKind::Return);
                    return_pending = false;
                }
                let workers = worker_count(&game, task.seat);
                if workers == 2 {
                    let trig_ready = opp_worker_trigger_turn == current_turn;
                    for component in Component::ALL {
                        for mark in MARKS {
                            if current_turn == mark {
                                this_turn.push(ArmKind::Resource(component, StartSpec::Fixed(mark)));
                            }
                        }
                        if trig_ready {
                            this_turn.push(ArmKind::Resource(component, StartSpec::Trig));
                        }
                    }
                }
                if !this_turn.is_empty() {
                    // D170a's own env calls observe_input() once per
                    // candidate, sequentially, with decisions_seen
                    // incremented (inside decide()) BETWEEN successive
                    // same-turn candidates -- so within one simultaneous
                    // group, candidate i (0-indexed in arrival order) sees
                    // decisions_seen_so_far = baseline + i, not a single
                    // shared snapshot. Recomputing state_family fresh per
                    // candidate reproduces that exactly (caught by the
                    // Phase-0-extended cross-check against the live
                    // tf_d170a_* FFI, which an earlier draft that computed
                    // `state` once per group failed on every multi-
                    // candidate turn).
                    let opp_workers = worker_count(&game, 1 - task.seat);
                    for arm in this_turn {
                        let state = state_family(
                            &game,
                            task.seat,
                            &owners,
                            max_own_workers,
                            own_created_crops,
                            opponent_created_crops,
                            own_reinvested_crops,
                            provenance_failures,
                            opp_worker_trigger_turn,
                            entry_captured,
                            decisions_seen,
                            true, // budget_remaining: every offered candidate in the real
                                  // sequential env is, by construction, only ever offered
                                  // while budget is unspent (offers stop the instant
                                  // budget_used flips) -- this field is a structural
                                  // invariant-true for every recorded candidate, not an
                                  // approximation.
                        );
                        decisions_seen += 1;
                        let mut input = [0f32; D170A_INPUT_FEATURES];
                        input[..D170A_STATE_FEATURES].copy_from_slice(&state);
                        {
                            let block = &mut input[D170A_STATE_FEATURES..];
                            block[0] = current_turn as f32 / MACRO_TOTAL_TURNS as f32;
                            block[1] = opp_workers as f32 / 6.0;
                            block[2 + decision_arm_index(arm)] = 1.0;
                            let (primary, secondary) =
                                affordance(&game, task.seat, entry_unit_id, arm);
                            block[2 + D170A_ARMS] = primary;
                            block[2 + D170A_ARMS + 1] = secondary;
                        }
                        assert!(input.iter().all(|value| value.is_finite()));
                        candidates.push(D172aCandidate {
                            arm,
                            turn: current_turn,
                            input,
                        });
                    }
                }
            }

            let commands = if task.seat == 0 {
                [seat_commands, theirs_commands]
            } else {
                [theirs_commands, seat_commands]
            };

            let before = game.clone();
            let owners_before = owners.clone();
            let before_plants: BTreeSet<_> = before.plants.iter().map(|plant| plant.pos()).collect();
            let attempts = [
                plant_attempts(&before, 0, &commands[0]),
                plant_attempts(&before, 1, &commands[1]),
            ];
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

            let (failures, own_plants, opponent_plants, _joint_plants, _ambiguous_plants) =
                update_provenance(&game, &before_plants, &attempts, &mut owners, task.seat);
            provenance_failures += failures;
            own_created_crops += own_plants;
            opponent_created_crops += opponent_plants;
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
            for event in production {
                history.insert(event.unit_id, event.record);
            }

            // OPT_RETURN's genuine post-step gate (byte-identical to
            // D169a's own post-step activation check); the trig gate above
            // is pre-step and same-turn, so it needs no post-step latch.
            if entry_captured && entry_turn == current_turn && bank_fruit_total(&game, task.seat) > 0
            {
                return_pending = true;
            }

            let after_workers = worker_count(&game, task.seat);
            max_own_workers = max_own_workers.max(after_workers);
            done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        }

        D172aScan {
            candidates,
            control_own_score: game.scores[task.seat],
            control_opponent_score: game.scores[1 - task.seat],
        }
    }

    /// One labeled corpus row: a candidate's full input vector + its exact
    /// counterfactual value (D169a's own per-(task,arm) paired margin,
    /// unmodified machinery).
    #[derive(Clone, Debug)]
    pub(super) struct D172aRow {
        pub(super) task: Task,
        pub(super) turn: i32,
        pub(super) arm_index: usize, // 1..=13, arm_catalog() index (0 = control, never emitted)
        pub(super) input: [f32; D170A_INPUT_FEATURES],
        pub(super) label: i32,
        pub(super) control_own_score: i32,
        pub(super) control_opponent_score: i32,
        pub(super) arm_own_score: i32,
        pub(super) arm_opponent_score: i32,
    }

    /// Phase 0/1: label every candidate the control scan discovers with its
    /// exact D169a-machinery counterfactual value. Cross-validates
    /// (panicking on any mismatch) that the scan's "offered" set agrees
    /// exactly with `d169a_play`'s own `activated` telemetry for all 13
    /// arms, and (for the 12 non-Return arms, whose offering convention is
    /// turn-identical to D169a's own bookkeeping) that the offered turn
    /// matches `d169a_play`'s own recorded `activation_turn` exactly.
    fn label_task(task: Task) -> Vec<D172aRow> {
        let scan = scan_task(task);
        let catalog = arm_catalog();
        let mut rows = Vec::with_capacity(scan.candidates.len());
        for arm_index in 1..catalog.len() {
            let arm = catalog[arm_index];
            let offered = scan.candidates.iter().find(|candidate| candidate.arm == arm);
            let played = d169a_play(task, arm_index, arm);
            assert_eq!(
                offered.is_some(),
                played.outcome.activated,
                "task {task:?} arm {arm:?}: scan-offered={} but d169a_play-activated={}",
                offered.is_some(),
                played.outcome.activated
            );
            if let Some(candidate) = offered {
                if !matches!(arm, ArmKind::Return) {
                    assert_eq!(
                        candidate.turn, played.outcome.activation_turn,
                        "task {task:?} arm {arm:?}: offered turn {} != d169a_play activation_turn {}",
                        candidate.turn, played.outcome.activation_turn
                    );
                }
                let label = (played.outcome.own_score - played.outcome.opponent_score)
                    - (scan.control_own_score - scan.control_opponent_score);
                rows.push(D172aRow {
                    task,
                    turn: candidate.turn,
                    arm_index,
                    input: candidate.input,
                    label,
                    control_own_score: scan.control_own_score,
                    control_opponent_score: scan.control_opponent_score,
                    arm_own_score: played.outcome.own_score,
                    arm_opponent_score: played.outcome.opponent_score,
                });
            }
        }
        rows
    }

    const D172A_CORPUS_HEADER: &str = "map_seed\tseat\topponent_index\topponent\tturn\tarm_index\tarm_label\tlabel\tcontrol_own_score\tcontrol_opponent_score\tarm_own_score\tarm_opponent_score\tfeatures";

    fn d172a_write_corpus_rows(writer: &mut impl Write, rows: &[D172aRow]) {
        let catalog = arm_catalog();
        for row in rows {
            let mut features = String::with_capacity(row.input.len() * 10);
            for (index, value) in row.input.iter().enumerate() {
                if index > 0 {
                    features.push(',');
                }
                features.push_str(&format!("{value:.9}"));
            }
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                row.task.map_seed,
                row.task.seat,
                row.task.opponent,
                MacroOpponentMode::from_index(row.task.opponent).label(),
                row.turn,
                row.arm_index,
                catalog[row.arm_index].label(),
                row.label,
                row.control_own_score,
                row.control_opponent_score,
                row.arm_own_score,
                row.arm_opponent_score,
                features,
            )
            .expect("write D172a corpus row");
        }
    }

    /// Phase 1 corpus generation over `[start_seed, start_seed+maps)` x 2
    /// seats x 8 families, threaded with the same manual work-stealing pool
    /// D169a's own `d169a_main` uses. Streams shard files every
    /// `SHARD_MAPS` maps (API-drop / storage-window resilience: never only
    /// writes at the very end) and prints a JSON progress line per shard to
    /// stderr for the phase-marker log.
    fn d172a_corpus_main(start_seed: i64, maps: usize, output_prefix: &str, threads: usize) {
        const SHARD_MAPS: usize = 128;
        let opponents = MacroOpponentMode::ALL.len();
        let started = Instant::now();
        let mut shard_start = 0usize;
        let mut total_rows = 0usize;
        let mut total_tasks = 0usize;
        while shard_start < maps {
            let shard_maps = SHARD_MAPS.min(maps - shard_start);
            let shard_seed = start_seed + shard_start as i64;
            let work: Vec<Task> = (0..shard_maps)
                .flat_map(|offset| {
                    let map_seed = shard_seed + offset as i64;
                    (0..2).flat_map(move |seat| {
                        (0..opponents).map(move |opponent| Task {
                            map_seed,
                            seat,
                            opponent,
                        })
                    })
                })
                .collect();
            let work = Arc::new(work);
            let next = Arc::new(AtomicUsize::new(0));
            let rows: Arc<Mutex<Vec<D172aRow>>> = Arc::new(Mutex::new(Vec::new()));
            let handles: Vec<_> = (0..threads.min(work.len()).max(1))
                .map(|_| {
                    let work = Arc::clone(&work);
                    let next = Arc::clone(&next);
                    let rows = Arc::clone(&rows);
                    thread::spawn(move || loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        let Some(task) = work.get(index).copied() else {
                            break;
                        };
                        let task_rows = label_task(task);
                        rows.lock().expect("D172a rows lock").extend(task_rows);
                    })
                })
                .collect();
            for handle in handles {
                handle.join().expect("D172a worker thread");
            }
            let mut rows = Arc::try_unwrap(rows)
                .ok()
                .expect("sole D172a rows")
                .into_inner()
                .expect("D172a rows lock");
            rows.sort_by(|a, b| {
                (a.task, a.arm_index, a.turn).cmp(&(b.task, b.arm_index, b.turn))
            });
            let shard_path = format!(
                "{output_prefix}.shard-{shard_seed}-{}.tsv",
                shard_seed + shard_maps as i64 - 1
            );
            {
                let mut writer = BufWriter::new(File::create(&shard_path).expect("create shard"));
                writeln!(writer, "{D172A_CORPUS_HEADER}").expect("write shard header");
                d172a_write_corpus_rows(&mut writer, &rows);
                writer.flush().expect("flush shard");
            }
            total_rows += rows.len();
            total_tasks += work.len();
            shard_start += shard_maps;
            eprintln!(
                "{{\"event\":\"d172a_corpus_shard\",\"shard_seed\":{shard_seed},\"shard_maps\":{shard_maps},\"maps_done\":{shard_start},\"maps_total\":{maps},\"shard_rows\":{},\"total_rows\":{total_rows},\"total_tasks\":{total_tasks},\"elapsed_s\":{:.3},\"path\":\"{shard_path}\"}}",
                rows.len(),
                started.elapsed().as_secs_f64()
            );
        }
        eprintln!(
            "{{\"event\":\"d172a_corpus_done\",\"maps\":{maps},\"tasks\":{total_tasks},\"rows\":{total_rows},\"elapsed_s\":{:.3}}}",
            started.elapsed().as_secs_f64()
        );
    }

    /// Phase 0: recompute a stride-sampled subset of D169a's own consumed-
    /// panel bulk TSV via `d169a_play` (this file's own copy, hash-verified
    /// byte-identical to the source) and compare own_score/opponent_score/
    /// action_hash/state_hash byte-exact. Column lookup is by header name
    /// (not hardcoded index) to avoid any transcription risk. Exits 1 on any
    /// mismatch.
    fn d172a_phase0_sample(tsv_path: &str, n: usize) {
        let text = std::fs::read_to_string(tsv_path).expect("read D169a bulk TSV");
        let mut lines = text.lines();
        let header: Vec<&str> = lines.next().expect("TSV header").split('\t').collect();
        let col = |name: &str| -> usize {
            header
                .iter()
                .position(|candidate| *candidate == name)
                .unwrap_or_else(|| panic!("column {name} not found in {tsv_path}"))
        };
        let (c_map_seed, c_seat, c_opponent_index, c_policy_index, c_own_score, c_opponent_score, c_action_hash, c_state_hash) = (
            col("map_seed"),
            col("seat"),
            col("opponent_index"),
            col("policy_index"),
            col("own_score"),
            col("opponent_score"),
            col("action_hash"),
            col("state_hash"),
        );
        let all_rows: Vec<Vec<&str>> = lines.map(|line| line.split('\t').collect()).collect();
        assert!(!all_rows.is_empty(), "D169a bulk TSV has no data rows");
        let stride = (all_rows.len() / n).max(1);
        let catalog = arm_catalog();
        let mut checked = 0usize;
        let mut mismatches = 0usize;
        for row in all_rows.iter().step_by(stride).take(n) {
            let map_seed: i64 = row[c_map_seed].parse().expect("map_seed");
            let seat: usize = row[c_seat].parse().expect("seat");
            let opponent: usize = row[c_opponent_index].parse().expect("opponent_index");
            let arm_index: usize = row[c_policy_index].parse().expect("policy_index");
            let recorded_own_score: i32 = row[c_own_score].parse().expect("own_score");
            let recorded_opponent_score: i32 = row[c_opponent_score].parse().expect("opponent_score");
            let recorded_action_hash: u64 = row[c_action_hash].parse().expect("action_hash");
            let recorded_state_hash: u64 = row[c_state_hash].parse().expect("state_hash");
            let task = Task {
                map_seed,
                seat,
                opponent,
            };
            let arm = catalog[arm_index];
            let recomputed = d169a_play(task, arm_index, arm);
            let ok = recomputed.outcome.own_score == recorded_own_score
                && recomputed.outcome.opponent_score == recorded_opponent_score
                && recomputed.outcome.action_hash == recorded_action_hash
                && recomputed.outcome.state_hash == recorded_state_hash;
            checked += 1;
            if !ok {
                mismatches += 1;
                eprintln!(
                    "{{\"event\":\"d172a_phase0_mismatch\",\"task\":{task:?},\"arm_index\":{arm_index},\"recorded_own_score\":{recorded_own_score},\"recomputed_own_score\":{},\"recorded_opponent_score\":{recorded_opponent_score},\"recomputed_opponent_score\":{},\"recorded_action_hash\":{recorded_action_hash},\"recomputed_action_hash\":{},\"recorded_state_hash\":{recorded_state_hash},\"recomputed_state_hash\":{}}}",
                    recomputed.outcome.own_score,
                    recomputed.outcome.opponent_score,
                    recomputed.outcome.action_hash,
                    recomputed.outcome.state_hash,
                );
            }
        }
        println!(
            "{{\"event\":\"d172a_phase0_result\",\"tsv\":\"{tsv_path}\",\"checked\":{checked},\"mismatches\":{mismatches},\"verdict\":\"{}\"}}",
            if mismatches == 0 { "PASS" } else { "BLOCKED" }
        );
        if mismatches > 0 {
            std::process::exit(1);
        }
    }

    // ── Phase 3/4: model loading + inference + closed-loop policy runtime ──

    const D172A_HIDDEN: usize = 16;

    /// Weights loaded from a plain whitespace-separated text file (this
    /// crate declares no serde dependency; the export format is documented
    /// in `cgauto/train_d172a_dense_counterfactual_option_policy.py`).
    /// `LINEAR <inputs> <outputs>` then row-major W (outputs x inputs) then
    /// b (outputs). `MLP <inputs> <hidden> <outputs>` then row-major W1
    /// (hidden x inputs), b1 (hidden), row-major W2 (outputs x hidden), b2
    /// (outputs).
    #[derive(Clone, Debug)]
    enum D172aModel {
        Linear {
            w: Vec<f32>,
            b: Vec<f32>,
        },
        Mlp {
            w1: Vec<f32>,
            b1: Vec<f32>,
            w2: Vec<f32>,
            b2: Vec<f32>,
        },
    }

    impl D172aModel {
        fn load(path: &str) -> Self {
            let text = std::fs::read_to_string(path).expect("read D172a model weights");
            let tokens: Vec<&str> = text.split_whitespace().collect();
            let mut pos = 0usize;
            macro_rules! next_str {
                () => {{
                    let value = tokens[pos];
                    pos += 1;
                    value
                }};
            }
            macro_rules! next_usize {
                () => {
                    next_str!().parse::<usize>().expect("usize weight token")
                };
            }
            macro_rules! next_f32 {
                () => {
                    next_str!().parse::<f32>().expect("f32 weight token")
                };
            }
            match next_str!() {
                "LINEAR" => {
                    let inputs = next_usize!();
                    let outputs = next_usize!();
                    assert_eq!(inputs, D170A_INPUT_FEATURES);
                    assert_eq!(outputs, D170A_ARMS);
                    let w: Vec<f32> = (0..inputs * outputs).map(|_| next_f32!()).collect();
                    let b: Vec<f32> = (0..outputs).map(|_| next_f32!()).collect();
                    D172aModel::Linear { w, b }
                }
                "MLP" => {
                    let inputs = next_usize!();
                    let hidden = next_usize!();
                    let outputs = next_usize!();
                    assert_eq!(inputs, D170A_INPUT_FEATURES);
                    assert_eq!(hidden, D172A_HIDDEN);
                    assert_eq!(outputs, D170A_ARMS);
                    let w1: Vec<f32> = (0..inputs * hidden).map(|_| next_f32!()).collect();
                    let b1: Vec<f32> = (0..hidden).map(|_| next_f32!()).collect();
                    let w2: Vec<f32> = (0..hidden * outputs).map(|_| next_f32!()).collect();
                    let b2: Vec<f32> = (0..outputs).map(|_| next_f32!()).collect();
                    D172aModel::Mlp { w1, b1, w2, b2 }
                }
                other => panic!("unknown D172a model kind {other}"),
            }
        }

        /// Per-option (13-wide) predicted value for one 81-field input.
        fn score(&self, x: &[f32; D170A_INPUT_FEATURES]) -> [f32; D170A_ARMS] {
            let mut out = [0f32; D170A_ARMS];
            match self {
                D172aModel::Linear { w, b } => {
                    for k in 0..D170A_ARMS {
                        let mut s = b[k];
                        for i in 0..D170A_INPUT_FEATURES {
                            s += w[k * D170A_INPUT_FEATURES + i] * x[i];
                        }
                        out[k] = s;
                    }
                }
                D172aModel::Mlp { w1, b1, w2, b2 } => {
                    let mut h = [0f32; D172A_HIDDEN];
                    for j in 0..D172A_HIDDEN {
                        let mut s = b1[j];
                        for i in 0..D170A_INPUT_FEATURES {
                            s += w1[j * D170A_INPUT_FEATURES + i] * x[i];
                        }
                        h[j] = s.max(0.0);
                    }
                    for k in 0..D170A_ARMS {
                        let mut s = b2[k];
                        for j in 0..D172A_HIDDEN {
                            s += w2[k * D172A_HIDDEN + j] * h[j];
                        }
                        out[k] = s;
                    }
                }
            }
            out
        }
    }

    #[derive(Clone, Debug)]
    pub(super) struct D172aEvalRow {
        pub(super) task: Task,
        pub(super) own_score: i32,
        pub(super) opponent_score: i32,
        pub(super) control_own_score: i32,
        pub(super) control_opponent_score: i32,
        pub(super) chosen_arm: usize, // 0 = control, else arm_catalog() index 1..=13
        pub(super) decisions_seen: usize,
        pub(super) purity_violations: u16,
        pub(super) invalid_direct_commands: u16,
        pub(super) provenance_failures: u16,
    }

    /// Phase 3/4 runtime: closed-loop, budget-1, true-argmax-over-the-
    /// simultaneously-offered-group decision using a fitted linear/MLP
    /// model, tau-thresholded. Built entirely from the same two primitives
    /// as Phase 1 (`scan_task` for candidates/features, `d169a_play` for
    /// the chosen arm's real full-game outcome) since both function classes
    /// are memoryless (Markov) in the observable features -- there is no
    /// difference between "decide online, turn by turn" and "scan once,
    /// then pick the first turn whose offered group's argmax clears tau"
    /// for a memoryless policy over a deterministic environment: every
    /// candidate a real online rollout would ever present before that turn
    /// is identical to control (nothing has been invoked yet), which is
    /// exactly what `scan_task` already enumerates.
    fn eval_task(task: Task, model: &D172aModel, tau: f32) -> D172aEvalRow {
        let scan = scan_task(task);
        let mut chosen: Option<(usize, ArmKind)> = None;
        let mut decisions_seen = 0usize;
        let mut index = 0usize;
        'groups: while index < scan.candidates.len() {
            let turn = scan.candidates[index].turn;
            let mut group_end = index;
            let mut best: Option<(usize, ArmKind, f32)> = None;
            while group_end < scan.candidates.len() && scan.candidates[group_end].turn == turn {
                let candidate = &scan.candidates[group_end];
                let zero_based = decision_arm_index(candidate.arm);
                decisions_seen += 1;
                let scores = model.score(&candidate.input);
                let value = scores[zero_based];
                if best.map_or(true, |(_, _, best_value)| value > best_value) {
                    best = Some((zero_based + 1, candidate.arm, value));
                }
                group_end += 1;
            }
            if let Some((arm_index, arm, value)) = best {
                if value > tau {
                    chosen = Some((arm_index, arm));
                    break 'groups;
                }
            }
            index = group_end;
        }
        match chosen {
            None => D172aEvalRow {
                task,
                own_score: scan.control_own_score,
                opponent_score: scan.control_opponent_score,
                control_own_score: scan.control_own_score,
                control_opponent_score: scan.control_opponent_score,
                chosen_arm: 0,
                decisions_seen,
                purity_violations: 0,
                invalid_direct_commands: 0,
                provenance_failures: 0,
            },
            Some((arm_index, arm)) => {
                let played = d169a_play(task, arm_index, arm);
                D172aEvalRow {
                    task,
                    own_score: played.outcome.own_score,
                    opponent_score: played.outcome.opponent_score,
                    control_own_score: scan.control_own_score,
                    control_opponent_score: scan.control_opponent_score,
                    chosen_arm: arm_index,
                    decisions_seen,
                    purity_violations: played.outcome.purity_violations,
                    invalid_direct_commands: played.outcome.invalid_direct_commands,
                    provenance_failures: played.outcome.provenance_failures,
                }
            }
        }
    }

    fn d172a_arm_label(chosen_arm: usize) -> String {
        if chosen_arm == 0 {
            "control".to_string()
        } else {
            arm_catalog()[chosen_arm].label()
        }
    }

    fn d172a_eval_row_json(row: &D172aEvalRow) -> String {
        let margin = row.own_score - row.opponent_score;
        let control_margin = row.control_own_score - row.control_opponent_score;
        let paired_margin = margin - control_margin;
        let own_score_delta = row.own_score - row.control_own_score;
        format!(
            "{{\"map_seed\":{},\"seat\":{},\"opponent\":{},\"opponent_name\":\"{}\",\"own_score\":{},\"opponent_score\":{},\"margin\":{},\"control_margin\":{},\"control_own_score\":{},\"paired_margin\":{},\"own_score_delta\":{},\"chosen_arm\":{},\"chosen_arm_label\":\"{}\",\"decisions_seen\":{},\"budget_used\":{},\"purity_violations\":{},\"invalid_direct_commands\":{},\"provenance_failures\":{}}}",
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.own_score,
            row.opponent_score,
            margin,
            control_margin,
            row.control_own_score,
            paired_margin,
            own_score_delta,
            row.chosen_arm,
            d172a_arm_label(row.chosen_arm),
            row.decisions_seen,
            row.chosen_arm != 0,
            row.purity_violations,
            row.invalid_direct_commands,
            row.provenance_failures,
        )
    }

    fn d172a_eval_main(
        model_path: &str,
        tau: f32,
        start_seed: i64,
        maps: usize,
        output: &str,
        threads: usize,
    ) {
        let model = Arc::new(D172aModel::load(model_path));
        let opponents = MacroOpponentMode::ALL.len();
        let work: Vec<Task> = (0..maps)
            .flat_map(|offset| {
                let map_seed = start_seed + offset as i64;
                (0..2).flat_map(move |seat| {
                    (0..opponents).map(move |opponent| Task {
                        map_seed,
                        seat,
                        opponent,
                    })
                })
            })
            .collect();
        let work = Arc::new(work);
        let next = Arc::new(AtomicUsize::new(0));
        let rows: Arc<Mutex<Vec<D172aEvalRow>>> = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
        let started = Instant::now();
        let handles: Vec<_> = (0..threads.min(work.len()).max(1))
            .map(|_| {
                let work = Arc::clone(&work);
                let next = Arc::clone(&next);
                let rows = Arc::clone(&rows);
                let model = Arc::clone(&model);
                thread::spawn(move || loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    let Some(task) = work.get(index).copied() else {
                        break;
                    };
                    let row = eval_task(task, &model, tau);
                    rows.lock().expect("D172a eval rows lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D172a eval worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D172a eval rows")
            .into_inner()
            .expect("D172a eval rows lock");
        rows.sort_by_key(|row| row.task);
        let mut writer = BufWriter::new(File::create(output).expect("create D172a eval output"));
        for row in &rows {
            writeln!(writer, "{}", d172a_eval_row_json(row)).expect("write D172a eval row");
        }
        writer.flush().expect("flush D172a eval output");
        eprintln!(
            "{{\"event\":\"d172a_eval_done\",\"tasks\":{},\"threads\":{},\"elapsed_s\":{:.3},\"path\":\"{output}\"}}",
            rows.len(),
            threads,
            started.elapsed().as_secs_f64()
        );
    }

    pub(super) fn d172a_main() {
        let args: Vec<_> = std::env::args().collect();
        match args.get(1).map(String::as_str) {
            Some("phase0-sample") => {
                assert_eq!(args.len(), 4, "usage: d172a_dense_counterfactual_corpus phase0-sample TSV_PATH N");
                let n: usize = parse(&args[3], "n");
                d172a_phase0_sample(&args[2], n);
            }
            Some("corpus") => {
                assert_eq!(
                    args.len(),
                    6,
                    "usage: d172a_dense_counterfactual_corpus corpus START_SEED MAPS OUTPUT_PREFIX THREADS"
                );
                let start_seed: i64 = parse(&args[2], "start seed");
                let maps: usize = parse(&args[3], "maps");
                let threads: usize = parse(&args[5], "threads");
                assert!(maps > 0 && threads > 0);
                d172a_corpus_main(start_seed, maps, &args[4], threads);
            }
            Some("eval") => {
                assert_eq!(
                    args.len(),
                    8,
                    "usage: d172a_dense_counterfactual_corpus eval MODEL_PATH TAU START_SEED MAPS OUTPUT THREADS"
                );
                let tau: f32 = args[3].parse().expect("tau");
                let start_seed: i64 = parse(&args[4], "start seed");
                let maps: usize = parse(&args[5], "maps");
                let threads: usize = parse(&args[7], "threads");
                assert!(maps > 0 && threads > 0);
                d172a_eval_main(&args[2], tau, start_seed, maps, &args[6], threads);
            }
            Some("dump-scan") => {
                // Phase-0 extended validation only: dump every candidate's
                // full input vector for an independent cross-language
                // comparison against the live tf_d170a_* FFI (via
                // D170aVecEnv, all-KEEP) -- not part of the frozen protocol
                // gates, a defensive check on top of them.
                assert_eq!(
                    args.len(), 5,
                    "usage: d172a_dense_counterfactual_corpus dump-scan START_SEED MAPS OUTPUT"
                );
                let start_seed: i64 = parse(&args[2], "start seed");
                let maps: usize = parse(&args[3], "maps");
                let output = &args[4];
                let opponents = MacroOpponentMode::ALL.len();
                let mut writer = BufWriter::new(File::create(output).expect("create dump-scan output"));
                for offset in 0..maps {
                    let map_seed = start_seed + offset as i64;
                    for seat in 0..2 {
                        for opponent in 0..opponents {
                            let task = Task { map_seed, seat, opponent };
                            let scan = scan_task(task);
                            for candidate in &scan.candidates {
                                let features: Vec<String> = candidate
                                    .input
                                    .iter()
                                    .map(|value| format!("{value:.9}"))
                                    .collect();
                                writeln!(
                                    writer,
                                    "{{\"map_seed\":{map_seed},\"seat\":{seat},\"opponent\":{opponent},\"turn\":{},\"arm\":\"{}\",\"features\":[{}]}}",
                                    candidate.turn,
                                    candidate.arm.label(),
                                    features.join(","),
                                )
                                .expect("write dump-scan row");
                            }
                        }
                    }
                }
                writer.flush().expect("flush dump-scan output");
            }
            other => panic!(
                "usage: d172a_dense_counterfactual_corpus {{phase0-sample|corpus|eval|dump-scan}} ... (got {other:?})"
            ),
        }
    }

    #[cfg(test)]
    mod d172a_tests {
        use super::*;

        const TASK0: Task = Task {
            map_seed: 9_860_000,
            seat: 0,
            opponent: 0,
        };

        #[test]
        fn scan_is_deterministic() {
            let first = scan_task(TASK0);
            let second = scan_task(TASK0);
            assert_eq!(first.control_own_score, second.control_own_score);
            assert_eq!(first.control_opponent_score, second.control_opponent_score);
            assert_eq!(first.candidates.len(), second.candidates.len());
            for (a, b) in first.candidates.iter().zip(second.candidates.iter()) {
                assert_eq!(a.arm, b.arm);
                assert_eq!(a.turn, b.turn);
                assert_eq!(a.input, b.input);
            }
        }

        #[test]
        fn scan_matches_control_arm_score_exactly() {
            for map_seed in 9_860_000..9_860_008 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        let scan = scan_task(task);
                        let control = d169a_play(task, 0, ArmKind::Control);
                        assert_eq!(scan.control_own_score, control.outcome.own_score);
                        assert_eq!(scan.control_opponent_score, control.outcome.opponent_score);
                    }
                }
            }
        }

        #[test]
        fn label_task_offered_set_matches_d169a_play_activated_for_every_arm() {
            // label_task itself asserts this internally (panics on
            // mismatch); this test just exercises it across a small sweep
            // and confirms it returns without panicking, plus sanity-checks
            // row content.
            for map_seed in 9_860_000..9_860_016 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        let rows = label_task(task);
                        for row in &rows {
                            assert!(row.arm_index >= 1 && row.arm_index <= 13);
                            assert_eq!(
                                row.label,
                                (row.arm_own_score - row.arm_opponent_score)
                                    - (row.control_own_score - row.control_opponent_score)
                            );
                            assert!(row.input.iter().all(|v| v.is_finite()));
                        }
                    }
                }
            }
        }

        #[test]
        fn eval_task_never_invokes_when_tau_is_effectively_infinite() {
            for map_seed in 9_860_000..9_860_004 {
                let task = Task {
                    map_seed,
                    seat: 0,
                    opponent: 0,
                };
                // A zero linear model always scores 0.0 everywhere; with
                // tau=1e9 it can never clear the threshold, so eval must be
                // byte-identical to control.
                let model = D172aModel::Linear {
                    w: vec![0.0; D170A_INPUT_FEATURES * D170A_ARMS],
                    b: vec![0.0; D170A_ARMS],
                };
                let row = eval_task(task, &model, 1.0e9);
                assert_eq!(row.chosen_arm, 0);
                let control = d169a_play(task, 0, ArmKind::Control);
                assert_eq!(row.own_score, control.outcome.own_score);
                assert_eq!(row.opponent_score, control.outcome.opponent_score);
            }
        }

        #[test]
        fn eval_task_always_invokes_first_offered_arm_when_tau_is_effectively_negative_infinite() {
            // A zero-weight linear model with all biases hugely positive
            // scores every arm identically; ties break toward the first
            // candidate encountered in this turn's group (stable `>`
            // comparison keeps the first max). With tau far below any
            // score, the very first turn that offers anything must invoke
            // its first-listed candidate.
            for map_seed in 9_860_000..9_860_004 {
                let task = Task {
                    map_seed,
                    seat: 0,
                    opponent: 0,
                };
                let model = D172aModel::Linear {
                    w: vec![0.0; D170A_INPUT_FEATURES * D170A_ARMS],
                    b: vec![100.0; D170A_ARMS],
                };
                let row = eval_task(task, &model, -1.0e9);
                let scan = scan_task(task);
                if scan.candidates.is_empty() {
                    assert_eq!(row.chosen_arm, 0);
                } else {
                    assert_ne!(row.chosen_arm, 0);
                    let first_turn = scan.candidates[0].turn;
                    let expected_arm = scan.candidates[0].arm;
                    assert_eq!(row.decisions_seen, scan.candidates.iter().take_while(|c| c.turn == first_turn).count());
                    assert_eq!(decision_arm_index(expected_arm) + 1, row.chosen_arm);
                }
            }
        }
    }
}

fn main() {
    inherited::d172a_main();
}
