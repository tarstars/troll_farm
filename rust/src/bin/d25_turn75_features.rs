//! Export referee-visible resident-prefix features for the D25 turn-75 selector.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

type Factory = fn() -> Box<dyn Strategy>;

fn compact() -> Box<dyn Strategy> {
    Box::new(CompactGold::new())
}

fn adaptive() -> Box<dyn Strategy> {
    Box::new(GoldElite::adaptive())
}

fn fixed_gold2() -> Box<dyn Strategy> {
    Box::new(GoldElite::configured(GoldEconomyConfig {
        max_trolls: 2,
        choppers: 1,
        stagger: 0,
        spec1: (2, 2, 0, 2),
        spec2: (2, 2, 0, 2),
        planters: 0,
        hold_until: 0,
        farm_cap: 12,
        co_fell: false,
        adaptive: false,
    }))
}

fn mybot() -> Box<dyn Strategy> {
    Box::new(MyBot::new())
}

fn printer() -> Box<dyn Strategy> {
    Box::new(PrinterBot::new())
}

fn scheduler() -> Box<dyn Strategy> {
    Box::new(SchedBot::new())
}

fn script() -> Box<dyn Strategy> {
    Box::new(ScriptBoss::new())
}

fn silver() -> Box<dyn Strategy> {
    Box::new(SilverBoss::new())
}

const OPPONENTS: [(&str, Factory); 8] = [
    ("compact_gold", compact),
    ("gold_adaptive", adaptive),
    ("gold_elite", fixed_gold2),
    ("mybot", mybot),
    ("printer_bot", printer),
    ("sched_bot", scheduler),
    ("script_boss", script),
    ("silver_boss", silver),
];

const CHECKPOINTS: [i32; 4] = [1, 25, 50, 75];
const ITEMS: [&str; 6] = ["plum", "lemon", "apple", "banana", "iron", "wood"];
const KINDS: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

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

fn manhattan(left: (i32, i32), right: (i32, i32)) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

struct Prefix {
    snapshots: BTreeMap<i32, GameState>,
    reached_cut: bool,
}

fn resident_prefix(seed: u64, seat: usize, opponent_index: usize) -> Prefix {
    let mut game = generate_bronze(seed);
    let mut resident = SecureOrchardBot::new();
    let opponent = OPPONENTS[opponent_index].1();
    let mut snapshots = BTreeMap::from([(1, game.clone())]);
    let mut stall_counter = 0;
    let mut ended = false;
    while game.turn < 75 && game.turn <= 300 {
        let ours = resident.commands(&yamo_view(&game, seat));
        let theirs = opponent.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        if CHECKPOINTS.contains(&game.turn) {
            snapshots.insert(game.turn, game.clone());
        }
        if has_stalled(&game, &mut stall_counter) {
            ended = true;
            break;
        }
    }
    if snapshots.len() != CHECKPOINTS.len() {
        for turn in CHECKPOINTS {
            snapshots.entry(turn).or_insert_with(|| game.clone());
        }
    }
    Prefix {
        reached_cut: !ended && game.turn == 75,
        snapshots,
    }
}

fn put(features: &mut BTreeMap<String, i64>, name: impl Into<String>, value: impl Into<i64>) {
    let previous = features.insert(name.into(), value.into());
    assert!(previous.is_none(), "duplicate D25 feature");
}

fn units_for(game: &GameState, player: usize) -> Vec<&troll_farm::game::state::Unit> {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect()
}

fn state_features(
    features: &mut BTreeMap<String, i64>,
    prefix: &str,
    game: &GameState,
    seat: usize,
) {
    let opponent = 1 - seat;
    put(features, format!("{prefix}_my_score"), game.scores[seat]);
    put(
        features,
        format!("{prefix}_opponent_score"),
        game.scores[opponent],
    );
    put(
        features,
        format!("{prefix}_score_gap"),
        game.scores[seat] - game.scores[opponent],
    );
    for (index, item) in ITEMS.iter().enumerate() {
        let ours = game.inventories[seat][index];
        let theirs = game.inventories[opponent][index];
        put(features, format!("{prefix}_my_inv_{item}"), ours);
        put(features, format!("{prefix}_opponent_inv_{item}"), theirs);
        put(features, format!("{prefix}_inv_gap_{item}"), ours - theirs);
    }

    for (label, player) in [("my", seat), ("opponent", opponent)] {
        let units = units_for(game, player);
        put(
            features,
            format!("{prefix}_{label}_workers"),
            units.len() as i64,
        );
        for (stat_name, values) in [
            ("ms", units.iter().map(|unit| unit.ms).collect::<Vec<_>>()),
            ("cc", units.iter().map(|unit| unit.cc).collect::<Vec<_>>()),
            ("hp", units.iter().map(|unit| unit.hp).collect::<Vec<_>>()),
            (
                "chop",
                units.iter().map(|unit| unit.chop).collect::<Vec<_>>(),
            ),
        ] {
            put(
                features,
                format!("{prefix}_{label}_{stat_name}_sum"),
                values.iter().sum::<i32>(),
            );
            put(
                features,
                format!("{prefix}_{label}_{stat_name}_max"),
                values.into_iter().max().unwrap_or(0),
            );
        }
        for (index, item) in ITEMS.iter().enumerate() {
            put(
                features,
                format!("{prefix}_{label}_carry_{item}"),
                units.iter().map(|unit| unit.carry[index]).sum::<i32>(),
            );
        }
        let own_shack = game.shacks[player];
        let other_shack = game.shacks[1 - player];
        put(
            features,
            format!("{prefix}_{label}_own_shack_distance_sum"),
            units
                .iter()
                .map(|unit| manhattan(unit.pos(), own_shack))
                .sum::<i32>(),
        );
        put(
            features,
            format!("{prefix}_{label}_other_shack_distance_sum"),
            units
                .iter()
                .map(|unit| manhattan(unit.pos(), other_shack))
                .sum::<i32>(),
        );
    }
    put(
        features,
        format!("{prefix}_worker_gap"),
        units_for(game, seat).len() as i64 - units_for(game, opponent).len() as i64,
    );

    put(
        features,
        format!("{prefix}_plants"),
        game.plants.len() as i64,
    );
    put(
        features,
        format!("{prefix}_plant_size"),
        game.plants.iter().map(|plant| plant.size).sum::<i32>(),
    );
    put(
        features,
        format!("{prefix}_plant_health"),
        game.plants.iter().map(|plant| plant.health).sum::<i32>(),
    );
    put(
        features,
        format!("{prefix}_plant_fruits"),
        game.plants.iter().map(|plant| plant.fruits).sum::<i32>(),
    );
    put(
        features,
        format!("{prefix}_plant_cooldown"),
        game.plants.iter().map(|plant| plant.cooldown).sum::<i32>(),
    );
    for kind in KINDS {
        let plants: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.plant_type == kind)
            .collect();
        let key = kind.to_ascii_lowercase();
        put(
            features,
            format!("{prefix}_{key}_count"),
            plants.len() as i64,
        );
        put(
            features,
            format!("{prefix}_{key}_size"),
            plants.iter().map(|plant| plant.size).sum::<i32>(),
        );
        put(
            features,
            format!("{prefix}_{key}_health"),
            plants.iter().map(|plant| plant.health).sum::<i32>(),
        );
        put(
            features,
            format!("{prefix}_{key}_fruits"),
            plants.iter().map(|plant| plant.fruits).sum::<i32>(),
        );
    }

    let mut closer_my = 0;
    let mut closer_opponent = 0;
    let mut tied = 0;
    let mut near_my = 0;
    let mut near_opponent = 0;
    let mut near_my_fruits = 0;
    let mut near_opponent_fruits = 0;
    let mut ripe_closer_my = 0;
    let mut ripe_closer_opponent = 0;
    for plant in &game.plants {
        let my_distance = manhattan(plant.pos(), game.shacks[seat]);
        let opponent_distance = manhattan(plant.pos(), game.shacks[opponent]);
        if my_distance < opponent_distance {
            closer_my += 1;
            ripe_closer_my += i32::from(plant.fruits > 0);
        } else if opponent_distance < my_distance {
            closer_opponent += 1;
            ripe_closer_opponent += i32::from(plant.fruits > 0);
        } else {
            tied += 1;
        }
        if my_distance <= 3 {
            near_my += 1;
            near_my_fruits += plant.fruits;
        }
        if opponent_distance <= 3 {
            near_opponent += 1;
            near_opponent_fruits += plant.fruits;
        }
    }
    for (name, value) in [
        ("closer_my", closer_my),
        ("closer_opponent", closer_opponent),
        ("equidistant", tied),
        ("near_my_3", near_my),
        ("near_opponent_3", near_opponent),
        ("near_my_3_fruits", near_my_fruits),
        ("near_opponent_3_fruits", near_opponent_fruits),
        ("ripe_closer_my", ripe_closer_my),
        ("ripe_closer_opponent", ripe_closer_opponent),
    ] {
        put(features, format!("{prefix}_{name}"), value);
    }
}

fn feature_map(prefix: &Prefix, seat: usize) -> BTreeMap<String, i64> {
    let initial = &prefix.snapshots[&1];
    let opponent = 1 - seat;
    let mut features = BTreeMap::new();
    put(&mut features, "map_width", initial.width);
    put(&mut features, "map_height", initial.height);
    put(
        &mut features,
        "map_walkable_count",
        initial.walkable.len() as i64,
    );
    put(&mut features, "map_water_count", initial.water.len() as i64);
    put(&mut features, "map_iron_count", initial.iron.len() as i64);
    put(
        &mut features,
        "map_shack_manhattan",
        manhattan(initial.shacks[seat], initial.shacks[opponent]),
    );
    for kind in KINDS {
        let key = kind.to_ascii_lowercase();
        let plants: Vec<_> = initial
            .plants
            .iter()
            .filter(|plant| plant.plant_type == kind)
            .collect();
        put(
            &mut features,
            format!("map_{key}_nearest_my"),
            plants
                .iter()
                .map(|plant| manhattan(plant.pos(), initial.shacks[seat]))
                .min()
                .unwrap_or(99),
        );
        put(
            &mut features,
            format!("map_{key}_nearest_opponent"),
            plants
                .iter()
                .map(|plant| manhattan(plant.pos(), initial.shacks[opponent]))
                .min()
                .unwrap_or(99),
        );
    }
    for turn in CHECKPOINTS {
        state_features(
            &mut features,
            &format!("t{turn}"),
            &prefix.snapshots[&turn],
            seat,
        );
    }

    let velocity_fields = [
        "my_score",
        "opponent_score",
        "score_gap",
        "my_inv_wood",
        "opponent_inv_wood",
        "inv_gap_wood",
        "my_workers",
        "opponent_workers",
        "worker_gap",
        "plants",
        "plant_size",
        "plant_health",
        "plant_fruits",
        "near_my_3",
        "near_opponent_3",
        "ripe_closer_my",
        "ripe_closer_opponent",
    ];
    for (start, end) in [(1, 25), (25, 50), (50, 75), (1, 75)] {
        for field in velocity_fields {
            let start_key = format!("t{start}_{field}");
            let end_key = format!("t{end}_{field}");
            let delta = features[&end_key] - features[&start_key];
            put(&mut features, format!("d{start}_{end}_{field}"), delta);
        }
    }
    features
}

struct Row {
    seed: u64,
    seat: usize,
    opponent_index: usize,
    reached_cut: bool,
    features: BTreeMap<String, i64>,
}

fn run(seed: u64, seat: usize, opponent_index: usize) -> Row {
    let prefix = resident_prefix(seed, seat, opponent_index);
    Row {
        seed,
        seat,
        opponent_index,
        reached_cut: prefix.reached_cut,
        features: feature_map(&prefix, seat),
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args
        .get(1)
        .map_or(0, |value| value.parse::<u64>().expect("numeric seed start"));
    let seed_count = args.get(2).map_or(5, |value| {
        value.parse::<usize>().expect("numeric seed count")
    });
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d25-turn75-features.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(16, |value| {
            value.parse::<usize>().expect("numeric thread count")
        })
        .clamp(1, 64);
    assert!(seed_count > 0, "seed count must be positive");

    let tasks: Vec<_> = (seed_start..seed_start + seed_count as u64)
        .flat_map(|seed| {
            (0..2).flat_map(move |seat| {
                (0..OPPONENTS.len()).map(move |opponent_index| (seed, seat, opponent_index))
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            thread::spawn(move || {
                let mut rows = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    let (seed, seat, opponent_index) = tasks[index];
                    rows.push(run(seed, seat, opponent_index));
                }
                rows
            })
        })
        .collect();
    let mut rows: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D25 feature worker"))
        .collect();
    rows.sort_by_key(|row| (row.seed, row.seat, row.opponent_index));
    let feature_names: Vec<_> = rows[0].features.keys().cloned().collect();
    assert!(rows
        .iter()
        .all(|row| { row.features.keys().cloned().collect::<Vec<_>>() == feature_names }));

    let mut writer = BufWriter::new(File::create(&output).expect("create D25 output"));
    write!(writer, "seed\tseat\topponent\treached_cut").expect("write D25 header");
    for feature in &feature_names {
        write!(writer, "\t{feature}").expect("write D25 feature header");
    }
    writeln!(writer).expect("finish D25 header");
    for row in &rows {
        write!(
            writer,
            "{}\t{}\t{}\t{}",
            row.seed,
            row.seat,
            OPPONENTS[row.opponent_index].0,
            usize::from(row.reached_cut),
        )
        .expect("write D25 key");
        for feature in &feature_names {
            write!(writer, "\t{}", row.features[feature]).expect("write D25 value");
        }
        writeln!(writer).expect("finish D25 row");
    }
    writer.flush().expect("flush D25 output");
    eprintln!(
        "saved {} rows x {} observable features in {:.3}s to {output}",
        rows.len(),
        feature_names.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn relative_feature_names_do_not_expose_identity_keys() {
        let prefix = resident_prefix(0, 0, 0);
        let features = feature_map(&prefix, 0);
        assert!(features.len() > 250);
        for forbidden in ["seed", "opponent_name", "opponent_index", "seat"] {
            assert!(!features.contains_key(forbidden));
        }
        assert!(features.contains_key("d50_75_opponent_score"));
        assert!(features.contains_key("t75_opponent_workers"));
    }
}
