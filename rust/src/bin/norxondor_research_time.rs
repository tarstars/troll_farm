//! Paired local league for the replay-derived workforce ladder research wrappers.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone resident addresses its modules through `crate::`; re-exporting preserves those
// paths when it is nested in this benchmark binary.
pub use yamo::{bot, game};

use std::cell::RefCell;
use std::collections::BTreeSet;
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::norxondor_research::{
    NorxondorCompact, NorxondorCooperativeSilver, NorxondorFundedSilver, NorxondorSilver,
    NorxondorSoftCooperativeSilver, NorxondorThreeWorkerSilver,
};
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
fn norx_compact() -> Box<dyn Strategy> {
    Box::new(NorxondorCompact::new())
}
fn silver() -> Box<dyn Strategy> {
    Box::new(SilverBoss::new())
}
fn norx_silver() -> Box<dyn Strategy> {
    Box::new(NorxondorSilver::new())
}
fn norx_funded_silver() -> Box<dyn Strategy> {
    Box::new(NorxondorFundedSilver::new())
}
fn norx_cooperative_silver() -> Box<dyn Strategy> {
    Box::new(NorxondorCooperativeSilver::new())
}
fn norx_soft_cooperative_silver() -> Box<dyn Strategy> {
    Box::new(NorxondorSoftCooperativeSilver::new())
}
fn norx_three_worker_silver() -> Box<dyn Strategy> {
    Box::new(NorxondorThreeWorkerSilver::new())
}
fn norx_native_three() -> Box<dyn Strategy> {
    Box::new(NorxondorNative::new(true))
}
fn norx_native_full() -> Box<dyn Strategy> {
    Box::new(NorxondorNative::new(false))
}

fn yamo_view(game: &troll_farm::game::state::GameState, player: usize) -> YamoState {
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

struct ResidentAdapter {
    bot: RefCell<SecureOrchardBot>,
}

impl ResidentAdapter {
    fn new() -> Self {
        Self {
            bot: RefCell::new(SecureOrchardBot::new()),
        }
    }
}

impl Strategy for ResidentAdapter {
    fn name(&self) -> &str {
        "resident"
    }

    fn decide(&self, game: &troll_farm::game::state::GameState, player: usize) -> Vec<String> {
        self.bot.borrow_mut().commands(&yamo_view(game, player))
    }
}

fn resident() -> Box<dyn Strategy> {
    Box::new(ResidentAdapter::new())
}
fn norx_resident_challenge() -> Box<dyn Strategy> {
    Box::new(NorxondorCooperativeSilver::new())
}
fn norx_soft_resident_challenge() -> Box<dyn Strategy> {
    Box::new(NorxondorSoftCooperativeSilver::new())
}
fn norx_three_worker_resident_challenge() -> Box<dyn Strategy> {
    Box::new(NorxondorThreeWorkerSilver::new())
}

struct NorxondorSignaturePortfolio {
    resident: RefCell<SecureOrchardBot>,
    alternative: NorxondorThreeWorkerSilver,
    use_alternative: RefCell<Option<bool>>,
}

fn safe_signature(turn: i32, spec: (i32, i32, i32, i32)) -> bool {
    let early = turn <= 4;
    let middle = (5..=30).contains(&turn);
    let late = (31..=60).contains(&turn);
    (early && spec == (2, 2, 2, 1))
        || (middle && spec == (2, 2, 0, 2))
        || (late && spec == (1, 1, 1, 0))
}

impl NorxondorSignaturePortfolio {
    fn new() -> Self {
        Self {
            resident: RefCell::new(SecureOrchardBot::new()),
            alternative: NorxondorThreeWorkerSilver::new(),
            use_alternative: RefCell::new(None),
        }
    }
}

impl Strategy for NorxondorSignaturePortfolio {
    fn name(&self) -> &str {
        "norx_signature_portfolio"
    }

    fn decide(&self, game: &troll_farm::game::state::GameState, player: usize) -> Vec<String> {
        if self.use_alternative.borrow().is_none() {
            let newest_opponent = game
                .units
                .iter()
                .filter(|unit| unit.player as usize == 1 - player)
                .max_by_key(|unit| unit.id);
            if game
                .units
                .iter()
                .filter(|unit| unit.player as usize == 1 - player)
                .count()
                > 1
            {
                let selected = newest_opponent.is_some_and(|unit| {
                    safe_signature(game.turn, (unit.ms, unit.cc, unit.hp, unit.chop))
                });
                *self.use_alternative.borrow_mut() = Some(selected);
            }
        }
        if *self.use_alternative.borrow() == Some(true) {
            self.alternative.decide(game, player)
        } else {
            self.resident
                .borrow_mut()
                .commands(&yamo_view(game, player))
        }
    }
}

fn norx_signature_portfolio() -> Box<dyn Strategy> {
    Box::new(NorxondorSignaturePortfolio::new())
}
fn gold() -> Box<dyn Strategy> {
    Box::new(GoldElite::new())
}
fn gold_adaptive() -> Box<dyn Strategy> {
    Box::new(GoldElite::adaptive())
}
fn sched() -> Box<dyn Strategy> {
    Box::new(SchedBot::new())
}
fn mybot() -> Box<dyn Strategy> {
    Box::new(MyBot::new())
}
fn printer() -> Box<dyn Strategy> {
    Box::new(PrinterBot::new())
}
fn script() -> Box<dyn Strategy> {
    Box::new(ScriptBoss::new())
}

const CANDIDATES: [(&str, Factory); 15] = [
    ("compact_gold", compact),
    ("norx_compact", norx_compact),
    ("silver_boss", silver),
    ("norx_silver", norx_silver),
    ("norx_funded_silver", norx_funded_silver),
    ("norx_cooperative_silver", norx_cooperative_silver),
    ("resident", resident),
    ("norx_resident_challenge", norx_resident_challenge),
    ("norx_soft_cooperative_silver", norx_soft_cooperative_silver),
    ("norx_soft_resident_challenge", norx_soft_resident_challenge),
    ("norx_three_worker_silver", norx_three_worker_silver),
    (
        "norx_three_worker_resident_challenge",
        norx_three_worker_resident_challenge,
    ),
    ("norx_signature_portfolio", norx_signature_portfolio),
    ("norx_native_three", norx_native_three),
    ("norx_native_full", norx_native_full),
];
const OPPONENTS: [(&str, Factory); 8] = [
    ("gold_elite", gold),
    ("gold_adaptive", gold_adaptive),
    ("sched_bot", sched),
    ("mybot", mybot),
    ("silver_boss", silver),
    ("printer_bot", printer),
    ("script_boss", script),
    ("compact_gold", compact),
];

#[derive(Clone, Copy)]
struct Task {
    candidate: usize,
    opponent: usize,
    seed: u64,
    seat: usize,
}

struct ResultRow {
    task: Task,
    margin: i32,
    score: i32,
    opponent_score: i32,
    wood: i32,
    workers: usize,
    train_attempts: i32,
    turn: i32,
    candidate_second_worker_turn: i32,
    candidate_third_worker_turn: i32,
    opponent_second_worker_turn: i32,
    opponent_second_ms: i32,
    opponent_second_cc: i32,
    opponent_second_hp: i32,
    opponent_second_chop: i32,
    moves: i32,
    harvests: i32,
    plants: i32,
    chops: i32,
    picks: i32,
    drops: i32,
    mines: i32,
    final_plum: i32,
    final_lemon: i32,
    final_apple: i32,
    final_iron: i32,
}

fn play(task: Task) -> ResultRow {
    let mut game = generate_bronze(task.seed);
    let candidate = CANDIDATES[task.candidate].1();
    let opponent = OPPONENTS[task.opponent].1();
    let mut train_attempts = 0;
    let mut turns_until_end = 0;
    let mut known_candidate_ids: BTreeSet<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == task.seat)
        .map(|unit| unit.id)
        .collect();
    let mut known_opponent_ids: BTreeSet<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == 1 - task.seat)
        .map(|unit| unit.id)
        .collect();
    let mut candidate_train_turns = Vec::new();
    let mut opponent_second = None;
    let mut action_counts = [0; 7];
    for _ in 0..300 {
        let candidate_commands = candidate.decide(&game, task.seat);
        train_attempts += candidate_commands
            .iter()
            .filter(|command| command.starts_with("TRAIN "))
            .count() as i32;
        for command in &candidate_commands {
            let index = match command.split_whitespace().next() {
                Some("MOVE") => Some(0),
                Some("HARVEST") => Some(1),
                Some("PLANT") => Some(2),
                Some("CHOP") => Some(3),
                Some("PICK") => Some(4),
                Some("DROP") => Some(5),
                Some("MINE") => Some(6),
                _ => None,
            };
            if let Some(index) = index {
                action_counts[index] += 1;
            }
        }
        let opponent_commands = opponent.decide(&game, 1 - task.seat);
        if task.seat == 0 {
            step(&mut game, &candidate_commands, &opponent_commands);
        } else {
            step(&mut game, &opponent_commands, &candidate_commands);
        }
        let mut new_candidate_units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| {
                unit.player as usize == task.seat && !known_candidate_ids.contains(&unit.id)
            })
            .collect();
        new_candidate_units.sort_by_key(|unit| unit.id);
        for unit in new_candidate_units {
            candidate_train_turns.push(game.turn);
            known_candidate_ids.insert(unit.id);
        }
        let mut new_opponent_units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| {
                unit.player as usize == 1 - task.seat && !known_opponent_ids.contains(&unit.id)
            })
            .collect();
        new_opponent_units.sort_by_key(|unit| unit.id);
        for unit in new_opponent_units {
            if opponent_second.is_none() {
                opponent_second = Some((game.turn, unit.ms, unit.cc, unit.hp, unit.chop));
            }
            known_opponent_ids.insert(unit.id);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    let score = game.scores[task.seat];
    let opponent_score = game.scores[1 - task.seat];
    ResultRow {
        task,
        margin: score - opponent_score,
        score,
        opponent_score,
        wood: game.inventories[task.seat][5],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == task.seat)
            .count(),
        train_attempts,
        turn: game.turn,
        candidate_second_worker_turn: candidate_train_turns.first().copied().unwrap_or(-1),
        candidate_third_worker_turn: candidate_train_turns.get(1).copied().unwrap_or(-1),
        opponent_second_worker_turn: opponent_second.map_or(-1, |event| event.0),
        opponent_second_ms: opponent_second.map_or(-1, |event| event.1),
        opponent_second_cc: opponent_second.map_or(-1, |event| event.2),
        opponent_second_hp: opponent_second.map_or(-1, |event| event.3),
        opponent_second_chop: opponent_second.map_or(-1, |event| event.4),
        moves: action_counts[0],
        harvests: action_counts[1],
        plants: action_counts[2],
        chops: action_counts[3],
        picks: action_counts[4],
        drops: action_counts[5],
        mines: action_counts[6],
        final_plum: game.inventories[task.seat][0],
        final_lemon: game.inventories[task.seat][1],
        final_apple: game.inventories[task.seat][2],
        final_iron: game.inventories[task.seat][4],
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(200);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "norxondor-research-rollouts.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(0);
    let selected_candidates: Vec<_> = args.get(5).map_or_else(
        || (0..CANDIDATES.len()).collect(),
        |value| {
            value
                .split(',')
                .map(|name| {
                    CANDIDATES
                        .iter()
                        .position(|(candidate, _)| *candidate == name)
                        .unwrap_or_else(|| panic!("unknown candidate {name}"))
                })
                .collect()
        },
    );

    let mut tasks = Vec::new();
    for candidate in selected_candidates {
        for opponent in 0..OPPONENTS.len() {
            for seed in seed_start..seed_start + seeds {
                for seat in 0..2 {
                    tasks.push(Task {
                        candidate,
                        opponent,
                        seed,
                        seat,
                    });
                }
            }
        }
    }
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(play(tasks[index]));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("rollout worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| {
        (
            row.task.candidate,
            row.task.opponent,
            row.task.seed,
            row.task.seat,
        )
    });

    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(
        writer,
        "candidate\topponent\tseed\tseat\tmargin\tscore\topponent_score\twood\tworkers\ttrain_attempts\tturn\tcandidate_second_worker_turn\tcandidate_third_worker_turn\topponent_second_worker_turn\topponent_second_ms\topponent_second_cc\topponent_second_hp\topponent_second_chop\tmoves\tharvests\tplants\tchops\tpicks\tdrops\tmines\tfinal_plum\tfinal_lemon\tfinal_apple\tfinal_iron"
    )
    .expect("write header");
    for row in &rows {
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            CANDIDATES[row.task.candidate].0,
            OPPONENTS[row.task.opponent].0,
            row.task.seed,
            row.task.seat,
            row.margin,
            row.score,
            row.opponent_score,
            row.wood,
            row.workers,
            row.train_attempts,
            row.turn,
            row.candidate_second_worker_turn,
            row.candidate_third_worker_turn,
            row.opponent_second_worker_turn,
            row.opponent_second_ms,
            row.opponent_second_cc,
            row.opponent_second_hp,
            row.opponent_second_chop,
            row.moves,
            row.harvests,
            row.plants,
            row.chops,
            row.picks,
            row.drops,
            row.mines,
            row.final_plum,
            row.final_lemon,
            row.final_apple,
            row.final_iron,
        )
        .expect("write row");
    }
    eprintln!(
        "saved {} paired rollout rows ({} threads) to {}",
        rows.len(),
        threads,
        output
    );
}

#[cfg(test)]
mod tests {
    use super::safe_signature;

    #[test]
    fn frozen_signature_boundaries_are_exact() {
        assert!(safe_signature(4, (2, 2, 2, 1)));
        assert!(safe_signature(5, (2, 2, 0, 2)));
        assert!(safe_signature(30, (2, 2, 0, 2)));
        assert!(safe_signature(31, (1, 1, 1, 0)));
        assert!(safe_signature(60, (1, 1, 1, 0)));
        assert!(!safe_signature(3, (2, 2, 0, 2)));
        assert!(!safe_signature(61, (1, 1, 1, 0)));
    }
}
