//! Closed-loop terminal outcome smoke for a compact complete-economy grammar.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeSet, HashSet};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{has_stalled, step, WOOD};
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

#[derive(Clone, Debug, Eq, PartialEq)]
struct Genome {
    label: String,
    config: GoldEconomyConfig,
}

fn config(
    max_trolls: i32,
    choppers: i32,
    stagger: i32,
    spec1: (i32, i32, i32, i32),
    spec2: (i32, i32, i32, i32),
    planters: i32,
    hold_until: i32,
    farm_cap: usize,
    adaptive: bool,
) -> GoldEconomyConfig {
    GoldEconomyConfig {
        max_trolls,
        choppers,
        stagger,
        spec1,
        spec2,
        planters,
        hold_until,
        farm_cap,
        co_fell: false,
        adaptive,
    }
}

fn genome_catalog() -> Vec<Genome> {
    let default_spec = (2, 2, 0, 2);
    let mut out = Vec::new();
    for spec in [(1, 2, 0, 2), default_spec, (2, 3, 0, 2), (2, 2, 0, 3)] {
        out.push(Genome {
            label: format!("lean_m{}c{}h{}k{}", spec.0, spec.1, spec.2, spec.3),
            config: config(2, 1, 0, spec, default_spec, 0, 0, 12, false),
        });
    }
    for stagger in [20, 60] {
        for harvest_power in [0, 1] {
            for farm_cap in [12, 20] {
                out.push(Genome {
                    label: format!("dual3_s{stagger}_h{harvest_power}_cap{farm_cap}"),
                    config: config(
                        3,
                        2,
                        stagger,
                        default_spec,
                        (2, 2, harvest_power, 2),
                        0,
                        0,
                        farm_cap,
                        false,
                    ),
                });
            }
        }
    }
    for hold_until in [0, 60, 100] {
        for farm_cap in [12, 20] {
            out.push(Genome {
                label: format!("farm3_hold{hold_until}_cap{farm_cap}"),
                config: config(
                    3,
                    1,
                    0,
                    default_spec,
                    default_spec,
                    1,
                    hold_until,
                    farm_cap,
                    false,
                ),
            });
        }
    }
    for stagger in [30, 60] {
        for hold_until in [0, 80, 120] {
            for farm_cap in [18, 24] {
                out.push(Genome {
                    label: format!("farm4_s{stagger}_hold{hold_until}_cap{farm_cap}"),
                    config: config(
                        4,
                        2,
                        stagger,
                        default_spec,
                        default_spec,
                        1,
                        hold_until,
                        farm_cap,
                        false,
                    ),
                });
            }
        }
    }
    out.push(Genome {
        label: "adaptive_density".to_string(),
        config: config(4, 2, 30, default_spec, default_spec, 1, 100, 24, true),
    });
    out
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

#[derive(Clone, Copy, Default)]
struct Actions {
    successful_trains: usize,
    successful_plants: usize,
    harvest: usize,
    chop: usize,
    drop: usize,
    pick: usize,
    mine: usize,
}

fn count_issued(actions: &mut Actions, commands: &[String]) {
    for command in commands {
        match command.split_whitespace().next().unwrap_or("") {
            "HARVEST" => actions.harvest += 1,
            "CHOP" => actions.chop += 1,
            "DROP" => actions.drop += 1,
            "PICK" => actions.pick += 1,
            "MINE" => actions.mine += 1,
            _ => {}
        }
    }
}

fn plant_attempts(
    game: &GameState,
    player: usize,
    commands: &[String],
) -> Vec<((i32, i32), String)> {
    commands
        .iter()
        .filter_map(|command| {
            let fields: Vec<_> = command.split_whitespace().collect();
            if fields.len() < 3 || fields[0] != "PLANT" {
                return None;
            }
            let id: i32 = fields[1].parse().ok()?;
            let unit = game
                .units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)?;
            Some((unit.pos(), fields[2].to_ascii_uppercase()))
        })
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
    divergence_turns: usize,
    actions: Actions,
}

enum CompletePolicy {
    Resident(SecureOrchardBot),
    Farm(GoldElite),
}

impl CompletePolicy {
    fn resident() -> Self {
        Self::Resident(SecureOrchardBot::new())
    }

    fn farm(config: GoldEconomyConfig) -> Self {
        Self::Farm(GoldElite::configured(config))
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::Farm(bot) => bot.decide(game, player),
        }
    }
}

fn play(
    initial: &GameState,
    seat: usize,
    model: usize,
    config: Option<GoldEconomyConfig>,
) -> Outcome {
    let mut game = initial.clone();
    let mut ours = config.map_or_else(CompletePolicy::resident, CompletePolicy::farm);
    let mut resident_shadow = SecureOrchardBot::new();
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    let mut divergence_turns = 0;
    let mut actions = Actions::default();
    while game.turn <= TOTAL_TURNS {
        let reference = resident_shadow.commands(&yamo_view(&game, seat));
        let commands = ours.commands(&game, seat);
        divergence_turns += usize::from(normalized(&reference) != normalized(&commands));
        count_issued(&mut actions, &commands);
        let attempts = plant_attempts(&game, seat, &commands);
        let workers_before = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count();
        let opposition = theirs.decide(&game, 1 - seat);
        if seat == 0 {
            step(&mut game, &commands, &opposition);
        } else {
            step(&mut game, &opposition, &commands);
        }
        let workers_after = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count();
        actions.successful_trains += workers_after.saturating_sub(workers_before);
        for (cell, kind) in attempts {
            if game
                .plants
                .iter()
                .any(|plant| plant.pos() == cell && plant.plant_type == kind)
            {
                actions.successful_plants += 1;
            }
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
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
        divergence_turns,
        actions,
    }
}

fn margin(outcome: Outcome) -> i32 {
    outcome.own_score - outcome.opponent_score
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    model: usize,
}

struct ResultRow {
    task: Task,
    genome: Genome,
    resident: Outcome,
    candidate: Outcome,
}

fn run_task(task: Task, genomes: &[Genome]) -> Vec<ResultRow> {
    let initial = generate_bronze(task.seed);
    let resident = play(&initial, task.seat, task.model, None);
    assert_eq!(resident.divergence_turns, 0, "resident grammar identity");
    genomes
        .iter()
        .cloned()
        .map(|genome| ResultRow {
            task,
            candidate: play(&initial, task.seat, task.model, Some(genome.config)),
            genome,
            resident,
        })
        .collect()
}

fn selected_genomes(value: &str) -> Vec<Genome> {
    let catalog = genome_catalog();
    if value == "all" {
        return catalog;
    }
    let requested: HashSet<_> = value.split(',').filter(|label| !label.is_empty()).collect();
    let selected: Vec<_> = catalog
        .into_iter()
        .filter(|genome| requested.contains(genome.label.as_str()))
        .collect();
    let found: HashSet<_> = selected
        .iter()
        .map(|genome| genome.label.as_str())
        .collect();
    let mut missing: Vec<_> = requested.difference(&found).copied().collect();
    missing.sort_unstable();
    assert!(missing.is_empty(), "unknown genome labels: {missing:?}");
    assert!(!selected.is_empty(), "select at least one genome");
    selected
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
        .unwrap_or_else(|| "complete-economy-search.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(20)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(0);
    let genomes = Arc::new(selected_genomes(args.get(5).map_or("all", String::as_str)));
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
                let genomes = Arc::clone(&genomes);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.extend(run_task(tasks[index], &genomes));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("complete-economy worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.model,
            row.task.seat,
            row.genome.label.clone(),
        )
    });

    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(writer, "seed\tseat\topponent\tgenome\tmax_trolls\tchoppers\tstagger\tspec1_ms\tspec1_cc\tspec1_hp\tspec1_chop\tspec2_ms\tspec2_cc\tspec2_hp\tspec2_chop\tplanters\thold_until\tfarm_cap\tco_fell\tadaptive\tresident_margin\tcandidate_margin\tmargin_delta\tresident_score\tcandidate_score\tscore_delta\tresident_opponent_score\tcandidate_opponent_score\topponent_score_delta\tresident_wood\tcandidate_wood\twood_delta\tresident_opponent_wood\tcandidate_opponent_wood\topponent_wood_delta\tresident_workers\tcandidate_workers\tresident_terminal_turn\tcandidate_terminal_turn\tresident_successful_trains\tcandidate_successful_trains\tresident_successful_plants\tcandidate_successful_plants\tresident_harvest\tcandidate_harvest\tresident_chop\tcandidate_chop\tresident_drop\tcandidate_drop\tresident_pick\tcandidate_pick\tresident_mine\tcandidate_mine\tdivergence_turns\tresident_identity_mismatches").expect("write header");
    for row in rows {
        let cfg = row.genome.config;
        writeln!(writer, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t0", row.task.seed, row.task.seat, OPPONENTS[row.task.model], row.genome.label, cfg.max_trolls, cfg.choppers, cfg.stagger, cfg.spec1.0, cfg.spec1.1, cfg.spec1.2, cfg.spec1.3, cfg.spec2.0, cfg.spec2.1, cfg.spec2.2, cfg.spec2.3, cfg.planters, cfg.hold_until, cfg.farm_cap, usize::from(cfg.co_fell), usize::from(cfg.adaptive), margin(row.resident), margin(row.candidate), margin(row.candidate)-margin(row.resident), row.resident.own_score, row.candidate.own_score, row.candidate.own_score-row.resident.own_score, row.resident.opponent_score, row.candidate.opponent_score, row.candidate.opponent_score-row.resident.opponent_score, row.resident.own_wood, row.candidate.own_wood, row.candidate.own_wood-row.resident.own_wood, row.resident.opponent_wood, row.candidate.opponent_wood, row.candidate.opponent_wood-row.resident.opponent_wood, row.resident.workers, row.candidate.workers, row.resident.terminal_turn, row.candidate.terminal_turn, row.resident.actions.successful_trains, row.candidate.actions.successful_trains, row.resident.actions.successful_plants, row.candidate.actions.successful_plants, row.resident.actions.harvest, row.candidate.actions.harvest, row.resident.actions.chop, row.candidate.actions.chop, row.resident.actions.drop, row.candidate.actions.drop, row.resident.actions.pick, row.candidate.actions.pick, row.resident.actions.mine, row.candidate.actions.mine, row.candidate.divergence_turns).expect("write row");
    }
    eprintln!(
        "saved {} scenarios x {} genomes ({} rows) to {}",
        tasks.len(),
        genomes.len(),
        tasks.len() * genomes.len(),
        output
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_catalog_has_31_unique_labels_and_configs() {
        let catalog = genome_catalog();
        let labels: HashSet<_> = catalog.iter().map(|genome| &genome.label).collect();
        let configs: HashSet<_> = catalog.iter().map(|genome| genome.config).collect();
        assert_eq!(catalog.len(), 31);
        assert_eq!(labels.len(), 31);
        assert_eq!(configs.len(), 31);
    }

    #[test]
    fn resident_genotype_is_exact_on_a_complete_stream() {
        let initial = generate_bronze(0);
        let outcome = play(&initial, 0, 0, None);
        assert_eq!(outcome.divergence_turns, 0);
        assert!(outcome.terminal_turn > 1);
    }
}
