//! Measure exact-engine terminal rollout cost with the promoted Yamo continuation.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone source addresses its modules through `crate::`; re-exporting
// them at this benchmark crate's root preserves those paths when it is nested.
pub use yamo::{bot, game};

use std::collections::BTreeSet;
use std::fs::File;
use std::io::{BufReader, Write};
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step, training_cost, APPLE, IRON, LEMON, PLUM};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{GameState, Plant as EnginePlant, Unit as EngineUnit};
use troll_farm::strategies::boss_real::BossReal;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::{MoisanBot, SecureOrchardBot, YamoBot, YamoOpeningPolicy};
use yamo::bot::Bot;
use yamo::game::protocol::{read_line, read_static_map, read_turn};
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const MODEL_NAMES: [&str; 4] = ["gold_elite", "sched_bot", "mybot", "silver_boss"];
const ROBUST_MODEL_NAMES: [&str; 8] = [
    "gold_elite",
    "sched_bot",
    "mybot",
    "silver_boss",
    "boss_real",
    "script_boss",
    "printer_bot",
    "gold_adaptive",
];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum FirstOption {
    Control,
    MaxBankHp0,
    FixedHp0 {
        movement_speed: i32,
        carry_capacity: i32,
        chop_power: i32,
    },
}

impl FirstOption {
    fn label(self) -> String {
        match self {
            Self::Control => "control".to_string(),
            Self::MaxBankHp0 => "max_bank_hp0".to_string(),
            Self::FixedHp0 {
                movement_speed,
                carry_capacity,
                chop_power,
            } => format!("m{movement_speed}c{carry_capacity}k{chop_power}"),
        }
    }

    fn bot(self) -> SecureOrchardBot {
        match self {
            Self::Control => SecureOrchardBot::new(),
            Self::MaxBankHp0 => SecureOrchardBot::max_bank_first_hp0(),
            Self::FixedHp0 {
                movement_speed,
                carry_capacity,
                chop_power,
            } => SecureOrchardBot::forced_first_worker_hp0(
                movement_speed,
                carry_capacity,
                chop_power,
            ),
        }
    }
}

fn first_options() -> Vec<FirstOption> {
    let mut options = vec![FirstOption::Control, FirstOption::MaxBankHp0];
    for movement_speed in 1..=3 {
        for carry_capacity in 1..=3 {
            for chop_power in 1..=3 {
                options.push(FirstOption::FixedHp0 {
                    movement_speed,
                    carry_capacity,
                    chop_power,
                });
            }
        }
    }
    options
}

fn yamo_view(game: &GameState, player: usize) -> YamoState {
    let opponent = 1 - player;
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: Stats {
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
            .map(|plant| Plant {
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
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

fn opponent(model: usize) -> Box<dyn Strategy> {
    match model {
        0 => Box::new(GoldElite::new()),
        1 => Box::new(SchedBot::new()),
        2 => Box::new(MyBot::new()),
        3 => Box::new(SilverBoss::new()),
        4 => Box::new(BossReal::new()),
        5 => Box::new(ScriptBoss::new()),
        6 => Box::new(PrinterBot::new()),
        7 => Box::new(GoldElite::adaptive()),
        8 => Box::new(CompactGold::new()),
        _ => unreachable!(),
    }
}

fn rollout(initial: &GameState, seat: usize, option: bool, model: usize) -> i32 {
    let mut game = initial.clone();
    let mut ours = if option {
        SecureOrchardBot::max_bank_first_hp0()
    } else {
        SecureOrchardBot::new()
    };
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    while game.turn <= 300 {
        let commands = ours.commands(&yamo_view(&game, seat));
        let opposition = theirs.decide(&game, 1 - seat);
        if seat == 0 {
            step(&mut game, &commands, &opposition);
        } else {
            step(&mut game, &opposition, &commands);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    game.scores[seat] - game.scores[1 - seat]
}

#[derive(Clone, Debug)]
struct OpeningRollout {
    margin: i32,
    first_commands: String,
    first_train: String,
}

fn opening_rollout(
    initial: &GameState,
    seat: usize,
    option: FirstOption,
    model: usize,
) -> OpeningRollout {
    let mut game = initial.clone();
    let mut ours = option.bot();
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    let mut first_commands = None;
    let mut first_train = None;
    while game.turn <= 300 {
        let commands = ours.commands(&yamo_view(&game, seat));
        if first_commands.is_none() {
            first_train = commands
                .iter()
                .find(|command| command.starts_with("TRAIN "))
                .cloned();
            first_commands = Some(commands.join(";"));
        }
        let opposition = theirs.decide(&game, 1 - seat);
        if seat == 0 {
            step(&mut game, &commands, &opposition);
        } else {
            step(&mut game, &opposition, &commands);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    OpeningRollout {
        margin: game.scores[seat] - game.scores[1 - seat],
        first_commands: first_commands.unwrap_or_else(|| "-".to_string()),
        first_train: first_train.unwrap_or_else(|| "-".to_string()),
    }
}

fn fixed_option_affordable(initial: &GameState, seat: usize, option: FirstOption) -> bool {
    let FirstOption::FixedHp0 {
        movement_speed,
        carry_capacity,
        chop_power,
    } = option
    else {
        return true;
    };
    let cost = training_cost(1, (movement_speed, carry_capacity, 0, chop_power));
    let inventory = initial.inventories[seat];
    inventory[PLUM] >= cost[PLUM]
        && inventory[LEMON] >= cost[LEMON]
        && inventory[APPLE] >= cost[APPLE]
        && (initial.iron.is_empty() || inventory[IRON] >= cost[IRON])
}

fn engine_state(view: YamoState) -> GameState {
    GameState {
        width: view.width,
        height: view.height,
        walkable: view.walkable.into_iter().collect(),
        shacks: view.shacks,
        inventories: view.inventories,
        units: view
            .units
            .into_iter()
            .map(|unit| EngineUnit {
                id: unit.id,
                player: unit.player as i32,
                x: unit.cell.0,
                y: unit.cell.1,
                ms: unit.stats.movement_speed,
                cc: unit.stats.carry_capacity,
                hp: unit.stats.harvest_power,
                chop: unit.stats.chop_power,
                carry: unit.carry,
            })
            .collect(),
        plants: view
            .plants
            .into_iter()
            .map(|plant| EnginePlant {
                plant_type: plant.kind.as_str().to_string(),
                x: plant.cell.0,
                y: plant.cell.1,
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: view.scores,
        turn: view.turn,
        next_id: view.next_id,
        iron: view.iron.into_iter().collect(),
        water: view.water.into_iter().collect(),
    }
}

fn read_dataset(path: &str) -> Vec<(u64, GameState)> {
    let file = File::open(path).expect("open rollout map dataset");
    let mut reader = BufReader::new(file);
    let mut maps = Vec::new();
    while let Some(line) = read_line(&mut reader) {
        if line.is_empty() {
            continue;
        }
        let mut fields = line.split_whitespace();
        assert_eq!(fields.next(), Some("SEED"), "expected SEED record");
        let seed = fields
            .next()
            .expect("seed value")
            .parse::<u64>()
            .expect("numeric seed");
        let map = read_static_map(&mut reader).expect("static map record");
        let view = read_turn(&mut reader, &map, 1).expect("turn-one map record");
        maps.push((seed, engine_state(view)));
    }
    maps
}

fn opening_command_grid_mode(args: &[String]) {
    let input = args.get(2).expect("opening-command-grid map path");
    let output = args.get(3).expect("opening-command-grid output path");
    let maps = read_dataset(input);
    let mut writer = std::io::BufWriter::new(File::create(output).expect("create command output"));
    writeln!(writer, "seed\tseat\tmodel\tcommands").expect("write command header");
    for (seed, initial) in maps {
        for seat in 0..2 {
            for (model, name) in ROBUST_MODEL_NAMES.iter().enumerate() {
                let commands = opponent(model).decide(&initial, seat).join(";");
                assert!(!commands.contains(['\t', '\n', '\r']));
                writeln!(writer, "{seed}\t{seat}\t{name}\t{commands}")
                    .expect("write opening command row");
            }
        }
    }
}

fn opening_plan_grid_mode(args: &[String]) {
    let input = args.get(2).expect("opening-plan-grid map path");
    let output = args.get(3).expect("opening-plan-grid output path");
    let maps = read_dataset(input);
    let mut writer = std::io::BufWriter::new(File::create(output).expect("create plan output"));
    writeln!(writer, "seed\tseat\tpolicy\ttrain").expect("write plan header");
    let policies = [
        ("tuned_carry", YamoOpeningPolicy::TUNED_CARRY),
        ("default", YamoOpeningPolicy::default()),
        ("carry2_chop2", YamoOpeningPolicy::CARRY2_CHOP2),
    ];
    for (seed, initial) in maps {
        for seat in 0..2 {
            let view = yamo_view(&initial, seat);
            for (name, policy) in policies {
                let stats = YamoBot::planned_second_troll(&view, policy);
                writeln!(
                    writer,
                    "{seed}\t{seat}\t{name}\tTRAIN {} {} {} {}",
                    stats.movement_speed,
                    stats.carry_capacity,
                    stats.harvest_power,
                    stats.chop_power,
                )
                .expect("write opening plan row");
            }
        }
    }
}

fn opening_policy_grid() -> Vec<(String, YamoOpeningPolicy)> {
    let mut policies = Vec::new();
    for train_horizon in [5, 10, 15, 20, 25] {
        for max_carry_capacity in [2, 3] {
            for preferred_min_carry in 1..=max_carry_capacity {
                for max_chop_power in [2, 3] {
                    for preferred_min_chop in 1..=max_chop_power {
                        for prefer_movement_ties in [false, true] {
                            let mut add =
                                |require_preferred: bool,
                                 max_extra_eta: i32,
                                 hard_train_turn: i32| {
                                    let policy = YamoOpeningPolicy {
                                        train_horizon,
                                        preferred_min_carry,
                                        max_carry_capacity,
                                        preferred_min_chop,
                                        max_chop_power,
                                        require_preferred,
                                        max_extra_eta,
                                        hard_train_turn,
                                        prefer_movement_ties,
                                    };
                                    let name = format!(
                                    "h{train_horizon}_pc{preferred_min_carry}_mc{max_carry_capacity}_pk{preferred_min_chop}_mk{max_chop_power}_r{}_e{max_extra_eta}_d{hard_train_turn}_m{}",
                                    usize::from(require_preferred),
                                    usize::from(prefer_movement_ties),
                                );
                                    policies.push((name, policy));
                                };
                            // When preferred stats are mandatory, extra ETA and deadline are
                            // behaviorally irrelevant.  Likewise, a zero extra-ETA policy does
                            // not consult the hard deadline.  Emit one canonical representative
                            // instead of thousands of duplicate configurations.
                            add(true, 0, 35);
                            add(false, 0, 35);
                            for max_extra_eta in [5, 10, 15] {
                                for hard_train_turn in [25, 35, 45] {
                                    add(false, max_extra_eta, hard_train_turn);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    policies
}

fn opening_policy_grid_mode(args: &[String]) {
    let input = args.get(2).expect("opening-policy-grid map path");
    let output = args.get(3).expect("opening-policy-grid output path");
    let maps = read_dataset(input);
    let policies = opening_policy_grid();
    let mut writer =
        std::io::BufWriter::new(File::create(output).expect("create policy-grid output"));
    writeln!(
        writer,
        "seed\tseat\tpolicy\ttrain_horizon\tpreferred_min_carry\tmax_carry_capacity\tpreferred_min_chop\tmax_chop_power\trequire_preferred\tmax_extra_eta\thard_train_turn\tprefer_movement_ties\ttrain"
    )
    .expect("write policy-grid header");
    for (seed, initial) in maps {
        for seat in 0..2 {
            let view = yamo_view(&initial, seat);
            for (name, policy) in &policies {
                let stats = YamoBot::planned_second_troll(&view, *policy);
                writeln!(
                    writer,
                    "{seed}\t{seat}\t{name}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\tTRAIN {} {} {} {}",
                    policy.train_horizon,
                    policy.preferred_min_carry,
                    policy.max_carry_capacity,
                    policy.preferred_min_chop,
                    policy.max_chop_power,
                    usize::from(policy.require_preferred),
                    policy.max_extra_eta,
                    policy.hard_train_turn,
                    usize::from(policy.prefer_movement_ties),
                    stats.movement_speed,
                    stats.carry_capacity,
                    stats.harvest_power,
                    stats.chop_power,
                )
                .expect("write policy-grid row");
            }
        }
    }
}

fn trajectory_command_grid_mode(args: &[String]) {
    let input = args.get(2).expect("trajectory-command-grid input path");
    let output = args.get(3).expect("trajectory-command-grid output path");
    let file = File::open(input).expect("open trajectory dataset");
    let mut reader = BufReader::new(file);
    let mut writer =
        std::io::BufWriter::new(File::create(output).expect("create trajectory command output"));
    writeln!(writer, "game_id\tturn\tmodel\tcommands").expect("write trajectory command header");
    while let Some(line) = read_line(&mut reader) {
        if line.is_empty() {
            continue;
        }
        let fields: Vec<_> = line.split_whitespace().collect();
        assert_eq!(
            fields.first().copied(),
            Some("GAME"),
            "expected GAME record"
        );
        assert_eq!(fields.len(), 3, "GAME record needs id and turn count");
        let game_id = fields[1].parse::<u64>().expect("numeric game id");
        let turns = fields[2].parse::<i32>().expect("numeric turn count");
        let map = read_static_map(&mut reader).expect("trajectory static map");
        let mut bots: Vec<(&str, Box<dyn Bot>)> = vec![
            ("resident_secure", Box::new(SecureOrchardBot::new())),
            (
                "resident_inner",
                Box::new(YamoBot::tuned_carry_regeneration_transit_idle_harvest()),
            ),
            ("yamo_plain", Box::new(YamoBot::tuned_carry())),
            ("moisan", Box::new(MoisanBot::default())),
        ];
        let strategies: Vec<_> = (0..ROBUST_MODEL_NAMES.len())
            .map(|model| (ROBUST_MODEL_NAMES[model], opponent(model)))
            .collect();
        for turn in 1..=turns {
            let view = read_turn(&mut reader, &map, turn).expect("trajectory turn block");
            for (name, bot) in &mut bots {
                let commands = bot.commands(&view).join(";");
                assert!(!commands.contains(['\t', '\n', '\r']));
                writeln!(writer, "{game_id}\t{turn}\t{name}\t{commands}")
                    .expect("write trajectory bot row");
            }
            let engine = engine_state(view);
            for (name, strategy) in &strategies {
                let commands = strategy.decide(&engine, 0).join(";");
                assert!(!commands.contains(['\t', '\n', '\r']));
                writeln!(writer, "{game_id}\t{turn}\t{name}\t{commands}")
                    .expect("write trajectory strategy row");
            }
        }
    }
}

fn parallel_rollouts(
    initial: &GameState,
    seats: &[usize],
    threads: usize,
    models: &[usize],
) -> Vec<(usize, bool, usize, i32)> {
    let tasks: Vec<_> = seats
        .iter()
        .copied()
        .flat_map(|seat| {
            [false, true].into_iter().flat_map(move |option| {
                models
                    .iter()
                    .copied()
                    .map(move |model| (seat, option, model))
            })
        })
        .collect();
    let chunk_size = tasks.len().div_ceil(threads);
    std::thread::scope(|scope| {
        let handles: Vec<_> = tasks
            .chunks(chunk_size)
            .map(|chunk| {
                scope.spawn(move || {
                    chunk
                        .iter()
                        .map(|(seat, option, model)| {
                            (
                                *seat,
                                *option,
                                *model,
                                rollout(initial, *seat, *option, *model),
                            )
                        })
                        .collect::<Vec<_>>()
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("rollout thread"))
            .collect()
    })
}

fn dataset_mode(args: &[String]) {
    let input = args.get(2).expect("dataset map path");
    let output = args.get(3).expect("dataset output path");
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(8)
        .clamp(1, 8);
    let compact_only = args.get(5).is_some_and(|value| value == "compact-only");
    let models: &[usize] = if compact_only { &[8] } else { &[0, 1, 2, 3] };
    let maps = read_dataset(input);
    let mut writer = std::io::BufWriter::new(File::create(output).expect("create rollout output"));
    writeln!(
        writer,
        "seed\tseat\tmodel\tcontrol_margin\toption_margin\tdelta\telapsed_us"
    )
    .expect("write rollout header");
    for (index, (seed, initial)) in maps.iter().enumerate() {
        let started = Instant::now();
        let values = parallel_rollouts(initial, &[0, 1], threads, models);
        let elapsed = started.elapsed().as_micros();
        for seat in 0..2 {
            for &model in models {
                let control = values
                    .iter()
                    .find(|value| value.0 == seat && !value.1 && value.2 == model)
                    .expect("control rollout")
                    .3;
                let option = values
                    .iter()
                    .find(|value| value.0 == seat && value.1 && value.2 == model)
                    .expect("option rollout")
                    .3;
                writeln!(
                    writer,
                    "{seed}\t{seat}\t{}\t{control}\t{option}\t{}\t{elapsed}",
                    if model == 8 {
                        "compact_gold"
                    } else {
                        MODEL_NAMES[model]
                    },
                    option - control,
                )
                .expect("write rollout row");
            }
        }
        eprintln!("completed {}/{} rollout maps", index + 1, maps.len());
    }
}

fn parallel_option_grid(
    initial: &GameState,
    threads: usize,
) -> Vec<(usize, FirstOption, usize, OpeningRollout)> {
    let options = first_options();
    let tasks: Vec<_> = (0..2)
        .flat_map(|seat| {
            options
                .iter()
                .copied()
                .filter(move |option| fixed_option_affordable(initial, seat, *option))
                .flat_map(move |option| {
                    (0..ROBUST_MODEL_NAMES.len()).map(move |model| (seat, option, model))
                })
        })
        .collect();
    let chunk_size = tasks.len().div_ceil(threads);
    std::thread::scope(|scope| {
        let handles: Vec<_> = tasks
            .chunks(chunk_size)
            .map(|chunk| {
                scope.spawn(move || {
                    chunk
                        .iter()
                        .map(|(seat, option, model)| {
                            (
                                *seat,
                                *option,
                                *model,
                                opening_rollout(initial, *seat, *option, *model),
                            )
                        })
                        .collect::<Vec<_>>()
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("option-grid thread"))
            .collect()
    })
}

fn option_grid_mode(args: &[String]) {
    let input = args.get(2).expect("option-grid map path");
    let output = args.get(3).expect("option-grid output path");
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(16)
        .clamp(1, 20);
    let maps = read_dataset(input);
    let options = first_options();
    let mut writer = std::io::BufWriter::new(File::create(output).expect("create grid output"));
    writeln!(
        writer,
        "seed\tseat\tmodel\toption\tactive\tcontrol_margin\toption_margin\tdelta\tfirst_train\telapsed_us"
    )
    .expect("write option-grid header");
    for (index, (seed, initial)) in maps.iter().enumerate() {
        let started = Instant::now();
        let values = parallel_option_grid(initial, threads);
        let elapsed = started.elapsed().as_micros();
        for seat in 0..2 {
            for model in 0..ROBUST_MODEL_NAMES.len() {
                let control = &values
                    .iter()
                    .find(|value| {
                        value.0 == seat && value.1 == FirstOption::Control && value.2 == model
                    })
                    .expect("option-grid control")
                    .3;
                for option in options.iter().copied() {
                    let result = if fixed_option_affordable(initial, seat, option) {
                        &values
                            .iter()
                            .find(|value| value.0 == seat && value.1 == option && value.2 == model)
                            .expect("active option-grid result")
                            .3
                    } else {
                        control
                    };
                    let active = result.first_commands != control.first_commands;
                    writeln!(
                        writer,
                        "{seed}\t{seat}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{elapsed}",
                        ROBUST_MODEL_NAMES[model],
                        option.label(),
                        usize::from(active),
                        control.margin,
                        result.margin,
                        result.margin - control.margin,
                        result.first_train,
                    )
                    .expect("write option-grid row");
                }
            }
        }
        eprintln!("completed {}/{} option-grid maps", index + 1, maps.len());
    }
}

fn percentile(samples: &[u64], fraction: f64) -> u64 {
    samples[((samples.len() - 1) as f64 * fraction).round() as usize]
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    if args
        .get(1)
        .is_some_and(|value| value == "trajectory-command-grid")
    {
        trajectory_command_grid_mode(&args);
        return;
    }
    if args
        .get(1)
        .is_some_and(|value| value == "opening-policy-grid")
    {
        opening_policy_grid_mode(&args);
        return;
    }
    if args
        .get(1)
        .is_some_and(|value| value == "opening-plan-grid")
    {
        opening_plan_grid_mode(&args);
        return;
    }
    if args
        .get(1)
        .is_some_and(|value| value == "opening-command-grid")
    {
        opening_command_grid_mode(&args);
        return;
    }
    if args.get(1).is_some_and(|value| value == "option-grid") {
        option_grid_mode(&args);
        return;
    }
    if args.get(1).is_some_and(|value| value == "dataset") {
        dataset_mode(&args);
        return;
    }
    let seeds = args
        .get(1)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(10);
    let threads = args
        .get(2)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(8)
        .clamp(1, 8);
    let parallel_only = args.get(3).is_some_and(|value| value == "parallel-only");
    let mut sequential = Vec::new();
    let mut parallel = Vec::new();
    let mut sink = 0i64;
    for seed in 0..seeds {
        let initial = generate_bronze(seed);
        if !parallel_only {
            let started = Instant::now();
            for option in [false, true] {
                for model in 0..4 {
                    sink += rollout(&initial, 0, option, model) as i64;
                }
            }
            sequential.push(started.elapsed().as_micros() as u64);
        }

        let started = Instant::now();
        let values = parallel_rollouts(&initial, &[0], threads, &[0, 1, 2, 3]);
        sink += values
            .into_iter()
            .map(|value| i64::from(value.3))
            .sum::<i64>();
        parallel.push(started.elapsed().as_micros() as u64);
    }
    sequential.sort_unstable();
    parallel.sort_unstable();
    let report = |name: &str, values: &[u64]| {
        let mean = values.iter().sum::<u64>() as f64 / values.len() as f64;
        println!(
            "{name}: mean {:.2} ms, p50 {:.2}, p95 {:.2}, max {:.2}",
            mean / 1000.0,
            percentile(values, 0.50) as f64 / 1000.0,
            percentile(values, 0.95) as f64 / 1000.0,
            values[values.len() - 1] as f64 / 1000.0,
        );
    };
    println!("Yamo option timing: {seeds} maps, eight terminal games/decision, {threads} workers");
    if !sequential.is_empty() {
        report("sequential", &sequential);
    }
    report("parallel", &parallel);
    println!("sink {sink}");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn first_option_grid_has_control_dynamic_and_all_hp0_specs() {
        let options = first_options();
        assert_eq!(options.len(), 29);
        assert_eq!(options[0].label(), "control");
        assert_eq!(options[1].label(), "max_bank_hp0");
        assert_eq!(options[2].label(), "m1c1k1");
        assert_eq!(options.last().unwrap().label(), "m3c3k3");
    }

    #[test]
    fn opening_policy_grid_is_canonical_and_contains_tuned_carry() {
        let policies = opening_policy_grid();
        assert_eq!(policies.len(), 2_750);
        let names: BTreeSet<_> = policies.iter().map(|(name, _)| name).collect();
        assert_eq!(names.len(), policies.len());
        assert!(policies
            .iter()
            .any(|(_, policy)| *policy == YamoOpeningPolicy::TUNED_CARRY));
    }

    #[test]
    fn unaffordable_fixed_option_is_exact_turn_one_control() {
        let mut game = generate_bronze(0);
        game.inventories[0] = [0; 6];
        let control = FirstOption::Control.bot().commands(&yamo_view(&game, 0));
        let forced = FirstOption::FixedHp0 {
            movement_speed: 3,
            carry_capacity: 3,
            chop_power: 3,
        }
        .bot()
        .commands(&yamo_view(&game, 0));
        assert_eq!(forced, control);
        assert!(!fixed_option_affordable(
            &game,
            0,
            FirstOption::FixedHp0 {
                movement_speed: 3,
                carry_capacity: 3,
                chop_power: 3,
            }
        ));
    }

    #[test]
    fn affordable_fixed_option_issues_requested_turn_one_train() {
        let mut game = generate_bronze(0);
        game.inventories[0] = [20; 6];
        let commands = FirstOption::FixedHp0 {
            movement_speed: 2,
            carry_capacity: 3,
            chop_power: 1,
        }
        .bot()
        .commands(&yamo_view(&game, 0));
        assert!(commands.iter().any(|command| command == "TRAIN 2 3 0 1"));
        assert!(fixed_option_affordable(
            &game,
            0,
            FirstOption::FixedHp0 {
                movement_speed: 2,
                carry_capacity: 3,
                chop_power: 1,
            }
        ));
    }
}
