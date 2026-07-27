//! D169a: resident-native option-interface envelope gate — unified crop-safe
//! envelope over the exact resident, OPT_RETURN (D168a's ARM_A BANK_SEED
//! successor return), and OPT_FRUIT/OPT_IRON/OPT_PROTECT (D163's three
//! resource-control components, each singly enabled, at three fixed starts
//! plus a new observable-trigger TRIG start). See
//! `data/analysis/live-agent-6553250/d169a-resident-option-interface-envelope-protocol-2026-07-27.md`.

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

    const D169A_HEADER: &str = "map_seed\tseat\topponent_index\topponent\tpolicy_index\tpolicy\tarm_family\tcomponent\tstart_kind\tfixed_start\tconfigured_start\tdone\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tmax_own_workers\tsuccessful_trains\tprovenance_failures\town_created_crops\topponent_created_crops\tjoint_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tentry_captured\tentry_turn\tentry_unit_id\tgeneric_return_captured\tgeneric_return_turn\tgeneric_return_verb\topp_worker_trigger_turn\tpurity_violations\tinvalid_direct_commands\tactivated\tactivation_turn\tdeadline\tcommitted\tcommitted_turn\taborted\tabort_reason\tactive_turns\treturn_gate_bank_ok\treturn_species_picked\treturn_species_planted\treturn_plant_cell_x\treturn_plant_cell_y\treturn_move_commands\treturn_pick_commands\treturn_plant_commands\treturn_hold_commands\treturn_pick_attempts\treturn_pick_successes\treturn_plant_attempts\treturn_plant_successes\treturn_vocabulary_violations\tresource_mask\tresource_option_overrides\tresource_fruit_overrides\tresource_iron_overrides\tresource_protected_commands\tresource_move_commands\tresource_bank_commands\tresource_fruit_bank_commands\tresource_iron_bank_commands\tresource_harvest_commands\tresource_mine_commands\tresource_resident_train_commands\tresource_controller_train_commands\tresource_suppressed_train_commands\tresource_initial_bank_deficit\tresource_closest_bank_deficit\tresource_option_command_failures\tresource_workforce_exit_events\tresource_horizon_violations\tresource_restart_violations";

    fn d169a_write_rows(output: &str, rows: &[D169aRow]) {
        let mut writer = BufWriter::new(File::create(output).expect("create D169a output"));
        writeln!(writer, "{D169A_HEADER}").expect("write D169a header");
        for row in rows {
            let out = &row.outcome;
            let ret = out.return_option;
            let res = out.resource;
            let values = vec![
                row.task.map_seed.to_string(),
                row.task.seat.to_string(),
                row.task.opponent.to_string(),
                MacroOpponentMode::from_index(row.task.opponent).label().to_string(),
                row.arm_index.to_string(),
                row.arm.label(),
                row.arm.arm_family().to_string(),
                row.arm.component_label().to_string(),
                row.arm.start_kind_label().to_string(),
                row.arm.fixed_start().to_string(),
                out.configured_start.to_string(),
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
                out.provenance_failures.to_string(),
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
                opt_i32(out.opp_worker_trigger_turn),
                out.purity_violations.to_string(),
                out.invalid_direct_commands.to_string(),
                usize::from(out.activated).to_string(),
                opt_i32(out.activation_turn),
                opt_i32(out.deadline),
                usize::from(out.committed).to_string(),
                opt_i32(out.committed_turn),
                usize::from(out.aborted).to_string(),
                out.abort_reason.to_string(),
                out.active_turns.to_string(),
                usize::from(ret.gate_bank_ok).to_string(),
                species_name(ret.species_picked).to_string(),
                species_name(ret.species_planted).to_string(),
                opt_i32(ret.plant_cell_x),
                opt_i32(ret.plant_cell_y),
                ret.move_commands.to_string(),
                ret.pick_commands.to_string(),
                ret.plant_commands.to_string(),
                ret.hold_commands.to_string(),
                ret.pick_attempts.to_string(),
                ret.pick_successes.to_string(),
                ret.plant_attempts.to_string(),
                ret.plant_successes.to_string(),
                ret.vocabulary_violations.to_string(),
                out.resource_mask.to_string(),
                res.option_overrides.to_string(),
                res.fruit_overrides.to_string(),
                res.iron_overrides.to_string(),
                res.protected_commands.to_string(),
                res.move_commands.to_string(),
                res.bank_commands.to_string(),
                res.fruit_bank_commands.to_string(),
                res.iron_bank_commands.to_string(),
                res.harvest_commands.to_string(),
                res.mine_commands.to_string(),
                res.resident_train_commands.to_string(),
                res.controller_train_commands.to_string(),
                res.suppressed_train_commands.to_string(),
                res.initial_bank_deficit.to_string(),
                res.closest_bank_deficit.to_string(),
                res.option_command_failures.to_string(),
                res.workforce_exit_events.to_string(),
                res.horizon_violations.to_string(),
                res.restart_violations.to_string(),
            ];
            writeln!(writer, "{}", values.join("\t")).expect("write D169a row");
        }
        writer.flush().expect("flush D169a output");
    }

    #[derive(Clone, Copy, Debug)]
    struct D169aWork {
        task: Task,
        arm_index: usize,
        arm: ArmKind,
    }

    pub(super) fn d169a_main() {
        let args: Vec<_> = std::env::args().collect();
        assert_eq!(
            args.len(),
            5,
            "usage: d169a_resident_option_envelope START_SEED MAPS OUTPUT THREADS"
        );
        let start_seed: i64 = parse(&args[1], "start seed");
        let maps: usize = parse(&args[2], "maps");
        let output = &args[3];
        let threads: usize = parse(&args[4], "threads");
        assert!(maps > 0 && threads > 0);
        assert!(start_seed >= 9_844_136);
        assert!(start_seed + maps as i64 <= 9_844_200);

        let arms = Arc::new(arm_catalog());
        let arm_count = arms.len();
        let work: Vec<_> = (start_seed..start_seed + maps as i64)
            .flat_map(|map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).flat_map(move |opponent| {
                        (0..arm_count).map(move |arm_index| D169aWork {
                            task: Task {
                                map_seed,
                                seat,
                                opponent,
                            },
                            arm_index,
                            arm: ArmKind::Control, // placeholder, replaced below via arms[]
                        })
                    })
                })
            })
            .collect();
        let work: Vec<_> = work
            .into_iter()
            .map(|item| D169aWork {
                arm: arms[item.arm_index],
                ..item
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
                    let row = d169a_play(item.task, item.arm_index, item.arm);
                    rows.lock().expect("D169a row lock").push(row);
                })
            })
            .collect();
        for handle in handles {
            handle.join().expect("D169a worker thread");
        }
        let mut rows = Arc::try_unwrap(rows)
            .ok()
            .expect("sole D169a rows")
            .into_inner()
            .expect("D169a rows lock");
        rows.sort_by_key(|row| (row.task, row.arm_index));
        d169a_write_rows(output, &rows);
        eprintln!(
            "saved {} D169a rows with {} workers in {:.3}s to {}",
            rows.len(),
            threads.min(work.len()),
            started.elapsed().as_secs_f64(),
            output,
        );
    }

    #[cfg(test)]
    mod d169a_tests {
        use super::*;

        const TASK0: Task = Task {
            map_seed: 9_844_136,
            seat: 0,
            opponent: 0,
        };

        #[test]
        fn frozen_catalog_has_control_return_and_twelve_resource_arms() {
            let arms = arm_catalog();
            assert_eq!(arms.len(), 14);
            assert_eq!(arms[0].label(), "control");
            assert_eq!(arms[1].label(), "opt_return");
            assert_eq!(arms[2].label(), "opt_fruit_t072");
            assert_eq!(arms[3].label(), "opt_fruit_t104");
            assert_eq!(arms[4].label(), "opt_fruit_t136");
            assert_eq!(arms[5].label(), "opt_fruit_trig");
            assert_eq!(arms[6].label(), "opt_iron_t072");
            assert_eq!(arms[9].label(), "opt_iron_trig");
            assert_eq!(arms[10].label(), "opt_protect_t072");
            assert_eq!(arms[13].label(), "opt_protect_trig");
            let labels: BTreeSet<_> = arms.iter().map(|arm| arm.label()).collect();
            assert_eq!(labels.len(), 14, "all 14 arm labels must be unique");
        }

        #[test]
        fn control_matches_d162s_own_disabled_option_control() {
            let d169a = d169a_play(TASK0, 0, ArmKind::Control);
            let d162_control = play(
                TASK0,
                0,
                &PolicySpec {
                    label: "resident".to_string(),
                    option: None,
                },
            );
            assert_eq!(d169a.outcome.own_score, d162_control.outcome.own_score);
            assert_eq!(d169a.outcome.opponent_score, d162_control.outcome.opponent_score);
            assert_eq!(d169a.outcome.action_hash, d162_control.outcome.action_hash);
            assert_eq!(d169a.outcome.state_hash, d162_control.outcome.state_hash);
            assert_eq!(d169a.outcome.activated, false);
            assert_eq!(d169a.outcome.purity_violations, 0);
        }

        #[test]
        fn every_arm_is_deterministic() {
            for arm in arm_catalog() {
                let first = d169a_play(TASK0, 0, arm);
                let second = d169a_play(TASK0, 0, arm);
                assert_eq!(first, second, "arm {:?} not deterministic", arm);
                assert!(first.outcome.done);
            }
        }

        #[test]
        fn inactive_arm_is_byte_exact_vs_control() {
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        let control = d169a_play(task, 0, ArmKind::Control);
                        for (index, arm) in arm_catalog().into_iter().enumerate().skip(1) {
                            let row = d169a_play(task, index, arm);
                            if !row.outcome.activated {
                                assert_eq!(
                                    control.outcome.own_score, row.outcome.own_score,
                                    "task {:?} arm {:?} inactive but score differs", task, arm
                                );
                                assert_eq!(control.outcome.opponent_score, row.outcome.opponent_score);
                                assert_eq!(control.outcome.action_hash, row.outcome.action_hash);
                                assert_eq!(control.outcome.state_hash, row.outcome.state_hash);
                                assert_eq!(control.outcome.max_own_workers, row.outcome.max_own_workers);
                                assert_eq!(control.outcome.own_created_crops, row.outcome.own_created_crops);
                            }
                        }
                    }
                }
            }
        }

        #[test]
        fn controller_command_purity_holds_every_arm() {
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        for (index, arm) in arm_catalog().into_iter().enumerate() {
                            let row = d169a_play(task, index, arm);
                            assert_eq!(
                                row.outcome.purity_violations, 0,
                                "task {:?} arm {:?} had a purity violation",
                                task, arm
                            );
                        }
                    }
                }
            }
        }

        #[test]
        fn resource_arms_never_synthesize_or_suppress_train() {
            for arm in arm_catalog() {
                if !matches!(arm, ArmKind::Resource(..)) {
                    continue;
                }
                let row = d169a_play(TASK0, 0, arm);
                assert_eq!(row.outcome.resource.controller_train_commands, 0);
                assert_eq!(row.outcome.resource.suppressed_train_commands, 0);
                assert_eq!(row.outcome.resource.option_command_failures, 0);
            }
        }

        #[test]
        fn trig_arm_configured_start_equals_observed_opponent_trigger_turn() {
            for map_seed in 9_844_136..9_844_144 {
                let task = Task {
                    map_seed,
                    seat: 0,
                    opponent: 0,
                };
                let control = d169a_play(task, 0, ArmKind::Control);
                let trig = d169a_play(task, 5, ArmKind::Resource(Component::Fruit, StartSpec::Trig));
                assert_eq!(trig.outcome.opp_worker_trigger_turn, control.outcome.opp_worker_trigger_turn);
                if trig.outcome.configured_start >= 0 {
                    assert_eq!(trig.outcome.configured_start, trig.outcome.opp_worker_trigger_turn);
                }
                if trig.outcome.activated {
                    assert_eq!(trig.outcome.activation_turn, trig.outcome.configured_start);
                }
            }
        }

        #[test]
        fn return_arm_never_exceeds_horizon_and_commits_at_most_once() {
            for map_seed in 9_844_136..9_844_140 {
                for seat in 0..2 {
                    for opponent in 0..troll_farm::rl_macro::MacroOpponentMode::ALL.len() {
                        let task = Task {
                            map_seed,
                            seat,
                            opponent,
                        };
                        let row = d169a_play(task, 1, ArmKind::Return);
                        let option = row.outcome.return_option;
                        if option.activated {
                            assert!(i32::from(option.active_turns) <= OPT_RETURN_HORIZON + 1);
                            assert!(!(option.committed && option.aborted));
                            assert!(option.plant_successes <= 1);
                        }
                    }
                }
            }
        }

        #[test]
        fn species_tie_break_prefers_banana_then_apple_then_plum_then_lemon() {
            assert_eq!(choose_species(&[1, 1, 1, 1, 0, 0]), Some(BANANA));
            assert_eq!(choose_species(&[1, 1, 1, 0, 0, 0]), Some(APPLE));
            assert_eq!(choose_species(&[1, 1, 0, 0, 0, 0]), Some(PLUM));
            assert_eq!(choose_species(&[0, 1, 0, 0, 0, 0]), Some(LEMON));
            assert_eq!(choose_species(&[0, 0, 0, 0, 5, 5]), None);
        }

        #[test]
        fn shadow_reserve_is_frozen_and_drops_iron_only_without_ore() {
            let mut game = generate_official(9_844_136);
            assert_eq!(shadow_reserve(&game), [3, 3, 2, 0, 3, 0]);
            game.iron.clear();
            assert_eq!(shadow_reserve(&game), [3, 3, 2, 0, 0, 0]);
        }

        #[test]
        fn no_task_exceeds_three_own_workers_across_all_arms() {
            for arm in arm_catalog() {
                let row = d169a_play(TASK0, 0, arm);
                assert!(row.outcome.max_own_workers <= 3, "arm {:?} exceeded 3 workers", arm);
            }
        }

        #[test]
        fn reward_identity_holds_across_all_arms() {
            for arm in arm_catalog() {
                let row = d169a_play(TASK0, 0, arm);
                assert!(row.outcome.reward_identity_error <= 1e-6);
            }
        }
    }
}

fn main() {
    inherited::d169a_main();
}
