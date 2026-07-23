//! Research-only provenance-aware opponent-crop priority sweep.

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
struct Profile {
    label: &'static str,
    bonus: i32,
    eta_limit: i32,
    start_turn: i32,
    minimum_seen: usize,
}

const PROFILES: [Profile; 11] = [
    Profile {
        label: "dual_value_e6",
        bonus: 0,
        eta_limit: 6,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b100_e6",
        bonus: 100,
        eta_limit: 6,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b250_e6",
        bonus: 250,
        eta_limit: 6,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b500_e6",
        bonus: 500,
        eta_limit: 6,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b250_e10",
        bonus: 250,
        eta_limit: 10,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b500_e10",
        bonus: 500,
        eta_limit: 10,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b1000_e10",
        bonus: 1000,
        eta_limit: 10,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b250_e20",
        bonus: 250,
        eta_limit: 20,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b500_e20",
        bonus: 500,
        eta_limit: 20,
        start_turn: 1,
        minimum_seen: 1,
    },
    Profile {
        label: "b500_e10_t50_s4",
        bonus: 500,
        eta_limit: 10,
        start_turn: 50,
        minimum_seen: 4,
    },
    Profile {
        label: "b500_e10_t75_s8",
        bonus: 500,
        eta_limit: 10,
        start_turn: 75,
        minimum_seen: 8,
    },
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
    workers: usize,
    terminal_turn: i32,
    crops_seen: usize,
    crop_priority_selections: usize,
    first_crop_priority_turn: Option<i32>,
    crops_alive: usize,
    divergence_turns: usize,
    first_divergence_turn: Option<i32>,
}

fn play(initial: &GameState, seat: usize, model: usize, profile: Option<Profile>) -> Outcome {
    let mut game = initial.clone();
    let mut ours = profile.map_or_else(SecureOrchardBot::new, |profile| {
        if profile.label == "dual_value_e6" {
            SecureOrchardBot::opponent_crop_dual_value_e6()
        } else {
            SecureOrchardBot::opponent_crop_priority(
                profile.bonus,
                profile.eta_limit,
                profile.start_turn,
                profile.minimum_seen,
            )
        }
    });
    let mut shadow = profile.map(|_| SecureOrchardBot::new());
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    let mut divergence_turns = 0;
    let mut first_divergence_turn = None;
    while game.turn <= TOTAL_TURNS {
        let view = yamo_view(&game, seat);
        let baseline = shadow.as_mut().map(|shadow| shadow.commands(&view));
        let commands = ours.commands(&view);
        if baseline
            .as_ref()
            .is_some_and(|baseline| normalized(baseline) != normalized(&commands))
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
    let (crops_seen, crop_priority_selections, first_crop_priority_turn, crops_alive) =
        ours.opponent_crop_telemetry();
    Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        own_wood: game.inventories[seat][WOOD],
        opponent_wood: game.inventories[1 - seat][WOOD],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        terminal_turn: game.turn,
        crops_seen,
        crop_priority_selections,
        first_crop_priority_turn,
        crops_alive,
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
    control: Outcome,
    profile: Profile,
    candidate: Outcome,
}

fn run_task(task: Task, profiles: &[Profile]) -> Vec<ResultRow> {
    let initial = generate_bronze(task.seed);
    let control = play(&initial, task.seat, task.model, None);
    profiles
        .iter()
        .copied()
        .map(|profile| ResultRow {
            task,
            control,
            profile,
            candidate: play(&initial, task.seat, task.model, Some(profile)),
        })
        .collect()
}

fn requested_profiles(label: &str) -> Vec<Profile> {
    if label == "all" {
        return PROFILES.to_vec();
    }
    label
        .split(',')
        .map(|requested| {
            *PROFILES
                .iter()
                .find(|profile| profile.label == requested)
                .unwrap_or_else(|| panic!("unknown profile {requested}"))
        })
        .collect()
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(30);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "yamo-crop-priority.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(16)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(1300);
    let profiles = requested_profiles(args.get(5).map_or("all", String::as_str));
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..OPPONENTS.len())
                .flat_map(move |model| (0..2).map(move |seat| Task { seed, seat, model }))
        })
        .collect();
    let tasks = Arc::new(tasks);
    let profiles = Arc::new(profiles);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let profiles = Arc::clone(&profiles);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.extend(run_task(tasks[index], &profiles));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("crop-priority worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.model,
            row.task.seat,
            row.profile.label,
        )
    });
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(writer, "seed\tseat\topponent\tprofile\tbonus\teta_limit\tstart_turn\tminimum_seen\tcontrol_margin\tcandidate_margin\tmargin_delta\tcontrol_score\tcandidate_score\tscore_delta\tcontrol_opponent_score\tcandidate_opponent_score\topponent_score_delta\tcontrol_wood\tcandidate_wood\twood_delta\tcontrol_opponent_wood\tcandidate_opponent_wood\topponent_wood_delta\tcontrol_workers\tcandidate_workers\tcontrol_terminal_turn\tcandidate_terminal_turn\tcrops_seen\tcrop_priority_selections\tfirst_crop_priority_turn\tcrops_alive\tdivergence_turns\tfirst_divergence_turn").expect("write header");
    let mut active = 0usize;
    for row in rows {
        let control_margin = row.control.own_score - row.control.opponent_score;
        let candidate_margin = row.candidate.own_score - row.candidate.opponent_score;
        active += usize::from(row.candidate.divergence_turns > 0);
        writeln!(writer, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", row.task.seed, row.task.seat, OPPONENTS[row.task.model], row.profile.label, row.profile.bonus, row.profile.eta_limit, row.profile.start_turn, row.profile.minimum_seen, control_margin, candidate_margin, candidate_margin-control_margin, row.control.own_score, row.candidate.own_score, row.candidate.own_score-row.control.own_score, row.control.opponent_score, row.candidate.opponent_score, row.candidate.opponent_score-row.control.opponent_score, row.control.own_wood, row.candidate.own_wood, row.candidate.own_wood-row.control.own_wood, row.control.opponent_wood, row.candidate.opponent_wood, row.candidate.opponent_wood-row.control.opponent_wood, row.control.workers, row.candidate.workers, row.control.terminal_turn, row.candidate.terminal_turn, row.candidate.crops_seen, row.candidate.crop_priority_selections, row.candidate.first_crop_priority_turn.map_or(-1, |turn| turn), row.candidate.crops_alive, row.candidate.divergence_turns, row.candidate.first_divergence_turn.map_or(-1, |turn| turn)).expect("write row");
    }
    eprintln!(
        "saved {} scenarios x {} profiles; {} active profile-cells to {}",
        tasks.len(),
        profiles.len(),
        active,
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_profile_catalog_is_unique_and_complete() {
        let labels: BTreeSet<_> = PROFILES.iter().map(|profile| profile.label).collect();
        assert_eq!(PROFILES.len(), 11);
        assert_eq!(labels.len(), PROFILES.len());
    }

    #[test]
    fn profiles_preserve_turn_one_commands() {
        let game = generate_bronze(1300);
        for profile in PROFILES {
            let view = yamo_view(&game, 0);
            let mut control = SecureOrchardBot::new();
            let mut candidate = if profile.label == "dual_value_e6" {
                SecureOrchardBot::opponent_crop_dual_value_e6()
            } else {
                SecureOrchardBot::opponent_crop_priority(
                    profile.bonus,
                    profile.eta_limit,
                    profile.start_turn,
                    profile.minimum_seen,
                )
            };
            assert_eq!(
                normalized(&control.commands(&view)),
                normalized(&candidate.commands(&view)),
                "{}",
                profile.label,
            );
        }
    }
}
