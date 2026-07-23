//! Consumed-seed comparison of resident, b100/e6, and harvest-on-contact residual.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone resident addresses these modules through `crate::`.
pub use yamo::{bot, game};

use std::collections::BTreeSet;
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{has_stalled, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const OPPONENTS: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Policy {
    Resident,
    B100E6,
    HarvestContact,
}

impl Policy {
    fn bot(self) -> SecureOrchardBot {
        match self {
            Self::Resident => SecureOrchardBot::new(),
            Self::B100E6 => SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1),
            Self::HarvestContact => SecureOrchardBot::opponent_crop_harvest_contact(),
        }
    }

    fn shadow(self) -> Option<SecureOrchardBot> {
        match self {
            Self::Resident => None,
            Self::B100E6 => Some(SecureOrchardBot::new()),
            Self::HarvestContact => Some(SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1)),
        }
    }
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
        0 => Box::new(CompactGold::new()),
        1 => Box::new(GoldElite::adaptive()),
        2 => Box::new(GoldElite::new()),
        3 => Box::new(MyBot::new()),
        4 => Box::new(PrinterBot::new()),
        5 => Box::new(SchedBot::new()),
        6 => Box::new(ScriptBoss::new()),
        7 => Box::new(SilverBoss::new()),
        _ => unreachable!(),
    }
}

fn normalized(commands: &[String]) -> Vec<&str> {
    commands
        .iter()
        .map(String::as_str)
        .filter(|command| !command.starts_with("MSG "))
        .collect()
}

#[derive(Clone, Copy)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    own_wood: i32,
    opponent_wood: i32,
    terminal_turn: i32,
    crops_seen: usize,
    crop_priority_selections: usize,
    harvest_rewrites: usize,
    divergence_turns: usize,
    first_divergence_turn: Option<i32>,
}

fn play(initial: &GameState, seat: usize, model: usize, policy: Policy) -> Outcome {
    let mut game = initial.clone();
    let mut ours = policy.bot();
    let mut shadow = policy.shadow();
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    let mut divergence_turns = 0;
    let mut first_divergence_turn = None;
    while game.turn <= TOTAL_TURNS {
        let view = yamo_view(&game, seat);
        let reference = shadow.as_mut().map(|bot| bot.commands(&view));
        let commands = ours.commands(&view);
        if reference
            .as_ref()
            .is_some_and(|reference| normalized(reference) != normalized(&commands))
        {
            divergence_turns += 1;
            first_divergence_turn.get_or_insert(game.turn);
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
    let (crops_seen, crop_priority_selections, _, _) = ours.opponent_crop_telemetry();
    Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        own_wood: game.inventories[seat][WOOD],
        opponent_wood: game.inventories[1 - seat][WOOD],
        terminal_turn: game.turn,
        crops_seen,
        crop_priority_selections,
        harvest_rewrites: ours.opponent_crop_harvest_rewrites(),
        divergence_turns,
        first_divergence_turn,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    model: usize,
}

struct ResultRow {
    task: Task,
    resident: Outcome,
    b100: Outcome,
    harvest: Outcome,
}

fn run_task(task: Task) -> ResultRow {
    let initial = generate_bronze(task.seed);
    ResultRow {
        task,
        resident: play(&initial, task.seat, task.model, Policy::Resident),
        b100: play(&initial, task.seat, task.model, Policy::B100E6),
        harvest: play(&initial, task.seat, task.model, Policy::HarvestContact),
    }
}

fn margin(outcome: Outcome) -> i32 {
    outcome.own_score - outcome.opponent_score
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(60);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "yamo-crop-harvest-contact.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(16)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(1300);
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..OPPONENTS.len())
                .flat_map(move |model| (0..2).map(move |seat| Task { seed, seat, model }))
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.push(run_task(tasks[index]));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("crop-harvest worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.model, row.task.seat));

    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(writer, "seed\tseat\topponent\tresident_margin\tb100_margin\tharvest_margin\tb100_resident_margin_delta\tharvest_resident_margin_delta\tharvest_b100_margin_delta\tresident_score\tb100_score\tharvest_score\tb100_resident_score_delta\tharvest_resident_score_delta\tharvest_b100_score_delta\tresident_opponent_score\tb100_opponent_score\tharvest_opponent_score\tb100_resident_opponent_score_delta\tharvest_resident_opponent_score_delta\tharvest_b100_opponent_score_delta\tresident_wood\tb100_wood\tharvest_wood\tb100_resident_wood_delta\tharvest_resident_wood_delta\tharvest_b100_wood_delta\tresident_opponent_wood\tb100_opponent_wood\tharvest_opponent_wood\tb100_resident_opponent_wood_delta\tharvest_resident_opponent_wood_delta\tharvest_b100_opponent_wood_delta\tresident_terminal_turn\tb100_terminal_turn\tharvest_terminal_turn\tb100_crops_seen\tb100_priority_selections\tb100_resident_divergence_turns\tb100_resident_first_divergence_turn\tharvest_crops_seen\tharvest_priority_selections\tharvest_rewrites\tharvest_b100_divergence_turns\tharvest_b100_first_divergence_turn").expect("write header");
    let mut active = 0usize;
    let mut rewrites = 0usize;
    for row in rows {
        active += usize::from(row.harvest.divergence_turns > 0);
        rewrites += row.harvest.harvest_rewrites;
        writeln!(writer, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", row.task.seed, row.task.seat, OPPONENTS[row.task.model], margin(row.resident), margin(row.b100), margin(row.harvest), margin(row.b100)-margin(row.resident), margin(row.harvest)-margin(row.resident), margin(row.harvest)-margin(row.b100), row.resident.own_score, row.b100.own_score, row.harvest.own_score, row.b100.own_score-row.resident.own_score, row.harvest.own_score-row.resident.own_score, row.harvest.own_score-row.b100.own_score, row.resident.opponent_score, row.b100.opponent_score, row.harvest.opponent_score, row.b100.opponent_score-row.resident.opponent_score, row.harvest.opponent_score-row.resident.opponent_score, row.harvest.opponent_score-row.b100.opponent_score, row.resident.own_wood, row.b100.own_wood, row.harvest.own_wood, row.b100.own_wood-row.resident.own_wood, row.harvest.own_wood-row.resident.own_wood, row.harvest.own_wood-row.b100.own_wood, row.resident.opponent_wood, row.b100.opponent_wood, row.harvest.opponent_wood, row.b100.opponent_wood-row.resident.opponent_wood, row.harvest.opponent_wood-row.resident.opponent_wood, row.harvest.opponent_wood-row.b100.opponent_wood, row.resident.terminal_turn, row.b100.terminal_turn, row.harvest.terminal_turn, row.b100.crops_seen, row.b100.crop_priority_selections, row.b100.divergence_turns, row.b100.first_divergence_turn.unwrap_or(-1), row.harvest.crops_seen, row.harvest.crop_priority_selections, row.harvest.harvest_rewrites, row.harvest.divergence_turns, row.harvest.first_divergence_turn.unwrap_or(-1)).expect("write row");
    }
    eprintln!(
        "saved {} scenarios; {} harvest-active cells and {} rewrites to {}",
        tasks.len(),
        active,
        rewrites,
        output
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn contact_views() -> (YamoState, YamoState) {
        let mut initial = YamoState::empty(5, 3);
        initial.walkable = BTreeSet::from([(1, 1), (2, 1), (3, 1)]);
        initial.shacks = [(0, 1), (4, 1)];
        initial.units = vec![
            Unit {
                id: 0,
                player: 0,
                cell: (1, 1),
                stats: Stats::STARTER_GOLD,
                carry: [0; 6],
            },
            Unit {
                id: 1,
                player: 0,
                cell: (2, 1),
                stats: Stats {
                    movement_speed: 1,
                    carry_capacity: 1,
                    harvest_power: 0,
                    chop_power: 1,
                },
                carry: [0; 6],
            },
        ];
        let mut ripe = initial.clone();
        ripe.turn = 2;
        ripe.plants.push(Plant {
            kind: PlantKind::Banana,
            cell: (1, 1),
            size: 2,
            health: 4,
            fruits: 1,
            cooldown: 2,
        });
        (initial, ripe)
    }

    #[test]
    fn harvest_contact_rewrites_only_the_first_selected_chop() {
        let (initial, ripe) = contact_views();
        let mut b100 = SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1);
        let mut harvest = SecureOrchardBot::opponent_crop_harvest_contact();
        b100.commands(&initial);
        harvest.commands(&initial);
        let b100_commands = b100.commands(&ripe);
        let harvest_commands = harvest.commands(&ripe);
        assert!(normalized(&b100_commands).contains(&"CHOP 0"));
        assert!(normalized(&harvest_commands).contains(&"HARVEST 0"));
        assert_eq!(harvest.opponent_crop_harvest_rewrites(), 1);
        let repeated = harvest.commands(&ripe);
        assert!(!normalized(&repeated).contains(&"HARVEST 0"));
        assert_eq!(harvest.opponent_crop_harvest_rewrites(), 1);
    }
}
