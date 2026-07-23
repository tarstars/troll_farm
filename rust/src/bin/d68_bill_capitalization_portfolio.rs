//! Run D68a's consumed bill-level, adversarial-capacity source portfolio gate.

use std::cmp::Reverse;
use std::collections::BTreeSet;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

use troll_farm::game::engine::{bfs_distances, training_cost, IRON};
use troll_farm::game::state::Cell;
use troll_farm::rl_macro::{
    macro_action, CompleteMacroEnv, MacroDecisionStage, MacroJobKind, MacroOpponentMode,
    MacroTerminal, MacroTrainGoal, PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
};

const SEEDS: [i64; 2] = [9_830_002, 9_830_014];
const FRUITS: [&str; 4] = ["plum", "lemon", "apple", "banana"];

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Policy {
    D40Control,
    BillPortfolio,
}

impl Policy {
    const ALL: [Self; 2] = [Self::D40Control, Self::BillPortfolio];

    fn label(self) -> &'static str {
        match self {
            Self::D40Control => "d40_control",
            Self::BillPortfolio => "bill_portfolio",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
}

#[derive(Clone, Copy, Debug)]
enum PortfolioAction {
    Close,
    Bank,
    Harvest {
        kind: usize,
        target: Cell,
    },
    Plant {
        kind: usize,
        deficit: i32,
        live: usize,
        threats: usize,
        additions: usize,
        target: usize,
    },
    D40,
}

#[derive(Clone, Debug)]
struct PortfolioTelemetry {
    prefix_seen: bool,
    prefix_turn: i32,
    prefix_state_hash: u64,
    prefix_action_hash: u64,
    prefix_bootstrap_mask: u8,
    prefix_bank: [i32; 6],
    prefix_carry: [i32; 6],
    prefix_ripe: [i32; 6],
    prefix_source_transactions: u16,
    missing_kind: usize,
    prefix_missing_bank: i32,
    max_missing_bank: i32,
    first_bill_affordable_turn: i32,
    first_worker_two_turn: i32,
    first_worker_three_turn: i32,
    max_workers: u8,
    portfolio_closed: bool,
    intervention_hash: u64,
    interventions: u16,
    source_transactions: u16,
    source_transactions_by_kind: [u16; 4],
    source_failures: u16,
    source_pick_commands: u16,
    source_plant_commands: u16,
    forced_bank_jobs: u16,
    forced_bank_deposits: u16,
    forced_bank_failures: u16,
    forced_harvest_jobs: u16,
    forced_harvest_jobs_by_kind: [u16; 4],
    forced_harvest_deposits: u16,
    forced_harvest_deposits_by_kind: [u16; 4],
    forced_harvest_units_by_kind: [i32; 4],
    forced_harvest_failures: u16,
    max_bank: [i32; 4],
    live_sources_peak: [u8; 4],
    target_sources_peak: [u8; 4],
    threat_peak: u8,
    formula_violations: u16,
    carry_before_plant_violations: u16,
    affordable_plant_violations: u16,
    harvest_target_violations: u16,
    interventions_after_worker_two: u16,
    finite_state_failures: u16,
}

impl PortfolioTelemetry {
    fn new(task: Task) -> Self {
        let missing_kind = missing_species(task.map_seed);
        Self {
            prefix_seen: false,
            prefix_turn: -1,
            prefix_state_hash: 0,
            prefix_action_hash: 0,
            prefix_bootstrap_mask: 0,
            prefix_bank: [0; 6],
            prefix_carry: [0; 6],
            prefix_ripe: [0; 6],
            prefix_source_transactions: 0,
            missing_kind,
            prefix_missing_bank: -1,
            max_missing_bank: -1,
            first_bill_affordable_turn: -1,
            first_worker_two_turn: -1,
            first_worker_three_turn: -1,
            max_workers: 1,
            portfolio_closed: false,
            intervention_hash: 0xcbf29ce484222325,
            interventions: 0,
            source_transactions: 0,
            source_transactions_by_kind: [0; 4],
            source_failures: 0,
            source_pick_commands: 0,
            source_plant_commands: 0,
            forced_bank_jobs: 0,
            forced_bank_deposits: 0,
            forced_bank_failures: 0,
            forced_harvest_jobs: 0,
            forced_harvest_jobs_by_kind: [0; 4],
            forced_harvest_deposits: 0,
            forced_harvest_deposits_by_kind: [0; 4],
            forced_harvest_units_by_kind: [0; 4],
            forced_harvest_failures: 0,
            max_bank: [0; 4],
            live_sources_peak: [0; 4],
            target_sources_peak: [0; 4],
            threat_peak: 0,
            formula_violations: 0,
            carry_before_plant_violations: 0,
            affordable_plant_violations: 0,
            harvest_target_violations: 0,
            interventions_after_worker_two: 0,
            finite_state_failures: 0,
        }
    }

    fn mix(&mut self, value: u64) {
        for byte in value.to_le_bytes() {
            self.intervention_hash ^= u64::from(byte);
            self.intervention_hash = self.intervention_hash.wrapping_mul(0x100000001b3);
        }
    }

    fn observe(&mut self, env: &CompleteMacroEnv) {
        let workers = own_worker_count(env);
        self.max_workers = self.max_workers.max(workers as u8);
        if self.first_worker_two_turn < 0 && workers >= 2 {
            self.first_worker_two_turn = env.state.turn;
        }
        if self.first_worker_three_turn < 0 && workers >= 3 {
            self.first_worker_three_turn = env.state.turn;
        }
        if self.prefix_seen {
            self.max_missing_bank = self
                .max_missing_bank
                .max(env.state.inventories[env.seat][self.missing_kind]);
        }
        for kind in 0..4 {
            self.max_bank[kind] = self.max_bank[kind].max(env.state.inventories[env.seat][kind]);
            self.live_sources_peak[kind] =
                self.live_sources_peak[kind].max(live_own_source_cells(env, kind).len() as u8);
        }
        if !env
            .state
            .inventories
            .iter()
            .flatten()
            .all(|value| value.abs() < 1_000_000)
        {
            self.finite_state_failures = self.finite_state_failures.saturating_add(1);
        }
    }

    fn record_intervention(&mut self, env: &CompleteMacroEnv, tag: u64, kind: usize) {
        self.interventions = self.interventions.saturating_add(1);
        self.interventions_after_worker_two = self
            .interventions_after_worker_two
            .saturating_add(u16::from(own_worker_count(env) >= 2));
        self.mix(env.state_hash());
        self.mix(env.state.turn as u64);
        self.mix(tag);
        self.mix(kind as u64);
    }
}

#[derive(Clone, Debug)]
struct Row {
    policy: Policy,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    telemetry: PortfolioTelemetry,
    terminal_live_own_plants: usize,
    terminal_live_portfolio_sources: [usize; 4],
    terminal_bank: [i32; 6],
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn own_worker_count(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
}

fn live_own_plants(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn fruit_index(name: &str) -> usize {
    match name {
        "PLUM" => 0,
        "LEMON" => 1,
        "APPLE" => 2,
        "BANANA" => 3,
        other => panic!("unknown D68 fruit {other}"),
    }
}

fn fruit_label(kind: usize) -> &'static str {
    FRUITS[kind]
}

fn missing_species(map_seed: i64) -> usize {
    match map_seed {
        9_830_002 => 1,
        9_830_014 => 0,
        other => panic!("unexpected D68 seed {other}"),
    }
}

fn producer_cost(env: &CompleteMacroEnv) -> [i32; 6] {
    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().expect("producer spec"));
    if env.state.iron.is_empty() {
        cost[IRON] = 0;
    }
    cost
}

fn stock(env: &CompleteMacroEnv) -> ([i32; 6], [i32; 6], [i32; 6]) {
    let bank = env.state.inventories[env.seat];
    let mut carry = [0i32; 6];
    let mut ripe = [0i32; 6];
    for unit in env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
    {
        for (total, amount) in carry.iter_mut().zip(unit.carry) {
            *total = total.saturating_add(amount);
        }
    }
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        ripe[fruit_index(&plant.plant_type)] =
            ripe[fruit_index(&plant.plant_type)].saturating_add(plant.fruits);
    }
    (bank, carry, ripe)
}

/// Exact D65 setup rule, retained only until the D67 root is reached.
fn d65_source_kind(env: &CompleteMacroEnv, bootstrapped: u8) -> Option<usize> {
    if env.stage() != MacroDecisionStage::Train
        || env.train_goal() != MacroTrainGoal::Producer
        || own_worker_count(env) != 1
    {
        return None;
    }
    let cost = producer_cost(env);
    let (bank, carry, ripe) = stock(env);
    if (0..6).all(|index| bank[index] >= cost[index]) {
        return None;
    }
    let deficit = std::array::from_fn::<_, 6, _>(|index| {
        (cost[index] - bank[index] - carry[index] - ripe[index]).max(0)
    });
    (0..4)
        .filter(|kind| deficit[*kind] > 0 && bank[*kind] > 0 && bootstrapped & (1u8 << *kind) == 0)
        .max_by_key(|kind| (deficit[*kind], Reverse(*kind)))
}

fn live_own_source_cells(env: &CompleteMacroEnv, kind: usize) -> Vec<Cell> {
    let mut cells: Vec<_> = env
        .state
        .plants
        .iter()
        .filter(|plant| {
            plant.health > 0
                && fruit_index(&plant.plant_type) == kind
                && env.owners().get(&plant.pos()) == Some(&PlantOwner::Own)
        })
        .map(|plant| plant.pos())
        .collect();
    cells.sort_unstable();
    cells
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn shack_doors(env: &CompleteMacroEnv, player: usize) -> Vec<Cell> {
    let (x, y) = env.state.shacks[player];
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        .into_iter()
        .filter(|cell| env.state.walkable.contains(cell))
        .collect()
}

fn d65_admissible_cells(env: &CompleteMacroEnv) -> Vec<Cell> {
    let Some(unit) = env
        .state
        .units
        .iter()
        .find(|unit| unit.player as usize == env.seat)
    else {
        return Vec::new();
    };
    let from_distance = bfs_distances(&env.state.walkable, &[unit.pos()]);
    let own_distance = bfs_distances(&env.state.walkable, &shack_doors(env, env.seat));
    let opponent_distance = bfs_distances(&env.state.walkable, &shack_doors(env, 1 - env.seat));
    let mut cells: Vec<_> = env
        .state
        .walkable
        .iter()
        .copied()
        .filter(|cell| manhattan(*cell, env.state.shacks[env.seat]) <= 4)
        .filter(|cell| !env.state.plants.iter().any(|plant| plant.pos() == *cell))
        .filter(|cell| !env.state.units.iter().any(|other| other.pos() == *cell))
        .filter(|cell| from_distance.contains_key(cell))
        .filter(|cell| {
            own_distance.get(cell).copied().unwrap_or(10_000)
                < opponent_distance.get(cell).copied().unwrap_or(10_000)
        })
        .collect();
    cells.sort_unstable();
    cells
}

fn hostile_capacity(env: &CompleteMacroEnv) -> usize {
    let mut targets: BTreeSet<_> = d65_admissible_cells(env).into_iter().collect();
    for kind in 0..4 {
        targets.extend(live_own_source_cells(env, kind));
    }
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize != env.seat && unit.chop > 0)
        .filter(|unit| {
            let distances = bfs_distances(&env.state.walkable, &[unit.pos()]);
            targets.iter().any(|target| distances.contains_key(target))
        })
        .count()
}

fn bill_resources_sufficient(env: &CompleteMacroEnv) -> bool {
    let cost = producer_cost(env);
    let bank = env.state.inventories[env.seat];
    (0..6).all(|index| bank[index] >= cost[index])
}

fn carried_training_currency(env: &CompleteMacroEnv) -> bool {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .any(|unit| {
            [0usize, 1, 2, IRON]
                .into_iter()
                .any(|kind| unit.carry[kind] > 0)
        })
}

fn ripe_own_missing_source(env: &CompleteMacroEnv, deficits: [i32; 6]) -> Option<(usize, Cell)> {
    let unit = env
        .state
        .units
        .iter()
        .find(|unit| unit.player as usize == env.seat)?;
    if unit.free() <= 0 || unit.hp <= 0 {
        return None;
    }
    let distances = bfs_distances(&env.state.walkable, &[unit.pos()]);
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0 && plant.fruits > 0)
        .filter_map(|plant| {
            let kind = fruit_index(&plant.plant_type);
            (kind < 4
                && deficits[kind] > 0
                && env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
            .then_some((kind, plant.pos(), distances.get(&plant.pos()).copied()?))
        })
        .min_by_key(|(_, cell, distance)| (*distance, *cell))
        .map(|(kind, cell, _)| (kind, cell))
}

fn required_additions(live: usize, threats: usize, deficit: i32) -> usize {
    assert!(deficit > 0);
    (0..=128)
        .find(|additional| {
            3 * (live + *additional).saturating_sub(threats) as i32 - *additional as i32 >= deficit
        })
        .expect("D68 portfolio formula must converge")
}

fn portfolio_action(env: &CompleteMacroEnv) -> PortfolioAction {
    if env.stage() != MacroDecisionStage::Train
        || env.train_goal() != MacroTrainGoal::Producer
        || own_worker_count(env) != 1
    {
        return PortfolioAction::D40;
    }
    if bill_resources_sufficient(env) {
        return PortfolioAction::Close;
    }
    if carried_training_currency(env) {
        return PortfolioAction::Bank;
    }
    let cost = producer_cost(env);
    let bank = env.state.inventories[env.seat];
    let mut carry = [0i32; 6];
    for unit in env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
    {
        for (total, amount) in carry.iter_mut().zip(unit.carry) {
            *total = total.saturating_add(amount);
        }
    }
    let deficits =
        std::array::from_fn::<_, 6, _>(|index| (cost[index] - bank[index] - carry[index]).max(0));
    if let Some((kind, target)) = ripe_own_missing_source(env, deficits) {
        return PortfolioAction::Harvest { kind, target };
    }
    let threats = hostile_capacity(env);
    (0..4)
        .filter_map(|kind| {
            let deficit = deficits[kind];
            if deficit <= 0 || bank[kind] <= 0 {
                return None;
            }
            let live = live_own_source_cells(env, kind).len();
            let additions = required_additions(live, threats, deficit);
            (additions > 0).then_some((kind, deficit, live, additions))
        })
        .max_by_key(|(kind, deficit, _, _)| (*deficit, Reverse(*kind)))
        .map_or(PortfolioAction::D40, |(kind, deficit, live, additions)| {
            PortfolioAction::Plant {
                kind,
                deficit,
                live,
                threats,
                additions,
                target: live + additions,
            }
        })
}

fn force_worker_job(
    env: &mut CompleteMacroEnv,
    kind: MacroJobKind,
    target: Cell,
    action_planes: &mut [u32; MACRO_ACTION_PLANES],
) -> MacroTerminal {
    assert_eq!(env.stage(), MacroDecisionStage::Train);
    let train_action = macro_action(
        MacroTrainGoal::Producer.action_plane(),
        env.state.shacks[env.seat],
    );
    assert!(env.legal_actions().contains(&train_action));
    action_planes[MacroTrainGoal::Producer.action_plane()] =
        action_planes[MacroTrainGoal::Producer.action_plane()].saturating_add(1);
    let train_terminal = env.step(train_action);
    assert!(!train_terminal.done, "D68 forced job ended at TRAIN choice");
    assert_eq!(env.stage(), MacroDecisionStage::Worker);
    let action = macro_action(kind.action_plane(), target);
    assert!(
        env.legal_actions().contains(&action),
        "D68 forced {} action missing at {:?}",
        kind.label(),
        target
    );
    action_planes[kind.action_plane()] = action_planes[kind.action_plane()].saturating_add(1);
    env.step(action)
}

fn record_prefix(
    env: &CompleteMacroEnv,
    terminal: MacroTerminal,
    bootstrapped: u8,
    telemetry: &mut PortfolioTelemetry,
) {
    let (bank, carry, ripe) = stock(env);
    telemetry.prefix_seen = true;
    telemetry.prefix_turn = env.state.turn;
    telemetry.prefix_state_hash = env.state_hash();
    telemetry.prefix_action_hash = terminal.action_hash;
    telemetry.prefix_bootstrap_mask = bootstrapped;
    telemetry.prefix_bank = bank;
    telemetry.prefix_carry = carry;
    telemetry.prefix_ripe = ripe;
    telemetry.prefix_missing_bank = bank[telemetry.missing_kind];
    telemetry.max_missing_bank = bank[telemetry.missing_kind];
    for kind in 0..4 {
        telemetry.max_bank[kind] = telemetry.max_bank[kind].max(bank[kind]);
    }
}

fn play(task: Task, policy: Policy) -> Row {
    let mut env = CompleteMacroEnv::new(task.map_seed, task.seat, MacroOpponentMode::Resident);
    let mut terminal = MacroTerminal::default();
    let mut telemetry = PortfolioTelemetry::new(task);
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut bootstrapped = 0u8;
    let mut portfolio_started = false;
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;

    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 10_000, "D68 decision loop on {task:?}");

        if policy == Policy::BillPortfolio && !portfolio_started {
            if let Some(kind) = d65_source_kind(&env, bootstrapped) {
                if kind == telemetry.missing_kind {
                    record_prefix(&env, terminal, bootstrapped, &mut telemetry);
                    portfolio_started = true;
                } else {
                    let outcome = env
                        .install_bank_seed_source(kind)
                        .expect("D68 exact earlier D65 source");
                    bootstrapped |= 1u8 << kind;
                    telemetry.prefix_source_transactions =
                        telemetry.prefix_source_transactions.saturating_add(1);
                    action_planes[MacroJobKind::Renew.action_plane()] =
                        action_planes[MacroJobKind::Renew.action_plane()].saturating_add(1);
                    terminal = outcome.terminal;
                    telemetry.observe(&env);
                    if terminal.done {
                        break;
                    }
                    if env.state.turn == last_turn {
                        stagnant += 1;
                    } else {
                        last_turn = env.state.turn;
                        stagnant = 0;
                    }
                    assert!(stagnant <= 16, "D68 zero-time setup loop on {task:?}");
                    continue;
                }
            }
        }

        if policy == Policy::BillPortfolio && portfolio_started && !telemetry.portfolio_closed {
            match portfolio_action(&env) {
                PortfolioAction::Close => {
                    telemetry.portfolio_closed = true;
                    telemetry.first_bill_affordable_turn = env.state.turn;
                    telemetry.mix(env.state_hash());
                    telemetry.mix(env.state.turn as u64);
                    telemetry.mix(0);
                }
                PortfolioAction::Bank => {
                    telemetry.record_intervention(&env, 1, 6);
                    telemetry.forced_bank_jobs = telemetry.forced_bank_jobs.saturating_add(1);
                    let bank_before = env.state.inventories[env.seat];
                    let carry_before = env
                        .state
                        .units
                        .iter()
                        .find(|unit| unit.player as usize == env.seat)
                        .expect("D68 sole worker")
                        .carry;
                    let shack = env.state.shacks[env.seat];
                    terminal =
                        force_worker_job(&mut env, MacroJobKind::Bank, shack, &mut action_planes);
                    let deposited = (0..6).all(|kind| {
                        env.state.inventories[env.seat][kind]
                            == bank_before[kind] + carry_before[kind]
                    });
                    telemetry.forced_bank_deposits = telemetry
                        .forced_bank_deposits
                        .saturating_add(u16::from(deposited));
                    telemetry.forced_bank_failures = telemetry
                        .forced_bank_failures
                        .saturating_add(u16::from(!deposited));
                    telemetry.observe(&env);
                    if terminal.done {
                        break;
                    }
                    continue;
                }
                PortfolioAction::Harvest { kind, target } => {
                    let valid_target = env.state.plants.iter().any(|plant| {
                        plant.pos() == target
                            && plant.health > 0
                            && plant.fruits > 0
                            && fruit_index(&plant.plant_type) == kind
                    }) && env.owners().get(&target) == Some(&PlantOwner::Own);
                    telemetry.harvest_target_violations = telemetry
                        .harvest_target_violations
                        .saturating_add(u16::from(!valid_target));
                    telemetry.record_intervention(&env, 2, kind);
                    telemetry.mix(target.0 as u64);
                    telemetry.mix(target.1 as u64);
                    telemetry.forced_harvest_jobs = telemetry.forced_harvest_jobs.saturating_add(1);
                    telemetry.forced_harvest_jobs_by_kind[kind] =
                        telemetry.forced_harvest_jobs_by_kind[kind].saturating_add(1);
                    let bank_before = env.state.inventories[env.seat][kind];
                    let invalidated_before = terminal.invalidated_jobs;
                    terminal = force_worker_job(
                        &mut env,
                        MacroJobKind::HarvestBank,
                        target,
                        &mut action_planes,
                    );
                    let deposited = env.state.inventories[env.seat][kind] > bank_before;
                    let deposited_units =
                        (env.state.inventories[env.seat][kind] - bank_before).max(0);
                    telemetry.forced_harvest_deposits = telemetry
                        .forced_harvest_deposits
                        .saturating_add(u16::from(deposited));
                    telemetry.forced_harvest_deposits_by_kind[kind] = telemetry
                        .forced_harvest_deposits_by_kind[kind]
                        .saturating_add(u16::from(deposited));
                    telemetry.forced_harvest_units_by_kind[kind] = telemetry
                        .forced_harvest_units_by_kind[kind]
                        .saturating_add(deposited_units);
                    telemetry.forced_harvest_failures =
                        telemetry.forced_harvest_failures.saturating_add(u16::from(
                            !deposited || terminal.invalidated_jobs > invalidated_before,
                        ));
                    telemetry.observe(&env);
                    if terminal.done {
                        break;
                    }
                    continue;
                }
                PortfolioAction::Plant {
                    kind,
                    deficit,
                    live,
                    threats,
                    additions,
                    target,
                } => {
                    telemetry.carry_before_plant_violations = telemetry
                        .carry_before_plant_violations
                        .saturating_add(u16::from(carried_training_currency(&env)));
                    telemetry.affordable_plant_violations = telemetry
                        .affordable_plant_violations
                        .saturating_add(u16::from(bill_resources_sufficient(&env)));
                    let formula_ok = additions == required_additions(live, threats, deficit)
                        && additions > 0
                        && target == live + additions;
                    telemetry.formula_violations = telemetry
                        .formula_violations
                        .saturating_add(u16::from(!formula_ok));
                    telemetry.target_sources_peak[kind] =
                        telemetry.target_sources_peak[kind].max(target as u8);
                    telemetry.threat_peak = telemetry.threat_peak.max(threats as u8);
                    telemetry.record_intervention(&env, 3, kind);
                    telemetry.mix(deficit as u64);
                    telemetry.mix(live as u64);
                    telemetry.mix(threats as u64);
                    telemetry.mix(additions as u64);
                    telemetry.mix(target as u64);
                    match env.install_bank_seed_source(kind) {
                        Some(outcome) => {
                            telemetry.source_transactions =
                                telemetry.source_transactions.saturating_add(1);
                            telemetry.source_transactions_by_kind[kind] =
                                telemetry.source_transactions_by_kind[kind].saturating_add(1);
                            telemetry.source_pick_commands = telemetry
                                .source_pick_commands
                                .saturating_add(outcome.pick_commands);
                            telemetry.source_plant_commands = telemetry
                                .source_plant_commands
                                .saturating_add(outcome.plant_commands);
                            action_planes[MacroJobKind::Renew.action_plane()] =
                                action_planes[MacroJobKind::Renew.action_plane()].saturating_add(1);
                            terminal = outcome.terminal;
                        }
                        None => {
                            telemetry.source_failures = telemetry.source_failures.saturating_add(1);
                        }
                    }
                    telemetry.observe(&env);
                    if terminal.done {
                        break;
                    }
                    continue;
                }
                PortfolioAction::D40 => {}
            }
        }

        let observation = env.candidate_observation();
        let action = observation.actions[observation.teacher_index] as usize;
        assert!(env.legal_actions().contains(&action));
        action_planes[action / MACRO_CELLS] = action_planes[action / MACRO_CELLS].saturating_add(1);
        terminal = env.step(action);
        telemetry.observe(&env);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D68 zero-time loop on {task:?}");
    }

    if policy == Policy::BillPortfolio {
        assert!(
            telemetry.prefix_seen,
            "D68 missing frozen prefix on {task:?}"
        );
    }
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    let terminal_live_portfolio_sources =
        std::array::from_fn(|kind| live_own_source_cells(&env, kind).len());
    Row {
        policy,
        task,
        terminal,
        reward_identity_error,
        telemetry,
        terminal_live_own_plants: live_own_plants(&env),
        terminal_live_portfolio_sources,
        terminal_bank: env.state.inventories[env.seat],
        action_planes,
    }
}

fn vector_text(values: [i32; 6]) -> String {
    values
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        2,
        "usage: d68_bill_capitalization_portfolio OUTPUT"
    );
    let mut rows = Vec::new();
    for policy in Policy::ALL {
        for map_seed in SEEDS {
            for seat in 0..2 {
                rows.push(play(Task { map_seed, seat }, policy));
            }
        }
    }
    rows.sort_by_key(|row| (row.policy, row.task));
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&args[1])
        .expect("create D68 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\tprefix_seen\tprefix_turn\tprefix_state_hash\tprefix_action_hash\tprefix_bootstrap_mask\tprefix_bank\tprefix_carry\tprefix_ripe\tprefix_source_transactions\tmissing_species\tprefix_missing_bank\tmax_missing_bank\tmissing_bank_progress\tfirst_bill_affordable_turn\tportfolio_closed\tintervention_hash\tinterventions\tsource_transactions\tsource_transactions_plum\tsource_transactions_lemon\tsource_transactions_apple\tsource_transactions_banana\tsource_failures\tsource_pick_commands\tsource_plant_commands\tforced_bank_jobs\tforced_bank_deposits\tforced_bank_failures\tforced_harvest_jobs\tforced_harvest_jobs_plum\tforced_harvest_jobs_lemon\tforced_harvest_jobs_apple\tforced_harvest_jobs_banana\tforced_harvest_deposits\tforced_harvest_deposits_plum\tforced_harvest_deposits_lemon\tforced_harvest_deposits_apple\tforced_harvest_deposits_banana\tforced_harvest_units_plum\tforced_harvest_units_lemon\tforced_harvest_units_apple\tforced_harvest_units_banana\tforced_harvest_failures\tmax_bank_plum\tmax_bank_lemon\tmax_bank_apple\tmax_bank_banana\tlive_sources_peak_plum\tlive_sources_peak_lemon\tlive_sources_peak_apple\tlive_sources_peak_banana\ttarget_sources_peak_plum\ttarget_sources_peak_lemon\ttarget_sources_peak_apple\ttarget_sources_peak_banana\tthreat_peak\tformula_violations\tcarry_before_plant_violations\taffordable_plant_violations\tharvest_target_violations\tinterventions_after_worker_two\tfirst_worker_two_turn\tfirst_worker_three_turn\tmax_workers\tfinite_state_failures\tterminal_live_own_plants\tterminal_live_source_plum\tterminal_live_source_lemon\tterminal_live_source_apple\tterminal_live_source_banana\tterminal_bank\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D68 header");
    for row in rows {
        let terminal = row.terminal;
        let t = row.telemetry;
        let fields = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            "resident".to_string(),
            row.policy.label().to_string(),
            terminal.turn.to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            (terminal.own_score - terminal.opponent_score).to_string(),
            format!("{:.8}", terminal.own_return),
            format!("{:.8}", terminal.opponent_return),
            format!("{:.8}", terminal.margin_return),
            format!("{:.8}", row.reward_identity_error),
            terminal.own_workers.to_string(),
            terminal.opponent_workers.to_string(),
            terminal.successful_trains.to_string(),
            terminal.completed_jobs.to_string(),
            terminal.invalidated_jobs.to_string(),
            terminal.invalid_direct_commands.to_string(),
            terminal.provenance_failures.to_string(),
            terminal.deposit_prediction_failures.to_string(),
            terminal.selected_decisions.to_string(),
            terminal.selected_jobs.to_string(),
            terminal.selected_nonidle_jobs.to_string(),
            terminal.selected_renew_jobs.to_string(),
            terminal.own_created_crops.to_string(),
            terminal.opponent_created_crops.to_string(),
            terminal.ambiguous_created_crops.to_string(),
            terminal.action_hash.to_string(),
            terminal.state_hash.to_string(),
            u8::from(t.prefix_seen).to_string(),
            t.prefix_turn.to_string(),
            t.prefix_state_hash.to_string(),
            t.prefix_action_hash.to_string(),
            t.prefix_bootstrap_mask.to_string(),
            vector_text(t.prefix_bank),
            vector_text(t.prefix_carry),
            vector_text(t.prefix_ripe),
            t.prefix_source_transactions.to_string(),
            fruit_label(t.missing_kind).to_string(),
            t.prefix_missing_bank.to_string(),
            t.max_missing_bank.to_string(),
            (t.max_missing_bank - t.prefix_missing_bank).to_string(),
            t.first_bill_affordable_turn.to_string(),
            u8::from(t.portfolio_closed).to_string(),
            t.intervention_hash.to_string(),
            t.interventions.to_string(),
            t.source_transactions.to_string(),
            t.source_transactions_by_kind[0].to_string(),
            t.source_transactions_by_kind[1].to_string(),
            t.source_transactions_by_kind[2].to_string(),
            t.source_transactions_by_kind[3].to_string(),
            t.source_failures.to_string(),
            t.source_pick_commands.to_string(),
            t.source_plant_commands.to_string(),
            t.forced_bank_jobs.to_string(),
            t.forced_bank_deposits.to_string(),
            t.forced_bank_failures.to_string(),
            t.forced_harvest_jobs.to_string(),
            t.forced_harvest_jobs_by_kind[0].to_string(),
            t.forced_harvest_jobs_by_kind[1].to_string(),
            t.forced_harvest_jobs_by_kind[2].to_string(),
            t.forced_harvest_jobs_by_kind[3].to_string(),
            t.forced_harvest_deposits.to_string(),
            t.forced_harvest_deposits_by_kind[0].to_string(),
            t.forced_harvest_deposits_by_kind[1].to_string(),
            t.forced_harvest_deposits_by_kind[2].to_string(),
            t.forced_harvest_deposits_by_kind[3].to_string(),
            t.forced_harvest_units_by_kind[0].to_string(),
            t.forced_harvest_units_by_kind[1].to_string(),
            t.forced_harvest_units_by_kind[2].to_string(),
            t.forced_harvest_units_by_kind[3].to_string(),
            t.forced_harvest_failures.to_string(),
            t.max_bank[0].to_string(),
            t.max_bank[1].to_string(),
            t.max_bank[2].to_string(),
            t.max_bank[3].to_string(),
            t.live_sources_peak[0].to_string(),
            t.live_sources_peak[1].to_string(),
            t.live_sources_peak[2].to_string(),
            t.live_sources_peak[3].to_string(),
            t.target_sources_peak[0].to_string(),
            t.target_sources_peak[1].to_string(),
            t.target_sources_peak[2].to_string(),
            t.target_sources_peak[3].to_string(),
            t.threat_peak.to_string(),
            t.formula_violations.to_string(),
            t.carry_before_plant_violations.to_string(),
            t.affordable_plant_violations.to_string(),
            t.harvest_target_violations.to_string(),
            t.interventions_after_worker_two.to_string(),
            t.first_worker_two_turn.to_string(),
            t.first_worker_three_turn.to_string(),
            t.max_workers.to_string(),
            t.finite_state_failures.to_string(),
            row.terminal_live_own_plants.to_string(),
            row.terminal_live_portfolio_sources[0].to_string(),
            row.terminal_live_portfolio_sources[1].to_string(),
            row.terminal_live_portfolio_sources[2].to_string(),
            row.terminal_live_portfolio_sources[3].to_string(),
            vector_text(row.terminal_bank),
            row.action_planes[0].to_string(),
            row.action_planes[1].to_string(),
            row.action_planes[2].to_string(),
            row.action_planes[3].to_string(),
            row.action_planes[4].to_string(),
            row.action_planes[5].to_string(),
            row.action_planes[6].to_string(),
            row.action_planes[7].to_string(),
            row.action_planes[8].to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D68 row");
    }
    writer.flush().expect("flush D68 output");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn derived_portfolio_formula_has_expected_boundaries() {
        assert_eq!(required_additions(0, 1, 1), 2);
        assert_eq!(required_additions(0, 1, 2), 3);
        assert_eq!(required_additions(2, 1, 3), 0);
        assert_eq!(required_additions(1, 2, 1), 2);
    }

    #[test]
    fn consumed_treatment_reaches_exact_prefix() {
        for map_seed in SEEDS {
            for seat in 0..2 {
                let row = play(Task { map_seed, seat }, Policy::BillPortfolio);
                assert!(row.telemetry.prefix_seen);
                assert_eq!(row.telemetry.missing_kind, missing_species(map_seed));
                assert!(row.terminal.done);
            }
        }
    }
}
