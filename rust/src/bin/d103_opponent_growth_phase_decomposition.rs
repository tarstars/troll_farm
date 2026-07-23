//! D103a: decompose D40 opponent growth across scale and paired-resident horizons.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::resident_policy::bot::moisan::SecureOrchardBot;
use troll_farm::resident_policy::bot::Bot as ResidentBot;
use troll_farm::resident_policy::game::{
    GameState as ResidentState, Plant as ResidentPlant, PlantKind, Stats as ResidentStats,
    Unit as ResidentUnit,
};
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroOpponentMode, MacroTerminal, PlantOwner, MACRO_TOTAL_TURNS,
};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Policy {
    D40,
    Resident,
}

impl Policy {
    fn label(self) -> &'static str {
        match self {
            Self::D40 => "d40",
            Self::Resident => "resident",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Owner {
    Natural,
    Own,
    Opponent,
    Joint,
    Ambiguous,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct LiveCrops {
    own: usize,
    opponent: usize,
    joint: usize,
    ambiguous: usize,
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
struct Cumulative {
    successful_trains: usize,
    completed_jobs: usize,
    invalidated_jobs: usize,
    invalid_direct_commands: usize,
    provenance_failures: usize,
    deposit_prediction_failures: usize,
    own_created_crops: usize,
    opponent_created_crops: usize,
    joint_created_crops: usize,
    ambiguous_created_crops: usize,
    own_crop_harvest_units: usize,
    own_reinvested_crops: usize,
}

impl Cumulative {
    fn from_terminal(terminal: MacroTerminal) -> Self {
        Self {
            successful_trains: terminal.successful_trains as usize,
            completed_jobs: terminal.completed_jobs as usize,
            invalidated_jobs: terminal.invalidated_jobs as usize,
            invalid_direct_commands: terminal.invalid_direct_commands as usize,
            provenance_failures: terminal.provenance_failures as usize,
            deposit_prediction_failures: terminal.deposit_prediction_failures as usize,
            own_created_crops: terminal.own_created_crops as usize,
            opponent_created_crops: terminal.opponent_created_crops as usize,
            joint_created_crops: 0,
            ambiguous_created_crops: terminal.ambiguous_created_crops as usize,
            own_crop_harvest_units: terminal.own_owned_crop_harvest_units as usize,
            own_reinvested_crops: terminal.own_reinvested_crops as usize,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Snapshot {
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    own_workers: usize,
    opponent_workers: usize,
    live: LiveCrops,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Interval {
    task: Task,
    policy: Policy,
    interval_index: usize,
    start: Snapshot,
    end: Snapshot,
    own_crop_births: usize,
    opponent_crop_births: usize,
    joint_crop_births: usize,
    ambiguous_crop_births: usize,
    own_crop_removals: usize,
    opponent_crop_removals: usize,
    own_crop_harvest_units: usize,
    own_reinvested_crops: usize,
    cumulative: Cumulative,
    done: bool,
    action_hash: u64,
    state_hash: u64,
}

enum Opponent {
    Resident(SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => Self::Resident(SecureOrchardBot::new()),
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => Self::Local(Box::new(NorxondorNative::new(true))),
            MacroOpponentMode::LegendBalanced => Self::Local(Box::new(
                LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }),
            )),
            MacroOpponentMode::MyBot => Self::Local(Box::new(MyBot::new())),
            MacroOpponentMode::ScriptBoss => Self::Local(Box::new(ScriptBoss::new())),
            MacroOpponentMode::SilverBoss => Self::Local(Box::new(SilverBoss::new())),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&resident_view(game, player)),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn resident_view(game: &GameState, player: usize) -> ResidentState {
    let opponent = 1 - player;
    ResidentState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| ResidentUnit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: ResidentStats {
                    movement_speed: unit.ms,
                    carry_capacity: unit.cc,
                    harvest_power: unit.hp,
                    chop_power: unit.chop,
                },
                carry: unit.carry,
            })
            .collect(),
        plants: game
            .plants
            .iter()
            .map(|plant| ResidentPlant {
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect(),
        water: game.water.iter().copied().collect(),
    }
}

fn worker_count(game: &GameState, player: usize) -> usize {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count()
}

fn plant_attempts(game: &GameState, player: usize, commands: &[String]) -> BTreeSet<Cell> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            (fields.next()? == "PLANT").then_some(())?;
            let id = fields.next()?.parse::<i32>().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(|unit| unit.pos())
        })
        .collect()
}

fn command_unit_ids(commands: &[String], verb: &str) -> Vec<i32> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            (fields.next()? == verb).then_some(())?;
            fields.next()?.parse::<i32>().ok()
        })
        .collect()
}

fn fnv1a(mut hash: u64, bytes: &[u8]) -> u64 {
    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(1_099_511_628_211);
    }
    hash
}

fn hash_i32(hash: u64, value: i32) -> u64 {
    fnv1a(hash, &value.to_le_bytes())
}

fn canonical_state_hash(game: &GameState) -> u64 {
    let mut hash = 14_695_981_039_346_656_037_u64;
    for value in [game.width, game.height, game.turn, game.next_id] {
        hash = hash_i32(hash, value);
    }
    for cell in game.shacks {
        hash = hash_i32(hash, cell.0);
        hash = hash_i32(hash, cell.1);
    }
    for inventory in game.inventories {
        for value in inventory {
            hash = hash_i32(hash, value);
        }
    }
    for value in game.scores {
        hash = hash_i32(hash, value);
    }
    for cells in [&game.walkable, &game.iron, &game.water] {
        let mut cells: Vec<_> = cells.iter().copied().collect();
        cells.sort_unstable();
        hash = hash_i32(hash, cells.len() as i32);
        for cell in cells {
            hash = hash_i32(hash, cell.0);
            hash = hash_i32(hash, cell.1);
        }
    }
    let mut units: Vec<_> = game.units.iter().collect();
    units.sort_by_key(|unit| unit.id);
    hash = hash_i32(hash, units.len() as i32);
    for unit in units {
        for value in [
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ] {
            hash = hash_i32(hash, value);
        }
        for value in unit.carry {
            hash = hash_i32(hash, value);
        }
    }
    let mut plants: Vec<_> = game.plants.iter().collect();
    plants.sort_by_key(|plant| (plant.x, plant.y, plant.plant_type.as_str()));
    hash = hash_i32(hash, plants.len() as i32);
    for plant in plants {
        hash = fnv1a(hash, plant.plant_type.as_bytes());
        hash = fnv1a(hash, &[0]);
        for value in [
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ] {
            hash = hash_i32(hash, value);
        }
    }
    hash
}

fn live_resident(owners: &BTreeMap<Cell, Owner>) -> LiveCrops {
    let mut result = LiveCrops::default();
    for owner in owners.values() {
        match owner {
            Owner::Natural => {}
            Owner::Own => result.own += 1,
            Owner::Opponent => result.opponent += 1,
            Owner::Joint => result.joint += 1,
            Owner::Ambiguous => result.ambiguous += 1,
        }
    }
    result
}

fn live_d40(env: &CompleteMacroEnv) -> LiveCrops {
    let mut result = LiveCrops::default();
    for owner in env.owners().values() {
        match owner {
            PlantOwner::Natural => {}
            PlantOwner::Own => result.own += 1,
            PlantOwner::Opponent => result.opponent += 1,
            PlantOwner::Ambiguous => result.ambiguous += 1,
        }
    }
    result
}

fn snapshot_d40(env: &CompleteMacroEnv) -> Snapshot {
    Snapshot {
        turn: env.state.turn,
        own_score: env.state.scores[env.seat],
        opponent_score: env.state.scores[1 - env.seat],
        own_workers: worker_count(&env.state, env.seat),
        opponent_workers: worker_count(&env.state, 1 - env.seat),
        live: live_d40(env),
    }
}

fn snapshot_resident(game: &GameState, seat: usize, owners: &BTreeMap<Cell, Owner>) -> Snapshot {
    Snapshot {
        turn: game.turn,
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        own_workers: worker_count(game, seat),
        opponent_workers: worker_count(game, 1 - seat),
        live: live_resident(owners),
    }
}

fn delta(after: usize, before: usize, label: &str) -> usize {
    after
        .checked_sub(before)
        .unwrap_or_else(|| panic!("D103 cumulative {label} decreased: {before} -> {after}"))
}

fn interval(
    task: Task,
    policy: Policy,
    interval_index: usize,
    start: Snapshot,
    end: Snapshot,
    before: Cumulative,
    after: Cumulative,
    done: bool,
    action_hash: u64,
    state_hash: u64,
) -> Interval {
    assert!(end.turn > start.turn, "D103 interval must advance time");
    let own_births = delta(
        after.own_created_crops,
        before.own_created_crops,
        "own births",
    );
    let opponent_births = delta(
        after.opponent_created_crops,
        before.opponent_created_crops,
        "opponent births",
    );
    let joint_births = delta(
        after.joint_created_crops,
        before.joint_created_crops,
        "joint births",
    );
    let ambiguous_births = delta(
        after.ambiguous_created_crops,
        before.ambiguous_created_crops,
        "ambiguous births",
    );
    let own_removals = start
        .live
        .own
        .checked_add(own_births)
        .and_then(|stock| stock.checked_sub(end.live.own))
        .expect("D103 own-crop stock flow");
    let opponent_removals = start
        .live
        .opponent
        .checked_add(opponent_births)
        .and_then(|stock| stock.checked_sub(end.live.opponent))
        .expect("D103 opponent-crop stock flow");
    Interval {
        task,
        policy,
        interval_index,
        start,
        end,
        own_crop_births: own_births,
        opponent_crop_births: opponent_births,
        joint_crop_births: joint_births,
        ambiguous_crop_births: ambiguous_births,
        own_crop_removals: own_removals,
        opponent_crop_removals: opponent_removals,
        own_crop_harvest_units: delta(
            after.own_crop_harvest_units,
            before.own_crop_harvest_units,
            "own crop harvest",
        ),
        own_reinvested_crops: delta(
            after.own_reinvested_crops,
            before.own_reinvested_crops,
            "own reinvestment",
        ),
        cumulative: after,
        done,
        action_hash,
        state_hash,
    }
}

fn play_d40(task: Task) -> Vec<Interval> {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut rows: Vec<Interval> = Vec::new();
    let mut cumulative = Cumulative::default();
    let mut terminal = MacroTerminal::default();
    let mut decisions = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions < 5_000, "D103 D40 decision loop");
        let start = snapshot_d40(&env);
        let selected = env.work_conserving_deficit_heuristic_action();
        terminal = env.step(selected);
        let end = snapshot_d40(&env);
        let current = Cumulative::from_terminal(terminal);
        if end.turn > start.turn {
            rows.push(interval(
                task,
                Policy::D40,
                rows.len(),
                start,
                end,
                cumulative,
                current,
                terminal.done,
                terminal.action_hash,
                terminal.state_hash,
            ));
        }
        cumulative = current;
    }
    assert!(!rows.is_empty());
    assert!(rows.last().is_some_and(|row| row.done));

    let mut direct = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let direct_terminal = direct.run_work_conserving_deficit_heuristic();
    assert_eq!(terminal, direct_terminal, "D103 D40 direct API parity");
    rows
}

fn update_provenance(
    game: &GameState,
    before_plants: &BTreeSet<Cell>,
    attempts: &[BTreeSet<Cell>; 2],
    owners: &mut BTreeMap<Cell, Owner>,
    seat: usize,
) -> (usize, usize, usize, usize, usize) {
    let after_plants: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    owners.retain(|cell, _| after_plants.contains(cell));
    let mut failures = 0usize;
    let mut own = 0usize;
    let mut opponent = 0usize;
    let mut joint = 0usize;
    let ambiguous = 0usize;
    for cell in after_plants.difference(before_plants) {
        let claimants: Vec<_> = (0..2)
            .filter(|player| attempts[*player].contains(cell))
            .collect();
        let owner = match claimants.as_slice() {
            [player] if *player == seat => {
                own += 1;
                Owner::Own
            }
            [player] if *player == 1 - seat => {
                opponent += 1;
                Owner::Opponent
            }
            [_, _] => {
                joint += 1;
                Owner::Joint
            }
            _ => {
                failures += 1;
                Owner::Ambiguous
            }
        };
        owners.insert(*cell, owner);
    }
    failures += owners
        .keys()
        .copied()
        .collect::<BTreeSet<_>>()
        .symmetric_difference(&after_plants)
        .count();
    (failures, own, opponent, joint, ambiguous)
}

fn play_resident(task: Task) -> Vec<Interval> {
    let mut game = generate_official(task.map_seed);
    let mut ours = SecureOrchardBot::new();
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(task.opponent));
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), Owner::Natural))
        .collect();
    let mut turns_until_end = 0i32;
    let mut action_hash = 14_695_981_039_346_656_037_u64;
    let mut cumulative = Cumulative::default();
    let mut rows = Vec::new();
    let mut done = false;

    while !done {
        let before_cumulative = cumulative;
        let start = snapshot_resident(&game, task.seat, &owners);
        let ours_commands = ours.commands(&resident_view(&game, task.seat));
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
        let had_renewable_receipt = cumulative.own_crop_harvest_units > 0;

        step(&mut game, &commands[0], &commands[1]);
        let (failures, own_plants, opponent_plants, joint_plants, ambiguous_plants) =
            update_provenance(&game, &before_plants, &attempts, &mut owners, task.seat);
        cumulative.provenance_failures += failures;
        cumulative.own_created_crops += own_plants;
        cumulative.opponent_created_crops += opponent_plants;
        cumulative.joint_created_crops += joint_plants;
        cumulative.ambiguous_created_crops += ambiguous_plants;
        if had_renewable_receipt {
            cumulative.own_reinvested_crops += own_plants;
        }
        for (id, before_carry) in own_crop_harvests {
            let Some(unit) = game.units.iter().find(|unit| unit.id == id) else {
                continue;
            };
            let gained = (0..4)
                .map(|kind| (unit.carry[kind] - before_carry[kind]).max(0))
                .sum::<i32>();
            cumulative.own_crop_harvest_units += gained.max(0) as usize;
        }
        let after_workers = worker_count(&game, task.seat);
        cumulative.successful_trains += after_workers.saturating_sub(before_workers);
        done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
        let end = snapshot_resident(&game, task.seat, &owners);
        rows.push(interval(
            task,
            Policy::Resident,
            rows.len(),
            start,
            end,
            before_cumulative,
            cumulative,
            done,
            action_hash,
            canonical_state_hash(&game),
        ));
    }
    assert!(!rows.is_empty());
    assert!(rows.last().is_some_and(|row| row.done));
    rows
}

fn play(task: Task) -> Vec<Interval> {
    let mut rows = play_d40(task);
    rows.extend(play_resident(task));
    rows
}

fn write_rows(output: &str, rows: &[Interval]) {
    let mut writer = BufWriter::new(File::create(output).expect("create D103a output"));
    writeln!(writer, "map_seed\tseat\topponent_index\topponent\tpolicy\tinterval_index\tstart_turn\tend_turn\tstart_own_workers\tend_own_workers\tstart_opponent_workers\tend_opponent_workers\tstart_own_score\tend_own_score\tstart_opponent_score\tend_opponent_score\tstart_live_own_crops\tend_live_own_crops\tstart_live_opponent_crops\tend_live_opponent_crops\tstart_live_joint_crops\tend_live_joint_crops\tstart_live_ambiguous_crops\tend_live_ambiguous_crops\town_crop_births\topponent_crop_births\tjoint_crop_births\tambiguous_crop_births\town_crop_removals\topponent_crop_removals\town_crop_harvest_units\town_reinvested_crops\tcumulative_successful_trains\tcumulative_completed_jobs\tcumulative_invalidated_jobs\tcumulative_invalid_direct_commands\tcumulative_provenance_failures\tcumulative_deposit_prediction_failures\tcumulative_own_created_crops\tcumulative_opponent_created_crops\tcumulative_joint_created_crops\tcumulative_ambiguous_created_crops\tcumulative_own_crop_harvest_units\tcumulative_own_reinvested_crops\tdone\taction_hash\tstate_hash").expect("write D103a header");
    for row in rows {
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.policy.label(),
            row.interval_index,
            row.start.turn,
            row.end.turn,
            row.start.own_workers,
            row.end.own_workers,
            row.start.opponent_workers,
            row.end.opponent_workers,
            row.start.own_score,
            row.end.own_score,
            row.start.opponent_score,
            row.end.opponent_score,
            row.start.live.own,
            row.end.live.own,
            row.start.live.opponent,
            row.end.live.opponent,
            row.start.live.joint,
            row.end.live.joint,
            row.start.live.ambiguous,
            row.end.live.ambiguous,
            row.own_crop_births,
            row.opponent_crop_births,
            row.joint_crop_births,
            row.ambiguous_crop_births,
            row.own_crop_removals,
            row.opponent_crop_removals,
            row.own_crop_harvest_units,
            row.own_reinvested_crops,
            row.cumulative.successful_trains,
            row.cumulative.completed_jobs,
            row.cumulative.invalidated_jobs,
            row.cumulative.invalid_direct_commands,
            row.cumulative.provenance_failures,
            row.cumulative.deposit_prediction_failures,
            row.cumulative.own_created_crops,
            row.cumulative.opponent_created_crops,
            row.cumulative.joint_created_crops,
            row.cumulative.ambiguous_created_crops,
            row.cumulative.own_crop_harvest_units,
            row.cumulative.own_reinvested_crops,
            usize::from(row.done),
            row.action_hash,
            row.state_hash,
        )
        .expect("write D103a row");
    }
    writer.flush().expect("flush D103a output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let start_seed = args
        .get(1)
        .map_or(9_824_100, |value| value.parse::<i64>().expect("start seed"));
    let map_count = args
        .get(2)
        .map_or(32, |value| value.parse::<usize>().expect("map count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d103a-d40-opponent-growth-phase-decomposition.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(20, |value| value.parse::<usize>().expect("threads"));
    assert!(map_count > 0 && threads > 0);

    let tasks: Vec<_> = (start_seed..start_seed + map_count as i64)
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
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::new()));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = tasks.get(index).copied() else {
                    break;
                };
                rows.lock().expect("D103a row lock").extend(play(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D103a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D103a rows")
        .into_inner()
        .expect("D103a rows lock");
    rows.sort_by_key(|row| (row.task, row.policy, row.interval_index));
    write_rows(&output, &rows);
    eprintln!(
        "saved {} D103a interval rows with {} workers in {:.3}s to {}",
        rows.len(),
        threads.min(tasks.len()),
        started.elapsed().as_secs_f64(),
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn smoke_task() -> Task {
        Task {
            map_seed: 9_824_000,
            seat: 0,
            opponent: 0,
        }
    }

    #[test]
    fn both_interval_paths_are_terminal_clean_and_deterministic() {
        let task = smoke_task();
        let first = play(task);
        let second = play(task);
        assert_eq!(first, second);
        for policy in [Policy::D40, Policy::Resident] {
            let rows: Vec<_> = first.iter().filter(|row| row.policy == policy).collect();
            assert!(!rows.is_empty());
            assert!(rows.last().is_some_and(|row| row.done));
            assert_eq!(rows.iter().filter(|row| row.done).count(), 1);
            assert!(rows.windows(2).all(|pair| {
                pair[0].interval_index + 1 == pair[1].interval_index
                    && pair[0].end.turn <= pair[1].start.turn
            }));
            let final_row = rows.last().unwrap();
            assert_eq!(final_row.cumulative.provenance_failures, 0);
            assert_eq!(final_row.cumulative.ambiguous_created_crops, 0);
        }
    }

    #[test]
    fn interval_crop_stock_flow_is_exact() {
        for row in play(smoke_task()) {
            assert_eq!(
                row.start.live.own + row.own_crop_births,
                row.end.live.own + row.own_crop_removals
            );
            assert_eq!(
                row.start.live.opponent + row.opponent_crop_births,
                row.end.live.opponent + row.opponent_crop_removals
            );
        }
    }
}
