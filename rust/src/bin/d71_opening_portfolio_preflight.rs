//! Run D71's deterministic closed-loop opening-portfolio mechanics panels.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::time::Instant;

use rayon::prelude::*;

use troll_farm::rl_macro::{MacroDecisionStage, MacroOpponentMode, MacroTerminal};
use troll_farm::rl_opening_portfolio::{
    OpeningPortfolioEnv, OpeningPortfolioMemory, OPENING_PORTFOLIO_ACTIONS,
};

const ANCHOR_SEED: i64 = 9_801_000;
const GRID_SEED: i64 = 9_803_000;
const GRID_MAPS: usize = 32;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Probe {
    Balanced,
    Seed(usize),
    Cyclic,
}

impl Probe {
    const ALL: [Self; 6] = [
        Self::Balanced,
        Self::Seed(0),
        Self::Seed(1),
        Self::Seed(2),
        Self::Seed(3),
        Self::Cyclic,
    ];

    fn label(self) -> &'static str {
        match self {
            Self::Balanced => "balanced",
            Self::Seed(0) => "seed_plum",
            Self::Seed(1) => "seed_lemon",
            Self::Seed(2) => "seed_apple",
            Self::Seed(3) => "seed_banana",
            Self::Seed(_) => unreachable!(),
            Self::Cyclic => "cyclic",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug)]
struct Telemetry {
    boundary_decisions: u32,
    action_counts: [u32; OPENING_PORTFOLIO_ACTIONS],
    pre_crop_boundaries: u32,
    pre_crop_two_seed_legal: u32,
    repeated_source_attempts: u32,
    source_attempts_after_death: u32,
    in_flight_boundaries: u32,
    finite_feature_failures: u32,
    legal_mask_failures: u32,
    source_assignment_failures: u32,
    boundary_failures: u32,
    reward_identity_error: f32,
}

impl Default for Telemetry {
    fn default() -> Self {
        Self {
            boundary_decisions: 0,
            action_counts: [0; OPENING_PORTFOLIO_ACTIONS],
            pre_crop_boundaries: 0,
            pre_crop_two_seed_legal: 0,
            repeated_source_attempts: 0,
            source_attempts_after_death: 0,
            in_flight_boundaries: 0,
            finite_feature_failures: 0,
            legal_mask_failures: 0,
            source_assignment_failures: 0,
            boundary_failures: 0,
            reward_identity_error: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
struct Row {
    probe: Probe,
    task: Task,
    terminal: MacroTerminal,
    memory: OpeningPortfolioMemory,
    telemetry: Telemetry,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn task(seed_base: i64, task_index: usize) -> Task {
    let opponents = MacroOpponentMode::ALL.len();
    let per_map = 2 * opponents;
    let within = task_index % per_map;
    Task {
        map_seed: seed_base + (task_index / per_map) as i64,
        seat: within / opponents,
        opponent: within % opponents,
    }
}

fn source_attempt_total(memory: OpeningPortfolioMemory) -> u16 {
    memory.source_attempts.iter().copied().sum()
}

fn choose_action(
    probe: Probe,
    mask: &[u8; OPENING_PORTFOLIO_ACTIONS],
    memory: OpeningPortfolioMemory,
    decision: u32,
) -> usize {
    match probe {
        Probe::Balanced => 0,
        Probe::Seed(kind) => {
            if memory.source_attempts[kind] < 4 && mask[4 + kind] == 1 {
                4 + kind
            } else {
                0
            }
        }
        Probe::Cyclic => {
            let attempts = source_attempt_total(memory) as usize;
            if attempts < 6 {
                for offset in 0..4 {
                    let kind = (attempts + offset) % 4;
                    if mask[4 + kind] == 1 {
                        return 4 + kind;
                    }
                }
            }
            for offset in 0..4 {
                let action = (decision as usize + offset) % 4;
                if mask[action] == 1 {
                    return action;
                }
            }
            unreachable!("balanced must remain legal")
        }
    }
}

fn play(probe: Probe, task: Task) -> Row {
    let mut env = OpeningPortfolioEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut telemetry = Telemetry::default();
    let terminal = loop {
        telemetry.boundary_decisions = telemetry.boundary_decisions.saturating_add(1);
        assert!(
            telemetry.boundary_decisions <= 5_000,
            "D71 decision loop on {probe:?} {task:?}"
        );
        let features = env.features();
        telemetry.finite_feature_failures = telemetry
            .finite_feature_failures
            .saturating_add(u32::from(features.iter().any(|value| !value.is_finite())));
        let mask = env.legal_mask();
        let memory = env.memory();
        let own_created =
            u32::from(memory.ended_own_generations) + u32::from(memory.live_own_generations);
        if own_created == 0 {
            telemetry.pre_crop_boundaries = telemetry.pre_crop_boundaries.saturating_add(1);
            telemetry.pre_crop_two_seed_legal = telemetry.pre_crop_two_seed_legal.saturating_add(
                u32::from(mask[4..].iter().filter(|value| **value == 1).count() >= 2),
            );
            telemetry.legal_mask_failures = telemetry
                .legal_mask_failures
                .saturating_add(u32::from(mask[1..4] != [0, 0, 0]));
        }
        telemetry.legal_mask_failures = telemetry
            .legal_mask_failures
            .saturating_add(u32::from(mask[0] != 1));
        telemetry.in_flight_boundaries = telemetry
            .in_flight_boundaries
            .saturating_add(u32::from(memory.source_in_flight));
        let action = choose_action(probe, &mask, memory, telemetry.boundary_decisions - 1);
        telemetry.legal_mask_failures = telemetry
            .legal_mask_failures
            .saturating_add(u32::from(mask[action] != 1));
        telemetry.action_counts[action] = telemetry.action_counts[action].saturating_add(1);
        if action >= 4 {
            telemetry.repeated_source_attempts = telemetry
                .repeated_source_attempts
                .saturating_add(u32::from(source_attempt_total(memory) > 0));
            telemetry.source_attempts_after_death = telemetry
                .source_attempts_after_death
                .saturating_add(u32::from(memory.ended_own_generations > 0));
        }
        let result = env.step(action);
        telemetry.source_assignment_failures = telemetry
            .source_assignment_failures
            .saturating_add(u32::from(action >= 4 && !result.source_assigned));
        telemetry.boundary_failures = telemetry.boundary_failures.saturating_add(u32::from(
            !result.terminal.done && env.batch.macro_env.stage() != MacroDecisionStage::Train,
        ));
        if result.terminal.done {
            break result.terminal;
        }
    };
    telemetry.reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Row {
        probe,
        task,
        terminal,
        memory: env.memory(),
        telemetry,
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        4,
        "usage: d71_opening_portfolio_preflight anchor|grid OUTPUT THREADS"
    );
    let panel = args[1].as_str();
    let output = &args[2];
    let threads: usize = parse(&args[3], "threads");
    assert!((1..=64).contains(&threads));
    let work: Vec<_> = match panel {
        "anchor" => (0..16)
            .map(|index| (Probe::Balanced, task(ANCHOR_SEED, index)))
            .collect(),
        "grid" => Probe::ALL
            .into_iter()
            .flat_map(|probe| {
                (0..GRID_MAPS * 2 * MacroOpponentMode::ALL.len())
                    .map(move |index| (probe, task(GRID_SEED, index)))
            })
            .collect(),
        other => panic!("unknown D71 panel {other:?}"),
    };
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .expect("build D71 thread pool");
    let started = Instant::now();
    let mut rows: Vec<_> = pool.install(|| {
        work.into_par_iter()
            .map(|(probe, task)| play(probe, task))
            .collect()
    });
    rows.sort_by_key(|row| (row.probe, row.task));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D71 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "probe\tmap_seed\tseat\topponent\tturn\town_score\topponent_score\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\town_owned_crop_harvest_units\town_reinvested_crops\taction_hash\tstate_hash\tboundary_decisions\taction_balanced\taction_harvest\taction_renew\taction_fell\taction_seed_plum\taction_seed_lemon\taction_seed_apple\taction_seed_banana\tattempt_plum\tattempt_lemon\tattempt_apple\tattempt_banana\tcreated_plum\tcreated_lemon\tcreated_apple\tcreated_banana\trenewable_receipts\tended_own_generations\treinvested_generations\tlive_own_generations\trepeated_source_attempts\tsource_attempts_after_death\tin_flight_boundaries\tpre_crop_boundaries\tpre_crop_two_seed_legal\tfinite_feature_failures\tlegal_mask_failures\tsource_assignment_failures\tboundary_failures\treward_identity_error").expect("write D71 header");
    for row in &rows {
        let terminal = row.terminal;
        let memory = row.memory;
        let telemetry = row.telemetry;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}",
            row.probe.label(),
            row.task.map_seed,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.own_owned_crop_harvest_units,
            terminal.own_reinvested_crops,
            terminal.action_hash,
            terminal.state_hash,
            telemetry.boundary_decisions,
            telemetry.action_counts[0],
            telemetry.action_counts[1],
            telemetry.action_counts[2],
            telemetry.action_counts[3],
            telemetry.action_counts[4],
            telemetry.action_counts[5],
            telemetry.action_counts[6],
            telemetry.action_counts[7],
            memory.source_attempts[0],
            memory.source_attempts[1],
            memory.source_attempts[2],
            memory.source_attempts[3],
            memory.source_creations[0],
            memory.source_creations[1],
            memory.source_creations[2],
            memory.source_creations[3],
            memory.renewable_receipts,
            memory.ended_own_generations,
            memory.reinvested_generations,
            memory.live_own_generations,
            telemetry.repeated_source_attempts,
            telemetry.source_attempts_after_death,
            telemetry.in_flight_boundaries,
            telemetry.pre_crop_boundaries,
            telemetry.pre_crop_two_seed_legal,
            telemetry.finite_feature_failures,
            telemetry.legal_mask_failures,
            telemetry.source_assignment_failures,
            telemetry.boundary_failures,
            telemetry.reward_identity_error,
        )
        .expect("write D71 row");
    }
    writer.flush().expect("flush D71 output");
    eprintln!(
        "saved {} D71 {panel} rows in {:.3}s ({:.1} boundary transitions/s)",
        rows.len(),
        started.elapsed().as_secs_f64(),
        rows.iter()
            .map(|row| row.telemetry.boundary_decisions as u64)
            .sum::<u64>() as f64
            / started.elapsed().as_secs_f64(),
    );
}
