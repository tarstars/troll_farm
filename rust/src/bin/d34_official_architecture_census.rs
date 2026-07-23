//! Full-game census of frozen controller architectures on exact official maps.
//!
//! D34 is deliberately a broad architecture discriminator.  Every controller
//! starts at turn one on the same official seed/seat/opponent cells; there are
//! no midgame handoffs and no parameter variants.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone resident uses `crate::game` and `crate::bot`.  Re-exporting
// its modules preserves those paths when it is compiled as a nested module.
pub use yamo::{bot, game};

use std::collections::BTreeSet;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState};
use troll_farm::strategies::capacity_separated_denial::CapacitySeparatedDenial;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::{GoldEconomyConfig, GoldElite};
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::norxondor_research::NorxondorThreeWorkerSilver;
use troll_farm::strategies::ownership_aware_farm::OwnershipAwareFarm;
use troll_farm::strategies::prefruit_interruption::PreFruitInterruption;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

enum Controller {
    Resident(SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Controller {
    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

type Factory = fn() -> Controller;

fn resident() -> Controller {
    Controller::Resident(SecureOrchardBot::new())
}

fn fixed_gold2() -> GoldElite {
    GoldElite::configured(GoldEconomyConfig {
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
    })
}

fn private2() -> Controller {
    Controller::Local(Box::new(fixed_gold2()))
}

fn ownership2() -> Controller {
    Controller::Local(Box::new(OwnershipAwareFarm::new()))
}

fn prefruit2() -> Controller {
    Controller::Local(Box::new(PreFruitInterruption::new()))
}

fn gold_adaptive() -> Controller {
    Controller::Local(Box::new(GoldElite::adaptive()))
}

fn separated_denial() -> Controller {
    Controller::Local(Box::new(CapacitySeparatedDenial::new()))
}

fn hybrid3() -> Controller {
    Controller::Local(Box::new(GoldElite::hybrid()))
}

fn accumulate4() -> Controller {
    Controller::Local(Box::new(GoldElite::configured(GoldEconomyConfig {
        max_trolls: 4,
        choppers: 2,
        stagger: 30,
        spec1: (2, 2, 0, 2),
        spec2: (2, 2, 0, 2),
        planters: 1,
        hold_until: 0,
        farm_cap: 18,
        co_fell: false,
        adaptive: false,
    })))
}

fn norx3() -> Controller {
    Controller::Local(Box::new(NorxondorThreeWorkerSilver::new()))
}

const CANDIDATES: [(&str, Factory); 9] = [
    ("resident", resident),
    ("private2", private2),
    ("ownership2", ownership2),
    ("prefruit2", prefruit2),
    ("gold_adaptive", gold_adaptive),
    ("separated_denial", separated_denial),
    ("hybrid3", hybrid3),
    ("accumulate4", accumulate4),
    ("norx3", norx3),
];

fn compact_gold() -> Controller {
    Controller::Local(Box::new(CompactGold::new()))
}

fn norx_native_three() -> Controller {
    Controller::Local(Box::new(NorxondorNative::new(true)))
}

fn legend_balanced() -> Controller {
    Controller::Local(Box::new(LegendFieldProxyV2::configured(
        LegendFieldProxyV2Config {
            producer_spec: (2, 2, 1, 1),
            chopper_spec: (2, 2, 0, 2),
            late_chop: true,
        },
    )))
}

fn mybot() -> Controller {
    Controller::Local(Box::new(MyBot::new()))
}

fn script_boss() -> Controller {
    Controller::Local(Box::new(ScriptBoss::new()))
}

fn silver_boss() -> Controller {
    Controller::Local(Box::new(SilverBoss::new()))
}

const OPPONENTS: [(&str, Factory); 8] = [
    ("resident", resident),
    ("gold_adaptive", gold_adaptive),
    ("compact_gold", compact_gold),
    ("norx_native_three", norx_native_three),
    ("legend_balanced", legend_balanced),
    ("mybot", mybot),
    ("script_boss", script_boss),
    ("silver_boss", silver_boss),
];

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

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

fn worker_count(game: &GameState, player: usize) -> usize {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count()
}

const VERBS: [&str; 8] = [
    "TRAIN", "MOVE", "CHOP", "HARVEST", "DROP", "PICK", "PLANT", "MINE",
];

fn count_commands(counts: &mut [usize; VERBS.len()], commands: &[String]) {
    for command in commands {
        let Some(verb) = command.split_whitespace().next() else {
            continue;
        };
        if let Some(index) = VERBS.iter().position(|known| *known == verb) {
            counts[index] += 1;
        }
    }
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

const FNV_OFFSET: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

fn trace_commands(hash: &mut u64, commands: &[String]) {
    for command in commands {
        for byte in command.as_bytes().iter().copied().chain([0xff]) {
            *hash ^= u64::from(byte);
            *hash = hash.wrapping_mul(FNV_PRIME);
        }
    }
    *hash ^= 0xfe;
    *hash = hash.wrapping_mul(FNV_PRIME);
}

#[derive(Clone, Copy)]
struct Task {
    seed: i64,
    seat: usize,
    opponent_index: usize,
    candidate_index: usize,
}

struct ResultRow {
    task: Task,
    width: i32,
    height: i32,
    initial_plants: usize,
    final_turn: i32,
    margin: i32,
    my_score: i32,
    opponent_score: i32,
    my_inventory: [i32; 6],
    opponent_inventory: [i32; 6],
    my_workers: usize,
    opponent_workers: usize,
    max_my_workers: usize,
    max_opponent_workers: usize,
    first_my_third_worker_turn: i32,
    first_opponent_third_worker_turn: i32,
    my_counts: [usize; VERBS.len()],
    opponent_counts: [usize; VERBS.len()],
    my_successful_plants: usize,
    opponent_successful_plants: usize,
    ambiguous_plants: usize,
    max_plants: usize,
    terminal_plants: usize,
    my_command_hash: u64,
    opponent_command_hash: u64,
}

fn run_task(task: Task) -> ResultRow {
    let mut game = generate_official(task.seed);
    let width = game.width;
    let height = game.height;
    let initial_plants = game.plants.len();
    let mut candidate = CANDIDATES[task.candidate_index].1();
    let mut opponent = OPPONENTS[task.opponent_index].1();
    let mut stall_counter = 0;
    let mut max_my_workers = worker_count(&game, task.seat);
    let mut max_opponent_workers = worker_count(&game, 1 - task.seat);
    let mut first_my_third_worker_turn = -1;
    let mut first_opponent_third_worker_turn = -1;
    let mut my_counts = [0; VERBS.len()];
    let mut opponent_counts = [0; VERBS.len()];
    let mut my_successful_plants = 0;
    let mut opponent_successful_plants = 0;
    let mut ambiguous_plants = 0;
    let mut max_plants = initial_plants;
    let mut my_command_hash = FNV_OFFSET;
    let mut opponent_command_hash = FNV_OFFSET;

    while game.turn <= 300 {
        let ours = candidate.commands(&game, task.seat);
        let theirs = opponent.commands(&game, 1 - task.seat);
        count_commands(&mut my_counts, &ours);
        count_commands(&mut opponent_counts, &theirs);
        trace_commands(&mut my_command_hash, &ours);
        trace_commands(&mut opponent_command_hash, &theirs);

        let before: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        let our_attempts = plant_attempts(&game, task.seat, &ours);
        let their_attempts = plant_attempts(&game, 1 - task.seat, &theirs);
        apply_commands(&mut game, task.seat, &ours, &theirs);
        let after: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
        for cell in after.difference(&before) {
            match (our_attempts.contains(cell), their_attempts.contains(cell)) {
                (true, false) => my_successful_plants += 1,
                (false, true) => opponent_successful_plants += 1,
                (true, true) => ambiguous_plants += 1,
                (false, false) => {}
            }
        }

        let my_workers = worker_count(&game, task.seat);
        let opponent_workers = worker_count(&game, 1 - task.seat);
        max_my_workers = max_my_workers.max(my_workers);
        max_opponent_workers = max_opponent_workers.max(opponent_workers);
        if first_my_third_worker_turn < 0 && my_workers >= 3 {
            first_my_third_worker_turn = game.turn;
        }
        if first_opponent_third_worker_turn < 0 && opponent_workers >= 3 {
            first_opponent_third_worker_turn = game.turn;
        }
        max_plants = max_plants.max(game.plants.len());
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }

    ResultRow {
        task,
        width,
        height,
        initial_plants,
        final_turn: game.turn,
        margin: game.scores[task.seat] - game.scores[1 - task.seat],
        my_score: game.scores[task.seat],
        opponent_score: game.scores[1 - task.seat],
        my_inventory: game.inventories[task.seat],
        opponent_inventory: game.inventories[1 - task.seat],
        my_workers: worker_count(&game, task.seat),
        opponent_workers: worker_count(&game, 1 - task.seat),
        max_my_workers,
        max_opponent_workers,
        first_my_third_worker_turn,
        first_opponent_third_worker_turn,
        my_counts,
        opponent_counts,
        my_successful_plants,
        opponent_successful_plants,
        ambiguous_plants,
        max_plants,
        terminal_plants: game.plants.len(),
        my_command_hash,
        opponent_command_hash,
    }
}

fn parse_selection(value: &str, catalog: &[(&str, Factory)]) -> Vec<usize> {
    let requested: Vec<_> = value.split(',').filter(|name| !name.is_empty()).collect();
    assert!(!requested.is_empty(), "selection cannot be empty");
    let mut indexes = Vec::new();
    for name in requested {
        let index = catalog
            .iter()
            .position(|(label, _)| *label == name)
            .unwrap_or_else(|| panic!("unknown controller {name}"));
        if !indexes.contains(&index) {
            indexes.push(index);
        }
    }
    indexes
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args.get(1).map_or(9_100_000, |value| {
        value.parse::<i64>().expect("numeric signed seed start")
    });
    let seed_count = args.get(2).map_or(2, |value| {
        value.parse::<usize>().expect("numeric seed count")
    });
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d34-official-architecture-census.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(16, |value| {
            value.parse::<usize>().expect("numeric thread count")
        })
        .clamp(1, 64);
    let candidate_indexes = parse_selection(
        args.get(5).map_or(
            "resident,private2,ownership2,prefruit2,gold_adaptive,separated_denial,hybrid3,accumulate4,norx3",
            String::as_str,
        ),
        &CANDIDATES,
    );
    let opponent_indexes = parse_selection(
        args.get(6).map_or(
            "resident,gold_adaptive,compact_gold,norx_native_three,legend_balanced,mybot,script_boss,silver_boss",
            String::as_str,
        ),
        &OPPONENTS,
    );
    assert!(seed_count > 0, "seed count must be positive");
    seed_start
        .checked_add(seed_count as i64)
        .expect("seed range overflow");

    let tasks: Vec<_> = (0..seed_count)
        .flat_map(|offset| {
            let candidate_indexes = candidate_indexes.clone();
            let opponent_indexes = opponent_indexes.clone();
            (0..2).flat_map(move |seat| {
                let candidate_indexes = candidate_indexes.clone();
                let opponent_indexes = opponent_indexes.clone();
                opponent_indexes
                    .into_iter()
                    .flat_map(move |opponent_index| {
                        let candidate_indexes = candidate_indexes.clone();
                        candidate_indexes
                            .into_iter()
                            .map(move |candidate_index| Task {
                                seed: seed_start + offset as i64,
                                seat,
                                opponent_index,
                                candidate_index,
                            })
                    })
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
                    rows.push(run_task(tasks[index]));
                }
                rows
            })
        })
        .collect();
    let mut rows: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D34 worker thread"))
        .collect();
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.seat,
            row.task.opponent_index,
            row.task.candidate_index,
        )
    });

    let file = File::create(&output).expect("create D34 output");
    let mut writer = BufWriter::new(file);
    let inventory_columns = (0..6)
        .flat_map(|index| [format!("my_inv{index}"), format!("opponent_inv{index}")])
        .collect::<Vec<_>>();
    let command_columns = VERBS
        .iter()
        .flat_map(|verb| {
            let lower = verb.to_ascii_lowercase();
            [format!("my_{lower}"), format!("opponent_{lower}")]
        })
        .collect::<Vec<_>>();
    writeln!(
        writer,
        "seed\tseat\topponent\tcontroller\twidth\theight\tinitial_plants\tfinal_turn\tmargin\tmy_score\topponent_score\t{}\tmy_workers\topponent_workers\tmax_my_workers\tmax_opponent_workers\tfirst_my_third_worker_turn\tfirst_opponent_third_worker_turn\t{}\tmy_successful_plants\topponent_successful_plants\tambiguous_plants\tmax_plants\tterminal_plants\tmy_command_hash\topponent_command_hash",
        inventory_columns.join("\t"),
        command_columns.join("\t"),
    )
    .expect("write D34 header");
    for row in &rows {
        let inventories = (0..6)
            .flat_map(|index| [row.my_inventory[index], row.opponent_inventory[index]])
            .map(|value| value.to_string())
            .collect::<Vec<_>>();
        let commands = (0..VERBS.len())
            .flat_map(|index| [row.my_counts[index], row.opponent_counts[index]])
            .map(|value| value.to_string())
            .collect::<Vec<_>>();
        let mut fields = vec![
            row.task.seed.to_string(),
            row.task.seat.to_string(),
            OPPONENTS[row.task.opponent_index].0.to_string(),
            CANDIDATES[row.task.candidate_index].0.to_string(),
            row.width.to_string(),
            row.height.to_string(),
            row.initial_plants.to_string(),
            row.final_turn.to_string(),
            row.margin.to_string(),
            row.my_score.to_string(),
            row.opponent_score.to_string(),
        ];
        fields.extend(inventories);
        fields.extend([
            row.my_workers.to_string(),
            row.opponent_workers.to_string(),
            row.max_my_workers.to_string(),
            row.max_opponent_workers.to_string(),
            row.first_my_third_worker_turn.to_string(),
            row.first_opponent_third_worker_turn.to_string(),
        ]);
        fields.extend(commands);
        fields.extend([
            row.my_successful_plants.to_string(),
            row.opponent_successful_plants.to_string(),
            row.ambiguous_plants.to_string(),
            row.max_plants.to_string(),
            row.terminal_plants.to_string(),
            row.my_command_hash.to_string(),
            row.opponent_command_hash.to_string(),
        ]);
        writeln!(writer, "{}", fields.join("\t")).expect("write D34 row");
    }
    writer.flush().expect("flush D34 output");
    eprintln!(
        "saved {} rows in {:.3}s to {output}",
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn catalogs_are_unique_and_protocol_complete() {
        let candidate_names: BTreeSet<_> = CANDIDATES.iter().map(|(name, _)| *name).collect();
        let opponent_names: BTreeSet<_> = OPPONENTS.iter().map(|(name, _)| *name).collect();
        assert_eq!(candidate_names.len(), CANDIDATES.len());
        assert_eq!(opponent_names.len(), OPPONENTS.len());
        assert_eq!(parse_selection("resident,norx3", &CANDIDATES), [0, 8]);
        assert_eq!(
            parse_selection("resident,legend_balanced", &OPPONENTS),
            [0, 4]
        );
    }

    #[test]
    fn command_hash_is_repeatable_and_order_sensitive() {
        let commands = vec!["MOVE 0 1 2".to_string(), "CHOP 1".to_string()];
        let mut first = FNV_OFFSET;
        let mut second = FNV_OFFSET;
        trace_commands(&mut first, &commands);
        trace_commands(&mut second, &commands);
        assert_eq!(first, second);
        let mut reversed = FNV_OFFSET;
        trace_commands(
            &mut reversed,
            &commands.into_iter().rev().collect::<Vec<_>>(),
        );
        assert_ne!(first, reversed);
    }

    #[test]
    fn plant_attempts_use_pre_step_unit_positions() {
        let game = generate_official(9_100_000);
        let unit = game.units.iter().find(|unit| unit.player == 0).unwrap();
        let commands = vec![format!("PLANT {} BANANA", unit.id)];
        assert_eq!(
            plant_attempts(&game, 0, &commands),
            BTreeSet::from([unit.pos()])
        );
        assert!(plant_attempts(&game, 1, &commands).is_empty());
    }
}
