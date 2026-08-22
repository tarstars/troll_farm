//! A2-1 referee-mode economy-skeleton panel.

#[path = "../d171a_control_resident_snapshot.rs"]
mod control_resident;
#[path = "../game/a2_economy_skeleton.rs"]
mod a2_economy_skeleton;

use std::collections::BTreeMap;
use std::fmt::Write as FmtWrite;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use a2_economy_skeleton::{EconomyMetrics, EconomySkeleton};
use troll_farm::game::a2_referee_parity::{self, LegalityReport, MovementRngStats};
use troll_farm::game::engine::has_stalled;
use troll_farm::game::state::{GameState, Plant, Unit};
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{
    LegendFieldProxyV2, LegendFieldProxyV2Config,
};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const FNV_OFFSET: u64 = 14_695_981_039_346_656_037;
const DEVELOPMENT_START: i64 = 9_880_000;
const DEVELOPMENT_MAPS: i64 = 32;
const CONFIRMATION_START: i64 = 9_881_000;
const CONFIRMATION_MAPS: i64 = 128;

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
    let mut hash = FNV_OFFSET;
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
    let mut units: Vec<_> = game.units.iter().collect();
    units.sort_by_key(|unit| unit.id);
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
    plants.sort_by_key(|plant| (plant.x, plant.y));
    for plant in plants {
        hash = fnv1a(hash, plant.plant_type.as_bytes());
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

enum Opponent {
    Resident(control_resident::bot::moisan::SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => {
                Self::Resident(control_resident::bot::moisan::SecureOrchardBot::new())
            }
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => {
                Self::Local(Box::new(NorxondorNative::new(true)))
            }
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
            Self::Resident(bot) => {
                use control_resident::bot::Bot as _;
                bot.commands(&control_view(game, player))
            }
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

fn control_view(game: &GameState, player: usize) -> control_resident::game::GameState {
    let opponent = 1 - player;
    control_resident::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| control_resident::game::Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: control_resident::game::Stats {
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
            .map(|plant| control_resident::game::Plant {
                kind: control_resident::game::PlantKind::parse(&plant.plant_type)
                    .expect("known plant type"),
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

#[derive(Clone)]
struct StateSnapshot {
    units: Vec<Unit>,
    plants: Vec<Plant>,
    inventories: [[i32; 6]; 2],
}

impl StateSnapshot {
    fn capture(game: &GameState) -> Self {
        Self {
            units: game.units.clone(),
            plants: game.plants.clone(),
            inventories: game.inventories,
        }
    }
}

struct SideResult {
    done: bool,
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    action_hash: u64,
    state_hash: u64,
    own_workers_final: usize,
    own_commands: usize,
    metrics: EconomyMetrics,
    legality: LegalityReport,
    movement_rng: MovementRngStats,
    map_rows: Vec<String>,
    states: Vec<StateSnapshot>,
    turn_commands: Vec<(Vec<String>, Vec<String>)>,
}

fn build_map_rows(game: &GameState) -> Vec<String> {
    (0..game.height)
        .map(|y| {
            (0..game.width)
                .map(|x| {
                    let cell = (x, y);
                    if game.shacks[0] == cell {
                        '0'
                    } else if game.shacks[1] == cell {
                        '1'
                    } else if game.iron.contains(&cell) {
                        '+'
                    } else if game.water.contains(&cell) {
                        '~'
                    } else if game.walkable.contains(&cell) {
                        '.'
                    } else {
                        '#'
                    }
                })
                .collect::<String>()
        })
        .collect()
}

fn hash_commands(mut hash: u64, commands: &[Vec<String>; 2]) -> u64 {
    for (player, player_commands) in commands.iter().enumerate() {
        hash = fnv1a(hash, &[player as u8]);
        for command in player_commands {
            hash = fnv1a(hash, command.as_bytes());
            hash = fnv1a(hash, &[0]);
        }
        hash = fnv1a(hash, &[255]);
    }
    hash
}

fn play(map_seed: i64, seat: usize, opponent_index: usize, dump: bool) -> SideResult {
    let mut referee = a2_referee_parity::generate_official(map_seed);
    let mut ours = EconomySkeleton::new();
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(opponent_index));
    let mut turns_until_end = 0;
    let mut action_hash = FNV_OFFSET;
    let mut own_commands = 0usize;
    let mut states = Vec::new();
    let mut turn_commands = Vec::new();
    let map_rows = if dump {
        build_map_rows(&referee.game)
    } else {
        Vec::new()
    };
    if dump {
        states.push(StateSnapshot::capture(&referee.game));
    }
    let mut done = false;

    while !done {
        let before = referee.game.clone();
        let opponent = 1 - seat;
        let ours_commands = ours.commands(&before, seat);
        let theirs_commands = theirs.commands(&before, opponent);
        own_commands += ours_commands
            .iter()
            .flat_map(|line| line.split(';'))
            .filter(|command| {
                let upper = command.trim().to_ascii_uppercase();
                !upper.is_empty() && upper != "WAIT" && !upper.starts_with("MSG ")
            })
            .count();
        let commands = if seat == 0 {
            [ours_commands, theirs_commands]
        } else {
            [theirs_commands, ours_commands]
        };
        action_hash = hash_commands(action_hash, &commands);
        if dump {
            turn_commands.push((commands[0].clone(), commands[1].clone()));
        }
        a2_referee_parity::step(&mut referee, &commands[0], &commands[1]);
        let own_commands_ref = &commands[seat];
        let opponent_commands_ref = &commands[opponent];
        ours.observe_transition(
            &before,
            &referee.game,
            seat,
            own_commands_ref,
            opponent_commands_ref,
        );
        if dump {
            states.push(StateSnapshot::capture(&referee.game));
        }
        done = referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&referee.game, &mut turns_until_end);
    }

    SideResult {
        done,
        turn: referee.game.turn,
        own_score: referee.game.scores[seat],
        opponent_score: referee.game.scores[1 - seat],
        action_hash,
        state_hash: canonical_state_hash(&referee.game),
        own_workers_final: referee
            .game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        own_commands,
        metrics: ours.metrics().clone(),
        legality: referee.legality,
        movement_rng: referee.movement_rng,
        map_rows,
        states,
        turn_commands,
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Row {
    task: Task,
    side: SideResult,
}

fn json_escape_into(buffer: &mut String, text: &str) {
    buffer.push('"');
    for character in text.chars() {
        match character {
            '"' => buffer.push_str("\\\""),
            '\\' => buffer.push_str("\\\\"),
            '\n' => buffer.push_str("\\n"),
            '\r' => buffer.push_str("\\r"),
            '\t' => buffer.push_str("\\t"),
            _ => buffer.push(character),
        }
    }
    buffer.push('"');
}

fn write_unit(buffer: &mut String, unit: &Unit) {
    write!(
        buffer,
        "[{},{},{},{},{},{},{},{},{},{},{},{},{},{}]",
        unit.id,
        unit.player,
        unit.x,
        unit.y,
        unit.ms,
        unit.cc,
        unit.hp,
        unit.chop,
        unit.carry[0],
        unit.carry[1],
        unit.carry[2],
        unit.carry[3],
        unit.carry[4],
        unit.carry[5],
    )
    .expect("write A2-1 unit");
}

fn write_plant(buffer: &mut String, plant: &Plant) {
    buffer.push('[');
    write!(buffer, "{},{},", plant.x, plant.y).expect("write A2-1 plant position");
    json_escape_into(buffer, &plant.plant_type);
    write!(
        buffer,
        ",{},{},{},{}]",
        plant.size, plant.health, plant.fruits, plant.cooldown
    )
    .expect("write A2-1 plant");
}

fn write_state(buffer: &mut String, state: &StateSnapshot) {
    buffer.push_str("{\"u\":[");
    for (index, unit) in state.units.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_unit(buffer, unit);
    }
    buffer.push_str("],\"p\":[");
    for (index, plant) in state.plants.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_plant(buffer, plant);
    }
    write!(
        buffer,
        "],\"b\":[[{},{},{},{},{},{}],[{},{},{},{},{},{}]]}}",
        state.inventories[0][0],
        state.inventories[0][1],
        state.inventories[0][2],
        state.inventories[0][3],
        state.inventories[0][4],
        state.inventories[0][5],
        state.inventories[1][0],
        state.inventories[1][1],
        state.inventories[1][2],
        state.inventories[1][3],
        state.inventories[1][4],
        state.inventories[1][5],
    )
    .expect("write A2-1 inventory");
}

fn write_commands(buffer: &mut String, commands: &[String]) {
    buffer.push('[');
    for (index, command) in commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        json_escape_into(buffer, command);
    }
    buffer.push(']');
}

fn write_trajectory_line(task: &Task, side: &SideResult) -> String {
    let (score0, score1) = if task.seat == 0 {
        (side.own_score, side.opponent_score)
    } else {
        (side.opponent_score, side.own_score)
    };
    let mut buffer = String::with_capacity(4096);
    write!(
        buffer,
        "{{\"seed\":{},\"seat\":{},\"opp\":{},\"opp_name\":",
        task.map_seed, task.seat, task.opponent
    )
    .expect("write A2-1 trajectory header");
    json_escape_into(
        &mut buffer,
        MacroOpponentMode::from_index(task.opponent).label(),
    );
    buffer.push_str(",\"arm\":\"a2_1\",\"map_rows\":[");
    for (index, row) in side.map_rows.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        json_escape_into(&mut buffer, row);
    }
    write!(
        buffer,
        "],\"turns\":{},\"scores\":[{},{}],\"states\":[",
        side.turn_commands.len(),
        score0,
        score1
    )
    .expect("write A2-1 trajectory scores");
    for (index, state) in side.states.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_state(&mut buffer, state);
    }
    buffer.push_str("],\"c0\":[");
    for (index, (commands0, _)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_commands(&mut buffer, commands0);
    }
    buffer.push_str("],\"c1\":[");
    for (index, (_, commands1)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_commands(&mut buffer, commands1);
    }
    buffer.push_str("]}\n");
    buffer
}

fn run_task(
    task: Task,
    dump: bool,
    trajectory_writer: Option<&Mutex<BufWriter<File>>>,
) -> Row {
    let side = play(task.map_seed, task.seat, task.opponent, dump);
    if dump {
        trajectory_writer
            .expect("A2-1 trajectory writer")
            .lock()
            .expect("A2-1 trajectory lock")
            .write_all(write_trajectory_line(&task, &side).as_bytes())
            .expect("write A2-1 trajectory");
    }
    Row { task, side }
}

fn reason_counts(report: &LegalityReport) -> String {
    report
        .reason_counts()
        .into_iter()
        .map(|(reason, count)| format!("{reason}={count}"))
        .collect::<Vec<_>>()
        .join(",")
}

fn reason_counts_for_player(report: &LegalityReport, player: usize) -> String {
    report
        .reason_counts_for_player(player)
        .into_iter()
        .map(|(reason, count)| format!("{reason}={count}"))
        .collect::<Vec<_>>()
        .join(",")
}

fn first_issue(report: &LegalityReport, player: Option<usize>, critical: bool) -> String {
    report
        .issues
        .iter()
        .find(|issue| {
            player.map_or(true, |expected| issue.player == expected)
                && (!critical || issue.critical)
        })
        .map(|issue| {
            format!(
                "t{}:p{}:{}:{}:{}",
                issue.turn, issue.player, issue.phase, issue.reason, issue.command
            )
            .replace(['\t', '\n', '\r'], " ")
        })
        .unwrap_or_default()
}

fn bill_text(bill: Option<[i32; 6]>) -> String {
    bill.map(|values| {
        values
            .iter()
            .map(i32::to_string)
            .collect::<Vec<_>>()
            .join(",")
    })
    .unwrap_or_default()
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create A2-1 output"));
    writeln!(
        writer,
        "map_seed\tseat\topponent_index\topponent\tdone\tturn\town_score\t\
opponent_score\tmargin\taction_hash\tstate_hash\town_workers_final\town_commands\t\
own_generations_created\town_harvest_plum\town_harvest_lemon\town_harvest_apple\t\
own_harvest_banana\town_bank_plum\town_bank_lemon\town_bank_apple\town_bank_banana\t\
own_bill_fruit_harvested\town_bill_fruit_banked\tfirst_worker3_turn\t\
fruit_funded_worker3\tworker3_bill\tworker3_bill_needs_owned_fruit\t\
mined_iron_roster2\tmined_iron_roster3plus\tiron_directed_moves\tcommands_checked\t\
legality_issues\town_legality_issues\topponent_legality_issues\tcritical_issues\t\
own_critical_issues\topponent_critical_issues\tunclassified_issues\t\
legality_reason_counts\town_legality_reason_counts\topponent_legality_reason_counts\t\
first_legality_issue\tfirst_own_legality_issue\tfirst_opponent_legality_issue\t\
first_critical_issue\tmovement_rng_draws\tmovement_tied_draws"
    )
    .expect("write A2-1 header");
    for row in rows {
        let side = &row.side;
        let metrics = &side.metrics;
        let opponent = 1 - row.task.seat;
        let fields = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            row.task.opponent.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_owned(),
            u8::from(side.done).to_string(),
            side.turn.to_string(),
            side.own_score.to_string(),
            side.opponent_score.to_string(),
            (side.own_score - side.opponent_score).to_string(),
            side.action_hash.to_string(),
            side.state_hash.to_string(),
            side.own_workers_final.to_string(),
            side.own_commands.to_string(),
            metrics.own_generations_created.to_string(),
            metrics.own_crop_harvested[0].to_string(),
            metrics.own_crop_harvested[1].to_string(),
            metrics.own_crop_harvested[2].to_string(),
            metrics.own_crop_harvested[3].to_string(),
            metrics.own_crop_banked[0].to_string(),
            metrics.own_crop_banked[1].to_string(),
            metrics.own_crop_banked[2].to_string(),
            metrics.own_crop_banked[3].to_string(),
            metrics.own_bill_fruit_harvested().to_string(),
            metrics.own_bill_fruit_banked().to_string(),
            metrics
                .first_worker3_turn
                .map(|turn| turn.to_string())
                .unwrap_or_default(),
            u8::from(metrics.fruit_funded_worker3).to_string(),
            bill_text(metrics.worker3_bill),
            u8::from(metrics.worker3_bill_needs_owned_fruit).to_string(),
            metrics.mined_iron_roster2.to_string(),
            metrics.mined_iron_roster3plus.to_string(),
            metrics.iron_directed_moves.to_string(),
            side.legality.commands_checked.to_string(),
            side.legality.issue_count().to_string(),
            side.legality
                .issue_count_for_player(row.task.seat)
                .to_string(),
            side.legality
                .issue_count_for_player(opponent)
                .to_string(),
            side.legality.critical_issue_count().to_string(),
            side.legality
                .critical_issue_count_for_player(row.task.seat)
                .to_string(),
            side.legality
                .critical_issue_count_for_player(opponent)
                .to_string(),
            side.legality.unclassified_issue_count().to_string(),
            reason_counts(&side.legality),
            reason_counts_for_player(&side.legality, row.task.seat),
            reason_counts_for_player(&side.legality, opponent),
            first_issue(&side.legality, None, false),
            first_issue(&side.legality, Some(row.task.seat), false),
            first_issue(&side.legality, Some(opponent), false),
            first_issue(&side.legality, None, true),
            side.movement_rng.draws.to_string(),
            side.movement_rng.tied_draws.to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write A2-1 row");
    }
}

fn parse<T: std::str::FromStr>(text: &str, what: &str) -> T {
    text.parse()
        .unwrap_or_else(|_| panic!("invalid {what}: {text}"))
}

fn range_allowed(start_seed: i64, maps: i64) -> bool {
    let end_seed = start_seed.saturating_add(maps);
    (start_seed >= DEVELOPMENT_START
        && end_seed <= DEVELOPMENT_START + DEVELOPMENT_MAPS)
        || (start_seed >= CONFIRMATION_START
            && end_seed <= CONFIRMATION_START + CONFIRMATION_MAPS)
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        args.len() == 5 || args.len() == 6,
        "usage: a2_1_economy_skeleton START_SEED MAPS OUTPUT THREADS [TRAJECTORIES]"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: i64 = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(
        range_allowed(start_seed, maps),
        "A2-1 runner is confined to its frozen development and confirmation ranges"
    );
    let dump = args.len() == 6;
    let trajectory_writer = if dump {
        Some(Mutex::new(BufWriter::new(
            File::create(&args[5]).expect("create A2-1 trajectory NDJSON"),
        )))
    } else {
        None
    };

    let work: Vec<Task> = (start_seed..start_seed + maps)
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
    let trajectory_writer = Arc::new(trajectory_writer);
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            let trajectory_writer = Arc::clone(&trajectory_writer);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = work.get(index).copied() else {
                    break;
                };
                let row =
                    run_task(task, dump, trajectory_writer.as_ref().as_ref());
                rows.lock().expect("A2-1 rows lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("A2-1 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole A2-1 rows")
        .into_inner()
        .expect("A2-1 rows lock");
    rows.sort_by_key(|row| row.task);
    write_rows(output, &rows);

    let fruit_funded = rows
        .iter()
        .filter(|row| row.side.metrics.fruit_funded_worker3)
        .count();
    let own_issues: usize = rows
        .iter()
        .map(|row| {
            row.side
                .legality
                .issue_count_for_player(row.task.seat)
        })
        .sum();
    let critical: usize = rows
        .iter()
        .map(|row| row.side.legality.critical_issue_count())
        .sum();
    let reason_totals = {
        let mut totals = BTreeMap::new();
        for row in &rows {
            for (reason, count) in row.side.legality.reason_counts() {
                *totals.entry(reason).or_insert(0usize) += count;
            }
        }
        totals
    };
    eprintln!(
        "saved {} A2-1 rows with {} workers in {:.3}s; fruit_funded_worker3={}/{} \
({:.3}%); own_issues={}; critical={}; all_reasons={:?}",
        rows.len(),
        threads.min(work.len()),
        started.elapsed().as_secs_f64(),
        fruit_funded,
        rows.len(),
        100.0 * fruit_funded as f64 / rows.len() as f64,
        own_issues,
        critical,
        reason_totals,
    );
}
