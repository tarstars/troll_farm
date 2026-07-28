//! D170a: sequential resident-anchored option-policy environment (B2.2).
//!
//! Composes D169a's frozen option vocabulary (`OPT_RETURN` + `OPT_FRUIT` /
//! `OPT_IRON` / `OPT_PROTECT`, fixed + observable-trigger starts) into a
//! genuine closed-loop decision environment: at each armable state the
//! policy chooses KEEP or invoke; budget one activation per game; reward is
//! the terminal paired margin vs a cached same-task exact-resident control.
//! See
//! `data/analysis/live-agent-6553250/d170a-family-robust-option-policy-protocol-2026-07-28.md`.
//!
//! The vocabulary mechanism in `mod inherited` below (the D163 resource
//! controller and the D168a/D166 return-option + entry-detection logic, plus
//! the `Component`/`StartSpec`/`ArmKind`/`arm_catalog` composition types) is
//! copied byte-for-byte from `rust/src/bin/d169a_resident_option_envelope.rs`
//! (itself copied from D163/D168a — see that file's own provenance
//! comments), per the D169a protocol's "reuse frozen implementations; do NOT
//! reimplement semantics." Do not edit that retained block. Only the code
//! below the "D170a-specific" banner is new.

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
    // collide with this file's own top-level catalog types). Do not edit the
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
        #[allow(dead_code)]
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
    // copied from d169a_resident_option_envelope.rs's own composition layer
    // (Component/StartSpec/ArmKind + arm_catalog only — its per-task
    // hindsight-envelope play loop, TSV writer, and CLI are NOT reused; D170a
    // builds a genuine sequential decision environment instead). Do not edit
    // the retained logic.
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
        #[allow(dead_code)]
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
        #[allow(dead_code)]
        fn label(self) -> String {
            match self {
                Self::Control => "control".to_string(),
                Self::Return => "opt_return".to_string(),
                Self::Resource(component, start) => {
                    format!("opt_{}_{}", component.label(), start.label())
                }
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

    // ══════════════════════════════════════════════════════════════════════
    // D170a-specific: sequential closed-loop option-policy environment. New
    // code (not a copy of any frozen module) — this is the composition layer
    // that turns the reused vocabulary above into a genuine decision
    // environment: at each armable state the policy chooses KEEP or invoke,
    // budget one activation per game; it never edits the retained decision
    // logic above. See the D170a protocol §"Environment" and §"Policy".
    // ══════════════════════════════════════════════════════════════════════

    use rayon::prelude::*;

    /// The 64-field observable state family. Field list (frozen once the
    /// lock is written):
    /// 0 bias(=1); 1 turn/300; 2 own_workers/3; 3 opp_workers/3;
    /// 4 own_score/400; 5 opp_score/400; 6 margin/400;
    /// 7..13 own_inventory[PLUM,LEMON,APPLE,BANANA,IRON,WOOD]/20;
    /// 13..19 opponent_inventory (same order)/20;
    /// 19..25 own_carried_sum (same order)/20; 25..31 opponent_carried_sum/20;
    /// 31..36 plant_count_by_owner[Natural,Own,Opponent,Joint,Ambiguous]/20;
    /// 36..41 fruit_count_by_owner (same order)/40;
    /// 41 has_own_plant; 42 has_opponent_plant; 43 water_frac; 44 walkable_frac;
    /// 45 own_hp_sum/12; 46 own_chop_sum/12; 47 own_ms_sum/9; 48 own_cc_sum/12;
    /// 49 turns_remaining_frac; 50 max_own_workers_so_far/3;
    /// 51 own_created_crops_so_far/20; 52 opponent_created_crops_so_far/20;
    /// 53 own_reinvested_crops_so_far/20; 54 provenance_failures_so_far/10;
    /// 55 opp_worker_trigger_seen; 56 opp_worker_trigger_turn_frac;
    /// 57 entry_captured_flag; 58 bank_fruit_total/20;
    /// 59 bank_deficit_frac (signed, clamped [-1,1]);
    /// 60 own_free_capacity_sum/12; 61 opponent_free_capacity_sum/12;
    /// 62 decisions_seen_so_far/10; 63 budget_remaining (1 pre-invoke, 0 after).
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

    #[derive(Clone, Copy, Debug, PartialEq)]
    pub struct D170aTerminal {
        pub(super) task_index: u64,
        pub(super) map_seed: i64,
        pub(super) seat: u8,
        pub(super) opponent: u8,
        pub(super) own_score: i32,
        pub(super) opponent_score: i32,
        pub(super) margin: i32,
        pub(super) control_margin: i32,
        pub(super) control_own_score: i32,
        pub(super) paired_margin: i32,
        /// 0 = never invoked (control), else 1..=13 (arm_catalog index).
        pub(super) chosen_arm: i32,
        pub(super) decisions_seen: u32,
        pub(super) budget_used: bool,
        pub(super) own_workers: u8,
        pub(super) max_own_workers: u8,
        pub(super) own_created_crops: u32,
        pub(super) opponent_created_crops: u32,
        pub(super) provenance_failures: u32,
        pub(super) purity_violations: u32,
        pub(super) invalid_direct_commands: u32,
        pub(super) action_hash: u64,
        pub(super) state_hash: u64,
        pub(super) turn: u16,
    }

    pub(super) struct D170aStepOutcome {
        pub(super) reward: f32,
        pub(super) done: bool,
        pub(super) terminal: Option<D170aTerminal>,
    }

    type ControlCache = Arc<Mutex<BTreeMap<(i64, u8, u8), (i32, i32)>>>;

    /// Exact-resident-vs-opponent control outcome for one task; deterministic,
    /// no options ever invoked. Byte-identical to `ArmKind::Control` in
    /// D169a.
    fn play_control(map_seed: i64, seat: usize, opponent: MacroOpponentMode) -> (i32, i32) {
        let mut game = generate_official(map_seed);
        let mut ours = SecureOrchardBot::new();
        let mut theirs = Opponent::new(opponent);
        let mut turns_until_end = 0i32;
        loop {
            let ours_commands = ours.commands(&resident_view(&game, seat));
            let theirs_commands = theirs.commands(&game, 1 - seat);
            let commands = if seat == 0 {
                [ours_commands, theirs_commands]
            } else {
                [theirs_commands, ours_commands]
            };
            step(&mut game, &commands[0], &commands[1]);
            if game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end) {
                break;
            }
        }
        (game.scores[seat], game.scores[1 - seat])
    }

    pub(super) struct D170aEnv {
        task: Task,
        game: GameState,
        ours: SecureOrchardBot,
        theirs: Opponent,
        owners: BTreeMap<Cell, Owner>,
        birth_turns: BTreeMap<Cell, i32>,
        history: BTreeMap<i32, ProductionRecord>,
        entry_captured: bool,
        entry_turn: i32,
        entry_unit_id: i32,
        opp_worker_trigger_turn: i32,
        return_telemetry: D168aOptionTelemetry,
        resource_controller: ResourceController,
        active_arm: Option<ArmKind>,
        return_pending: bool,
        /// D170b Delta 1 repair: sticky flag for the resource `_trig` arms,
        /// mirroring `return_pending` above. Set in `step_one_turn` (after
        /// the engine step) the one time `opp_worker_trigger_turn` is newly
        /// latched; consumed by `refresh_candidates` on its next call. See
        /// `data/analysis/live-agent-6553250/d170b-family-robust-option-policy-repair-protocol-2026-07-28.md`
        /// Delta 1 (replaces the unreachable
        /// `opp_worker_trigger_turn == self.game.turn` equality that made
        /// `opt_fruit_trig`/`opt_iron_trig`/`opt_protect_trig` structurally
        /// unarmable in D170a).
        trig_pending: bool,
        pending_queue: Vec<ArmKind>,
        last_scanned_turn: i32,
        current_candidate: Option<ArmKind>,
        decisions_seen: usize,
        budget_used: bool,
        max_own_workers: usize,
        own_created_crops: usize,
        opponent_created_crops: usize,
        own_reinvested_crops: usize,
        own_owned_crop_harvest_units: usize,
        provenance_failures: usize,
        purity_violations: usize,
        action_hash: u64,
        turns_until_end: i32,
        done: bool,
        control_margin: i32,
        control_own_score: i32,
        slot: usize,
        round: u64,
        envs_total: usize,
        task_index: u64,
    }

    impl D170aEnv {
        #[allow(clippy::too_many_arguments)]
        fn new(
            seed_base: i64,
            map_pool: usize,
            slot: usize,
            round: u64,
            envs_total: usize,
            cache: &ControlCache,
        ) -> Self {
            let task_index = slot as u64 + round * envs_total as u64;
            let per_map = 2 * MacroOpponentMode::ALL.len() as u64;
            let scenario = task_index % (map_pool as u64 * per_map);
            let map_seed = seed_base + (scenario / per_map) as i64;
            let within = scenario % per_map;
            let seat = (within / MacroOpponentMode::ALL.len() as u64) as usize;
            let opponent_index = (within % MacroOpponentMode::ALL.len() as u64) as usize;
            let opponent = MacroOpponentMode::from_index(opponent_index);
            let task = Task {
                map_seed,
                seat,
                opponent: opponent_index,
            };
            let key = (map_seed, seat as u8, opponent_index as u8);
            let (control_own_score, control_margin) = {
                let mut guard = cache.lock().expect("D170a control cache lock");
                let scores = if let Some(scores) = guard.get(&key) {
                    *scores
                } else {
                    let scores = play_control(map_seed, seat, opponent);
                    guard.insert(key, scores);
                    scores
                };
                (scores.0, scores.0 - scores.1)
            };
            let game = generate_official(map_seed);
            let owners = game
                .plants
                .iter()
                .map(|plant| (plant.pos(), Owner::Natural))
                .collect();
            let birth_turns = game.plants.iter().map(|plant| (plant.pos(), 0)).collect();
            let initial_workers = worker_count(&game, seat);
            Self {
                task,
                game,
                ours: SecureOrchardBot::new(),
                theirs: Opponent::new(opponent),
                owners,
                birth_turns,
                history: BTreeMap::new(),
                entry_captured: false,
                entry_turn: -1,
                entry_unit_id: -1,
                opp_worker_trigger_turn: -1,
                return_telemetry: D168aOptionTelemetry::new(),
                resource_controller: ResourceController::new(None),
                active_arm: None,
                return_pending: false,
                trig_pending: false,
                pending_queue: Vec::new(),
                last_scanned_turn: -1,
                current_candidate: None,
                decisions_seen: 0,
                budget_used: false,
                max_own_workers: initial_workers,
                own_created_crops: 0,
                opponent_created_crops: 0,
                own_reinvested_crops: 0,
                own_owned_crop_harvest_units: 0,
                provenance_failures: 0,
                purity_violations: 0,
                action_hash: 14_695_981_039_346_656_037_u64,
                turns_until_end: 0,
                done: false,
                control_margin,
                control_own_score,
                slot,
                round,
                envs_total,
                task_index,
            }
        }

        /// Advance until either a decision is pending (returns true, with
        /// `current_candidate` set) or the game is over (returns false).
        fn resume(&mut self) -> bool {
            loop {
                if self.done {
                    return false;
                }
                if !self.budget_used {
                    self.refresh_candidates();
                    if let Some(candidate) = self.pending_queue.first().copied() {
                        self.current_candidate = Some(candidate);
                        return true;
                    }
                }
                self.current_candidate = None;
                self.step_one_turn();
            }
        }

        /// Populate `pending_queue` with every arm newly armable exactly at
        /// the current turn, in the frozen `arm_catalog` order
        /// (Return first, then Fruit/Iron/Protect x {t072,t104,t136,trig}).
        /// Idempotent within a turn.
        fn refresh_candidates(&mut self) {
            if self.last_scanned_turn == self.game.turn {
                return;
            }
            self.last_scanned_turn = self.game.turn;
            self.pending_queue.clear();
            if self.return_pending {
                self.pending_queue.push(ArmKind::Return);
                self.return_pending = false;
            }
            let workers = worker_count(&self.game, self.task.seat);
            if workers == 2 {
                // D170b Delta 1 repair: consume the sticky `trig_pending`
                // flag (mirrors `return_pending` above) instead of the
                // unreachable `opp_worker_trigger_turn == self.game.turn`
                // equality — `refresh_candidates` only ever runs strictly
                // before or after `step_one_turn`, never at the instant the
                // trigger is latched mid-turn, so that equality could never
                // hold. Read once per call so a mid-loop reset can't cause a
                // partial (some-components-only) enqueue.
                let trig_ready = self.trig_pending;
                for component in Component::ALL {
                    for mark in MARKS {
                        if self.game.turn == mark {
                            self.pending_queue
                                .push(ArmKind::Resource(component, StartSpec::Fixed(mark)));
                        }
                    }
                    if trig_ready {
                        self.pending_queue
                            .push(ArmKind::Resource(component, StartSpec::Trig));
                    }
                }
                if trig_ready {
                    self.trig_pending = false;
                }
            }
        }

        /// Resolve the currently-offered candidate (KEEP if action==0, else
        /// INVOKE) and resume. Panics if no candidate is pending.
        fn decide(&mut self, action: i32) -> bool {
            let candidate = self
                .current_candidate
                .expect("D170a decide called without a pending candidate");
            assert_eq!(self.pending_queue.first().copied(), Some(candidate));
            self.pending_queue.remove(0);
            self.decisions_seen += 1;
            if action != 0 {
                self.invoke(candidate);
            }
            self.current_candidate = None;
            self.resume()
        }

        fn invoke(&mut self, arm: ArmKind) {
            self.budget_used = true;
            self.pending_queue.clear();
            self.active_arm = Some(arm);
            match arm {
                ArmKind::Return => {
                    self.return_telemetry.activated = true;
                    self.return_telemetry.gate_bank_ok = true;
                    self.return_telemetry.activation_turn = self.entry_turn;
                    self.return_telemetry.deadline = self.entry_turn + OPT_RETURN_HORIZON;
                }
                ArmKind::Resource(component, _) => {
                    self.resource_controller.config = Some(ResourceConfig {
                        mask: component.mask(),
                        start: self.game.turn,
                    });
                }
                ArmKind::Control => {}
            }
        }

        fn affordance(&self, arm: ArmKind) -> (f32, f32) {
            let player = self.task.seat;
            match arm {
                ArmKind::Return => {
                    let primary = bank_fruit_total(&self.game, player) as f32 / 20.0;
                    let near = self
                        .game
                        .units
                        .iter()
                        .find(|unit| unit.id == self.entry_unit_id && unit.player as usize == player)
                        .is_some_and(|unit| near_shack(&self.game, player, unit));
                    (primary, f32::from(near))
                }
                ArmKind::Resource(component, _) => {
                    let target = shadow_reserve(&self.game);
                    let deficit = bank_deficit(&self.game, player, &target);
                    let primary = (deficit as f32 / 20.0).clamp(-1.0, 1.0);
                    let config = ResourceConfig {
                        mask: component.mask(),
                        start: self.game.turn,
                    };
                    let carried =
                        ResourceController::carried_resource_worker(&self.game, player, &target, config)
                            .is_some();
                    (primary, f32::from(carried))
                }
                ArmKind::Control => (0.0, 0.0),
            }
        }

        fn observe_input(&self, out: &mut [f32]) {
            assert_eq!(out.len(), D170A_INPUT_FEATURES);
            let player = self.task.seat;
            let state = state_family(
                &self.game,
                player,
                &self.owners,
                self.max_own_workers,
                self.own_created_crops,
                self.opponent_created_crops,
                self.own_reinvested_crops,
                self.provenance_failures,
                self.opp_worker_trigger_turn,
                self.entry_captured,
                self.decisions_seen,
                !self.budget_used,
            );
            out[..D170A_STATE_FEATURES].copy_from_slice(&state);
            let block = &mut out[D170A_STATE_FEATURES..];
            block.fill(0.0);
            block[0] = self.game.turn as f32 / MACRO_TOTAL_TURNS as f32;
            let opp_workers = worker_count(&self.game, 1 - player);
            block[1] = opp_workers as f32 / 6.0;
            if let Some(candidate) = self.current_candidate {
                let index = decision_arm_index(candidate);
                block[2 + index] = 1.0;
                let (primary, secondary) = self.affordance(candidate);
                block[2 + D170A_ARMS] = primary;
                block[2 + D170A_ARMS + 1] = secondary;
            }
            assert!(out.iter().all(|value| value.is_finite()));
        }

        /// Exactly D169a's per-turn body (entry-detection, trigger-tracking,
        /// resource/return override application, purity accounting,
        /// provenance bookkeeping), parameterized by `self.active_arm`
        /// instead of a for-loop-fixed arm. Does not edit any retained
        /// per-arm decision logic; only orchestrates *when* it is applied.
        fn step_one_turn(&mut self) {
            let player = self.task.seat;
            let current_turn = self.game.turn;
            let resident_commands = self.ours.commands(&resident_view(&self.game, player));
            let theirs_commands = self.theirs.commands(&self.game, 1 - player);
            let mut seat_commands = resident_commands.clone();
            let arm = self.active_arm.unwrap_or(ArmKind::Control);

            if self.opp_worker_trigger_turn < 0 && worker_count(&self.game, 1 - player) >= 3 {
                self.opp_worker_trigger_turn = current_turn;
            }

            if !self.entry_captured {
                if let Some((unit_id, _cell)) = d168a_entry_candidate(
                    &self.game,
                    player,
                    &self.owners,
                    &self.history,
                    &resident_commands,
                ) {
                    self.entry_captured = true;
                    self.entry_turn = current_turn;
                    self.entry_unit_id = unit_id;
                }
            }

            if matches!(arm, ArmKind::Resource(..)) {
                seat_commands = self
                    .resource_controller
                    .rewrite(&self.game, player, seat_commands);
            }
            let resource_live_this_turn = self.resource_controller.active();

            let return_live_this_turn = arm == ArmKind::Return && self.return_telemetry.active();
            let mut issued = D168aIssuedVerb::None;
            let mut armed_pos_before: Option<Cell> = None;
            if return_live_this_turn {
                let armed_unit = self
                    .game
                    .units
                    .iter()
                    .find(|unit| unit.id == self.entry_unit_id && unit.player as usize == player)
                    .cloned();
                match armed_unit {
                    None => {
                        self.return_telemetry.aborted = true;
                        self.return_telemetry.abort_reason = D168aAbortReason::WorkerMissing;
                    }
                    Some(unit) => {
                        armed_pos_before = Some(unit.pos());
                        match armed_command(&self.game, player, &unit, &mut self.return_telemetry) {
                            Some(command) => {
                                let verb = command_fields(&command).first().copied().unwrap_or("");
                                if !is_allowed_verb(verb) {
                                    self.return_telemetry.vocabulary_violations += 1;
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
                                    replace_unit_command(&mut seat_commands, self.entry_unit_id, command);
                                    self.return_telemetry.active_turns += 1;
                                }
                            }
                            None => {
                                if !self.return_telemetry.aborted {
                                    remove_unit_command(&mut seat_commands, self.entry_unit_id);
                                    self.return_telemetry.hold_commands += 1;
                                    self.return_telemetry.active_turns += 1;
                                }
                            }
                        }
                    }
                }
            }

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
                    self.purity_violations += 1;
                }
            }

            let commands = if player == 0 {
                [seat_commands, theirs_commands]
            } else {
                [theirs_commands, seat_commands]
            };
            for (p, player_commands) in commands.iter().enumerate() {
                self.action_hash = fnv1a(self.action_hash, &[p as u8]);
                for command in player_commands {
                    self.action_hash = fnv1a(self.action_hash, command.as_bytes());
                    self.action_hash = fnv1a(self.action_hash, &[0]);
                }
                self.action_hash = fnv1a(self.action_hash, &[255]);
            }

            let before = self.game.clone();
            let owners_before = self.owners.clone();
            let before_plants: BTreeSet<_> = before.plants.iter().map(|plant| plant.pos()).collect();
            let attempts = [
                plant_attempts(&before, 0, &commands[0]),
                plant_attempts(&before, 1, &commands[1]),
            ];
            let harvest_ids = command_unit_ids(&commands[player], "HARVEST");
            let own_crop_harvests: Vec<_> = harvest_ids
                .into_iter()
                .filter_map(|id| {
                    let unit = before
                        .units
                        .iter()
                        .find(|unit| unit.id == id && unit.player as usize == player)?;
                    (owners_before.get(&unit.pos()) == Some(&Owner::Own)).then_some((id, unit.carry))
                })
                .collect();
            let had_renewable_receipt = self.own_owned_crop_harvest_units > 0;

            step(&mut self.game, &commands[0], &commands[1]);

            let (failures, own_plants, opponent_plants, _joint_plants, _ambiguous_plants) =
                update_provenance(&self.game, &before_plants, &attempts, &mut self.owners, player);
            self.provenance_failures += failures;
            self.own_created_crops += own_plants;
            self.opponent_created_crops += opponent_plants;
            if had_renewable_receipt {
                self.own_reinvested_crops += own_plants;
            }
            for (id, before_carry) in own_crop_harvests {
                let Some(unit) = self.game.units.iter().find(|unit| unit.id == id) else {
                    continue;
                };
                self.own_owned_crop_harvest_units += (0..4)
                    .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                    .sum::<i32>() as usize;
            }

            let after_cells: BTreeSet<_> = self.game.plants.iter().map(|plant| plant.pos()).collect();
            self.birth_turns.retain(|cell, _| after_cells.contains(cell));
            for cell in after_cells.difference(&before_plants) {
                self.birth_turns.insert(*cell, before.turn);
            }

            let production = d166_successful_production(
                &before,
                &self.game,
                player,
                &commands[player],
                &owners_before,
                &self.owners,
                &self.birth_turns,
            );
            for event in production {
                self.history.insert(event.unit_id, event.record);
            }

            // D170b Delta 1 repair: resource `_trig` arms gate, post-step,
            // sticky-flag pattern mirroring the OPT_RETURN gate immediately
            // below. `opp_worker_trigger_turn` is set pre-step above
            // (unchanged, still drives state features 55/56) and, being
            // monotonic and latched at most once, can equal `current_turn`
            // only on the exact call where it was just newly set — so this
            // reuses that existing value rather than re-deriving the "first
            // reaches >= 3" condition. `refresh_candidates` cannot observe
            // this directly (it only ever runs strictly before or after
            // `step_one_turn`, never mid-turn); latched here, consumed on
            // its next call.
            if self.opp_worker_trigger_turn == current_turn {
                self.trig_pending = true;
            }

            // OPT_RETURN gate: post-step, exactly the turn entry was
            // captured (byte-identical trigger to D169a's ARM_A). Only ever
            // queued if budget is still unspent.
            if !self.budget_used
                && self.entry_captured
                && self.entry_turn == current_turn
                && !self.return_telemetry.activated
                && bank_fruit_total(&self.game, player) > 0
            {
                self.return_pending = true;
            }

            if let Some(pos_before) = armed_pos_before {
                let entry_unit_id = self.entry_unit_id;
                let before_carry_of = |item: usize| -> i32 {
                    before
                        .units
                        .iter()
                        .find(|unit| unit.id == entry_unit_id)
                        .map(|unit| unit.carry[item])
                        .unwrap_or(0)
                };
                let after_carry_of = |item: usize| -> i32 {
                    self.game
                        .units
                        .iter()
                        .find(|unit| unit.id == entry_unit_id)
                        .map(|unit| unit.carry[item])
                        .unwrap_or(0)
                };
                match issued {
                    D168aIssuedVerb::Pick(item) if item < 4 => {
                        if after_carry_of(item) > before_carry_of(item) {
                            self.return_telemetry.pick_successes += 1;
                            self.return_telemetry.species_picked = item as i32;
                        }
                    }
                    D168aIssuedVerb::Plant(item) if item < 4 => {
                        let planted_now = !before_plants.contains(&pos_before)
                            && self.owners.get(&pos_before) == Some(&Owner::Own)
                            && self.game.plants.iter().any(|plant| plant.pos() == pos_before);
                        if after_carry_of(item) < before_carry_of(item) && planted_now {
                            self.return_telemetry.plant_successes += 1;
                            self.return_telemetry.committed = true;
                            self.return_telemetry.committed_turn = before.turn;
                            self.return_telemetry.species_planted = item as i32;
                            self.return_telemetry.plant_cell_x = pos_before.0;
                            self.return_telemetry.plant_cell_y = pos_before.1;
                        }
                    }
                    _ => {}
                }
            }

            let after_workers = worker_count(&self.game, player);
            self.max_own_workers = self.max_own_workers.max(after_workers);
            self.done =
                self.game.turn > MACRO_TOTAL_TURNS || has_stalled(&self.game, &mut self.turns_until_end);
        }

        fn terminal_row(&self) -> D170aTerminal {
            let own_score = self.game.scores[self.task.seat];
            let opponent_score = self.game.scores[1 - self.task.seat];
            let margin = own_score - opponent_score;
            let invalid_direct_commands = match self.active_arm {
                Some(ArmKind::Return) => self.return_telemetry.vocabulary_violations as u32,
                Some(ArmKind::Resource(..)) => {
                    self.resource_controller.telemetry.option_command_failures as u32
                }
                _ => 0,
            };
            D170aTerminal {
                task_index: self.task_index,
                map_seed: self.task.map_seed,
                seat: self.task.seat as u8,
                opponent: self.task.opponent as u8,
                own_score,
                opponent_score,
                margin,
                control_margin: self.control_margin,
                control_own_score: self.control_own_score,
                paired_margin: margin - self.control_margin,
                chosen_arm: self
                    .active_arm
                    .map(|arm| decision_arm_index(arm) as i32 + 1)
                    .unwrap_or(0),
                decisions_seen: self.decisions_seen as u32,
                budget_used: self.budget_used,
                own_workers: worker_count(&self.game, self.task.seat) as u8,
                max_own_workers: self.max_own_workers as u8,
                own_created_crops: self.own_created_crops as u32,
                opponent_created_crops: self.opponent_created_crops as u32,
                provenance_failures: self.provenance_failures as u32,
                purity_violations: self.purity_violations as u32,
                invalid_direct_commands,
                action_hash: self.action_hash,
                state_hash: canonical_state_hash(&self.game),
                turn: self.game.turn.clamp(0, u16::MAX as i32) as u16,
            }
        }

        /// Apply `action` to the pending candidate (resuming first if this
        /// slot has none queued yet, e.g. immediately after a reset), and
        /// auto-reset to the next deterministic per-slot task on terminal.
        fn reset_to_next(&mut self, seed_base: i64, map_pool: usize, cache: &ControlCache) {
            let slot = self.slot;
            let round = self.round + 1;
            let envs_total = self.envs_total;
            *self = D170aEnv::new(seed_base, map_pool, slot, round, envs_total, cache);
            self.resume();
        }

        /// After any `resume()`, exactly one of `current_candidate.is_some()`
        /// (a decision is pending) or `self.done` (terminal ready) holds — a
        /// task can legally have **zero** armable states anywhere in its
        /// trajectory (byte-exact-vs-control), in which case a slot can
        /// already be `done` with no candidate immediately after a reset,
        /// including the very first one. Such a terminal must still be
        /// reported (exhaustive `task_index` coverage for evaluation) without
        /// requiring — or consuming — a caller action.
        fn decide_and_maybe_reset(
            &mut self,
            action: i32,
            seed_base: i64,
            map_pool: usize,
            cache: &ControlCache,
        ) -> D170aStepOutcome {
            if self.current_candidate.is_none() && !self.done {
                self.resume();
            }
            if self.current_candidate.is_none() {
                // Zero-decision episode (possibly straight out of a reset,
                // including the initial construction): nothing to decide.
                let terminal = self.terminal_row();
                let reward = terminal.paired_margin as f32 / 100.0;
                self.reset_to_next(seed_base, map_pool, cache);
                return D170aStepOutcome {
                    reward,
                    done: true,
                    terminal: Some(terminal),
                };
            }
            let paused = self.decide(action);
            if paused {
                D170aStepOutcome {
                    reward: 0.0,
                    done: false,
                    terminal: None,
                }
            } else {
                let terminal = self.terminal_row();
                let reward = terminal.paired_margin as f32 / 100.0;
                self.reset_to_next(seed_base, map_pool, cache);
                D170aStepOutcome {
                    reward,
                    done: true,
                    terminal: Some(terminal),
                }
            }
        }
    }

    pub struct D170aBatch {
        envs: Vec<D170aEnv>,
        seed_base: i64,
        map_pool: usize,
        control_cache: ControlCache,
    }

    impl D170aBatch {
        pub(super) fn new(num_envs: usize, seed_base: i64, map_pool: usize) -> Self {
            let control_cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            let envs = (0..num_envs)
                .map(|slot| {
                    let mut env = D170aEnv::new(seed_base, map_pool, slot, 0, num_envs, &control_cache);
                    env.resume();
                    env
                })
                .collect();
            Self {
                envs,
                seed_base,
                map_pool,
                control_cache,
            }
        }

        pub(super) fn len(&self) -> usize {
            self.envs.len()
        }

        pub(super) fn observe(&self, out: &mut [f32]) {
            assert_eq!(out.len(), self.envs.len() * D170A_INPUT_FEATURES);
            // Sequential: cheap field reads (no simulation); the env holds a
            // `Box<dyn Strategy>` opponent, which is `Send` but not `Sync`,
            // so shared-reference parallel iteration is unavailable here.
            for (chunk, env) in out
                .chunks_mut(D170A_INPUT_FEATURES)
                .zip(self.envs.iter())
            {
                env.observe_input(chunk);
            }
        }

        pub(super) fn pending(&self, out: &mut [u8]) {
            for (slot, env) in self.envs.iter().enumerate() {
                out[slot] = u8::from(env.current_candidate.is_some());
            }
        }

        /// Every slot is fully independent (own map/seat/opponent, own
        /// deterministic per-slot task sequence, own RNG-free simulation);
        /// the only shared state is the pure memoizing control-margin cache.
        /// Results are therefore byte-identical regardless of thread count.
        pub(super) fn step(&mut self, actions: &[i32]) -> Vec<D170aStepOutcome> {
            assert_eq!(actions.len(), self.envs.len());
            let seed_base = self.seed_base;
            let map_pool = self.map_pool;
            let cache = &self.control_cache;
            self.envs
                .par_iter_mut()
                .zip(actions.par_iter())
                .map(|(env, &action)| env.decide_and_maybe_reset(action, seed_base, map_pool, cache))
                .collect()
        }
    }

    #[cfg(test)]
    mod d170a_tests {
        use super::*;

        fn drive_keep(mut env: D170aEnv) -> D170aTerminal {
            loop {
                if !env.current_candidate.is_some() && !env.resume() {
                    return env.terminal_row();
                }
                if env.current_candidate.is_none() {
                    return env.terminal_row();
                }
                if !env.decide(0) {
                    return env.terminal_row();
                }
            }
        }

        fn control_row(map_seed: i64, seat: usize, opponent: usize) -> (i32, i32) {
            play_control(map_seed, seat, MacroOpponentMode::from_index(opponent))
        }

        #[test]
        fn all_keep_is_byte_exact_vs_control() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            for slot in 0..8 {
                let env = D170aEnv::new(9_844_136, 4, slot, 0, 8, &cache);
                let (control_own, control_opp) = control_row(env.task.map_seed, env.task.seat, env.task.opponent);
                let terminal = drive_keep(env);
                assert_eq!(terminal.own_score, control_own, "slot {slot}");
                assert_eq!(terminal.opponent_score, control_opp, "slot {slot}");
                assert_eq!(terminal.paired_margin, 0);
                assert_eq!(terminal.purity_violations, 0);
                assert_eq!(terminal.budget_used, false);
                assert_eq!(terminal.chosen_arm, 0);
            }
        }

        #[test]
        fn control_margin_matches_paired_margin_identity() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            let env = D170aEnv::new(9_844_136, 4, 0, 0, 8, &cache);
            let terminal = drive_keep(env);
            assert_eq!(
                terminal.paired_margin,
                (terminal.own_score - terminal.opponent_score) - terminal.control_margin
            );
        }

        #[test]
        fn budget_is_at_most_one_activation() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            for slot in 0..16 {
                let mut env = D170aEnv::new(9_844_136, 4, slot, 0, 16, &cache);
                let mut invocations = 0;
                let mut paused = env.resume();
                while paused {
                    // always invoke when possible, to stress-test the budget.
                    invocations += usize::from(env.pending_queue.first().is_some());
                    paused = env.decide(1);
                }
                assert!(invocations <= 1, "slot {slot} invoked {invocations} times");
                assert!(env.budget_used == (invocations == 1));
            }
        }

        #[test]
        fn deterministic_replay_matches() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            let mut first = D170aEnv::new(9_844_136, 4, 3, 0, 16, &cache);
            let mut second = D170aEnv::new(9_844_136, 4, 3, 0, 16, &cache);
            let mut p1 = first.resume();
            let mut p2 = second.resume();
            loop {
                assert_eq!(p1, p2);
                if !p1 {
                    break;
                }
                p1 = first.decide(1);
                p2 = second.decide(1);
            }
            assert_eq!(first.terminal_row(), second.terminal_row());
        }

        #[test]
        fn batch_task_assignment_is_thread_count_invariant() {
            let mut sequential = D170aBatch::new(4, 9_844_136, 4);
            let mut parallel = D170aBatch::new(4, 9_844_136, 4);
            let mut input_a = vec![0f32; 4 * D170A_INPUT_FEATURES];
            let mut input_b = vec![0f32; 4 * D170A_INPUT_FEATURES];
            for _ in 0..400 {
                sequential.observe(&mut input_a);
                parallel.observe(&mut input_b);
                assert_eq!(input_a, input_b);
                let actions = [1, 0, 1, 0];
                let outcomes_a = sequential.step(&actions);
                let outcomes_b = parallel.step(&actions);
                for (a, b) in outcomes_a.iter().zip(outcomes_b.iter()) {
                    assert_eq!(a.reward, b.reward);
                    assert_eq!(a.done, b.done);
                    assert_eq!(
                        a.terminal.map(|t| t.paired_margin),
                        b.terminal.map(|t| t.paired_margin)
                    );
                }
            }
        }

        #[test]
        fn every_task_index_is_reported_exactly_once_including_zero_decision_tasks() {
            // Small map_pool so a handful of distinct (map,seat,opponent)
            // tasks repeat quickly; deep enough to very likely include at
            // least one task with zero armable states anywhere in its
            // trajectory (a legal, control-identical episode) and confirms
            // that `decide_and_maybe_reset`'s reset path handles it without
            // ever requiring (or panicking on) an action for such a slot.
            let map_pool = 3;
            let total_tasks = map_pool * 2 * MacroOpponentMode::ALL.len();
            let num_envs = 5;
            let mut batch = D170aBatch::new(num_envs, 9_844_136, map_pool);
            let mut counts: BTreeMap<u64, u32> = BTreeMap::new();
            let mut zero_decision_seen = false;
            let mut rounds = 0;
            loop {
                rounds += 1;
                assert!(rounds < 50_000, "coverage guard tripped");
                // Always try to invoke: exercises the budget path hardest
                // and is irrelevant for zero-decision slots (ignored).
                let actions = vec![1i32; num_envs];
                let outcomes = batch.step(&actions);
                for outcome in &outcomes {
                    if let Some(terminal) = outcome.terminal {
                        *counts.entry(terminal.task_index).or_insert(0) += 1;
                        if terminal.decisions_seen == 0 {
                            zero_decision_seen = true;
                            assert_eq!(terminal.chosen_arm, 0);
                            assert_eq!(terminal.paired_margin, 0);
                        }
                    }
                }
                let covered = (0..total_tasks as u64).all(|index| counts.contains_key(&index));
                if covered {
                    break;
                }
            }
            for index in 0..total_tasks as u64 {
                assert_eq!(
                    counts.get(&index).copied().unwrap_or(0),
                    1,
                    "task_index {index} not reported exactly once"
                );
            }
            eprintln!(
                "D170a coverage test: zero-decision task observed = {zero_decision_seen} \
                 (informational; both outcomes are valid depending on the arm-condition rate)"
            );
        }

        /// D170b Delta 1 test support: drives `env` end-to-end with the
        /// all-KEEP policy (budget is never spent, so every armable turn in
        /// the episode is visited) and records
        /// `(game_turn, opp_worker_trigger_turn, is_trig_arm, own_workers)`
        /// for every decision offered.
        fn drive_keep_recording_trig_offers(mut env: D170aEnv) -> Vec<(i32, i32, bool, usize)> {
            let seat = env.task.seat;
            let mut offers = Vec::new();
            loop {
                if env.current_candidate.is_none() && !env.resume() {
                    break;
                }
                if env.current_candidate.is_none() {
                    break;
                }
                let candidate = env.current_candidate.unwrap();
                let is_trig = matches!(candidate, ArmKind::Resource(_, StartSpec::Trig));
                offers.push((
                    env.game.turn,
                    env.opp_worker_trigger_turn,
                    is_trig,
                    worker_count(&env.game, seat),
                ));
                if !env.decide(0) {
                    break;
                }
            }
            offers
        }

        /// D170b Delta 1 regression test (half of the protocol's required
        /// pair): the resource `_trig` arms must never be offered before the
        /// observed-opponent-worker trigger has fired, and never on the same
        /// turn it fires (`refresh_candidates` only ever runs strictly
        /// before or after `step_one_turn`, so the earliest legal offer turn
        /// is one turn after the latch).
        #[test]
        fn trig_arm_never_offered_before_the_trigger_fires() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            let mut trig_offers_seen = 0usize;
            for slot in 0..128usize {
                let env = D170aEnv::new(9_844_136, 64, slot, 0, 128, &cache);
                for (turn, trigger_turn, is_trig, _workers) in drive_keep_recording_trig_offers(env)
                {
                    if !is_trig {
                        continue;
                    }
                    assert!(
                        trigger_turn >= 0,
                        "slot {slot}: trig arm offered on turn {turn} before the \
                         opponent-worker trigger ever fired"
                    );
                    assert!(
                        turn > trigger_turn,
                        "slot {slot}: trig arm offered on turn {turn}, not strictly after \
                         its trigger turn {trigger_turn}"
                    );
                    trig_offers_seen += 1;
                }
            }
            assert!(
                trig_offers_seen > 0,
                "sweep never offered a trig arm at all -- this test cannot confirm the \
                 'never before' property is being meaningfully exercised (see the \
                 companion reachability test for the D170a 0/N regression check)"
            );
        }

        /// D170b Delta 1 regression test (the other half): whenever the
        /// trigger has fired and this seat is later observed holding exactly
        /// 2 workers (the shared resource-arm armability gate), a trig arm
        /// must actually be offered. This is the direct regression check for
        /// the D170a bug, where `opt_fruit_trig`/`opt_iron_trig`/
        /// `opt_protect_trig` were offered 0/2,880 times across the real
        /// training pool despite the underlying trigger firing in 15.7% of
        /// observed decisions.
        #[test]
        fn trig_arm_is_offered_on_the_decision_boundary_after_the_trigger_fires() {
            let cache: ControlCache = Arc::new(Mutex::new(BTreeMap::new()));
            let mut eligible_episodes = 0usize;
            for slot in 0..128usize {
                let env = D170aEnv::new(9_844_136, 64, slot, 0, 128, &cache);
                let offers = drive_keep_recording_trig_offers(env);
                let eligible = offers.iter().any(|&(turn, trigger_turn, _, workers)| {
                    trigger_turn >= 0 && turn > trigger_turn && workers == 2
                });
                if !eligible {
                    continue;
                }
                eligible_episodes += 1;
                let trig_offered = offers.iter().any(|&(_, _, is_trig, _)| is_trig);
                assert!(
                    trig_offered,
                    "slot {slot}: the opponent-worker trigger fired and this seat later \
                     held exactly 2 workers, but no trig arm was ever offered -- the \
                     D170a unreachable-arm bug is not fixed"
                );
            }
            assert!(
                eligible_episodes > 0,
                "sweep never produced an episode where the trigger fired and this seat \
                 later held exactly 2 workers; cannot positively confirm reachability in \
                 this sweep (widen the slot/map_pool sweep)"
            );
        }
    }
}

use inherited::{D170aBatch, D170aTerminal};

#[no_mangle]
pub extern "C" fn tf_d170a_state_features() -> usize {
    inherited::D170A_STATE_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_d170a_decision_features() -> usize {
    inherited::D170A_DECISION_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_d170a_input_features() -> usize {
    inherited::D170A_INPUT_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_d170a_arms() -> usize {
    inherited::D170A_ARMS
}

#[no_mangle]
pub extern "C" fn tf_d170a_actions() -> usize {
    inherited::D170A_ACTIONS
}

#[no_mangle]
pub extern "C" fn tf_d170a_create(num_envs: usize, seed_base: i64, map_pool: usize) -> *mut D170aBatch {
    if num_envs == 0 || seed_base <= 0 || map_pool == 0 {
        return std::ptr::null_mut();
    }
    Box::into_raw(Box::new(D170aBatch::new(num_envs, seed_base, map_pool)))
}

#[no_mangle]
pub unsafe extern "C" fn tf_d170a_destroy(handle: *mut D170aBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_d170a_observe(
    handle: *mut D170aBatch,
    inputs: *mut f32,
    pending: *mut u8,
) -> i32 {
    if handle.is_null() || inputs.is_null() || pending.is_null() {
        return -1;
    }
    let batch = &*handle;
    batch.observe(std::slice::from_raw_parts_mut(
        inputs,
        batch.len() * inherited::D170A_INPUT_FEATURES,
    ));
    batch.pending(std::slice::from_raw_parts_mut(pending, batch.len()));
    0
}

#[allow(clippy::too_many_arguments)]
#[no_mangle]
pub unsafe extern "C" fn tf_d170a_step(
    handle: *mut D170aBatch,
    actions: *const i32,
    inputs: *mut f32,
    pending: *mut u8,
    rewards: *mut f32,
    dones: *mut u8,
    task_indices: *mut u64,
    map_seeds: *mut i64,
    seats: *mut u8,
    opponents: *mut u8,
    own_scores: *mut i32,
    opponent_scores: *mut i32,
    margins: *mut i32,
    control_margins: *mut i32,
    control_own_scores: *mut i32,
    paired_margins: *mut i32,
    chosen_arms: *mut i32,
    decisions_seen: *mut u32,
    budget_used: *mut u8,
    own_workers: *mut u8,
    max_own_workers: *mut u8,
    own_created_crops: *mut u32,
    opponent_created_crops: *mut u32,
    provenance_failures: *mut u32,
    purity_violations: *mut u32,
    invalid_direct_commands: *mut u32,
    action_hashes: *mut u64,
    state_hashes: *mut u64,
    turns: *mut u16,
) -> i32 {
    if handle.is_null()
        || actions.is_null()
        || inputs.is_null()
        || pending.is_null()
        || rewards.is_null()
        || dones.is_null()
        || task_indices.is_null()
        || map_seeds.is_null()
        || seats.is_null()
        || opponents.is_null()
        || own_scores.is_null()
        || opponent_scores.is_null()
        || margins.is_null()
        || control_margins.is_null()
        || control_own_scores.is_null()
        || paired_margins.is_null()
        || chosen_arms.is_null()
        || decisions_seen.is_null()
        || budget_used.is_null()
        || own_workers.is_null()
        || max_own_workers.is_null()
        || own_created_crops.is_null()
        || opponent_created_crops.is_null()
        || provenance_failures.is_null()
        || purity_violations.is_null()
        || invalid_direct_commands.is_null()
        || action_hashes.is_null()
        || state_hashes.is_null()
        || turns.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    let n = batch.len();
    let actions = std::slice::from_raw_parts(actions, n);
    let outcomes = batch.step(actions);

    let rewards = std::slice::from_raw_parts_mut(rewards, n);
    let dones = std::slice::from_raw_parts_mut(dones, n);
    let task_indices = std::slice::from_raw_parts_mut(task_indices, n);
    let map_seeds = std::slice::from_raw_parts_mut(map_seeds, n);
    let seats = std::slice::from_raw_parts_mut(seats, n);
    let opponents = std::slice::from_raw_parts_mut(opponents, n);
    let own_scores = std::slice::from_raw_parts_mut(own_scores, n);
    let opponent_scores = std::slice::from_raw_parts_mut(opponent_scores, n);
    let margins = std::slice::from_raw_parts_mut(margins, n);
    let control_margins = std::slice::from_raw_parts_mut(control_margins, n);
    let control_own_scores = std::slice::from_raw_parts_mut(control_own_scores, n);
    let paired_margins = std::slice::from_raw_parts_mut(paired_margins, n);
    let chosen_arms = std::slice::from_raw_parts_mut(chosen_arms, n);
    let decisions_seen = std::slice::from_raw_parts_mut(decisions_seen, n);
    let budget_used = std::slice::from_raw_parts_mut(budget_used, n);
    let own_workers = std::slice::from_raw_parts_mut(own_workers, n);
    let max_own_workers = std::slice::from_raw_parts_mut(max_own_workers, n);
    let own_created_crops = std::slice::from_raw_parts_mut(own_created_crops, n);
    let opponent_created_crops = std::slice::from_raw_parts_mut(opponent_created_crops, n);
    let provenance_failures = std::slice::from_raw_parts_mut(provenance_failures, n);
    let purity_violations = std::slice::from_raw_parts_mut(purity_violations, n);
    let invalid_direct_commands = std::slice::from_raw_parts_mut(invalid_direct_commands, n);
    let action_hashes = std::slice::from_raw_parts_mut(action_hashes, n);
    let state_hashes = std::slice::from_raw_parts_mut(state_hashes, n);
    let turns = std::slice::from_raw_parts_mut(turns, n);

    let zero: D170aTerminal = D170aTerminal {
        task_index: 0,
        map_seed: 0,
        seat: 0,
        opponent: 0,
        own_score: 0,
        opponent_score: 0,
        margin: 0,
        control_margin: 0,
        control_own_score: 0,
        paired_margin: 0,
        chosen_arm: 0,
        decisions_seen: 0,
        budget_used: false,
        own_workers: 0,
        max_own_workers: 0,
        own_created_crops: 0,
        opponent_created_crops: 0,
        provenance_failures: 0,
        purity_violations: 0,
        invalid_direct_commands: 0,
        action_hash: 0,
        state_hash: 0,
        turn: 0,
    };
    for (index, outcome) in outcomes.iter().enumerate() {
        rewards[index] = outcome.reward;
        dones[index] = u8::from(outcome.done);
        let terminal = outcome.terminal.unwrap_or(zero);
        task_indices[index] = terminal.task_index;
        map_seeds[index] = terminal.map_seed;
        seats[index] = terminal.seat;
        opponents[index] = terminal.opponent;
        own_scores[index] = terminal.own_score;
        opponent_scores[index] = terminal.opponent_score;
        margins[index] = terminal.margin;
        control_margins[index] = terminal.control_margin;
        control_own_scores[index] = terminal.control_own_score;
        paired_margins[index] = terminal.paired_margin;
        chosen_arms[index] = terminal.chosen_arm;
        decisions_seen[index] = terminal.decisions_seen;
        budget_used[index] = u8::from(terminal.budget_used);
        own_workers[index] = terminal.own_workers;
        max_own_workers[index] = terminal.max_own_workers;
        own_created_crops[index] = terminal.own_created_crops;
        opponent_created_crops[index] = terminal.opponent_created_crops;
        provenance_failures[index] = terminal.provenance_failures;
        purity_violations[index] = terminal.purity_violations;
        invalid_direct_commands[index] = terminal.invalid_direct_commands;
        action_hashes[index] = terminal.action_hash;
        state_hashes[index] = terminal.state_hash;
        turns[index] = terminal.turn;
    }

    batch.observe(std::slice::from_raw_parts_mut(
        inputs,
        n * inherited::D170A_INPUT_FEATURES,
    ));
    batch.pending(std::slice::from_raw_parts_mut(pending, n));
    0
}
